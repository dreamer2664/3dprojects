#!/usr/bin/env python3
"""Render one inspection camera from the saved master .blend.

Usage: blender -b -P scripts/render_views.py -- CAMERA OUT.png WIDTH HEIGHT SAMPLES
"""
import bpy
import os
import sys

args = sys.argv[sys.argv.index("--") + 1:]
cam_name, out, w, h, samples = args[0], args[1], int(args[2]), int(args[3]), int(args[4])
BLEND = "/home/user/3dprojects/assets/1899-bluthner-grand-piano/1899_bluthner_grand_piano_master.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
scene.camera = bpy.data.objects[cam_name]
# Interior inspection views remove the open lid so the frame/strings/action
# are not occluded; the hero and product views keep it intact.
if cam_name in {"CAM_INTERIOR_TOP", "CAM_ACTION", "CAM_MACRO_STRINGS"}:
    lid = bpy.data.objects.get("Lid — rosewood with inlaid border")
    if lid:
        lid.hide_render = True
        for child in lid.children:
            child.hide_render = True
scene.render.resolution_x = w
scene.render.resolution_y = h
scene.render.resolution_percentage = 100
scene.cycles.samples = samples
scene.cycles.use_denoising = False  # preserve thin strings / filigree; also avoids OOM
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = out
os.makedirs(os.path.dirname(out), exist_ok=True)
print("RENDER_START", cam_name, w, h, samples, flush=True)
bpy.ops.render.render(write_still=True)
print("RENDER_DONE", out, flush=True)
