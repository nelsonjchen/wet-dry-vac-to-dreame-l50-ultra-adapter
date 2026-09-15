"""Compare the reproduced mating profiles with sections of the reference STL."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import trimesh
from shapely.geometry import Polygon
from build123d import export_stl

from inspect_reference import ARCHIVE, OUTPUT, load_main
from reference_interface import build_interface


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ARCHIVE)
    args = parser.parse_args()
    source = load_main(args.archive)
    # Approximate placement removal only; retain the source's small tilt and
    # tessellation errors in the comparison instead of fitting them away.
    source.apply_translation([-109.782, -90.596, -0.0065])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / 'reference-interface-fit-test.stl'
    if not export_stl(build_interface(), path):
        raise RuntimeError('STL export failed')
    replica = trimesh.load(path)
    if not replica.is_watertight or len(replica.split()) != 1:
        raise RuntimeError('Expected one watertight mesh')
    fig, axes = plt.subplots(1, 2, figsize=(9, 5))
    for ax, height in zip(axes, [1.0, 3.0]):
        profiles = []
        for mesh in (source, replica):
            section = mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, height])
            profiles.append(sorted(
                [Polygon(p[:, :2]) for p in section.discrete],
                key=lambda p: p.area, reverse=True,
            ))
        if any(len(p) != 2 for p in profiles):
            raise RuntimeError(f'Expected outer profile and bore at Z={height}')
        for i, (original, rebuilt) in enumerate(zip(*profiles)):
            distance = original.boundary.hausdorff_distance(rebuilt.boundary)
            print(f'Z={height:g} mm, {"outer" if i == 0 else "bore"}: maximum boundary distance {distance:.4f} mm')
            if distance > 0.05:
                raise RuntimeError('Mating section differs from the source by more than 0.05 mm')
            ax.plot(*original.exterior.xy, color='#236aa0', linewidth=2, label='Source STL' if i == 0 else None)
            ax.plot(*rebuilt.exterior.xy, color='#d16b26', linestyle='--', linewidth=1, label='Recreated' if i == 0 else None)
        ax.set_aspect('equal')
        ax.set_title(f'Cross-section at Z = {height:g} mm')
        ax.set_xlabel('X (mm)'); ax.set_ylabel('Y (mm)')
        ax.legend(loc='upper right')
    fig.tight_layout()
    fig.savefig(OUTPUT / 'interface-section-comparison.png', dpi=160)
    plt.close(fig)
    print('Passed: sampled card sections agree within 0.05 mm. Bin neck and backing omitted.')


if __name__ == '__main__':
    main()
