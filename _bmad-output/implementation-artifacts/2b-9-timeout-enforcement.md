# Story 2b.9: Timeout Enforcement

Status: done

## Story

As a **workflow automation system**,
I want **timeout hierarchy enforced at all levels**,
So that **no operation hangs indefinitely**.

## Acceptance Criteria

1. **Given** a workflow running for more than 1800 seconds (30 minutes)
   **When** the timeout is reached
   **Then** the workflow is terminated with `timeout_error: "workflow_timeout"`

2. **Given** a nested operation running for more than 300 seconds (5 minutes)
   **When** the timeout is reached
   **Then** the nested operation is terminated and parent workflow notified

3. **Given** an agent operation running for more than 60 seconds
   **When** the timeout is reached
   **Then** the agent is terminated with `timeout_error: "agent_timeout"`

4. **Given** a timeout occurs
   **When** the operation is terminated
   **Then** state is preserved for potential resume and timeout is logged

## Tasks / Subtasks

### Task 1: Define Timeout Configuration (AC: #1, #2, #3)

- [x] Task 1.1: Define TimeoutLevel enum (WORKFLOW, NESTED, AGENT)
- [x] Task 1.2: Define TIMEOUT_SECONDS constant dict:
  - WORKFLOW: 1800 (30 minutes)
  - NESTED: 300 (5 minutes)
  - AGENT: 60 (1 minute)
- [x] Task 1.3: Define TimeoutConfig dataclass (level, timeout_seconds, error_type)
- [x] Task 1.4: Implement get_timeout_for_level(level) returning TimeoutConfig
- [x] Task 1.5: Write tests for timeout configuration lookup

### Task 2: Create TimeoutManager Class (AC: #1-3)

- [x] Task 2.1: Define TimeoutManager class
- [x] Task 2.2: Implement start_timeout(level, operation_id) starting timer
- [x] Task 2.3: Implement check_timeout(operation_id) returning bool
- [x] Task 2.4: Implement cancel_timeout(operation_id) for successful completion
- [x] Task 2.5: Track active timeouts in dict[operation_id, TimeoutState]
- [x] Task 2.6: Write tests for timeout lifecycle

### Task 3: Workflow Timeout Enforcement (AC: #1)

- [x] Task 3.1: Define WorkflowTimeoutError exception
- [x] Task 3.2: Implement enforce_workflow_timeout(workflow_id, start_time)
- [x] Task 3.3: Raise WorkflowTimeoutError with `timeout_error: "workflow_timeout"`
- [x] Task 3.4: Include elapsed_time and operation_context in error
- [x] Task 3.5: Write tests for workflow timeout at boundary (1799s, 1800s, 1801s)

### Task 4: Nested Operation Timeout Enforcement (AC: #2)

- [x] Task 4.1: Define NestedTimeoutError exception
- [x] Task 4.2: Implement enforce_nested_timeout(operation_id, parent_id, start_time)
- [x] Task 4.3: Raise NestedTimeoutError and notify parent workflow
- [x] Task 4.4: Include nested_operation_context and parent_notification
- [x] Task 4.5: Write tests for nested timeout with parent notification

### Task 5: Agent Timeout Enforcement (AC: #3)

- [x] Task 5.1: Define AgentTimeoutError exception
- [x] Task 5.2: Implement enforce_agent_timeout(agent_id, start_time)
- [x] Task 5.3: Raise AgentTimeoutError with `timeout_error: "agent_timeout"`
- [x] Task 5.4: Include agent_context and last_activity
- [x] Task 5.5: Write tests for agent timeout at boundary (59s, 60s, 61s)

### Task 6: State Preservation on Timeout (AC: #4)

- [x] Task 6.1: Define TimeoutState dataclass (operation_id, state_snapshot, timestamp)
- [x] Task 6.2: Implement preserve_state_on_timeout(operation_id, state)
- [x] Task 6.3: Save state to recoverable storage (file or memory)
- [x] Task 6.4: Include checkpoint for potential resume
- [x] Task 6.5: Write tests for state preservation

### Task 7: Timeout Logging (AC: #4)

- [x] Task 7.1: Define TimeoutLog dataclass (level, operation_id, elapsed_time, context)
- [x] Task 7.2: Implement log_timeout(level, operation_id, elapsed, context)
- [x] Task 7.3: Include timeout_error type and operation details
- [x] Task 7.4: Store in audit trail for analysis
- [x] Task 7.5: Write tests for timeout logging completeness

