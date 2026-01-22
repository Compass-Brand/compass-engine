"""Nested Menu Handling - Story 2b-4.

This module provides nested menu handling capabilities for BMAD workflow automation,
including depth tracking, context management, and specialized handling for
Party Mode and Advanced Elicitation sub-workflows.

Features:
- MenuDepthTracker: Tracks menu nesting depth up to MAX_NESTED_DEPTH (3)
- PartyModeMenuContext: Context for Party Mode internal menus
- ElicitationMenuContext: Context for Advanced Elicitation menus
- Detection functions for identifying menu types
- Selection handlers with context-aware logic
- ParentState and StateManager for parent state preservation
- UserEscalation and handle_depth_exceeded for depth limit handling

Tasks Implemented:
- Task 1: MenuDepthTracker with MenuContext dataclass
- Task 2: Party Mode Context Handling
- Task 3: Advanced Elicitation Context Handling
- Task 4: Parent State Restoration
- Task 5: Depth Exceeded Escalation
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from pcmrp_tools.bmad_automation.menu_participation_engine import (
    MenuDetectionResult,
)


# =============================================================================
# Constants (Task 1)
# =============================================================================

MAX_NESTED_DEPTH = 3
"""Maximum allowed depth for nested menu invocations."""

VALID_WORKFLOW_TYPES = frozenset({"party_mode", "elicitation", "standard"})
"""Valid workflow type values for MenuContext."""

VALID_ELICITATION_PHASES = frozenset({"technique_selection", "execution", "summary"})
"""Valid elicitation phase values for ElicitationMenuContext."""


# =============================================================================
# Compiled Regex Patterns
# =============================================================================

# Party Mode detection patterns
_PARTY_MODE_PATTERNS = [
    re.compile(r"\bexit\b", re.IGNORECASE),
    re.compile(r"\bagent", re.IGNORECASE),
    re.compile(r"\broster\b", re.IGNORECASE),
    re.compile(r"\bround\b", re.IGNORECASE),
    re.compile(r"\[E\]\s*Exit", re.IGNORECASE),
]

# Elicitation detection patterns
_ELICITATION_PATTERNS = [
    re.compile(r"\badvanced\b", re.IGNORECASE),
    re.compile(r"\[A\]\s*Advanced", re.IGNORECASE),
    re.compile(r"\btechnique\b", re.IGNORECASE),
    re.compile(r"\belicitation\b", re.IGNORECASE),
    re.compile(r"\bsocratic\b", re.IGNORECASE),
    re.compile(r"\b5\s*whys\b", re.IGNORECASE),
    re.compile(r"\bmind\s*mapping\b", re.IGNORECASE),
    re.compile(r"\bbrainstorming\b", re.IGNORECASE),
]

# Party Mode specific patterns (to exclude from elicitation)
_PARTY_MODE_EXCLUSION_PATTERNS = [
    re.compile(r"\bagent\b", re.IGNORECASE),
    re.compile(r"\broster\b", re.IGNORECASE),
    re.compile(r"\bselect\s+agent", re.IGNORECASE),
    re.compile(r"\bview\s+roster", re.IGNORECASE),
]


# =============================================================================
# Data Classes (Task 1)
# =============================================================================


@dataclass
class MenuContext:
    """Context for a menu in the nested menu stack.

    Attributes:
        menu_id: Unique identifier for this menu.
        parent_context: Reference to the parent menu context, or None if root.
        workflow_type: Type of workflow ("party_mode", "elicitation", "standard").
        depth_level: Current nesting level (1-indexed, 0 means no context).
    """

    menu_id: str
    parent_context: Optional[MenuContext]
    workflow_type: str  # "party_mode", "elicitation", "standard"
    depth_level: int


@dataclass
class PartyModeMenuContext(MenuContext):
    """Context for Party Mode internal menus.

    Extends MenuContext with Party Mode-specific tracking.

    Attributes:
        agent_roster: List of agent names in the current Party Mode session.
        current_round: Current discussion round number (0 = setup phase).
    """

    agent_roster: List[str] = field(default_factory=list)
    current_round: int = 0


@dataclass
class ElicitationMenuContext(MenuContext):
    """Context for Advanced Elicitation menus.

    Extends MenuContext with elicitation-specific tracking.

    Attributes:
        technique_selected: Currently selected elicitation technique, or None.
        elicitation_phase: Current phase ("technique_selection", "execution", "summary").
    """

    technique_selected: Optional[str] = None
    elicitation_phase: str = "technique_selection"


# =============================================================================
# MenuDepthTracker Class (Task 1)
# =============================================================================


class MenuDepthTracker:
    """Tracks the depth of nested menu invocations.

    Maintains a stack of MenuContext objects representing the nested menu
    hierarchy. Provides methods to push/pop contexts and check depth limits.

    Example:
        >>> tracker = MenuDepthTracker()
        >>> ctx = tracker.push_menu_context("menu-1", "standard")
        >>> print(tracker.get_current_depth())  # 1
        >>> tracker.is_depth_exceeded()  # False
    """

    def __init__(self) -> None:
        """Initialize MenuDepthTracker with empty stack."""
        self._context_stack: List[MenuContext] = []

    def push_menu_context(
        self,
        menu_id: str,
        workflow_type: str,
        context_class: Optional[type] = None,
        **kwargs: Any,
    ) -> MenuContext:
        """Push a new menu context onto the stack.

        Creates a new MenuContext (or specialized subclass) linked to the
        current top of stack (if any) and increments the depth level.

        Args:
            menu_id: Unique identifier for the new menu.
            workflow_type: Type of workflow ("party_mode", "elicitation", "standard").
            context_class: Optional MenuContext subclass to instantiate
                (e.g., PartyModeMenuContext, ElicitationMenuContext).
                Defaults to MenuContext if not specified.
            **kwargs: Additional keyword arguments passed to the context class
                constructor (e.g., agent_roster, current_round for PartyMode).

        Returns:
            The newly created MenuContext (or subclass instance).

        Example:
            >>> tracker = MenuDepthTracker()
            >>> # Standard context
            >>> ctx = tracker.push_menu_context("menu-1", "standard")
            >>> # Party Mode context with custom fields
            >>> ctx = tracker.push_menu_context(
            ...     "party-menu", "party_mode",
            ...     context_class=PartyModeMenuContext,
            ...     agent_roster=["analyst", "dev"],
            ...     current_round=1,
            ... )
        """
        # Validate workflow_type (Issue 3)
        if workflow_type not in VALID_WORKFLOW_TYPES:
            raise ValueError(
                f"Invalid workflow_type '{workflow_type}'. "
                f"Must be one of: {', '.join(sorted(VALID_WORKFLOW_TYPES))}"
            )

        # Validate elicitation_phase if provided (Issue 8)
        if "elicitation_phase" in kwargs:
            phase = kwargs["elicitation_phase"]
            if phase not in VALID_ELICITATION_PHASES:
                raise ValueError(
                    f"Invalid elicitation_phase '{phase}'. "
                    f"Must be one of: {', '.join(sorted(VALID_ELICITATION_PHASES))}"
                )

        parent = self.get_current_context()
        new_depth = len(self._context_stack) + 1

        # Use provided class or default to MenuContext
        cls = context_class if context_class is not None else MenuContext

        context = cls(
            menu_id=menu_id,
            parent_context=parent,
            workflow_type=workflow_type,
            depth_level=new_depth,
            **kwargs,
        )

        self._context_stack.append(context)
        return context

    def pop_menu_context(self) -> Optional[MenuContext]:
        """Pop the current menu context from the stack.

        Returns:
            The popped MenuContext, or None if stack was empty.
        """
        if not self._context_stack:
            return None

        return self._context_stack.pop()

    def get_current_depth(self) -> int:
        """Get the current nesting depth.

        Returns:
            Current depth (0 if stack is empty, otherwise stack size).
        """
        return len(self._context_stack)

    def get_current_context(self) -> Optional[MenuContext]:
        """Get the current (top of stack) menu context.

        Returns:
            The MenuContext at top of stack, or None if stack is empty.
        """
        if not self._context_stack:
            return None

        return self._context_stack[-1]

    def is_depth_exceeded(self) -> bool:
        """Check if the current depth exceeds the maximum allowed.

        Returns:
            True if depth > MAX_NESTED_DEPTH (3), False otherwise.
        """
        return len(self._context_stack) > MAX_NESTED_DEPTH


# =============================================================================
# Party Mode Detection and Handling (Task 2)
# =============================================================================


def detect_party_mode_menu(detection_result: MenuDetectionResult) -> bool:
    """Detect if the menu is a Party Mode internal menu.

    Checks for Party Mode-specific patterns:
    - [E] Exit option
    - Agent selection options
    - Round controls
    - Roster management

    Args:
        detection_result: The menu detection result to analyze.

    Returns:
        True if the menu appears to be a Party Mode internal menu.
    """
    # Non-detected menus are not Party Mode menus
    if not detection_result.menu_detected:
        return False

    raw_input = detection_result.raw_input
    options = detection_result.options

    # Check raw input for Party Mode patterns
    for pattern in _PARTY_MODE_PATTERNS:
        if pattern.search(raw_input):
            return True

    # Check options for Party Mode keywords
    options_text = " ".join(options).lower()
    party_mode_keywords = {"exit", "agent", "roster", "round", "select agent", "view roster"}

    for keyword in party_mode_keywords:
        if keyword in options_text:
            return True

    return False


def handle_party_mode_selection(
    context: PartyModeMenuContext, options: List[str]
) -> str:
    """Handle selection within a Party Mode menu.

    Applies Party Mode-specific selection logic:
    - During active rounds (round > 0), prefer Continue
    - During setup (round = 0), prefer agent selection or Exit
    - Consider roster context for agent-related menus

    Args:
        context: The current Party Mode menu context.
        options: List of available menu options.

    Returns:
        The selected option string, or empty string if no options.
    """
    if not options:
        return ""

    options_lower = [opt.lower() for opt in options]

    # During active rounds, prefer Continue
    if context.current_round > 0:
        for i, opt_lower in enumerate(options_lower):
            if "continue" in opt_lower:
                return options[i]

    # During setup phase (round = 0)
    if context.current_round == 0:
        # If no agents in roster, prefer agent selection
        if not context.agent_roster:
            for i, opt_lower in enumerate(options_lower):
                if "agent" in opt_lower or "select" in opt_lower:
                    return options[i]
            # Fallback to Exit
            for i, opt_lower in enumerate(options_lower):
                if "exit" in opt_lower:
                    return options[i]

    # With only one agent, might want to add more or continue
    if len(context.agent_roster) == 1:
        for i, opt_lower in enumerate(options_lower):
            if "add" in opt_lower or "more" in opt_lower:
                return options[i]
        for i, opt_lower in enumerate(options_lower):
            if "continue" in opt_lower:
                return options[i]

    # Default: return first option
    return options[0]


# =============================================================================
# Advanced Elicitation Detection and Handling (Task 3)
# =============================================================================


def detect_elicitation_menu(detection_result: MenuDetectionResult) -> bool:
    """Detect if the menu is an Advanced Elicitation menu.

    Checks for elicitation-specific patterns:
    - [A] Advanced option
    - Technique selection options (Socratic, 5 Whys, Mind mapping, etc.)
    - Elicitation keywords

    Excludes Party Mode menus that have overlapping patterns.

    Args:
        detection_result: The menu detection result to analyze.

    Returns:
        True if the menu appears to be an Advanced Elicitation menu.
    """
    # Non-detected menus are not elicitation menus
    if not detection_result.menu_detected:
        return False

    raw_input = detection_result.raw_input
    options = detection_result.options

    # Check for Party Mode exclusion patterns first
    for pattern in _PARTY_MODE_EXCLUSION_PATTERNS:
        if pattern.search(raw_input):
            return False

    options_text = " ".join(options).lower()
    for pattern in _PARTY_MODE_EXCLUSION_PATTERNS:
        if pattern.search(options_text):
            return False

    # Check raw input for elicitation patterns
    for pattern in _ELICITATION_PATTERNS:
        if pattern.search(raw_input):
            return True

    # Check options for elicitation keywords
    elicitation_keywords = {
        "advanced",
        "technique",
        "elicitation",
        "socratic",
        "5 whys",
        "mind mapping",
        "brainstorming",
    }

    for keyword in elicitation_keywords:
        if keyword in options_text:
            return True

    return False


def handle_elicitation_selection(
    context: ElicitationMenuContext, options: List[str]
) -> str:
    """Handle selection within an Advanced Elicitation menu.

    Applies elicitation-specific selection logic based on phase:
    - technique_selection: Select a technique option
    - execution: Prefer Continue or technique-appropriate options
    - summary: Prefer Complete or Review

    Args:
        context: The current Elicitation menu context.
        options: List of available menu options.

    Returns:
        The selected option string, or empty string if no options.
    """
    if not options:
        return ""

    options_lower = [opt.lower() for opt in options]
    phase = context.elicitation_phase

    # Phase: technique_selection
    if phase == "technique_selection":
        # Return the first technique option (any of them is valid)
        return options[0]

    # Phase: execution
    if phase == "execution":
        # Prefer Continue
        for i, opt_lower in enumerate(options_lower):
            if "continue" in opt_lower:
                return options[i]

        # Consider technique-appropriate options
        technique = (context.technique_selected or "").lower()
        if technique:
            # For brainstorming, prefer "Add idea" (with "add" taking priority)
            if "brainstorm" in technique:
                # First, look for options with "add"
                for i, opt_lower in enumerate(options_lower):
                    if "add" in opt_lower:
                        return options[i]
                # Then, look for options with "idea" alone
                for i, opt_lower in enumerate(options_lower):
                    if "idea" in opt_lower:
                        return options[i]
                # Then, look for "complete brainstorm"
                for i, opt_lower in enumerate(options_lower):
                    if "complete" in opt_lower and "brainstorm" in opt_lower:
                        return options[i]

        # Avoid Exit in execution phase
        for i, opt_lower in enumerate(options_lower):
            if "exit" not in opt_lower:
                return options[i]

        # Default: first option
        return options[0]

    # Phase: summary
    if phase == "summary":
        # Prefer Complete
        for i, opt_lower in enumerate(options_lower):
            if "complete" in opt_lower:
                return options[i]
        # Fallback to Review
        for i, opt_lower in enumerate(options_lower):
            if "review" in opt_lower:
                return options[i]
        # Default: first option
        return options[0]

    # Unknown phase: return first option
    return options[0]


# =============================================================================
# Task 4: Parent State Restoration
# =============================================================================

# Logger for nested menu operations
_logger = logging.getLogger(__name__)


@dataclass
class ParentState:
    """State of parent menu to restore after nested menu completes.

    Captures all necessary state before entering a nested menu so that
    the parent menu can be resumed correctly after the nested menu exits.

    Attributes:
        menu_context: The MenuContext of the parent menu.
        selection_history: List of selections made in the parent menu.
        continuation_markers: Dictionary of markers for workflow continuation.
        timestamp: When this state was saved.
    """

    menu_context: MenuContext
    selection_history: List[str]
    continuation_markers: Dict[str, Any]
    timestamp: datetime


class StateManager:
    """Manages saving and restoring parent menu state.

    Provides methods to save parent state before entering nested menus
    and restore it after returning. Uses a stack to support up to 3 levels
    of nesting (matching MAX_NESTED_DEPTH). Handles error paths gracefully.

    Example:
        >>> manager = StateManager()
        >>> state = ParentState(...)
        >>> manager.save_parent_state(state)
        >>> # Enter nested menu...
        >>> restored = manager.restore_parent_state()
    """

    def __init__(self) -> None:
        """Initialize StateManager with empty state stack."""
        self._state_stack: List[ParentState] = []

    def save_parent_state(self, state: ParentState) -> None:
        """Save parent state before entering nested menu.

        Pushes the state onto the stack. Supports up to 3 levels of nesting
        (matching MAX_NESTED_DEPTH).

        Args:
            state: The ParentState to save.
        """
        self._state_stack.append(state)

    def restore_parent_state(self) -> Optional[ParentState]:
        """Restore saved parent state and remove it from stack.

        Pops and returns the most recently saved state.

        Returns:
            The most recently saved ParentState, or None if stack is empty.
        """
        if not self._state_stack:
            return None
        return self._state_stack.pop()

    def has_saved_state(self) -> bool:
        """Check if there is saved state.

        Returns:
            True if at least one state is saved, False otherwise.
        """
        return len(self._state_stack) > 0

    def clear_saved_state(self) -> None:
        """Clear all saved states without returning them.

        Safe to call even if no state is saved.
        """
        self._state_stack.clear()


# =============================================================================
# Task 5: Depth Exceeded Escalation
# =============================================================================


@dataclass
class UserEscalation:
    """Information for escalating to user when automation cannot proceed.

    Used when menu depth exceeds limits or other conditions require
    user intervention.

    Attributes:
        reason: Description of why escalation is needed.
        context_stack: List of menu IDs in the current context stack.
        suggestion: Suggested action for the user.
        severity: Severity level ("info", "warning", "error").
    """

    reason: str
    context_stack: List[str]
    suggestion: str
    severity: str  # "info", "warning", "error"


def handle_depth_exceeded(tracker: MenuDepthTracker) -> UserEscalation:
    """Handle the case when menu nesting depth exceeds the limit.

    Logs a warning and generates user-friendly escalation information
    with navigation suggestions.

    Args:
        tracker: The MenuDepthTracker that has exceeded depth.

    Returns:
        UserEscalation with details about the depth exceeded condition.
    """
    # Build context stack from tracker
    context_stack: List[str] = []
    context = tracker.get_current_context()

    # Traverse up the parent chain to build the stack
    while context is not None:
        context_stack.insert(0, context.menu_id)
        context = context.parent_context

    current_depth = tracker.get_current_depth()

    # Log warning
    _logger.warning(
        "Menu nesting depth exceeded: depth=%d, max=%d, stack=%s",
        current_depth,
        MAX_NESTED_DEPTH,
        context_stack,
    )

    # Generate user-friendly message
    reason = (
        f"Maximum menu nesting depth ({MAX_NESTED_DEPTH}) exceeded. "
        f"Current depth: {current_depth}."
    )

    suggestion = (
        "Please use Exit or Back to return to a parent menu before "
        "navigating to additional nested menus."
    )

    return UserEscalation(
        reason=reason,
        context_stack=context_stack,
        suggestion=suggestion,
        severity="warning",
    )


# =============================================================================
# Issue 9: Context Handler Routing
# =============================================================================


def route_to_context_handler(
    detection_result: MenuDetectionResult,
) -> tuple[str, Optional[type]]:
    """Route a menu detection result to the appropriate context handler.

    Detects whether the menu is a Party Mode, Elicitation, or standard menu
    and returns the handler type and context class to use.

    Priority order:
    1. Party Mode detection (agent, roster, round patterns)
    2. Elicitation detection (technique, advanced patterns) - excludes Party Mode
    3. Standard handler (default)

    Args:
        detection_result: The menu detection result to analyze.

    Returns:
        Tuple of (handler_type, context_class) where:
        - handler_type: "party_mode", "elicitation", or "standard"
        - context_class: PartyModeMenuContext, ElicitationMenuContext, or None
            (None indicates use default MenuContext)

    Example:
        >>> detection = MenuDetectionResult.detected(...)
        >>> handler_type, context_class = route_to_context_handler(detection)
        >>> if handler_type == "party_mode":
        ...     # Use handle_party_mode_selection with PartyModeMenuContext
        ...     pass
    """
    # Check Party Mode first (takes precedence)
    if detect_party_mode_menu(detection_result):
        return ("party_mode", PartyModeMenuContext)

    # Check Elicitation (excludes Party Mode patterns internally)
    if detect_elicitation_menu(detection_result):
        return ("elicitation", ElicitationMenuContext)

    # Default to standard handler
    return ("standard", None)
