"""Shared helpers for the RSV4 Factory build (Blender 4.2 bpy).
Coordinate system: metres, Z up, +X forward, +Y rider's left, origin = ground under rear axle.
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix, Euler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "ASSETS", "textures")

# ---------------------------------------------------------------- collections
def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c

_CUR = {"c": None}
def set_coll(c):
    _CUR["c"] = c

def _link(o, c=None):
    (c or _CUR["c"] or bpy.context.scene.collection).objects.link(o)
    return o

# ---------------------------------------------------------------- mesh basics
def mesh_obj(name, verts, faces, mat=None, smooth=True, c=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.validate(); me.update()
    o = bpy.data.objects.new(name, me)
    _link(o, c)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    if mat: assign(o, mat)
    return o

def assign(o, mat, slot_only=False):
    if isinstance(mat, str): mat = MAT[mat]
    if o.data is None: return o
    if len(o.data.materials) == 0: o.data.materials.append(mat)
    else: o.data.materials[0] = mat
    return o

def add_mat(o, mat):
    if isinstance(mat, str): mat = MAT[mat]
    o.data.materials.append(mat); return len(o.data.materials) - 1

def xform(o, loc=(0, 0, 0), rot=(0, 0, 0), scale=None):
    o.location = loc; o.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
    if scale: o.scale = scale
    return o

def parent(child, par, keep=True):
    child.parent = par
    if keep:
        # matrix_world is stale for freshly created objects; build it from the basis chain
        M = par.matrix_basis.copy(); q = par.parent
        while q is not None:
            M = q.matrix_basis @ M; q = q.parent
        child.matrix_parent_inverse = M.inverted()
    return child

def empty(name, loc=(0, 0, 0), c=None, size=0.05):
    o = bpy.data.objects.new(name, None); o.empty_display_size = size; o.location = loc
    return _link(o, c)

# ---------------------------------------------------------------- modifiers
def bevel(o, w=0.002, seg=2, angle=40, harden=True):
    m = o.modifiers.new("Bevel", 'BEVEL'); m.width = w; m.segments = seg
    m.limit_method = 'ANGLE'; m.angle_limit = math.radians(angle); m.harden_normals = harden
    m.miter_outer = 'MITER_ARC'
    return m

def subsurf(o, lv=2, rlv=None):
    m = o.modifiers.new("Subsurf", 'SUBSURF'); m.levels = lv; m.render_levels = rlv if rlv is not None else lv
    return m

def solidify(o, t=0.003, offset=-1, rim=True):
    m = o.modifiers.new("Solidify", 'SOLIDIFY'); m.thickness = t; m.offset = offset; m.use_rim = rim
    m.use_even_offset = True
    return m

def mirror_y(o, merge=True, bisect=False):
    m = o.modifiers.new("MirrorY", 'MIRROR'); m.use_axis = (False, True, False)
    m.use_mirror_merge = merge; m.use_bisect_axis = (False, bisect, False); m.mirror_object = None
    return m

def wnormal(o):
    try:
        m = o.modifiers.new("WNormal", 'WEIGHTED_NORMAL'); m.keep_sharp = True
    except Exception:
        pass

def auto_smooth(o, angle=35):
    # Blender 4.1+: smooth by angle via modifier node group not needed; use shade_smooth_by_angle op
    if o.type != 'MESH': return
    try:
        o.data.set_sharp_from_angle(angle=math.radians(angle))
    except Exception:
        pass
    for p in o.data.polygons: p.use_smooth = True

def boolean(o, cutter, op='DIFFERENCE', apply=False, hide=True):
    m = o.modifiers.new("Bool_" + cutter.name, 'BOOLEAN'); m.object = cutter; m.operation = op; m.solver = 'EXACT'
    if hide:
        cutter.hide_render = True; cutter.display_type = 'WIRE'; cutter.hide_viewport = True
    if apply: apply_mods(o)
    return m

def apply_mods(o):
    dg = bpy.context.evaluated_depsgraph_get()
    oe = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(oe)
    old = o.data; o.modifiers.clear(); o.data = me
    if old.users == 0: bpy.data.meshes.remove(old)
    return o

# ---------------------------------------------------------------- primitives
def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, bev=0.0, seg=2, c=None):
    sx, sy, sz = [s / 2 for s in size]
    v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz), (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    o = mesh_obj(name, v, f, mat, smooth=False, c=c)
    xform(o, loc, rot)
    if bev > 0: bevel(o, bev, seg, angle=60); auto_smooth(o, 40)
    return o

def cyl(name, r, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, n=32, bev=0.0, r2=None, cap=True, c=None):
    """Cylinder along local Z, centred."""
    r2 = r if r2 is None else r2
    v = []; f = []
    for i in range(n):
        a = 2 * math.pi * i / n
        v.append((r * math.cos(a), r * math.sin(a), -depth / 2))
    for i in range(n):
        a = 2 * math.pi * i / n
        v.append((r2 * math.cos(a), r2 * math.sin(a), depth / 2))
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, n + j, n + i))
    if cap:
        f.append(tuple(range(n - 1, -1, -1))); f.append(tuple(range(n, 2 * n)))
    o = mesh_obj(name, v, f, mat, smooth=True, c=c)
    xform(o, loc, rot)
    if bev > 0: bevel(o, bev, 2, angle=50)
    auto_smooth(o, 45)
    return o

def lathe(name, prof, n=48, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, closed=False, c=None, angle=360.0):
    """Revolve a profile [(r,z),...] around local Z."""
    full = abs(angle - 360.0) < 1e-6
    steps = n if full else n + 1
    v = []
    for i in range(steps):
        a = math.radians(angle) * i / n
        ca, sa = math.cos(a), math.sin(a)
        for (r, z) in prof:
            v.append((r * ca, r * sa, z))
    m = len(prof); f = []
    for i in range(n):
        i2 = (i + 1) % steps if full else i + 1
        for k in range(m - 1 if not closed else m):
            k2 = (k + 1) % m
            f.append((i * m + k, i2 * m + k, i2 * m + k2, i * m + k2))
    o = mesh_obj(name, v, f, mat, c=c)
    me = o.data
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bm.to_mesh(me); bm.free()
    xform(o, loc, rot); auto_smooth(o, 40)
    return o

def loft(name, sections, mat=None, closed_sec=True, cap_ends=True, c=None, smooth=True):
    """sections: list of lists of 3D points (equal length). Rows along sections."""
    n = len(sections[0]); v = []; f = []
    for s in sections:
        v.extend(s)
    rows = len(sections)
    seg = n if closed_sec else n - 1
    for r in range(rows - 1):
        for k in range(seg):
            k2 = (k + 1) % n
            f.append((r * n + k, r * n + k2, (r + 1) * n + k2, (r + 1) * n + k))
    if cap_ends and closed_sec:
        f.append(tuple(range(n - 1, -1, -1)))
        f.append(tuple(range((rows - 1) * n, rows * n)))
    o = mesh_obj(name, v, f, mat, smooth=smooth, c=c)
    return o

def rrect(w, h, r, n=4):
    """Rounded rectangle points (2D) centred, counter-clockwise, 4*(n+1) pts."""
    pts = []
    r = min(r, w / 2 - 1e-5, h / 2 - 1e-5)
    for cx, cy, a0 in [(w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)]:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def ellipse(w, h, n=24, squareness=0.0):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ca, sa = math.cos(a), math.sin(a)
        e = 2.0 / (2.0 + squareness * 6)
        x = math.copysign(abs(ca) ** e, ca) * w / 2; y = math.copysign(abs(sa) ** e, sa) * h / 2
        pts.append((x, y))
    return pts

def sweep_sections(path, profile_fn, up=Vector((0, 0, 1))):
    """Build loft sections along a polyline path. profile_fn(t)-> list of (u,v) 2D points.
    u is along the path's side axis, v along the 'up-ish' axis."""
    path = [Vector(p) for p in path]
    secs = []
    N = len(path)
    for i, p in enumerate(path):
        if i == 0: t = (path[1] - path[0])
        elif i == N - 1: t = (path[-1] - path[-2])
        else: t = (path[i + 1] - path[i - 1])
        t.normalize()
        side = t.cross(up)
        if side.length < 1e-6: side = t.cross(Vector((1, 0, 0)))
        side.normalize(); nup = side.cross(t).normalized()
        prof = profile_fn(i / (N - 1))
        secs.append([p + side * u + nup * v for (u, v) in prof])
    return secs

