# BMAD Token Conservation User Guide
## Practical Strategies You Can Use Today

---

## Executive Summary

This guide provides **22 actionable strategies** that BMAD users can implement immediately to reduce token consumption. No code changes or system modifications required - these are behavioral and workflow choices that work with your current BMAD installation.

**Bottom Line:** Following these practices can **substantially reduce** token consumption and improve workflow consistency compared to uninformed usage.

### Complete Token Savings Reference

> **Note:** Impact ratings are qualitative assessments. Actual savings vary significantly based on project size, complexity, and existing documentation.

| # | Strategy | Impact | When to Use |
|---|----------|--------|-------------|
| ▸ | **PHASE 1: SETUP & INITIALIZATION** | | *Before you start* |
| 0 | Start fresh chat for each workflow | Critical | Every workflow |
| 1 | Generate project-context.md first | High | After first planning doc |
| 2 | Choose right track (Quick vs BMad) | High | At project start |
| 3 | Accept workflow resume | High | On interrupts/restarts |
| 4 | Use appropriate brownfield scan level | High | Documenting existing code |
| ▸ | **PHASE 2: SESSION MANAGEMENT** | | *While working* |
| 5 | Stay in one agent per phase | Moderate | Throughout session |
| 6 | Shard PRD, Architecture, and Epics | Moderate | After creating large docs |
| 7 | Use CSV manifests for lookups | High | Finding workflows/agents |
| 8 | Skip optional workflow steps | Moderate | When confident in output |
| 9 | Use focused, specific prompts | Moderate | Every interaction |
| ▸ | **PHASE 3: PROGRESS & VALIDATION** | | *Staying oriented, quality gates* |
| 10 | Check sprint status first | Low | Start of each session |
| 11 | Run implementation readiness check | Moderate | After completing Epics |
| 12 | Run retrospective after each epic | Moderate | After epic completion |
| 13 | Use workflow-status after each step | Low | Throughout workflow |
| 14 | Adversarial review in alt model | Moderate | Before implementation |
| ▸ | **PHASE 4: MAINTENANCE & HYGIENE** | | *Ongoing care* |
| 15 | Request sub-agent spawning | Time | Complex parallel tasks |
| 16 | Archive stale docs outside project | Low | Regular audits |
| 17 | Edit documents to remove bloat | Moderate | After major revisions |
| 18 | Use clear H2 titles for sharding | Moderate | When writing docs |
| 19 | Maintain code hygiene | Quality | Regular audits |
| ▸ | **PHASE 5: SESSION CONTINUITY** | | *Between sessions* |
| 20 | Use checkpoints for session continuity | High | Session breaks |
| 21 | Create handover docs for major transitions | High | Phase/model changes |

### Priority Actions (Highest Impact)

1. **Run** `*workflow-init` first for any new project to establish tracking
2. **Always** start fresh chats for each workflow (Strategy 0)
3. **Always** generate `project-context.md` after creating planning docs
4. **Match** task size to track: Quick Flow for Level 0-2, BMad Method for Level 3-4
5. **Accept** resume prompts - never restart unnecessarily
6. **Stay** in one agent until the phase is complete

### Brownfield Projects: Critical First Step

> **IMPORTANT:** For existing codebases (brownfield projects), you MUST run `*document-project` BEFORE any planning workflows. This scans and documents existing architecture, patterns, and conventions - essential context for AI agents working with your code.
>
> ```
> *document-project
> ```
>
> Skip this step and agents will hallucinate about your codebase structure.

---

## Phase 1: Setup & Initialization

*Strategies to apply BEFORE you begin working. These establish the foundation for an efficient session.*

---

### Key Concept: Understanding Auto-Compacting

Before diving into strategies, understand what happens when conversations get long:

**Auto-compacting** is when AI platforms automatically summarize older conversation content to stay within context limits. It triggers around 150-180K tokens and:
- **Preserves:** Recent messages, current task, active code
- **Summarizes:** Earlier context, previous decisions, files loaded earlier

**Why this matters for token conservation:**
- Many strategies in this guide (fresh chats, checkpoints, sharding) help you work WITH auto-compacting
- Knowing when it triggers helps you choose between "continue" vs "fresh chat"
- Detecting auto-compacting problems early prevents expensive rework

**Warning signs auto-compacting caused problems:**
- Agent asks about something you already discussed
- Quality drops mid-workflow
- Agent "forgets" earlier constraints

**Recovery:** Create checkpoint → Start fresh chat → Load checkpoint + project-context.md → Continue

*This context informs Strategy 0 below.*

---

## 0. Fresh Chat vs Continue: Decision Matrix

**What:** Choose strategically between starting a fresh chat or continuing in the current session. This is NOT "always fresh" - it's "fresh when it helps, continue when it helps."

**The Decision Matrix:**

| Situation | Recommendation | Why |
|-----------|----------------|-----|
| Starting a NEW workflow | Fresh chat | Clean slate, no context contamination |
| Switching BMAD phases (e.g., PRD → Architecture) | Fresh chat | Different agent, different focus |
| Context feels "garbled" or agent seems confused | Fresh chat | Reset corrupted context |
| Mid-workflow, step 1-5 of 11 | Continue | Context is still fresh and valuable |
| Mid-workflow, step 6+ of 11 | Consider checkpoint + fresh | Auto-compacting may have occurred |
| Quick follow-up question | Continue | Overhead of fresh chat exceeds benefit |
| Agent asks about something you already discussed | Fresh chat + checkpoint | Auto-compacting lost critical context |
| Exploratory conversation (brainstorming, research) | Continue | Let auto-compacting compress naturally |
| Implementation work (code, tests) | Continue | Recent code context is valuable |
| After extended break (hours/overnight) | Fresh chat + checkpoint | Context may be stale anyway |

**When to ALWAYS Start Fresh:**

- Starting any new workflow (PRD, Architecture, Epic creation, etc.)
- After completing a major phase
- When switching between agents
- When you notice quality degradation or confusion

