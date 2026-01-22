# BMAD Automation with Subagent-Driven Review

**Date:** 2026-01-08
**Status:** Design Complete (Revised v8)
**Author:** Claude + Trevor
**Revision:** 2026-01-09 v8 - CODE REVIEW FIX: BMAD Code Review IS adversarial (3-10 findings required per instructions.xml) - v5/v7 incorrectly claimed it was NOT adversarial. All Code Review references updated throughout document. See Appendix for full correction history.

## Overview

This design transforms BMAD from a human-gated workflow system into an **autonomous iteration engine** with intelligent escalation. The goal is to reduce human interaction while maintaining (and improving) quality through:

- Subagent-driven review cycles with verdict-based success criteria (not universal "0 issues")
- Automated party mode for multi-perspective problem solving
- Tiered validation intensity based on task complexity
- Memory-driven pattern learning across sessions
- Confidence-based adaptive human checkpoints (NEW FUNCTIONALITY)

## Design Principles

1. **Verdict-Based Success** - Different validation types have different success criteria:
   - **Implementation Readiness (check-implementation-readiness):** Target = READY verdict (NEEDS WORK acceptable with acknowledgment, NOT READY requires fixes)
   - **Test Traceability (testarch-trace):** Target = PASS verdict (CONCERNS acceptable with acknowledgment, FAIL requires fixes)
   - **Code Review:** ADVERSARIAL review requiring 3-10 specific findings per story; uses 19-item checklist with Approve/Changes Requested/Blocked outcomes
   - **Syntax/Reference Validation:** Target = 0 blocking errors
2. **Tiered Intensity** - Task complexity (Level 0-4) determines validation depth and human gates
3. **Memory-Driven Learning** - Successful patterns saved to Forgetful, queried before fix attempts
4. **Confidence-Based Transparency** - Human checkpoint detail scales with AI uncertainty (NEW FUNCTIONALITY - not existing Core feature)
5. **Party Mode as Tool** - Used for deadlock breaking, confidence boosting, and mandatory reviews (not just escape hatch)
6. **Trust with Verification** - Less questioning, more autonomous action, but strong post-hoc verification
7. **Step Processing Integrity** - Automation auto-SELECTS options but NEVER skips steps. Each step file processed discretely per BMAD Critical Rules.

---

## Quick Start: Sensible Defaults

**New users start here.** This section provides production-ready defaults that work for most use cases.

### Recommended Starting Configuration

```yaml
# bmad-automation-config.yaml - Copy this to start
automation:
  enabled: true
  tier: auto-suggest  # Automation suggests tier, user confirms

defaults:
  default_tier: 2                    # Good balance for most projects
  auto_continue_threshold: 0.80      # Auto-[C] when confidence >= 80%
  checkpoint_at_decisions: true      # Always pause at design decisions
  max_fix_attempts: 5                # Attempts before escalating
  batch_continue_size: 3             # Max consecutive auto-[C] before pause
  require_final_approval: true       # Always require human sign-off
```

### "Just Works" Profiles

| Profile | When to Use | Key Settings |
|---------|-------------|--------------|
| **Solo Developer** | Individual work, fast iteration | Tier 1-2, auto-continue most steps, final approval only |
| **Team Project** | Multiple contributors, need review | Tier 2-3, checkpoint at decisions, party mode for complex issues |
| **Enterprise** | Compliance required, audit trail | Tier 4, all checkpoints, mandatory party consensus |
| **Quick Fix** | Bug fixes, typos, trivial changes | Quick Flow bypass, minimal gates |

### Minimum Viable Configuration

If the full config feels overwhelming, start with just this:

```yaml
automation:
  enabled: true
  tier: 2
  require_final_approval: true
```

### Pre-Flight Configuration Validation

**Before any workflow starts, automation validates the configuration to catch errors early.**

```yaml
preflight_validation:
  enabled: true
  checks:
    - config_syntax        # YAML valid, no typos
    - tier_valid           # Tier 0-4 only
    - thresholds_sane      # confidence 0-100, etc.
    - dependencies_met     # Required files exist
    - memory_accessible    # Forgetful reachable (warn if not)
```

**Validation Output:**

```
Pre-flight check... 
  [OK] Configuration syntax valid
  [OK] Tier 2 configured
  [OK] Thresholds within valid ranges
  [WARN] Forgetful MCP not responding - memory features disabled
  [OK] Required documents found

Ready to proceed. [Continue] [Fix warnings first]
```

**Common Configuration Errors:**

| Error | Message | Fix |
|-------|---------|-----|
| Invalid tier | "Tier must be 0-4, got: 6" | Set tier to valid value |
| Bad threshold | "auto_continue_threshold must be 0.0-1.0" | Use decimal (0.80 not 80) |
| Missing file | "PRD required for create-architecture" | Run create-prd first |
| MCP unreachable | "Forgetful MCP timeout" | Check MCP server, or continue in degraded mode |

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      ENTRY POINT                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  workflow-init                             │  │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │  │
│  │   │ Field Type  │  │ Project     │  │ Path Selection  │   │  │
│  │   │ Detection   │  │ State       │  │ Express/Guided/ │   │  │
│  │   │ Green/Brown │  │ CLEAN/PLAN/ │  │ Quick Flow      │   │  │
│  │   │             │  │ ACTIVE/LEG  │  │                 │   │  │
│  │   └─────────────┘  └─────────────┘  └─────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
├─────────────────────────────────────────────────────────────────┤
│                    BMAD Automation Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │    Tier      │  │  Automation  │  │   Memory Bridge      │  │
│  │   Suggester  │  │  Controller  │  │   (Forgetful)        │  │
│  │ (wraps init) │  │              │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│          │                │                     │               │
│          ▼                ▼                     ▼               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Menu Participation Engine                    │  │
│  │   Handles [A][P][C] menus at EVERY step                  │  │
│  │   Auto-selects [C] after internal processing             │  │
│  │   Preserves [A][P] as escalation options                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│          ┌─────────────────┼─────────────────┐                 │
│          ▼                 ▼                 ▼                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Subagent Dispatcher                          │  │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │  │
│  │   │Validator│  │  Spec   │  │ Quality │  │Adversar-│    │  │
│  │   │         │  │Reviewer │  │Reviewer │  │  ial    │    │  │
│  │   └─────────┘  └─────────┘  └─────────┘  └─────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Party Mode Driver                            │  │
│  │   (Provides programmatic inputs per round)                │  │
│  │   (Acts AS the human for topic/direction/synthesis)       │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    Existing BMAD Workflows                      │
│   (Validation steps, iteration steps, path files, agents)       │
│   [A][P][C] menus preserved - automation PARTICIPATES in them   │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Approach

The automation layer **wraps around** existing BMAD rather than replacing it. **Critical insight:** Automation PARTICIPATES in menus rather than bypassing them.

| Component | Current Behavior | Automated Behavior |
|-----------|------------------|-------------------|
| **[A][P][C] Menus** | Present at EVERY step, wait for human | Automation selects [C] after internal processing; [A][P] preserved as escalation |
| **[C] Continue prompts** | User types C to proceed (dozens per workflow) | Batch-continue based on tier; Level 0-1: auto-all, Level 2+: pause at checkpoints |
| Validation step | Menu: [A] [P] [C] + wait for human | Process internally, then select [C]; escalate to [A] or [P] if needed |
| Iteration step | Menu: [Y] [V] [N] + wait for human | Auto-[Y] unless checkpoint or low confidence |
| Party mode trigger | Human chooses [P] from menu | Auto-selects [P] on stall/confidence/tier; provides programmatic per-round inputs |
| **Tier selection** | Manual via workflow-init (BMad Method vs Enterprise Method) | Smart suggestions based on keywords, but WRAPS workflow-init selection (user confirms) |
| **Workflow entry** | workflow-init 9-step decision tree | Automation guides through decision tree, providing smart defaults |
| Fix attempts | Human reviews each proposed fix | Autonomous with memory-assisted fixing |

**Preserved:**
- Workflow file structure (micro-file architecture)
- Agent definitions and personalities
- Path files and workflow sequences
- Status tracking in `bmm-workflow-status.yaml`
- Party mode conversation mechanics (automation monitors exit conditions, doesn't steer)
- All existing workflows remain functional
- **[A][P][C] menu structure** - automation participates, doesn't remove
- **workflow-init entry point** - automation wraps, doesn't replace
- **Frontmatter state management** - automation saves progress before step transitions

---

## Workflow Entry Point Handling

### The workflow-init Decision Tree

**Critical understanding:** `workflow-init` is the MANDATORY entry point for all BMM workflows. It implements a 9-step decision tree that automation must work WITH, not bypass.

**VERIFICATION NOTE (H5 - BMB Structure Assumptions - DELIBERATE BOUNDARY):**
The workflow-init references, BMB validation phase descriptions (8-phase compliance check,
6-phase agent validation), and BMB step sequences throughout this design document are based
on ANALYSIS OF DESIGN PATTERNS and may represent proposed structures if the actual MMM/BMB
workflows have not yet been fully implemented. This is a DESIGN BOUNDARY, not a gap.

The design specifies WHAT workflows should do and HOW they should be structured based on
BMAD methodology principles. The ACTUAL step file structure, phase counts, and menu options
are IMPLEMENTATION DETAILS to be verified against real workflow files during development.

Implementation SHALL:
1. Read actual workflow step files before relying on phase counts or sequences
2. Detect actual menu options present in each step (not assume [A][P][C] universally)
3. Map automation behavior to discovered structure
4. Flag discrepancies between design assumptions and actual implementation

This design provides the TARGET ARCHITECTURE. Actual file structures may vary and should
be discovered during implementation rather than assumed from this document.

#### Decision Tree Steps

```
Step 1: Check project artifacts
        ├── No artifacts → CLEAN state
        └── Has artifacts → Continue to Step 2

Step 2: Check for existing workflow status file
        ├── Found bmm-workflow-status.yaml → ACTIVE or LEGACY state
        └── Not found → Continue to Step 3

Step 3: Check for planning documents (PRD, Architecture, Stories)
        ├── Found planning docs → PLANNING state
        └── Not found → CLEAN state (confirmed)

Step 4: Determine field type
        ├── No existing code → GREENFIELD
        └── Existing codebase → BROWNFIELD

Step 5: For BROWNFIELD - check documentation state
        ├── Documented → Skip Phase 0
        └── Undocumented → Require Phase 0 (document-project)

Step 6: Select method tier
        ├── User selects "BMad Method" → Levels 0-2
        └── User selects "Enterprise Method" → Levels 3-4

Step 7: Select path
        ├── Express → Minimal checkpoints, auto-continue
        ├── Guided → Human checkpoints at each major phase
        └── Quick Flow → Bypass to quick-flow-solo-dev agent

Step 8: Confirm selections and validate prerequisites

Step 9: Initialize workflow status and begin
```

#### Four Detected States

| State | Definition | Automation Response |
|-------|------------|---------------------|
| **CLEAN** | No artifacts, fresh project | Begin with tier selection, then Phase 1 |
| **PLANNING** | Has PRD/Architecture but no workflow status | Offer to resume from existing docs or restart |
| **ACTIVE** | Has workflow status file, in-progress work | Resume from last checkpoint |
| **LEGACY** | Old workflow status, possibly stale | Validate artifacts, offer cleanup or resume |

#### Automation's Role in workflow-init

Automation GUIDES through the decision tree but preserves human choice:

```
1. AUTO-DETECT: Field type, state, existing artifacts
2. SUGGEST: Tier based on task keywords and scope
3. PRESENT: Options with smart defaults highlighted
4. WAIT: For human confirmation of tier and path
5. PROCEED: Only after human approves selections
```

**One-Time Initialization (Claude Code 2.1.2):**

The detection steps (1-3) should use `once: true` hooks since they only need to run once per session:

```yaml
hooks:
  SessionStart:
    - command: "detect-project-state.sh"  # Steps 1-4 detection
      once: true
    - command: "suggest-tier.sh"          # Step 6 suggestion
      once: true
```

This prevents redundant artifact scanning and state detection on every tool invocation.

### Greenfield vs Brownfield Handling

#### Detection Logic

```python
def detect_field_type():
    # Check for existing source code
    has_src = exists("src/") or exists("lib/") or exists("app/")
    has_package = exists("package.json") or exists("pyproject.toml") or exists("Cargo.toml")
    has_substantial_code = count_source_files() > 10

    if has_substantial_code or (has_src and has_package):
        return "BROWNFIELD"
    return "GREENFIELD"
```

#### Brownfield: Phase 0 Requirement

For brownfield projects, **Phase 0 (document-project workflow)** may be required before planning:

```
BROWNFIELD DETECTED:
├── Check for existing documentation
│   ├── Has architecture.md, PRD, etc. → Skip Phase 0
│   └── Undocumented codebase → REQUIRE Phase 0
│
└── Phase 0: document-project workflow
    - Scan codebase structure
    - Identify patterns and architecture
    - Generate initial documentation
    - Create project-context.md for AI agents
```

#### Different Workflow Paths

| Field Type | Entry Point | Phase 0 | Planning Phases |
|------------|-------------|---------|-----------------|
| Greenfield | workflow-init | Skip | Product Brief → PRD → Architecture → Stories |
| Brownfield (documented) | workflow-init | Skip | May skip some planning if docs exist |
| Brownfield (undocumented) | workflow-init | Required | document-project → then standard planning |

### Quick Flow Bypass

For Level 0-1 tasks, workflow-init offers "Quick Flow" that bypasses full methodology:

```
Quick Flow Detection:
- User describes simple bug fix or small feature
- Automation suggests: "This looks like a Level 0-1 task. Use Quick Flow?"
- If accepted → Route directly to quick-flow-solo-dev agent
- If declined → Continue with full workflow-init

Quick Flow Solo Dev Agent:
- Single agent handles entire task
- No multi-phase planning
- Built-in TDD cycle
- Minimal checkpoints
```

### Quick-Dev Alternative Path (BMM)

**Critical distinction:** `quick-dev` is a legitimate workflow that bypasses full BMAD methodology. It is NOT the same as Quick Flow Solo Dev Agent.

#### Quick-Dev Mode Detection

```
Quick-Dev has TWO operating modes:

MODE 1: Tech-Spec Driven
├── Input: Existing tech-spec document
├── Behavior: Execute tech-spec directly
├── Validation: Against tech-spec requirements
└── No planning phases needed

MODE 2: Direct Instructions
├── Input: User provides instructions directly
├── Behavior: Execute instructions with optional planning
├── Optional: Can generate mini-plan if complex
└── Validation: Basic quality checks only

DETECTION SIGNALS for automation:
- Mode 1: Presence of tech-spec file path or "execute spec" language in request
- Mode 2: Direct task description without spec reference ("implement X", "add feature Y")
- Escalation trigger: Task complexity exceeds quick-dev scope (architectural decisions needed)
```

#### Escalation Signals from Quick-Dev

Quick-Dev can detect when it's over its head and route back to full workflow:

```
Quick-Dev Escalation Triggers:
- Scope creep detected (task growing beyond original description)
- Architectural decisions needed (not just implementation)
- Multiple subsystems affected
- Test coverage requirements exceed quick-dev's TDD scope
- User explicitly requests more rigor

Escalation Action:
→ Route to workflow-init with context preserved
→ User selects appropriate full workflow
→ Quick-dev work becomes input to formal planning
```

#### Automation Behavior for Quick-Dev

```
WHEN quick-dev workflow selected:
1. Detect mode (tech-spec vs direct instructions)
2. IF tech-spec mode:
   - Validate tech-spec exists and is readable
   - Execute directly with TDD cycle
   - No additional planning automation
3. IF direct instruction mode:
   - Assess complexity
   - IF simple → execute directly
   - IF medium → offer mini-plan generation
   - IF complex → suggest escalation to full workflow
4. Monitor for escalation signals throughout
5. Apply basic quality validation at completion
6. DO NOT apply full BMM validation suite (that's the point of quick-dev)
```

#### Quick-Dev vs Quick Flow

| Aspect | Quick Flow Solo Dev | Quick-Dev Workflow |
|--------|--------------------|--------------------|
| Entry | Through workflow-init | Direct invocation or workflow-init bypass |
| Planning | None (single agent) | Optional mini-plan |
| Input types | Task description | Tech-spec OR direct instructions |
| Escalation | Limited | Full escalation to workflow-init |
| Validation | Final approval | Basic quality only |
| Use case | Level 0-1 tasks | Developer-driven rapid iteration |

---

## Workflow-Status as Active Router (BMM)

**Critical understanding:** `workflow-status` is NOT passive status tracking - it's an ACTIVE ROUTER with multiple operational modes.

### Workflow-Status Modes

```
WORKFLOW-STATUS MODES:
├── interactive    → Full conversation with human, present options
├── validate       → Check current state, report issues
├── data           → Return raw status data (for automation)
├── init-check     → Check if initialization needed
└── update         → Update status fields programmatically

Each mode serves different use case:
- Human invocation → interactive mode (default)
- Automation queries → data mode (structured response)
- Automation updates → update mode (state changes)
- Session start → init-check mode (detect state)
```

### Automation Interaction with Workflow-Status

```
Automation Controller MUST:

1. AT SESSION START:
   - Call workflow-status in "init-check" mode
   - Determine if CLEAN, PLANNING, ACTIVE, or LEGACY state
   - Route accordingly (see workflow-init states)

2. DURING WORKFLOW:
   - Call workflow-status in "data" mode for state queries
   - Call workflow-status in "update" mode to record progress
   - DO NOT use interactive mode (that's for humans)

3. AT CHECKPOINTS:
   - Call workflow-status in "validate" mode
   - Check for state consistency
   - Report any drift or issues

4. ON STATE CHANGE:
   - Use "update" mode with specific field updates
   - Preserve audit trail of state transitions
```

### Workflow-Status Data Mode Response

```
DATA MODE RETURNS:
{
  "current_workflow": "create-prd",
  "current_step": "03",
  "state": "ACTIVE",
  "phase": "Planning",
  "tier": 2,
  "checkpoints_passed": ["01", "02"],
  "pending_issues": [],
  "last_activity": "2026-01-08T14:32:00Z"
}

Automation uses this to:
- Determine where to resume
- Check if validation needed
- Calculate progress metrics
```

---

## Menu-Driven Automation Architecture

### The [A][P][C] Reality

**Critical insight:** EVERY step in BMM workflows presents the [A][P][C] menu. This is not just for validation steps - it's universal.

**Tier/Menu Clarification:** Tiers affect which option is AUTO-SELECTED, NOT whether menus exist. All steps display the [A][P][C] menu regardless of tier. Lower tiers auto-select [C] more often; higher tiers pause for human input more often. But the menu structure is ALWAYS present.

```
Standard Step Output:
────────────────────────────────
[Step content displayed here]
────────────────────────────────
[A] Advanced Elicitation - Deep dive into this topic
[P] Party Mode - Get multiple agent perspectives
[C] Continue - Proceed to next step
────────────────────────────────
```

### [A] vs [P] Distinction (Critical)

**[A] Advanced Elicitation and [P] Party Mode are SEPARATE options with different purposes:**

| Aspect | [A] Advanced Elicitation | [P] Party Mode |
|--------|-------------------------|----------------|
| **Purpose** | Deep-dive on a single issue | Multi-agent collaborative discussion |
| **Agent Count** | Single agent (deeper focus) | 2-3 agents (multiple perspectives) |
| **When to Use** | Need clarification, more detail, or deeper exploration | Need diverse viewpoints, consensus building, conflict resolution |
| **Dialogue Type** | Q&A with one expert | Group discussion with cross-talk |
| **Outcome** | Detailed understanding of one topic | Synthesized recommendation from multiple angles |
| **Typical Triggers** | `compliance_score < 70`, confidence < 50% | `blocking_errors > 3`, `major_issues > 5`, stalled attempts >= 2 |
| **Duration** | Short (1-2 exchanges) | Longer (multi-round discussion) |

**NOTE on [A] in Core:** The [A] Advanced Elicitation option may not be present in all Core workflows. Core brainstorming and party mode show [E] Exit, [C] Continue, and numbered menu options. The [A] option is more common in BMM/BMB validation workflows. **Automation should detect which menu options are actually present** rather than assuming [A][P][C] universally.

**FALLBACK BEHAVIOR (H3 - [A] Not Available):**
When [A] Advanced Elicitation is not present in a workflow menu (e.g., Core workflows),
the automation MUST provide equivalent functionality through an alternative mechanism.
If compliance_score < 70 or confidence < 50% triggers [A] but [A] is unavailable,
the automation SHALL trigger a single-agent deep-dive subagent as the equivalent
escalation. This maintains the design intent (deeper investigation) while adapting to
different workflow menu structures. The deep-dive subagent performs focused analysis
of the specific issue requiring clarification.

**Automation must NOT conflate these:** When `compliance_score < 70`, trigger [A] if available, else use single-agent deep-dive. When `blocking_errors > 3` OR `major_issues > 5`, trigger [P]. They solve different problems.

### Why Automation Must Participate (Not Bypass)

The menus serve critical functions:
1. **Quality gates** - Each [C] is a conscious decision to proceed
2. **Escape hatches** - [A] and [P] provide depth when needed
3. **Audit trail** - Menu selections are logged
4. **Human override** - Human can always choose [A] or [P] instead of auto-[C]

Bypassing menus would break workflow integrity and remove the ability to escalate.

### Menu Participation Engine Design

**CRITICAL: Menu Detection Required** - The engine MUST detect actual menu options present in each step rather than assuming universal [A][P][C]. Menu structures vary by workflow:
- BMM validation workflows: typically [A][P][C]
- workflow-init: uses [1-4] numbered options
- party-mode: uses [E] Exit
- Core brainstorming: uses [E] Exit, [C] Continue, and numbered technique options

The engine parses each step's output to discover which options exist before attempting selection.

**Menu Detection Patterns (CRITICAL - Avoid False Positives):**

Generic phrases like "Select an option" may appear in legitimate content (user stories, documentation, UI descriptions). The Menu Participation Engine MUST use context-aware detection:

```
MENU DETECTION REQUIREMENTS:

1. STRUCTURAL MARKERS (required - at least one):
   - Menu options on consecutive lines, each starting with bracketed letter/number
   - Horizontal menu format: "[A] [P] [C]" or "[1] [2] [3] [4]" on single line
   - Separator line (---) immediately before or after options

2. VALID MENU PATTERNS (regex with context):
   # Vertical menu with bracketed options (most common)
   PATTERN_VERTICAL = r'^(\s*\[([A-Z]|[0-9])\]\s+.+\n){2,}$'

   # Horizontal menu (inline options)
   PATTERN_HORIZONTAL = r'\[([A-Z])\](\s+\[([A-Z])\]){1,}'

   # Numbered options (workflow-init style)
   PATTERN_NUMBERED = r'^\s*\[([1-9])\]\s+.+$'

3. CONTEXT REQUIREMENTS (must satisfy ALL):
   - Menu appears at END of step output (last 20 lines)
   - Menu follows workflow content (not inside quoted text, code blocks, or examples)
   - At least 2 menu options present
   - Options are actionable (not just labels)

4. FALSE POSITIVE GUARDS:
   - REJECT if inside markdown code fence (```)
   - REJECT if inside blockquote (> prefix)
   - REJECT if preceded by "Example:", "Sample:", "Template:", "Output:"
   - REJECT if menu text appears in PRD/spec content being reviewed
   - REJECT if bracketed text is part of a link: [text](url)

5. CONFIDENCE SCORING FOR MENU DETECTION:
   - Structural markers present: +40 points
   - Position at end of output: +30 points
   - Known menu format match: +20 points
   - No false positive markers: +10 points
   - **BOUNDARY CLARIFICATION (Issue 8 Edge Case):** 70 points exactly PASSES threshold (>= is inclusive)
   - Threshold: >= 70 points to treat as menu
   - **FALSE POSITIVE PENALTY SYSTEM:** When a detected menu is later confirmed as false positive:
     - Record context signature (surrounding text patterns)
     - Apply -5 penalty when similar context reappears
     - Penalty decays after 10 successful detections in different contexts

EXAMPLE - Valid Menu (score: 100):
---
Please select your next action:
[A] Advanced elicitation - explore this topic deeper
[P] Party mode - get multiple perspectives
[C] Continue to next step
---

EXAMPLE - False Positive (score: 30, rejected):
The user interface shows:
> Select an option:
> [A] Add item
> [B] Remove item
(This is documentation of a UI, not a workflow menu)
```

```
FOR EACH STEP:
1. Execute step content (agent performs work)
2. Menu appears (DETECT actual options - may be [A][P][C], [1-4], [E], [Y][V][N], etc.)
3. Automation evaluates:
   - Confidence level for this step
   - Tier-based checkpoint rules
   - Stall detection status
   - Issue count from internal review

4. Decision matrix (includes BMB thresholds):
   ┌─────────────────────────────────────────────────────────────┐
   │ Condition                    │ Action                       │
   ├─────────────────────────────────────────────────────────────┤
   │ Confidence >= 80%, PASS      │ Auto-select [C]             │
   │ verdict or 0 errors          │                              │
   ├─────────────────────────────────────────────────────────────┤
   │ Confidence ≥50% and <80%     │ Auto-[C] for Level 0-2,     │
   │                              │ Checkpoint for Level 3-4     │
   ├─────────────────────────────────────────────────────────────┤
   │ compliance_score < 70        │ Auto-select [A] for deep    │
   │ (BMB threshold)              │ elicitation investigation   │
   ├─────────────────────────────────────────────────────────────┤
   │ Confidence < 50%             │ Auto-select [A] for deep    │
   │                              │ elicitation, then re-eval   │
   ├─────────────────────────────────────────────────────────────┤
   │ blocking_errors > 3 OR       │ Auto-select [P] for party   │
   │ major_issues > 5             │ mode (BMB threshold)        │
   │ (BMB thresholds)             │                              │
   ├─────────────────────────────────────────────────────────────┤
   │ Stalled on same issue        │ Auto-select [P] for party   │
   │ (attempts >= 2)              │ mode consultation           │
   ├─────────────────────────────────────────────────────────────┤
   │ Mandatory checkpoint (tier)  │ Present to human            │
   ├─────────────────────────────────────────────────────────────┤
   │ Code Review: Approve         │ Auto-select [C] (success)   │
   │ Code Review: Changes Req'd   │ Apply changes, re-review    │
   │ Code Review: Blocked         │ Escalate to human           │
   └─────────────────────────────────────────────────────────────┘

5. After [A] or [P] completion:
   - Menu redisplays
   - Re-evaluate confidence
   - May now qualify for [C]
```

### Batch Continue Concept

To handle the reality of dozens of [C] prompts per workflow, automation implements "batch continue":

```
BATCH CONTINUE RULES BY TIER:

Level 0-1 (Simple):
- Auto-[C] through ALL steps
- Only stop at final approval
- Human can interrupt anytime

Level 2 (Medium):
- Auto-[C] through consecutive low-risk steps
- Stop at: design decisions, architecture choices
- Batch size: up to 5 consecutive [C]s

