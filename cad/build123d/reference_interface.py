"""Recreate the inlet and sliding flange measured from the supplied V7 mesh.

Millimetres assumed (STL does not encode units). Origin is the inlet centre on
the underside. Only the card outline and inlet are retained from the source
bin interface. This is a physical fit-test part, not a bagless-bin floor.
"""
import argparse
from dataclasses import dataclass
from pathlib import Path

from build123d import (
    Align, Axis, Cylinder, Torus, Pos, Rot, Plane, RectangleRounded, Polygon, Text, FontStyle,
    export_step, export_stl, extrude, fillet, chamfer, revolve,
)


@dataclass(frozen=True)
class InterfaceDimensions:
    hole_diameter: float = 33.0
    flange_width: float = 70.0
    flange_length: float = 101.6
    flange_thickness: float = 3.4
    flange_corner_radius: float = 6.0
    flange_top_round: float = 0.6
    flange_bottom_chamfer: float = 0.3
    gasket_outer_diameter: float = 42.0
    gasket_inner_diameter: float = 35.0
    gasket_seat_depth: float = 1.6
    gasket_radial_clearance: float = 0.2
    gasket_proud: float = 1.0
    revision: int = 1
    revision_font_size: float = 4.0
    project_label: str = ''
    trailing_width: float | None = None
    trailing_positive_x_extra: float = 0.0
    trailing_end_inset: float = 0.0
    pull_tab_length: float = 0.0
    pull_tab_width: float = 24.0


def gasket_seat(d: InterfaceDimensions = InterfaceDimensions()):
    """Blind annular dovetail pocket entered from -Z; no through-card path."""
    if not (d.hole_diameter < d.gasket_inner_diameter < d.gasket_outer_diameter
            < min(d.flange_width, d.flange_length)):
        raise ValueError('Gasket seat must fit around the bore inside the card')
    if not 0 < d.gasket_seat_depth < d.flange_thickness:
        raise ValueError('Gasket seat must leave a solid backing')
    inner, outer = d.gasket_inner_diameter / 2, d.gasket_outer_diameter / 2
    profile = Plane.XZ * Polygon(
        (inner + .1, -.1), (outer - .1, -.1),
        (outer - .1, 0), (outer - .3, .2),
        (outer - .3, .35), (outer, .7), (outer, d.gasket_seat_depth),
        (inner, d.gasket_seat_depth), (inner, .7), (inner + .3, .35),
        (inner + .3, .2), (inner + .1, 0), align=None)
    return revolve(profile, axis=Axis.Z)


def build_gasket(d: InterfaceDimensions = InterfaceDimensions(), for_print=False):
    """Rounded sealing bead projects in -Z; print export is flange-flat."""
    gasket_seat(d)  # Validate the shared seat dimensions.
    outer = d.gasket_outer_diameter / 2 - d.gasket_radial_clearance
    inner = d.gasket_inner_diameter / 2
    if d.gasket_proud <= 0 or d.gasket_radial_clearance < 0 or outer-inner <= 0.8:
        raise ValueError('Invalid gasket lip or clearance')
    inner += d.gasket_radial_clearance
    depth = d.gasket_seat_depth - .2
    profile = Plane.XZ * Polygon(
        (inner + .3, 0), (outer - .3, 0),
        (outer - .3, .4), (outer, .8), (outer, depth),
        (inner, depth), (inner, .8), (inner + .3, .4), align=None)
    ring = revolve(profile, axis=Axis.Z)
    ring += Torus((inner + outer) / 2, d.gasket_proud)
    # Print flat backing on the bed; installed bead projects below Z=0.
    if for_print:
        ring = Pos(0, 0, depth) * Rot(180, 0, 0) * ring
    if not ring.is_valid or len(ring.solids()) != 1:
        raise RuntimeError('Expected one valid gasket solid')
    return ring


def build_interface(d: InterfaceDimensions = InterfaceDimensions()):
    outline = RectangleRounded(d.flange_width, d.flange_length, d.flange_corner_radius)
    if d.trailing_width is not None:
        if d.trailing_width < d.flange_width:
            raise ValueError('Trailing width must be at least the insertion width')
        w, t, end = d.flange_width / 2, d.trailing_width / 2, d.flange_length / 2
        rear = -end + d.trailing_end_inset
        right = t + d.trailing_positive_x_extra
        if d.trailing_end_inset < 0 or rear + 25 >= end or right < w:
            raise ValueError('Invalid trailing extension dimensions')
        outline = Polygon((-t, rear), (right, rear), (right, rear + 15),
                          (w, rear + 25), (w, end), (-w, end),
                          (-w, rear + 25), (-t, rear + 15), align=None)
        outline = fillet(outline.vertices(), radius=d.flange_corner_radius)
    if d.pull_tab_length > 0:
        rear = -d.flange_length / 2 + d.trailing_end_inset
        overlap = 6.0
        tab = Pos(0, rear + (overlap - d.pull_tab_length) / 2) * RectangleRounded(
            d.pull_tab_width, d.pull_tab_length + overlap, 6.0)
        outline += tab
    flange = extrude(outline, amount=d.flange_thickness)
    # Rounded entry edge on the top of the mating flange, observed in the STL.
    flange = fillet(flange.faces().sort_by(Axis.Z)[-1].edges(), d.flange_top_round)
    if d.flange_bottom_chamfer:
        flange = chamfer(flange.faces().sort_by(Axis.Z)[0].edges(), length=d.flange_bottom_chamfer)
    height = d.flange_thickness
    bore = Pos(0, 0, -1) * Cylinder(
        d.hole_diameter / 2, height + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    part = flange - bore - gasket_seat(d)
    # Provisional insertion-direction marker (+Y), NOT a measured dock feature.
    # Engrave the hose-side face, away from the bore and sliding edges.
    arrow = Polygon(
        (-2, 24), (2, 24), (2, 34), (6, 34),
        (0, 43), (-6, 34), (-2, 34), align=None,
    )
    if d.project_label:
        # Reserve two full-width lines for readable identification; put a
        # shorter insertion arrow on the clear upper-right area of the card.
        arrow = Polygon((18, 22), (22, 22), (22, 28), (26, 28),
                        (20, 35), (14, 28), (18, 28), align=None)
    part -= Pos(0, 0, height - 0.4) * extrude(arrow, amount=0.5)
    # Recessed label on the hose side, beside the arrow and outside the elbow.
    # No raised lettering on the sliding interface; TPU remains unmarked.
    if d.revision < 1:
        raise ValueError('Print revision must be positive')
    label = Text(f'REV {d.revision}', font_size=d.revision_font_size, font='Arial')
    part -= Pos(-18, 29 if d.project_label else 36, height - 0.4) * extrude(label, amount=0.5)
    if d.project_label:
        for line, y in zip(d.project_label.split('\n'), (46, 40)):
            name = Text(line, font_size=5.0, font='Arial', font_style=FontStyle.BOLD)
            if name.bounding_box().size.X > d.flange_width - 8:
                raise ValueError('Project label is too wide for the card')
            part -= Pos(0, y, height - 0.4) * extrude(name, amount=0.5)
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
    for extension, exporter in [('step', export_step), ('stl', export_stl)]:
        path = output / f'dock-gasket-tpu.{extension}'
        if not exporter(build_gasket(for_print=True), path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
    print(f'One valid solid; volume = {part.volume:.2f} mm³')
    if args.show:
        from ocp_vscode import Camera, show
        show(part, names=['V7 inlet / sliding flange (fit test)'], reset_camera=Camera.RESET)


if __name__ == '__main__':
    main()
