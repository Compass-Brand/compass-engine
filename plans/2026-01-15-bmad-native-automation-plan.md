# BMAD Native Automation Implementation Plan

**Date:** 2026-01-15
**Status:** Implementation Plan
**Approach:** Native BMAD modifications (no external Python code)

## Overview

This plan implements BMAD automation by modifying BMAD's native files:
- Config files (YAML)
- Agent files (XML handlers in Markdown)
- Workflow files (YAML)
- Tasks (YAML)

This replaces the previous Python-based approach. The archived Python code in `docs/reference/automation-spec-archive/` serves as detailed specification reference.

---

## Requirements Coverage

### Original 7 Epics → Native Implementation Mapping

| Epic | FRs | Native Implementation |
|------|-----|----------------------|
| 1: Foundation Validation | 4 | Workflow pre-steps + validation task |
| 2a: Workflow Entry & Detection | 13 | Config + workflow-init enhancements |
| 2b: Menu & Automation Core | 22 | Agent handlers + config + task |
| 3: State & Recovery | 8 | Sprint-status.yaml enhancements |
| 4: Memory Integration | 3 | Task + workflow pre/post-steps |
| 5: Multi-Agent Orchestration | 21 | Party-mode workflow + agent handlers |
| 6: Parallel Artifact Validation | 6 | BMB workflow modifications |
| 7: User Customization & Learning | 15 | Config + feedback task |

**Total: 92 FRs + 15 NFRs covered**

---

## Implementation Phases

### Phase 1: Core Configuration & Tier System
**Delivers:** Epic 2a core + Epic 2b foundation + Epic 7 tier overrides

### Phase 2: Menu Automation & Agent Handlers
**Delivers:** Epic 2b menu handling + confidence system

### Phase 3: State Management & Recovery
**Delivers:** Epic 3 fully + Epic 2b recovery paths

### Phase 4: Memory Integration
**Delivers:** Epic 4 fully + Epic 2a context pre-loading

### Phase 5: Multi-Agent & Party Mode
**Delivers:** Epic 5 fully + Epic 6 parallel validation

### Phase 6: User Experience & Learning
**Delivers:** Epic 7 remaining features

---

## Phase 1: Core Configuration & Tier System

### 1.1 Create Automation Config Section

**File:** `_bmad/_config/config.yaml`

**Add:**
```yaml
# =============================================================================
# AUTOMATION CONFIGURATION
# =============================================================================
automation:
  enabled: true
  version: "1.0"

  # Default tier (can be overridden per-session)
  default_tier: 2

  # Tier detection keywords for auto-suggestion
  tier_keywords:
    0: [fix, typo, bug, patch, hotfix, tweak]
    1: [small, minor, simple, quick, add, update]
    2: [feature, implement, create, build, medium]
    3: [complex, system, refactor, redesign, major]
    4: [enterprise, platform, architecture, migration]

  # Tier-specific behavior profiles
  tier_behaviors:
    0:  # Quick fixes - maximum automation
      menu_selection: auto
      validation_checkpoints: final_only
      batch_size: unlimited
      require_confirmation: false
      party_mode: on_deadlock_only
      subagent_depth: none

    1:  # Small features - high automation
      menu_selection: auto
      validation_checkpoints: final_only
      batch_size: 10
      require_confirmation: false
      party_mode: on_deadlock_only
      subagent_depth: single

    2:  # Medium projects - balanced
      menu_selection: high_confidence_auto  # >= 80%
      validation_checkpoints: design_and_final
      batch_size: 5
      require_confirmation: on_escalation
      party_mode: on_deadlock_or_low_confidence
      subagent_depth: parallel_reviewers

    3:  # Complex systems - more oversight
      menu_selection: high_confidence_auto  # >= 80%
      validation_checkpoints: arch_design_final
      batch_size: 3
      require_confirmation: on_major_decisions
      party_mode: mandatory_pre_final
      subagent_depth: parallel_reviewers

    4:  # Enterprise - maximum oversight
      menu_selection: always_prompt
      validation_checkpoints: all_phases
      batch_size: 1
      require_confirmation: always
      party_mode: every_phase
      subagent_depth: parallel_plus_party

  # Confidence thresholds
  confidence:
    high_threshold: 80      # Auto-proceed
    medium_threshold: 50    # Summary checkpoint
    low_threshold: 0        # Full audit trail

    # Confidence calculation weights (must sum to 100)
    weights:
      validation_verdict: 35
      memory_match: 25
      reviewer_agreement: 25
      party_mode_outcome: 15

    # Fallback values
    default_no_signals: 25
    single_source_cap: 60
    calculation_failure: 30

  # Menu detection settings
  menu_detection:
    confidence_threshold: 70  # Points required to detect menu
    structural_markers:
      - pattern: "\\[([A-Z])\\]"
        points: 30
      - pattern: "^\\s*-\\s*\\[([A-Z])\\]"
        points: 25
      - pattern: "Continue\\?"
        points: 20
    position_validators:
      end_of_response: 15
      after_blank_line: 10
    false_positive_guards:
      - context: code_block
        penalty: -50
      - context: blockquote
        penalty: -40
      - context: example_content
        penalty: -30

  # Batch-continue settings
  batch_continue:
    pause_after_consecutive: 10  # Force pause after N consecutive auto-continues
    min_interval_seconds: 2      # Minimum time between menu presentations

  # Timeout hierarchy (seconds)
  timeouts:
    workflow: 1800        # 30 minutes
    nested_operation: 300 # 5 minutes
    agent: 60             # 1 minute
    party_round: 120      # 2 minutes
    human_selection: 300  # 5 minutes
    synchronization: 120  # 2 minutes
    exit_grace: 0.5       # 500ms

  # Recovery settings
  recovery:
    max_validation_iterations: 10
    max_same_error_retries: 3
    max_party_mode_rounds: 5
    stall_detection:
      enabled: true
      hash_algorithm: sha256
      escalate_after_attempts: 2

  # BMB-specific thresholds
  bmb:
    party_mode_triggers:
      blocking_errors_threshold: 3
      major_issues_threshold: 5
    advanced_elicitation_trigger:
      compliance_score_threshold: 70
    parallel_validation:
      max_concurrent: 6
      mutex_timeout_seconds: 5

  # Override methods (priority order: highest to lowest)
  override_priority:
    - explicit_tier      # "Use tier 3"
    - profile_switch     # "Switch to enterprise mode"
    - specific_settings  # "Auto-approve all menus"
    - natural_language   # "I prefer minimal interruptions"

  # Safety settings (cannot be overridden)
  safety:
    require_final_approval: true
    stall_detection_enabled: true
    max_iterations_enforced: true

  # Progress display modes
  progress:
    default_mode: summary  # verbose, summary, silent, streaming
    streaming_threshold_seconds: 30
```

