# BUILD LOG — Aprilia RSV4 Factory 1100 (MY2026, Shakedown Indigo)

Times are the sandbox clock (UTC). User local time is Europe/Rome (UTC+1).

---

## Session 1 — 2026-11-18

### 20:19 — Repository setup
- Cloned `dreamer2664/3dprojects`. **The repository was completely empty** (no commits, no branches, so no existing modelling conventions to follow). Created branch `aprilia-rsv4-factory` from scratch; nothing else was touched.
- Created project structure `aprilia-rsv4-factory/{research,RENDERS,ASSETS,MODELS,scripts}`.
- Removed the access token from `.git/config` remote URL after cloning (token is supplied only at push time).

### 20:20 – 20:30 — Research phase
**Work completed**
- Read official product page (2026), official 2026 tech-spec PDF (archived), 2026 press release text; downloaded **all 9** RSV4 Factory press photos at the max size the server provides (1920 px) and studied each one.
- Downloaded official product-page imagery: 7 premium gallery images at **3840×2560**, plus box/hotspot/tab/wall images (16 files).
- Read 2025 evolution press release (winglets, Hypure, catalyst relocation, new top clamp).
- Parts catalogues: the diagram subpages return empty bodies to scripted requests, so the full-resolution diagram URL was derived from the index thumbnail hash and checked against a `fetch_page` read of the Öhlins fork subpage. **116 exploded diagrams** archived (58 × 2025 E5+, 58 × 2024). Studied 16 key diagrams in detail (frame, swingarm, exhaust, crankcases, fairings, cooling, airbox, tail, steering, heads, throttle bodies, shock, rear wheel, controls).
- Found and archived the official **Service Station Manual 2Q000401** (RSV4 1100 Factory 2019–20, 549 pp.); extracted the characteristics chapter (frame A/B/C dimensions, chain, ratios, cooling/lubrication architecture).
- Archived official 2022 + MY20 spec sheets (wheelbase, head angle 24.6°, trail 104.5 mm, 6-pin floating discs).
- Hypure and Öhlins TTX references via search.

**Problems & resolutions**
- Brochure PDF and first spec-PDF request → Akamai "Access Denied". The spec PDF succeeded with a browser user agent; the brochure stayed blocked → marked ❌ in the register.
- `/tmp` is a 1 GB RAM tmpfs: the Blender tarball filled it and broke later writes. Moved Blender to `/opt/bl` on disk.

**Decisions**: D-001 … D-007 recorded in `DECISIONS.md` (procedural Blender scripts, coordinate system, hard points, black frame for 2026).

**Sources consulted**: register entries 1–16.

**Renders**: none yet.

**Next**: commit research, then build the geometry hard-point skeleton + wheels/brakes/fork.

## Session 2 — Modelling (2026-11-18)

**20:50–21:40** Procedural build system + full motorcycle assembled.
- Wrote `scripts/lib.py` extensions (`rod`, `extrude_xz/xy`, viewport colours) and modules:
  `parts_fork` (Öhlins NIX30 EC fork, triple clamps, EC steering damper, clip-ons),
  `parts_frame` (twin-spar frame, pivot plates, subframe, fuel cell, rearsets, sidestand),
  `parts_swingarm` (silver arm + black top truss per photos, TTX36 shock, linkage),
  `parts_engine` (65° V4: cases, banks, magnesium cam covers, throttle bodies, airbox),
  `parts_exhaust` (4-2-1 headers, under-engine catalyst, Ti silencer right side),
  `parts_cooling` (curved radiator, twin fans, hoses, oil cooler),
  `parts_body` (nose/fairings/bellypan/tank/tail/seats/fenders/winglets/screen/headlights/mirrors
  with projection-mapped photo-traced livery), `parts_cockpit` (5" TFT with race screen texture,
  switchgear, master cylinders, levers, reservoirs), `parts_drive` (525 chain as link mesh, 16T front
  sprocket), `parts_details` (braided brake lines, plate holder, indicators, wiring).
- `scripts/build_all.py` builds everything (464 objects) into `MODELS/rsv4_factory_2026.blend`.
- `scripts/qc.py` (workbench QC views, left view exactly matches p_18 calibration) and
  `scripts/render.py` (Cycles render presets: studio/dark/tech/outdoor envs, 20 shot definitions).
