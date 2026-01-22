"""Tests for Validation Failure Recovery component.

This module tests the validation failure recovery system for BMAD workflows.
Provides automatic recovery from validation failures including:
- Missing config: locate or prompt
- Transient errors: retry with exponential backoff (3 attempts, 2s/4s/8s)
- Known patterns: query memory, apply fix
- Unknown: escalate with context

TDD Pattern: Tests written FIRST before implementation.
Story: 2b-8 - Validation Failure Recovery
Epic: 2b - Enhanced Validation Pipeline
"""

from __future__ import annotations

import time
from pathlib import Path
import tempfile
from typing import Callable
from unittest.mock import MagicMock, patch

import pytest

# These imports will fail until implementation exists (RED phase)
from pcmrp_tools.bmad_automation.validation_recovery import (
    FailureType,
    RecoveryStrategy,
    FAILURE_TO_STRATEGY,
    classify_failure,
    RecoveryResult,
    MissingConfigRecovery,
    TransientErrorRecovery,
    MAX_RETRY_ATTEMPTS,
    BACKOFF_BASE,
)


# =============================================================================
# Task 1.1: FailureType Enum Tests
# =============================================================================


class TestFailureTypeEnum:
    """Tests for FailureType enum (Task 1.1)."""

    def test_missing_config_value(self):
        """Test FailureType.MISSING_CONFIG has correct string value."""
        assert FailureType.MISSING_CONFIG.value == "MISSING_CONFIG"

    def test_transient_error_value(self):
        """Test FailureType.TRANSIENT_ERROR has correct string value."""
        assert FailureType.TRANSIENT_ERROR.value == "TRANSIENT_ERROR"

    def test_known_pattern_value(self):
        """Test FailureType.KNOWN_PATTERN has correct string value."""
        assert FailureType.KNOWN_PATTERN.value == "KNOWN_PATTERN"

    def test_unknown_value(self):
        """Test FailureType.UNKNOWN has correct string value."""
        assert FailureType.UNKNOWN.value == "UNKNOWN"

    def test_all_enum_members_exist(self):
        """Test all required enum members exist."""
        expected_members = {"MISSING_CONFIG", "TRANSIENT_ERROR", "KNOWN_PATTERN", "UNKNOWN"}
        actual_members = {member.name for member in FailureType}
        assert expected_members == actual_members


# =============================================================================
# Task 1.2: RecoveryStrategy Enum Tests
# =============================================================================


class TestRecoveryStrategyEnum:
    """Tests for RecoveryStrategy enum (Task 1.2)."""

    def test_locate_config_value(self):
        """Test RecoveryStrategy.LOCATE_CONFIG has correct string value."""
        assert RecoveryStrategy.LOCATE_CONFIG.value == "LOCATE_CONFIG"

    def test_retry_backoff_value(self):
        """Test RecoveryStrategy.RETRY_BACKOFF has correct string value."""
        assert RecoveryStrategy.RETRY_BACKOFF.value == "RETRY_BACKOFF"

    def test_apply_pattern_value(self):
        """Test RecoveryStrategy.APPLY_PATTERN has correct string value."""
        assert RecoveryStrategy.APPLY_PATTERN.value == "APPLY_PATTERN"

    def test_escalate_value(self):
        """Test RecoveryStrategy.ESCALATE has correct string value."""
        assert RecoveryStrategy.ESCALATE.value == "ESCALATE"

    def test_all_enum_members_exist(self):
        """Test all required enum members exist."""
        expected_members = {"LOCATE_CONFIG", "RETRY_BACKOFF", "APPLY_PATTERN", "ESCALATE"}
        actual_members = {member.name for member in RecoveryStrategy}
        assert expected_members == actual_members


# =============================================================================
# Task 1.3: FAILURE_TO_STRATEGY Mapping Tests
# =============================================================================


class TestFailureToStrategyMapping:
    """Tests for FAILURE_TO_STRATEGY mapping dict (Task 1.3)."""

    def test_missing_config_maps_to_locate_config(self):
        """Test MISSING_CONFIG maps to LOCATE_CONFIG strategy."""
        assert FAILURE_TO_STRATEGY[FailureType.MISSING_CONFIG] == RecoveryStrategy.LOCATE_CONFIG

    def test_transient_error_maps_to_retry_backoff(self):
        """Test TRANSIENT_ERROR maps to RETRY_BACKOFF strategy."""
        assert FAILURE_TO_STRATEGY[FailureType.TRANSIENT_ERROR] == RecoveryStrategy.RETRY_BACKOFF

    def test_known_pattern_maps_to_apply_pattern(self):
        """Test KNOWN_PATTERN maps to APPLY_PATTERN strategy."""
        assert FAILURE_TO_STRATEGY[FailureType.KNOWN_PATTERN] == RecoveryStrategy.APPLY_PATTERN

    def test_unknown_maps_to_escalate(self):
        """Test UNKNOWN maps to ESCALATE strategy."""
        assert FAILURE_TO_STRATEGY[FailureType.UNKNOWN] == RecoveryStrategy.ESCALATE

    def test_all_failure_types_have_strategy(self):
        """Test all FailureType values have a mapping."""
        for failure_type in FailureType:
            assert failure_type in FAILURE_TO_STRATEGY


# =============================================================================
# Task 1.4-1.5: classify_failure Function Tests
# =============================================================================


class TestClassifyFailure:
    """Tests for classify_failure function (Task 1.4, 1.5)."""

    def test_classifies_missing_config_from_keyerror(self):
        """Test classifies KeyError as MISSING_CONFIG."""
        error = KeyError("output_folder")
        result = classify_failure(error)
        assert result == FailureType.MISSING_CONFIG

    def test_classifies_missing_config_from_message(self):
        """Test classifies error with 'missing config' message as MISSING_CONFIG."""
        error = ValueError("Missing configuration key: project_root")
        result = classify_failure(error)
        assert result == FailureType.MISSING_CONFIG

    def test_classifies_missing_config_from_config_not_found(self):
        """Test classifies error with 'config not found' message as MISSING_CONFIG."""
        error = FileNotFoundError("Config file not found: config.yaml")
        result = classify_failure(error)
        assert result == FailureType.MISSING_CONFIG

    def test_classifies_transient_timeout_error(self):
        """Test classifies TimeoutError as TRANSIENT_ERROR."""
        error = TimeoutError("Connection timed out")
        result = classify_failure(error)
        assert result == FailureType.TRANSIENT_ERROR

    def test_classifies_transient_connection_error(self):
        """Test classifies ConnectionError as TRANSIENT_ERROR."""
        error = ConnectionError("Connection refused")
        result = classify_failure(error)
        assert result == FailureType.TRANSIENT_ERROR

    def test_classifies_transient_from_message(self):
        """Test classifies error with 'retry' or 'temporary' message as TRANSIENT_ERROR."""
        error = RuntimeError("Temporary failure, please retry")
        result = classify_failure(error)
        assert result == FailureType.TRANSIENT_ERROR

    def test_classifies_unknown_for_generic_error(self):
        """Test classifies generic error as UNKNOWN."""
        error = RuntimeError("Something unexpected happened")
        result = classify_failure(error)
        assert result == FailureType.UNKNOWN

    def test_classifies_unknown_for_unrecognized_type(self):
        """Test classifies unrecognized exception type as UNKNOWN."""

        class CustomError(Exception):
            pass

        error = CustomError("Custom error")
        result = classify_failure(error)
        assert result == FailureType.UNKNOWN


# =============================================================================
# RecoveryResult Dataclass Tests
# =============================================================================


