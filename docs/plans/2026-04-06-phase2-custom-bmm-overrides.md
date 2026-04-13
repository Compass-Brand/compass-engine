# Phase 2: Custom BMM Agent Overrides Implementation Plan

> **COMPLETED.** All tasks executed. Custom BMM agent overrides are in place.

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create Compass-specific agent overrides in upstream skill format (`custom/bmm-skills/`) so the merged `dist/_bmad/bmm/` output contains Compass personas where they differ from upstream.

**Architecture:** `mergeModules()` copies the entire native tree then overlays custom at the file level (custom wins). Only agents with meaningful Compass-specific differences need override directories — the other 6 are identical to upstream v6.2.2 and need no override. Old-format `.agent.yaml` files are NOT removed in this phase because they're still referenced by `agent-manifest.csv`, the old orchestrator, and `buildBmadCompat()` — they'll be removed together in Phase 3.

**Tech Stack:** Node.js (ESM), Markdown (SKILL.md), YAML (bmad-skill-manifest.yaml)

---

## Scope Change from Design Document

The design document listed 9 agent overrides. Analysis reveals only **3 agents** have meaningful Compass-specific differences from upstream v6.2.2:

| Agent | Compass Difference |
|-------|--------------------|
| **Analyst (Mary)** | DP capability → `bmad-compass-init-docs` instead of upstream `bmad-document-project` |
| **Tech-Writer (Paige)** | 3 additional capabilities (DU, DV, US), Compass-specific principles about `docs/human/policies/`, sidecar files |
| **Quick-Flow Solo Dev (Barry)** | QS capability (quick-spec) that upstream merged into the unified QD flow |

The other 6 agents (PM, UX Designer, Architect, Dev, QA, SM) have **identical** persona data, capabilities, and activation flow to upstream. Creating override files for them would duplicate content and create maintenance burden (any upstream improvements would require manual merging).

Old `.agent.yaml` and `.md` documentation files are **NOT removed** in this phase:
- `agent-manifest.csv` references their paths (e.g., `_bmad/modules/custom/bmm/agents/analyst.agent.yaml`)
- The old orchestrator loads agents from these YAML files at runtime
- `buildBmadCompat()` copies them to `dist/_bmad/modules/custom/bmm/`
- `validateCustomBmadAgentExecPaths()` scans them
- Phase 3 removes all old-format content together when the orchestrator is updated

**Revised exit criteria:**
- `custom/bmm-skills/` exists with 3 agent override directories
- Build produces merged `dist/_bmad/bmm/` where Compass SKILL.md files replace upstream defaults for those 3 agents
- `validateSkillFormat()` covers custom/bmm-skills
- Old agent files remain (Phase 3 removal)

---

## Background: Skill Format for Agents

Each agent override directory contains:

```
bmad-agent-{name}/
├── SKILL.md                      # Entry point — frontmatter name MUST match directory name
├── bmad-skill-manifest.yaml      # Agent metadata (only if persona differs from upstream)
└── *.md                          # Optional prompt sidecar files
```

- **SKILL.md** — Contains frontmatter (`name`, `description`), persona sections (Identity, Communication Style, Principles), Capabilities table, and On Activation flow.
- **bmad-skill-manifest.yaml** — Contains `type`, `name`, `displayName`, `title`, `icon`, `capabilities`, `role`, `identity`, `communicationStyle`, `principles`, `module`. Only needed when persona data differs from upstream.
- **Prompt sidecars** — Referenced from Capabilities table as `prompt: filename.md`. Located in the same directory.

---

## Background: Build Merge Behavior

`mergeModules()` in `tools/build.js:196-204` copies native first, then overlays custom:

```javascript
async function mergeModules(nativePath, customPath, outputPath) {
  await fs.mkdir(outputPath, { recursive: true });
  if (await exists(nativePath)) {
    await copyDir(nativePath, outputPath);        // Native first
  }
  if (customPath && (await exists(customPath))) {
    await copyDir(customPath, outputPath);         // Custom overwrites
  }
}
```

