# Tool Inventory

Operational tooling scripts for `compass-engine`.

## Active Tools

- `tools/build.js`
  - Maintainer-facing build script that turns `src/` into `dist/`.
- `tools/push.js`
  - Maintainer-facing push script that syncs selected targets from `dist/` into destination repositories.
- `tools/validate.js`
  - Maintainer-facing validation script for source layout and secret hygiene.
- `tools/create-bmad-module.js`
  - Scaffolds a custom BMAD module into `src/bmad/modules/` from upstream.
- `tools/check-github-drift.js`
  - Detects drift between `src/github/` and `.github/`.
- `tools/check-root-drift.js`
  - Detects drift between `src/root/` and repository root baseline files.

## Utility Tools

- `tools/update-bmad-method.sh`
  - Submodule helper for updating `BMAD-METHOD/` from upstream.

## Usage

```bash
npm run check
npm run push -- --all
npm run create:bmad-module -- --name compass-bmm --from bmm --code cbmm
```

For a shipped CLI entrypoint, use `compass-engine <command>`. The package runtime entrypoint lives in `src/cli.js`; root `tools/` remains the maintainer-script surface for this repository.
