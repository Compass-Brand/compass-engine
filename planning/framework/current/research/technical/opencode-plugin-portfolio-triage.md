# OpenCode Plugin Portfolio Triage

Status: draft
Owner:
Last Updated: 2026-03-24
Phase ID:
Parent Issue: `bmad-engine-ess`

## Objective

- Sort 40 candidate OpenCode plugins into a bounded review structure instead of a flat list.
- Decide for each plugin whether Compass should adopt it as-is, wrap it, rebuild it in-house, or skip it.
- Produce a shortlist of 2-3 pilot candidates that fit the Compass OpenCode plugin strategy.

## Scope

- Slice focus: OpenCode plugin portfolio triage for Compass workflow fit
- Systems touched: `src/opencode/`, `src/bmad/`, `planning/`, `bd`
- External dependencies: candidate third-party OpenCode plugins under review
- Candidate count: 40 provided links
- Source window: user-provided GitHub and DEV links on 2026-03-24

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

## Overlap Clusters

These clusters should be compared side by side rather than evaluated in isolation.

| Cluster | Candidates | Default posture |
| --- | --- | --- |
| Notifications | `opencode-notifier`, `opencode-notify`, `opencode-ntfy.sh` | Pick one low-friction path, do not ship multiple notifiers |
| Planning and review surfaces | `plannotator`, `open-plan-annotator`, `opencode-planning-toolkit`, `vibe-kanban`, `octto` | Avoid duplicating `bd` and BMAD planning state |
| Multi-agent orchestration | `opencode-workspace`, `oh-my-openagent`, `subtask2`, `opencode-background-agents`, `OpenAgentsControl`, `claude-code-teams-mcp`, `pocket-universe`, `swarm-tools`, `hcom`, `agent-of-empires`, `opencode-pilot` | Treat as reference or rebuild candidates, not direct dependencies |
| Context and memory | `opencode-agent-identity`, `opencode-agent-memory`, `opencode-dynamic-context-pruning`, `opencode-handoff`, `opencode-mem`, `opencode-sessions`, `agentic` | Narrow the problem first, then pilot one focused capability |
| Environment and workspace utilities | `opencode-devcontainers`, `opencode-worktree`, `opentmux`, `agent-of-empires`, `ocx` | Best source for low-risk pilot candidates |
| Authentication adapters | `opencode-antigravity-auth`, `opencode-gemini-auth` | High lock-in and credential risk; likely skip |

## Initial Inventory And Provisional Classification

This is the first-pass normalization table. Numeric scoring comes next after bucket-level comparison.

