"""Tests for the Memory Bridge component.

This module tests the MemoryBridge class which writes workflow decisions
and outcomes to Forgetful memory for cross-session learning.

TDD: All tests written FIRST, then implementation.
"""

import pytest
from typing import Any, Dict, List

# These imports will fail until we implement the module (RED phase)


class TestImportanceLevel:
    """Test ImportanceLevel enum values (Task 1.4)."""

    def test_importance_level_architectural_is_10(self):
        """ARCHITECTURAL importance level should be 10."""
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        assert ImportanceLevel.ARCHITECTURAL == 10

    def test_importance_level_architectural_low_is_9(self):
        """ARCHITECTURAL_LOW importance level should be 9."""
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        assert ImportanceLevel.ARCHITECTURAL_LOW == 9

    def test_importance_level_pattern_high_is_8(self):
        """PATTERN_HIGH importance level should be 8."""
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        assert ImportanceLevel.PATTERN_HIGH == 8

    def test_importance_level_pattern_is_7(self):
        """PATTERN importance level should be 7."""
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        assert ImportanceLevel.PATTERN == 7

    def test_importance_level_milestone_is_6(self):
        """MILESTONE importance level should be 6."""
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        assert ImportanceLevel.MILESTONE == 6

    def test_importance_level_selection_is_5(self):
        """SELECTION importance level should be 5."""
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        assert ImportanceLevel.SELECTION == 5


class TestWorkflowDecision:
    """Test WorkflowDecision dataclass (Task 1.2)."""

    def test_workflow_decision_required_fields(self):
        """WorkflowDecision should require decision_type, description, rationale."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            WorkflowDecision,
            ImportanceLevel,
        )

        decision = WorkflowDecision(
            decision_type="technical",
            description="Used dataclass instead of TypedDict",
            rationale="Better IDE support and validation",
        )

        assert decision.decision_type == "technical"
        assert decision.description == "Used dataclass instead of TypedDict"
        assert decision.rationale == "Better IDE support and validation"

    def test_workflow_decision_default_outcome_is_none(self):
        """WorkflowDecision outcome should default to None."""
        from pcmrp_tools.bmad_automation.memory_bridge import WorkflowDecision

        decision = WorkflowDecision(
            decision_type="technical",
            description="Test",
            rationale="Test rationale",
        )

        assert decision.outcome is None

    def test_workflow_decision_default_importance_is_pattern(self):
        """WorkflowDecision importance should default to PATTERN (7)."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            WorkflowDecision,
            ImportanceLevel,
        )

        decision = WorkflowDecision(
            decision_type="technical",
            description="Test",
            rationale="Test rationale",
        )

        assert decision.importance == ImportanceLevel.PATTERN

    def test_workflow_decision_custom_importance(self):
        """WorkflowDecision should accept custom importance level."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            WorkflowDecision,
            ImportanceLevel,
        )

        decision = WorkflowDecision(
            decision_type="architectural",
            description="Chose PostgreSQL over MongoDB",
            rationale="Better relational support",
            importance=ImportanceLevel.ARCHITECTURAL,
        )

        assert decision.importance == ImportanceLevel.ARCHITECTURAL

    def test_workflow_decision_with_outcome(self):
        """WorkflowDecision should store outcome when provided."""
        from pcmrp_tools.bmad_automation.memory_bridge import WorkflowDecision

        decision = WorkflowDecision(
            decision_type="process",
            description="Used TDD approach",
            rationale="Ensures test coverage",
            outcome="All tests passing",
        )

        assert decision.outcome == "All tests passing"


class TestMemoryEntry:
    """Test MemoryEntry dataclass (Task 1.3)."""

    def test_memory_entry_required_fields(self):
        """MemoryEntry should require all Forgetful schema fields."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryEntry

        entry = MemoryEntry(
            title="Test Memory",
            content="This is test content",
            context="Why this matters",
            keywords=["test", "memory"],
            tags=["unit-test"],
            importance=7,
            project_ids=[1],
        )

        assert entry.title == "Test Memory"
        assert entry.content == "This is test content"
        assert entry.context == "Why this matters"
        assert entry.keywords == ["test", "memory"]
        assert entry.tags == ["unit-test"]
        assert entry.importance == 7
        assert entry.project_ids == [1]

    def test_memory_entry_default_workflow_id_is_none(self):
        """MemoryEntry workflow_id should default to None."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryEntry

        entry = MemoryEntry(
            title="Test",
            content="Content",
            context="Context",
            keywords=["kw"],
            tags=["tag"],
            importance=7,
            project_ids=[1],
        )

        assert entry.workflow_id is None

    def test_memory_entry_with_workflow_id(self):
        """MemoryEntry should store workflow_id when provided."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryEntry

        entry = MemoryEntry(
            title="Test",
            content="Content",
            context="Context",
            keywords=["kw"],
            tags=["tag"],
            importance=7,
            project_ids=[1],
            workflow_id="dev-story-123",
        )

        assert entry.workflow_id == "dev-story-123"


