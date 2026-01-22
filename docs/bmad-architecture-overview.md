# BMAD Architecture Overview

## Executive Summary

BMAD (Build More, Architect Dreams) is a modular AI-driven development framework that provides **21 specialized AI agents** across **4 official modules** and **50+ guided workflows**. It adapts to project complexity through a scale-adaptive tier system, supporting everything from single bug fixes to enterprise platforms.

**Repository:** `bmad-code-org/BMAD-METHOD`
**Current Version:** V6 (Alpha)
**License:** MIT

---

## Core Architecture

### The Foundation: BMad Core (C.O.R.E.)

**C.O.R.E. = Collaboration Optimized Reflection Engine**

BMad Core is the universal foundation that all modules build upon. It provides:

1. **Global Configuration** - User settings, language preferences, output paths
2. **Core Workflows** - Domain-agnostic capabilities available to all modules:
   - **Party Mode** - Multi-agent conversation orchestration
   - **Brainstorming** - 60+ creative techniques
   - **Advanced Elicitation** - 50+ reasoning methods
3. **Core Tasks** - Common operations (document indexing, sharding, review)
4. **BMad Master Agent** - Primary orchestrator and knowledge custodian

### Core Module Configuration (`src/core/module.yaml`)

```yaml
code: core
name: "BMad Core Module"

# Configuration prompts collected during installation:
user_name: "What shall the agents call you?"
communication_language: "Preferred chat language/style?"
document_output_language: "Preferred document output language?"
output_folder: "Where should default output files be saved?"
```

---

## Module Architecture

### Module Hierarchy

```
BMAD Platform
|
+-- Core (Always Installed)
|   +-- bmad-master agent
|   +-- party-mode workflow
|   +-- brainstorming workflow
|   +-- advanced-elicitation workflow
|
+-- BMM (BMAD Method Module) - Software Development
|   +-- 9 specialized agents (PM, Architect, Dev, etc.)
|   +-- 34+ workflows across 4 phases
|   +-- Quick Flow track
|   +-- TestArch subsystem
|
+-- BMB (BMAD Builder Module) - Content Creation
|   +-- 3 builder agents
|   +-- Workflows for agents, workflows, and modules
|
+-- CIS (Creative Intelligence Suite)
|   +-- Creative facilitation workflows
|   +-- Innovation and ideation tools
|
+-- BMGD (BMAD Game Dev) - Game Development
    +-- Game design workflows
    +-- Narrative development
```

### Module Structure (Standard Pattern)

```
src/modules/{module}/
+-- module.yaml           # Module configuration and prompts
+-- agents/               # Agent definitions (*.agent.yaml)
+-- workflows/            # Workflow directories
|   +-- {workflow-name}/
|       +-- workflow.md or workflow.yaml  # Entry point
|       +-- steps/        # Step files (sequential)
|       +-- data/         # Reference materials
|       +-- templates/    # Output templates
+-- data/                 # Module-wide reference data
+-- teams/                # Team configurations (if applicable)
```

---

## The Three Tracks

BMAD uses a **scale-adaptive system** that matches planning depth to project complexity.

### Track Comparison

| Track | Use Case | Planning | Time to Start |
|-------|----------|----------|---------------|
| **Quick Flow** | Bug fixes, small features (1-10 stories) | Tech spec only | < 5 minutes |
| **BMad Method** | Products, platforms (5-40 stories) | PRD + Architecture + UX | < 15 minutes |
| **Enterprise** | Compliance, scale (40+ stories) | Full governance suite | < 30 minutes |

### Project Levels (`project-levels.yaml`)

The tier system maps project complexity to workflow requirements:

| Level | Title | Stories | Documentation | Architecture |
|-------|-------|---------|---------------|--------------|
| **0** | Single Atomic Change | 1 | Minimal - tech spec only | No |
| **1** | Small Feature | 1-10 | Tech spec | No |
| **2** | Medium Project | 5-15 | PRD + optional tech spec | No |
| **3** | Complex System | 12-40 | PRD + architecture + JIT tech specs | Yes |
| **4** | Enterprise Scale | 40+ | PRD + architecture + JIT tech specs | Yes |

