#!/usr/bin/env blender --python
"""
Remington MODEL 56 — 1950s portable manual typewriter
Procedural Blender build: geometry, materials, cameras, lighting.
Run:  blender -b -P build.py
"""
import bpy, math, os, sys, random
from math import radians, sin, cos, pi, atan2, sqrt, degrees
from mathutils import Vector, Matrix, Euler

random.seed(5601)

ROOT = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(ROOT, "textures")
BLEND_OUT = os.path.join(ROOT, "vintage_typewriter.blend")
GLB_OUT = os.path.join(ROOT, "vintage_typewriter.glb")

# ----------------------------------------------------------------- scene base
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001          # 1 BU = 1 mm
sc.unit_settings.length_unit = 'MILLIMETERS'
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8
sc.cycles.filter_width = 1.2
try:
    sc.render.use_denoising = True
except Exception:
    pass
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = 0.05
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGB'
sc.render.image_settings.color_depth = '8'
sc.render.image_settings.compression = 12
sc.render.film_transparent = False

COLLECTIONS = [
    "01_MAIN_CASING", "02_KEYBOARD", "03_CARRIAGE", "04_PLATEN_AND_PAPER",
    "05_RIBBON_MECHANISM", "06_TYPEBARS", "07_CONTROLS_AND_LEVERS",
    "08_FASTENERS_AND_DETAILS", "09_CAMERAS", "10_LIGHTING",
]
colls = {}
for name in COLLECTIONS:
    c = bpy.data.collections.new(name)
    sc.collection.children.link(c)
    colls[name] = c

def move_to_collection(obj, coll_name):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    colls[coll_name].objects.link(obj)

# ----------------------------------------------------------------- materials
def load_tex(filename, non_color=True):
    path = os.path.join(TEX, filename)
    img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        img.colorspace_settings.name = 'Non-Color'
    else:
        img.colorspace_settings.name = 'sRGB'
    return img

tex_cache = {}
def T(name, non_color=True):
    key = (name, non_color)
    if key not in tex_cache:
        tex_cache[key] = load_tex(name, non_color)
    return tex_cache[key]

def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m

def bsdf(m):
    return m.node_tree.nodes["Principled BSDF"]

def set_in(m, socket, value):
    try:
        bsdf(m).inputs[socket].default_value = value
    except KeyError:
        print("WARN: socket", socket, "missing on", m.name)

def tex_to(m, img, socket, non_color=True, mapping_scale=None):
    nt = m.node_tree
    node = nt.nodes.new("ShaderNodeTexImage")
    node.image = img
    if non_color:
        node.image.colorspace_settings.name = 'Non-Color'
    out = node.outputs["Color"]
    if mapping_scale:
        mp = nt.nodes.new("ShaderNodeMapping")
        tc = nt.nodes.new("ShaderNodeTexCoord")
        tc.outputs["UV"]
        mp.inputs["Scale"].default_value = (mapping_scale[0], mapping_scale[1], 1.0)
        nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], node.inputs["Vector"])
    nt.links.new(out, bsdf(m).inputs[socket])

M = {}
def build_materials():
    # warm ivory enamel with subtle orange-peel roughness
    m = new_mat("MAT_ivory_enamel")
    set_in(m, "Base Color", (0.847, 0.815, 0.706, 1.0))
    set_in(m, "Metallic", 0.0)
    set_in(m, "Roughness", 0.45)
    set_in(m, "Coat Weight", 0.35); set_in(m, "Coat Roughness", 0.28)
    tex_to(m, T("enamel_rough.png"), "Roughness")
    M["ivory"] = m
    # dark charcoal painted metal
    m = new_mat("MAT_charcoal_paint")
    set_in(m, "Base Color", (0.055, 0.051, 0.048, 1.0))
    set_in(m, "Metallic", 0.25); set_in(m, "Roughness", 0.50)
    set_in(m, "Coat Weight", 0.18); set_in(m, "Coat Roughness", 0.42)
    M["charcoal"] = m
    # Bakelite black (keycaps)
    m = new_mat("MAT_bakelite")
    set_in(m, "Base Color", (0.036, 0.034, 0.032, 1.0))
    set_in(m, "Metallic", 0.0); set_in(m, "Roughness", 0.35)
    set_in(m, "Coat Weight", 0.30); set_in(m, "Coat Roughness", 0.32)
    tex_to(m, T("keycap_rough.png"), "Roughness")
    M["bakelite"] = m
    # brushed chrome
    m = new_mat("MAT_brushed_chrome")
    set_in(m, "Base Color", (0.93, 0.93, 0.94, 1.0))
    set_in(m, "Metallic", 1.0); set_in(m, "Roughness", 0.18)
    tex_to(m, T("chrome_rough.png"), "Roughness")
    M["chrome"] = m
    # nickel plated accents
    m = new_mat("MAT_nickel")
    set_in(m, "Base Color", (0.82, 0.80, 0.76, 1.0))
    set_in(m, "Metallic", 1.0); set_in(m, "Roughness", 0.30)
    M["nickel"] = m
    # dark internal steel
    m = new_mat("MAT_dark_steel")
    set_in(m, "Base Color", (0.115, 0.115, 0.125, 1.0))
    set_in(m, "Metallic", 0.9); set_in(m, "Roughness", 0.42)
    M["dark_steel"] = m
    # blued spring steel
    m = new_mat("MAT_blued_steel")
    set_in(m, "Base Color", (0.160, 0.155, 0.180, 1.0))
    set_in(m, "Metallic", 0.85); set_in(m, "Roughness", 0.35)
    M["blued"] = m
    # rubber
    m = new_mat("MAT_rubber")
    set_in(m, "Base Color", (0.022, 0.022, 0.022, 1.0))
    set_in(m, "Metallic", 0.0); set_in(m, "Roughness", 0.92)
    tex_to(m, T("rubber_rough.png"), "Roughness")
    M["rubber"] = m
    # ribbon fabric (bicolor)
    m = new_mat("MAT_ribbon")
    set_in(m, "Base Color", (1.0, 1.0, 1.0, 1.0))
    set_in(m, "Metallic", 0.0); set_in(m, "Roughness", 0.88)
    tex_to(m, T("ribbon.png", non_color=False), "Base Color")
    M["ribbon"] = m
    # paper
    m = new_mat("MAT_paper")
    set_in(m, "Base Color", (1.0, 1.0, 1.0, 1.0))
    set_in(m, "Metallic", 0.0); set_in(m, "Roughness", 0.82)
    tex_to(m, T("paper.png", non_color=False), "Base Color")
    M["paper"] = m
    # carriage scale ruler
    m = new_mat("MAT_scale")
    set_in(m, "Base Color", (1.0, 1.0, 1.0, 1.0))
    set_in(m, "Metallic", 0.15); set_in(m, "Roughness", 0.5)
    tex_to(m, T("scale.png", non_color=False), "Base Color")
    M["scale"] = m
    # brass badge
    m = new_mat("MAT_badge")
    set_in(m, "Base Color", (1.0, 1.0, 1.0, 1.0))
    set_in(m, "Metallic", 0.78); set_in(m, "Roughness", 0.34)
    set_in(m, "Coat Weight", 0.3); set_in(m, "Coat Roughness", 0.25)
    tex_to(m, T("badge.png", non_color=False), "Base Color")
    M["badge"] = m
    # wound ribbon on spools (dark fabric)
    m = new_mat("MAT_spool_wrap")
    set_in(m, "Base Color", (0.045, 0.038, 0.036, 1.0))
    set_in(m, "Metallic", 0.05); set_in(m, "Roughness", 0.72)
    M["spool_wrap"] = m
    # brass strip (interior detail)
    m = new_mat("MAT_brass")
    set_in(m, "Base Color", (0.52, 0.40, 0.20, 1.0))
    set_in(m, "Metallic", 1.0); set_in(m, "Roughness", 0.38)
    M["brass"] = m
    # leather handle wrap
    m = new_mat("MAT_leather")
    set_in(m, "Base Color", (0.16, 0.075, 0.045, 1.0))
    set_in(m, "Metallic", 0.0); set_in(m, "Roughness", 0.65)
    M["leather"] = m
    # interior darkness
    m = new_mat("MAT_interior")
    set_in(m, "Base Color", (0.028, 0.026, 0.024, 1.0))
    set_in(m, "Metallic", 0.1); set_in(m, "Roughness", 0.85)
    M["interior"] = m

