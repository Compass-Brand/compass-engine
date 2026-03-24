# OpenCode Plugin Portfolio Triage

Status: draft
Owner:
Last Updated: 2026-03-24
Phase ID:
Parent Issue: `bmad-engine-pkr`

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
| Additive planning and review overlays | `plannotator`, `open-plan-annotator`, `octto` | Good candidates for wrapping when they annotate, review, or guide planning without becoming the source of truth |
| Parallel planning systems | `opencode-planning-toolkit`, `vibe-kanban` | Evaluate for visualization or interoperability value, but be explicit about task and artifact authority boundaries |
| Multi-agent orchestration | `opencode-workspace`, `oh-my-openagent`, `subtask2`, `opencode-background-agents`, `OpenAgentsControl`, `claude-code-teams-mcp`, `pocket-universe`, `swarm-tools`, `hcom`, `agent-of-empires`, `opencode-pilot` | Treat as reference or rebuild candidates, not direct dependencies |
| Context and memory | `opencode-agent-identity`, `opencode-agent-memory`, `opencode-dynamic-context-pruning`, `opencode-handoff`, `opencode-mem`, `opencode-sessions`, `agentic` | Narrow the problem first, then pilot one focused capability |
| Environment and workspace utilities | `opencode-devcontainers`, `opencode-worktree`, `opentmux`, `agent-of-empires`, `ocx` | Best source for low-risk pilot candidates |
| Authentication adapters | `opencode-antigravity-auth`, `opencode-gemini-auth` | High lock-in and credential risk; likely skip |

## OpenCode Plugin Development Model

OpenCode's official plugin model is broad enough to support both lightweight utilities and workflow overlays.

| Capability | Official behavior | Relevance to Compass |
| --- | --- | --- |
| Loading | Plugins can be loaded from project-local `.opencode/plugins/`, global plugin directories, or npm packages declared in `opencode.json` | Supports local prototyping first, then packaging once a plugin contract stabilizes |
| Implementation shape | A plugin is a JavaScript or TypeScript module that exports one or more async plugin functions returning hook objects | Fits the repo strategy of keeping plugin implementation in `src/opencode/plugins/` |
| Runtime context | Plugin functions receive `project`, `directory`, `worktree`, `client`, and Bun's `$` shell helper | Gives enough context to align behavior to repo roots, worktrees, and Compass control files |
| Event hooks | Official docs expose hooks for command, file, installation, LSP, message, permission, server, session, todo, shell, tool, and TUI events | This is why review overlays, notifications, and lifecycle helpers can be additive rather than replacements |
| Custom tools | Plugins can register custom tools using `@opencode-ai/plugin` and Zod-style schemas | Strong fit for `provider-bmad`, `provider-tracking`, and interop wrappers |
| Skills integration | OpenCode also supports on-demand `SKILL.md` loading through the native `skill` tool | Important for plugins like planning-toolkit that add guidance, not just commands |
| Compaction hooks | Plugins can inject or replace compaction context using `experimental.session.compacting` | Relevant to handoff, memory, and state-carry-forward work, but should stay tightly scoped |
| Dependencies | Local plugins can depend on npm packages via `.opencode/package.json`; OpenCode installs them with Bun | Useful for plugin iteration, but increases maintenance and supply-chain surface |

Implication:

- An overlay is not automatically a competing system just because it adds UI or tools.
- The real boundary is whether it becomes authoritative for tasks, plans, approvals, or artifact storage.
- Additive overlays that annotate or visualize BMAD and beads state can fit well behind wrappers.
- Plugins that create parallel issue boards, canonical plan stores, or orchestration authority should still be treated cautiously.

## Initial Inventory And Provisional Classification

This is the first-pass normalization table. Numeric scoring comes next after bucket-level comparison.

