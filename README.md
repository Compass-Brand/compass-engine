# Compass Engine

Central development tooling source for Compass Brand repositories.

## What This Repo Publishes

- `beads` - Agent files appendages to ensure beads usage
- `_bmad/` - Customization layer that sits on top of `BMAD-METHOD/`
- `.claude/` - Claude Code agents, commands, skills, rules, hooks
- `.codex/` - Codex skills, prompts, safe config template
- `.github/` - Source for distributed `.github/` defaults.
- `.opencode/` - OpenCode agents and commands
- `_planning/` - Compass Brand planning folder structure
- `root` - Root level config files

## Quick Start

First-time setup:

```bash
gh repo clone Compass-Brand/compass-engine
```

```bash
bd onboard
```

```bash
npm run check
npm run push -- --all
```

Prerequisites: Node.js 18+, Git, and `bd` (see [Installation](docs/getting-started/installation.md)).

Use `npm run push -- --targets claude,codex,opencode,github,root` to limit targets.

## Linting

This repo now defines a shared linting baseline in `src/root/.pre-commit-config.yaml`
and GitHub workflow linting in `src/github/workflows/linting.yml`.

Install and run locally:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Heavy hooks are configured as manual stages and can be invoked on demand:

```bash
pre-commit run --hook-stage manual pylint
pre-commit run --hook-stage manual checkov
```

Project outputs receive the same baseline through:

- `src/root/` -> project root files (`.pre-commit-config.yaml`, lint configs)
- `src/github/workflows/` -> project CI workflows (PR lint/security checks)

Deep analysis jobs run outside the PR fast path:

- `src/github/workflows/necessist.yml` -> manual and weekly `necessist` runs
- `src/github/workflows/runtime-security.yml` -> cluster/runtime security checks (manual)

## CodeQL

CodeQL is shipped in the GitHub baseline workflow:

- `src/github/workflows/codeql.yml` (source)
- `.github/workflows/codeql.yml` (applied in this repository)

To get CodeQL fully active in any target repository:

1. Apply the GitHub baseline workflow files.
2. Enable GitHub Code Scanning in repository settings.
3. For private/internal repos, enable GitHub Advanced Security.

Operational details and troubleshooting are documented in:

- [Linting and Security Gates](docs/development/linting-and-security.md#codeql-setup-and-troubleshooting)

## Repository Structure

```text
compass-engine/
├── .beads/                 # Beads tracking folder
├── .claude/                # Claude-code folder
├── .codex/                 # Codex CLI folder
├── .github/                # Github components folder
├── .opencode/              # Opencode folder
├── _bmad/                  # BMAD components
├── _planning/              # Planning folder
├── BMAD-METHOD/            # Upstream BMAD submodule
├── dist/                   # Generated distributable bundles
├── docs/                   # Documentation folder
├── reference/              # Misc. references
├── src/
│   ├── beads/              # Beads source bundle
│   ├── bmad/               # BMAD source bundle
│   │   └── modules/        # BMAD custom module development source
│   ├── claude/             # Claude source bundle
│   ├── codex/              # Codex source bundle
│   ├── github/             # GitHub baseline source bundle
│   ├── opencode/           # OpenCode source bundle
│   │   └── plugins/        # OpenCode plugin development source
│   ├── planning/           # Compass planning source bundle
│   ├── root/               # Universal root components source bundle.
│   └── scripts/
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
- [Linting and Security Gates](docs/development/linting-and-security.md)
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
