#!/usr/bin/env python3
"""Head swap with a rebuilt neck.

The body is cut just above the shoulders and the new head just below its jaw.
A brand-new neck is built between them as a smooth, straight, gently tapered
tube whose ends match the body's and the head's cross-sections exactly, so
nothing has to be stretched. Then the two joins are blended.

Usage: neck_rebuild.py body.stl head.stl out.stl   (settings via env vars)
"""
import os
import sys

import manifold3d as mf
import numpy as np
import pymeshlab
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
import trimesh

body_path, head_path, out_path = sys.argv[1:4]
E = lambda k, d: float(os.environ.get(k, d))

NECK_AXIS = np.array([2.2, 6.3])
BODY_CUT = E("BODY_CUT", 242.0)        # body kept below this (top of the shoulders)
NECK_LEN = E("NECK_LEN", 10.0)         # visible neck length from BODY_CUT to the head
NECK_SLIM = E("NECK_SLIM", 12.2)       # neck diameter at its slimmest (mm)
HEAD_CUT = E("HEAD_CUT", 18.5)         # head file trimmed below this (just under the jaw)
SCALE = E("HEAD_SCALE", 1.24)
NARROW = E("HEAD_NARROW", 0.10)
FACE_SRC = E("FACE_SRC", -118)
FACE_DIR = E("FACE_DIR", -55)
TILT = E("TILT", 15)
OVL = 3.0                              # tube overlap into body and head


def to_mf(t):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32),
                               tri_verts=np.asarray(t.faces, np.uint32)))


def from_mf(g):
    m = g.to_mesh()
    return trimesh.Trimesh(m.vert_properties[:, :3], m.tri_verts, process=False)


