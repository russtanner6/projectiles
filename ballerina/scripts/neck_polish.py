#!/usr/bin/env python3
"""Final gentle smoothing over the whole visible neck (shoulders to jaw)."""
import sys, numpy as np, pymeshlab, trimesh, scipy.sparse as sp
from scipy.sparse.linalg import spsolve
src, dst = sys.argv[1:3]
import os
C = np.array([2.55, 6.2]); Z0, Z1 = 239.5, float(os.environ.get("Z1", 254.5))
def ss(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
m = trimesh.load(src)
v = m.vertices; rr = np.hypot(v[:, 0] - C[0], v[:, 1] - C[1])
q = ((v[:, 2] > Z0 - 3) & (v[:, 2] < Z1 + 3) & (rr < 13)).astype(float)
ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(v, m.faces, v_scalar_array=q))
ms.compute_selection_by_condition_per_vertex(condselect="q > 0.5")
ms.compute_selection_transfer_vertex_to_face(inclusive=True)
ms.meshing_isotropic_explicit_remeshing(iterations=6, targetlen=pymeshlab.PureValue(0.3), selectedonly=True, featuredeg=180)
cm = ms.current_mesh(); m = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix())
v = m.vertices; rr = np.hypot(v[:, 0] - C[0], v[:, 1] - C[1])
w = ss((v[:, 2] - Z0) / 2.5) * ss((Z1 - v[:, 2]) / 2.5) * ss((11 - rr) / 2.5)
e = m.edges_unique; n = len(v)
A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
L = sp.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A - sp.identity(n)
vv = v.copy()
for _ in range(60):                      # Taubin: smooths without shrinking the neck
    vv = vv + 0.5 * w[:, None] * (L @ vv)
    vv = vv - 0.53 * w[:, None] * (L @ vv)
m.vertices = vv
m.export(dst); print("watertight", m.is_watertight, "parts", len(m.split(only_watertight=False)))
