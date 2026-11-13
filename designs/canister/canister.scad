// Canister shot: three printed petals around a load of steel balls (Russ).
// Air pushes the base; the base pushes the balls. In the barrel, the barrel holds
// the petals closed. At the muzzle a ring scoop around the front catches the air
// and throws the three petals outward; the shell slows down and the balls fly on
// as a spreading pattern.
//
// Shape (all three petals together):
//   - full 39.6 mm cylinder, 3 mm wall, solid 5 mm base
//   - payload cavity 33.6 mm across, 40 mm straight, then a 50 deg cone roof
//     with a 7 mm hole at the top (smaller than the balls, so they stay in)
//   - front scoop: the outer wall runs up past the roof, leaving a ring trough
//     open to the front; air filling it pushes the walls outward
//   - tape groove round the base: one wrap of masking tape (or a stout rubber
//     band) holds the 3 petals together at the base like a hinge. To load, fan
//     the tops open, pour in the balls, close it, slide it into the barrel.
//   - V key ridges on the petal faces (base and mid-wall) line the petals up
//     and stop them sliding, but let them swing apart
// Payload: 3/8 in. (9.5 mm) steel balls, about 40-45 to fill it (~150 g).
// Anything that fits works: smaller balls, hex nuts, gravel.
// Fire with the wad behind it.
//
// Print 3 petals (part = "petal"), standing on the base, supports off,
// 100% infill. Every downward face is 50 deg or steeper.

$fn = 160;
part      = "petal";      // "petal", "all" (closed), "open" (exploded preview), "loaded" (with balls)
D         = 39.6;         // Russ: 39.6 for everything (barrel ~40.1 mm)
wall      = 3.0;
base_t    = 5.0;
cav_h     = 40.0;         // straight part of the payload cavity
roof_t    = 3.0;          // roof thickness (normal to its surface)
hole_r    = 3.5;          // top hole (7 mm), smaller than a 9.5 mm ball
lip_up    = 10.0;         // scoop: wall top this far above where the roof meets the wall
groove_d  = 0.4;          // tape groove depth
groove_z0 = 1.5; groove_z1 = 9.5;
n_petals  = 3;
ball_d    = 9.525;        // 3/8 in. steel ball (preview / count only)
key_d = 0.9; key_h = key_d * tan(50); key_clr = 0.2;

T50 = tan(50);
R   = D / 2; ri = R - wall;
z_c   = base_t + cav_h;                         // roof starts (inner)
z_in  = function(r) z_c + (ri - r) * T50;       // roof inner surface
z_out = function(r) z_in(r) + roof_t / cos(50); // roof outer surface
z_top = z_out(ri) + lip_up;                     // wall top
lip_r = wall / 2;
keys  = [[2.5, 4.0, ri - 0.8], [z_c - 12, ri + 0.4, R - 0.6]];   // [height, inner r, outer r]
echo(str("canister: length ", max(z_top, z_out(hole_r)), " mm, roof peak ", z_out(hole_r), ", wall top ", z_top));

module body() {
    gd = groove_d * T50;   // groove ends slope at 50 deg
    rotate_extrude() polygon(concat(
        [[0, 0], [R, 0], [R, groove_z0], [R - groove_d, groove_z0 + gd], [R - groove_d, groove_z1 - gd], [R, groove_z1]],
        [for (a = [0 : 10 : 180]) [R - lip_r + lip_r * cos(a), z_top - lip_r + lip_r * sin(a)]],
        [[ri, z_out(ri)], [hole_r, z_out(hole_r)], [hole_r, z_in(hole_r)], [ri, z_c], [ri, base_t], [0, base_t]]));
}

module key(grow = 0) {
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
                rotate([0, 0, a0]) linear_extrude(height = 200)
                    polygon([[0, 0], [2 * R, 0], [2 * R * cos(360 / n_petals), 2 * R * sin(360 / n_petals)]]);
            }
            rotate([0, 0, a0]) key(0);
        }
        rotate([0, 0, a0 + 360 / n_petals]) key(key_clr);
    }
}

// rough ball load for the preview: hexagonal layers
module balls() {
    color("silver") for (L = [0 : 5]) let(z = base_t + ball_d / 2 + L * ball_d * 0.82, off = (L % 2) * 30)
        if (z + ball_d / 2 < z_c + 6) for (a = [0 : 45 : 315]) rotate([0, 0, a + off * 0.75])
            translate([ri - ball_d / 2 - 0.3, 0, z]) sphere(d = ball_d, $fn = 24);
}

if (part == "petal") petal(0);
else if (part == "p1") petal(1);
else if (part == "p2") petal(2);
else if (part == "all") for (i = [0 : n_petals - 1]) petal(i);
else if (part == "open") for (i = [0 : n_petals - 1])
    rotate([0, 0, 360 / n_petals * (i + 0.5)]) translate([12, 0, 0]) rotate([0, 0, -360 / n_petals * (i + 0.5)]) petal(i);
else { for (i = [1 : n_petals - 1]) petal(i); balls(); }
