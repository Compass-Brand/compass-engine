"""Tests for Menu Participation Engine - Menu Detection with Confidence Scoring.

Story 2b.1: Menu Detection with Confidence Scoring

This module tests the menu detection capability of the Menu Participation Engine,
including confidence scoring, false positive guards, and pattern matching.

TDD: Tests written FIRST, then implementation.
"""

import pytest
from dataclasses import asdict

# Import the module under test - this will fail until we create it
from pcmrp_tools.bmad_automation.menu_participation_engine import (
    MenuDetectionResult,
    MenuType,
    GuardType,
    CONFIDENCE_THRESHOLD,
    is_in_code_block,
    is_in_blockquote,
    is_example_content,
    is_in_comment,
    check_guards,
    MenuPatternMatch,
    match_apc_menu,
    match_yvn_menu,
    match_numbered_menu,
    match_exit_menu,
    find_menu_patterns,
    score_structural_markers,
    score_position_validation,
    score_option_count,
    score_pattern_match,
    calculate_confidence,
    apply_threshold,
    detect_menu,
)


# =============================================================================
# Task 1: MenuDetectionResult Dataclass Tests
# =============================================================================


class TestMenuDetectionResultDataclass:
    """Tests for the MenuDetectionResult dataclass (Task 1.1-1.5)."""

    # -------------------------------------------------------------------------
    # Task 1.1: Define dataclass with menu_detected, confidence, menu_type, options
    # -------------------------------------------------------------------------

    def test_menu_detection_result_has_menu_detected_field(self):
        """Result must have menu_detected boolean field."""
        result = MenuDetectionResult(
            menu_detected=True,
            confidence=80,
        )
        assert result.menu_detected is True

    def test_menu_detection_result_has_confidence_field(self):
        """Result must have confidence integer field (0-100)."""
        result = MenuDetectionResult(
            menu_detected=True,
            confidence=75,
        )
        assert result.confidence == 75

    def test_menu_detection_result_has_menu_type_field(self):
        """Result must have optional menu_type field."""
        result = MenuDetectionResult(
            menu_detected=True,
            confidence=80,
            menu_type=MenuType.APC,
        )
        assert result.menu_type == MenuType.APC

    def test_menu_detection_result_has_options_field(self):
        """Result must have options list field."""
        result = MenuDetectionResult(
            menu_detected=True,
            confidence=80,
            options=["Advanced", "Party", "Continue"],
        )
        assert result.options == ["Advanced", "Party", "Continue"]

    def test_menu_detection_result_options_defaults_to_empty_list(self):
        """Options field should default to empty list."""
        result = MenuDetectionResult(
            menu_detected=False,
            confidence=0,
        )
        assert result.options == []

    def test_menu_detection_result_menu_type_defaults_to_none(self):
        """menu_type field should default to None."""
        result = MenuDetectionResult(
            menu_detected=False,
            confidence=0,
        )
        assert result.menu_type is None

    # -------------------------------------------------------------------------
    # Task 1.2: Add confidence_breakdown dict for scoring transparency
    # -------------------------------------------------------------------------

    def test_menu_detection_result_has_confidence_breakdown(self):
        """Result must have confidence_breakdown dict field."""
        breakdown = {
            "structural_markers": 30,
            "position_validation": 20,
            "option_count": 20,
            "pattern_match": 30,
        }
        result = MenuDetectionResult(
            menu_detected=True,
            confidence=100,
            confidence_breakdown=breakdown,
        )
        assert result.confidence_breakdown == breakdown

    def test_confidence_breakdown_defaults_to_empty_dict(self):
        """confidence_breakdown should default to empty dict."""
        result = MenuDetectionResult(
            menu_detected=False,
            confidence=0,
        )
        assert result.confidence_breakdown == {}

    # -------------------------------------------------------------------------
    # Task 1.3: Add guard_triggered field to track which guard blocked detection
    # -------------------------------------------------------------------------

    def test_menu_detection_result_has_guard_triggered_field(self):
        """Result must have optional guard_triggered field."""
        result = MenuDetectionResult(
            menu_detected=False,
            confidence=0,
            guard_triggered=GuardType.CODE_BLOCK,
        )
        assert result.guard_triggered == GuardType.CODE_BLOCK

    def test_guard_triggered_defaults_to_none(self):
        """guard_triggered should default to None."""
        result = MenuDetectionResult(
            menu_detected=True,
            confidence=80,
        )
        assert result.guard_triggered is None

    def test_menu_detection_result_has_raw_input_field(self):
        """Result must have raw_input string field."""
        result = MenuDetectionResult(
            menu_detected=True,
            confidence=80,
            raw_input="[A] Advanced [P] Party [C] Continue",
        )
        assert result.raw_input == "[A] Advanced [P] Party [C] Continue"

    def test_raw_input_defaults_to_empty_string(self):
        """raw_input should default to empty string."""
        result = MenuDetectionResult(
            menu_detected=False,
            confidence=0,
        )
        assert result.raw_input == ""

    # -------------------------------------------------------------------------
    # Task 1.4: Add factory methods for detected/not_detected/blocked results
    # -------------------------------------------------------------------------

    def test_detected_factory_method_creates_detected_result(self):
        """detected() factory should create a properly configured result."""
        result = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Advanced", "Party", "Continue"],
            breakdown={"structural_markers": 30, "pattern_match": 30},
            raw_input="[A] Advanced [P] Party [C] Continue",
        )
        assert result.menu_detected is True
        assert result.confidence == 85
        assert result.menu_type == MenuType.APC
        assert result.options == ["Advanced", "Party", "Continue"]
        assert result.confidence_breakdown == {"structural_markers": 30, "pattern_match": 30}
        assert result.raw_input == "[A] Advanced [P] Party [C] Continue"
        assert result.guard_triggered is None

    def test_not_detected_factory_method_creates_undetected_result(self):
        """not_detected() factory should create a properly configured result."""
        result = MenuDetectionResult.not_detected(
            confidence=45,
            breakdown={"structural_markers": 15, "pattern_match": 20},
            raw_input="Some text without a menu",
        )
        assert result.menu_detected is False
        assert result.confidence == 45
        assert result.menu_type is None
        assert result.options == []
        assert result.confidence_breakdown == {"structural_markers": 15, "pattern_match": 20}
        assert result.raw_input == "Some text without a menu"
        assert result.guard_triggered is None

    def test_blocked_factory_method_creates_blocked_result(self):
        """blocked() factory should create a properly configured result."""
        result = MenuDetectionResult.blocked(
            guard=GuardType.CODE_BLOCK,
            raw_input="```\n[A] Advanced [P] Party\n```",
        )
        assert result.menu_detected is False
        assert result.confidence == 0
        assert result.menu_type is None
        assert result.options == []
        assert result.confidence_breakdown == {}
        assert result.guard_triggered == GuardType.CODE_BLOCK
        assert result.raw_input == "```\n[A] Advanced [P] Party\n```"

    def test_blocked_factory_with_all_guard_types(self):
        """blocked() should work with all guard types."""
        for guard_type in GuardType:
            result = MenuDetectionResult.blocked(
                guard=guard_type,
                raw_input="test",
            )
            assert result.guard_triggered == guard_type
            assert result.menu_detected is False

    # -------------------------------------------------------------------------
    # Task 1.5: Serialization tests
    # -------------------------------------------------------------------------

    def test_menu_detection_result_serializable_to_dict(self):
        """Result should be serializable to a dictionary."""
        result = MenuDetectionResult(
            menu_detected=True,
            confidence=80,
            menu_type=MenuType.APC,
            options=["Advanced", "Party", "Continue"],
            confidence_breakdown={"structural_markers": 30},
            guard_triggered=None,
            raw_input="[A] Advanced [P] Party [C] Continue",
        )
        result_dict = asdict(result)
        assert isinstance(result_dict, dict)
        assert result_dict["menu_detected"] is True
        assert result_dict["confidence"] == 80
        assert result_dict["options"] == ["Advanced", "Party", "Continue"]

    def test_menu_type_enum_values(self):
        """MenuType enum should have expected values."""
        assert MenuType.APC.value == "apc"
        assert MenuType.YVN.value == "yvn"
        assert MenuType.NUMBERED.value == "numbered"
        assert MenuType.EXIT.value == "exit"
        assert MenuType.AGENT.value == "agent"
        assert MenuType.UNKNOWN.value == "unknown"

    def test_guard_type_enum_values(self):
        """GuardType enum should have expected values."""
        assert GuardType.CODE_BLOCK.value == "code_block"
        assert GuardType.BLOCKQUOTE.value == "blockquote"
        assert GuardType.EXAMPLE.value == "example"
        assert GuardType.COMMENT.value == "comment"

    def test_confidence_threshold_constant_is_70(self):
        """CONFIDENCE_THRESHOLD should be 70."""
        assert CONFIDENCE_THRESHOLD == 70


