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
shape       = "ball";   // "ball" (round) or "slug" (39.6 x 39.6 mm cylinder: no overhangs, ~70% heavier)
slug_round  = 2.0;      // slug: rounded top edge
horns       = false;    // true = sea-mine version with thick horns on the upper half
faceted     = false;    // true = 8-sided body (octagon from above and from the side) and square horns (Russ:
                        // round shapes print jagged and stringy on his printer; flat faces print clean)
lead        = false;    // faceted only: two sealed side pockets for lead shot, filled during a print PAUSE (Russ)
lead_wall   = 3.0;      // plastic around the pockets
lead_pause  = 26.0;     // PAUSE here: pockets are open up to this height; their 50 deg roofs print after
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
barb        = 1.3;      // how far each hook sticks out (snap engagement; rev 3: was 1.0, Russ saw wear)
prong_len   = 13.0;     // springy prong length (longer = easier flex, less strain)
slot_w      = 2 * barb + 0.4;   // gap between the prongs so they can close fully
clr         = 0.2;      // pin-to-hole clearance
hook_flat   = 2.4;      // length of each hook's full-height catch (rev 3: was 1.6)
horn_r      = 1.0;      // faceted horns: long edges rounded, ends bevelled (fewer chips on rocks)
pin_round   = 2.0;      // pin's peak and roof corners rounded (Russ: sharp edges can cut Kevlar line)
// Faceted mine (flush, Russ): the pin goes in from ONE side only (-X). Its head fills a pocket
// its own size, flush with that flat face. The hooks snap into a hidden pocket inside the far
// side, so there's no hole there either. The pin is permanent; the cable still threads around it.
flush       = faceted;

assert(ball_d <= max_width, "ball_d exceeds max_width");
R  = ball_d / 2;
Rf = faceted ? R * cos(22.5) : R;      // distance to the flats on +/-X (pin ends stay inside)
zc = R;
zt = zc - R * cos(cone_a);
rt = R * sin(cone_a);
rb = rt - zt / tan(cone_a);
T50 = tan(50);

// x positions along the pin axis (ball centre = 0); head on -X, prongs on +X
chan_w    = pin_w + 2 * clr + 2 * cable_gap;   // channel width across the pin (15.4 mm)
x_head_in = flush ? -Rf + head_len : -Rf + head_len + 1.5;   // inner face of the head = counterbore shoulder
x_ledge   = flush ? Rf - 8.0 : Rf - 6.0;                    // square ledge the hooks catch on
x_tip     = flush ? Rf - 3.0 : faceted ? Rf - 0.3 : sqrt(R * R - pow(pin_w / 2 + barb, 2)) - 0.3;   // pin end, inside the ball surface
floor_z   = -pin_side / 2;              // pin floor, relative to the ball centre
pocket_w  = pin_w + 2 * barb + 0.8;     // hidden hook pocket (flush style): hooks spring out into it
x_pocket  = Rf - 2.6;                   // its far end: 2.6 mm of wall left under the flat face

module house(w, h, fl = floor_z) {      // flat floor, straight sides, 50 deg peaked roof
    polygon([[-w / 2, fl], [w / 2, fl], [w / 2, fl + h], [0, fl + h + w / 2 * T50], [-w / 2, fl + h]]);
}
module house_round(w, h) {             // the pin's profile: square floor corners, rounded roof and peak
    union() {
        offset(r = pin_round) offset(delta = -pin_round) house(w, h);
        translate([-w / 2, floor_z]) square([w, pin_round]);
    }
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
    } else if (faceted) {
        // side view: an octagon with a flat bottom (cable exit) and flat top; underside 50 deg
        fb = R * tan(22.5);                    // half the vertical band = octagon side / 2
        r_bot = R - (zc - fb) / tan(50);       // bottom flat radius
        rotate([0, 0, 22.5]) rotate_extrude($fn = 8)
            polygon([[0, 0], [r_bot, 0], [R, zc - fb], [R, zc + fb], [R - (R - fb), 2 * R], [0, 2 * R]]);
    } else intersection() {
        translate([0, 0, zc]) sphere(r = R);
        translate([0, 0, zt]) cylinder(h = 2 * R, r = R + 1);
    }
    if (shape != "slug" && !faceted) cylinder(h = zt + 0.6, r1 = rb, r2 = rb + (zt + 0.6) / tan(cone_a));
}

module rsq(w) { offset(r = horn_r, $fn = 24) square(w - 2 * horn_r, center = true); }   // square with rounded corners
module horn(len) {
    if (faceted) translate([0, 0, R - 4]) {
        // square horn: flared square base, straight square post, flat square end
        hull() { linear_extrude(0.01) rsq(horn_d + 5);
                 translate([0, 0, 5.5]) linear_extrude(0.01) rsq(horn_d); }
        linear_extrude(len + 3) rsq(horn_d);
        hull() { translate([0, 0, len + 3 - 0.01]) linear_extrude(0.01) rsq(horn_d);
                 translate([0, 0, len + 4 - 0.01]) linear_extrude(0.01) rsq(horn_d - 2); }   // 45 deg bevel at the end
    } else translate([0, 0, R - 2]) {
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
        if (!faceted) horn(top_horn);   // faceted mines: no top horn (Russ)
    }
}

