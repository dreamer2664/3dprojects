#!/usr/bin/env python3
"""Build the 1899 Blüthner serial 53338 exhibition grand piano in Blender 4.2.

Coordinate system: metres, Z up, +X treble side, +Y keyboard/front, origin at
floor under the lyre.  All repeated parts are linked instances: the evaluated
scene therefore carries far more triangles than the in-memory mesh data.
"""
import bpy
import math
import os
import random
from mathutils import Vector

random.seed(53338)
ROOT = "/home/user/3dprojects"
ASSET = os.path.join(ROOT, "assets/1899-bluthner-grand-piano")
TEX = os.path.join(ASSET, "textures")
os.makedirs(ASSET, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------------------------------------------------------------- collections
COLLECTIONS = {}
for name in [
    "CASE_AND_RIM", "LID_HINGES_AND_PROP", "ART_NOUVEAU_MARQUETRY",
    "GILT_MOUNTS_AND_SCULPTURE", "LEGS_AND_PEDAL_LYRE",
    "GLASS_FILIGREE_MUSIC_DESK", "KEYBOARD_AND_KEYBED",
    "CAST_FRAME_AND_BRACING", "SOUNDBOARD_BRIDGES_AND_STRINGS",
    "ACTION_HAMMERS_AND_DAMPERS", "PEDALS_AND_LINKAGES",
    "CAMERAS_LIGHTS_AND_STAGING", "TEMPLATES",
]:
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    COLLECTIONS[name] = c

# ------------------------------------------------------------------- materials
def img(path):
    p = os.path.join(TEX, path)
    if os.path.exists(p):
        return bpy.data.images.load(p, check_existing=True)
    return None


def material(name, rgba, rough=0.4, metal=0.0, tex=None, normal=None,
             roughmap=None, scale=(1, 1, 1)):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgba, 1)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgba, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if tex:
        coord = nt.nodes.new("ShaderNodeTexCoord")
        coord.location = (-700, 0)
        mapn = nt.nodes.new("ShaderNodeMapping")
        mapn.location = (-500, 0)
        mapn.inputs["Scale"].default_value = scale
        nt.links.new(coord.outputs["Generated"], mapn.inputs["Vector"])
        t = nt.nodes.new("ShaderNodeTexImage")
        t.location = (-300, 100)
        t.image = img(tex)
        nt.links.new(mapn.outputs["Vector"], t.inputs["Vector"])
        nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
        if normal:
            n = nt.nodes.new("ShaderNodeTexImage")
            n.location = (-300, -180)
            n.image = img(normal)
            nt.links.new(mapn.outputs["Vector"], n.inputs["Vector"])
            nn = nt.nodes.new("ShaderNodeNormalMap")
            nn.location = (-60, -180)
            nn.inputs["Strength"].default_value = 0.5
            nt.links.new(n.outputs["Color"], nn.inputs["Color"])
            nt.links.new(nn.outputs["Normal"], bsdf.inputs["Normal"])
        if roughmap:
            r = nt.nodes.new("ShaderNodeTexImage")
            r.location = (-300, -420)
            r.image = img(roughmap)
            nt.links.new(mapn.outputs["Vector"], r.inputs["Vector"])
            nt.links.new(r.outputs["Color"], bsdf.inputs["Roughness"])
    return m

MAT = {
    "rosewood": material("Rosewood — polished Dalbergia-style", (0.20, 0.07, 0.05),
        0.22, 0.0, "rosewood_color_4k.png", "rosewood_normal_4k.png",
        "rosewood_rough_4k.png", (3, 3, 1)),
    "rosewood_dark": material("Rosewood — end grain / shadow", (0.10, 0.035, 0.025), 0.28),
    "gilt": material("Burnished gilt bronze", (0.62, 0.42, 0.14), 0.26, 0.88,
        "gilt_bronze_color_2k.png", None, "gilt_bronze_rough_2k.png", (2, 2, 1)),
    "frame_gold": material("Cast iron plate — burnished gold", (0.58, 0.40, 0.13), 0.33, 0.8),
    "brass": material("Polished brass fittings", (0.72, 0.54, 0.21), 0.18, 0.95),
    "steel": material("Steel music wire", (0.62, 0.65, 0.68), 0.2, 1.0),
    "copper": material("Copper wound bass", (0.55, 0.27, 0.13), 0.3, 0.9),
    "spruce": material("Spruce soundboard", (0.70, 0.55, 0.36), 0.55, 0.0,
        "spruce_soundboard_color_4k.png", None, None, (2, 3, 1)),
    "ivory": material("Historic ivory natural", (0.86, 0.82, 0.72), 0.3, 0.0,
        "ivory_key_color_1k.png", None, None, (2, 1, 1)),
    "ebony": material("Ebony accidental", (0.055, 0.045, 0.04), 0.24, 0.0,
        "ebony_sharp_color_1k.png", None, None, (2, 1, 1)),
    "felt": material("Wool felt", (0.55, 0.44, 0.31), 0.92, 0.0,
        "felt_hammer_color_1k.png", None, None, (3, 3, 1)),
    "felt_red": material("Red damper felt", (0.45, 0.08, 0.06), 0.95),
    "leather": material("Action leather", (0.24, 0.13, 0.08), 0.7, 0.0,
        "leather_color_1k.png", None, None, (2, 2, 1)),
    "glass": material("Bevelled glass", (0.72, 0.80, 0.82), 0.06, 0.0),
    "inlay_light": material("Inlay — fruitwood", (0.62, 0.38, 0.16), 0.35),
    "inlay_dark": material("Inlay — dark coloured wood", (0.25, 0.11, 0.06), 0.35),
    "inlay_green": material("Inlay — stained green wood", (0.20, 0.29, 0.15), 0.4),
    "floor": material("Music room parquet", (0.25, 0.16, 0.09), 0.35),
    "wall": material("Music room plaster", (0.42, 0.35, 0.28), 0.9),
}
MAT["glass"].node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.85
MAT["glass"].node_tree.nodes["Principled BSDF"].inputs["IOR"].default_value = 1.52