# =============================================================================
# Task 2: False Positive Guards Tests
# =============================================================================


class TestCodeBlockGuard:
    """Tests for code block detection (Task 2.1)."""

    def test_detects_menu_inside_fenced_code_block(self):
        """Content inside triple backticks should be detected."""
        text = """Here's an example:
```
[A] Advanced [P] Party [C] Continue
```
"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_code_block(text, menu_line) is True

    def test_does_not_flag_menu_outside_code_block(self):
        """Content outside code blocks should not be flagged."""
        text = """Some regular text.

[A] Advanced [P] Party [C] Continue
"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_code_block(text, menu_line) is False

    def test_detects_menu_inside_indented_code_block(self):
        """Content in 4-space indented code should be detected."""
        text = """Here's an example:

    [A] Advanced [P] Party [C] Continue
"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        # Indented code blocks use 4 spaces
        assert is_in_code_block(text, menu_line) is True

    def test_handles_multiple_code_blocks(self):
        """Should correctly handle text with multiple code blocks."""
        text = """First block:
```
code here
```

[A] Advanced [P] Party [C] Continue

Second block:
```
more code
```
"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_code_block(text, menu_line) is False

    def test_handles_unclosed_code_block(self):
        """Should handle unclosed code block markers."""
        text = """Example:
```
[A] Advanced [P] Party [C] Continue
"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_code_block(text, menu_line) is True

    def test_handles_code_block_with_language(self):
        """Should detect content in code blocks with language specifiers."""
        text = """Example:
```python
[A] Advanced [P] Party [C] Continue
```
"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_code_block(text, menu_line) is True


