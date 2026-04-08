# When to Use BMAD: Decision Guide

Last reviewed: 2026-04-08

This guide answers the question: "I have work to do — which BMAD approach should I use?" It covers five approaches ranging from no BMAD at all through the full roadmap-driven methodology, explains how scale-adaptive intelligence levels map to those approaches, and provides criteria for choosing the right level.

## Decision Tree

Start at the top and follow the first branch that matches your situation.

```text
                        What kind of work is this?
                                  |
            +---------------------+---------------------+
            |                     |                     |
     Bug fix, typo,         New capability         New project,
     config tweak,          or change to           major redesign,
     dependency bump        existing system        multi-service work
            |                     |                     |
      (a) No BMAD          How large is it?        (e) Full BMAD
      Just fix it.                |
                     +------------+------------+
                     |            |            |
                Single file   Single feature  Multiple epics
                or trivial    or module       or unclear scope
                     |            |            |
              (b) Quick Dev  Does the spec    (d) Partial BMAD
              one-shot       need review      or (e) Full BMAD
                             before coding?
                             |            |
                            Yes          No
                             |            |
                      (c) Quick Spec  (b) Quick Dev
                      then Quick Dev  plan-code-review
```

### Five Approaches

| ID | Approach | When to Use | BMAD Artifacts | Typical Duration |
| --- | --- | --- | --- | --- |
| **(a)** | No BMAD | Bug fixes, typos, config tweaks, dependency bumps, trivial refactors | None | Minutes |
| **(b)** | Quick Dev | Small to moderate changes with clear intent; blast radius is zero (one-shot) or low-to-moderate (plan-code-review) | Spec generated inline, committed with code | Minutes to 1 hour |
| **(c)** | Quick Spec + Quick Dev | Changes that need a standalone specification reviewed before implementation — handoffs, team review, future-sprint work | Tech-spec artifact, then code in a separate session | 30 min to 2 hours |
| **(d)** | Partial BMAD | Moderate-to-large features where analysis/research can be skipped but planning and solutioning are needed | PRD, architecture, epics, stories (skip analysis phase) | Days |
| **(e)** | Full BMAD | New projects, major features, multi-service work, high-risk or compliance-sensitive changes | Full roadmap, research, PRD, architecture, epics, stories, gates | Days to weeks |

### Choosing Between Approaches: Quick Reference

| Criterion | (a) No BMAD | (b) Quick Dev | (c) Quick Spec | (d) Partial | (e) Full |
| --- | --- | --- | --- | --- | --- |
| Blast radius | Zero | Zero to moderate | Any | Moderate to high | Any |
| Files affected | 1-3 | 1-10 | Any | 10+ | Any |
| Architectural decisions needed | No | No | Maybe | Yes | Yes |
| Spec as standalone deliverable | No | No | Yes | Yes (PRD) | Yes (multiple) |
| Cross-service coordination | No | No | Possible | Likely | Yes |
| Team review before coding | No | In-session | Out-of-band | Formal gates | Formal gates |
| Planning artifacts required | None | None | None | PRD + architecture | All phases |

## Scale-Adaptive Intelligence Levels (0-4)

BMAD adjusts planning depth based on project scope through five scale levels. These levels control which artifacts are produced, which gates are enforced, and how much review rigor is applied.

### How Scale Level Is Determined

Scale level can be set in two ways:

1. **Manual selection.** The developer or team lead declares the level when initiating work. This is the most reliable method and is recommended when the team has a clear understanding of scope.

2. **Auto-detection heuristics.** BMAD workflows evaluate signals during routing to suggest a level. Key heuristics include:
   - **Blast radius assessment** — Quick Dev evaluates whether changes could cause unintended consequences. Zero blast radius routes to one-shot (Level 0-1); anything else routes to plan-code-review or higher.
   - **Multi-goal detection** — Quick Dev checks whether the intent contains multiple independently shippable goals. Multiple goals suggest Level 2+ or splitting.
   - **Token budget check** — specs exceeding 1600 tokens indicate scope that may warrant a higher level.
   - **File count and cross-module impact** — changes touching many files or crossing module boundaries suggest Level 2+.
   - **Presence of architectural decisions** — when the change requires choosing between approaches or establishing new patterns, Level 2+ is appropriate.

Auto-detection is advisory. The developer always has the final say.

### What Changes at Each Level

