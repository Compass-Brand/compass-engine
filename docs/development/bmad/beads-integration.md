# Beads Integration With BMAD Workflow

This document explains how Beads (`bd`) integrates with the Compass BMAD workflow lifecycle as the issue and task tracking system of record.

## What Beads Is And Why It Replaces TodoWrite

Beads is a CLI issue tracker invoked through the `bd` command. It manages issues, blockers, defects, and carry-over work as structured, trackable records with lifecycle states rather than freeform text.

Compass BMAD explicitly rejects TodoWrite and markdown task lists as authoritative task trackers for active delivery. The reasons are practical:

- **Lifecycle tracking.** Beads issues move through defined states (`open`, `in_progress`, `closed`) with timestamps. Markdown checkboxes have no lifecycle, no assignee, no dependency model, and no synchronization.
- **Cross-session persistence.** After context compaction or a fresh session, `bd prime` recovers issue-tracking context. Markdown task lists embedded in conversation state are lost on compaction.
- **Reconciliation.** At phase closeout, Beads provides a machine-queryable record of what was completed, what was deferred, and what was discovered. Markdown lists require manual auditing.
- **Separation of concerns.** Planning files in `planning/` hold references to Beads issue IDs; they do not duplicate issue truth. Status, assignee, dependency, and closure truth stay in `bd`.

The authority rule is simple: `bd` is authoritative for task and issue lifecycle; planning files hold references and planning state, not duplicate issue truth.

## The `bd` Command Lifecycle Mapped To BMAD Phases

Each `bd` subcommand maps to a specific point in the BMAD workflow.

### `bd prime`

**When:** At session start, after compaction, or when entering a fresh automation run.

Recovers issue-tracking context so the agent or operator can see the current issue set before planning work begins. Initialization (BMAD-workflow.md section A.1) requires verifying that `bd` is available and running `bd prime` when needed.

### `bd create`

**When:** Whenever a new trackable unit of work is identified.

- Phase issues: created during Phase Sync (section 4).
- Epic issues: created during epic start, before the story loop begins.
- Story issues: created before Dev Story (section 8C, step DS).
- Follow-up issues: created whenever blockers, defects, or carry-over work are discovered during implementation, review, or closeout.

### `bd update`

**When:** Work transitions between states.

- Claiming a story for implementation: `bd update <id> --status in_progress`.
- Recording an epic as active: update the epic issue to `in_progress` once epic start is approved.
- Any status change that reflects actual workflow progression.

### `bd close`

**When:** Work is accepted and complete.

- Story issues: closed after the story is accepted (post-review, post-traceability).
- Epic issues: closed after all stories are complete or explicitly deferred with carry-over issues.
- Phase issues: closed during Phase Closeout (section 10).

### `bd sync`

**When:** After material changes to the issue set.

- After phase issue reconciliation during Phase Sync.
- After epic start approval.
- After story acceptance and closure.
- After epic closeout with carry-over issue creation.
- At phase closeout as a final reconciliation step.
- At each execution boundary when the issue set changes materially.

## Phase Issues

Phase issues represent the active roadmap slice being executed.

**Creation.** During Phase Sync (BMAD workflow section 4), the workflow reconciles the active Beads phase issue and stores the issue reference in `phase-state.yaml`. The `beads` object in `phase-state.yaml` carries:

```yaml
beads:
  parent_issue_id: ""       # workspace or orchestration parent, if routed
  phase_issue_id: ""        # active phase issue for this repo scope
  active_epic_issue_id: ""  # set when epic execution starts
  active_story_issue_id: "" # set when a story is claimed
  follow_up_issue_ids: []   # discovered blockers, defects, carry-over
  last_synced_at: ""        # last bd sync timestamp
```

**Workspace and orchestration scope.** A parent initiative or orchestration issue may exist when the current work is routed from a workspace or parent repo. Child repo delivery work still belongs to child repo-local issues.

**Closure.** Phase issues are closed during Phase Closeout (section 10). The closeout workflow closes the completed phase issue, creates carry-over issues for deferred work, and runs `bd sync`.

## Story Issues

Story issues are the most granular trackable unit in the BMAD delivery spine.

### Creation Before Dev Story

Every active implementation story must have a Beads issue before Dev Story (`DS`) begins. The automation wrappers enforce this as a preflight check. If no issue exists, the wrapper reconciles or creates one and records it in `phase-state.yaml.beads.active_story_issue_id`.

