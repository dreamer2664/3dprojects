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