def legend_mat(name, filename):
    m = new_mat(f"MAT_legend_{name}")
    set_in(m, "Base Color", (1, 1, 1, 1))
    set_in(m, "Metallic", 0.0); set_in(m, "Roughness", 0.42)
    set_in(m, "Coat Weight", 0.35); set_in(m, "Coat Roughness", 0.3)
    tex_to(m, T(filename, non_color=False), "Base Color")
    return m

build_materials()

# ----------------------------------------------------------------- helpers
def add_obj(name, coll, mat=None):
    obj = bpy.context.active_object
    obj.name = name
    move_to_collection(obj, coll)
    if mat:
        obj.data.materials.append(mat)
    return obj

def apply_xf(obj, rot=True, scale=True):
    for c in obj.users_collection: c.objects.unlink(obj)
    colls["08_FASTENERS_AND_DETAILS"].objects.link(obj)  # temp home
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True); bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=rot, scale=scale)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    return obj

def box(name, sx, sy, sz, loc, mat, coll, bevel=0.0, rot=None, segments=3):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot or (0, 0, 0))
    o = bpy.context.active_object
    o.scale = (sx, sy, sz)
    apply_xf(o, rot=False, scale=True)
    if rot: o.rotation_euler = rot
    move_to_collection(o, coll)
    o.data.materials.append(mat)
    o.name = name
    if bevel > 0:
        bv = o.modifiers.new("Bevel", 'BEVEL')
        bv.width = bevel; bv.segments = segments
        bv.limit_method = 'ANGLE'; bv.angle_limit = radians(30); bv.profile = 0.65
    return o

def cyl(name, r, depth, loc, mat, coll, rot=None, r_top=None, vertices=32, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=r, depth=depth,
                                        location=loc, rotation=rot or (0, 0, 0))
    o = bpy.context.active_object
    if r_top is not None:
        # tapered cap: scale top ring inward via edit of mesh? use cone primitive instead
        pass
    move_to_collection(o, coll)
    o.data.materials.append(mat)
    o.name = name
    if bevel > 0:
        bv = o.modifiers.new("Bevel", 'BEVEL')
        bv.width = bevel; bv.segments = 2
        bv.limit_method = 'ANGLE'; bv.angle_limit = radians(35); bv.profile = 0.6
    return o

def tapered_cyl(name, r_bottom, r_top, depth, loc, mat, coll, rot=None, vertices=32, bevel=0.0):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=r_bottom, radius2=r_top,
                                    depth=depth, location=loc, rotation=rot or (0, 0, 0))
    o = bpy.context.active_object
    move_to_collection(o, coll)
    o.data.materials.append(mat)
    o.name = name
    if bevel > 0:
        bv = o.modifiers.new("Bevel", 'BEVEL')
        bv.width = bevel; bv.segments = 2
        bv.limit_method = 'ANGLE'; bv.angle_limit = radians(40); bv.profile = 0.6
    return o

def basis_from_dirs(x_dir, y_dir, z_dir):
    m = Matrix.Identity(3)
    m.col[0] = Vector(x_dir).normalized()
    m.col[1] = Vector(y_dir).normalized()
    m.col[2] = Vector(z_dir).normalized()
    return m

def look_rot(target_dir):
    return target_dir.to_track_quat('Z', 'Y').to_euler()

def screw(name, loc, axis_dir, coll="08_FASTENERS_AND_DETAILS", r=1.7):
    d = Vector(axis_dir).normalized()
    rot = d.to_track_quat('Z', 'Y').to_euler()
    head = cyl(name + "_head", r, 1.15, loc, M["nickel"], coll, rot=rot, vertices=24, bevel=0.28)
    slot = box(name + "_slot", r * 1.62, 0.46, 0.36,
               loc + d * 0.52, M["interior"], coll, bevel=0.06)
    slot.rotation_euler = rot
    # align slot tangentially
    return head

def helix_spring(name, start, end, radius, coils, wire, mat, coll):
    start = Vector(start); end = Vector(end)
    axis = end - start
    length = axis.length
    up = axis.normalized()
    tmp = Vector((0, 0, 1)) if abs(up.z) < 0.9 else Vector((1, 0, 0))
    u = up.cross(tmp).normalized()
    v = up.cross(u).normalized()
    n = int(coils * 20)
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = t * coils * 2 * pi
        p = start + up * (t * length) + u * (cos(ang) * radius) + v * (sin(ang) * radius)
        pts.append(p)
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 1
    cu.bevel_depth = wire
    cu.bevel_resolution = 2
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z, 1.0)
    obj = bpy.data.objects.new(name, cu)
    colls[coll].objects.link(obj)
    cu.materials.append(mat)
    return obj

def gear(name, teeth, r_out, r_root, thickness, loc, mat, coll):
    verts = []
    faces = []
    n = teeth
    for ring_z in (0.0, thickness):
        for i in range(n):
            a = (i / n) * 2 * pi
            step = 2 * pi / n
            ring = [(a, r_root), (a + step * 0.18, r_root), (a + step * 0.30, r_out),
                    (a + step * 0.52, r_out), (a + step * 0.64, r_root)]
            for ang, rad in ring:
                verts.append((cos(ang) * rad, sin(ang) * rad, ring_z))
    per = 5 * n
    base = per
    # side faces
    for i in range(per):
        j = (i + 1) % per
        faces.append((i, j, j + base, i + base))
    faces.append(tuple(range(per - 1, -1, -1)))      # bottom
    faces.append(tuple(range(base, base + per)))     # top
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    colls[coll].objects.link(obj)
    mesh.materials.append(mat)
    obj.location = loc
    return obj

# ==================================================================
# GEOMETRY
# ==================================================================
TH = atan2(48.0, 135.0)          # deck slope angle (rad)
CosT, SinT = cos(TH), sin(TH)
SLOPE_N = Vector((0, -SinT, CosT))

