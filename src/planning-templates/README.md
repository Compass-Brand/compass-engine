# Planning Templates

This folder contains templates for the Compass Brand planning folder structure. These templates are designed to be distributed to all repositories in the ecosystem.

## Templates

| Template | Purpose |
|----------|---------|
| `product-backlog.yaml` | Prioritized backlog with estimates and TDD gates |
| `sprint-goal-template.md` | Sprint objectives and commitments |
| `sprint-backlog-template.yaml` | Sprint work items with TDD tracking |
| `retrospective-template.md` | What went well/improve/actions |
| `epic-template.md` | Epic definition with Definition of Done |
| `story-template.md` | User story with TDD requirements |
| `adr-template.md` | Architecture Decision Record |
| `spike-template.md` | Technical investigation format |
| `test-plan-template.md` | Epic-level test strategy |
| `acceptance-tests-template.md` | Given/When/Then acceptance criteria |

## Usage

### Manual Setup

Copy the templates to a new repo's `planning/` folder:

```bash
cp -r src/planning-templates/* /path/to/repo/planning/
```

### Scaffold Script

Use the scaffold script to set up a complete planning structure:

```bash
./scripts/scaffold-planning.sh /path/to/repo
```

## TDD Enforcement

The templates enforce TDD through:

1. **Story template**: Requires TDD checklist completion
2. **Sprint backlog**: Tracks `tdd_gate` status for each item
3. **Test plan**: Must exist before stories are "ready-for-dev"
4. **Acceptance tests**: Written in Given/When/Then format before implementation

## Integration with BMAD

These templates complement BMAD outputs:

- BMAD generates initial artifacts in `_bmad-output/`
- Planning templates organize ongoing development work
- Sprint planning pulls from BMAD-generated epics/stories
- Retrospectives feed back into future BMAD cycles

## Customization

Repos may customize templates for their specific needs while maintaining:

- TDD checklist in all story templates
- Acceptance criteria format (Given/When/Then)
- Sprint backlog TDD gate tracking
- ADR format consistency
