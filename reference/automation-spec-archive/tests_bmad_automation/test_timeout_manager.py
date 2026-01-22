"""Tests for Timeout Manager.

This module tests the timeout enforcement functionality for BMAD workflow automation.

Story: 2b-9 - Timeout Enforcement
Epic: 2b - Menu Handling & Navigation

TDD: Tests are written FIRST, before implementation.

Timeout Hierarchy:
    - Workflow: 1800 seconds (30 minutes)
    - Nested operation: 300 seconds (5 minutes)
    - Agent: 60 seconds (1 minute)
"""

import pytest
from dataclasses import asdict
import time

from pcmrp_tools.bmad_automation.timeout_manager import (
    # Task 1: Timeout Configuration
    TimeoutLevel,
    TIMEOUT_SECONDS,
    TimeoutConfig,
    get_timeout_for_level,
    # Task 2: TimeoutManager Class
    TimeoutState,
    TimeoutManager,
    # Task 3: Workflow Timeout Enforcement
    WorkflowTimeoutError,
    enforce_workflow_timeout,
    # Task 4: Nested Operation Timeout Enforcement
    NestedTimeoutError,
    enforce_nested_timeout,
    # Task 5: Agent Timeout Enforcement
    AgentTimeoutError,
    enforce_agent_timeout,
    # Task 6: State Preservation
    PreservedTimeoutState,
    preserve_state_on_timeout,
    get_preserved_state,
    clear_preserved_state,
    # Task 7: Timeout Logging
    TimeoutLog,
    log_timeout,
    get_timeout_logs,
    clear_timeout_logs,
    # Task 8: Context Managers (Integration)
    workflow_timeout,
    nested_timeout,
    agent_timeout,
)


# =============================================================================
# Task 1: Timeout Configuration Tests
# =============================================================================


class TestTimeoutLevelEnum:
    """Tests for TimeoutLevel enum (Task 1.1)."""

    def test_timeout_level_has_workflow(self):
        """TimeoutLevel should have WORKFLOW level."""
        assert hasattr(TimeoutLevel, "WORKFLOW")
        assert TimeoutLevel.WORKFLOW is not None

    def test_timeout_level_has_nested(self):
        """TimeoutLevel should have NESTED level."""
        assert hasattr(TimeoutLevel, "NESTED")
        assert TimeoutLevel.NESTED is not None

    def test_timeout_level_has_agent(self):
        """TimeoutLevel should have AGENT level."""
        assert hasattr(TimeoutLevel, "AGENT")
        assert TimeoutLevel.AGENT is not None

    def test_timeout_levels_are_distinct(self):
        """All TimeoutLevel values should be distinct."""
        levels = [TimeoutLevel.WORKFLOW, TimeoutLevel.NESTED, TimeoutLevel.AGENT]
        assert len(set(levels)) == 3


class TestTimeoutSecondsConstant:
    """Tests for TIMEOUT_SECONDS constant (Task 1.2)."""

    def test_timeout_seconds_is_dict(self):
        """TIMEOUT_SECONDS should be a dictionary."""
        assert isinstance(TIMEOUT_SECONDS, dict)

    def test_workflow_timeout_is_1800(self):
        """WORKFLOW timeout should be 1800 seconds (30 minutes) (AC #1)."""
        assert TIMEOUT_SECONDS[TimeoutLevel.WORKFLOW] == 1800

    def test_nested_timeout_is_300(self):
        """NESTED timeout should be 300 seconds (5 minutes) (AC #2)."""
        assert TIMEOUT_SECONDS[TimeoutLevel.NESTED] == 300

    def test_agent_timeout_is_60(self):
        """AGENT timeout should be 60 seconds (1 minute) (AC #3)."""
        assert TIMEOUT_SECONDS[TimeoutLevel.AGENT] == 60

    def test_all_timeout_levels_have_values(self):
        """All TimeoutLevel values should have timeout seconds defined."""
        for level in TimeoutLevel:
            assert level in TIMEOUT_SECONDS


class TestTimeoutConfigDataclass:
    """Tests for TimeoutConfig dataclass (Task 1.3)."""

    def test_timeout_config_creation(self):
        """TimeoutConfig should be creatable with all fields."""
        config = TimeoutConfig(
            level=TimeoutLevel.WORKFLOW,
            timeout_seconds=1800,
            error_type="workflow_timeout",
        )
        assert config.level == TimeoutLevel.WORKFLOW
        assert config.timeout_seconds == 1800
        assert config.error_type == "workflow_timeout"

    def test_timeout_config_for_nested(self):
        """TimeoutConfig should work for NESTED level."""
        config = TimeoutConfig(
            level=TimeoutLevel.NESTED,
            timeout_seconds=300,
            error_type="nested_timeout",
        )
        assert config.level == TimeoutLevel.NESTED
        assert config.timeout_seconds == 300
        assert config.error_type == "nested_timeout"

    def test_timeout_config_for_agent(self):
        """TimeoutConfig should work for AGENT level."""
        config = TimeoutConfig(
            level=TimeoutLevel.AGENT,
            timeout_seconds=60,
            error_type="agent_timeout",
        )
        assert config.level == TimeoutLevel.AGENT
        assert config.timeout_seconds == 60
        assert config.error_type == "agent_timeout"

    def test_timeout_config_to_dict(self):
        """TimeoutConfig should be serializable to dict."""
        config = TimeoutConfig(
            level=TimeoutLevel.WORKFLOW,
            timeout_seconds=1800,
            error_type="workflow_timeout",
        )
        result = asdict(config)
        assert result["level"] == TimeoutLevel.WORKFLOW
        assert result["timeout_seconds"] == 1800
        assert result["error_type"] == "workflow_timeout"


class TestGetTimeoutForLevel:
    """Tests for get_timeout_for_level function (Task 1.4, 1.5)."""

    def test_get_timeout_for_workflow_level(self):
        """get_timeout_for_level(WORKFLOW) should return correct config."""
        config = get_timeout_for_level(TimeoutLevel.WORKFLOW)
        assert isinstance(config, TimeoutConfig)
        assert config.level == TimeoutLevel.WORKFLOW
        assert config.timeout_seconds == 1800
        assert config.error_type == "workflow_timeout"

    def test_get_timeout_for_nested_level(self):
        """get_timeout_for_level(NESTED) should return correct config."""
        config = get_timeout_for_level(TimeoutLevel.NESTED)
        assert isinstance(config, TimeoutConfig)
        assert config.level == TimeoutLevel.NESTED
        assert config.timeout_seconds == 300
        assert config.error_type == "nested_timeout"

    def test_get_timeout_for_agent_level(self):
        """get_timeout_for_level(AGENT) should return correct config."""
        config = get_timeout_for_level(TimeoutLevel.AGENT)
        assert isinstance(config, TimeoutConfig)
        assert config.level == TimeoutLevel.AGENT
        assert config.timeout_seconds == 60
        assert config.error_type == "agent_timeout"


# =============================================================================
# Task 2: TimeoutManager Class Tests
# =============================================================================


