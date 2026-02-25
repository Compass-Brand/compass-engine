# Phase Closeout Checklist

Use this checklist before moving an active phase into `previous/`.

## Prerequisites

1. `../current/phase.md` is complete and current.
2. Planning artifacts are present in:
   - `../current/planning/prd/`
   - `../current/planning/ux-design/`
   - `../current/planning/architecture/`
   - `../current/planning/epics/`
3. Implementation artifacts are present in:
   - `../current/implementation/stories/`
   - `../current/implementation/evidence/`
4. Validation material exists in:
   - `../current/testing/`
   - `../current/research/` (if used in this phase)

## Closeout Steps

1. Confirm final phase slug and completion date.
2. Create target folder: `../previous/<phase-slug>-<YYYY-MM-DD>/`.
3. Move all `../current/` content into that folder.
4. Recreate clean `../current/` scaffold for the next phase.
5. Create `../lessons/<phase-slug>-<YYYY-MM-DD>/`.
6. Record:
   - what worked
   - what failed
   - what should change next phase
7. Update `../roadmap/roadmap.md` with completion status and next horizon.
8. Move superseded roadmap artifacts to matching archive lane:
   - `../roadmap/archive/brainstorming/<YYYY-MM-DD>/`
   - `../roadmap/archive/research/<YYYY-MM-DD>/`
   - `../roadmap/archive/product-brief/<YYYY-MM-DD>/`

## Validation Checks

1. `../current/` contains only next-phase starter structure.
2. Closed phase artifacts exist only in `../previous/<phase-slug>-<YYYY-MM-DD>/`.
3. Lesson entry exists and is actionable.
4. `../roadmap/roadmap.md` reflects new status.

## Failure Modes To Avoid

- Leaving final artifacts in `current/` after closeout.
- Archiving roadmap documents without date folders.
- Skipping lessons extraction.
- Using non-standard folder names or date formats.