def tube(name, pts, r, mat=None, res=6, bev_res=8, c=None, smooth_curve=True, caps=True):
    """Curve tube through points (hoses, cables, exhaust pipes)."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.resolution_u = res; cu.bevel_depth = r; cu.bevel_resolution = bev_res; cu.use_fill_caps = caps
    if smooth_curve:
        sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
        for bp, p in zip(sp.bezier_points, pts):
            bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    else:
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for pp, p in zip(sp.points, pts): pp.co = (p[0], p[1], p[2], 1)
    o = bpy.data.objects.new(name, cu); _link(o, c)
    if mat:
        cu.materials.append(MAT[mat] if isinstance(mat, str) else mat)
    return o

def to_mesh(o):
    """Convert curve object to mesh in place (keeps name)."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    name = o.name; mats = list(o.data.materials) if o.data else []
    colls = list(o.users_collection)
    no = bpy.data.objects.new(name + "_m", me)
    for c in colls: c.objects.link(no)
    no.matrix_world = o.matrix_world.copy()
    bpy.data.objects.remove(o)
    no.name = name
    for p in me.polygons: p.use_smooth = True
    return no

def torus(name, R, r, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, n=48, m=12, c=None):
    v = []; f = []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            v.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(n):
        for j in range(m):
            i2 = (i + 1) % n; j2 = (j + 1) % m
            f.append((i * m + j, i2 * m + j, i2 * m + j2, i * m + j2))
    o = mesh_obj(name, v, f, mat, c=c); xform(o, loc, rot)
    return o

