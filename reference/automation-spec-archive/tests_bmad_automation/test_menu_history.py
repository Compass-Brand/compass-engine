"""Tests for Menu History Tracking - Story 2b-5.

Tests for:
- SelectionSource enum (Task 1)
- MenuHistoryEntry dataclass (Task 1)
- MenuHistoryManager class (Task 2)
- Serialization round-trip
- FIFO pruning behavior
"""

from datetime import datetime, timezone

import pytest


# =============================================================================
# Task 1: SelectionSource enum tests
# =============================================================================


class TestSelectionSourceEnum:
    """Tests for SelectionSource enum (Task 1)."""

    def test_selection_source_auto_value(self):
        """SelectionSource.AUTO has value 'auto'."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource

        assert SelectionSource.AUTO.value == "auto"

    def test_selection_source_manual_value(self):
        """SelectionSource.MANUAL has value 'manual'."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource

        assert SelectionSource.MANUAL.value == "manual"

    def test_selection_source_escalated_value(self):
        """SelectionSource.ESCALATED has value 'escalated'."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource

        assert SelectionSource.ESCALATED.value == "escalated"

    def test_selection_source_has_three_members(self):
        """SelectionSource enum has exactly three members."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource

        assert len(SelectionSource) == 3


# =============================================================================
# Task 1: MenuHistoryEntry dataclass tests
# =============================================================================


