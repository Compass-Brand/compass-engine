"""Tests for Nested Menu Handling - Story 2b-4.

TDD tests for:
- Task 1: MenuDepthTracker with MenuContext dataclass
- Task 2: Party Mode Context Handling
- Task 3: Advanced Elicitation Context Handling
- Task 4: Parent State Restoration (ParentState, StateManager)
- Task 5: Depth Exceeded Escalation (UserEscalation, handle_depth_exceeded)
"""

import logging
from datetime import datetime

import pytest

from pcmrp_tools.bmad_automation.nested_menu import (
    MAX_NESTED_DEPTH,
    MenuContext,
    MenuDepthTracker,
    PartyModeMenuContext,
    ElicitationMenuContext,
    ParentState,
    StateManager,
    UserEscalation,
    detect_party_mode_menu,
    handle_party_mode_selection,
    detect_elicitation_menu,
    handle_elicitation_selection,
    handle_depth_exceeded,
)
from pcmrp_tools.bmad_automation.menu_participation_engine import (
    MenuDetectionResult,
    MenuType,
)


# =============================================================================
# Task 1: MenuDepthTracker Tests
# =============================================================================


class TestMaxNestedDepthConstant:
    """Tests for MAX_NESTED_DEPTH constant."""

    def test_max_nested_depth_is_3(self) -> None:
        """MAX_NESTED_DEPTH should be 3 per requirements."""
        assert MAX_NESTED_DEPTH == 3


class TestMenuContextDataclass:
    """Tests for MenuContext dataclass."""

    def test_menu_context_creation_minimal(self) -> None:
        """MenuContext can be created with required fields."""
        ctx = MenuContext(
            menu_id="menu-1",
            parent_context=None,
            workflow_type="standard",
            depth_level=0,
        )
        assert ctx.menu_id == "menu-1"
        assert ctx.parent_context is None
        assert ctx.workflow_type == "standard"
        assert ctx.depth_level == 0

    def test_menu_context_with_parent(self) -> None:
        """MenuContext can reference a parent context."""
        parent = MenuContext(
            menu_id="parent-menu",
            parent_context=None,
            workflow_type="standard",
            depth_level=0,
        )
        child = MenuContext(
            menu_id="child-menu",
            parent_context=parent,
            workflow_type="party_mode",
            depth_level=1,
        )
        assert child.parent_context is parent
        assert child.parent_context.menu_id == "parent-menu"
        assert child.depth_level == 1

    def test_menu_context_workflow_types(self) -> None:
        """MenuContext supports party_mode, elicitation, standard workflow types."""
        for workflow_type in ["party_mode", "elicitation", "standard"]:
            ctx = MenuContext(
                menu_id=f"menu-{workflow_type}",
                parent_context=None,
                workflow_type=workflow_type,
                depth_level=0,
            )
            assert ctx.workflow_type == workflow_type


class TestMenuDepthTrackerInit:
    """Tests for MenuDepthTracker initialization."""

    def test_tracker_initial_state(self) -> None:
        """MenuDepthTracker starts with empty stack and depth 0."""
        tracker = MenuDepthTracker()
        assert tracker.get_current_depth() == 0
        assert tracker.get_current_context() is None

    def test_tracker_is_not_exceeded_initially(self) -> None:
        """MenuDepthTracker is not exceeded when empty."""
        tracker = MenuDepthTracker()
        assert tracker.is_depth_exceeded() is False


class TestMenuDepthTrackerPush:
    """Tests for MenuDepthTracker.push_menu_context()."""

    def test_push_single_context(self) -> None:
        """Push a single menu context."""
        tracker = MenuDepthTracker()
        ctx = tracker.push_menu_context("menu-1", "standard")
        assert ctx.menu_id == "menu-1"
        assert ctx.workflow_type == "standard"
        assert ctx.depth_level == 1
        assert ctx.parent_context is None
        assert tracker.get_current_depth() == 1

    def test_push_nested_contexts(self) -> None:
        """Push multiple nested contexts."""
        tracker = MenuDepthTracker()
        ctx1 = tracker.push_menu_context("menu-1", "standard")
        ctx2 = tracker.push_menu_context("menu-2", "party_mode")

        assert ctx2.parent_context is ctx1
        assert ctx2.depth_level == 2
        assert tracker.get_current_depth() == 2

    def test_push_up_to_max_depth(self) -> None:
        """Push contexts up to MAX_NESTED_DEPTH (3)."""
        tracker = MenuDepthTracker()
        for i in range(MAX_NESTED_DEPTH):
            ctx = tracker.push_menu_context(f"menu-{i}", "standard")
            assert ctx.depth_level == i + 1

        assert tracker.get_current_depth() == MAX_NESTED_DEPTH
        assert tracker.is_depth_exceeded() is False

    def test_push_exceeds_max_depth(self) -> None:
        """Depth is exceeded after pushing beyond MAX_NESTED_DEPTH."""
        tracker = MenuDepthTracker()
        for i in range(MAX_NESTED_DEPTH):
            tracker.push_menu_context(f"menu-{i}", "standard")

        # Push one more beyond max
        tracker.push_menu_context("menu-over", "standard")
        assert tracker.get_current_depth() == MAX_NESTED_DEPTH + 1
        assert tracker.is_depth_exceeded() is True


