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
