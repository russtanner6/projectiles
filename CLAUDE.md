# Projectiles: project notes for Claude

3D-printed projectiles for an air-compressed potato cannon, built by Russ and his
brother-in-law. Designs are written as code that generates STL files, which are
sliced in Bambu Studio and printed.

These are the current agreed rules. They can change: when Russ changes one,
update this file in the same commit as the design change.

## Hard constraints

- **Max width: 38.5 mm.** No part of any projectile may exceed 38.5 mm in diameter
  or width, fins and rings included. Verify this from the generated STL, not just
  from the parameters. (Raised from 38.0 after Russ's first barrel test: a dart
  slid in with a tiny bit of play. Confirm with `designs/fit-test/` rings.)
- **Material: PCTG.** Use PCTG for all mass, CG, and strength calculations
  (density about 1.23–1.27 g/cm³; use 1.25 unless a measured print weight says
  otherwise).
- **Printing only. No metal inserts.** No bolts, nuts, steel balls, or other
  non-printed parts. Every piece must be printable in PCTG.
- **Slicer: Bambu Studio.** Output STL files that import cleanly into it.
- **No supports.** Every design must print nose-up with supports turned off,
  internal cavities included. No downward-facing surface may be flatter than
  45° from horizontal (cone-tipped channels and roofs, no flat ceilings). Verify
  with `tools/overhangs.py` on the STL.

## Agreed design principles

- **Print orientation is nose-up** (base on the bed). That makes layer lines
  perpendicular to the projectile's axis, so layer splitting under bending is the
  main failure mode. Design against it.
- **Avoid abrupt infill-density changes along the length.** Russ's earlier prints
  used stepped infill (e.g. 100% top, 40% middle) and broke at layer lines,
  especially at the density transitions. Prefer one uniform high-density setting
  (gyroid, 6+ walls) and shape mass distribution with modeled geometry, such as a
  hollow tail pocket with a support-free cone top, instead of infill steps.
- **No narrow necks.** Bending strength scales with diameter cubed. Keep the body
  thick from nose to tail; the 14 mm stem in Gemini's Rev 15 dart is an example
  of what to avoid.
- **Forward CG for stability.** Get weight forward with geometry, not infill
  steps.
- **No thin lips or sharp edges on the outside**, especially at the nose: round
  over any opening (e.g. Mk1-W's inlet mouth) so impacts don't chip it.
- **Symmetry.** Everything must be on the axis or repeated evenly around it
  (holes, slots, internal parts) so the CG stays on the axis and the dart flies
  straight. Check the STL's CG x/y is ~0.
- **Moderate spin, not maximum spin.** Spin from canted or twisted fins should be
  enough to average out print imperfections. Extra cant adds drag and costs range.

## Proposed, not yet confirmed

- **Length:** Both darts are now ~133–135 mm. Russ approved lengthening past the
  original 115–125 mm range to move the CG forward relative to the fins
  (stability went from ~+0.62 to ~+0.75 cal).
- **Bearing diameter:** 38.5 mm (Russ's call). Not yet confirmed: the fit-test
  rings (38.2 / 38.5 / 38.8) will show which size slides with no play once
  printed in PCTG. Set `body_d` to the winner.
- **Barrel contact:** projectiles must bear on the barrel wall at two widely
  spaced full-diameter surfaces (e.g. a body band and a tail ring) so they don't
  wobble or tip in the barrel. Russ asked for this explicitly.

## Evaluated and rejected

- **Printed core rod** (PCTG rod printed flat, captured via pause at height):
  in Mk1 it would add only a few percent to the weakest layer's bending strength. Not
  worth the pause step. Revisit only if a design has a much larger core.

## Open questions

- Cannon specs: barrel inner diameter, barrel length, chamber volume, firing
  pressure. Needed for velocity, spin, and range estimates.
- Whether darts are fired bare or behind a wad or sabot.

## Designs

- `designs/mk1/`: Mk1 Ducted-Tail Dart (current). See its README for numbers.
- Weight distribution: without metal, adding plastic near the middle (thicker
  walls) doesn't move the CG forward. What works: a longer body (fins farther
  back), a shorter/lighter tail ring, and keeping hollow space behind the CG.
- `designs/mk1w/`: Mk1-W Screaming Dart, Mk1 with a ram-air death whistle inside.
  Rev A (2.8 mm holes, from a mis-measurement) was silent. Rev B copies whistle
  test piece D's internals. Waiting on Russ's print/blow test.
- `designs/fit-test/`: barrel fit rings at 38.2 / 38.5 / 38.8 mm.
- `designs/whistle-tests/`: four short test pieces. Results: A (skull copy) and
  D (dart-size + 22 mm × 8 mm inlet channel) scream like the skull; B and C (no
  channel) make sound but too high-pitched. The inlet channel is what gives the
  dart-size core its low scream: keep it in any whistle design.
- **Internal parts must survive impact.** Anything inside (like the whistle ball)
  must be tied to the outer wall so impact loads run along layers, not across
  them, and sized for a hard-ground stop (~25,000 g from 50 m/s in 5 mm).
- Russ's skull whistle (reference, not in the repo; source/license unknown):
  blown into a ~6 mm hole in the top through a ~3 mm wall; ~5.4 mm below is a
  ~7 mm hole with a short raised rim in a hollow ellipsoid ball (~32 mm, 1.2 mm
  shell), inside a chamber with a ~4 mm gap; air exits back slits and the open
  bottom. Measure features like these from zoomed sections, not coarse ones.
- Gemini's "Rev 15" dart is the reference for comparisons: weakest-layer
  section modulus ~733 mm³, estimated stability margin ~+0.8 cal. Its source isn't
  in the repo; Russ shared it only as an example.

## Workflow

- Designs are parametric OpenSCAD (`.scad`), with all key dimensions as named
  parameters at the top of the file.
- For every design change: render the STL, check it's watertight, check max width
  ≤ 38.5 mm, report volume and estimated PCTG mass, and render preview PNGs for
  Russ to review.
- Record each revision in git with a commit message describing what changed and
  why. Note print settings that matter (pause layer, infill, walls) in the design
  file's header comment.
- Use inches and pounds in conversation when it helps, but keep design files in
  millimeters (what Bambu Studio expects).

## Tooling

Setup in a fresh cloud container:
`apt-get install -y openscad xvfb && pip install trimesh scipy shapely rtree networkx matplotlib`

- `tools/render.sh design.scad`: STL (binary) + side/tail preview PNGs + checks.
- `tools/check_stl.py part.stl`: watertight, max diameter vs 38.5 mm, mass, CG.
- `tools/overhangs.py part.stl`: finds surfaces that would need supports.
- `tools/islands.py part.stl`: finds floating regions (layers starting in mid-air),
  the thing Bambu Studio warns about. Strict by default; Bambu flags even tiny ones.
- `tools/stability.py design.scad part.stl`: Barrowman CP estimate and stability
  margin (Mk1-style geometry; adapt for other layouts).
- `tools/strength.py a.stl b.stl`: weakest-layer bending section modulus, for
  comparing designs.
- `tools/section.py part.stl out.png --angle DEG`: true lengthwise cross-section.
- Use `-D '$fn=36' -D profile_steps=24` for fast low-res iterations (~13 s).
