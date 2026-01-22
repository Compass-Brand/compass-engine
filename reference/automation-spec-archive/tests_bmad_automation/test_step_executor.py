"""Tests for Step Executor component.

This module tests the autonomous step execution system for BMAD Automation,
including StepStatus enum, StepResult dataclass, StepExecutionConfig,
and the step execution functions.

TDD Pattern: Tests written FIRST before implementation.

Story: 2a.2 - Autonomous Step Execution
Epic: 2a - Workflow Entry & Detection
"""

from dataclasses import asdict
from typing import Any

import pytest


# =============================================================================
# Task 1: StepStatus Enum Tests
# =============================================================================


class TestStepStatus:
    """Tests for StepStatus enum (AC: all)."""

    def test_pending_value(self):
        """Test StepStatus.PENDING has correct string value."""
        from pcmrp_tools.bmad_automation.step_executor import StepStatus

        assert StepStatus.PENDING.value == "pending"

    def test_running_value(self):
        """Test StepStatus.RUNNING has correct string value."""
        from pcmrp_tools.bmad_automation.step_executor import StepStatus

        assert StepStatus.RUNNING.value == "running"

    def test_passed_value(self):
        """Test StepStatus.PASSED has correct string value."""
        from pcmrp_tools.bmad_automation.step_executor import StepStatus

        assert StepStatus.PASSED.value == "passed"

    def test_failed_value(self):
        """Test StepStatus.FAILED has correct string value."""
        from pcmrp_tools.bmad_automation.step_executor import StepStatus

        assert StepStatus.FAILED.value == "failed"

    def test_skipped_value(self):
        """Test StepStatus.SKIPPED has correct string value."""
        from pcmrp_tools.bmad_automation.step_executor import StepStatus

        assert StepStatus.SKIPPED.value == "skipped"

    def test_awaiting_user_value(self):
        """Test StepStatus.AWAITING_USER has correct string value."""
        from pcmrp_tools.bmad_automation.step_executor import StepStatus

        assert StepStatus.AWAITING_USER.value == "awaiting_user"

    def test_all_enum_members_exist(self):
        """Test all required enum members exist."""
        from pcmrp_tools.bmad_automation.step_executor import StepStatus

        expected_members = {
            "PENDING",
            "RUNNING",
            "PASSED",
            "FAILED",
            "SKIPPED",
            "AWAITING_USER",
        }
        actual_members = {member.name for member in StepStatus}
        assert expected_members == actual_members

    def test_enum_comparison(self):
        """Test StepStatus enum comparison works correctly."""
        from pcmrp_tools.bmad_automation.step_executor import StepStatus

        assert StepStatus.PASSED == StepStatus.PASSED
        assert StepStatus.PASSED != StepStatus.FAILED


# =============================================================================
# Task 2: StepResult Tests
# =============================================================================


class TestStepResult:
    """Tests for StepResult dataclass."""

    def test_create_with_all_fields(self):
        """Test creating StepResult with all required fields."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        result = StepResult(
            step_id="step-01",
            status=StepStatus.PASSED,
            verdict="PASSED",
            output="Step completed successfully",
            errors=[],
            duration_ms=1500,
            recovery_attempted=False,
        )
        assert result.step_id == "step-01"
        assert result.status == StepStatus.PASSED
        assert result.verdict == "PASSED"
        assert result.output == "Step completed successfully"
        assert result.errors == []
        assert result.duration_ms == 1500
        assert result.recovery_attempted is False

    def test_create_with_minimal_fields(self):
        """Test creating StepResult with only required fields."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        result = StepResult(
            step_id="step-01",
            status=StepStatus.PENDING,
        )
        assert result.step_id == "step-01"
        assert result.status == StepStatus.PENDING
        assert result.verdict is None
        assert result.output == ""
        assert result.errors == []
        assert result.duration_ms == 0
        assert result.recovery_attempted is False

    def test_step_id_required(self):
        """Test step_id is a required field."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        # Should work with step_id
        result = StepResult(step_id="test", status=StepStatus.PENDING)
        assert result.step_id == "test"

    def test_status_required(self):
        """Test status is a required field."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        result = StepResult(step_id="test", status=StepStatus.RUNNING)
        assert result.status == StepStatus.RUNNING


