---
name: bmad-bmm-initiative-routing
description: "For workspace or parent repos, route the approved active phase into concurrent repo-targeted initiative workstreams without creating repo-local delivery artifacts."
---

# /bmad-bmm-initiative-routing

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-bmm-initiative-routing`.

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

### Initiative Routing
- Phase: `2-planning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/planning/initiative-routing/workflow.yaml`
- Preferred agent: John (Product Manager)
- Mode / options: Create Mode
- Output lane: `planning_initiatives_root`
- Expected outputs: initiative routing report|initiative index|initiative workstreams
- Summary: For workspace or parent repos, route the approved active phase into concurrent repo-targeted initiative workstreams without creating repo-local delivery artifacts.
