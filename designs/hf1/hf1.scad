// WORK IN PROGRESS: threaded-nose + side-hatch layout, superseded pending Russ's decision on
// nose-ejection deployment with dual release. Kept for reference; not checked or printable yet.
// HF1 High-Flier, v1 (fit-test version).
// Full-bore dart for maximum height with parachute recovery, fired behind the wad.
// Two printed parts plus a steel rod:
//   BODY  (part = "body"):  boom + 4 fins (3.2 mm, root fillets) + thin ring, taper,
//         thin-walled parachute bay, side hatch printed OPEN on a flexure hinge
//         (the hinge is the spring: close it, latch it, and it pops open on release),
//         electronics bay on the axis, internal thread at the top.
//   NOSE  (part = "nose"):  bullet (tangent ogive) nose with a solid threaded spigot;
//         an 8 x 36.5 mm steel rod is sealed inside with a print PAUSE.
// Everything heavy sits on the axis (balance). Print both nose-up, supports off,
// 100% infill. Body: the hatch prints leaning out 35 deg (that's intended).
// NOSE PAUSE: pause at the layer where z = pause_z (echoed below), drop the rod in, resume.

$fn = 120;
part     = "assembly";   // "body", "nose", "assembly", "assembly_closed", "cutaway"
body_d   = 39.6;
L        = 185;
wall     = 1.6;
// tail
boom_d   = 16; boom_len = 42; taper = 30;
fin_n    = 4; fin_t = 3.2; fin_root = 50; fin_tip = 24; fillet = 2.0; fin_cant = 1.0; // deg at the tips
ring_len = 16; ring_wall = 1.6;
base_t   = 3;            // solid floor the wad pushes on
// joint and nose
joint_z  = 130;          // body top / nose shoulder
spigot   = 10;           // threaded length
nose_cyl = 7;            // short full-diameter section on the nose before the ogive
ogive_len= 48; tip_r = 3.0;
t_pitch  = 4; t_depth = 1.4; t_flank = 50; t_clr = 0.3;
// rod
rod_bore = 8.15; rod_len = 36.5; rod_floor = 3;
// electronics bay and parachute bay
sled_ledge = 101;        // ledge the electronics sled rests on (sled 103 -> 120)
// hatch (on +X), flexure hinge at the bottom, printed open
hatch_w  = 22; flex_z = 56; flex_len = 6; door_z0 = 62; door_z1 = 82; flex_t = 0.7;
door_open = 35;          // print angle
kerf     = 0.5;
tongue_w = 4; tongue_h = 5;

R  = body_d / 2; rb = boom_d / 2; ri = R - wall;
zo = joint_z + nose_cyl;                       // ogive base
apex = door_z1 + (hatch_w / 2) * tan(50);      // door gable apex
rho = (R * R + ogive_len * ogive_len) / (2 * R);
function smooth(t) = (1 - cos(180 * t)) / 2;
function outer_r(z) = z < boom_len ? rb : z < boom_len + taper ? rb + (R - rb) * smooth((z - boom_len) / taper)
                    : z < zo ? R : sqrt(rho * rho - pow(z - zo, 2)) + R - rho;
// thread radii
tb_root = R - 2.5;             // body groove root radius (2.5 mm wall there)
tb_crest = tb_root - t_depth;  // body ridge tip
tn_core = tb_crest - t_clr;    // nose spigot core
tn_crest = tn_core + t_depth;  // nose ridge tip (clears body root by t_clr)
rod_bot = joint_z - spigot + rod_floor;
rod_top = rod_bot + rod_len;
pause_z = rod_top + 0.5;       // straight pocket top: pause here
echo(str("NOSE: pause at z = ", pause_z - (joint_z - spigot), " mm above the nose's bed; rod ", rod_bot, "-", rod_top,
         " (", L - rod_top, " mm below the tip)"));