| Aspect | Level 0 | Level 1 | Level 2 | Level 3 | Level 4 |
| --- | --- | --- | --- | --- | --- |
| **Label** | Trivial | Small | Medium | Large | Enterprise |
| **BMAD approach** | (a) No BMAD | (b) Quick Dev | (b)/(c) Quick Dev or Quick Spec | (d) Partial or (e) Full | (e) Full BMAD |
| **Artifacts produced** | None (commit only) | Inline spec + code | Tech-spec or PRD + code | PRD, architecture, epics, stories | Full roadmap, research, PRD, architecture, epics, stories, gates |
| **Analysis phase** | Skip | Skip | Skip or lightweight | Skip if domain is well understood | Required |
| **Planning phase** | Skip | Skip | Lightweight (Quick Spec or condensed PRD) | Required (PRD + validation) | Required (PRD + UX design + validation) |
| **Solutioning phase** | Skip | Skip | Optional (architecture decision record only) | Required (architecture + epics) | Required (architecture + security + test design + epics) |
| **Implementation gates** | None | Quick Dev review system | Quick Dev review or story-level TDD | Sprint planning, story creation, dev story, code review | Full story loop with ATDD, test automation, traceability |
| **Review strictness** | Self-review or none | Quick Dev triple-reviewer (automated) | Quick Dev triple-reviewer or manual code review | Manual code review + test review | Manual code review + test review + security gates |
| **Documentation updates** | None | None | Optional | Required at phase boundaries | Required at every phase with validation |
| **Beads integration** | Optional | Optional | Recommended | Required (story issues) | Required (phase + story issues, closeout reconciliation) |

### Level Details

**Level 0 — Trivial.** Bug fixes with known root cause, typo corrections, config value changes, dependency version bumps. No BMAD workflow is needed. Fix the issue, run tests, commit. If you would not bother writing a spec, this is Level 0.

**Level 1 — Small.** Single-concern changes that are clear enough to implement without a plan: add a log line, rename a variable across a module, add a validation rule to an existing form. Quick Dev one-shot handles these. The routing step confirms zero blast radius before proceeding.

**Level 2 — Medium.** Single-feature changes that benefit from a plan: a new API endpoint, a refactored module, a caching layer for an existing service. Quick Dev plan-code-review is the default. Use Quick Spec instead when the spec needs out-of-band review or when the problem space is unfamiliar and deeper investigation is valuable.

**Level 3 — Large.** Multi-epic features, cross-service changes, work requiring architectural decisions that are expensive to reverse. Partial BMAD starts at planning (PRD) and proceeds through solutioning and implementation. Analysis is skipped when the team already understands the domain. Full BMAD is used when the domain is unfamiliar or research is needed.

**Level 4 — Enterprise.** New products, system redesigns, multi-team multi-service initiatives, compliance-sensitive work. Full roadmap-driven BMAD with all phases, all gates, and all documentation requirements. The roadmap layer ensures continuity across multiple phases and closeout cycles.

### Overriding or Adjusting Levels Mid-Project

Scale level is not locked at project start. Common adjustment scenarios:

- **Escalation.** Quick Dev's multi-goal detection flags that scope is larger than expected. The workflow recommends splitting goals or escalating to formal planning. Accept the recommendation and switch to a higher level.
- **De-escalation.** A Level 3 project turns out to have a simpler architecture than anticipated. After completing the PRD, the team decides stories are clear enough to skip formal epic creation and move directly to implementation with Quick Dev.
- **Mid-sprint discovery.** During a Level 2 Quick Dev run, the review system surfaces an `intent_gap` finding that reveals missing requirements. Pause implementation, create a PRD, and escalate to Level 3.
- **Phase-boundary adjustment.** After completing the analysis phase of a Level 4 project, the team determines that only one service is affected. Drop to Level 3 for planning and solutioning.

The key rule: escalate early when complexity is discovered, de-escalate only when you have evidence that the lower level is sufficient.

### Conditional Lanes and Scale Levels

Not all BMAD lanes activate at every level. The following lanes are conditional and activate based on project characteristics or explicit choice, not scale level alone:

| Lane | Activates When | Typical Levels |
| --- | --- | --- |
| **WDS (UX Design)** | Workflows, user journeys, UX complexity, or behavior design matter | 3-4 |
| **CYBERSEC (Security)** | Legacy auth, data flows, inherited attack surface, regulated work, or explicit choice | 2-4 |
| **TEA (Test Architecture)** | Formal test design, automation, or traceability are needed beyond basic TDD | 2-4 |
| **Storytelling** | Narrative framing is valuable for stakeholder communication | 3-4 |
| **Initiative Routing** | Execution scope is workspace or orchestration (polyrepo) | 4 |

Even at Level 4, these lanes remain conditional rather than mandatory. A Level 4 internal tool may skip UX design entirely; a Level 2 change touching authentication may activate the security lane.

## Criteria for Each Level

