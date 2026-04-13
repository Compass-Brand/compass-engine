# BMAD Reference Productization Plan

> **ARCHIVED:** Superseded by the src/-based BMAD upstream migration (see `docs/plans/2026-04-06-bmad-upstream-migration-design.md`). Retained for historical reference only.

Status: archived
Owner:
Last Updated: 2026-03-13

This file is the Phase 8 output for the reference-stage Compass BMAD rollout.

## Decision

The reference layer passes the gate for productization planning.

The reference layer does not yet pass the gate for immediate migration into `src/`.

That means:

- productization planning may proceed now
- direct `src/` migration should wait
- the next work should focus on proof, cleanup, and conversion planning rather than moving files prematurely

## Why The Gate Passed

The reference layer now satisfies the structural readiness criteria from the main implementation plan:

1. `reference/BMAD/BMAD-workflow.md` reflects the agreed Compass BMAD flow.
2. `reference/BMAD/modules/custom/bmm/module-help.csv` reflects the active command catalog.
3. CIS, WDS, and CYBERSEC lanes are present in the working BMM layer.
4. Automation phase specs exist in `reference/BMAD/tools/automation/`.
5. The roadmap-driven planning framework contract is explicit.
6. Output mapping is explicit for the new planning, WDS, CYBERSEC, and automation artifacts.
7. Documentation promotion and handoff rules are defined.
8. The flow shape has been reviewed and iterated enough to plan productization.

## Why `src/` Still Waits

The remaining blockers are operational, not structural:

1. The automation layer is still a reference-spec layer, not a runtime implementation layer.
2. The new planning state model has not yet gone through a full real project cycle.
3. The imported WDS and CYBERSEC lanes have not yet been proven through a complete usage cycle.
4. The source sub-repos have not yet passed a removal-readiness audit.
5. Repo evidence of formal productization sign-off is still weak and should be made explicit before migration starts.

## Productization Principles

1. `reference/` remains the shaping and proof layer until a surface is stable enough to be treated as authored product source.
2. `src/` only receives assets that are both structurally stable and operationally proven.
3. Provenance and planning history do not move into `src/`.
4. Runtime packaging should be derived from stable source assets, not copied directly from reference notes.
5. No productized asset may retain hidden dependency on the source sub-repos.

## Classification

### Group A: Productization Candidates After The Next Approval Gate

These are the strongest candidates to eventually move into `src/` once the prerequisite proof work is complete:

- `reference/BMAD/BMAD-workflow.md`
- `reference/BMAD/modules/custom/bmm/module-help.csv`
- `reference/BMAD/modules/custom/bmm/module.yaml`
- `reference/BMAD/modules/custom/bmm/workflows/1-analysis/innovation-strategy/`
- `reference/BMAD/modules/custom/bmm/workflows/1-analysis/design-thinking/`
- `reference/BMAD/modules/custom/bmm/workflows/anytime/problem-solving/`
- corresponding narrowed CIS agents under `reference/BMAD/modules/custom/bmm/agents/`

These are the best early candidates because they define the canonical Compass BMAD spine, the active BMM contract, and the least risky imported lane.

### Group B: Productization Candidates After One Real Usage Cycle

These should not move into `src/` until the updated reference layer has been exercised in a real project cycle:

- `reference/BMAD/modules/custom/bmm/workflows/0-governance/`
  - especially `phase-sync` and `phase-closeout`
- `reference/BMAD/modules/custom/bmm/workflows/2-plan-workflows/`
  - especially the WDS slice
- `reference/BMAD/modules/custom/bmm/workflows/3-solutioning/threat-modeling/`
- `reference/BMAD/modules/custom/bmm/workflows/3-solutioning/security-architecture-review/`
- `reference/BMAD/modules/custom/bmm/workflows/4-implementation/secure-gates/`
- `reference/BMAD/tools/automation/`

These assets are structurally aligned, but they are still too new to productize without a proof cycle.

### Group C: Reference-Only Surfaces

These should remain in `reference/` or `_planning/` and should not be migrated into `src/` as product source:

- `reference/BMAD/modules/custom/bmm/COMPASS-EXTENSION-MAP.md`
- `_planning/current/planning/2026-03-10-bmad-extension-implementation-plan.md`
- this productization plan file
- `reference/planning/docs/`
- `reference/planning/framework/README.md`
- `reference/planning/templates/`
- `reference/documentation/human/policies/documentation-governance.md`
- `reference/documentation/ai/README.md`

These are planning, governance, provenance, or reference guidance assets rather than product-runtime source.

## What Eventually Moves Into `src/`

The eventual `src/` target should focus on authored BMAD product assets, not the entire reference workspace.

Planned eventual `src/` migration scope:

1. the canonical Compass BMAD flow definition
2. the BMM module contract
3. stable workflow families that define the shipped Compass method
4. stable agent definitions required by those workflows
5. stable automation runtime assets once automation is implemented and proven

Planned non-scope for `src/`:

1. extension provenance documents
2. planning history
3. framework rationale documents
4. live project planning state examples
5. temporary gate packages, reports, and automation run logs

## What Becomes Buildable / Distributable

The buildable or distributable layer should eventually include:

