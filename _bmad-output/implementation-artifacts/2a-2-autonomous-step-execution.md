# Story 2a.2: Autonomous Step Execution

**Epic:** 2a - Workflow Entry & Detection
**Story ID:** 2a.2
**Status:** In Progress
**Created:** 2026-01-12

## Story Definition

**As a** workflow user,
**I want** workflows to execute autonomously without prompting me at each step,
**So that** I can focus on decisions rather than clicking "continue" repeatedly.

## Acceptance Criteria

### AC1: Auto-Transition on Verdict PASSED
**Given** a workflow with steps 1, 2, 3 and verdict-based success criteria
**When** step 1 completes with verdict "PASSED"
**Then** the system automatically transitions to step 2 without user prompt

### AC2: Pause for Oversight
**Given** a workflow step with `oversight: required` in configuration
**When** the step completes successfully
**Then** the system pauses for user confirmation before proceeding

### AC3: Recovery on Failure
**Given** a workflow step that fails validation
**When** the Automation Controller detects the failure
**Then** it attempts recovery before escalating to user (per FR16)

### AC4: Full Autonomous Execution
**Given** a workflow with no oversight requirements
**When** all steps complete successfully
**Then** the entire workflow completes autonomously with only a final summary

## Functional Requirements Covered

- **FR2:** Automation Controller can execute workflows autonomously without user prompts at each step
- **FR3:** Automation Controller can transition between workflow steps based on verdict-based success criteria
- **FR6:** Automation Controller can respect task-level oversight requirements defined in workflow configuration

## Dependencies

| Dependency | Module | Purpose |
|------------|--------|---------|
| ValidationTypeResult | validation_type_detector.py | Provides verdict detection (PASSED/FAILED/etc.) |
| WorkflowConfig | workflow_entry_wrapper.py | Provides configuration reading and oversight settings |
| PreflightResult | preflight_validator.py | Provides validation infrastructure patterns |

## Technical Design

### Module: `pcmrp_tools/bmad_automation/step_executor.py`

### Data Structures

```python
class StepStatus(Enum):
    """Status of a workflow step execution."""
    PENDING = "pending"        # Not yet started
    RUNNING = "running"        # Currently executing
    PASSED = "passed"          # Completed successfully
    FAILED = "failed"          # Completed with failure
    SKIPPED = "skipped"        # Skipped (dependencies not met)
    AWAITING_USER = "awaiting_user"  # Paused for user confirmation

@dataclass
class StepResult:
    """Result of executing a single workflow step."""
    step_id: str
    status: StepStatus
    verdict: str | None = None  # e.g., "PASSED", "FAILED", "CONCERNS"
    output: str = ""
    errors: list[str] = field(default_factory=list)
    duration_ms: int = 0
    recovery_attempted: bool = False

@dataclass
class StepExecutionConfig:
    """Configuration for step execution behavior."""
    oversight: str = "none"  # "none", "required", "optional"
    auto_continue: bool = True
    max_recovery_attempts: int = 3
    timeout_ms: int = 300000  # 5 minutes default
```

### Functions

1. **`execute_step(step_id, step_config, execution_config) -> StepResult`**
   - Executes a single workflow step
   - Returns StepResult with status, verdict, output, errors

2. **`should_auto_transition(result, config) -> bool`**
   - Determines if automatic transition to next step is allowed
   - Checks: verdict is PASSED, no oversight required, auto_continue enabled

3. **`attempt_recovery(result, step_config, attempt_num) -> StepResult`**
   - Attempts to recover from a step failure
   - Uses validation result patterns to determine recovery strategy
   - Returns new StepResult after recovery attempt

4. **`execute_workflow_steps(steps, workflow_config) -> WorkflowExecutionResult`**
   - Orchestrates sequential step execution
   - Handles auto-transitions, oversight pauses, and recovery
   - Returns aggregate result with all step results

### Integration Points

- Uses `ValidationTypeResult` for verdict detection
- Uses `WorkflowConfig` for oversight and threshold settings
- Follows same patterns as `PreflightResult` for status tracking

