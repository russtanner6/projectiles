// HF1 High-Flier: CONCEPT MOCKUP (not for printing yet).
// Full-bore dart for maximum height, fired behind the wad. Low drag where it
// counts: bullet-shaped (tangent ogive) nose, smooth body, gentle taper to a slim
// boom, 4 thin swept fins inside a THIN ring (the ring is needed: fins alone can't
// be big enough inside the 39 mm barrel to keep a light dart stable). Heavy nose (36.5 mm steel rod captured with a print pause),
// thin-walled body with a side parachute hatch and an electronics bay.

$fn = 120;
part     = "all";       // "all", "cutaway"
body_d   = 39.0;
L        = 160;
nose_len = 48;          // tangent ogive, ~1.2 diameters
tip_r    = 3.0;
boom_d   = 16;          // slim tail boom: gives the fins real span inside the barrel width
boom_len = 42;          // boom length (fins live here)
taper    = 30;          // smooth taper from the body down to the boom (acts as a boat tail)
wall     = 1.6;
fin_n    = 4;
fin_t    = 2.2;
fin_root = 50;          // fin root chord (along the boom)
fin_tip  = 24;          // fin tip chord; the tip edge is full diameter (rear barrel contact)
rod_d    = 8.15;        // pocket for the 8 mm rod
rod_len  = 36.5;
rod_gap  = 18.5;        // rod top below the tip
ring_len = 16;          // thin ring around the fin tips (needed for stability inside the barrel width)
ring_wall= 1.6;
hatch_z  = [66, 108];   // parachute hatch, one side
hatch_w  = 22;

R = body_d / 2; rb = boom_d / 2;
zn = L - nose_len;
rho = (R * R + nose_len * nose_len) / (2 * R);
function ogive_r(h) = sqrt(rho * rho - pow(h, 2)) + R - rho;   // h = distance from the nose base
function smooth(t) = (1 - cos(180 * t)) / 2;
function outer_r(z) = z < boom_len ? rb : z < boom_len + taper ? rb + (R - rb) * smooth((z - boom_len) / taper) : z < zn ? R : ogive_r(z - zn);

module outer() {
    hull() {
        rotate_extrude() polygon(concat([[0, 0]], [for (i = [0 : 60]) let(z = (L - tip_r * 1.2) * i / 60) [max(outer_r(z), 0.01), z]], [[0, L - tip_r * 1.2]]));
        translate([0, 0, L - tip_r]) sphere(r = tip_r);
    }
}
module inner() {   // hollow body with a 50 deg roof under the solid nose
    top = zn - 4;
    rotate_extrude() polygon(concat([[0, 3]],
        [for (i = [0 : 30]) let(z = 3 + (top - 3) * i / 30) [max(outer_r(z) - wall, 0.01), z]],
        [[0, top + (R - wall) * tan(50)]]));
}
module fins() {
    for (i = [0 : fin_n - 1]) rotate([0, 0, 45 + 90 * i])
        rotate([90, 0, 0]) linear_extrude(fin_t, center = true)
            polygon([[rb - 1, 0], [R, 0], [R, fin_tip], [rb + 1, fin_root], [rb - 1, fin_root]]);
}
module hatch_line() {   // shallow groove showing the hatch outline (concept only)
    intersection() {
        difference() {
            translate([0, -hatch_w / 2 - 0.6, hatch_z[0] - 0.6]) cube([R + 1, hatch_w + 1.2, hatch_z[1] - hatch_z[0] + 1.2]);
            translate([0, -hatch_w / 2, hatch_z[0]]) cube([R + 2, hatch_w, hatch_z[1] - hatch_z[0]]);
        }
        difference() { cylinder(h = L, r = R + 1); cylinder(h = L, r = R - 0.5); }
    }
}
// solid column hanging from the hollow's roof that holds the rod: 2.5 mm walls,
// a 5 mm solid floor under the rod, and a pointed (50 deg) bottom so it prints
col_r   = rod_d / 2 + 2.5;
col_bot = L - rod_gap - rod_len - 5;           // bottom of the solid floor
module rod_column() {
    translate([0, 0, col_bot]) cylinder(h = 40, r = col_r);
    translate([0, 0, col_bot - col_r * tan(50)]) cylinder(h = col_r * tan(50) + 0.01, r1 = 0.01, r2 = col_r);
}
// electronics tray mount on the wall opposite the hatch: two rails and a
// bottom ledge (wedge underneath so it prints) that the tray rests on
tray_z = [74, 100];
module tray_mount() {
    for (sy = [-1, 1]) translate([-R + wall - 0.5, sy * 8 - 1, tray_z[0]]) cube([4, 2, tray_z[1] - tray_z[0]]);
    hull() {
        translate([-R + wall - 0.5, -9, tray_z[0] - 0.01]) cube([7, 18, 0.01]);
        translate([-R + wall - 0.5, -9, tray_z[0] - 7 * tan(50)]) cube([0.5, 18, 0.01]);
    }
}
module rod_pocket() { translate([0, 0, L - rod_gap - rod_len]) cylinder(h = rod_len + 0.5, d = rod_d, $fn = 48); }

module airframe() {
    difference() {
        union() { outer(); intersection() { fins(); cylinder(h = L, r = R); }
                  intersection() { rod_column(); outer(); }
                  difference() { cylinder(h = ring_len, r = R); translate([0, 0, -1]) cylinder(h = ring_len + 2, r = R - ring_wall); } }
        difference() { inner(); rod_column(); } hatch_line(); rod_pocket();
    }
}
if (part == "cutaway") difference() { airframe(); translate([-50, 0, -1]) cube([100, 50, 200]); }
else airframe();