# ---------------------------------------------------- 01 MAIN CASING
box("CHASSIS_lower", 292, 252, 22, (0, 0, 17), M["ivory"], "01_MAIN_CASING", bevel=4.0, segments=4)

# side cheeks — extruded curved profile
cheek_pts = [(-150, 7), (-151.5, 28), (-146, 38.5), (-131, 46.5), (-95, 57.5), (-45, 71.5),
             (-12, 78.5), (28, 81.5), (56, 84), (78, 89.5), (98, 99.5), (122, 102),
             (150, 101), (153, 60), (153, 7)]
shape = bpy.data.curves.new  # placeholder to avoid lint confusion
sh = bpy.data.curves.new  # unused
def make_cheek(name, x0):
    shp = bpy.data.meshes.new  # not used
    crv = bpy.data.curves.new(name, 'CURVE')
    crv.dimensions = '2D'
    sp = crv.splines.new('POLY')
    sp.points.add(len(cheek_pts) - 1)
    for i, (a, b) in enumerate(cheek_pts):
        sp.points[i].co = (a, b, 0, 1)
    sp.use_cyclic_u = True
    cu = crv
    # convert curve -> shape extrusion manually via mesh from pydata is complex; use Shape instead
    return crv

# -- use Shape + ExtrudeGeometry for cheeks (proper rounded profile)
def make_cheek_shape(name, x_start):
    shp = bpy.data.shapes.new(name)
    shp.from_splines  # placeholder never used
    return shp

# simpler & robust: build cheek as extruded mesh via from_pydata with bevel modifier
def make_cheek_mesh(name, x_start, coll):
    # profile polygon in (y, z)
    n = len(cheek_pts)
    verts = []
    # back plate (inner face) and front plate (outer face) + rim
    th_thick = 13.0
    for zOff in (0.0, th_thick):
        for (a, b) in cheek_pts:
            verts.append((x_start + zOff, a, b))   # (x = lateral)
    faces = []
    faces.append(tuple(range(n - 1, -1, -1)))      # inner face (normal -X)
    faces.append(tuple(range(n, 2 * n)))           # outer face (+X)
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    colls[coll].objects.link(obj)
    mesh.materials.append(M["ivory"])
    bv = obj.modifiers.new("Bevel", 'BEVEL')
    bv.width = 2.3; bv.segments = 3
    bv.limit_method = 'ANGLE'; bv.angle_limit = radians(28); bv.profile = 0.6
    return obj

make_cheek_mesh("CASING_side_panel_R", 142.0, "01_MAIN_CASING")
make_cheek_mesh("CASING_side_panel_L", -155.0, "01_MAIN_CASING")

# hood rear panel (sloped)
box("CASING_hood_rear", 281, 88, 7, (0, 84.5, 93.0), M["ivory"], "01_MAIN_CASING",
    bevel=2.0, rot=(radians(12.4), 0, 0))
# ribbon deck plate
box("CASING_ribbon_deck", 252, 66, 5, (0, 16, 80.5), M["charcoal"], "01_MAIN_CASING", bevel=1.5)
# keyboard deck plate (sloped, charcoal)
deck_cx, deck_cz = 69.0 * CosT, 69.0 * SinT
box("CASING_deck_plate", 283, 140, 5, (0, -150 + deck_cx, 33 + deck_cz - 2.8), M["charcoal"],
    "01_MAIN_CASING", bevel=1.5, rot=(TH, 0, 0))
# front apron
box("CASING_apron", 291, 9, 28, (0, -147.5, 21), M["ivory"], "01_MAIN_CASING", bevel=2.5, segments=4)
box("CASING_apron_seam", 291, 0.7, 1.1, (0, -152.35, 33.4), M["interior"], "01_MAIN_CASING")
# rear access panel + hinges
box("CASING_access_panel", 158, 2.6, 64, (0, 151.2, 51), M["ivory"], "01_MAIN_CASING", bevel=1.8)
hinge_l = cyl("CASING_hinge_L", 2.3, 13, (-52, 151.4, 85.5), M["nickel"], "08_FASTENERS_AND_DETAILS",
              rot=(0, radians(90), 0), vertices=20)
hinge_r = cyl("CASING_hinge_R", 2.3, 13, (52, 151.4, 85.5), M["nickel"], "08_FASTENERS_AND_DETAILS",
              rot=(0, radians(90), 0), vertices=20)
# ventilation slots (side cheeks + rear)
for side in (-1, 1):
    for yy in (-108, -73, -38, -3):
        s = box(f"CASING_vent_{'L' if side < 0 else 'R'}_{yy}", 1.6, 27, 3.7,
                (side * 155.4, yy, 17.5), M["interior"], "01_MAIN_CASING", bevel=0.7,
                rot=(radians(14), 0, 0))
for xx in (-64, -32, 0, 32, 64):
    box(f"CASING_vent_rear_{xx}", 3.7, 1.6, 21, (xx, 152.6, 44), M["interior"], "01_MAIN_CASING", bevel=0.7)
# rubber feet
for fx in (-118, 118):
    for fy in (-112, 112):
        cyl(f"CHASSIS_foot_{fx}_{fy}", 8.2, 6.5, (fx, fy, 3.2), M["rubber"], "01_MAIN_CASING",
            vertices=28, bevel=1.6)
# rear carrying handle (portable machine)
handle_pts = [(-58, 150, 66), (-58, 172, 68), (-52, 179.5, 69), (52, 179.5, 69), (58, 172, 68), (58, 150, 66)]
cu = bpy.data.curves.new("CASING_handle", 'CURVE'); cu.dimensions = '3D'
cu.bevel_depth = 4.1; cu.bevel_resolution = 3; cu.resolution_u = 12
sp = cu.splines.new('POLY'); sp.points.add(len(handle_pts) - 1)
for i, p in enumerate(handle_pts):
    sp.points[i].co = (p[0], p[1], p[2], 1.0)
ho = bpy.data.objects.new("CASING_handle_bar", cu); colls["01_MAIN_CASING"].objects.link(ho)
cu.materials.append(M["dark_steel"])
box("CASING_handle_grip", 104, 7.4, 7.4, (0, 179.5, 69), M["leather"], "01_MAIN_CASING", bevel=3.4, segments=4)
box("CASING_handle_mount_L", 15, 7, 13, (-58, 150.5, 62.5), M["charcoal"], "01_MAIN_CASING", bevel=2)
box("CASING_handle_mount_R", 15, 7, 13, (58, 150.5, 62.5), M["charcoal"], "01_MAIN_CASING", bevel=2)

# ---------------------------------------------------- 02 KEYBOARD
stem_objs = []
def key_pos(v):
    return Vector((0.0, -150 + v * CosT, 33 + v * SinT))

def add_stem(name, x, v):
    p = key_pos(v) + Vector((x, 0, 0.0))
    s = tapered_cyl(name, 2.05, 1.5, 26, p + SLOPE_N * (-11.5), M["dark_steel"],
                    "08_FASTENERS_AND_DETAILS", rot=(TH, 0, 0), vertices=14)
    stem_objs.append(s)

