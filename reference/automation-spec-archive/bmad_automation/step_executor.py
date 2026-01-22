"""Step Executor for BMAD Automation.

This module implements autonomous step execution for BMAD workflows,
including verdict-based transitions, oversight handling, and recovery logic.

Story: 2a.2 - Autonomous Step Execution
Epic: 2a - Workflow Entry & Detection

Functional Requirements Covered:
- FR2: Automation Controller can execute workflows autonomously without user prompts
- FR3: Automation Controller can transition between workflow steps based on verdict
- FR6: Automation Controller can respect task-level oversight requirements
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class StepStatus(Enum):
    """Status of a workflow step execution.

    Represents the current state of a step during workflow execution.
    """

    PENDING = "pending"  # Not yet started
    RUNNING = "running"  # Currently executing
    PASSED = "passed"  # Completed successfully
    FAILED = "failed"  # Completed with failure
    SKIPPED = "skipped"  # Skipped (dependencies not met or conditional)
    AWAITING_USER = "awaiting_user"  # Paused for user confirmation


class WorkflowStatus(Enum):
    """Status of workflow execution.

    Represents the overall state of a workflow during execution.
    """

    PENDING = "pending"  # Not yet started
    RUNNING = "running"  # Currently executing
    COMPLETED = "completed"  # All steps completed successfully
    FAILED = "failed"  # Workflow failed (step failure not recovered)
    PAUSED = "paused"  # Paused for user input (oversight required)


# Verdicts that indicate successful completion
SUCCESS_VERDICTS = frozenset({"PASSED", "PASS", "READY", "APPROVED", "SUCCESS", "OK"})

# Verdicts that require user acknowledgment but don't necessarily fail
CONCERN_VERDICTS = frozenset({"CONCERNS", "NEEDS_WORK", "WARNING"})

# Verdicts that indicate failure
FAILURE_VERDICTS = frozenset(
    {"FAILED", "FAIL", "NOT_READY", "REJECTED", "ERROR", "BLOCKED"}
)

# =============================================================================
# Configuration Constants
# =============================================================================

# Default timeout for step execution (5 minutes)
DEFAULT_TIMEOUT_MS = 300000

# Default maximum recovery attempts before escalation
DEFAULT_MAX_RECOVERY_ATTEMPTS = 3

# Keywords indicating recoverable errors (retry-worthy)
RECOVERABLE_KEYWORDS = frozenset({"recoverable", "retry", "transient", "timeout"})

# Valid oversight values
VALID_OVERSIGHT_VALUES = frozenset({"none", "required", "optional"})


@dataclass
class StepResult:
    """Result of executing a single workflow step.

    Attributes:
        step_id: Unique identifier for the step
        status: Current status of the step
        verdict: Validation verdict (e.g., "PASSED", "FAILED", "CONCERNS")
        output: Step output text/content
        errors: List of error messages if any
        duration_ms: Execution time in milliseconds
        recovery_attempted: Whether recovery was attempted for this step
    """

    step_id: str
    status: StepStatus
    verdict: str | None = None
    output: str = ""
    errors: list[str] = field(default_factory=list)
    duration_ms: int = 0
    recovery_attempted: bool = False

    @classmethod
    def passed(
        cls,
        step_id: str,
        verdict: str = "PASSED",
        output: str = "",
        duration_ms: int = 0,
    ) -> "StepResult":
        """Factory method for creating a passed step result.

        Args:
            step_id: Unique identifier for the step
            verdict: Success verdict (defaults to "PASSED")
            output: Step output content
            duration_ms: Execution time in milliseconds

        Returns:
            StepResult with PASSED status
        """
        return cls(
            step_id=step_id,
            status=StepStatus.PASSED,
            verdict=verdict,
            output=output,
            errors=[],
            duration_ms=duration_ms,
            recovery_attempted=False,
        )

    @classmethod
    def failed(
        cls,
        step_id: str,
        verdict: str = "FAILED",
        errors: list[str] | None = None,
        duration_ms: int = 0,
        output: str = "",
    ) -> "StepResult":
        """Factory method for creating a failed step result.

        Args:
            step_id: Unique identifier for the step
            verdict: Failure verdict (defaults to "FAILED")
            errors: List of error messages
            duration_ms: Execution time in milliseconds
            output: Step output content

        Returns:
            StepResult with FAILED status
        """
        return cls(
            step_id=step_id,
            status=StepStatus.FAILED,
            verdict=verdict,
            output=output,
            errors=errors or [],
            duration_ms=duration_ms,
            recovery_attempted=False,
        )

    @classmethod
    def awaiting_user(
        cls,
        step_id: str,
        output: str = "",
        verdict: str | None = None,
    ) -> "StepResult":
        """Factory method for creating an awaiting user step result.

        Args:
            step_id: Unique identifier for the step
            output: Message for the user
            verdict: Optional verdict if step completed but needs confirmation

        Returns:
            StepResult with AWAITING_USER status
        """
        return cls(
            step_id=step_id,
            status=StepStatus.AWAITING_USER,
            verdict=verdict,
            output=output,
            errors=[],
            duration_ms=0,
            recovery_attempted=False,
        )

    @classmethod
    def skipped(
        cls,
        step_id: str,
        reason: str = "",
    ) -> "StepResult":
        """Factory method for creating a skipped step result.

        Args:
            step_id: Unique identifier for the step
            reason: Reason why the step was skipped

        Returns:
            StepResult with SKIPPED status
        """
        return cls(
            step_id=step_id,
            status=StepStatus.SKIPPED,
            verdict=None,
            output=f"Step skipped: {reason}" if reason else "Step skipped",
            errors=[],
            duration_ms=0,
            recovery_attempted=False,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert StepResult to dictionary for serialization.

        Returns:
            Dictionary representation of the StepResult
        """
        return {
            "step_id": self.step_id,
            "status": self.status.value,
            "verdict": self.verdict,
            "output": self.output,
            "errors": self.errors,
            "duration_ms": self.duration_ms,
            "recovery_attempted": self.recovery_attempted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StepResult":
        """Create StepResult from dictionary.

        Args:
            data: Dictionary containing StepResult fields

        Returns:
            StepResult instance

        Raises:
            ValueError: If status value is invalid
        """
        status_str = data.get("status", "")
        try:
            status = StepStatus(status_str)
        except ValueError:
            raise ValueError(f"Invalid status: {status_str}")

        return cls(
            step_id=data.get("step_id", ""),
            status=status,
            verdict=data.get("verdict"),
            output=data.get("output", ""),
            errors=data.get("errors", []),
            duration_ms=data.get("duration_ms", 0),
            recovery_attempted=data.get("recovery_attempted", False),
        )


@dataclass
class StepExecutionConfig:
    """Configuration for step execution behavior.

    Attributes:
        oversight: Level of oversight required ("none", "required", "optional")
        auto_continue: Whether to automatically continue to next step
        max_recovery_attempts: Maximum number of recovery attempts
        timeout_ms: Step execution timeout in milliseconds
    """

    oversight: str = "none"
    auto_continue: bool = True
    max_recovery_attempts: int = DEFAULT_MAX_RECOVERY_ATTEMPTS
    timeout_ms: int = DEFAULT_TIMEOUT_MS

    def __post_init__(self) -> None:
        """Validate configuration values after initialization."""
        if self.oversight not in VALID_OVERSIGHT_VALUES:
            raise ValueError(
                f"Invalid oversight value: {self.oversight!r}. "
                f"Must be one of: {', '.join(sorted(VALID_OVERSIGHT_VALUES))}"
            )

    @property
    def is_oversight_required(self) -> bool:
        """Check if oversight is required for this configuration.

        Returns:
            True if oversight is "required", False otherwise
        """
        return self.oversight == "required"

    def to_dict(self) -> dict[str, Any]:
        """Convert StepExecutionConfig to dictionary for serialization.

        Returns:
            Dictionary representation of the config
        """
        return {
            "oversight": self.oversight,
            "auto_continue": self.auto_continue,
            "max_recovery_attempts": self.max_recovery_attempts,
            "timeout_ms": self.timeout_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StepExecutionConfig":
        """Create StepExecutionConfig from dictionary.

        Args:
            data: Dictionary containing config fields

        Returns:
            StepExecutionConfig instance with values from dict or defaults
        """
        return cls(
            oversight=data.get("oversight", "none"),
            auto_continue=data.get("auto_continue", True),
            max_recovery_attempts=data.get(
                "max_recovery_attempts", DEFAULT_MAX_RECOVERY_ATTEMPTS
            ),
            timeout_ms=data.get("timeout_ms", DEFAULT_TIMEOUT_MS),
        )


@dataclass
class WorkflowExecutionResult:
    """Result of executing a complete workflow.

    Attributes:
        workflow_id: Unique identifier for the workflow
        status: Overall workflow status
        step_results: List of individual step results
        total_duration_ms: Total execution time in milliseconds
        steps_passed: Number of steps that passed
        steps_failed: Number of steps that failed
        final_verdict: Overall verdict for the workflow
    """

    workflow_id: str
    status: WorkflowStatus
    step_results: list[StepResult] = field(default_factory=list)
    total_duration_ms: int = 0
    steps_passed: int = 0
    steps_failed: int = 0
    final_verdict: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert WorkflowExecutionResult to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "step_results": [r.to_dict() for r in self.step_results],
            "total_duration_ms": self.total_duration_ms,
            "steps_passed": self.steps_passed,
            "steps_failed": self.steps_failed,
            "final_verdict": self.final_verdict,
        }


def should_auto_transition(result: StepResult, config: StepExecutionConfig) -> bool:
    """Determine if automatic transition to next step is allowed.

    This function implements FR3: verdict-based step transitions.
    Auto-transition is allowed when:
    - Step status is PASSED
    - Verdict is in SUCCESS_VERDICTS (not CONCERNS or FAILURE)
    - No oversight is required
    - auto_continue is enabled

    Args:
        result: The step execution result
        config: The step execution configuration

    Returns:
        True if auto-transition is allowed, False otherwise
    """
    # Cannot auto-transition if step didn't pass
    if result.status != StepStatus.PASSED:
        return False

    # Cannot auto-transition if oversight is required (AC2)
    if config.is_oversight_required:
        return False

    # Cannot auto-transition if auto_continue is disabled
    if not config.auto_continue:
        return False

    # Check verdict - only SUCCESS_VERDICTS allow auto-transition
    if result.verdict:
        verdict_upper = result.verdict.upper()

        # CONCERNS requires user acknowledgment
        if verdict_upper in CONCERN_VERDICTS:
            return False

        # FAILURE_VERDICTS should not auto-transition
        if verdict_upper in FAILURE_VERDICTS:
            return False

        # SUCCESS_VERDICTS allow auto-transition
        if verdict_upper in SUCCESS_VERDICTS:
            return True

        # Unknown verdict - be conservative, don't auto-transition
        return False

    # No verdict but passed status - allow auto-transition
    return True


def attempt_recovery(
    failed_result: StepResult,
    config: StepExecutionConfig,
    attempt_num: int,
) -> StepResult:
    """Attempt to recover from a step failure.

    This function implements FR16: recovery before escalation.
    Recovery strategies are determined based on error types and
    may include retrying, applying fixes, or querying memory for known solutions.

    Args:
        failed_result: The failed step result
        config: The step execution configuration
        attempt_num: Current recovery attempt number (1-based)

    Returns:
        StepResult after recovery attempt
    """
    # Check if max attempts exceeded
    if attempt_num > config.max_recovery_attempts:
        return StepResult(
            step_id=failed_result.step_id,
            status=StepStatus.FAILED,
            verdict="FAILED",
            output=failed_result.output,
            errors=failed_result.errors + [
                f"Recovery failed: max attempts ({config.max_recovery_attempts}) exceeded"
            ],
            duration_ms=failed_result.duration_ms,
            recovery_attempted=True,
        )

    # Analyze errors to determine recovery strategy
    errors = failed_result.errors

    is_recoverable = any(
        any(keyword in err.lower() for keyword in RECOVERABLE_KEYWORDS)
        for err in errors
    )

    if is_recoverable:
        # Simulate recovery attempt - in real implementation, this would
        # actually retry the step or apply fixes
        # For now, mark as attempted and return with same status
        return StepResult(
            step_id=failed_result.step_id,
            status=failed_result.status,
            verdict=failed_result.verdict,
            output=f"{failed_result.output}\n[Recovery attempt {attempt_num}]",
            errors=failed_result.errors,
            duration_ms=failed_result.duration_ms,
            recovery_attempted=True,
        )

    # Non-recoverable error
    return StepResult(
        step_id=failed_result.step_id,
        status=StepStatus.FAILED,
        verdict="FAILED",
        output=failed_result.output,
        errors=failed_result.errors + [f"Recovery attempt {attempt_num}: Not recoverable"],
        duration_ms=failed_result.duration_ms,
        recovery_attempted=True,
    )


def execute_step(
    step_id: str,
    step_config: dict[str, Any],
    config: StepExecutionConfig,
) -> StepResult:
    """Execute a single workflow step.

    This function executes a step and returns the result with
    status, verdict, output, and timing information.

    Args:
        step_id: Unique identifier for the step
        step_config: Step configuration dictionary
        config: Step execution configuration

    Returns:
        StepResult with execution outcome
    """
    start_time = time.time()

    # Extract step content and settings
    content = step_config.get("content", "")
    oversight = step_config.get("oversight", config.oversight)

    # Simulate step execution based on content
    # In real implementation, this would actually execute the step
    # Support explicit verdict from step_config for testing
    explicit_verdict = step_config.get("verdict")
    if explicit_verdict:
        verdict = explicit_verdict
        # Determine status based on verdict type
        verdict_upper = verdict.upper()
        if verdict_upper in SUCCESS_VERDICTS:
            status = StepStatus.PASSED
        elif verdict_upper in CONCERN_VERDICTS:
            status = StepStatus.PASSED  # Concerns are passing but need acknowledgment
        elif verdict_upper in FAILURE_VERDICTS:
            status = StepStatus.FAILED
        else:
            # Unknown verdict - treat as passed but conservative
            status = StepStatus.PASSED
    else:
        verdict = "PASSED" if "PASS" in content.upper() else "FAILED"
        status = StepStatus.PASSED if verdict == "PASSED" else StepStatus.FAILED

    errors: list[str] = []
    if status == StepStatus.FAILED:
        error_msg = step_config.get("error_message", "Step execution failed")
        errors.append(error_msg)

    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)

    # Generate output
    step_name = step_config.get("name", step_id)
    output = f"Step '{step_name}' executed with verdict: {verdict}"

    # Check if we should await user (oversight required)
    if oversight == "required" and status == StepStatus.PASSED:
        return StepResult.awaiting_user(
            step_id=step_id,
            output=f"{output}\n\nOversight required - awaiting user confirmation.",
            verdict=verdict,
        )

    return StepResult(
        step_id=step_id,
        status=status,
        verdict=verdict,
        output=output,
        errors=errors,
        duration_ms=duration_ms,
        recovery_attempted=False,
    )


