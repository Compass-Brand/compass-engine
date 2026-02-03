---
name: reflect
description: Intelligent learning system that captures corrections, preferences, and patterns from sessions, saves them to Forgetful Memory, and synthesizes learnings into skill improvements. Use when user says "reflect", "remember this", "learn from this", after corrections, or at session end.
---

# Reflect - Intelligent Learning System

## Overview

Reflect captures learnings from conversations and saves them to Forgetful Memory, creating a feedback loop that improves future interactions. Learnings are categorized, linked to skills/projects/entities, and periodically synthesized into skill improvements.

## Quick Reference

| Command                       | Purpose                                    |
| ----------------------------- | ------------------------------------------ |
| `/reflect`                    | Analyze current session, capture learnings |
| `/reflect [skill]`            | Focus analysis on specific skill           |
| `/reflect status`             | Show learning statistics                   |
| `/reflect synthesize [skill]` | Propose skill improvements from learnings  |
| `/reflect graph [skill]`      | Visualize learning connections             |
| `/reflect stale`              | Find outdated learnings                    |
| `/reflect conflicts`          | Find contradictory learnings               |

## Learning Types

See [LEARNING_TYPES.md](LEARNING_TYPES.md) for detailed reference.

| Type         | Tag            | Importance | Signal                                        |
| ------------ | -------------- | ---------- | --------------------------------------------- |
| Correction   | `correction`   | 9          | User said "no", "not like that", explicit fix |
| Preference   | `preference`   | 8          | Repeated choices, "I prefer", "always use"    |
| Pattern      | `pattern`      | 7          | Successful approach, "this worked well"       |
| Edge Case    | `edge-case`    | 7          | Unexpected scenario, workaround needed        |
| Anti-pattern | `anti-pattern` | 9          | "Never do this", caused problems              |

## Core Workflow

### Step 1: Analyze Session

Scan the conversation for learning signals:

**HIGH confidence signals (corrections):**

- User said "no", "wrong", "not like that", "I meant..."
- User explicitly corrected output
- User requested changes immediately after generation
- User expressed frustration

**MEDIUM confidence signals (preferences/patterns):**

- User said "perfect", "great", "yes", "exactly"
- User accepted output without modification
- User built upon the output
- Repeated choices across the session

**MEDIUM confidence signals (edge cases):**

- Questions the approach didn't anticipate
- Scenarios requiring workarounds
- Features user asked for that weren't covered

### Step 2: Check for Existing Similar Learnings

Before creating new memories, ALWAYS query for similar existing ones:

```python
# MCP tool invocation pseudocode (not executable Python)
mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<learning topic keywords>",
  "query_context": "Checking for existing similar learnings before creating new",
  "tags": ["skill-learning"],
  "k": 5,
  "include_links": True
})
```

**If similar learning exists:**

- Same topic, same conclusion → Update existing (bump importance if repeated)
- Same topic, different conclusion → Flag as conflict, link both
- Related but distinct → Create new, link to existing

### Step 3: Determine Scope

Identify what scope this learning applies to:

| Scope        | When                         | How to Tag          |
| ------------ | ---------------------------- | ------------------- |
| Personal     | User-specific preference     | Link to user entity |
| Project      | Project-specific pattern     | Use `project_ids`   |
| Skill        | Skill-specific learning      | Tag with skill name |
| Organization | Applies to all Compass Brand | Tag with `org-wide` |

### Step 4: Create Structured Memory

```python
mcp__forgetful__execute_forgetful_tool("create_memory", {
  "title": "[TYPE] Brief description",
  "content": "Detailed learning with context. What happened, why it matters, how to apply.",
  "context": "Captured during [skill/task] - [why this is important]",
  "keywords": ["topic1", "topic2", "skill-name"],
  "tags": ["skill-learning", "<type>", "<skill-name>"],
  "importance": <6-10 based on type and confidence>,
  "project_ids": [<if project-specific>]
})
```