### Claiming

When a story enters implementation, it is claimed with `bd update <id> --status in_progress`. This marks the story as actively being worked on and prevents duplicate effort.

### Closing After Acceptance

After the story passes review, test automation, traceability, and merge approval:

1. Close the story issue with `bd close`.
2. Append any new follow-up issue IDs to `phase-state.yaml.beads.follow_up_issue_ids`.
3. Clear `phase-state.yaml.beads.active_story_issue_id`.
4. Run `bd sync`.

If the story fails review or a gate, the issue stays open. The story run report records the last successful step and open blockers.

## Tracking Newly Discovered Work

During implementation, review, and closeout, new work surfaces that was not part of the original plan. Beads captures this with `bd create` rather than burying it in markdown evidence.

### Blockers

Issues that prevent the current story or epic from completing. Created with `bd create` as soon as the blocker is identified. Recorded in follow-up issue IDs so they are visible at the next reconciliation checkpoint.

### Defects

Bugs found during implementation, testing, or review. Created with `bd create` to ensure they are tracked independently from the story that discovered them.

### Carry-Over

Work that was in scope but deferred to a later epic or phase. Created during epic closeout (`auto-epic-end`) or phase closeout. The closeout workflow creates follow-up Beads issues for incomplete or deferred work, appends their IDs to `phase-state.yaml.beads.follow_up_issue_ids`, and runs `bd sync`.

The pattern is consistent: discovered work becomes a Beads issue, not a markdown note. The issue IDs are recorded in the runtime state so reconciliation at any boundary can account for them.

## Workspace Vs Repo-Local Issue Scoping

Beads issues follow the same ownership model as BMAD planning artifacts.

- **Repo-local issues.** Most delivery work (stories, epics, defects, blockers) belongs to the repo where the work is executed. These are created and managed within the repo's own Beads scope.
- **Workspace or orchestration issues.** A parent Beads issue may exist at the workspace or parent-repo level when work is routed through Initiative Routing (section 4A). This parent issue coordinates child repo workstreams but does not own child repo-local delivery work.
- **The `parent_issue_id` field** in `phase-state.yaml.beads` links the repo-local phase to its orchestration parent when applicable.
- **Child repo authority.** Even when a parent issue exists, the child repo's phase issue, epic issues, and story issues belong to the child repo. Status truth for those issues stays in the child repo's `bd` context.

## Phase Closeout Reconciliation

Phase Closeout (BMAD workflow section 10) is the formal reconciliation point where Beads issue state and planning state are brought into agreement.

The closeout sequence for Beads:

1. **Close the phase issue.** The completed phase issue is closed with `bd close`.
2. **Create carry-over issues.** Any deferred work, unresolved blockers, or incomplete stories become new Beads issues so they survive the phase boundary.
3. **Run `bd sync`.** Final synchronization ensures the issue set is consistent.
4. **Update `phase-state.yaml`.** The closeout updates the phase state to reflect the closed phase and the carry-over issue references.

This reconciliation happens within the larger closeout write order:

1. Update `current/phase-state.yaml`
2. Update `current/phase.md`
3. Update `roadmap/roadmap.yaml`
4. Update `roadmap/roadmap.md`

After closeout, the frozen phase snapshot is archived into `previous/<phase-slug>-<YYYY-MM-DD>/` and lessons are extracted into `lessons/<phase-slug>-<YYYY-MM-DD>/`. Carry-over issues persist in Beads, ready for the next phase to pick up.

## The 7 Beads Control Rules

These rules are quoted verbatim from `BMAD-workflow.md`:

> 1. `bd` is the issue and task system of record for Compass BMAD work.
> 2. TodoWrite and markdown task lists are not authoritative task trackers for active Compass BMAD delivery.
> 3. Every active phase should have a Beads phase issue recorded in `phase-state.yaml`.
> 4. Workspace or orchestration initiatives may also record a parent Beads issue, but child repo delivery work still belongs to child repo-local issues.
> 5. Every implementation story should have a Beads story issue before `Dev Story` begins.
> 6. Newly discovered blockers, defects, and carry-over work should be recorded with `bd create`, not only in markdown evidence.
> 7. Phase and automation closeout should reconcile issue status with `bd close` where appropriate and finish with `bd sync`.