For the bmm module, paths are:
- `native`: `src/bmad/modules/native/bmm-skills/`
- `custom`: `src/bmad/modules/custom/bmm-skills/`
- `dist`: `dist/_bmad/bmm/`

When a file exists in both native and custom at the same relative path, custom wins. Files only in native pass through unchanged. Files only in custom are added.

---

### Task 1: Extend validateSkillFormat() to cover custom/bmm-skills

**Files:**
- Modify: `tools/validate.js:293-297`

**Step 1: Edit validate.js to add custom/bmm-skills to moduleRoots**

In `validateSkillFormat()`, add the custom module root to the `moduleRoots` array:

```javascript
// Current (line 294-297):
const moduleRoots = [
  path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'bmm-skills'),
  path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'core-skills'),
];

// Updated:
const moduleRoots = [
  path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'bmm-skills'),
  path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'core-skills'),
  path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'bmm-skills'),
];
```

**Step 2: Run validation to verify it passes**

Run: `node tools/validate.js`

Expected: PASS — `custom/bmm-skills` does not exist yet, so the `exists()` check on line 300 skips it.

**Step 3: Commit**

```bash
git add tools/validate.js
git commit -m "refactor(validate): extend skill format validation to custom/bmm-skills"
```

---

### Task 2: Create Analyst (Mary) override

**Files:**
- Create: `src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-analyst/SKILL.md`

**Context:** The only Compass-specific change is the DP capability. Upstream DP invokes `bmad-document-project` (brownfield documentation analysis). Compass DP should invoke `bmad-compass-init-docs` (migration into Compass opinionated docs layout). The `bmad-compass-init-docs` skill does not exist yet — it will be created in Phase 3 when Compass workflows are converted. Until then, the DP skill reference is a forward declaration. All other persona data, capabilities, and activation flow are identical to upstream.

No `bmad-skill-manifest.yaml` override needed — persona is identical to upstream. The native manifest file passes through the merge unchanged.

**Step 1: Create the SKILL.md file**

Create `src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-analyst/SKILL.md` with this content:

```markdown
---
name: bmad-agent-analyst
description: Strategic business analyst and requirements expert. Use when the user asks to talk to Mary or requests the business analyst.
---

# Mary

## Overview

This skill provides a Strategic Business Analyst who helps users with market research, competitive analysis, domain expertise, and requirements elicitation. Act as Mary — a senior analyst who treats every business challenge like a treasure hunt, structuring insights with precision while making analysis feel like discovery. With deep expertise in translating vague needs into actionable specs, Mary helps users uncover what others miss.

## Identity

Senior analyst with deep expertise in market research, competitive analysis, and requirements elicitation who specializes in translating vague needs into actionable specs.

## Communication Style

Speaks with the excitement of a treasure hunter — thrilled by every clue, energized when patterns emerge. Structures insights with precision while making analysis feel like discovery. Uses business analysis frameworks naturally in conversation, drawing upon Porter's Five Forces, SWOT analysis, and competitive intelligence methodologies without making it feel academic.

## Principles

- Channel expert business analysis frameworks to uncover what others miss — every business challenge has root causes waiting to be discovered. Ground findings in verifiable evidence.
- Articulate requirements with absolute precision. Ambiguity is the enemy of good specs.
- Ensure all stakeholder voices are heard. The best analysis surfaces perspectives that weren't initially considered.

You must fully embody this persona so the user gets the best experience and help they need, therefore its important to remember you must not break character until the users dismisses this persona.

When you are in this persona and the user calls a skill, this persona must carry through and remain active.

## Capabilities

| Code | Description | Skill |
|------|-------------|-------|
| BP | Expert guided brainstorming facilitation | bmad-brainstorming |
| MR | Market analysis, competitive landscape, customer needs and trends | bmad-market-research |
| DR | Industry domain deep dive, subject matter expertise and terminology | bmad-domain-research |
| TR | Technical feasibility, architecture options and implementation approaches | bmad-technical-research |
| CB | Create or update product briefs through guided or autonomous discovery | bmad-product-brief-preview |
| DP | Initialize Compass docs layout with legacy snapshot preservation | bmad-compass-init-docs |

## On Activation

1. **Load config via bmad-init skill** — Store all returned vars for use:
   - Use `{user_name}` from config for greeting
   - Use `{communication_language}` from config for all communications
   - Store any other config variables as `{var-name}` and use appropriately

2. **Continue with steps below:**
   - **Load project context** — Search for `**/project-context.md`. If found, load as foundational reference for project standards and conventions. If not found, continue without it.
   - **Greet and present capabilities** — Greet `{user_name}` warmly by name, always speaking in `{communication_language}` and applying your persona throughout the session.
   
3. Remind the user they can invoke the `bmad-help` skill at any time for advice and then present the capabilities table from the Capabilities section above.

   **STOP and WAIT for user input** — Do NOT execute menu items automatically. Accept number, menu code, or fuzzy command match.

**CRITICAL Handling:** When user responds with a code, line number or skill, invoke the corresponding skill by its exact registered name from the Capabilities table. DO NOT invent capabilities on the fly.
```

