---
name: switch-context
description: Dynamically switch the operating context during a session
---

# Switch Context

Dynamically switch the operating context during a session.

## Usage

```
/switch-context [context-name]
```

Arguments:

- `dev` - Full edit access, TDD focus
- `review` - Read-only, checklist-driven
- `research` - Exploration only
- (or any custom context in `.claude/contexts/`)

## Process

1. **Validate ARGUMENTS format**:

   ```bash
   if [[ ! "${ARGUMENTS}" =~ ^[a-zA-Z0-9_-]+$ ]]; then
       echo "Invalid context name"; exit 1
   fi
   ```

1. **Validate context exists**:

   ```bash
   ls .claude/contexts/${ARGUMENTS}.md 2>/dev/null || echo "Context not found"
   ```

1. **Load new context**:

   ```bash
   cat .claude/contexts/${ARGUMENTS}.md
   ```

1. **Acknowledge transition**:
   Confirm the mode switch to the user and list key constraints of the new mode.

## Available Contexts

| Context    | Description                 |
| ---------- | --------------------------- |
| `dev`      | Full edit, TDD mandatory    |
| `review`   | Read-only, checklist-driven |
| `research` | Exploration, no edits       |

## Example

User: `/switch-context review`

Response:
"Switching to **review mode**. In this mode I will:

- NOT modify any files
- Follow the review checklist systematically
- Document findings as a structured report

What would you like me to review?"

## Notes

- Context switching is session-scoped
- Previous context state is not preserved
- For persistent context, use `CLAUDE_CONTEXT` environment variable