1. a productized BMM custom module package
2. stable workflow definitions referenced by that module
3. stable agent definitions referenced by that module
4. generated or packaged runtime command surfaces for Claude-facing execution
5. any later `_bmad/` or distribution artifact derived from those source assets

The buildable layer should not directly include:

1. planning framework working files
2. reference-stage templates that still carry open shaping assumptions
3. raw Phase 8 review notes

## What Becomes Actual `.claude` Command / Runtime Assets

These should only be created after the source layer is productized and a runtime implementation pass begins.

Planned future `.claude` or runtime candidates:

1. stable command surfaces derived from `module-help.csv`
2. stable BMM workflow entrypoints needed for the shipped Compass method
3. runtime versions of:
   - `auto-plan`
   - `auto-epic-start`
   - `auto-story`
   - `auto-epic-end`
4. runtime gate and handoff packaging for approved review checkpoints

Not ready for `.claude` runtime packaging yet:

1. automation reference specs in `reference/BMAD/tools/automation/`
2. WDS and CYBERSEC imports that have not yet gone through a proof cycle
3. planning-framework state files and templates

## Required Proof Work Before Migration Starts

### 1. Run A Full Reference-Layer Usage Cycle

Use the new reference BMAD layer on at least one real project slice that exercises:

- `Phase Sync`
- detailed analysis
- PRD and WDS
- architecture
- readiness
- at least one story loop
- `Phase Closeout`

This cycle should confirm that the new planning state model, output mapping, and human-machine authority rules hold up in practice.

### 2. Run A Conditional Security Usage Cycle

Use a security-active slice to prove:

- threat modeling
- security architecture review
- secure readiness gate
- secure release gate

### 3. Run An Automation Pilot

The automation layer should first be piloted as reference-guided execution before it is turned into shipped runtime assets.

Minimum pilot scope:

- one `auto-plan` run
- one `auto-story` run
- failure handling and resume validation
- artifact promotion validation

### 4. Complete A Sub-Repo Removal-Readiness Audit

Before deleting the adjacent source repos, verify:

1. every active imported asset exists in the BMM layer
2. no active BMM workflow or agent depends on source-repo paths
3. provenance references are informational only
4. any still-needed source material has been intentionally imported or explicitly deferred
5. deletion will not remove hidden templates, configs, criteria files, or agent dependencies

Status:

- completed on `2026-03-13`
- current result: not deletion-ready yet
- see `_planning/current/planning/2026-03-13-subrepo-removal-readiness-audit.md`

### 5. Record Durable Productization Approval

Before the first `src/` migration change set, add an explicit approval artifact that states:

- the reference flow is approved for productization
- which surfaces are approved for migration
- which surfaces remain reference-only
- who approved the move

## Recommended Migration Waves

### Wave 0: Proof And Cleanup

1. run the full reference-layer usage cycle
2. run the security-active usage cycle
3. run the automation pilot
4. complete the sub-repo removal-readiness audit
5. write the durable approval artifact

Exit criteria:

- at least one real cycle completed
- no hidden sub-repo dependency remains
- no major flow-order or path-contract changes discovered

### Wave 1: Core Method Productization

Move the most stable BMAD definition assets into `src/`:

1. `BMAD-workflow.md`
2. `module-help.csv`
3. `module.yaml`
4. the CIS strategy slice
5. stable supporting agents for that slice

Exit criteria:

- `src` has the stable BMM spine
- no divergence between reference and product source for these assets
- generation or packaging path is clear

### Wave 2: Governance And Planning-Lane Productization

After a clean proof cycle, promote:

1. governance workflows needed for the roadmap-driven flow
2. WDS planning and handoff workflows
3. any stable planning-contract assets that are required as product source

Exit criteria:

- WDS lane proven in real use
- phase-state choreography proven in real use
- no major artifact-contract changes required

### Wave 3: Security Lane Productization

After a clean security proof cycle, promote:

1. threat modeling
2. security architecture review
3. secure gate criteria and runtime gate flow

Exit criteria:

- security lane proven in at least one real slice
- gate placement and output contract stable

### Wave 4: Automation Runtime Productization

Only after the automation pilot succeeds, convert the reference automation design into product/runtime assets.

Scope:

1. real runtime command surfaces
2. stable command packaging
3. runtime templates and state files
4. `.claude` integration surfaces as needed

Exit criteria:

- resume, failure, and approval handling proven
- runtime packaging path agreed
- automation no longer depends on reference-only assumptions

## Sub-Repo Retirement Rule

The adjacent repos should not be deleted simply because the selected slices were imported.

They should be retired only after:

1. the removal-readiness audit passes
2. provenance notes are captured in reference or planning history
3. the imported Compass layer is complete enough that no source repo remains operationally necessary
4. the user explicitly approves retirement

## Immediate Next Steps

1. run one real reference-layer phase through the new planning and BMAD flow
2. run the automation pilot against that proof cycle
3. record a durable productization approval artifact after those proof steps
4. use the completed removal-readiness audit as the future cleanup checklist for the actual deletion change set
5. then start Wave 1 productization planning in detail

## Current Recommendation

Treat the reference layer as the working source of truth for method design.

Do not start moving content into `src/` yet.

Finish proof, audit, and approval first. Then migrate in waves.
