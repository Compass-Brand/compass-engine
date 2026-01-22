"""Tests for Checkpoint Presenter for Human Checkpoints.

This module tests the checkpoint presentation functionality that adapts
detail level based on confidence scores:
- High (>=80%): Minimal format (1-2 line summary)
- Medium (50-79%): Summary format (key decisions)
- Low (<50%): Full Audit Trail (complete log)

Story: 2b-7 - Human Checkpoint Presentation
Epic: 2b - Menu Selection & Navigation

TDD: Tests are written FIRST, before implementation.
"""

import pytest
from dataclasses import asdict

from pcmrp_tools.bmad_automation.checkpoint_presenter import (
    # Task 1: Format Types and Configuration
    CheckpointFormat,
    CONFIDENCE_THRESHOLDS,
    CheckpointConfig,
    get_format_for_confidence,
    # Task 2: CheckpointPresenter Class
    CheckpointPresenter,
    # Task 3: Minimal Format
    MinimalCheckpoint,
    generate_summary_line,
)


# =============================================================================
# Task 1.1: CheckpointFormat Enum Tests
# =============================================================================


class TestCheckpointFormatEnum:
    """Tests for CheckpointFormat enum (Task 1.1)."""

    def test_checkpoint_format_has_minimal(self) -> None:
        """CheckpointFormat should have MINIMAL value."""
        assert hasattr(CheckpointFormat, "MINIMAL")
        assert CheckpointFormat.MINIMAL.value == "minimal"

    def test_checkpoint_format_has_summary(self) -> None:
        """CheckpointFormat should have SUMMARY value."""
        assert hasattr(CheckpointFormat, "SUMMARY")
        assert CheckpointFormat.SUMMARY.value == "summary"

    def test_checkpoint_format_has_full_audit(self) -> None:
        """CheckpointFormat should have FULL_AUDIT value."""
        assert hasattr(CheckpointFormat, "FULL_AUDIT")
        assert CheckpointFormat.FULL_AUDIT.value == "full_audit"

    def test_checkpoint_format_has_exactly_three_values(self) -> None:
        """CheckpointFormat should have exactly 3 values."""
        assert len(CheckpointFormat) == 3


# =============================================================================
# Task 1.2: CONFIDENCE_THRESHOLDS Tests
# =============================================================================


class TestConfidenceThresholdsConstant:
    """Tests for CONFIDENCE_THRESHOLDS constant (Task 1.2)."""

    def test_confidence_thresholds_has_high_key(self) -> None:
        """CONFIDENCE_THRESHOLDS should have 'HIGH' key."""
        assert "HIGH" in CONFIDENCE_THRESHOLDS

    def test_confidence_thresholds_high_is_80(self) -> None:
        """CONFIDENCE_THRESHOLDS['HIGH'] should be 80."""
        assert CONFIDENCE_THRESHOLDS["HIGH"] == 80

    def test_confidence_thresholds_has_medium_key(self) -> None:
        """CONFIDENCE_THRESHOLDS should have 'MEDIUM' key."""
        assert "MEDIUM" in CONFIDENCE_THRESHOLDS

    def test_confidence_thresholds_medium_is_50(self) -> None:
        """CONFIDENCE_THRESHOLDS['MEDIUM'] should be 50."""
        assert CONFIDENCE_THRESHOLDS["MEDIUM"] == 50

    def test_confidence_thresholds_has_low_key(self) -> None:
        """CONFIDENCE_THRESHOLDS should have 'LOW' key (Issue #1 fix)."""
        assert "LOW" in CONFIDENCE_THRESHOLDS

    def test_confidence_thresholds_low_is_0(self) -> None:
        """CONFIDENCE_THRESHOLDS['LOW'] should be 0 (Issue #1 fix)."""
        assert CONFIDENCE_THRESHOLDS["LOW"] == 0

    def test_confidence_thresholds_is_frozen(self) -> None:
        """CONFIDENCE_THRESHOLDS should be immutable (frozen dict pattern)."""
        with pytest.raises((TypeError, AttributeError)):
            CONFIDENCE_THRESHOLDS["HIGH"] = 90  # type: ignore[index]


# =============================================================================
# Task 1.3: CheckpointConfig Dataclass Tests
# =============================================================================


class TestCheckpointConfigDataclass:
    """Tests for CheckpointConfig dataclass (Task 1.3)."""

    def test_checkpoint_config_creation_with_all_fields(self) -> None:
        """CheckpointConfig should be creatable with all fields."""
        config = CheckpointConfig(
            format=CheckpointFormat.MINIMAL,
            confidence=85.0,
            expandable=True,
        )
        assert config.format == CheckpointFormat.MINIMAL
        assert config.confidence == 85.0
        assert config.expandable is True

    def test_checkpoint_config_format_required(self) -> None:
        """CheckpointConfig format field should be CheckpointFormat."""
        config = CheckpointConfig(
            format=CheckpointFormat.SUMMARY,
            confidence=65.0,
            expandable=True,
        )
        assert isinstance(config.format, CheckpointFormat)

    def test_checkpoint_config_confidence_is_float(self) -> None:
        """CheckpointConfig confidence should be numeric."""
        config = CheckpointConfig(
            format=CheckpointFormat.FULL_AUDIT,
            confidence=45.5,
            expandable=True,
        )
        assert isinstance(config.confidence, (int, float))

    def test_checkpoint_config_expandable_is_bool(self) -> None:
        """CheckpointConfig expandable should be boolean."""
        config = CheckpointConfig(
            format=CheckpointFormat.MINIMAL,
            confidence=90.0,
            expandable=False,
        )
        assert isinstance(config.expandable, bool)

    def test_checkpoint_config_to_dict(self) -> None:
        """CheckpointConfig should be serializable to dict."""
        config = CheckpointConfig(
            format=CheckpointFormat.SUMMARY,
            confidence=75.0,
            expandable=True,
        )
        result = asdict(config)
        assert result["format"] == CheckpointFormat.SUMMARY
        assert result["confidence"] == 75.0
        assert result["expandable"] is True


# =============================================================================
# Task 1.4: get_format_for_confidence() Function Tests
# =============================================================================


class TestGetFormatForConfidence:
    """Tests for get_format_for_confidence() function (Task 1.4)."""

    def test_get_format_for_confidence_returns_checkpoint_format(self) -> None:
        """get_format_for_confidence() should return CheckpointFormat."""
        result = get_format_for_confidence(85.0)
        assert isinstance(result, CheckpointFormat)

    def test_high_confidence_returns_minimal(self) -> None:
        """Confidence >= 80 should return MINIMAL format (AC #1)."""
        assert get_format_for_confidence(80.0) == CheckpointFormat.MINIMAL
        assert get_format_for_confidence(85.0) == CheckpointFormat.MINIMAL
        assert get_format_for_confidence(100.0) == CheckpointFormat.MINIMAL

    def test_medium_confidence_returns_summary(self) -> None:
        """Confidence 50-79 should return SUMMARY format (AC #2)."""
        assert get_format_for_confidence(50.0) == CheckpointFormat.SUMMARY
        assert get_format_for_confidence(65.0) == CheckpointFormat.SUMMARY
        assert get_format_for_confidence(79.0) == CheckpointFormat.SUMMARY

    def test_low_confidence_returns_full_audit(self) -> None:
        """Confidence < 50 should return FULL_AUDIT format (AC #3)."""
        assert get_format_for_confidence(0.0) == CheckpointFormat.FULL_AUDIT
        assert get_format_for_confidence(25.0) == CheckpointFormat.FULL_AUDIT
        assert get_format_for_confidence(49.0) == CheckpointFormat.FULL_AUDIT


# =============================================================================
# Task 1.5: Boundary Tests for Confidence Levels
# =============================================================================


