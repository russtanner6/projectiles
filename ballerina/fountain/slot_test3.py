#!/usr/bin/env python3
"""Water-sheet test piece: one leg, her real hip outline, ring chamber and slot.

Prints upright with no supports. Water path:
  8 mm hose barb (points up, beside the leg) -> channel through the base ->
  5 mm channel up the leg -> central riser in the hip -> 8 feed holes rising
  at 55 deg -> ring chamber just inside her hip outline (peaked roof) ->
  continuous slot sloping 45 deg down and out -> sheet of water leaves a sharp
  lip at her widest point. Under the lip the body tucks in at 45 deg so the
  sheet can't cling to it.

Geometry is built in thin horizontal layers from 2D offsets of the outline,
so the slot keeps the same width all the way round the oval.

Usage: slot_test.py hip_outline.npy out.stl SLOT_W   (slot width in mm, measured across the slot)
"""
import sys

import manifold3d as mf
import numpy as np
import trimesh

outline_path, out_path, SLOT_W = sys.argv[1], sys.argv[2], float(sys.argv[3])

BASE_H = 10.0            # base plate height (holds the channel from the barb to the leg)
LEG_D, LEG_H = 12.0, 14.0
CH_D = 5.0               # leg channel
WALL = 2.4               # outer wall between her skin and the ring chamber
CW, CH = 3.0, 4.0        # ring chamber width and wall height (plus a peaked roof)
TOP = 6.0                # solid hip above the chamber roof
FEED_D, FEED_N, FEED_ANG = 2.6, 8, 55.0
BARB_X = -36.0           # barb far enough out that the hose clears the hips and the falling sheet
# hose barb for 1/2" ID (12.7 mm) vinyl tubing
B_SHANK_R, B_RIDGE_R, B_BORE_D = 6.1, 6.9, 8.0
SLOPE = 50.0             # deg from horizontal for every sloped inside surface (margin over 45)
K = 1 / np.tan(np.radians(SLOPE))   # inward move per mm of height
RT = mf.JoinType.Round

from shapely.geometry import Polygon, LineString
NA = 360
ANG = np.linspace(0, 2 * np.pi, NA, endpoint=False)
HIP = Polygon(np.load(outline_path))
_cache = {}


def polar(d):
    """radius of her outline offset inward by d (outward if d < 0), at each angle."""
    key = round(d, 4)
    if key not in _cache:
        g = HIP.buffer(-d, quad_segs=32) if d else HIP
        r = []
        for t_ in ANG:
            hit = LineString([(0, 0), (80 * np.cos(t_), 80 * np.sin(t_))]).intersection(g.exterior)
            pts = np.array([hit.coords[0]] if hit.geom_type == "Point" else [q.coords[0] for q in hit.geoms])
            r.append(np.linalg.norm(pts, axis=1).max())
        _cache[key] = np.array(r)
    return _cache[key]


def loft(R, zs):
    """closed solid from radius rows R[i] (one per height zs[i]) around the axis."""
    nz = len(zs)
    V = np.concatenate([np.c_[R[i] * np.cos(ANG), R[i] * np.sin(ANG), np.full(NA, zs[i])] for i in range(nz)])
    F = []
    for i in range(nz - 1):
        a_ = i * NA + np.arange(NA); b_ = i * NA + (np.arange(NA) + 1) % NA
        F += np.c_[a_, b_, b_ + NA].tolist() + np.c_[a_, b_ + NA, a_ + NA].tolist()
    V = np.vstack([V, [0, 0, zs[0]], [0, 0, zs[-1]]])
    c0, c1 = len(V) - 2, len(V) - 1
    j = np.arange(NA); jn = (j + 1) % NA
    F += np.c_[np.full(NA, c0), jn, j].tolist() + np.c_[np.full(NA, c1), (nz - 1) * NA + j, (nz - 1) * NA + jn].tolist()
    t = trimesh.Trimesh(V, np.array(F), process=False)
    if t.volume < 0:
        t.invert()
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))


