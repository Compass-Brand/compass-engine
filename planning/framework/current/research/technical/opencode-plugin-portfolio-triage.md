# OpenCode Plugin Portfolio Triage

Status: draft
Owner:
Last Updated: 2026-03-24
Phase ID:
Parent Issue: `bmad-engine-ygy`

## Objective

- Sort approximately 30 candidate OpenCode plugins into a bounded review structure instead of a flat list.
- Decide for each plugin whether Compass should adopt it as-is, wrap it, rebuild it in-house, or skip it.
- Produce a shortlist of 2-3 pilot candidates that fit the Compass OpenCode plugin strategy.

## Scope

- Slice focus: OpenCode plugin portfolio triage for Compass workflow fit
- Systems touched: `src/opencode/`, `src/bmad/`, `planning/`, `bd`
- External dependencies: candidate third-party OpenCode plugins under review

## Recommended Review Order

1. Group every plugin before scoring it.
2. Score each plugin against the same matrix.
3. Force a single decision: adopt as-is, wrap, rebuild, or skip.
4. Consolidate only the top 2-3 pilots into implementation recommendations.

## Functional Grouping

Use one primary group per plugin.

| Group | Decision bias | Review issue |
| --- | --- | --- |
| BMAD workflow and command surface | Bias toward `wrap` or `rebuild` because workflow authority should stay in Compass | `bmad-engine-4u2` |
| Tracking and session lifecycle | Bias toward `wrap` or `rebuild` because beads/session state is workflow-critical | `bmad-engine-hx3` |
| Context, memory, and oversight | Bias toward `skip` or narrow pilots unless there is a concrete approved problem | `bmad-engine-xlj` |
| Repo, file, and code utilities | Bias toward `adopt as-is` for safe commodity helpers, otherwise `wrap` | `bmad-engine-bdp` |
| External integration and interoperability | Bias toward `wrap` because naming, security, and parity control matter | `bmad-engine-jm0` |

## Evaluation Matrix

Score each dimension from 1 to 5 unless noted otherwise.

| Dimension | What to evaluate |
| --- | --- |
| BMAD phase fit | Does the plugin support the shipped BMAD workflow without changing artifact authority or gate order? |
| Architecture fit | Does it map cleanly to `plugin-core`, `provider-bmad`, `provider-tracking`, or `provider-interop`? |
| Cross-tool parity value | Does it reduce divergence across Claude, Codex, and OpenCode command surfaces? |
| Strategic leverage | Would this materially improve Compass delivery or operator efficiency? |
| Security and trust | Is the behavior understandable, reviewable, and acceptable to ship? |
| Maintenance burden | How costly is it to keep working over time? Lower burden should score higher. |
| Lock-in risk | How much does it tie Compass to an external runtime or opaque workflow? Lower lock-in should score higher. |
| Commodity factor | Is this generic utility behavior rather than workflow-defining logic? Higher means more commodity. |

## Decision Rules

- `Adopt as-is`
  - Commodity utility
  - Low lock-in
  - Minimal effect on BMAD sequencing, artifact authority, or beads lifecycle
- `Wrap`
  - Useful capability
  - Needs Compass naming, artifact paths, guardrails, or provider integration
- `Rebuild`
  - Workflow-defining
  - Parity-critical
  - Controls approvals, artifacts, issue state, or execution routing
- `Skip`
  - Low leverage
  - Redundant
  - High maintenance or lock-in
  - Pushes Compass toward the wrong workflow

## Default Heuristics

- Workflow-routing plugins should almost never be adopted raw.
- Beads-aware lifecycle plugins should usually be wrapped or rebuilt.
- Memory or oversight plugins should not be early pilots unless they solve an approved concrete gap.
- Commodity repo or file helpers are the best candidates for direct adoption.
- Interoperability plugins should be evaluated for whether they reduce or increase cross-tool drift.

## Review Table

Fill one row per candidate plugin.

| Plugin | Source | Primary group | BMAD fit | Architecture fit | Parity value | Strategic leverage | Security/trust | Maintenance | Lock-in | Commodity | Decision | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Pilot Selection Rules

- Limit the first implementation wave to 2-3 plugins.
- Prefer one workflow-facing candidate only if the wrapper/rebuild boundary is already clear.
- Prefer one tracking/lifecycle candidate only if its beads contract is explicit.
- Prefer at least one low-risk commodity or interoperability pilot to validate the integration path quickly.

## Beads Issue Structure

- Parent portfolio issue: `bmad-engine-ygy`
- Category review issues:
  - `bmad-engine-4u2` workflow and command surface
  - `bmad-engine-hx3` tracking and session lifecycle
  - `bmad-engine-xlj` context, memory, and oversight
  - `bmad-engine-bdp` repo, file, and code utilities
  - `bmad-engine-jm0` external integration and interoperability
- Consolidation issue:
  - `bmad-engine-8zr` shortlist and pilot recommendations

Dependency model:

- `bmad-engine-8zr` is blocked by all five category issues.
- `bmad-engine-ygy` is blocked by `bmad-engine-8zr`.
- Pilot implementation issues should be created only after the shortlist is approved.

## Recommended Next Step

Create the initial plugin inventory table in this file, assign each plugin one primary group, and start with the repo/file/code utility bucket first to establish scoring discipline on the lowest-risk set.

## Sources

- `docs/architecture/opencode-plugin-strategy.md`
- `docs/development/opencode/plugin-development.md`
- `src/opencode/plugins/README.md`
- `src/bmad/BMAD-workflow.md`

## Links Forward

- OpenCode plugin implementation work in `src/opencode/plugins/`
- OpenCode wrappers in `src/opencode/commands/` and `src/opencode/agents/`
- Follow-up pilot issues created from `bmad-engine-8zr`
