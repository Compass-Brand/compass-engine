# Story 2b.8: Validation Failure Recovery

Status: done

## Story

As a **workflow user**,
I want **the system to attempt automatic recovery from validation failures**,
So that **most issues resolve without interrupting my work**.

## Acceptance Criteria

1. **Given** a validation failure due to missing configuration
   **When** the Automation Controller detects the failure
   **Then** it attempts to locate or prompt for the missing config before user escalation

2. **Given** a validation failure due to transient error (network, timeout)
   **When** the Automation Controller detects the failure
   **Then** it retries up to 3 times with exponential backoff before escalation

3. **Given** a validation failure with known fix pattern in memory
   **When** the Automation Controller queries existing fix patterns via Context Pre-Loader (from Epic 2a)
   **Then** it applies the remembered fix pattern automatically

4. **Given** recovery attempts succeed
   **When** workflow resumes
   **Then** the recovery is logged with `recovery_method` and `attempts_count`

5. **Given** recovery attempts fail after all strategies exhausted
   **When** escalation to user occurs
   **Then** it includes attempted strategies and specific failure reasons

## Tasks / Subtasks

### Task 1: Define Failure Types and Recovery Strategies (AC: #1, #2, #3)

- [x] Task 1.1: Define FailureType enum (MISSING_CONFIG, TRANSIENT_ERROR, KNOWN_PATTERN, UNKNOWN)
- [x] Task 1.2: Define RecoveryStrategy enum (LOCATE_CONFIG, RETRY_BACKOFF, APPLY_PATTERN, ESCALATE)
- [x] Task 1.3: Define FAILURE_TO_STRATEGY mapping dict
- [x] Task 1.4: Implement classify_failure(error) returning FailureType
- [x] Task 1.5: Write tests for failure classification

### Task 2: Missing Configuration Recovery (AC: #1)

- [x] Task 2.1: Define MissingConfigRecovery class
- [x] Task 2.2: Implement detect_missing_config(error) returning config_key
- [x] Task 2.3: Implement locate_config(config_key) searching common locations
- [x] Task 2.4: Implement prompt_for_config(config_key) generating user prompt
- [x] Task 2.5: Return RecoveryResult with located config or prompt
- [x] Task 2.6: Write tests for config location scenarios

### Task 3: Transient Error Recovery with Exponential Backoff (AC: #2)

- [x] Task 3.1: Define TransientErrorRecovery class
- [x] Task 3.2: Define MAX_RETRY_ATTEMPTS = 3
- [x] Task 3.3: Define BACKOFF_BASE = 2 (seconds: 2, 4, 8)
- [x] Task 3.4: Implement is_transient_error(error) returning bool
- [x] Task 3.5: Implement retry_with_backoff(operation, max_attempts) with exponential delay
- [x] Task 3.6: Return RecoveryResult with success or exhausted_retries
- [x] Task 3.7: Write tests for retry behavior at each attempt

### Task 4: Memory-Based Fix Pattern Recovery (AC: #3)

- [x] Task 4.1: Define PatternRecovery class
- [x] Task 4.2: Implement query_fix_patterns(error) via Context Pre-Loader
- [x] Task 4.3: Implement apply_fix_pattern(pattern, context) executing known fix
- [x] Task 4.4: Track pattern application success/failure
- [x] Task 4.5: Update memory with new successful patterns
- [x] Task 4.6: Write tests for pattern query and application

### Task 5: Recovery Logging (AC: #4)

- [x] Task 5.1: Define RecoveryLog dataclass (recovery_method, attempts_count, timestamp)
- [x] Task 5.2: Implement log_recovery(method, attempts) recording successful recovery
- [x] Task 5.3: Include original error details and recovery details
- [x] Task 5.4: Store in recoverable format for analysis
- [x] Task 5.5: Write tests for recovery logging

### Task 6: Escalation with Context (AC: #5)

- [x] Task 6.1: Define EscalationReport dataclass (strategies_attempted, failure_reasons)
- [x] Task 6.2: Implement build_escalation_report(attempts) summarizing failures
- [x] Task 6.3: Include specific failure reason per strategy
- [x] Task 6.4: Format for user presentation (clear, actionable)
- [x] Task 6.5: Write tests for escalation report content