def shell(Rin, Rout, zs):
    """solid between two radius surfaces (a ring-shaped sheet), as outer loft minus inner loft."""
    return loft(Rout, zs) - loft(Rin, zs)


z_leg_top = BASE_H + LEG_H
flare = polar(0).max() - LEG_D / 2
LIP_BAND = 0.6                                  # short vertical face under the lip
z_lip = z_leg_top + flare / K + LIP_BAND        # lip = bottom edge of the slot exit
wh = SLOT_W / np.sin(np.radians(SLOPE))         # slot width measured horizontally
TD = 3.0                                        # trough depth below the slot's inner end
z_ch0 = z_lip + WALL / K                        # slot's lower wall meets the trough's outer wall
z_tf = z_ch0 - TD                               # trough floor
z_seat = z_lip + (WALL + CW + wh) / K           # flat seat: upper half rests on the lower core here
z_top = z_seat + TOP
FAR = -25.0                                     # an offset far outside her outline

# whole block (both halves together): flare from the leg, vertical band, then her outline
zs = np.r_[np.arange(z_leg_top, z_lip - LIP_BAND, 0.25), z_lip - LIP_BAND, z_top]
B = loft([np.minimum(polar(0), LEG_D / 2 + K * (z - z_leg_top)) for z in zs], zs)


def shell_z(r_in_fn, r_out_fn, z0, z1, step=0.1):
    zs_ = np.r_[np.arange(z0, z1, step), z1]
    return shell([r_in_fn(z) for z in zs_], [r_out_fn(z) for z in zs_], zs_)


# U = everything above the lower half's top surface (upper half + water space)
U = shell_z(lambda z: polar(K * (z - z_lip)), lambda z: polar(FAR), z_lip - 2.0, z_ch0)        # over the slot's lower wall
U += shell_z(lambda z: polar(WALL + CW), lambda z: polar(WALL), z_tf, z_ch0 + 0.01)              # the trough
U += shell_z(lambda z: polar(WALL + CW), lambda z: polar(FAR), z_ch0, z_seat + 0.01, 0.5)        # above the trough
U += mf.Manifold.cube([200, 200, 100]).translate([-100, -100, z_seat])                           # above the seat
# water space = part of U below the upper half's underside (slot + chamber)
G = loft([polar(K * (z - z_lip) - wh) for z in np.r_[np.arange(z_lip - 2.0, z_seat, 0.1), z_seat]],
         np.r_[np.arange(z_lip - 2.0, z_seat, 0.1), z_seat])
G = G - mf.Manifold.cube([200, 200, 100]).translate([-100, -100, z_seat])

# snap post: 3 springy prongs on the lower core click into a groove inside a blind
# socket in the upper half. No hardware; pull firmly to separate for cleaning.
T50 = np.tan(np.radians(SLOPE))
P_R, P_RIN = 4.0, 2.4            # prong outer / inner radius
HOOK = 0.6                       # how far each hook sticks out
CLR = 0.15                       # radial clearance in the socket
POCKET_R, POCKET_D = 5.6, 4.0    # ring pocket round the post base, so the prongs are long enough to flex
P_H = 4.6                        # post height above the seat
PRONG_GAP = 1.4                  # gap between prongs
zs0 = z_seat - POCKET_D
post = mf.Manifold.cylinder(P_H + POCKET_D, P_R, P_R, 96).translate([0, 0, zs0])
# hook: flares out at 50 deg (prints unsupported), then a 45-50 deg lead-in up to the tip
zh0 = z_seat + 1.8
post += mf.Manifold.cylinder(HOOK * T50, P_R, P_R + HOOK, 96).translate([0, 0, zh0])
zh1 = zh0 + HOOK * T50
post += mf.Manifold.cylinder(0.5, P_R + HOOK, P_R + HOOK, 96).translate([0, 0, zh1])
zh2 = zh1 + 0.5
lead = z_seat + P_H - zh2
post += mf.Manifold.cylinder(lead, P_R + HOOK, P_R - 0.4, 96).translate([0, 0, zh2])
post = post ^ mf.Manifold.cylinder(P_H + POCKET_D, 30, 30, 8).translate([0, 0, zs0])   # trim to height
post -= mf.Manifold.cylinder(P_H + POCKET_D + 1, P_RIN, P_RIN, 64).translate([0, 0, zs0 + 1.0])  # hollow
for k in range(3):
    post -= mf.Manifold.cube([30, PRONG_GAP, P_H + POCKET_D]).translate([0, -PRONG_GAP / 2, zs0 + 1.2]).rotate([0, 0, 120 * k + 90])
