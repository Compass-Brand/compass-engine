# Compass BMAD Extension And Automation Implementation Plan

> **ARCHIVED:** Superseded by the src/-based BMAD upstream migration (see `docs/plans/2026-04-06-bmad-upstream-migration-design.md`). Retained for historical reference only.

Status: archived
Date: 2026-03-11
Model: Reference-first

## Working Assumption

For this planning phase, the real method-development surface is not `src/`.

The active working surfaces are:

- `reference/BMAD/modules/custom/bmm`
- `reference/BMAD/modules/custom/core`
- `reference/BMAD/BMAD-workflow.md`
- `reference/BMAD/research`
- `_planning/current/`

For now, treat these as the place where Compass BMAD is being designed and changed.

Do not treat `src/`, `dist/`, or the repo docs as authoritative for BMAD design until the method is stable enough to productize.

## Objective

Define and implement the next Compass BMAD version inside `reference/BMAD/` first, then decide how to productize it later.

The first implementation track should do six things:

1. Continue extending the existing custom BMAD layer in `reference/BMAD/modules/custom/bmm`.
2. Add the selected CIS, WDS, and CYBERSEC workflows into that working layer.
3. Define the automation layer as reference-stage specs and workflow wrappers, not production runtime assets.
4. Update the reference planning/output model so new artifacts have explicit destinations.
5. Complete the `reference/` planning and documentation framework enough that it can act as a production-ready method-development surface.
6. Defer `src` migration and distribution wiring until the BMAD shape is actually stable.

## What This Plan Is And Is Not

### This plan is

- a method-development plan
- a structure-and-sequencing plan
- a path for evolving the Compass BMAD flow in `reference/`
- a staging plan before productization

### This plan is not

- a `src` migration plan
- a build/distribution plan
- a promise that current repo docs are correct
- a commitment to finalize command/runtime packaging before the method is aligned

## Current Operating Reality

These points are based on what is actually present in the repo right now.

1. `reference/BMAD/modules/custom/bmm` already exists and is the real active custom BMM surface.
2. `reference/BMAD/modules/custom/core` already exists and is the active custom core surface.
3. `reference/BMAD/BMAD-workflow.md` is already being used as the verified canonical workflow order.
4. `reference/BMAD/research` is already the active research corpus for automation and BMAD improvements.
5. `_planning/current/` is the correct place to hold rollout decisions, implementation sequencing, and alignment notes.
6. `src/` is not yet trustworthy as the BMAD implementation surface for this effort.

Because of that, the correct move right now is to keep development in `reference/BMAD/` and keep `src` out of scope until the method is settled.

## Recommended Planning-Phase Source Of Truth

### BMAD method logic

- `reference/BMAD/modules/custom/bmm`
- `reference/BMAD/modules/custom/core`

### Canonical workflow order

- `reference/BMAD/BMAD-workflow.md`

### Workflow catalog and command map

- `reference/BMAD/modules/custom/bmm/module-help.csv`
- `reference/BMAD/modules/custom/core/module-help.csv`

### Research inputs

- `reference/BMAD/research`

### Planning and rollout decisions

- `_planning/current/research`
- `_planning/current/planning`

### Planning framework source of truth

- `reference/planning/framework`
- `reference/planning/docs`

### Documentation framework source of truth

- `reference/documentation`

## Scope For This Reference-First Rollout

### In scope

- extend `reference/BMAD/modules/custom/bmm`
- extend `reference/BMAD/BMAD-workflow.md`
- extend `reference/BMAD/modules/custom/bmm/module-help.csv`
- add CIS workflows
- add WDS workflows
- add CYBERSEC workflows
- define BMAD automation wrapper specs in `reference/BMAD/`
- update reference planning/output mapping where needed

### Out of scope

- migrating BMAD into `src/`
- wiring BMAD into build and push scripts
- runtime `.claude` packaging
- Codex/OpenCode parity
- POV oversight as a default lane
- AI memory as a default lane
- parallel story execution

## Core Recommendation

Do not create a new planning-phase BMAD module right now.

Use the existing working layer:

- `reference/BMAD/modules/custom/bmm`

That gives us the shortest path to real progress because:

- it already exists
- it already has agents, workflows, module metadata, and TEA integration
- it already has a command catalog in `module-help.csv`
- it already has the custom Compass workflow order layered on top in `BMAD-workflow.md`

If we eventually want a renamed or restructured module, that should happen after the workflow set is stable.

## Target End-State For The Planning Phase

At the end of the reference-first rollout, we should have:

1. a revised `reference/BMAD/modules/custom/bmm` with the selected new lanes added
2. a revised `reference/BMAD/BMAD-workflow.md` showing the agreed Compass flow
3. a revised `reference/BMAD/modules/custom/bmm/module-help.csv` with all new workflows and commands
4. a reference-stage automation spec set under `reference/BMAD/tools/automation/`
5. an expanded planning framework that explicitly supports roadmap-level and phase-level BMAD operation
6. a documentation framework update plan that defines how stable planning artifacts graduate into human and AI docs
7. a clear output mapping for new artifacts into the Compass planning structure
8. a separate later-phase productization plan for migrating stable method assets into `src/`

## Current Recommended Compass BMAD Operating Model

Compass should operate as a roadmap-driven BMAD system, not as a one-time MVP pipeline.

The recommended continuous-development model is:

1. Initialization
2. High-Level Analysis
3. Project Roadmap
4. Phase Sync
5. Detailed Analysis
6. Planning and Experience Design
7. Solutioning
8. Implementation
9. Release Gate
10. Phase Closeout and roadmap update

### Why this model is recommended

- It preserves BMAD's strength in ideation and structured delivery.
- It fixes the continuity problem where good early ideas disappear after the MVP is scoped down.
- It gives Compass a persistent project-level roadmap lane plus a repeatable per-phase execution loop.
- It fits the existing planning framework shape of `roadmap/`, `current/`, `previous/`, and `lessons/`.

### Operating rules derived from discussion

1. `Phase Sync` should be the formal roadmap-slice selection and framing workflow. Do not create a separate roadmap-selection workflow unless a future implementation proves that `Phase Sync` is overloaded.
2. Compass should prefer many smaller artifacts over a few large planning documents.
3. Brownfield and greenfield initialization should diverge:
   - brownfield: initialize docs/planning and generate project context early from the existing repo reality
   - greenfield: initialize structure first, then generate a seed context after high-level framing and regenerate richer context after planning artifacts exist
4. The roadmap layer should stay human-readable in markdown and machine-readable in yaml.
5. The implementation loop should keep `Code Review` before `Test Review`.
6. `CI Setup` in the BMAD flow should be implemented as CI/CD alignment against the repo's existing delivery infrastructure, not as blind greenfield scaffolding.
7. Automation v1 should automate research, validation, traceability, routing, and state updates before attempting full autonomous product-definition.

### Recommended artifact families by stage

Initialization should establish structure, not deep content:

- Initialize Docs
- Initialize Planning
- Generate Project Context

High-Level Analysis should create project-level direction:

- high-level brainstorm
- high-level market research
- high-level domain research
- high-level technical research
- high-level innovation strategy
- high-level opportunity framing or design-thinking output
- high-level storytelling if retained
- high-level product brief
- project roadmap in markdown and yaml

Detailed Analysis should create the focused inputs for the current roadmap slice:

- detailed brainstorm
- detailed market research
- detailed domain research
- detailed technical research
- detailed innovation strategy
- detailed design-thinking output
- detailed product brief

Planning and Experience Design should then turn the detailed-analysis slice into implementation-ready plans:

- PRD
- WDS lane
- UX design outputs
- downstream solutioning inputs

## Full Recommended Compass BMAD Workflow

This is the full workflow the plan is currently built around.

It is intentionally split into:

- a project-level roadmap layer
- a repeatable per-phase execution layer

### A. Project-Level Setup And Direction

#### 1. Initialization

1. Initialize Docs
2. Initialize Planning
3. Generate Project Context

Rules:

- brownfield should initialize from existing repo reality and generate context early
- greenfield should initialize structure first, then generate seed context after high-level framing, then regenerate richer context later
- initialization sets up structure and context; it should not try to complete detailed planning

#### 2. High-Level Analysis

1. High-Level Brainstorm
2. High-Level Market Research
3. High-Level Domain Research
4. High-Level Technical Research
5. High-Level Innovation Strategy
6. High-Level Opportunity Framing or Design-Thinking Output
7. High-Level Storytelling if retained as a distinct lane
8. High-Level Product Brief

Rules:

- this layer exists to preserve long-horizon thinking beyond the MVP
- these outputs should live as smaller roadmap artifacts, not one giant strategy file
- the three research lanes are the first automation candidates

#### 3. Project Roadmap

1. Synthesize the high-level analysis into `roadmap.md`
2. Encode the phase sequence and current state in `roadmap.yaml`
3. Identify the current slice, next slice, deferred slices, and dependencies between them

Rules:

- roadmap markdown is human-readable
- roadmap yaml is machine-readable
- this is the persistent cross-phase source of truth

### B. Per-Phase Execution Loop

Each roadmap slice should run the following loop.

#### 4. Phase Sync

1. Select the active roadmap slice
2. Confirm why it is the correct next slice
3. Confirm dependencies and carry-over
4. Define scope and out-of-scope boundaries
5. Update `phase.md`
6. Update `phase-state.yaml`

Rules:

- `Phase Sync` is the formal roadmap-slice selection and framing workflow
- do not introduce a separate selection workflow unless later implementation proves it is necessary

#### 5. Detailed Analysis

1. Detailed Brainstorm
2. Detailed Market Research
3. Detailed Domain Research
4. Detailed Technical Research
5. Detailed Innovation Strategy
6. Detailed Design-Thinking Output
7. Detailed Product Brief

Rules:

- this layer is focused only on the active roadmap slice
- these outputs should feed planning and solutioning, not become detached research archives
- detailed research is a strong automation target in v1

#### 6. Planning And Experience Design

1. Create PRD
2. Validate PRD
3. Edit PRD if needed
4. Trigger Mapping
5. Outline Scenarios
6. Create UX Design
7. Conceptual Specifications
8. Design Delivery
9. Update Docs if needed

Rules:

- WDS stays after PRD and before architecture
- if WDS exposes requirement gaps, route back to `Edit PRD`
- planning and docs should be updated continuously, even if `Update Docs` is not always a formal gate
- if the command implementation still invokes `Phase Sync` at planning entry, it should be treated as a confirmation checkpoint, not a second scope-selection workflow

#### 7. Solutioning

1. Create Architecture
2. Threat Modeling if the security lane is active
3. Security Architecture Review if the security lane is active
4. Test Design in system-level mode
5. Create Epics and Stories
6. Test Framework Setup
7. CI/CD Alignment
8. Secure Readiness Gate if the security lane is active
9. Check Implementation Readiness
10. Update Docs if needed

Rules:

- CYBERSEC runs after an initial architecture draft, not before architecture exists
- security remains conditional, not mandatory for every project
- CI work should align with the repo's real delivery infrastructure rather than blindly scaffolding a new pipeline

#### 8. Implementation

##### Sprint Kickoff

1. Sprint Planning
2. Sprint Status as needed

##### Epic Loop

1. Implementation Brainstorming
2. Test Design in epic-level mode
3. Implementation Research

##### Story Loop

1. Create Story
2. Validate Story
3. ATDD
4. Dev Story
5. Test Automation
6. QA Automation Test if needed
7. Code Review
8. Test Review
9. Traceability
10. Sprint Status as needed

##### Epic Wrap-Up

1. Update Docs
2. Retrospective
3. Sprint Status as needed

Rules:

- `Test Automation` is the primary post-dev automation lane
- `QA Automation Test` is a secondary expansion lane, not the default first choice
- `Code Review` should stay before `Test Review`
- implementation automation should include adversarial review, traceability, and reuse checks
- before `Dev Story`, automation and prompts should check for existing reusable components, services, queries, and patterns

#### 9. Release Gate

1. NFR Assessment
2. Final Test Review
3. Traceability Gate
4. Secure Release Gate if the security lane is active
5. Validate Docs
6. Sprint Status as needed

Rules:

- release gating should collect evidence rather than rely on intuition
- secure release gates should only run when the security lane is active

#### 10. Phase Closeout

1. Phase Closeout
2. Archive the completed phase into `previous/`
3. Extract lessons into `lessons/`
4. Update `roadmap.md`
5. Update `roadmap.yaml`
6. Recreate clean `current/` structure for the next slice

Rules:

- closeout is where roadmap state advances
- closeout is also where project-level continuity is preserved across BMAD cycles

### C. Supporting And Alternate Lanes

These are part of the operating model but not part of the main linear gate chain:

1. Problem Solving as an anytime lane
2. Correct Course as a recovery lane
3. Quick Spec and Quick Dev as alternate small-work lanes
4. Update Docs as a utility workflow across phases
5. Sprint Status as a checkpoint workflow across implementation
6. Automation wrappers as orchestration around the canonical workflow, not replacements for it

## Planning Framework And Documentation Framework Reality

The planning and documentation framework review changed the rollout shape.

### Planning framework findings

The planning framework is already the right base model:

- `reference/planning/framework/roadmap/` is the cross-phase planning lane
- `reference/planning/framework/current/` is the active phase working set
- `reference/planning/framework/previous/` is the historical phase archive
- `reference/planning/framework/lessons/` is the reusable carry-forward lane

What is missing is explicit structure for the roadmap-driven BMAD model:

- machine-readable roadmap state
- machine-readable active phase state
- first-class homes for high-level analysis artifacts
- first-class homes for detailed-analysis artifacts
- explicit destinations for WDS outputs
- explicit destinations for CYBERSEC outputs
- explicit rules for how `Phase Closeout` updates roadmap state and archives the phase

