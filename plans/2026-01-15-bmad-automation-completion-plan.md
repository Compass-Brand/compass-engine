# BMAD Automation Completion Plan

**Date:** 2026-01-15
**Status:** CONFIGURATION COMPLETE - INTEGRATION PENDING
**Completed:** 2026-01-15 (Configuration Layer)
**Purpose:** Map every file requiring modification for full BMAD automation

> **⚠️ CRITICAL FINDING (2026-01-15 Analysis):** The automation *configuration* is complete, but the *integration* into the execution flow is missing. Claude doesn't execute XML conditionals - it reads them as text. The current implementation is **declarative** (describes what should happen) but not **imperative** (doesn't tell Claude to actually do it). See "Integration Gap Analysis" section below.

---

## Implementation Status: COMPLETE

### Files Created (5 files)
1. `_bmad/core/tasks/parallel-coordinator.xml` - Parallel workflow execution
2. `_bmad/core/tasks/rollback-to-checkpoint.xml` - Checkpoint rollback mechanism
3. `_bmad/bmm/workflows/2-plan-workflows/prd/review-automation.yaml` - PRD review automation
4. `_bmad/bmm/workflows/3-solutioning/create-architecture/review-automation.yaml` - Architecture review automation
5. `_bmad/bmb/workflows/parallel-validation.yaml` - 6-validator parallel validation

### Step Files Updated (~140 files)
All step files across BMM, Core, and BMB modules received AUTOMATION BEHAVIOR sections with:
- Tier loading from workflow.yaml
- Behavior announcements based on tier level
- Checkpoint markers at key decision points

**BMM Module (66 files):**
- PRD: 12 files (checkpoints: 03, 06, 09, 11)
- create-architecture: 8 files (checkpoints: 02, 04, 06, 08)
- create-ux-design: 15 files (checkpoints: 03, 07, 11, 14)
- create-epics-and-stories: 4 files (checkpoints: 02, 04)
- check-implementation-readiness: 6 files (checkpoints: 02, 04, 06)
- quick-dev: 6 files (checkpoints: 02, 04, 05)
- create-tech-spec: 4 files (checkpoints: 02, 04)
- create-product-brief: 7 files (checkpoints: 02, 04, 06)
- generate-project-context: 3 files (checkpoints: 02, 03)

**Core Module (11 files):**
- brainstorming: 8 files (checkpoints: 02 variants, 04)
- party-mode: 3 files (checkpoints: 02, 03)

**BMB Module (63 files):**
- create-workflow: 9 files (checkpoints: 03, 06, 09)
- create-module: 12 files (checkpoints: 03, 06, 08, 10, 11)
- edit-workflow: 5 files (checkpoints: 02, 04)
- edit-module: 21 files (checkpoints: 02, 05, 07)
- workflow-compliance-check: 8 files (checkpoints: 02, 04, 05, 08)

### Final Review Verdict: APPROVED_WITH_NOTES
- All created files pass structural validation
- Step file automation sections correctly added
- Minor placement inconsistencies in 2 edit-module step files (cosmetic only)

### Gap Remediation (2026-01-15)
After verification, 17 BMM workflows were found missing `automation:` sections in their workflow.yaml files. These were added:

**4-implementation workflows (2 files):**
- `correct-course/workflow.yaml` - Change management automation
- `retrospective/workflow.yaml` - Epic completion review automation

**document-project (1 file):**
- `document-project/workflow.yaml` - Brownfield documentation automation

**excalidraw-diagrams (4 files):**
- `create-dataflow/workflow.yaml` - DFD creation automation
- `create-diagram/workflow.yaml` - General diagram automation
- `create-flowchart/workflow.yaml` - Flowchart automation
- `create-wireframe/workflow.yaml` - Wireframe automation

**testarch (8 files):**
- `atdd/workflow.yaml` - ATDD test generation automation
- `automate/workflow.yaml` - Test automation expansion
- `ci/workflow.yaml` - CI/CD pipeline scaffolding automation
- `framework/workflow.yaml` - Test framework initialization automation
- `nfr-assess/workflow.yaml` - NFR assessment automation
- `test-design/workflow.yaml` - Test planning automation
- `test-review/workflow.yaml` - Test quality review automation
- `trace/workflow.yaml` - Traceability matrix automation

**workflow-status (2 files):**
- `workflow-status/workflow.yaml` - Status checking automation
- `workflow-status/init/workflow.yaml` - Project initialization automation

**Result:** 31/31 BMM workflows now have automation sections (100% coverage)

---

## Integration Gap Analysis (2026-01-15)

A thorough analysis of the automation implementation reveals a fundamental architectural gap:

### The Problem

BMAD is a **prompt-driven system** - Claude reads markdown/XML files and follows instructions literally. However:

1. **XML elements are not executed** - Tags like `<automation-step-init>`, `<calculate-confidence>`, and `<auto-select condition="...">` are rendered as text. Claude doesn't have an XML parser that evaluates conditions.

2. **workflow.xml doesn't use automation config** - The core execution engine (`_bmad/core/tasks/workflow.xml`) has "yolo" mode for auto-proceeding but doesn't integrate with the tier/confidence system.

3. **Step files are declarative, not imperative** - Step files say "Tier-based rules: Tier 0-1 auto-proceed" but don't tell Claude to actually auto-proceed.

### What Exists (Configuration Layer) ✅

| Component | Status | Location |
|-----------|--------|----------|
| Core config automation section | Complete | `_bmad/core/config.yaml:automation` (lines 165-309) |
| Workflow automation sections | 37/37 | All workflow.yaml files |
| Core task files | 20+ files | `_bmad/core/tasks/*.xml` |
| Agent menu-handlers | All agents | XML `<menu-handlers>` sections |
| Step AUTOMATION BEHAVIOR | 131 files | XML sections in step files |

### What's Missing (Integration Layer) ❌

| Gap | Impact | Required Fix |
|-----|--------|--------------|
| No confidence calculation | Confidence scores never computed | Add explicit instructions in step files |
| No tier variable tracking | Tier not persisted across steps | Track in sprint-status.yaml |
| No auto-selection execution | XML conditions never evaluated | Convert XML to imperative markdown |
| workflow.xml ignores automation | Core engine doesn't read tier | Update workflow.xml to load automation config |
| Step files need imperative instructions | Describe rules but don't implement | Rewrite AUTOMATION BEHAVIOR sections |

### What Would Make It Work

For automation to function, step files need **literal instructions**, not XML declarations:

