# Creating BMAD Skills

Last reviewed: 2026-04-08

How to create new workflow and agent skills for the Compass BMAD system.

## Prerequisites

- Working compass-engine checkout with `npm install` completed
- Familiarity with the [BMAD overview](./bmad-overview.md)

## Skill Types

| Type | Purpose | Entrypoint |
| --- | --- | --- |
| Workflow | Multi-step process with sequential execution | `SKILL.md` → `workflow.md` → `steps/` |
| Agent | AI persona with defined identity and capabilities | `SKILL.md` with inline persona |

## Using the Builder Agents

BMAD includes three meta-skill agents for creating components:

| Agent | Code | Persona | Purpose |
| --- | --- | --- | --- |
| Module Builder | `/bmad-builder-module-builder` | Morgan | Create complete BMAD modules |
| Workflow Builder | `/bmad-builder-workflow-builder` | Wendy | Create and validate workflows |
| Agent Builder | `/bmad-builder-agent-builder` | Bond | Create and validate agents |

These agents guide you through creation interactively. The manual process below is for understanding the structure or making targeted edits.

## Creating a Workflow Skill

### 1. Choose a Location

Skills are organized by phase inside a module:

```text
src/bmad/modules/custom/{module-name}/{phase}/{skill-name}/
```

Phases: `0-governance`, `1-analysis`, `2-plan-workflows`, `3-solutioning`, `4-implementation`, `anytime`

### 2. Create SKILL.md

Every skill needs a `SKILL.md` with YAML frontmatter:

```markdown
---
name: bmad-{skill-name}
description: '{One-line user-facing description}'
---

Follow the instructions in ./workflow.md.
```

The `name` field must be globally unique across all modules. Convention: prefix with `bmad-` followed by a descriptive kebab-case name.

### 3. Create workflow.md

The workflow file defines the initialization steps and references step files:

```markdown
# {Skill Display Name}

## Initialization

1. {Setup instructions for the agent executing this workflow}
2. Load context from {relevant files}

## Steps

Execute each step file in order:

1. [Step 1: {name}](./steps/step-01-{name}.md)
2. [Step 2: {name}](./steps/step-02-{name}.md)
3. [Step 3: {name}](./steps/step-03-{name}.md)

## Completion

{What to do when all steps are done}
```

### 4. Create Step Files

Each step file in `steps/` is a self-contained instruction set:

```markdown
# Step {N}: {Step Name}

## Context

{What this step needs from previous steps}

## Instructions

{Detailed instructions for the agent}

## Outputs

{What this step produces}

## Next

Proceed to [Step {N+1}](./step-{N+1}-{name}.md).
```

### 5. Add Supporting Templates (Optional)

If the workflow produces structured documents, add template files:

```text
skill-name/
├── SKILL.md
├── workflow.md
├── {output}-template.md        # Template for generated artifacts
└── steps/
    └── ...
```

### 6. Simple Workflows

For skills that do not need multi-step decomposition, put all instructions directly in `workflow.md` without a `steps/` directory:

```text
skill-name/
├── SKILL.md
└── workflow.md
```

## Creating an Agent Skill

### 1. Create SKILL.md with Inline Persona

Agent skills embed the full persona definition in `SKILL.md`:

```markdown
---
name: bmad-agent-{agent-name}
description: '{One-line description of the agent role}'
---

# Identity

You are {Persona Name}, {role description}.

# Communication Style

{How the agent communicates — tone, formality, patterns}

# Principles

{Core operating principles that guide all interactions}

# Capabilities

| Code | Description | Skill / Workflow |
| --- | --- | --- |
| XX | {Capability description} | {Referenced workflow} |

# On Activation

1. Load config via `bmad-init` skill
2. Search for and load `**/project-context.md`
3. Greet user by name
4. Present Capabilities table
5. **STOP and WAIT** for user input
6. When user responds with a code, load and execute the corresponding workflow
```

### 2. Create bmad-skill-manifest.yaml

Agent skills require a manifest for the build system:

```yaml
type: agent
name: bmad-agent-{agent-name}
displayName: {Persona Name}
title: "{Formal Title}"
icon: "{emoji}"
capabilities: "{comma-separated capability keywords}"
role: "{Formal Role Description}"
identity: "{Multi-sentence persona description}"
communicationStyle: "{Communication style description}"
principles: "{Core principles}"
module: {module-code}
```

The build system uses this to generate `agent-manifest.csv`.

## Registering Skills

### Update module-help.csv

Add a row to the module's `module-help.csv`:

```csv
{module},{skill-name},{display-name},{menu-code},{description},{action},{args},{phase},{after},{before},{required},{output-location},{outputs}
```

Field reference:

| Field | Description | Example |
| --- | --- | --- |
| module | Module display name | `compass` |
| skill | Skill name (matches SKILL.md name) | `bmad-compass-my-workflow` |
| display-name | Human-readable name | `My Workflow` |
| menu-code | 1-2 letter quick code | `MW` |
| description | Brief description | `Run my custom workflow` |
| action | Sub-action if applicable | (empty or `create`, `validate`) |
| args | CLI arguments | (empty or `--content`, `[path]`) |
| phase | Phase classification | `anytime`, `1-analysis`, etc. |
| after | Prerequisite skill | (empty or skill name) |
| before | Successor skill | (empty or skill name) |
| required | Part of required chain | `true` or `false` |
| output-location | Output directory template | `planning_artifacts` |
| outputs | Artifact types produced | `prd`, `architecture`, etc. |

### Build and Validate

```bash
npm run validate && npm run build
```

The build system will:

1. Discover your `SKILL.md` via recursive file scan
2. Extract frontmatter (name + description)
3. Add it to `dist/_bmad/_config/skill-manifest.csv`
4. Generate client skill wrappers in `.claude/skills/`, `.opencode/skills/`, `.codex/skills/`
5. Aggregate `module-help.csv` into `dist/_bmad/_config/bmad-help.csv`

### Client Skill Naming

The build system transforms skill names for client platforms:

| Module | Source Name | Client Name |
| --- | --- | --- |
| bmm | `bmad-create-prd` | `bmad-bmm-create-prd` |
| core | `bmad-brainstorming` | `bmad-brainstorming` |
| compass | `bmad-compass-my-skill` | `bmad-compass-my-skill` |
| bmad-builder | `bmad-module-builder` | `bmad-builder-module-builder` |

## Testing a New Skill

1. Run `npm run build` to generate dist artifacts
2. Run `npm run push -- --targets bmad --project . --dry-run` to preview distribution
3. Push to a test project: `npm run push -- --targets bmad --project /path/to/test-repo`
4. Invoke the skill in the test project to verify behavior

## Common Patterns

### Workflow with Templates

Many workflows produce structured documents. Include a template file that the workflow instructions reference:

```markdown
## Instructions

Generate the output using the template in [./output-template.md](./output-template.md).
```

### Context Loading

Workflows that need project state should load it during initialization:

```markdown
## Initialization

1. Search for and load `**/project-context.md`
2. Load active phase state from `planning/current/phase-state.yaml`
3. Review existing artifacts in `planning/current/planning/`
```

### Gate Workflows

Workflows that validate other artifacts should produce explicit pass/fail evidence:

```markdown
## Completion

1. Write validation results to `planning/current/testing/gates/`
2. Clearly state PASS or FAIL with specific findings
3. If FAIL, list required remediations before retry
```

## Related Documentation

- [BMAD Overview](./bmad-overview.md) — method and architecture introduction
- [Creating Modules](./creating-modules.md) — how to create a new module
- [Modifying BMAD](./modifying-bmad.md) — extending without forking upstream
