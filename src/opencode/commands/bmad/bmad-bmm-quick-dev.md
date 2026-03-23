---
name: bmad-bmm-quick-dev
description: "Quick one-off tasks, small changes, simple apps, and utilities without extensive planning. Do not suggest for complex work unless requested or the user explicitly wants to skip the full BMAD method."
---

# /bmad-bmm-quick-dev

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-bmm-quick-dev`.

## Scope

- Covered phases: anytime
- Primary agents: Barry (Quick Flow Solo Dev)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Quick Dev
- Phase: `anytime`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/bmad-quick-flow/quick-dev/workflow.md`
- Preferred agent: Barry (Quick Flow Solo Dev)
- Mode / options: Create Mode
- Output lane: `current_evidence_dir`
- Summary: Quick one-off tasks, small changes, simple apps, and utilities without extensive planning. Do not suggest for complex work unless requested or the user explicitly wants to skip the full BMAD method.
