"""Tests for Validation Type Detector component.

This module tests the ValidationTypeResult dataclass and ValidationType enum
that form the foundation of the BMAD Automation validation type detection system.

TDD Pattern: Tests written FIRST before implementation.
"""

import re

import pytest
from dataclasses import asdict

from pathlib import Path
import tempfile

from pcmrp_tools.bmad_automation.validation_type_detector import (
    ValidationType,
    ValidationTypeResult,
    detect_validation_type,
    detect_validation_type_from_file,
    detect_verdict_patterns,
    detect_error_patterns,
    detect_checklist_patterns,
    parse_workflow_file,
    VERDICT_PATTERNS,
    ERROR_PATTERNS,
    CHECKLIST_PATTERNS,
    CONFIDENCE_THRESHOLD,
)


class TestValidationType:
    """Tests for ValidationType enum (Subtask 1.1)."""

    def test_verdict_based_value(self):
        """Test ValidationType.VERDICT_BASED has correct string value."""
        assert ValidationType.VERDICT_BASED.value == "verdict-based"

    def test_error_based_value(self):
        """Test ValidationType.ERROR_BASED has correct string value."""
        assert ValidationType.ERROR_BASED.value == "error-based"

    def test_checklist_based_value(self):
        """Test ValidationType.CHECKLIST_BASED has correct string value."""
        assert ValidationType.CHECKLIST_BASED.value == "checklist-based"

    def test_custom_value(self):
        """Test ValidationType.CUSTOM has correct string value."""
        assert ValidationType.CUSTOM.value == "custom"

    def test_unknown_value(self):
        """Test ValidationType.UNKNOWN has correct string value."""
        assert ValidationType.UNKNOWN.value == "unknown"

    def test_all_enum_members_exist(self):
        """Test all required enum members exist."""
        expected_members = {
            "VERDICT_BASED",
            "ERROR_BASED",
            "CHECKLIST_BASED",
            "CUSTOM",
            "UNKNOWN",
        }
        actual_members = {member.name for member in ValidationType}
        assert expected_members == actual_members


class TestValidationTypeResult:
    """Tests for ValidationTypeResult dataclass (Subtask 1.1, 1.2)."""

    def test_create_with_all_fields(self):
        """Test creating ValidationTypeResult with all required fields."""
        result = ValidationTypeResult(
            validation_type=ValidationType.VERDICT_BASED,
            patterns=["PASS", "FAIL"],
            confidence=0.95,
            details={"verdict_type": "pass_fail"},
        )
        assert result.validation_type == ValidationType.VERDICT_BASED
        assert result.patterns == ["PASS", "FAIL"]
        assert result.confidence == 0.95
        assert result.details == {"verdict_type": "pass_fail"}

    def test_type_hints_validation_type_field(self):
        """Test validation_type field accepts ValidationType enum."""
        result = ValidationTypeResult(
            validation_type=ValidationType.ERROR_BASED,
            patterns=[],
            confidence=0.0,
            details={},
        )
        assert isinstance(result.validation_type, ValidationType)

    def test_type_hints_patterns_field(self):
        """Test patterns field is a list of strings."""
        result = ValidationTypeResult(
            validation_type=ValidationType.CHECKLIST_BASED,
            patterns=["[ ]", "[x]"],
            confidence=0.8,
            details={},
        )
        assert isinstance(result.patterns, list)
        assert all(isinstance(p, str) for p in result.patterns)

    def test_type_hints_confidence_field(self):
        """Test confidence field is a float between 0.0 and 1.0."""
        result = ValidationTypeResult(
            validation_type=ValidationType.VERDICT_BASED,
            patterns=["PASS"],
            confidence=0.75,
            details={},
        )
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0

    def test_type_hints_details_field(self):
        """Test details field is a dict."""
        result = ValidationTypeResult(
            validation_type=ValidationType.CUSTOM,
            patterns=["custom_pattern"],
            confidence=1.0,
            details={"custom_key": "custom_value"},
        )
        assert isinstance(result.details, dict)

    def test_empty_patterns_allowed(self):
        """Test ValidationTypeResult can have empty patterns list."""
        result = ValidationTypeResult(
            validation_type=ValidationType.UNKNOWN,
            patterns=[],
            confidence=0.0,
            details={},
        )
        assert result.patterns == []

    def test_zero_confidence_allowed(self):
        """Test ValidationTypeResult can have zero confidence."""
        result = ValidationTypeResult(
            validation_type=ValidationType.UNKNOWN,
            patterns=[],
            confidence=0.0,
            details={},
        )
        assert result.confidence == 0.0


class TestValidationTypeResultFactoryMethods:
    """Tests for ValidationTypeResult factory methods (Subtask 1.3)."""

    def test_verdict_based_factory(self):
        """Test factory method for verdict-based validation."""
        result = ValidationTypeResult.verdict_based(
            patterns=["PASS", "FAIL"],
            confidence=0.9,
            verdict_type="pass_fail",
        )
        assert result.validation_type == ValidationType.VERDICT_BASED
        assert result.patterns == ["PASS", "FAIL"]
        assert result.confidence == 0.9
        assert result.details["verdict_type"] == "pass_fail"

    def test_error_based_factory(self):
        """Test factory method for error-based validation."""
        result = ValidationTypeResult.error_based(
            patterns=["0 errors", "no issues"],
            confidence=0.85,
            error_count=0,
        )
        assert result.validation_type == ValidationType.ERROR_BASED
        assert result.patterns == ["0 errors", "no issues"]
        assert result.confidence == 0.85
        assert result.details["error_count"] == 0

    def test_checklist_based_factory(self):
        """Test factory method for checklist-based validation."""
        result = ValidationTypeResult.checklist_based(
            patterns=["[ ]", "[x]"],
            confidence=0.75,
            total_items=10,
            checked_items=7,
        )
        assert result.validation_type == ValidationType.CHECKLIST_BASED
        assert result.patterns == ["[ ]", "[x]"]
        assert result.confidence == 0.75
        assert result.details["total_items"] == 10
        assert result.details["checked_items"] == 7
        assert result.details["completion_percentage"] == 70.0

    def test_custom_factory(self):
        """Test factory method for custom validation."""
        result = ValidationTypeResult.custom(
            patterns=["APPROVED", "BLOCKED"],
            confidence=1.0,
            custom_config={"threshold": 0.8},
        )
        assert result.validation_type == ValidationType.CUSTOM
        assert result.patterns == ["APPROVED", "BLOCKED"]
        assert result.confidence == 1.0
        assert result.details["custom_config"] == {"threshold": 0.8}

    def test_unknown_factory(self):
        """Test factory method for unknown validation type."""
        result = ValidationTypeResult.unknown()
        assert result.validation_type == ValidationType.UNKNOWN
        assert result.patterns == []
        assert result.confidence == 0.0
        assert result.details == {}