**When to ALWAYS Continue:**

- Within a single multi-step workflow (until you notice problems)
- Quick clarifying questions
- Iterating on recently generated content
- Code review and refinement cycles

**The 11-Step Workflow Problem:**

BMAD workflows like PRD creation have 10-11 steps designed to run in ONE session. But auto-compacting may occur mid-workflow. Strategy:

1. **Steps 1-5:** Continue in same session (context is fresh)
2. **After Step 5-6:** Consider creating a checkpoint
3. **If you notice confusion:** Create checkpoint → fresh chat → reload checkpoint → continue

**Token Impact:** Strategic fresh chats prevent expensive rework from context corruption while avoiding unnecessary overhead from excessive fresh starts.

**Best Practice:** Monitor for auto-compacting symptoms (see "Detecting When Auto-Compacting Has Caused Problems" above). When detected, checkpoint and restart. Otherwise, continue.

---

## 1. Always Generate Project Context First

**What:** Run the `generate-project-context` workflow before any other workflow.

**Why:** Creates a lean, LLM-optimized summary (~50 lines) that agents can use instead of loading full documentation files.

**How:**
```
/bmad:bmm:workflows:generate-project-context
```

**Prerequisites:**
- `_bmad/bmm/config.yaml` must exist (created during BMAD installation)
- For brownfield projects, run `document-project` workflow first

**Token Impact:** Reduces context loading by an estimated 60-80% for subsequent workflows.

**Best Practice:** Regenerate after major architecture changes or when adding new epics.

**Troubleshooting:** If the workflow fails, ensure your `config.yaml` is properly configured and that you have at least one planning artifact (PRD, architecture doc, or documented project).

---

## 2. Choose the Right Track

### Project Level Guide

| Level | Description | Recommended Track | Story Count |
|-------|-------------|-------------------|-------------|
| 0 | Single file change | Quick Flow | 1 story |
| 1 | Single feature, few files | Quick Flow | 1-10 stories |
| 2 | Multi-file feature | Quick Flow | 5-15 stories |
| 3 | Multi-component feature | BMad Method | 12-40 stories |
| 4 | System-wide changes | BMad Method / Enterprise | 40+ stories |

> **Level vs Track Distinction:** *Levels* describe project complexity (how many stories). *Tracks* describe workflow depth (Quick Flow, BMad Method, Enterprise). Higher levels benefit from deeper tracks, but the mapping isn't rigid—use judgment based on requirement stability and team familiarity.

### Quick Flow (Level 0-2, 1-15 stories)

**Use Agent:** Barry (`*quick-flow-solo-dev`)
```
*quick-flow-solo-dev
```
**Or workflows:**
```
*quick-spec
*quick-dev
```

**Token Impact:** Estimated 10x reduction compared to BMad Method for small tasks.

### BMad Method (Level 3-4, 12-40+ stories)

**Use the standard phase workflows:**
- Product Brief → PRD → Architecture → Epics → Stories → Implementation

### Enterprise Track (Level 4+, 40+ stories)

For large-scale projects, Enterprise track adds extended security, DevOps strategies, and cross-team coordination workflows on top of BMad Method.

> **Note on Overlap:** The 10-15 story range intentionally overlaps. Use your judgment:
> - Lean toward Quick Flow if requirements are clear and stable
> - Lean toward BMad Method if requirements are uncertain or evolving
> - When in doubt, start with Quick Flow - you can always pivot to BMad Method

> **Tip:** If you started with Quick Flow but scope grew, run `*workflow-init` to establish proper tracking before expanding to BMad Method.

---

## 3. Accept Workflow Resume When Offered

**What:** When a workflow detects previous progress, it offers to resume. Always accept unless you want to start fresh.

**Why:** Resuming skips completed steps, avoiding re-processing of already-generated content.

**How:** Resume prompts appear in different formats depending on the workflow:

**Format A (Numbered):**
```
Previous progress detected.
1. Resume from where we left off
2. Start fresh with new session
3. Cancel

Enter choice (1-3):
```

**Format B (Letter codes):**
```
[A] Accept and continue | [R] Restart from beginning
```

Choose **1** or **[A]** to resume.

**Token Impact:** Substantial savings on interrupted workflows.

**Note:** If your output file was partially written or corrupted, restart may be necessary. Check the output file quality before accepting resume.

---

## 4. Use Appropriate Brownfield Scan Levels

**What:** When documenting existing codebases with `document-project`, the workflow offers different scan depths.

**How the Workflow Works:**
The `document-project` workflow analyzes your project and may auto-suggest an appropriate scan level based on:
- Existing documentation presence
- Project size and complexity
- File structure patterns

**Scan Levels:**

| Level | Description | Time | Token Cost |
|-------|-------------|------|------------|
| **Quick** | Pattern-based analysis, no source reading | 2-5 min | Low |
| **Deep** | Reads critical files per project type | 10-30 min | Medium |
| **Exhaustive** | Reads all source files comprehensively | 30-120 min | High |

**How:**
```
/bmad:bmm:workflows:document-project
```

When prompted for scan level, consider:
- **Quick:** Familiar codebase, need overview only, or already have some documentation
- **Deep:** Need to understand specific patterns, moderate-sized projects
- **Exhaustive:** Full documentation needed, unfamiliar codebase, large projects

**Best Practice:** Start with Quick scan. Only escalate to Deep/Exhaustive if Quick doesn't provide enough detail for your needs.

---

## Phase 2: Session Management

*Strategies to apply WHILE you're working. These keep your session efficient and focused.*

---

## 5. Stay in One Agent Per Phase

**What:** Avoid switching between agents mid-task. Complete the current phase before switching.

**Why:** Each agent switch reloads context. Staying in one agent keeps context warm.

**Phase-to-Agent Mapping:**

