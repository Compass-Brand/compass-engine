# Repo Refactor Blueprint

Last reviewed: 2026-02-23

This document is the execution plan to fully refactor `compass-engine` into a clean, source-first repository that downstream setup automation can reliably consume.

## Goal

Make `compass-engine` the single source of truth for Compass Brand engineering defaults:
- Claude Code (`.claude`)
- Codex (`.codex`)
- OpenCode (`.opencode`)
- GitHub baseline (`.github`)
- beads bootstrap
- BMAD customization layer

## Current Problems

1. Unclear source-vs-generated boundaries in some docs and folders
2. Workflow expectations not fully codified as enforceable checks
3. Testing strategy still mostly operational, with limited explicit contracts
4. BMAD customization path exists but needs stronger module lifecycle rules
5. OpenCode plugin direction exists but no implementation contract yet

## Target Architecture

1. `src/` is the only editable source for distributed bundles and templates
2. `dist/` is generated and minimal; never hand-edited
3. `_bmad-output/` is runtime-only and ignored
4. `BMAD-METHOD/` remains upstream input (submodule), not Compass customization output
5. Docs are explicit about "delete stale artifacts, do not archive in-repo"

## Keep vs Delete Policy

Keep:
- `src/`, `scripts/`, `docs/`, `tests/`, `reference/`, `.github/`, `BMAD-METHOD/`

Delete or stop tracking when found:
- Legacy duplicate source trees
- Runtime artifact dumps committed by mistake
- Archived "old" planning or review folders that are no longer active
- Any generated output that is reproducible from scripts

Rule: if a file is generated and reproducible, do not keep it as a tracked source artifact.

## Development Workflow Contract

Required path for all implementation work:

1. `bd ready`
2. `bd show <id>`
3. `bd update <id> --status in_progress`
4. Implement only in source locations (`src/`, `scripts/`, `docs/`, `tests/`)
5. Run `npm run check`
6. `bd close <id>` (or status update if partial)
7. `git pull --rebase --autostash`
8. `bd sync`
9. Commit and push

This contract must be mirrored in docs and CI expectations.

## Refactor Phases

### Phase 1: Structure Hardening

Deliverables:
- Final directory contract doc updates
- Remove remaining legacy or duplicated non-source artifacts
- Confirm ignore rules for runtime/generated outputs

Exit criteria:
- Root directory contains only active source, build, docs, and automation folders
- No tracked runtime-only artifacts

### Phase 2: Toolchain Baseline (Claude, Codex, OpenCode)

Deliverables:
- Normalize command/agent/skill layout under `src/claude`, `src/codex`, `src/opencode`
- Define parity matrix for equivalent workflows across all three tools
- Add validation checks for required bundle files per target

Exit criteria:
- `npm run check` fails if any target baseline is incomplete
- Push dry-run confirms deterministic output for all targets

### Phase 3: Beads Everywhere

Deliverables:
- Standard beads bootstrap payload in `src/beads`
- Explicit integration rules for AGENTS/copilot instructions in downstream repos
- Verification step that checks presence of beads onboarding snippets in output bundle

Exit criteria:
- Downstream setup consumes beads defaults without manual edits

### Phase 4: GitHub Default Setup

Deliverables:
- Standard workflow baseline in `src/github/workflows`
- Documented default policy set (PR checks, branch protection expectations, code scanning hooks)
- Compatibility table for repos with different runtime stacks

Exit criteria:
- Fresh downstream repo gets a working default CI baseline from this source alone

### Phase 5: BMAD as Default Planning Engine

Deliverables:
- BMAD default path documented as the planning system of record
- Custom module lifecycle documented and enforced (`create`, `edit`, `validate`, `reconcile with upstream`)
- Clear boundary: upstream in `BMAD-METHOD/`, Compass custom modules in `src/bmad/modules/`

Exit criteria:
- New custom module creation is repeatable via script and docs
- Module validation is part of normal quality flow

### Phase 6: OpenCode Plugin Foundation

Deliverables:
- Plugin architecture contract (command registry, BMAD provider adapter, beads hooks)
- First two plugin-backed BMAD workflows implemented and verified
- Cross-tool parity checks for generated artifacts

Exit criteria:
- OpenCode plugin execution produces the same planning outputs expected by Claude/Codex paths

### Phase 7: Documentation Reset

Deliverables:
- Remove stale docs; keep only current operational docs
- Rewrite docs around real workflows, not legacy history
- Add "last reviewed" metadata to operational docs

Exit criteria:
- A new maintainer can run end-to-end workflow without tribal knowledge

## Testing and Quality Gates Plan

Current gate:
- `npm run check` (`validate` + `build` + `push --dry-run`)

Required expansion:
1. Contract tests for required files per target bundle
2. Determinism checks for generated outputs
3. Integration smoke test against a temp downstream repo scaffold
4. Optional unit tests for script modules as scripts grow in complexity

## Downstream Integration Contract

The following target names are stable and must remain stable:
- `.claude`
- `.codex`
- `.opencode`
- `.github`

Migration changes must be additive or explicitly versioned with clear downstream update instructions.

## Definition of Done for Refactor Program

1. No legacy/duplicate source trees remain
2. Source-of-truth boundaries are explicit and enforced
3. All three dev CLIs are first-class and parity-tested for core workflows
4. Beads baseline is included in every downstream setup
5. GitHub defaults are delivered from source with clear policy docs
6. BMAD customization workflow is scriptable and documented
7. OpenCode plugin foundation exists with at least two working BMAD flows
8. Documentation is current, concise, and operational

## Execution Order Recommendation

1. Phase 1
2. Phase 2
3. Phase 3 and Phase 4 in parallel
4. Phase 5
5. Phase 6
6. Phase 7

Anything else to highlight or include that I might have missed?
