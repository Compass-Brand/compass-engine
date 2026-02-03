---
name: reflect
description: Analyze the current conversation for learnings and save them to Forgetful Memory
---

# Reflect - Analyze Session and Capture Learnings

Analyze the current conversation for learnings (corrections, preferences, patterns, edge cases, anti-patterns) and save them to Forgetful Memory.

## Usage

```bash
/reflect           # Analyze entire session
/reflect [skill]   # Focus on specific skill
```

## Workflow (5 Steps)

### Step 1: Scan Conversation

Look through the conversation for learning signals:

**HIGH confidence (create immediately):**

- User said "no", "wrong", "that's not right", "I meant..."
- User explicitly corrected output
- User expressed frustration

**MEDIUM confidence (verify context):**

- User said "perfect", "great", "exactly"
- User proceeded without modification
- Repeated choices

### Step 2: Check for Existing Learnings

Before creating new memories, query for similar existing ones:

```python
mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<learning topic>",
  "query_context": "Checking for existing similar learnings",
  "tags": ["skill-learning"],
  "k": 5
})
```

- Same topic, same conclusion → Update existing memory
- Same topic, different conclusion → Flag as conflict
- Related but distinct → Create new, link to existing

### Step 3: Create Structured Memory

For each learning found:

```python
mcp__forgetful__execute_forgetful_tool("create_memory", {
  "title": "[TYPE] Brief description",
  "content": "Detailed learning with context",
  "context": "Captured during [task] - [why important]",
  "keywords": ["<topic>", "<skill>"],
  "tags": ["skill-learning", "<type>", "<skill-name>"],
  "importance": <6-10>,
  "project_ids": [<if project-specific>]
})
```

### Step 4: Link Related Items

```python
# Link to entities
mcp__forgetful__execute_forgetful_tool("link_entity_to_memory", {
  "entity_id": <id>, "memory_id": <new_id>
})

# Link to related memories
mcp__forgetful__execute_forgetful_tool("link_memories", {
  "memory_id": <new_id>, "related_ids": [<ids>]
})
```

### Step 5: Present Summary

```text
┌─ Learning Captured ───────────────────────────────────────┐
│                                                           │
│  Type: [CORRECTION/PREFERENCE/PATTERN/etc.]               │
│  Skill: [skill-name or "general"]                         │
│  Scope: [personal/project/skill/org-wide]                 │
│                                                           │
│  Title: [learning title]                                  │
│  Confidence: [HIGH/MEDIUM/LOW]                            │
│                                                           │
│  Linked to: Memory #42, Entity: Trevor                    │
│  Memory ID: #[new_id]                                     │
└───────────────────────────────────────────────────────────┘
```

## Learning Types

| Type         | Tag            | Importance | Signal                      |
| ------------ | -------------- | ---------- | --------------------------- |
| Correction   | `correction`   | 9          | Explicit fix                |
| Preference   | `preference`   | 8          | "I prefer", repeated choice |
| Pattern      | `pattern`      | 7          | Successful approach         |
| Edge Case    | `edge-case`    | 7          | Special handling needed     |
| Anti-pattern | `anti-pattern` | 9          | "Never do this"             |

## Reference

See `.claude/skills/reflect/` for detailed documentation:

- `LEARNING_TYPES.md` - Detailed type reference
- `SYNTHESIS.md` - How to graduate learnings
- `LIFECYCLE.md` - Managing learning states
- `VISUALIZATION.md` - Graph visualization