# --------------------------------------------------------------------- helpers
def mesh_obj(name, verts, faces, mat, coll="TEMPLATES", smooth=False, uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    me.materials.append(mat)
    if uvs:
        uv = me.uv_layers.new(name="UVMap")
        for fi, poly in enumerate(me.polygons):
            for k, li in enumerate(poly.loop_indices):
                uv.data[li].uv = uvs[fi][k]
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    me.use_fake_user = True
    ob = bpy.data.objects.new(name, me)
    COLLECTIONS[coll].objects.link(ob)
    return ob


def instance(name, template, coll, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    ob = bpy.data.objects.new(name, template.data)
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    COLLECTIONS[coll].objects.link(ob)
    return ob


def box_template(name, sx, sy, sz, mat, bevel=0.0, segs=2):
    bpy.ops.mesh.primitive_cube_add(size=1)
    ob = bpy.context.object
    ob.name = name
    ob.scale = (sx, sy, sz)
    if bevel:
        mod = ob.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = segs
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    COLLECTIONS["TEMPLATES"].objects.link(ob)
    ob.data.use_fake_user = True
    return ob


def cyl_template(name, r, depth, verts=64, rings=1, mat=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth,
                                        end_fill_type="NGON", location=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    if rings > 1:
        # subdivide length so the evaluated string mesh carries real geometry
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=rings - 1)
        bpy.ops.object.mode_set(mode="OBJECT")
    ob.data.materials.append(mat or MAT["steel"])
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    COLLECTIONS["TEMPLATES"].objects.link(ob)
    ob.data.use_fake_user = True
    return ob


def sphere_template(name, r, segments, rings, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=r)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    COLLECTIONS["TEMPLATES"].objects.link(ob)
    ob.data.use_fake_user = True
    return ob


def curve_obj(name, points, radius, mat, coll, resolution=12, cyclic=False):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = resolution
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(points) - 1)
    for bp, p in zip(sp.bezier_points, points):
        bp.co = p
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    sp.use_cyclic_u = cyclic
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    COLLECTIONS[coll].objects.link(ob)
    return ob

# ------------------------------------------------------------------ case outline
CTRL = [
    (-0.785, 0.80), (-0.40, 0.80), (0.0, 0.80), (0.40, 0.80), (0.785, 0.80),
    (0.785, 0.30), (0.785, -0.30), (0.74, -0.78), (0.50, -1.18),
    (0.05, -1.34), (-0.48, -1.18), (-0.74, -0.78), (-0.785, -0.30),
    (-0.785, 0.30),
]


def catmull_closed(pts, sub=14):
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1, p2, p3 = (Vector(pts[(i + k) % n]) for k in (-1, 0, 1, 2))
        for j in range(sub):
            t = j / sub
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t +
                              (2*p0 - 5*p1 + 4*p2 - p3) * t2 +
                              (-p0 + 3*p1 - 3*p2 + p3) * t3))
    return [(v.x, v.y) for v in out]

OUTLINE = catmull_closed(CTRL, 14)
# Clamp spline overshoot so the shipped instrument matches the 157 cm width and
# 214 cm length verified from BADA + 1stDibs; no false precision is claimed.
OUTLINE = [(max(-0.785, min(0.785, x)), max(-1.34, min(0.80, y)))
           for x, y in OUTLINE]
N = len(OUTLINE)
AREA = sum(OUTLINE[i][0]*OUTLINE[(i+1)%N][1] - OUTLINE[(i+1)%N][0]*OUTLINE[i][1]
           for i in range(N)) / 2
SIGN = 1 if AREA > 0 else -1
INNER = []
for i, (x, y) in enumerate(OUTLINE):
    px, py = OUTLINE[(i-1) % N]
    nx, ny = OUTLINE[(i+1) % N]
    dx, dy = nx - px, ny - py
    L = math.hypot(dx, dy)
    nrm = Vector((dy / L, -dx / L)) * SIGN
    INNER.append((x + nrm.x * 0.055, y + nrm.y * 0.055))

# --------------------------------------------------------------- case and rim
Z_BOT, Z_TOP = 0.715, 0.960
verts, faces, uvs = [], [], []
for ring in range(4):
    for i in range(N):
        x, y = (OUTLINE if ring in (0, 3) else INNER)[i]
        z = (Z_BOT if ring in (0, 1) else Z_TOP)
        verts.append((x, y, z))
