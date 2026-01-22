# BMAD Workflow Maps

**Created:** 2026-01-09
**Purpose:** Comprehensive flow documentation for all BMAD modules

---

## Table of Contents

1. [BMAD Module Overview](#bmad-module-overview)
2. [Core Module Workflows](#core-module-workflows)
3. [BMM Module Workflows](#bmm-module-workflows)
4. [BMB Module Workflows](#bmb-module-workflows)
5. [Cross-Module Integration](#cross-module-integration)

---

## BMAD Module Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BMAD FRAMEWORK                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐            │
│  │    CORE     │     │      BMM        │     │      BMB        │            │
│  │  Foundation │     │  Method Module  │     │  Builder Module │            │
│  ├─────────────┤     ├─────────────────┤     ├─────────────────┤            │
│  │ brainstorm  │     │ Phase 0-4       │     │ Agent Builder   │            │
│  │ party-mode  │     │ Workflows       │     │ Module Builder  │            │
│  │ bmad-master │     │ 9 Agents        │     │ Workflow Builder│            │
│  └─────────────┘     └─────────────────┘     └─────────────────┘            │
│         │                    │                       │                      │
│         └────────────────────┼───────────────────────┘                      │
│                              │                                              │
│                    ┌─────────▼─────────┐                                    │
│                    │   _bmad/_config   │                                    │
│                    │  Agent Manifest   │                                    │
│                    │  Workflow Manifest│                                    │
│                    └───────────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Module Locations

| Module | Path | Purpose |
|--------|------|---------|
| Core | `_bmad/core/` | Foundation workflows (brainstorming, party-mode) |
| BMM | `_bmad/bmm/` | Method workflows (phases 0-4, project management) |
| BMB | `_bmad/bmb/` | Builder workflows (agents, modules, workflows) |
| Config | `_bmad/_config/` | Manifests and configuration |

---

## Core Module Workflows

### Brainstorming Workflow

**Location:** `_bmad/core/workflows/brainstorming/`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BRAINSTORMING WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │ step-01          │   Session Setup                                       │
│  │ session-setup    │   - Define topic, goals, constraints                  │
│  └────────┬─────────┘   - Set session parameters                            │
│           │                                                                 │
│           ▼                                                                 │
│  ┌──────────────────┐                                                       │
│  │ step-01b         │   Continue (Optional)                                 │
│  │ continue         │   - Resume previous session                           │
│  └────────┬─────────┘                                                       │
│           │                                                                 │
│           ▼                                                                 │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │                   TECHNIQUE SELECTION (Step 2)               │           │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────┐ │           │
│  │  │ step-02a   │  │ step-02b   │  │ step-02c   │  │step-02d │ │           │
│  │  │ user-      │  │ ai-        │  │ random-    │  │progress-│ │           │
│  │  │ selected   │  │ recommended│  │ selection  │  │ive-flow │ │           │
│  │  └────────────┘  └────────────┘  └────────────┘  └─────────┘ │           │
│  └──────────────────────────┬───────────────────────────────────┘           │
│                             │                                               │
│                             ▼                                               │
│  ┌──────────────────┐                                                       │
│  │ step-03          │   Technique Execution                                 │
│  │ technique-       │   - Execute ONE element at a time                     │
│  │ execution        │   - CONTINUOUS interaction checks                     │
│  └────────┬─────────┘   - "Continue with technique?" prompts                │
│           │                                                                 │
│           ▼                                                                 │
│  ┌──────────────────┐                                                       │
│  │ step-04          │   Idea Organization                                   │
│  │ idea-            │   - Organize generated ideas                          │
│  │ organization     │   - Create action plans                               │
│  └──────────────────┘   - Output to session document                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Files:**
- `workflow.md` - Main workflow definition
- `steps/step-01-session-setup.md`
- `steps/step-01b-continue.md`
- `steps/step-02a-user-selected.md`
- `steps/step-02b-ai-recommended.md`
- `steps/step-02c-random-selection.md`
- `steps/step-02d-progressive-flow.md`
- `steps/step-03-technique-execution.md`
- `steps/step-04-idea-organization.md`
- `data/brain-methods.csv` - Technique library

**Interaction Pattern:** HIGHEST frequency - continuous checks after each technique element

---

### Party Mode Workflow

**Location:** `_bmad/core/workflows/party-mode/`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PARTY MODE WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Human provides initial topic                                                │
│           │                                                                  │
│           ▼                                                                  │
│  ┌──────────────────┐                                                        │
│  │ step-01          │   Agent Loading                                        │
│  │ agent-loading    │   - Load agent manifest                                │
│  └────────┬─────────┘   - Prepare agent roster                               │
│           │                                                                  │
│           ▼                                                                  │
│  ┌──────────────────┐                                                        │
│  │ step-02          │   Discussion Orchestration                             │
│  │ discussion-      │   - AUTO-SELECT 2-3 relevant agents                    │
│  │ orchestration    │   - Agents respond AUTONOMOUSLY                        │
│  └────────┬─────────┘   - Cross-talk between agents                          │
│           │             - Loop until exit signal                             │
│           │                                                                  │
│           │  ◄──────────────────────────────────────┐                        │
│           │         (Agents auto-continue)          │                        │
│           │                                         │                        │
│           ▼                                         │                        │
│  ┌──────────────────┐                               │                        │
│  │ Exit Check       │   User sends exit signal?     │                        │
│  │                  │   - "*exit"                   │                        │
│  │                  │   - "goodbye"          NO ────┘                        │
│  │                  │   - "end party"                                        │
│  └────────┬─────────┘   - "quit"                                             │
│           │ YES                                                              │
│           ▼                                                                  │
│  ┌──────────────────┐                                                        │
│  │ step-03          │   Graceful Exit                                        │
│  │ graceful-exit    │   - Save discussion to memory (if configured)          │
│  └──────────────────┘   - Session ends                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

EXIT TRIGGERS (exact strings):
  - "*exit"      (literal asterisk)
  - "goodbye"
  - "end party"
  - "quit"

AGENT SELECTION (automatic):
  - Orchestrator analyzes topic
  - Selects 2-3 most relevant agents
  - Primary, Secondary, (Tertiary) roles
```

**Key Files:**
- `workflow.md` - Main workflow with exit_triggers defined
- `steps/step-01-agent-loading.md`
- `steps/step-02-discussion-orchestration.md`
- `steps/step-03-graceful-exit.md`

**Interaction Pattern:** AUTONOMOUS per round - human provides topic and exit only

---

## BMM Module Workflows

### Phase Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BMM PHASE PROGRESSION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  GREENFIELD PATH (method-greenfield.yaml)                                    │
│  ════════════════════════════════════════                                    │
│                                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
│  │  Phase 1    │   │  Phase 2    │   │  Phase 3    │   │  Phase 4    │      │
│  │  Analysis   │──▶│  Planning   │──▶│ Solutioning │──▶│Implementation│      │
│  │ (Optional)  │   │ (Required)  │   │ (Required)  │   │ (Required)  │      │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘      │
│                                                                              │
│  BROWNFIELD PATH (method-brownfield.yaml)                                    │
│  ═════════════════════════════════════════                                   │
│                                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
│  │  Phase 0    │   │  Phase 1    │   │  Phase 2    │   │  Phase 3-4  │      │
│  │Documentation│──▶│  Analysis   │──▶│  Planning   │──▶│  (same as   │      │
│  │(if needed)  │   │ (Optional)  │   │ (Required)  │   │  greenfield)│      │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 0: Documentation (Brownfield Only)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 0: DOCUMENTATION (if_undocumented)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────┐                                                  │
│  │ document-project       │   Agent: analyst                                 │
│  │ /bmad:bmm:workflows:   │   - Scan codebase structure                      │
│  │ document-project       │   - Identify patterns and architecture           │
│  └────────────────────────┘   - Generate project documentation               │
│                               - Create project-context.md                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: Analysis (Optional)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: ANALYSIS (Optional - user_choice)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────┐                                                 │
│  │ brainstorm-project     │   Agent: analyst                                │
│  │ (uses Core brainstorm) │   - Creative exploration                        │
│  └────────────────────────┘   - Uses brainstorm-context.md                  │
│                                                                             │
│  ┌────────────────────────┐                                                 │
│  │ research               │   Agent: analyst                                │
│  │ /bmad:bmm:workflows:   │   - Market/technical/domain research            │
│  │ research               │   - Can run multiple times                      │
│  └────────────────────────┘                                                 │
│                                                                             │
│  ┌────────────────────────┐                                                 │
│  │ create-product-brief   │   Agent: analyst                                │
│  │ /bmad:bmm:workflows:   │   - Recommended for greenfield                  │
│  │ create-product-brief   │   - High-level product vision                   │
│  └────────────────────────┘                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 2: Planning (Required)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: PLANNING (Required)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────┐                                                  │
│  │ create-prd             │   Agent: pm (John)                               │
│  │ /bmad:bmm:workflows:   │   - Product Requirements Document                │
│  │ create-prd             │   - FRs and NFRs                                 │
│  └──────────┬─────────────┘   - Required                                     │
│             │                                                                │
│             ▼                                                                │
│  ┌────────────────────────┐                                                  │
│  │ create-ux-design       │   Agent: ux-designer (Sally)                     │
│  │ /bmad:bmm:workflows:   │   - Conditional: if_has_ui                       │
│  │ create-ux-design       │   - UX patterns and wireframes                   │
│  └────────────────────────┘                                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 3: Solutioning (Required)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: SOLUTIONING (Required)                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────┐                                                  │
│  │ create-architecture    │   Agent: architect (Winston)                     │
│  │ /bmad:bmm:workflows:   │   - System architecture document                 │
│  │ create-architecture    │   - Required                                     │
│  └──────────┬─────────────┘                                                  │
│             │                                                                │
│             ▼                                                                │
│  ┌────────────────────────┐                                                  │
│  │ create-epics-stories   │   Agent: pm (John)                               │
│  │ /bmad:bmm:workflows:   │   - Break down PRD into epics/stories            │
│  │ create-epics-and-      │   - Full context (PRD + UX + Architecture)       │
│  │ stories                │   - Required                                     │
│  └──────────┬─────────────┘                                                  │
│             │                                                                │
│             ▼                                                                │
│  ┌────────────────────────┐                                                  │
│  │ test-design            │   Agent: tea (Murat)                             │
│  │ /bmad:bmm:workflows:   │   - System-level testability review              │
│  │ testarch-test-design   │   - Optional                                     │
│  └──────────┬─────────────┘                                                  │
│             │                                                                │
│             ▼                                                                │
│  ┌────────────────────────┐                                                  │
│  │ check-implementation-  │   Agent: architect (Winston)                     │
│  │ readiness              │   - Validates PRD + Arch + Epics + UX            │
│  │ /bmad:bmm:workflows:   │   - Required GATE                                │
│  │ check-implementation-  │                                                  │
│  │ readiness              │   VERDICTS:                                      │
│  └────────────────────────┘   - READY → proceed                              │
│                               - NEEDS WORK → human review                    │
│                               - NOT READY → fix issues                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 4: Implementation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: IMPLEMENTATION                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────┐                                                  │
│  │ sprint-planning        │   Agent: sm (Bob)                                │
│  │ /bmad:bmm:workflows:   │   - Creates sprint-status.yaml                   │
│  │ sprint-planning        │   - Extracts all epics/stories                   │
│  └──────────┬─────────────┘   - Required                                     │
│             │                                                                │
│             ▼                                                                │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                    SPRINT EXECUTION LOOP                         │        │
│  │                                                                  │        │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐         │        │
│  │  │ create-story │──▶│  dev-story   │──▶│ code-review  │         │        │
│  │  │ (sm)         │   │  (dev)       │   │ (reviewer)   │         │        │
│  │  └──────────────┘   └──────────────┘   └──────────────┘         │        │
│  │         │                                      │                 │        │
│  │         │                                      ▼                 │        │
│  │         │                          ┌──────────────────┐         │        │
│  │         │                          │ Code Review      │         │        │
│  │         │                          │ **ADVERSARIAL**  │         │        │
│  │         │                          │ 3-10 findings    │         │        │
│  │         │                          │ required. Then:  │         │        │
│  │         │                          │ - Approve        │         │        │
│  │         │                          │ - Changes Req'd  │         │        │
│  │         │                          │ - Blocked        │         │        │
│  │         │                          └──────────────────┘         │        │
│  │         │                                                        │        │
│  │         └──────── (next story) ◄─────────────────────────────────┤        │
│  │                                                                  │        │
│  │  ┌──────────────┐   ┌──────────────┐                            │        │
│  │  │correct-course│   │retrospective │   After epic completion    │        │
│  │  │ (if needed)  │   │ (optional)   │                            │        │
│  │  └──────────────┘   └──────────────┘                            │        │
│  │                                                                  │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                              │
│  STATUS STATE MACHINES:                                                      │
│  ──────────────────────                                                      │
│  Epic:    backlog → in-progress → done                                       │
│  Story:   backlog → ready-for-dev → in-progress → review → done             │
│  Retro:   optional ↔ done                                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### TestArch Workflows

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TESTARCH WORKFLOWS (Test Architecture)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Location: _bmad/bmm/workflows/testarch/                                     │
│                                                                              │
│  ┌────────────────┐                                                          │
│  │ testarch-atdd  │   Generate failing acceptance tests (TDD red phase)      │
│  └────────────────┘                                                          │
│                                                                              │
│  ┌────────────────┐                                                          │
│  │testarch-automate│  Expand test automation coverage                        │
│  └────────────────┘                                                          │
│                                                                              │
│  ┌────────────────┐                                                          │
│  │ testarch-ci    │   Scaffold CI/CD quality pipeline                        │
│  └────────────────┘                                                          │
│                                                                              │
│  ┌────────────────┐                                                          │
│  │testarch-framework│ Initialize test framework (Playwright/Cypress)        │
│  └────────────────┘                                                          │
│                                                                              │
│  ┌────────────────┐                                                          │
│  │ testarch-nfr   │   Assess non-functional requirements                     │
│  └────────────────┘                                                          │
│                                                                              │
│  ┌────────────────┐                                                          │
│  │testarch-test-  │   Dual-mode: System-level OR Epic-level test planning   │
│  │design          │                                                          │
│  └────────────────┘                                                          │
│                                                                              │
│  ┌────────────────┐                                                          │
│  │testarch-test-  │   Review test quality against best practices             │
│  │review          │                                                          │
│  └────────────────┘                                                          │
│                                                                              │
│  ┌────────────────┐   VERDICTS: PASS / CONCERNS / FAIL / WAIVED             │
│  │ testarch-trace │   Requirements-to-tests traceability matrix              │
│  └────────────────┘   Quality gate decision                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### BMM Agents

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BMM AGENTS                                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┬──────────┬─────────────────────────────────────────────┐   │
│  │ Agent ID    │ Name     │ Role                                        │   │
│  ├─────────────┼──────────┼─────────────────────────────────────────────┤   │
│  │ analyst     │ Mary     │ Business Analyst + Requirements Expert      │   │
│  │ architect   │ Winston  │ System Architect + Technical Design Leader  │   │
│  │ dev         │ Amelia   │ Senior Software Engineer                    │   │
│  │ pm          │ John     │ Product Manager                             │   │
│  │ quick-flow- │ Barry    │ Elite Full-Stack Developer (Quick Flow)     │   │
│  │ solo-dev    │          │                                             │   │
│  │ sm          │ Bob      │ Scrum Master + Story Preparation            │   │
│  │ tea         │ Murat    │ Master Test Architect                       │   │
│  │ tech-writer │ Paige    │ Technical Documentation Specialist          │   │
│  │ ux-designer │ Sally    │ User Experience Designer + UI Specialist    │   │
│  └─────────────┴──────────┴─────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## BMB Module Workflows

### Agent Workflow (Tri-Modal)

**Location:** `_bmad/bmb/workflows/agent/`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BMB AGENT WORKFLOW (TRI-MODAL)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                        MODE SELECTION                            │        │
│  │                                                                  │        │
│  │   [C]reate ──────────▶ steps-c/ (16 files)                      │        │
│  │   [E]dit   ──────────▶ steps-e/ (22 files)                      │        │
│  │   [V]alidate ────────▶ steps-v/ (7 files)                       │        │
│  │                                                                  │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### CREATE Mode Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CREATE MODE (steps-c/)                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐                                                        │
│  │ step-01          │   Brainstorm (Optional)                                │
│  │ brainstorm       │   - Uses Core brainstorming workflow                   │
│  └────────┬─────────┘   - "Would you like to brainstorm agent ideas?"        │
│           │                                                                  │
│           ▼                                                                  │
│  ┌──────────────────┐                                                        │
│  │ step-02          │   Discovery                                            │
│  │ discovery        │   - Understand user's agent vision                     │
│  └────────┬─────────┘   - Gather requirements                                │
│           │                                                                  │
│           ▼                                                                  │
│  ┌──────────────────┐                                                        │
│  │ step-03          │   Type & Metadata                                      │
│  │ type-metadata    │   - Simple / Expert / Module classification            │
│  └────────┬─────────┘   - Define id, name, title, icon, module, hasSidecar   │
│           │                                                                  │
│           ▼                                                                  │
│  ┌──────────────────┐                                                        │
│  │ step-04          │   Persona Development                                  │
│  │ persona          │   - Role, identity, communication style                │
│  └────────┬─────────┘   - Principles and character                           │
│           │                                                                  │
│           ▼                                                                  │
│  ┌──────────────────┐                                                        │
│  │ step-05          │   Commands & Menu                                      │
│  │ commands-menu    │   - Define agent menu structure                        │
│  └────────┬─────────┘   - Command definitions                                │
│           │                                                                  │
│           ▼                                                                  │
│  ┌──────────────────┐                                                        │
│  │ step-06          │   Activation Behavior                                  │
│  │ activation       │   - Define how agent activates                         │
│  └────────┬─────────┘   - Trigger conditions                                 │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                    BUILD STEP (Type-Dependent)                   │        │
│  │                                                                  │        │
│  │  ┌────────────┐   ┌────────────┐   ┌────────────┐               │        │
│  │  │ step-07a   │   │ step-07b   │   │ step-07c   │               │        │
│  │  │ build-     │   │ build-     │   │ build-     │               │        │
│  │  │ simple     │   │ expert     │   │ module     │               │        │
│  │  └────────────┘   └────────────┘   └────────────┘               │        │
│  │                                                                  │        │
│  └──────────────────────────┬──────────────────────────────────────┘        │
│                             │                                                │
│                             ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │              VALIDATION PHASE (6 Separate Step Files)            │        │
│  │                                                                  │        │
│  │  ┌────────────┐   ┌────────────┐   ┌────────────┐               │        │
│  │  │ step-08a   │   │ step-08b   │   │ step-08c   │               │        │
│  │  │ plan-      │──▶│ metadata-  │──▶│ persona-   │               │        │
│  │  │ traceability│   │ validation │   │ validation │               │        │
│  │  └────────────┘   └────────────┘   └────────────┘               │        │
│  │         │                                                        │        │
│  │         ▼                                                        │        │
│  │  ┌────────────┐   ┌────────────┐   ┌────────────┐               │        │
│  │  │ step-08d   │   │ step-08e   │   │ step-08f   │               │        │
│  │  │ menu-      │──▶│ structure- │──▶│ sidecar-   │               │        │
│  │  │ validation │   │ validation │   │ validation │               │        │
│  │  └────────────┘   └────────────┘   └────────────┘               │        │
│  │                                                                  │        │
│  └──────────────────────────┬──────────────────────────────────────┘        │
│                             │                                                │
│                             ▼                                                │
│  ┌──────────────────┐                                                        │
│  │ step-09          │   Celebrate!                                           │
│  │ celebrate        │   - Installation guidance                              │
│  └──────────────────┘   - Success confirmation                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### EDIT Mode Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  EDIT MODE (steps-e/)                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  e-01: load-existing      Load existing agent file                           │
│    │                                                                         │
│    ▼                                                                         │
│  e-02: discover-changes   What does user want to change?                     │
│    │                                                                         │
│    ▼                                                                         │
│  e-03: pre-edit-validation Validate before editing                           │
│    │                                                                         │
│    ▼                                                                         │
│  e-04: edit-metadata      Edit metadata if needed                            │
│    │                                                                         │
│    ▼                                                                         │
│  e-05: edit-persona       Edit persona if needed                             │
│    │                                                                         │
│    ▼                                                                         │
│  e-06: edit-menu          Edit menu if needed                                │
│    │                                                                         │
│    ▼                                                                         │
│  e-07: edit-activation    Edit activation if needed                          │
│    │                                                                         │
│    ▼                                                                         │
│  e-08: rebuild            Rebuild agent with changes                         │
│    │                                                                         │
│    ▼                                                                         │
│  e-09: post-edit-validation Validate after editing                           │
│    │                                                                         │
│    ▼                                                                         │
│  e-10: celebrate          Success confirmation                               │
│                                                                              │
│  Total: 22 step files (includes sub-steps)                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### VALIDATE Mode Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  VALIDATE MODE (steps-v/)                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  v-01: load-review        Load agent for review                              │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  v-02a through v-02e: Systematic Validation                      │        │
│  │                                                                  │        │
│  │  v-02a: metadata       Check all metadata properties             │        │
│  │  v-02b: persona        Validate persona completeness             │        │
│  │  v-02c: menu           Validate menu structure                   │        │
│  │  v-02d: structure      Check overall agent structure             │        │
│  │  v-02e: sidecar        Validate sidecar if applicable            │        │
│  │                                                                  │        │
│  └──────────────────────────┬──────────────────────────────────────┘        │
│                             │                                                │
│                             ▼                                                │
│  v-03: summary            Generate validation report                         │
│                           Offer option to apply fixes                        │
│                                                                              │
│  Total: 7 step files                                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### BMB Agents

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BMB AGENTS                                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┬──────────┬─────────────────────────────────────────┐   │
│  │ Agent ID        │ Name     │ Role                                    │   │
│  ├─────────────────┼──────────┼─────────────────────────────────────────┤   │
│  │ agent-builder   │ Bond     │ Agent Architecture Specialist           │   │
│  │ module-builder  │ Morgan   │ Module Architecture Specialist          │   │
│  │ workflow-builder│ Wendy    │ Workflow Architecture Specialist        │   │
│  └─────────────────┴──────────┴─────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Cross-Module Integration

### How Modules Connect

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CROSS-MODULE INTEGRATION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CORE ──────────────────────────────────────────────────────────────────    │
│    │                                                                         │
│    ├── brainstorming ────────▶ Used by BMM Phase 1 (brainstorm-project)     │
│    │                          Used by BMB Step 01 (agent brainstorm)         │
│    │                                                                         │
│    ├── party-mode ───────────▶ Available at [P] menu option in any step     │
│    │                          Used for multi-agent discussions               │
│    │                                                                         │
│    └── bmad-master ──────────▶ Master orchestrator for all modules          │
│                                                                              │
│  BMM ──────────────────────────────────────────────────────────────────     │
│    │                                                                         │
│    ├── Agents (9) ───────────▶ Execute workflows in their domain            │
│    │                                                                         │
│    ├── Phase workflows ──────▶ Produce artifacts consumed by next phase     │
│    │   - PRD → Architecture → Epics/Stories → Implementation                │
│    │                                                                         │
│    └── workflow-status ──────▶ Tracks state for all BMM workflows           │
│                                                                              │
│  BMB ──────────────────────────────────────────────────────────────────     │
│    │                                                                         │
│    ├── Agents (3) ───────────▶ Build new agents/modules/workflows           │
│    │                                                                         │
│    └── Built artifacts ──────▶ New agents/workflows added to manifest       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Menu System ([A][P][C])

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MENU SYSTEM                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  EVERY step in BMM/BMB workflows presents a menu after execution:            │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ [Step content displayed here]                                    │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │ [A] Advanced Elicitation - Deep dive into this topic            │        │
│  │ [P] Party Mode - Get multiple agent perspectives                │        │
│  │ [C] Continue - Proceed to next step                             │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                              │
│  [A] = Single-agent deep investigation (if available)                        │
│  [P] = Multi-agent discussion (2-3 agents)                                   │
│  [C] = Proceed to next step                                                  │
│                                                                              │
│  NOTE: Some Core workflows use different menus:                              │
│  - Brainstorming: [C] Continue only                                          │
│  - Party-mode: [E] Exit option                                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Validation Systems

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VALIDATION SYSTEMS                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  BMM VALIDATION (Verdict-Based / Semantic)                                   │
│  ═════════════════════════════════════════                                   │
│                                                                              │
│  ┌────────────────────────┬─────────────────────────────────────────────┐   │
│  │ Workflow               │ Verdicts                                    │   │
│  ├────────────────────────┼─────────────────────────────────────────────┤   │
│  │ check-implementation-  │ READY / NEEDS WORK / NOT READY              │   │
│  │ readiness              │                                             │   │
│  ├────────────────────────┼─────────────────────────────────────────────┤   │
│  │ testarch-trace         │ PASS / CONCERNS / FAIL / WAIVED             │   │
│  ├────────────────────────┼─────────────────────────────────────────────┤   │
│  │ code-review            │ ADVERSARIAL: 3-10 findings → Approve/Chg/Blk│   │
│  └────────────────────────┴─────────────────────────────────────────────┘   │
│                                                                              │
│  BMB VALIDATION (Structural / Syntax)                                        │
│  ═════════════════════════════════════                                       │
│                                                                              │
│  ┌────────────────────────┬─────────────────────────────────────────────┐   │
│  │ Validation Type        │ Checks                                      │   │
│  ├────────────────────────┼─────────────────────────────────────────────┤   │
│  │ 08a plan-traceability  │ Agent plan tracked correctly                │   │
│  │ 08b metadata-validation│ All metadata fields valid                   │   │
│  │ 08c persona-validation │ Persona complete and consistent             │   │
│  │ 08d menu-validation    │ Menu structure correct                      │   │
│  │ 08e structure-validation│ Overall agent structure valid              │   │
│  │ 08f sidecar-validation │ Sidecar config valid (if applicable)        │   │
│  └────────────────────────┴─────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Project Levels

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROJECT LEVELS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────┬─────────────────────┬────────────┬───────────────────────────┐   │
│  │ Level │ Title               │ Stories    │ Documentation             │   │
│  ├───────┼─────────────────────┼────────────┼───────────────────────────┤   │
│  │ 0     │ Single Atomic Change│ 1          │ Minimal - tech spec only  │   │
│  │ 1     │ Small Feature       │ 1-10       │ Tech spec                 │   │
│  │ 2     │ Medium Project      │ 5-15       │ PRD + optional tech spec  │   │
│  │ 3     │ Complex System      │ 12-40      │ PRD + architecture + JIT  │   │
│  │ 4     │ Enterprise Scale    │ 40+        │ PRD + architecture + JIT  │   │
│  └───────┴─────────────────────┴────────────┴───────────────────────────┘   │
│                                                                              │
│  Selection: Via workflow-init → BMad Method (0-2) or Enterprise (3-4)        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

### File Locations

| Component | Path |
|-----------|------|
| Core workflows | `_bmad/core/workflows/` |
| BMM workflows | `_bmad/bmm/workflows/` |
| BMB workflows | `_bmad/bmb/workflows/` |
| Agent manifest | `_bmad/_config/agent-manifest.csv` |
| Workflow manifest | `_bmad/_config/workflow-manifest.csv` |
| Workflow paths | `_bmad/bmm/workflows/workflow-status/paths/` |
| Project levels | `_bmad/bmm/workflows/workflow-status/project-levels.yaml` |

### Workflow Commands

| Workflow | Command |
|----------|---------|
| Brainstorming | `/bmad:core:workflows:brainstorming` |
| Party Mode | `/bmad:core:workflows:party-mode` |
| Create PRD | `/bmad:bmm:workflows:create-prd` |
| Create Architecture | `/bmad:bmm:workflows:create-architecture` |
| Sprint Planning | `/bmad:bmm:workflows:sprint-planning` |
| Code Review | `/bmad:bmm:workflows:code-review` |
| Agent Builder | `/bmad:bmb:workflows:agent` |

---

**Document Version:** 1.0
**Created:** 2026-01-09
**Source:** Comprehensive analysis of `_bmad/` directory structure