**Covers:**
- FR5 (Tier Suggester keywords)
- FR6 (Task-level oversight)
- FR12a (Batch-continue sizes)
- FR17 (Timeout hierarchy)
- FR19e-j (Confidence weights and thresholds)
- FR36-39 (Configuration)
- FR48-50 (Tier overrides)
- FR55-59 (Rate limiting and progress)
- NFR1, NFR5 (Timeouts)

---

### 1.2 Create Project Detection Task

**File:** `_bmad/core/tasks/detect-project.yaml`

```yaml
name: Detect Project Type
description: Detect greenfield/brownfield and suggest tier
version: "1.0"

inputs:
  project_root:
    type: path
    default: "."

outputs:
  field_type:
    type: enum
    values: [greenfield, brownfield]
  suggested_tier:
    type: integer
    range: [0, 4]
  confidence:
    type: float
    range: [0, 100]
  detection_details:
    type: object

detection_rules:
  brownfield_indicators:
    - check: directory_exists
      paths: [src/, lib/, app/]
      weight: 30
    - check: file_exists
      patterns: [package.json, pyproject.toml, Cargo.toml, go.mod]
      weight: 25
    - check: source_file_count
      threshold: 10
      weight: 45

  # If total weight >= 50, classify as brownfield
  brownfield_threshold: 50

tier_suggestion:
  # Analyze user request for keywords
  keyword_matching:
    strategy: majority_vote
    min_confidence: 50

  # Consider codebase size
  codebase_analysis:
    small: [0, 1]      # < 1000 lines
    medium: [2]        # 1000-10000 lines
    large: [3, 4]      # > 10000 lines

execution:
  - step: scan_directories
    description: Check for source directories
  - step: scan_files
    description: Check for package files
  - step: count_source_files
    description: Count source files by extension
  - step: analyze_keywords
    description: Match user request against tier keywords
  - step: compute_suggestion
    description: Calculate tier suggestion with confidence
```

**Covers:**
- FR4 (Project type detection)
- FR5 (Tier suggestion)

---

### 1.3 Create Pre-flight Validation Task

**File:** `_bmad/core/tasks/preflight-validation.yaml`