class TestMenuHistoryEntry:
    """Tests for MenuHistoryEntry dataclass (Task 1)."""

    def test_menu_history_entry_required_fields(self):
        """MenuHistoryEntry can be created with required fields."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        now = datetime.now(timezone.utc)
        entry = MenuHistoryEntry(
            timestamp=now,
            menu_id="test-menu-1",
            selection="Option A",
            confidence=0.85,
            source=SelectionSource.AUTO,
        )

        assert entry.timestamp == now
        assert entry.menu_id == "test-menu-1"
        assert entry.selection == "Option A"
        assert entry.confidence == 0.85
        assert entry.source == SelectionSource.AUTO

    def test_menu_history_entry_optional_workflow_context_default_none(self):
        """MenuHistoryEntry workflow_context defaults to None."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="Continue",
            confidence=0.90,
            source=SelectionSource.MANUAL,
        )

        assert entry.workflow_context is None

    def test_menu_history_entry_with_workflow_context(self):
        """MenuHistoryEntry can be created with workflow_context."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="Continue",
            confidence=0.75,
            source=SelectionSource.ESCALATED,
            workflow_context="bmad:bmm:workflows:create-prd",
        )

        assert entry.workflow_context == "bmad:bmm:workflows:create-prd"

    def test_menu_history_entry_confidence_can_be_zero(self):
        """MenuHistoryEntry confidence can be 0.0."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="Option",
            confidence=0.0,
            source=SelectionSource.MANUAL,
        )

        assert entry.confidence == 0.0

    def test_menu_history_entry_confidence_can_be_one(self):
        """MenuHistoryEntry confidence can be 1.0."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="Option",
            confidence=1.0,
            source=SelectionSource.AUTO,
        )

        assert entry.confidence == 1.0

    def test_menu_history_entry_confidence_below_zero_raises(self):
        """MenuHistoryEntry confidence below 0.0 should raise ValueError."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            MenuHistoryEntry(
                timestamp=datetime.now(timezone.utc),
                menu_id="menu-1",
                selection="Option",
                confidence=-0.1,
                source=SelectionSource.AUTO,
            )

    def test_menu_history_entry_confidence_above_one_raises(self):
        """MenuHistoryEntry confidence above 1.0 should raise ValueError."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            MenuHistoryEntry(
                timestamp=datetime.now(timezone.utc),
                menu_id="menu-1",
                selection="Option",
                confidence=1.5,
                source=SelectionSource.AUTO,
            )


# =============================================================================
# Task 1: MenuHistoryEntry serialization tests (AC #4)
# =============================================================================


class TestMenuHistoryEntrySerialization:
    """Tests for MenuHistoryEntry serialization (Task 1 - AC #4)."""

    def test_to_dict_includes_all_fields(self):
        """to_dict() includes all required fields."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        now = datetime(2026, 1, 13, 12, 0, 0, tzinfo=timezone.utc)
        entry = MenuHistoryEntry(
            timestamp=now,
            menu_id="menu-abc",
            selection="Yes",
            confidence=0.92,
            source=SelectionSource.AUTO,
            workflow_context="test-workflow",
        )

        data = entry.to_dict()

        assert "timestamp" in data
        assert "menu_id" in data
        assert "selection" in data
        assert "confidence" in data
        assert "source" in data
        assert "workflow_context" in data

    def test_to_dict_serializes_timestamp_as_iso_string(self):
        """to_dict() serializes timestamp as ISO format string."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        now = datetime(2026, 1, 13, 12, 30, 45, tzinfo=timezone.utc)
        entry = MenuHistoryEntry(
            timestamp=now,
            menu_id="menu-1",
            selection="A",
            confidence=0.5,
            source=SelectionSource.MANUAL,
        )

        data = entry.to_dict()

        assert isinstance(data["timestamp"], str)
        assert "2026-01-13" in data["timestamp"]

    def test_to_dict_serializes_source_as_string_value(self):
        """to_dict() serializes source as string value."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="A",
            confidence=0.5,
            source=SelectionSource.ESCALATED,
        )

        data = entry.to_dict()

        assert data["source"] == "escalated"

    def test_to_dict_preserves_none_workflow_context(self):
        """to_dict() preserves None for workflow_context."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="A",
            confidence=0.5,
            source=SelectionSource.AUTO,
        )

        data = entry.to_dict()

        assert data["workflow_context"] is None

    def test_from_dict_creates_entry_with_all_fields(self):
        """from_dict() creates entry with all fields."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        data = {
            "timestamp": "2026-01-13T12:00:00+00:00",
            "menu_id": "menu-xyz",
            "selection": "No",
            "confidence": 0.77,
            "source": "manual",
            "workflow_context": "workflow-1",
        }

        entry = MenuHistoryEntry.from_dict(data)

        assert entry.menu_id == "menu-xyz"
        assert entry.selection == "No"
        assert entry.confidence == 0.77
        assert entry.source == SelectionSource.MANUAL
        assert entry.workflow_context == "workflow-1"

    def test_from_dict_parses_timestamp(self):
        """from_dict() correctly parses ISO timestamp."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        data = {
            "timestamp": "2026-01-13T12:30:45+00:00",
            "menu_id": "menu-1",
            "selection": "A",
            "confidence": 0.5,
            "source": "auto",
            "workflow_context": None,
        }

        entry = MenuHistoryEntry.from_dict(data)

        assert entry.timestamp.year == 2026
        assert entry.timestamp.month == 1
        assert entry.timestamp.day == 13
        assert entry.timestamp.hour == 12
        assert entry.timestamp.minute == 30
        assert entry.timestamp.second == 45

    def test_from_dict_handles_escalated_source(self):
        """from_dict() correctly parses 'escalated' source."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        data = {
            "timestamp": "2026-01-13T12:00:00+00:00",
            "menu_id": "menu-1",
            "selection": "A",
            "confidence": 0.5,
            "source": "escalated",
            "workflow_context": None,
        }

        entry = MenuHistoryEntry.from_dict(data)

        assert entry.source == SelectionSource.ESCALATED

    def test_serialization_round_trip(self):
        """Serialization round-trip preserves all data."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        original = MenuHistoryEntry(
            timestamp=datetime(2026, 1, 13, 14, 25, 30, tzinfo=timezone.utc),
            menu_id="round-trip-menu",
            selection="Selected Option",
            confidence=0.88,
            source=SelectionSource.AUTO,
            workflow_context="bmad:core:workflows:brainstorming",
        )

        # Round-trip
        data = original.to_dict()
        restored = MenuHistoryEntry.from_dict(data)

        assert restored.menu_id == original.menu_id
        assert restored.selection == original.selection
        assert restored.confidence == original.confidence
        assert restored.source == original.source
        assert restored.workflow_context == original.workflow_context
        # Compare timestamps (strip microseconds for comparison)
        assert restored.timestamp.replace(microsecond=0) == original.timestamp.replace(
            microsecond=0
        )

    def test_round_trip_with_none_workflow_context(self):
        """Round-trip preserves None workflow_context."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        original = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="Option",
            confidence=0.5,
            source=SelectionSource.MANUAL,
            workflow_context=None,
        )

        data = original.to_dict()
        restored = MenuHistoryEntry.from_dict(data)

        assert restored.workflow_context is None


# =============================================================================
# from_dict() Error Handling Tests (Issue 5)
# =============================================================================


class TestFromDictErrorHandling:
    """Tests for from_dict() error handling with better messages."""

    def test_from_dict_missing_timestamp_raises_with_message(self):
        """from_dict() should raise ValueError with field name when timestamp missing."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryEntry

        data = {
            "menu_id": "menu-1",
            "selection": "Option",
            "confidence": 0.5,
            "source": "auto",
        }

        with pytest.raises(ValueError, match="timestamp"):
            MenuHistoryEntry.from_dict(data)

    def test_from_dict_missing_menu_id_raises_with_message(self):
        """from_dict() should raise ValueError with field name when menu_id missing."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryEntry

        data = {
            "timestamp": "2025-01-10T12:00:00+00:00",
            "selection": "Option",
            "confidence": 0.5,
            "source": "auto",
        }

        with pytest.raises(ValueError, match="menu_id"):
            MenuHistoryEntry.from_dict(data)

    def test_from_dict_invalid_source_raises_with_message(self):
        """from_dict() should raise ValueError with field info when source invalid."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryEntry

        data = {
            "timestamp": "2025-01-10T12:00:00+00:00",
            "menu_id": "menu-1",
            "selection": "Option",
            "confidence": 0.5,
            "source": "invalid_source",
        }

        with pytest.raises(ValueError, match="source"):
            MenuHistoryEntry.from_dict(data)

    def test_from_dict_invalid_timestamp_format_raises_with_message(self):
        """from_dict() should raise ValueError with field info when timestamp format invalid."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryEntry

        data = {
            "timestamp": "not-a-valid-timestamp",
            "menu_id": "menu-1",
            "selection": "Option",
            "confidence": 0.5,
            "source": "auto",
        }

        with pytest.raises(ValueError, match="timestamp"):
            MenuHistoryEntry.from_dict(data)

    def test_from_dict_invalid_confidence_raises_with_message(self):
        """from_dict() should raise ValueError with field info when confidence out of range."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryEntry

        data = {
            "timestamp": "2025-01-10T12:00:00+00:00",
            "menu_id": "menu-1",
            "selection": "Option",
            "confidence": 2.0,  # Invalid - above 1.0
            "source": "auto",
        }

        with pytest.raises(ValueError, match="[Cc]onfidence"):
            MenuHistoryEntry.from_dict(data)

    def test_from_dict_missing_workflow_context_defaults_to_none(self):
        """from_dict() handles missing workflow_context key gracefully (defaults to None)."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        # Data without workflow_context key at all
        data = {
            "timestamp": "2025-01-10T12:00:00+00:00",
            "menu_id": "menu-1",
            "selection": "Option",
            "confidence": 0.85,
            "source": "auto",
            # Note: no workflow_context key
        }

        entry = MenuHistoryEntry.from_dict(data)

        # Should default to None without error
        assert entry.workflow_context is None
        assert entry.menu_id == "menu-1"
        assert entry.source == SelectionSource.AUTO


# =============================================================================
# Task 2: MenuHistoryManager constants tests
# =============================================================================


class TestMenuHistoryManagerConstants:
    """Tests for MenuHistoryManager constants (Task 2)."""

    def test_max_history_size_is_100(self):
        """MAX_HISTORY_SIZE constant is 100."""
        from pcmrp_tools.bmad_automation.menu_history import MAX_HISTORY_SIZE

        assert MAX_HISTORY_SIZE == 100


# =============================================================================
# Task 2: MenuHistoryManager basic operations tests
# =============================================================================


class TestMenuHistoryManagerBasics:
    """Tests for MenuHistoryManager basic operations (Task 2)."""

    def test_init_creates_empty_history(self):
        """MenuHistoryManager initializes with empty history."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()

        assert len(manager) == 0

    def test_add_entry_increases_size(self):
        """add_entry() increases history size."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="A",
            confidence=0.8,
            source=SelectionSource.AUTO,
        )

        manager.add_entry(entry)

        assert len(manager) == 1

    def test_get_history_returns_all_entries(self):
        """get_history() returns all added entries."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry1 = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="A",
            confidence=0.8,
            source=SelectionSource.AUTO,
        )
        entry2 = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-2",
            selection="B",
            confidence=0.9,
            source=SelectionSource.MANUAL,
        )

        manager.add_entry(entry1)
        manager.add_entry(entry2)

        history = manager.get_history()

        assert len(history) == 2
        assert entry1 in history
        assert entry2 in history

    def test_get_history_returns_copy(self):
        """get_history() returns a copy, not the internal list."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="A",
            confidence=0.8,
            source=SelectionSource.AUTO,
        )
        manager.add_entry(entry)

        history = manager.get_history()
        history.clear()  # Modify the returned list

        # Internal list should be unchanged
        assert len(manager) == 1

    def test_clear_history_removes_all_entries(self):
        """clear_history() removes all entries."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        for i in range(5):
            entry = MenuHistoryEntry(
                timestamp=datetime.now(timezone.utc),
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.5,
                source=SelectionSource.AUTO,
            )
            manager.add_entry(entry)

        assert len(manager) == 5

        manager.clear_history()

        assert len(manager) == 0


