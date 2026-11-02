#!/usr/bin/env python3
"""Check the test piece's water path: plug the two intended openings (barb top
and slot exit), flood the inside from the base channel, and report whether the
water can reach the outside any other way, and whether it reaches the whole
ring and slot.  Usage: leak_check.py part.stl hip_outline.npy"""
import sys
import numpy as np
import scipy.ndimage as ndi
import trimesh
from matplotlib.path import Path
from shapely.geometry import Polygon

m = trimesh.load(sys.argv[1])
hip = Polygon(np.load(sys.argv[2]))
P = 0.15
lo, hi = m.bounds[0] - 1, m.bounds[1] + 1
xs, ys, zs = (np.arange(lo[i], hi[i], P) for i in range(3))
XY = np.stack(np.meshgrid(xs, ys, indexing="ij"), -1).reshape(-1, 2)
solid = np.zeros((len(xs), len(ys), len(zs)), bool)
for k, z in enumerate(zs):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        continue
    for poly in s.to_2D(to_2D=np.eye(4))[0].polygons_full:
        ins = Path(np.asarray(poly.exterior.coords)).contains_points(XY)
        for h in poly.interiors:
            ins &= ~Path(np.asarray(h.coords)).contains_points(XY)
        solid[:, :, k] |= ins.reshape(len(xs), len(ys))
void = ~solid
# plug the barb's open top (bore radius 2.1 at x=-26)
BX = float(sys.argv[4]) if len(sys.argv) > 4 else -26.0
X, Y = np.meshgrid(xs, ys, indexing="ij")
vb = m.vertices[(np.hypot(m.vertices[:, 0] - BX, m.vertices[:, 1]) < 9.0) & (m.vertices[:, 2] < 32)]
barb_top = vb[:, 2].max()
print("barb top at z %.1f" % barb_top)
void[(np.hypot(X - BX, Y) < 9.5)[:, :, None] & (zs > barb_top - 0.6)[None, None, :]] = False
# plug the slot exit: everything outside her outline in the slot's height band
z_lip = float(sys.argv[3]) if len(sys.argv) > 3 else 43.9
outside = ~Path(np.asarray(hip.buffer(0.3).exterior.coords)).contains_points(XY).reshape(X.shape)
inside_ring = ~Path(np.asarray(hip.buffer(-0.2).exterior.coords)).contains_points(XY).reshape(X.shape) & ~outside
if len(sys.argv) > 5:                                   # slot follows the waistband line
    belt = np.load(sys.argv[5]); sh = belt[:, 1] - belt[:, 1].min()
    zl = z_lip + np.interp(np.arctan2(Y, X), belt[:, 0], sh, period=2 * np.pi)
else:
    zl = np.full(X.shape, z_lip)
band3 = (zs[None, None, :] > zl[:, :, None] - 0.8) & (zs[None, None, :] < zl[:, :, None] + 3.0)
band = (zs > zl.min() - 0.8) & (zs < zl.max() + 3.0)
void[(outside | inside_ring)[:, :, None] & band3] = False
lab, n = ndi.label(void)
seed = (np.abs(xs - (-13)).argmin(), np.abs(ys - 0).argmin(), np.abs(zs - 4.0).argmin())
L = lab[seed]
assert L > 0, "seed not in the channel"
water = lab == L
leak = water[0].any() or water[-1].any() or water[:, 0].any() or water[:, -1].any() or water[:, :, 0].any() or water[:, :, -1].any()
print("water path volume: %.2f cm3" % (water.sum() * P**3 / 1000))
print("leaks anywhere except barb and slot:", "YES" if leak else "none")
# does the water reach the slot all the way round? check just inside the outline at the slot band
ring = (~Path(np.asarray(hip.buffer(-1.2).exterior.coords)).contains_points(XY).reshape(X.shape)) & ~outside
kz = np.flatnonzero(band)
reach = water[:, :, kz].any(2) & ring
ang = np.degrees(np.arctan2(Y[reach], X[reach]))
bins = np.histogram(ang, bins=72, range=(-180, 180))[0]
print("slot reached around the ring: %d of 72 five-degree sectors" % (bins > 0).sum())
if leak:
    # trace one escape route: shortest path from seed to the box boundary within the water
    dist = np.full(water.shape, -1, np.int32)
    from collections import deque
    q = deque([seed]); dist[seed] = 0; prev = {}
    end = None
    while q:
        c = q.popleft()
        if 0 in c or c[0] == water.shape[0]-1 or c[1] == water.shape[1]-1 or c[2] == water.shape[2]-1:
            end = c; break
        for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            nb = (c[0]+d[0], c[1]+d[1], c[2]+d[2])
            if water[nb] and dist[nb] < 0:
                dist[nb] = dist[c] + 1; prev[nb] = c; q.append(nb)
    path = [end]
    while path[-1] != seed:
        path.append(prev[path[-1]])
    pts = np.array([[xs[i], ys[j], zs[k]] for i, j, k in path[::-1]])
    for p in pts[::max(1, len(pts)//25)]:
        print("  route", p.round(1))
miss = np.flatnonzero(bins == 0)
print("unreached sectors (deg):", [(-180 + 5 * i, -175 + 5 * i) for i in miss])
