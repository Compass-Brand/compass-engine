# BMAD Documentation Suite — Implementation Plan

> **COMPLETED.** All documentation files created and indexed.
>
> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create 10 developer-facing documentation files covering BMAD concepts, workflows, and extension modules that are currently undocumented. Close all 11 open beads.

**Architecture:** Each doc is a standalone Markdown file in `docs/development/bmad/`, synthesized from source specs in `src/bmad/` and upstream `BMAD-METHOD/`. The README.md index is updated once at the end. One bead (`2tk`) is deferred, not a documentation task.

**Tech Stack:** Markdown documentation, `bd` CLI for issue tracking

---

## Execution Strategy

**Dependency chain:** `39b` → `2zj` → `42r` (must be sequential)
**Independent tasks:** `fqu`, `dk6`, `ds6`, `c73`, `4q3`, `y4d`, `ope` (can all run in parallel)

### Wave 1 — Parallel (8 docs + 1 deferral)

All independent docs plus `39b` (which unblocks `2zj`). Close `2tk` as deferred.

| Task | Bead | Doc File |
|------|------|----------|
| 1 | `fqu` | `automation-wrappers.md` |
| 2 | `39b` | `quick-spec-quick-dev.md` |
| 3 | `dk6` | `project-context.md` |
| 4 | `ds6` | `beads-integration.md` |
| 5 | `c73` | `extension-modules.md` |
| 6 | `4q3` | `agent-conflict-prevention.md` |
| 7 | `y4d` | `advanced-techniques.md` |
| 8 | `ope` | `script-replacement.md` |
| 9 | `2tk` | *(defer — not ready for prototype)* |

### Wave 2 — Sequential (depends on Wave 1 Task 2)

| Task | Bead | Doc File |
|------|------|----------|
| 10 | `2zj` | `when-to-use-bmad.md` |

### Wave 3 — Sequential (depends on Wave 2 Task 10)

| Task | Bead | Doc File |
|------|------|----------|
| 11 | `42r` | *(add "Scale-Adaptive Levels" section to `when-to-use-bmad.md`)* |

### Finalization

| Task | Description |
|------|-------------|
| 12 | Update `docs/development/bmad/README.md` index with all new docs |
| 13 | Commit all docs, close beads, sync, push |

---

## Task Details

### Task 1: Automation Wrappers Developer Guide (`bmad-engine-fqu`)

**Bead:** `bmad-engine-fqu` (P1)
**Create:** `docs/development/bmad/automation-wrappers.md`

**Sources to read:**
- `src/bmad/tools/automation/README.md` (114 lines)
- `src/bmad/tools/automation/commands/auto-plan.md` (233 lines)
- `src/bmad/tools/automation/commands/auto-epic-start.md` (80 lines)
- `src/bmad/tools/automation/commands/auto-story.md` (96 lines)
- `src/bmad/tools/automation/commands/auto-epic-end.md` (80 lines)
- `src/bmad/tools/automation/policies/state-model.md` (225 lines)
- `src/bmad/tools/automation/policies/patching-strategy.md` (128 lines)
- `src/bmad/tools/automation/policies/context-budgeting.md` (101 lines)
- `src/bmad/BMAD-workflow.md` — Automation Wrappers section

**Sections to write:**
1. What automation wrappers are and how they differ from direct workflow invocation
2. The 4 wrappers with scope summary (auto-plan, auto-epic-start, auto-story, auto-epic-end)
3. Current status: spec-only vs implemented as runtime commands
4. State model: how wrappers track progress across steps
5. Approval model: which checkpoints require human approval
6. Context budgeting: how wrappers manage AI context consumption
7. Patching strategy: correcting wrapper state mid-run
8. How to extend or modify automation wrappers
9. Relationship to canonical workflow in BMAD-workflow.md

**Steps:**
1. Claim bead: `bd update bmad-engine-fqu --status=in_progress`
2. Read all source files listed above
3. Write `docs/development/bmad/automation-wrappers.md` synthesizing the sources
4. Close bead: `bd close bmad-engine-fqu`
5. Commit: `git add docs/development/bmad/automation-wrappers.md && git commit -m "docs(bmad): add automation wrappers developer guide"`

---

### Task 2: Quick-Spec and Quick-Dev Decision Guide (`bmad-engine-39b`)

