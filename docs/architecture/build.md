# Build Process

Last reviewed: 2026-04-13

How compass-engine compiles source bundles into distributable artifacts.

`dist/` is a local and CI build artifact. The published npm package ships the `src`-backed bundle sources, not `dist/`.

## Build Command

```bash
npm run build
# or
node tools/build.js
```

## Source to Dist Mapping

```text
src/claude/        -> dist/.claude/
src/bmad/          -> dist/_bmad/
src/planning/      -> dist/planning/
src/documentation/ -> dist/docs/
src/codex/         -> dist/.codex/
src/opencode/      -> dist/.opencode/
src/github/        -> dist/.github/
src/beads/         -> dist/beads/
src/root/          -> dist/root/
```

## Build Behavior

1. Cleans `dist/`
2. Builds Claude bundle:
   - Copies `agents/`, `commands/`, `skills/`, `rules/`, `contexts/`, `config/`, `scripts/` from `src/claude/`
   - Generates `settings.json` from `src/claude/templates/settings.json.template`
   - Copies `settings.local.json.example` from templates
   - Copies Claude hook scripts from `src/scripts/claude/hooks/` (if present)
3. Builds BMAD skills:
   - Copies root-level BMAD assets from `src/bmad/` (excluding `modules/`)
   - Merges native + custom skill modules (`bmm`, `core`) from `src/bmad/modules/`
   - Copies custom-only modules (`compass`, `bmad-builder`)
   - Generates `_config/agent-manifest.csv`, `_config/bmad-help.csv`, `_config/skill-manifest.csv`
   - Generates client skill stubs in `dist/.claude/skills/`, `dist/.opencode/skills/`, `dist/.codex/skills/`
4. Copies planning bundle (README, docs, templates, framework overlay)
5. Copies documentation, codex, opencode, github, beads, and root bundles
6. Validates required output paths and minimum skill counts

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
- Documentation target skips `README.md` from source (consumer repos own their `docs/README.md`)
