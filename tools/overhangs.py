#!/usr/bin/env python3
"""Find surfaces that would need supports when printed nose-up (base on the bed).

Usage: overhangs.py part.stl [--max-angle 45] [--bed-tol 0.3]

A downward-facing surface needs support when it is tilted more than
--max-angle degrees from vertical (i.e. flatter than 45 deg from horizontal by
default). Faces lying on the bed (Z ~ 0) are ignored. Reports total overhang
area and where it is.
"""
import argparse
import sys

import numpy as np
import trimesh

ap = argparse.ArgumentParser()
ap.add_argument("stl")
ap.add_argument("--max-angle", type=float, default=45.0)
ap.add_argument("--bed-tol", type=float, default=0.3)
a = ap.parse_args()

m = trimesh.load(a.stl, force="mesh")
nz = m.face_normals[:, 2]
# angle from vertical of a down-facing face = asin(-nz)
limit = np.sin(np.radians(a.max_angle))
zmin = m.triangles[:, :, 2].min(axis=1)
bad = (-nz > limit + 1e-6) & (zmin > m.bounds[0][2] + a.bed_tol)
area = m.area_faces[bad].sum()
worst = np.degrees(np.arcsin(np.clip(-nz[(zmin > m.bounds[0][2] + a.bed_tol)], -1, 1))).max()
print(f"steepest downward face: {worst:.1f} deg from vertical (limit {a.max_angle:.0f})")
print(f"overhang area needing support: {area:.2f} mm^2 in {bad.sum()} faces")
if bad.any():
    zs = m.triangles_center[bad][:, 2]
    rs = np.hypot(*m.triangles_center[bad][:, :2].T)
    for z0 in np.unique(np.round(zs)):
        sel = np.round(zs) == z0
        print(f"  Z~{z0:.0f} mm, r {rs[sel].min():.1f}-{rs[sel].max():.1f} mm, {m.area_faces[bad][sel].sum():.2f} mm^2")
    sys.exit(1)
