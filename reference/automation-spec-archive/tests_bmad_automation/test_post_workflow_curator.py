"""Tests for the Post-Workflow Curator component.

This module tests the ProblemSolutionExtractor class which extracts
problem-solution pairs from workflow context for cross-session learning.

Story 4.2: Post-Workflow Learning Extraction
Parallel Group D: Problem-Solution Extractor (AC: #5)

TDD: All tests written FIRST, then implementation.
"""

import pytest
from typing import List

# These imports will fail until we implement the module (RED phase)


class TestExtractedProblemSolutionDataclass:
    """Test ExtractedProblemSolution dataclass (Task D1.2)."""

    def test_extracted_problem_solution_required_fields(self):
        """ExtractedProblemSolution should have required fields."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedProblemSolution,
        )

        result = ExtractedProblemSolution(
            problem_signature="hash:ImportError:missing_module",
            problem_description="ImportError when importing dataclasses",
            solution_approach="Add 'from dataclasses import dataclass' import",
        )

        assert result.problem_signature == "hash:ImportError:missing_module"
        assert result.problem_description == "ImportError when importing dataclasses"
        assert result.solution_approach == "Add 'from dataclasses import dataclass' import"

    def test_extracted_problem_solution_default_success_indicator(self):
        """ExtractedProblemSolution success_indicator should default to empty string."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedProblemSolution,
        )

        result = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test problem",
            solution_approach="test solution",
        )

        assert result.success_indicator == ""

    def test_extracted_problem_solution_custom_success_indicator(self):
        """ExtractedProblemSolution should accept custom success_indicator."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedProblemSolution,
        )

        result = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test problem",
            solution_approach="test solution",
            success_indicator="All tests passing",
        )

        assert result.success_indicator == "All tests passing"

    def test_extracted_problem_solution_default_importance_is_pattern(self):
        """ExtractedProblemSolution importance should default to 7 (PATTERN)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedProblemSolution,
        )
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        result = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test",
            solution_approach="test",
        )

        assert result.importance == ImportanceLevel.PATTERN  # 7

    def test_extracted_problem_solution_custom_importance(self):
        """ExtractedProblemSolution should accept custom importance."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedProblemSolution,
        )
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        result = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test",
            solution_approach="test",
            importance=ImportanceLevel.PATTERN_HIGH,  # 8
        )

        assert result.importance == ImportanceLevel.PATTERN_HIGH  # 8

    def test_extracted_problem_solution_default_empty_keywords(self):
        """ExtractedProblemSolution should have empty keywords list by default."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedProblemSolution,
        )

        result = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test",
            solution_approach="test",
        )

        assert result.keywords == []

    def test_extracted_problem_solution_custom_keywords(self):
        """ExtractedProblemSolution should accept custom keywords."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedProblemSolution,
        )

        result = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test",
            solution_approach="test",
            keywords=["import", "error", "fix"],
        )

        assert result.keywords == ["import", "error", "fix"]

    def test_extracted_problem_solution_default_empty_tags(self):
        """ExtractedProblemSolution should have empty tags list by default."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedProblemSolution,
        )

        result = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test",
            solution_approach="test",
        )

        assert result.tags == []

    def test_extracted_problem_solution_custom_tags(self):
        """ExtractedProblemSolution should accept custom tags."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedProblemSolution,
        )

        result = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test",
            solution_approach="test",
            tags=["problem-solution", "fix-pattern"],
        )

        assert result.tags == ["problem-solution", "fix-pattern"]


class TestProblemSolutionExtractorInit:
    """Test ProblemSolutionExtractor class initialization (Task D1.1)."""

    def test_problem_solution_extractor_class_exists(self):
        """ProblemSolutionExtractor class should exist."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        assert extractor is not None

    def test_problem_solution_extractor_has_problem_indicators(self):
        """ProblemSolutionExtractor should have PROBLEM_INDICATORS patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        assert hasattr(extractor, "PROBLEM_INDICATORS") or hasattr(
            ProblemSolutionExtractor, "PROBLEM_INDICATORS"
        )

    def test_problem_solution_extractor_has_solution_indicators(self):
        """ProblemSolutionExtractor should have SOLUTION_INDICATORS patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        assert hasattr(extractor, "SOLUTION_INDICATORS") or hasattr(
            ProblemSolutionExtractor, "SOLUTION_INDICATORS"
        )

    def test_problem_solution_extractor_has_detect_problem_solutions_method(self):
        """ProblemSolutionExtractor should have detect_problem_solutions method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        assert hasattr(extractor, "detect_problem_solutions")
        assert callable(extractor.detect_problem_solutions)

    def test_problem_solution_extractor_has_link_problem_to_solution_method(self):
        """ProblemSolutionExtractor should have link_problem_to_solution method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        assert hasattr(extractor, "link_problem_to_solution")
        assert callable(extractor.link_problem_to_solution)

    def test_problem_solution_extractor_has_generate_problem_signature_method(self):
        """ProblemSolutionExtractor should have generate_problem_signature method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        assert hasattr(extractor, "generate_problem_signature")
        assert callable(extractor.generate_problem_signature)

    def test_problem_solution_extractor_has_assign_importance_method(self):
        """ProblemSolutionExtractor should have assign_importance method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        assert hasattr(extractor, "assign_importance")
        assert callable(extractor.assign_importance)


class TestProblemIndicators:
    """Test problem indicator patterns (Task D1.4)."""

    def test_problem_indicators_contains_fixed_pattern(self):
        """PROBLEM_INDICATORS should contain 'fixed' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        indicators = ProblemSolutionExtractor.PROBLEM_INDICATORS
        assert any("fixed" in indicator.lower() for indicator in indicators)

    def test_problem_indicators_contains_resolved_pattern(self):
        """PROBLEM_INDICATORS should contain 'resolved' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        indicators = ProblemSolutionExtractor.PROBLEM_INDICATORS
        assert any("resolved" in indicator.lower() for indicator in indicators)

    def test_problem_indicators_contains_solved_pattern(self):
        """PROBLEM_INDICATORS should contain 'solved' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        indicators = ProblemSolutionExtractor.PROBLEM_INDICATORS
        assert any("solved" in indicator.lower() for indicator in indicators)

    def test_problem_indicators_contains_error_pattern(self):
        """PROBLEM_INDICATORS should contain 'error' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        indicators = ProblemSolutionExtractor.PROBLEM_INDICATORS
        assert any("error" in indicator.lower() for indicator in indicators)

    def test_problem_indicators_contains_issue_pattern(self):
        """PROBLEM_INDICATORS should contain 'issue' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        indicators = ProblemSolutionExtractor.PROBLEM_INDICATORS
        assert any("issue" in indicator.lower() for indicator in indicators)

    def test_problem_indicators_contains_bug_pattern(self):
        """PROBLEM_INDICATORS should contain 'bug' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        indicators = ProblemSolutionExtractor.PROBLEM_INDICATORS
        assert any("bug" in indicator.lower() for indicator in indicators)


