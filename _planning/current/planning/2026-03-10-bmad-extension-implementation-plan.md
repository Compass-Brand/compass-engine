# Compass BMAD Extension and Automation Implementation Plan

Status: Draft for alignment
Date: 2026-03-10
Owner: Trevor Leigh / Compass Engine

## Objective

Implement the selected BMAD improvements in `compass-engine` as a controlled rollout, not as a wholesale import.

The implementation will do four things:

1. Establish a real Compass BMAD customization source of truth in this repo.
2. Add the selected CIS, WDS, and CYBERSEC workflows as Compass-native extensions.
3. Add a first automation layer around BMAD using phase-based orchestration.
4. Leave POV oversight, AI memory, and advanced parallel execution as explicitly deferred follow-on work.

## Scope

### In scope for the first rollout

- BMAD source-of-truth cleanup and distribution path
- one Compass custom BMAD module scaffolded from upstream
- CIS workflow imports:
  - innovation strategy
  - design thinking
  - problem solving
- WDS workflow imports:
  - trigger mapping
  - outline scenarios
  - conceptual specifications
  - design delivery
- CYBERSEC workflow imports:
  - threat modeling
  - security architecture review
  - secure gate criteria
- Claude-first automation wrapper commands:
  - auto-plan
  - auto-epic-start
  - auto-story
  - auto-epic-end
- context budgeting, handoff, and artifact validation for automation

### Explicitly out of scope for the first rollout

- importing any adjacent repo wholesale
- replacing `bd` with another task system
- POV oversight as a default required lane
- AI memory hooks as a default required dependency
- Codex/OpenCode automation parity before Claude automation is stable
- story-parallel worktree execution before single-story automation is proven

## Current-State Constraints Found In The Repo

These are not theoretical. They are current implementation blockers in this repo.

1. `src/bmad/modules/` is documented as the canonical BMAD customization location, but it currently contains only [README.md](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/src/bmad/modules/README.md).
2. The build pipeline in [build.js](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/tools/build.js) does not build a BMAD bundle at all.
3. The sync pipeline in [push.js](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/tools/push.js) has no `_bmad` target.
4. The validation pipeline in [validate.js](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/tools/validate.js) only checks that `src/bmad/modules` exists, not that any actual module or distributable BMAD output exists.
5. The repo docs say `src/` is canonical, but `src/claude/` currently contains only templates while live runtime content still exists in top-level `.claude/`.
6. [README.md](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/README.md) and the BMAD development docs describe a publishable `_bmad/` surface, but that publish path is not actually wired into build/sync.
7. [src/planning/README.md](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/src/planning/README.md) describes planning templates, but the template files are not present under `src/planning/`.

Because of those gaps, the rollout has to start with foundation work before feature imports.

## Recommended Alignment Decisions

These are the decisions I recommend locking before implementation starts.

### Decision 1: Canonical BMAD source location

Recommendation:

- author BMAD customizations in `src/bmad/modules/`
- publish them to `dist/_bmad/`
- sync them to downstream repos as `_bmad/`

Why:

- it matches the existing documentation direction
- it avoids editing `BMAD-METHOD/`
- it keeps upstream sync and Compass customization separate

### Decision 2: Canonical command-authoring location

Recommendation:

- treat `src/claude/` as the only authored source
- treat top-level `.claude/` as generated/runtime content only

Why:

- the docs already claim this model
- build/push already assume this model
- automation commands should not be authored directly in runtime output

### Decision 3: Module shape

Recommendation:

- start with one primary custom module: `compass-bmm`
- keep external-source provenance inside that module
- only split into multiple Compass modules later if the module becomes too large

Why:

- faster to stand up
- simpler distribution path
- easier to reason about than four new modules at once

### Decision 4: Automation rollout surface

Recommendation:

- deliver automation v1 in Claude first
- keep Codex/OpenCode parity as a later adapter step

Why:

- Claude has the clearest current command model in repo docs
- the automation research was heavily Claude-oriented
- cross-platform parity is easier after workflow semantics are stable

### Decision 5: First-release scope cutoff

Recommendation:

- first release = foundation + CIS + WDS + conditional CYBERSEC + automation foundation
- later release = POV sidecars + AI memory + worktree parallelism

Why:

- this keeps the first rollout useful without mixing core lane work with advanced orchestration experiments

## Target End-State

After the first rollout, the repo should have:

1. a real Compass BMAD source tree under `src/bmad/modules/compass-bmm/`
2. a real BMAD distribution output under `dist/_bmad/`
3. a push target that can sync `_bmad/` into downstream repos
4. Claude automation commands in `src/claude/commands/bmad/`
5. Compass documentation updated so the documented workflow matches the implementation
6. a clear separation between:
   - upstream BMAD
   - Compass custom BMAD
   - automation wrappers
   - deferred sidecars

