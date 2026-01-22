"""Tier Suggester - Project Complexity Detection.

This module provides functionality to recommend appropriate project tiers (0-4)
based on user descriptions and codebase analysis.

Tier Definitions (from BMAD):
- Tier 0: Single Atomic Change (fix, bug, typo, patch, hotfix, tweak)
- Tier 1: Small Feature (small, simple, quick, minor, basic, straightforward)
- Tier 2: Medium Project (feature, component, module, service) - DEFAULT
- Tier 3: Complex System (platform, integration, complex, enterprise, multi-component)
- Tier 4: Enterprise/Regulated (compliance, regulated, audit, security-critical, healthcare, finance)

Examples:
    >>> suggest_tier("Fix the bug in login")
    TierSuggestion(tier=TIER_0, confidence=HIGH, matched_keywords=['fix', 'bug'], ...)

    >>> suggest_tier("Build a new integration platform")
    TierSuggestion(tier=TIER_3, confidence=HIGH, matched_keywords=['integration', 'platform'], ...)
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from .workflow_entry_wrapper import (
    ProjectType,
    ProjectTypeResult,
    detect_project_type,
    count_source_files,
)


# =============================================================================
# Enums
# =============================================================================


class ProjectTier(Enum):
    """Project complexity tier (0-4).

    Each tier represents a different level of project complexity,
    affecting validation depth and human checkpoints.

    Attributes:
        TIER_0: Single Atomic Change - minimal changes, single file
        TIER_1: Small Feature - small addition or change
        TIER_2: Medium Project - standard feature work (DEFAULT)
        TIER_3: Complex System - cross-cutting concerns
        TIER_4: Enterprise/Regulated - compliance requirements
    """

    TIER_0 = 0  # Single Atomic Change
    TIER_1 = 1  # Small Feature
    TIER_2 = 2  # Medium Project
    TIER_3 = 3  # Complex System
    TIER_4 = 4  # Enterprise/Regulated

    @property
    def description(self) -> str:
        """Get human-readable description for this tier."""
        descriptions = {
            ProjectTier.TIER_0: "Single Atomic Change - minimal change, single file",
            ProjectTier.TIER_1: "Small Feature - small addition or change",
            ProjectTier.TIER_2: "Medium Project - standard feature work",
            ProjectTier.TIER_3: "Complex System - cross-cutting concerns",
            ProjectTier.TIER_4: "Enterprise/Regulated - compliance requirements",
        }
        return descriptions.get(self, "Unknown tier")


class TierConfidence(Enum):
    """Confidence level in tier suggestion.

    Attributes:
        HIGH: >66% of keywords match a single tier
        MEDIUM: 34-66% of keywords match a single tier
        LOW: <34% or no keywords matched (uses default tier)
    """

    HIGH = "high"      # >66% keywords match single tier
    MEDIUM = "medium"  # 34-66% keywords match single tier
    LOW = "low"        # <34% or no keywords matched


# =============================================================================
# Constants
# =============================================================================


TIER_KEYWORDS: dict[ProjectTier, frozenset[str]] = {
    ProjectTier.TIER_0: frozenset({
        "fix", "bug", "typo", "patch", "hotfix", "tweak",
    }),
    ProjectTier.TIER_1: frozenset({
        "small", "simple", "quick", "minor", "basic", "straightforward",
    }),
    ProjectTier.TIER_2: frozenset({
        "feature", "component", "module", "service",
    }),
    ProjectTier.TIER_3: frozenset({
        "platform", "integration", "complex", "enterprise", "multi-component",
    }),
    ProjectTier.TIER_4: frozenset({
        "compliance", "regulated", "audit", "security-critical", "healthcare", "finance",
    }),
}

DEFAULT_TIER = ProjectTier.TIER_2

# Thresholds for confidence calculation
HIGH_CONFIDENCE_THRESHOLD = 0.66  # >66% = HIGH
MEDIUM_CONFIDENCE_THRESHOLD = 0.34  # 34-66% = MEDIUM, <34% = LOW

# Thresholds for codebase size adjustment
LARGE_CODEBASE_THRESHOLD = 100   # +1 tier for 100+ files
VERY_LARGE_CODEBASE_THRESHOLD = 500  # +2 tier for 500+ files


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class TierSuggestion:
    """Result of tier suggestion analysis.

    Attributes:
        tier: The suggested project tier (0-4)
        confidence: Confidence level of the suggestion (HIGH, MEDIUM, LOW)
        matched_keywords: List of keywords that matched for the suggested tier
        reasoning: Human-readable explanation of the suggestion
        all_matches: All keyword matches by tier (for transparency)
    """

    tier: ProjectTier
    confidence: TierConfidence
    matched_keywords: list[str]
    reasoning: str
    all_matches: dict[ProjectTier, list[str]] = field(default_factory=dict)

    @classmethod
    def default_suggestion(cls) -> "TierSuggestion":
        """Factory method for creating default Tier 2 suggestion with LOW confidence.

        Returns:
            TierSuggestion with TIER_2 and LOW confidence
        """
        return cls(
            tier=DEFAULT_TIER,
            confidence=TierConfidence.LOW,
            matched_keywords=[],
            reasoning="No keywords matched - using default tier",
            all_matches={},
        )

    @classmethod
    def from_analysis(
        cls,
        tier: ProjectTier,
        confidence: TierConfidence,
        all_matches: dict[ProjectTier, list[str]],
        reasoning: Optional[str] = None,
    ) -> "TierSuggestion":
        """Factory method for creating suggestion from analysis results.

        Args:
            tier: The suggested tier
            confidence: Confidence level
            all_matches: All keyword matches by tier
            reasoning: Optional custom reasoning (auto-generated if not provided)

        Returns:
            TierSuggestion with populated fields
        """
        matched_keywords = all_matches.get(tier, [])

        if reasoning is None:
            if matched_keywords:
                reasoning = f"Matched {len(matched_keywords)} Tier {tier.value} keyword(s): {', '.join(matched_keywords)}"
            else:
                reasoning = f"Suggested Tier {tier.value} based on analysis"

        return cls(
            tier=tier,
            confidence=confidence,
            matched_keywords=matched_keywords,
            reasoning=reasoning,
            all_matches=all_matches,
        )


# =============================================================================
# Analysis Functions
# =============================================================================


def analyze_description(description: str) -> dict[ProjectTier, list[str]]:
    """Analyze description text for tier keywords.

    Tokenizes the description and matches against TIER_KEYWORDS.
    Matching is case-insensitive.

    Args:
        description: User's project description text

    Returns:
        Dictionary mapping each tier to list of matched keywords
    """
    # Initialize result with all tiers
    matches: dict[ProjectTier, list[str]] = {tier: [] for tier in ProjectTier}

    if not description or not description.strip():
        return matches

    # Normalize description: lowercase, remove punctuation for matching
    normalized = description.lower()

    # Match each tier's keywords
    for tier, keywords in TIER_KEYWORDS.items():
        for keyword in keywords:
            # Handle multi-word keywords (e.g., "multi-component", "security-critical")
            if "-" in keyword:
                # Match exact hyphenated keyword
                if keyword in normalized:
                    matches[tier].append(keyword)
            else:
                # Match single words with word boundary detection
                # Use regex to find whole word matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, normalized):
                    matches[tier].append(keyword)

    return matches


def calculate_keyword_confidence(matches: dict[ProjectTier, list[str]]) -> TierConfidence:
    """Calculate confidence level from keyword matches.

    Confidence is based on how concentrated the matches are in a single tier:
    - HIGH: >66% of matches in one tier
    - MEDIUM: 34-66% of matches in one tier
    - LOW: <34% or no matches

    Args:
        matches: Dictionary mapping tiers to matched keywords

    Returns:
        TierConfidence enum value
    """
    if not matches:
        return TierConfidence.LOW

    # Count total matches
    total_matches = sum(len(v) for v in matches.values())

    if total_matches == 0:
        return TierConfidence.LOW

    # Find the tier with the most matches
    max_matches = max(len(v) for v in matches.values())

    # Calculate percentage for dominant tier
    dominant_percentage = max_matches / total_matches

    if dominant_percentage > HIGH_CONFIDENCE_THRESHOLD:
        return TierConfidence.HIGH
    elif dominant_percentage >= MEDIUM_CONFIDENCE_THRESHOLD:
        return TierConfidence.MEDIUM
    else:
        return TierConfidence.LOW


def analyze_codebase_metrics(
    project_result: ProjectTypeResult,
    file_count: Optional[int] = None,
) -> Optional[int]:
    """Analyze codebase metrics for tier adjustment.

    For brownfield projects, suggests tier adjustment based on codebase size:
    - Large codebase (100+ files): +1 tier
    - Very large codebase (500+ files): +2 tier

    Args:
        project_result: Result from detect_project_type()
        file_count: Optional explicit file count (for testing)

    Returns:
        Tier adjustment value (1 or 2) or None for no adjustment
    """
    # No adjustment for greenfield projects
    if project_result.project_type == ProjectType.GREENFIELD:
        return None

    # For brownfield, check file count
    # Try to extract file count from signals if not provided
    if file_count is None:
        for signal in project_result.detection_signals:
            if "source files" in signal.details.lower():
                # Try to parse count from details like "Found 150 source files"
                match = re.search(r'Found (\d+) source files', signal.details)
                if match:
                    file_count = int(match.group(1))
                    break

    if file_count is None:
        return None

    # Calculate adjustment based on file count
    if file_count >= VERY_LARGE_CODEBASE_THRESHOLD:
        return 2
    elif file_count >= LARGE_CODEBASE_THRESHOLD:
        return 1
    else:
        return None


def _determine_winning_tier(matches: dict[ProjectTier, list[str]]) -> ProjectTier:
    """Determine the tier with the most keyword matches.

    Args:
        matches: Dictionary mapping tiers to matched keywords

    Returns:
        ProjectTier with the most matches, or DEFAULT_TIER if no matches
    """
    if not matches:
        return DEFAULT_TIER

    # Filter to tiers with matches
    tiers_with_matches = [(tier, len(kws)) for tier, kws in matches.items() if kws]

    if not tiers_with_matches:
        return DEFAULT_TIER

    # Find tier with most matches
    # In case of tie, prefer higher tier (more conservative)
    winning_tier = max(tiers_with_matches, key=lambda x: (x[1], x[0].value))[0]
    return winning_tier


# =============================================================================
# Main Entry Point
# =============================================================================


def suggest_tier(
    description: str,
    project_path: Optional[Path] = None,
) -> TierSuggestion:
    """Suggest an appropriate project tier based on description and codebase.

    This is the main entry point for tier suggestion. It combines:
    1. Keyword analysis of the description
    2. Optional codebase metrics for brownfield projects

    Args:
        description: User's project description text
        project_path: Optional path to project directory for codebase analysis

    Returns:
        TierSuggestion with recommended tier, confidence, and reasoning

    Examples:
        >>> suggest_tier("Fix the bug in login")
        TierSuggestion(tier=TIER_0, confidence=HIGH, ...)

        >>> suggest_tier("Build a new platform", project_path=Path("./myproject"))
        TierSuggestion(tier=TIER_3, confidence=HIGH, ...)
    """
    # Analyze description for keywords
    matches = analyze_description(description)

    # Calculate confidence
    confidence = calculate_keyword_confidence(matches)

    # Determine winning tier from keywords
    base_tier = _determine_winning_tier(matches)

    # Check for no matches - use default
    total_matches = sum(len(v) for v in matches.values())
    if total_matches == 0:
        return TierSuggestion.default_suggestion()

    # Start with base tier from keyword analysis
    final_tier = base_tier

    # Apply codebase adjustment if project path provided
    codebase_adjustment = None
    adjustment_reason = ""

    if project_path is not None:
        try:
            if project_path.exists() and project_path.is_dir():
                # Detect project type and get file count
                project_result = detect_project_type(project_path)
                file_count, _ = count_source_files(project_path)

                # Calculate adjustment
                codebase_adjustment = analyze_codebase_metrics(project_result, file_count)

                if codebase_adjustment is not None:
                    # Apply adjustment, capped at TIER_4
                    adjusted_value = min(
                        final_tier.value + codebase_adjustment,
                        ProjectTier.TIER_4.value,
                    )
                    final_tier = ProjectTier(adjusted_value)
                    adjustment_reason = f" (adjusted +{codebase_adjustment} for {file_count} source files)"
        except (FileNotFoundError, NotADirectoryError, PermissionError):
            # Silently ignore path errors - just use keyword analysis
            pass

    # Build reasoning
    matched_keywords = matches.get(final_tier, []) or matches.get(base_tier, [])
    reasoning = (
        f"Matched {total_matches} keyword(s) with majority in Tier {base_tier.value}"
        + adjustment_reason
    )

    return TierSuggestion(
        tier=final_tier,
        confidence=confidence,
        matched_keywords=matched_keywords,
        reasoning=reasoning,
        all_matches=matches,
    )
