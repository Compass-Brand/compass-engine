"""Tests for Batch-Continue Logic - Story 2b-6.

This module tests the batch-continue functionality that manages operation
batching based on project tiers (0-4) with checkpoints and summaries.

TDD: Tests are written FIRST, before implementation.
"""

import pytest
from datetime import datetime
from typing import List

# Import will fail until implementation exists (TDD Red phase)
from pcmrp_tools.bmad_automation.batch_continue import (
    # Task 1: Batch Configuration
    BatchMode,
    BATCH_SIZE_BY_TIER,
    BatchConfig,
    get_batch_config,
    # Task 2: BatchContinueManager
    BatchState,
    BatchSummary,
    BatchContinueManager,
    # Task 3: Auto-All Mode
    CONTINUE_PATTERNS,
    is_continue_menu,
    AutoAllTracker,
)


# =============================================================================
# Task 1: Batch Configuration Tests
# =============================================================================


class TestBatchModeEnum:
    """Tests for BatchMode enum (Task 1.1)."""

    def test_batch_mode_has_auto_all(self):
        """BatchMode should have AUTO_ALL value."""
        assert BatchMode.AUTO_ALL.value == "auto_all"

    def test_batch_mode_has_batched(self):
        """BatchMode should have BATCHED value."""
        assert BatchMode.BATCHED.value == "batched"

    def test_batch_mode_has_single_step(self):
        """BatchMode should have SINGLE_STEP value."""
        assert BatchMode.SINGLE_STEP.value == "single_step"

    def test_batch_mode_iteration(self):
        """BatchMode should be iterable with exactly 3 members."""
        modes = list(BatchMode)
        assert len(modes) == 3


class TestBatchSizeByTier:
    """Tests for BATCH_SIZE_BY_TIER constant (Task 1.2)."""

    def test_tier_0_batch_size(self):
        """Tier 0 should have batch_size -1 (AUTO_ALL)."""
        assert BATCH_SIZE_BY_TIER[0] == -1

    def test_tier_1_batch_size(self):
        """Tier 1 should have batch_size -1 (AUTO_ALL)."""
        assert BATCH_SIZE_BY_TIER[1] == -1

    def test_tier_2_batch_size(self):
        """Tier 2 should have batch_size 5 (BATCHED)."""
        assert BATCH_SIZE_BY_TIER[2] == 5

    def test_tier_3_batch_size(self):
        """Tier 3 should have batch_size 3 (BATCHED)."""
        assert BATCH_SIZE_BY_TIER[3] == 3

    def test_tier_4_batch_size(self):
        """Tier 4 should have batch_size 1 (SINGLE_STEP)."""
        assert BATCH_SIZE_BY_TIER[4] == 1

    def test_all_tiers_present(self):
        """All tiers 0-4 should be present in BATCH_SIZE_BY_TIER."""
        for tier in range(5):
            assert tier in BATCH_SIZE_BY_TIER


class TestBatchConfigDataclass:
    """Tests for BatchConfig dataclass (Task 1.3)."""

    def test_batch_config_creation(self):
        """BatchConfig should be creatable with required fields."""
        config = BatchConfig(tier=2, batch_size=5, mode=BatchMode.BATCHED)
        assert config.tier == 2
        assert config.batch_size == 5
        assert config.mode == BatchMode.BATCHED

    def test_batch_config_auto_all_mode(self):
        """BatchConfig should support AUTO_ALL mode."""
        config = BatchConfig(tier=0, batch_size=-1, mode=BatchMode.AUTO_ALL)
        assert config.batch_size == -1
        assert config.mode == BatchMode.AUTO_ALL

    def test_batch_config_single_step_mode(self):
        """BatchConfig should support SINGLE_STEP mode."""
        config = BatchConfig(tier=4, batch_size=1, mode=BatchMode.SINGLE_STEP)
        assert config.batch_size == 1
        assert config.mode == BatchMode.SINGLE_STEP

    def test_batch_config_is_dataclass(self):
        """BatchConfig should be a dataclass."""
        from dataclasses import is_dataclass
        assert is_dataclass(BatchConfig)


class TestGetBatchConfig:
    """Tests for get_batch_config function (Task 1.4)."""

    def test_get_batch_config_tier_0(self):
        """get_batch_config(0) should return AUTO_ALL mode."""
        config = get_batch_config(0)
        assert config.tier == 0
        assert config.batch_size == -1
        assert config.mode == BatchMode.AUTO_ALL

    def test_get_batch_config_tier_1(self):
        """get_batch_config(1) should return AUTO_ALL mode."""
        config = get_batch_config(1)
        assert config.tier == 1
        assert config.batch_size == -1
        assert config.mode == BatchMode.AUTO_ALL

    def test_get_batch_config_tier_2(self):
        """get_batch_config(2) should return BATCHED mode with size 5."""
        config = get_batch_config(2)
        assert config.tier == 2
        assert config.batch_size == 5
        assert config.mode == BatchMode.BATCHED

    def test_get_batch_config_tier_3(self):
        """get_batch_config(3) should return BATCHED mode with size 3."""
        config = get_batch_config(3)
        assert config.tier == 3
        assert config.batch_size == 3
        assert config.mode == BatchMode.BATCHED

    def test_get_batch_config_tier_4(self):
        """get_batch_config(4) should return SINGLE_STEP mode with size 1."""
        config = get_batch_config(4)
        assert config.tier == 4
        assert config.batch_size == 1
        assert config.mode == BatchMode.SINGLE_STEP

    def test_get_batch_config_invalid_tier_negative(self):
        """get_batch_config should raise ValueError for negative tier."""
        with pytest.raises(ValueError, match="Invalid tier.*Must be 0-4"):
            get_batch_config(-1)

    def test_get_batch_config_invalid_tier_high(self):
        """get_batch_config should raise ValueError for tier > 4."""
        with pytest.raises(ValueError, match="Invalid tier.*Must be 0-4"):
            get_batch_config(5)


# =============================================================================
# Task 2: BatchContinueManager Tests
# =============================================================================


class TestBatchStateDataclass:
    """Tests for BatchState dataclass (Task 2.1)."""

    def test_batch_state_creation(self):
        """BatchState should be creatable with required fields."""
        now = datetime.now()
        state = BatchState(operations=["op1", "op2"], start_time=now, tier=2)
        assert state.operations == ["op1", "op2"]
        assert state.start_time == now
        assert state.tier == 2

    def test_batch_state_empty_operations(self):
        """BatchState should support empty operations list."""
        now = datetime.now()
        state = BatchState(operations=[], start_time=now, tier=0)
        assert state.operations == []

    def test_batch_state_is_dataclass(self):
        """BatchState should be a dataclass."""
        from dataclasses import is_dataclass
        assert is_dataclass(BatchState)


