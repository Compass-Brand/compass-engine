---
stepsCompleted: [1, 2, 3, 4, 7, 8, 9, 10, 11]
inputDocuments:
  - docs/plans/2026-01-08-bmad-automation-design.md
  - docs/bmad-workflow-maps.md
  - docs/bmad-agent-inventory.md
  - docs/bmad-architecture-overview.md
workflowType: 'prd'
lastStep: 11
skippedSteps: [5, 6]
documentCounts:
  briefs: 0
  research: 0
  project_docs: 4
---

# Product Requirements Document - BMAD Automation for Claude Code

**Author:** Trevor Leigh
**Date:** 2026-01-09

## Executive Summary

BMAD Automation transforms the manual orchestration overhead of the BMAD V6 framework into an autonomous execution layer for Claude Code. Currently, developers must manually invoke workflows, navigate step files, coordinate multi-agent sessions (Party Mode), and track workflow state across conversation boundaries. This automation layer eliminates that friction.

The system enables Claude Code to detect skill invocations, validate responses, orchestrate multi-agent conversations, manage workflow state machines, and make confidence-based decisions - all with minimal user intervention while respecting task-level oversight requirements defined in the design specification.

### What Makes This Special

- **Hands-free operation**: Workflows execute autonomously without constant user prompting
- **Context efficiency**: Better token utilization means more work completed per dollar spent
- **Consistency**: Deterministic workflow execution eliminates human orchestration errors
- **Speed**: Automated transitions between steps, agents, and phases without wait states
- **Intelligent oversight**: Task-level intervention points rather than step-by-step approval

## Project Classification

**Technical Type:** developer_tool
**Domain:** general
**Complexity:** medium
**Project Context:** Brownfield - extending existing BMAD V6 framework within Claude Code

This PRD defines the automation layer that bridges BMAD's structured methodology with Claude Code's autonomous execution capabilities. The 16-component architecture (10 adapted, 6 new) integrates with existing BMAD patterns while adding state management, recovery paths, and confidence-based decision making.

## Success Criteria

### User Success

- **Minimal interruptions**: Workflows execute with significantly fewer user prompts than manual orchestration
- **Trusted autonomy**: AI makes routine decisions without asking permission at each step
- **Graceful recovery**: When issues occur, automation recovers without user intervention 95% of the time
- **Predictable behavior**: Users can start a workflow and trust it will complete or clearly report why it couldn't

### Business Success

- **3-month milestone**: BMAD workflows run autonomously without constant supervision
- **12-month milestone**: Automation layer integrated into external platform serving other users
- **Key metrics**: Workflows completed per session, time saved per workflow vs manual orchestration

### Technical Success

- **Confidence-based decisions**: 80% threshold for autonomous action, escalate below
- **Timeout enforcement**: Workflow (1800s), nested (300s), agent (60s) timeouts prevent hangs
- **Recovery reliability**: All error paths reach terminal states, no infinite loops
- **Resource limits**: Queue capped at 100 entries, memory managed within bounds

### Measurable Outcomes

| Metric | Current (Manual) | Target (Automated) |
|--------|------------------|-------------------|
| User prompts per workflow | Many (10+) | Few (0-3 for oversight only) |
| Recovery success rate | N/A | 95% |
| Workflow completion rate | Variable | 90%+ |

## Product Scope

### MVP - Minimum Viable Product

All 16 components from design specification:
- 10 adapted components (skill detection, response validation, menu handling, etc.)
- 6 new components (workflow orchestrator, state machine, Party Mode coordinator, etc.)
- Core automation for all BMM workflows

### Growth Features (Post-MVP)

- Platform integration APIs
- Multi-user session management
- Usage analytics and optimization recommendations

### Vision (Future)

- Fully autonomous BMAD across any project type
- Self-improving workflow optimization based on outcomes
- Cross-project learning and pattern reuse

## User Journeys

### Journey 1: Alex Chen - Developer Running Autonomous Workflows

Alex is a senior developer working on a complex SaaS platform. They've been using BMAD workflows for sprint planning and story implementation, but find themselves constantly prompted: "Which agent should handle this?", "Is this step complete?", "Should I proceed to code review?". What should be a 2-hour dev-story workflow takes 4 hours because Alex has to stay engaged the whole time.