| Phase | Recommended Agent | Invoke Command |
|-------|-------------------|----------------|
| Analysis & Research | Mary (Analyst) | `/bmad:bmm:agents:analyst` |
| PRD Creation | John (PM) | `/bmad:bmm:agents:pm` |
| Architecture | Winston (Architect) | `/bmad:bmm:agents:architect` |
| UX Design | Sally (UX Designer) | `/bmad:bmm:agents:ux-designer` |
| Epic/Story Creation | John (PM) or Bob (SM) | `/bmad:bmm:agents:pm` or `/bmad:bmm:agents:sm` |
| Implementation | Amelia (Dev) | `/bmad:bmm:agents:dev` |
| Testing | Murat (Test Architect) | `/bmad:bmm:agents:tea` |

**Token Impact:** Estimated 30-50% savings by avoiding context reload.

**Best Practice:** Start fresh conversations for new phases. Long conversations accumulate context that degrades quality - consider breaking intensive work into separate sessions per phase.

---

## 6. Shard PRD, Architecture, and Epics Documents

**What:** Split large planning documents into smaller, focused files. The three documents that benefit most from sharding are:
- **PRD** (Product Requirements Document)
- **Architecture.md**
- **Epics.md**

**Why:** Agents only load the shard they need instead of the entire document. These three documents are loaded frequently throughout the BMAD workflow.

**How:**
```
/bmad:core:tasks:shard-doc
```

**The Process:** The shard task is interactive. After splitting your document, it will ask:
- **[d] Delete** - Remove the original file (recommended)
- **[m] Move** - Archive to a backup location
- **[k] Keep** - Retain both original and shards (not recommended)

> **Important:** If you keep both, workflows may load both, negating the benefit. Choose Delete or Move for maximum savings.

**Best Practice:**
- Shard by `##` (level 2) headings
- Each section becomes its own file in a folder structure with an `index.md`
- Archive originals **outside** the active project folder (e.g., `_bmad-output/archived/`)

**Token Impact:** Estimated 30-50% savings when working with large documents.

---

## 7. Use CSV Manifests for Lookups

**What:** When you need to find the right workflow/agent, check manifests first instead of exploring.

**Files:**
- `_bmad/_config/agent-manifest.csv` - All agents with descriptions
- `_bmad/_config/workflow-manifest.csv` - All workflows with descriptions
- `_bmad/_config/files-manifest.csv` - All files in BMAD (large file - use sparingly)

**Why:** Reading a CSV row costs ~50 tokens vs ~500+ tokens to explore a workflow folder.

**Example Usage:**
Instead of asking "What workflows are available for testing?", read the workflow manifest directly or ask the agent to check `workflow-manifest.csv` for testing-related workflows.

> **Note:** The `files-manifest.csv` can be very large (30K+ tokens). Prefer `agent-manifest.csv` and `workflow-manifest.csv` for lookups.

---

## 8. Skip Optional Workflow Steps

**What:** Many workflows have optional steps. Skip them if not needed.

**Common Skippable Steps:**
- Research workflows (if you already know the domain)
- UX Design (if no UI or using existing patterns)
- Validation steps (if confident in output quality)

**Understanding the A/P/C Menu:**
Some workflows present an options menu after completing a step:

| Option | Meaning | When to Use |
|--------|---------|-------------|
| **[A] Advanced** | Run advanced elicitation/deep analysis | When you need thorough review |
| **[P] Party Mode** | Engage multiple agents for discussion | For complex decisions needing diverse perspectives |
| **[C] Continue** | Proceed to next step | When satisfied with current output |

**How:** Choose **[C] Continue** to proceed efficiently without extensive iteration.

---

## 9. Use Focused Prompts

**What:** Give agents specific, focused instructions rather than open-ended requests.

**Instead of:**
> "Help me build a user authentication system"

**Say:**
> "Create a PRD for JWT-based authentication with email/password login. No social auth. Use existing User model."

**BMAD-Specific Tips:**
- Reference existing artifacts: "Based on the PRD in `_bmad-output/planning-artifacts/prd.md`..."
- Specify constraints upfront: "Using the patterns established in project-context.md..."
- Name the output format: "Generate a tech-spec following the BMAD template..."

**Why:** Vague prompts cause agents to explore more options, load more context, and ask more clarifying questions.

**Token Impact:** Estimated 20-40% reduction in back-and-forth.

---

## Phase 3: Progress & Validation

*Strategies for staying oriented and ensuring quality. Apply these to track progress and catch issues early.*

---

## 10. Leverage Sprint Status Tracking

**What:** Use the sprint-status workflow to track progress across sessions.

**Prerequisites:**
- Must have run `sprint-planning` workflow first to create `sprint-status.yaml`
- Requires existing epics and stories (from the `create-epics-and-stories` workflow)

**How:**
```
/bmad:bmm:workflows:sprint-status
```

**Why:** Gives you and agents a quick overview of what's done/pending without re-analyzing all documents.

**Best Practice:** Check sprint status at the start of each session to orient quickly.

**If Sprint Status Fails:**
- Ensure `sprint-planning` has been run at least once
- Check that `_bmad-output/implementation-artifacts/sprint-status.yaml` exists
- For new projects, run `workflow-init` first to establish tracking

---

## 11. Run Implementation Readiness Check

**What:** Before starting implementation, validate that your PRD, Architecture, and Epics are aligned and complete.

**Why:** Catching gaps and misalignments before coding prevents expensive rework. A missing requirement discovered mid-implementation can waste hundreds of thousands of tokens in refactoring.

**How:**
```
/bmad:bmm:workflows:check-implementation-readiness
```

**When to Run:**
- Immediately after completing `Epics.md`
- Before starting any story implementation
- After major changes to PRD or Architecture

**What It Checks:**
- PRD requirements fully covered by Epics
- Architecture decisions aligned with PRD
- Stories have complete acceptance criteria
- No orphaned requirements or undefined dependencies

**Token Impact:** Estimated 40-60% savings by preventing rework cycles.

**Best Practice:** Implement **all recommended amendments** before proceeding to implementation phase.

---

## 12. Run Retrospective After Each Epic

