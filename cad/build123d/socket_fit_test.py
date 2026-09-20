"""Standalone tapered hose fit coupon; mm. Print narrow end down, mouth up."""
from pathlib import Path

from build123d import Align, Axis, Cone, Cylinder, Pos, export_step, export_stl, fillet


def build_socket_fit_test(connector_od=30.75, clearance=0.4, taper=2.0, depth=35.0):
    """Match the proposed adapter socket, without elbow, card, or pedestal."""
    root = (connector_od + clearance - taper / 2) / 2
    mouth = (connector_od + clearance + taper / 2) / 2
    if root <= 0 or taper < 0 or clearance < 0 or depth < 5:
        raise ValueError('Invalid socket dimensions')
    wall, lead_in = 3.0, 1.5
    align = (Align.CENTER, Align.CENTER, Align.MIN)
    shell = Cylinder(mouth + wall, depth, align=align)
    shell = fillet(shell.faces().sort_by(Axis.Z)[-1].edges(), radius=0.5)
    slope = (mouth - root) / depth
    # Extend the tapered cutter beyond both ends for an open-ended coupon.
    bore = Pos(0, 0, -0.1) * Cone(root - slope * 0.1,
        mouth + slope * 0.1, depth + 0.2, align=align)
    bore += Pos(0, 0, depth - lead_in) * Cone(
        mouth - slope * lead_in, mouth + 1.0, lead_in, align=align)
    part = shell - bore
    part.label = 'Hose socket fit test — 30.75 mm estimate'
    if not part.is_valid or len(part.solids()) != 1:
        raise RuntimeError('Expected one valid solid')
    return part


if __name__ == '__main__':
    part = build_socket_fit_test()
    output = Path(__file__).resolve().parents[1] / 'exports'
    output.mkdir(parents=True, exist_ok=True)
    for extension, exporter in [('stl', export_stl), ('step', export_step)]:
        path = output / f'socket-fit-test-30p75.{extension}'
        if not exporter(part, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
    print('35 mm deep; root ID 30.15 mm; mouth ID 32.15 mm before entry chamfer')