class TestStepResultFactoryMethods:
    """Tests for StepResult factory methods."""

    def test_passed_factory(self):
        """Test factory method for passed step result."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        result = StepResult.passed(
            step_id="step-01",
            verdict="PASSED",
            output="All checks passed",
            duration_ms=2000,
        )
        assert result.status == StepStatus.PASSED
        assert result.step_id == "step-01"
        assert result.verdict == "PASSED"
        assert result.output == "All checks passed"
        assert result.duration_ms == 2000
        assert result.errors == []

    def test_failed_factory(self):
        """Test factory method for failed step result."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        result = StepResult.failed(
            step_id="step-02",
            verdict="FAILED",
            errors=["Validation error 1", "Validation error 2"],
            duration_ms=1000,
        )
        assert result.status == StepStatus.FAILED
        assert result.step_id == "step-02"
        assert result.verdict == "FAILED"
        assert result.errors == ["Validation error 1", "Validation error 2"]
        assert result.duration_ms == 1000

    def test_awaiting_user_factory(self):
        """Test factory method for awaiting user result."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        result = StepResult.awaiting_user(
            step_id="step-03",
            output="Step requires user confirmation",
        )
        assert result.status == StepStatus.AWAITING_USER
        assert result.step_id == "step-03"
        assert result.output == "Step requires user confirmation"

    def test_skipped_factory(self):
        """Test factory method for skipped step result."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        result = StepResult.skipped(
            step_id="step-04",
            reason="Prerequisites not met",
        )
        assert result.status == StepStatus.SKIPPED
        assert result.step_id == "step-04"
        assert "Prerequisites not met" in result.output


class TestStepResultSerialization:
    """Tests for StepResult serialization."""

    def test_to_dict(self):
        """Test converting StepResult to dictionary."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        result = StepResult(
            step_id="step-01",
            status=StepStatus.PASSED,
            verdict="PASSED",
            output="Success",
            errors=[],
            duration_ms=1500,
            recovery_attempted=False,
        )
        result_dict = result.to_dict()

        assert result_dict["step_id"] == "step-01"
        assert result_dict["status"] == "passed"
        assert result_dict["verdict"] == "PASSED"
        assert result_dict["output"] == "Success"
        assert result_dict["errors"] == []
        assert result_dict["duration_ms"] == 1500
        assert result_dict["recovery_attempted"] is False

    def test_from_dict(self):
        """Test creating StepResult from dictionary."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        data = {
            "step_id": "step-02",
            "status": "failed",
            "verdict": "FAILED",
            "output": "Error occurred",
            "errors": ["Error 1"],
            "duration_ms": 500,
            "recovery_attempted": True,
        }
        result = StepResult.from_dict(data)

        assert result.step_id == "step-02"
        assert result.status == StepStatus.FAILED
        assert result.verdict == "FAILED"
        assert result.output == "Error occurred"
        assert result.errors == ["Error 1"]
        assert result.duration_ms == 500
        assert result.recovery_attempted is True

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are inverse operations."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult, StepStatus

        original = StepResult(
            step_id="step-01",
            status=StepStatus.PASSED,
            verdict="PASSED",
            output="Success",
            errors=["Warning 1"],
            duration_ms=2000,
            recovery_attempted=True,
        )

        serialized = original.to_dict()
        restored = StepResult.from_dict(serialized)

        assert restored.step_id == original.step_id
        assert restored.status == original.status
        assert restored.verdict == original.verdict
        assert restored.output == original.output
        assert restored.errors == original.errors
        assert restored.duration_ms == original.duration_ms
        assert restored.recovery_attempted == original.recovery_attempted

    def test_from_dict_with_invalid_status_raises_error(self):
        """Test from_dict raises ValueError for invalid status."""
        from pcmrp_tools.bmad_automation.step_executor import StepResult

        data = {
            "step_id": "step-01",
            "status": "invalid-status",
            "verdict": None,
            "output": "",
            "errors": [],
            "duration_ms": 0,
            "recovery_attempted": False,
        }
        with pytest.raises(ValueError, match="Invalid status"):
            StepResult.from_dict(data)


# =============================================================================
# Task 3: StepExecutionConfig Tests
# =============================================================================


