---
stepsCompleted: [1, 2, 3, 4]
workflowStatus: complete
validationRounds: 4
finalValidationDate: 2026-01-12
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - docs/plans/2026-01-08-bmad-automation-design.md
---

# BMAD Automation - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for BMAD Automation, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

#### Workflow Automation (6 FRs)
- FR1: Automation Controller can detect skill invocations matching `/bmad:*` patterns and initiate workflow execution
- FR2: Automation Controller can execute workflows autonomously without user prompts at each step
- FR3: Automation Controller can transition between workflow steps based on verdict-based success criteria
- FR4: Workflow Entry Wrapper can detect project type (greenfield/brownfield) by checking for existing source directories (src/, lib/, app/), package files (package.json, pyproject.toml), and substantial code (>10 source files)
- FR5: Tier Suggester can recommend project level (0-4) based on user description and codebase analysis
- FR6: Automation Controller can respect task-level oversight requirements defined in workflow configuration

#### Menu Participation (8 FRs)
- FR7: Menu Participation Engine can detect menus using confidence scoring (>= 70 points threshold) with structural markers, position validation, and false positive guards (reject patterns inside code blocks, blockquotes, or example content)
- FR8: Menu Participation Engine can automatically select appropriate menu options based on confidence thresholds
- FR9: Menu Participation Engine can apply BMB-specific thresholds: trigger Party Mode when `blocking_errors > 3` OR `major_issues > 5`; trigger Advanced Elicitation when `compliance_score < 70`
- FR10: Menu Participation Engine can escalate to user when confidence is below 80% threshold
- FR11: Menu Participation Engine can handle nested menu selections within Party Mode or Advanced Elicitation
- FR12: Menu Participation Engine can track menu selection history for recovery purposes
- FR12a: Menu Participation Engine can implement batch-continue logic with tier-based batch sizes (Level 0-1: auto-all, Level 2: up to 5, Level 3: up to 3, Level 4: 1-2)
- FR12b: Automation Controller can present human checkpoints in three formats: Minimal (>=80% confidence), Summary (50-80%), Full Audit Trail (<50%)

#### Validation & Recovery (17 FRs)
- FR13: Validation Type Detector can identify workflow-specific success criteria (verdict-based, error-based, or checklist-based)
- FR14: Pre-flight Validation Subagent can verify required configuration before workflow start
- FR15: Cross-Reference Validator can check document alignment across workflow outputs
- FR16: Automation Controller can recover from validation failures without user intervention
- FR17: Automation Controller can enforce timeout hierarchy (1800s workflow, 300s nested, 60s agent)
- FR18: Automation Controller can reach terminal states for all error paths without infinite loops
- FR19: Confidence Calculator can compute confidence scores from validator outputs
- FR19a: Automation Controller can detect validation stalls using SHA-256 hash-based issue set comparison
- FR19b: Automation Controller triggers Party Mode escalation when stall detected AND attempts >= 2
- FR19c: Automation Controller tracks failed Party Mode hashes to prevent stall->party->fail loops
- FR19d: Automation Controller applies memory-first fix strategy with multi-approach fallback
- FR19e: Confidence Calculator uses 4 signal sources: Validation Verdict (0-35pts), Memory Match (0-25pts), Reviewer Agreement (0-25pts), Party Mode Outcome (0-15pts) (optional 5th signal: model selection 0-10pts)
- FR19f: Confidence Calculator applies tier adjustment and returns score 0-100 with threshold classification
- FR19g: Confidence Calculator defaults to 25% when no signals available
- FR19h: Confidence Calculator caps single-source confidence at 60% maximum
- FR19i: Confidence Calculator handles conflicting signals by weighting higher-priority sources
- FR19j: Confidence Calculator falls back to 30% on calculation failures

#### Multi-Agent Coordination (16 FRs)
- FR20: Party Mode Driver can provide programmatic inputs for each conversation round
- FR21: Party Mode Driver can track round progress and detect completion criteria
- FR21a: Party Mode Driver auto-triggers on BMB threshold violations or stall detection
- FR21b: Party Mode Driver auto-triggers on confidence < 60% at Tier 2+
- FR21c: Party Mode Driver provides mandatory pre-final review at Tier 3-4
- FR21d: Party Mode Driver uses exact exit keywords ("*exit", "goodbye", "end party", "quit") for session termination (LITERAL string matching, asterisk in *exit is literal)
- FR21e: Party Mode Driver handles in-flight response cleanup with 500ms grace period
- FR22: Subagent Dispatcher can manage agent pool allocation and lifecycle
- FR23: Subagent Dispatcher can route tasks to appropriate specialized agents
- FR23a: Subagent Dispatcher supports dynamic model selection (Haiku/Sonnet/Opus) based on task type and tier
- FR23b: Subagent Dispatcher uses context forking for parallel reviewers (information asymmetry)
- FR23c: Subagent Dispatcher tracks agent_id for potential resumption via Claude Code 2.1
- FR24: Loop-Back Handler can track iteration count for Edit-Module workflows
- FR25: Loop-Back Handler can enforce maximum iteration limits (MAX_VALIDATION_ITERATIONS=10, MAX_SAME_ERROR_RETRIES=3, oscillation detection)
- FR25a: Automation Controller can handle brainstorming workflows via pre-seeding (Tier 3-4) or simulated ideation (Tier 0-2)
- FR25b: Subagent Dispatcher can execute Simulated Party Mode using 3-5 subagent personas for Tier 0-2 when full party mode not warranted

#### State Management (5 FRs)
- FR26: Automation Controller can persist workflow state across conversation boundaries
- FR27: Automation Controller can resume workflows from last completed step after interruption
- FR28: Sprint Status Watcher can monitor workflow status files with 500ms debounce, 30s deduplication window, dual compare-and-swap for race prevention, and status cycling detection
- FR29: Automation Controller can manage queue of pending workflow tasks (capped at 100 entries)
- FR30: Automation Controller can track completion status of all workflow steps

#### Memory Integration (5 FRs)
- FR31: Context Pre-Loader can query Forgetful memory for relevant context before workflow start
- FR32: Memory Bridge can write workflow decisions and outcomes to Forgetful memory
- FR33: Post-Workflow Curator can extract key learnings and create atomic memories: architectural decisions (importance 9-10), implementation patterns (7-8), problem-solution pairs (7-8), milestone completions (6-7)
- FR34: Memory Bridge can gracefully degrade when Forgetful MCP is unavailable
- FR35: Context Pre-Loader can pre-populate agent context with relevant memories

#### Configuration & Adaptation (6 FRs)
- FR36: Automation Controller can read configuration from workflow YAML/MD frontmatter
- FR37: Automation Controller can apply module-specific settings (Core, BMM, BMB)
- FR38: Confidence Calculator can use configurable thresholds per workflow type
- FR39: Automation Controller can adapt behavior based on project classification (type, domain, complexity)
- FR40: Validation Type Detector can recognize custom workflow validation patterns
- FR41: Automation Controller can support both YAML and Markdown workflow formats

#### Code Review Integration (5 FRs)
- FR42: Automation Controller can invoke code review workflow after story implementation
- FR43: Automation Controller can parse code review verdicts and determine next action
- FR44: Automation Controller can track review iteration count and outcomes
- FR44a: Code Review is ADVERSARIAL - must find 3-10 specific issues per story using 19-item checklist
- FR44b: Code Review outcomes are Approve (issues addressed), Changes Requested (apply fixes, re-review), or Blocked (escalate)

#### BMB Module Support (6 FRs)
- FR45: Parallel BMB Validation can run up to 6 validation checks concurrently
- FR46: Automation Controller can orchestrate agent creation workflows with BMB-specific confidence thresholds
- FR47: Automation Controller can validate generated workflow/agent artifacts against BMAD standards
- FR47a: Parallel BMB Validation implements synchronization barrier waiting for all 6 subagents (08a-08f)
- FR47b: Parallel BMB Validation uses thread-safe aggregation with mutex (5s timeout, retry once)
- FR47c: Parallel BMB Validation applies partial failure handling: 6/0 success -> proceed; 4-5/1-2 -> retry failed sequentially; 2-3/3-4 -> retry all + escalate if still failing; 1/5 -> use single success as context for sequential retry; 0/6 -> abort parallel, fall back to full sequential

#### Tier Override & Configuration (3 FRs)
- FR48: Automation Controller supports tier override methods: natural language, explicit tier, specific settings, profile switch, inline modifier
- FR49: Automation Controller applies override priority: explicit tier > profile switch > specific settings > natural language hints
- FR50: Overrides persist for session but never bypass safety-critical behavior (final approval, stall detection)

#### Lifecycle & Hooks (4 FRs)
- FR51: Automation Controller discovers and executes hooks from step file frontmatter (PreToolUse, PostToolUse, Stop)
- FR52: Hooks have output size limits: 64KB stdout, 16KB stderr, 256KB total per step
- FR53: Hook failures are logged and continued unless marked `critical: true`
- FR54: SessionStart hooks support `once: true` for one-time initialization

#### Rate Limiting & Presentation (5 FRs)
- FR55: Menu Participation Engine can throttle menu presentations with minimum 2-second intervals between presentations
- FR56: Menu Participation Engine can force pause after 10 consecutive menus to prevent fatigue
- FR57: Automation Controller can batch silent progress into summaries (Verbose/Summary/Silent/Streaming modes)
- FR58: Automation Controller can display streaming progress for long operations (>30s) showing current step name and percentage
- FR59: Automation Controller can provide progress summary on user request showing completed/remaining steps

#### Rollback & Recovery (3 FRs)
- FR60: Automation Controller can create checkpoints at key workflow points (before step transitions, before validation fixes)
- FR61: Automation Controller can rollback to previous checkpoint on user request ("undo", "rollback to step N")
- FR62: Checkpoint data persisted to frontmatter includes: step_id, timestamp, state_snapshot, can_rollback flag

#### Feedback & Learning (3 FRs)
- FR63: Automation Controller can accept explicit feedback commands ("Don't do that again", "Good choice", "Remember this preference")
- FR64: Automation Controller can store positive/negative patterns in Forgetful memory for future reference
- FR65: Automation Controller can detect implicit feedback from user corrections and store learned preferences

### NonFunctional Requirements

#### Performance (5 NFRs)
- NFR1: Timeout Enforcement - Workflow timeouts (1800s), nested operation timeouts (300s), and agent timeouts (60s) must be enforced to prevent hangs
- NFR2: Response Expectations - Menu selections and step transitions should complete within 5 seconds under normal conditions
- NFR3: Context Efficiency - Automation should reduce token usage compared to manual orchestration through intelligent context management
- NFR4: Queue Processing - Task queue operations (add, remove, prioritize) must complete within 100ms
- NFR5: Extended Timeout Hierarchy - Party mode round (120s), background watcher poll (5s interval), exit grace period (500ms), synchronization wait (120s), human selection timeout (300s)

