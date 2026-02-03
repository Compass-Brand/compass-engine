# Learning Lifecycle Management

This document describes how to manage the lifecycle of learnings: tracking status, finding stale content, and resolving conflicts.

## Learning States

```text
┌──────────┐     ┌──────────┐     ┌─────────────┐     ┌──────────┐
│  Active  │ ──► │ Repeated │ ──► │ Synthesized │ ──► │ Archived │
└──────────┘     └──────────┘     └─────────────┘     └──────────┘
     │                │                  │
     ▼                ▼                  ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Stale   │     │ Conflict │     │ Obsolete │
└──────────┘     └──────────┘     └──────────┘
```

| State       | Description                              | Tags                             |
| ----------- | ---------------------------------------- | -------------------------------- |
| Active      | Currently relevant learning              | `skill-learning`                 |
| Repeated    | Observed multiple times, high confidence | `skill-learning`, `repeated`     |
| Synthesized | Incorporated into skill/doc              | `skill-learning`, `synthesized`  |
| Stale       | May no longer be relevant                | `skill-learning`, `needs-review` |
| Conflict    | Contradicts another learning             | `skill-learning`, `conflict`     |
| Obsolete    | No longer valid                          | (marked obsolete in Forgetful)   |
| Archived    | Kept for history, not active             | `skill-learning`, `archived`     |

---

## Status Command

### Command: `/reflect status`

Provides overview of learning system health.

### Workflow

```python
# Get all learnings
all_learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "skill-learning",
  "query_context": "Getting all learnings for status report",
  "tags": ["skill-learning"],
  "k": 100
})

# Get recent learnings
# Note: get_recent_memories accepts only "limit" (1-100) and "project_ids" parameters
# Filter by tags in application code after retrieval
recent = mcp__forgetful__execute_forgetful_tool("get_recent_memories", {
  "limit": 50
})
# Filter for skill-learning tags in code:
# skill_learnings = [m for m in recent.get("memories", []) if "skill-learning" in m.get("tags", [])]

# Get high-importance unsynthesized learnings
pending_synthesis = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "skill-learning high importance",
  "query_context": "Finding learnings ready for synthesis",
  "tags": ["skill-learning"],
  "min_importance": 8,
  "k": 20
})
# Filter out those already tagged "synthesized"
```

### Output Format

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
├─ By Skill ────────────────────────────────────────────────────┤
│                                                               │
│  code-generation:    18 learnings (5 ready for synthesis)     │
│  debugging:          12 learnings (2 ready for synthesis)     │
│  git-operations:      8 learnings (0 ready for synthesis)     │
│  communication:       9 learnings (1 ready for synthesis)     │
│                                                               │
├─ Health Indicators ───────────────────────────────────────────┤
│                                                               │
│  ⚠️  5 learnings pending synthesis (importance 8+)            │
│  ⚠️  3 learnings older than 90 days without review            │
│  ✅ No conflicts detected                                     │
│  ✅ Recent activity: 8 learnings in last 30 days              │
│                                                               │
├─ Recommendations ─────────────────────────────────────────────┤
│                                                               │
│  • Run `/reflect synthesize code-generation` (5 pending)      │
│  • Run `/reflect stale` to review old learnings               │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Stale Learning Detection

### Command: `/reflect stale`

Finds learnings that may no longer be relevant.

### Stale Criteria

A learning is considered potentially stale if:

1. **Age-based:** Created more than 90 days ago AND not marked as synthesized or repeated
2. **Context-based:** Related to technology/version that may have changed
3. **Contradiction:** New learning contradicts it
4. **Unused:** Not queried/accessed in a long time

### Workflow

```python
# MCP tool invocation syntax (not executable code)

# Get old learnings
old_learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "skill-learning",
  "query_context": "Finding potentially stale learnings",
  "tags": ["skill-learning"],
  "k": 50
})
# Filter by created_at date > 90 days ago
# Exclude those tagged "synthesized", "repeated", or "reviewed-[date]"

# Check for version-specific learnings
# contains_version_info is a conceptual helper you would implement:
# - Check if learning.content contains version strings (e.g., "v1.2", "Next.js 13")
# - Check if learning.tags include version-related tags
# - Check if learning.keywords reference specific package versions
# Example logic: return any(pattern in l.content for pattern in [r"v\d+\.", "version"])
version_specific = [l for l in old_learnings if contains_version_info(l)]
```

### Output Format