| Candidate | Source | Primary group | Overlap cluster | Preliminary decision | Notes |
| --- | --- | --- | --- | --- | --- |
| `opencode-workspace` | `kdcokenny/opencode-workspace` | BMAD workflow and command surface | Multi-agent orchestration | Skip | Bundled orchestration harness is too workflow-defining to adopt directly; use as reference only |
| `plannotator` | `backnotprop/plannotator` | BMAD workflow and command surface | Planning and review surfaces | Wrap | Visual plan and diff review could support approvals, but should not become the source of truth |
| `opencode-notifier` | `mohak34/opencode-notifier` | Tracking and session lifecycle | Notifications | Adopt as-is | Commodity desktop notifications are low-risk if we want a local notifier |
| `oh-my-openagent` | `code-yeongyu/oh-my-openagent` | BMAD workflow and command surface | Multi-agent orchestration | Skip | Harness-level replacement rather than a narrow Compass plugin |
| `opencode-md-table-formatter` | `franlol/opencode-md-table-formatter` | Repo, file, and code utilities | None | Adopt as-is | Narrow Markdown utility with low workflow impact |
| `opencode-devcontainers` | `athal7/opencode-devcontainers` | Repo, file, and code utilities | Environment and workspace utilities | Wrap | Useful environment setup primitive, but needs Compass guardrails around repo targeting and lifecycle |
| `opencode-antigravity-auth` | `NoeFabris/opencode-antigravity-auth` | External integration and interoperability | Authentication adapters | Skip | High credential and vendor-coupling risk for limited Compass value |
| `opencode-gemini-auth` | `jenslys/opencode-gemini-auth` | External integration and interoperability | Authentication adapters | Skip | Similar lock-in profile to Antigravity auth without clear Compass workflow leverage |
| `type-inject` | `nick-vi/type-inject` | Repo, file, and code utilities | None | Wrap | Strong utility candidate, but read/write interception should be introduced behind Compass controls |
| `subtask2` | `spoons-and-mirrors/subtask2` | BMAD workflow and command surface | Multi-agent orchestration | Skip | Stronger command handling is interesting, but command-routing authority should stay in Compass |
| `octto` | `vtemian/octto` | BMAD workflow and command surface | Planning and review surfaces | Wrap | Interactive brainstorming UI may fit analysis lanes, but only as a wrapper around BMAD artifacts |
| `ocx` | `kdcokenny/ocx` | Repo, file, and code utilities | Environment and workspace utilities | Skip | Portable extension/profile management is useful locally, but not a core Compass dependency |
| `opencode-background-agents` | `kdcokenny/opencode-background-agents` | BMAD workflow and command surface | Multi-agent orchestration | Rebuild | Async delegation with persistence is strategically relevant, but too core to adopt raw |
| `agentic` | `Cluster444/agentic` | Context, memory, and oversight | Context and memory | Skip | Context engineering is relevant, but the problem should be narrowed before adding another substrate |
| `OpenAgentsControl` | `darrenhinde/OpenAgentsControl` | BMAD workflow and command surface | Multi-agent orchestration | Rebuild | Plan-first, approval-based execution aligns conceptually, but workflow control belongs in Compass |
| `opencode-worktree` | `kdcokenny/opencode-worktree` | Repo, file, and code utilities | Environment and workspace utilities | Adopt as-is | Strong commodity candidate with clear utility and limited BMAD coupling |
| `claude-code-teams-mcp` | `cs50victor/claude-code-teams-mcp` | External integration and interoperability | Multi-agent orchestration | Skip | Good reference for interoperability, but direct dependency would overfit to Claude team semantics |
| `Building Agent Teams in OpenCode` | `dev.to/uenyioha/...` | External integration and interoperability | Multi-agent orchestration | Skip | Supporting architecture reference, not a plugin candidate |
| `opencode-agent-identity` | `gotgenes/opencode-agent-identity` | Context, memory, and oversight | Context and memory | Wrap | Identity continuity can help multi-agent work, but should be bounded and explicit |
| `opencode-agent-memory` | `joshuadavidthomas/opencode-agent-memory` | Context, memory, and oversight | Context and memory | Rebuild | Memory is strategically relevant but too behavior-shaping to depend on directly |
| `opencode-agent-skills` | `joshuadavidthomas/opencode-agent-skills` | BMAD workflow and command surface | Multi-agent orchestration | Wrap | Skills are compatible with Compass surfaces, but should be integrated through provider contracts |
| `opencode-beads` | `joshuadavidthomas/opencode-beads` | Tracking and session lifecycle | None | Wrap | High-fit candidate because beads is already the project system of record |
| `opencode-dynamic-context-pruning` | `Opencode-DCP/opencode-dynamic-context-pruning` | Context, memory, and oversight | Context and memory | Wrap | Useful token-management idea, but context control needs explicit Compass policy |
| `opencode-handoff` | `joshuadavidthomas/opencode-handoff` | Context, memory, and oversight | Context and memory | Wrap | Session handoff is valuable if constrained to Compass artifact and issue context |
| `open-plan-annotator` | `ndom91/open-plan-annotator` | BMAD workflow and command surface | Planning and review surfaces | Skip | Overlaps heavily with plannotator and should not outrank `bd` plus BMAD artifacts |
| `opentmux` | `AnganSamadder/opentmux` | Repo, file, and code utilities | Environment and workspace utilities | Wrap | tmux coordination may help power users, but should stay optional and bounded |
| `opencode-canvas` | `mailshieldai/opencode-canvas` | External integration and interoperability | Planning and review surfaces | Skip | Interactive canvases are interesting but outside the current plugin-core priorities |
| `opencode-mem` | `tickernelz/opencode-mem` | Context, memory, and oversight | Context and memory | Skip | Persistent vector-memory overlaps broader memory candidates and should not be an early pilot |
| `opencode-notify` | `kdcokenny/opencode-notify` | Tracking and session lifecycle | Notifications | Adopt as-is | Another strong notifier option; choose one notification path rather than several |
| `opencode-ntfy.sh` | `lannuttia/opencode-ntfy.sh` | External integration and interoperability | Notifications | Skip | Only needed if self-hosted `ntfy.sh` is a hard requirement; otherwise duplicates notifier coverage |
| `opencode-planning-toolkit` | `IgorWarzocha/opencode-planning-toolkit` | BMAD workflow and command surface | Planning and review surfaces | Skip | Repo-wide todo sharing conflicts with the repo rule that `bd` is the task system of record |
| `opencode-sessions` | `malhashemi/opencode-sessions` | Context, memory, and oversight | Context and memory | Skip | Session management overlaps orchestration and memory candidates without a narrowed problem statement |
| `opencode-snippets` | `JosXa/opencode-snippets` | Repo, file, and code utilities | None | Adopt as-is | Narrow productivity utility with low risk and little coupling to workflow authority |
| `opencode-pilot` | `athal7/opencode-pilot` | BMAD workflow and command surface | Multi-agent orchestration | Skip | Broad automation layer spans orchestration, UI, and notifications; too much surface area for a direct dependency |
| `pocket-universe` | `spoons-and-mirrors/pocket-universe` | BMAD workflow and command surface | Multi-agent orchestration | Rebuild | Async closed-loop coordination is strategically interesting, but core orchestration should stay owned |
| `swarm-tools` | `joelhooks/swarm-tools` | BMAD workflow and command surface | Multi-agent orchestration | Skip | Multi-agent coordination plus issue tracking overlaps too much with planned Compass providers and `bd` |
| `agent-of-empires` | `njbrake/agent-of-empires` | Repo, file, and code utilities | Environment and workspace utilities | Wrap | tmux and worktree session management is useful, but should stay modular and optional |
| `cupcake` | `eqtylab/cupcake` | External integration and interoperability | None | Wrap | Policy enforcement is promising, but guardrail policy is too important to adopt without a Compass boundary |
| `hcom` | `aannoo/hcom` | External integration and interoperability | Multi-agent orchestration | Rebuild | Cross-terminal agent messaging is core coordination infrastructure, not a commodity add-on |
| `vibe-kanban` | `BloopAI/vibe-kanban` | BMAD workflow and command surface | Planning and review surfaces | Skip | Kanban overlay overlaps with `bd` and risks splitting task authority |

