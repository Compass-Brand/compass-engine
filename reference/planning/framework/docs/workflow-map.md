# Workflow To Folder Map

This map defines where outputs should be stored when running BMAD-aligned planning and implementation activities.

## Phase 1: Analysis

| Workflow | Expected Output | Destination |
| --- | --- | --- |
| Brainstorming | raw ideas, themes | `../current/brainstorming/` |
| Market/domain/technical research | research notes and synthesis | `../current/research/` |
| Product brief creation | brief document | `../roadmap/product-brief/` and optionally `../current/planning/prd/` references |

## Phase 2: Planning

| Workflow | Expected Output | Destination |
| --- | --- | --- |
| Create PRD | PRD document and revisions | `../current/planning/prd/` |
| Create UX design | UX specs and flows | `../current/planning/ux-design/` |

## Phase 3: Solutioning

| Workflow | Expected Output | Destination |
| --- | --- | --- |
| Create architecture | architecture decisions and diagrams | `../current/planning/architecture/` |
| Create epics and stories | epic set and story drafts | `../current/planning/epics/` and `../current/implementation/stories/` |
| Implementation readiness checks | readiness evidence | `../current/testing/` or `../current/research/` |

## Phase 4: Implementation

| Workflow | Expected Output | Destination |
| --- | --- | --- |
| Story execution | implementation story updates | `../current/implementation/stories/` |
| QA and test automation | test results and coverage evidence | `../current/testing/` and `../current/implementation/evidence/` |
| Code review outcomes | evidence notes and defects | `../current/implementation/evidence/` |

## Cross-Phase Roadmap Operations

| Activity | Destination |
| --- | --- |
| Net-new roadmap brainstorming | `../roadmap/brainstorming/` |
| Strategic research | `../roadmap/research/` |
| Superseded roadmap docs | `../roadmap/archive/<lane>/<YYYY-MM-DD>/` where `<lane>` is `brainstorming`, `research`, or `product-brief` |

## Phase Transition Output

When a phase completes:
1. Move `../current/` contents into `../previous/<phase-slug>-<YYYY-MM-DD>/`.
2. Add lessons to `../lessons/<phase-slug>-<YYYY-MM-DD>/`.
3. Update `../roadmap/roadmap.md`.
