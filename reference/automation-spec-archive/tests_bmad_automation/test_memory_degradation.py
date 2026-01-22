"""Tests for memory degradation handling.

Story 4-3: Graceful Degradation When Memory Unavailable

This module tests the memory degradation functionality that allows
the BMAD automation system to operate in a degraded mode when
Forgetful MCP is unavailable.

Tasks covered:
- Task 1: MemoryAvailabilityChecker (MemoryStatus, AvailabilityResult, check intervals)
- Task 2: MemorySaveQueue (QueuedMemory, queue operations, file persistence)
- Task 3: Degraded query behavior
- Task 4: User notification
"""

import json
import tempfile
from dataclasses import dataclass, is_dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import logging


# =============================================================================
# Task 1-2 Tests: Base Structure (Group A would implement these)
# =============================================================================

class TestMemoryAvailabilityStatus:
    """Tests for MemoryAvailabilityStatus enum."""

    def test_status_has_available_value(self):
        """MemoryAvailabilityStatus should have AVAILABLE status."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemoryAvailabilityStatus
        assert MemoryAvailabilityStatus.AVAILABLE.value == "available"

    def test_status_has_degraded_value(self):
        """MemoryAvailabilityStatus should have DEGRADED status."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemoryAvailabilityStatus
        assert MemoryAvailabilityStatus.DEGRADED.value == "degraded"

    def test_status_has_unavailable_value(self):
        """MemoryAvailabilityStatus should have UNAVAILABLE status."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemoryAvailabilityStatus
        assert MemoryAvailabilityStatus.UNAVAILABLE.value == "unavailable"


class TestMemoryAvailabilityChecker:
    """Tests for MemoryAvailabilityChecker class."""

    def test_checker_can_be_instantiated(self):
        """MemoryAvailabilityChecker should be instantiable."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemoryAvailabilityChecker
        checker = MemoryAvailabilityChecker()
        assert checker is not None

    def test_check_availability_returns_status(self):
        """check_availability should return a MemoryAvailabilityStatus."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )
        checker = MemoryAvailabilityChecker()
        mock_client = Mock()
        mock_client.execute_forgetful_tool = Mock(return_value={"status": "ok"})

        status = checker.check_availability(mock_client)
        assert isinstance(status, MemoryAvailabilityStatus)

    def test_check_availability_returns_available_on_success(self):
        """check_availability should return AVAILABLE when client responds."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )
        checker = MemoryAvailabilityChecker()
        mock_client = Mock()
        mock_client.execute_forgetful_tool = Mock(return_value={"status": "ok"})

        status = checker.check_availability(mock_client)
        assert status == MemoryAvailabilityStatus.AVAILABLE

    def test_check_availability_returns_degraded_on_timeout(self):
        """check_availability should return DEGRADED on timeout."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )
        checker = MemoryAvailabilityChecker()
        mock_client = Mock()
        mock_client.execute_forgetful_tool = Mock(side_effect=TimeoutError("Connection timeout"))

        status = checker.check_availability(mock_client)
        assert status == MemoryAvailabilityStatus.DEGRADED

    def test_check_availability_returns_unavailable_on_connection_error(self):
        """check_availability should return UNAVAILABLE on connection failure."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )
        checker = MemoryAvailabilityChecker()
        mock_client = Mock()
        mock_client.execute_forgetful_tool = Mock(side_effect=ConnectionError("No connection"))

        status = checker.check_availability(mock_client)
        assert status == MemoryAvailabilityStatus.UNAVAILABLE

    def test_check_availability_returns_degraded_on_unexpected_error(self):
        """check_availability should return DEGRADED on unexpected exceptions."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )
        checker = MemoryAvailabilityChecker()
        mock_client = Mock()
        # Use a different exception type that isn't TimeoutError or ConnectionError
        mock_client.execute_forgetful_tool = Mock(side_effect=ValueError("Unexpected error"))

        status = checker.check_availability(mock_client)
        assert status == MemoryAvailabilityStatus.DEGRADED

    def test_check_availability_logs_unexpected_error(self, caplog):
        """check_availability should log unexpected errors."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemoryAvailabilityChecker

        checker = MemoryAvailabilityChecker()
        mock_client = Mock()
        mock_client.execute_forgetful_tool = Mock(side_effect=RuntimeError("Something went wrong"))

        with caplog.at_level(logging.WARNING):
            checker.check_availability(mock_client)

        assert any("unexpected" in record.message.lower() for record in caplog.records)


# =============================================================================
# Task 3 Tests: Degraded Query Behavior
# =============================================================================

class TestDegradedQueryResult:
    """Tests for DegradedQueryResult dataclass."""

    def test_degraded_query_result_exists(self):
        """DegradedQueryResult dataclass should exist."""
        from pcmrp_tools.bmad_automation.memory_degradation import DegradedQueryResult
        assert DegradedQueryResult is not None

    def test_degraded_query_result_default_values(self):
        """DegradedQueryResult should have correct default values."""
        from pcmrp_tools.bmad_automation.memory_degradation import DegradedQueryResult
        result = DegradedQueryResult()
        assert result.results == []
        assert result.status == "degraded"
        assert result.reason == "forgetful_unavailable"

    def test_degraded_query_result_custom_values(self):
        """DegradedQueryResult should accept custom values."""
        from pcmrp_tools.bmad_automation.memory_degradation import DegradedQueryResult
        result = DegradedQueryResult(
            results=["item1", "item2"],
            status="custom_status",
            reason="custom_reason"
        )
        assert result.results == ["item1", "item2"]
        assert result.status == "custom_status"
        assert result.reason == "custom_reason"

    def test_degraded_query_result_is_dataclass(self):
        """DegradedQueryResult should be a dataclass."""
        from dataclasses import is_dataclass
        from pcmrp_tools.bmad_automation.memory_degradation import DegradedQueryResult
        assert is_dataclass(DegradedQueryResult)


