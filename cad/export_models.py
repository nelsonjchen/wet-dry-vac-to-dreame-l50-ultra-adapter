"""Regenerate the four public model pairs from the editable build123d source."""
import sys
from pathlib import Path
from build123d import Pos, export_step, export_stl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'cad' / 'build123d'))
from rev5_full_adapter import build_rev5_adapter
from dewalt_rev5_adapter import build_dewalt_adapter
from dewalt_addon_elbow import build_addon_elbow


def main():
    output = ROOT / 'models'
    output.mkdir(exist_ok=True)
    parts = [
        ('hose-adapter-rev5', build_rev5_adapter()),
        ('hose-adapter-rev5-dewalt-measured', build_dewalt_adapter()),
    ]
    for kind in ('stanley', 'dewalt'):
        part, _ = build_addon_elbow(inlet=kind, outlet=kind)
        part = Pos(0, 0, -part.bounding_box().min.Z) * part
        parts.append((f'{kind}-to-{kind}-90-elbow', part))
    for name, part in parts:
        if not part.is_valid or len(part.solids()) != 1:
            raise RuntimeError(f'{name}: expected one valid solid')
        for extension, exporter in [('stl', export_stl), ('step', export_step)]:
            path = output / f'{name}.{extension}'
            if not exporter(part, path):
                raise RuntimeError(f'Export failed: {path}')
            print(path)


if __name__ == '__main__':
    main()
