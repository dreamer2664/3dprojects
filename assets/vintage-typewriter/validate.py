#!/usr/bin/env blender --python
"""Quality-control checks for vintage_typewriter.blend and .glb"""
import bpy, json, math, sys, os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(ROOT, "vintage_typewriter.blend")
GLB = os.path.join(ROOT, "vintage_typewriter.glb")

mode = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else "blend"

report = {}
if mode == "blend":
    # scene already open when passed as first arg
    objs = list(bpy.data.objects)
    meshes = [o for o in objs if o.type == 'MESH' and not o.name.startswith("FLOOR_")]
    # overall bounding box
    lo = Vector((1e9, 1e9, 1e9)); hi = -lo.copy()
    for o in meshes:
        for corner in o.bound_box:
            w = o.matrix_world @ Vector(corner)
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    dims = hi - lo
    key_objs = [o for o in objs if o.name.startswith("KEY_")
                and not o.name.endswith("_legend") and not o.name.endswith("_skirt")
                and o.name != "KEY_STEMS_ALL"]
    report = {
        "objects_total": len(objs),
        "mesh_objects": len(meshes),
        "materials": len(bpy.data.materials),
        "images": len(bpy.data.images),
        "images_packed": sum(1 for i in bpy.data.images if i.packed_file),
        "collections": [c.name for c in bpy.data.collections],
        "key_count": len(key_objs),
        "bbox_m": [round(v, 4) for v in dims],
        "bbox_mm": [round(v * 1000, 1) for v in dims],
        "cameras": sorted(o.name for o in objs if o.type == 'CAMERA'),
        "lights": sorted(o.name for o in objs if o.type == 'LIGHT'),
        "render_engine_saved": bpy.context.scene.render.engine,
    }
    # material assignment coverage
    unassigned = [o.name for o in meshes if len(o.data.materials) == 0]
    report["meshes_without_material"] = unassigned
    # textures referenced but missing
    missing = [i.name for i in bpy.data.images if i.source == 'FILE' and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))]
    report["missing_image_files"] = missing
else:  # glb
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=GLB)
    objs = list(bpy.data.objects)
    meshes = [o for o in objs if o.type == 'MESH']
    report = {
        "glb_objects": len(objs),
        "glb_meshes": len(meshes),
        "glb_materials": len(bpy.data.materials),
        "glb_images": len(bpy.data.images),
        "glb_size_bytes": os.path.getsize(GLB),
    }
print("VALIDATE", json.dumps(report, indent=1))
