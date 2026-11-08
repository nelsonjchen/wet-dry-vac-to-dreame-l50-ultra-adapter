"""U-loop routing preview: turn starts 15 mm past the wide trailing card edge.

The return bends down past the card edge and aims back along -Z. An inlet
riser keeps the entire socket above the card underside / print bed at Z=0.
This is a clearance concept, not a support-free print or verified dock fit. All mm.
"""
import argparse
from dataclasses import replace
from math import cos, sin, pi
from pathlib import Path

from build123d import (
    Align, Circle, Cone, Cylinder, Plane, Pos, Rot, ThreePointArc, Vector,
    export_step, export_stl, loft, sweep,
)
from dewalt_rev5_adapter import socket_dimensions
from reference_interface import build_interface, gasket_seat
from rev4_card_fit_test import rev4_dimensions


def build_u_loop(edge_offset=15.0, return_radius=32.0):
    dims = replace(rev4_dimensions(), revision=6, pull_tab_length=0,
                   project_label='DREAME L50 ULTRA\nU LOOP CONCEPT')
    socket = socket_dimensions()
    root = (socket['connector_od'] + socket['clearance'] - socket['taper']/2)/2
    mouth = root + socket['taper']/2
    wall, initial_radius = 3.0, 32.0
    depth, lead_in = socket['depth'], 1.5
    rear = -dims.flange_length/2 + dims.trailing_end_inset
    turn_y = rear - edge_offset
    # Raise the whole loop rather than shortening the measured socket: its
    # downward mouth must never extend beneath the card's Z=0 underside.
    elbow_base_z = max(dims.flange_thickness, return_radius + depth - initial_radius)
    inlet_rise = elbow_base_z - dims.flange_thickness
    z = elbow_base_z + initial_radius
    if edge_offset < 0 or -turn_y <= initial_radius:
        raise ValueError('Turn must start beyond the first elbow and card edge')
    if return_radius <= root + wall:
        raise ValueError('Return radius must exceed the outer duct radius')

    # First elbow: same inlet and measured DeWalt root bore, now aimed -Y.
    sections = []
    for i in range(17):
        t = i/16
        a = pi*t/2
        radius = dims.hole_diameter/2 + (root-dims.hole_diameter/2)*(3*t*t-2*t*t*t)
        loc = Pos(0, -initial_radius*(1-cos(a)),
                  elbow_base_z+initial_radius*sin(a))*Rot(a*180/pi, 0, 0)
        sections.append((loc, radius))
    outer = loft([loc*Circle(r+wall) for loc, r in sections])
    inner = loft([loc*Circle(r) for loc, r in sections])
    alignment = (Align.CENTER, Align.CENTER, Align.MIN)
    outer += Pos(0, 0, dims.flange_thickness-.2)*Cylinder(
        dims.hole_diameter/2+wall, inlet_rise+.2, align=alignment)
    inner += Pos(0, 0, -.1)*Cylinder(
        dims.hole_diameter/2, elbow_base_z+.1, align=alignment)

    outgoing = Pos(0, -initial_radius, z)*Rot(90, 0, 0)
    length = -turn_y-initial_radius
    outer += outgoing*Cylinder(root+wall, length, align=alignment)
    inner += outgoing*Cylinder(root, length, align=alignment)
    arc = ThreePointArc((0, turn_y, z),
                        (0, turn_y-return_radius*sin(pi/4),
                         z-return_radius*(1-cos(pi/4))),
                        (0, turn_y-return_radius, z-return_radius))
    start = Pos(0, turn_y, z)*Rot(90, 0, 0)
    outer += sweep(start*Circle(root+wall), path=arc)
    inner += sweep(start*Circle(root), path=arc)

    # Second 90-degree bend completes the U: inlet +Z, outlet -Z.
    end = Pos(0, turn_y-return_radius, z-return_radius)*Rot(180, 0, 0)
    outer += end*Cylinder(mouth+wall, depth, align=alignment)
    inner += end*Cone(root, mouth+.1*(mouth-root)/depth, depth+.1, align=alignment)
    inner += end*Pos(0, 0, depth-lead_in)*Cone(
        mouth-(mouth-root)*lead_in/depth, mouth+1, lead_in+.01, align=alignment)
    part = (build_interface(dims)+outer)-inner-gasket_seat(dims)
    part.label = 'REV 6 U-loop concept — DeWalt measured socket'
    if not part.is_valid or len(part.solids()) != 1:
        raise RuntimeError('Expected one valid connected adapter solid')
    if part.bounding_box().min.Z < -1e-5 or z-return_radius-depth < -1e-5:
        raise RuntimeError('Adapter must not extend below the card underside at Z=0')
    return part, dict(rear=rear, turn_y=turn_y, z=z,
                      inlet_rise=inlet_rise,
                      return_y=turn_y-return_radius, return_z=z-return_radius,
                      mouth_z=z-return_radius-depth, outlet_direction=(0, 0, -1),
                      edge_offset=edge_offset)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edge-offset', type=float, default=15)
    parser.add_argument('--return-radius', type=float, default=32)
    parser.add_argument('--show', action='store_true')
    args = parser.parse_args()
    part, geometry = build_u_loop(args.edge_offset, args.return_radius)
    output = Path(__file__).resolve().parents[1]/'exports'
    output.mkdir(parents=True, exist_ok=True)
    for ext, exporter in [('step', export_step), ('stl', export_stl)]:
        path = output/f'hose-adapter-u-loop-concept.{ext}'
        if not exporter(part, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
    print(f'Valid single solid; volume {part.volume:.1f} mm³')
    print(f'Routing references: {geometry}; bounds: {part.bounding_box()}')
    if args.show:
        from ocp_viewer import Camera, show
        rear, turn = geometry['rear'], geometry['turn_y']
        def reference_rod(start, finish):
            vector = Vector(finish)-Vector(start)
            return Plane(origin=start, z_dir=vector)*Cylinder(
                .45, vector.length, align=(Align.CENTER, Align.CENTER, Align.MIN))
        edge = reference_rod((-39, rear, 4), (42, rear, 4))
        offset = reference_rod((34, rear, 4), (34, turn, 4))
        turn_line = reference_rod((34, turn, 4), (0, turn, geometry['z']))
        show(part, edge, offset, turn_line,
             names=['U-loop — socket flush with card underside', 'Wide card edge',
                    f'{args.edge_offset:g} mm to start of turn', 'Turn start reference'],
             colors=['#d7dde3', '#ee9b27', '#ee9b27', '#ee9b27'],
             reset_camera=Camera.RESET, axes=False, axes0=False, grid=False,
             position=(230, -210, 155), target=(0, -20, 40), up='Z',
             port=3939)


if __name__ == '__main__':
    main()
