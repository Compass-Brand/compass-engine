"""Menu Selection - Confidence-Based Menu Option Selection.

Story 2b-2: Automatic Menu Selection

This module provides menu selection capabilities based on confidence tiers:
- High (>= 80%): Auto-select without user prompt (HighConfidenceSelector)
- Medium (50-79%): Present with recommendation (MediumConfidenceSelector)
- Low (< 50%): Present without recommendation (LowConfidenceSelector)

Parallel Group A implements the HighConfidenceSelector for auto-selection.
Parallel Group B implements the MediumConfidenceSelector for recommendations.
Parallel Group C implements the LowConfidenceSelector for neutral presentation.

Sequential Tasks D, E, F implement:
- SelectionLogger for audit trail (AC: #4)
- Timing instrumentation (AC: #5)
- MenuSelector orchestrator
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from pcmrp_tools.bmad_automation.batch_continue import (
    CONTINUE_PATTERNS,
    BatchCheckpoint,
    BatchContinueManager,
    create_checkpoint,
    is_continue_menu,
)
from pcmrp_tools.bmad_automation.bmb_thresholds import (
    BMBThresholdChecker,
    EscalationAction,
    EscalationResult,
    ValidationMetrics,
)
from pcmrp_tools.bmad_automation.menu_history import (
    MenuHistoryEntry,
    MenuHistoryManager,
    SelectionSource,
)
from pcmrp_tools.bmad_automation.menu_participation_engine import (
    MenuDetectionResult,
    MenuType,
)
from pcmrp_tools.bmad_automation.nested_menu import (
    MenuDepthTracker,
    StateManager,
    UserEscalation,
    detect_elicitation_menu,
    detect_party_mode_menu,
    handle_depth_exceeded,
)


# =============================================================================
# Constants
# =============================================================================

CONFIDENCE_THRESHOLD_HIGH = 80
"""Minimum confidence score for high confidence auto-selection (inclusive)."""

CONFIDENCE_THRESHOLD_MEDIUM_LOW = 50
"""Minimum confidence score for medium confidence tier (inclusive)."""

CONFIDENCE_THRESHOLD_MEDIUM_HIGH = 79
"""Maximum confidence score for medium confidence tier (inclusive)."""

# Score thresholds for text descriptions (Issue #4)
SCORE_HIGH_THRESHOLD = 70
"""Score threshold for 'highest-scoring' description."""

SCORE_MEDIUM_THRESHOLD = 50
"""Score threshold for 'best available' description."""

# Confidence thresholds for text descriptions (Issue #4)
CONFIDENCE_GOOD_THRESHOLD = 70
"""Confidence threshold for 'good' description."""

CONFIDENCE_MODERATE_THRESHOLD = 60
"""Confidence threshold for 'moderate' description."""


# =============================================================================
# Option Priority Configuration
# =============================================================================

# Default priority for common menu options (lower = higher priority)
_DEFAULT_OPTION_PRIORITIES: Dict[str, int] = {
    # Continue/Progress options - highest priority for workflow progression
    "continue": 1,
    "proceed": 1,
    "next": 1,
    # Approval options
    "yes": 2,
    "approve": 2,
    "confirm": 2,
    # View/Review options
    "view": 3,
    "review": 3,
    "details": 3,
    # Neutral options
    "skip": 4,
    "later": 4,
    # Negative/Exit options - lower priority
    "no": 5,
    "cancel": 5,
    "exit": 6,
    "quit": 6,
}

# Context-specific priority adjustments
_CONTEXT_PRIORITY_ADJUSTMENTS: Dict[str, Dict[str, int]] = {
    # When reviewing, View becomes higher priority
    "review": {"view": 1, "review": 1},
    # When approving, Yes becomes highest
    "approve": {"yes": 1, "approve": 1},
    # When exploring, Advanced becomes higher
    "explore": {"advanced": 1, "party mode": 2},
}


# =============================================================================
# Data Classes (Parallel Group A)
# =============================================================================


@dataclass
class SelectionResult:
    """Result of a menu selection operation.

    Attributes:
        selected: True if an option was auto-selected, False if user input needed.
        option: The selected menu option, or None if not selected.
        reason: Explanation for the selection decision.
        confidence: The confidence score from menu detection (0-100).
    """

    selected: bool
    option: Optional[str] = None
    reason: str = ""
    confidence: int = 0


@dataclass
class EscalationSelectionResult:
    """Result when BMB thresholds trigger escalation.

    This result type is returned when validation metrics exceed BMB thresholds,
    bypassing normal confidence-based menu selection.

    Attributes:
        escalation: The EscalationResult from BMB threshold evaluation.
        selected: Always False for escalation results (no auto-selection occurred).
        auto_selected: Always False for escalation results.
    """

    escalation: EscalationResult
    selected: bool = False
    auto_selected: bool = False


@dataclass
class ContinueSelectionResult:
    """Result when a continue menu is auto-continued (Tier 0-1 or batched).

    This result type is returned for continue menus that were automatically
    handled by the batch-continue logic.

    Attributes:
        auto_continued: True if the continue was automatic (within batch or AUTO_ALL mode).
        selected_option: The option that was selected (e.g., "[C] Continue").
        context: The context string for this continue operation.
        reason: Explanation for the auto-continue decision.
    """

    auto_continued: bool
    selected_option: str
    context: str = ""
    reason: str = ""


# =============================================================================
# HighConfidenceSelector Class (Parallel Group A)
# =============================================================================


class HighConfidenceSelector:
    """Selector for high confidence menu detection (>= 80%).

    When confidence is at or above 80%, this selector can automatically
    select the best option without requiring user confirmation.

    Example:
        >>> selector = HighConfidenceSelector()
        >>> if selector.should_auto_select(85):
        ...     result = selector.select_best_option(detection_result)
        ...     print(f"Auto-selected: {result.option}")
    """

    def should_auto_select(self, confidence: int) -> bool:
        """Check if confidence is high enough for automatic selection.

        Args:
            confidence: Confidence score from 0-100 (values outside this range
                are technically accepted but may produce unexpected results).

        Returns:
            True if confidence >= 80 (high confidence threshold).
        """
        return confidence >= CONFIDENCE_THRESHOLD_HIGH

    def select_best_option(
        self,
        detection_result: MenuDetectionResult,
        context: Optional[Dict] = None,
    ) -> SelectionResult:
        """Select the best option from a high-confidence menu detection.

        Analyzes the detected menu options and selects the most appropriate
        option based on context alignment and priority.

        Args:
            detection_result: The menu detection result containing options.
            context: Optional context dict with keys like 'action',
                'workflow_phase', 'expected_option', etc.

        Returns:
            SelectionResult with selected option and reasoning.
        """
        options = detection_result.options if detection_result.options else []
        confidence = detection_result.confidence

        # Validate high confidence threshold
        if not self.should_auto_select(confidence):
            return SelectionResult(
                selected=False,
                option=None,
                reason=f"Confidence {confidence}% is below auto-select threshold (80%).",
                confidence=confidence,
            )

        # Handle empty options
        if not options:
            return SelectionResult(
                selected=False,
                option=None,
                reason="No options available for selection.",
                confidence=confidence,
            )

        # Score all options and select the best
        scored_options = [
            (option, self.score_option(option, context)) for option in options
        ]

        # Pre-compute indices for O(1) lookup during sort (Issue #3: avoid O(n²))
        indices = {opt: i for i, opt in enumerate(options)}

        # Sort by score (descending), use stable sort for tie-breaking
        scored_options.sort(key=lambda x: (-x[1], indices[x[0]]))

        best_option, best_score = scored_options[0]

        # Generate selection reason
        reason = self._generate_selection_reason(
            option=best_option,
            score=best_score,
            confidence=confidence,
            menu_type=detection_result.menu_type,
            context=context,
        )

        return SelectionResult(
            selected=True,
            option=best_option,
            reason=reason,
            confidence=confidence,
        )

    def score_option(self, option: str, context: Optional[Dict] = None) -> int:
        """Score an option based on context alignment.

        Higher scores indicate better alignment with the current context.
        Scoring factors:
        - Default priority from common option patterns
        - Context-specific boosts (e.g., expected_option match)
        - Workflow phase alignment

        Args:
            option: Menu option label to score.
            context: Optional context for influencing scores.

        Returns:
            Score from 0-100 (higher is better).
        """
        option_lower = option.lower().strip()
        base_score = 50  # Default neutral score

        # Apply default priority bonuses (higher priority = higher score)
        base_score += self._get_priority_bonus(option_lower)

        # Apply context-specific adjustments
        if context:
            base_score += self._get_context_bonus(option_lower, context)

        # Clamp score to 0-100 range
        return max(0, min(100, base_score))

    def _get_priority_bonus(self, option_lower: str) -> int:
        """Get priority bonus based on common option patterns.

        Args:
            option_lower: Lowercased option text.

        Returns:
            Bonus score adjustment (-20 to +20).
        """
        # Split into words for precise matching (avoid "unknown" matching "no")
        words = set(option_lower.split())

        # High priority options (workflow progression)
        high_priority = {"continue", "proceed", "next", "yes", "approve", "confirm"}
        if words & high_priority or any(kw in option_lower for kw in high_priority):
            return 20

        # Medium priority options
        medium_priority = {"view", "review", "details", "advanced"}
        if words & medium_priority or any(kw in option_lower for kw in medium_priority):
            return 10

        # Low priority options (check substring for "party mode")
        if words & {"skip", "later"} or "party mode" in option_lower:
            return 0

        # Negative priority options - must match as whole words or exact substrings
        # to avoid "unknown" matching "no"
        negative_priority = {"cancel", "exit", "quit"}
        if words & negative_priority:
            return -10
        # Special case for "no" - must be a standalone word
        if "no" in words:
            return -10

        return 0  # Unknown options get no bonus

    def _get_context_bonus(self, option_lower: str, context: Dict) -> int:
        """Get context-specific score bonus.

        Args:
            option_lower: Lowercased option text.
            context: Context dictionary.

        Returns:
            Bonus score adjustment.
        """
        bonus = 0

        # Expected option match gives large bonus
        expected = context.get("expected_option", "").lower()
        if expected and expected in option_lower:
            bonus += 30

        # Workflow phase alignment
        phase = context.get("workflow_phase", "").lower()
        if phase:
            if phase == "review" and "view" in option_lower:
                bonus += 15
            elif phase == "approval" and ("yes" in option_lower or "approve" in option_lower):
                bonus += 15
            elif phase == "progression" and "continue" in option_lower:
                bonus += 15

        # Action context alignment
        action = context.get("action", "").lower()
        if action:
            if action == "explore" and ("advanced" in option_lower or "party" in option_lower):
                bonus += 15
            elif action == "confirm" and ("yes" in option_lower or "confirm" in option_lower):
                bonus += 15

        return bonus

    def _generate_selection_reason(
        self,
        option: str,
        score: int,
        confidence: int,
        menu_type: Optional[MenuType],
        context: Optional[Dict] = None,
    ) -> str:
        """Generate a human-readable reason for the selection.

        Args:
            option: The selected option.
            score: The option's score.
            confidence: Confidence score.
            menu_type: Type of menu detected.
            context: Optional context dict.

        Returns:
            Human-readable explanation string.
        """
        parts = []

        # Confidence statement
        parts.append(f"Auto-selected with {confidence}% confidence")

        # Score justification
        if score >= SCORE_HIGH_THRESHOLD:
            parts.append(f"'{option}' is the highest-scoring option (score: {score})")
        elif score >= SCORE_MEDIUM_THRESHOLD:
            parts.append(f"'{option}' is the best available option (score: {score})")
        else:
            parts.append(f"'{option}' selected as default (score: {score})")

        # Context influence
        if context:
            expected = context.get("expected_option", "")
            if expected and expected.lower() in option.lower():
                parts.append("matches expected option")

        return ". ".join(parts) + "."


# =============================================================================
# Data Classes (Parallel Group B)
# =============================================================================


@dataclass
class RecommendationResult:
    """Result of a menu recommendation for medium confidence tier.

    Attributes:
        recommended_option: The option recommended for selection.
        alternatives: Other available options (ranked by suitability).
        reason: Explanation for why the recommended option was chosen.
        confidence: The confidence score from menu detection (0-100).
    """

    recommended_option: str
    alternatives: List[str] = field(default_factory=list)
    reason: str = ""
    confidence: int = 0


# =============================================================================
# MediumConfidenceSelector Class
# =============================================================================


class MediumConfidenceSelector:
    """Selector for medium confidence menu detection (50-79%).

    When confidence is in the medium range, this selector provides a
    recommendation but does not auto-select. The user can override
    the recommendation.

    Example:
        >>> selector = MediumConfidenceSelector()
        >>> if selector.is_medium_confidence(65):
        ...     result = selector.get_recommendation(detection_result)
        ...     print(f"Recommended: {result.recommended_option}")
        ...     print(f"Alternatives: {result.alternatives}")
    """

    def is_medium_confidence(self, confidence: int) -> bool:
        """Check if the confidence score falls in the medium tier.

        Medium confidence is defined as 50 <= confidence <= 79.

        Args:
            confidence: Confidence score from 0-100 (values outside this range
                are technically accepted but may produce unexpected results).

        Returns:
            True if confidence is in medium tier (50-79 inclusive).
        """
        return CONFIDENCE_THRESHOLD_MEDIUM_LOW <= confidence <= CONFIDENCE_THRESHOLD_MEDIUM_HIGH

    def rank_options(
        self, options: List[str], context: Optional[Dict] = None
    ) -> List[str]:
        """Rank options by suitability.

        Uses default priorities and context-specific adjustments to
        order options from most to least suitable.

        Args:
            options: List of menu option labels.
            context: Optional context dict with keys like 'action',
                'workflow_phase', 'previous_action', etc.

        Returns:
            Options sorted by suitability (best first).
        """
        if not options:
            return []

        if len(options) == 1:
            return options.copy()

        # Build priority map with context adjustments
        priorities = self._build_priority_map(context)

        # Sort options by priority (lower priority value = higher rank)
        def get_priority(option: str) -> int:
            option_lower = option.lower().strip()
            # Check for exact match
            if option_lower in priorities:
                return priorities[option_lower]
            # Check for partial match
            for key, priority in priorities.items():
                if key in option_lower or option_lower in key:
                    return priority
            # Default priority for unknown options
            return 100

        return sorted(options, key=get_priority)

    def _build_priority_map(self, context: Optional[Dict] = None) -> Dict[str, int]:
        """Build priority map with context adjustments.

        Args:
            context: Optional context dict.

        Returns:
            Priority map (option -> priority value).
        """
        # Start with default priorities
        priorities = _DEFAULT_OPTION_PRIORITIES.copy()

        # Apply context-specific adjustments
        if context:
            action = context.get("action", "").lower()
            if action in _CONTEXT_PRIORITY_ADJUSTMENTS:
                adjustments = _CONTEXT_PRIORITY_ADJUSTMENTS[action]
                priorities.update(adjustments)

            # Workflow phase adjustments
            phase = context.get("workflow_phase", "").lower()
            if phase in _CONTEXT_PRIORITY_ADJUSTMENTS:
                adjustments = _CONTEXT_PRIORITY_ADJUSTMENTS[phase]
                priorities.update(adjustments)

        return priorities

    def get_recommendation(
        self,
        detection_result: MenuDetectionResult,
        context: Optional[Dict] = None,
    ) -> RecommendationResult:
        """Get a recommendation for which option to select.

        Analyzes the detected menu options and provides a recommendation
        with alternatives and reasoning.

        Args:
            detection_result: The menu detection result containing options.
            context: Optional context for influencing recommendations.

        Returns:
            RecommendationResult with recommendation and reasoning.
        """
        options = detection_result.options if detection_result.options else []

        # Handle empty options
        if not options:
            return RecommendationResult(
                recommended_option="",
                alternatives=[],
                reason="No options available for recommendation.",
                confidence=detection_result.confidence,
            )

        # Rank options by suitability
        ranked_options = self.rank_options(options, context)

        # Best option is first in ranked list
        recommended = ranked_options[0]
        alternatives = ranked_options[1:] if len(ranked_options) > 1 else []

        # Generate recommendation reason
        reason = self._generate_reason(
            recommended=recommended,
            alternatives=alternatives,
            menu_type=detection_result.menu_type,
            confidence=detection_result.confidence,
            context=context,
        )

        return RecommendationResult(
            recommended_option=recommended,
            alternatives=alternatives,
            reason=reason,
            confidence=detection_result.confidence,
        )

    def _generate_reason(
        self,
        recommended: str,
        alternatives: List[str],
        menu_type: Optional[MenuType],
        confidence: int,
        context: Optional[Dict] = None,
    ) -> str:
        """Generate a human-readable reason for the recommendation.

        Args:
            recommended: The recommended option.
            alternatives: Alternative options.
            menu_type: Type of menu detected.
            confidence: Confidence score.
            context: Optional context dict.

        Returns:
            Human-readable explanation string.
        """
        # Base reason components
        reasons = []

        # Add menu type context
        menu_type_desc = self._get_menu_type_description(menu_type)
        if menu_type_desc:
            reasons.append(f"For {menu_type_desc}")

        # Add recommendation with confidence context
        confidence_desc = self._get_confidence_description(confidence)
        reasons.append(
            f"'{recommended}' is recommended as the most suitable option "
            f"with {confidence_desc} confidence"
        )

        # Add context influence if applicable
        if context:
            action = context.get("action", "")
            if action:
                reasons.append(f"given the current '{action}' context")

        # Add alternatives note
        if alternatives:
            alt_count = len(alternatives)
            reasons.append(
                f"({alt_count} alternative{'s' if alt_count > 1 else ''} available)"
            )

        return ". ".join(reasons) + "."

    def _get_menu_type_description(self, menu_type: Optional[MenuType]) -> str:
        """Get human-readable description for menu type.

        Args:
            menu_type: The menu type enum value.

        Returns:
            Description string or empty string if unknown.
        """
        if menu_type is None:
            return ""

        descriptions = {
            MenuType.APC: "workflow progression menu",
            MenuType.YVN: "confirmation menu",
            MenuType.NUMBERED: "numbered options menu",
            MenuType.EXIT: "exit menu",
            MenuType.AGENT: "agent selection menu",
            MenuType.UNKNOWN: "menu",
        }
        return descriptions.get(menu_type, "menu")

    def _get_confidence_description(self, confidence: int) -> str:
        """Get human-readable description for confidence level.

        Args:
            confidence: Confidence score (0-100).

        Returns:
            Description string like 'moderate' or 'good'.
        """
        if confidence >= CONFIDENCE_GOOD_THRESHOLD:
            return "good"
        elif confidence >= CONFIDENCE_MODERATE_THRESHOLD:
            return "moderate"
        else:
            return "fair"


# =============================================================================
# Data Classes (Parallel Group C)
# =============================================================================


@dataclass
class PresentationResult:
    """Result of presenting menu options without recommendation (low confidence).

    Used when confidence is below the medium threshold (< 50%), indicating
    that no recommendation should be made. All options are presented
    neutrally without bias.

    Attributes:
        options: List of menu option labels (formatted neutrally).
        no_recommendation_reason: Explanation for why no recommendation given.
        confidence: The confidence score from menu detection (0-100).
    """

    options: List[str] = field(default_factory=list)
    no_recommendation_reason: str = ""
    confidence: int = 0


# =============================================================================
# LowConfidenceSelector Class (Parallel Group C)
# =============================================================================


class LowConfidenceSelector:
    """Selector for low confidence menu detection (< 50%).

    When confidence is below the threshold, this selector presents all
    options neutrally without making any recommendation. The user must
    make the choice themselves.

    Example:
        >>> selector = LowConfidenceSelector()
        >>> if selector.is_low_confidence(35):
        ...     result = selector.present_without_recommendation(detection)
        ...     print(f"Options: {result.options}")
        ...     print(f"Reason: {result.no_recommendation_reason}")
    """

    def is_low_confidence(self, confidence: int) -> bool:
        """Check if the confidence score is in the low tier.

        Low confidence is defined as confidence < 50.

        Args:
            confidence: Confidence score from 0-100 (values outside this range
                are technically accepted but may produce unexpected results).

        Returns:
            True if confidence is below the threshold (< 50).
        """
        return confidence < CONFIDENCE_THRESHOLD_MEDIUM_LOW

    def format_neutral_options(self, options: List[str]) -> List[str]:
        """Format options without bias indicators.

        Returns options in a neutral format without any markers that
        could suggest one option is preferred over another.

        Args:
            options: List of menu option labels.

        Returns:
            List of formatted options (preserving original content).
        """
        if not options:
            return []

        # Return options as-is, preserving original content
        # No prefixes, highlights, or bias markers added
        return list(options)

    def generate_no_recommendation_reason(self, confidence: int) -> str:
        """Generate explanation for why no recommendation is given.

        Produces a human-readable explanation that mentions the
        confidence level and explains the lack of recommendation.

        Args:
            confidence: Confidence score (0-100).

        Returns:
            Human-readable explanation string.
        """
        return (
            f"Low confidence ({confidence}%) prevents automatic recommendation. "
            f"Please review all options and make your selection."
        )

    def present_without_recommendation(
        self, detection_result: MenuDetectionResult
    ) -> PresentationResult:
        """Present menu options neutrally without recommendation.

        Extracts options from the detection result and presents them
        in a neutral format with an explanation for why no recommendation
        is provided.

        Args:
            detection_result: The menu detection result containing options.

        Returns:
            PresentationResult with neutral options and explanation.
        """
        options = detection_result.options if detection_result.options else []

        # Format options neutrally (no bias)
        formatted_options = self.format_neutral_options(options)

        # Generate reason for no recommendation
        reason = self.generate_no_recommendation_reason(detection_result.confidence)

        return PresentationResult(
            options=formatted_options,
            no_recommendation_reason=reason,
            confidence=detection_result.confidence,
        )


# =============================================================================
# Constants (Sequential Task E)
# =============================================================================

MAX_SELECTION_TIME_MS = 5000
"""Maximum allowed time for selection operation in milliseconds (NFR2 compliance)."""


# =============================================================================
# Data Classes (Sequential Task D)
# =============================================================================


@dataclass
class SelectionLogEntry:
    """Log entry for a menu selection operation.

    Attributes:
        timestamp: Unix timestamp when the selection occurred.
        menu_type: Type of menu detected (APC, YVN, NUMBERED, etc.).
        selection: The option that was selected (None for low confidence).
        reason: Explanation for the selection decision.
        confidence: The confidence score from menu detection (0-100).
        duration_ms: Time taken for the selection operation in milliseconds.
        auto_selected: True if auto-selected (high confidence), False otherwise.
    """

    timestamp: float
    menu_type: str
    selection: Optional[str]
    reason: str
    confidence: int
    duration_ms: int
    auto_selected: bool


# =============================================================================
# SelectionLogger Class (Sequential Task D)
# =============================================================================


class SelectionLogger:
    """Logger for menu selection operations with audit trail.

    Maintains a chronological audit trail of all menu selection operations
    for auditability (AC: #4).

    Example:
        >>> logger = SelectionLogger()
        >>> entry = SelectionLogEntry(
        ...     timestamp=time.time(),
        ...     menu_type="APC",
        ...     selection="Continue",
        ...     reason="Auto-selected with 85% confidence",
        ...     confidence=85,
        ...     duration_ms=100,
        ...     auto_selected=True,
        ... )
        >>> logger.log_selection(entry)
        >>> trail = logger.get_audit_trail()
        >>> print(f"Logged {len(trail)} selections")
    """

    def __init__(self) -> None:
        """Initialize SelectionLogger with empty audit trail."""
        self._audit_trail: List[SelectionLogEntry] = []

    def log_selection(self, entry: SelectionLogEntry) -> None:
        """Log a selection entry to the audit trail.

        Args:
            entry: The SelectionLogEntry to add to the trail.
        """
        self._audit_trail.append(entry)

    def get_audit_trail(self) -> List[SelectionLogEntry]:
        """Get a copy of the audit trail.

        Returns:
            A copy of the list of all logged SelectionLogEntry objects.
        """
        return list(self._audit_trail)

    def clear_audit_trail(self) -> None:
        """Clear all entries from the audit trail.

        Use this method to prevent unbounded memory growth in long-running
        sessions after audit data has been persisted or is no longer needed.
        """
        self._audit_trail.clear()


# =============================================================================
# Performance Check (Sequential Task E)
# =============================================================================


def performance_check(duration_ms: int) -> bool:
    """Check if selection duration is within acceptable limits.

    Args:
        duration_ms: Duration of the selection operation in milliseconds.

    Returns:
        True if duration is less than MAX_SELECTION_TIME_MS (5000ms),
        False otherwise.
    """
    return duration_ms < MAX_SELECTION_TIME_MS


# =============================================================================
# MenuSelector Orchestrator (Sequential Task F)
# =============================================================================


class MenuSelector:
    """Orchestrator for menu selection across all confidence tiers.

    Routes menu detection results to the appropriate selector based on
    confidence level and logs all selection operations.

    Confidence Tiers:
    - High (>= 80%): Routes to HighConfidenceSelector for auto-selection
    - Medium (50-79%): Routes to MediumConfidenceSelector for recommendation
    - Low (< 50%): Routes to LowConfidenceSelector for neutral presentation

    BMB Threshold Pre-Check:
    When validation_metrics are provided, BMB thresholds are evaluated FIRST.
    If escalation is needed (blocking_errors > 3, major_issues > 5, or
    compliance_score < 70), the confidence-based logic is bypassed and
    an EscalationSelectionResult is returned.

    Example:
        >>> selector = MenuSelector()
        >>> detection = MenuDetectionResult.detected(
        ...     confidence=85,
        ...     menu_type=MenuType.APC,
        ...     options=["Continue", "Exit"],
        ...     breakdown={"test": 85},
        ...     raw_input="[C] Continue [E] Exit",
        ... )
        >>> result = selector.select_or_present(detection)
        >>> if isinstance(result, SelectionResult):
        ...     print(f"Auto-selected: {result.option}")
    """

    def __init__(
        self,
        bmb_checker: Optional[BMBThresholdChecker] = None,
        tier: int = 2,
    ) -> None:
        """Initialize MenuSelector with all tier selectors and logger.

        Args:
            bmb_checker: Optional BMBThresholdChecker for validation metric
                pre-checks. If None, validation_metrics parameter in
                select_or_present will be ignored.
            tier: Project tier (0-4) for batch-continue behavior. Default is 2.
                - Tier 0-1: AUTO_ALL mode (auto-continue all continue menus)
                - Tier 2: Batched mode with size 5
                - Tier 3: Batched mode with size 3
                - Tier 4: Single-step mode (checkpoint every step)
        """
        self.high_selector = HighConfidenceSelector()
        self.medium_selector = MediumConfidenceSelector()
        self.low_selector = LowConfidenceSelector()
        self.logger = SelectionLogger()
        self.bmb_checker = bmb_checker
        self._history_manager = MenuHistoryManager()
        self._tier = tier
        self._batch_manager = BatchContinueManager(tier)
        # Story 2b-4 Task 6: Nested menu tracking
        self._depth_tracker = MenuDepthTracker()
        self._state_manager = StateManager()

    def set_tier(self, tier: int) -> None:
        """Update tier and reconfigure batch manager.

        Args:
            tier: New project tier (0-4) for batch-continue behavior.
        """
        self._tier = tier
        self._batch_manager = BatchContinueManager(tier)

    def record_selection(
        self,
        menu_id: str,
        selection: str,
        confidence: float,
        source: SelectionSource,
        workflow_context: Optional[str] = None,
    ) -> None:
        """Record a menu selection to history.

        Args:
            menu_id: Identifier for the menu that was presented.
            selection: The option that was selected.
            confidence: Confidence score (0.0 to 1.0) for the selection.
            source: How the selection was made (auto/manual/escalated).
            workflow_context: Optional workflow identifier for context.
        """
        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id=menu_id,
            selection=selection,
            confidence=confidence,
            source=source,
            workflow_context=workflow_context,
        )
        self._history_manager.add_entry(entry)

    def save_history(self, session_id: str) -> None:
        """Save history for session recovery.

        Saves the current history to a file that can be loaded later
        to resume a workflow after a crash or interruption.

        Args:
            session_id: Unique identifier for the session. Used to
                construct the file path for storage.
        """
        path = MenuHistoryManager.get_session_history_path(session_id)
        self._history_manager.save_to_file(path)

    def load_history(self, session_id: str) -> None:
        """Load history for workflow resume.

        Loads previously saved history from a session file. This is
        used to restore state when resuming a workflow.

        Args:
            session_id: Unique identifier for the session. Used to
                locate the file to load.
        """
        path = MenuHistoryManager.get_session_history_path(session_id)
        self._history_manager.load_from_file(path)

    def select_or_present(
        self,
        detection_result: MenuDetectionResult,
        context: Optional[Any] = None,
        validation_metrics: Optional[ValidationMetrics] = None,
    ) -> Union[
        SelectionResult,
        RecommendationResult,
        PresentationResult,
        EscalationSelectionResult,
        ContinueSelectionResult,
        BatchCheckpoint,
        UserEscalation,
    ]:
        """Route to appropriate selector based on confidence tier.

        If validation_metrics are provided and a bmb_checker is configured,
        BMB thresholds are evaluated FIRST. If escalation is triggered,
        the confidence-based logic is bypassed.

        For continue menus, batch-continue logic is applied based on tier:
        - Tier 0-1: AUTO_ALL mode (auto-continue without batching)
        - Tier 2-3: BATCHED mode (checkpoint after batch_size operations)
        - Tier 4: SINGLE_STEP mode (checkpoint every operation)

        Args:
            detection_result: The menu detection result containing options.
            context: Optional context (dict or string) for influencing selection.
            validation_metrics: Optional ValidationMetrics for BMB threshold
                pre-check. When provided with a bmb_checker, thresholds are
                evaluated before confidence-based selection.

        Returns:
            EscalationSelectionResult if BMB thresholds trigger escalation,
            ContinueSelectionResult for auto-continued continue menus,
            BatchCheckpoint when batch is complete (Tier 2-4),
            SelectionResult for high confidence (auto-select),
            RecommendationResult for medium confidence (recommend),
            PresentationResult for low confidence (neutral).
        """
        start_time = time.time()
        confidence = detection_result.confidence

        # Get menu type as string (used for logging)
        menu_type_str = (
            detection_result.menu_type.name
            if detection_result.menu_type
            else "UNKNOWN"
        )

        # Story 2b-4 Task 6: Check depth before processing
        if self._depth_tracker.is_depth_exceeded():
            return handle_depth_exceeded(self._depth_tracker)

        # BMB Threshold Pre-Check (Story 2b-3 Task 5)
        if validation_metrics is not None and self.bmb_checker is not None:
            escalation = self.bmb_checker.evaluate_all_thresholds(validation_metrics)
            if escalation.action != EscalationAction.NO_ESCALATION:
                # Calculate duration
                end_time = time.time()
                duration_ms = int((end_time - start_time) * 1000)

                # Log the escalation
                log_entry = SelectionLogEntry(
                    timestamp=start_time,
                    menu_type=menu_type_str,
                    selection=None,
                    reason=escalation.reason,
                    confidence=confidence,
                    duration_ms=duration_ms,
                    auto_selected=False,
                )
                self.logger.log_selection(log_entry)

                # Record to history (Story 2b-5 Task 5)
                self.record_selection(
                    menu_id=menu_type_str,
                    selection="",
                    confidence=confidence / 100.0 if confidence > 1.0 else confidence,
                    source=SelectionSource.ESCALATED,
                    workflow_context=None,
                )

                return EscalationSelectionResult(escalation=escalation)

        # Story 2b-6: Batch-continue logic for continue menus
        if is_continue_menu(detection_result.raw_input, detection_result.options):
            return self._handle_continue_with_batching(detection_result, context)

        # Normal confidence-based routing
        if self.high_selector.should_auto_select(confidence):
            result = self.high_selector.select_best_option(detection_result, context)
            selection = result.option
            reason = result.reason
            auto_selected = True
        elif self.medium_selector.is_medium_confidence(confidence):
            result = self.medium_selector.get_recommendation(detection_result, context)
            selection = result.recommended_option
            reason = result.reason
            auto_selected = False
        else:
            result = self.low_selector.present_without_recommendation(detection_result)
            selection = None
            reason = result.no_recommendation_reason
            auto_selected = False

        # Calculate duration
        end_time = time.time()
        duration_ms = int((end_time - start_time) * 1000)

        # Log the selection
        log_entry = SelectionLogEntry(
            timestamp=start_time,
            menu_type=menu_type_str,
            selection=selection,
            reason=reason,
            confidence=confidence,
            duration_ms=duration_ms,
            auto_selected=auto_selected,
        )
        self.logger.log_selection(log_entry)

        # Record to history (Story 2b-5 Task 5)
        # Determine source based on whether it was auto-selected
        history_source = SelectionSource.AUTO if auto_selected else SelectionSource.MANUAL
        # Normalize confidence to 0.0-1.0 scale
        normalized_confidence = confidence / 100.0 if confidence > 1.0 else confidence
        # Selection may be None for low confidence - use empty string
        history_selection = selection if selection is not None else ""
        self.record_selection(
            menu_id=menu_type_str,
            selection=history_selection,
            confidence=normalized_confidence,
            source=history_source,
            workflow_context=None,
        )

        return result

    def _handle_continue_with_batching(
        self,
        detection_result: MenuDetectionResult,
        context: Optional[Any] = None,
    ) -> Union[ContinueSelectionResult, BatchCheckpoint]:
        """Handle continue menus with batch-continue logic.

        Routes to appropriate handling based on tier:
        - Tier 0-1 (AUTO_ALL): Auto-continue without batching
        - Tier 2-4 (BATCHED/SINGLE_STEP): Track in batch, checkpoint when full

        Args:
            detection_result: The menu detection result for the continue menu.
            context: Optional context string describing the operation.

        Returns:
            ContinueSelectionResult if auto-continuing within batch,
            BatchCheckpoint when batch is complete and needs user review.
        """
        # Get context string
        context_str = self._normalize_context_string(context)

        # Check for AUTO_ALL mode (Tier 0-1)
        if self._batch_manager.is_auto_all_mode():
            return self._auto_select_continue(detection_result, context_str)

        # Batched mode (Tier 2-4): Track in batch
        # Start batch if needed
        if not self._batch_manager.has_active_batch():
            self._batch_manager.start_batch()

        # Add operation to current batch
        self._batch_manager.add_operation(f"Continue: {context_str}")

        # Check if batch is complete
        if self._batch_manager.is_batch_complete():
            # End batch and create checkpoint
            summary = self._batch_manager.end_batch()
            return create_checkpoint(summary)

        # Auto-continue within batch
        return self._auto_select_continue(detection_result, context_str)

    def _auto_select_continue(
        self,
        detection_result: MenuDetectionResult,
        context_str: str = "",
    ) -> ContinueSelectionResult:
        """Auto-select the continue option from a continue menu.

        Finds and selects the continue option (e.g., "[C] Continue", "Continue",
        "Proceed") from the menu options.

        Args:
            detection_result: The menu detection result.
            context_str: Context string for the operation.

        Returns:
            ContinueSelectionResult with the selected continue option.
        """
        # Find the continue option
        selected_option = self._find_continue_option(detection_result.options)

        return ContinueSelectionResult(
            auto_continued=True,
            selected_option=selected_option,
            context=context_str,
            reason="Auto-continued as part of batch-continue logic",
        )

    def _find_continue_option(self, options: Optional[List[str]]) -> str:
        """Find the continue option from a list of menu options.

        Uses CONTINUE_PATTERNS from batch_continue module for consistency.

        Args:
            options: List of menu option strings.

        Returns:
            The continue option string, or "Continue" if not found.
        """
        if not options:
            return "Continue"

        # Use centralized CONTINUE_PATTERNS for consistency with is_continue_menu
        for option in options:
            for pattern in CONTINUE_PATTERNS:
                if pattern in option:
                    return option

        # Default to first option or "Continue"
        return options[0] if options else "Continue"

    def _normalize_context_string(self, context: Optional[Any]) -> str:
        """Normalize context to a string representation.

        Args:
            context: Context can be None, a string, or a dict.

        Returns:
            String representation of the context.
        """
        if context is None:
            return ""
        if isinstance(context, str):
            return context
        if isinstance(context, dict):
            # Extract workflow_phase or action from dict if present
            if "workflow_phase" in context:
                return str(context["workflow_phase"])
            if "action" in context:
                return str(context["action"])
            return str(context)
        return str(context)
