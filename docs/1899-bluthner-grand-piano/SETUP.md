# Setup record — 1899 Blüthner Exhibition Grand Piano (serial 53338)

**Date:** 2026-11-26 (Europe/Rome)
**Branch:** `agent/1899-bluthner-grand-piano-masterpiece`
**Repository:** `https://github.com/dreamer2664/3dprojects`

## What this commit contains

- `COMMISSION_SPEC.md` — verbatim copy of the uploaded commission brief
  (`02_1899_bluthner_grand_piano.md`, 30,471 bytes). This preserves the full
  instructions, source list, acceptance tests and required deliverables.
- `.gitignore` — defensive patterns so a credential file can never be staged
  accidentally.
- This setup record.

**No model, texture, render or research work is included in this commit.** The
acceptance tests in the brief are not claimed as complete.

## Branch provenance

The repository's current default branch is `aprilia-rsv4-factory`, not `main`
(and not `master`). The branch was created from the latest fetched tip of that
default branch:

```
origin/aprilia-rsv4-factory @ da04ae86a04263abd04c1b801d6a4532b394f5e4
```

`origin/main` and the other existing branch (`feature/1950s-mechanical-typewriter`)
were not touched. `git fetch origin --prune` was run before branch creation.

## Credential handling

The supplied GitHub PAT was moved out of the uploads directory into
`/home/user/.secrets/github_pat.txt` with directory mode `700` and file mode
`600`. It is **outside the repository**, is not in `.git/config`, and is not
part of any commit. A local Git credential store file with the same restricted
permissions is used for pushes. The Git remote URL is the clean HTTPS URL with
no embedded token. No token value appears in any repository file or log.

## Repository-convention note

Existing projects in this repository live in a top-level project directory with
`ASSETS/`, `MODELS/`, `RENDERS/`, `research/`, `BUILD_LOG.md`, `DECISIONS.md`
and `TODO.md`. The commission brief instead mandates root-level
`assets/1899-bluthner-grand-piano/`, `renders/1899-bluthner-grand-piano/` and
`docs/1899-bluthner-grand-piano/` paths. Per §8 of the brief, this deviation is
explicitly recorded here: the brief's paths are being used, and existing
projects are untouched. If the project is later migrated to the repository's
per-project layout, this note must be updated.

## Next milestones (per brief §8)

1. Source lock / reference research (≥55 working sources).
2. Blockout and proportions, with documented dimensions and assumptions.
3. Case, rim, legs, lyre.
4. Ornament, marquetry, glass music desk, gilt mounts.
5. Interior: frame, soundboard, bridges, strings, pins.
6. Keyboard, action, hammers, dampers, pedals.
7. Materials and 8K texture sources.
8. Render package and independent GLB inspection.
9. Build report, reference log, quality gate, final push and commit hash.

## Build-session updates (2026-11-26)

- Git LFS was installed and configured locally (`.gitattributes`: `*.blend`,
  `*.glb`, `*.png`) because ordinary Git rejects files above 100 MB. This is a
  repository-convention adjustment for large binary assets; no existing project
  was changed.
- `research/1899-bluthner-grand-piano/` holds downloaded primary reference
  images, following the repository's existing per-project research convention.
- The master `.blend` and GLB were rebuilt after a material/ornament refinement
  pass; the committed versions are the ones used for the final render batch.
