# Compass BMAD Runtime

This directory defines the Compass BMAD runtime layer.

In deployed repositories this bundle lives at root `_bmad/`. The editable source for this bundle is maintained in `compass-engine`, not in downstream repos.

## Key Surfaces

- `BMAD-workflow.md` - canonical human-readable Compass BMAD workflow
- `modules/custom/bmm/` - active Compass BMAD custom module layer
- `modules/custom/core/` - active shared Compass core workflow layer
- `tools/automation/` - automation specs, policies, and templates shipped with the method
- `_config/` - shipped BMAD manifests and catalogs

## Read Order

1. `BMAD-workflow.md`
2. `modules/custom/bmm/module-help.csv`
3. `modules/custom/core/module-help.csv`
4. `tools/automation/README.md`
5. `../planning/README.md`

## Boundaries

- Do not treat imported sub-repo content as the active source of truth once it has been normalized into this source bundle.
- When maintaining `compass-engine`, keep the shipped BMAD, planning, and documentation bundles aligned when workflow outputs or artifact paths change.
- Downstream repos should not expect provenance, audits, or research-only material to be part of the deployed surface.
