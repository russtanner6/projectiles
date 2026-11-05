// Flechette parts: printed noses and tails that push onto a store-bought
// 150 mm steel rod. The rod is the reusable payload; noses and tails are
// cheap replaceables. Two rod sizes (set rod_d, see flechette_dims.scad):
//   8 mm hardened linear rod or 5/16 in. plain steel rod (default)
//   1/2 in. (12.7 mm) rod: -D rod_d=12.7 (6 fins instead of 4, bigger hub)
//
// part = "nose_spike"   sharp cone, sleekest, least drag (chips easily)
//        "nose_ogive"   rounded bullet nose, tougher
//        "tail_fins"    4 (8 mm) or 6 (1/2 in.) swept fins with a slight cant for gentle spin
//        "tail_basket"  flared, windowed drag cone (like a shuttlecock /
//                       the military tail Russ found); no fins to snap
//        "tail_basket_spin"  same, with the 4 inner vanes twisted like fan
//                       blades so air through the cone spins it gently
//        "assembly"     preview with the rod (not for printing)
//
// Fit: snug press fit, no glue, no crush ribs (rev 2: PCTG ribs didn't crush).
// A plain round grip section (rod + grip_fit, 0.1 mm) holds the part; the rest
// of the bore is looser so it only grips where it should. Tails have a lead-in
// chamfer. Press on by hand or with a vise. Tune grip_fit with the socket fit
// gauge (socket_fit_gauge.scad).
//
// Print (all supports off, 100% infill or 6+ walls):
//   noses: tip up (socket opens on the bed; its top is a pointed cone).
//          Use a brim: they stand on the narrow end of the taper.
//   tails: base down (socket opens upward; the rod end sits on its floor)
// The tails fit inside a 38 mm sabot: fin span 30 mm.

$fn = 96;

part        = "assembly";
include <flechette_dims.scad>

module nose_socket(depth, grip_from) {
    // opens at the bed; loose below grip_from, snug grip above, pointed (50 deg) top
    rc = clear_d / 2; rg = grip_d / 2;
    translate([0, 0, -0.01]) rotate_extrude() polygon([
        [0, 0], [rc, 0], [rc, grip_from], [rg, grip_from + (rc - rg) * T50],
        [rg, depth], [0, depth + rg * T50]]);
}

module tail_socket(h) {
    // opens at the top: lead-in chamfer, snug grip for grip_len, looser below
    // down to the floor the rod end sits on. The step from loose to snug slopes
    // at 50 deg so nothing overhangs.
    rc = clear_d / 2; rg = grip_d / 2;
    rotate_extrude() polygon([
        [0, tail_floor], [rc, tail_floor], [rc, h - grip_len],
        [rg, h - grip_len + (rc - rg) * T50], [rg, h - lead_in],
        [rg + lead_in, h], [rg + lead_in, h + 1], [0, h + 1]]);
}

// noses: a tapered tail (Russ's idea) runs back down the rod from the
// sleeve, so there's no abrupt step from the nose to the rod: cleaner airflow,
// and the longer grip keeps the nose straight. The taper part is a loose
// sliding fit; only the sleeve grips. Above the sleeve is the shaped tip, so the socket never
// comes near the outside.
module nose_base() {
    // taper (z 0..nose_taper, 1 mm wall at its end) + straight sleeve
    rotate_extrude() polygon([[0, 0], [taper_end_r, 0], [hub_d / 2, nose_taper],
                              [hub_d / 2, nose_taper + nose_sock], [0, nose_taper + nose_sock]]);
}

module nose_spike() {
    difference() {
        union() {
            nose_base();
            translate([0, 0, nose_taper + nose_sock - 0.01])
                rotate_extrude() polygon([[0, 0], [hub_d / 2, 0], [0.3, spike_len], [0, spike_len]]);
        }
        nose_socket(nose_taper + nose_sock, nose_taper);
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
            nose_base();
            translate([0, 0, nose_taper + nose_sock - 0.01]) hull() {
                rotate_extrude() polygon(concat([[0, 0]], [for (i = [40 : -1 : 0]) if (pts[i][1] < L - ogive_tip_r) pts[i]], [[0, L - ogive_tip_r]]));
                translate([0, 0, L - ogive_tip_r * 1.6]) sphere(r = ogive_tip_r);
            }
        }
        nose_socket(nose_taper + nose_sock, nose_taper);
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
        intersection() {   // flat bottom: the canted fins would poke a sliver below the bed
          cylinder(h = h + 20, r = 40);
          union() {
            cylinder(h = h, d = hub_d);
            for (i = [0 : fin_n - 1]) rotate([0, 0, 360 * i / fin_n + 180 / $fn]) rotate([fin_cant, 0, 0]) fin();   // offset half a facet: avoids a mesh sliver
          }
        }
        tail_socket(h);
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
        tail_socket(h);
        // diamond windows (pointed tops print without support), cut through the cone wall only
        intersection() {
            for (i = [0 : windows - 1]) rotate([0, 0, 360 * i / windows])
                translate([hub_d / 2 + 1.0, 0, basket_len * 0.42]) rotate([0, 90, 0])
                    linear_extrude(height = rb + 2) polygon([[window_h / 2, 0], [0, window_w / 2], [-window_h / 2, 0], [0, -window_w / 2]]);
            difference() {
                translate([0, 0, -0.01]) cylinder(h = basket_len + 0.02, r1 = rb + 1, r2 = rt + 1);
                translate([0, 0, -0.02]) cylinder(h = basket_len - 2, r1 = rb - basket_wall - 0.4, r2 = rt - 0.6);
            }
        }
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
    translate([-28, 0, 0]) { tail_fins(); translate([0, 0, tail_floor]) rod();
        translate([0, 0, tail_floor + rod_len - nose_sock - nose_taper]) nose_spike(); }
    translate([28, 0, 0]) { tail_basket(0); translate([0, 0, tail_floor]) rod();
        translate([0, 0, tail_floor + rod_len - nose_sock - nose_taper]) nose_ogive(); }
}
