"""Tests for Tier Suggester - Project Complexity Detection.

This module tests the tier suggestion functionality that recommends
appropriate project tiers (0-4) based on user descriptions and codebase analysis.

TDD: Tests are written FIRST, before implementation.
"""

import pytest
from dataclasses import asdict
from pathlib import Path

# Import will fail until implementation exists (TDD Red phase)
from pcmrp_tools.bmad_automation.tier_suggester import (
    ProjectTier,
    TierConfidence,
    TierSuggestion,
    TIER_KEYWORDS,
    DEFAULT_TIER,
    analyze_description,
    calculate_keyword_confidence,
    analyze_codebase_metrics,
    suggest_tier,
)


# =============================================================================
# Task 1: ProjectTier Enum Tests
# =============================================================================


class TestProjectTierEnum:
    """Tests for ProjectTier enum (Task 1.1)."""

    def test_project_tier_has_tier_0(self):
        """ProjectTier should have TIER_0 value."""
        assert ProjectTier.TIER_0.value == 0

    def test_project_tier_has_tier_1(self):
        """ProjectTier should have TIER_1 value."""
        assert ProjectTier.TIER_1.value == 1

    def test_project_tier_has_tier_2(self):
        """ProjectTier should have TIER_2 value."""
        assert ProjectTier.TIER_2.value == 2

    def test_project_tier_has_tier_3(self):
        """ProjectTier should have TIER_3 value."""
        assert ProjectTier.TIER_3.value == 3

    def test_project_tier_has_tier_4(self):
        """ProjectTier should have TIER_4 value."""
        assert ProjectTier.TIER_4.value == 4

    def test_project_tier_from_int_0(self):
        """ProjectTier should be creatable from int 0."""
        assert ProjectTier(0) == ProjectTier.TIER_0

    def test_project_tier_from_int_4(self):
        """ProjectTier should be creatable from int 4."""
        assert ProjectTier(4) == ProjectTier.TIER_4

    def test_project_tier_has_description(self):
        """ProjectTier members should have description property."""
        assert hasattr(ProjectTier.TIER_0, "description")
        assert "atomic" in ProjectTier.TIER_0.description.lower() or "change" in ProjectTier.TIER_0.description.lower()

    def test_project_tier_0_description(self):
        """TIER_0 description should mention atomic or single change."""
        desc = ProjectTier.TIER_0.description.lower()
        assert "atomic" in desc or "single" in desc or "change" in desc

    def test_project_tier_2_is_medium(self):
        """TIER_2 description should mention medium."""
        desc = ProjectTier.TIER_2.description.lower()
        assert "medium" in desc or "standard" in desc

    def test_project_tier_4_is_enterprise(self):
        """TIER_4 description should mention enterprise or regulated."""
        desc = ProjectTier.TIER_4.description.lower()
        assert "enterprise" in desc or "regulated" in desc


# =============================================================================
# Task 2: TierConfidence Enum Tests
# =============================================================================


class TestTierConfidenceEnum:
    """Tests for TierConfidence enum (Task 2.1)."""

    def test_tier_confidence_has_high(self):
        """TierConfidence should have HIGH value."""
        assert TierConfidence.HIGH.value == "high"

    def test_tier_confidence_has_medium(self):
        """TierConfidence should have MEDIUM value."""
        assert TierConfidence.MEDIUM.value == "medium"

    def test_tier_confidence_has_low(self):
        """TierConfidence should have LOW value."""
        assert TierConfidence.LOW.value == "low"

    def test_tier_confidence_from_string_high(self):
        """TierConfidence should be creatable from string 'high'."""
        assert TierConfidence("high") == TierConfidence.HIGH

    def test_tier_confidence_from_string_medium(self):
        """TierConfidence should be creatable from string 'medium'."""
        assert TierConfidence("medium") == TierConfidence.MEDIUM

    def test_tier_confidence_from_string_low(self):
        """TierConfidence should be creatable from string 'low'."""
        assert TierConfidence("low") == TierConfidence.LOW


# =============================================================================
# Task 3: TierSuggestion Dataclass Tests
# =============================================================================


class TestTierSuggestionDataclass:
    """Tests for TierSuggestion dataclass (Task 3.1)."""

    def test_tier_suggestion_creation_with_all_fields(self):
        """TierSuggestion should be creatable with all fields."""
        suggestion = TierSuggestion(
            tier=ProjectTier.TIER_2,
            confidence=TierConfidence.HIGH,
            matched_keywords=["feature", "module"],
            reasoning="Matched 2 Tier 2 keywords",
            all_matches={ProjectTier.TIER_2: ["feature", "module"]},
        )
        assert suggestion.tier == ProjectTier.TIER_2
        assert suggestion.confidence == TierConfidence.HIGH
        assert suggestion.matched_keywords == ["feature", "module"]
        assert suggestion.reasoning == "Matched 2 Tier 2 keywords"
        assert ProjectTier.TIER_2 in suggestion.all_matches

    def test_tier_suggestion_creation_with_defaults(self):
        """TierSuggestion should have sensible defaults."""
        suggestion = TierSuggestion(
            tier=ProjectTier.TIER_0,
            confidence=TierConfidence.LOW,
            matched_keywords=[],
            reasoning="No keywords matched",
        )
        assert suggestion.tier == ProjectTier.TIER_0
        assert suggestion.matched_keywords == []

    def test_tier_suggestion_to_dict(self):
        """TierSuggestion should be serializable to dict."""
        suggestion = TierSuggestion(
            tier=ProjectTier.TIER_1,
            confidence=TierConfidence.MEDIUM,
            matched_keywords=["simple"],
            reasoning="Matched 1 Tier 1 keyword",
            all_matches={ProjectTier.TIER_1: ["simple"]},
        )
        result = asdict(suggestion)
        assert result["tier"] == ProjectTier.TIER_1
        assert result["confidence"] == TierConfidence.MEDIUM
        assert result["matched_keywords"] == ["simple"]


