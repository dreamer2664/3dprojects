"""
export_glb.py — export an already-built master .blend to glTF binary.

Kept separate from the build so the (slow, memory-hungry) exporter can be run in the
background and retried without rebuilding: 1,559 objects x ~5.5 M evaluated triangles is
close to this sandbox's 1.9 GB of RAM.

    blender -b master.blend --python scripts/desk/export_glb.py -- --out <dir> [--draco]
"""
import bpy
import os
import sys
import json
import time
import argparse

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=".")
ap.add_argument("--name", default=None)
ap.add_argument("--draco", action="store_true")
ap.add_argument("--keep-env", action="store_true")
args = ap.parse_args(argv)


def rss_mb():
    with open("/proc/self/status") as f:
        return int(f.read().split("VmRSS:")[1].split()[0]) / 1024.0


# strip staging / environment objects: the GLB should contain the desk, not the set
if not args.keep_env:
    for ob in list(bpy.data.objects):
        if ob.name.startswith(("ENV_", "SWATCH", "GRAIN_SPACE", "CAM_", "LIGHT_")):
            bpy.data.objects.remove(ob, do_unlink=True)

name = args.name or (os.path.splitext(os.path.basename(bpy.data.filepath))[0] + ".glb")
path = os.path.join(args.out if os.path.isabs(args.out) else os.path.join(os.getcwd(),
                                                                         args.out), name)
os.makedirs(os.path.dirname(path), exist_ok=True)

t0 = time.time()
print(f"EXPORT_START rss={rss_mb():.0f}MB objects={len(bpy.data.objects)}", flush=True)
bpy.ops.export_scene.gltf(
    filepath=path,
    export_format='GLB',
    use_selection=False,
    export_apply=True,
    export_yup=True,
    export_draco_mesh_compression_enable=args.draco,
    export_draco_mesh_compression_level=6,
    export_cameras=False,
    export_lights=False,
    export_extras=False,
)
size = os.path.getsize(path)
print(f"EXPORT_DONE {path} {size/1e6:.1f}MB in {time.time()-t0:.0f}s "
      f"peak_rss={rss_mb():.0f}MB", flush=True)
with open(os.path.join(os.path.dirname(path), "_glb_export.json"), "w") as f:
    json.dump({"file": os.path.basename(path), "bytes": size,
               "seconds": round(time.time() - t0, 1),
               "rss_mb": round(rss_mb())}, f, indent=2)
