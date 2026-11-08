"""DXV05P-QT variant using the user's measured cuff taper; fit not yet tested."""
import argparse
from dataclasses import replace
from pathlib import Path
from build123d import export_step, export_stl
from hose_socket_concept import build_socket_concept
from rev4_card_fit_test import rev4_dimensions
from socket_fit_test import build_socket_fit_test


def socket_dimensions(tip_od=44.77, wide_od=45.77, cuff_length=62.24,
                      depth=35.0, clearance=0.20):
    """Convert a linear cuff taper into the builders' midpoint-OD convention."""
    if tip_od <= 0 or wide_od < tip_od or cuff_length <= 0 or not 5 <= depth <= cuff_length or clearance < 0:
        raise ValueError('Invalid measured cuff or insertion dimensions')
    taper = (wide_od-tip_od)*depth/cuff_length
    return dict(connector_od=tip_od+taper/2, clearance=clearance,
                taper=taper, depth=depth)


def build_dewalt_adapter(**measurements):
    dims = socket_dimensions(**measurements)
    return build_socket_concept(
        connector_od=dims['connector_od'], clearance=dims['clearance'],
        socket_taper=dims['taper'], insertion_depth=dims['depth'],
        bend_radius=32.0, tapered_elbow=True,
        interface_dimensions=replace(
            rev4_dimensions(), revision=5, pull_tab_length=0,
            project_label='DREAME L50 ULTRA\nDEWALT ADAPTER'),
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tip-od', type=float, default=44.77)
    parser.add_argument('--wide-od', type=float, default=45.77)
    parser.add_argument('--cuff-length', type=float, default=62.24)
    parser.add_argument('--depth', type=float, default=35.0)
    parser.add_argument('--clearance', type=float, default=0.20,
                        help='Diametral clearance in mm; starting fit-test allowance')
    args = parser.parse_args()
    output = Path(__file__).resolve().parents[1] / 'exports'
    output.mkdir(parents=True, exist_ok=True)
    dims = socket_dimensions(**vars(args))
    coupon = build_socket_fit_test(**dims)
    coupon.label = 'DeWalt measured taper — 44.77 to 45.77 mm over 62.24 mm'
    for name, part in [('hose-adapter-rev5-dewalt-measured', build_dewalt_adapter(**vars(args))),
                       ('socket-fit-test-dewalt-measured', coupon)]:
        for ext, exporter in [('stl', export_stl), ('step', export_step)]:
            path = output / f'{name}.{ext}'
            if not exporter(part, path):
                raise RuntimeError(f'Export failed: {path}')
            print(path)
    root = dims['connector_od']+dims['clearance']-dims['taper']/2
    print(f'Root/mouth ID before lead-in: {root:.4f}/{root+dims["taper"]:.4f} mm')
    print('Measured cuff geometry; printed fit still requires testing.')
