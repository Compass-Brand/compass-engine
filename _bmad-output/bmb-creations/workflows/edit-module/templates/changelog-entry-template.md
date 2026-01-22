# Changelog Entry Template

This template follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

---

## Entry Format

```markdown
## [Unreleased]

### {Category}
- {Description} ({date}, {user})
```

---

## Valid Categories

Use these exact category names (case-sensitive):

| Category | When to Use |
|----------|-------------|
| **Added** | New features, new agents, new workflows, new files |
| **Changed** | Modifications to existing functionality |
| **Deprecated** | Features marked for future removal |
| **Removed** | Features or files deleted |
| **Fixed** | Bug fixes, corrections |
| **Security** | Security-related changes |

---

## Entry Examples

### Adding a New Agent

```markdown
### Added
- New `data-analyst` agent with CSV processing capabilities (2026-01-07, Trevor Leigh)
```

### Modifying an Existing Workflow

```markdown
### Changed
- Updated `create-prd` workflow step-03 to include competitive analysis section (2026-01-07, Trevor Leigh)
```

### Removing a Component

```markdown
### Removed
- Deprecated `legacy-reporter` agent - functionality merged into `analyst` agent (2026-01-07, Trevor Leigh)
```

### Fixing an Issue

```markdown
### Fixed
- Corrected YAML syntax error in `module.yaml` dependencies array (2026-01-07, Trevor Leigh)
```

---

## Full Changelog Structure

When creating a new `CHANGELOG.md` file for a module:

```markdown
# Changelog

All notable changes to this module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Initial module creation (YYYY-MM-DD, User Name)

## [1.0.0] - YYYY-MM-DD

### Added
- First stable release
```

---

## Guidelines

1. **One entry per logical change** - Don't combine unrelated changes
2. **Use imperative mood** - "Add feature" not "Added feature" in the description
3. **Be specific** - Include component names, file paths where relevant
4. **Date format** - Use ISO 8601: YYYY-MM-DD
5. **Attribution** - Always include the user who made the change
6. **Link issues** - Reference issue numbers if applicable: "Fix login bug (#123)"
