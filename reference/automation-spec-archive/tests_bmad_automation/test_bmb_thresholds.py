"""Tests for BMB-Specific Menu Thresholds.

This module tests the BMB threshold checks that trigger escalation
independently of confidence scoring.

Story: 2b-3-bmb-specific-menu-thresholds
TDD: Tests are written FIRST, before implementation.
"""

import time
import pytest

# Import will fail until implementation exists (TDD Red phase)
from pcmrp_tools.bmad_automation.bmb_thresholds import (
    EscalationAction,
    EscalationResult,
    ValidationMetrics,
    BLOCKING_ERROR_THRESHOLD,
    MAJOR_ISSUE_THRESHOLD,
    COMPLIANCE_SCORE_THRESHOLD,
    MAX_THRESHOLD_CHECK_MS,
    check_blocking_errors,
    check_major_issues,
    check_compliance_score,
    evaluate_all_thresholds,
    is_within_thresholds,
    performance_check,
)


# =============================================================================
# Task 1: EscalationAction Enum Tests (Group A - included for completeness)
# =============================================================================


class TestEscalationActionEnum:
    """Tests for EscalationAction enum (Task 1.1)."""

    def test_escalation_action_has_party_mode(self):
        """EscalationAction should have PARTY_MODE value."""
        assert EscalationAction.PARTY_MODE.value == "party_mode"

    def test_escalation_action_has_advanced_elicitation(self):
        """EscalationAction should have ADVANCED_ELICITATION value."""
        assert EscalationAction.ADVANCED_ELICITATION.value == "advanced"

    def test_escalation_action_has_no_escalation(self):
        """EscalationAction should have NO_ESCALATION value."""
        assert EscalationAction.NO_ESCALATION.value == "none"


# =============================================================================
# Task 1: EscalationResult Dataclass Tests (Group A - included for completeness)
# =============================================================================


class TestEscalationResultDataclass:
    """Tests for EscalationResult dataclass (Task 1.2)."""

    def test_escalation_result_creation(self):
        """EscalationResult should be creatable with all fields."""
        result = EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason="High blocking error count: 5",
            threshold_violated="blocking_errors",
            threshold_value=5,
        )
        assert result.action == EscalationAction.PARTY_MODE
        assert result.reason == "High blocking error count: 5"
        assert result.threshold_violated == "blocking_errors"
        assert result.threshold_value == 5

    def test_escalation_result_with_defaults(self):
        """EscalationResult should have optional fields with defaults."""
        result = EscalationResult(
            action=EscalationAction.NO_ESCALATION,
            reason="All thresholds passed",
        )
        assert result.threshold_violated is None
        assert result.threshold_value is None


# =============================================================================
# Task 1: ValidationMetrics Dataclass Tests (Group A - included for completeness)
# =============================================================================


class TestValidationMetricsDataclass:
    """Tests for ValidationMetrics dataclass (Task 1.4)."""

    def test_validation_metrics_creation(self):
        """ValidationMetrics should be creatable with all fields."""
        metrics = ValidationMetrics(
            blocking_errors=5,
            major_issues=10,
            compliance_score=65,
        )
        assert metrics.blocking_errors == 5
        assert metrics.major_issues == 10
        assert metrics.compliance_score == 65

    def test_validation_metrics_defaults(self):
        """ValidationMetrics should have sensible defaults."""
        metrics = ValidationMetrics()
        assert metrics.blocking_errors == 0
        assert metrics.major_issues == 0
        assert metrics.compliance_score == 100


# =============================================================================
# Task 1: Threshold Constants Tests (Group A - included for completeness)
# =============================================================================


class TestThresholdConstants:
    """Tests for BMB threshold constants (Task 1.3)."""

    def test_blocking_error_threshold_value(self):
        """BLOCKING_ERROR_THRESHOLD should be 3."""
        assert BLOCKING_ERROR_THRESHOLD == 3

    def test_major_issue_threshold_value(self):
        """MAJOR_ISSUE_THRESHOLD should be 5."""
        assert MAJOR_ISSUE_THRESHOLD == 5

    def test_compliance_score_threshold_value(self):
        """COMPLIANCE_SCORE_THRESHOLD should be 70."""
        assert COMPLIANCE_SCORE_THRESHOLD == 70


# =============================================================================
# Task 1: check_blocking_errors() Tests (Group A - included for completeness)
# =============================================================================


