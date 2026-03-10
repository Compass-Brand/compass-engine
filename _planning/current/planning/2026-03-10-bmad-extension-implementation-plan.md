# Compass BMAD Extension And Automation Implementation Plan

Status: Draft for alignment
Date: 2026-03-10
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

The first implementation track should do five things:

1. Continue extending the existing custom BMAD layer in `reference/BMAD/modules/custom/bmm`.
2. Add the selected CIS, WDS, and CYBERSEC workflows into that working layer.
3. Define the automation layer as reference-stage specs and workflow wrappers, not production runtime assets.
4. Update the reference planning/output model so new artifacts have explicit destinations.
5. Defer `src` migration and distribution wiring until the BMAD shape is actually stable.

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
5. a clear output mapping for new artifacts into the Compass planning structure
6. a separate later-phase productization plan for migrating stable method assets into `src/`

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

## Phase 1: Baseline Compass Extension Map Inside `reference/BMAD`

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

## Phase 2: Add CIS Workflows Into The Active Custom BMM Layer

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
   - Design Thinking -> roadmap research lane
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

## Phase 3: Add WDS UX And Handoff Lane Into The Active Custom BMM Layer

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

## Phase 4: Add Conditional CYBERSEC Lane Into The Active Custom BMM Layer

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

## Phase 5: Define Automation As Reference-Stage Specs

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

### Inputs to use

- `reference/BMAD/BMAD-workflow.md`
- `reference/BMAD/modules/custom/bmm/module-help.csv`
- `reference/BMAD/research/bmad-automation-plugin/**`
- `reference/BMAD/research/bmad-automation-script/**`
- `reference/BMAD/research/meta-handover-documentation.md`

### Acceptance criteria

- all four automation phases are specified in `reference/BMAD/tools/automation/commands/`
- the state model is clearly documented as BMAD artifacts plus `bd`
- no runtime packaging assumptions are required yet

## Phase 6: Update Output Mapping And Planning Conventions

### Goal

Ensure every new workflow has an explicit artifact destination in the Compass planning model.

### Exact work

1. Update the reference planning map to include new artifact types:
   - innovation strategy outputs
   - design thinking outputs
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
   - any supporting files in `reference/planning/framework/` if needed

### Proposed artifact placement

- strategic outputs -> roadmap research lane
- UX enrichment outputs -> current planning UX lane
- threat/security outputs -> architecture, testing, or evidence lanes depending type
- automation reports -> implementation evidence or testing lane depending scope

### Acceptance criteria

- every added workflow in `module-help.csv` has a corresponding planning destination
- no new workflow depends on ambiguous output placement

## Phase 7: Alignment Review Before Productization

### Goal

Decide whether the reference-stage BMAD design is stable enough to move into `src`.

### Readiness criteria

All of the following should be true before `src` enters scope:

1. `BMAD-workflow.md` reflects the agreed Compass flow.
2. `module-help.csv` reflects the agreed command catalog.
3. CIS, WDS, and CYBERSEC lanes are present in the working BMAD layer.
4. Automation phase specs exist in `reference/BMAD/tools/automation/`.
5. Output mapping is explicit for all new artifacts.
6. You have reviewed and approved the flow shape.

### Output of this phase

A separate productization plan that answers:

- what moves from `reference/BMAD/` into `src/`
- what becomes buildable/distributable
- what becomes actual `.claude` command/runtime assets
- what remains reference-only

## Recommended Execution Order

1. Phase 0: lock the working surface
2. Phase 1: extension map
3. Phase 2: CIS lane
4. Phase 3: WDS lane
5. Phase 4: CYBERSEC lane
6. Phase 5: automation specs
7. Phase 6: output mapping
8. Phase 7: productization gate

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
5. Do you want automation specs stored under `reference/BMAD/tools/automation/`, or somewhere inside `reference/BMAD/modules/custom/bmm/`?

## Recommended Starting Point

My recommendation is:

1. keep the working layer as `reference/BMAD/modules/custom/bmm`
2. settle the WDS insertion order
3. settle where automation specs should live
4. then implement the CIS lane first

That keeps the next change set small and avoids solving productization before the method itself is aligned.
