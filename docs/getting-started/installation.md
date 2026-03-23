# Installation

Last reviewed: 2026-02-23

Getting started with compass-engine.

## Prerequisites

- Node.js 18+
- Git
- Access to Compass Brand repositories

## Clone

```bash
git clone --recurse-submodules https://github.com/Compass-Brand/compass-engine.git
cd compass-engine
```

## Validate + Build

```bash
npm run validate
npm run build
```

`npm run build` generates local/CI artifacts in `dist/`. The published npm package ships the `src`-backed bundles, not `dist/`.

Build output:

- `dist/_bmad/`
- `dist/planning/`
- `dist/docs/`
- `dist/.claude/`
- `dist/.codex/`
- `dist/.opencode/`
- `dist/.github/`
- `dist/beads/`
- `dist/root/`

## Push to Repositories

```bash
# all targets, all discovered repos
npm run push -- --all

# one repo, selected targets
npm run push -- --project /path/to/repo --targets claude,codex,opencode

# one repo, selected CI/CD features only
npm run push -- --project /path/to/repo --targets github,root --github-features baseline,linting --root-features baseline,javascript,docs
```

Selective CI/CD install groups:

- `--github-features`: `all`, `baseline`, `codeowners`, `dependabot`, `quality-checks`, `linting`, `codeql`, `pr-size-labeler`, `stale`, `necessist`, `runtime-security`, `submodule-security-monitoring`, `github-drift`, `profile-node`, `profile-python`, `profile-submodule-compass-engine`, `profile-submodule-bmad-method`, `profile-check-bmad-updates`
- `--root-features`: `all`, `baseline`, `javascript`, `python`, `docs`, `security`, `containers`, `terraform`

## Next Steps

- [Build process](../architecture/build.md)
- [Sync architecture](../architecture/sync.md)
- [Modifying Claude](../development/claude/modifying-claude.md)
- [Modifying BMAD](../development/bmad/modifying-bmad.md)
