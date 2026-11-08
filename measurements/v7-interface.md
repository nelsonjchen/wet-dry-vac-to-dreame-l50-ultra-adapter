# V7 reference inlet and sliding flange

Source supplied by the user: `Dreame+Dust+Bin+-+3MF+-+V7_stls.zip`, from the
[MakerWorld reusable dust-bin model](https://makerworld.com/en/models/1624511-mova-dreame-reusable-dust-bin-no-filters-needed#profileId-1715080).
Its inlet and mating-interface measurements were the starting reference;
later revisions were fine-tuned for this adapter using physical fit feedback.

- SHA-256: `a8e4d698d9315e869bab5a99be1ee444999cd803fef83ca99df1a5e2de68c678`
- Main mesh: `obj_2_Dreame Dust Bin - MAIN - STL - V7.stl`
- Other mesh: `obj_1_Dreame Dust Bin - DOOR - STL - V5.stl`
- Archive contains STL files only; no native CAD, compatibility information, or license text.
- Dimensions below assume millimetres; STL is unitless. L50 compatibility is unverified.

## Identified interface

The main bin is tilted about 35 degrees for printing. Its inlet flange lies near
the print bed (source Z = 0–3.4). The circular opening is approximately centred
at source X = 109.782, Y = 90.596. The inlet passes through a broad flange, a
narrower neck, and the bin floor. The narrower neck leaves room between the
flange and the bin for the receiving rails in the dock. This interpretation
comes from the mesh; the dock-side rails themselves are not included.

## Recovered nominal dimensions

| Feature | Dimension (mm) |
| --- | ---: |
| Through-hole diameter | 33 |
| Flange width × length | 70 × 101.6 |
| Flange thickness | 3.4 |
| Flange corner radius | 6 |
| Flange top edge round | approximately 0.6 |
| Neck width × length | 40 × 75 |
| Neck centre offset along Y from hole | +1.7 |
| Gap between flange top and backing underside | 3 |
| Nominal side ledge width, away from corner/edge rounds | 15 |

Nominal values are recovered from triangulated geometry, not original design
parameters. The file has a slight residual tilt and faceted circles. Avoid
interpreting extra decimal places as manufacturing precision.

## What was recreated

`cad/build123d/reference_interface.py` builds the flange, top edge round, neck,
and through-hole as editable build123d geometry. Its origin is the centre of
the inlet at the flange underside, with +Z pointing toward the future adapter.

The upper backing is a **simplified 85 × 75 × 2 mm rounded plate**, offset -5 mm
in X and +1.7 mm in Y. It replaces the irregular floor of the tilted bin.
Small neck-to-flange/backing junction rounds and the inlet's upper lip are
omitted. No gasket, sensor target, hose connection, or pressure-relief mechanism
has been added. The backing envelope and omitted details need physical checking.

## Validation and use

The build123d part is one valid solid, and its exported STL is one watertight
component. Comparison with source sections at Z = 1, 3, and 5 mm gives a maximum
boundary distance below 0.02 mm for the flange/neck outlines and bore after
removing source placement. These samples do not validate the simplified backing,
junction fillets, or physical dock compatibility.

```sh
uv run python cad/build123d/reference_interface.py
uv run --with ocp_vscode python cad/build123d/reference_interface.py --show
uv run --group reference python cad/build123d/compare_reference_interface.py --archive '/path/to/Dreame+Dust+Bin+-+3MF+-+V7_stls.zip'
uv run --group reference python cad/build123d/inspect_reference.py --archive '/path/to/Dreame+Dust+Bin+-+3MF+-+V7_stls.zip'
```

The viewer must already be running for `--show`. All exports and comparison
images go into ignored `cad/exports/`. The original ZIP remains in Downloads;
pass `--archive` if it moves. The source archive is not redistributed here.

Next step: print this small interface and check seating, sliding clearance,
cover clearance, seal contact, and bag detection on the actual L50. A successful
fit establishes the interface to use when adding the hose transition.
