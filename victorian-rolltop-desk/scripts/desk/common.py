"""
common.py — shared geometry helpers for the Victorian roll-top desk build.

Conventions used throughout the project (metres, real-world scale):
    +X = desk width, centred on 0
    +Y = depth, y = 0 at the front face of the pedestals, increasing toward the rear
    +Z = height, z = 0 at the floor
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

DEG = math.pi / 180.0


# ----------------------------------------------------------------------------- scene utils
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.length_unit = 'METERS'
    sc.unit_settings.scale_length = 1.0
    return sc


def collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col


COLLECTIONS = [
    "PEDESTAL_CARCASSES_AND_PANELS",
    "DESKTOP_AND_WRITING_SURFACE",
    "TAMBOUR_SLATS_BACKING_AND_TRACKS",
    "UPPER_FITTED_INTERIOR",
    "33_INTERNAL_DRAWERS",
    "VERTICAL_PIGEONHOLES_AND_LETTER_RACKS",
    "PEDESTAL_DRAWERS_AND_JOINERY",
    "LOCKS_KEYS_AND_LINKAGE",
    "WRITING_SLIDES_AND_SUPPORTS",
    "BRASS_HARDWARE_AND_CASTORS",
    "MATERIALS_AND_TEST_SWATCHES",
    "CAMERAS_LIGHTS_AND_STAGING",
]


def ensure_collections():
    root = collection("VICTORIAN_ROLLTOP_DESK")
    out = {}
    for name in COLLECTIONS:
        out[name] = collection(name, root)
    return out


def link(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


# ----------------------------------------------------------------------------- mesh makers
def new_mesh_obj(name, bm, col, mat=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if mat is not None:
        ob.data.materials.append(mat)
    return ob


def box_bm(sx, sy, sz, center=(0, 0, 0), matrix=None):
    """Axis-aligned box as a fresh bmesh."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector(center), verts=bm.verts)
    return bm


def box(name, size, center, col, mat=None, bevel=0.0, bevel_segments=2,
        bevel_profile=0.5, smooth=False, rot_z=0.0):
    """Box with optional bevel modifier (kept as a modifier so it stays editable)."""
    bm = box_bm(size[0], size[1], size[2])
    ob = new_mesh_obj(name, bm, col, mat, smooth=smooth)
    ob.location = Vector(center)
    if rot_z:
        ob.rotation_euler[2] = rot_z
    if bevel > 0:
        m = ob.modifiers.new("bevel", 'BEVEL')
        m.width = bevel
        m.segments = bevel_segments
        m.profile = bevel_profile
        m.limit_method = 'ANGLE'
        m.angle_limit = 40 * DEG
        m.harden_normals = False
    return ob


def cylinder(name, radius, depth, center, col, mat=None, verts=32, axis='Z',
             bevel=0.0, smooth=True, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                          radius1=radius, radius2=(radius if r2 is None else r2),
                          depth=depth)
    if axis == 'Y':
        bmesh.ops.rotate(bm, matrix=Matrix.Rotation(math.pi / 2, 3, 'X'), verts=bm.verts)
    elif axis == 'X':
        bmesh.ops.rotate(bm, matrix=Matrix.Rotation(math.pi / 2, 3, 'Y'), verts=bm.verts)
    ob = new_mesh_obj(name, bm, col, mat, smooth=smooth)
    ob.location = Vector(center)
    if bevel > 0:
        m = ob.modifiers.new("bevel", 'BEVEL')
        m.width = bevel
        m.segments = 2
        m.limit_method = 'ANGLE'
    return ob


def sphere(name, radius, center, col, mat=None, segs=24, rings=16, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius)
    ob = new_mesh_obj(name, bm, col, mat, smooth=True)
    ob.location = Vector(center)
    ob.scale = Vector(scale)
    return ob


