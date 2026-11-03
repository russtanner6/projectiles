// Chain-shot ball: one of two identical solid PCTG balls joined by a real
// (store-bought) chain. Fired one behind the other with the chain folded
// between them; in flight they spread apart and spin around each other.
//
// Shape: a 38 mm ball whose lower part is a 54 deg cone ending in a small
// flat, so it prints with no supports (a true sphere's underside would need
// them). Height stays 38 mm.
//
// Chain anchor (load path in compression, never pulling layers apart):
//   - a straight hole runs top to bottom on the axis
//   - the chain's end link goes up the hole from the flat bottom (chain side)
//   - a separate printed pin goes through that end link inside a round pocket
//     on top, resting in a cradle across the pocket floor
//   - when the chain pulls, the pin presses down on the solid ball: compression
//     through 30+ mm of plastic, the strongest way to load a print
// Print the pin lying flat (its layers then run along its length).
//
// Print the ball flat side down, no supports, 100% infill (solid).

$fn = 160;

part        = "ball";  // "ball", "pin", or "both"
max_width   = 38.0;
ball_d      = 38.0;
// chain fit: measure your chain's end link and adjust these
link_pass   = 8.0;     // hole the end link slides up (must clear the link's widest outside)
pin_d       = 5.5;     // pin through the end link (must fit inside the link's opening)
pin_len     = 17.0;
pocket_d    = 20.0;    // round pocket on top that holds the pin
pocket_depth= 8.0;
cradle_w    = pin_d + 0.4;

assert(ball_d <= max_width, "ball_d exceeds max_width");
R = ball_d / 2;
zc = R;                                      // ball centre height (bottom flat at z = 0)
cone_a = 54;                                 // underside cone slope from horizontal (>= 45, with margin)
zt = zc - R * cos(cone_a);                   // where the cone meets the ball tangentially
rt = R * sin(cone_a);
rb = rt - zt / tan(cone_a);                  // cone radius at the bed

module ball() {
    difference() {
        union() {
            intersection() {
                translate([0, 0, zc]) sphere(r = R);
                translate([0, 0, zt]) cylinder(h = 2 * R, r = R + 1);
            }
            cylinder(h = zt + 0.6, r1 = rb, r2 = rb + (zt + 0.6) / tan(cone_a));   // runs a hair past the tangent so no ledge shows
        }
        // straight hole for the chain, bottom to top
        translate([0, 0, -1]) cylinder(h = 2 * R + 2, d = link_pass);
        // round pocket on top; its walls are vertical and its floor faces up
        translate([0, 0, 2 * R - pocket_depth]) cylinder(h = pocket_depth + 1, d = pocket_d);
        // cradle for the pin across the pocket floor (half-round groove)
        translate([0, 0, 2 * R - pocket_depth]) rotate([0, 90, 0])
            cylinder(h = pocket_d - 1.0, d = cradle_w, center = true);   // stays inside the pocket
    }
}

module pin() {
    // printed lying flat: a round pin with a flat underside so it sits on the bed
    intersection() {
        rotate([0, 90, 0]) cylinder(h = pin_len, d = pin_d, center = true);
        translate([0, 0, pin_d / 2 - 0.4]) cube([pin_len + 1, pin_d + 1, pin_d], center = true);
    }
}

if (part == "ball") ball();
else if (part == "pin") translate([0, 0, pin_d / 2 - 0.4]) pin();
else { ball(); translate([0, 30, pin_d / 2 - 0.4]) pin(); }