```text
┌─ Stale Learning Review ───────────────────────────────────────┐
│                                                               │
│  Found 7 learnings that may need review:                      │
│                                                               │
├─ Age-Based (older than 90 days) ──────────────────────────────┤
│                                                               │
│  #23 [PREFERENCE] Use Jest for testing React components       │
│      Created: 2025-10-15 (98 days ago)                        │
│      Last accessed: Never                                     │
│      Action: [Keep] [Mark Obsolete] [Review]                  │
│                                                               │
│  #31 [PATTERN] Use Redux Toolkit for state management         │
│      Created: 2025-09-22 (122 days ago)                       │
│      Last accessed: 2025-11-01                                │
│      Action: [Keep] [Mark Obsolete] [Review]                  │
│                                                               │
├─ Version-Specific ────────────────────────────────────────────┤
│                                                               │
│  #45 [EDGE CASE] Next.js 13 app router image optimization     │
│      Mentions: Next.js 13 (current: 15.5)                     │
│      Action: [Update Version] [Mark Obsolete] [Review]        │
│                                                               │
├─ Potentially Superseded ──────────────────────────────────────┤
│                                                               │
│  #12 [PREFERENCE] Use .then() for promise chains              │
│      May conflict with: #42 [CORRECTION] Use async/await      │
│      Action: [Keep Both] [Mark #12 Obsolete] [Review]         │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Review Actions

**Keep:** Mark as reviewed, update last-reviewed timestamp

```python
mcp__forgetful__execute_forgetful_tool("update_memory", {
  "memory_id": <id>,
  "tags": ["skill-learning", "<type>", "reviewed-2026-01"]
})
```

**Mark Obsolete:**

```python
mcp__forgetful__execute_forgetful_tool("mark_memory_obsolete", {
  "memory_id": <id>,
  "reason": "No longer relevant: <reason>",
  "superseded_by": <newer_memory_id if applicable>
})
```

**Update:**

```python
mcp__forgetful__execute_forgetful_tool("update_memory", {
  "memory_id": <id>,
  "content": "<updated content with current info>",
  "tags": ["skill-learning", "<type>", "reviewed-2026-01"]
})
```

---

## Conflict Detection

### Command: `/reflect conflicts`

Finds learnings that contradict each other.

### Conflict Indicators

1. **Direct contradiction:** Same topic, opposite guidance
2. **Partial overlap:** Similar topic, incompatible approaches
3. **Scope conflict:** Personal vs project vs org-wide guidance conflicts

### Workflow

```python
# Get all active learnings grouped by topic
learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "skill-learning",
  "query_context": "Finding potential conflicts",
  "tags": ["skill-learning"],
  "k": 100,
  "include_links": True
})

# Group by keywords/topic
# Compare learnings within same topic for contradictions
# Flag pairs where one says "do X" and another says "don't do X"
```

### Conflict Detection Heuristics

| Pattern                                   | Conflict Type                         |
| ----------------------------------------- | ------------------------------------- |
| CORRECTION after PREFERENCE on same topic | Preference may be outdated            |
| Two PREFERENCES with opposite guidance    | User changed mind or context-specific |
| ANTI-PATTERN contradicts PATTERN          | Needs context clarification           |
| Different scopes (personal vs project)    | May both be valid                     |

### Output Format

```text
┌─ Conflict Analysis ───────────────────────────────────────────┐
│                                                               │
│  Found 2 potential conflicts:                                 │
│                                                               │
├─ Conflict #1: Direct Contradiction ───────────────────────────┤
│                                                               │
│  Memory #12: [PREFERENCE] Use .then() for promise chains      │
│  vs                                                           │
│  Memory #42: [CORRECTION] Always use async/await              │
│                                                               │
│  Analysis: Correction supersedes earlier preference           │
│  Recommendation: Mark #12 as obsolete, superseded by #42      │
│                                                               │
│  Actions: [Apply Recommendation] [Keep Both] [Manual Review]  │
│                                                               │
├─ Conflict #2: Scope Ambiguity ────────────────────────────────┤
│                                                               │
│  Memory #33: [PREFERENCE] Use tabs for indentation (personal) │
│  vs                                                           │
│  Memory #56: [PREFERENCE] Use spaces for indentation (project)│
│                                                               │
│  Analysis: Different scopes - both may be valid               │
│  Recommendation: Add scope clarification to both              │
│                                                               │
│  Actions: [Clarify Scopes] [Merge] [Manual Review]            │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Resolution Actions

**Apply Recommendation:**

```python
# For supersession
mcp__forgetful__execute_forgetful_tool("mark_memory_obsolete", {
  "memory_id": 12,
  "reason": "Superseded by newer correction",
  "superseded_by": 42
})
```

**Clarify Scopes:**

```python
# Add scope to both memories
mcp__forgetful__execute_forgetful_tool("update_memory", {
  "memory_id": 33,
  "content": "<content>\n\nScope: Personal preference (user's own projects)"
})

mcp__forgetful__execute_forgetful_tool("update_memory", {
  "memory_id": 56,
  "content": "<content>\n\nScope: Project-specific (Legacy System Analyzer)"
})
```

**Link as Related:**

```python
# If both valid in different contexts
mcp__forgetful__execute_forgetful_tool("link_memories", {
  "memory_id": 33,
  "related_ids": [56]
})
```

---

## Maintenance Schedule

| Task           | Frequency              | Command                       |
| -------------- | ---------------------- | ----------------------------- |
| Status check   | Weekly                 | `/reflect status`             |
| Stale review   | Monthly                | `/reflect stale`              |
| Conflict check | Monthly                | `/reflect conflicts`          |
| Synthesis      | When threshold reached | `/reflect synthesize [skill]` |

## Automation Opportunities

These lifecycle tasks can be triggered automatically:

1. **Status reminder:** Suggest `/reflect status` after 20+ learnings without check
2. **Stale alert:** Flag during session start if old learnings exist
3. **Conflict detection:** Run automatically when new learning created
4. **Synthesis trigger:** Suggest when 5+ learnings for same skill
