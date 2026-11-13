# Projectiles: project notes for Claude

3D-printed projectiles for an air-compressed potato cannon, built by Russ and his
brother-in-law. Designs are written as code that generates STL files, which are
sliced in Bambu Studio and printed.

These are the current agreed rules. They can change: when Russ changes one,
update this file in the same commit as the design change.

## How to work with Russ (his rules for every response)

Russ has ADHD: he's very productive when a task is set up so he can start
immediately, and stalls on vague or open-ended instructions. Use discretion:
these rules are for responses where he has something to do (print, click,
buy, decide). When he's only asking a question and there's nothing for him to
act on, just answer it plainly and briefly, without the "Do this next" format.
When there are action items:

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

- **Width: 39.6 mm, every projectile, one size only (Russ).** Sabot bands, wad, Mk1,
  Mk1-R, Mk1-W, HF1 and the chain-shot ball, slug and mine are all 39.6 mm across
  (barrel ~40.1 mm by calipers). History: 38.0 at first, a brief 38.5, then barrel-sized
  parts at 39.7 / 39.0 / 38.6; 39.7 worked best and Russ settled on 39.6. Build no
  other sizes unless he asks. Verify from the STL with `--max-width 39.6`.
  Parts that ride inside the sabot (flechette noses and tails) stay sized to the sabot.
- **Material: PCTG.** Use PCTG for all mass, CG, and strength calculations
  (density about 1.23–1.27 g/cm³; use 1.25 unless a measured print weight says
  otherwise).
- **Mostly printed; metal only where Russ says.** The default is still
  all-printed PCTG. Approved exceptions: a metal chain or steel cable joining
  the chain-shot balls; a steel rod down the middle of flechettes and some
  dart variants; non-printed parts (fabric, rubber band) for a parachute or
  streamer on the high-altitude projectile.
