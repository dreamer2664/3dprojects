# QUALITY GATE — acceptance tests from the commission brief (§13)

Honest status of every non-negotiable test. A box is ticked only where the delivered files prove
it. Where the test is not met, the reason is measured and stated; nothing is marked done to look
good.

| # | Test | Status | Evidence / reason |
|---|---|---|---|
| 1 | Late-Victorian English oak pedestal form, c.1890 reference, not modern office furniture | **PASS** | S-profile upper case with quarter-rounds onto a flat roll top, twin pedestals, fielded panels, cock-beaded drawer openings, plinths, castors; `params.py` derives every size from the listing. |
| 2 | Full-size proportions, kneehole, pedestals, upper case, fielded panels, S-shaped profile | **PARTIAL** | Height 1.381 m and writing height 0.775 m are exact; kneehole 0.600 × 0.625 m; S-profile built from two real quarter-rounds. **Width is 1.566 m against a 1.520 m target** (desktop side mouldings proud of the carcass) and depth is 0.961 m with the slides extended (0.885 m closed vs 0.910 m nominal). Recorded, not hidden. |
| 3 | Tambour of separate slats, flexible backing, real guide tracks, real open/closed route | **PASS** | 61 distinct slat objects, 61 canvas strips, two swept guide ribs per cheek forming an 11 mm channel, 1.638 m path, closed offset 0 / open offset 0.458 m built as two real states from the same geometry. |
| 4 | Central posting slot integrated in the tambour | **PASS** | 160 mm slot through slat 13 (slat split into two pieces) with brass lips and a recessed brass surround. |
| 5 | Fitted interior dense and deliberate, 33 drawers / 15 compartments target | **PASS** | Exactly 33 internal drawers (15 + 15 + 3 concealed cushion fronts) and exactly 15 vertical compartments, asserted in `BUILD_STATS`. |
| 6 | Small drawers are real boxes with runners, bottoms, sides, backs, hardware, joinery | **PARTIAL** | Every one of the 33 has front, two sides, back, grooved bottom, lacewood linings, runner groove, oak knob and brass label holder; case runners run under each row. Joinery on these small drawers is a dovetail **shadow**, not a cut joint (the 14 cut joints are on the large drawers). |
| 7 | Two pull-out slides, writing surface, letter rack, pen trays, large filing drawer | **PASS** | Slides modelled as assemblies (top, nosing, runners, guides, brass stops) and shown extended 110 mm; letter rack with rails + posts; 2 open pen trays; filing drawers present. |
| 8 | Linked tambour lock with plausible mechanism and demonstrable states | **PARTIAL** | Barrel lock, escutcheon, bolt, lock bar, 2 cranks, 2 rods, 2 catches modelled with thrown/withdrawn states in the closed/open builds. The linkage itself is **inferred** — no photograph of the original was available — and no key-turn animation was rendered. |
| 9 | Oak, lacewood, sycamore visually distinct; grain, rays, pores, end grain survive macro inspection | **PARTIAL** | Seven distinct timber materials with metric ring spacing and a ray-fleck term; separate end-grain materials; real 0.08–0.16 mm displacement on 231 surfaces. At macro distance the ray fleck reads as fine lines rather than true quarter-sawn fleck, and the two sources used for lacewood self-identify as AI-generated. Not yet catalogue-quality. |
| 10 | Brass, leather/baize, castors physically convincing | **PARTIAL** | Castors are full assemblies (plate, 4 screws, fork, crown, wheel, hub, axle, nuts); brass is two-tone tarnished; label frames carry cards and pins. Baize is used only for pen-tray floors and the tambour canvas. No leather writing inset (the reference desk is solid oak). |
| 11 | All surfaces complete: front, rear, sides, top, underside, drawer interiors, tambour housing | **PARTIAL** | Rear is fully fielded (pedestal backs + upper-case back panels), sides fielded both faces, drawer interiors lined, tambour pocket lined and closed. The **undersides** are modelled but thin (skirt + runners), not a full frame. |
| 12 | ≥ 30 M evaluated triangles, or a verified technical obstacle documented | **FAIL (documented)** | Measured ceiling: 8.39 M tris = 654 MB OK, 16.8 M = OOM kill; 1.9 GB RAM total. Delivered master = **5,487,528** evaluated triangles. The 30 M target was not reached; the obstacle is memory, quantified in `ENVIRONMENT_PROBE.md`. No arbitrary detail reduction was applied. |
| 13 | ≥ 45 real sources logged, meeting the required mix | **PASS (with caveat)** | 45 sources logged with type and verification level; 41 read as page text, 4 supplied by the brief. **Caveat:** no image gallery could be inspected (no browser in the environment), so the "15+ photographs" element is met by page type, not by actual image study. Stated in `REFERENCE_LOG.md` §E. |
| 14 | Full high-res hero, orthographic, open/closed, rear, mechanism and macro sets | **FAIL (documented)** | 17 stills rendered at **1280 × 800**, 32 spp, denoise off. 3840 × 2160 was killed during scene sync (849 MB); 1920 × 1080 with OIDN was killed after 112 s. Macro/detail shots use explicit camera distances. Resolution requirement not met. |
| 15 | `.blend` opens cleanly and `.glb` passes independent validation | **PASS** | Both masters re-opened in fresh sessions; GLB re-imported in a separate session: 1,551 meshes, 439,918 tris, 18 materials, 0 untextured meshes, bounds 1.566 × 0.961 × 1.381 m. |
| 16 | Build report, source log, quality checklist complete and truthful | **PASS** | This file, `BUILD_REPORT.md`, `REFERENCE_LOG.md`, `ENVIRONMENT_PROBE.md`. |
| 17 | All deliverables committed and pushed to the required branch | **PASS** | `agent/victorian-rolltop-desk-masterpiece`; commit hash in the final message. |

## Not delivered at all

- 8K/6K/4K stills, EXR masters.
- Tambour open/close animation, drawer/slide animations, lock animation, 360° turntable or video.
- Baked glTF textures (GLB carries geometry + nominal PBR base colours only).
- Exploded views of the fitted interior and the locking assembly (the camera presets exist in
  `render.py`, no frames were rendered).

## Overall verdict

**The mechanism, the inventory and the cabinetmaking structure pass. The photographic and
geometric scale targets do not.** This is a credible, mechanically real 1890 desk built at 5.49 M
evaluated triangles and rendered at 1280 × 800 on hardware that refuses anything larger. It is not
yet the "masterpiece" standard of the brief, and this document says so rather than implying
otherwise.
