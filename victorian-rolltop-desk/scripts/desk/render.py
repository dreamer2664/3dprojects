"""
render.py — Cycles render package for the desk.

    blender -b <master.blend> --python scripts/desk/render.py -- \
        --shot hero --res 1920x1080 --samples 64 --out renders/victorian-rolltop-desk

Two lighting environments:
  * study   — warm late-Victorian room: window light, wood floor, plaster wall
  * studio  — neutral grey seamless, three-point softboxes, no atmosphere
Every still is a real render of the built model; nothing is composited or photographed.
"""
import bpy
import os
import sys
import math
import json
import argparse
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--shot", default="hero")
ap.add_argument("--res", default="1920x1080")
ap.add_argument("--samples", type=int, default=64)
ap.add_argument("--out", default="renders/victorian-rolltop-desk")
ap.add_argument("--suffix", default="")
ap.add_argument("--env", default="study", choices=["study", "studio"])
ap.add_argument("--exr", action="store_true")
args = ap.parse_args(argv)

W, H = [int(v) for v in args.res.lower().split("x")]


# ----------------------------------------------------------------------------- helpers
def coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def norm_name(name):
    return name.replace(".", "_").replace(":", "_").replace(" ", "_").upper()


def obj(name):
    return bpy.data.objects.get(name)


def find(needle):
    for o in bpy.data.objects:
        if needle in o.name:
            return o
    return None


def make_camera(name, loc, target, lens=55.0, ortho=None):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    if ortho:
        cam_data.type = 'ORTHO'
        cam_data.ortho_scale = ortho
    cam = bpy.data.objects.new(name, cam_data)
    coll("CAMERAS_LIGHTS_AND_STAGING").objects.link(cam)
    cam.location = Vector(loc)
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return cam


def area_light(name, loc, target, size, power, color=(1.0, 0.96, 0.90), shape='RECTANGLE',
               size_y=None, spread=math.pi):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = power
    ld.color = color
    ld.shape = shape
    ld.size = size
    if size_y:
        ld.size_y = size_y
    ld.spread = spread
    ob = bpy.data.objects.new(name, ld)
    coll("CAMERAS_LIGHTS_AND_STAGING").objects.link(ob)
    ob.location = Vector(loc)
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


def material(name, color, rough=0.6, metallic=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    return m


# ----------------------------------------------------------------------------- environment
def build_environment(kind):
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("W")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if kind == "studio":
        bg.inputs[0].default_value = (0.055, 0.056, 0.060, 1)
        bg.inputs[1].default_value = 1.0
    else:
        bg.inputs[0].default_value = (0.075, 0.070, 0.062, 1)
        bg.inputs[1].default_value = 1.0

    if bpy.data.objects.get("ENV_FLOOR"):
        return

    # floor
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0.4, 0))
    floor = bpy.context.object
    floor.name = "ENV_FLOOR"
    if kind == "studio":
        floor.data.materials.append(material("ENV_STUDIO_FLOOR", (0.36, 0.355, 0.35), 0.62))
    else:
        floor.data.materials.append(material("ENV_OAK_FLOOR_BOARDS", (0.115, 0.068, 0.036),
                                            0.38))
    # back wall
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 2.6, 2.5),
                                     rotation=(math.pi / 2, 0, 0))
    wall = bpy.context.object
    wall.name = "ENV_BACK_WALL"
    if kind == "studio":
        wall.data.materials.append(material("ENV_STUDIO_WALL", (0.30, 0.30, 0.30), 0.75))
    else:
        wall.data.materials.append(material("ENV_STUDY_WALL", (0.145, 0.130, 0.105), 0.85))
    for o in (floor, wall):
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll("CAMERAS_LIGHTS_AND_STAGING").objects.link(o)

    if kind == "study":
        # window light: a big soft area light behind-left, warm, plus bounce/fill
        area_light("LIGHT_WINDOW", (-2.6, 0.9, 1.9), (0, 0.45, 0.85), 2.2, 320,
                   color=(1.0, 0.93, 0.82), size_y=2.6)
        area_light("LIGHT_FILL", (2.4, -1.5, 1.5), (0, 0.4, 0.8), 2.0, 95,
                   color=(0.95, 0.96, 1.0))
        area_light("LIGHT_KICK", (0.6, 2.2, 2.0), (0, 0.4, 0.95), 1.4, 110,
                   color=(1.0, 0.95, 0.88))
        area_light("LIGHT_FLOOR_BOUNCE", (0.0, -1.2, 0.05), (0, 0.4, 0.9), 1.6, 28,
                   color=(1.0, 0.92, 0.82))
    else:
        area_light("LIGHT_KEY", (-1.9, -2.0, 2.4), (0, 0.4, 0.8), 2.4, 260,
                   color=(1.0, 0.985, 0.97))
        area_light("LIGHT_FILL", (2.3, -1.4, 1.6), (0, 0.4, 0.8), 2.6, 90,
                   color=(0.96, 0.97, 1.0))
        area_light("LIGHT_RIM", (0.4, 2.4, 2.3), (0, 0.45, 1.0), 1.8, 120,
                   color=(1.0, 0.99, 0.96))
        area_light("LIGHT_TOPBACK", (0.0, 1.6, 2.6), (0, 0.45, 1.1), 1.6, 70)
    # a soft overhead for both
    area_light("LIGHT_TOP", (0.0, 0.55, 2.35), (0, 0.45, 0.95), 2.0, 80,
               color=(1.0, 0.97, 0.92), size_y=1.2)