**What:** After completing an epic, run the retrospective workflow to capture lessons learned.

**Why:** Learning from each epic prevents repeating mistakes. Insights compound over time, leading to progressively more efficient workflows.

**How:**
```
/bmad:bmm:workflows:retrospective
```

**When to Run:**
- After all stories in an epic are complete
- Before starting the next epic
- When significant blockers or issues occurred

**What It Captures:**
- What went well (to replicate)
- What went poorly (to avoid)
- Process improvements for future epics
- Updates needed to PRD, Architecture, or other artifacts

**Token Impact:** Estimated 20-40% savings on future epics through continuous improvement.

**Best Practice:** Apply retrospective recommendations to all related artifacts before starting the next epic.

---

## 13. Use workflow-status After Each Step

**What:** Run `workflow-status` frequently to verify progress and stay oriented.

**Why:** Getting lost in a complex workflow wastes tokens on re-orientation. Regular status checks keep you on track and surface issues early.

**How:**
```
/bmad:bmm:workflows:workflow-status
```

**When to Run:**
- After completing each major workflow step
- At the start of each new session
- When unsure what to do next
- After any interruption or context switch

**What It Shows:**
- Current phase and step
- Completed vs pending items
- Recommended next action
- Any blocking issues

**Token Impact:** Estimated 15-25% savings by preventing disorientation and redundant work.

**Best Practice:** Make `workflow-status` a habit - run it after every significant step, not just when lost.

---

## 14. Adversarial Review in Alternative Model

**What:** Before implementation, review your planning artifacts using a different AI model (e.g., Gemini 2.5 Pro, GPT-4).

**Why:** Different models have different blind spots. Cross-model review catches issues that a single model might miss consistently.

**How:**
1. Export your PRD, Architecture, and Epics documents
2. Open a session with an alternative model (Gemini, GPT-4, etc.)
3. Ask it to review for gaps, inconsistencies, and potential issues
4. Incorporate valid feedback before implementation

**What to Ask the Alternative Model:**
- "Review this PRD for missing requirements or ambiguities"
- "Check this architecture for scalability concerns and anti-patterns"
- "Identify any gaps between this PRD and these Epics"
- "What edge cases or failure modes are not addressed?"

**Token Impact:** Estimated 30-50% savings by catching issues before expensive implementation.

**Best Practice:** Use adversarial review for critical documents. The cost of a second model review is far less than implementation rework.

---

## Phase 4: Maintenance & Hygiene

*Strategies for ongoing project health. Apply these regularly throughout your project lifecycle.*

---

## 15. Request Sub-Agent Spawning for Parallel Work

**What:** Ask the AI to spawn background sub-agents for tasks that can run in parallel, such as multi-file analysis, parallel searches, or concurrent validations.

**Why:** Sub-agents can:
- Analyze multiple files simultaneously
- Run different elicitation methods in parallel
- Perform comprehensive searches without blocking the main conversation
- Reduce wall-clock time for complex analyses by 3-5x

> **Platform Note:** Sub-agent spawning is a Claude Code feature, not a core BMAD capability. Availability depends on your AI platform.

**How:**
When you have a task that involves analyzing multiple independent items, explicitly request parallel execution:

```
"Run these 5 validation checks in parallel using background sub-agents"
"Spawn sub-agents to analyze each epic file concurrently"
"Use parallel agents to search for all usages of this pattern across the codebase"
```

**Best Practices:**
- Request parallel execution for independent tasks (no dependencies between them)
- Specify the number of agents or let the AI determine optimal parallelization
- For dependent tasks, let them run sequentially
- Ask for synthesized results after all agents complete

**Time vs Token Trade-off:** Sub-agents trade tokens for time—each agent uses its own token budget, but parallel execution dramatically reduces wall-clock time. This is a *time optimization*, not a token savings strategy. Use when speed matters more than token cost.

**Estimated Impact:** 20-40% reduction in elapsed time on complex multi-file analyses. Token usage may increase slightly due to parallel context loading.

**Example Use Cases:**
- Advanced elicitation (run 5 methods in parallel)
- Code review across multiple files
- Searching for patterns across the codebase
- Validating multiple documents against requirements

---

## 16. Archive Stale Documents Outside Project Folder

**What:** Regularly audit your project folder and move outdated, superseded, or no-longer-relevant documents to an archive location OUTSIDE the active project.

**Why:** AI agents discover and load documents from your project folder. Stale documents:
- Consume tokens when loaded unnecessarily
- Confuse agents with outdated information
- Cause conflicts between old and new guidance
- Increase the chance of hallucinations based on obsolete content

**What to Archive:**
- Old versions of PRDs, architecture docs, or epics (after sharding or major rewrites)
- Superseded tech specs or design documents
- Completed sprint retrospectives older than 2 sprints
- Draft documents that were never finalized
- Exploration notes that informed decisions but aren't needed for implementation

**How:**

1. **Create archive folder OUTSIDE project:**
   ```
   ~/Archives/[project-name]/
   ```
   NOT inside `_bmad-output/` or project root

2. **Regular audit schedule:**
   - After each epic completion
   - Before starting a new major phase
   - When project-context.md is regenerated

3. **Archive checklist:**
   - [ ] Old PRD versions (keep only current)
   - [ ] Superseded architecture decisions
   - [ ] Completed/closed epic files
   - [ ] Old sprint status snapshots
   - [ ] Draft documents never finalized

**Token Impact:** Estimated 10-30% reduction in unnecessary document loading.

**Best Practice:** If you're unsure whether to archive, ask: "Would an AI agent implementing the next story need this document?" If no, archive it.

---

## 17. Edit Documents to Remove Bloat

**What:** Periodically review and trim your planning documents (Brief, PRD, Architecture, Epics) to remove redundant, verbose, or outdated content.

**Why:** Every word in your planning documents costs tokens when loaded. Bloated documents:
- Take longer to load and process
- Dilute critical information with noise
- Cause agents to miss important details buried in verbosity
- Make sharding less effective (bloated sections = bloated shards)

