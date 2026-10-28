// Whistle test pieces: find a death-whistle core that screams before
// building it into a dart. Blow into the hole on top; air leaves through the
// open bottom (between the ribs), like the skull whistle.
//
// These are test fixtures, not projectiles: piece A is wider than 38 mm on purpose.
//
//   A  Skull copy: the skull whistle's internals at full size (ellipsoid ball
//      32 mm, 7 mm ball hole with rim, 6 mm blow hole, 5.4 mm gap, 1.2 mm shell).
//      Baseline: if A is silent too, the skull's sound comes from something
//      these copies miss.
//   B  Dart size (fits inside Mk1's body), skull hole sizes, short blow hole,
//      cone-ended ball so it prints without supports.
//   C  Like B, but holes and gap scaled down 25% to match the smaller ball.
//   D  Like B, with a 22 mm long, 8 mm wide inlet channel above the blow hole,
//      the way the dart's nose would feed it.
//
// Print upright as modeled (blow hole on top), no supports, 100% infill.
// A's domes copy the skull's shape, so expect the same slight sag the skull had.

variant = "B";   // "A", "B", "C" or "D"

/* [Common] */
wall      = 3.0;     // outer wall
rib_count = 3;       // bottom ribs tying the ball's pedestal to the wall
rib_w     = 3.0;
rib_h     = 2.0;
shell     = 1.2;     // ball shell (skull: 1.2)
label_depth = 0.8;

/* [Skull copy (A)] */
skA_chamber_rx = 20.15;  // chamber inner radius
skA_chamber_rz = 24.2;   // chamber inner half-height
skA_ball_rx    = 16.2;   // ball outer radius
skA_ball_rz    = 17.7;   // ball outer half-height
skA_center_z   = 19.0;
skA_hole_d     = 7.0;    // ball hole
skA_rim_od     = 9.5;    // raised rim around the ball hole
skA_rim_top    = 37.8;
skA_blow_d     = 6.0;    // blow hole
skA_top_wall   = 3.0;

/* [Dart-size pieces (B, C, D)] */
body_d         = 37.6;
roof_angle     = 50;     // chamber roof, degrees from horizontal
ball_od        = 24.2;   // Mk1-W ball
ball_cone      = 50;     // ball end cones, degrees from horizontal
ball_mid_h     = 18.0;
pedestal_d     = 10.0;
hole_scale     = (variant == "C") ? 0.75 : 1.0;
blow_d         = 6.0 * hole_scale;
blow_len       = 3.0 * hole_scale;
ball_hole_d    = 7.0 * hole_scale;
jet_gap        = 5.4 * hole_scale;
inlet_len      = (variant == "D") ? 22.0 : 0;   // channel above the blow hole
inlet_d        = 8.0;

$fn = 96;

function ell_r(rx, rz, dz) = rx * sqrt(max(0, 1 - pow(dz / rz, 2)));

module label(z_top, r) {
    // engraved letter on the top face, off to the side of the blow hole
    translate([0, r, z_top - label_depth])
        linear_extrude(label_depth + 0.01)
            text(variant, size = 6, halign = "center", valign = "center",
                 font = "Liberation Sans:style=Bold");
}

module ribs(r_in, r_out) {
    intersection() {
        cylinder(r = r_out, h = rib_h);
        for (i = [0 : rib_count - 1])
            rotate(i * 360 / rib_count + 90)
                translate([r_in - 0.5, -rib_w / 2, 0]) cube([r_out - r_in + 1, rib_w, rib_h]);
    }
}

