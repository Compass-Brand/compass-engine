---
name: phase-sync
description: 'Sync active phase metadata in planning/framework/current/phase.md. Use when the user says "sync phase", "update phase goals", or "check phase metadata".'
---

# Phase Sync Workflow

**Goal:** Keep `planning/framework/current/phase.md` current and decision-usable before and during delivery work.

**Your Role:** You are a planning facilitator ensuring phase metadata stays accurate, explicit, and actionable.

## CONFIGURATION

Load config from `{project-root}/_bmad/bmm/config.yaml` and resolve:
- `project_name`, `user_name`
- `communication_language`, `document_output_language`
- `planning_root`, `planning_current`, `phase_snapshot_file`
- `date` as a system-generated value (`YYYY-MM-DD`)

## EXECUTION

1. Ensure `{planning_current}` exists.
2. If `{phase_snapshot_file}` does not exist, create it with this structure:

```md
Status: active
Owner: {{user_name}}
Last Updated: {{date}}

# Phase Snapshot

## Phase
- Name:
- Slug:
- Start Date:
- Target End Date:

## Goals
1.
2.
3.

## Exit Criteria
1.
2.

## Current Risks
1.
2.

## This Week Focus
1.
2.
```

3. If file exists, update in place with user-provided changes:
   - phase identity
   - goals
   - exit criteria
   - risks
   - weekly focus
4. Always set:
   - `Status: active`
   - `Last Updated: {{date}}`
5. Confirm saved path: `{phase_snapshot_file}`

## OUTPUT RULES

- Keep date format as `YYYY-MM-DD`.
- Do not write phase metadata outside `{phase_snapshot_file}`.
- Do not archive in this workflow (use `phase-closeout`).