def char_key(name, legend, x, v):
    p = key_pos(v) + Vector((x, 0, 0.0))
    cap = tapered_cyl(f"KEY_{name}", 5.75, 7.35, 6.6, p + SLOPE_N * 3.7, M["bakelite"],
                      "02_KEYBOARD", rot=(TH, 0, 0), vertices=28, bevel=1.15)
    # skirt ring
    sk = cyl(f"KEY_{name}_skirt", 8.65, 1.8, p + SLOPE_N * 0.85, M["bakelite"],
             "02_KEYBOARD", rot=(TH, 0, 0), vertices=28, bevel=0.8)
    # legend disc
    disc = bpy.ops.mesh.primitive_circle_add(vertices=28, radius=5.7, fill_type='NGON',
                                             location=p + SLOPE_N * (3.7 + 3.3 + 0.22),
                                             rotation=(TH, 0, 0))
    d = bpy.context.active_object
    d.name = f"KEY_{name}_legend"
    move_to_collection(d, "02_KEYBOARD")
    d.data.materials.append(legend_mat(name, f"legend_{name}.png"))
    add_stem(f"STEM_{name}", x, v)
    return cap

def wide_key(name, legend_file, x, v, w):
    p = key_pos(v) + Vector((x, 0, 0.0))
    cap = box(f"KEY_{name}", w, 15.5, 8.2, p + SLOPE_N * 3.9, M["bakelite"],
              "02_KEYBOARD", bevel=2.5, rot=(TH, 0, 0), segments=4)
    # top legend plate
    pl = bpy.ops.mesh.primitive_plane_add(size=1, location=p + SLOPE_N * (3.9 + 4.1 + 0.22),
                                          rotation=(TH, 0, 0))
    o = bpy.context.active_object
    o.name = f"KEY_{name}_legend"
    o.scale = (w - 5.5, 10.5, 1.0)
    apply_xf(o, rot=False, scale=True)
    o.rotation_euler = (TH, 0, 0)
    move_to_collection(o, "02_KEYBOARD")
    o.data.materials.append(legend_mat(name, f"legend_{legend_file}.png"))
    add_stem(f"STEM_{name}", x, v)

ROW_V = {"r1": 96.0, "r2": 76.5, "r3": 57.0, "r4": 37.5, "r5": 15.0}
ROW_XOFF = {"r1": 9.0, "r2": 2.0, "r3": 11.0, "r4": 6.5, "r5": 0.0}
CHAR_PITCH = 19.2

def layout_row(row_key, items):
    """items: list of (legend_name, display_w). Returns list of (name, x)."""
    widths = [w for _, w in items]
    total = sum(widths) + CHAR_PITCH - 16.0 + 0.0  # compact gaps
    # compute from pitch: sum of step per key
    steps = [w + (CHAR_PITCH - 16.0) for w in widths]
    total = sum(steps) - (CHAR_PITCH - 16.0)
    x = -total / 2.0 + ROW_XOFF[row_key]
    out = []
    for (nm, w) in items:
        half = w / 2.0
        out.append((nm, x + half))
        x += w + (CHAR_PITCH - 16.0)
    return out

r1_items = [(c, 16) for c in "1234567890"] + [("MINUS", 16)] + [("BACKW", 27)]
r2_items = [("TABW", 27)] + [(c, 16) for c in "QWERTYUIOP"] + [("LBRACKET", 16), ("RBRACKET", 16)]
r3_items = [(c, 16) for c in "ASDFGHJKL"] + [("SEMI", 16), ("QUOTE", 16)] + [("RETURN", 31)]
r4_items = [("SHIFT", 31)] + [(c, 16) for c in "ZXCVBNM"] + [("COMMA", 16), ("PERIOD", 16), ("SLASH", 16)] + [("SHIFT", 31)]

key_count = 0
for nm, x in layout_row("r1", r1_items):
    if nm == "BACKW": wide_key("BACKSPACE", "BACKW", x, ROW_V["r1"], 27); key_count += 1
    else: char_key(nm, None, x, ROW_V["r1"]); key_count += 1
for nm, x in layout_row("r2", r2_items):
    if nm == "TABW": wide_key("TAB", "TABW", x, ROW_V["r2"], 27); key_count += 1
    else: char_key(nm, None, x, ROW_V["r2"]); key_count += 1
for nm, x in layout_row("r3", r3_items):
    if nm == "RETURN": wide_key("RETURN", "RETURN", x, ROW_V["r3"], 31); key_count += 1
    else: char_key(nm, None, x, ROW_V["r3"]); key_count += 1
for i, (nm, x) in enumerate(layout_row("r4", r4_items)):
    if nm == "SHIFT": wide_key(f"SHIFT_{'L' if i == 0 else 'R'}", "SHIFT", x, ROW_V["r4"], 31); key_count += 1
    else: char_key(nm, None, x, ROW_V["r4"]); key_count += 1
# spacebar
p = key_pos(ROW_V["r5"])
box("KEY_SPACEBAR", 118, 16, 9.2, p + SLOPE_N * 4.0, M["bakelite"], "02_KEYBOARD",
    bevel=3.2, rot=(TH, 0, 0), segments=4)
add_stem("STEM_SPACE_L", -38, ROW_V["r5"])
add_stem("STEM_SPACE_R", 38, ROW_V["r5"])
key_count += 1
print("KEY_COUNT =", key_count)

# join stems into one object
bpy.ops.object.select_all(action='DESELECT')
for s in stem_objs:
    s.select_set(True)
if stem_objs:
    bpy.context.view_layer.objects.active = stem_objs[0]
    bpy.ops.object.join()
    stem_objs[0].name = "KEY_STEMS_ALL"
    move_to_collection(stem_objs[0], "02_KEYBOARD")

# ---------------------------------------------------- 03 CARRIAGE
# rail
cyl("CARRIAGE_rail", 3.4, 268, (0, 141, 144.5), M["blued"], "03_CARRIAGE",
    rot=(0, radians(90), 0), vertices=24)
box("CARRIAGE_rack", 244, 4.2, 1.7, (0, 141, 140.2), M["dark_steel"], "03_CARRIAGE")
# carriage end caps
box("CARRIAGE_endcap_R", 19, 84, 42, (146.5, 96, 121), M["charcoal"], "03_CARRIAGE", bevel=5.0, segments=4)
box("CARRIAGE_endcap_L", 19, 84, 42, (-146.5, 96, 121), M["charcoal"], "03_CARRIAGE", bevel=5.0, segments=4)
# margin stops on rail
box("CARRIAGE_margin_stop_L", 7.5, 6.0, 9.0, (-54, 141, 150.5), M["nickel"], "03_CARRIAGE", bevel=1.2)
box("CARRIAGE_margin_stop_R", 7.5, 6.0, 9.0, (68, 141, 150.5), M["nickel"], "03_CARRIAGE", bevel=1.2)
# margin release lever (left, under cap)
box("CARRIAGE_margin_release", 3.2, 5.0, 17, (-147, 48.5, 100), M["nickel"], "03_CARRIAGE",
    bevel=1.0, rot=(radians(-28), 0, 0))