```yaml
name: Pre-flight Validation
description: Validate configuration before workflow start
version: "1.0"

checks:
  config_syntax:
    description: Validate YAML syntax
    severity: blocking

  tier_valid:
    description: Ensure tier is 0-4
    severity: blocking

  thresholds_sane:
    description: Check threshold ranges
    severity: blocking
    rules:
      - field: automation.confidence.high_threshold
        range: [0, 100]
      - field: automation.menu_detection.confidence_threshold
        range: [0, 100]

  dependencies_met:
    description: Check required files exist
    severity: blocking
    per_workflow:
      create-architecture:
        requires: [prd.md]
      create-epics-and-stories:
        requires: [prd.md, architecture.md]
      dev-story:
        requires: [sprint-status.yaml, story_file]

  memory_accessible:
    description: Check Forgetful MCP connection
    severity: warning
    timeout: 5
    retry: 3
    on_failure: continue_degraded

output_format:
  success: |
    Pre-flight check...
      [OK] Configuration syntax valid
      [OK] Tier {tier} configured
      [OK] Thresholds within valid ranges
      [OK] Required documents found
    Ready to proceed.

  warning: |
    Pre-flight check...
      [OK] Configuration syntax valid
      [WARN] {warning_message}
    Ready to proceed with warnings. [Continue] [Fix warnings first]

  failure: |
    Pre-flight check FAILED:
      [FAIL] {failure_message}
    Please fix before continuing.
```

**Covers:**
- FR14 (Pre-flight validation)
- NFR9-10 (Graceful degradation)

---

### 1.4 Create Validation Type Detection Task

**File:** `_bmad/core/tasks/detect-validation-type.yaml`

```yaml
name: Detect Validation Type
description: Identify workflow-specific success criteria
version: "1.0"

detection_patterns:
  verdict_based:
    description: Pass/Fail or Approved/Rejected patterns
    patterns:
      - regex: "(READY|NEEDS WORK|NOT READY)"
        workflow: check-implementation-readiness
      - regex: "(PASS|CONCERNS|FAIL|WAIVED)"
        workflow: testarch-trace
      - regex: "(Approve|Changes Requested|Blocked)"
        workflow: code-review
    confidence: 90

  error_based:
    description: Zero errors success criteria
    patterns:
      - regex: "(0 errors|no issues|all checks passed)"
      - regex: "(blocking_errors:\\s*0)"
    confidence: 85

  checklist_based:
    description: Checkbox completion
    patterns:
      - regex: "^\\s*-\\s*\\[[ x]\\]"
        count_method: completion_percentage
    confidence: 80

  custom:
    description: User-defined in frontmatter
    source: workflow_frontmatter
    fields:
      - validation.type
      - validation.success_pattern
      - validation.failure_pattern
    priority: highest  # Custom overrides built-in

output:
  validation_type: string
  patterns: array
  confidence: float
  success_criteria: object
```

**Covers:**
- FR13 (Validation Type Detector)
- FR40 (Custom validation patterns)

---

## Phase 2: Menu Automation & Agent Handlers

### 2.1 Add Menu Handlers to Dev Agent

**File:** `_bmad/bmm/agents/dev.md`

