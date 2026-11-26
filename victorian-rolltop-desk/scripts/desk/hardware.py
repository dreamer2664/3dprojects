"""
hardware.py — brass and turned-wood hardware, drawn as real solids with backs, stems,
plates and fixings: knobs, label frames, escutcheons, cup handles, barrel locks, keys,
castor brackets and the tambour-to-drawer locking linkage.
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix
from . import params as P
from .common import (box, cylinder, sphere, new_mesh_obj, poly_solid, add_bevel,
                     add_subsurf, box_bm)


def lathe(name, profile, col, mat, axis='Y', segments=28, smooth=True, centre=(0, 0, 0)):
    """Revolve a (radius, axial) profile. Axis of revolution is the given axis."""
    bm = bmesh.new()
    verts = []
    for (r, a) in profile:
        if axis == 'Y':
            co = (r, a, 0.0)
        elif axis == 'Z':
            co = (r, 0.0, a)
        else:
            co = (a, r, 0.0)
        verts.append(bm.verts.new(co))
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    geom = bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0),
                          axis={'X': (1, 0, 0), 'Y': (0, 1, 0), 'Z': (0, 0, 1)}[axis],
                          dvec=(0, 0, 0), angle=2 * math.pi, steps=segments,
                          use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_mesh_obj(name, bm, col, mat, smooth=smooth)
    ob.location = Vector(centre)
    return ob


# ----------------------------------------------------------------------------- knobs
def brass_knob(name, pos, col, M, radius=0.009, length=0.020):
    """Turned brass knob: rosette, stem and bun, modelled as a lathe about the Y axis."""
    r = radius
    profile = [
        (0.0, 0.0), (r * 0.62, 0.0), (r * 0.66, 0.0015), (r * 0.52, 0.0028),
        (r * 0.34, 0.0040), (r * 0.30, length * 0.55), (r * 0.42, length * 0.62),
        (r * 0.78, length * 0.72), (r * 1.0, length * 0.82), (r * 0.92, length * 0.94),
        (r * 0.62, length * 0.99), (0.0, length * 0.995),
    ]
    ob = lathe(name, profile, col, M['brass'], axis='Y', segments=24)
    ob.location = Vector(pos)
    ob.rotation_euler[0] = math.pi           # point outward along -Y
    return [ob]


def oak_knob(name, pos, col, M, radius=0.010, length=0.022):
    profile = [
        (0.0, 0.0), (radius * 0.70, 0.0), (radius * 0.74, 0.002), (radius * 0.40, 0.004),
        (radius * 0.36, length * 0.5), (radius * 0.60, length * 0.62),
        (radius * 0.98, length * 0.76), (radius * 1.0, length * 0.88),
        (radius * 0.55, length * 0.98), (0.0, length),
    ]
    ob = lathe(name, profile, col, M['oak_turned'], axis='Y', segments=24)
    ob.location = Vector(pos)
    ob.rotation_euler[0] = math.pi
    return [ob]


# ----------------------------------------------------------------------------- label frames
def label_frame(name, pos, col, M, w=0.042, h=0.017):
    """Brass label holder with recessed card and two fixing pins."""
    objs = []
    t = 0.0022
    d = 0.0026
    x, y, z = pos
    for sy, nm in ((1, 'T'), (-1, 'B')):
        objs.append(box(f"{name}_BAR{nm}", (w, d, t), (x, y, z + sy * (h / 2 - t / 2)), col,
                        M['brass'], bevel=0.0004))
    for sx, nm in ((1, 'R'), (-1, 'L')):
        objs.append(box(f"{name}_BAR{nm}", (t, d, h - 2 * t), (x + sx * (w / 2 - t / 2), y,
                                                             z), col, M['brass'],
                        bevel=0.0004))
    objs.append(box(f"{name}_CARD", (w - 2 * t - 0.0015, 0.0008, h - 2 * t - 0.0015),
                    (x, y + 0.0009, z), col, M['paper'], bevel=0.0))
    for sx in (-1, 1):
        objs.append(cylinder(f"{name}_PIN{sx}", 0.0011, 0.0018,
                             (x + sx * (w / 2 - 0.0015), y - 0.0016, z), col, M['brass'],
                             verts=10, axis='Y'))
    return objs


# ----------------------------------------------------------------------------- escutcheons
def escutcheon(name, pos, col, M, w=0.026, h=0.036, star=False):
    """Shaped brass key plate with a real open keyhole through it."""
    objs = []
    x, y, z = pos
    plate = box(f"{name}_PLATE", (w, 0.0022, h), (x, y, z), col, M['brass'],
                bevel=0.0026, bevel_segments=3, bevel_profile=0.6)
    objs.append(plate)
    # keyhole: dark recess (round bow + tapered slot)
    objs.append(cylinder(f"{name}_HOLE_BOW", 0.0042, 0.0026, (x, y - 0.0004, z + h * 0.14),
                         col, M['ink'], verts=16, axis='Y'))
    objs.append(box(f"{name}_HOLE_SLOT", (0.0032, 0.0026, h * 0.28),
                    (x, y - 0.0004, z - h * 0.10), col, M['ink']))
    if star:
        for i, (dx, dz) in enumerate(((-0.006, 0.012), (0.006, 0.012), (0, -0.014))):
            objs.append(cylinder(f"{name}_STUD{i}", 0.0016, 0.0022, (x + dx, y - 0.0004,
                                                                   z + dz), col,
                                 M['brass_dark'], verts=8, axis='Y'))
    return objs


def cup_handle(name, pos, col, M, w=0.070, h=0.030):
    """Carved oak cup handle: a lathe-turned cup, split back plate and fixing screws."""
    objs = []
    x, y, z = pos
    prof = [
        (0.0, 0.0), (w * 0.30, 0.0), (w * 0.34, 0.004), (w * 0.315, 0.012),
        (w * 0.33, h * 0.55), (w * 0.30, h * 0.85), (w * 0.235, h),
        (w * 0.20, h * 0.94), (w * 0.215, h * 0.55), (w * 0.19, 0.006), (0.0, 0.006),
    ]
    ob = lathe(name + "_CUP", prof, col, M['oak_turned'], axis='Y', segments=36)
    ob.location = (x, y, z)
    ob.rotation_euler[0] = -math.pi / 2
    ob.scale = (1.0, 1.0, 0.62)
    add_bevel(ob, 0.0006, 1)
    objs.append(ob)
    # back plate + screws, mostly hidden behind the cup
    objs.append(box(f"{name}_BACKPLATE", (w * 0.52, 0.003, h * 0.62),
                    (x, y + 0.0022, z), col, M['r'] if False else M['oak_turned'],
                    bevel=0.0015))
    for sx in (-1, 1):
        objs.append(cylinder(f"{name}_SCREW{sx}", 0.0022, 0.0035,
                             (x + sx * w * 0.20, y + 0.0008, z), col, M['brass'],
                             verts=10, axis='Y'))
    return objs


# ----------------------------------------------------------------------------- locks
def barrel_lock(name, pos, col, M, plate=True):
    """Tambour barrel lock: brass body behind the slat, key plate in front."""
    objs = []
    x, y, z = pos
    objs.append(cylinder(f"{name}_BARREL", 0.0115, 0.024, (x, y + 0.012, z), col,
                         M['lock_steel'], verts=24, axis='Y', bevel=0.001))
    objs.append(cylinder(f"{name}_ESCUTCHEON_RING", 0.0155, 0.0035, (x, y - 0.0005, z),
                         col, M['brass'], verts=32, axis='Y', bevel=0.001))
    objs += escutcheon(f"{name}_PLATE", (x, y - 0.0022, z), col, M)
    # bolt that throws into the side cheek
    objs.append(box(f"{name}_BOLT", (0.010, 0.008, 0.007), (x + 0.020, y + 0.010, z), col,
                    M['steel'], bevel=0.001))
    return objs


def key_object(name, pos, col, M, rot=(0, 0, 0)):
    """Steel/brass key: bow, shaft and bit — modelled for the close-up renders."""
    objs = []
    x, y, z = pos
    bow = lathe(name + "_BOW", [(0.006, 0.0), (0.0105, 0.002), (0.0125, 0.008),
                                (0.0125, 0.020), (0.0095, 0.026), (0.0, 0.027)],
                col, M['steel'], axis='Y', segments=24)
    bow.location = (x, y, z + 0.020)
    bow.rotation_euler = rot
    objs.append(bow)
    objs.append(cylinder(name + "_SHAFT", 0.0022, 0.030, (x, y + 0.004, z), col,
                         M['steel'], verts=16, axis='Y'))
    objs.append(box(name + "_BIT", (0.0085, 0.0032, 0.006), (x + 0.0045, y + 0.016, z),
                    col, M['steel'], bevel=0.0006))
    objs.append(box(name + "_BIT2", (0.0050, 0.0032, 0.004), (x + 0.0030, y + 0.0125, z),
                    col, M['steel'], bevel=0.0006))
    return objs


def locking_linkage(col, M, dx=0.0, state="released"):
    """Visible part of the linked locking system described in the listing: the tambour
    lock drives a horizontal bar under the desktop which throws two vertical rods into
    the pedestal drawer banks. `dx` shifts the rods to show thrown/withdrawn state."""
    objs = []
    z_bar = P.DESK_TOP_Z - P.TOP_TH - 0.055
    bar = box("LOCK_BAR", (P.KNEE_W - 0.02, 0.012, 0.010), (0, 0.62, z_bar), col,
              M['steel'], bevel=0.0015)
    objs.append(bar)
    objs.append(box("LOCK_BAR_GUIDE_L", (0.014, 0.020, 0.020), (-P.KNEE_W / 2 + 0.03, 0.62,
                                                               z_bar), col, M['brass'],
                    bevel=0.002))
    objs.append(box("LOCK_BAR_GUIDE_R", (0.014, 0.020, 0.020), (P.KNEE_W / 2 - 0.03, 0.62,
                                                               z_bar), col, M['brass'],
                    bevel=0.002))
    for sx in (-1, 1):
        # bell crank at each end, then a vertical rod into the pedestal
        objs.append(cylinder(f"LOCK_CRANK_{sx}", 0.009, 0.008,
                             (sx * (P.KNEE_W / 2 - 0.02), 0.62, z_bar - 0.012), col,
                             M['steel'], verts=20, axis='Y'))
        objs.append(box(f"LOCK_ROD_{sx}", (0.008, 0.008, 0.150 + dx),
                        (sx * (P.KNEE_W / 2 - 0.02), 0.62, z_bar - 0.075 - dx / 2), col,
                        M['steel'], bevel=0.001))
        objs.append(box(f"LOCK_CATCH_{sx}", (0.020, 0.010, 0.014),
                        (sx * (P.KNEE_W / 2 + 0.004), 0.62, P.PED_Z1 - 0.030), col,
                        M['brass'], bevel=0.002))
    return objs


def tambour_pull(col, M):
    """The handle you actually grab to close the roll, plus its fixing plate."""
    objs = []
    y = P.TAMB_Y_FRONT - P.TAMB_SLAT_T / 2 - 0.004
    z = P.TAMB_FRONT_Z0 + 0.070
    objs.append(box("TAMBOUR_PULL_PLATE", (0.150, 0.004, 0.026), (0, y + 0.002, z), col,
                    M['brass'], bevel=0.0025, bevel_segments=2))
    objs.append(box("TAMBOUR_PULL_BAR", (0.130, 0.012, 0.009), (0, y - 0.008, z + 0.004),
                    col, M['brass'], bevel=0.003, bevel_segments=3))
    for sx in (-1, 1):
        objs.append(cylinder(f"TAMBOUR_PULL_POST{sx}", 0.0035, 0.012,
                             (sx * 0.055, y - 0.002, z + 0.001), col, M['brass'],
                             verts=12, axis='Y'))
    return objs
