# Oversight Substrate Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an optional risk/assumption tracking layer to BMAD that agents populate during work and verification checkpoints surface at gate approvals and story completion.

**Architecture:** Two YAML files (`risks.yaml`, `assumptions.yaml`) in `planning/current/oversight/` accumulate entries across sessions. Agents append `draft` entries during decision-making workflows. A checkpoint workflow generates verification reports at gate approvals (roadmap, PRD, architecture, readiness) and story completion, surfacing unreviewed items for user confirmation. Enabled by default via `oversight_mode` config flag.

**Tech Stack:** YAML data files, Markdown checkpoint reports, BMAD workflow instructions

---

## Task 1: Add oversight config variables

**Files:**
- Modify: `src/bmad/modules/custom/bmm/config.yaml`

**Step 1: Add oversight variables to config.yaml**

Read the file first. Then append after the `current_secure_release_gate_dir` line (around line 69):

```yaml
# Oversight substrate
oversight_mode: true
current_oversight_dir: "{planning_current}/oversight"
current_oversight_risks_file: "{current_oversight_dir}/risks.yaml"
current_oversight_assumptions_file: "{current_oversight_dir}/assumptions.yaml"
```

**Step 2: Commit**

```bash
git add src/bmad/modules/custom/bmm/config.yaml
git commit -m "feat(oversight): add oversight config variables"
```

---

## Task 2: Create oversight YAML templates

**Files:**
- Create: `src/planning/templates/oversight/risks.yaml`
- Create: `src/planning/templates/oversight/assumptions.yaml`

**Step 1: Create risks.yaml template**

Create `src/planning/templates/oversight/risks.yaml`:

```yaml
# Oversight risk register — agents append draft entries during decision-making workflows.
# Verification checkpoints surface unreviewed items at gate approvals.
#
# Schema:
#   id: risk-NNN
#   summary: one-line description
#   source_workflow: workflow that raised this risk
#   source_step: step within the workflow
#   raised_at: YYYY-MM-DD
#   status: draft | confirmed | mitigated | dismissed
#   severity: low | medium | high | critical
#   mitigation: description of mitigation (empty until documented)
#   resolved_at: YYYY-MM-DD (empty until resolved)
[]
```

**Step 2: Create assumptions.yaml template**

Create `src/planning/templates/oversight/assumptions.yaml`:

```yaml
# Oversight assumption register — agents append draft entries during decision-making workflows.
# Verification checkpoints surface unvalidated assumptions at gate approvals.
#
# Schema:
#   id: assumption-NNN
#   summary: one-line description
#   source_workflow: workflow that raised this assumption
#   source_step: step within the workflow
#   raised_at: YYYY-MM-DD
#   status: draft | confirmed | invalidated | dismissed
#   validated_by: which workflow, test, or evidence confirmed this (empty until validated)
#   resolved_at: YYYY-MM-DD (empty until resolved)
[]
```

**Step 3: Commit**

```bash
git add src/planning/templates/oversight/
git commit -m "feat(oversight): add risk and assumption YAML templates"
```

---

## Task 3: Create the oversight-checkpoint workflow

**Files:**
- Create: `src/bmad/modules/custom/bmm/workflows/0-governance/oversight-checkpoint/workflow.md`

**Step 1: Create the checkpoint workflow**

Create the file with this content:

```markdown
---
name: oversight-checkpoint
description: 'Generate a verification report from the oversight risk and assumption registers. Use at gate approvals and story completion to surface unreviewed items.'
---

# Oversight Checkpoint Workflow

**Goal:** Surface unreviewed risks and assumptions before a gate approval or after story completion.

**Your Role:** You are a verification facilitator. Read the registers, generate the report, and present items for user review. Do not block — oversight is advisory.

## CONFIGURATION

Load config from `{project-root}/_bmad/modules/custom/bmm/config.yaml` and resolve:
- `oversight_mode`
- `current_oversight_dir`
- `current_oversight_risks_file`
- `current_oversight_assumptions_file`
- `current_evidence_dir`
- `date` as a system-generated value (`YYYY-MM-DD`)

If `oversight_mode` is `false`, skip this workflow entirely and return.

## INPUTS

This workflow expects a `gate_name` parameter indicating which checkpoint triggered it. Valid values: `roadmap`, `prd`, `architecture`, `readiness`, `story-completion`.

## EXECUTION

1. Read `{current_oversight_risks_file}` and `{current_oversight_assumptions_file}`. If either file does not exist or is empty, note it and continue with whatever is available.

2. Categorize entries:
   - **Unreviewed**: `status: draft` — these need user attention
   - **Open confirmed risks**: `status: confirmed` with empty `mitigation` — acknowledged but unmitigated
   - **Resolved**: `status: mitigated | dismissed | confirmed | invalidated` with non-empty `resolved_at` — no action needed

3. Generate the checkpoint report with this structure:

```
# Oversight Checkpoint: {{gate_name}}

