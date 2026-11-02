#!/usr/bin/env python3
"""Attach a head-and-neck bust to the body without reshaping its neck.

The bust is moved as one rigid piece (scale, turn, tilt): its neck is never
stretched or bent. Its shoulder flare is buried inside her upper chest, so the
only join is low at the base of the neck, where it is blended.

Usage: bust_swap.py body.stl bust.stl out.stl   (settings via env vars)
"""
import os
import sys

import manifold3d as mf
import numpy as np
import pymeshlab
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
import trimesh

body_path, bust_path, out_path = sys.argv[1:4]
E = lambda k, d: float(os.environ.get(k, d))

NECK_AXIS = np.array([2.2, 6.3])
BODY_CUT = E("BODY_CUT", 241.0)    # her old neck/head removed above this
SEAT_Z = E("SEAT_Z", 12.0)         # bust height (file units) placed at BODY_CUT
BUST_CUT = E("BUST_CUT", 7.0)      # bust kept above this (file units)
SCALE = E("SCALE", 1.2)
FACE_SRC = E("FACE_SRC", -125)
FACE_DIR = E("FACE_DIR", -55)
TILT = E("TILT", 12)


def to_mf(t):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32),
                               tri_verts=np.asarray(t.faces, np.uint32)))


def from_mf(g):
    m = g.to_mesh()
    return trimesh.Trimesh(m.vert_properties[:, :3], m.tri_verts, process=False)


def ss(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def above(z):
    b = trimesh.creation.box(extents=[400, 400, 400])
    b.apply_translation([0, 0, z + 200])
    return b


body = trimesh.load(body_path, force="mesh")
bust = trimesh.load(bust_path, force="mesh")

# remove her old neck and head (arms untouched)
pieces = from_mf(to_mf(body) ^ to_mf(above(BODY_CUT))).split(only_watertight=False)
old = min(pieces, key=lambda p: np.hypot(*(p.centroid[:2] - NECK_AXIS)) if abs(p.volume) > 50 else 1e9)
body_cut = to_mf(body) - (to_mf(old.convex_hull) ^ to_mf(above(BODY_CUT)))

# bust: trim the bottom, centre its neck, then rigid scale / turn / tilt
b = from_mf(to_mf(bust) ^ to_mf(above(BUST_CUT)))
s = b.section(plane_origin=[0, 0, SEAT_Z], plane_normal=[0, 0, 1])
p = max(s.to_2D(to_2D=np.eye(4))[0].polygons_full, key=lambda q: q.area)
b.apply_translation([-p.centroid.x, -p.centroid.y, -SEAT_Z])
# straighten: rotate the whole bust (rigidly) so its neck stands vertical
zs_ = np.arange(SEAT_Z - 1, SEAT_Z + 8, 0.5)
cs_ = []
for s_ in b.section_multiplane([0, 0, 0], [0, 0, 1], list(zs_)):
    pp = max(s_.polygons_full, key=lambda q: q.area); cs_.append([pp.centroid.x, pp.centroid.y])
lean = np.polyfit(zs_, np.array(cs_), 1)[0]
# keep the natural forward lean; remove only the sideways part
fd = np.array([np.cos(np.radians(FACE_SRC)), np.sin(np.radians(FACE_SRC))])
side = lean - (lean @ fd) * fd
lean = side * E("SIDE_FIX", 1.0)
axis_v = np.array([lean[0], lean[1], 1.0]); axis_v /= np.linalg.norm(axis_v)
if E("STRAIGHTEN", 1):
    b.apply_transform(trimesh.geometry.align_vectors(axis_v, [0, 0, 1]))
    print(f"neck straightened by {np.degrees(np.arccos(axis_v[2])):.1f} deg")
b.apply_scale(SCALE)
b.apply_transform(trimesh.transformations.rotation_matrix(np.radians(FACE_DIR - FACE_SRC), [0, 0, 1]))
f = np.array([np.cos(np.radians(FACE_DIR)), np.sin(np.radians(FACE_DIR)), 0.0])
b.apply_transform(trimesh.transformations.rotation_matrix(np.radians(TILT), np.cross(f, [0, 0, 1]), [0, 0, 0]))
b.apply_translation([NECK_AXIS[0], NECK_AXIS[1], E("SEAT_AT", BODY_CUT)])
# taper the bust's buried bottom into a downward cone so it has no flat ledge
# that could sit proud of her chest and leave a horizontal crack
CR, CS = E("CONE_R", 8.6), E("CONE_SLOPE", 1.6)
zc0 = E("SEAT_AT", BODY_CUT)
r_bot = max(CR - CS * 8, 0.5)
cone = trimesh.creation.cone(radius=CR + CS * 60, height=60 + 8, sections=96)  # apex up
cone.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))  # apex down
cone.apply_translation([NECK_AXIS[0], NECK_AXIS[1], zc0 - CR / CS + 60 + 8 - (60 + 8) + (CR / CS) + 0])
# place so radius = CR at z = zc0: apex at zc0 - CR/CS
apex_z = zc0 - CR / CS
cone = trimesh.creation.cone(radius=CS * 80, height=80, sections=96)
cone.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
cone.apply_translation([NECK_AXIS[0], NECK_AXIS[1], apex_z + 80])
keep_top = above(E('SEAT_AT', BODY_CUT) + 1.0)
b = from_mf(to_mf(b) ^ (to_mf(cone) + to_mf(keep_top)))   # cone only shapes the buried bottom
print(f"bust: {b.extents.round(1)} mm, top at Z {b.bounds[1][2]:.1f}")

