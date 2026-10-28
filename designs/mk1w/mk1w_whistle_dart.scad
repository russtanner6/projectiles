// Mk1-W Screaming Dart, Rev B (death-whistle variant of the Mk1 Ducted-Tail Dart)
// 38 mm potato-cannon projectile, PCTG, printed nose-up (base on the bed).
//
// Same outside as Mk1. Inside, a death-whistle sound system driven by ram air,
// copied from whistle test piece D, which screamed like the skull whistle when
// blown (pieces B and C, without D's inlet channel, were too high-pitched):
//  - An 8 mm inlet at the nose tip, with a smoothly rounded mouth, feeds a 22 mm channel. In flight, air piles
//    up at the nose and is forced in, the way breath goes into the whistle.
//  - The channel ends in a 6 mm x 3 mm blow hole, aimed at the 7 mm hole in the
//    top of a hollow inner "ball" 5.4 mm below, inside a chamber with a gap all
//    around the ball.
//  - Air leaves through eight slots in the flare (between all fins) and the open
//    tail tube, about as much outlet area as the gap around the ball.
//  - Rev A (2.8 mm holes from a mis-measurement of the skull) was silent.
//  - Everything is centered on the axis or repeated evenly around it so the dart
//    stays balanced and flies straight.
//  - The ball is a capsule with cone ends instead of a sphere so it prints
//    without supports; four thin gussets hold it from below.
//
// Print settings: same as Mk1 (100% infill, 6+ walls, no supports, brim).
// After landing, clear dirt from the nose inlet (a paper clip works).

/* [Global] */
max_width      = 38.5;   // hard project limit, checked below
body_d         = 38.5;
total_length   = 125.0;

/* [Nose] */
nose_length    = 30.0;
mouth_r        = 2.5;    // rounding where the nose curves into the inlet (no lip or edge)

/* [Body] */
bearing_length = 40.0;
flare_length   = 22.0;

/* [Tail] */
boom_d         = 16.0;
duct_length    = 22.0;
duct_wall      = 3.0;    // thick enough to survive glancing hits
fin_count      = 8;
fin_thickness  = 4.2;    // thicker for glancing hits
fin_root_fillet= 2.0;
fin_tip_angle  = 6.0;

/* [Whistle: inlet and jet] */
inlet_d        = 8.0;    // channel from the nose tip down to the blow hole (test D)
inlet_len      = 22.0;   // straight part of the channel below the rounded mouth (test D)
blow_d         = 6.0;    // blow hole (skull and test D: 6 mm)
blow_len       = 3.0;    // blow hole length (skull and test D: 3 mm)
jet_gap        = 5.4;    // blow hole exit to the top of the ball's hole edge (test D)

/* [Whistle: chamber and ball] */
wall           = 3.0;    // outer wall around the chamber (test D)
roof_angle     = 50.0;   // chamber roof, degrees from horizontal (>= 45)
ball_od        = 24.2;   // same ball as test D; the gap around it is whatever is left
ball_shell     = 1.2;    // as in the skull and test D
ball_hole_d    = 7.0;    // skull and test D
ball_cone_angle= 50.0;   // ball end cones, degrees from horizontal (>= 45)
ball_mid_h     = 18.0;   // straight middle section of the ball

/* [Whistle: supports and outlets] */
gusset_count   = 4;
gusset_t       = 2.4;    // thick enough to hold the ball through hard impacts
slot_count     = 8;      // outlet slots in the flare, one between each pair of fins
slot_w         = 2.6;
slot_h         = 10.0;   // straight part; plus a pointed top for support-free printing
slot_z         = 43.0;   // bottom of the slots

/* [Resolution] */
$fn            = 120;
profile_steps  = 60;

assert(body_d <= max_width, "body_d exceeds max_width");

// Derived Z stations (Z = 0 at the base)
R          = body_d / 2;
rb         = boom_d / 2;
z_nose     = total_length - nose_length;
z_bearing  = z_nose - bearing_length;
z_boom     = z_bearing - flare_length;
fin_top    = z_bearing;
fin_twist  = tan(fin_tip_angle) * fin_top / R * 180 / PI;

// Inlet: where the rounded mouth meets the straight channel, then the blow hole exit
z_mouth    = z_nose + nose_length * sqrt(1 - pow((inlet_d / 2 + mouth_r) / R, 2)) - mouth_r;
jet_z      = z_mouth - inlet_len - blow_len;

// Chamber and ball
r_ch       = R - wall;                                // chamber radius in the body
z_roof     = jet_z - (r_ch - blow_d / 2) * tan(roof_angle);  // where the roof cone starts
r_ball     = ball_od / 2;                             // ball outer radius
cone_h     = r_ball * tan(ball_cone_angle);
// ball top apex (virtual; the hole cuts it off), placed so the hole edge sits jet_gap below the blow hole
z_ball_top = jet_z - jet_gap + (ball_hole_d / 2) * tan(ball_cone_angle);
z_ball_up  = z_ball_top - cone_h;                     // top of the straight section
z_ball_lo  = z_ball_up - ball_mid_h;                  // bottom of the straight section
z_ball_bot = z_ball_lo - cone_h;                      // bottom apex

assert(z_boom > duct_length, "duct must end below the flare so air can enter it");
assert(z_ball_lo > z_bearing, "ball's straight section must sit in the full-width body");
assert(jet_z < z_nose + 10, "jet exit too far into the nose");
assert(r_ball + 3 <= r_ch, "ball leaves less than a 3 mm gap to the chamber wall");
assert(fin_count % slot_count == 0, "slot_count must divide fin_count so every slot sits between fins");
assert(fin_count % gusset_count == 0, "gusset_count must divide fin_count so gussets line up with fins");