**Current (Declarative - doesn't work):**
```xml
<automation-step-init>
  <tier from="workflow.yaml:automation.tier" default="2" />
  <auto-select condition="confidence >= 80 AND tier <= 2">
    <choice>C</choice>
  </auto-select>
</automation-step-init>
```

**Required (Imperative - would work):**
```markdown
## BEFORE PRESENTING MENU - AUTOMATION CHECK

1. **Read tier:** Get automation.tier from workflow.yaml (default: 2)
2. **Announce mode:**
   - If tier ≤ 1: Output "🚀 Running in streamlined mode"
   - If tier ≥ 3: Output "🔍 Running with full checkpoints"
3. **Auto-proceed check:**
   - If tier ≤ 1 AND no errors in this step:
     - Skip the menu below
     - Output "✓ Auto-continuing (tier: {tier})"
     - Load and execute {nextStepFile} immediately
   - Otherwise: Present the menu and wait for input
```

### Recommendations

**Option A: Full Integration (High Effort)**
1. Rewrite all 131 step files to include imperative automation instructions
2. Update workflow.xml to read automation config and track tier/confidence
3. Add state tracking to sprint-status.yaml

**Option B: Simplified yolo Mode (Low Effort)**
1. Document that current "yolo" mode in workflow.xml is the automation option
2. Add tier presets that map to yolo on/off
3. Accept that this is binary (full automation or none)

**Option C: Hybrid Approach (Medium Effort)**
1. Create a pre-processor that converts XML to imperative markdown at runtime
2. Add tier tracking to workflow.xml initialization
3. Modify only key step files (those with menus)

### Verdict

The automation **configuration infrastructure** is well-designed and complete. The **integration into execution flow** requires additional work. Current BMAD workflows will NOT behave differently based on automation tiers until the integration layer is implemented.

---

## Implementation Roadmap (Added 2026-01-15 Deep Analysis)

### Critical Gap #4: Config Source Mismatch (NEW FINDING)

**Location:** All BMM workflow.yaml files (line 6)
**Problem:** workflow.yaml files point to `_bmad/bmm/config.yaml` as `config_source`, but that file has NO automation section!

```yaml
# In workflow.yaml files:
config_source: "{project-root}/_bmad/bmm/config.yaml"

# Then tries to reference:
automation:
  enabled: "{config_source}:automation.enabled"      # FAILS - doesn't exist!
  tier: "{config_source}:automation.default_tier"    # FAILS - doesn't exist!
```

The automation section exists only in `_bmad/core/config.yaml`, not `_bmad/bmm/config.yaml`.

### Full Gap Summary

| Gap | Priority | Description | Impact |
|-----|----------|-------------|--------|
| **#1: Config Source Mismatch** | P0 (Blocker) | BMM config has no automation section | All `{config_source}:automation.*` references fail |
| **#2: workflow.xml Ignores Automation** | P0 (Blocker) | Core engine doesn't read tier config | No tier-based behavior at runtime |
| **#3: No Automation Runtime** | P0 (Blocker) | No imperative instructions for Claude | Configuration is read but not acted upon |
| **#4: Step Files Declarative** | P1 (Major) | XML pseudo-code isn't executed | AUTOMATION BEHAVIOR sections are documentation only |

### Implementation Phases

#### Phase 1: Fix Config Source (2-3 hours) - P0 BLOCKER

**Goal:** Ensure `{config_source}:automation.*` references resolve correctly.

**Option A (Recommended): Add automation to BMM config**
```yaml
# _bmad/bmm/config.yaml - add at end:

# =============================================================================
# AUTOMATION CONFIGURATION (Inherited from core)
# =============================================================================
automation:
  enabled: true
  default_tier: 2
  # ... full automation section from _bmad/core/config.yaml
```

**Option B: Change all workflow.yaml config_source**
- Change ~31 files from `_bmad/bmm/config.yaml` to `_bmad/core/config.yaml`
- More invasive but keeps single source of truth

**Files to modify (Option A):**
- `_bmad/bmm/config.yaml` (1 file)

**Files to modify (Option B):**
- All 31 BMM workflow.yaml files

---

#### Phase 2: Create Automation Runtime (4-6 hours) - P0 BLOCKER

**Goal:** Create imperative document that Claude reads and follows.

**Create:** `_bmad/core/automation-runtime.md`

```markdown
# BMAD Automation Runtime

**When executing ANY BMAD workflow, follow these automation rules.**

## Initialization (Run at workflow start)

1. Read automation config from `{project-root}/_bmad/_config/config.yaml` (or BMM config)
2. Extract `automation.enabled` and `automation.default_tier`
3. Check workflow.yaml for tier override
4. Store tier as session variable
5. Announce: "🤖 Running in Tier {tier} automation mode"

## Tier Behaviors

| Tier | Name | Menu Behavior | Checkpoint Frequency |
|------|------|--------------|---------------------|
| 0 | Quick Fix | Auto-select if confidence ≥ 60% | Final only |
| 1 | Small Feature | Auto-select if confidence ≥ 70% | Final only |
| 2 | Medium Project | Auto-select if confidence ≥ 80% | Design + Final |
| 3 | Complex System | Auto-select if confidence ≥ 90% | Arch + Design + Final |
| 4 | Enterprise | Never auto-select | Every step |

## Confidence Calculation

At each decision point, calculate confidence:

| Signal | Weight | How to Evaluate |
|--------|--------|-----------------|
| Validation Result | 35% | APPROVED=35, APPROVED_WITH_NOTES=25, REVISE=10, REJECTED=0 |
| Memory Match | 25% | Strong=25, Partial=15, None=10, Contradicting=0 |
| Reviewer Agreement | 25% | Unanimous=25, Majority=15, Split=5, N/A=12 |
| Context Clarity | 15% | Clear=15, Multiple Valid=5, Ambiguous=0 |

**Total = sum of all applicable signals**

## Menu Handling

When you encounter a menu like `[A] Option A, [B] Option B, [C] Continue`:

1. Calculate confidence for the expected/default choice
2. Get tier threshold from table above
3. If confidence ≥ threshold:
   - Auto-select the expected option
   - Log: "✓ Auto-selected [{option}] (confidence: {X}%, tier: {tier})"
   - DO NOT present menu to user
4. If confidence < threshold:
   - Present menu to user
   - Wait for response

## Step Transitions

At the end of each step:

1. Check if this step has a mandatory checkpoint (from workflow.yaml)
2. Check tier rules:
   - Tier 0-1: Auto-proceed to next step
   - Tier 2: Checkpoint at key steps only
   - Tier 3-4: Checkpoint at most/all steps
3. If checkpoint required:
   - Summarize what was accomplished
   - Ask: "Continue to Step {N}? [Y/n]"
4. If no checkpoint:
   - Log: "→ Proceeding to Step {N}"
   - Load and execute next step immediately
```

---

#### Phase 3: Modify workflow.xml (3-4 hours) - P0 BLOCKER

**Goal:** Core execution engine reads and applies automation.

**Modify:** `_bmad/core/tasks/workflow.xml`

**Changes:**

1. **Add Step 0: Automation Initialization** (before current Step 1)
```xml
<step n="0" title="Automation Initialization">
  <substep n="0a" title="Load Automation Runtime">
    <mandate>Read and internalize {project-root}/_bmad/core/automation-runtime.md</mandate>
    <action>Follow ALL instructions in that document throughout this workflow</action>
  </substep>

  <substep n="0b" title="Determine Tier">
    <action>Read automation.default_tier from config (default: 2)</action>
    <action>Check workflow.yaml for tier override</action>
    <action>Store tier as session context</action>
  </substep>

  <substep n="0c" title="Announce Mode">
    <output>🤖 Running in Tier {tier} automation mode</output>
    <output if="tier <= 1">🚀 Streamlined execution - auto-proceeding when confident</output>
    <output if="tier >= 3">🔍 Full oversight - checkpoints at each step</output>
  </substep>
</step>
```

2. **Modify Step 2c (template-output handling)** - Add tier-based logic:
```xml
<substep n="2c" title="Handle template-output Tags (Tier-Aware)">
  <if tag="template-output">
    <mandate>Generate content for this section</mandate>
    <mandate>Save to file</mandate>

    <!-- AUTOMATION: Tier-based menu handling -->
    <automation-check>
      <calculate-confidence>
        <signal name="content_quality" weight="40">Was generation successful?</signal>
        <signal name="validation_pass" weight="35">Did validation pass?</signal>
        <signal name="memory_match" weight="25">Do patterns match known good?</signal>
      </calculate-confidence>

      <if confidence-meets-tier-threshold="true">
        <action>Auto-select [c] Continue</action>
        <log>✓ Auto-continuing (confidence: {confidence}%, tier: {tier})</log>
        <skip-menu/>
      </if>
    </automation-check>

    <!-- Only show menu if not auto-selected -->
    <if menu-not-skipped="true">
      <ask>[a] Advanced Elicitation, [c] Continue, [p] Party-Mode, [y] YOLO</ask>
    </if>
  </if>
</substep>
```

3. **Modify Step 2d** - Add tier-based step transitions:
```xml
<substep n="2d" title="Step Completion (Tier-Aware)">
  <automation-check>
    <if tier="0" OR tier="1">
      <action>Auto-proceed to next step</action>
      <log>→ Auto-proceeding to next step (tier: {tier})</log>
    </if>
    <if tier="2">
      <action>Check if this is a key checkpoint step</action>
      <if checkpoint="true">
        <ask>Continue to next step? (y/n)</ask>
      </if>
      <else>
        <action>Auto-proceed</action>
      </else>
    </if>
    <if tier="3" OR tier="4">
      <ask>Continue to next step? (y/n/edit)</ask>
    </if>
  </automation-check>
</substep>
```

---

#### Phase 4: Simplify Step Files (Optional - 8-12 hours)

**Goal:** Replace complex XML pseudo-code with simple runtime references.

**Current (~140 files):**
```markdown
## AUTOMATION BEHAVIOR:

<automation-step-init>
  <tier from="workflow.yaml:automation.tier" default="2" />
  <behavior-announce>
    <output condition="tier <= 1">🚀 Step 2 running in streamlined mode</output>
  </behavior-announce>
</automation-step-init>

**Tier-based rules for this step:**
- **Tier 0-1:** Auto-proceed after validation confirmation
```

**Simplified:**
```markdown
## AUTOMATION BEHAVIOR

Follow automation-runtime.md rules for this step:
- Step number: 2
- Mandatory checkpoint: No
- Expected confidence signals: validation_result, context_clarity
```

This is optional because:
1. Phases 1-3 make the system functional
2. Step files can remain as documentation
3. Can be done incrementally per workflow

---

### Implementation Priority

| Phase | Priority | Effort | Impact |
|-------|----------|--------|--------|
| Phase 1: Fix Config Source | P0 | 2-3 hours | Unblocks all config references |
| Phase 2: Create Runtime | P0 | 4-6 hours | Provides imperative instructions |
| Phase 3: Modify workflow.xml | P0 | 3-4 hours | Enables tier-based execution |
| Phase 4: Simplify Step Files | P2 | 8-12 hours | Code cleanup, optional |

**Total for functional automation: 9-13 hours (Phases 1-3)**
**Total including cleanup: 17-25 hours (all phases)**

---

### Success Criteria

After implementing Phases 1-3, BMAD should:

1. ✅ Read automation config at workflow start
2. ✅ Announce tier mode ("Running in Tier 2 mode")
3. ✅ Calculate confidence at decision points
4. ✅ Auto-select menu options when confidence meets tier threshold
5. ✅ Auto-proceed between steps based on tier
6. ✅ Checkpoint at mandatory points regardless of tier
7. ✅ Log all automation decisions for debugging

### Testing Protocol

Test with a simple workflow (e.g., create-product-brief):

1. **Tier 0 Test:** Set tier=0, run workflow
   - Expected: Almost no prompts, auto-proceeds through most steps
   - Checkpoints only at final validation

2. **Tier 2 Test:** Set tier=2 (default), run same workflow
   - Expected: Checkpoints at key steps (design review, final)
   - Auto-proceeds through simple steps

3. **Tier 4 Test:** Set tier=4, run same workflow
   - Expected: Checkpoints at every step
   - Never auto-selects

---

## Executive Summary

The previous implementation (47 files) added **automation configuration stubs** - YAML config sections and documentation about automation. However, BMAD is **prompt-driven**: Claude reads step files and follows instructions literally. For automation to work, explicit instructions must be embedded **directly in the prompts Claude reads**.

### What Exists Now
- `workflow.yaml` files with `automation:` sections (configuration)
- `workflow.md` files with `## AUTOMATION CONFIGURATION` sections (documentation)
- `instructions.xml/md` files with `<automation-init>` blocks (initialization)

### What's Missing
1. **Core automation engine** - 20 task files that define execution logic
2. **Agent menu-handlers** - XML blocks with confidence calculation and auto-selection
3. **Step file automation checkpoints** - Explicit instructions at every decision point
4. **Prerequisites mapping** - Dependencies for parallelization
5. **Parallel workflow coordination** - Logic for dispatching multiple workflows concurrently
6. **Rollback mechanism** - Explicit procedure for reverting to checkpoints
7. **Early-stage review automation** - Rules for PRD, Architecture, UX reviews

---

## Part 1: Core Automation Engine (20 Files)

These files define the automation rules and execution logic.

### Phase 1.1: Master Configuration

**File:** `_bmad/_config/config.yaml`
**Section to Add:** `automation:` (~220 lines)

```yaml
automation:
  enabled: true
  default_tier: 2

  tier_behaviors:
    0:  # Full auto
      name: "Full Automation"
      menu_auto_select: true
      confidence_threshold: 60
      checkpoint_frequency: "final_only"
      party_mode_auto_trigger: false
      subagent_depth: 0

    1:  # Supervised auto
      name: "Supervised Auto"
      menu_auto_select: true
      confidence_threshold: 70
      checkpoint_frequency: "final_only"
      party_mode_auto_trigger: false
      subagent_depth: 1

    2:  # Balanced
      name: "Balanced"
      menu_auto_select: true
      confidence_threshold: 80
      checkpoint_frequency: "design_and_final"
      party_mode_auto_trigger: true
      subagent_depth: 2

    3:  # Cautious
      name: "Cautious"
      menu_auto_select: false
      confidence_threshold: 90
      checkpoint_frequency: "major_decisions"
      party_mode_auto_trigger: true
      subagent_depth: 3

    4:  # Full oversight
      name: "Full Oversight"
      menu_auto_select: false
      confidence_threshold: 100
      checkpoint_frequency: "every_step"
      party_mode_auto_trigger: true
      subagent_depth: 4

  confidence_signals:
    validation_verdict:
      weight: 35
      source: "last_validation_result"
      mapping:
        PASS: 100
        PASS_WITH_NOTES: 85
        NEEDS_WORK: 40
        FAIL: 0

    memory_match:
      weight: 25
      source: "forgetful_query_results"
      mapping:
        exact_match: 100
        similar_pattern: 75
        related_context: 50
        no_match: 25

    reviewer_agreement:
      weight: 25
      source: "party_mode_consensus"
      mapping:
        unanimous: 100
        majority: 75
        split: 50
        deadlock: 0

    fallback:
      weight: 15
      default: 50

  checkpoints:
    mandatory:
      - "pre_final_review"
      - "architecture_decision"
      - "external_integration"

    by_tier:
      0-1: ["final_only"]
      2: ["design", "final"]
      3: ["architecture", "design", "final"]
      4: ["every_step"]

  party_mode:
    auto_triggers:
      - condition: "stall_detected"
        threshold: 2  # consecutive identical outputs
      - condition: "confidence_below"
        threshold: 60
      - condition: "mandatory_checkpoint"
        tier_minimum: 3

    timeout_seconds: 300
    max_iterations: 5

  recovery:
    max_retries: 3
    backoff_seconds: [5, 15, 30]
    terminal_states:
      - "validation_failed_3x"
      - "user_abort"
      - "timeout_exceeded"

  timeouts:
    step_execution: 300
    validation: 120
    party_mode: 300
    memory_query: 30
```

### Phase 1.2: Project Detection

**File:** `_bmad/core/tasks/detect-project.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<task name="detect-project" version="1.0">
  <description>Detect project type and recommend automation tier</description>

  <inputs>
    <input name="project_root" type="path" required="true"/>
  </inputs>

  <outputs>
    <output name="project_level" type="integer" range="0-4"/>
    <output name="recommended_tier" type="integer" range="0-4"/>
    <output name="detection_confidence" type="integer" range="0-100"/>
    <output name="signals" type="object"/>
  </outputs>

  <execution>
    <step id="1">
      <action>scan_for_indicators</action>
      <scan-paths>
        <path>README.md</path>
        <path>package.json</path>
        <path>pyproject.toml</path>
        <path>docs/</path>
        <path>_bmad/</path>
      </scan-paths>
    </step>

    <step id="2">
      <action>classify_project</action>
      <rules>
        <rule level="0" keywords="spike,prototype,poc,experiment,learning"/>
        <rule level="1" keywords="internal,tool,utility,script,automation"/>
        <rule level="2" keywords="team,department,project,application"/>
        <rule level="3" keywords="production,enterprise,multi-team,platform"/>
        <rule level="4" keywords="regulated,compliance,audit,financial,healthcare,legal"/>
      </rules>
    </step>

    <step id="3">
      <action>calculate_tier</action>
      <formula>
        recommended_tier = project_level
        IF memory_exists("project_tier_override"):
          recommended_tier = memory.project_tier_override
      </formula>
    </step>

    <step id="4">
      <action>return_result</action>
      <format>
        {
          "project_level": {level},
          "recommended_tier": {tier},
          "detection_confidence": {confidence},
          "signals": {
            "keywords_found": [...],
            "file_indicators": [...],
            "memory_override": {override_if_any}
          }
        }
      </format>
    </step>
  </execution>
</task>
```

### Phase 1.3: Preflight Validation

**File:** `_bmad/core/tasks/preflight-validation.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<task name="preflight-validation" version="1.0">
  <description>Validate prerequisites before workflow execution</description>

  <inputs>
    <input name="workflow_name" type="string" required="true"/>
    <input name="required_artifacts" type="array"/>
    <input name="tier" type="integer"/>
  </inputs>

  <outputs>
    <output name="can_proceed" type="boolean"/>
    <output name="missing_artifacts" type="array"/>
    <output name="warnings" type="array"/>
  </outputs>

  <execution>
    <step id="1">
      <action>check_required_artifacts</action>
      <artifacts>
        <artifact workflow="create-architecture" requires="product-brief,prd"/>
        <artifact workflow="create-epics-and-stories" requires="prd,architecture"/>
        <artifact workflow="dev-story" requires="story-file,sprint-status"/>
        <artifact workflow="code-review" requires="implementation-complete"/>
      </artifacts>
    </step>

    <step id="2">
      <action>check_tool_availability</action>
      <tools>
        <tool name="forgetful" required_for="memory_integration"/>
        <tool name="serena" required_for="code_analysis"/>
        <tool name="context7" required_for="documentation"/>
      </tools>
    </step>

    <step id="3">
      <action>evaluate_readiness</action>
      <rules>
        <rule>IF missing_artifacts.length > 0: can_proceed = false</rule>
        <rule>IF tier >= 3 AND warnings.length > 0: can_proceed = false</rule>
        <rule>ELSE: can_proceed = true</rule>
      </rules>
    </step>
  </execution>
</task>
```

### Phase 1.4: Validation Type Detection

**File:** `_bmad/core/tasks/detect-validation-type.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<task name="detect-validation-type" version="1.0">
  <description>Detect appropriate validation approach for current context</description>

  <inputs>
    <input name="workflow_name" type="string"/>
    <input name="step_name" type="string"/>
    <input name="artifact_type" type="string"/>
  </inputs>

  <outputs>
    <output name="validation_type" type="enum" values="verdict,structural,checklist,custom"/>
    <output name="validators" type="array"/>
    <output name="success_criteria" type="object"/>
  </outputs>

  <execution>
    <step id="1">
      <action>classify_validation</action>
      <mappings>
        <!-- Verdict-based (PASS/FAIL/NEEDS_WORK) -->
        <map artifact="prd" type="verdict" validators="pm,architect"/>
        <map artifact="architecture" type="verdict" validators="architect,dev"/>
        <map artifact="story" type="verdict" validators="pm,dev"/>
        <map artifact="code-review" type="verdict" validators="dev,tea"/>

        <!-- Structural validation (schema compliance) -->
        <map artifact="workflow.yaml" type="structural" schema="workflow-schema"/>
        <map artifact="agent.md" type="structural" schema="agent-schema"/>
        <map artifact="step.md" type="structural" schema="step-schema"/>

        <!-- Checklist validation -->
        <map artifact="sprint-status" type="checklist" checklist="sprint-readiness"/>
        <map artifact="implementation" type="checklist" checklist="code-complete"/>
      </mappings>
    </step>

    <step id="2">
      <action>define_success_criteria</action>
      <criteria>
        <verdict-based>
          <pass condition="all_validators_pass"/>
          <pass_with_notes condition="majority_pass AND no_blockers"/>
          <needs_work condition="any_blocker"/>
          <fail condition="majority_fail"/>
        </verdict-based>

        <structural>
          <pass condition="schema_valid AND no_errors"/>
          <fail condition="schema_invalid OR errors_present"/>
        </structural>

        <checklist>
          <pass condition="all_required_checked"/>
          <needs_work condition="optional_unchecked"/>
          <fail condition="required_unchecked"/>
        </checklist>
      </criteria>
    </step>
  </execution>
</task>
```

### Phase 2.1-2.3: Agent Menu Handlers

**Files:**
- `_bmad/bmm/agents/dev.md` (add `<menu-handlers>` section)
- `_bmad/bmm/agents/architect.md` (add `<menu-handlers>` section)
- `_bmad/bmm/agents/pm.md` (add `<menu-handlers>` section)

**Template for Each Agent:**

```xml
<menu-handlers>
  <!-- Automation Configuration -->
  <automation-config>
    <load from="_bmad/_config/config.yaml:automation"/>
    <tier source="config.default_tier" override="user_specified"/>
  </automation-config>

  <!-- Confidence Calculation -->
  <confidence-calculator>
    <signal name="validation_verdict" weight="35">
      <source>last_validation_result</source>
      <map PASS="100" PASS_WITH_NOTES="85" NEEDS_WORK="40" FAIL="0"/>
    </signal>

    <signal name="memory_match" weight="25">
      <source>forgetful_query_results</source>
      <map exact="100" similar="75" related="50" none="25"/>
    </signal>

    <signal name="reviewer_agreement" weight="25">
      <source>party_mode_consensus</source>
      <map unanimous="100" majority="75" split="50" deadlock="0"/>
    </signal>

    <signal name="fallback" weight="15" default="50"/>
  </confidence-calculator>

  <!-- Auto-Selection Logic -->
  <auto-select>
    <rule condition="tier <= 1 AND confidence >= {tier_threshold}">
      <action>select_continue</action>
      <log>✓ Auto-continuing (tier: {tier}, confidence: {confidence}%)</log>
    </rule>

    <rule condition="tier == 2 AND confidence >= 80">
      <action>select_continue</action>
      <log>✓ Auto-selected Continue (confidence: {confidence}%)</log>
    </rule>

    <rule condition="tier >= 3 OR confidence < 80">
      <action>present_menu</action>
      <summary>Confidence: {confidence}% | Tier: {tier}</summary>
    </rule>
  </auto-select>

  <!-- Menu Types -->
  <handler type="workflow">
    <before-menu>
      <execute task="calculate-confidence"/>
      <execute task="check-auto-select"/>
    </before-menu>
    <options>
      <option key="C" action="continue" label="Continue to next step"/>
      <option key="A" action="advanced" label="Advanced options"/>
      <option key="P" action="party-mode" label="Multi-agent discussion"/>
    </options>
  </handler>

  <handler type="validation">
    <before-menu>
      <execute task="detect-validation-type"/>
      <execute task="run-validation"/>
      <update signal="validation_verdict" from="validation_result"/>
    </before-menu>
    <auto-proceed condition="verdict == PASS AND tier <= 2"/>
  </handler>

  <!-- Stall Detection -->
  <stall-detector>
    <track>consecutive_identical_outputs</track>
    <threshold>2</threshold>
    <action>trigger_party_mode</action>
    <escalate-after>party_mode_fails</escalate-after>
  </stall-detector>
</menu-handlers>
```

### Phase 2.4: Checkpoint Presentation

**File:** `_bmad/core/tasks/present-checkpoint.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<task name="present-checkpoint" version="1.0">
  <description>Present checkpoint based on confidence and tier</description>

  <inputs>
    <input name="confidence" type="integer"/>
    <input name="tier" type="integer"/>
    <input name="checkpoint_type" type="string"/>
    <input name="context" type="object"/>
  </inputs>

  <execution>
    <step id="1">
      <action>determine_presentation</action>
      <rules>
        <!-- High confidence, low tier: minimal -->
        <rule condition="confidence >= 80 AND tier <= 1">
          <presentation>minimal</presentation>
          <format>✓ {action} (confidence: {confidence}%)</format>
          <auto_proceed>true</auto_proceed>
        </rule>

        <!-- Medium confidence or tier 2: summary -->
        <rule condition="confidence >= 50 AND tier <= 2">
          <presentation>summary</presentation>
          <format>
            📊 Checkpoint: {checkpoint_type}
            Confidence: {confidence}% | Tier: {tier}
            Key Points: {summary}
            [C] Continue | [R] Review Details | [P] Party Mode
          </format>
          <auto_proceed condition="confidence >= 80">true</auto_proceed>
        </rule>

        <!-- Low confidence or high tier: full audit -->
        <rule condition="confidence < 50 OR tier >= 3">
          <presentation>full_audit</presentation>
          <format>
            ⚠️ Checkpoint Requires Review: {checkpoint_type}

            Confidence Breakdown:
            - Validation: {validation_signal}% (weight: 35%)
            - Memory Match: {memory_signal}% (weight: 25%)
            - Agreement: {agreement_signal}% (weight: 25%)
            - Base: {fallback_signal}% (weight: 15%)
            = Total: {confidence}%

            Context:
            {full_context}

            Options:
            [C] Continue anyway
            [R] Request changes
            [P] Party Mode discussion
            [A] Abort workflow
          </format>
          <auto_proceed>false</auto_proceed>
        </rule>
      </rules>
    </step>
  </execution>
</task>
```

### Phase 3: State Management

**File:** `_bmad/_config/sprint-status-schema.yaml`
**Addition:** `automation_state:` section

```yaml
automation_state:
  current_tier: 2
  session_id: "{uuid}"

  workflow_stack:
    - workflow: "dev-story"
      step: 5
      started_at: "{timestamp}"
      confidence_history: [75, 82, 88]

  checkpoints:
    - id: "cp-001"
      type: "design_review"
      timestamp: "{timestamp}"
      confidence: 82
      decision: "auto_proceed"

  recovery:
    last_stable_state: "cp-001"
    retry_count: 0

  party_mode:
    triggers_this_session: 0
    last_trigger_reason: null
```

**File:** `_bmad/core/tasks/persist-state.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<task name="persist-state" version="1.0">
  <description>Atomically persist automation state</description>

  <execution>
    <step id="1">
      <action>create_checkpoint</action>
      <data>
        <checkpoint_id>generate_uuid()</checkpoint_id>
        <timestamp>now()</timestamp>
        <workflow_state>current_workflow_stack</workflow_state>
        <confidence>current_confidence</confidence>
      </data>
    </step>

    <step id="2">
      <action>update_sprint_status</action>
      <path>_bmad-output/sprint-status.yaml:automation_state</path>
      <atomic>true</atomic>
    </step>

    <step id="3">
      <action>verify_persistence</action>
      <rollback_on_failure>true</rollback_on_failure>
    </step>
  </execution>
</task>
```

### Phase 3.3: Sprint Status Watcher

**File:** `_bmad/core/tasks/sprint-watcher.yaml`

```yaml
name: Sprint Status Watcher
description: Monitor sprint-status.yaml for changes and route to next workflow
version: "1.0"

watch:
  file: _bmad-output/sprint-status.yaml
  debounce_ms: 500
  deduplication_window_seconds: 30

  # Race prevention
  concurrency:
    method: compare_and_swap
    dual_check: true  # Check before and after read

  # Status cycling detection
  cycling_detection:
    enabled: true
    window_size: 5
    pattern_length: 3  # A->B->A->B->A = cycling
    on_cycling: pause_and_alert

events:
  on_story_complete:
    - check: has_more_ready_stories
    - if_true:
        action: check_parallel_opportunity
        parallel_threshold: 2  # If 2+ stories ready, consider parallel
    - if_single:
        route_to: dev-story
        auto_start: "tier <= 2"
    - if_none:
        check: epic_complete
        route_to: retrospective

  on_epic_complete:
    - route_to: retrospective
    - then: sprint-planning

  on_validation_failure:
    - increment: recovery.validation_attempts
    - check: max_iterations_reached
    - if_true: escalate_to_user
    - if_false: retry_with_fix

  on_code_review_complete:
    - check: all_stories_reviewed
    - if_true:
        route_to: epic_completion_check
    - if_false:
        route_to: next_code_review

parallel_dispatch:
  # When multiple stories are ready, dispatch in parallel
  trigger: ready_stories.length >= 2
  max_concurrent: 3  # Don't overwhelm
  dispatch_each:
    workflow: dev-story
    context: story_file
  aggregation:
    wait_for: all
    on_complete: batch_code_review
```

---

### Phase 4: Memory Integration

**File:** `_bmad/core/tasks/context-preload.yaml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<task name="context-preload" version="1.0">
  <description>Pre-load relevant context from Forgetful before workflow</description>

  <inputs>
    <input name="workflow_name" type="string"/>
    <input name="project_id" type="integer" default="1"/>
  </inputs>

  <execution>
    <step id="1">
      <action>query_workflow_patterns</action>
      <query>
        mcp__forgetful__execute_forgetful_tool("query_memory", {
          "query": "BMAD {workflow_name} patterns decisions lessons",
          "query_context": "Pre-loading context for {workflow_name}",
          "project_ids": [{project_id}],
          "tags": ["bmad", "workflow-pattern"],
          "include_links": true,
          "limit": 5
        })
      </query>
    </step>

    <step id="2">
      <action>query_recent_decisions</action>
      <query>
        mcp__forgetful__execute_forgetful_tool("query_memory", {
          "query": "{workflow_name} recent decisions changes",
          "query_context": "Looking for recent decisions affecting this workflow"
        })
      </query>
    </step>

    <step id="3">
      <action>apply_to_context</action>
      <output>
        <patterns>{query_1_results}</patterns>
        <recent_decisions>{query_2_results}</recent_decisions>
        <memory_confidence>{calculate_memory_signal()}</memory_confidence>
      </output>
    </step>
  </execution>
</task>
```

**File:** `_bmad/core/tasks/extract-learnings.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<task name="extract-learnings" version="1.0">
  <description>Extract and persist learnings after workflow completion</description>

  <inputs>
    <input name="workflow_name" type="string"/>
    <input name="outcome" type="string"/>
    <input name="decisions" type="array"/>
    <input name="issues_encountered" type="array"/>
  </inputs>

  <execution>
    <step id="1">
      <action>evaluate_learning_value</action>
      <rules>
        <rule condition="issues_encountered.length > 0">importance = 8</rule>
        <rule condition="decisions.length > 2">importance = 7</rule>
        <rule condition="outcome == 'success'">importance = 6</rule>
        <rule default="true">importance = 5</rule>
      </rules>
    </step>

    <step id="2" condition="importance >= 7">
      <action>create_memory</action>
      <query>
        mcp__forgetful__execute_forgetful_tool("create_memory", {
          "title": "BMAD {workflow_name}: {outcome_summary}",
          "content": "Workflow: {workflow_name}. Outcome: {outcome}. Decisions: {decisions}. Issues: {issues_encountered}. Lessons: {extracted_lessons}.",
          "context": "Post-workflow learning extraction",
          "keywords": ["bmad", "{workflow_name}", "learning"],
          "tags": ["workflow-pattern", "learning"],
          "importance": {importance},
          "project_ids": [1]
        })
      </query>
    </step>
  </execution>
</task>
```

### Phase 4.4: Memory Bridge

**File:** `_bmad/core/tasks/memory-bridge.yaml`

```yaml
name: Memory Bridge
description: Write workflow decisions and outcomes to Forgetful
version: "1.0"

write_triggers:
  - event: workflow_decision_made
    importance: 8
    template:
      title: "Decision: {decision_title}"
      content: "{decision_content}"
      keywords: [decision, {workflow_name}]

  - event: validation_fix_succeeded
    importance: 7
    template:
      title: "Fix Pattern: {error_type}"
      content: "Error: {error}. Fix: {fix_description}. Context: {context}."
      keywords: [fix, validation, {workflow_name}]

  - event: architectural_decision
    importance: 9
    template:
      title: "ADR: {decision_title}"
      content: "{decision_content}"
      keywords: [architecture, decision, adr]

  - event: workflow_complete
    importance: 6
    template:
      title: "Milestone: {workflow_name} complete"
      content: "{summary}"
      keywords: [milestone, {workflow_name}]

queue_on_failure:
  enabled: true
  queue_path: "_bmad-output/.memory-queue/"
  max_entries: 100
  overflow_strategy: fifo_evict
  cache_ttl_minutes: 5

  retry_schedule:
    initial_delay_minutes: 5
    max_delay_minutes: 30
    permanent_unavailable_hours: 4

execution:
  # Actual tool call for writing to memory
  write_memory: |
    mcp__forgetful__execute_forgetful_tool("create_memory", {
      "title": "{title}",
      "content": "{content}",
      "context": "BMAD automation: {workflow_name}",
      "keywords": {keywords},
      "tags": ["bmad", "automation", "{event_type}"],
      "importance": {importance},
      "project_ids": [1]
    })
```

---

### Phase 5: Party Mode & Subagents

**File:** `_bmad/core/workflows/party-mode-triggers.yaml`

```yaml
party_mode:
  auto_triggers:
    stall_detection:
      enabled: true
      consecutive_identical_threshold: 2
      action: "auto_invoke_party_mode"

    low_confidence:
      enabled: true
      threshold: 60
      tier_minimum: 2
      action: "auto_invoke_party_mode"

    mandatory_checkpoints:
      enabled: true
      tier_minimum: 3
      checkpoints:
        - "pre_final_review"
        - "architecture_decision"
        - "external_integration"
      action: "require_party_mode"

    deadlock:
      enabled: true
      indicator: "reviewer_agreement == deadlock"
      action: "escalate_to_user"

  configuration:
    default_agents: ["architect", "dev", "pm"]
    timeout_seconds: 300
    max_iterations: 5
    consensus_threshold: 0.66

  outcomes:
    unanimous:
      confidence_boost: 25
      action: "proceed_with_high_confidence"
    majority:
      confidence_boost: 10
      action: "proceed_with_notes"
    split:
      confidence_boost: 0
      action: "present_options_to_user"
    deadlock:
      confidence_boost: -20
      action: "escalate_to_user"
```

**File:** `_bmad/core/tasks/dispatch-subagent.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<task name="dispatch-subagent" version="1.0">
  <description>Dispatch subagent for parallel review or validation</description>

  <inputs>
    <input name="agent_type" type="string"/>
    <input name="task" type="string"/>
    <input name="context" type="object"/>
    <input name="timeout_seconds" type="integer" default="300"/>
  </inputs>

  <execution>
    <step id="1">
      <action>prepare_context</action>
      <context_fork>
        <include>current_artifact</include>
        <include>validation_criteria</include>
        <include>relevant_memories</include>
        <exclude>full_conversation_history</exclude>
      </context_fork>
    </step>

    <step id="2">
      <action>dispatch</action>
      <tool>Task</tool>
      <parameters>
        <subagent_type>{agent_type}</subagent_type>
        <prompt>{task_prompt}</prompt>
        <description>"{agent_type} review: {task}"</description>
        <run_in_background>true</run_in_background>
      </parameters>
    </step>

    <step id="3">
      <action>track_dispatch</action>
      <update>automation_state.active_subagents</update>
    </step>
  </execution>
</task>
```

### Phase 5.3: Code Review Automation

**File:** `_bmad/bmm/workflows/4-implementation/code-review/automation-rules.yaml`

```yaml
code_review_automation:
  adversarial_mode:
    enabled: true
    minimum_findings: 3
    maximum_findings: 10

  finding_categories:
    - code_quality
    - test_coverage
    - architecture_compliance
    - security
    - performance
    - maintainability

  iteration_tracking:
    max_iterations: 5
    escalate_after: 3

  auto_fix:
    enabled: true
    requires_user_approval: true
    categories_allowed:
      - formatting
      - simple_refactoring
      - test_additions
    categories_blocked:
      - security
      - architecture_changes

  verdicts:
    APPROVED:
      condition: "findings.blockers == 0 AND findings.total <= 3"
      action: "proceed_to_merge"
    APPROVED_WITH_NOTES:
      condition: "findings.blockers == 0 AND findings.total <= 7"
      action: "proceed_with_tracking"
    NEEDS_WORK:
      condition: "findings.blockers > 0 OR findings.total > 7"
      action: "return_for_fixes"
    REJECTED:
      condition: "findings.critical > 0 OR iterations >= max_iterations"
      action: "escalate_to_user"
```

### Phase 5.4: Parallel Validation (BMB)

**File:** `_bmad/bmb/workflows/parallel-validation.yaml`

```yaml
parallel_validation:
  enabled: true
  max_concurrent: 6

  validators:
    - id: "08a"
      name: "goal_validator"
      focus: "Goal alignment and clarity"

    - id: "08b"
      name: "role_validator"
      focus: "Role definition and boundaries"

    - id: "08c"
      name: "architecture_validator"
      focus: "Step-file architecture compliance"

    - id: "08d"
      name: "menu_validator"
      focus: "Menu system and options"

    - id: "08e"
      name: "context_hub_validator"
      focus: "Context Hub integration"

    - id: "08f"
      name: "output_validator"
      focus: "Output format and structure"

  dispatch_strategy:
    mode: "parallel"
    wait_for: "all"
    timeout_seconds: 180

  aggregation:
    method: "weighted_average"
    weights:
      goal_validator: 20
      role_validator: 15
      architecture_validator: 25
      menu_validator: 15
      context_hub_validator: 10
      output_validator: 15

  verdicts:
    PASS:
      condition: "all_validators_pass"
      confidence_minimum: 90
    PASS_WITH_NOTES:
      condition: "majority_pass AND no_blockers"
      confidence_minimum: 70
    NEEDS_WORK:
      condition: "any_blocker OR confidence < 70"
    FAIL:
      condition: "majority_fail OR critical_issues"
```

---

## Phase 6: User Experience & Learning

### Phase 6.1: Feedback Learning

**File:** `_bmad/core/tasks/feedback-learning.yaml`

```yaml
name: Feedback Learning
description: Capture and store user feedback for future sessions
version: "1.0"

explicit_feedback:
  patterns:
    positive:
      - "good choice"
      - "that's right"
      - "remember this"
      - "always do this"
    negative:
      - "don't do that"
      - "stop doing"
      - "never"
      - "wrong"
    preference:
      - "I prefer"
      - "I like"
      - "from now on"

  storage:
    target: forgetful
    importance: 7
    tags: [preference, feedback]

implicit_feedback:
  detection:
    user_correction:
      - pattern: user_modifies_auto_selection
        inference: selection_was_wrong
        action: reduce_confidence_for_similar

    user_override:
      - pattern: user_changes_tier
        inference: tier_suggestion_incorrect
        action: store_tier_preference

    repeated_escalation:
      - pattern: user_rejects_auto_continue > 3
        inference: confidence_threshold_too_low
        action: increase_threshold_for_workflow

  learning:
    adjust_thresholds: true
    store_pattern: true
    memory_template:
      title: "User Preference: {preference_type}"
      content: "User indicated {preference}. Context: {context}. Workflow: {workflow}."
      importance: 7
```

---

### Phase 6.2: Progress Display

**File:** `_bmad/core/tasks/progress-display.yaml`

```yaml
name: Progress Display
description: Configure progress display modes
version: "1.0"

modes:
  verbose:
    show_every_step: true
    show_timing: true
    show_confidence: true
    template: |
      📍 Step {step_number}/{total_steps}: {step_name}
      ⏱️ Duration: {duration}s
      📊 Confidence: {confidence}%
      ✅ Status: {status}

  summary:
    batch_updates: true
    batch_size: 5
    show_milestones: true
    template: |
      ▸ Completed {count} steps ({percentage}%)
      ▸ Current: {current_step}
      ▸ Next milestone: {next_milestone}

  silent:
    suppress_during: true
    show_at_end: true
    template: |
      **Workflow Complete**
      Steps: {completed}/{total}
      Duration: {duration}
      Interventions: {intervention_count}

  streaming:
    threshold_seconds: 30
    update_interval_seconds: 5
    template: |
      {step_name}... {percentage}%

rate_limiting:
  min_interval_seconds: 2
  force_pause_after: 10
  pause_message: |
    ⏸️ Pausing for review. {consecutive_count} operations completed.
    [C] Continue | [R] Review Details | [A] Abort
```

---

### Phase 6.3: Hook Discovery

**File:** `_bmad/core/tasks/hook-discovery.yaml`

```yaml
name: Hook Discovery
description: Discover and execute hooks from step frontmatter
version: "1.0"

discovery:
  source: step_frontmatter
  supported_hooks:
    - PreToolUse
    - PostToolUse
    - Stop
    - SessionStart

  session_start_special:
    once_support: true  # Support once: true flag

execution:
  timeout_seconds: 30

  output_limits:
    stdout_bytes: 65536   # 64KB
    stderr_bytes: 16384   # 16KB
    total_bytes: 262144   # 256KB

  on_failure:
    default: log_and_continue
    critical: abort_workflow

  critical_flag:
    field: critical
    values: [true]
```

---

## Phase 7: Parallel Workflow Coordination (NEW)

### Phase 7.1: Parallel Coordinator

**File:** `_bmad/core/tasks/parallel-coordinator.yaml`

```yaml
name: Parallel Coordinator
description: Coordinate parallel execution of multiple workflows
version: "1.0"

# This is the KEY missing piece for parallelization
parallel_execution:
  triggers:
    sprint_has_multiple_ready_stories:
      condition: "ready_stories.length >= 2"
      action: dispatch_parallel_dev_stories

    multiple_reviews_pending:
      condition: "pending_reviews.length >= 2"
      action: dispatch_parallel_code_reviews

    bmb_validation:
      condition: "workflow == bmb AND step == validation"
      action: dispatch_6_validators

  dispatch_logic:
    # How to actually dispatch parallel workflows
    parallel_dev_stories:
      description: "Run multiple dev-story workflows in parallel"
      steps:
        - identify_ready_stories:
            query: "stories WHERE status == 'ready' AND prerequisites_met"
        - calculate_batch_size:
            max: 5
            formula: "min(ready_stories.length, max_concurrent)"
        - dispatch_each:
            tool: Task
            for_each: ready_story
            parameters:
              subagent_type: "general-purpose"
              prompt: |
                Execute the dev-story workflow for story: {story_id}
                Story file: {story_file_path}
                Sprint status: {sprint_status_path}
                Tier: {current_tier}

                Follow the workflow at _bmad/bmm/workflows/4-implementation/dev-story/
              description: "dev-story: {story_id}"
              run_in_background: true
        - track_dispatches:
            store_in: automation_state.parallel_executions
            fields: [task_id, story_id, started_at]

    parallel_code_reviews:
      description: "Run multiple code-review workflows in parallel"
      steps:
        - identify_pending_reviews:
            query: "implementations WHERE status == 'complete' AND NOT reviewed"
        - dispatch_each:
            tool: Task
            for_each: pending_review
            parameters:
              subagent_type: "general-purpose"
              prompt: |
                Execute adversarial code review for: {implementation_id}
                Find 3-10 specific issues.
                Follow _bmad/bmm/workflows/4-implementation/code-review/
              run_in_background: true

  aggregation:
    wait_strategy:
      method: wait_for_all
      timeout_seconds: 1800  # 30 minutes
      on_timeout: escalate_to_user

    result_collection:
      poll_interval_seconds: 30
      tool: TaskOutput
      parameters:
        task_id: "{dispatch_task_id}"
        block: false

    completion_handling:
      all_success:
        action: proceed_to_next_phase
        update_status: true
      partial_failure:
        action: report_and_continue
        retry_failed: true
        max_retries: 2
      all_failure:
        action: escalate_to_user
        preserve_state: true
```

---

### Phase 7.2: Rollback to Checkpoint

**File:** `_bmad/core/tasks/rollback-to-checkpoint.yaml`

```yaml
name: Rollback to Checkpoint
description: Revert automation state to a previous checkpoint
version: "1.0"

triggers:
  - condition: user_requests_rollback
  - condition: terminal_failure_reached
  - condition: validation_failed_3x

rollback_procedure:
  steps:
    - validate_checkpoint:
        check: checkpoint_exists AND checkpoint.can_rollback
        on_failure: report_no_rollback_available

    - load_checkpoint_state:
        source: automation_state.checkpoints[{checkpoint_id}]
        fields:
          - workflow_context
          - step_id
          - validation_state
          - confidence_scores

    - revert_files:
        if_applicable: true
        backup_current: true
        restore_from: checkpoint.file_snapshots

    - update_automation_state:
        set:
          current_step: checkpoint.step_id
          recovery.rollback_count: increment
          recovery.last_rollback: now()

    - notify_user:
        message: |
          ⏪ Rolled back to checkpoint: {checkpoint_id}
          Step: {checkpoint.step_id}
          Created: {checkpoint.timestamp}

          [C] Continue from here | [R] Review checkpoint details

safeguards:
  max_rollbacks_per_session: 3
  prevent_rollback_past: first_checkpoint
  preserve_learnings: true  # Don't delete memories created after checkpoint
```

---

## Phase 8: Early-Stage Review Automation (NEW)

### Phase 8.1: PRD Review Automation

**File:** `_bmad/bmm/workflows/2-solutioning/create-prd/review-automation.yaml`

```yaml
name: PRD Review Automation
description: Automated validation of PRD quality
version: "1.0"

review_type: adversarial
reviewers: [pm, architect]

validation_criteria:
  completeness:
    weight: 30
    checks:
      - has_problem_statement
      - has_user_stories
      - has_acceptance_criteria
      - has_success_metrics

  clarity:
    weight: 25
    checks:
      - no_ambiguous_requirements
      - measurable_criteria
      - clear_scope_boundaries

  feasibility:
    weight: 25
    checks:
      - technical_constraints_identified
      - dependencies_documented
      - risks_assessed

  alignment:
    weight: 20
    checks:
      - aligns_with_product_brief
      - supports_business_goals

verdicts:
  APPROVED:
    condition: "all_weights >= 80"
    action: proceed_to_architecture
  APPROVED_WITH_NOTES:
    condition: "total_score >= 70 AND no_blockers"
    action: proceed_with_tracking
  NEEDS_WORK:
    condition: "any_blocker OR total_score < 70"
    action: return_for_revision
    max_iterations: 3
```

---

### Phase 8.2: Architecture Review Automation

**File:** `_bmad/bmm/workflows/2-solutioning/create-architecture/review-automation.yaml`

```yaml
name: Architecture Review Automation
description: Automated validation of architecture decisions
version: "1.0"

review_type: adversarial
reviewers: [architect, dev, tea]

# Architecture reviews are more consequential - higher thresholds
confidence_threshold_override: 85

validation_criteria:
  decision_quality:
    weight: 35
    checks:
      - alternatives_documented
      - trade_offs_analyzed
      - decision_rationale_clear
      - ADRs_created

  technical_soundness:
    weight: 30
    checks:
      - patterns_appropriate
      - scalability_considered
      - security_addressed
      - performance_requirements_met

  alignment:
    weight: 20
    checks:
      - supports_prd_requirements
      - fits_existing_architecture
      - migration_path_clear

  completeness:
    weight: 15
    checks:
      - diagrams_included
      - integration_points_defined
      - deployment_strategy_documented

verdicts:
  APPROVED:
    condition: "all_weights >= 85"
    action: proceed_to_epics
  APPROVED_WITH_NOTES:
    condition: "total_score >= 75 AND no_blockers"
    action: proceed_with_adr_updates
  NEEDS_WORK:
    condition: "any_blocker OR total_score < 75"
    action: return_for_revision

# Mandatory party mode for architecture decisions at tier 3+
mandatory_party_mode:
  condition: "tier >= 3"
  agents: [architect, dev, tea]
```

---

## Part 2: Step File Modifications (~100 Files)

Every step file that presents a menu needs explicit automation instructions.

### Template for Step Files (EXPLICIT VERSION)

Add this section **BEFORE** every `## Present MENU OPTIONS` section.

**CRITICAL**: This template uses ACTUAL tool calls, not prose descriptions. Claude must execute these literally.

```markdown
## AUTOMATION CHECKPOINT

**Execute the following automation logic BEFORE presenting any menu.**

### Step 1: Read Automation Configuration

Read the automation settings to get current tier and behavior:

```
USE Read tool to read: _bmad/_config/config.yaml

Extract values:
- automation.default_tier → store as CURRENT_TIER
- automation.tier_behaviors[CURRENT_TIER] → store as TIER_BEHAVIOR
- automation.confidence.high_threshold → store as HIGH_THRESHOLD (default: 80)
```

### Step 2: Calculate Confidence Score

Calculate confidence using weighted signals:

**Signal 1: Validation Verdict (35%)**
```
IF last_validation_result exists:
  - PASS → validation_score = 100
  - PASS_WITH_NOTES → validation_score = 85
  - NEEDS_WORK → validation_score = 40
  - FAIL → validation_score = 0
ELSE:
  validation_score = 50 (neutral)

validation_weighted = validation_score × 0.35
```

**Signal 2: Memory Match (25%)**
```
Execute:
mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "{current_step_topic} patterns decisions",
  "query_context": "Checking for relevant patterns at {step_name}",
  "project_ids": [1],
  "limit": 3
})

