---
name: 'step-01-mode-detection'
description: 'Determine execution mode (tech-spec vs direct), handle escalation, set state variables'

nextStepFile_modeA: './step-03-execute.md'
nextStepFile_modeB: './step-02-context-gathering.md'
---

# Step 1: Mode Detection

**Goal:** Determine execution mode, capture baseline, handle escalation if needed.

---

## STATE VARIABLES (capture now, persist throughout)

These variables MUST be set in this step and available to all subsequent steps:

- `{baseline_commit}` - Git HEAD at workflow start (or "NO_GIT" if not a git repo)
- `{execution_mode}` - "tech-spec" or "direct"
- `{tech_spec_path}` - Path to tech-spec file (if Mode A)
- `{epic_num}` - Epic number inferred from the tech-spec (Mode A, A.1). Unset if not derivable.
- `{story_num}` - Story number inferred from the tech-spec (Mode A, A.1). Unset if not derivable.
- `{epic_context_path}` - Absolute path to the compiled epic context file (Mode A, A.1). Unset when A.1 falls through silently. **Precedence:** when set, downstream steps IGNORE `{planning_context_files}` (Mode B, B.0) — the epic context already summarizes planning docs.
- `{continuity_context}` - Concatenated Code Map + Design Notes + Spec Change Log + Tasks sections extracted from the most recent prior `status: done` spec in the same epic (Mode A, A.2). Unset when no prior story exists or the operator skips the in-review fallback.

---

## EXECUTION SEQUENCE

### 1. Capture Baseline

First, check if the project uses Git version control:

**If Git repo exists** (`.git` directory present or `git rev-parse --is-inside-work-tree` succeeds):

- Run `git rev-parse HEAD` and store result as `{baseline_commit}`

**If NOT a Git repo:**

- Set `{baseline_commit}` = "NO_GIT"

### 2. Load Project Context

Check if `{project_context}` exists (`**/project-context.md`). If found, load it as a foundational reference for ALL implementation decisions.

### 3. Parse User Input

Analyze the user's input to determine mode:

**Mode A: Tech-Spec**

- User provided a path to a tech-spec file (e.g., `quick-dev tech-spec-auth.md`)
- Load the spec, extract tasks/context/AC
- Set `{execution_mode}` = "tech-spec"
- Set `{tech_spec_path}` = provided path
- Proceed to sub-section **A.1 Epic inference** below before transitioning to step-03.

#### A.1 Epic inference

**Purpose:** When the tech-spec belongs to an epic, compile (or reuse) a cached epic-context summary so step-02/03 can load it as a single concise reference instead of re-deriving from raw planning docs.

**Enter when:** `{execution_mode}` = "tech-spec" AND `{tech_spec_path}` is set.
**Exit when:** `{epic_context_path}` is either set to a validated context file OR left unset (silent fall-through). In both cases, continue to sub-section **A.2 Previous story continuity** below.

Execute these sub-items in order:

**3a. Parse tech-spec frontmatter.** Read the YAML frontmatter of `{tech_spec_path}`. Derive `{epic_num}` using the first rule that yields a positive integer:

1. `epic:` field (e.g., `epic: 3`)
2. `story:` field parsed as `E.S` (e.g., `story: 3.2` → epic 3)
3. Filename slug regex `^(\d+)-` against `basename({tech_spec_path})` (e.g., `spec-3-2-auth.md` → 3)

Also derive `{story_num}` from the `story:` field when present (e.g., `story: 3.2` → 2), or from the second digit group of the filename slug `^\d+-(\d+)-` when absent. Leave `{story_num}` unset if neither source yields a value.

If no rule yields `{epic_num}`, skip to sub-item **3e** (silent fall-through).

**3b. Check for cached epic context.** Resolve `{epic_context_path}` candidate as `{implementation_artifacts}/epic-{epic_num}-context.md`. If the file exists AND its mtime is newer than every source planning doc under `{planning_artifacts}` (PRD, architecture, UX, epics, brief), set `{epic_context_path}` to the candidate path and skip to sub-item **3d** (cache is valid).

**3c. Spawn compile-epic-context sub-agent.** Invoke sibling task `compile-epic-context.md` via the sub-agent mechanism, passing `{epic_num}` as input. The sub-agent writes the summary to `{implementation_artifacts}/epic-{epic_num}-context.md` and returns that path. Set `{epic_context_path}` to the returned path.