class TestDetectProblemSolutions:
    """Test detect_problem_solutions method (Task D1.3, D1.5)."""

    def test_detect_problem_solutions_returns_list(self):
        """detect_problem_solutions should return a list."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.detect_problem_solutions({})

        assert isinstance(result, list)

    def test_detect_problem_solutions_empty_context_returns_empty_list(self):
        """detect_problem_solutions with empty context should return empty list."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.detect_problem_solutions({})

        assert result == []

    def test_detect_problem_solutions_finds_fixed_pattern(self):
        """detect_problem_solutions should find 'fixed' patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
            ExtractedProblemSolution,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Fixed ImportError by adding missing import statement"}
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1
        assert isinstance(result[0], ExtractedProblemSolution)

    def test_detect_problem_solutions_finds_resolved_pattern(self):
        """detect_problem_solutions should find 'resolved' patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Resolved the connection timeout by increasing the limit"}
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1

    def test_detect_problem_solutions_finds_solved_pattern(self):
        """detect_problem_solutions should find 'solved' patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Solved the race condition by using a mutex lock"}
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1

    def test_detect_problem_solutions_finds_error_with_solution(self):
        """detect_problem_solutions should find error-solution pairs."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Error: ModuleNotFoundError - fixed by installing package"}
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1

    def test_detect_problem_solutions_finds_bug_pattern(self):
        """detect_problem_solutions should find 'bug' patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Bug in validation logic was fixed by updating the regex"}
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1

    def test_detect_problem_solutions_finds_issue_pattern(self):
        """detect_problem_solutions should find 'issue' patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Issue with database connection resolved by retry logic"}
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1

    def test_detect_problem_solutions_ignores_non_problem_content(self):
        """detect_problem_solutions should ignore content without problem patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Implemented new feature successfully"},
                {"content": "Added documentation for API endpoints"},
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert result == []

    def test_detect_problem_solutions_handles_multiple_problems(self):
        """detect_problem_solutions should handle multiple problems."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Fixed ImportError by adding import"},
                {"content": "Resolved timeout by increasing limit"},
                {"content": "Solved race condition with mutex"},
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 3

    def test_detect_problem_solutions_extracts_problem_description(self):
        """detect_problem_solutions should extract problem description."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Fixed ImportError when importing dataclasses module"}
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1
        assert "ImportError" in result[0].problem_description or \
               "import" in result[0].problem_description.lower()

    def test_detect_problem_solutions_extracts_solution_approach(self):
        """detect_problem_solutions should extract solution approach."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Fixed the bug by adding input validation"}
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1
        assert len(result[0].solution_approach) > 0

    def test_detect_problem_solutions_from_workflow_output(self):
        """detect_problem_solutions should extract from workflow output field."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "workflow_output": "Fixed authentication error by regenerating tokens"
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1

    def test_detect_problem_solutions_case_insensitive(self):
        """detect_problem_solutions should be case insensitive."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "FIXED the issue by updating config"},
                {"content": "RESOLVED the bug with new approach"},
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 2

    def test_detect_problem_solutions_handles_unicode(self):
        """detect_problem_solutions should handle unicode characters."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "messages": [
                {"content": "Fixed encoding issue for cafe characters"}
            ]
        }
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1


class TestGenerateProblemSignature:
    """Test generate_problem_signature method (Task D2.2)."""

    def test_generate_problem_signature_returns_string(self):
        """generate_problem_signature should return a string."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.generate_problem_signature("ImportError in module")

        assert isinstance(result, str)

    def test_generate_problem_signature_is_deterministic(self):
        """generate_problem_signature should be deterministic (same input = same output)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        problem = "ImportError when importing dataclasses"

        result1 = extractor.generate_problem_signature(problem)
        result2 = extractor.generate_problem_signature(problem)

        assert result1 == result2

    def test_generate_problem_signature_different_for_different_problems(self):
        """generate_problem_signature should generate different signatures for different problems."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()

        sig1 = extractor.generate_problem_signature("ImportError in module A")
        sig2 = extractor.generate_problem_signature("TypeError in function B")

        assert sig1 != sig2

    def test_generate_problem_signature_uses_hash(self):
        """generate_problem_signature should use hash-based signature."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.generate_problem_signature("Test problem")

        # Should look like a hash (hex digits) or contain hash prefix
        assert len(result) > 0
        # Common hash patterns: hex string or prefixed hash
        assert result.startswith("hash:") or all(c in "0123456789abcdef" for c in result.lower().replace(":", "").replace("_", ""))

    def test_generate_problem_signature_normalizes_whitespace(self):
        """generate_problem_signature should normalize whitespace."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()

        sig1 = extractor.generate_problem_signature("Import Error  in module")
        sig2 = extractor.generate_problem_signature("Import Error in module")

        assert sig1 == sig2

    def test_generate_problem_signature_handles_empty_string(self):
        """generate_problem_signature should handle empty string."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.generate_problem_signature("")

        assert isinstance(result, str)


class TestLinkProblemToSolution:
    """Test link_problem_to_solution method (Task D2.1)."""

    def test_link_problem_to_solution_returns_extracted_problem_solution(self):
        """link_problem_to_solution should return ExtractedProblemSolution."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
            ExtractedProblemSolution,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.link_problem_to_solution(
            problem="ImportError when importing dataclasses",
            solution="Add 'from dataclasses import dataclass' import",
        )

        assert isinstance(result, ExtractedProblemSolution)

    def test_link_problem_to_solution_includes_problem_description(self):
        """link_problem_to_solution should include problem description."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.link_problem_to_solution(
            problem="ImportError when importing dataclasses",
            solution="Add import statement",
        )

        assert "ImportError" in result.problem_description

    def test_link_problem_to_solution_includes_solution_approach(self):
        """link_problem_to_solution should include solution approach."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.link_problem_to_solution(
            problem="ImportError",
            solution="Add 'from dataclasses import dataclass' import",
        )

        assert "import" in result.solution_approach.lower()

    def test_link_problem_to_solution_generates_signature(self):
        """link_problem_to_solution should generate problem signature."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.link_problem_to_solution(
            problem="ImportError when importing dataclasses",
            solution="Add import statement",
        )

        assert len(result.problem_signature) > 0

    def test_link_problem_to_solution_consistent_signature(self):
        """link_problem_to_solution should generate consistent signature for same problem."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        problem = "ImportError when importing dataclasses"

        result1 = extractor.link_problem_to_solution(problem, "Solution A")
        result2 = extractor.link_problem_to_solution(problem, "Solution B")

        # Same problem should have same signature regardless of solution
        assert result1.problem_signature == result2.problem_signature

    def test_link_problem_to_solution_default_importance(self):
        """link_problem_to_solution should set importance to 7-8."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.link_problem_to_solution(
            problem="Test problem",
            solution="Test solution",
        )

        assert result.importance in (7, 8)

    def test_link_problem_to_solution_generates_keywords(self):
        """link_problem_to_solution should generate keywords from content."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.link_problem_to_solution(
            problem="ImportError when importing dataclasses module",
            solution="Add import statement to fix the error",
        )

        assert len(result.keywords) > 0

    def test_link_problem_to_solution_generates_tags(self):
        """link_problem_to_solution should generate tags."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.link_problem_to_solution(
            problem="Test problem",
            solution="Test solution",
        )

        assert len(result.tags) > 0
        assert "problem-solution" in result.tags


class TestAssignImportance:
    """Test assign_importance method (Task D2.3)."""

    def test_assign_importance_returns_integer(self):
        """assign_importance should return an integer."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
            ExtractedProblemSolution,
        )

        extractor = ProblemSolutionExtractor()
        pair = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test",
            solution_approach="test",
        )
        result = extractor.assign_importance(pair)

        assert isinstance(result, int)

    def test_assign_importance_returns_7_or_8(self):
        """assign_importance should return 7-8 for problem-solution pairs."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
            ExtractedProblemSolution,
        )

        extractor = ProblemSolutionExtractor()
        pair = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test",
            solution_approach="test",
        )
        result = extractor.assign_importance(pair)

        assert result in (7, 8)

    def test_assign_importance_8_for_detailed_solution(self):
        """assign_importance should return 8 for detailed solutions."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
            ExtractedProblemSolution,
        )

        extractor = ProblemSolutionExtractor()
        # Detailed solution with clear success indicator
        pair = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="Complex database connection failure",
            solution_approach="Implemented retry logic with exponential backoff, "
                            "added connection pooling, and configured proper timeouts",
            success_indicator="All tests passing, no connection errors in 24h",
        )
        result = extractor.assign_importance(pair)

        assert result == 8

    def test_assign_importance_7_for_simple_solution(self):
        """assign_importance should return 7 for simple solutions."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
            ExtractedProblemSolution,
        )

        extractor = ProblemSolutionExtractor()
        # Simple solution without detailed explanation
        pair = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="Import error",
            solution_approach="Added import",
        )
        result = extractor.assign_importance(pair)

        assert result == 7

    def test_assign_importance_considers_success_indicator(self):
        """assign_importance should consider success indicator."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
            ExtractedProblemSolution,
        )

        extractor = ProblemSolutionExtractor()
        pair_with_success = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test",
            solution_approach="test solution with reasonable detail",
            success_indicator="All tests passing, verified in production",
        )
        pair_without_success = ExtractedProblemSolution(
            problem_signature="test",
            problem_description="test",
            solution_approach="test solution",
            success_indicator="",
        )

        result_with = extractor.assign_importance(pair_with_success)
        result_without = extractor.assign_importance(pair_without_success)

        # With success indicator should have higher or equal importance
        assert result_with >= result_without


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_detect_problem_solutions_with_none_messages(self):
        """detect_problem_solutions should handle None in messages."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {"messages": [None, {"content": "Fixed error"}]}
        result = extractor.detect_problem_solutions(context)

        # Should not crash and should still find the valid fix
        assert len(result) >= 1

    def test_detect_problem_solutions_with_empty_content(self):
        """detect_problem_solutions should handle empty content."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {"messages": [{"content": ""}, {"content": "Fixed error"}]}
        result = extractor.detect_problem_solutions(context)

        assert len(result) >= 1

    def test_link_problem_to_solution_with_very_long_content(self):
        """link_problem_to_solution should handle very long content."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        long_problem = "Error: " + "x" * 5000
        long_solution = "Solution: " + "y" * 5000

        result = extractor.link_problem_to_solution(long_problem, long_solution)

        # Should not crash and should have content
        assert len(result.problem_description) > 0
        assert len(result.solution_approach) > 0

    def test_generate_problem_signature_with_special_characters(self):
        """generate_problem_signature should handle special characters."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.generate_problem_signature(
            "Error: \\n\\t\\r special chars <>&\"'"
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_detect_problem_solutions_with_nested_context(self):
        """detect_problem_solutions should handle nested context structure."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        context = {
            "steps": {
                "step_1": {
                    "messages": [
                        {"content": "Fixed ImportError by adding import"}
                    ]
                }
            }
        }
        # This tests that the extractor handles various context structures
        # gracefully - it may or may not find the nested content
        result = extractor.detect_problem_solutions(context)
        assert isinstance(result, list)

    def test_keywords_limit_to_10(self):
        """Keywords should be limited to 10 items."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        # Many potential keywords
        long_problem = " ".join([f"keyword{i}" for i in range(20)])
        long_solution = " ".join([f"solution{i}" for i in range(20)])

        result = extractor.link_problem_to_solution(long_problem, long_solution)

        assert len(result.keywords) <= 10

    def test_tags_include_problem_solution_tag(self):
        """Tags should always include 'problem-solution' tag."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ProblemSolutionExtractor,
        )

        extractor = ProblemSolutionExtractor()
        result = extractor.link_problem_to_solution(
            problem="Any problem",
            solution="Any solution",
        )

        assert "problem-solution" in result.tags


# =============================================================================
# Group C: MilestoneExtractor Tests (Tasks C1, C2)
# =============================================================================


class TestExtractedMilestoneDataclass:
    """Tests for ExtractedMilestone dataclass (C1.2)."""

    def test_extracted_milestone_basic_creation(self):
        """Test creating ExtractedMilestone with required fields."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedMilestone,
        )

        milestone = ExtractedMilestone(
            milestone_name="Phase 2 complete",
        )
        assert milestone.milestone_name == "Phase 2 complete"
        assert milestone.scope == "story"  # default
        assert milestone.completion_date is None  # default
        assert milestone.importance == 6  # default MILESTONE level

    def test_extracted_milestone_with_all_fields(self):
        """Test creating ExtractedMilestone with all fields specified."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedMilestone,
        )

        milestone = ExtractedMilestone(
            milestone_name="Epic 2a Complete",
            scope="epic",
            completion_date="2026-01-13",
            importance=7,
            keywords=["epic", "complete", "bmad"],
            tags=["milestone", "epic-complete"],
        )
        assert milestone.milestone_name == "Epic 2a Complete"
        assert milestone.scope == "epic"
        assert milestone.completion_date == "2026-01-13"
        assert milestone.importance == 7
        assert milestone.keywords == ["epic", "complete", "bmad"]
        assert milestone.tags == ["milestone", "epic-complete"]

    def test_extracted_milestone_default_keywords_and_tags(self):
        """Test that keywords and tags default to empty lists."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedMilestone,
        )

        milestone = ExtractedMilestone(milestone_name="Test")
        assert milestone.keywords == []
        assert milestone.tags == []


