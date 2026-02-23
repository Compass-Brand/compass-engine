# Tool Inventory

Operational tooling scripts for `compass-engine`.

## Active Tools

- `tools/build.js`
  - Builds all distributable bundles from `src/` to `dist/`.
- `tools/push.js`
  - Syncs selected targets from `dist/` into destination repositories.
- `tools/validate.js`
  - Validates required source layout and checks for obvious secret leaks.
- `tools/create-bmad-module.js`
  - Scaffolds a custom BMAD module into `src/bmad/modules/` from upstream.

## Utility Tools

- `tools/update-bmad-method.sh`
  - Submodule helper for updating `BMAD-METHOD/` from upstream.

## Usage

```bash
npm run check
npm run push -- --all
npm run create:bmad-module -- --name compass-bmm --from bmm --code cbmm
```