### Step 5: Link Related Entities

If the learning involves specific people, technologies, or concepts:

```python
# Link to entity (person, technology, etc.)
mcp__forgetful__execute_forgetful_tool("link_entity_to_memory", {
  "entity_id": <entity_id>,
  "memory_id": <new_memory_id>
})

# Link to related memories
mcp__forgetful__execute_forgetful_tool("link_memories", {
  "memory_id": <new_memory_id>,
  "related_ids": [<related_memory_ids>]
})
```

### Step 6: Present Summary

```text
┌─ Learning Captured ───────────────────────────────────────┐
│                                                           │
│  Type: [CORRECTION/PREFERENCE/PATTERN/etc.]               │
│  Skill: [skill-name or "general"]                         │
│  Scope: [personal/project/skill/org-wide]                 │
│                                                           │
│  Title: [learning title]                                  │
│  Confidence: [HIGH/MEDIUM/LOW] (occurrence #X)            │
│                                                           │
│  Linked to:                                               │
│  • Memory #42: [related learning]                         │
│  • Entity: [person/technology]                            │
│                                                           │
│  Memory ID: #[new_id]                                     │
└───────────────────────────────────────────────────────────┘
```

## Confidence Tracking

Track learning confidence through repetition:

| Occurrences | Confidence | Importance | Action                         |
| ----------- | ---------- | ---------- | ------------------------------ |
| 1           | Low        | 6-7        | Create memory                  |
| 2           | Medium     | 7-8        | Link to first, note repetition |
| 3+          | High       | 8-9        | Consider graduating to skill   |

When a pattern repeats:

```python
# Update existing memory
mcp__forgetful__execute_forgetful_tool("update_memory", {
  "memory_id": <existing_id>,
  "importance": min(10, current_importance + 1),
  "content": "<updated content noting repetition count>"
})
```

## Integration Points

### Proactive Loading

When a skill starts, query relevant learnings:

```python
mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<skill-name> preferences corrections patterns",
  "query_context": "Loading learnings before skill execution",
  "tags": ["skill-learning"],
  "k": 5
})
```

### Correction Detection

Note: Stop hooks were removed from the reflect system (see `.claude/settings.json`). The system no longer automatically monitors for corrections. Use `/reflect` manually after sessions or when you want to capture learnings.

## Additional Documentation

| Document                                     | Purpose                                   |
| -------------------------------------------- | ----------------------------------------- |
| [LEARNING_TYPES.md](LEARNING_TYPES.md)       | Detailed reference for all learning types |
| [SYNTHESIS.md](SYNTHESIS.md)                 | How to graduate learnings to skills       |
| [LIFECYCLE.md](LIFECYCLE.md)                 | Status, stale, and conflict management    |
| [VISUALIZATION.md](VISUALIZATION.md)         | Graph visualization features              |
| [PROACTIVE_LOADING.md](PROACTIVE_LOADING.md) | Pre-skill context injection               |
| [HOOKS.md](HOOKS.md)                         | Hook configuration for automation         |

## Commands Reference

| Command               | Description                        | Details                                                       |
| --------------------- | ---------------------------------- | ------------------------------------------------------------- |
| `/reflect`            | Analyze session, capture learnings | [reflect.md](../../commands/reflect.md)                       |
| `/reflect status`     | Learning system health             | [reflect-status.md](../../commands/reflect-status.md)         |
| `/reflect synthesize` | Graduate learnings to skills       | [reflect-synthesize.md](../../commands/reflect-synthesize.md) |
| `/reflect graph`      | Visualize connections              | [reflect-graph.md](../../commands/reflect-graph.md)           |
| `/reflect stale`      | Find outdated learnings            | [reflect-stale.md](../../commands/reflect-stale.md)           |
| `/reflect conflicts`  | Find contradictions                | [reflect-conflicts.md](../../commands/reflect-conflicts.md)   |