# =============================================================================
# Task 2: MenuHistoryManager.get_recent() tests
# =============================================================================


class TestMenuHistoryManagerGetRecent:
    """Tests for MenuHistoryManager.get_recent() (Task 2)."""

    def test_get_recent_returns_last_n_entries(self):
        """get_recent(n) returns the last n entries."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        for i in range(10):
            entry = MenuHistoryEntry(
                timestamp=datetime.now(timezone.utc),
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.5,
                source=SelectionSource.AUTO,
            )
            manager.add_entry(entry)

        recent = manager.get_recent(3)

        assert len(recent) == 3
        # Should be the last 3 entries (menu-7, menu-8, menu-9)
        assert recent[0].menu_id == "menu-7"
        assert recent[1].menu_id == "menu-8"
        assert recent[2].menu_id == "menu-9"

    def test_get_recent_returns_all_if_count_exceeds_size(self):
        """get_recent(n) returns all entries if n exceeds history size."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        for i in range(5):
            entry = MenuHistoryEntry(
                timestamp=datetime.now(timezone.utc),
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.5,
                source=SelectionSource.AUTO,
            )
            manager.add_entry(entry)

        recent = manager.get_recent(10)

        assert len(recent) == 5

    def test_get_recent_returns_empty_for_empty_history(self):
        """get_recent() returns empty list for empty history."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()

        recent = manager.get_recent(5)

        assert recent == []

    def test_get_recent_with_zero_returns_empty(self):
        """get_recent(0) returns empty list."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="A",
            confidence=0.5,
            source=SelectionSource.AUTO,
        )
        manager.add_entry(entry)

        recent = manager.get_recent(0)

        assert recent == []

    def test_get_recent_with_negative_returns_empty(self):
        """get_recent(-n) with negative count returns empty list."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        for i in range(5):
            entry = MenuHistoryEntry(
                timestamp=datetime.now(timezone.utc),
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.5,
                source=SelectionSource.AUTO,
            )
            manager.add_entry(entry)

        # All negative values should return empty list
        assert manager.get_recent(-1) == []
        assert manager.get_recent(-10) == []
        assert manager.get_recent(-100) == []


# =============================================================================
# Task 2: MenuHistoryManager FIFO pruning tests (AC #3)
# =============================================================================


class TestMenuHistoryManagerFIFOPruning:
    """Tests for MenuHistoryManager FIFO pruning at MAX_HISTORY_SIZE (Task 2 - AC #3)."""

    def _create_entry(self, i: int) -> "MenuHistoryEntry":
        """Helper to create an entry with index in menu_id."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            SelectionSource,
        )

        return MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id=f"menu-{i}",
            selection=f"Option {i}",
            confidence=0.5,
            source=SelectionSource.AUTO,
        )

    def test_fifo_no_pruning_at_99_entries(self):
        """Adding 99 entries does not trigger pruning."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        for i in range(99):
            manager.add_entry(self._create_entry(i))

        assert len(manager) == 99

        # All entries should be present
        history = manager.get_history()
        assert history[0].menu_id == "menu-0"
        assert history[98].menu_id == "menu-98"

    def test_fifo_no_pruning_at_100_entries(self):
        """Adding 100 entries exactly fills history without pruning."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        for i in range(100):
            manager.add_entry(self._create_entry(i))

        assert len(manager) == 100

        # All entries should be present
        history = manager.get_history()
        assert history[0].menu_id == "menu-0"
        assert history[99].menu_id == "menu-99"

    def test_fifo_pruning_at_101_entries(self):
        """Adding 101st entry triggers FIFO pruning, removing oldest."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        for i in range(101):
            manager.add_entry(self._create_entry(i))

        # Should still be 100 after pruning
        assert len(manager) == 100

        # First entry (menu-0) should be removed
        history = manager.get_history()
        assert history[0].menu_id == "menu-1"  # Previously second
        assert history[99].menu_id == "menu-100"  # Newly added

    def test_fifo_preserves_order_after_pruning(self):
        """FIFO pruning preserves entry order."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        # Add 105 entries
        for i in range(105):
            manager.add_entry(self._create_entry(i))

        assert len(manager) == 100

        # Oldest 5 entries (0-4) should be removed
        history = manager.get_history()
        assert history[0].menu_id == "menu-5"
        assert history[1].menu_id == "menu-6"
        assert history[99].menu_id == "menu-104"

    def test_fifo_continuous_pruning(self):
        """FIFO pruning works continuously as entries are added."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()

        # Fill to 100
        for i in range(100):
            manager.add_entry(self._create_entry(i))
        assert len(manager) == 100

        # Add 10 more one at a time
        for i in range(100, 110):
            manager.add_entry(self._create_entry(i))
            assert len(manager) == 100  # Should always be 100

        history = manager.get_history()
        assert history[0].menu_id == "menu-10"
        assert history[99].menu_id == "menu-109"


# =============================================================================
# Task 2: MenuHistoryManager.__len__() tests
# =============================================================================


class TestMenuHistoryManagerLen:
    """Tests for MenuHistoryManager.__len__() (Task 2)."""

    def test_len_returns_zero_for_empty(self):
        """len() returns 0 for empty manager."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()

        assert len(manager) == 0

    def test_len_returns_correct_count(self):
        """len() returns correct count after adding entries."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()

        for i in range(25):
            entry = MenuHistoryEntry(
                timestamp=datetime.now(timezone.utc),
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.5,
                source=SelectionSource.AUTO,
            )
            manager.add_entry(entry)

        assert len(manager) == 25

    def test_len_updates_after_clear(self):
        """len() returns 0 after clear_history()."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()

        for i in range(10):
            entry = MenuHistoryEntry(
                timestamp=datetime.now(timezone.utc),
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.5,
                source=SelectionSource.AUTO,
            )
            manager.add_entry(entry)

        assert len(manager) == 10

        manager.clear_history()

        assert len(manager) == 0


# =============================================================================
# Task 3: File Persistence Tests (AC: #2)
# =============================================================================

import json
from pathlib import Path


class TestGetSessionHistoryPath:
    """Test Task 3.1: get_session_history_path() static method."""

    def test_get_session_history_path_returns_path(self):
        """get_session_history_path should return a Path object."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        result = MenuHistoryManager.get_session_history_path("test-session-123")
        assert isinstance(result, Path)

    def test_get_session_history_path_includes_session_id(self):
        """Path should include the session ID in filename."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        result = MenuHistoryManager.get_session_history_path("my-session-abc")
        assert "my-session-abc" in str(result)

    def test_get_session_history_path_has_json_extension(self):
        """Path should have .json extension."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        result = MenuHistoryManager.get_session_history_path("test-session")
        assert result.suffix == ".json"

    def test_get_session_history_path_uses_correct_directory(self):
        """Path should be in _bmad-output/.menu-history/ directory."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        result = MenuHistoryManager.get_session_history_path("session-001")
        # Check directory components
        assert "_bmad-output" in result.parts
        assert ".menu-history" in result.parts

    def test_get_session_history_path_pattern(self):
        """Path should follow pattern: _bmad-output/.menu-history/session-{id}.json"""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        result = MenuHistoryManager.get_session_history_path("abc123")
        assert result.name == "session-abc123.json"

    def test_get_session_history_path_rejects_path_traversal(self):
        """Session ID with path traversal characters should raise ValueError."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        with pytest.raises(ValueError, match="Invalid session_id"):
            MenuHistoryManager.get_session_history_path("../../../etc/passwd")

    def test_get_session_history_path_rejects_slashes(self):
        """Session ID with slashes should raise ValueError."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        with pytest.raises(ValueError, match="Invalid session_id"):
            MenuHistoryManager.get_session_history_path("path/to/evil")

    def test_get_session_history_path_rejects_backslashes(self):
        """Session ID with backslashes should raise ValueError."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        with pytest.raises(ValueError, match="Invalid session_id"):
            MenuHistoryManager.get_session_history_path("path\\to\\evil")

    def test_get_session_history_path_rejects_special_characters(self):
        """Session ID with special characters should raise ValueError."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        with pytest.raises(ValueError, match="Invalid session_id"):
            MenuHistoryManager.get_session_history_path("session!@#$%")

    def test_get_session_history_path_allows_alphanumeric_underscore_dash(self):
        """Session ID with alphanumeric, underscore, and dash should be valid."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        # These should all work without raising
        result1 = MenuHistoryManager.get_session_history_path("abc123")
        assert "abc123" in str(result1)

        result2 = MenuHistoryManager.get_session_history_path("session_with_underscores")
        assert "session_with_underscores" in str(result2)

        result3 = MenuHistoryManager.get_session_history_path("session-with-dashes")
        assert "session-with-dashes" in str(result3)

        result4 = MenuHistoryManager.get_session_history_path("MixedCase123_test-id")
        assert "MixedCase123_test-id" in str(result4)


class TestSaveToFile:
    """Test Task 3.2: save_to_file() method."""

    def test_save_to_file_creates_file(self, tmp_path):
        """save_to_file should create the JSON file."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime(2025, 1, 10, 12, 0, 0),
            menu_id="menu-1",
            selection="Continue",
            confidence=0.85,
            source=SelectionSource.AUTO,
            workflow_context="test-workflow",
        )
        manager.add_entry(entry)

        file_path = tmp_path / "history.json"
        manager.save_to_file(file_path)

        assert file_path.exists()

    def test_save_to_file_writes_valid_json(self, tmp_path):
        """save_to_file should write valid JSON."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime(2025, 1, 10, 12, 0, 0),
            menu_id="menu-1",
            selection="Continue",
            confidence=0.85,
            source=SelectionSource.AUTO,
            workflow_context="test-workflow",
        )
        manager.add_entry(entry)

        file_path = tmp_path / "history.json"
        manager.save_to_file(file_path)

        # Should be parseable JSON
        with open(file_path) as f:
            data = json.load(f)
        assert isinstance(data, list)

    def test_save_to_file_includes_all_entries(self, tmp_path):
        """save_to_file should include all history entries."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        for i in range(3):
            entry = MenuHistoryEntry(
                timestamp=datetime(2025, 1, 10, 12, i, 0),
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.80 + i * 0.01,
                source=SelectionSource.AUTO,
                workflow_context="test-workflow",
            )
            manager.add_entry(entry)

        file_path = tmp_path / "history.json"
        manager.save_to_file(file_path)

        with open(file_path) as f:
            data = json.load(f)
        assert len(data) == 3

    def test_save_to_file_preserves_entry_data(self, tmp_path):
        """save_to_file should preserve all entry fields."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime(2025, 1, 10, 14, 30, 45),
            menu_id="test-menu-id",
            selection="My Selection",
            confidence=0.92,
            source=SelectionSource.MANUAL,
            workflow_context="my-workflow-context",
        )
        manager.add_entry(entry)

        file_path = tmp_path / "history.json"
        manager.save_to_file(file_path)

        with open(file_path) as f:
            data = json.load(f)

        assert len(data) == 1
        saved_entry = data[0]
        assert saved_entry["menu_id"] == "test-menu-id"
        assert saved_entry["selection"] == "My Selection"
        assert saved_entry["confidence"] == 0.92
        assert saved_entry["workflow_context"] == "my-workflow-context"

    def test_save_to_file_empty_history(self, tmp_path):
        """save_to_file should handle empty history gracefully."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        file_path = tmp_path / "empty.json"
        manager.save_to_file(file_path)

        with open(file_path) as f:
            data = json.load(f)
        assert data == []

    def test_save_to_file_creates_parent_directories(self, tmp_path):
        """save_to_file should create parent directories if needed."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="Continue",
            confidence=0.85,
            source=SelectionSource.AUTO,
            workflow_context="test",
        )
        manager.add_entry(entry)

        file_path = tmp_path / "nested" / "deep" / "history.json"
        manager.save_to_file(file_path)

        assert file_path.exists()