IF results.length >= 3: memory_score = 100
ELIF results.length >= 1: memory_score = 75
ELSE: memory_score = 25

memory_weighted = memory_score × 0.25
```

**Signal 3: Reviewer Agreement (25%)**
```
IF party_mode_was_invoked_this_session:
  - unanimous → agreement_score = 100
  - majority → agreement_score = 75
  - split → agreement_score = 50
  - deadlock → agreement_score = 0
ELSE:
  agreement_score = 50 (neutral)

agreement_weighted = agreement_score × 0.25
```

**Signal 4: Fallback (15%)**
```
fallback_weighted = 50 × 0.15 = 7.5
```

**Total Confidence:**
```
CONFIDENCE = validation_weighted + memory_weighted + agreement_weighted + fallback_weighted
```

### Step 3: Apply Auto-Selection Rules

**Execute this decision tree:**

```
IF CURRENT_TIER <= 1:
  IF CONFIDENCE >= TIER_BEHAVIOR.confidence_threshold:
    → DO NOT show menu
    → Output: "✓ Auto-continuing from {step_name} (confidence: {CONFIDENCE}%, tier: {CURRENT_TIER})"
    → Load and execute next step file immediately
    → STOP processing this step
  ELSE:
    → Continue to show menu

ELIF CURRENT_TIER == 2:
  IF CONFIDENCE >= 80:
    → DO NOT show menu
    → Output: "✓ Auto-selected [C] Continue (confidence: {CONFIDENCE}%)"
    → Load and execute next step file immediately
    → STOP processing this step
  ELSE:
    → Continue to show menu

