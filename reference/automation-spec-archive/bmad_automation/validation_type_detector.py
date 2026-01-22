"""Validation Type Detector for BMAD Automation.

This module provides the ValidationTypeResult dataclass and ValidationType enum
that form the foundation of the BMAD Automation validation type detection system.

The Validation Type Detector identifies which validation approach a BMAD workflow
uses (verdict-based, error-based, checklist-based, custom, or unknown) and provides
metadata about the detected patterns.

Component: Validation Type Detector (Tier 1 - No dependencies)
Story: 1.1 - Validation Type Detection
Epic: 1 - Foundation Validation
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


# =============================================================================
# Confidence Calculation Constants
# =============================================================================

# Verdict-based confidence
VERDICT_BASE_CONFIDENCE = 0.5
VERDICT_MULTI_TYPE_BONUS_PER_TYPE = 0.1
VERDICT_MULTI_TYPE_BONUS_MAX = 0.2
VERDICT_PAIR_BONUS = 0.2
VERDICT_MATCH_COUNT_BONUS_PER_MATCH = 0.05
VERDICT_MATCH_COUNT_BONUS_MAX = 0.15

# Error-based confidence
ERROR_BASE_CONFIDENCE = 0.6
ERROR_ZERO_BONUS = 0.15
ERROR_MULTI_MATCH_BONUS_PER_MATCH = 0.05
ERROR_MULTI_MATCH_BONUS_MAX = 0.15
ERROR_NON_ZERO_PENALTY = -0.1
ERROR_MIN_CONFIDENCE = 0.5

# Checklist-based confidence
CHECKLIST_BASE_CONFIDENCE = 0.5
CHECKLIST_ITEM_COUNT_BONUS_PER_ITEM = 0.05
CHECKLIST_ITEM_COUNT_BONUS_MAX = 0.15
CHECKLIST_COMPLETION_BONUS_MULTIPLIER = 0.25


# =============================================================================
# Verdict Pattern Definitions (Task 2)
# =============================================================================

# Regex patterns for verdict-based validation detection
# Each category contains compiled regex patterns with word boundaries to avoid
# false positives like "passport" matching "pass"

VERDICT_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    # PASS/FAIL variants (Subtask 2.1)
    "pass_fail": [
        re.compile(r"\bPASS(?:ED)?\b", re.IGNORECASE),
        re.compile(r"\bFAIL(?:ED)?\b", re.IGNORECASE),
    ],
    # APPROVED/REJECTED variants (Subtask 2.2)
    "approved_rejected": [
        re.compile(r"\bAPPROV(?:E|ED|AL)\b", re.IGNORECASE),
        re.compile(r"\bREJECT(?:ED)?\b", re.IGNORECASE),
        re.compile(r"\bCHANGES\s+REQUESTED\b", re.IGNORECASE),
        re.compile(r"\bBLOCKED\b", re.IGNORECASE),
    ],
    # READY/NOT_READY variants (Subtask 2.3)
    "ready_not_ready": [
        re.compile(r"\bREADY\b", re.IGNORECASE),
        re.compile(r"\bNOT[\s_]READY\b", re.IGNORECASE),
        re.compile(r"\bNEEDS[\s_]WORK\b", re.IGNORECASE),
        re.compile(r"\bCONCERNS\b", re.IGNORECASE),
    ],
}


# =============================================================================
# Error Pattern Definitions (Task 3)
# =============================================================================

# Regex patterns for error-based validation detection
# These patterns identify error counting and zero-error success criteria

ERROR_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    # "0 errors", "zero errors", "no errors" variants (Subtask 3.1)
    "zero_errors": [
        re.compile(r"\b0\s+(?:blocking\s+)?errors?\b", re.IGNORECASE),
        re.compile(r"\bzero\s+errors?\b", re.IGNORECASE),
        re.compile(r"\bno\s+errors?\b", re.IGNORECASE),
    ],
    # "no issues", "0 issues", "no problems" variants (Subtask 3.2)
    "no_issues": [
        re.compile(r"\b0\s+(?:issues?|problems?)\b", re.IGNORECASE),
        re.compile(r"\bno\s+(?:issues?|problems?)\b", re.IGNORECASE),
        re.compile(r"\bzero\s+(?:issues?|problems?)\b", re.IGNORECASE),
    ],
    # Error count patterns like "3 errors", "5 errors found" (Subtask 3.3)
    "error_count": [
        re.compile(r"\b(\d+)\s+errors?\s*(?:found)?\b", re.IGNORECASE),
        re.compile(r"\bfound\s+(\d+)\s+errors?\b", re.IGNORECASE),
    ],
}


# =============================================================================
# Checklist Pattern Definitions (Task 4)
# =============================================================================

# Regex patterns for checklist-based validation detection
# These patterns identify markdown checkbox items [ ] and [x]

CHECKLIST_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    # Unchecked items: - [ ] or * [ ] (Subtask 4.1)
    "unchecked": [
        re.compile(r"^[\s]*[-*]\s*\[\s\]", re.MULTILINE),
    ],
    # Checked items: - [x] or - [X] or * [x] (Subtask 4.2)
    "checked": [
        re.compile(r"^[\s]*[-*]\s*\[[xX]\]", re.MULTILINE),
    ],
}


# =============================================================================
# Confidence Threshold (Task 5)
# =============================================================================

# Default confidence threshold for validation type detection (Subtask 5.1)
# Results below this threshold should be treated as unknown/uncertain
CONFIDENCE_THRESHOLD: float = 0.5


class ValidationType(Enum):
    """Enumeration of validation types supported by BMAD workflows.

    Each validation type has different success criteria:
    - VERDICT_BASED: Success determined by PASS/FAIL, APPROVED/REJECTED, etc.
    - ERROR_BASED: Success determined by error count (e.g., "0 errors")
    - CHECKLIST_BASED: Success determined by checkbox completion
    - CUSTOM: User-defined validation patterns from workflow frontmatter
    - UNKNOWN: No recognizable validation pattern detected
    """

    VERDICT_BASED = "verdict-based"
    ERROR_BASED = "error-based"
    CHECKLIST_BASED = "checklist-based"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


# =============================================================================
# Custom Pattern Dataclass (Story 1.4, Task 1)
# =============================================================================


@dataclass
class CustomPattern:
    """Custom validation pattern definition from workflow frontmatter.

    This dataclass represents user-defined validation patterns that can be
    specified in workflow configuration to define custom success criteria.

    Attributes:
        success_pattern: Regex pattern indicating successful validation.
        failure_pattern: Regex pattern indicating failed validation.
        warning_pattern: Optional regex pattern indicating warnings.
        case_sensitive: Whether pattern matching is case-sensitive (default False).
    """

    success_pattern: str
    failure_pattern: str
    warning_pattern: str | None = None
    case_sensitive: bool = False


@dataclass
class ValidationTypeResult:
    """Result of validation type detection for a BMAD workflow.

    This dataclass contains the detected validation type along with
    supporting metadata including the patterns matched, confidence score,
    and type-specific details.

    Attributes:
        validation_type: The detected ValidationType enum value.
        patterns: List of regex patterns or strings that were matched.
        confidence: Confidence score from 0.0 to 1.0 indicating detection certainty.
        details: Type-specific details (e.g., checkbox counts, verdict types).
        custom_patterns: CustomPattern instance for custom validation types.
    """

    validation_type: ValidationType
    patterns: list[str] = field(default_factory=list)
    confidence: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    custom_patterns: CustomPattern | None = None

    # Factory methods for each validation type

    @classmethod
    def verdict_based(
        cls,
        patterns: list[str],
        confidence: float,
        verdict_type: str,
    ) -> ValidationTypeResult:
        """Create a verdict-based validation result.

        Args:
            patterns: The verdict patterns detected (e.g., ["PASS", "FAIL"]).
            confidence: Confidence score from 0.0 to 1.0.
            verdict_type: Type of verdict (e.g., "pass_fail", "approved_rejected").

        Returns:
            ValidationTypeResult configured for verdict-based validation.
        """
        return cls(
            validation_type=ValidationType.VERDICT_BASED,
            patterns=patterns,
            confidence=confidence,
            details={"verdict_type": verdict_type},
        )

    @classmethod
    def error_based(
        cls,
        patterns: list[str],
        confidence: float,
        error_count: int,
    ) -> ValidationTypeResult:
        """Create an error-based validation result.

        Args:
            patterns: The error patterns detected (e.g., ["0 errors"]).
            confidence: Confidence score from 0.0 to 1.0.
            error_count: Number of errors detected.

        Returns:
            ValidationTypeResult configured for error-based validation.
        """
        return cls(
            validation_type=ValidationType.ERROR_BASED,
            patterns=patterns,
            confidence=confidence,
            details={"error_count": error_count},
        )

    @classmethod
    def checklist_based(
        cls,
        patterns: list[str],
        confidence: float,
        total_items: int,
        checked_items: int,
    ) -> ValidationTypeResult:
        """Create a checklist-based validation result.

        Args:
            patterns: The checkbox patterns detected (e.g., ["[ ]", "[x]"]).
            confidence: Confidence score from 0.0 to 1.0.
            total_items: Total number of checkbox items.
            checked_items: Number of checked items.

        Returns:
            ValidationTypeResult configured for checklist-based validation.
        """
        completion_percentage = (
            (checked_items / total_items * 100) if total_items > 0 else 0.0
        )
        return cls(
            validation_type=ValidationType.CHECKLIST_BASED,
            patterns=patterns,
            confidence=confidence,
            details={
                "total_items": total_items,
                "checked_items": checked_items,
                "completion_percentage": completion_percentage,
            },
        )

    @classmethod
    def custom(
        cls,
        patterns: list[str],
        confidence: float,
        custom_config: dict[str, Any],
        custom_patterns: CustomPattern | None = None,
    ) -> ValidationTypeResult:
        """Create a custom validation result.

        Args:
            patterns: The custom patterns detected.
            confidence: Confidence score from 0.0 to 1.0.
            custom_config: Custom configuration from workflow frontmatter.
            custom_patterns: Optional CustomPattern instance with pattern details.

        Returns:
            ValidationTypeResult configured for custom validation.
        """
        return cls(
            validation_type=ValidationType.CUSTOM,
            patterns=patterns,
            confidence=confidence,
            details={"custom_config": custom_config},
            custom_patterns=custom_patterns,
        )

    @classmethod
    def unknown(cls) -> ValidationTypeResult:
        """Create an unknown validation result.

        Used when no recognizable validation pattern is detected.

        Returns:
            ValidationTypeResult with UNKNOWN type and zero confidence.
        """
        return cls(
            validation_type=ValidationType.UNKNOWN,
            patterns=[],
            confidence=0.0,
            details={},
        )

    # Serialization methods

    def to_dict(self) -> dict[str, Any]:
        """Convert ValidationTypeResult to a dictionary.

        Returns:
            Dictionary representation with validation_type as string value.
        """
        result = {
            "validation_type": self.validation_type.value,
            "patterns": self.patterns,
            "confidence": self.confidence,
            "details": self.details,
        }
        if self.custom_patterns is not None:
            result["custom_patterns"] = {
                "success_pattern": self.custom_patterns.success_pattern,
                "failure_pattern": self.custom_patterns.failure_pattern,
                "warning_pattern": self.custom_patterns.warning_pattern,
                "case_sensitive": self.custom_patterns.case_sensitive,
            }
        else:
            result["custom_patterns"] = None
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ValidationTypeResult:
        """Create ValidationTypeResult from a dictionary.

        Args:
            data: Dictionary with validation_type, patterns, confidence, details.

        Returns:
            ValidationTypeResult instance.

        Raises:
            ValueError: If validation_type string is not a valid ValidationType.
        """
        validation_type_str = data["validation_type"]

        # Map string to enum
        type_mapping = {vt.value: vt for vt in ValidationType}
        if validation_type_str not in type_mapping:
            raise ValueError(
                f"Invalid validation type: '{validation_type_str}'. "
                f"Valid types are: {list(type_mapping.keys())}"
            )

        # Deserialize custom_patterns if present
        custom_patterns = None
        custom_patterns_data = data.get("custom_patterns")
        if custom_patterns_data is not None:
            custom_patterns = CustomPattern(
                success_pattern=custom_patterns_data["success_pattern"],
                failure_pattern=custom_patterns_data["failure_pattern"],
                warning_pattern=custom_patterns_data.get("warning_pattern"),
                case_sensitive=custom_patterns_data.get("case_sensitive", False),
            )

        return cls(
            validation_type=type_mapping[validation_type_str],
            patterns=data.get("patterns", []),
            confidence=data.get("confidence", 0.0),
            details=data.get("details", {}),
            custom_patterns=custom_patterns,
        )


def detect_validation_type(content: str) -> ValidationTypeResult:
    """Detect the validation type of a BMAD workflow from its content.

    This is the main entry point for validation type detection. It analyzes
    workflow content and returns the detected validation type with metadata.

    Priority order (Subtask 6.1): verdict > error > checklist
    Priority takes precedence when a type is detected above threshold.
    Confidence scoring helps when priority type is below threshold (Subtask 6.2, 6.3).

    Args:
        content: The workflow file content (YAML or Markdown).

    Returns:
        ValidationTypeResult with detected type, patterns, confidence, and details.
    """
    # Handle empty/whitespace content
    if not content or not content.strip():
        return ValidationTypeResult.unknown()

    # Check in priority order (Subtask 6.1)
    # Return the first type detected above confidence threshold
    # Priority: verdict > error > checklist

    # Check verdict patterns first (highest priority)
    verdict_result = detect_verdict_patterns(content)
    if verdict_result is not None and verdict_result.confidence >= CONFIDENCE_THRESHOLD:
        return verdict_result

    # Check error patterns second
    error_result = detect_error_patterns(content)
    if error_result is not None and error_result.confidence >= CONFIDENCE_THRESHOLD:
        return error_result

    # Check checklist patterns last (lowest priority)
    checklist_result = detect_checklist_patterns(content)
    if checklist_result is not None and checklist_result.confidence >= CONFIDENCE_THRESHOLD:
        return checklist_result

    # If any results below threshold, return highest-confidence one (Subtask 6.2, 6.3)
    results = [r for r in [verdict_result, error_result, checklist_result] if r is not None]
    if results:
        return max(results, key=lambda r: r.confidence)

    # No patterns detected
    return ValidationTypeResult.unknown()


def _strip_code_blocks(content: str) -> str:
    """Remove code blocks from content to avoid false positive pattern matches.

    Patterns inside code blocks (```...```) should not be considered as
    validation patterns since they're likely examples or documentation.

    Args:
        content: The content to process.

    Returns:
        Content with code blocks removed.
    """
    # Remove fenced code blocks (```...```)
    code_block_pattern = re.compile(r"```[\s\S]*?```", re.MULTILINE)
    return code_block_pattern.sub("", content)


def detect_verdict_patterns(content: str) -> ValidationTypeResult | None:
    """Detect verdict-based validation patterns in workflow content.

    This function scans content for verdict patterns like PASS/FAIL,
    APPROVED/REJECTED, READY/NOT_READY and returns a ValidationTypeResult
    if patterns are found.

    Args:
        content: The workflow file content to analyze.

    Returns:
        ValidationTypeResult if verdict patterns found, None otherwise.
    """
    if not content or not content.strip():
        return None

    # Strip code blocks to avoid false positives
    clean_content = _strip_code_blocks(content)

    # Track matches per verdict type
    matches_by_type: dict[str, list[str]] = {}
    total_match_count = 0

    for verdict_type, patterns in VERDICT_PATTERNS.items():
        matches_by_type[verdict_type] = []
        for pattern in patterns:
            found = pattern.findall(clean_content)
            if found:
                matches_by_type[verdict_type].extend(found)
                total_match_count += len(found)

    # No matches found
    if total_match_count == 0:
        return None

    # Determine dominant verdict type (the one with most matches)
    dominant_type = max(matches_by_type.keys(), key=lambda t: len(matches_by_type[t]))

    # If dominant type has no matches, check others
    if not matches_by_type[dominant_type]:
        # Find first type with matches
        for verdict_type, matches in matches_by_type.items():
            if matches:
                dominant_type = verdict_type
                break
        else:
            return None

    # Collect all matched patterns as strings
    all_patterns = []
    for matches in matches_by_type.values():
        all_patterns.extend(matches)

    # Remove duplicates while preserving order
    unique_patterns = list(dict.fromkeys(all_patterns))

    # Calculate confidence based on match characteristics
    confidence = _calculate_verdict_confidence(matches_by_type, clean_content)

    return ValidationTypeResult.verdict_based(
        patterns=unique_patterns,
        confidence=confidence,
        verdict_type=dominant_type,
    )


def _calculate_verdict_confidence(
    matches_by_type: dict[str, list[str]],
    content: str,
) -> float:
    """Calculate confidence score for verdict pattern detection.

    Confidence is higher when:
    - Multiple patterns are found (indicates intentional verdict system)
    - Paired patterns exist (e.g., both PASS and FAIL)
    - Patterns appear in structured contexts

    Args:
        matches_by_type: Dictionary of verdict types to their matches.
        content: The cleaned content (code blocks removed).

    Returns:
        Confidence score from 0.0 to 1.0.
    """
    # Count total unique patterns matched
    total_unique = sum(len(set(m)) for m in matches_by_type.values())

    # Bonus for multiple pattern types
    types_with_matches = sum(1 for m in matches_by_type.values() if m)
    multi_type_bonus = min(
        VERDICT_MULTI_TYPE_BONUS_PER_TYPE * (types_with_matches - 1),
        VERDICT_MULTI_TYPE_BONUS_MAX,
    )

    # Bonus for paired patterns within same type (e.g., PASS and FAIL both present)
    pair_bonus = 0.0
    for verdict_type, matches in matches_by_type.items():
        unique_matches = set(m.upper() for m in matches)
        # Check for common pairs
        if verdict_type == "pass_fail":
            has_pass = any("PASS" in m for m in unique_matches)
            has_fail = any("FAIL" in m for m in unique_matches)
            if has_pass and has_fail:
                pair_bonus = max(pair_bonus, VERDICT_PAIR_BONUS)
        elif verdict_type == "approved_rejected":
            has_approve = any("APPROV" in m for m in unique_matches)
            has_reject = any("REJECT" in m for m in unique_matches)
            if has_approve and has_reject:
                pair_bonus = max(pair_bonus, VERDICT_PAIR_BONUS)
        elif verdict_type == "ready_not_ready":
            has_ready = any(m == "READY" for m in unique_matches)
            has_not_ready = any("NOT" in m for m in unique_matches)
            if has_ready and has_not_ready:
                pair_bonus = max(pair_bonus, VERDICT_PAIR_BONUS)

    # Bonus for multiple unique matches
    match_count_bonus = min(
        VERDICT_MATCH_COUNT_BONUS_PER_MATCH * (total_unique - 1),
        VERDICT_MATCH_COUNT_BONUS_MAX,
    )

    # Calculate final confidence
    confidence = (
        VERDICT_BASE_CONFIDENCE + multi_type_bonus + pair_bonus + match_count_bonus
    )

    # Cap at 1.0
    return min(confidence, 1.0)


def detect_error_patterns(content: str) -> ValidationTypeResult | None:
    """Detect error-based validation patterns in workflow content.

    This function scans content for error patterns like "0 errors",
    "no issues", or specific error counts and returns a ValidationTypeResult
    if patterns are found.

    Args:
        content: The workflow file content to analyze.

    Returns:
        ValidationTypeResult if error patterns found, None otherwise.
    """
    if not content or not content.strip():
        return None

    # Strip code blocks to avoid false positives
    clean_content = _strip_code_blocks(content)

    # Track matches and extract error counts
    all_patterns: list[str] = []
    error_counts: list[int] = []
    match_count = 0

    # Check zero_errors patterns (Subtask 3.1)
    for pattern in ERROR_PATTERNS["zero_errors"]:
        matches = pattern.findall(clean_content)
        if matches:
            all_patterns.extend(matches if isinstance(matches[0], str) else [m for m in matches])
            error_counts.append(0)
            match_count += len(matches)

    # Check no_issues patterns (Subtask 3.2)
    for pattern in ERROR_PATTERNS["no_issues"]:
        matches = pattern.findall(clean_content)
        if matches:
            all_patterns.extend(matches if isinstance(matches[0], str) else [m for m in matches])
            error_counts.append(0)
            match_count += len(matches)

    # Check error_count patterns (Subtask 3.3)
    for pattern in ERROR_PATTERNS["error_count"]:
        matches = pattern.findall(clean_content)
        for match in matches:
            # Extract the number from the match (could be a group or full match)
            if isinstance(match, tuple):
                count = int(match[0]) if match[0] else 0
            else:
                count = int(match) if match.isdigit() else 0
            error_counts.append(count)
            all_patterns.append(pattern.pattern)
            match_count += 1

    # No matches found
    if match_count == 0:
        return None

    # Determine the primary error count (prefer 0 if found, otherwise min count)
    primary_error_count = 0 if 0 in error_counts else min(error_counts) if error_counts else 0

    # Remove duplicates while preserving order
    unique_patterns = list(dict.fromkeys(all_patterns))

    # Calculate confidence
    confidence = _calculate_error_confidence(error_counts, match_count)

    return ValidationTypeResult.error_based(
        patterns=unique_patterns,
        confidence=confidence,
        error_count=primary_error_count,
    )


def _calculate_error_confidence(error_counts: list[int], match_count: int) -> float:
    """Calculate confidence score for error pattern detection.

    Confidence is higher when:
    - Zero errors detected (indicates clean validation)
    - Multiple error-related patterns found
    - Consistent error counts across patterns

    Args:
        error_counts: List of error counts found in content.
        match_count: Total number of pattern matches.

    Returns:
        Confidence score from 0.0 to 1.0.
    """
    # Bonus for zero errors (high confidence success indicator)
    zero_bonus = ERROR_ZERO_BONUS if 0 in error_counts else 0.0

    # Bonus for multiple matches (indicates intentional error reporting)
    multi_match_bonus = min(
        ERROR_MULTI_MATCH_BONUS_PER_MATCH * (match_count - 1),
        ERROR_MULTI_MATCH_BONUS_MAX,
    )

    # Penalty for non-zero errors (less certain about success)
    non_zero_penalty = 0.0
    if error_counts and all(c > 0 for c in error_counts):
        non_zero_penalty = ERROR_NON_ZERO_PENALTY

    # Calculate final confidence
    confidence = (
        ERROR_BASE_CONFIDENCE + zero_bonus + multi_match_bonus + non_zero_penalty
    )

    # Cap at 1.0, floor at minimum
    return min(max(confidence, ERROR_MIN_CONFIDENCE), 1.0)


def detect_checklist_patterns(content: str) -> ValidationTypeResult | None:
    """Detect checklist-based validation patterns in workflow content.

    This function scans content for markdown checkbox patterns like
    `- [ ]` (unchecked) and `- [x]` (checked) and returns a ValidationTypeResult
    with checkbox counts and completion percentage.

    Args:
        content: The workflow file content to analyze.

    Returns:
        ValidationTypeResult if checklist patterns found, None otherwise.
    """
    if not content or not content.strip():
        return None

    # Strip code blocks to avoid false positives
    clean_content = _strip_code_blocks(content)

    # Count unchecked items (Subtask 4.1)
    unchecked_count = 0
    for pattern in CHECKLIST_PATTERNS["unchecked"]:
        matches = pattern.findall(clean_content)
        unchecked_count += len(matches)

    # Count checked items (Subtask 4.2)
    checked_count = 0
    for pattern in CHECKLIST_PATTERNS["checked"]:
        matches = pattern.findall(clean_content)
        checked_count += len(matches)

    # Total checkbox items (Subtask 4.3)
    total_items = unchecked_count + checked_count

    # No checklist found
    if total_items == 0:
        return None

    # Build pattern list for result
    patterns: list[str] = []
    if unchecked_count > 0:
        patterns.append("[ ]")
    if checked_count > 0:
        patterns.append("[x]")

    # Calculate confidence (Subtask 4.4 confidence portion)
    confidence = _calculate_checklist_confidence(total_items, checked_count)

    return ValidationTypeResult.checklist_based(
        patterns=patterns,
        confidence=confidence,
        total_items=total_items,
        checked_items=checked_count,
    )


def _calculate_checklist_confidence(total_items: int, checked_items: int) -> float:
    """Calculate confidence score for checklist pattern detection.

    Confidence is higher when:
    - More total items exist (indicates intentional checklist)
    - Higher completion percentage (indicates progress tracking)

    Args:
        total_items: Total number of checkbox items.
        checked_items: Number of checked items.

    Returns:
        Confidence score from 0.0 to 1.0.
    """
    # Bonus for having multiple items (indicates real checklist vs single item)
    item_count_bonus = min(
        CHECKLIST_ITEM_COUNT_BONUS_PER_ITEM * (total_items - 1),
        CHECKLIST_ITEM_COUNT_BONUS_MAX,
    )

    # Bonus based on completion percentage
    completion_pct = (checked_items / total_items) if total_items > 0 else 0
    completion_bonus = completion_pct * CHECKLIST_COMPLETION_BONUS_MULTIPLIER

    # Calculate final confidence
    confidence = CHECKLIST_BASE_CONFIDENCE + item_count_bonus + completion_bonus

    # Cap at 1.0
    return min(confidence, 1.0)


# =============================================================================
# Workflow File Parsing (Task 7)
# =============================================================================


def parse_workflow_file(file_path: Path) -> tuple[str | None, dict[str, Any] | None]:
    """Parse a workflow file and extract content and frontmatter.

    Supports both .yaml and .md workflow file formats. For Markdown files,
    extracts YAML frontmatter if present.

    Args:
        file_path: Path to the workflow file.

    Returns:
        Tuple of (content, frontmatter) where:
        - content: The full file content (or markdown body if frontmatter present)
        - frontmatter: Parsed YAML frontmatter dict, None if not present
        Returns (None, None) if file doesn't exist or can't be read.
    """
    if not file_path.exists():
        return (None, None)

    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, IOError):
        return (None, None)

    # Handle empty file
    if not content:
        return ("", None)

    # For .yaml files, return content as-is with no frontmatter parsing
    if file_path.suffix.lower() in (".yaml", ".yml"):
        return (content, None)

    # For .md files, check for YAML frontmatter
    if file_path.suffix.lower() == ".md":
        return _parse_markdown_with_frontmatter(content)

    # Other formats, return content as-is
    return (content, None)


def _parse_markdown_with_frontmatter(content: str) -> tuple[str, dict[str, Any] | None]:
    """Parse markdown content and extract YAML frontmatter if present.

    Frontmatter is expected to be at the start of the file, delimited by
    '---' on its own line.

    Args:
        content: The full markdown file content.

    Returns:
        Tuple of (body_content, frontmatter_dict).
    """
    # Check if content starts with frontmatter delimiter
    if not content.startswith("---"):
        return (content, None)

    # Find the closing delimiter
    lines = content.split("\n")
    end_index = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break

    if end_index is None:
        # No closing delimiter found, treat as no frontmatter
        return (content, None)

    # Extract frontmatter and body
    frontmatter_lines = lines[1:end_index]
    body_lines = lines[end_index + 1:]

    frontmatter_text = "\n".join(frontmatter_lines)
    body_text = "\n".join(body_lines)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if frontmatter is None:
            frontmatter = {}
    except yaml.YAMLError:
        frontmatter = {}

    return (body_text, frontmatter)


def detect_validation_type_from_file(file_path: Path) -> ValidationTypeResult:
    """Detect validation type from a workflow file.

    Reads the file, parses frontmatter, and detects the validation type.
    If custom validation is specified in frontmatter, uses that.
    Otherwise, uses content-based detection.

    Args:
        file_path: Path to the workflow file.

    Returns:
        ValidationTypeResult with detected type and metadata.
    """
    content, frontmatter = parse_workflow_file(file_path)

    # File doesn't exist or can't be read
    if content is None:
        return ValidationTypeResult.unknown()

    # Check for custom validation in frontmatter
    if frontmatter:
        custom_result = _check_custom_validation_frontmatter(frontmatter)
        if custom_result is not None:
            return custom_result

    # Use content-based detection
    return detect_validation_type(content)


def _check_custom_validation_frontmatter(
    frontmatter: dict[str, Any],
) -> ValidationTypeResult | None:
    """Check frontmatter for custom validation configuration.

    Args:
        frontmatter: Parsed YAML frontmatter dict.

    Returns:
        ValidationTypeResult if custom validation found, None otherwise.
    """
    validation_config = frontmatter.get("validation")
    if not validation_config:
        return None

    # Check if it's a custom validation type
    if isinstance(validation_config, dict):
        val_type = validation_config.get("type", "").lower()
        if val_type == "custom":
            # Parse custom patterns from frontmatter
            custom_pattern = parse_custom_patterns_from_frontmatter(frontmatter)

            if custom_pattern is not None:
                # Validate the custom pattern
                errors = validate_custom_pattern(custom_pattern)
                if errors:
                    # Return error result
                    return ValidationTypeResult(
                        validation_type=ValidationType.CUSTOM,
                        patterns=[],
                        confidence=0.0,
                        details={
                            "custom_config": validation_config,
                            "error": "invalid_pattern",
                            "validation_errors": errors,
                        },
                        custom_patterns=None,
                    )

                # Create patterns list from custom pattern
                patterns = [custom_pattern.success_pattern, custom_pattern.failure_pattern]
                if custom_pattern.warning_pattern:
                    patterns.append(custom_pattern.warning_pattern)

                return ValidationTypeResult.custom(
                    patterns=patterns,
                    confidence=1.0,  # Custom validation from frontmatter is explicit
                    custom_config=validation_config,
                    custom_patterns=custom_pattern,
                )
            else:
                # Custom type but missing patterns - return error
                return ValidationTypeResult(
                    validation_type=ValidationType.CUSTOM,
                    patterns=[],
                    confidence=0.0,
                    details={
                        "custom_config": validation_config,
                        "error": "invalid_pattern",
                        "validation_errors": ["success_pattern is required"],
                    },
                    custom_patterns=None,
                )

    return None


# =============================================================================
# Story 1.4: Custom Pattern Functions (Tasks 2-6)
# =============================================================================


def parse_custom_patterns_from_frontmatter(
    frontmatter: dict[str, Any] | None,
) -> CustomPattern | None:
    """Parse custom validation patterns from workflow frontmatter.

    Extracts success_pattern, failure_pattern, and optional warning_pattern
    and case_sensitive settings from the validation configuration.

    Args:
        frontmatter: Parsed YAML frontmatter dict, or None.

    Returns:
        CustomPattern instance if valid custom patterns found, None otherwise.
    """
    if frontmatter is None:
        return None

    validation_config = frontmatter.get("validation")
    if not validation_config:
        return None

    if not isinstance(validation_config, dict):
        return None

    val_type = validation_config.get("type", "").lower()
    if val_type != "custom":
        return None

    # Extract pattern fields
    success_pattern = validation_config.get("success_pattern", "")
    failure_pattern = validation_config.get("failure_pattern", "")

    # Don't create pattern if success_pattern is missing
    if not success_pattern:
        return None

    return CustomPattern(
        success_pattern=success_pattern,
        failure_pattern=failure_pattern,
        warning_pattern=validation_config.get("warning_pattern"),
        case_sensitive=validation_config.get("case_sensitive", False),
    )


def validate_custom_pattern(pattern: CustomPattern) -> list[str] | None:
    """Validate a custom pattern definition.

    Checks that required fields are present and that all patterns are valid
    regular expressions.

    Args:
        pattern: CustomPattern instance to validate.

    Returns:
        List of error messages if validation fails, None if valid.
    """
    errors: list[str] = []

    # Check required fields
    if not pattern.success_pattern:
        errors.append("success_pattern is required and cannot be empty")

    # Validate regex syntax for success_pattern
    if pattern.success_pattern:
        try:
            re.compile(pattern.success_pattern)
        except re.error as e:
            errors.append(f"success_pattern is invalid regex: {e}")

    # Validate regex syntax for failure_pattern
    if pattern.failure_pattern:
        try:
            re.compile(pattern.failure_pattern)
        except re.error as e:
            errors.append(f"failure_pattern is invalid regex: {e}")

    # Validate regex syntax for warning_pattern if provided
    if pattern.warning_pattern:
        try:
            re.compile(pattern.warning_pattern)
        except re.error as e:
            errors.append(f"warning_pattern is invalid regex: {e}")

    return errors if errors else None


def match_custom_patterns(
    content: str,
    pattern: CustomPattern,
) -> dict[str, Any]:
    """Match custom patterns against workflow content.

    Checks content for success, failure, and warning patterns.
    Failure patterns take precedence over success patterns.

    Args:
        content: The workflow output content to check.
        pattern: CustomPattern instance with patterns to match.

    Returns:
        Dictionary with 'status' ('success', 'failure', 'warning', 'unknown')
        and 'matched_pattern' (the pattern that matched).
    """
    flags = 0 if pattern.case_sensitive else re.IGNORECASE

    # Check failure pattern first (takes precedence)
    if pattern.failure_pattern:
        try:
            match = re.search(pattern.failure_pattern, content, flags)
            if match:
                return {
                    "status": "failure",
                    "matched_pattern": match.group(0),
                }
        except re.error:
            pass

    # Check warning pattern next
    if pattern.warning_pattern:
        try:
            match = re.search(pattern.warning_pattern, content, flags)
            if match:
                return {
                    "status": "warning",
                    "matched_pattern": match.group(0),
                }
        except re.error:
            pass

    # Check success pattern
    if pattern.success_pattern:
        try:
            match = re.search(pattern.success_pattern, content, flags)
            if match:
                return {
                    "status": "success",
                    "matched_pattern": match.group(0),
                }
        except re.error:
            pass

    # No pattern matched
    return {
        "status": "unknown",
        "matched_pattern": "",
    }


