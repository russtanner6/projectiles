#!/usr/bin/env python3
"""Sculpt fixes for the Meshy ballerina. Every edit is local with a soft falloff,
so the rest of the figure keeps its original surface.

  1. Thighs: move them slightly toward each other so they press together and
     the thigh gap closes. Fades out below the knees (calves, shins and feet are
     untouched, keeping their space) and above the hips. The overlap is merged
     into one clean solid.
  2. Calves: up to 10% slimmer at the fullest point, blending to zero.
  3. Bust: about 10% larger, blending smoothly into the chest.
  4. Re-triangulate the edited areas into fine, even triangles, then smooth:
     the hard edges under the butt, the jaw line, the bun's bottom lip, and the
     nose tip (rounded slightly, keeping the upturn).
  5. Scale to the final height (305 mm, about a foot).

Usage: sculpt.py in.stl out.stl
All coordinates below are in the source model's units (50 mm tall).
"""
import sys

import numpy as np
import pymeshlab
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from scipy.spatial import cKDTree
import trimesh

src, dst = sys.argv[1], sys.argv[2]
m = trimesh.load(src, force="mesh")

# ----- settings -----
THIGH_SHIFT = float(__import__('os').environ.get('SHIFT', 0.14))                       # mm per thigh, toward the other
THIGH_Z = (19.6, 22.6, 23.7, 26.2)       # fade in, full, full, fade out
SEAM_C = np.array([0.82, 0.52])          # point on the line between the thighs
SEAM_N = np.array([0.853, 0.522])        # direction from one thigh to the other

CALF = dict(z0=9.0, zpeak=13.2, z1=16.5, amount=0.10)

BUST_C = np.array([0.35, -2.0, 33.8])    # scaling center, inside the chest
BUST_R = (1.3, 2.4)                      # full effect / zero effect radius
BUST_SCALE = 0.08

HIP = (np.array([0.8, 0.6, 23.0]), 1.6, 3.0)
JAW = (np.array([0.90, 0.05, 39.40]), 1.1, 1.9)
JAW_ZMAX = (39.85, 40.25)                # no effect above this (keeps lips/chin)
BUN = (np.array([-2.55, 1.75, 41.05]), 0.7, 1.3)
NOSE = (np.array([2.90, -0.04, 41.15]), 0.12, 0.45)
REMESH_LEN = 0.04
ARCH_R = (0.2, 0.55)
ARCH_LAP = int(__import__('os').environ.get('ARCH_LAP', 6))
ARCH_LAM = float(__import__('os').environ.get('ARCH_LAM', 0))


def smoothstep(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def falloff(d, r_full, r_zero):
    return smoothstep((r_zero - d) / (r_zero - r_full))


def weight(v, region):
    c, r0, r1 = region
    return falloff(np.linalg.norm(v - c, axis=1), r0, r1)


def ramp(z, z0, z1, z2, z3):
    """0 below z0, rises to 1 at z1, holds to z2, falls to 0 at z3."""
    return np.where(z < z1, smoothstep((z - z0) / (z1 - z0)), smoothstep((z3 - z) / (z3 - z2)))


def adjacency(mesh):
    e = mesh.edges_unique
    n = len(mesh.vertices)
    a = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])),
                      shape=(n, n)).tocsr()
    deg = np.asarray(a.sum(1)).ravel()
    return sp.diags(1 / np.maximum(deg, 1)) @ a


def implicit_smooth(mesh, w, lam):
    """Strong, stable smoothing in one step: solve (I - lam*W*L) v' = v."""
    A = adjacency(mesh)
    n = len(mesh.vertices)
    M = (sp.identity(n) - lam * sp.diags(w) @ (A - sp.identity(n))).tocsc()
    v = mesh.vertices
    mesh.vertices = np.column_stack([spsolve(M, v[:, k]) for k in range(3)])
    return mesh


def smooth(mesh, w, laplace=0, taubin=0):
    A = adjacency(mesh)
    v = mesh.vertices.copy()
    W = w[:, None]
    for _ in range(laplace):
        v += 0.5 * W * (A @ v - v)
    for _ in range(taubin):
        v += 0.5 * W * (A @ v - v)
        v += -0.53 * W * (A @ v - v)
    mesh.vertices = v
    return mesh