def poly_solid(name, profile_pts, extrude_axis, extrude_len, col, mat=None, smooth=False):
    """Sweep a closed 2-D profile (list of (a,b) in the plane perpendicular to
    extrude_axis) along that axis. Used for mouldings, nosing and rails."""
    bm = bmesh.new()
    verts = []
    for (a, b) in profile_pts:
        if extrude_axis == 'X':
            co = Vector((0.0, a, b))
        elif extrude_axis == 'Y':
            co = Vector((a, 0.0, b))
        else:
            co = Vector((a, b, 0.0))
        verts.append(bm.verts.new(co))
    face = bm.faces.new(verts)
    r = bmesh.ops.extrude_face_region(bm, geom=[face])
    new_verts = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    delta = {'X': Vector((extrude_len, 0, 0)),
             'Y': Vector((0, extrude_len, 0)),
             'Z': Vector((0, 0, extrude_len))}[extrude_axis]
    bmesh.ops.translate(bm, vec=delta, verts=new_verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_mesh_obj(name, bm, col, mat, smooth=smooth)
    return ob


def moulding_profile(width, depth, kind="ovolo", steps=9):
    """Return a closed 2-D profile for a small moulding, origin at inner-bottom corner."""
    pts = [(0.0, 0.0)]
    if kind == "ovolo":
        for i in range(steps + 1):
            t = i / steps
            a = width * (1 - math.cos(t * math.pi / 2))
            b = depth * math.sin(t * math.pi / 2) * 0.5 + depth * 0.5 * t
            pts.append((a, b))
        pts.append((width, depth))
    elif kind == "cove":
        for i in range(steps + 1):
            t = i / steps
            a = width * math.sin(t * math.pi / 2)
            b = depth * (1 - math.cos(t * math.pi / 2))
            pts.append((a, b))
    elif kind == "bead":
        for i in range(steps + 1):
            t = i / steps
            a = width * t
            b = depth * math.sin(t * math.pi)
            pts.append((a, b))
    pts.append((0.0, depth))
    # drop duplicate consecutive points
    out = []
    for p in pts:
        if not out or (abs(p[0] - out[-1][0]) > 1e-9 or abs(p[1] - out[-1][1]) > 1e-9):
            out.append(p)
    return out


def tapered_box(name, size_bottom, size_top, height, center, col, mat=None, bevel=0.0):
    """Frustum-ish solid: useful for splayed legs and tapered drawer sides."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        t = 0.5 if v.co.z < 0 else -0.5   # cube verts at +-0.5
        sx = size_bottom[0] if v.co.z < 0 else size_top[0]
        sy = size_bottom[1] if v.co.z < 0 else size_top[1]
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= height
    ob = new_mesh_obj(name, bm, col, mat)
    ob.location = Vector(center)
    if bevel > 0:
        m = ob.modifiers.new("bevel", 'BEVEL')
        m.width = bevel
        m.segments = 2
        m.limit_method = 'ANGLE'
    return ob


# ----------------------------------------------------------------------------- modifiers
def add_bevel(ob, width, segments=2, angle=40, profile=0.5):
    m = ob.modifiers.new("bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.profile = profile
    m.limit_method = 'ANGLE'
    m.angle_limit = angle * DEG
    return m


def add_subsurf(ob, levels=1, render_levels=None):
    m = ob.modifiers.new("subsurf", 'SUBSURF')
    m.levels = levels
    m.render_levels = levels if render_levels is None else render_levels
    m.use_limit_surface = True
    return m


def add_displace(ob, tex, strength, mid=0.5):
    m = ob.modifiers.new("displace", 'DISPLACE')
    m.texture = tex
    m.strength = strength
    m.mid_level = mid
    return m


# ----------------------------------------------------------------------------- measurement
def evaluated_stats():
    """Real triangles actually present after modifiers, per object and total."""
    dg = bpy.context.evaluated_depsgraph_get()
    per_obj = {}
    total_v = total_t = 0
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH':
            continue
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        v = len(me.vertices)
        ev.to_mesh_clear()
        per_obj[ob.name] = (v, t)
        total_v += v
        total_t += t
    return total_v, total_t, per_obj


# ----------------------------------------------------------------------------- density
def densify(ob, cuts):
    """Subdivide every face of a mesh into a uniform grid so that a Displace modifier
    can show real grain relief. Returns the object."""
    if cuts <= 0 or ob.type != 'MESH':
        return ob
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return ob


def grain_displace_textures():
    """Anisotropic procedural textures used as actual geometry displacement."""
    out = {}
    for axis, scale in (('x', (1.0, 38.0, 38.0)), ('y', (38.0, 1.0, 38.0)),
                        ('z', (38.0, 38.0, 1.0))):
        name = f"grain_disp_{axis}"
        t = bpy.data.textures.get(name)
        if t is None:
            t = bpy.data.textures.new(name, 'CLOUDS')
        t.noise_scale = 0.0012
        t.noise_depth = 3
        t.noise_basis = 'BLENDER_ORIGINAL'
        # Texture datablocks expose noise_scale; anisotropic stretch is applied through
        # the modifier's texture coordinates, so a per-axis scale is set on the empty
        # mapping instead (see apply_density).
        out[axis] = t
    return out