class TestConfidenceBoundaries:
    """Tests for confidence level boundaries (Task 1.5)."""

    def test_boundary_49_is_full_audit(self) -> None:
        """Confidence 49 should return FULL_AUDIT (just below medium)."""
        assert get_format_for_confidence(49.0) == CheckpointFormat.FULL_AUDIT
        assert get_format_for_confidence(49.9) == CheckpointFormat.FULL_AUDIT

    def test_boundary_50_is_summary(self) -> None:
        """Confidence 50 should return SUMMARY (at medium boundary)."""
        assert get_format_for_confidence(50.0) == CheckpointFormat.SUMMARY

    def test_boundary_79_is_summary(self) -> None:
        """Confidence 79 should return SUMMARY (just below high)."""
        assert get_format_for_confidence(79.0) == CheckpointFormat.SUMMARY
        assert get_format_for_confidence(79.9) == CheckpointFormat.SUMMARY

    def test_boundary_80_is_minimal(self) -> None:
        """Confidence 80 should return MINIMAL (at high boundary)."""
        assert get_format_for_confidence(80.0) == CheckpointFormat.MINIMAL

    def test_boundary_negative_confidence_clamped_to_zero(self) -> None:
        """Negative confidence should be clamped to 0 and return FULL_AUDIT (Issue #3 fix)."""
        assert get_format_for_confidence(-10.0) == CheckpointFormat.FULL_AUDIT
        # Verify it's clamped (behavior same as 0)
        assert get_format_for_confidence(-100.0) == CheckpointFormat.FULL_AUDIT

    def test_boundary_over_100_confidence_clamped_to_100(self) -> None:
        """Confidence over 100 should be clamped to 100 and return MINIMAL (Issue #3 fix)."""
        assert get_format_for_confidence(110.0) == CheckpointFormat.MINIMAL
        # Verify it's clamped (behavior same as 100)
        assert get_format_for_confidence(200.0) == CheckpointFormat.MINIMAL
        assert get_format_for_confidence(1000.0) == CheckpointFormat.MINIMAL


# =============================================================================
# Task 2.1: CheckpointPresenter Class Tests
# =============================================================================


class TestCheckpointPresenterClass:
    """Tests for CheckpointPresenter class (Task 2.1)."""

    def test_checkpoint_presenter_instantiation(self) -> None:
        """CheckpointPresenter should be instantiable."""
        presenter = CheckpointPresenter()
        assert presenter is not None

    def test_checkpoint_presenter_has_format_checkpoint_method(self) -> None:
        """CheckpointPresenter should have format_checkpoint method."""
        presenter = CheckpointPresenter()
        assert hasattr(presenter, "format_checkpoint")
        assert callable(presenter.format_checkpoint)

    def test_format_checkpoint_returns_string(self) -> None:
        """format_checkpoint() should return string output."""
        presenter = CheckpointPresenter()
        checkpoint_data = {
            "step_id": "step-1",
            "confidence": 85.0,
            "operations": [{"type": "validate", "target": "prd"}],
        }
        result = presenter.format_checkpoint(checkpoint_data)
        assert isinstance(result, str)

    def test_format_checkpoint_selects_format_based_on_confidence(self) -> None:
        """format_checkpoint() should select format based on confidence."""
        presenter = CheckpointPresenter()

        # High confidence -> minimal
        high_conf: dict[str, object] = {"confidence": 85.0, "operations": []}
        result_high = presenter.format_checkpoint(high_conf)
        assert "[Confirm]" in result_high or "confirm" in result_high.lower()

        # Medium confidence -> summary
        medium_conf: dict[str, object] = {"confidence": 65.0, "operations": []}
        result_medium = presenter.format_checkpoint(medium_conf)
        assert len(result_medium) > len(result_high)  # Summary should be longer


# =============================================================================
# Task 2.2: format_minimal() Method Tests
# =============================================================================


class TestFormatMinimal:
    """Tests for format_minimal() method (Task 2.2)."""

    def test_format_minimal_returns_string(self) -> None:
        """format_minimal() should return string."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {"operations": [], "confidence": 90.0}
        result = presenter.format_minimal(checkpoint)
        assert isinstance(result, str)

    def test_format_minimal_is_concise(self) -> None:
        """format_minimal() should return 1-2 lines (AC #1)."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "operations": [{"type": "validate"}, {"type": "transform"}],
            "confidence": 90.0,
        }
        result = presenter.format_minimal(checkpoint)
        line_count = len(result.strip().split("\n"))
        assert line_count <= 2, f"Expected 1-2 lines, got {line_count}"

    def test_format_minimal_includes_confirm_action(self) -> None:
        """format_minimal() should include confirm button/action."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "operations": [{"type": "validate"}],
            "confidence": 90.0,
        }
        result = presenter.format_minimal(checkpoint)
        assert "[Confirm]" in result or "[confirm]" in result.lower()

    def test_format_minimal_includes_expand_details_link(self) -> None:
        """format_minimal() should include expand_details link (Task 2.5)."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {"operations": [], "confidence": 90.0}
        result = presenter.format_minimal(checkpoint)
        assert "[Expand]" in result or "expand" in result.lower()


# =============================================================================
# Task 2.3: format_summary() Method Tests
# =============================================================================


class TestFormatSummary:
    """Tests for format_summary() method (Task 2.3)."""

    def test_format_summary_returns_string(self) -> None:
        """format_summary() should return string."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "operations": [],
            "confidence": 65.0,
            "decisions": [],
        }
        result = presenter.format_summary(checkpoint)
        assert isinstance(result, str)

    def test_format_summary_includes_key_decisions(self) -> None:
        """format_summary() should include key decisions (AC #2)."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "operations": [{"type": "validate"}],
            "confidence": 65.0,
            "decisions": ["Used pattern A", "Skipped optional B"],
        }
        result = presenter.format_summary(checkpoint)
        # Should include decisions section
        assert "decision" in result.lower() or "pattern" in result.lower()

    def test_format_summary_includes_expandable_section(self) -> None:
        """format_summary() should be expandable (Task 2.5)."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {"operations": [], "confidence": 65.0}
        result = presenter.format_summary(checkpoint)
        assert "[Expand]" in result or "expand" in result.lower()

    def test_format_summary_more_detailed_than_minimal(self) -> None:
        """format_summary() should be more detailed than minimal."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "operations": [{"type": "validate"}],
            "confidence": 65.0,
        }
        summary = presenter.format_summary(checkpoint)
        checkpoint["confidence"] = 90.0
        minimal = presenter.format_minimal(checkpoint)
        assert len(summary) >= len(minimal)


# =============================================================================
# Task 2.4: format_full_audit() Method Tests
# =============================================================================


class TestFormatFullAudit:
    """Tests for format_full_audit() method (Task 2.4)."""

    def test_format_full_audit_returns_string(self) -> None:
        """format_full_audit() should return string."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {"operations": [], "confidence": 25.0}
        result = presenter.format_full_audit(checkpoint)
        assert isinstance(result, str)

    def test_format_full_audit_includes_complete_log(self) -> None:
        """format_full_audit() should include complete log (AC #3)."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "operations": [
                {"type": "validate", "target": "prd", "result": "passed"},
                {"type": "analyze", "target": "requirements", "result": "ok"},
            ],
            "confidence": 25.0,
            "log": ["Step 1: Validated", "Step 2: Analyzed"],
        }
        result = presenter.format_full_audit(checkpoint)
        # Should include detailed log
        assert "log" in result.lower() or "audit" in result.lower()

    def test_format_full_audit_requires_explicit_approval(self) -> None:
        """format_full_audit() should require explicit approval."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {"operations": [], "confidence": 25.0}
        result = presenter.format_full_audit(checkpoint)
        # Should have explicit approval action
        assert (
            "[Approve]" in result
            or "[Confirm]" in result
            or "approve" in result.lower()
        )

    def test_format_full_audit_excludes_expand_details_link(self) -> None:
        """format_full_audit() should NOT include expand_details link (Issue #2 fix).

        Full audit is already at maximum detail level. can_expand(FULL_AUDIT)
        returns False, so the format should not include [Expand] action.
        """
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {"operations": [], "confidence": 25.0}
        result = presenter.format_full_audit(checkpoint)
        # Full audit should NOT have expand - it's already at max detail
        assert "[Expand]" not in result

    def test_format_full_audit_most_detailed(self) -> None:
        """format_full_audit() should be more detailed than summary."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "operations": [{"type": "validate"}],
            "confidence": 25.0,
        }
        full = presenter.format_full_audit(checkpoint)
        checkpoint["confidence"] = 65.0
        summary = presenter.format_summary(checkpoint)
        # Full audit should be at least as long as summary
        assert len(full) >= len(summary)


