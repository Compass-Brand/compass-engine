---
name: reflect-conflicts
description: Find learnings that contradict each other and need resolution
---

# Reflect Conflicts - Find Contradictory Learnings

Find learnings that contradict each other and need resolution.

## Usage

```text
/reflect conflicts
```

## Conflict Types

1. **Direct contradiction:** Same topic, opposite guidance
2. **Partial overlap:** Similar topic, incompatible approaches
3. **Scope conflict:** Personal vs project guidance conflicts

## Workflow

### Step 1: Gather Learnings

```python
learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "skill-learning",
  "query_context": "Finding conflicts",
  "tags": ["skill-learning"],
  "k": 100,
  "include_links": True
})
```

### Step 2: Detect Conflicts

Group by keywords/topic. Compare within groups for:

- One says "do X", another says "don't do X"
- CORRECTION after PREFERENCE on same topic
- Different scopes with conflicting guidance

### Step 3: Present Conflicts

```text
┌─ Conflict Analysis ───────────────────────────────────────────┐
│                                                               │
│  Found 2 potential conflicts:                                 │
│                                                               │
├─ Conflict #1: Direct Contradiction ───────────────────────────┤
│                                                               │
│  Memory #12: [PREFERENCE] Use .then() for promises            │
│  vs                                                           │
│  Memory #42: [CORRECTION] Always use async/await              │
│                                                               │
│  Recommendation: Mark #12 obsolete, superseded by #42         │
│  Actions: [Apply] [Keep Both] [Manual Review]                 │
│                                                               │
├─ Conflict #2: Scope Ambiguity ────────────────────────────────┤
│                                                               │
│  Memory #33: [PREFERENCE] Use tabs (personal)                 │
│  vs                                                           │
│  Memory #56: [PREFERENCE] Use spaces (project)                │
│                                                               │
│  Recommendation: Both valid - clarify scopes                  │
│  Actions: [Clarify Scopes] [Merge] [Manual Review]            │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Step 4: Resolution Actions

**Apply Recommendation:**

```python
mcp__forgetful__execute_forgetful_tool("mark_memory_obsolete", {
  "memory_id": 12,
  "reason": "Superseded by newer correction",
  "superseded_by": 42
})
```

**Clarify Scopes:**

```python
# Note: Preserve the original memory content when adding scope clarification
# Fetch the original content first, then append the scope annotation
original = mcp__forgetful__execute_forgetful_tool("get_memory", {"memory_id": 33})
updated_content = original["content"] + "\n\nScope: Personal preference"
mcp__forgetful__execute_forgetful_tool("update_memory", {
  "memory_id": 33,
  "content": updated_content
})
```

**Link as Related:**

```python
mcp__forgetful__execute_forgetful_tool("link_memories", {
  "memory_id": 33,
  "related_ids": [56]
})
```

## Reference

See `.claude/skills/reflect/LIFECYCLE.md` for detailed documentation.
