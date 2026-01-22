# BMAD Automation Pivot: From Python to Native Implementation

**Date:** 2026-01-13
**Status:** Decision Document

## Background

During the implementation of BMAD automation epics (1, 2a, 2b, partial 3 and 4), we built Python code in `pcmrp_tools/bmad_automation/`. However, the original intent was to modify BMAD itself to support automation, not create an external Python system.

## The Problem

The Python code has no clear integration path with Claude Code:
- Could become MCP server, but would still need BMAD modifications
- No external orchestrator exists to intercept Claude Code conversations
- Essentially just detailed pseudocode/specifications

## The Solution: Native BMAD Implementation

BMAD already has an orchestration engine (`workflow.xml`) that can support everything we designed. The automation doesn't need external Python code - it can be implemented directly in BMAD's native structure.

---

## How Automation Should Be Implemented in BMAD

### 1. Tier-Based Automation via Config

In `_bmad/_config/config.yaml`, add an automation section:

```yaml
automation:
  default_tier: 2
  tier_behaviors:
    1:  # Maximum automation
      menu_selection: auto
      validation_checkpoints: skip
      batch_size: 10
      require_confirmation: false
    2:  # Balanced
      menu_selection: high_confidence_auto
      validation_checkpoints: summary
      batch_size: 5
      require_confirmation: on_escalation
    3:  # Maximum oversight
      menu_selection: always_prompt
      validation_checkpoints: full
      batch_size: 1
      require_confirmation: always
```

### 2. Menu Auto-Selection in Agent Files

The menu detection/selection logic translates directly to agent activation patterns. Example in `_bmad/bmm/agents/dev.md`:

```xml
<menu-handlers>
  <handler menu="proceed-options">
    <auto-select condition="confidence >= 80 AND tier <= 2">
      <default-choice>P</default-choice>
      <log>Auto-selected [P] Proceed (confidence: {confidence}%)</log>
    </auto-select>
  </handler>
</menu-handlers>
```

### 3. Workflow Routing via Instructions

Decision logic for "what comes next" can be added to workflow configs:

```yaml
post_completion:
  routing:
    - condition: "has_next_story AND tier <= 2"
      action: auto_route
      target: dev-story
    - condition: "epic_complete"
      action: auto_route
      target: retrospective
    - default:
      action: present_menu
```

### 4. Context Pre-Loading as Task

The "Context Pre-Loader" from Epic 2a becomes a task in `_bmad/core/tasks/`:

```yaml
# context-preload.yaml
name: Context Pre-Load
description: Query Forgetful for relevant patterns before workflow execution
steps:
  - query_forgetful:
      project_ids: [1]
      query: "{workflow_name} patterns"
  - store_context:
      target: workflow_context
```

### 5. State Persistence via Sprint Status

Epic 3's state management enhances `sprint-status.yaml`:

```yaml
automation_state:
  current_workflow: dev-story
  current_story: 3-1
  checkpoint:
    step: "Task 3.2"
    timestamp: 2026-01-13T10:30:00
  can_resume: true
```

---

## All 7 Epics Summary

| Epic | Stories | Status | Purpose |
|------|---------|--------|---------|
| 1 | 4 | Complete | Foundation Validation |
| 2a | 7 | Complete | Workflow Entry & Detection |
| 2b | 12 | Complete | Menu & Automation Core |
| 3 | 7 | In Progress | State & Recovery Management |
| 4 | 3 | Partial | Memory Integration |
| 5 | 13 | Not Started | Multi-Agent Orchestration |
| 6 | 4 | Not Started | Parallel Artifact Validation |
| 7 | 9 | Not Started | User Customization & Learning |

**Total:** 59 stories

---

## Implementation Phases (Native BMAD)

### Phase 1: Foundation (Epic 2a/2b concepts)
- Add `automation` section to config.yaml
- Add menu handlers to key agents (dev, architect, pm)
- Add routing logic to dev-story, create-story workflows

### Phase 2: State & Memory (Epic 3/4 concepts)
- Enhance sprint-status.yaml with checkpoint tracking
- Add context pre-load task
- Add Forgetful queries to workflow start

### Phase 3: Multi-Agent (Epic 5 concepts)
- Modify party-mode workflow with automation awareness
- Add subagent dispatch patterns

### Phase 4: Polish (Epic 6/7 concepts)
- Add user customization to config
- Add feedback collection

---

## Python Code Disposition

The Python code in `pcmrp_tools/bmad_automation/` has been **archived** to `docs/reference/automation-spec-archive/`.

It serves as detailed specification/pseudocode documenting:
- Class structures and relationships
- Test cases showing expected behavior
- Implementation patterns and edge cases

---

## BMAD Architecture Reference

```
_bmad/
├── _config/                 # Global manifests - ADD automation config here
├── core/                    # Foundation module
│   ├── agents/bmad-master.md
│   ├── tasks/workflow.xml   # CORE EXECUTION ENGINE
│   └── workflows/           # party-mode, brainstorming, etc.
├── bmb/                     # Builder module
│   ├── agents/              # agent-builder, workflow-builder
│   └── workflows/           # agent, create-module, etc.
└── bmm/                     # Methodology module
    ├── agents/              # ADD menu-handlers to these
    └── workflows/           # ADD routing logic to these
```

### Existing Automation Mechanisms in BMAD
- `#YOLO mode` - skips confirmations
- Sprint status tracking and routing
- Story auto-discovery in dev-story
- Context Hub auto-queries
- Decision trees in sprint-status workflow

---

## Key Decision

**The automation logic belongs IN BMAD itself, not in external Python tooling.**

The Python code was a specification exercise. The real implementation will modify:
1. Config files (YAML)
2. Agent files (XML in markdown)
3. Workflow configs (YAML)
4. Tasks (YAML)

No external orchestration code is needed.
