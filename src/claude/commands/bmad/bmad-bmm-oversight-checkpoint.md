---
name: bmad-bmm-oversight-checkpoint
description: "Generate a verification report from oversight risk and assumption registers."
---

# /bmad-bmm-oversight-checkpoint

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-bmm-oversight-checkpoint`.

## Scope

- Covered phases: governance
- Primary agents: John (Product Manager)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Oversight Checkpoint
- Phase: `0-governance`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/0-governance/oversight-checkpoint/workflow.md`
- Preferred agent: John (Product Manager)
- Mode / options: Create Mode
- Output lane: `oversight_report_file`
- Expected outputs: verification report|risk register|assumption register
- Required checkpoint: yes
- Summary: Generate a verification report from oversight risk and assumption registers.