**Bead:** `bmad-engine-39b` (P1, blocks `2zj`)
**Create:** `docs/development/bmad/quick-spec-quick-dev.md`

**Sources to read:**
- `src/bmad/modules/custom/compass-skills/4-implementation/bmad-compass-quick-spec/` — all files (~159 lines)
- `src/bmad/modules/native/bmm-skills/4-implementation/bmad-quick-dev/` — all files (~470 lines)
- `BMAD-METHOD/docs/explanation/quick-dev.md` (73 lines)
- `src/bmad/BMAD-workflow.md` — Supporting And Alternate Lanes section

**Sections to write:**
1. What Quick Spec is: lightweight intent-to-spec workflow
2. What Quick Dev is: unified intent-in code-out workflow
3. How they differ: QS produces spec artifact; QD goes straight to implementation
4. Why Compass preserves a separate QS path when upstream merged it into QD
5. The `bmad-compass-quick-spec` skill and its relationship to `bmad-bmm-quick-dev`
6. Decision criteria: when to use QS, QD, or the full 4-phase method
7. Quick Dev Review Trail (v6.2.1)
8. Scale-adaptive routing: how QD detects complexity and may escalate

**Steps:**
1. Claim bead: `bd update bmad-engine-39b --status=in_progress`
2. Read all source files listed above
3. Write `docs/development/bmad/quick-spec-quick-dev.md`
4. Close bead: `bd close bmad-engine-39b`
5. Commit: `git add docs/development/bmad/quick-spec-quick-dev.md && git commit -m "docs(bmad): add quick-spec and quick-dev decision guide"`

---

### Task 3: Project Context File Guide (`bmad-engine-dk6`)

**Bead:** `bmad-engine-dk6` (P2)
**Create:** `docs/development/bmad/project-context.md`

**Sources to read:**
- `BMAD-METHOD/docs/explanation/project-context.md` (157 lines)
- `src/bmad/modules/native/bmm-skills/3-solutioning/bmad-generate-project-context/workflow.md` (43 lines)
- `src/bmad/modules/native/bmm-skills/3-solutioning/bmad-generate-project-context/project-context-template.md` (21 lines)
- `src/bmad/modules/custom/bmm-skills/3-solutioning/bmad-generate-project-context/` — custom override
- `src/bmad/BMAD-workflow.md` — initialization section (step 5) and Detailed Analysis (step 1)

**Sections to write:**
1. What project-context.md is: AI-relevant project snapshot
2. Why it matters: agents load it on activation
3. When to generate: brownfield (early), greenfield (after framing), refresh at phase start
4. Where it lives in Compass: `current/research/project-context/`
5. How it differs from upstream location (`_bmad-output/project-context.md`)
6. The `/bmad-bmm-generate-project-context` command
7. What goes into a project context file (tech stack, conventions, structure, testing, config)
8. Which workflows and agents consume it
9. How to manually create or edit when auto-generation is insufficient
10. Relationship to CLAUDE.md and other AI configuration files

**Steps:**
1. Claim bead: `bd update bmad-engine-dk6 --status=in_progress`
2. Read all source files listed above
3. Write `docs/development/bmad/project-context.md`
4. Close bead: `bd close bmad-engine-dk6`
5. Commit: `git add docs/development/bmad/project-context.md && git commit -m "docs(bmad): add project context file guide"`

---

### Task 4: Beads Integration with BMAD Workflow (`bmad-engine-ds6`)

**Bead:** `bmad-engine-ds6` (P2)
**Create:** `docs/development/bmad/beads-integration.md`

**Sources to read:**
- `src/bmad/BMAD-workflow.md` — Beads Control Rules section (exact 7 rules), Phase Sync, Story Loop, Phase Closeout
- `src/planning/docs/how-to-use.md` (98 lines) — Beads overlay section
- `src/bmad/tools/automation/` — automation wrapper Beads integration points

**Sections to write:**
1. What Beads is and why it replaces TodoWrite/markdown task lists
2. The `bd` command lifecycle mapped to BMAD phases (prime, create, update, close, sync)
3. Phase issues: created during Phase Sync, closed during Phase Closeout
4. Story issues: creation before Dev Story, claiming, closing after acceptance
5. Tracking newly discovered work: blockers, defects, carry-over
6. Workspace vs repo-local issue scoping
7. Phase Closeout reconciliation
8. The 7 Beads Control Rules (verbatim from BMAD-workflow.md)

