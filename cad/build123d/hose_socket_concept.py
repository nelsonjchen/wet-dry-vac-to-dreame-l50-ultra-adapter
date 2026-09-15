"""90-degree outlet and female hose socket on the V7 interface; mm."""
import argparse
from pathlib import Path
from math import sqrt
from build123d import (
    Align, Axis, Box, Circle, Cone, Cylinder, Pos, Rot, ThreePointArc, Polygon, Rectangle,
    export_step, export_stl, sweep, extrude, revolve,
)
from reference_interface import InterfaceDimensions, build_interface

def build_socket_concept(connector_od=38.0, clearance=0.4, insertion_depth=25.0,
                         bend_radius=24.0, exit_angle=-90.0, support_access=False):
    # 38 mm is an illustrative connector OD, not a measurement of the Stanley
    # hose. Nominal hose size does not specify the end connector's outer size.
    if connector_od <= 0 or clearance < 0 or insertion_depth < 5:
        raise ValueError('Require positive connector OD, nonnegative clearance, and depth >= 5 mm')
    d = InterfaceDimensions()
    socket_id = connector_od + clearance
    if socket_id < d.hole_diameter:
        raise ValueError('This concept requires a socket ID at least as large as the 33 mm inlet')
    wall = 3.0
    transition_length = 6.0
    lead_in = 1.5
    top_of_plate = d.flange_thickness
    alignment = (Align.CENTER, Align.CENTER, Align.MIN)
    throat_radius = d.hole_diameter / 2
    if bend_radius <= throat_radius + wall:
        raise ValueError('Bend radius must exceed the outer duct radius (19.5 mm)')
    # The centreline turns from +Z to +X, keeping the air passage round.
    # Rotate the base +X bend to -Y by default, opposite the +Y insertion arrow.
    arc = ThreePointArc(
        (0, 0, top_of_plate),
        (bend_radius * (1 - 1 / sqrt(2)), 0, top_of_plate + bend_radius / sqrt(2)),
        (bend_radius, 0, top_of_plate + bend_radius),
    )
    outer = sweep(Pos(0, 0, top_of_plate) * Circle(throat_radius + wall), path=arc)
    inner = sweep(Pos(0, 0, top_of_plate) * Circle(throat_radius), path=arc)
    # Small overlap joins the elbow directly to the single card.
    outer += Pos(0, 0, top_of_plate - 0.2) * Cylinder(throat_radius + wall, 0.2, align=alignment)
    inner += Pos(0, 0, top_of_plate - 0.3) * Cylinder(throat_radius, 0.3, align=alignment)
    outlet = Pos(bend_radius, 0, top_of_plate + bend_radius) * Rot(0, 90, 0)
    outer += outlet * Cone(throat_radius + wall, socket_id / 2 + wall, transition_length, align=alignment)
    inner += outlet * Cone(throat_radius, socket_id / 2, transition_length, align=alignment)
    socket = Pos(bend_radius + transition_length, 0, top_of_plate + bend_radius) * Rot(0, 90, 0)
    outer += socket * Cylinder(socket_id / 2 + wall, insertion_depth, align=alignment)
    inner += socket * Cylinder(
        socket_id / 2, insertion_depth + 0.1, align=alignment,
    )
    inner += socket * Pos(0, 0, insertion_depth - lead_in) * Cone(
        socket_id / 2, socket_id / 2 + 1.0, lead_in, align=alignment,
    )
    orient = Rot(0, 0, exit_angle)
    # Fill beneath the outlet up to its centreline. The pedestal follows the
    # duct width, leaving the card's side rails and arrow end unchanged.
    # Start on the bed, including the short extension past the trailing edge,
    # so the pedestal itself does not introduce a suspended bottom lip.
    # Match the duct sides exactly, without a projecting pedestal lip.
    bend_outer_radius = throat_radius + wall
    socket_outer_radius = socket_id / 2 + wall
    socket_start = bend_radius + transition_length
    socket_end = socket_start + insertion_depth
    pedestal_profile = Polygon(
        (0, -bend_outer_radius), (bend_radius, -bend_outer_radius),
        (socket_start, -socket_outer_radius), (socket_end, -socket_outer_radius),
        (socket_end, socket_outer_radius), (socket_start, socket_outer_radius),
        (bend_radius, bend_outer_radius), (0, bend_outer_radius), align=None,
    )
    pedestal = extrude(pedestal_profile, amount=top_of_plate + bend_radius)
    # Trim the bend end to the actual toroidal outer envelope, rather than
    # letting the rectangular support corners protrude beyond the curved wall.
    # Filling the radial centre of the sweep profile preserves support below
    # the bend; the original inner duct is subtracted afterwards.
    filled_profile = Pos(0, 0, top_of_plate) * (
        Circle(bend_outer_radius)
        + Pos(bend_radius / 2, 0) * Rectangle(bend_radius, 2 * bend_outer_radius)
    )
    envelope = revolve(
        filled_profile, axis=Axis((bend_radius, 0, top_of_plate), (0, 1, 0)),
        revolution_arc=90,
    )
    envelope += Box(socket_end, 2 * socket_outer_radius, top_of_plate,
                    align=(Align.MIN, Align.CENTER, Align.MIN))
    envelope += Pos(bend_radius, 0, 0) * Box(
        socket_end - bend_radius, 2 * socket_outer_radius,
        top_of_plate + bend_radius, align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    pedestal = pedestal & envelope
    inlet = Pos(0, 0, -0.1) * Cylinder(
        throat_radius, top_of_plate + 0.1, align=alignment,
    )
    part = build_interface() + orient * (outer + pedestal) - orient * inner - inlet
    # support_access is retained as a legacy export-name alias only.
    # A single card has no trapped rail-gap supports and must not be perforated.
    part.label = '90-degree hose outlet concept - unmeasured connector'
    if not part.is_valid or len(part.solids()) != 1:
        raise RuntimeError('Expected one valid solid')
    return part


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--connector-od', type=float, default=38.0)
    parser.add_argument('--clearance', type=float, default=0.4, help='Diametral clearance, mm')
    parser.add_argument('--insertion-depth', type=float, default=25.0)
    parser.add_argument('--bend-radius', type=float, default=24.0, help='Duct centreline radius, mm')
    parser.add_argument('--exit-angle', type=float, default=-90.0, help='Rotation around inlet: -90=-Y (opposite arrow), 0=+X, 90=+Y, 180=-X')
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--support-access', action='store_true', help='Legacy filename alias; exports the same single-card elbow without access slots')
    args = parser.parse_args()
    part = build_socket_concept(args.connector_od, args.clearance, args.insertion_depth,
                               args.bend_radius, args.exit_angle, args.support_access)
    output = Path(__file__).resolve().parents[1] / 'exports'
    output.mkdir(parents=True, exist_ok=True)
    name = 'hose-elbow-support-access' if args.support_access else 'hose-elbow-concept'
    for ext, exporter in [('step', export_step), ('stl', export_stl)]:
        path = output / f'{name}.{ext}'
        if not exporter(part, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
    print(f'Socket ID: {args.connector_od + args.clearance:g} mm; depth: {args.insertion_depth:g} mm')
    print(f'Valid solid; volume: {part.volume:.2f} mm³')
    if args.show:
        from ocp_vscode import Camera, show
        show(part, names=[name], reset_camera=Camera.RESET)


if __name__ == '__main__':
    main()
