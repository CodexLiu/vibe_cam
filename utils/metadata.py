from __future__ import annotations

from typing import Dict

import numpy as np
import trimesh


async def compute_mesh_metadata(filepath: str) -> Dict[str, object]:
    loaded = trimesh.load(filepath)
    if isinstance(loaded, trimesh.Scene):
        scene = loaded
        bodies = []
        total_volume = 0.0
        total_area = 0.0
        total_tris = 0
        for name, geom in scene.geometry.items():
            if not isinstance(geom, trimesh.Trimesh):
                continue
            dims = tuple(float(x) for x in geom.extents)
            vol = float(geom.volume) if geom.volume is not None else 0.0
            area = float(geom.area)
            tris = int(geom.faces.shape[0])
            total_volume += vol
            total_area += area
            total_tris += tris
            bodies.append({
                "name": str(name),
                "dimensions_mm": dims,
                "volume_mm3": vol,
                "surface_area_mm2": area,
                "triangles": tris,
            })
        bounds = scene.bounds if scene.bounds is not None else np.array([[0,0,0],[0,0,0]])
        overall_dims = tuple(float(x) for x in (bounds[1] - bounds[0]))
        return {
            "units": "unknown",
            "body_count": len(bodies),
            "overall_dimensions_mm": overall_dims,
            "total_volume_mm3": total_volume,
            "total_surface_area_mm2": total_area,
            "total_triangles": total_tris,
            "bodies": bodies,
        }
    else:
        mesh = loaded
        extents = tuple(float(x) for x in mesh.extents)
        volume = float(mesh.volume) if mesh.volume is not None else 0.0
        surface_area = float(mesh.area)
        num_triangles = int(mesh.faces.shape[0])
        return {
            "units": "unknown",
            "body_count": 1,
            "overall_dimensions_mm": extents,
            "total_volume_mm3": volume,
            "total_surface_area_mm2": surface_area,
            "total_triangles": num_triangles,
            "bodies": [{
                "name": "body_0",
                "dimensions_mm": extents,
                "volume_mm3": volume,
                "surface_area_mm2": surface_area,
                "triangles": num_triangles,
            }],
        }