# =============================================================================
# Task 3.1: MinimalCheckpoint Dataclass Tests
# =============================================================================


class TestMinimalCheckpointDataclass:
    """Tests for MinimalCheckpoint dataclass (Task 3.1)."""

    def test_minimal_checkpoint_creation(self) -> None:
        """MinimalCheckpoint should be creatable with required fields."""
        checkpoint = MinimalCheckpoint(
            summary_line="Validated 3 items",
            confirm_action="[Confirm]",
        )
        assert checkpoint.summary_line == "Validated 3 items"
        assert checkpoint.confirm_action == "[Confirm]"

    def test_minimal_checkpoint_summary_line_is_string(self) -> None:
        """MinimalCheckpoint summary_line should be string."""
        checkpoint = MinimalCheckpoint(
            summary_line="Test summary",
            confirm_action="[Confirm]",
        )
        assert isinstance(checkpoint.summary_line, str)

    def test_minimal_checkpoint_confirm_action_is_string(self) -> None:
        """MinimalCheckpoint confirm_action should be string."""
        checkpoint = MinimalCheckpoint(
            summary_line="Test",
            confirm_action="[Confirm]",
        )
        assert isinstance(checkpoint.confirm_action, str)

    def test_minimal_checkpoint_to_dict(self) -> None:
        """MinimalCheckpoint should be serializable to dict."""
        checkpoint = MinimalCheckpoint(
            summary_line="Test summary",
            confirm_action="[Confirm]",
        )
        result = asdict(checkpoint)
        assert result["summary_line"] == "Test summary"
        assert result["confirm_action"] == "[Confirm]"


# =============================================================================
# Task 3.2-3.4: generate_summary_line() Function Tests
# =============================================================================


class TestGenerateSummaryLine:
    """Tests for generate_summary_line() function (Tasks 3.2-3.4)."""

    def test_generate_summary_line_returns_string(self) -> None:
        """generate_summary_line() should return string."""
        operations = [{"type": "validate", "target": "prd"}]
        result = generate_summary_line(operations)
        assert isinstance(result, str)

    def test_generate_summary_line_condenses_to_1_2_lines(self) -> None:
        """generate_summary_line() should condense to 1-2 lines (Task 3.2)."""
        operations = [
            {"type": "validate", "target": "prd"},
            {"type": "transform", "target": "architecture"},
            {"type": "analyze", "target": "epics"},
        ]
        result = generate_summary_line(operations)
        line_count = len(result.strip().split("\n"))
        assert line_count <= 2, f"Expected 1-2 lines, got {line_count}"

    def test_generate_summary_line_includes_operation_count(self) -> None:
        """generate_summary_line() should include operation count (Task 3.3)."""
        operations = [
            {"type": "validate"},
            {"type": "transform"},
            {"type": "analyze"},
        ]
        result = generate_summary_line(operations)
        # Should include count (3)
        assert "3" in result

    def test_generate_summary_line_includes_key_action_types(self) -> None:
        """generate_summary_line() should include key action types (Task 3.3)."""
        operations = [
            {"type": "validate", "target": "prd"},
            {"type": "transform", "target": "arch"},
        ]
        result = generate_summary_line(operations)
        # Should mention the action types
        assert "validate" in result.lower() or "transform" in result.lower()

    def test_generate_summary_line_handles_empty_operations(self) -> None:
        """generate_summary_line() should handle empty operations list."""
        result = generate_summary_line([])
        assert isinstance(result, str)
        assert len(result) > 0  # Should still return something

    def test_generate_summary_line_handles_single_operation(self) -> None:
        """generate_summary_line() should handle single operation."""
        operations = [{"type": "validate", "target": "prd"}]
        result = generate_summary_line(operations)
        assert "1" in result or "validate" in result.lower()

    def test_generate_summary_line_aggregates_action_types(self) -> None:
        """generate_summary_line() should aggregate same action types."""
        operations = [
            {"type": "validate", "target": "prd"},
            {"type": "validate", "target": "arch"},
            {"type": "validate", "target": "epics"},
        ]
        result = generate_summary_line(operations)
        # Should mention validate and count
        assert "validate" in result.lower()
        assert "3" in result


# =============================================================================
# Integration Tests: Format Selection by Confidence
# =============================================================================


