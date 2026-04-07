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

- `commands/bmad/` is auto-generated at build time from per-module `module-help.csv` files (output: `dist/_bmad/_config/bmad-help.csv`).
- `skills/bmad-method/` and `skills/bmad-automation/` are shipped Compass BMAD helper skills.
- Keep project-local only content out of `src/claude/`; local-only preservation is handled in the push layer.
