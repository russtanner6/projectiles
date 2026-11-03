#!/usr/bin/env python3
"""Water-sheet test piece, rev 5: her waist outline, slot following the waistband V,
two snap-together halves, tall stem.

Changes from rev 4 (which dribbled):
  - slot 0.4 mm (was 0.8): twice the exit speed for the same flow, and enough
    pressure in the ring that water comes out all the way round, not just at
    the lowest point of the V
  - slot exits 15 deg below level (was 50 deg) so the sheet throws outward;
    the two-piece design prints both slot faces facing up, so any angle works
  - flat seat (the V is taken up by a taller ring chamber, not by tilting the
    seat), so the top half sits level and the gap is even
  - bigger ring chamber, 10 feed holes, 6 mm leg channel, 7 mm base channel
  - stem 4x taller, wide base plate

Usage: slot_test5.py outline.npy belt_edge.npy out.stl [GAP] [ANGLE]
"""
import sys

import manifold3d as mf
import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString

outline_path, belt_path, out_path = sys.argv[1:4]
GAP = float(sys.argv[4]) if len(sys.argv) > 4 else 0.4      # slot width across the slot
ALPHA = float(sys.argv[5]) if len(sys.argv) > 5 else 15.0    # exit angle below level

SLOPE = 50.0; K = 1 / np.tan(np.radians(SLOPE)); T50 = np.tan(np.radians(SLOPE))
BASE_H, BASE_R = 12.0, 32.0
LEG_D, LEG_H, CH_D = 13.0, 60.0, 6.0
DW = 3.0                 # slot length (lip wall thickness)
WC, DT = 4.0, 4.0        # ring chamber width, depth of trough below the lip
CH_MIN = 2.5             # chamber height above the slot at the highest point of the V
DCORE = DW + WC + 2.0
TOPT = 6.0
FEED_D, FEED_N, FEED_ANG = 3.0, 10, 55.0
BARB_X = -46.0
B_SHANK_R, B_RIDGE_R, B_BORE_D = 6.1, 6.9, 8.0
NA = 360
ANG = np.linspace(-np.pi, np.pi, NA, endpoint=False)
HIP = Polygon(np.load(outline_path))
belt = np.load(belt_path)
SH = np.interp(ANG, belt[:, 0], belt[:, 1] - belt[:, 1].min(), period=2 * np.pi)   # waistband rise per angle

_c = {}


def polar(d):
    k = round(d, 4)
    if k not in _c:
        g = HIP.buffer(-d, quad_segs=32) if d else HIP
        r = []
        for t in ANG:
            hit = LineString([(0, 0), (90 * np.cos(t), 90 * np.sin(t))]).intersection(g.exterior)
            pts = np.array([hit.coords[0]] if hit.geom_type == "Point" else [q.coords[0] for q in hit.geoms])
            r.append(np.linalg.norm(pts, axis=1).max())
        _c[k] = np.array(r)
    return _c[k]


def to_mf(t):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32),
                               tri_verts=np.asarray(t.faces, np.uint32)))


def closed(V, F):
    t = trimesh.Trimesh(V, np.array(F), process=False)
    if t.volume < 0:
        t.invert()
    g = to_mf(t)
    assert g.status() == mf.Error.NoError, g.status()
    return g


def loft2(R, Z):
    """solid from rings: R[i], Z[i] are per-angle radius and height of ring i."""
    n = len(R)
    V = np.concatenate([np.c_[R[i] * np.cos(ANG), R[i] * np.sin(ANG), Z[i]] for i in range(n)])
    F = []
    j = np.arange(NA); jn = (j + 1) % NA
    for i in range(n - 1):
        a, b = i * NA + j, i * NA + jn
        F += np.c_[a, b, b + NA].tolist() + np.c_[a, b + NA, a + NA].tolist()
    V = np.vstack([V, [0, 0, np.mean(Z[0])], [0, 0, np.mean(Z[-1])]])
    c0, c1 = len(V) - 2, len(V) - 1
    F += np.c_[np.full(NA, c0), jn, j].tolist() + np.c_[np.full(NA, c1), (n - 1) * NA + j, (n - 1) * NA + jn].tolist()
    return closed(V, F)


