# BMAD Method Overview

Last reviewed: 2026-04-08

## What Is BMAD?

BMAD (Build More Architect Dreams) is an AI-driven agile development methodology. It provides structured workflows, specialized AI agent personas, and quality gates that guide software projects from ideation through delivery.

Compass Engine integrates the upstream [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) (MIT-licensed) and extends it with Compass Brand customizations.

## Current Version

- **Upstream:** v6.2.2 (March 26, 2026)
- **Architecture:** Skills-based (everything is a skill since v6.1.0)
- **Submodule:** `BMAD-METHOD/` at the repo root

## Core Architecture

### Skills-Based Design

Since v6.1.0, every BMAD component — workflow, agent, task — installs as a unified **skill** with a `SKILL.md` entrypoint. The installer discovers skills by scanning for `SKILL.md` files rather than manifests.

### Module System

Modules group related skills. Compass Engine uses four modules:

| Module | Code | Purpose |
| --- | --- | --- |
| BMad Method (BMM) | `bmm` | Core development methodology (~30 workflows and agents) |
| Core Skills | `core` | Utility skills (help, brainstorming, editorial review) |
| Compass Skills | `compass` | Compass Brand customizations and extensions |
| BMad Builder | `bmad-builder` | Meta-skills for creating agents, modules, and workflows |

BMM and Core each have a **native** layer (from upstream BMAD-METHOD) and a **custom** layer (Compass overrides). During build, custom overlays native.

### Dual-Layer Module Merge

```text
src/bmad/modules/native/bmm-skills/    (upstream base)
src/bmad/modules/custom/bmm-skills/    (Compass overrides)
────────────────────────────────────
dist/_bmad/bmm/                        (merged output)
```

Custom modules that have no native counterpart (compass-skills, bmad-builder-skills) are copied directly.

### Scale-Adaptive Intelligence

BMAD automatically adjusts planning depth based on project scope:

- **Level 0:** Bug fixes, trivial changes
- **Level 1:** Small features, single endpoints
- **Level 2:** Medium features
- **Level 3:** Large features, multi-service
- **Level 4:** Enterprise-scale systems

## The 4-Phase Methodology

### Phase 1: Analysis

Domain research, market research, technical research, innovation strategy, and opportunity framing. Outputs feed the product brief.

### Phase 2: Planning

Product brief, PRD creation and validation, UX design (optional WDS lane), and experience design. Produces the detailed requirements.

### Phase 3: Solutioning

Architecture design, security reviews (optional), test design, epic and story creation, and implementation readiness checks. Produces the technical blueprint.

### Phase 4: Implementation

Sprint planning, story creation, dev story execution (TDD), code review, test automation, and retrospectives. Produces the shipped code.

## Compass BMAD Workflow

The canonical workflow is defined in `src/bmad/BMAD-workflow.md`. It extends the upstream 4-phase model with:

- **Roadmap-driven execution** — projects operate as continuous roadmap systems, not one-time MVP pipelines
- **Phase sync** — formal roadmap-slice selection between phases
- **Initiative routing** — workspace/orchestration scope fans work into concurrent repo-targeted streams
- **Polyrepo support** — same structure at workspace, parent, and leaf repo levels
- **Beads integration** — issue tracking via `bd` throughout the workflow
- **Documentation control plane** — Diataxis-classified docs updated at each phase

### Required Progression Chain

```text
Initialize Docs → Init Planning → High-Level Product Brief → Project Roadmap
→ Phase Sync → [Initiative Routing if workspace] → Detailed Product Brief
→ Create PRD → Create Architecture → Create Epics and Stories
→ Check Implementation Readiness → Sprint Planning
→ Create Story → Dev Story → Phase Closeout
```

See `src/bmad/BMAD-workflow.md` for the complete workflow specification including all conditional and optional lanes.

## Skill Types

### Workflows

Multi-step processes with sequential execution. Structure:

```text
skill-name/
├── SKILL.md                    # Frontmatter + reference to workflow.md
├── workflow.md                 # Main orchestration and initialization
├── steps/                      # Sequential step files
│   ├── step-01-*.md
│   └── step-NN-*.md
└── {template}.md               # Supporting templates
```

### Agents

AI personas with defined identity, communication style, and capabilities. Structure:

```text
skill-name/
├── SKILL.md                    # Frontmatter + full persona definition
└── bmad-skill-manifest.yaml    # Agent metadata (type, role, identity, etc.)
```

## Key Slash Commands

Commands follow the pattern `/bmad-{module}-{skill-name}`. Examples:

| Command | Purpose |
| --- | --- |
| `/bmad-bmm-create-prd` | Create a Product Requirements Document |
| `/bmad-bmm-create-architecture` | Design system architecture |
| `/bmad-bmm-dev-story` | Execute a development story (TDD) |
| `/bmad-bmm-sprint-planning` | Plan a sprint |
| `/bmad-bmm-code-review` | Run code review |
| `/bmad-core-brainstorming` | Creative brainstorming session |
| `/bmad-core-help` | Get help with BMAD commands |

## Platform Support

BMAD v6 supports 15+ AI coding platforms. Compass Engine generates wrapper skills for:

- Claude Code (`.claude/skills/`)
- OpenCode (`.opencode/skills/`)
- Codex (`.codex/skills/`)

## Related Documentation

- [Creating Skills](./creating-skills.md) — how to build new workflow and agent skills
- [Creating Modules](./creating-modules.md) — how to create new BMAD modules
- [Custom Modules](./custom-modules.md) — Compass module principles
- [Modifying BMAD](./modifying-bmad.md) — extending without forking upstream
- [Upstream Changelog](./upstream-changelog.md) — BMAD-METHOD release history
- [BMAD Workflow](../../../src/bmad/BMAD-workflow.md) — canonical Compass workflow specification
