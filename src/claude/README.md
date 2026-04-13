# Claude Bundle

This directory is the source for distributed `.claude/` content.

Included:

- `agents/`
- `commands/`
- `skills/`
- `rules/`
- `contexts/`
- `config/`
- `scripts/`
- `templates/`

Notes:

- Client skills under `dist/.claude/skills/` are auto-generated at build time from `skill-manifest.csv`.
- `skills/bmad-method/` and `skills/bmad-automation/` are shipped Compass BMAD helper skills.
- Local-only preservation (e.g. `settings.local.json`, `scratchpad/`, `commands/local/`) is handled by the push layer.
