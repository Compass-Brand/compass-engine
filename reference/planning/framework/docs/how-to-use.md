# How To Use The Planning Framework

This guide defines daily usage for `reference/planning/framework/`.

## Quick Start

1. Read `../README.md` for model boundaries.
2. Open `../current/phase.md` and confirm phase metadata is current.
3. Place each new artifact in its required location (table below).
4. Keep active work in `../current/` only.
5. Use `phase-closeout-checklist.md` when the phase is complete.

## Artifact Placement

| Artifact | Destination |
| --- | --- |
| Phase overview and goals | `../current/phase.md` |
| Brainstorm notes | `../current/brainstorming/` |
| PRD drafts/finals | `../current/planning/prd/` |
| UX designs | `../current/planning/ux-design/` |
| Architecture outputs | `../current/planning/architecture/` |
| Epic definitions | `../current/planning/epics/` |
| Implementation stories | `../current/implementation/stories/` |
| Implementation evidence | `../current/implementation/evidence/` |
| Implementation research | `../current/research/` |
| Testing plans/results | `../current/testing/` |
| Cross-phase roadmap content | `../roadmap/` |

## Phase Lifecycle

1. Start: initialize `../current/phase.md`.
2. Plan: create PRD, UX, architecture, and epics in `../current/planning/`.
3. Implement: produce stories and evidence in `../current/implementation/`.
4. Validate: collect testing and research outputs.
5. Close: move `current` snapshot to `../previous/<phase-slug>-<YYYY-MM-DD>/`.
6. Learn: create `../lessons/<phase-slug>-<YYYY-MM-DD>/` entry.

## Weekly Operating Rhythm

1. Monday: confirm `phase.md` goals and planned artifacts for the week.
2. Midweek: verify artifacts are in correct paths and status is explicit.
3. Friday: update roadmap deltas and record lesson candidates.
4. End-of-phase: execute full closeout checklist.
