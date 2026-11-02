#!/usr/bin/env python3
"""Replace both hands with clean, sculpted ballet hands built from a distance field.

Each hand is modelled from simple rounded pieces (palm bones, three-segment
fingers, a tucked thumb) in a frame taken from the existing hand: wrist
centre, hand direction, palm direction and thumb side. The real forearm near
the wrist is turned into a distance field too, and the two are smoothly
unioned, so the hand grows out of her actual forearm with no seam. The result
is meshed (marching cubes) and joined to the body by a plane cut below the
wrist, then that band is blended.

Fingertips stay at least 2.0 mm thick (FD_MIN).

Usage: hand_sdf.py in.stl out.stl [hands_only.stl]
"""
import os
import sys

import manifold3d as mf
import numpy as np
import pymeshlab
import scipy.ndimage as ndi
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from matplotlib.path import Path
from skimage.measure import marching_cubes
import trimesh

E = lambda k, d: float(os.environ.get(k, d))
src, dst = sys.argv[1:3]
PITCH = E("PITCH", 0.12)
FRONT = np.array([np.cos(np.radians(-55)), np.sin(np.radians(-55)), 0.0])
ARMS = {"L": dict(side=-1, z_wrist=E("ZW_L", 296.5)), "R": dict(side=1, z_wrist=E("ZW_R", 297.5))}


def to_mf(t):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32),
                               tri_verts=np.asarray(t.faces, np.uint32)))


def from_mf(g):
    m_ = g.to_mesh()
    return trimesh.Trimesh(m_.vert_properties[:, :3], m_.tri_verts, process=False)


