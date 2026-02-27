# Human Documentation Standards

This directory defines the official Compass company standard for human-facing documentation.

## Scope

These standards apply to all company projects regardless of repository visibility or audience.

## Normative Language

The keywords `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` indicate requirement level.

## Required Policy Format

Every policy document in `policies/` MUST include:

1. Purpose
2. Scope
3. Requirements
4. Per-rule `Rationale:`
5. `Implementation Playbook (Mandatory):` for each requirement
6. Compliance checks
7. Exceptions
8. Related links

This format exists so teams can execute consistently and understand the intent behind each rule.

## Contents

- `policies/` - enforceable standards and mandatory playbooks.
- `templates/` - approved templates aligned to policy.

## Required Use Sequence

1. Start with `policies/documentation-governance.md` for ownership, lifecycle, and enforcement.
2. Apply `policies/docs-structure-standard.md` to scaffold or audit folder structure.
3. Apply `policies/style-standard.md` to prose and formatting.
4. Apply `policies/guides-standard.md` for Diataxis mode selection and modern practices.
5. Apply `policies/architecture-standard.md` for architecture docs and ADRs.
6. Use templates in `templates/` when writing new docs.

## Template Set

- `adr.md` - architecture decision record template.
- `guide-howto.md` - task-oriented guide template.
- `guide-tutorial.md` - learning-oriented tutorial template.
- `readme-docs-index.md` - `docs/README.md` index template.
- `readme-root.md` - repository root README template.

## Boundary

This directory does not define AI behavior files (`AGENTS.md`, `CLAUDE.md`, or similar). AI documentation is handled separately under `../ai/`.
