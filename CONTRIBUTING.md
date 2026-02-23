# Contributing

Contributions are welcome for `compass-engine`.

## Prerequisites

- Node.js 18+
- Git
- `bd` (beads) CLI available in your environment

## Workflow

1. Create or pick work with beads:
   - `bd ready`
   - `bd show <id>`
   - `bd update <id> --status in_progress`
2. Implement changes in source locations (`src/`, `scripts/`, `docs/`, `tests/`).
3. Run quality gates:
   - `npm run check`
4. Close/update issue status in beads.
5. Before push:
   - `git pull --rebase --autostash`
   - `bd sync`
6. Open a PR to `main`.

## Pull Requests

- Keep PRs focused and small when possible.
- Ensure checks pass.
- Include documentation updates when behavior or workflow changes.
- Link the associated beads issue in the PR description.
