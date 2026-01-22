"""Memory degradation handling for BMAD Automation.

Story 4-3: Graceful Degradation When Memory Unavailable

This module provides graceful degradation when the Forgetful MCP
memory system is unavailable, allowing the BMAD automation to
continue operating in a reduced capacity.

Tasks:
- Task 1: MemoryAvailabilityChecker (MemoryStatus, AvailabilityResult, check intervals)
- Task 2: MemorySaveQueue (QueuedMemory, queue operations, file persistence)
- Task 3: Degraded query behavior (DegradedQueryResult, query_with_fallback)
- Task 4: User notification (DEGRADED_MODE_NOTIFICATION, NotificationManager, SessionContext)
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


logger = logging.getLogger(__name__)


# =============================================================================
# Task 1 Constants
# =============================================================================

INITIAL_CHECK_INTERVAL_SECONDS = 300  # 5 minutes
EXTENDED_CHECK_INTERVAL_SECONDS = 1800  # 30 minutes
MAX_INITIAL_CHECKS = 6
MAX_RETRY_ATTEMPTS = 3
RETRY_INTERVAL_MS = 100

# =============================================================================
# Task 2 Constants
# =============================================================================

MAX_QUEUE_SIZE = 100


# =============================================================================
# Task 1: MemoryStatus Enum
# =============================================================================


class MemoryStatus(Enum):
    """Enhanced status of memory system availability.

    AVAILABLE: Memory system is fully operational
    DEGRADED: Memory system is temporarily unavailable (timeout, temporary issues)
    PERMANENTLY_UNAVAILABLE: Memory system is permanently unavailable
    """

    AVAILABLE = "available"
    DEGRADED = "degraded"
    PERMANENTLY_UNAVAILABLE = "permanently_unavailable"


# =============================================================================
# Task 1: AvailabilityResult Dataclass
# =============================================================================


@dataclass
class AvailabilityResult:
    """Result of an availability check with timing information.

    Attributes:
        status: The current memory system status
        reason: Description of why this status was determined
        last_check: When the check was performed
        next_check_at: When the next check should be performed
        check_count: Total number of checks performed
    """

    status: MemoryStatus
    reason: str
    last_check: datetime
    next_check_at: datetime
    check_count: int


# =============================================================================
# Task 2: QueuedMemory Dataclass
# =============================================================================


@dataclass
class QueuedMemory:
    """A memory item queued for later saving.

    Attributes:
        memory_data: The memory data to be saved
        timestamp: When the memory was queued
        retries: Number of save attempts made
    """

    memory_data: Dict[str, Any]
    timestamp: datetime
    retries: int = 0


# =============================================================================
# Task 2: MemorySaveQueue Class
# =============================================================================


class MemorySaveQueue:
    """Queue for storing memories when Forgetful MCP is unavailable.

    Provides FIFO queue with overflow handling, file persistence,
    and session recovery support.
    """

    def __init__(self) -> None:
        """Initialize an empty memory save queue."""
        self._queue: list[QueuedMemory] = []

    async def process_queued_saves(
        self, save_client: Callable[..., Any]
    ) -> dict[str, int]:
        """Process all queued saves with retry logic.

        Iterates through the queue, attempting to save each item.
        Failed items are retried up to MAX_RETRY_ATTEMPTS times.
        Successfully saved items are removed from the queue.

        Args:
            save_client: Async callable that saves memory data

        Returns:
            Dictionary with counts:
            - successful: Number of successfully saved items
            - failed: Number of items that failed after all retries
            - total: Total number of items attempted
        """
        successful = 0
        failed = 0
        total = len(self._queue)

        # Process items, keeping track of which ones to keep
        items_to_keep: list[QueuedMemory] = []

        for item in self._queue:
            saved = False

            # Try up to MAX_RETRY_ATTEMPTS times
            for attempt in range(MAX_RETRY_ATTEMPTS - item.retries):
                try:
                    await save_client(item.memory_data)
                    saved = True
                    successful += 1
                    break
                except Exception as e:
                    item.retries += 1
                    logger.debug(
                        f"Save attempt {item.retries} failed for queued memory: {e}"
                    )
                    continue

            if not saved:
                # Keep failed items in queue
                items_to_keep.append(item)
                if item.retries >= MAX_RETRY_ATTEMPTS:
                    failed += 1

        # Update queue with only failed items
        self._queue = items_to_keep

        return {
            "successful": successful,
            "failed": failed,
            "total": total,
        }

    def add_to_queue(self, memory_data: Dict[str, Any]) -> None:
        """Add memory data to the queue.

        Uses FIFO overflow handling - if queue is at MAX_QUEUE_SIZE,
        the oldest item is dropped.

        Args:
            memory_data: The memory data to queue for later saving
        """
        queued = QueuedMemory(
            memory_data=memory_data,
            timestamp=datetime.now(),
            retries=0,
        )
        self._queue.append(queued)

        # FIFO overflow handling
        while len(self._queue) > MAX_QUEUE_SIZE:
            self._queue.pop(0)

    def get_queue(self) -> List[QueuedMemory]:
        """Get a copy of the current queue.

        Returns:
            A copy of the queue contents
        """
        return list(self._queue)

    def clear_queue(self) -> None:
        """Clear all items from the queue."""
        self._queue.clear()

    def persist_to_file(self, path: Path) -> None:
        """Save the queue to a file for session recovery.

        Args:
            path: Path to the queue file
        """
        data = [
            {
                "memory_data": item.memory_data,
                "timestamp": item.timestamp.isoformat(),
                "retries": item.retries,
            }
            for item in self._queue
        ]
        with open(path, "w") as f:
            json.dump(data, f)

    def load_from_file(self, path: Path) -> None:
        """Load the queue from a file for session recovery.

        Handles missing files, corrupt files, and missing fields gracefully.

        Args:
            path: Path to the queue file
        """
        self._queue.clear()

        if not path.exists():
            return

        try:
            with open(path, "r") as f:
                content = f.read()
                if not content.strip():
                    return
                data = json.loads(content)

            for item in data:
                memory_data = item.get("memory_data", {})
                timestamp_str = item.get("timestamp")
                retries = item.get("retries", 0)

                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                else:
                    timestamp = datetime.now()

                queued = QueuedMemory(
                    memory_data=memory_data,
                    timestamp=timestamp,
                    retries=retries,
                )
                self._queue.append(queued)

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupt file - return empty queue
            self._queue.clear()


# =============================================================================
# Task 1-2: Base Availability Checking
# =============================================================================

class MemoryAvailabilityStatus(Enum):
    """Status of memory system availability.

    AVAILABLE: Memory system is fully operational
    DEGRADED: Memory system is temporarily unavailable (timeout, temporary issues)
    UNAVAILABLE: Memory system is permanently unavailable (connection failure)
    """

    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class MemoryAvailabilityChecker:
    """Checks the availability of the Forgetful MCP memory system.

    This class provides methods to check whether the memory system
    is available and operational, with support for async operations,
    retry logic, and check interval management.
    """

    def __init__(self) -> None:
        """Initialize the availability checker."""
        self._check_count: int = 0

    def check_availability(self, client: Any) -> MemoryAvailabilityStatus:
        """Check the availability of the memory system (sync).

        Args:
            client: The Forgetful MCP client to check

        Returns:
            MemoryAvailabilityStatus indicating the current state
        """
        try:
            # Attempt a simple operation to check connectivity
            client.execute_forgetful_tool("get_current_user", {})
            return MemoryAvailabilityStatus.AVAILABLE
        except TimeoutError:
            logger.warning("Memory system check timed out - operating in degraded mode")
            return MemoryAvailabilityStatus.DEGRADED
        except ConnectionError:
            logger.error("Memory system connection failed - system unavailable")
            return MemoryAvailabilityStatus.UNAVAILABLE
        except Exception as e:
            logger.warning(f"Memory system check failed with unexpected error: {e}")
            return MemoryAvailabilityStatus.DEGRADED

    async def check_availability_async(
        self, client: Callable[..., Any]
    ) -> AvailabilityResult:
        """Check the availability of the memory system asynchronously.

        Implements retry logic up to MAX_RETRY_ATTEMPTS times before
        returning a degraded status.

        Args:
            client: An async callable that performs the availability check

        Returns:
            AvailabilityResult with status, timing, and check count
        """
        self._check_count += 1
        last_error: Optional[Exception] = None

        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                await client()
                now = datetime.now()
                return AvailabilityResult(
                    status=MemoryStatus.AVAILABLE,
                    reason="Memory system available",
                    last_check=now,
                    next_check_at=self.get_next_check_time(self._check_count),
                    check_count=self._check_count,
                )
            except (TimeoutError, ConnectionError) as e:
                last_error = e
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(RETRY_INTERVAL_MS / 1000)
                continue
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(RETRY_INTERVAL_MS / 1000)
                continue

        # All retries exhausted
        now = datetime.now()
        reason = str(last_error) if last_error else "Unknown error"
        return AvailabilityResult(
            status=MemoryStatus.DEGRADED,
            reason=reason,
            last_check=now,
            next_check_at=self.get_next_check_time(self._check_count),
            check_count=self._check_count,
        )

    def get_next_check_time(self, check_count: int) -> datetime:
        """Calculate the next check time based on check count.

        Uses INITIAL_CHECK_INTERVAL for the first MAX_INITIAL_CHECKS checks,
        then switches to EXTENDED_CHECK_INTERVAL.

        Args:
            check_count: The current number of checks performed

        Returns:
            datetime when the next check should be performed
        """
        if check_count <= MAX_INITIAL_CHECKS:
            interval = INITIAL_CHECK_INTERVAL_SECONDS
        else:
            interval = EXTENDED_CHECK_INTERVAL_SECONDS

        return datetime.now() + timedelta(seconds=interval)

    def should_check_now(
        self, last_check: Optional[datetime], status: MemoryStatus
    ) -> bool:
        """Determine if an availability check should be performed now.

        Args:
            last_check: When the last check was performed (None if never)
            status: The current memory status

        Returns:
            True if a check should be performed, False otherwise
        """
        if last_check is None:
            return True

        # Use initial interval for timing check
        interval = timedelta(seconds=INITIAL_CHECK_INTERVAL_SECONDS)
        return datetime.now() - last_check >= interval


# =============================================================================
# Task 3: Degraded Query Behavior
# =============================================================================

@dataclass
class DegradedQueryResult:
    """Result returned when memory queries cannot be executed.

    This dataclass is returned instead of actual query results when
    the Forgetful MCP system is unavailable or degraded.

    Attributes:
        results: Empty list (no results available in degraded mode)
        status: Always "degraded" to indicate reduced functionality
        reason: Description of why the query couldn't be executed
    """

    results: List[Any] = field(default_factory=list)
    status: str = "degraded"
    reason: str = "forgetful_unavailable"


def query_with_fallback(
    forgetful_client: Any,
    query: str,
    availability_checker: "MemoryAvailabilityChecker",
) -> Union[Any, DegradedQueryResult]:
    """Execute a memory query with fallback to degraded mode.

    This function checks memory availability before executing a query.
    If the memory system is unavailable or degraded, it returns a
    DegradedQueryResult instead of failing.

    Args:
        forgetful_client: The Forgetful MCP client
        query: The query string to execute
        availability_checker: Checker to verify memory availability

    Returns:
        Query results if available, or DegradedQueryResult if degraded
    """
    # Check availability first
    status = availability_checker.check_availability(forgetful_client)

    if status != MemoryAvailabilityStatus.AVAILABLE:
        logger.warning(
            f"Memory system in degraded mode (status={status.value}). "
            f"Query will not be executed."
        )
        logger.debug(f"Degraded query skipped: {query}")
        return DegradedQueryResult()

    # Memory is available, attempt the query
    try:
        result = forgetful_client.execute_forgetful_tool(
            "query_memory",
            {"query": query, "query_context": "BMAD automation query"},
        )
        return result
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        logger.debug(f"Failed query: {query}")
        return DegradedQueryResult(
            reason=f"query_failed: {type(e).__name__}"
        )


# =============================================================================
# Task 4: User Notification
# =============================================================================

DEGRADED_MODE_NOTIFICATION = (
    "Memory system unavailable. Patterns from previous sessions won't be loaded, "
    "and new patterns won't be saved until reconnection."
)
"""Notification message displayed to users when operating in degraded mode.