**Steps:**
1. Claim bead: `bd update bmad-engine-ds6 --status=in_progress`
2. Read all source files listed above
3. Write `docs/development/bmad/beads-integration.md`
4. Close bead: `bd close bmad-engine-ds6`
5. Commit: `git add docs/development/bmad/beads-integration.md && git commit -m "docs(bmad): add Beads integration guide"`

---

### Task 5: Extension Modules Reference (`bmad-engine-c73`)

**Bead:** `bmad-engine-c73` (P2)
**Create:** `docs/development/bmad/extension-modules.md`

**Sources to read:**
- `src/bmad/BMAD-workflow.md` — TEA/CIS/WDS/CYBERSEC insertion rules and extension rules sections
- `src/bmad/modules/custom/compass-skills/4-implementation/bmad-compass-testarch-*/SKILL.md` — TEA skill summaries
- `src/bmad/modules/custom/compass-skills/4-implementation/bmad-agent-tea/SKILL.md`
- `src/bmad/modules/custom/compass-skills/1-analysis/bmad-compass-innovation-strategy/SKILL.md`
- `src/bmad/modules/custom/compass-skills/1-analysis/bmad-compass-design-thinking/SKILL.md`
- `src/bmad/modules/custom/compass-skills/1-analysis/bmad-agent-innovation-strategist/SKILL.md`
- `src/bmad/modules/custom/compass-skills/1-analysis/bmad-agent-design-thinking-coach/SKILL.md`
- `src/bmad/modules/custom/compass-skills/2-plan-workflows/bmad-agent-wds-designer/SKILL.md`
- `src/bmad/modules/custom/compass-skills/2-plan-workflows/bmad-compass-wds-ux-design/SKILL.md`
- `src/bmad/modules/custom/compass-skills/1-analysis/bmad-agent-wds-analyst/SKILL.md`
- `src/bmad/modules/custom/compass-skills/3-solutioning/bmad-compass-threat-modeling/SKILL.md`
- `src/bmad/modules/custom/compass-skills/3-solutioning/bmad-compass-security-architecture-review/SKILL.md`
- `src/bmad/modules/custom/compass-skills/3-solutioning/bmad-agent-threat-analyst/SKILL.md`

**Sections to write (one per extension):**

**TEA:**
1. What TEA is, key agent (Murat), 9 workflows
2. When to activate TEA lane vs built-in code review
3. TEA dual appearance: system-level (solutioning) and epic-level (implementation)
4. TEA insertion and replacement rules
5. Command compatibility table

**CIS:**
1. What CIS provides, key agents (Victor, Maya)
2. Innovation Strategy and Opportunity Framing as analysis steps
3. Problem Solving as anytime lane
4. Upstream vs Compass customizations

**WDS:**
1. What WDS is, 4 sub-workflows
2. WDS placement: after PRD, before architecture
3. When to activate, what it doesn't replace

**CYBERSEC:**
1. What CYBERSEC provides, key agent (Bastion)
2. Compass-only (not upstream)
3. Activation heuristic and dual gates

**Steps:**
1. Claim bead: `bd update bmad-engine-c73 --status=in_progress`
2. Read BMAD-workflow.md extension rules and all SKILL.md files listed above
3. Write `docs/development/bmad/extension-modules.md`
4. Close bead: `bd close bmad-engine-c73`
5. Commit: `git add docs/development/bmad/extension-modules.md && git commit -m "docs(bmad): add extension modules reference (TEA, CIS, WDS, CYBERSEC)"`

---

### Task 6: Agent Conflict Prevention in Polyrepo Context (`bmad-engine-4q3`)

**Bead:** `bmad-engine-4q3` (P3)
**Create:** `docs/development/bmad/agent-conflict-prevention.md`

**Sources to read:**
- `BMAD-METHOD/docs/explanation/preventing-agent-conflicts.md` (112 lines)
- `src/bmad/BMAD-workflow.md` — Polyrepo Routing Rules section
- `src/planning/docs/how-to-use.md` — authority rules