**Generated:** {{date}}
**Gate:** {{gate_name}}
**Phase:** {{phase_id}}

## Unreviewed Items (draft)

### Risks
{{for each risk with status: draft}}
- **{{id}}** [{{severity}}]: {{summary}}
  - Source: {{source_workflow}} / {{source_step}}
  - Action needed: confirm or dismiss
{{end}}

### Assumptions
{{for each assumption with status: draft}}
- **{{id}}** [draft]: {{summary}}
  - Source: {{source_workflow}} / {{source_step}}
  - Action needed: confirm or invalidate
{{end}}

## Open Confirmed Risks

{{for each risk with status: confirmed and empty mitigation}}
- **{{id}}** [{{severity}}, confirmed]: {{summary}}
  - Mitigation: (none documented)
  - Action needed: document mitigation or accept risk
{{end}}

## Summary

| Category | Draft | Confirmed | Mitigated/Resolved |
|----------|-------|-----------|-------------------|
| Risks | {{count}} | {{count}} | {{count}} |
| Assumptions | {{count}} | {{count}} | {{count}} |

**Recommendation:** {{count of draft + unmitigated confirmed}} items require review before gate approval.
```

4. Write the report to `{current_evidence_dir}/oversight-checkpoint-{{gate_name}}.md`.

5. Present the report to the user inline and ask:
   - "Would you like to update any statuses before proceeding with the {{gate_name}} approval?"
   - If yes: accept user updates and write them back to the YAML files.
   - If no: proceed. Oversight is advisory, not blocking.

## OUTPUT RULES

- Do not generate a report if both register files are empty or missing.
- Do not block gate approval — always allow the user to proceed.
- Keep date format as `YYYY-MM-DD`.
- When updating statuses, set `resolved_at` to the current date for any item moved to a terminal status.
```

**Step 2: Commit**

```bash
git add src/bmad/modules/custom/bmm/workflows/0-governance/oversight-checkpoint/
git commit -m "feat(oversight): add oversight-checkpoint verification workflow"
```

---

## Task 4: Add oversight capture rules to decision-making workflows

**Files:**
- Modify: `src/bmad/modules/custom/bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md`
- Modify: `src/bmad/modules/custom/bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md`
- Modify: `src/bmad/modules/custom/bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md`
- Modify: `src/bmad/modules/custom/bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md`
- Modify: `src/bmad/modules/custom/bmm/workflows/4-implementation/dev-story/instructions.xml` (or `.md` — check actual extension)
- Plus native mirrors of each

**Step 1: Read each file to find the OUTPUT RULES or equivalent section**

For each file, find the OUTPUT RULES, COMPLETION SEQUENCE, or final instructions section.

**Step 2: Add the oversight capture block to each file**

Add this block to the OUTPUT RULES or end-of-workflow section of each file (before success metrics if present):

```markdown
## OVERSIGHT CAPTURE

When `{oversight_mode}` is `true`:

- If you identified any risk during this workflow (a dependency that might not hold, a scale concern, an integration uncertainty), append it to `{current_oversight_risks_file}`:
  ```yaml
  - id: risk-NNN  # increment from last entry
    summary: "<one-line description>"
    source_workflow: <this workflow name>
    source_step: <current step>
    raised_at: "{{date}}"
    status: draft
    severity: <low|medium|high|critical>
    mitigation: ""
    resolved_at: ""
  ```

- If you made or relied on any assumption that has not been verified (a technology capability, an environment constraint, a user behavior expectation), append it to `{current_oversight_assumptions_file}`:
  ```yaml
  - id: assumption-NNN  # increment from last entry
    summary: "<one-line description>"
    source_workflow: <this workflow name>
    source_step: <current step>
    raised_at: "{{date}}"
    status: draft
    validated_by: ""
    resolved_at: ""
  ```

- Do not pause work to discuss these entries. Log and continue.
- If the files do not exist yet, create them with the entry as the first item.
```

**Step 3: Apply to all listed files (custom copies)**

Add the block to each custom copy. Placement:
- `step-06-complete.md` (product brief): before the SYSTEM SUCCESS/FAILURE METRICS section
- `step-12-complete.md` (PRD): before the SUCCESS METRICS section
- `step-08-complete.md` (architecture): before the SUCCESS METRICS section
- `step-04-final-validation.md` (epics/stories): before the end of the file
- `dev-story` instructions: before the final completion section

**Step 4: Apply identical changes to native mirrors**

The native copies live at the same relative paths under `src/bmad/modules/native/bmm/workflows/`.

**Step 5: Commit**

