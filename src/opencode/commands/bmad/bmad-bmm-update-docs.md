---
name: bmad-bmm-update-docs
description: "Checkpoint docs update after planning and experience-design artifacts are established."
---

# /bmad-bmm-update-docs

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-bmm-update-docs`.

## Scope

- Covered phases: planning, solutioning, implementation
- Primary agents: Paige (Technical Writer)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Update Docs (Planning)
- Phase: `2-planning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/documentation/update-docs/workflow.yaml`
- Preferred agent: Paige (Technical Writer)
- Mode / options: Create Mode
- Output lane: `docs_reference_dir`
- Expected outputs: documentation update report
- Summary: Checkpoint docs update after planning and experience-design artifacts are established.

### Update Docs (Solutioning)
- Phase: `3-solutioning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/documentation/update-docs/workflow.yaml`
- Preferred agent: Paige (Technical Writer)
- Mode / options: Create Mode
- Output lane: `docs_reference_dir`
- Expected outputs: documentation update report
- Summary: Checkpoint docs update after architecture, readiness, and security artifacts are refined.

### Update Docs (Implementation)
- Phase: `4-implementation`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/documentation/update-docs/workflow.yaml`
- Preferred agent: Paige (Technical Writer)
- Mode / options: Create Mode
- Output lane: `docs_reference_dir`
- Expected outputs: documentation update report
- Summary: Checkpoint docs update at epic boundaries or major implementation milestones.