**Add after existing persona section:**
```xml
<menu-handlers>
  <!-- Standard proceed menu [A][P][C] -->
  <handler menu="proceed-options" patterns="[A].*[P].*[C]|Continue\?">
    <auto-select condition="confidence >= config.automation.confidence.high_threshold AND tier <= 2">
      <choice>C</choice>
      <log level="info">Auto-selected [C] Continue (confidence: {confidence}%, tier: {tier})</log>
    </auto-select>
    <escalate condition="confidence < config.automation.confidence.medium_threshold">
      <to>user</to>
      <format>full_audit</format>
    </escalate>
    <default>
      <format>summary</format>
      <present-options>true</present-options>
    </default>
  </handler>

  <!-- Yes/Validate/No iteration menu [Y][V][N] -->
  <handler menu="iteration-options" patterns="[Y].*[V].*[N]|proceed with">
    <auto-select condition="validation_passed AND confidence >= 80">
      <choice>Y</choice>
      <log level="info">Auto-selected [Y] Yes - validation passed</log>
    </auto-select>
    <auto-select condition="NOT validation_passed AND attempts < config.automation.recovery.max_validation_iterations">
      <choice>V</choice>
      <log level="info">Auto-selected [V] Validate - attempting fix #{attempts}</log>
    </auto-select>
    <escalate condition="attempts >= config.automation.recovery.max_validation_iterations">
      <to>user</to>
      <reason>Max validation iterations reached</reason>
    </escalate>
  </handler>

  <!-- Party mode trigger [P] -->
  <handler menu="party-trigger" patterns="[P].*Party|call party mode">
    <auto-select condition="stall_detected AND attempts >= 2">
      <choice>P</choice>
      <log level="info">Auto-triggering Party Mode - stall detected</log>
    </auto-select>
    <auto-select condition="confidence < 60 AND tier >= 2">
      <choice>P</choice>
      <log level="info">Auto-triggering Party Mode - low confidence at tier {tier}</log>
    </auto-select>
  </handler>

  <!-- Code review outcomes -->
  <handler menu="review-outcome" patterns="Approve|Changes Requested|Blocked">
    <on-outcome value="Approve">
      <action>mark_complete</action>
      <route-to>next_story</route-to>
    </on-outcome>
    <on-outcome value="Changes Requested">
      <action>apply_fixes</action>
      <route-to>re_review</route-to>
      <max-iterations>3</max-iterations>
    </on-outcome>
    <on-outcome value="Blocked">
      <action>escalate</action>
      <route-to>user</route-to>
    </on-outcome>
  </handler>
</menu-handlers>

<confidence-calculator>
  <signals>
    <signal name="validation_verdict" weight="35">
      <source>last_validation_result</source>
      <mapping>
        <value result="READY" score="35"/>
        <value result="PASS" score="35"/>
        <value result="NEEDS WORK" score="20"/>
        <value result="CONCERNS" score="15"/>
        <value result="NOT READY" score="0"/>
        <value result="FAIL" score="0"/>
      </mapping>
    </signal>
    <signal name="memory_match" weight="25">
      <source>forgetful_query_results</source>
      <mapping>
        <condition matches=">= 3" score="25"/>
        <condition matches="1-2" score="15"/>
        <condition matches="0" score="0"/>
      </mapping>
    </signal>
    <signal name="reviewer_agreement" weight="25">
      <source>subagent_results</source>
      <mapping>
        <condition agreement="unanimous" score="25"/>
        <condition agreement="majority" score="15"/>
        <condition agreement="split" score="5"/>
      </mapping>
    </signal>
    <signal name="party_mode_outcome" weight="15">
      <source>party_mode_synthesis</source>
      <mapping>
        <condition consensus="true" score="15"/>
        <condition consensus="partial" score="8"/>
        <condition consensus="false" score="0"/>
      </mapping>
    </signal>
  </signals>
  <fallbacks>
    <no-signals>25</no-signals>
    <single-source-cap>60</single-source-cap>
    <calculation-error>30</calculation-error>
  </fallbacks>
</confidence-calculator>

<stall-detection>
  <algorithm>sha256</algorithm>
  <compare>consecutive_validation_outputs</compare>
  <threshold>2</threshold><!-- Same hash N times = stall -->
  <on-stall>
    <check>party_mode_already_tried</check>
    <if-not-tried>trigger_party_mode</if-not-tried>
    <if-tried>escalate_to_user</if-tried>
  </on-stall>
</stall-detection>
```

**Covers:**
- FR7-FR12 (Menu detection and selection)
- FR16 (Recovery without intervention)
- FR19a-j (Confidence calculation, stall detection)
- FR42-44b (Code review integration)

---

### 2.2 Add Menu Handlers to Architect Agent

**File:** `_bmad/bmm/agents/architect.md`

**Add similar handlers with architect-specific adjustments:**
```xml
<menu-handlers>
  <!-- Architecture decisions require more oversight -->
  <handler menu="proceed-options" patterns="[A].*[P].*[C]">
    <auto-select condition="confidence >= 90 AND tier <= 1">
      <choice>C</choice>
    </auto-select>
    <!-- Architect decisions are more consequential - lower auto-threshold -->
    <checkpoint condition="tier >= 2" format="summary">
      <reason>Architectural decision - confirming direction</reason>
    </checkpoint>
  </handler>

  <!-- ADR creation should always checkpoint -->
  <handler menu="adr-creation" patterns="Create ADR|Record decision">
    <checkpoint always="true" format="summary">
      <include>decision_rationale</include>
      <include>alternatives_considered</include>
    </checkpoint>
  </handler>
</menu-handlers>
```

---

### 2.3 Add Menu Handlers to PM Agent

**File:** `_bmad/bmm/agents/pm.md`

```xml
<menu-handlers>
  <!-- Story creation can be more automated -->
  <handler menu="proceed-options" patterns="[A].*[P].*[C]">
    <auto-select condition="confidence >= 80 AND tier <= 2">
      <choice>C</choice>
    </auto-select>
  </handler>

  <!-- Sprint planning checkpoints -->
  <handler menu="sprint-decisions" patterns="Add to sprint|Prioritize">
    <checkpoint condition="tier >= 3" format="summary"/>
    <auto-select condition="tier <= 2">
      <choice>C</choice>
    </auto-select>
  </handler>
</menu-handlers>
```

---

### 2.4 Create Human Checkpoint Presentation Task