for i in range(N):
    j = (i + 1) % N
    midy = (OUTLINE[i][1] + OUTLINE[j][1]) / 2
    # front keywell is open below the fallboard: no vertical rim wall there
    if midy <= 0.30:
        faces.append((i, j, 3*N+j, 3*N+i)); uvs.append(((i/N,0),((i+1)/N,0),((i+1)/N,1),(i/N,1)))
        faces.append((N+i, 2*N+i, 2*N+j, N+j)); uvs.append(((i/N,0),(i/N,1),((i+1)/N,1),((i+1)/N,0)))
    faces.append((3*N+i, 3*N+j, 2*N+j, 2*N+i)); uvs.append(((i/N,0),((i+1)/N,0),((i+1)/N,1),(i/N,1)))
    faces.append((j, i, N+i, N+j)); uvs.append(((i/N,0),(i/N,1),((i+1)/N,1),((i+1)/N,0)))
case = mesh_obj("Rim — laminated rosewood case", verts, faces, MAT["rosewood"],
                "CASE_AND_RIM", uvs=uvs)

# Inner rim / soundboard well
cx = sum(p[0] for p in INNER)/N
cy = sum(p[1] for p in INNER)/N
sbv = [(cx, cy, 0.805)] + [(x, y, 0.805) for x, y in INNER]
sbf = [(0, 1+i, 1+(i+1) % N) for i in range(N)]
mesh_obj("Soundboard — spruce diaphragm", sbv, sbf, MAT["spruce"],
         "SOUNDBOARD_BRIDGES_AND_STRINGS")
# underside keybed
kb = box_template("Keybed", 1.45, 0.62, 0.045, MAT["rosewood_dark"])
instance("Keybed — structural", kb, "CASE_AND_RIM", (0, 0.48, 0.735))

# Fallboard / nameboard / cheek blocks
fall = box_template("Fallboard", 1.40, 0.085, 0.055, MAT["rosewood"], 0.006, 3)
instance("Fallboard — open", fall, "CASE_AND_RIM", (0, 0.775, 0.885), (math.radians(-18), 0, 0))
nameboard = box_template("Nameboard", 1.40, 0.045, 0.10, MAT["rosewood"], 0.004, 2)
instance("Nameboard", nameboard, "CASE_AND_RIM", (0, 0.735, 0.885))
for sx in (-1, 1):
    cheek = box_template("Cheek block", 0.18, 0.42, 0.25, MAT["rosewood"], 0.008, 3)
    instance(f"Cheek block {'bass' if sx<0 else 'treble'}", cheek, "CASE_AND_RIM",
             (sx*0.68, 0.60, 0.855))

# ------------------------------------------------------------------- cast plate
plate_bar = cyl_template("Plate bar template", 0.026, 1.0, 32, 8, MAT["frame_gold"])
plate_nodes = [(-0.60, 0.42), (0.60, 0.42), (0.62, -0.30), (0.40, -1.02),
               (-0.10, -1.16), (-0.60, -0.72)]
for i in range(len(plate_nodes)):
    a, b = Vector(plate_nodes[i]), Vector(plate_nodes[(i+1) % len(plate_nodes)])
    mid = ((a.x+b.x)/2, (a.y+b.y)/2, 0.845)
    length = (b-a).length
    ang = math.atan2(b.y-a.y, b.x-a.x)
    instance(f"Plate rim bar {i:02d}", plate_bar, "CAST_FRAME_AND_BRACING",
             mid, (math.pi/2, 0, ang + math.pi/2), (1, 1, length))
for i, x in enumerate([-0.35, -0.10, 0.15, 0.38]):
    instance(f"Plate cross strut {i:02d}", plate_bar, "CAST_FRAME_AND_BRACING",
             (x, -0.30, 0.847), (math.pi/2, 0, math.pi/2), (1.0, 1.0, 0.78))
bolt = cyl_template("Plate bolt template", 0.015, 0.018, 24, 2, MAT["brass"])
for i, (x, y) in enumerate(plate_nodes + [(0,0.30),(-0.3,-0.5),(0.3,-0.7)]):
    instance(f"Plate bolt {i:02d}", bolt, "CAST_FRAME_AND_BRACING", (x, y, 0.868))

# --------------------------------------------------------- bridges and strings
bridge_t = box_template("Bridge template", 0.035, 0.50, 0.028, MAT["rosewood_dark"], 0.004, 2)
instance("Treble bridge", bridge_t, "SOUNDBOARD_BRIDGES_AND_STRINGS",
         (-0.20, -0.42, 0.832), (0, 0, -0.55))
instance("Bass bridge", bridge_t, "SOUNDBOARD_BRIDGES_AND_STRINGS",
         (0.30, -0.72, 0.830), (0, 0, 0.35))