def ss(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def cone(p, a, b, ra, rb):
    ba = b - a
    t = np.clip(((p - a) @ ba) / (ba @ ba), 0, 1)
    return np.linalg.norm(p - (a + t[:, None] * ba), axis=1) - (ra + t * (rb - ra))


def rot(axis, deg):
    return trimesh.transformations.rotation_matrix(np.radians(deg), axis)[:3, :3]


# ---------------- hand model, local frame: x along hand, y to thumb, z to palm
FD_MIN = E("FD_MIN", 2.0)
FINGERS = {  # knuckle y, segment lengths, flex per joint (deg), spread (deg), radii base->tip
    "index":  dict(y=3.1, seg=(4.8, 3.0, 2.4), flex=(8, 14, 8), spread=3, r=(1.32, 1.22, 1.12, 1.04)),
    "middle": dict(y=1.03, seg=(5.3, 3.4, 2.6), flex=(15, 22, 12), spread=0, r=(1.36, 1.25, 1.15, 1.05)),
    "ring":   dict(y=-1.03, seg=(5.0, 3.2, 2.5), flex=(12, 18, 10), spread=-2.5, r=(1.31, 1.2, 1.11, 1.03)),
    "pinky":  dict(y=-3.0, seg=(3.9, 2.6, 2.1), flex=(9, 15, 8), spread=-5, r=(1.2, 1.11, 1.04, 1.0)),
}
PALM_LEN = E("PALM_LEN", 10.5)
SCALE = E("HAND_SCALE", 1.0)


def hand_parts():
    """list of (a, b, ra, rb, group) round cones in local coordinates."""
    parts = []
    for name, f in FINGERS.items():
        k = np.array([PALM_LEN - abs(f["y"]) * 0.3, f["y"], 0.12 * abs(f["y"])])   # knuckle arc, cupped
        base = np.array([0.8, f["y"] * 0.55, 0.0])
        parts.append((base, k, 1.9, f["r"][0] - 0.12, "palm"))
        d = rot([0, 0, 1], f["spread"]) @ np.array([1.0, 0, 0])
        p = k
        ang = 0
        for i, (L, fl) in enumerate(zip(f["seg"], f["flex"])):
            ang += fl
            dd = rot(np.cross(d, [0, 0, 1]), ang) @ d        # bend toward +z (palm side)
            q = p + L * dd
            parts.append((p, q, f["r"][i], max(f["r"][i + 1], FD_MIN / 2), name))
            p = q
    # thumb: base in the heel of the hand, reaching forward, tip tucked under the index finger
    T = [np.array(x) for x in ([1.4, 2.4, 0.9], [5.2, 4.0, 2.0], [8.4, 4.0, 2.9], [10.8, 3.4, 3.1])]
    T = [t_ + np.array([0, 0, 0]) for t_ in T]
    TR = [2.0, 1.5, 1.36, 1.2, 1.07]
    parts.append((T[0], T[1], TR[0], TR[1], "palm"))
    parts.append((T[1], T[2], TR[1], TR[2], "thumb"))
    parts.append((T[2], T[3], TR[2], max(TR[4], FD_MIN / 2), "thumb"))
    # heel of the hand, as wide as her wrist
    for y in (-1.6, 1.6):
        parts.append((np.array([-2.5, y, 0.0]), np.array([3.0, y * 1.2, 0.3]), 2.75, 2.35, "palm"))
    return [(a * SCALE, b * SCALE, ra * SCALE, rb * SCALE, g) for a, b, ra, rb, g in parts]


def hand_sdf(p):
    groups = {}
    for a, b, ra, rb, g in hand_parts():
        d = cone(p, a, b, ra, rb)
        if g == "palm":
            groups[g] = d if g not in groups else smin(groups[g], d, E("K_PALM", 2.0))
        else:
            groups[g] = d if g not in groups else np.minimum(groups[g], d)   # one smooth tube per finger
    fing = None
    for g, d in groups.items():
        if g != "palm":
            fing = d if fing is None else smin(fing, d, E("K_FING", 0.4))
    return smin(groups["palm"], fing, E("K_PF", 0.9))


def octagon(w, t, ch=0.32):
    a_, b_ = w / 2, t / 2
    c_ = min(a_, b_) * ch * 2
    return np.array([[a_, b_ - c_], [a_ - c_, b_], [-a_ + c_, b_], [-a_, b_ - c_],
                     [-a_, -b_ + c_], [-a_ + c_, -b_], [a_ - c_, -b_], [a_, -b_ + c_]])


FACET_SECTIONS = [  # x along hand, width, thickness, bend toward palm (deg)
    (-1.5, 7.0, 5.6, 0),
    (3.5, 8.6, 4.9, 0),
    (9.5, 9.0, 3.7, 2),
    (14.5, 8.0, 3.1, 3),
    (18.5, 6.4, 2.6, 3),
    (E("TIP", 21.5), 4.2, 2.2, 2),     # squared-off tip, >= 2 mm thick
]


def facet_hulls():
    """convex hulls (local coords) between consecutive octagon sections."""
    rings, pos, d, nz, xp = [], np.zeros(3), np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), 0.0
    for i, (x, w, t, b) in enumerate(FACET_SECTIONS):
        if i:
            pos = pos + d * (x - xp)
        else:
            pos = d * x
        R = rot(np.cross(d, nz), b)
        d, nz = R @ d, R @ nz
        sy = np.cross(nz, d)
        sec = octagon(w, t)
        rings.append(pos + np.outer(sec[:, 0], sy) + np.outer(sec[:, 1], nz))
        xp = x
    hulls = [np.vstack([r0, r1]) for r0, r1 in zip(rings[:-1], rings[1:])]
    if E("THUMB", 0):
        tr = []
        for c_, w, t in (([3.0, 2.8, 0.6], 3.6, 3.4), ([7.5, 3.6, 1.3], 2.8, 2.7), ([11.0, 3.4, 1.6], 2.2, 2.1)):
            sec = octagon(w, t)
            tr.append(np.array(c_) + np.outer(sec[:, 0], [0, 0, 1.0]) + np.outer(sec[:, 1], [0, 1.0, 0]))
        hulls += [np.vstack([r0, r1]) for r0, r1 in zip(tr[:-1], tr[1:])]
    planes = []
    for pts in hulls:
        h = trimesh.Trimesh(pts).convex_hull
        n_ = h.face_normals
        planes.append((n_, np.einsum("ij,ij->i", n_, h.triangles[:, 0])))
    return planes