class TestQueryWithFallback:
    """Tests for query_with_fallback function."""

    def test_query_with_fallback_exists(self):
        """query_with_fallback function should exist."""
        from pcmrp_tools.bmad_automation.memory_degradation import query_with_fallback
        assert callable(query_with_fallback)

    def test_query_with_fallback_returns_result_when_available(self):
        """query_with_fallback should return query result when memory is available."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            query_with_fallback,
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )

        mock_client = Mock()
        expected_results = [{"id": 1, "content": "test memory"}]
        mock_client.execute_forgetful_tool = Mock(return_value=expected_results)

        mock_checker = Mock(spec=MemoryAvailabilityChecker)
        mock_checker.check_availability = Mock(return_value=MemoryAvailabilityStatus.AVAILABLE)

        result = query_with_fallback(mock_client, "test query", mock_checker)

        assert result == expected_results
        mock_client.execute_forgetful_tool.assert_called()

    def test_query_with_fallback_returns_degraded_result_when_degraded(self):
        """query_with_fallback should return DegradedQueryResult when status is DEGRADED."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            query_with_fallback,
            DegradedQueryResult,
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )

        mock_client = Mock()
        mock_checker = Mock(spec=MemoryAvailabilityChecker)
        mock_checker.check_availability = Mock(return_value=MemoryAvailabilityStatus.DEGRADED)

        result = query_with_fallback(mock_client, "test query", mock_checker)

        assert isinstance(result, DegradedQueryResult)
        assert result.status == "degraded"
        assert result.reason == "forgetful_unavailable"
        assert result.results == []

    def test_query_with_fallback_returns_degraded_result_when_unavailable(self):
        """query_with_fallback should return DegradedQueryResult when status is UNAVAILABLE."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            query_with_fallback,
            DegradedQueryResult,
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )

        mock_client = Mock()
        mock_checker = Mock(spec=MemoryAvailabilityChecker)
        mock_checker.check_availability = Mock(return_value=MemoryAvailabilityStatus.UNAVAILABLE)

        result = query_with_fallback(mock_client, "test query", mock_checker)

        assert isinstance(result, DegradedQueryResult)
        assert result.status == "degraded"
        assert result.reason == "forgetful_unavailable"

    def test_query_with_fallback_logs_degraded_query(self, caplog):
        """query_with_fallback should log when operating in degraded mode."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            query_with_fallback,
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )

        mock_client = Mock()
        mock_checker = Mock(spec=MemoryAvailabilityChecker)
        mock_checker.check_availability = Mock(return_value=MemoryAvailabilityStatus.DEGRADED)

        with caplog.at_level(logging.WARNING):
            query_with_fallback(mock_client, "test query", mock_checker)

        assert any("degraded" in record.message.lower() for record in caplog.records)

    def test_query_with_fallback_logs_query_text_for_debugging(self, caplog):
        """query_with_fallback should log the query text for debugging."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            query_with_fallback,
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )

        mock_client = Mock()
        mock_checker = Mock(spec=MemoryAvailabilityChecker)
        mock_checker.check_availability = Mock(return_value=MemoryAvailabilityStatus.DEGRADED)

        test_query = "specific test query for logging"

        with caplog.at_level(logging.DEBUG):
            query_with_fallback(mock_client, test_query, mock_checker)

        # The query text should appear in at least one log record
        all_messages = " ".join(record.message for record in caplog.records)
        assert test_query in all_messages

    def test_query_with_fallback_handles_query_exception(self):
        """query_with_fallback should handle exceptions during query execution."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            query_with_fallback,
            DegradedQueryResult,
            MemoryAvailabilityChecker,
            MemoryAvailabilityStatus,
        )

        mock_client = Mock()
        mock_client.execute_forgetful_tool = Mock(side_effect=RuntimeError("Query failed"))

        mock_checker = Mock(spec=MemoryAvailabilityChecker)
        mock_checker.check_availability = Mock(return_value=MemoryAvailabilityStatus.AVAILABLE)

        result = query_with_fallback(mock_client, "test query", mock_checker)

        # Should return degraded result when query fails
        assert isinstance(result, DegradedQueryResult)


# =============================================================================
# Task 4 Tests: User Notification
# =============================================================================

class TestDegradedModeNotification:
    """Tests for DEGRADED_MODE_NOTIFICATION constant."""

    def test_notification_constant_exists(self):
        """DEGRADED_MODE_NOTIFICATION constant should exist."""
        from pcmrp_tools.bmad_automation.memory_degradation import DEGRADED_MODE_NOTIFICATION
        assert DEGRADED_MODE_NOTIFICATION is not None

    def test_notification_is_string(self):
        """DEGRADED_MODE_NOTIFICATION should be a string."""
        from pcmrp_tools.bmad_automation.memory_degradation import DEGRADED_MODE_NOTIFICATION
        assert isinstance(DEGRADED_MODE_NOTIFICATION, str)

    def test_notification_mentions_memory_unavailable(self):
        """DEGRADED_MODE_NOTIFICATION should mention memory unavailability."""
        from pcmrp_tools.bmad_automation.memory_degradation import DEGRADED_MODE_NOTIFICATION
        assert "memory" in DEGRADED_MODE_NOTIFICATION.lower()
        assert "unavailable" in DEGRADED_MODE_NOTIFICATION.lower()

    def test_notification_mentions_patterns_not_loaded(self):
        """DEGRADED_MODE_NOTIFICATION should mention patterns won't be loaded."""
        from pcmrp_tools.bmad_automation.memory_degradation import DEGRADED_MODE_NOTIFICATION
        assert "pattern" in DEGRADED_MODE_NOTIFICATION.lower()

    def test_notification_mentions_reconnection(self):
        """DEGRADED_MODE_NOTIFICATION should mention reconnection."""
        from pcmrp_tools.bmad_automation.memory_degradation import DEGRADED_MODE_NOTIFICATION
        assert "reconnection" in DEGRADED_MODE_NOTIFICATION.lower()


