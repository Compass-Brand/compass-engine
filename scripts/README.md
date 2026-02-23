# Script Inventory

Operational scripts for `compass-engine`.

## Active Scripts

- `scripts/build.js`
  - Builds all distributable bundles from `src/` to `dist/`.
- `scripts/push.js`
  - Syncs selected targets from `dist/` into destination repositories.
- `scripts/validate.js`
  - Validates required source layout and checks for obvious secret leaks.
- `scripts/create-bmad-module.js`
  - Scaffolds a custom BMAD module into `src/bmad/modules/` from upstream.

## Utility Scripts

- `scripts/update-bmad-method.sh`
  - Submodule helper for updating `BMAD-METHOD/` from upstream.

## Usage

```bash
npm run validate
npm run build
npm run push -- --all
npm run create:bmad-module -- --name compass-bmm --from bmm --code cbmm
```