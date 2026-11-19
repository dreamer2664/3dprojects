#!/bin/bash
# Full render batch — real timestamps come from render.py at render start.
cd "$(dirname "$0")/.."
B=/opt/bl/blender-4.2.3-linux-x64/blender
BLEND=MODELS/rsv4_factory_2026.blend
run(){ echo "=== $1 $2 $3 ==="; $B -b $BLEND -P scripts/render.py -- --shot "$1" --res "$2" --samples "$3" 2>&1 | grep -E "\[render\]|Error|Traceback"; }
# heroes already rendered (2026-11-18_21-57-12 / 22-00-56)
run ortho_left   1600x1000 64
run ortho_right  1600x1000 64
run ortho_front  1200x1500 64
run ortho_rear   1200x1500 64
run ortho_top    1600x800  64
run low_front    1536x960 64
run engine       1280x800  72
run exhaust      1280x800  72
run front_susp   1280x800  72
run rear_susp    1280x800  72
run rear_wheel   1280x800  72
run cockpit      1280x800  80
run tank         1280x800  72
run winglets     1280x800  72
run naked        1536x960 56
run exploded     1536x960 48
run wireframe    1280x800  16
run final        1792x1120 96
echo "=== BATCH DONE ==="
