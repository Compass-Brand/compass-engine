---
name: bmad-cis-problem-solving
description: "Apply structured problem-solving methods to delivery blockers, design traps, or implementation challenges without forking the main BMAD pipeline."
---

# /bmad-cis-problem-solving

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-cis-problem-solving`.

## Scope

- Covered phases: anytime
- Primary agents: Dr. Quinn (Master Problem Solver)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Problem Solving
- Phase: `anytime`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/anytime/problem-solving/workflow.yaml`
- Preferred agent: Dr. Quinn (Master Problem Solver)
- Mode / options: Create Mode
- Output lane: `current_implementation_research_dir`
- Expected outputs: problem-solving analysis
- Summary: Apply structured problem-solving methods to delivery blockers, design traps, or implementation challenges without forking the main BMAD pipeline.