| Candidate | Source | Primary group | Overlap cluster | Preliminary decision | Notes |
| --- | --- | --- | --- | --- | --- |
| `opencode-workspace` | `kdcokenny/opencode-workspace` | BMAD workflow and command surface | Multi-agent orchestration | Skip | Bundled orchestration harness is too workflow-defining to adopt directly; use as reference only |
| `plannotator` | `backnotprop/plannotator` | BMAD workflow and command surface | Additive planning and review overlays | Wrap | After README review, this is better framed as an approval and annotation overlay than as a replacement planning system |
| `opencode-notifier` | `mohak34/opencode-notifier` | Tracking and session lifecycle | Notifications | Adopt as-is | Commodity desktop notifications are low-risk if we want a local notifier |
| `oh-my-openagent` | `code-yeongyu/oh-my-openagent` | BMAD workflow and command surface | Multi-agent orchestration | Skip | Harness-level replacement rather than a narrow Compass plugin |
| `opencode-md-table-formatter` | `franlol/opencode-md-table-formatter` | Repo, file, and code utilities | None | Adopt as-is | Narrow Markdown utility with low workflow impact |
| `opencode-devcontainers` | `athal7/opencode-devcontainers` | Repo, file, and code utilities | Environment and workspace utilities | Wrap | Useful environment setup primitive, but needs Compass guardrails around repo targeting and lifecycle |
| `opencode-antigravity-auth` | `NoeFabris/opencode-antigravity-auth` | External integration and interoperability | Authentication adapters | Skip | High credential and vendor-coupling risk for limited Compass value |
| `opencode-gemini-auth` | `jenslys/opencode-gemini-auth` | External integration and interoperability | Authentication adapters | Skip | Similar lock-in profile to Antigravity auth without clear Compass workflow leverage |
| `type-inject` | `nick-vi/type-inject` | Repo, file, and code utilities | None | Wrap | Strong utility candidate, but read/write interception should be introduced behind Compass controls |
| `subtask2` | `spoons-and-mirrors/subtask2` | BMAD workflow and command surface | Multi-agent orchestration | Skip | Stronger command handling is interesting, but command-routing authority should stay in Compass |
| `octto` | `vtemian/octto` | BMAD workflow and command surface | Additive planning and review overlays | Wrap | Interactive branching questions and browser review are additive, but its output path and agent prompts should be remapped to Compass artifacts |
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
| `open-plan-annotator` | `ndom91/open-plan-annotator` | BMAD workflow and command surface | Additive planning and review overlays | Wrap | README shows it intercepts plan flow and returns structured feedback; that is additive, but it overlaps with plannotator and should not create a separate approval authority |
| `opentmux` | `AnganSamadder/opentmux` | Repo, file, and code utilities | Environment and workspace utilities | Wrap | tmux coordination may help power users, but should stay optional and bounded |
| `opencode-canvas` | `mailshieldai/opencode-canvas` | External integration and interoperability | Additive planning and review overlays | Skip | Interactive canvases are additive, but they are not yet close to the current BMAD plugin-core priorities |
| `opencode-mem` | `tickernelz/opencode-mem` | Context, memory, and oversight | Context and memory | Skip | Persistent vector-memory overlaps broader memory candidates and should not be an early pilot |
| `opencode-notify` | `kdcokenny/opencode-notify` | Tracking and session lifecycle | Notifications | Adopt as-is | Another strong notifier option; choose one notification path rather than several |
| `opencode-ntfy.sh` | `lannuttia/opencode-ntfy.sh` | External integration and interoperability | Notifications | Skip | Only needed if self-hosted `ntfy.sh` is a hard requirement; otherwise duplicates notifier coverage |
| `opencode-planning-toolkit` | `IgorWarzocha/opencode-planning-toolkit` | BMAD workflow and command surface | Parallel planning systems | Wrap | The plugin uses OpenCode-native tools plus a bundled skill, so it is additive in shape, but its `docs/specs` and `docs/plans` storage model conflicts with raw Compass storage and would need remapping |
| `opencode-sessions` | `malhashemi/opencode-sessions` | Context, memory, and oversight | Context and memory | Skip | Session management overlaps orchestration and memory candidates without a narrowed problem statement |
| `opencode-snippets` | `JosXa/opencode-snippets` | Repo, file, and code utilities | None | Adopt as-is | Narrow productivity utility with low risk and little coupling to workflow authority |
| `opencode-pilot` | `athal7/opencode-pilot` | BMAD workflow and command surface | Multi-agent orchestration | Skip | Broad automation layer spans orchestration, UI, and notifications; too much surface area for a direct dependency |
| `pocket-universe` | `spoons-and-mirrors/pocket-universe` | BMAD workflow and command surface | Multi-agent orchestration | Rebuild | Async closed-loop coordination is strategically interesting, but core orchestration should stay owned |
| `swarm-tools` | `joelhooks/swarm-tools` | BMAD workflow and command surface | Multi-agent orchestration | Skip | Multi-agent coordination plus issue tracking overlaps too much with planned Compass providers and `bd` |
| `agent-of-empires` | `njbrake/agent-of-empires` | Repo, file, and code utilities | Environment and workspace utilities | Wrap | tmux and worktree session management is useful, but should stay modular and optional |
| `cupcake` | `eqtylab/cupcake` | External integration and interoperability | None | Wrap | Policy enforcement is promising, but guardrail policy is too important to adopt without a Compass boundary |
| `hcom` | `aannoo/hcom` | External integration and interoperability | Multi-agent orchestration | Rebuild | Cross-terminal agent messaging is core coordination infrastructure, not a commodity add-on |
| `vibe-kanban` | `BloopAI/vibe-kanban` | BMAD workflow and command surface | Parallel planning systems | Skip | It can add visualization value, but the product includes its own kanban issue layer and workspace lifecycle, so raw adoption would still split task authority from `bd` |