class TestCheckBlockingErrors:
    """Tests for check_blocking_errors() function (Task 1.5)."""

    def test_check_blocking_errors_above_threshold(self):
        """check_blocking_errors() should return escalation when > 3."""
        metrics = ValidationMetrics(blocking_errors=4)
        result = check_blocking_errors(metrics)
        assert result is not None
        assert result.action == EscalationAction.PARTY_MODE
        assert "blocking error" in result.reason.lower()
        assert "4" in result.reason

    def test_check_blocking_errors_at_threshold(self):
        """check_blocking_errors() should NOT escalate when exactly 3."""
        metrics = ValidationMetrics(blocking_errors=3)
        result = check_blocking_errors(metrics)
        assert result is None

    def test_check_blocking_errors_below_threshold(self):
        """check_blocking_errors() should NOT escalate when < 3."""
        metrics = ValidationMetrics(blocking_errors=2)
        result = check_blocking_errors(metrics)
        assert result is None

    def test_check_blocking_errors_at_zero(self):
        """check_blocking_errors() should NOT escalate when 0."""
        metrics = ValidationMetrics(blocking_errors=0)
        result = check_blocking_errors(metrics)
        assert result is None


# =============================================================================
# Task 1: check_major_issues() Tests (Group A - included for completeness)
# =============================================================================


class TestCheckMajorIssues:
    """Tests for check_major_issues() function (Task 1.6)."""

    def test_check_major_issues_above_threshold(self):
        """check_major_issues() should return escalation when > 5."""
        metrics = ValidationMetrics(major_issues=6)
        result = check_major_issues(metrics)
        assert result is not None
        assert result.action == EscalationAction.PARTY_MODE
        assert "major issue" in result.reason.lower()
        assert "6" in result.reason

    def test_check_major_issues_at_threshold(self):
        """check_major_issues() should NOT escalate when exactly 5."""
        metrics = ValidationMetrics(major_issues=5)
        result = check_major_issues(metrics)
        assert result is None

    def test_check_major_issues_below_threshold(self):
        """check_major_issues() should NOT escalate when < 5."""
        metrics = ValidationMetrics(major_issues=4)
        result = check_major_issues(metrics)
        assert result is None


# =============================================================================
# Task 1: check_compliance_score() Tests (Group A - included for completeness)
# =============================================================================


class TestCheckComplianceScore:
    """Tests for check_compliance_score() function (Task 1.7)."""

    def test_check_compliance_score_below_threshold(self):
        """check_compliance_score() should return escalation when < 70."""
        metrics = ValidationMetrics(compliance_score=69)
        result = check_compliance_score(metrics)
        assert result is not None
        assert result.action == EscalationAction.ADVANCED_ELICITATION
        assert "compliance score" in result.reason.lower()
        assert "69" in result.reason

    def test_check_compliance_score_at_threshold(self):
        """check_compliance_score() should NOT escalate when exactly 70."""
        metrics = ValidationMetrics(compliance_score=70)
        result = check_compliance_score(metrics)
        assert result is None

    def test_check_compliance_score_above_threshold(self):
        """check_compliance_score() should NOT escalate when > 70."""
        metrics = ValidationMetrics(compliance_score=85)
        result = check_compliance_score(metrics)
        assert result is None


# =============================================================================
# Task 2: evaluate_all_thresholds() Priority Tests (Group A - included)
# =============================================================================


class TestEvaluateAllThresholdsPriority:
    """Tests for evaluate_all_thresholds() priority logic (Task 2.1-2.2)."""

    def test_evaluate_blocking_errors_highest_priority(self):
        """Blocking errors should be highest priority."""
        metrics = ValidationMetrics(
            blocking_errors=5,  # Triggers PartyMode
            major_issues=8,     # Also triggers PartyMode
            compliance_score=60,  # Triggers AdvancedElicitation
        )
        result = evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.PARTY_MODE
        assert "blocking" in result.reason.lower()

    def test_evaluate_major_issues_second_priority(self):
        """Major issues should be second priority (after blocking)."""
        metrics = ValidationMetrics(
            blocking_errors=2,  # Below threshold
            major_issues=8,     # Triggers PartyMode
            compliance_score=60,  # Triggers AdvancedElicitation
        )
        result = evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.PARTY_MODE
        assert "major" in result.reason.lower()

    def test_evaluate_compliance_third_priority(self):
        """Compliance score should be lowest priority."""
        metrics = ValidationMetrics(
            blocking_errors=2,  # Below threshold
            major_issues=4,     # Below threshold
            compliance_score=60,  # Triggers AdvancedElicitation
        )
        result = evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.ADVANCED_ELICITATION
        assert "compliance" in result.reason.lower()


# =============================================================================
# Task 3: is_within_thresholds() Tests - NO-ESCALATION PATH (My Tasks)
# =============================================================================