class TestMenuDepthTrackerPop:
    """Tests for MenuDepthTracker.pop_menu_context()."""

    def test_pop_empty_stack(self) -> None:
        """Pop from empty stack returns None."""
        tracker = MenuDepthTracker()
        result = tracker.pop_menu_context()
        assert result is None
        assert tracker.get_current_depth() == 0

    def test_pop_single_context(self) -> None:
        """Pop the only context from stack."""
        tracker = MenuDepthTracker()
        pushed = tracker.push_menu_context("menu-1", "standard")
        popped = tracker.pop_menu_context()

        assert popped is pushed
        assert tracker.get_current_depth() == 0
        assert tracker.get_current_context() is None

    def test_pop_nested_contexts(self) -> None:
        """Pop nested contexts in LIFO order."""
        tracker = MenuDepthTracker()
        ctx1 = tracker.push_menu_context("menu-1", "standard")
        ctx2 = tracker.push_menu_context("menu-2", "party_mode")

        popped2 = tracker.pop_menu_context()
        assert popped2 is ctx2
        assert tracker.get_current_depth() == 1
        assert tracker.get_current_context() is ctx1

        popped1 = tracker.pop_menu_context()
        assert popped1 is ctx1
        assert tracker.get_current_depth() == 0

    def test_pop_after_exceeding_depth(self) -> None:
        """Pop restores depth_exceeded state when going back within limits."""
        tracker = MenuDepthTracker()
        for i in range(MAX_NESTED_DEPTH + 1):
            tracker.push_menu_context(f"menu-{i}", "standard")

        assert tracker.is_depth_exceeded() is True

        tracker.pop_menu_context()  # Now at MAX_NESTED_DEPTH
        assert tracker.is_depth_exceeded() is False


class TestMenuDepthTrackerGetters:
    """Tests for MenuDepthTracker getter methods."""

    def test_get_current_depth_changes_with_push_pop(self) -> None:
        """get_current_depth reflects push and pop operations."""
        tracker = MenuDepthTracker()

        assert tracker.get_current_depth() == 0

        tracker.push_menu_context("menu-1", "standard")
        assert tracker.get_current_depth() == 1

        tracker.push_menu_context("menu-2", "elicitation")
        assert tracker.get_current_depth() == 2

        tracker.pop_menu_context()
        assert tracker.get_current_depth() == 1

    def test_get_current_context_returns_top_of_stack(self) -> None:
        """get_current_context returns the most recently pushed context."""
        tracker = MenuDepthTracker()

        assert tracker.get_current_context() is None

        ctx1 = tracker.push_menu_context("menu-1", "standard")
        assert tracker.get_current_context() is ctx1

        ctx2 = tracker.push_menu_context("menu-2", "party_mode")
        assert tracker.get_current_context() is ctx2

        tracker.pop_menu_context()
        assert tracker.get_current_context() is ctx1


# =============================================================================
# Task 2: Party Mode Context Handling Tests
# =============================================================================


class TestPartyModeMenuContext:
    """Tests for PartyModeMenuContext dataclass."""

    def test_party_mode_context_creation(self) -> None:
        """PartyModeMenuContext extends MenuContext with agent roster and round."""
        ctx = PartyModeMenuContext(
            menu_id="party-menu-1",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
            agent_roster=["analyst", "architect", "pm"],
            current_round=1,
        )
        assert ctx.menu_id == "party-menu-1"
        assert ctx.workflow_type == "party_mode"
        assert ctx.agent_roster == ["analyst", "architect", "pm"]
        assert ctx.current_round == 1

    def test_party_mode_context_empty_roster(self) -> None:
        """PartyModeMenuContext can have empty roster initially."""
        ctx = PartyModeMenuContext(
            menu_id="party-menu-empty",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
            agent_roster=[],
            current_round=0,
        )
        assert ctx.agent_roster == []
        assert ctx.current_round == 0

    def test_party_mode_context_inherits_from_menu_context(self) -> None:
        """PartyModeMenuContext is a subclass of MenuContext."""
        ctx = PartyModeMenuContext(
            menu_id="party-menu",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
            agent_roster=["dev"],
            current_round=1,
        )
        assert isinstance(ctx, MenuContext)


class TestDetectPartyModeMenu:
    """Tests for detect_party_mode_menu function."""

    def test_detect_party_mode_with_exit_option(self) -> None:
        """Party Mode menus typically have [E] Exit option."""
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Select agent", "View roster", "Exit"],
            breakdown={"test": 85},
            raw_input="[A] Select agent [V] View roster [E] Exit",
        )
        assert detect_party_mode_menu(detection) is True

    def test_detect_party_mode_with_agent_selection(self) -> None:
        """Party Mode menus may present agent selections."""
        detection = MenuDetectionResult.detected(
            confidence=80,
            menu_type=MenuType.NUMBERED,
            options=["analyst", "architect", "pm", "dev"],
            breakdown={"test": 80},
            raw_input="Select agents: [1] analyst [2] architect [3] pm [4] dev",
        )
        # Agent selection patterns indicate Party Mode
        assert detect_party_mode_menu(detection) is True

    def test_detect_party_mode_with_round_controls(self) -> None:
        """Party Mode menus may have round controls."""
        detection = MenuDetectionResult.detected(
            confidence=75,
            menu_type=MenuType.APC,
            options=["Continue round", "End discussion", "Exit"],
            breakdown={"test": 75},
            raw_input="Round 3: [C] Continue round [E] End discussion [X] Exit",
        )
        assert detect_party_mode_menu(detection) is True

    def test_detect_party_mode_false_for_standard_menu(self) -> None:
        """Standard menus without Party Mode patterns are not detected."""
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 90},
            raw_input="[Y] Yes [N] No",
        )
        assert detect_party_mode_menu(detection) is False

    def test_detect_party_mode_not_detected_result(self) -> None:
        """Non-detected menus are not Party Mode menus."""
        detection = MenuDetectionResult.not_detected(
            confidence=40,
            breakdown={"test": 40},
            raw_input="Some random text",
        )
        assert detect_party_mode_menu(detection) is False


