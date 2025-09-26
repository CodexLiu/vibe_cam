import argparse
import asyncio
import os
import subprocess
import tempfile
from pathlib import Path

import dotenv
from utils.metadata import compute_mesh_metadata
from utils.step_to_stl_gmsh import convert_step_to_stl_with_gmsh

from utils.ai import generate_quote_from_images


def _find_blender_binary() -> str:
    from shutil import which
    p = "/Applications/Blender.app/Contents/MacOS/Blender"
    if os.path.exists(p):
        return p
    try:
        out = subprocess.check_output(["mdfind", "kMDItemCFBundleIdentifier == 'org.blenderfoundation.blender'"]).decode().strip().splitlines()
        if out:
            return os.path.join(out[0], "Contents", "MacOS", "Blender")
    except Exception:
        pass
    b = which("blender")
    if b:
        return b
    raise RuntimeError("Blender not found")


def _render_views(model_path: str, outdir: str, size: int = 640) -> list[str]:
    blender = _find_blender_binary()
    pyexpr = (
        "import sys; "
        f"sys.path.insert(0, {repr(str(Path.cwd()))}); "
        "import asyncio; "
        "from utils.blender_render import render_eight_views; "
        f"asyncio.run(render_eight_views({repr(model_path)}, {repr(outdir)}, {int(size)}))"
    )
    cmd = [blender, "--background", "--python-expr", pyexpr]
    subprocess.check_call(cmd)
    imgs = sorted(str(p) for p in Path(outdir).glob("view_*.png"))
    return imgs


def _ensure_glb(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    if ext in (".gltf", ".glb"):
        return filepath
    if ext in (".stl", ".obj"):
        import trimesh
        mesh = trimesh.load(filepath, force='mesh')
        glb = str(Path(filepath).with_suffix(".glb"))
        mesh.export(glb)
        return glb
    if ext in (".step", ".stp"):
        stl = str(Path(filepath).with_suffix(".stl"))
        convert_step_to_stl_with_gmsh(filepath, stl)
        import trimesh
        mesh = trimesh.load(stl, force='mesh')
        glb = str(Path(filepath).with_suffix(".glb"))
        mesh.export(glb)
        return glb
    return filepath


async def _run(material: str, filepath: str) -> None:
    dotenv.load_dotenv(".env.local")
    glb = _ensure_glb(filepath)
    with tempfile.TemporaryDirectory() as td:
        images = _render_views(glb, td, size=640)
        views = [
            "az=0 el=20",
            "az=45 el=20",
            "az=90 el=20",
            "az=135 el=20",
            "az=180 el=20",
            "az=225 el=20",
            "az=270 el=20",
            "az=315 el=20",
        ]
        metadata = await compute_mesh_metadata(glb)
        data = await generate_quote_from_images(images, views, material, metadata=metadata)
        import json as _json
        print(_json.dumps(data))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--material", required=True)
    ap.add_argument("--filepath", required=True)
    args = ap.parse_args()
    asyncio.run(_run(args.material, args.filepath))


if __name__ == "__main__":
    main()