class TestBlockquoteGuard:
    """Tests for blockquote detection (Task 2.2)."""

    def test_detects_menu_in_blockquote(self):
        """Lines starting with > should be detected."""
        text = """> [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_blockquote(text, menu_line) is True

    def test_detects_nested_blockquote(self):
        """Nested blockquotes should also be detected."""
        text = """>> [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_blockquote(text, menu_line) is True

    def test_does_not_flag_normal_text(self):
        """Regular text should not be flagged."""
        text = """[A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_blockquote(text, menu_line) is False

    def test_handles_multiline_blockquote(self):
        """Multi-line blockquotes should be detected."""
        text = """> Some quoted text
> [A] Advanced [P] Party [C] Continue
> More quoted text"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_blockquote(text, menu_line) is True

    def test_handles_blockquote_with_space(self):
        """Blockquotes with space after > should be detected."""
        text = """> [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_blockquote(text, menu_line) is True


class TestExampleContentGuard:
    """Tests for example content detection (Task 2.3)."""

    def test_detects_example_colon_label(self):
        """Content after 'Example:' should be detected."""
        text = """Example: [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_example_content(text, menu_line) is True

    def test_detects_eg_colon_label(self):
        """Content after 'e.g.:' should be detected."""
        text = """e.g.: [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_example_content(text, menu_line) is True

    def test_detects_for_instance_label(self):
        """Content after 'For instance:' should be detected."""
        text = """For instance: [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_example_content(text, menu_line) is True

    def test_detects_example_on_previous_line(self):
        """Content on line after 'Example:' should be detected."""
        text = """Example:
[A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_example_content(text, menu_line) is True

    def test_does_not_flag_without_example_label(self):
        """Normal content should not be flagged."""
        text = """Ready to proceed.

[A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_example_content(text, menu_line) is False

    def test_detects_sample_label(self):
        """Content after 'Sample:' should be detected."""
        text = """Sample: [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_example_content(text, menu_line) is True

    def test_case_insensitive_detection(self):
        """Example labels should be case-insensitive."""
        text = """EXAMPLE: [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_example_content(text, menu_line) is True


class TestCommentGuard:
    """Tests for comment detection (Task 2.4 - bonus guard)."""

    def test_detects_html_comment(self):
        """Content inside HTML comments should be detected."""
        text = """<!-- [A] Advanced [P] Party [C] Continue -->"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_comment(text, menu_line) is True

    def test_detects_multiline_html_comment(self):
        """Multi-line HTML comments should be detected."""
        text = """<!--
[A] Advanced [P] Party [C] Continue
-->"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_comment(text, menu_line) is True

    def test_does_not_flag_normal_text(self):
        """Normal text should not be flagged."""
        text = """[A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_comment(text, menu_line) is False

    def test_detects_unclosed_html_comment(self):
        """Unclosed HTML comment should still be detected."""
        text = """<!-- [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_comment(text, menu_line) is True

    def test_does_not_flag_text_before_unclosed_comment(self):
        """Text before an unclosed comment should not be flagged."""
        text = """[A] Advanced [P] Party [C] Continue
<!-- some comment"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        assert is_in_comment(text, menu_line) is False


class TestGuardChain:
    """Tests for guard chain (Task 2.4)."""

    def test_returns_none_when_no_guard_triggered(self):
        """Should return None when no guards are triggered."""
        text = """Ready to continue.

[A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        result = check_guards(text, menu_line)
        assert result is None

    def test_returns_code_block_guard(self):
        """Should return CODE_BLOCK when in code block."""
        text = """```
[A] Advanced [P] Party [C] Continue
```"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        result = check_guards(text, menu_line)
        assert result == GuardType.CODE_BLOCK

    def test_returns_blockquote_guard(self):
        """Should return BLOCKQUOTE when in blockquote."""
        text = """> [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        result = check_guards(text, menu_line)
        assert result == GuardType.BLOCKQUOTE

    def test_returns_example_guard(self):
        """Should return EXAMPLE when in example content."""
        text = """Example: [A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        result = check_guards(text, menu_line)
        assert result == GuardType.EXAMPLE

    def test_returns_comment_guard(self):
        """Should return COMMENT when in comment."""
        text = """<!-- [A] Advanced [P] Party [C] Continue -->"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        result = check_guards(text, menu_line)
        assert result == GuardType.COMMENT

    def test_code_block_takes_priority(self):
        """Code block guard should take priority over other guards."""
        text = """```
> Example: [A] Advanced [P] Party [C] Continue
```"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        result = check_guards(text, menu_line)
        assert result == GuardType.CODE_BLOCK


# =============================================================================
# Task 3: Menu Pattern Matchers Tests
# =============================================================================


class TestMenuPatternMatch:
    """Tests for the MenuPatternMatch dataclass."""

    def test_menu_pattern_match_has_required_fields(self):
        """MenuPatternMatch should have menu_type, options, menu_line fields."""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Advanced", "Party", "Continue"],
            menu_line="[A] Advanced [P] Party [C] Continue",
        )
        assert match.menu_type == MenuType.APC
        assert match.options == ["Advanced", "Party", "Continue"]
        assert match.menu_line == "[A] Advanced [P] Party [C] Continue"


class TestAPCMenuMatcher:
    """Tests for [A][P][C] style menu pattern matcher (Task 3.1)."""

    def test_matches_standard_apc_menu(self):
        """Should match [A] Advanced [P] Party [C] Continue pattern."""
        text = "[A] Advanced Elicitation  [P] Party Mode  [C] Continue"
        match = match_apc_menu(text)
        assert match is not None
        assert match.menu_type == MenuType.APC
        assert "Advanced" in match.options[0] or "Advanced Elicitation" in match.options[0]
        assert "Party" in match.options[1] or "Party Mode" in match.options[1]
        assert "Continue" in match.options[2]

    def test_matches_apc_menu_with_newlines(self):
        """Should match APC menu even with surrounding text."""
        text = """Step complete.

[A] Advanced [P] Party [C] Continue
"""
        match = match_apc_menu(text)
        assert match is not None
        assert match.menu_type == MenuType.APC

    def test_does_not_match_non_apc_text(self):
        """Should return None for non-menu text."""
        text = "This is regular text without any menu."
        match = match_apc_menu(text)
        assert match is None

    def test_matches_apc_with_descriptions(self):
        """Should extract option descriptions."""
        text = "[A] Advanced Elicitation [P] Party Mode [C] Continue"
        match = match_apc_menu(text)
        assert match is not None
        assert len(match.options) == 3

    def test_matches_bracketed_letter_format(self):
        """Should match [X] format options."""
        text = "[A] First [B] Second [C] Third"
        match = match_apc_menu(text)
        # This should match as a generic bracket-letter menu
        assert match is not None


class TestYVNMenuMatcher:
    """Tests for [Y][V][N] style menu pattern matcher (Task 3.2)."""

    def test_matches_standard_yvn_menu(self):
        """Should match [Y] Yes [V] View [N] No pattern."""
        text = "[Y] Yes [V] View Details [N] No"
        match = match_yvn_menu(text)
        assert match is not None
        assert match.menu_type == MenuType.YVN

    def test_matches_yn_menu(self):
        """Should match [Y]/[N] menu without [V]."""
        text = "[Y] Yes [N] No"
        match = match_yvn_menu(text)
        assert match is not None
        assert match.menu_type == MenuType.YVN

    def test_does_not_match_non_yvn_text(self):
        """Should return None for non-YVN text."""
        text = "[A] Advanced [P] Party [C] Continue"
        match = match_yvn_menu(text)
        assert match is None


class TestNumberedMenuMatcher:
    """Tests for numbered option pattern matcher (Task 3.3)."""

    def test_matches_numbered_menu(self):
        """Should match [1] [2] [3] numbered options."""
        text = "[1] First Option [2] Second Option [3] Third Option"
        match = match_numbered_menu(text)
        assert match is not None
        assert match.menu_type == MenuType.NUMBERED
        assert len(match.options) >= 3

    def test_matches_numbered_menu_vertical(self):
        """Should match vertical numbered options."""
        text = """[1] First Option
[2] Second Option
[3] Third Option"""
        match = match_numbered_menu(text)
        assert match is not None
        assert match.menu_type == MenuType.NUMBERED

    def test_does_not_match_non_numbered_text(self):
        """Should return None for non-numbered menus."""
        text = "[A] Advanced [P] Party [C] Continue"
        match = match_numbered_menu(text)
        assert match is None


class TestExitMenuMatcher:
    """Tests for [E] Exit pattern matcher (Task 3.4)."""

    def test_matches_exit_menu(self):
        """Should match [E] Exit pattern."""
        text = "[E] Exit"
        match = match_exit_menu(text)
        assert match is not None
        assert match.menu_type == MenuType.EXIT

    def test_matches_exit_with_description(self):
        """Should match [E] with description."""
        text = "[E] Exit Party Mode"
        match = match_exit_menu(text)
        assert match is not None
        assert "Exit" in match.options[0]

    def test_does_not_match_non_exit_text(self):
        """Should return None for non-exit text."""
        text = "[A] Advanced [P] Party"
        match = match_exit_menu(text)
        assert match is None


class TestFindMenuPatterns:
    """Tests for the main pattern finder function (Task 3.5)."""

    def test_finds_apc_menu(self):
        """Should find APC menu pattern."""
        text = """Ready for input.

[A] Advanced [P] Party [C] Continue"""
        matches = find_menu_patterns(text)
        assert len(matches) >= 1
        assert any(m.menu_type == MenuType.APC for m in matches)

    def test_finds_yvn_menu(self):
        """Should find YVN menu pattern."""
        text = "[Y] Yes [N] No"
        matches = find_menu_patterns(text)
        assert len(matches) >= 1
        assert any(m.menu_type == MenuType.YVN for m in matches)

    def test_finds_numbered_menu(self):
        """Should find numbered menu pattern."""
        text = "[1] Option A [2] Option B [3] Option C"
        matches = find_menu_patterns(text)
        assert len(matches) >= 1
        assert any(m.menu_type == MenuType.NUMBERED for m in matches)

    def test_finds_exit_menu(self):
        """Should find exit menu pattern."""
        text = "[E] Exit"
        matches = find_menu_patterns(text)
        assert len(matches) >= 1
        assert any(m.menu_type == MenuType.EXIT for m in matches)

    def test_returns_empty_for_no_menus(self):
        """Should return empty list for text without menus."""
        text = "This is regular text without any menus."
        matches = find_menu_patterns(text)
        assert matches == []

    def test_returns_best_match_first(self):
        """Should return matches sorted by relevance."""
        text = "[A] Advanced [P] Party [C] Continue"
        matches = find_menu_patterns(text)
        assert len(matches) >= 1
        # APC should be preferred match
        assert matches[0].menu_type == MenuType.APC


# =============================================================================
# Task 4: Confidence Scoring System Tests
# =============================================================================


class TestStructuralMarkerScoring:
    """Tests for structural marker scoring (Task 4.2)."""

    def test_full_points_for_brackets(self):
        """Should give full points (30) for proper bracket formatting."""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        score = score_structural_markers(menu_line)
        assert score == 30

    def test_reduced_points_for_partial_brackets(self):
        """Should give reduced points for inconsistent formatting."""
        menu_line = "[A] Advanced P Party [C] Continue"
        score = score_structural_markers(menu_line)
        assert 0 < score < 30

    def test_zero_for_no_brackets(self):
        """Should give zero for text without brackets."""
        menu_line = "Advanced Party Continue"
        score = score_structural_markers(menu_line)
        assert score == 0

    def test_score_range_is_0_to_30(self):
        """Score should always be between 0 and 30."""
        test_cases = [
            "[A] Test [B] Test",
            "No brackets here",
            "[1] [2] [3]",
        ]
        for text in test_cases:
            score = score_structural_markers(text)
            assert 0 <= score <= 30


class TestPositionValidationScoring:
    """Tests for position validation scoring (Task 4.3)."""

    def test_full_points_at_end_of_output(self):
        """Should give full points (20) for menu at end of output."""
        text = """Some workflow output here.

[A] Advanced [P] Party [C] Continue"""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        score = score_position_validation(text, menu_line)
        assert score == 20

    def test_reduced_points_for_embedded_menu(self):
        """Should give reduced points for menu embedded in middle."""
        text = """Start text.

[A] Advanced [P] Party [C] Continue

More text after menu."""
        menu_line = "[A] Advanced [P] Party [C] Continue"
        score = score_position_validation(text, menu_line)
        assert 0 < score < 20

    def test_points_for_standalone_line(self):
        """Should give points for menu on its own line."""
        text = "[A] Advanced [P] Party [C] Continue"
        menu_line = "[A] Advanced [P] Party [C] Continue"
        score = score_position_validation(text, menu_line)
        assert score > 0

    def test_score_range_is_0_to_20(self):
        """Score should always be between 0 and 20."""
        test_cases = [
            ("[A] Menu", "[A] Menu"),
            ("Text\n[A] Menu", "[A] Menu"),
            ("Text [A] Menu", "[A] Menu"),
        ]
        for text, menu_line in test_cases:
            score = score_position_validation(text, menu_line)
            assert 0 <= score <= 20

    def test_menu_not_found_in_text(self):
        """Should return low score when menu line not in text."""
        text = "Some completely different text"
        menu_line = "[A] Advanced [P] Party [C] Continue"
        score = score_position_validation(text, menu_line)
        assert score == 5


class TestOptionCountScoring:
    """Tests for option count scoring (Task 4.4)."""

    def test_full_points_for_three_options(self):
        """Should give full points (20) for 3 options (ideal)."""
        options = ["Advanced", "Party", "Continue"]
        score = score_option_count(options)
        assert score == 20

    def test_full_points_for_two_to_four_options(self):
        """Should give full points for 2-4 options."""
        for num_options in [2, 3, 4]:
            options = [f"Option {i}" for i in range(num_options)]
            score = score_option_count(options)
            assert score == 20

    def test_reduced_points_for_many_options(self):
        """Should give reduced points for >4 options."""
        options = [f"Option {i}" for i in range(6)]
        score = score_option_count(options)
        assert 0 < score < 20

    def test_reduced_points_for_single_option(self):
        """Should give reduced points for single option."""
        options = ["Exit"]
        score = score_option_count(options)
        assert 0 < score < 20

    def test_zero_for_no_options(self):
        """Should give zero for empty options."""
        options = []
        score = score_option_count(options)
        assert score == 0

    def test_score_range_is_0_to_20(self):
        """Score should always be between 0 and 20."""
        for num_options in range(10):
            options = [f"Option {i}" for i in range(num_options)]
            score = score_option_count(options)
            assert 0 <= score <= 20


class TestPatternMatchScoring:
    """Tests for pattern match strength scoring (Task 4.5)."""

    def test_full_points_for_apc_match(self):
        """Should give full points (30) for APC menu match."""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Advanced", "Party", "Continue"],
            menu_line="[A] Advanced [P] Party [C] Continue",
        )
        score = score_pattern_match(match)
        assert score == 30

    def test_full_points_for_yvn_match(self):
        """Should give full points for YVN menu match."""
        match = MenuPatternMatch(
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            menu_line="[Y] Yes [N] No",
        )
        score = score_pattern_match(match)
        assert score == 30

    def test_full_points_for_numbered_match(self):
        """Should give full points for numbered menu match."""
        match = MenuPatternMatch(
            menu_type=MenuType.NUMBERED,
            options=["Option 1", "Option 2"],
            menu_line="[1] Option 1 [2] Option 2",
        )
        score = score_pattern_match(match)
        assert score == 30

    def test_reduced_points_for_unknown_type(self):
        """Should give reduced points for unknown menu type."""
        match = MenuPatternMatch(
            menu_type=MenuType.UNKNOWN,
            options=["Something"],
            menu_line="Something",
        )
        score = score_pattern_match(match)
        assert 0 <= score < 30

    def test_score_range_is_0_to_30(self):
        """Score should always be between 0 and 30."""
        for menu_type in MenuType:
            match = MenuPatternMatch(
                menu_type=menu_type,
                options=["Test"],
                menu_line="[T] Test",
            )
            score = score_pattern_match(match)
            assert 0 <= score <= 30


class TestConfidenceCalculation:
    """Tests for overall confidence calculation (Task 4.5)."""

    def test_calculates_total_from_components(self):
        """Should sum all scoring components."""
        text = """Ready.

[A] Advanced [P] Party [C] Continue"""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Advanced", "Party", "Continue"],
            menu_line="[A] Advanced [P] Party [C] Continue",
        )
        confidence, breakdown = calculate_confidence(text, match)
        # Should have all four components
        assert "structural_markers" in breakdown
        assert "position_validation" in breakdown
        assert "option_count" in breakdown
        assert "pattern_match" in breakdown
        # Total should equal sum of components
        assert confidence == sum(breakdown.values())

    def test_max_confidence_is_100(self):
        """Perfect menu should get 100 confidence."""
        text = """Ready.

[A] Advanced [P] Party [C] Continue"""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Advanced", "Party", "Continue"],
            menu_line="[A] Advanced [P] Party [C] Continue",
        )
        confidence, breakdown = calculate_confidence(text, match)
        assert confidence == 100

    def test_breakdown_includes_all_components(self):
        """Breakdown should include all four scoring components."""
        text = "[A] Test [P] Test [C] Test"
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Test", "Test", "Test"],
            menu_line="[A] Test [P] Test [C] Test",
        )
        _, breakdown = calculate_confidence(text, match)
        assert set(breakdown.keys()) == {
            "structural_markers",
            "position_validation",
            "option_count",
            "pattern_match",
        }


# =============================================================================
# Task 5: 70-Point Threshold Logic Tests
# =============================================================================


class TestThresholdLogic:
    """Tests for 70-point threshold logic (Task 5)."""

    def test_threshold_constant_is_70(self):
        """CONFIDENCE_THRESHOLD should be 70."""
        assert CONFIDENCE_THRESHOLD == 70

    def test_above_threshold_returns_detected(self):
        """Confidence >= 70 should result in menu_detected: true."""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Advanced", "Party", "Continue"],
            menu_line="[A] Advanced [P] Party [C] Continue",
        )
        result = apply_threshold(
            confidence=80,
            breakdown={"structural_markers": 30, "pattern_match": 30, "position_validation": 10, "option_count": 10},
            match=match,
            raw_input="[A] Advanced [P] Party [C] Continue",
        )
        assert result.menu_detected is True
        assert result.confidence == 80

    def test_at_threshold_returns_detected(self):
        """Confidence exactly 70 should result in menu_detected: true."""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Advanced", "Party", "Continue"],
            menu_line="[A] Advanced [P] Party [C] Continue",
        )
        result = apply_threshold(
            confidence=70,
            breakdown={"structural_markers": 20, "pattern_match": 30, "position_validation": 10, "option_count": 10},
            match=match,
            raw_input="[A] Advanced [P] Party [C] Continue",
        )
        assert result.menu_detected is True
        assert result.confidence == 70

    def test_below_threshold_returns_not_detected(self):
        """Confidence < 70 should result in menu_detected: false."""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Test"],
            menu_line="[A] Test",
        )
        result = apply_threshold(
            confidence=50,
            breakdown={"structural_markers": 15, "pattern_match": 15, "position_validation": 10, "option_count": 10},
            match=match,
            raw_input="[A] Test",
        )
        assert result.menu_detected is False
        assert result.confidence == 50

    def test_returns_confidence_even_when_below_threshold(self):
        """Should include confidence score even when below threshold."""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Test"],
            menu_line="[A] Test",
        )
        result = apply_threshold(
            confidence=45,
            breakdown={"structural_markers": 15, "pattern_match": 15, "position_validation": 10, "option_count": 5},
            match=match,
            raw_input="[A] Test",
        )
        assert result.confidence == 45
        assert result.confidence_breakdown == {"structural_markers": 15, "pattern_match": 15, "position_validation": 10, "option_count": 5}

    def test_detected_result_includes_menu_type(self):
        """Detected result should include menu_type."""
        match = MenuPatternMatch(
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            menu_line="[Y] Yes [N] No",
        )
        result = apply_threshold(
            confidence=85,
            breakdown={"structural_markers": 25, "pattern_match": 30, "position_validation": 20, "option_count": 10},
            match=match,
            raw_input="[Y] Yes [N] No",
        )
        assert result.menu_type == MenuType.YVN

    def test_detected_result_includes_options(self):
        """Detected result should include extracted options."""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Advanced", "Party", "Continue"],
            menu_line="[A] Advanced [P] Party [C] Continue",
        )
        result = apply_threshold(
            confidence=90,
            breakdown={"structural_markers": 30, "pattern_match": 30, "position_validation": 20, "option_count": 10},
            match=match,
            raw_input="[A] Advanced [P] Party [C] Continue",
        )
        assert result.options == ["Advanced", "Party", "Continue"]

    def test_not_detected_result_has_no_menu_type(self):
        """Not detected result should have menu_type None."""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Test"],
            menu_line="[A] Test",
        )
        result = apply_threshold(
            confidence=40,
            breakdown={"structural_markers": 10, "pattern_match": 15, "position_validation": 10, "option_count": 5},
            match=match,
            raw_input="[A] Test",
        )
        assert result.menu_type is None

    def test_not_detected_result_has_empty_options(self):
        """Not detected result should have empty options list."""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Test"],
            menu_line="[A] Test",
        )
        result = apply_threshold(
            confidence=40,
            breakdown={"structural_markers": 10, "pattern_match": 15, "position_validation": 10, "option_count": 5},
            match=match,
            raw_input="[A] Test",
        )
        assert result.options == []

    def test_boundary_at_69_is_not_detected(self):
        """Confidence of 69 (just below threshold) should not be detected."""
        match = MenuPatternMatch(
            menu_type=MenuType.APC,
            options=["Test", "Test"],
            menu_line="[A] Test [B] Test",
        )
        result = apply_threshold(
            confidence=69,
            breakdown={"structural_markers": 20, "pattern_match": 25, "position_validation": 14, "option_count": 10},
            match=match,
            raw_input="[A] Test [B] Test",
        )
        assert result.menu_detected is False


# =============================================================================
# Task 6: Main detect_menu() Function Tests
# =============================================================================


class TestDetectMenuFunction:
    """Tests for the main detect_menu() function (Task 6)."""

    # -------------------------------------------------------------------------
    # AC #1: Detects [A] Advanced [P] Party [C] Continue with confidence >= 70
    # -------------------------------------------------------------------------

    def test_detects_apc_menu_with_high_confidence(self):
        """AC #1: Should detect APC menu with confidence >= 70."""
        text = """Step complete. Ready for next action.

[A] Advanced Elicitation  [P] Party Mode  [C] Continue"""
        result = detect_menu(text)
        assert result.menu_detected is True
        assert result.confidence >= 70
        assert result.menu_type == MenuType.APC

    def test_detects_standard_apc_menu(self):
        """Should detect standard [A][P][C] menu format."""
        text = "[A] Advanced [P] Party [C] Continue"
        result = detect_menu(text)
        assert result.menu_detected is True
        assert result.menu_type == MenuType.APC

    # -------------------------------------------------------------------------
    # AC #2: Rejects menu-like text inside code blocks
    # -------------------------------------------------------------------------

    def test_rejects_menu_in_code_block(self):
        """AC #2: Should reject menu-like text inside ``` code blocks."""
        text = """Here's an example of the menu format:
```
[A] Advanced  [P] Party  [C] Continue
```"""
        result = detect_menu(text)
        assert result.menu_detected is False
        assert result.guard_triggered == GuardType.CODE_BLOCK

    def test_rejects_menu_in_indented_code_block(self):
        """AC #2: Should reject menu in indented code blocks."""
        text = """Example:

    [A] Advanced [P] Party [C] Continue"""
        result = detect_menu(text)
        assert result.menu_detected is False
        assert result.guard_triggered == GuardType.CODE_BLOCK

    # -------------------------------------------------------------------------
    # AC #3: Rejects menu-like text inside blockquotes
    # -------------------------------------------------------------------------

    def test_rejects_menu_in_blockquote(self):
        """AC #3: Should reject menu-like text in blockquotes (> prefix)."""
        text = """> [A] Advanced [P] Party [C] Continue"""
        result = detect_menu(text)
        assert result.menu_detected is False
        assert result.guard_triggered == GuardType.BLOCKQUOTE

    def test_rejects_menu_in_nested_blockquote(self):
        """AC #3: Should reject menu in nested blockquotes."""
        text = """>> [A] Advanced [P] Party [C] Continue"""
        result = detect_menu(text)
        assert result.menu_detected is False
        assert result.guard_triggered == GuardType.BLOCKQUOTE

    # -------------------------------------------------------------------------
    # AC #4: Rejects menu-like text labeled as "Example:"
    # -------------------------------------------------------------------------

    def test_rejects_menu_after_example_label(self):
        """AC #4: Should reject menu-like text after 'Example:' label."""
        text = """Example: [A] Advanced [P] Party [C] Continue
This is how menus look."""
        result = detect_menu(text)
        assert result.menu_detected is False
        assert result.guard_triggered == GuardType.EXAMPLE

    def test_rejects_menu_on_line_after_example(self):
        """AC #4: Should reject menu on line after Example: label."""
        text = """Example:
[A] Advanced [P] Party [C] Continue"""
        result = detect_menu(text)
        assert result.menu_detected is False
        assert result.guard_triggered == GuardType.EXAMPLE

    # -------------------------------------------------------------------------
    # AC #5: Confidence breakdown includes all scoring components
    # -------------------------------------------------------------------------

    def test_confidence_breakdown_has_all_components(self):
        """AC #5: Confidence breakdown should include all scoring components."""
        text = """Ready.

[A] Advanced [P] Party [C] Continue"""
        result = detect_menu(text)
        assert result.menu_detected is True
        assert "structural_markers" in result.confidence_breakdown
        assert "position_validation" in result.confidence_breakdown
        assert "option_count" in result.confidence_breakdown
        assert "pattern_match" in result.confidence_breakdown

    def test_structural_markers_contributes_30_points(self):
        """AC #5: Structural markers should contribute up to 30 points."""
        text = "[A] Advanced [P] Party [C] Continue"
        result = detect_menu(text)
        assert result.confidence_breakdown["structural_markers"] == 30

    def test_position_validation_contributes_20_points(self):
        """AC #5: Position validation should contribute up to 20 points."""
        text = """Ready.

[A] Advanced [P] Party [C] Continue"""
        result = detect_menu(text)
        assert result.confidence_breakdown["position_validation"] == 20

    def test_option_count_contributes_20_points(self):
        """AC #5: Option count should contribute up to 20 points."""
        text = "[A] Advanced [P] Party [C] Continue"
        result = detect_menu(text)
        assert result.confidence_breakdown["option_count"] == 20

    # -------------------------------------------------------------------------
    # Task 6.3: Edge cases
    # -------------------------------------------------------------------------

    def test_empty_input_returns_not_detected(self):
        """Should return not_detected for empty input."""
        result = detect_menu("")
        assert result.menu_detected is False

    def test_whitespace_only_returns_not_detected(self):
        """Should return not_detected for whitespace-only input."""
        result = detect_menu("   \n\n   ")
        assert result.menu_detected is False

    def test_no_menu_returns_not_detected(self):
        """Should return not_detected when no menu pattern found."""
        text = "This is just regular text without any menu options."
        result = detect_menu(text)
        assert result.menu_detected is False

    def test_yvn_menu_detected(self):
        """Should detect [Y][V][N] menu type."""
        text = "[Y] Yes [V] View Details [N] No"
        result = detect_menu(text)
        assert result.menu_detected is True
        assert result.menu_type == MenuType.YVN

    def test_numbered_menu_detected(self):
        """Should detect numbered option menus."""
        text = "[1] First Option [2] Second Option [3] Third Option"
        result = detect_menu(text)
        assert result.menu_detected is True
        assert result.menu_type == MenuType.NUMBERED

    def test_exit_menu_detected(self):
        """Should detect [E] Exit menu."""
        text = "[E] Exit Party Mode"
        result = detect_menu(text)
        assert result.menu_detected is True
        assert result.menu_type == MenuType.EXIT

    def test_raw_input_preserved(self):
        """Result should preserve the raw input text."""
        text = "[A] Advanced [P] Party [C] Continue"
        result = detect_menu(text)
        assert result.raw_input == text

    def test_options_extracted(self):
        """Should extract option labels from detected menu."""
        text = "[A] Advanced [P] Party [C] Continue"
        result = detect_menu(text)
        assert result.menu_detected is True
        assert len(result.options) == 3


# =============================================================================
# Integration Tests - Full Acceptance Criteria Scenarios
# =============================================================================


class TestAcceptanceCriteriaIntegration:
    """Integration tests covering all Acceptance Criteria scenarios."""

    def test_ac1_full_scenario(self):
        """AC #1: Full scenario - detects APC menu with confidence >= 70."""
        workflow_output = """
Step complete. Ready for next action.

[A] Advanced Elicitation  [P] Party Mode  [C] Continue
"""
        result = detect_menu(workflow_output)
        assert result.menu_detected is True
        assert result.confidence >= 70
        assert result.menu_type == MenuType.APC
        assert len(result.options) >= 3

    def test_ac2_full_scenario(self):
        """AC #2: Full scenario - rejects menu in code block."""
        workflow_output = """
Here's an example of the menu format:
```
[A] Advanced  [P] Party  [C] Continue
```
"""
        result = detect_menu(workflow_output)
        assert result.menu_detected is False
        assert result.guard_triggered == GuardType.CODE_BLOCK
        assert result.confidence == 0

    def test_ac3_full_scenario(self):
        """AC #3: Full scenario - rejects menu in blockquote."""
        workflow_output = """> [A] Advanced [P] Party [C] Continue"""
        result = detect_menu(workflow_output)
        assert result.menu_detected is False
        assert result.guard_triggered == GuardType.BLOCKQUOTE
        assert result.confidence == 0

    def test_ac4_full_scenario(self):
        """AC #4: Full scenario - rejects menu labeled as example."""
        workflow_output = """
Example: [A] Advanced [P] Party [C] Continue
This is how menus look.
"""
        result = detect_menu(workflow_output)
        assert result.menu_detected is False
        assert result.guard_triggered == GuardType.EXAMPLE
        assert result.confidence == 0

    def test_ac5_full_scenario(self):
        """AC #5: Full scenario - confidence breakdown includes all components."""
        workflow_output = """Ready.

[A] Advanced [P] Party [C] Continue"""
        result = detect_menu(workflow_output)
        assert result.menu_detected is True
        # Verify all four components present
        assert set(result.confidence_breakdown.keys()) == {
            "structural_markers",
            "position_validation",
            "option_count",
            "pattern_match",
        }
        # Verify expected point allocations
        assert result.confidence_breakdown["structural_markers"] == 30
        assert result.confidence_breakdown["position_validation"] == 20
        assert result.confidence_breakdown["option_count"] == 20
        assert result.confidence_breakdown["pattern_match"] == 30
        # Total should be 100
        assert result.confidence == 100