ELIF CURRENT_TIER >= 3:
  → ALWAYS show menu (no auto-selection)
  → Prepend to menu: "📊 Confidence: {CONFIDENCE}% | Tier: {CURRENT_TIER}"
```

### Step 4: Stall Detection

**Check for identical outputs indicating a stall:**

```
Compare current step's output hash with previous 2 iterations.

IF hash matches previous 2 iterations:
  → Output: "🔄 Stall detected - same output 3 times"
  → Auto-invoke Party Mode workflow
  → Pass context: current_step, stall_reason, validation_history
  → DO NOT show menu until Party Mode resolves

To compute hash: SHA256 of validation_output + recommendation
Store in: automation_state.output_hashes[]
```

### Step 5: Present Menu (if not auto-selected)

If you reach this step, present the menu to the user with the confidence summary.
```

### Files to Modify by Module

#### BMM Module - Implementation Phase (~15 step files)

| Workflow | Steps | Files to Modify |
|----------|-------|-----------------|
| dev-story | 1-10 | `instructions.xml` - add checkpoints at steps 3, 5, 7, 9 |
| code-review | 1-7 | `instructions.xml` - add checkpoints at steps 2, 4, 6 |
| create-story | 1-5 | `instructions.xml` - add checkpoints at steps 2, 4 |
| sprint-planning | 1-6 | `instructions.md` - add checkpoints at steps 2, 4, 6 |
| sprint-status | 1-4 | `instructions.md` - add checkpoints at steps 2, 4 |