class TestBatchSummaryDataclass:
    """Tests for BatchSummary dataclass (Task 2.2)."""

    def test_batch_summary_creation(self):
        """BatchSummary should be creatable with required fields."""
        summary = BatchSummary(
            operations=["op1", "op2", "op3"],
            count=3,
            duration_seconds=10.5,
            tier=2
        )
        assert summary.operations == ["op1", "op2", "op3"]
        assert summary.count == 3
        assert summary.duration_seconds == 10.5
        assert summary.tier == 2

    def test_batch_summary_empty(self):
        """BatchSummary should support empty operations."""
        summary = BatchSummary(operations=[], count=0, duration_seconds=0.0, tier=1)
        assert summary.count == 0

    def test_batch_summary_is_dataclass(self):
        """BatchSummary should be a dataclass."""
        from dataclasses import is_dataclass
        assert is_dataclass(BatchSummary)


class TestBatchContinueManagerInit:
    """Tests for BatchContinueManager initialization (Task 2.3)."""

    def test_manager_creation_tier_0(self):
        """Manager should be creatable with tier 0."""
        manager = BatchContinueManager(tier=0)
        assert manager._config.tier == 0
        assert manager._config.mode == BatchMode.AUTO_ALL

    def test_manager_creation_tier_2(self):
        """Manager should be creatable with tier 2."""
        manager = BatchContinueManager(tier=2)
        assert manager._config.tier == 2
        assert manager._config.mode == BatchMode.BATCHED

    def test_manager_creation_tier_4(self):
        """Manager should be creatable with tier 4."""
        manager = BatchContinueManager(tier=4)
        assert manager._config.tier == 4
        assert manager._config.mode == BatchMode.SINGLE_STEP

    def test_manager_no_current_batch_initially(self):
        """Manager should have no current batch on creation."""
        manager = BatchContinueManager(tier=2)
        assert manager._current_batch is None

    def test_manager_is_auto_all_mode_tier_0(self):
        """is_auto_all_mode should return True for tier 0."""
        manager = BatchContinueManager(tier=0)
        assert manager.is_auto_all_mode() is True

    def test_manager_is_auto_all_mode_tier_1(self):
        """is_auto_all_mode should return True for tier 1."""
        manager = BatchContinueManager(tier=1)
        assert manager.is_auto_all_mode() is True

    def test_manager_is_auto_all_mode_tier_2(self):
        """is_auto_all_mode should return False for tier 2."""
        manager = BatchContinueManager(tier=2)
        assert manager.is_auto_all_mode() is False

    def test_manager_is_auto_all_mode_tier_4(self):
        """is_auto_all_mode should return False for tier 4."""
        manager = BatchContinueManager(tier=4)
        assert manager.is_auto_all_mode() is False


class TestBatchContinueManagerHasActiveBatch:
    """Tests for BatchContinueManager.has_active_batch (Issue #4 fix)."""

    def test_has_active_batch_false_initially(self):
        """has_active_batch should return False when no batch started."""
        manager = BatchContinueManager(tier=2)
        assert manager.has_active_batch() is False

    def test_has_active_batch_true_after_start(self):
        """has_active_batch should return True after start_batch."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        assert manager.has_active_batch() is True

    def test_has_active_batch_false_after_end(self):
        """has_active_batch should return False after end_batch."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        manager.add_operation("Test")
        manager.end_batch()
        assert manager.has_active_batch() is False


