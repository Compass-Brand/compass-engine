"""BMB-Specific Menu Thresholds.

This module provides BMB-specific threshold checks that trigger escalation
independently of confidence scoring. High-severity validation issues
automatically escalate to Party Mode or Advanced Elicitation before
stall detection kicks in.

Story: 2b-3-bmb-specific-menu-thresholds

Threshold Hierarchy:
    PRIMARY CHECK (BMB thresholds - evaluated FIRST):
        IF blocking_errors > 3:
            -> PartyModeEscalation (collaborative problem-solving)
        ELIF major_issues > 5:
            -> PartyModeEscalation (collaborative problem-solving)
        ELIF compliance_score < 70:
            -> AdvancedElicitationEscalation (deep investigation)
        ELSE:
            -> NoEscalation (continue to confidence-based flow)

Examples:
    >>> metrics = ValidationMetrics(blocking_errors=5, major_issues=2, compliance_score=80)
    >>> result = evaluate_all_thresholds(metrics)
    >>> result.action
    EscalationAction.PARTY_MODE
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# =============================================================================
# Enums
# =============================================================================


class EscalationAction(Enum):
    """Type of escalation action to take.

    Attributes:
        PARTY_MODE: [P] escalation - collaborative problem-solving
        ADVANCED_ELICITATION: [A] escalation - deep investigation
        NO_ESCALATION: Continue normal confidence-based flow
    """

    PARTY_MODE = "party_mode"
    ADVANCED_ELICITATION = "advanced"
    NO_ESCALATION = "none"


# =============================================================================
# Constants
# =============================================================================


# BMB Threshold Constants (from Architecture Design)
BLOCKING_ERROR_THRESHOLD = 3   # > 3 triggers Party Mode
MAJOR_ISSUE_THRESHOLD = 5      # > 5 triggers Party Mode
COMPLIANCE_SCORE_THRESHOLD = 70 # < 70 triggers Advanced Elicitation

# Performance constraint (Task 4)
MAX_THRESHOLD_CHECK_MS = 100


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class ValidationMetrics:
    """Metrics from validation results for threshold checking.

    Attributes:
        blocking_errors: Count of blocking/critical errors
        major_issues: Count of major (non-blocking) issues
        compliance_score: Compliance percentage (0-100)
    """

    blocking_errors: int = 0
    major_issues: int = 0
    compliance_score: int = 100  # 0-100 percentage


@dataclass
class EscalationResult:
    """Result of BMB threshold evaluation.

    Attributes:
        action: The escalation action to take
        reason: Human-readable explanation
        threshold_violated: Name of the threshold that triggered escalation
        threshold_value: The actual value that violated the threshold
        duration_ms: Time taken to evaluate thresholds (for performance validation)
    """

    action: EscalationAction
    reason: str
    threshold_violated: Optional[str] = None
    threshold_value: Optional[int] = None
    duration_ms: int = 0


# =============================================================================
# Threshold Check Functions (Task 1.5-1.7)
# =============================================================================


def check_blocking_errors(metrics: ValidationMetrics) -> Optional[EscalationResult]:
    """Check if blocking errors exceed threshold.

    Args:
        metrics: Validation metrics to check

    Returns:
        EscalationResult with PartyMode action if threshold exceeded, None otherwise

    Raises:
        ValueError: If blocking_errors is negative
    """
    if metrics.blocking_errors < 0:
        raise ValueError(
            f"blocking_errors cannot be negative: {metrics.blocking_errors}"
        )
    if metrics.blocking_errors > BLOCKING_ERROR_THRESHOLD:
        return EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason=f"High blocking error count: {metrics.blocking_errors}",
            threshold_violated="blocking_errors",
            threshold_value=metrics.blocking_errors,
        )
    return None


def check_major_issues(metrics: ValidationMetrics) -> Optional[EscalationResult]:
    """Check if major issues exceed threshold.

    Args:
        metrics: Validation metrics to check

    Returns:
        EscalationResult with PartyMode action if threshold exceeded, None otherwise

    Raises:
        ValueError: If major_issues is negative
    """
    if metrics.major_issues < 0:
        raise ValueError(
            f"major_issues cannot be negative: {metrics.major_issues}"
        )
    if metrics.major_issues > MAJOR_ISSUE_THRESHOLD:
        return EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason=f"High major issue count: {metrics.major_issues}",
            threshold_violated="major_issues",
            threshold_value=metrics.major_issues,
        )
    return None


def check_compliance_score(metrics: ValidationMetrics) -> Optional[EscalationResult]:
    """Check if compliance score is below threshold.

    Args:
        metrics: Validation metrics to check

    Returns:
        EscalationResult with AdvancedElicitation action if below threshold, None otherwise

    Raises:
        ValueError: If compliance_score is outside valid range (0-100)
    """
    if metrics.compliance_score < 0 or metrics.compliance_score > 100:
        raise ValueError(
            f"compliance_score outside valid range (0-100): {metrics.compliance_score}"
        )
    if metrics.compliance_score < COMPLIANCE_SCORE_THRESHOLD:
        return EscalationResult(
            action=EscalationAction.ADVANCED_ELICITATION,
            reason=f"Low compliance score: {metrics.compliance_score}%",
            threshold_violated="compliance_score",
            threshold_value=metrics.compliance_score,
        )
    return None


# =============================================================================
# Task 3: No-Escalation Path Functions
# =============================================================================


def is_within_thresholds(metrics: ValidationMetrics) -> bool:
    """Check if all metrics are within safe thresholds.

    This is a quick boolean check for whether escalation is needed.
    Use evaluate_all_thresholds() for detailed escalation information.

    Args:
        metrics: Validation metrics to check

    Returns:
        True if all thresholds pass (no escalation needed), False otherwise
    """
    # Check each threshold - return False if any is violated
    if metrics.blocking_errors > BLOCKING_ERROR_THRESHOLD:
        return False
    if metrics.major_issues > MAJOR_ISSUE_THRESHOLD:
        return False
    if metrics.compliance_score < COMPLIANCE_SCORE_THRESHOLD:
        return False
    return True


# =============================================================================
# Task 4: Performance Validation Functions
# =============================================================================


def performance_check(duration_ms: int) -> bool:
    """Check if duration is within acceptable performance limit.

    Args:
        duration_ms: Duration in milliseconds

    Returns:
        True if duration is under MAX_THRESHOLD_CHECK_MS, False otherwise
    """
    return duration_ms < MAX_THRESHOLD_CHECK_MS


# =============================================================================
# Task 2: Priority Logic / Main Evaluation Function
# =============================================================================


def evaluate_all_thresholds(metrics: ValidationMetrics) -> EscalationResult:
    """Evaluate all BMB thresholds and return highest-priority escalation.

    Priority order (highest to lowest):
    1. PartyMode (blocking errors) - highest severity
    2. PartyMode (major issues) - second priority
    3. AdvancedElicitation (compliance score) - third priority
    4. NoEscalation - all thresholds pass

    This function includes timing instrumentation for performance validation.

    Args:
        metrics: Validation metrics to check

    Returns:
        EscalationResult with the appropriate action and timing information
    """
    # Start timing (Task 4.1)
    start_time = time.perf_counter()

    # Check thresholds in priority order (Task 2.1-2.2)
    # 1. Blocking errors (highest priority)
    result = check_blocking_errors(metrics)
    if result is not None:
        end_time = time.perf_counter()
        result.duration_ms = int((end_time - start_time) * 1000)
        return result

    # 2. Major issues (second priority)
    result = check_major_issues(metrics)
    if result is not None:
        end_time = time.perf_counter()
        result.duration_ms = int((end_time - start_time) * 1000)
        return result

    # 3. Compliance score (third priority)
    result = check_compliance_score(metrics)
    if result is not None:
        end_time = time.perf_counter()
        result.duration_ms = int((end_time - start_time) * 1000)
        return result

    # 4. All thresholds pass - no escalation needed (Task 3.2)
    end_time = time.perf_counter()
    duration_ms = int((end_time - start_time) * 1000)

    return EscalationResult(
        action=EscalationAction.NO_ESCALATION,
        reason="All thresholds passed - within safe limits",
        threshold_violated=None,
        threshold_value=None,
        duration_ms=duration_ms,
    )


# =============================================================================
# Task 2: BMBThresholdChecker Class (Story 2b-3 Task 1-2)
# =============================================================================


# Priority mapping for escalation actions (lower number = higher priority)
_ESCALATION_PRIORITY: dict[EscalationAction, int] = {
    EscalationAction.PARTY_MODE: 1,           # Highest priority
    EscalationAction.ADVANCED_ELICITATION: 2,  # Medium priority
    EscalationAction.NO_ESCALATION: 3,         # Lowest priority
}


class BMBThresholdChecker:
    """Class-based wrapper for BMB threshold checking operations.

    This class provides an object-oriented interface for BMB threshold checking,
    wrapping the module-level functions and adding combine_escalation_reasons
    for multi-threshold violation handling.

    Example:
        >>> checker = BMBThresholdChecker()
        >>> metrics = ValidationMetrics(blocking_errors=5, major_issues=8)
        >>> result = checker.evaluate_all_thresholds(metrics)
        >>> result.action
        EscalationAction.PARTY_MODE
    """

    def check_blocking_errors(
        self, metrics: ValidationMetrics
    ) -> Optional[EscalationResult]:
        """Check if blocking errors exceed threshold.

        Args:
            metrics: Validation metrics to check

        Returns:
            EscalationResult with PartyMode action if threshold exceeded, None otherwise

        Raises:
            ValueError: If blocking_errors is negative
        """
        return check_blocking_errors(metrics)

    def check_major_issues(
        self, metrics: ValidationMetrics
    ) -> Optional[EscalationResult]:
        """Check if major issues exceed threshold.

        Args:
            metrics: Validation metrics to check

        Returns:
            EscalationResult with PartyMode action if threshold exceeded, None otherwise

        Raises:
            ValueError: If major_issues is negative
        """
        return check_major_issues(metrics)

    def check_compliance_score(
        self, metrics: ValidationMetrics
    ) -> Optional[EscalationResult]:
        """Check if compliance score is below threshold.

        Args:
            metrics: Validation metrics to check

        Returns:
            EscalationResult with AdvancedElicitation if below threshold, None otherwise

        Raises:
            ValueError: If compliance_score is outside valid range (0-100)
        """
        return check_compliance_score(metrics)

    def evaluate_all_thresholds(
        self, metrics: ValidationMetrics
    ) -> EscalationResult:
        """Evaluate all BMB thresholds and return highest-priority escalation.

        Priority order (highest to lowest):
        1. PartyMode (blocking errors) - highest severity
        2. PartyMode (major issues) - second priority
        3. AdvancedElicitation (compliance score) - third priority
        4. NoEscalation - all thresholds pass

        Args:
            metrics: Validation metrics to check

        Returns:
            EscalationResult with the appropriate action and timing information
        """
        return evaluate_all_thresholds(metrics)

    def combine_escalation_reasons(
        self, results: list[EscalationResult]
    ) -> EscalationResult:
        """Combine multiple escalation results into a single result.

        When multiple thresholds are violated, this method combines them
        into a single result with the highest-priority action and all
        reasons combined.

        Priority order:
        1. PARTY_MODE (highest)
        2. ADVANCED_ELICITATION
        3. NO_ESCALATION (lowest)

        Args:
            results: List of EscalationResult objects to combine

        Returns:
            Combined EscalationResult with highest-priority action

        Raises:
            ValueError: If results list is empty
        """
        if not results:
            raise ValueError("Cannot combine empty list of escalation results")

        # Single result - return as-is
        if len(results) == 1:
            return results[0]

        # Find highest priority action
        highest_priority_result = min(
            results,
            key=lambda r: _ESCALATION_PRIORITY.get(r.action, 999)
        )

        # Combine all reasons
        combined_reasons = " | ".join(r.reason for r in results)

        # Return combined result with highest priority action
        return EscalationResult(
            action=highest_priority_result.action,
            reason=combined_reasons,
            threshold_violated=highest_priority_result.threshold_violated,
            threshold_value=highest_priority_result.threshold_value,
            duration_ms=highest_priority_result.duration_ms,
        )