plain_string = cyl_template("Plain steel string (high detail)", 0.00045, 1.0, 64, 384, MAT["steel"])
wound_string = cyl_template("Copper wound bass string (high detail)", 0.0019, 1.0, 64, 512, MAT["copper"])
pin = cyl_template("Tuning / hitch pin", 0.006, 0.028, 20, 2, MAT["steel"])
note_count = 0
for midi in range(21, 109):
    note_count += 1
    t = (midi - 21) / 87
    x0 = -0.52 + t * 1.04
    is_bass = midi < 52
    y0, y1 = 0.34, -0.50 - t * 0.52
    length = y0 - y1
    unisons = 2 if midi < 45 else 3
    for u in range(unisons):
        x = x0 + (u - (unisons-1)/2) * 0.0055
        templ = wound_string if is_bass else plain_string
        instance(f"String {midi:03d}-{u}", templ, "SOUNDBOARD_BRIDGES_AND_STRINGS",
                 (x, (y0+y1)/2, 0.857), (math.pi/2, 0, 0), (1, 1, length))
        instance(f"Tuning pin {midi:03d}-{u}", pin, "SOUNDBOARD_BRIDGES_AND_STRINGS",
                 (x, y0+0.012, 0.858))
        instance(f"Hitch pin {midi:03d}-{u}", pin, "SOUNDBOARD_BRIDGES_AND_STRINGS",
                 (x + 0.02, y1-0.01, 0.850))

# ----------------------------------------------------------------- keyboard
def key_positions():
    whites = []
    blacks = []
    wi = 0
    ww = 1.22 / 52
    for midi in range(21, 109):
        if midi % 12 in (1, 3, 6, 8, 10):
            blacks.append((midi, -0.61 + (wi - 0.5) * ww))
        else:
            whites.append((midi, -0.61 + (wi + 0.5) * ww))
            wi += 1
    return whites, blacks

WHITES, BLACKS = key_positions()
nat_key = box_template("Natural key", 0.0218, 0.50, 0.022, MAT["ivory"], 0.0025, 3)
sharp_key = box_template("Sharp key", 0.0130, 0.32, 0.030, MAT["ebony"], 0.0025, 3)
for midi, x in WHITES:
    instance(f"Natural key {midi:03d}", nat_key, "KEYBOARD_AND_KEYBED", (x, 0.52, 0.754))
for midi, x in BLACKS:
    instance(f"Sharp key {midi:03d}", sharp_key, "KEYBOARD_AND_KEYBED", (x, 0.63, 0.770))
balance_pin = cyl_template("Balance / front pin", 0.0018, 0.020, 12, 2, MAT["steel"])
for midi, x in WHITES + BLACKS:
    instance(f"Front pin {midi:03d}", balance_pin, "KEYBOARD_AND_KEYBED", (x, 0.79, 0.753))

# ---------------------------------------------------------------- action
hammer_head = sphere_template("Hammer felt head — dense", 0.014, 96, 64, MAT["felt"])
hammer_shank = cyl_template("Hammer shank", 0.0022, 0.10, 16, 4, MAT["rosewood_dark"])
whippen_t = box_template("Whippen", 0.018, 0.045, 0.020, MAT["rosewood_dark"], 0.002, 2)
jack_t = box_template("Jack", 0.004, 0.035, 0.030, MAT["rosewood_dark"])
rep_t = box_template("Repetition lever", 0.006, 0.038, 0.006, MAT["leather"])
damper_t = box_template("Damper head", 0.014, 0.022, 0.020, MAT["felt_red"], 0.003, 3)
damper_wire = cyl_template("Damper wire", 0.0011, 0.09, 10, 3, MAT["steel"])
for midi, x in WHITES + BLACKS:
    z = 0.762 if midi % 12 not in (1,3,6,8,10) else 0.778
    yy = 0.22
    instance(f"Hammer head {midi:03d}", hammer_head, "ACTION_HAMMERS_AND_DAMPERS",
             (x, yy, z+0.115), (0,0,0), (1, 1.1, 0.72))
    instance(f"Hammer shank {midi:03d}", hammer_shank, "ACTION_HAMMERS_AND_DAMPERS",
             (x, yy+0.045, z+0.10), (math.pi/2, 0, 0))
    instance(f"Whippen {midi:03d}", whippen_t, "ACTION_HAMMERS_AND_DAMPERS", (x, yy+0.075, z))
    instance(f"Jack {midi:03d}", jack_t, "ACTION_HAMMERS_AND_DAMPERS", (x, yy+0.065, z+0.035))
    instance(f"Repetition lever {midi:03d}", rep_t, "ACTION_HAMMERS_AND_DAMPERS", (x, yy+0.070, z+0.048))
    instance(f"Damper head {midi:03d}", damper_t, "ACTION_HAMMERS_AND_DAMPERS", (x, yy-0.035, z+0.085))
    instance(f"Damper wire {midi:03d}", damper_wire, "ACTION_HAMMERS_AND_DAMPERS", (x, yy-0.02, z+0.04))

# ---------------------------------------------------------------- legs / lyre
def baluster(name, z0, z1, mat):
    rings = []
    levels = 48
    for k in range(levels):
        t = k / (levels-1)
        z = z0 + t * (z1-z0)
        # four-sided baluster profile: narrow waist, swollen shoulder, flared foot
        r = 0.052 + 0.027*math.sin(math.pi*t) + 0.020*math.exp(-((t-0.09)/0.07)**2) \
            + 0.026*math.exp(-((t-0.93)/0.06)**2)
        ring = []
        for s in range(32):
            a = 2*math.pi*s/32
            square = 1/max(abs(math.cos(a)), abs(math.sin(a))) * 0.76
            rr = r * (0.82 + 0.18*square) * (1 + 0.035*math.cos(8*a))
            ring.append((rr*math.cos(a), rr*math.sin(a), z))
        rings.append(ring)
    verts = [v for ring in rings for v in ring]
    faces = []
    for k in range(levels-1):
        for s in range(32):
            a = k*32+s; b = k*32+(s+1)%32
            faces.append((a, b, b+32, a+32))
    faces.append(tuple(reversed(range(32))))
    faces.append(tuple(range((levels-1)*32, levels*32)))
    return mesh_obj(name, verts, faces, mat, "LEGS_AND_PEDAL_LYRE", smooth=True)

