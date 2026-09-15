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

## Measurements to capture

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
