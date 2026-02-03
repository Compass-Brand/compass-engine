---
description: Create numbered implementation plan with complexity analysis
---

# Plan

## Usage

/plan <feature-or-task-description>

## What This Command Does

1. Invokes the planner agent
2. Analyzes the codebase for affected files
3. Creates numbered implementation steps
4. Assesses complexity and identifies risks
5. Notes dependencies between steps

## Invoked Components

- Agent: planner

## Example

```bash
/plan Add OAuth2 authentication
```

## Output

Numbered plan with:

- Step descriptions
- Files to modify
- Complexity rating
- Risks and mitigations

**Note:** Plans are stored in `docs/plans/` with format `YYYY-MM-DD-phase-N-<name>.md`.