pocket = mf.Manifold.cylinder(POCKET_D + 0.01, POCKET_R, POCKET_R, 96).translate([0, 0, zs0])
# socket in the upper half: bore + diamond groove (50 deg faces, prints either way up)
SOCK_D = P_H + 0.4
sock = mf.Manifold.cylinder(SOCK_D, P_R + CLR, P_R + CLR, 96).translate([0, 0, z_seat - 0.01])
g_r0, g_r1 = P_R + CLR, P_R + HOOK + CLR
gh = (g_r1 - g_r0) * T50
gz = zh0 - 0.1                                      # groove sits where the hook's flare is
sock += mf.Manifold.cylinder(gh, g_r0, g_r1, 96).translate([0, 0, gz])
sock += mf.Manifold.cylinder(0.5 + 0.2, g_r1, g_r1, 96).translate([0, 0, gz + gh])
sock += mf.Manifold.cylinder(gh, g_r1, g_r0, 96).translate([0, 0, gz + gh + 0.7])
lower = B - U - pocket + post
upper = (B ^ U) - G - sock
part = lower

# leg and base
leg = mf.CrossSection.circle(LEG_D / 2, 96)
part += mf.Manifold.extrude(leg, LEG_H + 0.2).translate([0, 0, BASE_H - 0.1])
base = mf.CrossSection.hull(mf.CrossSection.circle(9, 96) + mf.CrossSection.circle(B_SHANK_R + 3.0, 96).translate([BARB_X, 0]))
part += mf.Manifold.extrude(base, BASE_H)


def cyl(p0, p1, d, n=48):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = np.linalg.norm(p1 - p0)
    c = mf.Manifold.cylinder(L, d / 2, d / 2, n)
    T = trimesh.geometry.align_vectors([0, 0, 1], (p1 - p0) / L)
    T[:3, 3] = p0
    return c.transform(T[:3, :4])


def teardrop_x(x0, x1, z, d):
    """horizontal channel along x with a pointed 45 deg roof (prints without support)."""
    r = d / 2
    pts = [[r * np.cos(a), r * np.sin(a)] for a in np.linspace(-np.pi * 0.75, -np.pi * 0.25, 1)]
    prof = mf.CrossSection.hull(mf.CrossSection.circle(r, 48) + mf.CrossSection.circle(0.02, 8).translate([0, r * 1.7]))
    m = mf.Manifold.extrude(prof, x1 - x0)          # along z, profile in x-y
    return m.rotate([0, 90, 0]).rotate([90, 0, 0]).translate([x0, 0, z]) if False else \
        m.transform(np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, z]], float))


# barb: 8 mm hose, pointing up; ridges narrow upward so they print without support
BZ = BASE_H
barb = mf.Manifold.cylinder(2.0, B_SHANK_R + 2.0, B_SHANK_R + 2.0, 96).translate([BARB_X, 0, BZ])          # collar
barb += mf.Manifold.cylinder(15.5, B_SHANK_R, B_SHANK_R, 96).translate([BARB_X, 0, BZ + 1.9])        # shank
rh = B_RIDGE_R - B_SHANK_R
for i in range(3):   # ridge: 45 deg flare out (prints unsupported), then taper back to the shank
    z0 = BZ + 2.5 + 5.0 * i
    barb += mf.Manifold.cylinder(rh, B_SHANK_R, B_RIDGE_R, 96).translate([BARB_X, 0, z0])
    barb += mf.Manifold.cylinder(4.0, B_RIDGE_R, B_SHANK_R, 96).translate([BARB_X, 0, z0 + rh])