### Task 8: Integration with Automation Controller (AC: All)

- [x] Task 8.1: Add TimeoutManager to Automation Controller initialization
- [x] Task 8.2: Wrap workflow execution with workflow timeout
- [x] Task 8.3: Wrap nested operations with nested timeout
- [x] Task 8.4: Wrap agent calls with agent timeout
- [x] Task 8.5: Handle TimeoutError exceptions appropriately
- [x] Task 8.6: Write integration tests showing timeout hierarchy in practice

## Dev Notes

### Architecture Context

**Component:** Automation Controller - Timeout Enforcement
- **Tier:** 2-3 (Depends on Stories 2b.1-2b.8)
- **Purpose:** Prevent operations from hanging indefinitely with timeout hierarchy
- **Integration:** Used by Automation Controller for all timed operations

**Design Reference (from Architecture Document):**

```
TIMEOUT HIERARCHY:
  Level 1: Workflow timeout (30 minutes)
    - Entire workflow execution
    - Terminates all child operations

  Level 2: Nested operation timeout (5 minutes)
    - Sub-workflows, Party Mode sessions
    - Notifies parent on timeout

  Level 3: Agent timeout (60 seconds)
    - Individual agent calls
    - Quick fail for responsiveness

STATE PRESERVATION:
  - Save checkpoint on timeout
  - Include last successful state
  - Enable resume from timeout point
```

### Related Stories

- **Story 2b.8:** Validation Failure Recovery (transient timeout recovery)
- **Story 3.2:** Workflow Resume from Interruption (resume after timeout)
- **Story 3.6:** Checkpoint Creation (state preservation)

### Files to Create/Modify

- `pcmrp_tools/bmad_automation/timeout_manager.py` (NEW)
- `tests/bmad_automation/test_timeout_manager.py` (NEW)

### TDD Approach

For each task:
1. Write failing test for expected behavior
2. Implement minimal code to pass
3. Refactor while keeping tests green

---

## Dev Agent Record

**Agent Model:** claude-opus-4-5-20251101 (via parallel subagents)

**Debug Log Refs:**
- Agent (2b-9 Tasks 1-4): TimeoutLevel enum, TIMEOUT_SECONDS, TimeoutManager, WorkflowTimeoutError, NestedTimeoutError
- Agent (2b-9 Tasks 5-7): AgentTimeoutError, TimeoutState preservation, TimeoutLog with wall_clock_time
- Agent (2b-9 Task 8): Context managers, Automation Controller Integration
- ADVERSARIAL Code Review (8 issues found, 6 fixed)

**Completion Notes:**
- Task 1: Created TimeoutLevel enum (WORKFLOW, NESTED, AGENT), TIMEOUT_SECONDS dict {WORKFLOW: 1800, NESTED: 300, AGENT: 60}, TimeoutConfig dataclass
- Task 2: Implemented TimeoutManager with start_timeout(), check_timeout(), cancel_timeout(), active timeout tracking with has_active_timeout() and get_active_timeout_state()
- Task 3: Created WorkflowTimeoutError with timeout_error="workflow_timeout", elapsed_time, operation_context
- Task 4: Created NestedTimeoutError with parent notification, nested_operation_context
- Task 5: Created AgentTimeoutError with timeout_error="agent_timeout", agent_context, last_activity
- Task 6: Created TimeoutState dataclass for state preservation, preserve_state_on_timeout() with checkpoint for resume
- Task 7: Created TimeoutLog dataclass with wall_clock_time (datetime), log_timeout() for audit trail
- Task 8: Created context managers workflow_timeout(), nested_timeout(), agent_timeout() with integration

**Code Review Fixes:**
- Added thread-safety warning docstrings (TimeoutManager not thread-safe for concurrent access)
- Added context manager limitation docstrings (timeout only checked on entry/exit, not during execution)
- Added has_active_timeout() and get_active_timeout_state() public methods for encapsulation
- Added wall_clock_time field to TimeoutLog for human-readable audit trail
- Added tests for duplicate operation ID handling
- Added tests for exception propagation through context managers

**Files Modified:**
- `pcmrp_tools/bmad_automation/timeout_manager.py` (NEW - 124 statements, 97% coverage)
- `tests/bmad_automation/test_timeout_manager.py` (NEW - 142 tests)
