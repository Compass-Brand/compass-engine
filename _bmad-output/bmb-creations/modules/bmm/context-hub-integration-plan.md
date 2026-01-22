# BMM Context Hub Integration Plan

**Created:** 2026-01-08
**Session:** edit-session-bmm-20260108-083426
**Status:** Phase 1 Complete | Phase 2-4 Pending

---

## Overview

This plan integrates Serena (LSP-powered code navigation), Forgetful MCP (semantic memory), and Context7 (framework documentation) into the bmm module as background enhancements that improve BMAD's capabilities without requiring manual intervention.

**Design Principles:**
- **Toggleable** — All features controlled via config flags
- **Non-invasive** — Enhances existing patterns, doesn't replace them
- **Graceful degradation** — Works without these tools if unavailable
- **Background operation** — Automatic context gathering, not manual commands

---

## Phase 1: Foundation (Current)

### 1.1 Config Enhancement

**File:** `_bmad/bmm/config.yaml`

**Add:**
```yaml
# Context Hub Integration
# These features enhance BMAD with semantic memory, LSP code analysis, and framework docs
context_hub:
  enabled: true

  # Forgetful MCP - Semantic Memory
  memory:
    query_on_agent_start: true       # Agents query relevant memories at activation
    save_on_workflow_complete: true  # Save key outcomes/decisions as memories
    auto_link_artifacts: true        # Link created documents to memory entries
    default_project_id: null         # Set to project ID for scoped queries (null = all)

  # Serena - LSP Symbol Analysis
  serena:
    enabled: true
    use_for_code_analysis: true      # Use LSP for code exploration in dev workflows
    use_for_architecture: true       # Use for architecture analysis
    use_for_code_review: true        # Use for code review symbol tracing
    auto_activate_project: true      # Automatically activate Serena project

  # Context7 - Framework Documentation
  context7:
    enabled: true
    query_for_frameworks: true       # Query docs when working with known frameworks
    validate_patterns: true          # Validate observed patterns against official docs
```

### 1.2 Data Files

#### File 1: `_bmad/bmm/data/context-hub-integration.md`

**Purpose:** Comprehensive guide explaining how Context Hub tools integrate with bmm

**Contents:**
- When each tool is automatically invoked
- How to manually trigger context gathering
- Configuration options explained
- Troubleshooting guide

#### File 2: `_bmad/bmm/data/memory-patterns.md`

**Purpose:** Patterns for querying and saving memories

**Contents:**
- Query templates by agent role
- What to save and when
- Importance scoring guidelines
- Naming conventions for memories
- Linking strategies (entities, documents, artifacts)

#### File 3: `_bmad/bmm/data/serena-workflow-guide.md`

**Purpose:** When and how Serena is used in workflows

**Contents:**
- Serena vs grep decision matrix
- Symbol analysis patterns for each workflow type
- Integration with Forgetful (saving findings as memories)
- Performance considerations

### 1.3 Pilot Agent Modifications

**Agents:** architect, dev, analyst

**Modification Pattern:**
Add conditional activation step after config load:

```xml
<step n="2b">CONTEXT ENHANCEMENT (if context_hub.memory.query_on_agent_start):
    - Query Forgetful: "{role}-relevant patterns for {project_name}"
    - Store findings in {session_context} variable
    - If relevant memories found, briefly summarize for user
    - If context_hub.serena.auto_activate_project: Activate Serena
</step>
```

**Specific queries by agent:**

| Agent | Primary Query | Secondary Query |
|-------|---------------|-----------------|
| architect | "architecture patterns decisions {project}" | "technology stack rationale" |
| dev | "implementation patterns {project}" | "code conventions testing" |
| analyst | "research findings {domain}" | "stakeholder requirements" |

---

## Phase 2: Agent Rollout

### 2.1 Remaining Agents (6)

| Agent | Memory Query Focus | Serena | Context7 |
|-------|-------------------|--------|----------|
| pm | PRD patterns, requirements, stakeholder history | — | — |
| quick-flow-solo-dev | Same as dev + architecture | ✅ | ✅ |
| sm | Sprint patterns, velocity, retro learnings | — | — |
| tea | Test patterns, coverage strategies | ✅ | Testing frameworks |
| tech-writer | Doc patterns, terminology, style | ✅ | — |
| ux-designer | UX patterns, component decisions | — | UI frameworks |