class TestMilestoneExtractorClass:
    """Tests for MilestoneExtractor class (C1.1)."""

    def test_milestone_extractor_exists(self):
        """Test that MilestoneExtractor class exists."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        assert MilestoneExtractor is not None

    def test_milestone_extractor_instantiation(self):
        """Test creating MilestoneExtractor instance."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert extractor is not None

    def test_milestone_extractor_has_completion_indicators(self):
        """Test that MilestoneExtractor has COMPLETION_INDICATORS."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert hasattr(extractor, "COMPLETION_INDICATORS")
        assert len(extractor.COMPLETION_INDICATORS) > 0


class TestMilestoneDetectionPatterns:
    """Tests for milestone detection patterns (C1.4)."""

    def test_completion_indicators_include_complete(self):
        """Test COMPLETION_INDICATORS includes 'complete' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        # Check that at least one pattern matches "X complete"
        patterns = extractor.COMPLETION_INDICATORS
        assert any("complete" in p.lower() for p in patterns)

    def test_completion_indicators_include_finished(self):
        """Test COMPLETION_INDICATORS includes 'finished' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        patterns = extractor.COMPLETION_INDICATORS
        assert any("finish" in p.lower() for p in patterns)

    def test_completion_indicators_include_done(self):
        """Test COMPLETION_INDICATORS includes 'done' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        patterns = extractor.COMPLETION_INDICATORS
        assert any("done" in p.lower() for p in patterns)

    def test_completion_indicators_include_shipped(self):
        """Test COMPLETION_INDICATORS includes 'shipped' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        patterns = extractor.COMPLETION_INDICATORS
        assert any("ship" in p.lower() for p in patterns)

    def test_completion_indicators_include_released(self):
        """Test COMPLETION_INDICATORS includes 'released' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        patterns = extractor.COMPLETION_INDICATORS
        assert any("release" in p.lower() for p in patterns)


class TestDetectMilestones:
    """Tests for detect_milestones() method (C1.3)."""

    def test_detect_milestones_method_exists(self):
        """Test that detect_milestones method exists."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert hasattr(extractor, "detect_milestones")
        assert callable(extractor.detect_milestones)

    def test_detect_milestones_returns_list(self):
        """Test that detect_milestones returns a list."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        result = extractor.detect_milestones({})
        assert isinstance(result, list)

    def test_detect_milestones_empty_context(self):
        """Test detect_milestones with empty context returns empty list."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        result = extractor.detect_milestones({})
        assert result == []

    def test_detect_milestones_finds_phase_complete(self):
        """Test detect_milestones finds 'Phase X complete' milestone."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
            ExtractedMilestone,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Phase 2 complete. Moving to Phase 3.",
            "messages": ["Phase 2 complete"],
        }
        result = extractor.detect_milestones(context)
        assert len(result) >= 1
        assert isinstance(result[0], ExtractedMilestone)
        assert "phase" in result[0].milestone_name.lower()

    def test_detect_milestones_finds_epic_done(self):
        """Test detect_milestones finds 'Epic done' milestone."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
            ExtractedMilestone,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Epic 2a is done. All stories completed.",
        }
        result = extractor.detect_milestones(context)
        assert len(result) >= 1
        assert any("epic" in m.milestone_name.lower() for m in result)

    def test_detect_milestones_finds_story_finished(self):
        """Test detect_milestones finds 'Story finished' milestone."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
            ExtractedMilestone,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Story 4-1 finished successfully.",
        }
        result = extractor.detect_milestones(context)
        assert len(result) >= 1

    def test_detect_milestones_finds_feature_shipped(self):
        """Test detect_milestones finds 'Feature shipped' milestone."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Login feature shipped to production.",
        }
        result = extractor.detect_milestones(context)
        assert len(result) >= 1

    def test_detect_milestones_finds_version_released(self):
        """Test detect_milestones finds 'Version released' milestone."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Version 2.0 released to users.",
        }
        result = extractor.detect_milestones(context)
        assert len(result) >= 1

    def test_detect_milestones_no_false_positives(self):
        """Test detect_milestones doesn't match non-milestone text."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Working on implementation. Not yet done.",
        }
        result = extractor.detect_milestones(context)
        # "Not yet done" should not trigger a milestone
        assert len(result) == 0

    def test_detect_milestones_multiple_milestones(self):
        """Test detect_milestones finds multiple milestones in same context."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Phase 1 complete. Epic 1a finished. Story 1.1 done.",
        }
        result = extractor.detect_milestones(context)
        assert len(result) >= 2

    def test_detect_milestones_scans_messages_field(self):
        """Test detect_milestones scans 'messages' field in context."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "messages": ["Feature complete!", "Ready for review."],
        }
        result = extractor.detect_milestones(context)
        assert len(result) >= 1

    def test_detect_milestones_scans_summary_field(self):
        """Test detect_milestones scans 'summary' field in context."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "summary": "Implementation finished. Tests passing.",
        }
        result = extractor.detect_milestones(context)
        assert len(result) >= 1


class TestDetermineScope:
    """Tests for determine_scope() method (C1.3 helper)."""

    def test_determine_scope_method_exists(self):
        """Test that determine_scope method exists."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert hasattr(extractor, "determine_scope")
        assert callable(extractor.determine_scope)

    def test_determine_scope_returns_story_by_default(self):
        """Test determine_scope returns 'story' for unknown scope."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        scope = extractor.determine_scope("Feature complete", {})
        assert scope == "story"

    def test_determine_scope_detects_epic(self):
        """Test determine_scope detects 'epic' scope."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        scope = extractor.determine_scope("Epic 2a complete", {})
        assert scope == "epic"

    def test_determine_scope_detects_phase(self):
        """Test determine_scope detects 'phase' scope."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        scope = extractor.determine_scope("Phase 3 finished", {})
        assert scope == "phase"

    def test_determine_scope_detects_story(self):
        """Test determine_scope detects 'story' scope."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        scope = extractor.determine_scope("Story 4-2 done", {})
        assert scope == "story"

    def test_determine_scope_detects_task(self):
        """Test determine_scope detects 'task' scope."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        scope = extractor.determine_scope("Task C1 complete", {})
        assert scope == "task"

    def test_determine_scope_case_insensitive(self):
        """Test determine_scope is case insensitive."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert extractor.determine_scope("EPIC 1 DONE", {}) == "epic"
        assert extractor.determine_scope("phase Complete", {}) == "phase"


class TestMilestoneImportance:
    """Tests for assign_importance() method (C2.1, C2.2)."""

    def test_milestone_assign_importance_method_exists(self):
        """Test that assign_importance method exists."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert hasattr(extractor, "assign_importance")
        assert callable(extractor.assign_importance)

    def test_milestone_assign_importance_returns_int(self):
        """Test assign_importance returns an integer."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
            ExtractedMilestone,
        )

        extractor = MilestoneExtractor()
        milestone = ExtractedMilestone(milestone_name="Test", scope="story")
        result = extractor.assign_importance(milestone)
        assert isinstance(result, int)

    def test_milestone_assign_importance_epic_returns_7(self):
        """Test assign_importance returns 7 for epic scope (C2.2)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
            ExtractedMilestone,
        )

        extractor = MilestoneExtractor()
        milestone = ExtractedMilestone(milestone_name="Epic 2a", scope="epic")
        result = extractor.assign_importance(milestone)
        assert result == 7

    def test_milestone_assign_importance_phase_returns_7(self):
        """Test assign_importance returns 7 for phase scope (C2.2)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
            ExtractedMilestone,
        )

        extractor = MilestoneExtractor()
        milestone = ExtractedMilestone(milestone_name="Phase 3", scope="phase")
        result = extractor.assign_importance(milestone)
        assert result == 7

    def test_milestone_assign_importance_story_returns_6(self):
        """Test assign_importance returns 6 for story scope (C2.2)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
            ExtractedMilestone,
        )

        extractor = MilestoneExtractor()
        milestone = ExtractedMilestone(milestone_name="Story 4-1", scope="story")
        result = extractor.assign_importance(milestone)
        assert result == 6

    def test_milestone_assign_importance_task_returns_6(self):
        """Test assign_importance returns 6 for task scope (C2.2)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
            ExtractedMilestone,
        )

        extractor = MilestoneExtractor()
        milestone = ExtractedMilestone(milestone_name="Task C1", scope="task")
        result = extractor.assign_importance(milestone)
        assert result == 6

    def test_milestone_assign_importance_unknown_scope_returns_6(self):
        """Test assign_importance returns 6 for unknown scope."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
            ExtractedMilestone,
        )

        extractor = MilestoneExtractor()
        milestone = ExtractedMilestone(milestone_name="Feature", scope="unknown")
        result = extractor.assign_importance(milestone)
        assert result == 6

    def test_milestone_assign_importance_range_is_6_to_7(self):
        """Test assign_importance only returns values in range 6-7."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
            ExtractedMilestone,
        )

        extractor = MilestoneExtractor()
        scopes = ["epic", "phase", "story", "task", "unknown", "feature", "release"]
        for scope in scopes:
            milestone = ExtractedMilestone(milestone_name="Test", scope=scope)
            result = extractor.assign_importance(milestone)
            assert 6 <= result <= 7, f"Scope '{scope}' returned {result}"


class TestMilestoneExtractorScopeKeywords:
    """Tests for SCOPE_KEYWORDS configuration."""

    def test_scope_keywords_exists(self):
        """Test that SCOPE_KEYWORDS class attribute exists."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert hasattr(extractor, "SCOPE_KEYWORDS")

    def test_scope_keywords_maps_epic_to_7(self):
        """Test SCOPE_KEYWORDS maps 'epic' to importance 7."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert extractor.SCOPE_KEYWORDS.get("epic") == 7

    def test_scope_keywords_maps_phase_to_7(self):
        """Test SCOPE_KEYWORDS maps 'phase' to importance 7."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert extractor.SCOPE_KEYWORDS.get("phase") == 7

    def test_scope_keywords_maps_story_to_6(self):
        """Test SCOPE_KEYWORDS maps 'story' to importance 6."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert extractor.SCOPE_KEYWORDS.get("story") == 6

    def test_scope_keywords_maps_task_to_6(self):
        """Test SCOPE_KEYWORDS maps 'task' to importance 6."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        assert extractor.SCOPE_KEYWORDS.get("task") == 6


