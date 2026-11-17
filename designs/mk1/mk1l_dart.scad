// Mk1-L Lead Dart (Russ): the Mk1 ducted-tail dart with a sealed lead pocket in the nose,
// filled from the BASE after printing and closed with a snap-rivet plug.
// Generated from mk1r_dart.scad (same body); edit the lead / plug section here.
//
// Nose: solid, no hole, no print pause. Inside it, a thick-walled pocket (19 mm wide, 50 deg
// cone roof, 10.3 mm side walls, ~22 mm of solid nose in front, 9.5 mm floor). An 8.15 mm
// channel runs up the axis from the base into the pocket floor.
// Plug rev 2 (Russ: the first plug slid all the way up the tube when the shot was short):
//   - flat HEAD that sits in a recess at the base: a hard stop, it can't go in any farther;
//   - tuning-fork split with two big HOOKS that snap into a groove just inside the base:
//     it can't come back out (locked both ways, no travel);
//   - spring on its tip keeps the shot packed against the nose;
//   - to remove (if you overfill): pinch the two head halves together with needle-nose pliers
//     in the two notches beside the head, then pull.
// FILL GAUGE (part = "gauge"): a stick with two grooves. Dart nose-down in a cup, pour shot in,
// tap to settle, push the gauge in until its tip touches the shot:
//   neither groove showing -> add shot;  one groove showing -> just right;  both showing -> too much.
// Print the dart 100% infill, 6+ walls, nose up, supports off. Plug and gauge print on their flat side.
/* [Global] */
part           = "dart";   // "dart", "plug" (print orientation), "assembly" (preview)
max_width      = 40.0;   // barrel-sized like the sabot and wad (Russ): 39.6
body_d         = 39.6;   // bearing diameter (Russ: 39.6, the only size), barrel ~40.1 mm
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
cavity_top     = 55.0;   // Mk1-L: aft cavity shortened (Mk1: 62) to make room for a longer lead pocket
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
rod_len      = 36.5;      // rod length: four per 150 mm rod (rev 3; was 45). The rod's bottom end
                          // stays where it was, so the plug is unchanged and its tip sits 4 mm up inside the channel
rod_top_gap  = 18.5;      // channel top (rod end) this far below the nose tip (rev 3: was 10;
                          // ~13.6 mm of solid plastic over the channel's pointed top so hard hits don't crack the nose)
rat_z0       = 0.0;       // ratchet teeth start at the base
rat_n        = 16;       // Mk1-L: 16 teeth (Mk1-R has 10) so all 4 barbs stay engaged across the +/-6 mm fill range
rat_pitch    = 1.3;
rat_depth    = 0.8;       // tooth depth (radial)
plug_r       = 3.95;      // plug body radius (slides in the 8.15 bore)
plug_flat    = 2.75;      // plug has ONE flat (y = -plug_flat) to print on; the rest is round
                          // (rev 2: was flat on both sides, which left ~1.5 mm of side play)
arm_len      = 16.0;      // springy arms (split by a slot)
arm_slot     = 2.2;
barb_n       = 4;        // Mk1-L: 4 barbs per arm (Mk1-R has 2): Russ wants no chance of it coming out
spring_beams = 6;         // Mk1-L plug rev 2: more spring travel (takes +/-1.5 mm of fill level)
spring_beam  = 1.0;
spring_gap   = 0.8;
spring_cap   = 1.5;
preload      = 2.5;       // spring squeeze at the target fill level

lead_r      = 9.5;       // pocket radius: 10.3 mm side walls to the 39.6 mm body (Russ: thick walls, punishing hits)
roof_back   = 3.0;       // pocket roof starts this far behind the nose base (more solid nose in front)
lead_level_gap = 6.0;    // target shot surface this far below the pocket floor, in the channel; the ratchet takes +/-5 mm
z_roof0     = z_nose - roof_back;
z_peak      = z_roof0 + lead_r * tan(roof_angle);
aft_peak    = cavity_top + (outer_r(cavity_top) - wall) * tan(roof_angle);
lead_floor  = aft_peak + 9.5;                          // 9.5 mm floor over the aft cavity's cone roof
lead_level  = lead_floor - lead_level_gap;
z_chan0     = cavity_top + (outer_r(cavity_top) - wall - rod_bore / 2) * tan(roof_angle);  // channel's solid part starts
assert(total_length - z_peak >= 20, "nose too thin in front of the lead");
assert(lead_level - z_chan0 >= 6, "plug tip must sit well inside the channel");
rod_top  = lead_floor + 1;                              // channel runs up into the pocket
r_in     = rod_bore / 2;
// snap-rivet plug (rev 2)
cb_r     = 5.8;          // head recess at the base
cb_d     = 3.0;
head_r   = 5.6;
hook_h   = 1.3;          // how far each hook sticks out past the bore
z_g0     = 10.0;         // groove floor = the hooks' catch ledge
z_g1     = 13.0;         // groove straight part ends; 50 deg chamfer back to the bore above it
r_g      = r_in + hook_h + 0.2;
z_root   = 30.0;         // top of the fork slot (where the prongs bend)
z_hook   = z_g0 + 0.2;   // hooks' catch face (0.2 mm play)
pinch_w  = 4.0;          // pliers notches beside the head (on the prongs' sides)
pinch_r  = 7.0;
gauge_tol = 1.5;         // fill tolerance the spring takes (+/-)
spring_h = spring_beams * spring_beam + (spring_beams + 1) * spring_gap + spring_cap;
plug_top = lead_level + preload;                        // free (unsqueezed) top of the plug
plug_bot = 0.3;                                         // head sits 0.3 mm inside the base face
plug_len = plug_top - plug_bot;
assert(lead_level > z_root + spring_h + 5, "plug too short");
assert(spring_beams * 1 + 0 >= 0);