class TestTimeoutStateDataclass:
    """Tests for TimeoutState dataclass."""

    def test_timeout_state_creation(self):
        """TimeoutState should be creatable with all fields."""
        state = TimeoutState(
            operation_id="op-123",
            level=TimeoutLevel.WORKFLOW,
            start_time=1000.0,
            timeout_seconds=1800,
        )
        assert state.operation_id == "op-123"
        assert state.level == TimeoutLevel.WORKFLOW
        assert state.start_time == 1000.0
        assert state.timeout_seconds == 1800

    def test_timeout_state_to_dict(self):
        """TimeoutState should be serializable to dict."""
        state = TimeoutState(
            operation_id="op-123",
            level=TimeoutLevel.NESTED,
            start_time=500.0,
            timeout_seconds=300,
        )
        result = asdict(state)
        assert result["operation_id"] == "op-123"
        assert result["timeout_seconds"] == 300


class TestTimeoutManagerClass:
    """Tests for TimeoutManager class (Task 2.1)."""

    def test_timeout_manager_creation(self):
        """TimeoutManager should be instantiable."""
        manager = TimeoutManager()
        assert manager is not None

    def test_timeout_manager_has_active_timeouts_dict(self):
        """TimeoutManager should have _active_timeouts dict (Task 2.5)."""
        manager = TimeoutManager()
        assert hasattr(manager, "_active_timeouts")
        assert isinstance(manager._active_timeouts, dict)


class TestTimeoutManagerStartTimeout:
    """Tests for TimeoutManager.start_timeout method (Task 2.2)."""

    def test_start_timeout_returns_timeout_state(self):
        """start_timeout should return TimeoutState."""
        manager = TimeoutManager()
        state = manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        assert isinstance(state, TimeoutState)

    def test_start_timeout_duplicate_operation_id_overwrites(self):
        """start_timeout called twice with same operation_id silently overwrites.

        This documents the current behavior: calling start_timeout() with an
        operation_id that already has an active timeout will overwrite the
        existing timeout state without warning. The new timeout replaces the
        old one, resetting the start_time.
        """
        manager = TimeoutManager()
        # Start first timeout
        first_state = manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-dup")
        first_start_time = first_state.start_time

        # Wait a tiny bit to ensure time difference
        time.sleep(0.001)

        # Start second timeout with same operation_id but different level
        second_state = manager.start_timeout(TimeoutLevel.AGENT, "wf-dup")

        # Verify the timeout was overwritten
        assert second_state.level == TimeoutLevel.AGENT
        assert second_state.start_time > first_start_time
        assert second_state.timeout_seconds == 60  # AGENT timeout

        # Verify only one entry exists in active timeouts
        assert len([k for k in manager._active_timeouts if k == "wf-dup"]) == 1
        assert manager._active_timeouts["wf-dup"].level == TimeoutLevel.AGENT

    def test_start_timeout_records_operation_id(self):
        """start_timeout should record the operation_id."""
        manager = TimeoutManager()
        state = manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        assert state.operation_id == "wf-123"

    def test_start_timeout_records_level(self):
        """start_timeout should record the level."""
        manager = TimeoutManager()
        state = manager.start_timeout(TimeoutLevel.NESTED, "op-456")
        assert state.level == TimeoutLevel.NESTED

    def test_start_timeout_records_start_time(self):
        """start_timeout should record a start_time."""
        manager = TimeoutManager()
        before = time.monotonic()
        state = manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        after = time.monotonic()
        assert before <= state.start_time <= after

    def test_start_timeout_uses_correct_timeout_seconds(self):
        """start_timeout should use correct timeout_seconds for level."""
        manager = TimeoutManager()

        wf_state = manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-1")
        assert wf_state.timeout_seconds == 1800

        nested_state = manager.start_timeout(TimeoutLevel.NESTED, "nested-1")
        assert nested_state.timeout_seconds == 300

        agent_state = manager.start_timeout(TimeoutLevel.AGENT, "agent-1")
        assert agent_state.timeout_seconds == 60

    def test_start_timeout_adds_to_active_timeouts(self):
        """start_timeout should add operation to _active_timeouts."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        assert "wf-123" in manager._active_timeouts


class TestTimeoutManagerCheckTimeout:
    """Tests for TimeoutManager.check_timeout method (Task 2.3)."""

    def test_check_timeout_returns_false_when_not_expired(self):
        """check_timeout should return False when timeout not expired."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        # Just started, should not be expired
        assert manager.check_timeout("wf-123") is False

    def test_check_timeout_returns_true_when_expired(self):
        """check_timeout should return True when timeout expired."""
        manager = TimeoutManager()
        # Manually set a start time in the past
        state = TimeoutState(
            operation_id="wf-old",
            level=TimeoutLevel.AGENT,
            start_time=time.monotonic() - 100,  # 100 seconds ago
            timeout_seconds=60,  # 60 second timeout
        )
        manager._active_timeouts["wf-old"] = state
        assert manager.check_timeout("wf-old") is True

    def test_check_timeout_returns_none_for_unknown_operation(self):
        """check_timeout should return None for unknown operation_id."""
        manager = TimeoutManager()
        result = manager.check_timeout("unknown-op")
        assert result is None

    def test_check_timeout_boundary_at_timeout_exactly(self):
        """check_timeout at exactly timeout_seconds should return True."""
        manager = TimeoutManager()
        current_time = time.monotonic()
        state = TimeoutState(
            operation_id="wf-exact",
            level=TimeoutLevel.AGENT,
            start_time=current_time - 60,  # Exactly 60 seconds ago
            timeout_seconds=60,
        )
        manager._active_timeouts["wf-exact"] = state
        # At exactly timeout boundary, should be considered expired
        assert manager.check_timeout("wf-exact") is True

    def test_check_timeout_just_before_expiry(self):
        """check_timeout just before expiry should return False."""
        manager = TimeoutManager()
        current_time = time.monotonic()
        state = TimeoutState(
            operation_id="wf-almost",
            level=TimeoutLevel.AGENT,
            start_time=current_time - 59,  # 59 seconds ago (1 second remaining)
            timeout_seconds=60,
        )
        manager._active_timeouts["wf-almost"] = state
        assert manager.check_timeout("wf-almost") is False