### Task 7: Recovery Orchestrator Integration (AC: All)

- [x] Task 7.1: Create ValidationRecoveryOrchestrator class
- [x] Task 7.2: Implement attempt_recovery(error) trying strategies in order
- [x] Task 7.3: Order: missing_config → transient_retry → pattern_match → escalate
- [x] Task 7.4: Integrate with Automation Controller error handling
- [x] Task 7.5: Write integration tests showing full recovery flow

## Dev Notes

### Architecture Context

**Component:** Automation Controller - Validation Failure Recovery
- **Tier:** 2-3 (Depends on Stories 2b.1-2b.7, Epic 2a Context Pre-Loader)
- **Purpose:** Automatically recover from validation failures before escalating to user
- **Integration:** Used by Automation Controller when validation errors occur

**Design Reference (from Architecture Document):**

```
RECOVERY STRATEGY ORDER:
  1. Missing Config → Locate or prompt
  2. Transient Error → Retry with exponential backoff (2s, 4s, 8s)
  3. Known Pattern → Query memory, apply fix
  4. Unknown → Escalate with full context

RECOVERY LOGGING:
  - recovery_method: which strategy succeeded
  - attempts_count: total attempts before success
  - original_error: what triggered recovery
  - recovery_details: specific fix applied
```

### Related Stories

- **Story 2a.5:** Context Pre-Loading from Memory (fix pattern queries)
- **Story 2b.7:** Human Checkpoint Presentation (escalation format)
- **Story 4.1:** Writing Workflow Decisions to Memory (pattern storage)

### Files to Create/Modify

- `pcmrp_tools/bmad_automation/validation_recovery.py` (NEW)
- `tests/bmad_automation/test_validation_recovery.py` (NEW)

### TDD Approach

For each task:
1. Write failing test for expected behavior
2. Implement minimal code to pass
3. Refactor while keeping tests green

---

## Dev Agent Record

**Agent Model:** claude-opus-4-5-20251101 (via parallel subagents)

**Debug Log Refs:**
- Agent (2b-8 Tasks 1-3): FailureType/RecoveryStrategy enums, MissingConfigRecovery, TransientErrorRecovery
- Agent (2b-8 Tasks 4-6): PatternRecovery, RecoveryLog, EscalationReport
- Agent (2b-8 Task 7): ValidationRecoveryOrchestrator, Automation Controller Integration
- ADVERSARIAL Code Review (10 issues found, 5 Critical/High/Medium fixed)

**Completion Notes:**
- Task 1: Created FailureType enum, RecoveryStrategy enum, FAILURE_TO_STRATEGY mapping, classify_failure() with error type detection
- Task 2: Implemented MissingConfigRecovery with detect_missing_config(), locate_config() searching common locations, prompt_for_config() for user prompts
- Task 3: Created TransientErrorRecovery with MAX_RETRY_ATTEMPTS=3, BACKOFF_BASE=2, is_transient_error(), retry_with_backoff() with exponential delays (2s, 4s, 8s)
- Task 4: Implemented PatternRecovery with query_fix_patterns() via Context Pre-Loader, apply_fix_pattern(), success/failure tracking, memory updates
- Task 5: Created RecoveryLog dataclass with datetime timestamp (not Any), log_recovery() with original error and recovery details
- Task 6: Created EscalationReport dataclass, build_escalation_report() with per-strategy failure reasons, user-friendly formatting
- Task 7: Created ValidationRecoveryOrchestrator with attempt_recovery() following strategy order: missing_config → transient_retry → pattern_match → escalate

**Code Review Fixes:**
- **CRITICAL:** Refactored attempt_recovery() to follow documented strategy order (was incorrect)
- Changed RecoveryLog.timestamp type from Any to datetime for type safety
- Moved datetime import to module level (was inside function)
- Added test for non-transient error retry behavior (should not retry)
- Fixed strategy order: missing_config → transient_retry → pattern_match → escalate

**Files Modified:**
- `pcmrp_tools/bmad_automation/validation_recovery.py` (NEW - 264 statements, 96% coverage)
- `tests/bmad_automation/test_validation_recovery.py` (NEW - 133 tests)
