# Planning Conventions

These conventions are mandatory for all artifacts in `reference/planning/framework/`.

## Naming

- Phase snapshot folder: `<phase-slug>-<YYYY-MM-DD>`
- Lesson folder: `<phase-slug>-<YYYY-MM-DD>`
- Archive folder: `<YYYY-MM-DD>`
- `phase-slug` MUST be lowercase kebab-case.

Examples:
- `platform-hardening-2026-02-25`
- `release-readiness-2026-03-14`

## Dates

- Date format MUST be `YYYY-MM-DD`.
- Do not use relative dates such as "today" or "next-week" in filenames.

## Status Tags

Use one of these status markers at the top of working markdown files:
- `Status: draft`
- `Status: active`
- `Status: final`
- `Status: archived`

## Ownership

Each major artifact SHOULD include:
- `Owner: <name or team>`
- `Last Updated: <YYYY-MM-DD>`

## File Lifecycle

1. Draft in `current/`.
2. Finalize in `current/`.
3. Freeze and move with phase closeout into `previous/`.
4. Extract reusable insights into `lessons/`.
5. Archive superseded roadmap artifacts in `roadmap/archive/`.

## Path Rules

- Active phase content MUST NOT be written under `previous/`.
- Historical content MUST NOT remain in `current/` after closeout.
- Roadmap artifacts belong in `roadmap/`, not inside phase snapshots.
