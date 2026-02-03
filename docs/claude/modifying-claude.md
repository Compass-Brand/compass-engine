# Modifying Claude Code Configuration

Guide to adding and modifying Claude Code configuration in compass-engine.

## Directory Structure

```text
src/claude/
├── agents/      # Agent definitions (.md files)
├── commands/    # Slash commands (.md files)
│   └── bmad/    # BMAD-specific commands
├── skills/      # Skill definitions (directories with SKILL.md)
├── rules/       # Governance rules (.md files)
├── contexts/    # Context modes (.json/.md files)
├── config/      # Configuration files
├── scripts/     # Hook scripts
└── templates/   # Settings templates
```

## Adding a New Command

1. Create a new `.md` file in `src/claude/commands/`:

```markdown
---
name: my-command
description: Brief description of what this command does
---

# My Command

Detailed instructions for Claude Code when this command is invoked.

## Steps

1. First step
2. Second step
...
```

2. Build and test:

```bash
npm run build
# Test locally by copying dist/.claude to a test project
```

## Adding a New Agent

1. Create a new `.md` file in `src/claude/agents/`:

```markdown
---
name: my-agent
description: What this agent specializes in
tools: ["Read", "Grep", "Glob"]  # Tools this agent can use
model: sonnet  # Optional: sonnet, opus, haiku
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

1. Create or edit files in `src/claude/rules/`:

```markdown
# Rule Category Name

## Rule 1: Description

- Guideline 1
- Guideline 2

## Rule 2: Description

...
```

## Configuration Files

### `src/claude/config/`

Place configuration files here:
- `auto-fix-rules.json` - Auto-fix patterns for PR reviews
- `context-modes.json` - Context mode definitions

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
