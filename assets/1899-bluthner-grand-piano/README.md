# 1899 Blüthner Exhibition Grand Piano — serial 53338

| File | Content |
|---|---|
| `1899_bluthner_grand_piano_master.blend` | Blender 4.2.3 LTS master scene with all 12 required collections |
| `1899_bluthner_grand_piano.glb` | glTF 2.0 binary export; dense instancing preserved |
| `textures/` | Authored PBR maps, incl. an 8192² rosewood source |
| `../../renders/1899-bluthner-grand-piano/` | Cycles renders from this scene |
| `../../docs/1899-bluthner-grand-piano/` | Build report, 60-source register, decisions, quality gate |

Rebuild: `blender -b -P scripts/generate_textures.py` (outside Blender) then
`blender -b --factory-startup -P scripts/build_piano.py`.
Validate: `blender -b --factory-startup -P scripts/validate_scene.py`.
Export: `blender -b --factory-startup -P scripts/export_glb.py`.
Inspect GLB: `blender -b --factory-startup -P scripts/inspect_glb.py`.

Large binaries are stored with Git LFS (`.gitattributes` at repo root).
Coordinates: metres, Z up, +Y keyboard/front, +X treble side.
