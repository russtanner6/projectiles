// Shared flechette dimensions, used by flechette_parts.scad and sabot.scad.
// Every rod-carrying design comes in two rod sizes (Russ's rule):
//   rod_d = 8     8 mm hardened linear rod, or 5/16 in. (7.94 mm) Home Depot
//                 plain steel rod: both fit the same parts
//   rod_d = 12.7  1/2 in. rod (Home Depot plain steel, or a 1/2 in. linear shaft).
//                 A metric 12 mm rod would be loose in these: rebuild with rod_d = 12.
// Build either size with:  openscad -D rod_d=12.7 ...
// The 8 mm numbers are unchanged from the first design.

rod_d       = 8.0;
big         = rod_d > 10;
rod_len     = 150.0;

// push-on sockets (rev 2, no crush ribs: Russ found PCTG ribs don't crush, so
// the tails wouldn't go on, while the noses were a bit loose):
//   a plain round grip section, 12-14 mm long, sized for a snug press fit,
//   a slightly looser bore elsewhere, and a lead-in chamfer at the tail mouth.
// grip_d is the number to tune: use the socket fit gauge (socket_fit_gauge.scad)
// to find the hole that feels right on your rods, then set grip_fit to it.
sock_d      = rod_d + 0.2;          // reference size for the hub wall
grip_fit    = 0.00;                 // grip bore = rod + this. Russ's fit gauge: the +0.00 hole fit best (8 mm rod)
grip_d      = rod_d + grip_fit;
clear_d     = rod_d + 0.25;         // non-gripping parts of the bore: slides freely
grip_len    = 12.0;                 // tail: gripping length at the mouth
lead_in     = 0.6;                  // 45 deg chamfer at the tail mouth
wall        = big ? 2.0 : 1.7;      // socket wall (thicker for the 3x heavier rod)
hub_d       = sock_d + 2 * wall;    // 11.6 / 16.9 mm

// noses
nose_sock   = big ? 18.0 : 14.0;    // socket depth
spike_len   = big ? 40.0 : 30.0;    // shaped tip length above the sleeve
ogive_len   = big ? 26.0 : 18.0;    // rev 2: shorter, more bullet-shaped (about 1.5 hub diameters; was 32 / 24)
ogive_tip_r = big ? 3.4 : 2.4;      // rev 2: rounder tip, ~40% of the hub radius (was 2.3 / 1.6)
nose_gap    = 12.7;                 // rod end sits this far below the nose tip (Russ: about 1/2 in.),
                                    // unless that would leave less than 1.5 mm of wall (the 1/2 in. rod)
nose_taper  = big ? 18.0 : 20.0;    // tapered tail behind the sleeve, down toward the rod (1/2 in.: sabot clearance limits it)
taper_end_r = sock_d / 2 + 1.0;     // 1 mm wall at the taper's end (no feather edge)
trocar_len  = big ? 16.0 : 12.0;    // 3-sided (trocar) point length above the sleeve (Russ)
trocar_tip_r = big ? 1.4 : 1.0;     // blunt-ish tip: rounded, with 3 small flats across it
trocar_tip_flat = big ? 1.0 : 0.7;  // each face passes this far from the axis at the tip

// tails
tail_sock   = big ? 30.0 : 26.0;
tail_floor  = 3.0;
fin_n       = big ? 6 : 4;          // 1/2 in. rod needs 6 fins to stay stable (span is capped by the sabot)
tail_xl     = false;                // XL tails (Russ): 2 mm wider fins and basket, need the XL petal (-D tail_xl=true)
fin_span    = tail_xl ? 32.0 : 30.0;   // tip to tip, fits the sabot cavity
fin_t       = 1.8;
fin_root    = big ? 36.0 : 30.0;
fin_tip     = big ? 16.0 : 13.0;
fin_cant    = 2.0;
basket_d    = fin_span;
basket_len  = 30.0;
basket_wall = 1.6;
windows     = 8;
window_h    = 11.8;                 // diamond height (pointed top prints without supports)
window_w    = 4.5;                  // diamond width: leaves ~3 mm bridges between windows (was 7.35, ~0.1 mm)
basket_twist = 16;

// overall tail length (sabot cavity must hold it)
tail_len    = max(tail_floor + tail_sock, fin_root, basket_len);

T50 = tan(50);