- QC: left-view overlay on p_18 → wheels, fork, frame, swingarm all align with the photo.
  Fixed silencer position/angle (from p_17 crop: titanium box rising to x −0.15, z 0.66 + black cap),
  swingarm colour confirmed satin silver both sides + black truss; clutch/alternator covers black.
- Cycles smoke renders (hero, cockpit, rear wheel, naked, exhaust) verified materials, livery
  projection (arrows, RSV4 badge, tank logo land correctly), TFT emissive screen, chain wrap.
- Decisions: D-008 livery tracing, D-009 Poly Haven CC0, D-010 revised hard points (see DECISIONS.md).
- Problems solved: stale matrix in parent(), Mix node sockets OK, tyre brightness was correct
  physics under bright studio (lighting tuned down instead), TFT UVs.
- Next: full 20+ render batch, orthographic QC vs photos, documentation updates.

**21:44** Milestone commit `d9bfb7d` pushed (model + textures + render system). Started the 20-shot
render batch in the background: hero ×2, ortho ×5, low front (outdoor HDRI + asphalt), engine,
exhaust, front/rear suspension, rear wheel/chain, cockpit TFT, tank/livery, winglets, naked,
exploded, wireframe, final studio. All filenames timestamped by render.py at render start.

**21:57–22:20** Render batch: first two heroes completed (21-57-12 front, 22-00-56 rear). Found and
fixed a critical constraint: OIDN denoiser spikes >1 GB at ≥1.5 MP and OOM-killed ortho renders —
denoising disabled, samples raised instead (memory now peaks ~530 MB/scene). Livery textures
downscaled to 2048px (calibration is resolution-independent). Exposure tuned to −0.9 EV for studio
shots after pixel comparison with p_18 (fairing 109→~58 RGB). QC overlay of left ortho on p_18:
wheels/body/tail/screen silhouettes align within a few mm.

**23:15–00:10** Batch v4 completed all 18 shots (orthos, details, naked, exploded, wireframe, final).
QC of outputs surfaced 8 fix items, all applied and re-rendered in batch v5:
rear-ortho camera was inside the tail (moved to x=-4.3), top ortho mirrored (roll -90°),
headlamp projectors recessed behind nose (moved +35mm fwd), fairing lower-front edge raised 90mm
to expose fork per p_18, lower wing element relocated to chin position, pillion seat -20mm,
bellypan +20mm (catalyst visible), front calipers rotated to trail the fork leg (165°→130°),
rear shock moved behind swingarm pivot (photo-correct), fuel cell shortened 90mm (swingarm pivot
visible), TFT texture mirrored (UV flip), winglets + front_susp cameras re-aimed, exploded offsets
increased (fork 1.02X, exhaust -0.85Y, body stack 0.62/0.88/1.05Z) + camera (5.4,5.0,2.45).
Silencer side VERIFIED correct: on the right (-Y), absent in left ortho, present in right — matches bike.

**NOTE:** sandbox restart wiped Blender from /opt and all v4 PNGs. Blender re-installed to
~/blender (persisted). Batch v6 re-renders the full final set incl. heroes (--denoise 1 at ≤1.5MP).
RENDERS/ will be committed to git so deliverables survive on the remote.

**00:55–01:05** Batch v6 full set re-rendered (13 shots) + v7 heroes (80spp, no denoise — OIDN now OOMs
even at 1.47MP with the grown scene). Wireframe OOM fixed by zeroing subsurf render levels before
the wireframe modifier. 'final' shot lighting aligned to approved hero recipe (HDRI 0.22 +
studio_lights 0.9). Photo overlay QC on new ortho_left: PASS (fork, fairing edge, catalyst,
pillion height all match p_18 within mm). 20 deliverable renders in RENDERS/.

**Nov 19, 06:30** Repo repair: commit ce77842 was built from a stale index after a sandbox restore and
deleted scripts/MODELS on the remote. This commit restores the full project (scripts with all v5
geometry fixes, MODELS/rsv4_factory_2026.blend, ASSETS, docs) + render_all.sh (no OIDN; wireframe
subsurf OOM guard; final shot uses hero lighting). RENDERS were lost again with the sandbox and are re-rendered.

**Nov 19, 07:40** Full set re-rendered via scripts/render_all.sh (20/20, 0 OOM kills, ~76 min, no OIDN).
Photo overlay QC on new ortho_left: PASS. All 20 PNGs pushed to origin incrementally.
Blender now lives in ~/.cache/bl (excluded from snapshots; reinstall if missing — see README).
