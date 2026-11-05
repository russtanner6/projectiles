// Socket fit gauge: six short tubes with plain round holes in 0.05 mm steps
// around the rod size. Print it (supports off, 100% infill, same filament and
// settings as the noses and tails), push your rod into each hole from the top
// (chamfered end), and pick the one that feels right: needs a firm push by hand
// or a light tap, and then won't pull off or wiggle. Its label is the grip bore
// to use; set grip_fit in flechette_dims.scad to (label - rod size).
// Build: openscad -D rod_d=8 ...   or   -D rod_d=12.7 ...

$fn = 96;
rod_d   = 8.0;
steps   = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25];   // hole = rod + step
tube_h  = 12.0;      // same as the tails' grip length
wall    = 2.0;
plate_t = 2.0;
lead_in = 0.6;
pitch   = rod_d + 2 * wall + 5;
label_depth = 0.6;

module tube(hole) {
    od = hole + 2 * wall;
    difference() {
        cylinder(h = tube_h, d = od);
        translate([0, 0, -1]) cylinder(h = tube_h + 2, d = hole);
        translate([0, 0, tube_h - lead_in]) cylinder(h = lead_in + 0.01, d1 = hole, d2 = hole + 2 * lead_in);
    }
}

difference() {
    union() {
        translate([-pitch / 2, -(rod_d / 2 + wall + 9), 0])
            cube([pitch * len(steps), rod_d + 2 * wall + 9 + 2, plate_t]);
        for (i = [0 : len(steps) - 1]) translate([i * pitch, 0, 0]) tube(rod_d + steps[i]);
    }
    for (i = [0 : len(steps) - 1]) translate([i * pitch, 0, 0]) {
        translate([0, 0, -1]) cylinder(h = plate_t + 2, d = rod_d + steps[i]);
        translate([0, -(rod_d / 2 + wall + 4.5), plate_t - label_depth])
            linear_extrude(label_depth + 0.01)
                text(str(rod_d + steps[i]), size = 3.2, halign = "center", valign = "center",
                     font = "Liberation Sans:style=Bold");
    }
}
