# BMAD Automation Wrappers

This guide explains the automation orchestration layer that wraps the canonical Compass BMAD workflow into repeatable, checkpoint-driven sequences.

## What Automation Wrappers Are

The BMAD workflow defined in `BMAD-workflow.md` is a human-readable gate chain: a developer invokes individual slash commands (e.g., `/bmad-bmm-create-prd`, `/bmad-bmm-create-architecture`) one at a time, making decisions at each step. Automation wrappers sit above that workflow and orchestrate multiple steps into a single coordinated run with deterministic state tracking, staged approvals, and resume capability.

Key differences from direct workflow invocation:

| Concern | Direct Workflow | Automation Wrapper |
| --- | --- | --- |
| Invocation | One slash command per step | One wrapper command covers many steps |
| State tracking | Manual; developer remembers progress | Machine-readable YAML state files |
| Approvals | Ad hoc | Explicit gate checkpoints with structured reports |
| Resume after failure | Start over or improvise | Deterministic resume from last accepted checkpoint |
| Draft management | Developer manages file placement | Wrapper enforces draft-vs-canonical locations |
| Context loading | Developer loads whatever seems relevant | Policy-driven minimum-context loading |

Wrappers do not replace the workflow. They automate the sequencing, state management, and approval bookkeeping around it.

## The Four Wrappers

| Wrapper | Scope | Workflow Phases Covered |
| --- | --- | --- |
| `auto-plan` | Initialization through implementation readiness | Setup, Analysis, Roadmap, Detailed Analysis, Planning Experience, Solutioning |
| `auto-epic-start` | Epic kickoff and baseline prep | Epic validation, story ordering, test design |
| `auto-story` | One story loop from validation through merge | Story validation, ATDD, reuse scan, implementation, test automation, review, traceability |
| `auto-epic-end` | Epic closeout and next-epic handoff | Evidence gathering, retrospective, docs delta, next-epic preview |

Together these four wrappers cover the full delivery lifecycle after project setup. A typical run flows: `auto-plan` once per phase, then for each epic: `auto-epic-start`, repeated `auto-story` calls for each story, and `auto-epic-end` to close.

## Current Status

Automation wrappers are **spec-only orchestration contracts**. They are:

- Fully specified in `src/bmad/tools/automation/`
- Documented with exact step sequences, state schemas, and approval models
- Referenced in `BMAD-workflow.md` under "Automation Wrappers (Reference-Stage Orchestration Layer)"

They are **not yet**:

- Cataloged in `module-help.csv` as runtime slash commands
- Backed by a plugin runtime, background jobs, or scheduled automation
- Available as executable commands in the deployed client surfaces

The specs define the contract that a future runtime implementation must follow. Until then, developers can use the specs as structured checklists for manual orchestration.

## State Model

Automation state lives in YAML files, never in TodoWrite or in reviewer-facing markdown reports.

### Authority Order

When files disagree, the resolution order is:

1. `roadmap.yaml` wins over `roadmap.md`
2. `phase-state.yaml` wins over `phase.md`
3. `auto-plan-state.yaml` wins over reviewer-facing draft gate documents

### Runtime State Files

**`auto-plan-state.yaml`** is the primary runtime state file for `auto-plan`. It tracks:

- `version`, `command`, `phase_id`, `run_status`
- `lane_decisions` and `lane_outcomes` (storytelling, WDS, security)
- `approval_markers` for each gate (roadmap, PRD, architecture, readiness)
- `review_artifacts` pointing to gate package paths
- `beads` issue references (parent, phase, epic, story, follow-ups)
- `artifact_paths` (current, canonical, draft locations per artifact)
- `artifact_revisions` (current revision, approved revision, state, timestamp)
- `automation_state` (last step, last checkpoint, pending approval, stale outputs, derived-from map)
- `draft_artifacts` tracking each draft with path, revision, derived-from, status, and supersedes

**`phase-state.yaml`** becomes the canonical machine state after Phase Sync runs. From that point on, every checkpoint update must be written to both `auto-plan-state.yaml` and `phase-state.yaml`.

