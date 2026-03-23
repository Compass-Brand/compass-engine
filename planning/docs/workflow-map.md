# Workflow To Artifact Map

This map defines where outputs should be stored when running the roadmap-driven Compass BMAD workflow.

## Roadmap-Level Work

| Workflow | Expected Output | Destination | State Update |
| --- | --- | --- | --- |
| Initialize Planning | planning scaffold | `../framework/` | none |
| Initialize Planning (workspace/orchestration) | repo registry and initiative routing scaffold | `../framework/repositories.yaml`, `../framework/current/initiative-index.yaml`, and `../framework/current/initiatives/` | none |
| High-Level Brainstorm | high-level brainstorming artifacts | `../framework/roadmap/brainstorming/` | none |
| High-Level Market Research | market research and synthesis | `../framework/roadmap/research/market/` | none |
| High-Level Domain Research | domain research and synthesis | `../framework/roadmap/research/domain/` | none |
| High-Level Technical Research | technical research and synthesis | `../framework/roadmap/research/technical/` | none |
| High-Level Innovation Strategy | innovation strategy outputs | `../framework/roadmap/strategy/` | none |
| High-Level Opportunity Framing | opportunity framing outputs | `../framework/roadmap/strategy/` | none |
| High-Level Storytelling | storytelling artifacts when enabled | `../framework/roadmap/storytelling/` | `lane_decisions.storytelling_mode` |
| High-Level Product Brief | high-level product brief | `../framework/roadmap/product-brief/` | `artifact_revisions.brief.*` when used by automation |
| Project Roadmap | `roadmap.md` and `roadmap.yaml` with execution scope and repo targets | `../framework/roadmap/` | `active_phase_id` and `phases[]` |

## Phase Activation And Detailed Analysis

| Workflow | Expected Output | Destination | State Update |
| --- | --- | --- | --- |
| Phase Sync | `phase.md`, `phase-state.yaml`, scope framing | `../framework/current/` | `workflow_status.phase_sync` |
| Initiative Routing | initiative routing report, `initiative-index.yaml`, and per-initiative phase stubs | `../framework/current/initiative-index.yaml` and `../framework/current/initiatives/` | `workflow_status.initiative_routing` |
| Generate Project Context | generated project context | `../framework/current/research/project-context/` | `artifact_paths.project_context.*` |
| Detailed Brainstorm | detailed brainstorming artifacts | `../framework/current/brainstorming/detailed/` | none |
| Detailed Market Research | phase-scoped market research | `../framework/current/research/market/` | `workflow_status.detailed_analysis` |
| Detailed Domain Research | phase-scoped domain research | `../framework/current/research/domain/` | `workflow_status.detailed_analysis` |
| Detailed Technical Research | phase-scoped technical research | `../framework/current/research/technical/` | `workflow_status.detailed_analysis` |
| Detailed Innovation Strategy | detailed innovation strategy outputs | `../framework/current/research/strategy/` | `workflow_status.detailed_analysis` |
| Detailed Opportunity Framing | detailed opportunity framing outputs | `../framework/current/research/strategy/` | `workflow_status.detailed_analysis` |
| Detailed Product Brief | phase-scoped product brief | `../framework/current/planning/brief/` | `artifact_revisions.brief.*` |

## Planning And Experience Design

| Workflow | Expected Output | Destination | State Update |
| --- | --- | --- | --- |
| Create PRD | PRD drafts | `../framework/current/planning/prd/` | `artifact_revisions.prd.*` |
| Validate PRD | validation notes and gate package | `../framework/current/planning/prd/` and `../framework/current/testing/gates/` | `approval_markers.prd.*` |
| Edit PRD | revised PRD artifacts | `../framework/current/planning/prd/` | `stale_outputs[]` when downstream artifacts must be regenerated |
| Trigger Mapping | trigger maps | `../framework/current/planning/ux-design/trigger-mapping/` | `lane_outcomes.wds` |
| Outline Scenarios | scenario artifacts | `../framework/current/planning/ux-design/outline-scenarios/` | `lane_outcomes.wds` |
| Create UX Design | UX flow and design artifacts | `../framework/current/planning/ux-design/` | `artifact_revisions.ux_design.*` |
| Conceptual Specifications | conceptual specifications | `../framework/current/planning/ux-design/conceptual-specifications/` | `artifact_revisions.ux_design.*` |
| Design Delivery | design handoff artifacts | `../framework/current/planning/ux-design/design-delivery/` | `workflow_status.planning_experience` |

## Solutioning

| Workflow | Expected Output | Destination | State Update |
| --- | --- | --- | --- |
| Create Architecture | architecture artifacts | `../framework/current/planning/architecture/` | `artifact_revisions.architecture.*` |
| Threat Modeling | threat model outputs | `../framework/current/planning/architecture/threat-modeling/` | `lane_outcomes.security` |
| Security Architecture Review | security review outputs | `../framework/current/planning/architecture/security-review/` | `lane_outcomes.security` |
| Test Design | system-level or epic-level test design | `../framework/current/testing/test-design/` | `workflow_status.solutioning` |
| Create Epics And Stories | epics document with embedded story definitions for the manual flow | `../framework/current/planning/epics/` | `artifact_revisions.epics.*` |
| Test Framework Setup | test automation framework setup artifacts | `../framework/current/testing/automation/` | `workflow_status.solutioning` |
| CI/CD Alignment | CI/CD alignment notes and decisions | `../framework/current/testing/automation/` and `../framework/current/implementation/evidence/` | `workflow_status.solutioning` |
| Secure Readiness Gate | security gate package | `../framework/current/testing/gates/draft/security/` while pending, then `../framework/current/testing/gates/security/readiness/` when accepted | `approval_markers.readiness.*` |
| Check Implementation Readiness | readiness package and summary | `../framework/current/testing/gates/draft/` or `../framework/current/testing/gates/` | `approval_markers.readiness.*` |