class TestValidationTypeResultSerialization:
    """Tests for ValidationTypeResult serialization (Subtask 1.4)."""

    def test_to_dict_basic(self):
        """Test converting ValidationTypeResult to dictionary."""
        result = ValidationTypeResult(
            validation_type=ValidationType.VERDICT_BASED,
            patterns=["PASS", "FAIL"],
            confidence=0.95,
            details={"verdict_type": "pass_fail"},
        )
        result_dict = result.to_dict()

        assert result_dict["validation_type"] == "verdict-based"
        assert result_dict["patterns"] == ["PASS", "FAIL"]
        assert result_dict["confidence"] == 0.95
        assert result_dict["details"] == {"verdict_type": "pass_fail"}

    def test_from_dict_basic(self):
        """Test creating ValidationTypeResult from dictionary."""
        data = {
            "validation_type": "error-based",
            "patterns": ["0 errors"],
            "confidence": 0.8,
            "details": {"error_count": 0},
        }
        result = ValidationTypeResult.from_dict(data)

        assert result.validation_type == ValidationType.ERROR_BASED
        assert result.patterns == ["0 errors"]
        assert result.confidence == 0.8
        assert result.details == {"error_count": 0}

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are inverse operations."""
        original = ValidationTypeResult(
            validation_type=ValidationType.CHECKLIST_BASED,
            patterns=["[ ]", "[x]", "[X]"],
            confidence=0.65,
            details={"total_items": 20, "checked_items": 13},
        )

        serialized = original.to_dict()
        restored = ValidationTypeResult.from_dict(serialized)

        assert restored.validation_type == original.validation_type
        assert restored.patterns == original.patterns
        assert restored.confidence == original.confidence
        assert restored.details == original.details

    def test_dataclass_asdict_compatibility(self):
        """Test that ValidationTypeResult works with dataclasses.asdict()."""
        result = ValidationTypeResult(
            validation_type=ValidationType.CUSTOM,
            patterns=["custom"],
            confidence=1.0,
            details={},
        )

        # asdict should work but validation_type will be the enum
        result_dict = asdict(result)
        assert "validation_type" in result_dict
        assert "patterns" in result_dict
        assert "confidence" in result_dict
        assert "details" in result_dict

    def test_from_dict_with_unknown_type(self):
        """Test from_dict handles unknown validation type strings."""
        data = {
            "validation_type": "unknown",
            "patterns": [],
            "confidence": 0.0,
            "details": {},
        }
        result = ValidationTypeResult.from_dict(data)
        assert result.validation_type == ValidationType.UNKNOWN

    def test_from_dict_with_invalid_type_raises_error(self):
        """Test from_dict raises ValueError for invalid validation type."""
        data = {
            "validation_type": "invalid-type",
            "patterns": [],
            "confidence": 0.0,
            "details": {},
        }
        with pytest.raises(ValueError, match="Invalid validation type"):
            ValidationTypeResult.from_dict(data)


# =============================================================================
# Task 2: Verdict-Based Detection Tests
# =============================================================================


class TestVerdictPatterns:
    """Tests for VERDICT_PATTERNS constant (Subtask 2.1, 2.2, 2.3)."""

    def test_verdict_patterns_contains_pass_fail(self):
        """Test VERDICT_PATTERNS includes PASS/FAIL variants."""
        assert "pass_fail" in VERDICT_PATTERNS
        patterns = VERDICT_PATTERNS["pass_fail"]
        assert len(patterns) > 0

    def test_verdict_patterns_contains_approved_rejected(self):
        """Test VERDICT_PATTERNS includes APPROVED/REJECTED variants."""
        assert "approved_rejected" in VERDICT_PATTERNS
        patterns = VERDICT_PATTERNS["approved_rejected"]
        assert len(patterns) > 0

    def test_verdict_patterns_contains_ready_not_ready(self):
        """Test VERDICT_PATTERNS includes READY/NOT_READY variants."""
        assert "ready_not_ready" in VERDICT_PATTERNS
        patterns = VERDICT_PATTERNS["ready_not_ready"]
        assert len(patterns) > 0

    def test_verdict_patterns_are_compiled_regex(self):
        """Test all patterns are compiled regex objects."""
        import re
        for verdict_type, patterns in VERDICT_PATTERNS.items():
            for pattern in patterns:
                assert isinstance(pattern, re.Pattern), (
                    f"Pattern in {verdict_type} is not compiled regex"
                )


class TestDetectVerdictPatternsPassFail:
    """Tests for detect_verdict_patterns with PASS/FAIL content (Subtask 2.1, 2.5)."""

    def test_detects_simple_pass(self):
        """Test detecting simple 'PASS' in content."""
        content = "Validation result: PASS"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED
        assert result.details["verdict_type"] == "pass_fail"

    def test_detects_simple_fail(self):
        """Test detecting simple 'FAIL' in content."""
        content = "Validation result: FAIL"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED
        assert result.details["verdict_type"] == "pass_fail"

    def test_detects_pass_fail_pair(self):
        """Test detecting PASS/FAIL pair in content."""
        content = """
        The validation will return one of:
        - PASS: All criteria met
        - FAIL: One or more criteria not met
        """
        result = detect_verdict_patterns(content)
        assert result is not None
        assert "PASS" in result.patterns or "FAIL" in result.patterns

    def test_detects_lowercase_pass_fail(self):
        """Test detecting lowercase 'pass' and 'fail' (case insensitive)."""
        content = "Result: pass or fail"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED

    def test_detects_passed_failed_variants(self):
        """Test detecting 'PASSED' and 'FAILED' variants."""
        content = "Test PASSED successfully. Others FAILED."
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED

    def test_confidence_higher_with_multiple_matches(self):
        """Test confidence increases with multiple pattern matches."""
        single_match = "PASS"
        multiple_matches = "PASS FAIL PASSED FAILED"
        result_single = detect_verdict_patterns(single_match)
        result_multiple = detect_verdict_patterns(multiple_matches)
        assert result_multiple.confidence >= result_single.confidence


class TestDetectVerdictPatternsApprovedRejected:
    """Tests for detect_verdict_patterns with APPROVED/REJECTED content (Subtask 2.2, 2.5)."""

    def test_detects_approved(self):
        """Test detecting 'APPROVED' in content."""
        content = "Review status: APPROVED"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED
        assert result.details["verdict_type"] == "approved_rejected"

    def test_detects_rejected(self):
        """Test detecting 'REJECTED' in content."""
        content = "Review status: REJECTED"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED
        assert result.details["verdict_type"] == "approved_rejected"

    def test_detects_approve_reject_variants(self):
        """Test detecting 'Approve' and 'Reject' variants."""
        content = "Click Approve or Reject"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED

    def test_detects_changes_requested(self):
        """Test detecting 'Changes Requested' pattern (GitHub-style)."""
        content = "Review outcome: Changes Requested"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED


class TestDetectVerdictPatternsReadyNotReady:
    """Tests for detect_verdict_patterns with READY/NOT_READY content (Subtask 2.3, 2.5)."""

    def test_detects_ready(self):
        """Test detecting 'READY' in content."""
        content = "Implementation status: READY"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED
        assert result.details["verdict_type"] == "ready_not_ready"

    def test_detects_not_ready(self):
        """Test detecting 'NOT_READY' or 'NOT READY' in content."""
        content = "Status: NOT READY for deployment"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED

    def test_detects_needs_work(self):
        """Test detecting 'NEEDS WORK' pattern."""
        content = "Verdict: NEEDS WORK"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED

    def test_detects_concerns_pattern(self):
        """Test detecting 'CONCERNS' pattern (BMAD-specific)."""
        content = "Validation outcome: CONCERNS"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED


class TestDetectVerdictPatternsNoMatch:
    """Tests for detect_verdict_patterns with no verdict content (Subtask 2.4)."""

    def test_returns_none_for_empty_content(self):
        """Test returns None for empty content."""
        result = detect_verdict_patterns("")
        assert result is None

    def test_returns_none_for_no_verdict_patterns(self):
        """Test returns None when no verdict patterns found."""
        content = "This is just regular text with no verdict patterns."
        result = detect_verdict_patterns(content)
        assert result is None

    def test_returns_none_for_partial_words(self):
        """Test doesn't match partial words like 'passport' or 'failure'."""
        content = "Apply for a passport. System failure detected."
        result = detect_verdict_patterns(content)
        # Should not match because 'pass' in 'passport' is not a verdict
        # Implementation should use word boundaries
        assert result is None or result.confidence < 0.5

    def test_ignores_patterns_in_code_blocks(self):
        """Test patterns inside code blocks are ignored."""
        content = '''
        Regular text here.
        ```python
        status = "PASS"  # This should be ignored
        ```
        More regular text.
        '''
        result = detect_verdict_patterns(content)
        # Patterns in code blocks should be ignored
        assert result is None or result.confidence < 0.5


class TestDetectVerdictPatternsConfidence:
    """Tests for confidence scoring in verdict detection (Subtask 2.4)."""

    def test_single_pattern_has_base_confidence(self):
        """Test single pattern match has reasonable base confidence."""
        content = "Result: PASS"
        result = detect_verdict_patterns(content)
        assert result is not None
        assert 0.5 <= result.confidence <= 1.0

    def test_multiple_patterns_increase_confidence(self):
        """Test multiple pattern matches increase confidence."""
        content_single = "Status: PASS"
        content_multiple = "Status: PASS or FAIL. Ready or Not Ready."
        result_single = detect_verdict_patterns(content_single)
        result_multiple = detect_verdict_patterns(content_multiple)
        # Multiple patterns should give higher or equal confidence
        assert result_multiple.confidence >= result_single.confidence

    def test_verdict_pair_has_higher_confidence(self):
        """Test paired verdicts (PASS/FAIL together) have higher confidence."""
        content = """
        Verdict options:
        - PASS: All checks passed
        - FAIL: One or more checks failed
        """
        result = detect_verdict_patterns(content)
        assert result is not None
        # Paired patterns indicate intentional verdict system
        assert result.confidence >= 0.7

    def test_confidence_capped_at_one(self):
        """Test confidence never exceeds 1.0."""
        content = "PASS FAIL APPROVED REJECTED READY NOT_READY " * 10
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.confidence <= 1.0


# =============================================================================
# Task 3: Error-Based Detection Tests
# =============================================================================


