"""
params.py — the single source of truth for every dimension of the desk.

All values in metres. Scale anchor: the Antiques Atlas / Yola Gray "Roll top Desk 28"
listing, 152 x 90.8 x 138 cm, with the recorded 77.5 cm writing height honoured exactly.
"""

# ---------------------------------------------------------------- overall envelope
W = 1.520          # overall width
D = 0.910          # overall depth  (desktop overhang included)
H = 1.380          # overall height (crown of the tambour roll)

# ---------------------------------------------------------------- vertical stack
CAST_H      = 0.075     # floor -> top of castor / bottom of plinth
PLINTH_Z0   = CAST_H
PLINTH_H    = 0.045
PED_Z0      = PLINTH_Z0 + PLINTH_H           # 0.120  pedestal carcass starts
DESK_TOP_Z  = 0.775                          # writing surface (brief: 77.5 cm)
TOP_TH      = 0.030                          # desktop thickness -> underside 0.745
PED_Z1      = DESK_TOP_Z - TOP_TH            # 0.745  pedestal carcass top

# ---------------------------------------------------------------- pedestals
PED_W       = 0.460                          # each pedestal width
PED_X       = W / 2 - PED_W / 2              # 0.530  pedestal centre in X
PED_X0      = PED_X - PED_W / 2              # 0.300
PED_X1      = PED_X + PED_W / 2              # 0.760
PED_Y0      = 0.000                          # front face
PED_Y1      = 0.860                          # back face
PED_T       = 0.022                          # carcass panel thickness

KNEE_W      = 2 * PED_X0                     # 0.600  clear kneehole width
KNEE_H      = PED_Z1 - PLINTH_Z0             # 0.625  clear kneehole height

# desktop (slight overhang front and sides)
DESK_Y0     = -0.025
DESK_Y1     = 0.885
DESK_X0     = -W / 2
DESK_X1     = W / 2

# ---------------------------------------------------------------- upper case
# S-profile tambour section: roll rises at the front, turns through a quarter round onto
# a flat roll-top deck, turns again and hangs inside the rear of the case.
UC_W        = 1.160                          # upper case width
UC_X        = UC_W / 2                       # 0.580  outer face of each cheek
CHEEK_X_IN  = 0.552                          # inner face of each side cheek
CHEEK_T     = 0.028                          # cheek thickness in X
UC_T        = 0.018                          # case panel thickness

# ---------------------------------------------------------------- tambour path
TAMB_Y_FRONT = 0.240                         # mid-line of the vertical front run
                                             # (set back to leave a 26 cm writing ledge)
R_MID        = 0.120                         # tambour mid-thickness radius at both turns
TAMB_TOP_Z   = 1.368                         # mid-line of the flat top run
TAMB_SPRING  = TAMB_TOP_Z - R_MID            # 1.248  where each quarter-round starts
TAMB_FRONT_Z0 = DESK_TOP_Z + 0.015           # 0.790  bottom of the front run
TAMB_Y_FWD   = TAMB_Y_FRONT + R_MID          # first turn centre (Y)
TAMB_Y_AFT   = TAMB_Y_FWD + 0.255            # second turn centre (Y)
TAMB_Y_BACK  = TAMB_Y_AFT + R_MID            # rear hanging run
TAMB_TAIL_Z  = 0.700                         # lowest the hanging tail can travel
TAMB_SKIN_R  = R_MID + 0.0085                # 0.1285 cheek skin radius
TAMB_SLAT_T  = 0.011                         # slat thickness (radial)
TAMB_SLAT_PITCH = 0.0165                     # slat pitch along the path
TAMB_GAP     = 0.0022                        # shadow gap between slats
TAMB_LEN     = 1.000                         # total slat run (60 slats)
UC_Y1        = TAMB_Y_BACK + 0.020           # rear face of the upper case
UC_Y1        = TAMB_Y_BACK + 0.020           # rear face of the upper case
CHEEK_Y_FRONT = TAMB_Y_FRONT - TAMB_SLAT_T / 2 - 0.0035   # front edge of cheeks

# ---------------------------------------------------------------- fitted interior
INT_X0      = -0.546
INT_X1      = 0.546
INT_Y0      = 0.270
INT_Y1      = 0.725
INT_Z0      = DESK_TOP_Z + 0.015             # 0.790
INT_Z1      = 1.215

WING_X_IN    = 0.220                         # centre bank half width
WING_COLS    = 3
WING_ROWS    = 5
CENTRE_COLS  = 5
CENTRE_ROWS  = 3
N_PIGEONHOLES   = CENTRE_COLS * CENTRE_ROWS              # 15
N_SMALL_DRAWERS = 2 * WING_COLS * WING_ROWS + 3          # 15 + 15 + 3 cushion = 33

# ---------------------------------------------------------------- posting slot
POST_SLOT_HALF_W = 0.080                     # 160 mm wide slot through the tambour

# ---------------------------------------------------------------- pedestal drawers
N_PED_DRAWERS_PER_PEDESTAL = 4               # 3 graduated + 1 deep filing drawer
FILING_H        = 0.235                      # bottom (filing) drawer front height
DRAWER_FRONT_T  = 0.020

# ---------------------------------------------------------------- writing slides
SLIDE_W      = 0.250
SLIDE_T      = 0.022
SLIDE_TRAVEL_OPEN = 0.240
SLIDE_OUT    = 0.110                         # "extended slightly" for the hero state

# ---------------------------------------------------------------- hardware scale
KNOB_R      = 0.0115
KNOB_LEN    = 0.024
LABEL_W     = 0.048
LABEL_H     = 0.020
LOCK_R      = 0.019

# ---------------------------------------------------------------- castors
N_CASTORS   = 6                              # per pedestal: 2 front, 1 rear
CAST_R      = 0.024
CAST_W      = 0.014

# ---------------------------------------------------------------- geometry budget
# measured ceiling in this sandbox is ~8-12M evaluated tris (ENVIRONMENT_PROBE.md)
TRI_BUDGET = 9_000_000