class TestBatchContinueManagerStartBatch:
    """Tests for BatchContinueManager.start_batch (Task 2.4)."""

    def test_start_batch_creates_state(self):
        """start_batch should create a new BatchState."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        assert manager._current_batch is not None
        assert isinstance(manager._current_batch, BatchState)

    def test_start_batch_called_twice_resets_batch(self):
        """start_batch called twice should reset the batch (Issue #8 fix).

        This tests the behavior when start_batch is called while there
        is already an active batch without calling end_batch first.
        The existing batch is replaced with a fresh empty batch.
        """
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        manager.add_operation("Operation 1")
        manager.add_operation("Operation 2")
        assert len(manager._current_batch.operations) == 2

        # Call start_batch again without end_batch
        manager.start_batch()

        # The batch should be reset to empty
        assert manager._current_batch is not None
        assert manager._current_batch.operations == []

    def test_start_batch_empty_operations(self):
        """start_batch should create state with empty operations list."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        assert manager._current_batch.operations == []

    def test_start_batch_sets_start_time(self):
        """start_batch should set start_time to now."""
        before = datetime.now()
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        after = datetime.now()
        assert before <= manager._current_batch.start_time <= after

    def test_start_batch_sets_tier(self):
        """start_batch should set correct tier."""
        manager = BatchContinueManager(tier=3)
        manager.start_batch()
        assert manager._current_batch.tier == 3


class TestBatchContinueManagerAddOperation:
    """Tests for BatchContinueManager.add_operation (Task 2.5)."""

    def test_add_operation_after_start(self):
        """add_operation should add to current batch."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        manager.add_operation("Validated file structure")
        assert "Validated file structure" in manager._current_batch.operations

    def test_add_multiple_operations(self):
        """add_operation should accumulate operations."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        manager.add_operation("Op 1")
        manager.add_operation("Op 2")
        manager.add_operation("Op 3")
        assert len(manager._current_batch.operations) == 3

    def test_add_operation_without_start_raises(self):
        """add_operation without start_batch should raise RuntimeError."""
        manager = BatchContinueManager(tier=2)
        with pytest.raises(RuntimeError, match="batch.*started|no.*batch"):
            manager.add_operation("Test operation")


class TestBatchContinueManagerIsBatchComplete:
    """Tests for BatchContinueManager.is_batch_complete (Task 2.6)."""

    def test_is_batch_complete_tier_2_not_complete(self):
        """Tier 2 batch with 3 ops should not be complete (size 5)."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        for i in range(3):
            manager.add_operation(f"Op {i}")
        assert manager.is_batch_complete() is False

    def test_is_batch_complete_tier_2_complete(self):
        """Tier 2 batch with 5 ops should be complete (size 5)."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        for i in range(5):
            manager.add_operation(f"Op {i}")
        assert manager.is_batch_complete() is True

    def test_is_batch_complete_tier_3_at_limit(self):
        """Tier 3 batch with 3 ops should be complete (size 3)."""
        manager = BatchContinueManager(tier=3)
        manager.start_batch()
        for i in range(3):
            manager.add_operation(f"Op {i}")
        assert manager.is_batch_complete() is True

    def test_is_batch_complete_tier_4_single_step(self):
        """Tier 4 batch with 1 op should be complete (size 1)."""
        manager = BatchContinueManager(tier=4)
        manager.start_batch()
        manager.add_operation("Single step")
        assert manager.is_batch_complete() is True

    def test_is_batch_complete_tier_0_never_complete(self):
        """Tier 0 (AUTO_ALL) batch should never be complete (size -1)."""
        manager = BatchContinueManager(tier=0)
        manager.start_batch()
        for i in range(100):
            manager.add_operation(f"Op {i}")
        assert manager.is_batch_complete() is False

    def test_is_batch_complete_tier_1_never_complete(self):
        """Tier 1 (AUTO_ALL) batch should never be complete (size -1)."""
        manager = BatchContinueManager(tier=1)
        manager.start_batch()
        for i in range(50):
            manager.add_operation(f"Op {i}")
        assert manager.is_batch_complete() is False

    def test_is_batch_complete_without_start_raises(self):
        """is_batch_complete without start_batch should raise RuntimeError."""
        manager = BatchContinueManager(tier=2)
        with pytest.raises(RuntimeError, match="batch.*started|no.*batch"):
            manager.is_batch_complete()


class TestBatchContinueManagerGetBatchSummary:
    """Tests for BatchContinueManager.get_batch_summary (Task 2.7)."""

    def test_get_batch_summary_returns_operations(self):
        """get_batch_summary should return list of operation descriptions."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        manager.add_operation("Validated config")
        manager.add_operation("Checked MCP")
        result = manager.get_batch_summary()
        assert result == ["Validated config", "Checked MCP"]

    def test_get_batch_summary_empty_batch(self):
        """get_batch_summary should return empty list for empty batch."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        result = manager.get_batch_summary()
        assert result == []

    def test_get_batch_summary_without_start_raises(self):
        """get_batch_summary without start_batch should raise RuntimeError."""
        manager = BatchContinueManager(tier=2)
        with pytest.raises(RuntimeError, match="batch.*started|no.*batch"):
            manager.get_batch_summary()


class TestBatchContinueManagerEndBatch:
    """Tests for BatchContinueManager.end_batch (Task 2.8)."""

    def test_end_batch_returns_summary(self):
        """end_batch should return BatchSummary."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        manager.add_operation("Op 1")
        manager.add_operation("Op 2")
        result = manager.end_batch()
        assert isinstance(result, BatchSummary)

    def test_end_batch_correct_count(self):
        """end_batch summary should have correct operation count."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        manager.add_operation("Op 1")
        manager.add_operation("Op 2")
        manager.add_operation("Op 3")
        result = manager.end_batch()
        assert result.count == 3

    def test_end_batch_correct_operations(self):
        """end_batch summary should have correct operations list."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        manager.add_operation("Alpha")
        manager.add_operation("Beta")
        result = manager.end_batch()
        assert result.operations == ["Alpha", "Beta"]

    def test_end_batch_correct_tier(self):
        """end_batch summary should have correct tier."""
        manager = BatchContinueManager(tier=3)
        manager.start_batch()
        manager.add_operation("Test")
        result = manager.end_batch()
        assert result.tier == 3

    def test_end_batch_calculates_duration(self):
        """end_batch summary should calculate duration_seconds."""
        import time
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        time.sleep(0.01)  # Small delay
        manager.add_operation("Test")
        result = manager.end_batch()
        assert result.duration_seconds >= 0.01

    def test_end_batch_clears_current_batch(self):
        """end_batch should clear current batch."""
        manager = BatchContinueManager(tier=2)
        manager.start_batch()
        manager.add_operation("Test")
        manager.end_batch()
        assert manager._current_batch is None

    def test_end_batch_without_start_raises(self):
        """end_batch without start_batch should raise RuntimeError."""
        manager = BatchContinueManager(tier=2)
        with pytest.raises(RuntimeError, match="batch.*started|no.*batch"):
            manager.end_batch()


class TestBatchContinueManagerLifecycle:
    """Integration tests for batch lifecycle (Task 2.9)."""

    def test_full_batch_lifecycle_tier_2(self):
        """Full lifecycle: start -> add x5 -> complete -> end."""
        manager = BatchContinueManager(tier=2)

        # Start
        manager.start_batch()
        assert manager._current_batch is not None

        # Add operations until complete
        for i in range(5):
            manager.add_operation(f"Operation {i + 1}")
            if i < 4:
                assert manager.is_batch_complete() is False

        # Should be complete now
        assert manager.is_batch_complete() is True

        # End and get summary
        summary = manager.end_batch()
        assert summary.count == 5
        assert manager._current_batch is None

    def test_multiple_batch_cycles(self):
        """Manager should support multiple batch cycles."""
        manager = BatchContinueManager(tier=3)

        # First batch
        manager.start_batch()
        for i in range(3):
            manager.add_operation(f"Batch 1 Op {i}")
        summary1 = manager.end_batch()
        assert summary1.count == 3

        # Second batch
        manager.start_batch()
        for i in range(3):
            manager.add_operation(f"Batch 2 Op {i}")
        summary2 = manager.end_batch()
        assert summary2.count == 3

        # Summaries should be independent
        assert "Batch 1" in summary1.operations[0]
        assert "Batch 2" in summary2.operations[0]


# =============================================================================
# Task 3: Auto-All Mode Tests
# =============================================================================


class TestContinuePatterns:
    """Tests for CONTINUE_PATTERNS constant (Task 3.1)."""

    def test_continue_patterns_contains_c_bracket(self):
        """CONTINUE_PATTERNS should contain [C]."""
        assert "[C]" in CONTINUE_PATTERNS

    def test_continue_patterns_contains_continue(self):
        """CONTINUE_PATTERNS should contain Continue."""
        assert "Continue" in CONTINUE_PATTERNS

    def test_continue_patterns_contains_proceed(self):
        """CONTINUE_PATTERNS should contain Proceed."""
        assert "Proceed" in CONTINUE_PATTERNS

    def test_continue_patterns_contains_lowercase_continue(self):
        """CONTINUE_PATTERNS should contain [c]ontinue."""
        assert "[c]ontinue" in CONTINUE_PATTERNS

    def test_continue_patterns_is_list(self):
        """CONTINUE_PATTERNS should be a list."""
        assert isinstance(CONTINUE_PATTERNS, list)


class TestIsContinueMenu:
    """Tests for is_continue_menu function (Task 3.2)."""

    def test_is_continue_menu_with_c_bracket(self):
        """Menu with [C] option should be detected as continue menu."""
        menu_text = "Ready to proceed?"
        options = ["[C] Continue", "[S] Stop"]
        assert is_continue_menu(menu_text, options) is True

    def test_is_continue_menu_with_continue_word(self):
        """Menu with 'Continue' option should be detected."""
        menu_text = "What would you like to do?"
        options = ["Continue", "Stop", "Restart"]
        assert is_continue_menu(menu_text, options) is True

    def test_is_continue_menu_with_proceed(self):
        """Menu with 'Proceed' option should be detected."""
        menu_text = "Validation complete."
        options = ["Proceed", "Cancel"]
        assert is_continue_menu(menu_text, options) is True

    def test_is_continue_menu_with_lowercase(self):
        """Menu with [c]ontinue should be detected."""
        menu_text = "Continue with workflow?"
        options = ["[c]ontinue", "[a]bort"]
        assert is_continue_menu(menu_text, options) is True

    def test_is_continue_menu_no_match(self):
        """Menu without continue patterns should not be detected."""
        menu_text = "Select an agent"
        options = ["[A] Analyst", "[B] Builder", "[D] Developer"]
        assert is_continue_menu(menu_text, options) is False

    def test_is_continue_menu_empty_options(self):
        """Empty options list should not be detected as continue menu."""
        menu_text = "Some text"
        options: List[str] = []
        assert is_continue_menu(menu_text, options) is False

    def test_is_continue_menu_case_sensitivity(self):
        """Continue detection should be case-sensitive for pattern match."""
        menu_text = "Continue?"
        options = ["CONTINUE", "STOP"]
        # "CONTINUE" doesn't match "Continue" exactly
        assert is_continue_menu(menu_text, options) is False

    def test_is_continue_menu_partial_match(self):
        """Options containing pattern substring should match."""
        menu_text = "Proceed with next step?"
        options = ["Yes, Continue validation", "No, stop"]
        assert is_continue_menu(menu_text, options) is True


class TestAutoAllTracker:
    """Tests for AutoAllTracker class (Task 3.3)."""

    def test_auto_all_tracker_creation(self):
        """AutoAllTracker should be creatable."""
        tracker = AutoAllTracker()
        assert tracker is not None

    def test_auto_all_tracker_empty_initially(self):
        """AutoAllTracker should start with empty operations."""
        tracker = AutoAllTracker()
        assert tracker.get_summary() == []

    def test_record_auto_continue_single(self):
        """record_auto_continue should track a single operation."""
        tracker = AutoAllTracker()
        tracker.record_auto_continue("Auto-continued step 1")
        summary = tracker.get_summary()
        assert "Auto-continued step 1" in summary

    def test_record_auto_continue_multiple(self):
        """record_auto_continue should track multiple operations."""
        tracker = AutoAllTracker()
        tracker.record_auto_continue("Step 1")
        tracker.record_auto_continue("Step 2")
        tracker.record_auto_continue("Step 3")
        summary = tracker.get_summary()
        assert len(summary) == 3

    def test_get_summary_preserves_order(self):
        """get_summary should preserve insertion order."""
        tracker = AutoAllTracker()
        tracker.record_auto_continue("First")
        tracker.record_auto_continue("Second")
        tracker.record_auto_continue("Third")
        summary = tracker.get_summary()
        assert summary == ["First", "Second", "Third"]

    def test_clear_resets_tracker(self):
        """clear should remove all tracked operations."""
        tracker = AutoAllTracker()
        tracker.record_auto_continue("Op 1")
        tracker.record_auto_continue("Op 2")
        tracker.clear()
        assert tracker.get_summary() == []

    def test_get_summary_returns_copy(self):
        """get_summary should return a copy, not the internal list."""
        tracker = AutoAllTracker()
        tracker.record_auto_continue("Original")
        summary = tracker.get_summary()
        summary.append("Modified")
        # Internal list should be unchanged
        assert tracker.get_summary() == ["Original"]


class TestAutoAllTrackerIntegration:
    """Integration tests for AutoAllTracker with BatchContinueManager."""

    def test_auto_all_mode_uses_tracker_pattern(self):
        """Tier 0/1 managers should work with AutoAllTracker pattern."""
        manager = BatchContinueManager(tier=0)
        tracker = AutoAllTracker()

        # When in AUTO_ALL mode, we use tracker instead of batch
        assert manager.is_auto_all_mode() is True

        # Record operations to tracker
        tracker.record_auto_continue("Auto step 1")
        tracker.record_auto_continue("Auto step 2")

        # At end, get full summary
        summary = tracker.get_summary()
        assert len(summary) == 2

    def test_batched_mode_does_not_use_tracker(self):
        """Tier 2+ managers should use batches, not tracker."""
        manager = BatchContinueManager(tier=2)

        # In BATCHED mode, we use batch operations
        assert manager.is_auto_all_mode() is False

        manager.start_batch()
        manager.add_operation("Batched step 1")
        assert manager.is_batch_complete() is False


# =============================================================================
# Task 4: Checkpoint Presentation Tests
# =============================================================================


class TestBatchCheckpointDataclass:
    """Tests for BatchCheckpoint dataclass (Task 4.1)."""

    def test_batch_checkpoint_creation(self):
        """BatchCheckpoint should be creatable with required fields."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint

        checkpoint = BatchCheckpoint(
            operations=["Op 1", "Op 2"],
            summary="Completed 2 operations",
            has_details=True,
            options=["[C]ontinue", "[R]eview", "[S]top"],
        )
        assert checkpoint.operations == ["Op 1", "Op 2"]
        assert checkpoint.summary == "Completed 2 operations"
        assert checkpoint.has_details is True
        assert len(checkpoint.options) == 3

    def test_batch_checkpoint_stores_operations(self):
        """BatchCheckpoint should store list of operations."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint

        checkpoint = BatchCheckpoint(
            operations=["Step 1: Validated config", "Step 2: Processed input"],
            summary="Completed 2 steps",
            has_details=True,
            options=["[C]ontinue"],
        )
        assert checkpoint.operations == [
            "Step 1: Validated config",
            "Step 2: Processed input",
        ]

    def test_batch_checkpoint_stores_summary(self):
        """BatchCheckpoint should store summary text."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint

        checkpoint = BatchCheckpoint(
            operations=["Op 1"],
            summary="Completed 1 step in 0.5s",
            has_details=False,
            options=["[C]ontinue"],
        )
        assert checkpoint.summary == "Completed 1 step in 0.5s"

    def test_batch_checkpoint_stores_options(self):
        """BatchCheckpoint should store available user options."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint

        checkpoint = BatchCheckpoint(
            operations=[],
            summary="Done",
            has_details=False,
            options=["[C]ontinue", "[R]eview details", "[S]top"],
        )
        assert "[C]ontinue" in checkpoint.options
        assert "[R]eview details" in checkpoint.options
        assert "[S]top" in checkpoint.options

    def test_batch_checkpoint_is_dataclass(self):
        """BatchCheckpoint should be a dataclass."""
        from dataclasses import is_dataclass
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint

        assert is_dataclass(BatchCheckpoint)


class TestFormatCheckpointMessage:
    """Tests for format_checkpoint_message function (Task 4.2)."""

    def test_formats_single_operation(self):
        """Should format checkpoint for single operation."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            format_checkpoint_message,
        )

        summary = BatchSummary(
            operations=["Validated configuration"],
            count=1,
            duration_seconds=1.0,
            tier=2,
        )
        message = format_checkpoint_message(summary)

        assert "Completed 1 step" in message
        assert "Validated configuration" in message

    def test_formats_multiple_operations(self):
        """Should format checkpoint for multiple operations."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            format_checkpoint_message,
        )

        summary = BatchSummary(
            operations=[
                "Step 1: Validated configuration",
                "Step 2: Processed input",
                "Step 3: Generated output",
            ],
            count=3,
            duration_seconds=2.0,
            tier=2,
        )
        message = format_checkpoint_message(summary)

        assert "Completed 3 steps" in message
        assert "Step 1" in message
        assert "Step 2" in message
        assert "Step 3" in message

    def test_includes_elapsed_time(self):
        """Should include elapsed time in message."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            format_checkpoint_message,
        )

        summary = BatchSummary(
            operations=["Op 1", "Op 2"],
            count=2,
            duration_seconds=2.3,
            tier=2,
        )
        message = format_checkpoint_message(summary)

        assert "Elapsed:" in message or "elapsed:" in message.lower()
        assert "2.3s" in message

    def test_includes_user_options(self):
        """Should include user options at the end."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            format_checkpoint_message,
        )

        summary = BatchSummary(
            operations=["Op 1"],
            count=1,
            duration_seconds=1.0,
            tier=2,
        )
        message = format_checkpoint_message(summary)

        assert "[C]ontinue" in message
        assert "[R]eview" in message
        assert "[S]top" in message

    def test_formats_five_operations(self):
        """Should format example from task description correctly."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            format_checkpoint_message,
        )

        summary = BatchSummary(
            operations=[
                "Step 1: Validated configuration",
                "Step 2: Processed input",
                "Step 3: Generated output",
                "Step 4: Updated state",
                "Step 5: Saved progress",
            ],
            count=5,
            duration_seconds=2.3,
            tier=2,
        )
        message = format_checkpoint_message(summary)

        assert "Completed 5 steps" in message
        assert "2.3s" in message
        # All steps should be listed
        for i in range(1, 6):
            assert f"Step {i}" in message


