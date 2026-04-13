# Development Model

Last reviewed: 2026-04-13

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

1. Issue tracking: `bd` (beads) -- a local-first issue tracker bundled with compass-engine; run `bd help` for usage
2. Shipped distributed assets: `src/`
3. Framework, provenance, and research context: `reference/`
4. Build artifacts: `dist/`
5. Upstream BMAD: `BMAD-METHOD/` (read-only for normal development)

## Day-to-Day Workflow

1. `bd prime`
2. `bd ready`
3. `bd show <id>`
4. Create the issue first with `bd create ...` if the work is not already tracked.
5. `bd update <id> --status in_progress`
6. Implement changes in the correct surface for the work:
   - `src/` for shipped BMAD, planning, documentation, and tooling surfaces
   - `tools/` for maintainer build/push/validation automation
   - `reference/` only for framework context, provenance, audits, and research that should not ship
7. Run quality gates:
   - `npm run check`
8. Record newly discovered follow-up work in `bd`, not only in markdown notes.
9. Update/close issue in `bd`
10. Session close protocol:
   - `git pull --rebase --autostash`
   - `bd sync`
   - commit
   - push branch / PR (main is protected)

## Directory Intent

- `src/`: active shipped source bundles and templates
- `src/bmad/`: shipped BMAD source that becomes downstream `_bmad/`
- `src/planning/`: shipped planning source that becomes downstream `planning/`
- `src/documentation/`: shipped documentation source that becomes downstream `docs/`
- `src/opencode/plugins/`: canonical OpenCode plugin development location
- `tools/`: maintainer build, push, validation, and scaffolding automation
- `reference/`: framework references, provenance, audits, and research that stay out of shipped bundles
- Tests: `test/` contains runtime unit/integration suites

See also:

- `tools/README.md`
- `reference/README.md`