class TestTimeoutManagerCancelTimeout:
    """Tests for TimeoutManager.cancel_timeout method (Task 2.4)."""

    def test_cancel_timeout_removes_from_active(self):
        """cancel_timeout should remove operation from _active_timeouts."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        assert "wf-123" in manager._active_timeouts

        manager.cancel_timeout("wf-123")
        assert "wf-123" not in manager._active_timeouts

    def test_cancel_timeout_returns_true_on_success(self):
        """cancel_timeout should return True when operation was active."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        result = manager.cancel_timeout("wf-123")
        assert result is True

    def test_cancel_timeout_returns_false_for_unknown(self):
        """cancel_timeout should return False for unknown operation_id."""
        manager = TimeoutManager()
        result = manager.cancel_timeout("unknown-op")
        assert result is False

    def test_cancel_timeout_idempotent(self):
        """cancel_timeout called twice should not raise error."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        manager.cancel_timeout("wf-123")
        # Second cancel should return False but not raise
        result = manager.cancel_timeout("wf-123")
        assert result is False


class TestTimeoutManagerHasActiveTimeout:
    """Tests for TimeoutManager.has_active_timeout method (Issue 3 fix)."""

    def test_has_active_timeout_returns_true_when_active(self):
        """has_active_timeout should return True when timeout is active."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        assert manager.has_active_timeout("wf-123") is True

    def test_has_active_timeout_returns_false_when_not_active(self):
        """has_active_timeout should return False when no timeout exists."""
        manager = TimeoutManager()
        assert manager.has_active_timeout("unknown-op") is False

    def test_has_active_timeout_returns_false_after_cancel(self):
        """has_active_timeout should return False after timeout is cancelled."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        assert manager.has_active_timeout("wf-123") is True
        manager.cancel_timeout("wf-123")
        assert manager.has_active_timeout("wf-123") is False


class TestTimeoutManagerGetActiveTimeoutState:
    """Tests for TimeoutManager.get_active_timeout_state method (Issue 3 fix)."""

    def test_get_active_timeout_state_returns_state_when_active(self):
        """get_active_timeout_state should return TimeoutState when active."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        state = manager.get_active_timeout_state("wf-123")
        assert isinstance(state, TimeoutState)
        assert state.operation_id == "wf-123"
        assert state.level == TimeoutLevel.WORKFLOW

    def test_get_active_timeout_state_returns_none_when_not_active(self):
        """get_active_timeout_state should return None when no timeout exists."""
        manager = TimeoutManager()
        state = manager.get_active_timeout_state("unknown-op")
        assert state is None

    def test_get_active_timeout_state_returns_none_after_cancel(self):
        """get_active_timeout_state should return None after timeout is cancelled."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        assert manager.get_active_timeout_state("wf-123") is not None
        manager.cancel_timeout("wf-123")
        assert manager.get_active_timeout_state("wf-123") is None


class TestTimeoutManagerLifecycle:
    """Tests for complete timeout lifecycle (Task 2.6)."""

    def test_full_lifecycle_success_path(self):
        """Test full lifecycle: start -> check (not expired) -> cancel."""
        manager = TimeoutManager()

        # Start timeout
        state = manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-success")
        assert state.operation_id == "wf-success"
        assert "wf-success" in manager._active_timeouts

        # Check - should not be expired
        assert manager.check_timeout("wf-success") is False

        # Cancel on success
        result = manager.cancel_timeout("wf-success")
        assert result is True
        assert "wf-success" not in manager._active_timeouts

    def test_multiple_concurrent_timeouts(self):
        """TimeoutManager should handle multiple concurrent timeouts."""
        manager = TimeoutManager()

        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-1")
        manager.start_timeout(TimeoutLevel.NESTED, "nested-1")
        manager.start_timeout(TimeoutLevel.AGENT, "agent-1")

        assert len(manager._active_timeouts) == 3
        assert "wf-1" in manager._active_timeouts
        assert "nested-1" in manager._active_timeouts
        assert "agent-1" in manager._active_timeouts

    def test_get_elapsed_time(self):
        """TimeoutManager should provide elapsed time for operation."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")

        elapsed = manager.get_elapsed_time("wf-123")
        assert elapsed is not None
        assert elapsed >= 0

    def test_get_remaining_time(self):
        """TimeoutManager should provide remaining time for operation."""
        manager = TimeoutManager()
        manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")

        remaining = manager.get_remaining_time("wf-123")
        assert remaining is not None
        # Should be close to full timeout (1800) minus small elapsed
        assert 1790 <= remaining <= 1800

    def test_get_elapsed_time_unknown_operation(self):
        """get_elapsed_time should return None for unknown operation."""
        manager = TimeoutManager()
        elapsed = manager.get_elapsed_time("unknown-op")
        assert elapsed is None

    def test_get_remaining_time_unknown_operation(self):
        """get_remaining_time should return None for unknown operation."""
        manager = TimeoutManager()
        remaining = manager.get_remaining_time("unknown-op")
        assert remaining is None


# =============================================================================
# Task 3: Workflow Timeout Enforcement Tests
# =============================================================================


class TestWorkflowTimeoutError:
    """Tests for WorkflowTimeoutError exception (Task 3.1)."""

    def test_workflow_timeout_error_is_exception(self):
        """WorkflowTimeoutError should be an Exception."""
        assert issubclass(WorkflowTimeoutError, Exception)

    def test_workflow_timeout_error_has_timeout_error_attr(self):
        """WorkflowTimeoutError should have timeout_error attribute."""
        error = WorkflowTimeoutError(
            "Workflow timed out",
            timeout_error="workflow_timeout",
            elapsed_time=1801.0,
            operation_context={"workflow_id": "wf-123"},
        )
        assert error.timeout_error == "workflow_timeout"

    def test_workflow_timeout_error_has_elapsed_time(self):
        """WorkflowTimeoutError should have elapsed_time attribute (Task 3.4)."""
        error = WorkflowTimeoutError(
            "Workflow timed out",
            timeout_error="workflow_timeout",
            elapsed_time=1801.0,
            operation_context={"workflow_id": "wf-123"},
        )
        assert error.elapsed_time == 1801.0

    def test_workflow_timeout_error_has_operation_context(self):
        """WorkflowTimeoutError should have operation_context attribute (Task 3.4)."""
        context = {"workflow_id": "wf-123", "step": "step-5"}
        error = WorkflowTimeoutError(
            "Workflow timed out",
            timeout_error="workflow_timeout",
            elapsed_time=1801.0,
            operation_context=context,
        )
        assert error.operation_context == context

    def test_workflow_timeout_error_str(self):
        """WorkflowTimeoutError should have meaningful string representation."""
        error = WorkflowTimeoutError(
            "Workflow timed out after 1801 seconds",
            timeout_error="workflow_timeout",
            elapsed_time=1801.0,
            operation_context={"workflow_id": "wf-123"},
        )
        assert "Workflow timed out" in str(error)


class TestEnforceWorkflowTimeout:
    """Tests for enforce_workflow_timeout function (Task 3.2, 3.3, 3.5)."""

    def test_enforce_workflow_timeout_no_error_when_within_limit(self):
        """enforce_workflow_timeout should not raise when within 1800s."""
        # 1799 seconds elapsed - should be OK
        start_time = time.monotonic() - 1799
        # Should not raise
        enforce_workflow_timeout("wf-123", start_time)

    def test_enforce_workflow_timeout_raises_at_1800(self):
        """enforce_workflow_timeout should raise at exactly 1800 seconds (boundary)."""
        start_time = time.monotonic() - 1800
        with pytest.raises(WorkflowTimeoutError) as exc_info:
            enforce_workflow_timeout("wf-123", start_time)
        assert exc_info.value.timeout_error == "workflow_timeout"

    def test_enforce_workflow_timeout_raises_after_1801(self):
        """enforce_workflow_timeout should raise after 1801 seconds."""
        start_time = time.monotonic() - 1801
        with pytest.raises(WorkflowTimeoutError) as exc_info:
            enforce_workflow_timeout("wf-123", start_time)
        assert exc_info.value.timeout_error == "workflow_timeout"
        assert exc_info.value.elapsed_time >= 1801

    def test_enforce_workflow_timeout_includes_workflow_id_in_context(self):
        """enforce_workflow_timeout should include workflow_id in context."""
        start_time = time.monotonic() - 1801
        with pytest.raises(WorkflowTimeoutError) as exc_info:
            enforce_workflow_timeout("wf-123", start_time)
        assert exc_info.value.operation_context["workflow_id"] == "wf-123"

    def test_enforce_workflow_timeout_boundary_1799_no_error(self):
        """enforce_workflow_timeout at 1799s should not raise (Task 3.5)."""
        start_time = time.monotonic() - 1799
        # Should not raise - 1 second remaining
        enforce_workflow_timeout("wf-boundary", start_time)

    def test_enforce_workflow_timeout_includes_timeout_limit_in_context(self):
        """enforce_workflow_timeout should include timeout_limit_seconds in context."""
        start_time = time.monotonic() - 1801
        with pytest.raises(WorkflowTimeoutError) as exc_info:
            enforce_workflow_timeout("wf-123", start_time)
        assert exc_info.value.operation_context["timeout_limit_seconds"] == 1800