# rail end screws
screw("SCREW_rail_end_L", Vector((-134.5, 141, 144.5)), (-1, 0, 0), coll="08_FASTENERS_AND_DETAILS", r=2.0)
screw("SCREW_rail_end_R", Vector((134.5, 141, 144.5)), (1, 0, 0), coll="08_FASTENERS_AND_DETAILS", r=2.0)
# carriage return lever (left) — bent chrome rod + bakelite knob
cu = bpy.data.curves.new("CARRIAGE_return_lever", 'CURVE'); cu.dimensions = '3D'
cu.bevel_depth = 2.65; cu.bevel_resolution = 3; cu.resolution_u = 16
sp = cu.splines.new('POLY')
lever_pts = [(-156, 93, 133), (-171, 90.5, 150), (-176, 63.5, 162), (-172.5, 25.5, 152.5)]
sp.points.add(len(lever_pts) - 1)
for i, p in enumerate(lever_pts):
    sp.points[i].co = (p[0], p[1], p[2], 1.0)
lo = bpy.data.objects.new("CARRIAGE_return_lever_arm", cu); colls["03_CARRIAGE"].objects.link(lo)
cu.materials.append(M["chrome"])
lever_dir = (Vector(lever_pts[-1]) - Vector(lever_pts[-2])).normalized()
knob_rot = lever_dir.to_track_quat('Z', 'Y').to_euler()
cyl("CARRIAGE_return_lever_boss", 5.6, 8, (-158.5, 93, 131.5), M["bakelite"], "03_CARRIAGE",
    rot=(0, radians(90), 0), vertices=28, bevel=0.8)
cyl("CARRIAGE_return_lever_knob", 8.7, 15.5, Vector(lever_pts[-1]) + lever_dir * 2.0,
    M["bakelite"], "03_CARRIAGE", rot=knob_rot, vertices=28, bevel=2.4)
cyl("CARRIAGE_return_lever_pin", 2.3, 2.0, Vector(lever_pts[-1]) + lever_dir * 10.2,
    M["chrome"], "03_CARRIAGE", rot=knob_rot, vertices=16)
# carriage return torsion spring
helix_spring("SPRING_carriage_return", (-159, 101, 122), (-148.5, 117, 112), 3.3, 6, 0.72, M["blued"], "08_FASTENERS_AND_DETAILS")

# ---------------------------------------------------- 04 PLATEN AND PAPER
cyl("PLATEN_roller", 15.0, 296, (0, 98, 128), M["rubber"], "04_PLATEN_AND_PAPER",
    rot=(0, radians(90), 0), vertices=48, bevel=1.4)
for side in (-1, 1):
    cyl(f"PLATEN_axle_{'L' if side < 0 else 'R'}", 4.6, 16, (side * 152, 98, 128), M["chrome"],
        "04_PLATEN_AND_PAPER", rot=(0, radians(90), 0), vertices=20)
    cyl(f"PLATEN_knob_{'L' if side < 0 else 'R'}", 16.3, 13, (side * 165.5, 98, 128), M["bakelite"],
        "04_PLATEN_AND_PAPER", rot=(0, radians(90), 0), vertices=36, bevel=2.2)
    cyl(f"PLATEN_knob_cap_{'L' if side < 0 else 'R'}", 8.8, 2.6, (side * 172.6, 98, 128), M["chrome"],
        "04_PLATEN_AND_PAPER", rot=(0, radians(90), 0), vertices=24)
    cyl(f"PLATEN_knob_dot_{'L' if side < 0 else 'R'}", 2.6, 1.2, (side * 174.2, 98, 128), M["interior"],
        "04_PLATEN_AND_PAPER", rot=(0, radians(90), 0), vertices=16)
# paper sheet (typed "THE ART OF PRECISION")
pap_tilt = radians(78)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 112.5, 180), rotation=(pap_tilt, 0, 0))
paper = bpy.context.active_object
paper.name = "PAPER_sheet"
paper.scale = (212, 152, 1.0)
apply_xf(paper, rot=False, scale=True)
paper.rotation_euler = (pap_tilt, 0, 0)
move_to_collection(paper, "04_PLATEN_AND_PAPER")
paper.data.materials.append(M["paper"])
# paper table (short support behind sheet)
box("PLATEN_paper_table", 250, 1.7, 64, (0, 127.5, 152.5), M["ivory"], "04_PLATEN_AND_PAPER",
    bevel=1.6, rot=(radians(24), 0, 0))
for side in (-1, 1):
    cyl(f"PLATEN_paper_finger_{side}", 1.15, 46, (side * 52, 131.5, 170), M["nickel"],
        "04_PLATEN_AND_PAPER", rot=(radians(8), 0, 0), vertices=12)
# scale ruler at base of paper table
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 116.5, 128.6), rotation=(radians(52), 0, 0))
scale_plane = bpy.context.active_object
scale_plane.name = "PLATEN_scale_ruler"
scale_plane.scale = (238, 9.0, 1.0)
apply_xf(scale_plane, rot=False, scale=True)
scale_plane.rotation_euler = (radians(52), 0, 0)
move_to_collection(scale_plane, "04_PLATEN_AND_PAPER")
scale_plane.data.materials.append(M["scale"])
box("PLATEN_scale_back", 240, 1.2, 11, (0, 117.2, 127.0), M["charcoal"], "04_PLATEN_AND_PAPER",
    bevel=0.8, rot=(radians(52), 0, 0))
# paper bail rod + rollers + arms
cyl("PLATEN_bail_rod", 3.3, 232, (0, 99, 143.5), M["chrome"], "04_PLATEN_AND_PAPER",
    rot=(0, radians(90), 0), vertices=20)
for rx in (-88, -28, 28, 88):
    cyl(f"PLATEN_bail_roller_{rx}", 5.6, 10, (rx, 99, 143.5), M["bakelite"], "04_PLATEN_AND_PAPER",
        rot=(0, radians(90), 0), vertices=24, bevel=1.2)
for side in (-1, 1):
    box(f"PLATEN_bail_arm_{side}", 8.0, 2.3, 34, (side * 127, 108.5, 137.2), M["nickel"],
        "04_PLATEN_AND_PAPER", bevel=1.0, rot=(radians(-22), 0, 0))
# adjustable paper guide blocks on the bail + guide flags
for side in (-1, 1):
    box(f"PLATEN_paper_guide_{side}", 8.5, 5.4, 6.4, (side * 54, 99, 143.5), M["nickel"],
        "04_PLATEN_AND_PAPER", bevel=1.3)
    box(f"PLATEN_paper_guide_flag_{side}", 1.15, 10.5, 17, (side * 54, 99.5, 153.5), M["chrome"],
        "04_PLATEN_AND_PAPER", bevel=0.5)
# paper release lever (right rear of platen)
box("PLATEN_paper_release", 3.6, 15, 2.8, (159, 116, 140.5), M["chrome"], "04_PLATEN_AND_PAPER",
    bevel=0.9, rot=(radians(-38), 0, 0))
