// Chain-shot ball: one of two identical solid PCTG balls joined by a metal
// chain or steel cable. Fired one behind the other with the chain folded
// between them; in flight they spread apart and spin around each other.
//
// As round as a one-piece, support-free print allows: a 38 mm sphere whose
// only non-round spot is a small flat on the bottom with a short cone (the
// steepest the printer can bridge without supports). The chain leaves
// through that flat.
//
// Chain anchor (loads the ball in compression, never pulling layers apart):
//   - a hole runs up from the bottom flat to the middle of the ball
//   - a cross-hole runs straight through the middle, side to side
//   - push the chain's end link up the hole, slide the printed cross pin in
//     through the side hole and through the link; the pin's ends are shaped
//     to the ball, so they sit flush
//   - when the chain pulls, the pin presses on the solid plastic below it
//   - for steel cable: same idea with a cable loop (thimble/ferrule) on the pin
//
// The cross-hole and pin have a "house" profile (flat floor, straight sides,
// peaked 50 deg roof): the hole prints with no support, the pin prints lying
// on its flat side, and the chain's pull lands on the flat floor.
// Print: ball flat side down, 100% infill. Pin lying on its flat side.

$fn = 160;

part        = "ball";   // "ball", "pin", or "both"
horns       = false;    // true = sea-mine version with thick horns on the upper half
horn_n      = 5;        // horns in the ring
horn_elev   = 55;       // ring horns point this far above level (>= 45 so they print unsupported)
horn_d      = 8.0;      // thick, so they don't snap off
horn_out    = 7.5;      // how far a ring horn sticks out past the ball (kept inside 38 mm width)
top_horn    = 9.0;      // length of the horn on top (along the barrel, so not width-limited)
max_width   = 38.0;
ball_d      = 38.0;
cone_a      = 47;       // underside slope from horizontal: just over the 45 deg limit
// chain fit: measure your chain's end link and adjust
link_pass   = 8.0;      // hole the end link slides up (clears the link's outside)
pin_w       = 5.0;      // cross pin width (must fit inside the link's opening)
pin_h       = 3.0;      // height of the pin's straight sides
clr         = 0.25;     // pin-to-hole clearance

assert(ball_d <= max_width, "ball_d exceeds max_width");
R  = ball_d / 2;
zc = R;
zt = zc - R * cos(cone_a);              // where the cone meets the sphere
rt = R * sin(cone_a);
rb = rt - zt / tan(cone_a);             // flat radius at the bed

module house2d(w, h, grow = 0) {         // flat floor, straight sides, 50 deg peaked roof
    x = w / 2 + grow; y0 = -h / 2 - grow; y1 = h / 2;
    polygon([[-x, y0], [x, y0], [x, y1], [0, y1 + x * tan(50)], [-x, y1]]);
}

module ball_shape() {
    intersection() {
        translate([0, 0, zc]) sphere(r = R);
        translate([0, 0, zt]) cylinder(h = 2 * R, r = R + 1);
    }
    cylinder(h = zt + 0.6, r1 = rb, r2 = rb + (zt + 0.6) / tan(cone_a));
}

module horn(len) {
    // thick horn: flared root blended into the ball, straight body, domed tip
    translate([0, 0, R - 2]) {
        cylinder(h = 3.5, d1 = horn_d + 5, d2 = horn_d);           // root fillet
        cylinder(h = len + 2 - horn_d / 2, d = horn_d);
        translate([0, 0, len + 2 - horn_d / 2]) sphere(d = horn_d);
    }
}

module horns_all() {
    translate([0, 0, zc]) {
        for (i = [0 : horn_n - 1])
            rotate([0, 0, 360 * i / horn_n + 90]) rotate([0, 90 - horn_elev, 0]) horn(horn_out);
        horn(top_horn);
    }
}

module ball() {
    difference() {
        union() { ball_shape(); if (horns) horns_all(); }
        // chain hole: bottom flat up to just above the middle, pointed top
        translate([0, 0, -1]) cylinder(h = zc + 1 + 2.5, d = link_pass);
        translate([0, 0, zc + 2.5]) cylinder(h = link_pass / 2 * 1.4, d1 = link_pass, d2 = 0.01);   // pointed top, 54 deg
        // cross-hole through the middle, side to side (along X), house section
        translate([0, 0, zc]) rotate([90, 0, 90])
            linear_extrude(height = ball_d + 2, center = true) house2d(pin_w, pin_h, clr);
    }
}

module pin() {
    // house-section bar, ends trimmed to the ball's curve so they sit flush;
    // lies on its flat floor to print
    intersection() {
        rotate([90, 0, 90]) linear_extrude(height = ball_d, center = true) house2d(pin_w, pin_h);
        sphere(r = R - 0.1);
    }
}

if (part == "ball") ball();
else if (part == "pin") translate([0, 0, pin_h / 2]) pin();
else { ball(); translate([0, 30, pin_h / 2]) pin(); }