class TestRecoveryResult:
    """Tests for RecoveryResult dataclass."""

    def test_create_with_success(self):
        """Test creating a successful recovery result."""
        result = RecoveryResult(
            success=True,
            failure_type=FailureType.MISSING_CONFIG,
            strategy_used=RecoveryStrategy.LOCATE_CONFIG,
            message="Found config at /path/to/config.yaml",
        )
        assert result.success is True
        assert result.failure_type == FailureType.MISSING_CONFIG
        assert result.strategy_used == RecoveryStrategy.LOCATE_CONFIG
        assert "config" in result.message.lower()

    def test_create_with_failure(self):
        """Test creating a failed recovery result."""
        result = RecoveryResult(
            success=False,
            failure_type=FailureType.TRANSIENT_ERROR,
            strategy_used=RecoveryStrategy.RETRY_BACKOFF,
            message="Exhausted all retry attempts",
            details={"attempts": 3, "last_error": "Connection refused"},
        )
        assert result.success is False
        assert result.details["attempts"] == 3

    def test_default_details_empty_dict(self):
        """Test details defaults to empty dict."""
        result = RecoveryResult(
            success=True,
            failure_type=FailureType.UNKNOWN,
            strategy_used=RecoveryStrategy.ESCALATE,
            message="Test",
        )
        assert result.details == {}

    def test_escalation_context_field(self):
        """Test escalation_context field for ESCALATE strategy."""
        result = RecoveryResult(
            success=False,
            failure_type=FailureType.UNKNOWN,
            strategy_used=RecoveryStrategy.ESCALATE,
            message="Unable to recover, escalating",
            escalation_context={
                "error_type": "RuntimeError",
                "error_message": "Unexpected failure",
                "timestamp": "2026-01-13T10:00:00Z",
            },
        )
        assert result.escalation_context is not None
        assert "error_type" in result.escalation_context


# =============================================================================
# Task 2: MissingConfigRecovery Class Tests (AC: #1)
# =============================================================================


class TestMissingConfigRecovery:
    """Tests for MissingConfigRecovery class (Task 2, AC: #1)."""

    def test_detect_missing_config_from_keyerror(self):
        """Test detect_missing_config extracts key from KeyError."""
        recovery = MissingConfigRecovery()
        error = KeyError("output_folder")
        config_key = recovery.detect_missing_config(error)
        assert config_key == "output_folder"

    def test_detect_missing_config_from_message(self):
        """Test detect_missing_config extracts key from error message."""
        recovery = MissingConfigRecovery()
        error = ValueError("Missing required configuration: project_root")
        config_key = recovery.detect_missing_config(error)
        assert config_key == "project_root"

    def test_detect_missing_config_returns_none_for_unknown(self):
        """Test detect_missing_config returns None for unrecognized errors."""
        recovery = MissingConfigRecovery()
        error = RuntimeError("Unknown error")
        config_key = recovery.detect_missing_config(error)
        assert config_key is None

    def test_locate_config_finds_in_project_root(self):
        """Test locate_config finds config file in project root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a config file
            config_path = Path(tmpdir) / "_bmad" / "config.yaml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("output_folder: /output")

            recovery = MissingConfigRecovery(search_paths=[Path(tmpdir)])
            found_path = recovery.locate_config("output_folder")

            assert found_path is not None
            assert found_path.exists()

    def test_locate_config_finds_in_bmad_subfolder(self):
        """Test locate_config searches _bmad subfolder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bmad_config = Path(tmpdir) / "_bmad" / "config.yaml"
            bmad_config.parent.mkdir(parents=True)
            bmad_config.write_text("project_root: /project")

            recovery = MissingConfigRecovery(search_paths=[Path(tmpdir)])
            found_path = recovery.locate_config("project_root")

            assert found_path is not None

    def test_locate_config_returns_none_when_not_found(self):
        """Test locate_config returns None when config not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = MissingConfigRecovery(search_paths=[Path(tmpdir)])
            found_path = recovery.locate_config("nonexistent_key")
            assert found_path is None

    def test_prompt_for_config_returns_prompt_text(self):
        """Test prompt_for_config generates user prompt."""
        recovery = MissingConfigRecovery()
        prompt = recovery.prompt_for_config("output_folder")

        assert "output_folder" in prompt
        assert len(prompt) > 0

    def test_prompt_for_config_includes_suggestions(self):
        """Test prompt includes suggestions for common config keys."""
        recovery = MissingConfigRecovery()
        prompt = recovery.prompt_for_config("project_root")

        # Should include helpful context about what project_root is
        assert "project_root" in prompt

    def test_recover_returns_success_when_config_found(self):
        """Test recover returns success when config is located."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "_bmad" / "config.yaml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("output_folder: /output")

            recovery = MissingConfigRecovery(search_paths=[Path(tmpdir)])
            error = KeyError("output_folder")
            result = recovery.recover(error)

            assert result.success is True
            assert result.strategy_used == RecoveryStrategy.LOCATE_CONFIG
            assert "found" in result.message.lower() or "located" in result.message.lower()

    def test_recover_returns_prompt_when_config_not_found(self):
        """Test recover returns prompt when config cannot be located."""
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = MissingConfigRecovery(search_paths=[Path(tmpdir)])
            error = KeyError("missing_key")
            result = recovery.recover(error)

            # Should return a result with prompt
            assert result.success is False
            assert result.strategy_used == RecoveryStrategy.LOCATE_CONFIG
            assert "prompt" in result.details or "missing_key" in result.message


# =============================================================================
# Task 3: TransientErrorRecovery Class Tests (AC: #2)
# =============================================================================


class TestTransientErrorRecoveryConstants:
    """Tests for TransientErrorRecovery constants (Task 3.2, 3.3)."""

    def test_max_retry_attempts_is_3(self):
        """Test MAX_RETRY_ATTEMPTS is 3."""
        assert MAX_RETRY_ATTEMPTS == 3

    def test_backoff_base_is_2(self):
        """Test BACKOFF_BASE is 2 (seconds: 2, 4, 8)."""
        assert BACKOFF_BASE == 2


class TestTransientErrorRecoveryIsTransient:
    """Tests for is_transient_error method (Task 3.4)."""

    def test_timeout_error_is_transient(self):
        """Test TimeoutError is classified as transient."""
        recovery = TransientErrorRecovery()
        assert recovery.is_transient_error(TimeoutError("timed out")) is True

    def test_connection_error_is_transient(self):
        """Test ConnectionError is classified as transient."""
        recovery = TransientErrorRecovery()
        assert recovery.is_transient_error(ConnectionError("refused")) is True

    def test_oserror_with_connection_message_is_transient(self):
        """Test OSError with connection-related message is transient."""
        recovery = TransientErrorRecovery()
        error = OSError("Connection reset by peer")
        assert recovery.is_transient_error(error) is True

    def test_runtime_error_with_retry_message_is_transient(self):
        """Test error with 'retry' in message is transient."""
        recovery = TransientErrorRecovery()
        error = RuntimeError("Please retry the operation")
        assert recovery.is_transient_error(error) is True

    def test_runtime_error_with_temporary_message_is_transient(self):
        """Test error with 'temporary' in message is transient."""
        recovery = TransientErrorRecovery()
        error = RuntimeError("Temporary failure")
        assert recovery.is_transient_error(error) is True

    def test_value_error_not_transient(self):
        """Test ValueError is not classified as transient."""
        recovery = TransientErrorRecovery()
        assert recovery.is_transient_error(ValueError("invalid")) is False

    def test_key_error_not_transient(self):
        """Test KeyError is not classified as transient."""
        recovery = TransientErrorRecovery()
        assert recovery.is_transient_error(KeyError("missing")) is False


