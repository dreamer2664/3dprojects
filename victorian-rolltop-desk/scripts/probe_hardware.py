"""
probe_hardware.py — measure the *actual* geometry budget of this sandbox with Blender.

Run with:  ~/.local/opt/blender/blender -b --factory-startup --python scripts/probe_hardware.py
(or with a subdivision level:  --python scripts/probe_hardware.py -- 11)

Why this exists: brief §9 asks for a >= 30,000,000 evaluated-triangle master and brief §10 asks
for 8K renders. The sandbox has 2 vCPU and ~1.9 GB RAM, so those numbers must be established by
measurement rather than assumed. Each level is run in its own Blender process because a level
that exceeds RAM is OOM-killed by the kernel (exit 137) and takes the whole session with it.
"""
import bpy, sys, time, json, os

def rss_mb() -> float:
    with open("/proc/self/status") as f:
        return int(f.read().split("VmRSS:")[1].split()[0]) / 1024.0

def probe(level: int) -> dict:
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=2, y_subdivisions=2, size=1.0)
    ob = bpy.context.object
    mod = ob.modifiers.new("subdiv", 'SUBSURF')
    mod.levels = mod.render_levels = level
    t0 = time.time()
    dg = bpy.context.evaluated_depsgraph_get()
    me = ob.evaluated_get(dg).to_mesh()
    faces = len(me.polygons)
    tris = faces * 2  # all-quad grid
    out = {
        "subdiv_level": level,
        "evaluated_faces": faces,
        "evaluated_tris": tris,
        "eval_seconds": round(time.time() - t0, 1),
        "peak_rss_mb": round(rss_mb()),
        "mesh_bytes_per_tri": round(rss_mb() * 1024 * 1024 / max(tris, 1), 1),
    }
    print("RESULT " + json.dumps(out), flush=True)
    return out

def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    level = int(argv[0]) if argv else 10
    print(f"blender {bpy.app.version_string} | rss_baseline_mb={rss_mb():.0f}", flush=True)
    probe(level)

if __name__ == "__main__":
    main()