### Documentation framework findings

The documentation framework is directionally sound and should not be redesigned.

The main gaps are:

- no concrete rule yet for when planning artifacts graduate into stable human docs
- no meaningful AI-domain standards yet beyond the placeholder README
- no explicit bridge between BMAD planning outputs and documentation lifecycle control

### Planning implication

The planning framework needs structural expansion now.
The documentation framework needs targeted completion, not a rebuild.

## Exact Folder/File Contract For Core Roadmap And Phase Artifacts

These four files are the minimum contract for roadmap-driven Compass BMAD operation.

### 1. `reference/planning/framework/roadmap/roadmap.md`

Human-readable project roadmap.

Required purpose:

- summarize the project-level direction across multiple BMAD cycles
- show what phase is active now, what is next, and what is deferred
- link to the smaller high-level artifacts that justify the roadmap

Required update events:

- after initial high-level analysis
- when roadmap priorities materially change
- after every `Phase Closeout`

Required sections:

1. `Status`, `Owner`, `Last Updated`
2. `Project Direction`
3. `Current Horizon`
4. `Roadmap Sequence`
5. `Phase Index`
6. `Deferred Or Future Opportunities`
7. `Source Artifacts`
8. `Change Log`

Required content rules:

- this file is a summary and navigator, not the full content dump
- this file MUST only reflect approved roadmap state
- proposed roadmap changes MUST live in proposal or automation report artifacts until approved
- it MUST point to the smaller roadmap artifacts in sibling folders
- it MUST use exact phase ids and titles that match `roadmap.yaml`
- it MUST identify the active roadmap slice

### 2. `reference/planning/framework/roadmap/roadmap.yaml`

Machine-readable roadmap state.

Required purpose:

- provide deterministic roadmap state for automation, closeout, and phase selection
- track which roadmap slice is active, completed, deferred, or next

Required update events:

- after initial roadmap creation
- during `Phase Sync` when the active slice is selected or re-scoped
- during `Phase Closeout` when the current slice is completed, deferred, or requeued

Required top-level fields:

- `version`
- `project`
- `owner`
- `last_updated`
- `active_phase_id`
- `phases`

Required `phases[]` fields:

- `id`
- `slug`
- `title`
- `status`
- `objective`
- `roadmap_order`
- `depends_on`
- `entry_criteria`
- `exit_criteria`
- `supporting_docs`
- `planned_start`
- `target_end`
- `actual_end`
- `snapshot_path`
- `lessons_path`

Allowed `status` values:

- `planned`
- `active`
- `completed`
- `deferred`
- `cancelled`

Required content rules:

- this file MUST only reflect approved roadmap state
- proposed changes to phase ordering, activation, or status MUST remain outside this file until approved
- exactly one phase MAY be `active`
- phase ids MUST be stable across roadmap revisions
- `snapshot_path` and `lessons_path` MUST be empty until closeout creates them
- every phase listed here MUST appear in `roadmap.md`

### 3. `reference/planning/framework/current/phase.md`

Human-readable active-phase brief.

Required purpose:

- act as the human source of truth for the currently selected roadmap slice
- capture the framing output of `Phase Sync`
- point downstream workflows at the correct roadmap context and boundaries
- provide a readable brief for humans without duplicating machine-state detail

Required update events:

- at phase start during `Phase Sync`
- whenever scope materially changes
- before `Phase Closeout`

Required sections:

1. `Status`, `Owner`, `Last Updated`
2. `Phase Identity`
3. `Why This Phase Now`
4. `Objective`
5. `In Scope`
6. `Out Of Scope`
7. `Dependencies And Carry-Over`
8. `Required Source Artifacts`
9. `Planned Deliverables`
10. `Exit Criteria`
11. `Risks And Assumptions`
12. `Notes And Decisions`

Required content rules:

- the phase id and title MUST match `phase-state.yaml` and `roadmap.yaml`
- this file MUST explicitly state what is not being done in the current slice
- this file MUST link to the roadmap artifacts that justify the phase
- this file MUST stay concise and should point to smaller phase artifacts rather than duplicating them
- this file MUST remain the human-facing brief, not a duplicate of `phase-state.yaml`
- this file SHOULD summarize only the human-meaningful parts of active risks, not the full machine-readable risk state
- this file MUST NOT duplicate approval objects, artifact revision objects, stale-output records, or automation resume state
- scope changes and major phase decisions MUST be reflected in `Notes And Decisions`

### 4. `reference/planning/framework/current/phase-state.yaml`

Machine-readable active-phase state.

Required purpose:

- provide deterministic active-phase state for automation, validation, and closeout
- track workflow progression and artifact readiness inside the current phase

Required update events:

- when `Phase Sync` initializes the current slice
- when major workflow gates complete
- during `Phase Closeout`

Required top-level fields:

- `version`
- `phase_id`
- `slug`
- `title`
- `status`
- `owner`
- `last_updated`
- `roadmap_ref`
- `phase_doc`
- `in_scope`
- `out_of_scope`
- `dependencies`
- `lane_decisions`
- `lane_outcomes`
- `approval_markers`
- `workflow_status`
- `review_artifacts`
- `artifact_paths`
- `artifact_revisions`
- `automation_state`
- `open_risks`
- `next_checkpoint`

Required `lane_decisions` fields:

- `storytelling_mode`
- `wds_mode`
- `security_mode`
- `security_active`

Required `lane_outcomes` fields:

- `storytelling`
- `wds`
- `security`

Allowed `storytelling_mode` values:

- `separate`
- `embedded`
- `off`

Allowed `wds_mode` values:

- `required`
- `conditional`
- `skipped`

Allowed `security_mode` values:

- `forced_on`
- `forced_off`
- `auto`

Allowed `lane_outcomes.*` values:

- `pending`
- `complete`
- `skipped`
- `not_applicable`

Required `approval_markers` fields:

- `roadmap`
- `prd`
- `architecture`
- `readiness`

Required `approval_markers.<gate>` fields:

- `status`
- `requested_revision`
- `approved_revision`
- `reviewed_by`
- `reviewed_at`

Allowed `approval_markers.<gate>.status` values:

- `not_requested`
- `pending`
- `approved`
- `rejected`

Required `workflow_status` fields:

- `phase_sync`
- `detailed_analysis`
- `planning_experience`
- `solutioning`
- `implementation`
- `release_gate`
- `closeout`

Allowed `status` values:

- `planned`
- `active`
- `blocked`
- `review`
- `closed`

Allowed `workflow_status.*` values:

- `not_started`
- `in_progress`
- `complete`
- `blocked`

Required `review_artifacts` fields:

- `roadmap_gate`
- `prd_gate`
- `architecture_gate`
- `readiness_gate`

Required `artifact_paths` fields:

- `project_context`
- `brief`
- `prd`
- `ux_design`
- `architecture`
- `epics`
- `stories`
- `testing`
- `evidence`

Required `artifact_paths.<artifact>` fields:

- `current`
- `canonical`
- `draft`

Required `artifact_revisions` fields:

- `brief`
- `prd`
- `ux_design`
- `architecture`
- `epics`
- `stories`
- `readiness`

Required `artifact_revisions.<artifact>` fields:

- `current`
- `approved`
- `state`
- `updated_at`

Allowed `artifact_revisions.<artifact>.state` values:

- `not_started`
- `draft`
- `approved`
- `superseded`

Required `automation_state` fields:

- `last_completed_step`
- `last_completed_checkpoint`
- `pending_approval`
- `stale_outputs`
- `last_failure_report`
- `derived_from`

Allowed `automation_state.pending_approval` values:

- `null`
- object with the fields below

Required `automation_state.pending_approval` fields when present:

- `gate`
- `requested_revision`
- `review_artifact`
- `requested_at`

Allowed `automation_state.pending_approval.gate` values:

- `roadmap`
- `prd`
- `architecture`
- `readiness`

Required `automation_state.stale_outputs[]` fields:

- `artifact_key`
- `path`
- `reason`
- `caused_by_gate`
- `caused_by_revision`
- `stale_at`

Allowed `automation_state.stale_outputs[].reason` values:

- `gate_rejected`
- `revision_changed`
- `manual_reopen`
- `superseded`

Allowed `automation_state.stale_outputs[].caused_by_gate` values:

- `roadmap`
- `prd`
- `architecture`
- `readiness`
- `system`

Required `automation_state.derived_from.<artifact_key>` fields:

- `artifact_revision`
- `source_revisions`

Required `open_risks[]` fields:

- `id`
- `title`
- `severity`
- `status`
- `blocking`
- `owner`
- `affects`
- `mitigation`
- `source_artifact`
- `opened_at`
- `updated_at`

Allowed `open_risks[].severity` values:

- `low`
- `medium`
- `high`
- `critical`

Allowed `open_risks[].status` values:

- `open`
- `mitigating`
- `accepted`

Allowed `open_risks[].affects[]` values:

- `phase_sync`
- `detailed_analysis`
- `planning_experience`
- `solutioning`
- `implementation`
- `release_gate`
- `closeout`

Required content rules:

- this file MUST only describe the active phase in `current/`
- `roadmap_ref` MUST point to `../roadmap/roadmap.yaml`
- `phase_doc` MUST point to `phase.md`
- paths MAY be empty before an artifact exists, but the keys MUST exist
- `artifact_paths.<artifact>.current` MUST point to the active usable location for that artifact
- `artifact_paths.<artifact>.canonical` MUST point to the approved destination location for that artifact
- `artifact_paths.<artifact>.draft` MAY be empty when no draft namespace is used for that artifact
- when an artifact is pending approval in a draft namespace, `artifact_paths.<artifact>.current` MUST equal `artifact_paths.<artifact>.draft`
- after promotion or approval, `artifact_paths.<artifact>.current` MUST equal `artifact_paths.<artifact>.canonical`
- approval state MUST be recorded in `approval_markers.<gate>.status`, not inferred from artifact timestamps
- `approval_markers.<gate>.requested_revision` MUST identify the exact revision currently under review
- `approval_markers.<gate>.approved_revision` MUST match the accepted revision when `status=approved`
- `approval_markers.<gate>.approved_revision` MUST be empty when `status` is `not_requested`, `pending`, or `rejected`
- `reviewed_by` and `reviewed_at` MAY be empty until a human or automated gate decision is recorded
- each approval gate MUST map to exactly one reviewer-facing artifact in `review_artifacts`
- skipped or inapplicable lanes MUST be recorded explicitly in `lane_outcomes`
- `artifact_revisions.*` MUST use monotonic revision ids such as `brief-r1`, `prd-r2`, or `architecture-r3`
- `artifact_revisions.<artifact>.current` MUST identify the latest known revision for that artifact, or be empty when none exists
- `artifact_revisions.<artifact>.approved` MUST identify the last approved revision for that artifact, or be empty when none exists
- when `artifact_revisions.<artifact>.state=approved`, `current` MUST equal `approved`
- when `artifact_revisions.<artifact>.state=draft`, `current` MUST be set and `approved` MAY be empty or point to an older approved revision
- when `artifact_revisions.<artifact>.state=superseded`, at least one matching stale-output record MUST exist
- any artifact that participates in approval or resume MUST store `artifact_revision` and `derived_from` metadata in frontmatter or a companion state entry
- downstream artifacts MUST record the upstream revision(s) they were derived from in `automation_state.derived_from`
- `automation_state.pending_approval` MUST be `null` when no approval gate is currently waiting
- stale outputs MUST be recorded as structured entries in `automation_state.stale_outputs` when upstream approvals invalidate downstream artifacts
- `automation_state.derived_from` MUST record the current artifact revision and the exact source revisions used to produce it
- if an upstream artifact is reopened or changed materially, dependent approval markers MUST be downgraded and their `approved_revision`, `reviewed_by`, and `reviewed_at` fields cleared before resume continues
- `open_risks` MUST contain only unresolved or explicitly accepted residual risks for the active phase
- resolved risks MUST move to closeout or lessons artifacts instead of staying in `phase-state.yaml`
- if any risk has `blocking=true` and affects the current checkpoint, automation MUST NOT advance until the risk is resolved or explicitly accepted
- `closeout` MUST not be marked `complete` until roadmap state and archive paths are updated

### Core Artifact Authority And Update Order

Authority rules:

- `roadmap.yaml` is the machine authority for roadmap state
- `roadmap.md` is the human-readable reflection of approved roadmap state
- `phase-state.yaml` is the machine authority for the active phase
- `phase.md` is the human-readable reflection of approved active-phase framing

Update-order rules:

1. machine-readable files update first
2. human-readable files update second
3. roadmap files update only for roadmap-level decisions or status changes
4. phase files update for active-slice execution and scope framing

Conflict rule:

- if roadmap files disagree, `roadmap.yaml` wins
- if phase files disagree, `phase-state.yaml` wins

## Required Planning Framework Additions

To support the operating model above, the planning framework should be expanded as follows.

### Roadmap layer additions

- `reference/planning/framework/roadmap/roadmap.yaml`
- `reference/planning/framework/roadmap/research/market/`
- `reference/planning/framework/roadmap/research/domain/`
- `reference/planning/framework/roadmap/research/technical/`
- `reference/planning/framework/roadmap/strategy/`
- `reference/planning/framework/roadmap/storytelling/` if narrative remains a separate artifact lane

### Current-phase layer additions