**3d. Verify output.** Read the first non-blank line of `{epic_context_path}`. Assert it starts with `# Epic {epic_num} Context:` (exact heading prefix, matching the compile-epic-context output contract). On mismatch: HALT, surface the assertion failure (path + actual first line), and instruct the operator to re-run or inspect.

**3e. Silent fall-through.** If `{epic_num}` could not be derived in 3a, leave `{epic_context_path}` unset and proceed. Mode A must continue to work for non-epic tech-specs with no user-visible error.

**Post-conditions for A.1:**

- `{epic_context_path}` is either unset (no epic) or points to a file whose first line matches `# Epic <N> Context:`.
- `{epic_num}` and `{story_num}` are set when derivable; otherwise unset.
- **Precedence reminder:** downstream steps that see `{epic_context_path}` set MUST ignore `{planning_context_files}` (Mode B, B.0) — the epic context already summarizes the same planning docs.

#### A.2 Previous story continuity

**Purpose:** When the current tech-spec belongs to an epic with prior completed stories, load a continuity summary (Code Map + Design Notes + Spec Change Log + Tasks) from the most recent `status: done` sibling spec so step-02/03 can reuse established patterns and honor prior constraints.

**Enter when:** Mode A is active AND `{epic_num}` is set AND `{story_num}` is set (both populated by A.1 sub-item 3a).
**Exit when:** `{continuity_context}` is either set to an assembled summary OR left unset (no candidates, or operator skipped the in-review fallback). In both cases, continue to the NEXT directive at the end of Mode A.

Execute these sub-items in order:

**3a. Glob candidate sibling specs.** List files matching `{implementation_artifacts}/spec-{epic_num}-*.md`. Exclude `{tech_spec_path}` itself from the result set. If zero candidates remain, skip to sub-item **3d** (no continuity available).

**3b. Filter by status and story number.** For each candidate, parse YAML frontmatter and extract `status` and `story` (derive story number via the same rules as A.1 sub-item 3a: `story:` field first, then filename `^\d+-(\d+)-`). Retain candidates where:

- `status == "done"` AND parsed story number is a positive integer strictly less than `{story_num}`.

From the retained set, select the candidate with the greatest story number. Ties (should not occur with one spec per story) resolve by most recent file mtime. If the retained set is empty, skip to sub-item **4** (in-review fallback).

**3c-i. Extract continuity sections by heading.** From the chosen spec file, extract the bodies of the following level-2 headings (match by exact heading text, case-sensitive, body spans until the next `## ` heading or EOF):

- `## Code Map`
- `## Design Notes`
- `## Spec Change Log`
- `## Tasks` (or `## Task List` if `## Tasks` is absent — prefer `## Tasks`)

Missing sections are recorded as empty strings; do not halt.

**3c-ii. Assemble `{continuity_context}`.** Concatenate the extracted sections in the order listed above, preserving their level-2 headings as section labels, separated by a single blank line between sections. Prefix the assembled string with a one-line provenance header:

```
> Continuity from spec-{E}-{S}-<slug>.md (status: done)
```

Set `{continuity_context}` to the assembled string.

**4. In-review fallback prompt.** Reached only when sub-item 3b yields zero `status: done` candidates. Re-run the same filter with `status == "in-review"` and the same story-number constraint. If the retained set is non-empty, select the greatest-story-number candidate and HALT with this prompt:

```
No prior `done` spec found in epic {epic_num}. An `in-review` spec exists:

  {chosen_spec_basename} (story {chosen_story_num})

Loading it as continuity context means relying on a not-yet-finalized spec.

[L] Load — proceed with in-review continuity
[S] Skip — continue without continuity context
```

- IF L: execute sub-items 3c-i and 3c-ii against the chosen in-review spec. Amend the provenance header to read `status: in-review` instead of `status: done`.
- IF S: leave `{continuity_context}` unset and proceed.
- ALWAYS halt and wait for user input before branching; do NOT auto-select.

**3d. Silent fall-through.** Reached when no candidates exist at all (3a empty) or no in-review candidates exist after a miss (4 empty). Leave `{continuity_context}` unset and proceed.

**Post-conditions for A.2:**

- `{continuity_context}` is either unset or contains the assembled sections with a provenance header naming the source spec and its status.
- No file writes occurred in A.2 — it is a pure read/scan step.

