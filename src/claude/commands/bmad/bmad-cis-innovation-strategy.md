---
name: bmad-cis-innovation-strategy
description: "Identify disruption opportunities and strategic bets that strengthen roadmap-level product direction. Phase-scoped runs should redirect outputs to the current strategy lane."
---

# /bmad-cis-innovation-strategy

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-cis-innovation-strategy`.

## Scope

- Covered phases: analysis
- Primary agents: Victor (Disruptive Innovation Oracle)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Innovation Strategy
- Phase: `1-analysis`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/1-analysis/innovation-strategy/workflow.yaml`
- Preferred agent: Victor (Disruptive Innovation Oracle)
- Mode / options: Create Mode
- Output lane: `roadmap_strategy_dir`
- Expected outputs: innovation strategy
- Summary: Identify disruption opportunities and strategic bets that strengthen roadmap-level product direction. Phase-scoped runs should redirect outputs to the current strategy lane.
