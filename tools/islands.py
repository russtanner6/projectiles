#!/usr/bin/env python3
"""Find floating regions: parts of a layer with nothing under them on the layer below.

Usage: islands.py part.stl [--layer 0.2] [--min-area 0.05]

Slices the part every --layer mm (like the slicer) and reports any region on a
layer that doesn't overlap the layer below. Those print in mid-air and are what
Bambu Studio warns about as "floating regions".
"""
import argparse
import sys

import numpy as np
import shapely
import trimesh

ap = argparse.ArgumentParser()
ap.add_argument("stl")
ap.add_argument("--layer", type=float, default=0.1)
ap.add_argument("--min-area", type=float, default=0.0,
                help="ignore islands smaller than this (mm^2); Bambu flags even tiny ones")
a = ap.parse_args()

m = trimesh.load(a.stl, force="mesh")
zs = np.arange(m.bounds[0][2] + a.layer / 2, m.bounds[1][2], a.layer)
sections = m.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=list(zs))
prev = None
found = 0
for z, sec in zip(zs, sections):
    geom = shapely.union_all(sec.polygons_full) if sec is not None and len(sec.polygons_full) else None
    if geom is not None and prev is not None:
        parts = getattr(geom, "geoms", [geom])
        for p in parts:
            if p.area >= a.min_area and not p.intersects(prev):
                c = p.centroid
                print(f"floating region at Z={z:.2f} mm: area {p.area:.2f} mm^2, "
                      f"center ({c.x:.1f}, {c.y:.1f}), r={np.hypot(c.x, c.y):.1f} mm")
                found += 1
    prev = geom
print(f"{found} floating region(s)")
sys.exit(1 if found else 0)
