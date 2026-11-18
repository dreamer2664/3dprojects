"""Fast QC views (Workbench) to scratch dir.  blender -b file.blend -P scripts/qc.py -- --out ~/work/qc --views left,front34
Left view camera matches photo p_18 calibration so the PNG can be overlaid on the reference."""
import bpy, sys, os, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
out = os.path.expanduser(arg('--out', '~/work/qc')); os.makedirs(out, exist_ok=True)
views = arg('--views', 'left,front34').split(',')
hide = arg('--hide', '')
sc = bpy.context.scene
for c in bpy.data.collections:
    if hide and any(c.name.startswith(h) for h in hide.split(',')): c.hide_render = True
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading; sh.light = 'STUDIO'; sh.color_type = arg('--color', 'MATERIAL'); sh.show_cavity = True
sh.cavity_type = 'BOTH'; sh.show_object_outline = True
sc.display.render_aa = '8'
sc.view_settings.view_transform = 'Standard'
cd = bpy.data.cameras.new("QC"); cam = bpy.data.objects.new("QC", cd); sc.collection.objects.link(cam); sc.camera = cam
def look(loc, tgt):
    cam.location = loc; cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
for vi, v in enumerate(views):
    cd.type = 'PERSP'; cd.shift_x = cd.shift_y = 0
    if v == 'left':
        # p_18: X = (1553 - px)*0.0011816 ; Z = (1137 - py)*0.001143 ; 1920x1281 (non-square scale -> scale y)
        sx = 0.0011816; sz = 0.001143
        W, H = 1920, 1281
        cd.type = 'ORTHO'; cd.ortho_scale = W * sx
        sc.render.resolution_x, sc.render.resolution_y = W, int(round(H * sz / sx))
        cx = 1553 * sx - (W / 2) * sx   # model X at image centre
        cz = (1137 - H / 2) * sz
        # camera looks -Y (from +Y): image right = -X
        cam.location = (cx, 10, cz); cam.rotation_euler = (math.radians(90), 0, math.radians(180))
    elif v == 'right':
        sx = 0.0011816; W, H = 1920, 1281
        cd.type = 'ORTHO'; cd.ortho_scale = 2.4; sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
        cam.location = (0.72, -10, 0.6); cam.rotation_euler = (math.radians(90), 0, 0)
    elif v == 'front':
        cd.type = 'ORTHO'; cd.ortho_scale = 1.45; sc.render.resolution_x, sc.render.resolution_y = 900, 1300
        cam.location = (10, 0, 0.62); cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    elif v == 'rear':
        cd.type = 'ORTHO'; cd.ortho_scale = 1.45; sc.render.resolution_x, sc.render.resolution_y = 900, 1300
        cam.location = (-10, 0, 0.62); cam.rotation_euler = (math.radians(90), 0, math.radians(-90))
    elif v == 'top':
        cd.type = 'ORTHO'; cd.ortho_scale = 2.4; sc.render.resolution_x, sc.render.resolution_y = 1600, 800
        cam.location = (0.72, 0, 10); cam.rotation_euler = (0, 0, math.radians(90))
    elif v == 'front34':
        cd.lens = 45; sc.render.resolution_x, sc.render.resolution_y = 1400, 900; look((3.3, 2.5, 1.2), (0.72, 0, 0.55))
    elif v == 'rear34':
        cd.lens = 45; sc.render.resolution_x, sc.render.resolution_y = 1400, 900; look((-2.3, -2.6, 1.3), (0.72, 0, 0.55))
    elif v.startswith('cam:'):
        # cam:x,y,z,tx,ty,tz,lens
        p = [float(a) for a in v[4:].split('/')]
        cd.lens = p[6] if len(p) > 6 else 50; sc.render.resolution_x, sc.render.resolution_y = 1200, 800; look(p[0:3], p[3:6])
        v = f'cam{vi}'
    sc.render.resolution_percentage = int(arg('--pct', 50))
    sc.render.filepath = os.path.join(out, f"{v}.png")
    bpy.ops.render.render(write_still=True)
    print("[qc]", sc.render.filepath)
