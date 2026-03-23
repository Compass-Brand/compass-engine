# How To Use The Planning Framework

This guide defines daily usage for `reference/planning/framework/`.

## Quick Start

1. Read `../framework/README.md` for boundaries and authority rules.
2. Run `bd prime` after a fresh session or compaction so issue-tracking context is loaded before planning work starts.
3. Use `/bmad-bmm-init-planning` to scaffold or normalize the live framework before doing manual planning work.
4. Use `/bmad-bmm-project-roadmap` to create or update approved roadmap state.
5. Use the matching starter file in `../templates/` only when a planning artifact does not yet have a dedicated workflow.
6. Load `../framework/roadmap/roadmap.yaml` and `../framework/roadmap/roadmap.md` to understand approved roadmap state.
7. Load `../framework/current/phase-state.yaml` and `../framework/current/phase.md` to understand the active slice.
8. In workspace or orchestration repos, also load `../framework/repositories.yaml` and `../framework/current/initiative-index.yaml`.
9. Reconcile Beads tracking before execution:
   - record the active phase issue in `phase-state.yaml`
   - create or confirm epic and story issues before implementation begins
10. Place each artifact in its required location.
11. Keep active work in `../framework/current/` only.
12. If you are using automation wrappers, load `../../BMAD/tools/automation/README.md` and the relevant command spec before starting the run.
13. Use [phase-closeout-checklist.md](./phase-closeout-checklist.md) when the phase is complete.

## Authority Rules

- `roadmap.yaml` is authoritative over `roadmap.md`
- `phase-state.yaml` is authoritative over `phase.md`
- `bd` is authoritative for task and issue lifecycle; planning files hold references and planning state, not duplicate issue truth
- machine files update first, human files update second
- roadmap files change only for roadmap-level decisions
- phase files change for active-slice execution and scope
- copied framework artifacts are authoritative; templates are starter copies only
- do not update `reference/planning/templates/` to reflect live work inside an active phase

## Artifact Placement

| Artifact | Destination |
| --- | --- |
| Human roadmap summary | `../framework/roadmap/roadmap.md` |
| Machine roadmap state | `../framework/roadmap/roadmap.yaml` |
| Repo topology registry | `../framework/repositories.yaml` |
| High-level brainstorm | `../framework/roadmap/brainstorming/` |
| High-level market research | `../framework/roadmap/research/market/` |
| High-level domain research | `../framework/roadmap/research/domain/` |
| High-level technical research | `../framework/roadmap/research/technical/` |
| High-level innovation strategy and opportunity framing | `../framework/roadmap/strategy/` |
| High-level storytelling | `../framework/roadmap/storytelling/` |
| High-level product brief | `../framework/roadmap/product-brief/` |
| Human phase brief | `../framework/current/phase.md` |
| Machine phase state | `../framework/current/phase-state.yaml` |
| Initiative routing index | `../framework/current/initiative-index.yaml` |
| Initiative workstreams | `../framework/current/initiatives/<initiative-id>/` |
| Detailed brainstorming | `../framework/current/brainstorming/detailed/` |
| Project context | `../framework/current/research/project-context/` |
| Detailed market research | `../framework/current/research/market/` |
| Detailed domain research | `../framework/current/research/domain/` |
| Detailed technical research | `../framework/current/research/technical/` |
| Detailed innovation strategy and opportunity framing | `../framework/current/research/strategy/` |
| Implementation research | `../framework/current/research/implementation/` |
| Detailed product brief | `../framework/current/planning/brief/` |
| PRD drafts and validations | `../framework/current/planning/prd/` |
| WDS outputs | `../framework/current/planning/ux-design/` |
| Architecture and security outputs | `../framework/current/planning/architecture/` |
| Epics | `../framework/current/planning/epics/` |
| Stories | `../framework/current/implementation/stories/` |
| Implementation evidence and automation runtime files | `../framework/current/implementation/evidence/` |
| Retrospectives | `../framework/current/implementation/retrospectives/` |
| Test design | `../framework/current/testing/test-design/` |
| Test automation outputs | `../framework/current/testing/automation/` |
| Test reviews | `../framework/current/testing/reviews/` |
| Gate packages | `../framework/current/testing/gates/` |
| Secure readiness gate drafts | `../framework/current/testing/gates/draft/security/` |
| Approved secure readiness gate reports | `../framework/current/testing/gates/security/readiness/` |
| Secure release gate reports | `../framework/current/testing/gates/security/release/` |

## Phase Lifecycle

1. initialize or normalize the framework with `/bmad-bmm-init-planning` when needed, then build or refresh roadmap-level artifacts in `roadmap/`
2. run `Phase Sync` and initialize `phase-state.yaml` and `phase.md`
3. if the active slice is running in workspace or orchestration scope, run `Initiative Routing` and maintain `initiative-index.yaml`
4. execute detailed analysis in `current/brainstorming/detailed/` and `current/research/`
5. execute planning and experience design in `current/planning/`
6. execute solutioning, implementation, testing, automation, and gates in `current/`
7. close the phase and archive the frozen snapshot into `../framework/previous/<phase-slug>-<YYYY-MM-DD>/`
8. extract reusable lessons into `../framework/lessons/<phase-slug>-<YYYY-MM-DD>/`

## Promotion Rule

- planning artifacts remain in `reference/planning/` until they are stable
- once stable, they may graduate into the repo `docs/` tree only with an assigned owner, lifecycle state, destination path, and replacement link or archive note
- automation reports, gate packages, and runtime state files do not promote into `docs/`; they remain planning and evidence artifacts

## Weekly Operating Rhythm

1. start of week: confirm `phase-state.yaml`, `phase.md`, and the next checkpoint
2. midweek: verify artifacts are in the correct paths and stale outputs are explicit
3. before major gates: ensure machine state and human summaries agree
4. end of phase: execute full closeout with roadmap and phase state updates in the required order
5. at each execution boundary: claim or close the corresponding Beads issue and run `bd sync` when the issue set changes materially
