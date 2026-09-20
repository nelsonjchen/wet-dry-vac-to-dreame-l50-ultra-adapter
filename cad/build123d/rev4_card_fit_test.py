"""REV 4: preserve REV 3 fit outline, add a bag-style trailing pull tab."""
from pathlib import Path
from build123d import export_stl, export_step
from reference_interface import InterfaceDimensions, build_interface


def build_rev4_card():
    return build_interface(InterfaceDimensions(
        revision=4, trailing_width=78.0,
        trailing_positive_x_extra=3.0, trailing_end_inset=19.0,
        pull_tab_length=14.0, pull_tab_width=24.0))


if __name__ == '__main__':
    part = build_rev4_card()
    output = Path(__file__).resolve().parents[1] / 'exports'
    output.mkdir(parents=True, exist_ok=True)
    for suffix, exporter in [('stl', export_stl), ('step', export_step)]:
        path = output / f'reference-interface-rev4-fit-test.{suffix}'
        if not exporter(part, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