**File:** `_bmad/core/tasks/present-checkpoint.yaml`

```yaml
name: Present Human Checkpoint
description: Format checkpoint based on confidence level
version: "1.0"

formats:
  minimal:  # >= 80% confidence
    trigger: "confidence >= config.automation.confidence.high_threshold"
    template: |
      **Decision Point:** {decision_summary}

      Recommendation: {recommended_action}

      [Approve] [Modify] [Reject]
    include:
      - decision_summary
      - recommended_action
    exclude:
      - full_rationale
      - alternatives
      - audit_trail

  summary:  # 50-79% confidence
    trigger: "confidence >= config.automation.confidence.medium_threshold"
    template: |
      **Decision Point:** {decision_summary}

      **Rationale:** {rationale}

      **Open Concerns:** {concerns}

      [Approve] [Modify] [Reject] [More Detail]
    include:
      - decision_summary
      - rationale
      - concerns
      - recommended_action

  full_audit:  # < 50% confidence
    trigger: "confidence < config.automation.confidence.medium_threshold"
    template: |
      **Decision Point:** {decision_summary}

      **Attempts Made:** {attempt_count}
      **Issues Resolved:** {resolved_issues}
      **Remaining Issues:** {remaining_issues}

      **Agent Perspectives:**
      {agent_perspectives}

      **Synthesis:**
      {synthesis_outcome}

      **Full Rationale:**
      {full_rationale}

      [Approve] [Modify] [Reject] [Party Mode] [Abort]
    include:
      - all_available_context
```

**Covers:**
- FR12b (Checkpoint formats)

---

## Phase 3: State Management & Recovery

### 3.1 Enhance Sprint Status Schema

**File:** `_bmad/_config/sprint-status-schema.yaml`

**Add automation state section:**
```yaml
# Automation state tracking (added to existing schema)
automation_state:
  type: object
  properties:
    enabled:
      type: boolean
      default: true
    current_tier:
      type: integer
      enum: [0, 1, 2, 3, 4]
    session_id:
      type: string
      format: uuid

    # Current workflow tracking
    current_workflow:
      type: string
    current_step:
      type: string
    step_started_at:
      type: string
      format: datetime

    # Checkpoint tracking
    checkpoints:
      type: array
      items:
        type: object
        properties:
          id:
            type: string
          step_id:
            type: string
          timestamp:
            type: string
            format: datetime
          state_snapshot:
            type: object
          can_rollback:
            type: boolean

    # Recovery state
    recovery:
      type: object
      properties:
        validation_attempts:
          type: integer
          default: 0
        same_error_retries:
          type: integer
          default: 0
        last_error_hash:
          type: string
        party_mode_tried_hashes:
          type: array
          items:
            type: string
        resume_attempt_count:
          type: integer
          default: 0

    # Task queue
    pending_tasks:
      type: array
      maxItems: 100
      items:
        type: object
        properties:
          id:
            type: string
          workflow:
            type: string
          priority:
            type: integer
          queued_at:
            type: string
            format: datetime

    # Metrics
    metrics:
      type: object
      properties:
        auto_continues:
          type: integer
        user_interventions:
          type: integer
        party_mode_triggers:
          type: integer
        successful_recoveries:
          type: integer
```

**Covers:**
- FR26-30 (State management)
- FR60-62 (Checkpoints and rollback)
- NFR7, NFR8, NFR11 (Persistence, terminal states, idempotency)

---

### 3.2 Create State Persistence Task

**File:** `_bmad/core/tasks/persist-state.yaml`

```yaml
name: Persist Automation State
description: Save state before step transitions
version: "1.0"

triggers:
  - event: before_step_transition
  - event: before_validation_fix
  - event: on_checkpoint
  - event: on_user_request

persistence:
  target: sprint-status.yaml
  section: automation_state

  # Atomic write pattern
  write_strategy:
    method: write_temp_then_rename
    temp_suffix: .tmp
    backup_suffix: .bak

  # Idempotency check
  idempotency:
    enabled: true
    check_fields: [step_id, input_hash]
    on_duplicate: skip_with_log

checkpoint_creation:
  fields_to_capture:
    - step_id
    - timestamp
    - workflow_context
    - validation_state
    - confidence_scores

  rollback_eligibility:
    - condition: "step_type != 'final_approval'"
    - condition: "no_external_side_effects"
```

**Covers:**
- FR26 (State persistence)
- FR27 (Resume capability)
- FR60-62 (Checkpoint creation)
- NFR11 (Idempotency)

---

### 3.3 Create Sprint Status Watcher Configuration

**File:** `_bmad/core/tasks/sprint-watcher.yaml`

