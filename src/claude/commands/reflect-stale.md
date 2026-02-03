---
name: reflect-stale
description: Find learnings that may no longer be relevant and need review
---

# Reflect Stale - Find Outdated Learnings

Find learnings that may no longer be relevant and need review.

## Usage

```text
/reflect stale
```

## Stale Criteria

A learning is potentially stale if:

1. **Age-based:** >90 days old, not synthesized or repeated
2. **Version-specific:** Mentions outdated technology versions
3. **Superseded:** Newer learning contradicts it
4. **Unused:** Never accessed since creation

## Workflow

### Step 1: Find Old Learnings

```python
old = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "skill-learning",
  "query_context": "Finding stale learnings",
  "tags": ["skill-learning"],
  "k": 50
})
# Post-query filter: keep only learnings where created_at is older than 90 days
# and not tagged "synthesized" or "reviewed-*"
# Note: query_memory does not support date filtering - apply filter to returned results
```

### Step 2: Check for Version Info

Look for mentions of specific versions (e.g., "Next.js 13", "Python 3.9") that may be outdated.

### Step 3: Present Review

```text
┌─ Stale Learning Review ───────────────────────────────────────┐
│                                                               │
│  Found 7 learnings that may need review:                      │
│                                                               │
├─ Age-Based (>90 days) ────────────────────────────────────────┤
│                                                               │
│  #23 [PREFERENCE] Use Jest for testing                        │
│      Created: 98 days ago                                     │
│      Action: [Keep] [Mark Obsolete] [Review]                  │
│                                                               │
├─ Version-Specific ────────────────────────────────────────────┤
│                                                               │
│  #45 [EDGE CASE] Next.js image optimization                   │
│      Mentions: Next.js X (current: Y) - version outdated      │
│      Action: [Update] [Mark Obsolete] [Review]                │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Step 4: Apply Actions

**Keep:** Add review timestamp

```python
mcp__forgetful__execute_forgetful_tool("update_memory", {
  "memory_id": <id>,
  "tags": [...existing, "reviewed-2026-01"]
})
```

**Mark Obsolete:**

```python
mcp__forgetful__execute_forgetful_tool("mark_memory_obsolete", {
  "memory_id": <id>,
  "reason": "<why no longer valid>"
})
```

**Update:** Edit content to reflect current state.

## Reference

See `.claude/skills/reflect/LIFECYCLE.md` for detailed documentation.