#### BMM Module - Planning Phase (~45 step files)

| Workflow | Step Count | Key Checkpoints |
|----------|------------|-----------------|
| create-architecture | 8 | steps 02, 04, 06, 08 |
| prd (create-prd) | 11 | steps 03, 06, 09, 11 |
| create-product-brief | 6 | steps 02, 04, 06 |
| create-epics-and-stories | 4 | steps 02, 04 |
| check-implementation-readiness | 6 | steps 02, 04, 06 |
| create-ux-design | 14 | steps 03, 07, 11, 14 |
| create-tech-spec | 8 | steps 02, 05, 08 |
| quick-dev | 5 | steps 02, 04, 05 |
| research | 18 | steps vary by type |

#### Core Module (~11 step files)

| Workflow | Step Count | Key Checkpoints |
|----------|------------|-----------------|
| brainstorming | 8 | steps 02, 05, 08 |
| party-mode | 3 | steps 02, 03 |

#### BMB Module (~30 step files)

| Workflow | Step Count | Key Checkpoints |
|----------|------------|-----------------|
| agent (tri-modal) | 16 create, 22 edit, 7 validate | mode-dependent |
| create-workflow | 12 | steps 03, 06, 09, 12 |
| create-module | 10 | steps 03, 06, 08, 10 |
| edit-workflow | 6 | steps 02, 04, 06 |
| edit-module | 21 | steps vary by edit type |
| workflow-compliance-check | 5 | steps 02, 04, 05 |

