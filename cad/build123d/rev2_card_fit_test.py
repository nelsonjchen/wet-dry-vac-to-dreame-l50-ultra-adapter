"""Isolated REV 2 trailing-width trial; full REV 1 adapter is unchanged."""
from pathlib import Path
from build123d import export_stl, export_step
from reference_interface import InterfaceDimensions, build_interface


def build_rev2_card():
    # Scan suggests ~8 mm added trailing width relative to the leading width.
    # Preserve previously tried insertion width, length, thickness and bore.
    return build_interface(InterfaceDimensions(revision=2, trailing_width=78.0))


if __name__ == '__main__':
    part = build_rev2_card()
    output = Path(__file__).resolve().parents[1] / 'exports'
    output.mkdir(parents=True, exist_ok=True)
    for suffix, exporter in [('stl', export_stl), ('step', export_step)]:
        path = output / f'reference-interface-rev2-fit-test.{suffix}'
        if not exporter(part, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