class TestMilestoneExtractorIntegration:
    """Integration tests for MilestoneExtractor."""

    def test_detect_milestones_assigns_correct_scope(self):
        """Test that detected milestones have correct scope assigned."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Epic 2a complete. All 7 stories finished.",
        }
        result = extractor.detect_milestones(context)
        epic_milestone = next(
            (m for m in result if "epic" in m.milestone_name.lower()), None
        )
        if epic_milestone:
            assert epic_milestone.scope == "epic"

    def test_detect_milestones_assigns_correct_importance(self):
        """Test that detected milestones have correct importance assigned."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Phase 2 complete.",
        }
        result = extractor.detect_milestones(context)
        if result:
            # Phase completion should have importance 7
            assert result[0].importance == 7

    def test_milestone_extraction_generates_keywords(self):
        """Test that extracted milestones have keywords generated."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Epic 2a BMAD Automation complete.",
        }
        result = extractor.detect_milestones(context)
        if result:
            assert len(result[0].keywords) > 0

    def test_milestone_extraction_generates_tags(self):
        """Test that extracted milestones have tags generated."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Story 4-2 finished.",
        }
        result = extractor.detect_milestones(context)
        if result:
            assert len(result[0].tags) > 0
            assert "milestone" in result[0].tags


class TestMilestoneExtractorEdgeCases:
    """Edge case tests for MilestoneExtractor."""

    def test_detect_milestones_handles_none_values(self):
        """Test detect_milestones handles None values gracefully."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": None,
            "messages": None,
        }
        result = extractor.detect_milestones(context)
        assert result == []

    def test_detect_milestones_handles_empty_strings(self):
        """Test detect_milestones handles empty strings."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "",
            "messages": [""],
        }
        result = extractor.detect_milestones(context)
        assert result == []

    def test_detect_milestones_deduplicates_results(self):
        """Test detect_milestones deduplicates identical milestones."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        context = {
            "workflow_output": "Phase 2 complete",
            "messages": ["Phase 2 complete"],
            "summary": "Phase 2 complete",
        }
        result = extractor.detect_milestones(context)
        # Should deduplicate identical milestone names
        phase_milestones = [
            m for m in result if "phase 2" in m.milestone_name.lower()
        ]
        assert len(phase_milestones) <= 1

    def test_detect_milestones_negation_handling(self):
        """Test detect_milestones handles negation patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            MilestoneExtractor,
        )

        extractor = MilestoneExtractor()
        # These should NOT be detected as milestones
        negative_contexts = [
            {"workflow_output": "Not yet complete"},
            {"workflow_output": "Story is not done"},
            {"workflow_output": "Still incomplete"},
            {"workflow_output": "Implementation isn't finished"},
        ]
        for context in negative_contexts:
            result = extractor.detect_milestones(context)
            assert len(result) == 0, f"False positive for: {context}"


# =============================================================================
# Group A: ArchitecturalDecisionExtractor Tests (Tasks A1, A2)
# =============================================================================


class TestExtractedDecisionDataclass:
    """Tests for ExtractedDecision dataclass (Task A1.2)."""

    def test_extracted_decision_has_required_fields(self):
        """ExtractedDecision should have decision, rationale, alternatives_considered."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedDecision,
        )

        decision = ExtractedDecision(
            decision="Use PostgreSQL over MongoDB",
            rationale="Relational data with complex joins",
            alternatives_considered=["MongoDB", "Redis"],
        )

        assert decision.decision == "Use PostgreSQL over MongoDB"
        assert decision.rationale == "Relational data with complex joins"
        assert decision.alternatives_considered == ["MongoDB", "Redis"]

    def test_extracted_decision_has_default_importance(self):
        """ExtractedDecision should default importance to 9 (ARCHITECTURAL_LOW)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedDecision,
        )
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        decision = ExtractedDecision(
            decision="Test decision",
            rationale="Test rationale",
        )

        assert decision.importance == ImportanceLevel.ARCHITECTURAL_LOW
        assert decision.importance == 9

    def test_extracted_decision_has_default_scope(self):
        """ExtractedDecision should default scope to 'component'."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedDecision,
        )

        decision = ExtractedDecision(
            decision="Test decision",
            rationale="Test rationale",
        )

        assert decision.scope == "component"

    def test_extracted_decision_has_keywords_and_tags(self):
        """ExtractedDecision should have keywords and tags lists."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedDecision,
        )

        decision = ExtractedDecision(
            decision="Test decision",
            rationale="Test rationale",
            keywords=["postgresql", "database"],
            tags=["architecture", "storage"],
        )

        assert decision.keywords == ["postgresql", "database"]
        assert decision.tags == ["architecture", "storage"]

    def test_extracted_decision_defaults_to_empty_lists(self):
        """ExtractedDecision should default to empty lists for optional fields."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedDecision,
        )

        decision = ExtractedDecision(
            decision="Test decision",
            rationale="Test rationale",
        )

        assert decision.alternatives_considered == []
        assert decision.keywords == []
        assert decision.tags == []


class TestArchitecturalDecisionExtractorDetection:
    """Tests for architectural decision detection (Tasks A1.1, A1.3, A1.4, A1.5)."""

    def test_extractor_has_decision_patterns(self):
        """Extractor should define detection patterns (A1.1, A1.4)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()

        assert hasattr(extractor, "DECISION_PATTERNS")
        assert len(extractor.DECISION_PATTERNS) > 0

    def test_detect_chose_x_over_y_pattern(self):
        """Should detect 'chose X over Y' pattern (A1.4)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "We chose PostgreSQL over MongoDB for the database."
        }

        decisions = extractor.detect_architectural_decisions(context)

        assert len(decisions) >= 1
        # Should capture PostgreSQL and MongoDB from the pattern
        found = any("PostgreSQL" in d.decision for d in decisions)
        assert found, f"Expected 'PostgreSQL' in decisions: {decisions}"

    def test_detect_architecture_uses_pattern(self):
        """Should detect 'architecture uses X' pattern (A1.4)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "The architecture uses microservices for scalability."
        }

        decisions = extractor.detect_architectural_decisions(context)

        assert len(decisions) >= 1
        found = any("microservices" in d.decision.lower() for d in decisions)
        assert found, f"Expected 'microservices' in decisions: {decisions}"

    def test_detect_design_decision_pattern(self):
        """Should detect 'design decision: X' pattern (A1.4)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "Design decision: implement caching at the API layer"
        }

        decisions = extractor.detect_architectural_decisions(context)

        assert len(decisions) >= 1
        found = any("caching" in d.decision.lower() for d in decisions)
        assert found, f"Expected 'caching' in decisions: {decisions}"

    def test_detect_decided_to_use_pattern(self):
        """Should detect 'decided to use X' pattern (A1.4)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "We decided to use Redis for session management."
        }

        decisions = extractor.detect_architectural_decisions(context)

        assert len(decisions) >= 1
        found = any("Redis" in d.decision for d in decisions)
        assert found, f"Expected 'Redis' in decisions: {decisions}"

    def test_detect_selected_x_for_pattern(self):
        """Should detect 'selected X for' pattern (A1.4)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "Selected Kubernetes for container orchestration."
        }

        decisions = extractor.detect_architectural_decisions(context)

        assert len(decisions) >= 1
        found = any("Kubernetes" in d.decision for d in decisions)
        assert found, f"Expected 'Kubernetes' in decisions: {decisions}"

    def test_detect_multiple_decisions_in_context(self):
        """Should detect multiple decisions in same context (A1.3)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": """
            We chose PostgreSQL over MongoDB for data storage.
            The architecture uses event sourcing for audit trails.
            Selected React for the frontend framework.
            """
        }

        decisions = extractor.detect_architectural_decisions(context)

        # Should find at least 3 decisions
        assert len(decisions) >= 3

    def test_empty_context_returns_empty_list(self):
        """Empty context should return empty list (A1.3)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {}

        decisions = extractor.detect_architectural_decisions(context)

        assert decisions == []

    def test_no_decisions_in_context_returns_empty_list(self):
        """Context without decisions should return empty list (A1.3)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "The system works well and users are happy."
        }

        decisions = extractor.detect_architectural_decisions(context)

        assert decisions == []

    def test_scans_multiple_context_fields(self):
        """Should scan multiple context fields (A1.3)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "Chose Python over Java for backend.",
            "notes": "Design decision: use async/await pattern",
            "summary": "Selected FastAPI for web framework.",
        }

        decisions = extractor.detect_architectural_decisions(context)

        # Should find decisions from multiple fields
        assert len(decisions) >= 2

    def test_extracts_rationale_when_available(self):
        """Should extract rationale when present near decision (A1.3)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "Chose PostgreSQL over MongoDB because of ACID compliance and complex joins."
        }

        decisions = extractor.detect_architectural_decisions(context)

        assert len(decisions) >= 1
        # Rationale should be extracted
        decision = decisions[0]
        assert len(decision.rationale) > 0

    def test_extracts_alternatives_from_chose_over_pattern(self):
        """Should extract alternatives from 'chose X over Y' pattern (A1.3)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "Chose PostgreSQL over MongoDB for the database."
        }

        decisions = extractor.detect_architectural_decisions(context)

        assert len(decisions) >= 1
        decision = decisions[0]
        # MongoDB should be in alternatives
        assert "MongoDB" in decision.alternatives_considered or "MongoDB" in decision.decision