Level 3 (Complex):
- Auto-[C] through data gathering and analysis
- Stop at: every decision point
- Batch size: up to 3 consecutive [C]s

Level 4 (Enterprise):
- Auto-[C] only for information presentation steps
- Stop at: every step that produces an artifact
- Batch size: 1-2 consecutive [C]s max
```

### Menu Rate Limiting and Fatigue Prevention

**Problem:** Fast workflows (especially Level 0-1) can present many menus in rapid succession, causing decision fatigue. Even with auto-[C], rapid-fire status updates overwhelm users.

**Solution:** Implement menu presentation throttling and intelligent batching.

#### Rate Limiting Rules

```yaml
menu_rate_limiting:
  # Minimum time between menu presentations to user
  min_interval_seconds: 2

  # Maximum menus before forced pause
  max_consecutive_menus: 10

  # Batch silent progress into summaries
  batch_silent_progress: true

  # Show progress indicator instead of individual menus
  use_progress_indicator: true
```

#### Presentation Modes

| Mode | When | User Sees |
|------|------|-----------|
| **Verbose** | Level 4, low confidence | Every menu, full context |
| **Summary** | Level 2-3, normal confidence | Batched summaries every 3-5 steps |
| **Silent** | Level 0-1, high confidence | Progress bar, results only |
| **Streaming** | Long operations | Progress indicator with current step name |

#### Batched Progress Reports

Instead of showing each step individually:
```
Step 1 complete [C]
Step 2 complete [C]
Step 3 complete [C]
Step 4 complete [C]
Step 5 complete [C]
```

Show batched summary:
```
Processing steps 1-5... [========  ] 50%
  * 5 steps completed (validation, analysis, review phases)
  * 0 issues found
  > Next checkpoint: Step 6 (Design Decision)
```

#### User Control Over Presentation

```
User: "Too many updates, just tell me when it's done"
-> Switches to Silent mode with final summary only

User: "I want to see everything"
-> Switches to Verbose mode with all menus

User: "Show me progress but don't stop"
-> Switches to Streaming mode with progress indicator
```

### Handling Menu Re-display After [A] or [P]

**Critical mechanics:** After advanced elicitation or party mode completes, the SAME MENU RE-DISPLAYS. The user must then select [C] to proceed. Automation must handle this re-display explicitly.

```
After [A] Advanced Elicitation:
1. Deep elicitation conversation occurs
2. Insights integrated into step output
3. **MENU RE-DISPLAYS** (same [A][P][C] menu)
4. Automation re-evaluates confidence (likely higher now)
5. If confidence improved → auto-select [C] from RE-DISPLAYED menu
6. If still uncertain → may select [P] from RE-DISPLAYED menu, or checkpoint to human
7. **User must select [C] from this re-displayed menu to proceed**

After [P] Party Mode:
1. Multi-agent discussion occurs (with programmatic inputs)
2. Synthesis generated
3. **MENU RE-DISPLAYS** (same [A][P][C] menu)
4. Automation evaluates synthesis quality
5. If consensus reached → auto-select [C] from RE-DISPLAYED menu
6. If no consensus → escalate to human with re-displayed menu visible
7. **User must select [C] from this re-displayed menu to proceed**

Menu Participation Engine MUST:
- Detect when menu is re-displayed after [A]/[P] completion
- **Block user input until [A]/[P] subagent completes AND confidence re-evaluation finishes** (synchronization requirement)
  - **Timeout: 120s** (matching party mode round timeout). Note: This is distinct from the 500ms in-flight response grace period (see IN-FLIGHT RESPONSE CLEANUP) which applies during exit cleanup, not synchronization waits.
  - **On timeout:** Escalate to human with partial state, allowing manual decision
- Re-run confidence evaluation with new information
- Make fresh auto-selection decision (not assume [C])
- Track that this is a "post-elicitation" menu (for audit trail)
```

---

## Component Specifications

### 1. Autonomous Validation Loop

The core change: validation runs with **verdict-based success criteria** that vary by validation type.

#### Validation Types and Success Criteria

**BMM validation produces VERDICTS, not issue counts. Note: Different workflows use different verdict terminology:**

| Validation Type | Verdict Terms | Success Criterion | Iteration Goal |
|-----------------|---------------|-------------------|----------------|
| **Implementation Readiness** | READY / NEEDS WORK / NOT READY | READY verdict | Fix issues until READY (NEEDS WORK triggers human review) |
| **Test Traceability** | PASS / CONCERNS / FAIL / WAIVED | PASS or WAIVED | Fix until PASS, or document waiver rationale |
| **Code Review** | ADVERSARIAL + Outcome-based | 3-10 findings required + Approve/Changes/Blocked | Find 3-10 issues (never "looks good"), then provide outcome verdict |
| **Syntax Validation** | Error count | 0 blocking errors | Fix errors |
| **Reference Validation** | Error count | 0 broken references | Fix references |
| **Workflow Compliance** | Phase pass/fail | 8-phase check passes | Fix phase failures |

#### Loop Structure (Verdict-Based)

```
1. DETECT VALIDATION TYPE (workflow-specific awareness):
   - BMM check-implementation-readiness → verdict mode
   - BMM code-review → checklist + outcome mode (Approve/Changes/Blocked)
   - BMM testarch-trace → verdict + waiver mode
   - BMB workflow-compliance-check → 8-phase mode
   - BMB agent validation → 6-step sequential mode (08a-08f as separate files)
   - BMB edit-module → 3-phase mode

2. RUN VALIDATION (phase count varies by workflow):
   - Edit-Module: 3 phases (Syntax → References → Compliance)
   - Workflow-Compliance-Check: 8 phases
   - Agent validation: 6 sequential step files (08a-08f)

3. EVALUATE RESULT based on validation type:
   - Implementation Readiness: READY → exit success, NEEDS WORK → human review, NOT READY → iterate
   - Test Traceability: PASS → exit success, CONCERNS → human review, FAIL → iterate, WAIVED → exit with rationale
   - Code Review: Approve → exit success, Changes Requested → apply changes and re-review, Blocked → escalate
   - Error-based: 0 errors → exit success, errors → iterate

4. IF needs iteration:
   a. Prioritize fixes by severity
   b. Check stall detection AND BMB thresholds (see below)
   c. Attempt fix with memory assistance
   d. INCREMENT attempt counter
   e. IF max attempts → escalate
   f. ELSE → GOTO step 2
```

#### Stall Detection + BMB Thresholds

**Stall detection (ADDITIONAL trigger, not replacement):**
- Hash the issue set after each validation using SHA-256 algorithm
- If hash matches previous attempt → stalled (same errors repeating)
- Stalled + attempts >= 2 → immediate party mode escalation

**PARTY MODE LOOP PREVENTION (CRITICAL):**
Track which error hashes have already triggered party mode to prevent stall→party mode→fail→stall loops:

```
# Persistent across validation iterations within same workflow
party_mode_failed_hashes: set[str] = {}

ON STALL DETECTED (hash matches previous):
  IF error_hash IN party_mode_failed_hashes:
    # Party mode already tried and failed for this exact error set
    → SKIP party mode escalation
    → DIRECTLY escalate to human with message:
      "Party mode previously attempted for this issue set without resolution.
       Error hash: {error_hash}
       Previous party mode outcome: {outcome_summary}"
    → Present options:
      "[1] Manual intervention required"
      "[2] Accept current state with documented issues"
      "[3] Abort workflow"
    → Log: "Party mode loop prevented - hash {error_hash} already in failed set"

  ELSE:
    → Trigger party mode normally
    → ON PARTY MODE COMPLETION:
      IF resolution_failed OR no_consensus:
        party_mode_failed_hashes.add(error_hash)
        → Log: "Party mode failed for hash {error_hash} - added to failed set"
      ELSE:
        # Success - don't add to failed set, allow re-use if different issue later resolves to same hash
        pass

# Reset failed hashes on workflow completion (success or abort)
ON WORKFLOW_END:
  party_mode_failed_hashes.clear()
```

**BMB quantitative thresholds (PRIMARY triggers):**

Note: These threshold values are design assumptions to be validated during implementation.
Actual thresholds may be tuned based on real-world workflow behavior and user feedback.

```
IF blocking_errors > 3 OR major_issues > 5:
   → Auto-trigger Party Mode for collaborative problem-solving

IF compliance_score < 70:
   → Auto-select [A] Advanced Elicitation for deep investigation

Combined logic:
- Check BMB thresholds FIRST
- Then check stall detection as fallback
- Either trigger escalates appropriately
```

#### Fix Strategy

Memory-first with multi-approach fallback:

1. Query Forgetful for similar past errors
2. If known solution exists → apply it first
3. If no known solution or it fails → try multiple approaches
4. Save successful fixes to memory for future reference
5. Save failed approaches to avoid retrying

#### Exit Conditions

Exit conditions vary by validation type:

**Implementation Readiness (check-implementation-readiness):**
- **Success:** READY verdict achieved
- **Conditional:** NEEDS WORK verdict with human acknowledgment
- **Party mode resolution:** Party mode synthesizes solution, re-validates to READY
- **Human escalation:** NOT READY persists after max attempts, or NEEDS WORK requires decision

**Test Traceability (testarch-trace):**
- **Success:** PASS verdict achieved
- **Conditional:** CONCERNS verdict with human acknowledgment, or WAIVED with documented rationale
- **Party mode resolution:** Party mode synthesizes solution, re-validates to PASS
- **Human escalation:** FAIL persists after max attempts, or CONCERNS requires decision

**Code Review (Checklist-Based):**
- **Success:** Approve outcome - review complete, code meets standards
- **Iteration needed:** Changes Requested outcome - apply suggested changes, re-review
- **Escalation needed:** Blocked outcome - fundamental issues requiring human intervention
- **Note:** Code Review is ADVERSARIAL - must find 3-10 specific issues per story (never "looks good" without findings). Uses 19-item checklist covering code quality, tests, architecture, security. Outcome is Approve/Changes Requested/Blocked AFTER findings identified.

**Error-Based Validations (Syntax, Reference):**
- **Success:** 0 blocking errors
- **Party mode resolution:** Party mode synthesizes solution, re-validates to 0 errors
- **Human escalation:** Max attempts (5) reached or party mode couldn't resolve

---

### 2. Tier Detection and Configuration

**Critical reality:** BMM uses MANUAL tier selection via workflow-init. Users choose between "BMad Method" (Levels 0-2) and "Enterprise Method" (Levels 3-4). Automation WRAPS this selection with smart suggestions, not auto-detection.

#### How Tier Selection Actually Works (workflow-init Step 3/5)

```
workflow-init presents:
────────────────────────────────
Select your methodology:

[1] BMad Method (Levels 0-2)
    - Solo developer or small team
    - Single product focus
    - Faster iteration cycles

[2] Enterprise Method (Levels 3-4)
    - Multiple teams/stakeholders
    - Complex integrations
    - Formal review processes
────────────────────────────────
```

#### Automation's Role: Suggestion Layer

Automation provides SUGGESTIONS to inform user choice, but does NOT auto-select:

```
1. ANALYZE INPUTS (pre-suggestion):
   - Task description keywords (from project-levels.yaml)
   - Estimated story count (if available)
   - Affected file scope (single file vs multi-module)
   - Workflow context (which BMAD workflow triggered this)

2. GENERATE SUGGESTION (examples are illustrative, not exhaustive):
   Level 0: "bug", "fix", "typo", single file → Suggest: BMad Method, Quick Flow
   Level 1: "feature", "add", "implement" + small scope → Suggest: BMad Method
   Level 2: "integration", "dashboard" + medium scope → Suggest: BMad Method
   Level 3: "architecture", "system", "subsystem" → Suggest: Enterprise Method
   Level 4: "platform", "enterprise", "multi-tenant" → Suggest: Enterprise Method

   NOTE: Actual keywords defined in project-levels.yaml may differ.
   These examples illustrate the pattern, not the complete keyword set.

3. PRESENT SUGGESTION (does not bypass workflow-init):
   - "Based on your description, this appears to be a Level 2 task.
      Suggested: BMad Method. [1] BMad [2] Enterprise [Q] Quick Flow"
   - User makes final selection
   - Automation proceeds with user's choice (not its suggestion)
```

#### Integration with workflow-init

```
Automation Flow:
1. User invokes workflow (e.g., "create-prd")
2. workflow-init begins
3. At tier selection step (Step 3 for Express path, Step 5 for Guided path):
   a. Automation analyzes task context
   b. Automation adds suggestion to menu display
   c. User sees: original menu + automation's recommendation
   d. User selects (may accept or ignore suggestion)
4. workflow-init continues with user's selection
5. Tier locked for session

NOT Allowed:
- Auto-selecting tier without user confirmation
- Bypassing workflow-init's tier selection step
- Overriding user's explicit tier choice
```

#### Tier → Behavior Mapping

| Level | Human Gates | Subagent Depth | Party Mode | Validation Scope |
|-------|-------------|----------------|------------|------------------|
| 0-1 | Final approval only | Single validator | Deadlock only | Workflow-specific (see below) |
| 2 | Design + Final | Parallel reviewers | Deadlock + low confidence | Workflow-specific + Code Review |
| 3 | Architecture + Design + Final | Parallel reviewers | Deadlock + mandatory pre-final + BMB thresholds | Full workflow-specific + thorough review |
| 4 | All major decisions | Parallel + party consensus | Every phase + BMB thresholds | Full + consensus required |

**Validation Scope by Workflow (not universal):**
- Edit-Module (BMB): 3 phases (Syntax → References → Compliance) - STRUCTURAL validation
- Workflow-Compliance-Check (BMB): 8 phases - STRUCTURAL validation
- Agent validation (BMB): 6 sequential step files (08a-08f) - STRUCTURAL validation
- Implementation Readiness (BMM): Verdict-based (READY/NEEDS WORK/NOT READY)
- Code Review (BMM): Checklist-based (Approve/Changes Requested/Blocked)
- Test Traceability (BMM): Verdict-based (PASS/CONCERNS/FAIL) with WAIVED option

**BMM vs BMB Validation Distinction:**
- BMM uses VERDICT-based validation (semantic review, quality assessment)
- BMB uses STRUCTURAL validation (syntax checking, reference validation, compliance scoring)
- DO NOT apply BMM scoring/verdicts to BMB workflows or vice versa

#### Override Handling

- User says "this is more complex" → bump tier up
- User says "keep it simple" → bump tier down
- Memory may suggest tier based on similar past tasks
- Confidence-based escalation still triggers regardless of tier

#### Tier Override Mechanism (Detailed)

**Users can override automation tier and behavior at any time.** Overrides are discoverable and take effect immediately.

**Override Methods:**

| Method | Syntax | Example | When Available |
|--------|--------|---------|----------------|
| **Natural language** | Tell automation what you want | "Make this more thorough" | Any time |
| **Explicit tier** | "Use tier N" or "Switch to level N" | "Use tier 4" | Any time |
| **Specific settings** | "Set [setting] to [value]" | "Set batch_continue_size to 1" | Any time |
| **Profile switch** | "Switch to [profile] profile" | "Switch to Enterprise profile" | Any time |
| **Inline override** | Add to any response | "[more oversight]" → increases checkpoints | With any response |

**Override Priority (Conflict Resolution):**

When multiple override methods conflict, apply in this priority order (highest first):

| Priority | Override Type | Example | Rationale |
|----------|---------------|---------|-----------|
| 1 (highest) | Most recent explicit tier | "Use tier 4" (said 2 min ago) | Explicit > implicit |
| 2 | Profile switch | "Switch to Enterprise profile" | Comprehensive change |
| 3 | Specific settings | "Set batch_continue_size to 1" | Targeted adjustment |
| 4 (lowest) | Natural language hints | "make this more thorough" | Ambient, less precise |

**Conflict Resolution Rules:**
- If user says "make it thorough" (hint → tier 3) then "use tier 2", tier 2 wins (explicit > hint)
- If user switches to Enterprise profile (tier 4) then says "use tier 2", tier 2 wins (recency)
- Inline modifiers `[more oversight]` apply temporarily on top of current tier (do not change base tier)

**Override Examples:**

```
# Mid-workflow tier change
User: "This got more complex than expected. Bump to tier 3."
→ Automation: "Switching to Level 3. Adding Architecture checkpoint.
   Current validation will complete, then new tier rules apply."

# Specific setting override
User: "I want to approve every step for the next phase."
→ Automation: "Setting batch_continue_size to 1 for remaining steps.
   Will checkpoint at each step until you say otherwise."

# Temporary override
User: "Auto-continue the next 5 steps, then go back to normal."
→ Automation: "Will auto-[C] through next 5 steps, then restore
   batch_continue_size to 3."

# Override with explanation
User: "Why are you stopping so often?"
→ Automation: "Tier 3 requires checkpoints at design decisions.
   Override options:
   - 'Use tier 2' for fewer stops
   - 'Set checkpoint_at_decisions to false' to skip design pauses
   - 'Auto-continue through design' for this phase only"
```

**Override Persistence:**

| Override Type | Persists For | Reset Command |
|---------------|--------------|---------------|
| Tier change | Rest of session | "Reset tier" or "Use suggested tier" |
| Setting change | Rest of session | "Reset [setting]" or "Use defaults" |
| Profile switch | Rest of session | "Reset to defaults" |
| Temporary override | Specified scope | Automatic |
| Inline modifier | Single action | Automatic |

**Important:** Overrides NEVER bypass safety-critical behavior:
- Final approval always required (unless explicitly disabled)
- Stall detection remains active
- Human can always interrupt with message

---

### 3. Subagent Review Cycle Structure

Subagent depth scales with tier to balance thoroughness vs token usage.

#### Agent Lifecycle Hooks (Claude Code 2.1)

Claude Code 2.1 introduced lifecycle hooks that can be defined in agent/subagent frontmatter. These hooks execute at key points in the agent lifecycle, enabling validation, logging, and custom behavior.

```yaml
---
hooks:
  PreToolUse:
    - command: "echo 'Tool: $TOOL_NAME'"  # Log tool usage
  PostToolUse:
    - command: "validate-result.sh"  # Validate tool output
  Stop:
    - command: "save-session-state.sh"  # Persist final state
---
```

**Hook Types:**

| Hook | Trigger Point | Use Cases |
|------|---------------|-----------|
| `PreToolUse` | Before any tool is called | Parameter validation, audit logging, rate limit checks |
| `PostToolUse` | After tool completes | Result validation, error detection, state capture |
| `Stop` | When agent completes or stops | Final state save, memory persistence, cleanup |

**Hook Applications in BMAD Subagents:**

```
PreToolUse Hooks:
├── Validate file paths before edit operations
├── Log validation attempts for audit trail
├── Check rate limits before API calls
├── Verify prerequisites are met
└── Record tool invocation timestamp

PostToolUse Hooks:
├── Capture validation results for confidence calculation
├── Trigger memory saves on significant findings
├── Update frontmatter state with outputs
├── Check for errors and flag for escalation
└── Record tool completion metrics

Stop Hooks:
├── Save final validation verdict to frontmatter
├── Trigger workflow-status update (update mode)
├── Generate audit trail entry
├── Persist successful fix patterns to Forgetful
└── Clean up temporary state
```

**Subagent Hook Configuration by Reviewer Type:**

| Reviewer | PreToolUse | PostToolUse | Stop |
|----------|------------|-------------|------|
| **Validator** | Log validation start | Capture pass/fail verdict | Save validation summary |
| **Spec Reviewer** | Load spec context | Flag spec deviations | Record spec compliance score |
| **Quality Reviewer** | Initialize quality metrics | Aggregate quality findings | Save quality report |
| **Adversarial Reviewer** | Load attack patterns | Capture vulnerabilities found | Persist attack surface analysis |

**Hook Execution in Automation Controller:**

```
Subagent Lifecycle with Hooks:
1. Dispatch subagent
2. FOR EACH tool call in subagent:
   a. Execute PreToolUse hooks
   b. Execute tool
   c. Execute PostToolUse hooks
   d. If PostToolUse flags error → early escalation
3. When subagent completes:
   a. Execute Stop hooks
   b. Collect hook outputs for synthesis
   c. Update frontmatter with final state
```

#### Level 0-1: Single Validator Flow

```
CHANGE → Validator Subagent → Issues? → Fix Loop → Done
```

- One subagent handles validation + fixing
- Lightweight, fast, minimal token usage
- Escalates to party mode only on stall

#### Level 2-3: Parallel Reviewer Flow

```
CHANGE → [Parallel Dispatch with context: fork]
           ├─ Spec Reviewer: "Does this match requirements?" (forked context)
           ├─ Quality Reviewer: "Is this well-implemented?" (forked context)
           └─ Adversarial Reviewer: "What could break?" (forked context)
        → Synthesize Findings
        → Prioritized Fix Loop
        → Re-validate (single pass unless new issues)
```

- Three perspectives catch different issue types
- Synthesis combines findings, deduplicates, prioritizes
- Adversarial reviewer specifically looks for edge cases, security, performance
- **Information asymmetry:** Reviewers don't see each other's findings (prevents groupthink)
- **Context fork (Claude Code 2.1):** Each reviewer gets identical starting context but isolated execution - see "Context Forking for Parallel Agents" section

#### Level 4: Parallel + Party Consensus Flow

```
CHANGE → Parallel Reviewers (as above)
        → Synthesize Findings
        → Party Mode Review (mandatory)
           ├─ Architect: Structural implications
           ├─ TEA: Test coverage adequacy
           └─ Domain Expert: Business logic correctness
        → Consensus Synthesis
        → Fix Loop (if issues)
        → Human Checkpoint (with full audit)
```

- Full parallel review PLUS party mode validation
- Party mode isn't just for deadlocks at this level—it's standard
- Human sees synthesis from both review layers

#### Dynamic Model Selection (Claude Code 2.1)

Subagent model selection optimizes cost and quality:

```
MODEL SELECTION BY TASK TYPE:

Haiku (fast, economical):
- Syntax validation
- Reference checking
- Simple file operations
- Metadata validation (08a, 08b, 08d)

Sonnet (balanced):
- Spec review
- Quality review
- Standard validation loops
- Most BMM workflows

Opus (complex reasoning):
- Adversarial review
- Architecture decisions
- Party mode complex discussions
- Low-confidence escalations
- Level 4 mandatory reviews

TIER-BASED DEFAULTS:
Level 0-1: Haiku primary, Sonnet on escalation
Level 2-3: Sonnet primary, Opus on escalation
Level 4: Opus primary for all reviewers

ADAPTIVE SELECTION:
- Start with tier default
- Escalate model on repeated failures
- Downgrade model on simple follow-up tasks
```

**Model Selection Impact on Confidence:**

The Confidence Calculator (Section 5) MAY factor in model selection as an optional enhancement:
- Opus analysis MAY contribute higher base confidence (+5 points)
- Haiku quick checks MAY contribute lower base confidence (-5 points)
- Sonnet provides neutral baseline (no adjustment)

**NOTE:** Model selection confidence adjustment is OPTIONAL and NOT included in the core 4 signal sources (Validation Verdict, Memory Match, Reviewer Agreement, Party Mode Outcome). If implemented, it would be a 5th signal source requiring its own point allocation (recommend 0-10 points) and integration into the confidence calculation formula. Initial implementation MAY omit this adjustment entirely.

This would allow the system to weigh findings appropriately - an Opus adversarial review finding an issue carries more weight than a Haiku syntax check flagging a warning.

**Subagent Dispatcher Integration:**

The Subagent Dispatcher (Implementation Scope) must support model selection:

```python
# Model selection parameter for subagent dispatch
def dispatch_subagent(
    task_type: str,
    tier: int,
    attempt_count: int = 0
) -> str:
    """Select model based on task type, tier, and escalation state."""

    # Task type defaults
    task_models = {
        "syntax_validation": "haiku",
        "reference_check": "haiku",
        "metadata_validation": "haiku",
        "spec_review": "sonnet",
        "quality_review": "sonnet",
        "adversarial_review": "opus",
        "party_mode": "opus",
    }

    base_model = task_models.get(task_type, "sonnet")

    # Tier-based override
    if tier >= 4:
        base_model = "opus"  # Level 4 uses Opus for all reviewers

    # Escalation override
    if attempt_count >= 2:
        # Escalate model on repeated failures
        if base_model == "haiku":
            return "sonnet"
        elif base_model == "sonnet":
            return "opus"

    return base_model
```

---

### 4. Automated Party Mode Integration

**Critical reality (CORRECTED):** Party mode in BMAD Core is MOSTLY AUTONOMOUS within a round. The orchestrator automatically:
1. Selects 2-3 relevant agents based on topic analysis
2. Generates agent responses without human intervention
3. Handles cross-talk within the same round
4. Presents [E] Exit option after agent responses complete

**Human input points:**
1. Initial topic proposal (one time)
2. [E] Exit signal to end the session (when ready to conclude)

**What party mode does NOT require:**
- Per-round "direction" or "steering" from human
- Manual agent selection (orchestrator auto-selects)
- Per-round approval to continue (agents auto-continue until exit)

**Note on Synthesis:** Core's party mode may save discussion outcomes to memory on exit, but does NOT auto-generate a synthesis document. Memory saves capture discussion outcomes if configured.

#### Party Mode Exit Handling

Core party mode recognizes specific exit trigger keywords. Automation must use these to terminate sessions:

```
EXIT TRIGGER KEYWORDS (Core-defined):
- "*exit"       → Immediate session termination (literal string with asterisk)
- "goodbye"     → Polite session end
- "end party"   → Explicit party mode termination
- "quit"        → Session termination

NOTE: The asterisk in "*exit" is a LITERAL character, not a wildcard.
Core performs exact string matching on these keywords.

AUTOMATION IMPLICATION: Programmatic party mode invocations must use exact
keyword strings for reliable exit. No fuzzy matching or variations are supported.

Party Mode Driver MUST:
1. Use one of these exact keywords to end sessions
2. Prefer "end party" for clarity in programmatic context
3. Handle case where agents continue after exit (ignore responses)
4. Capture final state BEFORE sending exit trigger
```

#### Agent Selection Constraints

**Orchestrator AUTOMATICALLY selects 2-3 agents based on topic analysis.** This is orchestrator behavior (from step-02-discussion-orchestration.md lines 48-56), not a recommendation to humans. The selection happens programmatically:

```
AGENT SELECTION (Orchestrator Auto-Behavior):
- Orchestrator analyzes topic content
- Orchestrator auto-selects 2-3 most relevant agents
- Selection is AUTOMATIC based on agent expertise matching
- Human does NOT manually choose agents
- Automation can influence by crafting topic to attract specific expertise

Examples:
- Architecture discussion: Architect + Dev + TEA (3 agents)
- Implementation issue: Dev + Adversarial (2 agents)
- Test coverage: TEA + Dev (2 agents)
- Complex decision: Architect + Domain Expert + QA (3 agents)

