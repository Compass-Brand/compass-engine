# Compass Engine

Central development tools for Compass Brand projects.

## Quick Start

```bash
# Build
npm run build

# Push to all projects
npm run push -- --all
```

See [Installation](docs/getting-started/installation.md) for detailed setup.

## Documentation

| I want to... | Read this |
|--------------|-----------|
| Get started | [Installation](docs/getting-started/installation.md) |
| Modify Claude config (commands, skills) | [Modifying Claude](docs/claude/modifying-claude.md) |
| Modify BMAD (workflows, agents) | [Modifying BMAD](docs/bmad/modifying-bmad.md) |
| Understand distribution | [Sync Architecture](docs/architecture/sync.md) |
| Build and push changes | [Build Process](docs/architecture/build.md) |

## What's Included

- **Claude Code Configuration** - agents, commands, skills, rules, hooks
- **BMAD Customizations** - workflows, agents, MCP integration
- **Distribution Tooling** - build and push scripts

## Repository Structure

```
compass-engine/
├── src/                  # Source files (modify these)
│   ├── claude/           # Claude Code configuration
│   ├── bmad/             # BMAD customizations
│   └── scripts/          # Workflow scripts
├── dist/                 # Built output (generated)
│   └── .claude/          # Ready to distribute
├── BMAD-METHOD/          # Upstream submodule (read-only)
├── _bmad-output/         # BMAD runtime artifacts
├── docs/                 # Documentation
└── scripts/              # Build scripts
    ├── build.js          # Compile src/ to dist/
    └── push.js           # Distribute to projects
```

## BMAD Workflows

Available through Claude Code's skill system:

- `/bmad:bmm:workflows:create-prd` - Create a Product Requirements Document
- `/bmad:bmm:workflows:create-architecture` - Design system architecture
- `/bmad:bmm:workflows:sprint-planning` - Plan implementation sprints
- `/bmad:bmm:workflows:dev-story` - Execute story implementation

## License

AGPL-3.0 - Compass Brand © 2026
