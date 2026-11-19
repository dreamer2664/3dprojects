"""Render presets for the RSV4 model.
blender -b MODELS/rsv4_factory_2026.blend -P scripts/render.py -- --shot hero_front34 [--samples 64] [--res 1600x1000]
       [--preview path.png]  (quick QC to a scratch path, workbench/eevee-free low-sample cycles)
Final renders go to RENDERS/YYYY-MM-DD_HH-MM-SS__<desc>.png (real wall-clock time at render start); never overwrites.
"""
import bpy, sys, os, math, time, datetime
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
def flag(k): return k in argv

sc = bpy.context.scene
HDRI = os.path.join(ROOT, "ASSETS", "hdri")
CENTER = Vector((0.72, 0.0, 0.58))

def world_hdri(name, strength=1.0, rot=0.0, visible=True, bg_color=None):
    w = bpy.data.worlds.get("W") or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    N = w.node_tree.nodes; L = w.node_tree.links; N.clear()
    out = N.new('ShaderNodeOutputWorld'); bg = N.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = strength
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value[2] = math.radians(rot)
    env = N.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(HDRI, name), check_existing=True)
    L.new(tc.outputs['Generated'], mp.inputs['Vector']); L.new(mp.outputs['Vector'], env.inputs['Vector']); L.new(env.outputs['Color'], bg.inputs['Color'])
    if bg_color is not None:
        # camera sees flat colour, lighting from HDRI
        bg2 = N.new('ShaderNodeBackground'); bg2.inputs['Color'].default_value = (*bg_color, 1)
        lp = N.new('ShaderNodeLightPath'); mx = N.new('ShaderNodeMixShader')
        L.new(lp.outputs['Is Camera Ray'], mx.inputs['Fac']); L.new(bg.outputs[0], mx.inputs[1]); L.new(bg2.outputs[0], mx.inputs[2])
        L.new(mx.outputs[0], out.inputs['Surface'])
    else:
        L.new(bg.outputs[0], out.inputs['Surface'])

def area(name, loc, target, size, energy, color=(1, 1, 1), shape='RECTANGLE', sy=None):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = color; ld.shape = shape
    ld.size = size; ld.size_y = sy or size
    o = bpy.data.objects.new(name, ld); sc.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o

