# Story 2b.3: BMB-Specific Menu Thresholds

Status: done

## Story

As a **workflow automation system**,
I want **BMB-specific threshold checks that trigger escalation independently of confidence scoring**,
So that **high-severity validation issues automatically escalate to Party Mode or Advanced Elicitation before stall detection kicks in**.

## Acceptance Criteria

1. **Given** validation results with `blocking_errors > 3`
   **When** the BMB threshold checker evaluates the results
   **Then** it returns a `PartyModeEscalation` action with reason "High blocking error count: {count}"

2. **Given** validation results with `major_issues > 5`
   **When** the BMB threshold checker evaluates the results
   **Then** it returns a `PartyModeEscalation` action with reason "High major issue count: {count}"

3. **Given** validation results with `compliance_score < 70`
   **When** the BMB threshold checker evaluates the results
   **Then** it returns an `AdvancedElicitationEscalation` action with reason "Low compliance score: {score}%"

4. **Given** validation results meeting multiple thresholds (e.g., blocking > 3 AND major > 5)
   **When** the BMB threshold checker evaluates the results
   **Then** it prioritizes `PartyModeEscalation` over `AdvancedElicitationEscalation` (highest severity wins)

5. **Given** validation results not meeting any BMB threshold
   **When** the BMB threshold checker evaluates the results
   **Then** it returns `NoEscalation` action, allowing normal confidence-based flow

6. **Given** BMB threshold check is invoked
   **When** the check completes
   **Then** the check executes in under 100ms (NFR: lightweight threshold checks)

## Tasks / Subtasks

### Task 1: Create BMBThresholdChecker Class (AC: #1, #2, #3)

- [x] Task 1.1: Define EscalationAction enum (PartyMode, AdvancedElicitation, NoEscalation)
- [x] Task 1.2: Create EscalationResult dataclass (action, reason, threshold_violated, threshold_value)
- [x] Task 1.3: Define BMB threshold constants:
  - [x] BLOCKING_ERROR_THRESHOLD = 3
  - [x] MAJOR_ISSUE_THRESHOLD = 5
  - [x] COMPLIANCE_SCORE_THRESHOLD = 70
- [x] Task 1.4: Create ValidationMetrics dataclass (blocking_errors, major_issues, compliance_score)
- [x] Task 1.5: Implement check_blocking_errors() → Optional[EscalationResult]
- [x] Task 1.6: Implement check_major_issues() → Optional[EscalationResult]
- [x] Task 1.7: Implement check_compliance_score() → Optional[EscalationResult]
- [x] Task 1.8: Write tests for each threshold boundary condition

### Task 2: Implement Priority Logic (AC: #4)

- [x] Task 2.1: Implement evaluate_all_thresholds() returning highest-priority escalation
- [x] Task 2.2: Define priority order: PartyMode (blocking) > PartyMode (major) > AdvancedElicitation
- [x] Task 2.3: Implement combine_escalation_reasons() for multi-threshold violations
- [x] Task 2.4: Write tests for priority ordering and combination scenarios

### Task 3: Implement No-Escalation Path (AC: #5)

- [x] Task 3.1: Implement is_within_thresholds() returning bool
- [x] Task 3.2: Ensure check_all() returns NoEscalation when all thresholds pass
- [x] Task 3.3: Write tests for normal flow scenarios

### Task 4: Performance Validation (AC: #6)

- [x] Task 4.1: Add timing instrumentation to evaluate_all_thresholds()
- [x] Task 4.2: Implement performance_check() asserting < 100ms
- [x] Task 4.3: Write performance tests with timing assertions

### Task 5: Integration with MenuSelector (AC: All)

- [x] Task 5.1: Add BMBThresholdChecker to MenuSelector initialization
- [x] Task 5.2: Implement pre-check hook: run BMB thresholds BEFORE confidence-based selection
- [x] Task 5.3: If escalation returned, bypass confidence logic and return escalation action
- [x] Task 5.4: Write integration tests showing BMB thresholds take precedence

## Dev Notes

### Architecture Context

**Component:** Menu Participation Engine - BMB Threshold Checks (extends Stories 2b.1, 2b.2)
- **Tier:** 2-3 (Depends on Story 2b.2 Automatic Menu Selection)
- **Purpose:** Implement BMB-specific quantitative thresholds that trigger escalation BEFORE confidence-based selection
- **Integration:** Pre-check hook in MenuSelector that runs before confidence evaluation

**BMB Threshold Hierarchy (from Architecture):**

```
PRIMARY CHECK (BMB thresholds - evaluated FIRST):
  IF blocking_errors > 3:
    → PartyModeEscalation (collaborative problem-solving)
  ELIF major_issues > 5:
    → PartyModeEscalation (collaborative problem-solving)
  ELIF compliance_score < 70:
    → AdvancedElicitationEscalation (deep investigation)
  ELSE:
    → NoEscalation (continue to confidence-based flow)

SECONDARY CHECK (confidence-based - only if no BMB escalation):
  → Story 2b.2's HighConfidenceSelector/MediumConfidenceSelector/LowConfidenceSelector
```

