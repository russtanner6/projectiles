#!/usr/bin/env python3
"""Replace the ballerina's head and neck with a new head model.

  1. Cut the old head + upper neck off the body with a cylinder around the neck
     (so the raised arms are untouched).
  2. Trim the new model's shoulders off at its lower neck, scale it so its neck
     matches the body's neck, turn it to face HEAD_TURN degrees, and sink its
     neck OVERLAP mm into the body's neck stub.
  3. Merge into one solid, then re-skin a narrow band around the join so the
     neck flows into the body with no visible seam.

Usage: head_swap.py body.stl head.stl out.stl [HEAD_TURN=deg env]
"""
import os
import sys

import manifold3d as mf
import numpy as np
import pymeshlab
import trimesh
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

body_path, head_path, out_path = sys.argv[1:4]

NECK_AXIS = np.array([2.2, 6.3])      # body neck centre (x, y)
CUT_Z = 247.0                         # body is cut here (mid-neck)
CUT_R = 21.0                          # radius of the cutting cylinder
HEAD_NECK_Z = float(os.environ.get("NECK_Z", 16.5))                    # new model is trimmed at its slimmest neck point
SCALE = float(os.environ.get("HEAD_SCALE", 1.12))      # was 1.25 in v6
FACE_SHRINK = float(os.environ.get("FACE_SHRINK", 0.12))   # face area pulled in by up to 12%
FACE_SMOOTH = float(os.environ.get("FACE_SMOOTH", 60))     # smoothing strength on the face
FACE_SIDE = float(os.environ.get("FACE_SIDE", 125))       # degrees from face centre covered (reaches the ears)
FACE_DIR_SRC = float(os.environ.get("FACE_SRC", -157))  # where the face points in the head file (deg)
FACE_DIR = float(os.environ.get("FACE_DIR", -55))       # target: body front is -90, her left is +X
TILT = float(os.environ.get("TILT", 15))                 # chin up / head back, degrees
OVERLAP = 4.0
BLEND = (CUT_Z - float(os.environ.get('BL_LO', 7)), CUT_Z + float(os.environ.get('BL_HI', 6)))    # Z band re-skinned around the join


def to_mf(t):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32),
                               tri_verts=np.asarray(t.faces, np.uint32)))


def from_mf(g):
    m = g.to_mesh()
    return trimesh.Trimesh(m.vert_properties[:, :3], m.tri_verts, process=False)


body = trimesh.load(body_path, force="mesh")
head = trimesh.load(head_path, force="mesh")

# 1. remove old head: take everything above CUT_Z, keep the piece around the
# neck (arms are separate pieces up there), and subtract its convex hull
top = trimesh.creation.box(extents=[300, 300, 200])
top.apply_translation([0, 0, CUT_Z + 100])
above = from_mf(to_mf(body) ^ to_mf(top)).split(only_watertight=False)
old_head = min(above, key=lambda p: np.hypot(*(p.centroid[:2] - NECK_AXIS)) if abs(p.volume) > 50 else 1e9)
hull = old_head.convex_hull
hull.apply_translation([0, 0, 0])
body_cut = to_mf(body) - (to_mf(hull) ^ to_mf(top))
print(f"old head removed: {abs(old_head.volume):.0f} mm^3")

# 2. prepare new head: trim shoulders, centre the neck, scale, turn, place
box = trimesh.creation.box(extents=[200, 200, 200])
box.apply_translation([0, 0, HEAD_NECK_Z + 100])
h = from_mf(to_mf(head) ^ to_mf(box))
sec = h.section(plane_origin=[0, 0, HEAD_NECK_Z + 0.3], plane_normal=[0, 0, 1])
c = max(sec.to_2D(to_2D=np.eye(4))[0].polygons_full, key=lambda p: p.area).centroid
h.apply_translation([-c.x, -c.y, -HEAD_NECK_Z])

# 2b. smaller, smoother face (in the head file's own coordinates)
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
hv = h.vertices.copy()
hc = np.array([-1.5 + c.x * 0, -1.0]) - np.array([c.x, c.y])      # head axis after centring
dz = hv[:, 2] + HEAD_NECK_Z                                       # back to file heights
ang = np.degrees(np.arctan2(hv[:, 1] - hc[1], hv[:, 0] - hc[0]))
dang = np.abs((ang - FACE_DIR_SRC + 180) % 360 - 180)
def ss(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
wf = ss((85 - dang) / 45) * ss((dz - 18) / 3) * ss((37 - dz) / 4)
hv[:, :2] = hc + (hv[:, :2] - hc) * (1 - FACE_SHRINK * wf)[:, None]
h.vertices = hv
# wide zone: whole face + sides (ears) + jaw down into the neck, remeshed fine
# so it can be smoothed into one soft surface
wz = lambda v, a: ss((FACE_SIDE - a) / 35) * ss((v[:, 2] + HEAD_NECK_Z - 14) / 2) * ss((38 - v[:, 2] - HEAD_NECK_Z) / 4)
def zone(v):
    a = np.abs((np.degrees(np.arctan2(v[:, 1] - hc[1], v[:, 0] - hc[0])) - FACE_DIR_SRC + 180) % 360 - 180)
    return wz(v, a)
q = (zone(h.vertices) > 0.01).astype(float)
ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(h.vertices, h.faces, v_scalar_array=q))
ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
ms.compute_selection_transfer_vertex_to_face(inclusive=True)
ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(0.3),
                                        selectedonly=True, featuredeg=180)
