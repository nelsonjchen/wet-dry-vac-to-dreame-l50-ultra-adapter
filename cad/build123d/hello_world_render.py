"""Render a small build123d "hello world" plaque.

This is intentionally a visual smoke test for text, extrusion, boolean
geometry, tessellation, and export—not a measured part for the Dreame dock.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build123d import (
    Align,
    Cylinder,
    Pos,
    RectangleRounded,
    Text,
    export_step,
    export_stl,
    extrude,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = PROJECT_ROOT / "cad" / "exports"
RENDER_PATH = EXPORT_DIR / "build123d-hello-world.png"
STEP_PATH = EXPORT_DIR / "build123d-hello-world.step"
STL_PATH = EXPORT_DIR / "build123d-hello-world.stl"


def build_hello_world():
    """Return the plaque, the two raised text lines, and their union."""

    plaque = extrude(RectangleRounded(100, 48, 5), amount=4)
    for x in (-42, 42):
        plaque -= Pos(x, 0, 0) * Cylinder(
            2.5,
            4,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    hello = Pos(0, 8, 4) * extrude(Text("HELLO", font_size=18), amount=2)
    world = Pos(0, -12, 4) * extrude(Text("WORLD", font_size=18), amount=2)
    complete_model = plaque + hello + world
    return plaque, hello, world, complete_model


def polygons_for(shape, tolerance=0.08):
    """Convert a build123d shape tessellation into matplotlib polygons."""

    vertices, triangles = shape.tessellate(tolerance)
    return [
        [
            (float(vertices[index].X), float(vertices[index].Y), float(vertices[index].Z))
            for index in triangle
        ]
        for triangle in triangles
    ]


def add_rendered_model(axis, shape):
    polygons = polygons_for(shape)
    colors = [
        "#f2b84b" if sum(point[2] for point in polygon) / 3 > 4.01 else "#4f78a8"
        for polygon in polygons
    ]
    axis.add_collection3d(
        Poly3DCollection(
            polygons,
            facecolors=colors,
            edgecolors="none",
            linewidths=0,
        )
    )


def render(complete_model):
    figure = plt.figure(figsize=(10, 6), dpi=180)
    axis = figure.add_subplot(projection="3d")
    axis.set_facecolor("#f3efe7")
    figure.patch.set_facecolor("#f3efe7")

    add_rendered_model(axis, complete_model)

    axis.set_xlim(-55, 55)
    axis.set_ylim(-30, 30)
    axis.set_zlim(-2, 14)
    axis.set_box_aspect((110, 60, 16))
    axis.view_init(elev=46, azim=-58)
    axis.set_axis_off()
    figure.subplots_adjust(left=0, right=1, bottom=0, top=1)
    figure.savefig(RENDER_PATH, dpi=180, bbox_inches="tight", pad_inches=0.12)
    plt.close(figure)


def main():
    plaque, hello, world, complete_model = build_hello_world()
    if not complete_model.is_valid:
        raise RuntimeError("build123d produced an invalid hello-world model")

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_step(complete_model, STEP_PATH)
    export_stl(complete_model, STL_PATH)
    render(complete_model)

    bounds = complete_model.bounding_box()
    print("build123d hello-world render passed")
    print(f"bounds_min={bounds.min}")
    print(f"bounds_max={bounds.max}")
    print(f"render={RENDER_PATH}")
    print(f"step={STEP_PATH}")
    print(f"stl={STL_PATH}")


if __name__ == "__main__":
    main()
