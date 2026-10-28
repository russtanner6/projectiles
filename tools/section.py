#!/usr/bin/env python3
"""Draw a true lengthwise cross-section of an STL (cut through the axis).

Usage: section.py part.stl out.png [--angle DEG]
--angle rotates the cut plane about Z (useful to cut through or between fins).
"""
import argparse
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from trimesh.intersections import mesh_plane

ap = argparse.ArgumentParser()
ap.add_argument("stl")
ap.add_argument("out")
ap.add_argument("--angle", type=float, default=0.0)
a = ap.parse_args()

m = trimesh.load(a.stl, force="mesh")
t = math.radians(a.angle)
normal = [-math.sin(t), math.cos(t), 0]
segs = mesh_plane(m, plane_normal=normal, plane_origin=[0, 0, 0])
u = np.array([math.cos(t), math.sin(t), 0])  # in-plane horizontal axis

fig, ax = plt.subplots(figsize=(5, 9))
for s in segs:
    ax.plot(s[:, :3] @ u, s[:, 2], color="#1f4e79", lw=0.8)
ax.set_aspect("equal")
ax.set_xlabel("mm")
ax.set_ylabel("Z (mm, base on bed)")
ax.set_title(f"Lengthwise section at {a.angle:.0f} deg")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(a.out, dpi=130)