class TestHandlePartyModeSelection:
    """Tests for handle_party_mode_selection function."""

    def test_handle_party_mode_selection_continue(self) -> None:
        """Continue option is preferred in Party Mode during active rounds."""
        context = PartyModeMenuContext(
            menu_id="party-menu",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
            agent_roster=["analyst", "architect"],
            current_round=2,
        )
        options = ["Continue", "Exit", "View"]

        selection = handle_party_mode_selection(context, options)
        assert selection == "Continue"

    def test_handle_party_mode_selection_exit_when_round_zero(self) -> None:
        """Exit is appropriate when round is 0 (setup phase)."""
        context = PartyModeMenuContext(
            menu_id="party-menu",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
            agent_roster=[],
            current_round=0,
        )
        options = ["Continue", "Exit", "Select agents"]

        # When round is 0 and no agents, should prefer Select agents or Exit
        selection = handle_party_mode_selection(context, options)
        assert selection in ["Select agents", "Exit"]

    def test_handle_party_mode_selection_empty_options(self) -> None:
        """Empty options returns empty string."""
        context = PartyModeMenuContext(
            menu_id="party-menu",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
            agent_roster=["dev"],
            current_round=1,
        )
        options: list[str] = []

        selection = handle_party_mode_selection(context, options)
        assert selection == ""

    def test_handle_party_mode_selection_uses_roster_context(self) -> None:
        """Selection logic considers agent roster for agent-related menus."""
        context = PartyModeMenuContext(
            menu_id="party-menu",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
            agent_roster=["analyst"],  # Only analyst selected
            current_round=1,
        )
        options = ["Add more agents", "Continue with analyst", "Exit"]

        # With only one agent, might prefer to add more or continue
        selection = handle_party_mode_selection(context, options)
        assert selection in ["Add more agents", "Continue with analyst"]


# =============================================================================
# Task 3: Advanced Elicitation Context Handling Tests
# =============================================================================


class TestElicitationMenuContext:
    """Tests for ElicitationMenuContext dataclass."""

    def test_elicitation_context_creation(self) -> None:
        """ElicitationMenuContext extends MenuContext with technique and phase."""
        ctx = ElicitationMenuContext(
            menu_id="elicit-menu-1",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected=None,
            elicitation_phase="technique_selection",
        )
        assert ctx.menu_id == "elicit-menu-1"
        assert ctx.workflow_type == "elicitation"
        assert ctx.technique_selected is None
        assert ctx.elicitation_phase == "technique_selection"

    def test_elicitation_context_with_technique(self) -> None:
        """ElicitationMenuContext can track selected technique."""
        ctx = ElicitationMenuContext(
            menu_id="elicit-menu-2",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected="socratic_questioning",
            elicitation_phase="execution",
        )
        assert ctx.technique_selected == "socratic_questioning"
        assert ctx.elicitation_phase == "execution"

    def test_elicitation_context_phases(self) -> None:
        """ElicitationMenuContext supports all elicitation phases."""
        for phase in ["technique_selection", "execution", "summary"]:
            ctx = ElicitationMenuContext(
                menu_id=f"elicit-{phase}",
                parent_context=None,
                workflow_type="elicitation",
                depth_level=1,
                technique_selected=None,
                elicitation_phase=phase,
            )
            assert ctx.elicitation_phase == phase

    def test_elicitation_context_inherits_from_menu_context(self) -> None:
        """ElicitationMenuContext is a subclass of MenuContext."""
        ctx = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected=None,
            elicitation_phase="technique_selection",
        )
        assert isinstance(ctx, MenuContext)


class TestDetectElicitationMenu:
    """Tests for detect_elicitation_menu function."""

    def test_detect_elicitation_with_advanced_option(self) -> None:
        """Elicitation menus may have [A] Advanced option."""
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Continue", "Advanced", "Exit"],
            breakdown={"test": 85},
            raw_input="[C] Continue [A] Advanced [E] Exit",
        )
        assert detect_elicitation_menu(detection) is True

    def test_detect_elicitation_with_technique_selection(self) -> None:
        """Elicitation menus present technique options."""
        detection = MenuDetectionResult.detected(
            confidence=80,
            menu_type=MenuType.NUMBERED,
            options=["Socratic questioning", "5 Whys", "Mind mapping", "Brainstorming"],
            breakdown={"test": 80},
            raw_input="Select elicitation technique: [1] Socratic questioning [2] 5 Whys [3] Mind mapping [4] Brainstorming",
        )
        assert detect_elicitation_menu(detection) is True

    def test_detect_elicitation_false_for_party_mode(self) -> None:
        """Party Mode menus are not elicitation menus."""
        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Select agent", "View roster", "Exit"],
            breakdown={"test": 85},
            raw_input="[A] Select agent [V] View roster [E] Exit",
        )
        # Has Exit but no elicitation patterns
        result = detect_elicitation_menu(detection)
        # Party Mode patterns (agent, roster) should not trigger elicitation
        assert result is False

    def test_detect_elicitation_not_detected_result(self) -> None:
        """Non-detected menus are not elicitation menus."""
        detection = MenuDetectionResult.not_detected(
            confidence=30,
            breakdown={"test": 30},
            raw_input="Random text without menu",
        )
        assert detect_elicitation_menu(detection) is False

    def test_detect_elicitation_standard_yvn_menu(self) -> None:
        """Standard YVN menu without elicitation patterns is not elicitation."""
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 90},
            raw_input="[Y] Yes [N] No",
        )
        assert detect_elicitation_menu(detection) is False