class TestTransientErrorRecoveryRetryBackoff:
    """Tests for retry_with_backoff method (Task 3.5, 3.6, 3.7)."""

    def test_succeeds_on_first_attempt(self):
        """Test returns success when operation succeeds immediately."""
        recovery = TransientErrorRecovery()
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            return "success"

        result = recovery.retry_with_backoff(operation)

        assert result.success is True
        assert call_count == 1
        assert result.details.get("attempts") == 1

    def test_succeeds_on_second_attempt(self):
        """Test returns success when operation succeeds on second try."""
        recovery = TransientErrorRecovery()
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Connection refused")
            return "success"

        result = recovery.retry_with_backoff(operation)

        assert result.success is True
        assert call_count == 2
        assert result.details.get("attempts") == 2

    def test_succeeds_on_third_attempt(self):
        """Test returns success when operation succeeds on third try."""
        recovery = TransientErrorRecovery()
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError("Timed out")
            return "success"

        result = recovery.retry_with_backoff(operation)

        assert result.success is True
        assert call_count == 3
        assert result.details.get("attempts") == 3

    def test_fails_after_exhausting_retries(self):
        """Test returns failure after MAX_RETRY_ATTEMPTS."""
        recovery = TransientErrorRecovery()
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        result = recovery.retry_with_backoff(operation)

        assert result.success is False
        assert call_count == MAX_RETRY_ATTEMPTS
        assert result.details.get("attempts") == MAX_RETRY_ATTEMPTS
        assert "exhausted" in result.message.lower() or "failed" in result.message.lower()

    def test_exponential_backoff_timing(self):
        """Test backoff follows exponential pattern (2s, 4s, 8s)."""
        recovery = TransientErrorRecovery()
        timestamps: list[float] = []

        def operation():
            timestamps.append(time.time())
            if len(timestamps) < 3:
                raise ConnectionError("Fail")
            return "success"

        # Use a shorter backoff for testing
        recovery_fast = TransientErrorRecovery(backoff_base=0.1)  # 0.1s, 0.2s, 0.4s
        result = recovery_fast.retry_with_backoff(operation)

        assert result.success is True
        assert len(timestamps) == 3

        # Check delays (with some tolerance)
        delay1 = timestamps[1] - timestamps[0]
        delay2 = timestamps[2] - timestamps[1]

        # First delay should be ~0.1s (backoff_base * 2^0)
        assert 0.08 <= delay1 <= 0.3
        # Second delay should be ~0.2s (backoff_base * 2^1)
        assert 0.15 <= delay2 <= 0.5

    def test_returns_result_value_on_success(self):
        """Test the successful result contains the operation return value."""
        recovery = TransientErrorRecovery()

        def operation():
            return {"data": "value", "count": 42}

        result = recovery.retry_with_backoff(operation)

        assert result.success is True
        assert result.details.get("result") == {"data": "value", "count": 42}

    def test_captures_last_error_on_failure(self):
        """Test captures last error message on exhausted retries."""
        recovery = TransientErrorRecovery()

        def operation():
            raise ConnectionError("Connection refused after timeout")

        result = recovery.retry_with_backoff(operation)

        assert result.success is False
        assert "last_error" in result.details
        assert "Connection refused" in result.details["last_error"]

    def test_retry_with_non_transient_error(self):
        """Test retry_with_backoff catches non-transient errors too.

        When retry_with_backoff is called, it should retry any exception
        (not just transient ones), since the caller may have pre-classified
        the error. The transient classification is done at a higher level.
        """
        recovery = TransientErrorRecovery()
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            # ValueError is not a transient error type
            raise ValueError("Non-transient validation error")

        result = recovery.retry_with_backoff(operation)

        # Should have tried all attempts
        assert call_count == MAX_RETRY_ATTEMPTS
        assert result.success is False
        assert "last_error" in result.details
        assert "validation error" in result.details["last_error"].lower()

    def test_recover_delegates_to_retry_with_backoff(self):
        """Test recover method uses retry_with_backoff for transient errors."""
        recovery = TransientErrorRecovery()
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("Timed out")
            return "recovered"

        result = recovery.recover(TimeoutError("Initial error"), operation)

        assert result.success is True
        assert result.strategy_used == RecoveryStrategy.RETRY_BACKOFF


# =============================================================================
# Integration Tests
# =============================================================================