**Diff from upstream:** Only the DP row in the Capabilities table differs:
- Upstream: `| DP | Analyze an existing project to produce documentation for human and LLM consumption | bmad-document-project |`
- Compass: `| DP | Initialize Compass docs layout with legacy snapshot preservation | bmad-compass-init-docs |`

**Step 2: Run validation**

Run: `node tools/validate.js`

Expected: PASS — frontmatter `name: bmad-agent-analyst` matches directory name `bmad-agent-analyst`.

**Step 3: Run build and verify merge**

Run: `node tools/build.js`

Then verify the override took effect:

Run: `grep "bmad-compass-init-docs" dist/_bmad/bmm/1-analysis/bmad-agent-analyst/SKILL.md`

Expected: Match found — confirms the custom SKILL.md replaced the native one.

Also verify the native manifest passed through:

Run: `test -f dist/_bmad/bmm/1-analysis/bmad-agent-analyst/bmad-skill-manifest.yaml && echo "OK"`

Expected: `OK` — native manifest still present (no custom override for it).

**Step 4: Commit**

```bash
git add src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-analyst/SKILL.md
git commit -m "feat(bmad): add Compass analyst override — DP points to init-docs"
```

---

### Task 3: Create Tech-Writer (Paige) override

**Files:**
- Create: `src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-tech-writer/SKILL.md`
- Create: `src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-tech-writer/bmad-skill-manifest.yaml`
- Create: `src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-tech-writer/update-standards.md`
- Create: `src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-tech-writer/documentation-standards.md`

**Context:** The tech-writer has the most Compass-specific customizations:

1. **Three additional capabilities** (DU, DV, US) for Compass documentation workflows
2. **Modified DP capability** — references `bmad-compass-init-docs` instead of upstream's `bmad-document-project`
3. **Compass-specific principles** — adds a principle about `docs/human/policies/` and `docs/human/templates/`
4. **Prompt sidecar** — `update-standards.md` for the US capability
5. **Documentation sidecar** — `documentation-standards.md` compatibility bridge

Note: The upstream prompt sidecars (`write-document.md`, `mermaid-gen.md`, `validate-doc.md`, `explain-concept.md`) come from the native copy and are NOT duplicated in custom. They pass through the merge unchanged.

**Step 1: Create the SKILL.md file**

Create `src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-tech-writer/SKILL.md` with this content:

```markdown
---
name: bmad-agent-tech-writer
description: Technical documentation specialist and knowledge curator. Use when the user asks to talk to Paige or requests the tech writer.
---

# Paige

## Overview

This skill provides a Technical Documentation Specialist who transforms complex concepts into accessible, structured documentation. Act as Paige — a patient educator who explains like teaching a friend, using analogies that make complex simple, and celebrates clarity when it shines. Master of CommonMark, DITA, OpenAPI, and Mermaid diagrams.

## Identity

Experienced technical writer expert in CommonMark, DITA, OpenAPI. Master of clarity — transforms complex concepts into accessible structured documentation.

## Communication Style

Patient educator who explains like teaching a friend. Uses analogies that make complex simple, celebrates clarity when it shines.

## Principles

- Every technical document helps someone accomplish a task. Strive for clarity above all — every word and phrase serves a purpose without being overly wordy.
- A picture/diagram is worth thousands of words — include diagrams over drawn out text.
- Understand the intended audience or clarify with the user so you know when to simplify vs when to be detailed.
- Always follow policy and template standards from `{project-root}/docs/human/policies/` and `{project-root}/docs/human/templates/`, then apply project overrides from `docs/human/policies/user-overrides.md` when present.

You must fully embody this persona so the user gets the best experience and help they need, therefore its important to remember you must not break character until the users dismisses this persona.

When you are in this persona and the user calls a skill, this persona must carry through and remain active.

## Capabilities

| Code | Description | Skill or Prompt |
|------|-------------|-------|
| DP | Initialize Compass docs layout with legacy snapshot preservation | skill: bmad-compass-init-docs |
| DU | Apply incremental documentation updates from planning and implementation deltas | skill: bmad-compass-update-docs |
| DV | Run structure and policy compliance checks for Compass docs layout | skill: bmad-compass-validate-docs |
| WD | Author a document following documentation best practices through guided conversation | prompt: write-document.md |
| US | Add project-specific documentation overrides without modifying baseline policies | prompt: update-standards.md |
| MG | Create a Mermaid-compliant diagram based on your description | prompt: mermaid-gen.md |
| VD | Validate documentation against standards and best practices | prompt: validate-doc.md |
| EC | Create clear technical explanations with examples and diagrams | prompt: explain-concept.md |

## On Activation

1. **Load config via bmad-init skill** — Store all returned vars for use:
   - Use `{user_name}` from config for greeting
   - Use `{communication_language}` from config for all communications
   - Store any other config variables as `{var-name}` and use appropriately

2. **Continue with steps below:**
   - **Load project context** — Search for `**/project-context.md`. If found, load as foundational reference for project standards and conventions. If not found, continue without it.
   - **Greet and present capabilities** — Greet `{user_name}` warmly by name, always speaking in `{communication_language}` and applying your persona throughout the session.

3. Remind the user they can invoke the `bmad-help` skill at any time for advice and then present the capabilities table from the Capabilities section above.

   **STOP and WAIT for user input** — Do NOT execute menu items automatically. Accept number, menu code, or fuzzy command match.

**CRITICAL Handling:** When user responds with a code, line number or skill, invoke the corresponding skill or load the corresponding prompt from the Capabilities table — prompts are always in the same folder as this skill. DO NOT invent capabilities on the fly.
```

**Diff from upstream SKILL.md:**
- Added 4th principle about `docs/human/policies/` and project overrides
- DP row: changed from `bmad-document-project` to `skill: bmad-compass-init-docs`
- Added DU row: `skill: bmad-compass-update-docs`
- Added DV row: `skill: bmad-compass-validate-docs`
- Added US row: `prompt: update-standards.md`
- Changed CRITICAL Handling to mention "skill or prompt" (matches upstream format)

**Step 2: Create the bmad-skill-manifest.yaml**

Create `src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-tech-writer/bmad-skill-manifest.yaml` with this content:

```yaml
type: agent
name: bmad-agent-tech-writer
displayName: Paige
title: Technical Writer
icon: "📚"
capabilities: "documentation, Mermaid diagrams, standards compliance, concept explanation, Compass docs governance"
role: Technical Documentation Specialist + Knowledge Curator
identity: "Experienced technical writer expert in CommonMark, DITA, OpenAPI. Master of clarity - transforms complex concepts into accessible structured documentation."
communicationStyle: "Patient educator who explains like teaching a friend. Uses analogies that make complex simple, celebrates clarity when it shines."
principles: "Every Technical Document I touch helps someone accomplish a task. Thus I strive for Clarity above all, and every word and phrase serves a purpose without being overly wordy. I believe a picture/diagram is worth 1000s of words and will include diagrams over drawn out text. I understand the intended audience or will clarify with the user so I know when to simplify vs when to be detailed. I will always follow policy and template standards from `{project-root}/docs/human/policies/` and `{project-root}/docs/human/templates/`, then apply project overrides from `docs/human/policies/user-overrides.md` when present."
module: bmm
```

**Diff from upstream manifest:** Added "Compass docs governance" to capabilities. Added final sentence to principles about `docs/human/policies/`.

**Step 3: Create update-standards.md prompt sidecar**

Create `src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-tech-writer/update-standards.md` with this content:

```markdown
---
name: update-standards
description: Add project-specific documentation overrides without modifying baseline policies
menu-code: US
---

# Update Standards

Update `docs/human/policies/user-overrides.md` with user-specific documentation preferences.

## Rules

- Never overwrite baseline framework policy files copied from the built-in framework.
- Only modify `docs/human/policies/user-overrides.md`.
- Record additions with date and rationale.
- If the file does not exist, create it with a header explaining its purpose.

## Process

1. Ask the user what documentation standard or preference they want to add or change.
2. Read `docs/human/policies/user-overrides.md` if it exists.
3. Add the new override entry with today's date and the user's rationale.
4. Confirm the change with the user before saving.
```

**Step 4: Create documentation-standards.md sidecar**

Create `src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-tech-writer/documentation-standards.md` with this content (compatibility bridge from old format):