- `reference/planning/framework/current/phase-state.yaml`
- `reference/planning/framework/current/brainstorming/detailed/`
- `reference/planning/framework/current/research/project-context/`
- `reference/planning/framework/current/research/market/`
- `reference/planning/framework/current/research/domain/`
- `reference/planning/framework/current/research/technical/`
- `reference/planning/framework/current/research/strategy/`
- `reference/planning/framework/current/research/implementation/`
- `reference/planning/framework/current/planning/brief/`

### Recommended artifact placement model

- high-level brainstorm -> `roadmap/brainstorming/`
- high-level market/domain/technical research -> `roadmap/research/<lane>/`
- high-level innovation strategy and opportunity framing -> `roadmap/strategy/`
- high-level storytelling if retained -> `roadmap/storytelling/`
- high-level product brief -> `roadmap/product-brief/`
- detailed brainstorm -> `current/brainstorming/detailed/`
- project context -> `current/research/project-context/`
- detailed market/domain/technical research -> `current/research/<lane>/`
- detailed innovation strategy and opportunity framing -> `current/research/strategy/`
- implementation research -> `current/research/implementation/`
- detailed brief -> `current/planning/brief/`
- WDS outputs -> `current/planning/ux-design/`
- threat modeling and security architecture review -> `current/planning/architecture/`
- secure gate reports -> `current/testing/` and `current/implementation/evidence/`

## Required Documentation Framework Follow-Up

The documentation framework changes should stay targeted.

### Human documentation follow-up

Update the human documentation standards so they define:

- when stable planning artifacts become official human-facing docs
- what level of review is required before promotion
- how promoted planning artifacts are linked from the destination `docs/` tree

### AI documentation follow-up

Expand `reference/documentation/ai/` so it is not only a placeholder and can eventually define:

- AI-facing context artifact standards
- agent-instruction artifact boundaries
- lifecycle rules for AI-maintained context files

The documentation framework should govern the end-state documentation system.
The planning framework should govern the reference-stage BMAD design system.

## Execution Contract Additions Before Implementation

The sections below turn the plan into a concrete execution contract.

### 1. Exact Schema Examples

#### Example `roadmap.yaml`

```yaml
version: 1
project: compass-brand
owner: compass-engine
last_updated: 2026-03-11
active_phase_id: phase-002
phases:
  - id: phase-001
    slug: foundation-and-landing
    title: Foundation And Landing
    status: completed
    objective: Establish the initial brand presence and first conversion path.
    roadmap_order: 1
    depends_on: []
    entry_criteria:
      - Docs and planning scaffolds exist
      - Initial high-level analysis is complete
    exit_criteria:
      - Landing experience is live
      - Initial analytics path is in place
    supporting_docs:
      - roadmap/product-brief/high-level-product-brief.md
      - roadmap/research/market/2026-03-11-market-landscape.md
    planned_start: 2026-03-01
    target_end: 2026-03-20
    actual_end: 2026-03-19
    snapshot_path: previous/foundation-and-landing-2026-03-19/
    lessons_path: lessons/foundation-and-landing-2026-03-19/
  - id: phase-002
    slug: funnel-optimization
    title: Funnel Optimization
    status: active
    objective: Improve conversion performance and reuse branded CTA patterns.
    roadmap_order: 2
    depends_on:
      - phase-001
    entry_criteria:
      - Phase 001 is closed
      - Baseline metrics are available
    exit_criteria:
      - Funnel experiment set is shipped
      - Reusable CTA system is documented
    supporting_docs:
      - roadmap/roadmap.md
      - roadmap/product-brief/high-level-product-brief.md
      - roadmap/strategy/2026-03-11-opportunity-framing.md
    planned_start: 2026-03-21
    target_end: 2026-04-15
    actual_end: ""
    snapshot_path: ""
    lessons_path: ""
```

#### Example `phase-state.yaml`

```yaml
version: 1
phase_id: phase-002
slug: funnel-optimization
title: Funnel Optimization
status: active
owner: compass-engine
last_updated: 2026-03-11
roadmap_ref: ../roadmap/roadmap.yaml
phase_doc: phase.md
in_scope:
  - Improve landing-page-to-lead conversion flow
  - Add reusable CTA and analytics components
out_of_scope:
  - Replatform the CMS
  - Full brand rewrite
dependencies:
  - phase-001
lane_decisions:
  storytelling_mode: separate
  wds_mode: required
  security_mode: auto
  security_active: false
lane_outcomes:
  storytelling: complete
  wds: pending
  security: not_applicable
approval_markers:
  roadmap:
    status: approved
    requested_revision: roadmap-r2
    approved_revision: roadmap-r2
    reviewed_by: trevor.leigh
    reviewed_at: 2026-03-11T10:15:00-05:00
  prd:
    status: pending
    requested_revision: prd-r2
    approved_revision: ""
    reviewed_by: ""
    reviewed_at: ""
  architecture:
    status: not_requested
    requested_revision: ""
    approved_revision: ""
    reviewed_by: ""
    reviewed_at: ""
  readiness:
    status: not_requested
    requested_revision: ""
    approved_revision: ""
    reviewed_by: ""
    reviewed_at: ""
workflow_status:
  phase_sync: complete
  detailed_analysis: complete
  planning_experience: not_started
  solutioning: not_started
  implementation: not_started
  release_gate: not_started
  closeout: not_started
review_artifacts:
  roadmap_gate: implementation/evidence/auto-plan-roadmap-proposal.md
  prd_gate: implementation/evidence/auto-plan-prd-gate.md
  architecture_gate: implementation/evidence/auto-plan-architecture-gate.md
  readiness_gate: testing/gates/draft/auto-plan-readiness-summary.md
artifact_paths:
  project_context:
    current: research/project-context/project-context.md
    canonical: research/project-context/project-context.md
    draft: ""
  brief:
    current: planning/brief/detailed-product-brief.md
    canonical: planning/brief/detailed-product-brief.md
    draft: ""
  prd:
    current: planning/prd/draft/
    canonical: planning/prd/
    draft: planning/prd/draft/
  ux_design:
    current: ""
    canonical: planning/ux-design/
    draft: planning/ux-design/draft/
  architecture:
    current: ""
    canonical: planning/architecture/
    draft: planning/architecture/draft/
  epics:
    current: ""
    canonical: planning/epics/
    draft: planning/epics/draft/
  stories:
    current: ""
    canonical: implementation/stories/
    draft: implementation/stories/draft/
  testing:
    current: testing/
    canonical: testing/
    draft: ""
  evidence:
    current: implementation/evidence/
    canonical: implementation/evidence/
    draft: ""
artifact_revisions:
  brief:
    current: brief-r1
    approved: brief-r1
    state: approved
    updated_at: 2026-03-11T09:10:00-05:00
  prd:
    current: prd-r2
    approved: ""
    state: draft
    updated_at: 2026-03-11T10:55:00-05:00
  ux_design:
    current: ""
    approved: ""
    state: not_started
    updated_at: ""
  architecture:
    current: ""
    approved: ""
    state: not_started
    updated_at: ""
  epics:
    current: ""
    approved: ""
    state: not_started
    updated_at: ""
  stories:
    current: ""
    approved: ""
    state: not_started
    updated_at: ""
  readiness:
    current: ""
    approved: ""
    state: not_started
    updated_at: ""
automation_state:
  last_completed_step: "Detailed analysis complete"
  last_completed_checkpoint: "roadmap_approved"
  pending_approval:
    gate: prd
    requested_revision: prd-r2
    review_artifact: implementation/evidence/auto-plan-prd-gate.md
    requested_at: 2026-03-11T11:00:00-05:00
  stale_outputs: []
  last_failure_report: ""
  derived_from:
    brief:
      artifact_revision: brief-r1
      source_revisions:
        brief: brief-r1
    prd_validation:
      artifact_revision: prd-validation-r2
      source_revisions:
        prd: prd-r2
open_risks:
  - id: risk-001
    title: Storytelling lane final naming is not yet settled
    severity: low
    status: open
    blocking: false
    owner: compass-engine
    affects:
      - planning_experience
    mitigation: Lock the naming during planning framework cleanup before template generation.
    source_artifact: planning/brief/detailed-product-brief.md
    opened_at: 2026-03-11T09:00:00-05:00
    updated_at: 2026-03-11T09:00:00-05:00
  - id: risk-002
    title: Security lane activation still depends on integration scope
    severity: medium
    status: mitigating
    blocking: false
    owner: compass-engine
    affects:
      - solutioning
      - release_gate
    mitigation: Confirm integration scope before architecture approval and secure readiness review.
    source_artifact: planning/architecture/security-review/
    opened_at: 2026-03-11T10:15:00-05:00
    updated_at: 2026-03-11T10:30:00-05:00
next_checkpoint: Review auto-plan PRD gate package for approval
```

Implementation rule:

- the real templates should preserve this shape even if field order changes
- automation should validate required keys, not rely on formatting

### 2. Final Planning Framework Target Tree

```text
reference/planning/framework/
├── current/
│   ├── phase.md
│   ├── phase-state.yaml
│   ├── brainstorming/
│   │   └── detailed/
│   ├── research/
│   │   ├── project-context/
│   │   ├── market/
│   │   ├── domain/
│   │   ├── technical/
│   │   ├── strategy/
│   │   └── implementation/
│   ├── planning/
│   │   ├── brief/
│   │   ├── prd/
│   │   ├── ux-design/
│   │   │   ├── trigger-mapping/
│   │   │   ├── outline-scenarios/
│   │   │   ├── conceptual-specifications/
│   │   │   └── design-delivery/
│   │   ├── architecture/
│   │   │   ├── threat-modeling/
│   │   │   └── security-review/
│   │   └── epics/
│   ├── implementation/
│   │   ├── stories/
│   │   ├── evidence/
│   │   └── retrospectives/
│   └── testing/
│       ├── test-design/
│       ├── automation/
│       ├── reviews/
│       └── gates/
├── lessons/
├── previous/
└── roadmap/
    ├── brainstorming/
    ├── research/
    │   ├── market/
    │   ├── domain/
    │   └── technical/
    ├── strategy/
    ├── storytelling/
    ├── product-brief/
    ├── archive/
    │   ├── brainstorming/
    │   ├── research/
    │   │   ├── market/
    │   │   ├── domain/
    │   │   └── technical/
    │   ├── strategy/
    │   ├── storytelling/
    │   └── product-brief/
    ├── roadmap.md
    └── roadmap.yaml
```

Automation-specific additions to the baseline tree:

- `current/implementation/evidence/auto-plan-state.yaml` exists from preflight onward and remains the runtime state file for `auto-plan`
- `current/planning/epics/draft/` holds pre-readiness epic outputs until the readiness gate is approved
- `current/implementation/stories/draft/` holds pre-readiness story outputs until the readiness gate is approved
- `current/testing/gates/draft/` holds pre-readiness gate artifacts until the readiness gate is approved

Rules:

- `storytelling/` remains only if Compass decides it is a distinct artifact lane
- `current/` contains exactly one active roadmap slice
- `previous/` and `lessons/` remain append-only historical surfaces

### 3. Workflow-To-Artifact Execution Map

#### Setup, High-Level Analysis, And Roadmap

| Workflow | Primary outputs | Destination | State updates |
| --- | --- | --- | --- |
| Initialize Docs | docs scaffold and initialization note | repo docs tree and `current/phase.md` notes | none |
| Initialize Planning | planning scaffold and `auto-plan-state.yaml` runtime skeleton | `reference/planning/framework/current/` and `current/implementation/evidence/` | initialize draft automation state |
| Generate Project Context | `project-context.md` | `current/research/project-context/` | `artifact_paths.project_context.current` |
| High-Level Brainstorm | brainstorm notes and themes | `roadmap/brainstorming/` | none |
| High-Level Market Research | market research docs | `roadmap/research/market/` | none |
| High-Level Domain Research | domain research docs | `roadmap/research/domain/` | none |
| High-Level Technical Research | technical research docs | `roadmap/research/technical/` | none |
| High-Level Innovation Strategy | innovation strategy docs | `roadmap/strategy/` | none |
| High-Level Opportunity Framing | opportunity framing docs | `roadmap/strategy/` | none |
| High-Level Storytelling | storytelling docs | `roadmap/storytelling/` | none |
| High-Level Product Brief | high-level product brief | `roadmap/product-brief/` | none |
| Project Roadmap | `roadmap.md`, `roadmap.yaml` | `roadmap/` | set `active_phase_id` and phase sequence |

#### Phase Sync And Detailed Analysis

| Workflow | Primary outputs | Destination | State updates |
| --- | --- | --- | --- |
| Phase Sync | `phase.md`, `phase-state.yaml`, scope framing, runtime-state sync | `current/` | `workflow_status.phase_sync=complete` |
| Detailed Brainstorm | phase-specific brainstorm docs | `current/brainstorming/detailed/` | none |
| Detailed Market Research | phase-specific market research | `current/research/market/` | `workflow_status.detailed_analysis=in_progress` |
| Detailed Domain Research | phase-specific domain research | `current/research/domain/` | `workflow_status.detailed_analysis=in_progress` |
| Detailed Technical Research | phase-specific technical research | `current/research/technical/` | `workflow_status.detailed_analysis=in_progress` |
| Detailed Innovation Strategy | phase-specific strategy docs | `current/research/strategy/` | `workflow_status.detailed_analysis=in_progress` |
| Detailed Design-Thinking Output | phase-specific opportunity framing docs | `current/research/strategy/` | `workflow_status.detailed_analysis=in_progress` |
| Detailed Product Brief | detailed product brief | `current/planning/brief/` | `artifact_paths.brief.current` |

#### Planning, Experience Design, And Solutioning

