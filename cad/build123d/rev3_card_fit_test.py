"""REV 3: trailing +X edge +3 mm; rear end and shoulders shifted +Y 19 mm."""
from pathlib import Path
from build123d import export_stl, export_step
from reference_interface import InterfaceDimensions, build_interface


def build_rev3_card():
    return build_interface(InterfaceDimensions(
        revision=3, trailing_width=78.0,
        trailing_positive_x_extra=3.0, trailing_end_inset=19.0))


if __name__ == '__main__':
    part = build_rev3_card()
    output = Path(__file__).resolve().parents[1] / 'exports'
    output.mkdir(parents=True, exist_ok=True)
    for suffix, exporter in [('stl', export_stl), ('step', export_step)]:
        path = output / f'reference-interface-rev3-fit-test.{suffix}'
        if not exporter(part, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
