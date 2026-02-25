# Workflow To Folder Map

This map defines where outputs should be stored when running BMAD-aligned planning and implementation activities.

## Phase 1: Analysis

| Workflow | Expected Output | Destination |
| --- | --- | --- |
| Brainstorming | raw ideas, themes | `../framework/current/brainstorming/` |
| Market/domain/technical research | research notes and synthesis | `../framework/current/research/` |
| Product brief creation | brief document | `../framework/roadmap/product-brief/` and optionally `../framework/current/planning/prd/` references |

## Phase 2: Planning

| Workflow | Expected Output | Destination |
| --- | --- | --- |
| Create PRD | PRD document and revisions | `../framework/current/planning/prd/` |
| Create UX design | UX specs and flows | `../framework/current/planning/ux-design/` |

## Phase 3: Solutioning

| Workflow | Expected Output | Destination |
| --- | --- | --- |
| Create architecture | architecture decisions and diagrams | `../framework/current/planning/architecture/` |
| Create epics and stories | epic set and story drafts | `../framework/current/planning/epics/` and `../framework/current/implementation/stories/` |
| Implementation readiness checks | readiness evidence | `../framework/current/testing/` or `../framework/current/research/` |

## Phase 4: Implementation

| Workflow | Expected Output | Destination |
| --- | --- | --- |
| Story execution | implementation story updates | `../framework/current/implementation/stories/` |
| QA and test automation | test results and coverage evidence | `../framework/current/testing/` and `../framework/current/implementation/evidence/` |
| Code review outcomes | evidence notes and defects | `../framework/current/implementation/evidence/` |

## Cross-Phase Roadmap Operations

| Activity | Destination |
| --- | --- |
| Net-new roadmap brainstorming | `../framework/roadmap/brainstorming/` |
| Strategic research | `../framework/roadmap/research/` |
| Superseded roadmap docs | `../framework/roadmap/archive/<lane>/<YYYY-MM-DD>/` where `<lane>` is `brainstorming`, `research`, or `product-brief` |

## Phase Transition Output

When a phase completes:
1. Move `../framework/current/` contents into `../framework/previous/<phase-slug>-<YYYY-MM-DD>/`.
2. Add lessons to `../framework/lessons/<phase-slug>-<YYYY-MM-DD>/`.
3. Update `../framework/roadmap/roadmap.md`.
