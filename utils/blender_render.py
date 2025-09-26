import os
import math
import asyncio


async def render_eight_views(input_path: str, outdir: str, size: int = 512) -> None:
    import bpy
    import addon_utils
    import mathutils

    if not os.path.isdir(outdir):
        os.makedirs(outdir, exist_ok=True)

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".stl":
        addon_utils.enable("io_mesh_stl", default_set=True, persistent=True)
    if ext == ".obj":
        addon_utils.enable("io_scene_obj", default_set=True, persistent=True)

    if ext == ".stl":
        bpy.ops.import_mesh.stl(filepath=input_path)
    elif ext == ".obj":
        if hasattr(bpy.ops, "wm") and hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=input_path)
        else:
            bpy.ops.import_scene.obj(filepath=input_path)
    elif ext in (".gltf", ".glb"):
        bpy.ops.import_scene.gltf(filepath=input_path)
    else:
        bpy.ops.import_scene.gltf(filepath=input_path)

    imported = [obj for obj in bpy.context.scene.objects if obj.type in {"MESH"}]
    if not imported:
        return

    depsgraph = bpy.context.evaluated_depsgraph_get()
    world_pts = []
    for o in imported:
        eo = o.evaluated_get(depsgraph)
        mat = eo.matrix_world
        for corner in o.bound_box:
            p = mat @ mathutils.Vector(corner)
            world_pts.append(p)
    xs = [p.x for p in world_pts]
    ys = [p.y for p in world_pts]
    zs = [p.z for p in world_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)
    center = ((min_x + max_x) * 0.5, (min_y + max_y) * 0.5, (min_z + max_z) * 0.5)
    size_x = max_x - min_x
    size_y = max_y - min_y
    size_z = max_z - min_z
    max_dim = max(size_x, size_y, size_z)
    radius = max(1.0, max_dim * 1.5)

    mat = bpy.data.materials.new(name="PartRed")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.9, 0.1, 0.1, 1.0)
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.35
    for o in imported:
        if o.data and hasattr(o.data, "materials"):
            o.data.materials.clear()
            o.data.materials.append(mat)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
    target = bpy.context.active_object

    for l in list(bpy.data.lights):
        bpy.data.lights.remove(l, do_unlink=True)
    light_data = bpy.data.lights.new(name="KeyLight", type='SUN')
    light_data.energy = 5.0
    light_obj = bpy.data.objects.new(name="KeyLight", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (center[0] + radius, center[1] + radius, center[2] + radius)

    fill_light_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_light_data.energy = 300.0
    fill_light = bpy.data.objects.new(name="FillLight", object_data=fill_light_data)
    bpy.context.collection.objects.link(fill_light)
    fill_light.location = (center[0] - radius, center[1] - radius, center[2] + radius)

    for c in list(bpy.data.cameras):
        bpy.data.cameras.remove(c, do_unlink=True)
    cam_data = bpy.data.cameras.new(name="Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    cam_data.clip_start = max(0.001, radius * 0.01)
    cam_data.clip_end = radius * 50.0

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.color = (0.15, 0.5, 0.7)

    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    def set_cam_spherical(az_deg: float, el_deg: float, r: float):
        az = math.radians(az_deg)
        el = math.radians(el_deg)
        x = center[0] + r * math.cos(el) * math.cos(az)
        y = center[1] + r * math.cos(el) * math.sin(az)
        z = center[2] + r * math.sin(el)
        cam_obj.location = (x, y, z)
        bpy.context.view_layer.update()

    views = [
        (0, 20), (45, 20), (90, 20), (135, 20),
        (180, 20), (225, 20), (270, 20), (315, 20),
    ]

    for i, (az, el) in enumerate(views):
        set_cam_spherical(az, el, radius)
        scene.render.filepath = os.path.join(outdir, f"view_{i:02d}.png")
        bpy.ops.render.render(write_still=True)
    


