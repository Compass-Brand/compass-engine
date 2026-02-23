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
npm run check
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
│   │   └── plugins/       # OpenCode plugin development source
│   ├── bmad/
│   │   └── modules/       # BMAD custom module development source
│   ├── github/            # GitHub baseline source bundle
│   ├── beads/             # Beads bootstrap snippets
│   ├── planning-templates/
│   └── scripts/
├── dist/                  # Generated distributable bundles
├── BMAD-METHOD/           # Upstream BMAD submodule
├── docs/
└── tools/
    ├── build.js
    ├── push.js
    └── validate.js
```

## Documentation

- [Installation](docs/getting-started/installation.md)
- [Quickstart](docs/getting-started/quickstart.md)
- [Build Process](docs/architecture/build.md)
- [Sync Architecture](docs/architecture/sync.md)
- [GitHub Standardization](docs/architecture/github-standardization.md)
- [Development Model](docs/development/how-we-work.md)
- [Custom BMAD Modules](docs/development/bmad/custom-modules.md)
- [OpenCode Plugin Development](docs/development/opencode/plugin-development.md)
- [Modifying Claude](docs/development/claude/modifying-claude.md)
- [Modifying BMAD](docs/development/bmad/modifying-bmad.md)

## Project Policy Files

- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Changelog](CHANGELOG.md)
- [License](LICENSE)

## License

AGPL-3.0 - Compass Brand © 2026