# =============================================================================
# Task 4: Nested Operation Timeout Enforcement Tests
# =============================================================================


class TestNestedTimeoutError:
    """Tests for NestedTimeoutError exception (Task 4.1)."""

    def test_nested_timeout_error_is_exception(self):
        """NestedTimeoutError should be an Exception."""
        assert issubclass(NestedTimeoutError, Exception)

    def test_nested_timeout_error_has_timeout_error_attr(self):
        """NestedTimeoutError should have timeout_error attribute."""
        error = NestedTimeoutError(
            "Nested operation timed out",
            timeout_error="nested_timeout",
            elapsed_time=301.0,
            nested_operation_context={"operation_id": "op-123"},
            parent_notification={"parent_id": "wf-parent"},
        )
        assert error.timeout_error == "nested_timeout"

    def test_nested_timeout_error_has_elapsed_time(self):
        """NestedTimeoutError should have elapsed_time attribute."""
        error = NestedTimeoutError(
            "Nested operation timed out",
            timeout_error="nested_timeout",
            elapsed_time=301.0,
            nested_operation_context={"operation_id": "op-123"},
            parent_notification={"parent_id": "wf-parent"},
        )
        assert error.elapsed_time == 301.0

    def test_nested_timeout_error_has_nested_operation_context(self):
        """NestedTimeoutError should have nested_operation_context (Task 4.4)."""
        context = {"operation_id": "op-123", "operation_type": "validation"}
        error = NestedTimeoutError(
            "Nested operation timed out",
            timeout_error="nested_timeout",
            elapsed_time=301.0,
            nested_operation_context=context,
            parent_notification={"parent_id": "wf-parent"},
        )
        assert error.nested_operation_context == context

    def test_nested_timeout_error_has_parent_notification(self):
        """NestedTimeoutError should have parent_notification (Task 4.4)."""
        notification = {"parent_id": "wf-parent", "child_failed": True}
        error = NestedTimeoutError(
            "Nested operation timed out",
            timeout_error="nested_timeout",
            elapsed_time=301.0,
            nested_operation_context={"operation_id": "op-123"},
            parent_notification=notification,
        )
        assert error.parent_notification == notification


class TestEnforceNestedTimeout:
    """Tests for enforce_nested_timeout function (Task 4.2, 4.3, 4.5)."""

    def test_enforce_nested_timeout_no_error_when_within_limit(self):
        """enforce_nested_timeout should not raise when within 300s."""
        start_time = time.monotonic() - 299
        # Should not raise
        enforce_nested_timeout("op-123", "wf-parent", start_time)

    def test_enforce_nested_timeout_raises_at_300(self):
        """enforce_nested_timeout should raise at exactly 300 seconds."""
        start_time = time.monotonic() - 300
        with pytest.raises(NestedTimeoutError) as exc_info:
            enforce_nested_timeout("op-123", "wf-parent", start_time)
        assert exc_info.value.timeout_error == "nested_timeout"

    def test_enforce_nested_timeout_raises_after_301(self):
        """enforce_nested_timeout should raise after 301 seconds."""
        start_time = time.monotonic() - 301
        with pytest.raises(NestedTimeoutError) as exc_info:
            enforce_nested_timeout("op-123", "wf-parent", start_time)
        assert exc_info.value.elapsed_time >= 301

    def test_enforce_nested_timeout_includes_operation_id_in_context(self):
        """enforce_nested_timeout should include operation_id in context."""
        start_time = time.monotonic() - 301
        with pytest.raises(NestedTimeoutError) as exc_info:
            enforce_nested_timeout("op-123", "wf-parent", start_time)
        assert exc_info.value.nested_operation_context["operation_id"] == "op-123"

    def test_enforce_nested_timeout_notifies_parent(self):
        """enforce_nested_timeout should include parent notification (Task 4.3)."""
        start_time = time.monotonic() - 301
        with pytest.raises(NestedTimeoutError) as exc_info:
            enforce_nested_timeout("op-123", "wf-parent", start_time)
        assert exc_info.value.parent_notification["parent_id"] == "wf-parent"
        assert exc_info.value.parent_notification["child_operation_id"] == "op-123"
        assert exc_info.value.parent_notification["child_timed_out"] is True

    def test_enforce_nested_timeout_boundary_299_no_error(self):
        """enforce_nested_timeout at 299s should not raise (Task 4.5)."""
        start_time = time.monotonic() - 299
        # Should not raise - 1 second remaining
        enforce_nested_timeout("op-boundary", "wf-parent", start_time)

    def test_enforce_nested_timeout_includes_timeout_limit_in_context(self):
        """enforce_nested_timeout should include timeout_limit_seconds in context."""
        start_time = time.monotonic() - 301
        with pytest.raises(NestedTimeoutError) as exc_info:
            enforce_nested_timeout("op-123", "wf-parent", start_time)
        assert exc_info.value.nested_operation_context["timeout_limit_seconds"] == 300


# =============================================================================
# Acceptance Criteria Integration Tests
# =============================================================================


class TestAC1WorkflowTimeout30Minutes:
    """Tests for AC #1: Workflow timeout at 30 minutes."""

    def test_workflow_level_has_1800_second_timeout(self):
        """WORKFLOW level should have 1800 second timeout (30 min)."""
        assert TIMEOUT_SECONDS[TimeoutLevel.WORKFLOW] == 1800

    def test_workflow_timeout_config_has_correct_error_type(self):
        """WORKFLOW timeout config should have 'workflow_timeout' error type."""
        config = get_timeout_for_level(TimeoutLevel.WORKFLOW)
        assert config.error_type == "workflow_timeout"


class TestAC2NestedOperationTimeout5Minutes:
    """Tests for AC #2: Nested operation timeout at 5 minutes."""

    def test_nested_level_has_300_second_timeout(self):
        """NESTED level should have 300 second timeout (5 min)."""
        assert TIMEOUT_SECONDS[TimeoutLevel.NESTED] == 300

    def test_nested_timeout_config_has_correct_error_type(self):
        """NESTED timeout config should have 'nested_timeout' error type."""
        config = get_timeout_for_level(TimeoutLevel.NESTED)
        assert config.error_type == "nested_timeout"


class TestAC3AgentTimeout1Minute:
    """Tests for AC #3: Agent timeout at 1 minute."""

    def test_agent_level_has_60_second_timeout(self):
        """AGENT level should have 60 second timeout (1 min)."""
        assert TIMEOUT_SECONDS[TimeoutLevel.AGENT] == 60

    def test_agent_timeout_config_has_correct_error_type(self):
        """AGENT timeout config should have 'agent_timeout' error type."""
        config = get_timeout_for_level(TimeoutLevel.AGENT)
        assert config.error_type == "agent_timeout"