class TestNotificationManager:
    """Tests for NotificationManager class."""

    def test_notification_manager_exists(self):
        """NotificationManager class should exist."""
        from pcmrp_tools.bmad_automation.memory_degradation import NotificationManager
        assert NotificationManager is not None

    def test_notification_manager_can_be_instantiated(self):
        """NotificationManager should be instantiable."""
        from pcmrp_tools.bmad_automation.memory_degradation import NotificationManager
        manager = NotificationManager()
        assert manager is not None

    def test_notify_user_once_returns_message_first_time(self):
        """notify_user_once should return the notification message on first call."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            NotificationManager,
            DEGRADED_MODE_NOTIFICATION,
        )
        manager = NotificationManager()
        result = manager.notify_user_once()
        assert result == DEGRADED_MODE_NOTIFICATION

    def test_notify_user_once_returns_none_on_subsequent_calls(self):
        """notify_user_once should return None on subsequent calls."""
        from pcmrp_tools.bmad_automation.memory_degradation import NotificationManager
        manager = NotificationManager()

        # First call returns message
        first_result = manager.notify_user_once()
        assert first_result is not None

        # Subsequent calls return None
        second_result = manager.notify_user_once()
        assert second_result is None

        third_result = manager.notify_user_once()
        assert third_result is None

    def test_notify_user_once_deduplication_across_many_calls(self):
        """notify_user_once should only return message once across many calls."""
        from pcmrp_tools.bmad_automation.memory_degradation import NotificationManager
        manager = NotificationManager()

        results = [manager.notify_user_once() for _ in range(10)]

        # Only first result should be non-None
        non_none_results = [r for r in results if r is not None]
        assert len(non_none_results) == 1

    def test_different_managers_have_separate_state(self):
        """Different NotificationManager instances should have separate notification state."""
        from pcmrp_tools.bmad_automation.memory_degradation import NotificationManager

        manager1 = NotificationManager()
        manager2 = NotificationManager()

        # First call on manager1
        result1 = manager1.notify_user_once()
        assert result1 is not None

        # First call on manager2 should also return message
        result2 = manager2.notify_user_once()
        assert result2 is not None

        # Second call on manager1 should return None
        result3 = manager1.notify_user_once()
        assert result3 is None

    def test_notification_manager_has_notified_property(self):
        """NotificationManager should track whether user has been notified."""
        from pcmrp_tools.bmad_automation.memory_degradation import NotificationManager
        manager = NotificationManager()

        # Initially not notified
        assert manager.has_been_notified is False

        # After notification
        manager.notify_user_once()
        assert manager.has_been_notified is True

    def test_notification_manager_reset(self):
        """NotificationManager should support resetting notification state."""
        from pcmrp_tools.bmad_automation.memory_degradation import NotificationManager
        manager = NotificationManager()

        # Notify once
        first_result = manager.notify_user_once()
        assert first_result is not None

        # Second call returns None
        second_result = manager.notify_user_once()
        assert second_result is None

        # Reset state
        manager.reset()

        # After reset, should return message again
        third_result = manager.notify_user_once()
        assert third_result is not None


class TestSessionContext:
    """Tests for session context integration with NotificationManager."""

    def test_session_context_can_hold_notification_manager(self):
        """Session context should be able to hold a NotificationManager."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            NotificationManager,
            SessionContext,
        )

        context = SessionContext()
        assert hasattr(context, 'notification_manager')
        assert isinstance(context.notification_manager, NotificationManager)

    def test_session_context_notification_state_persists(self):
        """SessionContext should persist notification state across access."""
        from pcmrp_tools.bmad_automation.memory_degradation import SessionContext

        context = SessionContext()

        # First notification
        result1 = context.notification_manager.notify_user_once()
        assert result1 is not None

        # Access again - should still be notified
        result2 = context.notification_manager.notify_user_once()
        assert result2 is None

    def test_session_context_tracks_degraded_mode(self):
        """SessionContext should track whether system is in degraded mode."""
        from pcmrp_tools.bmad_automation.memory_degradation import SessionContext

        context = SessionContext()

        # Initially not in degraded mode
        assert context.is_degraded_mode is False

        # Can set degraded mode
        context.set_degraded_mode(True)
        assert context.is_degraded_mode is True

        # Can unset degraded mode
        context.set_degraded_mode(False)
        assert context.is_degraded_mode is False


# =============================================================================
# TASK 1: Enhanced MemoryAvailabilityChecker Tests (New Requirements)
# =============================================================================


class TestMemoryStatusEnum:
    """Test MemoryStatus enum values (Task 1)."""

    def test_memory_status_available_value(self):
        """AVAILABLE status should have value 'available'."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemoryStatus

        assert MemoryStatus.AVAILABLE.value == "available"

    def test_memory_status_degraded_value(self):
        """DEGRADED status should have value 'degraded'."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemoryStatus

        assert MemoryStatus.DEGRADED.value == "degraded"

    def test_memory_status_permanently_unavailable_value(self):
        """PERMANENTLY_UNAVAILABLE status should have value 'permanently_unavailable'."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemoryStatus

        assert MemoryStatus.PERMANENTLY_UNAVAILABLE.value == "permanently_unavailable"

    def test_memory_status_has_three_values(self):
        """MemoryStatus should have exactly three values."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemoryStatus

        assert len(MemoryStatus) == 3


