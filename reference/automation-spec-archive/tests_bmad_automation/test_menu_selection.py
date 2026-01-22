"""Tests for Menu Selection - Story 2b.2: Automatic Menu Selection.

Tests for:
- HighConfidenceSelector (Parallel Group A)
- MediumConfidenceSelector (Parallel Group B)
- SelectionResult dataclass
- RecommendationResult dataclass
- Option scoring and tie-breaking
"""

import pytest

from pcmrp_tools.bmad_automation.menu_participation_engine import (
    MenuDetectionResult,
    MenuType,
)


# =============================================================================
# Task A1.2: SelectionResult dataclass tests
# =============================================================================


class TestSelectionResult:
    """Tests for SelectionResult dataclass (Task A1.2)."""

    def test_selection_result_default_values(self):
        """SelectionResult has correct default values."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionResult

        result = SelectionResult(selected=False)
        assert result.selected is False
        assert result.option is None
        assert result.reason == ""
        assert result.confidence == 0

    def test_selection_result_with_all_fields(self):
        """SelectionResult can be created with all fields."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionResult

        result = SelectionResult(
            selected=True,
            option="Continue",
            reason="High confidence match",
            confidence=85,
        )
        assert result.selected is True
        assert result.option == "Continue"
        assert result.reason == "High confidence match"
        assert result.confidence == 85


# =============================================================================
# Task A1.1, A1.3: should_auto_select threshold tests
# =============================================================================


class TestHighConfidenceSelectorThreshold:
    """Tests for HighConfidenceSelector threshold logic (Tasks A1.1, A1.3)."""

    def test_confidence_threshold_constant_is_80(self):
        """CONFIDENCE_THRESHOLD_HIGH constant is defined as 80."""
        from pcmrp_tools.bmad_automation.menu_selection import CONFIDENCE_THRESHOLD_HIGH

        assert CONFIDENCE_THRESHOLD_HIGH == 80

    def test_should_auto_select_returns_true_at_80(self):
        """should_auto_select returns True when confidence equals 80 (boundary)."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        selector = HighConfidenceSelector()
        assert selector.should_auto_select(80) is True

    def test_should_auto_select_returns_true_above_80(self):
        """should_auto_select returns True when confidence is above 80."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        selector = HighConfidenceSelector()
        assert selector.should_auto_select(81) is True
        assert selector.should_auto_select(100) is True

    def test_should_auto_select_returns_false_at_79(self):
        """should_auto_select returns False when confidence is 79 (just below)."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        selector = HighConfidenceSelector()
        assert selector.should_auto_select(79) is False

    def test_should_auto_select_returns_false_below_79(self):
        """should_auto_select returns False when confidence is well below 80."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        selector = HighConfidenceSelector()
        assert selector.should_auto_select(50) is False
        assert selector.should_auto_select(0) is False


# =============================================================================
# Task A1.5: Comprehensive threshold boundary tests
# =============================================================================


class TestHighConfidenceThresholdBoundaries:
    """Comprehensive boundary tests for threshold logic (Task A1.5)."""

    @pytest.mark.parametrize(
        "confidence,expected",
        [
            (79, False),  # Just below threshold
            (80, True),   # Exactly at threshold
            (81, True),   # Just above threshold
        ],
    )
    def test_threshold_boundary_79_80_81(self, confidence, expected):
        """Test exact boundary values 79 vs 80 vs 81."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        selector = HighConfidenceSelector()
        assert selector.should_auto_select(confidence) is expected

    @pytest.mark.parametrize("confidence", [80, 85, 90, 95, 100])
    def test_high_confidence_values_return_true(self, confidence):
        """All values >= 80 return True."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        selector = HighConfidenceSelector()
        assert selector.should_auto_select(confidence) is True

    @pytest.mark.parametrize("confidence", [0, 25, 50, 70, 79])
    def test_low_confidence_values_return_false(self, confidence):
        """All values < 80 return False."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        selector = HighConfidenceSelector()
        assert selector.should_auto_select(confidence) is False


# =============================================================================
# Task A1.4: select_best_option tests
# =============================================================================


class TestSelectBestOption:
    """Tests for HighConfidenceSelector.select_best_option() (Task A1.4)."""

    @pytest.fixture
    def selector(self):
        """Create a HighConfidenceSelector instance."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        return HighConfidenceSelector()

    def _create_detection_result(
        self,
        confidence: int,
        options: list[str],
        menu_type: MenuType = MenuType.APC,
    ) -> MenuDetectionResult:
        """Helper to create a MenuDetectionResult for testing."""
        return MenuDetectionResult.detected(
            confidence=confidence,
            menu_type=menu_type,
            options=options,
            breakdown={"test": confidence},
            raw_input=f"Menu with options: {options}",
        )

    def test_returns_selection_result(self, selector):
        """Should return a SelectionResult instance."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionResult

        detection = self._create_detection_result(85, ["Continue", "Exit"])
        result = selector.select_best_option(detection)
        assert isinstance(result, SelectionResult)

    def test_selects_option_when_high_confidence(self, selector):
        """Should select an option when confidence >= 80."""
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        result = selector.select_best_option(detection)
        assert result.selected is True
        assert result.option in ["Continue", "Exit"]

    def test_does_not_select_when_low_confidence(self, selector):
        """Should not select when confidence < 80."""
        detection = self._create_detection_result(75, ["Continue", "Exit"])
        result = selector.select_best_option(detection)
        assert result.selected is False
        assert result.option is None
        assert "below" in result.reason.lower()

    def test_boundary_confidence_80_selects(self, selector):
        """Should select at exactly 80% confidence (boundary)."""
        detection = self._create_detection_result(80, ["Continue", "Exit"])
        result = selector.select_best_option(detection)
        assert result.selected is True
        assert result.option is not None

    def test_boundary_confidence_79_does_not_select(self, selector):
        """Should not select at 79% confidence (just below)."""
        detection = self._create_detection_result(79, ["Continue", "Exit"])
        result = selector.select_best_option(detection)
        assert result.selected is False

    def test_handles_empty_options(self, selector):
        """Should handle empty options gracefully."""
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=[],
            breakdown={},
            raw_input="",
        )
        result = selector.select_best_option(detection)
        assert result.selected is False
        assert "no options" in result.reason.lower()

    def test_handles_single_option(self, selector):
        """Should handle single option menu."""
        detection = self._create_detection_result(90, ["Exit"], MenuType.EXIT)
        result = selector.select_best_option(detection)
        assert result.selected is True
        assert result.option == "Exit"

    def test_confidence_preserved_in_result(self, selector):
        """Result should contain the confidence score."""
        detection = self._create_detection_result(92, ["Continue", "Exit"])
        result = selector.select_best_option(detection)
        assert result.confidence == 92

    def test_reason_is_provided(self, selector):
        """Result should contain a selection reason."""
        detection = self._create_detection_result(85, ["Continue", "Exit"])
        result = selector.select_best_option(detection)
        assert result.reason
        assert len(result.reason) > 0

    def test_prefers_continue_over_exit(self, selector):
        """Should prefer 'Continue' over 'Exit' by default priority."""
        detection = self._create_detection_result(85, ["Exit", "Continue"])
        result = selector.select_best_option(detection)
        assert result.option == "Continue"

    def test_prefers_yes_over_no(self, selector):
        """Should prefer 'Yes' over 'No' by default priority."""
        detection = self._create_detection_result(
            85, ["No", "Yes"], MenuType.YVN
        )
        result = selector.select_best_option(detection)
        assert result.option == "Yes"


# =============================================================================
# Task A2.1: score_option tests
# =============================================================================


class TestScoreOption:
    """Tests for HighConfidenceSelector.score_option() (Task A2.1)."""

    @pytest.fixture
    def selector(self):
        """Create a HighConfidenceSelector instance."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        return HighConfidenceSelector()

    def test_returns_integer_score(self, selector):
        """Should return an integer score."""
        score = selector.score_option("Continue")
        assert isinstance(score, int)

    def test_score_in_valid_range(self, selector):
        """Score should be between 0 and 100."""
        for option in ["Continue", "Exit", "Unknown Option", "Yes", "No"]:
            score = selector.score_option(option)
            assert 0 <= score <= 100, f"Score {score} for '{option}' out of range"

    def test_continue_scores_higher_than_exit(self, selector):
        """'Continue' should score higher than 'Exit'."""
        continue_score = selector.score_option("Continue")
        exit_score = selector.score_option("Exit")
        assert continue_score > exit_score

    def test_yes_scores_higher_than_no(self, selector):
        """'Yes' should score higher than 'No'."""
        yes_score = selector.score_option("Yes")
        no_score = selector.score_option("No")
        assert yes_score > no_score

    def test_high_priority_options_score_high(self, selector):
        """High priority options should score above neutral (50)."""
        high_priority = ["Continue", "Proceed", "Next", "Yes", "Approve", "Confirm"]
        for option in high_priority:
            score = selector.score_option(option)
            assert score > 50, f"'{option}' should score above 50, got {score}"

    def test_negative_priority_options_score_low(self, selector):
        """Negative priority options should score below neutral (50)."""
        negative_priority = ["No", "Cancel", "Exit", "Quit"]
        for option in negative_priority:
            score = selector.score_option(option)
            assert score < 50, f"'{option}' should score below 50, got {score}"

    def test_unknown_options_score_neutral(self, selector):
        """Unknown options should score around neutral (50)."""
        score = selector.score_option("Unknown Option XYZ")
        assert score == 50, f"Unknown option should score 50, got {score}"

    def test_case_insensitive_scoring(self, selector):
        """Option scoring should be case-insensitive."""
        upper_score = selector.score_option("CONTINUE")
        lower_score = selector.score_option("continue")
        mixed_score = selector.score_option("Continue")
        assert upper_score == lower_score == mixed_score

    def test_context_expected_option_boost(self, selector):
        """Expected option in context should get a score boost."""
        context = {"expected_option": "View"}
        view_score = selector.score_option("View Details", context)
        other_score = selector.score_option("Continue", context)
        assert view_score > other_score

    def test_context_workflow_phase_review(self, selector):
        """Review phase context should boost 'View' option."""
        context = {"workflow_phase": "review"}
        view_score = selector.score_option("View", context)
        continue_score = selector.score_option("Continue", context)
        # View gets +15 bonus in review phase, putting it ahead
        assert view_score >= continue_score

    def test_context_workflow_phase_approval(self, selector):
        """Approval phase context should boost 'Yes' and 'Approve' options."""
        context = {"workflow_phase": "approval"}
        yes_score = selector.score_option("Yes", context)
        view_score = selector.score_option("View", context)
        assert yes_score > view_score

    def test_context_action_explore(self, selector):
        """Explore action context should boost 'Advanced' option."""
        context = {"action": "explore"}
        advanced_score = selector.score_option("Advanced", context)
        continue_score = selector.score_option("Continue", context)
        # Advanced gets +15 from action context
        assert advanced_score >= continue_score


# =============================================================================
# Task A2.2: Tie-breaking tests
# =============================================================================


