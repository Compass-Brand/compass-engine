---
description: Generate a context handoff document for session continuation
---

# Compact Handoff

## Usage

/compact-handoff [output-path]

When `output-path` is omitted, the handoff is written to the scratchpad (internal session memory or workspace-specific notes).

## What This Command Does

1. Analyzes current session context
2. Identifies key decisions, changes, and progress
3. Generates a structured handoff document
4. Writes to specified path or scratchpad

## Invoked Components

- Skill: strategic-compact

## Example

```bash
/compact-handoff ./handoff-2026-01-29.md
```

When `output-path` is provided, the handoff document is written to that file. When omitted, output is written to `.claude/scratchpad/handoff-<timestamp>.md`.

## Output

A Markdown document with:

- Original goal
- Progress summary
- Current state
- Files changed with descriptions
- Decisions made with rationale
- Open questions
- Blockers
- Next steps