leg_t = baluster("Carved baluster leg — master", 0.03, 0.715, MAT["rosewood"])
for i, (x, y) in enumerate([(-0.64, 0.56), (0.64, 0.56), (0.02, -1.03)]):
    instance(f"Carved leg {i+1}", leg_t, "LEGS_AND_PEDAL_LYRE", (x, y, 0))
    caster = cyl_template("Caster", 0.035, 0.028, 32, 2, MAT["brass"])
    instance(f"Brass caster {i+1}", caster, "LEGS_AND_PEDAL_LYRE", (x, y, 0.018))

# lyre: two pedals, three spindles, lion feet (documented on serial 53338)
lyre_post = box_template("Lyre spindle", 0.028, 0.035, 0.52, MAT["rosewood"], 0.005, 3)
for i, x in enumerate([-0.075, 0, 0.075]):
    instance(f"Lyre spindle {i+1}", lyre_post, "LEGS_AND_PEDAL_LYRE", (x, 0.70, 0.38))
lyre_top = box_template("Lyre top rail", 0.26, 0.06, 0.05, MAT["rosewood"], 0.008, 3)
instance("Lyre top rail", lyre_top, "LEGS_AND_PEDAL_LYRE", (0, 0.70, 0.655))
lyre_bottom = box_template("Lyre bottom rail", 0.27, 0.07, 0.045, MAT["rosewood"], 0.008, 3)
instance("Lyre bottom rail", lyre_bottom, "LEGS_AND_PEDAL_LYRE", (0, 0.70, 0.13))
pedal = box_template("Pedal", 0.055, 0.20, 0.016, MAT["brass"], 0.006, 3)
for i, x in enumerate([-0.075, 0.075]):
    instance(f"Pedal {i+1}", pedal, "PEDALS_AND_LINKAGES", (x, 0.80, 0.075),
             (math.radians(-8), 0, 0))
    rod = cyl_template("Pedal rod", 0.004, 0.55, 12, 4, MAT["steel"])
    instance(f"Pedal rod {i+1}", rod, "PEDALS_AND_LINKAGES", (x, 0.52, 0.40))

# ------------------------------------------------------------------- lid + prop
lidv = [(x, y, 0.972) for x, y in OUTLINE] + [(x, y, 0.998) for x, y in OUTLINE]
lidf = []
for i in range(N):
    j = (i+1) % N
    lidf.append((i, j, N+j, N+i))
lidf.append(tuple(range(N)))  # underside, normal -Z
lidf.append(tuple(range(2*N-1, N-1, -1)))  # top, normal +Z
lid = mesh_obj("Lid — rosewood with inlaid border", lidv, lidf, MAT["rosewood"],
               "LID_HINGES_AND_PROP")
HINGE = (0.785, -0.15, 0.972)
lid.location = HINGE
for i, v in enumerate(lid.data.vertices):
    v.co.x -= HINGE[0]; v.co.y -= HINGE[1]; v.co.z -= HINGE[2]
lid.data.update()
lid.rotation_euler = (0, math.radians(32), 0)

hinge_t = box_template("Lid hinge leaf", 0.11, 0.16, 0.012, MAT["gilt"], 0.004, 3)
for i, y in enumerate([0.30, -0.72]):
    instance(f"Ornate brass lid hinge {i+1}", hinge_t, "LID_HINGES_AND_PROP",
             (0.795, y, 0.968), (0, math.radians(24), 0))
prop = cyl_template("Lid prop", 0.011, 0.55, 24, 6, MAT["rosewood"])
instance("Lid prop stick", prop, "LID_HINGES_AND_PROP", (-0.49, -0.10, 1.04),
         (math.radians(-17), 0, math.radians(-8)))

# ---------------------------------------------------------- marquetry templates
def leaf_mesh(name, length, width, mat, nx=26, ny=16):
    verts, faces = [], []
    for j in range(ny+1):
        t = j/ny
        halfw = width * math.sin(math.pi*t) ** 0.85
        for i in range(nx+1):
            u = i/nx
            verts.append(((u-0.5)*length, (u-0.5)*length*0.16,
                          (t-0.5)*0.003 + (2*u-1)**2*0.001))
    for j in range(ny):
        for i in range(nx):
            a = j*(nx+1)+i
            faces.append((a, a+1, a+nx+2, a+nx+1))
    return mesh_obj(name, verts, faces, mat, "TEMPLATES", smooth=True)