## Implementation

| Workflow | Expected Output | Destination | State Update |
| --- | --- | --- | --- |
| Sprint Planning | sprint routing and sprint-status initialization | `../framework/current/implementation/stories/` | `workflow_status.implementation` |
| Implementation Brainstorming | implementation brainstorming outputs | `../framework/current/brainstorming/detailed/` | `workflow_status.implementation` |
| Implementation Research | implementation research outputs | `../framework/current/research/implementation/` | `workflow_status.implementation` |
| Sprint Status | sprint status snapshot | `../framework/current/implementation/stories/` | `workflow_status.implementation` |
| Create Story | story package | `../framework/current/implementation/stories/` | `artifact_revisions.stories.*` |
| Validate Story | story validation notes | `../framework/current/implementation/evidence/` | `workflow_status.implementation` |
| ATDD | acceptance-test artifacts | `../framework/current/testing/test-design/` | `workflow_status.implementation` |
| Dev Story | implementation evidence and story updates | `../framework/current/implementation/stories/` and repo codebase | none |
| Test Automation | automated test artifacts and runs | `../framework/current/testing/automation/` | none |
| QA Automation Test | QA automation evidence | `../framework/current/testing/automation/` and `../framework/current/testing/reviews/` | none |
| Code Review | code review notes and defects | `../framework/current/implementation/evidence/` | none |
| Test Review | test review notes and defects | `../framework/current/testing/reviews/` | none |
| Traceability | traceability evidence | `../framework/current/implementation/evidence/` | none |
| Retrospective | epic or sprint retrospective | `../framework/current/implementation/retrospectives/` | none |

## Release Gate And Closeout

| Workflow | Expected Output | Destination | State Update |
| --- | --- | --- | --- |
| NFR Assessment | NFR evidence | `../framework/current/testing/gates/` | `workflow_status.release_gate` |
| Final Test Review | final test audit | `../framework/current/testing/reviews/` and `../framework/current/testing/gates/` | `workflow_status.release_gate` |
| Traceability Gate | release traceability package | `../framework/current/testing/gates/` | `workflow_status.release_gate` |
| Secure Release Gate | secure release package when active | `../framework/current/testing/gates/security/release/` | `lane_outcomes.security` |
| Validate Docs | documentation validation evidence | `../framework/current/implementation/evidence/` | `workflow_status.release_gate` |
| Phase Closeout | frozen phase snapshot, lessons, roadmap updates | `../framework/previous/`, `../framework/lessons/`, and `../framework/roadmap/` | `workflow_status.closeout` |

## Automation Wrappers

| Workflow | Expected Output | Destination | State Update |
| --- | --- | --- | --- |
| `auto-plan` | runtime state, roadmap proposal, gate packages, readiness handoff, run summary | `../framework/current/implementation/evidence/` plus `../framework/current/testing/gates/draft/` and approved gate locations | `approval_markers.*`, `review_artifacts.*`, `automation_state.*`, `draft_artifacts.*` |
| `auto-epic-start` | epic start report, epic test design, optional implementation research | `../framework/current/implementation/evidence/`, `../framework/current/testing/test-design/`, and `../framework/current/research/implementation/` | `next_checkpoint` when blocked |
| `auto-story` | reuse evidence, story run report, gate report, test automation, review outputs, traceability | `../framework/current/implementation/evidence/`, `../framework/current/testing/automation/`, `../framework/current/testing/reviews/`, and `../framework/current/testing/gates/` | story status plus merge gate state |
| `auto-epic-end` | retrospective, docs delta, epic end report, next-epic preview | `../framework/current/implementation/retrospectives/` and `../framework/current/implementation/evidence/` | proposed phase-state updates |

## Beads Tracking Overlay

- `bd` is authoritative for task and issue lifecycle across phases, epics, stories, blockers, and carry-over work.
- `phase-state.yaml.beads.*` and `auto-plan-state.yaml.beads.*` store references to the relevant Beads issues so planning state and task state can be reconciled.
- Active phases should have a phase issue before detailed analysis starts.
- Active epics should have an epic issue before story execution begins.
- Active stories should have a story issue before `Dev Story`.
- Follow-up work discovered during reviews, gates, or closeout should be created in Beads and recorded in the relevant `follow_up_issue_ids` field.

## Cross-Phase Archival

| Activity | Destination |
| --- | --- |
| Superseded roadmap brainstorming | `../framework/roadmap/archive/brainstorming/<YYYY-MM-DD>/` |
| Superseded market research | `../framework/roadmap/archive/research/market/<YYYY-MM-DD>/` |
| Superseded domain research | `../framework/roadmap/archive/research/domain/<YYYY-MM-DD>/` |
| Superseded technical research | `../framework/roadmap/archive/research/technical/<YYYY-MM-DD>/` |
| Superseded strategy artifacts | `../framework/roadmap/archive/strategy/<YYYY-MM-DD>/` |
| Superseded storytelling artifacts | `../framework/roadmap/archive/storytelling/<YYYY-MM-DD>/` |
| Superseded product briefs | `../framework/roadmap/archive/product-brief/<YYYY-MM-DD>/` |