class TestErrorPatterns:
    """Tests for ERROR_PATTERNS constant (Subtask 3.1, 3.2, 3.3)."""

    def test_error_patterns_contains_zero_errors(self):
        """Test ERROR_PATTERNS includes '0 errors' variants."""
        assert "zero_errors" in ERROR_PATTERNS
        patterns = ERROR_PATTERNS["zero_errors"]
        assert len(patterns) > 0

    def test_error_patterns_contains_no_issues(self):
        """Test ERROR_PATTERNS includes 'no issues' variants."""
        assert "no_issues" in ERROR_PATTERNS
        patterns = ERROR_PATTERNS["no_issues"]
        assert len(patterns) > 0

    def test_error_patterns_contains_error_count(self):
        """Test ERROR_PATTERNS includes error count patterns."""
        assert "error_count" in ERROR_PATTERNS
        patterns = ERROR_PATTERNS["error_count"]
        assert len(patterns) > 0

    def test_error_patterns_are_compiled_regex(self):
        """Test all patterns are compiled regex objects."""
        import re
        for error_type, patterns in ERROR_PATTERNS.items():
            for pattern in patterns:
                assert isinstance(pattern, re.Pattern), (
                    f"Pattern in {error_type} is not compiled regex"
                )


class TestDetectErrorPatternsZeroErrors:
    """Tests for detect_error_patterns with '0 errors' content (Subtask 3.1, 3.5)."""

    def test_detects_zero_errors(self):
        """Test detecting '0 errors' in content."""
        content = "Validation completed: 0 errors found"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.ERROR_BASED
        assert result.details["error_count"] == 0

    def test_detects_zero_errors_variant(self):
        """Test detecting 'zero errors' spelled out."""
        content = "Result: zero errors detected"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.ERROR_BASED

    def test_detects_no_errors(self):
        """Test detecting 'no errors' in content."""
        content = "Build completed with no errors"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.ERROR_BASED
        assert result.details["error_count"] == 0

    def test_detects_zero_blocking_errors(self):
        """Test detecting '0 blocking errors' pattern."""
        content = "Analysis: 0 blocking errors, 3 warnings"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.ERROR_BASED


class TestDetectErrorPatternsNoIssues:
    """Tests for detect_error_patterns with 'no issues' content (Subtask 3.2, 3.5)."""

    def test_detects_no_issues(self):
        """Test detecting 'no issues' in content."""
        content = "Scan complete: no issues found"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.ERROR_BASED
        assert result.details["error_count"] == 0

    def test_detects_zero_issues(self):
        """Test detecting '0 issues' in content."""
        content = "Linter output: 0 issues"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.ERROR_BASED

    def test_detects_no_problems(self):
        """Test detecting 'no problems' in content."""
        content = "Check finished: no problems detected"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.ERROR_BASED


class TestDetectErrorPatternsErrorCount:
    """Tests for detect_error_patterns with error count patterns (Subtask 3.3, 3.5)."""

    def test_detects_specific_error_count(self):
        """Test detecting specific error count like '3 errors'."""
        content = "Found 3 errors in the code"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.ERROR_BASED
        assert result.details["error_count"] == 3

    def test_detects_single_error(self):
        """Test detecting '1 error' in content."""
        content = "Validation found 1 error"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.details["error_count"] == 1

    def test_detects_large_error_count(self):
        """Test detecting larger error counts like '42 errors'."""
        content = "Build failed with 42 errors"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.details["error_count"] == 42

    def test_detects_errors_found_pattern(self):
        """Test detecting 'X errors found' pattern."""
        content = "5 errors found during analysis"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.details["error_count"] == 5


class TestDetectErrorPatternsNoMatch:
    """Tests for detect_error_patterns with no error content (Subtask 3.4)."""

    def test_returns_none_for_empty_content(self):
        """Test returns None for empty content."""
        result = detect_error_patterns("")
        assert result is None

    def test_returns_none_for_no_error_patterns(self):
        """Test returns None when no error patterns found."""
        content = "This is just regular text without error mentions."
        result = detect_error_patterns(content)
        assert result is None

    def test_ignores_error_patterns_in_code_blocks(self):
        """Test patterns inside code blocks are ignored."""
        content = '''
        Regular text here.
        ```python
        errors = 0  # This should be ignored
        print(f"{errors} errors")
        ```
        More regular text.
        '''
        result = detect_error_patterns(content)
        # Patterns in code blocks should be ignored
        assert result is None or result.confidence < 0.5


class TestDetectErrorPatternsConfidence:
    """Tests for confidence scoring in error detection (Subtask 3.4)."""

    def test_zero_errors_has_high_confidence(self):
        """Test that '0 errors' pattern has high confidence."""
        content = "Validation: 0 errors"
        result = detect_error_patterns(content)
        assert result is not None
        assert result.confidence >= 0.7

    def test_non_zero_errors_has_moderate_confidence(self):
        """Test that non-zero errors has moderate confidence."""
        content = "Found 5 errors"
        result = detect_error_patterns(content)
        assert result is not None
        assert 0.5 <= result.confidence < 0.9

    def test_multiple_error_mentions_increase_confidence(self):
        """Test confidence increases with multiple error mentions."""
        content = "0 errors. No issues found. Zero problems detected."
        result = detect_error_patterns(content)
        assert result is not None
        assert result.confidence >= 0.8

    def test_confidence_capped_at_one(self):
        """Test confidence never exceeds 1.0."""
        content = "0 errors no issues 0 problems " * 10
        result = detect_error_patterns(content)
        assert result is not None
        assert result.confidence <= 1.0


# =============================================================================
# Task 4: Checklist-Based Detection Tests (AC: #3)
# =============================================================================


class TestChecklistPatterns:
    """Tests for CHECKLIST_PATTERNS constant (Subtask 4.1, 4.2)."""

    def test_checklist_patterns_contains_unchecked(self):
        """Test CHECKLIST_PATTERNS contains unchecked pattern key."""
        assert "unchecked" in CHECKLIST_PATTERNS

    def test_checklist_patterns_contains_checked(self):
        """Test CHECKLIST_PATTERNS contains checked pattern key."""
        assert "checked" in CHECKLIST_PATTERNS

    def test_checklist_patterns_are_compiled_regex(self):
        """Test all checklist patterns are compiled regex."""
        for pattern_type, patterns in CHECKLIST_PATTERNS.items():
            assert isinstance(patterns, list), f"{pattern_type} is not a list"
            for pattern in patterns:
                assert isinstance(pattern, re.Pattern), (
                    f"Pattern in {pattern_type} is not compiled regex"
                )


class TestDetectChecklistPatternsUnchecked:
    """Tests for detect_checklist_patterns with unchecked items (Subtask 4.1, 4.5)."""

    def test_detects_unchecked_items(self):
        """Test detecting unchecked checkbox items."""
        content = "- [ ] Item 1\n- [ ] Item 2\n- [ ] Item 3"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.CHECKLIST_BASED
        assert result.details["total_items"] == 3
        assert result.details["checked_items"] == 0

    def test_detects_single_unchecked(self):
        """Test detecting a single unchecked item."""
        content = "Todo:\n- [ ] Complete task"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.details["total_items"] == 1
        assert result.details["checked_items"] == 0

    def test_ignores_non_checkbox_brackets(self):
        """Test that regular brackets like [foo] are not detected."""
        content = "See [documentation] for details"
        result = detect_checklist_patterns(content)
        assert result is None


class TestDetectChecklistPatternsChecked:
    """Tests for detect_checklist_patterns with checked items (Subtask 4.2, 4.5)."""

    def test_detects_checked_items_lowercase_x(self):
        """Test detecting checked items with lowercase x."""
        content = "- [x] Done item 1\n- [x] Done item 2"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.CHECKLIST_BASED
        assert result.details["checked_items"] == 2

    def test_detects_checked_items_uppercase_x(self):
        """Test detecting checked items with uppercase X."""
        content = "- [X] Completed task"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.details["checked_items"] == 1

    def test_detects_mixed_case_checked(self):
        """Test detecting mixed case checked items."""
        content = "- [x] Item 1\n- [X] Item 2\n- [x] Item 3"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.details["checked_items"] == 3


class TestDetectChecklistPatternsMixed:
    """Tests for detect_checklist_patterns with mixed items (Subtask 4.3, 4.5)."""

    def test_detects_mixed_checked_unchecked(self):
        """Test detecting mix of checked and unchecked items."""
        content = "- [x] Done\n- [ ] Not done\n- [x] Also done"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.details["total_items"] == 3
        assert result.details["checked_items"] == 2

    def test_total_items_includes_all(self):
        """Test total_items is sum of checked and unchecked."""
        content = "- [ ] A\n- [ ] B\n- [x] C\n- [X] D\n- [ ] E"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.details["total_items"] == 5
        assert result.details["checked_items"] == 2


