---
name: bmad-bmm-validate-docs
description: "Validate docs structure, policy compliance, and navigation integrity before closeout."
---

# /bmad-bmm-validate-docs

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-bmm-validate-docs`.

## Scope

- Covered phases: implementation
- Primary agents: Paige (Technical Writer)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Validate Docs
- Phase: `4-implementation`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/documentation/validate-docs/workflow.yaml`
- Preferred agent: Paige (Technical Writer)
- Mode / options: Validate Mode
- Output lane: `docs_reference_dir`
- Expected outputs: documentation validation report|gate recommendation
- Summary: Validate docs structure, policy compliance, and navigation integrity before closeout.