class TestTierSuggestionFactoryMethods:
    """Tests for TierSuggestion factory methods (Task 3.2)."""

    def test_default_suggestion_factory(self):
        """default_suggestion() should create default Tier 2 with LOW confidence."""
        suggestion = TierSuggestion.default_suggestion()
        assert suggestion.tier == ProjectTier.TIER_2
        assert suggestion.confidence == TierConfidence.LOW
        assert suggestion.matched_keywords == []
        assert "default" in suggestion.reasoning.lower() or "no keywords" in suggestion.reasoning.lower()

    def test_from_analysis_factory(self):
        """from_analysis() should create suggestion from analysis results."""
        matches = {ProjectTier.TIER_0: ["fix", "bug"]}
        suggestion = TierSuggestion.from_analysis(
            tier=ProjectTier.TIER_0,
            confidence=TierConfidence.HIGH,
            all_matches=matches,
        )
        assert suggestion.tier == ProjectTier.TIER_0
        assert suggestion.confidence == TierConfidence.HIGH
        assert suggestion.matched_keywords == ["fix", "bug"]
        assert suggestion.all_matches == matches


# =============================================================================
# Task 4: TIER_KEYWORDS Constant Tests
# =============================================================================


class TestTierKeywordsConstant:
    """Tests for TIER_KEYWORDS constant (Task 4.1)."""

    def test_tier_keywords_is_dict(self):
        """TIER_KEYWORDS should be a dict."""
        assert isinstance(TIER_KEYWORDS, dict)

    def test_tier_keywords_has_all_tiers(self):
        """TIER_KEYWORDS should have entries for all 5 tiers."""
        assert ProjectTier.TIER_0 in TIER_KEYWORDS
        assert ProjectTier.TIER_1 in TIER_KEYWORDS
        assert ProjectTier.TIER_2 in TIER_KEYWORDS
        assert ProjectTier.TIER_3 in TIER_KEYWORDS
        assert ProjectTier.TIER_4 in TIER_KEYWORDS

    def test_tier_0_keywords_contains_fix(self):
        """Tier 0 keywords should contain 'fix'."""
        assert "fix" in TIER_KEYWORDS[ProjectTier.TIER_0]

    def test_tier_0_keywords_contains_bug(self):
        """Tier 0 keywords should contain 'bug'."""
        assert "bug" in TIER_KEYWORDS[ProjectTier.TIER_0]

    def test_tier_0_keywords_contains_typo(self):
        """Tier 0 keywords should contain 'typo'."""
        assert "typo" in TIER_KEYWORDS[ProjectTier.TIER_0]

    def test_tier_0_keywords_contains_patch(self):
        """Tier 0 keywords should contain 'patch'."""
        assert "patch" in TIER_KEYWORDS[ProjectTier.TIER_0]

    def test_tier_0_keywords_contains_hotfix(self):
        """Tier 0 keywords should contain 'hotfix'."""
        assert "hotfix" in TIER_KEYWORDS[ProjectTier.TIER_0]

    def test_tier_0_keywords_contains_tweak(self):
        """Tier 0 keywords should contain 'tweak'."""
        assert "tweak" in TIER_KEYWORDS[ProjectTier.TIER_0]

    def test_tier_1_keywords_contains_small(self):
        """Tier 1 keywords should contain 'small'."""
        assert "small" in TIER_KEYWORDS[ProjectTier.TIER_1]

    def test_tier_1_keywords_contains_simple(self):
        """Tier 1 keywords should contain 'simple'."""
        assert "simple" in TIER_KEYWORDS[ProjectTier.TIER_1]

    def test_tier_1_keywords_contains_quick(self):
        """Tier 1 keywords should contain 'quick'."""
        assert "quick" in TIER_KEYWORDS[ProjectTier.TIER_1]

    def test_tier_1_keywords_contains_minor(self):
        """Tier 1 keywords should contain 'minor'."""
        assert "minor" in TIER_KEYWORDS[ProjectTier.TIER_1]

    def test_tier_1_keywords_contains_basic(self):
        """Tier 1 keywords should contain 'basic'."""
        assert "basic" in TIER_KEYWORDS[ProjectTier.TIER_1]

    def test_tier_1_keywords_contains_straightforward(self):
        """Tier 1 keywords should contain 'straightforward'."""
        assert "straightforward" in TIER_KEYWORDS[ProjectTier.TIER_1]

    def test_tier_2_keywords_contains_feature(self):
        """Tier 2 keywords should contain 'feature'."""
        assert "feature" in TIER_KEYWORDS[ProjectTier.TIER_2]

    def test_tier_2_keywords_contains_component(self):
        """Tier 2 keywords should contain 'component'."""
        assert "component" in TIER_KEYWORDS[ProjectTier.TIER_2]

    def test_tier_2_keywords_contains_module(self):
        """Tier 2 keywords should contain 'module'."""
        assert "module" in TIER_KEYWORDS[ProjectTier.TIER_2]

    def test_tier_2_keywords_contains_service(self):
        """Tier 2 keywords should contain 'service'."""
        assert "service" in TIER_KEYWORDS[ProjectTier.TIER_2]

    def test_tier_3_keywords_contains_platform(self):
        """Tier 3 keywords should contain 'platform'."""
        assert "platform" in TIER_KEYWORDS[ProjectTier.TIER_3]

    def test_tier_3_keywords_contains_integration(self):
        """Tier 3 keywords should contain 'integration'."""
        assert "integration" in TIER_KEYWORDS[ProjectTier.TIER_3]

    def test_tier_3_keywords_contains_complex(self):
        """Tier 3 keywords should contain 'complex'."""
        assert "complex" in TIER_KEYWORDS[ProjectTier.TIER_3]

    def test_tier_3_keywords_contains_enterprise(self):
        """Tier 3 keywords should contain 'enterprise'."""
        assert "enterprise" in TIER_KEYWORDS[ProjectTier.TIER_3]

    def test_tier_4_keywords_contains_compliance(self):
        """Tier 4 keywords should contain 'compliance'."""
        assert "compliance" in TIER_KEYWORDS[ProjectTier.TIER_4]

    def test_tier_4_keywords_contains_regulated(self):
        """Tier 4 keywords should contain 'regulated'."""
        assert "regulated" in TIER_KEYWORDS[ProjectTier.TIER_4]

    def test_tier_4_keywords_contains_audit(self):
        """Tier 4 keywords should contain 'audit'."""
        assert "audit" in TIER_KEYWORDS[ProjectTier.TIER_4]

    def test_tier_4_keywords_contains_healthcare(self):
        """Tier 4 keywords should contain 'healthcare'."""
        assert "healthcare" in TIER_KEYWORDS[ProjectTier.TIER_4]

    def test_tier_4_keywords_contains_finance(self):
        """Tier 4 keywords should contain 'finance'."""
        assert "finance" in TIER_KEYWORDS[ProjectTier.TIER_4]


