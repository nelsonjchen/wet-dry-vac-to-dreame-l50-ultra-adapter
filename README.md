# Dreame L50 Ultra → wet/dry vacuum adapters

Parametric build123d models for routing a Dreame L50 Ultra dock's evacuation
path into an external wet/dry vacuum, without cutting the dock. There are two
vacuum-specific versions:

- **Stanley SL18129** — based on an approximately 30.75 mm hose connector.
- **DeWalt DXV05P-QT** — based on a measured cuff taper: 44.77 to 45.77 mm
  outside diameter over 62.24 mm.

Each version has a dock-side card adapter and a separate plug-in 90-degree
elbow. The second bend turns the hose connection downward.

## Models

| Vacuum | Dock adapter | Matching plug-in elbow |
| --- | --- | --- |
| Stanley SL18129 | [STL](models/hose-adapter-rev5.stl) · [STEP](models/hose-adapter-rev5.step) | [STL](models/stanley-to-stanley-90-elbow.stl) · [STEP](models/stanley-to-stanley-90-elbow.step) |
| DeWalt DXV05P-QT | [STL](models/hose-adapter-rev5-dewalt-measured.stl) · [STEP](models/hose-adapter-rev5-dewalt-measured.step) | [STL](models/dewalt-to-dewalt-90-elbow.stl) · [STEP](models/dewalt-to-dewalt-90-elbow.step) |

### Stanley

![Stanley dock adapter and separate elbow](docs/images/stanley-adapter.webp)

### DeWalt

![DeWalt dock adapter and separate elbow](docs/images/dewalt-adapter.webp)

These are renders of the actual model meshes, not photographs of finished parts.
The finished DeWalt setup is in use. Nelson reports no hairballs since putting
it into service. Earlier card and socket coupons helped establish the fit during
development. The repository also includes Stanley and cross-vacuum variants;
check the measured dimensions when adapting them to another hose or dock.

## Edit and regenerate

Install [uv](https://docs.astral.sh/uv/), then:

```sh
uv sync --locked
uv run python cad/export_models.py
```

The initial inlet and mating-interface dimensions came from the
[MakerWorld reusable dust-bin model](https://makerworld.com/en/models/1624511-mova-dreame-reusable-dust-bin-no-filters-needed#profileId-1715080).
Those dimensions were recreated in build123d and then refined through
measurements and physical fit feedback for this adapter. The source archive
itself is not redistributed.

The source is under [cad/build123d/](cad/build123d/). The main entry points are
`rev5_full_adapter.py` for Stanley, `dewalt_rev5_adapter.py` for DeWalt, and
`dewalt_addon_elbow.py` for the separate elbows. `elbow_variants.py` also
contains a Stanley-to-DeWalt variant and slicing orientations.

Dimensions are in millimetres. STEP files retain solid geometry; STL files
are meshes. The elbow's exported position is a starting position for slicing,
not a claim that it prints without supports. See the
[development notes](DEVELOPMENT.md#elbow-variants-and-slicing-study-2026-10-04)
for the recorded slicing work.

Optional model renders require Blender:

```sh
blender --background --python cad/render_models.py
```

PNG renders are written to the ignored `cad/exports/blog/` directory.

## Status and background

The project handles dense dog hair that the stock dock struggled to empty.
The path is robot → existing dock evacuation path → printed adapter and hose
→ external wet/dry vacuum. The design remains removable. Nelson switched from
the Stanley to the newer DeWalt because it was quieter.

Home Assistant switches the external vacuum through a Sonoff S31 running
ESPHome, following the Dreame's auto-empty status. The plug has an independent
two-minute cutoff in its firmware and boots with its relay off. The earlier relay-only tests in the development notes were milestones
on the way to the working setup. If adapting the design, account for the
robot's bin, flaps and seals and use a motor-rated switching device.

Nelson supplied the idea, measurements and physical fit feedback. Codex did the
CAD implementation and helped with the automation and documentation.

The [development notes](DEVELOPMENT.md) preserve the historical revisions,
measurements and fit reports, including questions that were still open then. [Measurement notes](measurements/) record
the interface provenance; the supplied third-party reference archive is not
redistributed here.