**What to Trim:**

| Document | Common Bloat | Keep |
|----------|--------------|------|
| **Product Brief** | Lengthy market analysis, competitor deep-dives | Core vision, key differentiators, success metrics |
| **PRD** | Excessive rationale, repeated context | Clear requirements, acceptance criteria, constraints |
| **Architecture** | Over-explained decisions, hypothetical scenarios | Decisions made, patterns to follow, integration points |
| **Epics/Stories** | Background context repeated in each story | Specific tasks, acceptance criteria, dependencies |

**How to Trim:**

1. **Remove redundancy:** If the same information appears in multiple places, keep it in ONE authoritative location
2. **Cut rationale bloat:** "We chose X because..." can often become "Use X."
3. **Eliminate hedging:** "We might consider possibly..." → Make a decision or remove
4. **Compress examples:** One clear example beats three similar ones
5. **Delete resolved discussions:** Once a decision is made, remove the debate

**Bloat Reduction Checklist:**
- [ ] Each section answers ONE clear question
- [ ] No paragraph exceeds 3-4 sentences
- [ ] Examples are minimal and illustrative
- [ ] No "TBD" or "TODO" items left unresolved
- [ ] Cross-references replace repeated content

**Token Impact:** Estimated 20-50% reduction in document size without losing essential information.

**Best Practice:** After any major document revision, read it asking "What can I delete without losing actionable information?"

---

## 18. Use Clear H2 Section Titles for Effective Sharding

**What:** When writing documents that will be sharded (PRD, Architecture, Epics), use descriptive, self-contained H2 (`##`) section titles.

**Why:** The `*shard-doc` task splits documents at H2 (`##`) headings. Each section becomes a standalone file. If your H2 titles are vague or context-dependent, the resulting shards will be confusing when loaded individually.

**Bad H2 Titles (Context-Dependent):**
```markdown
## Overview
## Details
## Implementation
## Notes
## Part 1
## Continued
```

**Good H2 Titles (Self-Contained):**
```markdown
## User Authentication Requirements
## Database Schema Design
## API Endpoint Specifications
## Error Handling Strategy
## Security Constraints
## Performance Requirements
```

**H2 Title Checklist:**
- [ ] Title describes the section's content without needing document context
- [ ] Someone reading ONLY this section would understand its purpose
- [ ] Title is unique within the document (no duplicate H2s)
- [ ] Title uses domain terminology consistently
- [ ] Title is scannable (agent can decide to load or skip based on title alone)

**Document-Specific Guidance:**

| Document | H2 Pattern | Example |
|----------|------------|---------|
| **PRD** | Feature or requirement area | `## User Registration Flow` |
| **Architecture** | Component or decision area | `## Authentication Service Design` |
| **Epics** | Epic name with context | `## Epic 1: Core Authentication` |

**How to Audit Existing Documents:**

1. List all H2 headings in the document
2. For each, ask: "If I saw only this title, would I know what's in the section?"
3. Rename vague titles to be self-describing
4. Then run `*shard-doc`

**Token Impact:** Well-titled shards enable selective loading - agents load only relevant sections. Estimated 30-50% reduction in unnecessary content loading.

---

## 19. Maintain Code Hygiene - Remove Stale Code from Project

**What:** Regularly audit your codebase to remove or archive stale code, unused files, old tests, and deprecated modules that are no longer part of the active project.

**Why:** AI agents analyze your codebase to understand patterns and context. Stale code:
- Misleads agents about current architecture and patterns
- Causes agents to reference deprecated approaches
- Increases codebase scan time and token consumption
- Creates confusion when old and new patterns conflict

**What to Remove/Archive:**

| Category | Examples | Action |
|----------|----------|--------|
| **Dead Code** | Unused functions, commented-out blocks, unreachable branches | Delete |
| **Deprecated Modules** | Old implementations replaced by new ones | Archive outside project |
| **Stale Tests** | Tests for removed features, skipped tests with no plan to fix | Delete or archive |
| **Experiment Code** | Spikes, POCs, "trying something" code | Archive outside project |
| **Old Migrations** | Database migrations from 6+ months ago | Consider archiving |
| **Backup Files** | `.bak`, `.old`, `_backup` files | Delete |
| **Generated Files** | Build artifacts, compiled code in source folders | Add to .gitignore, delete |

**Code Hygiene Audit Process:**

1. **Identify candidates:**
   ```
   "Analyze this codebase and identify potentially stale code:
   - Functions/classes with no references
   - Files not modified in 6+ months
   - Tests that are skipped or commented out
   - Modules that appear deprecated"
   ```

2. **Verify before removing:**
   - Check git blame for context on why code exists
   - Search for dynamic references (string-based imports, reflection)
   - Confirm tests pass after removal

3. **Archive, don't just delete:**
   - Move to `~/Archives/[project-name]/stale-code/`
   - Include a README noting why it was archived and date
   - Keep git history intact (archive after committing removal)

**Recommended Audit Schedule:**
- After each epic completion
- Before major refactoring efforts
- Quarterly for long-running projects

**Token Impact:** Cleaner codebase = faster scans, more accurate pattern recognition, fewer misleading examples. Estimated 10-30% improvement in agent code understanding accuracy.

**Best Practice:** Before any `*document-project` or `*dev-story` workflow, ask: "Is there stale code that might confuse the AI about our current patterns?"

---

## Phase 5: Session Continuity

*Strategies for maintaining context BETWEEN sessions. Apply these when ending or resuming work.*

### Community Best Practices

> **Note:** Strategies 20-21 are user-developed practices that complement BMAD workflows. They are not official BMAD features but have proven effective for token conservation across sessions.

---

## 20. Use Checkpoints for Session Continuity

**What:** Create lightweight checkpoint files at natural breakpoints in your workflow to enable fresh chat resumption without losing progress.

**Why:** Checkpoints bridge the gap between "fresh chats for each workflow" (Strategy 0) and "not losing work." They capture just enough context to resume efficiently.

