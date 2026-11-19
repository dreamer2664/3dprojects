#!/usr/bin/env bash
# v5 revision batch: geometry/camera fixes only (runs against freshly rebuilt .blend)
set -u
cd "$(dirname "$0")/.."
BLENDER="$HOME/.cache/bl/blender-4.2.3-linux-x64/blender"
shot () {  # name res samples
  echo "=== $1 $2 $3 ==="
  $BLENDER -b MODELS/rsv4_factory_2026.blend -P scripts/render.py -- --shot "$1" --res "$2" --samples "$3" 2>&1 \
    | grep -E "\[render\]|Error|Traceback"
}
shot ortho_rear   1200x1500 64
shot ortho_top    1600x800  64
shot ortho_front  1200x1500 64
shot front_susp   1280x800  72
shot winglets     1280x800  72
shot cockpit      1280x800  80
shot exploded     1536x960  48
echo "ALL DONE v5"