**Sections to write:**
1. Why agents conflict: contradictory assumptions about architecture/conventions
2. How architecture docs prevent conflicts: shared source of truth
3. The role of project-context.md as primary conflict prevention mechanism
4. Polyrepo-specific concerns: workspace vs parent vs leaf repo authority
5. Cross-repo interface contracts and shared conventions
6. How BMAD's 4-phase methodology inherently prevents conflicts
7. Best practices for concurrent BMAD workflows across repos

**Steps:**
1. Claim bead: `bd update bmad-engine-4q3 --status=in_progress`
2. Read all source files listed above
3. Write `docs/development/bmad/agent-conflict-prevention.md`
4. Close bead: `bd close bmad-engine-4q3`
5. Commit: `git add docs/development/bmad/agent-conflict-prevention.md && git commit -m "docs(bmad): add agent conflict prevention guide for polyrepo"`

---

### Task 7: Advanced Elicitation and Adversarial Review (`bmad-engine-y4d`)

**Bead:** `bmad-engine-y4d` (P3)
**Create:** `docs/development/bmad/advanced-techniques.md`

**Sources to read:**
- `src/bmad/modules/custom/compass-skills/anytime/bmad-compass-advanced-elicitation/workflow.md` (84 lines)
- `src/bmad/modules/custom/compass-skills/anytime/bmad-compass-advanced-elicitation/methods.csv` (~80 rows)
- `src/bmad/modules/custom/compass-skills/anytime/bmad-compass-autonomous-refinement-loop/workflow.md` (149 lines)
- `src/bmad/modules/native/core-skills/` — adversarial review skill (locate via grep)

**Sections to write:**
1. What Advanced Elicitation is: pushing LLM to reconsider assumptions, find gaps
2. What Adversarial Review is: structured challenge of artifacts
3. The Autonomous Refinement Loop: party-mode + advanced elicitation for iterative improvement
4. When to use these techniques: complex PRDs, architecture docs, high-stakes decisions
5. How they integrate with the main workflow (anytime skills)
6. The `--content` argument pattern for targeting specific artifacts

**Steps:**
1. Claim bead: `bd update bmad-engine-y4d --status=in_progress`
2. Read all source files listed above
3. Write `docs/development/bmad/advanced-techniques.md`
4. Close bead: `bd close bmad-engine-y4d`
5. Commit: `git add docs/development/bmad/advanced-techniques.md && git commit -m "docs(bmad): add advanced elicitation and adversarial review guide"`

---

### Task 8: Script Replacement Strategy (`bmad-engine-ope`)

**Bead:** `bmad-engine-ope` (P4)
**Create:** `docs/development/bmad/script-replacement.md`

**Sources to read:**
- `src/bmad/tools/prompts/bmad-scripts.md` (29 lines)
- `src/bmad/tools/` — check for existing script implementations
- `src/bmad/tools/automation/` — relationship to automation wrappers

**Sections to write:**
1. What script replacement is: swapping AI workflow steps with deterministic code
2. Why: reduce context token consumption for predictable operations
3. Current status: experimental concept vs active approach
4. Which workflow steps are candidates for replacement
5. How to create a script replacement for a workflow step
6. Relationship to automation wrappers

**Note:** This is a P4 evaluation task. The source file is only 29 lines. The doc may be short — that's fine. If the concept is abandoned, document that finding and close the bead with a reason.

**Steps:**
1. Claim bead: `bd update bmad-engine-ope --status=in_progress`
2. Read source file and check for existing implementations
3. Write `docs/development/bmad/script-replacement.md` (or close with reason if concept is abandoned)
4. Close bead: `bd close bmad-engine-ope`
5. Commit: `git add docs/development/bmad/script-replacement.md && git commit -m "docs(bmad): add script replacement strategy guide"`

---

### Task 9: Defer Parallel Story Execution Prototype (`bmad-engine-2tk`)

**Bead:** `bmad-engine-2tk` (P3)

This is not a documentation task — it's an implementation prototype. The bead notes say to "revisit after the single-repo, polyrepo, and automation proof cycles are complete." This work is not ready.

**Steps:**
1. Close bead with reason: `bd close bmad-engine-2tk --reason="Deferred: prototype depends on completing single-repo, polyrepo, and automation proof cycles first. Revisit when those are stable."`

---

### Task 10: BMAD Usage Decision Tree (`bmad-engine-2zj`)

**Bead:** `bmad-engine-2zj` (P1, depends on `39b`, blocks `42r`)
**Create:** `docs/development/bmad/when-to-use-bmad.md`

