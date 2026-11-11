// Mk1-R Rod Dart: the Mk1 ducted-tail dart with an 8 mm steel rod locked
// inside the front by a one-way snap plug (Russ's design). Generated from
// mk1_dart.scad plus the rod channel and plug below; edit the rod/plug section here.
//
// Rod: 8 mm steel, rod_len (45 mm: three from a 150 mm rod), slid in from the
// base until it stops at the top of the channel, 10 mm below the nose tip.
// Channel bore 8.15 mm (Russ's fit-gauge pick for a sliding fit).
// Plug: pushed in from the base with any stick (a rod offcut works). Its two
// thick arms are cammed inward by the ramps inside the channel, then spring
// out into a ratchet of 10 one-way teeth near the base, so it can never come
// back out. A small spring stack on the plug's top presses the rod up against
// the channel top (no rattle); the ratchet and spring absorb +/-5 mm of rod
// length error, so the hacksaw cut doesn't have to be exact.
// Print the plug lying on its one flat side (part = "plug"); it is round everywhere else.
//
// Base dart: 38 mm-class potato-cannon projectile, PCTG, printed nose-up (base on the bed).
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
part           = "dart";   // "dart", "plug" (print orientation), "assembly" (preview)
max_width      = 40.0;   // barrel-sized like the sabot and wad (Russ): 39.7 / 39.0 / 38.6
body_d         = 39.0;   // bearing diameter: 39.7, 39.0 or 38.6 (-D body_d=...), barrel ~40.1 mm
total_length   = 135.0;  // lengthened from 125 to move the CG forward relative to the fins

/* [Nose] */
nose_length    = 30.0;   // ellipsoidal nose
nose_tip_d     = 6.0;    // small flat-ish blunt at the tip (0 = pointed ellipse)

/* [Body] */
bearing_length = 50.0;   // full-diameter band behind the nose
flare_length   = 22.0;   // smooth S-curve from body_d down to boom_d

/* [Tail] */
boom_d         = 16.0;   // outer diameter of the tail tube
duct_length    = 16.0;   // full-diameter ring around the fins, from the base
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


// ---------------------------------------------------------------------------
// Rod channel, ratchet and snap plug
rod_d        = 8.0;
rod_bore     = 8.15;      // Russ's fit gauge, 4th hole: slides in, no slop
rod_len      = 45.0;      // nominal rod length (three per 150 mm rod; the 15 mm offcut is the plug pusher).
                          // 45 (not 49) so the plug's spring tip sits 4 mm up inside the channel, centered
rod_top_gap  = 10.0;      // channel top (rod end) this far below the nose tip
rat_z0       = 0.0;       // ratchet teeth start at the base
rat_n        = 10;
rat_pitch    = 1.3;
rat_depth    = 0.8;       // tooth depth (radial)
plug_r       = 3.95;      // plug body radius (slides in the 8.15 bore)
plug_flat    = 2.75;      // plug has ONE flat (y = -plug_flat) to print on; the rest is round
                          // (rev 2: was flat on both sides, which left ~1.5 mm of side play)
arm_len      = 16.0;      // springy arms (split by a slot)
arm_slot     = 2.2;
barb_n       = 2;
spring_beams = 4;
spring_beam  = 1.0;
spring_gap   = 0.8;
spring_cap   = 1.5;
preload      = 1.5;       // spring squeeze when the rod is exactly rod_len

rod_top  = total_length - rod_top_gap;
r_in     = rod_bore / 2;
r_out    = r_in + rat_depth;
barb_r   = r_out - 0.15;
spring_h = spring_beams * spring_beam + (spring_beams + 1) * spring_gap + spring_cap;
plug_top = rod_top - rod_len + preload;                 // free (unsqueezed) top of the plug
plug_bot = rat_z0 + 5 * rat_pitch - 1.0;                // nominal: barbs on the middle teeth
plug_len = plug_top - plug_bot;
assert(rod_top - rod_len > plug_bot + arm_len + spring_h + 5, "rod too long for the plug");

