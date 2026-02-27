# Phase Closeout Checklist

Use this checklist before moving an active phase into `framework/previous/`.

## Prerequisites

1. `../framework/current/phase.md` is complete and current.
2. Planning artifacts are present in:
   - `../framework/current/planning/prd/`
   - `../framework/current/planning/ux-design/`
   - `../framework/current/planning/architecture/`
   - `../framework/current/planning/epics/`
3. Implementation artifacts are present in:
   - `../framework/current/implementation/stories/`
   - `../framework/current/implementation/evidence/`
4. Validation material exists in:
   - `../framework/current/testing/`
   - `../framework/current/research/` (if used in this phase)

## Closeout Steps

1. Confirm final phase slug and completion date.
2. Create target folder: `../framework/previous/<phase-slug>-<YYYY-MM-DD>/`.
3. Move all `../framework/current/` content into that folder.
4. Recreate clean `../framework/current/` scaffold for the next phase.
5. Create `../framework/lessons/<phase-slug>-<YYYY-MM-DD>/`.
6. Record:
   - what worked
   - what failed
   - what should change next phase
7. Update `../framework/roadmap/roadmap.md` with completion status and next horizon.
8. Move superseded roadmap artifacts to matching archive lane:
   - `../framework/roadmap/archive/brainstorming/<YYYY-MM-DD>/`
   - `../framework/roadmap/archive/research/<YYYY-MM-DD>/`
   - `../framework/roadmap/archive/product-brief/<YYYY-MM-DD>/`

## Validation Checks

1. `../framework/current/` contains only next-phase starter structure.
2. Closed-phase artifacts exist only in `../framework/previous/<phase-slug>-<YYYY-MM-DD>/`.
3. Lesson entry exists and is actionable.
4. `../framework/roadmap/roadmap.md` reflects new status.

## Failure Modes To Avoid

- Leaving final artifacts in `current/` after closeout.
- Archiving roadmap documents without date folders.
- Skipping lessons extraction.
- Using non-standard folder names or date formats.
