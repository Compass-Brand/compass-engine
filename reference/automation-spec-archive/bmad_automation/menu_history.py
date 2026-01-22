"""Menu History Tracking - Story 2b-5.

Provides tracking of menu selections with FIFO pruning for audit trails.

Components:
- SelectionSource enum: How a menu selection was made
- MenuHistoryEntry: Record of a single menu selection
- MenuHistoryManager: Manages menu selection history with FIFO pruning

Tasks 1-2: Basic entry and manager with FIFO pruning
Tasks 3-4: File persistence and chronological access
"""

import json
import logging
import re
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


# =============================================================================
# Constants
# =============================================================================

MAX_HISTORY_SIZE = 100
"""Maximum number of menu history entries before FIFO pruning."""

HISTORY_DIR_NAME = "_bmad-output"
"""Directory for BMAD output files."""

MENU_HISTORY_SUBDIR = ".menu-history"
"""Subdirectory for menu history files."""

SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
"""Valid session ID pattern: alphanumeric, underscore, and dash only."""

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class SelectionSource(Enum):
    """How a menu selection was made."""

    AUTO = "auto"  # Automatic selection by confidence
    MANUAL = "manual"  # User made the selection
    ESCALATED = "escalated"  # Selection after escalation


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class MenuHistoryEntry:
    """Record of a single menu selection.

    Attributes:
        timestamp: When the selection was made. IMPORTANT: All timestamps
            should be in UTC (use datetime.now(timezone.utc)). This ensures
            consistent chronological ordering across timezone boundaries
            and during workflow recovery.
        menu_id: Identifier for the menu that was presented.
        selection: The option that was selected.
        confidence: Confidence score (0.0 to 1.0) for the selection.
        source: How the selection was made (auto/manual/escalated).
        workflow_context: Optional workflow identifier for context.

    Note:
        The timestamp field expects UTC datetimes. Using local time may cause
        incorrect ordering in get_entries_since() and other chronological queries.
    """

    timestamp: datetime
    menu_id: str
    selection: str
    confidence: float
    source: SelectionSource
    workflow_context: str | None = None

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON storage.

        Returns:
            Dictionary with all fields serialized to JSON-safe types.
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "menu_id": self.menu_id,
            "selection": self.selection,
            "confidence": self.confidence,
            "source": self.source.value,
            "workflow_context": self.workflow_context,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MenuHistoryEntry":
        """Deserialize from dictionary.

        Args:
            data: Dictionary with serialized entry data.

        Returns:
            MenuHistoryEntry instance.

        Raises:
            ValueError: If required fields are missing or have invalid values.
        """
        # Check required fields
        required_fields = ["timestamp", "menu_id", "selection", "confidence", "source"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in menu history data")

        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(data["timestamp"])
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid timestamp format '{data['timestamp']}': {e}"
            ) from e

        # Parse source enum
        try:
            source = SelectionSource(data["source"])
        except ValueError as e:
            raise ValueError(
                f"Invalid source value '{data['source']}'. "
                f"Must be one of: {[s.value for s in SelectionSource]}"
            ) from e

        return cls(
            timestamp=timestamp,
            menu_id=data["menu_id"],
            selection=data["selection"],
            confidence=data["confidence"],
            source=source,
            workflow_context=data.get("workflow_context"),
        )


# =============================================================================
# Manager Class
# =============================================================================


