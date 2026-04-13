# Modifying Claude Code Configuration

Last reviewed: 2026-04-13

Guide to adding and modifying Claude Code configuration in compass-engine.

## Directory Structure

The build copies any of the following directories from `src/claude/` into `dist/.claude/`:

```text
src/claude/
├── agents/      # Agent definitions (.md files)
├── commands/    # Slash commands (.md files)
├── skills/      # Skill definitions (directories with SKILL.md)
├── rules/       # Governance rules (.md files)
├── contexts/    # Context modes (.json/.md files)
├── config/      # Configuration files
├── scripts/     # Hook scripts
└── templates/   # Settings templates (not copied directly; used for generation)
```

Directories that do not exist are skipped during the build. Currently present:

- `agents/` -- agent definitions
- `skills/` -- shipped Compass BMAD helper skills (`bmad-method/`, `bmad-automation/`)
- `templates/` -- `settings.json.template` and `settings.local.json.example`

Generated client skill stubs:

- At build time, `dist/.claude/skills/` receives auto-generated stubs from `dist/_bmad/_config/skill-manifest.csv`
- These stubs point to the corresponding `_bmad/` skill paths
- The same stubs are generated for `dist/.opencode/skills/` and `dist/.codex/skills/`

## Adding a New Command

1. Create a new `.md` file in `src/claude/commands/` (create the directory if it does not exist):

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

- `settings.json.template` - Base settings (built into `dist/.claude/settings.json`)
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