# ----------------------------------------------------------------------------- shots
DESK_C = (0.0, 0.38, 0.72)

# direction, target, lens, ortho_scale(optional), fill
# directions are unit-ish vectors from the target toward the camera
SHOTS = {
    "hero":            ((-0.72, -0.90, 0.42), (0.0, 0.34, 0.70), 62, None, 0.90),
    "hero_closed":     ((-0.72, -0.90, 0.42), (0.0, 0.34, 0.70), 62, None, 0.90),
    "hero_open":       ((-0.66, -0.95, 0.38), (0.0, 0.34, 0.74), 62, None, 0.90),
    "front":           ((0.0, -1.0, 0.06), (0.0, 0.34, 0.70), 64, None, 0.94),
    "front_ortho":     ((0.0, -1.0, 0.0), (0.0, 0.40, 0.70), 60, 1.60, 0.96),
    "side":            ((1.0, 0.0, 0.06), (0.0, 0.40, 0.70), 64, None, 0.94),
    "side_ortho":      ((1.0, 0.02, 0.0), (0.0, 0.40, 0.70), 60, 1.60, 0.96),
    "rear":            ((0.68, 0.92, 0.34), (0.0, 0.40, 0.70), 62, None, 0.90),
    "rear_straight":   ((0.0, 1.0, 0.06), (0.0, 0.40, 0.72), 64, None, 0.94),
    "top":             ((0.0, -0.18, 1.0), (0.0, 0.40, 0.74), 55, None, 0.92),
    "interior":        ((0.0, -1.0, 0.30), (0.0, 0.30, 0.99), 58, None, 0.72),
    "interior_high":   ((-0.45, -0.95, 0.42), (0.0, 0.30, 0.99), 55, None, 0.70),
    "tambour":         ((0.20, -1.0, 0.16), (0.02, 0.06, 1.05), 80, None, 0.62),
    "tambour_track":   ((-0.85, -0.55, 0.30), (-0.52, 0.24, 1.16), 90, None, 0.42),
    "posting_slot":    ((0.05, -1.0, 0.10), (0.0, 0.05, 1.06), 100, None, 0.30),
    "lock":            ((0.0, -1.0, 0.10), (0.0, 0.06, 0.87), 95, None, 0.26),
    "drawer_open":     ((-0.55, -0.85, 0.20), (-0.50, 0.10, 0.55), 72, None, 0.40),
    "hardware":        ((-0.35, -1.0, 0.18), (-0.30, 0.02, 0.72), 90, None, 0.30),
    "grain":           ((-0.25, -1.0, 0.12), (-0.15, 0.10, 0.98), 105, None, 0.20),
    "panel":           ((0.95, -0.55, 0.10), (0.76, 0.30, 0.44), 85, None, 0.34),
    "writing":         ((0.15, -0.95, 0.42), (0.0, 0.18, 0.80), 62, None, 0.55),
    "castor":          ((0.30, -1.0, 0.16), (0.70, 0.10, 0.09), 90, None, 0.22),
    "explode_interior": ((0.0, -1.0, 0.55), (0.0, 0.30, 1.00), 50, None, 0.86),
    "explode_tambour":  ((0.0, -1.0, 0.35), (0.0, 0.28, 1.10), 55, None, 0.70),
    "swatches":        ((0.0, -1.0, 0.16), (2.60, 0.30, 0.80), 85, None, None, 0.62),
}


