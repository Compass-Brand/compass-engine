---
name: bmad-bmm-domain-research
description: "Industry domain deep dive, subject matter expertise, and terminology."
---

# /bmad-bmm-domain-research

Use this OpenCode command to invoke the Compass BMAD workflow entry point for `bmad-bmm-domain-research`.

## Scope

- Covered phases: analysis
- Primary agents: Mary (Business Analyst)

## Execution Rules

1. Resolve `_bmad/` from the current target repo only. Use the local repo root that contains the active `planning/`, `docs/`, and `_bmad/` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate `_bmad/` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

### Domain Research
- Phase: `1-analysis`
- Module: `bmm`
- Workflow: `_bmad/modules/custom/bmm/workflows/1-analysis/research/workflow-domain-research.md`
- Preferred agent: Mary (Business Analyst)
- Mode / options: Create Mode
- Output lane: `roadmap_domain_research_dir`
- Expected outputs: research documents
- Summary: Industry domain deep dive, subject matter expertise, and terminology.
