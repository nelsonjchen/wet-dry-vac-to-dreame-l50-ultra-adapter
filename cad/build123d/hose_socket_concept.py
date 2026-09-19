"""Parametric elbow and female hose socket on the V7 interface; mm."""
import argparse
from pathlib import Path
from math import sin, cos, radians, degrees, asin, atan2, hypot
from build123d import (
    Align, Axis, Box, Circle, Cone, Cylinder, Pos, Rot, ThreePointArc, Polygon, Rectangle,
    export_step, export_stl, sweep, extrude, revolve, loft,
)
from reference_interface import InterfaceDimensions, build_interface, gasket_seat

def build_socket_concept(connector_od=32.0, clearance=0.4, insertion_depth=35.0,
                         bend_radius=24.0, exit_angle=None, support_access=False,
                         tilt_up=0.0, socket_taper=2.0):
    # Provisional 32 mm end OD guessed from the SL18129's nominal 1.25-inch
    # hose family. This is NOT a measured connector diameter.
    if connector_od <= 0 or clearance < 0 or insertion_depth < 5:
        raise ValueError('Require positive connector OD, nonnegative clearance, and depth >= 5 mm')
    d = InterfaceDimensions()
    if not 0 <= tilt_up <= 60:
        raise ValueError('Upward tilt must be between 0 and 60 degrees')
    bend_degrees = 90 - tilt_up
    theta = radians(bend_degrees)
    socket_id = connector_od + clearance
    # Diametral taper centered on the nominal bore; wider toward the mouth.
    root_radius = (socket_id - socket_taper / 2) / 2
    mouth_radius = (socket_id + socket_taper / 2) / 2
    if socket_taper < 0 or root_radius <= 0:
        raise ValueError('Require nonnegative taper and positive socket root diameter')
    wall = 3.0
    transition_length = 6.0
    lead_in = 1.5
    top_of_plate = d.flange_thickness
    alignment = (Align.CENTER, Align.CENTER, Align.MIN)
    throat_radius = d.hole_diameter / 2
    if bend_radius <= throat_radius + wall:
        raise ValueError('Bend radius must exceed the outer duct radius (19.5 mm)')
    # Default: horizontal outlet; XY aim is constrained by the right rail margin.
    arc = ThreePointArc(
        (0, 0, top_of_plate),
        (bend_radius * (1 - cos(theta / 2)), 0, top_of_plate + bend_radius * sin(theta / 2)),
        (bend_radius * (1 - cos(theta)), 0, top_of_plate + bend_radius * sin(theta)),
    )
    outer = sweep(Pos(0, 0, top_of_plate) * Circle(throat_radius + wall), path=arc)
    inner = sweep(Pos(0, 0, top_of_plate) * Circle(throat_radius), path=arc)
    # Small overlap joins the elbow directly to the single card.
    outer += Pos(0, 0, top_of_plate - 0.2) * Cylinder(throat_radius + wall, 0.2, align=alignment)
    inner += Pos(0, 0, top_of_plate - 0.3) * Cylinder(throat_radius, 0.3, align=alignment)
    bend_x = bend_radius * (1 - cos(theta))
    bend_z = top_of_plate + bend_radius * sin(theta)
    outlet = Pos(bend_x, 0, bend_z) * Rot(0, bend_degrees, 0)
    outer += outlet * Cone(throat_radius + wall, mouth_radius + wall, transition_length, align=alignment)
    inner += outlet * Cone(throat_radius, root_radius, transition_length, align=alignment)
    socket = outlet * Pos(0, 0, transition_length)
    outer += socket * Cylinder(mouth_radius + wall, insertion_depth, align=alignment)
    inner += socket * Cone(
        root_radius, mouth_radius + (mouth_radius - root_radius) * 0.1 / insertion_depth,
        insertion_depth + 0.1, align=alignment,
    )
    inner += socket * Pos(0, 0, insertion_depth - lead_in) * Cone(
        mouth_radius - (mouth_radius - root_radius) * lead_in / insertion_depth,
        mouth_radius + 1.0, lead_in, align=alignment,
    )
    # Fill beneath the outlet up to its centreline. The pedestal follows the
    # duct width, leaving the card's side rails and arrow end unchanged.
    # Start on the bed, including the short extension past the trailing edge,
    # so the pedestal itself does not introduce a suspended bottom lip.
    # Match the duct sides exactly, without a projecting pedestal lip.
    bend_outer_radius = throat_radius + wall
    socket_outer_radius = mouth_radius + wall
    # Trim the bend end to the actual toroidal outer envelope, rather than
    # letting the rectangular support corners protrude beyond the curved wall.
    # Filling the radial centre of the sweep profile preserves support below
    # the bend; the original inner duct is subtracted afterwards.
    filled_profile = Pos(0, 0, top_of_plate) * (
        Circle(bend_outer_radius)
        + Pos(bend_radius / 2, 0) * Rectangle(bend_radius, 2 * bend_outer_radius)
    )
    pedestal = revolve(
        filled_profile, axis=Axis((bend_radius, 0, top_of_plate), (0, 1, 0)),
        revolution_arc=bend_degrees,
    )
    # D-shaped sections carry the socket's lower half down to the bed.
    # Local +X points downward in the tilted socket plane. Extend below the
    # bed, then clip; no rectangular corner protrudes above the round shell.
    support_depth = 4 * (bend_radius + socket_outer_radius + insertion_depth)
    def supported_section(radius):
        return Circle(radius) + Pos(support_depth / 2, 0) * Rectangle(support_depth, 2 * radius)
    pedestal += loft([
        outlet * supported_section(bend_outer_radius),
        socket * supported_section(socket_outer_radius),
    ])
    pedestal += extrude(socket * supported_section(socket_outer_radius),
                        amount=insertion_depth, dir=(sin(theta), 0, cos(theta)))
    mouth_x = bend_x + (transition_length + insertion_depth) * sin(theta)
    footprint_end = mouth_x + socket_outer_radius * cos(theta)
    # Retain only the area below/within the outlet's projected footprint.
    pedestal &= Box(footprint_end, 2 * socket_outer_radius, support_depth,
                    align=(Align.MIN, Align.CENTER, Align.MIN))
    if exit_angle is None:
        # Keep the whole pipe/pedestal bounding footprint inside X=32 mm for
        # the default 70 mm card. L*sin(a)+W*cos(a) is its rightmost corner.
        limit = d.flange_width / 2 - 3.0
        bounds = (outer + pedestal).bounding_box()
        length, half_width = bounds.max.X, max(abs(bounds.min.Y), abs(bounds.max.Y))
        if half_width > limit:
            raise ValueError('Socket too wide to preserve the 3 mm right-edge margin')
        angle = degrees(asin(min(1.0, limit / hypot(length, half_width)))
                        - atan2(half_width, length))
        exit_angle = -90 + min(30.0, max(0.0, angle))
    orient = Rot(0, 0, exit_angle)
    inlet = Pos(0, 0, -0.1) * Cylinder(
        throat_radius, top_of_plate + 0.1, align=alignment,
    )
    part = build_interface() + orient * (outer + pedestal) - orient * inner - inlet
    # Cut after union: the bed-level pedestal must not refill the dock seal seat.
    part -= gasket_seat(d)
    # support_access is retained as a legacy export-name alias only.
    # A single card has no trapped rail-gap supports and must not be perforated.
    part.label = f'{tilt_up:g}-degree upward hose outlet - unmeasured connector'
    if not part.is_valid or len(part.solids()) != 1:
        raise RuntimeError('Expected one valid solid')
    return part


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--connector-od', type=float, default=32.0)
    parser.add_argument('--clearance', type=float, default=0.4, help='Diametral clearance, mm')
    parser.add_argument('--insertion-depth', type=float, default=35.0)
    parser.add_argument('--socket-taper', type=float, default=2.0,
                        help='Mouth minus root bore diameter, mm; centered on OD + clearance')
    parser.add_argument('--bend-radius', type=float, default=24.0, help='Duct centreline radius, mm')
    parser.add_argument('--exit-angle', type=float, default=None, help='Override automatic 3 mm right-edge clearance; -90=straight down, -60=30 degrees down-right')
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--tilt-up', type=float, default=0.0, help='Socket elevation above card, degrees (0 to 60); default horizontal')
    parser.add_argument('--support-access', action='store_true', help='Legacy filename alias; exports the same single-card elbow without access slots')
    args = parser.parse_args()
    part = build_socket_concept(args.connector_od, args.clearance, args.insertion_depth,
                               args.bend_radius, args.exit_angle, args.support_access, args.tilt_up,
                               args.socket_taper)
    output = Path(__file__).resolve().parents[1] / 'exports'
    output.mkdir(parents=True, exist_ok=True)
    name = 'hose-elbow-support-access' if args.support_access else 'hose-elbow-concept'
    for ext, exporter in [('step', export_step), ('stl', export_stl)]:
        path = output / f'{name}.{ext}'
        if not exporter(part, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
    nominal = args.connector_od + args.clearance
    print(f'Socket root/mouth ID: {nominal - args.socket_taper / 2:g}/{nominal + args.socket_taper / 2:g} mm (before entry chamfer); depth: {args.insertion_depth:g} mm')
    print(f'Valid solid; volume: {part.volume:.2f} mm³')
    if args.show:
        from ocp_viewer import Camera, show
        show(part, names=[name], reset_camera=Camera.RESET)


if __name__ == '__main__':
    main()
