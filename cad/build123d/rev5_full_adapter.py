"""REV 5: gradually narrowing elbow, with the tested REV 4 card and socket."""
from dataclasses import replace
from pathlib import Path
from build123d import export_step, export_stl
from hose_socket_concept import build_socket_concept
from rev4_card_fit_test import rev4_dimensions


def build_rev5_adapter():
    return build_socket_concept(
        interface_dimensions=replace(rev4_dimensions(), revision=5, pull_tab_length=0),
        tapered_elbow=True,
    )


if __name__ == '__main__':
    part = build_rev5_adapter()
    output = Path(__file__).resolve().parents[1] / 'exports'
    output.mkdir(parents=True, exist_ok=True)
    for extension, exporter in [('stl', export_stl), ('step', export_step)]:
        path = output / f'hose-adapter-rev5.{extension}'
        if not exporter(part, path):
            raise RuntimeError(f'Export failed: {path}')
        print(path)
