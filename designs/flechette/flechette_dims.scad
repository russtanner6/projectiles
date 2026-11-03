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

// push-on sockets: bore 0.2 mm over the rod, 4 crush ribs 0.25 mm into the rod
sock_d      = rod_d + 0.2;
rib_r       = rod_d / 2 - 0.25;
rib_w       = 1.0;
wall        = big ? 2.0 : 1.7;      // socket wall (thicker for the 3x heavier rod)
hub_d       = sock_d + 2 * wall;    // 11.6 / 16.9 mm

// noses
nose_sock   = big ? 18.0 : 14.0;    // socket depth
spike_len   = big ? 40.0 : 30.0;    // shaped tip length above the sleeve
ogive_len   = big ? 32.0 : 24.0;
ogive_tip_r = big ? 2.3 : 1.6;      // ~28% of the hub radius: rounded, chip-resistant

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