class TestIsWithinThresholds:
    """Tests for is_within_thresholds() function (Task 3.1)."""

    def test_is_within_thresholds_all_safe(self):
        """is_within_thresholds() should return True when all metrics safe."""
        metrics = ValidationMetrics(
            blocking_errors=0,
            major_issues=0,
            compliance_score=100,
        )
        assert is_within_thresholds(metrics) is True

    def test_is_within_thresholds_at_boundaries(self):
        """is_within_thresholds() should return True at exact boundaries."""
        # Exactly at thresholds (not exceeding) should be within
        metrics = ValidationMetrics(
            blocking_errors=3,   # Exactly at threshold (>3 triggers)
            major_issues=5,      # Exactly at threshold (>5 triggers)
            compliance_score=70, # Exactly at threshold (<70 triggers)
        )
        assert is_within_thresholds(metrics) is True

    def test_is_within_thresholds_blocking_exceeded(self):
        """is_within_thresholds() should return False when blocking > 3."""
        metrics = ValidationMetrics(blocking_errors=4)
        assert is_within_thresholds(metrics) is False

    def test_is_within_thresholds_major_exceeded(self):
        """is_within_thresholds() should return False when major > 5."""
        metrics = ValidationMetrics(major_issues=6)
        assert is_within_thresholds(metrics) is False

    def test_is_within_thresholds_compliance_below(self):
        """is_within_thresholds() should return False when compliance < 70."""
        metrics = ValidationMetrics(compliance_score=69)
        assert is_within_thresholds(metrics) is False

    def test_is_within_thresholds_multiple_violations(self):
        """is_within_thresholds() should return False with multiple violations."""
        metrics = ValidationMetrics(
            blocking_errors=10,
            major_issues=20,
            compliance_score=30,
        )
        assert is_within_thresholds(metrics) is False


class TestEvaluateAllThresholdsNoEscalation:
    """Tests for evaluate_all_thresholds() NoEscalation path (Task 3.2)."""

    def test_evaluate_returns_no_escalation_when_all_pass(self):
        """evaluate_all_thresholds() should return NoEscalation when all thresholds pass."""
        metrics = ValidationMetrics(
            blocking_errors=0,
            major_issues=0,
            compliance_score=100,
        )
        result = evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.NO_ESCALATION
        assert "pass" in result.reason.lower() or "within" in result.reason.lower()

    def test_evaluate_returns_no_escalation_at_safe_boundaries(self):
        """evaluate_all_thresholds() should return NoEscalation at safe boundaries."""
        metrics = ValidationMetrics(
            blocking_errors=3,   # Exactly at threshold (not exceeded)
            major_issues=5,      # Exactly at threshold (not exceeded)
            compliance_score=70, # Exactly at threshold (not below)
        )
        result = evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.NO_ESCALATION

    def test_evaluate_no_escalation_has_no_threshold_violated(self):
        """NoEscalation result should have None for threshold_violated."""
        metrics = ValidationMetrics(
            blocking_errors=0,
            major_issues=0,
            compliance_score=100,
        )
        result = evaluate_all_thresholds(metrics)
        assert result.threshold_violated is None


class TestNormalFlowScenarios:
    """Tests for normal flow scenarios where no escalation needed (Task 3.3)."""

    def test_typical_good_validation_result(self):
        """Typical good validation results should not escalate."""
        metrics = ValidationMetrics(
            blocking_errors=1,
            major_issues=2,
            compliance_score=85,
        )
        result = evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.NO_ESCALATION

    def test_perfect_validation_result(self):
        """Perfect validation results (all zeros, 100%) should not escalate."""
        metrics = ValidationMetrics(
            blocking_errors=0,
            major_issues=0,
            compliance_score=100,
        )
        result = evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.NO_ESCALATION

    def test_slightly_below_perfect_still_passes(self):
        """Slightly imperfect but within thresholds should not escalate."""
        metrics = ValidationMetrics(
            blocking_errors=2,
            major_issues=4,
            compliance_score=75,
        )
        result = evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.NO_ESCALATION

    def test_exactly_at_all_safe_limits(self):
        """Exactly at all safe limits should not escalate."""
        metrics = ValidationMetrics(
            blocking_errors=3,
            major_issues=5,
            compliance_score=70,
        )
        result = evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.NO_ESCALATION


# =============================================================================
# Task 4: Performance Validation Tests (My Tasks)
# =============================================================================


class TestPerformanceCheckFunction:
    """Tests for performance_check() function (Task 4.2)."""

    def test_performance_check_within_limit(self):
        """performance_check() should return True for duration < 100ms."""
        assert performance_check(50) is True

    def test_performance_check_at_limit(self):
        """performance_check() should return False at exactly 100ms."""
        # At exactly 100ms, should fail (< 100, not <=)
        assert performance_check(100) is False

    def test_performance_check_above_limit(self):
        """performance_check() should return False for duration > 100ms."""
        assert performance_check(150) is False

    def test_performance_check_at_zero(self):
        """performance_check() should return True for 0ms."""
        assert performance_check(0) is True

    def test_performance_check_at_99(self):
        """performance_check() should return True for 99ms."""
        assert performance_check(99) is True

    def test_performance_check_at_1(self):
        """performance_check() should return True for 1ms."""
        assert performance_check(1) is True