## Test Plan

### Unit Tests (TDD)

1. **StepStatus Enum Tests**
   - All enum values exist and have correct string values
   - Enum comparison and serialization works

2. **StepResult Tests**
   - Creation with all fields
   - Factory methods (passed, failed, awaiting_user)
   - to_dict/from_dict serialization

3. **StepExecutionConfig Tests**
   - Default values
   - Custom configuration
   - Validation of oversight values

4. **execute_step Tests**
   - Returns PASSED status on successful execution
   - Returns FAILED status on execution failure
   - Captures output and errors
   - Respects timeout configuration

5. **should_auto_transition Tests**
   - Returns True for PASSED verdict with no oversight
   - Returns False for FAILED verdict
   - Returns False when oversight is required
   - Returns False when auto_continue is disabled
   - Handles CONCERNS verdict (configurable behavior)

6. **attempt_recovery Tests**
   - Attempts recovery up to max_recovery_attempts
   - Returns success after successful recovery
   - Returns failure after max attempts exceeded
   - Sets recovery_attempted flag

7. **execute_workflow_steps Tests**
   - Executes all steps sequentially
   - Auto-transitions between steps on PASSED
   - Pauses at oversight-required steps
   - Attempts recovery on failures
   - Returns final summary

### Integration Tests

1. **Full Workflow Execution**
   - Execute 3-step workflow with all PASSED
   - Execute workflow with oversight pause
   - Execute workflow with recovery scenario

## File Locations

| Artifact | Path |
|----------|------|
| Implementation | `pcmrp_tools/bmad_automation/step_executor.py` |
| Tests | `tests/bmad_automation/test_step_executor.py` |
| Spec (this file) | `_bmad-output/implementation-artifacts/2a-2-autonomous-step-execution.md` |

## Progress Tracking

- [x] Spec created
- [x] StepStatus enum tests written and passing (8 tests)
- [x] StepResult tests written and passing (12 tests)
- [x] StepExecutionConfig tests written and passing (7 tests)
- [x] execute_step tests written and passing (6 tests)
- [x] should_auto_transition tests written and passing (13 tests)
- [x] attempt_recovery tests written and passing (5 tests)
- [x] execute_workflow_steps tests written and passing (8 tests)
- [x] WorkflowExecutionResult tests written and passing (3 tests)
- [x] Edge case tests added (5 tests)
- [x] Integration tests (3 tests)
- [x] __init__.py updated with exports
- [x] Coverage verified at 99% (70 tests total, all passing)

## Implementation Summary

**Completed:** 2026-01-12

### Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `pcmrp_tools/bmad_automation/step_executor.py` | Created | 174 lines - Core step execution module |
| `tests/bmad_automation/test_step_executor.py` | Created | 1300+ lines - Comprehensive test suite |
| `pcmrp_tools/bmad_automation/__init__.py` | Modified | Added 12 new exports |
| `_bmad-output/implementation-artifacts/2a-2-autonomous-step-execution.md` | Created | This spec file |

### Test Results

- **Total Tests:** 70
- **Passed:** 70
- **Failed:** 0
- **Coverage:** 99% for step_executor.py

### Components Implemented

1. **StepStatus Enum** - 6 statuses (PENDING, RUNNING, PASSED, FAILED, SKIPPED, AWAITING_USER)
2. **WorkflowStatus Enum** - 5 statuses (PENDING, RUNNING, COMPLETED, FAILED, PAUSED)
3. **StepResult Dataclass** - With factory methods and serialization
4. **StepExecutionConfig Dataclass** - Configuration for step execution
5. **WorkflowExecutionResult Dataclass** - Aggregate workflow result
6. **Verdict Constants** - SUCCESS_VERDICTS, CONCERN_VERDICTS, FAILURE_VERDICTS
7. **should_auto_transition()** - Verdict-based transition logic
8. **attempt_recovery()** - Recovery attempt logic
9. **execute_step()** - Single step execution
10. **execute_workflow_steps()** - Workflow orchestration
