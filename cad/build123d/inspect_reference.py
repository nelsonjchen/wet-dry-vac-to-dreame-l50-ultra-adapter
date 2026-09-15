"""Render the supplied reference meshes for interface identification."""
import argparse
import io
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh

ARCHIVE = Path('/Users/nelson/Downloads/Dreame+Dust+Bin+-+3MF+-+V7_stls.zip')
OUTPUT = Path(__file__).resolve().parents[1] / 'exports'

def load_main(archive_path=ARCHIVE):
    with zipfile.ZipFile(archive_path) as archive:
        name = next(n for n in archive.namelist() if 'MAIN' in n)
        return trimesh.load(io.BytesIO(archive.read(name)), file_type='stl')

def render_mesh(mesh, output, views):
    fig = plt.figure(figsize=(15, 9))
    light = np.array([0.3, -0.5, 0.8])
    shade = 0.5 + 0.5 * np.abs(mesh.face_normals @ light)
    colors = np.column_stack([shade * .45, shade * .7, shade * .9, np.ones(len(shade))])
    for i, (elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 3, i + 1, projection='3d')
        ax.add_collection3d(Poly3DCollection(mesh.triangles, facecolors=colors, edgecolors='none', linewidths=0, antialiased=False))
        for setter, low, high in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), mesh.bounds[0], mesh.bounds[1]):
            setter(low, high)
        ax.set_box_aspect(np.maximum(mesh.extents, 1))
        ax.set_proj_type('ortho')
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
        ax.set_title(f'elev={elev}, azim={azim}')
    fig.tight_layout()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=130)
    plt.close(fig)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ARCHIVE)
    args = parser.parse_args()
    mesh = load_main(args.archive)
    render_mesh(mesh, OUTPUT / 'reference-main.png', [(20,-65),(20,115),(90,-90),(0,-90),(0,0),(0,90)])
    render_mesh(mesh.slice_plane([0,0,12], [0,0,-1]), OUTPUT / 'reference-interface.png', [(25,-65),(25,115),(90,-90),(0,-90),(0,0),(-90,-90)])