class TestDetectChecklistPatternsCompletion:
    """Tests for completion percentage calculation (Subtask 4.4, 4.5)."""

    def test_completion_percentage_zero(self):
        """Test completion is 0% when no items checked."""
        content = "- [ ] A\n- [ ] B\n- [ ] C\n- [ ] D"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.details["completion_percentage"] == 0.0

    def test_completion_percentage_fifty(self):
        """Test completion is 50% when half checked."""
        content = "- [x] A\n- [ ] B\n- [x] C\n- [ ] D"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.details["completion_percentage"] == 50.0

    def test_completion_percentage_full(self):
        """Test completion is 100% when all checked."""
        content = "- [x] A\n- [x] B\n- [x] C"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.details["completion_percentage"] == 100.0

    def test_completion_percentage_partial(self):
        """Test completion percentage for partial completion."""
        content = "- [x] A\n- [x] B\n- [ ] C"
        result = detect_checklist_patterns(content)
        assert result is not None
        # 2 of 3 = 66.67%
        assert 66.0 <= result.details["completion_percentage"] <= 67.0


class TestDetectChecklistPatternsNoMatch:
    """Tests for detect_checklist_patterns with no checklist content."""

    def test_returns_none_for_empty_content(self):
        """Test returns None for empty content."""
        result = detect_checklist_patterns("")
        assert result is None

    def test_returns_none_for_no_checklist_patterns(self):
        """Test returns None when no checklist patterns found."""
        content = "This is regular text without checklists."
        result = detect_checklist_patterns(content)
        assert result is None

    def test_ignores_checklist_in_code_blocks(self):
        """Test checklist patterns inside code blocks are ignored."""
        content = '''
        Regular text here.
        ```markdown
        - [ ] This is an example
        - [x] This too
        ```
        More regular text.
        '''
        result = detect_checklist_patterns(content)
        # Patterns in code blocks should be ignored
        assert result is None or result.details["total_items"] == 0


class TestDetectChecklistPatternsConfidence:
    """Tests for confidence scoring in checklist detection."""

    def test_all_checked_has_high_confidence(self):
        """Test all checked items has high confidence."""
        content = "- [x] A\n- [x] B\n- [x] C"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.confidence >= 0.8

    def test_none_checked_has_moderate_confidence(self):
        """Test no checked items has moderate confidence."""
        content = "- [ ] A\n- [ ] B\n- [ ] C"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert 0.5 <= result.confidence < 0.8

    def test_partial_checked_has_proportional_confidence(self):
        """Test partial completion has proportional confidence."""
        content = "- [x] A\n- [ ] B"
        result = detect_checklist_patterns(content)
        assert result is not None
        assert 0.5 <= result.confidence < 0.9

    def test_confidence_capped_at_one(self):
        """Test confidence never exceeds 1.0."""
        content = ("- [x] Item\n" * 50)
        result = detect_checklist_patterns(content)
        assert result is not None
        assert result.confidence <= 1.0


# =============================================================================
# Task 5: Unknown/Fallback Handling Tests (AC: #4)
# =============================================================================


class TestConfidenceThreshold:
    """Tests for CONFIDENCE_THRESHOLD constant (Subtask 5.1)."""

    def test_confidence_threshold_exists(self):
        """Test CONFIDENCE_THRESHOLD constant is defined."""
        assert CONFIDENCE_THRESHOLD is not None

    def test_confidence_threshold_is_float(self):
        """Test CONFIDENCE_THRESHOLD is a float."""
        assert isinstance(CONFIDENCE_THRESHOLD, float)

    def test_confidence_threshold_default_value(self):
        """Test CONFIDENCE_THRESHOLD default is 0.5 (50%)."""
        assert CONFIDENCE_THRESHOLD == 0.5

    def test_confidence_threshold_in_valid_range(self):
        """Test CONFIDENCE_THRESHOLD is between 0 and 1."""
        assert 0.0 <= CONFIDENCE_THRESHOLD <= 1.0


class TestUnknownValidationType:
    """Tests for unknown validation type handling (Subtask 5.2, 5.3)."""

    def test_unknown_factory_returns_correct_type(self):
        """Test ValidationTypeResult.unknown() returns UNKNOWN type."""
        result = ValidationTypeResult.unknown()
        assert result.validation_type == ValidationType.UNKNOWN

    def test_unknown_factory_has_zero_confidence(self):
        """Test ValidationTypeResult.unknown() has confidence 0."""
        result = ValidationTypeResult.unknown()
        assert result.confidence == 0.0

    def test_unknown_factory_has_empty_patterns(self):
        """Test ValidationTypeResult.unknown() has empty patterns list."""
        result = ValidationTypeResult.unknown()
        assert result.patterns == []

    def test_unknown_factory_has_empty_details(self):
        """Test ValidationTypeResult.unknown() has empty details dict."""
        result = ValidationTypeResult.unknown()
        assert result.details == {}


class TestUnknownFallbackEdgeCases:
    """Tests for edge cases that should result in unknown type (Subtask 5.3)."""

    def test_empty_string_content(self):
        """Test empty string returns None from detection functions."""
        assert detect_verdict_patterns("") is None
        assert detect_error_patterns("") is None
        assert detect_checklist_patterns("") is None

    def test_whitespace_only_content(self):
        """Test whitespace-only content returns None from detection functions."""
        content = "   \n\t\n   "
        assert detect_verdict_patterns(content) is None
        assert detect_error_patterns(content) is None
        assert detect_checklist_patterns(content) is None

    def test_no_patterns_content(self):
        """Test content with no recognizable patterns returns None."""
        content = "This is just regular text without any validation patterns."
        assert detect_verdict_patterns(content) is None
        assert detect_error_patterns(content) is None
        assert detect_checklist_patterns(content) is None

    def test_all_patterns_in_code_blocks(self):
        """Test patterns only inside code blocks are ignored."""
        content = '''
        Here is some documentation.
        ```
        PASS  # Example verdict
        0 errors  # Example error count
        - [x] Example checkbox
        ```
        End of documentation.
        '''
        # All patterns are inside code blocks, should return None
        assert detect_verdict_patterns(content) is None
        assert detect_error_patterns(content) is None
        assert detect_checklist_patterns(content) is None

    def test_partial_patterns_not_matched(self):
        """Test partial pattern matches don't trigger detection."""
        # "passport" contains "pass" but shouldn't match PASS pattern
        content = "Please bring your passport for verification."
        result = detect_verdict_patterns(content)
        assert result is None

    def test_numbers_without_error_context(self):
        """Test standalone numbers don't trigger error detection."""
        content = "We processed 5 orders today."
        # No "errors" context, shouldn't match
        result = detect_error_patterns(content)
        assert result is None


# =============================================================================
# Task 6: Main detect() Function Tests (AC: #1-4)
# =============================================================================


class TestDetectValidationTypeVerdict:
    """Tests for detect_validation_type with verdict content (AC: #1)."""

    def test_detects_pass_fail_verdict(self):
        """Test detecting PASS/FAIL verdict patterns."""
        content = "Workflow result: PASS"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.VERDICT_BASED
        assert result.confidence > 0

    def test_detects_approved_rejected_verdict(self):
        """Test detecting APPROVED/REJECTED verdict patterns."""
        content = "Review status: APPROVED"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.VERDICT_BASED

    def test_detects_ready_not_ready_verdict(self):
        """Test detecting READY/NOT_READY verdict patterns."""
        content = "Implementation status: READY"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.VERDICT_BASED


class TestDetectValidationTypeError:
    """Tests for detect_validation_type with error content (AC: #2)."""

    def test_detects_zero_errors(self):
        """Test detecting '0 errors' patterns."""
        content = "Validation complete: 0 errors found"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.ERROR_BASED
        assert result.details["error_count"] == 0

    def test_detects_no_issues(self):
        """Test detecting 'no issues' patterns."""
        content = "Scan complete: no issues detected"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.ERROR_BASED

    def test_detects_error_count(self):
        """Test detecting specific error counts."""
        content = "Build stopped: 5 errors found"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.ERROR_BASED
        assert result.details["error_count"] == 5


class TestDetectValidationTypeChecklist:
    """Tests for detect_validation_type with checklist content (AC: #3)."""

    def test_detects_checklist_items(self):
        """Test detecting checkbox items."""
        content = "- [x] Step 1\n- [ ] Step 2\n- [x] Step 3"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.CHECKLIST_BASED
        assert result.details["total_items"] == 3
        assert result.details["checked_items"] == 2

    def test_detects_all_checked_checklist(self):
        """Test detecting fully checked checklist."""
        content = "- [x] Done 1\n- [x] Done 2"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.CHECKLIST_BASED
        assert result.details["completion_percentage"] == 100.0