| Workflow | Primary outputs | Destination | State updates |
| --- | --- | --- | --- |
| Create PRD | PRD drafts and final | `current/planning/prd/` | `artifact_paths.prd.current`, `workflow_status.planning_experience=in_progress` |
| Validate PRD | PRD validation notes | `current/planning/prd/` | none |
| Edit PRD | PRD revision | `current/planning/prd/` | none |
| Trigger Mapping | trigger map docs | `current/planning/ux-design/trigger-mapping/` | none |
| Outline Scenarios | scenario docs | `current/planning/ux-design/outline-scenarios/` | none |
| Create UX Design | UX design docs and flows | `current/planning/ux-design/` | `artifact_paths.ux_design.current` |
| Conceptual Specifications | conceptual specs | `current/planning/ux-design/conceptual-specifications/` | none |
| Design Delivery | implementation handoff docs | `current/planning/ux-design/design-delivery/` | `workflow_status.planning_experience=complete` once approved |
| Create Architecture | architecture docs | `current/planning/architecture/` | `artifact_paths.architecture.current`, `workflow_status.solutioning=in_progress` |
| Threat Modeling | threat model docs | `current/planning/architecture/threat-modeling/` | none |
| Security Architecture Review | security review docs | `current/planning/architecture/security-review/` | none |
| Test Design (System-Level) | system-level test design | `current/testing/test-design/` | none |
| Create Epics and Stories | draft epic definitions and draft initial story set | `current/planning/epics/draft/` and `current/implementation/stories/draft/` | `artifact_paths.epics.current`, `artifact_paths.stories.current` |
| Test Framework Setup | framework setup guidance | `current/testing/automation/` | none |
| CI/CD Alignment | CI/CD alignment plan | `current/testing/automation/` and `current/implementation/evidence/` | none |
| Secure Readiness Gate | secure gate report | `current/testing/gates/` | none |
| Check Implementation Readiness | draft readiness report | `current/testing/gates/draft/` until approved | `workflow_status.solutioning=complete` once passed |

#### Implementation, Release, And Closeout

| Workflow | Primary outputs | Destination | State updates |
| --- | --- | --- | --- |
| Sprint Planning | sprint plan and status | `current/implementation/evidence/` | `workflow_status.implementation=in_progress` |
| Sprint Status | sprint status snapshot | `current/implementation/evidence/` | none |
| Implementation Brainstorming | epic brainstorming docs | `current/brainstorming/detailed/` | none |
| Test Design (Epic-Level) | epic-level test design | `current/testing/test-design/` | none |
| Implementation Research | implementation research docs | `current/research/implementation/` | none |
| Create Story | story file | `current/implementation/stories/` | `artifact_paths.stories.current` |
| Validate Story | story validation notes | `current/implementation/stories/` | none |
| ATDD | ATDD artifacts | `current/testing/test-design/` | none |
| Dev Story | code changes plus updated story file | repo codebase and `current/implementation/stories/` | none |
| Test Automation | automation artifacts and summary | `current/testing/automation/` | `artifact_paths.testing.current` |
| QA Automation Test | expanded API/E2E automation artifacts | `current/testing/automation/` | none |
| Code Review | code review notes | `current/testing/reviews/` | none |
| Test Review | test review notes | `current/testing/reviews/` | none |
| Traceability | traceability report | `current/testing/gates/` | none |
| Update Docs | docs deltas and promoted docs | target docs tree and `current/implementation/evidence/` | none |
| Retrospective | retrospective report | `current/implementation/retrospectives/` | none |
| NFR Assessment | NFR report | `current/testing/gates/` | `workflow_status.release_gate=in_progress` |
| Secure Release Gate | secure release report | `current/testing/gates/` | none |
| Validate Docs | docs validation notes | `current/testing/reviews/` | none |
| Phase Closeout | archive, lessons, roadmap updates | `previous/`, `lessons/`, and `roadmap/` | `workflow_status.closeout=complete`, `status=closed` |

#### Anytime And Alternate Lanes

| Workflow | Primary outputs | Destination | State updates |
| --- | --- | --- | --- |
| Problem Solving | problem-solving memo | `current/research/implementation/` or `current/implementation/evidence/` | none |
| Correct Course | correction plan | `current/implementation/evidence/` and `phase.md` | may update `next_checkpoint` |
| Quick Spec | compact spec artifact | `current/planning/brief/` or `current/planning/prd/` | none |
| Quick Dev | compact delivery artifact | `current/implementation/stories/` and `current/implementation/evidence/` | none |

### 4. Greenfield vs Brownfield Rules

| Area | Greenfield rule | Brownfield rule |
| --- | --- | --- |
| Initialize Docs | Scaffold the standard docs tree and indexes | Audit existing docs, preserve what is still valid, scaffold only missing structure |
| Initialize Planning | Create clean planning scaffold and empty state files | Create scaffold plus migration notes for inherited artifacts |
| Generate Project Context | Create a seed context after high-level framing, then regenerate after PRD and architecture exist | Generate context early from the live repo, existing docs, and architecture reality |
| High-Level Analysis | Run full high-level analysis unless the repo is a very small utility | Reuse valid prior roadmap artifacts, but refresh assumptions against current repo reality |
| Detailed Analysis | Always run for the active roadmap slice | Always run, but inherit prior lessons and previous-phase constraints |
| WDS Lane | Run when UX, workflows, user journeys, or behavior design matter | Run when existing UX is changing materially or drift is already evident |
| CYBERSEC Lane | Activate by heuristic or manual trigger | Activate by heuristic or manual trigger, with extra weight on inherited attack surface and legacy auth/data flows |
| Allowed skips | Storytelling may be folded into the high-level brief if not useful | Storytelling may be folded into the high-level brief if not useful |

Minimum rules:

- no project may skip `roadmap.md`, `roadmap.yaml`, `phase.md`, or `phase-state.yaml`
- no brownfield project may enter solutioning without refreshed project context
- no project may enter implementation without PRD, architecture, epics, and readiness artifacts

### 5. Phase Sync And Phase Closeout Operating Checklists

#### Phase Sync checklist

Required reads:

- `roadmap/roadmap.md`
- `roadmap/roadmap.yaml`
- relevant roadmap research, strategy, brief, and storytelling artifacts
- previous phase lessons if dependencies exist

Required writes:

- `current/phase.md`
- `current/phase-state.yaml`
- `roadmap/roadmap.md` if active phase or sequencing changes
- `roadmap/roadmap.yaml` if active phase or sequencing changes

Required write order:

1. update `roadmap.yaml` if the approved active slice, sequencing, or roadmap state changed
2. update `roadmap.md` to match the approved roadmap state
3. create or update `phase-state.yaml` from the approved active slice
4. create or update `phase.md` from `phase-state.yaml` plus the human framing

Required decisions:

- why this slice is next
- what is in scope
- what is explicitly out of scope
- which prior-phase outputs are dependencies
- whether the security lane should start as `forced_on`, `forced_off`, or `auto`

Required validation:

- active phase id matches roadmap state
- phase title and slug match roadmap state
- exit criteria are concrete and testable
- downstream teams can identify required source artifacts
- `roadmap.yaml` remains the authority over `roadmap.md`
- `phase-state.yaml` remains the authority over `phase.md`

#### Mid-phase material scope-change rule

Required reads:

- `current/phase.md`
- `current/phase-state.yaml`
- relevant planning and implementation artifacts affected by the change
- roadmap files only if the change might alter roadmap sequencing or phase-level objective

Required write order:

1. update `phase-state.yaml` first
2. update `phase.md` second
3. update `roadmap.yaml` only if the change affects roadmap-level ordering, objective, or status
4. update `roadmap.md` only if `roadmap.yaml` changed

Required validation:

- active scope, out-of-scope, and dependencies remain aligned between `phase.md` and `phase-state.yaml`
- roadmap files remain untouched unless the change is truly roadmap-level
- human-readable files do not become the source of truth for machine state

#### Phase Closeout checklist

Required reads:

- `current/phase.md`
- `current/phase-state.yaml`
- current implementation evidence and testing artifacts
- current roadmap state

Required writes:

- `previous/<phase-slug>-<YYYY-MM-DD>/`
- `lessons/<phase-slug>-<YYYY-MM-DD>/`
- updated `roadmap.md`
- updated `roadmap.yaml`
- clean next-phase scaffold in `current/`

Required write order:

1. mark closeout state and archive targets in `phase-state.yaml`
2. finalize any closeout notes needed in `phase.md`
3. archive the current phase into `previous/`
4. extract lessons into `lessons/`
5. update `roadmap.yaml` with completed, deferred, or requeued status and the next active slice
6. update `roadmap.md` to match the new roadmap state
7. recreate clean `current/` scaffolding for the next slice

Required decisions:

- is the phase completed, deferred, or requeued
- what lessons must carry forward
- what becomes the next active roadmap slice
- what planning artifacts remain reference-only versus promoted

Required validation:

- archive and lessons paths recorded in machine state match what was actually written
- `roadmap.yaml` and `roadmap.md` agree on the next active slice
- no stale phase files remain in `current/` after the new scaffold is created

Required validation:

- archived snapshot path exists
- lessons path exists
- roadmap state no longer marks the closed phase as active
- `current/` only contains next-phase starter structure

### 6. Security-Lane Activation Rules

Activation modes:

- `forced_on`
- `forced_off`
- `auto`

`forced_on` rules:

- always activate the security lane
- required when contract, regulatory, or explicit stakeholder requirements demand security artifacts

`forced_off` rules:

- may only be used when there is no contractual, regulatory, or platform-security requirement
- requires written rationale in `phase.md`

`auto` rules:

Activate if **any one** of these high-signal triggers is true:

- authentication, authorization, or RBAC is in scope
- payments, billing, or financial transactions are in scope
- PII, PHI, secrets, or multi-tenant data separation is in scope
- public network exposure, external webhooks, or file uploads are in scope
- admin, privileged, or destructive operations are in scope
- the project must produce formal security evidence

Activate if **any two** of these medium-signal triggers are true:

- third-party integrations with write access
- background jobs, queues, or scheduled automation
- user-generated content handling
- new persistence models or migrations
- shared services reused across multiple repos or apps
- AI actions with external side effects

When active, the lane MUST produce:

- threat model
- security architecture review
- secure readiness gate
- secure release gate

### 7. WDS Completion Criteria

| Workflow | Required output | Done when | Loop-back trigger |
| --- | --- | --- | --- |
| Trigger Mapping | trigger map for primary actors and systems | all in-scope triggers, entry points, and expected outcomes are captured | missing user/system trigger reveals a product requirement gap |
| Outline Scenarios | prioritized scenarios with success, alternate, and failure flows | major user journeys are represented and prioritized for implementation | scenario exposes unowned requirement, dependency, or flow contradiction |
| Conceptual Specifications | conceptual interaction and state model | states, transitions, key components, and content/data expectations are defined | spec reveals missing business rule, constraint, or data dependency |
| Design Delivery | implementation handoff package | implementation team can identify what to build without design ambiguity | unresolved design ambiguity blocks story creation or architecture decisions |

WDS lane completion rule:

- the WDS lane is not complete until design delivery is implementation-ready and open blockers are either resolved or routed back to `Edit PRD`

### 8. Automation Boundaries

| Automation wrapper | May do | Must stop for human approval | Must never do without explicit approval |
| --- | --- | --- | --- |
| `auto-plan` | run research, draft roadmap proposals, draft PRD and architecture inputs, prepare test and CI alignment proposals, and assemble readiness evidence | before roadmap activation, before final PRD approval, before final architecture approval, before readiness approval | silently finalize strategy, canonical roadmap state, PRD, architecture, or readiness |
| `auto-epic-start` | review prior artifacts, order stories, draft epic-level test design, prep baseline | before materially changing epic scope or story order | silently expand epic scope |
| `auto-story` | create/validate story, run ATDD, implement, automate tests, produce reviews and traceability | before merge, before net-new architecture, before destructive schema or migration changes | silently merge risky work or approve itself on irreversible changes |
| `auto-epic-end` | gather retro, update docs, prepare next-epic preview, draft state updates | before marking epic complete or advancing phase/roadmap state | silently close an epic or phase without review |

Global automation hard stops:

- access-control changes
- secrets handling changes
- destructive data migrations
- major dependency swaps
- large-scale deletions or rewrites
- cross-repo contract changes

### 8A. Shared Automation Implementation Contract

All four wrappers should be implemented to the same shared command contract.

#### Proposed command shape

```text
auto-<name> [--phase-id <phase-id>] [--epic-id <epic-id>] [--story-id <story-id>] [--mode greenfield|brownfield] [--resume] [--approval-mode manual]
```

#### Shared runtime steps

1. Run preflight checks:
   - verify required files exist
   - create the minimal `current/` scaffold and fallback evidence path if missing
   - detect greenfield or brownfield mode
   - verify `bd` is available
   - load `roadmap.yaml` and `phase-state.yaml` when applicable
2. Load only the minimum artifact set needed for the current command.
3. Resolve the target scope:
   - roadmap slice
   - epic
   - story
4. Execute steps sequentially.
5. After each major step, write a checkpoint summary and update the active runtime state file.
6. If a human approval gate is reached, stop and emit the exact reviewer-facing gate artifact for that checkpoint.
7. If a failure occurs, write a partial-failure report and update phase state.
8. If resumed, detect the last completed step from runtime state plus accepted outputs, then continue from the next step.

#### Shared implementation files

- command specs:
  - `reference/BMAD/tools/automation/commands/auto-plan.md`
  - `reference/BMAD/tools/automation/commands/auto-epic-start.md`
  - `reference/BMAD/tools/automation/commands/auto-story.md`
  - `reference/BMAD/tools/automation/commands/auto-epic-end.md`
