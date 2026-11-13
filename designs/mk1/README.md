# Mk1 Ducted-Tail Dart

![side](previews/mk1_dart_side.png)

Claude's first from-scratch design. Now barrel-sized at 39.6 mm to match the sabot and wad: `mk1_dart.stl` (137 g). The table below is from the original 38.0 mm version. The goal is the strongest dart that still flies
nose-first, within the 38 mm limit, printed in PCTG with no metal.

| | Mk1 | Gemini Rev 15 (reference) |
|---|---|---|
| Length | 135 mm | 115 mm |
| Max diameter | 38.00 mm | 38.00 mm |
| Mass (solid PCTG) | ~128 g | ~93 g |
| CG from tip | 62.8 mm (47%) | 56.8 mm (49%) |
| Weakest layer, section modulus | **1981 mm³** | 733 mm³ |
| Stability margin (est., fins only) | +0.62 cal | +0.77 cal |
| Stability margin (est., incl. duct/ring) | +0.76 cal | ~+0.8 cal |

## How it works

- **Strength.** No skinny neck. The tail is a hollow 16 mm tube joined by 8 fins
  (4.2 mm thick) to a full-diameter duct ring (3 mm wall), so every layer has a wide, well-spread cross-section.
  The weakest layer (Z ≈ 126 mm, just behind the nose tip) resists bending about
  2.7x better than Rev 15's weakest layer.
- **Stability without metal.** The aft body is hollow (open at the base through
  the tail tube), so the solid nose and bearing band carry most of the mass and
  the CG sits forward. The cavity stops behind the CG; hollowing further forward
  moves the CG backward.
- **Fit in the barrel.** Two full-diameter (38.0 mm) bearing surfaces about 95 mm
  apart: the 50 mm band behind the nose and the 16 mm duct ring at the base. The fin
  tips also reach full diameter between them.
- **Spin.** Fins are helical, about 6° at the tips. Ideal roll rate is about
  53 RPM per m/s of velocity (≈3,200 RPM at 60 m/s); expect less in practice.
- **Printing.** Nose-up, no supports. Verified on the STL: the steepest
  downward-facing surface is 40° from vertical (the cavity roof), inside the 45°
  limit; the flare and fins are gentler.

## Print settings (Bambu Studio)

- One uniform infill setting for the whole part: 100%, or high-density gyroid. No
  height-range modifiers that change density.
- 6+ walls.
- Hot nozzle (upper end of the PCTG range), low part-cooling fan, dry filament.
- A brim is a good idea. The part is tall and its footprint is a ring of fins.
- Check elephant's-foot compensation. The duct ring sits on the bed at full
  width, and first-layer squish adds width.

## Caveats

- Stability numbers use the Barrowman method plus a rough duct term. They are
  good for comparing designs, not exact. The duct and spin should add stability
  beyond the fins-only figure, but test flights decide.
- Mass assumes 100% infill at 1.25 g/cm³. Weigh a print and update it.
- The core-rod idea was evaluated and left out. A printed rod that fits inside
  the tail tube would add only a few percent to the weakest layer's bending strength,
  not worth the pause-and-drop step.

## Files

- `mk1_dart.scad`: the parametric source; all key dimensions are at the top.
- `mk1_dart.stl`: ready to import into Bambu Studio.
- `previews/`: renders and true lengthwise cross-sections.

Regenerate: `tools/render.sh designs/mk1/mk1_dart.scad`, then
`tools/stability.py designs/mk1/mk1_dart.scad designs/mk1/mk1_dart.stl` and
`tools/strength.py designs/mk1/mk1_dart.stl`.

## Mk1-R Rod Dart (`mk1r_dart.scad`)

![cutaway](previews/mk1r_cutaway.png)

Same outside as Mk1, plus an 8 mm steel rod locked in the front with a one-way snap plug.

- **Rod:** 8 mm steel, 36.5 mm long (four from one 150 mm rod), in an
  8.15 mm channel up the center that ends 18.5 mm below the nose tip (13.6 mm of solid
  plastic over the channel's pointed top, so hard hits don't crack the nose).
- **Rod length:** stability is about +0.80 cal (vs +0.76 with no rod); the rod's bottom end sits so the plug's tip is ~4 mm up inside the channel and both ends of the plug are centered (about +0.82 to +0.85 cal vs
  +0.76 without a rod). Longer rods put steel behind the balance point and stability drops.
- **Plug:** printed lying flat. Two thick arms are squeezed inward by ramps inside the
  channel as you push it in, then catch on a 10-tooth ratchet near the base: it can
  never back out. A 4-beam spring on its tip presses the rod against the channel top,
  so nothing rattles; ratchet + spring take up rod-length error.
- **Size:** `mk1r_dart.stl`, 39.6 mm (134 g printed), plug `mk1r_plug.stl` (3.7 g).
  Assembled: ~150 g, CG 61 mm from the tip.
