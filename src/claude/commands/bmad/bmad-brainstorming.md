---
name: bmad-brainstorming
description: "Generate diverse ideas through interactive techniques. Broad strategic brainstorming writes to roadmap lane by default."
---

# /bmad-brainstorming

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-brainstorming`.

## Scope

- Covered phases: analysis, anytime
- Primary agents: Mary (Business Analyst)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Brainstorm Project
- Phase: `1-analysis`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/core/workflows/brainstorming/workflow.md`
- Preferred agent: Mary (Business Analyst)
- Mode / options: data=_bmad/modules/custom/bmm/data/project-context-template.md
- Output lane: `roadmap_brainstorming_dir`
- Expected outputs: brainstorming session
- Summary: Expert guided facilitation through a single or multiple techniques.

### Brainstorming
- Phase: `anytime`
- Module: `core`
- Workflow: `_bmad/modules/custom/core/workflows/brainstorming/workflow.md`
- Preferred agent: Mary (Business Analyst)
- Output lane: `roadmap_brainstorming_dir`
- Expected outputs: brainstorming session
- Summary: Generate diverse ideas through interactive techniques. Broad strategic brainstorming writes to roadmap lane by default.