class TestAvailabilityResultDataclass:
    """Test AvailabilityResult dataclass (Task 1)."""

    def test_availability_result_is_dataclass(self):
        """AvailabilityResult should be a dataclass."""
        from pcmrp_tools.bmad_automation.memory_degradation import AvailabilityResult

        assert is_dataclass(AvailabilityResult)

    def test_availability_result_has_status_field(self):
        """AvailabilityResult should have status field."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            AvailabilityResult,
            MemoryStatus,
        )

        result = AvailabilityResult(
            status=MemoryStatus.AVAILABLE,
            reason="Connected",
            last_check=datetime.now(),
            next_check_at=datetime.now() + timedelta(minutes=5),
            check_count=1,
        )

        assert result.status == MemoryStatus.AVAILABLE

    def test_availability_result_has_reason_field(self):
        """AvailabilityResult should have reason field."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            AvailabilityResult,
            MemoryStatus,
        )

        result = AvailabilityResult(
            status=MemoryStatus.DEGRADED,
            reason="Connection timeout",
            last_check=datetime.now(),
            next_check_at=datetime.now() + timedelta(minutes=5),
            check_count=2,
        )

        assert result.reason == "Connection timeout"

    def test_availability_result_has_last_check_field(self):
        """AvailabilityResult should have last_check field."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            AvailabilityResult,
            MemoryStatus,
        )

        now = datetime.now()
        result = AvailabilityResult(
            status=MemoryStatus.AVAILABLE,
            reason="OK",
            last_check=now,
            next_check_at=now + timedelta(minutes=5),
            check_count=1,
        )

        assert result.last_check == now

    def test_availability_result_has_next_check_at_field(self):
        """AvailabilityResult should have next_check_at field."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            AvailabilityResult,
            MemoryStatus,
        )

        now = datetime.now()
        next_check = now + timedelta(minutes=5)
        result = AvailabilityResult(
            status=MemoryStatus.AVAILABLE,
            reason="OK",
            last_check=now,
            next_check_at=next_check,
            check_count=1,
        )

        assert result.next_check_at == next_check

    def test_availability_result_has_check_count_field(self):
        """AvailabilityResult should have check_count field."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            AvailabilityResult,
            MemoryStatus,
        )

        result = AvailabilityResult(
            status=MemoryStatus.AVAILABLE,
            reason="OK",
            last_check=datetime.now(),
            next_check_at=datetime.now() + timedelta(minutes=5),
            check_count=5,
        )

        assert result.check_count == 5


class TestTask1Constants:
    """Test module constants for Task 1."""

    def test_initial_check_interval_seconds_is_300(self):
        """INITIAL_CHECK_INTERVAL_SECONDS should be 300 (5 minutes)."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            INITIAL_CHECK_INTERVAL_SECONDS,
        )

        assert INITIAL_CHECK_INTERVAL_SECONDS == 300

    def test_extended_check_interval_seconds_is_1800(self):
        """EXTENDED_CHECK_INTERVAL_SECONDS should be 1800 (30 minutes)."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            EXTENDED_CHECK_INTERVAL_SECONDS,
        )

        assert EXTENDED_CHECK_INTERVAL_SECONDS == 1800

    def test_max_initial_checks_is_6(self):
        """MAX_INITIAL_CHECKS should be 6."""
        from pcmrp_tools.bmad_automation.memory_degradation import MAX_INITIAL_CHECKS

        assert MAX_INITIAL_CHECKS == 6

    def test_max_retry_attempts_is_3(self):
        """MAX_RETRY_ATTEMPTS should be 3."""
        from pcmrp_tools.bmad_automation.memory_degradation import MAX_RETRY_ATTEMPTS

        assert MAX_RETRY_ATTEMPTS == 3

    def test_retry_interval_ms_is_100(self):
        """RETRY_INTERVAL_MS should be 100."""
        from pcmrp_tools.bmad_automation.memory_degradation import RETRY_INTERVAL_MS

        assert RETRY_INTERVAL_MS == 100


class TestEnhancedMemoryAvailabilityChecker:
    """Test enhanced MemoryAvailabilityChecker with async and intervals (Task 1)."""

    def test_checker_has_get_next_check_time_method(self):
        """MemoryAvailabilityChecker should have get_next_check_time method."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
        )

        checker = MemoryAvailabilityChecker()

        assert hasattr(checker, "get_next_check_time")
        assert callable(checker.get_next_check_time)

    def test_checker_has_should_check_now_method(self):
        """MemoryAvailabilityChecker should have should_check_now method."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
        )

        checker = MemoryAvailabilityChecker()

        assert hasattr(checker, "should_check_now")
        assert callable(checker.should_check_now)

    def test_checker_has_check_availability_async_method(self):
        """MemoryAvailabilityChecker should have check_availability_async method."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
        )

        checker = MemoryAvailabilityChecker()

        assert hasattr(checker, "check_availability_async")
        assert callable(checker.check_availability_async)


class TestCheckAvailabilityAsync:
    """Test check_availability_async method (Task 1)."""

    @pytest.mark.asyncio
    async def test_check_availability_async_returns_availability_result(self):
        """check_availability_async should return AvailabilityResult."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            AvailabilityResult,
            MemoryAvailabilityChecker,
        )

        mock_client = AsyncMock(return_value={"status": "ok"})
        checker = MemoryAvailabilityChecker()

        result = await checker.check_availability_async(mock_client)

        assert isinstance(result, AvailabilityResult)

    @pytest.mark.asyncio
    async def test_check_availability_async_returns_available_on_success(self):
        """check_availability_async should return AVAILABLE status on success."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryStatus,
        )

        mock_client = AsyncMock(return_value={"status": "ok"})
        checker = MemoryAvailabilityChecker()

        result = await checker.check_availability_async(mock_client)

        assert result.status == MemoryStatus.AVAILABLE

    @pytest.mark.asyncio
    async def test_check_availability_async_returns_degraded_on_timeout(self):
        """check_availability_async should return DEGRADED status on timeout."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryStatus,
        )

        mock_client = AsyncMock(side_effect=TimeoutError("Connection timed out"))
        checker = MemoryAvailabilityChecker()

        result = await checker.check_availability_async(mock_client)

        assert result.status == MemoryStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_check_availability_async_returns_degraded_on_connection_error(self):
        """check_availability_async should return DEGRADED status on connection error."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryStatus,
        )

        mock_client = AsyncMock(side_effect=ConnectionError("Failed to connect"))
        checker = MemoryAvailabilityChecker()

        result = await checker.check_availability_async(mock_client)

        assert result.status == MemoryStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_check_availability_async_retries_on_failure(self):
        """check_availability_async should retry up to MAX_RETRY_ATTEMPTS times."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MAX_RETRY_ATTEMPTS,
            MemoryAvailabilityChecker,
        )

        mock_client = AsyncMock(side_effect=TimeoutError("Timeout"))
        checker = MemoryAvailabilityChecker()

        await checker.check_availability_async(mock_client)

        # Should have been called MAX_RETRY_ATTEMPTS times
        assert mock_client.call_count == MAX_RETRY_ATTEMPTS

    @pytest.mark.asyncio
    async def test_check_availability_async_succeeds_on_retry(self):
        """check_availability_async should succeed if any retry succeeds."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryStatus,
        )

        # Fail twice, succeed on third attempt
        mock_client = AsyncMock(
            side_effect=[
                TimeoutError("Timeout"),
                TimeoutError("Timeout"),
                {"status": "ok"},
            ]
        )
        checker = MemoryAvailabilityChecker()

        result = await checker.check_availability_async(mock_client)

        assert result.status == MemoryStatus.AVAILABLE
        assert mock_client.call_count == 3

    @pytest.mark.asyncio
    async def test_check_availability_async_increments_check_count(self):
        """check_availability_async should increment check_count."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
        )

        mock_client = AsyncMock(return_value={"status": "ok"})
        checker = MemoryAvailabilityChecker()

        result1 = await checker.check_availability_async(mock_client)
        result2 = await checker.check_availability_async(mock_client)

        assert result1.check_count == 1
        assert result2.check_count == 2

    @pytest.mark.asyncio
    async def test_check_availability_async_sets_last_check_time(self):
        """check_availability_async should set last_check to current time."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
        )

        mock_client = AsyncMock(return_value={"status": "ok"})
        checker = MemoryAvailabilityChecker()

        before = datetime.now()
        result = await checker.check_availability_async(mock_client)
        after = datetime.now()

        assert before <= result.last_check <= after

    @pytest.mark.asyncio
    async def test_check_availability_async_sets_next_check_time(self):
        """check_availability_async should set next_check_at appropriately."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
        )

        mock_client = AsyncMock(return_value={"status": "ok"})
        checker = MemoryAvailabilityChecker()

        result = await checker.check_availability_async(mock_client)

        assert result.next_check_at > result.last_check

    @pytest.mark.asyncio
    async def test_check_availability_async_includes_reason_for_failure(self):
        """check_availability_async should include error reason on failure."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
        )

        mock_client = AsyncMock(side_effect=TimeoutError("Connection timed out"))
        checker = MemoryAvailabilityChecker()

        result = await checker.check_availability_async(mock_client)

        assert "timeout" in result.reason.lower() or "timed out" in result.reason.lower()