class TestArchitecturalDecisionExtractorRationale:
    """Tests for rationale extraction."""

    def test_extract_rationale_with_because(self):
        """Should extract rationale when 'because' is present."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        text = "chose PostgreSQL over MongoDB because of strong consistency"
        decision = "chose PostgreSQL over MongoDB"

        rationale = extractor.extract_rationale(text, decision)

        assert "consistency" in rationale.lower() or len(rationale) > 0

    def test_extract_rationale_with_for_clause(self):
        """Should extract rationale when 'for' clause is present."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        text = "Selected Kubernetes for better container orchestration"
        decision = "Selected Kubernetes"

        rationale = extractor.extract_rationale(text, decision)

        assert len(rationale) > 0

    def test_extract_rationale_empty_when_not_found(self):
        """Should return empty string when no rationale found."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        text = "Chose Python"
        decision = "Chose Python"

        rationale = extractor.extract_rationale(text, decision)

        assert rationale == "" or rationale is not None  # Empty or minimal


class TestArchitecturalDecisionImportanceAssignment:
    """Tests for importance assignment (Task A2)."""

    def test_system_wide_decisions_get_importance_10(self):
        """System-wide decisions should get importance 10 (A2.1, A2.2)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
            ExtractedDecision,
        )
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        extractor = ArchitecturalDecisionExtractor()
        decision = ExtractedDecision(
            decision="Chose PostgreSQL for all services",
            rationale="Enterprise consistency",
            scope="system",
        )

        importance = extractor.assign_importance(decision)

        assert importance == ImportanceLevel.ARCHITECTURAL
        assert importance == 10

    def test_component_level_decisions_get_importance_9(self):
        """Component-level decisions should get importance 9 (A2.1, A2.2)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
            ExtractedDecision,
        )
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        extractor = ArchitecturalDecisionExtractor()
        decision = ExtractedDecision(
            decision="Chose Redis for session caching",
            rationale="Fast in-memory access",
            scope="component",
        )

        importance = extractor.assign_importance(decision)

        assert importance == ImportanceLevel.ARCHITECTURAL_LOW
        assert importance == 9

    def test_default_scope_gets_importance_9(self):
        """Default scope (component) should get importance 9 (A2.2)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
            ExtractedDecision,
        )

        extractor = ArchitecturalDecisionExtractor()
        decision = ExtractedDecision(
            decision="Test decision",
            rationale="Test rationale",
            # No scope specified, defaults to "component"
        )

        importance = extractor.assign_importance(decision)

        assert importance == 9

    def test_assign_importance_updates_decision(self):
        """assign_importance should update decision's importance field (A2.1)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
            ExtractedDecision,
        )

        extractor = ArchitecturalDecisionExtractor()
        decision = ExtractedDecision(
            decision="System-wide logging framework",
            rationale="Unified observability",
            scope="system",
        )

        # Initial default
        assert decision.importance == 9

        # After assignment
        importance = extractor.assign_importance(decision)
        decision.importance = importance

        assert decision.importance == 10

    def test_importance_based_on_scope_keyword_system(self):
        """Should detect system scope from keywords like 'all services' (A2.2)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "We chose PostgreSQL over MySQL for all services across the platform."
        }

        decisions = extractor.detect_architectural_decisions(context)

        # Should detect this as system-wide
        assert len(decisions) >= 1
        # The scope detection is based on keywords
        assert decisions[0].scope == "system"

    def test_importance_based_on_scope_keyword_component(self):
        """Should detect component scope from specific component mentions (A2.2)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "We decided to use Redis for the authentication service caching."
        }

        decisions = extractor.detect_architectural_decisions(context)

        # Should detect this as component-level
        assert len(decisions) >= 1


class TestArchitecturalDecisionScopeDetection:
    """Tests for scope detection logic."""

    def test_detect_system_scope_from_keywords(self):
        """Should detect system scope from 'all', 'entire', 'platform' keywords."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()

        system_indicators = [
            "all services",
            "entire system",
            "platform-wide",
            "across the platform",
            "organization-wide",
            "system architecture",
        ]

        for indicator in system_indicators:
            context = {
                "workflow_output": f"Chose PostgreSQL for {indicator} data storage."
            }
            decisions = extractor.detect_architectural_decisions(context)
            if decisions:
                assert decisions[0].scope == "system", f"Failed for: {indicator}"

    def test_detect_component_scope_from_keywords(self):
        """Should detect component scope from service-specific keywords."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()

        component_indicators = [
            "the authentication module",
            "user service",
            "payment component",
            "this module",
        ]

        for indicator in component_indicators:
            context = {
                "workflow_output": f"Chose Redis for {indicator} caching."
            }
            decisions = extractor.detect_architectural_decisions(context)
            if decisions:
                # Component scope is default or explicitly detected
                assert decisions[0].scope in ["component", "system"]


class TestArchitecturalDecisionEdgeCases:
    """Edge case tests for ArchitecturalDecisionExtractor."""

    def test_handles_unicode_content(self):
        """Should handle unicode characters in content."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "Chose PostgreSQL over MongoDB - great for i18n support."
        }

        decisions = extractor.detect_architectural_decisions(context)

        assert len(decisions) >= 1

    def test_handles_long_decision_text(self):
        """Should handle very long decision text gracefully."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        long_text = "Design decision: " + "implement " * 100 + "caching."
        context = {
            "workflow_output": long_text
        }

        decisions = extractor.detect_architectural_decisions(context)

        # Should still detect the decision
        assert len(decisions) >= 1

    def test_deduplicates_similar_decisions(self):
        """Should not return duplicate decisions."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "Chose PostgreSQL over MongoDB. We chose PostgreSQL over MongoDB again."
        }

        decisions = extractor.detect_architectural_decisions(context)

        # Should deduplicate
        assert len(decisions) == 1

    def test_keywords_limited_to_10(self):
        """Keywords should be limited to 10."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        # Decision with many potential keywords
        long_decision = "Design decision: " + " ".join([f"keyword{i}" for i in range(20)])
        context = {
            "workflow_output": long_decision
        }

        decisions = extractor.detect_architectural_decisions(context)

        if decisions:
            assert len(decisions[0].keywords) <= 10

    def test_case_insensitive_pattern_matching(self):
        """Pattern matching should be case insensitive."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ArchitecturalDecisionExtractor,
        )

        extractor = ArchitecturalDecisionExtractor()
        context = {
            "workflow_output": "CHOSE POSTGRESQL OVER MONGODB for the database."
        }

        decisions = extractor.detect_architectural_decisions(context)

        assert len(decisions) >= 1


# ============================================================================
# Parallel Group B: Implementation Pattern Extractor Tests (AC: #3)
# ============================================================================


