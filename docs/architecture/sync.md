# Sync Architecture

Last reviewed: 2026-02-23

How compass-engine distributes tooling to Compass Brand repositories.

## Design

Each selected target is synced with replacement + local-state restore.

For each target:

1. Backup local-only paths
2. Remove destination directory (or merge for `root`)
3. Copy fresh content from `dist/`
4. Restore preserved local paths

For `root`, sync is merge-based and additionally removes files previously managed by `root` that no longer exist in `dist/root`, tracked in git-local metadata (`.git/compass-engine-root-sync.json`, with `.compass-engine/root-sync-manifest.json` fallback outside git repos).

## Targets

- `claude` -> `.claude`
- `codex` -> `.codex`
- `opencode` -> `.opencode`
- `github` -> `.github`
- `root` -> project root (managed baseline files)

Default push includes all five targets.

## Push Commands

```bash
# Push all targets to all discovered projects
npm run push -- --all

# Push selected targets only
npm run push -- --targets claude,codex

# Push to one project
npm run push -- --project /path/to/repo

# Dry run
npm run push -- --all --dry-run
```

## Preserved Local Paths

- `.claude`: `settings.local.json`, `scratchpad/`, `commands/local/`
- `.codex`: `auth.json`, `history.jsonl`, `models_cache.json`, `sessions/`, `tmp/`, `version.json`
- `.opencode`: `state/`, `cache/`
- `.github`: none
- `root`: none (merge strategy; stale managed files removed via manifest)

## Project Discovery

Push discovers projects by:

1. optional config file (`--projects-config <path>`, `COMPASS_PROJECTS_FILE`, or `compass-engine/.compass-projects`)
2. optional `COMPASS_PROJECTS` (path-delimited list)
3. known workspace paths (`.`, `compass-forge`, `compass-services`, `compass-initiative`, `compass-modules`, `compass-brand-infrastructure`, `compass-brand-setup`, `mcps`, `legacy-system-analyzer`, `competitor-analysis-toolkit`)
4. Git repo detection (`.git`)

## Security Rule

Never commit secrets to source bundles. Keep machine-specific credentials in local files or environment variables.
