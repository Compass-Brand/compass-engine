# OpenCode Plugin Development

How OpenCode plugin work should be done from `compass-engine`.

## Current State

- `.opencode` command/agent bundles are maintained under `src/opencode/`.
- Plugin implementation source lives in `src/opencode/plugins/`.
- Strategy and target architecture: `docs/architecture/opencode-plugin-strategy.md`.

## Development Workflow

1. Define plugin requirement as a `bd` issue.
2. Map requirement to BMAD workflow or command capability.
3. Implement plugin code/metadata in `src/opencode/plugins/`.
4. Implement/adjust OpenCode command and agent assets in `src/opencode/` as wrappers/adapters.
5. Verify parity with Claude/Codex command behavior where applicable.
6. Run `npm run validate` and `npm run build`.
7. Dry-run distribution with `npm run push -- --dry-run --targets opencode`.

## Plugin Design Rules

- No hardcoded secrets.
- Keep BMAD integration module-aware (`src/bmad/modules`).
- Preserve deterministic artifact and output paths.
- Prefer shared logic/design across Claude/Codex/OpenCode where possible.

## Next Milestones

1. Command registry schema for OpenCode plugin commands.
2. Pilot BMAD command integration (`create-prd`, `dev-story`).
3. Cross-platform parity checks.