class TestFormatSelectionByConfidence:
    """Integration tests for format selection based on confidence."""

    def test_high_confidence_uses_minimal_format(self) -> None:
        """High confidence (>=80) should use minimal format (AC #1)."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "confidence": 85.0,
            "operations": [{"type": "validate"}],
        }
        result = presenter.format_checkpoint(checkpoint)
        # Minimal format should be concise
        assert len(result.strip().split("\n")) <= 3

    def test_medium_confidence_uses_summary_format(self) -> None:
        """Medium confidence (50-79) should use summary format (AC #2)."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "confidence": 65.0,
            "operations": [{"type": "validate"}],
            "decisions": ["Decision 1"],
        }
        result = presenter.format_checkpoint(checkpoint)
        # Summary format should include decisions
        assert len(result) > 50  # More than minimal

    def test_low_confidence_uses_full_audit_format(self) -> None:
        """Low confidence (<50) should use full audit format (AC #3)."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "confidence": 25.0,
            "operations": [{"type": "validate"}],
            "log": ["Step 1"],
        }
        result = presenter.format_checkpoint(checkpoint)
        # Full audit should be comprehensive
        assert len(result) > 50


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================


class TestCheckpointPresenterEdgeCases:
    """Edge case tests for checkpoint presenter."""

    def test_format_checkpoint_missing_confidence_defaults_to_low(self) -> None:
        """Missing confidence should default to low (full audit)."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {"operations": []}
        result = presenter.format_checkpoint(checkpoint)
        # Should still work and default to safe (full audit)
        assert isinstance(result, str)

    def test_format_checkpoint_missing_operations(self) -> None:
        """Missing operations should be handled gracefully."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {"confidence": 85.0}
        result = presenter.format_checkpoint(checkpoint)
        assert isinstance(result, str)

    def test_format_checkpoint_empty_dict(self) -> None:
        """Empty checkpoint dict should be handled."""
        presenter = CheckpointPresenter()
        result = presenter.format_checkpoint({})
        assert isinstance(result, str)

    def test_expandable_formats_include_expand_option(self) -> None:
        """Expandable format levels (MINIMAL, SUMMARY) should include expand option.

        FULL_AUDIT is already at max detail, so it does NOT have [Expand].
        (Issue #2 fix - can_expand(FULL_AUDIT) returns False)
        """
        presenter = CheckpointPresenter()

        # MINIMAL and SUMMARY should have [Expand]
        for confidence in [90.0, 65.0]:
            checkpoint: dict[str, object] = {"confidence": confidence, "operations": []}
            result = presenter.format_checkpoint(checkpoint)
            assert (
                "[Expand]" in result or "expand" in result.lower()
            ), f"Expand option missing for confidence {confidence}"

        # FULL_AUDIT should NOT have [Expand] - already at max detail
        checkpoint_full: dict[str, object] = {"confidence": 25.0, "operations": []}
        result_full = presenter.format_checkpoint(checkpoint_full)
        assert "[Expand]" not in result_full, "FULL_AUDIT should not have [Expand]"


# =============================================================================
# Acceptance Criteria Tests
# =============================================================================


class TestAC1HighConfidenceMinimalFormat:
    """Tests for AC #1: High confidence uses minimal format."""

    def test_confidence_80_uses_minimal(self) -> None:
        """Confidence 80 should use minimal format."""
        assert get_format_for_confidence(80.0) == CheckpointFormat.MINIMAL

    def test_confidence_95_uses_minimal(self) -> None:
        """Confidence 95 should use minimal format."""
        assert get_format_for_confidence(95.0) == CheckpointFormat.MINIMAL

    def test_minimal_format_has_single_confirm(self) -> None:
        """Minimal format should have single [Confirm] button."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {"confidence": 90.0, "operations": []}
        result = presenter.format_minimal(checkpoint)
        assert result.count("[Confirm]") == 1 or "confirm" in result.lower()


class TestAC2MediumConfidenceSummaryFormat:
    """Tests for AC #2: Medium confidence uses summary format."""

    def test_confidence_50_uses_summary(self) -> None:
        """Confidence 50 should use summary format."""
        assert get_format_for_confidence(50.0) == CheckpointFormat.SUMMARY

    def test_confidence_70_uses_summary(self) -> None:
        """Confidence 70 should use summary format."""
        assert get_format_for_confidence(70.0) == CheckpointFormat.SUMMARY

    def test_summary_format_shows_key_decisions(self) -> None:
        """Summary format should show key decisions."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "confidence": 65.0,
            "operations": [],
            "decisions": ["Used caching strategy"],
        }
        result = presenter.format_summary(checkpoint)
        assert "decision" in result.lower() or "caching" in result.lower()


class TestAC3LowConfidenceFullAuditFormat:
    """Tests for AC #3: Low confidence uses full audit trail."""

    def test_confidence_49_uses_full_audit(self) -> None:
        """Confidence 49 should use full audit format."""
        assert get_format_for_confidence(49.0) == CheckpointFormat.FULL_AUDIT

    def test_confidence_10_uses_full_audit(self) -> None:
        """Confidence 10 should use full audit format."""
        assert get_format_for_confidence(10.0) == CheckpointFormat.FULL_AUDIT

    def test_full_audit_format_shows_complete_log(self) -> None:
        """Full audit format should show complete log."""
        presenter = CheckpointPresenter()
        checkpoint: dict[str, object] = {
            "confidence": 25.0,
            "operations": [],
            "log": ["Entry 1", "Entry 2", "Entry 3"],
        }
        result = presenter.format_full_audit(checkpoint)
        # Should include log entries or audit trail
        assert (
            "log" in result.lower()
            or "audit" in result.lower()
            or "entry" in result.lower()
        )


# =============================================================================
# Task 4-6: Summary Format, Full Audit Trail, and Expandable Details Tests
# (Story 2b-7 - Human Checkpoint Presentation)
# =============================================================================

from datetime import datetime

from pcmrp_tools.bmad_automation.checkpoint_presenter import (
    # Task 4: Summary Format
    SummaryCheckpoint,
    extract_key_decisions,
    format_summary_checkpoint,
    # Task 5: Full Audit Trail Format
    AuditTrailCheckpoint,
    OperationLogEntry,
    generate_operation_log,
    format_audit_trail_checkpoint,
    # Task 6: Expandable Details
    ExpandableDetails,
    ExpansionState,
    expand_checkpoint,
    can_expand,
    get_expansion_state,
)


class TestSummaryCheckpointDataclass:
    """Tests for SummaryCheckpoint dataclass (Task 4.1)."""

    def test_summary_checkpoint_creation(self) -> None:
        """SummaryCheckpoint should be creatable with decisions and details_available."""
        checkpoint = SummaryCheckpoint(
            decisions=["Created module A", "Updated config B"],
            details_available=True,
        )
        assert checkpoint.decisions == ["Created module A", "Updated config B"]
        assert checkpoint.details_available is True

    def test_summary_checkpoint_empty_decisions(self) -> None:
        """SummaryCheckpoint should accept empty decisions list."""
        checkpoint = SummaryCheckpoint(decisions=[], details_available=False)
        assert checkpoint.decisions == []
        assert checkpoint.details_available is False

    def test_summary_checkpoint_to_dict(self) -> None:
        """SummaryCheckpoint should be serializable to dict."""
        checkpoint = SummaryCheckpoint(
            decisions=["Decision 1"],
            details_available=True,
        )
        result = asdict(checkpoint)
        assert result["decisions"] == ["Decision 1"]
        assert result["details_available"] is True

    def test_summary_checkpoint_many_decisions(self) -> None:
        """SummaryCheckpoint should handle many decisions."""
        decisions = [f"Decision {i}" for i in range(10)]
        checkpoint = SummaryCheckpoint(decisions=decisions, details_available=True)
        assert len(checkpoint.decisions) == 10


class TestExtractKeyDecisions:
    """Tests for extract_key_decisions function (Task 4.2)."""

    def test_extract_key_decisions_returns_list(self) -> None:
        """extract_key_decisions should return List[str]."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
        ]
        result = extract_key_decisions(operations)
        assert isinstance(result, list)
        assert all(isinstance(d, str) for d in result)

    def test_extract_key_decisions_single_operation(self) -> None:
        """extract_key_decisions should extract decision from single operation."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
        ]
        result = extract_key_decisions(operations)
        assert len(result) == 1
        assert "create" in result[0].lower() or "module.py" in result[0]

    def test_extract_key_decisions_multiple_operations(self) -> None:
        """extract_key_decisions should extract decisions from multiple operations."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
            {"type": "update", "target": "config.yaml", "outcome": "success"},
            {"type": "delete", "target": "old_file.py", "outcome": "success"},
        ]
        result = extract_key_decisions(operations)
        assert len(result) == 3

    def test_extract_key_decisions_empty_operations(self) -> None:
        """extract_key_decisions should return empty list for empty operations."""
        result = extract_key_decisions([])
        assert result == []

    def test_extract_key_decisions_with_description(self) -> None:
        """extract_key_decisions should use description field if present."""
        operations: list[dict[str, object]] = [
            {
                "type": "create",
                "target": "module.py",
                "description": "Created new validation module",
                "outcome": "success",
            },
        ]
        result = extract_key_decisions(operations)
        assert len(result) == 1
        assert "validation" in result[0].lower() or "Created" in result[0]

    def test_extract_key_decisions_includes_failed(self) -> None:
        """extract_key_decisions should include failed operations distinctly."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
            {"type": "update", "target": "config.yaml", "outcome": "failed"},
        ]
        result = extract_key_decisions(operations)
        assert len(result) == 2


class TestFormatSummaryCheckpointFunc:
    """Tests for format_summary_checkpoint function (Task 4.3, 4.4)."""

    def test_format_summary_checkpoint_returns_string(self) -> None:
        """format_summary_checkpoint should return formatted string."""
        checkpoint = SummaryCheckpoint(
            decisions=["Decision 1", "Decision 2"],
            details_available=True,
        )
        result = format_summary_checkpoint(checkpoint)
        assert isinstance(result, str)

    def test_format_summary_checkpoint_numbered_list(self) -> None:
        """format_summary_checkpoint should format as numbered list (Task 4.3)."""
        checkpoint = SummaryCheckpoint(
            decisions=["Created module A", "Updated config B", "Deleted old file"],
            details_available=True,
        )
        result = format_summary_checkpoint(checkpoint)
        assert "1." in result or "1)" in result
        assert "2." in result or "2)" in result
        assert "3." in result or "3)" in result

    def test_format_summary_checkpoint_includes_expand_action(self) -> None:
        """format_summary_checkpoint should include [Expand Details] action (Task 4.4)."""
        checkpoint = SummaryCheckpoint(
            decisions=["Decision 1"],
            details_available=True,
        )
        result = format_summary_checkpoint(checkpoint)
        assert "[Expand Details]" in result or "Expand" in result

    def test_format_summary_checkpoint_no_expand_when_unavailable(self) -> None:
        """format_summary_checkpoint should not show expand when details unavailable."""
        checkpoint = SummaryCheckpoint(
            decisions=["Decision 1"],
            details_available=False,
        )
        result = format_summary_checkpoint(checkpoint)
        assert "[Expand Details]" not in result

    def test_format_summary_checkpoint_empty_decisions(self) -> None:
        """format_summary_checkpoint should handle empty decisions."""
        checkpoint = SummaryCheckpoint(decisions=[], details_available=False)
        result = format_summary_checkpoint(checkpoint)
        assert isinstance(result, str)
        assert "No decisions" in result or len(result) > 0


