# Sync Architecture

How compass-engine distributes configuration to all Compass Brand projects.

## Design Philosophy

**Full replacement, not merge.**

When syncing to a project, we:

1. **Backup** local-only content
2. **Delete** the existing `.claude/` directory
3. **Copy** fresh content from `dist/.claude/`
4. **Restore** local-only content

This ensures bug fixes propagate correctly. If we merged instead, bugs would persist.

## Distribution Flow

```text
compass-engine                    Target Projects
─────────────────                 ────────────────────
src/claude/
    │
    ▼
  build.js
    │
    ▼
dist/.claude/  ──── push.js ────► compass-brand/.claude/
                        │         compass-forge/.claude/
                        │         compass-services/.claude/
                        │         legacy-system-analyzer/.claude/
                        │         ...
                        ▼
              Local content preserved:
              - settings.local.json
              - scratchpad/
              - commands/local/
```

## Distribution Mechanisms

### 1. NPM Push (Primary)

```bash
cd compass-engine
npm run build
npm run push -- --all
```

### 2. Installer Integration

compass-brand-setup automatically:
1. Builds compass-engine
2. Pushes to all projects during setup

### 3. Direct Sync Script

Each project can pull from compass-engine:

```bash
./scripts/sync-from-engine.sh
```

## Local-Only Paths

These paths are **never** overwritten:

| Path | Purpose |
|------|---------|
| `settings.local.json` | Machine-specific settings (API keys, paths) |
| `scratchpad/` | User's temporary workspace |
| `commands/local/` | Project-specific commands |

## Project Discovery

The push script discovers projects by looking for:

1. Directories with `.git` in the workspace
2. Known Compass Brand project paths:
   - compass-brand (root)
   - compass-forge
   - compass-services
   - compass-initiative
   - compass-modules
   - compass-brand-infrastructure
   - compass-brand-setup
   - mcps
   - legacy-system-analyzer
   - competitor-analysis-toolkit

## When to Sync

**Manual sync needed after:**
- Adding/modifying commands
- Adding/modifying agents
- Adding/modifying skills
- Changing rules
- Updating hook scripts

**Automatic sync via:**
- compass-brand-setup install
- Git hooks (if configured)

## Version Tracking

The `package.json` version tracks compass-engine releases:

```json
{
  "version": "0.1.0"
}
```

Bump version for:
- Major: Breaking changes to sync process
- Minor: New features (commands, agents)
- Patch: Bug fixes, documentation

## Conflict Resolution

If a project has customizations that conflict:

1. **Move to local**: Put project-specific files in `commands/local/`
2. **Contribute upstream**: Add to compass-engine if broadly useful
3. **Override in settings**: Use `settings.local.json` for settings

## Rollback

If a sync causes issues:

```bash
# In the affected project
git checkout HEAD -- .claude/
```

Or restore from the backup created during sync.

## Security Considerations

- **No secrets in source**: Never commit API keys to compass-engine
- **Local settings**: Use `settings.local.json` for sensitive config
- **Audit before push**: Review changes before `--all` push