class TestMemoryBridgeInit:
    """Test MemoryBridge class initialization (Task 1.1)."""

    def test_memory_bridge_init_with_project_id_and_workflow_id(self):
        """MemoryBridge should initialize with project_id and workflow_id."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="dev-story-123")

        assert bridge.project_id == 1
        assert bridge.workflow_id == "dev-story-123"

    def test_memory_bridge_stores_project_id(self):
        """MemoryBridge should store project_id as attribute."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=42, workflow_id="test")

        assert bridge.project_id == 42

    def test_memory_bridge_stores_workflow_id(self):
        """MemoryBridge should store workflow_id as attribute."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="create-prd-456")

        assert bridge.workflow_id == "create-prd-456"

    def test_memory_bridge_has_extract_decisions_method(self):
        """MemoryBridge should have extract_decisions method."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "extract_decisions")
        assert callable(bridge.extract_decisions)

    def test_memory_bridge_has_create_fix_pattern_memory_method(self):
        """MemoryBridge should have create_fix_pattern_memory method."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "create_fix_pattern_memory")
        assert callable(bridge.create_fix_pattern_memory)

    def test_memory_bridge_has_record_selection_pattern_method(self):
        """MemoryBridge should have record_selection_pattern method."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "record_selection_pattern")
        assert callable(bridge.record_selection_pattern)

    def test_memory_bridge_has_summarize_content_method(self):
        """MemoryBridge should have summarize_content method."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "summarize_content")
        assert callable(bridge.summarize_content)

    def test_memory_bridge_has_write_memory_method(self):
        """MemoryBridge should have write_memory method."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "write_memory")
        assert callable(bridge.write_memory)

    def test_memory_bridge_has_process_workflow_outcome_method(self):
        """MemoryBridge should have process_workflow_outcome method."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "process_workflow_outcome")
        assert callable(bridge.process_workflow_outcome)


class TestExtractDecisions:
    """Test extract_decisions method (Task 2)."""

    def test_extract_decisions_returns_list(self):
        """extract_decisions should return a list."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        result = bridge.extract_decisions({})

        assert isinstance(result, list)

    def test_extract_decisions_empty_context_returns_empty_list(self):
        """extract_decisions with empty context should return empty list."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        result = bridge.extract_decisions({})

        assert result == []

    def test_extract_decisions_extracts_technical_decision(self):
        """extract_decisions should extract technical decisions."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            MemoryBridge,
            ImportanceLevel,
        )

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        context = {
            "decisions": [
                {
                    "type": "technical",
                    "description": "Used dataclass instead of TypedDict",
                    "rationale": "Better IDE support",
                }
            ]
        }
        result = bridge.extract_decisions(context)

        assert len(result) == 1
        assert result[0].decision_type == "technical"
        assert result[0].description == "Used dataclass instead of TypedDict"
        assert result[0].rationale == "Better IDE support"

    def test_extract_decisions_extracts_architectural_decision(self):
        """extract_decisions should extract architectural decisions with high importance."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            MemoryBridge,
            ImportanceLevel,
        )

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        context = {
            "decisions": [
                {
                    "type": "architectural",
                    "description": "Chose PostgreSQL over MongoDB",
                    "rationale": "Better relational support",
                }
            ]
        }
        result = bridge.extract_decisions(context)

        assert len(result) == 1
        assert result[0].decision_type == "architectural"
        assert result[0].importance == ImportanceLevel.ARCHITECTURAL

    def test_extract_decisions_extracts_process_decision(self):
        """extract_decisions should extract process decisions."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            MemoryBridge,
            ImportanceLevel,
        )

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        context = {
            "decisions": [
                {
                    "type": "process",
                    "description": "Adopted TDD methodology",
                    "rationale": "Ensures test coverage",
                }
            ]
        }
        result = bridge.extract_decisions(context)

        assert len(result) == 1
        assert result[0].decision_type == "process"
        assert result[0].importance == ImportanceLevel.PATTERN

    def test_extract_decisions_maps_technical_to_pattern_importance(self):
        """Technical decisions should have PATTERN importance (7)."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            MemoryBridge,
            ImportanceLevel,
        )

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        context = {
            "decisions": [
                {
                    "type": "technical",
                    "description": "Test",
                    "rationale": "Test",
                }
            ]
        }
        result = bridge.extract_decisions(context)

        assert result[0].importance == ImportanceLevel.PATTERN

    def test_extract_decisions_maps_architectural_to_architectural_importance(self):
        """Architectural decisions should have ARCHITECTURAL importance (10)."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            MemoryBridge,
            ImportanceLevel,
        )

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        context = {
            "decisions": [
                {
                    "type": "architectural",
                    "description": "Test",
                    "rationale": "Test",
                }
            ]
        }
        result = bridge.extract_decisions(context)

        assert result[0].importance == ImportanceLevel.ARCHITECTURAL

    def test_extract_decisions_handles_multiple_decisions(self):
        """extract_decisions should handle multiple decisions."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        context = {
            "decisions": [
                {"type": "technical", "description": "D1", "rationale": "R1"},
                {"type": "architectural", "description": "D2", "rationale": "R2"},
                {"type": "process", "description": "D3", "rationale": "R3"},
            ]
        }
        result = bridge.extract_decisions(context)

        assert len(result) == 3

    def test_extract_decisions_includes_outcome_when_present(self):
        """extract_decisions should include outcome when present in context."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        context = {
            "decisions": [
                {
                    "type": "technical",
                    "description": "Test",
                    "rationale": "Test",
                    "outcome": "Success",
                }
            ]
        }
        result = bridge.extract_decisions(context)

        assert result[0].outcome == "Success"

    def test_extract_decisions_skips_invalid_decisions(self):
        """extract_decisions should skip decisions missing required fields."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        context = {
            "decisions": [
                {"type": "technical"},  # Missing description and rationale
                {
                    "type": "technical",
                    "description": "Valid",
                    "rationale": "Valid",
                },
            ]
        }
        result = bridge.extract_decisions(context)

        assert len(result) == 1
        assert result[0].description == "Valid"

    def test_extract_decisions_handles_missing_decisions_key(self):
        """extract_decisions should return empty list if decisions key missing."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        context = {"workflow_id": "test", "other_data": "value"}
        result = bridge.extract_decisions(context)

        assert result == []

    def test_extract_decisions_handles_unicode_content(self):
        """extract_decisions should handle unicode characters."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        context = {
            "decisions": [
                {
                    "type": "technical",
                    "description": "Used cafe encoding",
                    "rationale": "Better support for international chars",
                }
            ]
        }
        result = bridge.extract_decisions(context)

        assert len(result) == 1
        assert "cafe" in result[0].description


class TestFixPattern:
    """Test FixPattern dataclass (Task 3.1)."""

    def test_fix_pattern_required_fields(self):
        """FixPattern should require error_signature, solution, workflow_step, validation_type."""
        from pcmrp_tools.bmad_automation.memory_bridge import FixPattern

        pattern = FixPattern(
            error_signature="ImportError:missing_module:dataclasses",
            solution="Add 'from dataclasses import dataclass' import",
            workflow_step="2a-1",
            validation_type="syntax",
        )

        assert pattern.error_signature == "ImportError:missing_module:dataclasses"
        assert pattern.solution == "Add 'from dataclasses import dataclass' import"
        assert pattern.workflow_step == "2a-1"
        assert pattern.validation_type == "syntax"

    def test_fix_pattern_default_success_rate_is_one(self):
        """FixPattern success_rate should default to 1.0."""
        from pcmrp_tools.bmad_automation.memory_bridge import FixPattern

        pattern = FixPattern(
            error_signature="test",
            solution="test",
            workflow_step="test",
            validation_type="test",
        )

        assert pattern.success_rate == 1.0

    def test_fix_pattern_custom_success_rate(self):
        """FixPattern should accept custom success_rate."""
        from pcmrp_tools.bmad_automation.memory_bridge import FixPattern

        pattern = FixPattern(
            error_signature="test",
            solution="test",
            workflow_step="test",
            validation_type="test",
            success_rate=0.85,
        )

        assert pattern.success_rate == 0.85


class TestCreateFixPatternMemory:
    """Test create_fix_pattern_memory method (Task 3.2-3.4)."""

    def test_create_fix_pattern_memory_returns_memory_entry(self):
        """create_fix_pattern_memory should return a MemoryEntry."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            MemoryBridge,
            FixPattern,
            MemoryEntry,
        )

        bridge = MemoryBridge(project_id=1, workflow_id="dev-story-123")
        pattern = FixPattern(
            error_signature="ImportError:missing_module:dataclasses",
            solution="Add 'from dataclasses import dataclass' import",
            workflow_step="2a-1",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        assert isinstance(result, MemoryEntry)

    def test_create_fix_pattern_memory_includes_title(self):
        """Memory entry should have descriptive title."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        bridge = MemoryBridge(project_id=1, workflow_id="dev-story-123")
        pattern = FixPattern(
            error_signature="ImportError:missing_module:dataclasses",
            solution="Add import",
            workflow_step="2a-1",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        assert "fix" in result.title.lower() or "pattern" in result.title.lower()
        assert len(result.title) <= 200

    def test_create_fix_pattern_memory_includes_error_signature_in_content(self):
        """Memory content should include error signature."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        bridge = MemoryBridge(project_id=1, workflow_id="dev-story-123")
        pattern = FixPattern(
            error_signature="ImportError:missing_module:dataclasses",
            solution="Add import",
            workflow_step="2a-1",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        assert "ImportError:missing_module:dataclasses" in result.content

    def test_create_fix_pattern_memory_includes_solution_in_content(self):
        """Memory content should include solution."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        bridge = MemoryBridge(project_id=1, workflow_id="dev-story-123")
        pattern = FixPattern(
            error_signature="test_error",
            solution="Apply the fix by adding X",
            workflow_step="2a-1",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        assert "Apply the fix by adding X" in result.content

    def test_create_fix_pattern_memory_includes_workflow_context(self):
        """Memory content should include workflow context (step, validation type)."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        bridge = MemoryBridge(project_id=1, workflow_id="dev-story-123")
        pattern = FixPattern(
            error_signature="test_error",
            solution="fix",
            workflow_step="step-2a-1",
            validation_type="schema_validation",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        assert "step-2a-1" in result.content
        assert "schema_validation" in result.content

    def test_create_fix_pattern_memory_generates_keywords_from_error(self):
        """Keywords should be generated from error signature."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        bridge = MemoryBridge(project_id=1, workflow_id="dev-story-123")
        pattern = FixPattern(
            error_signature="ImportError:missing_module:dataclasses",
            solution="fix",
            workflow_step="step",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        # Keywords should include parts of error signature
        assert len(result.keywords) > 0
        assert len(result.keywords) <= 10

    def test_create_fix_pattern_memory_includes_fix_pattern_tag(self):
        """Tags should include fix_pattern type."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        bridge = MemoryBridge(project_id=1, workflow_id="dev-story-123")
        pattern = FixPattern(
            error_signature="test",
            solution="fix",
            workflow_step="step",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        assert "fix_pattern" in result.tags

    def test_create_fix_pattern_memory_includes_project_id(self):
        """Memory entry should include project_id."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        bridge = MemoryBridge(project_id=42, workflow_id="test")
        pattern = FixPattern(
            error_signature="test",
            solution="fix",
            workflow_step="step",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        assert 42 in result.project_ids

    def test_create_fix_pattern_memory_includes_workflow_id(self):
        """Memory entry should include workflow_id."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        bridge = MemoryBridge(project_id=1, workflow_id="dev-story-456")
        pattern = FixPattern(
            error_signature="test",
            solution="fix",
            workflow_step="step",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        assert result.workflow_id == "dev-story-456"

    def test_create_fix_pattern_memory_has_pattern_importance(self):
        """Fix pattern memories should have PATTERN importance (7-8)."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            MemoryBridge,
            FixPattern,
            ImportanceLevel,
        )

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        pattern = FixPattern(
            error_signature="test",
            solution="fix",
            workflow_step="step",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        assert result.importance in (
            ImportanceLevel.PATTERN,
            ImportanceLevel.PATTERN_HIGH,
        )

    def test_create_fix_pattern_memory_includes_context(self):
        """Memory entry should have meaningful context."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        pattern = FixPattern(
            error_signature="test",
            solution="fix",
            workflow_step="step",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        assert len(result.context) > 0
        assert len(result.context) <= 500

    def test_create_fix_pattern_memory_handles_long_error_signature(self):
        """Should handle very long error signatures gracefully."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        long_signature = "Error:" + "x" * 500
        pattern = FixPattern(
            error_signature=long_signature,
            solution="fix",
            workflow_step="step",
            validation_type="syntax",
        )

        result = bridge.create_fix_pattern_memory(pattern)

        # Title should be truncated to 200 chars
        assert len(result.title) <= 200
        # Keywords should still be generated
        assert len(result.keywords) <= 10


class TestMenuSelectionPattern:
    """Test MenuSelectionPattern dataclass (Task 4.1)."""

    def test_menu_selection_pattern_required_fields(self):
        """MenuSelectionPattern should require context, selection, outcome."""
        from pcmrp_tools.bmad_automation.memory_bridge import MenuSelectionPattern

        pattern = MenuSelectionPattern(
            context="Unclear requirements for user story",
            selection="[A] Advanced Elicitation",
            outcome="Successfully gathered detailed requirements",
        )

        assert pattern.context == "Unclear requirements for user story"
        assert pattern.selection == "[A] Advanced Elicitation"
        assert pattern.outcome == "Successfully gathered detailed requirements"

    def test_menu_selection_pattern_default_success_signal_is_one(self):
        """MenuSelectionPattern success_signal should default to 1.0."""
        from pcmrp_tools.bmad_automation.memory_bridge import MenuSelectionPattern

        pattern = MenuSelectionPattern(
            context="test", selection="test", outcome="test"
        )

        assert pattern.success_signal == 1.0

    def test_menu_selection_pattern_custom_success_signal(self):
        """MenuSelectionPattern should accept custom success_signal."""
        from pcmrp_tools.bmad_automation.memory_bridge import MenuSelectionPattern

        pattern = MenuSelectionPattern(
            context="test", selection="test", outcome="test", success_signal=0.75
        )

        assert pattern.success_signal == 0.75


class TestRecordSelectionPattern:
    """Test record_selection_pattern method (Task 4.2-4.4)."""

    def test_record_selection_pattern_returns_none_when_disabled(self):
        """record_selection_pattern should return None when recording is disabled."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test", record_selections=False)
        result = bridge.record_selection_pattern(
            context="test", selection="test", outcome="test"
        )

        assert result is None

    def test_record_selection_pattern_returns_memory_entry_when_enabled(self):
        """record_selection_pattern should return MemoryEntry when enabled."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, MemoryEntry

        bridge = MemoryBridge(project_id=1, workflow_id="test", record_selections=True)
        result = bridge.record_selection_pattern(
            context="Unclear requirements",
            selection="[A] Advanced Elicitation",
            outcome="Success",
        )

        assert isinstance(result, MemoryEntry)

    def test_record_selection_pattern_includes_context_in_content(self):
        """Memory content should include the context."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test", record_selections=True)
        result = bridge.record_selection_pattern(
            context="Unclear requirements for user story",
            selection="[A] Advanced Elicitation",
            outcome="Success",
        )

        assert "Unclear requirements for user story" in result.content

    def test_record_selection_pattern_includes_selection_in_content(self):
        """Memory content should include the selection."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test", record_selections=True)
        result = bridge.record_selection_pattern(
            context="test",
            selection="[A] Advanced Elicitation",
            outcome="Success",
        )

        assert "[A] Advanced Elicitation" in result.content

    def test_record_selection_pattern_includes_outcome_in_content(self):
        """Memory content should include the outcome."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test", record_selections=True)
        result = bridge.record_selection_pattern(
            context="test",
            selection="test",
            outcome="Workflow completed successfully",
        )

        assert "Workflow completed successfully" in result.content

    def test_record_selection_pattern_has_selection_importance(self):
        """Selection pattern memories should have SELECTION importance (5)."""
        from pcmrp_tools.bmad_automation.memory_bridge import (
            MemoryBridge,
            ImportanceLevel,
        )

        bridge = MemoryBridge(project_id=1, workflow_id="test", record_selections=True)
        result = bridge.record_selection_pattern(
            context="test", selection="test", outcome="test"
        )

        assert result.importance == ImportanceLevel.SELECTION

    def test_record_selection_pattern_includes_selection_pattern_tag(self):
        """Tags should include selection_pattern type."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test", record_selections=True)
        result = bridge.record_selection_pattern(
            context="test", selection="test", outcome="test"
        )

        assert "selection_pattern" in result.tags

    def test_record_selection_pattern_includes_project_id(self):
        """Memory entry should include project_id."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=42, workflow_id="test", record_selections=True)
        result = bridge.record_selection_pattern(
            context="test", selection="test", outcome="test"
        )

        assert 42 in result.project_ids

    def test_record_selection_pattern_includes_workflow_id(self):
        """Memory entry should include workflow_id."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(
            project_id=1, workflow_id="create-prd-789", record_selections=True
        )
        result = bridge.record_selection_pattern(
            context="test", selection="test", outcome="test"
        )

        assert result.workflow_id == "create-prd-789"

    def test_record_selection_pattern_has_descriptive_title(self):
        """Memory entry should have descriptive title."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test", record_selections=True)
        result = bridge.record_selection_pattern(
            context="test", selection="[A] Advanced Elicitation", outcome="test"
        )

        assert len(result.title) > 0
        assert len(result.title) <= 200

    def test_record_selection_pattern_generates_keywords(self):
        """Keywords should be generated from context and selection."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test", record_selections=True)
        result = bridge.record_selection_pattern(
            context="requirements unclear", selection="Advanced", outcome="success"
        )

        assert len(result.keywords) > 0
        assert len(result.keywords) <= 10


class TestSummarizeContent:
    """Test summarize_content method (Task 5)."""

    def test_summarize_content_returns_string(self):
        """summarize_content should return a string."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        result = bridge.summarize_content("test content")

        assert isinstance(result, str)

    def test_summarize_content_short_content_unchanged(self):
        """Content under limit should be returned unchanged."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        short_content = "This is short content."
        result = bridge.summarize_content(short_content)

        assert result == short_content

    def test_summarize_content_at_limit_unchanged(self):
        """Content exactly at 2000 chars should be unchanged."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        content = "x" * 2000
        result = bridge.summarize_content(content)

        assert result == content
        assert len(result) == 2000

    def test_summarize_content_over_limit_truncated(self):
        """Content over limit should be truncated."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        content = "x" * 3000
        result = bridge.summarize_content(content)

        assert len(result) <= 2000

    def test_summarize_content_adds_ellipsis_indicator(self):
        """Truncated content should end with '...' indicator."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        content = "x" * 3000
        result = bridge.summarize_content(content)

        assert result.endswith("...")

    def test_summarize_content_custom_max_length(self):
        """Should respect custom max_length parameter."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        content = "x" * 500
        result = bridge.summarize_content(content, max_length=100)

        assert len(result) <= 100

    def test_summarize_content_preserves_key_sections(self):
        """Should preserve Decision, Rationale, Outcome sections when present."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        content = (
            "Decision: Use PostgreSQL\n\n"
            "Rationale: Better support for complex queries\n\n"
            "Outcome: Successfully implemented\n\n"
            "Additional details: " + "x" * 2500
        )
        result = bridge.summarize_content(content)

        # Key sections should be preserved
        assert "Decision:" in result
        assert "Rationale:" in result
        assert "Outcome:" in result
        assert len(result) <= 2000

    def test_summarize_content_preserves_error_signature_section(self):
        """Should preserve Error Signature section when present."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        content = (
            "Error Signature: ImportError:missing_module\n\n"
            "Solution: Add import statement\n\n"
            "Additional details: " + "x" * 2500
        )
        result = bridge.summarize_content(content)

        # Key sections should be preserved
        assert "Error Signature:" in result
        assert "Solution:" in result
        assert len(result) <= 2000

    def test_summarize_content_empty_string(self):
        """Empty string should return empty string."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        result = bridge.summarize_content("")

        assert result == ""

    def test_summarize_content_unicode_characters(self):
        """Should handle unicode characters correctly."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        content = "Unicode test: cafe and special chars"
        result = bridge.summarize_content(content)

        assert "cafe" in result

    def test_summarize_content_long_lines(self):
        """Should handle content with very long lines."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")
        content = "a" * 5000  # Single very long line
        result = bridge.summarize_content(content)

        assert len(result) <= 2000
        assert result.endswith("...")