class TestOperationLogEntryDataclass:
    """Tests for OperationLogEntry dataclass."""

    def test_operation_log_entry_creation(self) -> None:
        """OperationLogEntry should be creatable with all fields."""
        entry = OperationLogEntry(
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            operation_type="create",
            target="module.py",
            details="Created new validation module",
            outcome="success",
        )
        assert entry.operation_type == "create"
        assert entry.target == "module.py"
        assert entry.outcome == "success"

    def test_operation_log_entry_to_dict(self) -> None:
        """OperationLogEntry should be serializable to dict."""
        entry = OperationLogEntry(
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            operation_type="update",
            target="config.yaml",
            details="Updated settings",
            outcome="success",
        )
        result = asdict(entry)
        assert result["operation_type"] == "update"
        assert result["target"] == "config.yaml"


class TestAuditTrailCheckpointDataclass:
    """Tests for AuditTrailCheckpoint dataclass (Task 5.1)."""

    def test_audit_trail_checkpoint_creation(self) -> None:
        """AuditTrailCheckpoint should be creatable."""
        log_entries = [
            OperationLogEntry(
                timestamp=datetime.now(),
                operation_type="create",
                target="module.py",
                details="Created module",
                outcome="success",
            )
        ]
        checkpoint = AuditTrailCheckpoint(
            operation_log=log_entries,
            approval_required=True,
        )
        assert len(checkpoint.operation_log) == 1
        assert checkpoint.approval_required is True

    def test_audit_trail_checkpoint_empty_log(self) -> None:
        """AuditTrailCheckpoint should accept empty operation log."""
        checkpoint = AuditTrailCheckpoint(
            operation_log=[],
            approval_required=False,
        )
        assert checkpoint.operation_log == []
        assert checkpoint.approval_required is False

    def test_audit_trail_checkpoint_to_dict(self) -> None:
        """AuditTrailCheckpoint should be serializable to dict."""
        checkpoint = AuditTrailCheckpoint(
            operation_log=[],
            approval_required=True,
        )
        result = asdict(checkpoint)
        assert result["approval_required"] is True