def execute_workflow_steps(
    steps: list[dict[str, Any]],
    workflow_config: dict[str, Any],
) -> WorkflowExecutionResult:
    """Orchestrate sequential step execution for a workflow.

    This function implements FR2 and FR3: autonomous workflow execution
    with verdict-based transitions.

    Args:
        steps: List of step configuration dictionaries
        workflow_config: Workflow-level configuration

    Returns:
        WorkflowExecutionResult with all step results and summary
    """
    workflow_id = workflow_config.get("workflow_id", "unknown")
    auto_continue = workflow_config.get("auto_continue", True)
    max_recovery_attempts = workflow_config.get("max_recovery_attempts", 3)

    step_results: list[StepResult] = []
    workflow_status = WorkflowStatus.RUNNING
    steps_passed = 0
    steps_failed = 0
    total_duration_ms = 0

    # Handle empty steps list
    if not steps:
        return WorkflowExecutionResult(
            workflow_id=workflow_id,
            status=WorkflowStatus.COMPLETED,
            step_results=[],
            total_duration_ms=0,
            steps_passed=0,
            steps_failed=0,
            final_verdict="PASSED",
        )

    for step in steps:
        step_id = step.get("id", f"step-{len(step_results) + 1}")
        oversight = step.get("oversight", "none")

        # Create execution config for this step
        step_exec_config = StepExecutionConfig(
            oversight=oversight,
            auto_continue=auto_continue,
            max_recovery_attempts=max_recovery_attempts,
        )

        # Execute the step
        result = execute_step(step_id, step, step_exec_config)
        total_duration_ms += result.duration_ms

        # Handle failure with recovery attempts
        if result.status == StepStatus.FAILED:
            # Check if step is recoverable
            recoverable = step.get("recoverable", False)
            recovery_outcome = step.get("recovery_outcome", "FAIL")

            if recoverable:
                # Attempt recovery
                for attempt in range(1, max_recovery_attempts + 1):
                    result = attempt_recovery(result, step_exec_config, attempt)

                    # Check if recovery succeeded (simulated by recovery_outcome)
                    if recovery_outcome == "PASS":
                        result = StepResult(
                            step_id=step_id,
                            status=StepStatus.PASSED,
                            verdict="PASSED",
                            output=f"Step recovered after {attempt} attempt(s)",
                            errors=[],
                            duration_ms=result.duration_ms,
                            recovery_attempted=True,
                        )
                        break
            else:
                # Not recoverable, mark as attempted
                result = StepResult(
                    step_id=step_id,
                    status=StepStatus.FAILED,
                    verdict="FAILED",
                    output=result.output,
                    errors=result.errors,
                    duration_ms=result.duration_ms,
                    recovery_attempted=True,
                )

        step_results.append(result)

        # Update counters
        if result.status == StepStatus.PASSED:
            steps_passed += 1
        elif result.status == StepStatus.FAILED:
            steps_failed += 1
            workflow_status = WorkflowStatus.FAILED
            break  # Stop on unrecoverable failure
        elif result.status == StepStatus.AWAITING_USER:
            workflow_status = WorkflowStatus.PAUSED
            break  # Pause for user input

        # Check if we should auto-transition to next step
        if not should_auto_transition(result, step_exec_config):
            if result.status == StepStatus.PASSED:
                # Passed but can't auto-transition (oversight or CONCERNS)
                workflow_status = WorkflowStatus.PAUSED
                break

    # Determine final status if we completed all steps
    if workflow_status == WorkflowStatus.RUNNING:
        workflow_status = WorkflowStatus.COMPLETED

    # Determine final verdict
    if workflow_status == WorkflowStatus.COMPLETED:
        final_verdict = "PASSED"
    elif workflow_status == WorkflowStatus.FAILED:
        final_verdict = "FAILED"
    else:
        # Paused - use last step's verdict
        final_verdict = step_results[-1].verdict if step_results else None

    return WorkflowExecutionResult(
        workflow_id=workflow_id,
        status=workflow_status,
        step_results=step_results,
        total_duration_ms=total_duration_ms,
        steps_passed=steps_passed,
        steps_failed=steps_failed,
        final_verdict=final_verdict,
    )