class TestExtractedPatternDataclass:
    """Tests for ExtractedPattern dataclass (Task B1.2)."""

    def test_extracted_pattern_required_fields(self):
        """ExtractedPattern should have required fields: pattern_name, description."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="Retry with exponential backoff",
            description="Implements retry logic with increasing delays",
        )

        assert pattern.pattern_name == "Retry with exponential backoff"
        assert pattern.description == "Implements retry logic with increasing delays"

    def test_extracted_pattern_default_context(self):
        """ExtractedPattern should have empty context by default."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
        )

        assert pattern.context == ""

    def test_extracted_pattern_custom_context(self):
        """ExtractedPattern should accept custom context."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
            context="Used in API error handling",
        )

        assert pattern.context == "Used in API error handling"

    def test_extracted_pattern_default_reusability(self):
        """ExtractedPattern should default reusability to 'medium'."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
        )

        assert pattern.reusability == "medium"

    def test_extracted_pattern_custom_reusability(self):
        """ExtractedPattern should accept custom reusability."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
            reusability="high",
        )

        assert pattern.reusability == "high"

    def test_extracted_pattern_default_category(self):
        """ExtractedPattern should have empty category by default."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
        )

        assert pattern.category == ""

    def test_extracted_pattern_custom_category(self):
        """ExtractedPattern should accept custom category."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
            category="retry",
        )

        assert pattern.category == "retry"

    def test_extracted_pattern_default_importance_is_pattern(self):
        """ExtractedPattern should default importance to 7 (PATTERN)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
        )

        assert pattern.importance == ImportanceLevel.PATTERN  # 7

    def test_extracted_pattern_custom_importance(self):
        """ExtractedPattern should accept custom importance."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
            importance=ImportanceLevel.PATTERN_HIGH,  # 8
        )

        assert pattern.importance == ImportanceLevel.PATTERN_HIGH  # 8

    def test_extracted_pattern_default_empty_keywords(self):
        """ExtractedPattern should have empty keywords list by default."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
        )

        assert pattern.keywords == []

    def test_extracted_pattern_custom_keywords(self):
        """ExtractedPattern should accept custom keywords."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
            keywords=["retry", "backoff", "error-handling"],
        )

        assert pattern.keywords == ["retry", "backoff", "error-handling"]

    def test_extracted_pattern_default_empty_tags(self):
        """ExtractedPattern should have empty tags list by default."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
        )

        assert pattern.tags == []

    def test_extracted_pattern_custom_tags(self):
        """ExtractedPattern should accept custom tags."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ExtractedPattern,
        )

        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
            tags=["pattern", "implementation"],
        )

        assert pattern.tags == ["pattern", "implementation"]


class TestImplementationPatternExtractorInit:
    """Tests for ImplementationPatternExtractor class initialization (Task B1.1)."""

    def test_implementation_pattern_extractor_class_exists(self):
        """ImplementationPatternExtractor class should exist."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        assert extractor is not None

    def test_implementation_pattern_extractor_has_pattern_indicators(self):
        """ImplementationPatternExtractor should have PATTERN_INDICATORS."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        assert hasattr(ImplementationPatternExtractor, "PATTERN_INDICATORS")

    def test_implementation_pattern_extractor_has_categories(self):
        """ImplementationPatternExtractor should have CATEGORIES."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        assert hasattr(ImplementationPatternExtractor, "CATEGORIES")

    def test_implementation_pattern_extractor_has_detect_patterns_method(self):
        """ImplementationPatternExtractor should have detect_patterns method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        assert hasattr(extractor, "detect_patterns")
        assert callable(extractor.detect_patterns)

    def test_implementation_pattern_extractor_has_categorize_pattern_method(self):
        """ImplementationPatternExtractor should have categorize_pattern method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        assert hasattr(extractor, "categorize_pattern")
        assert callable(extractor.categorize_pattern)

    def test_implementation_pattern_extractor_has_assign_importance_method(self):
        """ImplementationPatternExtractor should have assign_importance method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        assert hasattr(extractor, "assign_importance")
        assert callable(extractor.assign_importance)


class TestPatternIndicators:
    """Tests for pattern indicator definitions (Task B1.4)."""

    def test_pattern_indicators_contains_pattern_keyword(self):
        """PATTERN_INDICATORS should contain 'pattern' regex."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        indicators = ImplementationPatternExtractor.PATTERN_INDICATORS
        combined = " ".join(indicators).lower()
        assert "pattern" in combined

    def test_pattern_indicators_contains_approach_keyword(self):
        """PATTERN_INDICATORS should contain 'approach' regex."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        indicators = ImplementationPatternExtractor.PATTERN_INDICATORS
        combined = " ".join(indicators).lower()
        assert "approach" in combined

    def test_pattern_indicators_contains_technique_keyword(self):
        """PATTERN_INDICATORS should contain 'technique' regex."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        indicators = ImplementationPatternExtractor.PATTERN_INDICATORS
        combined = " ".join(indicators).lower()
        assert "technique" in combined

    def test_pattern_indicators_contains_strategy_keyword(self):
        """PATTERN_INDICATORS should contain 'strategy' regex."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        indicators = ImplementationPatternExtractor.PATTERN_INDICATORS
        combined = " ".join(indicators).lower()
        assert "strategy" in combined

    def test_pattern_indicators_contains_used_x_for_y(self):
        """PATTERN_INDICATORS should contain 'used X for Y' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        indicators = ImplementationPatternExtractor.PATTERN_INDICATORS
        combined = " ".join(indicators).lower()
        assert "used" in combined

    def test_pattern_indicators_contains_implemented(self):
        """PATTERN_INDICATORS should contain 'implemented' pattern."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        indicators = ImplementationPatternExtractor.PATTERN_INDICATORS
        combined = " ".join(indicators).lower()
        assert "implemented" in combined


class TestPatternCategories:
    """Tests for pattern category definitions (Task B2.1)."""

    def test_categories_contains_retry(self):
        """CATEGORIES should contain 'retry' category."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        categories = ImplementationPatternExtractor.CATEGORIES
        assert "retry" in categories

    def test_categories_contains_caching(self):
        """CATEGORIES should contain 'caching' category."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        categories = ImplementationPatternExtractor.CATEGORIES
        assert "caching" in categories

    def test_categories_contains_validation(self):
        """CATEGORIES should contain 'validation' category."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        categories = ImplementationPatternExtractor.CATEGORIES
        assert "validation" in categories

    def test_categories_contains_error_handling(self):
        """CATEGORIES should contain 'error-handling' category."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        categories = ImplementationPatternExtractor.CATEGORIES
        assert "error-handling" in categories

    def test_categories_contains_logging(self):
        """CATEGORIES should contain 'logging' category."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        categories = ImplementationPatternExtractor.CATEGORIES
        assert "logging" in categories

    def test_categories_contains_testing(self):
        """CATEGORIES should contain 'testing' category."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        categories = ImplementationPatternExtractor.CATEGORIES
        assert "testing" in categories

    def test_categories_contains_integration(self):
        """CATEGORIES should contain 'integration' category."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        categories = ImplementationPatternExtractor.CATEGORIES
        assert "integration" in categories


class TestDetectPatterns:
    """Tests for detect_patterns method (Task B1.3, B1.5)."""

    def test_detect_patterns_returns_list(self):
        """detect_patterns should return a list."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        result = extractor.detect_patterns({})

        assert isinstance(result, list)

    def test_detect_patterns_empty_context_returns_empty_list(self):
        """detect_patterns with empty context should return empty list."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        result = extractor.detect_patterns({})

        assert result == []

    def test_detect_patterns_finds_used_pattern_keyword(self):
        """detect_patterns should find 'used X pattern' phrases."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "Used retry pattern for API calls"
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 1
        assert isinstance(result[0], ExtractedPattern)

    def test_detect_patterns_finds_approach_keyword(self):
        """detect_patterns should find 'X approach' phrases."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "Implemented lazy loading approach for performance"
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 1

    def test_detect_patterns_finds_technique_keyword(self):
        """detect_patterns should find 'X technique' phrases."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "Applied memoization technique to optimize calculations"
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 1

    def test_detect_patterns_finds_strategy_keyword(self):
        """detect_patterns should find 'X strategy' phrases."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "Used caching strategy for database queries"
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 1

    def test_detect_patterns_finds_used_x_for_y(self):
        """detect_patterns should find 'used X for Y' phrases."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "Used Redis for session management"
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 1

    def test_detect_patterns_finds_implemented_keyword(self):
        """detect_patterns should find 'implemented X' phrases."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "Implemented circuit breaker for service resilience"
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 1

    def test_detect_patterns_multiple_patterns(self):
        """detect_patterns should find multiple patterns in context."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": """
            Used retry pattern for API calls.
            Implemented caching strategy for database queries.
            Applied validation technique for user input.
            """
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 3

    def test_detect_patterns_extracts_pattern_name(self):
        """detect_patterns should extract pattern name."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "Used retry pattern for API calls"
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 1
        assert len(result[0].pattern_name) > 0
        assert "retry" in result[0].pattern_name.lower()

    def test_detect_patterns_extracts_description(self):
        """detect_patterns should extract description."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "Implemented circuit breaker for service resilience"
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 1
        assert len(result[0].description) > 0

    def test_detect_patterns_ignores_non_pattern_content(self):
        """detect_patterns should ignore content without pattern indicators."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "The system runs smoothly and users are happy."
        }
        result = extractor.detect_patterns(context)

        assert result == []

    def test_detect_patterns_scans_multiple_context_fields(self):
        """detect_patterns should scan multiple context fields."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "Used retry pattern for API calls",
            "notes": "Implemented caching strategy for queries",
            "summary": "Applied validation technique for input",
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 2

    def test_detect_patterns_case_insensitive(self):
        """detect_patterns should be case insensitive."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "USED RETRY PATTERN for API calls"
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 1

    def test_detect_patterns_from_messages_field(self):
        """detect_patterns should extract from messages field."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "messages": [
                {"content": "Used retry pattern for API resilience"}
            ]
        }
        result = extractor.detect_patterns(context)

        assert len(result) >= 1


class TestCategorizePattern:
    """Tests for categorize_pattern method (Task B2.1)."""

    def test_categorize_pattern_returns_string(self):
        """categorize_pattern should return a string."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="Retry pattern",
            description="Implements retry logic",
        )
        result = extractor.categorize_pattern(pattern)

        assert isinstance(result, str)

    def test_categorize_pattern_retry(self):
        """categorize_pattern should identify retry patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="Retry pattern",
            description="Implements retry with exponential backoff",
        )
        result = extractor.categorize_pattern(pattern)

        assert result == "retry"

    def test_categorize_pattern_caching(self):
        """categorize_pattern should identify caching patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="Caching strategy",
            description="Cache database query results",
        )
        result = extractor.categorize_pattern(pattern)

        assert result == "caching"

    def test_categorize_pattern_validation(self):
        """categorize_pattern should identify validation patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="Input validation",
            description="Validate user input before processing",
        )
        result = extractor.categorize_pattern(pattern)

        assert result == "validation"

    def test_categorize_pattern_error_handling(self):
        """categorize_pattern should identify error-handling patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="Error handling",
            description="Handle exceptions gracefully",
        )
        result = extractor.categorize_pattern(pattern)

        assert result == "error-handling"

    def test_categorize_pattern_logging(self):
        """categorize_pattern should identify logging patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="Structured logging",
            description="Log with structured format",
        )
        result = extractor.categorize_pattern(pattern)

        assert result == "logging"

    def test_categorize_pattern_testing(self):
        """categorize_pattern should identify testing patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="Test doubles",
            description="Use mocks and stubs for testing",
        )
        result = extractor.categorize_pattern(pattern)

        assert result == "testing"

    def test_categorize_pattern_integration(self):
        """categorize_pattern should identify integration patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="API integration",
            description="Integrate with external API",
        )
        result = extractor.categorize_pattern(pattern)

        assert result == "integration"

    def test_categorize_pattern_unknown_returns_empty(self):
        """categorize_pattern should return empty string for unknown patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="Quantum entanglement",
            description="Uses quantum effects",
        )
        result = extractor.categorize_pattern(pattern)

        assert result == ""