# ---------- 1. thighs closer ----------
v = m.vertices.copy()
s = (v[:, :2] - SEAM_C) @ SEAM_N
w = ramp(v[:, 2], *THIGH_Z)
# Above the thigh gap the seam becomes the butt cleft: there, don't move the
# surface right next to the seam, so the cleft's two walls never cross.
cleft = smoothstep((v[:, 2] - 23.55) / 0.4)
w = w * ((1 - cleft) + cleft * smoothstep(np.abs(s) / 0.7))
v[:, :2] -= (np.sign(s) * THIGH_SHIFT * w)[:, None] * SEAM_N
m.vertices = v

# merge the overlap into one solid (libigl boolean resolves self-intersections)
ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(m.vertices, m.faces))
dot = trimesh.creation.icosphere(subdivisions=1, radius=0.05)
dot.apply_translation([0.6, -0.3, 30.0])          # tiny seed inside the torso
ms.add_mesh(pymeshlab.Mesh(dot.vertices, dot.faces))
ms.generate_boolean_union(first_mesh=0, second_mesh=1)
mm = ms.current_mesh()
m = trimesh.Trimesh(mm.vertex_matrix(), mm.face_matrix(), process=False)
print("thighs moved together and merged; watertight:", m.is_watertight)


def check(mesh, label):
    from collections import Counter
    c = Counter(Counter(map(tuple, mesh.edges_sorted)).values())
    parts = mesh.split(only_watertight=False)
    print(f"  [{label}] watertight={mesh.is_watertight} bad_edges={sum(v for k, v in c.items() if k != 2)} "
          f"parts={len(parts)}")


def keep_largest(mesh):
    parts = mesh.split(only_watertight=False)
    return max(parts, key=lambda p: abs(p.volume)) if len(parts) > 1 else mesh


def union_pml(a, b):
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(a.vertices, a.faces))
    ms.add_mesh(pymeshlab.Mesh(b.vertices, b.faces))
    ms.generate_boolean_union(first_mesh=0, second_mesh=1)
    r = ms.current_mesh()
    return trimesh.Trimesh(r.vertex_matrix(), r.face_matrix(), process=False)


check(m, "after leg move")
m = keep_largest(m)

# close any hairline slivers left along the seam (tiny rounded fill, r = 0.15 mm)
import shapely
SLIVER_R = float(__import__('os').environ.get('SLIVER_R', 0))
slabs = []
for z in (np.arange(THIGH_Z[0], THIGH_Z[3] + 1e-6, 0.05) if SLIVER_R > 0 else []):
    sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        continue
    body = shapely.union_all([p for p in sec.to_2D(to_2D=np.eye(4))[0].polygons_full if p.area > 0.3]).buffer(0)
    add_ = body.buffer(SLIVER_R, quad_segs=16).buffer(-SLIVER_R, quad_segs=16).difference(body)
    gs = [g for g in getattr(add_, "geoms", [add_]) if g.area > 1e-5]
    slabs.append((z, gs))
pieces = []
for (za, fa), (zb, fb) in zip(slabs[:-1], slabs[1:]):
    if fa and fb:
        pa = np.vstack([np.c_[np.asarray(g.exterior.coords), np.full(len(g.exterior.coords), za)] for g in fa])
        pb = np.vstack([np.c_[np.asarray(g.exterior.coords), np.full(len(g.exterior.coords), zb)] for g in fb])
        pieces.append(trimesh.Trimesh(np.vstack([pa, pb])).convex_hull)
if pieces:
    import manifold3d as mf

    def to_mf(t):
        return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32),
                                   tri_verts=np.asarray(t.faces, np.uint32)))
    sliver = mf.Manifold.batch_boolean([to_mf(pc) for pc in pieces], mf.OpType.Add)
    out = (to_mf(m) + sliver).to_mesh()
    m = keep_largest(trimesh.Trimesh(out.vert_properties[:, :3], out.tri_verts, process=False))
    print(f"  closed hairline slivers ({len(pieces)} slices)")
check(m, "after sliver fill")
SEAM_PTS = None


# ---------- 1b. refill the back pocket between the thighs ----------
# From behind, the thighs meet in a deep V pocket (up to ~1.8 mm deep right
# under the butt) that reads as an arch/tongue. Cut out the pocket's walls and
# refill the opening with a fair, minimum-curvature surface that meets the
# surrounding body smoothly. The butt cleft above Z ~24.4 is kept.
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import shapely
from patch import refill

