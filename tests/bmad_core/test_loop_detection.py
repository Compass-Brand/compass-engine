"""Tests for BMAD loop detection module.

NOTE: These tests are skipped because the _bmad module has not been implemented yet.
The module is planned as part of the BMAD automation layer but the implementation
is deferred until the core engine components are built.
"""

import pytest

# Skip entire module - the _bmad package does not exist yet
pytest.skip(
    "Skipping: _bmad.core.lib.loop_detection module not implemented",
    allow_module_level=True,
)


class TestDetectLoop:
    def test_empty_history_no_loop(self):
        assert detect_loop("some output", []) is False

    def test_empty_output_no_loop(self):
        assert detect_loop("", ["previous"]) is False

    def test_identical_output_is_loop(self):
        history = ["exact same output"]
        assert detect_loop("exact same output", history) is True

    def test_similar_output_is_loop(self):
        history = ["The quick brown fox jumps over the lazy dog"]
        # 95% similar (minor change)
        assert (
            detect_loop("The quick brown fox jumps over the lazy cat", history) is True
        )

    def test_different_output_not_loop(self):
        history = ["completely different content here"]
        assert detect_loop("something entirely new", history) is False

    def test_respects_history_size(self):
        history = ["old1", "old2", "old3", "old4", "old5", "old6"]
        # Only checks last 5
        assert detect_loop("old1", history) is False  # old1 not in last 5


class TestLoopDetector:
    def test_first_output_not_loop(self):
        detector = LoopDetector()
        assert detector.check("first output") is False

    def test_repeated_output_is_loop(self):
        detector = LoopDetector()
        detector.check("repeated output")
        assert detector.check("repeated output") is True

    def test_clear_resets_history(self):
        detector = LoopDetector()
        detector.check("output")
        detector.clear()
        assert detector.check("output") is False  # After clear, not a loop

    def test_hash_persistence(self):
        detector = LoopDetector()
        detector.check("output1")
        detector.check("output2")

        hashes = detector.get_hashes()
        assert len(hashes) == 2

        new_detector = LoopDetector()
        new_detector.restore_hashes(hashes)
        # Can detect based on restored hashes
        assert compute_hash(normalize_output("output1")) in new_detector.hash_history


class TestNormalizeOutput:
    def test_removes_timestamps(self):
        output = "Error at 2026-01-15T10:30:00 in module"
        normalized = normalize_output(output)
        assert "2026-01-15" not in normalized

    def test_removes_uuids(self):
        output = "Task 550e8400-e29b-41d4-a716-446655440000 failed"
        normalized = normalize_output(output)
        assert "550e8400" not in normalized

    def test_normalizes_whitespace(self):
        output = "multiple   spaces\n\nand\nnewlines"
        normalized = normalize_output(output)
        assert "  " not in normalized
        assert "\n" not in normalized