class TestTimeoutHierarchy:
    """Tests for timeout hierarchy ordering."""

    def test_workflow_timeout_greater_than_nested(self):
        """WORKFLOW timeout should be greater than NESTED timeout."""
        assert TIMEOUT_SECONDS[TimeoutLevel.WORKFLOW] > TIMEOUT_SECONDS[TimeoutLevel.NESTED]

    def test_nested_timeout_greater_than_agent(self):
        """NESTED timeout should be greater than AGENT timeout."""
        assert TIMEOUT_SECONDS[TimeoutLevel.NESTED] > TIMEOUT_SECONDS[TimeoutLevel.AGENT]

    def test_timeout_ratio_workflow_to_nested(self):
        """WORKFLOW should be 6x NESTED timeout (30min / 5min)."""
        ratio = TIMEOUT_SECONDS[TimeoutLevel.WORKFLOW] / TIMEOUT_SECONDS[TimeoutLevel.NESTED]
        assert ratio == 6.0

    def test_timeout_ratio_nested_to_agent(self):
        """NESTED should be 5x AGENT timeout (5min / 1min)."""
        ratio = TIMEOUT_SECONDS[TimeoutLevel.NESTED] / TIMEOUT_SECONDS[TimeoutLevel.AGENT]
        assert ratio == 5.0


# =============================================================================
# Task 5: Agent Timeout Enforcement Tests
# =============================================================================


class TestAgentTimeoutError:
    """Tests for AgentTimeoutError exception (Task 5.1)."""

    def test_agent_timeout_error_is_exception(self):
        """AgentTimeoutError should be an Exception."""
        assert issubclass(AgentTimeoutError, Exception)

    def test_agent_timeout_error_has_timeout_error_attr(self):
        """AgentTimeoutError should have timeout_error attribute."""
        error = AgentTimeoutError(
            "Agent timed out",
            timeout_error="agent_timeout",
            agent_id="agent-123",
        )
        assert error.timeout_error == "agent_timeout"

    def test_agent_timeout_error_has_agent_id(self):
        """AgentTimeoutError should have agent_id attribute."""
        error = AgentTimeoutError(
            "Agent timed out",
            timeout_error="agent_timeout",
            agent_id="agent-123",
        )
        assert error.agent_id == "agent-123"

    def test_agent_timeout_error_has_elapsed_time(self):
        """AgentTimeoutError should have elapsed_time attribute."""
        error = AgentTimeoutError(
            "Agent timed out",
            timeout_error="agent_timeout",
            agent_id="agent-123",
            elapsed_time=61.0,
        )
        assert error.elapsed_time == 61.0

    def test_agent_timeout_error_has_agent_context(self):
        """AgentTimeoutError should have agent_context attribute."""
        context = {"step": "validation", "item": "item-1"}
        error = AgentTimeoutError(
            "Agent timed out",
            timeout_error="agent_timeout",
            agent_id="agent-123",
            agent_context=context,
        )
        assert error.agent_context == context

    def test_agent_timeout_error_has_last_activity(self):
        """AgentTimeoutError should have last_activity attribute."""
        error = AgentTimeoutError(
            "Agent timed out",
            timeout_error="agent_timeout",
            agent_id="agent-123",
            last_activity=1000.5,
        )
        assert error.last_activity == 1000.5


class TestEnforceAgentTimeout:
    """Tests for enforce_agent_timeout function (Task 5.2, 5.3)."""

    def test_enforce_agent_timeout_no_error_when_within_limit(self):
        """enforce_agent_timeout should not raise when within 60s."""
        start_time = time.monotonic() - 59
        # Should not raise
        enforce_agent_timeout("agent-123", start_time)

    def test_enforce_agent_timeout_raises_at_60(self):
        """enforce_agent_timeout should raise at exactly 60 seconds."""
        start_time = time.monotonic() - 60
        with pytest.raises(AgentTimeoutError) as exc_info:
            enforce_agent_timeout("agent-123", start_time)
        assert exc_info.value.timeout_error == "agent_timeout"

    def test_enforce_agent_timeout_raises_after_61(self):
        """enforce_agent_timeout should raise after 61 seconds."""
        start_time = time.monotonic() - 61
        with pytest.raises(AgentTimeoutError) as exc_info:
            enforce_agent_timeout("agent-123", start_time)
        assert exc_info.value.elapsed_time >= 61

    def test_enforce_agent_timeout_includes_agent_id(self):
        """enforce_agent_timeout should include agent_id in error."""
        start_time = time.monotonic() - 61
        with pytest.raises(AgentTimeoutError) as exc_info:
            enforce_agent_timeout("agent-123", start_time)
        assert exc_info.value.agent_id == "agent-123"

    def test_enforce_agent_timeout_includes_context(self):
        """enforce_agent_timeout should include context if provided."""
        start_time = time.monotonic() - 61
        context = {"step": "validation"}
        with pytest.raises(AgentTimeoutError) as exc_info:
            enforce_agent_timeout("agent-123", start_time, context=context)
        assert exc_info.value.agent_context == context

    def test_enforce_agent_timeout_includes_last_activity(self):
        """enforce_agent_timeout should include last_activity if provided."""
        start_time = time.monotonic() - 61
        last_activity = time.monotonic() - 30
        with pytest.raises(AgentTimeoutError) as exc_info:
            enforce_agent_timeout(
                "agent-123", start_time, last_activity=last_activity
            )
        assert exc_info.value.last_activity == last_activity


# =============================================================================
# Task 6: State Preservation Tests
# =============================================================================


class TestPreservedTimeoutState:
    """Tests for PreservedTimeoutState dataclass (Task 6.1)."""

    def test_preserved_state_creation(self):
        """PreservedTimeoutState should be creatable."""
        preserved = PreservedTimeoutState(
            operation_id="op-123",
            state_snapshot={"step": 5, "data": "test"},
            timestamp=1000.0,
            level=TimeoutLevel.AGENT,
        )
        assert preserved.operation_id == "op-123"
        assert preserved.state_snapshot == {"step": 5, "data": "test"}
        assert preserved.timestamp == 1000.0
        assert preserved.level == TimeoutLevel.AGENT

    def test_preserved_state_optional_checkpoint(self):
        """PreservedTimeoutState should have optional checkpoint."""
        preserved = PreservedTimeoutState(
            operation_id="op-123",
            state_snapshot={},
            timestamp=1000.0,
            level=TimeoutLevel.WORKFLOW,
            checkpoint="checkpoint-5",
        )
        assert preserved.checkpoint == "checkpoint-5"


class TestPreserveStateOnTimeout:
    """Tests for preserve_state_on_timeout function (Task 6.2)."""

    def test_preserve_state_returns_preserved_state(self):
        """preserve_state_on_timeout should return PreservedTimeoutState."""
        result = preserve_state_on_timeout(
            "op-123",
            {"step": 5},
            level=TimeoutLevel.WORKFLOW,
        )
        assert isinstance(result, PreservedTimeoutState)
        assert result.operation_id == "op-123"
        assert result.state_snapshot == {"step": 5}

    def test_preserve_state_records_timestamp(self):
        """preserve_state_on_timeout should record current time."""
        before = time.monotonic()
        result = preserve_state_on_timeout("op-123", {})
        after = time.monotonic()
        assert before <= result.timestamp <= after

    def test_preserve_state_can_include_checkpoint(self):
        """preserve_state_on_timeout should accept checkpoint."""
        result = preserve_state_on_timeout(
            "op-123",
            {},
            checkpoint="cp-5",
        )
        assert result.checkpoint == "cp-5"


class TestGetPreservedState:
    """Tests for get_preserved_state function (Task 6.3)."""

    def test_get_preserved_state_retrieves_preserved(self):
        """get_preserved_state should retrieve preserved state."""
        preserve_state_on_timeout("op-retrieve", {"data": "test"})
        result = get_preserved_state("op-retrieve")
        assert result is not None
        assert result.state_snapshot == {"data": "test"}

    def test_get_preserved_state_returns_none_for_unknown(self):
        """get_preserved_state should return None for unknown operation."""
        result = get_preserved_state("unknown-op-xyz")
        assert result is None