**Prerequisites:** Task 2 (`39b`) must be complete — this doc references quick-spec/quick-dev concepts.

**Sources to read:**
- `docs/development/bmad/quick-spec-quick-dev.md` (created in Task 2)
- `src/bmad/BMAD-workflow.md` — required progression chain and conditional lanes
- `BMAD-METHOD/docs/how-to/established-projects.md` (if exists)
- `docs/development/bmad/bmad-overview.md` — scale-adaptive intelligence description

**Sections to write:**
1. Decision tree (flowchart or table) covering 5 paths:
   - (a) Ad hoc changes with no BMAD
   - (b) Quick-spec only
   - (c) Quick-dev
   - (d) Partial BMAD
   - (e) Full roadmap-driven BMAD
2. How scale-adaptive levels 0-4 map to these approaches
3. Criteria for each level: team size, scope, risk, compliance, timeline
4. Real-scenario examples with recommended approach
5. How to transition: starting with quick-dev, escalating when complexity is discovered
6. Brownfield vs greenfield considerations

**Steps:**
1. Claim bead: `bd update bmad-engine-2zj --status=in_progress`
2. Read all source files listed above (including the doc created in Task 2)
3. Write `docs/development/bmad/when-to-use-bmad.md`
4. Close bead: `bd close bmad-engine-2zj`
5. Commit: `git add docs/development/bmad/when-to-use-bmad.md && git commit -m "docs(bmad): add BMAD usage decision tree"`

---

### Task 11: Scale-Adaptive Intelligence Levels (`bmad-engine-42r`)

**Bead:** `bmad-engine-42r` (P3, depends on `2zj`)
**Modify:** `docs/development/bmad/when-to-use-bmad.md` (add detailed section)

**Prerequisites:** Task 10 (`2zj`) must be complete.

**Sources to read:**
- `docs/development/bmad/when-to-use-bmad.md` (created in Task 10)
- `src/bmad/BMAD-workflow.md` — required vs conditional gate classifications
- BMAD-METHOD source for scale-adaptive detection logic (search for scale/level references)

**Section to add (expand existing scale-adaptive coverage in when-to-use-bmad.md):**
1. How scale level is determined: manual selection vs auto-detection heuristics
2. What changes at each level (0-4): artifacts, workflows, gates, review strictness
3. Concrete examples mapping real scenarios to levels
4. How to override or adjust levels mid-project
5. Cross-reference back to decision tree section

**Steps:**
1. Claim bead: `bd update bmad-engine-42r --status=in_progress`
2. Read when-to-use-bmad.md and source files
3. Expand scale-adaptive section in `docs/development/bmad/when-to-use-bmad.md`
4. Close bead: `bd close bmad-engine-42r`
5. Commit: `git add docs/development/bmad/when-to-use-bmad.md && git commit -m "docs(bmad): expand scale-adaptive intelligence levels detail"`

---

### Task 12: Update README Index

**Modify:** `docs/development/bmad/README.md`

**Steps:**
1. Read current README.md
2. Add entries for all new docs under a new "## Usage & Integration" section:
   - [When to Use BMAD](./when-to-use-bmad.md) — decision tree for choosing the right BMAD approach
   - [Quick-Spec & Quick-Dev](./quick-spec-quick-dev.md) — fast-path workflows and when to use them
   - [Project Context](./project-context.md) — the project-context.md artifact and its role
   - [Automation Wrappers](./automation-wrappers.md) — developer guide for automation orchestration
   - [Beads Integration](./beads-integration.md) — how Beads integrates with BMAD lifecycle
   - [Extension Modules](./extension-modules.md) — TEA, CIS, WDS, and CYBERSEC reference
   - [Agent Conflict Prevention](./agent-conflict-prevention.md) — preventing conflicts in polyrepo context
   - [Advanced Techniques](./advanced-techniques.md) — elicitation, adversarial review, and refinement loops
   - [Script Replacement](./script-replacement.md) — strategy for replacing workflow steps with scripts
3. Commit: `git add docs/development/bmad/README.md && git commit -m "docs(bmad): update README index with all new documentation"`

---

### Task 13: Final Sync and Push

**Steps:**
1. `git status` — verify all changes committed
2. `bd sync` — sync beads state
3. `git push` — push to remote