def scene_bounds(exclude_env=True):
    from mathutils import Vector
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH':
            continue
        if exclude_env and (ob.name.startswith("ENV_") or ob.name.startswith("SWATCH")):
            continue
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], w[i])
                hi[i] = max(hi[i], w[i])
    return lo, hi


def fit_camera(cam, target, fill=0.9):
    """Move the camera along its own view axis until the desk bounding box fills the
    frame by `fill`. Keeps every shot framed from real geometry, not guesswork."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    lo, hi = scene_bounds()
    corners = [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y)
               for z in (lo.z, hi.z)]
    tgt = Vector(target)
    for _ in range(8):
        bpy.context.view_layer.update()      # camera matrices must be current
        d = cam.location - tgt
        maxx = maxy = 0.0
        for c in corners:
            co = world_to_camera_view(sc, cam, c)
            maxx = max(maxx, abs(co.x - 0.5) * 2)
            maxy = max(maxy, abs(co.y - 0.5) * 2)
        worst = max(maxx, maxy)
        if worst < 1e-4:
            break
        factor = worst / fill
        cam.location = tgt + d * factor
    return cam


def setup_camera(shot):
    spec = SHOTS.get(shot, SHOTS["hero"])
    direction, target, lens = spec[0], spec[1], spec[2]
    ortho = spec[3] if len(spec) > 3 else None
    fill = spec[4] if len(spec) > 4 else 0.9
    d = Vector(direction).normalized()
    dist = spec[5] if len(spec) > 5 else (3.0 if (fill or 0) >= 0.95 else 0.95)
    cam = make_camera(f"CAM_{shot}", Vector(target) + d * dist, target, lens=lens,
                      ortho=ortho)
    # only the full-object shots are auto-framed; detail shots use their stated distance
    if ortho is None and (fill or 0) >= 0.95:
        fit_camera(cam, target, fill=fill)
    bpy.context.scene.camera = cam
    return cam


def setup_render():
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = args.samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = os.environ.get("NO_DENOISE","0") != "1"
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 8
    sc.cycles.diffuse_bounces = 4
    sc.cycles.glossy_bounces = 4
    sc.cycles.transmission_bounces = 4
    sc.cycles.transparent_max_bounces = 4
    sc.cycles.use_fast_gi = False
    sc.render.resolution_x = W
    sc.render.resolution_y = H
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'OPEN_EXR' if args.exr else 'PNG'
    sc.render.image_settings.color_depth = '16' if args.exr else '8'
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.view_settings.exposure = 0.0


def main():
    build_environment(args.env)
    setup_camera(args.shot)
    setup_render()
    out = args.out if os.path.isabs(args.out) else os.path.join(os.getcwd(), args.out)
    os.makedirs(out, exist_ok=True)
    ext = "exr" if args.exr else "png"
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(out, f"{args.shot}{args.suffix}.{ext}")
    print("RENDER_START", args.shot, f"{W}x{H}", args.samples, flush=True)
    bpy.ops.render.render(write_still=True)
    print("RENDER_DONE", sc.render.filepath, flush=True)


if __name__ == "__main__":
    main()