class TestClearPreservedState:
    """Tests for clear_preserved_state function (Task 6.3)."""

    def test_clear_preserved_state_removes_state(self):
        """clear_preserved_state should remove the state."""
        preserve_state_on_timeout("op-clear", {"data": "test"})
        assert get_preserved_state("op-clear") is not None
        clear_preserved_state("op-clear")
        assert get_preserved_state("op-clear") is None

    def test_clear_preserved_state_idempotent(self):
        """clear_preserved_state should not error on unknown operation."""
        # Should not raise
        clear_preserved_state("unknown-op-clear")


# =============================================================================
# Task 7: Timeout Logging Tests
# =============================================================================


class TestTimeoutLog:
    """Tests for TimeoutLog dataclass (Task 7.1)."""

    def test_timeout_log_creation(self):
        """TimeoutLog should be creatable with all fields."""
        from datetime import datetime

        wall_time = datetime.now()
        log = TimeoutLog(
            level=TimeoutLevel.WORKFLOW,
            operation_id="op-123",
            elapsed_time=1801.0,
            context={"workflow_id": "wf-1"},
            error_type="workflow_timeout",
            timestamp=1000.0,
            wall_clock_time=wall_time,
        )
        assert log.level == TimeoutLevel.WORKFLOW
        assert log.operation_id == "op-123"
        assert log.elapsed_time == 1801.0
        assert log.context == {"workflow_id": "wf-1"}
        assert log.error_type == "workflow_timeout"
        assert log.timestamp == 1000.0
        assert log.wall_clock_time == wall_time

    def test_timeout_log_has_wall_clock_time_field(self):
        """TimeoutLog should have wall_clock_time field for human-readable timestamps.

        Issue 7 fix: Using monotonic time for audit logs makes them hard to read.
        The wall_clock_time field provides datetime for human-readable timestamps
        while keeping the monotonic timestamp field for elapsed calculations.
        """
        from datetime import datetime

        wall_time = datetime(2026, 1, 13, 10, 30, 45)
        log = TimeoutLog(
            level=TimeoutLevel.AGENT,
            operation_id="agent-123",
            elapsed_time=61.0,
            context={},
            error_type="agent_timeout",
            timestamp=1000.0,
            wall_clock_time=wall_time,
        )
        # wall_clock_time should be a datetime object
        assert isinstance(log.wall_clock_time, datetime)
        # It should be the actual wall clock time, not monotonic
        assert log.wall_clock_time.year == 2026
        assert log.wall_clock_time.month == 1
        assert log.wall_clock_time.day == 13


class TestLogTimeout:
    """Tests for log_timeout function (Task 7.2)."""

    def test_log_timeout_returns_timeout_log(self):
        """log_timeout should return TimeoutLog."""
        clear_timeout_logs()  # Clean state
        result = log_timeout(
            TimeoutLevel.AGENT,
            "agent-123",
            61.0,
            {"agent_id": "agent-123"},
        )
        assert isinstance(result, TimeoutLog)
        assert result.operation_id == "agent-123"

    def test_log_timeout_auto_sets_error_type(self):
        """log_timeout should auto-set error_type based on level."""
        clear_timeout_logs()
        result = log_timeout(
            TimeoutLevel.NESTED,
            "nested-op",
            301.0,
            {},
        )
        assert result.error_type == "nested_timeout"

    def test_log_timeout_records_timestamp(self):
        """log_timeout should record current timestamp."""
        clear_timeout_logs()
        before = time.monotonic()
        result = log_timeout(TimeoutLevel.WORKFLOW, "wf-1", 1801.0, {})
        after = time.monotonic()
        assert before <= result.timestamp <= after

    def test_log_timeout_records_wall_clock_time(self):
        """log_timeout should record wall clock time for human-readable timestamps.

        Issue 7 fix: The wall_clock_time field should be automatically populated
        by log_timeout for human-readable audit logs.
        """
        from datetime import datetime

        clear_timeout_logs()
        before = datetime.now()
        result = log_timeout(TimeoutLevel.AGENT, "agent-1", 61.0, {})
        after = datetime.now()

        # wall_clock_time should be a datetime instance
        assert isinstance(result.wall_clock_time, datetime)
        # It should be between before and after (close to current time)
        assert before <= result.wall_clock_time <= after


class TestGetTimeoutLogs:
    """Tests for get_timeout_logs function (Task 7.3)."""

    def test_get_timeout_logs_returns_all_logs(self):
        """get_timeout_logs should return all logged timeouts."""
        clear_timeout_logs()
        log_timeout(TimeoutLevel.WORKFLOW, "wf-1", 1801.0, {})
        log_timeout(TimeoutLevel.AGENT, "agent-1", 61.0, {})
        logs = get_timeout_logs()
        assert len(logs) == 2

    def test_get_timeout_logs_filter_by_level(self):
        """get_timeout_logs should filter by level."""
        clear_timeout_logs()
        log_timeout(TimeoutLevel.WORKFLOW, "wf-1", 1801.0, {})
        log_timeout(TimeoutLevel.AGENT, "agent-1", 61.0, {})
        log_timeout(TimeoutLevel.AGENT, "agent-2", 62.0, {})
        logs = get_timeout_logs(level=TimeoutLevel.AGENT)
        assert len(logs) == 2
        assert all(log.level == TimeoutLevel.AGENT for log in logs)


class TestClearTimeoutLogs:
    """Tests for clear_timeout_logs function (Task 7.4)."""

    def test_clear_timeout_logs_removes_all(self):
        """clear_timeout_logs should remove all logs."""
        log_timeout(TimeoutLevel.WORKFLOW, "wf-1", 1801.0, {})
        clear_timeout_logs()
        logs = get_timeout_logs()
        assert len(logs) == 0


# =============================================================================
# Task 8: Context Manager Tests (Integration)
# =============================================================================


class TestWorkflowTimeoutContextManager:
    """Tests for workflow_timeout context manager (Task 8.2)."""

    def test_workflow_timeout_is_context_manager(self):
        """workflow_timeout should be usable as context manager."""
        # Should not raise when within timeout
        with workflow_timeout("wf-cm-1"):
            pass  # Successful operation

    def test_workflow_timeout_allows_successful_completion(self):
        """workflow_timeout should allow code to complete successfully."""
        result = []
        with workflow_timeout("wf-cm-2"):
            result.append("completed")
        assert result == ["completed"]

    def test_workflow_timeout_cancels_on_success(self):
        """workflow_timeout should cancel timeout on successful exit."""
        manager = TimeoutManager()
        with workflow_timeout("wf-cm-3", manager=manager):
            # Timeout should be active during execution
            assert "wf-cm-3" in manager._active_timeouts
        # After exit, timeout should be cancelled
        assert "wf-cm-3" not in manager._active_timeouts

    def test_workflow_timeout_raises_on_timeout(self):
        """workflow_timeout should raise WorkflowTimeoutError on timeout."""
        manager = TimeoutManager()
        # Manually inject an expired timeout state
        state = TimeoutState(
            operation_id="wf-expired",
            level=TimeoutLevel.WORKFLOW,
            start_time=time.monotonic() - 1801,  # Expired
            timeout_seconds=1800,
        )
        manager._active_timeouts["wf-expired"] = state

        with pytest.raises(WorkflowTimeoutError):
            with workflow_timeout("wf-expired", manager=manager, check_on_entry=True):
                pass  # Should raise before this

    def test_workflow_timeout_logs_on_timeout(self):
        """workflow_timeout should log timeout when it occurs."""
        clear_timeout_logs()
        manager = TimeoutManager()
        # Inject expired state
        state = TimeoutState(
            operation_id="wf-log-test",
            level=TimeoutLevel.WORKFLOW,
            start_time=time.monotonic() - 1801,
            timeout_seconds=1800,
        )
        manager._active_timeouts["wf-log-test"] = state

        with pytest.raises(WorkflowTimeoutError):
            with workflow_timeout("wf-log-test", manager=manager, check_on_entry=True):
                pass

        logs = get_timeout_logs(level=TimeoutLevel.WORKFLOW)
        assert len(logs) >= 1
        assert logs[-1].operation_id == "wf-log-test"