class TestHandleElicitationSelection:
    """Tests for handle_elicitation_selection function."""

    def test_handle_elicitation_technique_selection_phase(self) -> None:
        """During technique selection, should select a technique option."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected=None,
            elicitation_phase="technique_selection",
        )
        options = ["Socratic questioning", "5 Whys", "Mind mapping"]

        selection = handle_elicitation_selection(context, options)
        # Should select one of the techniques
        assert selection in options

    def test_handle_elicitation_execution_phase_continue(self) -> None:
        """During execution phase, prefer continue if available."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected="5 Whys",
            elicitation_phase="execution",
        )
        options = ["Continue", "Restart", "Exit"]

        selection = handle_elicitation_selection(context, options)
        assert selection == "Continue"

    def test_handle_elicitation_summary_phase_complete(self) -> None:
        """During summary phase, prefer completion options."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected="Mind mapping",
            elicitation_phase="summary",
        )
        options = ["Complete", "Review", "Restart"]

        selection = handle_elicitation_selection(context, options)
        assert selection in ["Complete", "Review"]

    def test_handle_elicitation_empty_options(self) -> None:
        """Empty options returns empty string."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected=None,
            elicitation_phase="technique_selection",
        )
        options: list[str] = []

        selection = handle_elicitation_selection(context, options)
        assert selection == ""

    def test_handle_elicitation_uses_technique_context(self) -> None:
        """Selection considers already-selected technique."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected="Brainstorming",
            elicitation_phase="execution",
        )
        options = ["Add idea", "Complete brainstorm", "Exit"]

        selection = handle_elicitation_selection(context, options)
        # Should prefer technique-appropriate options
        assert selection in ["Add idea", "Complete brainstorm"]


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Edge case tests for nested menu handling."""

    def test_deeply_nested_contexts_parent_chain(self) -> None:
        """Verify parent chain is maintained through deep nesting."""
        tracker = MenuDepthTracker()
        contexts = []

        for i in range(5):  # Beyond max depth
            ctx = tracker.push_menu_context(f"menu-{i}", "standard")
            contexts.append(ctx)

        # Verify parent chain
        for i, ctx in enumerate(contexts):
            if i == 0:
                assert ctx.parent_context is None
            else:
                assert ctx.parent_context is contexts[i - 1]

    def test_pop_all_then_push(self) -> None:
        """Tracker works correctly after popping all and pushing again."""
        tracker = MenuDepthTracker()

        # Push and pop all
        tracker.push_menu_context("menu-1", "standard")
        tracker.push_menu_context("menu-2", "standard")
        tracker.pop_menu_context()
        tracker.pop_menu_context()

        assert tracker.get_current_depth() == 0

        # Push again
        new_ctx = tracker.push_menu_context("menu-new", "elicitation")
        assert new_ctx.depth_level == 1
        assert new_ctx.parent_context is None

    def test_mixed_workflow_types_in_stack(self) -> None:
        """Different workflow types can be nested."""
        tracker = MenuDepthTracker()

        ctx1 = tracker.push_menu_context("standard-menu", "standard")
        ctx2 = tracker.push_menu_context("party-menu", "party_mode")
        ctx3 = tracker.push_menu_context("elicit-menu", "elicitation")

        assert ctx1.workflow_type == "standard"
        assert ctx2.workflow_type == "party_mode"
        assert ctx3.workflow_type == "elicitation"
        assert ctx3.parent_context.workflow_type == "party_mode"


# =============================================================================
# Additional Coverage Tests for Selection Logic Edge Cases
# =============================================================================


class TestPartyModeSelectionEdgeCases:
    """Additional tests for Party Mode selection edge cases."""

    def test_party_mode_no_continue_in_active_round(self) -> None:
        """When active round but no Continue, returns first option."""
        context = PartyModeMenuContext(
            menu_id="party-menu",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
            agent_roster=["analyst", "dev"],
            current_round=3,
        )
        options = ["View details", "End discussion", "Skip"]

        selection = handle_party_mode_selection(context, options)
        # No Continue available, should return first option
        assert selection == "View details"

    def test_party_mode_round_zero_with_agents(self) -> None:
        """Round 0 with existing agents returns first option."""
        context = PartyModeMenuContext(
            menu_id="party-menu",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
            agent_roster=["analyst", "pm", "dev"],  # Full roster
            current_round=0,
        )
        options = ["Start discussion", "Review roster", "Exit"]

        selection = handle_party_mode_selection(context, options)
        # Has agents, round 0 - should return first option
        assert selection == "Start discussion"

    def test_party_mode_single_agent_continue(self) -> None:
        """Single agent prefers Continue if Add not available."""
        context = PartyModeMenuContext(
            menu_id="party-menu",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
            agent_roster=["analyst"],
            current_round=1,
        )
        options = ["Continue discussion", "End", "Exit"]

        selection = handle_party_mode_selection(context, options)
        assert selection == "Continue discussion"


