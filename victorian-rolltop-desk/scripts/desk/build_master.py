"""
build_master.py — assemble the whole desk, measure it, save the master .blend and export GLB.

    blender -b --factory-startup --python scripts/desk/build_master.py -- \
        --state closed --out assets/victorian-rolltop-desk

Everything is built from parameters in params.py; nothing is eyeballed.
"""
import bpy
import os
import sys
import json
import math
import argparse
import time

# allow "python3 build_master.py" style imports when run through Blender
_here = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(_here) not in sys.path:
    sys.path.insert(0, os.path.dirname(_here))

from desk import params as P
from desk import common as C
from desk import materials as MAT
from desk import parts_lower as LOW
from desk import parts_upper as UPPER
from desk import parts_interior as INT
from desk import parts_drawers as DRW
from desk import hardware as HW


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="closed", choices=["closed", "open"])
    ap.add_argument("--out", default="assets/victorian-rolltop-desk")
    ap.add_argument("--tambour-offset", type=float, default=None)
    ap.add_argument("--no-glb", action="store_true")
    ap.add_argument("--density", type=float, default=1.0,
                    help="multiplier on displacement-grid density")
    return ap.parse_args(argv)


def apply_density(M):
    """Real grain relief: densify the large surfaces and displace them."""
    tex = C.grain_displace_textures()
    rules = [
        # (name prefix, cuts, displace strength, grain axis)
        ("DESKTOP_TOP", 190, 0.00016, 'x'),
        ("DESKTOP_NOSING", 0, 0.0, 'x'),
        ("PED0_SIDE", 26, 0.00013, 'y'),
        ("PED1_SIDE", 26, 0.00013, 'y'),
        ("PED0_BACKPANEL", 30, 0.00015, 'x'),
        ("PED1_BACKPANEL", 30, 0.00015, 'x'),
        ("PED0_SIDEPANEL", 34, 0.00015, 'y'),
        ("PED1_SIDEPANEL", 34, 0.00015, 'y'),
        ("MODESTY", 26, 0.00014, 'x'),
        ("CHEEK_", 30, 0.00014, 'y'),
        ("TAMB_SLAT", 4, 0.00008, 'x'),
        ("UPPER_BACK", 40, 0.00015, 'x'),
        ("UPPER_BACKPANEL", 26, 0.00015, 'x'),
        ("_FRONT", 12, 0.00012, 'x'),
        ("INT_PIGEON", 10, 0.00025, 'x'),
        ("INT_WING", 10, 0.00025, 'x'),
    ]
    touched = 0
    for ob in list(bpy.context.scene.objects):
        if ob.type != 'MESH':
            continue
        for prefix, cuts, strength, axis in rules:
            if prefix in ob.name and cuts > 0:
                C.densify(ob, int(cuts * DENSITY))
                m = ob.modifiers.new("grain_displace", 'DISPLACE')
                m.texture = tex[axis]
                m.texture_coords = 'LOCAL'
                # stretch the noise along the grain direction so relief reads as grain
                m.texture_coords = 'OBJECT'
                obg = _grain_empty(axis)
                m.texture_coords_object = obg
                m.strength = strength
                m.mid_level = 0.5
                touched += 1
                break
    return touched


DENSITY = 1.0
_GRAIN_EMPTIES = {}


def _grain_empty(axis):
    """A scaled empty used as the displacement coordinate space, stretching the noise
    anisotropy along the board's grain direction."""
    if axis in _GRAIN_EMPTIES:
        return _GRAIN_EMPTIES[axis]
    name = f"GRAIN_SPACE_{axis.upper()}"
    emp = bpy.data.objects.get(name)
    if emp is None:
        emp = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(emp)
        C.link(emp, C.collection("CAMERAS_LIGHTS_AND_STAGING"))
    emp.scale = {'x': (0.03, 1.0, 1.0), 'y': (1.0, 0.03, 1.0),
                 'z': (1.0, 1.0, 0.03)}[axis]
    _GRAIN_EMPTIES[axis] = emp
    return emp


def build_swatches(col, M):
    """Test swatches proving the material separation (used in the material render)."""
    objs = []
    mats = [('oak_qsa', 'QUARTER-SAWN OAK'), ('oak_rift', 'RIFT-SAWN OAK'),
            ('oak_cathedral', 'PLAIN-SAWN OAK'), ('lacewood', 'LACEWOOD'),
            ('sycamore', 'SYCAMORE'), ('brass', 'AGED BRASS')]
    # swatches live in a staging group well clear of the desk so no render includes them
    for i, (key, label) in enumerate(mats):
        x = -0.375 + i * 0.15
        o = C.box(f"SWATCH_{key.upper()}", (0.13, 0.012, 0.13), (2.60 + x, 0.30, 0.80), col,
                  M[key], bevel=0.003)
        C.densify(o, 26)
        t = C.grain_displace_textures()['x']
        m = o.modifiers.new("disp", 'DISPLACE')
        m.texture = t
        m.strength = 0.0004
        objs.append(o)
    return objs