---

## Part 3: Agent File Modifications (13 Agents)

Each agent file needs the `<menu-handlers>` XML section added.

### BMM Agents (9 files)

| Agent | File | Priority |
|-------|------|----------|
| dev | `_bmad/bmm/agents/dev.md` | HIGH - most used |
| architect | `_bmad/bmm/agents/architect.md` | HIGH |
| pm | `_bmad/bmm/agents/pm.md` | HIGH |
| analyst | `_bmad/bmm/agents/analyst.md` | MEDIUM |
| sm | `_bmad/bmm/agents/sm.md` | MEDIUM |
| tea | `_bmad/bmm/agents/tea.md` | MEDIUM |
| tech-writer | `_bmad/bmm/agents/tech-writer.md` | LOW |
| ux-designer | `_bmad/bmm/agents/ux-designer.md` | LOW |
| quick-flow-solo-dev | `_bmad/bmm/agents/quick-flow-solo-dev.md` | LOW |

### BMB Agents (3 files)

| Agent | File | Priority |
|-------|------|----------|
| agent-builder | `_bmad/bmb/agents/agent-builder.md` | HIGH |
| module-builder | `_bmad/bmb/agents/module-builder.md` | MEDIUM |
| workflow-builder | `_bmad/bmb/agents/workflow-builder.md` | MEDIUM |

