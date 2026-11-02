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
BARB_X = -26.0
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
z_lip = z_leg_top + flare / K                       # lip = bottom edge of the slot exit
wh = SLOT_W / np.sin(np.radians(SLOPE))         # slot width measured horizontally
z_ch0 = z_lip + WALL / K
z_ch1 = z_ch0 + CH
z_roof = z_ch1 + CW / 2 / K
z_top = z_roof + TOP

# body: flares from the leg at 45 deg out to her outline, then straight up
zs = np.r_[np.arange(z_leg_top, z_lip, 0.25), z_lip, z_top]
Rb = [np.minimum(polar(0), LEG_D / 2 + K * (z - z_leg_top)) for z in zs]
part = loft(Rb, zs)
# slot: a 45 deg sheet, lower wall through the lip, reaching into the chamber
zs = np.arange(z_lip - 1.0, z_lip + (WALL + wh) / K + 0.3, 0.1)     # top rim ends inside the chamber
part -= shell([polar(K * (z - z_lip)) for z in zs], [polar(K * (z - z_lip) - wh) for z in zs], zs)
# ring chamber with a peaked 45 deg roof
zs = np.r_[z_ch0 - 0.001, z_ch1, np.linspace(z_ch1, z_roof - 0.05, 8)[1:]]
rin = [polar(WALL + CW) if z <= z_ch1 else polar(WALL + CW - K * (z - z_ch1)) for z in zs]
rout = [polar(WALL) if z <= z_ch1 else polar(WALL + K * (z - z_ch1)) for z in zs]
part -= shell(rin, rout, zs)

# leg and base
leg = mf.CrossSection.circle(LEG_D / 2, 96)
part += mf.Manifold.extrude(leg, LEG_H + 0.2).translate([0, 0, BASE_H - 0.1])
base = mf.CrossSection.hull(mf.CrossSection.circle(9, 96) + mf.CrossSection.circle(7, 96).translate([BARB_X, 0]))
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
barb = mf.Manifold.cylinder(2.0, 5.5, 5.5, 64).translate([BARB_X, 0, BZ])          # collar
barb += mf.Manifold.cylinder(12.0, 3.6, 3.6, 64).translate([BARB_X, 0, BZ + 1.9])     # shank
for i in range(3):   # ridge: 45 deg flare out (prints unsupported), then taper back to the shank
    z0 = BZ + 2.0 + 4.0 * i
    barb += mf.Manifold.cylinder(1.0, 3.6, 4.6, 64).translate([BARB_X, 0, z0])
    barb += mf.Manifold.cylinder(3.0, 4.6, 3.6, 64).translate([BARB_X, 0, z0 + 1.0])
part += barb
z_run = 4.0                                                    # channel height in the base (floor 1.5 mm, roof 1.75 mm)
holes = [cyl([BARB_X, 0, z_run - 1.5], [BARB_X, 0, BZ + 14.5], 4.2),          # barb bore
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
    z_end = z_ch0 + 1.4
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

m = part.to_mesh()
t = trimesh.Trimesh(m.vert_properties[:, :3], m.tri_verts)
t = max(t.split(only_watertight=False), key=lambda q: abs(q.volume))   # drop zero-area slivers
t.export(out_path)
print(f"slot {SLOT_W} mm: height {t.extents[2]:.1f} mm, lip at z {z_lip:.1f}, "
      f"riser top z {z_feed_top:.1f}, watertight {t.is_watertight}, parts {len(t.split(only_watertight=False))}, "
      f"volume {t.volume/1000:.1f} cm3")
