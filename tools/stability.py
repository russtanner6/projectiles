#!/usr/bin/env python3
"""Estimate static stability for an Mk1-style ducted-tail dart.

Usage: stability.py design.scad part.stl [-D name=value ...]

Reads the numeric parameters at the top of the .scad file (with optional -D
overrides, same as OpenSCAD), takes the CG from the rendered STL (uniform
density), and estimates the center of pressure (CP) with the Barrowman method:
nose + flare (boattail) + fins, plus a rough annular-wing term for the duct.

Results are estimates for comparing designs, not guarantees: Barrowman ignores
body lift, which matters for short, fat bodies, and the duct term is crude.
Stability margin = (CP - CG) / diameter, in calibers. Positive = nose-first.
"""
import math
import re
import sys

import trimesh


def read_params(path, overrides):
    p = {}
    for line in open(path):
        mt = re.match(r"\s*([A-Za-z_]\w*)\s*=\s*(-?[\d.]+)\s*;", line)
        if mt:
            p[mt.group(1)] = float(mt.group(2))
    for o in overrides:
        k, v = o.split("=", 1)
        p[k.strip()] = float(v)
    return p


def barrowman_fins(n, s, d_body, cr, ct, xr):
    """Normal-force slope and CP (from fin root leading edge) of a fin set."""
    lf = math.hypot(s, xr + ct / 2 - cr / 2)
    cn4 = 16 * (s / d_body) ** 2 / (1 + math.sqrt(1 + (2 * lf / (cr + ct)) ** 2))
    cn = cn4 * n / 4 * (1 + (d_body / 2) / (s + d_body / 2))
    x = xr * (cr + 2 * ct) / (3 * (cr + ct)) + (cr + ct - cr * ct / (cr + ct)) / 6
    return cn, x


def main():
    args = sys.argv[1:]
    scad, stl = args[0], args[1]
    overrides = [args[i + 1] for i, a in enumerate(args) if a == "-D"]
    p = read_params(scad, overrides)

    L, D = p["total_length"], p["body_d"]
    Ln, Lb, Lf = p["nose_length"], p["bearing_length"], p["flare_length"]
    db, Ld = p["boom_d"], p["duct_length"]
    R, rb = D / 2, db / 2
    z_bearing = L - Ln - Lb
    z_boom = z_bearing - Lf

    m = trimesh.load(stl, force="mesh")
    x_cg = m.bounds[1][2] - m.center_mass[2]

    terms = []
    terms.append(("nose (ellipsoid)", 2.0, 0.333 * Ln))
    ratio = D / db
    terms.append(("flare", 2 * ((db / D) ** 2 - 1),
                  Ln + Lb + Lf / 3 * (1 + (1 - ratio) / (1 - ratio ** 2))))
    cn_f, x_f = barrowman_fins(p["fin_count"], R - rb, db, cr=z_bearing, ct=z_boom, xr=Lf)
    terms.append(("fins", cn_f, (L - z_bearing) + x_f))
    ar = D / Ld
    cn_d = 2 * math.pi * ar / (ar + 2) * (D * Ld) / (math.pi * D * D / 4)
    terms.append(("duct (rough)", cn_d, L - Ld + 0.25 * Ld))

    def cp(ts):
        cn = sum(t[1] for t in ts)
        return sum(t[1] * t[2] for t in ts) / cn

    x_cp_all, x_cp_nod = cp(terms), cp(terms[:3])
    print(f"CG from tip: {x_cg:.1f} mm")
    for name, cn, x in terms:
        print(f"  {name:17s} CNa {cn:+.2f}  at {x:.1f} mm")
    print(f"CP (all terms):  {x_cp_all:.1f} mm  margin {(x_cp_all - x_cg) / D:+.2f} cal")
    print(f"CP (no duct):    {x_cp_nod:.1f} mm  margin {(x_cp_nod - x_cg) / D:+.2f} cal")
    tip_r = R
    lead = 2 * math.pi * tip_r / math.tan(math.radians(p["fin_tip_angle"]))
    print(f"spin: ~{60000 / lead:.0f} RPM per m/s of velocity (ideal, real is lower); "
          f"e.g. {60 * 60000 / lead:.0f} RPM at 60 m/s")


if __name__ == "__main__":
    main()
