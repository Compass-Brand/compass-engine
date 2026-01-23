# Proactive Learning Loading

This document describes how to load relevant learnings before skill execution.

## Overview

Proactive loading ensures past learnings are applied to current work without requiring manual recall. When a skill starts, relevant learnings are automatically queried and injected into the context.

## When to Load

**Always load learnings when:**
- A skill is invoked (e.g., `/commit`, `/review-pr`)
- Starting work on a specific topic
- Beginning a new project task

**Skip loading when:**
- Quick one-off questions
- Learnings were already loaded this session
- No relevant skill context

## Loading Workflow

### Step 1: Identify Context

Determine what to query based on:
- Skill name being invoked
- Project context (from `project_ids`)
- Task description keywords

### Step 2: Query Learnings

```python
# Load learnings for specific skill
learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<skill-name> corrections preferences patterns anti-patterns",
  "query_context": "Loading learnings before <skill-name> execution",
  "tags": ["skill-learning"],
  "k": 5,
  "min_importance": 7
})
```

### Step 3: Prioritize by Type

Order of application:
1. **Anti-patterns** (importance 9+): Explicitly avoid these
2. **Corrections** (importance 9): Don't repeat past mistakes
3. **Preferences** (importance 8): Follow user's preferred approach
4. **Patterns** (importance 7): Use proven successful approaches
5. **Edge cases** (importance 7): Watch for special scenarios

### Step 4: Apply to Approach

```
┌─ Loaded Learnings ────────────────────────────────────────────┐
│                                                               │
│  For skill: code-generation                                   │
│                                                               │
│  ⛔ AVOID:                                                    │
│  • #60: Never use N+1 database queries                        │
│  • #42: Don't use arrow functions for React components        │
│                                                               │
│  ✅ APPLY:                                                    │
│  • #23: User prefers async/await over .then()                 │
│  • #30: Always include TypeScript types                       │
│                                                               │
│  ⚠️  WATCH FOR:                                               │
│  • #50: Handle null date fields explicitly                    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Integration Points

### Skill-Level Integration

Add to each skill's SKILL.md:

```markdown
## Before Starting

Query Forgetful Memory for relevant learnings:

\`\`\`python
mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<this-skill> corrections preferences",
  "query_context": "Loading learnings before execution",
  "tags": ["skill-learning"],
  "k": 5
})
\`\`\`

Apply any corrections or preferences found.
```

### Hook-Based Integration

Use PreToolUse hook (see [HOOKS.md](HOOKS.md)):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Skill(*)",
        "type": "prompt",
        "prompt": "Load relevant learnings from Forgetful Memory before executing this skill."
      }
    ]
  }
}
```

### Session-Start Integration

Load general learnings at session start:

```python
# At session start, load high-priority learnings
critical_learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "corrections anti-patterns high importance",
  "query_context": "Session start - loading critical learnings",
  "tags": ["skill-learning", "correction"],
  "min_importance": 9,
  "k": 10
})
```

## Project-Specific Loading

When working on a specific project:

```python
# Load project-specific learnings
project_learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<topic>",
  "query_context": "Loading project-specific learnings",
  "tags": ["skill-learning"],
  "project_ids": [1],  # Legacy System Analyzer
  "k": 5
})
```

## Caching Strategy

To avoid redundant queries:

1. Track what was loaded this session
2. Don't re-query for same skill within session
3. Clear cache if user makes new correction

```
Session State:
{
  "loaded_skills": ["code-generation", "debugging"],
  "loaded_at": "2026-01-22T10:30:00",
  "corrections_since_load": 0
}
```

## Display Format

When learnings are loaded, optionally show a brief summary:

**Verbose (detailed):**
```
Loaded 5 learnings for code-generation:
- 2 corrections to avoid
- 2 preferences to follow
- 1 edge case to watch for
```

**Concise (default):**
```
📚 5 learnings loaded for code-generation
```

**Silent (no display):**
Apply learnings without notification.

## Automatic vs Manual

| Mode | Description | When to Use |
|------|-------------|-------------|
| Automatic | Load via hook on skill invocation | Default behavior |
| Manual | User runs `/reflect load [skill]` | When debugging or reviewing |
| Silent | Load without display | Background operation |

## Command: Load Learnings

```
/reflect load [skill]
```

Explicitly load and display learnings for a skill:

```
┌─ Learnings Loaded: debugging ─────────────────────────────────┐
│                                                               │
│  Memory #30: [PATTERN] Binary search approach for bugs        │
│  Memory #31: [EDGE-CASE] Async stack traces need special      │
│              handling                                         │
│  Memory #42: [PREFERENCE] Always check logs first             │
│                                                               │
│  These learnings will be applied to this session.             │
└───────────────────────────────────────────────────────────────┘
```

## Effectiveness Tracking

Track whether proactive loading reduces corrections:

| Metric | Target |
|--------|--------|
| Corrections after loading | -50% vs without |
| Learnings applied per session | 3-5 average |
| User satisfaction | Fewer "I already told you" |
