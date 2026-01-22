# BMM (BMAD Method Module) Workflow Structure

This document provides a comprehensive map of all workflows in the local BMM module (`_bmad/bmm/workflows/`).

## Table of Contents

1. [Overview](#overview)
2. [Workflow Categories](#workflow-categories)
3. [Workflow File Patterns](#workflow-file-patterns)
4. [Phase Flow Diagram](#phase-flow-diagram)
5. [Individual Workflow Details](#individual-workflow-details)
6. [Menu Patterns](#menu-patterns)
7. [Validation Workflows](#validation-workflows)
8. [Flow Connections](#flow-connections)

---

## Overview

BMM organizes workflows into a phased methodology covering the full software development lifecycle:

| Phase | Name | Purpose |
|-------|------|---------|
| 0 | Documentation | Document brownfield projects (conditional) |
| 1 | Analysis | Research, brainstorming, product briefs |
| 2 | Planning | PRD, UX Design |
| 3 | Solutioning | Architecture, Epics & Stories, Implementation Readiness |
| 4 | Implementation | Sprint planning, story creation, development, code review |

### Project Levels

Projects are classified by scale (from `project-levels.yaml`):

| Level | Title | Stories | Documentation Required |
|-------|-------|---------|----------------------|
| 0 | Single Atomic Change | 1 | Minimal - tech spec only |
| 1 | Small Feature | 1-10 | Tech spec |
| 2 | Medium Project | 5-15 | PRD + optional tech spec |
| 3 | Complex System | 12-40 | PRD + architecture + JIT tech specs |
| 4 | Enterprise Scale | 40+ | PRD + architecture + JIT tech specs |

### Field Types

- **Greenfield**: New projects starting from scratch
- **Brownfield**: Existing projects with codebase to document

---

## Workflow Categories

### 1-analysis/ - Analysis Phase Workflows

| Workflow | Description | Agent |
|----------|-------------|-------|
| `create-product-brief` | Create comprehensive product briefs through collaborative discovery | analyst |
| `research` | Conduct research (Market, Domain, or Technical) with web sources | analyst |

### 2-plan-workflows/ - Planning Phase Workflows

| Workflow | Description | Agent |
|----------|-------------|-------|
| `prd` | Create PRD through collaborative step-by-step discovery | pm |
| `create-ux-design` | Design UX patterns, look and feel | ux-designer |

### 3-solutioning/ - Solutioning Phase Workflows

| Workflow | Description | Agent |
|----------|-------------|-------|
| `create-architecture` | Collaborative architectural decision facilitation | architect |
| `create-epics-and-stories` | Transform PRD + Architecture into implementation-ready epics/stories | pm |
| `check-implementation-readiness` | Validate PRD, Architecture, Epics alignment (gate check) | architect |

### 4-implementation/ - Implementation Phase Workflows

| Workflow | Description | Agent |
|----------|-------------|-------|
| `sprint-planning` | Generate sprint-status.yaml tracking file | sm |
| `create-story` | Create next user story from epics | sm |
| `dev-story` | Execute story implementation | dev |
| `code-review` | Adversarial senior developer code review | dev |
| `correct-course` | Navigate significant changes during sprint | sm |
| `retrospective` | Epic completion review with next epic preparation | sm |
| `sprint-status` | Lightweight status checker ("what should I do now?") | any |

### bmad-quick-flow/ - Quick Flow Workflows

| Workflow | Description | Agent |
|----------|-------------|-------|
| `create-tech-spec` | Conversational spec engineering for implementation-ready specs | dev |
| `quick-dev` | Execute tech-specs OR direct instructions with optional planning | dev |

### testarch/ - Test Architect Workflows

| Workflow | Description | Agent |
|----------|-------------|-------|
| `atdd` | Generate failing acceptance tests before implementation (TDD) | tea |
| `automate` | Expand test automation coverage | tea |
| `ci` | Scaffold CI/CD quality pipeline | tea |
| `framework` | Initialize production-ready test framework | tea |
| `nfr-assess` | Assess non-functional requirements before release | tea |
| `test-design` | System-level or epic-level test planning (auto-detects mode) | tea |
| `test-review` | Review test quality with best practices validation | tea |
| `trace` | Generate requirements-to-tests traceability matrix | tea |

### excalidraw-diagrams/ - Diagram Generation Workflows

| Workflow | Description |
|----------|-------------|
| `create-dataflow` | Create data flow diagrams in Excalidraw format |
| `create-diagram` | Create system architecture, ERD, UML diagrams |
| `create-flowchart` | Create flowcharts for processes/pipelines |
| `create-wireframe` | Create website/app wireframes |

### Other Workflows

| Workflow | Description |
|----------|-------------|
| `document-project` | Analyze and document brownfield projects |
| `generate-project-context` | Create concise project-context.md for AI agents |
| `workflow-status` | Master router and status tracker |
| `workflow-status/init` | Initialize new BMM project |

---

## Workflow File Patterns

### Pattern A: Step-File Architecture (Markdown)

Used by planning/solutioning workflows with extensive user interaction.

```
workflow-name/
  workflow.md           # Main entry point (initialization, role definition)
  steps/
    step-01-init.md     # First step (may have step-01b-continue.md)
    step-02-*.md        # Subsequent steps
    ...
    step-NN-complete.md # Final step
  template.md           # Output document template (if applicable)
  data/                 # CSV files, reference data (if applicable)
```

**Key characteristics:**
- Micro-file design: Each step is self-contained
- Just-in-time loading: Only current step in memory
- Sequential enforcement: No skipping or optimization
- State tracking: `stepsCompleted` array in output frontmatter
- Append-only building: Document built incrementally

**Step file structure:**
```markdown
---
name: 'step-XX-name'
description: 'Step description'
nextStepFile: '{workflow_path}/steps/step-XX+1-name.md'
---

# Step XX: Title

## STEP GOAL:
## MANDATORY EXECUTION RULES:
## EXECUTION PROTOCOLS:
## CONTEXT BOUNDARIES:
## Sequence of Instructions:
## Present MENU OPTIONS:
## CRITICAL STEP COMPLETION NOTE:
## SUCCESS/FAILURE METRICS:
```

### Pattern B: YAML + Instructions (Implementation Workflows)

Used by implementation phase workflows with less interactive, more automated execution.

```
workflow-name/
  workflow.yaml         # Configuration and variable definitions
  instructions.md       # Execution instructions (often XML-based workflow)
  checklist.md          # Validation checklist
  template.md           # Output template (if applicable)
```

**Workflow.yaml structure:**
```yaml
name: workflow-name
description: "..."
config_source: "{project-root}/_bmad/bmm/config.yaml"
installed_path: "{project-root}/_bmad/bmm/workflows/..."
instructions: "{installed_path}/instructions.md"
validation: "{installed_path}/checklist.md"
template: "{installed_path}/template.md"
variables:
  story_dir: "..."
input_file_patterns:
  architecture:
    whole: "{planning_artifacts}/*architecture*.md"
    sharded: "{planning_artifacts}/*architecture*/*.md"
    load_strategy: "FULL_LOAD|SELECTIVE_LOAD"
standalone: true
context_enhancement:
  enabled: "{config_source}:context_hub.enabled"
  memory_query: "..."
  serena_enabled: true|false
  context7_enabled: true|false
```

### Pattern C: XML Workflow Instructions

Used within instruction files for precise step control.

```xml
<workflow>
  <step n="1" goal="Step goal">
    <action>Do something</action>
    <check if="condition">
      <action>Conditional action</action>
    </check>
    <ask>User prompt?</ask>
    <output>Display text</output>
    <template-output>variable = {{value}}</template-output>
  </step>
</workflow>
```

---

## Phase Flow Diagram

```
                    ┌─────────────────────────────────────────────────┐
                    │           WORKFLOW INITIALIZATION               │
                    │              workflow-init                       │
                    │  (Determines level, type, creates status file)  │
                    └─────────────────────────────────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
               BROWNFIELD             GREENFIELD           QUICK-FLOW
                    │                     │                     │
                    ▼                     │                     ▼
          ┌─────────────────┐             │           ┌─────────────────┐
          │ PHASE 0         │             │           │ create-tech-spec│
          │ document-project│             │           │       OR        │
          └────────┬────────┘             │           │   quick-dev     │
                   │                      │           └─────────────────┘
                   ▼                      ▼
          ┌────────────────────────────────────────────────────────────┐
          │                    PHASE 1: ANALYSIS (Optional)            │
          │  brainstorm-project  │  research  │  create-product-brief  │
          └────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
          ┌────────────────────────────────────────────────────────────┐
          │                    PHASE 2: PLANNING                       │
          │              prd (required) → create-ux-design (if UI)     │
          └────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
          ┌────────────────────────────────────────────────────────────┐
          │                   PHASE 3: SOLUTIONING                     │
          │  create-architecture → create-epics-and-stories            │
          │       ↓                          ↓                         │
          │  test-design (optional)   check-implementation-readiness   │
          │                              (GATE CHECK)                  │
          └────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
          ┌────────────────────────────────────────────────────────────┐
          │                  PHASE 4: IMPLEMENTATION                   │
          │                                                            │
          │  sprint-planning ──────────────────────────────────────┐   │
          │         │                                              │   │
          │         ▼                                              │   │
          │  ┌──────────────────────────────────────────────┐     │   │
          │  │           SPRINT LOOP (per epic)             │     │   │
          │  │                                              │     │   │
          │  │  sprint-status ─────────────┐                │     │   │
          │  │       │                     │                │     │   │
          │  │       ▼                     ▼                │     │   │
          │  │  create-story ───────► dev-story             │     │   │
          │  │       │                     │                │     │   │
          │  │       │                     ▼                │     │   │
          │  │       │              code-review             │     │   │
          │  │       │                     │                │     │   │
          │  │       └─────────────────────┘                │     │   │
          │  │                     │                        │     │   │
          │  │              (story done?)                   │     │   │
          │  │               yes ↓  no ↑                    │     │   │
          │  │                     │                        │     │   │
          │  │              (epic done?)                    │     │   │
          │  │                yes │                         │     │   │
          │  │                    ▼                         │     │   │
          │  │             retrospective                    │     │   │
          │  │                    │                         │     │   │
          │  │            (next epic?)                      │     │   │
          │  │              yes │ no │                      │     │   │
          │  │                  │    └── PROJECT COMPLETE   │     │   │
          │  │                  └────────────┘              │     │   │
          │  └──────────────────────────────────────────────┘     │   │
          │                                                        │   │
          │  ┌────────────────────────────────────────────────┐   │   │
          │  │          CHANGE MANAGEMENT                      │   │   │
          │  │  correct-course (when significant changes)      │   │   │
          │  └────────────────────────────────────────────────┘   │   │
          │                                                        │   │
          │  ┌────────────────────────────────────────────────┐   │   │
          │  │          TEST ARCHITECT WORKFLOWS               │   │   │
          │  │  atdd, automate, ci, framework, nfr-assess,    │   │   │
          │  │  test-design, test-review, trace               │   │   │
          │  └────────────────────────────────────────────────┘   │   │
          └────────────────────────────────────────────────────────────┘
```

---

## Individual Workflow Details

### 1-analysis/create-product-brief

**Entry Point:** `workflow.md`

**Steps:**
1. `step-01-init.md` - Initialize workflow, discover input documents
2. `step-01b-continue.md` - Handle workflow continuation
3. `step-02-vision.md` - Product vision discovery
4. `step-03-users.md` - User personas and needs
5. `step-04-metrics.md` - Success metrics definition
6. `step-05-scope.md` - Scope definition
7. `step-06-complete.md` - Completion and summary

**Template:** `product-brief.template.md`

**Output:** `{planning_artifacts}/product-brief-{project_name}-{date}.md`

---

### 1-analysis/research

**Entry Point:** `workflow.md`

**Research Types (Routes to):**
- **Market Research:** `market-steps/step-01-init.md` through `step-06-research-completion.md`
- **Domain Research:** `domain-steps/step-01-init.md` through `step-06-research-synthesis.md`
- **Technical Research:** `technical-steps/step-01-init.md` through `step-06-research-synthesis.md`

**Template:** `research.template.md`

**Output:** `{planning_artifacts}/research/{type}-{topic}-research-{date}.md`

**Prerequisite:** Web search capability required

---

### 2-plan-workflows/prd

**Entry Point:** `workflow.md`

**Steps:**
1. `step-01-init.md` - Initialize, discover inputs
2. `step-01b-continue.md` - Continuation handler
3. `step-02-discovery.md` - Project discovery
4. `step-03-success.md` - Success criteria
5. `step-04-journeys.md` - User journeys
6. `step-05-domain.md` - Domain requirements
7. `step-06-innovation.md` - Innovation analysis
8. `step-07-project-type.md` - Project type classification
9. `step-08-scoping.md` - Scope definition
10. `step-09-functional.md` - Functional requirements
11. `step-10-nonfunctional.md` - Non-functional requirements
12. `step-11-complete.md` - Completion

**Data Files:**
- `domain-complexity.csv`
- `project-types.csv`

**Template:** `prd-template.md`

**Output:** `{planning_artifacts}/prd.md`

---

### 2-plan-workflows/create-ux-design

**Entry Point:** `workflow.md`

**Steps:**
1. `step-01-init.md` / `step-01b-continue.md`
2. `step-02-discovery.md`
3. `step-03-core-experience.md`
4. `step-04-emotional-response.md`
5. `step-05-inspiration.md`
6. `step-06-design-system.md`
7. `step-07-defining-experience.md`
8. `step-08-visual-foundation.md`
9. `step-09-design-directions.md`
10. `step-10-user-journeys.md`
11. `step-11-component-strategy.md`
12. `step-12-ux-patterns.md`
13. `step-13-responsive-accessibility.md`
14. `step-14-complete.md`

**Template:** `ux-design-template.md`

---

### 3-solutioning/create-architecture

**Entry Point:** `workflow.md`

**Steps:**
1. `step-01-init.md` / `step-01b-continue.md`
2. `step-02-context.md`
3. `step-03-starter.md`
4. `step-04-decisions.md`
5. `step-05-patterns.md`
6. `step-06-structure.md`
7. `step-07-validation.md`
8. `step-08-complete.md`

**Data Files:**
- `data/domain-complexity.csv`
- `data/project-types.csv`

**Template:** `architecture-decision-template.md`

---

### 3-solutioning/create-epics-and-stories

**Entry Point:** `workflow.md`

**Steps:**
1. `step-01-validate-prerequisites.md`
2. `step-02-design-epics.md`
3. `step-03-create-stories.md`
4. `step-04-final-validation.md`

**Template:** `templates/epics-template.md`

---

### 3-solutioning/check-implementation-readiness

**Entry Point:** `workflow.md`

**Steps:**
1. `step-01-document-discovery.md`
2. `step-02-prd-analysis.md`
3. `step-03-epic-coverage-validation.md`
4. `step-04-ux-alignment.md`
5. `step-05-epic-quality-review.md`
6. `step-06-final-assessment.md`

**Template:** `templates/readiness-report-template.md`

**Verdicts:** READY | NEEDS WORK | NOT READY

---

### 4-implementation/sprint-planning

**Files:** `workflow.yaml`, `instructions.md`, `checklist.md`

**Template:** `sprint-status-template.yaml`

**Output:** `{implementation_artifacts}/sprint-status.yaml`

---

### 4-implementation/sprint-status

**Files:** `workflow.yaml`, `instructions.md`

**Modes:**
- `interactive` (default): Display status and offer actions
- `validate`: Check if workflow should proceed
- `data`: Extract specific information
- `init-check`: Simple existence check
- `update`: Centralized status file updates

**Actions Menu:**
1. Run recommended workflow now
2. Show all stories grouped by status
3. Show raw sprint-status.yaml
4. Exit

---

### 4-implementation/create-story

**Files:** `workflow.yaml`, `instructions.xml`, `checklist.md`, `template.md`

**Output:** `{story_dir}/{story_key}.md`

---

### 4-implementation/dev-story

**Files:** `workflow.yaml`, `instructions.xml`, `checklist.md`

**Context Enhancement:** Serena (code navigation), Context7 (framework APIs)

---

### 4-implementation/code-review

**Files:** `workflow.yaml`, `instructions.xml`, `checklist.md`

**Purpose:** ADVERSARIAL senior developer review - must find 3-10 issues per story

**Outcomes:** Approve | Changes Requested | Blocked

---

### 4-implementation/correct-course

**Files:** `workflow.yaml`, `instructions.md`, `checklist.md`

**User Mode Selection:**
- **Incremental** (recommended): Refine each edit collaboratively
- **Batch**: Present all changes at once

**Scope Classification:** Minor | Moderate | Major

---

### 4-implementation/retrospective

**Files:** `workflow.yaml`, `instructions.md`

**Two-part structure:**
1. Epic Review (what went well/didn't)
2. Next Epic Preparation

**Party Mode:** All agent dialogue uses "Name (Role): dialogue" format

---

### bmad-quick-flow/create-tech-spec

**Entry Point:** `workflow.md`

**Steps:**
1. `step-01-understand.md`
2. `step-02-investigate.md`
3. `step-03-generate.md`
4. `step-04-review.md`

**Template:** `tech-spec-template.md`

**Ready for Development Standard:**
- Actionable: Every task has clear file path and action
- Logical: Tasks ordered by dependency
- Testable: All ACs follow Given/When/Then
- Complete: No placeholders or "TBD"
- Self-Contained: Fresh agent can implement without history

---

### bmad-quick-flow/quick-dev

**Entry Point:** `workflow.md`

**Steps:**
1. `step-01-mode-detection.md`
2. `step-02-context-gathering.md`
3. `step-03-execute.md`
4. `step-04-self-check.md`
5. `step-05-adversarial-review.md`
6. `step-06-resolve-findings.md`

---

### workflow-status/init (workflow-init)

**Files:** `workflow.yaml`, `instructions.md`

**Output:** `{planning_artifacts}/bmm-workflow-status.yaml`

**Path Files Available:**
- `paths/method-greenfield.yaml`
- `paths/method-brownfield.yaml`
- `paths/enterprise-greenfield.yaml`
- `paths/enterprise-brownfield.yaml`

---

## Menu Patterns

### [C] Continue Pattern

Used in step-file workflows to proceed to next step:

```markdown
### Present MENU OPTIONS

"[C] Continue - Save this and move to {next step name} (Step X of Y)"

#### Menu Handling Logic:
- IF C: Update frontmatter, load next step
- IF user provides additional input: Handle and redisplay menu
- IF user asks questions: Answer and redisplay menu

#### EXECUTION RULES:
- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
```

### [A][P][C] Pattern

Used for checkpoint options in collaborative workflows:

```
[A] Approve - Accept current section
[P] Propose changes - Suggest modifications
[C] Continue - Proceed as-is
```

### [Y][N] Pattern

Simple yes/no decisions:

```
Continue with incomplete epic? (yes/no)
Do you approve this Sprint Change Proposal? (yes/no/revise)
```

### Numbered Menu Options

Used in status/routing workflows:

```markdown
Pick an option:
1) Run recommended workflow now
2) Show all stories grouped by status
3) Show raw sprint-status.yaml
4) Exit
Choice:
```

### Choice Selection Pattern

```markdown
What would you like to do?

1. **Start next workflow** - {workflow_name} ({agent})
2. **Run optional workflow** - Choose from available options
3. **View full status YAML** - See complete status file
4. **Update workflow status** - Mark workflow completed/skipped
5. **Exit** - Return to agent

Your choice:
```

---

## Validation Workflows

### Primary Gate Check: check-implementation-readiness

**Purpose:** Validate PRD + Architecture + Epics + UX alignment before Phase 4

**Verdicts:**
- **READY**: All documents complete and aligned, proceed to implementation
- **NEEDS WORK**: Issues identified but addressable
- **NOT READY**: Critical gaps prevent implementation

**Steps analyze:**
1. Document discovery and loading
2. PRD analysis and completeness
3. Epic coverage validation (all requirements traced)
4. UX alignment (if UI exists)
5. Epic quality review
6. Final assessment with recommendations

---

### Test Architect Validation Workflows

#### testarch-trace (Traceability)

**Verdicts:** PASS | CONCERNS | FAIL | WAIVED

**Purpose:** Generate requirements-to-tests traceability matrix

**Gate Types:** story | epic | release | hotfix

**Decision Modes:**
- `deterministic`: Rule-based automatic decision
- `manual`: Team decision required

---

#### testarch-nfr (NFR Assessment)

**Purpose:** Assess non-functional requirements (performance, security, reliability, maintainability)

**Produces:** Evidence-based validation report

---

#### testarch-test-review

**Purpose:** Review test quality using comprehensive knowledge base

**Produces:** Test quality assessment with best practices validation

---

### Code Review Validation

**Location:** `4-implementation/code-review`

**Approach:** ADVERSARIAL - must find 3-10 specific problems per story

**Review Areas:**
- Code quality
- Test coverage
- Architecture compliance
- Security
- Performance

**Outcomes:** Approve | Changes Requested | Blocked

**Checklist validates:**
- Story file loaded and status verified
- Epic and Story IDs resolved
- Architecture/standards docs loaded
- Tech stack detected
- Acceptance Criteria cross-checked
- Tests mapped to ACs
- Security review performed
- Outcome decided and documented

---

## Flow Connections

### Workflow Path Definitions

Paths are defined in `workflow-status/paths/` and determine which workflows are required/optional:

#### method-greenfield.yaml

```
Phase 1 (Optional Analysis):
  - brainstorm-project (optional)
  - research (optional)
  - product-brief (optional)

Phase 2 (Planning):
  - prd (required)
  - create-ux-design (conditional: if_has_ui)

Phase 3 (Solutioning):
  - create-architecture (required)
  - create-epics-and-stories (required)
  - test-design (optional)
  - implementation-readiness (required - GATE)

Phase 4 (Implementation):
  - sprint-planning (required)
  [Sprint loop managed by sprint-status.yaml]
```

#### method-brownfield.yaml

```
Phase 0 (Documentation - conditional: if_undocumented):
  - document-project (required)

Phase 1-4: Same as greenfield
```

### Sprint Loop Flow

```
sprint-planning creates sprint-status.yaml
       │
       ▼
sprint-status reads status → recommends next workflow:
       │
       ├── in-progress story → dev-story
       ├── review story → code-review
       ├── ready-for-dev story → dev-story
       ├── backlog story → create-story
       ├── optional retrospective → retrospective
       └── all done → workflow-status
```

### Workflow Invocation Methods

1. **Skill/Command invocation:**
   ```
   /bmad:bmm:workflows:{workflow-id}
   ```

2. **Status-based recommendation:**
   - `workflow-status` recommends next workflow
   - `sprint-status` recommends next implementation workflow

3. **Workflow-to-workflow handoff:**
   - Completion steps suggest next workflows
   - Path files define required sequence

### Context Hub Integration

All workflows can optionally integrate with:

- **Forgetful MCP:** Query/save semantic memories
- **Serena:** LSP-powered code analysis
- **Context7:** Framework documentation lookup

Configuration in each workflow.yaml:
```yaml
context_enhancement:
  enabled: "{config_source}:context_hub.enabled"
  memory_query: "..."
  memory_context: "..."
  serena_enabled: true|false
  serena_purpose: "..."
  context7_enabled: true|false
  context7_purpose: "..."
```

---

## Summary

The BMM workflow system provides:

1. **Phased methodology** from analysis through implementation
2. **Flexible paths** for greenfield/brownfield and different project scales
3. **Step-file architecture** for interactive planning workflows
4. **YAML + instructions** for automated implementation workflows
5. **Gate checks** at critical transitions (implementation-readiness)
6. **Status tracking** via workflow-status.yaml and sprint-status.yaml
7. **Menu patterns** for user interaction ([C], [A][P][C], [Y][N], numbered)
8. **Test architect workflows** for quality assurance throughout
9. **Context Hub integration** for memory, code analysis, and documentation