// ---- helpers
module helix_ridge(r0, r1, z0, h, inward = false) {
    // triangular thread ridge from radius r0 (root) to r1 (tip), right-hand, swept along z
    n = 48; turns = h / t_pitch; steps = ceil(n * turns);
    hw = t_depth / tan(t_flank);       // half the root width
    pts = [for (i = [0 : steps]) let(a = 360 * i / n, z = z0 + t_pitch * i / n)
             each [[r0 * cos(a), r0 * sin(a), z - hw], [r1 * cos(a), r1 * sin(a), z], [r0 * cos(a), r0 * sin(a), z + hw]]];
    faces = concat(
        [for (i = [0 : steps - 1]) for (k = [0 : 2]) let(a = 3 * i + k, b = 3 * i + (k + 1) % 3)
            each [[a, b, b + 3], [a, b + 3, a + 3]]],
        [[0, 1, 2], [3 * steps + 2, 3 * steps + 1, 3 * steps]]);
    polyhedron(pts, inward ? faces : [for (f = faces) [f[2], f[1], f[0]]]);
}
module window2d(grow = 0) {   // hatch outline in the (y, z) plane: rectangle + 50 deg gable
    polygon([[-hatch_w / 2 - grow, door_z0 - grow], [hatch_w / 2 + grow, door_z0 - grow], [hatch_w / 2 + grow, door_z1],
             [tongue_w / 2 + grow, apex - (tongue_w / 2) * tan(50)], [tongue_w / 2 + grow, apex + tongue_h + grow],
             [-tongue_w / 2 - grow, apex + tongue_h + grow], [-tongue_w / 2 - grow, apex - (tongue_w / 2) * tan(50)],
             [-hatch_w / 2 - grow, door_z1]]);
}
module window_prism(grow = 0) { rotate([90, 0, 90]) linear_extrude(R + 5) window2d(grow); }
module flex_prism(grow = 0) { translate([0, -hatch_w / 2 - grow, flex_z]) cube([R + 5, hatch_w + 2 * grow, door_z0 - flex_z + 0.01]); }
module shell_ring(z0, z1) { translate([0, 0, z0]) difference() { cylinder(h = z1 - z0, r = R); translate([0, 0, -1]) cylinder(h = z1 - z0 + 2, r = ri); } }

