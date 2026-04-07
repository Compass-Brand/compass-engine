# OpenCode Bundle

This directory is the source for distributed `.opencode/` content.

Included:

- `agents/`
- `commands/`
- `plugins/` (Compass plugin source)

Notes:

- `commands/bmad/` is auto-generated at build time from per-module `module-help.csv` files (output: `dist/_bmad/_config/bmad-help.csv`).
- `agents/` contains OpenCode-facing wrappers for Compass BMAD orchestration behavior.
