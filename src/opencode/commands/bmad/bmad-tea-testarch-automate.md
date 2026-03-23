---
name: bmad-tea-testarch-automate
description: "TEA insert: expand automated coverage after implementation. Pick the primary lane versus QA automation to avoid duplicates."
---

# /bmad-tea-testarch-automate

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-tea-testarch-automate`.

## Scope

- Covered phases: implementation
- Primary agents: Murat (Master Test Architect and Quality Advisor)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Test Automation
- Phase: `4-implementation`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/testarch/automate/workflow.yaml`
- Preferred agent: Murat (Master Test Architect and Quality Advisor)
- Mode / options: Create Mode
- Output lane: `current_testing_automation_dir`
- Expected outputs: test suite
- Summary: TEA insert: expand automated coverage after implementation. Pick the primary lane versus QA automation to avoid duplicates.