One morning, Alex updates to BMAD Automation. They invoke `/bmad:bmm:workflows:dev-story`, select the story, and walk away to grab coffee. When they return, the story is implemented with tests passing and a code review completed. The only notification waiting: "Story DEV-142 complete. 3 files changed, 94% coverage. Review summary attached."

The breakthrough comes during a sprint where Alex completes 8 stories in the time that previously took 3. Their team lead notices the velocity jump. Six months later, Alex's workflow has spread across the engineering org, and they're known as "the person who made BMAD actually autonomous."

### Journey 2: Sam Rivera - Module Installer Setting Up New Projects

Sam is a tech lead starting a new microservices project. They've heard about BMAD but have never set it up. The old way meant reading documentation, manually copying files, configuring paths, and hoping nothing broke. Sam has 30 minutes before a sprint planning meeting.

Sam runs the BMAD installer, answers three questions (project name, preferred modules, output folder), and watches the automation scaffold everything. When they invoke `/bmad:bmm:workflows:workflow-init`, the system detects it's a greenfield Level 3 project and suggests the Method track. No manual classification needed.

The real magic happens when Sam's teammate joins the project a week later. Instead of a 2-hour onboarding session, Sam says "just pull main and run `/bmad:bmm:workflows:workflow-status`" - the automation shows exactly where the project is and what workflow comes next.

### Journey 3: Jordan Park - Workflow Author Creating Custom Automation

Jordan is a DevOps engineer whose team has a unique deployment process that doesn't fit standard BMAD workflows. They need a custom "deploy-to-staging" workflow that runs security scans, builds containers, and coordinates with their CD pipeline.

Previously, creating a custom workflow meant studying BMAD's internal structure, manually creating step files, and hoping the format was correct. Jordan tried once and gave up after 3 hours of debugging YAML syntax.

With BMAD Automation, Jordan invokes `/bmad:bmb:workflows:create-workflow` and describes what they need conversationally. The Workflow Builder agent asks clarifying questions, generates the step files, and validates the structure automatically. When Jordan runs their new workflow for the first time, it executes autonomously - no manual orchestration required because it inherits the automation layer.

Three months later, Jordan has published five custom workflows to their organization's internal BMAD registry. They've become the go-to person for "if you can describe it, I can automate it."

### Journey Requirements Summary

| Journey | Capabilities Required |
|---------|----------------------|
| Developer (Alex) | Skill detection, autonomous workflow execution, state persistence, code review automation, progress reporting |
| Module Installer (Sam) | Project detection, automatic classification, module scaffolding, status tracking, team onboarding |
| Workflow Author (Jordan) | BMB integration, workflow validation, automation inheritance, conversational workflow creation |

## Developer Tool Specific Requirements

### Project-Type Overview

BMAD Automation is an internal Claude Code extension for a single user. It enhances the existing BMAD V6 installation with autonomous workflow execution capabilities. No external distribution, API surface, or multi-platform support required.

### Technical Architecture Considerations

**Platform:** Claude Code only (no VS Code, CLI, or other IDE support planned)

**Installation:** Leverages existing BMAD installation pattern (`_bmad/` folder structure). Automation components integrate as additional skills and configuration.

**Interface:** Skill invocations via `/bmad:*` slash commands - no programmatic API needed for internal use.

**Dependencies:**
- Existing BMAD V6 modules (Core, BMM, BMB)
- Claude Code skill system
- Existing MCP server integrations (Forgetful, Serena, etc.)

### Documentation Requirements

- Internal README covering automation behavior and configuration
- Troubleshooting guide for common failure scenarios
- Configuration reference for thresholds and timeouts

### Implementation Considerations

**Simplified scope due to internal use:**
- No backwards compatibility concerns
- No migration guide needed (fresh implementation)
- No API versioning required
- Direct iteration based on personal workflow needs
- Documentation can be minimal and living

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Foundation MVP - implement all 16 components per design specification
**Resource Requirements:** Single developer (you), iterating based on personal use

Since this is internal tooling with a complete design specification, the design document IS the scoping decision. No market validation or early adopter concerns - the goal is autonomous BMAD execution.

### Implementation Phases (from Design Specification)

