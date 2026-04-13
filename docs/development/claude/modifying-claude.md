# Modifying Claude Code Configuration

Last reviewed: 2026-02-23

Guide to adding and modifying Claude Code configuration in compass-engine.

## Directory Structure

```text
src/claude/
├── agents/      # Agent definitions (.md files)
├── skills/      # Skill definitions (directories with SKILL.md)
└── templates/   # Settings templates
```

Generated BMAD adapters:

- Client skills under `dist/.claude/skills/` are auto-generated at build time from `skill-manifest.csv`
- run `npm run build` to regenerate BMAD skill adapters

## Adding a New Command

BMAD commands are auto-generated at build time from `skill-manifest.csv`. To add a new BMAD command, add an entry to the manifest and run `npm run build`.

For non-BMAD commands, create a skill directory under `src/claude/skills/` (see Adding a New Skill below).

## Adding a New Agent

1. Create a new `.md` file in `src/claude/agents/`:

```markdown
---
name: my-agent
description: What this agent specializes in
tools: ['Read', 'Grep', 'Glob'] # Tools this agent can use
model: sonnet # Optional: sonnet, opus, haiku
---

# My Agent

System prompt for this specialized agent.

## Capabilities

- What this agent is good at
- Specific use cases

## Guidelines

1. How the agent should behave
2. What it should/shouldn't do
```

## Adding a New Skill

1. Create a directory in `src/claude/skills/`:

```text
src/claude/skills/my-skill/
├── SKILL.md      # Main skill definition
└── examples/     # Optional examples
```

2. Create `SKILL.md`:

```markdown
---
name: my-skill
description: What this skill provides
---

# My Skill

## When to Use

Describe scenarios where this skill should be invoked.

## Instructions

Step-by-step instructions for the skill.
```

## Adding Rules

Rules are managed in the project-level `.claude/rules/` directory, not in the `src/claude/` source bundle. Each target repo maintains its own rules. See the parent repo `.claude/rules/` for examples.

## Configuration Files

### `src/claude/templates/`

Settings templates:

- `settings.json.template` - Base settings
- `settings.local.json.example` - Example local settings

## After Making Changes

1. **Build**: `npm run build`
2. **Test locally**: Copy `dist/.claude/` to a test project
3. **Distribute**: `npm run push -- --all`

## Best Practices

- **Descriptive names**: Use clear, descriptive names for commands and agents
- **Documentation**: Include usage examples in command/skill descriptions
- **Testing**: Test changes locally before pushing to all projects
- **Versioning**: Update version in `package.json` for significant changes