ENVK = 'none'
def floor(kind='studio'):
    import bmesh
    global ENVK; ENVK = kind
    if kind == 'none': return
    if kind == 'asphalt':
        me = bpy.data.meshes.new("Ground"); bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=30); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("ENV_Ground_asphalt", me); sc.collection.objects.link(o)
        m = bpy.data.materials.new("asphalt"); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
        b = N["Principled BSDF"]; tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.4, 0.4, 0.4)
        L.new(tc.outputs['Object'], mp.inputs['Vector'])
        A = os.path.join(ROOT, "ASSETS", "textures", "asphalt")
        for f, sock, nc in (("asphalt_02_diff_2k.jpg", 'Base Color', False), ("asphalt_02_rough_2k.jpg", 'Roughness', True)):
            t = N.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(A, f))
            if nc: t.image.colorspace_settings.name = 'Non-Color'
            L.new(mp.outputs['Vector'], t.inputs['Vector']); L.new(t.outputs['Color'], b.inputs[sock])
        t = N.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(A, "asphalt_02_nor_gl_2k.jpg")); t.image.colorspace_settings.name = 'Non-Color'
        nm = N.new('ShaderNodeNormalMap'); L.new(mp.outputs['Vector'], t.inputs['Vector']); L.new(t.outputs['Color'], nm.inputs['Color']); L.new(nm.outputs['Normal'], b.inputs['Normal'])
        o.data.materials.append(m); return o
    # seamless cyclorama sweep
    me = bpy.data.meshes.new("Cyc"); bm = bmesh.new()
    prof = []
    for i in range(13):
        a = math.radians(90 * i / 12); prof.append((-4.0 - 1.5 * math.sin(a), 1.5 - 1.5 * math.cos(a)))
    prof = [(9.0, 0.0)] + prof[0:1] + prof[1:] + [(-5.5, 9.0)]
    rows = []
    for y in (-25, 25):
        rows.append([bm.verts.new((x, y, z)) for x, z in prof])
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("ENV_Cyclorama", me); sc.collection.objects.link(o)
    for p in me.polygons: p.use_smooth = True
    m = bpy.data.materials.new("cyc"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    col = {'studio': (0.22, 0.22, 0.23), 'dark': (0.03, 0.03, 0.033), 'tech': (0.60, 0.60, 0.62)}[kind]
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = 0.45 if kind == 'dark' else 0.7
    o.data.materials.append(m)
    o.rotation_euler[2] = math.radians({'studio': 0, 'dark': 0, 'tech': 0}[kind] + float(arg('--cycrot', 0)))
    return o

def camera(loc, target, lens=50, ortho=None, shift=(0, 0)):
    cd = bpy.data.cameras.new("Cam"); c = bpy.data.objects.new("CAM", cd); sc.collection.objects.link(c)
    c.location = loc; d = Vector(target) - Vector(loc); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if ortho: cd.type = 'ORTHO'; cd.ortho_scale = ortho
    else: cd.lens = lens
    cd.shift_x, cd.shift_y = shift; cd.clip_start = 0.01; cd.clip_end = 200
    sc.camera = c; return c

def studio_lights(k=1.0, warm=False):
    area("L_key", (2.8, 2.6, 3.2), CENTER, 2.5, 700 * k, (1, 0.97, 0.93) if warm else (1, 1, 1))
    area("L_fill", (-1.8, 3.2, 1.4), CENTER, 3.0, 180 * k)
    area("L_rim", (-1.5, -3.0, 2.6), CENTER, 1.2, 650 * k, sy=3.0)
    area("L_top", (0.7, 0, 4.5), CENTER, 3.5, 450 * k, sy=1.6)

def to_mesh2(o):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    colls = list(o.users_collection)
    no = bpy.data.objects.new(o.name, me)
    for cc in colls: cc.objects.link(no)
    no.matrix_world = o.matrix_world.copy()
    for m in o.data.materials: me.materials.append(m)
    bpy.data.objects.remove(o)

def hide_collections(names):
    for c in bpy.data.collections:
        if any(c.name.startswith(n) for n in names):
            c.hide_render = True; c.hide_viewport = True

# ----------------------------------------------------------------- shots
def S(name, desc, cam, env, extra=None):
    return dict(name=name, desc=desc, cam=cam, env=env, extra=extra)

def setup(shot):
    D = CENTER
    if shot == 'hero_front34':
        floor('studio'); world_hdri("studio_small_09_2k.hdr", 0.22); studio_lights(0.9, warm=True)
        camera((3.55, 2.65, 1.05), D + Vector((0.02, 0, -0.04)), lens=60); return "front-three-quarter-hero_studio"
    if shot == 'hero_rear34':
        floor('dark'); world_hdri("brown_photostudio_02_2k.hdr", 0.5, rot=120)
        area("L_key", (-2.2, 2.6, 3.0), D, 2.5, 1100); area("L_rim", (2.5, -2.5, 2.0), D, 1.2, 1200, sy=3); area("L_top", (0.6, 0, 4.4), D, 3, 600, sy=1.4)
        camera((-2.55, 2.75, 1.25), D + Vector((0.08, 0, -0.06)), lens=58); return "rear-three-quarter-hero_dark-studio"
    if shot.startswith('ortho_'):
        floor('tech'); world_hdri("studio_small_09_2k.hdr", 0.9, bg_color=(0.8, 0.8, 0.81)); studio_lights(0.8)
        v = shot[6:]
        if v == 'left': camera((0.72, 8, 0.575), (0.72, 0, 0.575), ortho=2.35); return "left-orthographic_technical"
        if v == 'right': camera((0.72, -8, 0.575), (0.72, 0, 0.575), ortho=2.35); return "right-orthographic_technical"
        if v == 'front': camera((9, 0, 0.575), (0, 0, 0.575), ortho=1.30); return "front-orthographic_technical"
        if v == 'rear': camera((-4.3, 0, 0.575), (0, 0, 0.575), ortho=1.30); return "rear-orthographic_technical"
        if v == 'top':
            c = camera((0.70, 0, 9), (0.70, 0, 0), ortho=2.35); c.rotation_euler = (0, 0, math.radians(-90)); return "top-orthographic_technical"
    if shot == 'low_front':
        floor('asphalt'); world_hdri("kloofendal_48d_partly_cloudy_puresky_2k.hdr", 1.0, rot=200)
        camera((2.85, 0.95, 0.20), D + Vector((0.2, 0, 0.12)), lens=28); return "low-front_outdoor-track"
    if shot == 'engine':
        floor('studio'); world_hdri("studio_small_09_2k.hdr", 0.7); studio_lights(1.0)
        hide_collections(["80_BODY"])
        camera((1.25, 1.55, 0.62), (0.68, 0, 0.47), lens=50); return "engine-detail_fairings-off"
    if shot == 'exhaust':
        floor('dark'); world_hdri("brown_photostudio_02_2k.hdr", 0.6, rot=60); studio_lights(0.9)
        camera((0.2, -1.55, 0.55), (0.35, 0, 0.42), lens=45); return "exhaust-system_right-side"
    if shot == 'front_susp':
        floor('studio'); world_hdri("studio_small_09_2k.hdr", 0.7); studio_lights(1.0)
        camera((2.60, 1.45, 0.68), (1.34, 0, 0.44), lens=56); return "front-suspension-brake_ohlins-hypure"
    if shot == 'rear_susp':
        floor('studio'); world_hdri("studio_small_09_2k.hdr", 0.7); studio_lights(1.0)
        hide_collections(["80_BODY"])
        camera((0.15, -1.35, 0.62), (0.32, 0, 0.45), lens=45); return "rear-suspension-swingarm_right"
    if shot == 'rear_wheel':
        floor('studio'); world_hdri("studio_small_09_2k.hdr", 0.7); studio_lights(1.0)
        camera((-0.35, 1.10, 0.45), (0.05, 0.08, 0.33), lens=50); return "rear-wheel-chain-sprocket_left"
    if shot == 'cockpit':
        floor('dark'); world_hdri("brown_photostudio_02_2k.hdr", 0.6); studio_lights(0.6)
        camera((0.72, 0.0, 1.32), (1.12, 0, 0.98), lens=32); return "cockpit-TFT_rider-view"
    if shot == 'tank':
        floor('studio'); world_hdri("studio_small_09_2k.hdr", 0.7); studio_lights(1.0, warm=True)
        camera((1.05, 1.15, 1.25), (0.82, 0.05, 0.86), lens=50); return "tank-fairing-livery_detail"
    if shot == 'winglets':
        floor('dark'); world_hdri("brown_photostudio_02_2k.hdr", 0.6); studio_lights(0.9)
        camera((2.60, 2.40, 1.02), (1.15, 0, 0.66), lens=72); return "dual-layer-winglets_detail"
    if shot == 'naked':
        floor('tech'); world_hdri("studio_small_09_2k.hdr", 0.9, bg_color=(0.78, 0.78, 0.79)); studio_lights(0.9)
        hide_collections(["80_BODY", "85_LIGHTS"])
        camera((3.1, 2.6, 1.15), D, lens=55); return "fairings-removed_mechanical"
    if shot == 'exploded':
        # offset top-level objects per group (children follow via parenting)
        rules = [('10_', None), ('20_', (1.02, 0, 0.26)), ('30_', (0, 0, 0)), ('40_', (-0.35, 0, -0.16)),
                 ('50_', (0, 0, -0.30)), ('60_', (-0.10, -0.85, -0.12)), ('70_', (0.85, 0, 0.10)),
                 ('80_', (0.10, 0, 0.62)), ('85_', (0.16, 0, 0.88)), ('82_', (0.08, 0, 1.05)),
                 ('90_', (-0.55, 0, 0)), ('95_', (-0.85, 0, 0.24))]
        for o in sc.collection.all_objects:
            if o.parent is not None or o.type in ('CAMERA', 'LIGHT'): continue
            for pre, off in rules:
                if o.name.split('_')[0] and any(o.users_collection[0].name.startswith(pre) for _ in [0]):
                    if off is None:
                        off = (0.80, 0, 0) if o.name.startswith('F_') else (-0.80, 0, 0)
                    o.location = Vector((o.location.x + off[0], o.location.y + off[1], o.location.z + off[2]))
                    break
        floor('tech'); world_hdri("studio_small_09_2k.hdr", 0.5, bg_color=(0.75, 0.75, 0.76)); studio_lights(0.85)
        camera((5.4, 5.0, 2.45), (0.70, 0, 0.85), lens=52); return "exploded-view_technical"
    if shot == 'wireframe':
        import bmesh
        for o in list(sc.collection.all_objects):
            if o.type == 'CURVE':
                try: to_mesh2(o)
                except Exception: pass
        for o in sc.collection.all_objects:
            if o.type == 'MESH' and not o.name.startswith('ENV'):
                for md in o.modifiers:
                    if md.type == 'SUBSURF': md.render_levels = 0   # wireframe at base density (OOM guard)
                m = o.modifiers.new('WF', 'WIREFRAME'); m.thickness = 0.0012; m.use_replace = True
        floor('tech'); world_hdri("studio_small_09_2k.hdr", 0.5, bg_color=(0.12, 0.13, 0.15)); studio_lights(0.8)
        camera((3.4, 2.8, 1.35), CENTER, lens=55); return "wireframe_technical"
    if shot == 'final':
        floor('studio'); world_hdri("studio_small_09_2k.hdr", 0.22); studio_lights(0.9)
        camera((3.95, 2.2, 0.72), D + Vector((0.0, 0, -0.06)), lens=70); return "final-photoreal-studio"
    raise SystemExit("unknown shot " + shot)

shot = arg('--shot', 'hero_front34')
desc = setup(shot)
res = arg('--res', '1600x1000'); rx, ry = [int(v) for v in res.split('x')]
if shot in ('ortho_front', 'ortho_rear'): rx, ry = int(ry * 0.8), ry
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = int(arg('--samples', 64)); sc.cycles.use_denoising = False   # OIDN spikes >1 GB at 1.5MP+ on this box (OOM); noise floor handled with samples
try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
sc.cycles.max_bounces = 8; sc.cycles.transmission_bounces = 8; sc.cycles.glossy_bounces = 4
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02
sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = float(arg('--ev', {'studio': -0.9, 'dark': -0.7, 'tech': -0.35, 'asphalt': -0.5, 'none': -0.6}.get(ENVK, -0.6)))
sc.render.film_transparent = False; sc.render.threads_mode = 'AUTO'
sc.cycles.texture_limit_render = '1024'
prev = arg('--preview')
if prev:
    sc.render.filepath = prev
else:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sc.render.filepath = os.path.join(ROOT, "RENDERS", f"{ts}__{arg('--desc', desc)}.png")
    assert not os.path.exists(sc.render.filepath)
t0 = time.time()
bpy.ops.render.render(write_still=True)
print(f"[render] {shot} -> {sc.render.filepath} in {time.time()-t0:.0f}s", flush=True)
