# Planning Framework Domain

`framework/` contains the live planning structure for roadmap-driven Compass BMAD work.

## Intent

- keep one active roadmap slice in `current/`
- keep cross-phase direction in `roadmap/`
- preserve completed phase snapshots in `previous/`
- extract reusable learning into `lessons/`

This layout is designed for continuous development across repeated BMAD cycles, not just first-pass MVP planning.

## Core Areas

- `../docs/`: guidance, workflow mapping, conventions, and rationale
- `repositories.yaml`: repo topology registry for workspace and parent-repo orchestration
- `current/`: active phase working set
- `previous/`: immutable snapshots of completed phases
- `lessons/`: reusable practices and anti-patterns extracted at closeout
- `roadmap/`: project-level direction and approved phase sequence

## Authority Files

- `repositories.yaml`: machine-readable repo topology and parent/child ownership map
- `roadmap/roadmap.yaml`: machine source of truth for roadmap-level state
- `roadmap/roadmap.md`: human-readable roadmap summary
- `current/phase-state.yaml`: machine source of truth for the active phase
- `current/phase.md`: human-readable active-phase brief
- `current/initiative-index.yaml`: machine source of truth for concurrent initiative routing in workspace or orchestration scope

If files disagree:

- `roadmap.yaml` wins over `roadmap.md`
- `phase-state.yaml` wins over `phase.md`
- instantiated files in `framework/` always win over copied starter templates
- `templates/` provides starter artifacts only and is never authoritative during live execution

## Working Areas

- `current/brainstorming/detailed/`: detailed brainstorming for the active slice
- `current/research/`: project context, market, domain, technical, strategy, and implementation research
- `current/planning/`: brief, PRD, UX design, architecture, and epics
- `current/implementation/`: stories, evidence, retrospectives, and automation runtime reports
- `current/testing/`: test design, automation, reviews, and gates, including secure sub-lanes
- `current/initiatives/`: concurrent initiative workstreams for workspace or orchestration scope
- `roadmap/brainstorming/`: high-level project brainstorming
- `roadmap/research/`: high-level market, domain, and technical research
- `roadmap/strategy/`: high-level innovation strategy and opportunity framing
- `roadmap/storytelling/`: optional high-level storytelling artifacts
- `roadmap/product-brief/`: high-level product brief artifacts

## Handoff Rule

- planning artifacts remain in `planning/` until stable
- stable human-facing content may graduate into the repo `docs/` tree only with owner, lifecycle state, destination path, and replacement or archive note
- automation runtime files, gate packages, and phase-specific evidence remain in the planning framework and do not promote into `docs/`

## Naming Rules

- phase snapshot folder: `<phase-slug>-<YYYY-MM-DD>`
- lesson folder: `<phase-slug>-<YYYY-MM-DD>`
- roadmap archive folder: `<YYYY-MM-DD>`
- `phase-slug` and phase IDs MUST be lowercase kebab-case
- file-system dates MUST use `YYYY-MM-DD`

## Lifecycle

1. initialize or normalize the framework with `/bmad-bmm-init-planning` when needed
2. refresh repo topology with `/bmad-bmm-sync-repositories` when repos are added, moved, or missed
3. from workspace or orchestration roots, use `/bmad-bmm-workspace-bootstrap` to initialize selected child repos
4. update roadmap-level artifacts in `roadmap/`, normally through `/bmad-bmm-project-roadmap`
5. activate one approved slice into `current/` with `Phase Sync`
6. if the repo is operating in workspace or orchestration scope, route concurrent initiatives with `Initiative Routing`
7. run detailed analysis, planning, solutioning, implementation, and gates in `current/`
8. close the phase with `../docs/phase-closeout-checklist.md`
9. move the frozen phase snapshot into `previous/`
10. record reusable learning in `lessons/`