def ss(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def section(mesh, z, near=None):
    s = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    ps = s.to_2D(to_2D=np.eye(4))[0].polygons_full
    if near is not None:
        return min(ps, key=lambda p: np.hypot(p.centroid.x - near[0], p.centroid.y - near[1]))
    return max(ps, key=lambda p: p.area)


def box_above(z, keep_above=True):
    b = trimesh.creation.box(extents=[400, 400, 400])
    b.apply_translation([0, 0, z + 200 if keep_above else z - 200])
    return b


body = trimesh.load(body_path, force="mesh")
head = trimesh.load(head_path, force="mesh")

# ---- body: remove the old head and neck above BODY_CUT (arms are untouched) ----
above = from_mf(to_mf(body) ^ to_mf(box_above(BODY_CUT))).split(only_watertight=False)
old = min(above, key=lambda p: np.hypot(*(p.centroid[:2] - NECK_AXIS)) if abs(p.volume) > 50 else 1e9)
body_cut = to_mf(body) - (to_mf(old.convex_hull.copy()).__xor__(to_mf(box_above(BODY_CUT))))
bsec = section(from_mf(body_cut), BODY_CUT - 0.3, near=NECK_AXIS)
b_c = np.array([bsec.centroid.x, bsec.centroid.y])
b_r = np.sqrt(bsec.area / np.pi)
print(f"body neck at cut: centre {b_c.round(2)}, diameter {2*b_r:.1f} mm")

# ---- head: trim under the jaw, centre, narrow, scale, aim, tilt ----
h = from_mf(to_mf(head) ^ to_mf(box_above(HEAD_CUT)))
hsec = section(h, HEAD_CUT + 0.2)
h.apply_translation([-hsec.centroid.x, -hsec.centroid.y, -HEAD_CUT])
if NARROW:
    ua = np.radians(FACE_SRC + 90)
    u = np.array([np.cos(ua), np.sin(ua), 0.0])
    v = h.vertices.copy()
    v -= np.outer((v @ u) * NARROW * ss(v[:, 2] / 3.0), u)
    h.vertices = v
h.apply_scale(SCALE)
h.apply_transform(trimesh.transformations.rotation_matrix(np.radians(FACE_DIR - FACE_SRC), [0, 0, 1]))
f = np.array([np.cos(np.radians(FACE_DIR)), np.sin(np.radians(FACE_DIR)), 0.0])
h.apply_transform(trimesh.transformations.rotation_matrix(np.radians(TILT), np.cross(f, [0, 0, 1]), [0, 0, 0]))
z_top = BODY_CUT + NECK_LEN
h.apply_translation([b_c[0], b_c[1], z_top - 0.5 + E("HEAD_DROP", 0)])
h = from_mf(to_mf(h) ^ to_mf(box_above(z_top)))             # flat, horizontal cut
hsec2 = section(h, z_top + 0.15, near=b_c)
h_c = np.array([hsec2.centroid.x, hsec2.centroid.y])
print(f"head neck at cut: diameter {2*np.sqrt(hsec2.area/np.pi):.1f} mm; head top at Z {h.bounds[1][2]:.1f}")


def radial(poly, c, ang):
    """distance from c to the polygon boundary along each angle (star-shaped)."""
    from shapely.geometry import LineString
    out = []
    for a_ in ang:
        far = c + 60 * np.array([np.cos(a_), np.sin(a_)])
        inter = LineString([c, far]).intersection(poly.exterior)
        pts = np.array([g.coords[0] for g in getattr(inter, "geoms", [inter])]) if not inter.is_empty else np.array([c])
        out.append(np.max(np.linalg.norm(pts - c, axis=1)))
    return np.array(out)


# ---- new neck: lofted between the real body and head cross-sections ----
NZ, NA = 90, 144
ang = np.linspace(0, 2 * np.pi, NA, endpoint=False)
ring = np.stack([np.cos(ang), np.sin(ang)], 1)
rb_ = radial(bsec, b_c, ang)
rh_ = radial(hsec2, h_c, ang)
z0, z1 = BODY_CUT - OVL, z_top + OVL
zs = np.linspace(z0, z1, NZ)
t = np.clip((zs - BODY_CUT) / NECK_LEN, 0, 1)
blend = ss(t)
mean_mid = 0.5 * (rb_.mean() + rh_.mean())
slim = min(1.0, (NECK_SLIM / 2) / mean_mid)
pinch = 1 - (1 - slim) * np.sin(np.pi * t) ** 2         # 1 at both ends, slimmest mid-neck
def lowpass(r, keep):
    F = np.fft.rfft(r)
    F[keep + 1:] = 0
    return np.fft.irfft(F, len(r))


rb_s, rh_s = lowpass(rb_, 2), lowpass(rh_, 2)        # smooth ovals
END = E("END_ZONE", 2.0)                            # mm over which the ends match exactly
rows = []
for z, bl, pc in zip(zs, blend, pinch):
    shape = (1 - bl) * rb_s + bl * rh_s
    exact_b = ss((BODY_CUT + END - z) / END)        # 1 at/below the body cut
    exact_h = ss((z - (z_top - END)) / END)         # 1 at/above the head cut
    rr_ = shape + exact_b * (rb_ - rb_s) + exact_h * (rh_ - rh_s)
    cc_ = (1 - bl) * b_c + bl * h_c
    rr_ = rr_ * pc
    # the hidden overlap ends shrink inward so they can't poke out as a ledge
    if z > z_top:
        rr_ = rr_ * (1 - 0.35 * (z - z_top) / OVL)
    elif z < BODY_CUT:
        rr_ = rr_ * (1 - 0.35 * (BODY_CUT - z) / OVL)
    rows.append(np.column_stack([cc_ + rr_[:, None] * ring, np.full(NA, z)]))
verts = np.concatenate(rows)
faces = []
for i in range(NZ - 1):
    for j in range(NA):
        a_, b_ = i * NA + j, i * NA + (j + 1) % NA
        c_, d_ = a_ + NA, b_ + NA
        faces += [[a_, b_, d_], [a_, d_, c_]]
verts = np.vstack([verts, [[*b_c, z0], [*h_c, z1]]])
bot, top = len(verts) - 2, len(verts) - 1
for j in range(NA):
    faces.append([bot, (j + 1) % NA, j])
    faces.append([top, (NZ - 1) * NA + j, (NZ - 1) * NA + (j + 1) % NA])
tube = trimesh.Trimesh(verts, np.array(faces), process=True)
if tube.volume < 0:
    tube.invert()

merged = from_mf(body_cut + to_mf(tube) + to_mf(h))
merged = max(merged.split(only_watertight=False), key=lambda p: abs(p.volume))

# ---- blend the two joins: fine triangles, then soft local smoothing ----
v = merged.vertices
rr = np.hypot(v[:, 0] - b_c[0], v[:, 1] - b_c[1])
near = (rr < 14) & (np.abs(v[:, 2] - BODY_CUT) < 4) | (rr < 11) & (np.abs(v[:, 2] - z_top) < 4)
ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(v, merged.faces, v_scalar_array=near.astype(float)))
ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
ms.compute_selection_transfer_vertex_to_face(inclusive=True)
ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(0.3),
                                        selectedonly=True, featuredeg=180)
cm = ms.current_mesh()
merged = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=False)
v = merged.vertices
rr = np.hypot(v[:, 0] - b_c[0], v[:, 1] - b_c[1])
w = (ss((2.2 - np.abs(v[:, 2] - BODY_CUT)) / 1.5) * ss((12 - rr) / 2)
     + ss((2.2 - np.abs(v[:, 2] - z_top)) / 1.5) * ss((9.5 - rr) / 2))
w = np.clip(w, 0, 1)
e = merged.edges_unique
n = len(v)
A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
L = sp.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A - sp.identity(n)
M = (sp.identity(n) - E("JOIN_LAM", 15) * sp.diags(w) @ L).tocsc()
vv = np.column_stack([spsolve(M, v[:, k]) for k in range(3)])
for _ in range(15):
    vv = vv + 0.5 * w[:, None] * (L @ vv)
    vv = vv - 0.53 * w[:, None] * (L @ vv)
merged.vertices = vv

ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(merged.vertices, merged.faces))
ms.meshing_remove_duplicate_faces()
ms.meshing_remove_null_faces()
ms.meshing_repair_non_manifold_edges()
ms.meshing_repair_non_manifold_vertices()
ms.meshing_close_holes(maxholesize=50)
cm = ms.current_mesh()
merged = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix())
parts = merged.split(only_watertight=False)
merged = max(parts, key=lambda p: abs(p.volume))
merged.export(out_path)
print("watertight:", merged.is_watertight, "parts:", len(parts), "size:", merged.extents.round(1))