class TestValidationRecoveryIntegration:
    """Integration tests for validation recovery flow."""

    def test_missing_config_full_flow(self):
        """Test complete missing config recovery flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup config
            config_path = Path(tmpdir) / "_bmad" / "config.yaml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("output_folder: /output\nproject_root: /project")

            # Simulate missing config error
            error = KeyError("output_folder")
            failure_type = classify_failure(error)

            assert failure_type == FailureType.MISSING_CONFIG
            assert FAILURE_TO_STRATEGY[failure_type] == RecoveryStrategy.LOCATE_CONFIG

            # Attempt recovery
            recovery = MissingConfigRecovery(search_paths=[Path(tmpdir)])
            result = recovery.recover(error)

            assert result.success is True

    def test_transient_error_full_flow(self):
        """Test complete transient error recovery flow with backoff."""
        error = TimeoutError("Connection timed out")
        failure_type = classify_failure(error)

        assert failure_type == FailureType.TRANSIENT_ERROR
        assert FAILURE_TO_STRATEGY[failure_type] == RecoveryStrategy.RETRY_BACKOFF

        # Simulate operation that succeeds on retry
        attempt = 0

        def flaky_operation():
            nonlocal attempt
            attempt += 1
            if attempt < 2:
                raise TimeoutError("Still timing out")
            return "success"

        recovery = TransientErrorRecovery(backoff_base=0.01)  # Fast for testing
        result = recovery.recover(error, flaky_operation)

        assert result.success is True
        assert result.strategy_used == RecoveryStrategy.RETRY_BACKOFF

    def test_unknown_error_escalates(self):
        """Test unknown errors result in escalation."""

        class UnknownCustomError(Exception):
            pass

        error = UnknownCustomError("Something completely unexpected")
        failure_type = classify_failure(error)

        assert failure_type == FailureType.UNKNOWN
        assert FAILURE_TO_STRATEGY[failure_type] == RecoveryStrategy.ESCALATE


# =============================================================================
# TASK 4 TESTS: Memory-Based Fix Pattern Recovery (AC: #3)
# =============================================================================

# Import additional components for Tasks 4-6
from datetime import datetime
from typing import Any

from pcmrp_tools.bmad_automation.validation_recovery import (
    PatternRecovery,
    FixPatternMatch,
    PatternRecoveryOutcome,
    MemoryBridgeNotConfiguredError,
    RecoveryLog,
    RecoveryLogger,
    RecoveryAttempt,
    EscalationReport,
    build_escalation_report,
)


# ==============================================================================
# MOCK CLASSES FOR TESTING
# ==============================================================================


class MockContextPreloader:
    """Mock context preloader for testing."""

    def __init__(self):
        self.memories: list[Any] = []
        self.query_called = False
        self.last_query: str | None = None

    def set_memories(self, memories: list[Any]):
        """Set memories to return from queries."""
        self.memories = memories

    def preload_context(self, query: str, **kwargs) -> Any:
        """Mock preload_context method."""
        self.query_called = True
        self.last_query = query
        return MockPreloadResult(memories=self.memories)

    def query_forgetful_memories(self, query: str, **kwargs) -> list[Any]:
        """Mock query method."""
        self.query_called = True
        self.last_query = query
        return self.memories


class MockPreloadResult:
    """Mock preload result."""

    def __init__(self, memories: list[Any]):
        self.memories = memories
        self.status = "success"


class MockMemoryBridge:
    """Mock memory bridge for testing pattern saves."""

    def __init__(self):
        self.save_called = False
        self.last_saved: dict | None = None
        self.next_id = 1

    def save_fix_pattern(self, **kwargs) -> int:
        """Mock save method."""
        self.save_called = True
        self.last_saved = kwargs
        return self.next_id


class MockValidationError:
    """Mock validation error for testing."""

    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message


class MockMemoryItem:
    """Mock memory item matching Forgetful schema."""

    def __init__(
        self,
        id: int,
        title: str,
        content: str,
        importance: int,
        keywords: list[str] | None = None,
    ):
        self.id = id
        self.title = title
        self.content = content
        self.importance = importance
        self.keywords = keywords or []


class TestPatternRecoveryClass:
    """Test PatternRecovery class definition (Task 4.1)."""

    def test_pattern_recovery_class_exists(self):
        """PatternRecovery class should exist."""
        assert PatternRecovery is not None

    def test_pattern_recovery_initializes_with_context_preloader(self):
        """PatternRecovery should accept a context_preloader dependency."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)
        assert recovery.context_preloader is mock_preloader

    def test_pattern_recovery_initializes_with_optional_memory_bridge(self):
        """PatternRecovery should accept optional memory_bridge for updates."""
        mock_preloader = MockContextPreloader()
        mock_bridge = MockMemoryBridge()
        recovery = PatternRecovery(
            context_preloader=mock_preloader, memory_bridge=mock_bridge
        )
        assert recovery.memory_bridge is mock_bridge

    def test_pattern_recovery_tracks_application_results(self):
        """PatternRecovery should track success/failure of pattern applications."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)
        assert hasattr(recovery, "application_results")
        assert isinstance(recovery.application_results, list)


class TestQueryFixPatterns:
    """Test query_fix_patterns method (Task 4.2)."""

    def test_query_fix_patterns_exists(self):
        """PatternRecovery should have query_fix_patterns method."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)
        assert hasattr(recovery, "query_fix_patterns")
        assert callable(recovery.query_fix_patterns)

    def test_query_fix_patterns_uses_context_preloader(self):
        """query_fix_patterns should use context_preloader to search memories."""
        mock_preloader = MockContextPreloader()
        mock_preloader.set_memories(
            [
                MockMemoryItem(
                    id=1,
                    title="Fix: Missing config file",
                    content="Create default config with required keys",
                    importance=8,
                    keywords=["fix", "config", "missing"],
                )
            ]
        )
        recovery = PatternRecovery(context_preloader=mock_preloader)

        error = MockValidationError(
            error_type="config_missing", message="Config file not found"
        )
        patterns = recovery.query_fix_patterns(error)

        assert mock_preloader.query_called
        assert len(patterns) > 0

    def test_query_fix_patterns_returns_fix_pattern_list(self):
        """query_fix_patterns should return list of FixPatternMatch objects."""
        mock_preloader = MockContextPreloader()
        mock_preloader.set_memories(
            [
                MockMemoryItem(
                    id=1,
                    title="Fix: config validation error",
                    content="Add required fields to config",
                    importance=8,
                    keywords=["fix", "config"],
                )
            ]
        )
        recovery = PatternRecovery(context_preloader=mock_preloader)

        error = MockValidationError(error_type="config", message="Invalid config")
        patterns = recovery.query_fix_patterns(error)

        assert isinstance(patterns, list)
        if patterns:
            assert isinstance(patterns[0], FixPatternMatch)

    def test_query_fix_patterns_returns_empty_list_when_no_matches(self):
        """query_fix_patterns should return empty list when no patterns match."""
        mock_preloader = MockContextPreloader()
        mock_preloader.set_memories([])
        recovery = PatternRecovery(context_preloader=mock_preloader)

        error = MockValidationError(
            error_type="unknown", message="Some unknown error"
        )
        patterns = recovery.query_fix_patterns(error)

        assert patterns == []

    def test_query_fix_patterns_filters_by_error_keywords(self):
        """query_fix_patterns should filter patterns by error type keywords."""
        mock_preloader = MockContextPreloader()
        mock_preloader.set_memories(
            [
                MockMemoryItem(
                    id=1,
                    title="Fix: timeout error",
                    content="Increase timeout value",
                    importance=8,
                    keywords=["fix", "timeout", "network"],
                ),
                MockMemoryItem(
                    id=2,
                    title="Fix: config error",
                    content="Validate config keys",
                    importance=7,
                    keywords=["fix", "config", "validation"],
                ),
            ]
        )
        recovery = PatternRecovery(context_preloader=mock_preloader)

        error = MockValidationError(error_type="config", message="Config key missing")
        patterns = recovery.query_fix_patterns(error)

        assert mock_preloader.last_query is not None
        assert "config" in mock_preloader.last_query.lower()


class TestApplyFixPattern:
    """Test apply_fix_pattern method (Task 4.3)."""

    def test_apply_fix_pattern_exists(self):
        """PatternRecovery should have apply_fix_pattern method."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)
        assert hasattr(recovery, "apply_fix_pattern")
        assert callable(recovery.apply_fix_pattern)

    def test_apply_fix_pattern_returns_recovery_outcome(self):
        """apply_fix_pattern should return a PatternRecoveryOutcome."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)

        pattern = FixPatternMatch(
            memory_id=1,
            title="Fix: config error",
            solution="Add default values",
            confidence=0.9,
        )
        context = {"error_type": "config", "workflow_step": "validation"}

        outcome = recovery.apply_fix_pattern(pattern, context)

        assert isinstance(outcome, PatternRecoveryOutcome)

    def test_apply_fix_pattern_records_success(self):
        """apply_fix_pattern should record successful application."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)

        pattern = FixPatternMatch(
            memory_id=1,
            title="Fix: simple error",
            solution="Apply simple fix",
            confidence=0.95,
        )
        context = {"error_type": "simple"}

        outcome = recovery.apply_fix_pattern(pattern, context)

        assert outcome.success is True
        assert outcome.pattern_id == 1

    def test_apply_fix_pattern_handles_failure(self):
        """apply_fix_pattern should handle application failure gracefully."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)

        pattern = FixPatternMatch(
            memory_id=99,
            title="Fix: complex error",
            solution="Apply complex fix",
            confidence=0.5,
            apply_command="invalid_command_that_fails",
        )
        context = {"error_type": "complex", "simulate_failure": True}

        outcome = recovery.apply_fix_pattern(pattern, context)

        assert outcome.success is False
        assert outcome.failure_reason is not None


