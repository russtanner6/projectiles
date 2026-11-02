"""Cut out a bad region and refill it with a fair (minimum-curvature) surface."""
import numpy as np
import pymeshlab
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
import trimesh


def _adj(mesh):
    e = mesh.edges_unique
    n = len(mesh.vertices)
    a = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])),
                      shape=(n, n)).tocsr()
    deg = np.asarray(a.sum(1)).ravel()
    return sp.diags(1 / np.maximum(deg, 1)) @ a


def refill(mesh, vert_mask, edge_len=0.04, grow=1, blend_rings=3):
    """Delete faces touching vert_mask (grown by `grow` rings), close the hole,
    refine the patch, and solve a bilaplacian (thin-plate) fairing for it with
    everything else held fixed, so it meets the surroundings smoothly."""
    m = mesh.copy()
    sel = vert_mask.copy()
    A = _adj(m)
    for _ in range(grow):
        sel = sel | (A @ sel.astype(float) > 0)
    fsel = sel[m.faces].any(axis=1)
    keep = ~fsel
    m = trimesh.Trimesh(m.vertices, m.faces[keep], process=False)
    m.remove_unreferenced_vertices()
    n_before = len(m.vertices)
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(m.vertices, m.faces))
    ms.meshing_close_holes(maxholesize=100000, newfaceselected=True, selfintersection=False, refinehole=True)
    ms.meshing_isotropic_explicit_remeshing(iterations=8, targetlen=pymeshlab.PureValue(edge_len),
                                            selectedonly=True, featuredeg=180)
    # remember which vertices belong to the new patch (selected faces' vertices)
    fs = ms.current_mesh().face_selection_array()
    cm = ms.current_mesh()
    out = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=False)
    patch_v = np.zeros(len(out.vertices), bool)
    patch_v[out.faces[fs].ravel()] = True
    # boundary of the patch stays fixed: free = patch vertices not touching unselected faces
    # free = the new patch plus a few rings of the surrounding surface, so the
    # patch and its border are faired together and no seam is left
    A2 = _adj(out)
    free = patch_v.copy()
    for _ in range(blend_rings):
        free = free | (A2 @ free.astype(float) > 0)
    # keep an outer ring fixed (two rings, so slope is continuous too)
    L = A2 - sp.identity(len(out.vertices))
    K = (L @ L).tocsr()
    P = np.flatnonzero(free)
    Fx = np.flatnonzero(~free)
    KPP = K[P][:, P].tocsc()
    KPF = K[P][:, Fx]
    v = out.vertices.copy()
    for k in range(3):
        v[P, k] = spsolve(KPP, -KPF @ v[Fx, k])
    out.vertices = v
    return out, free
