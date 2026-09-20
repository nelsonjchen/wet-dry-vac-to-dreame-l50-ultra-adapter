# REV 2 trailing-width trial

Reference: `scans/2026-09-19/vacuum-bag-interface-with-library-card-200dpi.jpg`.
User reports REV 1 fits into the dock but can wiggle out, and identifies the
original's wider end as the trailing end opposite the insertion arrow.

Calibration: assuming the supplied library card is ISO ID-1 (85.60 x 53.98 mm),
a minimum-area rectangle around its colored image region measures approximately
673.64 x 425.03 pixels: 7.870 and 7.874 pixels/mm. This agrees with 200 dpi,
not the requested 600 dpi. Colored-region extraction is approximate.

Grayscale edge-gradient samples on the bag interface:

| Scan X (pixels) | Upper Y | Lower Y | Width (pixels) |
| --- | --- | --- | --- |
| 1040 | 395 | 1022 | 627 |
| 1080 | 395 | 1021 | 626 |
| 1360 | 414 | 983 | 569 |
| 1440 | 411 | 981 | 570 |
| 1520 | 409 | 978 | 569 |

These imply roughly 79.6 mm versus 72.3 mm, a 7–8 mm difference. Shadows,
raised plastic, slight rotation, and adjacent bag fabric limit accuracy.
The whole scanned outline is NOT being adopted as exact geometry.

Trial choice: preserve REV 1's 70 mm insertion width, 101.6 mm length, 3.4 mm
thickness, central 33 mm bore, and seal pocket. Increase only the trailing
width to 78 mm (4 mm per side), with a nominal 15 mm rear section and 10 mm
transition to the original width. Corners are rounded R6. Transition lengths
are approximate design choices consistent with the scan, not precise tracing.

Export: `cad/exports/reference-interface-rev2-fit-test.stl`, labeled REV 2.
No elbow. Full REV 1 exports/defaults remain unchanged pending physical fit.
