---
name: bmad-review-adversarial-general
description: "Review content critically to find issues and weaknesses. Use for quality assurance or before finalizing deliverables. Code Review in other modules run this automatically, but its useful also for document reviews"
---

# /bmad-review-adversarial-general

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-review-adversarial-general`.

## Scope

- Covered phases: anytime
- Primary agents: workflow-defined

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Adversarial Review (General)
- Phase: `anytime`
- Module: `core`
- Workflow: `_bmad/modules/custom/core/tasks/review-adversarial-general.md`
- Summary: Review content critically to find issues and weaknesses. Use for quality assurance or before finalizing deliverables. Code Review in other modules run this automatically, but its useful also for document reviews
