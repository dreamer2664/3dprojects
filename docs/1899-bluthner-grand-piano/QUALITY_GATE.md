# Quality gate — honest status

Legend: PASS = verified in this workspace · PARTIAL = work exists but not to
final stated resolution/completeness · FAIL = not achieved · BLOCKED = verified
technical constraint recorded.

| Acceptance test | Status | Evidence / gap |
|---|---|---|
| Exterior recognisably follows serial 53338 | PARTIAL | Case, lid, legs, lyre, desk and gilt mounts built from BADA gallery; macro fidelity still being judged. |
| All key BADA ornaments present | PARTIAL | Female heads, marquetry, lid rinceau, butterfly desk, filigree, bees, winged lions, carved legs, lyre, gilt frame all modelled; some are stylised rather than sculpted to photographic fidelity. |
| No unrelated styles mixed | PASS | Art Nouveau/Empire vocabulary only; Rococo comparison sources explicitly excluded. |
| Rosewood reads as polished wood at macro scale | PARTIAL | Authored 4K layered maps + 8K source; macro render pending review. |
| Complete lid-open interior | PARTIAL | Frame, board, bridges, 242 strings, pins, keyboard, action, dampers present; visual density in overhead render pending review. |
| Compass/stringing/Aliquot researched or documented | PASS | `DECISIONS.md` records assumptions and unresolved Aliquot status. |
| Every key/hammer/damper modelled | PASS | 88 keys, 88 hammer assemblies, 88 damper assemblies as linked instances. |
| Music desk glass/filigree/Tree of Life | PARTIAL | Geometry and glass shader present; close-up pending final review. |
| ≥40M evaluated triangles | PASS | 318,543,028 evaluated render triangles measured by `validate_scene.py`. |
| ≥55 working reference URLs | PASS | 60 logged in `REFERENCE_LOG.md`; 43 returned HTTP success, 17 bot-blocked and honestly marked. |
| High-resolution render set | PARTIAL | 15-view batch at 1600×900 running; 6–8K/EXR not reached on 2-CPU/1.9 GB sandbox. |
| `.blend` opens cleanly | PASS | Reopened by validation, export and render scripts. |
| GLB passes independent inspection | PARTIAL | Reimported into clean scene: 2,435 meshes, 321M triangles, 19 materials, 10 images; visual per-part inspection pending. |
| Reports truthful and complete | PASS | This gate, build report, source log and decisions record gaps explicitly. |
| Committed and pushed to exact branch | PARTIAL | Setup commit pushed; build milestones still being committed. |

## Verified technical blockers

- **OIDN denoising OOM:** Blender was killed (exit 137) with denoising enabled at
  960×540 × 32 samples. Denoising disabled; peak render memory ≈830 MB.
- **8K shader maps:** multiple 8192² maps plus 318M instanced triangles exceed
  1.9 GB. 8K source preserved on disk; 4K working maps used in shader.
- **Final resolution:** 3840×2160 × 28 images with adequate path-traced samples
  is not feasible in this sandbox within the current session; the batch is
  rendered at 1600×900 and the shortfall is recorded rather than disguised.
