#!/usr/bin/env bash
# Full deliverable set (15 shot types / 20 images incl. 4 orthos). No OIDN denoise: it OOMs on 2 GB RAM.
# Usage: scripts/render_all.sh [shot ...]   (no args = everything)
set -u
cd "$(dirname "$0")/.."
BLENDER="$HOME/.cache/bl/blender-4.2.3-linux-x64/blender"
declare -A RES=( [hero_front34]=1536x960 [hero_rear34]=1536x960 [ortho_left]=1600x1000 [ortho_right]=1600x1000
  [ortho_front]=1200x1500 [ortho_rear]=1200x1500 [ortho_top]=1600x800 [low_front]=1536x960 [engine]=1280x800
  [exhaust]=1280x800 [rear_susp]=1280x800 [rear_wheel]=1280x800 [tank]=1280x800 [front_susp]=1280x800
  [winglets]=1280x800 [cockpit]=1280x800 [exploded]=1536x960 [naked]=1536x960 [wireframe]=1280x800 [final]=1792x1120 )
declare -A SPP=( [hero_front34]=80 [hero_rear34]=80 [ortho_left]=64 [ortho_right]=64 [ortho_front]=64 [ortho_rear]=64
  [ortho_top]=64 [low_front]=64 [engine]=72 [exhaust]=72 [rear_susp]=72 [rear_wheel]=72 [tank]=72 [front_susp]=72
  [winglets]=72 [cockpit]=80 [exploded]=48 [naked]=56 [wireframe]=16 [final]=96 )
ORDER="hero_front34 hero_rear34 final ortho_left ortho_right ortho_front ortho_rear ortho_top low_front engine exhaust rear_susp rear_wheel tank front_susp winglets cockpit exploded naked wireframe"
[ $# -gt 0 ] && ORDER="$*"
for s in $ORDER; do
  echo "=== $s ${RES[$s]} ${SPP[$s]} ==="
  $BLENDER -b MODELS/rsv4_factory_2026.blend -P scripts/render.py -- --shot "$s" --res "${RES[$s]}" --samples "${SPP[$s]}" > /tmp/r_$s.log 2>&1
  rc=$?
  grep -E "\[render\]|Error|Traceback" /tmp/r_$s.log
  [ $rc -ne 0 ] && echo "!!! $s FAILED rc=$rc (137 = OOM kill)"
done
echo "ALL DONE"
