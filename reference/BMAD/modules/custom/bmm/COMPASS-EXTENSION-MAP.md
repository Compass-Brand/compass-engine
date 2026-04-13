# Compass Extension Map

Status: phase-2-through-phase-8-reviewed
Owner:
Last Updated: 2026-03-12

This file is the Phase 2 extension inventory for the active Compass BMAD reference layer.

## Purpose

- record what adjacent BMAD assets are being adopted into the active `custom/bmm` layer
- record what is explicitly rejected or deferred
- define target insertion points before catalog or workflow copying begins
- define output destinations in the planning framework

## Source Repos Reviewed

- `BMAD-CYBERSEC`
- `bmad-method-wds-expansion`
- `bmad-module-creative-intelligence-suite`
- `pov-oversight-agent`
- `ai-memory`

## Adoption Summary

> **Note:** The selected sub-repos have been consumed into `src/bmad/modules/custom/` and the original sub-repo directories were removed from compass-engine. The deferred repos were not consumed.

| Source | Status | Consumed Into | Reason |
| --- | --- | --- | --- |
| `bmad-module-creative-intelligence-suite` | Consumed | `custom/compass-skills/1-analysis/` | Strong early-phase strategic additions with low overlap when narrowed to specific workflows |
| `bmad-method-wds-expansion` | Consumed | `custom/compass-skills/2-plan-workflows/` | Strong PRD-to-UX-to-handoff lane that fixes a real gap in baseline BMAD |
| `BMAD-CYBERSEC` | Consumed | `custom/compass-skills/3-solutioning/` | Strong conditional security planning and gate lane |
| `pov-oversight-agent` | Deferred | n/a | Useful as optional oversight sidecar, but not core to the current reference rollout |
| `ai-memory` | Deferred | n/a | Useful later for optional memory substrate, but not part of the current core rollout |

## Selected Workflow Imports

### CIS

| Workflow | Source command | Proposed target path | Proposed command | Phase placement | Planning destination |
| --- | --- | --- | --- | --- | --- |
| Innovation Strategy | `bmad-cis-innovation-strategy` | `reference/BMAD/modules/custom/bmm/workflows/1-analysis/innovation-strategy/` | `bmad-cis-innovation-strategy` | High-level analysis and detailed analysis | `roadmap/strategy/` and `current/research/strategy/` |
| Design Thinking | `bmad-cis-design-thinking` | `reference/BMAD/modules/custom/bmm/workflows/1-analysis/design-thinking/` | `bmad-cis-design-thinking` | High-level analysis and detailed analysis | `roadmap/strategy/` and `current/research/strategy/` |
| Problem Solving | `bmad-cis-problem-solving` | `reference/BMAD/modules/custom/bmm/workflows/anytime/problem-solving/` | `bmad-cis-problem-solving` | Anytime lane | `current/research/implementation/` or `current/implementation/evidence/` |

### WDS

| Workflow | Source command | Proposed target path | Proposed command | Phase placement | Planning destination |
| --- | --- | --- | --- | --- | --- |
| Trigger Mapping | `bmad-wds-trigger-mapping` | `reference/BMAD/modules/custom/bmm/workflows/2-plan-workflows/trigger-mapping/` | `bmad-wds-trigger-mapping` | Planning and experience design | `current/planning/ux-design/trigger-mapping/` |
| Outline Scenarios | `bmad-wds-outline-scenarios` | `reference/BMAD/modules/custom/bmm/workflows/2-plan-workflows/outline-scenarios/` | `bmad-wds-outline-scenarios` | Planning and experience design | `current/planning/ux-design/outline-scenarios/` |
| Conceptual Specifications | `bmad-wds-conceptual-specs` | `reference/BMAD/modules/custom/bmm/workflows/2-plan-workflows/wds-ux-design/workflow-specify.md` | `bmad-wds-conceptual-specs` | Planning and experience design | `current/planning/ux-design/conceptual-specifications/` |
| Design Delivery | `bmad-wds-design-delivery` | `reference/BMAD/modules/custom/bmm/workflows/2-plan-workflows/wds-ux-design/workflow-handover.md` | `bmad-wds-design-delivery` | Planning and experience design | `current/planning/ux-design/design-delivery/` |

### CYBERSEC

