# PROJECT STATE — victorian-rolltop-desk

Live status / engineering log for Commission 03. Updated at every milestone commit.
The commission brief is [`03_victorian_roll_top_desk.md`](03_victorian_roll_top_desk.md) (verbatim copy supplied with the commission).

## 1. Repository / branch facts (verified against GitHub API, 2026-11-26)

| Item | Value |
|---|---|
| Repository | `dreamer2664/3dprojects` (public, push access confirmed) |
| Remote default branch | `aprilia-rsv4-factory` — **not** `main`; this repo uses a per-commission branch per asset and no `main` branch exists |
| Working branch | `agent/victorian-rolltop-desk-masterpiece` |
| Branch base | `da04ae8` (= current default branch tip at branch creation) |
| Git LFS | **not installed and not configured** in this repo (no `.gitattributes`, `git lfs` unavailable in the sandbox) |

### Convention adjustment (brief §12.4)

The brief specifies delivery paths rooted at `assets/`, `renders/`, `docs/`.
The repository's established convention is **one top-level folder per commission**
(`aprilia-rsv4-factory/…`). To avoid colliding with other agents' work, this commission therefore lives in:

```
victorian-rolltop-desk/
  assets/victorian-rolltop-desk/      <- victorian_rolltop_desk_master.blend, .glb, textures/
  renders/victorian-rolltop-desk/     <- render package
  docs/victorian-rolltop-desk/        <- BUILD_REPORT.md, REFERENCE_LOG.md, QUALITY_GATE.md
  research/                           <- reference archive / source log working data
  scripts/                            <- Blender build + render automation
```

This is the only deviation from the literal paths in brief §11; nothing else is renamed.

## 2. Sandbox environment — measured, not assumed

| Resource | Measured value | Consequence for the brief |
|---|---|---|
| Blender | **not installed** at session start | must be provisioned before any geometry work |
| CPU | 2 cores | Cycles CPU path tracing only; no GPU/OptiX |
| RAM | ~1.9 GB total | hard ceiling on evaluated geometry and on frame-buffer size |
| Disk free | ~20 GB on `/` | sufficient for `.blend` masters + textures, tight for large EXR sets |
| OS | Debian 13 (trixie), Python 3.13 | no `bpy` pip wheel for 3.13; use the official Linux tarball build from blender.org |

### Known risk to brief §9 / §10 (must be documented, not hidden)

- **30M evaluated triangles** in one scene is near-certainly unreachable inside ~1.9 GB of RAM
  (Blender mesh data alone ≈ 40–60 B/triangle, plus sources and render buffers).
  Mitigation per brief §9: build **logical subassemblies** (pedestal carcasses, tambour + tracks,
  upper fitted interior, pedestal drawers, hardware) as separate high-detail parts, keep a single
  master `.blend` that links them, and count triangles from the evaluated depsgraph per part,
  summed honestly with the measurement method stated in `BUILD_REPORT.md`.
- **8K / 6K renders** need ≈ 0.5 GB per float RGBA buffer; 8K multi-layer EXR will exceed RAM.
  Mitigation: render at 4K-class resolutions (≥ 3840×2160 as the brief's stated minimum), or tile/
  crop for macro shots, and record exactly which frames were reduced and why. No claim will be made
  of an 8K render that was not actually produced at 8K.

No reduced target will be asserted as achieved; the gap between the brief and the hardware will be
stated with numbers in `QUALITY_GATE.md`.

## 3. Milestones (commit log of record)

| # | Milestone | Status |
|---|---|---|
| 0 | Branch + scaffold + credential safety + environment audit | **done** (this commit) |
| 1 | Research lock: ≥ 45 verified URLs, `REFERENCE_LOG.md` | pending |
| 2 | Proportions / dimension control block (1.52 × 0.91 × 1.38 m, 77.5 cm writing height check) | pending |
| 3 | Pedestal carcasses, fielded panels, plinth, castors | pending |
| 4 | Tambour: individual slats, backing, curved tracks, posting slot | pending |
| 5 | Upper fitted interior (33 drawers / 15 compartments target) | pending |
| 6 | Pedestal drawers + dovetail joinery + filing drawer | pending |
| 7 | Locking mechanism + linkage, open/closed states | pending |
| 8 | Materials: oak (QSA/rift), lacewood, sycamore, brass, leather, polish layers | pending |
| 9 | Render package + animations | pending |
| 10 | Independent GLB validation + `BUILD_REPORT.md` / `QUALITY_GATE.md` | pending |

## 4. Credential handling

The GitHub PAT supplied for this commission is **not** stored in the repository and is not printed
in any log. It is held at `~/.secrets/github_token` (mode `0600`, outside the working tree) and is
used only through a `git credential.helper` shell function that reads that file at call time, so no
credential is written into `.gitconfig`, `.git/config` or `.git-credentials`.
`.gitignore` additionally blocks `*.pat`, `*.token`, `github_pat*.txt`.
A `git grep` sweep for the token is run before every push.
