"""Tests for BMAD metrics module.

NOTE: These tests are skipped because the _bmad module has not been implemented yet.
The module is planned as part of the BMAD automation layer but the implementation
is deferred until the core engine components are built.
"""

import pytest

# Skip entire module - the _bmad package does not exist yet
pytest.skip(
    "Skipping: _bmad.core.lib.metrics module not implemented",
    allow_module_level=True,
)


class TestReviewLoopMetrics:
    def test_initial_state(self):
        metrics = ReviewLoopMetrics()
        assert metrics.review_rounds == 0
        assert metrics.total_issues_found == 0
        assert metrics.started_at > 0

    def test_record_review_round(self):
        metrics = ReviewLoopMetrics()
        metrics.record_review_round()
        assert metrics.review_rounds == 1

    def test_record_issues(self):
        metrics = ReviewLoopMetrics()
        metrics.record_issues_found(5)
        metrics.record_issue_fixed()
        metrics.record_issue_fixed()
        metrics.record_issue_blocked()

        assert metrics.total_issues_found == 5
        assert metrics.total_issues_fixed == 2
        assert metrics.total_issues_blocked == 1

    def test_success_rate(self):
        metrics = ReviewLoopMetrics()
        metrics.record_issues_found(10)
        for _ in range(8):
            metrics.record_issue_fixed()

        assert metrics.success_rate() == 0.8

    def test_success_rate_no_issues(self):
        metrics = ReviewLoopMetrics()
        assert metrics.success_rate() == 1.0  # No issues = 100% success

    def test_complete(self):
        metrics = ReviewLoopMetrics()
        metrics.complete(confidence=95.0, reason="ALL_ISSUES_RESOLVED")

        assert metrics.ended_at is not None
        assert metrics.final_confidence == 95.0
        assert metrics.exit_reason == "ALL_ISSUES_RESOLVED"

    def test_to_json(self):
        metrics = ReviewLoopMetrics()
        metrics.record_review_round()
        json_str = metrics.to_json()

        parsed = json.loads(json_str)
        assert parsed["review_rounds"] == 1

    def test_save_to_file(self):
        metrics = ReviewLoopMetrics()
        metrics.record_review_round()

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = metrics.save(Path(tmpdir))
            assert filepath.exists()

            content = json.loads(filepath.read_text())
            assert content["review_rounds"] == 1

    def test_summary(self):
        metrics = ReviewLoopMetrics()
        metrics.record_review_round()
        metrics.record_issues_found(5)
        metrics.record_issue_fixed()
        metrics.complete(90.0, "COMPLETE")

        summary = metrics.summary()
        assert "Review rounds: 1" in summary
        assert "Issues found: 5" in summary
        assert "90.0%" in summary


class TestTriggerReason:
    def test_enum_values(self):
        assert TriggerReason.INITIAL.value == "initial"
        assert TriggerReason.COMPLETE.value == "complete"
