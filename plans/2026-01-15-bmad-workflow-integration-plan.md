# BMAD Workflow Integration Plan

**Date:** 2026-01-15
**Status:** Completed
**Purpose:** Integrate automation directly INTO actual BMAD workflow files

---

## Implementation Summary

### Completed Work

#### BMM Module (Pattern B - YAML + Instructions)
- **5 workflow.yaml files** - Added automation sections with tier-based behaviors, confidence signals, mandatory checkpoints
- **3 instructions.xml files** - Added `<automation-init>` blocks and checkpoint definitions (dev-story, code-review, create-story)
- **2 instructions.md files** - Added automation initialization and checkpoints (sprint-planning, sprint-status)

#### BMM Module (Pattern A - Step-File Architecture)
- **9 workflow.yaml files created** - New automation config files for each Pattern A workflow:
  - create-architecture, prd, create-product-brief, create-ux-design
  - create-epics-and-stories, check-implementation-readiness
  - quick-dev, create-tech-spec, generate-project-context
- **9 workflow.md files updated** - Added `config: workflow.yaml` frontmatter and `## AUTOMATION CONFIGURATION` section
- **1 sample step file updated** - create-architecture/step-01-init.md with automation behavior section

#### Core Module (Pattern C - Entry Workflows)
- **2 workflow.yaml files created** - brainstorming, party-mode
- **2 workflow.md files updated** - Added automation configuration sections

#### BMB Module (Pattern A - Step-File Architecture)
- **6 workflow.yaml files created** - agent, create-workflow, create-module, edit-workflow, workflow-compliance-check, edit-module
- **6 workflow.md files updated** - Added automation configuration sections

### Total Files Modified/Created
- **22 workflow.yaml files** (new)
- **19 workflow.md files** (updated)
- **3 instructions.xml files** (updated)
- **2 instructions.md files** (updated)
- **1 step file** (sample update)

**Grand Total: 47 files integrated with automation**

---

## Problem Statement

The previous implementation (Phase 1-6) created standalone configuration and task files:
- `_bmad/_config/config.yaml` (automation section)
- `_bmad/core/tasks/*.xml` (detection, validation tasks)
- `_bmad/bmm/agents/*.md` (menu-handlers XML sections)

However, these files are **not referenced by the actual workflow files** that Claude reads and executes. The automation needs to be integrated INTO:
- Step files (`step-XX-*.md`)
- Instructions files (`instructions.xml`, `instructions.md`)
- Workflow entry files (`workflow.md`, `workflow.yaml`)

## Integration Strategy

### Three Workflow Patterns to Modify