### Beads Integration

Both state files include a `beads` object tracking issue references:

| Field | Purpose |
| --- | --- |
| `parent_issue_id` | Parent initiative or orchestration issue |
| `phase_issue_id` | Active Beads issue for the current roadmap slice |
| `active_epic_issue_id` | Set when epic execution is approved |
| `active_story_issue_id` | Set when a story is claimed for implementation |
| `follow_up_issue_ids` | Discovered blockers, defects, or deferred work |
| `last_synced_at` | Timestamp of the last `bd sync` |

These are references into Beads, not a replacement. Status, assignee, and closure truth stays in `bd`.

## Approval Model

Approvals are structured gate objects, not simple booleans. Each gate carries:

- `status`: `not_requested` | `pending` | `approved` | `rejected`
- `requested_revision`: the artifact revision submitted for review
- `approved_revision`: the revision that was accepted
- `reviewed_by` and `reviewed_at`: audit trail

### Checkpoints by Wrapper

| Wrapper | Approval Checkpoints |
| --- | --- |
| `auto-plan` | Roadmap activation, PRD acceptance, Architecture acceptance, Implementation readiness |
| `auto-epic-start` | Scope expansion, material story reordering, new architectural patterns |
| `auto-story` | Hard-stop changes (net-new architecture, destructive schema work), merge/story-complete |
| `auto-epic-end` | Epic-complete decision, carry-over of incomplete stories, docs promotion, advancing with open blockers |

### Rejection Cascades

Rejections trigger structured invalidation of downstream artifacts:

- **Roadmap rejected**: canonical roadmap files untouched; proposal stays as draft
- **PRD rejected**: WDS, architecture, draft epics/stories, and readiness outputs marked stale; architecture and readiness approvals downgraded
- **Architecture rejected**: security review, test design, draft epics/stories, and readiness outputs marked stale; readiness approval downgraded
- **Readiness rejected**: epics, stories, and readiness outputs stay in draft locations

Resume after rejection regenerates every stale output before continuing.

### Hard Stops

Automation must stop and wait for human approval when:

- Any of the four `auto-plan` gates is pending
- A blocking risk affects the current checkpoint
- A story triggers a hard-stop change category (net-new architecture, destructive migration)

## Context Budgeting

Wrappers follow a minimum-context loading policy to keep runs deterministic and cost-effective.

### Core Rules

1. Load only the context required for the current checkpoint
2. Prefer sharded planning artifacts over large omnibus documents
3. Re-read only artifacts that changed since the last accepted checkpoint
4. Use machine state to decide what to reload, not memory
5. Never load future workflow steps or unrelated artifacts speculatively

### Per-Wrapper Loading

| Wrapper | Primary Context | Excluded by Default |
| --- | --- | --- |
| `auto-plan` | Runtime state, phase state, roadmap YAML/MD, current-slice artifacts | Full codebase (greenfield), unrelated slices |
| `auto-epic-start` | Phase state, target epic, architecture, WDS, prior retro | Unrelated epics, completed stories |
| `auto-story` | Phase state, target story, minimum PRD/WDS/arch slices, touched codebase surfaces | Full PRD, full architecture, broad repo scans |
| `auto-epic-end` | Target epic, story statuses, review/traceability evidence, roadmap/phase for carry-over | Deep planning history |

### Refresh Triggers

Context is reloaded when: an approval is rejected, a revision changes, a stale-output record exists for an artifact being reused, or a blocking risk is added.

## Patching Strategy

The patching strategy governs how automation mutates artifacts without corrupting canonical state.

### Draft-First Rule

All gate-dependent outputs start in draft locations:

- Roadmap proposals, PRD gate packages, architecture gate packages
- Draft epics and stories
- Readiness and secure readiness gate packages

### Canonical Write Rule

Canonical locations are updated only when:

1. The relevant approval checkpoint is `approved`
2. The approved revision matches the current revision
3. No stale-output record exists for the artifact

### Write Order

