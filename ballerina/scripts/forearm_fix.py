#!/usr/bin/env python3
"""Round out the faceted forearms and blend the wrist crease.

Each forearm is remeshed finely, then its surface is refit as a smooth tube:
in coordinates along the forearm axis, the radius r(angle, height) is fit with
a few angular harmonics times smooth splines along the arm, and vertices are
moved onto that fit. Flat facets and the wrist step disappear; the forearm's
overall shape (taper, oval section) is kept. Weights fade out at the elbow and
just past the wrist so nothing else moves.

Usage: forearm_fix.py in.stl out.stl
"""
import os
import sys

import numpy as np
import pymeshlab
import scipy.sparse as sp
from scipy.interpolate import BSpline
import trimesh

E = lambda k, d: float(os.environ.get(k, d))
src, dst = sys.argv[1:3]
K = int(E("HARM", 4))          # angular harmonics kept
KNOT = E("KNOT", 3.0)          # mm between spline knots along the arm
ARMS = {"L": dict(side=-1, z_elbow=266.0, z_wrist=E("ZW_L", 296.5)),
        "R": dict(side=1, z_elbow=267.5, z_wrist=E("ZW_R", 297.5))}


def ss(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def arm_axis(m, side):
    cs = []
    zs = np.arange(270, 294, 1.0)
    for z in zs:
        ps = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1]).to_2D(to_2D=np.eye(4))[0].polygons_full
        p = max([q for q in ps if np.sign(q.centroid.x) == side and abs(q.centroid.x) > 20], key=lambda q: q.area)
        cs.append([p.centroid.x, p.centroid.y])
    c1, c0 = np.polyfit(zs, np.array(cs), 1)
    a = np.array([c1[0], c1[1], 1.0]); a /= np.linalg.norm(a)
    return np.array([*c0, 0.0]), a


def remesh(m, q, target):
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(m.vertices, m.faces, v_scalar_array=q.astype(float)))
    ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
    ms.compute_selection_transfer_vertex_to_face(inclusive=True)
    ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(target),
                                            selectedonly=True, featuredeg=180)
    cm = ms.current_mesh()
    return trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=False)


m = trimesh.load(src, force="mesh")
axes = {k: arm_axis(m, a["side"]) for k, a in ARMS.items()}


def local(v, k):
    p0, a = axes[k]
    h_ = (v - p0) @ a                      # p0 is at z = 0, so h ~ z / cos(tilt)
    foot = p0 + np.outer(h_, a)
    d = v - foot
    return h_, foot, d


# fine, even triangles over both forearms (elbow to past the wrist)
q = np.zeros(len(m.vertices), bool)
for k, arm in ARMS.items():
    h_, foot, d = local(m.vertices, k)
    rr = np.linalg.norm(d, axis=1)
    hz = lambda z: z / axes[k][1][2]
    q |= (h_ > hz(arm["z_elbow"] - 6)) & (h_ < hz(arm["z_wrist"] + 10)) & (rr < 12)
m = remesh(m, q, 0.35)

v = m.vertices.copy()
for k, arm in ARMS.items():
    p0, a = axes[k]
    hz = lambda z: z / a[2]
    h_, foot, d = local(v, k)
    rr = np.linalg.norm(d, axis=1)
    u = np.cross(a, [0, 0, 1.0]) if abs(a[2]) < 0.999 else np.array([1.0, 0, 0])
    u = np.cross([0, 1.0, 0], a); u /= np.linalg.norm(u)
    w2 = np.cross(a, u)
    th = np.arctan2(d @ w2, d @ u)
    h_lo, h_hi = hz(arm["z_elbow"] - 5), hz(arm["z_wrist"] + E("FIT_HI", 8))
    sel = (h_ > h_lo) & (h_ < h_hi) & (rr < E("RMAX", 11))
    # spline basis along the arm x Fourier basis around it
    deg = 3
    inner = np.arange(h_lo, h_hi + 1e-6, KNOT)
    t = np.r_[[inner[0]] * deg, inner, [inner[-1]] * deg]
    nb = len(t) - deg - 1

    def basis(hh, tt):
        Bh = BSpline.design_matrix(np.clip(hh, inner[0], inner[-1] - 1e-9), t, deg).toarray()
        F = [np.ones_like(tt)]
        for j in range(1, K + 1):
            F += [np.cos(j * tt), np.sin(j * tt)]
        F = np.stack(F, 1)
        return (Bh[:, :, None] * F[:, None, :]).reshape(len(hh), -1)

    X = basis(h_[sel], th[sel])
    lam = 1e-3
    coef = np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ rr[sel])
    r_fit = basis(h_[sel], th[sel]) @ coef
    w = ss((h_[sel] - hz(arm["z_elbow"] - 3)) / 4) * ss((hz(arm["z_wrist"] + E("W1", 6)) - h_[sel]) / (E("W1", 6) - E("W0", 2)))
    dirn = d[sel] / rr[sel, None]
    v[sel] += (w * (r_fit - rr[sel]))[:, None] * dirn
    print(f"{k}: moved up to {np.abs(w*(r_fit-rr[sel])).max():.2f} mm, "
          f"median {np.median(np.abs(w*(r_fit-rr[sel]))[w > 0.5]):.2f} mm; fit rms {np.sqrt(np.mean((r_fit-rr[sel])**2)):.2f}")
m.vertices = v

# soften the fade edges with a short Taubin pass over the same band
w = np.zeros(len(v))
for k, arm in ARMS.items():
    h_, foot, d = local(v, k)
    rr = np.linalg.norm(d, axis=1)
    hz = lambda z: z / axes[k][1][2]
    w = np.maximum(w, ((h_ > hz(arm["z_elbow"] - 6)) & (h_ < hz(arm["z_wrist"] + E("W1", 6) + 1)) & (rr < 12)).astype(float))
e = m.edges_unique
n = len(v)
A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
L = sp.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A - sp.identity(n)
for _ in range(int(E("TAUBIN", 15))):
    v = v + 0.5 * w[:, None] * (L @ v)
    v = v - 0.53 * w[:, None] * (L @ v)
m.vertices = v

# wrist: blend the hand-to-forearm seam with strong local smoothing in a band
# around the wrist (the radial fit stops here; the palm is not tube-shaped)
from scipy.sparse.linalg import spsolve
wb = np.zeros(len(v))
for k, arm in ARMS.items():
    h_, foot, d = local(v, k)
    rr = np.linalg.norm(d, axis=1)
    hz = lambda z: z / axes[k][1][2]
    hw = hz(arm["z_wrist"] + E("WC", 1.0))
    wb = np.maximum(wb, ss((E("WB", 3.5) - np.abs(h_ - hw)) / 2.0) * (rr < 12))
vv = np.column_stack([spsolve((sp.identity(n) - E("W_LAM", 20) * sp.diags(wb) @ L).tocsc(), v[:, k_]) for k_ in range(3)])
for _ in range(20):
    vv = vv + 0.5 * wb[:, None] * (L @ vv)
    vv = vv - 0.53 * wb[:, None] * (L @ vv)
m.vertices = vv
m = trimesh.Trimesh(m.vertices, m.faces)
m.export(dst)
print("watertight:", m.is_watertight, "parts:", len(m.split(only_watertight=False)), "size:", m.extents.round(1))
