# Installation

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

Build output:
- `dist/.claude/`
- `dist/.codex/`
- `dist/.opencode/`
- `dist/.github/`
- `dist/beads/`

## Push to Repositories

```bash
# all targets, all discovered repos
npm run push -- --all

# one repo, selected targets
npm run push -- --project /path/to/repo --targets claude,codex,opencode
```

## Next Steps

- [Build process](../architecture/build.md)
- [Sync architecture](../architecture/sync.md)
- [Modifying Claude](../claude/modifying-claude.md)
- [Modifying BMAD](../bmad/modifying-bmad.md)