class TestLoadFromFile:
    """Test Task 3.3: load_from_file() method."""

    def test_load_from_file_restores_entries(self, tmp_path):
        """load_from_file should restore saved entries."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        # First save some entries
        manager1 = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime(2025, 1, 10, 12, 0, 0),
            menu_id="menu-1",
            selection="Continue",
            confidence=0.85,
            source=SelectionSource.AUTO,
            workflow_context="test-workflow",
        )
        manager1.add_entry(entry)

        file_path = tmp_path / "history.json"
        manager1.save_to_file(file_path)

        # Then load into new manager
        manager2 = MenuHistoryManager()
        manager2.load_from_file(file_path)

        entries = manager2.get_all_entries()
        assert len(entries) == 1
        assert entries[0].menu_id == "menu-1"
        assert entries[0].selection == "Continue"

    def test_load_from_file_missing_file_returns_empty(self, tmp_path):
        """load_from_file should handle missing file gracefully."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        nonexistent_path = tmp_path / "does_not_exist.json"

        # Should not raise, should result in empty history
        manager.load_from_file(nonexistent_path)

        entries = manager.get_all_entries()
        assert entries == []

    def test_load_from_file_corrupt_json_returns_empty(self, tmp_path):
        """load_from_file should handle corrupt JSON gracefully."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        # Create a corrupt JSON file
        file_path = tmp_path / "corrupt.json"
        with open(file_path, "w") as f:
            f.write("{ this is not valid json [")

        manager = MenuHistoryManager()
        # Should not raise, should result in empty history
        manager.load_from_file(file_path)

        entries = manager.get_all_entries()
        assert entries == []

    def test_load_from_file_empty_file_returns_empty(self, tmp_path):
        """load_from_file should handle empty file gracefully."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        # Create an empty file
        file_path = tmp_path / "empty.json"
        file_path.touch()

        manager = MenuHistoryManager()
        manager.load_from_file(file_path)

        entries = manager.get_all_entries()
        assert entries == []

    def test_load_from_file_preserves_all_fields(self, tmp_path):
        """load_from_file should preserve all entry fields."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        original_time = datetime(2025, 1, 15, 10, 30, 45)

        manager1 = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=original_time,
            menu_id="full-test-menu",
            selection="Full Test Option",
            confidence=0.99,
            source=SelectionSource.ESCALATED,
            workflow_context="full-test-context",
        )
        manager1.add_entry(entry)

        file_path = tmp_path / "history.json"
        manager1.save_to_file(file_path)

        manager2 = MenuHistoryManager()
        manager2.load_from_file(file_path)

        loaded = manager2.get_all_entries()
        assert len(loaded) == 1
        assert loaded[0].menu_id == "full-test-menu"
        assert loaded[0].selection == "Full Test Option"
        assert loaded[0].confidence == 0.99
        assert loaded[0].workflow_context == "full-test-context"
        # Timestamp should be restored
        assert loaded[0].timestamp.year == 2025
        assert loaded[0].timestamp.month == 1
        assert loaded[0].timestamp.day == 15

    def test_load_from_file_multiple_entries(self, tmp_path):
        """load_from_file should load multiple entries correctly."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager1 = MenuHistoryManager()
        for i in range(5):
            entry = MenuHistoryEntry(
                timestamp=datetime(2025, 1, 10, 12, i, 0),
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.80 + i * 0.01,
                source=SelectionSource.AUTO,
                workflow_context=f"workflow-{i}",
            )
            manager1.add_entry(entry)

        file_path = tmp_path / "history.json"
        manager1.save_to_file(file_path)

        manager2 = MenuHistoryManager()
        manager2.load_from_file(file_path)

        loaded = manager2.get_all_entries()
        assert len(loaded) == 5
        for i in range(5):
            assert loaded[i].menu_id == f"menu-{i}"

    def test_load_from_file_replaces_existing_entries(self, tmp_path):
        """load_from_file should replace any existing entries in manager."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        # Create a file with one entry
        manager1 = MenuHistoryManager()
        entry1 = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="from-file",
            selection="FileOption",
            confidence=0.90,
            source=SelectionSource.AUTO,
            workflow_context="file-context",
        )
        manager1.add_entry(entry1)
        file_path = tmp_path / "history.json"
        manager1.save_to_file(file_path)

        # Create a manager with a different entry
        manager2 = MenuHistoryManager()
        entry2 = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="existing",
            selection="ExistingOption",
            confidence=0.50,
            source=SelectionSource.MANUAL,
            workflow_context="existing-context",
        )
        manager2.add_entry(entry2)

        # Loading from file should replace
        manager2.load_from_file(file_path)

        entries = manager2.get_all_entries()
        assert len(entries) == 1
        assert entries[0].menu_id == "from-file"


# =============================================================================
# Task 4: Chronological Access Tests (AC: #4)
# =============================================================================


class TestGetEntriesSince:
    """Test Task 4.1: get_entries_since() method."""

    def test_get_entries_since_returns_list(self):
        """get_entries_since should return a list."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        result = manager.get_entries_since(datetime.now(timezone.utc))
        assert isinstance(result, list)

    def test_get_entries_since_empty_history(self):
        """get_entries_since should return empty list for empty history."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        result = manager.get_entries_since(datetime(2020, 1, 1))
        assert result == []

    def test_get_entries_since_filters_by_timestamp(self):
        """get_entries_since should only return entries after timestamp."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()

        # Add entries at different times
        times = [
            datetime(2025, 1, 10, 10, 0, 0),  # Before cutoff
            datetime(2025, 1, 10, 12, 0, 0),  # At cutoff
            datetime(2025, 1, 10, 14, 0, 0),  # After cutoff
            datetime(2025, 1, 10, 16, 0, 0),  # After cutoff
        ]
        for i, t in enumerate(times):
            entry = MenuHistoryEntry(
                timestamp=t,
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.80,
                source=SelectionSource.AUTO,
                workflow_context="test",
            )
            manager.add_entry(entry)

        # Get entries since 12:00
        cutoff = datetime(2025, 1, 10, 12, 0, 0)
        result = manager.get_entries_since(cutoff)

        # Should include entries AT or AFTER cutoff
        assert len(result) == 3  # 12:00, 14:00, 16:00
        assert all(e.timestamp >= cutoff for e in result)

    def test_get_entries_since_chronological_order(self):
        """get_entries_since should return entries in chronological order (oldest first)."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()

        # Add entries out of order
        times = [
            datetime(2025, 1, 10, 16, 0, 0),
            datetime(2025, 1, 10, 12, 0, 0),
            datetime(2025, 1, 10, 14, 0, 0),
        ]
        for i, t in enumerate(times):
            entry = MenuHistoryEntry(
                timestamp=t,
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.80,
                source=SelectionSource.AUTO,
                workflow_context="test",
            )
            manager.add_entry(entry)

        cutoff = datetime(2025, 1, 10, 11, 0, 0)
        result = manager.get_entries_since(cutoff)

        # Should be in chronological order
        assert len(result) == 3
        assert result[0].timestamp == datetime(2025, 1, 10, 12, 0, 0)
        assert result[1].timestamp == datetime(2025, 1, 10, 14, 0, 0)
        assert result[2].timestamp == datetime(2025, 1, 10, 16, 0, 0)

    def test_get_entries_since_no_matches(self):
        """get_entries_since should return empty list if no entries after timestamp."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime(2025, 1, 10, 12, 0, 0),
            menu_id="menu-1",
            selection="Option",
            confidence=0.80,
            source=SelectionSource.AUTO,
            workflow_context="test",
        )
        manager.add_entry(entry)

        # Cutoff after all entries
        cutoff = datetime(2025, 1, 11, 0, 0, 0)
        result = manager.get_entries_since(cutoff)
        assert result == []