def main():
    global DENSITY
    args = parse_args()
    DENSITY = args.density
    t0 = time.time()
    C.reset_scene()
    cols = C.ensure_collections()
    M = MAT.build_material_library()

    L = cols
    # ---------------- lower case
    LOW.build_castors(L['BRASS_HARDWARE_AND_CASTORS'], M)
    LOW.build_plinth(L['PEDESTAL_CARCASSES_AND_PANELS'], M)
    all_openings = {}
    for i in (0, 1):
        objs, openings = LOW.build_pedestal(i, L['PEDESTAL_CARCASSES_AND_PANELS'], M)
        all_openings[i] = openings
    LOW.build_desktop(L['DESKTOP_AND_WRITING_SURFACE'], M)
    LOW.build_kneehole(L['PEDESTAL_CARCASSES_AND_PANELS'], M)
    LOW.build_writing_slides(L['WRITING_SLIDES_AND_SUPPORTS'], M)

    # ---------------- upper case + tambour
    UPPER.build_cheeks(L['TAMBOUR_SLATS_BACKING_AND_TRACKS'], M)
    UPPER.build_upper_case(L['TAMBOUR_SLATS_BACKING_AND_TRACKS'], M)
    offset = P.TAMB_FRONT_Z0 * 0 + (UPPER.L1 if args.state == "open" else 0.0)
    if args.tambour_offset is not None:
        offset = args.tambour_offset
    UPPER.build_tambour(L['TAMBOUR_SLATS_BACKING_AND_TRACKS'], M, offset=offset)

    # ---------------- fitted interior + 33 drawers
    inter, cols_ph, cw, rows2, rh, zshelf = INT.build_interior_carcass(
        L['UPPER_FITTED_INTERIOR'], M)
    for o in inter:
        if "PIGEON" in o.name or "LETTER_RACK" in o.name or "PEN_TRAY" in o.name:
            C.link(o, L['VERTICAL_PIGEONHOLES_AND_LETTER_RACKS'])
    drawers, wings = INT.build_internal_drawers(L['33_INTERNAL_DRAWERS'], M,
                                                cols_ph, cw, rows2, rh, zshelf)

    # ---------------- large drawers
    for i in (0, 1):
        DRW.build_pedestal_drawers(L['PEDESTAL_DRAWERS_AND_JOINERY'], M, i,
                                   all_openings[i])
    DRW.build_central_drawer(L['PEDESTAL_DRAWERS_AND_JOINERY'], M)

    # ---------------- locks, key, linkage, tambour pull
    HW.barrel_lock("TAMBOUR_LOCK", (0, P.TAMB_Y_FRONT - 0.006, P.TAMB_FRONT_Z0 + 0.070),
                   L['LOCKS_KEYS_AND_LINKAGE'], M)
    HW.key_object("DOOR_KEY", (0.16, P.TAMB_Y_FRONT - 0.10, P.DESK_TOP_Z + 0.004),
                  L['LOCKS_KEYS_AND_LINKAGE'], M)
    HW.locking_linkage(L['LOCKS_KEYS_AND_LINKAGE'], M,
                       dx=0.05 if args.state == "open" else 0.0)
    HW.tambour_pull(L['BRASS_HARDWARE_AND_CASTORS'], M)
    build_swatches(L['MATERIALS_AND_TEST_SWATCHES'], M)

    # ---------------- density + measurement
    touched = apply_density(M)
    bpy.context.view_layer.update()
    v, t, per_obj = C.evaluated_stats()

    counts = {
        "slats": len([o for o in bpy.data.objects if "TAMB_SLAT_" in o.name]),
        "internal_drawers": len([o for o in bpy.data.objects
                                 if o.name.startswith("UPPER_DRAWER_") and
                                 o.name.endswith("_FRONT")]) +
                            len([o for o in bpy.data.objects
                                 if o.name.startswith("UPPER_CUSHION_DRAWER_") and
                                 o.name.endswith("_FRONT")]),
        "pigeonholes": P.N_PIGEONHOLES,
        "pedestal_drawers": len([o for o in bpy.data.objects
                                 if o.name.startswith("PED") and
                                 o.name.endswith("_FRONT")]),
        "objects": len(bpy.data.objects),
        "displaced_surfaces": touched,
        "dovetail_joints_cut": len(DRW.DOVETAIL_OK),
        "dovetail_joints_failed": len(DRW.DOVETAIL_FAIL),
        "vertices": v,
        "triangles": t,
        "build_seconds": round(time.time() - t0, 1),
        "state": args.state,
    }
    print("BUILD_STATS " + json.dumps(counts), flush=True)

    # ---------------- save
    out = args.out if os.path.isabs(args.out) else os.path.join(os.getcwd(), args.out)
    os.makedirs(out, exist_ok=True)
    blend = os.path.join(out, f"victorian_rolltop_desk_{args.state}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=False)
    print("SAVED " + blend, flush=True)

    stats_path = os.path.join(out, f"_build_stats_{args.state}.json")
    with open(stats_path, "w") as f:
        json.dump({**counts, "per_object_top": dict(
            sorted(per_obj.items(), key=lambda kv: -kv[1][1])[:25])}, f, indent=2)

    if not args.no_glb:
        for ob in list(bpy.data.objects):
            if ob.name.startswith(("SWATCH", "ENV_", "GRAIN_SPACE", "CAM_", "LIGHT_")):
                bpy.data.objects.remove(ob, do_unlink=True)
        for ob in bpy.context.scene.objects:
            ob.select_set(True)
        bpy.ops.export_scene.gltf(
            filepath=os.path.join(out, f"victorian_rolltop_desk_{args.state}.glb"),
            export_format='GLB',
            use_selection=False,
            export_apply=True,
            export_yup=True,
        )
        print("GLB_OK", flush=True)


if __name__ == "__main__":
    main()
