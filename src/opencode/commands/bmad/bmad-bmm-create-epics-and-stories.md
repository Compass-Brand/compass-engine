---
name: bmad-bmm-create-epics-and-stories
description: "Create the epics and stories list for the active slice."
---

# /bmad-bmm-create-epics-and-stories

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-bmm-create-epics-and-stories`.

## Scope

- Covered phases: solutioning
- Primary agents: John (Product Manager)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Create Epics and Stories
- Phase: `3-solutioning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/3-solutioning/create-epics-and-stories/workflow.md`
- Preferred agent: John (Product Manager)
- Mode / options: Create Mode
- Output lane: `current_epics_dir`
- Expected outputs: epics and stories
- Required checkpoint: yes
- Summary: Create the epics and stories list for the active slice.