def bolt(name, d=0.008, L=0.02, loc=(0, 0, 0), rot=(0, 0, 0), head='hex', mat='bolt_zinc', c=None):
    """Simple fastener: socket cap (allen) or hex flange head, axis local Z, head at +Z."""
    if head == 'allen':
        prof = [(0, L * 0.5), (d * 0.75, L * 0.5), (d * 0.8, L * 0.5 + d * 0.1), (d * 0.8, L * 0.5 + d * 0.9),
                (d * 0.72, L * 0.5 + d), (d * 0.42, L * 0.5 + d), (d * 0.42, L * 0.5 + d * 0.55), (0, L * 0.5 + d * 0.55)]
        o = lathe(name, prof, n=24, loc=loc, rot=rot, mat=mat, c=c)
    else:
        prof = [(0, L * 0.5), (d * 1.05, L * 0.5), (d * 1.05, L * 0.5 + d * 0.15), (d * 0.8, L * 0.5 + d * 0.2),
                (d * 0.8, L * 0.5 + d * 0.75), (d * 0.7, L * 0.5 + d * 0.8), (0, L * 0.5 + d * 0.8)]
        o = lathe(name, prof, n=6, loc=loc, rot=rot, mat=mat, c=c)
        auto_smooth(o, 20)
    return o

def rod(name, a, b, r, mat=None, n=24, r2=None, bev=0.0, c=None):
    """Cylinder between two points."""
    a, b = Vector(a), Vector(b)
    d = b - a
    o = cyl(name, r, d.length, mat=mat, n=n, r2=r2, bev=bev, c=c)
    o.location = (a + b) / 2
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = d.to_track_quat('Z', 'Y')
    return o

def extrude_xz(name, pts, y0, y1, mat=None, bev=0.0, coll=None):
    """Polygon in XZ extruded along Y from y0..y1."""
    n=len(pts); vs=[(x,y0,z) for x,z in pts]+[(x,y1,z) for x,z in pts]; fs=[]
    fs.append(tuple(range(n-1,-1,-1))); fs.append(tuple(range(n,2*n)))
    for i in range(n):
        j=(i+1)%n; fs.append((i,j,n+j,n+i))
    o=mesh_obj(name, vs, fs, c=coll)
    if mat: assign(o, mat)
    if bev: bevel(o, bev, 2); wnormal(o)
    return o

def extrude_xy(name, pts, z0, z1, mat=None, bev=0.0, coll=None):
    n=len(pts); vs=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts]; fs=[]
    fs.append(tuple(range(n-1,-1,-1))); fs.append(tuple(range(n,2*n)))
    for i in range(n):
        j=(i+1)%n; fs.append((i,j,n+j,n+i))
    o=mesh_obj(name, vs, fs, c=coll)
    if mat: assign(o, mat)
    if bev: bevel(o, bev, 2); wnormal(o)
    return o

def look_rot(direction, up=Vector((0, 0, 1))):
    """Euler (degrees) rotating local +Z onto direction."""
    d = Vector(direction).normalized()
    q = Vector((0, 0, 1)).rotation_difference(d)
    e = q.to_euler('XYZ')
    return tuple(math.degrees(a) for a in e)

# ---------------------------------------------------------------- materials
MAT = {}

def _nodes(m):
    m.use_nodes = True
    nt = m.node_tree
    return nt, nt.nodes, nt.links

