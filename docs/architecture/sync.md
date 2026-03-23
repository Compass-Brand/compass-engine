# Sync Architecture

Last reviewed: 2026-02-23

How compass-engine distributes tooling to Compass Brand repositories.

Push and sync operate from locally built `dist/` artifacts, but the published npm package ships the `src`-backed bundle sources rather than `dist/`.

## Design

Targets use one of two strategies:

- replacement + local-state restore
- managed merge with manifest-based cleanup for shipped files only

For each target:

1. Backup preserved local paths when the target uses replacement sync
2. Replace or merge the target from `dist/`
3. Remove stale shipped files when the target uses managed sync
4. Restore preserved local paths when applicable

For `root`, sync is merge-based and additionally removes files previously managed by `root` that no longer exist in `dist/root`, tracked in git-local metadata (`.git/compass-engine-root-sync.json`, with `.compass-engine/root-sync-manifest.json` fallback outside git repos).

## Targets

- `claude` -> `.claude`
- `codex` -> `.codex`
- `opencode` -> `.opencode`
- `github` -> `.github`
- `root` -> project root (managed baseline files)

Default push includes all five targets.
For `github` and `root`, you can optionally install only selected CI/CD feature groups instead of the full shipped bundle.

## Push Commands

```bash
# Push all targets to all discovered projects
npm run push -- --all

# Push selected targets only
npm run push -- --targets claude,codex

# Push only selected CI/CD features
npm run push -- --targets github,root --github-features baseline,linting --root-features baseline,javascript,docs

# Push to one project
npm run push -- --project /path/to/repo

# Dry run
npm run push -- --all --dry-run
```

## Preserved Local Paths

- `.claude`: `settings.local.json`, `scratchpad/`, `commands/local/`
- `.codex`: managed sync, so shipped files are updated while local runtime state and unrelated local files remain intact
- `.opencode`: managed sync, so shipped files are updated while local runtime state and unrelated local files remain intact
- `.github`: managed sync, so shipped files are updated while repo-local workflows or metadata outside the selected managed set remain intact
- `root`: none (merge strategy; stale managed files removed via manifest)

## Selective CI/CD Feature Groups

GitHub bundle groups:

- `baseline`: `CODEOWNERS`, `dependabot.yml`, `quality-checks`, `pr-size-labeler`, `stale`, `codeql`
- additional workflow groups: `linting`, `necessist`, `runtime-security`, `submodule-security-monitoring`, `github-drift`
- profile groups: `profile-node`, `profile-python`, `profile-submodule-compass-engine`, `profile-submodule-bmad-method`, `profile-check-bmad-updates`

Root bundle groups:

- `baseline`: `.editorconfig`, `.gitattributes`, `.pre-commit-config.yaml`, `.coderabbit.yaml`
- `javascript`: Biome, ESLint, Prettier configs
- `python`: Ruff, pylint, isort configs
- `docs`: markdown/yaml/codespell configs plus `.lint/`
- `security`: `gitleaks`, `checkov`
- `containers`: `hadolint`, `ansible-lint`
- `terraform`: `tflint`

Use `all` or omit the feature flag entirely to install the full shipped bundle.

## Project Discovery

Push discovers projects in this order:

1. optional config file (`--projects-config <path>`, `COMPASS_PROJECTS_FILE`, or `compass-engine/.compass-projects`)
2. optional `COMPASS_PROJECTS` (path-delimited list)
3. known workspace paths (`.`, `compass-forge`, `compass-services`, `compass-initiative`, `compass-modules`, `compass-brand-infrastructure`, `compass-brand-setup`, `mcps`, `legacy-system-analyzer`, `competitor-analysis-toolkit`)
4. fallback sibling-repo detection under the workspace root by checking immediate child directories for `.git`

For deterministic automation, prefer an explicit projects file over fallback discovery.

## Security Rule

Never commit secrets to source bundles. Keep machine-specific credentials in local files or environment variables.
