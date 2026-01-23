# Learning Visualization

This document describes how to visualize learning connections, patterns, and relationships.

## Overview

Visualizations help understand:
- How learnings connect to skills, projects, and entities
- Clusters of related learnings
- Knowledge gaps
- Learning evolution over time

## Graph Command

### Command: `/reflect graph [skill]`

Generates a visual map of learnings and their relationships.

### Workflow

```python
# Get learnings for skill (or all if no skill specified)
learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<skill-name or 'all'> learnings",
  "query_context": "Building learning graph visualization",
  "tags": ["skill-learning"],
  "k": 50,
  "include_links": true
})

# Get related entities
for learning in learnings:
    entities = mcp__forgetful__execute_forgetful_tool("get_entity_memories", {
      "entity_id": <linked_entity_id>
    })
```

### Mermaid Graph Output

Generate a Mermaid diagram showing relationships:

```mermaid
graph TB
    subgraph Skills
        S1[code-generation]
        S2[debugging]
        S3[git-operations]
    end

    subgraph "code-generation Learnings"
        L1[["#23 PREFERENCE<br/>Use async/await"]]
        L2[["#24 CORRECTION<br/>No arrow functions"]]
        L3[["#25 PATTERN<br/>Error boundaries"]]
    end

    subgraph "debugging Learnings"
        L4[["#30 PATTERN<br/>Binary search bugs"]]
        L5[["#31 EDGE-CASE<br/>Async stack traces"]]
    end

    subgraph Entities
        E1((Trevor))
        E2((Legacy Analyzer))
    end

    S1 --> L1
    S1 --> L2
    S1 --> L3
    S2 --> L4
    S2 --> L5

    L1 -.->|related| L2
    L3 -.->|related| L5

    E1 -->|preference| L1
    E2 -->|project| L3

    style L1 fill:#4CAF50
    style L2 fill:#f44336
    style L3 fill:#2196F3
    style L4 fill:#2196F3
    style L5 fill:#FF9800
```

### Color Legend