## Scored Implementable Candidate Comparison

This scorecard covers every candidate still considered implementable after the provisional pass: all `Adopt as-is`, `Wrap`, and `Rebuild` candidates. Scores are comparative, not absolute. Higher totals indicate stronger overall fit, but pilot order also depends on implementation shape.

Scoring legend:

- `B` = BMAD fit
- `A` = architecture fit
- `P` = parity value
- `L` = strategic leverage
- `T` = security and trust
- `M` = maintenance burden score, where higher means easier to maintain
- `K` = lock-in score, where higher means lower lock-in
- `C` = commodity factor

| Candidate | Posture | B | A | P | L | T | M | K | C | Total | Recommended lane |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `opencode-beads` | Wrap | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 3 | 34 | Pilot now |
| `opencode-worktree` | Adopt as-is | 3 | 4 | 3 | 4 | 5 | 4 | 5 | 5 | 33 | Pilot now |
| `type-inject` | Wrap | 3 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 30 | Pilot now |
| `opencode-handoff` | Wrap | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 2 | 30 | Follow-on wrap |
| `plannotator` | Wrap | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 2 | 29 | Follow-on wrap |
| `opencode-agent-skills` | Wrap | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 2 | 29 | Follow-on wrap |
| `opencode-notify` | Adopt as-is | 2 | 3 | 2 | 3 | 5 | 4 | 5 | 5 | 29 | Optional utility |
| `opencode-devcontainers` | Wrap | 3 | 4 | 3 | 4 | 4 | 3 | 4 | 3 | 28 | Follow-on wrap |
| `open-plan-annotator` | Wrap | 4 | 4 | 4 | 3 | 4 | 3 | 4 | 2 | 28 | Follow-on wrap |
| `opencode-notifier` | Adopt as-is | 2 | 3 | 2 | 3 | 4 | 4 | 5 | 5 | 28 | Optional utility |
| `opencode-background-agents` | Rebuild | 4 | 5 | 5 | 5 | 3 | 2 | 3 | 1 | 28 | Strategic rebuild |
| `octto` | Wrap | 4 | 3 | 3 | 4 | 4 | 3 | 4 | 2 | 27 | Follow-on wrap |
| `opencode-dynamic-context-pruning` | Wrap | 3 | 4 | 3 | 4 | 4 | 3 | 4 | 2 | 27 | Follow-on wrap |
| `cupcake` | Wrap | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 1 | 27 | Follow-on wrap |
| `OpenAgentsControl` | Rebuild | 4 | 5 | 4 | 5 | 3 | 2 | 3 | 1 | 27 | Strategic rebuild |
| `opencode-snippets` | Adopt as-is | 1 | 2 | 1 | 2 | 5 | 5 | 5 | 5 | 26 | Optional utility |
| `opencode-md-table-formatter` | Adopt as-is | 1 | 2 | 1 | 2 | 5 | 5 | 5 | 5 | 26 | Optional utility |
| `pocket-universe` | Rebuild | 4 | 5 | 4 | 4 | 3 | 2 | 3 | 1 | 26 | Strategic rebuild |
| `opencode-planning-toolkit` | Wrap | 3 | 4 | 3 | 4 | 4 | 3 | 3 | 1 | 25 | Follow-on wrap |
| `opencode-agent-identity` | Wrap | 3 | 4 | 3 | 3 | 4 | 3 | 4 | 1 | 25 | Exploratory wrap |
| `hcom` | Rebuild | 3 | 5 | 4 | 4 | 3 | 2 | 3 | 1 | 25 | Strategic rebuild |
| `agent-of-empires` | Wrap | 2 | 3 | 3 | 3 | 3 | 2 | 4 | 3 | 23 | Exploratory wrap |
| `opentmux` | Wrap | 2 | 3 | 2 | 3 | 3 | 3 | 4 | 3 | 23 | Exploratory wrap |
| `opencode-agent-memory` | Rebuild | 3 | 4 | 3 | 4 | 3 | 2 | 2 | 1 | 22 | Strategic rebuild |