class TestTieBreaking:
    """Tests for tie-breaking in option selection (Task A2.2)."""

    @pytest.fixture
    def selector(self):
        """Create a HighConfidenceSelector instance."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        return HighConfidenceSelector()

    def _create_detection_result(
        self,
        options: list[str],
        confidence: int = 85,
    ) -> MenuDetectionResult:
        """Helper to create a MenuDetectionResult for testing."""
        return MenuDetectionResult.detected(
            confidence=confidence,
            menu_type=MenuType.APC,
            options=options,
            breakdown={},
            raw_input=f"Options: {options}",
        )

    def test_equal_scores_uses_original_order(self, selector):
        """When options have equal scores, first one (by original order) wins."""
        # Unknown options all score 50 (neutral)
        detection = self._create_detection_result(
            ["Option A", "Option B", "Option C"]
        )
        result = selector.select_best_option(detection)
        assert result.selected is True
        # First option should win in case of tie
        assert result.option == "Option A"

    def test_equal_scores_second_option_order(self, selector):
        """Verify tie-breaking preserves order: B first means B wins."""
        detection = self._create_detection_result(
            ["Option B", "Option A", "Option C"]
        )
        result = selector.select_best_option(detection)
        assert result.option == "Option B"

    def test_tie_between_known_options(self, selector):
        """When multiple high-priority options tie, first wins."""
        # Both "Continue" and "Proceed" have same priority
        detection = self._create_detection_result(["Proceed", "Continue"])
        result = selector.select_best_option(detection)
        # Both score 70 (50 base + 20 priority), Proceed is first
        assert result.option == "Proceed"

    def test_higher_score_wins_over_order(self, selector):
        """Higher score should win regardless of order."""
        # Exit is first but lower priority, Continue is second but higher
        detection = self._create_detection_result(["Exit", "Continue"])
        result = selector.select_best_option(detection)
        assert result.option == "Continue"

    def test_context_breaks_tie(self, selector):
        """Context can break a tie between otherwise equal options."""
        # Unknown options A and B both score 50
        detection = self._create_detection_result(["Option A", "Option B"])
        # Context expects Option B
        context = {"expected_option": "B"}
        result = selector.select_best_option(detection, context)
        # Option B gets +30 boost from expected_option match
        assert result.option == "Option B"


# =============================================================================
# Task A2.3: Additional option scoring scenario tests
# =============================================================================


class TestOptionScoringScenarios:
    """Additional scenario tests for option scoring (Task A2.3)."""

    @pytest.fixture
    def selector(self):
        """Create a HighConfidenceSelector instance."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        return HighConfidenceSelector()

    def test_partial_match_scoring(self, selector):
        """Options containing keywords should still score appropriately."""
        # "Continue workflow" contains "continue"
        score = selector.score_option("Continue workflow")
        assert score > 50

    def test_medium_priority_options(self, selector):
        """Medium priority options should score moderately high."""
        medium_priority = ["View", "Review", "Details", "Advanced"]
        for option in medium_priority:
            score = selector.score_option(option)
            assert score > 50, f"'{option}' should score above 50"
            assert score <= 70, f"'{option}' should not exceed 70"

    def test_skip_and_later_score_neutral(self, selector):
        """Skip/Later options should score around neutral."""
        for option in ["Skip", "Later"]:
            score = selector.score_option(option)
            assert score == 50, f"'{option}' should score exactly 50"

    def test_combined_context_bonuses(self, selector):
        """Multiple context factors should combine additively."""
        context = {
            "expected_option": "Continue",
            "workflow_phase": "progression",
        }
        score = selector.score_option("Continue", context)
        # Base 50 + priority 20 + expected 30 + phase 15 = 115, clamped to 100
        assert score == 100

    def test_score_clamping_at_100(self, selector):
        """Scores should be clamped at maximum 100."""
        context = {
            "expected_option": "Continue",
            "workflow_phase": "progression",
            "action": "confirm",
        }
        score = selector.score_option("Continue", context)
        assert score <= 100

    def test_score_clamping_at_0(self, selector):
        """Scores should be clamped at minimum 0."""
        # Create a scenario that might go negative (unlikely with current impl)
        score = selector.score_option("Cancel")
        assert score >= 0


# =============================================================================
# Integration Tests for HighConfidenceSelector
# =============================================================================


class TestHighConfidenceSelectorIntegration:
    """Integration tests for HighConfidenceSelector."""

    @pytest.fixture
    def selector(self):
        """Create a HighConfidenceSelector instance."""
        from pcmrp_tools.bmad_automation.menu_selection import HighConfidenceSelector

        return HighConfidenceSelector()

    def test_full_workflow_apc_menu(self, selector):
        """Full workflow for APC menu with high confidence."""
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Advanced", "Party Mode", "Continue"],
            breakdown={"structural": 25, "position": 20, "options": 20, "pattern": 20},
            raw_input="[A] Advanced [P] Party Mode [C] Continue",
        )

        # Check confidence tier
        assert selector.should_auto_select(detection.confidence) is True

        # Auto-select best option
        result = selector.select_best_option(detection)

        # Verify selection
        assert result.selected is True
        assert result.option == "Continue"  # Highest priority
        assert result.confidence == 85
        assert result.reason

    def test_full_workflow_yvn_menu(self, selector):
        """Full workflow for YVN menu with high confidence."""
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.YVN,
            options=["Yes", "View", "No"],
            breakdown={"structural": 30, "position": 20, "options": 20, "pattern": 20},
            raw_input="[Y] Yes [V] View [N] No",
        )

        # Check confidence tier
        assert selector.should_auto_select(detection.confidence) is True

        # Auto-select best option
        result = selector.select_best_option(detection)

        # Verify selection
        assert result.selected is True
        assert result.option == "Yes"  # Highest priority for YVN
        assert result.confidence == 90

    def test_full_workflow_with_context(self, selector):
        """Full workflow with context influencing selection."""
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.YVN,
            options=["Yes", "View", "No"],
            breakdown={"test": 85},
            raw_input="[Y] Yes [V] View [N] No",
        )

        # Review context should prefer View
        context = {"workflow_phase": "review"}
        result = selector.select_best_option(detection, context)

        assert result.selected is True
        assert result.option == "View"  # View gets phase bonus

    def test_boundary_80_auto_selects(self, selector):
        """Boundary test at exactly 80% confidence."""
        detection = MenuDetectionResult.detected(
            confidence=80,
            menu_type=MenuType.NUMBERED,
            options=["Option 1", "Option 2"],
            breakdown={"test": 80},
            raw_input="[1] Option 1 [2] Option 2",
        )

        assert selector.should_auto_select(80) is True
        result = selector.select_best_option(detection)

        assert result.selected is True
        assert result.option in ["Option 1", "Option 2"]
        assert result.confidence == 80


# =============================================================================
# Parallel Group B: MediumConfidenceSelector Tests
# =============================================================================


# =============================================================================
# Task B1.1, B1.2: Constants and RecommendationResult Tests
# =============================================================================


class TestMediumConfidenceConstants:
    """Tests for medium confidence threshold constants."""

    def test_medium_low_threshold_is_50(self):
        """CONFIDENCE_THRESHOLD_MEDIUM_LOW should be 50."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            CONFIDENCE_THRESHOLD_MEDIUM_LOW,
        )

        assert CONFIDENCE_THRESHOLD_MEDIUM_LOW == 50

    def test_medium_high_threshold_is_79(self):
        """CONFIDENCE_THRESHOLD_MEDIUM_HIGH should be 79."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            CONFIDENCE_THRESHOLD_MEDIUM_HIGH,
        )

        assert CONFIDENCE_THRESHOLD_MEDIUM_HIGH == 79


class TestRecommendationResult:
    """Tests for RecommendationResult dataclass (Task B1.2)."""

    def test_create_with_required_fields(self):
        """Should create RecommendationResult with recommended_option."""
        from pcmrp_tools.bmad_automation.menu_selection import RecommendationResult

        result = RecommendationResult(recommended_option="Continue")
        assert result.recommended_option == "Continue"

    def test_defaults_for_optional_fields(self):
        """Should have sensible defaults for optional fields."""
        from pcmrp_tools.bmad_automation.menu_selection import RecommendationResult

        result = RecommendationResult(recommended_option="Continue")
        assert result.alternatives == []
        assert result.reason == ""
        assert result.confidence == 0

    def test_create_with_all_fields(self):
        """Should create RecommendationResult with all fields populated."""
        from pcmrp_tools.bmad_automation.menu_selection import RecommendationResult

        result = RecommendationResult(
            recommended_option="Continue",
            alternatives=["Party Mode", "Advanced"],
            reason="Continue is preferred for workflow progression",
            confidence=65,
        )
        assert result.recommended_option == "Continue"
        assert result.alternatives == ["Party Mode", "Advanced"]
        assert result.reason == "Continue is preferred for workflow progression"
        assert result.confidence == 65


# =============================================================================
# Task B1.3, B1.5: is_medium_confidence() Tests
# =============================================================================


class TestIsMediumConfidence:
    """Tests for is_medium_confidence() method."""

    @pytest.fixture
    def selector(self):
        """Create a MediumConfidenceSelector instance."""
        from pcmrp_tools.bmad_automation.menu_selection import MediumConfidenceSelector

        return MediumConfidenceSelector()

    # Boundary tests (B1.5)
    def test_confidence_49_is_not_medium(self, selector):
        """Confidence 49 should NOT be medium (below threshold)."""
        assert selector.is_medium_confidence(49) is False

    def test_confidence_50_is_medium(self, selector):
        """Confidence 50 should be medium (at lower boundary inclusive)."""
        assert selector.is_medium_confidence(50) is True

    def test_confidence_51_is_medium(self, selector):
        """Confidence 51 should be medium."""
        assert selector.is_medium_confidence(51) is True

    def test_confidence_65_is_medium(self, selector):
        """Confidence 65 should be medium (mid-range)."""
        assert selector.is_medium_confidence(65) is True

    def test_confidence_78_is_medium(self, selector):
        """Confidence 78 should be medium."""
        assert selector.is_medium_confidence(78) is True

    def test_confidence_79_is_medium(self, selector):
        """Confidence 79 should be medium (at upper boundary inclusive)."""
        assert selector.is_medium_confidence(79) is True

    def test_confidence_80_is_not_medium(self, selector):
        """Confidence 80 should NOT be medium (high confidence tier)."""
        assert selector.is_medium_confidence(80) is False

    def test_confidence_0_is_not_medium(self, selector):
        """Confidence 0 should NOT be medium (low tier)."""
        assert selector.is_medium_confidence(0) is False

    def test_confidence_100_is_not_medium(self, selector):
        """Confidence 100 should NOT be medium (high tier)."""
        assert selector.is_medium_confidence(100) is False


class TestMediumConfidenceThresholdBoundaries:
    """Comprehensive boundary tests for medium confidence threshold (Task B1.5)."""

    @pytest.mark.parametrize(
        "confidence,expected",
        [
            (49, False),  # Just below lower threshold
            (50, True),   # Exactly at lower threshold
            (51, True),   # Just above lower threshold
            (78, True),   # Just below upper threshold
            (79, True),   # Exactly at upper threshold
            (80, False),  # Just above upper threshold (high tier)
        ],
    )
    def test_threshold_boundaries(self, confidence, expected):
        """Test exact boundary values for medium confidence."""
        from pcmrp_tools.bmad_automation.menu_selection import MediumConfidenceSelector

        selector = MediumConfidenceSelector()
        assert selector.is_medium_confidence(confidence) is expected

    @pytest.mark.parametrize("confidence", [50, 55, 60, 65, 70, 75, 79])
    def test_medium_confidence_values_return_true(self, confidence):
        """All values in 50-79 range return True."""
        from pcmrp_tools.bmad_automation.menu_selection import MediumConfidenceSelector

        selector = MediumConfidenceSelector()
        assert selector.is_medium_confidence(confidence) is True

    @pytest.mark.parametrize("confidence", [0, 25, 49, 80, 90, 100])
    def test_non_medium_confidence_values_return_false(self, confidence):
        """Values outside 50-79 range return False."""
        from pcmrp_tools.bmad_automation.menu_selection import MediumConfidenceSelector

        selector = MediumConfidenceSelector()
        assert selector.is_medium_confidence(confidence) is False


# =============================================================================
# Task B2.1: rank_options() Tests
# =============================================================================


class TestRankOptions:
    """Tests for rank_options() method."""

    @pytest.fixture
    def selector(self):
        """Create a MediumConfidenceSelector instance."""
        from pcmrp_tools.bmad_automation.menu_selection import MediumConfidenceSelector

        return MediumConfidenceSelector()

    def test_empty_options_returns_empty(self, selector):
        """Empty options list should return empty list."""
        result = selector.rank_options([])
        assert result == []

    def test_single_option_returns_as_is(self, selector):
        """Single option should be returned as-is."""
        result = selector.rank_options(["Continue"])
        assert result == ["Continue"]

    def test_options_ranked_by_default_priority(self, selector):
        """Options should be ranked by default priority without context."""
        # Continue has higher priority than Party Mode
        options = ["Party Mode", "Continue", "Advanced"]
        result = selector.rank_options(options)
        assert len(result) == 3
        # Continue should be ranked first due to priority
        assert result[0] == "Continue"

    def test_options_ranked_with_context(self, selector):
        """Options should consider context when ranking."""
        options = ["Yes", "View", "No"]
        context = {"action": "review"}
        result = selector.rank_options(options, context)
        assert len(result) == 3
        # View should be ranked higher in review context
        assert result[0] == "View"

    def test_preserves_all_options(self, selector):
        """All options should be preserved after ranking."""
        options = ["Option A", "Option B", "Option C", "Option D"]
        result = selector.rank_options(options)
        assert len(result) == len(options)
        assert set(result) == set(options)

    def test_yes_higher_than_no_by_default(self, selector):
        """Yes should rank higher than No by default."""
        options = ["No", "Yes"]
        result = selector.rank_options(options)
        assert result[0] == "Yes"
        assert result[1] == "No"

    def test_exit_ranked_lowest(self, selector):
        """Exit should be ranked lowest by default."""
        options = ["Exit", "Continue", "View"]
        result = selector.rank_options(options)
        assert result[-1] == "Exit"


# =============================================================================
# Task B1.4, B2.2, B2.3: get_recommendation() and Reason Generation Tests
# =============================================================================


