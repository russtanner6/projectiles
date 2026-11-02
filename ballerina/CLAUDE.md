# Ballerina fountain: project notes for Claude

A ~305 mm (12") 3D-printed ballerina standing on a rock island in a stone-block
pool. Water is pumped up one leg and leaves a slot under her waistband as a
thin sheet of water (the "tutu"), falling back into the pool. Built by Russ as
Christmas gifts. Printed on a Bambu H2D (build height 325 mm), sliced in Bambu
Studio. Russ will paint the finished piece.

These are the current agreed decisions. When Russ changes one, update this file
in the same commit.

## The figure

- **Current model:** `models/current/ballerina_current.stl` (120 x 120 x 316.6 mm
  on her old 24 mm display base, one watertight part). It is Russ's
  `Ballarina_2.stl` Blender edit with:
  - smoothed (rounded) forearms, from `scripts/forearm_fix.py`
  - the wrist seams between hands and forearms blended
  - one pinched non-manifold vertex at the neck base (x -3.8, z 239.6) patched
  - Russ's own hands kept as they are
- Russ prefers the figure in one piece. Two pieces is OK if needed for quality.
- Style: the body is chiselled / low-poly from feet to neck; the face is realistic.
- **Rejected:**
  - sculpted SDF hands ("alien hands")
  - faceted blade hands ("looks terrible")
  - script-stretching necks or limbs (makes bumps)
- **Lessons:**
  - Prefer rigid placement of whole parts with a buried, blended join.
  - Remesh a region finely before deforming it.
  - Russ catches flaws that lit renders hide, so check close-ups from several angles in flat shading.
- Source files in `models/source/`:
  - Russ's Blender edits (Ballarina.stl, Ballarina_2.stl)
  - the original Meshy figure
  - three Meshy heads and the Meshy hands

## Fountain design (agreed)

- **No rotation.** The turntable idea was dropped for simplicity.
- **Water path:** pump (in a well under the island) -> a few inches of
  1/2" ID vinyl tubing inside the hollow island -> barb at her foot ->
  **5 mm channel printed up one leg (no tubing in the leg)** -> ring channel
  inside her hips, fed by 8 holes -> slot under her waistband -> sheet falls
  into the pool -> hidden crevices at the island's foot -> well -> pump.
- **The slot follows her waistband's lower edge exactly** (V dips ~10 mm at
  the front, ~3 mm at the back). Belt line: `fountain/belt_edge.npy`.
- **Two-piece hips, snap-together.**
  - A single-piece ring slot can't print: its upper lip starts in mid-air.
  - So the hips split at the slot. The lower half prints upright; the upper half prints upside down.
  - A central 3-prong snap post clicks into a blind socket. No screws (M3 screws bound in the pilot holes).
  - Halves come apart for cleaning.
- **No supports anywhere in the water path.** Every internal ceiling is pointed or sloped
  at 50 deg or steeper. Check with `tools/overhangs.py` and `tools/islands.py`
  (in the projectiles repo) and `fountain/leak_check.py`.
- **Pool:** stone-block basin ~300 mm inside (~330 mm outside), water ~25 mm
  deep, walls 15-20 mm above water. Likely printed in 2-4 segments. Sealed inside
  with epoxy before painting (printed plastic seeps).
- **Island:** hollow rock pedestal ~120-130 mm across, top lifts off with her
  on it for pump access. Pump sits at the bottom of a deep well so it never
  runs dry. Screen over the intake; distilled water; optional float switch.
- **Sheet landing** (from her slot ~170 mm above the water, 50 deg down):
  ~100 mm (1 m/s) to ~130 mm (2 m/s) from her centre. Re-check with test data.

## Pump

- **Testing now:** TotalPond **M** fountain pump (Home Depot, 110 V, 338 GPH max,
  5 ft ideal height, adjustable flow lever) plugged into a GFCI outlet.
  1/2" ID x 5/8" OD vinyl tubing pushes onto its adapter and onto the test
  piece's barb.
- **Final pump: undecided.** Either:
  - the TotalPond M if it works well, or
  - a 12 V brushless submersible (~800 L/h, 5 m head) with a 12 V 2 A adapter and an inline speed controller.

  Small cat-fountain or 1.5-3 ft pumps are too weak.
- **Needs:** roughly 250-370 L/h at the slot, against an effective head of ~3 m
  because of the narrow 5 mm leg channel. These are estimates; the test decides.
- **Reliability plan:**
  - keep the pump submerged
  - screen the intake
  - burn it in for a few days in a bucket before installing
  - run it below max
  - make swapping it a 2-minute job
  - keep a spare

## Test pieces (fountain/test_pieces)

- `waist_0.8_lower.stl` + `waist_0.8_upper.stl`: **current.**
  - her real outline under the belt
  - slot follows the waistband V, 0.8 mm wide
  - snap-together
  - barb for 1/2" ID tubing

  Print with supports off, 0.12 mm layers, 4 walls, PETG/PCTG. Leave the upper half upside down as it loads.
- `snap_0.8_*`: flat (non-V) snap version.
- `two_0.8_*`: older screw version (screw holes too tight; superseded).
- **Test procedure:**
  1. Check the slot gap against a light.
  2. Pump in a bucket with the flow lever low.
  3. Open it up slowly and note where the sheet first turns smooth and where it starts to spray.
  4. Watch whether the sheet clings to the body.
- **Adjustment:** slot width can be changed (paper shim at the seat widens it ~0.64x the shim
  thickness; sanding narrows it). Russ requirement: **no spray, no trickle**:
  a smooth, unbroken sheet.

## Not yet decided / open

- Slot test results (flow sweet spot, landing distance, clinging).
- Final pump; then design the well around its measured size.
- Island shape (round rock vs square stone blocks) and exact pool size.
- Fibre-optic glow for the outfit: feasible (second leg channel + hollow torso
  + stationary LED ring under the base), parked for now. Keep space for it if
  convenient.

## Tooling

Setup: `apt-get install -y openscad xvfb && pip install trimesh scipy shapely rtree networkx matplotlib manifold3d pymeshlab scikit-image`

- `fountain/slot_test4.py outline.npy out.stl SLOT_W [belt_edge.npy]`:
  - builds the two-piece snap test
  - with a belt file, the slot follows the waistband
  - writes `_lower`, `_upper` (flipped for printing) and `_assembled` STLs
- `fountain/leak_check.py assembled.stl outline.npy z_lip barb_x [belt_edge.npy]`:
  - plugs the barb and slot, floods the inside, reports leaks and slot coverage
- `fountain/system_diagram.py`: to-scale diagram of the whole fountain.
- `scripts/`: figure-editing scripts:
  - `forearm_fix.py` (forearm smoothing)
  - `bust_swap.py` (head attach)
  - `neck_polish.py`
  - `hand_sdf.py` / `hand_facet.py` (rejected hand attempts)
  - `views.sh` / `views2.sh` (flat-orange Bambu-style renders)