### Detection Keywords

```yaml
level_0: ["fix", "bug", "typo", "small change", "quick update", "patch"]
level_1: ["simple", "basic", "small feature", "add", "minor"]
level_2: ["dashboard", "several features", "admin panel", "medium"]
level_3: ["platform", "integration", "complex", "system", "architecture"]
level_4: ["enterprise", "multi-tenant", "multiple products", "ecosystem", "scale"]
```

---

## Four-Phase Methodology

### Phase Overview

| Phase | Name | Purpose | Required? |
|-------|------|---------|-----------|
| **1** | Analysis | Exploration and discovery | Optional |
| **2** | Planning | Requirements definition | Required |
| **3** | Solutioning | Technical design | Track-dependent |
| **4** | Implementation | Building the software | Required |

### Phase 1: Analysis (Optional)

**Purpose:** Explore ideas, validate markets, understand requirements before planning.

**Workflows:**
- `brainstorm-project` - Solution exploration (Core)
- `research` - Market/technical/competitive research
- `product-brief` - Strategic vision capture

**Agents:** Analyst

### Phase 2: Planning (Required)

**Purpose:** Define WHAT to build and WHY.

**Workflows:**
- `prd` - Product Requirements Document (Method/Enterprise)
- `tech-spec` - Technical specification (Quick Flow)
- `create-ux-design` - UX specification (if UI exists)

**Agents:** PM, UX Designer

### Phase 3: Solutioning (Track-Dependent)

**Purpose:** Design HOW to build - architecture and work breakdown.

**Workflows:**
- `create-architecture` - System design with ADRs
- `create-epics-and-stories` - Work breakdown (after architecture)
- `test-design` - System-level testability review (optional)
- `implementation-readiness` - Gate check

**Agents:** Architect, PM, TEA (Test Architect)

**Note:** V6 creates epics AFTER architecture for better quality.

### Phase 4: Implementation (Required)

**Purpose:** Iterative sprint-based development.

**Workflows:**
- `sprint-planning` - Initialize tracking
- `create-story` - Prepare stories (JIT)
- `dev-story` - Implement with tests
- `code-review` - Quality assurance
- `retrospective` - Continuous improvement

**Agents:** Scrum Master (SM), Developer (Dev)

---

## Workflow Architecture

### Workflow Structure

```
{workflow-name}/
+-- workflow.md or workflow.yaml    # Entry point (minimal)
+-- steps/                          # Sequential step files
|   +-- step-01-init.md
|   +-- step-02-profile.md
|   +-- step-N-final.md
+-- steps-c/                        # Create mode steps (tri-modal)
+-- steps-e/                        # Edit mode steps (tri-modal)
+-- steps-v/                        # Validate mode steps (tri-modal)
+-- data/                           # Reference materials, CSVs
+-- templates/                      # Output document templates
```

### Key Workflow Concepts

#### Progressive Disclosure

The AI only sees the current step. It cannot see step 5 when on step 2. This prevents:
- Getting ahead of itself
- Skipping steps
- Losing focus

Each step gets full attention before the next step loads.

#### Tri-Modal Pattern

Critical workflows use three modes:

1. **Create Mode** - Build new artifacts from scratch or convert non-compliant documents
2. **Validate Mode** - Standalone quality check against standards
3. **Edit Mode** - Modify existing artifacts while enforcing standards

All BMAD planning workflows use this pattern.

#### Continuable Workflows

Complex workflows can span multiple sessions:
- Progress tracked in output document frontmatter
- Users can stop and resume later
- Suitable for large documents, complex decisions, 8+ steps

#### Workflow Chaining

Outputs become inputs for next workflow:

```
brainstorming -> research -> brief -> PRD -> UX -> architecture -> epics -> sprint-planning
                                                                        |
                                                            implement-story -> review -> repeat
```

### Workflow Path Files

Each track has a path file defining the workflow sequence:

**Location:** `src/modules/bmm/workflows/workflow-status/paths/`

- `method-greenfield.yaml` - New projects with full methodology
- `method-brownfield.yaml` - Existing codebase integration
- `enterprise-greenfield.yaml` - Enterprise new projects
- `enterprise-brownfield.yaml` - Enterprise existing code

**Path File Structure:**

```yaml
method_name: "BMad Method"
track: "bmad-method"
field_type: "greenfield"
description: "Complete product and system design methodology"

phases:
  - phase: 1
    name: "Analysis (Optional)"
    optional: true
    workflows:
      - id: "brainstorm-project"
        exec: "{project-root}/_bmad/core/workflows/brainstorming/workflow.md"
        optional: true
        agent: "analyst"
        command: "/bmad:bmm:workflows:brainstorming"
```

---

## Agent Architecture

### Agent Definition Structure

Agents are defined in YAML with the following structure:

```yaml
agent:
  metadata:
    id: "_bmad/module/agents/agent-name.md"
    name: "Agent Display Name"
    title: "Full Agent Title"
    icon: "emoji"
    hasSidecar: false  # true for expert agents

  persona:
    role: "Primary role description"
    identity: "Detailed expertise and knowledge"
    communication_style: "How the agent communicates"
    principles: "Core operating principles"

  critical_actions:
    - "Actions to execute on load"

  menu:
    - trigger: "command or fuzzy match"
      action: "what to do"
      description: "Menu item description"
```

### Agent Types

1. **Simple Agents** - Single file, self-contained
2. **Expert Agents** - Include sidecar folder with additional resources
3. **Module Agents** - Integrated with workflows, professional tools

### BMM Agents (9)

| Agent | Role | Phase |
|-------|------|-------|
| **Analyst** | Business analysis, research, briefs | 1 |
| **PM** | Product requirements, epics/stories | 2, 3 |
| **UX Designer** | User experience design | 2 |
| **Architect** | System architecture, tech decisions | 3 |
| **SM** (Scrum Master) | Sprint planning, tracking | 4 |
| **Dev** | Implementation, coding | 4 |
| **TEA** (Test Architect) | Testing strategy, automation | 3, 4 |
| **Tech Writer** | Documentation | All |
| **Quick Flow Solo Dev** | Combined spec+dev for simple tasks | Quick Flow |

### BMB Agents (3)

| Agent | Role |
|-------|------|
| **Agent Builder** | Create custom agents |
| **Workflow Builder** | Create custom workflows |
| **Module Builder** | Create custom modules |

### Core Agent (1)

| Agent | Role |
|-------|------|
| **BMad Master** | Orchestration, task execution, knowledge custodian |

---

## Module Relationships

### Dependency Graph

```
                    +-------------+
                    | BMad Core   |
                    | (Required)  |
                    +------+------+
                           |
           +---------------+---------------+
           |               |               |
    +------v------+ +------v------+ +------v------+
    |    BMM      | |    BMB      | |    CIS      |
    | (Method)    | | (Builder)   | | (Creative)  |
    +-------------+ +------+------+ +-------------+
                           |
                           v
                   Custom Modules
                   (User Created)
```

### Inheritance Model

1. **Core -> All Modules**
   - Global configuration (user name, language, output folder)
   - Core workflows (party-mode, brainstorming, elicitation)
   - Core tasks (indexing, sharding, review)

2. **BMB -> Custom Content**
   - Agent creation workflows
   - Workflow authoring tools
   - Module scaffolding

3. **Module -> Workflows -> Agents**
   - Workflows invoke specific agents
   - Agents access module configuration
   - Outputs chain between workflows