| Criterion | Level 0 | Level 1 | Level 2 | Level 3 | Level 4 |
| --- | --- | --- | --- | --- | --- |
| **Team size** | Solo | Solo | Solo or pair | Small team (2-5) | Cross-team |
| **Scope** | Single fix | Single concern | Single feature | Multi-epic feature | Multi-service system |
| **Files affected** | 1-3 | 1-5 | 5-15 | 15+ | Cross-repo |
| **Risk** | None | Minimal | Moderate (reversible) | High (expensive to reverse) | Critical (compliance, data, security) |
| **Compliance needs** | None | None | None | May apply | Required (audit trail, gates) |
| **Timeline** | Minutes | Minutes to 1 hour | Hours to 1 day | Days to 1 week | Weeks to months |
| **Domain familiarity** | Known | Known | Known or learnable quickly | May need research | Research required |
| **Architectural impact** | None | None | Local (single module) | Cross-module | Cross-service or new system |

## Real-Scenario Examples

### Level 0 — No BMAD

**Scenario:** A log message has a typo that confuses operators. Fix the string, run tests, commit.

**Scenario:** A dependency has a known CVE. Bump the version in the lock file, verify tests pass, commit.

### Level 1 — Quick Dev One-Shot

**Scenario:** An API endpoint returns a 500 when a required field is missing instead of a 400. The cause is a missing validation check. Run `/bmad-bmm-quick-dev`, describe the bug, let it fix and review.

**Scenario:** A developer wants to rename `UserService` to `AccountService` across a module. Run Quick Dev one-shot with the intent.

### Level 2 — Quick Dev Plan-Code-Review or Quick Spec

**Scenario:** The team needs a new `/health` endpoint that checks database connectivity, cache availability, and queue status. Run `/bmad-bmm-quick-dev`. The routing step detects non-zero blast radius (new endpoint, multiple integrations) and routes to plan-code-review.

**Scenario:** A developer needs to design a caching strategy for a frequently-queried report. The strategy needs review from the team lead before implementation. Run `/bmad-bmm-quick-spec` to produce the tech-spec, get approval, then run `/bmad-bmm-quick-dev path/to/spec.md` in a fresh session.

### Level 3 — Partial BMAD

**Scenario:** The authentication system needs to support OAuth2 in addition to the existing JWT flow. This touches the auth middleware, user model, session management, and frontend login flow. The team understands the domain well (no research needed), but needs a PRD to capture requirements, an architecture doc to record the integration approach, and stories to divide the work. Start at Phase 2 (Planning) with `/bmad-bmm-create-prd`.

### Level 4 — Full BMAD

**Scenario:** A company is building a new multi-tenant SaaS platform from scratch. This requires market research, domain analysis, product brief, PRD, UX design, architecture (including security review and threat modeling), epic planning, sprint execution, and release gating. Start at Phase 1 with the full initialization and analysis workflow.

**Scenario:** An existing monolith is being decomposed into microservices. The work spans multiple repositories, requires coordination across teams, involves data migration, and has compliance requirements. Full roadmap-driven BMAD with initiative routing at the workspace level.

## Transitioning Between Levels

The most common path is starting low and escalating when complexity surfaces. BMAD is designed so that work at a lower level is never wasted when you escalate — specs feed into PRDs, PRDs feed into architecture, and all prior context carries forward.

### Starting with Quick Dev, Escalating When Needed

1. **Begin with Quick Dev.** Describe your intent and let the routing step assess complexity.
2. **Watch for escalation signals:**
   - Multi-goal detection flags multiple independently shippable goals
   - Token budget exceeds 1600 tokens (spec is too large for reliable implementation)
   - Review system surfaces `intent_gap` or `bad_spec` findings repeatedly
   - You find yourself saying "but first we need to..." more than once
   - A change that seemed local turns out to require coordinating with another service or module
3. **When escalation is warranted:**
   - If Quick Dev suggests splitting, split and continue with Quick Dev for each piece
   - If the pieces still feel too large, pause and create a Quick Spec for the overall design
   - If the Quick Spec reveals multi-epic scope, escalate to partial or full BMAD
4. **Preserve work done at the lower level.** Quick Dev specs and Quick Spec tech-specs can feed into PRD creation. Nothing is wasted.

### Common Anti-Patterns

- **Over-engineering small changes.** Running full BMAD for a config tweak wastes time and produces artifacts nobody will reference. If the change is obvious and reversible, Level 0 or 1 is correct.
- **Under-planning large changes.** Jumping into Quick Dev for a multi-epic feature leads to scope creep, missed edge cases, and rework. If you cannot articulate the full scope in a single paragraph, you likely need Level 3+.
- **Refusing to escalate.** Pushing through with Quick Dev when the review system keeps surfacing `intent_gap` findings is a sign that requirements are unclear. Stop and escalate rather than looping.
- **Skipping project context in brownfield.** Starting BMAD work on an existing codebase without generating project context means the AI agent will not respect established patterns. Always run project context generation first.