```yaml
name: Sprint Status Watcher
description: Monitor sprint-status.yaml for changes
version: "1.0"

watch:
  file: sprint-status.yaml
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
    - check: has_next_story
    - if_true:
        route_to: create-story
        auto_start: "tier <= 2"
    - if_false:
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
```

**Covers:**
- FR28 (Sprint Status Watcher)
- NFR8 (Terminal states)

---

## Phase 4: Memory Integration

### 4.1 Create Context Pre-Load Task

**File:** `_bmad/core/tasks/context-preload.yaml`

```yaml
name: Context Pre-Load
description: Query Forgetful for relevant context before workflow start
version: "1.0"

execution:
  when: workflow_start
  timeout_seconds: 10

queries:
  - name: workflow_patterns
    query: "{workflow_name} patterns decisions"
    project_ids: [current_project]
    k: 5
    store_in: workflow_context.memory_matches

  - name: recent_learnings
    query: "lesson learned {domain}"
    project_ids: [current_project]
    k: 3
    filter: "created_at > 7 days ago"
    store_in: workflow_context.recent_learnings

  - name: fix_patterns
    query: "{error_type} fix solution"
    project_ids: [current_project]
    k: 5
    only_if: has_validation_errors
    store_in: workflow_context.fix_patterns

graceful_degradation:
  on_timeout:
    action: continue_without_memory
    log_level: warning

  on_connection_error:
    retry_count: 3
    retry_delay_ms: 100
    fallback: continue_without_memory

  on_permanent_unavailable:
    action: disable_memory_features
    notify_user: true
```

**Covers:**
- FR31, FR35 (Context Pre-Loader)
- FR34 (Graceful degradation)
- NFR9-10 (Graceful degradation details)

---

### 4.2 Create Memory Bridge Task

**File:** `_bmad/core/tasks/memory-bridge.yaml`

```yaml
name: Memory Bridge
description: Write workflow decisions and outcomes to Forgetful
version: "1.0"

write_triggers:
  - event: workflow_decision_made
    importance: 8

  - event: validation_fix_succeeded
    importance: 7
    template:
      title: "Fix Pattern: {error_type}"
      content: "{fix_description}"
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
```

**Covers:**
- FR32 (Memory Bridge writes)
- FR33 (Post-Workflow Curator)
- NFR10 (Queue details)
- NFR12 (MCP Compatibility)

---

### 4.3 Create Post-Workflow Learning Task

**File:** `_bmad/core/tasks/extract-learnings.yaml`

```yaml
name: Post-Workflow Learning Extraction
description: Extract and save key learnings after workflow completion
version: "1.0"

extraction_rules:
  architectural_decisions:
    importance: [9, 10]
    indicators:
      - "decided to"
      - "chose X over Y"
      - "ADR"
      - "architecture decision"
    memory_template:
      title: "Architecture: {summary}"
      tags: [architecture, decision]

  implementation_patterns:
    importance: [7, 8]
    indicators:
      - "pattern"
      - "approach"
      - "technique"
      - "method"
    memory_template:
      title: "Pattern: {summary}"
      tags: [pattern, implementation]

  problem_solutions:
    importance: [7, 8]
    indicators:
      - "fixed by"
      - "resolved"
      - "solution"
      - "workaround"
    memory_template:
      title: "Solution: {problem_summary}"
      tags: [fix, solution]

  milestones:
    importance: [6, 7]
    indicators:
      - "complete"
      - "finished"
      - "done"
      - "shipped"
    memory_template:
      title: "Milestone: {summary}"
      tags: [milestone, progress]

atomic_memory_limits:
  max_content_length: 2000
  max_keywords: 10
  max_tags: 10
```

**Covers:**
- FR33 (Post-Workflow Curator)

---

## Phase 5: Multi-Agent & Party Mode

### 5.1 Enhance Party Mode Workflow

**File:** `_bmad/core/workflows/party-mode.yaml` (modifications)

**Add automation section:**
```yaml
# Add to existing party-mode workflow config
automation:
  auto_triggers:
    - condition: stall_detected
      requirements:
        - validation_attempts >= 2
        - NOT party_mode_hash_tried
      action: initiate_party_mode
      topic_generation: synthesize_from_stall_context

    - condition: low_confidence
      requirements:
        - confidence < 60
        - tier >= 2
      action: initiate_party_mode
      topic_generation: decision_requiring_input

    - condition: mandatory_pre_final
      requirements:
        - tier >= 3
        - step_type == final_review
      action: initiate_party_mode
      agents: [architect, tea, domain_expert]

    - condition: bmb_threshold_violation
      requirements:
        - module == bmb
        - blocking_errors > 3 OR major_issues > 5
      action: initiate_party_mode

  agent_selection:
    method: topic_analysis
    min_agents: 2
    max_agents: 3

  exit_detection:
    keywords:
      - "*exit"      # Literal asterisk
      - "goodbye"
      - "end party"
      - "quit"
    matching: literal_string
    grace_period_ms: 500

  convergence_detection:
    enabled: true
    agreement_threshold: 0.8
    max_rounds: 5
    on_convergence: synthesize_and_exit

  synthesis:
    method: automated
    template: |
      **Party Mode Synthesis**

      **Agreements:** {agreements}
      **Disagreements:** {disagreements}
      **Recommended Action:** {recommendation}
      **Confidence:** {synthesis_confidence}%

    escalate_on_critical_disagreement: true
```