**When to Create Checkpoints:**

| Trigger | Checkpoint Type | What to Capture |
|---------|-----------------|-----------------|
| End of work session | Session checkpoint | Current step, pending decisions, next actions |
| Workflow step completion | Step checkpoint | Step output summary, blockers encountered |
| Before complex decision | Decision checkpoint | Options considered, criteria, leaning toward |
| After major output | Artifact checkpoint | What was created, where it's saved, validation status |
| When stuck/blocked | Blocker checkpoint | What failed, what was tried, hypotheses |

**Checkpoint File Structure:**

```markdown
# Checkpoint: [Workflow/Task Name]

## Metadata
**Version:** 1.0
**Created:** YYYY-MM-DD HH:MM
**Last Updated:** YYYY-MM-DD HH:MM
**Valid Until:** [Date or "Until workflow completes"]
**Session:** [Brief identifier]
**Agent:** [Which agent was active]

## Validation Status
- [ ] Checkpoint reflects current project state
- [ ] No major decisions have changed since creation
- [ ] Referenced artifacts still exist at listed paths

## Current State
- **Phase:** [BMAD phase]
- **Workflow:** [Active workflow name]
- **Step:** [Current/last completed step]
- **Output file:** [Path to any generated artifacts]
- **Project-context.md version:** [Version or date if exists]

## Context Summary (MAX 10 BULLETS)
- [Key decision 1]
- [Key decision 2]
- [Important constraint discovered]
- [Pattern established]
- ...

## Pending Items
- [ ] [Next immediate action]
- [ ] [Unresolved question]
- [ ] [Blocker to address]

## Resume Instructions
To continue this work:
1. Start fresh chat
2. Load [specific agent]
3. **Verify this checkpoint is still valid** (check Validation Status above)
4. Run [specific command]
5. Reference this checkpoint for context

## Staleness Warning
If this checkpoint is older than 48 hours OR if major decisions have been made since creation, verify it against current project state before using.
```

**Checkpoint Best Practices:**

| DO | DON'T |
|----|-------|
| Keep under 50 lines | Write full narrative of session |
| Bullet points only | Include paragraphs of explanation |
| Reference artifact paths | Duplicate artifact content |
| Note decisions MADE | Rehash decision debates |
| List specific next actions | Vague "continue work" |

**Where to Store Checkpoints:**

```
_bmad-output/
├── checkpoints/           # Active checkpoints
│   ├── session-2026-01-12.md
│   └── prd-step-5.md
└── checkpoints-archive/   # Completed/stale checkpoints
```

**Token Impact:**
- **Cost:** ~200-500 tokens to create a checkpoint
- **Savings:** Avoids 2,000-10,000 tokens of "catching up" conversation
- **Net:** Estimated 80-90% reduction in session-start overhead

**Checkpoint Lifecycle:**

