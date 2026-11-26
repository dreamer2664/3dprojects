"""
parts_interior.py — the fitted upper interior: carcass, dividers, 15 vertical pigeonholes,
the letter rack, two pen trays, and 33 individually built internal drawers.

Inventory (asserted at build time by build_master.py):
    left wing   3 columns x 5 rows  = 15 drawers
    right wing  3 columns x 5 rows  = 15 drawers
    centre      3 cushion-front drawers (no external pulls)
    centre      5 columns x 3 rows  = 15 vertical pigeonholes
"""
import bpy
import math
from mathutils import Vector, Matrix
from . import params as P
from .common import box, cylinder, poly_solid, add_bevel, moulding_profile
from . import hardware as HW

LINING_T = 0.006
SHELF_T = 0.008
DIV_T = 0.006
DRAWER_DEPTH = 0.300


def _span(a, b, n, gap):
    """Divide a length into n equal cells separated by `gap`, return cell centres/widths."""
    total = b - a - gap * (n - 1)
    w = total / n
    return [(a + i * (w + gap), w) for i in range(n)], w


def build_interior_carcass(col, M):
    objs = []
    x0, x1 = P.INT_X0, P.INT_X1
    y0, y1 = P.INT_Y0, P.INT_Y1
    z0, z1 = P.INT_Z0, P.INT_Z1
    # side linings + back lining
    for sx in (x0, x1):
        objs.append(box(f"INT_LINING_SIDE_{sx:+.3f}", (LINING_T, y1 - y0, z1 - z0),
                        (sx + (LINING_T / 2 if sx > 0 else -LINING_T / 2),
                         (y0 + y1) / 2, (z0 + z1) / 2), col, M['oak_qsa_y'], bevel=0.001))
    objs.append(box("INT_LINING_BACK", (x1 - x0, LINING_T, z1 - z0),
                    (0, y1 - LINING_T / 2, (z0 + z1) / 2), col, M['oak_qsa'], bevel=0.001))
    objs.append(box("INT_LINING_BOTTOM", (x1 - x0, y1 - y0, SHELF_T),
                    (0, (y0 + y1) / 2, z0 + SHELF_T / 2), col, M['oak_qsa'], bevel=0.001))

    # ---- the two vertical partitions that separate the wings from the centre bank
    for sx in (-1, 1):
        objs.append(box(f"INT_PARTITION_{sx}", (DIV_T + 0.004, y1 - y0, z1 - z0),
                        (sx * P.WING_X_IN, (y0 + y1) / 2, (z0 + z1) / 2), col,
                        M['oak_qsa'], bevel=0.0018))

    # ---- wings: 3 columns x 5 rows of drawer cells
    cl = x0 + LINING_T
    cr = x1 - LINING_T
    for sx in (-1, 1):
        wx0 = P.WING_X_IN + DIV_T / 2 if sx > 0 else cl
        wx1 = cr if sx > 0 else -P.WING_X_IN - DIV_T / 2
        cells, w = _span(wx0, wx1, P.WING_COLS, DIV_T)
        # vertical dividers between the 3 columns
        for i in range(1, P.WING_COLS):
            xd = cells[i][0] - w / 2 - DIV_T / 2
            objs.append(box(f"INT_WING_DIV_{sx}_{i}", (DIV_T, y1 - y0 - 0.004, z1 - z0),
                            (xd, (y0 + y1) / 2, (z0 + z1) / 2), col, M['oak_rift'],
                            bevel=0.0012))
        # 4 shelves between 5 rows
        rows, h = _span(z0 + SHELF_T, z1, P.WING_ROWS, 0.0)
        for i in range(1, P.WING_ROWS):
            zs = rows[i][0] - h / 2
            objs.append(box(f"INT_WING_SHELF_{sx}_{i}", (wx1 - wx0, y1 - y0 - 0.002, SHELF_T),
                            ((wx0 + wx1) / 2, (y0 + y1) / 2, zs), col, M['oak_rift'],
                            bevel=0.0012))
            # drawer runners on each shelf: two per cell
            for cell in cells:
                for s2 in (-1, 1):
                    rx = cell[0] + s2 * (cell[1] / 2 - 0.010)
                    if abs(rx) > 0.528:      # keep runners inside the locked lining
                        continue
                    objs.append(box(f"INT_RUNNER_{sx}_{i}_{cell[0]:+.2f}_{s2}",
                                    (0.008, DRAWER_DEPTH - 0.04, 0.009),
                                    (rx, y0 + DRAWER_DEPTH / 2, zs + SHELF_T / 2 + 0.0045),
                                    col, M['oak_rift'], bevel=0.001))
        # shelf lip along the front edge of the whole wing
        for i in range(1, P.WING_ROWS):
            zs = rows[i][0] - h / 2
            objs.append(box(f"INT_SHELF_LIP_{sx}_{i}", (wx1 - wx0, 0.010, 0.006),
                            ((wx0 + wx1) / 2, y0 + 0.005, zs + 0.007), col,
                            M['oak_qsa'], bevel=0.0012))

    # ---- centre bank: shelf over the 3 cushion drawers, then the pigeonhole grid
    zshelf = 0.895
    objs.append(box("INT_CENTRE_SHELF", (2 * P.WING_X_IN - DIV_T, y1 - y0, SHELF_T),
                    (0, (y0 + y1) / 2, zshelf), col, M['oak_qsa'], bevel=0.0018))
    objs.append(box("INT_CENTRE_SHELF_LIP", (2 * P.WING_X_IN - DIV_T, 0.012, 0.007),
                    (0, y0 + 0.006, zshelf + 0.0075), col, M['oak_qsa'], bevel=0.0015))
    cols, cw = _span(-P.WING_X_IN + DIV_T, P.WING_X_IN - DIV_T, P.CENTRE_COLS, DIV_T)
    rows2, rh = _span(zshelf + SHELF_T, z1, P.CENTRE_ROWS, SHELF_T)
    for i in range(1, P.CENTRE_COLS):
        xd = cols[i][0] - cw / 2 - DIV_T / 2
        objs.append(box(f"INT_PIGEON_DIV_{i}", (DIV_T, y1 - y0, z1 - (zshelf + SHELF_T)),
                        (xd, (y0 + y1) / 2, (zshelf + SHELF_T + z1) / 2), col,
                        M['oak_qsa'], bevel=0.0012))
    for i in range(1, P.CENTRE_ROWS):
        zs = rows2[i][0] - rh / 2
        objs.append(box(f"INT_PIGEON_SHELF_{i}",
                        (2 * P.WING_X_IN - 2 * DIV_T, y1 - y0, SHELF_T),
                        (0, (y0 + y1) / 2, zs), col, M['oak_qsa'], bevel=0.0012))
    # shaped arch tops / small mouldings in each pigeonhole: a delicate shelf bead
    for (cx0, _w) in cols:
        cx = cx0 + _w / 2
        for i in range(1, P.CENTRE_ROWS):
            zs = rows2[i][0] - rh / 2
            objs.append(box(f"INT_PIGEON_BEAD_{cx:+.2f}_{i}", (cw - 0.012, 0.008, 0.004),
                            (cx, y0 + 0.004, zs - SHELF_T / 2 - 0.002), col,
                            M['oak_qsa'], bevel=0.0012))

    # ---- letter rack: rails across the upper centre columns
    for i, zz in enumerate((z1 - 0.045, z1 - 0.095)):
        objs.append(box(f"LETTER_RACK_RAIL_{i}", (2 * P.WING_X_IN - 2 * DIV_T, 0.0085, 0.0105),
                        (0, y0 + 0.016, zz), col, M['oak_turned'], bevel=0.0025,
                        bevel_segments=2))
        for (cx0, _w) in cols[1:]:
            cx = cx0 + _w / 2
            objs.append(box(f"LETTER_RACK_POST_{i}_{cx:+.2f}", (0.008, 0.008, 0.030),
                            (cx, y0 + 0.016, zz + 0.010), col, M['oak_turned'],
                            bevel=0.0015))

    # ---- two horizontal pen trays on the centre shelf
    for i, sx in enumerate((-1, 1)):
        tc = sx * 0.108
        objs.append(box(f"PEN_TRAY_{i}_BODY", (0.192, 0.115, 0.020),
                        (tc, y0 + 0.062, zshelf + SHELF_T / 2 + 0.010), col,
                        M['oak_qsa'], bevel=0.0025))
        # hollow the tray: raised rim strips (open tray, real void between them)
        for sy in (-1, 1):
            objs.append(box(f"PEN_TRAY_{i}_RIM_Y{sy}", (0.192, 0.010, 0.011),
                            (tc, y0 + 0.062 + sy * 0.0525, zshelf + SHELF_T / 2 + 0.0255),
                            col, M['oak_qsa'], bevel=0.0018))
        for sx2 in (-1, 1):
            objs.append(box(f"PEN_TRAY_{i}_RIM_X{sx2}", (0.010, 0.115, 0.011),
                            (tc + sx2 * 0.091, y0 + 0.062,
                             zshelf + SHELF_T / 2 + 0.0255), col, M['oak_qsa'],
                            bevel=0.0018))
        objs.append(box(f"PEN_TRAY_{i}_FLOOR", (0.176, 0.099, 0.004),
                        (tc, y0 + 0.062, zshelf + SHELF_T / 2 + 0.0205), col,
                        M['baize'], bevel=0.0008))
    return objs, cols, cw, rows2, rh, zshelf


