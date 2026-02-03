---
name: reflect-synthesize
description: Analyze accumulated learnings for a skill and propose improvements to codify them
---

# Reflect Synthesize - Graduate Learnings to Skills

Analyze accumulated learnings for a skill and propose improvements to codify them.

## Usage

```text
/reflect synthesize [skill]
```

## Triggers

Run synthesis when:

- 5+ learnings accumulated for a skill
- 3+ high-confidence learnings on same topic
- Manual request

## Workflow

### Step 1: Gather Learnings

```python
learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<skill-name> corrections preferences patterns",
  "query_context": "Gathering learnings for synthesis",
  "tags": ["skill-learning"],
  "k": 20,
  "include_links": True
})
```

### Step 2: Analyze Patterns

Group learnings by:

1. Type (correction, preference, pattern, edge-case, anti-pattern)
2. Topic (what aspect they affect)
3. Confidence (occurrence count)

Look for:

- Clusters of related learnings
- High-frequency corrections
- Gaps in coverage

### Step 3: Generate Proposals

For each cluster:

```markdown
## Proposed Improvement: [Title]

**Source Learnings:**

- Memory #42: [description]
- Memory #45: [description]

**Improvement Type:** Skill prompt addition

**Proposed Text:**
[The actual text to add to the skill]

**Confidence:** HIGH (3 related learnings)
```

### Step 4: Present Report

```text
┌─ Learning Synthesis Report ──────────────────────────────────┐
│                                                               │
│  Skill: code-generation                                       │
│  Learnings Analyzed: 18                                       │
│                                                               │
├─ Proposed Improvements ───────────────────────────────────────┤
│                                                               │
│  1. [High Priority] Add async/await guidelines                │
│     Source: 3 learnings, avg importance 8.3                   │
│                                                               │
│  2. [Medium Priority] Document error handling                 │
│     Source: 2 learnings, avg importance 7.5                   │
│                                                               │
├─ Recommended Actions ─────────────────────────────────────────┤
│                                                               │
│  [ ] Apply improvement #1 to skill prompt                     │
│  [ ] Create guidance document for #2                          │
│  [ ] Mark source learnings as "synthesized"                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Step 5: Apply (with approval)

If user approves:

**Option A:** Update skill SKILL.md directly
**Option B:** Create supplementary document
**Option C:** Create Forgetful document for project-specific

### Step 6: Mark Learnings

```python
mcp__forgetful__execute_forgetful_tool("update_memory", {
  "memory_id": <id>,
  "tags": ["skill-learning", "<type>", "synthesized"]
})
```

## Reference

See `.claude/skills/reflect/SYNTHESIS.md` for detailed documentation.