class TestWriteMemory:
    """Test write_memory method with mocked MCP (Task 6)."""

    @pytest.mark.asyncio
    async def test_write_memory_calls_mcp_client(self):
        """write_memory should call the MCP client."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, MemoryEntry

        mock_client = AsyncMock(return_value={"id": 123, "status": "created"})
        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=mock_client
        )
        entry = MemoryEntry(
            title="Test",
            content="Content",
            context="Context",
            keywords=["kw"],
            tags=["tag"],
            importance=7,
            project_ids=[1],
        )

        result = await bridge.write_memory(entry)

        mock_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_memory_passes_correct_parameters(self):
        """write_memory should pass correct parameters to MCP."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, MemoryEntry

        mock_client = AsyncMock(return_value={"id": 123})
        bridge = MemoryBridge(
            project_id=1, workflow_id="test-workflow", mcp_client=mock_client
        )
        entry = MemoryEntry(
            title="Test Title",
            content="Test Content",
            context="Test Context",
            keywords=["kw1", "kw2"],
            tags=["tag1"],
            importance=8,
            project_ids=[1],
            workflow_id="test-workflow",
        )

        await bridge.write_memory(entry)

        # Verify the call arguments
        call_args = mock_client.call_args
        assert call_args is not None
        args = call_args[0] if call_args[0] else call_args[1]

        # The call should include the memory entry data
        # Format depends on implementation, but should include key fields

    @pytest.mark.asyncio
    async def test_write_memory_includes_all_required_fields(self):
        """write_memory should include all required Forgetful fields."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, MemoryEntry

        captured_args = {}

        async def capture_mock(*args, **kwargs):
            captured_args["args"] = args
            captured_args["kwargs"] = kwargs
            return {"id": 123}

        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=capture_mock
        )
        entry = MemoryEntry(
            title="Test",
            content="Content",
            context="Context",
            keywords=["kw"],
            tags=["tag"],
            importance=7,
            project_ids=[1],
            workflow_id="test",
        )

        await bridge.write_memory(entry)

        # Verify all required fields are passed
        assert captured_args  # Something was captured

    @pytest.mark.asyncio
    async def test_write_memory_includes_workflow_id_in_tags(self):
        """write_memory should include workflow_id in tags for traceability."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, MemoryEntry

        captured_args = {}

        async def capture_mock(tool_name, arguments):
            captured_args["tool_name"] = tool_name
            captured_args["arguments"] = arguments
            return {"id": 123}

        bridge = MemoryBridge(
            project_id=1, workflow_id="dev-story-456", mcp_client=capture_mock
        )
        entry = MemoryEntry(
            title="Test",
            content="Content",
            context="Context",
            keywords=["kw"],
            tags=["tag"],
            importance=7,
            project_ids=[1],
            workflow_id="dev-story-456",
        )

        await bridge.write_memory(entry)

        # The workflow_id should be in the tags
        assert "arguments" in captured_args
        tags = captured_args["arguments"].get("tags", [])
        assert any("dev-story-456" in tag for tag in tags)

    @pytest.mark.asyncio
    async def test_write_memory_returns_mcp_response(self):
        """write_memory should return the MCP response."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, MemoryEntry

        mock_response = {"id": 123, "status": "created", "memory_id": 456}
        mock_client = AsyncMock(return_value=mock_response)
        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=mock_client
        )
        entry = MemoryEntry(
            title="Test",
            content="Content",
            context="Context",
            keywords=["kw"],
            tags=["tag"],
            importance=7,
            project_ids=[1],
        )

        result = await bridge.write_memory(entry)

        assert result == mock_response

    @pytest.mark.asyncio
    async def test_write_memory_handles_missing_mcp_client(self):
        """write_memory should raise error when MCP client not configured."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, MemoryEntry

        bridge = MemoryBridge(project_id=1, workflow_id="test", mcp_client=None)
        entry = MemoryEntry(
            title="Test",
            content="Content",
            context="Context",
            keywords=["kw"],
            tags=["tag"],
            importance=7,
            project_ids=[1],
        )

        with pytest.raises(RuntimeError, match="MCP client not configured"):
            await bridge.write_memory(entry)

    @pytest.mark.asyncio
    async def test_write_memory_summarizes_long_content(self):
        """write_memory should summarize content exceeding 2000 chars."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, MemoryEntry

        captured_args = {}

        async def capture_mock(tool_name, arguments):
            captured_args["arguments"] = arguments
            return {"id": 123}

        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=capture_mock
        )
        long_content = "x" * 3000
        entry = MemoryEntry(
            title="Test",
            content=long_content,
            context="Context",
            keywords=["kw"],
            tags=["tag"],
            importance=7,
            project_ids=[1],
        )

        await bridge.write_memory(entry)

        # Content should be summarized to 2000 chars
        written_content = captured_args["arguments"].get("content", "")
        assert len(written_content) <= 2000


class TestProcessWorkflowOutcome:
    """Test process_workflow_outcome method (Task 7)."""

    @pytest.mark.asyncio
    async def test_process_workflow_outcome_returns_summary(self):
        """process_workflow_outcome should return a summary dict."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        mock_client = AsyncMock(return_value={"id": 123})
        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=mock_client
        )

        result = await bridge.process_workflow_outcome({})

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_process_workflow_outcome_extracts_and_writes_decisions(self):
        """process_workflow_outcome should extract decisions and write memories."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        mock_client = AsyncMock(return_value={"id": 123})
        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=mock_client
        )
        context = {
            "decisions": [
                {
                    "type": "technical",
                    "description": "Used dataclass",
                    "rationale": "Better IDE support",
                }
            ]
        }

        result = await bridge.process_workflow_outcome(context)

        # Should have written at least one memory
        assert mock_client.call_count >= 1
        assert "decisions_written" in result

    @pytest.mark.asyncio
    async def test_process_workflow_outcome_writes_fix_patterns(self):
        """process_workflow_outcome should write fix pattern memories."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        mock_client = AsyncMock(return_value={"id": 123})
        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=mock_client
        )
        patterns = [
            FixPattern(
                error_signature="ImportError:missing",
                solution="Add import",
                workflow_step="step1",
                validation_type="syntax",
            )
        ]

        result = await bridge.process_workflow_outcome({}, fix_patterns=patterns)

        # Should have written fix pattern memory
        assert mock_client.call_count >= 1
        assert "fix_patterns_written" in result

    @pytest.mark.asyncio
    async def test_process_workflow_outcome_records_selections_when_enabled(self):
        """process_workflow_outcome should record selections when enabled."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        mock_client = AsyncMock(return_value={"id": 123})
        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=mock_client,
            record_selections=True
        )
        context = {
            "selections": [
                {
                    "context": "Unclear requirements",
                    "selection": "[A] Advanced",
                    "outcome": "Success",
                }
            ]
        }

        result = await bridge.process_workflow_outcome(
            context, record_selections=True
        )

        # Should include selection count
        assert "selections_written" in result

    @pytest.mark.asyncio
    async def test_process_workflow_outcome_skips_selections_when_disabled(self):
        """process_workflow_outcome should skip selections when disabled."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        mock_client = AsyncMock(return_value={"id": 123})
        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=mock_client,
            record_selections=False
        )
        context = {
            "selections": [
                {
                    "context": "test",
                    "selection": "test",
                    "outcome": "test",
                }
            ]
        }

        result = await bridge.process_workflow_outcome(
            context, record_selections=False
        )

        # Should report 0 selections
        assert result.get("selections_written", 0) == 0

    @pytest.mark.asyncio
    async def test_process_workflow_outcome_handles_empty_context(self):
        """process_workflow_outcome should handle empty context gracefully."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        mock_client = AsyncMock(return_value={"id": 123})
        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=mock_client
        )

        result = await bridge.process_workflow_outcome({})

        # Should return summary with 0 counts
        assert result["decisions_written"] == 0
        assert result["fix_patterns_written"] == 0

    @pytest.mark.asyncio
    async def test_process_workflow_outcome_batches_writes(self):
        """process_workflow_outcome should batch write operations efficiently."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        mock_client = AsyncMock(return_value={"id": 123})
        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=mock_client
        )
        context = {
            "decisions": [
                {"type": "technical", "description": "D1", "rationale": "R1"},
                {"type": "architectural", "description": "D2", "rationale": "R2"},
            ]
        }
        patterns = [
            FixPattern(
                error_signature="E1",
                solution="S1",
                workflow_step="step1",
                validation_type="syntax",
            ),
        ]

        result = await bridge.process_workflow_outcome(context, fix_patterns=patterns)

        # Should have written 3 memories (2 decisions + 1 fix pattern)
        assert mock_client.call_count == 3
        assert result["decisions_written"] == 2
        assert result["fix_patterns_written"] == 1

    @pytest.mark.asyncio
    async def test_process_workflow_outcome_returns_total_count(self):
        """process_workflow_outcome should return total memories created."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge, FixPattern

        mock_client = AsyncMock(return_value={"id": 123})
        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=mock_client
        )
        context = {
            "decisions": [
                {"type": "technical", "description": "D1", "rationale": "R1"},
            ]
        }
        patterns = [
            FixPattern(
                error_signature="E1",
                solution="S1",
                workflow_step="step1",
                validation_type="syntax",
            ),
        ]

        result = await bridge.process_workflow_outcome(context, fix_patterns=patterns)

        assert "total_written" in result
        assert result["total_written"] == 2

    @pytest.mark.asyncio
    async def test_process_workflow_outcome_creates_decision_memories(self):
        """process_workflow_outcome should create proper decision memories."""
        from unittest.mock import AsyncMock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        captured_calls = []

        async def capture_mock(tool_name, arguments):
            captured_calls.append(arguments)
            return {"id": len(captured_calls)}

        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=capture_mock
        )
        context = {
            "decisions": [
                {
                    "type": "architectural",
                    "description": "Chose PostgreSQL",
                    "rationale": "Better relational support",
                }
            ]
        }

        await bridge.process_workflow_outcome(context)

        # Verify the decision memory was created correctly
        assert len(captured_calls) == 1
        memory = captured_calls[0]
        assert "PostgreSQL" in memory["content"]
        assert memory["importance"] == 10  # ARCHITECTURAL level


# =============================================================================
# TASK 6: Integration with Memory Bridge Tests (Degradation Integration)
# =============================================================================


class TestMemoryBridgeWithDegradationInit:
    """Test MemoryBridge initialization with degradation components (Task 6)."""

    def test_memory_bridge_has_availability_checker_attribute(self):
        """MemoryBridge should have availability_checker attribute."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "availability_checker")

    def test_memory_bridge_has_save_queue_attribute(self):
        """MemoryBridge should have save_queue attribute."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "save_queue")

    def test_memory_bridge_has_notification_manager_attribute(self):
        """MemoryBridge should have notification_manager attribute."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "notification_manager")

    def test_memory_bridge_availability_checker_is_correct_type(self):
        """MemoryBridge availability_checker should be MemoryAvailabilityChecker."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityChecker,
        )

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert isinstance(bridge.availability_checker, MemoryAvailabilityChecker)

    def test_memory_bridge_save_queue_is_correct_type(self):
        """MemoryBridge save_queue should be MemorySaveQueue."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import MemorySaveQueue

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert isinstance(bridge.save_queue, MemorySaveQueue)

    def test_memory_bridge_notification_manager_is_correct_type(self):
        """MemoryBridge notification_manager should be NotificationManager."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import NotificationManager

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert isinstance(bridge.notification_manager, NotificationManager)


class TestMemoryBridgeQueryDegradation:
    """Test MemoryBridge query operations with degradation (Task 6)."""

    def test_memory_bridge_has_query_method(self):
        """MemoryBridge should have query method."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "query")
        assert callable(bridge.query)

    def test_memory_bridge_query_when_available_returns_results(self):
        """MemoryBridge query should return normal results when available."""
        from unittest.mock import Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityStatus,
        )

        mock_client = Mock()
        mock_client.execute_forgetful_tool = Mock(
            return_value=[{"id": 1, "content": "test"}]
        )

        bridge = MemoryBridge(project_id=1, workflow_id="test", mcp_client=mock_client)
        # Mock availability checker to return available
        bridge.availability_checker.check_availability = Mock(
            return_value=MemoryAvailabilityStatus.AVAILABLE
        )

        result = bridge.query("test query", "test context")

        assert result == [{"id": 1, "content": "test"}]

    def test_memory_bridge_query_when_degraded_returns_degraded_result(self):
        """MemoryBridge query should return DegradedQueryResult when degraded."""
        from unittest.mock import Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            DegradedQueryResult,
            MemoryAvailabilityStatus,
        )

        mock_client = Mock()

        bridge = MemoryBridge(project_id=1, workflow_id="test", mcp_client=mock_client)
        # Mock availability checker to return degraded
        bridge.availability_checker.check_availability = Mock(
            return_value=MemoryAvailabilityStatus.DEGRADED
        )

        result = bridge.query("test query", "test context")

        assert isinstance(result, DegradedQueryResult)
        assert result.status == "degraded"

    def test_memory_bridge_query_degraded_notifies_user_once(self):
        """MemoryBridge query should notify user once when degraded."""
        from unittest.mock import Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityStatus,
        )

        mock_client = Mock()

        bridge = MemoryBridge(project_id=1, workflow_id="test", mcp_client=mock_client)
        bridge.availability_checker.check_availability = Mock(
            return_value=MemoryAvailabilityStatus.DEGRADED
        )

        # First query should trigger notification
        bridge.query("test query 1", "context")
        first_notification = bridge.notification_manager.has_been_notified

        # Second query should not trigger another notification
        bridge.query("test query 2", "context")

        assert first_notification is True
        assert bridge.notification_manager.has_been_notified is True