## Phased Implementation Plan

## Phase 0: Foundation And Source-Of-Truth Cleanup

### Goal

Make the repo internally consistent before adding BMAD features.

### Exact work

1. Create the missing authored Claude source directories under `src/claude/`:
   - `src/claude/agents/`
   - `src/claude/commands/`
   - `src/claude/skills/`
   - `src/claude/rules/`
   - `src/claude/contexts/`
   - `src/claude/config/`
   - `src/claude/scripts/`
2. Move authored runtime content from top-level `.claude/` into `src/claude/` where appropriate.
3. Add BMAD bundle support to [tools/build.js](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/tools/build.js):
   - `src/bmad/` -> `dist/_bmad/`
4. Add BMAD sync target to [tools/push.js](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/tools/push.js):
   - target name: `bmad`
   - dist source: `dist/_bmad`
   - destination: `_bmad`
5. Strengthen [tools/validate.js](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/tools/validate.js) so it validates:
   - actual BMAD module presence
   - actual BMAD build output after `npm run build`
   - actual Claude authored directories expected by docs
6. Reconcile docs so they describe the real source/build/sync model:
   - [README.md](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/README.md)
   - [build.md](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/docs/architecture/build.md)
   - [sync.md](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/docs/architecture/sync.md)
   - [modifying-bmad.md](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/docs/development/bmad/modifying-bmad.md)
   - [modifying-claude.md](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/docs/development/claude/modifying-claude.md)

### Files and directories expected to change

- `tools/build.js`
- `tools/push.js`
- `tools/validate.js`
- `src/claude/**`
- `src/bmad/**`
- `docs/architecture/**`
- `docs/development/bmad/**`
- `docs/development/claude/**`
- `README.md`

### Deliverables

- consistent authored source tree in `src/`
- distributable BMAD bundle in `dist/_bmad/`
- push support for `_bmad/`
- corrected documentation

### Acceptance criteria

- `npm run build` produces `dist/_bmad/`
- `npm run push -- --targets bmad --dry-run` works
- docs no longer describe nonexistent authored directories or outputs
- new BMAD work can be added without editing top-level runtime folders directly

## Phase 1: Scaffold The Compass BMAD Module

### Goal

Create the actual Compass BMAD customization base that all later workflow imports will land in.

### Exact work

1. Scaffold `compass-bmm` from upstream `bmm` using [create-bmad-module.js](C:/Users/Trevor%20Leigh/Desktop/compass-brand/compass-brand/compass-forge/compass-engine/tools/create-bmad-module.js):

```bash
npm run create:bmad-module -- --name compass-bmm --from bmm --code cbmm
```

2. Add module-level provenance documentation inside `src/bmad/modules/compass-bmm/`:
   - imported workflow source repos
   - selection rationale
   - what was intentionally excluded
3. Add a Compass extension manifest that maps each imported lane to:
   - source repo
   - target workflow path
   - expected invocation point in Compass BMAD
   - output artifact destination
4. Define internal naming conventions for imported workflows and companion command aliases.

### Target directory shape

```text
src/bmad/modules/compass-bmm/
├── module.yaml
├── custom-module.json
├── README.md
├── COMPASS-EXTENSIONS.md
├── imports/
│   ├── cis.md
│   ├── wds.md
│   └── cybersec.md
└── workflows/
```

### Acceptance criteria

- `src/bmad/modules/compass-bmm/` exists and builds into the BMAD output
- provenance is documented inside the module
- the module is the single import target for the selected first-rollout lanes

## Phase 2: Add CIS Discovery Lane

### Goal

Improve upstream product/discovery quality before PRD and architecture work.

### Exact workflows to add

| Workflow | Source repo | Proposed target path in `compass-bmm` | Use |
| --- | --- | --- | --- |
| Innovation Strategy | `bmad-module-creative-intelligence-suite` | `workflows/1-analysis/innovation-strategy/` | clarify competitive angle and positioning |
| Design Thinking | `bmad-module-creative-intelligence-suite` | `workflows/1-analysis/design-thinking/` | deepen user/problem understanding |
| Problem Solving | `bmad-module-creative-intelligence-suite` | `workflows/1-analysis/problem-solving/` | structured stuck-state / decision support |

### Exact work

1. Copy only the selected CIS workflows, templates, and supporting instructions into `compass-bmm`.
2. Normalize naming, metadata, and outputs to Compass conventions.
3. Update module help / manifest surfaces so the workflows are discoverable.
4. Create Claude command adapters for invocation under `src/claude/commands/bmad/`.
5. Update planning guidance so these workflows sit before product brief / PRD creation.