def loft(rings):
    nr, k = len(rings), len(rings[0])
    V = np.vstack(rings)
    F = []
    for i in range(nr - 1):
        for j in range(k):
            a_, b_ = i * k + j, i * k + (j + 1) % k
            F += [[a_, b_, b_ + k], [a_, b_ + k, a_ + k]]
    V = np.vstack([V, rings[0].mean(0), rings[-1].mean(0)])
    c0, c1 = len(V) - 2, len(V) - 1
    for j in range(k):
        F.append([c0, (j + 1) % k, j])
        F.append([c1, (nr - 1) * k + j, (nr - 1) * k + (j + 1) % k])
    t = trimesh.Trimesh(V, np.array(F))
    if t.volume < 0:
        t.invert()
    return t


def facet_mesh():
    rings, pos, d, nz, xp = [], np.zeros(3), np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), 0.0
    for i, (x, w, t, b) in enumerate(FACET_SECTIONS):
        pos = pos + d * (x - xp) if i else d * x
        R = rot(np.cross(d, nz), b)
        d, nz = R @ d, R @ nz
        sy = np.cross(nz, d)
        sec = octagon(w, t)
        rings.append(pos + np.outer(sec[:, 0], sy) + np.outer(sec[:, 1], nz))
        xp = x
    meshes = [loft(rings)]
    if E("THUMB", 0):
        tr = []
        for c_, w, t in (([3.0, 2.8, 0.6], 3.6, 3.4), ([7.5, 3.6, 1.3], 2.8, 2.7), ([11.0, 3.4, 1.6], 2.2, 2.1)):
            sec = octagon(w, t)
            tr.append(np.array(c_) + np.outer(sec[:, 0], [0, 0, 1.0]) + np.outer(sec[:, 1], [0, 1.0, 0]))
        meshes.append(loft(tr))
    return meshes


def occupancy(mesh, xs, ys, zs, keep=None):
    occ = np.zeros((len(xs), len(ys), len(zs)), bool)
    XY = np.stack(np.meshgrid(xs, ys, indexing="ij"), -1).reshape(-1, 2)
    zmin, zmax = mesh.bounds[:, 2]
    for k, z in enumerate(zs):
        if z <= zmin or z >= zmax:
            continue
        sec_ = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if sec_ is None:
            continue
        for poly in sec_.to_2D(to_2D=np.eye(4))[0].polygons_full:
            if keep is not None and not keep(z, poly):
                continue
            inside = Path(np.asarray(poly.exterior.coords)).contains_points(XY)
            for hole in poly.interiors:
                inside &= ~Path(np.asarray(hole.coords)).contains_points(XY)
            occ[:, :, k] |= inside.reshape(len(xs), len(ys))
    return occ


def facet_sdf(p):
    out_ = None
    for n_, d_ in facet_hulls():
        dd = (p @ n_.T - d_).max(1)
        out_ = dd if out_ is None else np.minimum(out_, dd)
    return out_


if E("FACET", 0):
    hand_sdf = facet_sdf


# ---------------- body
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


