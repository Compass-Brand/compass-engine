# Project Roadmap Workflow

<critical>The workflow engine is governed by: {project-root}/reference/BMAD/modules/custom/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and resolved: {project-root}/reference/BMAD/modules/custom/bmm/workflows/planning/project-roadmap/workflow.yaml</critical>
<critical>Communicate all responses in {communication_language}</critical>

## Goal

Turn high-level analysis into the authoritative roadmap control surface:

- human summary in `{roadmap_summary_file}`
- machine state in `{roadmap_state_file}`

This workflow is the project-level continuity layer that decides:

- what slice is active now
- what comes next
- what is deferred
- what depends on prior phases
- whether the slice is repo-local or orchestration-scoped
- which repos are targeted when orchestration is required
- which Beads parent or phase issues should own the approved active slice

## Step 1: Gather Roadmap Inputs

Inspect the roadmap-level source artifacts:

- `{roadmap_brainstorming_dir}`
- `{roadmap_market_research_dir}`
- `{roadmap_domain_research_dir}`
- `{roadmap_technical_research_dir}`
- `{roadmap_strategy_dir}`
- `{roadmap_storytelling_dir}` when storytelling is enabled
- `{roadmap_product_brief_dir}`
- existing `{roadmap_summary_file}` and `{roadmap_state_file}` if present
- `{planning_repositories_file}` when repo routing or child-repo orchestration is needed

If brownfield planning snapshots exist, use them as background context, not as the new source of truth.

## Step 2: Identify Candidate Phases and Sequencing

From the gathered inputs, derive:

- candidate roadmap slices or phases
- a recommended ordering
- dependencies between phases
- the recommended active phase
- deferred or future opportunities
- execution scope for each phase (`repo`, `orchestration`, or `workspace`)
- repo targets when execution scope is not `repo`
- major risks or assumptions that affect ordering

Keep the roadmap phase list concise and execution-oriented. Do not turn the roadmap into a backlog dump.

## Step 3: Draft the Roadmap Proposal

Write `{roadmap_proposal_file}` before changing authoritative roadmap state.

Include:

- proposed phase list with ids, titles, and objectives
- execution scope for each proposed phase
- repo targets for any workspace or orchestration phase
- proposed Beads parent or phase tracking issue strategy when new slices are being activated
- recommended active phase
- recommended next phase
- dependencies
- deferred work
- rationale for the ordering
- any gaps in the high-level inputs

Do not update `{roadmap_state_file}` yet.

## Step 4: Approval Checkpoint

Obtain explicit approval for:

- phase ordering
- active phase selection
- deferred or requeued work
- dependency chain

If the proposal is not approved:

- revise the proposal
- keep `{roadmap_state_file}` and `{roadmap_summary_file}` unchanged
- record unresolved gaps in `{default_output_file}` only if asked to emit a draft report

## Step 5: Update Authoritative Roadmap State

After approval:

1. Update `{roadmap_state_file}` first.
2. Set:
   - `version`
   - `project`
   - `owner`
   - `last_updated`
   - `active_phase_id`
   - `phases[]`
3. For each phase entry, populate at minimum:
   - `id`
   - `slug`
   - `title`
   - `status`
   - `execution_scope`
   - `objective`
   - `roadmap_order`
   - `depends_on`
   - `repo_targets`
   - `workstreams`
   - `dependency_edges`
   - `overlap_domains`
   - `integration_gates`
   - `entry_criteria`
   - `exit_criteria`
   - `supporting_docs`

Only approved state belongs in `{roadmap_state_file}`.

## Step 6: Update the Human Roadmap Summary

Update `{roadmap_summary_file}` second so it matches the approved machine state.

Ensure it includes:

- current horizon
- active phase and objective
- roadmap sequence table
- phase index
- deferred or future opportunities
- source artifact list
- change log entry for this update

If `{roadmap_state_file}` and `{roadmap_summary_file}` disagree, the YAML must win.

## Step 7: Emit Roadmap Update Report

Write `{default_output_file}` including:

- source artifacts inspected
- approved active phase
- approved next phase
- approved execution scope
- approved repo targets
- deferred work
- key sequencing rationale
- remaining gaps or assumptions
- recommended next command: `/bmad-bmm-phase-sync`

## Step 8: Boundary Rule

Do not update `current/phase.md` or `current/phase-state.yaml` here.

Roadmap work stays in `roadmap/`.
`Phase Sync` owns activation of the approved active slice into `current/`.
