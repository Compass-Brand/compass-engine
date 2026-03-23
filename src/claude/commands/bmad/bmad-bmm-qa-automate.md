---
name: bmad-bmm-qa-automate
description: "Generate automated API and E2E tests for implemented code using the existing project test framework. Use after implementation to add coverage, not for code review or story validation."
---

# /bmad-bmm-qa-automate

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-bmm-qa-automate`.

## Scope

- Covered phases: implementation
- Primary agents: Quinn (QA Engineer)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### QA Automation Test
- Phase: `4-implementation`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/qa-generate-e2e-tests/workflow.yaml`
- Preferred agent: Quinn (QA Engineer)
- Mode / options: Create Mode
- Output lane: `current_testing_automation_dir`
- Expected outputs: test suite
- Summary: Generate automated API and E2E tests for implemented code using the existing project test framework. Use after implementation to add coverage, not for code review or story validation.
