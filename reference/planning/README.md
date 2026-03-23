# Planning Reference Framework

This directory is the retained planning reference index for the roadmap-driven Compass BMAD model.

## Purpose

- provide the reference layout for project-level and phase-level planning
- separate operational guidance from the live planning framework
- support repeatable multi-phase development instead of one-off MVP planning

## Domains

- `framework/` documents the planning framework layout retained for reference
- `docs/` contains usage guidance, conventions, and lifecycle rationale
- `templates/` contains starter artifacts retained for provenance and comparison

Workspace and parent repos may also use orchestration-specific control surfaces:

- `framework/repositories.yaml`
- `framework/current/initiative-index.yaml`
- `framework/current/initiatives/`

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
5. `framework/roadmap/roadmap.md`
6. `framework/current/phase.md`

When machine state matters, also load:

1. `framework/repositories.yaml` when repo routing or ownership matters
1. `framework/roadmap/roadmap.yaml`
2. `framework/current/phase-state.yaml`
3. `framework/current/initiative-index.yaml` when multiple concurrent initiatives are active

## Structure

```text
reference/planning/
├── README.md
├── docs/
├── templates/
└── framework/
    ├── README.md
    ├── repositories.yaml
    ├── current/
    ├── previous/
    ├── lessons/
    └── roadmap/
```