class TestGetEntriesForMenu:
    """Test Task 4.2: get_entries_for_menu() method."""

    def test_get_entries_for_menu_returns_list(self):
        """get_entries_for_menu should return a list."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        result = manager.get_entries_for_menu("any-menu")
        assert isinstance(result, list)

    def test_get_entries_for_menu_empty_history(self):
        """get_entries_for_menu should return empty list for empty history."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        result = manager.get_entries_for_menu("menu-id")
        assert result == []

    def test_get_entries_for_menu_filters_by_menu_id(self):
        """get_entries_for_menu should only return entries with matching menu_id."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()

        # Add entries for different menus
        menu_ids = ["menu-a", "menu-b", "menu-a", "menu-c", "menu-a"]
        for i, menu_id in enumerate(menu_ids):
            entry = MenuHistoryEntry(
                timestamp=datetime(2025, 1, 10, 12, i, 0),
                menu_id=menu_id,
                selection=f"Option {i}",
                confidence=0.80,
                source=SelectionSource.AUTO,
                workflow_context="test",
            )
            manager.add_entry(entry)

        # Get entries for menu-a
        result = manager.get_entries_for_menu("menu-a")

        assert len(result) == 3
        assert all(e.menu_id == "menu-a" for e in result)

    def test_get_entries_for_menu_chronological_order(self):
        """get_entries_for_menu should return entries in chronological order."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()

        # Add entries out of order
        times = [
            datetime(2025, 1, 10, 16, 0, 0),
            datetime(2025, 1, 10, 12, 0, 0),
            datetime(2025, 1, 10, 14, 0, 0),
        ]
        for t in times:
            entry = MenuHistoryEntry(
                timestamp=t,
                menu_id="same-menu",
                selection="Option",
                confidence=0.80,
                source=SelectionSource.AUTO,
                workflow_context="test",
            )
            manager.add_entry(entry)

        result = manager.get_entries_for_menu("same-menu")

        assert len(result) == 3
        # Should be chronological (oldest first)
        assert result[0].timestamp == datetime(2025, 1, 10, 12, 0, 0)
        assert result[1].timestamp == datetime(2025, 1, 10, 14, 0, 0)
        assert result[2].timestamp == datetime(2025, 1, 10, 16, 0, 0)

    def test_get_entries_for_menu_no_matches(self):
        """get_entries_for_menu should return empty list if no matching menu_id."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-a",
            selection="Option",
            confidence=0.80,
            source=SelectionSource.AUTO,
            workflow_context="test",
        )
        manager.add_entry(entry)

        result = manager.get_entries_for_menu("menu-b")
        assert result == []


class TestGetEntriesForWorkflow:
    """Test Task 4.3: get_entries_for_workflow() method."""

    def test_get_entries_for_workflow_returns_list(self):
        """get_entries_for_workflow should return a list."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        result = manager.get_entries_for_workflow("any-workflow")
        assert isinstance(result, list)

    def test_get_entries_for_workflow_empty_history(self):
        """get_entries_for_workflow should return empty list for empty history."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        manager = MenuHistoryManager()
        result = manager.get_entries_for_workflow("workflow-id")
        assert result == []

    def test_get_entries_for_workflow_filters_by_context(self):
        """get_entries_for_workflow should filter by workflow_context."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()

        # Add entries for different workflows
        workflows = ["wf-a", "wf-b", "wf-a", "wf-c", "wf-a"]
        for i, wf in enumerate(workflows):
            entry = MenuHistoryEntry(
                timestamp=datetime(2025, 1, 10, 12, i, 0),
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.80,
                source=SelectionSource.AUTO,
                workflow_context=wf,
            )
            manager.add_entry(entry)

        result = manager.get_entries_for_workflow("wf-a")

        assert len(result) == 3
        assert all(e.workflow_context == "wf-a" for e in result)

    def test_get_entries_for_workflow_chronological_order(self):
        """get_entries_for_workflow should return entries in chronological order."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()

        # Add entries out of order
        times = [
            datetime(2025, 1, 10, 16, 0, 0),
            datetime(2025, 1, 10, 12, 0, 0),
            datetime(2025, 1, 10, 14, 0, 0),
        ]
        for i, t in enumerate(times):
            entry = MenuHistoryEntry(
                timestamp=t,
                menu_id=f"menu-{i}",
                selection="Option",
                confidence=0.80,
                source=SelectionSource.AUTO,
                workflow_context="same-workflow",
            )
            manager.add_entry(entry)

        result = manager.get_entries_for_workflow("same-workflow")

        assert len(result) == 3
        # Should be chronological (oldest first)
        assert result[0].timestamp == datetime(2025, 1, 10, 12, 0, 0)
        assert result[1].timestamp == datetime(2025, 1, 10, 14, 0, 0)
        assert result[2].timestamp == datetime(2025, 1, 10, 16, 0, 0)

    def test_get_entries_for_workflow_no_matches(self):
        """get_entries_for_workflow should return empty list if no matching workflow."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="Option",
            confidence=0.80,
            source=SelectionSource.AUTO,
            workflow_context="workflow-a",
        )
        manager.add_entry(entry)

        result = manager.get_entries_for_workflow("workflow-b")
        assert result == []


