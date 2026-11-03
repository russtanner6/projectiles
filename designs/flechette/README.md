# Steel flechette and sabot

![overview](previews/flechette_overview.png)

A store-bought **8 mm x 150 mm hardened steel rod** (3D-printer linear rod,
59 g) with a printed nose and tail pushed on (no glue), fired inside a
three-petal printed sabot that falls away at the muzzle.

| Part | File | Mass | Notes |
|---|---|---|---|
| Spike nose | `nose_spike.stl` | 2.2 g | sleekest; chips on hard hits |
| Ogive nose (default) | `nose_ogive.stl` | 2.6 g | rounded bullet tip, tougher; best at subsonic potato-cannon speeds |
| Fin tail | `tail_fins.stl` | 3.9 g | 4 swept fins, 2 deg cant, 30 mm span |
| Basket tail | `tail_basket.stl` | 5.3 g | flared windowed cone, no fins to snap |
| Spinning basket tail | `tail_basket_spin.stl` | 5.3 g | same, inner vanes twisted 16 deg like fan blades for gentle spin |
| Sabot petal (print 3) | `sabot_petal.stl` | 12.2 g each | 36.6 g per sabot; solid 4 mm base |

Finished flechette: about 65-67 g and 178-184 mm long. Estimated stability
margin +2.3 to +3.9 cal (Barrowman, rough): very stable.

**Fit:** very tight, no glue.
- Sockets are 8.2 mm with 4 crush ribs that the rod shaves as it goes in
  (0.25 mm interference per rib).
- Press on with a vise, or tap with a mallet against a wood block.
- If a batch is too tight to start, run an 8 mm drill bit into the mouth by hand.

**Sabot:**
- Two 38 mm touch points about 95 mm apart: the rear band, and the front band
  with its scoop.
- A hollow rear cavity holds the tail fins. The tail sits on the sabot's base, so
  air pushes base -> tail -> rod.
- At the muzzle, air fills the front ring scoop and pushes the three petals
  outward evenly.
- V-shaped alignment keys between the petals (a ridge on one face, a groove on the
  next) stop them sliding or twisting against each other but let them pull
  straight apart. Hold the petals together for loading with one turn of tape or a
  thin rubber band at the waist. Fire with a wad behind it to seal the petal seams.

**Print:** supports off, 100% infill or 6+ walls.
- noses: tip up
- tails: base down
- petals: standing on their rear face

Every downward face is at least 50 deg; checked with tools/overhangs.py and tools/islands.py.

**Safety:** this is a real steel penetrator. Shoot it into a dirt berm or
hillside with nothing and nobody beyond the target.
