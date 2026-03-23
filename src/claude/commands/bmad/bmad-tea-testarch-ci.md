---
name: bmad-tea-testarch-ci
description: "TEA insert: align CI/CD quality automation with the current repo reality before readiness approval."
---

# /bmad-tea-testarch-ci

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-tea-testarch-ci`.

## Scope

- Covered phases: solutioning
- Primary agents: Murat (Master Test Architect and Quality Advisor)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### CI/CD Alignment
- Phase: `3-solutioning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/testarch/ci/workflow.yaml`
- Preferred agent: Murat (Master Test Architect and Quality Advisor)
- Mode / options: Create Mode
- Output lane: `current_evidence_dir`
- Expected outputs: ci/cd alignment notes|pipeline updates
- Summary: TEA insert: align CI/CD quality automation with the current repo reality before readiness approval.
