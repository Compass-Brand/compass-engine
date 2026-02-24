# Build Process

Last reviewed: 2026-02-23

How compass-engine compiles source bundles into distributable artifacts.

## Build Command

```bash
npm run build
# or
node tools/build.js
```

## Source to Dist Mapping

```text
src/claude/    -> dist/.claude/
src/codex/     -> dist/.codex/
src/opencode/  -> dist/.opencode/
src/github/    -> dist/.github/
src/beads/     -> dist/beads/
```

## Build Behavior

1. Cleans `dist/`
2. Builds Claude bundle with template generation and hook copy
3. Copies Codex, OpenCode, GitHub, and beads bundles
4. Validates required output paths

## Validation Command

```bash
npm run validate
```

Validation checks:

- required source/bundle paths exist
- `src/codex/config.toml` does not include hardcoded secret-like values

## Notes

- Claude local-only paths are excluded from source copy (`settings.local.json`, `scratchpad/`, `commands/local/`)
- Codex config in source is a safe template; repos should inject local secrets via environment variables
