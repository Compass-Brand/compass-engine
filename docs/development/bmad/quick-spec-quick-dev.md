# Quick Spec and Quick Dev Decision Guide

Last reviewed: 2026-04-15

Quick Spec and Quick Dev are fast-path workflows for changes that do not warrant the full 4-phase BMAD methodology. Both live in the Supporting And Alternate Lanes section of the Compass BMAD Workflow and can be invoked at any time without completing the required progression chain.

## Spec File Naming and Lifecycle

Both workflows produce per-spec markdown files (no singleton WIP file — that pattern was removed in upstream BMAD v6.3.0, PR #2214):

- **Location:** `{implementation_artifacts}/spec-{slug}.md`.
- **Slug derivation:** `tools/quick-dev-scan.js` exports `deriveSpecSlug(intent, options)`. When the intent references a tracking identifier (`story 3.2`, `#47`, `issue 47`, `gh-47`) the slug leads with it — `3-2-digest-delivery`, `gh-47-fix-auth`. Otherwise the title is slugified to lowercase kebab-case. On collision in `{implementation_artifacts}`, `-2`, `-3`, ... are appended.
- **Status lifecycle:** `draft → ready-for-dev → in-progress → in-review → done`.
  - `draft` — Quick Spec step 1 initializes this when the spec file is first created; Quick Spec step 3 keeps it while the full spec is generated.
  - `ready-for-dev` — Quick Spec step 4 flips to this on user approval; Quick Dev also writes this when a plan-code-review spec leaves the plan step.
  - `in-progress` — Quick Dev sets this when implementation begins.
  - `in-review` — Quick Dev sets this while the adversarial review loop runs.
  - `done` — Quick Dev writes this during spec-trace generation. Two mutually-exclusive write-back sites own this flip:
    - **Standard pipeline** — `src/bmad/modules/custom/bmm-skills/4-implementation/bmad-quick-dev/steps/step-07-spec-trace.md` runs after `step-06-resolve-findings.md` for ALL completed runs and writes `route: 'standard'` with `status: 'done'`.
    - **One-shot route** — `steps/step-oneshot.md` writes `route: 'one-shot'` with `status: 'done'` inline; it never reaches step-07.
    - **Never step-06.** `step-06-resolve-findings.md` resolves adversarial-review findings only — it MUST NOT touch the frontmatter. Letting step-06 flip the status would create two writers and break the single-source-of-truth contract that Feature 2's continuity scan relies on.

Parallel drafts are supported: multiple `spec-*.md` files can coexist in `{implementation_artifacts}/` with `status: draft`. Quick Spec step 1 scans for them and lets the user pick one to resume or archive.



## What Is Quick Spec?

Quick Spec (`/bmad-bmm-quick-spec`) is a lightweight intent-to-specification workflow. It produces a self-contained tech-spec artifact through conversational discovery and codebase investigation, but stops before writing any code.

**Skill:** `bmad-compass-quick-spec` (Compass custom skill)
**Source:** `src/bmad/modules/custom/compass-skills/4-implementation/bmad-compass-quick-spec/`

### How It Works

Quick Spec runs a 4-step guided process:

| Step | Name | What Happens |
| --- | --- | --- |
| 1 | Understand | Greet, capture intent, quick-scan the codebase, ask informed questions, initialize a draft spec file at `{implementation_artifacts}/spec-{slug}.md` |
| 2 | Investigate | Deep code investigation: map anchor files, patterns, tech stack, test conventions, and constraints |
| 3 | Generate | Build the implementation plan with ordered tasks (file + action), Given/When/Then acceptance criteria, dependencies, and testing strategy |
| 4 | Review | Present the complete spec for human review, iterate on edits, optionally run adversarial review, then finalize |

Each step has a checkpoint menu where the user can invoke Advanced Elicitation, Party Mode, or continue. The workflow halts at every checkpoint and waits for human input before proceeding.

### Output

A finalized tech-spec markdown file at `{implementation_artifacts}/spec-{slug}.md` with frontmatter tracking status and metadata. The spec must meet the Ready for Development standard:

- **Actionable** — every task has a clear file path and specific action
- **Logical** — tasks ordered by dependency
- **Testable** — all acceptance criteria use Given/When/Then
- **Complete** — no placeholders or TBDs
- **Self-Contained** — a fresh agent can implement without reading workflow history

The final menu recommends running implementation in a fresh context via `quick-dev {spec-file}`.

## What Is Quick Dev?

Quick Dev (`/bmad-bmm-quick-dev`) is a unified intent-in, code-out workflow. It handles clarification, planning, implementation, review, and presentation in a single session.

**Skill:** `bmad-quick-dev` (upstream BMM skill)
**Source:** `src/bmad/modules/native/bmm-skills/4-implementation/bmad-quick-dev/`

### How It Works

Quick Dev starts with routing, then follows one of two paths depending on complexity:

| Step | Name | What Happens |
| --- | --- | --- |
| 1 | Clarify and Route | Capture intent, check for existing specs, run multi-goal detection, then route to one-shot or plan-code-review |
| 2 | Plan | (Plan-code-review only) Investigate codebase, fill spec template, self-review against scope and quality standards, get human approval |
| 3 | Implement | Execute against the approved spec, mark tasks complete |
| 4 | Review | Construct diff, launch three context-free review subagents (blind hunter, edge case hunter, acceptance auditor), classify findings, loop back if needed |
| 5 | Present | Generate suggested review order with clickable links, commit, open spec in editor |

The one-shot path (step-oneshot) compresses steps 2 through 5 into a single pass: implement directly, run one adversarial review subagent, classify findings into patch/defer/reject, commit, and present.

### Routing Logic

Step 1 decides the path:

- **One-shot** — zero blast radius. No plausible path by which the change causes unintended consequences. Clear intent, no architectural decisions.
- **Plan-code-review** — everything else. When uncertain whether blast radius is truly zero, this path is chosen.

### Output

Working code committed locally, a spec file with status `done` and a Suggested Review Order section containing clickable links for human code review. The workflow offers to push or create a pull request at the end.

## How They Differ

| Dimension | Quick Spec | Quick Dev |
| --- | --- | --- |
| **Primary output** | Tech-spec document (no code) | Working code + spec artifact |
| **Ends at** | Finalized specification | Committed implementation |
| **Who implements?** | A separate agent in a fresh context | The same workflow session |
| **Human checkpoints** | 4 (after each step) | 2 for plan-code-review (intent approval, spec approval); 0 for one-shot |
| **Built-in review** | Optional adversarial review of the spec | Mandatory triple-reviewer review of the code diff |
| **Scope control** | Manual — user decides scope during discovery | Automated — multi-goal detection and token-count checks |
| **Spec template** | Custom Compass tech-spec template (overview, context, tasks, ACs, dependencies, testing, notes) | Upstream BMM spec template (frozen intent, boundaries, I/O matrix, code map, tasks, change log) |
| **Spec output** | `{implementation_artifacts}/spec-{slug}.md` (status `draft` → `ready-for-dev`) | `{implementation_artifacts}/spec-{slug}.md` (status advances through full lifecycle) |
| **Origin** | Compass custom skill | Upstream BMAD-METHOD |

## Why Compass Preserves a Separate Quick Spec Path

Upstream BMAD merged quick-spec functionality into Quick Dev starting in v6.2.0. The plan step inside Quick Dev now generates a spec before implementing. Compass preserves a separate Quick Spec skill for three reasons:

1. **Spec-only workflows are valuable.** Some changes need a specification reviewed by a human or a team before any code is written. Quick Dev always continues to implementation, which is not appropriate when the spec itself is the deliverable — for example, when handing off to a different developer, queuing work for a future sprint, or when the spec needs approval from a stakeholder who is not in the current session.

2. **Richer discovery process.** Quick Spec has a deeper investigation step with explicit technical mapping (anchor files, code patterns, test patterns, tech stack capture) and four human checkpoints. Quick Dev's plan step is deliberately compressed to reduce friction. When the problem space is unfamiliar, the extra discovery in Quick Spec produces better specifications.

3. **Context separation.** Quick Spec produces a spec that is designed to be consumed by a fresh agent with clean context. This avoids the context contamination that can occur when the same session that discovered the problem also implements the solution. The recommended handoff is `quick-dev {spec-file}` in a new session.

## Decision Criteria

Use this table to choose the right workflow for a given change:

| Criterion | Quick Dev (one-shot) | Quick Dev (plan-code-review) | Quick Spec | Full 4-Phase |
| --- | --- | --- | --- | --- |
| **Blast radius** | Zero | Low to moderate | Any | Any |
| **Scope** | Single trivial change | Single cohesive goal | Single feature or change | Multi-epic, multi-phase |
| **Spec needed as standalone artifact?** | No | Generated but secondary | Yes, primary output | Yes, multiple artifacts |
| **Code output in this session?** | Yes | Yes | No | Yes (in implementation phase) |
| **Planning artifacts exist?** | Not needed | Not needed | Not needed | Required (PRD, architecture, epics, stories) |
| **Team review of spec before coding?** | Not applicable | Spec approved in-session | Spec reviewed out-of-band | Formal gates |
| **Typical duration** | Minutes | 15-45 minutes | 15-30 minutes | Days to weeks |
| **Examples** | Fix a typo, rename a variable, add a log line | Add a validation rule, create a new API endpoint, refactor a module | Design a caching strategy, spec a migration plan, document a cross-service change | New product feature, system redesign, new service |

### Rules of Thumb

- **If you would not bother writing a spec** — use Quick Dev one-shot.
- **If you need a spec but will implement immediately** — use Quick Dev plan-code-review.
- **If the spec is the deliverable** (handoff, team review, future work) — use Quick Spec.
- **If the work spans multiple epics or requires PRD/architecture** — use the full 4-phase method.
- **When in doubt between Quick Dev and Quick Spec** — prefer Quick Dev. Its routing step will escalate to plan-code-review if needed, and the built-in review system catches mistakes.
- **When in doubt between Quick Dev and full 4-phase** — prefer Quick Dev. Its multi-goal detection will flag when scope is too large.

## Quick Dev Review Trail (v6.2.1)

Quick Dev v6.2.1 introduced a structured review trail that diagnoses failures at the correct layer rather than patching symptoms. The review system in step 4 launches three context-free subagents:

| Reviewer | Input | Purpose |
| --- | --- | --- |
| Blind hunter | Diff only (no spec, no project context) | Catch issues visible from code alone, free from anchoring bias |
| Edge case hunter | Diff + project read access | Find edge cases and integration risks using real codebase context |
| Acceptance auditor | Diff + spec + project read access | Verify acceptance criteria compliance and constraint adherence |

Subagents receive no conversation context. This is deliberate — it prevents the reviewers from being anchored by the same assumptions that guided implementation.

### Finding Classification

Findings are deduplicated and classified into five categories:

| Category | Meaning | Action |
| --- | --- | --- |
| `intent_gap` | The captured intent is incomplete; the spec cannot resolve this | Revert code, return to human for intent clarification, re-run steps 2-4 |
| `bad_spec` | The spec should have prevented this; root cause is in the non-frozen spec sections | Extract KEEP instructions, revert code, amend spec (respecting change log), re-derive code from step 3 |
| `patch` | Trivially fixable implementation issue | Auto-fix in place |
| `defer` | Pre-existing issue not caused by this change | Append to deferred-work file |
| `reject` | Noise | Drop silently |

The cascade is strict: if `intent_gap` or `bad_spec` findings exist, lower-severity findings are discarded because the code will be regenerated. The loop counter (`specLoopIteration`) prevents infinite cycles — after 5 iterations, the workflow halts and escalates to the human.

### Frozen Intent

The spec template separates human-owned intent (inside `<frozen-after-approval>`) from agent-generated planning. During `bad_spec` loopbacks, only the non-frozen sections are amended. This ensures the human's original intent is never silently altered by the review system.

## Scale-Adaptive Routing

Quick Dev detects complexity at two points and may escalate:

### 1. Blast Radius Assessment (Step 1)

During routing, the workflow evaluates whether the change has zero blast radius. The criteria for one-shot are strict: no plausible path by which the change causes unintended consequences, clear intent, and no architectural decisions. When uncertain, the workflow defaults to the plan-code-review path. This is a deliberate bias toward safety — a false positive (unnecessary planning) costs minutes, while a false negative (skipped planning on a risky change) costs hours of debugging.

### 2. Multi-Goal Detection (Step 1)

The workflow checks whether the intent contains multiple independently shippable goals. The test is specific: two or more top-level deliverables that could each be reviewed, tested, and merged as separate PRs without breaking each other. Cross-layer implementation details inside one user goal (like "add validation and display errors") do not trigger a split.

When multiple goals are detected, the user chooses:

- **Split** — pick the first goal, defer the rest to `deferred-work.md`
- **Keep** — accept the coupling risks and proceed with all goals

### 3. Token Budget Check (Step 2)

During planning, the workflow checks whether the generated spec exceeds 1600 tokens. Above this threshold, implementation agents risk context rot — degraded output quality as the spec consumes too much of the context window. The optimal range is 900-1600 tokens. The user can choose to split secondary goals or keep the full spec with acknowledged risk.

These checks do not replace the full 4-phase method for genuinely large work. They catch common cases where a developer underestimates scope and routes them toward either a smaller Quick Dev run or a recommendation to use the full methodology.

## Invocation

```text
# Quick Spec — produces a spec artifact, no code
/bmad-bmm-quick-spec

# Quick Dev — intent to code in one session
/bmad-bmm-quick-dev

# Quick Dev with an existing spec (from Quick Spec or elsewhere)
/bmad-bmm-quick-dev path/to/spec-file.md
```

## Related Documentation

- [BMAD Overview](./bmad-overview.md) — architecture and 4-phase methodology
- [BMAD Workflow](../../../src/bmad/BMAD-workflow.md) — canonical Compass workflow specification
- [Upstream Quick Dev Explanation](../../../BMAD-METHOD/docs/explanation/quick-dev.md) — upstream design rationale
