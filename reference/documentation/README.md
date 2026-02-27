# Documentation Reference Framework

This directory is the canonical documentation framework for Compass Engine.

## Purpose

- Define company-wide standards for human and AI documentation.
- Ensure documentation quality and structure are consistent across all projects.
- Keep policy decisions, authoring templates, and enforcement guidance in one place.

## Domain Split

### Human Domain

`human/` contains enforceable standards and templates for all human-facing docs.

### AI Domain

`ai/` contains standards for AI-facing context and behavior documentation.

Human and AI standards are intentionally separate and MUST NOT be mixed in the same policy files.

## Precedence and Interpretation

1. `human/policies/` files define enforceable requirements.
2. `human/templates/` files operationalize those requirements.
3. If guidance conflicts, policy files win.

Normative keywords `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are requirement levels.

## Human Policy Model

Every human policy file follows this model:

1. Requirement statement.
2. `Rationale:` line explaining why the rule exists.
3. `Implementation Playbook (Mandatory):` execution steps.

This is required so teams can understand not only what to do, but why the standard exists.

## Change Control

- Any exception MUST be documented with scope, owner, rationale, and expiry date.
- Policy changes MUST be approved by a documentation owner.
- Template changes MUST remain aligned to current policy language.

## Structure

```text
reference/documentation/
├── ai/
│   └── README.md
├── human/
│   ├── README.md
│   ├── policies/
│   │   ├── architecture-standard.md
│   │   ├── docs-structure-standard.md
│   │   ├── documentation-governance.md
│   │   ├── guides-standard.md
│   │   └── style-standard.md
│   └── templates/
│       ├── adr.md
│       ├── guide-howto.md
│       ├── guide-tutorial.md
│       ├── readme-docs-index.md
│       └── readme-root.md
└── README.md
```
