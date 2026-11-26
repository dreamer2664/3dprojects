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
| Blender | **not installed** at session start → **4.5.3 LTS now provisioned** at `~/.local/opt/blender` (see `scripts/provision_blender.sh`); headless + Cycles CPU smoke-tested | geometry and render work can proceed |
| CPU | 2 cores | Cycles CPU path tracing only; no GPU/OptiX |
| RAM | ~1.9 GB total | hard ceiling on evaluated geometry and on frame-buffer size |
| Disk free | ~20 GB on `/` | sufficient for `.blend` masters + textures, tight for large EXR sets |
| OS | Debian 13 (trixie), Python 3.13 | no `bpy` pip wheel for 3.13; use the official Linux tarball build from blender.org |

### Measured ceiling — brief §9 / §10 (evidence in `docs/victorian-rolltop-desk/ENVIRONMENT_PROBE.md`)

`scripts/probe_hardware.py` divides one mesh until the kernel kills Blender:

| Subdiv level | Evaluated tris | Peak RSS | Result |
|---|---|---|---|
| 10 | 8.39 M | 654 MB | OK, 1.3 s |
| 11 | 16.8 M | — | **OOM-killed** (exit 137, `anon-rss 1.29 GB`) |

So a realistic budget for the whole master in this sandbox is **≈ 8–12 M evaluated triangles**,
at ≈ 82 B of RSS per evaluated triangle — not the brief's ≥ 30 M. Consequences:

- **Geometry (§9):** build the desk as **logical subassemblies** (pedestal carcasses, tambour +
  tracks, upper fitted interior, pedestal drawers, hardware), each an independently modelled
  high-detail part in its own `.blend`/collection, with the master linking/referencing them. Triangle
  counts will be reported **per part from the evaluated depsgraph** and summed, with the method and
  the per-part memory measured at build time — never as hypothetical subdivision levels.
- **Renders (§10):** one 8K float RGBA layer is ≈ 530 MB, one 4K layer ≈ 132 MB, before Cycles
  buffers and BVH. 8K stills and multi-layer EXR masters are therefore **not producible here**.
  4K (3840×2160, the brief's stated minimum) is the realistic target, with macro shots done as
  cropped 4K frames.

Neither shortfall will be silently absorbed: the exact gap between brief target and delivered
numbers is recorded in `QUALITY_GATE.md`. These are hardware limits, not a choice to reduce detail.

## 3. Milestones (commit log of record)

| # | Milestone | Status |
|---|---|---|
| 0 | Branch + scaffold + credential safety + environment audit | **done** |
| 0b | Blender provisioned + hardware ceiling measured (`ENVIRONMENT_PROBE.md`) | **done** |
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
