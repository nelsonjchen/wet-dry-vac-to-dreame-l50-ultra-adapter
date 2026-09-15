"""Small build123d workflow test for the L50 adapter concept.

The dimensions in this file are placeholders. They intentionally describe a
generic collar-to-hose adapter so the CAD toolchain can be evaluated before
real L50 measurements are available.
"""

from pathlib import Path

from build123d import Align, Cone, Cylinder, Pos, Rot, export_step, export_stl


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = PROJECT_ROOT / "cad" / "exports"


# Placeholder geometry only. Replace these with measured values before using
# the resulting model as an L50 part.
COLLAR_OUTER_DIAMETER = 64.0
COLLAR_INNER_DIAMETER = 52.0
COLLAR_HEIGHT = 18.0
TRANSITION_HEIGHT = 24.0
HOSE_OUTER_DIAMETER = 38.0
HOSE_INNER_DIAMETER = 32.0
HOSE_STRAIGHT_HEIGHT = 20.0

RELIEF_BOSS_DIAMETER = 12.0
RELIEF_BORE_DIAMETER = 8.0
RELIEF_BOSS_LENGTH = 12.0


def cylinder(radius: float, height: float, z: float = 0.0):
    """Create a Z-aligned cylinder with its bottom at ``z``."""

    return Pos(0, 0, z) * Cylinder(
        radius,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def build_adapter():
    """Build a hollow collar, tapered transition, hose outlet, and relief boss."""

    collar_outer_radius = COLLAR_OUTER_DIAMETER / 2
    collar_inner_radius = COLLAR_INNER_DIAMETER / 2
    hose_outer_radius = HOSE_OUTER_DIAMETER / 2
    hose_inner_radius = HOSE_INNER_DIAMETER / 2

    collar = cylinder(collar_outer_radius, COLLAR_HEIGHT)
    collar -= cylinder(collar_inner_radius, COLLAR_HEIGHT)

    outer_transition = Pos(0, 0, COLLAR_HEIGHT) * Cone(
        collar_outer_radius,
        hose_outer_radius,
        TRANSITION_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    hose_outlet = cylinder(
        hose_outer_radius,
        HOSE_STRAIGHT_HEIGHT,
        COLLAR_HEIGHT + TRANSITION_HEIGHT,
    )

    inner_transition = Pos(0, 0, COLLAR_HEIGHT) * Cone(
        collar_inner_radius,
        hose_inner_radius,
        TRANSITION_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    hose_bore = cylinder(
        hose_inner_radius,
        HOSE_STRAIGHT_HEIGHT,
        COLLAR_HEIGHT + TRANSITION_HEIGHT,
    )

    adapter = collar + outer_transition + hose_outlet
    adapter -= inner_transition + hose_bore

    # A simple side boss gives the eventual adjustable air-bleed a place to
    # attach. Its location is intentionally generic until the real adapter
    # envelope and relief hardware are selected.
    relief_z = COLLAR_HEIGHT / 2
    relief_boss = (
        Pos(collar_outer_radius - 1.0, 0, relief_z)
        * Rot(0, 90, 0)
        * Cylinder(
            RELIEF_BOSS_DIAMETER / 2,
            RELIEF_BOSS_LENGTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
    relief_bore = (
        Pos(0, 0, relief_z)
        * Rot(0, 90, 0)
        * Cylinder(
            RELIEF_BORE_DIAMETER / 2,
            collar_outer_radius + RELIEF_BOSS_LENGTH + 2.0,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )

    return adapter + relief_boss - relief_bore


def main() -> None:
    adapter = build_adapter()
    if not adapter.is_valid:
        raise RuntimeError("build123d produced an invalid adapter solid")

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    step_path = EXPORT_DIR / "build123d-adapter-test.step"
    stl_path = EXPORT_DIR / "build123d-adapter-test.stl"

    export_step(adapter, step_path)
    export_stl(adapter, stl_path)

    bounds = adapter.bounding_box()
    print("build123d adapter test passed")
    print(f"volume_mm3={adapter.volume:.2f}")
    print(f"bounds_min={bounds.min}")
    print(f"bounds_max={bounds.max}")
    print(f"step={step_path}")
    print(f"stl={stl_path}")


if __name__ == "__main__":
    main()
