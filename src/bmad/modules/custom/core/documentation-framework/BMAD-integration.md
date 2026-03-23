# BMAD And Documentation Integration

This document defines how the Compass BMAD method consumes the documentation framework and writes live project documentation.

## Authority Order

1. `docs/human/policies/` defines the human-doc requirements.
2. `docs/human/templates/` operationalizes those requirements.
3. `docs/human/policies/user-overrides.md` may add project-specific overrides without weakening baseline policy.
4. `docs/` is the live deployed documentation tree in target repositories.
5. BMAD docs workflow reports are evidence and audit artifacts, not the canonical human docs themselves.

## Deployment Model

In deployed project repositories:

- `docs/` is the live documentation tree.
- `planning/` is the live planning tree.
- `_bmad/` is the live BMAD runtime tree.

The BMAD method should therefore read standards from `docs/` and write project documentation into `docs/`.

## BMAD Phase To Docs Mapping

### Initialize Docs

`Initialize Docs` must:

- scaffold the required `docs/` tree
- install the documentation control-plane lanes used by Compass BMAD:
  - `docs/human/policies/`
  - `docs/human/templates/`
  - `docs/human/policies/user-overrides.md`
  - `docs/ai/README.md`
- create or refresh index `README.md` files using the documentation templates
- record docs ownership and review expectations in `docs/README.md`
- preserve any migrated legacy docs in a dated snapshot during brownfield setup
- preserve project-owned `docs/README.md` content when installing or refreshing Compass docs control-plane files

### Update Docs (Planning)

Planning-stage docs updates must:

- classify each updated doc by primary Diataxis mode
- route onboarding, task, explanation, and reference content into the correct docs destination
- capture promotion candidates when planning artifacts are becoming stable human docs
- update navigation and related links

### Update Docs (Solutioning)

Solutioning-stage docs updates must:

- update architecture overview content
- create or update ADRs when decisions are expensive to reverse
- record interfaces, dependencies, and operational linkage when architecture artifacts change
- keep docs/reference pages aligned with implementation constraints and readiness evidence

### Update Docs (Implementation)

Implementation-stage docs updates must:

- refresh developer and operator guidance when implementation behavior changes
- add troubleshooting, run, or usage guidance when new workflows become real
- keep reference entries aligned with shipped behavior

### Validate Docs

`Validate Docs` must audit:

- docs tree structure and indexing
- policy/template sync
- lifecycle and review metadata
- Diataxis mode separation
- architecture-document requirements
- style and quality rules
- planning-to-doc promotion evidence when relevant

## Required Report Content

### Docs Initialization Report

Must include:

- migrated inputs and snapshot path
- created control-plane and user-facing docs locations
- docs owner and ownership-model status
- unresolved lifecycle or migration gaps

### Docs Update Report

Must include:

- update scope
- files changed
- source artifacts used
- target docs destinations
- Diataxis mode chosen for new or materially changed docs
- lifecycle, owner, and review metadata updates
- ADRs created or updated
- promotion candidates or blockers

### Docs Validation Report

Must include:

- structure results
- governance and lifecycle results
- Diataxis and architecture results
- style and quality results
- blocking issues
- remediation order
- final gate recommendation

## Hard Rules

- BMAD docs workflows must read standards from `docs/`, not a stale copy.
- Live project docs belong in `docs/`, not in `reference/`.
- Compass documentation bundle ownership is limited to:
  - `docs/human/`
  - `docs/ai/`
  - `docs/BMAD-integration.md`
- `docs/README.md` remains project-owned and must not be overwritten by the shipped documentation bundle.
- Planning artifacts do not become canonical docs without owner, lifecycle state, destination, and replacement or archive notes.
- Workflow reports are evidence only; they do not replace final docs in `docs/`.