**Covers:**
- FR20-21e (Party Mode Driver)
- FR25a (Brainstorming handling)

---

### 5.2 Create Subagent Dispatcher Configuration

**File:** `_bmad/core/tasks/dispatch-subagent.yaml`

```yaml
name: Subagent Dispatcher
description: Manage agent pool and task routing
version: "1.0"

pool_management:
  max_concurrent: 6  # For BMB parallel validation

  agent_types:
    validator:
      model_default: haiku
      timeout: 60

    spec_reviewer:
      model_default: sonnet
      timeout: 120

    quality_reviewer:
      model_default: sonnet
      timeout: 120

    adversarial_reviewer:
      model_default: sonnet
      timeout: 120
      instructions: "Find 3-10 specific issues"

    domain_expert:
      model_default: opus
      timeout: 180

model_selection:
  dynamic: true
  rules:
    - task_type: simple_validation
      model: haiku
    - task_type: code_review
      model: sonnet
    - task_type: architectural_review
      model: opus
    - tier_based:
        tier_0_1: haiku
        tier_2: sonnet
        tier_3_4: opus

context_forking:
  enabled: true
  use_case: parallel_reviewers
  strategy: information_asymmetry
  # Each reviewer gets different context slice for diverse perspectives

tracking:
  store_agent_ids: true  # For potential resumption
  store_in: sprint-status.yaml
  section: automation_state.active_agents

patterns:
  fire_and_summarize:
    description: Single agent, summarize result
    wait: true

  parallel_and_aggregate:
    description: Multiple agents, aggregate results
    wait_all: true
    aggregation: merge_with_dedup

  background_and_notify:
    description: Fire and forget, notify on complete
    wait: false
    callback: on_complete_handler

  context_fork_isolation:
    description: Parallel with isolated context
    fork_context: true
    merge_strategy: synthesis
```

**Covers:**
- FR22-23c (Subagent Dispatcher)
- FR25b (Simulated Party Mode)

---

### 5.3 Create Code Review Integration

**File:** `_bmad/bmm/workflows/code-review-automation.yaml`

```yaml
name: Code Review Automation
description: Adversarial code review with 3-10 findings requirement
version: "1.0"

invocation:
  auto_after: story_implementation_complete

review_requirements:
  type: adversarial
  min_findings: 3
  max_findings: 10
  checklist_items: 19

  outcomes:
    approve:
      condition: "all_findings_addressed"
      action: mark_story_complete

    changes_requested:
      condition: "has_actionable_findings"
      action: apply_fixes_and_re_review
      max_iterations: 3

    blocked:
      condition: "critical_issue_found OR max_iterations_exceeded"
      action: escalate_to_user

iteration_tracking:
  store_in: sprint-status.yaml
  fields:
    - review_round
    - findings_by_round
    - fixes_applied

loop_back:
  max_iterations: 10
  same_error_max: 3
  oscillation_detection:
    enabled: true
    pattern_length: 3
    on_oscillation: escalate
```

**Covers:**
- FR42-44b (Code Review)
- FR24-25 (Loop-Back Handler)

---

### 5.4 BMB Parallel Validation Configuration

**File:** `_bmad/bmb/workflows/parallel-validation.yaml`

```yaml
name: BMB Parallel Validation
description: Run 6 validation checks concurrently
version: "1.0"

validators:
  - id: 08a
    name: plan-traceability
    parallel: true

  - id: 08b
    name: metadata-validation
    parallel: true

  - id: 08c
    name: persona-validation
    parallel: true

  - id: 08d
    name: menu-validation
    parallel: true

  - id: 08e
    name: structure-validation
    parallel: true

  - id: 08f
    name: sidecar-validation
    parallel: true

synchronization:
  barrier:
    wait_for: all
    timeout_seconds: 120

  aggregation:
    mutex_timeout_seconds: 5
    retry_on_mutex_failure: true

partial_failure_handling:
  "6/0":  # All succeed
    action: proceed

  "4-5/1-2":  # Mostly succeed
    action: retry_failed_sequentially

  "2-3/3-4":  # Mixed
    action: retry_all
    escalate_if_still_failing: true

  "1/5":  # One success
    action: use_success_as_context
    retry: sequential

  "0/6":  # All fail
    action: abort_parallel
    fallback: full_sequential
```

