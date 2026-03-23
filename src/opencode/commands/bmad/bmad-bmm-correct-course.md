---
name: bmad-bmm-correct-course
description: "Anytime: navigate significant changes. May recommend restart, PRD updates, architecture changes, sprint replanning, or story corrections."
---

# /bmad-bmm-correct-course

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-bmm-correct-course`.

## Scope

- Covered phases: anytime
- Primary agents: Bob (Scrum Master)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Correct Course
- Phase: `anytime`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/4-implementation/correct-course/workflow.yaml`
- Preferred agent: Bob (Scrum Master)
- Mode / options: Create Mode
- Output lane: `current_evidence_dir`
- Expected outputs: change proposal
- Summary: Anytime: navigate significant changes. May recommend restart, PRD updates, architecture changes, sprint replanning, or story corrections.