module rod_channel() {
    // straight bore up the axis with a sawtooth ratchet at the base and a
    // 50 deg pointed top; every tooth's catch face faces up, every ramp >= 50 deg
    ramp = rat_pitch;   // full pitch is ramp (step is vertical in Z)
    pts = concat(
        [[0, -1], [r_out, -1]],
        [for (i = [0 : rat_n - 1]) each [[r_out, rat_z0 + i * rat_pitch], [r_in, rat_z0 + (i + 1) * rat_pitch]]],
        [[r_in, rod_top], [0, rod_top + r_in * tan(50)]]
    );
    rotate_extrude($fn = 64) polygon(pts);
}

module rod_dart() {
    difference() {
        union() { outer_body(); fins(); duct(); }
        cavity();
        rod_channel();
    }
}

// plug in the dart frame, at its nominal installed position (unsqueezed)
module plug_section(h) {
    linear_extrude(h) intersection() { circle(r = plug_r, $fn = 64); translate([-plug_r - 1, -plug_flat]) square([2 * plug_r + 2, plug_flat + plug_r + 1]); }
}
module plug() {
    zb = plug_bot; zs = plug_top - spring_h;
    difference() {
        union() {
            translate([0, 0, zb]) plug_section(zs - zb);
            // barbs: square catch face down, ramp up, as rings (so they follow the
            // round bore exactly) cut down to the flat-sided arms
            intersection() {
                for (k = [0 : barb_n - 1]) let(zc = zb + 1.0 + k * rat_pitch)
                    rotate_extrude($fn = 64) polygon([[plug_r - 0.3, zc], [barb_r, zc], [r_in - 0.1, zc + rat_pitch - 0.1], [plug_r - 0.3, zc + rat_pitch - 0.1]]);
                // hooks only on the sides (within 30 deg of the arms' bending direction),
                // so they fold fully inward when the arms squeeze
                translate([0, 0, zb]) linear_extrude(arm_len) translate([-barb_r - 1, -plug_flat]) square([2 * barb_r + 2, plug_flat + barb_r * sin(30)]);   // down to the print flat (no overhang)
            }
        }
        // slot that splits the bottom into two arms
        translate([-arm_slot / 2, -plug_flat - 1, zb - 1]) cube([arm_slot, plug_flat + plug_r + 3, arm_len + 1]);
    }
    // spring stack: beams joined at alternating ends, then a cap that meets the rod
    intersection() {
        union() {
            for (k = [0 : spring_beams]) let(z0 = zs + k * (spring_beam + spring_gap), side = (k % 2 == 0) ? 1 : -1)
                translate([side > 0 ? plug_r - 1.2 : -plug_r - 0.5, -plug_flat, z0 - 0.01]) cube([1.7, plug_flat + plug_r + 1, spring_gap + 0.02]);
            for (k = [0 : spring_beams - 1]) let(z0 = zs + spring_gap + k * (spring_beam + spring_gap))
                translate([-plug_r - 1, -plug_flat, z0]) cube([2 * plug_r + 2, plug_flat + plug_r + 1, spring_beam]);
            translate([-plug_r - 1, -plug_flat, plug_top - spring_cap]) cube([2 * plug_r + 2, plug_flat + plug_r + 1, spring_cap]);
        }
        translate([0, 0, zs - 0.02]) plug_section(spring_h + 0.04);
    }
}

echo(str("rod ", rod_len, " mm, top at ", rod_top, " (", rod_top_gap, " mm below the tip); plug length ", plug_len));

if (part == "dart") rod_dart();
else if (part == "plug") translate([0, 0, plug_flat]) rotate([90, 0, 0]) translate([0, 0, -plug_bot]) plug();
else if (part == "plug_placed") plug();
else { rod_dart(); color("silver") translate([0, 0, rod_top - rod_len]) cylinder(d = rod_d, h = rod_len); color("orange") plug(); }