class TestGetNextCheckTime:
    """Test get_next_check_time method (Task 1)."""

    def test_get_next_check_time_uses_initial_interval_for_first_6_checks(self):
        """get_next_check_time should use INITIAL_CHECK_INTERVAL for checks 1-6."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            INITIAL_CHECK_INTERVAL_SECONDS,
            MemoryAvailabilityChecker,
        )

        checker = MemoryAvailabilityChecker()

        for check_count in range(1, 7):
            before = datetime.now()
            result = checker.get_next_check_time(check_count)
            expected = before + timedelta(seconds=INITIAL_CHECK_INTERVAL_SECONDS)
            # Allow 2 second tolerance
            assert abs((result - expected).total_seconds()) < 2

    def test_get_next_check_time_uses_extended_interval_after_6_checks(self):
        """get_next_check_time should use EXTENDED_CHECK_INTERVAL for checks > 6."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            EXTENDED_CHECK_INTERVAL_SECONDS,
            MemoryAvailabilityChecker,
        )

        checker = MemoryAvailabilityChecker()

        for check_count in range(7, 10):
            before = datetime.now()
            result = checker.get_next_check_time(check_count)
            expected = before + timedelta(seconds=EXTENDED_CHECK_INTERVAL_SECONDS)
            # Allow 2 second tolerance
            assert abs((result - expected).total_seconds()) < 2

    def test_get_next_check_time_boundary_check_6(self):
        """get_next_check_time at check 6 should use INITIAL interval."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            INITIAL_CHECK_INTERVAL_SECONDS,
            MemoryAvailabilityChecker,
        )

        checker = MemoryAvailabilityChecker()

        before = datetime.now()
        result = checker.get_next_check_time(6)
        expected = before + timedelta(seconds=INITIAL_CHECK_INTERVAL_SECONDS)
        # Allow 2 second tolerance
        assert abs((result - expected).total_seconds()) < 2

    def test_get_next_check_time_boundary_check_7(self):
        """get_next_check_time at check 7 should use EXTENDED interval."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            EXTENDED_CHECK_INTERVAL_SECONDS,
            MemoryAvailabilityChecker,
        )

        checker = MemoryAvailabilityChecker()

        before = datetime.now()
        result = checker.get_next_check_time(7)
        expected = before + timedelta(seconds=EXTENDED_CHECK_INTERVAL_SECONDS)
        # Allow 2 second tolerance
        assert abs((result - expected).total_seconds()) < 2


class TestShouldCheckNow:
    """Test should_check_now method (Task 1)."""

    def test_should_check_now_returns_true_if_no_last_check(self):
        """should_check_now should return True if never checked before."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryStatus,
        )

        checker = MemoryAvailabilityChecker()

        result = checker.should_check_now(None, MemoryStatus.DEGRADED)

        assert result is True

    def test_should_check_now_returns_true_if_past_next_check_time(self):
        """should_check_now should return True if past expected check interval."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryStatus,
        )

        checker = MemoryAvailabilityChecker()
        # Last check was 10 minutes ago (past INITIAL_CHECK_INTERVAL of 5 min)
        last_check = datetime.now() - timedelta(minutes=10)

        result = checker.should_check_now(last_check, MemoryStatus.DEGRADED)

        assert result is True

    def test_should_check_now_returns_false_if_recently_checked(self):
        """should_check_now should return False if checked recently."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryStatus,
        )

        checker = MemoryAvailabilityChecker()
        # Last check was 1 minute ago (within INITIAL_CHECK_INTERVAL of 5 min)
        last_check = datetime.now() - timedelta(minutes=1)

        result = checker.should_check_now(last_check, MemoryStatus.DEGRADED)

        assert result is False

    def test_should_check_now_returns_false_for_available_status_recently_checked(self):
        """should_check_now with AVAILABLE status and recent check should return False."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
            MemoryStatus,
        )

        checker = MemoryAvailabilityChecker()
        # Recent check with available status
        last_check = datetime.now() - timedelta(seconds=30)

        result = checker.should_check_now(last_check, MemoryStatus.AVAILABLE)

        # When available, no need to check again immediately
        assert result is False


# =============================================================================
# TASK 2: MemorySaveQueue Tests
# =============================================================================


class TestQueuedMemoryDataclass:
    """Test QueuedMemory dataclass (Task 2)."""

    def test_queued_memory_is_dataclass(self):
        """QueuedMemory should be a dataclass."""
        from pcmrp_tools.bmad_automation.memory_degradation import QueuedMemory

        assert is_dataclass(QueuedMemory)

    def test_queued_memory_has_memory_data_field(self):
        """QueuedMemory should have memory_data field."""
        from pcmrp_tools.bmad_automation.memory_degradation import QueuedMemory

        memory_data = {"title": "Test", "content": "Content"}
        queued = QueuedMemory(
            memory_data=memory_data,
            timestamp=datetime.now(),
            retries=0,
        )

        assert queued.memory_data == memory_data

    def test_queued_memory_has_timestamp_field(self):
        """QueuedMemory should have timestamp field."""
        from pcmrp_tools.bmad_automation.memory_degradation import QueuedMemory

        now = datetime.now()
        queued = QueuedMemory(
            memory_data={"title": "Test"},
            timestamp=now,
            retries=0,
        )

        assert queued.timestamp == now

    def test_queued_memory_has_retries_field(self):
        """QueuedMemory should have retries field."""
        from pcmrp_tools.bmad_automation.memory_degradation import QueuedMemory

        queued = QueuedMemory(
            memory_data={"title": "Test"},
            timestamp=datetime.now(),
            retries=3,
        )

        assert queued.retries == 3