def sweep(profile):
    """closed (d, z) profile per angle, swept round: profile(j) -> list of (d, z)."""
    P = [profile(j) for j in range(NA)]
    m = len(P[0])
    V = np.zeros((NA, m, 3))
    for j in range(NA):
        for i, (d, z) in enumerate(P[j]):
            r = polar(d)[j]
            V[j, i] = [r * np.cos(ANG[j]), r * np.sin(ANG[j]), z]
    V = V.reshape(-1, 3)
    F = []
    for j in range(NA):
        jn = (j + 1) % NA
        for i in range(m):
            inx = (i + 1) % m
            a, b, c, d = j * m + i, j * m + inx, jn * m + inx, jn * m + i
            F += [[a, b, c], [a, c, d]]
    return closed(V, F)


ta = np.tan(np.radians(ALPHA))
gv = GAP / np.cos(np.radians(ALPHA))                  # vertical size of the gap
r0 = polar(0)
z_leg_top = BASE_H + LEG_H
LEG_R = LEG_D / 2
LB, UC = 7.0, 0.6                                    # straight band under the lip; undercut depth
UCH = UC * T50                                        # undercut height (50 deg chamfer)
Z_LIP0 = z_leg_top + (r0.max() - UC - LEG_R) / K + LB + UCH   # lowest lip (front of the V)
ZL = Z_LIP0 + SH                                      # lip height per angle
ZSEAT = ZL.max() + DW * ta + gv + CH_MIN
ZTOP = ZSEAT + TOPT

# body: leg, 50 deg flare out to her outline (minus the undercut), a straight band,
# then a 50 deg undercut chamfer out to the sharp lip, then straight up
rows_R, rows_Z = [], []
zb = ZL - UCH - LB                                     # where the flare meets the band
for f in np.linspace(0, 1, 40):
    z = z_leg_top + f * (zb - z_leg_top)
    rows_R.append(np.maximum(LEG_R, r0 - UC - K * (zb - z))); rows_Z.append(z)
rows_R += [r0 - UC, r0, r0]; rows_Z += [ZL - UCH, ZL, np.full(NA, ZTOP)]
B = loft2(rows_R, rows_Z)

core_r = polar(DCORE - 0.3)
def core_above(z0, z1):
    return loft2([core_r, core_r], [np.full(NA, z0), np.full(NA, z1)])

# everything above the lower half (upper half + water spaces)
AL = sweep(lambda j: [(-4, ZL[j]), (0, ZL[j]), (DW, ZL[j] + DW * ta), (DW, ZL[j] - DT),
                      (DW + WC, ZL[j] - DT), (DW + WC, ZSEAT), (DCORE, ZSEAT), (DCORE, ZTOP + 1), (-4, ZTOP + 1)])
AL += core_above(ZSEAT, ZTOP + 1)
# everything the upper half may occupy (above the slot's top face and above the seat)
AU = sweep(lambda j: [(-4, ZL[j] + gv), (0, ZL[j] + gv), (DW, ZL[j] + DW * ta + gv), (DW, ZSEAT),
                      (DCORE, ZSEAT), (DCORE, ZTOP + 1), (-4, ZTOP + 1)])
AU += core_above(ZSEAT, ZTOP + 1)