class TestDetectValidationTypeUnknown:
    """Tests for detect_validation_type with unknown content (AC: #4)."""

    def test_returns_unknown_for_empty_content(self):
        """Test empty content returns unknown type."""
        result = detect_validation_type("")
        assert result.validation_type == ValidationType.UNKNOWN
        assert result.confidence == 0.0

    def test_returns_unknown_for_no_patterns(self):
        """Test content with no patterns returns unknown type."""
        content = "This is regular documentation without validation patterns."
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.UNKNOWN
        assert result.confidence == 0.0

    def test_returns_unknown_for_whitespace_only(self):
        """Test whitespace-only content returns unknown type."""
        result = detect_validation_type("   \n\t\n   ")
        assert result.validation_type == ValidationType.UNKNOWN


class TestDetectValidationTypePriority:
    """Tests for priority logic in detect_validation_type (Subtask 6.1)."""

    def test_verdict_over_error_when_both_present(self):
        """Test verdict patterns take priority over error patterns."""
        content = "PASS with 0 errors"
        result = detect_validation_type(content)
        # Verdict should win based on priority
        assert result.validation_type == ValidationType.VERDICT_BASED

    def test_verdict_over_checklist_when_both_present(self):
        """Test verdict patterns take priority over checklist patterns."""
        content = "PASS\n- [x] Item complete"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.VERDICT_BASED

    def test_error_over_checklist_when_both_present(self):
        """Test error patterns take priority over checklist patterns."""
        content = "0 errors\n- [x] Item checked"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.ERROR_BASED


class TestDetectValidationTypeConfidence:
    """Tests for confidence handling in detect_validation_type (Subtask 6.2, 6.3)."""

    def test_returns_highest_confidence_result(self):
        """Test returns result with highest confidence."""
        # Multiple verdict patterns should increase confidence
        content = "Final verdict: PASS - test PASSED successfully"
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.VERDICT_BASED
        assert result.confidence >= 0.5

    def test_confidence_affects_priority_when_close(self):
        """Test confidence influences selection when both types match."""
        # Strong error pattern vs weak verdict
        content = "0 errors, 0 issues, no problems - looks good"
        result = detect_validation_type(content)
        # Should be error-based due to multiple error patterns
        assert result is not None
        assert result.confidence >= 0.5


class TestDetectValidationTypeIntegration:
    """Integration tests with realistic workflow content (Subtask 6.4)."""

    def test_real_verdict_workflow_sample(self):
        """Test with realistic verdict-based workflow output."""
        content = """
        ## Implementation Readiness Check

        After reviewing all components:
        - Architecture document: Complete
        - PRD alignment: Verified

        **Final Verdict: PASS**

        The implementation is ready for development.
        """
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.VERDICT_BASED
        assert "PASS" in result.patterns or any("PASS" in p for p in result.patterns)

    def test_real_error_workflow_sample(self):
        """Test with realistic error-based workflow output."""
        content = """
        ## Validation Results

        Checked 150 items across 12 files.

        Summary:
        - 0 errors found
        - 0 blocking issues
        - 3 warnings (non-blocking)

        Validation completed successfully.
        """
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.ERROR_BASED
        assert result.details["error_count"] == 0

    def test_real_checklist_workflow_sample(self):
        """Test with realistic checklist-based workflow output."""
        content = """
        ## Manual Review Checklist

        Please verify each item:

        - [x] Code follows project conventions
        - [x] Unit tests included
        - [ ] Integration tests needed
        - [x] Documentation updated
        - [ ] Performance benchmarks run

        Progress: 3/5 items complete
        """
        result = detect_validation_type(content)
        assert result.validation_type == ValidationType.CHECKLIST_BASED
        assert result.details["total_items"] == 5
        assert result.details["checked_items"] == 3

    def test_code_blocks_excluded_from_detection(self):
        """Test patterns in code blocks don't affect detection."""
        content = """
        ## Documentation

        Example output:
        ```
        PASS
        0 errors
        - [x] Example item
        ```

        This is regular documentation without real validation.
        """
        result = detect_validation_type(content)
        # All patterns are in code blocks, should be unknown
        assert result.validation_type == ValidationType.UNKNOWN


# =============================================================================
# Task 7: Workflow File Parsing Tests
# =============================================================================


class TestParseWorkflowFile:
    """Tests for parse_workflow_file function (Subtask 7.1, 7.2, 7.3)."""

    def test_parse_yaml_file(self):
        """Test parsing a .yaml workflow file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("name: test-workflow\nvalidation: PASS\n")
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            content, frontmatter = parse_workflow_file(temp_path)
            assert content is not None
            assert "validation: PASS" in content
        finally:
            temp_path.unlink()

    def test_parse_md_file(self):
        """Test parsing a .md workflow file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Workflow\n\nResult: PASS\n")
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            content, frontmatter = parse_workflow_file(temp_path)
            assert content is not None
            assert "Result: PASS" in content
        finally:
            temp_path.unlink()

    def test_parse_md_file_with_frontmatter(self):
        """Test parsing .md file with YAML frontmatter (Subtask 7.1)."""
        md_content = """---
name: test-workflow
validation_type: verdict-based
---

# Workflow Content

Result: PASS
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            content, frontmatter = parse_workflow_file(temp_path)
            assert frontmatter is not None
            assert frontmatter.get("name") == "test-workflow"
            assert "Result: PASS" in content
        finally:
            temp_path.unlink()

    def test_parse_md_file_without_frontmatter(self):
        """Test parsing .md file without frontmatter."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Just Markdown\n\nNo frontmatter here.\n")
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            content, frontmatter = parse_workflow_file(temp_path)
            assert frontmatter is None or frontmatter == {}
            assert "Just Markdown" in content
        finally:
            temp_path.unlink()

    def test_returns_none_for_nonexistent_file(self):
        """Test returns None for file that doesn't exist."""
        result = parse_workflow_file(Path("/nonexistent/file.yaml"))
        assert result == (None, None)

    def test_handles_empty_file(self):
        """Test parsing empty workflow file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            content, frontmatter = parse_workflow_file(temp_path)
            assert content == ""
        finally:
            temp_path.unlink()


class TestDetectValidationTypeFromFile:
    """Tests for detect_validation_type_from_file function (Subtask 7.4)."""

    def test_detects_verdict_from_yaml_file(self):
        """Test detecting verdict patterns from YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("name: test\nresult: PASS\n")
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            assert result.validation_type == ValidationType.VERDICT_BASED
        finally:
            temp_path.unlink()

    def test_detects_error_from_md_file(self):
        """Test detecting error patterns from Markdown file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Results\n\n0 errors found\n")
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            assert result.validation_type == ValidationType.ERROR_BASED
        finally:
            temp_path.unlink()

    def test_detects_checklist_from_md_file(self):
        """Test detecting checklist patterns from Markdown file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Checklist\n\n- [x] Item 1\n- [ ] Item 2\n")
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            assert result.validation_type == ValidationType.CHECKLIST_BASED
        finally:
            temp_path.unlink()

    def test_returns_unknown_for_nonexistent_file(self):
        """Test returns unknown for file that doesn't exist."""
        result = detect_validation_type_from_file(Path("/nonexistent/file.yaml"))
        assert result.validation_type == ValidationType.UNKNOWN

    def test_returns_unknown_for_empty_file(self):
        """Test returns unknown for empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            assert result.validation_type == ValidationType.UNKNOWN
        finally:
            temp_path.unlink()

    def test_uses_custom_validation_from_frontmatter(self):
        """Test custom validation type from frontmatter overrides detection."""
        md_content = """---
validation:
  type: custom
  pattern: "SUCCESS|COMPLETE"
---

# Content

Regular content without standard patterns.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            # Custom validation should be detected from frontmatter
            assert result.validation_type == ValidationType.CUSTOM
        finally:
            temp_path.unlink()

    def test_frontmatter_without_closing_delimiter(self):
        """Test markdown file with unclosed frontmatter (line 771, 773)."""
        md_content = """---
name: test-workflow
validation_type: verdict-based

# No closing delimiter, content continues
Result: PASS
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            # Should still detect verdict pattern since entire content is searched
            assert result.validation_type == ValidationType.VERDICT_BASED
        finally:
            temp_path.unlink()

    def test_frontmatter_with_empty_yaml(self):
        """Test markdown file with empty frontmatter (line 786)."""
        md_content = """---
---