function smooth(t) = (1 - cos(t * 180)) / 2;
function outer_r(z) =
    z <= z_boom    ? rb :
    z <= z_bearing ? rb + (R - rb) * smooth((z - z_boom) / flare_length) :
                     R;
function nose_r(h) = R * sqrt(max(0, 1 - pow(h / nose_length, 2)));
function chamber_r(z) = min(outer_r(z) - wall, r_ch);

// ---------- Outside (Mk1 shape, with a rounded inlet mouth at the nose) ----------

module outer_body() {
    pts = concat(
        [[0, 0]],
        [for (i = [0 : profile_steps]) let(z = z_bearing * i / profile_steps) [outer_r(z), z]],
        [[R, z_nose], [0, z_nose]]
    );
    rotate_extrude() polygon(pts);
    nose();
}

// Ellipsoidal nose with the inlet bored through it. Rounding the 2D profile
// (shrink then grow by mouth_r) turns the rim around the inlet into a smooth
// curve, so there is no thin lip or sharp edge at the tip.
module nose() {
    ri = inlet_d / 2;
    h_end = nose_length * sqrt(1 - pow(ri / R, 2));   // where the ellipse reaches the bore
    rotate_extrude()
        offset(r = mouth_r) offset(r = -mouth_r)
            polygon(concat(
                [[ri, z_nose - 10], [R, z_nose - 10]],   // overlaps the body; hidden there
                [for (i = [0 : profile_steps]) let(h = h_end * i / profile_steps)
                    [nose_r(h), z_nose + h]],
                [[ri, z_nose + h_end]]
            ));
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

// ---------- Inside: whistle ----------

// Chamber: follows the outer profile inward by `wall`, open at the base through
// the tail tube, cone roof up to the jet exit.
module chamber() {
    pts = concat(
        [[0, -1], [rb - wall, -1]],
        [for (i = [0 : profile_steps]) let(z = z_roof * i / profile_steps)
            [chamber_r(z), z]],
        [[blow_d / 2, jet_z], [0, jet_z]]
    );
    rotate_extrude() polygon(pts);
}

// Inlet channel from the nose tip, then the short blow hole into the chamber
module inlet() {
    translate([0, 0, jet_z - 1])
        cylinder(d = blow_d, h = blow_len + 1.01);
    translate([0, 0, jet_z + blow_len])
        cylinder(d = inlet_d, h = total_length - jet_z - blow_len + 1);
}

// Capsule with cone ends, given outer radius and apex-to-apex layout
module capsule(r, z_bot, z_lo, z_up, z_top) {
    rotate_extrude() polygon([
        [0, z_bot], [r, z_lo], [r, z_up], [0, z_top]
    ]);
}

module ball() {
    difference() {
        capsule(r_ball, z_ball_bot, z_ball_lo, z_ball_up, z_ball_top);
        ball_interior();
        translate([0, 0, z_ball_up]) cylinder(d = ball_hole_d, h = cone_h + 0.01);
    }
}

module ball_interior() {
    // shell thickness measured normal to the cones
    dz = ball_shell / cos(ball_cone_angle);
    capsule(r_ball - ball_shell, z_ball_bot + dz, z_ball_lo, z_ball_up, z_ball_top - dz);
}

// Gussets: thin radial plates under the ball, tied into the chamber wall.
// Their lower edge runs from the axis, just below the ball's bottom apex,
// down and outward at gusset_angle until it meets the chamber wall (the
// intersection with the chamber trims it there). So the ball's tip always
// starts on top of the gussets, and the gussets grow out of the wall without
// supports.
gusset_angle = 55;   // degrees from horizontal (>= 45)
gusset_lead  = 0.6;  // how far below the ball's apex the gussets meet the axis
module gussets() {
    z_axis = z_ball_bot - gusset_lead;
    reach  = r_ch + 1;                     // past the wall; trimmed to the chamber
    difference() {
        // line up with the fins at slot height, so each gusset sits between
        // two outlet slots instead of blocking one
        for (i = [0 : gusset_count - 1])
            rotate(fin_twist * (slot_z + slot_h / 2) / fin_top + i * 360 / gusset_count)
                rotate([90, 0, 0])
                    linear_extrude(height = gusset_t, center = true)
                        polygon([
                            [0, z_axis],
                            [reach, z_axis - reach * tan(gusset_angle)],
                            [reach, z_ball_lo],
                            [0, z_ball_lo]
                        ]);
        ball_interior();   // keep the inside of the ball clear
    }
}

// Outlet slots through the flare wall, centered between fins (fins twist, so
// the slot angle follows the fin twist at the slot height). Pointed tops
// print without supports.
module slots() {
    z_mid = slot_z + slot_h / 2;
    twist_here = fin_twist * z_mid / fin_top;
    // fins sit at multiples of 360/fin_count (plus twist); go halfway between
    for (i = [0 : slot_count - 1])
        rotate(twist_here + 180 / fin_count + i * 360 / slot_count)
            rotate([90, 0, 90])
                translate([0, 0, rb - 1])
                    linear_extrude(height = R + 2)
                        polygon([
                            [-slot_w / 2, slot_z],
                            [ slot_w / 2, slot_z],
                            [ slot_w / 2, slot_z + slot_h],
                            [0, slot_z + slot_h + slot_w * 0.6],
                            [-slot_w / 2, slot_z + slot_h]
                        ]);
}

module mk1w_dart() {
    union() {
        difference() {
            union() {
                outer_body();
                fins();
                duct();
            }
            chamber();
            inlet();
            slots();
        }
        intersection() {
            // keep the gussets inside the chamber; they fuse to its wall
            chamber();
            union() {
                ball();
                gussets();
            }
        }
    }
}

mk1w_dart();
