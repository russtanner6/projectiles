#!/usr/bin/env python3
"""Check a projectile STL against project rules and report its mass properties.

Usage: check_stl.py part.stl [--density 1.25] [--max-width 38.0] [--binary]

Assumes the part is modeled nose-up along +Z with the base at Z = 0, and that
it prints at uniform density (so the solid's centroid is the CG).
--binary rewrites the file as binary STL (OpenSCAD writes large ASCII files).
"""
import argparse
import sys

import numpy as np
import trimesh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stl")
    ap.add_argument("--density", type=float, default=1.25, help="g/cm^3 (PCTG ~1.23-1.27)")
    ap.add_argument("--max-width", type=float, default=38.0, help="mm")
    ap.add_argument("--binary", action="store_true", help="rewrite as binary STL")
    args = ap.parse_args()

    m = trimesh.load(args.stl, force="mesh")
    r = np.hypot(m.vertices[:, 0], m.vertices[:, 1])
    max_d = 2 * r.max()
    length = m.bounds[1][2] - m.bounds[0][2]
    mass = m.volume / 1000 * args.density
    cg_from_tip = m.bounds[1][2] - m.center_mass[2]

    ok_width = max_d <= args.max_width + 1e-6
    print(f"file:          {args.stl}")
    print(f"watertight:    {m.is_watertight}")
    print(f"max diameter:  {max_d:.2f} mm (limit {args.max_width:.1f}) {'OK' if ok_width else 'TOO WIDE'}")
    print(f"length:        {length:.2f} mm")
    print(f"volume:        {m.volume / 1000:.2f} cm^3")
    print(f"mass (solid):  {mass:.1f} g ({mass / 28.3495:.2f} oz) at {args.density} g/cm^3")
    print(f"CG from tip:   {cg_from_tip:.1f} mm ({cg_from_tip / length * 100:.0f}% of length)")

    if args.binary:
        m.export(args.stl, file_type="stl")
        print("rewrote as binary STL")

    if not (m.is_watertight and ok_width):
        sys.exit(1)


if __name__ == "__main__":
    main()