### Core Agents (1 file)

| Agent | File | Priority |
|-------|------|----------|
| bmad-master | `_bmad/core/agents/bmad-master.md` | HIGH |

---

## Part 4: Prerequisites Mapping for Parallelization

### Workflow Dependencies

```
Level 0 (No Prerequisites):
├── create-product-brief
├── research (any type)
└── brainstorming

Level 1 (Requires Level 0):
├── create-prd (requires: product-brief)
└── create-ux-design (requires: product-brief)

Level 2 (Requires Level 1):
├── create-architecture (requires: prd)
├── create-epics-and-stories (requires: prd, architecture)
└── check-implementation-readiness (requires: prd, architecture)

Level 3 (Requires Level 2):
├── sprint-planning (requires: epics-and-stories)
├── create-tech-spec (requires: architecture, story)
└── generate-project-context (requires: architecture)

Level 4 (Requires Level 3):
├── create-story (requires: sprint-planning, epics)
└── sprint-status (requires: sprint-planning)

Level 5 (Requires Level 4):
├── dev-story (requires: story, sprint-status)
└── quick-dev (requires: tech-spec OR story)

Level 6 (Requires Level 5):
├── code-review (requires: dev-story complete)
└── retrospective (requires: epic complete)
```

### Parallel Execution Opportunities

