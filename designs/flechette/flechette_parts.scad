// Flechette parts: printed noses and tails that push onto a store-bought
// 8 mm x 150 mm hardened steel rod (3D-printer linear rod). The rod is the
// reusable payload; noses and tails are cheap replaceables.
//
// part = "nose_spike"   sharp cone, sleekest, least drag (chips easily)
//        "nose_ogive"   rounded bullet nose, tougher
//        "tail_fins"    4 swept fins with a slight cant for gentle spin
//        "tail_basket"  flared, windowed drag cone (like a shuttlecock /
//                       the military tail Russ found); no fins to snap
//        "tail_basket_spin"  same, with the 4 inner vanes twisted like fan
//                       blades so air through the cone spins it gently
//        "assembly"     preview with the rod (not for printing)
//
// Fit: very tight, no glue. Sockets are 8.2 mm with 4 thin crush ribs that
// the rod shaves down as it's pressed in (0.25 mm interference per rib).
// Press on with a vise or tap with a mallet against a wood block. If a batch
// is too tight to start, run an 8 mm drill bit into the first few mm by hand.
//
// Print (all supports off, 100% infill or 6+ walls):
//   noses: tip up (socket opens on the bed; its top is a pointed cone)
//   tails: base down (socket opens upward; the rod end sits on its floor)
// The tails fit inside a 38 mm sabot: fin span 30 mm.

$fn = 96;

part        = "assembly";
rod_d       = 8.0;
rod_len     = 150.0;
sock_d      = 8.2;          // socket bore before ribs
rib_r       = 3.75;         // ribs reach this radius (rod radius 4.0): very tight, ribs crush as it goes on
rib_w       = 1.0;
wall        = 1.7;          // socket wall
hub_d       = sock_d + 2 * wall;    // 11.7 mm

// noses
nose_sock   = 14.0;         // socket depth
spike_len   = 30.0;         // shaped tip length above the sleeve
ogive_len   = 24.0;         // shaped tip length above the sleeve
ogive_tip_r = 1.6;

// tails
tail_sock   = 26.0;         // socket depth (long, so it can only go on straight)
tail_floor  = 3.0;          // solid floor under the rod end
fin_span    = 30.0;         // tip to tip (fits inside the sabot)
fin_t       = 1.8;          // fin thickness
fin_root    = 30.0;         // fin length along the hub
fin_tip     = 13.0;         // fin length at the tip
fin_cant    = 2.0;          // deg, gentle spin
basket_d    = 30.0;         // flared tail, outer diameter at the base
basket_len  = 30.0;
basket_wall = 1.6;
windows     = 8;
basket_twist = 16;          // deg the inner vanes turn over the cone length (~5 deg blade angle)

T50 = tan(50);

module socket(depth, from_top = false) {
    // straight bore with crush ribs; pointed (50 deg) end so no flat ceiling
    difference() {
        union() {
            cylinder(h = depth, d = sock_d);
            translate([0, 0, depth - 0.01]) cylinder(h = sock_d / 2 * T50, d1 = sock_d, d2 = 0.01);
        }
        for (a = [45 : 90 : 315]) rotate([0, 0, a])
            translate([rib_r, -rib_w / 2, 0]) cube([sock_d, rib_w, depth]);
    }
}

// noses: a straight sleeve holds the rod; the shaped tip starts above it,
// so the socket never comes near the outside
module nose_spike() {
    difference() {
        union() {
            cylinder(h = nose_sock, d = hub_d);
            translate([0, 0, nose_sock - 0.01])
                rotate_extrude() polygon([[0, 0], [hub_d / 2, 0], [0.3, spike_len], [0, spike_len]]);
        }
        translate([0, 0, -0.01]) socket(nose_sock);
    }
}

module nose_ogive() {
    // tangent ogive from the sleeve to a rounded tip
    Rb = hub_d / 2; L = ogive_len;
    rho = (Rb * Rb + L * L) / (2 * Rb);
    // x = distance from the tip; profile point = [radius, height above the ogive base]
    pts = [for (i = [0 : 40]) let(x = L * i / 40, y = sqrt(rho * rho - pow(L - x, 2)) + Rb - rho) [max(y, 0), L - x]];
    difference() {
        union() {
            cylinder(h = nose_sock, d = hub_d);
            translate([0, 0, nose_sock - 0.01]) hull() {
                rotate_extrude() polygon(concat([[0, 0]], [for (i = [40 : -1 : 0]) if (pts[i][1] < L - ogive_tip_r) pts[i]], [[0, L - ogive_tip_r]]));
                translate([0, 0, L - ogive_tip_r * 1.6]) sphere(r = ogive_tip_r);
            }
        }
        translate([0, 0, -0.01]) socket(nose_sock);
    }
}

