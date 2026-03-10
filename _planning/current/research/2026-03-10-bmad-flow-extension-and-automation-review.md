# BMAD Flow Extension and Automation Review

Date: 2026-03-10

## Scope

This note captures two related reviews:

1. Candidate BMAD flow extensions from adjacent repos:
   - `BMAD-CYBERSEC`
   - `bmad-method-wds-expansion`
   - `bmad-module-creative-intelligence-suite`
   - `pov-oversight-agent`
   - `ai-memory`
2. Automation and workflow-improvement research in `reference/BMAD/research`

The current Compass baseline remains the primary source of truth:
- `reference/BMAD/BMAD-workflow.md`
- `reference/BMAD/modules/custom/bmm/module-help.csv`

## Executive View

Compass should keep its current BMAD spine and add targeted extension lanes around it. Nothing reviewed here should be imported wholesale.

The strongest path is:

1. Add targeted early-phase strategy workflows from CIS.
2. Add a richer UX/spec lane from WDS.
3. Add a conditional security lane from CYBERSEC.
4. Keep POV oversight and AI memory as optional sidecars.
5. Add automation as a thin orchestration layer around BMAD, not as a second BMAD system.

## Current Baseline Assessment

The existing Compass BMAD flow already has the right delivery backbone:

- analysis
- planning
- solutioning
- implementation
- release gate
- TEA insertion and implementation support surfaces

That means the highest-value work is not replacing the flow. It is improving rigor at specific weak points:

- early discovery and strategic framing
- UX and specification depth between PRD and implementation
- security and compliance gates for higher-risk work
- session continuity and project oversight
- automation-safe orchestration for repeatable execution

## Recommended Flow Extensions

### 1. CIS: Add strategy and discovery depth first

Best additions:

- `innovation-strategy`
- `design-thinking`
- `problem-solving`

Why:

- These add real upstream value before PRD and architecture work starts.
- They improve problem framing, user understanding, and solution-space exploration.
- They overlap less with the existing Compass flow than the other reviewed modules.

Keep optional:

- `storytelling`

Do not import:

- duplicate brainstorming surfaces when current BMAD brainstorming already covers the same need

### 2. WDS: Add a stronger UX and design handoff lane

Best additions:

- `trigger-mapping`
- `outline-scenarios`
- `conceptual-specifications`
- `design-delivery`
- `product-evolution` for brownfield follow-on work

Why:

- This is the clearest gap in the current Compass flow.
- WDS adds better transition structure from strategy and PRD into usable interaction design and implementation-ready handoff.
- It is especially valuable where the product needs behavioral design, user journey definition, and clearer front-end implementation guidance.

Do not import wholesale:

- the full WDS brief stack as a new parallel entry point
- any flow that forks Compass planning instead of enriching it

### 3. CYBERSEC: Add a conditional security lane

Best additions:

- threat modeling
- security architecture review
- compliance and audit prep
- secure phase gates before implementation and release

Why:

- This gives Compass a clean way to scale up for regulated, customer-data, auth-heavy, or externally exposed systems.
- The reviewed material is strongest when treated as an opt-in lane triggered by project risk.

Recommended activation conditions:

- regulated or compliance-scoped work
- authentication, payments, PII, PHI, or external integrations
- public-facing attack surface
- customer requirement for explicit security artifacts

Do not make default for every project. It adds too much process weight for low-risk work.

### 4. POV Oversight + AI Memory: keep as optional sidecars

Useful imports:

- session work index / task tracker / risk register / assumption registry patterns
- lightweight escalation and verification artifacts
- session-start and pre/post-work memory hooks
- continuity support across long-running multi-session work

Why optional:

- These improve governance and continuity, but they are not core delivery steps.
- The value is highest for long-running work, complex projects, or multi-agent execution.

Do not import directly:

- any rule set that turns normal delivery agents into non-implementing supervisors by default
- heavyweight oversight that duplicates Compass phase ownership

## What Not To Import

The review repeatedly pointed to the same boundary:

- do not merge any adjacent repo wholesale
- do not create a second planning backbone beside Compass BMAD
- do not replace existing task tracking with alternative task systems
- do not hard-wire memory or oversight into every project by default
- do not adopt opinionated constraints that reduce normal delivery velocity for low-risk work

## Recommended Adoption Order

1. CIS additions
2. WDS design lane
3. CYBERSEC conditional lane
4. POV oversight and AI memory sidecars

This order keeps overlap low and makes each layer easier to evaluate in isolation.

## Automation Research Review

The strongest automation idea in `reference/BMAD/research` is not "fully automate BMAD exactly as written." It is "wrap BMAD in a coordinator layer that makes repeated execution deterministic, resumable, and token-aware."

### High-value automation patterns to adopt

#### A. Stage-based orchestration

From the automation plugin, the most reusable pattern is lifecycle segmentation:

- plan
- epic-start
- story
- epic-end

Why it matters:

- It matches real delivery boundaries.
- It creates natural resume points.
- It keeps prompts smaller and responsibilities clearer than one giant end-to-end flow.

Compass should adopt this structure as coordinator commands or wrappers around existing BMAD workflows.

#### B. Full vs lite automation profiles

The plugin's full and lite variants are useful.

Compass equivalent:

- `guided`: more checks, more artifacts, more review
- `fast-path`: minimal safe automation for experienced operators and lower-risk work

This is better than a single automation mode because it keeps process weight proportional to project risk and maturity.

#### C. Deterministic state and sprint-status reconciliation

The automation script's strongest operational idea is deterministic project state tracking backed by evidence from artifacts.

Useful pattern:

- state file for runtime recovery
- human-readable sprint status
- evidence-based repair and validation from actual artifacts

Compass should adopt the idea, but integrate it with existing artifacts and `bd`, not as an unrelated side system.

#### D. Workflow patching instead of source workflow rewrites

`workflow-patches.md` is one of the most useful documents in the research set.

Core idea:

- keep the original workflows human-usable
- generate automation-safe variants for non-interactive runs
- validate the patched output deterministically

This is the right architecture for Compass automation. The source BMAD workflows should stay readable and operator-friendly. Automation-specific adjustments should live in a wrapper or patch layer.

#### E. Strategic context budgeting

`strategic-context.md` is directly applicable.

Best idea:

- load only the planning documents a given workflow actually needs
- cap token budget
- prefer index files for sharded artifacts unless full detail is required

Compass should adopt per-workflow context policies rather than loading PRD, architecture, UX, and project-context indiscriminately.

#### F. Session handoff protocol

`meta-handover-documentation.md` is worth adapting.

What to adopt:

- compact handoff artifacts
- explicit next action
- files touched
- decisions made
- blockers and open risks

This aligns well with Phase Closeout and with optional POV / AI memory sidecars.

#### G. Lightweight hook model

The plugin's `SessionStart` and `PreToolUse` hooks show a useful direction:

- dependency checks at session start
- lightweight guardrails before high-risk tool usage

Compass can reuse the concept, but should keep hooks minimal, portable, and repo-safe.

#### H. Parallel story execution with merge gates

The example automation and enhanced sprint material show a strong advanced pattern:

- story-level parallelism where dependencies allow it
- worktree isolation for implementation and fix phases
- sequential merge gates to protect the main branch

This is valuable, but it should be treated as a later-stage optimization after the single-story automation path is stable.

## Automation Patterns To Reject Or Rework

### 1. TodoWrite / task-list dependence

`task-management.md` and parts of `example-automation.md` assume Claude task tooling and TodoWrite as the control plane.

That does not fit this repo. Compass already uses `bd`, and `bd` should remain the source of truth for task tracking.

Use the idea of dependency-aware execution, not the specific task system.

### 2. Tight coupling to Claude plugin internals

The plugin materials are useful as design input, but they are tightly coupled to:

- specific slash commands
- plugin-local hooks
- project-specific step assumptions
- direct coordinator behavior tied to one environment

Compass should not adopt that stack directly.

### 3. Bash-heavy, platform-specific runtime assumptions

The automation script material is sophisticated, but it leans heavily on shell tooling and a Unix-oriented runtime model.

That makes it a poor direct dependency for this Windows-based workspace. Treat it as a design reference, not as an immediate runtime component.

### 4. Recovery models that depend on destructive git patterns

Several automation flows rely on rollback tags and hard resets.

That can be useful in isolated automation sandboxes, but it is too risky as a default operating model in a live collaborative repo. Compass automation should prefer:

- worktree isolation
- checkpoint artifacts
- explicit operator confirmation for destructive recovery

## Proposed Compass Automation Architecture

### Layer 1: Existing BMAD workflows remain primary

Keep current human-usable workflow definitions intact.

### Layer 2: Automation coordinator wrappers

Add Compass automation entry points aligned to delivery phases:

- `auto-plan`
- `auto-epic-start`
- `auto-story`
- `auto-epic-end`

These should orchestrate existing BMAD workflows rather than replace them.

### Layer 3: Patch/compile layer for automation-safe variants

Use a deterministic transformation layer to:

- remove interactive pauses where safe
- add structured handoff requirements
- enforce artifact checks
- add resume metadata and validation rules

### Layer 4: State, evidence, and tracking

Use:

- BMAD artifacts as execution evidence
- `bd` as task source of truth
- a human-readable status layer for sprint/story state
- repair and validation routines derived from actual artifacts

### Layer 5: Optional continuity sidecars

Add later if needed:

- handoff templates
- memory hooks
- oversight/risk registers

These should support automation and long-running work, not block normal delivery.

## Recommended Near-Term Backlog

### Flow additions

- add CIS `innovation-strategy`, `design-thinking`, and `problem-solving`
- add WDS `trigger-mapping`, `outline-scenarios`, and `design-delivery`
- add CYBERSEC threat modeling and secure gate criteria as a conditional lane

### Automation foundations

- define Compass phase-based automation entry points
- design a workflow patching mechanism for automation-safe variants
- define a token-budgeted context-loading policy per workflow
- define a handoff artifact format for session continuity
- map automation state tracking to `bd` plus BMAD artifacts

### Later-stage automation

- prototype deterministic sprint-status repair / validation
- prototype story-parallel execution with worktrees and merge gates
- evaluate lightweight hooks for session start and risky tool usage
- evaluate optional memory and oversight sidecars after the core automation layer is stable

## Related Tracking

Existing issues created from the earlier extension review:

- `bmad-engine-509` - security extension lane
- `bmad-engine-8gj` - WDS design extension lane
- `bmad-engine-uzd` - targeted CIS workflows
- `bmad-engine-lny` - optional oversight and memory substrate
- `bmad-engine-2oq` - persist findings and review automation research
- `bmad-engine-k0b` - design phase-based automation coordinator
- `bmad-engine-vm7` - define automation patching, context budgeting, and handoff model
- `bmad-engine-2tk` - prototype parallel story execution with worktrees and merge gates

## Bottom Line

Compass does not need a new BMAD. It needs:

- a few better lanes around the existing BMAD spine
- a thin automation coordinator around current workflows
- deterministic state, handoff, and context management
- optional oversight and memory only where the work justifies it

That keeps the system extensible without forking it into a second methodology.