// ---------- A: skull copy ----------
module piece_A() {
    R = skA_chamber_rx + wall;
    top = skA_center_z + skA_chamber_rz + skA_top_wall;
    r_ped = ell_r(skA_ball_rx, skA_ball_rz, 6 - skA_center_z);
    difference() {
        union() {
            difference() {
                cylinder(r = R, h = top);
                translate([0, 0, skA_center_z])
                    scale([skA_chamber_rx, skA_chamber_rx, skA_chamber_rz]) sphere(1);
                translate([0, 0, -1]) cylinder(r = skA_chamber_rx, h = skA_center_z + 1);
            }
            // ball: ellipsoid shell on a pedestal, with a rim around its hole
            difference() {
                union() {
                    translate([0, 0, skA_center_z])
                        scale([skA_ball_rx, skA_ball_rx, skA_ball_rz]) sphere(1);
                    cylinder(r = r_ped, h = 6);
                    cylinder(d = skA_rim_od, h = skA_rim_top);
                }
                translate([0, 0, skA_center_z])
                    scale([skA_ball_rx - shell, skA_ball_rx - shell, skA_ball_rz - shell]) sphere(1);
            }
            ribs(r_ped, R);
        }
        translate([0, 0, skA_center_z])                          // ball hole (through rim)
            cylinder(d = skA_hole_d, h = skA_rim_top - skA_center_z + 1);
        translate([0, 0, skA_center_z])                          // keep ball interior clear
            scale([skA_ball_rx - shell, skA_ball_rx - shell, skA_ball_rz - shell]) sphere(1);
        translate([0, 0, skA_center_z + skA_chamber_rz - 1])     // blow hole
            cylinder(d = skA_blow_d, h = skA_top_wall + 2);
        label(top, R - 6);
    }
}

// ---------- B, C, D: dart-size pieces ----------
module capsule(r, z_bot, z_lo, z_up, z_top) {
    rotate_extrude() polygon([[0, z_bot], [r, z_lo], [r, z_up], [0, z_top]]);
}

module piece_dart() {
    R      = body_d / 2;
    r_ch   = R - wall;
    rb     = ball_od / 2;
    cone_h = rb * tan(ball_cone);
    // ball: cone bottom rising at ball_cone from the edge of a pedestal on the bed
    z_bot  = rib_h - (pedestal_d / 2) * tan(ball_cone);      // virtual apex (below the bed)
    z_lo   = rib_h + (rb - pedestal_d / 2) * tan(ball_cone);
    z_up   = z_lo + ball_mid_h;
    z_apex = z_up + cone_h;
    z_rim  = z_apex - (ball_hole_d / 2) * tan(ball_cone);   // top of the ball at the hole edge
    z_jet  = z_rim + jet_gap;                                 // blow hole exit
    z_roof = z_jet - (r_ch - blow_d / 2) * tan(roof_angle);  // roof cone starts here
    z_top  = z_jet + blow_len + inlet_len;
    dz     = shell / cos(ball_cone);
    intersection() {
    cylinder(r = R + 1, h = z_top + 1);   // trim anything below the bed
    difference() {
        union() {
            difference() {
                cylinder(r = R, h = z_top);
                // chamber: open bottom, cone roof up to the blow hole
                rotate_extrude() polygon([
                    [0, -1], [r_ch, -1], [r_ch, z_roof], [blow_d / 2, z_jet], [0, z_jet]
                ]);
            }
            difference() {
                union() {
                    capsule(rb, z_bot, z_lo, z_up, z_apex);
                    cylinder(d = pedestal_d, h = rib_h + 0.01);
                }
                // interior, with a flat floor above the pedestal
                intersection() {
                    capsule(rb - shell, z_bot + dz, z_lo, z_up, z_apex - dz);
                    translate([0, 0, rib_h + shell]) cylinder(r = rb, h = z_apex);
                }
            }
            ribs(pedestal_d / 2, R);
        }
        // ball hole and blow hole
        translate([0, 0, z_up]) cylinder(d = ball_hole_d, h = cone_h + 0.01);
        translate([0, 0, z_jet - 1]) cylinder(d = blow_d, h = blow_len + 2);
        if (inlet_len > 0)
            translate([0, 0, z_jet + blow_len]) cylinder(d = inlet_d, h = inlet_len + 1);
        label(z_top, R - 6);
    }
    }
}

if (variant == "A") piece_A(); else piece_dart();