### Installation Structure

After installation, BMAD creates:

```
{project-root}/
+-- _bmad/
|   +-- _config/           # Installation configuration
|   |   +-- config.yaml    # Global config
|   |   +-- task-manifest.csv
|   |   +-- workflow-manifest.csv
|   +-- core/              # Core module (always present)
|   +-- bmm/               # BMAD Method (if installed)
|   +-- bmb/               # BMAD Builder (if installed)
|   +-- cis/               # Creative Intelligence (if installed)
|   +-- bmgd/              # Game Dev (if installed)
+-- _bmad-output/          # Default output folder
    +-- planning-artifacts/  # PRDs, architectures, etc.
    +-- implementation-artifacts/  # Sprint files, stories
```

---

## Custom Content Types

BMB enables creation of custom content:

### Custom Modules

| Type | Description |
|------|-------------|
| **Stand-Alone** | Independent modules with full capabilities |
| **Add-On** | Extensions for existing modules |
| **Global** | Cross-cutting functionality for all modules |

### Custom Agents

| Type | Structure |
|------|-----------|
| **BMad Tiny** | Personal, highly specific single-file agents |
| **Simple** | Self-contained single file |
| **Expert** | Includes sidecar folder with additional resources |

### Custom Workflows

- Single or series of prompts
- Can include step files
- Distributable via slash commands
- Can operate without associated agents

---

## Quick Flow vs Full Method

### Quick Flow (Fast Track)

**3-step process:**

```
Tech-Spec -> Dev -> Optional Review
```

**Automatic features:**
- Stack detection (package.json, requirements.txt, etc.)
- Brownfield code analysis
- Test framework detection
- Convention confirmation
- Auto-validation

### Full BMad Method (Standard Track)

```
Phase 1 (Optional) -> Phase 2 (PRD) -> Phase 3 (Architecture) -> Phase 4 (Implementation)
```

**Manual features:**
- Stakeholder alignment
- Comprehensive documentation
- Deep architectural analysis
- Multi-team coordination

---

## State Management

### Workflow Status File

**Location:** `{planning_artifacts}/bmm-workflow-status.yaml`

Tracks:
- Current project level and type
- Active workflow path
- Completion status of each workflow
- Next workflow to execute

### Status File Structure

```yaml
project: "Project Name"
project_type: "method"  # quick-flow, method, enterprise
project_level: 3
field_type: "greenfield"  # or brownfield
workflow_path: "method-greenfield"

workflow_status:
  brainstorm-project: optional
  research: optional
  product-brief: optional
  prd: required
  create-ux-design: conditional
  create-architecture: required
  # ... etc
```

### Status Values

- **required** - Must complete
- **optional** - User choice
- **conditional** - Depends on context (e.g., `if_has_ui`)
- **skipped** - Deliberately skipped
- **{file_path}** - Completed (path to output)

---

## Key Architectural Principles

1. **Progressive Disclosure** - AI sees only current step, preventing shortcuts
2. **Sequential Enforcement** - Steps must complete fully before next loads
3. **Facilitative Philosophy** - AI as partner, user as domain expert
4. **Scale Adaptation** - Methodology matches project complexity
5. **Module Independence** - Modules work alone but integrate together
6. **Update Safety** - Custom content persists through updates

---

## Resources

- **GitHub:** https://github.com/bmad-code-org/BMAD-METHOD
- **Documentation:** http://docs.bmad-method.org/
- **Discord:** https://discord.gg/gk8jAdXWmj
- **YouTube:** https://www.youtube.com/@BMadCode

---

## Version History

- **V4** - Previous stable version (legacy)
- **V6 Alpha** - Current version with:
  - Complete architectural overhaul
  - Scale-adaptive intelligence
  - BMad Core framework
  - BMad Builder module
  - 50+ workflows (up from 20)
  - Visual workflow diagrams
  - Multi-language support
  - Document sharding (90% token savings)
