#!/usr/bin/env python3
"""v5 refinements on top of Russ's Blender edit (full scale, on base, mm).

  1. Trim definition: find the step edges of the raised trim (waist V band,
     straps) as sharp creases on the torso, and lift only the raised side of
     each step by TRIM_LIFT, so the steps get taller and read more clearly.
     Bust and body facets are soft creases and are left alone.
  2. Slimmer fingers: pull the finger surface part of the way toward a heavily
     smoothed copy of the hand (which collapses toward each finger's centre
     line). That slims fingers smoothly without roughening the surface.

Usage: refine_v5.py in.stl out.stl
"""
import os
import sys

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from scipy.spatial import cKDTree
import trimesh

TRIM_LIFT = float(os.environ.get("TRIM_LIFT", 0.5))       # mm
TRIM_ANGLE = float(os.environ.get("TRIM_ANGLE", 28))      # crease sharper than this = trim edge
TRIM_REACH = (1.4, 2.2)                                   # full / zero distance from a trim edge
FINGER_SLIM = float(os.environ.get("FINGER_SLIM", 0.2))   # fraction pulled toward the centre line
FINGER_Z = (300.5, 304.5)                                 # fade-in from palm to fingers
MAX_MOVE = float(os.environ.get("MAX_MOVE", 0.7))                                           # mm per side

src, dst = sys.argv[1], sys.argv[2]
m = trimesh.load(src, force="mesh")


def smoothstep(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def laplacian(mesh):
    e = mesh.edges_unique
    n = len(mesh.vertices)
    a = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])),
                      shape=(n, n)).tocsr()
    deg = np.asarray(a.sum(1)).ravel()
    return sp.diags(1 / np.maximum(deg, 1)) @ a - sp.identity(n)


def smoothed(mesh, lam):
    L = laplacian(mesh)
    M = (sp.identity(len(mesh.vertices)) - lam * L).tocsc()
    return np.column_stack([spsolve(M, mesh.vertices[:, k]) for k in range(3)])


def region(mesh, face_mask):
    sub = mesh.submesh([np.flatnonzero(face_mask)], append=True)
    dist, idx = cKDTree(mesh.vertices).query(sub.vertices)
    return sub, idx, dist < 1e-6


# ---------- 1. trim definition ----------
import pymeshlab
tc = m.triangles_center
sub, idx, ok = region(m, (tc[:, 2] > 163) & (tc[:, 2] < 252) & (np.abs(tc[:, 0]) < 27))
ang = np.degrees(sub.face_adjacency_angles)
mid = sub.vertices[sub.face_adjacency_edges].mean(1)
edges = mid[ang > TRIM_ANGLE]
t_ = cKDTree(edges)
edges = edges[np.array([len(t_.query_ball_point(p, 1.5)) >= 5 for p in edges])]
# even, fine triangles around the trim first, so the lift moves smoothly
q = (cKDTree(edges).query(m.vertices)[0] < TRIM_REACH[1] + 1.0).astype(float)
ms = pymeshlab.MeshSet()
ms.add_mesh(pymeshlab.Mesh(m.vertices, m.faces, v_scalar_array=q))
ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
ms.compute_selection_transfer_vertex_to_face(inclusive=False)
ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(0.25),
                                        selectedonly=True, featuredeg=25)
cm = ms.current_mesh()
m = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=False)
tc = m.triangles_center
sub, idx, ok = region(m, (tc[:, 2] > 163) & (tc[:, 2] < 252) & (np.abs(tc[:, 0]) < 27))
vs = smoothed(sub, 40)
relief = np.einsum("ij,ij->i", sub.vertices - vs, sub.vertex_normals)
smooth_n = trimesh.Trimesh(vs, sub.faces, process=False).vertex_normals   # stable directions
d_edge = cKDTree(edges).query(sub.vertices)[0]
w = smoothstep((TRIM_REACH[1] - d_edge) / (TRIM_REACH[1] - TRIM_REACH[0]))
w *= smoothstep(relief / 0.15)
zv = sub.vertices[:, 2]
w *= smoothstep((zv - 165) / 3) * smoothstep((250 - zv) / 3)
L = laplacian(sub)
for _ in range(6):                                  # neighbours move together
    w = w + 0.5 * (L @ w)
v = m.vertices.copy()
v[idx[ok]] += smooth_n[ok] * (TRIM_LIFT * w[ok])[:, None]
m.vertices = v
print(f"trim: {len(edges)} edge points, {int((w > 0.05).sum())} vertices lifted up to {TRIM_LIFT} mm")

# ---------- 2. slimmer fingers ----------
tc = m.triangles_center
hand, hidx, hok = region(m, tc[:, 2] > 290)
hv = hand.vertices
toward = smoothed(hand, 60) - hv
move = FINGER_SLIM * toward
mag = np.linalg.norm(move, axis=1, keepdims=True)
move *= np.minimum(1, MAX_MOVE / np.maximum(mag, 1e-9))
move *= smoothstep((hv[:, 2] - FINGER_Z[0]) / (FINGER_Z[1] - FINGER_Z[0]))[:, None]
v = m.vertices.copy()
v[hidx[hok]] += move[hok]
m.vertices = v
print(f"fingers: surface moved up to {np.linalg.norm(move, axis=1).max():.2f} mm "
      f"(median {np.median(np.linalg.norm(move, axis=1)[hv[:, 2] > 305]):.2f} mm on the fingers)")

m.export(dst)
print("watertight:", m.is_watertight, "size:", m.extents.round(1))
