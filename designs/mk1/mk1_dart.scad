// Mk1 Ducted-Tail Dart
// 38 mm potato-cannon projectile, PCTG, printed nose-up (base on the bed).
//
// Design intent (see CLAUDE.md for project rules):
//  - Strength: no skinny neck. The tail is a tube (boom) inside a full-diameter
//    duct ring, joined by fins. Tubes resist bending far better per gram than
//    solid rods, and every layer through the tail has a large cross-section.
//  - Stability without metal: the aft body is hollow (open at the base), which
//    moves the CG forward. The nose and front of the body are solid.
//  - Fit: two widely spaced full-diameter bearing surfaces (body band behind the
//    nose, duct ring at the tail) keep it from tipping in the barrel.
//  - Spin: helical fins inside the duct, about 6 degrees at the tips.
//  - Prints without supports: all overhangs are 45 degrees or steeper from horizontal.
//
// Suggested print settings (Bambu Studio): uniform infill everywhere (100%, or
// gyroid at high density), 6+ walls, no height-range infill changes, hot nozzle
// and low part-cooling fan for layer adhesion, dry filament.

/* [Global] */
max_width      = 38.5;   // hard project limit, checked below
body_d         = 38.5;   // bearing diameter
total_length   = 125.0;

/* [Nose] */
nose_length    = 30.0;   // ellipsoidal nose
nose_tip_d     = 6.0;    // small flat-ish blunt at the tip (0 = pointed ellipse)

/* [Body] */
bearing_length = 40.0;   // full-diameter band behind the nose
flare_length   = 22.0;   // smooth S-curve from body_d down to boom_d

/* [Tail] */
boom_d         = 16.0;   // outer diameter of the tail tube
duct_length    = 22.0;   // full-diameter ring around the fins, from the base
duct_wall      = 3.0;    // thick enough to survive glancing hits
fin_count      = 8;
fin_thickness  = 4.2;    // thicker for glancing hits
fin_root_fillet= 2.0;
fin_tip_angle  = 6.0;    // helix angle at the fin tips (degrees); sets spin

/* [Hollow aft body] */
wall           = 4.0;    // minimum wall around the internal cavity
cavity_top     = 62.0;   // Z where the cavity's straight section ends
roof_angle     = 50.0;   // cavity roof angle from horizontal (>= 45 prints clean)

/* [Resolution] */
$fn            = 120;
profile_steps  = 60;

assert(body_d <= max_width, "body_d exceeds max_width");

// Derived Z stations (Z = 0 at the base)
R          = body_d / 2;
rb         = boom_d / 2;
z_nose     = total_length - nose_length;      // nose base
z_bearing  = z_nose - bearing_length;         // bottom of bearing band
z_boom     = z_bearing - flare_length;        // top of straight boom
fin_top    = z_bearing;                       // fins run until the body is full width
// Twist so the helix angle at the tip radius equals fin_tip_angle
fin_twist  = tan(fin_tip_angle) * fin_top / R * 180 / PI;

assert(z_boom > duct_length, "duct must end below the flare so air can enter it");

// Outer radius as a function of Z (below the nose)
function smooth(t) = (1 - cos(t * 180)) / 2;
function outer_r(z) =
    z <= z_boom    ? rb :
    z <= z_bearing ? rb + (R - rb) * smooth((z - z_boom) / flare_length) :
                     R;

// Ellipsoidal nose radius at height h above the nose base, with a blunt tip
function nose_r(h) =
    let(a = nose_length, rt = nose_tip_d / 2,
        r = R * sqrt(max(0, 1 - pow(h / a, 2))))
    max(r, h >= a ? 0 : rt);

module outer_body() {
    pts = concat(
        [[0, 0]],
        [for (i = [0 : profile_steps]) let(z = z_bearing * i / profile_steps) [outer_r(z), z]],
        [for (i = [0 : profile_steps]) let(h = nose_length * i / profile_steps)
            [nose_r(h), z_nose + h]],
        [[0, total_length]]
    );
    rotate_extrude() polygon(pts);
}

// Internal cavity: follows the outer profile inward by `wall`, open at the base,
// closed by a cone roof so it prints without supports.
module cavity() {
    r_top = outer_r(cavity_top) - wall;
    roof_h = r_top * tan(roof_angle);
    pts = concat(
        [[0, -1], [rb - wall, -1]],
        [for (i = [0 : profile_steps]) let(z = cavity_top * i / profile_steps)
            [outer_r(z) - wall, z]],
        [[0, cavity_top + roof_h]]
    );
    rotate_extrude() polygon(pts);
}

module fins_2d() {
    offset(r = -fin_root_fillet) offset(r = fin_root_fillet) {
        circle(r = rb);
        for (i = [0 : fin_count - 1])
            rotate(i * 360 / fin_count)
                translate([0, -fin_thickness / 2]) square([R + 2, fin_thickness]);
    }
}

module fins() {
    // Helical fins clipped to the bearing diameter
    intersection() {
        linear_extrude(height = fin_top, twist = -fin_twist, slices = 40, convexity = 10)
            fins_2d();
        cylinder(r = R, h = fin_top);
    }
}

module duct() {
    difference() {
        cylinder(r = R, h = duct_length);
        translate([0, 0, -1]) cylinder(r = R - duct_wall, h = duct_length + 2);
    }
}

module mk1_dart() {
    difference() {
        union() {
            outer_body();
            fins();
            duct();
        }
        cavity();
    }
}

mk1_dart();