POCKET_Z = tuple(float(x) for x in __import__('os').environ.get('POCKET_Z', '18.2,24.7').split(','))
POCKET_MIN_DEPTH = float(__import__("os").environ.get("POCKET_MIN_DEPTH", 0.08))
T_DIR = np.array([-0.522, 0.853])


def pocket_mask(mesh):
    v = mesh.vertices
    mask = np.zeros(len(v), bool)
    for z in np.arange(POCKET_Z[0], POCKET_Z[1], 0.04):
        sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if sec is None:
            continue
        body = shapely.union_all([p for p in sec.to_2D(to_2D=np.eye(4))[0].polygons_full if p.area > 0.3]).buffer(0)
        hull = body.convex_hull
        near = np.flatnonzero(np.abs(v[:, 2] - z) < 0.02)
        if not len(near):
            continue
        recess = shapely.distance(hull.exterior, shapely.points(v[near, :2]))
        on_back = (v[near, :2] - SEAM_C) @ T_DIR > 0.2
        inside = shapely.contains_xy(hull, v[near, 0], v[near, 1])
        mask[near[(recess > POCKET_MIN_DEPTH) & on_back & inside]] = True
    return mask


# where the thighs meet (bottom of the pocket), recorded before the refill
from notch import back_notch_profile
_prof = [r for r in back_notch_profile(m, np.arange(POCKET_Z[0] - 0.3, POCKET_Z[1] + 0.31, 0.1)) if r]
CZ = np.array([r["z"] for r in _prof])
CB = np.array([r["bottom"] for r in _prof])
CU = np.array([r["u"] for r in _prof])

REFILL = __import__('os').environ.get('REFILL', '0') == '1'
if REFILL:
    # re-triangulate the pocket and a margin around it first, so the cut is clean
    mask0 = pocket_mask(m)
    dist0 = cKDTree(m.vertices[mask0]).query(m.vertices)[0]
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(m.vertices, m.faces, v_scalar_array=(dist0 < 0.7).astype(float)))
    ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
    ms.compute_selection_transfer_vertex_to_face(inclusive=True)
    ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(REMESH_LEN),
                                            selectedonly=True, featuredeg=180)
    cm = ms.current_mesh()
    m = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=False)
    mask = pocket_mask(m)
    # make the cut region solid: everything within 0.15 mm of a pocket vertex
    mask = cKDTree(m.vertices[mask]).query(m.vertices)[0] < 0.15
    print("back pocket: refilling", int(mask.sum()), "vertices")
    m, POCKET_FREE = refill(m, mask, edge_len=REMESH_LEN, grow=1, blend_rings=4)
    m = keep_largest(m)
    check(m, "after pocket refill")


# ---------- 2. calves ----------
def slim_calves(mesh, z0, zpeak, z1, amount):
    v = mesh.vertices.copy()
    zs = np.arange(z0, z1 + 0.25, 0.25)
    cents = []
    for sec in mesh.section_multiplane([0, 0, 0], [0, 0, 1], list(zs)):
        ps = sorted([p for p in sec.polygons_full if p.area > 0.3], key=lambda p: p.centroid.y)
        cents.append([(p.centroid.x, p.centroid.y) for p in ps] if len(ps) == 2 else None)
    ok = [i for i, cc in enumerate(cents) if cc is not None]
    zs_ok = zs[ok]
    legs = [np.array([cents[i][j] for i in ok]) for j in (0, 1)]
    sel = (v[:, 2] > z0) & (v[:, 2] < z1)
    z = v[sel, 2]
    w = ramp(z, z0, zpeak, zpeak, z1)
    cl = [np.column_stack([np.interp(z, zs_ok, L[:, 0]), np.interp(z, zs_ok, L[:, 1])]) for L in legs]
    d = [np.linalg.norm(v[sel, :2] - ci, axis=1) for ci in cl]
    cc = np.where((d[0] < d[1])[:, None], cl[0], cl[1])
    v[sel, :2] = cc + (v[sel, :2] - cc) * (1 - amount * w)[:, None]
    mesh.vertices = v
    return mesh


m = slim_calves(m, **CALF)