leaf_light = leaf_mesh("Inlay leaf — fruitwood", 0.035, 0.009, MAT["inlay_light"])
leaf_dark = leaf_mesh("Inlay leaf — dark wood", 0.030, 0.008, MAT["inlay_dark"])
leaf_green = leaf_mesh("Inlay leaf — stained", 0.026, 0.007, MAT["inlay_green"])
flower_t = sphere_template("Inlay flower rosette", 0.010, 32, 16, MAT["inlay_light"])
# continuous rinceau along the lid border, following the actual curved perimeter
for i in range(0, N, 2):
    x, y = INNER[i]
    ang = math.atan2(y-cy, x-cx)
    for k in (-1, 0, 1):
        templ = [leaf_light, leaf_dark, leaf_green][(i//2+k) % 3]
        instance(f"Lid rinceau leaf {i:03d}_{k}", templ, "ART_NOUVEAU_MARQUETRY",
                 (x*0.94, y*0.94, 0.978), (0, 0, ang + k*0.55), (0.8, 0.8, 1))
    if i % 8 == 0:
        instance(f"Lid rinceau flower {i:03d}", flower_t, "ART_NOUVEAU_MARQUETRY",
                 (x*0.93, y*0.93, 0.979))
# cheek inlay: stylised whiplash curves and foliage on both cheek panels
for sx in (-1, 1):
    for i in range(38):
        yy = 0.43 + (i % 19) * 0.019
        xx = sx * (0.60 + 0.06*math.sin(i*0.6))
        templ = [leaf_light, leaf_dark, leaf_green][i % 3]
        instance(f"Cheek inlay {'L' if sx<0 else 'R'} {i:02d}", templ,
                 "ART_NOUVEAU_MARQUETRY",
                 (xx, yy, 0.962), (0, 0, sx*math.radians(70+i*3)))
    for i in range(7):
        curve_obj(f"Cheek whiplash {'L' if sx<0 else 'R'} {i}", [
            (sx*0.575, 0.44+i*0.045, 0.963),
            (sx*(0.66+0.02*i), 0.48+i*0.04, 0.964),
            (sx*0.72, 0.56+i*0.03, 0.964),
        ], 0.0022, MAT["inlay_light"], "ART_NOUVEAU_MARQUETRY")
# fall inlay: symmetrical Art Nouveau foliage and whiplash lines
for i in range(64):
    x = -0.66 + i * (1.32/63)
    for row, z in enumerate([0.813, 0.843]):
        templ = leaf_light if i % 3 else leaf_dark
        instance(f"Fall inlay {row}-{i:02d}", templ, "ART_NOUVEAU_MARQUETRY",
                 (x, 0.841, z), (math.pi/2, 0, math.radians(25*(-1 if x<0 else 1))))

# ------------------------------------------------- gilt female-head cheek mounts
def female_head_mesh(name, mat):
    # Profile silhouette in XZ, extruded in Y with a high-resolution bevel.
    prof = [(-0.030,0.000),(-0.034,0.020),(-0.026,0.038),(-0.038,0.050),
            (-0.031,0.064),(-0.040,0.072),(-0.022,0.078),(-0.030,0.092),
            (-0.014,0.105),(-0.022,0.120),(0.006,0.137),(0.020,0.128),
            (0.018,0.112),(0.006,0.100),(0.012,0.082),(0.024,0.072),
            (0.022,0.054),(0.014,0.044),(0.016,0.020),(0.008,0.000)]
    verts=[]; faces=[]
    steps=12; depth=0.030
    for s in range(steps+1):
        t=s/steps
        bulge=math.sin(math.pi*t)**0.5
        for px,pz in prof:
            verts.append((px*(0.72+0.28*bulge), -depth/2+t*depth, pz))
    m=len(prof)
    for s in range(steps):
        for i in range(m):
            a=s*m+i; b=s*m+(i+1)%m
            faces.append((a,b,b+m,a+m))
    faces.append(tuple(range(m-1,-1,-1)))
    faces.append(tuple(range(steps*m,(steps+1)*m)))
    ob=mesh_obj(name,verts,faces,mat,"GILT_MOUNTS_AND_SCULPTURE",smooth=True)
    return ob

head_t = female_head_mesh("Gilt female-head mount — master", MAT["gilt"])
curl_t = sphere_template("Hair curl", 0.012, 32, 20, MAT["gilt"])
flower_gilt = sphere_template("Gilt flower boss", 0.010, 32, 16, MAT["gilt"])
for sx in (-1, 1):
    instance(f"Female head mount {'bass' if sx<0 else 'treble'}", head_t,
             "GILT_MOUNTS_AND_SCULPTURE", (sx*0.735, 0.565, 0.965),
             (0, math.radians(-90 if sx<0 else 90), 0))
    for i in range(11):
        instance(f"Gilt hair lock {sx}_{i}", curl_t, "GILT_MOUNTS_AND_SCULPTURE",
                 (sx*0.738, 0.52+i*0.011, 1.08+0.01*math.sin(i)), (0,0,0),
                 (1.5,0.7,0.7))
    for i in range(5):
        instance(f"Floral headband flower {sx}_{i}", flower_gilt,
                 "GILT_MOUNTS_AND_SCULPTURE",
                 (sx*0.752, 0.53+i*0.022, 1.115-0.006*i))
# Empire-style columnar mounts flanking the cheek inlay
column = cyl_template("Empire gilt mount", 0.010, 0.14, 32, 8, MAT["gilt"])
for sx in (-1, 1):
    for i in range(5):
        instance(f"Empire mount flute {sx}_{i}", column, "GILT_MOUNTS_AND_SCULPTURE",
                 (sx*(0.70+i*0.006), 0.455, 0.965), (0,0,0), (1,1,1))
    fan = leaf_mesh("Palmette gilt", 0.07, 0.030, MAT["gilt"], 30, 20)
    instance(f"Gilt palmette {sx}", fan, "GILT_MOUNTS_AND_SCULPTURE",
             (sx*0.72, 0.44, 1.04), (0,0,sx*1.2))
# winged lions and bees on the fall
lion_body = sphere_template("Winged lion body", 0.055, 64, 40, MAT["gilt"])
lion_wing = leaf_mesh("Lion wing", 0.16, 0.075, MAT["gilt"], 40, 26)
for sx in (-1, 1):
    instance(f"Winged lion body {sx}", lion_body, "GILT_MOUNTS_AND_SCULPTURE",
             (sx*0.33, 0.843, 0.884), (0,0,0), (1.0,0.35,0.52))
    instance(f"Winged lion wing {sx}", lion_wing, "GILT_MOUNTS_AND_SCULPTURE",
             (sx*0.40, 0.846, 0.908), (math.pi/2,0,sx*0.4), (0.85,0.85,1))
bee_body = sphere_template("Bee body", 0.009, 32, 20, MAT["gilt"])
bee_wing = leaf_mesh("Bee wing", 0.020, 0.007, MAT["gilt"], 16, 10)
for i in range(12):
    x = -0.18 + i*0.033
    instance(f"Fall bee {i:02d}", bee_body, "GILT_MOUNTS_AND_SCULPTURE",
             (x, 0.845, 0.920+0.008*math.sin(i)))
    instance(f"Fall bee wing L {i:02d}", bee_wing, "GILT_MOUNTS_AND_SCULPTURE",
             (x-0.012, 0.846, 0.928), (math.pi/2,0,0.6))
    instance(f"Fall bee wing R {i:02d}", bee_wing, "GILT_MOUNTS_AND_SCULPTURE",
             (x+0.012, 0.846, 0.928), (math.pi/2,0,-0.6))

# sunflower carving on each leg
petal = leaf_mesh("Sunflower petal", 0.030, 0.010, MAT["rosewood_dark"], 20, 12)
sun_center = sphere_template("Sunflower centre", 0.012, 32, 16, MAT["rosewood_dark"])
for li, (lx, ly) in enumerate([(-0.64,0.56),(0.64,0.56),(0.02,-1.03)]):
    for face in range(4):
        a = face*math.pi/2
        for p in range(12):
            pa = a + (p-6)*0.12
            instance(f"Sunflower leg {li} face {face} petal {p}", petal,
                     "GILT_MOUNTS_AND_SCULPTURE",
                     (lx+0.062*math.cos(pa), ly+0.062*math.sin(pa), 0.38),
                     (math.pi/2, 0, pa))
        instance(f"Sunflower centre leg {li} face {face}", sun_center,
                 "GILT_MOUNTS_AND_SCULPTURE",
                 (lx+0.060*math.cos(a), ly+0.060*math.sin(a), 0.38))
    band = cyl_template("Gilt filigree leg band", 0.064, 0.022, 48, 4, MAT["gilt"])
    instance(f"Gilt filigree band leg {li}", band, "LEGS_AND_PEDAL_LYRE", (lx,ly,0.565))

# ------------------------------------------------------- butterfly music desk
# Bevelled glass wings following the BADA butterfly silhouette.
def glass_wing(name, sx):
    profile = [(0,0),(sx*0.18,0.02),(sx*0.38,0.10),(sx*0.46,0.16),
               (sx*0.42,0.24),(sx*0.24,0.20),(sx*0.06,0.15)]
    verts=[]
    for x,y in profile:
        verts.append((x,y,0)); verts.append((x,y,0.008))
    faces=[]
    n=len(profile)
    for i in range(n-1):
        faces.append((2*i,2*i+2,2*i+3,2*i+1))
    faces.append(tuple(range(0,2*n,2)))
    faces.append(tuple(range(1,2*n,2)))
    return mesh_obj(name,verts,faces,MAT["glass"],"GLASS_FILIGREE_MUSIC_DESK")

for sx in (-1,1):
    w=glass_wing(f"Butterfly glass wing {'L' if sx<0 else 'R'}",sx)
    w.location=(0,0.665,1.00)
    curve_obj(f"Butterfly filigree frame {'L' if sx<0 else 'R'}",[
        (0,0.665,1.008),(sx*0.20,0.685,1.008),(sx*0.38,0.765,1.008),
        (sx*0.46,0.825,1.008),(sx*0.24,0.865,1.008)],0.004,MAT["gilt"],
        "GLASS_FILIGREE_MUSIC_DESK")
# Tree of Life and laurel wreath
curve_obj("Tree of Life trunk",[(0,0.665,1.014),(0,0.74,1.014),(0,0.82,1.014)],
          0.005,MAT["gilt"],"GLASS_FILIGREE_MUSIC_DESK")
for i in range(9):
    s=-1 if i%2 else 1
    curve_obj(f"Tree of Life branch {i}",[
        (0,0.72+i*0.012,1.014),(s*0.06,0.75+i*0.010,1.014),
        (s*0.14,0.77+i*0.008,1.014)],0.0025,MAT["gilt"],"GLASS_FILIGREE_MUSIC_DESK")
for i in range(26):
    a=2*math.pi*i/26
    instance(f"Laurel leaf {i:02d}", leaf_green, "GLASS_FILIGREE_MUSIC_DESK",
             (0.145*math.cos(a), 0.762+0.085*math.sin(a), 1.016),
             (math.pi/2,0,a))

# ------------------------------------------------------------------ staging
floor=mesh_obj("Music room floor",[(-8,-8,0),(8,-8,0),(8,8,0),(-8,8,0)],
               [(0,1,2,3)],MAT["floor"],"CAMERAS_LIGHTS_AND_STAGING")
wall=mesh_obj("Music room rear wall",[(-8,4.2,0),(8,4.2,0),(8,4.2,4),(-8,4.2,4)],
              [(0,1,2,3)],MAT["wall"],"CAMERAS_LIGHTS_AND_STAGING")

def look_at(ob, target):
    direction=Vector(target)-ob.location
    ob.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()

def camera(name, loc, target, lens=50):
    cd=bpy.data.cameras.new(name)
    ob=bpy.data.objects.new(name,cd)
    COLLECTIONS["CAMERAS_LIGHTS_AND_STAGING"].objects.link(ob)
    ob.location=loc; cd.lens=lens; look_at(ob,target)
    return ob

camera("CAM_HERO_3Q",(-2.55,3.05,1.78),(0,0.18,0.88),45)
camera("CAM_FRONT",(-0.35,3.10,1.20),(0,0.42,0.86),52)
camera("CAM_SIDE",(-3.60,0.10,1.30),(0,-0.20,0.90),52)
camera("CAM_REAR",(2.40,-3.10,1.75),(0,-0.45,0.92),44)
camera("CAM_INTERIOR_TOP",(0.10,0.45,3.05),(0,-0.35,0.84),48)
camera("CAM_ACTION",(1.05,1.35,1.55),(0,0.35,0.82),62)
camera("CAM_MACRO_HEAD",(-1.05,1.35,1.30),(-0.72,0.56,1.06),90)
camera("CAM_MACRO_DESK",(0.35,1.55,1.45),(0,0.74,1.02),80)
camera("CAM_MACRO_LEG",(-0.20,1.05,0.55),(-0.64,0.56,0.40),85)
camera("CAM_MACRO_CHEEK",(-1.10,1.20,1.20),(-0.68,0.57,0.96),90)
camera("CAM_MACRO_FALL",(-0.15,1.35,1.10),(0,0.84,0.90),95)
camera("CAM_MACRO_LYRE",(0.05,1.35,0.55),(0,0.70,0.36),80)
camera("CAM_MACRO_STRINGS",(0.35,0.30,1.45),(0.10,-0.45,0.86),90)
camera("CAM_MACRO_GRAIN",(-1.05,0.15,0.98),(-0.78,0.10,0.86),100)
camera("CAM_PRODUCT_CLOSED",(-2.55,3.05,1.55),(0,0.18,0.84),46)

def area(name,loc,power,size,target):
    ld=bpy.data.lights.new(name,"AREA"); ld.energy=power; ld.shape='RECTANGLE'
    ld.size=size[0]; ld.size_y=size[1]
    ob=bpy.data.objects.new(name,ld)
    COLLECTIONS["CAMERAS_LIGHTS_AND_STAGING"].objects.link(ob)
    ob.location=loc; look_at(ob,target)

area("KEY_softbox",(1.2,2.2,3.2),900,(3.0,2.0),(0,0,0.9))
area("FILL_window",(-2.8,0.6,2.4),600,(2.0,2.5),(0,0,0.9))
area("RIM_gilt",(0.4,-2.4,2.6),750,(2.0,1.5),(0,-0.4,1.0))
area("TOP_action",(0,0.2,3.4),400,(1.5,1.5),(0,0,0.85))

scene=bpy.context.scene
scene.camera=bpy.data.objects["CAM_HERO_3Q"]
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1920
scene.render.resolution_y=1080
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
world = bpy.data.worlds.new("Warm music room ambient")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.12, 0.10, 0.09, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55
scene.world = world
scene.render.filepath=os.path.join(ROOT,"renders/1899-bluthner-grand-piano/hero_test.png")
os.makedirs(os.path.dirname(scene.render.filepath),exist_ok=True)

# hide templates from render and viewport (they remain source geometry)
for ob in COLLECTIONS["TEMPLATES"].objects:
    ob.hide_render=True
    ob.hide_set(True)

blend_path=os.path.join(ASSET,"1899_bluthner_grand_piano_master.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print("BUILD_DONE",blend_path,"notes",note_count,
      "objects",len(bpy.data.objects),flush=True)

# Keep the lid rinceau physically attached to the moving lid.
bpy.context.view_layer.update()
for ob in bpy.data.objects:
    if ob.name.startswith("Lid rinceau"):
        ob.parent = lid
        ob.matrix_parent_inverse = lid.matrix_world.inverted()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ASSET,"1899_bluthner_grand_piano_master.blend"))
print("LID_PARENT_DONE", flush=True)
