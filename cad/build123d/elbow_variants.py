"""Build the three requested plug-in elbow variants and slicing orientations."""
import argparse
import json
from pathlib import Path
from build123d import Pos, Rot, export_step, export_stl
from dewalt_addon_elbow import build_addon_elbow, installed_location
from dewalt_rev5_adapter import build_dewalt_adapter
from rev5_full_adapter import build_rev5_adapter

VARIANTS = [('dewalt', 'dewalt'), ('stanley', 'dewalt'), ('stanley', 'stanley')]
ORIENTATIONS = {
    'female-down': Rot(0, 0, 0),
    'male-down': Rot(0, -90, 0),
    'side': Rot(90, 0, 0),
    'openings-up-120': Rot(0, 120, 0),
    'openings-up-135': Rot(0, 135, 0),
    'openings-up-150': Rot(0, 150, 0),
}


def on_bed(part, rotation):
    rotated = rotation*part
    bounds = rotated.bounding_box()
    return Pos(-(bounds.min.X+bounds.max.X)/2,
               -(bounds.min.Y+bounds.max.Y)/2, -bounds.min.Z)*rotated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--show', action='store_true')
    args = parser.parse_args()
    output = Path(__file__).resolve().parents[1]/'exports'
    analysis = output/'elbow-slice-study'
    analysis.mkdir(parents=True, exist_ok=True)
    manifest, display, names, colors = {}, [], [], []
    upstream = {'dewalt': build_dewalt_adapter(), 'stanley': build_rev5_adapter()}
    for index, (inlet, outlet) in enumerate(VARIANTS):
        name = f'{inlet}-to-{outlet}-90-elbow'
        part, dimensions = build_addon_elbow(inlet=inlet, outlet=outlet)
        installed = installed_location(dimensions['upstream_socket_outer_radius'], inlet)*part
        interference = upstream[inlet].intersect(installed)
        collision_volume = interference.volume if interference else 0
        if collision_volume > .01:
            raise RuntimeError(f'{name} interference: {collision_volume} mm³')
        dimensions['interference_volume'] = collision_volume
        dimensions['volume'] = part.volume
        manifest[name] = dimensions
        printable = on_bed(part, ORIENTATIONS['female-down'])
        for ext, exporter in [('step', export_step), ('stl', export_stl)]:
            if not exporter(printable, output/f'{name}.{ext}'):
                raise RuntimeError(f'Export failed: {name}')
        for orientation, rotation in ORIENTATIONS.items():
            if not export_stl(on_bed(part, rotation), analysis/f'{name}--{orientation}.stl'):
                raise RuntimeError(f'Orientation export failed: {orientation}')
        offset = Pos(index*160, 0, 0)
        display.extend([offset*upstream[inlet], offset*installed])
        names.extend([f'{inlet.title()} existing adapter', f'{inlet.title()} → {outlet.title()} elbow'])
        colors.extend(['#c7cdd3', ['#e8a242', '#65a7db', '#79b891'][index]])
        print(f'{name}: {dimensions}')
    (analysis/'dimensions.json').write_text(json.dumps(manifest, indent=2)+'\n')
    if args.show:
        from ocp_viewer import Camera, show
        show(*display, names=names, colors=colors, port=3939,
             reset_camera=Camera.RESET, axes=False, axes0=False, grid=False,
             position=(400, -400, 240), target=(160, -30, 20), up='Z')


if __name__ == '__main__':
    main()
