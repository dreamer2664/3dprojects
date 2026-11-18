"""Build the complete RSV4 Factory 2026 scene.
Usage:  blender -b -P scripts/build_all.py [-- --only wheels,fork --out path.blend]
"""
import bpy, sys, os, json, importlib, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib; importlib.reload(lib)
import geom; importlib.reload(geom)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None):
    return argv[argv.index(k) + 1] if k in argv else d

MODULES = ["parts_wheels", "parts_fork", "parts_frame", "parts_swingarm", "parts_engine", "parts_exhaust",
           "parts_cooling", "parts_body", "parts_cockpit", "parts_drive", "parts_details"]
only = arg("--only")
if only: MODULES = [m for m in MODULES if m.split("_", 1)[1] in only.split(",")]
out = arg("--out", os.path.join(lib.ROOT, "MODELS", "rsv4_factory_2026.blend"))

# clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
cal = json.load(open(os.path.join(lib.TEX, "livery_calibration.json")))
lib.build_materials(cal)
root = lib.coll("RSV4_FACTORY_2026")
ctx = {}
for m in MODULES:
    t0 = time.time()
    mod = importlib.import_module(m); importlib.reload(mod)
    # every module creates its own sub-collection under root
    r = mod.build(ctx)
    if isinstance(r, dict): ctx.update(r)
    print(f"[build] {m}: {time.time()-t0:.1f}s, objects={len(bpy.data.objects)}", flush=True)
# move top-level module collections under root
for c in list(sc.collection.children):
    if c is not root and c.name[:2].isdigit():
        sc.collection.children.unlink(c); root.children.link(c)
# stray objects into root
for o in list(sc.collection.objects):
    sc.collection.objects.unlink(o); root.objects.link(o)
os.makedirs(os.path.dirname(out), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print("[build] saved", out, "objects:", len(bpy.data.objects), flush=True)