Interpretation:

- `Pilot now` means high fit and bounded enough scope to start without first inventing a new control plane.
- `Follow-on wrap` means promising, but the wrapper contract should be designed after the first pilots.
- `Strategic rebuild` means important capability area, but direct adoption would hand off too much workflow authority.
- `Optional utility` means low-risk convenience rather than strategic differentiation.
- `Exploratory wrap` means possible value, but not enough near-term leverage to outrank the higher-fit set.

## Revised Pilot Set

The strongest first-wave candidates from this initial pass are:

| Candidate | Why it stands out | Current posture |
| --- | --- | --- |
| `opencode-beads` | Direct fit with the existing issue-tracking contract | Wrap |
| `opencode-worktree` | Commodity utility with clear engineering leverage and low workflow coupling | Adopt as-is |
| `type-inject` | Valuable code-intelligence utility if introduced behind Compass controls | Wrap |
| `opencode-handoff` | Strong contextual fit for session continuity without immediately introducing a full memory substrate | Wrap |
| `opencode-devcontainers` | Useful workspace utility, but more operationally invasive than `opencode-worktree` | Wrap |
| `opencode-notify` or `opencode-notifier` | Low-risk notification pilot if local eventing becomes important | Adopt as-is |

## Research Refinement Notes

- Not all planning or review plugins are substitutes for BMAD or beads.
- `plannotator` and `open-plan-annotator` are better treated as approval and feedback overlays.
- `octto` is better treated as a brainstorming and elicitation overlay.
- `opencode-planning-toolkit` and `vibe-kanban` are more likely to create parallel planning state unless explicitly wrapped around Compass artifacts.
- Official OpenCode plugin hooks make additive overlays technically feasible because plugins can observe events, add tools, and shape plan/review flows without owning the canonical state.
- Official OpenCode skills support also matters because some planning plugins extend behavior by loading reusable instructions rather than only by adding commands or hooks.
- The highest-value immediate pool is not identical to the highest-scoring strategic pool; rebuild-heavy orchestration candidates score for importance, but they are not first-wave pilots.

## Pilot Selection Rules

- Limit the first implementation wave to 2-3 plugins.
- Prefer one workflow-facing candidate only if the wrapper/rebuild boundary is already clear.
- Prefer one tracking/lifecycle candidate only if its beads contract is explicit.
- Prefer at least one low-risk commodity or interoperability pilot to validate the integration path quickly.

## Beads Issue Structure

- Setup issue: `bmad-engine-ygy` (closed after framework creation)
- Inventory issue: `bmad-engine-ess`
- Refinement issue: `bmad-engine-pkr`
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
- `bmad-engine-pkr` captures the refinement pass using official OpenCode plugin documentation plus deeper overlay research.
- Pilot implementation issues should be created only after the shortlist is approved.

## Recommended Next Step

Use `bmad-engine-8zr` to turn the scored comparison into a shortlist of 2-3 pilot plugins, then create one implementation issue per approved pilot with an explicit adopt, wrap, or rebuild scope.

## Sources

- `docs/architecture/opencode-plugin-strategy.md`
- `docs/development/opencode/plugin-development.md`
- `src/opencode/plugins/README.md`
- `src/bmad/BMAD-workflow.md`
- OpenCode plugin docs: `https://opencode.ai/docs/plugins/`
- OpenCode agent docs: `https://opencode.ai/docs/agents/`
- OpenCode skills docs: `https://opencode.ai/docs/skills`
- `https://github.com/backnotprop/plannotator`
- `https://github.com/ndom91/open-plan-annotator`
- `https://github.com/IgorWarzocha/opencode-planning-toolkit`
- `https://github.com/BloopAI/vibe-kanban`
- `https://github.com/vtemian/octto`

## Links Forward

- OpenCode plugin implementation work in `src/opencode/plugins/`
- OpenCode wrappers in `src/opencode/commands/` and `src/opencode/agents/`
- Follow-up pilot issues created from `bmad-engine-8zr`