out = m
hands_only = []
for key, arm in ARMS.items():
    side = arm["side"]
    p0, a = arm_axis(side)
    W = p0 + a * (arm["z_wrist"] / a[2])                    # wrist centre on the forearm axis
    v = m.vertices
    hsel = (np.sign(v[:, 0]) == side) & (np.abs(v[:, 0]) > 8) & ((v - W) @ a > 1.5)
    hp = v[hsel]
    c = hp.mean(0)
    _, _, Vt = np.linalg.svd(hp - c, full_matrices=False)
    dist = np.linalg.norm(hp - W, axis=1)
    tip = hp[dist > dist.max() - 5].mean(0)
    Lx = tip - W; Lx /= np.linalg.norm(Lx)
    Nz = Vt[2] - (Vt[2] @ Lx) * Lx; Nz /= np.linalg.norm(Nz)
    if Nz[2] > 0:                                          # palms face down / in
        Nz = -Nz
    Sy = np.cross(Nz, Lx)
    if Sy @ FRONT < 0:                                     # thumbs toward her front
        Sy = -Sy
    # tilt the hand frame: the chord to the old fingertips is lower than the palm line
    Lx = rot(np.cross(Lx, Nz), 0) @ Lx
    pitch = E("PITCH_" + key, 4)                           # deg: lift the palm line above the chord
    R = rot(Sy if np.linalg.det(np.c_[Lx, Sy, Nz]) > 0 else -Sy, 0)
    Lx2 = Lx * np.cos(np.radians(pitch)) - Nz * np.sin(np.radians(pitch))
    Nz2 = Nz * np.cos(np.radians(pitch)) + Lx * np.sin(np.radians(pitch))
    Lx, Nz = Lx2, Nz2
    Fr = np.c_[Lx, Sy, Nz]                                 # local -> world
    print(f"{key}: wrist {W.round(1)}, hand dir {Lx.round(2)}, palm {Nz.round(2)}, thumb {Sy.round(2)}")

    # grid (world, axis aligned) around the wrist and hand
    corners = np.array([[x, y, z] for x in (-8, 28) for y in (-8, 8) for z in (-6, 9)]) @ Fr.T + W
    corners = np.vstack([corners, W - a * 8 + np.array([[s1 * 7, s2 * 7, 0] for s1 in (-1, 1) for s2 in (-1, 1)])])
    lo, hi = corners.min(0) - 1, corners.max(0) + 1
    xs, ys, zs = (np.arange(lo[i], hi[i], PITCH) for i in range(3))
    print(f"  grid {len(xs)}x{len(ys)}x{len(zs)}")

    # forearm stub occupancy from horizontal slices of the real mesh
    occ = np.zeros((len(xs), len(ys), len(zs)), bool)
    XY = np.stack(np.meshgrid(xs, ys, indexing="ij"), -1).reshape(-1, 2)
    for k, z in enumerate(zs):
        s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if s is None:
            continue
        ax_pt = p0 + a * (z / a[2])
        for poly in s.to_2D(to_2D=np.eye(4))[0].polygons_full:
            if np.hypot(poly.centroid.x - ax_pt[0], poly.centroid.y - ax_pt[1]) > 7:
                continue
            inside = Path(np.asarray(poly.exterior.coords)).contains_points(XY)
            for hole in poly.interiors:
                inside &= ~Path(np.asarray(hole.coords)).contains_points(XY)
            occ[:, :, k] |= inside.reshape(len(xs), len(ys))
    sd_stub = (ndi.distance_transform_edt(~occ) - ndi.distance_transform_edt(occ)) * PITCH
    sd_stub = ndi.gaussian_filter(sd_stub, E("STUB_SIG", 1.2)).astype(np.float32)

    G = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
    hcoord = ((G - W) @ a).reshape(occ.shape).astype(np.float32)
    cap = hcoord - E("STUB_END", 1.0)
    kc = E("K_CAP", 2.0)                                     # rounded end, no flat ledge
    hh = np.maximum(kc - np.abs(sd_stub - cap), 0) / kc
    stub = np.maximum(sd_stub, cap) + hh * hh * kc * 0.25
    if E("FACET", 0):
        hocc = np.zeros(occ.shape, bool)
        for hm in facet_mesh():
            hm = hm.copy()
            hm.vertices = hm.vertices @ Fr.T + W            # local -> world
            hocc |= occupancy(hm, xs, ys, zs)
        hs = ((ndi.distance_transform_edt(~hocc) - ndi.distance_transform_edt(hocc)) * PITCH).astype(np.float32)
    else:
        loc = (G - W) @ Fr                                  # world -> local
        hs = np.empty(len(G), np.float32)
        for i in range(0, len(G), 2_000_000):
            hs[i:i + 2_000_000] = hand_sdf(loc[i:i + 2_000_000])
        hs = hs.reshape(occ.shape)
    kw = E("K_WRIST", 2.2) * ss((E("K_FADE", 3.0) - hcoord) / 3.0) + 0.02   # blend only at the wrist
    field = smin(stub, hs, kw)
    if E("FIELD_SIG", 0):
        field = ndi.gaussian_filter(field, E("FIELD_SIG", 0))   # removes marching-cubes speckle on facet edges
    field[[0, -1], :, :] = field[:, [0, -1], :] = 1          # closed surface at the box faces
    field[:, :, [0, -1]] = 1
    vs, fs, _, _ = marching_cubes(field, 0.0, spacing=(PITCH,) * 3)
    piece = trimesh.Trimesh(vs + lo, fs[:, ::-1])
    if piece.volume < 0:
        piece.invert()
    hands_only.append(piece)
    # keep the new piece above a cut plane across the forearm; drop the old hand above it
    cut = E("CUT", 5.0)
    box = trimesh.creation.box(extents=[200, 200, 200])
    T = np.eye(4); T[:3, :3] = trimesh.geometry.align_vectors([0, 0, 1], a)[:3, :3]
    T[:3, 3] = W + a * (100 - cut)
    box.apply_transform(T)                                  # half-space above the cut
    box2 = box.copy(); box2.apply_translation(-a * 0.6)
    above = from_mf(to_mf(out) ^ to_mf(box)).split(only_watertight=False)
    old = [q for q in above if np.linalg.norm(q.centroid - W) < 25 and abs(q.volume) > 20]
    old = max(old, key=lambda q: abs(q.volume))
    body_cut = to_mf(out) - (to_mf(old.convex_hull) ^ to_mf(box))
    newp = to_mf(piece) ^ to_mf(box2)
    out = from_mf(body_cut + newp)
    out = max(out.split(only_watertight=False), key=lambda q: abs(q.volume))
    arm["W"], arm["a"], arm["cut"] = W, a, cut