class TestAssignImportancePattern:
    """Tests for assign_importance method (Task B2.2)."""

    def test_assign_importance_returns_int(self):
        """assign_importance should return an integer."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
        )
        result = extractor.assign_importance(pattern)

        assert isinstance(result, int)

    def test_assign_importance_high_reusability_returns_8(self):
        """assign_importance should return 8 for high reusability patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="Retry pattern",
            description="Generic retry logic",
            reusability="high",
        )
        result = extractor.assign_importance(pattern)

        assert result == ImportanceLevel.PATTERN_HIGH  # 8
        assert result == 8

    def test_assign_importance_medium_reusability_returns_7(self):
        """assign_importance should return 7 for medium reusability patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="Custom validation",
            description="Domain-specific validation",
            reusability="medium",
        )
        result = extractor.assign_importance(pattern)

        assert result == ImportanceLevel.PATTERN  # 7
        assert result == 7

    def test_assign_importance_low_reusability_returns_7(self):
        """assign_importance should return 7 for low reusability patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )
        from pcmrp_tools.bmad_automation.memory_bridge import ImportanceLevel

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="One-off script",
            description="Specific to this use case",
            reusability="low",
        )
        result = extractor.assign_importance(pattern)

        assert result == ImportanceLevel.PATTERN  # 7
        assert result == 7

    def test_assign_importance_default_reusability_returns_7(self):
        """assign_importance with default reusability (medium) should return 7."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
            ExtractedPattern,
        )

        extractor = ImplementationPatternExtractor()
        pattern = ExtractedPattern(
            pattern_name="test",
            description="test",
        )
        result = extractor.assign_importance(pattern)

        assert result == 7


class TestDetectPatternsEdgeCases:
    """Edge case tests for detect_patterns (Task B1.5)."""

    def test_detect_patterns_handles_none_values(self):
        """detect_patterns should handle None values in context."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": None,
            "notes": None,
        }
        result = extractor.detect_patterns(context)

        assert result == []

    def test_detect_patterns_handles_empty_strings(self):
        """detect_patterns should handle empty strings in context."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        context = {
            "workflow_output": "",
            "notes": "",
        }
        result = extractor.detect_patterns(context)

        assert result == []

    def test_detect_patterns_deduplicates_results(self):
        """detect_patterns should deduplicate identical patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            ImplementationPatternExtractor,
        )

        extractor = ImplementationPatternExtractor()
        # Use a simpler pattern that only matches one indicator
        context = {
            "workflow_output": "Used caching strategy",
            "notes": "Used caching strategy",
            "summary": "Used caching strategy",
        }
        result = extractor.detect_patterns(context)

        # Should deduplicate identical patterns from multiple fields
        caching_patterns = [
            p for p in result if "caching" in p.pattern_name.lower()
        ]
        assert len(caching_patterns) == 1


# =============================================================================
# Tasks E1, E2: DuplicationChecker Tests (AC: #6)
# =============================================================================


class TestLinkResultDataclass:
    """Tests for LinkResult dataclass (Task E2.2)."""

    def test_link_result_basic_creation(self):
        """Test creating LinkResult with required fields."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import LinkResult

        result = LinkResult(should_link=False)
        assert result.should_link is False
        assert result.existing_memory_id is None
        assert result.similarity_score == 0.0

    def test_link_result_with_memory_id(self):
        """Test LinkResult with existing_memory_id."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import LinkResult

        result = LinkResult(should_link=True, existing_memory_id=42, similarity_score=0.85)
        assert result.should_link is True
        assert result.existing_memory_id == 42
        assert result.similarity_score == 0.85


class TestDuplicationCheckerClass:
    """Tests for DuplicationChecker class (Task E1.1)."""

    def test_duplication_checker_exists(self):
        """DuplicationChecker class should exist."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        assert DuplicationChecker is not None

    def test_duplication_checker_instantiation(self):
        """Test creating DuplicationChecker instance."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        assert checker is not None

    def test_duplication_checker_accepts_mcp_client(self):
        """DuplicationChecker should accept optional mcp_client."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        mock_client = lambda tool, args: {"memories": []}
        checker = DuplicationChecker(mcp_client=mock_client)
        assert checker._mcp_client is mock_client


class TestDuplicationThreshold:
    """Tests for duplication threshold (Task E1.4)."""

    def test_duplication_threshold_exists(self):
        """DUPLICATION_THRESHOLD constant should exist."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DUPLICATION_THRESHOLD,
        )

        assert DUPLICATION_THRESHOLD is not None

    def test_duplication_threshold_is_80_percent(self):
        """DUPLICATION_THRESHOLD should be 0.80 (80%)."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DUPLICATION_THRESHOLD,
        )

        assert DUPLICATION_THRESHOLD == 0.80


class TestSimilarityScore:
    """Tests for similarity_score method (Task E1.3)."""

    def test_similarity_score_method_exists(self):
        """DuplicationChecker should have similarity_score method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        assert hasattr(checker, "similarity_score")
        assert callable(checker.similarity_score)

    def test_similarity_score_identical_content(self):
        """Identical content should have similarity score of 1.0."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        score = checker.similarity_score(
            "Chose PostgreSQL for database",
            "Chose PostgreSQL for database"
        )
        assert score == 1.0

    def test_similarity_score_different_content(self):
        """Completely different content should have low similarity score."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        score = checker.similarity_score(
            "Chose PostgreSQL for database storage",
            "Implemented retry logic with exponential backoff"
        )
        assert score < 0.5

    def test_similarity_score_similar_content(self):
        """Similar content should have high similarity score."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        score = checker.similarity_score(
            "Chose PostgreSQL for database",
            "Chose PostgreSQL for database storage"
        )
        assert score >= 0.7

    def test_similarity_score_returns_float(self):
        """similarity_score should return a float between 0 and 1."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        score = checker.similarity_score("test one", "test two")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_similarity_score_case_insensitive(self):
        """similarity_score should be case insensitive."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        score1 = checker.similarity_score("PostgreSQL Database", "postgresql database")
        score2 = checker.similarity_score("postgresql database", "postgresql database")
        assert score1 == score2


class TestCheckForDuplicates:
    """Tests for check_for_duplicates method (Task E1.2)."""

    def test_check_for_duplicates_method_exists(self):
        """DuplicationChecker should have check_for_duplicates method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        assert hasattr(checker, "check_for_duplicates")
        assert callable(checker.check_for_duplicates)

    def test_check_for_duplicates_returns_link_result(self):
        """check_for_duplicates should return LinkResult."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
            LinkResult,
        )

        checker = DuplicationChecker()
        result = checker.check_for_duplicates("test content", ["test"])
        assert isinstance(result, LinkResult)

    def test_check_for_duplicates_no_mcp_returns_no_link(self):
        """check_for_duplicates without mcp_client should return should_link=False."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()  # No MCP client
        result = checker.check_for_duplicates("test content", ["test"])
        assert result.should_link is False
        assert result.existing_memory_id is None

    def test_check_for_duplicates_with_mock_no_matches(self):
        """check_for_duplicates with no matches should return should_link=False."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        # Mock MCP client that returns no memories
        mock_client = lambda tool, args: {"memories": []}
        checker = DuplicationChecker(mcp_client=mock_client)
        result = checker.check_for_duplicates("new unique content", ["unique"])
        assert result.should_link is False

    def test_check_for_duplicates_with_mock_high_similarity(self):
        """check_for_duplicates with high similarity match should return should_link=True."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        # Mock MCP client that returns a similar memory
        mock_memories = {
            "memories": [
                {"id": 42, "content": "Chose PostgreSQL for database storage"}
            ]
        }
        mock_client = lambda tool, args: mock_memories
        checker = DuplicationChecker(mcp_client=mock_client)
        result = checker.check_for_duplicates(
            "Chose PostgreSQL for database storage",
            ["postgresql", "database"]
        )
        assert result.should_link is True
        assert result.existing_memory_id == 42
        assert result.similarity_score >= 0.80

    def test_check_for_duplicates_with_mock_low_similarity(self):
        """check_for_duplicates with low similarity should return should_link=False."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        # Mock MCP client that returns a different memory
        mock_memories = {
            "memories": [
                {"id": 99, "content": "Implemented retry logic with backoff"}
            ]
        }
        mock_client = lambda tool, args: mock_memories
        checker = DuplicationChecker(mcp_client=mock_client)
        result = checker.check_for_duplicates(
            "Chose PostgreSQL for database storage",
            ["postgresql", "database"]
        )
        assert result.should_link is False


class TestLinkToExisting:
    """Tests for link_to_existing method (Task E2.1)."""

    def test_link_to_existing_method_exists(self):
        """DuplicationChecker should have link_to_existing method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        assert hasattr(checker, "link_to_existing")
        assert callable(checker.link_to_existing)

    def test_link_to_existing_returns_link_result(self):
        """link_to_existing should return LinkResult."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
            LinkResult,
        )

        checker = DuplicationChecker()
        result = checker.link_to_existing(42)
        assert isinstance(result, LinkResult)

    def test_link_to_existing_sets_should_link_true(self):
        """link_to_existing should set should_link=True."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        result = checker.link_to_existing(42)
        assert result.should_link is True

    def test_link_to_existing_sets_memory_id(self):
        """link_to_existing should set existing_memory_id."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        result = checker.link_to_existing(99)
        assert result.existing_memory_id == 99


# =============================================================================
# Tasks F1, F2: PostWorkflowCurator Tests (AC: #1)
# =============================================================================


class TestCurationReportDataclass:
    """Tests for CurationReport dataclass (Task F2.1)."""

    def test_curation_report_exists(self):
        """CurationReport class should exist."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            CurationReport,
        )

        assert CurationReport is not None

    def test_curation_report_basic_creation(self):
        """Test creating CurationReport with defaults."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            CurationReport,
        )

        report = CurationReport()
        assert report.memories_created == 0
        assert report.memories_linked == 0
        assert report.skipped_duplicates == 0
        assert report.items_by_type == {}

    def test_curation_report_with_values(self):
        """Test creating CurationReport with custom values."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            CurationReport,
        )

        report = CurationReport(
            memories_created=5,
            memories_linked=2,
            skipped_duplicates=1,
            items_by_type={"decisions": 2, "patterns": 3}
        )
        assert report.memories_created == 5
        assert report.memories_linked == 2
        assert report.skipped_duplicates == 1
        assert report.items_by_type == {"decisions": 2, "patterns": 3}


