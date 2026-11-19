# Aprilia RSV4 Factory 1100 — MY2026 Shakedown Indigo — 3D reconstruction

Procedurally built Blender project (Blender 4.2 LTS).

| Path | Content |
|---|---|
| `scripts/` | Python build scripts — run `blender -b -P scripts/build_all.py` to regenerate `MODELS/rsv4_factory_2026.blend` |
| `MODELS/` | Editable `.blend` project files |
| `ASSETS/textures/` | Generated textures (livery, carbon, TFT, etc.) |
| `RENDERS/` | Timestamped renders `YYYY-MM-DD_HH-MM-SS__description.png` (never overwritten) |
| `research/` | Source archive, `SOURCE_REGISTER.md`, `TECHNICAL_NOTES.md` |
| `BUILD_LOG.md` · `DECISIONS.md` · `TODO.md` | Diary, assumptions, open items |

Coordinate system: metres, Z up, +X forward, +Y rider's left, origin on the ground under the rear axle.

## Re-rendering
Blender 4.2.3 LTS is not stored in the repo. Install: download `blender-4.2.3-linux-x64.tar.xz` from
download.blender.org into `~/.cache/bl/` (needs `libxkbcommon0`), then `scripts/render_all.sh [shot ...]`.
Do not use `--denoise 1` on 2 GB machines: OIDN causes OOM kills.