# blend the two join bands (plane cuts across the forearms)
v = out.vertices
q = np.zeros(len(v), bool)
for arm in ARMS.values():
    h_ = (v - arm["W"]) @ arm["a"]
    rr = np.linalg.norm(v - arm["W"] - np.outer(h_, arm["a"]), axis=1)
    q |= (h_ > -arm["cut"] - 3) & (h_ < 3) & (rr < 10)
ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(v, out.faces, v_scalar_array=q.astype(float)))
ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
ms.compute_selection_transfer_vertex_to_face(inclusive=True)
ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(0.3),
                                        selectedonly=True, featuredeg=180)
cm = ms.current_mesh()
out = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=False)
v = out.vertices
w = np.zeros(len(v))
for arm in ARMS.values():
    h_ = (v - arm["W"]) @ arm["a"]
    rr = np.linalg.norm(v - arm["W"] - np.outer(h_, arm["a"]), axis=1)
    w = np.maximum(w, ss((h_ + arm["cut"] + 2) / 1.5) * ss((2.0 - h_) / 2.0) * (rr < 9))
e = out.edges_unique
n = len(v)
A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
L = sp.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A - sp.identity(n)
for _ in range(int(E("JOIN_IT", 50))):
    v = v + 0.5 * w[:, None] * (L @ v)
    v = v - 0.53 * w[:, None] * (L @ v)
out.vertices = v

ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(out.vertices, out.faces))
ms.meshing_remove_duplicate_faces()
ms.meshing_remove_null_faces()
ms.meshing_repair_non_manifold_edges()
ms.meshing_repair_non_manifold_vertices()
ms.meshing_close_holes(maxholesize=50)
cm = ms.current_mesh()
out = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix())
parts = out.split(only_watertight=False)
out = max(parts, key=lambda q: abs(q.volume))
out.export(dst)
if len(sys.argv) > 3:
    trimesh.util.concatenate(hands_only).export(sys.argv[3])
print("watertight:", out.is_watertight, "parts:", len(parts), "size:", out.extents.round(1))