class TestFormatDetailView:
    """Tests for format_detail_view function (Task 4.3)."""

    def test_includes_tier_information(self):
        """Detail view should include tier information."""
        from pcmrp_tools.bmad_automation.batch_continue import format_detail_view

        summary = BatchSummary(
            operations=["Op 1"],
            count=1,
            duration_seconds=1.0,
            tier=3,
        )
        detail = format_detail_view(summary)

        assert "tier" in detail.lower() or "Tier" in detail
        assert "3" in detail

    def test_includes_duration(self):
        """Detail view should include duration."""
        from pcmrp_tools.bmad_automation.batch_continue import format_detail_view

        summary = BatchSummary(
            operations=["Op 1"],
            count=1,
            duration_seconds=5.25,
            tier=2,
        )
        detail = format_detail_view(summary)

        assert "5.25" in detail or "Duration" in detail

    def test_lists_all_operations(self):
        """Detail view should list all operations with details."""
        from pcmrp_tools.bmad_automation.batch_continue import format_detail_view

        summary = BatchSummary(
            operations=[
                "Validated configuration",
                "Processed input file",
                "Generated output report",
            ],
            count=3,
            duration_seconds=3.0,
            tier=2,
        )
        detail = format_detail_view(summary)

        assert "Validated configuration" in detail
        assert "Processed input file" in detail
        assert "Generated output report" in detail


