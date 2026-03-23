# Modifying BMAD Customizations

Last reviewed: 2026-03-13

Guide to extending BMAD in `compass-engine` without forking upstream internals.

## Source of Truth

- Upstream: `BMAD-METHOD/` (read-only in normal workflow)
- Current shipped custom layer: `src/bmad/`
- Current module development root: `src/bmad/modules/custom/`
- Retained framework/provenance layer: `reference/BMAD/`

## Current Working Model

- Make BMAD method changes in the shipped source layer:
  - `src/bmad/BMAD-workflow.md`
  - `src/bmad/modules/custom/bmm/`
  - `src/bmad/modules/custom/core/`
  - `src/bmad/tools/automation/`
- Keep planning structure changes aligned in `src/planning/`.
- Keep `reference/` limited to supporting context that should not ship.

## Why This Pattern

- Keeps upstream updates easy (`BMAD-METHOD` can be synced independently)
- Keeps shipped runtime assets in one canonical source tree
- Makes module ownership explicit for future automation and documentation

## Upstream Sync

```bash
cd BMAD-METHOD
git pull origin main
cd ..
git add BMAD-METHOD
git commit -m "chore: sync BMAD-METHOD"
```

## Best Practices

1. Do not edit upstream module files directly.
2. Keep current BMAD method changes in `src/bmad/modules/custom/`.
3. Record intent, tradeoffs, provenance, and research in `reference/` when those materials should not ship.
4. Re-run build/validate after productized BMAD source changes.