// lead pockets: one each side of the pin/cable slab (+/-Y), symmetric so the CG stays centred.
// Each is one convex hull: a thin start low in the chamfer, full width through the band,
// open top at lead_pause, then a 50 deg roof that closes after the pause.
lp_y0 = (flush ? max(pin_w + 2 * cable_gap + 2 * clr, head_w + 2 * clr, pocket_w) : release_w) / 2 + 2.6;   // 2.6 mm past the cable channel / openings
// Pockets are unions of convex pieces, each with its own 50 deg roof (a union adds no new
// overhangs). Piece 1 spans the middle beside the cable channel; pieces 2 and 3 (flush style)
// reach further in toward the pin near each end, where the channel isn't.
lp_y1 = (flush ? max(head_w + 2 * clr, pocket_w) : release_w) / 2 + 2.6;   // past the head pocket / hook pocket
lp_x1 = chan_t / 2 + 2.6;                                                   // past the cable channel
module lead_sec(a, y0, xa, xb) {       // octagon of apothem a (flats on X and Y), part with y >= y0, xa <= x <= xb
    intersection() {
        rotate([0, 0, 22.5]) circle(r = a / cos(22.5), $fn = 8);
        translate([xa, y0]) square([xb - xa, 50]);
    }
}
module lead_piece(y0, xa, xb, d) {   // d: how far the 50 deg roof closes in (under the piece's inradius)
    a_band = R * cos(22.5) - lead_wall;            // inner flat distance in the straight band
    fb = R * tan(22.5);
    z_band = zc - fb;                              // bottom of the straight band
    hull() {
        // flat floor 1 mm above the top of the sloped underside (rev 4, Russ: a thin wall leaning out
        // over the pocket softened and curled while printing), so the overhanging part is solid
        translate([0, 0, z_band + 1.0]) linear_extrude(lead_pause - z_band - 1.0) lead_sec(a_band, y0, xa, xb);
        translate([0, 0, lead_pause + d * tan(50) - 0.01]) linear_extrude(0.01) offset(delta = -d) lead_sec(a_band, y0, xa, xb);
    }
}
module lead_pocket() {
    lead_piece(lp_y0, -50, 50, (R * cos(22.5) - lead_wall - lp_y0) / 2 - 0.05);
    if (flush) { lead_piece(lp_y1, lp_x1, 50, 2.0); lead_piece(lp_y1, -50, -lp_x1, 2.0); }
}

module ball() {
    roof_top = floor_z + pin_side + pin_w / 2 * T50;
    difference() {
        union() { ball_shape(); if (horns) horns_all(); }
        if (faceted && lead) for (s = [0, 1]) mirror([0, s, 0]) lead_pocket();
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
            if (flush) {
                // head pocket: exactly the head's size, so the head ends flush with the flat face
                along_x(-R - 2, x_head_in) house(head_w + 2 * clr, pin_side + 2 * clr, floor_z - clr);
                // hidden hook pocket inside the far side (no hole to the outside)
                along_x(x_ledge, x_pocket) house(pocket_w, pin_side + 2 * clr, floor_z - clr);
            } else {
            // entry opening for the head: as wide as the release opening on the
            // far side, so the ball stays balanced (the pin body centres the head)
            along_x(-R - 2, x_head_in) house(release_w, pin_side + 2 * clr, floor_z - clr);
            // exit pocket the hooks spring into, open to the surface and wide
            // enough to get pliers (or fingertips) on both hooks
            along_x(x_ledge, R + 2) house(release_w, pin_side + 2 * clr, floor_z - clr);
            }
        }
    }
}

module pin_raw() {
    difference() {
        union() {
            along_x(x_head_in - 0.15, x_tip) house_round(pin_w, pin_side);      // body (rounded roof: kind to the cable)
            along_x(flush ? -Rf + 0.1 : -R, x_head_in - 0.15) house(head_w, pin_side);   // head (0.15 short of its shoulder)
            // hooks: square catch face just past the ledge, then a lead-in taper to the tip
            for (s = [-1, 1]) mirror([0, s < 0 ? 1 : 0, 0])
                translate([0, 0, floor_z]) linear_extrude(height = pin_side)
                    polygon([[x_ledge + 0.25, pin_w / 2 - 0.01], [x_ledge + 0.25, pin_w / 2 + barb],
                             [x_ledge + hook_flat, pin_w / 2 + barb], [x_tip, pin_w / 2 + 0.05], [x_tip, pin_w / 2 - 0.01]]);
        }
        // split the end into two springy prongs
        translate([x_tip - prong_len, -slot_w / 2, floor_z - 1]) cube([prong_len + 1, slot_w, 30]);
    }
}
module pin() {
    // ends trimmed flush to the outside: a sphere for the ball, a cylinder for the slug
    intersection() {
        pin_raw();
        if (shape == "slug") translate([0, 0, -R]) cylinder(h = ball_d, r = R - 0.15);
        else if (faceted) translate([-Rf + 0.15, -R, -R]) cube([2 * Rf - 0.3, 2 * R, 2 * R]);
        else sphere(r = R - 0.15);
    }
}

if (part == "ball") ball();
else if (part == "pin") translate([0, 0, -floor_z]) pin();
else if (part == "pinplaced") translate([0, 0, zc]) pin();
else { ball(); translate([0, 32, -floor_z]) pin(); }
