# Setup & Environment Record — Commission 01 (`victorian-grandfather-clock`)

- **Commission:** Masterpiece Commission 01 — The 1900 J. Smith & Sons Exhibition Longcase Clock (NT 902584)
- **Repository:** `https://github.com/dreamer2664/3dprojects`
- **Base / Default Branch:** `aprilia-rsv4-factory` (`da04ae86a04263abd04c1b801d6a4532b394f5e4`)
- **Working Branch:** `agent/victorian-grandfather-clock-masterpiece`
- **Asset Slug:** `victorian-grandfather-clock`
- **Date Initialized:** 2026-11-26

## Deliverable Directory Layout

Per Section 8 of `COMMISSION_BRIEF.md`:

- `assets/victorian-grandfather-clock/victorian_grandfather_clock_master.blend`
- `assets/victorian-grandfather-clock/victorian_grandfather_clock.glb`
- `assets/victorian-grandfather-clock/textures/`
- `renders/victorian-grandfather-clock/`
- `docs/victorian-grandfather-clock/COMMISSION_BRIEF.md`
- `docs/victorian-grandfather-clock/BUILD_REPORT.md`
- `docs/victorian-grandfather-clock/REFERENCE_LOG.md`
- `docs/victorian-grandfather-clock/QUALITY_GATE.md`
- `scripts/victorian-grandfather-clock/` (procedural/sculpting/validation Blender Python scripts)

## Initial Sandbox Hardware Audit

- **CPU:** 2 vCPU — Intel(R) Xeon(R) @ 2.60GHz
- **RAM:** 1.9 GiB (0 B swap)
- **GPU:** None (CPU path tracing)
- **Disk:** 25 GB root filesystem (~20 GB free)
- **Credentials:** Stored outside repository in restricted sandbox storage (`chmod 700` / `chmod 600` + `GIT_ASKPASS` helper) and excluded via `.gitignore`. Never committed or logged.