cm = ms.current_mesh()
h = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix())
hv = h.vertices.copy()
wf = zone(hv)
e = h.edges_unique; n = len(hv)
A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
Lh = sp.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A - sp.identity(n)
Mh = (sp.identity(n) - FACE_SMOOTH * sp.diags(wf) @ Lh).tocsc()
hv = np.column_stack([spsolve(Mh, hv[:, k]) for k in range(3)])
for _ in range(20):                       # Taubin pass: removes leftover facets, keeps volume
    hv = hv + 0.5 * wf[:, None] * (Lh @ hv)
    hv = hv - 0.53 * wf[:, None] * (Lh @ hv)
h.vertices = hv
print(f"face: {int((wf > 0.05).sum())} vertices smoothed (face, ears, jaw-to-neck)")
# even, fine triangles on the neck and under the jaw first, so reshaping it
# can't leave streaks from long sliver triangles
_q = ((h.vertices[:, 2] + HEAD_NECK_Z) < float(os.environ.get("JAW_Z", 20.0)) + 3).astype(float)
_ms = pymeshlab.MeshSet()
_ms.add_mesh(pymeshlab.Mesh(h.vertices, h.faces, v_scalar_array=_q))
_ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
_ms.compute_selection_transfer_vertex_to_face(inclusive=True)
_ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(0.25),
                                         selectedonly=True, featuredeg=60)
_cm = _ms.current_mesh()
h = trimesh.Trimesh(_cm.vertex_matrix(), _cm.face_matrix())

# straighten + thin the neck. The head file's neck leans; shift each slice so
# the neck's centre line is vertical (fading to a constant offset above the jaw),
# then thin it radially about that single straight axis.
JAW_Z = float(os.environ.get("JAW_Z", 20.0))
zs = np.arange(HEAD_NECK_Z + 0.1, JAW_Z + 0.01, 0.25)
cs, ds = [], []
for sec2 in h.section_multiplane([0, 0, 0], [0, 0, 1], list(zs - HEAD_NECK_Z)):
    p = max(sec2.polygons_full, key=lambda p: p.area)
    cs.append([p.centroid.x, p.centroid.y]); ds.append(2 * np.sqrt(p.area / np.pi))
cs, ds = np.array(cs), np.array(ds)
fit = np.polyfit(zs, cs, 1)                          # straight-line fit of the neck centre
hv = h.vertices.copy()
fzv = hv[:, 2] + HEAD_NECK_Z
zc = np.clip(fzv, zs[0], JAW_Z)
off = np.column_stack([np.polyval(fit[:, 0], zc), np.polyval(fit[:, 1], zc)])
hv[:, :2] -= off                                      # neck axis now vertical through (0,0)
NECK_D_BASE = float(os.environ.get("NECK_D_BASE", 0))
if NECK_D_BASE:
    NECK_D_SLIM = float(os.environ.get("NECK_D_SLIM", NECK_D_BASE))
    # smooth model of the neck's width (slices near the jaw can pick up hair and
    # jump around, which made the squeeze uneven); fit only below the jaw
    good = zs <= JAW_Z - 1.0
    dfit = np.polyval(np.polyfit(zs[good], ds[good], 2), np.clip(fzv, zs[0], JAW_Z - 1.0))
    t = np.clip((fzv - HEAD_NECK_Z) / (JAW_Z - 1.5 - HEAD_NECK_Z), 0, 1)
    tgt = (NECK_D_BASE + (NECK_D_SLIM - NECK_D_BASE) * t) / SCALE
    k = tgt / dfit
    k = 1 + (k - 1) * ss((JAW_Z + 1.0 - fzv) / 3.0)   # fade out smoothly into the jaw
    hv[:, :2] *= k[:, None]
    print(f"neck straightened, thinned to {NECK_D_BASE}->{NECK_D_SLIM} mm")
h.vertices = hv
# smooth the transition band (top of the neck, under the jaw and hairline)
# where the squeeze fades out, so no ridges are left
if NECK_D_BASE:
    hv = h.vertices.copy()
    fzv = hv[:, 2] + HEAD_NECK_Z
    wb = ss((fzv - (JAW_Z - 4)) / 2) * ss((JAW_Z + 3 - fzv) / 2)
    e = h.edges_unique; n = len(hv)
    A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
    Lb = sp.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A - sp.identity(n)
    for _ in range(int(os.environ.get("BAND_SMOOTH", 40))):
        hv = hv + 0.5 * wb[:, None] * (Lb @ hv)
        hv = hv - 0.53 * wb[:, None] * (Lb @ hv)
h.vertices = hv

