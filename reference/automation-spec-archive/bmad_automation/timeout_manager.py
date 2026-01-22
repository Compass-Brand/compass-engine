"""Timeout Manager for BMAD Automation.

This module provides timeout enforcement functionality for workflow automation.

Story: 2b-9 - Timeout Enforcement
Epic: 2b - Menu Handling & Navigation

Warning:
    **Thread Safety:** This module is NOT thread-safe. The TimeoutManager class
    and module-level state (_preserved_states, _timeout_logs, _default_manager)
    use mutable shared state without synchronization. Each thread should use
    its own TimeoutManager instance. Do not share TimeoutManager instances
    across threads.

Timeout Hierarchy:
    | Level  | Timeout | Use Case                    |
    |--------|---------|-----------------------------
    | WORKFLOW | 1800s (30 min) | Full workflow execution |
    | NESTED   | 300s (5 min)   | Nested operations       |
    | AGENT    | 60s (1 min)    | Individual agent calls  |

Examples:
    >>> from pcmrp_tools.bmad_automation.timeout_manager import (
    ...     TimeoutLevel, get_timeout_for_level, TimeoutManager
    ... )
    >>> config = get_timeout_for_level(TimeoutLevel.WORKFLOW)
    >>> config.timeout_seconds
    1800

    >>> manager = TimeoutManager()
    >>> state = manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
    >>> manager.check_timeout("wf-123")
    False
    >>> manager.cancel_timeout("wf-123")
    True
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# =============================================================================
# Task 1: Timeout Configuration
# =============================================================================


class TimeoutLevel(Enum):
    """Timeout levels in the hierarchy.

    The timeout hierarchy defines three levels:
    - WORKFLOW: Top-level workflow execution (30 minutes)
    - NESTED: Nested operations within workflow (5 minutes)
    - AGENT: Individual agent calls (1 minute)
    """

    WORKFLOW = "workflow"
    NESTED = "nested"
    AGENT = "agent"


# Timeout seconds for each level (Task 1.2)
# AC #1: Workflow = 1800s (30 min)
# AC #2: Nested = 300s (5 min)
# AC #3: Agent = 60s (1 min)
TIMEOUT_SECONDS: dict[TimeoutLevel, int] = {
    TimeoutLevel.WORKFLOW: 1800,  # 30 minutes
    TimeoutLevel.NESTED: 300,     # 5 minutes
    TimeoutLevel.AGENT: 60,       # 1 minute
}


# Error types for each level
ERROR_TYPES: dict[TimeoutLevel, str] = {
    TimeoutLevel.WORKFLOW: "workflow_timeout",
    TimeoutLevel.NESTED: "nested_timeout",
    TimeoutLevel.AGENT: "agent_timeout",
}


@dataclass
class TimeoutConfig:
    """Configuration for a specific timeout level.

    Attributes:
        level: The timeout level (WORKFLOW, NESTED, or AGENT)
        timeout_seconds: Number of seconds before timeout
        error_type: The error type string for this level
    """

    level: TimeoutLevel
    timeout_seconds: int
    error_type: str


def get_timeout_for_level(level: TimeoutLevel) -> TimeoutConfig:
    """Get the timeout configuration for a specific level.

    Args:
        level: The timeout level (WORKFLOW, NESTED, or AGENT)

    Returns:
        TimeoutConfig with the level's timeout settings

    Examples:
        >>> config = get_timeout_for_level(TimeoutLevel.WORKFLOW)
        >>> config.timeout_seconds
        1800
        >>> config.error_type
        'workflow_timeout'
    """
    return TimeoutConfig(
        level=level,
        timeout_seconds=TIMEOUT_SECONDS[level],
        error_type=ERROR_TYPES[level],
    )


# =============================================================================
# Task 2: TimeoutManager Class
# =============================================================================


@dataclass
class TimeoutState:
    """State for an active timeout.

    Attributes:
        operation_id: Unique identifier for the operation
        level: The timeout level being enforced
        start_time: Monotonic time when timeout started
        timeout_seconds: Number of seconds before timeout
    """

    operation_id: str
    level: TimeoutLevel
    start_time: float
    timeout_seconds: int


class TimeoutManager:
    """Manager for tracking and enforcing timeouts.

    The TimeoutManager tracks active timeouts for operations and provides
    methods to start, check, and cancel timeouts.

    Warning:
        **Thread Safety:** This class is NOT thread-safe. Each thread should
        use its own TimeoutManager instance. Do not share instances across
        threads or use the module-level get_default_manager() in multi-threaded
        contexts.

    Examples:
        >>> manager = TimeoutManager()
        >>> state = manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
        >>> manager.check_timeout("wf-123")
        False
        >>> manager.cancel_timeout("wf-123")
        True
    """

    def __init__(self) -> None:
        """Initialize the TimeoutManager with empty active timeouts."""
        self._active_timeouts: dict[str, TimeoutState] = {}

    def start_timeout(
        self,
        level: TimeoutLevel,
        operation_id: str,
    ) -> TimeoutState:
        """Start a timeout for an operation.

        Creates a new timeout state and adds it to active timeouts.

        Note:
            If an active timeout already exists for the given operation_id,
            it will be silently overwritten with the new timeout state.
            The new timeout replaces the old one, resetting the start_time.

        Args:
            level: The timeout level (WORKFLOW, NESTED, or AGENT)
            operation_id: Unique identifier for the operation

        Returns:
            TimeoutState for the started timeout

        Examples:
            >>> manager = TimeoutManager()
            >>> state = manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
            >>> state.operation_id
            'wf-123'
        """
        state = TimeoutState(
            operation_id=operation_id,
            level=level,
            start_time=time.monotonic(),
            timeout_seconds=TIMEOUT_SECONDS[level],
        )
        self._active_timeouts[operation_id] = state
        return state

    def check_timeout(self, operation_id: str) -> bool | None:
        """Check if an operation has timed out.

        Args:
            operation_id: The operation identifier to check

        Returns:
            True if timed out, False if not, None if operation unknown

        Examples:
            >>> manager = TimeoutManager()
            >>> manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
            >>> manager.check_timeout("wf-123")
            False
            >>> manager.check_timeout("unknown")
            None
        """
        state = self._active_timeouts.get(operation_id)
        if state is None:
            return None

        elapsed = time.monotonic() - state.start_time
        return elapsed >= state.timeout_seconds

    def cancel_timeout(self, operation_id: str) -> bool:
        """Cancel an active timeout.

        Removes the operation from active timeouts.

        Args:
            operation_id: The operation identifier to cancel

        Returns:
            True if operation was active and cancelled, False if not found

        Examples:
            >>> manager = TimeoutManager()
            >>> manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
            >>> manager.cancel_timeout("wf-123")
            True
            >>> manager.cancel_timeout("wf-123")
            False
        """
        if operation_id in self._active_timeouts:
            del self._active_timeouts[operation_id]
            return True
        return False

    def has_active_timeout(self, operation_id: str) -> bool:
        """Check if an operation has an active timeout.

        This is the public interface for checking timeout existence.
        Context managers and external code should use this method instead
        of accessing _active_timeouts directly.

        Args:
            operation_id: The operation identifier to check

        Returns:
            True if the operation has an active timeout, False otherwise

        Examples:
            >>> manager = TimeoutManager()
            >>> manager.has_active_timeout("wf-123")
            False
            >>> manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
            >>> manager.has_active_timeout("wf-123")
            True
        """
        return operation_id in self._active_timeouts

    def get_active_timeout_state(self, operation_id: str) -> TimeoutState | None:
        """Get the timeout state for an active operation.

        This is the public interface for retrieving timeout state.
        Context managers and external code should use this method instead
        of accessing _active_timeouts directly.

        Args:
            operation_id: The operation identifier to look up

        Returns:
            TimeoutState if the operation has an active timeout, None otherwise

        Examples:
            >>> manager = TimeoutManager()
            >>> manager.get_active_timeout_state("wf-123")
            None
            >>> manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
            >>> state = manager.get_active_timeout_state("wf-123")
            >>> state.level
            <TimeoutLevel.WORKFLOW: 'workflow'>
        """
        return self._active_timeouts.get(operation_id)

    def get_elapsed_time(self, operation_id: str) -> float | None:
        """Get elapsed time for an operation.

        Args:
            operation_id: The operation identifier

        Returns:
            Elapsed time in seconds, or None if operation unknown

        Examples:
            >>> manager = TimeoutManager()
            >>> manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
            >>> elapsed = manager.get_elapsed_time("wf-123")
            >>> elapsed >= 0
            True
        """
        state = self._active_timeouts.get(operation_id)
        if state is None:
            return None
        return time.monotonic() - state.start_time

    def get_remaining_time(self, operation_id: str) -> float | None:
        """Get remaining time before timeout for an operation.

        Args:
            operation_id: The operation identifier

        Returns:
            Remaining time in seconds (may be negative if expired),
            or None if operation unknown

        Examples:
            >>> manager = TimeoutManager()
            >>> manager.start_timeout(TimeoutLevel.WORKFLOW, "wf-123")
            >>> remaining = manager.get_remaining_time("wf-123")
            >>> 0 < remaining <= 1800
            True
        """
        state = self._active_timeouts.get(operation_id)
        if state is None:
            return None
        elapsed = time.monotonic() - state.start_time
        return state.timeout_seconds - elapsed


# =============================================================================
# Task 3: Workflow Timeout Enforcement
# =============================================================================


class WorkflowTimeoutError(Exception):
    """Exception raised when a workflow exceeds its timeout.

    Attributes:
        timeout_error: Error type string ("workflow_timeout")
        elapsed_time: Time elapsed when timeout occurred
        operation_context: Context information about the operation
    """

    def __init__(
        self,
        message: str,
        *,
        timeout_error: str,
        elapsed_time: float,
        operation_context: dict,
    ) -> None:
        """Initialize WorkflowTimeoutError.

        Args:
            message: Error message
            timeout_error: Error type string
            elapsed_time: Time elapsed when timeout occurred
            operation_context: Context information about the operation
        """
        super().__init__(message)
        self.timeout_error = timeout_error
        self.elapsed_time = elapsed_time
        self.operation_context = operation_context


def enforce_workflow_timeout(
    workflow_id: str,
    start_time: float,
) -> None:
    """Enforce workflow timeout of 1800 seconds (30 minutes).

    Checks if elapsed time exceeds workflow timeout limit and raises
    WorkflowTimeoutError if exceeded.

    Args:
        workflow_id: Identifier for the workflow
        start_time: Monotonic start time of the workflow

    Raises:
        WorkflowTimeoutError: If workflow has exceeded 1800 seconds

    Examples:
        >>> import time
        >>> start = time.monotonic()
        >>> enforce_workflow_timeout("wf-123", start)  # OK, just started
        >>> # After 30+ minutes, would raise WorkflowTimeoutError
    """
    timeout_limit = TIMEOUT_SECONDS[TimeoutLevel.WORKFLOW]
    elapsed = time.monotonic() - start_time

    if elapsed >= timeout_limit:
        raise WorkflowTimeoutError(
            f"Workflow timed out after {elapsed:.1f} seconds "
            f"(limit: {timeout_limit} seconds)",
            timeout_error="workflow_timeout",
            elapsed_time=elapsed,
            operation_context={
                "workflow_id": workflow_id,
                "timeout_limit_seconds": timeout_limit,
            },
        )


# =============================================================================
# Task 4: Nested Operation Timeout Enforcement
# =============================================================================


class NestedTimeoutError(Exception):
    """Exception raised when a nested operation exceeds its timeout.

    Attributes:
        timeout_error: Error type string ("nested_timeout")
        elapsed_time: Time elapsed when timeout occurred
        nested_operation_context: Context about the nested operation
        parent_notification: Notification data for parent workflow
    """

    def __init__(
        self,
        message: str,
        *,
        timeout_error: str,
        elapsed_time: float,
        nested_operation_context: dict,
        parent_notification: dict,
    ) -> None:
        """Initialize NestedTimeoutError.

        Args:
            message: Error message
            timeout_error: Error type string
            elapsed_time: Time elapsed when timeout occurred
            nested_operation_context: Context about the nested operation
            parent_notification: Notification data for parent workflow
        """
        super().__init__(message)
        self.timeout_error = timeout_error
        self.elapsed_time = elapsed_time
        self.nested_operation_context = nested_operation_context
        self.parent_notification = parent_notification


def enforce_nested_timeout(
    operation_id: str,
    parent_id: str,
    start_time: float,
) -> None:
    """Enforce nested operation timeout of 300 seconds (5 minutes).

    Checks if elapsed time exceeds nested timeout limit and raises
    NestedTimeoutError if exceeded. The error includes parent notification
    data for the parent workflow.

    Args:
        operation_id: Identifier for the nested operation
        parent_id: Identifier for the parent workflow
        start_time: Monotonic start time of the operation

    Raises:
        NestedTimeoutError: If operation has exceeded 300 seconds

    Examples:
        >>> import time
        >>> start = time.monotonic()
        >>> enforce_nested_timeout("op-123", "wf-parent", start)  # OK
        >>> # After 5+ minutes, would raise NestedTimeoutError
    """
    timeout_limit = TIMEOUT_SECONDS[TimeoutLevel.NESTED]
    elapsed = time.monotonic() - start_time

    if elapsed >= timeout_limit:
        raise NestedTimeoutError(
            f"Nested operation timed out after {elapsed:.1f} seconds "
            f"(limit: {timeout_limit} seconds)",
            timeout_error="nested_timeout",
            elapsed_time=elapsed,
            nested_operation_context={
                "operation_id": operation_id,
                "timeout_limit_seconds": timeout_limit,
            },
            parent_notification={
                "parent_id": parent_id,
                "child_operation_id": operation_id,
                "child_timed_out": True,
            },
        )


# =============================================================================
# Task 5: Agent Timeout Enforcement
# =============================================================================


class AgentTimeoutError(Exception):
    """Exception raised when an agent exceeds its timeout (60 seconds).

    Attributes:
        timeout_error: Error type string ("agent_timeout")
        agent_id: Identifier for the agent that timed out
        elapsed_time: Time elapsed when timeout occurred
        agent_context: Context information about the agent state
        last_activity: Timestamp of last agent activity
    """

    def __init__(
        self,
        message: str,
        *,
        timeout_error: str,
        agent_id: str,
        elapsed_time: float | None = None,
        agent_context: dict | None = None,
        last_activity: float | None = None,
    ) -> None:
        """Initialize AgentTimeoutError.

        Args:
            message: Error message
            timeout_error: Error type string
            agent_id: Identifier for the agent
            elapsed_time: Time elapsed when timeout occurred
            agent_context: Context information about the agent state
            last_activity: Timestamp of last agent activity
        """
        super().__init__(message)
        self.timeout_error = timeout_error
        self.agent_id = agent_id
        self.elapsed_time = elapsed_time
        self.agent_context = agent_context
        self.last_activity = last_activity


def enforce_agent_timeout(
    agent_id: str,
    start_time: float,
    *,
    context: dict | None = None,
    last_activity: float | None = None,
) -> None:
    """Enforce agent timeout of 60 seconds (1 minute).

    Checks if elapsed time exceeds agent timeout limit and raises
    AgentTimeoutError if exceeded.

    Args:
        agent_id: Identifier for the agent
        start_time: Monotonic start time of the agent execution
        context: Optional context information about the agent state
        last_activity: Optional timestamp of last agent activity

    Returns:
        None if within timeout limit

    Raises:
        AgentTimeoutError: If agent has exceeded 60 seconds
    """
    timeout_limit = TIMEOUT_SECONDS[TimeoutLevel.AGENT]
    elapsed = time.monotonic() - start_time

    if elapsed >= timeout_limit:
        raise AgentTimeoutError(
            f"Agent timed out after {elapsed:.1f} seconds "
            f"(limit: {timeout_limit} seconds)",
            timeout_error="agent_timeout",
            agent_id=agent_id,
            elapsed_time=elapsed,
            agent_context=context,
            last_activity=last_activity,
        )
    return None


# =============================================================================
# Task 6: State Preservation on Timeout
# =============================================================================


@dataclass
class PreservedTimeoutState:
    """State preserved when a timeout occurs for potential recovery.

    Attributes:
        operation_id: Unique identifier for the operation
        state_snapshot: Snapshot of the operation state at timeout
        timestamp: When the state was preserved
        level: The timeout level that triggered preservation
        checkpoint: Optional checkpoint identifier for resume
    """

    operation_id: str
    state_snapshot: dict
    timestamp: float
    level: TimeoutLevel
    checkpoint: str | None = None


# In-memory storage for preserved states (Task 6.3)
_preserved_states: dict[str, PreservedTimeoutState] = {}


def preserve_state_on_timeout(
    operation_id: str,
    state: dict,
    *,
    level: TimeoutLevel = TimeoutLevel.AGENT,
    checkpoint: str | None = None,
) -> PreservedTimeoutState:
    """Preserve operation state when a timeout occurs.

    Saves the current state to recoverable storage for potential resume.

    Args:
        operation_id: Unique identifier for the operation
        state: State snapshot to preserve
        level: The timeout level (defaults to AGENT)
        checkpoint: Optional checkpoint identifier for resume

    Returns:
        PreservedTimeoutState with the preserved data
    """
    preserved = PreservedTimeoutState(
        operation_id=operation_id,
        state_snapshot=state,
        timestamp=time.monotonic(),
        level=level,
        checkpoint=checkpoint,
    )
    _preserved_states[operation_id] = preserved
    return preserved


def get_preserved_state(operation_id: str) -> PreservedTimeoutState | None:
    """Retrieve a preserved timeout state.

    Args:
        operation_id: The operation identifier to retrieve

    Returns:
        PreservedTimeoutState if found, None otherwise
    """
    return _preserved_states.get(operation_id)


def clear_preserved_state(operation_id: str) -> None:
    """Clear a preserved timeout state.

    Removes the preserved state for the given operation.

    Args:
        operation_id: The operation identifier to clear
    """
    _preserved_states.pop(operation_id, None)


# =============================================================================
# Task 7: Timeout Logging
# =============================================================================


@dataclass
class TimeoutLog:
    """Log entry for a timeout event.

    Attributes:
        level: The timeout level that triggered
        operation_id: Identifier for the operation that timed out
        elapsed_time: Time elapsed when timeout occurred
        context: Context information about the operation
        error_type: The error type string for this timeout
        timestamp: Monotonic time when the timeout was logged (for elapsed calculations)
        wall_clock_time: Wall clock datetime when timeout occurred (for human-readable logs)

    Note:
        Issue 7 fix: The timestamp field uses monotonic time which is ideal for
        calculating elapsed durations but hard to read in audit logs. The
        wall_clock_time field provides a human-readable datetime for audit purposes.
    """

    level: TimeoutLevel
    operation_id: str
    elapsed_time: float
    context: dict
    error_type: str
    timestamp: float
    wall_clock_time: datetime


# In-memory audit trail for timeout logs (Task 7.4)
_timeout_logs: list[TimeoutLog] = []


def log_timeout(
    level: TimeoutLevel,
    operation_id: str,
    elapsed: float,
    context: dict,
) -> TimeoutLog:
    """Log a timeout event to the audit trail.

    Creates a TimeoutLog entry with automatically determined error_type
    based on the level. Also captures wall clock time for human-readable
    audit logs.

    Args:
        level: The timeout level (WORKFLOW, NESTED, or AGENT)
        operation_id: Identifier for the operation that timed out
        elapsed: Time elapsed when timeout occurred
        context: Context information about the operation

    Returns:
        TimeoutLog entry that was created and stored

    Note:
        Issue 7 fix: Both monotonic timestamp (for elapsed calculations) and
        wall_clock_time (for human-readable logs) are recorded.
    """
    log_entry = TimeoutLog(
        level=level,
        operation_id=operation_id,
        elapsed_time=elapsed,
        context=context,
        error_type=ERROR_TYPES[level],
        timestamp=time.monotonic(),
        wall_clock_time=datetime.now(),
    )
    _timeout_logs.append(log_entry)
    return log_entry


def get_timeout_logs(
    *,
    level: TimeoutLevel | None = None,
) -> list[TimeoutLog]:
    """Retrieve timeout logs from the audit trail.

    Args:
        level: Optional filter by timeout level

    Returns:
        List of TimeoutLog entries, optionally filtered by level
    """
    if level is None:
        return list(_timeout_logs)
    return [log for log in _timeout_logs if log.level == level]


def clear_timeout_logs() -> None:
    """Clear all timeout logs from the audit trail."""
    _timeout_logs.clear()


# =============================================================================
# Task 8: Context Managers for Timeout Wrapping
# =============================================================================


# Global default manager for context managers
_default_manager: TimeoutManager | None = None


def get_default_manager() -> TimeoutManager:
    """Get or create the default TimeoutManager instance."""
    global _default_manager
    if _default_manager is None:
        _default_manager = TimeoutManager()
    return _default_manager


class workflow_timeout:
    """Context manager for workflow timeout wrapping.

    Wraps workflow execution with a 1800-second (30-minute) timeout.
    Starts timeout on entry, cancels on successful exit, and logs/preserves
    state on timeout.

    Important:
        **Timeout Enforcement Limitation:** The timeout is only checked on
        context entry (if check_on_entry=True) and exit, NOT during execution.
        For long-running operations inside the context, you must periodically
        call manager.check_timeout(operation_id) to enforce the timeout.
        This context manager does not interrupt running code.

    Args:
        workflow_id: Unique identifier for the workflow
        manager: Optional TimeoutManager instance (uses default if not provided)
        check_on_entry: If True, checks for timeout immediately on entry
        state_to_preserve: Optional state to preserve if timeout occurs

    Examples:
        >>> with workflow_timeout("wf-123"):
        ...     # Workflow code here
        ...     pass
    """

    def __init__(
        self,
        workflow_id: str,
        *,
        manager: TimeoutManager | None = None,
        check_on_entry: bool = False,
        state_to_preserve: dict | None = None,
    ) -> None:
        """Initialize workflow_timeout context manager."""
        self.workflow_id = workflow_id
        self.manager = manager or get_default_manager()
        self.check_on_entry = check_on_entry
        self.state_to_preserve = state_to_preserve
        self._start_time: float | None = None

    def __enter__(self) -> "workflow_timeout":
        """Enter the context manager, starting the timeout."""
        # Check if we're re-entering with an existing timeout
        # Uses public API (has_active_timeout, get_active_timeout_state) per Issue 3 fix
        if self.manager.has_active_timeout(self.workflow_id):
            if self.check_on_entry:
                state = self.manager.get_active_timeout_state(self.workflow_id)
                if state is not None:
                    elapsed = time.monotonic() - state.start_time
                    if elapsed >= state.timeout_seconds:
                        # Preserve state if provided
                        if self.state_to_preserve:
                            preserve_state_on_timeout(
                                self.workflow_id,
                                self.state_to_preserve,
                                level=TimeoutLevel.WORKFLOW,
                            )
                        # Log the timeout
                        log_timeout(
                            TimeoutLevel.WORKFLOW,
                            self.workflow_id,
                            elapsed,
                            {"workflow_id": self.workflow_id},
                        )
                        # Cancel the timeout state
                        self.manager.cancel_timeout(self.workflow_id)
                        raise WorkflowTimeoutError(
                            f"Workflow timed out after {elapsed:.1f} seconds "
                            f"(limit: {state.timeout_seconds} seconds)",
                            timeout_error="workflow_timeout",
                            elapsed_time=elapsed,
                            operation_context={
                                "workflow_id": self.workflow_id,
                                "timeout_limit_seconds": state.timeout_seconds,
                            },
                        )
        else:
            # Start a new timeout
            state = self.manager.start_timeout(TimeoutLevel.WORKFLOW, self.workflow_id)
            self._start_time = state.start_time
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit the context manager, cancelling the timeout on success."""
        # Cancel the timeout regardless of exception
        self.manager.cancel_timeout(self.workflow_id)
        # Don't suppress exceptions
        return False


