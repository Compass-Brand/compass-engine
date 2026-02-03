# Installation

Getting started with compass-engine.

## Prerequisites

- Node.js 18+
- Git
- Access to Compass Brand repositories

## As Part of Compass Brand Workspace

If you're setting up the full Compass Brand workspace:

```bash
# Clone the workspace with submodules
git clone --recurse-submodules https://github.com/Compass-Brand/compass-brand.git
cd compass-brand

# compass-engine is at compass-forge/compass-engine/
cd compass-forge/compass-engine
```

## Standalone Clone

For standalone development:

```bash
git clone --recurse-submodules https://github.com/Compass-Brand/compass-engine.git
cd compass-engine
```

## Building

Build the distributable configuration:

```bash
npm run build
```

Output will be in `dist/.claude/`.

## Distributing to Projects

Push to all Compass Brand projects:

```bash
npm run push -- --all
```

Or to a specific project:

```bash
npm run push -- --project /path/to/project
```

## Directory Structure

After installation:

```text
compass-engine/
├── src/                  # Source files (modify these)
│   ├── claude/           # Claude Code configuration
│   ├── bmad/             # BMAD customizations
│   └── scripts/          # Workflow scripts
├── dist/                 # Built output (generated)
│   └── .claude/          # Ready to distribute
├── BMAD-METHOD/          # Upstream submodule
├── _bmad-output/         # BMAD runtime artifacts
├── docs/                 # Documentation
└── scripts/              # Build and push scripts
```

## Verifying Installation

Check the build works:

```bash
npm run build
ls -la dist/.claude/
```

Expected output:
- agents/
- commands/
- skills/
- rules/
- contexts/
- config/
- scripts/
- settings.json

## Next Steps

- [Modifying Claude Code config](../claude/modifying-claude.md)
- [Modifying BMAD](../bmad/modifying-bmad.md)
- [Build process](../architecture/build.md)
- [Sync architecture](../architecture/sync.md)