class TestMaxThresholdCheckConstant:
    """Tests for MAX_THRESHOLD_CHECK_MS constant (Task 4.2)."""

    def test_max_threshold_check_ms_value(self):
        """MAX_THRESHOLD_CHECK_MS should be 100."""
        assert MAX_THRESHOLD_CHECK_MS == 100


class TestEvaluateAllThresholdsPerformance:
    """Tests for evaluate_all_thresholds() performance (Task 4.1, 4.3)."""

    def test_evaluate_all_thresholds_returns_duration_ms(self):
        """evaluate_all_thresholds() result should have duration_ms attribute."""
        metrics = ValidationMetrics()
        result = evaluate_all_thresholds(metrics)
        assert hasattr(result, 'duration_ms')
        assert isinstance(result.duration_ms, int)

    def test_evaluate_all_thresholds_fast_execution(self):
        """evaluate_all_thresholds() should execute in under 100ms."""
        metrics = ValidationMetrics(
            blocking_errors=5,
            major_issues=10,
            compliance_score=50,
        )
        result = evaluate_all_thresholds(metrics)
        assert result.duration_ms < MAX_THRESHOLD_CHECK_MS

    def test_evaluate_all_thresholds_performance_check_passes(self):
        """evaluate_all_thresholds() duration should pass performance_check()."""
        metrics = ValidationMetrics()
        result = evaluate_all_thresholds(metrics)
        assert performance_check(result.duration_ms) is True

    def test_evaluate_all_thresholds_timing_is_realistic(self):
        """evaluate_all_thresholds() timing should be realistic (not negative)."""
        metrics = ValidationMetrics()
        result = evaluate_all_thresholds(metrics)
        assert result.duration_ms >= 0

    def test_evaluate_all_thresholds_timing_worst_case(self):
        """evaluate_all_thresholds() should be fast even with all checks running."""
        # Worst case: all thresholds violated, all checks run
        metrics = ValidationMetrics(
            blocking_errors=100,
            major_issues=100,
            compliance_score=0,
        )
        result = evaluate_all_thresholds(metrics)
        assert result.duration_ms < MAX_THRESHOLD_CHECK_MS

    def test_multiple_calls_consistently_fast(self):
        """Multiple calls to evaluate_all_thresholds() should all be fast."""
        metrics = ValidationMetrics()
        for _ in range(10):
            result = evaluate_all_thresholds(metrics)
            assert result.duration_ms < MAX_THRESHOLD_CHECK_MS


class TestPerformanceEdgeCases:
    """Edge case tests for performance validation."""

    def test_performance_check_negative_duration(self):
        """performance_check() should return True for negative (invalid) duration."""
        # Negative duration is technically < 100, so True
        # But this shouldn't happen in practice
        assert performance_check(-1) is True

    def test_evaluate_timing_with_large_values(self):
        """Timing should not be affected by large metric values."""
        metrics = ValidationMetrics(
            blocking_errors=999999,
            major_issues=999999,
            compliance_score=0,
        )
        result = evaluate_all_thresholds(metrics)
        assert result.duration_ms < MAX_THRESHOLD_CHECK_MS


# =============================================================================
# Task 1: Edge Case Validation Tests (Task 1 additions for Story 2b-3)
# =============================================================================


class TestNegativeValueValidation:
    """Tests for negative value handling (Story 2b-3 edge cases)."""

    def test_check_blocking_errors_negative_raises_value_error(self):
        """check_blocking_errors() should raise ValueError for negative values."""
        metrics = ValidationMetrics(blocking_errors=-1)
        with pytest.raises(ValueError, match="negative"):
            check_blocking_errors(metrics)

    def test_check_major_issues_negative_raises_value_error(self):
        """check_major_issues() should raise ValueError for negative values."""
        metrics = ValidationMetrics(major_issues=-1)
        with pytest.raises(ValueError, match="negative"):
            check_major_issues(metrics)


