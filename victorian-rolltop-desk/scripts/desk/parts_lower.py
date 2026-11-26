"""
parts_lower.py — castors, plinths, pedestal carcasses with fielded panels, desktop,
kneehole, modesty board, central lockable drawer and the two pull-out writing slides.
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix
from . import params as P
from .common import (box, cylinder, sphere, box_bm, new_mesh_obj, poly_solid,
                     moulding_profile, add_bevel, add_subsurf, link, DEG)


# ----------------------------------------------------------------------------- helpers
def frame_and_panel(name, w, h, frame_w, thick, col, mat_frame, mat_panel,
                    matrix, field_bevel=0.013, panel_t=None, field_mat=None,
                    inner_border=0.0, rings=True):
    """Frame-and-panel assembly in local space (panel plane = XZ, thickness = Y).
    `matrix` places it in the world. Returns list of objects."""
    objs = []
    panel_t = thick * 0.62 if panel_t is None else panel_t
    y0 = -thick / 2
    # stiles (vertical) and rails (horizontal) sit flush, panel floats between them
    stile_w = frame_w
    for i, sx in enumerate((-1, 1)):
        o = box(f"{name}_stile{i}", (stile_w, thick, h), (sx * (w - stile_w) / 2, 0, 0),
                col, mat_frame, bevel=0.0035, bevel_segments=2)
        objs.append(o)
    rail_h = frame_w
    for i, sz in enumerate((-1, 1)):
        o = box(f"{name}_rail{i}", (w - 2 * stile_w + 0.002, thick, rail_h),
                (0, 0, sz * (h - rail_h) / 2), col, mat_frame, bevel=0.0035,
                bevel_segments=2)
        objs.append(o)
    # panel, recessed to sit in the groove, fielded by a broad chamfer
    pw = w - 2 * stile_w + 0.006
    ph = h - 2 * rail_h + 0.006
    p = box(f"{name}_panel", (pw, panel_t, ph), (0, -0.002, 0), col,
            field_mat or mat_panel, bevel=field_bevel, bevel_segments=3,
            bevel_profile=0.62)
    objs.append(p)
    # groove shadow lines at the panel/frame junction
    for sx in (-1, 1):
        objs.append(box(f"{name}_groove{sx}", (0.0016, thick * 0.55, ph),
                        (sx * (pw / 2 + 0.0012), -0.004, 0), col,
                        bpy.data.materials.get("JOINT_SHADOW")))
    for o in objs:
        o.matrix_world = matrix @ o.matrix_basis
    return objs


def place(x, y, z, rx=0.0, ry=0.0, rz=0.0):
    return (Matrix.Translation((x, y, z)) @
            Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(ry, 4, 'Y') @
            Matrix.Rotation(rx, 4, 'X'))


def moulded_edge(name, w, d, h, center, col, mat, profile="ovolo", mould_w=0.012,
                 mould_d=0.010, around='front'):
    """Small run of ovolo/cove moulding used on plinth tops, drawer lips, rails."""
    prof = moulding_profile(mould_w, mould_d, profile)
    objs = []
    obj = poly_solid(name, prof, 'X', w, col, mat, smooth=True)
    obj.location = Vector((center[0] - w / 2, center[1], center[2]))
    objs.append(obj)
    return objs


# ----------------------------------------------------------------------------- castors
def build_castors(col, M):
    """Six castors: brass fork, darkened steel wheel, axle, screwed fixing plate."""
    objs = []
    positions = []
    for sx in (-1, 1):
        positions += [(sx * 0.712, 0.078), (sx * 0.392, 0.078), (sx * 0.552, 0.792)]
    for i, (x, y) in enumerate(positions):
        tag = f"CAST_{i:02d}"
        # fixing plate
        objs.append(box(f"{tag}_plate", (0.062, 0.062, 0.006), (x, y, 0.072), col,
                        M['brass'], bevel=0.0015))
        for sx in (-1, 1):
            for sy in (-1, 1):
                objs.append(cylinder(f"{tag}_screw{sx}{sy}", 0.0032, 0.0035,
                                     (x + sx * 0.023, y + sy * 0.023, 0.0755), col,
                                     M['brass'], verts=12, bevel=0.0006))
        # fork: two side plates with a shaped outline
        for sx in (-1, 1):
            bm = box_bm(0.0045, 0.052, 0.050)
            ob = new_mesh_obj(f"{tag}_fork{sx}", bm, col, M['steel'])
            ob.location = (x + sx * 0.0095, y - 0.004, 0.046)
            bevel = add_bevel(ob, 0.0016, 2)
            objs.append(ob)
        # fork crown
        objs.append(box(f"{tag}_crown", (0.024, 0.020, 0.008), (x, y - 0.004, 0.0655), col,
                        M['steel'], bevel=0.0015))
        # wheel: hub + tyre, slightly worn flat at contact
        wheel = cylinder(f"{tag}_wheel", P.CAST_R, P.CAST_W, (x, y - 0.006, P.CAST_R), col,
                         M['iron'], verts=48, axis='X', bevel=0.0012)
        add_subsurf(wheel, 1)
        objs.append(wheel)
        objs.append(cylinder(f"{tag}_hub", 0.0075, P.CAST_W + 0.004,
                             (x, y - 0.006, P.CAST_R), col, M['steel'], verts=24, axis='X'))
        objs.append(cylinder(f"{tag}_axle", 0.0035, P.CAST_W + 0.030,
                             (x, y - 0.006, P.CAST_R), col, M['steel'], verts=16, axis='X'))
        for sx in (-1, 1):
            objs.append(cylinder(f"{tag}_axle_nut{sx}", 0.0058, 0.004,
                                 (x + sx * (P.CAST_W / 2 + 0.014), y - 0.006, P.CAST_R),
                                 col, M['brass'], verts=6, axis='X'))
    return objs


# ----------------------------------------------------------------------------- plinth
def build_plinth(col, M):
    objs = []
    for i, sx in enumerate((-1, 1)):
        cx = sx * P.PED_X
        # plinth block, slightly proud of the carcass
        objs.append(box(f"PLINTH_{i}", (P.PED_W + 0.024, P.PED_Y1 - P.PED_Y0 + 0.024,
                                        P.PLINTH_H),
                        (cx, (P.PED_Y0 + P.PED_Y1) / 2, P.PLINTH_Z0 + P.PLINTH_H / 2),
                        col, M['oak_qsa'], bevel=0.003))
        # top moulding (ovolo) running round the plinth
        prof = moulding_profile(0.011, 0.008, "ovolo")
        for name, axis, length, loc, rot in [
            (f"PLINTH_MOULD_F_{i}", 'X', P.PED_W + 0.024,
             (cx, P.PED_Y0 - 0.012, P.PLINTH_Z0 + P.PLINTH_H - 0.008), 0),
            (f"PLINTH_MOULD_B_{i}", 'X', P.PED_W + 0.024,
             (cx, P.PED_Y1 + 0.012, P.PLINTH_Z0 + P.PLINTH_H - 0.008), 0),
        ]:
            o = poly_solid(name, prof, axis, length, col, M['oak_qsa'], smooth=True)
            o.location = Vector((cx - P.PED_W / 2 - 0.012, loc[1], loc[2]))
            if rot:
                o.rotation_euler[2] = rot
            objs.append(o)
        side_len = P.PED_Y1 - P.PED_Y0 + 0.024
        for sx2 in (-1, 1):
            o = poly_solid(f"PLINTH_MOULD_S_{i}{sx2}", prof, 'Y', side_len, col,
                           M['oak_qsa'], smooth=True)
            if sx2 > 0:
                o.location = Vector((cx + P.PED_W / 2 + 0.012, P.PED_Y0 - 0.012,
                                     P.PLINTH_Z0 + P.PLINTH_H - 0.008))
            else:
                o.rotation_euler[2] = math.pi
                o.location = Vector((cx - P.PED_W / 2 - 0.012, P.PED_Y0 - 0.012 + side_len,
                                     P.PLINTH_Z0 + P.PLINTH_H - 0.008))
            objs.append(o)
        # dust skirt under the plinth so the underside is not a hole
        objs.append(box(f"PLINTH_SKIRT_{i}", (P.PED_W - 0.02, P.PED_Y1 - P.PED_Y0 - 0.02, 0.012),
                        (cx, (P.PED_Y0 + P.PED_Y1) / 2, P.PLINTH_Z0 + 0.006), col,
                        M['oak_end']))
    return objs


# ----------------------------------------------------------------------------- pedestals
def drawer_stack_heights(available_h, n, filing_h):
    """Graduated stack: deep filing drawer at the bottom, then progressively shallower."""
    rail = 0.012
    usable = available_h - rail * (n - 1) - 0.010
    rest = usable - filing_h
    weights = [1.00, 1.10, 1.22]
    s = sum(weights[:n - 1])
    return [filing_h] + [rest * w / s for w in weights[:n - 1]]


def build_pedestal(idx, col, M):
    """One pedestal: side panels, back, face frame, dust boards, inner structure."""
    objs = []
    cx = P.PED_X * (1 if idx == 0 else -1)
    x0, x1 = cx - P.PED_W / 2, cx + P.PED_W / 2
    y0, y1 = P.PED_Y0, P.PED_Y1
    z0, z1 = P.PED_Z0, P.PED_Z1
    t = P.PED_T
    tag = f"PED{idx}"

    # ---- carcass side panels (thickness across X)
    for sxn, xw in (("L", x0 + t / 2), ("R", x1 - t / 2)):
        objs.append(box(f"{tag}_SIDE_{sxn}", (t, y1 - y0, z1 - z0),
                        (xw, (y0 + y1) / 2, (z0 + z1) / 2), col, M['oak_qsa_y'],
                        bevel=0.002))
    # ---- back panel + fielded back (fully finished rear, brief §3)
    objs.append(box(f"{tag}_BACK", (P.PED_W - 2 * t, t, z1 - z0),
                    (cx, y1 - t / 2, (z0 + z1) / 2), col, M['oak_qsa'], bevel=0.002))
    for i, ox in enumerate((-0.098, 0.098)):
        m = place(cx + ox, y1 + 0.002, (z0 + z1) / 2)
        objs += frame_and_panel(f"{tag}_BACKPANEL{i}", 0.175, z1 - z0 - 0.06, 0.048, 0.016,
                                col, M['oak_qsa'], M['oak_cathedral'], m,
                                field_bevel=0.010)
    # ---- outer side: fielded panels (the "pronounced solid fielded panels")
    outward = 1 if cx > 0 else -1
    rz_side = -math.pi / 2 if outward > 0 else math.pi / 2
    x_face = (x1 - 0.009) if outward > 0 else (x0 + 0.009)
    for i, zc in enumerate((0.335, 0.560)):
        m = place(x_face, (y0 + y1) / 2 + 0.010, zc, rz=rz_side)
        objs += frame_and_panel(f"{tag}_SIDEPANEL{i}", 0.60, 0.190, 0.048, 0.018,
                                col, M['oak_qsa_y'], M['oak_qsa_y'], m,
                                field_bevel=0.010)
    # ---- inner side (faces the kneehole) - plain panels with shadow line
    inward = -1 if cx > 0 else 1
    rz_in = math.pi / 2 if inward < 0 else -math.pi / 2
    x_in_face = (x0 + 0.008) if inward < 0 else (x1 - 0.008)
    m = place(x_in_face, (y0 + y1) / 2, (z0 + z1) / 2, rz=rz_in)
    objs += frame_and_panel(f"{tag}_INNERSIDEPANEL", 0.58, 0.46, 0.048, 0.016,
                            col, M['oak_qsa_y'], M['oak_cathedral'], m, field_bevel=0.009)

    # ---- face frame: two stiles, top rail, bottom rail, and drawer rails
    fw = 0.052
    objs.append(box(f"{tag}_STILE_L", (fw, 0.024, z1 - z0), (x0 + fw / 2, y0 + 0.012,
                                                            (z0 + z1) / 2), col,
                    M['oak_rift'], bevel=0.003))
    objs.append(box(f"{tag}_STILE_R", (fw, 0.024, z1 - z0), (x1 - fw / 2, y0 + 0.012,
                                                            (z0 + z1) / 2), col,
                    M['oak_rift'], bevel=0.003))

    # ---- drawer stack inside the pedestal
    inner_z0 = z0 + 0.012
    inner_z1 = z1 - 0.030          # top rail
    heights = drawer_stack_heights(inner_z1 - inner_z0, P.N_PED_DRAWERS_PER_PEDESTAL,
                                   P.FILING_H)
    openings = []
    zc = inner_z1
    for i, h in enumerate(heights):
        openings.append((zc - h, zc))
        zc -= h + 0.012
    # rails between openings
    for i in range(1, len(openings)):
        top_of_lower = openings[i][1]
        objs.append(box(f"{tag}_DRAWER_RAIL{i}", (x1 - x0 - 2 * fw + 0.004, 0.024, 0.012),
                        (cx, y0 + 0.012, top_of_lower + 0.006), col, M['oak_rift'],
                        bevel=0.002))
    objs.append(box(f"{tag}_TOP_RAIL", (x1 - x0 - 2 * fw + 0.004, 0.024, 0.030),
                    (cx, y0 + 0.012, z1 - 0.015), col, M['oak_rift'], bevel=0.003))
    objs.append(box(f"{tag}_BOTTOM_RAIL", (x1 - x0 - 2 * fw + 0.004, 0.024, 0.012),
                    (cx, y0 + 0.012, inner_z0 + 0.006), col, M['oak_rift'], bevel=0.002))
    # ---- cock bead round each drawer opening (moulded lip, not a bare hole)
    for i, (lo, hi) in enumerate(openings):
        for sy, zz in ((1, hi), (-1, lo)):
            objs.append(box(f"{tag}_BEAD_Z{i}{sy}", (x1 - x0 - 2 * fw + 0.006, 0.006, 0.0045),
                            (cx, y0 + 0.0025, zz), col, M['oak_rift'], bevel=0.0016))
        for sx2 in (-1, 1):
            objs.append(box(f"{tag}_BEAD_X{i}{sx2}", (0.0045, 0.006, hi - lo - 0.004),
                            (cx + sx2 * (x1 - x0 - 2 * fw) / 2, y0 + 0.0025, (lo + hi) / 2),
                            col, M['oak_rift'], bevel=0.0016))
    # ---- dust boards / dividers between drawer openings, with runners
    for i, (lo, hi) in enumerate(openings):
        objs.append(box(f"{tag}_DUST{i}", (x1 - x0 - 2 * t - 0.004, y1 - y0 - 0.09, 0.010),
                        (cx, (y0 + y1) / 2 + 0.02, lo - 0.005), col, M['oak_rift'],
                        bevel=0.0015))
        for sxn in (-1, 1):
            objs.append(box(f"{tag}_RUNNER{i}{sxn}", (0.016, y1 - y0 - 0.13, 0.014),
                            (cx + sxn * (P.PED_W / 2 - t - 0.012),
                             (y0 + y1) / 2 + 0.01, lo + 0.004), col, M['oak_rift'],
                            bevel=0.0015))
    # ---- centre vertical divider so each drawer has two supports
    objs.append(box(f"{tag}_CENTRE_DIVIDER", (t, y1 - y0 - 0.10, inner_z1 - inner_z0),
                    (cx, (y0 + y1) / 2 + 0.02, (inner_z0 + inner_z1) / 2), col,
                    M['oak_rift'], bevel=0.002))
    return objs, openings


# ----------------------------------------------------------------------------- desktop
def build_desktop(col, M):
    objs = []
    w = P.DESK_X1 - P.DESK_X0
    d = P.DESK_Y1 - P.DESK_Y0
    cz = P.DESK_TOP_Z - P.TOP_TH / 2
    objs.append(box("DESKTOP_TOP", (w, d, P.TOP_TH), (0, (P.DESK_Y0 + P.DESK_Y1) / 2, cz),
                    col, M['oak_qsa'], bevel=0.004, bevel_segments=3))
    # front nosing: ogee/ovolo moulding under the top edge
    prof = moulding_profile(0.016, 0.017, "cove")
    o = poly_solid("DESKTOP_NOSING", prof, 'X', w, col, M['oak_qsa'], smooth=True)
    o.location = Vector((-w / 2, P.DESK_Y0, P.DESK_TOP_Z - P.TOP_TH - 0.017 + 0.001))
    objs.append(o)
    # side mouldings
    for sx in (-1, 1):
        o = poly_solid(f"DESKTOP_SIDE_MOULD{sx}", prof, 'Y', d, col, M['oak_qsa_y'],
                       smooth=True)
        if sx > 0:
            o.location = Vector((w / 2 - 0.001, P.DESK_Y0, P.DESK_TOP_Z - P.TOP_TH -
                                 0.017 + 0.001))
        else:
            o.rotation_euler[2] = math.pi
            o.location = Vector((-w / 2 + 0.001, P.DESK_Y0 + d,
                                 P.DESK_TOP_Z - P.TOP_TH - 0.017 + 0.001))
        objs.append(o)
    # leather-free writing surface: solid oak with a shallow tooled border line
    objs.append(box("WRITING_SURFACE_LEDGE", (w - 0.02, 0.085, 0.006),
                    (0, 0.028, P.DESK_TOP_Z + 0.003), col, M['oak_qsa'], bevel=0.0012))
    # support rails beneath the top between the pedestals
    for sy in (0.30, 0.66):
        objs.append(box(f"DESKTOP_BEARER{sy}", (P.KNEE_W + 0.10, 0.055, 0.024),
                        (0, sy, P.DESK_TOP_Z - P.TOP_TH - 0.012), col, M['oak_rift'],
                        bevel=0.002))
    return objs


# ----------------------------------------------------------------------------- kneehole
def build_kneehole(col, M):
    """Modesty board, central lockable drawer, centre filler and the slide housings."""
    objs = []
    # modesty board: a full frame-and-panel closing the kneehole at the back
    mod_h = 0.560
    mod_zc = P.PLINTH_Z0 + 0.030 + mod_h / 2
    m = place(0, P.PED_Y1 - 0.075, mod_zc)
    objs += frame_and_panel("MODESTY", P.KNEE_W - 0.006, mod_h, 0.052, 0.020, col,
                            M['oak_qsa'], M['oak_cathedral'], m, field_bevel=0.013)
    objs.append(box("MODESTY_BACKING", (P.KNEE_W - 0.006, 0.014, mod_h),
                    (0, P.PED_Y1 - 0.062, mod_zc), col, M['oak_rift'], bevel=0.002))
    # shoe rail under the modesty board
    objs.append(box("KNEEHOLE_SHOE_RAIL", (P.KNEE_W - 0.006, 0.020, 0.026),
                    (0, P.PED_Y1 - 0.075, P.PLINTH_Z0 + 0.020), col, M['oak_qsa'],
                    bevel=0.003))
    # central lockable drawer box under the desktop
    dz0, dz1 = 0.610, 0.700
    objs.append(box("CENTRE_DRAWER_CASE_TOP", (P.KNEE_W - 0.02, 0.60, 0.014),
                    (0, 0.32, dz1 + 0.007), col, M['oak_rift'], bevel=0.002))
    for sx in (-1, 1):
        objs.append(box(f"CENTRE_DRAWER_CASE_SIDE{sx}", (0.016, 0.60, dz1 - dz0 + 0.02),
                        (sx * (P.KNEE_W / 2 - 0.008), 0.32, (dz0 + dz1) / 2), col,
                        M['oak_rift'], bevel=0.002))
    objs.append(box("CENTRE_DRAWER_CASE_BOTTOM", (P.KNEE_W - 0.02, 0.60, 0.012),
                    (0, 0.32, dz0 - 0.006), col, M['oak_rift'], bevel=0.002))
    # centre post between the two slides (fixed)
    objs.append(box("CENTRE_POST", (0.096, 0.30, 0.075), (0, 0.16, 0.704), col,
                    M['oak_qsa'], bevel=0.003))
    return objs


# ----------------------------------------------------------------------------- slides
def build_writing_slides(col, M, out=P.SLIDE_OUT):
    """Two pull-out writing slides: top board, side runners, stops and guide rails."""
    objs = []
    for i, sx in enumerate((-1, 1)):
        x_c = sx * (P.KNEE_W / 2 - 0.078)
        z_c = 0.712
        y_c = 0.30 - out
        tag = f"SLIDE{i}"
        objs.append(box(f"{tag}_TOP", (P.SLIDE_W, 0.520, P.SLIDE_T),
                        (x_c, y_c, z_c), col, M['oak_qsa'], bevel=0.003,
                        bevel_segments=2))
        # lipped edge so the slide reads as a writing surface, not a shelf
        objs.append(box(f"{tag}_NOSING", (P.SLIDE_W + 0.012, 0.016, 0.010),
                        (x_c, y_c - 0.258, z_c + 0.002), col, M['oak_rift'],
                        bevel=0.002))
        for s in (-1, 1):
            objs.append(box(f"{tag}_RUNNER{s}", (0.014, 0.510, 0.024),
                            (x_c + s * (P.SLIDE_W / 2 - 0.007), y_c, z_c - 0.020), col,
                            M['oak_rift'], bevel=0.002))
        # fixed guide rails the slide travels on
        for s in (-1, 1):
            objs.append(box(f"{tag}_GUIDE{s}", (0.018, 0.520, 0.012),
                            (x_c + s * (P.SLIDE_W / 2 + 0.004), 0.285, z_c - 0.030), col,
                            M['oak_rift'], bevel=0.002))
        # brass stop blocks
        for s in (-1, 1):
            objs.append(box(f"{tag}_STOP{s}", (0.020, 0.016, 0.016),
                            (x_c + s * (P.SLIDE_W / 2 - 0.010), 0.062, z_c - 0.014), col,
                            M['brass'], bevel=0.002))
    return objs