#### Reliability (6 NFRs)
- NFR6: Recovery Rate - 95% of recoverable errors should resolve without user intervention
- NFR7: State Persistence - Workflow state must survive conversation boundaries and be resumable
- NFR8: Terminal States - All error paths must reach terminal states (no infinite loops or hangs)
- NFR9: Graceful Degradation - System must continue operating when optional dependencies (Forgetful MCP) are unavailable
- NFR10: Graceful Degradation Details - When Forgetful unavailable: 3 retries at 100ms intervals, queue to local file (`_bmad-output/.memory-queue/`), max 100 queued entries with FIFO overflow, 5-minute cache TTL, PERMANENTLY_UNAVAILABLE after 4 hours
- NFR11: Idempotency - Repeated execution of the same workflow step should produce consistent results

#### Integration (4 NFRs)
- NFR12: MCP Compatibility - Must work with Forgetful MCP and Serena MCP when available
- NFR13: Skill System - Must integrate cleanly with Claude Code's existing skill invocation mechanism
- NFR14: BMAD Compatibility - Must work with existing BMAD V6 module structure without modifications to source workflows
- NFR15: File System - Must read/write workflow state and output files reliably to configured paths

### Additional Requirements

#### From Architecture Document

**No Starter Template Required:**
- This is brownfield development extending existing BMAD V6 framework
- Integration point: `_bmad/` folder structure already exists
- No greenfield scaffolding needed

**16-Component Architecture (Implementation Order by Dependency Tier):**

*Tier 1 (No Dependencies):*
- Validation Type Detector - Workflow-specific awareness for verdict-based success
- Pre-flight Validation Subagent - Config validation before workflow start
- Cross-Reference Validator - Document alignment checks

*Tier 2-3 (Core Engine):*
- Workflow Entry Wrapper - workflow-init integration (depends on Validation Type Detector)
- Menu Participation Engine - [A][P][C] handling with BMB thresholds
- Context Pre-Loader - Forgetful memory pre-population
- Automation Controller - Verdict-based loop logic (depends on Menu Participation Engine)
- Confidence Calculator - 80% threshold for autonomous decisions
- Tier Suggester - Smart tier suggestions (depends on Workflow Entry Wrapper)

*Tier 4 (Specialized Handlers):*
- Party Mode Driver - Programmatic per-round inputs (depends on Automation Controller)
- Loop-Back Handler - Edit-Module iteration tracking
- Subagent Dispatcher - Agent pool management
- Memory Bridge - Forgetful integration (depends on Context Pre-Loader)

*Tier 5 (Integration):*
- Parallel BMB Validation - 6x parallel validation (depends on Subagent Dispatcher)
- Sprint Status Watcher - Background file monitoring
- Post-Workflow Curator - Automated memory extraction (depends on Memory Bridge)

**State Machine Transitions:**
- States: IDLE -> INITIALIZING -> RUNNING -> VALIDATING -> WAITING_USER -> COMPLETING -> TERMINAL
- All transitions must be valid and reach terminal states
- Recovery paths for FAILED -> RECOVERING -> RUNNING

**Interface Contracts (from Design Specification):**
- Each component has defined input/output TypeScript-style interfaces
- All components must implement these contracts exactly
- Cross-component communication via defined interfaces only

**Memory Patterns:**
- Atomic memory principle: Each memory represents ONE concept
- Importance levels: architectural decisions (9-10), patterns (7-8), milestones (6-7)
- Memory queuing when Forgetful unavailable

**Hook System:**
- Discover hooks from step file frontmatter
- Execute PreToolUse, PostToolUse, Stop hooks
- Support `once: true` for one-time initialization

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1-FR6 | Epic 2a | Workflow Entry Wrapper, Tier Suggester, skill detection |
| FR7-FR12b | Epic 2b | Menu Participation Engine, batch-continue logic |
| FR13, FR14, FR15 | Epic 1 | Validation Type Detector, Pre-flight Validation, Cross-Reference |
| FR16-FR19j | Epic 2b | Automation Controller recovery, Confidence Calculator |
| FR20-FR25b | Epic 5 | Party Mode Driver, Subagent Dispatcher, Loop-Back Handler |
| FR26-FR30 | Epic 3 | State Management, Sprint Status Watcher |
| FR31 | Epic 2a | Context Pre-Loader query |
| FR35 | Epic 2a | Context Pre-Loader pre-population |
| FR32-FR34 | Epic 4 | Memory Bridge, Post-Workflow Curator |
| FR36-FR39, FR41 | Epic 2a | Configuration & Adaptation |
| FR40 | Epic 1 | Validation Type Detector custom patterns |
| FR42-FR44b | Epic 5 | Code Review Integration |
| FR45-FR47c | Epic 6 | Parallel BMB Validation |
| FR48-FR50 | Epic 7 | Tier Override (feature of Automation Controller) |
| FR51-FR54 | Epic 7 | Lifecycle & Hooks (feature of Automation Controller) |
| FR55-FR56 | Epic 7 | Rate Limiting (feature of Menu Participation Engine) |
| FR57-FR59 | Epic 7 | Progress Display (feature of Automation Controller) |
| FR60-FR62 | Epic 3 | Rollback & Recovery |
| FR63-FR65 | Epic 7 | Feedback Learning (stored via Memory Bridge) |

**Coverage:** 92/92 FRs mapped (100%)

### NFR Coverage Map

| NFR | Epic | Description |
|-----|------|-------------|
| NFR1 | Epic 5 | Timeout Enforcement (Party Mode, Subagent timeouts) |
| NFR2, NFR3, NFR4 | Epic 2b | Response, Context Efficiency, Queue Processing |
| NFR5 | Epic 5 | Extended Timeout Hierarchy |
| NFR6 | Epic 5 | Recovery Rate |
| NFR7, NFR8 | Epic 3 | State Persistence, Terminal States |
| NFR9, NFR10 | Epic 4 | Graceful Degradation (Memory Bridge) |
| NFR11 | Epic 3 | Idempotency |
| NFR12 | Epic 4 | MCP Compatibility |
| NFR13, NFR14 | Epic 2b | Skill System, BMAD Compatibility |
| NFR15 | Epic 3, Epic 7 | File System (state files in Epic 3, output files in Epic 7) |

**Coverage:** 15/15 NFRs mapped (100%)

---

## Epic List

### Epic 1: Foundation Validation
**Goal:** Developers can verify workflow prerequisites and understand validation requirements before starting any workflow.

**User Outcome:** Before starting a workflow, developers get clear feedback on what's ready, what's missing, and what validation rules apply.

**FRs covered:** FR13, FR14, FR15, FR40 (4 FRs)

**Components:** Validation Type Detector, Pre-flight Validation Subagent, Cross-Reference Validator

**Dependencies:** None (Tier 1)

**NFRs addressed:** None (Tier 1 validation is synchronous and has no recovery/timeout requirements)

**Acceptance Criteria:**
- Pre-flight validation catches 100% of missing required configuration before workflow start
- Validation Type Detector correctly identifies verdict-based, error-based, and checklist-based validation types
- Cross-Reference Validator detects document alignment issues (missing PRD requirements in architecture, unaddressed architecture decisions in stories, orphaned FRs) with zero false negatives
- Validation Type Detector correctly classifies custom workflow validation patterns defined in workflow configuration files - verified by pattern registration and subsequent detection test (FR40)

---

### Epic 2a: Workflow Entry & Detection
**Goal:** Developers can invoke BMAD workflows with intelligent project classification and context pre-loading.

**User Outcome:** Running `/bmad:bmm:workflows:workflow-init` automatically detects greenfield/brownfield, suggests appropriate tier, and pre-loads relevant context from memory.

**FRs covered:** FR1-FR6, FR31, FR35, FR36-FR39, FR41 (13 FRs)

**Components:** Workflow Entry Wrapper, Tier Suggester, Context Pre-Loader

**NFRs addressed:** None directly (configuration reading supports NFR15 implementation in Epic 7)

**Dependencies:** Epic 1 (validation awareness for config reading)

**Acceptance Criteria:**
- Skill invocations matching `/bmad:*` patterns are detected and initiate workflow execution
- Project type detection follows defined rules: greenfield when no src/lib/app directories AND no package files AND <10 source files; brownfield otherwise
- Tier suggestions match the tier indicated by more than 50% of detected complexity keywords (validated against project-specific test cases)
- Context Pre-Loader retrieves relevant memories before workflow start
- Context Pre-Loader pre-populates agent context with memories matching workflow keywords - verified by checking agent context contains at least 1 relevant memory when available (FR35)
- Both YAML and Markdown workflow formats supported

---

### Epic 2b: Menu & Automation Core
**Goal:** Workflows execute autonomously with intelligent menu handling and confidence-based decisions.

**User Outcome:** Running `/bmad:bmm:workflows:dev-story` completes without constant "Should I continue?" prompts. Menus are handled automatically based on confidence thresholds.

**FRs covered:** FR7-FR12b, FR16-FR19j (22 FRs)

**Components:** Menu Participation Engine, Automation Controller, Confidence Calculator

**NFRs addressed:** NFR2 (Response Expectations), NFR3 (Context Efficiency), NFR4 (Queue Processing), NFR6 (Recovery Rate - 95% target in AC), NFR13 (Skill System), NFR14 (BMAD Compatibility)

**Dependencies:** Epic 2a (entry points and context), Epic 1 (validation awareness)

**Acceptance Criteria:**
- Menu detection achieves >= 70 points confidence with zero false positives in code blocks/blockquotes
- Confidence Calculator produces scores 0-100 using 4+ signal sources. Note: When optional 5th signal (model selection 0-10pts) is active, scoring weights are proportionally adjusted to maintain 0-100 scale per FR19f
- Autonomous decisions made at >= 80% confidence threshold
- Automation Controller attempts automatic recovery before user escalation - given a recoverable validation failure (missing config, transient error), system retries with fix strategy before prompting user (FR16)
- Recovery succeeds in 95% of recoverable cases (NFR6 target)
- Human checkpoints presented in appropriate format based on confidence level
- Batch-continue respects tier-based batch sizes
- Task queue operations (add, remove, prioritize) complete within 100ms (NFR4)
- Stall detection uses SHA-256 hash comparison of consecutive outputs (FR19a)
- Party Mode escalation triggers when stall detected AND attempts >= 2; failed Party Mode hashes are tracked to prevent re-escalation (FR19b, FR19c)
- Fix strategy prioritizes memory-based solutions before fallback strategies (FR19d)
- Confidence defaults to 25% when no signals available; single-source capped at 60%; conflicting signals resolved by weighting higher-priority sources (Validation Verdict > Memory Match > Reviewer Agreement > Party Mode); calculation failures return 30% (FR19g-FR19j)
- Confidence Calculator applies tier adjustment and returns score 0-100 with threshold classification (High: >=70, Medium: 40-69, Low: <40) (FR19f)

---

### Epic 3: State & Recovery Management
**Goal:** Developers can interrupt, resume, and roll back workflows with confidence that work is preserved.

**User Outcome:** Close laptop, come back next day, invoke workflow-status, and resume exactly where you left off. If something goes wrong, rollback to a previous checkpoint.

**FRs covered:** FR26-FR30, FR60-FR62 (8 FRs)