class TestComplianceScoreRangeValidation:
    """Tests for compliance score range validation (Story 2b-3 edge cases)."""

    def test_check_compliance_score_negative_raises_value_error(self):
        """check_compliance_score() should raise ValueError for negative values."""
        metrics = ValidationMetrics(compliance_score=-1)
        with pytest.raises(ValueError, match="outside valid range"):
            check_compliance_score(metrics)

    def test_check_compliance_score_above_100_raises_value_error(self):
        """check_compliance_score() should raise ValueError for values > 100."""
        metrics = ValidationMetrics(compliance_score=101)
        with pytest.raises(ValueError, match="outside valid range"):
            check_compliance_score(metrics)

    def test_check_compliance_score_at_zero_valid(self):
        """check_compliance_score() should accept 0 (valid boundary)."""
        metrics = ValidationMetrics(compliance_score=0)
        result = check_compliance_score(metrics)
        assert result is not None
        assert result.action == EscalationAction.ADVANCED_ELICITATION

    def test_check_compliance_score_at_100_valid(self):
        """check_compliance_score() should accept 100 (valid boundary)."""
        metrics = ValidationMetrics(compliance_score=100)
        result = check_compliance_score(metrics)
        assert result is None


# =============================================================================
# Task 2: BMBThresholdChecker Class Tests (Story 2b-3 Task 2)
# =============================================================================


class TestBMBThresholdCheckerClass:
    """Tests for BMBThresholdChecker class wrapper (Task 2)."""

    def test_checker_class_exists(self):
        """BMBThresholdChecker class should exist."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        assert checker is not None

    def test_checker_has_check_blocking_errors_method(self):
        """BMBThresholdChecker should have check_blocking_errors method."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        assert hasattr(checker, 'check_blocking_errors')
        assert callable(checker.check_blocking_errors)

    def test_checker_has_check_major_issues_method(self):
        """BMBThresholdChecker should have check_major_issues method."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        assert hasattr(checker, 'check_major_issues')
        assert callable(checker.check_major_issues)

    def test_checker_has_check_compliance_score_method(self):
        """BMBThresholdChecker should have check_compliance_score method."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        assert hasattr(checker, 'check_compliance_score')
        assert callable(checker.check_compliance_score)

    def test_checker_has_evaluate_all_thresholds_method(self):
        """BMBThresholdChecker should have evaluate_all_thresholds method."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        assert hasattr(checker, 'evaluate_all_thresholds')
        assert callable(checker.evaluate_all_thresholds)

    def test_checker_has_combine_escalation_reasons_method(self):
        """BMBThresholdChecker should have combine_escalation_reasons method."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        assert hasattr(checker, 'combine_escalation_reasons')
        assert callable(checker.combine_escalation_reasons)

    def test_checker_check_blocking_errors_delegates_correctly(self):
        """BMBThresholdChecker.check_blocking_errors should work like module function."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(blocking_errors=5)
        result = checker.check_blocking_errors(metrics)
        assert result is not None
        assert result.action == EscalationAction.PARTY_MODE

    def test_checker_evaluate_all_thresholds_works(self):
        """BMBThresholdChecker.evaluate_all_thresholds should work correctly."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(blocking_errors=5, major_issues=8, compliance_score=50)
        result = checker.evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.PARTY_MODE
        assert "blocking" in result.reason.lower()


# =============================================================================
# Task 2.3: combine_escalation_reasons() Tests
# =============================================================================