cyl("PLATEN_paper_release_pivot", 2.5, 4.6, (159, 109.5, 136.5), M["nickel"], "04_PLATEN_AND_PAPER",
    rot=(0, radians(90), 0), vertices=16)

# ---------------------------------------------------- 05 RIBBON MECHANISM
def spool(side):
    x = side * 68.0
    cyl(f"RIBBON_spool_{'L' if side < 0 else 'R'}_flange_bot", 21.5, 2.6, (x, 17, 84.6), M["dark_steel"], "05_RIBBON_MECHANISM", vertices=36, bevel=0.7)
    cyl(f"RIBBON_spool_{'L' if side < 0 else 'R'}_roll", 18.8, 7.2, (x, 17, 89.3), M["spool_wrap"], "05_RIBBON_MECHANISM", vertices=36)
    cyl(f"RIBBON_spool_{'L' if side < 0 else 'R'}_flange_top", 21.5, 2.5, (x, 17, 94.2), M["dark_steel"], "05_RIBBON_MECHANISM", vertices=36, bevel=0.7)
    cyl(f"RIBBON_spool_{'L' if side < 0 else 'R'}_hub", 4.1, 6.6, (x, 17, 97.2), M["chrome"], "05_RIBBON_MECHANISM", vertices=20)
    cyl(f"RIBBON_spool_{'L' if side < 0 else 'R'}_nut", 3.2, 2.3, (x, 17, 100.6), M["nickel"], "05_RIBBON_MECHANISM", vertices=6)

spool(-1); spool(1)

def ribbon_seg(name, p1, p2):
    p1 = Vector(p1); p2 = Vector(p2)
    mid = (p1 + p2) / 2.0
    T_ = (p2 - p1).normalized()
    up = Vector((0, 0, 1))
    localY = (up - T_ * up.dot(T_)).normalized()
    localZ = T_.cross(localY).normalized()
    m = Matrix.Identity(3)
    m.col[0] = T_; m.col[1] = localY; m.col[2] = localZ
    bpy.ops.mesh.primitive_plane_add(size=1, location=mid, rotation=m.to_euler())
    o = bpy.context.active_object
    o.name = name
    o.scale = ((p2 - p1).length, 8.6, 1.0)
    apply_xf(o, rot=False, scale=True)
    o.rotation_euler = m.to_euler()
    move_to_collection(o, "05_RIBBON_MECHANISM")
    o.data.materials.append(M["ribbon"])
    return o

ribbon_seg("RIBBON_strip_left", (-68, 31, 89.5), (-24.5, 80, 116.5))
ribbon_seg("RIBBON_strip_right", (68, 31, 89.5), (24.5, 80, 116.5))
ribbon_seg("RIBBON_strip_center", (-24.5, 80, 116.5), (24.5, 80, 116.5))
# ribbon guide posts with eyes
for side, sign in (("L", -1), ("R", 1)):
    cyl(f"RIBBON_guide_post_{side}", 1.5, 9.5, (sign * 24.5, 80, 112.5), M["chrome"],
        "05_RIBBON_MECHANISM", vertices=14)
    bpy.ops.mesh.primitive_torus_add(major_radius=2.15, minor_radius=0.62, location=(sign * 24.5, 80, 117.6), rotation=(radians(90), 0, 0))
    eye = bpy.context.active_object
    eye.name = f"RIBBON_guide_eye_{side}"
    move_to_collection(eye, "05_RIBBON_MECHANISM")
    eye.data.materials.append(M["nickel"])
# ribbon vibrator (fork arms lifting ribbon to print line)
cyl("RIBBON_vibrator_arm_L", 1.5, 17.5, (-5.4, 75.8, 106.6), M["chrome"], "05_RIBBON_MECHANISM",
    rot=(radians(24), radians(-14), 0), vertices=12)
cyl("RIBBON_vibrator_arm_R", 1.5, 17.5, (5.4, 75.8, 106.6), M["chrome"], "05_RIBBON_MECHANISM",
    rot=(radians(24), radians(14), 0), vertices=12)
box("RIBBON_vibrator_block", 11, 3.2, 3.4, (0, 77.5, 99.5), M["dark_steel"], "05_RIBBON_MECHANISM", bevel=0.8)
# mounting brackets on the deck rear corners
for side in (-1, 1):
    box(f"RIBBON_bracket_{'L' if side < 0 else 'R'}", 16, 4, 9, (side * 108, 42, 85.5), M["dark_steel"], "05_RIBBON_MECHANISM", bevel=0.8)
    box(f"RIBBON_bracket_{'L' if side < 0 else 'R'}_up", 16, 4, 12, (side * 108, 44.5, 88), M["dark_steel"], "05_RIBBON_MECHANISM", bevel=0.8, rot=(radians(12), 0, 0))

# ---------------------------------------------------- 06 TYPEBARS
P_PRINT = Vector((0, 82.5, 126.2))
bar_objects = []
N_BARS = 40
for i in range(N_BARS):
    a = radians(-57.0 + (114.0 * i / (N_BARS - 1)))
    S = Vector((62.0 * sin(a), 82.0 - 62.0 * cos(a), 63.0))
    d = (P_PRINT - S)
    total = d.length
    d.normalize()
    length = total - 16.0
    center = S + d * (length / 2.0 + 2.0)
    localZ = d
    localX = Vector((0, 0, 1)).cross(d)
    if localX.length < 1e-4:
        localX = Vector((1, 0, 0))
    localX.normalize()
    localY = localZ.cross(localX)
    basis = Matrix.Identity(3)
    basis.col[0] = localX; basis.col[1] = localY; basis.col[2] = localZ
    rot = basis.to_euler()
    bar = box(f"TYPEBAR_{i+1:02d}", 2.5, 1.35, length, center, M["blued"], "06_TYPEBARS",
              bevel=0.35, rot=rot)
    E = S + d * (length + 2.0)
    slug = box(f"TYPEBAR_{i+1:02d}_slug", 6.4, 3.1, 4.6, E + d * 1.4, M["dark_steel"], "06_TYPEBARS",
               bevel=0.6, rot=rot)
    tip = box(f"TYPEBAR_{i+1:02d}_tip", 5.1, 1.5, 1.0, E + d * 3.6, M["nickel"], "06_TYPEBARS",
              bevel=0.25, rot=rot)
# typebar basket segment: two arc rails (tube curves along the basket arc)
def arc_rail(name, radius, z, wire, mat):
    pts = []
    for i in range(49):
        a = radians(206 + (128.0 * i / 48.0))
        pts.append((radius * cos(a), 82.0 + radius * sin(a), z))
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = wire; cu.bevel_resolution = 2; cu.resolution_u = 6
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, pt in enumerate(pts):
        sp.points[i].co = (pt[0], pt[1], pt[2], 1.0)
    o = bpy.data.objects.new(name, cu); colls["06_TYPEBARS"].objects.link(o)
    cu.materials.append(mat)
    return o

