# Whitepaper Ingestion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an optional whitepaper ingestion step to the BMAD analysis phase that summarizes external markdown whitepapers into a digest consumed by downstream workflows.

**Architecture:** Users drop `.md` whitepapers into `planning/roadmap/whitepapers/`. A new ingest workflow reads them, extracts key themes/requirements/constraints, and generates `whitepapers-digest.md`. Downstream init steps discover the digest via existing glob patterns plus new `*whitepaper*` and `*digest*` patterns.

**Tech Stack:** Markdown workflow instructions, BMAD workflow manifest CSV

---

## Task 1: Create the ingest-whitepapers workflow

**Files:**
- Create: `src/bmad/modules/custom/bmm/workflows/1-analysis/ingest-whitepapers/workflow.md`

**Step 1: Create the workflow file**

```markdown
---
name: ingest-whitepapers
description: 'Ingest external whitepapers into a condensed digest for downstream BMAD workflows. Use when the user has placed markdown whitepapers in planning/roadmap/whitepapers/ and wants them incorporated into the analysis phase.'
---

# Ingest Whitepapers Workflow

**Goal:** Summarize external whitepapers into a single digest that downstream workflows can discover and consume efficiently.

**Your Role:** You are a research analyst. Read each whitepaper, extract the signal, and produce a structured digest. Do not editorialize — preserve the author's intent.

## CONFIGURATION

Load config from `{project-root}/_bmad/modules/custom/bmm/config.yaml` and resolve:
- `planning_roadmap`
- `date` as a system-generated value (`YYYY-MM-DD`)

The whitepapers directory is `{planning_roadmap}/whitepapers/`.
The digest output is `{planning_roadmap}/whitepapers/whitepapers-digest.md`.

## EXECUTION

1. Check if `{planning_roadmap}/whitepapers/` exists. If it does not exist or contains no `.md` files (excluding `whitepapers-digest.md` itself), report "No whitepapers found" and return.

2. List all `.md` files in the directory (excluding `whitepapers-digest.md`). Report the count to the user:
   "Found {{count}} whitepaper(s) in `planning/roadmap/whitepapers/`. Ingesting now."

3. For each whitepaper, read the full content and extract:
   - **Key ideas**: the core concepts, proposals, or innovations described
   - **Requirements or goals mentioned**: anything that reads like a requirement, success criterion, or project goal
   - **Technical constraints or preferences**: technology choices, architectural patterns, scale expectations, or limitations
   - **Decisions or recommendations**: explicit recommendations the author makes

4. After processing all whitepapers, identify **cross-cutting themes** — ideas, requirements, or constraints that appear in more than one whitepaper. Note which documents each theme appears in.

5. Generate `{planning_roadmap}/whitepapers/whitepapers-digest.md` with this structure:

```
# Whitepapers Digest

**Generated:** {{date}}
**Source:** planning/roadmap/whitepapers/
**Documents ingested:** {{count}}

## Cross-Cutting Themes

{{for each theme that appears in 2+ documents}}
- **{{theme}}**: {{description}} (appears in: {{doc-a.md}}, {{doc-b.md}})
{{end}}
{{if no cross-cutting themes: "No cross-cutting themes detected across documents."}}

## Per-Document Summaries

### {{filename}} — "{{title or first heading}}"

**Key ideas:**
- {{idea}}

**Requirements or goals mentioned:**
- {{requirement}}

**Technical constraints or preferences:**
- {{constraint}}

**Decisions or recommendations:**
- {{recommendation}}

{{repeat for each whitepaper}}
```

6. Report completion:
   "Digest generated at `planning/roadmap/whitepapers/whitepapers-digest.md` with {{count}} document(s) summarized. Downstream workflows (product brief, PRD) will discover this automatically."

## OUTPUT RULES

- The digest replaces any previous digest — it is regenerated from all whitepapers each time.
- Preserve the author's intent in summaries. Do not add analysis or recommendations beyond what the whitepaper states.
- If a whitepaper has no content for a category (e.g., no technical constraints), omit that category header for that document rather than writing "None."
- Keep summaries concise — each per-document section should be 100-200 words, not a full reproduction.
- Do not modify the original whitepaper files.
```

**Step 2: Commit**

```bash
git add src/bmad/modules/custom/bmm/workflows/1-analysis/ingest-whitepapers/
git commit -m "feat: add ingest-whitepapers workflow for BMAD analysis phase"
```

---

## Task 2: Create command entries for Claude and OpenCode

**Files:**
- Create: `src/claude/commands/bmad/bmad-bmm-ingest-whitepapers.md`
- Create: `src/opencode/commands/bmad/bmad-bmm-ingest-whitepapers.md`

**Step 1: Read the pattern from an existing command**

Read `src/claude/commands/bmad/bmad-bmm-oversight-checkpoint.md` for the format.

**Step 2: Create the Claude command**