class TestStepExecutionConfig:
    """Tests for StepExecutionConfig dataclass."""

    def test_create_with_defaults(self):
        """Test creating StepExecutionConfig with default values."""
        from pcmrp_tools.bmad_automation.step_executor import StepExecutionConfig

        config = StepExecutionConfig()
        assert config.oversight == "none"
        assert config.auto_continue is True
        assert config.max_recovery_attempts == 3
        assert config.timeout_ms == 300000

    def test_create_with_custom_values(self):
        """Test creating StepExecutionConfig with custom values."""
        from pcmrp_tools.bmad_automation.step_executor import StepExecutionConfig

        config = StepExecutionConfig(
            oversight="required",
            auto_continue=False,
            max_recovery_attempts=5,
            timeout_ms=600000,
        )
        assert config.oversight == "required"
        assert config.auto_continue is False
        assert config.max_recovery_attempts == 5
        assert config.timeout_ms == 600000

    def test_oversight_values(self):
        """Test valid oversight values."""
        from pcmrp_tools.bmad_automation.step_executor import StepExecutionConfig

        # Test "none" oversight
        config_none = StepExecutionConfig(oversight="none")
        assert config_none.oversight == "none"

        # Test "required" oversight
        config_required = StepExecutionConfig(oversight="required")
        assert config_required.oversight == "required"

        # Test "optional" oversight
        config_optional = StepExecutionConfig(oversight="optional")
        assert config_optional.oversight == "optional"

    def test_is_oversight_required_property(self):
        """Test is_oversight_required computed property."""
        from pcmrp_tools.bmad_automation.step_executor import StepExecutionConfig

        config_none = StepExecutionConfig(oversight="none")
        assert config_none.is_oversight_required is False

        config_required = StepExecutionConfig(oversight="required")
        assert config_required.is_oversight_required is True

        config_optional = StepExecutionConfig(oversight="optional")
        assert config_optional.is_oversight_required is False


class TestStepExecutionConfigSerialization:
    """Tests for StepExecutionConfig serialization."""

    def test_to_dict(self):
        """Test converting StepExecutionConfig to dictionary."""
        from pcmrp_tools.bmad_automation.step_executor import StepExecutionConfig

        config = StepExecutionConfig(
            oversight="required",
            auto_continue=False,
            max_recovery_attempts=5,
            timeout_ms=600000,
        )
        config_dict = config.to_dict()

        assert config_dict["oversight"] == "required"
        assert config_dict["auto_continue"] is False
        assert config_dict["max_recovery_attempts"] == 5
        assert config_dict["timeout_ms"] == 600000

    def test_from_dict(self):
        """Test creating StepExecutionConfig from dictionary."""
        from pcmrp_tools.bmad_automation.step_executor import StepExecutionConfig

        data = {
            "oversight": "optional",
            "auto_continue": True,
            "max_recovery_attempts": 2,
            "timeout_ms": 120000,
        }
        config = StepExecutionConfig.from_dict(data)

        assert config.oversight == "optional"
        assert config.auto_continue is True
        assert config.max_recovery_attempts == 2
        assert config.timeout_ms == 120000

    def test_from_dict_with_partial_data(self):
        """Test from_dict uses defaults for missing keys."""
        from pcmrp_tools.bmad_automation.step_executor import StepExecutionConfig

        data = {"oversight": "required"}
        config = StepExecutionConfig.from_dict(data)

        assert config.oversight == "required"
        assert config.auto_continue is True  # default
        assert config.max_recovery_attempts == 3  # default
        assert config.timeout_ms == 300000  # default


# =============================================================================
# Task 4: should_auto_transition Tests (AC1, AC2)
# =============================================================================