# ---------------------------------------------------------------- internal drawers
def build_small_drawer(name, w, h, centre, col, M, cushion=False, label=True, knob=True):
    """One internal drawer: oak front, sycamore sides/back/bottom, lacewood lining,
    runner grooves, brass knob and (optionally) a brass label frame."""
    objs = []
    cx, cy, cz = centre
    ft = 0.014                      # front thickness
    st = 0.0055                     # side thickness
    bt = 0.0045                     # bottom thickness
    depth = DRAWER_DEPTH - 0.02
    front_w = w - 0.004
    front_h = h - 0.005
    y_front = cy - depth / 2

    # front: oak, cushion-front moulding when requested
    f = box(f"{name}_FRONT", (front_w, ft, front_h), (cx, y_front + ft / 2, cz), col,
            M['oak_qsa'], bevel=(0.004 if cushion else 0.0018), bevel_segments=3,
            bevel_profile=0.7)
    objs.append(f)
    # sides (sycamore, dovetail-grain along the drawer length)
    for sx in (-1, 1):
        objs.append(box(f"{name}_SIDE{sx}", (st, depth - ft, h - 0.012),
                        (cx + sx * (front_w / 2 - st / 2), y_front + ft + (depth - ft) / 2,
                         cz - 0.002), col, M['sycamore'], bevel=0.0008))
        # runner groove shadow (the runner inside the case engages here)
        objs.append(box(f"{name}_RUNGROOVE{sx}", (0.0022, depth - ft - 0.03, 0.006),
                        (cx + sx * (front_w / 2 + 0.0002), y_front + ft + (depth - ft) / 2,
                         cz - h / 2 + 0.014), col, M['shadow']))
    # back
    objs.append(box(f"{name}_BACK", (front_w - 2 * st, st, h - 0.014),
                    (cx, y_front + depth - st / 2, cz - 0.002), col, M['sycamore'],
                    bevel=0.0008))
    # bottom, set into a groove 3 mm above the lower edge
    objs.append(box(f"{name}_BOTTOM", (front_w - 2 * st + 0.002, depth - ft - st + 0.002,
                                      bt),
                    (cx, y_front + ft + (depth - ft - st) / 2, cz - h / 2 + 0.006),
                    col, M['sycamore'], bevel=0.0006))
    # lacewood lining: bottom liner + side liners (the reference's lacewood linings)
    objs.append(box(f"{name}_LINER_BOTTOM", (front_w - 2 * st - 0.001,
                                             depth - ft - st - 0.004, 0.0018),
                    (cx, y_front + ft + (depth - ft - st) / 2,
                     cz - h / 2 + 0.006 + bt / 2 + 0.0009), col, M['lacewood'],
                    bevel=0.0))
    for sx in (-1, 1):
        objs.append(box(f"{name}_LINER_SIDE{sx}", (0.0016, depth - ft - st - 0.006, h - 0.03),
                        (cx + sx * (front_w / 2 - st - 0.0009), y_front + ft +
                         (depth - ft) / 2, cz + 0.002), col, M['lacewood'], bevel=0.0))
    # dovetail shadow lines at both front corners (cut joint representation)
    for sx in (-1, 1):
        for k in range(4):
            zz = cz - front_h / 2 + front_h * (k + 0.5) / 4
            objs.append(box(f"{name}_DT_{sx}_{k}", (0.0012, 0.006, front_h / 4 * 0.55),
                            (cx + sx * (front_w / 2 - st / 2), y_front + ft + 0.0025, zz),
                            col, M['shadow']))
    if knob:
        # reference: every internal drawer carries an oak knob plus a brass label holder
        objs += HW.oak_knob(f"{name}_KNOB", (cx, y_front - 0.0015, cz), col, M,
                            radius=0.0090, length=0.017)
    if label:
        objs += HW.label_frame(f"{name}_LABEL", (cx, y_front - 0.0008,
                                                 cz + front_h / 2 - 0.016), col, M,
                               w=min(0.042, front_w - 0.02))
    return objs