- policy files:
  - `reference/BMAD/tools/automation/policies/state-model.md`
  - `reference/BMAD/tools/automation/policies/context-budgeting.md`
  - `reference/BMAD/tools/automation/policies/patching-strategy.md`
- templates:
  - `reference/BMAD/tools/automation/templates/auto-plan-state.yaml`
  - `reference/BMAD/tools/automation/templates/handoff-template.md`
  - `reference/BMAD/tools/automation/templates/approval-gate-report.md`
  - `reference/BMAD/tools/automation/templates/partial-failure-report.md`
  - `reference/BMAD/tools/automation/templates/story-gate-report.md`
  - `reference/BMAD/tools/automation/templates/roadmap-state-update.md`

#### Shared state rules

- automation state lives in BMAD artifacts plus `bd`
- TodoWrite is not part of the design
- `roadmap.yaml` is the source of truth for roadmap-level state
- `phase-state.yaml` is the source of truth for active-phase state after `Phase Sync`
- `current/implementation/evidence/auto-plan-state.yaml` is the source of truth for `auto-plan` runtime state before `Phase Sync` and the checkpoint-resume spine throughout the command
- `bd` is the source of truth for implementation task ownership and closure
- an output is considered `accepted` only when its corresponding `approval_markers.<gate>.status` is `approved`, its `approved_revision` matches the current accepted revision, and its `source_revisions` match current `artifact_revisions`
- outputs listed in `automation_state.stale_outputs` must be regenerated before they can be treated as reusable on resume
- `automation_state.pending_approval` stores the exact active gate request, not just the gate name
- `automation_state.stale_outputs` stores one structured record per stale artifact or stale artifact group
- `automation_state.derived_from` uses a keyed map where each entry stores `artifact_revision` plus `source_revisions`
- `auto-plan-report.md` is never used as a checkpoint-resume source
- pre-Phase-Sync failures must still be written to a deterministic fallback artifact:
  - `reference/planning/framework/current/implementation/evidence/auto-plan-preflight-failure.md`

### 8B. Detailed Automation Command Specifications

#### `auto-plan`

Purpose:

- automate the analysis, roadmap, detailed-analysis, planning, and solutioning flow up to implementation readiness

Prerequisites:

- `reference/planning/framework/roadmap/` exists or can be scaffolded
- `reference/planning/framework/current/` exists or can be scaffolded
- for brownfield, project context can be derived from the existing repo
- for greenfield, initialization can scaffold the missing planning surfaces

Reads:

- `reference/BMAD/BMAD-workflow.md`
- `reference/BMAD/modules/custom/bmm/module-help.csv`
- `reference/planning/framework/roadmap/roadmap.md` if present
- `reference/planning/framework/roadmap/roadmap.yaml` if present
- `reference/planning/framework/current/phase.md` if present
- `reference/planning/framework/current/phase-state.yaml` if present
- `reference/planning/framework/current/implementation/evidence/auto-plan-state.yaml` if present
- roadmap artifacts in `reference/planning/framework/roadmap/**`
- prior lessons in `reference/planning/framework/lessons/**` when relevant
- repo structure and existing docs/planning artifacts for brownfield

Writes:

- `reference/planning/framework/current/implementation/evidence/auto-plan-preflight-failure.md` as the fallback failure artifact
- `reference/planning/framework/current/implementation/evidence/auto-plan-state.yaml`
- `reference/planning/framework/current/research/project-context/project-context.md`
- `reference/planning/framework/roadmap/brainstorming/`
- `reference/planning/framework/roadmap/research/market/`
- `reference/planning/framework/roadmap/research/domain/`
- `reference/planning/framework/roadmap/research/technical/`
- `reference/planning/framework/roadmap/strategy/`
- `reference/planning/framework/roadmap/storytelling/` when `lane_decisions.storytelling_mode=separate`
- `reference/planning/framework/roadmap/product-brief/`
- `reference/planning/framework/current/implementation/evidence/auto-plan-roadmap-proposal.md`
- `reference/planning/framework/current/implementation/evidence/auto-plan-prd-gate.md`
- `reference/planning/framework/current/implementation/evidence/auto-plan-architecture-gate.md`
- `reference/planning/framework/roadmap/roadmap.md` only after roadmap approval
- `reference/planning/framework/roadmap/roadmap.yaml` only after roadmap approval
- `reference/planning/framework/current/phase.md`
- `reference/planning/framework/current/phase-state.yaml`
- `reference/planning/framework/current/brainstorming/detailed/`
- `reference/planning/framework/current/research/market/`
- `reference/planning/framework/current/research/domain/`
- `reference/planning/framework/current/research/technical/`
- `reference/planning/framework/current/research/strategy/`
- `reference/planning/framework/current/planning/brief/`
- `reference/planning/framework/current/planning/prd/`
- `reference/planning/framework/current/planning/ux-design/trigger-mapping/` when `lane_decisions.wds_mode!=skipped`
- `reference/planning/framework/current/planning/ux-design/outline-scenarios/` when `lane_decisions.wds_mode!=skipped`
- `reference/planning/framework/current/planning/ux-design/conceptual-specifications/` when `lane_decisions.wds_mode!=skipped`
- `reference/planning/framework/current/planning/ux-design/design-delivery/` when `lane_decisions.wds_mode!=skipped`
- `reference/planning/framework/current/planning/architecture/`
- `reference/planning/framework/current/planning/architecture/threat-modeling/` when `lane_decisions.security_active=true`
- `reference/planning/framework/current/planning/architecture/security-review/` when `lane_decisions.security_active=true`
- `reference/planning/framework/current/planning/epics/draft/`
- `reference/planning/framework/current/implementation/stories/draft/`
- `reference/planning/framework/current/planning/epics/` only after readiness approval
- `reference/planning/framework/current/implementation/stories/` only after readiness approval
- `reference/planning/framework/current/testing/test-design/`
- `reference/planning/framework/current/testing/automation/`
- `reference/planning/framework/current/testing/gates/draft/auto-plan-readiness-summary.md`
- `reference/planning/framework/current/testing/gates/auto-plan-readiness-summary.md` only after readiness approval
- `reference/planning/framework/current/implementation/evidence/auto-plan-report.md`

Required `auto-plan-state.yaml` fields:

- `version`
- `command`
- `phase_id`
- `run_status`
- `lane_decisions`
- `lane_outcomes`
- `approval_markers`
- `review_artifacts`
- `artifact_revisions`
- `automation_state`
- `draft_artifacts`

Required `draft_artifacts` fields:

- `roadmap_proposal`
- `prd_gate`
- `architecture_gate`
- `epics`
- `stories`
- `readiness_gate`

Required `draft_artifacts.*` fields:

- `path`
- `revision`
- `derived_from`
- `status`
- `supersedes`

Runtime rules:

- `auto-plan-state.yaml` is the only machine-readable runtime state file before `phase-state.yaml` exists
- after `phase-state.yaml` exists, `auto-plan-state.yaml` remains the canonical runtime checkpoint file for the wrapper and `phase-state.yaml` remains the canonical active-phase state file
- reviewer-facing markdown artifacts such as `auto-plan-roadmap-proposal.md`, `auto-plan-prd-gate.md`, and `auto-plan-architecture-gate.md` are never machine-readable resume sources
- every time a draft artifact is created or regenerated, its `draft_artifacts.*` entry MUST update `path`, `revision`, `derived_from`, `status`, and `supersedes`
- any `Edit PRD` action immediately invalidates the prior PRD validation result for resume purposes
- no implementation or sprint workflow may consume outputs from any `draft/` directory

Exact step sequence:

1. Preflight and determine greenfield or brownfield mode.
2. Initialize docs and planning structure if required, create the minimal fallback evidence path, and initialize `auto-plan-state.yaml`. Do not create canonical `phase-state.yaml` yet.
3. If brownfield, generate or refresh project context from the live repo and existing artifacts.
4. Run high-level market, domain, and technical research.
5. Draft high-level innovation strategy and opportunity framing.
6. Handle storytelling according to `lane_decisions.storytelling_mode`, record the result in `lane_outcomes.storytelling`, and draft the corresponding artifact when applicable.
7. Draft the high-level product brief, update `artifact_paths.brief.current` as needed, and record the revision in `artifact_revisions.brief.current`.
8. If greenfield, generate the seed project context now that high-level framing exists.
9. Draft `auto-plan-roadmap-proposal.md` using the roadmap-state-update template, set `review_artifacts.roadmap_gate` to that file, and update `auto-plan-state.yaml`.
10. Set `approval_markers.roadmap.status=pending`, set `approval_markers.roadmap.requested_revision` to the current roadmap proposal revision, clear its approval metadata, set `automation_state.pending_approval` to an object containing the roadmap gate, requested revision, review artifact, and request time, and stop for roadmap approval.
11. If roadmap approval is rejected, record the rejection in the proposal artifact and `auto-plan-state.yaml`, set `approval_markers.roadmap.status=rejected`, clear `approval_markers.roadmap.approved_revision`, record `reviewed_by` and `reviewed_at`, keep canonical roadmap files unchanged, and stop.
12. If roadmap approval is granted, update approved `roadmap.md` and `roadmap.yaml`, set `approval_markers.roadmap.status=approved`, copy `requested_revision` into `approved_revision`, record `reviewed_by` and `reviewed_at`, and set `automation_state.pending_approval=null`.
13. Run `Phase Sync` and create/update `phase.md` and `phase-state.yaml` from the approved slice plus the accepted values from `auto-plan-state.yaml`.
14. Run detailed market, domain, and technical research for the active slice.
15. Draft detailed innovation strategy, detailed design-thinking output, and detailed brief, then update `artifact_paths.brief.current` and `artifact_revisions.brief.current`.
16. Draft PRD into its draft location, set `artifact_paths.prd.current=artifact_paths.prd.draft`, run PRD validation, and record the resulting PRD revision in `artifact_revisions.prd.current` with `state=draft`.
17. If `lane_decisions.wds_mode!=skipped`, generate Trigger Mapping, Outline Scenarios, Create UX Design, Conceptual Specifications, and Design Delivery, set `artifact_paths.ux_design.current` to the appropriate draft or canonical location, record `lane_outcomes.wds=in_progress`, and record their `artifact_revision` and `source_revisions` entries in `automation_state.derived_from`.
18. If WDS exposes requirement gaps, run `Edit PRD`, increment `artifact_revisions.prd.current`, keep `artifact_revisions.prd.state=draft`, and rerun `Validate PRD` on the revised PRD.
19. If the revised PRD fails validation, mark WDS and all downstream planning outputs stale, set `approval_markers.prd.status=not_requested`, set `approval_markers.prd.requested_revision` to the current PRD revision, clear its approval metadata, write `auto-plan-prd-gate.md` as blocked, and stop for manual correction.
20. If the revised PRD passes validation after PRD edits, regenerate the affected WDS outputs and refresh their `automation_state.derived_from` entries so they derive from the latest PRD revision.
21. The PRD gate MUST NOT reopen until the most recent PRD revision has a fresh validation result bound to the same `artifact_revisions.prd.current` value.
22. If WDS is skipped, set `lane_outcomes.wds=skipped`; otherwise set it to `complete` once the WDS set matches the current PRD revision.
23. Write `auto-plan-prd-gate.md`, set `review_artifacts.prd_gate` to that file, set `approval_markers.prd.status=pending`, set `approval_markers.prd.requested_revision` to the current PRD revision, clear its approval metadata, set `automation_state.pending_approval` to an object containing the PRD gate, requested revision, review artifact, and request time, and stop for PRD approval.
24. If PRD approval is rejected, set `approval_markers.prd.status=rejected`, clear `approval_markers.prd.approved_revision`, record `reviewed_by` and `reviewed_at`, downgrade `approval_markers.architecture` and `approval_markers.readiness` to `not_requested` with cleared approval metadata, append stale-output records for WDS, architecture, draft epics/stories, and readiness artifacts, set `automation_state.pending_approval=null`, and stop.
25. If PRD approval is granted, set `approval_markers.prd.status=approved`, copy `requested_revision` into `approved_revision`, record `reviewed_by` and `reviewed_at`, and set `automation_state.pending_approval=null`.
26. Draft architecture into its draft location, set `artifact_paths.architecture.current=artifact_paths.architecture.draft`, record `artifact_revisions.architecture.current` with `state=draft`, and record its `artifact_revision` and source revisions in `automation_state.derived_from`.
27. Resolve security activation according to `lane_decisions.security_mode`. If the security lane is active, run Threat Modeling and Security Architecture Review and set `lane_outcomes.security=in_progress`; otherwise set `lane_outcomes.security=skipped` or `not_applicable` according to repo rules.
28. Run system-level test design and record its `artifact_revision` and source revisions in `automation_state.derived_from`.
29. Run CI/CD alignment.
30. Write `auto-plan-architecture-gate.md`, set `review_artifacts.architecture_gate` to that file, set `approval_markers.architecture.status=pending`, set `approval_markers.architecture.requested_revision` to the current architecture revision, clear its approval metadata, set `automation_state.pending_approval` to an object containing the architecture gate, requested revision, review artifact, and request time, and stop for architecture approval.
31. If architecture approval is rejected, set `approval_markers.architecture.status=rejected`, clear `approval_markers.architecture.approved_revision`, record `reviewed_by` and `reviewed_at`, downgrade `approval_markers.readiness` to `not_requested` with cleared approval metadata, append stale-output records for architecture-dependent outputs, including security review, test design, draft epics/stories, and readiness artifacts, set `automation_state.pending_approval=null`, and stop.
32. If architecture approval is granted, set `approval_markers.architecture.status=approved`, copy `requested_revision` into `approved_revision`, record `reviewed_by` and `reviewed_at`, set `automation_state.pending_approval=null`, and if the security lane was active set `lane_outcomes.security=complete`.
33. Draft epics and story inputs into `current/planning/epics/draft/` and `current/implementation/stories/draft/`, set `artifact_paths.epics.current=artifact_paths.epics.draft` and `artifact_paths.stories.current=artifact_paths.stories.draft`, record `artifact_revisions.epics.current` and `artifact_revisions.stories.current` with `state=draft`, and populate `automation_state.derived_from` for both using the strict keyed map shape.
34. If the security lane is active, run Secure Readiness Gate.
35. Draft implementation-readiness outputs and write `current/testing/gates/draft/auto-plan-readiness-summary.md`, record `artifact_revisions.readiness.current` with `state=draft`, set `review_artifacts.readiness_gate` to that file, and record its `artifact_revision` and source revisions in `automation_state.derived_from`.
36. Set `approval_markers.readiness.status=pending`, set `approval_markers.readiness.requested_revision` to the current readiness package revision, clear its approval metadata, set `automation_state.pending_approval` to an object containing the readiness gate, requested revision, review artifact, and request time, and stop for implementation-readiness approval.
37. If readiness approval is rejected, set `approval_markers.readiness.status=rejected`, clear `approval_markers.readiness.approved_revision`, record `reviewed_by` and `reviewed_at`, keep `artifact_paths.epics.current`, `artifact_paths.stories.current`, and `review_artifacts.readiness_gate` pointed at their draft locations, keep draft outputs non-executable by leaving them unpromoted, mark the affected revision entries as `superseded` where appropriate, append stale-output records for the rejected readiness package, set `automation_state.pending_approval=null`, and stop.
38. If readiness approval is granted, set `approval_markers.readiness.status=approved`, copy `requested_revision` into `approved_revision`, record `reviewed_by` and `reviewed_at`, set `automation_state.pending_approval=null`, promote approved epics/stories from `draft/` into their canonical folders, set `artifact_paths.epics.current=artifact_paths.epics.canonical` and `artifact_paths.stories.current=artifact_paths.stories.canonical`, set the promoted revision entries so `approved=current` and `state=approved`, promote the readiness summary into `current/testing/gates/auto-plan-readiness-summary.md`, set `artifact_revisions.readiness.approved=artifact_revisions.readiness.current` with `state=approved`, write `auto-plan-report.md`, and mark the solutioning stage complete.

