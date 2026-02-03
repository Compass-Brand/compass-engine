---
name: reflect-status
description: Display overview of learning system health, statistics, and recommendations
---

# Reflect Status - Learning System Health

Display overview of learning system health, statistics, and recommendations.

## Usage

```text
/reflect status
```

## Workflow

### Step 1: Gather Metrics

```python
# Get all learnings
all_learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "skill-learning",
  "query_context": "Getting all learnings for status",
  "tags": ["skill-learning"],
  "k": 100
})

# Get recent learnings
recent = mcp__forgetful__execute_forgetful_tool("get_recent_memories", {
  "days": 30,
  "tags": ["skill-learning"]
})
```

### Step 2: Calculate Statistics

- Count by type (correction, preference, pattern, edge-case, anti-pattern)
- Count by skill
- Count by state (active, synthesized, stale)
- Calculate confidence distribution

### Step 3: Identify Issues

- Learnings pending synthesis (importance 8+, not synthesized)
- Old learnings (>90 days without review)
- Potential conflicts

### Step 4: Display Report

```text
┌─ Learning System Status ──────────────────────────────────────┐
│                                                               │
│  Total Learnings: 47                                          │
│  Active: 32  │  Synthesized: 12  │  Obsolete: 3               │
│                                                               │
├─ By Type ─────────────────────────────────────────────────────┤
│                                                               │
│  Corrections:   ████████░░░░░░░░  12 (25%)                    │
│  Preferences:   ██████████░░░░░░  15 (32%)                    │
│  Patterns:      ████████████░░░░  18 (38%)                    │
│  Edge Cases:    ██░░░░░░░░░░░░░░   2 (4%)                     │
│  Anti-patterns: ░░░░░░░░░░░░░░░░   0 (0%)                     │
│                                                               │
├─ Health Indicators ───────────────────────────────────────────┤
│                                                               │
│  ⚠️  5 learnings pending synthesis                            │
│  ⚠️  3 learnings older than 90 days                           │
│  ✅ No conflicts detected                                     │
│                                                               │
├─ Recommendations ─────────────────────────────────────────────┤
│                                                               │
│  • Run `/reflect synthesize code-generation`                  │
│  • Run `/reflect stale` to review old learnings               │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Reference

See `.claude/skills/reflect/LIFECYCLE.md` for detailed documentation.