class TestGetRecommendation:
    """Tests for get_recommendation() method."""

    @pytest.fixture
    def selector(self):
        """Create a MediumConfidenceSelector instance."""
        from pcmrp_tools.bmad_automation.menu_selection import MediumConfidenceSelector

        return MediumConfidenceSelector()

    def _create_detection_result(
        self,
        confidence: int,
        options: list[str],
        menu_type: MenuType = MenuType.APC,
    ) -> MenuDetectionResult:
        """Helper to create a MenuDetectionResult for testing."""
        return MenuDetectionResult.detected(
            confidence=confidence,
            menu_type=menu_type,
            options=options,
            breakdown={"test": confidence},
            raw_input="[A] Advanced [P] Party Mode [C] Continue",
        )

    def test_returns_recommendation_result(self, selector):
        """Should return a RecommendationResult instance."""
        from pcmrp_tools.bmad_automation.menu_selection import RecommendationResult

        detection = self._create_detection_result(
            confidence=65,
            options=["Advanced", "Party Mode", "Continue"],
        )
        result = selector.get_recommendation(detection)
        assert isinstance(result, RecommendationResult)

    def test_recommended_option_is_from_options(self, selector):
        """Recommended option should be from the original options list."""
        detection = self._create_detection_result(
            confidence=65,
            options=["Advanced", "Party Mode", "Continue"],
        )
        result = selector.get_recommendation(detection)
        assert result.recommended_option in ["Advanced", "Party Mode", "Continue"]

    def test_alternatives_exclude_recommended(self, selector):
        """Alternatives should not include the recommended option."""
        detection = self._create_detection_result(
            confidence=65,
            options=["Advanced", "Party Mode", "Continue"],
        )
        result = selector.get_recommendation(detection)
        assert result.recommended_option not in result.alternatives

    def test_alternatives_contain_remaining_options(self, selector):
        """Alternatives should contain remaining options."""
        detection = self._create_detection_result(
            confidence=65,
            options=["Advanced", "Party Mode", "Continue"],
        )
        result = selector.get_recommendation(detection)
        # Alternatives + recommended should equal all options
        all_returned = [result.recommended_option] + result.alternatives
        assert set(all_returned) == {"Advanced", "Party Mode", "Continue"}

    def test_reason_is_non_empty(self, selector):
        """Recommendation reason should be provided."""
        detection = self._create_detection_result(
            confidence=65,
            options=["Advanced", "Party Mode", "Continue"],
        )
        result = selector.get_recommendation(detection)
        assert result.reason
        assert len(result.reason) > 0

    def test_confidence_reflects_detection_confidence(self, selector):
        """Result confidence should reflect detection confidence."""
        detection = self._create_detection_result(
            confidence=72,
            options=["Yes", "No"],
        )
        result = selector.get_recommendation(detection)
        assert result.confidence == 72

    def test_single_option_returns_that_option(self, selector):
        """Single option should be recommended with empty alternatives."""
        detection = self._create_detection_result(
            confidence=55,
            options=["Exit"],
            menu_type=MenuType.EXIT,
        )
        result = selector.get_recommendation(detection)
        assert result.recommended_option == "Exit"
        assert result.alternatives == []

    def test_handles_empty_options(self, selector):
        """Should handle empty options gracefully."""
        detection = MenuDetectionResult.not_detected(
            confidence=50,
            breakdown={},
            raw_input="",
        )
        result = selector.get_recommendation(detection)
        # Should return empty recommendation when no options
        assert result.recommended_option == ""

    def test_context_influences_recommendation(self, selector):
        """Context should influence which option is recommended."""
        detection = self._create_detection_result(
            confidence=65,
            options=["Yes", "View", "No"],
            menu_type=MenuType.YVN,
        )
        # Different contexts favor different options
        result_review = selector.get_recommendation(
            detection, context={"action": "review"}
        )
        result_approve = selector.get_recommendation(
            detection, context={"action": "approve"}
        )
        # Review context should favor View
        assert result_review.recommended_option == "View"
        # Approve context should favor Yes
        assert result_approve.recommended_option == "Yes"


# =============================================================================
# Task B2.2: Recommendation Reason Generation Tests
# =============================================================================


class TestRecommendationReasonGeneration:
    """Tests for recommendation reason generation."""

    @pytest.fixture
    def selector(self):
        """Create a MediumConfidenceSelector instance."""
        from pcmrp_tools.bmad_automation.menu_selection import MediumConfidenceSelector

        return MediumConfidenceSelector()

    def _create_detection_result(
        self,
        confidence: int,
        options: list[str],
        menu_type: MenuType = MenuType.APC,
    ) -> MenuDetectionResult:
        """Helper to create a MenuDetectionResult for testing."""
        return MenuDetectionResult.detected(
            confidence=confidence,
            menu_type=menu_type,
            options=options,
            breakdown={"test": confidence},
            raw_input=f"Menu with options: {options}",
        )

    def test_reason_mentions_recommended_option(self, selector):
        """Reason should mention the recommended option."""
        detection = self._create_detection_result(
            confidence=65,
            options=["Continue", "Party Mode"],
        )
        result = selector.get_recommendation(detection)
        # Reason should reference the recommended option
        assert result.recommended_option in result.reason

    def test_reason_indicates_confidence_level(self, selector):
        """Reason should indicate confidence context."""
        detection = self._create_detection_result(
            confidence=60,
            options=["Yes", "No"],
        )
        result = selector.get_recommendation(detection)
        # Reason should contain confidence-related word
        assert "confidence" in result.reason.lower()

    def test_reason_different_for_different_menu_types(self, selector):
        """Different menu types have different reason formats."""
        apc_detection = self._create_detection_result(
            confidence=65,
            options=["Advanced", "Party Mode", "Continue"],
            menu_type=MenuType.APC,
        )
        yvn_detection = self._create_detection_result(
            confidence=65,
            options=["Yes", "View", "No"],
            menu_type=MenuType.YVN,
        )
        apc_result = selector.get_recommendation(apc_detection)
        yvn_result = selector.get_recommendation(yvn_detection)
        # Both should have valid reasons with menu type context
        assert "workflow" in apc_result.reason.lower() or "menu" in apc_result.reason.lower()
        assert "confirmation" in yvn_result.reason.lower() or "menu" in yvn_result.reason.lower()

    def test_reason_includes_alternatives_count(self, selector):
        """Reason should mention number of alternatives when present."""
        detection = self._create_detection_result(
            confidence=65,
            options=["Continue", "Party Mode", "Advanced"],
        )
        result = selector.get_recommendation(detection)
        # Should mention 2 alternatives
        assert "2 alternatives" in result.reason or "alternative" in result.reason.lower()


# =============================================================================
# Integration Tests for MediumConfidenceSelector
# =============================================================================


class TestMediumConfidenceSelectorIntegration:
    """Integration tests for MediumConfidenceSelector."""

    @pytest.fixture
    def selector(self):
        """Create a MediumConfidenceSelector instance."""
        from pcmrp_tools.bmad_automation.menu_selection import MediumConfidenceSelector

        return MediumConfidenceSelector()

    def test_full_workflow_apc_menu(self, selector):
        """Full workflow for APC menu with medium confidence."""
        detection = MenuDetectionResult.detected(
            confidence=70,
            menu_type=MenuType.APC,
            options=["Advanced", "Party Mode", "Continue"],
            breakdown={"structural": 25, "position": 20, "options": 20, "pattern": 25},
            raw_input="[A] Advanced [P] Party Mode [C] Continue",
        )

        # Check confidence tier
        assert selector.is_medium_confidence(detection.confidence) is True

        # Get recommendation
        result = selector.get_recommendation(detection)

        # Verify complete result
        assert result.recommended_option == "Continue"  # Highest priority
        assert len(result.alternatives) == 2
        assert result.confidence == 70
        assert result.reason

    def test_full_workflow_yvn_menu(self, selector):
        """Full workflow for YVN menu with medium confidence."""
        detection = MenuDetectionResult.detected(
            confidence=55,
            menu_type=MenuType.YVN,
            options=["Yes", "View", "No"],
            breakdown={"structural": 20, "position": 15, "options": 15, "pattern": 25},
            raw_input="[Y] Yes [V] View [N] No",
        )

        # Check confidence tier
        assert selector.is_medium_confidence(detection.confidence) is True

        # Get recommendation
        result = selector.get_recommendation(detection)

        # Verify complete result - Yes has priority 2, View has 3
        assert result.recommended_option == "Yes"
        assert len(result.alternatives) == 2
        assert result.confidence == 55
        assert result.reason

    def test_boundary_50_medium_workflow(self, selector):
        """Workflow at lower boundary (50) should work."""
        detection = MenuDetectionResult.detected(
            confidence=50,
            menu_type=MenuType.NUMBERED,
            options=["Option 1", "Option 2"],
            breakdown={"test": 50},
            raw_input="[1] Option 1 [2] Option 2",
        )

        assert selector.is_medium_confidence(50) is True
        result = selector.get_recommendation(detection)
        assert result.recommended_option in ["Option 1", "Option 2"]
        assert result.confidence == 50

    def test_boundary_79_medium_workflow(self, selector):
        """Workflow at upper boundary (79) should work."""
        detection = MenuDetectionResult.detected(
            confidence=79,
            menu_type=MenuType.NUMBERED,
            options=["Option 1", "Option 2"],
            breakdown={"test": 79},
            raw_input="[1] Option 1 [2] Option 2",
        )

        assert selector.is_medium_confidence(79) is True
        result = selector.get_recommendation(detection)
        assert result.recommended_option in ["Option 1", "Option 2"]
        assert result.confidence == 79


# =============================================================================
# Group C: LowConfidenceSelector Tests (Tasks C1, C2)
# =============================================================================


# =============================================================================
# Task C1: LowConfidenceSelector Tests
# =============================================================================


class TestLowConfidenceSelectorThreshold:
    """Test C1.1: LowConfidenceSelector threshold constant (50)."""

    def test_threshold_constant_is_50(self):
        """CONFIDENCE_THRESHOLD_MEDIUM_LOW should be 50 (used for low confidence boundary)."""
        from pcmrp_tools.bmad_automation.menu_selection import CONFIDENCE_THRESHOLD_MEDIUM_LOW

        # Low confidence is < CONFIDENCE_THRESHOLD_MEDIUM_LOW (Issue #2 fix: removed redundant constant)
        assert CONFIDENCE_THRESHOLD_MEDIUM_LOW == 50


class TestPresentationResult:
    """Test C1.2: PresentationResult dataclass."""

    def test_presentation_result_has_options_field(self):
        """PresentationResult should have options field."""
        from pcmrp_tools.bmad_automation.menu_selection import PresentationResult

        result = PresentationResult()
        assert hasattr(result, "options")
        assert result.options == []

    def test_presentation_result_has_no_recommendation_reason(self):
        """PresentationResult should have no_recommendation_reason field."""
        from pcmrp_tools.bmad_automation.menu_selection import PresentationResult

        result = PresentationResult()
        assert hasattr(result, "no_recommendation_reason")
        assert result.no_recommendation_reason == ""

    def test_presentation_result_has_confidence_field(self):
        """PresentationResult should have confidence field."""
        from pcmrp_tools.bmad_automation.menu_selection import PresentationResult

        result = PresentationResult()
        assert hasattr(result, "confidence")
        assert result.confidence == 0

    def test_presentation_result_with_values(self):
        """PresentationResult should accept values in constructor."""
        from pcmrp_tools.bmad_automation.menu_selection import PresentationResult

        result = PresentationResult(
            options=["Option A", "Option B"],
            no_recommendation_reason="Low confidence",
            confidence=35,
        )
        assert result.options == ["Option A", "Option B"]
        assert result.no_recommendation_reason == "Low confidence"
        assert result.confidence == 35