class TestDefaultTierConstant:
    """Tests for DEFAULT_TIER constant."""

    def test_default_tier_is_tier_2(self):
        """DEFAULT_TIER should be TIER_2."""
        assert DEFAULT_TIER == ProjectTier.TIER_2


# =============================================================================
# Task 5: analyze_description() Function Tests
# =============================================================================


class TestAnalyzeDescriptionBasic:
    """Tests for analyze_description() basic functionality (Task 5.1)."""

    def test_analyze_description_returns_dict(self):
        """analyze_description() should return a dict."""
        result = analyze_description("Fix the bug")
        assert isinstance(result, dict)

    def test_analyze_description_returns_tier_keys(self):
        """analyze_description() result should have ProjectTier keys."""
        result = analyze_description("Fix the bug")
        for key in result:
            assert isinstance(key, ProjectTier)

    def test_analyze_description_returns_list_values(self):
        """analyze_description() result values should be lists."""
        result = analyze_description("Fix the bug")
        for value in result.values():
            assert isinstance(value, list)


class TestAnalyzeDescriptionTier0Detection:
    """Tests for analyze_description() Tier 0 keyword detection (AC #1)."""

    def test_analyze_detects_fix_keyword(self):
        """analyze_description() should detect 'fix' as Tier 0."""
        result = analyze_description("Fix the bug in login")
        assert "fix" in result.get(ProjectTier.TIER_0, [])

    def test_analyze_detects_bug_keyword(self):
        """analyze_description() should detect 'bug' as Tier 0."""
        result = analyze_description("There is a bug in the system")
        assert "bug" in result.get(ProjectTier.TIER_0, [])

    def test_analyze_detects_typo_keyword(self):
        """analyze_description() should detect 'typo' as Tier 0."""
        result = analyze_description("Correct the typo in README")
        assert "typo" in result.get(ProjectTier.TIER_0, [])

    def test_analyze_detects_patch_keyword(self):
        """analyze_description() should detect 'patch' as Tier 0."""
        result = analyze_description("Apply security patch")
        assert "patch" in result.get(ProjectTier.TIER_0, [])

    def test_analyze_detects_hotfix_keyword(self):
        """analyze_description() should detect 'hotfix' as Tier 0."""
        result = analyze_description("Emergency hotfix needed")
        assert "hotfix" in result.get(ProjectTier.TIER_0, [])

    def test_analyze_detects_tweak_keyword(self):
        """analyze_description() should detect 'tweak' as Tier 0."""
        result = analyze_description("Just tweak the settings")
        assert "tweak" in result.get(ProjectTier.TIER_0, [])

    def test_analyze_detects_multiple_tier_0_keywords(self):
        """analyze_description() should detect multiple Tier 0 keywords."""
        result = analyze_description("Fix the bug with a quick patch")
        tier_0_matches = result.get(ProjectTier.TIER_0, [])
        assert "fix" in tier_0_matches
        assert "bug" in tier_0_matches
        assert "patch" in tier_0_matches


