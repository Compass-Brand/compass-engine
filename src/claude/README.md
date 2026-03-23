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

- `commands/bmad/` is generated from `src/bmad/_config/bmad-help.csv` by `npm run sync:client-bundles`.
- `skills/bmad-method/` and `skills/bmad-automation/` are shipped Compass BMAD helper skills.
- Keep project-local only content out of `src/claude/`; local-only preservation is handled in the push layer.