Required state transitions:

- after step 2:
  - create `auto-plan-state.yaml`
  - initialize each `approval_markers.<gate>` object with `status=not_requested` and empty revision/reviewer metadata
  - initialize `automation_state.pending_approval=null`
  - initialize `automation_state.stale_outputs=[]`
  - initialize each `artifact_revisions.<artifact>` object with `state=not_started` unless an artifact already exists
  - initialize `lane_outcomes.storytelling=pending`, `lane_outcomes.wds=not_applicable`, and `lane_outcomes.security=not_applicable`
  - do not create canonical `phase-state.yaml` yet
- after step 12:
  - canonical roadmap state becomes approved
  - set `automation_state.last_completed_checkpoint=roadmap_approved` in `auto-plan-state.yaml`
- after step 13:
  - create or update canonical `phase-state.yaml` by copying `lane_outcomes`, `approval_markers`, `review_artifacts`, `artifact_revisions`, and `automation_state` from `auto-plan-state.yaml`
  - set `workflow_status.phase_sync=complete`
- after step 15:
  - set `workflow_status.detailed_analysis=complete`
  - set `next_checkpoint=Draft PRD for active slice`
- after step 23:
  - set `workflow_status.planning_experience=in_progress`
- after step 25:
  - set `workflow_status.planning_experience=complete`
- after step 26:
  - set `workflow_status.solutioning=in_progress`
- after step 38:
  - set `workflow_status.solutioning=complete`
  - update `artifact_paths.epics.current` and `artifact_paths.stories.current` to canonical approved locations
  - update the approved revision fields for epics, stories, and readiness
  - update `review_artifacts.readiness_gate` to the canonical approved location
  - set `next_checkpoint=Begin sprint planning`
- after canonical `phase-state.yaml` exists:
  - every checkpoint update MUST be written to both `auto-plan-state.yaml` and `phase-state.yaml`

Invalidation and regeneration rules:

- if roadmap approval is rejected:
  - do not modify canonical roadmap files
  - set `approval_markers.roadmap.status=rejected` and clear its `approved_revision`
  - downgrade `approval_markers.prd`, `approval_markers.architecture`, and `approval_markers.readiness` to `status=not_requested` and clear their approval metadata
  - keep `auto-plan-roadmap-proposal.md` as the only reviewer-facing roadmap draft
  - keep `auto-plan-state.yaml` as the only machine-readable draft state source
- if PRD approval is rejected or the PRD revision changes materially:
  - append structured stale-output records for WDS outputs
  - append structured stale-output records for architecture outputs
  - append structured stale-output records for draft epics/stories inputs
  - append structured stale-output records for readiness outputs
  - set `approval_markers.prd.status=rejected` when the current PRD revision is no longer approved and clear its `approved_revision`
  - downgrade `approval_markers.architecture` and `approval_markers.readiness` to `status=not_requested` and clear their approval metadata
  - clear any `automation_state.derived_from` entries that depend on the rejected PRD revision
- if architecture approval is rejected or the architecture revision changes materially:
  - append structured stale-output records for security review outputs when architecture changed materially
  - append structured stale-output records for system test design
  - append structured stale-output records for draft epics/stories inputs
  - append structured stale-output records for readiness outputs
  - set `approval_markers.architecture.status=rejected` when the current architecture revision is no longer approved and clear its `approved_revision`
  - downgrade `approval_markers.readiness` to `status=not_requested` and clear its approval metadata
  - clear any `automation_state.derived_from` entries that depend on the rejected architecture revision
- if readiness approval is rejected:
  - keep draft epics/stories and readiness outputs in draft locations
  - do not promote draft outputs into canonical execution locations
  - append structured stale-output records only for readiness outputs unless the rejection explicitly reopens architecture
- resume must regenerate every output listed in `automation_state.stale_outputs` before continuing
- resume must also regenerate any output whose `automation_state.derived_from.<artifact_key>.source_revisions` no longer match current `artifact_revisions`

Human approval checkpoints:

- roadmap activation or major roadmap reordering via `current/implementation/evidence/auto-plan-roadmap-proposal.md`
- final PRD acceptance via `current/implementation/evidence/auto-plan-prd-gate.md`
- final architecture acceptance via `current/implementation/evidence/auto-plan-architecture-gate.md`
- implementation-readiness approval via `current/testing/gates/draft/auto-plan-readiness-summary.md`
- security-lane activation if the activation mode is not already settled

Failure handling:

- write `partial-failure-report.md` output to `current/implementation/evidence/auto-plan-failure.md`
- if the failure occurs before `Phase Sync`, also write the fallback preflight failure artifact
- always record the failure in `auto-plan-state.yaml`
- if canonical `phase-state.yaml` exists, also set its `status` to `blocked`
- if canonical `phase-state.yaml` exists, also record `automation_state.last_failure_report`
- if canonical `phase-state.yaml` exists, also record `automation_state.last_completed_step`
- keep completed artifacts and record the last successful step

Resume behavior:

- if `--resume` is used, inspect `auto-plan-state.yaml` first, then reconcile with `phase-state.yaml` if it exists
- before `Phase Sync`, `auto-plan-state.yaml` is the sole machine-readable resume source
- `auto-plan-roadmap-proposal.md` is the only reviewer-facing roadmap draft artifact
- `auto-plan-report.md` is never used to determine resume position
- accepted outputs are only those with corresponding `approval_markers.<gate>.status=approved`, matching `approved_revision`, with no matching stale-output record in `automation_state.stale_outputs`, and whose `automation_state.derived_from.<artifact_key>.source_revisions` match current `artifact_revisions`
- skip completed steps only when outputs are accepted
- restart from the first missing, rejected, or revision-mismatched checkpoint
- if an approval was denied, resume from the first step associated with the denied checkpoint after stale outputs are regenerated
- if a lane is marked `skipped` or `not_applicable` in `lane_outcomes`, resume MUST not infer work for that lane from missing files

Final outputs:

- active roadmap state
- `auto-plan-state.yaml` as the canonical runtime record for the wrapper
- active phase state
- reviewer-facing gate artifacts for roadmap, PRD, architecture, and readiness
- detailed-analysis artifacts
- PRD and WDS outputs aligned to the current accepted PRD revision
- architecture outputs aligned to the current accepted architecture revision
- approved epics/stories promoted out of `draft/` only after readiness approval
- explicit lane outcome declarations for storytelling, WDS, and security in both runtime state and the readiness handoff
- `auto-plan-readiness-summary.md` as the canonical implementation-readiness handoff artifact only after readiness approval
- `auto-plan-report.md` as the execution log and run summary, not a resume surface

Example invocation:

```text
auto-plan --phase-id phase-002 --mode brownfield --approval-mode manual
```

Example outcome:

- brownfield repo context is refreshed
- roadmap proposal is drafted, then the canonical roadmap is updated only after approval
- `auto-plan-state.yaml` carries the machine-readable checkpoint state from preflight through readiness
- roadmap slice `phase-002` is activated only after roadmap approval
- WDS-triggered PRD edits force a second `Validate PRD` pass before the PRD gate can open
- detailed analysis, PRD, WDS, architecture, security artifacts if applicable, test design, CI/CD alignment, and readiness artifacts are drafted across staged approval checkpoints
- epics, stories, and readiness outputs stay in `draft/` locations until readiness approval is granted
- human review is required at roadmap, PRD, architecture, and readiness gates

#### `auto-epic-start`

Purpose:

- prepare one epic for execution by validating order, dependencies, test design, and baseline expectations

Prerequisites:

- `phase-state.yaml` exists and `workflow_status.solutioning` is `complete`
- target epic exists in `current/planning/epics/`
- prior epic cleanup is complete or explicitly acknowledged

Reads:

- `reference/planning/framework/current/phase.md`
- `reference/planning/framework/current/phase-state.yaml`
- epic definitions in `reference/planning/framework/current/planning/epics/`
- architecture docs
- relevant WDS outputs
- previous retrospective if this is not the first epic
- existing sprint status and evidence

Writes:

- `reference/planning/framework/current/implementation/evidence/epic-<epic-id>-start-report.md`
- `reference/planning/framework/current/testing/test-design/test-design-epic-<epic-id>.md`
- `reference/planning/framework/current/research/implementation/epic-<epic-id>-implementation-research.md` if needed

Exact step sequence:

1. Preflight the epic id, dependencies, and solutioning status.
2. Read epic scope, stories, dependencies, and architecture context.
3. Check prior epic cleanup items and unresolved blockers.
4. Order stories for execution and identify parallel-safe vs sequential work.
5. Run epic-level test design.
6. Run implementation brainstorming if delivery risk or ambiguity is high.
7. Run implementation research if the epic introduces new patterns, integrations, or constraints.
8. Write the epic start report with story order, risks, and ready-state summary.
9. Stop for human approval if epic scope or story order changed materially.

Human approval checkpoints:

- material epic scope expansion
- material story reordering caused by new dependencies
- newly introduced technical pattern that changes architecture assumptions

Failure handling:

- write `reference/planning/framework/current/implementation/evidence/epic-<epic-id>-start-failure.md`
- keep the prior epic state unchanged if the new epic is not ready
- set `next_checkpoint` in `phase-state.yaml` to the unresolved epic-start blocker

Resume behavior:

- if epic test design already exists and is accepted, skip regeneration
- if story ordering was already approved, resume from the next missing step

Final outputs:

- approved epic story order
- epic-level test design
- epic start report

Example invocation:

```text
auto-epic-start --phase-id phase-002 --epic-id epic-03 --approval-mode manual
```

Example outcome:

- story execution order is proposed
- epic-level testing is prepared
- the epic is either marked ready for story execution or blocked pending approval

#### `auto-story`

Purpose:

- automate the story loop from validation through implementation evidence, without bypassing review or risky-change approvals

Prerequisites:

- target story exists in `current/implementation/stories/`
- story dependencies are satisfied
- epic has been started and is ready

Reads:

- target story file
- `phase-state.yaml`
- relevant PRD, WDS, architecture, and epic artifacts
- existing codebase surfaces needed for the story
- prior reuse notes, ADRs, and shared patterns
- relevant tests and fixtures

Writes:

- updated story file in `current/implementation/stories/`
- reuse-check note in `current/implementation/evidence/`
- ATDD artifacts in `current/testing/test-design/`
- test automation artifacts in `current/testing/automation/`
- code review notes in `current/testing/reviews/`
- test review notes in `current/testing/reviews/`
- traceability report in `current/testing/gates/`
- `reference/planning/framework/current/implementation/evidence/story-<story-id>-run-report.md`
- `reference/planning/framework/current/implementation/evidence/story-<story-id>-gate-report.md` when approval is required

Exact step sequence:

1. Preflight story readiness and dependency completion.
2. Load the minimum context needed from PRD, WDS, architecture, epic, and codebase sources.
3. Validate the story and update it if validation findings are minor.
4. Run ATDD.
5. Run the required reuse scan and write reuse evidence.
6. Stop for approval if the story appears to require net-new architecture, destructive schema work, or another hard-stop condition.
7. Implement the story.
8. Run primary test automation.
9. Run QA automation only when API/E2E expansion is justified.
10. Run code review.
11. Run test review.
12. Run traceability.
13. Write the story run report and stop for merge approval.

