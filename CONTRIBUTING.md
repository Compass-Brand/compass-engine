# Contributing

Contributions are welcome for `compass-engine`.

## Prerequisites

- Node.js 18+
- Git
- `bd` (beads) CLI available in your environment

## Workflow

1. Create or pick work with beads:
   - `bd prime`
   - `bd ready`
   - `bd show <id>`
   - `bd create --title="..." --type task --priority 2` when the work is not already tracked
   - `bd update <id> --status in_progress`
2. Implement changes in the active source surface for the work:
   - `reference/BMAD/`, `reference/planning/`, and `reference/documentation/` for the current BMAD/planning/documentation method work
   - `src/`, `tools/`, `docs/`, and `tests/` for already-productized or shipped surfaces
3. Run quality gates:
   - `npm run check`
4. Create follow-up issues in beads for newly discovered blockers or deferred work.
5. Close/update issue status in beads.
6. Before push:
   - `git pull --rebase --autostash`
   - `bd sync`
7. Open a PR to `main`.

## Pull Requests

- Keep PRs focused and small when possible.
- Ensure checks pass.
- Include documentation updates when behavior or workflow changes.
- Link the associated beads issue in the PR description.
