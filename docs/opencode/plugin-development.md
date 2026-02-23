# OpenCode Plugin Development

How OpenCode plugin work should be done from `compass-engine`.

## Current State

- `.opencode` command/agent bundles are maintained under `src/opencode/`.
- Strategy and target architecture: `docs/architecture/opencode-plugin-strategy.md`.

## Development Workflow

1. Define plugin requirement as a `bd` issue.
2. Map requirement to BMAD workflow or command capability.
3. Implement/adjust OpenCode command and agent assets in `src/opencode/`.
4. Verify parity with Claude/Codex command behavior where applicable.
5. Run `npm run validate` and `npm run build`.
6. Dry-run distribution with `npm run push -- --dry-run --targets opencode`.

## Plugin Design Rules

- No hardcoded secrets.
- Keep BMAD integration module-aware (`src/bmad/modules`).
- Preserve deterministic artifact and output paths.
- Prefer shared logic/design across Claude/Codex/OpenCode where possible.

## Next Milestones

1. Command registry schema for OpenCode plugin commands.
2. Pilot BMAD command integration (`create-prd`, `dev-story`).
3. Cross-platform parity checks.