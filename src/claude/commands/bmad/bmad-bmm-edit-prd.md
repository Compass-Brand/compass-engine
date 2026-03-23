---
name: bmad-bmm-edit-prd
description: "Revise an existing PRD when validation, WDS, or architecture work exposes requirement gaps."
---

# /bmad-bmm-edit-prd

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-bmm-edit-prd`.

## Scope

- Covered phases: planning
- Primary agents: John (Product Manager)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Edit PRD
- Phase: `2-planning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/2-plan-workflows/create-prd/workflow-edit-prd.md`
- Preferred agent: John (Product Manager)
- Mode / options: Edit Mode
- Output lane: `current_prd_dir`
- Expected outputs: updated prd
- Summary: Revise an existing PRD when validation, WDS, or architecture work exposes requirement gaps.