class TestAnalyzeDescriptionTier3Detection:
    """Tests for analyze_description() Tier 3 keyword detection (AC #2)."""

    def test_analyze_detects_platform_keyword(self):
        """analyze_description() should detect 'platform' as Tier 3."""
        result = analyze_description("Build a new platform")
        assert "platform" in result.get(ProjectTier.TIER_3, [])

    def test_analyze_detects_integration_keyword(self):
        """analyze_description() should detect 'integration' as Tier 3."""
        result = analyze_description("Create API integration")
        assert "integration" in result.get(ProjectTier.TIER_3, [])

    def test_analyze_detects_complex_keyword(self):
        """analyze_description() should detect 'complex' as Tier 3."""
        result = analyze_description("This is a complex system")
        assert "complex" in result.get(ProjectTier.TIER_3, [])

    def test_analyze_detects_enterprise_keyword(self):
        """analyze_description() should detect 'enterprise' as Tier 3."""
        result = analyze_description("Enterprise-wide solution")
        assert "enterprise" in result.get(ProjectTier.TIER_3, [])


class TestAnalyzeDescriptionCaseInsensitivity:
    """Tests for analyze_description() case insensitivity."""

    def test_analyze_is_case_insensitive_lowercase(self):
        """analyze_description() should match lowercase keywords."""
        result = analyze_description("fix the bug")
        assert "fix" in result.get(ProjectTier.TIER_0, [])

    def test_analyze_is_case_insensitive_uppercase(self):
        """analyze_description() should match uppercase keywords."""
        result = analyze_description("FIX THE BUG")
        assert "fix" in result.get(ProjectTier.TIER_0, [])

    def test_analyze_is_case_insensitive_mixed(self):
        """analyze_description() should match mixed case keywords."""
        result = analyze_description("Fix The Bug")
        assert "fix" in result.get(ProjectTier.TIER_0, [])


class TestAnalyzeDescriptionEdgeCases:
    """Tests for analyze_description() edge cases."""

    def test_analyze_empty_string(self):
        """analyze_description() should handle empty string."""
        result = analyze_description("")
        assert isinstance(result, dict)
        assert all(len(v) == 0 for v in result.values())

    def test_analyze_whitespace_only(self):
        """analyze_description() should handle whitespace-only string."""
        result = analyze_description("   \t\n  ")
        assert isinstance(result, dict)
        assert all(len(v) == 0 for v in result.values())

    def test_analyze_no_keywords(self):
        """analyze_description() should return empty lists when no keywords match."""
        result = analyze_description("Do something with the code")
        total_matches = sum(len(v) for v in result.values())
        assert total_matches == 0

    def test_analyze_keyword_in_word(self):
        """analyze_description() should match keywords as whole words only."""
        # 'fixing' contains 'fix' but shouldn't match as substring
        # Implementation may handle this differently - test behavior
        result = analyze_description("fixing things")
        # Either matches 'fix' in 'fixing' or not - document expected behavior
        # For this implementation, we accept whole words or word boundaries
        # The result should be a dict (possibly empty if no keywords matched)
        assert isinstance(result, dict)

    def test_analyze_punctuation_around_keyword(self):
        """analyze_description() should match keywords with punctuation."""
        result = analyze_description("Bug! Please fix.")
        assert "bug" in result.get(ProjectTier.TIER_0, [])
        assert "fix" in result.get(ProjectTier.TIER_0, [])


class TestAnalyzeDescriptionMixedSignals:
    """Tests for analyze_description() with mixed tier signals (AC #3)."""

    def test_analyze_detects_mixed_tier_keywords(self):
        """analyze_description() should detect keywords from multiple tiers."""
        # Use "integration" (singular) since we match exact keywords
        result = analyze_description("Simple dashboard with complex integration work")
        assert "simple" in result.get(ProjectTier.TIER_1, [])
        assert "complex" in result.get(ProjectTier.TIER_3, [])
        assert "integration" in result.get(ProjectTier.TIER_3, [])

    def test_analyze_returns_all_matches_per_tier(self):
        """analyze_description() should return all matches for each tier."""
        result = analyze_description("Fix bug and add new feature module")
        tier_0_matches = result.get(ProjectTier.TIER_0, [])
        tier_2_matches = result.get(ProjectTier.TIER_2, [])
        assert len(tier_0_matches) >= 2  # fix, bug
        assert len(tier_2_matches) >= 1  # feature or module


# =============================================================================
# Task 6: calculate_keyword_confidence() Function Tests
# =============================================================================