**Components:** State persistence within Automation Controller, Sprint Status Watcher, Checkpoint system

**NFRs addressed:** NFR7 (State Persistence), NFR8 (Terminal States), NFR11 (Idempotency), NFR15 (File System - for state persistence files)

**Dependencies:** Epic 2b (Automation Controller for state operations; Sprint Status Watcher uses Automation Controller events). Note: Sprint Status Watcher is architecturally Tier 5 but functionally only depends on Automation Controller (Epic 2b), enabling earlier implementation.

**Acceptance Criteria:**
- Workflow state persists across conversation boundaries and resumes from last completed step with 100% reliability (FR27)
- All error paths reach terminal states (no infinite loops or hangs verified via testing)
- Checkpoints created before step transitions and validation fixes
- Rollback to previous checkpoint succeeds on user request
- Sprint Status Watcher monitors with 500ms debounce and 30s deduplication
- Sprint Status Watcher monitors bmm-workflow-status.yaml file for workflow state changes
- Repeated execution of same workflow step with identical inputs produces identical outputs and no duplicate state changes
- Idempotency enforced via state versioning - duplicate executions detected by matching step ID and input hash, then skipped without side effects. Verification: re-running completed step produces no new state file writes.
- Pending workflow task queue capped at 100 entries with FIFO overflow handling (FR29)

---

### Epic 4: Memory Integration
**Goal:** Workflows automatically leverage past decisions and save learnings for future sessions.

**User Outcome:** When fixing a validation error, the system stores successful fix patterns via Memory Bridge. The Memory Bridge component uses Context Pre-Loader (from Epic 2a) to read existing patterns, then writes new learnings.

**FRs covered:** FR32-FR34 (3 FRs)

**Components:** Memory Bridge, Post-Workflow Curator

**NFRs addressed:** NFR9 (Graceful Degradation), NFR10 (Graceful Degradation Details), NFR12 (MCP Compatibility)

**Dependencies:** Epic 2a (Context Pre-Loader initialized there; Memory Bridge reads existing memories via Context Pre-Loader from Epic 2a to inform fix strategies before writing new learnings)

**Acceptance Criteria:**
- Memory Bridge writes workflow decisions to Forgetful memory
- Post-Workflow Curator extracts key learnings with correct importance levels (9-10 architectural, 7-8 patterns, 6-7 milestones)
- System continues operating when Forgetful MCP unavailable (graceful degradation)
- Failed memory writes queued to local file with max 100 entries, FIFO overflow (NFR10)
- Memory cache TTL of 5 minutes (NFR10)

---

### Epic 5: Multi-Agent Orchestration
**Goal:** Complex problems automatically trigger collaborative problem-solving via Party Mode and parallel reviewers.

**User Outcome:** Stuck on a validation stall? Party Mode activates automatically with the right agents. Code review happens with adversarial reviewers who find real issues.

**FRs covered:** FR20-FR25b, FR42-FR44b (21 FRs)

**Components:** Party Mode Driver, Subagent Dispatcher, Loop-Back Handler

**NFRs addressed:** NFR1 (Timeout Enforcement), NFR5 (Extended Timeout Hierarchy), NFR6 (Recovery Rate)

**Dependencies:** Epic 2b (Automation Controller coordination)

**Acceptance Criteria:**
- Party Mode auto-triggers on BMB threshold violations (blocking_errors > 3 OR major_issues > 5) (FR21a)
- Party Mode auto-triggers on stall detection when attempts >= 2
- Party Mode auto-triggers when confidence < 60% at Tier 2+
- Subagent Dispatcher manages agent pool with dynamic model selection (Haiku/Sonnet/Opus)
- Code Review is adversarial - finds 3-10 specific issues per story
- Loop-Back Handler enforces MAX_VALIDATION_ITERATIONS=10 and MAX_SAME_ERROR_RETRIES=3
- All timeouts enforced: workflow (1800s), nested (300s), agent (60s), party round (120s)
- 95% of recoverable errors resolve without user intervention
- Party Mode exit keywords (*exit, goodbye, end party, quit) use literal string matching including asterisk character (FR21d)
- Brainstorming workflows handled via pre-seeding (Tier 3-4) or simulated ideation (Tier 0-2) (FR25a)
- Simulated Party Mode executes with 3-5 subagent personas for lower-tier workflows (FR25b)
- Code Review automatically invoked after story implementation completes (FR42)
- Review verdicts parsed and iteration count tracked across review cycles (FR43, FR44)
- Code Review produces one of three outcomes: Approve, Changes Requested, or Blocked (FR44b)
- Party Mode Driver handles in-flight response cleanup with 500ms grace period before session termination (FR21e)

---

### Epic 6: Parallel Artifact Validation
**Goal:** Agent and workflow creation (BMB module) runs with parallel validation and module-specific handling.

**User Outcome:** Creating a new custom agent via `/bmad:bmb:workflows:agent` runs 6 parallel validators, handles partial failures gracefully, and produces BMAD-compliant artifacts.

**FRs covered:** FR45-FR47c (6 FRs)

**Components:** Parallel BMB Validation

**NFRs addressed:** NFR1 (Timeout Enforcement - 5s mutex lock timeout), NFR5 (Extended Timeout Hierarchy - agent-level timeouts). Does not inherit NFR6 as Epic 6 has explicit partial failure handling per FR47c.

**Dependencies:** Epic 5 (Subagent Dispatcher for parallel execution)

**Acceptance Criteria:**
- Up to 6 validation checks run concurrently
- Synchronization barrier waits for all 6 subagents with 5s mutex timeout
- Partial failure handling follows defined rules: 6/0 success -> proceed; 4-5/1-2 -> retry failed sequentially; 2-3/3-4 -> retry all + escalate if still failing; 1/5 -> use single success as context for sequential retry; 0/6 -> abort parallel, fall back to full sequential
- Generated artifacts validated against BMAD standards
- BMB-specific confidence thresholds applied

---

### Epic 7: User Customization & Continuous Learning
**Goal:** Developers can customize automation behavior, control rate limiting, and the system learns from feedback.

**User Outcome:** Say "I prefer minimal interruptions" and tier behavior adjusts. Run 10 workflows and the system remembers your preferences. Sprint status is monitored in the background.

**FRs covered:** FR48-FR59, FR63-FR65 (15 FRs)

**Components:** Automation Controller (extended with tier override, lifecycle hooks, progress display features), Menu Participation Engine (extended with rate limiting), Memory Bridge (for feedback pattern storage)

**NFRs addressed:** NFR15 (File System)

**Dependencies:** Epic 2b (Automation Controller), Epic 4 (Memory Bridge for feedback storage), Epic 5 (Subagent Dispatcher infrastructure used for progress aggregation in multi-agent operations; single-agent progress uses Automation Controller directly)

**Acceptance Criteria:**
- Tier override methods work: natural language, explicit tier, profile switch, inline modifier
- Override priority enforced: explicit tier > profile switch > specific settings > natural language
- Hooks discovered from frontmatter and executed (PreToolUse, PostToolUse, Stop)
- Hook output limits enforced: 64KB stdout, 16KB stderr, 256KB total
- Menu rate limiting: 2s minimum interval, forced pause after 10 consecutive menus
- Progress modes work: Verbose, Summary, Silent, Streaming
- Explicit feedback commands stored to Forgetful memory
- Implicit feedback from user corrections detected and stored
- Streaming progress displays current step name and percentage for operations exceeding 30 seconds
- Progress summary available on user request showing completed steps, remaining steps, and estimated progress
- Safety-critical behavior (final approval, stall detection) cannot be bypassed by any tier override or configuration change - verified by attempting override of safety settings and confirming rejection
- Silent mode batches progress updates into end-of-operation summaries (FR57)

---

## Epic Summary

| Epic | User Value | FR Count | NFR Coverage | Dependencies |
|------|------------|----------|--------------|--------------|
| 1: Foundation Validation | Pre-flight checks work | 4 | - | None |
| 2a: Workflow Entry & Detection | Smart project classification | 13 | None (supports NFR15) | Epic 1 |
| 2b: Menu & Automation Core | Workflows run autonomously | 22 | NFR2-4, NFR6, NFR13-14 | Epics 1, 2a |
| 3: State & Recovery | Workflows can be paused/resumed | 8 | NFR7, NFR8, NFR11, NFR15 | Epic 2b |
| 4: Memory Integration | Past decisions inform current work | 3 | NFR9-10, NFR12 | Epic 2a |
| 5: Multi-Agent Orchestration | Complex problems get multi-perspective solutions | 21 | NFR1, NFR5-6 | Epic 2b |
| 6: Parallel Artifact Validation | BMB creation workflows run in parallel | 6 | NFR1, NFR5 | Epic 5 |
| 7: Customization & Learning | System adapts to user preferences | 15 | NFR15 | Epics 2b, 4, 5 |
| **Total** | | **92** | **15 NFRs** | |

*Note: Unique FR count is 92 (65 base FRs FR1-FR65 + 27 sub-lettered FRs: FR12a-b, FR19a-j, FR21a-e, FR23a-c, FR25a-b, FR44a-b, FR47a-c).

---

## Epic 1: Foundation Validation - Stories

### Story 1.1: Validation Type Detection

As a **workflow developer**,
I want **the system to automatically identify the validation type (verdict-based, error-based, or checklist-based) for any BMAD workflow**,
So that **the automation controller can apply the correct success criteria without manual configuration**.

**Acceptance Criteria:**

**Given** a workflow file with verdict-based validation (contains "PASS/FAIL" or "APPROVED/REJECTED" patterns)
**When** the Validation Type Detector analyzes the workflow
**Then** it returns `validation_type: "verdict-based"` with the detected verdict patterns

**Given** a workflow file with error-based validation (contains "0 errors" or "no issues" success criteria)
**When** the Validation Type Detector analyzes the workflow
**Then** it returns `validation_type: "error-based"` with the error detection patterns

**Given** a workflow file with checklist-based validation (contains checkbox items `[ ]` or `[x]`)
**When** the Validation Type Detector analyzes the workflow
**Then** it returns `validation_type: "checklist-based"` with the checkbox count

**Given** a workflow file with no recognizable validation pattern
**When** the Validation Type Detector analyzes the workflow
**Then** it returns `validation_type: "unknown"` with `confidence: 0`

---

### Story 1.2: Pre-flight Configuration Validation

As a **workflow user**,
I want **required configuration to be validated before a workflow starts**,
So that **I get immediate feedback on missing settings rather than failing mid-workflow**.

**Acceptance Criteria:**

**Given** a workflow requiring `output_folder` configuration
**When** the Pre-flight Validation Subagent runs before workflow start
**And** `output_folder` is not configured
**Then** it returns `status: "FAILED"` with `missing: ["output_folder"]` and a remediation message

**Given** a workflow requiring Forgetful MCP connection
**When** the Pre-flight Validation Subagent runs before workflow start
**And** Forgetful MCP is available
**Then** it returns `status: "PASSED"` for the MCP check

**Given** a workflow requiring input documents (PRD, Architecture)
**When** the Pre-flight Validation Subagent runs before workflow start
**And** the required input files exist at configured paths
**Then** it returns `status: "PASSED"` with `validated_files: [paths]`

