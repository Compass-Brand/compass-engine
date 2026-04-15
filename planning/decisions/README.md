# Architecture Decision Records (ADRs)

This directory holds Architecture Decision Records for compass-engine. An ADR is a lightweight, dated record of a significant design or process choice that affects how this repo is built, distributed, or integrated with upstream BMAD.

## When to write an ADR

Write one when a decision:

- Changes how compass-engine builds, ships, or consumes upstream BMAD (`tools/build.js`, `tools/push.js`, submodule posture, marketplace distribution).
- Constrains future work across multiple phases or beads issues.
- Establishes a supply-chain boundary (allowed vs. disallowed upstream imports, network touchpoints).
- Creates or removes a directory or contract that other repos or humans will depend on.

Routine implementation choices — file layouts inside a single skill, test helpers, local refactors — do not need an ADR.

## Format

Each ADR is a single Markdown file numbered sequentially: `adr-NNNN-short-slug.md`. Standard sections:

- **Context** — what prompted the decision; cite audit notes, beads issues, upstream PRs.
- **Options considered** — enumerate alternatives with tradeoffs.
- **Decision** — the chosen option, with justification grounded in the context.
- **Consequences** — what changes, what doesn't, downstream impact.
- **Backwards-compatibility plan** — migration path, if any.
- **References** — links to audit notes, issues, upstream PRs, code paths.

## Status

ADRs are immutable once merged. If a decision is revisited, write a new ADR that supersedes it (and add a `Superseded by: adr-NNNN` line to the old one).

## Index

- [ADR-0001: Marketplace adoption (Option 5 narrowed)](./adr-0001-marketplace-adoption.md)