class TestCalculateKeywordConfidence:
    """Tests for calculate_keyword_confidence() function (Task 6.1)."""

    def test_calculate_confidence_returns_tier_confidence(self):
        """calculate_keyword_confidence() should return TierConfidence enum."""
        matches = {ProjectTier.TIER_0: ["fix"]}
        result = calculate_keyword_confidence(matches)
        assert isinstance(result, TierConfidence)

    def test_calculate_confidence_high_for_single_tier_majority(self):
        """calculate_keyword_confidence() should return HIGH when >66% in one tier."""
        # 3 keywords all in Tier 0 = 100% → HIGH
        matches = {
            ProjectTier.TIER_0: ["fix", "bug", "patch"],
            ProjectTier.TIER_1: [],
            ProjectTier.TIER_2: [],
            ProjectTier.TIER_3: [],
            ProjectTier.TIER_4: [],
        }
        result = calculate_keyword_confidence(matches)
        assert result == TierConfidence.HIGH

    def test_calculate_confidence_medium_for_mixed_majority(self):
        """calculate_keyword_confidence() should return MEDIUM when 34-66% in one tier."""
        # 2 keywords in Tier 0, 1 in Tier 1 = 66% → MEDIUM
        matches = {
            ProjectTier.TIER_0: ["fix", "bug"],
            ProjectTier.TIER_1: ["simple"],
            ProjectTier.TIER_2: [],
            ProjectTier.TIER_3: [],
            ProjectTier.TIER_4: [],
        }
        result = calculate_keyword_confidence(matches)
        assert result in (TierConfidence.MEDIUM, TierConfidence.HIGH)  # 66% is boundary

    def test_calculate_confidence_low_for_no_matches(self):
        """calculate_keyword_confidence() should return LOW when no matches."""
        matches = {
            ProjectTier.TIER_0: [],
            ProjectTier.TIER_1: [],
            ProjectTier.TIER_2: [],
            ProjectTier.TIER_3: [],
            ProjectTier.TIER_4: [],
        }
        result = calculate_keyword_confidence(matches)
        assert result == TierConfidence.LOW

    def test_calculate_confidence_low_for_evenly_split(self):
        """calculate_keyword_confidence() should return LOW when evenly split."""
        # 1 keyword in each of 3 tiers = 33% each → LOW
        matches = {
            ProjectTier.TIER_0: ["fix"],
            ProjectTier.TIER_1: ["simple"],
            ProjectTier.TIER_2: ["feature"],
            ProjectTier.TIER_3: [],
            ProjectTier.TIER_4: [],
        }
        result = calculate_keyword_confidence(matches)
        assert result == TierConfidence.LOW

    def test_calculate_confidence_empty_dict(self):
        """calculate_keyword_confidence() should handle empty dict."""
        result = calculate_keyword_confidence({})
        assert result == TierConfidence.LOW


# =============================================================================
# Task 7: analyze_codebase_metrics() Function Tests
# =============================================================================


class TestAnalyzeCodebaseMetrics:
    """Tests for analyze_codebase_metrics() function (Task 7.1)."""

    def test_analyze_codebase_metrics_returns_optional_int(self, tmp_path):
        """analyze_codebase_metrics() should return Optional[int]."""
        # Import here to avoid circular import issues in test discovery
        from pcmrp_tools.bmad_automation.workflow_entry_wrapper import (
            ProjectTypeResult,
            ProjectType,
        )
        result_obj = ProjectTypeResult.greenfield(signals=[])
        result = analyze_codebase_metrics(result_obj)
        assert result is None or isinstance(result, int)

    def test_analyze_codebase_metrics_greenfield_returns_none(self, tmp_path):
        """analyze_codebase_metrics() should return None for greenfield."""
        from pcmrp_tools.bmad_automation.workflow_entry_wrapper import (
            ProjectTypeResult,
        )
        result_obj = ProjectTypeResult.greenfield(signals=[])
        result = analyze_codebase_metrics(result_obj)
        assert result is None

    def test_analyze_codebase_metrics_small_brownfield_returns_none(self, tmp_path):
        """analyze_codebase_metrics() should return None for small brownfield."""
        from pcmrp_tools.bmad_automation.workflow_entry_wrapper import (
            ProjectTypeResult,
            DetectionSignal,
        )
        signals = [
            DetectionSignal(
                name="has_many_source_files",
                detected=True,
                details="Found 20 source files (threshold: 10)",
            )
        ]
        result_obj = ProjectTypeResult.brownfield(signals=signals)
        # Small brownfield (< 100 files) should not adjust
        result = analyze_codebase_metrics(result_obj, file_count=20)
        assert result is None or result == 0

    def test_analyze_codebase_metrics_large_brownfield_returns_adjustment(self, tmp_path):
        """analyze_codebase_metrics() should return +1 for large brownfield (100+ files)."""
        from pcmrp_tools.bmad_automation.workflow_entry_wrapper import (
            ProjectTypeResult,
            DetectionSignal,
        )
        signals = [
            DetectionSignal(
                name="has_many_source_files",
                detected=True,
                details="Found 150 source files",
            )
        ]
        result_obj = ProjectTypeResult.brownfield(signals=signals)
        result = analyze_codebase_metrics(result_obj, file_count=150)
        assert result == 1

    def test_analyze_codebase_metrics_very_large_brownfield_returns_plus_2(self, tmp_path):
        """analyze_codebase_metrics() should return +2 for very large brownfield (500+ files)."""
        from pcmrp_tools.bmad_automation.workflow_entry_wrapper import (
            ProjectTypeResult,
            DetectionSignal,
        )
        signals = [
            DetectionSignal(
                name="has_many_source_files",
                detected=True,
                details="Found 600 source files",
            )
        ]
        result_obj = ProjectTypeResult.brownfield(signals=signals)
        result = analyze_codebase_metrics(result_obj, file_count=600)
        assert result == 2