**Given** all pre-flight checks pass
**When** the Pre-flight Validation Subagent completes
**Then** it returns `overall_status: "READY"` with 100% checks passed

---

### Story 1.3: Cross-Reference Document Alignment

As a **workflow user**,
I want **automatic detection of alignment issues between planning documents**,
So that **I catch missing requirements, orphaned decisions, and gaps before implementation starts**.

**Acceptance Criteria:**

**Given** a PRD with FR1, FR2, FR3 defined
**When** the Cross-Reference Validator compares PRD to Architecture
**And** Architecture references FR1 and FR2 but not FR3
**Then** it reports `orphaned_requirements: ["FR3"]` with severity "HIGH"

**Given** an Architecture document with decision ADR-001
**When** the Cross-Reference Validator compares Architecture to Stories
**And** no story references ADR-001
**Then** it reports `unaddressed_decisions: ["ADR-001"]` with affected components

**Given** aligned PRD, Architecture, and Stories documents
**When** the Cross-Reference Validator performs full comparison
**Then** it returns `alignment_status: "ALIGNED"` with `issues: []`

**Given** multiple alignment issues detected
**When** the Cross-Reference Validator completes
**Then** it returns issues sorted by severity (HIGH > MEDIUM > LOW)

---

### Story 1.4: Custom Validation Pattern Recognition

As a **workflow author**,
I want **custom validation patterns defined in workflow configuration to be recognized**,
So that **specialized workflows can define their own success criteria beyond the built-in types**.

**Acceptance Criteria:**

**Given** a workflow with custom validation pattern in frontmatter:
```yaml
validation:
  type: custom
  success_pattern: "Quality Gate: PASSED"
  failure_pattern: "Quality Gate: FAILED"
```
**When** the Validation Type Detector analyzes the workflow
**Then** it returns `validation_type: "custom"` with the registered patterns

**Given** a registered custom pattern "Quality Gate: PASSED"
**When** workflow output contains "Quality Gate: PASSED"
**Then** the pattern is detected and validation returns success

**Given** a custom pattern that conflicts with built-in patterns
**When** the Validation Type Detector analyzes the workflow
**Then** custom patterns take precedence over built-in detection

**Given** an invalid custom pattern definition (missing required fields)
**When** the Validation Type Detector attempts to register the pattern
**Then** it returns `error: "invalid_pattern"` with specific validation failures

---

## Epic 2a: Workflow Entry & Detection - Stories

### Story 2a.1: Skill Invocation Detection

As a **workflow user**,
I want **the system to detect when I invoke a BMAD skill using `/bmad:*` patterns**,
So that **workflow execution initiates automatically without additional commands**.

**Acceptance Criteria:**

**Given** a user invokes `/bmad:bmm:workflows:dev-story`
**When** the Workflow Entry Wrapper processes the input
**Then** it detects the skill pattern and returns `{module: "bmm", type: "workflows", name: "dev-story"}`

**Given** a user invokes `/bmad:core:workflows:brainstorming`
**When** the Workflow Entry Wrapper processes the input
**Then** it detects the core module pattern and initiates the brainstorming workflow

**Given** a user types a message without `/bmad:*` pattern
**When** the Workflow Entry Wrapper processes the input
**Then** it returns `{detected: false}` and does not initiate workflow execution

**Given** a malformed skill invocation `/bmad:invalid`
**When** the Workflow Entry Wrapper processes the input
**Then** it returns `{error: "invalid_skill_path"}` with valid pattern examples

---

### Story 2a.2: Autonomous Step Execution

As a **workflow user**,
I want **workflows to execute autonomously without prompting me at each step**,
So that **I can focus on decisions rather than clicking "continue" repeatedly**.

**Acceptance Criteria:**

**Given** a workflow with steps 1, 2, 3 and verdict-based success criteria
**When** step 1 completes with verdict "PASSED"
**Then** the system automatically transitions to step 2 without user prompt

**Given** a workflow step with `oversight: required` in configuration
**When** the step completes successfully
**Then** the system pauses for user confirmation before proceeding

**Given** a workflow step that fails validation
**When** the Automation Controller detects the failure
**Then** it attempts recovery before escalating to user (per FR16)

**Given** a workflow with no oversight requirements
**When** all steps complete successfully
**Then** the entire workflow completes autonomously with only a final summary

---

### Story 2a.3: Project Type Detection

As a **workflow user**,
I want **the system to automatically detect if my project is greenfield or brownfield**,
So that **appropriate workflow paths and templates are selected**.

**Acceptance Criteria:**

**Given** a project directory with no `src/`, `lib/`, or `app/` directories
**And** no `package.json` or `pyproject.toml` files
**And** fewer than 10 source files
**When** the Workflow Entry Wrapper analyzes the project
**Then** it returns `project_type: "greenfield"`

**Given** a project directory with `src/` directory containing 50+ files
**And** a `package.json` file present
**When** the Workflow Entry Wrapper analyzes the project
**Then** it returns `project_type: "brownfield"`

**Given** a project with `package.json` but no source directories
**When** the Workflow Entry Wrapper analyzes the project
**Then** it returns `project_type: "brownfield"` (package file indicates existing project)

**Given** project detection completes
**When** the result is returned
**Then** it includes `detection_signals: [list of matched criteria]` for transparency

---

### Story 2a.4: Tier Suggestion

As a **workflow user**,
I want **the system to recommend an appropriate project tier (0-4) based on my description**,
So that **the methodology depth matches my project's actual complexity**.

**Acceptance Criteria:**

**Given** a user description containing "fix", "bug", "typo", or "patch"
**When** the Tier Suggester analyzes the description
**Then** it suggests `tier: 0` (Single Atomic Change) with matched keywords

**Given** a user description containing "platform", "integration", "complex system"
**When** the Tier Suggester analyzes the description
**Then** it suggests `tier: 3` (Complex System) with matched keywords

**Given** a description with mixed signals ("simple dashboard with complex integrations")
**When** the Tier Suggester analyzes the description
**Then** it suggests the tier indicated by >50% of detected keywords with confidence score

**Given** a description with no recognizable tier keywords
**When** the Tier Suggester analyzes the description
**Then** it defaults to `tier: 2` (Medium Project) with `confidence: "low"`

**Given** a brownfield project with existing codebase metrics
**When** the Tier Suggester combines description analysis with code metrics
**Then** it adjusts tier suggestion based on actual codebase size and complexity

---

### Story 2a.5: Context Pre-Loading from Memory

As a **workflow user**,
I want **relevant memories from Forgetful to be loaded before my workflow starts**,
So that **past decisions and patterns inform the current work**.

**Acceptance Criteria:**

**Given** a workflow starting for project "pcmrp-migration"
**When** the Context Pre-Loader queries Forgetful memory
**Then** it retrieves memories matching project_id and workflow-relevant keywords

**Given** memories retrieved include architectural decisions (importance 9-10)
**When** the Context Pre-Loader prepares agent context
**Then** high-importance memories are prioritized in the context window

**Given** Forgetful MCP is unavailable
**When** the Context Pre-Loader attempts to query
**Then** it logs the failure and continues with empty context (graceful degradation)

**Given** memories are retrieved successfully
**When** the workflow agent initializes
**Then** the agent context contains at least 1 relevant memory when available (FR35)

**Given** multiple relevant memories exist
**When** the Context Pre-Loader prepares context
**Then** it deduplicates and summarizes to fit context limits

---

### Story 2a.6: Workflow Configuration Parsing

As a **workflow developer**,
I want **the system to read configuration from both YAML and Markdown frontmatter**,
So that **I can define workflow behavior in my preferred format**.

**Acceptance Criteria:**

**Given** a workflow file `workflow.yaml` with configuration block
**When** the Automation Controller loads the workflow
**Then** it parses YAML configuration and applies settings

**Given** a workflow file `workflow.md` with YAML frontmatter (between `---` delimiters)
**When** the Automation Controller loads the workflow
**Then** it extracts and parses the frontmatter configuration

**Given** a workflow with module-specific settings `module: bmm`
**When** the Automation Controller applies configuration
**Then** BMM-specific defaults and behaviors are activated

**Given** a workflow with module-specific settings `module: bmb`
**When** the Automation Controller applies configuration
**Then** BMB-specific thresholds (blocking_errors > 3, etc.) are activated

**Given** a configuration file with syntax errors
**When** the Automation Controller attempts to parse
**Then** it returns `error: "config_parse_error"` with line number and details

---

### Story 2a.7: Adaptive Behavior Configuration

As a **workflow user**,
I want **automation behavior to adapt based on project classification and configurable thresholds**,
So that **different projects get appropriately calibrated automation**.

**Acceptance Criteria:**

**Given** a Tier 0-1 project (simple)
**When** the Automation Controller initializes
**Then** it applies aggressive automation (auto-all batch size, minimal checkpoints)

**Given** a Tier 3-4 project (complex/enterprise)
**When** the Automation Controller initializes
**Then** it applies conservative automation (small batch sizes, more checkpoints)

**Given** a workflow type with custom confidence thresholds in configuration
**When** the Confidence Calculator evaluates decisions
**Then** it uses the workflow-specific thresholds instead of defaults

**Given** a project classified as `domain: "healthcare"` or `domain: "finance"`
**When** the Automation Controller initializes
**Then** it enables additional validation gates appropriate for regulated domains

**Given** configurable thresholds are modified mid-workflow
**When** the next decision point is reached
**Then** the updated thresholds are applied immediately

---

## Epic 2b: Menu & Automation Core - Stories

### Story 2b.1: Menu Detection with Confidence Scoring

As a **workflow automation system**,
I want **to detect menus in workflow output using confidence scoring**,
So that **menus are identified accurately without false positives in code blocks or examples**.

**Acceptance Criteria:**

**Given** workflow output containing `[A] Advanced Elicitation [P] Party Mode [C] Continue`
**When** the Menu Participation Engine analyzes the output
**Then** it returns `menu_detected: true` with confidence >= 70 points

