---
name: bmad-cybersec-security-architecture-review
description: "Review the draft architecture with zero-trust and control-assessment lenses when the security lane is active."
---

# /bmad-cybersec-security-architecture-review

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-cybersec-security-architecture-review`.

## Scope

- Covered phases: solutioning
- Primary agents: Bastion (Compass Security Architect)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Security Architecture Review
- Phase: `3-solutioning`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/3-solutioning/security-architecture-review/workflow.md`
- Preferred agent: Bastion (Compass Security Architect)
- Mode / options: Create Mode
- Output lane: `current_security_review_dir`
- Expected outputs: security architecture review
- Summary: Review the draft architecture with zero-trust and control-assessment lenses when the security lane is active.
