# Planning Reference Framework

This directory is the retained planning reference index for the roadmap-driven Compass BMAD model.

> **Note:** This is reference documentation for the shipped `src/planning/` bundle. The deployed structure in project repositories does not include a `framework/` subdirectory; all framework paths shown here map to the root `planning/` level in deployed repos.

## Purpose

- provide the reference layout for project-level and phase-level planning
- separate operational guidance from the live planning framework
- support repeatable multi-phase development instead of one-off MVP planning

## Domains

- `framework/` documents the planning framework layout retained for reference
- `docs/` contains usage guidance, conventions, and lifecycle rationale
- `templates/` contains starter artifacts retained for provenance and comparison

Workspace and parent repos may also use orchestration-specific control surfaces:

- `repositories.yaml`
- `current/initiative-index.yaml`
- `current/initiatives/`

## Primary Entry Commands

- use `/bmad-bmm-init-planning` to scaffold or normalize the live planning framework from the shipped `src/planning/` surface
- use `/bmad-bmm-sync-repositories` to refresh the approved repo-topology registry when repos are added, moved, or missed
- use `/bmad-bmm-workspace-bootstrap` from workspace or parent repos to initialize selected child repos into the BMAD planning and docs structure
- use `/bmad-bmm-project-roadmap` to create or update approved roadmap state before `Phase Sync`
- use templates directly only when a remaining planning step does not yet have a dedicated workflow

## Read Order

1. `framework/README.md`
2. `docs/how-to-use.md`
3. `docs/workflow-map.md`
4. `templates/README.md`
5. `roadmap/roadmap.md`
6. `current/phase.md`

When machine state matters, also load:

1. `repositories.yaml` when repo routing or ownership matters
1. `roadmap/roadmap.yaml`
2. `current/phase-state.yaml`
3. `current/initiative-index.yaml` when multiple concurrent initiatives are active

## Structure

```text
reference/planning/
├── README.md
├── repositories.yaml
├── current/
├── previous/
├── lessons/
├── roadmap/
├── docs/
├── templates/
└── framework/
    └── README.md
```