Human approval checkpoints:

- any hard-stop change category
- net-new architecture or subsystem creation
- destructive schema or migration changes
- final merge or story-complete decision

Failure handling:

- write `reference/planning/framework/current/implementation/evidence/story-<story-id>-failure.md`
- keep the story in a non-closed state
- write the last successful step and open blockers into the story run report

Resume behavior:

- if ATDD exists and is accepted, do not rerun it unless the story changed materially
- if implementation is complete but reviews failed, resume at review remediation
- if automation artifacts exist, only regenerate the missing or invalid pieces

Final outputs:

- validated story
- reuse evidence
- implementation changes
- automation and review evidence
- traceability evidence
- merge-approval gate report

Example invocation:

```text
auto-story --phase-id phase-002 --epic-id epic-03 --story-id story-03-02 --approval-mode manual
```

Example outcome:

- the story is validated, implemented, tested, reviewed, and traced
- merge is blocked until human approval is given
- risky architectural or migration changes stop the run before irreversible work proceeds

#### `auto-epic-end`

Purpose:

- close the active epic cleanly by gathering evidence, producing the retrospective, updating docs, and preparing the next epic

Prerequisites:

- all in-scope stories in the epic are completed, deferred, or explicitly waived
- traceability and review outputs exist for completed stories

Reads:

- epic definition
- story files for the epic
- current implementation evidence
- testing and gate outputs
- sprint status
- current roadmap and phase state

Writes:

- `reference/planning/framework/current/implementation/retrospectives/epic-<epic-id>-retrospective.md`
- `reference/planning/framework/current/implementation/evidence/epic-<epic-id>-end-report.md`
- docs delta summary in `reference/planning/framework/current/implementation/evidence/epic-<epic-id>-docs-update.md`
- next-epic preview in `reference/planning/framework/current/implementation/evidence/epic-<next-epic-id>-preview.md` if another epic exists
- proposed phase-state updates

Exact step sequence:

1. Preflight epic completion and verify story statuses.
2. Gather testing, review, traceability, and implementation evidence.
3. Draft the retrospective.
4. Draft the docs delta and promotion candidates.
5. Draft the next-epic preview and identify carry-over items.
6. Draft any required phase-state updates.
7. Stop for human approval before marking the epic complete or advancing to the next epic.

Human approval checkpoints:

- epic-complete decision
- carry-over of incomplete or waived stories
- promotion of planning artifacts into stable docs
- advancing to the next epic when open blockers remain

Failure handling:

- write `reference/planning/framework/current/implementation/evidence/epic-<epic-id>-end-failure.md`
- do not mark the epic complete
- set `next_checkpoint` in `phase-state.yaml` to the unresolved epic-closeout action

Resume behavior:

- if the retrospective exists but docs delta is missing, resume from docs update
- if next-epic preview exists but approval is pending, resume at approval checkpoint

Final outputs:

- retrospective
- epic end report
- docs delta summary
- next-epic preview or final-epic note

Example invocation:

```text
auto-epic-end --phase-id phase-002 --epic-id epic-03 --approval-mode manual
```

Example outcome:

- the epic is either approved for closure or clearly blocked
- the next epic is previewed with carry-over and dependency notes
- docs updates and lessons candidates are prepared for human review

Implementation rule for all four commands:

- the command markdown specs in `reference/BMAD/tools/automation/commands/` should use this exact structure:
  - purpose
  - prerequisites
  - reads
  - writes
  - exact step sequence
  - approval checkpoints
  - failure handling
  - resume behavior
  - final outputs
  - example invocation
  - example outcome

### 9. Reuse Policy

Before `Dev Story`, the workflow or automation must perform a reuse scan in this order:

1. existing UI components
2. existing domain services
3. existing data-access layers and queries
4. existing integration clients
5. existing shared utilities and types
6. existing test fixtures and helpers
7. prior architectural patterns and ADRs

Required evidence:

- a short reuse note in `current/implementation/evidence/`
- what was searched
- what existing candidates were found
- what was reused or extended
- if net-new code is introduced, why extension or reuse was not chosen

Allowed justifications for net-new code:

- no suitable existing asset exists
- the existing asset is unsafe to extend
- extension would create worse coupling than a new isolated unit
- regulatory or security isolation requires a separate implementation

Code review rule:

- if a story introduces a new subsystem or major new abstraction without reuse evidence, code review should fail until justification is documented

### 10. Promotion Path Out Of `reference`

There are three different destinations:

1. historical planning artifacts remain in `reference/planning/`
2. stable human-facing documentation graduates into the repo `docs/` tree
3. stable BMAD method assets graduate into `src/`

#### Promotion to human docs

A planning artifact may move from `reference/planning/` into the repo docs tree only when:

- the content is stable for the current phase or repo baseline
- an owner is assigned
- lifecycle state is set
- the destination docs location is defined
- the artifact has been reviewed for structure, terminology, and links

#### Promotion to `src/`

A BMAD method asset may move from `reference/BMAD/` into `src/` only when:

- the workflow and command contract is approved
- the asset has survived at least two real usage cycles without structural rewrite
- required templates and output rules are stable
- owner and maintenance boundary are assigned
- packaging/runtime assumptions are defined

Non-promotion rule:

- project-specific roadmap and phase artifacts never move into `src/`

### 11. Template Inventory

#### Planning templates to create

```text
reference/planning/templates/
├── roadmap/
│   ├── high-level-brainstorm.md
│   ├── market-research.md
│   ├── domain-research.md
│   ├── technical-research.md
│   ├── innovation-strategy.md
│   ├── opportunity-framing.md
│   ├── storytelling.md
│   ├── high-level-product-brief.md
│   ├── roadmap.md
│   └── roadmap.yaml
├── phase/
│   ├── phase.md
│   ├── phase-state.yaml
│   ├── detailed-brainstorm.md
│   ├── detailed-market-research.md
│   ├── detailed-domain-research.md
│   ├── detailed-technical-research.md
│   ├── detailed-innovation-strategy.md
│   ├── detailed-opportunity-framing.md
│   └── detailed-product-brief.md
└── implementation/
    ├── reuse-check.md
    ├── readiness-summary.md
    └── phase-closeout-summary.md
```

#### Automation templates to create or refine

```text
reference/BMAD/tools/automation/templates/
├── auto-plan-report.md
├── epic-start-report.md
├── story-run-report.md
├── epic-end-report.md
├── handoff-template.md
├── partial-failure-report.md
├── story-gate-report.md
└── roadmap-state-update.md
```

Additional automation templates required:

- `reference/BMAD/tools/automation/templates/auto-plan-state.yaml`
- `reference/BMAD/tools/automation/templates/approval-gate-report.md`

### 12. Cross-Repo Rollout Rule

Universal across Compass repos:

- the roadmap-driven BMAD phase model
- the `roadmap.md` and `roadmap.yaml` contract
- the `phase.md` and `phase-state.yaml` contract
- the WDS insertion point
- the conditional security-lane model
- the reuse policy
- the automation wrapper names and approval boundaries

Repo-specific:

- actual roadmap content
- whether storytelling remains a separate lane
- CI/CD alignment details
- technology-specific templates or prompts
- repo docs destinations and cross-links

Exception rule:

- repos may not silently fork the universal contract
- any repo-specific deviation requires owner, rationale, scope, and expiry

Rollout sequence:

1. define and validate the method in `compass-engine`
2. pilot it in one downstream Compass repo
3. validate it in a second repo with a meaningfully different stack or lifecycle
4. only then treat it as the standard rollout baseline

### 13. Polyrepo Compass Brand Operating Model

Compass Brand should use one BMAD method across three operating levels:

- workspace root: portfolio orchestration
- parent repos with child repos: domain or program orchestration
- leaf repos: repo-local delivery

Authority rules:

- the actual nested repo root is authoritative for its own docs and planning state
- parent and workspace repos coordinate child workstreams but do not own child repo-local PRDs, architecture, stories, or implementation evidence
- `repositories.yaml` is the authoritative topology map for repo ids, paths, parent-child relationships, and repo-root ownership
- `initiative-index.yaml` is the authoritative concurrent-work index for workspace and orchestration repos

Polyrepo control surfaces:

- deployed repos always use `docs/`, `planning/roadmap/`, `planning/current/`, `planning/previous/`, and `planning/lessons/`
- workspace and orchestration repos also use:
  - `planning/repositories.yaml`
  - `planning/current/initiative-index.yaml`
  - `planning/current/initiatives/<initiative-id>/`

Concurrency rules:

- multiple active workspace or orchestration initiatives are allowed
- overlap on the same repo, shared interface, or shared release boundary must be explicitly gated
- repo-local execution still happens inside the authoritative target repo

Workflow implications:

1. `Initialize Planning` must detect `workspace`, `orchestration`, or `delivery` scope and scaffold the required control surfaces for that scope.
2. `Project Roadmap` must capture execution scope and repo targets for orchestration-level phases.
3. `Phase Sync` must copy execution scope and repo targets into `phase-state.yaml`.
4. `Initiative Routing` must fan orchestration phases into concurrent repo-targeted initiative workstreams without creating repo-local delivery artifacts.
5. `Phase Closeout` must update initiative routing state when the phase used workspace or orchestration scope.

## Phase Structure

## Phase 0: Lock The Working Surface

### Goal

Stop arguing with incorrect repo docs and explicitly define where work happens during planning.

### Exact work

1. Treat `reference/BMAD/modules/custom/bmm` as the working BMAD module.
2. Treat `reference/BMAD/modules/custom/core` as the working custom core module.
3. Treat `reference/BMAD/BMAD-workflow.md` plus `module-help.csv` as the active flow definition.
4. Treat `_planning/current/planning` as the implementation-plan and alignment space.
5. Do not touch `src/` as part of BMAD feature work in this phase.

### Deliverables

- this implementation plan updated to reflect `reference`-first work
- clear agreement that `src` is deferred

### Acceptance criteria

- all new BMAD method-development work for this initiative is scoped to `reference/BMAD/`
- no new tasks in this initiative require `src` changes yet

## Phase 1: Lock The Planning And Documentation Framework Contract

### Goal

Make the planning and documentation framework explicit enough to support roadmap-driven BMAD before deeper workflow rollout proceeds.

### Exact work

1. Treat `reference/planning/framework/` as the planning source of truth for artifact destinations.
2. Treat `reference/documentation/` as the documentation source of truth for human and AI documentation standards.
3. Add the missing planning framework contract to this implementation plan:
   - roadmap-level artifact model
   - active-phase artifact model
   - exact contract for `roadmap.md`, `roadmap.yaml`, `phase.md`, and `phase-state.yaml`
4. Define the required framework expansions:
   - roadmap-level high-level analysis lanes
   - current-phase detailed-analysis lanes
   - WDS and CYBERSEC output placement
5. Define the documentation framework follow-up:
   - planning-artifact promotion into human docs
   - future AI-documentation standards

### Files expected to change later in implementation

- `reference/planning/framework/roadmap/roadmap.md`
- `reference/planning/framework/roadmap/roadmap.yaml`
- `reference/planning/framework/current/phase.md`
- `reference/planning/framework/current/phase-state.yaml`
- `reference/planning/docs/workflow-map.md`
- `reference/planning/docs/conventions.md`
- `reference/planning/docs/how-to-use.md`
- `reference/planning/docs/phase-closeout-checklist.md`
- `reference/documentation/README.md`
- `reference/documentation/human/policies/documentation-governance.md`
- `reference/documentation/ai/README.md`

### Acceptance criteria

- the roadmap-driven planning model is explicitly defined
- the four core roadmap/phase artifacts have a concrete contract
- framework expansion work is identified before workflow outputs are remapped

## Phase 2: Baseline Compass Extension Map Inside `reference/BMAD`

### Goal

Define exactly what will be changed inside the active custom BMM layer before importing anything.

### Exact work

1. Add an extension inventory file inside the working BMAD layer:
   - `reference/BMAD/modules/custom/bmm/COMPASS-EXTENSION-MAP.md`
2. Record in that file:
   - selected source repos
   - selected workflows
   - rejected workflows
   - target insertion points
   - proposed command names
   - output destinations
3. Add an automation inventory file:
   - `reference/BMAD/tools/automation/README.md`
4. Define the planning-phase folder contract for automation specs:
   - `reference/BMAD/tools/automation/commands/`
   - `reference/BMAD/tools/automation/policies/`
   - `reference/BMAD/tools/automation/templates/`

### Files expected to change

- `reference/BMAD/modules/custom/bmm/COMPASS-EXTENSION-MAP.md`
- `reference/BMAD/tools/automation/README.md`

### Acceptance criteria

- every planned import has a target path before copying work begins
- automation design has an explicit home in `reference/BMAD/`

## Phase 3: Add CIS Workflows Into The Active Custom BMM Layer

### Goal

Add the best early-phase CIS workflows into the existing `custom/bmm` module without forking the flow.

### Selected workflows

- Innovation Strategy
- Design Thinking
- Problem Solving

### Proposed target paths

- `reference/BMAD/modules/custom/bmm/workflows/1-analysis/innovation-strategy/`
- `reference/BMAD/modules/custom/bmm/workflows/1-analysis/design-thinking/`
- `reference/BMAD/modules/custom/bmm/workflows/anytime/problem-solving/`

### Why these placements

- Innovation Strategy belongs in Phase 1 because it sharpens positioning and value before brief/PRD work.
- Design Thinking belongs in Phase 1 because it improves user/problem understanding before specification.
- Problem Solving should be an anytime lane, because its value is highest when the team gets stuck during planning or implementation.

### Exact work