| Pattern | Structure | Example Workflows | Integration Approach |
|---------|-----------|-------------------|---------------------|
| **A: Step-File** | workflow.md + steps/*.md | create-architecture, prd, create-product-brief | Add `## AUTOMATION RULES` section to each step, modify `## Present MENU OPTIONS` |
| **B: YAML + Instructions** | workflow.yaml + instructions.xml | dev-story, code-review, sprint-planning | Add `automation:` section to YAML, add `<automation-rules>` to XML |
| **C: Entry Workflow** | workflow.md with inline execution | brainstorming, party-mode | Add automation hooks to INITIALIZATION section |

### Key Modifications Per Pattern

#### Pattern A: Step Files

Each step file gets:

```markdown
## AUTOMATION RULES (Tier-Based):

<automation-behavior tier="{current_tier}">
  <!-- Tier 0-1: Maximum automation -->
  <when tier="0-1">
    - Auto-select [C] Continue unless explicit user input requested
    - Skip confirmation checkpoints
    - Batch process without pause
  </when>

  <!-- Tier 2: Balanced -->
  <when tier="2">
    - Auto-select [C] if confidence >= 80%
    - Checkpoint at design and final steps only
    - Batch size: 5 operations before pause
  </when>

  <!-- Tier 3-4: Maximum oversight -->
  <when tier="3-4">
    - Present all menu options with summary
    - Checkpoint at major decision points
    - Require explicit confirmation
  </when>
</automation-behavior>

<stall-detection>
  - Track consecutive identical outputs
  - After 2 same outputs: auto-trigger Party Mode
  - After Party Mode fails: escalate to user
</stall-detection>
```

Menu options section modified to:

```markdown
## Present MENU OPTIONS:

<menu confidence="{calculated_confidence}" tier="{current_tier}">
  <!-- Auto-selection logic -->
  <auto-select condition="confidence >= 80 AND tier <= 2">
    <choice>C</choice>
    <announce>✓ Auto-continuing (confidence: {confidence}%, tier: {tier})</announce>
  </auto-select>

  <!-- Manual presentation -->
  <present condition="confidence < 80 OR tier >= 3">
    [C] Continue - Proceed to {next_step_name}
    [A] Advanced - Additional options
    [P] Party Mode - Multi-agent discussion
  </present>
</menu>
```

#### Pattern B: YAML + Instructions

workflow.yaml additions:

```yaml
automation:
  enabled: "{config_source}:automation.enabled"
  tier: "{config_source}:automation.default_tier"
  behavior: "{config_source}:automation.tier_behaviors"

  # Workflow-specific overrides
  checkpoints:
    - step: 5  # Implementation step
      condition: "tier >= 2"
    - step: 9  # Completion step
      condition: "always"

  # Menu handling
  menu_auto_select:
    enabled: "tier <= 2 AND confidence >= 80"
    log_format: "✓ Auto-selected {choice} (confidence: {confidence}%)"

  # Recovery
  max_iterations: 10
  stall_detection: true
```

instructions.xml additions:

```xml
<workflow>
  <!-- Add at top -->
  <automation-config>
    <load-tier from="config:automation.default_tier" />
    <load-behaviors from="config:automation.tier_behaviors" />
    <init-confidence default="50" />
  </automation-config>

  <!-- Add before each menu/decision point -->
  <automation-checkpoint step="N">
    <calculate-confidence>
      <signal name="validation_verdict" weight="35" source="last_validation_result" />
      <signal name="memory_match" weight="25" source="forgetful_query_results" />
      <fallback value="25" />
    </calculate-confidence>

    <auto-proceed condition="confidence >= {tier_threshold} AND tier <= 2">
      <log level="info">Auto-proceeding from step {N} (confidence: {confidence}%)</log>
    </auto-proceed>
  </automation-checkpoint>
</workflow>
```

#### Pattern C: Entry Workflows

Add to INITIALIZATION section:

```markdown
### Automation Initialization

<automation-init>
  <!-- Load tier from config or detect -->
  <load-tier>
    <from-config path="_bmad/_config/config.yaml:automation.default_tier" />
    <from-detection task="_bmad/core/tasks/detect-project.xml" />
    <from-user-override />
  </load-tier>

  <!-- Announce tier -->
  <announce>🎯 Operating at Tier {tier}: {tier_name}</announce>

  <!-- Load behavior profile -->
  <load-behavior profile="config:automation.tier_behaviors[{tier}]" />

  <!-- Query memory for context -->
  <pre-load-context>
    <forgetful-query topic="{workflow_topic}" />
    <apply-matches to="workflow_context" />
  </pre-load-context>
</automation-init>
```

---

## Implementation Order

### Phase 1: BMM Implementation Workflows (Sprint Loop)

Priority target since they run most frequently:

1. `dev-story` - Pattern B (YAML + XML)
2. `code-review` - Pattern B (YAML + XML)
3. `create-story` - Pattern B (YAML + XML)
4. `sprint-planning` - Pattern B (YAML + MD)
5. `sprint-status` - Pattern B (YAML + MD)

### Phase 2: BMM Planning/Solutioning Workflows

Step-file architecture workflows:

1. `create-architecture` - Pattern A (14 step files)
2. `prd` - Pattern A (11 step files)
3. `create-epics-and-stories` - Pattern A (4 step files)
4. `check-implementation-readiness` - Pattern A (6 step files)
5. `create-ux-design` - Pattern A (14 step files)

### Phase 3: BMM Analysis Workflows

1. `create-product-brief` - Pattern A (6 step files)
2. `research` - Pattern A (3 research types, ~18 step files)

### Phase 4: Core Module Workflows

1. `brainstorming` - Pattern C (8 step files)
2. `party-mode` - Pattern C (3 step files)
3. `workflow.xml` (core execution engine)

### Phase 5: BMB Module Workflows

1. `agent` workflow - tri-modal CREATE/EDIT/VALIDATE
2. `create-workflow` - Pattern A
3. `create-module` - Pattern B

---

## Files to Modify

### BMM Implementation Workflows (Pattern B)

| File | Modification |
|------|-------------|
| `_bmad/bmm/workflows/4-implementation/dev-story/workflow.yaml` | Add `automation:` section |
| `_bmad/bmm/workflows/4-implementation/dev-story/instructions.xml` | Add automation checkpoints |
| `_bmad/bmm/workflows/4-implementation/code-review/workflow.yaml` | Add `automation:` section |
| `_bmad/bmm/workflows/4-implementation/code-review/instructions.xml` | Add automation checkpoints |
| `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml` | Add `automation:` section |
| `_bmad/bmm/workflows/4-implementation/create-story/instructions.xml` | Add automation checkpoints |
| `_bmad/bmm/workflows/4-implementation/sprint-planning/workflow.yaml` | Add `automation:` section |
| `_bmad/bmm/workflows/4-implementation/sprint-planning/instructions.md` | Add automation hooks |
| `_bmad/bmm/workflows/4-implementation/sprint-status/workflow.yaml` | Add `automation:` section |
| `_bmad/bmm/workflows/4-implementation/sprint-status/instructions.md` | Add automation hooks |

### BMM Step-File Workflows (Pattern A)

Each step file in these workflows needs modifications:

| Workflow | Step Files | Sections to Modify |
|----------|-----------|-------------------|
| `create-architecture` | 8 steps | EXECUTION RULES, MENU OPTIONS |
| `prd` | 11 steps | EXECUTION RULES, MENU OPTIONS |
| `create-epics-and-stories` | 4 steps | EXECUTION RULES, MENU OPTIONS |
| `check-implementation-readiness` | 6 steps | EXECUTION RULES, MENU OPTIONS |

**Total: ~100 files across all modules**

---

## Validation Approach

After each phase:

1. **Syntax validation** - YAML/XML parsers
2. **Workflow execution test** - Run actual workflow at different tiers
3. **Automation behavior test** - Verify tier-based behavior works

---

## Reference Materials

- **Automation Config:** `_bmad/_config/config.yaml` (automation section)
- **Detection Tasks:** `_bmad/core/tasks/detect-*.xml`
- **Menu Handlers:** `_bmad/bmm/agents/*.md` (menu-handlers sections)
- **Original Plan:** `docs/plans/2026-01-15-bmad-native-automation-plan.md`