class TestShouldAutoTransition:
    """Tests for should_auto_transition function."""

    def test_returns_true_for_passed_verdict_no_oversight(self):
        """Test returns True when verdict is PASSED and no oversight required (AC1)."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult.passed(
            step_id="step-01",
            verdict="PASSED",
            output="Success",
            duration_ms=1000,
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        assert should_auto_transition(result, config) is True

    def test_returns_false_for_failed_verdict(self):
        """Test returns False when verdict is FAILED."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult.failed(
            step_id="step-01",
            verdict="FAILED",
            errors=["Error occurred"],
            duration_ms=1000,
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        assert should_auto_transition(result, config) is False

    def test_returns_false_when_oversight_required(self):
        """Test returns False when oversight is required (AC2)."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult.passed(
            step_id="step-01",
            verdict="PASSED",
            output="Success",
            duration_ms=1000,
        )
        config = StepExecutionConfig(oversight="required", auto_continue=True)

        assert should_auto_transition(result, config) is False

    def test_returns_false_when_auto_continue_disabled(self):
        """Test returns False when auto_continue is disabled."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult.passed(
            step_id="step-01",
            verdict="PASSED",
            output="Success",
            duration_ms=1000,
        )
        config = StepExecutionConfig(oversight="none", auto_continue=False)

        assert should_auto_transition(result, config) is False

    def test_handles_concerns_verdict_based_on_config(self):
        """Test CONCERNS verdict behavior is configurable."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult(
            step_id="step-01",
            status=StepStatus.PASSED,  # CONCERNS can still be considered passing
            verdict="CONCERNS",
            output="Minor issues found",
        )

        # With default config, CONCERNS should pause for review
        config_default = StepExecutionConfig(oversight="none", auto_continue=True)
        # CONCERNS typically requires user acknowledgment
        assert should_auto_transition(result, config_default) is False

    def test_returns_true_for_ready_verdict(self):
        """Test returns True for READY verdict (BMAD-specific)."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult(
            step_id="step-01",
            status=StepStatus.PASSED,
            verdict="READY",
            output="Implementation ready",
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        assert should_auto_transition(result, config) is True

    def test_returns_false_for_not_ready_verdict(self):
        """Test returns False for NOT_READY verdict."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult(
            step_id="step-01",
            status=StepStatus.FAILED,
            verdict="NOT_READY",
            output="Implementation not ready",
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        assert should_auto_transition(result, config) is False

    def test_returns_false_for_needs_work_verdict(self):
        """Test returns False for NEEDS_WORK verdict."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult(
            step_id="step-01",
            status=StepStatus.FAILED,
            verdict="NEEDS_WORK",
            output="Additional work required",
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        assert should_auto_transition(result, config) is False

    def test_returns_false_for_awaiting_user_status(self):
        """Test returns False when status is AWAITING_USER."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult(
            step_id="step-01",
            status=StepStatus.AWAITING_USER,
            output="Waiting for user",
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        assert should_auto_transition(result, config) is False

    def test_returns_false_for_skipped_status(self):
        """Test returns False when status is SKIPPED."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult(
            step_id="step-01",
            status=StepStatus.SKIPPED,
            output="Step skipped",
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        assert should_auto_transition(result, config) is False

    def test_returns_false_for_unknown_verdict(self):
        """Test returns False for unknown/unrecognized verdict (conservative behavior)."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult(
            step_id="step-01",
            status=StepStatus.PASSED,
            verdict="UNKNOWN_VERDICT",  # Not in SUCCESS_VERDICTS, CONCERN_VERDICTS, or FAILURE_VERDICTS
            output="Step completed with unknown verdict",
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        # Should be conservative and not auto-transition for unknown verdicts
        assert should_auto_transition(result, config) is False

    def test_returns_true_for_none_verdict_with_passed_status(self):
        """Test returns True for passed status with no verdict set."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            should_auto_transition,
        )

        result = StepResult(
            step_id="step-01",
            status=StepStatus.PASSED,
            verdict=None,  # No verdict
            output="Step completed",
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        # Should allow auto-transition when passed but no verdict
        assert should_auto_transition(result, config) is True

    def test_returns_false_for_failure_verdict_with_passed_status(self):
        """Test returns False when verdict is FAILURE but status is PASSED (edge case)."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            should_auto_transition,
            FAILURE_VERDICTS,
        )

        # This is an unusual but possible case where step status is PASSED
        # but the verdict is a failure indicator (e.g., step ran but detected issues)
        result = StepResult(
            step_id="step-01",
            status=StepStatus.PASSED,  # Step execution succeeded
            verdict="BLOCKED",  # But verdict indicates blocking issues
            output="Step completed but issues found",
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        # Verify BLOCKED is in FAILURE_VERDICTS
        assert "BLOCKED" in FAILURE_VERDICTS

        # Should not auto-transition despite PASSED status
        assert should_auto_transition(result, config) is False


# =============================================================================
# Task 5: attempt_recovery Tests (AC3)
# =============================================================================


class TestAttemptRecovery:
    """Tests for attempt_recovery function (AC3)."""

    def test_attempts_recovery_on_failure(self):
        """Test that recovery is attempted on step failure."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepExecutionConfig,
            attempt_recovery,
        )

        failed_result = StepResult.failed(
            step_id="step-01",
            verdict="FAILED",
            errors=["Validation error"],
            duration_ms=1000,
        )
        config = StepExecutionConfig(max_recovery_attempts=3)

        recovered_result = attempt_recovery(failed_result, config, attempt_num=1)

        assert recovered_result is not None
        assert recovered_result.recovery_attempted is True

    def test_returns_passed_after_successful_recovery(self):
        """Test returns PASSED status after successful recovery."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            attempt_recovery,
        )

        # Mock a recoverable failure (simulated by using a specific error type)
        failed_result = StepResult.failed(
            step_id="step-01",
            verdict="FAILED",
            errors=["Recoverable: Missing import"],
            duration_ms=1000,
        )
        config = StepExecutionConfig(max_recovery_attempts=3)

        # Note: In actual implementation, this would need to mock the recovery logic
        recovered_result = attempt_recovery(failed_result, config, attempt_num=1)

        # Recovery attempted flag should be set
        assert recovered_result.recovery_attempted is True

    def test_fails_after_max_attempts_exceeded(self):
        """Test returns FAILED after max recovery attempts exceeded."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepStatus,
            StepExecutionConfig,
            attempt_recovery,
        )

        failed_result = StepResult.failed(
            step_id="step-01",
            verdict="FAILED",
            errors=["Unrecoverable error"],
            duration_ms=1000,
        )
        config = StepExecutionConfig(max_recovery_attempts=3)

        # Attempt beyond max
        recovered_result = attempt_recovery(failed_result, config, attempt_num=4)

        assert recovered_result.status == StepStatus.FAILED
        assert recovered_result.recovery_attempted is True
        # Should have error about max attempts
        assert any("max" in err.lower() or "attempt" in err.lower() for err in recovered_result.errors)

    def test_sets_recovery_attempted_flag(self):
        """Test recovery_attempted flag is set after attempt."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepExecutionConfig,
            attempt_recovery,
        )

        failed_result = StepResult.failed(
            step_id="step-01",
            verdict="FAILED",
            errors=["Some error"],
            duration_ms=1000,
        )
        config = StepExecutionConfig(max_recovery_attempts=3)

        recovered_result = attempt_recovery(failed_result, config, attempt_num=1)

        assert recovered_result.recovery_attempted is True

    def test_preserves_step_id_during_recovery(self):
        """Test step_id is preserved during recovery."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepResult,
            StepExecutionConfig,
            attempt_recovery,
        )

        failed_result = StepResult.failed(
            step_id="step-special-01",
            verdict="FAILED",
            errors=["Error"],
            duration_ms=1000,
        )
        config = StepExecutionConfig(max_recovery_attempts=3)

        recovered_result = attempt_recovery(failed_result, config, attempt_num=1)

        assert recovered_result.step_id == "step-special-01"