def build_internal_drawers(col, M, cols, cw, rows2, rh, zshelf):
    """33 drawers: 15 left wing, 15 right wing, 3 centre cushion fronts."""
    objs = []
    wings = []
    cl = P.INT_X0 + LINING_T
    cr = P.INT_X1 - LINING_T
    for sx in (-1, 1):
        wx0 = P.WING_X_IN + DIV_T / 2 if sx > 0 else cl
        wx1 = cr if sx > 0 else -P.WING_X_IN - DIV_T / 2
        cells, w = _span(wx0, wx1, P.WING_COLS, DIV_T)
        rows, h = _span(P.INT_Z0 + SHELF_T, P.INT_Z1, P.WING_ROWS, 0.0)
        for ci, (cx0, wid) in enumerate(cells):
            cx = cx0 + wid / 2          # _span returns cell START, not centre
            for ri, (cz, hei) in enumerate(rows):
                n = f"UPPER_DRAWER_{'L' if sx < 0 else 'R'}{ci}{ri}"
                objs += build_small_drawer(n, wid - 0.006, hei - 0.008,
                                           (cx, P.INT_Y0 + DRAWER_DEPTH / 2 +
                                            0.01, cz), col, M,
                                           cushion=False, label=True, knob=True)
                wings.append(n)
    # centre: three concealed cushion-front drawers
    ccells, ccw = _span(-P.WING_X_IN + DIV_T, P.WING_X_IN - DIV_T, 3, DIV_T)
    for i, (cx0, wid) in enumerate(ccells):
        cx = cx0 + wid / 2
        n = f"UPPER_CUSHION_DRAWER_{i}"
        objs += build_small_drawer(n, wid - 0.006, zshelf - P.INT_Z0 - 0.020,
                                   (cx, P.INT_Y0 + DRAWER_DEPTH / 2 + 0.01,
                                    (zshelf - 0.008 + P.INT_Z0 + SHELF_T) / 2 + 0.004),
                                   col, M, cushion=True, label=False, knob=False)
    return objs, wings
