// Wad: a cup that sits behind the dart so all the compressed air pushes on it.
//
// Shape: a solid pusher disc (front, against the dart) with a long skirt
// (rear, open toward the air chamber). Air pressure inside the cup presses
// the thin skirt lip against the barrel wall, sealing it. The long skirt
// keeps the wad square in the barrel so it can't cock or flip: it can only
// tilt by about (clearance / skirt length).
//
// Print: pusher face down on the bed, skirt pointing up. No supports.
// Settings: 100% infill (matches the other parts). Load it skirt-first toward the air chamber, flat face
// against the dart's tail.

$fn = 180;

// Rev 2 (Russ): sized to the barrel like the sabot (barrel ~40.1 mm inside), in
// the same three sizes as the sabot: 39.7, 39.0 and 38.6 mm (-D wad_d=...).
// Base 1 mm thicker and skirt longer, so it's stronger and can't cock or fold.
max_width   = 40.0;   // barrel-sized part (Russ approved), like the sabot bands
wad_d       = 39.0;   // outer diameter: 39.7 / 39.0 / 38.6
disc_t      = 6.0;    // pusher disc thickness (rev 2: was 5.0)
skirt_len   = 28.0;   // skirt length behind the disc (rev 2: was 22; ~0.7 x bore)
skirt_wall  = 1.8;    // skirt wall at the disc
lip_wall    = 0.9;    // thin feather edge at the open end, flares out under pressure to seal
taper_len   = 8.0;    // length over which the wall thins to the lip
edge_round  = 0.8;    // rounds the front outer edge so it loads easily

assert(wad_d <= max_width, "wad_d exceeds max_width");

R = wad_d / 2;

difference() {
    // outer body: front edge lightly chamfered, otherwise full diameter
    rotate_extrude()
        polygon([
            [0, 0],
            [R - edge_round, 0],
            [R, edge_round],
            [R, disc_t + skirt_len],
            [0, disc_t + skirt_len],
        ]);
    // cup: straight bore, then the wall thins toward the lip (bore widens upward,
    // so every inside face prints without support)
    rotate_extrude()
        polygon([
            [0, disc_t],
            [R - skirt_wall, disc_t],
            [R - skirt_wall, disc_t + skirt_len - taper_len],
            [R - lip_wall, disc_t + skirt_len + 0.01],
            [0, disc_t + skirt_len + 0.01],
        ]);
}