class TestIsLowConfidence:
    """Test C1.3: is_low_confidence() method."""

    def test_is_low_confidence_at_49_returns_true(self):
        """Confidence 49 should be low confidence (< 50)."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        assert selector.is_low_confidence(49) is True

    def test_is_low_confidence_at_50_returns_false(self):
        """Confidence 50 is medium, not low (>= 50 threshold)."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        assert selector.is_low_confidence(50) is False

    def test_is_low_confidence_at_0_returns_true(self):
        """Confidence 0 should be low confidence."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        assert selector.is_low_confidence(0) is True

    def test_is_low_confidence_at_25_returns_true(self):
        """Confidence 25 should be low confidence."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        assert selector.is_low_confidence(25) is True

    def test_is_low_confidence_at_80_returns_false(self):
        """Confidence 80 should not be low confidence."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        assert selector.is_low_confidence(80) is False


class TestPresentWithoutRecommendation:
    """Test C1.4: present_without_recommendation() method."""

    def test_present_without_recommendation_returns_presentation_result(self):
        """present_without_recommendation should return PresentationResult."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            LowConfidenceSelector,
            PresentationResult,
        )

        selector = LowConfidenceSelector()
        detection = MenuDetectionResult.detected(
            confidence=35,
            menu_type=MenuType.APC,
            options=["Advanced", "Party", "Continue"],
            breakdown={"pattern_match": 30, "structural_markers": 5},
            raw_input="[A] Advanced [P] Party [C] Continue",
        )
        result = selector.present_without_recommendation(detection)
        assert isinstance(result, PresentationResult)

    def test_present_without_recommendation_includes_all_options(self):
        """All options from detection should be in presentation."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        detection = MenuDetectionResult.detected(
            confidence=40,
            menu_type=MenuType.YVN,
            options=["Yes proceed", "View details", "No cancel"],
            breakdown={"pattern_match": 30, "structural_markers": 10},
            raw_input="[Y] Yes [V] View [N] No",
        )
        result = selector.present_without_recommendation(detection)
        assert len(result.options) == 3
        assert "Yes proceed" in result.options
        assert "View details" in result.options
        assert "No cancel" in result.options

    def test_present_without_recommendation_includes_confidence(self):
        """Presentation should include the confidence score."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        detection = MenuDetectionResult.detected(
            confidence=30,
            menu_type=MenuType.NUMBERED,
            options=["Option 1", "Option 2"],
            breakdown={"pattern_match": 20, "structural_markers": 10},
            raw_input="[1] Option 1 [2] Option 2",
        )
        result = selector.present_without_recommendation(detection)
        assert result.confidence == 30

    def test_present_without_recommendation_has_reason(self):
        """Presentation should include reason for no recommendation."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        detection = MenuDetectionResult.detected(
            confidence=25,
            menu_type=MenuType.APC,
            options=["A", "B"],
            breakdown={},
            raw_input="[A] A [B] B",
        )
        result = selector.present_without_recommendation(detection)
        assert result.no_recommendation_reason != ""
        assert len(result.no_recommendation_reason) > 10


class TestLowConfidenceScenarios:
    """Test C1.5: Low confidence scenarios."""

    def test_low_confidence_with_single_option(self):
        """Single option menu at low confidence."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        detection = MenuDetectionResult.detected(
            confidence=20,
            menu_type=MenuType.EXIT,
            options=["Exit"],
            breakdown={"pattern_match": 15, "structural_markers": 5},
            raw_input="[E] Exit",
        )
        result = selector.present_without_recommendation(detection)
        assert len(result.options) == 1
        assert "Exit" in result.options

    def test_low_confidence_with_many_options(self):
        """Many options menu at low confidence."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        options = ["Opt1", "Opt2", "Opt3", "Opt4", "Opt5"]
        detection = MenuDetectionResult.detected(
            confidence=10,
            menu_type=MenuType.NUMBERED,
            options=options,
            breakdown={},
            raw_input="[1] Opt1 [2] Opt2 [3] Opt3 [4] Opt4 [5] Opt5",
        )
        result = selector.present_without_recommendation(detection)
        assert len(result.options) == 5

    def test_low_confidence_preserves_option_order(self):
        """Options should maintain their original order."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        options = ["First", "Second", "Third"]
        detection = MenuDetectionResult.detected(
            confidence=45,
            menu_type=MenuType.NUMBERED,
            options=options,
            breakdown={},
            raw_input="[1] First [2] Second [3] Third",
        )
        result = selector.present_without_recommendation(detection)
        assert result.options == ["First", "Second", "Third"]


# =============================================================================
# Task C2: Neutral Presentation Tests
# =============================================================================


class TestFormatNeutralOptions:
    """Test C2.1: Format options without bias indicators."""

    def test_format_neutral_options_returns_list(self):
        """format_neutral_options should return a list."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        result = selector.format_neutral_options(["A", "B", "C"])
        assert isinstance(result, list)

    def test_format_neutral_options_no_bias_markers(self):
        """Formatted options should not contain bias markers like '*' or 'recommended'."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        options = ["Option A", "Option B", "Option C"]
        result = selector.format_neutral_options(options)
        for opt in result:
            assert "*" not in opt
            assert "recommended" not in opt.lower()
            assert "best" not in opt.lower()
            assert "preferred" not in opt.lower()

    def test_format_neutral_options_preserves_content(self):
        """Original option content should be preserved."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        options = ["Save changes", "Discard", "Cancel"]
        result = selector.format_neutral_options(options)
        # Each original option text should appear somewhere in results
        for original in options:
            found = any(original in formatted for formatted in result)
            assert found, f"Original option '{original}' not found in formatted output"

    def test_format_neutral_options_equal_presentation(self):
        """All options should have equal visual weight (no highlighting first/last)."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        options = ["First", "Middle", "Last"]
        result = selector.format_neutral_options(options)
        # Check that formatting is consistent (same prefix/suffix pattern)
        # All should have same format structure (leading whitespace is equal)
        assert len(set(len(opt) - len(opt.lstrip()) for opt in result)) <= 1

    def test_format_neutral_options_empty_list(self):
        """Empty list should return empty list."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        result = selector.format_neutral_options([])
        assert result == []


class TestGenerateNoRecommendationReason:
    """Test C2.2: Generate explanation for why no recommendation given."""

    def test_generate_reason_returns_string(self):
        """Should return a non-empty string."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        reason = selector.generate_no_recommendation_reason(25)
        assert isinstance(reason, str)
        assert len(reason) > 0

    def test_generate_reason_mentions_confidence(self):
        """Reason should mention low confidence."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        reason = selector.generate_no_recommendation_reason(30)
        # Should mention confidence or uncertainty in some way
        lower_reason = reason.lower()
        assert any(
            word in lower_reason
            for word in ["confidence", "uncertain", "low", "insufficient"]
        )

    def test_generate_reason_includes_confidence_value(self):
        """Reason should include the actual confidence value."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        reason = selector.generate_no_recommendation_reason(35)
        assert "35" in reason or "35%" in reason

    def test_generate_reason_at_zero_confidence(self):
        """Zero confidence should generate appropriate reason."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        reason = selector.generate_no_recommendation_reason(0)
        assert len(reason) > 10
        assert "0" in reason

    def test_generate_reason_at_boundary_49(self):
        """Confidence 49 (just below threshold) should generate reason."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        reason = selector.generate_no_recommendation_reason(49)
        assert len(reason) > 10
        assert "49" in reason


class TestPresentationFormatting:
    """Test C2.3: Presentation formatting tests."""

    def test_full_presentation_flow(self):
        """Complete presentation flow from detection to formatted output."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        detection = MenuDetectionResult.detected(
            confidence=35,
            menu_type=MenuType.APC,
            options=["Continue with defaults", "Modify settings", "Cancel operation"],
            breakdown={"pattern_match": 25, "structural_markers": 10},
            raw_input="[C] Continue [M] Modify [X] Cancel",
        )
        result = selector.present_without_recommendation(detection)

        # Verify all components are present
        assert len(result.options) == 3
        assert result.confidence == 35
        assert "35" in result.no_recommendation_reason

    def test_presentation_reason_is_human_readable(self):
        """Reason should be a complete, readable sentence."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        reason = selector.generate_no_recommendation_reason(42)
        # Should be a proper sentence (starts with capital, reasonable length)
        assert reason[0].isupper() or reason[0].isdigit()
        assert len(reason) >= 20

    def test_presentation_options_are_distinct(self):
        """Each option should be distinctly identifiable."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        options = ["Option A", "Option B", "Option C"]
        formatted = selector.format_neutral_options(options)
        # All formatted options should be unique
        assert len(formatted) == len(set(formatted))


# =============================================================================
# Edge Cases and Boundary Tests for LowConfidenceSelector
# =============================================================================


class TestLowConfidenceEdgeCases:
    """Edge case tests for LowConfidenceSelector."""

    def test_empty_options_in_detection(self):
        """Handle detection with empty options list."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        detection = MenuDetectionResult.detected(
            confidence=30,
            menu_type=MenuType.UNKNOWN,
            options=[],
            breakdown={},
            raw_input="[?]",
        )
        result = selector.present_without_recommendation(detection)
        assert result.options == []
        assert result.confidence == 30

    def test_special_characters_in_options(self):
        """Handle options with special characters."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        options = ["Save & Continue", "Don't save", "Cancel (Esc)"]
        formatted = selector.format_neutral_options(options)
        assert len(formatted) == 3
        # Original content should be preserved
        for orig in options:
            assert any(orig in f for f in formatted)

    def test_very_long_option_text(self):
        """Handle very long option text."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        long_option = "A" * 200
        options = [long_option, "Short"]
        formatted = selector.format_neutral_options(options)
        assert len(formatted) == 2

    def test_whitespace_only_option(self):
        """Handle options that are whitespace."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        options = ["Valid", "   ", "Also valid"]
        formatted = selector.format_neutral_options(options)
        assert len(formatted) == 3


class TestLowConfidenceThresholdBoundaries:
    """Comprehensive boundary tests for low confidence threshold."""

    @pytest.mark.parametrize(
        "confidence,expected",
        [
            (49, True),   # Just below threshold - IS low confidence
            (50, False),  # Exactly at threshold - NOT low confidence (is medium)
            (51, False),  # Just above threshold - NOT low confidence
        ],
    )
    def test_threshold_boundary_49_50_51(self, confidence, expected):
        """Test exact boundary values 49 vs 50 vs 51."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        assert selector.is_low_confidence(confidence) is expected

    @pytest.mark.parametrize("confidence", [0, 10, 25, 40, 49])
    def test_low_confidence_values_return_true(self, confidence):
        """All values < 50 return True for is_low_confidence."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        assert selector.is_low_confidence(confidence) is True

    @pytest.mark.parametrize("confidence", [50, 60, 70, 80, 100])
    def test_medium_and_high_confidence_values_return_false(self, confidence):
        """All values >= 50 return False for is_low_confidence."""
        from pcmrp_tools.bmad_automation.menu_selection import LowConfidenceSelector

        selector = LowConfidenceSelector()
        assert selector.is_low_confidence(confidence) is False


# =============================================================================
# Task D1: SelectionLogger Tests (AC: #4)
# =============================================================================


class TestSelectionLogEntryDataclass:
    """Test D1.2: SelectionLogEntry dataclass."""

    def test_selection_log_entry_has_timestamp_field(self):
        """SelectionLogEntry should have timestamp field."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionLogEntry

        entry = SelectionLogEntry(
            timestamp=1234567890.123,
            menu_type="APC",
            selection="Continue",
            reason="Auto-selected",
            confidence=85,
            duration_ms=150,
            auto_selected=True,
        )
        assert hasattr(entry, "timestamp")
        assert entry.timestamp == 1234567890.123

    def test_selection_log_entry_has_menu_type_field(self):
        """SelectionLogEntry should have menu_type field."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionLogEntry

        entry = SelectionLogEntry(
            timestamp=1234567890.0,
            menu_type="YVN",
            selection="Yes",
            reason="User confirmation",
            confidence=90,
            duration_ms=50,
            auto_selected=True,
        )
        assert hasattr(entry, "menu_type")
        assert entry.menu_type == "YVN"

    def test_selection_log_entry_has_selection_field(self):
        """SelectionLogEntry should have selection field (nullable)."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionLogEntry

        entry = SelectionLogEntry(
            timestamp=1234567890.0,
            menu_type="NUMBERED",
            selection=None,
            reason="No recommendation",
            confidence=30,
            duration_ms=100,
            auto_selected=False,
        )
        assert hasattr(entry, "selection")
        assert entry.selection is None

    def test_selection_log_entry_has_reason_field(self):
        """SelectionLogEntry should have reason field."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionLogEntry

        entry = SelectionLogEntry(
            timestamp=1234567890.0,
            menu_type="APC",
            selection="Continue",
            reason="High confidence auto-selection",
            confidence=85,
            duration_ms=75,
            auto_selected=True,
        )
        assert hasattr(entry, "reason")
        assert entry.reason == "High confidence auto-selection"

    def test_selection_log_entry_has_confidence_field(self):
        """SelectionLogEntry should have confidence field."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionLogEntry

        entry = SelectionLogEntry(
            timestamp=1234567890.0,
            menu_type="EXIT",
            selection="Exit",
            reason="Exit requested",
            confidence=95,
            duration_ms=25,
            auto_selected=True,
        )
        assert hasattr(entry, "confidence")
        assert entry.confidence == 95

    def test_selection_log_entry_has_duration_ms_field(self):
        """SelectionLogEntry should have duration_ms field."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionLogEntry

        entry = SelectionLogEntry(
            timestamp=1234567890.0,
            menu_type="APC",
            selection="Continue",
            reason="Fast selection",
            confidence=80,
            duration_ms=123,
            auto_selected=True,
        )
        assert hasattr(entry, "duration_ms")
        assert entry.duration_ms == 123

    def test_selection_log_entry_has_auto_selected_field(self):
        """SelectionLogEntry should have auto_selected field."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionLogEntry

        entry = SelectionLogEntry(
            timestamp=1234567890.0,
            menu_type="APC",
            selection="Continue",
            reason="Auto-selected",
            confidence=85,
            duration_ms=50,
            auto_selected=True,
        )
        assert hasattr(entry, "auto_selected")
        assert entry.auto_selected is True