- **NEXT (after A.2 completes):** Read fully and follow: `{project-root}/_bmad/bmm/4-implementation/bmad-quick-dev/steps/step-03-execute.md`

**Mode B: Direct Instructions**

- User provided task description directly (e.g., `refactor src/foo.ts...`)
- Set `{execution_mode}` = "direct"
- **NEXT:** Evaluate escalation threshold, then proceed

---

## ESCALATION THRESHOLD (Mode B only)

Evaluate user input with minimal token usage (no file loading):

**Triggers escalation (if 2+ signals present):**

- Multiple components mentioned (dashboard + api + database)
- System-level language (platform, integration, architecture)
- Uncertainty about approach ("how should I", "best way to")
- Multi-layer scope (UI + backend + data together)
- Extended timeframe ("this week", "over the next few days")

**Reduces signal:**

- Simplicity markers ("just", "quickly", "fix", "bug", "typo", "simple")
- Single file/component focus
- Confident, specific request

Use holistic judgment, not mechanical keyword matching.

---

## ESCALATION HANDLING

### No Escalation (simple request)

Display: "**Select:** [P] Plan first (tech-spec) [E] Execute directly"

#### Menu Handling Logic:

- IF P: Direct user to `{quick_spec_workflow}`. **EXIT Quick Dev.**
- IF E: Ask for any additional guidance, then **NEXT:** Read fully and follow: `{project-root}/_bmad/bmm/4-implementation/bmad-quick-dev/steps/step-02-context-gathering.md`

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed when user makes a selection

---

### Escalation Triggered - Level 0-2

Present: "This looks like a focused feature with multiple components."

Display:

**[P] Plan first (tech-spec)** (recommended)
**[W] Seems bigger than quick-dev** - Recommend the Full BMad Flow PRD Process
**[E] Execute directly**

#### Menu Handling Logic:

- IF P: Direct to `{quick_spec_workflow}`. **EXIT Quick Dev.**
- IF W: Direct user to run the PRD workflow instead. **EXIT Quick Dev.**
- IF E: Ask for guidance, then **NEXT:** Read fully and follow: `{project-root}/_bmad/bmm/4-implementation/bmad-quick-dev/steps/step-02-context-gathering.md`

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed when user makes a selection

---

### Escalation Triggered - Level 3+

Present: "This sounds like platform/system work."

Display:

**[W] Start BMad Method** (recommended)
**[P] Plan first (tech-spec)** (lighter planning)
**[E] Execute directly** - feeling lucky

#### Menu Handling Logic:

- IF P: Direct to `{quick_spec_workflow}`. **EXIT Quick Dev.**
- IF W: Direct user to run the PRD workflow instead. **EXIT Quick Dev.**
- IF E: Ask for guidance, then **NEXT:** Read fully and follow: `{project-root}/_bmad/bmm/4-implementation/bmad-quick-dev/steps/step-02-context-gathering.md`

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed when user makes a selection

---

## NEXT STEP DIRECTIVE

**CRITICAL:** When this step completes, explicitly state which step to load:

- Mode A (tech-spec, after A.1 Epic inference and A.2 Previous story continuity complete): "**NEXT:** read fully and follow: `{project-root}/_bmad/bmm/4-implementation/bmad-quick-dev/steps/step-03-execute.md`"
- Mode B (direct, [E] selected): "**NEXT:** Read fully and follow: `{project-root}/_bmad/bmm/4-implementation/bmad-quick-dev/steps/step-02-context-gathering.md`"
- Escalation ([P] or [W]): "**EXITING Quick Dev.** Follow the directed workflow."

---

## SUCCESS METRICS

- `{baseline_commit}` captured and stored
- `{execution_mode}` determined ("tech-spec" or "direct")
- `{tech_spec_path}` set if Mode A
- A.1 Epic inference executed when Mode A: `{epic_context_path}` set to a verified summary OR left unset via silent fall-through
- Project context loaded if exists
- Escalation evaluated appropriately (Mode B)
- Explicit NEXT directive provided

## FAILURE MODES

- Proceeding without capturing baseline commit
- Not setting execution_mode variable
- Loading step-02 when Mode A (tech-spec provided)
- Attempting to "return" after escalation instead of EXIT
- No explicit NEXT directive at step completion