merged = from_mf(body_cut + to_mf(b))
merged = max(merged.split(only_watertight=False), key=lambda q: abs(q.volume))

# fill the slits where the bust's neck base meets her chest: in each slice of
# the join band, a rounded closing fills narrow grooves; slices are joined with
# convex hulls into one filler that is unioned in
import shapely
FR = E("FILL_R", 1.2)
fz0, fz1 = E("F_LO", BODY_CUT - 6), E("F_HI", BODY_CUT + 2)
slabs = []
for z in np.arange(fz0, fz1 + 1e-6, 0.1):
    sec_ = merged.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec_ is None:
        continue
    polys = [p_ for p_ in sec_.to_2D(to_2D=np.eye(4))[0].polygons_full
             if p_.distance(shapely.Point(*NECK_AXIS)) < 15]
    if not polys:
        continue
    g = shapely.union_all(polys).buffer(0)
    add = g.buffer(FR, quad_segs=16).buffer(-FR, quad_segs=16).difference(g)
    add = add.intersection(shapely.Point(*NECK_AXIS).buffer(E("FILL_RAD", 10.5)))
    gs = [x for x in getattr(add, "geoms", [add]) if x.area > 1e-4]
    slabs.append((z, gs))
fill = []
for (za, fa), (zb, fb) in zip(slabs[:-1], slabs[1:]):
    if fa and fb:
        pa = np.vstack([np.c_[np.asarray(x.exterior.coords), np.full(len(x.exterior.coords), za)] for x in fa])
        pb = np.vstack([np.c_[np.asarray(x.exterior.coords), np.full(len(x.exterior.coords), zb)] for x in fb])
        fill.append(to_mf(trimesh.Trimesh(np.vstack([pa, pb])).convex_hull))
if fill:
    merged = from_mf(to_mf(merged) + mf.Manifold.batch_boolean(fill, mf.OpType.Add))
    merged = max(merged.split(only_watertight=False), key=lambda q: abs(q.volume))
    print(f"join slits filled ({len(fill)} slices)")

# blend only the low join (base of the neck / top of the shoulders)
JZ0, JZ1 = E("J_LO", BODY_CUT - 4), E("J_HI", BODY_CUT + 2.5)
v = merged.vertices
rr = np.hypot(v[:, 0] - NECK_AXIS[0], v[:, 1] - NECK_AXIS[1])
q = ((v[:, 2] > JZ0 - 2) & (v[:, 2] < JZ1 + 2) & (rr < 22)).astype(float)
ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(v, merged.faces, v_scalar_array=q))
ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
ms.compute_selection_transfer_vertex_to_face(inclusive=True)
ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(0.35),
                                        selectedonly=True, featuredeg=180)
cm = ms.current_mesh()
merged = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=False)
v = merged.vertices
rr = np.hypot(v[:, 0] - NECK_AXIS[0], v[:, 1] - NECK_AXIS[1])
w = ss((v[:, 2] - JZ0) / 1.5) * ss((JZ1 - v[:, 2]) / 1.5) * ss((20 - rr) / 4)
e = merged.edges_unique
n = len(v)
A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
L = sp.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A - sp.identity(n)
vv = np.column_stack([spsolve((sp.identity(n) - E("J_LAM", 20) * sp.diags(w) @ L).tocsc(), v[:, k]) for k in range(3)])
for _ in range(30):
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
merged = max(parts, key=lambda q: abs(q.volume))
merged.export(out_path)
print("watertight:", merged.is_watertight, "parts:", len(parts))