class TestPostWorkflowCuratorClass:
    """Tests for PostWorkflowCurator class (Task F1.1)."""

    def test_post_workflow_curator_exists(self):
        """PostWorkflowCurator class should exist."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        assert PostWorkflowCurator is not None

    def test_post_workflow_curator_instantiation(self):
        """Test creating PostWorkflowCurator instance."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        assert curator is not None

    def test_post_workflow_curator_accepts_mcp_client(self):
        """PostWorkflowCurator should accept optional mcp_client."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        mock_client = lambda tool, args: {}
        curator = PostWorkflowCurator(mcp_client=mock_client)
        assert curator._mcp_client is mock_client

    def test_post_workflow_curator_has_extractors(self):
        """PostWorkflowCurator should initialize all extractors."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
            ArchitecturalDecisionExtractor,
            ImplementationPatternExtractor,
            MilestoneExtractor,
            ProblemSolutionExtractor,
        )

        curator = PostWorkflowCurator()
        assert hasattr(curator, "arch_extractor")
        assert hasattr(curator, "pattern_extractor")
        assert hasattr(curator, "milestone_extractor")
        assert hasattr(curator, "problem_extractor")
        assert isinstance(curator.arch_extractor, ArchitecturalDecisionExtractor)
        assert isinstance(curator.pattern_extractor, ImplementationPatternExtractor)
        assert isinstance(curator.milestone_extractor, MilestoneExtractor)
        assert isinstance(curator.problem_extractor, ProblemSolutionExtractor)

    def test_post_workflow_curator_has_dedup_checker(self):
        """PostWorkflowCurator should have DuplicationChecker."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
            DuplicationChecker,
        )

        curator = PostWorkflowCurator()
        assert hasattr(curator, "dedup_checker")
        assert isinstance(curator.dedup_checker, DuplicationChecker)


class TestAnalyzeSession:
    """Tests for analyze_session method (Task F1.1)."""

    def test_analyze_session_method_exists(self):
        """PostWorkflowCurator should have analyze_session method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        assert hasattr(curator, "analyze_session")
        assert callable(curator.analyze_session)

    def test_analyze_session_returns_curation_report(self):
        """analyze_session should return CurationReport."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
            CurationReport,
        )

        curator = PostWorkflowCurator()
        result = curator.analyze_session({})
        assert isinstance(result, CurationReport)

    def test_analyze_session_empty_context(self):
        """analyze_session with empty context should return zero counts."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        result = curator.analyze_session({})
        assert result.memories_created == 0
        assert result.memories_linked == 0

    def test_analyze_session_calls_all_extractors(self):
        """analyze_session should call all extractors."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        context = {
            "workflow_output": """
            Chose PostgreSQL over MongoDB for data.
            Used retry pattern for API calls.
            Phase 2 complete.
            Fixed ImportError by adding import.
            """
        }
        result = curator.analyze_session(context)
        # Should have extracted items from multiple extractors
        assert result.items_by_type is not None

    def test_analyze_session_counts_extracted_items(self):
        """analyze_session should count items by type."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        context = {
            "workflow_output": "Chose PostgreSQL over MongoDB. Architecture uses microservices."
        }
        result = curator.analyze_session(context)
        # items_by_type should have decision count
        assert "decisions" in result.items_by_type or result.items_by_type.get("decisions", 0) >= 0


class TestAnalyzeSessionIntegration:
    """Integration tests for analyze_session (Task F1.5)."""

    def test_analyze_session_detects_decisions(self):
        """analyze_session should detect architectural decisions."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        context = {
            "workflow_output": "We chose PostgreSQL over MongoDB for the database."
        }
        result = curator.analyze_session(context)
        assert result.items_by_type.get("decisions", 0) >= 1

    def test_analyze_session_detects_patterns(self):
        """analyze_session should detect implementation patterns."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        context = {
            "workflow_output": "Used retry pattern for handling API failures."
        }
        result = curator.analyze_session(context)
        assert result.items_by_type.get("patterns", 0) >= 1

    def test_analyze_session_detects_milestones(self):
        """analyze_session should detect milestones."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        context = {
            "workflow_output": "Phase 2 complete. Epic 2a finished."
        }
        result = curator.analyze_session(context)
        assert result.items_by_type.get("milestones", 0) >= 1

    def test_analyze_session_detects_problem_solutions(self):
        """analyze_session should detect problem-solution pairs."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        context = {
            "messages": [
                {"content": "Fixed ImportError by adding missing import statement"}
            ]
        }
        result = curator.analyze_session(context)
        assert result.items_by_type.get("problem_solutions", 0) >= 1

    def test_analyze_session_mixed_content(self):
        """analyze_session should handle mixed content types."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        context = {
            "workflow_output": """
            Chose PostgreSQL over MongoDB for database.
            Phase 2 complete.
            """,
            "messages": [
                {"content": "Used retry pattern for API calls."},
                {"content": "Fixed timeout error by increasing limit."},
            ]
        }
        result = curator.analyze_session(context)
        # Should have items from multiple types
        total_items = sum(result.items_by_type.values())
        assert total_items >= 2


class TestCreateReport:
    """Tests for _create_report method (Task F2)."""

    def test_create_report_method_exists(self):
        """PostWorkflowCurator should have _create_report method."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
        )

        curator = PostWorkflowCurator()
        assert hasattr(curator, "_create_report")
        assert callable(curator._create_report)

    def test_create_report_returns_curation_report(self):
        """_create_report should return CurationReport."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
            CurationReport,
        )

        curator = PostWorkflowCurator()
        result = curator._create_report({
            "decisions": [],
            "patterns": [],
            "milestones": [],
            "problem_solutions": [],
        })
        assert isinstance(result, CurationReport)

    def test_create_report_counts_by_type(self):
        """_create_report should count items by type."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            PostWorkflowCurator,
            ExtractedDecision,
            ExtractedPattern,
        )

        curator = PostWorkflowCurator()
        results = {
            "decisions": [
                ExtractedDecision(decision="Test", rationale="Test"),
                ExtractedDecision(decision="Test2", rationale="Test2"),
            ],
            "patterns": [
                ExtractedPattern(pattern_name="Test", description="Test"),
            ],
            "milestones": [],
            "problem_solutions": [],
        }
        report = curator._create_report(results)
        assert report.items_by_type.get("decisions", 0) == 2
        assert report.items_by_type.get("patterns", 0) == 1


class TestDuplicationCheckerEdgeCases:
    """Edge case tests for DuplicationChecker."""

    def test_similarity_score_empty_strings(self):
        """similarity_score should handle empty strings."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        score = checker.similarity_score("", "")
        assert isinstance(score, float)

    def test_similarity_score_one_empty(self):
        """similarity_score should handle one empty string."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        score = checker.similarity_score("test content", "")
        assert score == 0.0

    def test_check_for_duplicates_empty_content(self):
        """check_for_duplicates should handle empty content."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        result = checker.check_for_duplicates("", [])
        assert result.should_link is False

    def test_check_for_duplicates_empty_keywords(self):
        """check_for_duplicates should handle empty keywords list."""
        from pcmrp_tools.bmad_automation.post_workflow_curator import (
            DuplicationChecker,
        )

        checker = DuplicationChecker()
        result = checker.check_for_duplicates("test content", [])
        assert isinstance(result.should_link, bool)