module rod_channel() {
    // head recess, bore, hook groove (flat catch floor, 50 deg chamfer roof), bore up to the pocket
    rotate_extrude($fn = 64) polygon([
        [0, -1], [cb_r, -1], [cb_r, cb_d], [r_in, cb_d + (cb_r - r_in) * tan(50)],   // 50 deg conical seat (no flat ceiling)
        [r_in, z_g0], [r_g, z_g0], [r_g, z_g1], [r_in, z_g1 + (r_g - r_in) * tan(50)],
        [r_in, rod_top], [0, rod_top + r_in * tan(50)]]);
    // pliers notches beside the head, on the prongs' sides (+/-X); flat roof is the base face side
    for (s = [-1, 1]) rotate([0, 0, s > 0 ? 0 : 180]) rotate([90, 0, 90]) linear_extrude(pinch_r)
        polygon([[-pinch_w / 2, -1], [pinch_w / 2, -1], [pinch_w / 2, cb_d - 1.5], [0, cb_d - 1.5 + pinch_w / 2 * tan(50)], [-pinch_w / 2, cb_d - 1.5]]);   // gable roof
}
module lead_pocket() {
    rotate_extrude() polygon([[0, lead_floor], [lead_r, lead_floor], [lead_r, z_roof0], [0, z_peak]]);
}
module lead_fill() {     // shot volume: pocket + channel down to lead_level
    lead_pocket();
    translate([0, 0, lead_level]) cylinder(h = lead_floor - lead_level + 0.01, r = rod_bore / 2, $fn = 64);
}
module rod_dart() {
    difference() {
        union() { outer_body(); fins(); duct(); }
        cavity();
        rod_channel();
        lead_pocket();
    }
}

// plug in the dart frame, installed (spring unsqueezed)
module plug_section(h, r = plug_r) {
    linear_extrude(h) intersection() { circle(r = r, $fn = 64); translate([-r - 1, -plug_flat]) square([2 * r + 2, plug_flat + r + 1]); }
}
module plug() {
    zs = plug_top - spring_h;
    difference() {
        union() {
            intersection() {                                                            // head (hard stop): cone top
                translate([0, 0, plug_bot]) plug_section(cb_d + 3 - plug_bot, head_r);    // seats on the 50 deg seat
                rotate_extrude($fn = 64) polygon([[0, 0], [head_r, 0], [head_r, cb_d - 0.15 - (cb_r - head_r) * tan(50)], [0, cb_d - 0.15 + cb_r * tan(50)]]);
            }
            translate([0, 0, cb_d - 0.01]) plug_section(zs - cb_d + 0.01);              // stem
            // hooks on both prongs: flat catch face down, 30 deg lead-in ramp up. Made as a ring
            // (so the ramp follows the round bore exactly) cut down to the two prong sides
            intersection() {
                rotate_extrude($fn = 64) polygon([[plug_r - 0.5, z_hook], [r_g - 0.2, z_hook], [r_g - 0.2, z_hook + 2.0],
                                 [plug_r - 0.5, z_hook + 2.0 + (r_g - 0.2 - plug_r + 0.5) / tan(30)]]);
                translate([-10, -plug_flat, z_hook - 1]) cube([20, plug_flat + 2.0, 10]);    // within ~30 deg of the bend direction
            }
        }
        // tuning-fork slot: wide at the head, closing to nothing at z_root, so pinching the head
        // halves pulls both hooks fully inside the bore
        w_hook = 2 * (hook_h + 0.1);
        w0 = w_hook * (z_root - plug_bot) / (z_root - z_hook - 1);
        translate([0, plug_r + 2, 0]) rotate([90, 0, 0]) linear_extrude(2 * plug_r + 4)
            polygon([[-w0 / 2, -1], [w0 / 2, -1], [0, z_root]]);
    }
    // spring stack: beams joined at alternating ends, then a cap that meets the shot
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
// fill gauge: round stick (one flat), tip end goes in; two grooves at lead_level -/+ gauge_tol
// from the tip, then a fat handle
module gauge() {
    gl = lead_level + 25;
    difference() {
        union() {
            plug_section(gl, 3.6);
            translate([0, 0, lead_level + 12]) plug_section(13, 6);                       // handle
        }
        for (d = [lead_level - gauge_tol, lead_level + gauge_tol])
            translate([-10, 1.5, d - 0.6]) cube([20, 10, 1.2]);                       // groove across the top
    }
}

echo(str("PLUG rev 2: length ", plug_len, "; groove at ", z_g0, "; gauge grooves at ", lead_level - gauge_tol, " and ", lead_level + gauge_tol, " from the tip. LEAD: shot surface ", total_length - lead_level, " mm from the nose tip = ", lead_level, " mm down from the base; plug length ", plug_len, "; solid nose over pocket ", total_length - z_peak, " mm; floor ", lead_floor - aft_peak, " mm"));

if (part == "dart") rod_dart();
else if (part == "plug") translate([0, 0, plug_flat]) rotate([90, 0, 0]) translate([0, 0, -plug_bot]) plug();
else if (part == "gauge") translate([0, 0, plug_flat]) rotate([90, 0, 0]) gauge();
else if (part == "plug_placed") plug();
else if (part == "slug") lead_fill();
else { rod_dart(); color("silver") lead_fill(); color("orange") plug(); }
