"""
parts_drawers.py — the nine large drawers (four per pedestal plus the central lockable
drawer) with real boxes, sycamore sides, dovetail joints, runners, cup handles,
escutcheons and a divided filing drawer.
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix
from . import params as P
from .common import box, cylinder, new_mesh_obj, add_bevel, box_bm
from . import hardware as HW

DOVETAIL_OK = []          # records which joints were actually cut with a boolean
DOVETAIL_FAIL = []


def dovetail_tails(name, x_side, y_front, side_t, front_t, height, col, M,
                   n_tails=5, z_centre=0.0, tail_ratio=0.46, depth=0.0105):
    """Trapezoidal tails on a sycamore drawer side, cut to interlock with the oak front.
    Returns (tail_objects, cutter_object)."""
    tails = []
    gap = height / n_tails
    tw = gap * tail_ratio
    bm = bmesh.new()
    for i in range(n_tails):
        z0 = -height / 2 + i * gap + (gap - tw) / 2
        z1 = z0 + tw
        # trapezoid in the XZ plane, extruded in Y through the front thickness
        pts = [(z0 - tw * 0.28, 0.0), (z1 + tw * 0.28, 0.0),
               (z1, depth), (z0, depth)]
        ring = []
        for (z, dy) in pts:
            ring.append(bm.verts.new((x_side - side_t / 2, y_front + front_t - depth + dy,
                                      z_centre + z)))
        ring2 = []
        for (z, dy) in pts:
            ring2.append(bm.verts.new((x_side + side_t / 2, y_front + front_t - depth + dy,
                                       z_centre + z)))
        bm.faces.new(ring)
        bm.faces.new(list(reversed(ring2)))
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((ring[k], ring[k2], ring2[k2], ring2[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    tails_obj = new_mesh_obj(name, bm, col, M['sycamore_end'])
    return tails_obj


def cut_socket(front_obj, tail_obj):
    """Boolean the tail shapes out of the drawer front so the joint interlocks."""
    try:
        front_obj.data.materials.append(front_obj.data.materials[0])
    except Exception:
        pass
    m = front_obj.modifiers.new("dovetail_socket", 'BOOLEAN')
    m.operation = 'DIFFERENCE'
    m.solver = 'EXACT'
    m.object = tail_obj
    with bpy.context.temp_override(object=front_obj, active_object=front_obj,
                                   selected_objects=[front_obj]):
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
            DOVETAIL_OK.append(front_obj.name)
            return True
        except Exception as e:
            DOVETAIL_FAIL.append((front_obj.name, str(e)))
            front_obj.modifiers.remove(m)
            return False


def build_drawer(name, x_c, width, height, z_c, y_front, depth, col, M,
                 lip=True, filing=False, lockable=False, cup=True, dovetails=True):
    """One large drawer: front, sides, back, bottom, joinery, hardware."""
    objs = []
    ft = P.DRAWER_FRONT_T
    st = 0.014
    bt = 0.006
    # ---- front, with a moulded / cushion edge and a lipped top edge
    front = box(f"{name}_FRONT", (width, ft, height), (x_c, y_front + ft / 2, z_c), col,
                M['oak_qsa'], bevel=0.0045, bevel_segments=3, bevel_profile=0.62)
    objs.append(front)
    # ---- sides
    for sx in (-1, 1):
        x_side = x_c + sx * (width / 2 - st / 2)
        objs.append(box(f"{name}_SIDE{sx}", (st, depth - ft, height - 0.018),
                        (x_side, y_front + ft + (depth - ft) / 2, z_c - 0.004), col,
                        M['sycamore'], bevel=0.0012))
        # runner groove
        objs.append(box(f"{name}_GROOVE{sx}", (0.0024, depth - ft - 0.05, 0.008),
                        (x_c + sx * (width / 2 + 0.0004),
                         y_front + ft + (depth - ft) / 2, z_c - height / 2 + 0.022), col,
                        M['shadow']))
        if dovetails:
            tails = dovetail_tails(f"{name}_TAILS{sx}", x_side, y_front, st, ft,
                                   height - 0.030, col, M, n_tails=5,
                                   z_centre=z_c - 0.004)
            if cut_socket(front, tails):
                tails.data.materials.clear()
                tails.data.materials.append(M['sycamore_end'])
                objs.append(tails)
            else:
                tails.hide_render = True
                tails.location = (0, 0, -5)
                objs.append(tails)
    # ---- back
    objs.append(box(f"{name}_BACK", (width - 2 * st, st, height - 0.020),
                    (x_c, y_front + depth - st / 2, z_c - 0.004), col, M['sycamore'],
                    bevel=0.0012))
    # ---- bottom in a groove
    objs.append(box(f"{name}_BOTTOM", (width - 2 * st + 0.004, depth - ft - st + 0.004,
                                       bt),
                    (x_c, y_front + ft + (depth - ft - st) / 2,
                     z_c - height / 2 + 0.014), col, M['sycamore'], bevel=0.001))
    if filing:
        # adjustable file dividers: two sliding rails and a divider
        for i, sx in enumerate((-0.075, 0.075)):
            objs.append(box(f"{name}_FILERAIL{i}", (0.010, depth - ft - 0.05, 0.020),
                            (x_c + sx, y_front + ft + (depth - ft) / 2,
                             z_c - height / 2 + 0.030), col, M['oak_rift'],
                            bevel=0.0018))
        objs.append(box(f"{name}_FILEDIV", (width - 2 * st - 0.02, 0.008, height - 0.06),
                        (x_c, y_front + ft + (depth - ft) / 2,
                         z_c - 0.006), col, M['oak_rift'], bevel=0.0018))
    # ---- hardware
    if cup:
        objs += HW.cup_handle(f"{name}_HANDLE", (x_c, y_front - 0.004,
                                                 z_c + height * 0.06), col, M,
                              w=min(0.090, width * 0.44), h=0.032)
    if lockable:
        objs += HW.escutcheon(f"{name}_ESCUTCHEON", (x_c, y_front - 0.0016,
                                                     z_c + height * 0.02), col, M)
        objs += HW.barrel_lock(f"{name}_LOCK", (x_c, y_front + ft * 0.4,
                                                z_c + height * 0.02), col, M)
    return objs


def build_pedestal_drawers(col, M, ped_idx, openings):
    """Four drawers per pedestal, graduated, the bottom one a deep filing drawer."""
    objs = []
    x_c = P.PED_X * (1 if ped_idx == 0 else -1)
    inner_w = P.PED_W - 2 * P.PED_T - 0.010
    for i, (lo, hi) in enumerate(openings):
        h = hi - lo
        filing = (i == 0)
        depth = 0.760 if filing else 0.520
        # drawers sit flush with the face frame, 2 mm reveals
        objs += build_drawer(f"PED{ped_idx}_DRAWER{i}", x_c, inner_w - 0.002,
                             h - 0.002, (lo + hi) / 2, P.PED_Y0 + 0.001, depth, col, M,
                             filing=filing, lockable=(i == 0 and ped_idx == 0),
                             cup=True, dovetails=not filing)
    return objs


def build_central_drawer(col, M):
    """The central lockable drawer between the pedestals."""
    return build_drawer("CENTRE_DRAWER", 0, P.KNEE_W - 0.06, 0.082, 0.655, 0.012, 0.560,
                        col, M, lockable=True, cup=True, dovetails=True)
