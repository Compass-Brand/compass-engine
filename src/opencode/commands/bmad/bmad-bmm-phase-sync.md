---
name: bmad-bmm-phase-sync
description: "Select and frame the active roadmap slice, maintain the human phase brief, and keep the machine phase state aligned."
---

# /bmad-bmm-phase-sync

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-bmm-phase-sync`.

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

### Phase Sync
- Phase: `2-planning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/0-governance/phase-sync/workflow.md`
- Preferred agent: John (Product Manager)
- Mode / options: Create Mode
- Output lane: `phase_snapshot_file`
- Expected outputs: phase brief|phase state
- Required checkpoint: yes
- Summary: Select and frame the active roadmap slice, maintain the human phase brief, and keep the machine phase state aligned.