# narrower head: squeeze ear-to-ear by HEAD_NARROW, fading in above the neck so
# the neck still matches the body
NARROW = float(os.environ.get("HEAD_NARROW", 0.0))
if NARROW:
    ua = np.radians(FACE_DIR_SRC + 90)
    u = np.array([np.cos(ua), np.sin(ua), 0.0])
    hv = h.vertices.copy()
    fz = ss((hv[:, 2] + HEAD_NECK_Z - 19) / 4)          # 0 on the neck, 1 from the jaw up
    hv -= np.outer((hv @ u) * NARROW * fz, u)
    h.vertices = hv
    print(f"head narrowed {NARROW*100:.0f}% ear-to-ear")
h.apply_scale(SCALE)
h.apply_transform(trimesh.transformations.rotation_matrix(np.radians(FACE_DIR - FACE_DIR_SRC), [0, 0, 1]))
f = np.array([np.cos(np.radians(FACE_DIR)), np.sin(np.radians(FACE_DIR)), 0.0])
# chin-up tilt as a gradual bend through the upper neck: the rotation angle
# ramps from 0 to TILT across the band, always about one fixed pivot, so the
# mapping stays smooth (no torn triangles)
hv = h.vertices
axis = np.cross(f, [0, 0, 1]); axis /= np.linalg.norm(axis)
b0 = float(os.environ.get("BEND_LO", 2.0)); b1 = (JAW_Z - HEAD_NECK_Z) * SCALE + 2.0
pivot = np.array([0.0, 0.0, b0])
th = np.radians(TILT) * ss((hv[:, 2] - b0) / (b1 - b0))
rel = hv - pivot
c_, s_ = np.cos(th)[:, None], np.sin(th)[:, None]
h.vertices = pivot + rel * c_ + np.cross(axis, rel) * s_ + np.outer(rel @ axis, axis) * (1 - c_)
h.apply_translation([NECK_AXIS[0], NECK_AXIS[1], CUT_Z - OVERLAP])
if os.environ.get("DEBUG_HEAD"): h.export(os.environ["DEBUG_HEAD"])
print(f"new head: {h.extents.round(1)} mm after scaling x{SCALE}, top at Z {h.bounds[1][2]:.1f}")

# thin the body's neck stub to match (fades to nothing at the shoulders)
BODY_NECK_D = float(os.environ.get("BODY_NECK_D", 0))
body_cut_mesh = from_mf(body_cut)
if BODY_NECK_D:
    bv = body_cut_mesh.vertices.copy()
    rr0 = np.hypot(bv[:, 0] - NECK_AXIS[0], bv[:, 1] - NECK_AXIS[1])
    sel = (bv[:, 2] > 238) & (rr0 < 10)
    z = bv[sel, 2]
    k = 1 + (BODY_NECK_D / 13.5 - 1) * ss((z - 241.5) / 4) * ss((9.5 - rr0[sel]) / 2.5)
    bv[sel, :2] = NECK_AXIS + (bv[sel, :2] - NECK_AXIS) * k[:, None]
    body_cut_mesh.vertices = bv
    body_cut = to_mf(body_cut_mesh)
    print(f"body neck thinned toward {BODY_NECK_D} mm")

# 3. merge
merged = from_mf(body_cut + to_mf(h))
parts = merged.split(only_watertight=False)
print("after merge parts:", [round(abs(p.volume)) for p in parts])
merged = max(parts, key=lambda p: abs(p.volume))

# 4. blend the join: fine triangles around it, then cut out and fair a band
v = merged.vertices
rr = np.hypot(v[:, 0] - NECK_AXIS[0], v[:, 1] - NECK_AXIS[1])
near = (v[:, 2] > BLEND[0] - 2) & (v[:, 2] < BLEND[1] + 2) & (rr < 16)
ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(v, merged.faces, v_scalar_array=near.astype(float)))
ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
ms.compute_selection_transfer_vertex_to_face(inclusive=True)
ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(0.35),
                                        selectedonly=True, featuredeg=180)
cm = ms.current_mesh()
merged = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=False)
v = merged.vertices
rr = np.hypot(v[:, 0] - NECK_AXIS[0], v[:, 1] - NECK_AXIS[1])
# smooth a soft band around the join (a full ring, so smooth rather than cut)
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
zc = (BLEND[0] + BLEND[1]) / 2
hw = (BLEND[1] - BLEND[0]) / 2
t = np.clip(1 - np.abs(v[:, 2] - zc) / hw, 0, 1)
t = np.clip(t * 1.6, 0, 1)                      # flat full-strength middle
w = t * t * (3 - 2 * t) * np.clip((14 - rr) / 2, 0, 1)
e = merged.edges_unique
n = len(v)
A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
deg = np.asarray(A.sum(1)).ravel()
L = sp.diags(1 / np.maximum(deg, 1)) @ A - sp.identity(n)
M = (sp.identity(n) - float(os.environ.get("BLEND_LAM", 60)) * sp.diags(w) @ L).tocsc()
vv = np.column_stack([spsolve(M, v[:, k]) for k in range(3)])
for _ in range(30):
    vv = vv + 0.5 * w[:, None] * (L @ vv)
    vv = vv - 0.53 * w[:, None] * (L @ vv)
merged.vertices = vv
# clean up any sliver the merge left at the join
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
