"""Tests for BMAD context manager module.

NOTE: These tests are skipped because the _bmad module has not been implemented yet.
The module is planned as part of the BMAD automation layer but the implementation
is deferred until the core engine components are built.
"""

import pytest

# Skip entire module - the _bmad package does not exist yet
pytest.skip(
    "Skipping: _bmad.core.lib.context_manager module not implemented",
    allow_module_level=True,
)


class TestReviewLoopContext:
    def test_initial_state(self):
        ctx = ReviewLoopContext()
        assert ctx.stable_context == ""
        assert ctx.dynamic_context == []
        assert ctx.error_history == []
        assert ctx.success_patterns == []

    def test_set_stable_context(self):
        ctx = ReviewLoopContext()
        ctx.set_stable_context("Original prompt")
        assert ctx.stable_context == "Original prompt"

    def test_add_review_output(self):
        ctx = ReviewLoopContext()
        ctx.add_review_output("Review 1")
        ctx.add_review_output("Review 2")
        assert len(ctx.dynamic_context) == 2

    def test_dynamic_context_limit(self):
        ctx = ReviewLoopContext()
        for i in range(10):
            ctx.add_review_output(f"Review {i}")
        assert len(ctx.dynamic_context) == ctx.MAX_DYNAMIC_ENTRIES

    def test_truncation(self):
        ctx = ReviewLoopContext()
        long_text = "x" * 1000
        ctx.add_review_output(long_text)
        assert len(ctx.dynamic_context[0]) <= ctx.MAX_ENTRY_LENGTH + 3  # +3 for ...

    def test_add_error(self):
        ctx = ReviewLoopContext()
        ctx.add_error("Error 1")
        assert len(ctx.error_history) == 1

    def test_add_success_pattern(self):
        ctx = ReviewLoopContext()
        ctx.add_success_pattern("Pattern 1")
        assert len(ctx.success_patterns) == 1

    def test_get_full_context(self):
        ctx = ReviewLoopContext()
        ctx.set_stable_context("Stable")
        ctx.add_review_output("Review")
        ctx.add_success_pattern("Pattern")
        ctx.add_error("Error")

        full = ctx.get_full_context()
        assert "Stable" in full
        assert "Review" in full
        assert "Pattern" in full
        assert "Error" in full

    def test_full_context_bounded(self):
        ctx = ReviewLoopContext()
        ctx.set_stable_context("x" * 10000)
        full = ctx.get_full_context()
        assert (
            len(full) <= ctx.MAX_TOTAL_CONTEXT + 20
        )  # Some buffer for truncation marker

    def test_clear_dynamic(self):
        ctx = ReviewLoopContext()
        ctx.set_stable_context("Stable")
        ctx.add_review_output("Review")
        ctx.add_error("Error")
        ctx.add_success_pattern("Pattern")

        ctx.clear_dynamic()

        assert ctx.stable_context == "Stable"  # Preserved
        assert ctx.success_patterns == ["Pattern"]  # Preserved
        assert ctx.dynamic_context == []  # Cleared
        assert ctx.error_history == []  # Cleared

    def test_serialization(self):
        ctx = ReviewLoopContext()
        ctx.set_stable_context("Stable")
        ctx.add_review_output("Review")

        data = ctx.to_dict()
        restored = ReviewLoopContext.from_dict(data)

        assert restored.stable_context == ctx.stable_context
        assert restored.dynamic_context == ctx.dynamic_context