class nested_timeout:
    """Context manager for nested operation timeout wrapping.

    Wraps nested operations with a 300-second (5-minute) timeout.
    Starts timeout on entry, cancels on successful exit, and logs/preserves
    state on timeout. Includes parent notification in timeout errors.

    Important:
        **Timeout Enforcement Limitation:** The timeout is only checked on
        context entry (if check_on_entry=True) and exit, NOT during execution.
        For long-running operations inside the context, you must periodically
        call manager.check_timeout(operation_id) to enforce the timeout.
        This context manager does not interrupt running code.

    Args:
        operation_id: Unique identifier for the nested operation
        parent_id: Identifier for the parent workflow
        manager: Optional TimeoutManager instance (uses default if not provided)
        check_on_entry: If True, checks for timeout immediately on entry
        state_to_preserve: Optional state to preserve if timeout occurs

    Examples:
        >>> with nested_timeout("op-123", "wf-parent"):
        ...     # Nested operation code here
        ...     pass
    """

    def __init__(
        self,
        operation_id: str,
        parent_id: str,
        *,
        manager: TimeoutManager | None = None,
        check_on_entry: bool = False,
        state_to_preserve: dict | None = None,
    ) -> None:
        """Initialize nested_timeout context manager."""
        self.operation_id = operation_id
        self.parent_id = parent_id
        self.manager = manager or get_default_manager()
        self.check_on_entry = check_on_entry
        self.state_to_preserve = state_to_preserve
        self._start_time: float | None = None

    def __enter__(self) -> "nested_timeout":
        """Enter the context manager, starting the timeout."""
        # Check if we're re-entering with an existing timeout
        # Uses public API (has_active_timeout, get_active_timeout_state) per Issue 3 fix
        if self.manager.has_active_timeout(self.operation_id):
            if self.check_on_entry:
                state = self.manager.get_active_timeout_state(self.operation_id)
                if state is not None:
                    elapsed = time.monotonic() - state.start_time
                    if elapsed >= state.timeout_seconds:
                        # Preserve state if provided
                        if self.state_to_preserve:
                            preserve_state_on_timeout(
                                self.operation_id,
                                self.state_to_preserve,
                                level=TimeoutLevel.NESTED,
                            )
                        # Log the timeout
                        log_timeout(
                            TimeoutLevel.NESTED,
                            self.operation_id,
                            elapsed,
                            {"operation_id": self.operation_id},
                        )
                        # Cancel the timeout state
                        self.manager.cancel_timeout(self.operation_id)
                        raise NestedTimeoutError(
                            f"Nested operation timed out after {elapsed:.1f} seconds "
                            f"(limit: {state.timeout_seconds} seconds)",
                            timeout_error="nested_timeout",
                            elapsed_time=elapsed,
                            nested_operation_context={
                                "operation_id": self.operation_id,
                                "timeout_limit_seconds": state.timeout_seconds,
                            },
                            parent_notification={
                                "parent_id": self.parent_id,
                                "child_operation_id": self.operation_id,
                                "child_timed_out": True,
                            },
                        )
        else:
            # Start a new timeout
            state = self.manager.start_timeout(TimeoutLevel.NESTED, self.operation_id)
            self._start_time = state.start_time
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit the context manager, cancelling the timeout on success."""
        # Cancel the timeout regardless of exception
        self.manager.cancel_timeout(self.operation_id)
        # Don't suppress exceptions
        return False


class agent_timeout:
    """Context manager for agent timeout wrapping.

    Wraps agent execution with a 60-second (1-minute) timeout.
    Starts timeout on entry, cancels on successful exit, and logs/preserves
    state on timeout.

    Important:
        **Timeout Enforcement Limitation:** The timeout is only checked on
        context entry (if check_on_entry=True) and exit, NOT during execution.
        For long-running operations inside the context, you must periodically
        call manager.check_timeout(operation_id) to enforce the timeout.
        This context manager does not interrupt running code.

    Args:
        agent_id: Unique identifier for the agent
        manager: Optional TimeoutManager instance (uses default if not provided)
        check_on_entry: If True, checks for timeout immediately on entry
        state_to_preserve: Optional state to preserve if timeout occurs

    Examples:
        >>> with agent_timeout("agent-123"):
        ...     # Agent code here
        ...     pass
    """

    def __init__(
        self,
        agent_id: str,
        *,
        manager: TimeoutManager | None = None,
        check_on_entry: bool = False,
        state_to_preserve: dict | None = None,
    ) -> None:
        """Initialize agent_timeout context manager."""
        self.agent_id = agent_id
        self.manager = manager or get_default_manager()
        self.check_on_entry = check_on_entry
        self.state_to_preserve = state_to_preserve
        self._start_time: float | None = None

    def __enter__(self) -> "agent_timeout":
        """Enter the context manager, starting the timeout."""
        # Check if we're re-entering with an existing timeout
        # Uses public API (has_active_timeout, get_active_timeout_state) per Issue 3 fix
        if self.manager.has_active_timeout(self.agent_id):
            if self.check_on_entry:
                state = self.manager.get_active_timeout_state(self.agent_id)
                if state is not None:
                    elapsed = time.monotonic() - state.start_time
                    if elapsed >= state.timeout_seconds:
                        # Preserve state if provided
                        if self.state_to_preserve:
                            preserve_state_on_timeout(
                                self.agent_id,
                                self.state_to_preserve,
                                level=TimeoutLevel.AGENT,
                            )
                        # Log the timeout
                        log_timeout(
                            TimeoutLevel.AGENT,
                            self.agent_id,
                            elapsed,
                            {"agent_id": self.agent_id},
                        )
                        # Cancel the timeout state
                        self.manager.cancel_timeout(self.agent_id)
                        raise AgentTimeoutError(
                            f"Agent timed out after {elapsed:.1f} seconds "
                            f"(limit: {state.timeout_seconds} seconds)",
                            timeout_error="agent_timeout",
                            agent_id=self.agent_id,
                            elapsed_time=elapsed,
                            agent_context=None,
                            last_activity=None,
                        )
        else:
            # Start a new timeout
            state = self.manager.start_timeout(TimeoutLevel.AGENT, self.agent_id)
            self._start_time = state.start_time
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit the context manager, cancelling the timeout on success."""
        # Cancel the timeout regardless of exception
        self.manager.cancel_timeout(self.agent_id)
        # Don't suppress exceptions
        return False