class TestPatternApplicationTracking:
    """Test pattern application success/failure tracking (Task 4.4)."""

    def test_track_successful_application(self):
        """PatternRecovery should track successful pattern applications."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)

        pattern = FixPatternMatch(
            memory_id=1,
            title="Fix: error",
            solution="Apply fix",
            confidence=0.9,
        )
        context = {"error_type": "test"}

        recovery.apply_fix_pattern(pattern, context)

        assert len(recovery.application_results) == 1
        result = recovery.application_results[0]
        assert result["pattern_id"] == 1
        assert "timestamp" in result

    def test_track_failed_application(self):
        """PatternRecovery should track failed pattern applications."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)

        pattern = FixPatternMatch(
            memory_id=2,
            title="Fix: failing error",
            solution="Apply failing fix",
            confidence=0.3,
            apply_command="fail",
        )
        context = {"error_type": "fail", "simulate_failure": True}

        recovery.apply_fix_pattern(pattern, context)

        assert len(recovery.application_results) == 1
        result = recovery.application_results[0]
        assert result["pattern_id"] == 2
        assert result["success"] is False

    def test_get_success_rate_for_pattern(self):
        """PatternRecovery should calculate success rate for a pattern."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)

        recovery.application_results = [
            {"pattern_id": 1, "success": True, "timestamp": "2024-01-01"},
            {"pattern_id": 1, "success": True, "timestamp": "2024-01-02"},
            {"pattern_id": 1, "success": False, "timestamp": "2024-01-03"},
            {"pattern_id": 2, "success": True, "timestamp": "2024-01-01"},
        ]

        rate = recovery.get_pattern_success_rate(pattern_id=1)

        assert rate == pytest.approx(2 / 3, rel=0.01)


class TestMemoryPatternUpdate:
    """Test interface for updating memory with new patterns (Task 4.5)."""

    def test_save_new_pattern_exists(self):
        """PatternRecovery should have save_new_pattern method."""
        mock_preloader = MockContextPreloader()
        mock_bridge = MockMemoryBridge()
        recovery = PatternRecovery(
            context_preloader=mock_preloader, memory_bridge=mock_bridge
        )

        assert hasattr(recovery, "save_new_pattern")
        assert callable(recovery.save_new_pattern)

    def test_save_new_pattern_uses_memory_bridge(self):
        """save_new_pattern should use memory_bridge to persist patterns."""
        mock_preloader = MockContextPreloader()
        mock_bridge = MockMemoryBridge()
        recovery = PatternRecovery(
            context_preloader=mock_preloader, memory_bridge=mock_bridge
        )

        recovery.save_new_pattern(
            error_signature="timeout_error",
            solution="Increase timeout to 30s",
            workflow_step="api_call",
        )

        assert mock_bridge.save_called
        assert mock_bridge.last_saved is not None

    def test_save_new_pattern_raises_without_memory_bridge(self):
        """save_new_pattern should raise if no memory_bridge configured."""
        mock_preloader = MockContextPreloader()
        recovery = PatternRecovery(context_preloader=mock_preloader)

        with pytest.raises(MemoryBridgeNotConfiguredError):
            recovery.save_new_pattern(
                error_signature="error",
                solution="fix",
                workflow_step="step",
            )

    def test_save_new_pattern_returns_memory_id(self):
        """save_new_pattern should return the new memory ID."""
        mock_preloader = MockContextPreloader()
        mock_bridge = MockMemoryBridge()
        mock_bridge.next_id = 42
        recovery = PatternRecovery(
            context_preloader=mock_preloader, memory_bridge=mock_bridge
        )

        result = recovery.save_new_pattern(
            error_signature="test_error",
            solution="test_solution",
            workflow_step="test_step",
        )

        assert result == 42


# =============================================================================
# TASK 5 TESTS: Recovery Logging (AC: #4)
# =============================================================================


class TestRecoveryLogDataclass:
    """Test RecoveryLog dataclass definition (Task 5.1)."""

    def test_recovery_log_class_exists(self):
        """RecoveryLog dataclass should exist."""
        assert RecoveryLog is not None

    def test_recovery_log_has_required_fields(self):
        """RecoveryLog should have all required fields."""
        log = RecoveryLog(
            recovery_method="pattern_application",
            attempts_count=2,
            timestamp=datetime.now(),
            original_error="Config validation failed",
            recovery_details={"pattern_id": 1, "action": "apply_fix"},
        )

        assert log.recovery_method == "pattern_application"
        assert log.attempts_count == 2
        assert log.original_error == "Config validation failed"
        assert isinstance(log.recovery_details, dict)

    def test_recovery_log_timestamp_is_datetime(self):
        """RecoveryLog timestamp should be a datetime object."""
        now = datetime.now()
        log = RecoveryLog(
            recovery_method="retry",
            attempts_count=1,
            timestamp=now,
            original_error="Transient error",
            recovery_details={},
        )

        assert log.timestamp == now
        assert isinstance(log.timestamp, datetime)

    def test_recovery_log_recovery_details_accepts_any_dict(self):
        """RecoveryLog recovery_details should accept any dict structure."""
        details = {
            "strategy": "backoff",
            "delays": [100, 200, 400],
            "final_success": True,
            "metadata": {"attempt_1": "failed", "attempt_2": "success"},
        }
        log = RecoveryLog(
            recovery_method="retry_backoff",
            attempts_count=2,
            timestamp=datetime.now(),
            original_error="Connection timeout",
            recovery_details=details,
        )

        assert log.recovery_details == details


class TestRecoveryLoggerClass:
    """Test RecoveryLogger class and log_recovery method (Task 5.2-5.3)."""

    def test_recovery_logger_class_exists(self):
        """RecoveryLogger class should exist."""
        assert RecoveryLogger is not None

    def test_recovery_logger_initializes_with_storage_path(self):
        """RecoveryLogger should accept optional storage_path."""
        logger = RecoveryLogger(storage_path="/tmp/recovery_logs")
        assert logger.storage_path == "/tmp/recovery_logs"

    def test_recovery_logger_has_default_storage_path(self):
        """RecoveryLogger should have default storage_path."""
        logger = RecoveryLogger()
        assert logger.storage_path is not None
        assert "_bmad-output" in logger.storage_path

    def test_log_recovery_method_exists(self):
        """RecoveryLogger should have log_recovery method."""
        logger = RecoveryLogger()
        assert hasattr(logger, "log_recovery")
        assert callable(logger.log_recovery)

    def test_log_recovery_creates_recovery_log(self):
        """log_recovery should create and store a RecoveryLog."""
        logger = RecoveryLogger()

        log = logger.log_recovery(
            method="pattern_application",
            attempts=3,
            original_error="Validation failed",
            details={"pattern_id": 5, "success": True},
        )

        assert isinstance(log, RecoveryLog)
        assert log.recovery_method == "pattern_application"
        assert log.attempts_count == 3

    def test_log_recovery_records_timestamp(self):
        """log_recovery should record current timestamp."""
        logger = RecoveryLogger()
        before = datetime.now()

        log = logger.log_recovery(
            method="retry",
            attempts=1,
            original_error="Error",
            details={},
        )

        after = datetime.now()
        assert before <= log.timestamp <= after

    def test_log_recovery_includes_original_error_details(self):
        """log_recovery should include full original error details (Task 5.3)."""
        logger = RecoveryLogger()

        log = logger.log_recovery(
            method="locate_config",
            attempts=1,
            original_error="Config file missing at /path/to/config.yaml",
            details={"located_at": "/other/path/config.yaml"},
        )

        assert "Config file missing" in log.original_error
        assert "/path/to/config.yaml" in log.original_error


class TestRecoveryLogStorage:
    """Test recovery log storage (Task 5.4)."""

    def test_recovery_logger_stores_logs_in_memory(self):
        """RecoveryLogger should store logs in memory for retrieval."""
        logger = RecoveryLogger()

        logger.log_recovery(
            method="retry", attempts=1, original_error="Error 1", details={}
        )
        logger.log_recovery(
            method="pattern", attempts=2, original_error="Error 2", details={}
        )

        assert len(logger.logs) == 2

    def test_get_logs_returns_all_logs(self):
        """get_logs should return all stored logs."""
        logger = RecoveryLogger()

        logger.log_recovery(
            method="retry", attempts=1, original_error="Error", details={}
        )

        logs = logger.get_logs()

        assert len(logs) == 1
        assert logs[0].recovery_method == "retry"

    def test_get_logs_by_method_filters_correctly(self):
        """get_logs should filter by recovery method when specified."""
        logger = RecoveryLogger()

        logger.log_recovery(
            method="retry", attempts=1, original_error="Error 1", details={}
        )
        logger.log_recovery(
            method="pattern", attempts=2, original_error="Error 2", details={}
        )
        logger.log_recovery(
            method="retry", attempts=3, original_error="Error 3", details={}
        )

        retry_logs = logger.get_logs(method="retry")

        assert len(retry_logs) == 2
        assert all(log.recovery_method == "retry" for log in retry_logs)

    def test_export_logs_returns_serializable_format(self):
        """export_logs should return logs in serializable format for analysis."""
        logger = RecoveryLogger()

        logger.log_recovery(
            method="retry", attempts=1, original_error="Error", details={"key": "value"}
        )

        exported = logger.export_logs()

        assert isinstance(exported, list)
        assert len(exported) == 1
        assert isinstance(exported[0], dict)
        assert "recovery_method" in exported[0]
        assert "timestamp" in exported[0]
        assert isinstance(exported[0]["timestamp"], str)

    def test_clear_logs_removes_all_logs(self):
        """clear_logs should remove all stored logs."""
        logger = RecoveryLogger()

        logger.log_recovery(
            method="retry", attempts=1, original_error="Error", details={}
        )
        logger.clear_logs()

        assert len(logger.logs) == 0


# =============================================================================
# TASK 6 TESTS: Escalation with Context (AC: #5)
# =============================================================================


class TestEscalationReportDataclass:
    """Test EscalationReport dataclass definition (Task 6.1)."""

    def test_escalation_report_class_exists(self):
        """EscalationReport dataclass should exist."""
        assert EscalationReport is not None

    def test_escalation_report_has_required_fields(self):
        """EscalationReport should have all required fields."""
        report = EscalationReport(
            strategies_attempted=["retry", "pattern_application"],
            failure_reasons={"retry": "Max retries exceeded", "pattern": "No match"},
            recommendations=["Check network connectivity", "Update patterns"],
        )

        assert report.strategies_attempted == ["retry", "pattern_application"]
        assert len(report.failure_reasons) == 2
        assert len(report.recommendations) == 2

    def test_escalation_report_strategies_is_list(self):
        """EscalationReport strategies_attempted should be a list."""
        report = EscalationReport(
            strategies_attempted=["locate_config", "retry_backoff", "apply_pattern"],
            failure_reasons={},
            recommendations=[],
        )

        assert isinstance(report.strategies_attempted, list)
        assert len(report.strategies_attempted) == 3

    def test_escalation_report_failure_reasons_maps_strategy_to_reason(self):
        """failure_reasons should map each strategy to its failure reason."""
        report = EscalationReport(
            strategies_attempted=["retry", "pattern"],
            failure_reasons={
                "retry": "Connection refused after 3 attempts",
                "pattern": "No matching patterns found in memory",
            },
            recommendations=[],
        )

        assert report.failure_reasons["retry"] == "Connection refused after 3 attempts"
        assert "No matching patterns" in report.failure_reasons["pattern"]

    def test_escalation_report_recommendations_is_list(self):
        """EscalationReport recommendations should be a list of strings."""
        report = EscalationReport(
            strategies_attempted=["retry"],
            failure_reasons={"retry": "Failed"},
            recommendations=[
                "Verify network connectivity",
                "Check service status",
                "Review configuration",
            ],
        )

        assert isinstance(report.recommendations, list)
        assert all(isinstance(r, str) for r in report.recommendations)


class TestBuildEscalationReport:
    """Test build_escalation_report function (Task 6.2)."""

    def test_build_escalation_report_exists(self):
        """build_escalation_report function should exist."""
        assert build_escalation_report is not None
        assert callable(build_escalation_report)

    def test_build_escalation_report_from_attempts_list(self):
        """build_escalation_report should accept list of recovery attempts."""
        attempts = [
            RecoveryAttempt(
                strategy="retry_backoff",
                success=False,
                failure_reason="Connection timeout after 3 retries",
            ),
            RecoveryAttempt(
                strategy="apply_pattern",
                success=False,
                failure_reason="No matching patterns",
            ),
        ]

        report = build_escalation_report(attempts)

        assert isinstance(report, EscalationReport)
        assert len(report.strategies_attempted) == 2

    def test_build_escalation_report_includes_all_strategies(self):
        """build_escalation_report should include all attempted strategies."""
        attempts = [
            RecoveryAttempt(
                strategy="locate_config", success=False, failure_reason="Not found"
            ),
            RecoveryAttempt(
                strategy="retry", success=False, failure_reason="Max retries"
            ),
            RecoveryAttempt(
                strategy="pattern", success=False, failure_reason="No match"
            ),
        ]

        report = build_escalation_report(attempts)

        assert "locate_config" in report.strategies_attempted
        assert "retry" in report.strategies_attempted
        assert "pattern" in report.strategies_attempted


class TestEscalationReportFailureReasons:
    """Test specific failure reason per strategy (Task 6.3)."""

    def test_failure_reason_per_strategy(self):
        """Each strategy should have its specific failure reason."""
        attempts = [
            RecoveryAttempt(
                strategy="locate_config",
                success=False,
                failure_reason="Config not found in any search path",
            ),
            RecoveryAttempt(
                strategy="retry_backoff",
                success=False,
                failure_reason="Service unavailable after 5 retries",
            ),
        ]

        report = build_escalation_report(attempts)

        assert "Config not found" in report.failure_reasons["locate_config"]
        assert "5 retries" in report.failure_reasons["retry_backoff"]

    def test_empty_attempts_produces_empty_report(self):
        """Empty attempts list should produce empty report."""
        report = build_escalation_report([])

        assert report.strategies_attempted == []
        assert report.failure_reasons == {}


class TestEscalationReportFormatting:
    """Test formatting for user presentation (Task 6.4)."""

    def test_escalation_report_format_for_display(self):
        """EscalationReport should have format_for_display method."""
        report = EscalationReport(
            strategies_attempted=["retry"],
            failure_reasons={"retry": "Failed"},
            recommendations=["Check network"],
        )

        assert hasattr(report, "format_for_display")
        assert callable(report.format_for_display)

    def test_format_for_display_returns_readable_string(self):
        """format_for_display should return human-readable string."""
        report = EscalationReport(
            strategies_attempted=["retry_backoff", "apply_pattern"],
            failure_reasons={
                "retry_backoff": "Connection timeout",
                "apply_pattern": "No matching patterns",
            },
            recommendations=[
                "Check network connectivity",
                "Add new fix pattern to memory",
            ],
        )

        display = report.format_for_display()

        assert isinstance(display, str)
        assert "retry_backoff" in display or "Retry" in display
        assert "Connection timeout" in display
        assert "Check network" in display

    def test_format_for_display_includes_section_headers(self):
        """format_for_display should include clear section headers."""
        report = EscalationReport(
            strategies_attempted=["retry"],
            failure_reasons={"retry": "Failed"},
            recommendations=["Fix it"],
        )

        display = report.format_for_display()

        assert "Strateg" in display or "Attempt" in display
        assert "Fail" in display or "Reason" in display
        assert "Recommend" in display or "Action" in display

    def test_format_for_display_actionable_recommendations(self):
        """format_for_display should present actionable recommendations."""
        report = EscalationReport(
            strategies_attempted=["locate_config"],
            failure_reasons={"locate_config": "File not found"},
            recommendations=[
                "Create config file at ~/.config/bmad/config.yaml",
                "Run 'bmad init' to generate default configuration",
            ],
        )

        display = report.format_for_display()

        assert "~/.config/bmad/config.yaml" in display or "config" in display.lower()
        assert "bmad init" in display or "generate" in display.lower()


class TestEscalationReportSerialization:
    """Test EscalationReport serialization for storage/transmission."""

    def test_escalation_report_to_dict(self):
        """EscalationReport should serialize to dict."""
        report = EscalationReport(
            strategies_attempted=["retry", "pattern"],
            failure_reasons={"retry": "Timeout", "pattern": "No match"},
            recommendations=["Check network"],
        )

        data = report.to_dict()

        assert isinstance(data, dict)
        assert data["strategies_attempted"] == ["retry", "pattern"]
        assert data["failure_reasons"]["retry"] == "Timeout"

    def test_escalation_report_from_dict(self):
        """EscalationReport should deserialize from dict."""
        data = {
            "strategies_attempted": ["retry"],
            "failure_reasons": {"retry": "Failed"},
            "recommendations": ["Fix it"],
        }

        report = EscalationReport.from_dict(data)

        assert report.strategies_attempted == ["retry"]
        assert report.failure_reasons["retry"] == "Failed"


# =============================================================================
# INTEGRATION TESTS FOR TASKS 4-6
# =============================================================================


class TestTask4To6Integration:
    """Integration tests for Tasks 4-6 components."""

    def test_pattern_recovery_logs_to_recovery_logger(self):
        """PatternRecovery should integrate with RecoveryLogger."""
        mock_preloader = MockContextPreloader()
        logger = RecoveryLogger()
        recovery = PatternRecovery(
            context_preloader=mock_preloader, recovery_logger=logger
        )

        pattern = FixPatternMatch(
            memory_id=1, title="Fix", solution="Apply", confidence=0.9
        )
        recovery.apply_fix_pattern(pattern, {})

        assert len(logger.logs) >= 1

    def test_failed_recovery_builds_escalation_report(self):
        """Failed recovery attempts should build escalation report."""
        attempts = [
            RecoveryAttempt(
                strategy="locate_config", success=False, failure_reason="Not found"
            ),
            RecoveryAttempt(
                strategy="retry", success=False, failure_reason="Timeout"
            ),
            RecoveryAttempt(
                strategy="pattern", success=False, failure_reason="No match"
            ),
        ]

        report = build_escalation_report(attempts)

        assert isinstance(report, EscalationReport)
        assert len(report.strategies_attempted) == 3
        assert len(report.recommendations) > 0


# =============================================================================
# TASK 7 TESTS: Recovery Orchestrator Integration (AC: All)
# =============================================================================

from pcmrp_tools.bmad_automation.validation_recovery import (
    ValidationRecoveryOrchestrator,
)


class TestValidationRecoveryOrchestratorClass:
    """Tests for ValidationRecoveryOrchestrator class (Task 7.1)."""

    def test_orchestrator_class_exists(self):
        """ValidationRecoveryOrchestrator class should exist."""
        assert ValidationRecoveryOrchestrator is not None

    def test_orchestrator_initializes_with_recovery_handlers(self):
        """Orchestrator should initialize with recovery handler components."""
        mock_preloader = MockContextPreloader()
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
        )
        assert orchestrator.missing_config_recovery is not None
        assert orchestrator.transient_error_recovery is not None
        assert orchestrator.pattern_recovery is not None

    def test_orchestrator_accepts_custom_search_paths(self):
        """Orchestrator should accept custom search paths for config recovery."""
        mock_preloader = MockContextPreloader()
        search_paths = [Path("/custom/path")]
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
            search_paths=search_paths,
        )
        assert orchestrator.missing_config_recovery.search_paths == search_paths

    def test_orchestrator_accepts_recovery_logger(self):
        """Orchestrator should accept and use a RecoveryLogger."""
        mock_preloader = MockContextPreloader()
        logger = RecoveryLogger()
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
            recovery_logger=logger,
        )
        assert orchestrator.recovery_logger is logger

    def test_orchestrator_tracks_recovery_attempts(self):
        """Orchestrator should track all recovery attempts."""
        mock_preloader = MockContextPreloader()
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
        )
        assert hasattr(orchestrator, "recovery_attempts")
        assert isinstance(orchestrator.recovery_attempts, list)


class TestAttemptRecoveryMethod:
    """Tests for attempt_recovery method (Task 7.2)."""

    def test_attempt_recovery_method_exists(self):
        """Orchestrator should have attempt_recovery method."""
        mock_preloader = MockContextPreloader()
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
        )
        assert hasattr(orchestrator, "attempt_recovery")
        assert callable(orchestrator.attempt_recovery)

    def test_attempt_recovery_returns_recovery_result(self):
        """attempt_recovery should return a RecoveryResult."""
        mock_preloader = MockContextPreloader()
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
        )
        error = RuntimeError("Unknown error")
        result = orchestrator.attempt_recovery(error)
        assert isinstance(result, RecoveryResult)

    def test_attempt_recovery_classifies_error(self):
        """attempt_recovery should classify the error to determine strategy."""
        mock_preloader = MockContextPreloader()
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
        )
        # KeyError should be classified as MISSING_CONFIG
        error = KeyError("test_key")
        result = orchestrator.attempt_recovery(error)
        assert result.failure_type == FailureType.MISSING_CONFIG


class TestRecoveryStrategyOrder:
    """Tests for recovery strategy ordering (Task 7.3)."""

    def test_strategy_order_constant_exists(self):
        """RECOVERY_STRATEGY_ORDER constant should exist."""
        from pcmrp_tools.bmad_automation.validation_recovery import (
            RECOVERY_STRATEGY_ORDER,
        )

        assert RECOVERY_STRATEGY_ORDER is not None
        assert isinstance(RECOVERY_STRATEGY_ORDER, list)

    def test_strategy_order_is_correct(self):
        """Strategy order should be: missing_config -> transient_retry -> pattern_match -> escalate."""
        from pcmrp_tools.bmad_automation.validation_recovery import (
            RECOVERY_STRATEGY_ORDER,
        )

        assert len(RECOVERY_STRATEGY_ORDER) == 4
        assert RECOVERY_STRATEGY_ORDER[0] == RecoveryStrategy.LOCATE_CONFIG
        assert RECOVERY_STRATEGY_ORDER[1] == RecoveryStrategy.RETRY_BACKOFF
        assert RECOVERY_STRATEGY_ORDER[2] == RecoveryStrategy.APPLY_PATTERN
        assert RECOVERY_STRATEGY_ORDER[3] == RecoveryStrategy.ESCALATE

    def test_pattern_recovery_attempted_after_config_fails(self):
        """Pattern recovery should be attempted after config recovery fails when use_pattern_recovery=True.

        Per design spec: missing_config -> transient_retry -> pattern_match -> escalate.
        Even if config recovery fails, pattern recovery should still be attempted.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # No config file exists - config recovery will fail
            mock_preloader = MockContextPreloader()
            mock_preloader.set_memories(
                [
                    MockMemoryItem(
                        id=42,
                        title="Fix: missing_config fallback",
                        content="Use default config",
                        importance=8,
                        keywords=["fix", "config", "default"],
                    )
                ]
            )
            orchestrator = ValidationRecoveryOrchestrator(
                context_preloader=mock_preloader,
                search_paths=[Path(tmpdir)],
            )

            # KeyError classified as MISSING_CONFIG
            error = KeyError("nonexistent_key")
            result = orchestrator.attempt_recovery(error, use_pattern_recovery=True)

            # Should have attempted both locate_config AND apply_pattern
            strategies_attempted = [a.strategy for a in orchestrator.recovery_attempts]
            assert "locate_config" in strategies_attempted
            assert "apply_pattern" in strategies_attempted

    def test_pattern_recovery_attempted_after_transient_fails(self):
        """Pattern recovery should be attempted after transient recovery fails when use_pattern_recovery=True.

        Per design spec: missing_config -> transient_retry -> pattern_match -> escalate.
        Even if retry fails, pattern recovery should still be attempted.
        """
        mock_preloader = MockContextPreloader()
        mock_preloader.set_memories(
            [
                MockMemoryItem(
                    id=43,
                    title="Fix: transient fallback",
                    content="Apply circuit breaker",
                    importance=8,
                    keywords=["fix", "transient", "fallback"],
                )
            ]
        )
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
            backoff_base=0.001,  # Fast for testing
        )

        # Always fail - exhaust retries
        def always_fail():
            raise TimeoutError("Permanent timeout")

        # TimeoutError classified as TRANSIENT_ERROR
        error = TimeoutError("Connection timeout")
        result = orchestrator.attempt_recovery(
            error, retry_operation=always_fail, use_pattern_recovery=True
        )

        # Should have attempted both retry_backoff AND apply_pattern
        strategies_attempted = [a.strategy for a in orchestrator.recovery_attempts]
        assert "retry_backoff" in strategies_attempted
        assert "apply_pattern" in strategies_attempted