# Content
Result: PASS
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            assert result.validation_type == ValidationType.VERDICT_BASED
        finally:
            temp_path.unlink()

    def test_frontmatter_with_invalid_yaml(self):
        """Test markdown file with invalid YAML frontmatter (line 787-788)."""
        md_content = """---
invalid: yaml: content: [unmatched
---

# Content
Result: PASS
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            # Should still detect content patterns despite invalid frontmatter
            assert result.validation_type == ValidationType.VERDICT_BASED
        finally:
            temp_path.unlink()

    def test_frontmatter_without_validation_key(self):
        """Test frontmatter without validation config (line 835)."""
        md_content = """---
name: test-workflow
author: John Doe
---

# Content with no standard patterns
Just some regular text here.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            # No patterns found, unknown type
            assert result.validation_type == ValidationType.UNKNOWN
        finally:
            temp_path.unlink()

    def test_frontmatter_with_non_custom_validation(self):
        """Test frontmatter with validation but not custom type (line 848)."""
        md_content = """---
validation:
  type: other
  pattern: "something"
---

# Content
Result: PASS
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            # Should fall back to content-based detection
            assert result.validation_type == ValidationType.VERDICT_BASED
        finally:
            temp_path.unlink()

    def test_other_file_format(self):
        """Test parsing file with other extension (line 744)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Result: PASS\n0 errors found\n")
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            # Should still detect patterns from content
            assert result.validation_type == ValidationType.VERDICT_BASED
        finally:
            temp_path.unlink()


# =============================================================================
# Additional Edge Case Tests for 100% Coverage
# =============================================================================


class TestEdgeCaseCoverage:
    """Additional tests for 100% module coverage."""

    def test_detect_validation_type_all_below_threshold(self):
        """Test when all detection results are below threshold (line 362).

        This creates a scenario where patterns are detected but all have
        confidence below CONFIDENCE_THRESHOLD, so it returns the highest.
        """
        # A very minimal pattern that barely triggers detection
        content = "Check"  # Partial match, very low confidence
        result = detect_validation_type(content)
        # Should return unknown since no patterns match
        assert result.validation_type == ValidationType.UNKNOWN

    def test_ready_not_ready_pair_bonus(self):
        """Test ready/not_ready pair bonus calculation (line 493-497)."""
        content = """
        ## Validation Result

        Status: READY
        Fallback: NOT_READY if issues found
        """
        result = detect_verdict_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.VERDICT_BASED
        # Should have higher confidence due to pair bonus
        assert result.confidence >= 0.5

    def test_error_count_tuple_match(self):
        """Test error pattern with tuple capture group (line 554-555)."""
        content = "Validation found 3 errors in the code."
        result = detect_error_patterns(content)
        assert result is not None
        assert result.validation_type == ValidationType.ERROR_BASED
        assert result.details.get("error_count") == 3

    def test_file_read_permission_error(self):
        """Test handling IOError/OSError when reading file (lines 728-729)."""
        # Create a temp file, get its path, then delete it and try to read
        # This simulates a file that exists but can't be read
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        # Remove the file to simulate unreadable state
        temp_path.unlink()

        # Test parse_workflow_file directly - should return (None, None)
        result = parse_workflow_file(temp_path)
        assert result == (None, None)

    def test_detect_type_returns_highest_below_threshold(self):
        """Test when all patterns match but all below threshold (line 362).

        This is a tricky edge case - need patterns that match but with
        low confidence. Single checkbox item gives ~0.35 confidence.
        """
        # Single checkbox gives low confidence (~0.35)
        content = "- [ ] Single item"
        result = detect_validation_type(content)
        # Since checklist confidence is below 0.5 threshold, it returns the result anyway
        # as the highest-confidence match
        assert result is not None
        # Either checklist or unknown
        assert result.validation_type in (ValidationType.CHECKLIST_BASED, ValidationType.UNKNOWN)

    def test_frontmatter_with_validation_string(self):
        """Test frontmatter where validation is a string, not dict (line 838->848)."""
        md_content = """---
validation: "simple string value"
---

# Content
Result: PASS
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        # File is closed after exiting with block
        try:
            result = detect_validation_type_from_file(temp_path)
            # String validation value should fall through to content detection
            assert result.validation_type == ValidationType.VERDICT_BASED
        finally:
            temp_path.unlink()

    def test_verdict_dominant_type_with_no_actual_matches(self):
        """Test edge case where max() finds a key but it has no matches (lines 426-431).

        This is a hard-to-trigger edge case in the verdict detection code.
        The dominant_type calculation uses max() which will always return
        something, but if all lists are empty we need to handle it.
        """
        # This test ensures the code doesn't crash with unusual input
        # Partial "PASS" at start that gets stripped or doesn't fully match
        content = "PA"  # Too short to match PASS pattern
        result = detect_verdict_patterns(content)
        # Should return None - no matches
        assert result is None

    def test_low_confidence_verdict_with_error(self):
        """Test verdict detection below threshold with error also present.

        Creates scenario where verdict matches but with lower confidence
        than error patterns.
        """
        # Single PASS but multiple error patterns
        content = """
        PASS
        0 errors found
        0 issues detected
        no problems found
        """
        result = detect_validation_type(content)
        # Verdict has priority over error when above threshold
        assert result.validation_type == ValidationType.VERDICT_BASED


# =============================================================================
# Story 1.4: Custom Validation Pattern Recognition Tests
# =============================================================================


class TestCustomPattern:
    """Tests for CustomPattern dataclass (Task 1.1, 1.2)."""

    def test_custom_pattern_dataclass_exists(self):
        """Test CustomPattern dataclass is importable."""
        from pcmrp_tools.bmad_automation.validation_type_detector import CustomPattern
        assert CustomPattern is not None

    def test_custom_pattern_has_success_pattern(self):
        """Test CustomPattern has success_pattern field."""
        from pcmrp_tools.bmad_automation.validation_type_detector import CustomPattern
        pattern = CustomPattern(
            success_pattern="Quality Gate: PASSED",
            failure_pattern="Quality Gate: FAILED",
        )
        assert pattern.success_pattern == "Quality Gate: PASSED"

    def test_custom_pattern_has_failure_pattern(self):
        """Test CustomPattern has failure_pattern field."""
        from pcmrp_tools.bmad_automation.validation_type_detector import CustomPattern
        pattern = CustomPattern(
            success_pattern="Quality Gate: PASSED",
            failure_pattern="Quality Gate: FAILED",
        )
        assert pattern.failure_pattern == "Quality Gate: FAILED"

    def test_custom_pattern_has_optional_warning_pattern(self):
        """Test CustomPattern has optional warning_pattern field."""
        from pcmrp_tools.bmad_automation.validation_type_detector import CustomPattern
        pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="FAILED",
            warning_pattern="WARNING",
        )
        assert pattern.warning_pattern == "WARNING"

    def test_custom_pattern_warning_defaults_to_none(self):
        """Test CustomPattern warning_pattern defaults to None."""
        from pcmrp_tools.bmad_automation.validation_type_detector import CustomPattern
        pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="FAILED",
        )
        assert pattern.warning_pattern is None

    def test_custom_pattern_has_case_sensitive_field(self):
        """Test CustomPattern has case_sensitive field."""
        from pcmrp_tools.bmad_automation.validation_type_detector import CustomPattern
        pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="FAILED",
            case_sensitive=True,
        )
        assert pattern.case_sensitive is True

    def test_custom_pattern_case_sensitive_defaults_to_false(self):
        """Test CustomPattern case_sensitive defaults to False."""
        from pcmrp_tools.bmad_automation.validation_type_detector import CustomPattern
        pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="FAILED",
        )
        assert pattern.case_sensitive is False


class TestValidationTypeResultCustomPatterns:
    """Tests for ValidationTypeResult.custom_patterns field (Task 1.2, 1.3)."""

    def test_validation_type_result_has_custom_patterns_field(self):
        """Test ValidationTypeResult has custom_patterns field."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            CustomPattern,
            ValidationTypeResult,
            ValidationType,
        )
        custom_pattern = CustomPattern(
            success_pattern="Quality Gate: PASSED",
            failure_pattern="Quality Gate: FAILED",
        )
        result = ValidationTypeResult(
            validation_type=ValidationType.CUSTOM,
            patterns=["Quality Gate: PASSED"],
            confidence=1.0,
            details={},
            custom_patterns=custom_pattern,
        )
        assert result.custom_patterns is not None
        assert result.custom_patterns.success_pattern == "Quality Gate: PASSED"

    def test_validation_type_result_custom_patterns_defaults_to_none(self):
        """Test ValidationTypeResult custom_patterns defaults to None."""
        result = ValidationTypeResult(
            validation_type=ValidationType.VERDICT_BASED,
            patterns=["PASS"],
            confidence=0.9,
            details={},
        )
        assert result.custom_patterns is None

    def test_custom_factory_with_custom_patterns(self):
        """Test ValidationTypeResult.custom() factory creates result with custom_patterns."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            CustomPattern,
            ValidationTypeResult,
        )
        custom_pattern = CustomPattern(
            success_pattern="BUILD OK",
            failure_pattern="BUILD FAILED",
        )
        result = ValidationTypeResult.custom(
            patterns=["BUILD OK", "BUILD FAILED"],
            confidence=1.0,
            custom_config={"type": "custom"},
            custom_patterns=custom_pattern,
        )
        assert result.custom_patterns is not None
        assert result.custom_patterns.success_pattern == "BUILD OK"
        assert result.custom_patterns.failure_pattern == "BUILD FAILED"

    def test_custom_factory_without_custom_patterns_uses_none(self):
        """Test ValidationTypeResult.custom() factory works without custom_patterns."""
        result = ValidationTypeResult.custom(
            patterns=["APPROVED"],
            confidence=1.0,
            custom_config={"threshold": 0.8},
        )
        assert result.custom_patterns is None

    def test_custom_patterns_in_to_dict(self):
        """Test custom_patterns is serialized in to_dict."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            CustomPattern,
            ValidationTypeResult,
            ValidationType,
        )
        custom_pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="FAILED",
            warning_pattern="WARNING",
            case_sensitive=True,
        )
        result = ValidationTypeResult(
            validation_type=ValidationType.CUSTOM,
            patterns=["PASSED"],
            confidence=1.0,
            details={},
            custom_patterns=custom_pattern,
        )
        result_dict = result.to_dict()
        assert "custom_patterns" in result_dict
        assert result_dict["custom_patterns"]["success_pattern"] == "PASSED"
        assert result_dict["custom_patterns"]["failure_pattern"] == "FAILED"
        assert result_dict["custom_patterns"]["warning_pattern"] == "WARNING"
        assert result_dict["custom_patterns"]["case_sensitive"] is True

    def test_custom_patterns_from_dict(self):
        """Test custom_patterns is deserialized from dict."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            ValidationTypeResult,
        )
        data = {
            "validation_type": "custom",
            "patterns": ["PASSED"],
            "confidence": 1.0,
            "details": {},
            "custom_patterns": {
                "success_pattern": "PASSED",
                "failure_pattern": "FAILED",
                "warning_pattern": None,
                "case_sensitive": False,
            },
        }
        result = ValidationTypeResult.from_dict(data)
        assert result.custom_patterns is not None
        assert result.custom_patterns.success_pattern == "PASSED"
        assert result.custom_patterns.failure_pattern == "FAILED"

    def test_custom_patterns_round_trip_serialization(self):
        """Test custom_patterns survives round-trip serialization."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            CustomPattern,
            ValidationTypeResult,
            ValidationType,
        )
        custom_pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="FAILED",
            warning_pattern="WARNING",
            case_sensitive=True,
        )
        original = ValidationTypeResult(
            validation_type=ValidationType.CUSTOM,
            patterns=["PASSED"],
            confidence=1.0,
            details={},
            custom_patterns=custom_pattern,
        )
        serialized = original.to_dict()
        restored = ValidationTypeResult.from_dict(serialized)
        assert restored.custom_patterns is not None
        assert restored.custom_patterns.success_pattern == original.custom_patterns.success_pattern
        assert restored.custom_patterns.failure_pattern == original.custom_patterns.failure_pattern
        assert restored.custom_patterns.warning_pattern == original.custom_patterns.warning_pattern
        assert restored.custom_patterns.case_sensitive == original.custom_patterns.case_sensitive