## Early Pilot Bias

The strongest first-wave candidates from this initial pass are:

| Candidate | Why it stands out | Current posture |
| --- | --- | --- |
| `opencode-beads` | Direct fit with the existing issue-tracking contract | Wrap |
| `opencode-worktree` | Commodity utility with clear engineering leverage and low workflow coupling | Adopt as-is |
| `type-inject` | Valuable code-intelligence utility if introduced behind Compass controls | Wrap |
| `opencode-devcontainers` | Useful workspace utility, but more operationally invasive than `opencode-worktree` | Wrap |
| `opencode-notify` or `opencode-notifier` | Low-risk notification pilot if local eventing becomes important | Adopt as-is |

## Pilot Selection Rules

- Limit the first implementation wave to 2-3 plugins.
- Prefer one workflow-facing candidate only if the wrapper/rebuild boundary is already clear.
- Prefer one tracking/lifecycle candidate only if its beads contract is explicit.
- Prefer at least one low-risk commodity or interoperability pilot to validate the integration path quickly.

## Beads Issue Structure

- Setup issue: `bmad-engine-ygy` (closed after framework creation)
- Inventory issue: `bmad-engine-ess`
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
- `bmad-engine-ygy` captured framework setup only and is now closed.
- `bmad-engine-ess` captures the initial inventory and provisional bucket assignments.
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
