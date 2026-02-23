# Sync Architecture

How compass-engine distributes tooling to Compass Brand repositories.

## Design

Each selected target is synced with replacement + local-state restore.

For each target:
1. Backup local-only paths
2. Remove destination directory
3. Copy fresh content from `dist/`
4. Restore preserved local paths

## Targets

- `claude` -> `.claude`
- `codex` -> `.codex`
- `opencode` -> `.opencode`
- `github` -> `.github`

Default push includes all four targets.

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

## Project Discovery

Push discovers projects by:
1. optional `COMPASS_PROJECTS`
2. known workspace paths
3. Git repo detection (`.git`)

## Security Rule

Never commit secrets to source bundles. Keep machine-specific credentials in local files or environment variables.