# =============================================================================
# Edge Cases and Error Handling Tests for Tasks 3-4
# =============================================================================


class TestFilePersistenceEdgeCases:
    """Edge case tests for file persistence (Task 3)."""

    def test_save_and_load_with_special_characters_in_selection(self, tmp_path):
        """Should handle special characters in selection."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        entry = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-1",
            selection="Option with quotes and special chars",
            confidence=0.85,
            source=SelectionSource.AUTO,
            workflow_context="test",
        )
        manager.add_entry(entry)

        file_path = tmp_path / "special.json"
        manager.save_to_file(file_path)

        manager2 = MenuHistoryManager()
        manager2.load_from_file(file_path)

        loaded = manager2.get_all_entries()
        assert len(loaded) == 1
        assert "quotes" in loaded[0].selection

    def test_load_from_file_with_empty_json_array(self, tmp_path):
        """Should handle file with empty JSON array."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        file_path = tmp_path / "empty_array.json"
        with open(file_path, "w") as f:
            f.write("[]")

        manager = MenuHistoryManager()
        manager.load_from_file(file_path)

        entries = manager.get_all_entries()
        assert entries == []

    def test_load_from_file_with_non_array_json(self, tmp_path):
        """Should handle file with non-array JSON (should treat as corrupt)."""
        from pcmrp_tools.bmad_automation.menu_history import MenuHistoryManager

        file_path = tmp_path / "object.json"
        with open(file_path, "w") as f:
            f.write('{"key": "value"}')

        manager = MenuHistoryManager()
        manager.load_from_file(file_path)

        # Non-array should be treated as invalid, return empty
        entries = manager.get_all_entries()
        assert entries == []


