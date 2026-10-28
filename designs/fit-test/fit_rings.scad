// Barrel fit-test rings. Print all three, slide each into the barrel, and use the
// largest one that slides freely with no play as the dart's body_d.
// Each ring's diameter is engraved on top. Print flat (as modeled), same PCTG
// and settings as the darts, including elephant's-foot compensation, so the fit
// matches what a dart's tail ring and body will do.

sizes   = [38.2, 38.5, 38.8];   // outer diameters to test
height  = 6.0;
hole_d  = 22.0;                 // big center hole keeps them quick to print
spacing = 45;
label_depth = 0.6;

$fn = 180;

module ring(d) {
    difference() {
        cylinder(d = d, h = height);
        translate([0, 0, -1]) cylinder(d = hole_d, h = height + 2);
        translate([0, (d / 2 + hole_d / 2) / 2, height - label_depth])
            linear_extrude(label_depth + 0.01)
                text(str(d), size = 3.6, halign = "center", valign = "center",
                     font = "Liberation Sans:style=Bold");
    }
}

for (i = [0 : len(sizes) - 1])
    translate([i * spacing, 0, 0]) ring(sizes[i]);