#### Phase 1: Foundation (Tier 1 - No Dependencies)

Components that can start immediately:
- **Validation Type Detector** - Workflow-specific awareness for verdict-based success
- **Pre-flight Validation Subagent** - Config validation before workflow start
- **Cross-Reference Validator** - Document alignment checks

*Rationale: These have no dependencies and provide immediate value.*

#### Phase 2: Core Engine (Tiers 2-3)

Entry points and core automation:
- **Workflow Entry Wrapper** - workflow-init integration (depends on Validation Type Detector)
- **Menu Participation Engine** - [A][P][C] handling with BMB thresholds (depends on Validation Type Detector)
- **Context Pre-Loader** - Forgetful memory pre-population (standalone)
- **Automation Controller** - Verdict-based loop logic (depends on Menu Participation Engine)
- **Confidence Calculator** - 80% threshold for autonomous decisions (uses validator outputs)
- **Tier Suggester** - Smart tier suggestions (depends on Workflow Entry Wrapper)

*Rationale: Core engine that enables autonomous workflow execution.*

#### Phase 3: Specialized Handlers (Tier 4)

Advanced automation capabilities:
- **Party Mode Driver** - Programmatic per-round inputs (depends on Automation Controller)
- **Loop-Back Handler** - Edit-Module iteration tracking (depends on Automation Controller)
- **Subagent Dispatcher** - Agent pool management (depends on Automation Controller)
- **Memory Bridge** - Forgetful integration (depends on Context Pre-Loader)

*Rationale: Enables multi-agent coordination and memory persistence.*

#### Phase 4: Integration (Tier 5)

Full system integration:
- **Parallel BMB Validation** - 6x parallel validation (depends on Subagent Dispatcher)
- **Sprint Status Watcher** - Background file monitoring (depends on Automation Controller)
- **Post-Workflow Curator** - Automated memory extraction (depends on Memory Bridge)

*Rationale: Polish and optimization for production use.*

### Component Summary

| Phase | Components | Dependencies |
|-------|------------|--------------|
| 1: Foundation | 3 | None |
| 2: Core Engine | 6 | Phase 1 |
| 3: Specialized | 4 | Phase 2 |
| 4: Integration | 3 | Phases 2-3 |
| **Total** | **16** | |

### Risk Mitigation Strategy

**Technical Risks:**
- Complex state management → Explicit initialization/shutdown sequences defined in design
- MCP unavailability → Graceful degradation built into design (continue without Forgetful)
- Timeout handling → Hierarchy defined (1800s/300s/60s)

**Implementation Risks:**
- Component interdependencies → Follow dependency tiers strictly
- Regression during iteration → TDD approach (tests before implementation)

**Resource Risks:**
- Single developer → Phased approach allows incremental value delivery
- Context limits → Subagent patterns isolate heavy operations

## Functional Requirements

### Workflow Automation

- FR1: Automation Controller can detect skill invocations matching `/bmad:*` patterns and initiate workflow execution
- FR2: Automation Controller can execute workflows autonomously without user prompts at each step
- FR3: Automation Controller can transition between workflow steps based on verdict-based success criteria
- FR4: Workflow Entry Wrapper can detect project type (greenfield/brownfield) by checking for existing source directories (src/, lib/, app/), package files (package.json, pyproject.toml), and substantial code (>10 source files)
- FR5: Tier Suggester can recommend project level (0-4) based on user description and codebase analysis
- FR6: Automation Controller can respect task-level oversight requirements defined in workflow configuration

### Menu Participation

- FR7: Menu Participation Engine can detect menus using confidence scoring (>= 70 points threshold) with structural markers, position validation, and false positive guards (reject patterns inside code blocks, blockquotes, or example content)
- FR8: Menu Participation Engine can automatically select appropriate menu options based on confidence thresholds
- FR9: Menu Participation Engine can apply BMB-specific thresholds: trigger Party Mode when `blocking_errors > 3` OR `major_issues > 5`; trigger Advanced Elicitation when `compliance_score < 70`
- FR10: Menu Participation Engine can escalate to user when confidence is below 80% threshold
- FR11: Menu Participation Engine can handle nested menu selections within Party Mode or Advanced Elicitation
- FR12: Menu Participation Engine can track menu selection history for recovery purposes
- FR12a: Menu Participation Engine can implement batch-continue logic with tier-based batch sizes (Level 0-1: auto-all, Level 2: up to 5, Level 3: up to 3, Level 4: 1-2)
- FR12b: Automation Controller can present human checkpoints in three formats: Minimal (>=80% confidence), Summary (50-80%), Full Audit Trail (<50%)