### 2.2 Agent Enhancement Details

#### pm.md
```xml
<step n="2b">CONTEXT ENHANCEMENT:
    - Query: "PRD patterns requirements {project}"
    - Query: "stakeholder preferences decisions"
</step>
```

#### quick-flow-solo-dev.md
```xml
<step n="2b">CONTEXT ENHANCEMENT:
    - Query: "implementation patterns architecture {project}"
    - Activate Serena project
    - Query Context7 for framework: {detected_framework}
</step>
```

#### sm.md
```xml
<step n="2b">CONTEXT ENHANCEMENT:
    - Query: "sprint patterns velocity {project}"
    - Query: "retrospective learnings improvements"
</step>
```

#### tea.md
```xml
<step n="2b">CONTEXT ENHANCEMENT:
    - Query: "test patterns coverage {project}"
    - Activate Serena for test discovery
    - Query Context7 for testing framework docs
</step>
```

#### tech-writer.md
```xml
<step n="2b">CONTEXT ENHANCEMENT:
    - Query: "documentation patterns style {project}"
    - Activate Serena for symbol documentation
</step>
```

#### ux-designer.md
```xml
<step n="2b">CONTEXT ENHANCEMENT:
    - Query: "UX patterns components {project}"
    - Query Context7 for UI framework docs if applicable
</step>
```

---

## Phase 3: Workflow Integration

### 3.1 Phase 1 Workflows (Analysis)

#### create-product-brief/workflow.md
**Enhancement:**
- Pre-step: Query memories for related briefs, market research
- Post-step: Save brief summary as memory (importance: 7)

#### research/workflow.md
**Enhancement:**
- Pre-step: Query memories for existing research on topic
- During: Use Context7 for industry framework docs
- Post-step: Save key findings as memories (importance: 6-7)

### 3.2 Phase 2 Workflows (Planning)

#### create-ux-design/workflow.md
**Enhancement:**
- Pre-step: Query UX patterns, accessibility decisions
- During: Query Context7 for UI framework best practices
- Post-step: Save design decisions as memories

#### prd/workflow.md
**Enhancement:**
- Pre-step: Query related PRDs, requirement patterns
- Post-step: Save PRD summary and key requirements as memory (importance: 8)

### 3.3 Phase 3 Workflows (Solutioning)

#### check-implementation-readiness/workflow.md
**Enhancement:**
- Query: Architecture decisions, known technical debt
- Validate against memories for completeness

#### create-architecture/workflow.md (CRITICAL PATH)
**Full Integration:**
- Pre-step: Query all architecture-related memories
- During:
  - Use Serena for codebase symbol analysis
  - Use Context7 for framework architectural guidance
  - Query for related architectural decisions
- Post-step: Save architecture as memory (importance: 9)
- Auto-link to any created architecture documents

#### create-epics-and-stories/workflow.md
**Enhancement:**
- Pre-step: Query story patterns, estimation history
- Post-step: Save epic summaries as memories

### 3.4 Phase 4 Workflows (Implementation)

#### code-review/workflow.yaml
**Full Integration:**
- Use Serena: Trace symbol references, understand call hierarchies
- Query: Code standards, past review feedback patterns
- Post-step: Save significant findings as memories

#### correct-course/workflow.yaml
**Enhancement:**
- Query: Past course corrections, their outcomes
- Post-step: Save correction rationale as memory

#### create-story/workflow.yaml
**Enhancement:**
- Query: Similar stories, task breakdown patterns
- Use patterns to inform story structure

#### dev-story/workflow.yaml (CRITICAL PATH)
**Full Integration:**
- Pre-step:
  - Query memories for similar implementations
  - Activate Serena project
  - Query Context7 for relevant framework APIs
- During:
  - Use Serena for code navigation
  - Reference memory patterns for consistency
- Post-step: Save implementation notes as memory (importance: 7)

#### retrospective/workflow.yaml
**Enhancement:**
- Query: Past retrospectives, recurring themes
- Post-step: Save learnings as memories (importance: 7) — CRITICAL for organizational learning

#### sprint-planning/workflow.yaml
**Enhancement:**
- Query: Velocity history, capacity patterns
- Use historical data to inform planning

