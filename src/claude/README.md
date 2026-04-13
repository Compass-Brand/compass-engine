# Claude Bundle

This directory is the source for distributed `.claude/` content.

Included:

- `agents/`
- `skills/`
- `templates/`

Notes:

- Client skills under `dist/.claude/skills/` are auto-generated at build time from `skill-manifest.csv`.
- `skills/bmad-method/` and `skills/bmad-automation/` are shipped Compass BMAD helper skills.
- Keep project-local only content out of `src/claude/`; local-only preservation is handled in the push layer.