class TestNestedTimeoutContextManager:
    """Tests for nested_timeout context manager (Task 8.3)."""

    def test_nested_timeout_is_context_manager(self):
        """nested_timeout should be usable as context manager."""
        with nested_timeout("nested-cm-1", "wf-parent"):
            pass  # Successful operation

    def test_nested_timeout_allows_successful_completion(self):
        """nested_timeout should allow code to complete successfully."""
        result = []
        with nested_timeout("nested-cm-2", "wf-parent"):
            result.append("completed")
        assert result == ["completed"]

    def test_nested_timeout_cancels_on_success(self):
        """nested_timeout should cancel timeout on successful exit."""
        manager = TimeoutManager()
        with nested_timeout("nested-cm-3", "wf-parent", manager=manager):
            assert "nested-cm-3" in manager._active_timeouts
        assert "nested-cm-3" not in manager._active_timeouts

    def test_nested_timeout_raises_on_timeout(self):
        """nested_timeout should raise NestedTimeoutError on timeout."""
        manager = TimeoutManager()
        # Inject expired state
        state = TimeoutState(
            operation_id="nested-expired",
            level=TimeoutLevel.NESTED,
            start_time=time.monotonic() - 301,
            timeout_seconds=300,
        )
        manager._active_timeouts["nested-expired"] = state

        with pytest.raises(NestedTimeoutError):
            with nested_timeout(
                "nested-expired", "wf-parent", manager=manager, check_on_entry=True
            ):
                pass

    def test_nested_timeout_includes_parent_id(self):
        """nested_timeout should include parent_id in error."""
        manager = TimeoutManager()
        state = TimeoutState(
            operation_id="nested-parent-test",
            level=TimeoutLevel.NESTED,
            start_time=time.monotonic() - 301,
            timeout_seconds=300,
        )
        manager._active_timeouts["nested-parent-test"] = state

        with pytest.raises(NestedTimeoutError) as exc_info:
            with nested_timeout(
                "nested-parent-test",
                "wf-parent-123",
                manager=manager,
                check_on_entry=True,
            ):
                pass
        assert exc_info.value.parent_notification["parent_id"] == "wf-parent-123"


class TestAgentTimeoutContextManager:
    """Tests for agent_timeout context manager (Task 8.4)."""

    def test_agent_timeout_is_context_manager(self):
        """agent_timeout should be usable as context manager."""
        with agent_timeout("agent-cm-1"):
            pass  # Successful operation

    def test_agent_timeout_allows_successful_completion(self):
        """agent_timeout should allow code to complete successfully."""
        result = []
        with agent_timeout("agent-cm-2"):
            result.append("completed")
        assert result == ["completed"]

    def test_agent_timeout_cancels_on_success(self):
        """agent_timeout should cancel timeout on successful exit."""
        manager = TimeoutManager()
        with agent_timeout("agent-cm-3", manager=manager):
            assert "agent-cm-3" in manager._active_timeouts
        assert "agent-cm-3" not in manager._active_timeouts

    def test_agent_timeout_raises_on_timeout(self):
        """agent_timeout should raise AgentTimeoutError on timeout."""
        manager = TimeoutManager()
        state = TimeoutState(
            operation_id="agent-expired",
            level=TimeoutLevel.AGENT,
            start_time=time.monotonic() - 61,
            timeout_seconds=60,
        )
        manager._active_timeouts["agent-expired"] = state

        with pytest.raises(AgentTimeoutError):
            with agent_timeout("agent-expired", manager=manager, check_on_entry=True):
                pass

    def test_agent_timeout_preserves_state_on_timeout(self):
        """agent_timeout should preserve state on timeout."""
        clear_preserved_state("agent-preserve-test")
        manager = TimeoutManager()
        state = TimeoutState(
            operation_id="agent-preserve-test",
            level=TimeoutLevel.AGENT,
            start_time=time.monotonic() - 61,
            timeout_seconds=60,
        )
        manager._active_timeouts["agent-preserve-test"] = state

        try:
            with agent_timeout(
                "agent-preserve-test",
                manager=manager,
                check_on_entry=True,
                state_to_preserve={"step": 5, "data": "important"},
            ):
                pass
        except AgentTimeoutError:
            pass

        preserved = get_preserved_state("agent-preserve-test")
        assert preserved is not None
        assert preserved.state_snapshot == {"step": 5, "data": "important"}


class TestContextManagerExceptionPropagation:
    """Tests for exception propagation in context managers (Issue 6 fix).

    Verifies that exceptions raised inside context managers are properly
    propagated to the caller while still ensuring the timeout is cancelled.
    """

    def test_workflow_timeout_propagates_exceptions(self):
        """workflow_timeout should propagate exceptions raised inside."""
        manager = TimeoutManager()

        with pytest.raises(ValueError, match="test error"):
            with workflow_timeout("wf-exc-1", manager=manager):
                raise ValueError("test error")

        # Timeout should be cancelled even though exception was raised
        assert not manager.has_active_timeout("wf-exc-1")

    def test_workflow_timeout_propagates_custom_exceptions(self):
        """workflow_timeout should propagate custom exception types."""
        manager = TimeoutManager()

        class CustomError(Exception):
            pass

        with pytest.raises(CustomError):
            with workflow_timeout("wf-exc-2", manager=manager):
                raise CustomError("custom error")

        assert not manager.has_active_timeout("wf-exc-2")

    def test_nested_timeout_propagates_exceptions(self):
        """nested_timeout should propagate exceptions raised inside."""
        manager = TimeoutManager()

        with pytest.raises(RuntimeError, match="nested error"):
            with nested_timeout("nested-exc-1", "wf-parent", manager=manager):
                raise RuntimeError("nested error")

        # Timeout should be cancelled even though exception was raised
        assert not manager.has_active_timeout("nested-exc-1")

    def test_nested_timeout_propagates_key_error(self):
        """nested_timeout should propagate KeyError exceptions."""
        manager = TimeoutManager()

        with pytest.raises(KeyError):
            with nested_timeout("nested-exc-2", "wf-parent", manager=manager):
                raise KeyError("missing_key")

        assert not manager.has_active_timeout("nested-exc-2")

    def test_agent_timeout_propagates_exceptions(self):
        """agent_timeout should propagate exceptions raised inside."""
        manager = TimeoutManager()

        with pytest.raises(TypeError, match="agent error"):
            with agent_timeout("agent-exc-1", manager=manager):
                raise TypeError("agent error")

        # Timeout should be cancelled even though exception was raised
        assert not manager.has_active_timeout("agent-exc-1")

    def test_agent_timeout_propagates_attribute_error(self):
        """agent_timeout should propagate AttributeError exceptions."""
        manager = TimeoutManager()

        with pytest.raises(AttributeError):
            with agent_timeout("agent-exc-2", manager=manager):
                raise AttributeError("missing_attr")

        assert not manager.has_active_timeout("agent-exc-2")

    def test_nested_context_managers_propagate_inner_exception(self):
        """Nested context managers should propagate inner exception to outer."""
        wf_manager = TimeoutManager()
        agent_manager = TimeoutManager()

        with pytest.raises(IOError, match="inner exception"):
            with workflow_timeout("wf-nested-exc", manager=wf_manager):
                with agent_timeout("agent-nested-exc", manager=agent_manager):
                    raise IOError("inner exception")

        # Both timeouts should be cancelled
        assert not wf_manager.has_active_timeout("wf-nested-exc")
        assert not agent_manager.has_active_timeout("agent-nested-exc")

    def test_exception_does_not_suppress_timeout_cleanup(self):
        """Exceptions should not prevent timeout cleanup on exit."""
        manager = TimeoutManager()

        # Start workflow
        try:
            with workflow_timeout("wf-cleanup", manager=manager):
                # Verify timeout is active
                assert manager.has_active_timeout("wf-cleanup")
                raise Exception("any error")
        except Exception:
            pass

        # Verify timeout was cleaned up despite exception
        assert not manager.has_active_timeout("wf-cleanup")