| Phase | Parallelizable Workflows | Prerequisites |
|-------|-------------------------|---------------|
| Analysis | research + brainstorming | none |
| Solutioning | create-prd + create-ux-design | product-brief |
| Solutioning | architecture + epics | prd |
| Implementation | Multiple stories within epic | sprint-planning |
| Review | Multiple code-reviews | implementations |
| BMB Validation | 6 validators (08a-08f) | workflow complete |

---

## Part 5: Implementation Order

### Phase 1: Core Engine (Priority: CRITICAL)
1. `_bmad/_config/config.yaml` - automation section
2. `_bmad/core/tasks/detect-project.xml`
3. `_bmad/core/tasks/preflight-validation.xml`
4. `_bmad/core/tasks/present-checkpoint.xml`

### Phase 2: High-Use Agents (Priority: HIGH)
5. `_bmad/bmm/agents/dev.md` - menu-handlers
6. `_bmad/bmm/agents/architect.md` - menu-handlers
7. `_bmad/bmm/agents/pm.md` - menu-handlers
8. `_bmad/core/agents/bmad-master.md` - menu-handlers

### Phase 3: Sprint Loop Steps (Priority: HIGH)
9. `dev-story/instructions.xml` - automation checkpoints
10. `code-review/instructions.xml` - automation checkpoints
11. `create-story/instructions.xml` - automation checkpoints
12. `sprint-planning/instructions.md` - automation checkpoints
13. `sprint-status/instructions.md` - automation checkpoints

### Phase 4: State & Memory (Priority: MEDIUM)
14. `_bmad/_config/sprint-status-schema.yaml` - automation_state
15. `_bmad/core/tasks/persist-state.xml`
16. `_bmad/core/tasks/context-preload.xml`
17. `_bmad/core/tasks/extract-learnings.xml`

### Phase 5: Party Mode & Subagents (Priority: MEDIUM)
18. `_bmad/core/workflows/party-mode-triggers.yaml`
19. `_bmad/core/tasks/dispatch-subagent.xml`
20. `_bmad/bmm/workflows/code-review/automation-rules.yaml`
21. `_bmad/bmb/workflows/parallel-validation.yaml`

### Phase 6: Remaining Agents (Priority: LOW)
22-27. Remaining BMM agents
28-30. BMB agents

### Phase 7: All Step Files (Priority: VARIES)
31+. Step file modifications (batch by workflow)

---

## Validation Checklist

After each phase:

- [ ] YAML/XML syntax validation passes
- [ ] Workflow can be invoked without errors
- [ ] Tier 0 behavior: auto-proceeds through steps
- [ ] Tier 2 behavior: checkpoints at design and final
- [ ] Tier 4 behavior: checkpoints at every step
- [ ] Party Mode triggers on low confidence
- [ ] Memory queries execute successfully
- [ ] State persists across steps

---

## File Count Summary (UPDATED)

| Category | File Count | Status |
|----------|------------|--------|
| Core config (config.yaml automation section) | 1 | TODO |
| Core tasks (Phase 1-4) | 12 | TODO |
| Agent menu-handlers | 13 | TODO |
| Step file checkpoints | ~100 | TODO |
| Workflow automation (Party mode, code review, BMB) | 4 | TODO |
| State schemas | 1 | TODO |
| UX & Learning tasks (Phase 6) | 3 | TODO |
| Parallel coordination tasks (Phase 7) | 2 | TODO |
| Early-stage review automation (Phase 8) | 2 | TODO |
| **TOTAL** | ~138 | TODO |

---

## Complete File List (All 28 Task/Config Files)

### Core Configuration (1 file)
1. `_bmad/_config/config.yaml` - Add `automation:` section (~220 lines)

### Core Tasks - Detection & Validation (4 files)
2. `_bmad/core/tasks/detect-project.yaml` - Project type detection
3. `_bmad/core/tasks/preflight-validation.yaml` - Pre-flight checks
4. `_bmad/core/tasks/detect-validation-type.yaml` - Validation type detection
5. `_bmad/core/tasks/present-checkpoint.yaml` - Checkpoint presentation

### Core Tasks - State Management (3 files)
6. `_bmad/_config/sprint-status-schema.yaml` - Add `automation_state:` section
7. `_bmad/core/tasks/persist-state.yaml` - State persistence
8. `_bmad/core/tasks/sprint-watcher.yaml` - Status monitoring & routing

### Core Tasks - Memory Integration (3 files)
9. `_bmad/core/tasks/context-preload.yaml` - Pre-load context from Forgetful
10. `_bmad/core/tasks/extract-learnings.yaml` - Post-workflow learning
11. `_bmad/core/tasks/memory-bridge.yaml` - Write decisions to memory

### Core Tasks - Multi-Agent (2 files)
12. `_bmad/core/workflows/party-mode-triggers.yaml` - Auto-trigger rules
13. `_bmad/core/tasks/dispatch-subagent.yaml` - Subagent dispatch

### Workflow Automation (4 files)
14. `_bmad/bmm/workflows/4-implementation/code-review/automation-rules.yaml` - Code review rules
15. `_bmad/bmb/workflows/parallel-validation.yaml` - BMB 6-validator parallel
16. `_bmad/bmm/workflows/2-solutioning/create-prd/review-automation.yaml` - PRD review
17. `_bmad/bmm/workflows/2-solutioning/create-architecture/review-automation.yaml` - Arch review

### UX & Learning (3 files)
18. `_bmad/core/tasks/feedback-learning.yaml` - User feedback capture
19. `_bmad/core/tasks/progress-display.yaml` - Progress display modes
20. `_bmad/core/tasks/hook-discovery.yaml` - Hook discovery

### Parallel Coordination (2 files)
21. `_bmad/core/tasks/parallel-coordinator.yaml` - Multi-workflow dispatch
22. `_bmad/core/tasks/rollback-to-checkpoint.yaml` - Rollback mechanism

### Agent Files (13 files - add menu-handlers XML)
23. `_bmad/bmm/agents/dev.md`
24. `_bmad/bmm/agents/architect.md`
25. `_bmad/bmm/agents/pm.md`
26. `_bmad/bmm/agents/analyst.md`
27. `_bmad/bmm/agents/sm.md`
28. `_bmad/bmm/agents/tea.md`
29. `_bmad/bmm/agents/tech-writer.md`
30. `_bmad/bmm/agents/ux-designer.md`
31. `_bmad/bmm/agents/quick-flow-solo-dev.md`
32. `_bmad/bmb/agents/agent-builder.md`
33. `_bmad/bmb/agents/module-builder.md`
34. `_bmad/bmb/agents/workflow-builder.md`
35. `_bmad/core/agents/bmad-master.md`

### Step Files (~100 files - add AUTOMATION CHECKPOINT)
- See "Files to Modify by Module" section above for complete breakdown

---

## Reference Materials

- Original automation design: `plans/2026-01-08-bmad-automation-design.md`
- Original automation design: `plans/2026-01-08-bmad-automation-design.md`
- Native implementation plan: `plans/2026-01-15-bmad-native-automation-plan.md`
- Workflow integration (completed): `plans/2026-01-15-bmad-workflow-integration-plan.md`
- Workflow maps: `docs/bmad-workflow-maps.md`
- Agent inventory: `docs/bmad-agent-inventory.md`
- Architecture overview: `docs/bmad-architecture-overview.md`
