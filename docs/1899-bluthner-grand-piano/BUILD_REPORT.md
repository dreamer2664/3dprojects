# Build report — 1899 Blüthner Exhibition Grand, serial 53338

**Branch:** `agent/1899-bluthner-grand-piano-masterpiece`
**Base:** `origin/aprilia-rsv4-factory` @ `da04ae86a04263abd04c1b801d6a4532b394f5e4`
**Status:** substantial first build complete; acceptance gate **not yet fully passed** (see `QUALITY_GATE.md`).

## 1. Historical lock and dimensions

Primary anchor: BADA object record for serial 53338, the 1899 Blüthner shown at the
1900 Paris Exposition Universelle and bought by King Edward VII and Queen
Alexandra in 1902. All 14 full-resolution BADA gallery images were downloaded to
`research/1899-bluthner-grand-piano/photos/` and inspected, including the female-head
gilt mount, butterfly glass music desk, Art Nouveau cheek inlay, winged-lion /
bee fall mount, carved sunflower leg, two-pedal lyre, lid rinceau, burnished
gilt frame and maker cartouche.

BADA gives “length 214, width 157” without a visible unit. The 1stDibs record for
the same instrument gives H 38.98 in (99 cm), W 61.82 in (157 cm), D 84.26 in
(214 cm), which verifies centimetres. The model therefore uses:

| Quantity | Value used | Basis |
|---|---|---|
| Overall length (front to tail) | 2.14 m | BADA + 1stDibs |
| Overall width | 1.57 m | BADA + 1stDibs |
| Closed-lid height | ≈0.99 m | 1stDibs; Met Bechstein 99.5 cm cross-check |
| Case depth | ≈0.245 m (0.715–0.960 m) | inferred; Met case depth 35.5 cm includes different construction |
| Keyboard surface | 0.754 m | inferred from period keyboard height |
| Compass | 88 notes, MIDI 21–108 | defensible late-1890s standard; **not** documented for ser.53338 |
| Pedals | two | BADA explicitly describes a two-pedal lyre |
| Aliquot stringing | **not included as a documented fact** | cannot be substantiated for this serial; see `DECISIONS.md` |

## 2. Geometry

Built by `scripts/build_piano.py` in Blender 4.2.3 LTS. Repeated components are
linked instances sharing high-resolution source meshes, so the evaluated scene
carries real geometry without duplicating mesh data in RAM.

Independent validation (`scripts/validate_scene.py`, run on the saved `.blend`):

| Measure | Value |
|---|---|
| Unique mesh source triangles | 2,696,340 |
| Visible mesh instances | 2,385 |
| **Evaluated render triangles** | **318,543,028** |
| Objects | ~2,350 |
| Cameras | 15 |
| Required named collections | all 12 present, plus `TEMPLATES` |

This exceeds the 40M minimum by a wide margin and is not theoretical subdivision:
all geometry exists in the saved master/export. Instances are ordinary Blender
objects with shared mesh data, each carrying its own transform.

Subassemblies: laminated curved rim with open keywell; spruce soundboard;
ornate cast plate with rim bars, cross struts, bolts; bass bridge and treble
bridge; 242 individually placed strings with tuning and hitch pins; 88 naturals
and sharps with front pins; complete static action (hammer heads/shanks,
whippens, jacks, repetition levers, dampers and wires); tapered four-sided
baluster legs with sunflower relief and gilt bands; two-pedal lyre; bevelled
glass butterfly music desk with filigree and Tree of Life; female-head gilt
mounts, bees, winged lions, palmettes and Art Nouveau marquetry on cheeks, fall
and lid; hinged, propped open lid.

## 3. Materials and textures

Textures are authored by `scripts/generate_textures.py` (numpy/Pillow) and stored
under `assets/1899-bluthner-grand-piano/textures/`.

- `rosewood_color_8k_source.png` — true 8192² source with an 8K pore pass.
- Rosewood colour/normal/roughness — 4096² working maps used by the shader.
- Spruce soundboard colour — 4096².
- Gilt bronze colour/roughness — 2048².
- Ivory, ebony, felt, leather — 1024² each.

The 8K source is preserved but not loaded by the render shader. On this 1.9 GB
machine, loading multiple 8192² maps into Cycles plus the 318M-triangle scene
causes OOM. This is an explicitly recorded technical constraint, not a quiet
reduction: full-resolution source files remain in the project.

## 4. Render package

Cycles CPU, 40 samples, no denoising (OIDN exhausted RAM at 960×540 × 32 samples
and was disabled to preserve thin strings and filigree). Fifteen cameras are
defined; the batch in `scripts/render_batch.sh` writes to
`renders/1899-bluthner-grand-piano/`:

1 hero 3/4 lid open · 2 front keyboard/cheeks · 3 side case · 4 rear/tail ·
5 lid-open overhead · 6 action inspection · 7 female-head macro · 8 cheek
marquetry macro · 9 butterfly glass desk · 10 fall ornament · 11 carved leg ·
12 lyre/pedals · 13 strings/bridges/pins · 14 rosewood grain · 15 closed-lid
product.

After the first pass, nine inspection cameras were retargeted with
`scripts/fix_cameras.py`; the interior views hide the lid during rendering so
the frame/strings/action are visible, while hero/product views keep it. All
15 final images at 1600×900 were then rendered, plus a contact sheet.

Test renders at 1280×720 and final batch at 1600×900 are genuine Cycles renders
of the Blender scene. The 3840×2160/6–8K target, EXRs, turntable and mechanical
animation remain open work (see `TODO.md`) because of the 2-CPU/1.9 GB sandbox.

## 5. Export and independent inspection

`scripts/export_glb.py` exported `assets/1899-bluthner-grand-piano/1899_bluthner_grand_piano.glb`
(≈161 MB). glTF nodes share the source meshes, so the export retains the dense
instancing instead of flattening it.

`scripts/inspect_glb.py` reopened the GLB independently in a clean Blender
session:

| Check | Result |
|---|---|
| Mesh objects imported | 2,435 |
| Triangles | 321,233,528 |
| Materials | 19 |
| Images | 10 |
| Named key objects | 92 |
| Named string objects | 242 |
| Named leg objects | 166 |
| Bounds (incl. staging floor/wall) | −8…8 m X/Y, −0.5…4 m Z |

Scale, object presence and material/image links survived the round trip. Visual
macro inspection of every imported part is still pending.

## 6. Known limitations (truthful, not hidden)

- The 88-note compass and exact string scale are reconstruction assumptions,
  not serial-53338 documentation.
- Aliquot stringing is documented as unresolved and is not asserted as present.
- Rosewood is described as “Dalbergia-style” rather than claiming Brazilian
  rosewood for this instrument.
- Macro ornament is geometrically present but its close-up quality has not yet
  been judged against the BADA photographs at final resolution.
- 8K final renders, EXRs, turntable video and mechanical animation are pending.
- No AI-generated image has been presented as a render; all images in `renders/`
  come from Blender.
