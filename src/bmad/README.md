# BMAD Customization Layer

`src/bmad/` is the customization layer that sits on top of `BMAD-METHOD/` (upstream).

Principles:
- never edit `BMAD-METHOD/` directly
- create custom modules in `src/bmad/modules/`
- document custom decisions close to modified module content

## Create a Custom Module

```bash
node scripts/create-bmad-module.js --name compass-bmm --from bmm --code cbmm
```

This copies the upstream module into `src/bmad/modules/<name>/`, updates `module.yaml`, and writes `custom-module.json` metadata.