class TestGenerateOperationLog:
    """Tests for generate_operation_log function (Task 5.2)."""

    def test_generate_operation_log_returns_string(self) -> None:
        """generate_operation_log should return formatted string."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
        ]
        result = generate_operation_log(operations)
        assert isinstance(result, str)

    def test_generate_operation_log_includes_timestamp(self) -> None:
        """generate_operation_log should include timestamps (Task 5.3)."""
        operations: list[dict[str, object]] = [
            {
                "type": "create",
                "target": "module.py",
                "outcome": "success",
                "timestamp": "2024-01-15T10:30:00",
            },
        ]
        result = generate_operation_log(operations)
        assert "10:30" in result or "2024" in result or ":" in result

    def test_generate_operation_log_includes_details(self) -> None:
        """generate_operation_log should include operation details (Task 5.3)."""
        operations: list[dict[str, object]] = [
            {
                "type": "create",
                "target": "module.py",
                "description": "Created new validation module",
                "outcome": "success",
            },
        ]
        result = generate_operation_log(operations)
        assert "create" in result.lower() or "module.py" in result

    def test_generate_operation_log_includes_outcomes(self) -> None:
        """generate_operation_log should include outcomes (Task 5.3)."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
            {"type": "update", "target": "config.yaml", "outcome": "failed"},
        ]
        result = generate_operation_log(operations)
        assert "success" in result.lower() or "failed" in result.lower()

    def test_generate_operation_log_empty_operations(self) -> None:
        """generate_operation_log should handle empty operations."""
        result = generate_operation_log([])
        assert isinstance(result, str)

    def test_generate_operation_log_multiple_operations(self) -> None:
        """generate_operation_log should format multiple operations."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
            {"type": "update", "target": "config.yaml", "outcome": "success"},
            {"type": "delete", "target": "old_file.py", "outcome": "success"},
        ]
        result = generate_operation_log(operations)
        assert "module.py" in result or "create" in result.lower()
        assert "config.yaml" in result or "update" in result.lower()


class TestFormatAuditTrailCheckpoint:
    """Tests for format_audit_trail_checkpoint function (Task 5.4)."""

    def test_format_audit_trail_checkpoint_returns_string(self) -> None:
        """format_audit_trail_checkpoint should return formatted string."""
        checkpoint = AuditTrailCheckpoint(
            operation_log=[],
            approval_required=True,
        )
        result = format_audit_trail_checkpoint(checkpoint)
        assert isinstance(result, str)

    def test_format_audit_trail_checkpoint_requires_explicit_approval(self) -> None:
        """format_audit_trail_checkpoint should require explicit approval (Task 5.4)."""
        checkpoint = AuditTrailCheckpoint(
            operation_log=[],
            approval_required=True,
        )
        result = format_audit_trail_checkpoint(checkpoint)
        assert "APPROVE" in result.upper() or "Approval Required" in result

    def test_format_audit_trail_checkpoint_approval_not_confirm(self) -> None:
        """format_audit_trail_checkpoint approval should not be just 'confirm' (Task 5.4)."""
        checkpoint = AuditTrailCheckpoint(
            operation_log=[],
            approval_required=True,
        )
        result = format_audit_trail_checkpoint(checkpoint)
        assert "APPROVE" in result.upper() or "approve" in result.lower()

    def test_format_audit_trail_checkpoint_no_approval_when_not_required(self) -> None:
        """format_audit_trail_checkpoint should not require approval when not set."""
        checkpoint = AuditTrailCheckpoint(
            operation_log=[],
            approval_required=False,
        )
        result = format_audit_trail_checkpoint(checkpoint)
        assert "APPROVE" not in result.upper() or "optional" in result.lower()

    def test_format_audit_trail_checkpoint_includes_log(self) -> None:
        """format_audit_trail_checkpoint should include operation log content."""
        log_entries = [
            OperationLogEntry(
                timestamp=datetime(2024, 1, 15, 10, 30, 0),
                operation_type="create",
                target="module.py",
                details="Created module",
                outcome="success",
            )
        ]
        checkpoint = AuditTrailCheckpoint(
            operation_log=log_entries,
            approval_required=True,
        )
        result = format_audit_trail_checkpoint(checkpoint)
        assert "module.py" in result or "create" in result.lower()


class TestExpansionStateEnum:
    """Tests for ExpansionState enum."""

    def test_expansion_state_has_collapsed(self) -> None:
        """ExpansionState should have COLLAPSED value."""
        assert hasattr(ExpansionState, "COLLAPSED")

    def test_expansion_state_has_expanded(self) -> None:
        """ExpansionState should have EXPANDED value."""
        assert hasattr(ExpansionState, "EXPANDED")


class TestExpandableDetailsDataclass:
    """Tests for ExpandableDetails dataclass (Task 6.1)."""

    def test_expandable_details_creation(self) -> None:
        """ExpandableDetails should be creatable with collapsed_view and expanded_view."""
        details = ExpandableDetails(
            collapsed_view="Summary: 3 operations completed",
            expanded_view="Full audit trail with timestamps...",
            state=ExpansionState.COLLAPSED,
        )
        assert details.collapsed_view == "Summary: 3 operations completed"
        assert details.expanded_view == "Full audit trail with timestamps..."
        assert details.state == ExpansionState.COLLAPSED

    def test_expandable_details_to_dict(self) -> None:
        """ExpandableDetails should be serializable to dict."""
        details = ExpandableDetails(
            collapsed_view="Summary",
            expanded_view="Full details",
            state=ExpansionState.COLLAPSED,
        )
        result = asdict(details)
        assert result["collapsed_view"] == "Summary"
        assert result["expanded_view"] == "Full details"

    def test_expandable_details_default_state_collapsed(self) -> None:
        """ExpandableDetails should default to COLLAPSED state."""
        details = ExpandableDetails(
            collapsed_view="Summary",
            expanded_view="Full details",
        )
        assert details.state == ExpansionState.COLLAPSED


class TestExpandCheckpoint:
    """Tests for expand_checkpoint function (Task 6.2)."""

    def test_expand_checkpoint_returns_string(self) -> None:
        """expand_checkpoint should return full details string."""
        details = ExpandableDetails(
            collapsed_view="Summary: 3 operations",
            expanded_view="Full audit: Operation 1, Operation 2, Operation 3",
            state=ExpansionState.COLLAPSED,
        )
        result = expand_checkpoint(details)
        assert isinstance(result, str)

    def test_expand_checkpoint_reveals_full_details(self) -> None:
        """expand_checkpoint should reveal full details (Task 6.2)."""
        details = ExpandableDetails(
            collapsed_view="Summary: 3 operations",
            expanded_view="Full audit: Operation 1, Operation 2, Operation 3",
            state=ExpansionState.COLLAPSED,
        )
        result = expand_checkpoint(details)
        assert "Full audit" in result or "Operation 1" in result

    def test_expand_checkpoint_updates_state(self) -> None:
        """expand_checkpoint should update state to EXPANDED (Task 6.3)."""
        details = ExpandableDetails(
            collapsed_view="Summary",
            expanded_view="Full details",
            state=ExpansionState.COLLAPSED,
        )
        expand_checkpoint(details)
        assert details.state == ExpansionState.EXPANDED

    def test_expand_checkpoint_already_expanded(self) -> None:
        """expand_checkpoint should handle already expanded state."""
        details = ExpandableDetails(
            collapsed_view="Summary",
            expanded_view="Full details",
            state=ExpansionState.EXPANDED,
        )
        result = expand_checkpoint(details)
        assert isinstance(result, str)
        assert details.state == ExpansionState.EXPANDED


class TestCollapseCheckpoint:
    """Tests for collapse_checkpoint function (Issue #4 fix)."""

    def test_collapse_checkpoint_returns_string(self) -> None:
        """collapse_checkpoint should return collapsed view string."""
        from pcmrp_tools.bmad_automation.checkpoint_presenter import collapse_checkpoint

        details = ExpandableDetails(
            collapsed_view="Summary: 3 operations",
            expanded_view="Full audit: Operation 1, Operation 2, Operation 3",
            state=ExpansionState.EXPANDED,
        )
        result = collapse_checkpoint(details)
        assert isinstance(result, str)

    def test_collapse_checkpoint_returns_collapsed_view(self) -> None:
        """collapse_checkpoint should return collapsed_view content."""
        from pcmrp_tools.bmad_automation.checkpoint_presenter import collapse_checkpoint

        details = ExpandableDetails(
            collapsed_view="Summary: 3 operations completed",
            expanded_view="Full audit trail...",
            state=ExpansionState.EXPANDED,
        )
        result = collapse_checkpoint(details)
        assert result == "Summary: 3 operations completed"

    def test_collapse_checkpoint_updates_state(self) -> None:
        """collapse_checkpoint should update state to COLLAPSED."""
        from pcmrp_tools.bmad_automation.checkpoint_presenter import collapse_checkpoint

        details = ExpandableDetails(
            collapsed_view="Summary",
            expanded_view="Full details",
            state=ExpansionState.EXPANDED,
        )
        collapse_checkpoint(details)
        assert details.state == ExpansionState.COLLAPSED

    def test_collapse_checkpoint_already_collapsed(self) -> None:
        """collapse_checkpoint should handle already collapsed state."""
        from pcmrp_tools.bmad_automation.checkpoint_presenter import collapse_checkpoint

        details = ExpandableDetails(
            collapsed_view="Summary",
            expanded_view="Full details",
            state=ExpansionState.COLLAPSED,
        )
        result = collapse_checkpoint(details)
        assert isinstance(result, str)
        assert details.state == ExpansionState.COLLAPSED
        assert result == "Summary"

    def test_expand_then_collapse_roundtrip(self) -> None:
        """Expand followed by collapse should return to original state."""
        from pcmrp_tools.bmad_automation.checkpoint_presenter import collapse_checkpoint

        details = ExpandableDetails(
            collapsed_view="Summary view",
            expanded_view="Expanded view",
            state=ExpansionState.COLLAPSED,
        )
        # Expand
        expanded_result = expand_checkpoint(details)
        assert details.state == ExpansionState.EXPANDED
        assert expanded_result == "Expanded view"

        # Collapse
        collapsed_result = collapse_checkpoint(details)
        assert details.state == ExpansionState.COLLAPSED
        assert collapsed_result == "Summary view"


class TestCanExpand:
    """Tests for can_expand function (Task 6.4)."""

    def test_can_expand_minimal_format(self) -> None:
        """Minimal format should be expandable to Full Audit (Task 6.4)."""
        result = can_expand(CheckpointFormat.MINIMAL)
        assert result is True

    def test_can_expand_summary_format(self) -> None:
        """Summary format should be expandable to Full Audit (Task 6.4)."""
        result = can_expand(CheckpointFormat.SUMMARY)
        assert result is True

    def test_can_expand_full_audit_format(self) -> None:
        """Full Audit format should not be expandable (already full)."""
        result = can_expand(CheckpointFormat.FULL_AUDIT)
        assert result is False


class TestGetExpansionState:
    """Tests for get_expansion_state function (Task 6.3)."""

    def test_get_expansion_state_returns_state(self) -> None:
        """get_expansion_state should return current state."""
        details = ExpandableDetails(
            collapsed_view="Summary",
            expanded_view="Full details",
            state=ExpansionState.COLLAPSED,
        )
        result = get_expansion_state(details)
        assert result == ExpansionState.COLLAPSED

    def test_get_expansion_state_expanded(self) -> None:
        """get_expansion_state should return EXPANDED after expansion."""
        details = ExpandableDetails(
            collapsed_view="Summary",
            expanded_view="Full details",
            state=ExpansionState.EXPANDED,
        )
        result = get_expansion_state(details)
        assert result == ExpansionState.EXPANDED


class TestFormatTransitions:
    """Tests for format transitions and expansion behavior."""

    def test_minimal_to_full_audit_expansion(self) -> None:
        """Minimal format should expand to full audit content."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
        ]
        decisions = extract_key_decisions(operations)
        summary = SummaryCheckpoint(decisions=decisions, details_available=True)
        assert can_expand(CheckpointFormat.MINIMAL)
        assert summary.details_available is True

    def test_summary_to_full_audit_expansion(self) -> None:
        """Summary format should expand to full audit content."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
            {"type": "update", "target": "config.yaml", "outcome": "success"},
        ]
        decisions = extract_key_decisions(operations)
        summary = SummaryCheckpoint(decisions=decisions, details_available=True)
        formatted = format_summary_checkpoint(summary)
        assert "[Expand Details]" in formatted or "Expand" in formatted
        assert can_expand(CheckpointFormat.SUMMARY)

    def test_expandable_details_workflow(self) -> None:
        """Complete expandable details workflow should work end-to-end."""
        details = ExpandableDetails(
            collapsed_view="Summary: 2 operations completed successfully",
            expanded_view=(
                "Full Audit Trail:\n"
                "1. [10:30:00] CREATE module.py - success\n"
                "2. [10:30:05] UPDATE config.yaml - success"
            ),
            state=ExpansionState.COLLAPSED,
        )
        assert get_expansion_state(details) == ExpansionState.COLLAPSED
        expanded_content = expand_checkpoint(details)
        assert get_expansion_state(details) == ExpansionState.EXPANDED
        assert "Full Audit Trail" in expanded_content


