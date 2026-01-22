"""Batch-Continue Logic - Story 2b-6.

This module manages batch-continue operations based on project tiers (0-4).
Different tiers have different batching behaviors:

- Tier 0-1 (AUTO_ALL): No batching, auto-continue all menus, summarize at end
- Tier 2-3 (BATCHED): Batch operations with checkpoints every N steps
- Tier 4 (SINGLE_STEP): Checkpoint after each step for maximum oversight

Examples:
    >>> config = get_batch_config(tier=2)
    >>> config.mode
    <BatchMode.BATCHED: 'batched'>
    >>> config.batch_size
    5

    >>> manager = BatchContinueManager(tier=2)
    >>> manager.start_batch()
    >>> manager.add_operation("Validated config")
    >>> manager.is_batch_complete()
    False
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# Task 1: Batch Configuration
# =============================================================================


class BatchMode(Enum):
    """Batching mode based on tier.

    Attributes:
        AUTO_ALL: Tier 0-1 - no batching, auto-continue all menus
        BATCHED: Tier 2-3 - batch with checkpoints every N steps
        SINGLE_STEP: Tier 4 - checkpoint after each step
    """

    AUTO_ALL = "auto_all"
    BATCHED = "batched"
    SINGLE_STEP = "single_step"


# Batch sizes by tier (-1 = AUTO_ALL mode, no batching)
BATCH_SIZE_BY_TIER: Dict[int, int] = {
    0: -1,  # AUTO_ALL - no limit
    1: -1,  # AUTO_ALL - no limit
    2: 5,   # Batch of 5 operations
    3: 3,   # Batch of 3 operations
    4: 1,   # Single step (checkpoint after each)
}


@dataclass
class BatchConfig:
    """Configuration for batch-continue behavior.

    Attributes:
        tier: Project tier (0-4)
        batch_size: Number of operations per batch (-1 for AUTO_ALL)
        mode: Batching mode (AUTO_ALL, BATCHED, SINGLE_STEP)
    """

    tier: int
    batch_size: int  # -1 for AUTO_ALL
    mode: BatchMode


def get_batch_config(tier: int) -> BatchConfig:
    """Get batch configuration for the given tier.

    Args:
        tier: Project tier (0-4)

    Returns:
        BatchConfig with appropriate batch_size and mode

    Raises:
        ValueError: If tier is not in range 0-4
    """
    if tier < 0 or tier > 4:
        raise ValueError(f"Invalid tier: {tier}. Must be 0-4.")

    batch_size = BATCH_SIZE_BY_TIER[tier]

    # Determine mode based on batch_size
    if batch_size == -1:
        mode = BatchMode.AUTO_ALL
    elif batch_size == 1:
        mode = BatchMode.SINGLE_STEP
    else:
        mode = BatchMode.BATCHED

    return BatchConfig(tier=tier, batch_size=batch_size, mode=mode)


# =============================================================================
# Task 2: BatchContinueManager
# =============================================================================


@dataclass
class BatchState:
    """Current state of a batch operation.

    Attributes:
        operations: List of operation descriptions in this batch
        start_time: When the batch was started
        tier: Project tier for this batch
    """

    operations: List[str]
    start_time: datetime
    tier: int


@dataclass
class BatchSummary:
    """Summary of completed batch.

    Attributes:
        operations: List of operation descriptions
        count: Number of operations in the batch
        duration_seconds: How long the batch took
        tier: Project tier for this batch
    """

    operations: List[str]
    count: int
    duration_seconds: float
    tier: int


class BatchContinueManager:
    """Manages batch-continue operations based on tier.

    This manager tracks batches of operations and determines when
    checkpoints should occur based on the configured tier.

    Attributes:
        _config: BatchConfig for this manager
        _current_batch: Current BatchState or None if no batch active
    """

    def __init__(self, tier: int) -> None:
        """Initialize the manager with the specified tier.

        Args:
            tier: Project tier (0-4)
        """
        self._config = get_batch_config(tier)
        self._current_batch: Optional[BatchState] = None

    def start_batch(self) -> None:
        """Begin tracking a new batch of operations."""
        self._current_batch = BatchState(
            operations=[],
            start_time=datetime.now(),
            tier=self._config.tier,
        )

    def add_operation(self, operation: str) -> None:
        """Add an operation to the current batch.

        Args:
            operation: Description of the operation

        Raises:
            RuntimeError: If no batch has been started
        """
        if self._current_batch is None:
            raise RuntimeError("No batch has been started. Call start_batch() first.")
        self._current_batch.operations.append(operation)

    def is_batch_complete(self) -> bool:
        """Check if batch has reached size limit.

        Returns:
            True if batch has reached the configured batch_size,
            False otherwise. AUTO_ALL mode (batch_size=-1) never completes.

        Raises:
            RuntimeError: If no batch has been started
        """
        if self._current_batch is None:
            raise RuntimeError("No batch has been started. Call start_batch() first.")

        # AUTO_ALL mode never completes (batch_size = -1)
        if self._config.batch_size == -1:
            return False

        return len(self._current_batch.operations) >= self._config.batch_size

    def get_batch_summary(self) -> List[str]:
        """Get descriptions of batched operations.

        Returns:
            List of operation descriptions

        Raises:
            RuntimeError: If no batch has been started
        """
        if self._current_batch is None:
            raise RuntimeError("No batch has been started. Call start_batch() first.")
        return list(self._current_batch.operations)

    def end_batch(self) -> BatchSummary:
        """Complete the batch and return summary.

        Returns:
            BatchSummary with operation details and duration

        Raises:
            RuntimeError: If no batch has been started
        """
        if self._current_batch is None:
            raise RuntimeError("No batch has been started. Call start_batch() first.")

        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - self._current_batch.start_time).total_seconds()

        # Create summary
        summary = BatchSummary(
            operations=list(self._current_batch.operations),
            count=len(self._current_batch.operations),
            duration_seconds=duration,
            tier=self._current_batch.tier,
        )

        # Clear current batch
        self._current_batch = None

        return summary

    def is_auto_all_mode(self) -> bool:
        """Check if running in auto-all mode (Tier 0-1).

        Returns:
            True if mode is AUTO_ALL, False otherwise
        """
        return self._config.mode == BatchMode.AUTO_ALL

    def has_active_batch(self) -> bool:
        """Check if there is an active batch.

        Returns:
            True if a batch is currently active, False otherwise.
        """
        return self._current_batch is not None


# =============================================================================
# Task 3: Auto-All Mode
# =============================================================================


# Constants for continue menu detection
CONTINUE_PATTERNS: List[str] = ["[C]", "Continue", "Proceed", "[c]ontinue"]


def is_continue_menu(menu_text: str, options: List[str]) -> bool:
    """Detect if this is a continue-type menu.

    A continue menu is one where one of the options contains a continue
    pattern like "[C]", "Continue", "Proceed", or "[c]ontinue".

    Args:
        menu_text: The menu prompt text (not used for detection)
        options: List of option strings

    Returns:
        True if any option contains a continue pattern, False otherwise
    """
    if not options:
        return False

    for option in options:
        for pattern in CONTINUE_PATTERNS:
            if pattern in option:
                return True

    return False


class AutoAllTracker:
    """Tracks operations when in auto-all mode for final summary.

    In AUTO_ALL mode (Tier 0-1), we don't checkpoint during execution.
    Instead, we track all auto-continued operations and provide a
    summary at the end.
    """

    def __init__(self) -> None:
        """Initialize the tracker with empty operations list."""
        self._operations: List[str] = []

    def record_auto_continue(self, operation: str) -> None:
        """Record an auto-continued operation.

        Args:
            operation: Description of the auto-continued operation
        """
        self._operations.append(operation)

    def get_summary(self) -> List[str]:
        """Get all auto-continued operations for final summary.

        Returns:
            Copy of the list of operation descriptions
        """
        return list(self._operations)

    def clear(self) -> None:
        """Clear tracked operations."""
        self._operations.clear()


# =============================================================================
# Task 4: Checkpoint Presentation
# =============================================================================


@dataclass
class BatchCheckpoint:
    """Checkpoint presented after batch completes.

    Attributes:
        operations: List of operations completed in this batch
        summary: Short summary text for the checkpoint
        has_details: Whether detailed view is available
        options: Available user options (e.g., ["[C]ontinue", "[R]eview", "[S]top"])
    """

    operations: List[str]
    summary: str
    has_details: bool
    options: List[str]


# Default user options for checkpoints
DEFAULT_CHECKPOINT_OPTIONS: List[str] = ["[C]ontinue", "[R]eview details", "[S]top"]


def format_checkpoint_message(batch_summary: BatchSummary) -> str:
    """Format checkpoint message for display.

    Creates a concise message showing:
    - Number of completed steps
    - List of operations
    - Elapsed time
    - Available user options

    Args:
        batch_summary: The batch summary to format

    Returns:
        Formatted checkpoint message string

    Example output:
        Completed 5 steps:
        - Step 1: Validated configuration
        - Step 2: Processed input
        - Step 3: Generated output
        - Step 4: Updated state
        - Step 5: Saved progress

        Elapsed: 2.3s

        [C]ontinue | [R]eview details | [S]top
    """
    count = batch_summary.count
    step_word = "step" if count == 1 else "steps"

    lines = [f"Completed {count} {step_word}:"]

    for operation in batch_summary.operations:
        lines.append(f"- {operation}")

    lines.append("")
    lines.append(f"Elapsed: {batch_summary.duration_seconds:.1f}s")
    lines.append("")
    lines.append(" | ".join(DEFAULT_CHECKPOINT_OPTIONS))

    return "\n".join(lines)


def format_detail_view(batch_summary: BatchSummary) -> str:
    """Format expanded detail view when user requests [R]eview.

    Provides more detailed information than the checkpoint message,
    including tier and full operation list.

    Args:
        batch_summary: The batch summary to format

    Returns:
        Formatted detail view string
    """
    lines = [
        "=== Batch Details ===",
        f"Tier: {batch_summary.tier}",
        f"Duration: {batch_summary.duration_seconds:.2f}s",
        f"Operations: {batch_summary.count}",
        "",
        "Operations Performed:",
    ]

    for i, operation in enumerate(batch_summary.operations, 1):
        lines.append(f"  {i}. {operation}")

    return "\n".join(lines)


def create_checkpoint(batch_summary: BatchSummary) -> BatchCheckpoint:
    """Create checkpoint object for presentation.

    Converts a BatchSummary into a BatchCheckpoint suitable for
    display to the user.

    Args:
        batch_summary: The batch summary to convert

    Returns:
        BatchCheckpoint object ready for presentation
    """
    count = batch_summary.count
    elapsed = batch_summary.duration_seconds

    summary = f"Completed {count} operations in {elapsed:.1f}s"

    return BatchCheckpoint(
        operations=list(batch_summary.operations),
        summary=summary,
        has_details=len(batch_summary.operations) > 0,
        options=list(DEFAULT_CHECKPOINT_OPTIONS),
    )


# =============================================================================
# Task 5: Context Management
# =============================================================================


@dataclass
class BatchHistoryEntry:
    """Compacted history entry for token efficiency.

    Instead of storing full operation details, this stores a compact summary
    suitable for maintaining context without excessive token usage.

    Attributes:
        batch_id: Unique identifier for this batch
        operation_count: Number of operations in the batch
        summary: Short summary instead of full operations
        tier: Automation tier for this batch
        timestamp: When this entry was created
    """

    batch_id: str
    operation_count: int
    summary: str
    tier: int
    timestamp: datetime


def _extract_keywords(operation: str) -> List[str]:
    """Extract key terms from an operation string.

    Simple heuristic: take significant words, skip common ones.

    Args:
        operation: The operation string to extract from

    Returns:
        List of key terms
    """
    # Common words to skip
    skip_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "for",
        "on",
        "with",
        "is",
        "was",
        "step",
        "operation",
    }

    # Extract words, filter short ones and common ones
    words = []
    for word in operation.lower().split():
        # Remove punctuation and digits
        clean = "".join(c for c in word if c.isalpha())
        if len(clean) >= 3 and clean not in skip_words:
            words.append(clean)

    return words


def compact_batch_history(
    batch_operations: List[str],
    batch_id: str,
    tier: int,
) -> BatchHistoryEntry:
    """Compact batch operations for token-efficient storage.

    Instead of storing the full operation list, creates a compact summary
    that preserves key information while using fewer tokens.

    Args:
        batch_operations: List of operation strings
        batch_id: Unique identifier for this batch
        tier: Automation tier for this batch

    Returns:
        BatchHistoryEntry with compacted summary

    Example:
        Instead of storing:
        - Operation 1: Validated configuration
        - Operation 2: Processed input
        - Operation 3: Generated output

        Store:
        - "Batch of 3: validation, processing, output"
    """
    count = len(batch_operations)

    if count == 0:
        summary = "Batch of 0"
    else:
        # Extract key terms from each operation
        all_keywords: List[str] = []
        for op in batch_operations:
            keywords = _extract_keywords(op)
            # Take at most 2 keywords per operation
            all_keywords.extend(keywords[:2])

        # Deduplicate while preserving order
        seen: set = set()
        unique_keywords: List[str] = []
        for kw in all_keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        # Limit to 5 keywords for compactness
        keywords_str = ", ".join(unique_keywords[:5])
        summary = f"Batch of {count}: {keywords_str}"

    return BatchHistoryEntry(
        batch_id=batch_id,
        operation_count=count,
        summary=summary,
        tier=tier,
        timestamp=datetime.now(),
    )


def calculate_token_savings(
    original: List[str],
    compacted: BatchHistoryEntry,
) -> int:
    """Calculate approximate token savings from compaction.

    Uses a simple character-based estimate since tokens roughly
    correlate with text length.

    Args:
        original: Original list of operation strings
        compacted: Compacted history entry

    Returns:
        Approximate token savings (non-negative)
    """
    if not original:
        return 0

    # Calculate original text length
    original_text = "\n".join(original)
    original_len = len(original_text)

    # Calculate compacted text length (summary only since that's what's stored)
    compacted_len = len(compacted.summary)

    # Return savings, but never negative
    savings = original_len - compacted_len
    return max(0, savings)