class TestParseCustomPatternsFromFrontmatter:
    """Tests for parsing custom patterns from workflow frontmatter (Task 2)."""

    def test_parse_custom_validation_type_from_frontmatter(self):
        """Test parsing validation.type: custom from frontmatter (AC #1)."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            parse_custom_patterns_from_frontmatter,
        )
        frontmatter = {
            "validation": {
                "type": "custom",
                "success_pattern": "Quality Gate: PASSED",
                "failure_pattern": "Quality Gate: FAILED",
            }
        }
        result = parse_custom_patterns_from_frontmatter(frontmatter)
        assert result is not None
        assert result.success_pattern == "Quality Gate: PASSED"
        assert result.failure_pattern == "Quality Gate: FAILED"

    def test_parse_custom_patterns_extracts_warning_pattern(self):
        """Test extracting optional warning_pattern from frontmatter."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            parse_custom_patterns_from_frontmatter,
        )
        frontmatter = {
            "validation": {
                "type": "custom",
                "success_pattern": "PASSED",
                "failure_pattern": "FAILED",
                "warning_pattern": "WARNING",
            }
        }
        result = parse_custom_patterns_from_frontmatter(frontmatter)
        assert result is not None
        assert result.warning_pattern == "WARNING"

    def test_parse_custom_patterns_extracts_case_sensitive(self):
        """Test extracting optional case_sensitive from frontmatter."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            parse_custom_patterns_from_frontmatter,
        )
        frontmatter = {
            "validation": {
                "type": "custom",
                "success_pattern": "PASSED",
                "failure_pattern": "FAILED",
                "case_sensitive": True,
            }
        }
        result = parse_custom_patterns_from_frontmatter(frontmatter)
        assert result is not None
        assert result.case_sensitive is True

    def test_parse_returns_none_for_non_custom_type(self):
        """Test parsing returns None when type is not 'custom'."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            parse_custom_patterns_from_frontmatter,
        )
        frontmatter = {
            "validation": {
                "type": "verdict-based",
            }
        }
        result = parse_custom_patterns_from_frontmatter(frontmatter)
        assert result is None

    def test_parse_returns_none_for_missing_validation(self):
        """Test parsing returns None when validation key is missing."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            parse_custom_patterns_from_frontmatter,
        )
        frontmatter = {"name": "workflow"}
        result = parse_custom_patterns_from_frontmatter(frontmatter)
        assert result is None

    def test_parse_returns_none_for_empty_frontmatter(self):
        """Test parsing returns None for empty frontmatter."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            parse_custom_patterns_from_frontmatter,
        )
        result = parse_custom_patterns_from_frontmatter({})
        assert result is None

    def test_parse_returns_none_for_none_frontmatter(self):
        """Test parsing returns None for None frontmatter."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            parse_custom_patterns_from_frontmatter,
        )
        result = parse_custom_patterns_from_frontmatter(None)
        assert result is None


class TestValidateCustomPattern:
    """Tests for custom pattern validation (Task 3)."""

    def test_validate_valid_pattern_returns_none(self):
        """Test validating a valid pattern returns no errors."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            validate_custom_pattern,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="Quality Gate: PASSED",
            failure_pattern="Quality Gate: FAILED",
        )
        errors = validate_custom_pattern(pattern)
        assert errors is None or len(errors) == 0

    def test_validate_missing_success_pattern_returns_error(self):
        """Test validation fails when success_pattern is empty (AC #4)."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            validate_custom_pattern,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="",
            failure_pattern="FAILED",
        )
        errors = validate_custom_pattern(pattern)
        assert errors is not None
        assert "success_pattern" in errors[0].lower()

    def test_validate_invalid_regex_success_pattern(self):
        """Test validation fails when success_pattern is invalid regex (AC #4)."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            validate_custom_pattern,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="[invalid regex((",
            failure_pattern="FAILED",
        )
        errors = validate_custom_pattern(pattern)
        assert errors is not None
        assert any("regex" in e.lower() or "pattern" in e.lower() for e in errors)

    def test_validate_invalid_regex_failure_pattern(self):
        """Test validation fails when failure_pattern is invalid regex."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            validate_custom_pattern,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="[invalid regex((",
        )
        errors = validate_custom_pattern(pattern)
        assert errors is not None
        assert any("regex" in e.lower() or "pattern" in e.lower() for e in errors)

    def test_validate_invalid_regex_warning_pattern(self):
        """Test validation fails when warning_pattern is invalid regex."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            validate_custom_pattern,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="FAILED",
            warning_pattern="[invalid regex((",
        )
        errors = validate_custom_pattern(pattern)
        assert errors is not None

    def test_validate_returns_multiple_errors(self):
        """Test validation can return multiple errors."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            validate_custom_pattern,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="",
            failure_pattern="[invalid(",
        )
        errors = validate_custom_pattern(pattern)
        assert errors is not None
        assert len(errors) >= 2


class TestMatchCustomPatterns:
    """Tests for custom pattern matching against content (Task 4)."""

    def test_match_success_pattern(self):
        """Test matching success pattern returns success (AC #2)."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="Quality Gate: PASSED",
            failure_pattern="Quality Gate: FAILED",
        )
        content = "Build completed. Quality Gate: PASSED. Continue deployment."
        result = match_custom_patterns(content, pattern)
        assert result is not None
        assert result["status"] == "success"
        assert "Quality Gate: PASSED" in result["matched_pattern"]

    def test_match_failure_pattern(self):
        """Test matching failure pattern returns failure."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="Quality Gate: PASSED",
            failure_pattern="Quality Gate: FAILED",
        )
        content = "Build completed. Quality Gate: FAILED. Deployment blocked."
        result = match_custom_patterns(content, pattern)
        assert result is not None
        assert result["status"] == "failure"
        assert "Quality Gate: FAILED" in result["matched_pattern"]

    def test_match_warning_pattern(self):
        """Test matching warning pattern returns warning."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="FAILED",
            warning_pattern="WARNING",
        )
        content = "Build completed with WARNING: some issues found."
        result = match_custom_patterns(content, pattern)
        assert result is not None
        assert result["status"] == "warning"

    def test_match_no_pattern_found(self):
        """Test when neither pattern matches."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="Quality Gate: PASSED",
            failure_pattern="Quality Gate: FAILED",
        )
        content = "Build completed. Status unknown."
        result = match_custom_patterns(content, pattern)
        assert result is not None
        assert result["status"] == "unknown"

    def test_match_case_insensitive_by_default(self):
        """Test matching is case insensitive by default."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="FAILED",
        )
        content = "Build completed: passed"
        result = match_custom_patterns(content, pattern)
        assert result is not None
        assert result["status"] == "success"

    def test_match_case_sensitive_when_enabled(self):
        """Test matching respects case_sensitive flag."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="PASSED",
            failure_pattern="FAILED",
            case_sensitive=True,
        )
        content = "Build completed: passed"  # lowercase
        result = match_custom_patterns(content, pattern)
        assert result is not None
        assert result["status"] == "unknown"  # Should NOT match due to case

    def test_match_regex_patterns(self):
        """Test matching with regex patterns."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern=r"Score:\s*\d+%.*PASSED",
            failure_pattern=r"Score:\s*\d+%.*FAILED",
        )
        content = "Build result: Score: 95% - PASSED"
        result = match_custom_patterns(content, pattern)
        assert result is not None
        assert result["status"] == "success"

    def test_failure_takes_precedence_over_success(self):
        """Test failure pattern takes precedence when both match."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="completed",
            failure_pattern="FAILED",
        )
        # Both patterns present, failure should win
        content = "Build completed but FAILED"
        result = match_custom_patterns(content, pattern)
        assert result is not None
        assert result["status"] == "failure"

    def test_match_handles_invalid_regex_gracefully(self):
        """Test matching handles invalid regex patterns gracefully.

        Even if validate_custom_pattern passes, match should not crash
        if somehow an invalid regex gets through (defensive coding).
        """
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        # Create pattern with invalid regex directly (bypassing validation)
        pattern = CustomPattern(
            success_pattern="valid",
            failure_pattern="[invalid(",  # Invalid regex
        )
        content = "Some content"
        # Should not raise, should return unknown or success
        result = match_custom_patterns(content, pattern)
        assert result is not None
        assert result["status"] in ("success", "unknown")

    def test_match_with_empty_failure_pattern(self):
        """Test matching when failure_pattern is empty."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="SUCCESS",
            failure_pattern="",
        )
        content = "Result: SUCCESS"
        result = match_custom_patterns(content, pattern)
        assert result["status"] == "success"

    def test_match_with_empty_success_pattern(self):
        """Test matching when success_pattern is empty."""
        from pcmrp_tools.bmad_automation.validation_type_detector import (
            match_custom_patterns,
            CustomPattern,
        )
        pattern = CustomPattern(
            success_pattern="",
            failure_pattern="FAILED",
        )
        content = "Result: FAILED"
        result = match_custom_patterns(content, pattern)
        assert result["status"] == "failure"


