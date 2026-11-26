#!/usr/bin/env python3
"""Export the Blender master to GLB; glTF nodes share the instanced meshes."""
import bpy
import os

BLEND = "/home/user/3dprojects/assets/1899-bluthner-grand-piano/1899_bluthner_grand_piano_master.blend"
OUT = "/home/user/3dprojects/assets/1899-bluthner-grand-piano/1899_bluthner_grand_piano.glb"
bpy.ops.wm.open_mainfile(filepath=BLEND)
# Templates are source geometry, never renderable / exportable parts.
for ob in bpy.data.collections["TEMPLATES"].objects:
    ob.hide_render = True
print("EXPORT_START", flush=True)
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=False,
    export_apply=False,
    export_yup=True,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
    export_image_format="AUTO",
)
print("EXPORT_DONE", OUT, os.path.getsize(OUT), flush=True)
