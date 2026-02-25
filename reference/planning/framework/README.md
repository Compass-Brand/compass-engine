# Planning Framework Domain

`framework/` contains the canonical BMAD-compatible planning structure for Compass Engine.

## Intent

- Keep one active roadmap phase in `current/`.
- Move completed phases into `previous/<roadmap-phase>-<completion-date>/`.
- Capture reusable lessons in `lessons/<roadmap-phase>-<completion-date>/`.
- Track cross-phase direction in `roadmap/`.

This layout is optimized for brownfield continuation where teams run multiple BMAD cycles over time and need continuity between cycles.

## Core Areas

- `../docs/`: operational guidance and rationale for this framework.
- `current/`: active phase working set.
- `previous/`: immutable snapshots of completed phases.
- `lessons/`: carry-forward practices and anti-patterns from completed phases.
- `roadmap/`: project-level planning context that spans phases.

## Naming Rules

- Phase snapshot folders: `<phase-slug>-<YYYY-MM-DD>`
- Lesson folders: `<phase-slug>-<YYYY-MM-DD>`
- Dates MUST use `YYYY-MM-DD`.

## Lifecycle

1. Run active work only in `current/`.
2. Close the phase using `../docs/phase-closeout-checklist.md`.
3. Move closed artifacts into `previous/`.
4. Extract reusable findings into `lessons/`.
5. Update `roadmap/roadmap.md` and archive superseded roadmap materials.
