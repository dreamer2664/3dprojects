"""
parts_upper.py — the working tambour: individual slats, canvas backing, the S-shaped side
cheeks with their real guide channels, posting slot, stops and the upper case structure.

Single path definition shared by slats, backing, guide ribs and the animation:

    A  front vertical   y = 0.090,  z 0.790 -> 1.248           length 0.458
    B  quarter round    centre (y 0.210, z 1.248) r 0.120      0.1885
    C  flat roll top    z = 1.368,  y 0.210 -> 0.465           0.255
    D  quarter round    centre (y 0.465, z 1.248) r 0.120      0.1885
    E  rear hanging     y = 0.585,  z 1.248 -> 0.700           0.548

Travelling `s` is arc length along that path; the open/closed state is one scalar offset
applied to every slat, exactly like the physical object.
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix
from . import params as P
from .common import box, cylinder, box_bm, new_mesh_obj, poly_solid, add_bevel, DEG

L1 = P.TAMB_SPRING - P.TAMB_FRONT_Z0
L2 = math.pi / 2 * P.R_MID
L3 = P.TAMB_Y_AFT - P.TAMB_Y_FWD
L4 = L2
L5 = P.TAMB_SPRING - P.TAMB_TAIL_Z
PATH_LEN = L1 + L2 + L3 + L4 + L5
OPEN_OFFSET = L1


def path_at(s):
    """(y, z, ty, tz, ny, nz) at arc length s along the tambour path."""
    if s <= L1:                                        # A: front vertical
        return (P.TAMB_Y_FRONT, P.TAMB_FRONT_Z0 + s, 0.0, 1.0, -1.0, 0.0)
    s -= L1
    if s <= L2:                                        # B: front quarter round
        phi = math.pi - s / P.R_MID
        return (P.TAMB_Y_FWD + P.R_MID * math.cos(phi),
                P.TAMB_SPRING + P.R_MID * math.sin(phi),
                math.sin(phi), -math.cos(phi), math.cos(phi), math.sin(phi))
    s -= L2
    if s <= L3:                                        # C: flat roll top
        return (P.TAMB_Y_FWD + s, P.TAMB_TOP_Z, 1.0, 0.0, 0.0, 1.0)
    s -= L3
    if s <= L4:                                        # D: rear quarter round
        phi = math.pi / 2 - s / P.R_MID
        return (P.TAMB_Y_AFT + P.R_MID * math.cos(phi),
                P.TAMB_SPRING + P.R_MID * math.sin(phi),
                math.sin(phi), -math.cos(phi), math.cos(phi), math.sin(phi))
    s -= L4
    s = min(s, L5)                                     # E: rear hanging run
    return (P.TAMB_Y_BACK, P.TAMB_SPRING - s, 0.0, -1.0, 1.0, 0.0)


def slat_transform(s):
    y, z, ty, tz, ny, nz = path_at(s)
    return Vector((0.0, y, z)), math.atan2(-ty, tz)


def sweep_ribbon(name, s0, s1, x0, x1, off0, off1, col, mat, steps=None,
                 smooth=True, cap=True):
    steps = steps or max(6, int(abs(s1 - s0) / 0.008))
    bm = bmesh.new()
    rings = []
    for i in range(steps + 1):
        s = s0 + (s1 - s0) * i / steps
        y, z, ty, tz, ny, nz = path_at(s)
        quad = []
        for (xo, off) in ((x0, off0), (x1, off0), (x1, off1), (x0, off1)):
            quad.append(bm.verts.new((xo, y + ny * off, z + nz * off)))
        rings.append(quad)
    for i in range(steps):
        a, b = rings[i], rings[i + 1]
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    if cap:
        bm.faces.new(tuple(reversed(rings[0])))
        bm.faces.new(tuple(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_obj(name, bm, col, mat, smooth=smooth)


# ----------------------------------------------------------------------------- tambour
def slat_length():
    return 2 * (P.CHEEK_X_IN + 0.010)


def build_tambour(col, M, offset=0.0, prefix="TAMB", posting_slot_index=13,
                  with_backing=True):
    objs = []
    by_index = {}
    n = int(P.TAMB_LEN / P.TAMB_SLAT_PITCH)
    slat_len = slat_length()
    slat_h = P.TAMB_SLAT_PITCH - P.TAMB_GAP
    for i in range(n):
        s = i * P.TAMB_SLAT_PITCH + offset + P.TAMB_SLAT_PITCH / 2
        if s > PATH_LEN:
            continue
        loc, alpha = slat_transform(s)
        pieces = ([(-slat_len / 2, -P.POST_SLOT_HALF_W), (P.POST_SLOT_HALF_W, slat_len / 2)]
                  if i == posting_slot_index else [(-slat_len / 2, slat_len / 2)])
        group = []
        for k, (xa, xb) in enumerate(pieces):
            sfx = f"_P{k}" if len(pieces) > 1 else ""
            ob = box(f"{prefix}_SLAT_{i:03d}{sfx}", (xb - xa, P.TAMB_SLAT_T, slat_h),
                     (0, 0, 0), col, M['oak_rift'] if (i % 3) else M['oak_qsa'],
                     bevel=0.0011, bevel_segments=1)
            ob.location = Vector(((xa + xb) / 2, loc.y, loc.z))
            ob.rotation_euler[0] = alpha
            objs.append(ob)
            group.append(ob)
        if with_backing:
            y, z, ty, tz, ny, nz = path_at(s)
            back = box(f"{prefix}_CANVAS_{i:03d}",
                       (slat_len - 0.026, 0.0014, P.TAMB_SLAT_PITCH + 0.0012),
                       (0, y - ny * 0.0064, z - nz * 0.0064), col, M['baize'])
            back.rotation_euler[0] = alpha
            objs.append(back)
            group.append(back)
        by_index[i] = group

    # posting-slot trim, riding on the slat that carries the slot
    s_slot = posting_slot_index * P.TAMB_SLAT_PITCH + offset + P.TAMB_SLAT_PITCH / 2
    loc, alpha = slat_transform(s_slot)
    w = 2 * P.POST_SLOT_HALF_W
    for sy, nm in ((1, "TOP"), (-1, "BOT")):
        lip = box(f"{prefix}_POSTSLOT_LIP_{nm}", (w + 0.004, 0.0026, 0.0024),
                  (0, 0, 0), col, M['brass'], bevel=0.0005)
        lip.location = Vector((0, loc.y, loc.z))
        lip.rotation_euler[0] = alpha
        lip.location += Vector((0, 0, 0))
        # offset along the slat's own thickness axis after rotation
        lip.location.y += math.cos(alpha) * sy * (slat_h / 2)
        lip.location.z += math.sin(alpha) * sy * (slat_h / 2)
        objs.append(lip)
    # brass surround sunk into the front face of the slat pair
    frame = box(f"{prefix}_POSTSLOT_FRAME", (w + 0.008, 0.0022, slat_h * 0.96),
                (0, 0, 0), col, M['brass_dark'], bevel=0.0006)
    frame.location = Vector((0, loc.y - math.cos(alpha) * (P.TAMB_SLAT_T / 2 + 0.0011),
                             loc.z - math.sin(alpha) * (P.TAMB_SLAT_T / 2 + 0.0011)))
    frame.rotation_euler[0] = alpha
    objs.append(frame)
    return objs, by_index


# ----------------------------------------------------------------------------- cheeks
def _offset_pt(y, z, t, off):
    """Point offset perpendicular to a tangent (ty,tz): normal is (-tz, ty)."""
    return (y - t[0] * off * -1.0 if False else y + (-t[1]) * off,
            z + (t[0]) * off)


def cheek_profile_points():
    """S-shaped outer profile of one cheek in the YZ plane (closed polygon)."""
    pts = [(P.CHEEK_Y_FRONT, P.DESK_TOP_Z), (P.CHEEK_Y_FRONT, P.TAMB_SPRING)]
    steps = 28
    r = P.TAMB_SKIN_R
    for i in range(1, steps + 1):                       # front quarter round
        phi = math.pi - (math.pi / 2) * i / steps
        pts.append((P.TAMB_Y_FWD + r * math.cos(phi), P.TAMB_SPRING + r * math.sin(phi)))
    pts.append((P.TAMB_Y_AFT, P.TAMB_SPRING + r))       # flat top
    for i in range(1, steps + 1):                       # rear quarter round
        phi = math.pi / 2 - (math.pi / 2) * i / steps
        pts.append((P.TAMB_Y_AFT + r * math.cos(phi), P.TAMB_SPRING + r * math.sin(phi)))
    pts.append((P.TAMB_Y_AFT + r, P.DESK_TOP_Z))
    return pts


def build_cheeks(col, M):
    objs = []
    prof = cheek_profile_points()
    plate_t = P.CHEEK_T - 0.010
    for sx in (-1, 1):
        x_in = P.CHEEK_X_IN + 0.010                     # channel floor
        o = poly_solid(f"CHEEK_{sx}_PLATE", prof, 'X', plate_t, col, M['oak_qsa_y'])
        base = x_in if sx > 0 else -x_in - plate_t
        o.location = Vector((base, 0, 0))
        add_bevel(o, 0.0022, 2)
        objs.append(o)
        # two guide ribs leave an 11 mm channel for the slat ends
        for tag, (o0, o1) in (("IN", (-0.0125, -0.0057)), ("OUT", (0.0057, 0.0125))):
            x0, x1 = ((P.CHEEK_X_IN, P.CHEEK_X_IN + 0.010) if sx > 0
                      else (-P.CHEEK_X_IN - 0.010, -P.CHEEK_X_IN))
            objs.append(sweep_ribbon(f"CHEEK_{sx}_TRACK_{tag}", 0.0, PATH_LEN, x0, x1,
                                     o0, o1, col, M['oak_rift'],
                                     steps=int(PATH_LEN / 0.007)))
    # liner closing the two quarter rounds so an open tambour shows a finished barrel
    for tag, (a, b) in (("F", (L1, L1 + L2)), ("R", (L1 + L2 + L3, L1 + L2 + L3 + L4))):
        objs.append(sweep_ribbon(f"TAMBOUR_ROLL_LINER_{tag}", a, b, -P.CHEEK_X_IN,
                                 P.CHEEK_X_IN, -0.0130, -0.0110, col, M['oak_qsa'],
                                 steps=60))
    objs.append(box("TAMBOUR_ROLL_LINER_TOP", (2 * P.CHEEK_X_IN, L3, 0.0020),
                    (0, P.TAMB_Y_FWD + L3 / 2, P.TAMB_TOP_Z - 0.0120), col,
                    M['oak_qsa']))
    # closing stop the lowest slat lands on
    objs.append(box("TAMBOUR_STOP_RAIL", (2 * P.CHEEK_X_IN, 0.018, 0.014),
                    (0, P.TAMB_Y_FRONT, P.TAMB_FRONT_Z0 - 0.008), col, M['oak_rift'],
                    bevel=0.002))
    for sx in (-1, 1):
        objs.append(box(f"TAMBOUR_END_STOP_{sx}", (0.012, 0.022, 0.020),
                        (sx * (P.CHEEK_X_IN - 0.006), P.TAMB_Y_BACK,
                         P.TAMB_TAIL_Z + 0.012), col, M['brass'], bevel=0.002))
    return objs


# ----------------------------------------------------------------------------- upper case
def build_upper_case(col, M):
    from .parts_lower import frame_and_panel, place
    objs = []
    x = P.CHEEK_X_IN
    # interior floor across the case
    objs.append(box("UPPER_FLOOR", (2 * x, P.UC_Y1 - P.CHEEK_Y_FRONT - 0.01, 0.015),
                    (0, (P.CHEEK_Y_FRONT + P.UC_Y1) / 2, P.DESK_TOP_Z + 0.0075), col,
                    M['oak_qsa'], bevel=0.002))
    # rear wall, fielded on the outside so the back of the desk is properly finished
    objs.append(box("UPPER_BACK", (2 * P.UC_X, P.UC_T, P.TAMB_SPRING - P.DESK_TOP_Z),
                    (0, P.UC_Y1 - P.UC_T / 2, (P.DESK_TOP_Z + P.TAMB_SPRING) / 2), col,
                    M['oak_qsa'], bevel=0.002))
    for i, ox in enumerate((-0.195, 0.0, 0.195)):
        m = place(ox, P.UC_Y1 + 0.001, (P.DESK_TOP_Z + P.TAMB_SPRING) / 2)
        objs += frame_and_panel(f"UPPER_BACKPANEL{i}", 0.175,
                                P.TAMB_SPRING - P.DESK_TOP_Z - 0.07, 0.045, 0.016, col,
                                M['oak_qsa'], M['oak_cathedral'], m, field_bevel=0.010)
    # the pocket the tambour hangs into
    objs.append(box("TAMBOUR_POCKET_BOTTOM", (2 * x, P.UC_Y1 - P.INT_Y1 - 0.006, 0.014),
                    (0, (P.INT_Y1 + P.UC_Y1) / 2, P.TAMB_TAIL_Z - 0.030), col,
                    M['oak_end'], bevel=0.0015))
    for sx in (-1, 1):
        objs.append(box(f"TAMBOUR_POCKET_SIDE_{sx}",
                        (0.008, P.UC_Y1 - P.INT_Y1 - 0.006,
                         P.TAMB_SPRING - P.TAMB_TAIL_Z),
                        (sx * (x - 0.004), (P.INT_Y1 + P.UC_Y1) / 2,
                         (P.TAMB_TAIL_Z + P.TAMB_SPRING) / 2), col, M['oak_rift'],
                        bevel=0.0015))
    # rear top deck behind the roll, and its cap moulding
    objs.append(box("UPPER_TOP_DECK", (2 * P.UC_X, P.UC_Y1 - (P.TAMB_Y_AFT + P.TAMB_SKIN_R)
                                       + 0.002, 0.016),
                    (0, (P.TAMB_Y_AFT + P.TAMB_SKIN_R + P.UC_Y1) / 2,
                     P.TAMB_SPRING - 0.008), col, M['oak_qsa'], bevel=0.003))
    objs.append(box("UPPER_BACK_CAP", (2 * P.UC_X + 0.010, 0.022, 0.014),
                    (0, P.UC_Y1, P.TAMB_SPRING - 0.004), col, M['oak_qsa'],
                    bevel=0.003))
    # pilaster beads on the cheeks, either side of the tambour
    for sx in (-1, 1):
        objs.append(cylinder(f"UPPER_PILASTER_BEAD_{sx}", 0.0055, P.TAMB_SPRING -
                             P.DESK_TOP_Z, (sx * (P.UC_X - 0.007),
                                            P.CHEEK_Y_FRONT - 0.0016,
                                            (P.DESK_TOP_Z + P.TAMB_SPRING) / 2), col,
                             M['oak_qsa'], verts=20, bevel=0.0008))
        # bead running along the cheek's S-curve edge
        objs.append(sweep_ribbon_edge(f"CHEEK_{sx}_EDGE_BEAD", 0.0042,
                                      col=col, mat=M['oak_qsa'], sx=sx))
    return objs


def sweep_ribbon_edge(name, inset, col, mat, sx, steps=80):
    """A small moulded bead following the cheek's outer S-profile along the outside face,
    so the edge reads as a worked moulding rather than a flat sawn line."""
    prof = cheek_profile_points()
    path = prof[1:len(prof) - 1]          # outer boundary only (front edge -> rear turn)
    bm = bmesh.new()
    rings = []
    for i, (y, z) in enumerate(path):
        j = min(i, len(path) - 2)
        ty = path[j + 1][0] - path[j][0]
        tz = path[j + 1][1] - path[j][1]
        L = math.hypot(ty, tz) or 1.0
        ty, tz = ty / L, tz / L
        ny, nz = -tz, ty                  # outward normal of the profile boundary
        x_out = sx * P.UC_X
        x_in = sx * (P.UC_X - 0.0060)
        q = []
        for (dy, dx) in ((0.0, 0.0), (inset, 0.0), (inset, 0.0060), (0.0, 0.0060)):
            q.append(bm.verts.new((x_in + (x_out - x_in) * dx / 0.0060,
                                   y + ny * dy, z + nz * dy)))
        rings.append(q)
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    bm.faces.new(tuple(reversed(rings[0])))
    bm.faces.new(tuple(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_obj(name, bm, col, mat, smooth=True)


# ----------------------------------------------------------------------------- animation
def animate_tambour(by_index, frame_start=1, frame_end=96, out_of_frame=None):
    """Key every slat from its own path station: no fake scaling, no mesh swapping."""
    for f in range(frame_start, frame_end + 1):
        t = (f - frame_start) / (frame_end - frame_start)
        e = 0.5 - 0.5 * math.cos(math.pi * min(max((t - 0.08) / 0.84, 0.0), 1.0))
        off = OPEN_OFFSET * e
        for i, objs in by_index.items():
            s = i * P.TAMB_SLAT_PITCH + off + P.TAMB_SLAT_PITCH / 2
            loc, alpha = slat_transform(s)
            for k, ob in enumerate(objs):
                if k == 0:
                    ob.location = loc
                    ob.rotation_euler[0] = alpha
                ob.keyframe_insert("location", frame=f)
                ob.keyframe_insert("rotation_euler", index=0, frame=f)
