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
grip_fit    = 0.10;                 // grip bore = rod + this (nose felt ~0.1 mm loose at +0.2)
grip_d      = rod_d + grip_fit;
clear_d     = rod_d + 0.25;         // non-gripping parts of the bore: slides freely
grip_len    = 12.0;                 // tail: gripping length at the mouth
lead_in     = 0.6;                  // 45 deg chamfer at the tail mouth
wall        = big ? 2.0 : 1.7;      // socket wall (thicker for the 3x heavier rod)
hub_d       = sock_d + 2 * wall;    // 11.6 / 16.9 mm

// noses
nose_sock   = big ? 18.0 : 14.0;    // socket depth
spike_len   = big ? 40.0 : 30.0;    // shaped tip length above the sleeve
ogive_len   = big ? 32.0 : 24.0;
ogive_tip_r = big ? 2.3 : 1.6;      // ~28% of the hub radius: rounded, chip-resistant
nose_taper  = big ? 22.0 : 20.0;    // tapered tail behind the sleeve, down toward the rod (1/2 in.: sabot clearance limits it)
taper_end_r = sock_d / 2 + 1.0;     // 1 mm wall at the taper's end (no feather edge)

// tails
tail_sock   = big ? 30.0 : 26.0;
tail_floor  = 3.0;
fin_n       = big ? 6 : 4;          // 1/2 in. rod needs 6 fins to stay stable (span is capped by the sabot)
fin_span    = 30.0;                 // tip to tip, fits the sabot cavity
fin_t       = 1.8;
fin_root    = big ? 36.0 : 30.0;
fin_tip     = big ? 16.0 : 13.0;
fin_cant    = 2.0;
basket_d    = 30.0;
basket_len  = 30.0;
basket_wall = 1.6;
windows     = 8;
window_h    = 11.8;                 // diamond height (pointed top prints without supports)
window_w    = 4.5;                  // diamond width: leaves ~3 mm bridges between windows (was 7.35, ~0.1 mm)
basket_twist = 16;

// overall tail length (sabot cavity must hold it)
tail_len    = max(tail_floor + tail_sock, fin_root, basket_len);

T50 = tan(50);