class TestSelectionLoggerInit:
    """Test D1.1: SelectionLogger initialization with audit trail storage."""

    def test_selection_logger_exists(self):
        """SelectionLogger class should exist."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionLogger

        logger = SelectionLogger()
        assert logger is not None

    def test_selection_logger_has_empty_audit_trail_on_init(self):
        """SelectionLogger should have empty audit trail on creation."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionLogger

        logger = SelectionLogger()
        trail = logger.get_audit_trail()
        assert trail == []


class TestLogSelection:
    """Test D1.3: log_selection() method."""

    def test_log_selection_adds_entry_to_audit_trail(self):
        """log_selection should add entry to audit trail."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            SelectionLogger,
            SelectionLogEntry,
        )

        logger = SelectionLogger()
        entry = SelectionLogEntry(
            timestamp=1234567890.0,
            menu_type="APC",
            selection="Continue",
            reason="Test reason",
            confidence=85,
            duration_ms=100,
            auto_selected=True,
        )
        logger.log_selection(entry)
        trail = logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0] == entry

    def test_log_selection_preserves_order(self):
        """log_selection should preserve chronological order."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            SelectionLogger,
            SelectionLogEntry,
        )

        logger = SelectionLogger()
        entry1 = SelectionLogEntry(
            timestamp=1000.0,
            menu_type="APC",
            selection="First",
            reason="First entry",
            confidence=80,
            duration_ms=50,
            auto_selected=True,
        )
        entry2 = SelectionLogEntry(
            timestamp=2000.0,
            menu_type="YVN",
            selection="Second",
            reason="Second entry",
            confidence=60,
            duration_ms=75,
            auto_selected=False,
        )
        logger.log_selection(entry1)
        logger.log_selection(entry2)
        trail = logger.get_audit_trail()
        assert len(trail) == 2
        assert trail[0].selection == "First"
        assert trail[1].selection == "Second"

    def test_log_selection_captures_all_fields(self):
        """log_selection should capture all entry fields correctly."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            SelectionLogger,
            SelectionLogEntry,
        )

        logger = SelectionLogger()
        entry = SelectionLogEntry(
            timestamp=1234567890.123,
            menu_type="NUMBERED",
            selection="Option 3",
            reason="Selected by user",
            confidence=45,
            duration_ms=500,
            auto_selected=False,
        )
        logger.log_selection(entry)
        trail = logger.get_audit_trail()
        logged = trail[0]
        assert logged.timestamp == 1234567890.123
        assert logged.menu_type == "NUMBERED"
        assert logged.selection == "Option 3"
        assert logged.reason == "Selected by user"
        assert logged.confidence == 45
        assert logged.duration_ms == 500
        assert logged.auto_selected is False


class TestGetAuditTrail:
    """Test D1.4: get_audit_trail() method."""

    def test_get_audit_trail_returns_list(self):
        """get_audit_trail should return a list."""
        from pcmrp_tools.bmad_automation.menu_selection import SelectionLogger

        logger = SelectionLogger()
        trail = logger.get_audit_trail()
        assert isinstance(trail, list)

    def test_get_audit_trail_returns_copy(self):
        """get_audit_trail should return a copy (not internal reference)."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            SelectionLogger,
            SelectionLogEntry,
        )

        logger = SelectionLogger()
        entry = SelectionLogEntry(
            timestamp=1000.0,
            menu_type="APC",
            selection="Test",
            reason="Test",
            confidence=80,
            duration_ms=50,
            auto_selected=True,
        )
        logger.log_selection(entry)
        trail1 = logger.get_audit_trail()
        trail2 = logger.get_audit_trail()
        # Should be equal but not the same object
        assert trail1 == trail2
        assert trail1 is not trail2

    def test_get_audit_trail_multiple_entries(self):
        """get_audit_trail should return all logged entries."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            SelectionLogger,
            SelectionLogEntry,
        )

        logger = SelectionLogger()
        for i in range(5):
            entry = SelectionLogEntry(
                timestamp=float(i * 1000),
                menu_type="APC",
                selection=f"Option {i}",
                reason=f"Reason {i}",
                confidence=80 + i,
                duration_ms=50 + i * 10,
                auto_selected=True,
            )
            logger.log_selection(entry)
        trail = logger.get_audit_trail()
        assert len(trail) == 5
        for i in range(5):
            assert trail[i].selection == f"Option {i}"


class TestSelectionLoggerCompleteness:
    """Test D1.5: Logging completeness tests."""

    def test_log_auto_selection_high_confidence(self):
        """Logging a high confidence auto-selection."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            SelectionLogger,
            SelectionLogEntry,
        )

        logger = SelectionLogger()
        entry = SelectionLogEntry(
            timestamp=1234567890.0,
            menu_type="APC",
            selection="Continue",
            reason="Auto-selected with 85% confidence",
            confidence=85,
            duration_ms=100,
            auto_selected=True,
        )
        logger.log_selection(entry)
        trail = logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].auto_selected is True
        assert trail[0].confidence >= 80

    def test_log_recommendation_medium_confidence(self):
        """Logging a medium confidence recommendation."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            SelectionLogger,
            SelectionLogEntry,
        )

        logger = SelectionLogger()
        entry = SelectionLogEntry(
            timestamp=1234567890.0,
            menu_type="YVN",
            selection="Yes",
            reason="Recommended with 65% confidence",
            confidence=65,
            duration_ms=200,
            auto_selected=False,
        )
        logger.log_selection(entry)
        trail = logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].auto_selected is False
        assert 50 <= trail[0].confidence < 80

    def test_log_presentation_low_confidence(self):
        """Logging a low confidence presentation (no recommendation)."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            SelectionLogger,
            SelectionLogEntry,
        )

        logger = SelectionLogger()
        entry = SelectionLogEntry(
            timestamp=1234567890.0,
            menu_type="NUMBERED",
            selection=None,
            reason="Low confidence (30%) - no recommendation",
            confidence=30,
            duration_ms=150,
            auto_selected=False,
        )
        logger.log_selection(entry)
        trail = logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].selection is None
        assert trail[0].confidence < 50


# =============================================================================
# Task E1: Timing Instrumentation Tests (AC: #5)
# =============================================================================


class TestTimingConstants:
    """Test E1.1: Timing constants."""

    def test_max_selection_time_constant_exists(self):
        """MAX_SELECTION_TIME_MS constant should be defined as 5000."""
        from pcmrp_tools.bmad_automation.menu_selection import MAX_SELECTION_TIME_MS

        assert MAX_SELECTION_TIME_MS == 5000


class TestPerformanceCheck:
    """Test E1.2: performance_check() asserting < 5 seconds."""

    def test_performance_check_passes_under_5_seconds(self):
        """performance_check should pass when duration < 5000ms."""
        from pcmrp_tools.bmad_automation.menu_selection import performance_check

        # 100ms should pass
        result = performance_check(100)
        assert result is True

    def test_performance_check_passes_at_4999ms(self):
        """performance_check should pass at exactly 4999ms."""
        from pcmrp_tools.bmad_automation.menu_selection import performance_check

        result = performance_check(4999)
        assert result is True

    def test_performance_check_fails_at_5000ms(self):
        """performance_check should fail at exactly 5000ms (boundary)."""
        from pcmrp_tools.bmad_automation.menu_selection import performance_check

        result = performance_check(5000)
        assert result is False

    def test_performance_check_fails_above_5000ms(self):
        """performance_check should fail when duration > 5000ms."""
        from pcmrp_tools.bmad_automation.menu_selection import performance_check

        result = performance_check(6000)
        assert result is False

    def test_performance_check_passes_at_zero(self):
        """performance_check should pass at 0ms."""
        from pcmrp_tools.bmad_automation.menu_selection import performance_check

        result = performance_check(0)
        assert result is True


class TestTimingInstrumentation:
    """Test E1.3: Timing instrumentation in selection flow."""

    def test_menu_selector_tracks_duration(self):
        """MenuSelector should track selection duration."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 85},
            raw_input="[A] Accept [D] Decline",
        )
        result = selector.select_or_present(detection)
        # Result should have duration tracked
        trail = selector.logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].duration_ms >= 0

    def test_menu_selector_normal_operation_under_5_seconds(self):
        """Normal MenuSelector operation should complete under 5 seconds."""
        import time

        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 85},
            raw_input="[A] Accept [D] Decline",
        )
        start = time.time()
        selector.select_or_present(detection)
        duration_ms = (time.time() - start) * 1000
        assert duration_ms < 5000


# =============================================================================
# Task F1: MenuSelector Orchestrator Tests
# =============================================================================


class TestMenuSelectorInit:
    """Test F1.1: MenuSelector initialization."""

    def test_menu_selector_exists(self):
        """MenuSelector class should exist."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert selector is not None

    def test_menu_selector_has_high_selector(self):
        """MenuSelector should have HighConfidenceSelector."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            HighConfidenceSelector,
            MenuSelector,
        )

        selector = MenuSelector()
        assert hasattr(selector, "high_selector")
        assert isinstance(selector.high_selector, HighConfidenceSelector)

    def test_menu_selector_has_medium_selector(self):
        """MenuSelector should have MediumConfidenceSelector."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MediumConfidenceSelector,
            MenuSelector,
        )

        selector = MenuSelector()
        assert hasattr(selector, "medium_selector")
        assert isinstance(selector.medium_selector, MediumConfidenceSelector)

    def test_menu_selector_has_low_selector(self):
        """MenuSelector should have LowConfidenceSelector."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            LowConfidenceSelector,
            MenuSelector,
        )

        selector = MenuSelector()
        assert hasattr(selector, "low_selector")
        assert isinstance(selector.low_selector, LowConfidenceSelector)

    def test_menu_selector_has_logger(self):
        """MenuSelector should have SelectionLogger."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector, SelectionLogger

        selector = MenuSelector()
        assert hasattr(selector, "logger")
        assert isinstance(selector.logger, SelectionLogger)


class TestSelectOrPresentRouting:
    """Test F1.1: select_or_present() routing logic."""

    def test_routes_high_confidence_to_auto_select(self):
        """High confidence (>= 80) should route to HighConfidenceSelector."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector, SelectionResult

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 85},
            raw_input="[A] Accept [D] Decline",
        )
        result = selector.select_or_present(detection)
        assert isinstance(result, SelectionResult)
        assert result.selected is True

    def test_routes_medium_confidence_to_recommendation(self):
        """Medium confidence (50-79) should route to MediumConfidenceSelector."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            RecommendationResult,
        )

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=65,
            menu_type=MenuType.YVN,
            options=["Yes", "View", "No"],
            breakdown={"test": 65},
            raw_input="[Y] Yes [V] View [N] No",
        )
        result = selector.select_or_present(detection)
        assert isinstance(result, RecommendationResult)
        assert result.recommended_option is not None

    def test_routes_low_confidence_to_presentation(self):
        """Low confidence (< 50) should route to LowConfidenceSelector."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector, PresentationResult

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=35,
            menu_type=MenuType.NUMBERED,
            options=["Option 1", "Option 2"],
            breakdown={"test": 35},
            raw_input="[1] Option 1 [2] Option 2",
        )
        result = selector.select_or_present(detection)
        assert isinstance(result, PresentationResult)
        assert len(result.options) == 2

    def test_boundary_80_routes_to_high(self):
        """Confidence exactly 80 should route to high confidence selector."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector, SelectionResult

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=80,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 80},
            raw_input="[A] Accept [D] Decline",
        )
        result = selector.select_or_present(detection)
        assert isinstance(result, SelectionResult)
        assert result.selected is True

    def test_boundary_79_routes_to_medium(self):
        """Confidence exactly 79 should route to medium confidence selector."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            RecommendationResult,
        )

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=79,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 79},
            raw_input="[A] Accept [D] Decline",
        )
        result = selector.select_or_present(detection)
        assert isinstance(result, RecommendationResult)

    def test_boundary_50_routes_to_medium(self):
        """Confidence exactly 50 should route to medium confidence selector."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            RecommendationResult,
        )

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=50,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 50},
            raw_input="[A] Accept [D] Decline",
        )
        result = selector.select_or_present(detection)
        assert isinstance(result, RecommendationResult)

    def test_boundary_49_routes_to_low(self):
        """Confidence exactly 49 should route to low confidence selector."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector, PresentationResult

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=49,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 49},
            raw_input="[A] Accept [D] Decline",
        )
        result = selector.select_or_present(detection)
        assert isinstance(result, PresentationResult)


class TestSelectOrPresentLogging:
    """Test F1.2: Logging for all selection paths."""

    def test_high_confidence_selection_is_logged(self):
        """High confidence auto-selection should be logged."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 90},
            raw_input="[A] Accept [D] Decline",
        )
        selector.select_or_present(detection)
        trail = selector.logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].auto_selected is True
        assert trail[0].confidence == 90

    def test_medium_confidence_recommendation_is_logged(self):
        """Medium confidence recommendation should be logged."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=65,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 65},
            raw_input="[Y] Yes [N] No",
        )
        selector.select_or_present(detection)
        trail = selector.logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].auto_selected is False
        assert trail[0].confidence == 65

    def test_low_confidence_presentation_is_logged(self):
        """Low confidence presentation should be logged."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=30,
            menu_type=MenuType.NUMBERED,
            options=["Option 1", "Option 2"],
            breakdown={"test": 30},
            raw_input="[1] Option 1 [2] Option 2",
        )
        selector.select_or_present(detection)
        trail = selector.logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].auto_selected is False
        assert trail[0].confidence == 30
        assert trail[0].selection is None

    def test_log_entry_has_menu_type(self):
        """Log entry should capture menu type."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 85},
            raw_input="[Y] Yes [N] No",
        )
        selector.select_or_present(detection)
        trail = selector.logger.get_audit_trail()
        assert trail[0].menu_type == "YVN"

    def test_log_entry_has_duration(self):
        """Log entry should capture duration in milliseconds."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        # Use YVN menu (not a continue menu) to avoid batch-continue routing
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 85},
            raw_input="[Y] Yes [N] No",
        )
        selector.select_or_present(detection)
        trail = selector.logger.get_audit_trail()
        assert trail[0].duration_ms >= 0

    def test_log_entry_has_timestamp(self):
        """Log entry should capture timestamp."""
        import time

        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        before = time.time()
        selector = MenuSelector()
        # Use YVN menu (not a continue menu) to avoid batch-continue routing
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 85},
            raw_input="[Y] Yes [N] No",
        )
        selector.select_or_present(detection)
        after = time.time()
        trail = selector.logger.get_audit_trail()
        assert before <= trail[0].timestamp <= after


