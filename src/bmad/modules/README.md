# BMAD Module Development

`src/bmad/modules/` is the dedicated source location for Compass custom BMAD modules.

Rules:
- New modules are created from upstream via `tools/create-bmad-module.js`.
- Each module keeps its own `module.yaml` and `custom-module.json`.
- Do not place runtime artifacts in this directory.

Example:

```bash
npm run create:bmad-module -- --name compass-bmm --from bmm --code cbmm
```