```bash
git add src/bmad/modules/custom/ src/bmad/modules/native/
git commit -m "feat(oversight): add risk/assumption capture rules to decision workflows"
```

---

## Task 5: Add checkpoint triggers to gate approvals

**Files:**
- Modify: `src/bmad/tools/automation/commands/auto-plan.md`
- Modify: `src/bmad/modules/custom/bmm/workflows/4-implementation/sprint-status/instructions.md`
- Plus native mirror of sprint-status

**Step 1: Read auto-plan.md and find the four gate approval stops**

The gates are at steps 10 (roadmap), 23 (PRD), 30 (architecture), and 36 (readiness). Before each "stop for approval" instruction, add:

```markdown
If `{oversight_mode}` is `true`, run the oversight checkpoint workflow with `gate_name` set to `roadmap` (or `prd`, `architecture`, `readiness` respectively) before presenting the approval request. Include the checkpoint report in the gate artifact.
```

**Step 2: Read sprint-status instructions and find the story completion path**

At step 3, action 6 ("All implementation items are complete"), add:

```markdown
If `{oversight_mode}` is `true`, run the oversight checkpoint workflow with `gate_name` set to `story-completion` before confirming completion.
```

**Step 3: Apply the same change to the native sprint-status mirror**

**Step 4: Commit**

```bash
git add src/bmad/tools/automation/ src/bmad/modules/custom/ src/bmad/modules/native/
git commit -m "feat(oversight): add checkpoint triggers at gate approvals and story completion"
```

---

## Task 6: Register the checkpoint workflow in the manifest

**Files:**
- Modify: `src/bmad/_config/workflow-manifest.csv`
- Modify: `src/bmad/modules/custom/bmm/module-help.csv`

**Step 1: Read both CSV files to understand the format**

**Step 2: Add the oversight-checkpoint entry**

In `workflow-manifest.csv`, add a row for the oversight-checkpoint workflow in the `0-governance` phase, with:
- phase: `0-governance`
- sequence: after existing governance workflows
- workflow: `oversight-checkpoint`
- command: `bmad-bmm-oversight-checkpoint`
- agent: `pm`
- required: `false`
- outputs: `{current_evidence_dir}/oversight-checkpoint-*.md`

In `module-help.csv`, add a matching entry so help.md can recommend it.

**Step 3: Commit**

```bash
git add src/bmad/_config/ src/bmad/modules/custom/bmm/
git commit -m "feat(oversight): register oversight-checkpoint in workflow manifest"
```

---

## Task 7: Add the oversight-checkpoint command entry

**Files:**
- Create: `src/claude/commands/bmad/bmad-bmm-oversight-checkpoint.md`
- Create: `src/opencode/commands/bmad/bmad-bmm-oversight-checkpoint.md`

**Step 1: Read an existing command file for the pattern**

Read `src/claude/commands/bmad/bmad-bmm-phase-sync.md` to see the command format.

**Step 2: Create the Claude command**

Create `src/claude/commands/bmad/bmad-bmm-oversight-checkpoint.md` following the same pattern, pointing to the oversight-checkpoint workflow.

**Step 3: Create the OpenCode command**

Create `src/opencode/commands/bmad/bmad-bmm-oversight-checkpoint.md` following the same pattern.

**Step 4: Commit**

```bash
git add src/claude/commands/bmad/ src/opencode/commands/bmad/
git commit -m "feat(oversight): add oversight-checkpoint command for Claude and OpenCode"
```

---

## Task 8: Update init-planning to scaffold oversight directory

**Files:**
- Modify: `src/bmad/modules/custom/bmm/workflows/planning/init-planning/instructions.md`

**Step 1: Read the init-planning instructions**

Find where it creates the `planning/current/` directory structure.

**Step 2: Add oversight directory creation**

In the directory scaffolding section, add:

```markdown
- If `{oversight_mode}` is `true`, ensure `{current_oversight_dir}` exists. If it does not, create it and copy the template files from `{planning_templates_root}/oversight/risks.yaml` and `{planning_templates_root}/oversight/assumptions.yaml` into it.
```

**Step 3: Commit**

```bash
git add src/bmad/modules/custom/bmm/workflows/planning/init-planning/
git commit -m "feat(oversight): scaffold oversight directory in init-planning"
```

---

## Task 9: Build, validate, and verify

**Step 1: Run build**

Run: `npm run build`
Expected: Build completes with no errors.

**Step 2: Run full validation**

Run: `npm run check`
Expected: All checks pass.

**Step 3: Verify the oversight files are in dist**

Run: `ls dist/_bmad/modules/custom/bmm/workflows/0-governance/oversight-checkpoint/`
Expected: `workflow.md`

Run: `ls dist/planning/templates/oversight/`
Expected: `risks.yaml`, `assumptions.yaml`

**Step 4: Final commit if any adjustments needed**
