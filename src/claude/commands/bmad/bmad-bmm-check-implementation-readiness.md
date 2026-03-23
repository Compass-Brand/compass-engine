---
name: bmad-bmm-check-implementation-readiness
description: "Ensure the PRD, UX, architecture, epics, and stories are aligned before implementation starts."
---

# /bmad-bmm-check-implementation-readiness

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-bmm-check-implementation-readiness`.

## Scope

- Covered phases: solutioning
- Primary agents: Winston (Architect)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Check Implementation Readiness
- Phase: `3-solutioning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/3-solutioning/check-implementation-readiness/workflow.md`
- Preferred agent: Winston (Architect)
- Mode / options: Validate Mode
- Output lane: `current_testing_gates_draft_dir`
- Expected outputs: readiness report
- Required checkpoint: yes
- Summary: Ensure the PRD, UX, architecture, epics, and stories are aligned before implementation starts.