# snap post (lower) and blind socket with groove (upper), as rev 4
P_R, P_RIN, HOOK, CLR = 4.0, 2.4, 0.6, 0.15
POCKET_R, POCKET_D, P_H, PRONG_GAP = 5.6, 4.0, 4.6, 1.4
zs0 = ZSEAT - POCKET_D
post = mf.Manifold.cylinder(P_H + POCKET_D, P_R, P_R, 96).translate([0, 0, zs0])
zh0 = ZSEAT + 1.8
post += mf.Manifold.cylinder(HOOK * T50, P_R, P_R + HOOK, 96).translate([0, 0, zh0])
zh1 = zh0 + HOOK * T50
post += mf.Manifold.cylinder(0.5, P_R + HOOK, P_R + HOOK, 96).translate([0, 0, zh1])
zh2 = zh1 + 0.5
post += mf.Manifold.cylinder(ZSEAT + P_H - zh2, P_R + HOOK, P_R - 0.4, 96).translate([0, 0, zh2])
post = post ^ mf.Manifold.cylinder(P_H + POCKET_D, 30, 30, 8).translate([0, 0, zs0])
post -= mf.Manifold.cylinder(P_H + POCKET_D + 1, P_RIN, P_RIN, 64).translate([0, 0, zs0 + 1.0])
for k in range(3):
    post -= mf.Manifold.cube([30, PRONG_GAP, P_H + POCKET_D]).translate([0, -PRONG_GAP / 2, zs0 + 1.2]).rotate([0, 0, 120 * k + 90])
pocket = mf.Manifold.cylinder(POCKET_D + 0.01, POCKET_R, POCKET_R, 96).translate([0, 0, zs0])
sock = mf.Manifold.cylinder(P_H + 0.4, P_R + CLR, P_R + CLR, 96).translate([0, 0, ZSEAT - 0.01])
g_r0, g_r1 = P_R + CLR, P_R + HOOK + CLR
gh = (g_r1 - g_r0) * T50
gz = zh0 - 0.1
sock += mf.Manifold.cylinder(gh, g_r0, g_r1, 96).translate([0, 0, gz])
sock += mf.Manifold.cylinder(0.7, g_r1, g_r1, 96).translate([0, 0, gz + gh])
sock += mf.Manifold.cylinder(gh, g_r1, g_r0, 96).translate([0, 0, gz + gh + 0.7])

lower = B - AL - pocket + post
upper = (B ^ AU) - sock

# stem, base plate, barb
lower += mf.Manifold.cylinder(LEG_H + 0.4, LEG_R, LEG_R, 96).translate([0, 0, BASE_H - 0.2])
base = mf.CrossSection.hull(mf.CrossSection.circle(BASE_R, 128) + mf.CrossSection.circle(B_SHANK_R + 3.0, 96).translate([BARB_X, 0]))
lower += mf.Manifold.extrude(base, BASE_H)
BZ = BASE_H
barb = mf.Manifold.cylinder(2.0, B_SHANK_R + 2.0, B_SHANK_R + 2.0, 96).translate([BARB_X, 0, BZ])
barb += mf.Manifold.cylinder(15.5, B_SHANK_R, B_SHANK_R, 96).translate([BARB_X, 0, BZ + 1.9])
rh = B_RIDGE_R - B_SHANK_R
for i in range(3):
    z0 = BZ + 2.5 + 5.0 * i
    barb += mf.Manifold.cylinder(rh, B_SHANK_R, B_RIDGE_R, 96).translate([BARB_X, 0, z0])
    barb += mf.Manifold.cylinder(4.0, B_RIDGE_R, B_SHANK_R, 96).translate([BARB_X, 0, z0 + rh])
lower += barb


def cyl(p0, p1, d, n=48):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = np.linalg.norm(p1 - p0)
    c = mf.Manifold.cylinder(L, d / 2, d / 2, n)
    T = trimesh.geometry.align_vectors([0, 0, 1], (p1 - p0) / L)
    T[:3, 3] = p0
    return c.transform(T[:3, :4])


