# Modifying BMAD Customizations

Guide to customizing BMAD workflows and agents in compass-engine.

## BMAD Overview

BMAD (Breakthrough Method of Agile AI-Driven Development) is the core methodology. This repository contains:

1. **BMAD-METHOD/** - Upstream submodule (do not modify directly)
2. **src/bmad/** - Our customizations and integrations
3. **_bmad-output/** - Runtime output and artifacts

## Directory Structure

```
src/bmad/
├── workflows/     # Custom or modified workflows
├── agents/        # Custom BMAD agents
├── patches/       # Patches to upstream BMAD-METHOD
└── integration/   # MCP integration configs
```

## Custom Workflows

To create a custom workflow:

1. Create a directory in `src/bmad/workflows/`:

```
src/bmad/workflows/my-workflow/
├── workflow.md          # Main workflow definition
├── steps/               # Step files
│   ├── step-01-init.md
│   ├── step-02-analyze.md
│   └── step-03-complete.md
└── templates/           # Output templates
```

2. Define the workflow in `workflow.md`:

```markdown
---
name: my-workflow
module: bmm
description: What this workflow does
---

# My Workflow

## Purpose

What this workflow accomplishes.

## Steps

1. **Init** - step-01-init.md
2. **Analyze** - step-02-analyze.md
3. **Complete** - step-03-complete.md

## Usage

`/bmad:bmm:workflows:my-workflow`
```

## Custom Agents

To add a custom BMAD agent:

1. Create in `src/bmad/agents/`:

```markdown
---
name: CustomAgent
role: Role description
module: bmm
---

# CustomAgent

## Persona

Describe the agent's personality and approach.

## Responsibilities

- What this agent does
- Areas of expertise

## Guidelines

- How the agent should behave
```

## Patching Upstream BMAD

When upstream BMAD needs modification:

1. Create a patch file in `src/bmad/patches/`:

```diff
--- a/workflows/create-prd/step-01.md
+++ b/workflows/create-prd/step-01.md
@@ -10,6 +10,8 @@
 Original content
+
+Our customization
```

2. Document why the patch is needed

## MCP Integration

Integration configs in `src/bmad/integration/`:

- `forgetful-integration.md` - How BMAD uses Forgetful memory
- `serena-integration.md` - How BMAD uses Serena for code analysis

## Syncing Upstream BMAD

To update from upstream BMAD-METHOD:

```bash
# Use the sync command
/sync-bmad-method

# Or manually:
cd BMAD-METHOD
git pull origin main
cd ..
git add BMAD-METHOD
git commit -m "chore: sync BMAD-METHOD from upstream"
```

## Best Practices

1. **Don't modify BMAD-METHOD directly** - Use patches or custom workflows
2. **Document changes** - Always explain why customizations exist
3. **Test workflows** - Run through workflows before distributing
4. **Version tracking** - Note which BMAD-METHOD version customizations are based on

## Runtime Output

The `_bmad-output/` directory contains:

- `bmb-creations/` - Custom modules created with BMB (BMAD Builder)
- `planning-artifacts/` - Product briefs, PRDs
- `implementation-artifacts/` - Sprint status, reviews

These are runtime artifacts and should not be distributed to other projects.