module fin() {
    // swept trapezoid: root along the hub, leading edge (top) swept back
    r0 = hub_d / 2 - 0.5; r1 = fin_span / 2;
    rotate([90, 0, 0]) linear_extrude(height = fin_t, center = true)
        polygon([[r0, 0], [r1, 0], [r1, fin_tip], [r0, fin_root]]);
}

module tail_fins() {
    h = tail_floor + tail_sock;
    difference() {
        union() {
            cylinder(h = h, d = hub_d);
            for (a = [0 : 90 : 270]) rotate([0, 0, a]) rotate([fin_cant, 0, 0]) fin();
        }
        translate([0, 0, tail_floor]) cylinder(h = h, d = sock_d);
    }
    // crush ribs inside the open socket
    intersection() {
        for (a = [45 : 90 : 315]) rotate([0, 0, a]) translate([rib_r, -rib_w / 2, tail_floor]) cube([sock_d / 2 - rib_r + 0.3, rib_w, tail_sock]);
        cylinder(h = h, d = sock_d + 0.2);
    }
}

module basket_vanes(twist) {
    // 4 thin vanes tying the cone to the hub; twisted = gentle spin
    rb = basket_d / 2; rt = hub_d / 2;
    intersection() {
        linear_extrude(height = basket_len, twist = twist, slices = 60)
            for (a = [0 : 90 : 270]) rotate([0, 0, a + 22.5]) translate([0, -0.8]) square([rb, 1.6]);
        cylinder(h = basket_len, r1 = rb - 0.3, r2 = rt);
    }
}

module tail_basket(twist = 0) {
    h = tail_floor + tail_sock;
    rb = basket_d / 2; rt = hub_d / 2;
    difference() {
        union() {
            cylinder(h = h, d = hub_d);
            // flared cone: wide at the base, joins the hub at basket_len (walls ~73 deg, prints fine)
            difference() {
                cylinder(h = basket_len, r1 = rb, r2 = rt);
                translate([0, 0, -0.01]) cylinder(h = basket_len - 2, r1 = rb - basket_wall, r2 = rt - 0.2);
            }
            basket_vanes(twist);
        }
        translate([0, 0, tail_floor]) cylinder(h = h, d = sock_d);
        // diamond windows (pointed tops print without support), cut through the cone wall only
        intersection() {
            for (i = [0 : windows - 1]) rotate([0, 0, 360 * i / windows])
                translate([hub_d / 2 + 1.0, 0, basket_len * 0.42]) rotate([0, 90, 0])
                    linear_extrude(height = rb + 2) scale([1.6, 1]) rotate([0, 0, 45]) square(5.2, center = true);
            difference() {
                translate([0, 0, -0.01]) cylinder(h = basket_len + 0.02, r1 = rb + 1, r2 = rt + 1);
                translate([0, 0, -0.02]) cylinder(h = basket_len - 2, r1 = rb - basket_wall - 0.4, r2 = rt - 0.6);
            }
        }
    }
    intersection() {
        for (a = [45 : 90 : 315]) rotate([0, 0, a]) translate([rib_r, -rib_w / 2, tail_floor]) cube([sock_d / 2 - rib_r + 0.3, rib_w, tail_sock]);
        cylinder(h = h, d = sock_d + 0.2);
    }
}

module rod() { color("silver") cylinder(h = rod_len, d = rod_d); }

if (part == "nose_spike") nose_spike();
else if (part == "nose_ogive") nose_ogive();
else if (part == "tail_fins") tail_fins();
else if (part == "tail_basket") tail_basket(0);
else if (part == "tail_basket_spin") tail_basket(basket_twist);
else {
    // two finished flechettes side by side, nose up
    translate([-25, 0, 0]) { tail_fins(); translate([0, 0, tail_floor]) rod();
        translate([0, 0, tail_floor + rod_len - nose_sock]) nose_spike(); }
    translate([25, 0, 0]) { tail_basket(0); translate([0, 0, tail_floor]) rod();
        translate([0, 0, tail_floor + rod_len - nose_sock]) nose_ogive(); }
}
