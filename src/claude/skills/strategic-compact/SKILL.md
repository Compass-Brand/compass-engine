---
name: strategic-compact
description: Generate handoff documents before context limits are reached, preserving critical information for session continuation
---

# Strategic Compaction

## Purpose

Generate handoff documents before context limits are reached, preserving critical information for session continuation.

## When to Use

- Context window approaching limits
- Before complex multi-step operations
- At session transitions
- When preserving state for another agent/session

## Process

### 1. Assess Current Context

- Identify key decisions made this session
- Note files modified and their purposes
- Track open questions and blockers

### 2. Generate Handoff Document

Create a structured summary with:

- **Original Goal**: Original objective
- **Progress Summary**: What was accomplished
- **State**: Current position in workflow
- **Files Changed**: List with brief descriptions
- **Decisions Made**: Key choices and rationale
- **Blockers/Questions**: Unresolved issues
- **Next Steps**: Immediate actions for continuation

### 3. Output Format

```markdown
# Session Handoff: [Date/Time]

## Original Goal

[What we set out to accomplish]

## Progress Summary

- [Completed item 1]
- [Completed item 2]

## Current State

[Where we are in the process]

## Files Changed

| File         | Changes           |
| ------------ | ----------------- |
| path/to/file | Brief description |

## Decisions Made

1. [Decision]: [Rationale]

## Open Questions

- [Question 1]

## Next Steps

1. [Immediate next action]
2. [Following action]
```

## Integration

- Triggered by /compact-handoff command
- Manual trigger criteria: token count exceeds 50,000, more than 10 files modified, or session exceeds 30 minutes
- Writes to scratchpad or user-specified location
  - **Scratchpad location**: `.claude/scratchpad/` directory in the project root (auto-created if missing)
  - **Persistence**: Scratchpad files persist across sessions and are gitignored by default
