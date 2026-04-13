# Compass Engine

Central development tooling source for Compass Brand repositories.

## What This Repo Publishes

- `_bmad/` - Compass BMAD runtime layer
- `planning/` - Compass planning framework bundle for deployed repos
- `docs/` - Compass documentation framework bundle for deployed repos
- `.claude/` - Claude Code agents, commands, skills, rules, hooks
- `.codex/` - Codex skills, prompts, safe config template
- `.github/` - Source for distributed `.github/` defaults
- `.opencode/` - OpenCode agents and commands
- `beads` - Beads bootstrap snippets and integration guidance
- `root` - Root-level baseline config files

## Source Of Truth

- `src/` is the active shipped source for Compass Engine bundles.
- `src/bmad/` is the canonical shipped BMAD source.
- `src/planning/` is the canonical shipped planning source.
- `src/documentation/` is the canonical shipped documentation source.
- the published npm package ships `src`-backed assets, not `dist/`.
- `reference/` is retained for framework context, provenance, audits, and research that should not ship.

Do not treat `reference/` as the active runtime implementation tree.

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

Use `npm run push -- --targets bmad,planning,documentation,claude,codex,opencode,github,root` to limit targets.
For selective CI/CD installation, use `--github-features` and `--root-features` with the `github` and `root` targets.

## Linting

This repo now defines a shared linting baseline in `src/root/.pre-commit-config.yaml`
and GitHub workflow linting in `src/github/workflows/lint-core.yml` and `src/github/workflows/lint-languages.yml`.

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
├── _planning/              # Internal planning history and productization records
├── BMAD-METHOD/            # Upstream BMAD submodule
├── docs/                   # Documentation folder
├── planning/               # Live planning control surface for this repo
├── reference/              # Framework, provenance, audit, and research material
├── src/
│   ├── beads/              # Beads source bundle
│   ├── bmad/               # Shipped BMAD source bundle -> downstream _bmad/
│   ├── claude/             # Claude source bundle
│   ├── codex/              # Codex source bundle
│   ├── documentation/      # Shipped documentation source bundle -> downstream docs/
│   ├── github/             # GitHub baseline source bundle
│   ├── opencode/           # OpenCode source bundle
│   │   └── plugins/        # OpenCode plugin development source
│   ├── planning/           # Shipped planning source bundle -> downstream planning/
│   ├── root/               # Universal root components source bundle
│   ├── cli.js              # Shipped CLI entrypoint
│   └── index.js            # Shipped package entrypoint
├── test/                   # Unit and integration tests
└── tools/
    ├── build.js            # Maintainer build script
    ├── check-github-drift.js  # GitHub drift detection
    ├── check-root-drift.js    # Root baseline drift detection
    ├── create-bmad-module.js  # BMAD module scaffolding
    ├── push.js             # Maintainer push script
    ├── update-bmad-method.sh  # Upstream submodule updater
    └── validate.js         # Maintainer validation script
```

## Documentation

- [Installation](docs/getting-started/installation.md)
- [Quickstart](docs/getting-started/quickstart.md)
- [Build Process](docs/architecture/build.md)
- [Sync Architecture](docs/architecture/sync.md)
- [GitHub Standardization](docs/architecture/github-standardization.md)
- [Development Model](docs/development/how-we-work.md)
- [Linting and Security Gates](docs/development/linting-and-security.md)
- [BMAD Overview](docs/development/bmad/bmad-overview.md)
- [Creating BMAD Skills](docs/development/bmad/creating-skills.md)
- [Creating BMAD Modules](docs/development/bmad/creating-modules.md)
- [Custom BMAD Modules](docs/development/bmad/custom-modules.md)
- [Modifying BMAD](docs/development/bmad/modifying-bmad.md)
- [Upstream BMAD Changelog](docs/development/bmad/upstream-changelog.md)
- [BMAD Integration](docs/BMAD-integration.md)
- [OpenCode Plugin Development](docs/development/opencode/plugin-development.md)
- [Modifying Claude](docs/development/claude/modifying-claude.md)
- [Reference Materials](reference/README.md)

## Project Policy Files

- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Changelog](CHANGELOG.md)
- [License](LICENSE)

## License

AGPL-3.0 - Compass Brand © 2026