def principled(name, color=(0.5, 0.5, 0.5), metal=0.0, rough=0.5, coat=0.0, coat_rough=0.03, aniso=0.0,
               spec=0.5, ior=1.5, transm=0.0, alpha=1.0, emit=None, emit_str=0.0, sheen=0.0, bump=None,
               rough_noise=0.0, noise_scale=400.0, bump_strength=0.0, aniso_rot=0.0):
    m = bpy.data.materials.new(name); nt, N, L = _nodes(m)
    b = N.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (*color, 1)
    m.diffuse_color = (*[min(1, c ** 0.6) for c in color], 1); m.metallic = metal; m.roughness = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    b.inputs['IOR'].default_value = ior
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = coat_rough
    b.inputs['Anisotropic'].default_value = aniso
    b.inputs['Anisotropic Rotation'].default_value = aniso_rot
    b.inputs['Specular IOR Level'].default_value = spec
    b.inputs['Transmission Weight'].default_value = transm
    b.inputs['Alpha'].default_value = alpha
    b.inputs['Sheen Weight'].default_value = sheen
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = emit_str
    if rough_noise > 0 or bump_strength > 0:
        tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = noise_scale; nz.inputs['Detail'].default_value = 8
        L.new(tc.outputs['Object'], nz.inputs['Vector'])
        if rough_noise > 0:
            mr = N.new('ShaderNodeMapRange')
            mr.inputs['To Min'].default_value = max(0.0, rough - rough_noise)
            mr.inputs['To Max'].default_value = min(1.0, rough + rough_noise)
            L.new(nz.outputs['Fac'], mr.inputs['Value']); L.new(mr.outputs['Result'], b.inputs['Roughness'])
        if bump_strength > 0:
            bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump_strength
            bp.inputs['Distance'].default_value = 0.001
            L.new(nz.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    if alpha < 1.0:
        m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    MAT[name] = m
    return m

def mat_heat_tint(name, base=(0.62, 0.60, 0.58), axis='Z', lo=0.0, hi=1.0, invert=False):
    """Stainless with weld heat discolouration: straw -> bronze -> blue -> violet along an object axis."""
    m = bpy.data.materials.new(name); nt, N, L = _nodes(m)
    b = N.get("Principled BSDF")
    b.inputs['Metallic'].default_value = 1.0; b.inputs['Roughness'].default_value = 0.32
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['Object'], sep.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 18; nz.inputs['Detail'].default_value = 6
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = hi
    L.new(sep.outputs[{'X': 0, 'Y': 1, 'Z': 2}[axis]], mr.inputs['Value'])
    add = N.new('ShaderNodeMath'); add.operation = 'ADD'
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 0.12
    L.new(nz.outputs['Fac'], mul.inputs[0]); L.new(mr.outputs['Result'], add.inputs[0]); L.new(mul.outputs[0], add.inputs[1])
    ramp = N.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
    stops = [(0.0, (0.30, 0.20, 0.38)), (0.18, (0.16, 0.22, 0.42)), (0.35, (0.45, 0.30, 0.18)),
             (0.55, (0.70, 0.55, 0.32)), (0.75, (0.66, 0.62, 0.55)), (1.0, base)]
    if invert: stops = [(1 - p, c) for p, c in stops][::-1]
    cr.elements[0].position = stops[0][0]; cr.elements[0].color = (*stops[0][1], 1)
    cr.elements[1].position = stops[-1][0]; cr.elements[1].color = (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        e = cr.elements.new(p); e.color = (*c, 1)
    L.new(add.outputs[0], ramp.inputs['Fac']); L.new(ramp.outputs['Color'], b.inputs['Base Color'])
    MAT[name] = m
    return m

def mat_carbon(name, scale=180.0, gloss=True):
    """2x2 twill carbon: two perpendicular wave bands checkered in a twill offset."""
    m = bpy.data.materials.new(name); nt, N, L = _nodes(m)
    b = N.get("Principled BSDF")
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    w1 = N.new('ShaderNodeTexWave'); w1.wave_type = 'BANDS'; w1.bands_direction = 'X'; w1.inputs['Scale'].default_value = 1.0
    w2 = N.new('ShaderNodeTexWave'); w2.wave_type = 'BANDS'; w2.bands_direction = 'Y'; w2.inputs['Scale'].default_value = 1.0
    for w in (w1, w2):
        w.inputs['Distortion'].default_value = 0.0; L.new(mp.outputs['Vector'], w.inputs['Vector'])
    chk = N.new('ShaderNodeTexChecker'); chk.inputs['Scale'].default_value = 1.0
    L.new(mp.outputs['Vector'], chk.inputs['Vector'])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'FLOAT'
    L.new(chk.outputs['Fac'], mix.inputs['Factor']); L.new(w1.outputs['Fac'], mix.inputs[2]); L.new(w2.outputs['Fac'], mix.inputs[3])
    ramp = N.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (0.006, 0.006, 0.007, 1)
    ramp.color_ramp.elements[1].color = (0.05, 0.05, 0.055, 1)
    L.new(mix.outputs[0], ramp.inputs['Fac']); L.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.35; b.inputs['Anisotropic'].default_value = 0.6
    b.inputs['Coat Weight'].default_value = 1.0 if gloss else 0.0; b.inputs['Coat Roughness'].default_value = 0.02
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.15; bp.inputs['Distance'].default_value = 0.0004
    L.new(mix.outputs[0], bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    MAT[name] = m
    return m

def mat_image(name, path, rough=0.5, metal=0.0, emit=0.0, coat=0.0, uv='UV', alpha=False):
    m = bpy.data.materials.new(name); nt, N, L = _nodes(m)
    b = N.get("Principled BSDF")
    t = N.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path, check_existing=True)
    L.new(t.outputs['Color'], b.inputs['Base Color'])
    if emit > 0:
        L.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit
    if alpha:
        L.new(t.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    MAT[name] = m
    return m

def mat_brushed(name, color=(0.80, 0.80, 0.80), rough=0.28, radial=False, scale=(1, 1, 400)):
    """Brushed / machined aluminium: stretched noise drives roughness + micro bump."""
    m = bpy.data.materials.new(name); nt, N, L = _nodes(m)
    b = N.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Metallic'].default_value = 1.0
    m.diffuse_color = (*color, 1); m.metallic = 1.0
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = scale
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 60; nz.inputs['Detail'].default_value = 10
    if radial:
        # concentric machining rings: distance from local Z axis
        sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs['Vector'])
        vl = N.new('ShaderNodeVectorMath'); vl.operation = 'LENGTH'
        cmb = N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs['X'], cmb.inputs['X']); L.new(sep.outputs['Y'], cmb.inputs['Y'])
        L.new(cmb.outputs['Vector'], vl.inputs[0])
        w = N.new('ShaderNodeTexWave'); w.wave_type = 'BANDS'; w.inputs['Scale'].default_value = 1.0
        mpr = N.new('ShaderNodeMath'); mpr.operation = 'MULTIPLY'; mpr.inputs[1].default_value = 900.0
        L.new(vl.outputs['Value'], mpr.inputs[0])
        sn = N.new('ShaderNodeMath'); sn.operation = 'SINE'; L.new(mpr.outputs[0], sn.inputs[0])
        src = sn.outputs[0]
    else:
        L.new(tc.outputs['Object'], mp.inputs['Vector']); L.new(mp.outputs['Vector'], nz.inputs['Vector'])
        src = nz.outputs['Fac']
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = rough * 0.75; mr.inputs['To Max'].default_value = rough * 1.3
    L.new(src, mr.inputs['Value']); L.new(mr.outputs['Result'], b.inputs['Roughness'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.05; bp.inputs['Distance'].default_value = 0.0002
    L.new(src, bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Anisotropic'].default_value = 0.5
    MAT[name] = m
    return m

def mat_braided(name):
    m = bpy.data.materials.new(name); nt, N, L = _nodes(m)
    b = N.get("Principled BSDF"); b.inputs['Metallic'].default_value = 1.0; b.inputs['Base Color'].default_value = (0.7, 0.7, 0.72, 1)
    b.inputs['Roughness'].default_value = 0.3
    tc = N.new('ShaderNodeTexCoord'); w = N.new('ShaderNodeTexWave'); w.inputs['Scale'].default_value = 900; w.bands_direction = 'DIAGONAL'
    w2 = N.new('ShaderNodeTexWave'); w2.inputs['Scale'].default_value = 900; w2.bands_direction = 'DIAGONAL'
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (-1, 1, 1)
    L.new(tc.outputs['Generated'], w.inputs['Vector']); L.new(tc.outputs['Generated'], mp.inputs['Vector']); L.new(mp.outputs['Vector'], w2.inputs['Vector'])
    mx = N.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'
    L.new(w.outputs['Fac'], mx.inputs[0]); L.new(w2.outputs['Fac'], mx.inputs[1])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6
    L.new(mx.outputs[0], bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    MAT[name] = m
    return m

def mat_tyre(name):
    """Tyre rubber: very dark, rough, slight sheen, micro bump; scrubbed band slightly lighter via Generated Z."""
    m = principled(name, color=(0.012, 0.012, 0.013), rough=0.88, sheen=0.05, bump_strength=0.06, noise_scale=900, rough_noise=0.05)
    return m

def mat_livery(name, cal):
    """Projection-mapped livery. cal = dict loaded from ASSETS/textures/livery_calibration.json.
    Side projections (left/right by world-Y sign), top and front projections are blended by normal."""
    m = bpy.data.materials.new(name); nt, N, L = _nodes(m)
    b = N.get("Principled BSDF")
    b.inputs['Coat Weight'].default_value = 0.55; b.inputs['Coat Roughness'].default_value = 0.04
    geo = N.new('ShaderNodeNewGeometry')
    sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs['Vector'])
    nsep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Normal'], nsep.inputs['Vector'])
    axis = {'X': 'X', 'Y': 'Y', 'Z': 'Z'}

    def proj(view):
        c = cal[view]; W = c['width']; H = c['height']
        def uvcoord(spec, size, flip):
            ax, a0, k = spec
            mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY_ADD'
            # px = a0 + k*val ; u = px/size ; v = 1 - py/H
            if not flip:
                mul.inputs[1].default_value = k / size; mul.inputs[2].default_value = a0 / size
            else:
                mul.inputs[1].default_value = -k / size; mul.inputs[2].default_value = 1.0 - a0 / size
            L.new(sep.outputs[axis[ax]], mul.inputs[0])
            return mul.outputs[0]
        u = uvcoord(c['u'], W, False); v = uvcoord(c['v'], H, True)
        cmb = N.new('ShaderNodeCombineXYZ'); L.new(u, cmb.inputs['X']); L.new(v, cmb.inputs['Y'])
        ta = N.new('ShaderNodeTexImage'); ta.image = bpy.data.images.load(os.path.join(TEX, f"livery_{view}_albedo.png"), check_existing=True)
        ta.extension = 'EXTEND'; ta.interpolation = 'Cubic'
        tr = N.new('ShaderNodeTexImage'); tr.image = bpy.data.images.load(os.path.join(TEX, f"livery_{view}_rough.png"), check_existing=True)
        tr.image.colorspace_settings.name = 'Non-Color'; tr.extension = 'EXTEND'
        L.new(cmb.outputs['Vector'], ta.inputs['Vector']); L.new(cmb.outputs['Vector'], tr.inputs['Vector'])
        return ta.outputs['Color'], tr.outputs['Color']

    cl, rl = proj('left'); cr_, rr = proj('right'); cf, rf = proj('front'); ct, rt = proj('top')
    # side select by sign of Y
    gt = N.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.0
    L.new(sep.outputs['Y'], gt.inputs[0])
    ms = N.new('ShaderNodeMix'); ms.data_type = 'RGBA'; L.new(gt.outputs[0], ms.inputs['Factor']); L.new(cr_, ms.inputs[6]); L.new(cl, ms.inputs[7])
    msr = N.new('ShaderNodeMix'); msr.data_type = 'RGBA'; L.new(gt.outputs[0], msr.inputs['Factor']); L.new(rr, msr.inputs[6]); L.new(rl, msr.inputs[7])
    # weights: front where normal.x high AND x > 1.30 ; top where normal.z high
    def wpow(sock, p, lo):
        a = N.new('ShaderNodeMath'); a.operation = 'ABSOLUTE'; L.new(sock, a.inputs[0])
        s = N.new('ShaderNodeMapRange'); s.inputs['From Min'].default_value = lo; s.inputs['From Max'].default_value = lo + 0.25
        L.new(a.outputs[0], s.inputs['Value']); return s.outputs['Result']
    wf_n = wpow(nsep.outputs['X'], 4, 0.55)
    xg = N.new('ShaderNodeMapRange'); xg.inputs['From Min'].default_value = 1.30; xg.inputs['From Max'].default_value = 1.38
    L.new(sep.outputs['X'], xg.inputs['Value'])
    wf = N.new('ShaderNodeMath'); wf.operation = 'MULTIPLY'; L.new(wf_n, wf.inputs[0]); L.new(xg.outputs['Result'], wf.inputs[1])
    wt_n = wpow(nsep.outputs['Z'], 4, 0.72)
    # top projection only on tank (0.45 < x < 1.10)
    xt0 = N.new('ShaderNodeMapRange'); xt0.inputs['From Min'].default_value = 0.50; xt0.inputs['From Max'].default_value = 0.55
    L.new(sep.outputs['X'], xt0.inputs['Value'])
    xt1 = N.new('ShaderNodeMapRange'); xt1.inputs['From Min'].default_value = 1.10; xt1.inputs['From Max'].default_value = 1.05
    L.new(sep.outputs['X'], xt1.inputs['Value'])
    wt = N.new('ShaderNodeMath'); wt.operation = 'MULTIPLY'; L.new(wt_n, wt.inputs[0]); L.new(xt0.outputs['Result'], wt.inputs[1])
    wt2 = N.new('ShaderNodeMath'); wt2.operation = 'MULTIPLY'; L.new(wt.outputs[0], wt2.inputs[0]); L.new(xt1.outputs['Result'], wt2.inputs[1])
    m1 = N.new('ShaderNodeMix'); m1.data_type = 'RGBA'; L.new(wt2.outputs[0], m1.inputs['Factor']); L.new(ms.outputs[2], m1.inputs[6]); L.new(ct, m1.inputs[7])
    m2 = N.new('ShaderNodeMix'); m2.data_type = 'RGBA'; L.new(wf.outputs[0], m2.inputs['Factor']); L.new(m1.outputs[2], m2.inputs[6]); L.new(cf, m2.inputs[7])
    r1 = N.new('ShaderNodeMix'); r1.data_type = 'RGBA'; L.new(wt2.outputs[0], r1.inputs['Factor']); L.new(msr.outputs[2], r1.inputs[6]); L.new(rt, r1.inputs[7])
    r2 = N.new('ShaderNodeMix'); r2.data_type = 'RGBA'; L.new(wf.outputs[0], r2.inputs['Factor']); L.new(r1.outputs[2], r2.inputs[6]); L.new(rf, r2.inputs[7])
    L.new(m2.outputs[2], b.inputs['Base Color'])
    rsep = N.new('ShaderNodeSeparateColor'); L.new(r2.outputs[2], rsep.inputs['Color'])
    L.new(rsep.outputs['Red'], b.inputs['Roughness'])
    # clearcoat only where glossy (rough < 0.3)
    cw = N.new('ShaderNodeMapRange'); cw.inputs['From Min'].default_value = 0.35; cw.inputs['From Max'].default_value = 0.15
    cw.inputs['To Min'].default_value = 0.08; cw.inputs['To Max'].default_value = 0.9
    L.new(rsep.outputs['Red'], cw.inputs['Value']); L.new(cw.outputs['Result'], b.inputs['Coat Weight'])
    # micro orange-peel on paint
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1800; nz.inputs['Detail'].default_value = 2
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.025
    L.new(geo.outputs['Position'], nz.inputs['Vector']); L.new(nz.outputs['Fac'], bp.inputs['Height'])
    L.new(bp.outputs['Normal'], b.inputs['Coat Normal'])
    MAT[name] = m
    return m

def build_materials(cal):
    P = principled
    # paints
    P('paint_black_matte', (0.012, 0.012, 0.013), rough=0.45, coat=0.15, coat_rough=0.25)
    P('paint_black_gloss', (0.008, 0.008, 0.009), rough=0.15, coat=1.0)
    P('paint_violet', (0.10, 0.018, 0.55), rough=0.2, coat=1.0)
    P('frame_black', (0.015, 0.015, 0.016), metal=0.25, rough=0.38, coat=0.4, coat_rough=0.12, rough_noise=0.05)
    mat_livery('paint_livery', cal); MAT['paint_livery'].diffuse_color = (0.08, 0.04, 0.25, 1)
    for nm, dc in (('screen_smoke', (0.25, 0.28, 0.30, 0.35)), ('reservoir_smoke', (0.3, 0.28, 0.22, 0.6)),
                   ('mirror_glass', (0.7, 0.72, 0.75, 1)), ('led_white', (0.9, 0.95, 1.0, 1)),
                   ('led_red', (0.8, 0.05, 0.05, 1)), ('reflector_amber', (0.9, 0.5, 0.05, 1))):
        if nm in MAT: MAT[nm].diffuse_color = dc
    
    # metals
    mat_brushed('alu_satin', (0.80, 0.80, 0.81), rough=0.30, scale=(1, 1, 300))
    mat_brushed('alu_machined', (0.86, 0.86, 0.87), rough=0.18, radial=True)
    P('alu_cast', (0.70, 0.70, 0.71), metal=1.0, rough=0.48, rough_noise=0.12, bump_strength=0.15, noise_scale=1500)
    P('alu_black_anod', (0.03, 0.03, 0.032), metal=0.9, rough=0.32)
    P('alu_grey_anod', (0.30, 0.30, 0.31), metal=1.0, rough=0.35, rough_noise=0.05)   # Brembo Hypure natural
    P('magnesium', (0.075, 0.075, 0.08), metal=0.6, rough=0.55, rough_noise=0.12, bump_strength=0.2, noise_scale=900)  # cam covers / casings
    P('engine_black', (0.025, 0.025, 0.027), metal=0.35, rough=0.5, rough_noise=0.1, bump_strength=0.15, noise_scale=1200)
    P('steel_stainless', (0.66, 0.66, 0.67), metal=1.0, rough=0.25)
    P('steel_dark', (0.12, 0.12, 0.13), metal=1.0, rough=0.42)
    P('chrome', (0.9, 0.9, 0.9), metal=1.0, rough=0.05)
    P('bolt_zinc', (0.62, 0.63, 0.66), metal=1.0, rough=0.3)
    P('bolt_black', (0.03, 0.03, 0.03), metal=0.8, rough=0.35)
    P('bolt_ti', (0.50, 0.47, 0.42), metal=1.0, rough=0.28)
    mat_brushed('titanium_brushed', (0.55, 0.53, 0.50), rough=0.28, scale=(1, 1, 500))
    mat_heat_tint('header_tint', axis='Z', lo=-0.05, hi=0.45)
    mat_heat_tint('cat_tint', base=(0.55, 0.47, 0.36), axis='X', lo=-0.2, hi=0.2)
    mat_brushed('disc_steel', (0.70, 0.70, 0.71), rough=0.22, radial=True)
    P('disc_carrier', (0.06, 0.06, 0.065), metal=0.9, rough=0.35)
    P('ohlins_gold', (0.85, 0.62, 0.22), metal=1.0, rough=0.16)       # TiN fork tubes
    P('ohlins_gold_anod', (0.80, 0.55, 0.15), metal=1.0, rough=0.28)
    P('ohlins_yellow', (0.85, 0.62, 0.02), rough=0.3, coat=0.6)       # spring
    P('fork_black', (0.02, 0.02, 0.022), metal=0.8, rough=0.3)
    P('chain_steel', (0.35, 0.35, 0.36), metal=1.0, rough=0.45)
    P('sprocket_alu', (0.06, 0.06, 0.065), metal=0.9, rough=0.3)
    # rubbers / plastics
    mat_tyre('tyre'); MAT['tyre'].diffuse_color = (0.05, 0.05, 0.05, 1)
    P('rubber', (0.02, 0.02, 0.02), rough=0.7, bump_strength=0.1, noise_scale=600)
    P('hose_rubber', (0.025, 0.025, 0.025), rough=0.62)
    P('plastic_black', (0.02, 0.02, 0.021), rough=0.55, bump_strength=0.25, noise_scale=2500)
    P('plastic_gloss_black', (0.01, 0.01, 0.011), rough=0.12, coat=0.6)
    P('seat_vinyl', (0.02, 0.02, 0.021), rough=0.62, sheen=0.3, bump_strength=0.35, noise_scale=700)
    P('seat_alcantara', (0.028, 0.028, 0.03), rough=0.85, sheen=0.6, bump_strength=0.2, noise_scale=1600)
    mat_carbon('carbon'); MAT['carbon'].diffuse_color = (0.03, 0.03, 0.035, 1)
    mat_braided('braided')
    P('brake_pad', (0.08, 0.075, 0.07), metal=0.3, rough=0.8)
    P('cable_black', (0.015, 0.015, 0.015), rough=0.5)
    P('connector_grey', (0.12, 0.12, 0.13), rough=0.55)
    P('wire_red', (0.4, 0.02, 0.02), rough=0.5)
    P('radiator_core', (0.06, 0.06, 0.065), metal=0.8, rough=0.5)
    # glass / lights
    P('screen_poly', (0.85, 0.86, 0.88), rough=0.02, transm=1.0, ior=1.58, spec=0.5)
    P('screen_smoke', (0.25, 0.25, 0.27), rough=0.02, transm=1.0, ior=1.58)
    P('lens_clear', (1, 1, 1), rough=0.0, transm=1.0, ior=1.49)
    P('lens_red', (0.8, 0.02, 0.02), rough=0.02, transm=1.0, ior=1.49)
    P('lens_amber', (1.0, 0.45, 0.02), rough=0.05, transm=0.9, ior=1.49)
    P('reflector_chrome', (0.92, 0.92, 0.94), metal=1.0, rough=0.08)
    P('led_white', (1, 1, 1), emit=(0.9, 0.95, 1.0), emit_str=6.0, rough=0.3)
    P('led_off', (0.7, 0.7, 0.72), metal=0.2, rough=0.25)
    P('led_red', (0.3, 0.0, 0.0), emit=(1.0, 0.02, 0.01), emit_str=3.0)
    P('mirror_glass', (0.95, 0.95, 0.95), metal=1.0, rough=0.0)
    P('reservoir_smoke', (0.28, 0.24, 0.20), rough=0.1, transm=0.6, ior=1.5)
    P('reflector_amber', (1.0, 0.35, 0.0), rough=0.15, coat=1.0)
    P('ground_white', (0.82, 0.82, 0.82), rough=0.6)
    return MAT