- **Two rod sizes, always (Russ's rule).** Everything designed around a steel
  rod must come in both sizes, as a `rod_d` parameter with both STL sets built:
  - **8 mm**: hardened linear rod, or 5/16 in. (7.94 mm) Home Depot plain steel
    rod, which fits the same parts. The penetrator.
  - **1/2 in. (12.7 mm)**: Home Depot plain steel rod (or a 1/2 in. linear
    shaft). The heavy hitter, ~2.5x the mass. Metric 12 mm is 0.7 mm thinner
    and would be loose in these, so a 12 mm set (`12mm/`) is built too.
  Home Depot rod is mild steel: cheap practice rods that bend more easily on
  rocks or concrete; hardened rods are for real targets. Check stability for
  each size: a fatter rod weakens the fins (their span is capped by the sabot).
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
- **Bearing diameter:** 39.6 mm (Russ's call), fired behind a wad (`designs/wad/`).
- **Barrel contact:** projectiles must bear on the barrel wall at two widely
  spaced full-diameter surfaces (e.g. a body band and a tail ring) so they don't
  wobble or tip in the barrel. Russ asked for this explicitly.

## Evaluated and rejected

- **Printed core rod** (PCTG rod printed flat, captured via pause at height):
  in Mk1 it would add only a few percent to the weakest layer's bending strength. Not
  worth the pause step. Revisit only if a design has a much larger core.

## Open questions

- Cannon specs: barrel inner diameter (caliper: ~40.1 mm), barrel length, chamber volume, firing
  pressure. Needed for velocity, spin, and range estimates. Known: barrel ~4-5 ft;
  air from a VEVOR 8 L tire bead blaster, 85-116 psi (120 max). Estimated 300-500 J
  reaches the projectile (~1,000 J ideal).

## Designs

- `designs/mk1/`: Mk1 Ducted-Tail Dart (current). See its README for numbers.
  Now barrel-sized like the sabot and wad (Russ): `mk1_dart.stl`, 39.6 mm,
  137 g, margin ~+0.76 cal.
- `designs/mk1/mk1r_dart.scad`: Mk1-R Rod Dart (Russ's design): the Mk1 shape with an
  8 mm steel rod (36.5 mm, four from a 150 mm rod; aim within ~1 mm) in a 8.15 mm center
  channel (Russ's fit-gauge pick) ending 18.5 mm below the tip (rev 3, Russ: was 10 mm,
  45 mm rod; now ~13.6 mm of solid over the channel point so hard hits don't crack the nose;
  rod bottom and plug unchanged; stability +0.80 vs +0.82). Rod length chosen for the
  best stability: 40-60 mm all give ~+0.82-0.85 cal (vs +0.76 without); longer rods
  reach behind the CG and stability drops. A one-way snap plug (printed flat) pushes up
  from the base: two thick arms cammed in by ramps catch a 10-tooth ratchet near the
  base, and a 4-beam spring on its tip preloads the rod (~1.5 mm) so it can't rattle.
  The rod bottom sits at 80 mm so the plug's tip is ~4 mm up inside the channel, centered
  at both ends (Russ worried the post would wander in the open cavity).
  Plug rev 2: round except one flat it prints on (side play ~0.7 mm per side, was ~1.5);
  hooks only on the sides so they fold in fully (arms squeeze 0.9 mm; slot allows 1.1).
  `mk1r_dart.stl` (39.6 mm, 134 g), plug `mk1r_plug.stl`; packet
  `Mk1-R Rod Dart Packet.zip`. ~150 g assembled, CG 61 mm from tip, +0.80 cal.
- `designs/hf1/`: HF1 High-Flier, for maximum height with parachute recovery (Russ:
  "no failure is an option"; robustness and reliability required for electronics and chute).
  Agreed: full-bore dart (not a sabot), fired behind the wad, ~175-185 mm, three widths;
  bullet nose with a 36.5 mm rod sealed in by a print pause; thin ring around 4 fins
  (fins alone can't stabilize a light dart inside the barrel width); fins 3.2 mm with
  root fillets; everything heavy on the axis (balance). Deployment: the nose pops off
  (axial, symmetric), pushed by a steel spring, pulling the chute out; nose, chute and
  body stay tied together by a Kevlar shock cord. Electronics approved (first in the
  project): two independent channels, each a board + barometric altimeter + battery,
  either of which can release the nose (redundant). Release by burning through a nylon
  holding line with nichrome (no moving parts), chosen over servos. LED for status/night,
  peak altitude logged. Range rules in `FIELD_CHECKLIST.md` are the real safety net.
  Parts (Russ chose cheap parts, "but make sure they're still good"): per channel an
  ESP32-C3 SuperMini, a BMP280 (GY-BMP280-3.3, 6-pin), a 1S 150 mAh 25C LiPo (drone type,
  own USB charger), a D4184 MOSFET module, 32 AWG nichrome, slide switch, 3 mm LED.
  Holding line 20 lb nylon mono; shock cord 80 lb braided line; DIY parachute (template).
  Launch detected from the barometer (fast climb); apogee by barometer with a backup
  timer. Quality plan: multi-packs for spares, a test program for every board/sensor,
  repeated bench burn tests per channel. Russ and his brother-in-law will solder.
  `hf1_concept.scad` is the early mockup; `hf1.scad` is a superseded side-hatch draft.
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
- `designs/chain-shot/`: two identical solid 39.6 mm balls joined by a metal chain
  or cable (store-bought).
  - As round as a supportless print allows: the only flat is a small spot on the bottom, with a 47 deg cone.
  - Anchor: a thick (7 mm) house-section snap pin goes in first, through the
    side hole. Then the cable threads up a channel from the bottom flat, up one
    side of the pin, over its peaked top and down the other side, and out; its
    loop is crimped outside the ball. The channel is the pin's house shape grown
    4 mm all round (Russ found the first 8.5 mm hole left no room around the pin).
    - Its head stops it going further in.
    - Its split end's two hooks spring out past a square ledge so it can't back out.
    - To remove it, squeeze the hooks with pliers or fingertips through the wide
      (16 mm) far-side opening and push. The head-side opening is equally wide
      so the ball stays balanced.
    - Prong strain on snapping is ~2%. A pull loads the ball in compression.
    - Cable: 1/8 in. 7x19 galvanized or stainless (~1,700-2,000 lb), stronger
      than the printed pin, so the cable isn't the weak link. A chain can't be
      threaded around an installed pin (use a quick link).
  - `chain_shot_slug.scad`: 39.6 x 39.6 mm cylinder (54 g). It has no overhangs, so it prints
    clean; Russ's round balls came out fuzzy on their underside. Same snap pin,
    with ends trimmed flat (`chain_shot_slug_pin.stl`).
  - `chain_shot_mine.scad`: sea-mine version with thick 8 mm horns. A ring of 5 points
    55 deg up, plus 1 on top; horns on the underside can't print without support.
    It stays inside the 39.6 mm width.
- `designs/flechette/`: steel flechette, a 150 mm rod with push-on printed parts
  (snug press fit, no glue). Sockets rev 2: no crush ribs (Russ: PCTG ribs don't
  crush, tails wouldn't go on; noses at +0.2 mm were a bit loose). A plain grip
  bore of rod + `grip_fit` (0.00 mm: Russ's fit gauge, the rod-size hole fit best) over 12-14 mm, rod + 0.25 mm elsewhere, a
  lead-in chamfer on tails. Tune `grip_fit` with `socket_fit_gauge.scad`
  (holes at rod +0.00 to +0.25 mm). Russ's Amazon 8 mm rods are 150 mm (6 in.). Both rod sizes: `8mm/` (59 g rod) and
  `12.7mm/` (149 g rod), plus `12mm/` for metric 12 mm rod, built by `build.sh`
  from `flechette_dims.scad`. `Flechette Print Packet.zip` holds every printable
  part per size, the wad and a print sheet; `Flechette 8mm Packet.zip`
  is Russ's short set (bullet nose, spinning basket, petal, wad). Rebuild both when parts change.
  - 1/2 in. version: bigger hub, 6 longer fins (4 would be about neutral);
    the basket tail is its recommended tail (~28 mm vs ~12 mm stability margin).
  - Noses: spike or ogive (ogive is the default: it's best at subsonic speeds and tougher).
    Ogive rev 2 (Russ): more bullet-shaped (ogive 18 mm / 26 mm, tip radius 2.4 / 3.4 mm)
    and the rod runs up into it to ~1/2 in. (12.7 mm) below the tip on 8 mm; 16.7 mm on
    1/2 in., where 1.5 mm minimum wall around the rod end limits it. Both have a tapered
    tail running ~20 mm back down the rod (Russ's idea): no step from nose to rod,
    longer grip; only the sleeve grips. Print with a brim. A nose wider than the
    hub was evaluated and rejected: more nose lift and drag cancel its weight gain.
    Trocar nose (`nose_trocar`, Russ's idea): a 3-sided point for plywood: three flat faces
    ground into a fat ogive (12 mm long on 8 mm, 16 mm on 1/2 in.), thick rounded ridges,
    blunt-ish tip (r 1.0 / 1.4). Stays within the hub width. The point is too slim to hold
    the rod with 1.5 mm wall, so the rod stops at its base (~13 mm below the tip on 8 mm)
    and the point is solid PCTG. Expect the tip to blunt on wood; glass chews it up. Tails: 4 fins, a windowed basket, or the basket with
    twisted inner vanes for gentle spin.
  - Basket windows are narrow diamonds (4.5 mm wide) so the bridges between them
    are 3.5-5 mm thick; Russ found the first version's ~0.2-1 mm bridges too skinny.
  - Three-petal sabot (75-79 g, solid 5 mm base): 39.6 mm (rev 6), full width over the whole tail
    section (rev 4, Russ) plus a front band ~95 mm up; hollow fin cavity, thick waist (r 13-13.5 mm), front ring scoop that opens it at the muzzle.
    Rev 2: Russ's first petals all snapped at the bottom of the slim waist near the end of
    the print (3.35 mm sliver, ~1.6 mm over the cavity roof, 112 mm tall). Now the waist,
    cavity wall (2.4 mm), scoop walls and collar are thicker and the outer taper starts
    5 mm above the cavity: thinnest section 84 mm² (was 23). Costs ~27 g of sabot.
    Rev 3: bands 39.7 mm; cavity wall 2.4 -> 3.4 mm and scoop wall 2.4 -> 3.0 mm after
    Russ snapped a rev 2 petal by hand-bending it at the cavity wall.
    Rev 4: 39.0 mm, and the tail-cavity section is full width (`cav_full`), so the
    cavity wall is 3.7 mm. Rev 5: 39.7 mm (Russ: fit best). Rev 6: 39.6 mm, the only size.
    Radial V-key ridges and grooves align the petals without stopping separation.
  - The tail sits on the sabot base: air pushes base -> tail -> rod.
  - 150 mm rod chosen over 100 or 200 mm (see the README).
- `designs/wad/`: wad cup fired behind the projectile, rev 2 (Russ): barrel-sized like
  the sabot: `wad.stl`, 39.6 mm (16 g),
  6 mm pusher disc (was 5), 28 mm skirt (was 22; 34 mm overall), thin flared lip that
  pressure seals against the barrel. The long skirt keeps it from cocking or folding.
  Prints disc-down, no supports, 100% infill.
- `designs/fit-test/`: barrel fit rings at 38.5 / 38.8 / 39.0 / 39.2 mm, for
  measuring the barrel's real inside diameter (Russ estimates ~39 mm).
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
  ≤ 39.6 mm, report volume and estimated PCTG mass, and render preview PNGs for
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
- `tools/check_stl.py part.stl`: watertight, max diameter vs `--max-width` (use 39.6), mass, CG.
- `tools/overhangs.py part.stl`: finds surfaces that would need supports.
- `tools/islands.py part.stl`: finds floating regions (layers starting in mid-air),
  the thing Bambu Studio warns about. Strict by default; Bambu flags even tiny ones.
- `tools/stability.py design.scad part.stl`: Barrowman CP estimate and stability
  margin (Mk1-style geometry; adapt for other layouts).
- `tools/strength.py a.stl b.stl`: weakest-layer bending section modulus, for
  comparing designs.
- `tools/section.py part.stl out.png --angle DEG`: true lengthwise cross-section.
- Use `-D '$fn=36' -D profile_steps=24` for fast low-res iterations (~13 s).