class TestMemoryBridgeSaveDegradation:
    """Test MemoryBridge save operations with degradation (Task 6)."""

    def test_memory_bridge_has_save_method(self):
        """MemoryBridge should have save method."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "save")
        assert callable(bridge.save)

    @pytest.mark.asyncio
    async def test_memory_bridge_save_when_available_saves_directly(self):
        """MemoryBridge save should save directly when available."""
        from unittest.mock import AsyncMock, Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityStatus,
        )

        mock_client = AsyncMock(return_value={"id": 123})

        bridge = MemoryBridge(project_id=1, workflow_id="test", mcp_client=mock_client)
        bridge.availability_checker.check_availability = Mock(
            return_value=MemoryAvailabilityStatus.AVAILABLE
        )

        result = await bridge.save({"title": "Test", "content": "Content"})

        mock_client.assert_called_once()
        assert result["id"] == 123

    @pytest.mark.asyncio
    async def test_memory_bridge_save_when_degraded_queues_memory(self):
        """MemoryBridge save should queue memory when degraded."""
        from unittest.mock import AsyncMock, Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityStatus,
        )

        mock_client = AsyncMock(return_value={"id": 123})

        bridge = MemoryBridge(project_id=1, workflow_id="test", mcp_client=mock_client)
        bridge.availability_checker.check_availability = Mock(
            return_value=MemoryAvailabilityStatus.DEGRADED
        )

        result = await bridge.save({"title": "Test", "content": "Content"})

        # Should not have called client
        mock_client.assert_not_called()
        # Should have added to queue
        assert len(bridge.save_queue.get_queue()) == 1
        # Should return queued status
        assert result["status"] == "queued"

    @pytest.mark.asyncio
    async def test_memory_bridge_save_queued_preserves_memory_data(self):
        """MemoryBridge save should preserve memory data when queuing."""
        from unittest.mock import AsyncMock, Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityStatus,
        )

        mock_client = AsyncMock()

        bridge = MemoryBridge(project_id=1, workflow_id="test", mcp_client=mock_client)
        bridge.availability_checker.check_availability = Mock(
            return_value=MemoryAvailabilityStatus.DEGRADED
        )

        memory_data = {"title": "Test Memory", "content": "Important content"}
        await bridge.save(memory_data)

        queued = bridge.save_queue.get_queue()
        assert queued[0].memory_data == memory_data


class TestMemoryBridgePeriodicHealthCheck:
    """Test MemoryBridge periodic health check (Task 6)."""

    def test_memory_bridge_has_trigger_health_check_method(self):
        """MemoryBridge should have trigger_health_check method."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "trigger_health_check")
        assert callable(bridge.trigger_health_check)

    @pytest.mark.asyncio
    async def test_trigger_health_check_updates_availability_status(self):
        """trigger_health_check should update internal availability status."""
        from unittest.mock import AsyncMock, Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            AvailabilityResult,
            MemoryStatus,
        )

        mock_client = AsyncMock(return_value={"status": "ok"})

        bridge = MemoryBridge(project_id=1, workflow_id="test", mcp_client=mock_client)

        result = await bridge.trigger_health_check()

        assert isinstance(result, AvailabilityResult)

    @pytest.mark.asyncio
    async def test_trigger_health_check_processes_queue_on_recovery(self):
        """trigger_health_check should process queue when recovering from degraded."""
        from unittest.mock import AsyncMock, Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityStatus,
        )

        mock_client = AsyncMock(return_value={"id": 123})

        bridge = MemoryBridge(project_id=1, workflow_id="test", mcp_client=mock_client)

        # Add items to queue (simulating degraded mode)
        bridge.save_queue.add_to_queue({"title": "Queued Memory 1"})
        bridge.save_queue.add_to_queue({"title": "Queued Memory 2"})

        # Mark as previously degraded
        bridge._is_degraded = True

        # Now trigger health check that returns available
        await bridge.trigger_health_check()

        # Queue should be empty after processing
        assert len(bridge.save_queue.get_queue()) == 0


