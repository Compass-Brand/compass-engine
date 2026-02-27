# How To Use The Planning Framework

This guide defines daily usage for `reference/planning/framework/`.

## Quick Start

1. Read `../framework/README.md` for model boundaries.
2. Open `../framework/current/phase.md` and confirm phase metadata is current.
3. Place each new artifact in its required location (table below).
4. Keep active work in `../framework/current/` only.
5. Use [phase-closeout-checklist.md](./phase-closeout-checklist.md) when the phase is complete.

## Artifact Placement

| Artifact | Destination |
| --- | --- |
| Phase overview and goals | `../framework/current/phase.md` |
| Brainstorm notes | `../framework/current/brainstorming/` |
| PRD drafts/finals | `../framework/current/planning/prd/` |
| UX designs | `../framework/current/planning/ux-design/` |
| Architecture outputs | `../framework/current/planning/architecture/` |
| Epic definitions | `../framework/current/planning/epics/` |
| Implementation stories | `../framework/current/implementation/stories/` |
| Implementation evidence | `../framework/current/implementation/evidence/` |
| Implementation research | `../framework/current/research/` |
| Testing plans/results | `../framework/current/testing/` |
| Cross-phase roadmap content | `../framework/roadmap/` |

## Phase Lifecycle

1. Start: initialize `../framework/current/phase.md`.
2. Plan: create PRD, UX, architecture, and epics in `../framework/current/planning/`.
3. Implement: produce stories and evidence in `../framework/current/implementation/`.
4. Validate: collect testing and research outputs.
5. Close: move `current` snapshot to `../framework/previous/<phase-slug>-<YYYY-MM-DD>/`.
6. Learn: create `../framework/lessons/<phase-slug>-<YYYY-MM-DD>/` entry.

## Weekly Operating Rhythm

1. Monday: confirm `phase.md` goals and planned artifacts for the week.
2. Midweek: verify artifacts are in correct paths and status is explicit.
3. Friday: update roadmap deltas and record lesson candidates.
4. End-of-phase: execute full closeout checklist.