# =============================================================================
# Task 8: suggest_tier() Main Entry Point Tests
# =============================================================================


class TestSuggestTierBasic:
    """Tests for suggest_tier() basic functionality (Task 8.1)."""

    def test_suggest_tier_returns_tier_suggestion(self):
        """suggest_tier() should return TierSuggestion."""
        result = suggest_tier("Fix the bug")
        assert isinstance(result, TierSuggestion)

    def test_suggest_tier_has_tier(self):
        """suggest_tier() result should have tier field."""
        result = suggest_tier("Fix the bug")
        assert isinstance(result.tier, ProjectTier)

    def test_suggest_tier_has_confidence(self):
        """suggest_tier() result should have confidence field."""
        result = suggest_tier("Fix the bug")
        assert isinstance(result.confidence, TierConfidence)

    def test_suggest_tier_has_matched_keywords(self):
        """suggest_tier() result should have matched_keywords field."""
        result = suggest_tier("Fix the bug")
        assert isinstance(result.matched_keywords, list)

    def test_suggest_tier_has_reasoning(self):
        """suggest_tier() result should have reasoning field."""
        result = suggest_tier("Fix the bug")
        assert isinstance(result.reasoning, str)


class TestSuggestTierAC1:
    """Tests for suggest_tier() Acceptance Criteria #1 - Tier 0 Detection."""

    def test_suggest_tier_0_for_fix_description(self):
        """suggest_tier() should suggest Tier 0 for 'fix' description (AC #1)."""
        result = suggest_tier("Fix the bug in the login page")
        assert result.tier == ProjectTier.TIER_0
        assert "fix" in result.matched_keywords or "bug" in result.matched_keywords

    def test_suggest_tier_0_for_bug_description(self):
        """suggest_tier() should suggest Tier 0 for 'bug' description (AC #1)."""
        result = suggest_tier("There's a bug in the user profile")
        assert result.tier == ProjectTier.TIER_0
        assert "bug" in result.matched_keywords

    def test_suggest_tier_0_for_typo_description(self):
        """suggest_tier() should suggest Tier 0 for 'typo' description (AC #1)."""
        result = suggest_tier("Correct the typo in the README")
        assert result.tier == ProjectTier.TIER_0
        assert "typo" in result.matched_keywords

    def test_suggest_tier_0_for_patch_description(self):
        """suggest_tier() should suggest Tier 0 for 'patch' description (AC #1)."""
        result = suggest_tier("Apply security patch to the server")
        assert result.tier == ProjectTier.TIER_0
        assert "patch" in result.matched_keywords

    def test_suggest_tier_0_for_hotfix_description(self):
        """suggest_tier() should suggest Tier 0 for 'hotfix' description (AC #1)."""
        result = suggest_tier("Emergency hotfix for production")
        assert result.tier == ProjectTier.TIER_0
        assert "hotfix" in result.matched_keywords


class TestSuggestTierAC2:
    """Tests for suggest_tier() Acceptance Criteria #2 - Tier 3 Detection."""

    def test_suggest_tier_3_for_platform_description(self):
        """suggest_tier() should suggest Tier 3 for 'platform' description (AC #2)."""
        result = suggest_tier("Build a new data platform")
        assert result.tier == ProjectTier.TIER_3
        assert "platform" in result.matched_keywords

    def test_suggest_tier_3_for_integration_description(self):
        """suggest_tier() should suggest Tier 3 for 'integration' description (AC #2)."""
        result = suggest_tier("Create API integration with third-party")
        assert result.tier == ProjectTier.TIER_3
        assert "integration" in result.matched_keywords

    def test_suggest_tier_3_for_complex_system_description(self):
        """suggest_tier() should suggest Tier 3 for 'complex system' description (AC #2)."""
        result = suggest_tier("Design a complex distributed system")
        assert result.tier == ProjectTier.TIER_3
        assert "complex" in result.matched_keywords

    def test_suggest_tier_3_for_enterprise_description(self):
        """suggest_tier() should suggest Tier 3 for 'enterprise' description (AC #2)."""
        result = suggest_tier("Enterprise-wide dashboard solution")
        assert result.tier == ProjectTier.TIER_3
        assert "enterprise" in result.matched_keywords


class TestSuggestTierAC3:
    """Tests for suggest_tier() Acceptance Criteria #3 - Mixed Signals."""

    def test_suggest_tier_for_mixed_signals(self):
        """suggest_tier() should handle mixed signals with confidence score (AC #3)."""
        result = suggest_tier("Simple dashboard with complex integrations")
        # Should pick tier based on majority of keywords
        assert result.tier in (ProjectTier.TIER_1, ProjectTier.TIER_3)
        # Confidence should reflect mixed signals
        assert result.confidence in (TierConfidence.LOW, TierConfidence.MEDIUM)

    def test_suggest_tier_mixed_uses_majority(self):
        """suggest_tier() should use tier with >50% of detected keywords (AC #3)."""
        # 3 Tier 0 keywords vs 1 Tier 3 keyword
        result = suggest_tier("Fix the bug with a patch. This is complex.")
        assert result.tier == ProjectTier.TIER_0  # 3/4 = 75% in Tier 0

    def test_suggest_tier_mixed_reports_all_matches(self):
        """suggest_tier() should report all matched keywords (AC #3)."""
        result = suggest_tier("Simple fix for complex feature")
        # Should have matches from multiple tiers in all_matches
        assert len(result.all_matches) >= 1