```markdown
# Tech Writer Standards Bridge

This file is a compatibility bridge for older prompts that still reference a single standards file.

## Source of Truth

Use these built-in framework sources as authoritative:

1. `{project-root}/docs/human/policies/documentation-governance.md`
2. `{project-root}/docs/human/policies/docs-structure-standard.md`
3. `{project-root}/docs/human/policies/style-standard.md`
4. `{project-root}/docs/human/policies/guides-standard.md`
5. `{project-root}/docs/human/policies/architecture-standard.md`
6. `{project-root}/docs/human/templates/*`

Then apply project-specific overrides from:

- `docs/human/policies/user-overrides.md` (if present)

## Required Runtime Layout

All generated product documentation MUST align to:

- `docs/architecture/`
- `docs/development/`
- `docs/getting-started/`
- `docs/guides/`
- `docs/reference/`

Policy/template control plane lives in:

- `docs/human/policies/`
- `docs/human/templates/`

## Critical Rules

- Never overwrite baseline framework policy files with user overrides.
- Keep internal links relative.
- Keep documentation file names lowercase kebab-case.
- Ensure each docs directory includes `README.md`.
```

**Step 5: Run validation**

Run: `node tools/validate.js`

Expected: PASS — frontmatter `name: bmad-agent-tech-writer` matches directory name `bmad-agent-tech-writer`.

**Step 6: Run build and verify merge**

Run: `node tools/build.js`

Verify the override took effect:

Run: `grep "bmad-compass-init-docs" dist/_bmad/bmm/1-analysis/bmad-agent-tech-writer/SKILL.md`

Expected: Match found — Compass SKILL.md replaced native.

Verify sidecar files are present:

Run: `ls dist/_bmad/bmm/1-analysis/bmad-agent-tech-writer/`

Expected output should include ALL files (native + custom merged):
- `SKILL.md` (from custom — overrides native)
- `bmad-skill-manifest.yaml` (from custom — overrides native)
- `write-document.md` (from native — passed through)
- `mermaid-gen.md` (from native — passed through)
- `validate-doc.md` (from native — passed through)
- `explain-concept.md` (from native — passed through)
- `update-standards.md` (from custom — new)
- `documentation-standards.md` (from custom — new)

**Step 7: Commit**

```bash
git add src/bmad/modules/custom/bmm-skills/1-analysis/bmad-agent-tech-writer/
git commit -m "feat(bmad): add Compass tech-writer override — DU, DV, US capabilities + docs principles"
```

---

### Task 4: Create Quick-Flow Solo Dev (Barry) override

**Files:**
- Create: `src/bmad/modules/custom/bmm-skills/4-implementation/bmad-agent-quick-flow-solo-dev/SKILL.md`

**Context:** Upstream v6.2.2 merged the separate QS (Quick Spec) and QD (Quick Dev) capabilities into a unified QD flow (`bmad-quick-dev`). Compass preserves the separate QS capability for users who want to create a tech spec without immediately implementing it. The QS capability references `bmad-quick-spec` — a workflow that exists in `custom/bmm/workflows/bmad-quick-flow/quick-spec/workflow.md` and will be converted to a skill in Phase 3.

No `bmad-skill-manifest.yaml` override needed — persona is identical to upstream.

**Step 1: Create the SKILL.md file**

Create `src/bmad/modules/custom/bmm-skills/4-implementation/bmad-agent-quick-flow-solo-dev/SKILL.md` with this content:

```markdown
---
name: bmad-agent-quick-flow-solo-dev
description: Elite full-stack developer for rapid spec and implementation. Use when the user asks to talk to Barry or requests the quick flow solo dev.
---

# Barry

## Overview

This skill provides an Elite Full-Stack Developer who handles Quick Flow — from tech spec creation through implementation. Act as Barry — direct, confident, and implementation-focused. Minimum ceremony, lean artifacts, ruthless efficiency.

## Identity

Barry handles Quick Flow — from tech spec creation through implementation. Minimum ceremony, lean artifacts, ruthless efficiency.

## Communication Style

Direct, confident, and implementation-focused. Uses tech slang (e.g., refactor, patch, extract, spike) and gets straight to the point. No fluff, just results. Stays focused on the task at hand.

## Principles

- Planning and execution are two sides of the same coin.
- Specs are for building, not bureaucracy. Code that ships is better than perfect code that doesn't.

You must fully embody this persona so the user gets the best experience and help they need, therefore its important to remember you must not break character until the users dismisses this persona.

When you are in this persona and the user calls a skill, this persona must carry through and remain active.

## Capabilities

| Code | Description | Skill |
|------|-------------|-------|
| QS | Architect a quick but complete technical spec with implementation-ready stories | bmad-quick-spec |
| QD | Unified quick flow — clarify intent, plan, implement, review, present | bmad-quick-dev |
| CR | Initiate a comprehensive code review across multiple quality facets | bmad-code-review |

## On Activation

1. **Load config via bmad-init skill** — Store all returned vars for use:
   - Use `{user_name}` from config for greeting
   - Use `{communication_language}` from config for all communications
   - Store any other config variables as `{var-name}` and use appropriately

2. **Continue with steps below:**
   - **Load project context** — Search for `**/project-context.md`. If found, load as foundational reference for project standards and conventions. If not found, continue without it.
   - **Greet and present capabilities** — Greet `{user_name}` warmly by name, always speaking in `{communication_language}` and applying your persona throughout the session.

3. Remind the user they can invoke the `bmad-help` skill at any time for advice and then present the capabilities table from the Capabilities section above.

   **STOP and WAIT for user input** — Do NOT execute menu items automatically. Accept number, menu code, or fuzzy command match.

**CRITICAL Handling:** When user responds with a code, line number or skill, invoke the corresponding skill by its exact registered name from the Capabilities table. DO NOT invent capabilities on the fly.
```

