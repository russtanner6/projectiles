// Slug version (39.6 x 39.6 mm cylinder): generated from chain_shot_ball.scad, edit that file.
// Chain-shot ball: one of two identical solid PCTG balls joined by steel
// cable (recommended) or chain. Fired one behind the other with the cable
// folded between them; in flight they spread and spin around each other.
//
// Shape: as round as a one-piece, support-free print allows. A 39.6 mm sphere
// whose only non-round spot is a small flat on the bottom (with a short 47 deg
// cone), where the cable leaves. Optional sea-mine horns (set horns = true).
//
// Cable/chain anchor: a thick snap-in cross pin with a channel around it.
//   - Pin first: push it in through the side hole marked by the wide
//     counterbore (the "head" side) until its split end snaps into the pocket
//     on the far side. It takes a firm push.
//   - Then the cable: push one end up the channel from the bottom flat on one
//     side of the pin. The peaked ceiling steers it over the top of the pin
//     and back down the other side and out the bottom. Pull it through and
//     crimp a loop (or join the two ends) outside the ball.
//   - Locked both ways: the head stops the pin going further in; two hooks on
//     the split end catch a square ledge so it can't back out.
//   - To remove: squeeze the two hooks together through the wide far-side
//     opening (pliers or fingertips) and push the pin back out the head side.
//   - The cable's pull presses the pin down onto solid plastic (compression).
// Pin and hole have a "house" profile (flat floor, straight sides, 50 deg
// roof): the hole prints with no support, the pin prints lying on its floor,
// and it can't spin.
//
// Cable: 1/8 in. 7x19 galvanized or stainless wire rope (about 1,700-2,000 lb
// breaking strength), stronger than the printed pin, so the cable is not the
// weak link. The channel leaves 4 mm around the pin for it (1/16 or 3/32 in.
// cable also fits). Chain: a link wire up to ~3.5 mm thick fits the channel,
// but a chain can't be threaded around an installed pin: open the end link or
// use a quick link through the channel instead.
//
// Print: ball flat side down, 100% infill. Pin flat side down, 100% infill,
// 5+ walls. Supports off.

$fn = 160;

part        = "ball";   // "ball", "pin", or "both"
shape       = "slug";   // "ball" (round) or "slug" (39.6 x 39.6 mm cylinder: no overhangs, ~70% heavier)
slug_round  = 2.0;      // slug: rounded top edge
horns       = false;    // true = sea-mine version with thick horns on the upper half
horn_n      = 5;
horn_elev   = 55;       // ring horns point this far above level (>= 45 to print unsupported)
horn_d      = 8.0;
horn_out    = 7.5;      // ring horns stick out this far (kept inside the 39.6 mm width)
top_horn    = 9.0;

max_width   = 39.6;
ball_d      = 39.6;     // Russ: 39.6 for everything (barrel ~40.1 mm)
cone_a      = 47;       // underside slope from horizontal
// cable channel: up from the bottom flat, with room for the cable to run up
// one side of the installed pin, over its peaked top and down the other side
cable_gap   = 4.0;      // room for the cable each side of / above the pin (1/8 in. cable = 3.2 mm)
chan_t      = 7.0;      // channel thickness (along the pin)
release_w   = 16.0;     // width of the far-side opening where you pinch the hooks (pliers room)

// snap pin
pin_w       = 7.0;      // pin width (thick)
pin_side    = 4.0;      // height of the pin's straight sides (roof adds pin_w/2*tan(50))
head_w      = 10.5;     // head at the entry end
head_len    = 4.0;      // head length (sits in the entry counterbore)
barb        = 1.0;      // how far each hook sticks out (snap engagement)
prong_len   = 13.0;     // springy prong length (longer = easier flex, less strain)
slot_w      = 2 * barb + 0.4;   // gap between the prongs so they can close fully
clr         = 0.2;      // pin-to-hole clearance

assert(ball_d <= max_width, "ball_d exceeds max_width");
R  = ball_d / 2;
zc = R;
zt = zc - R * cos(cone_a);
rt = R * sin(cone_a);
rb = rt - zt / tan(cone_a);
T50 = tan(50);

// x positions along the pin axis (ball centre = 0); head on -X, prongs on +X
chan_w    = pin_w + 2 * clr + 2 * cable_gap;   // channel width across the pin (15.4 mm)
x_head_in = -R + head_len + 1.5;        // inner face of the head = counterbore shoulder
x_ledge   = R - 6.0;                    // square ledge the hooks catch on
x_tip     = sqrt(R * R - pow(pin_w / 2 + barb, 2)) - 0.3;   // pin end, inside the ball surface
floor_z   = -pin_side / 2;              // pin floor, relative to the ball centre

module house(w, h, fl = floor_z) {      // flat floor, straight sides, 50 deg peaked roof
    polygon([[-w / 2, fl], [w / 2, fl], [w / 2, fl + h], [0, fl + h + w / 2 * T50], [-w / 2, fl + h]]);
}
module along_x(x0, x1) {                // extrude a profile (y, z) along X from x0 to x1
    translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(height = x1 - x0) children();
}