### Expected command surface

- `/bmad-cis-innovation-strategy`
- `/bmad-cis-design-thinking`
- `/bmad-cis-problem-solving`

### Acceptance criteria

- each workflow is callable from the Compass command surface
- each workflow has a defined output location under `_planning/current/`
- none of the CIS imports duplicate existing Compass brainstorming unnecessarily

## Phase 3: Add WDS UX And Design Handoff Lane

### Goal

Close the gap between PRD-level intent and implementation-ready UX/design handoff.

### Exact workflows to add

| Workflow | Source repo | Proposed target path in `compass-bmm` | Use |
| --- | --- | --- | --- |
| Trigger Mapping | `bmad-method-wds-expansion` | `workflows/2-planning/trigger-mapping/` | behavioral/system trigger analysis |
| Outline Scenarios | `bmad-method-wds-expansion` | `workflows/2-planning/outline-scenarios/` | user-flow and scenario definition |
| Conceptual Specifications | `bmad-method-wds-expansion` | `workflows/2-planning/conceptual-specifications/` | UX/spec detail before build |
| Design Delivery | `bmad-method-wds-expansion` | `workflows/2-planning/design-delivery/` | implementation-ready handoff |

### Exact work

1. Copy only the selected WDS workflows and required templates/checklists into `compass-bmm`.
2. Define where each workflow writes outputs:
   - trigger mapping -> `_planning/current/planning/ux-design/`
   - outline scenarios -> `_planning/current/planning/ux-design/`
   - conceptual specs -> `_planning/current/planning/ux-design/`
   - design delivery -> `_planning/current/planning/ux-design/`
3. Update workflow guidance so WDS sits between PRD and implementation planning.
4. Add companion Claude commands under `src/claude/commands/bmad/`.
5. Defer `product-evolution` until after the first lane is stable.

### Expected command surface

- `/bmad-wds-trigger-mapping`
- `/bmad-wds-outline-scenarios`
- `/bmad-wds-conceptual-specifications`
- `/bmad-wds-design-delivery`

### Acceptance criteria

- the WDS lane has a clear entry and exit point in Compass BMAD
- WDS outputs land in the planning tree, not ad hoc locations
- the lane improves implementation handoff without replacing Compass planning

## Phase 4: Add Conditional Security Lane

### Goal

Add a security and compliance lane that can be invoked when the work justifies it.

### Exact workflows to add

| Workflow / artifact | Source repo | Proposed target path in `compass-bmm` | Use |
| --- | --- | --- | --- |
| Threat Modeling | `BMAD-CYBERSEC` | `workflows/3-solutioning/threat-modeling/` | solution-level risk modeling |
| Security Architecture Review | `BMAD-CYBERSEC` | `workflows/3-solutioning/security-architecture-review/` | architecture validation before build |
| Secure Gate Criteria | `BMAD-CYBERSEC` | `workflows/4-implementation/secure-gates/` | pre-implementation / pre-release gates |

### Exact work

1. Import the selected CYBERSEC workflows, templates, and gate criteria only.
2. Remove or exclude unrelated legal/intel/strategy material from the first rollout.
3. Define security-lane trigger conditions in workflow docs and command docs.
4. Add companion command adapters under `src/claude/commands/bmad/`.
5. Add security output destinations under `_planning/current/`:
   - threat models -> `planning/architecture/`
   - security review notes -> `implementation/evidence/`
   - gate evidence -> `testing/` or `implementation/evidence/`
6. Update Compass workflow documentation so this lane is explicitly conditional.

### Expected trigger conditions

- auth or permission-heavy systems
- payment or customer-data handling
- regulated or compliance-scoped work
- public network attack surface
- explicit customer security deliverables

### Acceptance criteria

- security workflows are available but not mandatory for every project
- secure gates have explicit artifact requirements
- the security lane can be added without forking the main Compass BMAD path

## Phase 5: Add Claude-First Automation Foundation

### Goal

Wrap the BMAD phases in a coordinator layer without replacing source workflows.

### Exact commands to create

- `src/claude/commands/bmad/auto-plan.md`
- `src/claude/commands/bmad/auto-epic-start.md`
- `src/claude/commands/bmad/auto-story.md`
- `src/claude/commands/bmad/auto-epic-end.md`

### Exact work

1. Create the four phase-based orchestration commands above.
2. Make each automation command call existing BMAD workflows rather than duplicating workflow logic.
3. Require `bd`-compatible task tracking and status updates instead of TodoWrite.
4. Add structured step-summary and handoff requirements to all automation wrappers.
5. Add resume-safe checkpoints and partial-failure reporting.
6. Keep automation v1 sequential by default.
7. Add one "guided" path and one lighter "fast-path" path only if command complexity stays manageable.