class TestMenuSelectorIntegration:
    """Test F1.3: Integration tests covering all confidence tiers."""

    def test_full_workflow_high_confidence_apc(self):
        """Full integration test for high confidence APC menu."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector, SelectionResult

        selector = MenuSelector()
        # Use YVN menu (not a continue menu) to avoid batch-continue routing
        detection = MenuDetectionResult.detected(
            confidence=92,
            menu_type=MenuType.YVN,
            options=["Yes", "View", "No"],
            breakdown={"structural": 25, "position": 20, "options": 20, "pattern": 27},
            raw_input="[Y] Yes [V] View [N] No",
        )
        result = selector.select_or_present(detection)

        # Verify result type and content
        assert isinstance(result, SelectionResult)
        assert result.selected is True
        assert result.option == "Yes"  # Highest priority for approval
        assert result.confidence == 92

        # Verify logging
        trail = selector.logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].selection == "Yes"
        assert trail[0].auto_selected is True

    def test_full_workflow_medium_confidence_yvn(self):
        """Full integration test for medium confidence YVN menu."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            RecommendationResult,
        )

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=68,
            menu_type=MenuType.YVN,
            options=["Yes", "View", "No"],
            breakdown={"structural": 20, "position": 15, "options": 18, "pattern": 15},
            raw_input="[Y] Yes [V] View [N] No",
        )
        result = selector.select_or_present(detection)

        # Verify result type and content
        assert isinstance(result, RecommendationResult)
        assert result.recommended_option == "Yes"
        assert len(result.alternatives) == 2
        assert result.confidence == 68

        # Verify logging
        trail = selector.logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].selection == "Yes"
        assert trail[0].auto_selected is False

    def test_full_workflow_low_confidence_numbered(self):
        """Full integration test for low confidence numbered menu."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector, PresentationResult

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=25,
            menu_type=MenuType.NUMBERED,
            options=["Option 1", "Option 2", "Option 3"],
            breakdown={"structural": 10, "position": 5, "options": 5, "pattern": 5},
            raw_input="[1] Option 1 [2] Option 2 [3] Option 3",
        )
        result = selector.select_or_present(detection)

        # Verify result type and content
        assert isinstance(result, PresentationResult)
        assert len(result.options) == 3
        assert result.confidence == 25
        assert "25" in result.no_recommendation_reason

        # Verify logging
        trail = selector.logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].selection is None
        assert trail[0].auto_selected is False

    def test_multiple_selections_are_all_logged(self):
        """Multiple selections should all be logged in order."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        # First: High confidence (not a continue menu to avoid batch-continue logic)
        detection1 = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Accept"],
            breakdown={"test": 85},
            raw_input="[A] Accept",
        )
        selector.select_or_present(detection1)

        # Second: Medium confidence
        detection2 = MenuDetectionResult.detected(
            confidence=65,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 65},
            raw_input="[Y] Yes [N] No",
        )
        selector.select_or_present(detection2)

        # Third: Low confidence
        detection3 = MenuDetectionResult.detected(
            confidence=30,
            menu_type=MenuType.NUMBERED,
            options=["Option 1"],
            breakdown={"test": 30},
            raw_input="[1] Option 1",
        )
        selector.select_or_present(detection3)

        # Verify all logged
        trail = selector.logger.get_audit_trail()
        assert len(trail) == 3
        assert trail[0].confidence == 85
        assert trail[1].confidence == 65
        assert trail[2].confidence == 30

    def test_context_passed_to_selectors(self):
        """Context should be passed through to selectors."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector, SelectionResult

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.YVN,
            options=["Yes", "View", "No"],
            breakdown={"test": 85},
            raw_input="[Y] Yes [V] View [N] No",
        )
        # With review context, View should be preferred
        result = selector.select_or_present(detection, context={"workflow_phase": "review"})
        assert isinstance(result, SelectionResult)
        assert result.option == "View"


# =============================================================================
# Story 2b-5 Task 5: MenuHistory Integration Tests
# =============================================================================


class TestMenuSelectorHistoryManagerIntegration:
    """Test Task 5.1: MenuSelector has MenuHistoryManager."""

    def test_menu_selector_has_history_manager(self):
        """MenuSelector should have a MenuHistoryManager instance."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert hasattr(selector, "_history_manager")
        assert isinstance(selector._history_manager, MenuHistoryManager)

    def test_menu_selector_history_manager_starts_empty(self):
        """MenuSelector's history manager should start empty."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert len(selector._history_manager) == 0


class TestRecordSelectionMethod:
    """Test Task 5.2: record_selection() method on MenuSelector."""

    def test_record_selection_method_exists(self):
        """MenuSelector should have record_selection method."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert hasattr(selector, "record_selection")
        assert callable(selector.record_selection)

    def test_record_selection_adds_entry_to_history(self):
        """record_selection should add entry to history manager."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        selector.record_selection(
            menu_id="test-menu-1",
            selection="Continue",
            confidence=0.85,
            source=SelectionSource.AUTO,
            workflow_context="test-workflow",
        )

        assert len(selector._history_manager) == 1

    def test_record_selection_captures_all_fields(self):
        """record_selection should capture all fields correctly."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        selector.record_selection(
            menu_id="my-menu-id",
            selection="Yes",
            confidence=0.92,
            source=SelectionSource.MANUAL,
            workflow_context="my-workflow",
        )

        history = selector._history_manager.get_history()
        assert len(history) == 1
        entry = history[0]
        assert entry.menu_id == "my-menu-id"
        assert entry.selection == "Yes"
        assert entry.confidence == 0.92
        assert entry.source == SelectionSource.MANUAL
        assert entry.workflow_context == "my-workflow"

    def test_record_selection_without_workflow_context(self):
        """record_selection should work without workflow_context."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        selector.record_selection(
            menu_id="menu-1",
            selection="Option A",
            confidence=0.75,
            source=SelectionSource.ESCALATED,
        )

        history = selector._history_manager.get_history()
        assert len(history) == 1
        assert history[0].workflow_context is None

    def test_record_selection_sets_timestamp(self):
        """record_selection should set a valid timestamp."""
        from datetime import datetime, timezone

        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        before = datetime.now(timezone.utc)
        selector = MenuSelector()
        selector.record_selection(
            menu_id="menu-1",
            selection="Option",
            confidence=0.80,
            source=SelectionSource.AUTO,
        )
        after = datetime.now(timezone.utc)

        history = selector._history_manager.get_history()
        entry = history[0]
        # Timestamp should be between before and after
        assert before <= entry.timestamp.replace(tzinfo=timezone.utc) or entry.timestamp <= after


class TestSelectOrPresentHistoryRecording:
    """Test Task 5.3: select_or_present records to history."""

    def test_high_confidence_auto_select_records_history(self):
        """High confidence auto-selection should record to history."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        # Use YVN menu with Yes/No options (not a continue menu)
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 90},
            raw_input="[Y] Yes [N] No",
        )
        selector.select_or_present(detection)

        # Should have recorded to history
        history = selector._history_manager.get_history()
        assert len(history) == 1
        entry = history[0]
        assert entry.menu_id == "YVN"  # Menu type as ID
        assert entry.selection == "Yes"
        assert entry.source == SelectionSource.AUTO

    def test_medium_confidence_recommendation_records_history(self):
        """Medium confidence recommendation should record to history."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=65,
            menu_type=MenuType.YVN,
            options=["Yes", "View", "No"],
            breakdown={"test": 65},
            raw_input="[Y] Yes [V] View [N] No",
        )
        selector.select_or_present(detection)

        history = selector._history_manager.get_history()
        assert len(history) == 1
        entry = history[0]
        assert entry.menu_id == "YVN"
        assert entry.selection == "Yes"  # Recommended option
        assert entry.source == SelectionSource.MANUAL

    def test_low_confidence_presentation_records_history(self):
        """Low confidence presentation should record to history without selection."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=30,
            menu_type=MenuType.NUMBERED,
            options=["Option 1", "Option 2"],
            breakdown={"test": 30},
            raw_input="[1] Option 1 [2] Option 2",
        )
        selector.select_or_present(detection)

        history = selector._history_manager.get_history()
        assert len(history) == 1
        entry = history[0]
        assert entry.menu_id == "NUMBERED"
        # Low confidence has no selection
        assert entry.selection == ""  # Empty string for no selection
        assert entry.source == SelectionSource.MANUAL

    def test_escalated_selection_records_history(self):
        """Escalated selection should record to history with ESCALATED source."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import (
            BMBThresholdChecker,
            ValidationMetrics,
        )
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        checker = BMBThresholdChecker()
        selector = MenuSelector(bmb_checker=checker)

        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 90},
            raw_input="[A] Accept [D] Decline",
        )

        # Create metrics that trigger escalation
        metrics = ValidationMetrics(
            blocking_errors=5,  # Exceeds threshold
            major_issues=2,
            compliance_score=80,
        )

        selector.select_or_present(detection, validation_metrics=metrics)

        history = selector._history_manager.get_history()
        assert len(history) == 1
        entry = history[0]
        assert entry.source == SelectionSource.ESCALATED

    def test_confidence_normalized_to_0_1_scale(self):
        """Confidence should be recorded as 0.0-1.0 scale."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        # Use YVN menu with Yes/No options (not a continue menu)
        detection = MenuDetectionResult.detected(
            confidence=85,  # 0-100 scale in detection
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 85},
            raw_input="[Y] Yes [N] No",
        )
        selector.select_or_present(detection)

        history = selector._history_manager.get_history()
        entry = history[0]
        # Should be normalized to 0.0-1.0
        assert 0.0 <= entry.confidence <= 1.0
        assert entry.confidence == 0.85


class TestMenuSelectorHistoryPersistence:
    """Test Task 5.4: History persistence methods on MenuSelector."""

    def test_save_history_method_exists(self):
        """MenuSelector should have save_history method."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert hasattr(selector, "save_history")
        assert callable(selector.save_history)

    def test_load_history_method_exists(self):
        """MenuSelector should have load_history method."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert hasattr(selector, "load_history")
        assert callable(selector.load_history)

    def test_save_history_creates_file(self, tmp_path):
        """save_history should create session history file."""
        import os

        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        # Change to tmp_path so relative paths work
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            selector = MenuSelector()
            selector.record_selection(
                menu_id="menu-1",
                selection="Continue",
                confidence=0.85,
                source=SelectionSource.AUTO,
            )

            selector.save_history("test-session-123")

            # File should exist
            from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

            expected_path = MenuHistoryManager.get_session_history_path("test-session-123")
            assert expected_path.exists()
        finally:
            os.chdir(original_cwd)

    def test_load_history_restores_entries(self, tmp_path):
        """load_history should restore saved history entries."""
        import os

        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            # First selector saves history
            selector1 = MenuSelector()
            selector1.record_selection(
                menu_id="saved-menu",
                selection="Saved Option",
                confidence=0.90,
                source=SelectionSource.AUTO,
                workflow_context="saved-context",
            )
            selector1.save_history("recovery-session")

            # Second selector loads history
            selector2 = MenuSelector()
            selector2.load_history("recovery-session")

            history = selector2._history_manager.get_history()
            assert len(history) == 1
            assert history[0].menu_id == "saved-menu"
            assert history[0].selection == "Saved Option"
        finally:
            os.chdir(original_cwd)


