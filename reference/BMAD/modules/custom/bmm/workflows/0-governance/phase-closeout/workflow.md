---
name: phase-closeout
description: 'Close active phase and archive artifacts into previous/ with lessons capture. Use when the user says "close this phase" or "run phase closeout".'
---

# Phase Closeout Workflow

**Goal:** Close the active phase by archiving current artifacts, capturing lessons, and preparing the next phase scaffold.

**Your Role:** You are a sprint/phase facilitator executing closeout rigorously using Compass planning conventions.

## CONFIGURATION

Load config from `{project-root}/_bmad/bmm/config.yaml` and resolve:
- `planning_root`, `planning_current`, `planning_previous`, `planning_lessons`, `planning_roadmap`
- `phase_snapshot_file`, `current_evidence_dir`
- `user_name`, `communication_language`
- `date` as a system-generated value (`YYYY-MM-DD`)

## PREREQUISITES

Verify active-phase artifacts exist (or explicitly confirm intentional gaps):
- `{planning_current}/planning/prd/`
- `{planning_current}/planning/ux-design/`
- `{planning_current}/planning/architecture/`
- `{planning_current}/planning/epics/`
- `{planning_current}/implementation/stories/`
- `{planning_current}/implementation/evidence/`
- `{planning_current}/testing/`
- `{planning_current}/research/` (if used)
- `{phase_snapshot_file}`

## EXECUTION

1. Read `{phase_snapshot_file}` and extract:
   - phase slug (lowercase kebab-case)
   - completion date (`YYYY-MM-DD`, default `{{date}}` if not provided)
2. Create archive targets:
   - `{planning_previous}/{phase_slug}-{completion_date}/`
   - `{planning_lessons}/{phase_slug}-{completion_date}/`
3. Write a closeout report to:
   - `{current_evidence_dir}/phase-closeout-{completion_date}.md`
   Include:
   - completed scope
   - open risks
   - deltas vs goals
   - archival actions taken
4. Move all active phase artifacts from `{planning_current}/` into:
   - `{planning_previous}/{phase_slug}-{completion_date}/`
5. Create lessons file:
   - `{planning_lessons}/{phase_slug}-{completion_date}/lessons.md`
   With sections:
   - what worked
   - what failed
   - what to change next phase
6. Recreate clean current scaffold:
   - `brainstorming/`
   - `planning/prd/`
   - `planning/product-brief/`
   - `planning/ux-design/`
   - `planning/architecture/`
   - `planning/epics/`
   - `implementation/stories/`
   - `implementation/evidence/`
   - `research/`
   - `testing/`
7. Initialize new `{phase_snapshot_file}` with active status and next-phase placeholders.
8. Update `{planning_roadmap}/roadmap.md` with:
   - closed phase reference
   - next horizon notes
9. If roadmap artifacts were superseded, move them to dated archive lanes:
   - `{planning_roadmap}/archive/brainstorming/{completion_date}/`
   - `{planning_roadmap}/archive/research/{completion_date}/`
   - `{planning_roadmap}/archive/product-brief/{completion_date}/`

## OUTPUT RULES

- Never use relative dates in folder/file names.
- Do not leave closed-phase artifacts in `{planning_current}`.
- Keep phase snapshot naming strictly: `{phase_slug}-{YYYY-MM-DD}`.
