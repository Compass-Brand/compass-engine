# Development Model

Last reviewed: 2026-02-23

This document defines how work is done in `compass-engine`.

## Scope

`compass-engine` is the source repository for shared engineering tooling distributed to Compass Brand repositories.

Primary outputs:
- `.claude`
- `.codex`
- `.opencode`
- `.github`
- beads bootstrap snippets

## Source of Truth

1. Issue tracking: `bd` (beads)
2. Distributed assets: `src/`
3. Build artifacts: `dist/`
4. Upstream BMAD: `BMAD-METHOD/` (read-only for normal development)

## Day-to-Day Workflow

1. `bd ready`
2. `bd show <id>`
3. `bd update <id> --status in_progress`
4. Implement changes in `src/`, `tools/`, and `docs/`
5. Run quality gates:
   - `npm run check`
6. Update/close issue in `bd`
7. Session close protocol:
   - `git pull --rebase --autostash`
   - `bd sync`
   - commit
   - push branch / PR (main is protected)

## Directory Intent

- `src/`: canonical source bundles and templates
- `src/bmad/modules/`: canonical BMAD custom module development location
- `src/opencode/plugins/`: canonical OpenCode plugin development location
- `tools/`: build, push, validation, and scaffolding automation
- `tests/`: test location (currently no runtime suite; gate uses `npm run check`)
- `reference/`: current reference notes only; no legacy archives
- `src/planning-templates/`: planning template source for downstream repos

See also:
- `tests/README.md`
- `tools/README.md`
- `reference/README.md`
- `src/planning-templates/README.md`