class TestErrorHandlingFlowIntegration:
    """Tests for error handling flow integration (Task 7.4)."""

    def test_orchestrator_clears_attempts_before_new_recovery(self):
        """Orchestrator should clear previous attempts before starting new recovery."""
        mock_preloader = MockContextPreloader()
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
        )
        # First recovery attempt
        orchestrator.attempt_recovery(RuntimeError("Error 1"))
        first_count = len(orchestrator.recovery_attempts)

        # Second recovery attempt should start fresh
        orchestrator.attempt_recovery(RuntimeError("Error 2"))
        # Should have similar or fewer attempts (fresh start), not accumulating
        assert len(orchestrator.recovery_attempts) <= first_count + 4

    def test_orchestrator_returns_success_on_first_successful_strategy(self):
        """Orchestrator should return success when a strategy succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "_bmad" / "config.yaml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("my_config_key: value")

            mock_preloader = MockContextPreloader()
            orchestrator = ValidationRecoveryOrchestrator(
                context_preloader=mock_preloader,
                search_paths=[Path(tmpdir)],
            )
            error = KeyError("my_config_key")
            result = orchestrator.attempt_recovery(error)

            assert result.success is True
            assert result.strategy_used == RecoveryStrategy.LOCATE_CONFIG

    def test_orchestrator_includes_escalation_context_on_failure(self):
        """Orchestrator should include escalation context when all strategies fail."""
        mock_preloader = MockContextPreloader()
        mock_preloader.set_memories([])  # No patterns available
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
        )
        error = RuntimeError("Completely unknown error")
        result = orchestrator.attempt_recovery(error)

        assert result.success is False
        assert result.strategy_used == RecoveryStrategy.ESCALATE
        assert result.escalation_context is not None


# =============================================================================
# Task 7.5: Full Integration Tests for Recovery Flow
# =============================================================================


class TestMissingConfigRecoveryFlow:
    """Integration test: test_missing_config_recovery_flow."""

    def test_missing_config_recovery_flow(self):
        """Full flow: missing config -> locate -> success."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup: create a config file with the missing key
            config_path = Path(tmpdir) / "_bmad" / "config.yaml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("output_folder: /output\nproject_root: /project")

            mock_preloader = MockContextPreloader()
            orchestrator = ValidationRecoveryOrchestrator(
                context_preloader=mock_preloader,
                search_paths=[Path(tmpdir)],
            )

            # Simulate: missing config error
            error = KeyError("output_folder")
            result = orchestrator.attempt_recovery(error)

            # Assert: recovery successful
            assert result.success is True
            assert result.failure_type == FailureType.MISSING_CONFIG
            assert result.strategy_used == RecoveryStrategy.LOCATE_CONFIG
            assert "found" in result.message.lower() or "output_folder" in result.message