class MenuHistoryManager:
    """Manages menu selection history with FIFO pruning.

    Maintains a history of menu selections up to MAX_HISTORY_SIZE entries.
    When the limit is exceeded, oldest entries are removed first (FIFO).
    Uses collections.deque with maxlen for O(1) FIFO pruning.

    Features:
    - FIFO pruning at MAX_HISTORY_SIZE (Task 1-2)
    - File persistence for recovery (Task 3)
    - Chronological access queries (Task 4)
    """

    def __init__(self) -> None:
        """Initialize with empty history using deque for efficient FIFO."""
        self._history: deque[MenuHistoryEntry] = deque(maxlen=MAX_HISTORY_SIZE)

    # =========================================================================
    # Tasks 1-2: Basic Entry Management
    # =========================================================================

    def add_entry(self, entry: MenuHistoryEntry) -> None:
        """Add entry with automatic FIFO pruning at MAX_HISTORY_SIZE.

        Uses deque maxlen for O(1) automatic pruning when capacity is reached.

        Args:
            entry: The menu history entry to add.
        """
        self._history.append(entry)

    def get_history(self) -> list[MenuHistoryEntry]:
        """Return full history list.

        Returns:
            Copy of the full history list.
        """
        return list(self._history)

    def get_all_entries(self) -> list[MenuHistoryEntry]:
        """Return all history entries.

        Alias for get_history() for clearer API.

        Returns:
            Copy of the full history list.
        """
        return list(self._history)

    def get_recent(self, count: int) -> list[MenuHistoryEntry]:
        """Return most recent N entries.

        Args:
            count: Number of recent entries to return.

        Returns:
            List of the most recent entries (up to count).
        """
        if count <= 0:
            return []
        # Convert to list and slice for negative indexing
        history_list = list(self._history)
        return history_list[-count:]

    def clear_history(self) -> None:
        """Clear all history entries."""
        self._history.clear()

    def __len__(self) -> int:
        """Return current history size.

        Returns:
            Number of entries in history.
        """
        return len(self._history)

    # =========================================================================
    # Task 3: File Persistence for Recovery (AC: #2)
    # =========================================================================

    @staticmethod
    def get_session_history_path(session_id: str) -> Path:
        """Generate path for session history file.

        Path pattern: _bmad-output/.menu-history/session-{id}.json

        Args:
            session_id: Unique identifier for the session. Must match pattern
                ^[a-zA-Z0-9_-]+$ (alphanumeric, underscore, dash only).

        Returns:
            Path to the session history JSON file.

        Raises:
            ValueError: If session_id contains invalid characters (path injection).
        """
        if not SESSION_ID_PATTERN.match(session_id):
            raise ValueError(
                f"Invalid session_id '{session_id}'. Must contain only "
                "alphanumeric characters, underscores, and dashes."
            )
        return Path(HISTORY_DIR_NAME) / MENU_HISTORY_SUBDIR / f"session-{session_id}.json"

    def save_to_file(self, path: Path) -> None:
        """Save history to JSON file for persistence.

        Creates parent directories if they don't exist.

        Args:
            path: Path to save the JSON file.
        """
        # Ensure parent directories exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize all entries
        data = [entry.to_dict() for entry in self._history]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, path: Path) -> None:
        """Load history from JSON file for recovery.

        Handles gracefully:
        - Missing file: results in empty history
        - Corrupt JSON: logs warning, results in empty history
        - Empty file: results in empty history
        - Non-array JSON: treated as corrupt, results in empty history

        Args:
            path: Path to the JSON file to load.
        """
        # Clear existing history (loading replaces)
        self._history.clear()

        # Handle missing file
        if not path.exists():
            logger.debug("History file does not exist: %s", path)
            return

        try:
            content = path.read_text(encoding="utf-8")

            # Handle empty file
            if not content.strip():
                logger.debug("History file is empty: %s", path)
                return

            data = json.loads(content)

            # Validate it's a list
            if not isinstance(data, list):
                logger.warning("History file is not a JSON array: %s", path)
                return

            # Deserialize entries
            for item in data:
                try:
                    entry = MenuHistoryEntry.from_dict(item)
                    self._history.append(entry)
                except (KeyError, TypeError, ValueError) as e:
                    logger.warning("Skipping invalid entry in history file: %s", e)

        except json.JSONDecodeError as e:
            logger.warning("Corrupt JSON in history file %s: %s", path, e)
        except OSError as e:
            logger.warning("Error reading history file %s: %s", path, e)

    # =========================================================================
    # Task 4: Chronological Access (AC: #4)
    # =========================================================================

    def get_entries_since(self, timestamp: datetime) -> list[MenuHistoryEntry]:
        """Return entries at or after the given timestamp, chronologically ordered.

        Args:
            timestamp: The cutoff timestamp (inclusive).

        Returns:
            List of entries with timestamp >= cutoff, sorted oldest first.
        """
        filtered = [e for e in self._history if e.timestamp >= timestamp]
        return sorted(filtered, key=lambda e: e.timestamp)

    def get_entries_for_menu(self, menu_id: str) -> list[MenuHistoryEntry]:
        """Return all entries for a specific menu_id, chronologically ordered.

        Case-sensitive matching on menu_id.

        Args:
            menu_id: The menu identifier to filter by.

        Returns:
            List of entries with matching menu_id, sorted oldest first.
        """
        filtered = [e for e in self._history if e.menu_id == menu_id]
        return sorted(filtered, key=lambda e: e.timestamp)

    def get_entries_for_workflow(self, workflow: str) -> list[MenuHistoryEntry]:
        """Return entries matching workflow_context, chronologically ordered.

        Args:
            workflow: The workflow context to filter by.

        Returns:
            List of entries with matching workflow_context, sorted oldest first.
        """
        filtered = [e for e in self._history if e.workflow_context == workflow]
        return sorted(filtered, key=lambda e: e.timestamp)