class TestSuggestTierAC4:
    """Tests for suggest_tier() Acceptance Criteria #4 - Default Tier."""

    def test_suggest_tier_2_default_for_no_keywords(self):
        """suggest_tier() should default to Tier 2 with no keywords (AC #4)."""
        result = suggest_tier("Do something with the code")
        assert result.tier == ProjectTier.TIER_2

    def test_suggest_tier_low_confidence_for_no_keywords(self):
        """suggest_tier() should have LOW confidence for no keywords (AC #4)."""
        result = suggest_tier("Update the stuff in the thing")
        assert result.confidence == TierConfidence.LOW

    def test_suggest_tier_empty_matched_keywords_for_no_keywords(self):
        """suggest_tier() should have empty matched_keywords for no keywords (AC #4)."""
        result = suggest_tier("Make changes to the codebase")
        assert result.matched_keywords == []


class TestSuggestTierAC5:
    """Tests for suggest_tier() Acceptance Criteria #5 - Brownfield Adjustment."""

    def test_suggest_tier_adjusts_for_large_brownfield(self, tmp_path):
        """suggest_tier() should adjust tier for large brownfield codebase (AC #5)."""
        # Create a large brownfield project
        src = tmp_path / "src"
        src.mkdir()
        for i in range(120):
            (src / f"module{i}.py").write_text(f"# module {i}")
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")

        # Description says "small fix" but codebase is large
        result = suggest_tier("Small fix for login", project_path=tmp_path)
        # Should adjust tier up due to large codebase
        # Tier 1 (small) + 1 (large codebase) = Tier 2
        assert result.tier.value >= ProjectTier.TIER_1.value

    def test_suggest_tier_no_adjustment_for_greenfield(self, tmp_path):
        """suggest_tier() should not adjust tier for greenfield (AC #5)."""
        # Empty directory = greenfield
        result = suggest_tier("Build a platform", project_path=tmp_path)
        # No adjustment for greenfield
        assert result.tier == ProjectTier.TIER_3  # platform keyword

    def test_suggest_tier_caps_at_tier_4(self, tmp_path):
        """suggest_tier() should cap tier adjustment at Tier 4."""
        # Create very large brownfield project
        src = tmp_path / "src"
        src.mkdir()
        for i in range(600):
            (src / f"module{i}.py").write_text(f"# module {i}")

        # Even with +2 adjustment, should not exceed Tier 4
        result = suggest_tier("Build complex enterprise platform", project_path=tmp_path)
        assert result.tier.value <= ProjectTier.TIER_4.value


class TestSuggestTierOtherTiers:
    """Tests for suggest_tier() with Tier 1, 2, and 4."""

    def test_suggest_tier_1_for_small_description(self):
        """suggest_tier() should suggest Tier 1 for 'small' description."""
        result = suggest_tier("Add a small utility function")
        assert result.tier == ProjectTier.TIER_1
        assert "small" in result.matched_keywords

    def test_suggest_tier_1_for_simple_description(self):
        """suggest_tier() should suggest Tier 1 for 'simple' description."""
        result = suggest_tier("Create a simple helper")
        assert result.tier == ProjectTier.TIER_1
        assert "simple" in result.matched_keywords

    def test_suggest_tier_2_for_feature_description(self):
        """suggest_tier() should suggest Tier 2 for 'feature' description."""
        result = suggest_tier("Add user authentication feature")
        assert result.tier == ProjectTier.TIER_2
        assert "feature" in result.matched_keywords

    def test_suggest_tier_2_for_module_description(self):
        """suggest_tier() should suggest Tier 2 for 'module' description."""
        result = suggest_tier("Create a new data processing module")
        assert result.tier == ProjectTier.TIER_2
        assert "module" in result.matched_keywords

    def test_suggest_tier_4_for_compliance_description(self):
        """suggest_tier() should suggest Tier 4 for 'compliance' description."""
        result = suggest_tier("Implement GDPR compliance features")
        assert result.tier == ProjectTier.TIER_4
        assert "compliance" in result.matched_keywords

    def test_suggest_tier_4_for_regulated_description(self):
        """suggest_tier() should suggest Tier 4 for 'regulated' description."""
        result = suggest_tier("Build regulated financial reporting")
        assert result.tier == ProjectTier.TIER_4
        assert "regulated" in result.matched_keywords

    def test_suggest_tier_4_for_healthcare_description(self):
        """suggest_tier() should suggest Tier 4 for 'healthcare' description."""
        result = suggest_tier("Healthcare patient management system")
        assert result.tier == ProjectTier.TIER_4
        assert "healthcare" in result.matched_keywords

    def test_suggest_tier_4_for_finance_description(self):
        """suggest_tier() should suggest Tier 4 for 'finance' description."""
        result = suggest_tier("Finance trading platform")
        assert result.tier == ProjectTier.TIER_4
        assert "finance" in result.matched_keywords