part += barb
z_run = 4.0                                                    # channel height in the base (floor 1.5 mm, roof 1.75 mm)
holes = [cyl([BARB_X, 0, z_run - 1.5], [BARB_X, 0, BZ + 18.0], B_BORE_D),          # barb bore
         teardrop_x(BARB_X, 0.0, z_run, CH_D)]
# leg channel up into the hip, opening into a small plenum the feed holes leave from;
# the plenum is wide enough that neighbouring feed holes don't touch at their start
PLEN_R, FEED_R0 = 4.2, 3.4
mid = HIP.buffer(-(WALL + CW / 2))
feeds, starts = [], []
for k in range(FEED_N):
    a = 2 * np.pi * (k + 0.5) / FEED_N
    ray = LineString([(0, 0), (60 * np.cos(a), 60 * np.sin(a))])
    hit = ray.intersection(mid.exterior)
    hit = np.array(hit.coords[0] if hit.geom_type == "Point" else hit.geoms[0].coords[0])
    rad = np.linalg.norm(hit)
    z_end = z_tf + 0.6
    z_start = z_end - (rad - FEED_R0) * np.tan(np.radians(FEED_ANG))
    u = np.array([np.cos(a), np.sin(a)])
    feeds.append(([*(u * FEED_R0), z_start], [*(u * (rad + 0.6)), z_end]))
    starts.append(z_start)
z_p0 = min(starts) - 1.0                                   # plenum floor
z_p1 = max(starts) + 1.5                                   # plenum wall top
cone_h = (PLEN_R - CH_D / 2) * np.tan(np.radians(SLOPE))
holes.append(cyl([0, 0, z_run], [0, 0, z_p0 - cone_h + 0.01], CH_D))
holes.append(mf.Manifold.cylinder(cone_h, CH_D / 2, PLEN_R, 64).translate([0, 0, z_p0 - cone_h]))   # widens at 50 deg
holes.append(mf.Manifold.cylinder(z_p1 - z_p0, PLEN_R, PLEN_R, 64).translate([0, 0, z_p0]))
holes.append(mf.Manifold.cylinder(PLEN_R * 1.3, PLEN_R, 0.01, 64).translate([0, 0, z_p1]))         # pointed roof
for p0, p1 in feeds:
    holes.append(cyl(p0, p1, FEED_D))
z_feed_top = z_p1 + PLEN_R * 1.3
part = part - mf.Manifold.batch_boolean(holes, mf.OpType.Add)



def export(g, path, flip=False):
    m = g.to_mesh()
    t = trimesh.Trimesh(m.vert_properties[:, :3], m.tri_verts)
    t = max(t.split(only_watertight=False), key=lambda q: abs(q.volume))   # drop zero-area slivers
    if flip:                                     # print the upper half upside down
        t.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    t.apply_translation([0, 0, -t.bounds[0][2]])
    t.export(path)
    return t


tl = export(part, out_path.replace(".stl", "_lower.stl"))
tu = export(upper, out_path.replace(".stl", "_upper.stl"), flip=True)
ta = export(part + upper, out_path.replace(".stl", "_assembled.stl"))
for name, t in (("lower", tl), ("upper (printed upside down)", tu)):
    print(f"slot {SLOT_W} mm {name}: {t.extents.round(1)} mm, watertight {t.is_watertight}, "
          f"parts {len(t.split(only_watertight=False))}, volume {t.volume/1000:.1f} cm3")
print(f"lip at z {z_lip:.1f}, trough floor {z_tf:.1f}, seat {z_seat:.1f}, top {z_top:.1f}; "
      f"snap post {P_H} mm tall, socket roof {TOP - SOCK_D:.1f} mm")