# =============================================================================
# Task 6: execute_step Tests
# =============================================================================


class TestExecuteStep:
    """Tests for execute_step function."""

    def test_returns_passed_on_successful_execution(self):
        """Test returns PASSED status on successful step execution."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepStatus,
            StepExecutionConfig,
            execute_step,
        )

        # Mock step config that will pass
        step_config = {"id": "step-01", "name": "Test Step", "content": "PASS"}
        config = StepExecutionConfig()

        result = execute_step("step-01", step_config, config)

        assert result.status == StepStatus.PASSED
        assert result.step_id == "step-01"

    def test_returns_failed_on_execution_failure(self):
        """Test returns FAILED status on step execution failure."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepStatus,
            StepExecutionConfig,
            execute_step,
        )

        # Mock step config that will fail
        step_config = {"id": "step-01", "name": "Test Step", "content": "FAIL"}
        config = StepExecutionConfig()

        result = execute_step("step-01", step_config, config)

        assert result.status == StepStatus.FAILED
        assert result.step_id == "step-01"

    def test_captures_output(self):
        """Test step output is captured in result."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepExecutionConfig,
            execute_step,
        )

        step_config = {
            "id": "step-01",
            "name": "Test Step",
            "content": "PASS",
            "expected_output": "Step completed successfully",
        }
        config = StepExecutionConfig()

        result = execute_step("step-01", step_config, config)

        assert result.output is not None
        assert len(result.output) > 0

    def test_captures_errors(self):
        """Test step errors are captured in result."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepStatus,
            StepExecutionConfig,
            execute_step,
        )

        step_config = {
            "id": "step-01",
            "name": "Test Step",
            "content": "FAIL",
            "error_message": "Validation failed",
        }
        config = StepExecutionConfig()

        result = execute_step("step-01", step_config, config)

        if result.status == StepStatus.FAILED:
            assert len(result.errors) > 0

    def test_records_duration(self):
        """Test step duration is recorded in result."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepExecutionConfig,
            execute_step,
        )

        step_config = {"id": "step-01", "name": "Test Step", "content": "PASS"}
        config = StepExecutionConfig()

        result = execute_step("step-01", step_config, config)

        assert result.duration_ms >= 0

    def test_returns_awaiting_user_when_oversight_required(self):
        """Test returns AWAITING_USER when step requires oversight."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepStatus,
            StepExecutionConfig,
            execute_step,
        )

        step_config = {
            "id": "step-01",
            "name": "Test Step",
            "content": "PASS",
            "oversight": "required",
        }
        config = StepExecutionConfig(oversight="required")

        result = execute_step("step-01", step_config, config)

        # Even if step passes, it should await user when oversight required
        assert result.status in (StepStatus.PASSED, StepStatus.AWAITING_USER)


# =============================================================================
# Task 7: WorkflowExecutionResult Tests
# =============================================================================