Writes always follow: machine state first, then human-readable state, then downstream artifacts. For example, roadmap changes flow as:

1. Draft proposal artifact
2. Update runtime state
3. Stop for approval
4. Update `roadmap.yaml` (machine)
5. Update `roadmap.md` (human)

### Promotion

Draft artifacts are promoted to canonical locations only when approval is accepted, revisions match, derived inputs are current, and no stale-output records remain. Promotion updates `artifact_paths.current` to canonical, sets `artifact_revisions.state=approved`, and clears the draft record.

### Failure Safety

On failure, automation writes a partial-failure report, records the failure in runtime state, preserves completed artifacts, and records the last successful step. Draft artifacts are never silently promoted.

### Reuse Scan

Before story implementation, `auto-story` performs a mandatory reuse scan across: UI components, domain services, data-access layers, integration clients, shared utilities, test fixtures, and prior ADRs. The scan produces evidence documenting what was searched, what candidates were found, what was reused, and why net-new code was chosen when applicable.

## How to Extend or Modify Wrappers

Since wrappers are currently spec-only, extension means modifying the specification files.

### Adding a Step to an Existing Wrapper

1. Edit the relevant command spec in `src/bmad/tools/automation/commands/`
2. Insert the step in the "Exact Step Sequence" section at the correct position
3. Add any new reads/writes to the Reads and Writes sections
4. If the step produces a gate-dependent artifact, add it to the draft artifact tracking schema
5. Update the "Required state transitions" section
6. If a new approval checkpoint is needed, add it to the approval model in `policies/state-model.md`

### Adding a New Policy

1. Create a new policy file in `src/bmad/tools/automation/policies/`
2. Reference it from the automation `README.md`
3. Update any command specs that must follow the new policy

### Adding a New Template

1. Create the template in `src/bmad/tools/automation/templates/`
2. Reference it from `README.md` and from the command spec that uses it
3. Document the template's required fields and purpose

### Creating a New Wrapper

1. Create a command spec in `src/bmad/tools/automation/commands/` following the existing format
2. Define: Purpose, Prerequisites, Reads, Writes, Exact Step Sequence, Approval Checkpoints, Failure Handling, Resume Behavior, and Final Outputs
3. Add the wrapper to `README.md` and to the "Automation Wrappers" table in `BMAD-workflow.md`
4. Ensure the new wrapper follows all existing policies (state model, context budgeting, patching strategy)

## Relationship to the Canonical Workflow

The canonical workflow in `BMAD-workflow.md` remains the source of truth for what steps exist and in what order they run. Automation wrappers reference the workflow but add:

- **Sequencing contracts**: exact step-by-step sequences derived from the workflow phases
- **State tracking**: machine-readable YAML state that the workflow itself does not define
- **Approval orchestration**: structured gate objects that formalize the human checkpoints implied by the workflow
- **Draft management**: explicit draft-vs-canonical file placement rules
- **Resume semantics**: deterministic restart from the last accepted checkpoint
- **Context policies**: minimum-context loading rules per wrapper

If the canonical workflow changes (steps added, reordered, or removed), the automation wrapper specs must be updated to match. The workflow is upstream; wrappers are downstream consumers.

## Reference

| Resource | Path |
| --- | --- |
| Automation README | `src/bmad/tools/automation/README.md` |
| auto-plan spec | `src/bmad/tools/automation/commands/auto-plan.md` |
| auto-epic-start spec | `src/bmad/tools/automation/commands/auto-epic-start.md` |
| auto-story spec | `src/bmad/tools/automation/commands/auto-story.md` |
| auto-epic-end spec | `src/bmad/tools/automation/commands/auto-epic-end.md` |
| State model policy | `src/bmad/tools/automation/policies/state-model.md` |
| Context budgeting policy | `src/bmad/tools/automation/policies/context-budgeting.md` |
| Patching strategy policy | `src/bmad/tools/automation/policies/patching-strategy.md` |
| Templates | `src/bmad/tools/automation/templates/` |
| Canonical workflow | `src/bmad/BMAD-workflow.md` |