### Files and directories expected to change

- `src/claude/commands/bmad/**`
- `src/claude/config/**`
- `docs/development/claude/**`
- `docs/development/bmad/**`

### Acceptance criteria

- a user can invoke `auto-plan`, `auto-epic-start`, `auto-story`, and `auto-epic-end` from the Claude command surface
- the automation wrappers reference Compass BMAD workflows, not hardcoded forked copies
- the wrappers use `bd` and BMAD artifacts as the state model

## Phase 6: Add Context Budgeting, Handoff, And Automation-Safe Patching

### Goal

Make the automation layer token-aware and resumable without rewriting the underlying BMAD source workflows.

### Exact work

1. Define per-workflow strategic context policy:
   - what planning documents each wrapper loads
   - token budget caps
   - when sharded docs load only index files
2. Create a compact handoff artifact format for long-running or interrupted automation.
3. Add a workflow-patching strategy so automation-specific adjustments do not mutate the original workflow definitions.
4. Add validation rules for patched automation prompts and required artifacts.
5. Document recovery behavior for interrupted runs.

### Proposed file locations

- `src/claude/config/bmad-automation-context.yaml`
- `src/claude/config/bmad-automation-patches/`
- `src/claude/templates/bmad-handoff-template.md`
- `docs/architecture/bmad-automation.md`

### Acceptance criteria

- automation wrappers do not indiscriminately load every strategic document
- interrupted automation runs can produce a handoff artifact
- automation-specific prompt changes are kept outside the source workflow definitions

## Phase 7: Deferred Advanced Automation

### Goal

Capture advanced work without mixing it into the first rollout.

### Deferred items

1. worktree-based parallel story execution
2. sequential merge gates for parallel implementation
3. optional POV oversight artifacts
4. optional AI memory hook integration
5. Codex/OpenCode automation adapters after Claude flow stabilizes

### Why deferred

- they add high complexity and more recovery risk
- they are easier to evaluate after the basic automation path works

## Implementation Order And Work Packages

This is the recommended execution order for actual implementation work:

1. `bmad-engine-3hi`
   - align on this plan
2. Foundation slice
   - source-of-truth cleanup
   - BMAD build/push/validate wiring
3. `bmad-engine-uzd`
   - CIS lane
4. `bmad-engine-8gj`
   - WDS lane
5. `bmad-engine-509`
   - CYBERSEC lane
6. `bmad-engine-k0b`
   - phase-based automation coordinator
7. `bmad-engine-vm7`
   - patching, context budgeting, handoff model
8. `bmad-engine-lny`
   - optional oversight and memory sidecars
9. `bmad-engine-2tk`
   - parallel story execution with worktrees and merge gates

## Delivery Slices

If we want to land this in reviewable chunks instead of one large batch, I recommend these slices:

### Slice A: Repo foundation

- Phase 0 only

### Slice B: Compass BMAD base module

- Phase 1 only

### Slice C: CIS lane

- Phase 2 only

### Slice D: WDS lane

- Phase 3 only

### Slice E: CYBERSEC lane

- Phase 4 only

### Slice F: Automation v1

- Phase 5 and Phase 6

### Slice G: Deferred advanced automation

- Phase 7

## Acceptance Criteria For The Overall Initiative

The initiative is successful when all of the following are true:

1. Compass has a real custom BMAD module in `src/bmad/modules/`.
2. `_bmad/` becomes a real distributable target, not just a documented idea.
3. CIS, WDS, and CYBERSEC additions are usable without importing their source repos wholesale.
4. The automation layer wraps BMAD workflows instead of replacing them.
5. `bd` remains the task system for tracked work.
6. The repo documentation matches the actual source/build/distribution model.

## Review Checkpoints For Alignment

Before implementation starts, I want explicit confirmation on these points:

1. Do you want one primary Compass custom module (`compass-bmm`) or multiple Compass modules from day one?
2. Do you want automation v1 to be Claude-only first, or do you want Codex/OpenCode adapter work included in the first rollout?
3. Do you want Phase 0 source-of-truth cleanup to happen first even though it adds non-feature infrastructure work?
4. Do you want POV / AI memory kept deferred, or should one of those move into the first rollout?
5. Do you want WDS `product-evolution` included in the first pass, or kept out until the main WDS lane is stable?

## Recommended Starting Point

My recommendation is to begin with:

1. Phase 0 foundation
2. Phase 1 `compass-bmm` scaffold
3. Phase 2 CIS lane

That gives us a stable base, adds the cleanest net-new value first, and keeps the next review checkpoint small.