#### sprint-status/workflow.yaml
**Enhancement:**
- Query: Status reporting patterns
- Consistent status language

### 3.5 Quick Flow Workflows

#### create-tech-spec/workflow.md
**Enhancement:**
- Query: Architecture context, related specs
- Use Serena: Analyze code to be modified
- Post-step: Save spec summary as memory

#### quick-dev/workflow.md
**Full Integration:**
- Same as dev-story but streamlined
- Memory query + Serena + Context7

### 3.6 Utility Workflows

#### document-project/workflow.yaml
**Full Integration:**
- Use Serena: Extract accurate symbol information
- Query: Existing documentation patterns
- Generate symbol-accurate documentation

#### generate-project-context/workflow.md
**Full Integration:**
- Use Serena: Symbol-accurate context generation
- Query: Existing context, patterns
- More accurate than text-based analysis

### 3.7 TestArch Workflows (All 8)

**Common Enhancement Pattern:**
- Query: Test patterns, framework configurations
- Use Context7: Testing framework documentation
- Use Serena: Test file discovery and analysis

| Workflow | Specific Enhancement |
|----------|---------------------|
| atdd | Query: ATDD patterns, acceptance criteria examples |
| automate | Query: Automation patterns, selector strategies |
| ci | Query: CI configurations, pipeline patterns |
| framework | Query: Framework setup patterns |
| nfr-assess | Query: NFR benchmarks, past assessments |
| test-design | Query: Test design patterns, coverage strategies |
| test-review | Query: Review criteria, past findings |
| trace | Query: Traceability patterns |

---

## Phase 4: Validation & Refinement

### 4.1 Test Scenarios

1. **Agent Activation Test**
   - Start each agent
   - Verify memory queries execute
   - Confirm context is available

2. **Workflow Integration Test**
   - Run create-architecture with memory enhancement
   - Verify Serena activates
   - Confirm memories are saved

3. **End-to-End Flow**
   - Product brief → PRD → Architecture → Stories → Dev
   - Verify context carries through
   - Confirm memory accumulation

### 4.2 Metrics

| Metric | Target |
|--------|--------|
| Memory queries per session | 2-5 |
| Memories created per workflow | 1-3 |
| Context relevance (subjective) | High |
| Performance impact | Minimal (<2s delay) |

### 4.3 Refinement Areas

- Query effectiveness — tune query patterns
- Memory importance calibration
- Serena activation timing
- Context7 framework detection

---

## Implementation Checklist

### Phase 1 ✅ COMPLETE (2026-01-08)
- [x] Update config.yaml with context_hub section
- [x] Create data/context-hub-integration.md (501 lines)
- [x] Create data/memory-patterns.md (588 lines)
- [x] Create data/serena-workflow-guide.md (564 lines)
- [x] Modify agents/architect.md
- [x] Modify agents/dev.md
- [x] Modify agents/analyst.md
- [ ] Test pilot agents (manual testing recommended)

### Phase 2
- [ ] Modify agents/pm.md
- [ ] Modify agents/quick-flow-solo-dev.md
- [ ] Modify agents/sm.md
- [ ] Modify agents/tea.md
- [ ] Modify agents/tech-writer.md
- [ ] Modify agents/ux-designer.md
- [ ] Test all agents

### Phase 3
- [ ] Modify Phase 1 workflows (2)
- [ ] Modify Phase 2 workflows (2)
- [ ] Modify Phase 3 workflows (3)
- [ ] Modify Phase 4 workflows (7)
- [ ] Modify Quick Flow workflows (2)
- [ ] Modify Utility workflows (2)
- [ ] Modify TestArch workflows (8)
- [ ] Test critical paths

### Phase 4
- [ ] Run validation scenarios
- [ ] Measure metrics
- [ ] Document refinements
- [ ] Update guidance docs

---

## Rollback Strategy

All changes are tracked in the edit session document. If issues arise:

1. **Config rollback:** Set `context_hub.enabled: false`
2. **Agent rollback:** Remove step 2b from activation
3. **Full rollback:** Restore from `.backup/` directory

---

## Notes

- This integration assumes Forgetful MCP, Serena, and Context7 are available
- Graceful degradation: If a tool isn't available, skip that enhancement
- Config flags allow selective enabling/disabling
- Memory queries are scoped by project when `default_project_id` is set