class TestTimeoutHierarchyEnforcement:
    """Tests for timeout hierarchy enforcement in practice (Task 8.6)."""

    def test_workflow_contains_nested_operations(self):
        """Workflow timeout should allow nested operations within it."""
        wf_manager = TimeoutManager()
        nested_manager = TimeoutManager()

        with workflow_timeout("wf-hierarchy-1", manager=wf_manager):
            # Start a nested operation within the workflow
            with nested_timeout(
                "nested-in-wf", "wf-hierarchy-1", manager=nested_manager
            ):
                # Both should be active
                assert "wf-hierarchy-1" in wf_manager._active_timeouts
                assert "nested-in-wf" in nested_manager._active_timeouts

        # Both should be cancelled after completion
        assert "wf-hierarchy-1" not in wf_manager._active_timeouts
        assert "nested-in-wf" not in nested_manager._active_timeouts

    def test_nested_contains_agent_operations(self):
        """Nested operation should allow agent operations within it."""
        nested_manager = TimeoutManager()
        agent_manager = TimeoutManager()

        with nested_timeout("nested-hierarchy", "wf-parent", manager=nested_manager):
            with agent_timeout("agent-in-nested", manager=agent_manager):
                assert "nested-hierarchy" in nested_manager._active_timeouts
                assert "agent-in-nested" in agent_manager._active_timeouts

        assert "nested-hierarchy" not in nested_manager._active_timeouts
        assert "agent-in-nested" not in agent_manager._active_timeouts

    def test_full_three_level_hierarchy(self):
        """Full workflow -> nested -> agent hierarchy should work."""
        wf_manager = TimeoutManager()
        nested_manager = TimeoutManager()
        agent_manager = TimeoutManager()

        with workflow_timeout("wf-full", manager=wf_manager):
            with nested_timeout("nested-full", "wf-full", manager=nested_manager):
                with agent_timeout("agent-full", manager=agent_manager):
                    # All three levels active
                    assert "wf-full" in wf_manager._active_timeouts
                    assert "nested-full" in nested_manager._active_timeouts
                    assert "agent-full" in agent_manager._active_timeouts

        # All cancelled after completion
        assert "wf-full" not in wf_manager._active_timeouts
        assert "nested-full" not in nested_manager._active_timeouts
        assert "agent-full" not in agent_manager._active_timeouts

    def test_agent_timeout_is_shortest(self):
        """Agent timeout (60s) should be shorter than nested (300s)."""
        agent_config = get_timeout_for_level(TimeoutLevel.AGENT)
        nested_config = get_timeout_for_level(TimeoutLevel.NESTED)
        assert agent_config.timeout_seconds < nested_config.timeout_seconds

    def test_nested_timeout_is_shorter_than_workflow(self):
        """Nested timeout (300s) should be shorter than workflow (1800s)."""
        nested_config = get_timeout_for_level(TimeoutLevel.NESTED)
        workflow_config = get_timeout_for_level(TimeoutLevel.WORKFLOW)
        assert nested_config.timeout_seconds < workflow_config.timeout_seconds


class TestStatePreservedOnTimeout:
    """Tests for state preservation when timeout occurs (Task 8.6)."""

    def test_workflow_timeout_preserves_state(self):
        """workflow_timeout should preserve state when provided."""
        clear_preserved_state("wf-state-test")
        manager = TimeoutManager()
        state = TimeoutState(
            operation_id="wf-state-test",
            level=TimeoutLevel.WORKFLOW,
            start_time=time.monotonic() - 1801,
            timeout_seconds=1800,
        )
        manager._active_timeouts["wf-state-test"] = state

        try:
            with workflow_timeout(
                "wf-state-test",
                manager=manager,
                check_on_entry=True,
                state_to_preserve={"step": 10, "progress": "halfway"},
            ):
                pass
        except WorkflowTimeoutError:
            pass

        preserved = get_preserved_state("wf-state-test")
        assert preserved is not None
        assert preserved.state_snapshot["step"] == 10
        assert preserved.state_snapshot["progress"] == "halfway"
        assert preserved.level == TimeoutLevel.WORKFLOW

    def test_nested_timeout_preserves_state(self):
        """nested_timeout should preserve state when provided."""
        clear_preserved_state("nested-state-test")
        manager = TimeoutManager()
        state = TimeoutState(
            operation_id="nested-state-test",
            level=TimeoutLevel.NESTED,
            start_time=time.monotonic() - 301,
            timeout_seconds=300,
        )
        manager._active_timeouts["nested-state-test"] = state

        try:
            with nested_timeout(
                "nested-state-test",
                "wf-parent",
                manager=manager,
                check_on_entry=True,
                state_to_preserve={"nested_step": 3},
            ):
                pass
        except NestedTimeoutError:
            pass

        preserved = get_preserved_state("nested-state-test")
        assert preserved is not None
        assert preserved.state_snapshot["nested_step"] == 3
        assert preserved.level == TimeoutLevel.NESTED

    def test_preserved_state_recoverable_after_timeout(self):
        """Preserved state should be recoverable for resume."""
        op_id = "recoverable-op"
        clear_preserved_state(op_id)
        manager = TimeoutManager()
        state = TimeoutState(
            operation_id=op_id,
            level=TimeoutLevel.AGENT,
            start_time=time.monotonic() - 61,
            timeout_seconds=60,
        )
        manager._active_timeouts[op_id] = state

        # Simulate timeout with state preservation
        try:
            with agent_timeout(
                op_id,
                manager=manager,
                check_on_entry=True,
                state_to_preserve={
                    "items_processed": 50,
                    "next_item_index": 51,
                    "checkpoint_id": "cp-50",
                },
            ):
                pass
        except AgentTimeoutError:
            pass

        # Verify state can be retrieved for resume
        preserved = get_preserved_state(op_id)
        assert preserved is not None
        assert preserved.state_snapshot["items_processed"] == 50
        assert preserved.state_snapshot["next_item_index"] == 51

        # Clean up for potential resume
        clear_preserved_state(op_id)
        assert get_preserved_state(op_id) is None