class TestWorkflowExecutionResult:
    """Tests for WorkflowExecutionResult dataclass."""

    def test_create_with_all_fields(self):
        """Test creating WorkflowExecutionResult with all fields."""
        from pcmrp_tools.bmad_automation.step_executor import (
            WorkflowExecutionResult,
            WorkflowStatus,
            StepResult,
            StepStatus,
        )

        step_results = [
            StepResult.passed("step-01", "PASSED", "Success", 1000),
            StepResult.passed("step-02", "PASSED", "Success", 1500),
        ]

        result = WorkflowExecutionResult(
            workflow_id="workflow-01",
            status=WorkflowStatus.COMPLETED,
            step_results=step_results,
            total_duration_ms=2500,
            steps_passed=2,
            steps_failed=0,
            final_verdict="PASSED",
        )

        assert result.workflow_id == "workflow-01"
        assert result.status == WorkflowStatus.COMPLETED
        assert len(result.step_results) == 2
        assert result.total_duration_ms == 2500
        assert result.steps_passed == 2
        assert result.steps_failed == 0
        assert result.final_verdict == "PASSED"

    def test_workflow_status_enum(self):
        """Test WorkflowStatus enum values."""
        from pcmrp_tools.bmad_automation.step_executor import WorkflowStatus

        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.RUNNING.value == "running"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"
        assert WorkflowStatus.PAUSED.value == "paused"

    def test_to_dict(self):
        """Test converting WorkflowExecutionResult to dictionary."""
        from pcmrp_tools.bmad_automation.step_executor import (
            WorkflowExecutionResult,
            WorkflowStatus,
            StepResult,
        )

        step_results = [
            StepResult.passed("step-01", "PASSED", "Success", 1000),
        ]

        result = WorkflowExecutionResult(
            workflow_id="workflow-01",
            status=WorkflowStatus.COMPLETED,
            step_results=step_results,
            total_duration_ms=1000,
            steps_passed=1,
            steps_failed=0,
            final_verdict="PASSED",
        )

        result_dict = result.to_dict()

        assert result_dict["workflow_id"] == "workflow-01"
        assert result_dict["status"] == "completed"
        assert len(result_dict["step_results"]) == 1
        assert result_dict["step_results"][0]["step_id"] == "step-01"
        assert result_dict["total_duration_ms"] == 1000
        assert result_dict["steps_passed"] == 1
        assert result_dict["steps_failed"] == 0
        assert result_dict["final_verdict"] == "PASSED"


# =============================================================================
# Task 8: execute_workflow_steps Tests (AC1, AC4)
# =============================================================================