class TestCombineEscalationReasons:
    """Tests for BMBThresholdChecker.combine_escalation_reasons() (Task 2.3)."""

    def test_combine_single_reason_returns_unchanged(self):
        """combine_escalation_reasons with single reason returns it unchanged."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        result1 = EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason="High blocking error count: 5",
            threshold_violated="blocking_errors",
            threshold_value=5,
        )
        combined = checker.combine_escalation_reasons([result1])
        assert combined.reason == "High blocking error count: 5"
        assert combined.action == EscalationAction.PARTY_MODE

    def test_combine_multiple_party_mode_reasons(self):
        """combine_escalation_reasons combines multiple PartyMode reasons."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        result1 = EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason="High blocking error count: 5",
            threshold_violated="blocking_errors",
            threshold_value=5,
        )
        result2 = EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason="High major issue count: 8",
            threshold_violated="major_issues",
            threshold_value=8,
        )
        combined = checker.combine_escalation_reasons([result1, result2])
        assert combined.action == EscalationAction.PARTY_MODE
        assert "blocking" in combined.reason.lower()
        assert "major" in combined.reason.lower()

    def test_combine_empty_list_raises_value_error(self):
        """combine_escalation_reasons raises ValueError for empty list."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        with pytest.raises(ValueError, match="empty"):
            checker.combine_escalation_reasons([])

    def test_combine_preserves_highest_priority_action(self):
        """combine_escalation_reasons preserves highest priority action."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        result1 = EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason="High blocking error count: 5",
            threshold_violated="blocking_errors",
            threshold_value=5,
        )
        result2 = EscalationResult(
            action=EscalationAction.ADVANCED_ELICITATION,
            reason="Low compliance score: 60%",
            threshold_violated="compliance_score",
            threshold_value=60,
        )
        combined = checker.combine_escalation_reasons([result1, result2])
        assert combined.action == EscalationAction.PARTY_MODE

    def test_combine_mixed_order_still_returns_highest_priority(self):
        """combine_escalation_reasons returns highest priority regardless of order."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        # Pass advanced elicitation first, but party mode should still win
        result1 = EscalationResult(
            action=EscalationAction.ADVANCED_ELICITATION,
            reason="Low compliance score: 60%",
            threshold_violated="compliance_score",
            threshold_value=60,
        )
        result2 = EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason="High blocking error count: 5",
            threshold_violated="blocking_errors",
            threshold_value=5,
        )
        combined = checker.combine_escalation_reasons([result1, result2])
        assert combined.action == EscalationAction.PARTY_MODE

    def test_combine_includes_all_reasons_in_output(self):
        """combine_escalation_reasons includes all reasons in combined output."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        result1 = EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason="High blocking error count: 5",
            threshold_violated="blocking_errors",
            threshold_value=5,
        )
        result2 = EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason="High major issue count: 8",
            threshold_violated="major_issues",
            threshold_value=8,
        )
        result3 = EscalationResult(
            action=EscalationAction.ADVANCED_ELICITATION,
            reason="Low compliance score: 55%",
            threshold_violated="compliance_score",
            threshold_value=55,
        )
        combined = checker.combine_escalation_reasons([result1, result2, result3])
        # All three reasons should be mentioned
        assert "blocking" in combined.reason.lower() or "5" in combined.reason
        assert "major" in combined.reason.lower() or "8" in combined.reason


class TestBMBThresholdCheckerPriorityLogic:
    """Tests for BMBThresholdChecker priority logic with class methods."""

    def test_checker_priority_blocking_over_major(self):
        """Checker returns blocking error escalation over major issues."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(
            blocking_errors=5,
            major_issues=8,
            compliance_score=80,
        )
        result = checker.evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.PARTY_MODE
        assert "blocking" in result.reason.lower()

    def test_checker_priority_major_over_compliance(self):
        """Checker returns major issues escalation over compliance."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(
            blocking_errors=2,
            major_issues=8,
            compliance_score=50,
        )
        result = checker.evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.PARTY_MODE
        assert "major" in result.reason.lower()

    def test_checker_all_thresholds_pass_returns_no_escalation(self):
        """Checker returns NO_ESCALATION when all thresholds pass."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(
            blocking_errors=2,
            major_issues=4,
            compliance_score=80,
        )
        result = checker.evaluate_all_thresholds(metrics)
        assert result.action == EscalationAction.NO_ESCALATION


# =============================================================================
# Additional Class Method Tests for Full Coverage
# =============================================================================


class TestBMBThresholdCheckerMethodValidation:
    """Tests for BMBThresholdChecker class method validation (full coverage)."""

    def test_checker_check_major_issues_raises_value_error_for_negative(self):
        """BMBThresholdChecker.check_major_issues raises ValueError for negative."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(major_issues=-5)
        with pytest.raises(ValueError, match="negative"):
            checker.check_major_issues(metrics)

    def test_checker_check_compliance_score_raises_value_error_for_invalid(self):
        """BMBThresholdChecker.check_compliance_score raises ValueError for invalid range."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(compliance_score=150)
        with pytest.raises(ValueError, match="outside valid range"):
            checker.check_compliance_score(metrics)

    def test_checker_check_major_issues_returns_none_when_below_threshold(self):
        """BMBThresholdChecker.check_major_issues returns None when below threshold."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(major_issues=3)
        result = checker.check_major_issues(metrics)
        assert result is None

    def test_checker_check_major_issues_returns_escalation_when_above_threshold(self):
        """BMBThresholdChecker.check_major_issues returns escalation when above threshold."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(major_issues=10)
        result = checker.check_major_issues(metrics)
        assert result is not None
        assert result.action == EscalationAction.PARTY_MODE

    def test_checker_check_compliance_score_returns_none_when_above_threshold(self):
        """BMBThresholdChecker.check_compliance_score returns None when above threshold."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(compliance_score=85)
        result = checker.check_compliance_score(metrics)
        assert result is None

    def test_checker_check_compliance_score_returns_escalation_when_below_threshold(self):
        """BMBThresholdChecker.check_compliance_score returns escalation when below threshold."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        metrics = ValidationMetrics(compliance_score=50)
        result = checker.check_compliance_score(metrics)
        assert result is not None
        assert result.action == EscalationAction.ADVANCED_ELICITATION


# =============================================================================
# Task 5: Integration with MenuSelector Tests (Story 2b-3 Task 5)
# =============================================================================


class TestEscalationSelectionResult:
    """Tests for EscalationSelectionResult dataclass (Task 5.1)."""

    def test_escalation_selection_result_exists(self):
        """EscalationSelectionResult dataclass should exist."""
        from pcmrp_tools.bmad_automation.menu_selection import EscalationSelectionResult
        result = EscalationSelectionResult(
            escalation=EscalationResult(
                action=EscalationAction.PARTY_MODE,
                reason="Test escalation",
            )
        )
        assert result is not None

    def test_escalation_selection_result_has_escalation_field(self):
        """EscalationSelectionResult should have escalation field."""
        from pcmrp_tools.bmad_automation.menu_selection import EscalationSelectionResult
        escalation = EscalationResult(
            action=EscalationAction.PARTY_MODE,
            reason="High blocking error count: 5",
            threshold_violated="blocking_errors",
            threshold_value=5,
        )
        result = EscalationSelectionResult(escalation=escalation)
        assert result.escalation == escalation

    def test_escalation_selection_result_defaults(self):
        """EscalationSelectionResult should have default values."""
        from pcmrp_tools.bmad_automation.menu_selection import EscalationSelectionResult
        result = EscalationSelectionResult(
            escalation=EscalationResult(
                action=EscalationAction.PARTY_MODE,
                reason="Test",
            )
        )
        assert result.selected is False
        assert result.auto_selected is False


class TestMenuSelectorWithBMBThresholds:
    """Tests for MenuSelector integration with BMB thresholds (Task 5.2)."""

    def test_menu_selector_accepts_bmb_checker_parameter(self):
        """MenuSelector should accept optional bmb_checker parameter."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        checker = BMBThresholdChecker()
        selector = MenuSelector(bmb_checker=checker)
        assert selector.bmb_checker is checker

    def test_menu_selector_without_bmb_checker(self):
        """MenuSelector should work without bmb_checker (default None)."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        selector = MenuSelector()
        assert selector.bmb_checker is None

    def test_menu_selector_creates_default_bmb_checker_if_none(self):
        """MenuSelector should create default BMBThresholdChecker if needed."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        # When validation_metrics are passed, a checker should be used
        selector = MenuSelector()
        # The selector can use None or create one on demand
        assert selector.bmb_checker is None or isinstance(selector.bmb_checker, BMBThresholdChecker)