module ball_shape() {
    if (shape == "slug") {
        // straight walls and a flat top: nothing overhangs, so it prints clean
        rotate_extrude() hull() {
            square([R, 0.01]);
            square([0.01, ball_d]);
            translate([R - slug_round, ball_d - slug_round]) circle(r = slug_round, $fn = 48);
            translate([R - 0.01, 0]) square([0.01, ball_d - slug_round]);
        }
    } else intersection() {
        translate([0, 0, zc]) sphere(r = R);
        translate([0, 0, zt]) cylinder(h = 2 * R, r = R + 1);
    }
    if (shape != "slug") cylinder(h = zt + 0.6, r1 = rb, r2 = rb + (zt + 0.6) / tan(cone_a));
}

module horn(len) {
    translate([0, 0, R - 2]) {
        cylinder(h = 3.5, d1 = horn_d + 5, d2 = horn_d);
        cylinder(h = len + 2 - horn_d / 2, d = horn_d);
        translate([0, 0, len + 2 - horn_d / 2]) sphere(d = horn_d);
    }
}
module horns_all() {
    translate([0, 0, zc]) {
        // ring rotated so no horn sits over the pin's side openings (+/-X)
        for (i = [0 : horn_n - 1])
            rotate([0, 0, 360 * i / horn_n + 90]) rotate([0, 90 - horn_elev, 0]) horn(horn_out);
        horn(top_horn);
    }
}

module ball() {
    roof_top = floor_z + pin_side + pin_w / 2 * T50;
    difference() {
        union() { ball_shape(); if (horns) horns_all(); }
        // cable channel: the pin's own house shape grown by cable_gap all
        // round, so the ceiling runs parallel to the pin's 50 deg roof and
        // steers a cable pushed up one side over the top and down the other.
        // Open at the bottom flat; walls vertical, ceiling 50 deg (no supports).
        translate([0, 0, zc]) {
            pin_peak = floor_z - clr + pin_side + 2 * clr + (pin_w / 2 + clr) * T50;
            ch_peak  = pin_peak + cable_gap / cos(50);
            ch_side  = ch_peak - chan_w / 2 * T50;
            translate([-chan_t / 2, 0, 0]) rotate([90, 0, 90]) linear_extrude(height = chan_t)
                polygon([[-chan_w / 2, -zc - 1], [chan_w / 2, -zc - 1], [chan_w / 2, ch_side],
                         [0, ch_peak], [-chan_w / 2, ch_side]]);
        }
        translate([0, 0, zc]) {
            // pin hole through the middle
            along_x(x_head_in - 0.01, x_ledge + 0.01) house(pin_w + 2 * clr, pin_side + 2 * clr, floor_z - clr);
            // entry opening for the head: as wide as the release opening on the
            // far side, so the ball stays balanced (the pin body centres the head)
            along_x(-R - 2, x_head_in) house(release_w, pin_side + 2 * clr, floor_z - clr);
            // exit pocket the hooks spring into, open to the surface and wide
            // enough to get pliers (or fingertips) on both hooks
            along_x(x_ledge, R + 2) house(release_w, pin_side + 2 * clr, floor_z - clr);
        }
    }
}

module pin_raw() {
    difference() {
        union() {
            along_x(x_head_in - 0.15, x_tip) house(pin_w, pin_side);            // body
            along_x(-R, x_head_in - 0.15) house(head_w, pin_side);             // head (0.15 short of its shoulder)
            // hooks: square catch face just past the ledge, then a lead-in taper to the tip
            for (s = [-1, 1]) mirror([0, s < 0 ? 1 : 0, 0])
                translate([0, 0, floor_z]) linear_extrude(height = pin_side)
                    polygon([[x_ledge + 0.25, pin_w / 2 - 0.01], [x_ledge + 0.25, pin_w / 2 + barb],
                             [x_ledge + 1.6, pin_w / 2 + barb], [x_tip, pin_w / 2 + 0.05], [x_tip, pin_w / 2 - 0.01]]);
        }
        // split the end into two springy prongs
        translate([x_tip - prong_len, -slot_w / 2, floor_z - 1]) cube([prong_len + 1, slot_w, 30]);
    }
}
module pin() {
    // ends trimmed flush to the outside: a sphere for the ball, a cylinder for the slug
    intersection() {
        pin_raw();
        if (shape == "slug") translate([0, 0, -R]) cylinder(h = ball_d, r = R - 0.15); else sphere(r = R - 0.15);
    }
}

if (part == "ball") ball();
else if (part == "pin") translate([0, 0, -floor_z]) pin();
else if (part == "pinplaced") translate([0, 0, zc]) pin();
else { ball(); translate([0, 32, -floor_z]) pin(); }