**Given** workflow output containing menu-like text inside a code block (``` markers)
**When** the Menu Participation Engine analyzes the output
**Then** it returns `menu_detected: false` (false positive guard activated)

**Given** workflow output containing menu-like text inside a blockquote (> prefix)
**When** the Menu Participation Engine analyzes the output
**Then** it returns `menu_detected: false` (false positive guard activated)

**Given** workflow output containing menu-like text labeled as "Example:"
**When** the Menu Participation Engine analyzes the output
**Then** it returns `menu_detected: false` (example content guard activated)

**Given** menu detection with structural markers (brackets, numbered options)
**When** confidence is calculated
**Then** the score includes: structural markers (+30), position validation (+20), option count (+20)

---

### Story 2b.2: Automatic Menu Selection

As a **workflow user**,
I want **menus to be selected automatically when confidence is high**,
So that **I don't have to manually select obvious choices**.

**Acceptance Criteria:**

**Given** a detected menu with confidence >= 80%
**When** the Menu Participation Engine evaluates options
**Then** it automatically selects the most appropriate option without user prompt

**Given** a detected menu with confidence between 50-79%
**When** the Menu Participation Engine evaluates options
**Then** it presents the menu to user with a recommended selection

**Given** a detected menu with confidence < 50%
**When** the Menu Participation Engine evaluates options
**Then** it presents the menu to user without recommendation

**Given** automatic selection is made
**When** the selection is logged
**Then** it includes `selection_reason` and `confidence_score` for auditability

**Given** any menu detection and selection operation
**When** the operation completes under normal conditions
**Then** total time from detection to selection is under 5 seconds (NFR2 compliance)

---

### Story 2b.3: BMB-Specific Menu Thresholds

As a **BMB module user**,
I want **BMB-specific thresholds applied to menu decisions**,
So that **agent and workflow creation gets appropriate quality gates**.

**Acceptance Criteria:**

**Given** a BMB workflow validation result with `blocking_errors > 3`
**When** the Menu Participation Engine processes the result
**Then** it automatically triggers Party Mode escalation

**Given** a BMB workflow validation result with `major_issues > 5`
**When** the Menu Participation Engine processes the result
**Then** it automatically triggers Party Mode escalation

**Given** a BMB workflow with `compliance_score < 70`
**When** the Menu Participation Engine processes the result
**Then** it automatically triggers Advanced Elicitation

**Given** a BMB workflow with `blocking_errors <= 3` AND `major_issues <= 5` AND `compliance_score >= 70`
**When** the Menu Participation Engine processes the result
**Then** it proceeds to Continue without escalation

---

### Story 2b.4: Nested Menu Handling

As a **workflow user**,
I want **nested menus within Party Mode or Advanced Elicitation to be handled correctly**,
So that **sub-workflows complete properly before returning to the parent menu**.

**Acceptance Criteria:**

**Given** Party Mode is active and presents an internal menu
**When** the Menu Participation Engine detects the nested menu
**Then** it tracks the menu depth and handles selection within Party Mode context

**Given** Advanced Elicitation presents technique selection menu
**When** the Menu Participation Engine processes the menu
**Then** it applies elicitation-specific selection logic

**Given** a nested menu completes with a selection
**When** control returns to the parent workflow
**Then** the parent workflow state is restored correctly

**Given** nested menu depth exceeds 3 levels
**When** the Menu Participation Engine detects this
**Then** it logs a warning and escalates to user for manual navigation

---

### Story 2b.5: Menu History Tracking

As a **workflow automation system**,
I want **menu selection history tracked for recovery purposes**,
So that **interrupted workflows can resume with correct menu context**.

**Acceptance Criteria:**

**Given** a menu selection is made (automatic or manual)
**When** the selection is processed
**Then** it is recorded to `menu_history` with timestamp, menu_id, selection, and confidence

**Given** a workflow is interrupted after menu selections
**When** the workflow resumes
**Then** menu history is available to restore context

**Given** menu history grows beyond 100 entries
**When** a new entry is added
**Then** oldest entries are pruned (FIFO) to maintain limit

**Given** a recovery scenario needs to replay menu selections
**When** history is accessed
**Then** entries are returned in chronological order with full metadata

---

### Story 2b.6: Batch-Continue Logic

As a **workflow user**,
I want **multiple continue operations batched based on project tier**,
So that **simple projects flow faster while complex projects get more checkpoints**.

**Acceptance Criteria:**

**Given** a Tier 0-1 project with sequential continue menus
**When** the Menu Participation Engine processes them
**Then** it auto-continues all without batching (auto-all mode)

**Given** a Tier 2 project with sequential continue menus
**When** the Menu Participation Engine processes them
**Then** it batches up to 5 continues before presenting checkpoint

**Given** a Tier 3 project with sequential continue menus
**When** the Menu Participation Engine processes them
**Then** it batches up to 3 continues before presenting checkpoint

**Given** a Tier 4 project with sequential continue menus
**When** the Menu Participation Engine processes them
**Then** it batches exactly 1 continue (batch size 1) for maximum oversight, presenting checkpoint after each operation

**Given** a batch completes
**When** the checkpoint is presented
**Then** it shows summary of batched operations with option to review details

**Given** batch-continue mode is active
**When** operations are batched
**Then** context is managed to avoid redundant menu state in history, reducing token usage compared to unbatched operation (NFR3 compliance)

---

### Story 2b.7: Human Checkpoint Presentation

As a **workflow user**,
I want **human checkpoints presented in appropriate detail based on confidence**,
So that **high-confidence operations don't overwhelm me while low-confidence ones get full context**.

**Acceptance Criteria:**

**Given** a checkpoint with confidence >= 80%
**When** the checkpoint is presented to user
**Then** it uses Minimal format (1-2 line summary, single confirm button)

**Given** a checkpoint with confidence 50-79%
**When** the checkpoint is presented to user
**Then** it uses Summary format (key decisions listed, expandable details)

**Given** a checkpoint with confidence < 50%
**When** the checkpoint is presented to user
**Then** it uses Full Audit Trail format (complete operation log, explicit approval required)

**Given** any checkpoint is presented
**When** user reviews it
**Then** they can expand to full details regardless of initial format

---

### Story 2b.8: Validation Failure Recovery

As a **workflow user**,
I want **the system to attempt automatic recovery from validation failures**,
So that **most issues resolve without interrupting my work**.

**Acceptance Criteria:**

**Given** a validation failure due to missing configuration
**When** the Automation Controller detects the failure
**Then** it attempts to locate or prompt for the missing config before user escalation

**Given** a validation failure due to transient error (network, timeout)
**When** the Automation Controller detects the failure
**Then** it retries up to 3 times with exponential backoff before escalation

**Given** a validation failure with known fix pattern in memory
**When** the Automation Controller queries existing fix patterns via Context Pre-Loader (from Epic 2a)
**Then** it applies the remembered fix pattern automatically

**Given** recovery attempts succeed
**When** workflow resumes
**Then** the recovery is logged with `recovery_method` and `attempts_count`

**Given** recovery attempts fail after all strategies exhausted
**When** escalation to user occurs
**Then** it includes attempted strategies and specific failure reasons

---

### Story 2b.9: Timeout Enforcement

As a **workflow automation system**,
I want **timeout hierarchy enforced at all levels**,
So that **no operation hangs indefinitely**.

**Acceptance Criteria:**

**Given** a workflow running for more than 1800 seconds (30 minutes)
**When** the timeout is reached
**Then** the workflow is terminated with `timeout_error: "workflow_timeout"`

**Given** a nested operation running for more than 300 seconds (5 minutes)
**When** the timeout is reached
**Then** the nested operation is terminated and parent workflow notified

**Given** an agent operation running for more than 60 seconds
**When** the timeout is reached
**Then** the agent is terminated with `timeout_error: "agent_timeout"`

**Given** a timeout occurs
**When** the operation is terminated
**Then** state is preserved for potential resume and timeout is logged

---

### Story 2b.10: Terminal State Enforcement

As a **workflow automation system**,
I want **all error paths to reach terminal states**,
So that **no workflow hangs in an unrecoverable state**.

**Acceptance Criteria:**

**Given** an error occurs during workflow execution
**When** recovery is attempted and fails
**Then** the workflow reaches terminal state FAILED with error details

**Given** a workflow completes all steps successfully
**When** final validation passes
**Then** the workflow reaches terminal state COMPLETED

**Given** a user cancels a workflow
**When** cancellation is processed
**Then** the workflow reaches terminal state CANCELLED with cleanup performed

**Given** any workflow state
**When** the state machine is queried
**Then** a valid path to a terminal state exists (verified via testing)

**Given** potential infinite loop detected (same state visited 5+ times)
**When** the loop is detected
**Then** workflow is terminated with `error: "infinite_loop_detected"`

---

### Story 2b.11: Confidence Score Calculation

As a **workflow automation system**,
I want **confidence scores calculated from multiple signal sources**,
So that **decisions reflect the true reliability of available information**.

**Acceptance Criteria:**

**Given** 4 signal sources available (Validation Verdict, Memory Match, Reviewer Agreement, Party Mode Outcome)
**When** the Confidence Calculator computes a score
**Then** it combines: Validation Verdict (0-35pts), Memory Match (0-25pts), Reviewer Agreement (0-25pts), Party Mode Outcome (0-15pts) = 100pts max

**Given** the optional 5th signal (model selection) is active
**When** the Confidence Calculator computes a score
**Then** weights are scaled proportionally: each base weight multiplied by (100/110), model selection contributes 0-9.1pts, maintaining 0-100 scale total

**Given** no signals are available
**When** the Confidence Calculator is invoked
**Then** it returns default confidence of 25%

**Given** only one signal source is available
**When** the Confidence Calculator computes a score
**Then** it caps the result at 60% maximum (single-source cap)

**Given** conflicting signals detected (signals differ by >30 points when normalized to 0-100)
**When** the Confidence Calculator resolves conflicts
**Then** it applies weighted priority resolution: Validation Verdict (1.5x multiplier) > Memory Match (1.25x) > Reviewer Agreement (1.0x) > Party Mode (0.75x). Final score = sum of (signal_score * priority_multiplier * base_weight) / sum of (priority_multiplier * base_weight). Non-conflicting signals use simple weighted average.

**Given** calculation fails due to error
**When** the Confidence Calculator handles the error
**Then** it returns fallback confidence of 30%

**Given** confidence score is calculated
**When** the result is returned
**Then** it includes threshold classification: High (>=70), Medium (40-69), Low (<40). Note: Classification thresholds differ from decision thresholds - autonomous decisions require >=80% (Story 2b.2), checkpoint format uses 50/80% boundaries (Story 2b.7)

---

### Story 2b.12: Stall Detection and Escalation

As a **workflow user**,
I want **validation stalls detected and escalated to Party Mode**,
So that **stuck workflows get multi-perspective problem solving**.

**Acceptance Criteria:**

**Given** two consecutive validation outputs with identical SHA-256 hash
**When** the Automation Controller compares outputs
**Then** it detects a stall condition

**Given** a stall is detected and validation attempts >= 2
**When** escalation logic runs
**Then** Party Mode is triggered automatically

**Given** Party Mode is triggered for a stall
**When** Party Mode fails to resolve the issue
**Then** the failed Party Mode hash is tracked to prevent re-escalation loop

**Given** a stall with attempts < 2
**When** escalation logic runs
**Then** it retries validation with memory-first fix strategy before escalation

**Given** memory-first fix strategy fails
**When** fallback strategies are attempted
**Then** it tries in order: memory patterns, heuristic fixes, template-based fixes, user escalation

**Given** Party Mode resolves a stall
**When** the resolution is processed
**Then** the successful fix pattern is stored to Memory Bridge for future use; if Memory Bridge unavailable, pattern is queued per Epic 4 graceful degradation

---

## Epic 3: State & Recovery Management - Stories

### Story 3.1: Workflow State Persistence

As a **workflow user**,
I want **workflow state persisted across conversation boundaries**,
So that **my progress is never lost even if the session ends unexpectedly**.

**Acceptance Criteria:**

**Given** a workflow executing step 3 of 5
**When** the conversation ends (timeout, disconnect, user closes)
**Then** state is persisted with `current_step: 3`, `completed_steps: [1, 2]`, and step-specific data

**Given** workflow state is being saved
**When** persistence operation executes
**Then** state is written to `_bmad-output/.workflow-state/{workflow_id}.json`

**Given** state file exists from previous session
**When** the same workflow is invoked
**Then** the system detects existing state and offers resume option

**Given** state persistence fails (disk error, permissions)
**When** the failure is detected
**Then** retry is attempted with exponential backoff and user is warned if all retries fail

---

### Story 3.2: Workflow Resume from Interruption

As a **workflow user**,
I want **to resume workflows from the last completed step**,
So that **I don't have to restart from the beginning after interruptions**.

**Acceptance Criteria:**

**Given** a persisted workflow state with `completed_steps: [1, 2, 3]`
**When** the user invokes workflow-status or the same workflow
**Then** the system offers to resume from step 4

**Given** user confirms resume
**When** the workflow restarts
**Then** it loads state from step 3 output and begins step 4 execution

**Given** persisted state is corrupted or invalid
**When** resume is attempted
**Then** the system offers to start fresh with clear warning about lost progress

**Given** workflow has been updated since state was saved
**When** resume is attempted with incompatible state
**Then** the system detects version mismatch and advises fresh start

**Given** resume succeeds
**When** workflow continues
**Then** progress counter shows "Resumed at step 4/5" with visual indicator

---

### Story 3.3: Sprint Status File Monitoring

As a **workflow automation system**,
I want **sprint status files monitored for changes**,
So that **workflow state changes trigger appropriate responses**.

**Acceptance Criteria:**

**Given** `bmm-workflow-status.yaml` file exists
**When** the Sprint Status Watcher initializes
**Then** it begins monitoring with 500ms debounce interval

**Given** file is modified twice within 500ms
**When** debounce period elapses
**Then** only one change event is processed (debounce working)

**Given** same change is detected within 30s deduplication window
**When** change event would be raised
**Then** it is suppressed as duplicate (30s deduplication)

**Given** potential race condition (concurrent writes)
**When** file access occurs
**Then** dual compare-and-swap prevents corruption: (1) CAS for file content, (2) CAS for status field - both must succeed atomically. If CAS #1 succeeds but CAS #2 fails, CAS #1 is rolled back before retry. Algorithm: read version -> modify -> compare expected version -> swap if match, rollback on partial success, retry up to 3 times on version mismatch

**Given** status cycling detected (A->B->A->B pattern)
**When** cycle count exceeds 3
**Then** warning is logged and monitoring continues with increased debounce

---

### Story 3.4: Pending Task Queue Management

As a **workflow automation system**,
I want **pending workflow tasks managed in a queue**,
So that **multiple workflows can be queued and processed in order**.

**Acceptance Criteria:**

**Given** a new workflow is triggered while another is active
**When** the task is queued
**Then** it is added to pending queue with timestamp and priority

**Given** active workflow completes
**When** the queue is checked
**Then** next pending task is dequeued and started (FIFO order)

**Given** queue contains 100 entries
**When** a new task is added
**Then** oldest entry is removed (FIFO overflow) and warning logged

**Given** queue operations (add, remove, prioritize)
**When** the operation executes
**Then** it completes within 100ms (NFR4)

**Given** task in queue is cancelled by user
**When** cancellation is processed
**Then** task is removed from queue without affecting other entries

**Given** system restarts
**When** queue state is loaded
**Then** persisted queue entries are restored with correct order

---

### Story 3.5: Step Completion Tracking

As a **workflow user**,
I want **completion status tracked for all workflow steps**,
So that **I can see progress and know exactly where I am in the workflow**.

**Acceptance Criteria:**

**Given** a workflow with 5 steps
**When** step 2 completes successfully
**Then** completion status shows `step_2: {status: "completed", completed_at: timestamp, duration_ms: N}`

**Given** a step fails
**When** failure is recorded
**Then** completion status shows `step_N: {status: "failed", error: "reason", attempts: N}`

**Given** a step is skipped (optional step not executed)
**When** workflow proceeds
**Then** completion status shows `step_N: {status: "skipped", reason: "optional"}`

**Given** user requests progress
**When** status is queried
**Then** response includes completed count, remaining count, current step name, and estimated progress %

---

### Story 3.6: Checkpoint Creation

As a **workflow user**,
I want **checkpoints created at key workflow points**,
So that **I can rollback if something goes wrong**.

**Acceptance Criteria:**

**Given** workflow is about to transition from step N to step N+1
**When** the transition begins
**Then** a checkpoint is created with current state snapshot

**Given** validation fixes are about to be applied
**When** the fix operation begins
**Then** a checkpoint is created before modifications

**Given** checkpoint is created
**When** checkpoint data is saved
**Then** it includes: `step_id`, `timestamp`, `state_snapshot`, `can_rollback: true`

**Given** checkpoint data is written to frontmatter
**When** the file is saved
**Then** checkpoint is persisted in document frontmatter under `checkpoints: []`

**Given** more than 10 checkpoints exist for a workflow
**When** new checkpoint is created
**Then** oldest checkpoint beyond the 10 most recent is pruned

---

### Story 3.7: Rollback to Checkpoint

As a **workflow user**,
I want **to rollback to a previous checkpoint on request**,
So that **I can recover from mistakes or unwanted changes**.

**Acceptance Criteria:**

**Given** user says "undo" or "rollback"
**When** the command is processed
**Then** system shows available checkpoints with step names and timestamps

**Given** user says "rollback to step 3"
**When** the command is processed
**Then** system finds checkpoint for step 3 and confirms rollback action

**Given** rollback is confirmed
**When** rollback executes
**Then** state is restored from checkpoint and workflow resumes from that point

**Given** user requests rollback to a step whose checkpoint was pruned (beyond 10 most recent)
**When** rollback is attempted
**Then** system explains checkpoint was pruned due to age, offers nearest available checkpoint, and suggests manual recreation if critical

**Given** checkpoint has `can_rollback: false`
**When** user attempts rollback to that checkpoint
**Then** system explains why rollback is not available and offers alternatives

**Given** rollback succeeds
**When** workflow state is updated
**Then** steps after rollback point are marked as `status: "rolled_back"`

**Given** rollback target checkpoint has associated output files
**When** rollback executes
**Then** output files from steps after rollback point are preserved in `_bmad-output/.rollback-archive/{timestamp}/` but not used by resumed workflow

**Given** rollback fails (corrupted checkpoint, missing files)
**When** failure is detected
**Then** current state is preserved and user is informed of failure reason

---

## Epic 4: Memory Integration - Stories

### Story 4.1: Writing Workflow Decisions to Memory

As a **workflow automation system**,
I want **workflow decisions and outcomes written to Forgetful memory**,
So that **future workflows can learn from past experiences**.

**Acceptance Criteria:**

**Given** a workflow completes with key decisions made
**When** the Memory Bridge processes the workflow outcome
**Then** it creates memories for each significant decision with appropriate importance level

**Given** a validation fix pattern resolves an issue
**When** the fix is successful
**Then** Memory Bridge writes a memory with `type: "fix_pattern"`, the error signature, and the solution

**Given** a menu selection leads to successful outcome
**When** workflow completes successfully
**Then** Memory Bridge optionally records the selection pattern for similar future contexts

**Given** memory content exceeds 2000 characters
**When** Memory Bridge prepares the memory
**Then** it summarizes to fit the atomic memory limit while preserving key information

**Given** memory is created
**When** the write completes
**Then** it includes: `project_id`, `workflow_id`, `keywords`, `tags`, and appropriate `importance` level

---

### Story 4.2: Post-Workflow Learning Extraction

As a **workflow user**,
I want **key learnings automatically extracted after workflow completion**,
So that **important patterns are preserved without manual effort**.

**Acceptance Criteria:**

**Given** a workflow completes successfully
**When** Post-Workflow Curator analyzes the session
**Then** it identifies architectural decisions, implementation patterns, and milestone completions

**Given** an architectural decision is identified (e.g., "chose PostgreSQL over MongoDB")
**When** the memory is created
**Then** it has `importance: 9-10` (architectural decisions)

**Given** an implementation pattern is identified (e.g., "used retry with exponential backoff")
**When** the memory is created
**Then** it has `importance: 7-8` (patterns)

**Given** a milestone completion is identified (e.g., "Phase 2 complete")
**When** the memory is created
**Then** it has `importance: 6-7` (milestones)

**Given** Post-Workflow Curator identifies a problem-solution pair
**When** the memory is created
**Then** it includes both the problem signature and the successful solution approach

**Given** similar memory already exists
**When** duplication check runs
**Then** existing memory is linked instead of creating duplicate

---

### Story 4.3: Graceful Degradation When Memory Unavailable

As a **workflow user**,
I want **the system to continue operating when Forgetful MCP is unavailable**,
So that **memory issues don't block my workflow**.

**Acceptance Criteria:**

**Given** Forgetful MCP connection fails
**When** Memory Bridge attempts to write
**Then** it retries 3 times at 100ms intervals before failing over

**Given** all retries fail
**When** failover activates
**Then** memory is queued to local file at `_bmad-output/.memory-queue/`

**Given** local memory queue exists
**When** new memory is queued
**Then** it is appended with timestamp and `status: "pending"`

**Given** queue contains 100 entries
**When** new entry is added
**Then** oldest entry is removed (FIFO overflow) and warning logged

**Given** queued memories exist
**When** Forgetful MCP becomes available
**Then** queued memories are flushed to Forgetful in order

**Given** Forgetful MCP unavailable for 4+ hours
**When** status is checked
**Then** it is marked as `PERMANENTLY_UNAVAILABLE` and queue processing stops

**Given** memory read is attempted during unavailability
**When** cache exists (< 5 minute TTL)
**Then** cached results are returned with staleness indicator

**Given** cache is stale or missing during unavailability
**When** read is attempted
**Then** empty result is returned with `source: "degraded"` flag

**Given** writes are being queued locally during degradation
**When** Context Pre-Loader queries for recently-written patterns from same session
**Then** local queue is also searched before returning empty result, ensuring session-local patterns are found

---

## Epic 5: Multi-Agent Orchestration - Stories

### Story 5.1: Party Mode Programmatic Input

As a **workflow automation system**,
I want **to provide programmatic inputs for each Party Mode conversation round**,
So that **multi-agent discussions proceed automatically without manual intervention**.

**Acceptance Criteria:**

**Given** Party Mode is initiated for a validation stall
**When** the first round begins
**Then** Party Mode Driver provides initial context and problem statement programmatically

**Given** a Party Mode round completes with agent responses
**When** the next round begins
**Then** Party Mode Driver synthesizes previous responses and provides follow-up prompt

**Given** Party Mode Driver prepares round input
**When** input is submitted
**Then** it includes: round number, discussion context, specific questions, and expected output format

**Given** agent responses are ambiguous or off-topic
**When** Party Mode Driver prepares next round
**Then** it includes clarifying questions to redirect discussion

---

### Story 5.2: Party Mode Round Progress Tracking

As a **workflow automation system**,
I want **Party Mode round progress tracked with completion detection**,
So that **discussions end when consensus is reached or maximum rounds exceeded**.

**Acceptance Criteria:**

**Given** Party Mode is running
**When** each round completes
**Then** progress is tracked with `round_number`, `agents_responded`, `consensus_level`

**Given** all agents converge on same recommendation
**When** consensus is detected
**Then** Party Mode exits early with `exit_reason: "consensus_reached"`

**Given** maximum rounds (default: 5) is reached
**When** round limit is hit
**Then** Party Mode exits with `exit_reason: "max_rounds"` and best recommendation

**Given** no progress made for 2 consecutive rounds
**When** stagnation is detected
**Then** Party Mode escalates to user with summary of positions

---

### Story 5.3: Party Mode Auto-Trigger Conditions

As a **workflow user**,
I want **Party Mode to trigger automatically under specific conditions**,
So that **complex problems get multi-perspective attention without manual escalation**.

**Acceptance Criteria:**

**Given** a BMB workflow with `blocking_errors > 3` OR `major_issues > 5`
**When** the threshold is exceeded
**Then** Party Mode is auto-triggered with BMB agent configuration

**Given** validation stall detected AND attempts >= 2
**When** stall escalation logic runs
**Then** Party Mode is auto-triggered with problem context

**Given** confidence score < 60% at Tier 2 or higher
**When** low confidence is detected
**Then** Party Mode is auto-triggered for additional perspectives

**Given** a Tier 3-4 project with all validation steps complete and ready for workflow completion
**When** the final step transition is initiated
**Then** Party Mode provides mandatory pre-final review with at least 2 agent perspectives before allowing workflow completion

---

### Story 5.4: Party Mode Session Termination

As a **workflow automation system**,
I want **Party Mode sessions to terminate cleanly with proper cleanup**,
So that **resources are released and in-flight responses handled gracefully**.

**Acceptance Criteria:**

**Given** Party Mode receives exit keyword: "*exit", "goodbye", "end party", or "quit"
**When** the keyword is detected (literal string match, asterisk is literal character)
**Then** session termination begins immediately

**Given** agents have in-flight responses when termination begins
**When** the 500ms grace period elapses
**Then** remaining responses are discarded and cleanup completes

**Given** Party Mode completes normally
**When** termination executes
**Then** final summary is generated with recommendations and confidence level

**Given** Party Mode is forcefully terminated (timeout, error)
**When** cleanup runs
**Then** partial results are preserved and error state is logged

---

### Story 5.5: Subagent Pool Management

As a **workflow automation system**,
I want **agent pool allocation and lifecycle managed efficiently**,
So that **agents are available when needed without resource waste**.

**Acceptance Criteria:**

**Given** a workflow requires specialized agents
**When** Subagent Dispatcher initializes
**Then** it allocates agents from pool based on task requirements

**Given** agent task completes
**When** agent is released
**Then** it returns to pool for reuse or is terminated based on pool policy

**Given** pool size exceeds maximum (default: 10 concurrent)
**When** new agent is requested
**Then** oldest idle agent is terminated to make room

**Given** agent crashes or times out
**When** failure is detected
**Then** agent is removed from pool and new agent spawned if needed

**Given** all agents in pool are busy
**When** new agent is requested with `priority: high`
**Then** lowest-priority task is preempted to free an agent

---

### Story 5.6: Task Routing to Specialized Agents

As a **workflow automation system**,
I want **tasks routed to appropriate specialized agents**,
So that **the right expertise is applied to each task type**.

**Acceptance Criteria:**

**Given** a validation task
**When** Subagent Dispatcher routes the task
**Then** it selects a validation-specialized agent (Cross-Reference, Pre-flight, etc.)

**Given** a code review task
**When** Subagent Dispatcher routes the task
**Then** it selects adversarial code reviewer agent

**Given** a creative task (brainstorming, ideation)
**When** Subagent Dispatcher routes the task
**Then** it selects creative/analyst agent configuration

**Given** task type is unknown
**When** Subagent Dispatcher evaluates routing
**Then** it uses general-purpose agent with warning logged

---

### Story 5.7: Dynamic Model Selection

As a **workflow automation system**,
I want **models selected dynamically based on task type and tier**,
So that **expensive models are used only when needed**.

**Acceptance Criteria:**

**Given** a simple validation task at Tier 0-1
**When** model selection runs
**Then** Haiku is selected for fast, cost-effective processing

**Given** a complex analysis task at Tier 3-4
**When** model selection runs
**Then** Opus is selected for deep reasoning capability

**Given** a standard implementation task at Tier 2
**When** model selection runs
**Then** Sonnet is selected as balanced default

**Given** task requires code generation
**When** model selection considers task type
**Then** preference shifts toward Sonnet/Opus regardless of tier

**Given** budget constraints are active
**When** model selection runs
**Then** it respects `max_model` configuration setting

---

### Story 5.8: Context Forking for Parallel Reviewers

As a **workflow automation system**,
I want **context forked for parallel reviewers with information asymmetry**,
So that **reviewers provide independent perspectives without groupthink**.

**Acceptance Criteria:**

**Given** parallel code review with 4 reviewers
**When** Subagent Dispatcher initializes reviewers
**Then** each reviewer gets forked context with different emphasis areas

**Given** forked contexts are created
**When** reviewers execute
**Then** they cannot see each other's findings until aggregation

**Given** reviewers complete independently
**When** results are aggregated
**Then** Subagent Dispatcher merges findings with deduplication

**Given** subagent is spawned
**When** agent_id is assigned
**Then** it is tracked for potential resumption via Claude Code 2.1 Task resume

---

### Story 5.9: Edit-Module Iteration Tracking

As a **workflow automation system**,
I want **iteration count tracked for Edit-Module workflows**,
So that **progress is visible and limits can be enforced**.

**Acceptance Criteria:**

**Given** an Edit-Module workflow starts
**When** Loop-Back Handler initializes
**Then** iteration count starts at 0

**Given** a validation-edit-revalidate cycle completes
**When** the loop iterates
**Then** iteration count increments and is logged

**Given** iteration state exists
**When** status is queried
**Then** response includes `current_iteration`, `max_iterations`, `errors_by_iteration`

**Given** same error appears in consecutive iterations
**When** the error is detected
**Then** `same_error_count` is tracked separately from total iterations

---

### Story 5.10: Iteration Limit Enforcement

As a **workflow user**,
I want **maximum iteration limits enforced to prevent infinite loops**,
So that **stuck workflows don't run forever**.

**Acceptance Criteria:**

**Given** iteration count reaches MAX_VALIDATION_ITERATIONS (10)
**When** the limit is hit
**Then** workflow exits with `error: "max_iterations_exceeded"` and summary of attempts

**Given** same error occurs MAX_SAME_ERROR_RETRIES (3) times consecutively
**When** the limit is hit
**Then** workflow escalates with `error: "persistent_error"` and error details

**Given** oscillation pattern detected using sliding 5-iteration window (error A -> fix -> error B -> fix -> error A pattern)
**When** the same error signature appears 3+ times within any consecutive 5 iterations
**Then** workflow escalates with `error: "oscillation_detected"` and pattern details

**Given** limit is about to be reached (iteration 9 of 10)
**When** the penultimate iteration begins
**Then** warning is logged and user is notified of impending limit

---

### Story 5.11: Brainstorming Workflow Handling

As a **workflow user**,
I want **brainstorming workflows handled appropriately for project tier**,
So that **simple projects get quick ideation while complex projects get thorough exploration**.

**Acceptance Criteria:**

**Given** a Tier 3-4 project requiring brainstorming
**When** brainstorming workflow initiates
**Then** it uses pre-seeding with domain-specific prompts and full Party Mode

**Given** a Tier 0-2 project requiring brainstorming
**When** brainstorming workflow initiates
**Then** it uses simulated ideation instead of full Party Mode

**Given** simulated ideation mode
**When** Subagent Dispatcher configures agents
**Then** it spawns 3-5 subagent personas with diverse perspectives

**Given** simulated ideation completes
**When** results are aggregated
**Then** output format matches full Party Mode for consistency

---

### Story 5.12: Code Review Invocation

As a **workflow user**,
I want **code review automatically invoked after story implementation**,
So that **every story gets quality review without manual triggering**.

**Acceptance Criteria:**

**Given** a story implementation completes (dev-story workflow)
**When** implementation step finishes
**Then** code review workflow is automatically invoked

**Given** code review is invoked
**When** reviewer agent initializes
**Then** it receives: story context, changed files, acceptance criteria, project standards

**Given** code review is configured as optional
**When** the workflow checks configuration
**Then** it respects `skip_review: true` setting with warning logged

---

### Story 5.13: Code Review Verdict Processing

As a **workflow automation system**,
I want **code review verdicts parsed and acted upon appropriately**,
So that **review outcomes drive correct next steps**.

**Acceptance Criteria:**

**Given** code review finds 3-10 specific issues (adversarial requirement)
**When** review completes
**Then** issues are returned with severity, location, and suggested fix

**Given** code review verdict is "Approve"
**When** verdict is processed
**Then** workflow proceeds to next story or completion

**Given** code review verdict is "Changes Requested"
**When** verdict is processed
**Then** fixes are applied automatically and re-review triggered

**Given** code review verdict is "Blocked"
**When** verdict is processed
**Then** workflow escalates to user with blocking issues

**Given** review iteration occurs
**When** iteration count is updated
**Then** `review_iterations` is tracked separately from implementation iterations

**Given** code review uses 19-item checklist
**When** review executes
**Then** all checklist items are evaluated and reported

---

## Epic 6: Parallel Artifact Validation - Stories

### Story 6.1: Concurrent Validation Checks

As a **BMB module user**,
I want **up to 6 validation checks running concurrently**,
So that **agent/workflow validation completes quickly**.

**Acceptance Criteria:**

**Given** a BMB artifact (agent or workflow) ready for validation
**When** Parallel BMB Validation initiates
**Then** it spawns up to 6 validation subagents (08a-08f) concurrently

**Given** 6 subagents are running
**When** validation executes
**Then** all agents run in parallel with independent contexts

**Given** fewer than 6 validation types are needed
**When** validation initiates
**Then** only required validators are spawned (no wasteful spawning)

**Given** validation is running
**When** progress is queried
**Then** status shows which validators are complete, in-progress, and pending

---

### Story 6.2: Synchronization Barrier

As a **workflow automation system**,
I want **a synchronization barrier waiting for all subagents**,
So that **validation results are aggregated only when all validators complete**.

**Acceptance Criteria:**

**Given** 6 validation subagents are running
**When** aggregation is requested
**Then** the barrier waits for all 6 to complete before proceeding

**Given** thread-safe aggregation is required
**When** results are collected
**Then** mutex with 5-second timeout protects individual result aggregation (distinct from NFR5's 120s overall synchronization wait which covers the full barrier duration)

**Given** mutex acquisition times out
**When** the 5s timeout is reached
**Then** exactly one retry is attempted with fresh mutex acquisition before failing with `error: "sync_timeout"` and releasing all held resources

**Given** barrier wait exceeds 120s (NFR5 synchronization wait limit)
**When** the timeout is reached
**Then** barrier aborts with `error: "barrier_timeout"`, any completed results are preserved, and partial failure handling per Story 6.3 is invoked

**Given** all validators complete successfully
**When** the barrier releases
**Then** results are aggregated in consistent order (08a, 08b, ... 08f)

---

### Story 6.3: Partial Failure Handling

As a **BMB module user**,
I want **partial validation failures handled gracefully**,
So that **a single validator failure doesn't abort the entire validation**.

**Acceptance Criteria:**

**Given** 6/6 validators succeed (6 success, 0 failure)
**When** results are evaluated
**Then** validation proceeds to next phase with aggregated results

**Given** 4-5/6 validators succeed (1-2 failures)
**When** results are evaluated
**Then** failed validators are retried sequentially, then results aggregated

**Given** 2-3/6 validators succeed (3-4 failures)
**When** results are evaluated
**Then** all validators are retried, and if still failing, escalation occurs

**Given** 1/6 validators succeed (5 failures)
**When** results are evaluated
**Then** single success is used as context for sequential retry of failed validators

**Given** 0/6 validators succeed (all failures)
**When** results are evaluated
**Then** parallel validation is aborted and full sequential fallback is executed

**Given** sequential fallback completes
**When** results are available
**Then** output format matches parallel validation for consistency

---

### Story 6.4: Artifact Standards Validation

As a **BMB module user**,
I want **generated artifacts validated against BMAD standards**,
So that **agents and workflows are compliant before deployment**.

**Acceptance Criteria:**

**Given** a generated agent artifact
**When** standards validation runs
**Then** it checks: persona definition, critical_actions, menu structure, metadata completeness

**Given** a generated workflow artifact
**When** standards validation runs
**Then** it checks: step structure, frontmatter format, template compliance, path references

**Given** standards validation fails
**When** issues are reported
**Then** each issue includes: field, expected format, actual value, remediation suggestion

**Given** BMB-specific confidence thresholds are configured
**When** validation scoring applies
**Then** it uses BMB thresholds instead of default workflow thresholds

**Given** artifact passes all standards checks
**When** validation completes
**Then** it returns `compliance_score: 100` with `status: "COMPLIANT"`

---

## Epic 7: User Customization & Continuous Learning - Stories

### Story 7.1: Tier Override Methods

As a **workflow user**,
I want **multiple methods to override the default tier behavior**,
So that **I can customize automation depth without changing configuration files**.

**Acceptance Criteria:**

**Given** user says "I want minimal interruptions" (natural language)
**When** the command is processed
**Then** tier behavior shifts toward more automation (fewer checkpoints)

**Given** user says "use tier 3" (explicit tier)
**When** the command is processed
**Then** Tier 3 behavior is applied immediately

**Given** user says "profile: cautious" (profile switch)
**When** the command is processed
**Then** the cautious profile's tier settings are applied

**Given** user adds "[thorough]" inline in a message (inline modifier)
**When** the message is processed
**Then** that specific operation uses thorough/higher-tier behavior

**Given** user specifies specific settings "batch_size: 2"
**When** the command is processed
**Then** only the specified setting is overridden, other tier settings remain

---

### Story 7.2: Override Priority Enforcement

As a **workflow automation system**,
I want **override priority consistently enforced**,
So that **conflicting overrides resolve predictably**.

**Acceptance Criteria:**

**Given** multiple override sources exist (explicit tier + profile + natural language)
**When** override resolution runs
**Then** priority is: explicit tier > profile switch > specific settings > natural language hints

**Given** explicit tier 2 is set, then profile "aggressive" is activated
**When** tier is determined
**Then** explicit tier 2 takes precedence over profile

**Given** an override is applied
**When** session continues
**Then** override persists for the session (not just one operation)

**Given** safety-critical behavior (final approval, stall detection) would be bypassed
**When** override is attempted
**Then** override is rejected with explanation that safety behavior cannot be bypassed

**Given** user attempts to override via "skip final approval"
**When** the command is processed
**Then** it is rejected with `error: "safety_override_blocked"`

---

### Story 7.3: Hook Discovery and Execution

As a **workflow developer**,
I want **hooks discovered from step file frontmatter and executed at appropriate times**,
So that **custom behavior can be injected into workflow steps**.

**Acceptance Criteria:**

**Given** a step file with `hooks.PreToolUse` in frontmatter
**When** the step is about to execute a tool
**Then** the PreToolUse hook is executed first

**Given** a step file with `hooks.PostToolUse` in frontmatter
**When** a tool completes execution
**Then** the PostToolUse hook is executed after

**Given** a step file with `hooks.Stop` in frontmatter
**When** the workflow reaches the step's end
**Then** the Stop hook is executed before transition

**Given** a hook fails and is NOT marked `critical: true`
**When** the failure is detected
**Then** failure is logged and workflow continues

**Given** a hook fails and IS marked `critical: true`
**When** the failure is detected
**Then** workflow is halted with `error: "critical_hook_failed"`

---

### Story 7.4: Hook Output Limits

As a **workflow automation system**,
I want **hook output size limits enforced**,
So that **hooks don't overwhelm context with excessive output**.

**Acceptance Criteria:**

**Given** a hook produces stdout output
**When** stdout exceeds 64KB
**Then** output is truncated at 64KB with `truncated: true` flag

**Given** a hook produces stderr output
**When** stderr exceeds 16KB
**Then** output is truncated at 16KB with warning logged

**Given** a hook's total output (stdout + stderr + metadata)
**When** total exceeds 256KB per step
**Then** oldest output is pruned to stay within limit

**Given** output is truncated
**When** truncation occurs
**Then** message indicates bytes truncated and original size

---

### Story 7.5: SessionStart Hook Handling

As a **workflow developer**,
I want **SessionStart hooks to support one-time initialization**,
So that **expensive setup only runs once per session**.

**Acceptance Criteria:**

**Given** a SessionStart hook with `once: true`
**When** the session starts
**Then** hook executes exactly once

**Given** a SessionStart hook with `once: true` has already executed
**When** another workflow in the same session starts
**Then** hook is skipped (already ran)

**Given** a SessionStart hook without `once: true`
**When** each workflow in the session starts
**Then** hook executes for each workflow

**Given** session ends and restarts
**When** SessionStart hooks are evaluated
**Then** `once: true` hooks run again (new session)

---

### Story 7.6: Menu Rate Limiting

As a **workflow user**,
I want **menu presentations rate-limited**,
So that **I'm not overwhelmed by rapid-fire menu prompts**.

**Acceptance Criteria:**

**Given** a menu is presented
**When** another menu would be presented within 2 seconds
**Then** the second menu is delayed until 2 seconds have elapsed

**Given** 10 consecutive menus have been presented
**When** the 11th menu would be presented
**Then** a forced pause occurs with summary of recent menus

**Given** forced pause is active
**When** user acknowledges
**Then** menu presentation resumes with counter reset

**Given** rate limiting is causing delays
**When** status is queried
**Then** it indicates `rate_limited: true` with `next_available_at` timestamp

---

### Story 7.7: Progress Display Modes

As a **workflow user**,
I want **progress displayed in different modes based on preference**,
So that **I get the right level of detail for my workflow**.

**Acceptance Criteria:**

**Given** progress mode is "Verbose"
**When** operations execute
**Then** each operation shows detailed output immediately

**Given** progress mode is "Summary"
**When** operations execute
**Then** operations batch into periodic summaries (every 5 operations or 30 seconds)

**Given** progress mode is "Silent"
**When** operations execute
**Then** no progress is shown until operation completes with end-of-operation summary

**Given** progress mode is "Streaming" and operation exceeds 30 seconds
**When** the long operation runs
**Then** streaming progress shows current step name and percentage

**Given** user requests progress summary
**When** the request is processed
**Then** response shows completed steps, remaining steps, current step, and estimated progress %

---

### Story 7.8: Explicit Feedback Commands

As a **workflow user**,
I want **explicit feedback commands stored for future reference**,
So that **my preferences are remembered across sessions**.

**Acceptance Criteria:**

**Given** user says "Don't do that again" after an action
**When** the feedback is processed
**Then** the action is stored as negative pattern in Forgetful memory

**Given** user says "Good choice" after an action
**When** the feedback is processed
**Then** the action is stored as positive pattern in Forgetful memory

**Given** user says "Remember this preference: always use thorough validation"
**When** the feedback is processed
**Then** the preference is stored with `type: "explicit_preference"`

**Given** stored feedback exists for a situation
**When** similar situation arises in future
**Then** the stored pattern influences decision (positive patterns preferred, negative avoided)

---

### Story 7.9: Implicit Feedback Detection

As a **workflow automation system**,
I want **implicit feedback detected from user corrections**,
So that **preferences are learned even without explicit feedback**.

**Acceptance Criteria:**

**Given** system makes automatic selection A, then user immediately selects B
**When** the correction is detected
**Then** it is recorded as implicit negative feedback for A, positive for B

**Given** user frequently skips a certain menu option
**When** pattern is detected (3+ skips of same option)
**Then** option is de-prioritized in future presentations

**Given** user consistently accepts system recommendations
**When** pattern is detected (5+ accepts without modification)
**Then** confidence threshold for that decision type is increased

**Given** implicit feedback conflicts with explicit feedback
**When** both exist for same pattern
**Then** explicit feedback takes precedence

**Given** learned preferences exist
**When** preferences are applied
**Then** they are traceable via `decision_source: "learned_preference"` in logs

---

## Story Summary

| Epic | Epic Title | Story Count | FR Coverage |
|------|------------|-------------|-------------|
| 1 | Foundation Validation | 4 | FR13-15, FR40 |
| 2a | Workflow Entry & Detection | 7 | FR1-6, FR31, FR35-39, FR41 |
| 2b | Menu & Automation Core | 12 | FR7-12b, FR16-19j |
| 3 | State & Recovery Management | 7 | FR26-30, FR60-62 |
| 4 | Memory Integration | 3 | FR32-34 |
| 5 | Multi-Agent Orchestration | 13 | FR20-25b, FR42-44b |
| 6 | Parallel Artifact Validation | 4 | FR45-47c |
| 7 | User Customization & Continuous Learning | 9 | FR48-59, FR63-65 |
| **Total** | | **59 stories** | **92 FRs (100%)** |

### Stories by Epic

- **Epic 1:** 1.1, 1.2, 1.3, 1.4
- **Epic 2a:** 2a.1, 2a.2, 2a.3, 2a.4, 2a.5, 2a.6, 2a.7
- **Epic 2b:** 2b.1, 2b.2, 2b.3, 2b.4, 2b.5, 2b.6, 2b.7, 2b.8, 2b.9, 2b.10, 2b.11, 2b.12
- **Epic 3:** 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
- **Epic 4:** 4.1, 4.2, 4.3
- **Epic 5:** 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12, 5.13
- **Epic 6:** 6.1, 6.2, 6.3, 6.4
- **Epic 7:** 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9