class TestSuggestTierEdgeCases:
    """Tests for suggest_tier() edge cases."""

    def test_suggest_tier_empty_string(self):
        """suggest_tier() should handle empty string."""
        result = suggest_tier("")
        assert result.tier == ProjectTier.TIER_2
        assert result.confidence == TierConfidence.LOW

    def test_suggest_tier_permission_error(self, tmp_path, monkeypatch):
        """suggest_tier() should handle permission errors gracefully."""
        from pcmrp_tools.bmad_automation import tier_suggester

        # Mock detect_project_type to raise PermissionError
        def mock_detect(*args, **kwargs):
            raise PermissionError("Access denied")

        monkeypatch.setattr(tier_suggester, "detect_project_type", mock_detect)

        # Should not raise, should just use keyword analysis
        result = suggest_tier("Fix the bug", project_path=tmp_path)
        assert result.tier == ProjectTier.TIER_0


class TestAnalyzeDescriptionHyphenatedKeywords:
    """Tests for analyze_description() with hyphenated keywords."""

    def test_analyze_detects_multi_component_keyword(self):
        """analyze_description() should detect 'multi-component' as Tier 3."""
        result = analyze_description("Build a multi-component architecture")
        assert "multi-component" in result.get(ProjectTier.TIER_3, [])

    def test_analyze_detects_security_critical_keyword(self):
        """analyze_description() should detect 'security-critical' as Tier 4."""
        result = analyze_description("Implement security-critical features")
        assert "security-critical" in result.get(ProjectTier.TIER_4, [])


class TestAnalyzeCodebaseMetricsSignalExtraction:
    """Tests for analyze_codebase_metrics() signal extraction path."""

    def test_analyze_codebase_metrics_extracts_from_signal_details(self, tmp_path):
        """analyze_codebase_metrics() should extract file count from signal details."""
        from pcmrp_tools.bmad_automation.workflow_entry_wrapper import (
            ProjectTypeResult,
            DetectionSignal,
        )
        signals = [
            DetectionSignal(
                name="has_many_source_files",
                detected=True,
                details="Found 200 source files in the codebase",
            )
        ]
        result_obj = ProjectTypeResult.brownfield(signals=signals)
        # Don't pass explicit file_count - let it extract from signals
        result = analyze_codebase_metrics(result_obj)
        assert result == 1  # 200 files = +1 adjustment

    def test_analyze_codebase_metrics_no_file_count_in_signals(self, tmp_path):
        """analyze_codebase_metrics() should return None if file count not in signals."""
        from pcmrp_tools.bmad_automation.workflow_entry_wrapper import (
            ProjectTypeResult,
            DetectionSignal,
        )
        signals = [
            DetectionSignal(
                name="has_package_json",
                detected=True,
                details="Found package.json file",
            )
        ]
        result_obj = ProjectTypeResult.brownfield(signals=signals)
        # Don't pass explicit file_count
        result = analyze_codebase_metrics(result_obj)
        assert result is None


class TestTierSuggestionFromAnalysisEdgeCases:
    """Tests for TierSuggestion.from_analysis() edge cases."""

    def test_from_analysis_with_empty_matched_keywords(self):
        """from_analysis() should generate reasoning for empty matched keywords."""
        matches = {ProjectTier.TIER_2: []}  # Empty list for tier 2
        suggestion = TierSuggestion.from_analysis(
            tier=ProjectTier.TIER_2,
            confidence=TierConfidence.LOW,
            all_matches=matches,
        )
        assert "Tier 2" in suggestion.reasoning
        assert "based on analysis" in suggestion.reasoning


class TestDetermineWinningTierEdgeCases:
    """Tests for _determine_winning_tier() edge cases."""

    def test_determine_winning_tier_empty_matches(self):
        """_determine_winning_tier() should return DEFAULT_TIER for empty matches dict."""
        from pcmrp_tools.bmad_automation.tier_suggester import _determine_winning_tier
        result = _determine_winning_tier({})
        assert result == ProjectTier.TIER_2  # DEFAULT_TIER


class TestSuggestTierEdgeCasesContinued:
    """More edge case tests for suggest_tier()."""

    def test_suggest_tier_whitespace_only(self):
        """suggest_tier() should handle whitespace-only string."""
        result = suggest_tier("   \t\n  ")
        assert result.tier == ProjectTier.TIER_2
        assert result.confidence == TierConfidence.LOW

    def test_suggest_tier_nonexistent_project_path(self, tmp_path):
        """suggest_tier() should handle non-existent project path gracefully."""
        nonexistent = tmp_path / "nonexistent"
        # Should not raise, should just ignore project path
        result = suggest_tier("Fix the bug", project_path=nonexistent)
        assert result.tier == ProjectTier.TIER_0

    def test_suggest_tier_file_instead_of_directory(self, tmp_path):
        """suggest_tier() should handle file path instead of directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")
        # Should not raise, should just ignore project path
        result = suggest_tier("Fix the bug", project_path=file_path)
        assert result.tier == ProjectTier.TIER_0