1. Copy only the selected CIS workflows, templates, and supporting files.
2. Normalize names and references so they fit the existing `custom/bmm` folder scheme.
3. Add corresponding rows to `reference/BMAD/modules/custom/bmm/module-help.csv`.
4. Add the workflows to `reference/BMAD/BMAD-workflow.md`.
5. Define output destinations for each:
   - Innovation Strategy -> roadmap research lane
   - Design Thinking -> roadmap strategy lane as `opportunity framing` unless Compass chooses a different artifact name
   - Problem Solving -> current research or evidence lane depending context

### Proposed command names

- `bmad-cis-innovation-strategy`
- `bmad-cis-design-thinking`
- `bmad-cis-problem-solving`

### Flow insertion

Recommended Phase 1 sequence after import:

1. Brainstorm Project
2. Market Research
3. Domain Research
4. Technical Research
5. Innovation Strategy
6. Design Thinking
7. Create Brief

Problem Solving remains outside the linear gate chain as an anytime lane.

### Acceptance criteria

- all three CIS workflows exist under `reference/BMAD/modules/custom/bmm`
- `module-help.csv` includes them
- `BMAD-workflow.md` shows their position
- no duplicate brainstorming lane is introduced

## Phase 4: Add WDS UX And Handoff Lane Into The Active Custom BMM Layer

### Goal

Add a stronger bridge from PRD to UX and implementation-ready design handoff.

### Selected workflows

- Trigger Mapping
- Outline Scenarios
- Conceptual Specifications
- Design Delivery

### Deferred workflow

- Product Evolution

### Proposed target paths

- `reference/BMAD/modules/custom/bmm/workflows/2-plan-workflows/trigger-mapping/`
- `reference/BMAD/modules/custom/bmm/workflows/2-plan-workflows/outline-scenarios/`
- `reference/BMAD/modules/custom/bmm/workflows/2-plan-workflows/conceptual-specifications/`
- `reference/BMAD/modules/custom/bmm/workflows/2-plan-workflows/design-delivery/`

### Exact work

1. Copy only the selected WDS workflows and required templates/checklists.
2. Normalize naming and references to fit `custom/bmm`.
3. Add corresponding rows to `module-help.csv`.
4. Update `BMAD-workflow.md` with the agreed sequence.
5. Define output destinations for all four workflows in the UX planning lane.

### Proposed command names

- `bmad-wds-trigger-mapping`
- `bmad-wds-outline-scenarios`
- `bmad-wds-conceptual-specifications`
- `bmad-wds-design-delivery`

### Recommended flow insertion

Recommended Phase 2 sequence after import:

1. Phase Sync
2. Create PRD
3. Validate PRD
4. Trigger Mapping
5. Outline Scenarios
6. Create UX
7. Conceptual Specifications
8. Design Delivery
9. Update Docs (Planning)

Current recommendation:

- keep WDS after PRD and before architecture
- use `Edit PRD` as the formal loop-back point if WDS exposes requirement gaps
- revisit moving WDS earlier only if Compass decides the PRD should be fully downstream of trigger/scenario work

### Output destinations

All four should map into the UX planning lane and support downstream architecture and implementation:

- trigger mapping -> current UX planning artifacts
- outline scenarios -> current UX planning artifacts
- conceptual specs -> current UX planning artifacts
- design delivery -> current UX planning artifacts

### Acceptance criteria

- the WDS lane lives inside `custom/bmm`
- the WDS lane has a clear entry and exit point
- the WDS lane enriches existing Compass planning instead of replacing it

## Phase 5: Add Conditional CYBERSEC Lane Into The Active Custom BMM Layer

### Goal

Add security-specific planning and gate logic without making it mandatory for every project.

### Selected workflows

- Threat Modeling
- Security Architecture Review
- Secure Gate Criteria

### Proposed target paths

- `reference/BMAD/modules/custom/bmm/workflows/3-solutioning/threat-modeling/`
- `reference/BMAD/modules/custom/bmm/workflows/3-solutioning/security-architecture-review/`
- `reference/BMAD/modules/custom/bmm/workflows/4-implementation/secure-gates/`

### Exact work

1. Copy only the selected CYBERSEC workflows, templates, and gate rules.
2. Exclude unrelated legal, intel, and strategy packs from this rollout.
3. Add a security activation note:
   - `reference/BMAD/modules/custom/bmm/workflows/0-governance/security-activation.md`
4. Add corresponding rows to `module-help.csv`.
5. Update `BMAD-workflow.md` to show the conditional lane.
6. Define security output destinations:
   - threat models -> architecture lane
   - security architecture review -> architecture/evidence lane
   - secure gates -> testing/evidence lane

### Proposed command names

- `bmad-cybersec-threat-modeling`
- `bmad-cybersec-security-architecture-review`
- `bmad-cybersec-secure-gates`

### Recommended conditional insertion

Recommended Phase 3 conditional sequence:

1. Create Architecture
2. Threat Modeling if security lane is activated
3. Security Architecture Review if security lane is activated
4. Test Design
5. Create Epics and Stories
6. Check Implementation Readiness

Secure gate checks also appear later in implementation and release boundaries.

### Activation conditions

- auth-heavy or permissions-heavy systems
- payment or customer-data handling
- regulated work
- public-facing attack surface
- explicit security artifact requirements

### Acceptance criteria

- the security lane is available in the working BMAD layer
- it is conditional, not mandatory
- its artifact destinations are explicitly defined

## Phase 6: Define Automation As Reference-Stage Specs

### Goal

Design automation around the BMAD flow without productizing it yet.

### Important rule

In this phase, automation is a spec and workflow-definition effort inside `reference/BMAD/`.
It is not yet a `src` command implementation effort.

### Proposed automation spec structure

```text
reference/BMAD/tools/automation/
├── README.md
├── commands/
│   ├── auto-plan.md
│   ├── auto-epic-start.md
│   ├── auto-story.md
│   └── auto-epic-end.md
├── policies/
│   ├── context-budgeting.md
│   ├── patching-strategy.md
│   └── state-model.md
└── templates/
    ├── handoff-template.md
    └── partial-failure-report.md
```

### Exact work

1. Write phase-based automation command specs:
   - `auto-plan`
   - `auto-epic-start`
   - `auto-story`
   - `auto-epic-end`
2. Base them on the current Compass BMAD order in `BMAD-workflow.md`.
3. Keep `bd` as the task system in all specs.
4. Explicitly reject TodoWrite as the state model.
5. Define structured handoff requirements.
6. Define partial-failure reporting.
7. Define resume boundaries.
8. Keep automation v1 sequential by default.
9. Prioritize automation in this order:
   - research workflows
   - validation and review routing
   - traceability and gate evidence
   - roadmap and phase state updates
10. Do not automate brainstorming, brief, PRD, or architecture generation end-to-end in v1.
11. Define a `reuse scan` requirement before `Dev Story`:
   - search for existing components, services, queries, and patterns
   - require justification when new code is introduced instead of reusing existing assets
12. Treat CodeRabbit or similar review tooling as checkpoint automation at story-exit or PR boundaries, not as a mandatory per-commit step.
13. Each automation command spec must include:
   - purpose
   - prerequisites
   - reads
   - writes
   - exact step sequence
   - approval checkpoints
   - failure handling
   - resume behavior
   - final outputs
   - example invocation
   - example outcome

### Inputs to use

- `reference/BMAD/BMAD-workflow.md`
- `reference/BMAD/modules/custom/bmm/module-help.csv`
- `reference/BMAD/research/bmad-automation-plugin/**`
- `reference/BMAD/research/bmad-automation-script/**`
- `reference/BMAD/research/meta-handover-documentation.md`

### Acceptance criteria

- all four automation phases are specified in `reference/BMAD/tools/automation/commands/`
- the state model is clearly documented as BMAD artifacts plus `bd`
- each automation command has an explicit implementation contract and example run
- no runtime packaging assumptions are required yet

## Phase 7: Update Output Mapping, Planning Conventions, And Documentation Handoffs

### Goal

Ensure every new workflow has an explicit artifact destination in the Compass planning model and a clear path into the documentation framework when it stabilizes.

### Exact work

1. Update the reference planning map to include new artifact types:
   - high-level brainstorm outputs
   - high-level market/domain/technical research outputs
   - innovation strategy outputs
   - opportunity framing or design thinking outputs
   - storytelling outputs if retained
   - roadmap markdown and yaml state outputs
   - detailed brainstorm outputs
   - detailed market/domain/technical research outputs
   - phase markdown and yaml state outputs
   - trigger maps
   - scenario outlines
   - conceptual specs
   - design delivery artifacts
   - threat models
   - security review notes
   - secure gate reports
   - automation handoff reports
2. Update:
   - `reference/planning/docs/workflow-map.md`
   - `reference/planning/docs/conventions.md`
   - `reference/planning/docs/how-to-use.md`
   - `reference/planning/docs/phase-closeout-checklist.md`
   - `reference/planning/framework/README.md`
   - `reference/planning/framework/roadmap/README.md`
   - `reference/planning/framework/current/README.md`
   - `reference/documentation/human/policies/documentation-governance.md`
   - `reference/documentation/ai/README.md`
   - any supporting files in `reference/planning/framework/` if needed

### Proposed artifact placement

- strategic outputs -> roadmap research or strategy lane depending type
- UX enrichment outputs -> current planning UX lane
- threat/security outputs -> architecture, testing, or evidence lanes depending type
- automation reports -> implementation evidence or testing lane depending scope
- roadmap markdown/yaml -> `reference/planning/framework/roadmap/`
- phase markdown/yaml -> `reference/planning/framework/current/`

### Documentation handoff rule to define

Add an explicit rule that planning artifacts remain in `reference/planning/` until they are stable, then graduate into the destination human docs tree under the documentation framework with an owner, lifecycle state, and replacement link if the planning artifact is later archived.

### Acceptance criteria

- every added workflow in `module-help.csv` has a corresponding planning destination
- no new workflow depends on ambiguous output placement

## Phase 8: Alignment Review Before Productization

### Goal

Decide whether the reference-stage BMAD design is stable enough to move into `src`.

### Readiness criteria

All of the following should be true before `src` enters scope:

1. `BMAD-workflow.md` reflects the agreed Compass flow.
2. `module-help.csv` reflects the agreed command catalog.
3. CIS, WDS, and CYBERSEC lanes are present in the working BMAD layer.
4. Automation phase specs exist in `reference/BMAD/tools/automation/`.
5. The roadmap-driven planning framework contract is explicit.
6. Output mapping is explicit for all new artifacts.
7. Documentation handoff rules are defined for stable planning artifacts.
8. You have reviewed and approved the flow shape.

### Output of this phase

A separate productization plan that answers:

- what moves from `reference/BMAD/` into `src/`
- what becomes buildable/distributable
- what becomes actual `.claude` command/runtime assets
- what remains reference-only

Current Phase 8 decision:

- the reference layer is ready for productization planning
- the reference layer is not yet ready for direct `src/` migration
- see `_planning/current/planning/2026-03-13-bmad-reference-productization-plan.md`

## Recommended Execution Order

1. Phase 0: lock the working surface
2. Phase 1: planning and documentation framework contract
3. Phase 2: extension map
4. Phase 3: CIS lane
5. Phase 4: WDS lane
6. Phase 5: CYBERSEC lane
7. Phase 6: automation specs
8. Phase 7: output mapping and documentation handoff
9. Phase 8: productization gate

## Existing Tracking

- `bmad-engine-509` - security extension lane
- `bmad-engine-8gj` - WDS design extension lane
- `bmad-engine-uzd` - targeted CIS workflows
- `bmad-engine-lny` - optional oversight and memory substrate
- `bmad-engine-k0b` - phase-based automation coordinator
- `bmad-engine-vm7` - automation patching, context budgeting, handoff model
- `bmad-engine-2tk` - parallel story execution with worktrees and merge gates
- `bmad-engine-3hi` - detailed implementation plan and alignment

## Recommended Defaults For Alignment

These are my current recommendations:

1. Keep using `reference/BMAD/modules/custom/bmm` as the working BMAD layer.
2. Add CIS first.
3. Add WDS second.
4. Add CYBERSEC third as a conditional lane.
5. Define automation specs in `reference/BMAD/tools/automation/`.
6. Keep `src` out of scope until the method design is approved.
7. Treat `Phase Sync` as the roadmap-slice selection workflow.
8. Prefer many smaller planning artifacts over a few large ones.

## Key Decisions To Settle Together

1. Do you want to keep extending `reference/BMAD/modules/custom/bmm`, or do you want to create a new custom module inside `reference/BMAD/modules/custom/` now?
2. Do you want Problem Solving as an anytime lane, or do you want it forced into Phase 1?
3. Is the proposed WDS sequence correct:
   - Create PRD
   - Validate PRD
   - Trigger Mapping
   - Outline Scenarios
   - Create UX
   - Conceptual Specifications
   - Design Delivery
4. Do you want the security lane to activate only by explicit choice, or should the workflow also recommend activation heuristically?
5. Do you want storytelling to remain a distinct roadmap artifact lane, or should it fold into the high-level product brief?
6. Do you want the design-thinking output named `opportunity framing`, or do you want a different artifact name?
7. Do you want automation specs stored under `reference/BMAD/tools/automation/`, or somewhere inside `reference/BMAD/modules/custom/bmm/`?

## Recommended Starting Point

My recommendation is:

1. keep the working layer as `reference/BMAD/modules/custom/bmm`
2. settle the roadmap and phase artifact contract
3. settle the WDS insertion order
4. settle where automation specs should live
5. then implement the CIS lane first

That keeps the next change set small and avoids solving productization before the method itself is aligned.
