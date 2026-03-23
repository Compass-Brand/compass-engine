---
name: bmad-bmm-implementation-research
description: "Implementation-focused research for active epics and stories plus delivery risk reduction."
---

# /bmad-bmm-implementation-research

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-bmm-implementation-research`.

## Scope

- Covered phases: implementation
- Primary agents: Mary (Business Analyst)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Implementation Research
- Phase: `4-implementation`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/4-implementation/implementation-research/workflow.md`
- Preferred agent: Mary (Business Analyst)
- Mode / options: Create Mode
- Output lane: `current_implementation_research_dir`
- Expected outputs: implementation research
- Summary: Implementation-focused research for active epics and stories plus delivery risk reduction.
