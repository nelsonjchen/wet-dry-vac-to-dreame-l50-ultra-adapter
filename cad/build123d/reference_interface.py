"""Recreate the inlet and sliding flange measured from the supplied V7 mesh.

Millimetres assumed (STL does not encode units). Origin is the inlet centre on
the underside. Only the card outline and inlet are retained from the source
bin interface. This is a physical fit-test part, not a bagless-bin floor.
"""
import argparse
from dataclasses import dataclass
from pathlib import Path

from build123d import (
    Align, Axis, Cylinder, Pos, RectangleRounded, Polygon,
    export_step, export_stl, extrude, fillet,
)


@dataclass(frozen=True)
class InterfaceDimensions:
    hole_diameter: float = 33.0
    flange_width: float = 70.0
    flange_length: float = 101.6
    flange_thickness: float = 3.4
    flange_corner_radius: float = 6.0
    flange_top_round: float = 0.6


def build_interface(d: InterfaceDimensions = InterfaceDimensions()):
    flange = extrude(
        RectangleRounded(d.flange_width, d.flange_length, d.flange_corner_radius),
        amount=d.flange_thickness,
    )
    # Rounded entry edge on the top of the mating flange, observed in the STL.
    flange = fillet(flange.faces().sort_by(Axis.Z)[-1].edges(), d.flange_top_round)
    height = d.flange_thickness
    bore = Pos(0, 0, -1) * Cylinder(
        d.hole_diameter / 2, height + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    part = flange - bore
    # Provisional insertion-direction marker (+Y), NOT a measured dock feature.
    # Engrave the hose-side face, away from the bore and sliding edges.
    arrow = Polygon(
        (-2, 24), (2, 24), (2, 34), (6, 34),
        (0, 43), (-6, 34), (-2, 34), align=None,
    )
    part -= Pos(0, 0, height - 0.4) * extrude(arrow, amount=0.5)
    part.label = 'V7 inlet and sliding flange — fit test'
    if not part.is_valid or len(part.solids()) != 1:
        raise RuntimeError('Expected one valid solid')
    return part


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--show', action='store_true', help='Send to a running OCP CAD Viewer')
    args = parser.parse_args()
    part = build_interface()
    output = Path(__file__).resolve().parents[1] / 'exports'
    output.mkdir(parents=True, exist_ok=True)
    for extension, exporter in [('step', export_step), ('stl', export_stl)]:
        path = output / f'reference-interface-fit-test.{extension}'
        if not exporter(part, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
    print(f'One valid solid; volume = {part.volume:.2f} mm³')
    if args.show:
        from ocp_vscode import Camera, show
        show(part, names=['V7 inlet / sliding flange (fit test)'], reset_camera=Camera.RESET)


if __name__ == '__main__':
    main()