1. **Create** at natural breakpoints
2. **Use** to start fresh sessions
3. **Update** as work progresses (don't create new ones for same workflow)
4. **Archive** when workflow completes
5. **Delete** archived checkpoints after 1 week

**Anti-Pattern Warning:**
Creating checkpoints for every minor step creates more overhead than it saves. Use checkpoints for:
- Session boundaries (stopping for the day)
- Phase transitions
- Before/after complex decisions
- When blocked and need fresh perspective

NOT for:
- Every file edit
- Minor clarifications
- Within a single workflow step

---

## 21. Create Handover Documents for Major Transitions

**What:** Create structured handover documents when transitioning between major project phases, changing AI models, or when another person/agent will continue the work.

**Why:** Handovers capture comprehensive context that checkpoints don't - the "why" behind decisions, lessons learned, and strategic context that enables informed continuation.

**Checkpoints vs Handovers:**

| Aspect | Checkpoint | Handover Document |
|--------|------------|-------------------|
| **Purpose** | Resume same work quickly | Transfer knowledge comprehensively |
| **Length** | 30-50 lines | 100-300 lines |
| **Audience** | Same agent/model | Different agent, model, or person |
| **Lifespan** | Hours to days | Weeks to permanent |
| **Detail level** | What & next steps | What, why, how, and lessons |
| **When to create** | Session breaks | Phase completions, model switches |

**When to Create Handover Documents:**

1. **Phase Transition Handovers** - End of Analysis, Planning, Solutioning phases
2. **Epic Completion Handovers** - After each epic is fully implemented
3. **Model Switch Handovers** - Before switching from Claude to GPT or vice versa
4. **Person Handovers** - When another developer will continue
5. **Blocker Escalation Handovers** - When stuck and need expert help
6. **Project Pause Handovers** - Before extended breaks (vacation, deprioritization)

**Handover Document Template:**

```markdown
# Handover: [Project/Phase/Epic Name]

## Document Metadata
| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Created** | YYYY-MM-DD |
| **Last Validated** | YYYY-MM-DD |
| **Author** | [Agent or person] |
| **Recipient** | [Intended continuation agent/model/person] |
| **Handover Type** | [Phase/Epic/Model-Switch/Blocker/Pause] |
| **PRD Version** | [Version/date of PRD this aligns with] |
| **Architecture Version** | [Version/date of architecture this aligns with] |
| **Project-context.md Version** | [Version/date or "Regenerate recommended"] |

## Validation Checklist (Before Using This Handover)
- [ ] PRD has not changed significantly since this handover was created
- [ ] Architecture decisions still match what's documented here
- [ ] No new epics or major stories have been added
- [ ] Project-context.md is current (regenerate if older than this handover)
- [ ] Listed file paths still exist and are current

> **Staleness Warning:** If this handover is older than 1 week AND work has continued, verify key decisions against current artifacts before proceeding.

---

## Executive Summary
[2-3 sentences: What was accomplished, current state, what's next]

---

## Completed Work

### Artifacts Created
| Artifact | Path | Version/Date | Status | Notes |
|----------|------|--------------|--------|-------|
| PRD | `_bmad-output/planning-artifacts/prd.md` | v1.2 | Complete | Sharded |
| Architecture | `_bmad-output/planning-artifacts/architecture.md` | v1.0 | Complete | - |
| Project Context | `_bmad-output/project-context.md` | 2026-01-12 | Current | - |
| ... | ... | ... | ... | ... |

### Key Decisions Made
1. **[Decision Area]:** [Decision] - [Brief rationale]
2. **[Decision Area]:** [Decision] - [Brief rationale]
3. ...

### Patterns Established
- [Pattern 1: e.g., "All API endpoints use /api/v1/ prefix"]
- [Pattern 2: e.g., "Error responses follow RFC 7807 format"]
- ...

---

## Current State

### What's Working
- [Working aspect 1]
- [Working aspect 2]

### Known Issues
- [Issue 1] - [Severity] - [Workaround if any]
- [Issue 2] - [Severity] - [Workaround if any]

### Technical Debt Incurred
- [Debt item 1] - [Why it was accepted] - [When to address]
- ...

---

## Lessons Learned
1. **[Lesson]:** [What we learned and how to apply it going forward]
2. **[Lesson]:** [What we learned and how to apply it going forward]
3. ...

---

## Continuation Instructions

### Immediate Next Steps
1. [ ] [Specific action 1]
2. [ ] [Specific action 2]
3. [ ] [Specific action 3]

### Recommended Approach
[Paragraph explaining the suggested approach for continuing]

### Watch Out For
- [Pitfall to avoid 1]
- [Pitfall to avoid 2]

### Questions to Resolve
- [Open question 1]
- [Open question 2]

---

## Context for New Agent/Model

### Project Summary
[Brief description for someone with no prior context]

### Critical Files to Load First
1. `project-context.md` - Start here (verify version matches above)
2. `[specific artifact]` - [Why it's important]
3. ...

### Don't Load (Stale/Archived)
- `[old file]` - [Why to skip]
- ...

### Version Compatibility
This handover was created against:
- PRD version: [X]
- Architecture version: [X]
- If these have changed, review Key Decisions section for potential conflicts.
```

**Handover Best Practices:**

| DO | DON'T |
|----|-------|
| Focus on decisions and rationale | Dump entire conversation history |
| List specific file paths | Say "see the PRD" without path |
| Note what NOT to load | Assume all project files are relevant |
| Include lessons learned | Only list what was done |
| Provide continuation steps | End with vague "continue work" |

**Where to Store Handovers:**

```
Handovers/
├── phase-1-analysis-handover-2026-01-10.md
├── epic-1-auth-handover-2026-01-15.md
├── model-switch-claude-to-gpt-2026-01-18.md
└── [archived after 30 days to ~/Archives/]
```

**Token Impact:**

| Scenario | Without Handover | With Handover | Savings |
|----------|------------------|---------------|---------|
| Phase transition | 5,000-15,000 tokens catching up | 500-1,000 tokens reading handover | 80-95% |
| Model switch | 10,000-20,000 tokens re-explaining | 1,000-2,000 tokens reading handover | 85-90% |
| Epic continuation | 3,000-8,000 tokens reviewing | 500-1,000 tokens reading handover | 75-85% |

**What Handovers CAN'T Do:**

- **Replace artifacts:** Handovers summarize, they don't replace PRDs or architecture docs
- **Stay current automatically:** They capture a point in time; update if work continues
- **Transfer tacit knowledge:** Complex patterns may still need re-discovery
- **Guarantee continuity:** New agent may still interpret things differently

**Handover + Checkpoint Strategy:**

Use BOTH together for optimal results:
1. **Checkpoints** for day-to-day session continuity (same agent, same workflow)
2. **Handovers** for major transitions (phase complete, model switch, person change)

```
Session 1 → [checkpoint] → Session 2 → [checkpoint] → Session 3
                                                          ↓
                                                   [HANDOVER]
                                                          ↓
                             New Phase / New Agent / New Model
```

**When NOT to Create Handovers:**

- Mid-workflow (use checkpoint instead)
- For small tasks (overhead exceeds benefit)
- When artifacts are self-documenting (well-structured PRD speaks for itself)
- Every session (that's checkpoint territory)

---

## Understanding BMAD Workflow States

### Workflow Initialization
Before starting any BMAD project, consider running:
```
/bmad:bmm:workflows:workflow-init
```
This determines your project level and track, creating proper status tracking.

### Checking Current Status
At any point, check where you are:
```
/bmad:bmm:workflows:workflow-status
```
This shows current phase, completed steps, and recommended next actions.

---

## Anti-Patterns to Avoid

### DON'T: Start BMad Method for Small Tasks
**Problem:** Creating a Product Brief + PRD + Architecture for a 2-hour feature.
**Solution:** Use Quick Flow (`quick-flow-solo-dev` agent or `quick-spec` workflow).

### DON'T: Switch Agents Mid-Conversation
**Problem:** "Let me ask Winston about this architecture question" while working with Amelia on implementation.
**Solution:** Complete the current task first, or ask Amelia to consider the architecture question. Start a new conversation for the next phase.

### DON'T: Load All Documents "Just in Case"
**Problem:** Asking agents to "review all project documentation before starting."
**Solution:** Let agents discover what they need through the standard workflow steps.

### DON'T: Ignore Resume Prompts
**Problem:** Clicking "Restart" or "2" when a workflow offers to resume.
**Solution:** Accept resume unless you specifically need to redo previous steps.

### DON'T: Use Exhaustive Scans on Familiar Codebases
**Problem:** Running exhaustive brownfield scan on code you wrote last week.
**Solution:** Use Quick scan for familiar code, Deep only when patterns are unclear.

### DON'T: Keep Original After Sharding
**Problem:** Sharding a large PRD but keeping the original file.
**Solution:** Delete or move the original so workflows don't load both versions.

---

## Troubleshooting Common Issues

### Workflow Won't Start
1. Check that `_bmad/bmm/config.yaml` exists and is configured
2. Run `/bmad:bmm:workflows:workflow-init` to establish tracking
3. Ensure prerequisites are met (see individual strategy sections)

### Resume Not Working
1. Check if the output file exists and is valid
2. If file is corrupted or partial, restart is necessary
3. Some workflows track state in frontmatter - check the output document's YAML header

### Agent Not Found
1. Check exact agent name in `_bmad/_config/agent-manifest.csv`
2. Use the full command format: `/bmad:bmm:agents:<agent-name>`
3. Agent names are case-sensitive and use hyphens

### Sprint Status Empty
1. Run `sprint-planning` workflow first
2. Ensure epics and stories exist in `_bmad-output/planning-artifacts/`
3. Check that `sprint-status.yaml` was created successfully

---

## Token-Saving Checklist

### Before Starting Any BMAD Session

- [ ] Is `project-context.md` up to date?
- [ ] Have I chosen the right track (Quick vs Full)?
- [ ] Do I know which single agent I'll use for this phase?
- [ ] Am I starting with a focused, specific prompt?

### During the Session

- [ ] Accept resume when offered (option 1 or [A])
- [ ] Use [C] Continue to skip optional elaboration
- [ ] Stay in the current agent until phase complete
- [ ] Choose minimal scan levels for brownfield
- [ ] Start fresh conversations for new phases

### After Completing Major Documents

- [ ] Shard PRD, Architecture.md, and Epics.md
- [ ] Delete/move originals after sharding
- [ ] Regenerate project-context.md if architecture changed
- [ ] Run implementation readiness check before coding

### After Each Epic

- [ ] Run retrospective workflow
- [ ] Apply recommendations to related artifacts
- [ ] Consider adversarial review in alternative model for critical projects

---

## Quick Commands Reference

> **Note:** Commands can be invoked two ways:
> - **Shortcut:** `*command-name` (e.g., `*workflow-init`) - quicker to type
> - **Full path:** `/bmad:module:type:name` - explicit and unambiguous
>
> **Important:** The `*` shortcut syntax only works when an agent is already loaded in the conversation. If starting fresh, use the full `/bmad:...` path. Both formats invoke the same underlying workflow.

| Task | Shortcut | Full Command |
|------|----------|--------------|
| Initialize workflow tracking | `*workflow-init` | `/bmad:bmm:workflows:workflow-init` |
| Check current status | `*workflow-status` | `/bmad:bmm:workflows:workflow-status` |
| Generate project context | `*generate-project-context` | `/bmad:bmm:workflows:generate-project-context` |
| Quick spec for small feature | `*quick-spec` | `/bmad:bmm:workflows:quick-spec` |
| Quick dev implementation | `*quick-dev` | `/bmad:bmm:workflows:quick-dev` |
| Create PRD | `*prd` | `/bmad:bmm:workflows:prd` |
| Create architecture | `*create-architecture` | `/bmad:bmm:workflows:create-architecture` |
| Create epics and stories | `*create-epics-and-stories` | `/bmad:bmm:workflows:create-epics-and-stories` |
| Sprint planning | `*sprint-planning` | `/bmad:bmm:workflows:sprint-planning` |
| Create next story | `*create-story` | `/bmad:bmm:workflows:create-story` |
| Implement story | `*dev-story` | `/bmad:bmm:workflows:dev-story` |
| Code review | `*code-review` | `/bmad:bmm:workflows:code-review` |
| Shard large document | `*shard-doc` | `/bmad:core:tasks:shard-doc` |
| Check sprint status | `*sprint-status` | `/bmad:bmm:workflows:sprint-status` |
| Document existing project | `*document-project` | `/bmad:bmm:workflows:document-project` |
| Implementation readiness check | `*implementation-readiness` | `/bmad:bmm:workflows:check-implementation-readiness` |
| Epic retrospective | `*retrospective` | `/bmad:bmm:workflows:retrospective` |

### Agent Quick Reference

| Role | Agent | Shortcut | Full Command |
|------|-------|----------|--------------|
| Business Analysis | Mary | `*analyst` | `/bmad:bmm:agents:analyst` |
| Product Management | John | `*pm` | `/bmad:bmm:agents:pm` |
| Architecture | Winston | `*architect` | `/bmad:bmm:agents:architect` |
| UX Design | Sally | `*ux-designer` | `/bmad:bmm:agents:ux-designer` |
| Scrum Master | Bob | `*sm` | `/bmad:bmm:agents:sm` |
| Development | Amelia | `*dev` | `/bmad:bmm:agents:dev` |
| Test Architecture | Murat | `*tea` | `/bmad:bmm:agents:tea` |
| Quick Flow | Barry | `*quick-flow-solo-dev` | `/bmad:bmm:agents:quick-flow-solo-dev` |
| Technical Writing | Paige | `*tech-writer` | `/bmad:bmm:agents:tech-writer` |

---

## Glossary

| Term | Definition |
|------|------------|
| **Brownfield** | An existing codebase with established patterns, architecture, and technical debt |
| **Greenfield** | A new project starting from scratch with no existing code |
| **Epic** | A large body of work that can be broken down into smaller stories |
| **Story** | A single unit of deliverable work, typically completable in one session |
| **Sharding** | Splitting a large document into smaller, section-based files for efficient loading |
| **Sprint** | A time-boxed period for completing a set of stories |
| **PRD** | Product Requirements Document - defines what to build and why |
| **Tech Spec** | Technical Specification - defines how to build it |
| **Quick Flow** | Lightweight BMAD track for small tasks (1-15 stories) |
| **BMad Method** | Full BMAD track for complex projects (10-50+ stories) |
| **Context Window** | The amount of text an AI can process in one conversation |
| **Token** | A unit of text (roughly 4 characters or 0.75 words) that AI models process |

---

## Summary

The biggest token savings come from three simple habits:

1. **Start with project-context.md** - One small file replaces loading many large ones
2. **Match track to task size** - Quick Flow for sm... (7 KB left)