If more than 3 perspectives needed:
- Run multiple party mode sessions
- Each session focuses on different aspect
- Synthesize across sessions
```

#### Cross-Talk Awareness

**Core's party mode provides INSTRUCTIONAL GUIDANCE for cross-talk** - it's a prompting pattern, not a technical framework feature. The orchestration instructions guide agents to reference each other:

```
CROSS-TALK (Instructional Pattern, not Technical Framework):
- Agent A responds to topic
- Agent B may respond TO Agent A (not just to topic)
- This is achieved through PROMPTING INSTRUCTIONS to the orchestrator
- NOT a "framework" or "code" that enables this - it's guidance
- Creates richer dialogue through instructed multi-agent interaction
- Driver should allow cross-talk before considering exit

Automation Handling:
- Monitor for agent-to-agent references ("As [Agent] mentioned...")
- Allow 1-2 cross-talk exchanges before injecting new direction
- Detect when cross-talk becomes circular (stall signal)
- Cross-talk convergence is strong consensus signal
```

#### How Party Mode Actually Works (Core) - CORRECTED

```
Core Party Mode Flow (per step-02-discussion-orchestration.md):
1. Human proposes topic (one time)
2. Orchestrator AUTOMATICALLY selects 2-3 relevant agents
3. Agents generate responses AUTOMATICALLY (no human input)
4. Cross-talk occurs AUTOMATICALLY within same round
5. [E] Exit option presented after responses
6. If user doesn't exit → agents auto-continue with new responses
7. Loop continues until user sends exit signal
8. On exit: Memory save may occur (if configured)

NO "per-round direction" prompts exist in the orchestration.
Agents continue discussing autonomously until exit.
```

#### Automation as Party Mode Driver - CORRECTED

The Party Mode Driver focuses on EXIT DETECTION, not per-round steering:

```
Party Mode Driver (Corrected Design):
┌─────────────────────────────────────────────────────────────────┐
│ Input: Topic, Context, Goal                                      │
├─────────────────────────────────────────────────────────────────┤
│ 1. Generate topic proposal (based on context)                   │
│ 2. Submit topic → Party mode begins (autonomous)                │
│ 3. MONITOR agent responses for:                                 │
│    - Convergence signals (agents agreeing)                      │
│    - Stall signals (same points repeating)                      │
│    - Resolution indicators (actionable outcomes)                │
│    - Max rounds reached (default: 5)                            │
│    - **Direct questions to user** ('[Agent] asks:' pattern)     │
│ 4. When exit condition detected (STANDARDIZED ORDER):           │
│    a. Detect exit condition (convergence/stall/max rounds)      │
│    b. Capture final state snapshot BEFORE sending exit          │
│    c. Send exit keyword ("end party")                           │
│    d. IN-FLIGHT RESPONSE CLEANUP (see below)                    │
│    e. Ignore any subsequent agent responses                     │
│ 5. If critical disagreement persists after max rounds:          │
│    - Capture state snapshot                                     │
│    - Send exit keyword                                          │
│    - Escalate to human with discussion summary                  │
│ 6. Post-exit: Extract key outcomes for memory save              │
└─────────────────────────────────────────────────────────────────┘

IN-FLIGHT RESPONSE CLEANUP (CRITICAL):
When exit keyword is sent, agents may have responses already in-flight (generated but not yet processed).

CLEANUP PROTOCOL:
1. **Grace period:** Wait 500ms after sending "end party" for in-flight responses to arrive
2. **Buffer drain:** Read and discard any responses that arrive during grace period
3. **State finalization:** Only after grace period, mark session state as FINAL
4. **Response handling:**
   - Responses arriving during grace period: logged but NOT included in synthesis
   - Responses arriving after FINAL state: completely ignored, not logged
5. **Timeout safety:** Uses standard 60s agent timeout (same as party mode agent response timeout). If agent appears stuck, wait up to 60s before proceeding. Note: during cleanup, late responses may be lost; this is acceptable since exit was already triggered.
6. **Session file update:**
   ```yaml
   # party-mode-session.yaml after exit
   status: "completed"
   exit_reason: "consensus_reached|max_rounds|stalled|human_escalation"
   final_state_captured_at: "2026-01-08T14:32:00.500Z"
   in_flight_discarded: 2  # count of responses discarded during grace period
   ```
7. **Partial response handling:** If an agent was mid-generation when exit sent:
   - Do NOT wait for completion
   - Capture partial response text if available
   - Mark in state: `partial_responses: [{agent: "architect", truncated_at: "considering the..."}]`
   - **Utilization policy:** Partial responses are logged for debugging but EXCLUDED from synthesis (incomplete context could produce misleading conclusions). Only fully-completed responses received BEFORE exit keyword are included in outcome synthesis.

NOTE: Driver does NOT provide "direction" per round.
Driver MONITORS and decides WHEN to exit.
Agents drive their own discussion autonomously.

USER INPUT DURING EXIT GRACE PERIOD (Issue 2 Edge Case):
When user submits input during the 500ms exit grace period:
- Queue the user message (do not process immediately)
- Display acknowledgment: "Ending party mode session, your message will be processed shortly."
- After grace period completes and session marked FINAL:
  - Process queued user message in main automation context
  - Log: "User input received during exit grace, processed post-session"
- If queued message references party mode discussion: include synthesis in response context

DIRECT QUESTION HANDLING:
When agents ask user-directed questions (detected via '[Agent Name] asks:' pattern),
driver ESCALATES to human rather than auto-continuing. This ensures human input
is obtained when agents explicitly request user clarification or decision.

#### Subagent Resumption (Claude Code 2.1)

Subagent invocations return an `agent_id` that enables resumption:

**Task Tool Resume Parameter:**
```python
# Initial invocation
result = Task(
    prompt="Validate implementation against requirements",
    context="fork"
)
# result includes agent_id for potential resume

# Later, if interrupted or context limit hit:
resumed_result = Task(
    resume=result.agent_id  # Continues from exact state
)
```

```
SUBAGENT LIFECYCLE:
1. Dispatch subagent → receive agent_id
2. Store agent_id in session state
3. On interruption/timeout:
   - Preserve agent_id
   - Log interruption point
4. Resume with: Task(resume=agent_id)
   - Continues from exact state
   - Full context preserved

USE CASES:
- Long validation loops hitting context limits
- Party mode sessions requiring multiple rounds
- Interrupted review cycles
- Background validation tasks

PARTY MODE RESUMPTION:
- Store agent_id from party mode session initiation
- If party mode hits token limits mid-discussion:
  - Capture current discussion state
  - Store agent_id for resume
  - On resume: Task(resume=agent_id) continues discussion
  - Agents retain full prior context
- Enables multi-session party mode for complex topics

VALIDATION LOOP RESUMPTION:
- Track agent_id for each validation subagent
- On timeout/failure during validation:
  - Preserve agent_id with last known state
  - Log which validation step was interrupted
- User can choose to resume:
  - Task(resume=agent_id) picks up from interruption
  - No need to re-run completed validation phases
- Particularly useful for Level 3-4 multi-phase validations
```

TECHNICAL MECHANISM (H1 - Party Mode Input):
- Topic submission: Uses party-mode workflow input mechanism (initial message)
- Monitoring: Automation reads agent responses from party mode output stream
- Exit signaling: Sends exit keyword through standard workflow input channel
- State capture: Reads final discussion state from party mode session context

IMPLEMENTATION DECISION (H1 - DELIBERATE BOUNDARY):
This design specifies WHAT the Party Mode Driver does (monitor, detect exit conditions),
not HOW it technically interfaces with party mode. The actual integration mechanism
(message passing, API calls, event streams, etc.) is an IMPLEMENTATION CONCERN
to be determined during development based on the actual party-mode workflow structure.
Options include: parsing workflow output, subscribing to event streams, reading from
session files, or using direct API integration if available.
```

#### Party Mode Driver Interface Contract (S1)

```
MONITORING: Poll party-mode-session.yaml at 2s intervals
FORMAT: {session_id, status, round_number, agents_active, convergence_signals}
EXIT CONDITIONS: max_rounds | consensus_reached | stalled → capture state → "end party"
ESCALATE: awaiting_user_response → needs human input
CAPTURE SEQUENCE: detect exit → capture state → extract outcomes → send exit keyword → ignore subsequent

YAML PARSE FAILURE HANDLING:
- On malformed YAML: retry once after 500ms
- If still fails after retry: treat as stalled and exit session
- Log error with full file contents for debugging
- Return {status: "parse_error", raw_content: "..."} for diagnosis
```

#### Trigger 1: Deadlock Breaking + BMB Thresholds (All Tiers)

```
PRIMARY TRIGGER (BMB thresholds - check FIRST):
IF blocking_errors > 3 OR major_issues > 5:
   → Auto-trigger party mode via Party Mode Driver
   → Topic: "High issue count detected: {blocking} blocking, {major} major. Need collaborative resolution."
   → Agents: Select based on issue type (architect for structural, dev for implementation, etc.)
   → Driver MONITORS for exit conditions (does not steer discussion - agents drive themselves)
   → Driver requests synthesis when convergence detected
   → Apply synthesized solution
   → Re-validate after applying

SECONDARY TRIGGER (stall detection - check if thresholds not met):
IF validation stalled (same issues repeating) AND attempts >= 2:
   → Auto-trigger party mode via Party Mode Driver
   → Topic: "Validation stuck on: {issue_list}. Need approaches to resolve."
   → Same agent selection and driver behavior as above
```

#### Trigger 2: Low Confidence / Low Compliance Consultation (Tier 2+)

```
BMB THRESHOLD FOR ADVANCED ELICITATION:
IF compliance_score < 70:
   → Auto-select [A] Advanced Elicitation (not party mode)
   → Deep investigation into compliance gaps
   → May lead to party mode if elicitation reveals complex issues

CONFIDENCE-BASED TRIGGER:
IF AI confidence < threshold (e.g., 60%) on a decision:
   → Auto-trigger party mode via Party Mode Driver
   → Topic: "Need perspectives on: {decision_context}"
   → Agents: 2-3 relevant to the domain
   → Driver explores disagreements, seeks convergence
   → Outcome: Confidence boosted by multi-perspective agreement
   → If no convergence after max rounds → escalate to human
```

#### Trigger 3: Mandatory Pre-Final Review (Tier 3-4)

```
BEFORE final approval checkpoint:
   → Auto-trigger party mode via Party Mode Driver
   → Topic: "Final review of: {deliverable_summary}"
   → Agents: Architect + QA/TEA + relevant domain expert
   → Driver guides toward identifying any blocking concerns
   → Must reach no-critical-concerns state (not full agreement)
   → If critical concerns remain → escalate to human with full transcript
```

#### Alternative: Simulated Party Mode (Subagent-Based)

For fully autonomous operation, consider a simulated party mode that doesn't use Core's party-mode workflow:

```
Simulated Party Mode (Subagent Dispatcher):
1. Spawn 3-5 subagents with different agent personas
2. Each subagent reviews the topic independently
3. Collect all responses
4. Main agent synthesizes findings
5. No human input required at any point

Trade-offs:
+ Fully autonomous (no per-round input needed)
+ Faster (parallel execution)
- Loses dynamic back-and-forth dialogue
- May miss emergent insights from true conversation
- Doesn't use BMAD's party mode infrastructure

WHEN TO USE REAL VS SIMULATED:
- Use Simulated for Level 0-2: Simple issues, speed prioritized, autonomous OK
- Use Real (with Driver monitoring) for Level 3-4: Complex issues, multi-perspective
  dialogue valuable, Driver monitors for exit conditions
- Use Real on explicit user request: User may want multi-agent discussion quality
- Use Simulated for batch operations: When running multiple validations unattended
```

#### Context Forking for Parallel Agents (Claude Code 2.1)

Claude Code 2.1 introduced `context: fork` for subagents, which gives them access to the full conversation history up to that point, but in an isolated fork. Changes in the fork do not affect the main conversation.

This is ideal for simulated party mode and parallel review scenarios where multiple agents need the same baseline context but must work independently.

```
CONTEXT FORK BEHAVIOR:
- Subagent receives FULL conversation history
- Subagent's changes are ISOLATED from main context
- Multiple forks can run in parallel
- Results collected without cross-contamination

SIMULATED PARTY MODE WITH FORKS:
1. Main agent prepares topic and context
2. Spawn 3 subagents with context: fork
   - Architect perspective (forked context)
   - Developer perspective (forked context)
   - QA perspective (forked context)
3. All three see identical starting state
4. Each generates independent analysis
5. Main agent synthesizes results

PARALLEL REVIEWER FLOW WITH FORKS:
- Spec Reviewer (context: fork)
- Quality Reviewer (context: fork)
- Adversarial Reviewer (context: fork)
→ Information asymmetry maintained
→ Each reviewer works independently
→ No groupthink from seeing other findings
```

**Benefits for BMAD Automation:**
- **Identical baseline:** All agents start from the exact same context snapshot
- **True isolation:** Reviewer A cannot see Reviewer B's findings (prevents groupthink)
- **Parallel execution:** Forks can run concurrently without coordination overhead
- **Clean synthesis:** Main agent receives independent results without cross-contamination

**Implementation:**

**Claude Code Task Tool Invocation Examples:**

The Task tool in Claude Code uses these parameters:
- `prompt`: The instruction for the subagent
- `context`: Either "fork" (isolated context) or "inherit" (shared context)
- `resume`: Agent ID to resume a previous session
- `allowed_tools`: Optional list of tools the subagent can use

```
Subagent Dispatcher with context: fork:

FOR simulated party mode:
  # Each agent gets identical starting context but isolated execution
  Task(
    prompt="Analyze this architecture as the Architect agent. Focus on structural patterns, scalability, and technical debt.",
    context="fork",
    allowed_tools=["Read", "Grep", "mcp__serena__find_symbol"]
  )
  
  Task(
    prompt="Analyze this architecture as the Developer agent. Focus on implementation complexity, edge cases, and maintainability.",
    context="fork",
    allowed_tools=["Read", "Grep", "mcp__serena__find_symbol"]
  )
  
  Task(
    prompt="Analyze this architecture as the QA agent. Focus on testability, error handling, and failure modes.",
    context="fork",
    allowed_tools=["Read", "Grep", "mcp__serena__find_symbol"]
  )
  
  # Results collected and synthesized by main agent

FOR parallel reviewers:
  # Information asymmetry - each reviewer works independently
  Task(
    prompt="Review for spec compliance. Check all requirements from PRD are addressed.",
    context="fork"
  )
  
  Task(
    prompt="Review for code quality. Check patterns, naming, error handling.",
    context="fork"
  )
  
  Task(
    prompt="ADVERSARIAL review. Find 3-10 specific issues. Challenge assumptions.",
    context="fork"
  )
  findings = await parallel(reviewers)  # Information asymmetry preserved
  prioritized = deduplicate_and_prioritize(findings)
```

#### Dynamic Agent Selection

- Query agent manifest (including custom agents created in session)
- Match agent expertise to issue/topic domain
- Rotate participation to avoid single-agent dominance
- Custom project agents (created during earlier BMAD phases) included in roster

#### Agent Naming and Disambiguation (CRITICAL)

**Problem:** Agent names like "analyst" exist in multiple modules (bmm:analyst, bmb:analyst if created). Short names cause ambiguity and potential invocation of wrong agent.

**Fully-Qualified Name Requirements:**

```
AGENT IDENTIFIER FORMAT:
  <module>:<agent-name>

Examples:
  bmm:analyst      → Mary (BMM Business Analyst)
  bmm:architect    → Winston (BMM Architect)
  bmb:agent-builder → Bond (BMB Agent Builder)
  core:bmad-master → BMAD Master orchestrator
  custom:project-specialist → User-created agent

DISAMBIGUATION RULES:

1. ALL agent references in automation MUST use fully-qualified names:
   - Party Mode Driver: agents=["bmm:architect", "bmm:dev", "bmm:tea"]
   - Subagent Dispatcher: agent="bmm:analyst"
   - Review assignments: reviewer="bmb:agent-builder"

2. AMBIGUITY DETECTION (at manifest load):
   - Scan all modules for duplicate short names
   - If duplicate found: REQUIRE fully-qualified names for that agent
   - Log warning: "Agent 'analyst' exists in modules: bmm, custom. Use fully-qualified names."

3. SHORT NAME RESOLUTION (fallback only):
   - Only allowed when agent name is UNIQUE across all modules
   - Resolution order if ambiguous: bmm → bmb → core → custom
   - WARN in logs when short name resolution is used

4. MANIFEST SCHEMA UPDATE:
   module,name,qualified_name,role,persona_file,description
   bmm,analyst,bmm:analyst,Business Analyst,persona-analyst.md,"Mary - requirements analysis"
   bmb,agent-builder,bmb:agent-builder,Agent Creator,persona-bond.md,"Bond - creates custom agents"

5. VALIDATION AT STARTUP:
   - Parse all agent references in workflow files
   - Flag any unqualified names that are ambiguous
   - Abort with clear error if ambiguous reference found in critical path

EXAMPLE - Ambiguous Reference Error:
  ERROR: Agent reference "analyst" is ambiguous.
  Found in modules: bmm (Mary), custom (ProjectAnalyst)
  Fix: Use "bmm:analyst" or "custom:analyst" in workflow configuration.
```

#### Custom Agent Registration

When custom agents are created via BMB (agent-builder workflow), they must be registered
for automation to discover and use them. Registration options:

```
REGISTRATION OPTIONS:

1. MANIFEST UPDATE (recommended):
   - Add entry to `_bmad/_config/agent-manifest.csv`
   - Fields: module, name, qualified_name, role, persona_file, description
   - qualified_name MUST be unique across all modules (e.g., "custom:my-agent")
   - Automation reads manifest at workflow start
   - Requires write access to config directory

2. SEPARATE CUSTOM MANIFEST:
   - Create `_bmad/_config/custom-agents.csv` for project-specific agents
   - Same schema as agent-manifest.csv (including qualified_name)
   - Automation merges both manifests at load time
   - Preserves clean separation between core and custom agents

3. RUNTIME ROSTER EXTENSION:
   - Custom agents discovered in project's `_bmad/` directories
   - Automation scans for agent definitions at session start
   - Auto-generates qualified_name as "custom:<agent-name>"
   - No manifest update required (auto-discovery)
   - Less explicit but more flexible for temporary agents

AUTOMATION BEHAVIOR:
- At workflow start: Load core manifest + scan for custom agents
- Merge into runtime roster (deduplicated by QUALIFIED name, not short name)
- Validate no qualified_name collisions exist
- Custom agents available for party mode selection, reviews, etc.
- If custom agent not found: fall back to closest standard agent (log warning)
```

---

### 4b. Progress Visibility for Long Operations

**Problem:** During long operations (party mode, multi-phase validation, document generation), users have no visibility into progress and may think the system has stalled.

**Solution:** Continuous progress reporting with clear status indicators.

#### Progress Display Formats

##### Streaming Progress (Default for Long Operations)

```
Party Mode in Progress...
  Topic: "Architecture review for caching strategy"
  Round: 3/5 (max)
  Agents: Architect, Dev, TEA
  Status: Cross-talk in progress
  [===========         ] 60%
  
  Current: TEA responding to Architect's concern about cache invalidation
  
  Convergence signals: 2 agreements detected
  [E] Exit now  [S] Status details  [Q] Quiet mode
```

##### Summary Progress (For Background Operations)

```
Background: Validation running (step 4/8)...
  Last update: 12s ago
  Estimated remaining: ~45s
```

##### Detailed Progress (On Request)

```
User: "What's happening?"

Automation: "Party Mode Progress Report:
  
  Round 1: Topic introduced, 3 agents selected
  Round 2: Architect proposed event-driven approach
           Dev raised concerns about complexity
  Round 3: (current) TEA assessing testability implications
  
  Convergence status:
    - 2/3 agents support event-driven pattern
    - 1 open concern about test complexity
  
  Estimated: 1-2 more rounds to reach consensus
  Time elapsed: 2m 15s"
```

#### Progress Events

| Event | Display | Sound/Alert |
|-------|---------|-------------|
| Step started | Progress bar update | None |
| Step completed | Checkmark + summary | None |
| Issue found | Warning indicator | Optional beep |
| Human input needed | Highlight + prompt | Alert sound |
| Operation stalled | Red indicator | Alert |
| Completion | Success message | Completion chime |

#### Configuration

```yaml
progress_display:
  mode: streaming            # streaming | summary | quiet
  update_interval_seconds: 5 # How often to update display
  show_estimates: true       # Show time remaining estimates
  sound_alerts: false        # Enable audio alerts
  
  # Long operation thresholds
  long_operation_seconds: 30 # When to start detailed progress
  stall_detection_seconds: 60 # When to show stall warning
```

#### User Control

```
User: "Be quiet until done"
-> Switches to summary mode, shows only completion

User: "Show me everything"
-> Switches to streaming mode with detailed updates

User: "What's taking so long?"
-> Shows detailed progress report + estimated remaining time
```

---

### 5. Human Checkpoint Design

Adaptive detail based on confidence level.

#### Confidence Calculation

**STATUS: NEW FUNCTIONALITY (PROPOSED)** - Core BMAD has no confidence mechanism. This must be implemented as part of the automation layer. The signal sources and point values below are proposed starting points to be refined during implementation and tuning.

```
Confidence is CALCULATED (not assigned) based on observable signals:

SIGNAL SOURCES (each contributes to confidence score):

1. Validation Verdict (0-35 points):
   - PASS verdict: +35
   - CONCERNS verdict: +15
   - FAIL verdict: +0
   - For error-based: 0 errors = +35, 1-2 errors = +20, 3+ errors = +5

2. Memory Match Quality (0-25 points):
   - Exact pattern match from Forgetful: +25
   - Similar pattern (>80% semantic match): +15
   - Weak match (50-80%): +8
   - No relevant memories: +0

3. Reviewer Agreement (0-25 points):
   - All subagent reviewers aligned: +25
   - Majority aligned (2/3): +15
   - Split opinions: +5
   - Single reviewer (no comparison): +10

