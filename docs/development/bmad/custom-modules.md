# Custom BMAD Modules

Last reviewed: 2026-04-08

Principles for maintaining Compass-specific BMAD modules. For step-by-step creation instructions, see [Creating Modules](./creating-modules.md).

## Principles

- Upstream module source lives in `BMAD-METHOD/`.
- Current Compass BMAD custom module source lives in `src/bmad/modules/custom/`.
- `reference/BMAD/` is retained for workflow/provenance context, not as the active runtime module tree.
- Do not directly edit upstream module files for Compass-specific behavior.

## Current Active Modules

| Module | Location | Type |
| --- | --- | --- |
| BMM (custom layer) | `src/bmad/modules/custom/bmm-skills/` | Overlays native |
| Core (custom layer) | `src/bmad/modules/custom/core-skills/` | Overlays native |
| Compass Skills | `src/bmad/modules/custom/compass-skills/` | Custom-only |
| BMad Builder | `src/bmad/modules/custom/bmad-builder-skills/` | Custom-only |

## Current Working Model

1. Shape BMAD workflows, agents, automation specs, and catalogs in `src/bmad/`.
2. Keep planning destinations aligned in `src/planning/`.
3. Use `reference/` only for supporting framework notes, provenance, and research that should not ship.

## Customize

1. Edit workflows, agents, templates, and catalogs in `src/bmad/modules/custom/`.
2. Document major decisions in module-level notes.
3. Keep naming/versioning stable so downstream automation can target the module.

## Update Workflow

When upstream BMAD changes:

1. Update `BMAD-METHOD/` submodule.
2. Review diffs against custom modules.
3. Reconcile custom module behavior explicitly.
4. Run `npm run validate && npm run build`.
