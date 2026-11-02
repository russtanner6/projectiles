#!/usr/bin/env python3
"""Chiselled, low-poly hands to match the faceted body and pointe-shoe feet.

Each hand is a single faceted blade (fingers together, no separate digits):
a chain of octagonal cross-sections from the wrist through the palm to a
squared-off tip, curving gently toward the palm. Consecutive sections are
joined with convex hulls, which gives flat facets and crisp edges. The first
sections are taken from her actual forearm at the wrist so the hand starts
flush with the arm. An optional faceted thumb wedge lies along the palm side.

Usage: hand_facet.py in.stl out.stl
"""
import os
import sys

import manifold3d as mf
import numpy as np
import trimesh

E = lambda k, d: float(os.environ.get(k, d))
src, dst = sys.argv[1:3]
FRONT = np.array([np.cos(np.radians(-55)), np.sin(np.radians(-55)), 0.0])
ARMS = {"L": dict(side=-1, z_wrist=E("ZW_L", 296.5)), "R": dict(side=1, z_wrist=E("ZW_R", 297.5))}
THUMB = E("THUMB", 1)

# hand sections along the hand (local x from the wrist): x, width, thickness, bend (deg, toward palm)
SECTIONS = [
    (3.5, 8.6, 4.9, 0),      # heel of the hand
    (9.5, 9.0, 3.7, 2),      # knuckles (widest)
    (14.5, 8.0, 3.1, 3),     # fingers together
    (18.5, 6.4, 2.6, 3),
    (E("TIP", 21.5), 4.2, 2.2, 2),   # squared-off tip (>= 2 mm thick)
]


def to_mf(t):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32),
                               tri_verts=np.asarray(t.faces, np.uint32)))


def from_mf(g):
    m_ = g.to_mesh()
    return trimesh.Trimesh(m_.vert_properties[:, :3], m_.tri_verts, process=False)


def octagon(w, t, ch=0.32):
    """flattened octagon in (y, z): flat top/bottom and sides, chamfered corners."""
    a, b = w / 2, t / 2
    c = min(a, b) * ch * 2
    return np.array([[a, b - c], [a - c, b], [-a + c, b], [-a, b - c],
                     [-a, -b + c], [-a + c, -b], [a - c, -b], [a, -b + c]])


def rot(axis, deg):
    return trimesh.transformations.rotation_matrix(np.radians(deg), axis)[:3, :3]


m = trimesh.load(src, force="mesh")


def arm_axis(side):
    cs, zs = [], np.arange(272, 294, 1.0)
    for z in zs:
        ps = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1]).to_2D(to_2D=np.eye(4))[0].polygons_full
        p = max([q for q in ps if np.sign(q.centroid.x) == side and abs(q.centroid.x) > 20], key=lambda q: q.area)
        cs.append([p.centroid.x, p.centroid.y])
    c1, c0 = np.polyfit(zs, np.array(cs), 1)
    a = np.array([c1[0], c1[1], 1.0])
    return np.array([*c0, 0.0]), a / np.linalg.norm(a)


def wrist_ring(origin, nrm, scale, n=32):
    """her actual forearm outline at this plane, resampled, scaled about its centre."""
    s = m.section(plane_origin=origin, plane_normal=nrm)
    best = min(s.discrete, key=lambda p: np.linalg.norm(p.mean(0) - origin))
    path = trimesh.load_path(best)
    pts = np.array([path.entities[0].discrete(path.vertices)][0])
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    t = np.linspace(0, seg[-1], n, endpoint=False)
    res = np.column_stack([np.interp(t, seg, pts[:, k]) for k in range(3)])
    c = res.mean(0)
    return c + (res - c) * scale


