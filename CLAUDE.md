# Projectiles: project notes for Claude

3D-printed projectiles for an air-compressed potato cannon, built by Russ and his
brother-in-law. Designs are written as code that generates STL files, which are
sliced in Bambu Studio and printed.

These are the current agreed rules. They can change: when Russ changes one,
update this file in the same commit as the design change.

## Hard constraints

- **Max width: 38.0 mm.** No part of any projectile may exceed 38.0 mm in diameter
  or width, fins and rings included. Verify this from the generated STL, not just
  from the parameters.
- **Material: PCTG.** Use PCTG for all mass, CG, and strength calculations
  (density about 1.23–1.27 g/cm³; use 1.25 unless a measured print weight says
  otherwise).
- **Printing only. No metal inserts.** No bolts, nuts, steel balls, or other
  non-printed parts. Every piece must be printable in PCTG.
- **Slicer: Bambu Studio.** Output STL files that import cleanly into it.

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
- **Moderate spin, not maximum spin.** Spin from canted or twisted fins should be
  enough to average out print imperfections. Extra cant adds drag and costs range.
- **Support-free printing.** Internal voids and overhangs should print without
  supports (cone-tipped channels, roughly 45° or steeper overhangs).

## Proposed, not yet confirmed

- **Length:** Gemini's Rev 15 dart is 115 mm. Russ said that length or a little
  longer is fine; 115–125 mm is the working range.
- **Bearing diameter:** about 37.6 mm to leave clearance for PCTG's slight
  oversizing and elephant's foot. Confirm against test prints and the barrel's
  actual inner diameter.
- **Printed core rod:** a hex PCTG rod printed lying flat (layers along its
  length), dropped into a central channel during a pause at height so it's
  captured inside the dart. Waiting on Russ's OK for the pause step.

## Open questions

- Cannon specs: barrel inner diameter, barrel length, chamber volume, firing
  pressure. Needed for velocity, spin, and range estimates.
- Whether darts are fired bare or behind a wad or sabot.

## Workflow

- Designs are parametric OpenSCAD (`.scad`), with all key dimensions as named
  parameters at the top of the file.
- For every design change: render the STL, check it's watertight, check max width
  ≤ 38.0 mm, report volume and estimated PCTG mass, and render preview PNGs for
  Russ to review.
- Record each revision in git with a commit message describing what changed and
  why. Note print settings that matter (pause layer, infill, walls) in the design
  file's header comment.
- Use inches and pounds in conversation when it helps, but keep design files in
  millimeters (what Bambu Studio expects).

## Tooling notes (cloud container)

- `apt-get install -y openscad xvfb` provides OpenSCAD (2021.01) and a virtual
  display for PNG renders.
- Render STL: `openscad -o out.stl design.scad`
- Render PNG: create a wrapper `.scad` containing `import("out.stl");`, then run
  `xvfb-run -a openscad -o view.png --imgsize=900,1100 --camera=0,0,57,70,0,25,280 wrapper.scad`
- `pip install trimesh manifold3d` for watertightness, bounds, and volume checks.