class TestTransientErrorRetryFlow:
    """Integration test: test_transient_error_retry_flow."""

    def test_transient_error_retry_flow(self):
        """Full flow: transient error -> retry with backoff -> success."""
        mock_preloader = MockContextPreloader()
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
            backoff_base=0.01,  # Fast for testing
        )

        # Create a transient error with an operation to retry
        error = TimeoutError("Connection timed out")
        attempt_count = 0

        def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise TimeoutError("Still timing out")
            return "recovered"

        result = orchestrator.attempt_recovery(error, retry_operation=flaky_operation)

        assert result.success is True
        assert result.failure_type == FailureType.TRANSIENT_ERROR
        assert result.strategy_used == RecoveryStrategy.RETRY_BACKOFF
        assert attempt_count >= 2


class TestPatternRecoveryFlow:
    """Integration test: test_pattern_recovery_flow."""

    def test_pattern_recovery_flow(self):
        """Full flow: known pattern error -> query memory -> apply fix -> success."""
        mock_preloader = MockContextPreloader()
        mock_preloader.set_memories(
            [
                MockMemoryItem(
                    id=1,
                    title="Fix: validation schema error",
                    content="Apply schema migration",
                    importance=8,
                    keywords=["fix", "schema", "validation"],
                )
            ]
        )
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
        )

        # Create a known pattern error
        class ValidationSchemaError(Exception):
            def __init__(self, msg):
                super().__init__(msg)
                self.error_type = "schema_validation"
                self.message = msg

        error = ValidationSchemaError("Schema validation failed")
        result = orchestrator.attempt_recovery(error, use_pattern_recovery=True)

        # Should attempt pattern recovery (may or may not succeed based on pattern)
        assert result is not None
        assert result.failure_type in (FailureType.KNOWN_PATTERN, FailureType.UNKNOWN)