class TestElicitationSelectionEdgeCases:
    """Additional tests for elicitation selection edge cases."""

    def test_elicitation_execution_no_continue_avoids_exit(self) -> None:
        """In execution, avoids Exit when Continue not available."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected="5 Whys",
            elicitation_phase="execution",
        )
        options = ["Dig deeper", "Exit"]

        selection = handle_elicitation_selection(context, options)
        # Should avoid Exit
        assert selection == "Dig deeper"

    def test_elicitation_execution_only_exit_available(self) -> None:
        """If only Exit available in execution, returns Exit."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected="5 Whys",
            elicitation_phase="execution",
        )
        options = ["Exit"]

        selection = handle_elicitation_selection(context, options)
        assert selection == "Exit"

    def test_elicitation_summary_review_fallback(self) -> None:
        """In summary, falls back to Review if Complete not available."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected="Socratic questioning",
            elicitation_phase="summary",
        )
        options = ["Review findings", "Restart", "Exit"]

        selection = handle_elicitation_selection(context, options)
        assert selection == "Review findings"

    def test_elicitation_summary_no_complete_or_review(self) -> None:
        """In summary with no Complete/Review, returns first option."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected="Mind mapping",
            elicitation_phase="summary",
        )
        options = ["Export results", "Share", "Exit"]

        selection = handle_elicitation_selection(context, options)
        assert selection == "Export results"

    def test_elicitation_unknown_phase_returns_first(self) -> None:
        """Unknown phase returns first option."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected=None,
            elicitation_phase="unknown_phase",
        )
        options = ["Option A", "Option B", "Option C"]

        selection = handle_elicitation_selection(context, options)
        assert selection == "Option A"

    def test_elicitation_execution_brainstorm_add_idea(self) -> None:
        """Brainstorming technique prefers Add idea option."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected="Brainstorming",
            elicitation_phase="execution",
        )
        options = ["View ideas", "Add new idea", "Complete brainstorm", "Exit"]

        selection = handle_elicitation_selection(context, options)
        assert selection == "Add new idea"

    def test_elicitation_execution_brainstorm_complete(self) -> None:
        """Brainstorming complete option when Add not available."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected="Brainstorming",
            elicitation_phase="execution",
        )
        options = ["View list", "Complete brainstorm", "Exit"]

        selection = handle_elicitation_selection(context, options)
        assert selection == "Complete brainstorm"

    def test_elicitation_execution_no_technique(self) -> None:
        """Execution phase with no technique falls back to first non-exit."""
        context = ElicitationMenuContext(
            menu_id="elicit-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=1,
            technique_selected=None,
            elicitation_phase="execution",
        )
        options = ["Proceed", "Exit"]

        selection = handle_elicitation_selection(context, options)
        assert selection == "Proceed"


class TestDetectionEdgeCases:
    """Additional tests for detection function edge cases."""

    def test_detect_party_mode_roster_in_options(self) -> None:
        """Detect Party Mode via roster keyword in options."""
        detection = MenuDetectionResult.detected(
            confidence=80,
            menu_type=MenuType.APC,
            options=["View current roster", "Continue"],
            breakdown={"test": 80},
            raw_input="[V] View current roster [C] Continue",
        )
        assert detect_party_mode_menu(detection) is True

    def test_detect_elicitation_technique_keyword(self) -> None:
        """Detect elicitation via technique keyword in options."""
        detection = MenuDetectionResult.detected(
            confidence=75,
            menu_type=MenuType.NUMBERED,
            options=["Use technique A", "Use technique B"],
            breakdown={"test": 75},
            raw_input="Select your technique: [1] Use technique A [2] Use technique B",
        )
        assert detect_elicitation_menu(detection) is True

    def test_detect_elicitation_excludes_party_mode_options(self) -> None:
        """Elicitation detection excludes menus with Party Mode keywords in options."""
        detection = MenuDetectionResult.detected(
            confidence=80,
            menu_type=MenuType.APC,
            options=["Select agent", "Advanced"],  # Has both, but agent wins
            breakdown={"test": 80},
            raw_input="[S] Select agent [A] Advanced",
        )
        # Has "agent" in options, should be excluded from elicitation
        assert detect_elicitation_menu(detection) is False


# =============================================================================
# Task 4: ParentState and StateManager Tests
# =============================================================================


class TestParentState:
    """Tests for ParentState dataclass."""

    def test_parent_state_creation(self) -> None:
        """ParentState can be created with all required fields."""
        menu_ctx = MenuContext(
            menu_id="parent-menu",
            parent_context=None,
            workflow_type="standard",
            depth_level=1,
        )
        state = ParentState(
            menu_context=menu_ctx,
            selection_history=["option1", "option2"],
            continuation_markers={"marker1": "value1"},
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
        )
        assert state.menu_context is menu_ctx
        assert state.selection_history == ["option1", "option2"]
        assert state.continuation_markers == {"marker1": "value1"}
        assert state.timestamp == datetime(2025, 1, 1, 12, 0, 0)

    def test_parent_state_empty_history(self) -> None:
        """ParentState can have empty selection history."""
        menu_ctx = MenuContext(
            menu_id="new-menu",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=1,
        )
        state = ParentState(
            menu_context=menu_ctx,
            selection_history=[],
            continuation_markers={},
            timestamp=datetime.now(),
        )
        assert state.selection_history == []
        assert state.continuation_markers == {}

    def test_parent_state_with_nested_markers(self) -> None:
        """ParentState continuation_markers can contain nested structures."""
        menu_ctx = MenuContext(
            menu_id="complex-menu",
            parent_context=None,
            workflow_type="elicitation",
            depth_level=2,
        )
        markers = {
            "phase": "execution",
            "nested": {"key1": "val1", "key2": 42},
            "list_data": [1, 2, 3],
        }
        state = ParentState(
            menu_context=menu_ctx,
            selection_history=["A", "B", "C"],
            continuation_markers=markers,
            timestamp=datetime.now(),
        )
        assert state.continuation_markers["nested"]["key1"] == "val1"
        assert state.continuation_markers["list_data"] == [1, 2, 3]


class TestStateManager:
    """Tests for StateManager class."""

    def test_state_manager_initial_state(self) -> None:
        """StateManager starts with no saved state."""
        manager = StateManager()
        assert manager.has_saved_state() is False
        assert manager.restore_parent_state() is None

    def test_save_parent_state(self) -> None:
        """save_parent_state stores the state."""
        manager = StateManager()
        menu_ctx = MenuContext(
            menu_id="menu-1",
            parent_context=None,
            workflow_type="standard",
            depth_level=1,
        )
        state = ParentState(
            menu_context=menu_ctx,
            selection_history=["opt1"],
            continuation_markers={},
            timestamp=datetime.now(),
        )
        manager.save_parent_state(state)
        assert manager.has_saved_state() is True

    def test_restore_parent_state_returns_and_clears(self) -> None:
        """restore_parent_state returns the state and clears it."""
        manager = StateManager()
        menu_ctx = MenuContext(
            menu_id="menu-1",
            parent_context=None,
            workflow_type="standard",
            depth_level=1,
        )
        state = ParentState(
            menu_context=menu_ctx,
            selection_history=["opt1"],
            continuation_markers={"key": "value"},
            timestamp=datetime.now(),
        )
        manager.save_parent_state(state)

        restored = manager.restore_parent_state()
        assert restored is state
        assert manager.has_saved_state() is False
        # Second restore returns None
        assert manager.restore_parent_state() is None

    def test_clear_saved_state(self) -> None:
        """clear_saved_state removes saved state."""
        manager = StateManager()
        menu_ctx = MenuContext(
            menu_id="menu-1",
            parent_context=None,
            workflow_type="standard",
            depth_level=1,
        )
        state = ParentState(
            menu_context=menu_ctx,
            selection_history=[],
            continuation_markers={},
            timestamp=datetime.now(),
        )
        manager.save_parent_state(state)
        assert manager.has_saved_state() is True

        manager.clear_saved_state()
        assert manager.has_saved_state() is False

    def test_clear_saved_state_safe_when_empty(self) -> None:
        """clear_saved_state is safe to call when no state is saved."""
        manager = StateManager()
        # Should not raise
        manager.clear_saved_state()
        assert manager.has_saved_state() is False

    def test_save_stacks_states_lifo(self) -> None:
        """Saving multiple states stacks them in LIFO order."""
        manager = StateManager()
        ctx1 = MenuContext(
            menu_id="menu-1",
            parent_context=None,
            workflow_type="standard",
            depth_level=1,
        )
        state1 = ParentState(
            menu_context=ctx1,
            selection_history=["first"],
            continuation_markers={},
            timestamp=datetime.now(),
        )
        ctx2 = MenuContext(
            menu_id="menu-2",
            parent_context=None,
            workflow_type="party_mode",
            depth_level=2,
        )
        state2 = ParentState(
            menu_context=ctx2,
            selection_history=["second"],
            continuation_markers={},
            timestamp=datetime.now(),
        )

        manager.save_parent_state(state1)
        manager.save_parent_state(state2)

        # Should get state2 first (LIFO)
        restored = manager.restore_parent_state()
        assert restored is state2

        # Then state1
        restored = manager.restore_parent_state()
        assert restored is state1

        # No more states
        assert manager.has_saved_state() is False

    def test_state_stack_supports_three_levels(self) -> None:
        """StateManager should support 3 levels of nesting (Issue 2 fix)."""
        manager = StateManager()

        # Create 3 states for 3 levels
        states = []
        for i in range(3):
            ctx = MenuContext(
                menu_id=f"menu-{i}",
                parent_context=None,
                workflow_type="standard",
                depth_level=i + 1,
            )
            state = ParentState(
                menu_context=ctx,
                selection_history=[f"selection-{i}"],
                continuation_markers={"level": i},
                timestamp=datetime.now(),
            )
            states.append(state)
            manager.save_parent_state(state)

        # Should be able to restore all 3 in LIFO order
        for i in range(2, -1, -1):
            restored = manager.restore_parent_state()
            assert restored is not None
            assert restored.menu_context.menu_id == f"menu-{i}"
            assert restored.continuation_markers["level"] == i

        # No more states
        assert manager.has_saved_state() is False


# =============================================================================
# Task 5: UserEscalation and handle_depth_exceeded Tests
# =============================================================================


class TestUserEscalation:
    """Tests for UserEscalation dataclass."""

    def test_user_escalation_creation(self) -> None:
        """UserEscalation can be created with all required fields."""
        escalation = UserEscalation(
            reason="Maximum depth exceeded",
            context_stack=["menu-1", "menu-2", "menu-3"],
            suggestion="Use Exit to return to parent menu",
            severity="warning",
        )
        assert escalation.reason == "Maximum depth exceeded"
        assert escalation.context_stack == ["menu-1", "menu-2", "menu-3"]
        assert escalation.suggestion == "Use Exit to return to parent menu"
        assert escalation.severity == "warning"

    def test_user_escalation_empty_context_stack(self) -> None:
        """UserEscalation can have empty context stack."""
        escalation = UserEscalation(
            reason="Unexpected state",
            context_stack=[],
            suggestion="Restart workflow",
            severity="error",
        )
        assert escalation.context_stack == []

    def test_user_escalation_severity_levels(self) -> None:
        """UserEscalation supports different severity levels."""
        for severity in ["info", "warning", "error"]:
            escalation = UserEscalation(
                reason=f"Test {severity}",
                context_stack=["menu-1"],
                suggestion="Test suggestion",
                severity=severity,
            )
            assert escalation.severity == severity


class TestHandleDepthExceeded:
    """Tests for handle_depth_exceeded function."""

    def test_handle_depth_exceeded_returns_escalation(self) -> None:
        """handle_depth_exceeded returns a UserEscalation."""
        tracker = MenuDepthTracker()
        for i in range(MAX_NESTED_DEPTH + 1):
            tracker.push_menu_context(f"menu-{i}", "standard")

        result = handle_depth_exceeded(tracker)
        assert isinstance(result, UserEscalation)
        assert result.severity == "warning"

    def test_handle_depth_exceeded_includes_reason(self) -> None:
        """Escalation reason mentions max depth and current depth."""
        tracker = MenuDepthTracker()
        for i in range(4):  # Push 4 (exceeds max of 3)
            tracker.push_menu_context(f"menu-{i}", "standard")

        result = handle_depth_exceeded(tracker)
        assert str(MAX_NESTED_DEPTH) in result.reason
        assert "4" in result.reason  # Current depth

    def test_handle_depth_exceeded_includes_suggestion(self) -> None:
        """Escalation includes navigation suggestion."""
        tracker = MenuDepthTracker()
        for i in range(4):
            tracker.push_menu_context(f"menu-{i}", "standard")

        result = handle_depth_exceeded(tracker)
        # Should suggest Exit or Back
        assert "Exit" in result.suggestion or "Back" in result.suggestion

    def test_handle_depth_exceeded_logs_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """handle_depth_exceeded logs a warning."""
        tracker = MenuDepthTracker()
        for i in range(4):
            tracker.push_menu_context(f"menu-{i}", "standard")

        with caplog.at_level(logging.WARNING):
            handle_depth_exceeded(tracker)

        assert len(caplog.records) > 0
        assert "depth" in caplog.records[0].message.lower()

    def test_context_stack_built_from_parent_chain(self) -> None:
        """Context stack is built by traversing parent chain (Issue 6)."""
        tracker = MenuDepthTracker()
        # Push 4 menus to exceed depth
        tracker.push_menu_context("root-menu", "standard")
        tracker.push_menu_context("party-menu", "party_mode")
        tracker.push_menu_context("elicit-menu", "elicitation")
        tracker.push_menu_context("deep-menu", "standard")

        result = handle_depth_exceeded(tracker)

        # Context stack should contain all menu IDs in order (root to leaf)
        assert result.context_stack == ["root-menu", "party-menu", "elicit-menu", "deep-menu"]

    def test_handle_depth_exceeded_empty_tracker(self) -> None:
        """Handle edge case of empty tracker (shouldn't happen but be safe)."""
        tracker = MenuDepthTracker()
        # Don't push anything - depth is 0, not exceeded, but test function behavior
        result = handle_depth_exceeded(tracker)
        assert isinstance(result, UserEscalation)
        assert result.context_stack == []


# =============================================================================
# Issue 7: Specialized Contexts with Tracker Tests
# =============================================================================


class TestPushMenuContextWithContextClass:
    """Tests for push_menu_context with context_class parameter (Issue 7)."""

    def test_push_standard_context_default(self) -> None:
        """Default push creates standard MenuContext."""
        tracker = MenuDepthTracker()
        ctx = tracker.push_menu_context("menu-1", "standard")

        assert isinstance(ctx, MenuContext)
        # Should NOT be PartyModeMenuContext or ElicitationMenuContext
        assert type(ctx) is MenuContext

    def test_push_party_mode_context_with_class(self) -> None:
        """push_menu_context can create PartyModeMenuContext."""
        tracker = MenuDepthTracker()
        ctx = tracker.push_menu_context(
            "party-menu",
            "party_mode",
            context_class=PartyModeMenuContext,
        )

        assert isinstance(ctx, PartyModeMenuContext)
        assert ctx.menu_id == "party-menu"
        assert ctx.workflow_type == "party_mode"
        assert ctx.depth_level == 1
        assert ctx.agent_roster == []  # Default
        assert ctx.current_round == 0  # Default

    def test_push_party_mode_context_with_kwargs(self) -> None:
        """push_menu_context can pass kwargs to PartyModeMenuContext."""
        tracker = MenuDepthTracker()
        ctx = tracker.push_menu_context(
            "party-menu",
            "party_mode",
            context_class=PartyModeMenuContext,
            agent_roster=["analyst", "dev"],
            current_round=2,
        )

        assert isinstance(ctx, PartyModeMenuContext)
        assert ctx.agent_roster == ["analyst", "dev"]
        assert ctx.current_round == 2

    def test_push_elicitation_context_with_class(self) -> None:
        """push_menu_context can create ElicitationMenuContext."""
        tracker = MenuDepthTracker()
        ctx = tracker.push_menu_context(
            "elicit-menu",
            "elicitation",
            context_class=ElicitationMenuContext,
        )

        assert isinstance(ctx, ElicitationMenuContext)
        assert ctx.menu_id == "elicit-menu"
        assert ctx.workflow_type == "elicitation"
        assert ctx.technique_selected is None  # Default
        assert ctx.elicitation_phase == "technique_selection"  # Default

    def test_push_elicitation_context_with_kwargs(self) -> None:
        """push_menu_context can pass kwargs to ElicitationMenuContext."""
        tracker = MenuDepthTracker()
        ctx = tracker.push_menu_context(
            "elicit-menu",
            "elicitation",
            context_class=ElicitationMenuContext,
            technique_selected="5 Whys",
            elicitation_phase="execution",
        )

        assert isinstance(ctx, ElicitationMenuContext)
        assert ctx.technique_selected == "5 Whys"
        assert ctx.elicitation_phase == "execution"

    def test_nested_specialized_contexts(self) -> None:
        """Can nest different specialized context types."""
        tracker = MenuDepthTracker()

        # Push standard first
        ctx1 = tracker.push_menu_context("standard-menu", "standard")
        assert isinstance(ctx1, MenuContext)

        # Push party mode nested
        ctx2 = tracker.push_menu_context(
            "party-menu",
            "party_mode",
            context_class=PartyModeMenuContext,
            agent_roster=["pm"],
        )
        assert isinstance(ctx2, PartyModeMenuContext)
        assert ctx2.parent_context is ctx1

        # Push elicitation nested within party mode
        ctx3 = tracker.push_menu_context(
            "elicit-menu",
            "elicitation",
            context_class=ElicitationMenuContext,
            technique_selected="Brainstorming",
        )
        assert isinstance(ctx3, ElicitationMenuContext)
        assert ctx3.parent_context is ctx2

        # Verify depths
        assert ctx1.depth_level == 1
        assert ctx2.depth_level == 2
        assert ctx3.depth_level == 3


# =============================================================================
# Issue 9: MenuSelector Context Handler Routing Tests
# =============================================================================


class TestRouteToContextHandler:
    """Tests for route_to_context_handler function (Issue 9)."""

    def test_route_to_party_mode_handler(self) -> None:
        """Detects Party Mode menu and routes to party_mode handler."""
        from pcmrp_tools.bmad_automation.nested_menu import route_to_context_handler

        detection = MenuDetectionResult.detected(
            confidence=85,
            menu_type=MenuType.APC,
            options=["Select agent", "View roster", "Exit"],
            breakdown={"test": 85},
            raw_input="[A] Select agent [V] View roster [E] Exit",
        )

        handler_type, context_class = route_to_context_handler(detection)

        assert handler_type == "party_mode"
        assert context_class is PartyModeMenuContext

    def test_route_to_elicitation_handler(self) -> None:
        """Detects Elicitation menu and routes to elicitation handler."""
        from pcmrp_tools.bmad_automation.nested_menu import route_to_context_handler

        detection = MenuDetectionResult.detected(
            confidence=80,
            menu_type=MenuType.NUMBERED,
            options=["Socratic questioning", "5 Whys", "Mind mapping"],
            breakdown={"test": 80},
            raw_input="Select technique: [1] Socratic [2] 5 Whys [3] Mind mapping",
        )

        handler_type, context_class = route_to_context_handler(detection)

        assert handler_type == "elicitation"
        assert context_class is ElicitationMenuContext

    def test_route_to_standard_handler(self) -> None:
        """Standard menus route to standard handler."""
        from pcmrp_tools.bmad_automation.nested_menu import route_to_context_handler

        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.YVN,
            options=["Yes", "No"],
            breakdown={"test": 90},
            raw_input="[Y] Yes [N] No",
        )

        handler_type, context_class = route_to_context_handler(detection)

        assert handler_type == "standard"
        assert context_class is None  # Use default MenuContext

    def test_route_not_detected_menu(self) -> None:
        """Non-detected menus route to standard handler."""
        from pcmrp_tools.bmad_automation.nested_menu import route_to_context_handler

        detection = MenuDetectionResult.not_detected(
            confidence=30,
            breakdown={"test": 30},
            raw_input="Some random text",
        )

        handler_type, context_class = route_to_context_handler(detection)

        assert handler_type == "standard"
        assert context_class is None

    def test_party_mode_takes_precedence_over_elicitation(self) -> None:
        """Party Mode patterns take precedence when both could match."""
        from pcmrp_tools.bmad_automation.nested_menu import route_to_context_handler

        # Menu with both agent selection and "advanced" keyword
        detection = MenuDetectionResult.detected(
            confidence=80,
            menu_type=MenuType.APC,
            options=["Select agent", "Advanced mode", "Exit"],
            breakdown={"test": 80},
            raw_input="[A] Select agent [D] Advanced mode [E] Exit",
        )

        handler_type, context_class = route_to_context_handler(detection)

        # Party mode detection excludes elicitation when agent patterns present
        assert handler_type == "party_mode"
        assert context_class is PartyModeMenuContext


