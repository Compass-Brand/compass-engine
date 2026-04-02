# BMAD Reference Workspace

This directory retains Compass BMAD workflow context, provenance, and research that should not ship as runtime source.

> **Note:** The `research/` directory is intentionally retained here in `reference/` and not shipped in `src/bmad/`. It provides provenance, historical context, and design exploration that informed the shipped runtime. The authoritative shipped runtime lives in `src/bmad/`. This reference copy is maintained for audit, provenance, and research purposes.

## Current Status

Current rule:

- the shipped BMAD source of truth is `src/bmad/`
- keep `reference/BMAD/` for workflow notes, provenance, audits, and research
- do not treat this directory as the active runtime module tree

## Key Surfaces

- `BMAD-workflow.md` - canonical human-readable Compass BMAD workflow
- `modules/custom/bmm/` - retained Compass BMAD provenance and supporting material
- `modules/custom/core/` - retained shared Compass core provenance and supporting material
- `tools/automation/` - retained automation specs, policies, and templates
- `research/` - BMAD research and design inputs
- `_config/` - retained BMAD manifests and catalogs

## Read Order

1. `BMAD-workflow.md`
2. `modules/custom/bmm/module-help.csv`
3. `modules/custom/core/module-help.csv`
4. `tools/automation/README.md`
5. `../planning/README.md`

## Boundaries

- Do not treat imported sub-repo content as the active source of truth once it has been normalized into `src/`.
- Keep retained reference materials aligned enough to explain the shipped method, but do not duplicate active implementation edits here by default.
