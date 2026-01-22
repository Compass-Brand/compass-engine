# BMB (BMAD Method Builder) Workflow Structure Documentation

**Version:** 6.0.0-alpha
**Location:** `_bmad/bmb/`
**Date:** 2026-01-09

This document provides a comprehensive map of all BMB workflows, their step files, and execution patterns.

---

## Table of Contents

1. [Overview](#overview)
2. [Module Structure](#module-structure)
3. [Workflow Catalog](#workflow-catalog)
4. [Agent Workflow Deep-Dive](#agent-workflow-deep-dive)
5. [Create-Workflow Workflow](#create-workflow-workflow)
6. [Edit-Workflow Workflow](#edit-workflow-workflow)
7. [Workflow-Compliance-Check Workflow](#workflow-compliance-check-workflow)
8. [Create-Module Workflow](#create-module-workflow)
9. [Edit-Module Workflow](#edit-module-workflow)
10. [Data Files Reference](#data-files-reference)
11. [Templates Reference](#templates-reference)
12. [Common Patterns](#common-patterns)

---

## Overview

BMB provides specialized tools and workflows for creating, customizing, and extending BMAD components. It consists of:

- **3 Builder Agents**: Bond (Agent Builder), Morgan (Module Builder), Wendy (Workflow Builder)
- **6 Creation Workflows**: agent/, create-module/, edit-module/, create-workflow/, edit-workflow/, workflow-compliance-check/
- **Full Context Hub Integration**: Forgetful MCP, Serena LSP, Context7

### Core Principles

All BMB workflows use **step-file architecture**:

| Principle | Description |
|-----------|-------------|
| Micro-file Design | Each step is a self-contained instruction file |
| Just-In-Time Loading | Only the current step file is in memory |
| Sequential Enforcement | Steps completed in order, no skipping |
| State Tracking | Progress documented in tracking files |
| Menu-Driven Flow | User selects options at each step |

### Critical Rules (All Workflows)

- NEVER load multiple step files simultaneously
- ALWAYS read entire step file before execution
- NEVER skip steps unless explicitly optional
- ALWAYS halt at menus and wait for input
- NEVER create mental todo lists from future steps

---

## Module Structure

```
_bmad/bmb/
├── config.yaml                    # Module configuration with Context Hub
├── README.md                      # Module overview
├── agents/
│   ├── agent-builder.md           # Bond - Agent specialist
│   ├── module-builder.md          # Morgan - Module specialist
│   └── workflow-builder.md        # Wendy - Workflow specialist
├── workflows/
│   ├── agent/                     # Tri-modal agent workflow (CREATE/EDIT/VALIDATE)
│   │   ├── workflow.md
│   │   ├── steps-c/               # CREATE mode steps (01-09)
│   │   ├── steps-e/               # EDIT mode steps (e-01 to e-10)
│   │   ├── steps-v/               # VALIDATE mode steps (v-01 to v-03)
│   │   ├── data/                  # Reference data files
│   │   └── templates/             # Agent templates
│   ├── create-module/             # Module creation workflow
│   │   ├── workflow.md
│   │   ├── steps/                 # Steps 01-11
│   │   └── templates/
│   ├── edit-module/               # Module editing workflow
│   │   ├── workflow.md
│   │   ├── steps/                 # 21 step files
│   │   ├── data/
│   │   └── templates/
│   ├── create-workflow/           # Workflow creation workflow
│   │   ├── workflow.md
│   │   ├── steps/                 # Steps 01-09
│   │   └── data/examples/
│   ├── edit-workflow/             # Workflow editing workflow
│   │   ├── workflow.md
│   │   ├── steps/                 # Steps 01-05
│   │   └── templates/
│   └── workflow-compliance-check/ # Compliance validation
│       ├── workflow.md
│       ├── steps/                 # 8 validation phases
│       └── templates/
├── data/                          # Integration guides
│   ├── context-hub-integration.md
│   ├── serena-workflow-guide.md
│   └── memory-patterns.md
├── docs/                          # Full documentation
│   └── workflows/
│       ├── architecture.md
│       ├── step-file-rules.md
│       ├── intent-vs-prescriptive-spectrum.md
│       └── templates/             # Reference templates
└── reference/                     # Working examples
    ├── agents/simple-examples/
    └── workflows/meal-prep-nutrition/
```

---

## Workflow Catalog

| Workflow | Purpose | Entry | Output |
|----------|---------|-------|--------|
| `agent/` (CREATE) | Build new agent from scratch | `steps-c/step-01-brainstorm.md` | `.agent.yaml` file |
| `agent/` (EDIT) | Modify existing agent | `steps-e/e-01-load-existing.md` | Updated `.agent.yaml` |
| `agent/` (VALIDATE) | Review existing agent | `steps-v/v-01-load-review.md` | Validation report |
| `create-module/` | Build complete modules | `steps/step-01-init.md` | Full module structure |
| `edit-module/` | Modify existing modules | `steps/step-01-init.md` | Updated module |
| `create-workflow/` | Build new workflows | `steps/step-01-init.md` | Workflow structure |
| `edit-workflow/` | Modify existing workflows | `steps/step-01-analyze.md` | Updated workflow |
| `workflow-compliance-check/` | Validate against BMAD standards | `steps/step-01-validate-goal.md` | Compliance report |

---

## Agent Workflow Deep-Dive

The Agent workflow is the most complex, supporting three modes: CREATE, EDIT, and VALIDATE.

### Mode Selection

The workflow determines mode from:
1. User invocation ("create agent" / "edit agent" / "validate agent")
2. Or explicit menu: [C]reate / [E]dit / [V]alidate

### CREATE Mode Steps (steps-c/)

| Step | File | Purpose | Menu Options |
|------|------|---------|--------------|
| 01 | `step-01-brainstorm.md` | Optional brainstorming | [y/n] for brainstorm, [C] Continue |
| 02 | `step-02-discovery.md` | Holistic discovery | [A] Advanced, [P] Party Mode, [C] Continue |
| 03 | `step-03-type-metadata.md` | Determine agent type, define metadata | [A][P][C] |
| 04 | `step-04-persona.md` | Four-field persona development | [A][P][C] |
| 05 | `step-05-commands-menu.md` | Build command structure | [A][P][C] |
| 06 | `step-06-activation.md` | Plan activation, route to build | [A][P][C] → routes to 07a/07b/07c |
| 07a | `step-07a-build-simple.md` | Build Simple agent YAML | [A][P][C] |
| 07b | `step-07b-build-expert.md` | Build Expert agent YAML + sidecar | [A][P][C] |
| 07c | `step-07c-build-module.md` | Build Module agent YAML | [A][P][C] |
| 08a | `step-08a-plan-traceability.md` | Verify build matches plan | [A][F][P][C] |
| 08b | `step-08b-metadata-validation.md` | Validate metadata properties | [A][F][P][C] |
| 08c | `step-08c-persona-validation.md` | Validate persona fields | [A][F][P][C] |
| 08d | `step-08d-menu-validation.md` | Validate menu patterns | [A][F][P][C] |
| 08e | `step-08e-structure-validation.md` | Validate YAML structure | [A][F][P][C] → routes to 08f or 09 |
| 08f | `step-08f-sidecar-validation.md` | Validate sidecar (Expert only) | [A][F][P][C] |
| 09 | `step-09-celebrate.md` | Completion and installation guidance | [A][P][X] |

#### Routing Logic (Step 06)

```
hasSidecar: false                    → step-07a-build-simple.md
hasSidecar: true + module: stand-alone → step-07b-build-expert.md
hasSidecar: true + module: != stand-alone → step-07c-build-module.md
```

#### Validation Steps (08a-08f)

The validation sequence provides systematic quality gates:

| Step | Validates | Key Checks |
|------|-----------|------------|
| 08a Plan Traceability | Build matches plan | Metadata, persona, commands, critical actions |
| 08b Metadata | Properties | Required fields, format, naming conventions |
| 08c Persona | Four fields | Role, identity, communication style, principles |
| 08d Menu | Commands | Structure, patterns, alignment |
| 08e Structure | YAML | Syntax, completeness, type requirements |
| 08f Sidecar | Expert agents | Folder existence, path references, file contents |

### EDIT Mode Steps (steps-e/)

| Step | File | Purpose |
|------|------|---------|
| e-01 | `e-01-load-existing.md` | Load and analyze existing agent |
| e-02 | `e-02-discover-edits.md` | Discover what user wants to change |
| e-03a | `e-03a-validate-metadata.md` | Pre-edit metadata validation |
| e-03b | `e-03b-validate-persona.md` | Pre-edit persona validation |
| e-03c | `e-03c-validate-menu.md` | Pre-edit menu validation |
| e-03d | `e-03d-validate-structure.md` | Pre-edit structure validation |
| e-03e | `e-03e-validate-sidecar.md` | Pre-edit sidecar validation |
| e-03f | `e-03f-validation-summary.md` | Pre-edit validation summary |
| e-04 | `e-04-type-metadata.md` | Edit type and metadata |
| e-05 | `e-05-persona.md` | Edit persona |
| e-06 | `e-06-commands-menu.md` | Edit commands/menu |
| e-07 | `e-07-activation.md` | Edit activation |
| e-08a | `e-08a-edit-simple.md` | Apply Simple agent edits |
| e-08b | `e-08b-edit-expert.md` | Apply Expert agent edits |
| e-08c | `e-08c-edit-module.md` | Apply Module agent edits |
| e-09a-f | `e-09a-f-*.md` | Post-edit validation (6 steps) |
| e-10 | `e-10-celebrate.md` | Completion |

### VALIDATE Mode Steps (steps-v/)

| Step | File | Purpose |
|------|------|---------|
| v-01 | `v-01-load-review.md` | Load agent, initialize report |
| v-02a | `v-02a-validate-metadata.md` | Metadata validation |
| v-02b | `v-02b-validate-persona.md` | Persona validation |
| v-02c | `v-02c-validate-menu.md` | Menu validation |
| v-02d | `v-02d-validate-structure.md` | Structure validation |
| v-02e | `v-02e-validate-sidecar.md` | Sidecar validation |
| v-03 | `v-03-summary.md` | Summary and next steps |

---

## Create-Workflow Workflow

**Purpose:** Create structured, repeatable standalone workflows through collaborative conversation.

### Step Sequence

| Step | File | Purpose | Key Actions |
|------|------|---------|-------------|
| 01 | `step-01-init.md` | Initialize workflow creation | Load config, check continuity |
| 02 | `step-02-gather.md` | Gather requirements | Understand purpose, users, outcomes |
| 03 | `step-03-tools-configuration.md` | Configure tools | Identify needed tools, permissions |
| 04 | `step-04-plan-review.md` | Review plan | Validate approach |
| 05 | `step-05-output-format-design.md` | Design outputs | Define deliverables |
| 06 | `step-06-design.md` | Design workflow | Step structure, flow |
| 07 | `step-07-build.md` | Build workflow | Create files |
| 08 | `step-08-review.md` | Review and validate | Quality check |
| 09 | `step-09-complete.md` | Complete workflow | Finalize, document |

### Example Workflow

The workflow includes a complete example at `data/examples/meal-prep-nutrition/` demonstrating:
- Proper step file structure
- Data files (CSV)
- Templates
- Main workflow.md

---

## Edit-Workflow Workflow

**Purpose:** Intelligently edit and improve existing workflows while following best practices.

### Step Sequence

| Step | File | Purpose |
|------|------|---------|
| 01 | `step-01-analyze.md` | Analyze current workflow structure |
| 02 | `step-02-discover.md` | Discover improvement goals |
| 03 | `step-03-improve.md` | Apply improvements |
| 04 | `step-04-validate.md` | Validate changes |
| 05 | `step-05-compliance-check.md` | Run compliance check |

### Templates Produced

| Template | Purpose |
|----------|---------|
| `workflow-analysis.md` | Current state analysis |
| `improvement-goals.md` | Documented improvement targets |
| `improvement-log.md` | Changes made |
| `validation-results.md` | Validation findings |
| `completion-summary.md` | Final summary |

---

## Workflow-Compliance-Check Workflow

**Purpose:** Systematically validate workflows against BMAD standards with adversarial analysis.

### 8-Phase Validation

| Phase | Step | Purpose | Key Checks |
|-------|------|---------|------------|
| 1 | `step-01-validate-goal.md` | Goal confirmation | Target workflow, scope |
| 2 | `step-02-workflow-validation.md` | Workflow.md validation | Frontmatter, role, architecture, initialization |
| 3 | `step-03-step-validation.md` | Step file validation | Each step against template |
| 4 | `step-04-file-validation.md` | File validation | References, paths |
| 5 | `step-05-intent-spectrum-validation.md` | Intent spectrum | Intent vs prescriptive balance |
| 6 | `step-06-web-subprocess-validation.md` | Web subprocess | External integrations |
| 7 | `step-07-holistic-analysis.md` | Holistic analysis | Flow, goals, optimization, meta-workflow failures |
| 8 | `step-08-generate-report.md` | Report generation | Comprehensive compliance report |

### Violation Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| Critical | Workflow cannot function | Must fix immediately |
| Major | Impacts quality/maintainability | Should fix before use |
| Minor | Standards compliance | Fix for full compliance |

### Report Structure

```markdown
# Workflow Compliance Report
- Executive Summary (status, issue counts, score)
- Phase 1: Workflow.md Validation Results
- Phase 2: Step-by-Step Validation Results
- Phase 3: Holistic Analysis Results
- Meta-Workflow Failure Analysis
- Severity-Ranked Fix Recommendations
- Automated Fix Options
- Next Steps Recommendation
```

---

## Create-Module Workflow

**Purpose:** Build complete, installable BMAD modules with proper structure, agents, workflows, and documentation.

### Step Sequence

| Step | File | Purpose |
|------|------|---------|
| 01 | `step-01-init.md` | Initialize module creation |
| 01b | `step-01b-continue.md` | Resume existing session |
| 02 | `step-02-concept.md` | Define module concept |
| 03 | `step-03-components.md` | Plan components |
| 04 | `step-04-structure.md` | Define file structure |
| 05 | `step-05-config.md` | Create config.yaml |
| 06 | `step-06-agents.md` | Define agents |
| 07 | `step-07-workflows.md` | Plan workflows |
| 08 | `step-08-installer.md` | Create installer |
| 09 | `step-09-documentation.md` | Write documentation |
| 10 | `step-10-roadmap.md` | Define roadmap |
| 11 | `step-11-validate.md` | Validate module |

### Templates Produced

| Template | Purpose |
|----------|---------|
| `agent.template.md` | Agent structure template |
| `installer.template.js` | Installation script |
| `module-plan.template.md` | Module planning doc |
| `module.template.yaml` | Module configuration |
| `workflow-plan-template.md` | Workflow planning doc |

---

## Edit-Module Workflow

**Purpose:** Safely edit agents, workflows, config, and documentation in existing BMAD modules.

### Step Structure (21 Steps)

| Phase | Steps | Purpose |
|-------|-------|---------|
| Init | 01, 01b | Session creation or continuation |
| Analysis | 02 | Module structure analysis |
| Selection | 03 | Edit type menu |
| Agent Editing | 04a, 04a1-04a3, 04a+, 04a- | Agent modifications |
| Workflow Editing | 04b, 04b1-04b2, 04b+, 04b- | Workflow modifications |
| Config/Docs | 04c, 04d | Configuration and documentation |
| Validation | 05 | BMAD compliance checking |
| Iteration | 06 | "More edits?" decision loop |
| Completion | 07 | Backup cleanup, changelog, close |

### Agent Editing Steps

| Step | Purpose |
|------|---------|
| `step-04a-agent-load.md` | Load existing agent |
| `step-04a-agent-add.md` | Add new agent |
| `step-04a-agent-remove.md` | Remove agent |
| `step-04a1-agent-simple.md` | Edit Simple agent |
| `step-04a2-agent-expert.md` | Edit Expert agent |
| `step-04a3-agent-module.md` | Edit Module agent |

### Workflow Editing Steps

| Step | Purpose |
|------|---------|
| `step-04b-workflow-load.md` | Load existing workflow |
| `step-04b-workflow-add.md` | Add new workflow |
| `step-04b-workflow-remove.md` | Remove workflow |
| `step-04b1-workflow-standalone.md` | Edit standalone workflow |
| `step-04b2-workflow-legacy.md` | Edit legacy workflow |

---

## Data Files Reference

### Agent Workflow Data (workflows/agent/data/)

| File | Purpose |
|------|---------|
| `agent-metadata.md` | Metadata properties reference (id, name, title, icon, module, hasSidecar) |
| `agent-compilation.md` | YAML source to compiled agent transformation |
| `agent-menu-patterns.md` | Menu structure patterns |
| `brainstorm-context.md` | Context for brainstorming step |
| `communication-presets.csv` | Communication style options |
| `critical-actions.md` | Critical actions reference |
| `expert-agent-architecture.md` | Expert agent structure |
| `expert-agent-validation.md` | Expert validation rules |
| `module-agent-validation.md` | Module validation rules |
| `persona-properties.md` | Persona field definitions |
| `principles-crafting.md` | Principles composition guidance |
| `simple-agent-architecture.md` | Simple agent structure |
| `simple-agent-validation.md` | Simple validation rules |
| `understanding-agent-types.md` | Agent type classification guide |

### Agent Metadata Properties

| Property | Purpose | Format |
|----------|---------|--------|
| `id` | Compiled output path | `_bmad/agents/{name}/{name}.md` |
| `name` | Persona's identity name | "First Last" or "Name Title" |
| `title` | Professional role (becomes filename) | "Code Review Specialist" |
| `icon` | Visual identifier | Single emoji only |
| `module` | Team/ecosystem membership | `stand-alone`, `bmm`, `cis`, `bmgd`, or custom |
| `hasSidecar` | Sidecar folder exists | `true` (Expert) or `false` (Simple) |

### Four-Field Persona System

| Field | Purpose | Content |
|-------|---------|---------|
| `role` | WHAT they do | Professional identity, expertise domain |
| `identity` | WHO they are | Character, personality, attitude |
| `communication_style` | HOW they speak | Language patterns, tone, voice |
| `principles` | WHY they act | Decision-making framework, values |

### BMB Module Data (_bmad/bmb/data/)

| File | Purpose |
|------|---------|
| `context-hub-integration.md` | Complete Context Hub usage guide |
| `memory-patterns.md` | Memory system patterns for BMB |
| `serena-workflow-guide.md` | Serena LSP usage for BMB |

---

## Templates Reference

### Agent Templates (workflows/agent/templates/)

| Template | Purpose |
|----------|---------|
| `agent-plan.template.md` | Agent planning document |
| `simple-agent.template.md` | Simple agent YAML structure |
| `expert-agent-template/expert-agent.template.md` | Expert agent YAML structure |

### Workflow Templates (docs/workflows/templates/)

| Template | Purpose |
|----------|---------|
| `step-template.md` | Standard step file structure |
| `step-01-init-continuable-template.md` | Init step with session continuity |
| `step-1b-template.md` | Continuation step template |
| `workflow-template.md` | Main workflow.md structure |
| `workflow.md` | Reference workflow |

---

## Common Patterns

### Standard Menu Pattern

All step files use consistent menu patterns:

```markdown
### N. Present MENU OPTIONS

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}, then redisplay menu
- IF P: Execute {partyModeWorkflow}, then redisplay menu
- IF C: Save content, update frontmatter, load and execute {nextStepFile}
- IF Any other comments: help user, then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
```

### Validation Step Pattern

Validation steps include additional [F] Fix option:

```markdown
Display: "**Select an Option:** [A] Advanced Elicitation [F] Fix Findings [P] Party Mode [C] Continue"

- IF F: Apply auto-fixes to {builtYaml} for identified issues, then redisplay menu
```

### Step File Structure

Every step file follows this structure:

```yaml
---
name: 'step-XX-name'
description: 'Step description'

# File References
nextStepFile: './step-XX-next.md'
# ... other references
---

# Step Title

## STEP GOAL:
[Clear goal statement]

## MANDATORY EXECUTION RULES (READ FIRST):
### Universal Rules:
- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read complete step file before action
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ ALWAYS speak in {communication_language}

### Role Reinforcement:
[Role-specific guidance]

### Step-Specific Rules:
[Rules for this step]

## EXECUTION PROTOCOLS:
[Detailed protocols]

## CONTEXT BOUNDARIES:
[What's in/out of scope]

## Sequence of Instructions (Do not deviate, skip, or optimize)
### 1. [First instruction]
### 2. [Second instruction]
...
### N. Present MENU OPTIONS

## CRITICAL STEP COMPLETION NOTE
[When step is considered complete]

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
[Success criteria]

### ❌ SYSTEM FAILURE:
[Failure indicators]

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
```

### Context Hub Integration Pattern

All workflows support Context Hub hooks:

```python
# Pre-Workflow Hook - Query for patterns
mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "relevant patterns {type}",
  "query_context": "Starting {workflow}",
  "tags": ["{pattern-type}", "bmb"],
  "include_links": true
})

# Post-Workflow Hook - Save patterns
IF success:
  mcp__forgetful__execute_forgetful_tool("create_memory", {
    "title": "BMB {Type}: {name}",
    "content": "Created/edited {type}. Details: {details}. Lessons: {lessons}.",
    "context": "{Type} via BMB",
    "keywords": ["bmb", "{type}", "{pattern}"],
    "importance": 7-9
  })
```

---

## Quick Reference: Agent Type Classification

| Type | hasSidecar | Complexity | Use Case |
|------|------------|------------|----------|
| Simple | `false` | Single focused purpose | Code reviewer, documentation generator |
| Expert | `true` | Multi-capability, domain expertise | Game architect, system designer |
| Module | `true` | Agent builder/manager, deploys workflows | Agent-builder, workflow-builder |

---

## Quick Reference: Importance Levels for Memories

| Type | Importance | Examples |
|------|------------|----------|
| Module patterns | 9 | Complete module creation with agents and workflows |
| Agent patterns | 8 | Agent creation with lessons learned |
| Workflow patterns | 8 | Workflow creation with patterns used |
| Edit lessons | 7 | Changes made and their rationale |
| Compliance findings | 6-7 | Validation results and improvements |

---

*This document generated from analysis of `_bmad/bmb/` workflow structure.*
