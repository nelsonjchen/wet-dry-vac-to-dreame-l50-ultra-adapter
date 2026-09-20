# Dreame L50 Ultra → Wet/Dry Vac Adapter

A reversible, 3D-printable adapter concept for using an external wet/dry vacuum to evacuate the dust bin of a Dreame L50 Ultra when the stock dock struggles with dense dog hair and other fibrous debris.

> Status: concept / measurement phase. No dimensions or safety claims in this repository should be treated as validated until they have been measured and tested on real hardware.

## The idea

The first prototype will treat the external wet/dry vacuum as the collection system while leaving the Dreame dock and robot unmodified:

```text
Dreame robot
    │
    ▼
stock dock evacuation path
    │
    ▼
genuine Dreame bag collar
    │
    ▼
printed adapter + vacuum-relief bleed
    │
    ▼
short 1¼ in. hose
    │
    ▼
wet/dry vacuum
```

The preferred way to satisfy the dock's bag-presence detection is to reuse the collar/handle assembly from a sacrificial Dreame bag. The adapter should preserve the original insertion depth, sealing surfaces, and any feature the dock uses to detect that a bag is installed. Electrically bypassing the sensor is a later experiment, not the starting point.

## Goals

- Remove hairballs and packed debris that the stock auto-empty cycle leaves behind.
- Keep the adapter reversible and avoid cutting or opening the Dreame dock for the initial prototype.
- Fit beneath the normal dust-compartment cover if the geometry allows it.
- Use a short, compact hose suitable for a space-constrained installation.
- Keep the design parametric so collar dimensions, hose size, clearances, and relief-port settings can be adjusted without rebuilding the model from scratch.
- Document measurements, test results, and failure modes instead of treating the first successful print as final.

## Non-goals for the first version

- Replacing or modifying the Dreame dock's internal blower.
- Permanently defeating a safety interlock.
- Assuming that more vacuum is always better.
- Designing around a particular smart-home trigger before the mechanical path is proven.

## Proposed prototype sequence

1. Photograph and measure an unused bag collar and the empty bag slot.
2. Test whether the genuine collar alone clears the dock's “bag missing” condition.
3. Model only the collar interface and a simple hose outlet.
4. Print a low-cost fit-check version before printing a full-strength adapter.
5. Verify that the adapter seals, latches, and remains removable with the cover closed.
6. Add an adjustable vacuum-relief / air-bleed path.
7. Test with the wet/dry vacuum at low exposure first, then increase suction gradually.
8. Add automatic triggering only after the airflow path is reliable.

## Safety notes

This adapter connects a high-power motor to a small robot-vacuum duct and dust bin. A blockage could expose the robot's seals, flaps, filter, or plastic housing to substantially more vacuum than the stock dock produces.

- Use an adjustable bleed or relief path during testing.
- Start with short, supervised runs and a conservative runtime limit.
- Do not leave the wet/dry vacuum unattended until the system has demonstrated reliable shutoff.
- Keep the wet/dry vacuum's required filter and any manufacturer-required separator in place.
- Verify that the switching device is rated for the vacuum motor's inrush and inductive load.
- Stop immediately if the robot bin, dock, hose, or adapter deforms, overheats, leaks, or makes an abnormal sound.
- This is a hobby prototype. You are responsible for the electrical, mechanical, fire, noise, and warranty implications of your installation.

## CAD direction