| Color | Learning Type |
|-------|--------------|
| Green (#4CAF50) | Preference |
| Red (#f44336) | Correction |
| Blue (#2196F3) | Pattern |
| Orange (#FF9800) | Edge Case |
| Purple (#9C27B0) | Anti-pattern |

### Graph Variations

#### 1. Skill-Focused Graph

Shows all learnings for a specific skill:

```
/reflect graph code-generation
```

```mermaid
graph LR
    subgraph "code-generation"
        direction TB
        C[Corrections<br/>5 items]
        P[Preferences<br/>8 items]
        PA[Patterns<br/>12 items]
        E[Edge Cases<br/>3 items]
        A[Anti-patterns<br/>2 items]
    end

    C --> C1[#23: Use async/await]
    C --> C2[#24: No arrow functions]

    P --> P1[#30: Prefer TypeScript]
    P --> P2[#31: Use named exports]

    C1 -.->|supersedes| P3[#12: Use .then]

    style C fill:#f44336
    style P fill:#4CAF50
    style PA fill:#2196F3
    style E fill:#FF9800
    style A fill:#9C27B0
```

#### 2. Timeline Graph

Shows learning evolution over time:

```
/reflect graph --timeline
```

```mermaid
gantt
    title Learning Timeline
    dateFormat  YYYY-MM-DD
    section Corrections
    #23 async/await           :done, 2025-11-15, 1d
    #24 arrow functions       :done, 2025-11-20, 1d
    section Preferences
    #30 TypeScript            :done, 2025-10-01, 1d
    #31 named exports         :done, 2025-12-05, 1d
    section Patterns
    #40 error boundaries      :done, 2025-12-10, 1d
    section Synthesis
    code-gen synthesis v1     :milestone, 2026-01-15, 0d
```

#### 3. Confidence Graph

Shows learning confidence based on repetition:

```
/reflect graph --confidence
```

```mermaid
graph TB
    subgraph "High Confidence (3+ occurrences)"
        H1[#23 async/await<br/>Seen 5 times]
        H2[#30 TypeScript<br/>Seen 4 times]
    end

    subgraph "Medium Confidence (2 occurrences)"
        M1[#24 arrow functions<br/>Seen 2 times]
        M2[#31 named exports<br/>Seen 2 times]
    end

    subgraph "Low Confidence (1 occurrence)"
        L1[#40 error boundaries<br/>Seen 1 time]
        L2[#41 suspense pattern<br/>Seen 1 time]
    end

    H1 -->|ready for| SYN[Synthesis]
    H2 -->|ready for| SYN

    style H1 fill:#4CAF50
    style H2 fill:#4CAF50
    style M1 fill:#FFC107
    style M2 fill:#FFC107
    style L1 fill:#9E9E9E
    style L2 fill:#9E9E9E
```

#### 4. Entity Relationship Graph

Shows how entities connect to learnings:

```
/reflect graph --entities
```

```mermaid
graph TB
    subgraph People
        P1((Trevor))
        P2((Team Lead))
    end

    subgraph Projects
        PR1[Legacy Analyzer]
        PR2[Competitor Toolkit]
    end

    subgraph Technologies
        T1{{React}}
        T2{{FastAPI}}
        T3{{PostgreSQL}}
    end

    subgraph Learnings
        L1[#23 async/await]
        L2[#30 TypeScript]
        L3[#40 error handling]
    end

    P1 -->|prefers| L1
    P1 -->|prefers| L2
    PR1 -->|requires| L3
    T1 -->|related| L2
    T2 -->|related| L3
```

## Text-Based Visualization

For environments without Mermaid rendering, provide ASCII visualization:

```
┌─ Learning Graph: code-generation ─────────────────────────────┐
│                                                               │
│  CORRECTIONS (5)              PREFERENCES (8)                 │
│  ├── #23 async/await          ├── #30 TypeScript              │
│  │   └── supersedes #12       │   └── confidence: HIGH        │
│  ├── #24 arrow functions      ├── #31 named exports           │
│  │   └── confidence: MED      │   └── linked to: #23          │
│  └── #25 strict types         └── #32 explicit returns        │
│                                                               │
│  PATTERNS (12)                EDGE CASES (3)                  │
│  ├── #40 error boundaries     ├── #50 null dates              │
│  │   └── linked to: #25       │   └── project: Legacy         │
│  ├── #41 suspense             └── #51 Windows paths           │
│  └── #42 lazy loading                                         │
│                                                               │
│  ANTI-PATTERNS (2)                                            │
│  ├── #60 N+1 queries                                          │
│  └── #61 sync in async                                        │
│                                                               │
│  ─────────────────────────────────────────────────────────────│
│  Legend: ─── direct link  ··· related  >>> supersedes         │
└───────────────────────────────────────────────────────────────┘
```

## Statistics Dashboard

Include summary statistics with visualizations:

```
┌─ Learning Statistics ─────────────────────────────────────────┐
│                                                               │
│  Total Learnings: 47        Active: 38    Synthesized: 9      │
│                                                               │
│  By Type:                                                     │
│  Corrections   ████████████░░░░░░░░  12 (26%)                 │
│  Preferences   ████████████████░░░░  16 (34%)                 │
│  Patterns      ██████████████░░░░░░  14 (30%)                 │
│  Edge Cases    ██░░░░░░░░░░░░░░░░░░   3 (6%)                  │
│  Anti-patterns ██░░░░░░░░░░░░░░░░░░   2 (4%)                  │
│                                                               │
│  By Confidence:                                               │
│  High (3+)     ████████░░░░░░░░░░░░   8 (17%)                 │
│  Medium (2)    ████████████░░░░░░░░  12 (26%)                 │
│  Low (1)       ██████████████████░░  27 (57%)                 │
│                                                               │
│  Top Skills:                                                  │
│  1. code-generation (18)  ████████████████████                │
│  2. debugging (12)        █████████████                       │
│  3. git-operations (8)    █████████                           │
│  4. communication (9)     ██████████                          │
│                                                               │
│  Health Score: 85/100                                         │
│  - No conflicts detected (+20)                                │
│  - 8 pending synthesis (-10)                                  │
│  - Recent activity (+15)                                      │
│  - Good distribution (+10)                                    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Interactive Features

When running in an environment that supports it:

### Drill-Down

```
User: /reflect graph code-generation
[Shows overview graph]

User: Show me more about #23
[Expands to show full memory content, links, and history]
```

### Filtering

```
User: /reflect graph --type=correction --skill=code-generation
[Shows only corrections for code-generation skill]

User: /reflect graph --confidence=high
[Shows only high-confidence learnings across all skills]
```

### Export

```
User: /reflect graph --export=mermaid
[Outputs raw Mermaid code for use in documentation]

User: /reflect graph --export=json
[Outputs structured JSON for external visualization tools]
```

## Implementation Notes

1. **Mermaid Generation:** Build diagram strings programmatically from memory data
2. **Layout Optimization:** Group related nodes, minimize edge crossings
3. **Responsive:** Use text-based fallback when Mermaid unavailable
4. **Caching:** Cache graph data for quick re-rendering with filters
5. **Links:** Make memory IDs clickable where possible
