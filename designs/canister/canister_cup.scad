// Canister cup (Russ): one-piece, solid-walled shot cup, like a shotgun wad cup.
// Russ found the 3-petal canister looked flimsy; this is the one-piece version.
//
// How it works: fill it from the open front with shot, push the thin lid in on
// top of the shot. Firing presses the shot back against the solid base, so it
// can't leak. Out of the barrel, air slows the light cup (~40 g) while the heavy
// shot keeps going: the shot pushes the loose lid out and leaves the cup within
// the first few feet, then spreads as it flies. The empty cup trails behind.
//
// Payload: any shot or small balls. Steel 3/8 in. balls, lead buckshot or
// birdshot. Full to the lid is ~40 cm^3 of space: ~160 g of steel balls, but
// ~280 g of lead (too heavy; fill lead about 2/3 full, ~180 g, then the lid).
//
// Parts: cup (part = "cup", prints base down) and lid (part = "lid", prints flat).
// Supports off, 100% infill. Every downward face is 50 deg or steeper.

$fn = 160;
part     = "cup";       // "cup", "lid", "loaded" (preview cutaway)
D        = 39.6;        // Russ: 39.6 for everything (barrel ~40.1 mm)
wall     = 3.0;
base_t   = 6.0;         // solid base the wad pushes on
cav_h    = 48.0;        // cavity depth (open front)
lip_r    = wall / 2;    // fully rounded front edge (no thin lip to chip)
lid_t    = 1.6;
lid_clr  = 0.15;        // lid slides in snugly but pops out easily
bot_ch   = 0.6;         // small chamfer on the outer bottom edge (no elephant-foot flare)

R  = D / 2; ri = R - wall;
H  = base_t + cav_h;
echo(str("canister cup: height ", H, " mm, cavity ", 2 * ri, " x ", cav_h, " mm = ",
         round(PI * ri * ri * cav_h / 100) / 10, " cm^3"));

module cup() {
    rotate_extrude() polygon(concat(
        [[0, 0], [R - bot_ch, 0], [R, bot_ch]],
        [for (a = [0 : 10 : 180]) [R - lip_r + lip_r * cos(a), H - lip_r + lip_r * sin(a)]],
        [[ri, H - lip_r], [ri, base_t], [0, base_t]]));
}

module lid() {
    // thin solid disc with chamfered edges (no hole: birdshot would leak through)
    rl = ri - lid_clr;
    rotate_extrude() polygon([[0, 0], [rl - 0.5, 0], [rl, 0.5], [rl, lid_t - 0.5], [rl - 0.5, lid_t], [0, lid_t]]);
}

if (part == "cup") cup();
else if (part == "lid") lid();
else difference() {
    union() {
        cup();
        translate([0, 0, base_t + 30]) lid();
        color("silver") for (L = [0 : 3]) for (a = [0 : 45 : 315]) rotate([0, 0, a + (L % 2) * 22.5])
            translate([ri - 5.1, 0, base_t + 4.8 + L * 7.8]) sphere(d = 9.525, $fn = 24);
    }
    translate([-50, -100, -1]) cube([100, 100, 100]);
}