**Covers:**
- FR45-47c (Parallel BMB Validation)

---

## Phase 6: User Experience & Learning

### 6.1 Create Feedback Learning Task

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

    user_override:
      - pattern: user_changes_tier
        inference: tier_suggestion_incorrect

    repeated_escalation:
      - pattern: user_rejects_auto_continue > 3
        inference: confidence_threshold_too_low

  learning:
    adjust_thresholds: true
    store_pattern: true
```

**Covers:**
- FR63-65 (Feedback learning)

---

### 6.2 Progress Display Configuration

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

  summary:
    batch_updates: true
    batch_size: 5
    show_milestones: true

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
    Pausing for review. {consecutive_count} operations completed.
    [Continue] [Review Details] [Abort]
```

**Covers:**
- FR55-59 (Rate limiting and progress)

---

### 6.3 Hook Discovery Configuration

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

**Covers:**
- FR51-54 (Hooks)

---

## Implementation Order

### Recommended Sequence

1. **Phase 1.1** - Create config.yaml automation section (foundation for everything)
2. **Phase 1.2-1.4** - Create detection tasks (project, preflight, validation type)
3. **Phase 2.1-2.3** - Add menu handlers to agents (dev, architect, pm)
4. **Phase 2.4** - Create checkpoint presentation task
5. **Phase 3.1-3.3** - State management (sprint-status schema, persistence, watcher)
6. **Phase 4.1-4.3** - Memory integration tasks
7. **Phase 5.1-5.4** - Multi-agent configuration
8. **Phase 6.1-6.3** - User experience tasks

### Files to Create/Modify

| Phase | File | Action |
|-------|------|--------|
| 1.1 | `_bmad/_config/config.yaml` | Modify (add section) |
| 1.2 | `_bmad/core/tasks/detect-project.yaml` | Create |
| 1.3 | `_bmad/core/tasks/preflight-validation.yaml` | Create |
| 1.4 | `_bmad/core/tasks/detect-validation-type.yaml` | Create |
| 2.1 | `_bmad/bmm/agents/dev.md` | Modify (add handlers) |
| 2.2 | `_bmad/bmm/agents/architect.md` | Modify (add handlers) |
| 2.3 | `_bmad/bmm/agents/pm.md` | Modify (add handlers) |
| 2.4 | `_bmad/core/tasks/present-checkpoint.yaml` | Create |
| 3.1 | `_bmad/_config/sprint-status-schema.yaml` | Create/Modify |
| 3.2 | `_bmad/core/tasks/persist-state.yaml` | Create |
| 3.3 | `_bmad/core/tasks/sprint-watcher.yaml` | Create |
| 4.1 | `_bmad/core/tasks/context-preload.yaml` | Create |
| 4.2 | `_bmad/core/tasks/memory-bridge.yaml` | Create |
| 4.3 | `_bmad/core/tasks/extract-learnings.yaml` | Create |
| 5.1 | `_bmad/core/workflows/party-mode.yaml` | Modify |
| 5.2 | `_bmad/core/tasks/dispatch-subagent.yaml` | Create |
| 5.3 | `_bmad/bmm/workflows/code-review-automation.yaml` | Create |
| 5.4 | `_bmad/bmb/workflows/parallel-validation.yaml` | Create |
| 6.1 | `_bmad/core/tasks/feedback-learning.yaml` | Create |
| 6.2 | `_bmad/core/tasks/progress-display.yaml` | Create |
| 6.3 | `_bmad/core/tasks/hook-discovery.yaml` | Create |

**Total: 20 files (8 modify, 12 create)**

---

## Validation Approach

Since this is native BMAD modification, validation is:

1. **Syntax validation** - YAML/XML parsers
2. **Schema validation** - Against existing BMAD schemas
3. **Integration testing** - Run actual workflows with automation
4. **User acceptance** - Does it behave as expected?

No Python unit tests needed - the "tests" are the workflows themselves working correctly.

---

## Reference Materials

- **Original Design:** `plans/2026-01-08-bmad-automation-design.md`
- **Original Epics:** `_bmad-output/planning-artifacts/epics.md`
- **Archived Python Spec:** `docs/reference/automation-spec-archive/`
- **Pivot Decision:** `docs/plans/2026-01-13-bmad-automation-pivot.md`