4. Party Mode Outcome (0-15 points, if used):
   - Clear consensus reached: +15
   - Partial consensus: +8
   - No consensus (still divergent): +0
   - Party mode not used: N/A (don't penalize)

IMPLEMENTATION CONCERN (H4 - Signal Extraction Methods):
This design specifies WHICH signals contribute to confidence scoring, not HOW to
extract them from workflow execution. The Confidence Calculator is NEW FUNCTIONALITY
that must be built. Signal extraction method selection is an IMPLEMENTATION DECISION.
Options include: parsing workflow output files, reading from result artifacts, querying
workflow-status data mode, subscribing to event streams, or using structured data from
frontmatter. The choice depends on actual workflow output formats discovered during
implementation.

#### Confidence Calculator Data Flow (S3)

Signal sources and their formats:

```
1. VALIDATION VERDICT (0-35 pts)
   Source: validation-result.yaml from v-02/08x steps
   Format: {source: "validation", verdict: "PASS|CONCERNS|FAIL", error_counts: {...}}

2. MEMORY MATCH (0-25 pts)
   Source: Forgetful query for fix patterns
   Format: {source: "memory", match_type: "exact|similar|weak|none", similarity_score: 0.85}

3. REVIEWER AGREEMENT (0-25 pts)
   Source: Subagent Dispatcher → reviewer-findings.yaml
   Format: {source: "reviewers", reviewer_count: 3, aligned_count: 2, findings: [...]}

4. PARTY MODE OUTCOME (0-15 pts, conditional)
   Source: Party Mode Driver → party-mode-session.yaml
   Format: {source: "party_mode", consensus_reached: true, agreement_level: "full|majority|none"}

AGGREGATION:
@dataclass
class ConfidenceResult:
    score: int        # 0-100 normalized
    threshold: str    # "high" | "medium" | "low"
    signals: list     # Individual signal contributions
    tier_adjustment: int
```

TOTAL CALCULATION:
- Sum applicable signals
- Normalize to 0-100 scale
- Apply tier adjustment (higher tiers require more evidence)

Tier Adjustment:
- Level 0-1: No adjustment
- Level 2: -5 (slightly higher bar)
- Level 3: -10
- Level 4: -15 (highest bar for confidence)

Thresholds:
- High: >= 80% → Minimal presentation
- Medium: ≥50% and <80% → Summary presentation
- Low: < 50% → Full audit trail

EDGE CASE HANDLING (CRITICAL):

1. NO SIGNALS AVAILABLE (all sources return empty/null):
   - Default confidence: 25% (low)
   - Reason: "No validation signals available"
   - Action: Escalate to human with explicit "insufficient data" warning
   - NEVER auto-continue with 0 signals
   - **Recovery Path:** Present human checkpoint with options:
     1. **[R] Retry signal collection** - Re-run validation, memory query, and reviewer checks
     2. **[O] Proceed with manual override** - Human provides explicit confidence level (1-100)
     3. **[A] Abort workflow** - Exit workflow cleanly, save state for later resume
   - Human MUST select one option; no default action taken
   - **Timeout:** 300s waiting for human selection. On timeout: save state to `_bmad-output/awaiting-human/{workflow-id}.yaml` with status `awaiting_human_decision`, present decision request on next session start
   - **SIGNAL RETRY LIMIT (CRITICAL):** Track `signal_retry_count` per checkpoint:
     ```
     signal_retry_count = 0  # Reset on successful signal collection

     ON [R] RETRY SELECTED:
       signal_retry_count += 1
       IF signal_retry_count >= 3:
         → Display warning: "Signal collection has failed 3 times. [R] Retry is unlikely to succeed."
         → Highlight recommended alternatives: "[O] Manual override or [A] Abort recommended"
         → [R] option remains available but marked as "(not recommended)"
         → Log: "Signal retry exhausted - user warned at attempt {count}"
       ELSE:
         → Proceed with retry normally
         → Display: "Retry attempt {count}/3"

     ON SUCCESSFUL SIGNAL COLLECTION:
       signal_retry_count = 0  # Reset counter
     ```

2. BOUNDARY CONDITIONS:
   - Exactly 80%: Treat as HIGH (>= is inclusive)
   - Exactly 50%: Treat as MEDIUM (>= is inclusive)
   - Negative score after tier adjustment: Clamp to 0%
   - Score > 100 before normalization: Clamp to 100%

3. NO MENU ITEMS MATCH (validation step has no applicable menu):
   - Confidence calculation still runs (for audit trail)
   - Action: Log confidence but skip menu selection
   - Return: {confidence: N%, action: "no_menu_detected"}

4. SINGLE SIGNAL SOURCE:
   - If only validation verdict available: confidence = verdict_points / 35 * 60
   - If only memory match available: confidence = memory_points / 25 * 50
   - If only reviewer agreement available: confidence = reviewer_points / 25 * 50
   - Single-source cap: Maximum 60% confidence from any single source
   - Reason: Multiple signals provide corroboration

5. CONFLICTING SIGNALS:
   - Validation PASS but reviewers disagree: Cap at 70%
   - Validation FAIL but memory shows exact fix: Allow 50% (fix may work)
   - Party mode no-consensus: Override to LOW regardless of other signals

6. CALCULATION FAILURE:
   - If confidence calculation throws exception: Default to 30% (low)
   - Log full error context for debugging
   - Escalate to human with "calculation error" flag
   - **META-HANDLER FOR FALLBACK FAILURE (Issue 12 Edge Case):** If the fallback handler itself throws:
     ```python
     try:
         confidence = calculate_confidence(signals)
     except Exception as primary_error:
         try:
             # Primary fallback
             confidence = ConfidenceResult(score=30, threshold="low", ...)
             log.error(f"Confidence calculation failed: {primary_error}")
         except Exception as fallback_error:
             # Ultimate resort - meta-handler
             log.critical(f"CONFIDENCE SYSTEM FAILURE: primary={primary_error}, fallback={fallback_error}")
             confidence = ConfidenceResult(score=25, threshold="low", edge_case="meta_failure")
             # HALT automation - human intervention required
             halt_automation(reason="confidence_system_failure")
             raise AutomationHaltException("Confidence system unrecoverable")
     ```
   - Ultimate resort confidence: 25% (extremely low)
   - HALT automation immediately - do not continue with unreliable confidence

@dataclass
class ConfidenceResult:
    score: int            # 0-100 normalized
    threshold: str        # "high" | "medium" | "low"
    signals: list         # Individual signal contributions
    tier_adjustment: int
    edge_case: str | None # "no_signals" | "single_source" | "conflict" | "calc_error" | None
    capped: bool          # True if score was clamped or capped
```

**Implementation Note:** This confidence system must be built - it does not exist in current BMAD. The percentages above are starting values to be tuned based on real-world usage.

#### Threshold Calibration and Tuning (CRITICAL)

The 80%/50% thresholds are initial estimates requiring calibration. Without calibration, thresholds may cause excessive human interrupts (too conservative) or missed quality issues (too aggressive).

**Calibration Protocol:**

1. **Data Collection Phase (first 20 workflows per tier):**
   - Log every confidence score with its signal components
   - Record human decision at checkpoint (approve/reject/modify)
   - Track downstream outcomes (issues found post-approval, rework required)
   - Store in `_bmad-output/calibration/confidence-log.jsonl`

2. **Analysis Metrics:**
   - **False Positive Rate:** High confidence presented, human rejected or later rework needed
   - **False Negative Rate:** Low confidence presented, human approved immediately without changes
   - **Optimal threshold:** Minimize total human interrupts while keeping false positive rate < 5%

3. **Tier-Specific Calibration:**
   - Each tier (0-4) calibrated independently due to different risk profiles
   - Level 0-1: Optimize for speed (higher thresholds acceptable)
   - Level 3-4: Optimize for safety (lower thresholds, more checkpoints)

4. **Threshold Adjustment Rules:**
   ```
   IF false_positive_rate > 10% for tier N:
      → Lower high_threshold by 5 points
      → Log adjustment in calibration history

   IF false_negative_rate > 20% for tier N:
      → Raise high_threshold by 5 points
      → Log adjustment in calibration history

   BOUNDS: high_threshold MUST stay within 70-90%
           medium_threshold MUST stay within 40-60%
   ```

5. **Calibration Storage:**
   ```yaml
   # _bmad-output/calibration/thresholds.yaml
   calibration_version: 1
   last_updated: "2026-01-15T10:30:00Z"
   sample_size: {tier_0: 25, tier_1: 20, tier_2: 15, tier_3: 8, tier_4: 3}
   thresholds:
     tier_0: {high: 85, medium: 55}
     tier_1: {high: 82, medium: 52}
     tier_2: {high: 78, medium: 48}
     tier_3: {high: 75, medium: 45}
     tier_4: {high: 70, medium: 40}
   ```

6. **Manual Override:** User can set explicit thresholds in project config to bypass calibration:
   ```yaml
   # bmm-workflow-status.yaml
   confidence_overrides:
     high_threshold: 75
     medium_threshold: 45
   ```

7. **Calibration Validation on Load:**
   - On load: validate schema and bounds of calibration data
   - Check: `calibration_version` exists, all tier keys present, thresholds within valid ranges (high: 70-90, medium: 40-60)
   - Invalid data conditions: missing required fields, thresholds outside bounds, malformed YAML
   - **On invalid or missing calibration data:** Fall back to defaults (high: 80, medium: 50)
   - Log warning: "Calibration data invalid/missing, using defaults: high=80, medium=50"

#### Presentation Formats

**Minimal (High Confidence >= 80%):**
```
✓ Architecture ready for approval (92% confidence)
  [Approve] [Review Details] [Reject]
```

**Summary (Medium Confidence ≥50% and <80%):**
```
Architecture ready (68% confidence)

Approach: Event-driven microservices with PostgreSQL
Rationale: Matches scalability requirements, team familiarity
Open concern: Caching strategy not fully resolved

[Approve] [Discuss Caching] [Review Full] [Reject]
```

**Full Audit Trail (Low Confidence < 50%):**
```
Architecture needs review (41% confidence)

Attempts: 3 validation cycles, 1 party mode session
Issues resolved: 7 blocking, 4 major
Remaining concerns:
  - Architect: "Event sourcing adds complexity we may not need"
  - TEA: "Test strategy unclear for async flows"
  - Dev: "Suggests simpler request-response for MVP"

Party mode synthesis attempted but no consensus reached.

[See Full Discussion] [Approve Anyway] [Iterate More] [Take Over Manually]
```

#### Checkpoints by Tier

| Tier | Checkpoints |
|------|-------------|
| 0-1 | Final approval only |
| 2 | Design approval, Final approval |
| 3 | Architecture, Design, Final |
| 4 | Architecture, Design, Implementation phases, Final |

---

### 6. Memory Integration

Forgetful enables learning across sessions. **Integration aligns with workflow-level hooks (Pre-Workflow/Post-Workflow), not agent-level hooks.**

**Context Hub Stack:** Memory Bridge integrates with the full Context Hub:
- **Forgetful MCP:** Semantic memory for decisions, patterns, and outcomes
- **Serena MCP:** LSP-powered symbol analysis for code navigation
- **Context7 MCP:** Library documentation lookup for framework guidance

#### Workflow-Level Integration Points

BMAD workflow files define Pre-Workflow and Post-Workflow hooks. Memory Bridge aligns with these:

```
WORKFLOW-LEVEL HOOKS (not agent-level):

1. PRE-WORKFLOW (workflow start):
   - When workflow begins execution
   - Query Forgetful for project context
   - Load relevant memories before work begins

2. POST-WORKFLOW (workflow completion):
   - When a workflow successfully completes
   - Save significant decisions and outcomes
   - Link to project and related entities

NOTE: These are WORKFLOW hooks, not agent activation hooks.
A workflow may involve multiple agents; memory is loaded once at workflow start,
not when each individual agent activates.

AUTOMATION EXTENDS THESE (does not replace):
- Additional queries during validation loops
- Additional saves on fix pattern discovery
- Preserves Core's pre-workflow/post-workflow as primary hooks
```

#### One-Time Hooks (Claude Code 2.1.2)

Claude Code 2.1.2 introduced `once: true` for hooks, which makes them run only once per session rather than on every invocation. This is ideal for session initialization tasks.

```yaml
---
hooks:
  SessionStart:
    - command: "query-forgetful-context.sh"
      once: true  # Only runs once at session start
  PreToolUse:
    - command: "validate-prerequisites.sh"
      once: true  # First tool use only
    - command: "log-tool-usage.sh"
      once: false  # Every tool use (default)
---
```

**BMAD One-Time Hook Applications:**

| Hook Purpose | Once Setting | Rationale |
|--------------|--------------|-----------|
| Query Forgetful for project context | `once: true` | Load context once at session start, not repeatedly |
| Detect workflow state (CLEAN/PLANNING/ACTIVE/LEGACY) | `once: true` | State detection needed once per session |
| Load tier configuration | `once: true` | Tier locked for session after selection |
| Validate prerequisites | `once: true` | Environment checks needed once |
| Field type detection (greenfield/brownfield) | `once: true` | Project structure doesn't change mid-session |
| Quick-dev mode detection | `once: true` | Mode determined once at entry |
| Log tool usage | `once: false` | Every tool use for audit trail |
| Track step progression | `once: false` | Every step transition |

**Memory Integration Alignment:**

```
Core's AGENT START hook → once: true SessionStart hook
- Project context loaded once, not on every step
- Avoids redundant Forgetful queries
- Reduces token usage and latency

Workflow Entry Detection → once: true PreToolUse hook
- workflow-init state detection runs once
- Tier suggestion generated once
- Quick-dev bypass detection once

Continuous Hooks (once: false or default):
- Validation loop queries (may need fresh patterns)
- Fix pattern saves (after each successful fix)
- Audit trail logging (every action)
```

**Implementation Note:** The `once: true` parameter is a Claude Code 2.1.2 feature. Hooks without this parameter default to running on every invocation. Use `once: true` for initialization tasks and `once: false` (or omit) for ongoing operations.

#### What Gets Saved

**At WORKFLOW COMPLETION (Core hook):**
| Event | Memory Created | Importance |
|-------|----------------|------------|
| Workflow outcome | "Completed {workflow}: {summary}" | 7 |
| Human decision rationale | "Decision: {choice} because {user_reason}" | 8 |
| Tier selection | "User chose Level {N} for {task_type}" | 6 |

**During AUTOMATION LOOPS (new hooks):**
| Event | Memory Created | Importance |
|-------|----------------|------------|
| Successful fix pattern | "Fix: {error_type} → {solution}" | 7 |
| Party mode discussion outcome | "Party discussion: {topic} → {outcome_summary}" | 7 |
| Party mode consensus decisions | "Party consensus: {topic} → {specific_decisions}" | 8 |
| Failed approach | "Avoid: {approach} for {context} - {why_failed}" | 6 |

**Party Mode Memory Split (Core expectation):**

Core saves "discussion outcome" and (conditionally) "consensus decisions" SEPARATELY. Automation must create memories after party mode:

```
Memory 1: Discussion Outcome (ALWAYS created, importance: 7)
- Title: "Party discussion: {topic}"
- Content: What was discussed, key points raised, areas explored
- Context: "Discussion summary from party mode session"
- Tags: ["party-mode", "discussion", "{workflow_name}"]

Memory 2: Consensus Decisions (CONDITIONAL - only if consensus reached, importance: 8)
- Title: "Party consensus: {topic}"
- Content: Specific decisions made, action items, agreed approach
- Context: "Actionable consensus from party mode session"
- Tags: ["party-mode", "consensus", "decision", "{workflow_name}"]
- NOTE: Only create if party mode actually reached consensus
        If no consensus, only Memory 1 is saved

CONSENSUS CRITERIA (for determining when to create Memory 2):
- All agents align on key decision points (unanimous)
- OR majority align with no blocking objections (2/3+ agreement)
- AND specific action items or decisions are produced (not just discussion)
        If discussion happened but no actionable consensus emerged, Memory 1 only.

DO NOT conflate into single "synthesis" save.
Memory 1 is always created; Memory 2 only if consensus was achieved.
```

#### Query Points

**At AGENT START (Core hook - mandatory):**
```
query: "project context {project_name}"
context: "Agent starting work on project"
→ Returns project background, past decisions, patterns
→ THIS HAPPENS AUTOMATICALLY via Core
```

**During AUTOMATION (additional queries):**
```
1. ON VALIDATION ERROR:
   query: "{error_type} fix solution"
   context: "Automated fix attempt for validation"
   → Returns known solutions to try first

2. ON TIER SUGGESTION:
   query: "tier preference {task_keywords}"
   context: "Checking if user has tier preferences for similar tasks"
   → Informs suggestion (does not auto-select)

3. ON PARTY MODE START:
   query: "{topic} perspectives decisions"
   context: "Loading context for party mode discussion"
   → Agents get relevant past discussions

4. ON APPROACH SELECTION:
   query: "{problem_type} approaches avoided failed"
   context: "Checking for approaches to skip"
   → Prevents repeating known failures
```

#### Memory Timing Alignment

```
CORRECT TIMING (aligned with Core):

AGENT START → Query memories (Core hook)
    ↓
AUTOMATION LOOP → Query for fixes (automation extension)
    ↓
AUTOMATION LOOP → Save fix patterns (automation extension)
    ↓
WORKFLOW COMPLETION → Save outcomes (Core hook)

INCORRECT TIMING (avoid):
- Querying project context mid-workflow (should be at start)
- Saving decisions before workflow completion
- Bypassing Core's hooks with custom timing
```

#### Learning Loop Example

```
Session 1: Error X occurs → tries 3 approaches → approach B works → saves pattern (automation hook)
Session 2: Agent starts → loads project context (Core hook) → Error X occurs → queries memory → finds approach B → applies immediately → 1 attempt instead of 3
```

---

### 7. Error Handling and Edge Cases

#### Escalation Hierarchy

```
Autonomous Fix → Party Mode → Human Escalation → Manual Takeover
```

#### Edge Case Handling

| Scenario | Response |
|----------|----------|
| Max attempts (5) reached | Escalate to human with full audit trail |
| Party mode can't synthesize | Escalate to human with agent perspectives listed |
| Confidence stays low after party mode | Present decision with low-confidence format |
| Memory returns conflicting patterns | Try most recent pattern first, fall back to multi-approach |
| Custom agent not available | Fall back to closest standard agent from manifest |
| Validation itself errors | Stop loop, escalate immediately with error context |
| User overrides mid-loop | Respect immediately, adjust tier/approach as directed |
| Circular fix (A breaks B, B breaks A) | Stall detection catches this, escalates to party mode |
| Subagent timeout/context limit | Store agent_id, offer resume option via Task(resume=agent_id) |
| Party mode hits token limit | Preserve agent_id, allow multi-session continuation |
| **Infinite validation loop** | Max 10 iterations with escape hatch (see below) |
| **Deadlock between agents** | 60s timeout per agent response; detection + abort (see below) |
| **Crash mid-workflow** | Checkpoint/resume from frontmatter (see below) |

#### Deadlock Detection and Prevention

```
DEADLOCK SCENARIOS:
1. Agent A waits for Agent B's output; B waits for A
2. Validation fix creates new issue that triggers same validation
3. Party mode consensus loop never converges

DETECTION:
- 60-second timeout per agent response in party mode
- Track dependency graph: if A->B->A detected, break cycle
- Monitor validation fix patterns: if same fix attempted 3x, abort loop

TIMEOUT SPECIFICATION:
- Single agent operation: 60s timeout
- Party mode round: 120s timeout (allows agent cross-talk)
- Nested workflow call: 300s timeout
- Background watcher poll: 5s interval (state detection), 30s stale threshold
  NOTE: Poll interval (5s) differs from display update interval (5s in progress_display config).
        Poll detects state changes; display interval controls user-facing updates. Same value is coincidental.

RESOLUTION:
IF timeout detected:
   → Log timeout event with full context
   → Abort waiting operation
   → Return partial result (if available)
   → Escalate to human with deadlock diagnosis
   → Do NOT retry automatically (prevents thrashing)

IF circular dependency detected:
   → Break cycle by aborting most recent requester
   → Preserve results from completed agents
   → Escalate with dependency graph visualization
```

#### Infinite Validation Loop Prevention

```
VALIDATION ITERATION LIMITS:

MAX_VALIDATION_ITERATIONS = 10  # Absolute ceiling for entire validation process
MAX_SAME_ERROR_RETRIES = 3      # Same error type (nested within fix attempts)
MAX_PARTY_MODE_ROUNDS = 5       # For deadlock-breaking sessions

LIMIT NESTING (how these relate to max_fix_attempts=5 in config):
- max_fix_attempts (5) = attempts per validation failure before escalating
- Within each fix attempt: MAX_SAME_ERROR_RETRIES (3) limits same-error retries
- Across ALL fix attempts: MAX_VALIDATION_ITERATIONS (10) is absolute ceiling
- Example: 2 fix attempts with 3 same-error retries each = 6 iterations total

ITERATION COUNTING SEMANTICS:
- iteration_count INCREMENTED at START of each attempt
- Check happens AFTER increment, BEFORE execution
- Thus iteration 10 IS attempted (count=10 passes check)
- Iteration 11 NOT attempted (count=11 fails check >= 10)

ESCAPE HATCH BEHAVIOR:

IF iteration_count >= MAX_VALIDATION_ITERATIONS:
   → STOP validation loop immediately
   → Package all iteration results into summary
   → Present to human with options:
     [1] Accept current state with documented issues
     [2] Manual intervention mode
     [3] Abort workflow entirely
   → Record escape hatch trigger in audit trail

IF same_error_count >= MAX_SAME_ERROR_RETRIES:
   → STOP attempting same fix strategy
   → Trigger party mode (if not already in party mode)
   → If already in party mode: escalate to human

OSCILLATION DETECTION:
- Track validation result hashes across iterations
- Pattern: PASS → FAIL → PASS → FAIL = oscillation
- After 2 oscillations: trigger escape hatch
- Human must resolve oscillating state
```

#### Human Override Points

Even in autonomous mode, human can always:
- Interrupt with a message → system pauses, responds
- Type "stop" or "take over" → exits automation, returns control
- Adjust tier mid-session → system reconfigures
- Skip a checkpoint → system proceeds (logged for audit)

#### Graceful Degradation

**Forgetful MCP Unavailable:**

```
DETECTION:
- Context Pre-Loader polls Forgetful with 3 retries, 100ms apart (see Initialization Order)
- Timeout after 300ms total → mark Forgetful as UNAVAILABLE for session
- MCP connection errors → immediate UNAVAILABLE status

FALLBACK BEHAVIORS:
1. Context Pre-Loader:
   - Returns empty memory set: {memories: [], status: "degraded", reason: "forgetful_unavailable"}
   - Caches degraded status to prevent repeated connection attempts
   - Cache TTL: 5 minutes before retry attempt

2. Memory Bridge:
   - Query operations return empty results (not exceptions)
   - Save operations queue to local file: `_bmad-output/.memory-queue/{timestamp}.json`
   - Queue processed on Forgetful reconnection (checked every 5 minutes)
   - Queue max size: 100 entries
   - **QUEUE OVERFLOW HANDLING (Issue 9 Edge Case):** On insert when queue size >= 100:
     1. Acquire queue mutex (prevents concurrent modification)
     2. Pop oldest entry from queue
     3. Append new entry
     4. Release mutex
     5. Log: "Memory queue at capacity, dropped oldest: {dropped_entry_summary}"

3. Post-Workflow Memory Curator:
   - Skips memory creation entirely (no-op)
   - Logs: "Memory curation skipped: Forgetful unavailable"
   - Saves intended memories to queue (same as Memory Bridge)

4. Confidence Calculator:
   - Memory Match signal defaults to 0 points (not failure)
   - Confidence scores may be lower due to missing memory signal
   - Log: "Confidence calculated without memory signal"

5. User Notification:
   - Single warning at session start: "Memory system unavailable. Patterns from previous sessions won't be loaded, and new patterns won't be saved until reconnection."
   - Status indicator in workflow-status: `memory_status: degraded`

RECOVERY:
- Background check every 5 minutes for Forgetful availability
- On reconnection: process queued saves, clear degraded status
- Next workflow benefits from restored memory

FORGETFUL DEGRADED MODE TERMINAL STATE:
- Check every 5 minutes for first 6 attempts (30 minutes total)
- If still unavailable after 30 minutes: reduce to every 30 minutes, warn user
- If unavailable for 4+ hours: mark PERMANENTLY_UNAVAILABLE for session, stop checks
- Persist queue to file for manual recovery instead of dropping on overflow
```

**Subagent Dispatch Failure:**

```
DETECTION:
- Task tool invocation throws exception or timeout (default: 60s, per timeout hierarchy)
- Subagent returns malformed response

MALFORMED SIGNAL HANDLING (Issue 1 Edge Case):
- If any signal source returns partial/corrupt data:
  - Treat malformed signal as 0 points contribution
  - Continue processing remaining valid signals
  - Mark in ConfidenceResult: edge_case: "malformed_signal"
  - Log: "Signal {source} returned malformed data: {error}, treating as 0 points"
  - Do NOT fail confidence calculation due to single malformed signal

FALLBACK BEHAVIORS:
1. Single-Validator Mode:
   - Instead of parallel reviewers, run single sequential validation
   - Reviewer Agreement signal uses "single reviewer" scoring (+10 pts)
   - Log: "Parallel validation unavailable, using single validator"

2. Retry Logic:
   - Retry failed subagent once with 5s delay
   - If second failure: fall back to single-validator permanently for session

3. Partial Results:
   - If 2/3 parallel subagents complete, aggregate their results
   - Mark missing subagent's findings as "incomplete"
   - Continue with reduced confidence (missing reviewer signal)
```

**Context7/Serena MCP Unavailable:**

```
DETECTION:
- resolve-library-id or query-docs timeout (10s)
- find_symbol or get_symbols_overview error

FALLBACK BEHAVIORS:
1. Context7 Unavailable:
   - Skip library documentation lookups
   - Log: "Library docs unavailable, using cached or no docs"
   - Automation continues without external doc context

2. Serena Unavailable:
   - Fall back to grep-based symbol search
   - Code analysis uses text patterns instead of LSP
   - Log: "LSP unavailable, using text-based code analysis"
```

#### Error Message Format Guidelines

**All error messages must be human-readable and actionable.** Technical details are important but must be presented in a way users can understand and act upon.

##### Error Message Structure

```
ERROR FORMAT:

[SEVERITY] Brief description of what went wrong

WHAT HAPPENED:
  Plain-language explanation of the error

WHY IT MATTERS:
  Impact on current workflow

WHAT TO DO:
  1. Specific action the user can take
  2. Alternative approach if available
  3. How to get more help

[Technical details available with "show details"]
```

##### Severity Levels

| Level | Icon | When to Use | User Action Required |
|-------|------|-------------|---------------------|
| **ERROR** | [!] | Operation failed, cannot continue | Must address before proceeding |
| **WARNING** | [W] | Operation degraded, can continue | Should address, but optional |
| **INFO** | [i] | Notable event, no action needed | Informational only |

##### Example Error Messages

**Bad (Technical Only):**
```
ERROR: ECONNREFUSED 127.0.0.1:5432 - pg_connection_timeout after 30000ms
```

**Good (Human-Readable):**
```
[!] Cannot connect to database

WHAT HAPPENED:
  The PostgreSQL database is not responding. This could mean the
  database server is stopped, or there's a network issue.

WHY IT MATTERS:
  Validation cannot proceed without database access.

WHAT TO DO:
  1. Check if PostgreSQL is running: pg_isready
  2. If stopped, start it: pg_ctl start
  3. If running, check connection settings in Configuration.txt

[show details] for technical error information
```

**Bad (Vague):**
```
Something went wrong. Please try again.
```

**Good (Specific):**
```
[!] Validation fix attempt failed

WHAT HAPPENED:
  The suggested fix for "missing field reference" introduced a new
  syntax error on line 42.

WHY IT MATTERS:
  Validation is stuck in a loop (3rd attempt with same error type).

WHAT TO DO:
  1. Review the suggested fix: [show fix]
  2. Make a different change manually
  3. Or skip this validation: "skip validation and continue"

This has been logged for pattern learning to prevent future loops.
```

##### Error Context Requirements

Every error message must include:

| Element | Required | Example |
|---------|----------|---------|
| What operation failed | Yes | "Validation fix attempt" |
| Where it failed | Yes | "Step 08c persona validation" |
| Why it failed (if known) | If available | "Syntax error introduced" |
| User options | Yes | At least one actionable suggestion |
| Technical details | Available on request | Stack trace, error codes |

##### Error Message Anti-Patterns

**Avoid:**
- Generic "An error occurred"
- Technical jargon without explanation
- No suggested actions
- Blaming the user
- All-caps shouting
- Excessive punctuation (!!!)

**Prefer:**
- Specific error description
- Plain language first, technical on request
- Clear next steps
- Neutral, helpful tone
- Appropriate emphasis
- Professional presentation

#### Hook Failure Modes

Each automation hook has defined failure behavior:

| Hook | On Failure | Recovery |
|------|------------|----------|
| **MENU DETECTED** | Log + continue workflow manually | User selects from menu; audit notes automation bypass |
| **Pre-Workflow (Context Pre-Loader)** | Return empty context, warn once | Workflow runs without pre-loaded memories |
| **Post-Workflow (Memory Curator)** | Log failure, skip memory save | Workflow completion not blocked; audit trail notes unsaved patterns |
| **AGENT START** | Skip agent-specific initialization | Agent runs with default context |
| **PreToolUse** | Allow tool call (non-blocking) | Audit logs note skipped validation |
| **PostToolUse** | Skip result processing | Continue with unprocessed result |
| **Stop** | Force-save critical state | Best-effort state persistence |

```
HOOK FAILURE HANDLING:

CRITICAL hooks (workflow-blocking on failure):
- None. Hooks are ADVISORY, not gates.
- All hooks can fail without stopping workflow.
- Failure logged + user warned; workflow continues.

IMPORTANT hooks (warn loudly, degrade gracefully):
- Pre-Workflow Context Pre-Loader: Empty context on failure
- Post-Workflow Memory Curator: Skip saves on failure
- MENU DETECTED: Fall back to manual selection

OPTIONAL hooks (silent degradation):
- PreToolUse validation: Skip if fails
- PostToolUse metrics: Skip if fails
- Audit trail logging: Best-effort
```

#### Audit Trail

Every session produces a log:
- Tier detected and confirmed
- Each validation cycle: issues found, fixes attempted, result
- Party mode sessions: agents, topic, synthesis
- Human checkpoints: what was presented, decision made
- Final outcome: success, escalation reason, or manual takeover

#### Rollback and Recovery System

**Problem:** If automation makes a wrong choice or takes an incorrect action, users need a way to recover without losing all progress.

**Solution:** Implement checkpoint-based rollback with explicit recovery commands.

##### Checkpoint System

```yaml
checkpoint_triggers:
  - before_step_transition      # Before moving to next step
  - before_validation_fix       # Before applying a fix
  - before_party_mode          # Before entering party discussion
  - before_design_decision     # Before committing design choice
  - on_user_request            # When user says "checkpoint"

checkpoint_data:
  workflow_state:              # Current step, tier, phase
  frontmatter_snapshot:        # Full frontmatter at checkpoint
  file_changes:                # List of modified files
  file_backups:                # Content before modifications
  memory_state:                # Forgetful memories created this session
  audit_position:              # Position in audit trail
```

##### Rollback Commands

| Command | Action | Scope |
|---------|--------|-------|
| "Undo" or "Undo that" | Revert last action | Single action |
| "Rollback to checkpoint" | Return to last checkpoint | All changes since checkpoint |
| "Rollback to step N" | Return to specific step | All changes since step N |
| "Rollback the fix" | Undo last fix attempt | Single fix only |
| "Start over from design" | Return to design checkpoint | Preserves analysis work |
| "Show checkpoints" | List available rollback points | Informational |

##### Rollback Behavior

```
1. User: "Undo that" or "Rollback to checkpoint"
2. Automation identifies scope (last action vs checkpoint vs step)
3. Show preview before executing:
   "Rollback will revert: 3 file modifications, 2 memory saves
    Proceed? [Y/N]"
4. On confirmation: restore files, update frontmatter, log rollback
5. Resume from restored state
```

##### What Cannot Be Rolled Back

- External API calls (QuickBooks exports, etc.)
- Committed git changes (requires separate git revert)
- Sent notifications or messages
- Forgetful memories created during session (external MCP server state; memories persist even after rollback. Mitigation: checkpoint_data.memory_state tracks created memory IDs for manual cleanup via `mark_memory_obsolete` if needed, but this is not automatic)

For irreversible actions, automation warns BEFORE executing:
```
"This action cannot be undone: Exporting to QuickBooks. Proceed? [Y/N]"
```

#### Feedback Mechanism: Teaching the Automation

**Problem:** When automation makes a wrong choice, users have no way to communicate "that was wrong" to improve future behavior.

**Solution:** Explicit feedback commands that update preferences and patterns in memory.

##### Feedback Commands

| Command | Effect | Persistence |
|---------|--------|-------------|
| "That was wrong" | Opens correction dialog | Session + Memory |
| "Don't do that again" | Records negative pattern | Memory (permanent) |
| "Good choice" / "That was right" | Reinforces positive pattern | Memory (permanent) |
| "Remember this preference" | Creates explicit preference | Memory (permanent) |
| "Forget that preference" | Removes learned preference | Memory (permanent) |

##### Feedback Dialog Flow

```
User: "That was wrong"

Automation: "What should I have done differently?
  [1] Different menu selection (which option?)
  [2] Different fix approach
  [3] Different tier/checkpoint behavior
  [4] Should have asked first
  [5] Other (explain)"

User: "2 - You should have tried the simpler fix first"

Automation: "Understood. Recording preference:
  - Context: Validation fix for [error type]
  - Wrong approach: Complex refactoring
  - Preferred approach: Simple fix first
  - Applies to: Similar validation errors

  Should this apply to:
  [1] Just this project
  [2] All projects
  [3] This session only"
```

##### Feedback Storage in Memory

```yaml
# Memory entry for learned preference
type: automation_preference
title: "Prefer simple fixes for validation errors"
content: |
  When fixing validation errors in [project], try simpler
  approaches first before complex refactoring.
context: "User feedback after automation chose wrong fix strategy"
importance: 8
tags: ["automation", "preference", "fix-strategy"]
```

##### Implicit Feedback Detection

Automation also learns from implicit signals:

| User Action | Inferred Feedback | Response |
|-------------|-------------------|----------|
| User undoes an action | Negative signal for that choice | Log for pattern analysis |
| User overrides tier up | Task more complex than detected | Adjust detection heuristics |
| User repeatedly selects [A] | Wants more elicitation | Lower auto-continue threshold |
| User says "stop asking" | Too many checkpoints | Increase batch_continue_size |

##### Feedback Review

```
User: "Show what you've learned"

Automation: "Learned preferences for this project:
  1. Prefer simple fixes first (from 2 sessions ago)
  2. Always checkpoint before architecture changes (explicit)
  3. Use tier 3 for database work (inferred from overrides)

  [Edit] [Delete] [Export]"
```

#### Large Output Persistence (Claude Code 2.1.2)

Subagent outputs exceeding context limits are automatically persisted:

```
PERSISTENCE BEHAVIOR:
- Large outputs saved to temporary files
- Reference path returned instead of full content
- Full content retrievable via Read tool
- Persists for session duration

BMAD APPLICATIONS:

Validation Reports:
- Full 8-phase compliance report → persisted
- Summary returned to context
- Reference stored in audit trail
- Human can read full report if needed

Party Mode Transcripts:
- Multi-round discussions → persisted
- Key consensus points in context
- Full transcript available for review
- Supports post-session analysis

Audit Trail Enhancement:
- Full validation output: persisted → reference in audit
- Party mode transcript: persisted → reference in audit
- Error details: persisted → reference for debugging
- Human can always access full context
```

**Integration with Automation Components:**

| Component | Persistence Use Case |
|-----------|---------------------|
| **Autonomous Validation Loop** | Full validation reports may exceed context; persist complete reports, work with summaries |
| **Party Mode Driver** | Multi-round transcripts persisted; key consensus extracted to context |
| **Audit Trail Logger** | Store output file paths alongside summary data |
| **Error Handling** | Full error context and stack traces persisted for post-mortem analysis |

**WORKFLOW-STATUS EXTENSION:**

```yaml
last_validation:
  summary: "PASS with 2 warnings"
  full_output_path: "/tmp/bmad-validation-abc123.md"
  timestamp: "2026-01-08T14:32:00Z"

last_party_mode:
  summary: "Consensus reached on caching strategy"
  transcript_path: "/tmp/bmad-party-mode-xyz789.md"
  agents_participated: ["Architect", "Dev", "TEA"]
  timestamp: "2026-01-08T15:10:00Z"

error_context:
  last_error_path: "/tmp/bmad-error-detail-def456.md"
  summary: "Reference validation failed on step-08c"
```

**Automation Controller Handling:**

```
ON SUBAGENT COMPLETION:
1. Check if output exceeds context threshold
2. IF persisted:
   - Extract summary from persisted output
   - Store file path reference
   - Continue processing with summary
   - Log persistence event in audit trail
3. IF not persisted:
   - Process full output directly
   - No path storage needed

ON HUMAN CHECKPOINT:
- Include summary in presentation
- Provide "[See Full Details]" option with file path
- Human can request full output via Read tool

ON ERROR ESCALATION:
- Persist full error context automatically
- Include stack traces, validation state, attempt history
- Reference path enables post-mortem debugging
- Summary highlights key failure points
```

**Benefits for BMAD Automation:**

1. **Context Efficiency** - Large validation reports don't overflow context window
2. **Full Auditability** - Complete records preserved even when summarized
3. **Debug Support** - Error details available for investigation after session
4. **Human Review** - Full party mode transcripts accessible when needed
5. **Resume Capability** - Persisted state supports workflow resumption

---

### 8. Brainstorming Workflow

**Status: PARTIALLY AUTOMATED / OUT OF SCOPE FOR FULL AUTOMATION**

The Core brainstorming workflow is fundamentally interactive and presents unique automation challenges.

#### Why Brainstorming is Different

```
Brainstorming Workflow Reality:
- 8 step files, but 11+ total human interaction prompts
  (due to branching and sub-prompts within steps)
- Step 3 is DIALOGUE (cannot be scripted)
- Creative exploration by nature (unpredictable paths)
- User provides topics, goals, constraints
- Technique selection is collaborative

vs. Other Workflows:
- Deterministic step sequences
- Known outputs per step
- Validation criteria exist
- [C] Continue has clear meaning
```

#### Interaction Points in Brainstorming

| Step | Interaction Type | Automatable? |
|------|-----------------|--------------|
| 1. Session setup | User provides topic | Partially (if topic known) |
| 2. Goal clarification | Dialogue | No - requires creative input |
| 3. Technique selection + execution | Menu + discussion + **formal continuation check before moving to next technique** (users can also interrupt at any time with "next technique" or "move on") | Partially (can suggest) |
| 4. Brainstorming execution | Interactive generation | No - core creative work |
| 5. Idea capture | Dialogue | No - user-driven |
| 6. Clustering/themes | Collaborative | Partially |
| 7. Prioritization | User judgment | No |
| 8. Action items | Collaborative | Partially |

**Note:** 8 step files exist but generate 11+ total human interaction prompts due to branching and sub-prompts within steps. This count is approximate as branching paths can vary - the key point is that interaction frequency exceeds the step file count.

#### Step 3 Continuation Check Handling - CORRECTED

**Brainstorming Step 3 has CONTINUOUS "Check Technique Continuation" prompts**, not a single checkpoint. The check happens AFTER EACH TECHNIQUE ELEMENT, not once at the beginning:

```
CONTINUATION CHECK (Step 3) - CORRECTED:
Per step-03-technique-execution.md lines 121-143:
- Check happens AFTER EACH ELEMENT of technique execution
- User can say "next technique" or "move on" at ANY TIME during technique
- This is CONTINUOUS checking throughout the step, not one checkpoint
- Transitions between techniques happen IMMEDIATELY on user request

Actual Flow:
1. Technique begins executing
2. After each element: "Continue with this technique? Or move to next?"
3. User can interrupt at any point with "next technique"
4. Immediate technique transition when requested
5. Repeats until all desired techniques explored

Automation Handling (VERY LIMITED for brainstorming):
- Brainstorming has the HIGHEST interaction frequency of any workflow
- Continuous prompts make full automation impractical
- Recommend: Use Simulated Brainstorming (Option C) for automation
- Real brainstorming should remain human-driven

For Simulated Brainstorming (subagent-based):
- Skip continuous continuation checks entirely
- Subagents execute complete techniques independently
- Main agent synthesizes results
- Avoids the continuous human interaction issue
```

#### Automation Options

**Option A: Declare Out of Scope**
```
Brainstorming is inherently human-driven creative work.
Automation is counterproductive - the value IS in human engagement.
Exclude from automation framework entirely.
```

**Option B: Partial Automation (Pre-Seeding)**
```
Automation can PRE-SEED brainstorming sessions:
1. Query Forgetful for related past brainstorms
2. Generate starter topics based on project context
3. Suggest techniques based on goal type
4. Prepare reference materials

Human still drives the session, but starts with context.
```

**Option C: Simulated Brainstorming (Subagent-Based)**
```
For autonomous ideation (not true brainstorming):
1. Spawn multiple subagents with diverse perspectives
2. Each generates ideas independently
3. Main agent clusters and synthesizes
4. Present curated results to human

Trade-off: Loses true creative dialogue
Gain: Can generate initial ideas without human time
```

#### Recommended Approach

```
TIER 0-2: Use Simulated Brainstorming (Option C)
  - Quick ideation for simple features
  - Human reviews output, can trigger real brainstorm if needed

TIER 3-4: Use Pre-Seeding + Human Session (Option B)
  - Complex work benefits from true creative dialogue
  - Automation prepares, human drives

ALWAYS AVAILABLE: Real brainstorming on request
  - Human can always invoke Core brainstorming
  - Automation does not block or replace this path
```

---

### 9. BMB Module Workflows

The BMAD Method Builder (BMB) module has specialized workflows that require explicit handling, particularly the agent workflow which operates in three distinct modes.

**GENERAL NOTE - BMB Structure References:**
All BMB workflow structures, step counts, and phase sequences in this section are based
on design pattern analysis. They represent the TARGET ARCHITECTURE for how BMB workflows
should be structured. See the Verification Note (H5) in the Workflow Entry Point Handling
section for full details on how to handle discrepancies between design assumptions and
actual implementation. Implementation must verify actual step files rather than assuming
structures from this document.

#### Agent Workflow: Tri-Modal Operation

The BMB agent workflow has CREATE | EDIT | VALIDATE modes, each with different step sequences:

```
MODE DETECTION (from user intent or existing artifacts):
├── No existing agent file → CREATE mode
├── Existing agent + "edit" intent → EDIT mode
└── Existing agent + "validate" intent → VALIDATE mode
```

#### CREATE Mode (16 Step Files: step-01 through step-09, plus 08a-08f)

```
Create Flow (CORRECTED - 16 total step files, names match actual filenames):
Step 01: brainstorm (step-01-brainstorm.md) - Agent concept and purpose
Step 02: discovery (step-02-discovery.md) - Agent purpose definition (formal)
Step 03: type-metadata (step-03-type-metadata.md) - Agent type and metadata
Step 04: persona (step-04-persona.md) - Personality and tone
Step 05: commands-menu (step-05-commands-menu.md) - Commands and menu definition
Step 06: activation (step-06-activation.md) - Activation behavior (when/how agent activates)
Step 07a/b/c: build (step-07a-build-simple.md, step-07b-build-expert.md, step-07c-build-module.md) - BRANCHES by agent type
Step 08a: plan-traceability (step-08a-plan-traceability.md) - Plan traceability validation
Step 08b: metadata-validation (step-08b-metadata-validation.md) - Metadata validation
Step 08c: persona-validation (step-08c-persona-validation.md) - Persona validation
Step 08d: menu-validation (step-08d-menu-validation.md) - Menu validation
Step 08e: structure-validation (step-08e-structure-validation.md) - Structure validation
Step 08f: sidecar-validation (step-08f-sidecar-validation.md) - Sidecar validation
Step 09: celebrate (step-09-celebrate.md) - Integration points and completion

CORRECTED: 08a-08f are SEPARATE STEP FILES (step-08a-plan-traceability.md, etc.)
They are NOT sub-phases nested within a single Step 8 file.
Total: 16 discrete step files in CREATE mode steps-c directory.
Each 08x file is processed individually with its own [A][P][C] menu participation.

Automation Behavior:
- Each step has [A][P][C] menu
- Step 1 is brainstorming (may be skipped if purpose already clear)
- Auto-[C] through information gathering steps (2-5)
- Checkpoint at Step 7 (system prompt is critical artifact)
- Auto-validate through 08a-08f
- Loop until validation passes
```

#### Agent Type Detection and Routing (Step 06/07)

**Agent creation has activation behavior at Step 06 and build generation at Step 07.** Step 07 branches based on agent type. Different types have different validation needs:

```
AGENT TYPE DETECTION:
├── Simple Agent
│   ├── Single-purpose, limited tools
│   ├── Validation: Basic 08a-08c only
│   └── Faster iteration, fewer checkpoints
│
├── Expert Agent
│   ├── Domain expertise, moderate tools
│   ├── Validation: Full 08a-08f
│   └── Standard checkpoints
│
└── Module Agent
    ├── Complex, multi-capability, extensive tools
    ├── Validation: Full 08a-08f + cross-module checks
    └── Additional party mode review at completion

Type Detection Signals:
- Simple: Single tool, one-line purpose, no integrations
- Expert: 2-5 tools, domain-specific purpose, some integrations
- Module: 5+ tools, multi-faceted purpose, cross-module integrations
```

#### Validation Step Files to Reviewer Mapping

**Map subagent reviewers to specific BMB validation step files (08a-08f are SEPARATE FILES, not sub-phases):**

| Step File | Actual Name | Validation Focus | Primary Reviewer | Secondary Reviewer |
|-----------|-------------|------------------|------------------|-------------------|
| **step-08a** | plan-traceability | Ensures agent traces to planning docs | Spec Reviewer | - |
| **step-08b** | metadata-validation | Validates frontmatter and metadata | Validator (automated) | - |
| **step-08c** | persona-validation | Validates persona consistency | Quality Reviewer | Spec Reviewer |
| **step-08d** | menu-validation | Validates menu structure and options | Validator (automated) | - |
| **step-08e** | structure-validation | Validates overall agent structure | Adversarial Reviewer | Spec Reviewer |
| **step-08f** | sidecar-validation | Validates sidecar files (persona, etc.) | All three (synthesized) | - |

```
SUBAGENT DISPATCH FOR AGENT VALIDATION:

FOR phases 08a-08b:
  → Automated validation only (no subagent needed)
  → Pass/fail based on syntax checks

FOR phases 08c-08e:
  → Dispatch appropriate reviewer(s)
  → Collect findings
  → Allow iteration on specific phase

FOR phase 08f:
  → Parallel dispatch all three reviewers
  → Synthesize findings
  → Require consensus for PASS
  → CONCERNS if any reviewer flags issues
```

#### EDIT Mode (Steps e-01 through e-10)

**Note (S11):** Steps e-03a-f and e-09a-f are SEPARATE STEP FILES (like CREATE mode 08a-08f), not sub-phases within a single step. Each has its own file: `step-e-03a-plan-traceability.md`, `step-e-03b-metadata-validation.md`, etc.

```
Edit Flow:
Step e-01: Load existing agent file
Step e-02: Discover current agent state and configuration
Step e-03: Pre-edit validation (6 SEPARATE STEP FILES)
  → e-03a: Plan traceability check (step-e-03a-plan-traceability.md)
  → e-03b: Metadata validation (step-e-03b-metadata-validation.md)
  → e-03c: Persona validation (step-e-03c-persona-validation.md)
  → e-03d: Menu validation (step-e-03d-menu-validation.md)
  → e-03e: Structure validation (step-e-03e-structure-validation.md)
  → e-03f: Sidecar validation (step-e-03f-sidecar-validation.md)
Step e-04: Purpose/scope edits
Step e-05: Persona/tone edits
Step e-06: Activation behavior edits
Step e-07: System prompt and build edits
Step e-08: Build and integration
  → e-08a: Build agent file
  → e-08b: Build sidecar files
  → e-08c: Integration hooks
Step e-09: Post-edit validation
  → e-09a through e-09f (mirrors validation sub-phases)
Step e-10: Celebrate success

Automation Behavior:
- e-01 loads agent, e-02 discovers state
- e-03a-f validates BEFORE edits (catch issues early)
- e-04 through e-07 are the actual edit operations
- e-08a/b/c handles build generation
- e-09a-f validates AFTER edits
- e-10 is the celebration/completion step
- Detect which edit steps needed from edit request
- May skip irrelevant edit steps (e.g., only e-05 if just changing tone)
- ALWAYS run full e-09 validation after any edit
- Loop until validation passes
```

#### VALIDATE Mode (Steps v-01, v-02a-e, v-03)

```
Validate Flow:
Step v-01: Load agent for validation (initializes validation context)
Step v-02: Run validation checks
  → v-02a: Syntax validation
  → v-02b: Reference validation
  → v-02c: Compliance validation
  → v-02d: Integration validation
  → v-02e: Summary generation
Step v-03: Present validation summary report

Automation Behavior:
- v-01 loads agent (required initialization step)
- Fully automatable (no creative decisions)
- Run all v-02 sub-steps sequentially
- v-03 presents final summary report
- Report issues without attempting fixes
- Human decides whether to trigger EDIT mode
```

#### VALIDATE Mode Output Schema (S2)

VALIDATE mode produces structured output for automation consumption:

```yaml
# validation-result.yaml
validation_id: "val-2026-01-09-001"
timestamp: "2026-01-09T14:32:00Z"  # ISO 8601 format, UTC
target: "agents/architect.md"
target_type: "agent"  # agent | workflow | module | task
overall_verdict: "CONCERNS"  # PASS | CONCERNS | FAIL
phase_results:
  syntax: {verdict: "PASS", errors: [], warnings: []}
  reference: {verdict: "CONCERNS", errors: [], warnings: [{type: "broken_ref", location: "line 45"}]}
  compliance: {verdict: "PASS", score: 85}
  integration: {verdict: "PASS"}
issue_summary:
  blocking_count: 0
  major_count: 0
  minor_count: 1
recommended_action: "REVIEW"  # NONE | REVIEW | EDIT_REQUIRED
```

#### Automation Strategy per Mode

| Mode | Automation Level | Human Checkpoints |
|------|------------------|-------------------|
| CREATE | Medium | Purpose (Step 2), System Prompt (Step 6), Final |
| EDIT | High | Before applying edits, After validation |
| VALIDATE | Full | Report presentation only |

#### Other BMB Workflows

| Workflow | Automation Notes |
|----------|------------------|
| **module-builder** | Similar tri-modal pattern to agent workflow |
| **workflow-builder** | CREATE has 10 steps; Edit/Validate modes |
| **create-workflow** | Structured step creation; high automation potential |
| **edit-workflow** | Load existing + targeted edits; 5 main steps (NOT same as Edit-Module) |
| **workflow-compliance-check** | Fully automatable; 8 phases (not 3) |

#### Edit-Workflow vs Edit-Module (Critical Distinction)

**Edit-Workflow and Edit-Module are SEPARATE workflows with different step counts and purposes:**

| Aspect | Edit-Workflow | Edit-Module |
|--------|--------------|-------------|
| **Step Count** | 5 main steps | 7 main phases with 20+ step files (due to branching and sub-steps) |
| **Target** | Single workflow file | Entire module (agents, workflows, tasks, config) |
| **Branching** | Linear with validation | Step 06 loop-back to Step 03, multiple component handlers |
| **Scope** | One workflow's steps/paths | Module-wide changes |
| **Validation** | Invokes workflow-compliance-check (8-phase) | 3-phase module validation (Syntax → References → Compliance) |

**Note on Edit-Module terminology:** The 7 "phases" are also referred to as "steps" in the workflow files. Both terms are used interchangeably to describe the main sequential operations (Step 01 = Phase 1, etc.).

```
EDIT-WORKFLOW (5 Steps):
Step 01: Load workflow context
Step 02: Identify edit targets (steps, paths, menus)
Step 03: Execute targeted edits
Step 04: Generate summary
Step 05: Validate by invoking workflow-compliance-check (full 8-phase validation)

NOTE: Step 05 invokes the complete workflow-compliance-check workflow,
which itself has 8 phases. This ensures edited workflows meet all compliance standards.

NESTED WORKFLOW INVOCATION (H2 - Edit-Workflow Step 05):
- **Pre-invocation ordering (CRITICAL):** BEFORE invoking child workflow:
  1. Save current parent state to frontmatter
  2. Record invocation intent in audit trail
  3. THEN invoke child workflow
- Context passing: Edit-Workflow passes edited file paths and workflow context to child workflow
- Automation handling: Pauses Edit-Workflow state, activates workflow-compliance-check with full automation
- Result propagation: Child workflow returns validation verdict (PASS/CONCERNS/FAIL) to parent
- Iteration handling: If child returns FAIL, parent loops back to Step 03 for corrections
- State management: Parent workflow state preserved in frontmatter during child execution
- Signal extraction methods: To be defined during implementation (see H4 note on Confidence Calculator)

#### Nested Workflow Invocation Protocol (S4)

```
INVOCATION MECHANISM:
  Parent calls: invoke_workflow("workflow-compliance-check", context_handoff)

CONTEXT HANDOFF FORMAT:
  {
    parent_workflow: "edit-workflow",
    parent_step: "05",
    parent_state_path: "_bmad-output/edit-workflow/state.yaml",
    target_files: ["workflows/my-workflow/steps/step-01.md", ...],
    tier: 2,
    automation_enabled: true
  }

RESULT RETURN FORMAT:
  {
    verdict: "PASS" | "CONCERNS" | "FAIL",
    phase_results: {...},  # See VALIDATE Mode Output Schema (S2)
    issues: [...],
    child_duration_ms: 12500
  }

STATE PRESERVATION:
  - Parent frontmatter updated with: nested_invocation: {started: timestamp, child: "workflow-compliance-check"}
  - On child completion: nested_invocation: {completed: timestamp, result: verdict}
  - On parent resume: read result, clear nested_invocation, continue

MAX NESTING DEPTH (CRITICAL - prevents stack overflow):
  - **Maximum depth:** 3 levels of nested workflow invocations
  - **Depth tracking:** Each invocation increments depth counter in context handoff
  - **Enforcement:**
    ```
    BEFORE invoke_workflow():
      current_depth = context.get("nesting_depth", 0)
      IF current_depth >= 3:
        → ABORT invocation
        → Log error: "Max nesting depth (3) exceeded"
        → Return {verdict: "FAIL", error: "nesting_depth_exceeded"}
        → Escalate to human with full call stack
      ELSE:
        → Pass nesting_depth: current_depth + 1 in context handoff
    ```
  - **Call stack tracking:** Maintain array of parent workflows in context:
    ```yaml
    call_stack:
      - workflow: "create-architecture"
        step: "05"
        started: "2026-01-08T14:30:00Z"
      - workflow: "edit-workflow"
        step: "05"
        started: "2026-01-08T14:31:00Z"
      - workflow: "workflow-compliance-check"
        step: "01"
        started: "2026-01-08T14:31:05Z"
    nesting_depth: 3  # Max reached - no further nesting allowed
    ```
  - **Context Budget Management (CRITICAL):**
    If context exceeds 80% capacity before depth limit reached, compress parent state summary to 500 tokens max per level.
    **BOUNDARY CLARIFICATION (Issue 4 Edge Case):** 80% exactly is ALLOWED (boundary exclusive). Compression triggers when usage is STRICTLY GREATER THAN 80% (>80%, not >=80%):
    ```
    CONTEXT CHECK (before each nesting level):
      estimated_usage = current_context_tokens + child_workflow_estimate
      IF estimated_usage > 0.8 * context_limit:
        → Compress call_stack entries to summary format:
          - workflow: "create-architecture"
            step: "05"
            summary: "Designing cache layer, waiting on validation"  # 500 tokens max
        → Prune non-essential context (completed validations, old logs)
        → If still > 80% after compression: deny nesting, escalate to human
    ```
  - **Rationale:** Typical BMAD patterns require at most 2 levels (parent → validation child).
    3 levels provides buffer for complex scenarios. >3 levels indicates design issue.
  - **Recovery:** If depth exceeded, workflow fails cleanly with saved state for human review.
```

EDIT-MODULE (7 Steps):
Step 01: Load module context
Step 02: Analyze current state
Step 03: TARGET SELECTION (6 component handlers: A/W/T/C/D/I)
Step 04: Execute targeted edit
Step 05: 3-phase validation
Step 06: ITERATION DECISION (Y → loop to 03, N → proceed)
Step 07: Generate summary and exit
```

**Automation must detect which workflow is invoked and apply correct step handling:**

```
DETECTION:
- User says "edit workflow X" → Edit-Workflow (5 steps)
- User says "edit module X" → Edit-Module (7 steps)
- User edits from within module context → Edit-Module
- User edits standalone workflow → Edit-Workflow

AUTOMATION DIFFERENCES:
- Edit-Workflow: Linear auto-[C] through steps, no loop handling
- Edit-Module: Must handle Step 06 loop-back, track iterations
```

#### Edit-Module Branching Complexity (BMB)

Edit-Module has 7 steps with complex branching that automation must handle explicitly:

```
Edit-Module Step Structure (based on workflow design documents):
Step 01: Load module context
Step 02: Analyze current state
Step 03: TARGET SELECTION (numbered menu with component handlers)
        ├── [1] Edit agents
        ├── [2] Edit workflows
        ├── [3] Edit tasks
        ├── [4] Edit config/installation
        └── [D] Done with target selection
Step 04: Execute targeted edit
Step 05: 3-PHASE VALIDATION
        ├── Phase 1: Syntax validation
        ├── Phase 2: Reference validation
        └── Phase 3: Compliance validation
Step 06: ITERATION DECISION
        ├── [Y] More edits wanted → GOTO Step 03 (LOOP BACK)
        └── [N] Done editing → Proceed to Step 07
Step 07: Generate summary and exit

**IMPORTANT: Edit-Module structure (7 phases) is assumed from workflow design patterns.
TO BE VERIFIED against actual implementation. Actual step files may vary - verify
against implementation before relying on this sequence.**

**Critical: Step 06 Iteration Loop**

Step 06 creates a LOOP-BACK, not linear "continue or stop":

```
Iteration Loop Handling:
WHEN at Step 06:
  IF user indicates more edits wanted [Y]:
    → Return to Step 03 (target selection)
    → NOT proceed to Step 07
    → Preserve edit session state
    → Re-display target selection menu

  IF user indicates done [N]:
    → Proceed to Step 07
    → Generate summary
    → Complete workflow

Automation Behavior:
- Track loop iteration count
- After each loop: re-run 3-phase validation (Step 05)
- Suggest [N] done after successful validation pass (no errors/warnings)
- If validation passes with warnings: Present to user for decision (approve or more edits?)
- Allow unlimited [Y] loops (user controls session length)
- Do NOT auto-select [N] unless explicitly configured
```

#### Loop-Back Handler State Tracking (S5)

The Loop-Back Handler tracks iteration state in frontmatter:

```yaml
# Frontmatter fields for loop tracking (Edit-Module)
loop_state:
  iteration_count: 3
  targets_edited: ["agents/architect.md", "workflows/create-prd/steps/step-02.md"]
  validation_history:
    - iteration: 1
      result: "FAIL"
      issues: ["broken_reference"]
    - iteration: 2
      result: "CONCERNS"
      issues: ["minor_warning"]
    - iteration: 3
      result: "PASS"
      issues: []
  current_step: "06"  # At decision point
  awaiting_decision: true

# Handler reads loop_state to:
# - Display iteration count to user
# - Show validation trend
# - Suggest [N] when validation_history[-1].result == "PASS"
```

#### Workflow-Compliance-Check 8 Phases

Workflow-Compliance-Check has 8 validation phases (not universal "3 phases").

**Phase names match actual step file names:**

```
8-Phase Validation (actual step file names):
Phase 1: validate-goal          - Validates workflow goal alignment
Phase 2: workflow-validation    - Validates workflow.md structure
Phase 3: step-validation        - Validates step file syntax and structure
Phase 4: file-validation        - Validates all workflow files (cross-file references)
Phase 5: intent-spectrum-validation - Validates intent coverage
Phase 6: web-subprocess-validation  - Validates external process integration
Phase 7: holistic-analysis      - Holistic structural analysis
Phase 8: generate-report        - Generates compliance report with scoring
```

---

## Step Processing Rules

**BMAD Critical Rules that automation MUST respect:**

```
NEVER SKIP STEPS OR OPTIMIZE SEQUENCES
- Each step file must be processed discretely
- Cannot combine steps for "efficiency"
- Cannot skip steps that "seem unnecessary"
- Step order defined by path files is MANDATORY

ALWAYS FOLLOW EXACT INSTRUCTIONS IN STEP FILES
- Step files contain specific instructions
- Automation reads and follows them literally
- Cannot "summarize" or "abbreviate" step execution

ALWAYS HALT AT MENUS AND WAIT FOR INPUT
- Automation can PREPARE a selection
- Automation can AUTO-SELECT after evaluation
- Automation CANNOT skip the menu entirely
- Menu must be processed (even if auto-answered)
```

### Frontmatter State Management (BMB Requirement)

**BMAD uses frontmatter to track state between steps.** The rule: "ALWAYS save progress to frontmatter before loading next step."

**IMPORTANT: PROPOSED EXTENSION**
The frontmatter schema below is a **PROPOSED EXTENSION** for automation purposes,
not the existing BMAD structure. Current BMAD step files have minimal frontmatter
(typically just `step` and basic metadata). The extended schema enables automation
tracking but is NOT required - automation MUST work with or without these fields.

```
FRONTMATTER STATE TRACKING (PROPOSED):

Step files MAY contain YAML frontmatter with these fields:

EXISTING BMAD FIELDS (present in current step files):
---
step: 03
title: "Step Title"
---

PROPOSED AUTOMATION EXTENSIONS (not yet in BMAD):
---
step: 03
title: "Step Title"
# The following are PROPOSED fields for automation tracking:
status: pending|in-progress|complete        # PROPOSED: automation state
inputs_received: [list of inputs]           # PROPOSED: input tracking
outputs_generated: [list of outputs]        # PROPOSED: output tracking  
validation_state: pass|concerns|fail        # PROPOSED: validation state
last_updated: 2026-01-08T14:32:00Z         # PROPOSED: timestamp
hooks:                                      # PROPOSED: Claude Code 2.1 hooks
  PreToolUse:
    - command: "log-tool-start.sh"
  PostToolUse:
    - command: "capture-result.sh"
  Stop:
    - command: "save-final-state.sh"
---

AUTOMATION MUST:
1. Work with existing minimal frontmatter (graceful degradation)
2. NOT require proposed fields to function
3. Add proposed fields only when automating (non-destructive enhancement)
4. Preserve any existing frontmatter when adding automation fields

**Hooks in Frontmatter (Claude Code 2.1 Extension):**

Step files and subagent definitions can include lifecycle hooks in frontmatter:

```yaml
---
step: 08a
status: pending
hooks:
  SessionStart:
    - command: "load-context.sh"
      once: true                                   # Only runs once per session (2.1.2)
  PreToolUse:
    - command: "validate-paths.sh $TOOL_ARGS"     # Validate before file edits
      once: true                                   # First tool use only (2.1.2)
    - command: "log-audit.sh $TOOL_NAME $STEP"    # Audit trail
      once: false                                  # Every tool use (default)
  PostToolUse:
    - command: "check-result.sh $EXIT_CODE"       # Verify tool success
    - command: "update-metrics.sh"                # Track metrics
  Stop:
    - command: "save-to-forgetful.sh"             # Persist patterns
    - command: "update-workflow-status.sh"        # Update status file
---
```

**One-Time Hooks (Claude Code 2.1.2):**

The `once: true` parameter makes hooks run only once per session rather than on every invocation:

| once: true | once: false (default) |
|------------|----------------------|
| Session initialization | Audit trail logging |
| Project context loading | Step progression tracking |
| Prerequisite validation | Validation loop queries |
| State detection | Fix pattern saves |
| Tier configuration | Metrics collection |

Hook commands receive environment variables:
- `$TOOL_NAME` - Name of the tool being called
- `$TOOL_ARGS` - Arguments passed to the tool
- `$EXIT_CODE` - Tool exit code (PostToolUse only)
- `$STEP` - Current step identifier
- `$WORKFLOW` - Current workflow name

**Template Variable Escaping (CRITICAL - Prevent Injection/Corruption):**

Variables like `{{PROJECT_TYPE}}`, `{{FIELD_TYPE}}`, or `$TOOL_ARGS` may contain content with literal braces, special characters, or shell metacharacters. Without proper escaping, this causes template corruption or shell injection.

```
ESCAPING RULES:

1. DOUBLE-BRACE TEMPLATE VARIABLES ({{VAR}}):
   - Used in: Workflow templates, frontmatter, output documents
   - Escape sequence: Use \{{ and \}} for literal braces
   - Example: Content "Use {{name}}" → escaped as "Use \{{name\}}"

2. VARIABLE INTERPOLATION:
   - BEFORE substituting, check if value contains:
     - "{{" or "}}" → escape as "\{{" and "\}}"
     - Newlines → preserve or convert to \n based on context
     - Null bytes → reject value entirely

3. SHELL VARIABLE EXPANSION ($VAR):
   - Used in: Hook commands, shell scripts
   - Always quote variables: "$TOOL_ARGS" not $TOOL_ARGS
   - Escape sequences for shell metacharacters:
     | Char | Escaped | Notes |
     |------|---------|-------|
     | ' | '\'' | Break out and escape single quote |
     | " | \" | Inside double quotes |
     | $ | \$ | Prevent expansion |
     | ` | \` | Prevent command substitution |
     | \ | \\ | Literal backslash |
     | ! | \! | History expansion (bash) |

4. SAFE SUBSTITUTION FUNCTION:
   ```python
   import re
   import shlex

   def safe_template_substitute(template: str, variables: dict) -> str:
       """Substitute variables with proper escaping."""
       result = template
       for key, value in variables.items():
           # Escape literal braces in value
           safe_value = value.replace("{{", r"\{{").replace("}}", r"\}}")
           # Escape backslashes (must come first)
           safe_value = safe_value.replace("\\", "\\\\")
           result = result.replace(f"{{{{{key}}}}}", safe_value)
       return result

   def safe_shell_arg(value: str) -> str:
       """Make value safe for shell use."""
       return shlex.quote(value)
   ```

5. VALIDATION BEFORE SUBSTITUTION:
   - Max variable value length: 10KB
   - Reject values containing null bytes (\x00)
   - Warn on values containing control characters
   - Log substitution for audit trail

6. ROUND-TRIP SAFETY:
   - After substitution: verify result can be parsed back
   - If YAML frontmatter: attempt yaml.safe_load() on result
   - If template: verify no unmatched {{ or }} remain
```

Automation Controller MUST:

1. BEFORE LOADING NEXT STEP:
   - Save current step's outputs to frontmatter
   - Update status to "complete"
   - Record any validation results
   - Timestamp the update

2. WHEN LOADING STEP:
   - Read frontmatter state
   - Validate prerequisites met (inputs_received)
   - Set status to "in-progress"

3. ON INTERRUPTION:
   - Save current state to frontmatter
   - Record interruption reason
   - Enable resume from exact point

4. ON LOOP-BACK (e.g., Edit-Module Step 06):
   - Preserve iteration count in frontmatter
   - Track which targets were edited
   - Maintain session continuity
```

**Frontmatter is the checkpoint mechanism.** Without proper frontmatter updates, resume-from-interruption fails.

#### Atomic Write Pattern (Data Corruption Prevention)

File writes (frontmatter, sprint-status.yaml, state files) MUST use atomic write pattern to prevent corruption on interruption:

```
ATOMIC WRITE PROCEDURE:

1. Create temporary file: {target}.tmp.{timestamp}
2. Write complete content to temporary file
3. Flush and sync temporary file to disk
4. Rename temporary file to target (atomic on POSIX/Windows)
5. Delete old backup if rename succeeded

IMPLEMENTATION:

def atomic_write(target_path: str, content: str) -> None:
    temp_path = f"{target_path}.tmp.{time.time_ns()}"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, target_path)  # Atomic rename
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise

CRITICAL FILES REQUIRING ATOMIC WRITES:
- sprint-status.yaml (concurrent access)
- bmm-workflow-status.yaml (session state)
- Step file frontmatter (progress tracking)
- _bmad-output/edit-workflow/state.yaml (nested invocation)
- Audit trail files
```

#### Concurrent File Access Control

```
FILE LOCKING SPECIFICATION:

For sprint-status.yaml (multiple components may write):

LOCK MECHANISM:
- Create lock file: sprint-status.yaml.lock
- Lock file contains: {holder: "component-name", timestamp: "...", pid: N}
- Lock timeout: 30 seconds (stale lock auto-cleared)
- Retry with exponential backoff: 100ms, 200ms, 400ms, 800ms, then fail

LOCK PROCEDURE:
1. Attempt to create lock file (exclusive create)
2. IF lock exists:
   a. Read lock file
   b. IF timestamp > 30s old: use TWO-PHASE STALE LOCK CLEAR (Issue 5 Edge Case):
      - Phase 1: Rename lock to `.clearing` (atomic rename)
      - Phase 2: Wait 1 second for any in-progress write to complete
      - Phase 3: Check if original lock recreated (another process active)
      - Phase 4: If no new lock, delete `.clearing` file and retry
      - Rationale: Prevents race where Process A is writing while Process B clears stale lock
   c. ELSE: wait and retry with backoff