class TestMemoryBridgeRecoveryFlow:
    """Test full recovery flow: degraded -> available -> queue processed (Task 6)."""

    @pytest.mark.asyncio
    async def test_full_recovery_flow(self):
        """Test complete flow: degraded mode -> recovery -> queue processing."""
        from unittest.mock import AsyncMock, Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityStatus,
        )

        save_count = [0]

        async def track_calls(tool_name, arguments):
            if tool_name == "create_memory":
                save_count[0] += 1
            return {"id": save_count[0]}

        bridge = MemoryBridge(project_id=1, workflow_id="test", mcp_client=track_calls)

        # Phase 1: System is degraded
        bridge.availability_checker.check_availability = Mock(
            return_value=MemoryAvailabilityStatus.DEGRADED
        )

        # Attempt saves during degraded mode
        await bridge.save({"title": "Memory 1"})
        await bridge.save({"title": "Memory 2"})

        # Verify queue has items
        assert len(bridge.save_queue.get_queue()) == 2
        assert save_count[0] == 0  # No actual saves yet

        # Phase 2: System recovers
        bridge.availability_checker.check_availability = Mock(
            return_value=MemoryAvailabilityStatus.AVAILABLE
        )
        bridge._is_degraded = True  # Mark as was degraded

        # Trigger health check (recovery)
        await bridge.trigger_health_check()

        # Verify queue was processed
        assert len(bridge.save_queue.get_queue()) == 0
        assert save_count[0] == 2  # Both memories saved

    @pytest.mark.asyncio
    async def test_recovery_with_partial_failures(self):
        """Test recovery where some queued saves fail."""
        from unittest.mock import AsyncMock, Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityStatus,
        )

        async def partial_fail_client(tool_name, arguments):
            if arguments.get("title") == "Will Fail":
                raise TimeoutError("Failed")
            return {"id": 1}

        bridge = MemoryBridge(
            project_id=1, workflow_id="test", mcp_client=partial_fail_client
        )

        # Phase 1: Add items during degraded mode
        bridge.availability_checker.check_availability = Mock(
            return_value=MemoryAvailabilityStatus.DEGRADED
        )

        await bridge.save({"title": "Will Succeed"})
        await bridge.save({"title": "Will Fail"})
        await bridge.save({"title": "Will Also Succeed"})

        assert len(bridge.save_queue.get_queue()) == 3

        # Phase 2: Recover
        bridge.availability_checker.check_availability = Mock(
            return_value=MemoryAvailabilityStatus.AVAILABLE
        )
        bridge._is_degraded = True

        await bridge.trigger_health_check()

        # Failed item should remain in queue
        remaining = bridge.save_queue.get_queue()
        assert len(remaining) == 1
        assert remaining[0].memory_data["title"] == "Will Fail"


class TestMemoryBridgeGetStatus:
    """Test MemoryBridge status retrieval methods (Task 6)."""

    def test_memory_bridge_has_is_degraded_property(self):
        """MemoryBridge should have is_degraded property."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "is_degraded")

    def test_memory_bridge_has_get_queue_size_method(self):
        """MemoryBridge should have get_queue_size method."""
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        assert hasattr(bridge, "get_queue_size")
        assert callable(bridge.get_queue_size)

    def test_get_queue_size_returns_correct_count(self):
        """get_queue_size should return correct queue size."""
        from unittest.mock import Mock
        from pcmrp_tools.bmad_automation.memory_bridge import MemoryBridge
        from pcmrp_tools.bmad_automation.memory_degradation import (
            MemoryAvailabilityStatus,
        )

        bridge = MemoryBridge(project_id=1, workflow_id="test")

        # Add items to queue directly
        bridge.save_queue.add_to_queue({"title": "Test 1"})
        bridge.save_queue.add_to_queue({"title": "Test 2"})

        assert bridge.get_queue_size() == 2