### Escalation Decision Points

| Signal | From | To | Action |
| --- | --- | --- | --- |
| Multi-goal detection fires | Quick Dev | Quick Dev (split) or Quick Spec | Split goals or spec the whole picture first |
| Token budget exceeded | Quick Dev | Quick Spec or Partial BMAD | Produce standalone spec, assess if PRD is needed |
| Review finds `intent_gap` | Quick Dev | Quick Spec or Partial BMAD | Pause, clarify requirements, possibly create PRD |
| Architectural decisions needed | Quick Dev or Quick Spec | Partial BMAD | Create architecture doc before continuing implementation |
| Cross-service impact discovered | Any | Full BMAD | Initialize roadmap, phase sync, initiative routing |
| Compliance or audit needs identified | Any | Full BMAD | Ensure gate evidence and traceability |

## Brownfield vs Greenfield Considerations

### Brownfield (Existing Codebase)

Brownfield projects have existing patterns, conventions, and constraints that shape the approach.

**Key differences from greenfield:**

- **Project context is essential.** Run `/bmad-bmm-generate-project-context` before starting any significant work. This captures existing patterns, tech stack, and conventions so that AI agents respect the established codebase.
- **Analysis phase may be shorter or skippable.** Domain research and market research are less relevant when the product already exists. Technical research focuses on understanding the current system rather than evaluating alternatives.
- **Architecture must respect existing decisions.** The architecture workflow should scan the existing codebase and document how new work integrates with current patterns. Prevent reinventing existing solutions.
- **Quick Dev and Quick Spec are the common paths.** Most brownfield work is feature additions, bug fixes, or refactors — Levels 0-2. Reserve Levels 3-4 for major redesigns or new subsystems.
- **Reuse checks matter more.** Before implementing any story, check for existing components, services, queries, and patterns that can be reused. The reuse check step in the story loop is especially important in brownfield codebases.
- **Documentation may need catching up.** If documentation is outdated or missing, consider running docs initialization before starting BMAD work, regardless of scale level.

**Brownfield routing rules from the Compass BMAD Workflow:**

1. Initialize docs and planning from live repo reality.
2. Generate project context early.
3. Detailed analysis still runs for the active slice (but may be lighter).
4. The security lane gets extra weight for legacy auth, data flows, inherited attack surface, and regulated work.

### Greenfield (New Project)

Greenfield projects start from nothing, which means more upfront structure is needed.

**Key differences from brownfield:**

- **Full initialization is required.** Run docs initialization and planning initialization to establish the project structure before any development.
- **Analysis phase is valuable.** Without an existing codebase to learn from, research and brainstorming establish the foundation for good decisions.
- **Architecture decisions are first-time decisions.** There are no existing patterns to follow, so the architecture phase carries more weight.
- **Start at Level 3 or 4.** New projects almost always warrant at least partial BMAD. Even a small new service benefits from a PRD and architecture doc to establish the initial patterns that all future work will follow.
- **Generate seed context after high-level framing.** Unlike brownfield (where context comes from scanning the codebase), greenfield context is generated after initial planning and regenerated as the codebase takes shape.

**Greenfield routing rules from the Compass BMAD Workflow:**

1. Initialize structure first.
2. Complete high-level framing.
3. Generate a seed project context after framing.
4. Regenerate richer context as the codebase grows.

### Summary: Brownfield vs Greenfield Starting Points

| Starting Point | Brownfield | Greenfield |
| --- | --- | --- |
| **First step** | Generate project context | Initialize docs and planning structure |
| **Typical starting level** | 0-2 (most work is incremental) | 3-4 (foundation must be established) |
| **Analysis phase** | Often skippable (domain is known) | Usually required (domain is new) |
| **Architecture phase** | Focused on integration with existing patterns | Focused on establishing initial patterns |
| **Risk emphasis** | Regression, compatibility, inherited tech debt | Design mistakes that are expensive to reverse later |

## Related Documentation

- [Quick Spec and Quick Dev Decision Guide](./quick-spec-quick-dev.md) — detailed fast-path workflow documentation
- [BMAD Overview](./bmad-overview.md) — architecture, modules, and 4-phase methodology
- [BMAD Workflow](../../../src/bmad/BMAD-workflow.md) — canonical Compass workflow specification
- [Project Context](./project-context.md) — generating and maintaining project context
