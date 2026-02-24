# Custom BMAD Modules

Last reviewed: 2026-02-23

How to create and maintain Compass-specific BMAD modules.

## Principles

- Upstream module source lives in `BMAD-METHOD/`.
- Compass custom modules live in `src/bmad/modules/`.
- Do not directly edit upstream module files for Compass-specific behavior.

## Create a Module

```bash
npm run create:bmad-module -- --name compass-bmm --from bmm --code cbmm
```

Generated output:

- `src/bmad/modules/compass-bmm/`
- `src/bmad/modules/compass-bmm/module.yaml`
- `src/bmad/modules/compass-bmm/custom-module.json`

## Customize

1. Edit workflows/agents/templates in the generated module folder.
2. Document major decisions in module-level notes.
3. Keep naming/versioning stable so downstream automation can target the module.

## Update Workflow

When upstream BMAD changes:

1. Update `BMAD-METHOD/`.
2. Review diffs against custom modules.
3. Reconcile custom module behavior explicitly.
4. Run validate/build gates.