### Validation & Recovery

- FR13: Validation Type Detector can identify workflow-specific success criteria (verdict-based, error-based, or checklist-based)
- FR14: Pre-flight Validation Subagent can verify required configuration before workflow start
- FR15: Cross-Reference Validator can check document alignment across workflow outputs
- FR16: Automation Controller can recover from validation failures without user intervention
- FR17: Automation Controller can enforce timeout hierarchy (1800s workflow, 300s nested, 60s agent)
- FR18: Automation Controller can reach terminal states for all error paths without infinite loops
- FR19: Confidence Calculator can compute confidence scores from validator outputs
- FR19a: Automation Controller can detect validation stalls using SHA-256 hash-based issue set comparison
- FR19b: Automation Controller triggers Party Mode escalation when stall detected AND attempts >= 2
- FR19c: Automation Controller tracks failed Party Mode hashes to prevent stall→party→fail loops
- FR19d: Automation Controller applies memory-first fix strategy with multi-approach fallback
- FR19e: Confidence Calculator uses 4 signal sources: Validation Verdict (0-35pts), Memory Match (0-25pts), Reviewer Agreement (0-25pts), Party Mode Outcome (0-15pts) (optional 5th signal: model selection 0-10pts)
- FR19f: Confidence Calculator applies tier adjustment and returns score 0-100 with threshold classification
- FR19g: Confidence Calculator defaults to 25% when no signals available
- FR19h: Confidence Calculator caps single-source confidence at 60% maximum
- FR19i: Confidence Calculator handles conflicting signals by weighting higher-priority sources
- FR19j: Confidence Calculator falls back to 30% on calculation failures

### Multi-Agent Coordination

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

### State Management

- FR26: Automation Controller can persist workflow state across conversation boundaries
- FR27: Automation Controller can resume workflows from last completed step after interruption
- FR28: Sprint Status Watcher can monitor workflow status files with 500ms debounce, 30s deduplication window, dual compare-and-swap for race prevention, and status cycling detection
- FR29: Automation Controller can manage queue of pending workflow tasks (capped at 100 entries)
- FR30: Automation Controller can track completion status of all workflow steps

### Memory Integration

- FR31: Context Pre-Loader can query Forgetful memory for relevant context before workflow start
- FR32: Memory Bridge can write workflow decisions and outcomes to Forgetful memory
- FR33: Post-Workflow Curator can extract key learnings and create atomic memories: architectural decisions (importance 9-10), implementation patterns (7-8), problem-solution pairs (7-8), milestone completions (6-7)
- FR34: Memory Bridge can gracefully degrade when Forgetful MCP is unavailable
- FR35: Context Pre-Loader can pre-populate agent context with relevant memories

### Configuration & Adaptation

- FR36: Automation Controller can read configuration from workflow YAML/MD frontmatter
- FR37: Automation Controller can apply module-specific settings (Core, BMM, BMB)
- FR38: Confidence Calculator can use configurable thresholds per workflow type
- FR39: Automation Controller can adapt behavior based on project classification (type, domain, complexity)
- FR40: Validation Type Detector can recognize custom workflow validation patterns
- FR41: Automation Controller can support both YAML and Markdown workflow formats

### Code Review Integration

- FR42: Automation Controller can invoke code review workflow after story implementation
- FR43: Automation Controller can parse code review verdicts and determine next action
- FR44: Automation Controller can track review iteration count and outcomes
- FR44a: Code Review is ADVERSARIAL - must find 3-10 specific issues per story using 19-item checklist
- FR44b: Code Review outcomes are Approve (issues addressed), Changes Requested (apply fixes, re-review), or Blocked (escalate)

### BMB Module Support

