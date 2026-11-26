#!/usr/bin/env bash
# Provision a headless Blender for this commission inside the sandbox.
# Verified working on Debian 13 (trixie), 2 vCPU / 1.9 GB RAM, no GPU.
# Blender 4.5.3 LTS adds ~1.2 GB of disk; it is installed to ~/.local/opt/blender
# (outside the repository, never committed).
set -euo pipefail

BLENDER_VERSION="${BLENDER_VERSION:-4.5.3}"
SERIES="${BLENDER_VERSION%.*}"          # 4.5
DEST="$HOME/.local/opt"
URL="https://download.blender.org/release/Blender${SERIES}/blender-${BLENDER_VERSION}-linux-x64.tar.xz"

echo "== 1/4 system libraries required by the headless binary =="
# Without libxkbcommon0 the tarball build dies with
#   "error while loading shared libraries: libxkbcommon.so.0"
sudo -n apt-get update -qq
sudo -n apt-get install -y -q \
  libxkbcommon0 libx11-6 libxi6 libxxf86vm1 libxfixes3 libxrender1 \
  libgl1 libglu1-mesa libsm6 libice6 libegl1

echo "== 2/4 download Blender ${BLENDER_VERSION} =="
mkdir -p "$DEST"
if [ ! -x "$DEST/blender/blender" ]; then
  curl -sL -o /tmp/blender.tar.xz "$URL"
  tar -xf /tmp/blender.tar.xz -C "$DEST"
  mv "$DEST/blender-${BLENDER_VERSION}-linux-x64" "$DEST/blender"
  rm -f /tmp/blender.tar.xz
fi

echo "== 3/4 version check =="
"$DEST/blender/blender" --version | head -1

echo "== 4/4 headless python + Cycles smoke test =="
cat > /tmp/_smoke.py <<'PY'
import bpy
bpy.ops.mesh.primitive_cube_add(size=1)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 8
sc.render.resolution_x = 128
sc.render.resolution_y = 128
sc.render.filepath = '/tmp/_smoke.png'
bpy.ops.render.render(write_still=True)
print("SMOKE_OK", bpy.app.version_string)
PY
"$DEST/blender/blender" -b --factory-startup --python /tmp/_smoke.py 2>&1 | grep -E "SMOKE_OK|Error"
echo "Blender ready at $DEST/blender/blender"
