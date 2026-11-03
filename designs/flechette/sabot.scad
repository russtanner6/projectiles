// Sabot for the 150 mm steel flechette (rod + printed nose + tail), 8 mm or
// 1/2 in. rod: set rod_d (see flechette_dims.scad), e.g. -D rod_d=12.7.
//
// Three identical petals close around the flechette and fill the 38 mm
// barrel. Air pushes the base; the base pushes the tail; the tail's floor
// pushes the rod. At the muzzle the petals fall away and the flechette
// flies on alone.
//
// Shape (after the military sabots Russ found):
//   - rear band: full 38 mm, rides and seals in the barrel (touch point 1)
//   - hollow rear cavity that holds the tail fins (30 mm span)
//   - slim waist (saves weight: every gram of sabot is wasted energy)
//   - front band: full 38 mm (touch point 2, ~95 mm from the rear band)
//   - front scoop: an open ring-shaped cup. Leaving the muzzle, oncoming air
//     fills it and pushes the three petals outward and back, evenly, so the
//     flechette isn't knocked off line.
// Alignment keys: each petal has a V ridge on one side face that drops into
// a V groove on its neighbor (one near the rear band, one at the front
// flare). The ridges run outward from the centre, so they stop the petals
// sliding lengthwise or twisting against each other but let them pull
// straight apart at the muzzle. Their faces slope 50 deg, so they print fine.
// The barrel holds the petals together while firing. To load, pinch them
// around the rod at the waist; once the first band is in, the barrel holds them. Fire it with a wad behind it to seal
// the petal seams.
//
// Print 3 petals (part = "petal"), each standing on its rear face, supports
// off, 100% infill or 6+ walls. Every downward face is >= 50 deg.

$fn = 160;

part        = "petal";      // "petal", "all" (3 petals, closed), "assembly", "open"
// The two bearing bands are sized to Russ's barrel (about 39 mm inside), not
// the 38.0 mm projectile limit, so the barrel squeezes the petals closed and
// centered. Only the bands touch the barrel; Russ approved this exception.
band_d      = 38.8;         // snug in a ~39.0 mm bore; confirm with the 38.8 fit ring
max_width   = 39.0;
D           = band_d;
n_petals    = 3;

include <flechette_dims.scad>     // rod size (rod_d) and tail/nose sizes, shared with the parts

// sabot
base_t      = 4.0;          // base the tail sits on (thick: it takes the air blast and the tail's push)
rear_band   = 10.0;         // length of the rear bearing band
fin_clr     = 0.8;          // clearance around the fins
bore_clr    = 0.15;         // rod bore clearance (rod slides out freely)
cav_wall    = 1.6;
waist_r     = rod_d / 2 + bore_clr + 3.35;   // 3.35 mm of wall around the rod at the waist (7.5 / 9.85)
front_top   = 112.0;        // front end of the sabot (rod's front 40+ mm and nose stick out)
front_band  = 10.0;
scoop_depth = 9.0;
scoop_in_r  = rod_d / 2 + bore_clr + 2.85;   // collar around the rod (7.0 / 9.35)
scoop_wall  = 1.6;
key_d       = 0.9;          // how far a ridge sticks out of the face
key_h       = key_d * tan(50);   // half-height (faces at 50 deg)
key_clr     = 0.2;
assert(D <= max_width);
R  = D / 2;
fc_r   = fin_span / 2 + fin_clr;                 // fin cavity radius
cav_top = base_t + tail_len + 1.0;               // top of the straight fin cavity
bore_r = rod_d / 2 + bore_clr;
cone_top = cav_top + (fc_r - bore_r) * T50;      // cavity roof cone (50 deg) down to the rod bore
mid_r  = fc_r + cav_wall;                        // outer radius around the fin cavity
waist0 = cav_top + (mid_r - waist_r) * T50;      // outer cone reaches the waist here
band0  = front_top - front_band;
flare0 = band0 - (R - waist_r) * T50;            // front flare (widens upward at 50 deg)

assert(flare0 > waist0 + 5, "waist too short");
assert(front_top < base_t + tail_floor + rod_len - nose_sock - 3, "sabot would reach the nose sleeve");
key_z2      = 96.0;
keys        = [[6.0, 16.3, 18.5], [key_z2, rod_d / 2 + bore_clr + 1.05, waist_r + (key_z2 - flare0) / T50 - 1.4]];   // [height, inner r, outer r]


module body() {
    difference() {
        rotate_extrude() polygon([
            [0, 0], [R, 0], [R, rear_band], [mid_r, rear_band + (R - mid_r)], [mid_r, cav_top],
            [waist_r, waist0], [waist_r, flare0], [R, band0], [R, front_top], [0, front_top]]);
        // fin cavity with a 50 deg roof down to the rod bore
        translate([0, 0, base_t]) cylinder(h = cav_top - base_t, r = fc_r);
        translate([0, 0, cav_top - 0.01]) cylinder(h = cone_top - cav_top + 0.02, r1 = fc_r + 0.05, r2 = bore_r);
        // rod bore (starts above the base, so the base stays solid)
        translate([0, 0, base_t]) cylinder(h = front_top + 1, r = bore_r);
        // front scoop: ring cup open to the front, floor sloping outward/down
        translate([0, 0, front_top - scoop_depth])
            rotate_extrude() polygon([[scoop_in_r, scoop_depth * 0.35], [R - scoop_wall, 0],
                                      [R - scoop_wall, scoop_depth + 1], [scoop_in_r, scoop_depth + 1]]);
    }
}

module key(grow = 0) {
    // V ridge on the face y = 0, sticking out toward -y, running radially along +x
    for (k = keys) translate([k[1] - grow, 0, k[0]]) rotate([90, 0, 90])
        linear_extrude(height = k[2] - k[1] + 2 * grow)
            polygon([[grow, -key_h - grow * 1.6], [-key_d - grow, 0], [grow, key_h + grow * 1.6]]);
}

module petal(i = 0) {
    a0 = 360 / n_petals * i;
    difference() {
        union() {
            intersection() {
                body();
                rotate([0, 0, a0]) linear_extrude(height = front_top + 1)
                    polygon([[0, 0], [2 * R, 0], [2 * R * cos(360 / n_petals), 2 * R * sin(360 / n_petals)]]);
            }
            rotate([0, 0, a0]) key(0);                               // ridges on the start face
        }
        rotate([0, 0, a0 + 360 / n_petals]) key(key_clr);            // grooves on the end face
    }
}

module flechette() {
    color("silver") translate([0, 0, base_t + tail_floor]) cylinder(h = rod_len, d = rod_d);
}

if (part == "petal") petal(0);
else if (part == "all") for (i = [0 : n_petals - 1]) petal(i);
else if (part == "open") for (i = [0 : n_petals - 1])
    rotate([0, 0, 360 / n_petals * (i + 0.5)]) translate([14, 0, 0]) rotate([0, 0, -360 / n_petals * (i + 0.5)]) petal(i);
else { for (i = [0 : n_petals - 1]) petal(i); flechette(); }
