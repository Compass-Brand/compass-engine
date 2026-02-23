# Compass Engine

Central development tooling source for Compass Brand repositories.

## What This Repo Publishes

- `.claude/` - Claude Code agents, commands, skills, rules, hooks
- `.codex/` - Codex skills, prompts, safe config template
- `.opencode/` - OpenCode agents and commands
- `.github/` - default workflows and automation baseline
- `beads` bootstrap snippets - issue tracking conventions for `AGENTS.md` and Copilot instructions

## Quick Start

```bash
npm run validate
npm run build
npm run push -- --all
```

Use `npm run push -- --targets claude,codex,opencode,github` to limit targets.

## Repository Structure

```text
compass-engine/
├── src/
│   ├── claude/            # Claude source bundle
│   ├── codex/             # Codex source bundle
│   ├── opencode/          # OpenCode source bundle
│   ├── github/            # GitHub baseline source bundle
│   ├── beads/             # Beads bootstrap snippets
│   ├── planning-templates/
│   └── scripts/
├── dist/                  # Generated distributable bundles
├── BMAD-METHOD/           # Upstream BMAD submodule
├── _bmad-output/          # BMAD runtime artifacts
├── docs/
└── scripts/
    ├── build.js
    ├── push.js
    └── validate.js
```

## Documentation

- [Installation](docs/getting-started/installation.md)
- [Build Process](docs/architecture/build.md)
- [Sync Architecture](docs/architecture/sync.md)
- [Development Model](docs/development/how-we-work.md)
- [Custom BMAD Modules](docs/bmad/custom-modules.md)
- [OpenCode Plugin Development](docs/opencode/plugin-development.md)
- [Modifying Claude](docs/claude/modifying-claude.md)
- [Modifying BMAD](docs/bmad/modifying-bmad.md)

## License

AGPL-3.0 - Compass Brand © 2026
