---
name: bmad-autonomous-refinement-loop
description: "Run autonomous party-mode and auto-elicitation loops with agent teams until zero unresolved issues remain; manual Party Mode and Advanced Elicitation remain available separately. Escalates only on blocked fixes."
---

# /bmad-autonomous-refinement-loop

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-autonomous-refinement-loop`.

## Scope

- Covered phases: anytime
- Primary agents: workflow-defined

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Autonomous Refinement Loop
- Phase: `anytime`
- Module: `core`
- Workflow: `_bmad/modules/custom/core/workflows/autonomous-refinement-loop/workflow.md`
- Summary: Run autonomous party-mode and auto-elicitation loops with agent teams until zero unresolved issues remain; manual Party Mode and Advanced Elicitation remain available separately. Escalates only on blocked fixes.