// ---- body
module body_outer() {
    rotate_extrude() polygon(concat([[0, 0]], [for (i = [0 : 80]) let(z = joint_z * i / 80) [outer_r(z), z]], [[0, joint_z]]));
}
module body_hollow() {
    // thin-walled interior from the base floor up to the electronics bay; ledge and thread wall left solid
    rotate_extrude() polygon(concat([[0, base_t]],
        [for (i = [0 : 60]) let(z = base_t + (sled_ledge - 3 - base_t) * i / 60) [max(outer_r(z) - wall, 0.01), z]],
        [[ri - 3, sled_ledge - 3 + 3 * tan(50)], [ri - 3, joint_z - spigot - 0.01]],          // ledge: 3 mm ring, 50 deg underside
        [[tb_root - 0.01, joint_z - spigot], [tb_root, joint_z + 1], [0, joint_z + 1]]));
}
module fins2d() {
    offset(r = -fillet) offset(r = fillet) {
        circle(r = rb);
        for (i = [0 : fin_n - 1]) rotate(45 + 360 * i / fin_n) translate([0, -fin_t / 2]) square([R + 2, fin_t]);
    }
}
module fins() {
    twist = tan(fin_cant) * fin_root / R * 180 / PI;
    intersection() {
        linear_extrude(height = fin_root, twist = -twist, slices = 30) fins2d();
        rotate_extrude() polygon([[0, 0], [R, 0], [R, fin_tip], [rb + 0.5, fin_root], [0, fin_root]]);
    }
}
module ring() { difference() { cylinder(h = ring_len, r = R); translate([0, 0, -1]) cylinder(h = ring_len + 2, r = R - ring_wall); } }
module latch_boss() {
    // inside the wall behind the door's tongue; radial pin hole; 50 deg underside
    z0 = apex - 1;
    difference() {
        hull() {
            translate([ri - 3, -3, z0]) cube([3.2, 6, tongue_h + 1]);
            translate([ri, -3, z0 - 3 * tan(50)]) cube([0.2, 6, 0.01]);
        }
        translate([ri - 4, 0, apex + tongue_h / 2]) rotate([0, 90, 0]) cylinder(h = 4.5, d = 1.2, $fn = 16);
    }
}
module door(open = 0) {
    // the shell piece inside the window (minus kerf) + flexure strip below it + tongue with a blind pin hole
    translate([0, 0, flex_z]) rotate([0, open, 0]) translate([0, 0, -flex_z]) {
        difference() {
            intersection() { shell_ring(door_z0, apex + tongue_h); window_prism(-kerf / 2); }
            translate([ri - 1, 0, apex + tongue_h / 2]) rotate([0, 90, 0]) cylinder(h = 1 + wall - 0.5, d = 1.25, $fn = 16);
        }
        // flexure: thin strip on the outer side of the wall from flex_z up to the door
        intersection() { shell_ring(flex_z, door_z0 + 0.5); translate([R - flex_t, -hatch_w / 2 + kerf / 2, flex_z]) cube([2, hatch_w - kerf, door_z0 - flex_z + 0.5]); }
    }
}
module body(open = door_open) {
    difference() {
        union() {
            difference() {
                union() { body_outer(); intersection() { fins(); cylinder(h = L, r = R); } ring(); }
                body_hollow();
                // anchor hole for the shroud lines, opposite the hatch, through the ledge
                translate([-(ri - 1.5), 0, sled_ledge - 8]) cylinder(h = 12, d = 2, $fn = 16);
            }
            translate([0, 0, joint_z - spigot]) helix_ridge(tb_root + 0.01, tb_crest, 0, spigot - t_pitch / 2 + 0.5, true);
            latch_boss();
        }
        window_prism(kerf / 2);
        flex_prism(kerf / 2);
    }
    door(open);
}

// ---- nose
module nose() {
    difference() {
        union() {
            rotate_extrude() polygon(concat([[0, joint_z]], [for (i = [0 : 60]) let(z = joint_z + (L - tip_r * 1.2 - joint_z) * i / 60) [outer_r(z), z]],
                                            [[0, L - tip_r * 1.2]]));
            translate([0, 0, L - tip_r]) sphere(r = tip_r);
            translate([0, 0, joint_z - spigot]) cylinder(h = spigot + 0.01, r = tn_core);
            translate([0, 0, joint_z - spigot]) intersection() {
                helix_ridge(tn_core - 0.01, tn_crest, t_pitch / 2, spigot - t_pitch);
                cylinder(h = spigot, r = tn_crest + 1);
            }
        }
        // rod pocket: straight to pause_z, then a 50 deg cone printed after the pause
        translate([0, 0, rod_bot]) cylinder(h = pause_z - rod_bot, d = rod_bore, $fn = 48);
        translate([0, 0, pause_z - 0.01]) cylinder(h = rod_bore / 2 * tan(50), d1 = rod_bore, d2 = 0.01, $fn = 48);
        // lead-in chamfer on the spigot bottom edge
        translate([0, 0, joint_z - spigot - 0.01]) difference() { cylinder(h = 1.2, r = tn_crest + 1); cylinder(h = 1.2, r1 = tn_core - 0.6, r2 = tn_core + 0.6); }
    }
}

if (part == "body") body();
else if (part == "nose") translate([0, 0, -(joint_z - spigot)]) nose();
else if (part == "assembly_closed") { body(0); nose(); }
else if (part == "cutaway") difference() { union() { body(0); nose(); color("silver") translate([0, 0, rod_bot]) cylinder(h = rod_len, d = 8); } translate([-50, 0, -1]) cube([100, 60, 300]); }
else { body(); color("SteelBlue") nose(); }