def teardrop_x(x0, x1, z, d):
    r = d / 2
    prof = mf.CrossSection.hull(mf.CrossSection.circle(r, 48) + mf.CrossSection.circle(0.02, 8).translate([0, r * 1.7]))
    m = mf.Manifold.extrude(prof, x1 - x0)
    return m.transform(np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, z]], float))


Z_RUN, BASE_CH = 4.5, 7.0
holes = [cyl([BARB_X, 0, Z_RUN - 2.0], [BARB_X, 0, BZ + 18.0], B_BORE_D),
         teardrop_x(BARB_X, 0.0, Z_RUN, BASE_CH)]
# leg channel -> plenum -> feed holes rising to the trough floor
PLEN_R, FEED_R0 = 6.2, 5.3
mid = HIP.buffer(-(DW + WC / 2))
feeds, starts = [], []
for k in range(FEED_N):
    a = 2 * np.pi * (k + 0.5) / FEED_N - np.pi
    hit = LineString([(0, 0), (90 * np.cos(a), 90 * np.sin(a))]).intersection(mid.exterior)
    hit = np.array(hit.coords[0] if hit.geom_type == "Point" else hit.geoms[0].coords[0])
    rad = np.linalg.norm(hit)
    zl = np.interp(a, ANG, ZL, period=2 * np.pi)
    z_end = zl - DT + 0.7
    z_start = z_end - (rad - FEED_R0) * np.tan(np.radians(FEED_ANG))
    u = np.array([np.cos(a), np.sin(a)])
    feeds.append(([*(u * FEED_R0), z_start], [*(u * (rad + 0.5)), z_end]))
    starts.append(z_start)
z_p0 = min(starts) - 1.2
z_p1 = max(starts) + 1.8
cone_h = (PLEN_R - CH_D / 2) * T50
holes.append(cyl([0, 0, Z_RUN], [0, 0, z_p0 - cone_h + 0.01], CH_D))
holes.append(mf.Manifold.cylinder(cone_h, CH_D / 2, PLEN_R, 64).translate([0, 0, z_p0 - cone_h]))
holes.append(mf.Manifold.cylinder(z_p1 - z_p0, PLEN_R, PLEN_R, 64).translate([0, 0, z_p0]))
roof_top = z_p1 + PLEN_R * 1.3
holes.append(mf.Manifold.cylinder(PLEN_R * 1.3, PLEN_R, 0.01, 64).translate([0, 0, z_p1]))
for p0, p1 in feeds:
    holes.append(cyl(p0, p1, FEED_D))
assert roof_top < zs0 - 1.0, f"plenum roof {roof_top:.1f} hits the snap pocket {zs0:.1f}"
lower = lower - mf.Manifold.batch_boolean(holes, mf.OpType.Add)


def export(g, path, flip=False):
    m = g.to_mesh()
    t = trimesh.Trimesh(m.vert_properties[:, :3], m.tri_verts)
    t = max(t.split(only_watertight=False), key=lambda q: abs(q.volume))
    if flip:
        t.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    t.apply_translation([0, 0, -t.bounds[0][2]])
    t.export(path)
    return t


tl = export(lower, out_path.replace(".stl", "_lower.stl"))
tu = export(upper, out_path.replace(".stl", "_upper.stl"), flip=True)
export(lower + upper, out_path.replace(".stl", "_assembled.stl"))
for name, t in (("lower", tl), ("upper (printed upside down)", tu)):
    print(f"{name}: {t.extents.round(1)} mm, watertight {t.is_watertight}, parts {len(t.split(only_watertight=False))}, {t.volume/1000:.1f} cm3")
area = HIP.length * GAP
print(f"gap {GAP} mm at {ALPHA} deg; lip z {ZL.min():.1f}..{ZL.max():.1f}, seat {ZSEAT:.1f}, top {ZTOP:.1f}; "
      f"slot area {area:.0f} mm2 vs leg channel {np.pi*CH_D**2/4:.0f} mm2; plenum roof {roof_top:.1f} < pocket {zs0:.1f}")