# =============================================================================
# Task 5: Integration Tests (Issue 3 - HIGH)
# =============================================================================


class TestIntegrationSelectionToRecovery:
    """Integration tests for full selection-to-recovery flow (Task 5 - Issue 3)."""

    def test_menu_selector_record_selection_stores_entry(self, tmp_path, monkeypatch):
        """MenuSelector.record_selection() correctly stores an entry in history."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        # Create a selector with default settings
        selector = MenuSelector()

        # Record a selection
        selector.record_selection(
            menu_id="test-menu-1",
            selection="Option A",
            confidence=0.85,
            source=SelectionSource.AUTO,
            workflow_context="bmad:bmm:workflows:create-prd",
        )

        # Verify the entry was stored
        history = selector._history_manager.get_history()
        assert len(history) == 1
        assert history[0].menu_id == "test-menu-1"
        assert history[0].selection == "Option A"
        assert history[0].confidence == 0.85
        assert history[0].source == SelectionSource.AUTO
        assert history[0].workflow_context == "bmad:bmm:workflows:create-prd"

    def test_history_persisted_on_workflow_checkpoint(self, tmp_path, monkeypatch):
        """History is persisted when save_history is called on workflow checkpoint."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryManager,
            SelectionSource,
            HISTORY_DIR_NAME,
            MENU_HISTORY_SUBDIR,
        )
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        selector = MenuSelector()

        # Record multiple selections
        selector.record_selection(
            menu_id="checkpoint-menu-1",
            selection="Continue",
            confidence=0.92,
            source=SelectionSource.AUTO,
            workflow_context="test-workflow",
        )
        selector.record_selection(
            menu_id="checkpoint-menu-2",
            selection="Approve",
            confidence=0.88,
            source=SelectionSource.MANUAL,
            workflow_context="test-workflow",
        )

        # Save history (simulating a workflow checkpoint)
        selector.save_history("test-session-checkpoint")

        # Verify file was created
        expected_path = tmp_path / HISTORY_DIR_NAME / MENU_HISTORY_SUBDIR / "session-test-session-checkpoint.json"
        assert expected_path.exists()

        # Verify content
        import json
        with open(expected_path) as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["menu_id"] == "checkpoint-menu-1"
        assert data[1]["menu_id"] == "checkpoint-menu-2"

    def test_history_loads_correctly_on_workflow_resume(self, tmp_path, monkeypatch):
        """History loads correctly when load_history is called on workflow resume."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryManager,
            SelectionSource,
        )
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # First session: record and save
        selector1 = MenuSelector()
        selector1.record_selection(
            menu_id="resume-menu-1",
            selection="First Choice",
            confidence=0.75,
            source=SelectionSource.AUTO,
            workflow_context="workflow-to-resume",
        )
        selector1.record_selection(
            menu_id="resume-menu-2",
            selection="Second Choice",
            confidence=0.80,
            source=SelectionSource.MANUAL,
            workflow_context="workflow-to-resume",
        )
        selector1.save_history("resume-session")

        # Second session: load history
        selector2 = MenuSelector()
        selector2.load_history("resume-session")

        # Verify history was loaded
        history = selector2._history_manager.get_history()
        assert len(history) == 2
        assert history[0].menu_id == "resume-menu-1"
        assert history[0].selection == "First Choice"
        assert history[1].menu_id == "resume-menu-2"
        assert history[1].selection == "Second Choice"

    def test_full_selection_to_recovery_flow(self, tmp_path, monkeypatch):
        """End-to-end test of full selection-to-recovery flow.

        Scenario:
        1. Workflow starts and makes menu selections
        2. Selections are recorded to history
        3. History is saved at a checkpoint
        4. Workflow "crashes" (simulated by creating new selector)
        5. New selector loads history from checkpoint
        6. Workflow continues with more selections
        7. History contains both pre-crash and post-crash entries
        """
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        session_id = "e2e-test-session"
        workflow = "bmad:bmm:workflows:create-prd"

        # Step 1-3: Initial workflow session with checkpoint
        selector_v1 = MenuSelector()
        selector_v1.record_selection(
            menu_id="e2e-menu-1",
            selection="Define Requirements",
            confidence=0.95,
            source=SelectionSource.AUTO,
            workflow_context=workflow,
        )
        selector_v1.record_selection(
            menu_id="e2e-menu-2",
            selection="Add Feature",
            confidence=0.88,
            source=SelectionSource.MANUAL,
            workflow_context=workflow,
        )
        # Save at checkpoint
        selector_v1.save_history(session_id)

        # Step 4: Simulate crash by creating new selector
        del selector_v1

        # Step 5: Load history in new session
        selector_v2 = MenuSelector()
        selector_v2.load_history(session_id)

        # Step 6: Continue workflow with more selections
        selector_v2.record_selection(
            menu_id="e2e-menu-3",
            selection="Confirm Changes",
            confidence=0.92,
            source=SelectionSource.AUTO,
            workflow_context=workflow,
        )

        # Step 7: Verify complete history
        history = selector_v2._history_manager.get_history()
        assert len(history) == 3

        # Pre-crash entries preserved
        assert history[0].menu_id == "e2e-menu-1"
        assert history[0].selection == "Define Requirements"
        assert history[1].menu_id == "e2e-menu-2"
        assert history[1].selection == "Add Feature"

        # Post-crash entry added
        assert history[2].menu_id == "e2e-menu-3"
        assert history[2].selection == "Confirm Changes"

        # All have same workflow context
        assert all(e.workflow_context == workflow for e in history)

    def test_workflow_query_history_by_workflow_context(self, tmp_path, monkeypatch):
        """Workflow can query history by workflow_context after recovery."""
        from pcmrp_tools.bmad_automation.menu_history import SelectionSource
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        monkeypatch.chdir(tmp_path)

        # Create entries for different workflows
        selector = MenuSelector()
        selector.record_selection(
            menu_id="menu-1",
            selection="Option A",
            confidence=0.85,
            source=SelectionSource.AUTO,
            workflow_context="workflow-alpha",
        )
        selector.record_selection(
            menu_id="menu-2",
            selection="Option B",
            confidence=0.90,
            source=SelectionSource.MANUAL,
            workflow_context="workflow-beta",
        )
        selector.record_selection(
            menu_id="menu-3",
            selection="Option C",
            confidence=0.88,
            source=SelectionSource.AUTO,
            workflow_context="workflow-alpha",
        )

        # Save and reload
        selector.save_history("multi-workflow-session")

        new_selector = MenuSelector()
        new_selector.load_history("multi-workflow-session")

        # Query by workflow
        alpha_entries = new_selector._history_manager.get_entries_for_workflow("workflow-alpha")
        beta_entries = new_selector._history_manager.get_entries_for_workflow("workflow-beta")

        assert len(alpha_entries) == 2
        assert alpha_entries[0].selection == "Option A"
        assert alpha_entries[1].selection == "Option C"

        assert len(beta_entries) == 1
        assert beta_entries[0].selection == "Option B"


class TestChronologicalAccessEdgeCases:
    """Edge case tests for chronological access methods (Task 4)."""

    def test_get_entries_since_exact_timestamp_match(self):
        """get_entries_since should include entries at exactly the cutoff time."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        exact_time = datetime(2025, 1, 10, 12, 0, 0)
        entry = MenuHistoryEntry(
            timestamp=exact_time,
            menu_id="menu-1",
            selection="Option",
            confidence=0.80,
            source=SelectionSource.AUTO,
            workflow_context="test",
        )
        manager.add_entry(entry)

        result = manager.get_entries_since(exact_time)
        assert len(result) == 1

    def test_entries_with_same_timestamp(self):
        """Should handle multiple entries with the same timestamp."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()
        same_time = datetime(2025, 1, 10, 12, 0, 0)

        for i in range(3):
            entry = MenuHistoryEntry(
                timestamp=same_time,
                menu_id=f"menu-{i}",
                selection=f"Option {i}",
                confidence=0.80,
                source=SelectionSource.AUTO,
                workflow_context="test",
            )
            manager.add_entry(entry)

        result = manager.get_entries_since(same_time)
        assert len(result) == 3

    def test_get_entries_for_menu_case_sensitivity(self):
        """get_entries_for_menu should be case-sensitive."""
        from pcmrp_tools.bmad_automation.menu_history import (
            MenuHistoryEntry,
            MenuHistoryManager,
            SelectionSource,
        )

        manager = MenuHistoryManager()

        entry1 = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="Menu-A",
            selection="Option 1",
            confidence=0.80,
            source=SelectionSource.AUTO,
            workflow_context="test",
        )
        entry2 = MenuHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            menu_id="menu-a",
            selection="Option 2",
            confidence=0.80,
            source=SelectionSource.MANUAL,
            workflow_context="test",
        )
        manager.add_entry(entry1)
        manager.add_entry(entry2)

        result_upper = manager.get_entries_for_menu("Menu-A")
        result_lower = manager.get_entries_for_menu("menu-a")

        assert len(result_upper) == 1
        assert result_upper[0].selection == "Option 1"
        assert len(result_lower) == 1
        assert result_lower[0].selection == "Option 2"