- FR45: Parallel BMB Validation can run up to 6 validation checks concurrently
- FR46: Automation Controller can orchestrate agent creation workflows with BMB-specific confidence thresholds
- FR47: Automation Controller can validate generated workflow/agent artifacts against BMAD standards
- FR47a: Parallel BMB Validation implements synchronization barrier waiting for all 6 subagents (08a-08f)
- FR47b: Parallel BMB Validation uses thread-safe aggregation with mutex (5s timeout, retry once)
- FR47c: Parallel BMB Validation applies partial failure handling: 6/0 success → proceed; 4-5/1-2 → retry failed sequentially; 2-3/3-4 → retry all + escalate if still failing; 1/5 → use single success as context for sequential retry; 0/6 → abort parallel, fall back to full sequential

### Tier Override & Configuration

- FR48: Automation Controller supports tier override methods: natural language, explicit tier, specific settings, profile switch, inline modifier
- FR49: Automation Controller applies override priority: explicit tier > profile switch > specific settings > natural language hints
- FR50: Overrides persist for session but never bypass safety-critical behavior (final approval, stall detection)

### Lifecycle & Hooks

- FR51: Automation Controller discovers and executes hooks from step file frontmatter (PreToolUse, PostToolUse, Stop)
- FR52: Hooks have output size limits: 64KB stdout, 16KB stderr, 256KB total per step
- FR53: Hook failures are logged and continued unless marked `critical: true`
- FR54: SessionStart hooks support `once: true` for one-time initialization

### Rate Limiting & Presentation

- FR55: Menu Participation Engine can throttle menu presentations with minimum 2-second intervals between presentations
- FR56: Menu Participation Engine can force pause after 10 consecutive menus to prevent fatigue
- FR57: Automation Controller can batch silent progress into summaries (Verbose/Summary/Silent/Streaming modes)
- FR58: Automation Controller can display streaming progress for long operations (>30s) showing current step name and percentage
- FR59: Automation Controller can provide progress summary on user request showing completed/remaining steps

### Rollback & Recovery

- FR60: Automation Controller can create checkpoints at key workflow points (before step transitions, before validation fixes)
- FR61: Automation Controller can rollback to previous checkpoint on user request ("undo", "rollback to step N")
- FR62: Checkpoint data persisted to frontmatter includes: step_id, timestamp, state_snapshot, can_rollback flag

### Feedback & Learning

- FR63: Automation Controller can accept explicit feedback commands ("Don't do that again", "Good choice", "Remember this preference")
- FR64: Automation Controller can store positive/negative patterns in Forgetful memory for future reference
- FR65: Automation Controller can detect implicit feedback from user corrections and store learned preferences

## Non-Functional Requirements

### Performance

- **Timeout Enforcement**: Workflow timeouts (1800s), nested operation timeouts (300s), and agent timeouts (60s) must be enforced to prevent hangs
- **Response Expectations**: Menu selections and step transitions should complete within 5 seconds under normal conditions
- **Context Efficiency**: Automation should reduce token usage compared to manual orchestration through intelligent context management
- **Queue Processing**: Task queue operations (add, remove, prioritize) must complete within 100ms
- **Extended Timeout Hierarchy**: Party mode round (120s), background watcher poll (5s interval), exit grace period (500ms), synchronization wait (120s), human selection timeout (300s)

### Reliability

- **Recovery Rate**: 95% of recoverable errors should resolve without user intervention
- **State Persistence**: Workflow state must survive conversation boundaries and be resumable
- **Terminal States**: All error paths must reach terminal states (no infinite loops or hangs)
- **Graceful Degradation**: System must continue operating when optional dependencies (Forgetful MCP) are unavailable
- **Graceful Degradation Details**: When Forgetful unavailable: 3 retries at 100ms intervals, queue to local file (`_bmad-output/.memory-queue/`), max 100 queued entries with FIFO overflow, 5-minute cache TTL, PERMANENTLY_UNAVAILABLE after 4 hours
- **Idempotency**: Repeated execution of the same workflow step should produce consistent results

### Integration

- **MCP Compatibility**: Must work with Forgetful MCP and Serena MCP when available
- **Skill System**: Must integrate cleanly with Claude Code's existing skill invocation mechanism
- **BMAD Compatibility**: Must work with existing BMAD V6 module structure without modifications to source workflows
- **File System**: Must read/write workflow state and output files reliably to configured paths