arc_rail("TYPEBAR_segment_rail_top", 60.0, 60.5, 2.6, M["blued"])
arc_rail("TYPEBAR_segment_rail_bottom", 52.0, 55.5, 1.8, M["dark_steel"])
for side in (-1, 1):
    a = radians(57) * side
    px, py = 56.0 * sin(a), 82.0 - 56.0 * cos(a)
    cyl(f"TYPEBAR_segment_post_{'L' if side < 0 else 'R'}", 3.1, 13, (px, py, 55), M["blued"],
        "06_TYPEBARS", vertices=16)
# universal bars (linkages across the width)
cyl("TYPEBAR_universal_bar_front", 1.7, 226, (0, 46, 70), M["chrome"], "06_TYPEBARS",
    rot=(0, radians(90), 0), vertices=14)
cyl("TYPEBAR_universal_bar_rear", 1.7, 226, (0, 52.5, 75.5), M["chrome"], "06_TYPEBARS",
    rot=(0, radians(90), 0), vertices=14)
# escapement gears
gear("TYPEBAR_escapement_wheel", 18, 8.6, 6.7, 4.0, (96, 60, 77.5), M["blued"], "06_TYPEBARS")
gear("TYPEBAR_escapement_pinion", 10, 4.7, 3.4, 5.2, (81.5, 56.5, 77.2), M["dark_steel"], "06_TYPEBARS")

# ---------------------------------------------------- 07 CONTROLS AND LEVERS
# ribbon selector (3-position lever, front of right spool area)
cyl("CTRL_ribbon_selector_base", 2.7, 3.4, (36.5, 33, 84.2), M["nickel"], "07_CONTROLS_AND_LEVERS",
    vertices=20)
box("CTRL_ribbon_selector_lever", 2.3, 15.5, 3.0, (36.5, 33, 90.6), M["nickel"],
    "07_CONTROLS_AND_LEVERS", bevel=0.8, rot=(radians(37), 0, 0))
cyl("CTRL_ribbon_selector_tip", 2.5, 3.0, (36.5, 38.2, 96.4), M["bakelite"], "07_CONTROLS_AND_LEVERS",
    vertices=16)
for i in range(3):
    a = radians(-38 + i * 38)
    dot = cyl(f"CTRL_ribbon_selector_dot_{i}", 0.85, 0.7,
              (36.5 + sin(a) * 8.2, 33 - cos(a) * 8.2, 83.6), M["brass"], "07_CONTROLS_AND_LEVERS",
              vertices=10)
# line spacing selector on right carriage end cap (vertical quadrant, 3 positions)
box("CTRL_spacing_quadrant", 2.2, 21, 25, (156.6, 84, 121), M["charcoal"], "07_CONTROLS_AND_LEVERS", bevel=1.0)
for i, zpos in enumerate((114.0, 121.0, 128.0)):
    cyl(f"CTRL_spacing_dot_{i}", 0.95, 0.7, (157.85, 77.5, zpos), M["brass"], "07_CONTROLS_AND_LEVERS",
        rot=(0, radians(90), 0), vertices=10)
cyl("CTRL_spacing_lever", 1.75, 20, (157.6, 84, 121), M["chrome"], "07_CONTROLS_AND_LEVERS",
    rot=(radians(-32), 0, 0), vertices=14)
cyl("CTRL_spacing_knob", 3.6, 4.2, (157.6, 90.7, 130.5), M["bakelite"], "07_CONTROLS_AND_LEVERS",
    vertices=18, bevel=0.8)
# knurled adjustment thumb wheels on the rear deck
for side in (-1, 1):
    wheel = cyl(f"CTRL_adjust_wheel_{'L' if side < 0 else 'R'}", 6.8, 3.6, (side * 102, 46, 85.3),
                M["dark_steel"], "07_CONTROLS_AND_LEVERS", vertices=26, bevel=0.9)
    cyl(f"CTRL_adjust_wheel_cap_{'L' if side < 0 else 'R'}", 2.2, 1.5, (side * 102, 46, 87.4),
        M["chrome"], "07_CONTROLS_AND_LEVERS", vertices=14)
# margin release lever already modelled in 03 (carriage group)

# ---------------------------------------------------- 08 FASTENERS AND DETAILS
screw("SCREW_apron_FL_top", Vector((-131, -152.2, 30.3)), (0, -1, 0), r=1.6)
screw("SCREW_apron_FR_top", Vector((131, -152.2, 30.3)), (0, -1, 0), r=1.6)
screw("SCREW_apron_FL_bot", Vector((-131, -152.2, 11.3)), (0, -1, 0), r=1.6)
screw("SCREW_apron_FR_bot", Vector((131, -152.2, 11.3)), (0, -1, 0), r=1.6)
screw("SCREW_access_TL", Vector((-64, 152.4, 76.5)), (0, 1, 0), r=1.7)
screw("SCREW_access_TR", Vector((64, 152.4, 76.5)), (0, 1, 0), r=1.7)
screw("SCREW_access_BL", Vector((-64, 152.4, 26.5)), (0, 1, 0), r=1.7)
screw("SCREW_access_BR", Vector((64, 152.4, 26.5)), (0, 1, 0), r=1.7)
screw("SCREW_cheek_R_rear", Vector((155.6, 118, 95)), (1, 0, 0), r=1.7)
screw("SCREW_cheek_L_rear", Vector((-155.6, 118, 95)), (-1, 0, 0), r=1.7)
screw("SCREW_deck_R", Vector((98, -12, 83.4)), (0, 0, 1), r=1.5)
screw("SCREW_deck_L", Vector((-98, -12, 83.4)), (0, 0, 1), r=1.5)
screw("SCREW_cap_R_front", Vector((156.4, 64, 133)), (1, 0, 0), r=1.6)
screw("SCREW_cap_R_rear", Vector((156.4, 128, 133)), (1, 0, 0), r=1.6)
screw("SCREW_cap_L_front", Vector((-156.4, 64, 133)), (-1, 0, 0), r=1.6)
screw("SCREW_cap_L_rear", Vector((-156.4, 128, 133)), (-1, 0, 0), r=1.6)
# hood top screw following hood slope normal
n_hood = Vector((0, -sin(radians(12.4)), cos(radians(12.4))))
screw("SCREW_hood_center", Vector((0, 126.5, 101.5)) + n_hood * 0.4, n_hood, r=1.6)
# rear corner coil springs (chassis <-> carriage ends)
helix_spring("SPRING_rear_R", (136, 131, 110.5), (161, 137, 105.5), 3.0, 5, 0.66, M["blued"], "08_FASTENERS_AND_DETAILS")
helix_spring("SPRING_rear_L", (-136, 131, 110.5), (-161, 137, 105.5), 3.0, 5, 0.66, M["blued"], "08_FASTENERS_AND_DETAILS")
# manufacturer badge on the front apron (brass backing + engraved face plate)
box("DETAIL_badge_model56", 74, 2.4, 30, (0, -152.9, 21.5), M["brass"], "08_FASTENERS_AND_DETAILS",
    bevel=2.3, segments=4)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -154.25, 21.5), rotation=(radians(90), 0, 0))
