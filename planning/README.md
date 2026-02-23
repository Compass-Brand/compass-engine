# Planning

This folder contains planning artifacts/templates for this repository following the Compass Brand unified planning structure.

In `compass-engine`, operational task tracking uses `bd` (`.beads/`) as the source of truth. Planning files here support larger planning/architecture workflows and templates.

## Structure

```
planning/
├── backlog/              # Product backlog and refinement notes
│   ├── product-backlog.yaml
│   └── refinement-notes/
├── sprints/              # Sprint artifacts
│   ├── current/          # Active sprint
│   ├── archive/          # Completed sprints
│   └── templates/        # Sprint templates
├── epics/                # Epic definitions
│   └── templates/        # Epic and story templates
│       └── tests/        # TDD test templates
├── decisions/            # Local ADRs
│   └── templates/
└── spikes/               # Technical investigations
```

## TDD Enforcement

Before starting development on any epic:

1. Create test plan at `planning/epics/{epic}/tests/test-plan.md`
2. Write acceptance tests at `planning/epics/{epic}/tests/acceptance-tests.md`
3. Follow RED-GREEN-REFACTOR cycle

## Relationship to Beads

- Use `bd` for active execution tracking, dependencies, and session status.
- Use `planning/` for higher-level artifacts (epics, ADRs, spike docs, templates).

## Templates

- **product-backlog.yaml** - Prioritized backlog with TDD gates
- **sprint-goal-template.md** - Sprint objectives
- **epic-template.md** - Epic definition with DoD
- **story-template.md** - Story with TDD checklist
- **adr-template.md** - Architecture Decision Record

## Related

- [Workspace Planning](../../planning/README.md) (if in submodule)
- [ADR-0001: Planning Structure](../../planning/decisions/adr-0001-planning-structure.md)