class TestCreateCheckpoint:
    """Tests for create_checkpoint function (Task 4.4)."""

    def test_creates_checkpoint_from_summary(self):
        """Should create BatchCheckpoint from BatchSummary."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            BatchCheckpoint,
            create_checkpoint,
        )

        summary = BatchSummary(
            operations=["Op 1", "Op 2"],
            count=2,
            duration_seconds=2.0,
            tier=2,
        )
        checkpoint = create_checkpoint(summary)

        assert isinstance(checkpoint, BatchCheckpoint)
        assert checkpoint.operations == ["Op 1", "Op 2"]
        assert "[C]ontinue" in checkpoint.options

    def test_checkpoint_has_details_when_operations_exist(self):
        """Checkpoint has_details should be True when operations present."""
        from pcmrp_tools.bmad_automation.batch_continue import create_checkpoint

        summary = BatchSummary(
            operations=["Op 1"],
            count=1,
            duration_seconds=1.0,
            tier=2,
        )
        checkpoint = create_checkpoint(summary)

        assert checkpoint.has_details is True

    def test_checkpoint_summary_includes_count_and_time(self):
        """Checkpoint summary should include operation count and elapsed time."""
        from pcmrp_tools.bmad_automation.batch_continue import create_checkpoint

        summary = BatchSummary(
            operations=["Op 1", "Op 2", "Op 3"],
            count=3,
            duration_seconds=5.0,
            tier=2,
        )
        checkpoint = create_checkpoint(summary)

        assert "3" in checkpoint.summary
        assert "5" in checkpoint.summary or "5.0" in checkpoint.summary


# =============================================================================
# Task 5: Context Management Tests
# =============================================================================


class TestBatchHistoryEntry:
    """Tests for BatchHistoryEntry dataclass (Task 5.1)."""

    def test_history_entry_creation(self):
        """BatchHistoryEntry should store compacted batch info."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchHistoryEntry

        entry = BatchHistoryEntry(
            batch_id="batch-001",
            operation_count=5,
            summary="Batch of 5: config, processing, output, state, save",
            tier=2,
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
        )

        assert entry.batch_id == "batch-001"
        assert entry.operation_count == 5
        assert "config" in entry.summary
        assert entry.tier == 2

    def test_history_entry_timestamp(self):
        """BatchHistoryEntry should store timestamp."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchHistoryEntry

        ts = datetime(2024, 6, 15, 14, 30, 0)
        entry = BatchHistoryEntry(
            batch_id="batch-002",
            operation_count=3,
            summary="Batch of 3",
            tier=1,
            timestamp=ts,
        )

        assert entry.timestamp == ts

    def test_history_entry_is_dataclass(self):
        """BatchHistoryEntry should be a dataclass."""
        from dataclasses import is_dataclass
        from pcmrp_tools.bmad_automation.batch_continue import BatchHistoryEntry

        assert is_dataclass(BatchHistoryEntry)


class TestCompactBatchHistory:
    """Tests for compact_batch_history function (Task 5.2)."""

    def test_compacts_single_operation(self):
        """Should compact single operation to history entry."""
        from pcmrp_tools.bmad_automation.batch_continue import compact_batch_history

        operations = ["Validated configuration"]
        entry = compact_batch_history(operations, batch_id="batch-001", tier=2)

        assert entry.operation_count == 1
        assert "1" in entry.summary

    def test_compacts_multiple_operations(self):
        """Should compact multiple operations to short summary."""
        from pcmrp_tools.bmad_automation.batch_continue import compact_batch_history

        operations = [
            "Operation 1: Validated configuration",
            "Operation 2: Processed input",
            "Operation 3: Generated output",
        ]
        entry = compact_batch_history(operations, batch_id="batch-002", tier=2)

        assert entry.operation_count == 3
        # Summary should be shorter than full operations
        total_orig = sum(len(op) for op in operations)
        assert len(entry.summary) < total_orig

    def test_compact_summary_mentions_key_terms(self):
        """Compacted summary should mention key terms from operations."""
        from pcmrp_tools.bmad_automation.batch_continue import compact_batch_history

        operations = [
            "Validated configuration",
            "Processed input",
            "Generated output",
        ]
        entry = compact_batch_history(operations, batch_id="batch-003", tier=2)

        # Should contain keywords from operations
        summary_lower = entry.summary.lower()
        assert "config" in summary_lower or "valid" in summary_lower
        assert "input" in summary_lower or "process" in summary_lower
        assert "output" in summary_lower or "generat" in summary_lower

    def test_compact_preserves_batch_id(self):
        """Compacted entry should preserve batch ID."""
        from pcmrp_tools.bmad_automation.batch_continue import compact_batch_history

        entry = compact_batch_history(
            ["Op 1"], batch_id="my-special-batch-id", tier=2
        )

        assert entry.batch_id == "my-special-batch-id"

    def test_compact_preserves_tier(self):
        """Compacted entry should preserve tier."""
        from pcmrp_tools.bmad_automation.batch_continue import compact_batch_history

        entry = compact_batch_history(["Op 1"], batch_id="batch-001", tier=3)

        assert entry.tier == 3

    def test_compact_sets_timestamp(self):
        """Compacted entry should have a timestamp."""
        from pcmrp_tools.bmad_automation.batch_continue import compact_batch_history

        before = datetime.now()
        entry = compact_batch_history(["Op 1"], batch_id="batch-001", tier=2)
        after = datetime.now()

        assert before <= entry.timestamp <= after

    def test_compact_empty_operations(self):
        """Compacting empty operations should work."""
        from pcmrp_tools.bmad_automation.batch_continue import compact_batch_history

        entry = compact_batch_history([], batch_id="batch-empty", tier=1)

        assert entry.operation_count == 0
        assert "0" in entry.summary


class TestCalculateTokenSavings:
    """Tests for calculate_token_savings function (Task 5.3)."""

    def test_calculates_positive_savings(self):
        """Should calculate positive savings when compacted is smaller."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            BatchHistoryEntry,
            calculate_token_savings,
        )

        original = [
            "Operation 1: Validated configuration thoroughly",
            "Operation 2: Processed input data from multiple sources",
            "Operation 3: Generated comprehensive output report",
        ]

        compacted = BatchHistoryEntry(
            batch_id="batch-001",
            operation_count=3,
            summary="Batch of 3: validation, processing, output",
            tier=2,
            timestamp=datetime.now(),
        )

        savings = calculate_token_savings(original, compacted)

        assert savings > 0

    def test_savings_proportional_to_reduction(self):
        """Larger reductions should yield larger savings."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            BatchHistoryEntry,
            calculate_token_savings,
        )

        small_original = ["Op 1", "Op 2"]
        large_original = [
            "Very long operation description number one with lots of details",
            "Another extremely verbose operation description here",
            "Yet another lengthy operation explanation text",
            "More detailed operation information stored here",
            "Final verbose operation with extended description",
        ]

        small_compacted = BatchHistoryEntry(
            batch_id="b1",
            operation_count=2,
            summary="Batch of 2",
            tier=2,
            timestamp=datetime.now(),
        )

        large_compacted = BatchHistoryEntry(
            batch_id="b2",
            operation_count=5,
            summary="Batch of 5: varied ops",
            tier=2,
            timestamp=datetime.now(),
        )

        small_savings = calculate_token_savings(small_original, small_compacted)
        large_savings = calculate_token_savings(large_original, large_compacted)

        assert large_savings > small_savings

    def test_savings_are_non_negative(self):
        """Token savings should never be negative (worst case is 0)."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            BatchHistoryEntry,
            calculate_token_savings,
        )

        # Edge case: very short original
        original = ["x"]
        compacted = BatchHistoryEntry(
            batch_id="b",
            operation_count=1,
            summary="Batch of 1: x",
            tier=1,
            timestamp=datetime.now(),
        )

        savings = calculate_token_savings(original, compacted)

        # Even if compacted is larger, we report 0 not negative
        assert savings >= 0

    def test_empty_original_returns_zero(self):
        """Empty original list should return zero savings."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            BatchHistoryEntry,
            calculate_token_savings,
        )

        original: List[str] = []
        compacted = BatchHistoryEntry(
            batch_id="b",
            operation_count=0,
            summary="",
            tier=1,
            timestamp=datetime.now(),
        )

        savings = calculate_token_savings(original, compacted)

        assert savings == 0


# =============================================================================
# Issue #1 Fix: Tier Change Mid-Workflow Tests
# =============================================================================


class TestTierChangeMidWorkflow:
    """Tests for tier change behavior during active batch (Issue #1 fix).

    These tests verify that changing tier during an active batch handles
    state correctly, batch size changes are applied, and state is either
    preserved or cleanly reset.
    """

    def test_set_tier_during_active_batch_resets_manager(self):
        """Changing tier during active batch should reset the batch manager.

        When set_tier is called, a new BatchContinueManager is created,
        which means the old batch state is discarded.
        """
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=2)
        selector._batch_manager.start_batch()
        selector._batch_manager.add_operation("Op 1")
        selector._batch_manager.add_operation("Op 2")

        # Verify we have an active batch
        assert selector._batch_manager.has_active_batch()
        assert len(selector._batch_manager.get_batch_summary()) == 2

        # Change tier
        selector.set_tier(3)

        # Batch manager should be reset - no active batch
        assert not selector._batch_manager.has_active_batch()

    def test_set_tier_updates_batch_size(self):
        """Changing tier should apply new batch size for future batches."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=2)  # batch_size = 5
        assert selector._batch_manager._config.batch_size == 5

        # Change to tier 3 (batch_size = 3)
        selector.set_tier(3)
        assert selector._batch_manager._config.batch_size == 3

        # Start a new batch and verify new size is used
        selector._batch_manager.start_batch()
        for i in range(3):
            selector._batch_manager.add_operation(f"Op {i}")
        assert selector._batch_manager.is_batch_complete()

    def test_tier_change_to_auto_all_mode(self):
        """Changing from batched tier to AUTO_ALL tier should work correctly."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=2)  # BATCHED mode
        assert not selector._batch_manager.is_auto_all_mode()

        # Start a batch and add some operations
        selector._batch_manager.start_batch()
        selector._batch_manager.add_operation("Op 1")

        # Change to tier 0 (AUTO_ALL mode)
        selector.set_tier(0)

        # Should now be in AUTO_ALL mode
        assert selector._batch_manager.is_auto_all_mode()
        # No active batch since manager was reset
        assert not selector._batch_manager.has_active_batch()

    def test_tier_change_preserves_selector_state(self):
        """Tier change should preserve MenuSelector configuration except batch manager."""
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=2)
        original_high_selector = selector.high_selector
        original_medium_selector = selector.medium_selector
        original_logger = selector.logger

        # Change tier
        selector.set_tier(4)

        # Other components should be preserved
        assert selector.high_selector is original_high_selector
        assert selector.medium_selector is original_medium_selector
        assert selector.logger is original_logger
        # But batch manager should be new
        assert selector._tier == 4


# =============================================================================
# Issue #2 Fix: Context Management Integration Tests
# =============================================================================


# =============================================================================
# Issue #10 Fix: Full Batch Flow Per Tier Tests
# =============================================================================


class TestFullBatchFlowPerTier:
    """Tests for full batch flow behavior at each tier (Issue #10 fix).

    These tests verify end-to-end batch behavior for each tier:
    - Tier 0-1: AUTO_ALL mode returns immediately (no batching)
    - Tier 2: Returns checkpoint after 5 continues
    - Tier 3: Returns checkpoint after 3 continues
    - Tier 4: Returns checkpoint after every continue
    """

    def test_tier_0_auto_all_immediate_continue(self):
        """Tier 0 (AUTO_ALL) should return ContinueSelectionResult immediately."""
        from pcmrp_tools.bmad_automation.menu_participation_engine import (
            MenuDetectionResult,
            MenuType,
        )
        from pcmrp_tools.bmad_automation.menu_selection import (
            ContinueSelectionResult,
            MenuSelector,
        )

        selector = MenuSelector(tier=0)
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.APC,
            options=["[C] Continue", "[S] Stop"],
            breakdown={"test": 90},
            raw_input="[C] Continue [S] Stop",
        )

        # First continue
        result1 = selector.select_or_present(detection)
        assert isinstance(result1, ContinueSelectionResult)
        assert result1.auto_continued is True

        # Second continue - still immediate, no checkpoint
        result2 = selector.select_or_present(detection)
        assert isinstance(result2, ContinueSelectionResult)
        assert result2.auto_continued is True

        # Even after 10 continues, still no checkpoint
        for _ in range(10):
            result = selector.select_or_present(detection)
            assert isinstance(result, ContinueSelectionResult)

    def test_tier_1_auto_all_immediate_continue(self):
        """Tier 1 (AUTO_ALL) should return ContinueSelectionResult immediately."""
        from pcmrp_tools.bmad_automation.menu_participation_engine import (
            MenuDetectionResult,
            MenuType,
        )
        from pcmrp_tools.bmad_automation.menu_selection import (
            ContinueSelectionResult,
            MenuSelector,
        )

        selector = MenuSelector(tier=1)
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.APC,
            options=["Continue", "Exit"],
            breakdown={"test": 90},
            raw_input="Continue or Exit?",
        )

        # Multiple continues should all be immediate
        for _ in range(20):
            result = selector.select_or_present(detection)
            assert isinstance(result, ContinueSelectionResult)
            assert result.auto_continued is True

    def test_tier_2_checkpoint_after_5_continues(self):
        """Tier 2 should return BatchCheckpoint after 5 continues."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint
        from pcmrp_tools.bmad_automation.menu_participation_engine import (
            MenuDetectionResult,
            MenuType,
        )
        from pcmrp_tools.bmad_automation.menu_selection import (
            ContinueSelectionResult,
            MenuSelector,
        )

        selector = MenuSelector(tier=2)  # batch_size = 5
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.APC,
            options=["[C] Continue", "[S] Stop"],
            breakdown={"test": 90},
            raw_input="[C] Continue [S] Stop",
        )

        # First 4 continues should return ContinueSelectionResult
        for i in range(4):
            result = selector.select_or_present(detection)
            assert isinstance(result, ContinueSelectionResult), f"Continue {i+1} failed"

        # 5th continue should return BatchCheckpoint
        result = selector.select_or_present(detection)
        assert isinstance(result, BatchCheckpoint), "5th continue should be checkpoint"
        assert len(result.operations) == 5

    def test_tier_3_checkpoint_after_3_continues(self):
        """Tier 3 should return BatchCheckpoint after 3 continues."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint
        from pcmrp_tools.bmad_automation.menu_participation_engine import (
            MenuDetectionResult,
            MenuType,
        )
        from pcmrp_tools.bmad_automation.menu_selection import (
            ContinueSelectionResult,
            MenuSelector,
        )

        selector = MenuSelector(tier=3)  # batch_size = 3
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.APC,
            options=["Proceed", "Cancel"],
            breakdown={"test": 90},
            raw_input="Proceed or Cancel?",
        )

        # First 2 continues should return ContinueSelectionResult
        for i in range(2):
            result = selector.select_or_present(detection)
            assert isinstance(result, ContinueSelectionResult), f"Continue {i+1} failed"

        # 3rd continue should return BatchCheckpoint
        result = selector.select_or_present(detection)
        assert isinstance(result, BatchCheckpoint), "3rd continue should be checkpoint"
        assert len(result.operations) == 3

    def test_tier_4_checkpoint_after_every_continue(self):
        """Tier 4 should return BatchCheckpoint after every continue."""
        from pcmrp_tools.bmad_automation.batch_continue import BatchCheckpoint
        from pcmrp_tools.bmad_automation.menu_participation_engine import (
            MenuDetectionResult,
            MenuType,
        )
        from pcmrp_tools.bmad_automation.menu_selection import MenuSelector

        selector = MenuSelector(tier=4)  # batch_size = 1 (SINGLE_STEP)
        detection = MenuDetectionResult.detected(
            confidence=90,
            menu_type=MenuType.APC,
            options=["[C] Continue", "[S] Stop"],
            breakdown={"test": 90},
            raw_input="[C] Continue [S] Stop",
        )

        # Every continue should return BatchCheckpoint
        for i in range(5):
            result = selector.select_or_present(detection)
            assert isinstance(result, BatchCheckpoint), f"Continue {i+1} should be checkpoint"
            assert len(result.operations) == 1


class TestContextManagementIntegration:
    """Tests for compacted history storage on batch completion (Issue #2 fix).

    Note: compact_batch_history is currently a standalone function in batch_continue.py
    that can be used for token-efficient history storage. This test class verifies that
    the function works correctly when called at batch completion time.

    TODO: Consider integrating compact_batch_history into MenuSelector._handle_continue_with_batching
    to automatically store compacted history when batches complete. Current implementation
    leaves the calling responsibility to the consumer.
    """

    def test_compact_history_on_batch_completion(self):
        """Compacted history should be storable when a batch completes."""
        from pcmrp_tools.bmad_automation.batch_continue import compact_batch_history

        manager = BatchContinueManager(tier=2)
        manager.start_batch()

        # Add 5 operations to complete the batch
        operations_added = [
            "Validated configuration",
            "Processed input",
            "Generated output",
            "Updated state",
            "Saved progress",
        ]
        for op in operations_added:
            manager.add_operation(op)

        assert manager.is_batch_complete()

        # End the batch
        summary = manager.end_batch()

        # Compact the history for storage
        compacted = compact_batch_history(
            summary.operations,
            batch_id=f"batch-{summary.tier}-{int(summary.duration_seconds * 1000)}",
            tier=summary.tier,
        )

        # Verify compaction works correctly
        assert compacted.operation_count == 5
        assert compacted.tier == 2
        assert "5" in compacted.summary
        # Summary should contain keywords from operations
        assert len(compacted.summary) < sum(len(op) for op in operations_added)

    def test_compacted_history_maintains_batch_context(self):
        """Compacted history should maintain enough context to understand batch."""
        from pcmrp_tools.bmad_automation.batch_continue import compact_batch_history

        manager = BatchContinueManager(tier=3)
        manager.start_batch()
        manager.add_operation("Validated MCP configuration")
        manager.add_operation("Checked workflow dependencies")
        manager.add_operation("Ran pre-flight checks")

        summary = manager.end_batch()
        compacted = compact_batch_history(
            summary.operations,
            batch_id="test-batch",
            tier=summary.tier,
        )

        # The compacted summary should contain some key terms
        summary_lower = compacted.summary.lower()
        # Should have batch count
        assert "3" in compacted.summary or "three" in summary_lower
        # Should have some recognizable keywords
        has_keywords = any(
            kw in summary_lower
            for kw in ["mcp", "workflow", "flight", "valid", "config", "check"]
        )
        assert has_keywords


class TestCheckpointAndContextIntegration:
    """Integration tests for checkpoint and context management."""

    def test_manager_to_checkpoint_workflow(self):
        """Full workflow: manager -> batch summary -> checkpoint."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            create_checkpoint,
            format_checkpoint_message,
        )

        manager = BatchContinueManager(tier=2)
        manager.start_batch()

        # Add operations
        manager.add_operation("Validated configuration")
        manager.add_operation("Processed input")
        manager.add_operation("Generated output")

        # End batch and get summary
        summary = manager.end_batch()

        # Create checkpoint from summary
        checkpoint = create_checkpoint(summary)

        assert checkpoint.operations == [
            "Validated configuration",
            "Processed input",
            "Generated output",
        ]
        assert checkpoint.has_details is True
        assert "[C]ontinue" in checkpoint.options

        # Format for display
        message = format_checkpoint_message(summary)
        assert "Completed 3 steps" in message

    def test_summary_to_compact_history(self):
        """Workflow: batch summary -> compact history entry."""
        from pcmrp_tools.bmad_automation.batch_continue import (
            calculate_token_savings,
            compact_batch_history,
        )

        manager = BatchContinueManager(tier=3)
        manager.start_batch()

        operations = [
            "Validated configuration settings",
            "Processed input data files",
            "Generated output reports",
        ]
        for op in operations:
            manager.add_operation(op)

        summary = manager.end_batch()

        # Compact for storage
        entry = compact_batch_history(
            summary.operations, batch_id="batch-123", tier=summary.tier
        )

        assert entry.operation_count == 3
        assert entry.tier == 3

        # Verify savings
        savings = calculate_token_savings(summary.operations, entry)
        assert savings > 0
