# Modifying BMAD Customizations

Last reviewed: 2026-02-23

Guide to extending BMAD in `compass-engine` without forking upstream internals.

## Source of Truth

- Upstream: `BMAD-METHOD/` (read-only in normal workflow)
- Custom layer: `src/bmad/`
- Module development root: `src/bmad/modules/`

## Custom Module Workflow

Create a custom module derived from upstream:

```bash
node tools/create-bmad-module.js --name compass-bmm --from bmm --code cbmm
```

Output is created in:
- `src/bmad/modules/compass-bmm/`
- `src/bmad/modules/compass-bmm/module.yaml` (code/name rewritten)
- `src/bmad/modules/compass-bmm/custom-module.json` (provenance metadata)

## Why This Pattern

- Keeps upstream updates easy (`BMAD-METHOD` can be synced independently)
- Preserves a clear change boundary for Compass-specific planning behavior
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
2. Keep each customization in a module-specific folder under `src/bmad/modules/`.
3. Record intent and tradeoffs in module-level notes or metadata.
4. Re-run build/validate after customization changes.
