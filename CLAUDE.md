# Projectiles: project notes for Claude

3D-printed projectiles for an air-compressed potato cannon, built by Russ and his
brother-in-law. Designs are written as code that generates STL files, which are
sliced in Bambu Studio and printed.

These are the current agreed rules. They can change: when Russ changes one,
update this file in the same commit as the design change.

## How to work with Russ (his rules for every response)

Russ has ADHD: he's very productive when a task is set up so he can start
immediately, and stalls on vague or open-ended instructions. Every response:

1. Start with "Do this next:" and one specific action, or "Nothing for you to
   do right now" and why.
2. Numbered steps, one action per step. Never two actions in one step.
3. Exact link for every place he needs to go (the specific page, not the home
   page). Name the exact button, menu, tab or setting as it appears on screen.
4. After each step, say what he should see if it worked.
5. A time estimate for each task (e.g. "about 5 minutes").
6. End each task with "You're done when you see…".
7. Decisions: recommend one option and why in one or two sentences, so he can
   reply "yes". Several decisions go in one short numbered list.
8. Keep it short. Background goes at the bottom under a "Background" label.
9. Never say "check the dashboard", "update the settings" or "configure it"
   without the exact location and the exact name of the thing to change.
10. If unsure where something is in an app (layouts change), say so and tell
    him exactly what to look for by name.
11. If something is missing, ask one clear question at a time.
12. Do everything that can be done without him; only bring him in for what
    truly needs him.

## Hard constraints

- **Max width: 38.0 mm.** No part of any projectile may exceed 38.0 mm in diameter
  or width, fins and rings included. Verify this from the generated STL, not just
  from the parameters. (Was briefly 38.5 after a dart slid in with a little play;
  Russ set it back to 38.0. A wad behind the dart takes up the seal.)
- **Material: PCTG.** Use PCTG for all mass, CG, and strength calculations
  (density about 1.23–1.27 g/cm³; use 1.25 unless a measured print weight says
  otherwise).
- **Mostly printed; metal only where Russ says.** The default is still
  all-printed PCTG. Approved exceptions: a metal chain or steel cable joining
  the chain-shot balls; a steel rod down the middle of some dart variants
  (3/8 in. plain steel round rod, cut to length); non-printed parts (fabric,
  rubber band) for a parachute or streamer on the high-altitude projectile.
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
- **Bearing diameter:** 38.0 mm (Russ's call), fired behind a wad (`designs/wad/`).
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

## Designs

- `designs/mk1/`: Mk1 Ducted-Tail Dart (current). See its README for numbers.
- Weight distribution: without metal, adding plastic near the middle (thicker
  walls) doesn't move the CG forward. What works: a longer body (fins farther
  back), a shorter/lighter tail ring, and keeping hollow space behind the CG.
- **Whistle work is parked (Russ's call).** Focus is non-whistle projectiles.
  Russ may revisit the death whistle later; the notes below keep what was learned.
- `designs/mk1w/`: Mk1-W Screaming Dart, Mk1 with a ram-air death whistle inside.
  Rev A (2.8 mm holes, from a mis-measurement) was silent. Rev B copies whistle
  test piece D's internals; Russ: it sounds like a sports whistle, not menacing.
  Untried ideas for a Rev C: outlets right under the ball, seal off the long
  tail tube, ~3.5 mm ball gap.
- `designs/chain-shot/`: two identical solid 38 mm balls joined by a metal chain
  or cable (store-bought).
  - As round as a supportless print allows: the only flat is a small spot on the bottom, with a 47 deg cone.
  - Anchor: the cable loop (or chain end link) goes up an 8.5 mm hole from the
    bottom flat. A thick (7 mm) house-section snap pin pushes in through the
    side hole and the loop.
    - Its head stops it going further in.
    - Its split end's two hooks spring out past a square ledge so it can't back out.
    - To remove it, squeeze the hooks with pliers through the far opening and push.
    - Prong strain on snapping is ~2%. A pull loads the ball in compression.
    - Steel cable (1/16-3/32 in., crimped loops) is recommended. A chain's end link
      needs an inside opening of at least ~8 x 11 mm.
  - `chain_shot_slug.scad`: 38 x 38 mm cylinder (49 g). It has no overhangs, so it prints
    clean; Russ's round balls came out fuzzy on their underside. Same snap pin,
    with ends trimmed flat (`chain_shot_slug_pin.stl`).
  - `chain_shot_mine.scad`: sea-mine version with thick 8 mm horns. A ring of 5 points
    55 deg up, plus 1 on top; horns on the underside can't print without support.
    It stays inside the 38 mm width.
- `designs/flechette/`: steel flechette, an 8 x 150 mm hardened linear rod (59 g),
  with push-on printed parts (very tight crush-rib sockets, no glue).
  - Noses: spike or ogive (ogive is the default: it's best at subsonic speeds and tougher). Tails: 4 fins, a windowed basket, or the basket with
    twisted inner vanes for gentle spin.
  - Three-petal sabot (36.6 g, solid 4 mm base): 38 mm rear band and front band ~95 mm apart,
    hollow fin cavity, slim waist, front ring scoop that opens it at the muzzle.
    Radial V-key ridges and grooves align the petals without stopping separation.
  - The tail sits on the sabot base: air pushes base -> tail -> rod.
  - 150 mm rod chosen over 100 or 200 mm (see the README).
- `designs/wad/`: wad cup fired behind the dart: 38.0 mm, 5 mm pusher disc,
  22 mm skirt with a thin flared lip that pressure seals against the barrel.
  The long skirt keeps it from cocking or flipping. Prints disc-down, no supports.
- `designs/fit-test/`: barrel fit rings at 38.2 / 38.5 / 38.8 mm (from the
  38.5 mm period; the darts are now 38.0 mm).
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
  ≤ 38.0 mm, report volume and estimated PCTG mass, and render preview PNGs for
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
- `tools/check_stl.py part.stl`: watertight, max diameter vs 38.0 mm, mass, CG.
- `tools/overhangs.py part.stl`: finds surfaces that would need supports.
- `tools/islands.py part.stl`: finds floating regions (layers starting in mid-air),
  the thing Bambu Studio warns about. Strict by default; Bambu flags even tiny ones.
- `tools/stability.py design.scad part.stl`: Barrowman CP estimate and stability
  margin (Mk1-style geometry; adapt for other layouts).
- `tools/strength.py a.stl b.stl`: weakest-layer bending section modulus, for
  comparing designs.
- `tools/section.py part.stl out.png --angle DEG`: true lengthwise cross-section.
- Use `-D '$fn=36' -D profile_steps=24` for fast low-res iterations (~13 s).