out = to_mf(m)
for key, arm in ARMS.items():
    side = arm["side"]
    p0, a = arm_axis(side)
    W = p0 + a * (arm["z_wrist"] / a[2])
    v_ = m.vertices
    hp = v_[(np.sign(v_[:, 0]) == side) & (np.abs(v_[:, 0]) > 8) & ((v_ - W) @ a > 1.5)]
    _, _, Vt = np.linalg.svd(hp - hp.mean(0), full_matrices=False)
    dist = np.linalg.norm(hp - W, axis=1)
    tip = hp[dist > dist.max() - 5].mean(0)
    Lx = tip - W; Lx /= np.linalg.norm(Lx)
    Nz = Vt[2] - (Vt[2] @ Lx) * Lx; Nz /= np.linalg.norm(Nz)
    if Nz[2] > 0:
        Nz = -Nz                                            # palm faces down / in
    Sy = np.cross(Nz, Lx)
    if Sy @ FRONT < 0:
        Sy = -Sy                                            # thumb toward her front
    pitch = E("PITCH", 8)                                   # lift the palm line above the old chord
    Lx, Nz = (Lx * np.cos(np.radians(pitch)) - Nz * np.sin(np.radians(pitch)),
              Nz * np.cos(np.radians(pitch)) + Lx * np.sin(np.radians(pitch)))

    # wrist rings perpendicular to the forearm, oriented like the hand's octagon
    u = Sy - (Sy @ a) * a; u /= np.linalg.norm(u)
    vv = np.cross(a, u)
    if vv @ Nz < 0:
        vv = -vv
    rings = [wrist_ring(W + a * -3.0, a, 0.94), wrist_ring(W + a * 0.3, a, E("WR_SCALE", 0.985))]
    # hand rings along a path that bends toward the palm
    pos, d, nz, x_prev, bend = W + a * 0.3, Lx.copy(), Nz.copy(), 0.0, 0.0
    sy = Sy
    for x, w, t, b in SECTIONS:
        pos = pos + d * (x - x_prev)
        bend_axis = np.cross(d, nz)
        R = rot(bend_axis, b)                              # +b bends toward the palm
        d, nz = R @ d, R @ nz
        sec = octagon(w, t)
        rings.append(pos + np.outer(sec[:, 0], sy) + np.outer(sec[:, 1], nz))
        x_prev = x
    hulls = [to_mf(trimesh.Trimesh(np.vstack([r0, r1])).convex_hull) for r0, r1 in zip(rings[:-1], rings[1:])]
    hand = mf.Manifold.batch_boolean(hulls, mf.OpType.Add)
    if THUMB:
        # faceted thumb wedge lying along the palm side, tip short of the knuckles
        T0 = W + Lx * 3.0 + Sy * 2.8 + Nz * 0.6
        T1 = W + Lx * 7.5 + Sy * 3.6 + Nz * 1.3
        T2 = W + Lx * 11.0 + Sy * 3.4 + Nz * 1.6
        tr = []
        for c_, w, t in ((T0, 3.6, 3.4), (T1, 2.8, 2.7), (T2, 2.2, 2.1)):
            sec = octagon(w, t)
            tr.append(c_ + np.outer(sec[:, 0], Nz) + np.outer(sec[:, 1], Sy))
        hand = hand + mf.Manifold.batch_boolean(
            [to_mf(trimesh.Trimesh(np.vstack([r0, r1])).convex_hull) for r0, r1 in zip(tr[:-1], tr[1:])], mf.OpType.Add)
    # remove the old hand above the wrist plane (this arm only)
    box = trimesh.creation.box(extents=[200, 200, 200])
    T = np.eye(4); T[:3, :3] = trimesh.geometry.align_vectors([0, 0, 1], a)[:3, :3]
    T[:3, 3] = W + a * (100 + 0.3)
    box.apply_transform(T)
    above = from_mf(out ^ to_mf(box)).split(only_watertight=False)
    old = max([q for q in above if np.linalg.norm(q.centroid - W) < 25], key=lambda q: abs(q.volume))
    out = out - (to_mf(old.convex_hull) ^ to_mf(box))
    out = out + hand
    arm["W"], arm["a"] = W, a
    print(f"{key}: hand dir {Lx.round(2)}, palm {Nz.round(2)}, tip at {pos.round(1)}")

print("manifold status:", out.status(), "components:", len(out.decompose()))
comps = sorted(out.decompose(), key=lambda g: -g.volume())
print("dropped loose bits (mm3):", [round(g.volume(), 3) for g in comps[1:]][:8], "...")
out = comps[0]
res = from_mf(out)
# blend the wrist: smooth forearm turning into the chiselled hand over a short band
import pymeshlab
import scipy.sparse as sp


def ss(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def band(v, lo, hi, rmax):
    q = np.zeros(len(v))
    for arm in ARMS.values():
        h_ = (v - arm["W"]) @ arm["a"]
        rr = np.linalg.norm(v - arm["W"] - np.outer(h_, arm["a"]), axis=1)
        q = np.maximum(q, ss((h_ - lo) / 1.0) * ss((hi - h_) / 1.0) * (rr < rmax))
    return q


BL, BH = E("B_LO", -2.5), E("B_HI", 2.5)
ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(res.vertices, res.faces, v_scalar_array=(band(res.vertices, BL - 1.5, BH + 1.5, 9) > 0).astype(float)))
ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
ms.compute_selection_transfer_vertex_to_face(inclusive=True)
ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(0.3), selectedonly=True, featuredeg=180)
cm = ms.current_mesh()
res = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=False)
v = res.vertices
w = band(v, BL, BH, 8.5)
e = res.edges_unique
n = len(v)
A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
L = sp.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A - sp.identity(n)
for _ in range(int(E("B_IT", 40))):
    v = v + 0.5 * w[:, None] * (L @ v)
    v = v - 0.53 * w[:, None] * (L @ v)
ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(v, res.faces))
ms.meshing_remove_duplicate_faces()
ms.meshing_remove_null_faces()
ms.meshing_repair_non_manifold_edges()
ms.meshing_repair_non_manifold_vertices()
ms.meshing_close_holes(maxholesize=50)
cm = ms.current_mesh()
res = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix())
res = max(res.split(only_watertight=False), key=lambda q: abs(q.volume))
for _ in range(4):                                         # patch any leftover bad edges
    if res.is_watertight and res.is_winding_consistent:
        break
    es = np.sort(res.edges, 1)
    uniq, inv, cnt = np.unique(es, axis=0, return_inverse=True, return_counts=True)
    badv = np.unique(uniq[cnt != 2])
    kill = np.isin(res.faces, badv).any(1)
    res.update_faces(~kill)
    res.remove_unreferenced_vertices()
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(res.vertices, res.faces))
    ms.meshing_repair_non_manifold_edges()
    ms.meshing_repair_non_manifold_vertices()
    ms.meshing_close_holes(maxholesize=60)
    ms.meshing_re_orient_faces_coherently()
    cm = ms.current_mesh()
    res = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix())
    res = max(res.split(only_watertight=False), key=lambda q: abs(q.volume))
trimesh.repair.fix_normals(res)
res.export(dst)
print("watertight:", res.is_watertight, "winding ok:", res.is_winding_consistent, "size:", res.extents.round(1))
