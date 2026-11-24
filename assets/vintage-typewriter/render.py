#!/usr/bin/env blender --python
"""Render all CAM_* cameras with per-camera studio setups."""
import bpy, os, sys, json
from math import radians
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(ROOT, "vintage_typewriter.blend")
OUT = os.path.join(ROOT, "renders")
os.makedirs(OUT, exist_ok=True)

ONLY = None
ENGINE = 'cycles'
argv = sys.argv
if "--only" in argv:
    ONLY = argv[argv.index("--only") + 1]
if "--engine" in argv:
    ENGINE = argv[argv.index("--engine") + 1]

bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene
sc.cycles.device = 'CPU'
if ENGINE == 'eevee':
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.eevee.taa_render_samples = 192
    sc.eevee.use_raytracing = True
    try:
        sc.eevee.ray_tracing_method = 'PROBE'
    except Exception as e:
        print('rt method:', e)
    sc.eevee.use_gtao = True
    sc.eevee.gtao_distance = 0.35
    sc.eevee.gtao_quality = 0.6
else:
    sc.render.engine = 'CYCLES'
    sc.cycles.use_denoising = False
    for vl in sc.view_layers:
        vl.cycles.use_denoising = False
    sc.cycles.filter_width = 1.8
    sc.cycles.max_bounces = 3
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 1
    sc.cycles.volume_bounces = 0
sc.cycles.max_bounces = 4
sc.cycles.caustics_reflective = False
sc.cycles.caustics_refractive = False
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.06
sc.cycles.adaptive_min_samples = 12
sc.view_settings.exposure = 0.05
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_depth = '8'
sc.render.image_settings.compression = 12

world = sc.world
bg = world.node_tree.nodes["Background"]

SETUPS = {
    "HERO":  dict(world=(0.062, 0.060, 0.058), wstr=1.0, floor='dark',
                  key=(10.2, (1.00, 0.97, 0.92)), fill=(6.0, (0.93, 0.96, 1.00)), rim=(14, (1.0, 0.98, 0.94))),
    "DARK":  dict(world=(0.007, 0.007, 0.008), wstr=1.0, floor='dark',
                  key=(4.2, (1.00, 0.95, 0.88)), fill=(0.0, (1, 1, 1)),  rim=(17.5, (0.82, 0.88, 1.0))),
    "WHITE": dict(world=(0.90, 0.90, 0.90),   wstr=2.9, floor='white',
                  key=(13.5, (1.00, 1.00, 1.00)), fill=(9.5, (0.97, 0.98, 1.0)), rim=(7.5, (1, 1, 1))),
    "WARM":  dict(world=(0.026, 0.015, 0.009), wstr=1.0, floor='dark',
                  key=(10.5, (1.00, 0.76, 0.52)), fill=(3.2, (0.88, 0.66, 0.48)), rim=(9.0, (1.0, 0.86, 0.62))),
}

lights = {o.name: o for o in bpy.data.objects if o.type == 'LIGHT'}
floors = {o.name: o for o in bpy.data.objects if o.name.startswith("FLOOR_")}
cameras = [o for o in bpy.data.objects if o.name.startswith("CAM_")]
cameras.sort(key=lambda o: o.name)

EXPO = {"05_top": -0.30, "08_platen": -0.38, "09_ribbon": -0.18, "10_typebars": -0.12,
        "11_carriage_lever": -0.08, "13_white_studio": -0.10, "16_spool_detail": -0.12}
for cam in cameras:
    out_name = cam.name[4:]  # strip CAM_
    if ONLY and out_name != ONLY:
        continue
    sc.view_settings.exposure = 0.05 + EXPO.get(out_name, 0.0)
    setup = SETUPS[cam.get("setup", "HERO")]
    bg.inputs["Color"].default_value = (*setup["world"], 1.0)
    bg.inputs["Strength"].default_value = setup["wstr"]
    for lname, key in (("LIGHT_key", "key"), ("LIGHT_fill", "fill"), ("LIGHT_rim", "rim")):
        e, col = setup[key]
        lights[lname].data.energy = e
        lights[lname].data.color = col
    want_white = setup["floor"] == 'white'
    floors["FLOOR_white"].hide_render = not want_white
    floors["FLOOR_dark"].hide_render = want_white
    # resolution
    if cam.get("macro", False):
        sc.render.resolution_x, sc.render.resolution_y = 2200, 2200
        sc.cycles.samples = 110
    else:
        sc.render.resolution_x, sc.render.resolution_y = 2560, 1440
        sc.cycles.samples = 110
    sc.render.resolution_percentage = 100
    sc.camera = cam
    sc.render.filepath = os.path.join(OUT, out_name + ".png")
    print("RENDER", out_name, sc.render.resolution_x, "x", sc.render.resolution_y, flush=True)
    bpy.ops.render.render(write_still=True)
    print("DONE", out_name, flush=True)
print("ALL_RENDERS_DONE")