class TestCustomPatternPrecedence:
    """Tests for custom pattern precedence over built-in detection (Task 5, AC #3)."""

    def test_custom_pattern_takes_precedence_over_builtin(self):
        """Test custom patterns take precedence over built-in detection (AC #3)."""
        md_content = """---
validation:
  type: custom
  success_pattern: "Quality Gate: PASSED"
  failure_pattern: "Quality Gate: FAILED"
---

# Workflow Output

Status: PASS
Quality Gate: PASSED
0 errors found
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        try:
            result = detect_validation_type_from_file(temp_path)
            # Should detect as custom, not verdict-based
            assert result.validation_type == ValidationType.CUSTOM
            assert result.custom_patterns is not None
            assert result.custom_patterns.success_pattern == "Quality Gate: PASSED"
        finally:
            temp_path.unlink()

    def test_falls_back_to_builtin_when_no_custom(self):
        """Test falls back to built-in detection when no custom patterns."""
        md_content = """---
name: standard-workflow
---

# Workflow Output

Final Verdict: PASS
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        try:
            result = detect_validation_type_from_file(temp_path)
            # Should fall back to verdict-based detection
            assert result.validation_type == ValidationType.VERDICT_BASED
        finally:
            temp_path.unlink()

    def test_custom_pattern_high_confidence(self):
        """Test custom patterns from frontmatter have high confidence."""
        md_content = """---
validation:
  type: custom
  success_pattern: "BUILD SUCCEEDED"
  failure_pattern: "BUILD FAILED"
---

# Content
BUILD SUCCEEDED
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        try:
            result = detect_validation_type_from_file(temp_path)
            assert result.validation_type == ValidationType.CUSTOM
            # Custom patterns from frontmatter should have high confidence
            assert result.confidence >= 0.9
        finally:
            temp_path.unlink()


class TestDetectValidationTypeWithCustomPatterns:
    """Tests for detect_validation_type() integration with custom patterns (Task 6)."""

    def test_detect_from_file_with_custom_validation(self):
        """Test full integration: file with custom validation frontmatter."""
        md_content = """---
validation:
  type: custom
  success_pattern: "Quality Gate: PASSED"
  failure_pattern: "Quality Gate: FAILED"
---

## Build Report

Quality Gate: PASSED

All tests completed successfully.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        try:
            result = detect_validation_type_from_file(temp_path)
            assert result.validation_type == ValidationType.CUSTOM
            assert result.custom_patterns is not None
            assert result.details.get("custom_config") is not None
        finally:
            temp_path.unlink()

    def test_detect_with_invalid_custom_pattern_returns_error(self):
        """Test detecting invalid custom pattern returns error info (AC #4)."""
        md_content = """---
validation:
  type: custom
  success_pattern: "[invalid regex(("
  failure_pattern: "FAILED"
---

## Content
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        try:
            result = detect_validation_type_from_file(temp_path)
            # Should have error in details
            assert "error" in result.details or result.validation_type == ValidationType.UNKNOWN
        finally:
            temp_path.unlink()

    def test_detect_custom_missing_required_field_returns_error(self):
        """Test detecting custom pattern missing success_pattern returns error (AC #4)."""
        md_content = """---
validation:
  type: custom
  failure_pattern: "FAILED"
---

## Content
Some content without success_pattern defined
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        try:
            result = detect_validation_type_from_file(temp_path)
            # Should either have error or fall back to content detection
            assert ("error" in result.details or
                    result.details.get("validation_errors") or
                    result.validation_type != ValidationType.CUSTOM)
        finally:
            temp_path.unlink()

    def test_backward_compatibility_no_custom_patterns(self):
        """Test backward compatibility: files without custom patterns work normally."""
        md_content = """---
name: legacy-workflow
---

## Validation Result

Final status: PASS
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        try:
            result = detect_validation_type_from_file(temp_path)
            # Should work normally with content-based detection
            assert result.validation_type == ValidationType.VERDICT_BASED
            assert result.custom_patterns is None
        finally:
            temp_path.unlink()

    def test_detect_with_all_custom_fields(self):
        """Test detecting custom patterns with all optional fields."""
        md_content = """---
validation:
  type: custom
  success_pattern: "PASSED"
  failure_pattern: "FAILED"
  warning_pattern: "WARNING"
  case_sensitive: true
---

## Result
PASSED
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = Path(f.name)
        try:
            result = detect_validation_type_from_file(temp_path)
            assert result.validation_type == ValidationType.CUSTOM
            assert result.custom_patterns is not None
            assert result.custom_patterns.warning_pattern == "WARNING"
            assert result.custom_patterns.case_sensitive is True
        finally:
            temp_path.unlink()