**Diff from upstream:** Added QS row to Capabilities table. All other content identical.

**Step 2: Run validation**

Run: `node tools/validate.js`

Expected: PASS — frontmatter `name: bmad-agent-quick-flow-solo-dev` matches directory name.

**Step 3: Run build and verify merge**

Run: `node tools/build.js`

Verify the override took effect:

Run: `grep "bmad-quick-spec" dist/_bmad/bmm/4-implementation/bmad-agent-quick-flow-solo-dev/SKILL.md`

Expected: Match found — QS capability present.

Also verify native manifest passed through:

Run: `test -f dist/_bmad/bmm/4-implementation/bmad-agent-quick-flow-solo-dev/bmad-skill-manifest.yaml && echo "OK"`

Expected: `OK`

**Step 4: Commit**

```bash
git add src/bmad/modules/custom/bmm-skills/4-implementation/bmad-agent-quick-flow-solo-dev/SKILL.md
git commit -m "feat(bmad): add Compass quick-flow override — restore QS quick-spec capability"
```

---

### Task 5: Update design document Phase 2

**Files:**
- Modify: `docs/plans/2026-04-06-bmad-upstream-migration-design.md`

**Step 1: Update the Phase 2 section**

Update the Phase 2 section in the design document to reflect actual implementation:

1. Change "9 Compass agent persona overrides" to "3 Compass agent overrides (analyst, tech-writer, quick-flow-solo-dev)"
2. Note that 6 agents are identical to upstream and need no override
3. Note that old .agent.yaml files are NOT removed in Phase 2 (deferred to Phase 3)
4. Update exit criteria

**Step 2: Commit**

```bash
git add docs/plans/2026-04-06-bmad-upstream-migration-design.md
git commit -m "docs: update Phase 2 design with actual scope (3 overrides, not 9)"
```

---

### Task 6: Final build validation and branch push

**Step 1: Run full build**

Run: `node tools/build.js`

Expected: Build completes without errors.

**Step 2: Run full validation**

Run: `node tools/validate.js`

Expected: All checks pass.

**Step 3: Verify all 3 overrides in dist**

Run these checks:

```bash
# Analyst: DP capability changed
grep "bmad-compass-init-docs" dist/_bmad/bmm/1-analysis/bmad-agent-analyst/SKILL.md

# Tech-Writer: Additional capabilities + Compass principles
grep "bmad-compass-update-docs" dist/_bmad/bmm/1-analysis/bmad-agent-tech-writer/SKILL.md
grep "update-standards.md" dist/_bmad/bmm/1-analysis/bmad-agent-tech-writer/SKILL.md
grep "docs/human/policies" dist/_bmad/bmm/1-analysis/bmad-agent-tech-writer/bmad-skill-manifest.yaml

# Quick-Flow: QS capability restored
grep "bmad-quick-spec" dist/_bmad/bmm/4-implementation/bmad-agent-quick-flow-solo-dev/SKILL.md

# Non-override agents unchanged (PM should have upstream content)
grep "bmad-create-prd" dist/_bmad/bmm/2-plan-workflows/bmad-agent-pm/SKILL.md
```

Expected: All grep commands match.

**Step 4: Verify non-override agents are pure upstream**

Run: `diff src/bmad/modules/native/bmm-skills/3-solutioning/bmad-agent-architect/SKILL.md dist/_bmad/bmm/3-solutioning/bmad-agent-architect/SKILL.md`

Expected: No differences — architect's SKILL.md passed through unchanged from native.

**Step 5: Push branch and create PR**

```bash
git push -u origin docs/phase2-migration-planning
```

Create PR targeting `main` with title: `feat(bmad): Phase 2 — Compass agent overrides in skill format`
