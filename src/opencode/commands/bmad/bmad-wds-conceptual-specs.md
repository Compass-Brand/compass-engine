---
name: bmad-wds-conceptual-specs
description: "Convert approved UX direction and scenario context into implementation-ready conceptual specifications for the active slice."
---

# /bmad-wds-conceptual-specs

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-wds-conceptual-specs`.

## Scope

- Covered phases: planning
- Primary agents: Freya (Compass WDS Designer)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Conceptual Specifications
- Phase: `2-planning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/2-plan-workflows/wds-ux-design/workflow-specify.md`
- Preferred agent: Freya (Compass WDS Designer)
- Mode / options: Create Mode
- Output lane: `current_conceptual_specifications_dir`
- Expected outputs: conceptual specifications
- Summary: Convert approved UX direction and scenario context into implementation-ready conceptual specifications for the active slice.