| Workflow | Source workflow id | Proposed target path | Proposed command | Phase placement | Planning destination |
| --- | --- | --- | --- | --- | --- |
| Threat Modeling | `threat-modeling` | `reference/BMAD/modules/custom/bmm/workflows/3-solutioning/threat-modeling/` | `bmad-cybersec-threat-modeling` | Solutioning | `current/planning/architecture/threat-modeling/` |
| Security Architecture Review | `security-architecture-review` | `reference/BMAD/modules/custom/bmm/workflows/3-solutioning/security-architecture-review/` | `bmad-cybersec-security-architecture-review` | Solutioning | `current/planning/architecture/security-review/` |
| Secure Gates | secure gate criteria and gate logic | `reference/BMAD/modules/custom/bmm/workflows/4-implementation/secure-gates/` | `bmad-cybersec-secure-gates` | Solutioning and release gate | `current/testing/gates/security/` plus `current/testing/gates/draft/security/` while approval is pending |

## Explicit Rejections

| Source | Workflow / area | Decision | Reason |
| --- | --- | --- | --- |
| CIS | Brainstorming | Reject as import | Duplicates the existing brainstorming lane |
| CIS | Storytelling as mandatory lane | Reject as mandatory | Keep as conditional `storytelling_mode`, not forced everywhere |
| WDS | Product Evolution | Defer | Valuable later, but not part of the current core WDS bridge |
| WDS | Full WDS project-management/agent shell | Reject as import | Keep only the workflows that enrich the active BMM spine |
| CYBERSEC | Non-product-delivery modules outside the selected lane | Reject | Out of scope for current rollout |
| POV | Core-flow replacement / hard oversight model | Defer | Optional sidecar later, not core method now |
| AI Memory | Core-flow requirement | Defer | Optional sidecar later, not core method now |

## Proposed Insertion Points

### Project-Level And Analysis Layer

1. `Innovation Strategy` after technical research and before the brief
2. `Design Thinking` after innovation strategy and before the brief
3. `Storytelling` remains conditional and may be embedded into the high-level brief

### Planning And Experience Design

1. `Trigger Mapping` after PRD validation
2. `Outline Scenarios` after trigger mapping
3. `Create UX Design` remains in the lane
4. `Conceptual Specifications` after UX design
5. `Design Delivery` after conceptual specifications
6. If WDS exposes requirement gaps, route back to `Edit PRD`

### Solutioning And Gates

1. `Threat Modeling` after the first architecture draft
2. `Security Architecture Review` after threat modeling
3. `Secure Readiness Gate` before implementation readiness approval
4. `Secure Release Gate` during the release gate when the security lane is active

## Workflow Status By Plan Phase

| Plan phase | Status | Notes |
| --- | --- | --- |
| Phase 2: extension map | Complete | Inventory, insertion points, and target paths are defined here |
| Phase 3: CIS import | Complete | Core CIS workflows and commands are landed in the active BMM layer |
| Phase 4: WDS import | Complete | Shared WDS workflow family is imported and mapped into the Compass planning lanes |
| Phase 5: CYBERSEC import | Complete | Conditional security workflows, agents, activation note, and secure-gate criteria are landed in the active BMM layer |
| Phase 6: automation specs | Complete | Reference-stage automation specs, policies, and templates are landed under `reference/BMAD/tools/automation/` |
| Phase 7: output mapping and documentation handoff | Complete | Planning destinations and documentation promotion rules are aligned with the expanded BMAD flow |
| Phase 8: productization gate | Reviewed | Reference layer is ready for productization planning, but not ready for direct `src/` migration yet |

## Catalog Follow-Up

The catalog rows identified during Phase 2 have now been landed in `reference/BMAD/modules/custom/bmm/module-help.csv`:

- CIS:
  - Innovation Strategy
  - Design Thinking
  - Problem Solving
- WDS:
  - Trigger Mapping
  - Outline Scenarios
  - Conceptual Specifications
  - Design Delivery
- CYBERSEC:
  - Threat Modeling
  - Security Architecture Review
  - Secure Readiness Gate
  - Secure Release Gate

Remaining catalog work is no longer the Phase 2 import list. It is later productization and runtime packaging alignment.

## Output Mapping Rules

1. Roadmap-level strategy work writes to `reference/planning/framework/roadmap/`.
2. Active-slice analysis, planning, and solutioning work writes to `reference/planning/framework/current/`.
3. WDS outputs write only to the UX-design planning lane, with:
   - Trigger Mapping -> `trigger-mapping/`
   - Outline Scenarios -> `outline-scenarios/`
   - Conceptual Specifications -> `conceptual-specifications/`
   - Design Delivery -> `design-delivery/`
4. CYBERSEC outputs write to architecture or testing gates depending on type.
5. Problem Solving writes to the evidence or implementation research lane depending on when it is used.

## Deferred Work

- optional POV oversight sidecar design
- optional AI memory substrate design
- productization of stable reference-stage BMAD assets into `src/`
