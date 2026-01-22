"""Menu Participation Engine - Menu Detection with Confidence Scoring.

Story 2b.1: Menu Detection with Confidence Scoring

This module provides menu detection capabilities for BMAD workflow automation,
including confidence scoring, false positive guards, and pattern matching.

Menu Types Detected:
- [A][P][C] - Advanced Elicitation / Party Mode / Continue
- [Y][V][N] - Yes / View / No (iteration menus)
- [1][2][3] - Numbered options (multi-select)
- [E] - Exit (party mode termination)
- [MH][CH] - Agent menus (Menu Help, Chat, etc.)

Confidence Scoring (100 points max):
- Structural markers: 0-30 points (brackets, separators, consistent formatting)
- Position validation: 0-20 points (end of output, standalone line, not embedded)
- Option count: 0-20 points (2-4 options = full points, >4 = reduced)
- Pattern match strength: 0-30 points (exact match vs partial)

False Positive Guards:
1. Code Block Guard - Reject if inside ``` markers
2. Blockquote Guard - Reject if line starts with >
3. Example Guard - Reject if preceded by "Example:", "e.g.:", etc.
4. Comment Guard - Reject if inside <!-- --> or # comments
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# Compiled Regex Patterns (Performance Optimization)
# =============================================================================

# Example content detection patterns
_EXAMPLE_PATTERNS = [
    re.compile(r"example\s*:", re.IGNORECASE),
    re.compile(r"e\.g\.?\s*:", re.IGNORECASE),
    re.compile(r"for\s+instance\s*:", re.IGNORECASE),
    re.compile(r"sample\s*:", re.IGNORECASE),
    re.compile(r"such\s+as\s*:", re.IGNORECASE),
]

# HTML comment pattern
_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)

# Menu pattern matchers
_APC_PATTERN = re.compile(r"\[([A-Z])\]\s*([^\[\n]+?)(?=\s*\[[A-Z]\]|\s*$)", re.IGNORECASE)
_YVN_PATTERN = re.compile(r"\[([YVN])\]\s*([^\[\n]+?)(?=\s*\[[YVN]\]|\s*$)", re.IGNORECASE)
_NUMBERED_PATTERN = re.compile(r"\[(\d+)\]\s*([^\[\n]+?)(?=\s*\[\d+\]|\s*$)")
_EXIT_PATTERN = re.compile(r"\[E\]\s*(Exit[^\[\n]*)", re.IGNORECASE)

# Structural marker pattern
_BRACKET_PATTERN = re.compile(r"\[[A-Za-z0-9]+\]")


# =============================================================================
# Constants
# =============================================================================

CONFIDENCE_THRESHOLD = 70
"""Minimum confidence score required for menu_detected to be True."""


# =============================================================================
# Enums
# =============================================================================


class MenuType(Enum):
    """Types of menus that can be detected in BMAD workflow output."""

    APC = "apc"  # [A][P][C] - Advanced/Party/Continue
    YVN = "yvn"  # [Y][V][N] - Yes/View/No
    NUMBERED = "numbered"  # [1][2][3] - Numbered options
    EXIT = "exit"  # [E] - Exit
    AGENT = "agent"  # [MH][CH] - Agent menus
    UNKNOWN = "unknown"  # Unrecognized menu type


class GuardType(Enum):
    """Types of false positive guards that can block menu detection."""

    CODE_BLOCK = "code_block"  # Content inside ``` markers
    BLOCKQUOTE = "blockquote"  # Lines starting with >
    EXAMPLE = "example"  # Content after "Example:", "e.g.:", etc.
    COMMENT = "comment"  # Content inside <!-- --> or # comments


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class MenuDetectionResult:
    """Result of menu detection analysis.

    Attributes:
        menu_detected: True if a menu was detected with sufficient confidence.
        confidence: Confidence score from 0-100.
        menu_type: Type of menu detected, or None if not detected.
        options: List of menu option labels extracted.
        confidence_breakdown: Dict showing how confidence score was calculated.
        guard_triggered: Which guard blocked detection, or None if not blocked.
        raw_input: The original input text that was analyzed.
    """

    menu_detected: bool
    confidence: int
    menu_type: Optional[MenuType] = None
    options: List[str] = field(default_factory=list)
    confidence_breakdown: Dict[str, int] = field(default_factory=dict)
    guard_triggered: Optional[GuardType] = None
    raw_input: str = ""

    @classmethod
    def detected(
        cls,
        confidence: int,
        menu_type: MenuType,
        options: List[str],
        breakdown: Dict[str, int],
        raw_input: str,
    ) -> "MenuDetectionResult":
        """Factory method for creating a detected menu result.

        Args:
            confidence: Confidence score (0-100).
            menu_type: Type of menu detected.
            options: List of menu option labels.
            breakdown: Dict showing confidence score breakdown.
            raw_input: Original input text.

        Returns:
            MenuDetectionResult with menu_detected=True.
        """
        return cls(
            menu_detected=True,
            confidence=confidence,
            menu_type=menu_type,
            options=options,
            confidence_breakdown=breakdown,
            guard_triggered=None,
            raw_input=raw_input,
        )

    @classmethod
    def not_detected(
        cls,
        confidence: int,
        breakdown: Dict[str, int],
        raw_input: str,
    ) -> "MenuDetectionResult":
        """Factory method for creating a not-detected result.

        Args:
            confidence: Confidence score that was below threshold.
            breakdown: Dict showing confidence score breakdown.
            raw_input: Original input text.

        Returns:
            MenuDetectionResult with menu_detected=False.
        """
        return cls(
            menu_detected=False,
            confidence=confidence,
            menu_type=None,
            options=[],
            confidence_breakdown=breakdown,
            guard_triggered=None,
            raw_input=raw_input,
        )

    @classmethod
    def blocked(
        cls,
        guard: GuardType,
        raw_input: str,
    ) -> "MenuDetectionResult":
        """Factory method for creating a blocked (false positive guard) result.

        Args:
            guard: Which guard type blocked the detection.
            raw_input: Original input text.

        Returns:
            MenuDetectionResult with menu_detected=False and guard_triggered set.
        """
        return cls(
            menu_detected=False,
            confidence=0,
            menu_type=None,
            options=[],
            confidence_breakdown={},
            guard_triggered=guard,
            raw_input=raw_input,
        )


# =============================================================================
# False Positive Guards (Task 2)
# =============================================================================


def is_in_code_block(text: str, menu_line: str) -> bool:
    """Check if the menu line is inside a code block.

    Detects both fenced code blocks (``` ... ```) and indented code blocks
    (4 spaces or 1 tab indentation).

    Args:
        text: The full text to analyze.
        menu_line: The potential menu line to check.

    Returns:
        True if the menu line is inside a code block.
    """
    lines = text.split("\n")
    in_fenced_block = False

    for line in lines:
        # Check for fenced code block markers (``` or ```language)
        if line.strip().startswith("```"):
            in_fenced_block = not in_fenced_block
            continue

        # Check if this line contains the menu text
        if menu_line in line:
            # If we're in a fenced block, return True
            if in_fenced_block:
                return True

            # Check for indented code block (4 spaces or tab)
            if line.startswith("    ") or line.startswith("\t"):
                return True

    return False


def is_in_blockquote(text: str, menu_line: str) -> bool:
    """Check if the menu line is inside a blockquote.

    Detects lines starting with > (with optional nesting).

    Args:
        text: The full text to analyze.
        menu_line: The potential menu line to check.

    Returns:
        True if the menu line is inside a blockquote.
    """
    lines = text.split("\n")

    for line in lines:
        if menu_line in line:
            # Check if line starts with > (blockquote marker)
            stripped = line.lstrip()
            if stripped.startswith(">"):
                return True

    return False


def is_example_content(text: str, menu_line: str) -> bool:
    """Check if the menu line is preceded by an example label.

    Detects patterns like "Example:", "e.g.:", "For instance:", "Sample:".

    Args:
        text: The full text to analyze.
        menu_line: The potential menu line to check.

    Returns:
        True if the menu line appears to be example content.
    """
    lines = text.split("\n")
    found_example_label_line = -1

    for i, line in enumerate(lines):
        # Check if this line has an example label
        for pattern in _EXAMPLE_PATTERNS:
            match = pattern.search(line)  # Single search, not duplicate
            if match:
                # Check if menu is on same line after the label
                if menu_line in line[match.end():]:
                    return True
                # Record this line as having an example label
                found_example_label_line = i
                break  # Found a match, no need to check other patterns

        # Check if menu is on this line and we found an example label recently
        if menu_line in line and found_example_label_line >= 0:
            # Menu is on same line as label or immediately after
            if i == found_example_label_line or i == found_example_label_line + 1:
                return True

    return False


def is_in_comment(text: str, menu_line: str) -> bool:
    """Check if the menu line is inside an HTML comment.

    Detects content within <!-- ... --> markers.

    Args:
        text: The full text to analyze.
        menu_line: The potential menu line to check.

    Returns:
        True if the menu line is inside an HTML comment.
    """
    # Check for single-line comments using pre-compiled pattern
    for match in _COMMENT_PATTERN.finditer(text):
        if menu_line in match.group():
            return True

    # Check for unclosed comments (starts with <!-- but no -->)
    unclosed_start = text.find("<!--")
    if unclosed_start != -1:
        unclosed_end = text.find("-->", unclosed_start)
        if unclosed_end == -1:
            # Comment never closed
            if menu_line in text[unclosed_start:]:
                return True

    return False


def check_guards(text: str, menu_line: str) -> Optional[GuardType]:
    """Check all false positive guards and return the first one triggered.

    Guards are checked in priority order:
    1. Code block (highest priority)
    2. Comment
    3. Blockquote
    4. Example content

    Args:
        text: The full text to analyze.
        menu_line: The potential menu line to check.

    Returns:
        The GuardType that was triggered, or None if no guards triggered.
    """
    # Check guards in priority order
    if is_in_code_block(text, menu_line):
        return GuardType.CODE_BLOCK

    if is_in_comment(text, menu_line):
        return GuardType.COMMENT

    if is_in_blockquote(text, menu_line):
        return GuardType.BLOCKQUOTE

    if is_example_content(text, menu_line):
        return GuardType.EXAMPLE

    return None


# =============================================================================
# Menu Pattern Matchers (Task 3)
# =============================================================================


@dataclass
class MenuPatternMatch:
    """Result of a menu pattern match.

    Attributes:
        menu_type: Type of menu detected.
        options: List of option labels extracted from the menu.
        menu_line: The full line containing the menu.
    """

    menu_type: MenuType
    options: List[str]
    menu_line: str


def match_apc_menu(text: str) -> Optional[MenuPatternMatch]:
    """Match [A][P][C] style menus (Advanced/Party/Continue).

    Also matches generic [X] bracket-letter menus with 2+ options.

    Args:
        text: Text to search for menu patterns.

    Returns:
        MenuPatternMatch if found, None otherwise.
    """
    matches = list(_APC_PATTERN.finditer(text))

    if len(matches) >= 2:
        letters = [m.group(1).upper() for m in matches]
        options = [m.group(2).strip() for m in matches]

        start_pos = matches[0].start()
        end_pos = matches[-1].end()
        menu_segment = text[start_pos:end_pos]

        # All matched letters are already uppercase A-Z from regex
        return MenuPatternMatch(
            menu_type=MenuType.APC,
            options=options,
            menu_line=menu_segment.strip(),
        )

    return None


def match_yvn_menu(text: str) -> Optional[MenuPatternMatch]:
    """Match [Y][V][N] style menus (Yes/View/No).

    Args:
        text: Text to search for menu patterns.

    Returns:
        MenuPatternMatch if found, None otherwise.
    """
    matches = list(_YVN_PATTERN.finditer(text))

    if len(matches) >= 2:
        letters = [m.group(1).upper() for m in matches]
        options = [m.group(2).strip() for m in matches]

        # Must have Y and N, V is optional
        if "Y" in letters and "N" in letters:
            start_pos = matches[0].start()
            end_pos = matches[-1].end()
            menu_segment = text[start_pos:end_pos]

            return MenuPatternMatch(
                menu_type=MenuType.YVN,
                options=options,
                menu_line=menu_segment.strip(),
            )

    return None


def match_numbered_menu(text: str) -> Optional[MenuPatternMatch]:
    """Match [1][2][3] numbered option menus.

    Args:
        text: Text to search for menu patterns.

    Returns:
        MenuPatternMatch if found, None otherwise.
    """
    matches = list(_NUMBERED_PATTERN.finditer(text))

    if len(matches) >= 2:
        numbers = [int(m.group(1)) for m in matches]
        options = [m.group(2).strip() for m in matches]

        # Check for sequential or reasonable numbering
        if all(n > 0 for n in numbers):
            start_pos = matches[0].start()
            end_pos = matches[-1].end()
            menu_segment = text[start_pos:end_pos]

            return MenuPatternMatch(
                menu_type=MenuType.NUMBERED,
                options=options,
                menu_line=menu_segment.strip(),
            )

    return None


def match_exit_menu(text: str) -> Optional[MenuPatternMatch]:
    """Match [E] Exit pattern.

    Args:
        text: Text to search for exit menu.

    Returns:
        MenuPatternMatch if found, None otherwise.
    """
    match = _EXIT_PATTERN.search(text)

    if match:
        option = match.group(1).strip()
        return MenuPatternMatch(
            menu_type=MenuType.EXIT,
            options=[option],
            menu_line=match.group(0).strip(),
        )

    return None


def find_menu_patterns(text: str) -> List[MenuPatternMatch]:
    """Find all menu patterns in text, sorted by relevance.

    Tries all menu pattern matchers and returns matches sorted by
    specificity (more specific menu types first).

    Args:
        text: Text to search for menu patterns.

    Returns:
        List of MenuPatternMatch objects, sorted by relevance.
    """
    matches: List[MenuPatternMatch] = []

    # Try each matcher in order of specificity
    # YVN and Exit are most specific
    yvn_match = match_yvn_menu(text)
    if yvn_match:
        matches.append(yvn_match)

    exit_match = match_exit_menu(text)
    if exit_match:
        matches.append(exit_match)

    numbered_match = match_numbered_menu(text)
    if numbered_match:
        matches.append(numbered_match)

    # APC is more general (matches any bracket-letter pattern)
    apc_match = match_apc_menu(text)
    if apc_match:
        # Only add if not already matched by YVN
        if not yvn_match:
            matches.append(apc_match)

    # Sort by specificity: YVN > EXIT > NUMBERED > APC
    type_priority = {
        MenuType.YVN: 0,
        MenuType.EXIT: 1,
        MenuType.NUMBERED: 2,
        MenuType.APC: 3,
        MenuType.AGENT: 4,
        MenuType.UNKNOWN: 5,
    }

    matches.sort(key=lambda m: type_priority.get(m.menu_type, 99))

    return matches


# =============================================================================
# Confidence Scoring (Task 4)
# =============================================================================


def score_structural_markers(menu_line: str) -> int:
    """Score based on structural markers (brackets, separators).

    Full points (30) for consistent bracket formatting.
    Reduced points for inconsistent or missing brackets.

    Args:
        menu_line: The menu line to score.

    Returns:
        Score from 0-30.
    """
    max_score = 30

    # Count bracket pairs [X]
    bracket_matches = _BRACKET_PATTERN.findall(menu_line)

    if not bracket_matches:
        return 0

    # More brackets = more structural markers = higher score
    num_brackets = len(bracket_matches)

    if num_brackets >= 3:
        return max_score
    elif num_brackets == 2:
        return 25
    else:
        return 15


def score_position_validation(text: str, menu_line: str) -> int:
    """Score based on menu position in output.

    Full points (20) for menu at end of output.
    Reduced points for embedded menus.

    Args:
        text: Full text containing the menu.
        menu_line: The menu line to validate.

    Returns:
        Score from 0-20.
    """
    max_score = 20

    # Check if menu is at end of text
    text_stripped = text.strip()
    menu_stripped = menu_line.strip()

    if text_stripped.endswith(menu_stripped):
        return max_score

    # Check if menu is on its own line
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if menu_stripped in line:
            # Is this the last non-empty line?
            remaining_lines = [l.strip() for l in lines[i + 1 :] if l.strip()]
            if not remaining_lines:
                return max_score
            # Otherwise, give partial credit for being on own line
            return 10

    # Menu embedded in text
    return 5


def score_option_count(options: List[str]) -> int:
    """Score based on number of options.

    Full points (20) for 2-4 options (ideal).
    Reduced points for too few or too many options.

    Args:
        options: List of menu options.

    Returns:
        Score from 0-20.
    """
    max_score = 20
    num_options = len(options)

    if num_options == 0:
        return 0

    # 2-4 options is ideal
    if 2 <= num_options <= 4:
        return max_score

    # Single option (like [E] Exit)
    if num_options == 1:
        return 10

    # 5 options
    if num_options == 5:
        return 15

    # More than 5 options - progressively less likely to be a menu
    return max(5, max_score - (num_options - 4) * 3)


def score_pattern_match(match: MenuPatternMatch) -> int:
    """Score based on pattern match strength.

    Full points (30) for recognized menu types.
    Reduced points for unknown types.

    Args:
        match: The pattern match result.

    Returns:
        Score from 0-30.
    """
    max_score = 30

    # Known menu types get full points
    known_types = {MenuType.APC, MenuType.YVN, MenuType.NUMBERED, MenuType.EXIT, MenuType.AGENT}

    if match.menu_type in known_types:
        return max_score

    # Unknown type gets reduced points
    return 15


def calculate_confidence(
    text: str, match: MenuPatternMatch
) -> tuple[int, Dict[str, int]]:
    """Calculate overall confidence score with breakdown.

    Combines all scoring components:
    - Structural markers (30 pts max)
    - Position validation (20 pts max)
    - Option count (20 pts max)
    - Pattern match strength (30 pts max)

    Total max: 100 points.

    Args:
        text: Full text containing the menu.
        match: The pattern match result.

    Returns:
        Tuple of (total_confidence, breakdown_dict).
    """
    breakdown = {
        "structural_markers": score_structural_markers(match.menu_line),
        "position_validation": score_position_validation(text, match.menu_line),
        "option_count": score_option_count(match.options),
        "pattern_match": score_pattern_match(match),
    }

    total = sum(breakdown.values())

    # Cap at 100
    total = min(100, total)

    return total, breakdown


# =============================================================================
# Threshold Logic (Task 5)
# =============================================================================


def apply_threshold(
    confidence: int,
    breakdown: Dict[str, int],
    match: MenuPatternMatch,
    raw_input: str,
) -> MenuDetectionResult:
    """Apply the 70-point threshold to determine if menu is detected.

    Args:
        confidence: Total confidence score (0-100).
        breakdown: Dict showing confidence score breakdown.
        match: The pattern match result.
        raw_input: Original input text.

    Returns:
        MenuDetectionResult with appropriate detection status.
    """
    if confidence >= CONFIDENCE_THRESHOLD:
        return MenuDetectionResult.detected(
            confidence=confidence,
            menu_type=match.menu_type,
            options=match.options,
            breakdown=breakdown,
            raw_input=raw_input,
        )
    else:
        return MenuDetectionResult.not_detected(
            confidence=confidence,
            breakdown=breakdown,
            raw_input=raw_input,
        )


# =============================================================================
# Main Entry Point (Task 6)
# =============================================================================


def detect_menu(text: str) -> MenuDetectionResult:
    """Main entry point for menu detection.

    Implements the full detection pipeline:
    1. Handle edge cases (empty input)
    2. Find potential menu patterns
    3. Check false positive guards
    4. Calculate confidence score
    5. Apply threshold and return result

    Args:
        text: The workflow output text to analyze.

    Returns:
        MenuDetectionResult with detection status, confidence, and details.
    """
    # Handle edge cases
    if not text or not text.strip():
        return MenuDetectionResult.not_detected(
            confidence=0,
            breakdown={},
            raw_input=text or "",
        )

    # Find potential menu patterns
    matches = find_menu_patterns(text)

    if not matches:
        return MenuDetectionResult.not_detected(
            confidence=0,
            breakdown={},
            raw_input=text,
        )

    # Use the best match (first one after sorting)
    best_match = matches[0]

    # Check false positive guards
    guard_triggered = check_guards(text, best_match.menu_line)

    if guard_triggered:
        return MenuDetectionResult.blocked(
            guard=guard_triggered,
            raw_input=text,
        )

    # Calculate confidence score
    confidence, breakdown = calculate_confidence(text, best_match)

    # Apply threshold and return result
    return apply_threshold(
        confidence=confidence,
        breakdown=breakdown,
        match=best_match,
        raw_input=text,
    )