class TestTask2Constants:
    """Test module constants for Task 2."""

    def test_max_queue_size_is_100(self):
        """MAX_QUEUE_SIZE should be 100."""
        from pcmrp_tools.bmad_automation.memory_degradation import MAX_QUEUE_SIZE

        assert MAX_QUEUE_SIZE == 100


class TestMemorySaveQueueInit:
    """Test MemorySaveQueue initialization (Task 2)."""

    def test_queue_initializes_empty(self):
        """MemorySaveQueue should initialize with empty queue."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        assert len(queue.get_queue()) == 0

    def test_queue_has_add_to_queue_method(self):
        """MemorySaveQueue should have add_to_queue method."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        assert hasattr(queue, "add_to_queue")
        assert callable(queue.add_to_queue)

    def test_queue_has_get_queue_method(self):
        """MemorySaveQueue should have get_queue method."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        assert hasattr(queue, "get_queue")
        assert callable(queue.get_queue)

    def test_queue_has_clear_queue_method(self):
        """MemorySaveQueue should have clear_queue method."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        assert hasattr(queue, "clear_queue")
        assert callable(queue.clear_queue)

    def test_queue_has_persist_to_file_method(self):
        """MemorySaveQueue should have persist_to_file method."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        assert hasattr(queue, "persist_to_file")
        assert callable(queue.persist_to_file)

    def test_queue_has_load_from_file_method(self):
        """MemorySaveQueue should have load_from_file method."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        assert hasattr(queue, "load_from_file")
        assert callable(queue.load_from_file)


class TestAddToQueue:
    """Test add_to_queue method (Task 2)."""

    def test_add_to_queue_adds_memory_data(self):
        """add_to_queue should add memory data to queue."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        memory_data = {"title": "Test Memory", "content": "Test content"}

        queue.add_to_queue(memory_data)

        assert len(queue.get_queue()) == 1

    def test_add_to_queue_preserves_memory_data(self):
        """add_to_queue should preserve the memory data."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        memory_data = {"title": "Test Memory", "content": "Test content"}

        queue.add_to_queue(memory_data)

        assert queue.get_queue()[0].memory_data == memory_data

    def test_add_to_queue_sets_timestamp(self):
        """add_to_queue should set timestamp on queued memory."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        memory_data = {"title": "Test Memory"}

        before = datetime.now()
        queue.add_to_queue(memory_data)
        after = datetime.now()

        queued = queue.get_queue()[0]
        assert before <= queued.timestamp <= after

    def test_add_to_queue_initializes_retries_to_zero(self):
        """add_to_queue should initialize retries to 0."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        memory_data = {"title": "Test Memory"}

        queue.add_to_queue(memory_data)

        assert queue.get_queue()[0].retries == 0

    def test_add_to_queue_maintains_order(self):
        """add_to_queue should maintain FIFO order."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        queue.add_to_queue({"title": "First"})
        queue.add_to_queue({"title": "Second"})
        queue.add_to_queue({"title": "Third"})

        items = queue.get_queue()
        assert items[0].memory_data["title"] == "First"
        assert items[1].memory_data["title"] == "Second"
        assert items[2].memory_data["title"] == "Third"

    def test_add_to_queue_drops_oldest_at_max_size(self):
        """add_to_queue should drop oldest when MAX_QUEUE_SIZE exceeded."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MAX_QUEUE_SIZE,
            MemorySaveQueue,
        )

        queue = MemorySaveQueue()

        # Fill queue to max
        for i in range(MAX_QUEUE_SIZE):
            queue.add_to_queue({"title": f"Memory {i}"})

        # Add one more (should drop oldest)
        queue.add_to_queue({"title": "Overflow Memory"})

        items = queue.get_queue()
        assert len(items) == MAX_QUEUE_SIZE
        # First item should now be "Memory 1" (Memory 0 was dropped)
        assert items[0].memory_data["title"] == "Memory 1"
        # Last item should be the overflow memory
        assert items[-1].memory_data["title"] == "Overflow Memory"

    def test_add_to_queue_fifo_overflow_handling(self):
        """add_to_queue with overflow should use FIFO (drop oldest)."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MAX_QUEUE_SIZE,
            MemorySaveQueue,
        )

        queue = MemorySaveQueue()

        # Fill queue to max
        for i in range(MAX_QUEUE_SIZE):
            queue.add_to_queue({"title": f"Memory {i}"})

        # Add two more
        queue.add_to_queue({"title": "New 1"})
        queue.add_to_queue({"title": "New 2"})

        items = queue.get_queue()
        assert len(items) == MAX_QUEUE_SIZE
        # First two originals should be dropped
        assert items[0].memory_data["title"] == "Memory 2"
        assert items[-2].memory_data["title"] == "New 1"
        assert items[-1].memory_data["title"] == "New 2"


class TestGetQueueMethod:
    """Test get_queue method (Task 2)."""

    def test_get_queue_returns_list(self):
        """get_queue should return a list."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        result = queue.get_queue()

        assert isinstance(result, list)

    def test_get_queue_returns_queued_memory_objects(self):
        """get_queue should return list of QueuedMemory objects."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemorySaveQueue,
            QueuedMemory,
        )

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Test"})

        result = queue.get_queue()

        assert all(isinstance(item, QueuedMemory) for item in result)

    def test_get_queue_returns_copy(self):
        """get_queue should return a copy, not the internal queue."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Test"})

        result1 = queue.get_queue()
        result2 = queue.get_queue()

        # Should be equal but not the same object
        assert result1 is not result2


class TestClearQueueMethod:
    """Test clear_queue method (Task 2)."""

    def test_clear_queue_removes_all_items(self):
        """clear_queue should remove all items from queue."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})
        queue.add_to_queue({"title": "Memory 2"})
        queue.add_to_queue({"title": "Memory 3"})

        queue.clear_queue()

        assert len(queue.get_queue()) == 0

    def test_clear_queue_on_empty_queue(self):
        """clear_queue on empty queue should not raise error."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        # Should not raise
        queue.clear_queue()

        assert len(queue.get_queue()) == 0