**Decision Flow:**

```
ValidationMetrics → BMBThresholdChecker.evaluate_all_thresholds()
  ├── PartyModeEscalation? → Return escalation, skip confidence logic
  ├── AdvancedElicitationEscalation? → Return escalation, skip confidence logic
  └── NoEscalation → Continue to MenuSelector.select_or_present()
```

### Technical Requirements

**Language:** Python 3.11+
**Testing Framework:** pytest with TDD (Red-Green-Refactor)
**File Location:** `pcmrp_tools/bmad_automation/bmb_thresholds.py`
**Test Location:** `tests/bmad_automation/test_bmb_thresholds.py`

### Code Patterns to Follow

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class EscalationAction(Enum):
    PARTY_MODE = "party_mode"           # [P] escalation
    ADVANCED_ELICITATION = "advanced"   # [A] escalation
    NO_ESCALATION = "none"              # Continue normal flow

@dataclass
class ValidationMetrics:
    blocking_errors: int = 0
    major_issues: int = 0
    compliance_score: int = 100  # 0-100 percentage

@dataclass
class EscalationResult:
    action: EscalationAction
    reason: str
    threshold_violated: Optional[str] = None
    threshold_value: Optional[int] = None

# BMB Threshold Constants (from Architecture Design)
BLOCKING_ERROR_THRESHOLD = 3   # > 3 triggers Party Mode
MAJOR_ISSUE_THRESHOLD = 5      # > 5 triggers Party Mode
COMPLIANCE_SCORE_THRESHOLD = 70 # < 70 triggers Advanced Elicitation

# Performance constraint
MAX_THRESHOLD_CHECK_MS = 100
```

### Testing Standards

- **100% test coverage required**
- **TDD cycle:** Write failing test FIRST, then implementation
- **Test file naming:** `test_bmb_thresholds.py`
- **Test function naming:** `test_<function>_<scenario>_<expected_result>`

### Edge Cases to Handle

1. Exactly at threshold (blocking=3, major=5, score=70) - should NOT escalate
2. All thresholds violated simultaneously - highest priority wins
3. Negative values (invalid input) - should raise ValueError
4. compliance_score outside 0-100 range - should raise ValueError
5. Multiple PartyMode triggers (blocking AND major) - combine reasons

### Dependencies

**Story 2b.2 Provides:**
- MenuSelector orchestrator
- SelectionResult dataclass
- SelectionLogger for audit trail

**This Story Provides (for downstream):**
- BMBThresholdChecker class
- EscalationResult for menu routing
- Pre-check hook pattern for automation controller

### References

- [Source: docs/plans/2026-01-08-bmad-automation-design.md#Stall Detection + BMB Thresholds]
- [Source: docs/plans/2026-01-08-bmad-automation-design.md#Decision matrix (includes BMB thresholds)]
- [Source: docs/plans/2026-01-08-bmad-automation-design.md#Menu Participation Engine]
- [Source: _bmad-output/implementation-artifacts/2b-2-automatic-menu-selection.md#Architecture Context]

## Dev Agent Record

### Agent Model Used

claude-opus-4-5-20251101 (via parallel subagents)

### Debug Log References

- Agent a1d204d: Tasks 1-2 (BMBThresholdChecker, Priority Logic)
- Agent a8aeade: Tasks 3-4 (NoEscalation Path, Performance Validation)
- Agent afbf915: Task 5 (MenuSelector Integration)
- Agent a79b51e: ADVERSARIAL Code Review

### Completion Notes List

- Task 1: Created EscalationAction enum (PARTY_MODE, ADVANCED_ELICITATION, NO_ESCALATION), EscalationResult dataclass, BMB threshold constants (BLOCKING=3, MAJOR=5, COMPLIANCE=70), ValidationMetrics dataclass, check methods for each threshold
- Task 2: Implemented evaluate_all_thresholds() with priority order: blocking > major > compliance, combine_escalation_reasons() for multi-threshold violations
- Task 3: Implemented is_within_thresholds() returning bool, check_all() returns NoEscalation when thresholds pass
- Task 4: Added timing instrumentation, performance_check() asserting < 100ms, performance tests
- Task 5: Integrated BMBThresholdChecker into MenuSelector as pre-check hook before confidence-based selection

### File List

- `pcmrp_tools/bmad_automation/bmb_thresholds.py` (NEW)
- `pcmrp_tools/bmad_automation/menu_selection.py` (MODIFIED - added pre-check hook)
- `tests/bmad_automation/test_bmb_thresholds.py` (NEW)