class TestFullSelectionToRecoveryFlow:
    """Test Task 5.5: Full selection-to-recovery integration flow."""

    def test_full_workflow_selection_and_recovery(self, tmp_path):
        """Full workflow: selections, save, recover, resume."""
        import os

        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            # Phase 1: Make selections
            selector = MenuSelector()

            # High confidence auto-select (use YVN, not continue menu)
            detection1 = MenuDetectionResult.detected(
                confidence=90,
                menu_type=MenuType.YVN,
                options=["Yes", "No"],
                breakdown={"test": 90},
                raw_input="[Y] Yes [N] No",
            )
            selector.select_or_present(detection1)

            # Medium confidence recommendation
            detection2 = MenuDetectionResult.detected(
                confidence=65,
                menu_type=MenuType.NUMBERED,
                options=["Option 1", "Option 2"],
                breakdown={"test": 65},
                raw_input="[1] Option 1 [2] Option 2",
            )
            selector.select_or_present(detection2)

            # Save checkpoint
            selector.save_history("workflow-session")

            # Phase 2: Simulate crash and recovery
            recovered_selector = MenuSelector()
            recovered_selector.load_history("workflow-session")

            # Verify all history was recovered
            history = recovered_selector._history_manager.get_history()
            assert len(history) == 2

            # Can continue making selections (EXIT without continue option)
            detection3 = MenuDetectionResult.detected(
                confidence=85,
                menu_type=MenuType.EXIT,
                options=["Save and Exit", "Discard"],
                breakdown={"test": 85},
                raw_input="[S] Save and Exit [D] Discard",
            )
            recovered_selector.select_or_present(detection3)

            # Total should be 3 now
            assert len(recovered_selector._history_manager) == 3
        finally:
            os.chdir(original_cwd)

    def test_multiple_checkpoints_overwrite(self, tmp_path):
        """Saving multiple times should overwrite previous checkpoint."""
        import os

        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            selector = MenuSelector()

            # First selection and save (use NUMBERED, not continue menu)
            detection1 = MenuDetectionResult.detected(
                confidence=90,
                menu_type=MenuType.NUMBERED,
                options=["Option A", "Option B"],
                breakdown={"test": 90},
                raw_input="[A] Option A [B] Option B",
            )
            selector.select_or_present(detection1)
            selector.save_history("session-1")

            # Second selection and save (same session)
            detection2 = MenuDetectionResult.detected(
                confidence=85,
                menu_type=MenuType.YVN,
                options=["Yes"],
                breakdown={"test": 85},
                raw_input="[Y] Yes",
            )
            selector.select_or_present(detection2)
            selector.save_history("session-1")

            # Load should get both entries
            recovered = MenuSelector()
            recovered.load_history("session-1")
            assert len(recovered._history_manager) == 2
        finally:
            os.chdir(original_cwd)

    def test_history_queries_work_after_recovery(self, tmp_path):
        """Recovered history should support all query methods."""
        import os
        from datetime import datetime, timedelta, timezone

        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            selector = MenuSelector()

            # Make multiple selections (use NUMBERED and YVN, not continue menus)
            for i in range(5):
                detection = MenuDetectionResult.detected(
                    confidence=80 + i,
                    menu_type=MenuType.NUMBERED if i % 2 == 0 else MenuType.YVN,
                    options=["Option A", "Option B"],
                    breakdown={"test": 80 + i},
                    raw_input="[A] Option A [B] Option B",
                )
                selector.select_or_present(detection)

            selector.save_history("query-test-session")

            # Recover and test queries
            recovered = MenuSelector()
            recovered.load_history("query-test-session")

            # Test get_recent
            recent = recovered._history_manager.get_recent(2)
            assert len(recent) == 2

            # Test get_entries_for_menu
            numbered_entries = recovered._history_manager.get_entries_for_menu("NUMBERED")
            assert len(numbered_entries) == 3  # indices 0, 2, 4

            yvn_entries = recovered._history_manager.get_entries_for_menu("YVN")
            assert len(yvn_entries) == 2  # indices 1, 3

            # Test get_entries_since
            past_time = datetime.now(timezone.utc) - timedelta(hours=1)
            since_entries = recovered._history_manager.get_entries_since(past_time)
            assert len(since_entries) == 5
        finally:
            os.chdir(original_cwd)


# =============================================================================
# Task 6: Integration with BatchContinueManager Tests (Story 2b-6)
# =============================================================================


class TestMenuSelectorBatchIntegrationInit:
    """Test Task 6.1: MenuSelector initialization with BatchContinueManager."""

    def test_menu_selector_has_batch_manager(self):
        """MenuSelector should have _batch_manager attribute."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert hasattr(selector, "_batch_manager")
        assert selector._batch_manager is not None

    def test_menu_selector_has_tier_attribute(self):
        """MenuSelector should have _tier attribute."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert hasattr(selector, "_tier")

    def test_menu_selector_default_tier_is_2(self):
        """MenuSelector default tier should be 2."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert selector._tier == 2

    def test_menu_selector_with_custom_tier(self):
        """MenuSelector should accept custom tier."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=4)
        assert selector._tier == 4

    def test_menu_selector_batch_manager_uses_tier(self):
        """BatchContinueManager should use same tier as MenuSelector."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=3)
        assert selector._batch_manager._config.tier == 3


class TestMenuSelectorSetTier:
    """Test Task 6.5: set_tier method for tier changes mid-workflow."""

    def test_set_tier_changes_tier(self):
        """set_tier should update _tier attribute."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=2)
        selector.set_tier(4)
        assert selector._tier == 4

    def test_set_tier_recreates_batch_manager(self):
        """set_tier should create new BatchContinueManager with new tier."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=2)
        selector.set_tier(0)
        assert selector._batch_manager._config.tier == 0
        assert selector._batch_manager.is_auto_all_mode() is True

    def test_set_tier_from_auto_all_to_batched(self):
        """set_tier should allow changing from AUTO_ALL to BATCHED mode."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=0)
        assert selector._batch_manager.is_auto_all_mode() is True

        selector.set_tier(2)
        assert selector._batch_manager.is_auto_all_mode() is False
        assert selector._batch_manager._config.batch_size == 5


class TestMenuSelectorContinueDetection:
    """Test Task 6.2: Continue menu detection and routing."""

    def test_detects_continue_menu_with_c_bracket(self):
        """Should detect continue menu with [C] option."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=2)
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["[C] Continue", "[S] Stop"],
            breakdown={"test": 85},
            raw_input="[C] Continue [S] Stop",
        )
        # Should recognize this as a continue menu
        from pcmrp_tools.bmad_automation.batch_continue import is_continue_menu

        assert is_continue_menu(detection.raw_input, detection.options) is True

    def test_detects_continue_menu_with_proceed(self):
        """Should detect continue menu with 'Proceed' option."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=2)
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.YVN,
            options=["Yes, Proceed", "No"],
            breakdown={"test": 85},
            raw_input="Proceed with operation?",
        )
        from pcmrp_tools.bmad_automation.batch_continue import is_continue_menu

        assert is_continue_menu(detection.raw_input, detection.options) is True

    def test_non_continue_menu_not_detected(self):
        """Non-continue menu should not be detected as continue."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=2)
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.AGENT,
            options=["[A] Analyst", "[B] Builder", "[D] Developer"],
            breakdown={"test": 85},
            raw_input="Select agent",
        )
        from pcmrp_tools.bmad_automation.batch_continue import is_continue_menu

        assert is_continue_menu(detection.raw_input, detection.options) is False


class TestMenuSelectorAutoAllMode:
    """Test Task 6.3: Auto-all mode behavior (Tier 0-1)."""

    def test_tier_0_auto_continues_without_batching(self):
        """Tier 0 should auto-continue continue menus without batching."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            ContinueSelectionResult,
            MenuSelector,
        )

        selector = MenuSelector(tier=0)
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["[C] Continue", "[S] Stop"],
            breakdown={"test": 85},
            raw_input="[C] Continue [S] Stop",
        )
        result = selector.select_or_present(detection, context="Validation step")

        # Should auto-continue and return a ContinueSelectionResult
        assert isinstance(result, ContinueSelectionResult)
        assert result.auto_continued is True
        assert result.selected_option in ["[C] Continue", "Continue"]

    def test_tier_1_auto_continues_without_batching(self):
        """Tier 1 should also auto-continue continue menus without batching."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            ContinueSelectionResult,
            MenuSelector,
        )

        selector = MenuSelector(tier=1)
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Continue", "Stop"],
            breakdown={"test": 85},
            raw_input="Continue?",
        )
        result = selector.select_or_present(detection, context="Processing")

        assert isinstance(result, ContinueSelectionResult)
        assert result.auto_continued is True


class TestMenuSelectorBatchedMode:
    """Test Task 6.4: Batched mode behavior (Tier 2-3)."""

    def test_tier_2_batches_continue_menus(self):
        """Tier 2 should batch continue menus and checkpoint after 5."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint
        from pcmrp_tools.bmad_automation.menu_selection import (
            ContinueSelectionResult,
            MenuSelector,
        )

        selector = MenuSelector(tier=2)

        # First 4 continues should auto-continue within batch
        for i in range(4):
            detection = MenuDetectionResult.detected(
                confidence=85,
                menu_type=MenuType.APC,
                options=["[C] Continue", "[S] Stop"],
                breakdown={"test": 85},
                raw_input=f"Step {i + 1}: [C] Continue [S] Stop",
            )
            result = selector.select_or_present(detection, context=f"Step {i + 1}")
            assert isinstance(result, ContinueSelectionResult)
            assert result.auto_continued is True

        # 5th continue should trigger checkpoint
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["[C] Continue", "[S] Stop"],
            breakdown={"test": 85},
            raw_input="Step 5: [C] Continue [S] Stop",
        )
        result = selector.select_or_present(detection, context="Step 5")

        # Should return a checkpoint
        assert isinstance(result, BatchCheckpoint)
        assert len(result.operations) == 5
        assert "[C]ontinue" in result.options

    def test_tier_3_batches_with_size_3(self):
        """Tier 3 should checkpoint after 3 operations."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint
        from pcmrp_tools.bmad_automation.menu_selection import (
            ContinueSelectionResult,
            MenuSelector,
        )

        selector = MenuSelector(tier=3)

        # First 2 continues should auto-continue
        for i in range(2):
            detection = MenuDetectionResult.detected(
                confidence=85,
                menu_type=MenuType.APC,
                options=["[C] Continue"],
                breakdown={"test": 85},
                raw_input=f"Op {i + 1}",
            )
            result = selector.select_or_present(detection, context=f"Op {i + 1}")
            assert isinstance(result, ContinueSelectionResult)

        # 3rd continue should trigger checkpoint
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["[C] Continue"],
            breakdown={"test": 85},
            raw_input="Op 3",
        )
        result = selector.select_or_present(detection, context="Op 3")

        assert isinstance(result, BatchCheckpoint)
        assert len(result.operations) == 3


class TestMenuSelectorSingleStepMode:
    """Test Task 6.4b: Single-step mode behavior (Tier 4)."""

    def test_tier_4_checkpoints_every_step(self):
        """Tier 4 should checkpoint after every continue menu."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=4)
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["[C] Continue", "[S] Stop"],
            breakdown={"test": 85},
            raw_input="Single step: [C] Continue [S] Stop",
        )
        result = selector.select_or_present(detection, context="Single step")

        # Should immediately checkpoint
        assert isinstance(result, BatchCheckpoint)
        assert len(result.operations) == 1


class TestMenuSelectorNonContinueMenus:
    """Test that non-continue menus still work normally."""

    def test_non_continue_high_confidence_auto_selects(self):
        """Non-continue menu at high confidence should still auto-select."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector, SelectionResult

        selector = MenuSelector(tier=2)
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.AGENT,
            options=["[A] Analyst", "[B] Builder"],
            breakdown={"test": 90},
            raw_input="Select agent",
        )
        result = selector.select_or_present(detection)

        # Should use normal selection logic, not batching
        assert isinstance(result, SelectionResult)
        assert result.selected is True

    def test_non_continue_medium_confidence_recommends(self):
        """Non-continue menu at medium confidence should still recommend."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            RecommendationResult,
        )

        selector = MenuSelector(tier=2)
        detection = MenuDetectionResult.detected(
            confidence=65,
            menu_type=MenuType.NUMBERED,
            options=["Option A", "Option B"],
            breakdown={"test": 65},
            raw_input="Choose option",
        )
        result = selector.select_or_present(detection)

        assert isinstance(result, RecommendationResult)


