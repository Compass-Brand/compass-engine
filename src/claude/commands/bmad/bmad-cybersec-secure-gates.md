---
name: bmad-cybersec-secure-gates
description: "Apply the conditional pre-implementation security gate and record the draft gate package before readiness approval."
---

# /bmad-cybersec-secure-gates

Use this Claude command to invoke the Compass BMAD workflow entry point for `bmad-cybersec-secure-gates`.

## Scope

- Covered phases: solutioning, implementation
- Primary agents: Bastion (Compass Security Architect)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Secure Readiness Gate
- Phase: `3-solutioning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/4-implementation/secure-gates/workflow.md`
- Preferred agent: Bastion (Compass Security Architect)
- Mode / options: Readiness Mode
- Output lane: `current_secure_gates_draft_dir`
- Expected outputs: secure readiness gate report
- Summary: Apply the conditional pre-implementation security gate and record the draft gate package before readiness approval.

### Secure Release Gate
- Phase: `4-implementation`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/4-implementation/secure-gates/workflow.md`
- Preferred agent: Bastion (Compass Security Architect)
- Mode / options: Release Mode
- Output lane: `current_secure_release_gate_dir`
- Expected outputs: secure release gate report
- Summary: Apply the conditional release security gate using available test, scan, and security evidence before final validation and closeout.