class TestAC2SummaryFormatContent:
    """Tests for AC #2: Summary Format with key decisions."""

    def test_summary_format_has_key_decisions(self) -> None:
        """Summary format should display key decisions (AC #2)."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
            {"type": "update", "target": "config.yaml", "outcome": "success"},
        ]
        decisions = extract_key_decisions(operations)
        assert len(decisions) >= 2

    def test_summary_format_numbered_list(self) -> None:
        """Summary format should be numbered list (AC #2)."""
        checkpoint = SummaryCheckpoint(
            decisions=["Decision A", "Decision B", "Decision C"],
            details_available=True,
        )
        formatted = format_summary_checkpoint(checkpoint)
        assert "1" in formatted and "2" in formatted and "3" in formatted


class TestAC3FullAuditTrailCompleteness:
    """Tests for AC #3: Full Audit Trail with complete information."""

    def test_audit_trail_has_timestamps(self) -> None:
        """Full audit trail should include timestamps (AC #3)."""
        operations: list[dict[str, object]] = [
            {
                "type": "create",
                "target": "module.py",
                "outcome": "success",
                "timestamp": "2024-01-15T10:30:00",
            },
        ]
        log = generate_operation_log(operations)
        assert "10:30" in log or ":" in log

    def test_audit_trail_has_operation_details(self) -> None:
        """Full audit trail should include operation details (AC #3)."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
        ]
        log = generate_operation_log(operations)
        assert "create" in log.lower() or "module" in log.lower()

    def test_audit_trail_has_outcomes(self) -> None:
        """Full audit trail should include outcomes (AC #3)."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
        ]
        log = generate_operation_log(operations)
        assert "success" in log.lower()

    def test_audit_trail_requires_explicit_approval(self) -> None:
        """Full audit trail should require explicit approval (AC #3)."""
        checkpoint = AuditTrailCheckpoint(
            operation_log=[],
            approval_required=True,
        )
        formatted = format_audit_trail_checkpoint(checkpoint)
        assert "APPROVE" in formatted.upper()


class TestAC4ExpandableDetailsFull:
    """Tests for AC #4: Expandable Details functionality."""

    def test_minimal_can_expand_to_full(self) -> None:
        """Minimal format should expand to Full Audit (AC #4)."""
        assert can_expand(CheckpointFormat.MINIMAL) is True

    def test_summary_can_expand_to_full(self) -> None:
        """Summary format should expand to Full Audit (AC #4)."""
        assert can_expand(CheckpointFormat.SUMMARY) is True

    def test_expansion_tracks_state(self) -> None:
        """Expansion should track state for UI rendering (AC #4)."""
        details = ExpandableDetails(
            collapsed_view="Summary",
            expanded_view="Full details",
            state=ExpansionState.COLLAPSED,
        )
        assert get_expansion_state(details) == ExpansionState.COLLAPSED
        expand_checkpoint(details)
        assert get_expansion_state(details) == ExpansionState.EXPANDED

    def test_expansion_reveals_context(self) -> None:
        """Expand action should reveal full context (AC #4)."""
        details = ExpandableDetails(
            collapsed_view="3 operations completed",
            expanded_view="Full context with all operation details and timestamps",
            state=ExpansionState.COLLAPSED,
        )
        result = expand_checkpoint(details)
        assert "Full context" in result or "operation details" in result


class TestTask456EdgeCases:
    """Tests for edge cases and boundary conditions in Tasks 4-6."""

    def test_extract_key_decisions_missing_fields(self) -> None:
        """extract_key_decisions should handle operations with missing fields."""
        operations: list[dict[str, object]] = [
            {"type": "create"},
            {"target": "file.py"},
        ]
        result = extract_key_decisions(operations)
        assert isinstance(result, list)

    def test_generate_operation_log_missing_timestamp(self) -> None:
        """generate_operation_log should handle missing timestamps."""
        operations: list[dict[str, object]] = [
            {"type": "create", "target": "module.py", "outcome": "success"},
        ]
        result = generate_operation_log(operations)
        assert isinstance(result, str)

    def test_expand_checkpoint_empty_expanded_view(self) -> None:
        """expand_checkpoint should handle empty expanded_view."""
        details = ExpandableDetails(
            collapsed_view="Summary",
            expanded_view="",
            state=ExpansionState.COLLAPSED,
        )
        result = expand_checkpoint(details)
        assert isinstance(result, str)

    def test_format_summary_checkpoint_special_characters(self) -> None:
        """format_summary_checkpoint should handle special characters."""
        checkpoint = SummaryCheckpoint(
            decisions=["Created file: path/to/module.py", "Updated <config> & settings"],
            details_available=True,
        )
        result = format_summary_checkpoint(checkpoint)
        assert isinstance(result, str)

    def test_audit_trail_large_log(self) -> None:
        """AuditTrailCheckpoint should handle large operation logs."""
        log_entries = [
            OperationLogEntry(
                timestamp=datetime(2024, 1, 15, 10 + i // 60, 30, i % 60),
                operation_type="update",
                target=f"file_{i}.py",
                details=f"Updated file {i}",
                outcome="success",
            )
            for i in range(100)
        ]
        checkpoint = AuditTrailCheckpoint(
            operation_log=log_entries,
            approval_required=True,
        )
        assert len(checkpoint.operation_log) == 100


# =============================================================================
# Task 7: Integration with Automation Controller (Story 2b-7)
# =============================================================================

from pcmrp_tools.bmad_automation.checkpoint_presenter import (
    CheckpointOrchestrator,
    OrchestratorResult,
)


class TestCheckpointOrchestratorClass:
    """Tests for CheckpointOrchestrator class (Task 7.1)."""

    def test_checkpoint_orchestrator_instantiation(self) -> None:
        """CheckpointOrchestrator should be instantiable."""
        orchestrator = CheckpointOrchestrator()
        assert orchestrator is not None

    def test_checkpoint_orchestrator_has_present_checkpoint_method(self) -> None:
        """CheckpointOrchestrator should have present_checkpoint method."""
        orchestrator = CheckpointOrchestrator()
        assert hasattr(orchestrator, "present_checkpoint")
        assert callable(orchestrator.present_checkpoint)

    def test_checkpoint_orchestrator_has_handle_expansion_method(self) -> None:
        """CheckpointOrchestrator should have handle_expansion method."""
        orchestrator = CheckpointOrchestrator()
        assert hasattr(orchestrator, "handle_expansion")
        assert callable(orchestrator.handle_expansion)


class TestOrchestratorResultDataclass:
    """Tests for OrchestratorResult dataclass (Task 7.1)."""

    def test_orchestrator_result_creation(self) -> None:
        """OrchestratorResult should be creatable with all fields."""
        result = OrchestratorResult(
            formatted_output="Test output",
            format_used=CheckpointFormat.MINIMAL,
            confidence_score=85.0,
            expandable=True,
        )
        assert result.formatted_output == "Test output"
        assert result.format_used == CheckpointFormat.MINIMAL
        assert result.confidence_score == 85.0
        assert result.expandable is True

    def test_orchestrator_result_to_dict(self) -> None:
        """OrchestratorResult should be serializable to dict."""
        result = OrchestratorResult(
            formatted_output="Test",
            format_used=CheckpointFormat.SUMMARY,
            confidence_score=65.0,
            expandable=True,
        )
        result_dict = asdict(result)
        assert result_dict["formatted_output"] == "Test"
        assert result_dict["format_used"] == CheckpointFormat.SUMMARY


class TestOrchestratorPresentCheckpoint:
    """Tests for present_checkpoint method (Task 7.2)."""

    def test_present_checkpoint_returns_orchestrator_result(self) -> None:
        """present_checkpoint should return OrchestratorResult."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 85.0,
            "operations": [{"type": "validate"}],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert isinstance(result, OrchestratorResult)

    def test_present_checkpoint_includes_confidence_score(self) -> None:
        """present_checkpoint should include confidence score in result."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 75.0,
            "operations": [],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.confidence_score == 75.0

    def test_present_checkpoint_sets_expandable_flag(self) -> None:
        """present_checkpoint should set expandable flag based on format."""
        orchestrator = CheckpointOrchestrator()
        # High confidence (minimal) should be expandable
        high_conf: dict[str, object] = {"confidence": 90.0, "operations": []}
        result_high = orchestrator.present_checkpoint(high_conf)
        assert result_high.expandable is True

        # Full audit should not be expandable (already full)
        low_conf: dict[str, object] = {"confidence": 25.0, "operations": []}
        result_low = orchestrator.present_checkpoint(low_conf)
        assert result_low.expandable is False


class TestOrchestratorFormatSelection:
    """Tests for format selection in orchestrator (Task 7.2)."""

    def test_high_confidence_checkpoint_uses_minimal_format(self) -> None:
        """High confidence (>=80%) should use MINIMAL format (AC Integration #1)."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 85.0,
            "operations": [{"type": "validate", "target": "prd"}],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.format_used == CheckpointFormat.MINIMAL
        # Verify output is concise (1-2 lines)
        line_count = len(result.formatted_output.strip().split("\n"))
        assert line_count <= 2

    def test_medium_confidence_checkpoint_uses_summary_format(self) -> None:
        """Medium confidence (50-79%) should use SUMMARY format (AC Integration #2)."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 65.0,
            "operations": [{"type": "validate"}, {"type": "transform"}],
            "decisions": ["Used default pattern", "Skipped optional step"],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.format_used == CheckpointFormat.SUMMARY
        # Summary should include decision info
        assert "decision" in result.formatted_output.lower() or len(result.formatted_output) > 50

    def test_low_confidence_checkpoint_uses_full_audit_format(self) -> None:
        """Low confidence (<50%) should use FULL_AUDIT format (AC Integration #3)."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 30.0,
            "operations": [{"type": "analyze", "target": "requirements"}],
            "log": ["Step 1 started", "Analysis complete", "Issues found"],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.format_used == CheckpointFormat.FULL_AUDIT
        # Full audit should include approval action
        assert "APPROVE" in result.formatted_output.upper() or "audit" in result.formatted_output.lower()


class TestOrchestratorHandleExpansion:
    """Tests for handle_expansion method (Task 7.4)."""

    def test_handle_expansion_returns_expanded_content(self) -> None:
        """handle_expansion should return expanded content."""
        orchestrator = CheckpointOrchestrator()
        # First present a minimal checkpoint
        checkpoint_data: dict[str, object] = {
            "confidence": 90.0,
            "operations": [{"type": "validate", "target": "prd"}],
        }
        initial_result = orchestrator.present_checkpoint(checkpoint_data)
        # Then expand it
        expanded = orchestrator.handle_expansion(checkpoint_data)
        assert isinstance(expanded, str)
        assert len(expanded) >= len(initial_result.formatted_output)

    def test_handle_expansion_shows_full_audit(self) -> None:
        """handle_expansion should show full audit trail."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 90.0,
            "operations": [
                {"type": "validate", "target": "prd", "outcome": "success"},
                {"type": "analyze", "target": "requirements", "outcome": "success"},
            ],
            "log": ["Started validation", "PRD validated", "Requirements analyzed"],
        }
        expanded = orchestrator.handle_expansion(checkpoint_data)
        # Expanded content should be comprehensive
        assert "audit" in expanded.lower() or "log" in expanded.lower() or len(expanded) > 100

    def test_expansion_from_minimal_to_full_details(self) -> None:
        """Expansion from minimal should reveal full details (AC Integration #4)."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 95.0,
            "operations": [
                {"type": "create", "target": "module.py", "outcome": "success"},
                {"type": "update", "target": "config.yaml", "outcome": "success"},
            ],
            "decisions": ["Used factory pattern", "Applied singleton config"],
            "log": ["Module creation started", "Module created", "Config updated"],
        }

        # Initial minimal presentation
        initial_result = orchestrator.present_checkpoint(checkpoint_data)
        assert initial_result.format_used == CheckpointFormat.MINIMAL
        initial_lines = len(initial_result.formatted_output.strip().split("\n"))

        # Expand to full details
        expanded = orchestrator.handle_expansion(checkpoint_data)
        expanded_lines = len(expanded.strip().split("\n"))

        # Expanded should have more content
        assert expanded_lines > initial_lines


class TestOrchestratorConfidencePassthrough:
    """Tests for confidence score passthrough (Task 7.3)."""

    def test_confidence_from_validation_source(self) -> None:
        """Orchestrator should accept confidence from validation source."""
        orchestrator = CheckpointOrchestrator()
        # Simulating confidence from a validation result
        validation_confidence = 92.5
        checkpoint_data: dict[str, object] = {
            "confidence": validation_confidence,
            "source": "validation",
            "operations": [{"type": "validate"}],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.confidence_score == validation_confidence

    def test_confidence_from_batch_source(self) -> None:
        """Orchestrator should accept confidence from batch source."""
        orchestrator = CheckpointOrchestrator()
        # Simulating confidence from a batch operation
        batch_confidence = 45.0
        checkpoint_data: dict[str, object] = {
            "confidence": batch_confidence,
            "source": "batch",
            "operations": [{"type": "batch_update"}],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.confidence_score == batch_confidence
        assert result.format_used == CheckpointFormat.FULL_AUDIT

    def test_missing_confidence_defaults_to_zero(self) -> None:
        """Missing confidence should default to 0 (full audit)."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "operations": [{"type": "unknown"}],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.confidence_score == 0.0
        assert result.format_used == CheckpointFormat.FULL_AUDIT


class TestOrchestratorIntegrationScenarios:
    """Integration tests showing format selection in practice (Task 7.5)."""

    def test_high_confidence_workflow_validation(self) -> None:
        """High confidence workflow validation uses minimal checkpoint."""
        orchestrator = CheckpointOrchestrator()
        # Simulating a high-confidence validation checkpoint
        checkpoint_data: dict[str, object] = {
            "confidence": 88.0,
            "step_id": "validation-step",
            "operations": [
                {"type": "validate", "target": "prd.md", "outcome": "passed"},
                {"type": "validate", "target": "architecture.md", "outcome": "passed"},
            ],
            "decisions": ["All required sections present"],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.format_used == CheckpointFormat.MINIMAL
        assert "[Confirm]" in result.formatted_output
        assert result.expandable is True

    def test_medium_confidence_transformation(self) -> None:
        """Medium confidence transformation uses summary checkpoint."""
        orchestrator = CheckpointOrchestrator()
        # Simulating a medium-confidence transformation
        checkpoint_data: dict[str, object] = {
            "confidence": 72.0,
            "step_id": "transform-step",
            "operations": [
                {"type": "transform", "target": "data.json", "outcome": "success"},
                {"type": "transform", "target": "config.yaml", "outcome": "warning"},
            ],
            "decisions": [
                "Applied schema migration v2",
                "Preserved legacy field mappings",
            ],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.format_used == CheckpointFormat.SUMMARY
        assert result.expandable is True

    def test_low_confidence_analysis(self) -> None:
        """Low confidence analysis uses full audit checkpoint."""
        orchestrator = CheckpointOrchestrator()
        # Simulating a low-confidence analysis
        checkpoint_data: dict[str, object] = {
            "confidence": 35.0,
            "step_id": "analysis-step",
            "operations": [
                {"type": "analyze", "target": "dependencies", "outcome": "issues_found"},
            ],
            "decisions": [
                "Detected circular dependency",
                "Manual review recommended",
            ],
            "log": [
                "Analysis started",
                "Scanning dependencies...",
                "Found circular ref: A -> B -> A",
                "Analysis complete with warnings",
            ],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.format_used == CheckpointFormat.FULL_AUDIT
        assert result.expandable is False  # Already full audit
        assert "[Approve]" in result.formatted_output

    def test_expansion_workflow_complete(self) -> None:
        """Complete expansion workflow from initial presentation to full details."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 82.0,
            "operations": [
                {"type": "create", "target": "new_module.py", "outcome": "success"},
            ],
            "decisions": ["Used standard module template"],
            "log": ["Module scaffolded", "Imports added", "Tests generated"],
        }

        # Step 1: Present initial checkpoint
        initial = orchestrator.present_checkpoint(checkpoint_data)
        assert initial.format_used == CheckpointFormat.MINIMAL
        assert initial.expandable is True

        # Step 2: User requests expansion
        expanded = orchestrator.handle_expansion(checkpoint_data)

        # Step 3: Verify expanded content is comprehensive
        assert len(expanded) > len(initial.formatted_output)
        assert "AUDIT" in expanded.upper() or "Log" in expanded

    def test_boundary_confidence_80(self) -> None:
        """Confidence exactly 80 should use minimal format."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 80.0,
            "operations": [{"type": "validate"}],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.format_used == CheckpointFormat.MINIMAL

    def test_boundary_confidence_50(self) -> None:
        """Confidence exactly 50 should use summary format."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 50.0,
            "operations": [{"type": "validate"}],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.format_used == CheckpointFormat.SUMMARY

    def test_boundary_confidence_49(self) -> None:
        """Confidence 49 should use full audit format."""
        orchestrator = CheckpointOrchestrator()
        checkpoint_data: dict[str, object] = {
            "confidence": 49.0,
            "operations": [{"type": "validate"}],
        }
        result = orchestrator.present_checkpoint(checkpoint_data)
        assert result.format_used == CheckpointFormat.FULL_AUDIT