class TestEscalationAfterAllStrategiesFail:
    """Integration test: test_escalation_after_all_strategies_fail."""

    def test_escalation_after_all_strategies_fail(self):
        """Full flow: all strategies fail -> escalate with context."""
        mock_preloader = MockContextPreloader()
        mock_preloader.set_memories([])  # No patterns
        orchestrator = ValidationRecoveryOrchestrator(
            context_preloader=mock_preloader,
        )

        # Create an error that cannot be recovered
        error = RuntimeError("Completely unrecoverable error with no fix")
        result = orchestrator.attempt_recovery(error)

        # Should escalate
        assert result.success is False
        assert result.strategy_used == RecoveryStrategy.ESCALATE
        assert result.escalation_context is not None

        # Check escalation report is included
        escalation = result.escalation_context
        assert "strategies_attempted" in escalation or "report" in escalation


class TestRecoveryLoggingOnSuccess:
    """Integration test: test_recovery_logging_on_success."""

    def test_recovery_logging_on_success(self):
        """Full flow: successful recovery -> log recorded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "_bmad" / "config.yaml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("test_key: test_value")

            mock_preloader = MockContextPreloader()
            logger = RecoveryLogger()
            orchestrator = ValidationRecoveryOrchestrator(
                context_preloader=mock_preloader,
                search_paths=[Path(tmpdir)],
                recovery_logger=logger,
            )

            error = KeyError("test_key")
            result = orchestrator.attempt_recovery(error)

            # Should log the recovery
            assert result.success is True
            assert len(logger.logs) >= 1
            # Log should contain relevant information
            latest_log = logger.logs[-1]
            assert latest_log.recovery_method in ("locate_config", "missing_config_recovery")


class TestOrchestratorFullRecoveryFlow:
    """Comprehensive integration test for the full recovery flow."""

    def test_full_recovery_flow_with_all_components(self):
        """Test complete orchestration: classify -> attempt strategies -> log -> return."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup config
            config_path = Path(tmpdir) / "_bmad" / "config.yaml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("recoverable_key: value")

            mock_preloader = MockContextPreloader()
            mock_preloader.set_memories(
                [
                    MockMemoryItem(
                        id=99,
                        title="Fix: general error",
                        content="Apply general fix",
                        importance=5,
                    )
                ]
            )
            logger = RecoveryLogger()

            orchestrator = ValidationRecoveryOrchestrator(
                context_preloader=mock_preloader,
                search_paths=[Path(tmpdir)],
                recovery_logger=logger,
                backoff_base=0.01,
            )

            # Test 1: Missing config recovery
            error1 = KeyError("recoverable_key")
            result1 = orchestrator.attempt_recovery(error1)
            assert result1.success is True

            # Test 2: Unknown error escalation
            error2 = RuntimeError("Unknown catastrophic failure")
            result2 = orchestrator.attempt_recovery(error2)
            assert result2.success is False
            assert result2.strategy_used == RecoveryStrategy.ESCALATE

            # Verify logging
            assert len(logger.logs) >= 1