This message is shown once per session to inform users that the memory
system is unavailable and functionality is reduced.
"""


class NotificationManager:
    """Manages user notifications for degraded mode with deduplication.

    This class ensures that users are only notified once per session
    about degraded mode status, avoiding notification spam.

    Attributes:
        _notified: Internal flag tracking if user has been notified
    """

    def __init__(self) -> None:
        """Initialize the notification manager."""
        self._notified: bool = False

    @property
    def has_been_notified(self) -> bool:
        """Check if the user has already been notified.

        Returns:
            True if user has been notified, False otherwise
        """
        return self._notified

    def notify_user_once(self) -> Optional[str]:
        """Notify the user about degraded mode exactly once.

        This method returns the degraded mode notification message
        on the first call, and None on all subsequent calls. This
        ensures users are informed but not spammed with notifications.

        Returns:
            DEGRADED_MODE_NOTIFICATION on first call, None thereafter
        """
        if not self._notified:
            self._notified = True
            return DEGRADED_MODE_NOTIFICATION
        return None

    def reset(self) -> None:
        """Reset the notification state.

        This allows the notification to be shown again, which may be
        useful when starting a new logical session or after recovery.
        """
        self._notified = False


class SessionContext:
    """Session context tracking degraded mode state and notifications.

    This class maintains session-level state for memory degradation,
    including notification management and degraded mode tracking.

    Attributes:
        notification_manager: Manager for user notifications
        _is_degraded_mode: Flag indicating if system is in degraded mode
    """

    def __init__(self) -> None:
        """Initialize the session context."""
        self.notification_manager = NotificationManager()
        self._is_degraded_mode: bool = False

    @property
    def is_degraded_mode(self) -> bool:
        """Check if the system is currently in degraded mode.

        Returns:
            True if in degraded mode, False otherwise
        """
        return self._is_degraded_mode

    def set_degraded_mode(self, degraded: bool) -> None:
        """Set the degraded mode state.

        Args:
            degraded: True to enter degraded mode, False to exit
        """
        self._is_degraded_mode = degraded
        if degraded:
            logger.info("Session entered degraded mode")
        else:
            logger.info("Session exited degraded mode")