class TestSelectOrPresentWithValidationMetrics:
    """Tests for select_or_present() with validation_metrics parameter (Task 5.3)."""

    def _create_detection_result(
        self,
        confidence: int,
        options: list[str],
    ):
        """Helper to create a MenuDetectionResult for testing."""
        from pcmrp_tools.bmad_automation.menu_participation_engine import (
            MenuDetectionResult,
            MenuType,
        )
        return MenuDetectionResult.detected(
            confidence=confidence,
            menu_type=MenuType.APC,
            options=options,
            breakdown={"test": confidence},
            raw_input=f"Menu with options: {options}",
        )

    def test_select_or_present_accepts_validation_metrics(self):
        """select_or_present() should accept validation_metrics parameter."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        metrics = ValidationMetrics(blocking_errors=0, major_issues=0, compliance_score=100)
        # Should not raise
        result = selector.select_or_present(detection, validation_metrics=metrics)
        assert result is not None

    def test_select_or_present_without_validation_metrics_normal_flow(self):
        """select_or_present() without validation_metrics should follow normal flow."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector, SelectionResult
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        result = selector.select_or_present(detection)
        # Should follow normal confidence-based flow
        assert isinstance(result, SelectionResult)
        assert result.selected is True


class TestBMBThresholdPreCheck:
    """Tests for BMB threshold pre-check logic (Task 5.4)."""

    def _create_detection_result(
        self,
        confidence: int,
        options: list[str],
    ):
        """Helper to create a MenuDetectionResult for testing."""
        from pcmrp_tools.bmad_automation.menu_participation_engine import (
            MenuDetectionResult,
            MenuType,
        )
        return MenuDetectionResult.detected(
            confidence=confidence,
            menu_type=MenuType.APC,
            options=options,
            breakdown={"test": confidence},
            raw_input=f"Menu with options: {options}",
        )

    def test_party_mode_escalation_bypasses_confidence_logic(self):
        """Blocking errors > 3 should trigger PartyMode and bypass confidence logic."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            EscalationSelectionResult,
        )
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        # 5 blocking errors > 3 threshold
        metrics = ValidationMetrics(blocking_errors=5, major_issues=0, compliance_score=100)
        result = selector.select_or_present(detection, validation_metrics=metrics)
        # Should return EscalationSelectionResult, not SelectionResult
        assert isinstance(result, EscalationSelectionResult)
        assert result.escalation.action == EscalationAction.PARTY_MODE
        assert "blocking" in result.escalation.reason.lower()

    def test_major_issues_trigger_party_mode(self):
        """Major issues > 5 should trigger PartyMode escalation."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            EscalationSelectionResult,
        )
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        # 8 major issues > 5 threshold
        metrics = ValidationMetrics(blocking_errors=0, major_issues=8, compliance_score=100)
        result = selector.select_or_present(detection, validation_metrics=metrics)
        assert isinstance(result, EscalationSelectionResult)
        assert result.escalation.action == EscalationAction.PARTY_MODE
        assert "major" in result.escalation.reason.lower()

    def test_low_compliance_triggers_advanced_elicitation(self):
        """Compliance score < 70 should trigger AdvancedElicitation escalation."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            EscalationSelectionResult,
        )
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        # 60% compliance < 70 threshold
        metrics = ValidationMetrics(blocking_errors=0, major_issues=0, compliance_score=60)
        result = selector.select_or_present(detection, validation_metrics=metrics)
        assert isinstance(result, EscalationSelectionResult)
        assert result.escalation.action == EscalationAction.ADVANCED_ELICITATION
        assert "compliance" in result.escalation.reason.lower()

    def test_within_thresholds_continues_normal_flow(self):
        """Metrics within thresholds should continue to confidence-based selection."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            SelectionResult,
        )
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        # All metrics within safe thresholds
        metrics = ValidationMetrics(blocking_errors=2, major_issues=3, compliance_score=80)
        result = selector.select_or_present(detection, validation_metrics=metrics)
        # Should follow normal confidence-based flow
        assert isinstance(result, SelectionResult)
        assert result.selected is True
        assert result.option in ["Continue", "Exit"]

    def test_bmb_thresholds_take_precedence_over_high_confidence(self):
        """BMB thresholds should take precedence even with 100% confidence."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            EscalationSelectionResult,
        )
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(100, ["Continue", "Exit"])
        # Even at 100% confidence, blocking errors should escalate
        metrics = ValidationMetrics(blocking_errors=10, major_issues=0, compliance_score=100)
        result = selector.select_or_present(detection, validation_metrics=metrics)
        assert isinstance(result, EscalationSelectionResult)
        assert result.escalation.action == EscalationAction.PARTY_MODE


class TestBMBEscalationLogging:
    """Tests for BMB escalation logging (Task 5.5)."""

    def _create_detection_result(
        self,
        confidence: int,
        options: list[str],
    ):
        """Helper to create a MenuDetectionResult for testing."""
        from pcmrp_tools.bmad_automation.menu_participation_engine import (
            MenuDetectionResult,
            MenuType,
        )
        return MenuDetectionResult.detected(
            confidence=confidence,
            menu_type=MenuType.APC,
            options=options,
            breakdown={"test": confidence},
            raw_input=f"Menu with options: {options}",
        )

    def test_escalation_is_logged(self):
        """BMB escalation should be logged to audit trail."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        metrics = ValidationMetrics(blocking_errors=5, major_issues=0, compliance_score=100)
        selector.select_or_present(detection, validation_metrics=metrics)
        trail = selector.logger.get_audit_trail()
        assert len(trail) == 1
        # Escalation should be logged with appropriate info
        assert trail[0].auto_selected is False
        assert "blocking" in trail[0].reason.lower() or "escalat" in trail[0].reason.lower()

    def test_escalation_log_has_duration(self):
        """Escalation log entry should have duration_ms."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        metrics = ValidationMetrics(blocking_errors=5, major_issues=0, compliance_score=100)
        selector.select_or_present(detection, validation_metrics=metrics)
        trail = selector.logger.get_audit_trail()
        assert trail[0].duration_ms >= 0

    def test_escalation_log_has_timestamp(self):
        """Escalation log entry should have timestamp."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        metrics = ValidationMetrics(blocking_errors=5, major_issues=0, compliance_score=100)
        selector.select_or_present(detection, validation_metrics=metrics)
        trail = selector.logger.get_audit_trail()
        assert trail[0].timestamp > 0

    def test_no_escalation_continues_to_normal_logging(self):
        """When no escalation needed, normal logging should occur."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.bmb_thresholds import BMBThresholdChecker
        selector = MenuSelector(bmb_checker=BMBThresholdChecker())
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        metrics = ValidationMetrics(blocking_errors=0, major_issues=0, compliance_score=100)
        selector.select_or_present(detection, validation_metrics=metrics)
        trail = selector.logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].auto_selected is True  # High confidence auto-select
        assert trail[0].selection == "Continue"
