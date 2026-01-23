# Learning Synthesis

This document describes how to synthesize accumulated learnings into actionable skill improvements.

## Overview

Synthesis transforms individual learnings stored in Forgetful Memory into:
1. Skill prompt improvements
2. New guidance documents
3. Agent behavior modifications
4. Workflow enhancements

## When to Synthesize

**Automatic triggers:**
- 5+ learnings accumulated for a single skill
- 3+ high-confidence (importance 9+) learnings on same topic
- User explicitly requests `/reflect synthesize`

**Manual triggers:**
- After completing a major project phase
- Before starting similar work
- During skill maintenance

## Synthesis Workflow

### Command: `/reflect synthesize [skill]`

### Step 1: Gather Learnings

Query all learnings for the target skill:

```python
# Get all learnings for skill
learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<skill-name> corrections preferences patterns",
  "query_context": "Gathering learnings for synthesis",
  "tags": ["skill-learning"],
  "k": 20,
  "include_links": true
})

# Get high-importance learnings specifically
high_priority = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<skill-name>",
  "query_context": "Finding high-priority learnings",
  "tags": ["skill-learning", "correction"],
  "min_importance": 9,
  "k": 10
})
```

### Step 2: Analyze Patterns

Group learnings by:
1. **Type** (correction, preference, pattern, edge-case, anti-pattern)
2. **Topic** (what aspect of the skill they affect)
3. **Confidence** (how many times observed)

Look for:
- Clusters of related learnings
- Contradictions that need resolution
- Gaps in coverage
- High-frequency corrections (indicating systematic issues)

### Step 3: Generate Improvement Proposals

For each cluster of learnings, generate a specific improvement:

```markdown
## Proposed Improvement: [Title]

**Source Learnings:**
- Memory #42: [CORRECTION] Always use async/await instead of .then()
- Memory #45: [PREFERENCE] Prefer explicit error handling
- Memory #51: [PATTERN] Wrap API calls in try-catch

**Improvement Type:** Skill prompt addition

**Proposed Text:**
When writing asynchronous code:
- Always use async/await syntax instead of .then() chains
- Wrap all API calls in try-catch blocks with explicit error handling
- Include meaningful error messages that help with debugging

**Impact:** Reduces corrections for async code patterns

**Confidence:** HIGH (3 related learnings, importance avg 8.3)
```

### Step 4: Present for Review

Format the synthesis report:

```
┌─ Learning Synthesis Report ──────────────────────────────────┐
│                                                               │
│  Skill: [skill-name]                                          │
│  Learnings Analyzed: [count]                                  │
│  Time Period: [date range]                                    │
│                                                               │
├─ Summary ─────────────────────────────────────────────────────┤
│                                                               │
│  Corrections: [count] (indicates systematic issues)           │
│  Preferences: [count] (user customization needed)             │
│  Patterns: [count] (successful approaches to codify)          │
│  Edge Cases: [count] (special handling needed)                │
│  Anti-patterns: [count] (things to explicitly avoid)          │
│                                                               │
├─ Proposed Improvements ───────────────────────────────────────┤
│                                                               │
│  1. [High Priority] Add async/await guidelines                │
│     Source: 3 learnings, avg importance 8.3                   │
│     Type: Skill prompt addition                               │
│                                                               │
│  2. [Medium Priority] Document error handling preference      │
│     Source: 2 learnings, avg importance 7.5                   │
│     Type: New guidance section                                │
│                                                               │
│  3. [Low Priority] Note Windows path edge case                │
│     Source: 1 learning, importance 7                          │
│     Type: Edge case documentation                             │
│                                                               │
├─ Recommended Actions ─────────────────────────────────────────┤
│                                                               │
│  [ ] Apply improvement #1 to skill prompt                     │
│  [ ] Create guidance document for #2                          │
│  [ ] Add #3 to edge cases documentation                       │
│  [ ] Mark source learnings as "synthesized"                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Step 5: Apply Improvements (with approval)

If user approves improvements:

**Option A: Update Skill File**
- Edit the SKILL.md to incorporate learnings
- Add new sections or modify existing guidance

**Option B: Create Supplementary Document**
- Create new file in skill folder (e.g., `ASYNC_GUIDELINES.md`)
- Reference from main SKILL.md

**Option C: Create Memory Document**
- For project-specific learnings that don't belong in skill
- Create a Forgetful document linking all memories

```python
# Create synthesis document
mcp__forgetful__execute_forgetful_tool("create_document", {
  "title": "[skill-name] Synthesized Learnings v[version]",
  "description": "Compiled learnings from [date range]",
  "content": "<synthesized guidance>",
  "document_type": "text",
  "tags": ["synthesis", "<skill-name>"],
  "project_id": <if project-specific>
})
```

### Step 6: Mark Learnings as Synthesized

After applying improvements, mark source learnings:

```python
# Update each learning memory
mcp__forgetful__execute_forgetful_tool("update_memory", {
  "memory_id": <learning_id>,
  "tags": ["skill-learning", "<type>", "<skill-name>", "synthesized"],
  "content": "<original content>\n\n---\nSynthesized into [target] on [date]"
})
```

## Synthesis Templates

### Template: Skill Prompt Addition

```markdown
## [Topic] Guidelines

Based on accumulated learnings:

**Do:**
- [Pattern 1 from learnings]
- [Pattern 2 from learnings]
- [Preference from learnings]

**Don't:**
- [Anti-pattern 1]
- [Anti-pattern 2]

**Edge Cases:**
- [Edge case 1]: [How to handle]
- [Edge case 2]: [How to handle]
```

### Template: Guidance Document

```markdown
# [Topic] Guidance

## Overview
[Brief description of what this covers]

## Key Principles
[Derived from preferences and patterns]

## Common Mistakes
[Derived from corrections and anti-patterns]

## Special Cases
[Derived from edge cases]

## Source Learnings
- Memory #[id]: [brief description]
- Memory #[id]: [brief description]
```

## Synthesis Metrics

Track synthesis effectiveness:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Correction reduction | -50% | Fewer same-type corrections after synthesis |
| Learning graduation | 80% | % of high-confidence learnings synthesized |
| Skill improvement | Monthly | At least one synthesis per active skill |

## Integration with Learning Lifecycle

```
[New Learning] → [Stored in Forgetful] → [Confidence grows with repetition]
                                                    ↓
                            [Threshold reached] → [Synthesis triggered]
                                                    ↓
                            [Improvement proposed] → [User reviews]
                                                    ↓
                            [Applied to skill] → [Learning marked synthesized]
                                                    ↓
                            [Future sessions benefit from improved skill]
```
