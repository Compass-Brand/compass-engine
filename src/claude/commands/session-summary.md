---
name: session-summary
description: Generate a comprehensive handoff document for session continuation or team handoff
---

# Session Summary

Generate a comprehensive handoff document for session continuation or team handoff.

## Output Sections

### 1. Summary

Brief overview of what was accomplished in this session.

### 2. What Worked

- Successful approaches and solutions
- Patterns that proved effective
- Tools that helped

### 3. What Failed / Challenges

- Approaches that didn't work
- Blockers encountered
- Issues requiring follow-up

### 4. Files Modified

List all files created, modified, or deleted:

```bash
git diff --name-status HEAD~10
```

Or for uncommitted changes:

```bash
git status --porcelain
```

### 5. Next Steps

Prioritized list of remaining work or follow-up items.

## Generation Process

1. **Review git history** for this session:

   ```bash
   # Default: last 8 hours. Adjust --since for longer sessions or use commit range.
   # Alternative: git log --oneline HEAD~20..HEAD (last 20 commits)
   git log --oneline --since="8 hours ago"
   ```

2. **Check for uncommitted work**:

   ```bash
   git status
   git diff --stat
   ```

3. **Review any error logs or failed tests**:

   ```bash
   # Check for recent test failures (8 hours = 480 minutes, matching git log window)
   find . -name "*.log" -mmin -480 -not -path "*/node_modules/*" -not -path "*/.git/*" -exec tail -20 {} \;
   ```

4. **Compile the summary** in Markdown format.

## Output Format

```text
# Session Summary: [DATE]

## Summary

[2-3 sentence overview]

## What Worked

- [Item 1]
- [Item 2]

## Challenges

- [Challenge 1]
- [Challenge 2]

## Files Modified

| File            | Action   | Description          |
| --------------- | -------- | -------------------- |
| path/to/file.ts | Modified | Added authentication |
| path/to/new.py  | Created  | New utility module   |

## Next Steps

1. [ ] [Priority 1 task]
2. [ ] [Priority 2 task]
3. [ ] [Priority 3 task]

---

Generated: [TIMESTAMP]
Session Duration: ~[X] hours
Commits: [N]
```

## Saving to Forgetful

After generating, optionally save to Forgetful:

```
mcp__forgetful__execute_forgetful_tool with:
- tool: "save_memory"
- params: {
    "title": "Session Summary: [DATE] - [TOPIC]",
    "content": "[Full summary content]",
    "tags": ["session-summary", "handoff"],
    # Replace with your project ID (e.g., compass-brand=2, legacy-system-analyzer=1)
    "project_id": "<YOUR_PROJECT_ID>"
  }
```

## Related Commands

- `/compact-handoff` - Shorter version for quick handoffs
- `/verify` - Verify changes before summarizing
