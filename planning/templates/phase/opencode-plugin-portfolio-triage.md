# OpenCode Plugin Portfolio Triage

Status: draft
Owner:
Last Updated:
Phase ID:
Parent Issue:

## Objective

- Evaluate a candidate OpenCode plugin portfolio against Compass BMAD workflow, OpenCode plugin strategy, and cross-tool parity needs.
- Force a decision for each plugin: adopt as-is, wrap, rebuild, or skip.
- Produce a shortlist of pilot plugins worth integrating next.

## Review Scope

- Candidate count:
- Review source:
- Review window:
- Reviewers:

## Functional Grouping

Use one primary group per plugin.

| Group | What belongs here |
| --- | --- |
| BMAD workflow and command surface | Command dispatch, workflow routing, planning artifact generation, phase progression, approvals |
| Tracking and session lifecycle | Beads hooks, session recovery, issue state, closeout reminders, run-state checkpoints |
| Context, memory, and oversight | Memory layers, context carry-forward, reflection loops, oversight or review substrates |
| Repo, file, and code utilities | Repo scanning, file operations, code helpers, search, transformation, implementation support |
| External integration and interoperability | Third-party services, transport adapters, parity helpers across Claude/Codex/OpenCode |

## Evaluation Matrix

Score each dimension from 1 to 5 unless noted otherwise.

| Dimension | What to evaluate |
| --- | --- |
| BMAD phase fit | Does the plugin cleanly support analysis, planning, solutioning, implementation, or closeout without distorting the workflow? |
| Architecture fit | Does it map cleanly to `plugin-core`, `provider-bmad`, `provider-tracking`, or `provider-interop`? |
| Cross-tool parity value | Does it reduce divergence across Claude, Codex, and OpenCode surfaces? |
| Strategic leverage | Would this materially improve Compass workflow capability or speed? |
| Security and trust | Is the plugin behavior understandable, reviewable, and safe to ship? |
| Maintenance burden | How costly is it to keep compatible over time? Lower maintenance should score higher. |
| Lock-in risk | Does it couple Compass to an external runtime, vendor, or opaque behavior? Lower lock-in should score higher. |
| Commodity factor | Is this generic utility behavior that does not define Compass workflow? Higher means more commodity. |

## OpenCode Plugin Model Checks

Before deciding whether to adopt, wrap, rebuild, or skip, identify which official OpenCode extension surfaces the candidate uses.

| Surface | What to check |
| --- | --- |
| Event hooks | Does the plugin observe or modify command, file, session, todo, shell, tool, or TUI events? |
| Custom tools | Does it add new tools that should map to `provider-bmad`, `provider-tracking`, or `provider-interop`? |
| Skills | Does it rely on bundled `SKILL.md` guidance rather than only executable hooks? |
| Compaction | Does it change continuation or memory behavior using compaction hooks? |
| Storage paths | Does it write to its own canonical plan, task, or workflow files? |

Boundary rule:

- Additive overlays that annotate, visualize, or guide work can still fit Compass well.
- Plugins that become authoritative for tasks, plans, approvals, or artifact storage need stronger caution.

## Decision Rules

- `Adopt as-is`
  - Use for commodity capabilities with high utility, low lock-in, and low workflow-shaping impact.
- `Wrap`
  - Use when the capability is useful but needs Compass naming, artifact paths, guards, or BMAD/beads integration.
- `Rebuild`
  - Use when the plugin shapes workflow sequencing, approvals, artifact authority, tracking state, or parity-critical behavior.
- `Skip`
  - Use when the plugin adds little leverage, overlaps existing capability, creates lock-in, or fights Compass conventions.

## Plugin Review Table

| Plugin | Source | Primary group | OpenCode surface | BMAD fit | Architecture fit | Parity value | Strategic leverage | Security/trust | Maintenance | Lock-in | Commodity | Decision | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Example plugin | example/repo | Repo, file, and code utilities | Hook + custom tool | 2 | 3 | 2 | 2 | 3 | 4 | 4 | 5 | Adopt as-is | Commodity helper with limited workflow impact |

## Shortlist Rules

- Prefer 2-3 pilot candidates, not a broad first wave.
- Include at most one pilot per high-risk category unless there is a strong dependency between them.
- Favor one workflow-facing pilot, one tracking/lifecycle pilot, and one interoperability or utility pilot when possible.
- Do not pilot memory or oversight plugins first unless there is a specific approved problem they solve.

## Pilot Recommendation Table

| Plugin | Decision | Why now | Required wrapper/rebuild scope | Blocking risks | Follow-up issue |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD |

## Beads Issue Structure

- Parent portfolio issue:
- Category issues:
  - workflow and command surface
  - tracking and session lifecycle
  - context, memory, and oversight
  - repo, file, and code utilities
  - external integration and interoperability
- Consolidation issue:
- Implementation follow-ups:
  - one issue per approved pilot plugin
  - separate parity/test issue when behavior must match Claude/Codex surfaces

## References

- `docs/architecture/opencode-plugin-strategy.md`
- `docs/development/opencode/plugin-development.md`
- `src/opencode/plugins/README.md`
- `src/bmad/BMAD-workflow.md`