class TestPersistToFile:
    """Test persist_to_file method (Task 2)."""

    def test_persist_to_file_creates_file(self):
        """persist_to_file should create the file."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Test Memory"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            queue.persist_to_file(path)

            assert path.exists()

    def test_persist_to_file_saves_all_items(self):
        """persist_to_file should save all queued items."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})
        queue.add_to_queue({"title": "Memory 2"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            queue.persist_to_file(path)

            with open(path, "r") as f:
                data = json.load(f)

            assert len(data) == 2

    def test_persist_to_file_saves_memory_data(self):
        """persist_to_file should preserve memory_data field."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Test Title", "content": "Test content"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            queue.persist_to_file(path)

            with open(path, "r") as f:
                data = json.load(f)

            assert data[0]["memory_data"]["title"] == "Test Title"
            assert data[0]["memory_data"]["content"] == "Test content"

    def test_persist_to_file_saves_timestamp(self):
        """persist_to_file should preserve timestamp field."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Test"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            queue.persist_to_file(path)

            with open(path, "r") as f:
                data = json.load(f)

            assert "timestamp" in data[0]

    def test_persist_to_file_saves_retries(self):
        """persist_to_file should preserve retries field."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Test"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            queue.persist_to_file(path)

            with open(path, "r") as f:
                data = json.load(f)

            assert data[0]["retries"] == 0

    def test_persist_to_file_overwrites_existing(self):
        """persist_to_file should overwrite existing file."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            # First save
            queue1 = MemorySaveQueue()
            queue1.add_to_queue({"title": "First"})
            queue1.persist_to_file(path)

            # Second save
            queue2 = MemorySaveQueue()
            queue2.add_to_queue({"title": "Second"})
            queue2.persist_to_file(path)

            with open(path, "r") as f:
                data = json.load(f)

            assert len(data) == 1
            assert data[0]["memory_data"]["title"] == "Second"

    def test_persist_to_file_empty_queue(self):
        """persist_to_file with empty queue should create empty JSON array."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            queue.persist_to_file(path)

            with open(path, "r") as f:
                data = json.load(f)

            assert data == []


class TestLoadFromFile:
    """Test load_from_file method (Task 2)."""

    def test_load_from_file_restores_items(self):
        """load_from_file should restore queued items."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            # Save some items
            queue1 = MemorySaveQueue()
            queue1.add_to_queue({"title": "Memory 1"})
            queue1.add_to_queue({"title": "Memory 2"})
            queue1.persist_to_file(path)

            # Load into new queue
            queue2 = MemorySaveQueue()
            queue2.load_from_file(path)

            items = queue2.get_queue()
            assert len(items) == 2
            assert items[0].memory_data["title"] == "Memory 1"
            assert items[1].memory_data["title"] == "Memory 2"

    def test_load_from_file_restores_timestamp(self):
        """load_from_file should restore timestamp field."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            queue1 = MemorySaveQueue()
            queue1.add_to_queue({"title": "Test"})
            original_timestamp = queue1.get_queue()[0].timestamp
            queue1.persist_to_file(path)

            queue2 = MemorySaveQueue()
            queue2.load_from_file(path)

            restored_timestamp = queue2.get_queue()[0].timestamp
            # Allow 1 second tolerance for serialization rounding
            assert abs((restored_timestamp - original_timestamp).total_seconds()) < 1

    def test_load_from_file_restores_retries(self):
        """load_from_file should restore retries field."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            # Manually create a file with retries > 0
            data = [
                {
                    "memory_data": {"title": "Test"},
                    "timestamp": datetime.now().isoformat(),
                    "retries": 5,
                }
            ]
            with open(path, "w") as f:
                json.dump(data, f)

            queue = MemorySaveQueue()
            queue.load_from_file(path)

            assert queue.get_queue()[0].retries == 5

    def test_load_from_file_nonexistent_returns_empty(self):
        """load_from_file with nonexistent file should result in empty queue."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        queue.load_from_file(Path("/nonexistent/path/queue.json"))

        assert len(queue.get_queue()) == 0

    def test_load_from_file_corrupt_file_returns_empty(self):
        """load_from_file with corrupt file should result in empty queue."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            # Write corrupt JSON
            with open(path, "w") as f:
                f.write("{ invalid json content }")

            queue = MemorySaveQueue()
            queue.load_from_file(path)

            assert len(queue.get_queue()) == 0

    def test_load_from_file_empty_file_returns_empty(self):
        """load_from_file with empty file should result in empty queue."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            # Write empty file
            with open(path, "w") as f:
                f.write("")

            queue = MemorySaveQueue()
            queue.load_from_file(path)

            assert len(queue.get_queue()) == 0

    def test_load_from_file_replaces_existing_queue(self):
        """load_from_file should replace existing queue contents."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            # Create file with one item
            queue1 = MemorySaveQueue()
            queue1.add_to_queue({"title": "From File"})
            queue1.persist_to_file(path)

            # Create queue with different items
            queue2 = MemorySaveQueue()
            queue2.add_to_queue({"title": "Existing 1"})
            queue2.add_to_queue({"title": "Existing 2"})

            # Load should replace
            queue2.load_from_file(path)

            items = queue2.get_queue()
            assert len(items) == 1
            assert items[0].memory_data["title"] == "From File"

    def test_load_from_file_handles_missing_fields_gracefully(self):
        """load_from_file should handle items with missing optional fields."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "queue.json"

            # Create file with minimal data (missing timestamp and retries)
            data = [{"memory_data": {"title": "Test"}}]
            with open(path, "w") as f:
                json.dump(data, f)

            queue = MemorySaveQueue()
            queue.load_from_file(path)

            items = queue.get_queue()
            assert len(items) == 1
            assert items[0].memory_data["title"] == "Test"
            # Should have default values for missing fields
            assert items[0].retries == 0


# =============================================================================
# TASK 5: Queue Processing on Recovery Tests
# =============================================================================


class TestProcessQueuedSavesMethod:
    """Test process_queued_saves method exists (Task 5)."""

    def test_queue_has_process_queued_saves_method(self):
        """MemorySaveQueue should have process_queued_saves method."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()

        assert hasattr(queue, "process_queued_saves")
        assert callable(queue.process_queued_saves)


class TestProcessQueuedSavesAllSuccessful:
    """Test process_queued_saves with all saves successful (Task 5)."""

    @pytest.mark.asyncio
    async def test_process_queued_saves_returns_result_dict(self):
        """process_queued_saves should return a result dictionary."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        mock_client = AsyncMock(return_value={"id": 1})

        result = await queue.process_queued_saves(mock_client)

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_process_queued_saves_clears_queue_on_success(self):
        """process_queued_saves should clear queue when all saves succeed."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})
        queue.add_to_queue({"title": "Memory 2"})

        mock_client = AsyncMock(return_value={"id": 1})

        await queue.process_queued_saves(mock_client)

        assert len(queue.get_queue()) == 0

    @pytest.mark.asyncio
    async def test_process_queued_saves_calls_client_for_each_item(self):
        """process_queued_saves should call client for each queued item."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})
        queue.add_to_queue({"title": "Memory 2"})
        queue.add_to_queue({"title": "Memory 3"})

        mock_client = AsyncMock(return_value={"id": 1})

        await queue.process_queued_saves(mock_client)

        assert mock_client.call_count == 3

    @pytest.mark.asyncio
    async def test_process_queued_saves_returns_success_count(self):
        """process_queued_saves should return count of successful saves."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})
        queue.add_to_queue({"title": "Memory 2"})

        mock_client = AsyncMock(return_value={"id": 1})

        result = await queue.process_queued_saves(mock_client)

        assert result["successful"] == 2

    @pytest.mark.asyncio
    async def test_process_queued_saves_returns_failed_count(self):
        """process_queued_saves should return count of failed saves."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})
        queue.add_to_queue({"title": "Memory 2"})

        mock_client = AsyncMock(return_value={"id": 1})

        result = await queue.process_queued_saves(mock_client)

        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_process_queued_saves_empty_queue(self):
        """process_queued_saves with empty queue should return zero counts."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        mock_client = AsyncMock(return_value={"id": 1})

        result = await queue.process_queued_saves(mock_client)

        assert result["successful"] == 0
        assert result["failed"] == 0


class TestProcessQueuedSavesPartialFailure:
    """Test process_queued_saves with partial failures (Task 5)."""

    @pytest.mark.asyncio
    async def test_process_queued_saves_handles_partial_failures(self):
        """process_queued_saves should handle partial failures."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})
        queue.add_to_queue({"title": "Memory 2"})
        queue.add_to_queue({"title": "Memory 3"})

        # First succeeds, second fails, third succeeds
        mock_client = AsyncMock(
            side_effect=[
                {"id": 1},
                TimeoutError("Failed"),
                {"id": 3},
            ]
        )

        result = await queue.process_queued_saves(mock_client)

        assert result["successful"] == 2
        assert result["failed"] == 1

    @pytest.mark.asyncio
    async def test_process_queued_saves_retries_failed_items(self):
        """process_queued_saves should retry failed items up to MAX_RETRY_ATTEMPTS."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MAX_RETRY_ATTEMPTS,
            MemorySaveQueue,
        )

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})

        # Always fail
        mock_client = AsyncMock(side_effect=TimeoutError("Failed"))

        await queue.process_queued_saves(mock_client)

        # Should have tried MAX_RETRY_ATTEMPTS times
        assert mock_client.call_count == MAX_RETRY_ATTEMPTS

    @pytest.mark.asyncio
    async def test_process_queued_saves_succeeds_on_retry(self):
        """process_queued_saves should succeed if retry succeeds."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})

        # Fail twice, then succeed
        mock_client = AsyncMock(
            side_effect=[
                TimeoutError("Failed"),
                TimeoutError("Failed"),
                {"id": 1},
            ]
        )

        result = await queue.process_queued_saves(mock_client)

        assert result["successful"] == 1
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_process_queued_saves_failed_items_remain_in_queue(self):
        """process_queued_saves should keep failed items in queue after max retries."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Will Fail"})
        queue.add_to_queue({"title": "Will Succeed"})

        # First always fails, second succeeds
        call_count = [0]
        async def mock_save(memory_data):
            call_count[0] += 1
            if memory_data.get("title") == "Will Fail":
                raise TimeoutError("Failed")
            return {"id": 1}

        result = await queue.process_queued_saves(mock_save)

        # Failed item should remain in queue
        remaining = queue.get_queue()
        assert len(remaining) == 1
        assert remaining[0].memory_data["title"] == "Will Fail"

    @pytest.mark.asyncio
    async def test_process_queued_saves_increments_retry_count(self):
        """process_queued_saves should increment retry count on failed items."""
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MAX_RETRY_ATTEMPTS,
            MemorySaveQueue,
        )

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})

        # Always fail
        mock_client = AsyncMock(side_effect=TimeoutError("Failed"))

        await queue.process_queued_saves(mock_client)

        # The remaining item should have incremented retries
        remaining = queue.get_queue()
        assert len(remaining) == 1
        assert remaining[0].retries == MAX_RETRY_ATTEMPTS


class TestProcessQueuedSavesRemoveProcessed:
    """Test that processed entries are removed from queue (Task 5)."""

    @pytest.mark.asyncio
    async def test_process_queued_saves_removes_successful_entries(self):
        """process_queued_saves should remove only successful entries."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Success 1"})
        queue.add_to_queue({"title": "Fail"})
        queue.add_to_queue({"title": "Success 2"})

        async def mock_save(memory_data):
            if memory_data.get("title") == "Fail":
                raise TimeoutError("Failed")
            return {"id": 1}

        await queue.process_queued_saves(mock_save)

        remaining = queue.get_queue()
        assert len(remaining) == 1
        assert remaining[0].memory_data["title"] == "Fail"

    @pytest.mark.asyncio
    async def test_process_queued_saves_returns_total_processed(self):
        """process_queued_saves should return total items attempted."""
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        queue = MemorySaveQueue()
        queue.add_to_queue({"title": "Memory 1"})
        queue.add_to_queue({"title": "Memory 2"})
        queue.add_to_queue({"title": "Memory 3"})

        mock_client = AsyncMock(return_value={"id": 1})

        result = await queue.process_queued_saves(mock_client)

        assert result["total"] == 3