OpenSCAD is still a good starting point for this project. The first adapter is mostly parameterized solids and boolean operations: collars, cylinders, wall thicknesses, tapers, hose transitions, mounting clearances, and repeated fit-check revisions. Its script-based workflow also makes the measurements and design assumptions visible in version control. See the [OpenSCAD documentation](https://openscad.org/documentation).

The plan is not to treat OpenSCAD as a permanent constraint. Re-evaluate if the project needs any of the following:

- imported scan or STEP geometry that must be edited interactively;
- complex freeform surfaces or unusually smooth lofts;
- assemblies with many constrained parts;
- automated export and parameter sweeps in Python.

For the last case, [CadQuery](https://cadquery.readthedocs.io/en/stable/) is a reasonable next option because it provides scripted parametric CAD and can export formats such as STEP and 3MF. For the first three cases, a conventional feature-based CAD tool may become more productive. Until those needs appear, OpenSCAD keeps the prototype small and easy to iterate.

### build123d experiment

This repository also includes a small [build123d test model](cad/build123d/adapter_test.py). It uses placeholder dimensions to exercise a Python-based parametric workflow, boolean modeling, and STEP/STL export. It is not an L50-fit adapter yet.

Run it with:

```sh
uv run python cad/build123d/adapter_test.py
```

The generated files are written under `cad/exports/` and intentionally remain ignored by Git. If this workflow feels better once real measurements arrive, build123d is a credible candidate for the main implementation rather than just a test tool.

For a visual smoke test, render the small raised-text model:

```sh
uv run python cad/build123d/hello_world_render.py
```

## Measurements to capture

### Hose socket concept

For the user's approximate 30.75 mm hose-end measurement, the standalone
coupon command `uv run python cad/build123d/socket_fit_test.py` exports
`cad/exports/socket-fit-test-30p75.stl`. Print narrow end on the bed and wide
mouth up, with no supports. Its open-ended 35 mm socket tapers from 32.15 mm
mouth ID to 30.15 mm root ID, with the same 1.5 mm entry chamfer and 0.5 mm
outer-mouth rounding. Try a gentle push fit; do not force it. An upright coupon
may print differently from a horizontally oriented final elbow. The user reports
that this coupon fits very well and that card insertion works. The main REV 1
adapter now uses the same socket dimensions. Next test is the full PLA adapter
without TPU, leaving its blind gasket groove empty. Full assembly clearance,
air sealing, and suction performance remain unverified; add TPU later if needed.

`cad/build123d/hose_socket_concept.py` adds a **90-degree elbow with a horizontal
socket aimed down-right in top view**, automatically limited to preserve a
3 mm clear strip inside the card's +X edge.
The bend keeps a 33 mm round passage, then transitions over 6 mm
to the socket. Defaults use the **approximately measured 30.75 mm connector OD** for the
Stanley SL18129, with a **30.15 mm root / 32.15 mm mouth tapered bore** before
the entry chamfer. The taper is centered on OD + 0.4 mm diametral clearance.
Defaults are 2 mm diametral taper, 35 mm insertion depth (including a 1.5 mm entry
chamfer), 3 mm walls, and a 24 mm bend centreline radius.
Default XY angle is calculated from the pipe/support footprint; elevation defaults
to `--tilt-up 0`. An explicit `--exit-angle` overrides the clearance constraint.
Measure the hose connector's outside diameter; nominal hose size is not that
measurement. Dock cover clearance, seal/retention, and relief remain unresolved.
Use `--socket-taper` to tune the mouth-minus-root diameter (0 gives a straight
bore), and `--insertion-depth` to tune engagement length. These are provisional
push-fit dimensions, not a verified fit; do not force the hose into the card.

```sh
uv run --with ocp_viewer python cad/build123d/hose_socket_concept.py --show
# Substitute the measured connector OD:
uv run python cad/build123d/hose_socket_concept.py --connector-od 38 --clearance 0.4
# Aim the elbow toward another side of the compartment if needed:
uv run --with ocp_viewer python cad/build123d/hose_socket_concept.py --exit-angle 90 --show
```

The default exit points slightly right of -Y, away from the +Y insertion arrow.
Height and hose insertion space
still need checking against the compartment.

A solid pedestal fills beneath the elbow/socket to its centreline, with the
air passage subtracted through it. Its underside is coplanar with the card,
and rotates with the outlet. Its local width is 39–44.4 mm. Automatic aiming
keeps the entire pipe/support footprint at or inside X=32 mm, preserving 3 mm
to the right edge. Physical rail fit still needs checking; the fit-test card is unchanged. This removes
the external underside gap; the internal duct roof still needs slicer review.
The bend-end pedestal is trimmed to the elbow's curved outer envelope, removing
the projecting box corners without changing the internal passage.

Exports: `cad/exports/hose-elbow-concept.step` and `.stl`. Earlier upright
`hose-socket-concept` exports are superseded. This is a concept
for geometry review; use the separate interface part for the initial dock fit test.

### Reference interface

**Full REV 4 preview:** `uv run python cad/build123d/rev4_full_adapter.py`
REV 4 rigid models use 5.5 mm revision lettering and bold 5 mm project-name
lettering on two lines, `DREAME L50 ULTRA` / `VAC ADAPTER`, on the base.
The shorter insertion arrow is on the upper right. All markings are recessed 0.4 mm;
the part dimensions are unchanged by this labeling update.
exports `hose-adapter-rev4.stl` and STEP, leaving the earlier full adapter files
untouched. It shares REV 4's fit dimensions, but omits the pull tab, plus the successfully
tested 30.75 mm-based tapered socket. No TPU is included in the rigid export;
the blind gasket groove remains for optional later use. REV 4's standalone
card was not printed; only REV 3's fit improvement was physically reported.
The centered pull tab remains on the standalone test card only, since the full
adapter's pipe/support overlaps it.

**REV 4 pull-tab trial:** `uv run python cad/build123d/rev4_card_fit_test.py`
exports `reference-interface-rev4-fit-test.stl`. REV 3 was reported to fit much
better. Its fit outline is preserved; a centered bag-style flat pull tab adds
14 mm in -Y, 24 mm wide, with R6 end corners and the card's existing edge
treatments. These tab dimensions are prototype choices inspired by the original
bag, not an exact scan trace. Tab thickness remains 3.4 mm, with no through-hole
or raised handle. Check finger access and compartment clearance. Earlier test
exports and the full REV 1 adapter remain unchanged.

**REV 3 card-only trial:** `uv run python cad/build123d/rev3_card_fit_test.py`
exports `reference-interface-rev3-fit-test.stl`. Relative to REV 2, the trailing
+X edge moves from X=39 to X=42 mm; the -X edge stays X=-39 mm. The rear edge
moves from Y=-50.8 to Y=-31.8 mm (19 mm toward the hole). The 15 mm rear section
and 10 mm shoulder transition move with that edge, preserving the extension
shape rather than slicing it off. Overall length is 82.6 mm, maximum width
81 mm; insertion end remains Y=50.8, X=±35 mm. Hole, thickness and gasket seat
stay fixed. REV 1 full adapter and REV 2 exports are unchanged.

**REV 2 card-only width trial:** run `uv run python cad/build123d/rev2_card_fit_test.py`.
The separate `reference-interface-rev2-fit-test.stl` widens only the trailing
end to 78 mm while retaining the 70 mm insertion end. See
[scan measurements and assumptions](measurements/rev2-trailing-width.md).
The full adapter stays REV 1 until this outline has been physically checked.

Rigid prints carry a recessed **REV 1** label beside the insertion arrow on
the hose-facing side (4 mm font, 0.4 mm engraving depth). The TPU ring is
unmarked. `InterfaceDimensions.revision` controls this shared print revision;
bump it deliberately when making the next physical revision. It is independent
of the Git commit and is not automatically incremented by regeneration.

REV 1 finishing: 0.3 mm bottom card-perimeter chamfer, 0.2 mm gasket-pocket
entry chamfers (retaining undercut unchanged), and 0.5 mm outer socket-mouth
rounding. The existing upper card rounding and inner hose lead-in remain.

The TPU seal resembles an attached O-ring: a rounded bead extends **-Z toward
the dock**, 1 mm below the card's dock-facing surface. It presses in from -Z
into a blind annular dovetail groove (35 mm ID, 42 mm OD, 1.6 mm deep).
The +Z face remains solid above the groove: 1.8 mm backing, with a 1 mm radial
plastic rim separating it from the unchanged 33 mm airflow hole. The TPU
does not pass through the card or appear on its +Z face. The flexible widened
base fits behind the groove mouth for prototype retention. Both card and elbow
share this seat. Use the matching updated ring, not the earlier through-card seal.

`cad/exports/dock-gasket-tpu.stl` prints flange-flat, rounded sealing bead up;
total height is 2.4 mm. This print orientation is opposite its installed orientation
(installed Z=-1 to 1.4 mm). Regenerate with `reference_interface.py`. Dimensions
are adjustable in `InterfaceDimensions`. Compression and snap retention are
unverified: test insertion, pull-out, and sealing before powered use. Inspect
slicing of the blind groove and its undercut; support may be needed. This removes
the direct through-card pocket path but does not guarantee an airtight dock seal.

A 0.4 mm-deep arrow on the hose-side face marks the **provisional +Y insertion
direction**. The elbow exits down-right with a 3 mm right-edge margin. This relative direction
is user-specified; physical fit and compartment clearance remain unverified.

The current interface is a single 70 × 101.6 × 3.4 mm card with a Ø33 mm
rigid inlet. The source bin's neck and backing slab are omitted: the dock takes a
card, not a two-plate groove. The elbow now joins directly to the card.
The fit-test card can lie flat on the bed; the elbow still needs its own
orientation/support review. Physical dock fit and sealing remain unverified.

For compatibility with the previous support-access filename:

```sh
uv run --with ocp_vscode python cad/build123d/hose_socket_concept.py --support-access --show
```

This exports `cad/exports/hose-elbow-support-access.stl` and `.step` as aliases
of the current single-card elbow. Support-access slots have been removed from
both models: there is no trapped rail-gap overhang, and extra holes in the
single card could compromise the seal. Reimport STLs into saved slicer projects;
existing 3MF files are not updated automatically.

The supplied V7 dust-bin mesh has now been used to recreate an inlet and sliding
flange. See [the measurement record](measurements/v7-interface.md) for recovered
dimensions, comparison results, and known simplifications. Build its fit-test part:

```sh
uv run python cad/build123d/reference_interface.py
```

This reproduces the reference mesh's mating dimensions; physical L50 fit remains
unverified.

The first CAD model should not guess these values:

- collar outside dimensions and insertion depth;
- sealing surface profile and gasket location;
- latch, handle, tab, magnet, or optical-target geometry;
- bag-slot width, height, and nearby cover clearances;
- dock-side duct opening and centerline;
- hose inside diameter and outside diameter;
- minimum bend radius available in the installation;
- adapter wall thickness and print orientation constraints.

All measurements should be recorded in millimetres. Where a feature is uncertain, record a range and make the uncertainty explicit in the model parameters.

## Planned repository layout

```text
README.md                 project scope and test notes
cad/                      parametric source models
  openscad/                initial OpenSCAD implementation
  exports/                 generated STL/3MF/STEP files, when useful
measurements/             source measurements and annotated photos
tests/                    fit, airflow, and trigger test notes
```

Generated meshes should be treated as build outputs. The editable CAD source and the measurement record are the authoritative design artifacts.

## Open questions

- Does the original collar alone satisfy the L50 dock's bag-presence sensor?
- Is the collar interface shared with another Dreame model, or is it L50-specific?
- Does the stock DualBoost airflow need to remain available during external evacuation?
- What vacuum level and runtime clear a typical hairball without stressing the robot bin?
- Is a dock power signature, pressure switch, or Home Assistant event the most reliable trigger?
- Does the final adapter need a cyclone or debris pre-separator, or is the wet/dry vacuum tank sufficient?

## Working principle

Prototype the smallest reversible mechanical change first, measure what the dock actually does, and only then add automation or more aggressive suction. The intended result is a practical external evacuation path—not an irreversible modification to the robot or dock.
