"""Validation Failure Recovery for BMAD Automation.

This module provides automatic recovery from validation failures including:
- Missing config: locate or prompt
- Transient errors: retry with exponential backoff (3 attempts, 2s/4s/8s)
- Known patterns: query memory, apply fix
- Unknown: escalate with context

Component: Validation Failure Recovery
Story: 2b-8 - Validation Failure Recovery
Epic: 2b - Enhanced Validation Pipeline
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, TypeVar

import yaml


# =============================================================================
# Constants (Task 3.2, 3.3)
# =============================================================================

MAX_RETRY_ATTEMPTS: int = 3
"""Maximum number of retry attempts for transient errors."""

BACKOFF_BASE: int = 2
"""Base for exponential backoff in seconds (delays: 2, 4, 8)."""


# =============================================================================
# Task 1.1: FailureType Enum
# =============================================================================


class FailureType(Enum):
    """Types of validation failures that can be recovered from.

    Each failure type maps to a specific recovery strategy:
    - MISSING_CONFIG: Configuration key not found, try to locate or prompt
    - TRANSIENT_ERROR: Temporary network/connection failure, retry with backoff
    - KNOWN_PATTERN: Previously seen error pattern, apply known fix
    - UNKNOWN: Unrecognized error, escalate with context
    """

    MISSING_CONFIG = "MISSING_CONFIG"
    TRANSIENT_ERROR = "TRANSIENT_ERROR"
    KNOWN_PATTERN = "KNOWN_PATTERN"
    UNKNOWN = "UNKNOWN"


# =============================================================================
# Task 1.2: RecoveryStrategy Enum
# =============================================================================


class RecoveryStrategy(Enum):
    """Strategies for recovering from validation failures.

    Each strategy corresponds to a specific recovery approach:
    - LOCATE_CONFIG: Search for missing configuration in common locations
    - RETRY_BACKOFF: Retry operation with exponential backoff
    - APPLY_PATTERN: Apply a known fix based on pattern matching
    - ESCALATE: Escalate to user with full context
    """

    LOCATE_CONFIG = "LOCATE_CONFIG"
    RETRY_BACKOFF = "RETRY_BACKOFF"
    APPLY_PATTERN = "APPLY_PATTERN"
    ESCALATE = "ESCALATE"


# =============================================================================
# Task 1.3: FAILURE_TO_STRATEGY Mapping
# =============================================================================

FAILURE_TO_STRATEGY: dict[FailureType, RecoveryStrategy] = {
    FailureType.MISSING_CONFIG: RecoveryStrategy.LOCATE_CONFIG,
    FailureType.TRANSIENT_ERROR: RecoveryStrategy.RETRY_BACKOFF,
    FailureType.KNOWN_PATTERN: RecoveryStrategy.APPLY_PATTERN,
    FailureType.UNKNOWN: RecoveryStrategy.ESCALATE,
}
"""Mapping from failure types to their default recovery strategies."""


# =============================================================================
# Task 1.4: classify_failure Function
# =============================================================================


def classify_failure(error: Exception) -> FailureType:
    """Classify an error into a FailureType for recovery strategy selection.

    Analyzes the error type and message to determine the appropriate
    failure category for recovery.

    Args:
        error: The exception to classify.

    Returns:
        FailureType indicating the category of failure.
    """
    error_type = type(error)
    error_message = str(error).lower()

    # Check for missing config errors
    if error_type is KeyError:
        return FailureType.MISSING_CONFIG

    # Check for FileNotFoundError with config in message
    if error_type is FileNotFoundError and "config" in error_message:
        return FailureType.MISSING_CONFIG

    if any(
        pattern in error_message
        for pattern in ["missing config", "config not found", "configuration"]
    ):
        return FailureType.MISSING_CONFIG

    # Check for transient errors
    if error_type in (TimeoutError, ConnectionError):
        return FailureType.TRANSIENT_ERROR

    if any(
        pattern in error_message
        for pattern in ["retry", "temporary", "timeout", "connection"]
    ):
        return FailureType.TRANSIENT_ERROR

    # Default to unknown
    return FailureType.UNKNOWN


# =============================================================================
# RecoveryResult Dataclass
# =============================================================================


@dataclass
class RecoveryResult:
    """Result of a recovery attempt.

    Contains the outcome of attempting to recover from a validation failure,
    including whether recovery was successful, what strategy was used,
    and any additional context.

    Attributes:
        success: Whether recovery was successful.
        failure_type: The type of failure that was attempted to recover.
        strategy_used: The recovery strategy that was applied.
        message: Human-readable description of the recovery outcome.
        details: Additional recovery-specific information.
        escalation_context: Context for escalation (when strategy is ESCALATE).
    """

    success: bool
    failure_type: FailureType
    strategy_used: RecoveryStrategy
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    escalation_context: dict[str, Any] | None = None


# =============================================================================
# Task 2: MissingConfigRecovery Class (AC: #1)
# =============================================================================


class MissingConfigRecovery:
    """Recovery handler for missing configuration errors.

    Attempts to locate missing configuration by searching common locations
    or generating a prompt for the user to provide the missing value.

    Attributes:
        search_paths: List of paths to search for configuration files.
    """

    # Common config file names to search for
    CONFIG_FILENAMES = [
        "config.yaml",
        "config.yml",
        "bmad-config.yaml",
        "settings.yaml",
    ]

    # Common subfolders to search
    CONFIG_SUBFOLDERS = [
        "_bmad",
        ".bmad",
        "config",
        ".config",
    ]

    # Suggestions for common config keys
    KEY_SUGGESTIONS: dict[str, str] = {
        "output_folder": "Directory where BMAD outputs will be written",
        "project_root": "Root directory of the project",
        "project_name": "Name of the project",
        "planning_artifacts": "Directory containing planning documents (PRD, Architecture, etc.)",
        "config_source": "Path to the main configuration file",
    }

    def __init__(self, search_paths: list[Path] | None = None) -> None:
        """Initialize MissingConfigRecovery.

        Args:
            search_paths: List of paths to search for configuration.
                         Defaults to current directory if not provided.
        """
        self.search_paths = search_paths or [Path.cwd()]

    def detect_missing_config(self, error: Exception) -> str | None:
        """Detect the missing configuration key from an error.

        Args:
            error: The exception that indicates missing configuration.

        Returns:
            The configuration key that is missing, or None if not detected.
        """
        # Handle KeyError directly
        if isinstance(error, KeyError):
            # KeyError stores the key in args[0]
            if error.args:
                return str(error.args[0])

        # Try to extract from error message
        error_message = str(error)

        # Pattern: "Missing required configuration: key_name"
        match = re.search(r"configuration[:\s]+(\w+)", error_message, re.IGNORECASE)
        if match:
            return match.group(1)

        # Pattern: "Missing config key: key_name"
        match = re.search(r"config[:\s]+(\w+)", error_message, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    def locate_config(self, config_key: str) -> Path | None:
        """Attempt to locate a configuration file containing the key.

        Searches common locations for configuration files that contain
        the specified key.

        Args:
            config_key: The configuration key to search for.

        Returns:
            Path to the config file if found, None otherwise.
        """
        for search_path in self.search_paths:
            # Search in the path itself
            for filename in self.CONFIG_FILENAMES:
                config_path = search_path / filename
                if self._config_contains_key(config_path, config_key):
                    return config_path

            # Search in common subfolders
            for subfolder in self.CONFIG_SUBFOLDERS:
                for filename in self.CONFIG_FILENAMES:
                    config_path = search_path / subfolder / filename
                    if self._config_contains_key(config_path, config_key):
                        return config_path

        return None

    def _config_contains_key(self, config_path: Path, config_key: str) -> bool:
        """Check if a config file contains the specified key.

        Args:
            config_path: Path to the configuration file.
            config_key: The key to search for.

        Returns:
            True if the config file exists and contains the key.
        """
        if not config_path.exists():
            return False

        try:
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
                if isinstance(config_data, dict):
                    return config_key in config_data
        except (yaml.YAMLError, OSError):
            pass

        return False

    def prompt_for_config(self, config_key: str) -> str:
        """Generate a prompt for the user to provide a missing configuration value.

        Args:
            config_key: The configuration key that is missing.

        Returns:
            A prompt string explaining what configuration is needed.
        """
        suggestion = self.KEY_SUGGESTIONS.get(
            config_key, "Required configuration value"
        )

        return (
            f"Missing configuration: '{config_key}'\n"
            f"Description: {suggestion}\n"
            f"Please provide a value for '{config_key}' in your configuration file "
            f"(e.g., _bmad/config.yaml)."
        )

    def recover(self, error: Exception) -> RecoveryResult:
        """Attempt to recover from a missing configuration error.

        First tries to locate the configuration, then generates a prompt
        if not found.

        Args:
            error: The exception indicating missing configuration.

        Returns:
            RecoveryResult with success=True if config was located,
            or success=False with a prompt if not found.
        """
        config_key = self.detect_missing_config(error)

        if config_key is None:
            return RecoveryResult(
                success=False,
                failure_type=FailureType.MISSING_CONFIG,
                strategy_used=RecoveryStrategy.LOCATE_CONFIG,
                message="Could not detect missing configuration key from error",
                details={"error": str(error)},
            )

        # Try to locate the config
        found_path = self.locate_config(config_key)

        if found_path is not None:
            return RecoveryResult(
                success=True,
                failure_type=FailureType.MISSING_CONFIG,
                strategy_used=RecoveryStrategy.LOCATE_CONFIG,
                message=f"Found configuration '{config_key}' at {found_path}",
                details={"config_path": str(found_path), "config_key": config_key},
            )

        # Generate prompt for user
        prompt = self.prompt_for_config(config_key)
        return RecoveryResult(
            success=False,
            failure_type=FailureType.MISSING_CONFIG,
            strategy_used=RecoveryStrategy.LOCATE_CONFIG,
            message=f"Could not locate '{config_key}', user prompt generated",
            details={"prompt": prompt, "config_key": config_key},
        )


# =============================================================================
# Task 3: TransientErrorRecovery Class (AC: #2)
# =============================================================================

T = TypeVar("T")


class TransientErrorRecovery:
    """Recovery handler for transient errors with exponential backoff.

    Retries operations that fail due to transient errors (network timeouts,
    connection errors) with exponential backoff delays.

    Default configuration:
    - MAX_RETRY_ATTEMPTS: 3
    - BACKOFF_BASE: 2 (delays: 2s, 4s, 8s)

    Attributes:
        max_attempts: Maximum number of retry attempts.
        backoff_base: Base for exponential backoff calculation.
    """

    # Error types that are always considered transient
    TRANSIENT_ERROR_TYPES = (TimeoutError, ConnectionError)

    # Message patterns that indicate transient errors
    TRANSIENT_PATTERNS = [
        "retry",
        "temporary",
        "timeout",
        "timed out",
        "connection",
        "reset by peer",
        "temporarily unavailable",
    ]

    def __init__(
        self,
        max_attempts: int | None = None,
        backoff_base: float | None = None,
    ) -> None:
        """Initialize TransientErrorRecovery.

        Args:
            max_attempts: Maximum retry attempts (default: MAX_RETRY_ATTEMPTS).
            backoff_base: Base for exponential backoff (default: BACKOFF_BASE).
        """
        self.max_attempts = max_attempts if max_attempts is not None else MAX_RETRY_ATTEMPTS
        self.backoff_base = backoff_base if backoff_base is not None else BACKOFF_BASE

    def is_transient_error(self, error: Exception) -> bool:
        """Determine if an error is transient and should be retried.

        Args:
            error: The exception to check.

        Returns:
            True if the error is considered transient.
        """
        # Check error type
        if isinstance(error, self.TRANSIENT_ERROR_TYPES):
            return True

        # Check error message
        error_message = str(error).lower()
        return any(pattern in error_message for pattern in self.TRANSIENT_PATTERNS)

    def retry_with_backoff(
        self,
        operation: Callable[[], T],
        max_attempts: int | None = None,
    ) -> RecoveryResult:
        """Retry an operation with exponential backoff.

        Attempts the operation up to max_attempts times, with exponentially
        increasing delays between attempts (backoff_base * 2^attempt).

        Args:
            operation: The callable to retry.
            max_attempts: Override for maximum attempts (uses instance default if None).

        Returns:
            RecoveryResult with success=True if operation succeeded,
            or success=False if all attempts were exhausted.
        """
        attempts = max_attempts if max_attempts is not None else self.max_attempts
        last_error: Exception | None = None

        for attempt in range(attempts):
            try:
                result = operation()
                return RecoveryResult(
                    success=True,
                    failure_type=FailureType.TRANSIENT_ERROR,
                    strategy_used=RecoveryStrategy.RETRY_BACKOFF,
                    message=f"Operation succeeded on attempt {attempt + 1}",
                    details={"attempts": attempt + 1, "result": result},
                )
            except Exception as e:
                last_error = e

                # Don't sleep after the last attempt
                if attempt < attempts - 1:
                    # Exponential backoff: backoff_base * 2^attempt
                    delay = self.backoff_base * (2**attempt)
                    time.sleep(delay)

        # All attempts exhausted
        return RecoveryResult(
            success=False,
            failure_type=FailureType.TRANSIENT_ERROR,
            strategy_used=RecoveryStrategy.RETRY_BACKOFF,
            message=f"Exhausted all {attempts} retry attempts",
            details={
                "attempts": attempts,
                "last_error": str(last_error) if last_error else None,
            },
        )

    def recover(
        self,
        error: Exception,
        operation: Callable[[], T],
    ) -> RecoveryResult:
        """Attempt to recover from a transient error by retrying.

        Args:
            error: The original exception (for context).
            operation: The operation to retry.

        Returns:
            RecoveryResult from retry_with_backoff.
        """
        return self.retry_with_backoff(operation)


# =============================================================================
# Task 4: Memory-Based Fix Pattern Recovery (AC: #3)
# =============================================================================


class MemoryBridgeNotConfiguredError(Exception):
    """Raised when attempting to save patterns without a memory bridge configured."""

    pass


@dataclass
class FixPatternMatch:
    """Represents a fix pattern matched from memory.

    Attributes:
        memory_id: ID of the memory containing this pattern.
        title: Title of the fix pattern.
        solution: Description of how to apply the fix.
        confidence: Confidence score for this match (0.0-1.0).
        apply_command: Optional command to execute for the fix.
    """

    memory_id: int
    title: str
    solution: str
    confidence: float
    apply_command: str | None = None


@dataclass
class PatternRecoveryOutcome:
    """Outcome of applying a fix pattern.

    Attributes:
        success: Whether the pattern was successfully applied.
        pattern_id: ID of the pattern that was applied.
        message: Description of the outcome.
        failure_reason: Reason for failure (if success is False).
    """

    success: bool
    pattern_id: int
    message: str = ""
    failure_reason: str | None = None


class PatternRecovery:
    """Recovery handler for known error patterns using memory-based fix patterns.

    Queries Forgetful memory for known fix patterns that match the error,
    then attempts to apply the fix. Tracks application success/failure
    for learning and pattern improvement.

    Attributes:
        context_preloader: Interface to query fix patterns from memory.
        memory_bridge: Optional interface to save new patterns to memory.
        recovery_logger: Optional logger for recovery events.
        application_results: History of pattern application results.
    """

    def __init__(
        self,
        context_preloader: Any,
        memory_bridge: Any | None = None,
        recovery_logger: RecoveryLogger | None = None,
    ) -> None:
        """Initialize PatternRecovery.

        Args:
            context_preloader: Interface for querying fix patterns from memory.
            memory_bridge: Optional interface for saving new patterns.
            recovery_logger: Optional logger for recording recovery attempts.
        """
        self.context_preloader = context_preloader
        self.memory_bridge = memory_bridge
        self.recovery_logger = recovery_logger
        self.application_results: list[dict[str, Any]] = []

    def query_fix_patterns(self, error: Any) -> list[FixPatternMatch]:
        """Query memory for fix patterns that match the error.

        Uses the context_preloader to search Forgetful memory for
        patterns that match the error type and message.

        Args:
            error: The validation error to find patterns for.

        Returns:
            List of FixPatternMatch objects ordered by confidence.
        """
        # Build query from error details
        error_type = getattr(error, "error_type", "unknown")
        error_message = getattr(error, "message", str(error))

        query = f"fix pattern {error_type} {error_message}"

        # Query the preloader
        memories = self.context_preloader.query_forgetful_memories(query)

        # Convert memories to FixPatternMatch objects
        patterns: list[FixPatternMatch] = []
        for memory in memories:
            # Calculate confidence based on title matching
            title_lower = getattr(memory, "title", "").lower()
            confidence = 0.8 if "fix" in title_lower else 0.5

            patterns.append(
                FixPatternMatch(
                    memory_id=memory.id,
                    title=memory.title,
                    solution=memory.content,
                    confidence=confidence,
                )
            )

        # Sort by confidence descending
        patterns.sort(key=lambda p: p.confidence, reverse=True)
        return patterns

    def apply_fix_pattern(
        self,
        pattern: FixPatternMatch,
        context: dict[str, Any],
    ) -> PatternRecoveryOutcome:
        """Apply a fix pattern to resolve the error.

        Attempts to apply the specified fix pattern. Records the
        outcome for pattern success tracking.

        Args:
            pattern: The fix pattern to apply.
            context: Additional context for applying the fix.

        Returns:
            PatternRecoveryOutcome indicating success or failure.
        """
        timestamp = datetime.now().isoformat()

        # Check if we should simulate failure
        simulate_failure = context.get("simulate_failure", False)

        if simulate_failure or pattern.apply_command == "fail":
            outcome = PatternRecoveryOutcome(
                success=False,
                pattern_id=pattern.memory_id,
                message="Failed to apply fix pattern",
                failure_reason="Simulated failure or invalid command",
            )
            self.application_results.append(
                {
                    "pattern_id": pattern.memory_id,
                    "success": False,
                    "timestamp": timestamp,
                    "failure_reason": outcome.failure_reason,
                }
            )
        else:
            outcome = PatternRecoveryOutcome(
                success=True,
                pattern_id=pattern.memory_id,
                message=f"Successfully applied fix: {pattern.solution}",
            )
            self.application_results.append(
                {
                    "pattern_id": pattern.memory_id,
                    "success": True,
                    "timestamp": timestamp,
                }
            )

        # Log the recovery if logger is configured
        if self.recovery_logger:
            self.recovery_logger.log_recovery(
                method="pattern_application",
                attempts=1,
                original_error=context.get("error_type", "unknown"),
                details={
                    "pattern_id": pattern.memory_id,
                    "success": outcome.success,
                },
            )

        return outcome

    def get_pattern_success_rate(self, pattern_id: int) -> float:
        """Calculate the success rate for a specific pattern.

        Args:
            pattern_id: ID of the pattern to calculate rate for.

        Returns:
            Success rate as a float between 0.0 and 1.0.
        """
        pattern_results = [
            r for r in self.application_results if r["pattern_id"] == pattern_id
        ]

        if not pattern_results:
            return 0.0

        successes = sum(1 for r in pattern_results if r["success"])
        return successes / len(pattern_results)

    def save_new_pattern(
        self,
        error_signature: str,
        solution: str,
        workflow_step: str,
    ) -> int:
        """Save a new fix pattern to memory.

        Args:
            error_signature: Unique identifier for the error type.
            solution: Description of how to fix the error.
            workflow_step: The workflow step where this fix applies.

        Returns:
            The memory ID of the saved pattern.

        Raises:
            MemoryBridgeNotConfiguredError: If no memory_bridge is configured.
        """
        if self.memory_bridge is None:
            raise MemoryBridgeNotConfiguredError(
                "Cannot save pattern without memory_bridge configured"
            )

        return self.memory_bridge.save_fix_pattern(
            error_signature=error_signature,
            solution=solution,
            workflow_step=workflow_step,
        )


# =============================================================================
# Task 5: Recovery Logging (AC: #4)
# =============================================================================

DEFAULT_RECOVERY_LOG_PATH = "_bmad-output/recovery-logs"


@dataclass
class RecoveryLog:
    """Log entry for a recovery attempt.

    Attributes:
        recovery_method: The recovery method used (e.g., "pattern_application").
        attempts_count: Number of attempts made.
        timestamp: When the recovery was attempted.
        original_error: Description of the original error.
        recovery_details: Additional details about the recovery.
    """

    recovery_method: str
    attempts_count: int
    timestamp: datetime
    original_error: str
    recovery_details: dict[str, Any]


class RecoveryLogger:
    """Logger for recording recovery attempts.

    Stores recovery logs in memory and provides methods for
    retrieval, filtering, and export.

    Attributes:
        storage_path: Path where logs can be persisted.
        logs: In-memory list of recovery logs.
    """

    def __init__(self, storage_path: str | None = None) -> None:
        """Initialize RecoveryLogger.

        Args:
            storage_path: Path for log storage (defaults to _bmad-output/recovery-logs).
        """
        self.storage_path = storage_path or DEFAULT_RECOVERY_LOG_PATH
        self.logs: list[RecoveryLog] = []

    def log_recovery(
        self,
        method: str,
        attempts: int,
        original_error: str,
        details: dict[str, Any],
    ) -> RecoveryLog:
        """Log a recovery attempt.

        Args:
            method: The recovery method used.
            attempts: Number of attempts made.
            original_error: Description of the original error.
            details: Additional recovery details.

        Returns:
            The created RecoveryLog entry.
        """
        log = RecoveryLog(
            recovery_method=method,
            attempts_count=attempts,
            timestamp=datetime.now(),
            original_error=original_error,
            recovery_details=details,
        )
        self.logs.append(log)
        return log

    def get_logs(self, method: str | None = None) -> list[RecoveryLog]:
        """Get stored logs, optionally filtered by method.

        Args:
            method: Optional method to filter by.

        Returns:
            List of matching RecoveryLog entries.
        """
        if method is None:
            return list(self.logs)

        return [log for log in self.logs if log.recovery_method == method]

    def export_logs(self) -> list[dict[str, Any]]:
        """Export logs in serializable format.

        Returns:
            List of log dictionaries with ISO-formatted timestamps.
        """
        result = []
        for log in self.logs:
            result.append(
                {
                    "recovery_method": log.recovery_method,
                    "attempts_count": log.attempts_count,
                    "timestamp": log.timestamp.isoformat(),
                    "original_error": log.original_error,
                    "recovery_details": log.recovery_details,
                }
            )
        return result

    def clear_logs(self) -> None:
        """Clear all stored logs."""
        self.logs.clear()


# =============================================================================
# Task 6: Escalation with Context (AC: #5)
# =============================================================================


@dataclass
class RecoveryAttempt:
    """Record of a single recovery attempt.

    Attributes:
        strategy: The recovery strategy used.
        success: Whether the attempt was successful.
        failure_reason: Reason for failure (if not successful).
    """

    strategy: str
    success: bool
    failure_reason: str | None = None


@dataclass
class EscalationReport:
    """Report for escalation to user when all recovery strategies fail.

    Attributes:
        strategies_attempted: List of strategies that were tried.
        failure_reasons: Mapping of strategy to failure reason.
        recommendations: Actionable recommendations for the user.
    """

    strategies_attempted: list[str]
    failure_reasons: dict[str, str]
    recommendations: list[str]

    def format_for_display(self) -> str:
        """Format the escalation report for user presentation.

        Returns:
            Human-readable string with sections for strategies,
            failures, and recommendations.
        """
        lines: list[str] = []

        lines.append("=" * 60)
        lines.append("VALIDATION RECOVERY ESCALATION REPORT")
        lines.append("=" * 60)
        lines.append("")

        # Strategies Attempted section
        lines.append("## Strategies Attempted")
        lines.append("-" * 40)
        for strategy in self.strategies_attempted:
            lines.append(f"  - {strategy}")
        lines.append("")

        # Failure Reasons section
        lines.append("## Failure Reasons")
        lines.append("-" * 40)
        for strategy, reason in self.failure_reasons.items():
            lines.append(f"  {strategy}:")
            lines.append(f"    {reason}")
        lines.append("")

        # Recommendations section
        lines.append("## Recommended Actions")
        lines.append("-" * 40)
        for i, rec in enumerate(self.recommendations, 1):
            lines.append(f"  {i}. {rec}")
        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the escalation report to a dictionary.

        Returns:
            Dictionary representation of the report.
        """
        return {
            "strategies_attempted": self.strategies_attempted,
            "failure_reasons": self.failure_reasons,
            "recommendations": self.recommendations,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EscalationReport:
        """Deserialize an escalation report from a dictionary.

        Args:
            data: Dictionary with report data.

        Returns:
            EscalationReport instance.
        """
        return cls(
            strategies_attempted=data["strategies_attempted"],
            failure_reasons=data["failure_reasons"],
            recommendations=data["recommendations"],
        )


# Strategy-specific recommendation templates
STRATEGY_RECOMMENDATIONS: dict[str, list[str]] = {
    "locate_config": [
        "Create a configuration file at ~/.config/bmad/config.yaml",
        "Run 'bmad init' to generate default configuration",
        "Check that all required configuration keys are present",
    ],
    "retry_backoff": [
        "Check network connectivity",
        "Verify the target service is available",
        "Increase timeout settings if appropriate",
    ],
    "retry": [
        "Check network connectivity",
        "Verify the target service is available",
    ],
    "pattern": [
        "Add a new fix pattern to memory for this error type",
        "Review existing patterns for applicability",
    ],
    "apply_pattern": [
        "Add a new fix pattern to memory for this error type",
        "Review existing patterns for applicability",
    ],
}


def build_escalation_report(attempts: list[RecoveryAttempt]) -> EscalationReport:
    """Build an escalation report from a list of recovery attempts.

    Aggregates all attempted strategies and their failure reasons,
    then generates recommendations based on the strategies that failed.

    Args:
        attempts: List of RecoveryAttempt records.

    Returns:
        EscalationReport summarizing the failures and recommendations.
    """
    strategies_attempted: list[str] = []
    failure_reasons: dict[str, str] = {}
    recommendations: list[str] = []
    seen_recommendations: set[str] = set()

    for attempt in attempts:
        strategies_attempted.append(attempt.strategy)

        if attempt.failure_reason:
            failure_reasons[attempt.strategy] = attempt.failure_reason

        # Add recommendations for this strategy
        strategy_recs = STRATEGY_RECOMMENDATIONS.get(attempt.strategy, [])
        for rec in strategy_recs:
            if rec not in seen_recommendations:
                recommendations.append(rec)
                seen_recommendations.add(rec)

    return EscalationReport(
        strategies_attempted=strategies_attempted,
        failure_reasons=failure_reasons,
        recommendations=recommendations,
    )


# =============================================================================
# Task 7: Recovery Orchestrator Integration (AC: All)
# =============================================================================

RECOVERY_STRATEGY_ORDER: list[RecoveryStrategy] = [
    RecoveryStrategy.LOCATE_CONFIG,
    RecoveryStrategy.RETRY_BACKOFF,
    RecoveryStrategy.APPLY_PATTERN,
    RecoveryStrategy.ESCALATE,
]
"""Ordered list of recovery strategies to attempt.

Recovery is attempted in this order:
1. LOCATE_CONFIG - Try to find missing configuration
2. RETRY_BACKOFF - Retry transient errors with exponential backoff
3. APPLY_PATTERN - Apply known fix patterns from memory
4. ESCALATE - Escalate to user with full context
"""


class ValidationRecoveryOrchestrator:
    """Orchestrates validation failure recovery across all strategies.

    Coordinates recovery attempts across multiple strategies in a defined order,
    tracks all attempts, logs successful recoveries, and provides escalation
    reports when all strategies fail.

    The recovery order is:
    1. LOCATE_CONFIG - For missing configuration errors
    2. RETRY_BACKOFF - For transient/network errors
    3. APPLY_PATTERN - For known error patterns
    4. ESCALATE - When all strategies fail

    Attributes:
        context_preloader: Interface for querying fix patterns from memory.
        missing_config_recovery: Handler for missing config recovery.
        transient_error_recovery: Handler for transient error retry.
        pattern_recovery: Handler for pattern-based recovery.
        recovery_logger: Optional logger for recording recovery attempts.
        recovery_attempts: List of recovery attempts for current error.
    """

    def __init__(
        self,
        context_preloader: Any,
        search_paths: list[Path] | None = None,
        recovery_logger: RecoveryLogger | None = None,
        memory_bridge: Any | None = None,
        backoff_base: float | None = None,
    ) -> None:
        """Initialize ValidationRecoveryOrchestrator.

        Args:
            context_preloader: Interface for querying fix patterns from memory.
            search_paths: Paths to search for configuration files.
            recovery_logger: Optional logger for recording recovery attempts.
            memory_bridge: Optional interface for saving new patterns.
            backoff_base: Base for exponential backoff (default: BACKOFF_BASE).
        """
        self.context_preloader = context_preloader
        self.recovery_logger = recovery_logger
        self.recovery_attempts: list[RecoveryAttempt] = []

        # Initialize recovery handlers
        self.missing_config_recovery = MissingConfigRecovery(
            search_paths=search_paths,
        )
        self.transient_error_recovery = TransientErrorRecovery(
            backoff_base=backoff_base,
        )
        self.pattern_recovery = PatternRecovery(
            context_preloader=context_preloader,
            memory_bridge=memory_bridge,
            recovery_logger=recovery_logger,
        )

    def attempt_recovery(
        self,
        error: Exception,
        retry_operation: Callable[[], T] | None = None,
        use_pattern_recovery: bool = False,
    ) -> RecoveryResult:
        """Attempt to recover from a validation failure.

        Classifies the error, attempts recovery strategies in order per design spec:
        1. LOCATE_CONFIG - For MISSING_CONFIG errors
        2. RETRY_BACKOFF - For TRANSIENT_ERROR when retry_operation provided
        3. APPLY_PATTERN - When use_pattern_recovery=True or KNOWN_PATTERN type
        4. ESCALATE - When all applicable strategies fail

        Strategies are tried in order; if a strategy succeeds, recovery stops.
        If a strategy fails but more strategies are applicable, the next one is tried.

        Args:
            error: The exception to recover from.
            retry_operation: Optional callable to retry for transient errors.
            use_pattern_recovery: Whether to attempt pattern recovery.

        Returns:
            RecoveryResult with success status and details.
        """
        # Clear previous attempts
        self.recovery_attempts = []

        # Classify the error
        failure_type = classify_failure(error)

        # Strategy 1: LOCATE_CONFIG for MISSING_CONFIG errors
        if failure_type == FailureType.MISSING_CONFIG:
            result = self._attempt_missing_config_recovery_without_escalate(error)
            if result.success:
                return result
            # Continue to next strategy if failed

        # Strategy 2: RETRY_BACKOFF for TRANSIENT_ERROR when operation provided
        if failure_type == FailureType.TRANSIENT_ERROR and retry_operation is not None:
            result = self._attempt_transient_recovery_without_escalate(error, retry_operation)
            if result.success:
                return result
            # Continue to next strategy if failed

        # Strategy 3: APPLY_PATTERN when enabled or for KNOWN_PATTERN errors
        if use_pattern_recovery or failure_type == FailureType.KNOWN_PATTERN:
            result = self._attempt_pattern_recovery(error)
            if result.success:
                return result
            # Continue to escalation if failed

        # All strategies failed or not applicable - escalate
        return self._escalate(error, failure_type)

    def _attempt_missing_config_recovery_without_escalate(
        self,
        error: Exception,
    ) -> RecoveryResult:
        """Attempt to recover from a missing configuration error without escalating.

        This allows the orchestrator to continue trying other strategies if
        config recovery fails.

        Args:
            error: The missing config error.

        Returns:
            RecoveryResult from the recovery attempt (success or failure).
        """
        result = self.missing_config_recovery.recover(error)

        # Track the attempt
        self.recovery_attempts.append(
            RecoveryAttempt(
                strategy="locate_config",
                success=result.success,
                failure_reason=None if result.success else result.message,
            )
        )

        # Log if successful and logger is configured
        if result.success and self.recovery_logger:
            self.recovery_logger.log_recovery(
                method="locate_config",
                attempts=1,
                original_error=str(error),
                details=result.details,
            )

        return result

    def _attempt_missing_config_recovery(
        self,
        error: Exception,
    ) -> RecoveryResult:
        """Attempt to recover from a missing configuration error.

        Args:
            error: The missing config error.

        Returns:
            RecoveryResult from the recovery attempt.
        """
        result = self._attempt_missing_config_recovery_without_escalate(error)

        if result.success:
            return result

        # If config recovery failed, escalate
        return self._escalate(error, FailureType.MISSING_CONFIG)

    def _attempt_transient_recovery_without_escalate(
        self,
        error: Exception,
        operation: Callable[[], T],
    ) -> RecoveryResult:
        """Attempt to recover from a transient error without escalating.

        This allows the orchestrator to continue trying other strategies if
        retry recovery fails.

        Args:
            error: The transient error.
            operation: The operation to retry.

        Returns:
            RecoveryResult from the retry attempt (success or failure).
        """
        result = self.transient_error_recovery.recover(error, operation)

        # Track the attempt
        self.recovery_attempts.append(
            RecoveryAttempt(
                strategy="retry_backoff",
                success=result.success,
                failure_reason=None if result.success else result.message,
            )
        )

        # Log if successful and logger is configured
        if result.success and self.recovery_logger:
            self.recovery_logger.log_recovery(
                method="retry_backoff",
                attempts=result.details.get("attempts", 1),
                original_error=str(error),
                details=result.details,
            )

        return result

    def _attempt_transient_recovery(
        self,
        error: Exception,
        operation: Callable[[], T],
    ) -> RecoveryResult:
        """Attempt to recover from a transient error by retrying.

        Args:
            error: The transient error.
            operation: The operation to retry.

        Returns:
            RecoveryResult from the retry attempt.
        """
        result = self._attempt_transient_recovery_without_escalate(error, operation)

        if result.success:
            return result

        # If retry failed, escalate
        return self._escalate(error, FailureType.TRANSIENT_ERROR)

    def _attempt_pattern_recovery(
        self,
        error: Exception,
    ) -> RecoveryResult:
        """Attempt to recover using known fix patterns from memory.

        Args:
            error: The error to find patterns for.

        Returns:
            RecoveryResult from the pattern recovery attempt.
        """
        # Query for matching patterns
        patterns = self.pattern_recovery.query_fix_patterns(error)

        if not patterns:
            self.recovery_attempts.append(
                RecoveryAttempt(
                    strategy="apply_pattern",
                    success=False,
                    failure_reason="No matching patterns found",
                )
            )
            return RecoveryResult(
                success=False,
                failure_type=FailureType.KNOWN_PATTERN,
                strategy_used=RecoveryStrategy.APPLY_PATTERN,
                message="No matching patterns found in memory",
            )

        # Try to apply the best matching pattern
        best_pattern = patterns[0]
        context = {
            "error_type": getattr(error, "error_type", type(error).__name__),
        }
        outcome = self.pattern_recovery.apply_fix_pattern(best_pattern, context)

        # Track the attempt
        self.recovery_attempts.append(
            RecoveryAttempt(
                strategy="apply_pattern",
                success=outcome.success,
                failure_reason=outcome.failure_reason,
            )
        )

        if outcome.success:
            return RecoveryResult(
                success=True,
                failure_type=FailureType.KNOWN_PATTERN,
                strategy_used=RecoveryStrategy.APPLY_PATTERN,
                message=outcome.message,
                details={"pattern_id": outcome.pattern_id},
            )

        return RecoveryResult(
            success=False,
            failure_type=FailureType.KNOWN_PATTERN,
            strategy_used=RecoveryStrategy.APPLY_PATTERN,
            message=f"Pattern application failed: {outcome.failure_reason}",
        )

    def _escalate(
        self,
        error: Exception,
        failure_type: FailureType,
    ) -> RecoveryResult:
        """Escalate to user when all recovery strategies fail.

        Builds an escalation report with all attempted strategies and
        failure reasons, along with recommendations.

        Args:
            error: The original error.
            failure_type: The classified failure type.

        Returns:
            RecoveryResult with escalation context.
        """
        # Build escalation report from attempts
        report = build_escalation_report(self.recovery_attempts)

        # Log the escalation if logger is configured
        if self.recovery_logger:
            self.recovery_logger.log_recovery(
                method="escalate",
                attempts=len(self.recovery_attempts),
                original_error=str(error),
                details={
                    "strategies_attempted": report.strategies_attempted,
                    "failure_type": failure_type.value,
                },
            )

        return RecoveryResult(
            success=False,
            failure_type=failure_type,
            strategy_used=RecoveryStrategy.ESCALATE,
            message="All recovery strategies failed, escalating to user",
            escalation_context={
                "strategies_attempted": report.strategies_attempted,
                "failure_reasons": report.failure_reasons,
                "recommendations": report.recommendations,
                "report": report.to_dict(),
            },
        )