badge_face = bpy.context.active_object
badge_face.name = "DETAIL_badge_face"
badge_face.scale = (70.5, 26.5, 1.0)
apply_xf(badge_face, rot=False, scale=True)
badge_face.rotation_euler = (radians(90), 0, 0)
move_to_collection(badge_face, "08_FASTENERS_AND_DETAILS")
badge_face.data.materials.append(M["badge"])

for _o in bpy.data.objects:
    if _o.type == 'CAMERA':
        _o.hide_viewport = True

# ---------------------------------------------------- 10 LIGHTING (world, floors, lights)
world = bpy.data.worlds.new("WORLD_studio")
sc.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.062, 0.060, 0.058, 1.0)
bg.inputs["Strength"].default_value = 1.0

floor_mat_dark = new_mat("MAT_floor_dark")
set_in(floor_mat_dark, "Base Color", (0.155, 0.15, 0.145, 1.0))
set_in(floor_mat_dark, "Roughness", 0.55); set_in(floor_mat_dark, "Metallic", 0.0)
set_in(floor_mat_dark, "Coat Weight", 0.18); set_in(floor_mat_dark, "Coat Roughness", 0.4)
floor_mat_white = new_mat("MAT_floor_white")
set_in(floor_mat_white, "Base Color", (0.93, 0.93, 0.925, 1.0))
set_in(floor_mat_white, "Roughness", 0.85)

bpy.ops.mesh.primitive_plane_add(size=9000, location=(0, 0, 0))
floor_dark = bpy.context.active_object
floor_dark.name = "FLOOR_dark"
move_to_collection(floor_dark, "10_LIGHTING")
floor_dark.data.materials.append(floor_mat_dark)
bpy.ops.mesh.primitive_plane_add(size=9000, location=(0, 0, 0.05))
floor_white = bpy.context.active_object
floor_white.name = "FLOOR_white"
move_to_collection(floor_white, "10_LIGHTING")
floor_white.data.materials.append(floor_mat_white)
floor_white.hide_render = True
floor_white.hide_viewport = True

def add_light(name, energy, color, size_x, size_y, loc, target):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.color = color
    ld.shape = 'RECTANGLE'
    ld.size = size_x; ld.size_y = size_y
    o = bpy.data.objects.new(name, ld)
    colls["10_LIGHTING"].objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o

add_light("LIGHT_key", 10.2, (1.0, 0.97, 0.92), 380, 260, (350, -260, 430), (0, 0, 70))
add_light("LIGHT_fill", 6.0, (0.93, 0.96, 1.0), 540, 350, (-400, -240, 300), (0, 0, 70))
add_light("LIGHT_rim", 14.0, (1.0, 0.98, 0.94), 520, 170, (30, 360, 430), (0, 20, 90))

# ---------------------------------------------------- 09 CAMERAS
def add_camera(name, loc, target, lens, fstop, setup, macro=False):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36.0
    cd.clip_start = 1.0
    cd.clip_end = 30000.0
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = fstop
    locv = Vector(loc); tgt = Vector(target)
    cd.dof.focus_distance = (locv - tgt).length
    o = bpy.data.objects.new(name, cd)
    colls["09_CAMERAS"].objects.link(o)
    o.location = locv
    o.rotation_euler = (tgt - locv).to_track_quat('-Z', 'Y').to_euler()
    o["setup"] = setup
    o["macro"] = macro
    return o

# cameras stay in the file but don't clutter the viewport when opened
# (render.py only needs them to exist; unhide in the viewport if needed)
add_camera("CAM_01_hero", (315, -400, 235), (0, 0, 68), 40, 5.6, "HERO")
add_camera("CAM_02_front", (0, -580, 108), (0, 0, 82), 50, 8.0, "HERO")
add_camera("CAM_03_side", (568, -38, 96), (0, 10, 82), 50, 8.0, "HERO")
add_camera("CAM_04_rear", (140, 478, 198), (0, 55, 110), 40, 8.0, "HERO")
add_camera("CAM_05_top", (0, -28, 655), (0, 10, 78), 42, 11.0, "HERO")
add_camera("CAM_06_angled_top", (300, -330, 425), (0, 5, 68), 38, 8.0, "HERO")
add_camera("CAM_07_keyboard", (78, -238, 180), (0, -96, 52), 55, 4.0, "HERO")
add_camera("CAM_08_platen", (120, -98, 234), (2, 106, 168), 58, 4.0, "HERO")
add_camera("CAM_09_ribbon", (-95, -255, 320), (0, 45, 100), 48, 4.0, "HERO")
add_camera("CAM_10_typebars", (8, -118, 175), (2, 45, 103), 58, 3.6, "HERO")
add_camera("CAM_11_carriage_lever", (-338, -148, 240), (-158, 58, 140), 46, 2.8, "HERO")
add_camera("CAM_12_dark_studio", (358, -432, 222), (0, 5, 62), 40, 4.0, "DARK")
add_camera("CAM_13_white_studio", (330, -425, 220), (0, 8, 64), 42, 8.0, "WHITE")
add_camera("CAM_14_warm_studio", (-352, -405, 260), (0, 0, 66), 42, 4.0, "WARM")
add_camera("CAM_15_macro_details", (16, -258, 66), (0, -152.9, 23), 62, 3.6, "HERO", macro=True)
add_camera("CAM_16_spool_detail", (150, -95, 245), (66, 20, 99), 72, 4.0, "HERO", macro=True)

# ---------------------------------------------------- rescale mm -> metres
def rescale_to_metres():
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:
        o.select_set(True)
    if meshes:
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.convert(target='MESH')
    # convert curves -> mesh too
    curves = [o for o in bpy.data.objects if o.type == 'CURVE']
    bpy.ops.object.select_all(action='DESELECT')
    for o in curves:
        o.select_set(True)
    if curves:
        bpy.context.view_layer.objects.active = curves[0]
        bpy.ops.object.convert(target='MESH')
    # scale mesh vertex data + object locations deterministically (no pivot ambiguity)
    for mesh in bpy.data.meshes:
        mesh.transform(Matrix.Scale(0.001, 4))
    for o in bpy.data.objects:
        o.location = o.location * 0.001
    # cameras / lights: fix unit-dependent data manually
    for cam in [o for o in bpy.data.objects if o.type == 'CAMERA']:
        cam.data.clip_start = 0.01
        cam.data.clip_end = 40.0
        cam.data.dof.focus_distance *= 0.001
    for li in [o for o in bpy.data.objects if o.type == 'LIGHT']:
        li.data.size *= 0.001
        try:
            li.data.size_y *= 0.001
        except AttributeError:
            pass
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = 'METERS'

rescale_to_metres()

# ---------------------------------------------------- pack, save, export GLB
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
print("saved:", BLEND_OUT)

try:
    bpy.ops.export_scene.gltf(
        filepath=GLB_OUT,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_cameras=True,
    )
    print("exported GLB:", GLB_OUT)
except TypeError as e:
    print("export with lights failed, retrying minimal:", e)
    bpy.ops.export_scene.gltf(
        filepath=GLB_OUT,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
    )
    print("exported GLB (minimal):", GLB_OUT)
print("BUILD_DONE")