Create `src/claude/commands/bmad/bmad-bmm-ingest-whitepapers.md` following the same pattern:
- Name: `bmad-bmm-ingest-whitepapers`
- Description: "Ingest external whitepapers into a condensed digest for downstream BMAD workflows."
- Scope: analysis (phase 1)
- Primary agent: Analyst
- Workflow path: `_bmad/modules/custom/bmm/workflows/1-analysis/ingest-whitepapers/workflow.md`
- Expected outputs: whitepapers-digest.md

**Step 3: Create the OpenCode command**

Read `src/opencode/commands/bmad/bmad-bmm-oversight-checkpoint.md` for the OpenCode format. Create `src/opencode/commands/bmad/bmad-bmm-ingest-whitepapers.md` with the same content adapted for OpenCode.

**Step 4: Commit**

```bash
git add src/claude/commands/bmad/ src/opencode/commands/bmad/
git commit -m "feat: add ingest-whitepapers command for Claude and OpenCode"
```

---

## Task 3: Register in workflow manifest and help CSV

**Files:**
- Modify: `src/bmad/_config/workflow-manifest.csv`
- Modify: `src/bmad/modules/custom/bmm/module-help.csv`

**Step 1: Read both CSVs to understand format**

**Step 2: Add to workflow-manifest.csv**

Add a new row (maintain alphabetical ordering by name):
```
"bmad-bmm-ingest-whitepapers","Ingest external whitepapers into a condensed digest for downstream BMAD workflows.","bmm","_bmad/modules/custom/bmm/workflows/1-analysis/ingest-whitepapers/workflow.md"
```

**Step 3: Add to module-help.csv**

Add a new row in the `1-analysis` phase section (or a suitable location before `2-plan`):
- module: `bmm`
- phase: `1-analysis`
- name: `Ingest Whitepapers`
- code: `IW`
- sequence: `5` (before research workflows)
- workflow-file: `_bmad/modules/custom/bmm/workflows/1-analysis/ingest-whitepapers/workflow.md`
- command: `bmad-bmm-ingest-whitepapers`
- required: `false`
- agent: `analyst`
- options: `Create Mode`
- description: `Ingest external whitepapers into a condensed digest for downstream BMAD workflows.`
- output-location: `planning_roadmap`
- outputs: `whitepapers-digest.md`

**Step 4: Commit**

```bash
git add src/bmad/_config/ src/bmad/modules/custom/bmm/
git commit -m "feat: register ingest-whitepapers in workflow manifest and help"
```

---

## Task 4: Add whitepaper/digest discovery to product brief init

**Files:**
- Modify: `src/bmad/modules/custom/bmm/workflows/1-analysis/create-product-brief/steps/step-01-init.md`
- Modify: `src/bmad/modules/native/bmm/workflows/1-analysis/create-product-brief/steps/step-01-init.md`

**Step 1: Read the custom copy**

Find the "Try to discover the following:" section (around line 97-105).

**Step 2: Add whitepaper digest to discovery list**

After the existing discovery targets (Brainstorming Reports, Research Documents, etc.), add:

```markdown
- Whitepapers Digest (`{planning_roadmap}/whitepapers/whitepapers-digest.md` or `*whitepaper*digest*.md`)
```

**Step 3: Add to Primary Inputs classification**

In the "Primary Inputs" tier of the Source Classification section (around line 114-119), add:

```markdown
   - Whitepapers digest (`*whitepaper*digest*.md`)
```

**Step 4: Apply the same changes to the native mirror**

**Step 5: Commit**

```bash
git add src/bmad/modules/custom/ src/bmad/modules/native/
git commit -m "feat: add whitepaper digest discovery to product brief init"
```

---

## Task 5: Add whitepaper/digest discovery to PRD init

**Files:**
- Modify: `src/bmad/modules/custom/bmm/workflows/2-plan-workflows/create-prd/steps-c/step-01-init.md`
- Modify: `src/bmad/modules/native/bmm/workflows/2-plan-workflows/create-prd/steps-c/step-01-init.md`

**Step 1: Read the custom copy**

Find the discovery targets section (similar location to product brief init).

**Step 2: Add whitepaper digest to discovery list**

Add to the discovery list:

```markdown
- Whitepapers Digest (`{planning_roadmap}/whitepapers/whitepapers-digest.md` or `*whitepaper*digest*.md`)
```

**Step 3: Add to Primary Inputs classification**

In the Primary Inputs tier, add:

```markdown
   - Whitepapers digest (`*whitepaper*digest*.md`)
```

**Step 4: Apply the same changes to the native mirror**

**Step 5: Commit**

```bash
git add src/bmad/modules/custom/ src/bmad/modules/native/
git commit -m "feat: add whitepaper digest discovery to PRD init"
```

---

## Task 6: Build, validate, and verify

**Step 1: Run build**

Run: `npm run build`
Expected: Build completes with no errors.

**Step 2: Run full validation**

Run: `npm run check`
Expected: All checks pass.

**Step 3: Verify the ingest workflow is in dist**

Run: `ls dist/_bmad/modules/custom/bmm/workflows/1-analysis/ingest-whitepapers/`
Expected: `workflow.md`

**Step 4: Verify the command files are in dist**

Run: `ls dist/.claude/commands/bmad/bmad-bmm-ingest-whitepapers.md`
Expected: File exists.
