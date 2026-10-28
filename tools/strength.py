#!/usr/bin/env python3
"""Bending section modulus along the length of a nose-up projectile STL.

Usage: strength.py part.stl [other.stl ...] [--step 1.0]

At each height Z, slices the part and computes the section modulus
Z = I / c (mm^3) for bending, taking the weaker of the X and Y axes. The
stress across a layer line is (bending moment) / Z, so a layer with half the
Z cracks at half the bending load. Compare designs by their minimum Z,
ignoring the first and last few mm, where the bending load is near zero.
"""
import argparse

import numpy as np
import shapely
import trimesh


def section_modulus(m, z, res=0.25):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return 0.0
    polys = [p for p in s.to_2D(to_2D=np.eye(4))[0].polygons_full]
    if not polys:
        return 0.0
    g = shapely.union_all(polys)
    x0, y0, x1, y1 = g.bounds
    xs, ys = np.meshgrid(np.arange(x0, x1, res), np.arange(y0, y1, res))
    inside = shapely.contains_xy(g, xs, ys)
    x, y = xs[inside], ys[inside]
    da = res * res
    x, y = x - x.mean(), y - y.mean()
    ix, iy = (y ** 2).sum() * da, (x ** 2).sum() * da
    return min(ix / np.abs(y).max(), iy / np.abs(x).max())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stl", nargs="+")
    ap.add_argument("--step", type=float, default=1.0)
    ap.add_argument("--skip", type=float, default=8.0, help="ignore this many mm at each end")
    a = ap.parse_args()
    for path in a.stl:
        m = trimesh.load(path, force="mesh")
        top = m.bounds[1][2]
        zs = np.arange(a.skip, top - a.skip, a.step)
        zm = np.array([section_modulus(m, z) for z in zs])
        i = zm.argmin()
        print(f"{path}: weakest layer at Z={zs[i]:.0f} mm ({top - zs[i]:.0f} mm from tip), "
              f"section modulus {zm[i]:.0f} mm^3; median {np.median(zm):.0f} mm^3")


if __name__ == "__main__":
    main()
