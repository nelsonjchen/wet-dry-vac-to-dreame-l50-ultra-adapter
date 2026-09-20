"""Full REV 4 adapter, using the revised card and tested hose socket."""
from pathlib import Path
from dataclasses import replace
from build123d import export_step, export_stl
from hose_socket_concept import build_socket_concept
from rev4_card_fit_test import rev4_dimensions


def build_rev4_adapter():
    # The pipe pedestal covers the center tab; retain it only on the test card.
    return build_socket_concept(interface_dimensions=replace(rev4_dimensions(), pull_tab_length=0.0))


if __name__ == '__main__':
    part = build_rev4_adapter()
    output = Path(__file__).resolve().parents[1] / 'exports'
    output.mkdir(parents=True, exist_ok=True)
    for extension, exporter in [('stl', export_stl), ('step', export_step)]:
        path = output / f'hose-adapter-rev4.{extension}'
        if not exporter(part, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
