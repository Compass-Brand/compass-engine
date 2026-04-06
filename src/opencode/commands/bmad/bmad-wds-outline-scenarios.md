---
name: bmad-wds-outline-scenarios
description: "”Transform the active slice trigger map into scenario outlines that feed UX"
---

# /bmad-wds-outline-scenarios

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-wds-outline-scenarios`.

## Scope

- Covered phases: planning
- Primary agents: ”Saga” (”Compass WDS Analyst”)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Outline Scenarios
- Phase: `2-planning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/2-plan-workflows/outline-scenarios/workflow.md`
- Preferred agent: ”Saga” (”Compass WDS Analyst”)
- Mode / options: ”Create Mode”
- Output lane: `conceptual specs`
- Expected outputs: and delivery handoff.”
- Summary: ”Transform the active slice trigger map into scenario outlines that feed UX
