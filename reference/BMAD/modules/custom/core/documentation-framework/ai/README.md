# AI Documentation Domain

This directory is the home for AI-facing documentation standards, automation contracts, and model-operational guidance.

## Boundary

- AI behavior and context artifacts are governed separately from human-facing docs.
- Human documentation policy and templates are defined in `../human/`.
- This domain covers AI-operational artifacts such as prompt-policy contracts, automation wrapper expectations, context rules, and agent-facing conventions.

When a deployed project carries project-local AI documentation, it should live under `docs/ai/` and derive its standards from this framework.

## Required Content Areas

- AI behavior and safety expectations
- automation wrapper and state-model guidance
- context-loading and handoff rules
- agent or model integration notes when those become stable
- links to the canonical reference-stage BMAD automation specs when relevant

## Working Rule

- AI-facing standards may begin in `reference/BMAD/` or `reference/planning/` while they are still being shaped
- once stable, they should graduate into this AI documentation domain with an owner, lifecycle state, and explicit scope
- runtime state files, gate packages, and phase-specific evidence do not belong here
- live framework state in `reference/planning/framework/` remains authoritative while standards are still reference-stage
- templates and reference drafts are never authoritative once a live framework artifact exists

## Current Reference Inputs

- `reference/BMAD/tools/automation/`
- `reference/BMAD/BMAD-workflow.md`
- `reference/planning/framework/`

## Minimum Governance

- each AI-facing standard should declare owner and last-updated date
- AI-facing standards should link to the human policy they complement when one exists
- deprecated AI-facing docs should include a replacement link or deprecation reason