# ---------- 3. bust ----------
v = m.vertices.copy()
d = np.linalg.norm(v - BUST_C, axis=1)
front = smoothstep((BUST_C[1] + 0.3 - v[:, 1]) / 0.6)    # front of the chest only
wb = falloff(d, *BUST_R) * front
v += (v - BUST_C) * (BUST_SCALE * wb)[:, None]
m.vertices = v

# ---------- 4. remesh edited areas, then smooth ----------
# hip: only a thin strip around the sharp edges where the thighs meet and under
# the butt, so the thighs' outer surfaces keep their original look
v = m.vertices
ang = np.degrees(m.face_adjacency_angles)
mid = v[m.face_adjacency_edges].mean(1)
sharp = mid[(weight(mid, HIP) > 0) & (ang > 20)]
tree = cKDTree(sharp) if len(sharp) else None
q = np.zeros(len(v))
if tree is not None:
    q = (tree.query(v)[0] < 0.6).astype(float)
POCKET_MOVED = None
crescent0 = mid[(mid[:, 1] > 0.6) & (mid[:, 2] > 22.8) & (mid[:, 2] < 25.2)
                & (np.abs(mid[:, 0] - 0.3) < 2.2) & (ang > 12)]
if len(crescent0):
    q = np.maximum(q, (cKDTree(crescent0).query(v)[0] < ARCH_R[1] + 0.35).astype(float))
for (c, _, r1) in (JAW, BUN, NOSE):
    q = np.maximum(q, (np.linalg.norm(v - c, axis=1) < r1 + 0.2).astype(float))
ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(v, m.faces, v_scalar_array=q))
ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
ms.compute_selection_transfer_vertex_to_face(inclusive=False)
ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(REMESH_LEN),
                                        selectedonly=True, featuredeg=180)
mm = ms.current_mesh()
m = keep_largest(trimesh.Trimesh(mm.vertex_matrix(), mm.face_matrix(), process=False))
check(m, "after remesh")


# hips: smooth a thin strip around the sharp edges (crease + arch)
v = m.vertices
ang = np.degrees(m.face_adjacency_angles)
mid = v[m.face_adjacency_edges].mean(1)
sharp = mid[(weight(mid, HIP) > 0) & (ang > 20)]
w_hip = np.zeros(len(v))
if len(sharp):
    dist = cKDTree(sharp).query(v)[0]
    w_hip = falloff(dist, 0.15, 0.55) * weight(v, HIP)
print("hip smoothing over", int((w_hip > 0).sum()), "vertices")
m = smooth(m, w_hip, laplace=int(__import__('os').environ.get('DESPIKE', 30)))   # melts small spikes first
m = implicit_smooth(m, w_hip, lam=float(__import__('os').environ.get('HIP_LAM', 30)))
m = smooth(m, w_hip, taubin=20)

# arch: the crescent edge where the bottom of the left cheek meets the thigh
# behind it. Round it into a soft fold with a stronger pass along that curve.
v = m.vertices
ang = np.degrees(m.face_adjacency_angles)
mid = v[m.face_adjacency_edges].mean(1)
crescent = crescent0
if len(crescent) and ARCH_LAM > 0:
    dist = cKDTree(crescent).query(v)[0]
    w_arch = falloff(dist, ARCH_R[0], ARCH_R[1])
    print("arch rounding over", int((w_arch > 0).sum()), "vertices")
    m = smooth(m, w_arch, laplace=ARCH_LAP)
    m = implicit_smooth(m, w_arch, lam=ARCH_LAM)
    m = smooth(m, w_arch, taubin=20)

v = m.vertices
w_jaw = weight(v, JAW) * falloff(v[:, 2] - JAW_ZMAX[0], 0, JAW_ZMAX[1] - JAW_ZMAX[0])
m = smooth(m, w_jaw, laplace=12, taubin=60)
v = m.vertices
m = smooth(m, weight(v, BUN), laplace=60, taubin=60)
v = m.vertices
m = smooth(m, weight(v, NOSE), laplace=25, taubin=20)

# ---------- 5. scale ----------
m.apply_translation([0, 0, -m.bounds[0][2]])
m.apply_scale(305.0 / m.extents[2])
check(m, "final")
m.export(dst)
print("scaled to", m.extents.round(1), "mm; watertight:", m.is_watertight, "faces:", len(m.faces))
