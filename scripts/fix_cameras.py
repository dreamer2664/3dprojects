#!/usr/bin/env python3
"""Retarget the inspection cameras using the as-built geometry coordinates."""
import bpy
from mathutils import Vector

BLEND = "/home/user/3dprojects/assets/1899-bluthner-grand-piano/1899_bluthner_grand_piano_master.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

FIX = {
    "CAM_INTERIOR_TOP": ((-0.15, 0.95, 1.95), (0.0, -0.35, 0.84), 55),
    "CAM_ACTION": ((-0.60, 1.05, 1.42), (0.0, 0.28, 0.82), 70),
    "CAM_MACRO_HEAD": ((-1.22, 0.92, 1.14), (-0.70, 0.62, 1.05), 72),
    "CAM_MACRO_CHEEK": ((-1.16, 1.06, 1.16), (-0.68, 0.57, 0.97), 72),
    "CAM_MACRO_DESK": ((-0.30, 1.28, 1.34), (0.0, 0.76, 1.01), 75),
    "CAM_MACRO_FALL": ((-0.22, 1.22, 1.02), (0.0, 0.845, 0.90), 90),
    "CAM_MACRO_LEG": ((-1.20, 0.96, 0.56), (-0.64, 0.56, 0.40), 80),
    "CAM_MACRO_LYRE": ((-0.48, 1.24, 0.46), (0.0, 0.70, 0.38), 72),
    "CAM_MACRO_STRINGS": ((-0.32, 0.48, 1.38), (0.0, -0.35, 0.85), 75),
    "CAM_MACRO_GRAIN": ((-1.05, 0.15, 0.98), (-0.78, 0.10, 0.86), 100),
}
for name, (loc, target, lens) in FIX.items():
    ob = bpy.data.objects[name]
    ob.location = loc
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat('-Z', 'Y').to_euler()
    ob.data.lens = lens
    print("CAMERA_FIXED", name, loc, target, lens)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("CAMERAS_SAVED")
