import numpy as np, shapely, trimesh
from shapely.geometry import Point

def back_notch_profile(m, zs, t_dir=np.array([-0.522, 0.853]), c=np.array([0.82, 0.52])):
    """Per slice: deepest point of the back pocket, its depth, and the outward direction."""
    out = []
    for z in zs:
        sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if sec is None:
            out.append(None); continue
        body = shapely.union_all([p for p in sec.to_2D(to_2D=np.eye(4))[0].polygons_full if p.area > 0.3]).buffer(0)
        pock = body.convex_hull.difference(body)
        gs = [g for g in getattr(pock, "geoms", [pock]) if g.area > 0.02]
        if not gs:
            out.append(None); continue
        # back pocket = the one furthest along t (toward the butt)
        g = max(gs, key=lambda g: (np.array(g.centroid.coords[0]) - c) @ t_dir)
        if (np.array(g.centroid.coords[0]) - c) @ t_dir < 0.3:
            out.append(None); continue
        hull_edge = body.convex_hull.exterior
        bnd = np.asarray(g.exterior.coords)
        d = np.array([hull_edge.distance(Point(p)) for p in bnd])
        i = np.argmax(d)
        bottom = bnd[i]
        mouth = np.asarray(hull_edge.interpolate(hull_edge.project(Point(bottom))).coords[0])
        u = mouth - bottom
        depth = np.linalg.norm(u)
        width = g.area / max(depth, 1e-6) * 2          # rough mouth width
        out.append(dict(z=z, bottom=bottom, u=u / max(depth, 1e-9), depth=depth, width=width))
    return out

if __name__ == "__main__":
    m = trimesh.load("b2.stl"); m.apply_scale(1 / 6.1)
    for r in back_notch_profile(m, np.arange(20.5, 25.6, 0.25)):
        if r: print(f"z={r['z']:.2f} bottom={r['bottom'].round(2)} out={r['u'].round(2)} depth={r['depth']:.2f} width~{r['width']:.2f}")
