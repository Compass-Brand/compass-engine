# Sub-Repo Removal Readiness Audit

> **ARCHIVED:** Sub-repos have been consumed into the src/-based BMAD modules. This audit is historical context only.

Status: archived
Owner:
Last Updated: 2026-03-13

This audit checks whether the five adjacent source repos can be removed from this repository without breaking the active Compass BMAD reference layer.

## Scope

Candidate removals:

- `BMAD-CYBERSEC`
- `bmad-method-wds-expansion`
- `bmad-module-creative-intelligence-suite`
- `pov-oversight-agent`
- `ai-memory`

This audit is only about those five repos.

It does not assess removal of:

- `BMAD-METHOD`
- `bmad-method-test-architecture-enterprise`
- `bmad-builder`

## Audit Question

Can the five adjacent source repos be removed right now?

## Decision

No.

The active Compass BMAD reference layer is no longer operationally dependent on those repos for the selected CIS, WDS, and CYBERSEC lanes.

However, the repository is not deletion-ready yet because the sub-repos are still registered as git submodules and are still referenced by repo-management and tooling configuration.

## Method

The audit checked:

1. active BMM workflow, agent, planning, and automation surfaces for live path references into the five source repos
2. the active BMM command catalog for workflow-file paths that fail to resolve locally
3. repo-level submodule registration and status
4. repo-level tooling and policy files that still assume those sub-repos exist
5. provenance-only references that can remain as historical context

## Findings

### 1. Active Compass BMAD Layer: Pass

The active reference-stage BMAD layer no longer shows operational dependency on the five source repos.

Evidence:

- no active references were found in the audited BMAD/planning/automation/documentation surfaces to:
  - `_bmad/wds`
  - `_bmad/cybersec-team`
  - `src/cybersec-team`
- the active command catalog in `reference/BMAD/modules/custom/bmm/module-help.csv` resolves through local reference mappings
- the selected CIS, WDS, and CYBERSEC assets now exist under `reference/BMAD/modules/custom/bmm/`

Interpretation:

- the method-level import work is far enough along that these five repos are no longer acting as hidden runtime sources for the active BMM layer

### 2. Git Submodule Registration: Fail

The repository is still configured to carry these repos as submodules.

Evidence:

- `.gitmodules` still contains entries for:
  - `BMAD-CYBERSEC`
  - `bmad-method-wds-expansion`
  - `bmad-module-creative-intelligence-suite`
  - `pov-oversight-agent`
  - `ai-memory`
- `git submodule status` still lists all five submodules as present

Interpretation:

- even though the active BMAD layer no longer depends on them operationally, the repo still depends on them structurally
- removing them now without planned cleanup would leave the repo in an inconsistent state

### 3. Repo Tooling And Policy References: Fail

Several repo-level files still assume these sub-repos exist.

Evidence:

- `biome.json`
- `src/root/biome.json`
- `src/github/workflows/linting.yml`
- `src/github/workflows/quality-checks.yml`
- `src/github/profiles/dependabot-submodule-bmad-method.yml`
- `SUBMODULE_SECURITY.md`

Interpretation:

- these are not method-runtime dependencies, but they are real repo-management dependencies
- deletion cannot be considered complete until these are cleaned up or intentionally rewritten

### 4. Provenance And Historical References: Acceptable With Intentional Retention

Some files still mention the source repos as provenance or planning inputs.

Evidence:

- `reference/BMAD/BMAD-workflow.md`
- `reference/BMAD/modules/custom/bmm/COMPASS-EXTENSION-MAP.md`
- `_planning/current/research/2026-03-10-bmad-flow-extension-and-automation-review.md`

Interpretation:

- these do not block deletion by themselves
- they should either remain as historical provenance or be rewritten later if you want the repo to stop naming the former source repos entirely

## Classification

### Deletion Blockers

These must be resolved before the five source repos can be removed:

1. `.gitmodules` still registers all five repos
2. `git submodule status` still expects all five repos
3. repo tooling and policy files still refer to them as active submodules or managed directories
4. no explicit removal change set has yet been prepared

### Non-Blocking Provenance References

These may remain temporarily without preventing deletion:

1. extension provenance in `COMPASS-EXTENSION-MAP.md`
2. historical source references in `BMAD-workflow.md`
3. planning research notes in `_planning/current/research/`

### Not Yet Proven For Productization

These are not deletion blockers by themselves, but they remain part of the larger productization risk picture:

1. no full real-world usage cycle has run through the new planning-state choreography
2. no automation pilot has proven the reference automation design
3. no durable productization approval artifact has been written yet

## Readiness Summary

| Area | Result | Notes |
| --- | --- | --- |
| Active BMAD operational dependence on the five repos | Pass | Selected imports are landed in the BMM layer |
| Command catalog local resolution | Pass | `module-help.csv` resolves through local reference mappings |
| Git submodule registration cleanup | Fail | `.gitmodules` and `git submodule status` still carry all five repos |
| Repo tooling cleanup | Fail | linting, quality, dependabot, and submodule policy files still refer to them |
| Provenance handling | Pending but acceptable | historical references can remain intentionally |
| Removal approval | Pending | user has not yet approved an actual deletion change set |

## Removal Exit Criteria

The five source repos can be considered removal-ready only when all of the following are true:

1. the active BMM layer still resolves without them
2. `.gitmodules` no longer registers them
3. `git submodule status` no longer expects them
4. repo tooling and policy files are cleaned up
5. only intentional provenance references remain
6. the user explicitly approves the removal change set

## Recommended Next Step

Do not remove the five source repos yet.

The next move should be:

1. run a real reference-layer usage cycle
2. keep the audit results as the cleanup checklist for the future removal change set
3. perform actual submodule and tooling cleanup only when you are ready to delete those repos for real