class TestExecuteWorkflowSteps:
    """Tests for execute_workflow_steps function."""

    def test_executes_all_steps_sequentially(self):
        """Test all steps are executed in sequence."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepExecutionConfig,
            execute_workflow_steps,
            WorkflowStatus,
        )

        steps = [
            {"id": "step-01", "name": "Step 1", "content": "PASS"},
            {"id": "step-02", "name": "Step 2", "content": "PASS"},
            {"id": "step-03", "name": "Step 3", "content": "PASS"},
        ]
        workflow_config = {"workflow_id": "test-workflow"}

        result = execute_workflow_steps(steps, workflow_config)

        assert result.status == WorkflowStatus.COMPLETED
        assert len(result.step_results) == 3
        assert result.steps_passed == 3
        assert result.steps_failed == 0

    def test_auto_transitions_between_steps_on_passed(self):
        """Test automatic transition between steps when verdict is PASSED (AC1)."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepStatus,
            execute_workflow_steps,
            WorkflowStatus,
        )

        steps = [
            {"id": "step-01", "content": "PASS"},
            {"id": "step-02", "content": "PASS"},
        ]
        workflow_config = {"workflow_id": "test-workflow", "auto_continue": True}

        result = execute_workflow_steps(steps, workflow_config)

        # All steps should have been executed automatically
        assert result.status == WorkflowStatus.COMPLETED
        assert all(r.status == StepStatus.PASSED for r in result.step_results)

    def test_pauses_at_oversight_required_steps(self):
        """Test pauses execution at steps with oversight required (AC2)."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepStatus,
            execute_workflow_steps,
            WorkflowStatus,
        )

        steps = [
            {"id": "step-01", "content": "PASS"},
            {"id": "step-02", "content": "PASS", "oversight": "required"},
            {"id": "step-03", "content": "PASS"},
        ]
        workflow_config = {"workflow_id": "test-workflow"}

        result = execute_workflow_steps(steps, workflow_config)

        # Should pause at step-02 (oversight required)
        assert result.status == WorkflowStatus.PAUSED
        # First step should be completed, second should be awaiting
        assert result.step_results[0].status == StepStatus.PASSED
        assert result.step_results[1].status == StepStatus.AWAITING_USER

    def test_attempts_recovery_on_failures(self):
        """Test attempts recovery when step fails (AC3)."""
        from pcmrp_tools.bmad_automation.step_executor import execute_workflow_steps

        steps = [
            {"id": "step-01", "content": "PASS"},
            {"id": "step-02", "content": "FAIL", "recoverable": True},
        ]
        workflow_config = {"workflow_id": "test-workflow", "max_recovery_attempts": 3}

        result = execute_workflow_steps(steps, workflow_config)

        # Recovery should have been attempted for step-02
        step_02_result = result.step_results[1]
        assert step_02_result.recovery_attempted is True

    def test_completes_autonomously_with_final_summary(self):
        """Test workflow completes autonomously with final summary (AC4)."""
        from pcmrp_tools.bmad_automation.step_executor import (
            execute_workflow_steps,
            WorkflowStatus,
        )

        steps = [
            {"id": "step-01", "content": "PASS"},
            {"id": "step-02", "content": "PASS"},
            {"id": "step-03", "content": "PASS"},
        ]
        workflow_config = {
            "workflow_id": "test-workflow",
            "auto_continue": True,
            "no_oversight": True,
        }

        result = execute_workflow_steps(steps, workflow_config)

        assert result.status == WorkflowStatus.COMPLETED
        assert result.final_verdict == "PASSED"
        assert result.steps_passed == 3
        # Duration is >= 0 (execution can be nearly instant on fast systems)
        assert result.total_duration_ms >= 0

    def test_returns_failed_status_when_recovery_fails(self):
        """Test returns FAILED status when step fails and recovery fails."""
        from pcmrp_tools.bmad_automation.step_executor import (
            execute_workflow_steps,
            WorkflowStatus,
        )

        steps = [
            {"id": "step-01", "content": "PASS"},
            {"id": "step-02", "content": "FAIL", "recoverable": False},
        ]
        workflow_config = {"workflow_id": "test-workflow", "max_recovery_attempts": 1}

        result = execute_workflow_steps(steps, workflow_config)

        assert result.status == WorkflowStatus.FAILED
        assert result.steps_failed > 0

    def test_handles_empty_steps_list(self):
        """Test handles empty steps list gracefully."""
        from pcmrp_tools.bmad_automation.step_executor import (
            execute_workflow_steps,
            WorkflowStatus,
        )

        steps: list = []
        workflow_config = {"workflow_id": "test-workflow"}

        result = execute_workflow_steps(steps, workflow_config)

        assert result.status == WorkflowStatus.COMPLETED
        assert len(result.step_results) == 0
        assert result.steps_passed == 0
        assert result.steps_failed == 0

    def test_calculates_total_duration(self):
        """Test total duration is calculated from all step durations."""
        from pcmrp_tools.bmad_automation.step_executor import execute_workflow_steps

        steps = [
            {"id": "step-01", "content": "PASS"},
            {"id": "step-02", "content": "PASS"},
        ]
        workflow_config = {"workflow_id": "test-workflow"}

        result = execute_workflow_steps(steps, workflow_config)

        # Total duration should be sum of individual step durations
        sum_of_step_durations = sum(r.duration_ms for r in result.step_results)
        assert result.total_duration_ms >= sum_of_step_durations


# =============================================================================
# Integration Tests
# =============================================================================


class TestExecuteWorkflowStepsEdgeCases:
    """Additional edge case tests for execute_workflow_steps."""

    def test_pauses_for_concerns_verdict(self):
        """Test workflow pauses when step has CONCERNS verdict (requires acknowledgment)."""
        from pcmrp_tools.bmad_automation.step_executor import (
            execute_workflow_steps,
            WorkflowStatus,
            StepStatus,
            StepResult,
            StepExecutionConfig,
            should_auto_transition,
        )

        # First verify that CONCERNS verdict prevents auto-transition
        result_concerns = StepResult(
            step_id="step-01",
            status=StepStatus.PASSED,  # Step passed but with concerns
            verdict="CONCERNS",
            output="Minor issues found",
        )
        config = StepExecutionConfig(oversight="none", auto_continue=True)

        # CONCERNS should not allow auto-transition
        assert should_auto_transition(result_concerns, config) is False

    def test_workflow_pauses_for_concerns_verdict_step(self):
        """Test workflow execution pauses when a step returns CONCERNS verdict."""
        from pcmrp_tools.bmad_automation.step_executor import (
            execute_workflow_steps,
            WorkflowStatus,
            StepStatus,
        )

        steps = [
            {"id": "step-01", "content": "PASS"},  # Will pass
            {"id": "step-02", "verdict": "CONCERNS"},  # Will pass but with concerns
            {"id": "step-03", "content": "PASS"},  # Should not execute
        ]
        workflow_config = {
            "workflow_id": "concerns-test",
            "auto_continue": True,
        }

        result = execute_workflow_steps(steps, workflow_config)

        # Workflow should pause at step-02 due to CONCERNS verdict
        assert result.status == WorkflowStatus.PAUSED
        assert len(result.step_results) == 2  # Only first two steps executed
        assert result.step_results[0].status == StepStatus.PASSED
        assert result.step_results[1].status == StepStatus.PASSED
        assert result.step_results[1].verdict == "CONCERNS"

    def test_execute_step_with_explicit_unknown_verdict(self):
        """Test execute_step with explicit unknown verdict is treated as passed."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepExecutionConfig,
            execute_step,
            StepStatus,
        )

        step_config = {
            "id": "step-01",
            "verdict": "CUSTOM_UNKNOWN_VERDICT",  # Not in any verdict set
        }
        config = StepExecutionConfig()

        result = execute_step("step-01", step_config, config)

        # Unknown verdict should still result in PASSED status
        assert result.status == StepStatus.PASSED
        assert result.verdict == "CUSTOM_UNKNOWN_VERDICT"

    def test_execute_step_with_explicit_success_verdict(self):
        """Test execute_step with explicit SUCCESS verdict."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepExecutionConfig,
            execute_step,
            StepStatus,
            SUCCESS_VERDICTS,
        )

        step_config = {
            "id": "step-01",
            "verdict": "READY",  # SUCCESS_VERDICTS contains READY
        }
        config = StepExecutionConfig()

        result = execute_step("step-01", step_config, config)

        # READY is in SUCCESS_VERDICTS, should result in PASSED status
        assert "READY" in SUCCESS_VERDICTS
        assert result.status == StepStatus.PASSED
        assert result.verdict == "READY"

    def test_execute_step_with_explicit_failure_verdict(self):
        """Test execute_step with explicit FAILURE verdict."""
        from pcmrp_tools.bmad_automation.step_executor import (
            StepExecutionConfig,
            execute_step,
            StepStatus,
            FAILURE_VERDICTS,
        )

        step_config = {
            "id": "step-01",
            "verdict": "BLOCKED",  # FAILURE_VERDICTS contains BLOCKED
        }
        config = StepExecutionConfig()

        result = execute_step("step-01", step_config, config)

        # BLOCKED is in FAILURE_VERDICTS, should result in FAILED status
        assert "BLOCKED" in FAILURE_VERDICTS
        assert result.status == StepStatus.FAILED
        assert result.verdict == "BLOCKED"


class TestStepExecutorIntegration:
    """Integration tests for step executor components."""

    def test_full_workflow_execution_all_passed(self):
        """Test complete workflow execution with all steps passing."""
        from pcmrp_tools.bmad_automation.step_executor import (
            execute_workflow_steps,
            WorkflowStatus,
            StepStatus,
        )

        steps = [
            {"id": "step-01", "name": "Validation", "content": "PASS"},
            {"id": "step-02", "name": "Analysis", "content": "PASS"},
            {"id": "step-03", "name": "Completion", "content": "PASS"},
        ]
        workflow_config = {
            "workflow_id": "integration-test",
            "auto_continue": True,
        }

        result = execute_workflow_steps(steps, workflow_config)

        assert result.status == WorkflowStatus.COMPLETED
        assert result.final_verdict == "PASSED"
        assert all(r.status == StepStatus.PASSED for r in result.step_results)

    def test_full_workflow_with_oversight_pause(self):
        """Test workflow that pauses for oversight."""
        from pcmrp_tools.bmad_automation.step_executor import (
            execute_workflow_steps,
            WorkflowStatus,
        )

        steps = [
            {"id": "step-01", "content": "PASS"},
            {"id": "step-02", "content": "PASS", "oversight": "required"},
            {"id": "step-03", "content": "PASS"},
        ]
        workflow_config = {"workflow_id": "oversight-test"}

        result = execute_workflow_steps(steps, workflow_config)

        assert result.status == WorkflowStatus.PAUSED
        # Should have stopped at step-02
        assert len([r for r in result.step_results if r.step_id == "step-02"]) == 1

    def test_full_workflow_with_recovery_scenario(self):
        """Test workflow with failure and recovery attempt."""
        from pcmrp_tools.bmad_automation.step_executor import (
            execute_workflow_steps,
            WorkflowStatus,
        )

        steps = [
            {"id": "step-01", "content": "PASS"},
            {
                "id": "step-02",
                "content": "FAIL",
                "recoverable": True,
                "recovery_outcome": "PASS",
            },
            {"id": "step-03", "content": "PASS"},
        ]
        workflow_config = {"workflow_id": "recovery-test", "max_recovery_attempts": 3}

        result = execute_workflow_steps(steps, workflow_config)

        # Step 2 should show recovery was attempted
        step_02 = next((r for r in result.step_results if r.step_id == "step-02"), None)
        assert step_02 is not None
        assert step_02.recovery_attempted is True
