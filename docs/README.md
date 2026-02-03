# Compass Engine Documentation

Central documentation hub for compass-engine.

## Quick Links

| I want to... | Read this |
|--------------|-----------|
| Get started | [Getting Started](./getting-started/installation.md) |
| Modify Claude Code config | [Modifying Claude](./claude/modifying-claude.md) |
| Modify BMAD workflows | [Modifying BMAD](./bmad/modifying-bmad.md) |
| Understand distribution | [Sync Architecture](./architecture/sync.md) |
| Build and push changes | [Build Process](./architecture/build.md) |

## Documentation Structure

```text
docs/
├── getting-started/     # Installation and first steps
│   └── installation.md
├── claude/              # Claude Code configuration
│   └── modifying-claude.md
├── bmad/                # BMAD customizations
│   └── modifying-bmad.md
├── architecture/        # System architecture
│   ├── build.md
│   └── sync.md
└── reference/           # API and reference docs
```

## What is Compass Engine?

Compass Engine is the central development tools repository for all Compass Brand projects. It contains:

1. **Claude Code Configuration** - agents, commands, skills, rules, hooks
2. **BMAD Customizations** - modified workflows, custom agents
3. **Distribution Tooling** - build and push mechanisms

All Compass Brand projects receive their `.claude/` configuration from this repository.