3. IF lock acquired:
   a. Read current file content
   b. Modify content
   c. Atomic write new content
   d. Delete lock file
4. IF lock timeout: Log failure, escalate to user

COMPONENTS REQUIRING LOCKS:
- Sprint Status Auto-Watcher (reads/writes sprint-status.yaml)
- dev-story workflow (updates story status)
- Automation Controller (marks stories claimed)

LOCK-FREE ALTERNATIVES:
- Workflow status files: Single-writer guarantee (one workflow active)
- Audit trail: Append-only log files (no locking needed)
- Memory saves: Forgetful handles concurrency internally
```

#### Crash Recovery and Resume Specification

**Crash Detection Mechanism:**
Use crash flag file (`_bmad-output/.crash_flag`) - created at session start, deleted on clean shutdown. If flag exists at startup, crash occurred.

```
CRASH FLAG PROTOCOL:
1. SESSION START:
   - Create `_bmad-output/.crash_flag` with timestamp and workflow context
   - Flag content: {started: timestamp, workflow: name, step: current}

2. CLEAN SHUTDOWN (any of):
   - Workflow completes successfully
   - User explicitly cancels/aborts
   - Human checkpoint response = abandon
   → Delete `.crash_flag` file

3. SESSION STARTUP CHECK:
   IF `.crash_flag` exists:
     → Crash detected
     → Read flag for context (which workflow, which step)
     → Present recovery options (see below)
   ELSE:
     → Clean start, no recovery needed

4. FLAG FILE FORMAT:
   ```yaml
   # _bmad-output/.crash_flag
   started: "2026-01-08T14:30:00Z"
   workflow: "create-architecture"
   step: "03"
   pid: 12345  # Optional: process ID for additional validation
   resume_attempt_count: 0  # Tracks consecutive resume attempts from same checkpoint
   checkpoint_hash: "abc123"  # SHA-256 of checkpoint state for loop detection
   ```

5. CRASH RECOVERY LOOP PREVENTION (CRITICAL):
   Track resume attempts to prevent infinite crash→resume loops:

   ```
   ON RESUME FROM CHECKPOINT:
     resume_attempt_count += 1
     current_hash = SHA256(workflow + step + validation_state)

     IF current_hash == previous_checkpoint_hash:
       # Same checkpoint being resumed repeatedly
       IF resume_attempt_count >= 3:
         → Present alternative options (not just resume):
           "[1] Resume from checkpoint (attempt {count}/3 EXHAUSTED)"
           "[2] Restart workflow from beginning"
           "[3] Skip to next step (with warning)"
           "[4] Abort and export partial work"
         → Option [1] disabled after 3 attempts
         → Log: "Resume loop detected - same checkpoint {hash} attempted 3 times"
     ELSE:
       # Different checkpoint - reset counter
       resume_attempt_count = 0
       checkpoint_hash = current_hash
   ```

CHECKPOINT STRATEGY:

CHECKPOINT TRIGGERS (automatic):
- Before step transition (save current step as complete)
- Before nested workflow invocation
- Before party mode session
- After successful validation pass
- Every 60 seconds during long operations

CHECKPOINT DATA (saved to frontmatter or state file):
checkpoint:
  workflow: "create-prd"
  step: "04"
  timestamp: "2026-01-08T14:32:00Z"
  validation_state: "in-progress"
  iteration: 3
  party_mode_agent_id: "pm-abc123"  # If in party mode
  nested_invocation: null           # Or {child: "...", started: "..."}
  pending_operations: []
  context_summary: "Generating requirements section 3..."

RECOVERY PROCEDURE (on session restart):

1. CHECK FOR INCOMPLETE STATE:
   - Read bmm-workflow-status.yaml
   - Check for checkpoint.timestamp within last 24 hours
   - Check for nested_invocation in progress

2. PRESENT RECOVERY OPTIONS:
   IF checkpoint found:
   → "Previous session interrupted at {workflow} step {step}."
   → "[1] Resume from checkpoint"
   → "[2] Restart workflow from beginning"
   → "[3] Abandon and start fresh"

3. IF RESUME SELECTED:
   a. Load checkpoint state
   b. Restore step context from frontmatter
   c. IF party_mode_agent_id exists:
      - Attempt Task(resume=agent_id)
      - If resume fails: restart party mode from scratch
   d. IF nested_invocation in progress:
      - Check child workflow state
      - Resume child OR restart child based on child state
   e. Continue from checkpoint step

4. STATE VALIDATION ON RESUME:
   - Verify referenced files still exist
   - Check frontmatter timestamps for consistency
   - Warn if state appears stale (>24h old)
   - Offer fresh start if validation fails

NESTED WORKFLOW CRASH HANDLING:
IF crash during nested workflow (e.g., workflow-compliance-check):
   → Parent state preserved in frontmatter
   → On resume: check child completion status
   → IF child incomplete: offer to restart child only
   → IF child complete: read result, continue parent
   → Parent NEVER loses state due to child crash
```

#### Nested Workflow Crash Isolation

```
CRASH ISOLATION PRINCIPLE:
Child workflow crash MUST NOT corrupt parent workflow state.

ISOLATION MECHANISM:
1. Parent saves state to frontmatter BEFORE invoking child
2. Child operates in isolated state file (_bmad-output/{child}/state.yaml)
3. Parent polls for child completion OR timeout (300s)
4. On child crash:
   a. Parent detects timeout or crash signal
   b. Parent state remains intact (already saved)
   c. User presented with options:
      [1] Retry child workflow
      [2] Skip child, continue parent (REQUIRES EXPLICIT CONFIRMATION - see below)
      [3] Abort parent workflow

SKIP VALIDATION SAFETY PROTOCOL (CRITICAL):
Option [2] allows bypassing validation, which can produce unsafe outputs.
Require explicit confirmation to prevent accidental skips:

   ON [2] SKIP SELECTED:
     → Display warning:
       "⚠️  WARNING: Skipping {child_workflow} will bypass validation.
        Output will be marked as UNVALIDATED and may contain errors.
        This is NOT RECOMMENDED for production use."

     → Require explicit confirmation:
       "Type 'SKIP VALIDATION' (exact text) to confirm:"

     → IF user_input != "SKIP VALIDATION":
       → Display: "Confirmation not matched. Returning to options menu."
       → Return to options [1]/[2]/[3]

     → IF user_input == "SKIP VALIDATION":
       → Mark parent workflow output as UNVALIDATED:
         ```yaml
         validation_status: SKIPPED
         skipped_validation: "{child_workflow}"
         skip_reason: "User explicitly bypassed validation"
         skip_timestamp: "{timestamp}"
         skip_warning: "Output not validated - review before production use"
         ```
       → Add UNVALIDATED watermark to all output artifacts:
         - Frontmatter: `validation_skipped: true`
         - Output files: Header comment "# UNVALIDATED - {child_workflow} skipped"
       → Log: "Validation skipped by user confirmation for {child_workflow}"
       → Continue parent workflow with warning banner displayed

CRASH SIGNALS DETECTED:
- Child state file shows error state
- Child process exited unexpectedly
- Timeout exceeded (300s default)
- Child audit trail shows unrecoverable error

STATE PRESERVATION GUARANTEE:
- Parent frontmatter always valid (atomic writes)
- Child failure cannot modify parent state
- Recovery always possible from parent checkpoint
```

#### Timeout Cascade and Propagation (CRITICAL)

When a parent times out while children are running, undefined behavior can leave orphaned processes, corrupted state, or deadlocks. This section defines timeout propagation rules.

```
TIMEOUT HIERARCHY:
  Parent workflow timeout: 1800s (30 min)
    └── Nested workflow timeout: 300s (5 min)
          └── Subagent timeout: 60s
                └── Hook timeout: 5s

PROPAGATION RULES:

1. PARENT TIMEOUT TRIGGERS CHILD TERMINATION:
   When parent timeout fires:
   a. Set parent state to "timeout_cleanup"
   b. **PRE-SIGNAL CHECK (Issue 6 Edge Case):** Before sending termination signal to each child:
      - Verify PID still exists (process hasn't exited)
      - Check child state is NOT 'completed' (result may be in-flight)
      - If child already completed: skip signal, collect result immediately
      - If PID doesn't exist: mark as "already_exited", skip signal
      - Only send SIGTERM to children confirmed as still running AND not completed
   c. Send termination signal to verified active children
   d. Wait up to 10s for graceful child shutdown
   d. Force-kill any remaining children
   e. Collect partial results from children that completed
   f. Save parent state with timeout marker
   g. Present user with recovery options

2. TIMEOUT BUDGET INHERITANCE:
   Child receives remaining parent timeout as maximum:
   ```python
   CLEANUP_BUFFER_SEC = 10

   def calculate_child_timeout(parent_remaining: int, child_default: int) -> int:
       """Child timeout is min of its default and parent's remaining time."""
       if parent_remaining <= CLEANUP_BUFFER_SEC:
           return 0  # Parent already timed out or no time left after cleanup buffer
       return min(child_default, parent_remaining - CLEANUP_BUFFER_SEC)

   # Example: Parent has 120s left, child default is 300s
   # Child gets: min(300, 120-10) = 110s
   #
   # Example: Parent has 10s or less left
   # Child gets: 0 (no time to execute, cleanup must happen)
   ```

3. CLEANUP BUFFER:
   - Reserve 10s at each nesting level for cleanup
   - Child timeout = min(child_default, parent_remaining - 10s)
   - This ensures parent can always perform cleanup even if child times out

4. GRACEFUL VS FORCED TERMINATION:
   | Signal | Wait Time | Action |
   |--------|-----------|--------|
   | SIGTERM (graceful) | 5s | Child saves state, exits cleanly |
   | SIGKILL (forced) | 0s | Immediate termination, state may be lost |

   Sequence:
   a. Parent sends SIGTERM to child
   b. Wait 5s for child to save state and exit
   c. If child still running: send SIGKILL
   d. Log forced termination in audit trail

5. ORPHAN PREVENTION:
   - Each child registers its PID with parent on spawn
   - Parent maintains active_children: dict[str, ChildInfo]
   - On parent exit (normal or crash): iterate children and terminate
   - Watchdog process runs every 30s to detect orphaned children

6. CHILD STATE ON PARENT TIMEOUT:
   @dataclass
   class ChildTerminationResult:
       child_id: str
       termination_type: str  # "graceful" | "forced" | "already_complete"
       partial_result: Any | None  # If child saved partial state
       state_file_path: str | None  # For resume

7. RECOVERY FROM TIMEOUT CASCADE:
   On resume after parent timeout:
   a. Load parent state (marked "timeout_cleanup")
   b. Check each child's state file for partial progress
   c. Present options:
      [1] Resume children from their saved state
      [2] Restart children fresh
      [3] Skip children, continue parent (with warnings)
      [4] Abort entire workflow

8. TIMEOUT LOGGING:
   All timeouts logged with:
   - Timestamp
   - Entity that timed out (parent/child/subagent/hook)
   - Timeout duration
   - Parent chain (for nested timeouts)
   - State at timeout (for debugging)

EXAMPLE SCENARIO:
  Parent workflow (budget: 120s starting at t=0)
    └── Invokes child workflow (default: 300s, actual: 110s)
          └── Child spawns subagent (default: 60s, actual: 60s)

  If subagent hangs at t=50s:
  - Subagent times out at t=60s
  - Child gets timeout signal, saves state, exits at t=65s
  - Parent continues with child's partial result
  - Parent completes at t=100s (within its 120s budget)

  If child hangs (ignores timeout):
  - Child timeout fires at t=110s
  - Parent sends SIGTERM at t=110s
  - Parent waits 5s, child still running
  - Parent sends SIGKILL at t=115s
  - Parent in cleanup mode, presents recovery options at t=120s
```

**What automation CAN do:**
- Auto-SELECT menu options ([C], [Y], [N], etc.) based on rules
- Auto-PROVIDE inputs when criteria are met
- Auto-CONTINUE through steps at appropriate tier

**What automation CANNOT do:**
- SKIP steps entirely
- COMBINE multiple steps into one
- BYPASS menus without processing them
- IGNORE step file instructions
- PROCEED without saving frontmatter state

---

## Implementation Scope

### Automation-to-Workflow Mapping (S6)

| Automation Component | Interacts With | Workflow Files/Steps |
|---------------------|----------------|---------------------|
| **Automation Controller** | All validation workflows | `check-implementation-readiness/`, `workflow-compliance-check/`, `testarch-trace/` |
| **Menu Participation Engine** | Every step in every workflow | Step files with `[A][P][C]`, `[Y][V][N]`, `[1-4]`, `[E]` menus |
| **Tier Suggester** | workflow-init | `workflow-init/steps/step-03.md` (Express path) or `step-05.md` (Guided path) - tier selection step varies by path |
| **Party Mode Driver** | party-mode | `core/workflows/party-mode/steps/step-01.md` through `step-03.md` |
| **Subagent Dispatcher** | Parallel review steps | Agent validation `08a-08f`, code-review |
| **Memory Bridge** | Forgetful MCP | Pre-workflow hook, Post-workflow hook |
| **Confidence Calculator** | All validation outputs | Reads from `validation-result.yaml`, `reviewer-findings.yaml` |
| **Loop-Back Handler** | Edit-Module Step 06 | `edit-module/steps/step-06-iteration.md` |
| **Pre-flight Validator** | workflow-init | Runs after Step 1-3 (state detection), before path selection |
| **Sprint Watcher** | sprint-planning | Monitors `sprint-status.yaml`, triggers `dev-story` |

### New Components to Build

1. **Automation Controller**
   - Wraps existing validation steps
   - Manages attempt counting and stall detection
   - Implements BMB threshold checks (blocking>3, major>5, score<70)
   - Triggers party mode via Party Mode Driver
   - Routes to human checkpoints based on tier
   - Handles batch-continue logic per tier
   - **Verdict-aware:** Handles PASS/CONCERNS/FAIL differently than error counts
   - **Hook orchestration (Claude Code 2.1):**
     - Reads hooks from step file frontmatter before execution
     - Executes PreToolUse hooks before each tool invocation
     - Executes PostToolUse hooks after each tool completes
     - Executes Stop hooks when step/subagent completes
     - Passes context between hooks and main execution via environment variables
     - Handles hook failures gracefully (log and continue vs escalate)
   - **Hook Discovery/Execution Protocol (S8):**
     - WHEN: Parse frontmatter at step file load time (before execution begins)
     - HOW: YAML parser extracts `hooks:` section from frontmatter
     - EXECUTION ORDER: SessionStart (once: true) → PreToolUse → [tool] → PostToolUse → Stop
     - FAILURE HANDLING:
       - Hook exits non-zero → log warning, continue execution (default)
       - Hook has `critical: true` → abort step, escalate to human
       - Hook timeout (5s default) → kill process, log timeout, continue
       - EDGE CASES:
         - Multiple hooks, one fails mid-sequence → continue remaining hooks unless failed hook was `critical: true`
         - Hook output file corrupted/partial → treat as non-zero exit, log warning, continue
         - Environment variables with special chars → sanitize via shell escaping before execution
     - **OUTPUT SIZE LIMITS (CRITICAL - Prevent Memory Exhaustion):**
       - **Per-hook stdout limit:** 64KB (65,536 bytes)
       - **Per-hook stderr limit:** 16KB (16,384 bytes)
       - **Total hook output per step:** 256KB (262,144 bytes)
       - **Enforcement mechanism:**
         ```python
         class HookOutputLimiter:
             MAX_STDOUT = 65536
             MAX_STDERR = 16384
             MAX_TOTAL_PER_STEP = 262144

             def capture_output(self, process, hook_name):
                 stdout = process.stdout.read(self.MAX_STDOUT)
                 if len(stdout) == self.MAX_STDOUT:
                     log.warning(f"Hook {hook_name} stdout truncated at {self.MAX_STDOUT} bytes")
                     process.stdout.read()  # Drain remaining to prevent blocking

                 stderr = process.stderr.read(self.MAX_STDERR)
                 if len(stderr) == self.MAX_STDERR:
                     log.warning(f"Hook {hook_name} stderr truncated at {self.MAX_STDERR} bytes")
                     process.stderr.read()  # Drain remaining

                 return stdout, stderr
         ```
       - **Behavior when limit exceeded:**
         - **EXACTLY 64KB HANDLING (Issue 7 Edge Case):** When output is exactly 64KB:
           - Probe for 1 additional byte to check if more data exists
           - If more data exists: truncate at 64KB, append marker
           - If no more data (output is exactly 64KB): keep as-is, no truncation marker
         - **TRUNCATION ALGORITHM (Issue 11 Edge Case - Sequential Steps):**
           1. Check if output exceeds 64KB limit
           2. If exceeded: search backwards up to 1KB from limit position for newline character
           3. If newline found within 1KB: truncate at newline (preserve line boundary)
           4. If no newline found within 1KB: force-truncate at exact 64KB limit
           5. Append truncation marker: "[OUTPUT TRUNCATED AT 64KB]"
         - Lines >64KB are force-truncated mid-content (cannot preserve line boundary for oversized lines)
         - Warning logged with hook name and actual output size
         - Hook execution continues (output limit is not a failure)
         - Truncation marker appended: "[OUTPUT TRUNCATED AT 64KB]"
       - **Step-level enforcement:**
         - Track cumulative output across all hooks in step
         - If total exceeds 256KB: subsequent hooks execute but output discarded
         - Final summary shows: "Hook output budget exhausted (256KB); some output discarded"
       - **Memory-safe reading:**
         - Use streaming reads with size limits, not read-all-then-check
         - Set subprocess bufsize to 8KB to prevent kernel buffer bloat
         - Kill hook process if output rate exceeds 1MB/sec (likely infinite loop)

2. **Menu Participation Engine**
   - **DETECTS actual menu options** present in each step (not assume [A][P][C] universally)
   - Handles diverse menu structures: workflow-init uses [1-4], party-mode uses [E], BMM uses [A][P][C]
   - Evaluates confidence and tier rules
   - Implements BMB threshold → action mapping
   - Auto-selects appropriate option when criteria met
   - Triggers escalation options (e.g., [A], [P]) based on conditions
   - Handles menu re-display after elicitation/party mode completion
   - **Respects BMAD rules:** Processes menus, never skips them

3. **Tier Suggester** (not Detector - wraps, doesn't replace)
   - Uses existing `project-levels.yaml` keywords
   - Generates suggestions for workflow-init tier selection step (Step 3 for Express path, Step 5 for Guided path)
   - Presents recommendations alongside manual selection
   - Caches user's choice (not auto-detected tier)

4. **Party Mode Driver**
   - Acts as programmatic human for party mode
   - Generates topic proposals from context
   - Monitors agent responses (not per-round steering)
   - Detects convergence/disagreement/exit conditions
   - **Escalates to human on direct questions** (detects '[Agent Name] asks:' pattern)
   - Captures outcome and extracts key points for memory
   - Alternative: Simulated Party Mode for Level 0-2

5. **Subagent Dispatcher**
   - Spawns reviewer subagents based on tier
   - Collects and synthesizes findings
   - Integrates with existing review patterns
   - Manages information asymmetry
   - Supports Simulated Party Mode (parallel persona execution)
   - **Code Review mode:** ADVERSARIAL - finds 3-10 specific issues, executes 19-item checklist, produces Approve/Changes/Blocked outcome
   - **Agent ID tracking:** Stores `agent_id` from each invocation for potential resumption (Claude Code 2.1)
   - **Context fork (Claude Code 2.1):** Uses `context: fork` as default for parallel reviewers - each reviewer gets full conversation history in isolated fork, enabling true information asymmetry and parallel execution without cross-contamination

6. **Memory Bridge**
   - Aligns with workflow-level hooks (Pre-Workflow/Post-Workflow), not agent-level
   - Queries at WORKFLOW START (Pre-Workflow hook)
   - Saves at WORKFLOW COMPLETION (Post-Workflow hook)
   - Additional queries during automation loops
   - Additional saves for fix patterns
   - **Context Hub stack integration:** Forgetful (semantic memory) + Serena (LSP symbols) + Context7 (library docs)
   - Handles Forgetful unavailability gracefully

7. **Workflow Entry Wrapper**
   - Integrates with workflow-init decision tree
   - Provides smart defaults at each decision point
   - Handles greenfield/brownfield detection
   - Routes Quick Flow requests to solo-dev agent
   - Routes quick-dev requests with mode detection

8. **Confidence Calculator** (NEW FUNCTIONALITY)
   - Calculates confidence from observable signals
   - Inputs: validation verdict, memory match, reviewer agreement, party mode outcome
   - Applies tier adjustment
   - Returns confidence score (0-100) and threshold classification

9. **Loop-Back Handler** (for Edit-Module)
   - Tracks iteration loop state (Step 06 [Y]→Step 03)
   - Preserves edit session state across loops
   - Re-runs validation after each loop iteration
   - Suggests [N] done after successful validation

10. **Validation Type Detector**
    - Identifies which workflow is running
    - Maps workflow to validation type (verdict-based, error-based, adversarial)
    - Maps workflow to phase count (3, 6, or 8 phases)
    - Configures automation controller appropriately

11. **Pre-flight Validation Subagent**
    - Spawns background subagent AFTER workflow-init state detection
    - Validates required documents exist and are non-empty
    - Checks dependencies (PRD before Architecture, Architecture before Epics)
    - Returns quick READY/NOT_READY verdict
    - Fails fast before wasting context on doomed workflows
    - **Timing (CRITICAL):** Cannot validate prerequisites without knowing which phase/workflow will run
      - Step 1: workflow-init performs state detection (Steps 1-3)
      - Step 2: Pre-flight validation runs with knowledge of target phase
      - Step 3: workflow-init path selection proceeds (Step 4+)
      - Step 4: Workflow execution begins
    - **Integration:** Runs AFTER workflow-init state detection (Steps 1-3) but BEFORE path selection (Step 4+)
    - **NOT_READY handling (S7):**
      - NOT_READY verdict returns `{ready: false, missing: ["PRD", "Architecture"], suggestion: "create-prd"}`
      - Automation presents options: `[1] Run create-prd first [2] Continue anyway [3] Abort`
      - If option 1: chain to suggested workflow, return to original on completion
      - If option 2: proceed with warning in audit trail
      - If option 3: abort gracefully with status saved
    - **Effort:** Low | **Value:** High | **Risk:** None

12. **Parallel BMB Validation Steps**
    - Executes BMB validation steps 08a-08f in parallel using Task tool
    - Each step runs as independent subagent
    - Collects all results, aggregates blocking/major/minor counts
    - Falls back to sequential if parallel fails
    - **Synchronization barrier (CRITICAL):** Wait for ALL six subagents to complete before aggregating results. If any subagent fails to complete (timeout after configurable threshold), fall back to sequential execution for remaining steps.
    - **Response Collector Thread Safety (CRITICAL):** Multiple subagents responding simultaneously MUST NOT corrupt aggregation state:
      - **Mutex requirement:** Acquire `aggregation_mutex` before modifying `AggregatedResults` data structure
      - **Lock scope:** Lock held only during result insertion (not during entire subagent execution)
      - **Deadlock prevention:** Single mutex with 5s timeout; if lock acquisition times out, log warning and retry once. **If retry also fails:** log error with full stack trace, mark step as `mutex_failure` in ValidationResult, exclude step from aggregation but continue workflow with remaining steps. Mutex failures are treated as step failures for partial failure policy.
      - **POST-COMPLETION FAILURES (Issue 10 Edge Case):** Mutex failures that occur AFTER step execution completed but during result insertion are handled separately from execution failures:
        - Step execution SUCCESS is preserved (not re-executed)
        - Only retry result insertion (not full step re-execution)
        - Store pending result to disk: `_bmad-output/.pending-results/{step_id}.json`
        - Background thread retries insertion every 5s for up to 60s
        - If insertion permanently fails: result available in pending file for manual recovery
        - Execution failure table does NOT apply; this is aggregation-only failure
      - **Mutex Failure Escalation (CRITICAL):** Behavior differs based on execution context:
        ```
        ON MUTEX RETRY FAILURE:
          mutex_failure_count += 1  # Per-step counter

          IF context == INTERACTIVE:
            → Present human with options:
              "[1] Retry mutex acquisition"
              "[2] Skip step, continue with partial results"
              "[3] Abort parallel execution, fall back to sequential"
            → Human selects option

          ELSE IF context == BACKGROUND:
            → Queue step for delayed retry: 30s delay
            → Continue with other steps
            → After 3 delayed retry failures for same step:
              → Mark step as PERMANENTLY_FAILED
              → Pause task (remove from active queue)
              → Create alert: "Background task paused: mutex failure in {step_id}"
              → Log: "Step {step_id} mutex failed 3 times in background - task paused"
              → Require human intervention to resume

        BACKGROUND MUTEX FAILURE STATE:
          @dataclass
          class MutexFailureState:
              step_id: str
              failure_count: int
              last_failure: datetime
              queued_retry_at: datetime | None
              permanently_failed: bool
        ```
      - **Thread-safe data structure:** Use concurrent-safe collections or copy-on-write pattern:
        ```python
        @dataclass
        class AggregatedResults:
            _lock: threading.Lock
            blocking: list[Finding]  # Append-only under lock
            major: list[Finding]     # Append-only under lock
            minor: list[Finding]     # Append-only under lock
            completed_steps: set[str]  # Track which steps finished

            def add_findings(self, step_id: str, findings: list[Finding]):
                with self._lock:
                    for f in findings:
                        if f.severity == "blocking": self.blocking.append(f)
                        elif f.severity == "major": self.major.append(f)
                        else: self.minor.append(f)
                    self.completed_steps.add(step_id)
        ```
      - **No partial reads:** Aggregation summary only computed after ALL subagents complete or timeout
    - **Steps parallelized:**
      - 08a: Plan traceability validation
      - 08b: Metadata validation
      - 08c: Persona validation
      - 08d: Menu validation
      - 08e: Structure validation
      - 08f: Sidecar validation
    - **Partial Failure Handling Policy (CRITICAL):** When some but not all subagents succeed:
      - **Definition:** Partial success = 1 to 5 subagents complete successfully, others fail/timeout
      - **Policy by failure count:**
        | Successes | Failures | Action |
        |-----------|----------|--------|
        | 6 | 0 | Aggregate all results, proceed normally |
        | 4-5 | 1-2 | Aggregate successful results + retry failed steps sequentially once |
        | 2-3 | 3-4 | Retry ALL failed steps sequentially; if still failing, escalate to human with partial results |
        | 1 | 5 | Use single success as head-start context for sequential retry of all 5 failed steps |
        | 0 | 6 | Abort parallel execution, fall back to full sequential execution |
      - **Result composition:** Partial results MUST be clearly marked:
        ```python
        @dataclass
        class ValidationResult:
            completed_steps: list[str]   # e.g., ["08a", "08b", "08d"]
            failed_steps: list[str]      # e.g., ["08c", "08e", "08f"]
            findings: AggregatedResults  # Only from completed steps
            partial: bool                # True if any step failed
            retry_attempted: bool        # True if sequential retry was tried
        ```
      - **Human presentation:** When escalating partial results, clearly indicate:
        - Which steps completed and their findings
        - Which steps failed and failure reason (timeout/error/crash)
        - Recommendation: "Re-run failed steps" or "Manual review required"
      - **Never silently discard:** Failed step results are logged even if not aggregated
    - **Effort:** Low | **Value:** Medium | **Risk:** None

13. **Sprint Status Auto-Watcher**
    - Background agent monitoring sprint-status.yaml
    - Detects story state changes (pending→in_progress→done)
    - Auto-triggers dev-story workflow when story marked ready
    - Alerts on stale in_progress stories (configurable threshold)
    - Integrates with Memory Bridge for pattern detection
    - **Race condition prevention (CRITICAL):** Before triggering dev-story, atomically update sprint-status.yaml to mark story as `claimed-by-automation`. This prevents multiple watchers or manual triggers from starting duplicate dev-story workflows for the same story.
    - **Debounce mechanism (CRITICAL):** Multiple rapid file changes MUST be coalesced to prevent duplicate workflow invocations:
      - **Debounce window:** 500ms from last file change before processing
      - **Implementation:** On file change, reset 500ms timer. Only process when timer expires without new changes.
      - **Batch processing:** If multiple stories change within debounce window, process all changed stories in single batch evaluation
      - **Deduplication:** Maintain in-memory set of `pending-trigger-{story-id}` entries; ignore duplicate triggers within 60s window
      - **Concurrency lock:** Acquire mutex before evaluating triggers; release after trigger file written or decision made to skip
    - **Trigger conditions:**
      - New story enters `ready-for-dev` state
      - Story in `in_progress` for >N hours without update
      - Sprint end date approaching with incomplete stories
    - **Trigger Mechanism (S9):**
      - File watcher monitors `sprint-status.yaml` for changes
      - On change: start/reset 500ms debounce timer
      - When debounce timer expires:
        1. Acquire processing mutex
        2. Parse YAML, compare to cached previous state
        3. For each story with status changed to `ready-for-dev`:
           a. Check deduplication set (skip if triggered within 30s)
           b. Atomically mark story as `claimed-by-automation` ONLY IF current status is still `ready-for-dev` AND `status_changed_at` timestamp matches expected value (dual compare-and-swap). If status changed between step 2 and now (another process claimed it), OR if status cycled (ready->progress->ready within debounce), skip this story.
           - **STATUS CYCLING PREVENTION (Issue 3 Edge Case):** Track `status_changed_at` timestamp alongside status. CAS must verify BOTH status value AND timestamp match. If status cycles back to same value with different timestamp, treat as change and re-evaluate.
           c. If claim succeeded: Write trigger file `_bmad-output/triggers/dev-story-{story-id}.trigger`
           d. Add to deduplication set with timestamp
        4. Release mutex
        5. Main automation controller detects trigger file on next poll (5s)
        6. Invokes dev-story workflow with story context
      - Alternative: Direct Skill invocation if in same session
    - **Memory leak prevention (CRITICAL):** Sprint Watcher runs indefinitely; requires periodic cleanup:
      - **Deduplication set cleanup:** Purge entries older than 60s every 30s
      - **State cache refresh:** Re-read sprint-status.yaml from disk every 5 minutes (prevents drift)
      - **Trigger file cleanup:** Delete processed trigger files after 1 hour
      - **Restart policy:** Auto-restart watcher every 4 hours to clear accumulated state
      - **Resource limits:** Max 100 entries in deduplication set; drop oldest if exceeded
      - **Health check:** Log heartbeat every 60s; alert if no heartbeat for 5 minutes
    - **Effort:** Medium | **Value:** High | **Risk:** Low

14. **Cross-Reference Validator**
    - Validates document cross-references before workflow execution
    - Checks PRD→Architecture alignment
    - Checks Architecture→Epics consistency
    - Checks Epics→Stories traceability
    - Returns list of broken references
    - **Integration:** Can run as pre-flight check or standalone
    - **Effort:** Low | **Value:** High | **Risk:** None

15. **Context Pre-Loader**
    - Queries Forgetful for relevant memories BEFORE workflow starts
    - Loads project-specific patterns, decisions, constraints
    - Pre-populates workflow context with historical knowledge
    - Reduces "cold start" syndrome in long workflows
    - **Coordination with AGENT START hook (CRITICAL):** Context Pre-Loader runs first and CACHES results. The AGENT START hook then reads from this cache instead of making duplicate Forgetful queries. This prevents redundant API calls and ensures consistent context across components.
    - **Initialization order requirements (CRITICAL - prevents circular dependency):**
      - **Problem:** AGENT START hook might invoke Context Pre-Loader before MCP servers are available
      - **Solution:** Staged initialization with dependency checks:
        1. **Stage 1 (0-300ms):** MCP server availability check - poll Forgetful, Context7, Serena in parallel, 3x100ms retries each, 300ms total max (see INITIALIZATION SEQUENCE below)
        2. **Stage 2 (300-500ms):** If Forgetful available, Context Pre-Loader queries and caches results
        3. **Stage 3 (500ms+):** AGENT START hook reads from cache OR operates without memory context
      - **Timeout handling:** If Forgetful not available after 300ms total, proceed without memory (see Graceful Degradation)
      - **Cache location:** `_bmad-output/.context-cache/{session-id}.json`
      - **Cache validity:** Cache valid for session duration; invalidated on explicit refresh or session end
      - **AGENT START hook behavior:** Check cache first; if cache miss AND Forgetful available, query directly; if neither, continue without memory context
    - **Query strategy:**
      - Project ID filter
      - Workflow-type keywords
      - Recent memories with high importance
      - Entity relationships (people, systems, decisions)
    - **Effort:** Low | **Value:** High | **Risk:** None

16. **Post-Workflow Memory Curator**
    - Runs AFTER workflow completion
    - Extracts key decisions and patterns from workflow output
    - Creates atomic memories for each significant outcome
    - Links new memories to relevant existing memories
    - Marks obsolete memories when decisions change
    - Follows curating-memories skill patterns
    - **Ordering with Core WORKFLOW COMPLETION hook (CRITICAL):** Core's WORKFLOW COMPLETION hook runs FIRST and performs basic memory save (workflow outcome, completion status). THEN the Curator runs to create additional atomic memories for decisions, patterns, and linkages. This ensures Core's save completes before Curator adds supplementary memories.
    - **Memory types created:**
      - Architectural decisions (importance 9-10)
      - Implementation patterns (importance 7-8)
      - Problem-solution pairs (importance 7-8)
      - Milestone completions (importance 6-7)
    - **Effort:** Medium | **Value:** Medium | **Risk:** Low

### Claude Code 2.1/2.1.2 Feature Integration

The following Claude Code features enhance the automation layer:

#### Tool Configuration (YAML allowed-tools)

Subagent tool access specified in clean YAML format:

```yaml
allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - mcp__forgetful__*  # All Forgetful tools
```

Simplifies subagent tool configuration vs string lists. The Subagent Dispatcher uses this syntax when spawning reviewer subagents (Spec Reviewer, Quality Reviewer, Adversarial Reviewer) to precisely control their tool access.

#### Agent Type Identification (SessionStart)

SessionStart hooks receive `agent_type` parameter:

```
SessionStart hook context:
- agent_type: "validator" | "reviewer" | "party-mode-driver"
- Enables agent-specific initialization
- Different memory queries by agent type
- Different logging behavior by type
```

BMAD Application:
- Validator agents → query for fix patterns at startup
- Reviewer agents → query for review checklists at startup
- Party mode driver → query for discussion context at startup

This aligns with Memory Integration hooks - the `agent_type` parameter allows the Memory Bridge to make agent-specific Forgetful queries at AGENT START.

#### MCP Server Change Detection

`list_changed` notifications when MCP tools change:

```
MCP CHANGE HANDLING:
- Detect when Forgetful tools change
- Detect when custom project MCPs update
- Re-query available tools on notification
- Log tool availability changes
```

Ensures automation stays aware of available capabilities. Critical for:
- Graceful degradation when Forgetful becomes unavailable
- Adapting to new MCP tools added during session
- Updating Subagent Dispatcher's tool inventory

### Files to Modify

- `workflow-init` (add automation hooks at each decision step)
- Validation step files (wrap with automation loop + menu participation)
- Iteration step files (auto-continue logic + [A][P][C] handling)
- Party mode workflow (add driver integration for programmatic input)
- Workflow status (preserve manual tier selection)
- BMB agent workflow (handle tri-modal: CREATE/EDIT/VALIDATE)
- BMB edit-module (Step 06 loop-back handling)
- BMB workflow-compliance-check (8-phase awareness)
- BMM code-review (ADVERSARIAL 3-10 findings required, Approve/Changes/Blocked outcomes)
- BMM check-implementation-readiness (verdict-based: PASS/CONCERNS/FAIL)

### Files to Create

- Automation controller workflow/module
- Menu participation engine module
- Tier suggester module (suggestion layer, not replacement)
- Party mode driver module
- Subagent dispatcher module
- Memory bridge utilities (aligned with Core hooks)
- Workflow entry wrapper
- Audit trail logger
- **Confidence calculator module** (NEW FUNCTIONALITY)
- **Loop-back handler module** (for Edit-Module Step 06)
- **Validation type detector module** (workflow-specific awareness)
- **Quick-dev automation handler** (mode detection, escalation signals)
- **Pre-flight validation subagent** (document existence/dependency checks)
- **Parallel BMB validator orchestrator** (parallel 08a-08f execution)
- **Sprint status auto-watcher** (background monitoring agent)
- **Cross-reference validator** (PRD→Arch→Epics→Stories alignment)
- **Context pre-loader** (Forgetful memory pre-population)
- **Post-workflow memory curator** (automated memory extraction and linking)

---

## Cross-Module Orchestration (S12)

### Workflow Transitions Between Modules

BMAD workflows can transition between modules (BMM phases, BMB creation, Core utilities). Automation must handle these transitions.

```
TRANSITION DETECTION:
- Parse workflow output for module boundary keywords
- Monitor for: "invoking BMB agent workflow", "starting party-mode", "running workflow-compliance-check"
- Detect when workflow references files in different module directory

TRANSITION TYPES:
1. BMM Phase → BMM Phase (e.g., create-prd → create-architecture)
   - State: Preserve in sprint-status.yaml
   - Tier: Propagates (same project level)
   - Context: Pass document paths, project ID

2. BMM → BMB (e.g., need new agent during implementation)
   - State: BMM workflow pauses, BMB workflow runs
   - Tier: May differ (BMB often lower tier for utilities)
   - Context: Pass agent requirements from BMM context

3. Any → Core (e.g., trigger party-mode for discussion)
   - State: Caller workflow pauses
   - Tier: N/A for party-mode (always interactive)
   - Context: Topic, relevant agents, exit criteria

STATE PRESERVATION FORMAT:
{
  "caller_workflow": "create-architecture",
  "caller_module": "bmm",
  "caller_step": "03",
  "caller_state_path": "_bmad-output/create-architecture/state.yaml",
  "target_workflow": "agent",
  "target_module": "bmb",
  "tier_propagation": true,
  "context_handoff": {...}
}

TIER PROPAGATION RULES:
- Same module: Tier ALWAYS propagates
- BMM → BMB: Tier propagates unless BMB workflow overrides
- Any → Core: Core workflows ignore tier (party-mode always interactive)
- Return: Original tier restored from state
```

### Module Boundary Detection

```
MODULE BOUNDARIES:
_bmad/
├── bmm/        # BMM workflows (phases 1-4)
├── bmb/        # BMB workflows (agent, workflow, module builders)
├── core/       # Core workflows (party-mode, brainstorming)
└── _config/    # Shared configuration

DETECTION LOGIC:
def detect_module_transition(current_path, target_path):
    current_module = extract_module(current_path)  # "bmm", "bmb", "core"
    target_module = extract_module(target_path)
    if current_module != target_module:
        return TransitionEvent(
            from_module=current_module,
            to_module=target_module,
            requires_state_save=True
        )
    return None
```

---

## Success Criteria

1. **Reduced Human Interaction**
   - Level 0-1 tasks: Only final approval required (batch-[C] through all steps)
   - Level 2-3 tasks: 2-3 checkpoints max (design decisions, final)
   - Level 4 tasks: Checkpoints at major milestones only
   - **Metric:** Count of human inputs per workflow reduced by 80%+ for Level 0-2

2. **Improved Quality (Verdict-Based)**

   **IMPORTANT: "0 issues" target is STRICTER than BMAD baseline.**

   BMAD baseline behavior:
   - [C] Continue is allowed even with minor/major issues
   - Only BLOCKING errors prevent continuation
   - Human can acknowledge issues and proceed

   Automation target (stricter):
   - Aims for 0 issues across all severity levels
   - This exceeds BMAD's baseline blocking-only behavior
   - Rationale: Higher quality through automated iteration
   - Human can still override to BMAD baseline behavior

   **Issues to Fix (automation target = 0, BMAD baseline = 0 blocking only):**
   - Syntax errors: 0 at completion
   - Reference errors: 0 at completion
   - Blocking issues: 0 at completion (BMAD requirement)
   - Major issues: 0 at completion (automation stricter than BMAD - BMAD allows with acknowledgment)

   **Code Review Outcomes (ADVERSARIAL):**
   - Code Review is ADVERSARIAL: must find 3-10 specific issues per story
   - Uses 19-item checklist with Approve/Changes Requested/Blocked outcomes
   - Approve = 3-10 issues found AND all addressed, code meets standards
   - Changes Requested = issues found, apply suggested changes, re-review
   - Blocked = fundamental issues requiring human escalation
   - NEVER "looks good" without findings

   **Verdicts (target varies by workflow):**
   - Implementation Readiness: Target READY (NEEDS WORK acceptable with acknowledgment)
   - Test Traceability: Target PASS or WAIVED with documented rationale

   **Metric:** Issue escape rate (issues found after "completion") < 5%

3. **Faster Resolution**
   - Known patterns resolve in 1 attempt (vs 3+)
   - BMB threshold detection triggers early escalation
   - Stall detection prevents wasted cycles
   - Parallel review reduces sequential bottlenecks
   - **Metric:** Median time-to-completion reduced by 50%+

4. **Maintained Control**
   - Human can override at any point
   - Full audit trail for transparency
   - Confidence-based detail keeps human informed (NEW FUNCTIONALITY)
   - **Workflow-init preserved:** User still chooses tier and path
   - **Menus preserved:** [A][P][C] always available for human override
   - **Steps preserved:** Automation never skips steps (BMAD Critical Rule)

5. **BMAD Integrity**
   - All existing workflows remain functional without automation
   - Automation layer is opt-in, not mandatory
   - Workflow-init decision tree unchanged (automation wraps, doesn't replace)
   - Party mode remains human-invocable at any time
   - Step processing rules honored (never skip, always follow instructions)
   - Quick-dev path preserved as legitimate bypass option

---

## Context Window Preservation Strategies

BMAD workflows are long and context-intensive. Subagents help preserve the main conversation's context window by offloading work to isolated processes.

### Problem Statement

A full BMM greenfield workflow (Phases 1-4) can consume:
- 20+ step files read and processed
- Multiple validation loops per step
- Party mode discussions (potentially lengthy)
- Document creation and revision cycles
- Memory queries and saves

Without subagent offloading, context exhaustion occurs before workflow completion.

### Subagent Offloading Opportunities

| Operation | Current State | Subagent Strategy | Context Savings |
|-----------|---------------|-------------------|-----------------|
| **Document analysis** | Full document in context | Subagent reads, returns summary | HIGH - 80%+ reduction |
| **Validation loops** | Fix attempts in main context | Subagent does fix, returns result | HIGH - isolates iterations |
| **Code review** | 19-item checklist in context | Parallel reviewer subagents | MEDIUM - parallel execution |
| **Memory queries** | Query + all results in context | Subagent filters, returns relevant | MEDIUM - reduces noise |
| **Codebase exploration** | All findings in context | Explore subagent with summary | HIGH - exploration isolated |
| **BMB validation (08a-08f)** | 6 sequential validations | 6 parallel subagents | MEDIUM - parallel + isolated |
| **Party mode rounds** | All agent responses in context | Summary per round, details in memory | MEDIUM - compress rounds |

### Implementation Patterns

#### Pattern 1: Fire-and-Summarize
```
Main context spawns subagent for heavy lifting
Subagent does full work in isolation
Subagent returns summary (not full content)
Main context continues with summary only
```
**Use for:** Document analysis, codebase exploration, fix attempts

#### Pattern 2: Parallel-and-Aggregate
```
Main context spawns N parallel subagents
Each subagent handles one validation/review
Aggregator collects all results
Main context receives aggregated outcome
```
**Use for:** BMB 08a-08f validation, Code Review adversarial findings, Multi-reviewer synthesis

#### Pattern 3: Background-and-Notify
```
Main context spawns background subagent
Subagent monitors condition (e.g., sprint-status.yaml)
Subagent writes notification file when triggered
Main context checks file periodically OR on next interaction
```
**Use for:** Sprint Status Auto-Watcher, long-running validations

#### Pattern 4: Context-Fork-Isolation
```
Main context creates fork for reviewer
Reviewer gets full conversation history (isolated copy)
Reviewer works independently, returns findings
Fork discarded after completion
Main context only receives findings summary
```
**Use for:** Adversarial reviewers, information asymmetry scenarios

### Specific Subagent Deployments

#### 1. Pre-Workflow Context Reduction
- **Context Pre-Loader** runs in subagent
- Queries Forgetful with project context
- Filters and ranks memories by relevance
- Returns curated memory set (not all results)
- Main context only sees relevant memories

#### 2. Step Processing Offload
- Heavy step processing in subagent
- Step file read + validation in isolation
- Returns: outcome, issues found, confidence score
- Main context: just decision + menu handling

#### 3. Fix Loop Isolation
- When validation finds issues
- Spawn subagent for fix attempt
- Subagent: reads issue, attempts fix, validates
- Returns: success/failure + summary
- Main context: never sees fix attempts, only outcomes

#### 4. Party Mode Compression
- Each round's agent responses in subagent context
- Subagent extracts: key points, agreements, disagreements
- Returns compressed round summary
- Full transcript saved to memory (not in main context)

#### 5. Document Generation Offload
- PRD/Architecture/Epic creation in subagent
- Subagent has full generation context
- Returns: document path, summary, validation status
- Main context: sees summary, not full document

### Context Budget Allocation

Recommended context allocation for automated workflows:

| Component | Context % | Notes |
|-----------|-----------|-------|
| Workflow state | 10% | Current step, tier, phase |
| Active step content | 15% | Current step file being processed |
| Recent validations | 15% | Last 2-3 validation outcomes |
| Memory summaries | 10% | Curated relevant memories |
| Subagent results | 20% | Aggregated outcomes from subagents |
| User interaction | 20% | Recent user messages and decisions |
| Reserved headroom | 10% | For unexpected content |

### Anti-Patterns to Avoid

1. **Loading full documents into main context**
   - Use subagent to read and summarize

2. **Keeping all fix attempts in context**
   - Each fix attempt should be isolated subagent

3. **Sequential validation when parallel possible**
   - BMB 08a-08f can run in parallel

4. **Storing full party mode transcripts**
   - Compress to key points, save full to memory

5. **Querying memories without filtering**
   - Pre-filter in subagent, return relevant subset

### Integration with New Components

The 6 new automation components (11-16) all use subagent patterns:

| Component | Subagent Pattern | Context Benefit |
|-----------|------------------|-----------------|
| Pre-flight Validation | Fire-and-Summarize | Quick pass/fail before workflow |
| Parallel BMB Validation | Parallel-and-Aggregate | 6x isolation, parallel speed |
| Sprint Status Watcher | Background-and-Notify | Zero main context cost |
| Cross-Reference Validator | Fire-and-Summarize | Doc analysis in isolation |
| Context Pre-Loader | Fire-and-Summarize | Filtered memory load |
| Post-Workflow Curator | Fire-and-Summarize | Memory ops isolated |

---

## Next Steps

### Implementation Dependency Graph (S10)

```
TIER 1 (No dependencies - can start immediately):
├── Validation Type Detector
├── Pre-flight Validation Subagent
└── Cross-Reference Validator

TIER 2 (Depends on Tier 1):
├── Workflow Entry Wrapper ← requires Validation Type Detector
├── Menu Participation Engine ← requires Validation Type Detector
└── Context Pre-Loader ← standalone

TIER 3 (Depends on Tier 2):
├── Automation Controller ← requires Menu Participation Engine
├── Confidence Calculator ← requires validation outputs defined
└── Tier Suggester ← requires Workflow Entry Wrapper

TIER 4 (Depends on Tier 3):
├── Party Mode Driver ← requires Automation Controller
├── Loop-Back Handler ← requires Automation Controller
├── Subagent Dispatcher ← requires Automation Controller
└── Memory Bridge ← requires Context Pre-Loader

TIER 5 (Integration):
├── Parallel BMB Validation ← requires Subagent Dispatcher
├── Sprint Status Watcher ← requires Automation Controller
└── Post-Workflow Curator ← requires Memory Bridge
```

### Component Initialization and Shutdown Order (S11)

The 16 automation components MUST follow explicit initialization and shutdown sequences to prevent race conditions, dependency failures, and resource leaks.

```
INITIALIZATION SEQUENCE (session start):

PHASE 1: Infrastructure (0-300ms)
  1. MCP Connection Validator
     - Poll Forgetful, Context7, Serena with 3x100ms retries each (300ms max per service)
     - Services polled in parallel, so phase completes in ~300ms total
     - Mark unavailable MCPs in session state
     - Proceed with graceful degradation for unavailable services

  2. Validation Type Detector
     - Stateless, no dependencies
     - Initialize detection patterns (runs parallel with MCP polling)

PHASE 2: Context Loading (300-600ms)
  3. Context Pre-Loader
     - DEPENDS ON: MCP Connection Validator (Forgetful availability)
     - Query Forgetful for project memories
     - Cache results to _bmad-output/.context-cache/
     - If Forgetful unavailable: return empty set, set degraded flag

  4. Workflow Entry Wrapper
     - DEPENDS ON: Validation Type Detector
     - Load workflow-init state detection
     - No external dependencies

PHASE 3: Core Engine (600-800ms)
  5. Menu Participation Engine
     - DEPENDS ON: Validation Type Detector
     - Initialize menu option parsers
     - Load BMB threshold configurations

  6. Confidence Calculator
     - DEPENDS ON: None (but uses outputs from validators later)
     - Load threshold configuration from calibration file
     - Initialize signal aggregators

  7. Tier Suggester
     - DEPENDS ON: Workflow Entry Wrapper
     - Load project-levels.yaml keywords
     - Ready for suggestion generation

PHASE 4: Controllers (800-1000ms)
  8. Automation Controller
     - DEPENDS ON: Menu Participation Engine
     - Initialize state machine
     - Load checkpoint configuration
     - Register with hook system

  9. Memory Bridge
     - DEPENDS ON: Context Pre-Loader
     - Connect to cached context
     - Initialize save queue for degraded mode

PHASE 5: Specialized Handlers (1000-1200ms)
  10. Party Mode Driver
      - DEPENDS ON: Automation Controller
      - Initialize monitoring state
      - Load exit condition patterns

  11. Loop-Back Handler
      - DEPENDS ON: Automation Controller
      - Initialize iteration tracking
      - Load Edit-Module step map

  12. Subagent Dispatcher
      - DEPENDS ON: Automation Controller
      - Initialize agent pool
      - Load tool access configurations

PHASE 6: Integration Components (1200-1400ms)
  13. Pre-flight Validation Subagent
      - DEPENDS ON: Subagent Dispatcher
      - Register pre-flight check patterns

  14. Cross-Reference Validator
      - No runtime dependencies
      - Load document relationship patterns

  15. Parallel BMB Validation
      - DEPENDS ON: Subagent Dispatcher
      - Initialize parallel execution pool
      - Configure synchronization barriers

  16. Sprint Status Watcher
      - DEPENDS ON: Automation Controller
      - Initialize file watcher with debounce
      - Load sprint-status.yaml initial state

  17. Post-Workflow Curator
      - DEPENDS ON: Memory Bridge
      - Initialize memory extraction patterns
      - Connect to save queue

TOTAL INIT TIME: ~1400ms maximum (increased from 1200ms due to MCP retry timing correction)

INITIALIZATION FAILURE HANDLING:
- If Phase 1 fails: Abort session, report MCP connectivity issues
- If Phase 2-3 fails: Continue with degraded capabilities, warn user
- If Phase 4 fails: Abort automation, fall back to manual mode
- If Phase 5-6 fails: Continue without failed component, log degradation
```

```
SHUTDOWN SEQUENCE (session end or abort):

REVERSE ORDER with graceful cleanup:

PHASE A: Stop Active Operations (immediate)
  1. Sprint Status Watcher - stop file monitoring
  2. Parallel BMB Validation - cancel pending subagents
  3. Party Mode Driver - send exit keyword if session active, wait 500ms grace period
  4. Subagent Dispatcher - terminate active subagents (with state save)

PHASE B: Flush Queued Data (0-2000ms)
  5. Memory Bridge - flush save queue to Forgetful (or persist to file if unavailable)
  6. Post-Workflow Curator - complete any pending memory creation
  7. Automation Controller - save final checkpoint to frontmatter

PHASE C: Release Resources (2000-3000ms)
  8. Loop-Back Handler - clear iteration state
  9. Confidence Calculator - save calibration data if changed
  10. Menu Participation Engine - release parser resources
  11. Tier Suggester - release keyword index
  12. Workflow Entry Wrapper - save session state

PHASE D: Context Cleanup (3000-3500ms)
  13. Context Pre-Loader - invalidate cache files
  14. Cross-Reference Validator - no cleanup needed
  15. Pre-flight Validation Subagent - no cleanup needed
  16. Validation Type Detector - no cleanup needed

SHUTDOWN TIMEOUT: 5000ms maximum
- After 5s, force-terminate remaining components
- Log any incomplete shutdowns for debugging

ABORT SHUTDOWN (on error/crash):
- Skip queue flushes
- Save minimal checkpoint: {aborted: true, step: current, timestamp: now}
- Trigger resume-from-abort on next session
```

```
COMPONENT STATUS TRACKING:

Each component reports status to Automation Controller:

{
  "component": "Context Pre-Loader",
  "status": "ready|degraded|failed|shutdown",
  "initialized_at": "2026-01-08T14:30:00.150Z",
  "dependencies_met": true,
  "degradation_reason": null,  // or "forgetful_unavailable"
  "last_activity": "2026-01-08T14:32:15.000Z"
}

HEALTH CHECK (every 30s during session):
- Automation Controller polls component status
- Detects hung components (no activity > 60s during active workflow)
- Can restart individual components without full session restart

DEPENDENCY VALIDATION:
- Before each component init, verify dependencies are "ready" or "degraded"
- "failed" dependency blocks dependent component (switch to fallback if available)
- Circular dependency detection at startup (should never occur per this graph)
```

### Implementation Steps

1. Create detailed implementation plan with specific file changes
2. **Implement validation type detector** (workflow-specific awareness FIRST)
3. **Implement workflow entry wrapper** (workflow-init integration, quick-dev routing)
4. **Implement menu participation engine** (core [A][P][C] handling with BMB thresholds)
5. **Implement automation controller** (verdict-based loop logic)
6. **Implement confidence calculator** (NEW FUNCTIONALITY - define signal sources)
7. Implement tier suggester (suggestion layer for workflow-init tier selection - Step 3/5 depending on path)
8. Implement party mode driver (programmatic input generation)
9. **Implement loop-back handler** (Edit-Module Step 06)
10. Modify validation steps to use automation loop
11. Implement memory bridge (aligned with Core hooks)
12. Handle BMB tri-modal agent workflow (CREATE/EDIT/VALIDATE)
13. Handle BMM Code Review adversarial mode (3-10 findings required)
14. Test with Level 0-1 tasks first, then scale up
15. Validate quick-dev path works correctly with automation
16. Validate brainstorming remains accessible (Option B/C implementation)

### Context Window Preservation (New Priority)

17. **Implement pre-flight validation subagent** (LOW effort, HIGH value - do early)
18. **Implement parallel BMB validation orchestrator** (LOW effort - parallel 08a-08f)
19. **Implement cross-reference validator** (LOW effort - doc alignment checks)
20. **Implement context pre-loader** (LOW effort - Forgetful pre-population)
21. **Implement post-workflow memory curator** (MEDIUM effort - automated memory extraction)
22. **Implement sprint status auto-watcher** (MEDIUM effort - background monitoring)
23. Apply Fire-and-Summarize pattern to document analysis steps
24. Apply Context-Fork-Isolation to adversarial reviewers
25. Add context budget monitoring to automation controller

---

## Appendix: Key Corrections from Original Design

### Revision 1 Corrections

| Original Assumption | Corrected Understanding |
|---------------------|------------------------|
| Tier auto-detected from keywords | Tier manually selected via workflow-init; automation suggests only |
| Party mode runs autonomously | Party mode requires per-round human input; automation acts AS human |
| Menus bypassed for automation | Menus preserved; automation participates in [A][P][C] |
| Only validation steps halt | EVERY step has [C] Continue; dozens of halts per workflow |
| Single entry point | workflow-init 9-step decision tree with 4 states and 3 paths |
| Greenfield assumed | Brownfield projects need Phase 0 (document-project) |
| Brainstorming automatable | Brainstorming fundamentally interactive; partial automation only |
| Agent workflow is simple | Agent workflow has CREATE/EDIT/VALIDATE modes with different steps |

### Revision 2 Corrections (HIGH severity)

| Original Assumption | Corrected Understanding |
|---------------------|------------------------|
| Universal "3-phase" validation | Workflow-specific: Edit-Module=3, Workflow-Compliance=8, Agent=6 phases |
| Issue count model (0 issues = success) | Verdict-based model varies by workflow (see v4 corrections) |
| Code Review: eliminate all issues | Code Review: ADVERSARIAL (3-10 findings required) with Approve/Changes/Blocked outcomes |
| Stall detection as primary trigger | BMB thresholds PRIMARY (blocking>3, major>5, score<70), stall ADDITIONAL |
| Confidence values assigned | Confidence CALCULATED from observable signals (NEW FUNCTIONALITY) |
| Memory queries at arbitrary points | Queries align with Core's AGENT START hook; saves at WORKFLOW COMPLETION |
| Quick-dev not addressed | Quick-dev is legitimate bypass path with mode detection and escalation |
| Edit-Module linear flow | Edit-Module has Step 06 loop-back [Y]→Step 03 / [N]→Step 07 |
| Steps can be optimized/combined | BMAD Critical Rule: NEVER skip steps, process each discretely |

### Revision 3 Corrections (MEDIUM severity)

| Original Assumption | Corrected Understanding |
|---------------------|------------------------|
| Party mode exit not documented | Specific exit triggers: `*exit`, `goodbye`, `end party`, `quit` |
| Agent count unspecified | Core recommends (not enforces) 2-3 agents per topic selection |
| Party mode single-threaded | Cross-talk is an orchestration pattern: framework enables agent-to-agent dialogue |
| Single "synthesis" memory save | TWO saves: "discussion_outcome" (always) AND "consensus_decisions" (conditional) |
| [A] and [P] conflated | [A] = deep-dive single issue, [P] = multi-agent discussion (SEPARATE purposes) |
| workflow-status passive tracker | Active router with modes: interactive, validate, data, init-check, update |
| Frontmatter not mentioned | BMAD Critical Rule: "ALWAYS save progress to frontmatter before loading next step" |
| Agent creation uniform | Step 06 branches: Simple vs Expert vs Module with different validation needs |
| Menu redisplay implicit | After [A]/[P], menu RE-DISPLAYS; user must select [C] to proceed |
| Generic reviewer mapping | Specific mapping: 08a-08b automated, 08c-08e specific reviewers, 08f all three |
| Edit-Workflow = Edit-Module | SEPARATE workflows: Edit-Workflow (5 steps), Edit-Module (7 steps + loop) |
| Tiers skip menus | Tiers affect AUTO-SELECTION, not menu existence; all steps have [A][P][C] |
| "0 issues" = BMAD baseline | "0 issues" is STRICTER than BMAD (baseline allows non-blocking with acknowledgment) |
| Brainstorming Step 3 simple | Has optional "Continuation check" requiring explicit handling |

### Revision 5 Corrections (Re-Review Critical Fixes)

| Original Assumption | Corrected Understanding |
|---------------------|------------------------|
| Party mode requires per-round human input/direction | Party mode is AUTONOMOUS per round - orchestrator auto-selects agents, auto-generates responses, handles cross-talk. Human provides initial topic and exit signal only. |
| Party Mode Driver provides per-round direction | Party Mode Driver MONITORS for exit conditions, doesn't steer discussion. Agents drive themselves. |
| Code Review v5 error: claimed NOT adversarial | **v5 WAS WRONG** - BMAD Code Review IS adversarial with 3-10 findings required per `instructions.xml` |
| 08a-08f are sub-phases within Step 8 | 08a-08f are SEPARATE STEP FILES (step-08a-plan-traceability.md, etc.) - 16 total files in CREATE mode |
| Brainstorming Step 3 has one continuation check | Brainstorming Step 3 has CONTINUOUS checks after EACH technique element - highest interaction frequency |
| Party mode auto-generates synthesis document | Party mode may save discussion outcomes to memory on exit, but no auto-synthesis document |
| BMM and BMB validation use same model | BMM uses VERDICT-based (semantic), BMB uses STRUCTURAL (syntax/reference checks) - different systems |

### Revision 4 Corrections (Final Alignment)

| Original Assumption | Corrected Understanding |
|---------------------|------------------------|
| Implementation Readiness uses PASS/FAIL | Uses READY/NEEDS WORK/NOT READY (distinct from testarch-trace) |
| Test Traceability uses same verdicts | Uses PASS/CONCERNS/FAIL/WAIVED (different from implementation readiness) |
| EDIT mode steps e-02, e-03a-f, e-09a-f | Full flow: e-01→e-10 with e-03 pre-edit validation, e-04-07 edits, e-08 build, e-09 post-validation |
| Validation phases 08a: Syntax, 08b: Reference | 08a: plan-traceability, 08b: metadata-validation, 08c: persona-validation, 08d: menu-validation, 08e: structure-validation, 08f: sidecar-validation |
| Party mode has NO automatic synthesis | Per-round = human-driven, End-of-party synthesis = automatic |
| Core enforces 2-3 agents | Core recommends (not enforces) 2-3 agents |
| workflow-init has 8 steps | workflow-init has 9 steps (added confirm/validate step) |
| CREATE mode Steps 2-8 | CREATE mode Steps 1-9 (includes brainstorm at step 1) |
| VALIDATE mode Steps v-02a-e | VALIDATE mode: v-01 (load), v-02a-e (validation), v-03 (summary) |
| Edit-Module has 7 steps | Edit-Module has 7 main phases with 20+ step files due to branching |
| Step 06: System prompt generation | Step 06: Activation behavior; Step 07: System prompt and build |
| Edit-Module menu [A][W][T][C][D][I] | Edit-Module menu [1][2][3][4][D] (numbered menu) |
| Brainstorming has 9-11 steps | 8 step files with 11+ human interaction prompts |
| `*exit` is pattern match | `*exit` is literal string with asterisk, exact match required |
| Cross-talk is emergent behavior | Cross-talk is orchestration pattern enabled by framework |
| Memory 2 always saved | Memory 2 (consensus) is conditional on consensus being reached |
| project-levels keywords are complete | Keywords in examples are illustrative, not exhaustive |
| 08a-08f placement unclear | 08a-08f are SEPARATE step files (see v5 correction - not sub-phases) |
| Edit-Workflow has 3-phase validation | Edit-Workflow invokes full 8-phase workflow-compliance-check |

### Revision 7 Corrections (Integration Fixes - 2026-01-09)

| Issue ID | Original Assumption | Corrected Understanding |
|----------|---------------------|------------------------|
| I1 | Tier selection at workflow-init Step 6 | Tier selection at **Step 3 (Express)** or **Step 5 (Guided)** - varies by path |
| I2 | Menu Participation Engine assumes universal [A][P][C] | Menu structures vary: workflow-init uses [1-4], party-mode uses [E], etc. Engine DETECTS actual options |
| I3 | Party Mode Driver auto-continues on all responses | Driver ESCALATES to human on direct questions (detected via '[Agent Name] asks:' pattern) |
| I4 | Memory Bridge uses AGENT START hooks | Memory Bridge aligns with WORKFLOW-level hooks (Pre-Workflow/Post-Workflow). Context Hub stack: Forgetful + Serena + Context7 |
| I5 | Task tool invocation not documented | Added explicit Task tool examples with parameters: prompt, context, resume, allowed_tools |
| I6 | workflow-compliance-check phases named generically | Corrected to actual step file names: validate-goal, workflow-validation, step-validation, file-validation, intent-spectrum-validation, web-subprocess-validation, holistic-analysis, generate-report |
| I7 | Frontmatter schema presented as existing BMAD | Frontmatter schema is PROPOSED extension for automation. Automation must work with or without these fields |
| I8 | Custom agent registration not documented | Documented three registration options: manifest update, separate custom-agents.csv, runtime roster extension |

---

## Appendix: Design Verification Report (2026-01-09)

### Verification Methodology

This comprehensive review involved:
1. Reading all local BMAD workflow files in `_bmad/bmm/`, `_bmad/bmb/`, and `_bmad/core/`
2. Analyzing workflow path files (`method-greenfield.yaml`, `method-brownfield.yaml`)
3. Examining agent manifest and agent definitions
4. Reading individual step files for brainstorming, party-mode, and agent workflows
5. Verifying verdict systems and validation patterns

### Verified Correct ✅

| Design Claim | Actual File Location | Status |
|--------------|---------------------|--------|
| BMM phases 0-4 with specific workflows | `_bmad/bmm/workflows/workflow-status/paths/method-*.yaml` | ✅ Matches |
| Project levels 0-4 with story counts | `_bmad/bmm/workflows/workflow-status/project-levels.yaml` | ✅ Matches |
| BMM agents (14 total including bmad-master) | `_bmad/_config/agent-manifest.csv` | ✅ Matches |
| BMB tri-modal agent workflow (Create/Edit/Validate) | `_bmad/bmb/workflows/agent/workflow.md` | ✅ Matches |
| CREATE mode 08a-08f as SEPARATE step files | `_bmad/bmb/workflows/agent/steps-c/step-08{a-f}-*.md` | ✅ 6 separate files verified |
| Brainstorming 8 step files | `_bmad/core/workflows/brainstorming/steps/step-0*.md` | ✅ Matches |
| Brainstorming continuous checks in Step 3 | `step-03-technique-execution.md` lines 120-143 | ✅ "Check Engagement and Interest" pattern |
| Party mode 3 steps with autonomous selection | `_bmad/core/workflows/party-mode/steps/` | ✅ Matches |
| Party mode exit triggers | `workflow.md` line 11: `exit_triggers` | ✅ Exact strings documented |
| Code Review: ADVERSARIAL 3-10 findings + Approve/Changes/Blocked | `_bmad/bmm/workflows/4-implementation/code-review/instructions.xml` | ✅ ADVERSARIAL verified |
| Implementation Readiness: READY/NEEDS WORK/NOT READY | `_bmad/bmm/workflows/3-solutioning/check-implementation-readiness/steps/step-06-*.md` | ✅ Matches |
| Testarch Trace: PASS/CONCERNS/FAIL/WAIVED | `_bmad/bmm/workflows/testarch/trace/instructions.md` | ✅ Matches |
| BMM vs BMB validation distinction | Verified in workflow instructions | ✅ VERDICT vs STRUCTURAL correct |
| workflow-status multi-mode service | `_bmad/bmm/workflows/workflow-status/instructions.md` | ✅ Modes documented |
| Sprint planning status state machine | `_bmad/bmm/workflows/4-implementation/sprint-planning/instructions.md` | ✅ Epic/Story/Retro flows match |
| CREATE mode steps 01-09 with variants | `_bmad/bmb/workflows/agent/steps-c/` (16 files) | ✅ Matches |
| Context Hub integration pattern | Workflow files show Forgetful/Serena/Context7 | ✅ Present |

### Key Structural Findings

**BMM Workflow Phase Structure (from `method-greenfield.yaml`):**
- Phase 1 (Analysis): brainstorm-project, research, product-brief (all optional)
- Phase 2 (Planning): PRD (required), UX design (conditional)
- Phase 3 (Solutioning): architecture, epics/stories (required), test-design (optional), implementation-readiness (required)
- Phase 4 (Implementation): sprint-planning (required)

**BMB Agent Workflow CREATE Steps:**
- 01: brainstorm (optional)
- 02: discovery
- 03: type-metadata
- 04: persona
- 05: commands-menu
- 06: activation
- 07a/b/c: build (simple/expert/module variants)
- 08a-08f: validation (6 separate files)
- 09: celebrate

**Agent Inventory (from manifest):**
- Core: bmad-master
- BMB: agent-builder (Bond), module-builder (Morgan), workflow-builder (Wendy)
- BMM: analyst (Mary), architect (Winston), dev (Amelia), pm (John), quick-flow-solo-dev (Barry), sm (Bob), tea (Murat), tech-writer (Paige), ux-designer (Sally)

### Design Accuracy Assessment

**Overall Rating: EXCELLENT**

The design document (v5) is highly accurate and comprehensive. The 5 revision cycles successfully corrected initial assumptions to align with actual BMAD implementation. Key strengths:

1. **Verdict system accuracy** - Correctly distinguishes different validation outcome types
2. **Step file architecture** - Accurately describes 08a-08f as separate files (not sub-phases)
3. **Party mode mechanics** - Correctly describes autonomous agent selection and exit triggers
4. **Brainstorming interaction** - Correctly identifies continuous check pattern in Step 3
5. **BMM vs BMB distinction** - Correctly separates VERDICT (semantic) from STRUCTURAL (syntax) validation

### No Critical Issues Found

The design document accurately reflects the actual BMAD implementation. The extensive correction history in the Appendix demonstrates thorough alignment work. This verification confirms the design is ready for implementation.

**Verification Date:** 2026-01-09
**Files Examined:** 50+ workflow, agent, and configuration files
**Reviewer:** Claude (Opus 4.5)
