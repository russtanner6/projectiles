# Mk1-W Screaming Dart (Rev B)

![section](previews/mk1w_whistle_dart_section_slots.png)

The Mk1 Ducted-Tail Dart with a death-whistle sound system inside, driven by air
rammed into the nose in flight. Same outside shape, fit, and print orientation as
Mk1.

## History

- **Rev A** printed fine but was silent: its holes (2.8 mm) came from a
  mis-measurement of the skull whistle.
- **Whistle tests** (`../whistle-tests/`): A (skull copy) and D (dart-size with
  a 22 mm inlet channel) screamed like the skull. B and C (no channel) made sound
  but were too high-pitched.
- **Rev B** (this version) copies test piece D's internals.

## How it makes noise

| | Test piece D (works) | Rev B |
|---|---|---|
| Inlet | 8 mm × 22 mm channel (you blow into it) | 8 mm × 22 mm channel from the nose tip (ram air) |
| Blow hole | 6 mm × 3 mm | 6 mm × 3 mm |
| Blow hole to ball hole | 5.4 mm | 5.4 mm |
| Ball | 24.2 mm cone-ended capsule, 1.2 mm shell, 7 mm hole | Same |
| Gap around ball | 3.5 mm | 3.5 mm |
| Ball held by | Pedestal on the bed | Four 2.4 mm gussets under the ball |
| Exits | Open bottom | 8 slots between the fins (~220 mm²) + open tail tube (~80 mm²) |

Ram-air pressure at the nose is about 1.0 kPa at 40 m/s, 2.2 kPa at 60 m/s, and
3.9 kPa at 80 m/s, similar to hard blowing. Expect it loudest right after launch.

## Internal strength

On a nose-first impact the ball keeps moving forward and loads its gussets. The
ball shell weighs ~4 g. Stopping from 50 m/s in ~50 mm of dirt puts ~105 N on
the gussets; stopping in ~5 mm on hard ground puts ~1,050 N. That is about
6 MPa of shear in the gusset joints in the hard case, several times below PCTG's
strength. The load runs ball → gusset → wall along joints within each layer, so
it does not pull layers apart. The nose rim around the 8 mm inlet is 2 mm thick at
the very tip and thickens quickly behind it.

## Numbers vs Mk1

| | Mk1-W Rev B | Mk1 |
|---|---|---|
| Mass (100% PCTG) | ~84 g | ~107 g |
| CG from tip | 58.8 mm | 56.6 mm |
| CG off-axis | 0.000 mm | 0.000 mm |
| Stability margin (est., fins only / with duct) | +0.50 / +0.64 cal | +0.56 / +0.70 cal |
| Weakest layer, section modulus | 1555 mm³ (Z = 26 mm) | 1570 mm³ (Z = 26 mm) |
| Supports needed | None (steepest overhang 40.9°) | None (40.0°) |

## Printing and use

- Same settings as Mk1: 100% infill, 6+ walls, supports off, brim, nose-up.
- Test it before firing: blow into the nose. It should sound like test piece D.
- After landing, clear dirt out of the nose inlet and shake out the tail.

Regenerate: `tools/render.sh designs/mk1w/mk1w_whistle_dart.scad`.