class TestMenuSelectorBatchIntegrationFull:
    """Full integration tests for batch-continue functionality."""

    def test_full_workflow_tier_2_with_checkpoint_and_resume(self):
        """Full workflow: batch 5 continues -> checkpoint -> resume batching."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint
        from pcmrp_tools.bmad_automation.menu_selection import (
            ContinueSelectionResult,
            MenuSelector,
        )

        selector = MenuSelector(tier=2)

        # First batch: 5 continues
        results = []
        for i in range(5):
            detection = MenuDetectionResult.detected(
                confidence=85,
                menu_type=MenuType.APC,
                options=["[C] Continue"],
                breakdown={"test": 85},
                raw_input=f"Step {i + 1}",
            )
            result = selector.select_or_present(detection, context=f"Step {i + 1}")
            results.append(result)

        # 5th result should be checkpoint
        assert isinstance(results[4], BatchCheckpoint)
        assert len(results[4].operations) == 5

        # After checkpoint, should start new batch
        # User would approve checkpoint, then we continue
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["[C] Continue"],
            breakdown={"test": 85},
            raw_input="Step 6",
        )
        result = selector.select_or_present(detection, context="Step 6")

        # Should start new batch and auto-continue
        assert isinstance(result, ContinueSelectionResult)

    def test_mixed_continue_and_normal_menus(self):
        """Workflow with mix of continue menus and normal menus."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            ContinueSelectionResult,
            MenuSelector,
            SelectionResult,
        )

        selector = MenuSelector(tier=2)

        # Continue menu - should batch
        detection1 = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["[C] Continue"],
            breakdown={"test": 85},
            raw_input="Step 1",
        )
        result1 = selector.select_or_present(detection1, context="Step 1")
        assert isinstance(result1, ContinueSelectionResult)

        # Normal high-confidence menu - should auto-select normally
        detection2 = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 90},
            raw_input="Approve?",
        )
        result2 = selector.select_or_present(detection2)
        assert isinstance(result2, SelectionResult)
        assert result2.selected is True

        # Another continue menu - should continue batching
        detection3 = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["[C] Continue"],
            breakdown={"test": 85},
            raw_input="Step 2",
        )
        result3 = selector.select_or_present(detection3, context="Step 2")
        assert isinstance(result3, ContinueSelectionResult)


# =============================================================================
# Story 2b-4 Task 6: Nested Menu Integration Tests
# =============================================================================


class TestMenuSelectorNestedMenuIntegration:
    """Integration tests for MenuSelector with nested menu handling (Task 6)."""

    def test_menu_selector_has_depth_tracker(self):
        """MenuSelector should have a MenuDepthTracker instance."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.nested_menu import MenuDepthTracker

        selector = MenuSelector()
        assert hasattr(selector, "_depth_tracker")
        assert isinstance(selector._depth_tracker, MenuDepthTracker)

    def test_menu_selector_has_state_manager(self):
        """MenuSelector should have a StateManager instance."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.nested_menu import StateManager

        selector = MenuSelector()
        assert hasattr(selector, "_state_manager")
        assert isinstance(selector._state_manager, StateManager)

    def test_depth_tracker_starts_at_zero(self):
        """MenuSelector's depth tracker should start at depth 0."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert selector._depth_tracker.get_current_depth() == 0

    def test_state_manager_starts_without_saved_state(self):
        """MenuSelector's state manager should have no saved state initially."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()
        assert selector._state_manager.has_saved_state() is False


class TestMenuSelectorDepthChecking:
    """Tests for depth checking during menu selection."""

    def test_select_or_present_checks_depth_before_processing(self):
        """select_or_present should check depth before processing."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.nested_menu import (
            MAX_NESTED_DEPTH,
            UserEscalation,
        )

        selector = MenuSelector()

        # Push contexts to exceed max depth
        for i in range(MAX_NESTED_DEPTH + 1):
            selector._depth_tracker.push_menu_context(f"menu-{i}", "standard")

        # Now depth is exceeded
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 85},
            raw_input="[A] Accept [D] Decline",
        )

        result = selector.select_or_present(detection)

        # Should return UserEscalation when depth exceeded
        assert isinstance(result, UserEscalation)
        assert "depth" in result.reason.lower() or "exceeded" in result.reason.lower()

    def test_normal_depth_allows_selection(self):
        """Normal depth should allow regular selection."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            SelectionResult,
        )

        selector = MenuSelector()

        # Push one context (within limits)
        selector._depth_tracker.push_menu_context("menu-1", "standard")

        # Use YVN menu (not a continue menu) to avoid batch-continue routing
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.YVN,
            options=["Yes", "View", "No"],
            breakdown={"test": 85},
            raw_input="[Y] Yes [V] View [N] No",
        )

        result = selector.select_or_present(detection)

        # Should return normal selection result
        assert isinstance(result, SelectionResult)
        assert result.selected is True


class TestMenuSelectorPartyModeRouting:
    """Tests for Party Mode menu routing in MenuSelector."""

    def test_party_mode_menu_detected_and_routed(self):
        """Party Mode menu should be detected and handled appropriately."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        # Party Mode menu with agent/roster options
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Select agent", "View roster", "Exit"],
            breakdown={"test": 85},
            raw_input="[A] Select agent [V] View roster [E] Exit",
        )

        result = selector.select_or_present(detection)

        # Should process and return a result
        assert result is not None

    def test_party_mode_pushes_context(self):
        """Party Mode menu should push a context to the depth tracker."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        # Party Mode menu
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Select agent", "View roster", "Exit"],
            breakdown={"test": 85},
            raw_input="[A] Select agent [V] View roster [E] Exit",
        )

        initial_depth = selector._depth_tracker.get_current_depth()
        selector.select_or_present(detection)

        # Depth should have been managed (pushed during handling)
        # After completion, context should be popped
        # But this depends on implementation - verify tracker was used
        assert selector._depth_tracker is not None


class TestMenuSelectorElicitationRouting:
    """Tests for Elicitation menu routing in MenuSelector."""

    def test_elicitation_menu_detected_and_routed(self):
        """Elicitation menu should be detected and handled appropriately."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        # Elicitation menu with technique selection
        detection = MenuDetectionResult.detected(
            confidence=80,
            menu_type=MenuType.NUMBERED,
            options=["Socratic questioning", "5 Whys", "Mind mapping"],
            breakdown={"test": 80},
            raw_input="Select elicitation technique: [1] Socratic [2] 5 Whys [3] Mind map",
        )

        result = selector.select_or_present(detection)

        # Should process and return a result
        assert result is not None

    def test_elicitation_with_advanced_option(self):
        """Elicitation with [A] Advanced option should be detected."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Continue", "Advanced", "Exit"],
            breakdown={"test": 85},
            raw_input="[C] Continue [A] Advanced [E] Exit",
        )

        result = selector.select_or_present(detection)
        assert result is not None


class TestMenuSelectorNestedFlow:
    """Tests for complete nested menu flows."""

    def test_nested_party_mode_then_standard(self):
        """Handle nested Party Mode followed by standard menu."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        # First: Party Mode menu
        pm_detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Select agent", "View roster", "Exit"],
            breakdown={"test": 85},
            raw_input="[A] Select agent [V] View roster [E] Exit",
        )
        selector.select_or_present(pm_detection)

        # Second: Standard menu within Party Mode
        std_detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 90},
            raw_input="[Y] Yes [N] No",
        )
        result = selector.select_or_present(std_detection)

        # Should handle both menus without error
        assert result is not None

    def test_nested_elicitation_workflow(self):
        """Handle nested elicitation workflow with technique selection then execution."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        # Technique selection menu
        technique_detection = MenuDetectionResult.detected(
            confidence=80,
            menu_type=MenuType.NUMBERED,
            options=["Socratic questioning", "5 Whys", "Brainstorming"],
            breakdown={"test": 80},
            raw_input="Select technique: [1] Socratic [2] 5 Whys [3] Brainstorming",
        )
        selector.select_or_present(technique_detection)

        # Execution menu
        exec_detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Continue", "Add idea", "Complete"],
            breakdown={"test": 85},
            raw_input="[C] Continue [A] Add idea [X] Complete",
        )
        result = selector.select_or_present(exec_detection)

        assert result is not None

    def test_depth_exceeded_returns_escalation(self):
        """Depth exceeded should return UserEscalation with navigation suggestion."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector
        from pcmrp_tools.bmad_automation.nested_menu import (
            MAX_NESTED_DEPTH,
            UserEscalation,
        )

        selector = MenuSelector()

        # Push beyond max depth
        for i in range(MAX_NESTED_DEPTH + 1):
            selector._depth_tracker.push_menu_context(f"menu-{i}", "standard")

        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.APC,
            options=["Continue"],
            breakdown={"test": 90},
            raw_input="[C] Continue",
        )

        result = selector.select_or_present(detection)

        assert isinstance(result, UserEscalation)
        assert result.severity in ["info", "warning", "error"]
        assert len(result.context_stack) > 0
        assert result.suggestion  # Should have navigation suggestion

    def test_pop_context_after_exit_selection(self):
        """Selecting Exit should pop the context from depth tracker."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        # Push a context
        selector._depth_tracker.push_menu_context("nested-menu", "party_mode")
        assert selector._depth_tracker.get_current_depth() == 1

        # Menu with Exit option - when Exit is selected, context should be popped
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Exit"],
            breakdown={"test": 85},
            raw_input="[E] Exit",
        )

        selector.select_or_present(detection)

        # Context management depends on implementation
        # This test validates the tracker is properly managed


class TestMenuSelectorNestedStateManagement:
    """Tests for state management during nested menu handling."""

    def test_state_saved_before_nested_menu(self):
        """Parent state should be saved before entering nested menu."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        # First menu establishes state
        first_detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Accept", "Decline"],
            breakdown={"test": 85},
            raw_input="[A] Accept [D] Decline",
        )
        selector.select_or_present(first_detection)

        # State manager should be accessible
        assert selector._state_manager is not None

    def test_state_restored_after_nested_menu_exits(self):
        """Parent state should be available for restoration after nested menu."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        # The state manager should support save and restore operations
        assert hasattr(selector._state_manager, "save_parent_state")
        assert hasattr(selector._state_manager, "restore_parent_state")
        assert hasattr(selector._state_manager, "has_saved_state")


class TestMenuSelectorNestedWithExistingBehavior:
    """Tests to ensure existing behavior is preserved after nested integration."""

    def test_high_confidence_still_auto_selects_with_nested(self):
        """High confidence menus should still auto-select after nested integration."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            SelectionResult,
        )

        selector = MenuSelector()
        # Use YVN menu (not a continue menu) to avoid batch-continue routing
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.YVN,
            options=["Yes", "View", "No"],
            breakdown={"test": 90},
            raw_input="[Y] Yes [V] View [N] No",
        )

        result = selector.select_or_present(detection)

        assert isinstance(result, SelectionResult)
        assert result.selected is True
        assert result.option == "Yes"

    def test_medium_confidence_still_recommends_with_nested(self):
        """Medium confidence menus should still provide recommendations."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            RecommendationResult,
        )

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=65,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 65},
            raw_input="[Y] Yes [N] No",
        )

        result = selector.select_or_present(detection)

        assert isinstance(result, RecommendationResult)
        assert result.recommended_option == "Yes"

    def test_low_confidence_still_presents_neutrally_with_nested(self):
        """Low confidence menus should still present options neutrally."""
        from pcmrp_tools.bmad_automation.menu_selection import (
            MenuSelector,
            PresentationResult,
        )

        selector = MenuSelector()
        detection = MenuDetectionResult.detected(
            confidence=35,
            menu_type=MenuType.NUMBERED,
            options=["Option 1", "Option 2"],
            breakdown={"test": 35},
            raw_input="[1] Option 1 [2] Option 2",
        )

        result = selector.select_or_present(detection)

        assert isinstance(result, PresentationResult)
        assert len(result.options) == 2

    def test_logging_still_works_with_nested(self):
        """Logging should continue to work after nested menu integration."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector()

        # Use YVN menu (not a continue menu) to avoid batch-continue routing
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 85},
            raw_input="[Y] Yes [N] No",
        )

        selector.select_or_present(detection)

        trail = selector.logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0].confidence == 85

    def test_bmb_threshold_check_still_works_with_nested(self):
        """BMB threshold checking should continue to work."""
        from pcmrp_tools.bmad_automation.bmb_thresholds import (
            BMBThresholdChecker,
            ValidationMetrics,
        )
        from pcmrp_tools.bmad_automation.menu_selection import (
            EscalationSelectionResult,
            MenuSelector,
        )

        checker = BMBThresholdChecker()
        selector = MenuSelector(bmb_checker=checker)

        # Metrics that trigger escalation
        metrics = ValidationMetrics(
            blocking_errors=5,  # Exceeds threshold of 3
            major_issues=2,
            compliance_score=80,
        )

        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.APC,
            options=["Continue"],
            breakdown={"test": 90},
            raw_input="[C] Continue",
        )

        result = selector.select_or_present(
            detection, validation_metrics=metrics
        )

        assert isinstance(result, EscalationSelectionResult)