# =============================================================================
# MEDIUM Issues: Validation Tests
# =============================================================================


class TestWorkflowTypeValidation:
    """Tests for workflow_type validation (Issue 3)."""

    def test_valid_workflow_types_accepted(self) -> None:
        """Valid workflow types are accepted."""
        from pcmrp_tools.bmad_automation.nested_menu import VALID_WORKFLOW_TYPES

        assert "party_mode" in VALID_WORKFLOW_TYPES
        assert "elicitation" in VALID_WORKFLOW_TYPES
        assert "standard" in VALID_WORKFLOW_TYPES

    def test_push_with_valid_workflow_type(self) -> None:
        """push_menu_context works with valid workflow types."""
        tracker = MenuDepthTracker()

        for wf_type in ["party_mode", "elicitation", "standard"]:
            ctx = tracker.push_menu_context(f"menu-{wf_type}", wf_type)
            assert ctx.workflow_type == wf_type
            tracker.pop_menu_context()

    def test_push_with_invalid_workflow_type_raises(self) -> None:
        """push_menu_context raises ValueError for invalid workflow type."""
        tracker = MenuDepthTracker()

        with pytest.raises(ValueError, match="Invalid workflow_type"):
            tracker.push_menu_context("invalid-menu", "invalid_type")


class TestElicitationPhaseValidation:
    """Tests for elicitation_phase validation (Issue 8)."""

    def test_valid_elicitation_phases_accepted(self) -> None:
        """Valid elicitation phases are accepted."""
        from pcmrp_tools.bmad_automation.nested_menu import VALID_ELICITATION_PHASES

        assert "technique_selection" in VALID_ELICITATION_PHASES
        assert "execution" in VALID_ELICITATION_PHASES
        assert "summary" in VALID_ELICITATION_PHASES

    def test_elicitation_context_with_valid_phase(self) -> None:
        """ElicitationMenuContext works with valid phases."""
        for phase in ["technique_selection", "execution", "summary"]:
            ctx = ElicitationMenuContext(
                menu_id="elicit-menu",
                parent_context=None,
                workflow_type="elicitation",
                depth_level=1,
                technique_selected=None,
                elicitation_phase=phase,
            )
            assert ctx.elicitation_phase == phase

    def test_push_elicitation_with_invalid_phase_raises(self) -> None:
        """push_menu_context raises ValueError for invalid elicitation_phase."""
        tracker = MenuDepthTracker()

        with pytest.raises(ValueError, match="Invalid elicitation_phase"):
            tracker.push_menu_context(
                "elicit-menu",
                "elicitation",
                context_class=ElicitationMenuContext,
                elicitation_phase="invalid_phase",
            )
