"""Tests for Workflow Entry Wrapper - Skill Invocation Detection.

This module tests the skill invocation detection functionality that parses
/bmad:{module}:{type}:{name} patterns.

TDD: Tests are written FIRST, before implementation.
"""

import pytest
from dataclasses import asdict

# Import will fail until implementation exists (TDD Red phase)
from pcmrp_tools.bmad_automation.workflow_entry_wrapper import (
    BMADModule,
    SkillType,
    SkillInvocation,
    SKILL_PATTERN,
    match_skill_pattern,
    detect_skill_invocation,
    detect_and_parse_skill,
    # Story 2a.3: Project Type Detection
    ProjectType,
    DetectionSignal,
    ProjectTypeResult,
    SOURCE_DIRECTORIES,
    detect_source_directories,
    PACKAGE_FILES,
    detect_package_files,
    SOURCE_EXTENSIONS,
    EXCLUDED_DIRS,
    count_source_files,
    detect_project_type,
)


# =============================================================================
# Task 1: SkillInvocation Dataclass Tests
# =============================================================================


class TestBMADModuleEnum:
    """Tests for BMADModule enum."""

    def test_bmad_module_has_core(self):
        """BMADModule should have CORE value."""
        assert BMADModule.CORE.value == "core"

    def test_bmad_module_has_bmm(self):
        """BMADModule should have BMM value."""
        assert BMADModule.BMM.value == "bmm"

    def test_bmad_module_has_bmb(self):
        """BMADModule should have BMB value."""
        assert BMADModule.BMB.value == "bmb"

    def test_bmad_module_from_string_core(self):
        """BMADModule should be creatable from string 'core'."""
        assert BMADModule("core") == BMADModule.CORE

    def test_bmad_module_from_string_bmm(self):
        """BMADModule should be creatable from string 'bmm'."""
        assert BMADModule("bmm") == BMADModule.BMM

    def test_bmad_module_from_string_bmb(self):
        """BMADModule should be creatable from string 'bmb'."""
        assert BMADModule("bmb") == BMADModule.BMB


class TestSkillTypeEnum:
    """Tests for SkillType enum."""

    def test_skill_type_has_workflows(self):
        """SkillType should have WORKFLOWS value."""
        assert SkillType.WORKFLOWS.value == "workflows"

    def test_skill_type_has_agents(self):
        """SkillType should have AGENTS value."""
        assert SkillType.AGENTS.value == "agents"

    def test_skill_type_has_tasks(self):
        """SkillType should have TASKS value."""
        assert SkillType.TASKS.value == "tasks"


class TestSkillInvocationDataclass:
    """Tests for SkillInvocation dataclass creation and attributes."""

    def test_skill_invocation_creation_with_all_fields(self):
        """SkillInvocation should be creatable with all fields."""
        invocation = SkillInvocation(
            detected=True,
            module=BMADModule.BMM,
            skill_type=SkillType.WORKFLOWS,
            name="dev-story",
            error=None,
            raw_input="/bmad:bmm:workflows:dev-story",
        )
        assert invocation.detected is True
        assert invocation.module == BMADModule.BMM
        assert invocation.skill_type == SkillType.WORKFLOWS
        assert invocation.name == "dev-story"
        assert invocation.error is None
        assert invocation.raw_input == "/bmad:bmm:workflows:dev-story"

    def test_skill_invocation_creation_with_defaults(self):
        """SkillInvocation should have sensible defaults."""
        invocation = SkillInvocation(detected=False, raw_input="hello")
        assert invocation.detected is False
        assert invocation.module is None
        assert invocation.skill_type is None
        assert invocation.name is None
        assert invocation.error is None
        assert invocation.raw_input == "hello"

    def test_skill_invocation_to_dict(self):
        """SkillInvocation should be serializable to dict."""
        invocation = SkillInvocation(
            detected=True,
            module=BMADModule.CORE,
            skill_type=SkillType.WORKFLOWS,
            name="brainstorming",
            raw_input="/bmad:core:workflows:brainstorming",
        )
        result = asdict(invocation)
        assert result["detected"] is True
        assert result["module"] == BMADModule.CORE
        assert result["skill_type"] == SkillType.WORKFLOWS
        assert result["name"] == "brainstorming"


class TestSkillInvocationFactoryMethods:
    """Tests for SkillInvocation factory methods."""

    def test_detected_skill_factory_creates_valid_invocation(self):
        """detected_skill() should create a detected=True invocation."""
        invocation = SkillInvocation.detected_skill(
            module=BMADModule.BMM,
            skill_type=SkillType.WORKFLOWS,
            name="dev-story",
            raw_input="/bmad:bmm:workflows:dev-story",
        )
        assert invocation.detected is True
        assert invocation.module == BMADModule.BMM
        assert invocation.skill_type == SkillType.WORKFLOWS
        assert invocation.name == "dev-story"
        assert invocation.error is None

    def test_not_detected_factory_creates_false_invocation(self):
        """not_detected() should create a detected=False invocation."""
        invocation = SkillInvocation.not_detected(raw_input="hello world")
        assert invocation.detected is False
        assert invocation.module is None
        assert invocation.skill_type is None
        assert invocation.name is None
        assert invocation.error is None
        assert invocation.raw_input == "hello world"

    def test_invalid_factory_creates_error_invocation(self):
        """invalid() should create an invocation with error message."""
        invocation = SkillInvocation.invalid(
            error="invalid_skill_path",
            raw_input="/bmad:invalid",
        )
        assert invocation.detected is False
        assert invocation.error == "invalid_skill_path"
        assert invocation.raw_input == "/bmad:invalid"
        assert invocation.module is None
        assert invocation.skill_type is None
        assert invocation.name is None


# =============================================================================
# Task 2: Skill Pattern Regex Tests
# =============================================================================


class TestSkillPatternConstant:
    """Tests for the SKILL_PATTERN regex constant."""

    def test_skill_pattern_is_compiled_regex(self):
        """SKILL_PATTERN should be a compiled regex pattern."""
        import re
        assert hasattr(SKILL_PATTERN, 'match')
        assert hasattr(SKILL_PATTERN, 'search')

    def test_skill_pattern_matches_bmm_workflows(self):
        """SKILL_PATTERN should match /bmad:bmm:workflows:name."""
        match = SKILL_PATTERN.search("/bmad:bmm:workflows:dev-story")
        assert match is not None
        assert match.group("module") == "bmm"
        assert match.group("type") == "workflows"
        assert match.group("name") == "dev-story"

    def test_skill_pattern_matches_core_workflows(self):
        """SKILL_PATTERN should match /bmad:core:workflows:name."""
        match = SKILL_PATTERN.search("/bmad:core:workflows:brainstorming")
        assert match is not None
        assert match.group("module") == "core"
        assert match.group("type") == "workflows"
        assert match.group("name") == "brainstorming"

    def test_skill_pattern_matches_bmb_agents(self):
        """SKILL_PATTERN should match /bmad:bmb:agents:name."""
        match = SKILL_PATTERN.search("/bmad:bmb:agents:agent-builder")
        assert match is not None
        assert match.group("module") == "bmb"
        assert match.group("type") == "agents"
        assert match.group("name") == "agent-builder"

    def test_skill_pattern_matches_tasks_type(self):
        """SKILL_PATTERN should match tasks type."""
        match = SKILL_PATTERN.search("/bmad:core:tasks:index-docs")
        assert match is not None
        assert match.group("type") == "tasks"

    def test_skill_pattern_captures_hyphenated_names(self):
        """SKILL_PATTERN should capture names with hyphens."""
        match = SKILL_PATTERN.search("/bmad:bmm:workflows:check-implementation-readiness")
        assert match is not None
        assert match.group("name") == "check-implementation-readiness"

    def test_skill_pattern_captures_underscored_names(self):
        """SKILL_PATTERN should capture names with underscores."""
        match = SKILL_PATTERN.search("/bmad:bmm:workflows:workflow_test_name")
        assert match is not None
        assert match.group("name") == "workflow_test_name"

    def test_skill_pattern_no_match_on_plain_text(self):
        """SKILL_PATTERN should not match plain text."""
        match = SKILL_PATTERN.search("hello world")
        assert match is None

    def test_skill_pattern_no_match_on_partial_pattern(self):
        """SKILL_PATTERN should not match partial patterns."""
        match = SKILL_PATTERN.search("/bmad:bmm")
        assert match is None


class TestMatchSkillPatternFunction:
    """Tests for the match_skill_pattern() helper function."""

    def test_match_skill_pattern_returns_match_object(self):
        """match_skill_pattern() should return a Match object on success."""
        result = match_skill_pattern("/bmad:bmm:workflows:dev-story")
        assert result is not None

    def test_match_skill_pattern_returns_none_on_no_match(self):
        """match_skill_pattern() should return None when no match."""
        result = match_skill_pattern("hello world")
        assert result is None

    def test_match_skill_pattern_extracts_groups(self):
        """match_skill_pattern() result should have extractable groups."""
        result = match_skill_pattern("/bmad:core:agents:bmad-master")
        assert result is not None
        assert result.group("module") == "core"
        assert result.group("type") == "agents"
        assert result.group("name") == "bmad-master"

    def test_match_skill_pattern_handles_whitespace_prefix(self):
        """match_skill_pattern() should match with leading whitespace."""
        result = match_skill_pattern("  /bmad:bmm:workflows:dev-story")
        assert result is not None

    def test_match_skill_pattern_handles_text_before_pattern(self):
        """match_skill_pattern() should match pattern in longer text."""
        result = match_skill_pattern("Please run /bmad:bmm:workflows:dev-story for me")
        assert result is not None
        assert result.group("name") == "dev-story"

    def test_match_skill_pattern_case_insensitive_bmad(self):
        """match_skill_pattern() should be case-insensitive for /bmad prefix."""
        result = match_skill_pattern("/BMAD:bmm:workflows:dev-story")
        assert result is not None

    def test_match_skill_pattern_preserves_module_case(self):
        """match_skill_pattern() should preserve the case of captured groups."""
        # Note: We normalize in validation, not in pattern matching
        result = match_skill_pattern("/bmad:BMM:workflows:dev-story")
        assert result is not None
        # The raw match preserves case
        assert result.group("module") == "BMM"


# =============================================================================
# Task 3: detect_skill_invocation() Function Tests
# =============================================================================


# Import the function for Task 3 (will be added to imports at top)
from pcmrp_tools.bmad_automation.workflow_entry_wrapper import detect_skill_invocation


class TestDetectSkillInvocationBasic:
    """Tests for basic detect_skill_invocation() functionality."""

    def test_detect_skill_invocation_returns_skill_invocation(self):
        """detect_skill_invocation() should return a SkillInvocation."""
        result = detect_skill_invocation("/bmad:bmm:workflows:dev-story")
        assert isinstance(result, SkillInvocation)

    def test_detect_skill_invocation_detected_bmm_workflows(self):
        """detect_skill_invocation() should detect bmm:workflows pattern."""
        result = detect_skill_invocation("/bmad:bmm:workflows:dev-story")
        assert result.detected is True
        assert result.module == BMADModule.BMM
        assert result.skill_type == SkillType.WORKFLOWS
        assert result.name == "dev-story"

    def test_detect_skill_invocation_detected_core_workflows(self):
        """detect_skill_invocation() should detect core:workflows pattern."""
        result = detect_skill_invocation("/bmad:core:workflows:brainstorming")
        assert result.detected is True
        assert result.module == BMADModule.CORE
        assert result.skill_type == SkillType.WORKFLOWS
        assert result.name == "brainstorming"

    def test_detect_skill_invocation_detected_bmb_agents(self):
        """detect_skill_invocation() should detect bmb:agents pattern."""
        result = detect_skill_invocation("/bmad:bmb:agents:agent-builder")
        assert result.detected is True
        assert result.module == BMADModule.BMB
        assert result.skill_type == SkillType.AGENTS
        assert result.name == "agent-builder"

    def test_detect_skill_invocation_detected_tasks_type(self):
        """detect_skill_invocation() should detect tasks type."""
        result = detect_skill_invocation("/bmad:core:tasks:index-docs")
        assert result.detected is True
        assert result.skill_type == SkillType.TASKS


class TestDetectSkillInvocationNotDetected:
    """Tests for detect_skill_invocation() non-detection scenarios."""

    def test_detect_skill_invocation_not_detected_plain_text(self):
        """detect_skill_invocation() should not detect plain text."""
        result = detect_skill_invocation("hello world")
        assert result.detected is False
        assert result.module is None
        assert result.skill_type is None
        assert result.name is None
        assert result.error is None
        assert result.raw_input == "hello world"

    def test_detect_skill_invocation_not_detected_empty_string(self):
        """detect_skill_invocation() should handle empty string."""
        result = detect_skill_invocation("")
        assert result.detected is False
        assert result.raw_input == ""

    def test_detect_skill_invocation_not_detected_whitespace_only(self):
        """detect_skill_invocation() should handle whitespace-only input."""
        result = detect_skill_invocation("   \t\n   ")
        assert result.detected is False

    def test_detect_skill_invocation_preserves_raw_input(self):
        """detect_skill_invocation() should preserve the original input."""
        raw = "Some text /bmad:bmm:workflows:dev-story more text"
        result = detect_skill_invocation(raw)
        assert result.raw_input == raw


class TestDetectSkillInvocationCaseSensitivity:
    """Tests for detect_skill_invocation() case handling."""

    def test_detect_skill_invocation_normalizes_module_to_lowercase(self):
        """detect_skill_invocation() should normalize module to lowercase enum."""
        result = detect_skill_invocation("/bmad:BMM:workflows:dev-story")
        assert result.detected is True
        assert result.module == BMADModule.BMM

    def test_detect_skill_invocation_normalizes_type_to_lowercase(self):
        """detect_skill_invocation() should normalize type to lowercase enum."""
        result = detect_skill_invocation("/bmad:bmm:WORKFLOWS:dev-story")
        assert result.detected is True
        assert result.skill_type == SkillType.WORKFLOWS

    def test_detect_skill_invocation_preserves_name_case(self):
        """detect_skill_invocation() should preserve name case."""
        result = detect_skill_invocation("/bmad:bmm:workflows:Dev-Story")
        assert result.detected is True
        assert result.name == "Dev-Story"


# =============================================================================
# Task 4: Malformed Pattern Handling Tests
# =============================================================================


class TestDetectSkillInvocationMalformedPatterns:
    """Tests for detect_skill_invocation() malformed pattern handling."""

    def test_detect_invalid_module_returns_error(self):
        """Invalid module should return error with invalid_module message."""
        result = detect_skill_invocation("/bmad:invalid:workflows:dev-story")
        assert result.detected is False
        assert result.error is not None
        assert "invalid_module" in result.error

    def test_detect_invalid_type_returns_error(self):
        """Invalid type should return error with invalid_type message."""
        result = detect_skill_invocation("/bmad:bmm:badtype:dev-story")
        assert result.detected is False
        assert result.error is not None
        assert "invalid_type" in result.error

    def test_detect_partial_pattern_bmad_only_not_detected(self):
        """Partial pattern /bmad: alone should not be detected (not error)."""
        result = detect_skill_invocation("/bmad:")
        assert result.detected is False
        # No error because pattern doesn't match at all

    def test_detect_partial_pattern_two_parts_not_detected(self):
        """Partial pattern /bmad:bmm should not be detected."""
        result = detect_skill_invocation("/bmad:bmm")
        assert result.detected is False

    def test_detect_partial_pattern_three_parts_no_name_not_detected(self):
        """Partial pattern /bmad:bmm:workflows should not be detected."""
        result = detect_skill_invocation("/bmad:bmm:workflows")
        assert result.detected is False

    def test_detect_partial_pattern_three_parts_with_colon_not_detected(self):
        """Partial pattern /bmad:bmm:workflows: should not be detected."""
        result = detect_skill_invocation("/bmad:bmm:workflows:")
        assert result.detected is False


class TestDetectSkillInvocationEdgeCases:
    """Tests for detect_skill_invocation() edge case handling."""

    def test_detect_empty_string_not_detected(self):
        """Empty string should not be detected."""
        result = detect_skill_invocation("")
        assert result.detected is False
        assert result.error is None

    def test_detect_whitespace_only_not_detected(self):
        """Whitespace-only string should not be detected."""
        result = detect_skill_invocation("   \t\n  ")
        assert result.detected is False
        assert result.error is None

    def test_detect_leading_whitespace_still_detects(self):
        """Leading whitespace should not prevent detection."""
        result = detect_skill_invocation("   /bmad:bmm:workflows:dev-story")
        assert result.detected is True

    def test_detect_trailing_whitespace_still_detects(self):
        """Trailing whitespace should not prevent detection."""
        result = detect_skill_invocation("/bmad:bmm:workflows:dev-story   ")
        assert result.detected is True

    def test_detect_pattern_in_sentence_still_detects(self):
        """Pattern embedded in sentence should still be detected."""
        result = detect_skill_invocation("Please run /bmad:bmm:workflows:dev-story now")
        assert result.detected is True
        assert result.name == "dev-story"

    def test_detect_special_chars_in_name_hyphen(self):
        """Names with hyphens should be detected."""
        result = detect_skill_invocation("/bmad:bmm:workflows:check-implementation-readiness")
        assert result.detected is True
        assert result.name == "check-implementation-readiness"

    def test_detect_special_chars_in_name_underscore(self):
        """Names with underscores should be detected."""
        result = detect_skill_invocation("/bmad:bmm:workflows:my_workflow_name")
        assert result.detected is True
        assert result.name == "my_workflow_name"

    def test_detect_special_chars_in_name_numbers(self):
        """Names with numbers should be detected."""
        result = detect_skill_invocation("/bmad:bmm:workflows:workflow123")
        assert result.detected is True
        assert result.name == "workflow123"


# =============================================================================
# Task 5: Path Validation Tests
# =============================================================================


class TestDetectSkillInvocationModuleValidation:
    """Tests for module validation in detect_skill_invocation()."""

    def test_valid_module_core(self):
        """Module 'core' should be valid."""
        result = detect_skill_invocation("/bmad:core:workflows:test")
        assert result.detected is True
        assert result.module == BMADModule.CORE

    def test_valid_module_bmm(self):
        """Module 'bmm' should be valid."""
        result = detect_skill_invocation("/bmad:bmm:workflows:test")
        assert result.detected is True
        assert result.module == BMADModule.BMM

    def test_valid_module_bmb(self):
        """Module 'bmb' should be valid."""
        result = detect_skill_invocation("/bmad:bmb:workflows:test")
        assert result.detected is True
        assert result.module == BMADModule.BMB

    def test_invalid_module_returns_error_with_module_name(self):
        """Invalid module should return error containing the invalid module name."""
        result = detect_skill_invocation("/bmad:xyz:workflows:test")
        assert result.detected is False
        assert result.error is not None
        assert "xyz" in result.error

    def test_invalid_module_foo_returns_error(self):
        """Module 'foo' should be invalid."""
        result = detect_skill_invocation("/bmad:foo:workflows:test")
        assert result.detected is False
        assert "invalid_module" in result.error


class TestDetectSkillInvocationTypeValidation:
    """Tests for type validation in detect_skill_invocation()."""

    def test_valid_type_workflows(self):
        """Type 'workflows' should be valid."""
        result = detect_skill_invocation("/bmad:bmm:workflows:test")
        assert result.detected is True
        assert result.skill_type == SkillType.WORKFLOWS

    def test_valid_type_agents(self):
        """Type 'agents' should be valid."""
        result = detect_skill_invocation("/bmad:bmm:agents:test")
        assert result.detected is True
        assert result.skill_type == SkillType.AGENTS

    def test_valid_type_tasks(self):
        """Type 'tasks' should be valid."""
        result = detect_skill_invocation("/bmad:bmm:tasks:test")
        assert result.detected is True
        assert result.skill_type == SkillType.TASKS

    def test_invalid_type_returns_error_with_type_name(self):
        """Invalid type should return error containing the invalid type name."""
        result = detect_skill_invocation("/bmad:bmm:badtype:test")
        assert result.detected is False
        assert result.error is not None
        assert "badtype" in result.error

    def test_invalid_type_scripts_returns_error(self):
        """Type 'scripts' should be invalid."""
        result = detect_skill_invocation("/bmad:bmm:scripts:test")
        assert result.detected is False
        assert "invalid_type" in result.error


class TestDetectSkillInvocationValidationCombinations:
    """Tests for combined validation scenarios."""

    def test_all_valid_modules_with_workflows(self):
        """All valid modules should work with 'workflows' type."""
        for module in ["core", "bmm", "bmb"]:
            result = detect_skill_invocation(f"/bmad:{module}:workflows:test")
            assert result.detected is True, f"Failed for module: {module}"

    def test_all_valid_types_with_bmm(self):
        """All valid types should work with 'bmm' module."""
        for skill_type in ["workflows", "agents", "tasks"]:
            result = detect_skill_invocation(f"/bmad:bmm:{skill_type}:test")
            assert result.detected is True, f"Failed for type: {skill_type}"

    def test_invalid_module_valid_type(self):
        """Invalid module with valid type should return module error."""
        result = detect_skill_invocation("/bmad:invalid:workflows:test")
        assert result.detected is False
        assert "invalid_module" in result.error

    def test_valid_module_invalid_type(self):
        """Valid module with invalid type should return type error."""
        result = detect_skill_invocation("/bmad:bmm:invalid:test")
        assert result.detected is False
        assert "invalid_type" in result.error


# =============================================================================
# Story 2a.3: Project Type Detection Tests
# =============================================================================


# =============================================================================
# Task 1: ProjectTypeResult Dataclass Tests
# =============================================================================


class TestProjectTypeEnum:
    """Tests for ProjectType enum (Task 1.1)."""

    def test_project_type_has_greenfield(self):
        """ProjectType should have GREENFIELD value."""
        assert ProjectType.GREENFIELD.value == "greenfield"

    def test_project_type_has_brownfield(self):
        """ProjectType should have BROWNFIELD value."""
        assert ProjectType.BROWNFIELD.value == "brownfield"

    def test_project_type_from_string_greenfield(self):
        """ProjectType should be creatable from string 'greenfield'."""
        assert ProjectType("greenfield") == ProjectType.GREENFIELD

    def test_project_type_from_string_brownfield(self):
        """ProjectType should be creatable from string 'brownfield'."""
        assert ProjectType("brownfield") == ProjectType.BROWNFIELD


class TestDetectionSignalDataclass:
    """Tests for DetectionSignal dataclass (Task 1.2)."""

    def test_detection_signal_creation_with_all_fields(self):
        """DetectionSignal should be creatable with all fields."""
        signal = DetectionSignal(
            name="has_source_directory",
            detected=True,
            details="Found src/ directory with 50 files",
        )
        assert signal.name == "has_source_directory"
        assert signal.detected is True
        assert signal.details == "Found src/ directory with 50 files"

    def test_detection_signal_creation_with_defaults(self):
        """DetectionSignal should have empty string as default details."""
        signal = DetectionSignal(name="has_package_json", detected=False)
        assert signal.name == "has_package_json"
        assert signal.detected is False
        assert signal.details == ""

    def test_detection_signal_to_dict(self):
        """DetectionSignal should be serializable to dict."""
        signal = DetectionSignal(
            name="has_source_files",
            detected=True,
            details="Found 15 source files",
        )
        result = asdict(signal)
        assert result["name"] == "has_source_files"
        assert result["detected"] is True
        assert result["details"] == "Found 15 source files"


class TestProjectTypeResultDataclass:
    """Tests for ProjectTypeResult dataclass (Task 1.2)."""

    def test_project_type_result_creation_with_all_fields(self):
        """ProjectTypeResult should be creatable with all fields."""
        signals = [
            DetectionSignal("has_src_dir", True, "Found src/"),
            DetectionSignal("has_package_json", True, "Found package.json"),
        ]
        result = ProjectTypeResult(
            project_type=ProjectType.BROWNFIELD,
            detection_signals=signals,
            confidence=0.9,
        )
        assert result.project_type == ProjectType.BROWNFIELD
        assert len(result.detection_signals) == 2
        assert result.confidence == 0.9

    def test_project_type_result_creation_with_defaults(self):
        """ProjectTypeResult should have sensible defaults."""
        result = ProjectTypeResult(project_type=ProjectType.GREENFIELD)
        assert result.project_type == ProjectType.GREENFIELD
        assert result.detection_signals == []
        assert result.confidence == 1.0

    def test_project_type_result_to_dict(self):
        """ProjectTypeResult should be serializable to dict."""
        signals = [DetectionSignal("test", True, "test details")]
        result = ProjectTypeResult(
            project_type=ProjectType.BROWNFIELD,
            detection_signals=signals,
            confidence=0.8,
        )
        result_dict = asdict(result)
        assert result_dict["project_type"] == ProjectType.BROWNFIELD
        assert len(result_dict["detection_signals"]) == 1
        assert result_dict["confidence"] == 0.8


class TestProjectTypeResultFactoryMethods:
    """Tests for ProjectTypeResult factory methods (Task 1.3)."""

    def test_greenfield_factory_creates_greenfield_result(self):
        """greenfield() should create a GREENFIELD result."""
        signals = [DetectionSignal("no_src_dir", False, "No src/ directory found")]
        result = ProjectTypeResult.greenfield(signals=signals)
        assert result.project_type == ProjectType.GREENFIELD
        assert result.detection_signals == signals

    def test_greenfield_factory_with_confidence(self):
        """greenfield() should accept optional confidence parameter."""
        result = ProjectTypeResult.greenfield(signals=[], confidence=0.7)
        assert result.project_type == ProjectType.GREENFIELD
        assert result.confidence == 0.7

    def test_brownfield_factory_creates_brownfield_result(self):
        """brownfield() should create a BROWNFIELD result."""
        signals = [DetectionSignal("has_package_json", True, "Found package.json")]
        result = ProjectTypeResult.brownfield(signals=signals)
        assert result.project_type == ProjectType.BROWNFIELD
        assert result.detection_signals == signals

    def test_brownfield_factory_with_confidence(self):
        """brownfield() should accept optional confidence parameter."""
        result = ProjectTypeResult.brownfield(signals=[], confidence=0.85)
        assert result.project_type == ProjectType.BROWNFIELD
        assert result.confidence == 0.85


# =============================================================================
# Task 2: Source Directory Detection Tests
# =============================================================================


class TestSourceDirectoriesConstant:
    """Tests for SOURCE_DIRECTORIES constant (Task 2.1)."""

    def test_source_directories_is_set(self):
        """SOURCE_DIRECTORIES should be a set."""
        assert isinstance(SOURCE_DIRECTORIES, (set, frozenset))

    def test_source_directories_contains_src(self):
        """SOURCE_DIRECTORIES should contain 'src'."""
        assert "src" in SOURCE_DIRECTORIES

    def test_source_directories_contains_lib(self):
        """SOURCE_DIRECTORIES should contain 'lib'."""
        assert "lib" in SOURCE_DIRECTORIES

    def test_source_directories_contains_app(self):
        """SOURCE_DIRECTORIES should contain 'app'."""
        assert "app" in SOURCE_DIRECTORIES


class TestDetectSourceDirectoriesFunction:
    """Tests for detect_source_directories() function (Task 2.1-2.3)."""

    def test_detect_source_directories_returns_list_of_signals(self, tmp_path):
        """detect_source_directories() should return list of DetectionSignal."""
        result = detect_source_directories(tmp_path)
        assert isinstance(result, list)
        for signal in result:
            assert isinstance(signal, DetectionSignal)

    def test_detect_source_directories_detects_src_dir(self, tmp_path):
        """detect_source_directories() should detect src/ directory."""
        (tmp_path / "src").mkdir()
        result = detect_source_directories(tmp_path)
        src_signals = [s for s in result if "src" in s.name.lower()]
        assert len(src_signals) >= 1
        assert any(s.detected for s in src_signals)

    def test_detect_source_directories_detects_lib_dir(self, tmp_path):
        """detect_source_directories() should detect lib/ directory."""
        (tmp_path / "lib").mkdir()
        result = detect_source_directories(tmp_path)
        lib_signals = [s for s in result if "lib" in s.name.lower()]
        assert len(lib_signals) >= 1
        assert any(s.detected for s in lib_signals)

    def test_detect_source_directories_detects_app_dir(self, tmp_path):
        """detect_source_directories() should detect app/ directory."""
        (tmp_path / "app").mkdir()
        result = detect_source_directories(tmp_path)
        app_signals = [s for s in result if "app" in s.name.lower()]
        assert len(app_signals) >= 1
        assert any(s.detected for s in app_signals)

    def test_detect_source_directories_no_source_dirs(self, tmp_path):
        """detect_source_directories() should report no source dirs found."""
        (tmp_path / "docs").mkdir()  # Non-source directory
        result = detect_source_directories(tmp_path)
        # Should have signals indicating no source directories were found
        assert isinstance(result, list)
        # All source directory signals should be not detected
        detected_source_dirs = [s for s in result if s.detected and "dir" in s.name.lower()]
        # Either empty or all not detected
        assert len([s for s in result if s.detected]) == 0 or not any(s.detected for s in result)

    def test_detect_source_directories_counts_files(self, tmp_path):
        """detect_source_directories() should count files in source directories."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        # Create 5 files
        for i in range(5):
            (src_dir / f"file{i}.py").write_text(f"# file {i}")
        result = detect_source_directories(tmp_path)
        # Check that a signal mentions the file count
        src_signals = [s for s in result if s.detected and "src" in s.name.lower()]
        assert len(src_signals) >= 1
        # The details should mention the count
        assert any("5" in s.details for s in src_signals)

    def test_detect_source_directories_empty_directory(self, tmp_path):
        """detect_source_directories() should handle empty project directory."""
        result = detect_source_directories(tmp_path)
        assert isinstance(result, list)

    def test_detect_source_directories_multiple_source_dirs(self, tmp_path):
        """detect_source_directories() should detect multiple source directories."""
        (tmp_path / "src").mkdir()
        (tmp_path / "lib").mkdir()
        result = detect_source_directories(tmp_path)
        detected = [s for s in result if s.detected]
        assert len(detected) >= 2


# =============================================================================
# Task 3: Package File Detection Tests
# =============================================================================


class TestPackageFilesConstant:
    """Tests for PACKAGE_FILES constant (Task 3.1-3.3)."""

    def test_package_files_is_set(self):
        """PACKAGE_FILES should be a set."""
        assert isinstance(PACKAGE_FILES, (set, frozenset))

    def test_package_files_contains_package_json(self):
        """PACKAGE_FILES should contain 'package.json'."""
        assert "package.json" in PACKAGE_FILES

    def test_package_files_contains_pyproject_toml(self):
        """PACKAGE_FILES should contain 'pyproject.toml'."""
        assert "pyproject.toml" in PACKAGE_FILES

    def test_package_files_contains_cargo_toml(self):
        """PACKAGE_FILES should contain 'Cargo.toml'."""
        assert "Cargo.toml" in PACKAGE_FILES

    def test_package_files_contains_go_mod(self):
        """PACKAGE_FILES should contain 'go.mod'."""
        assert "go.mod" in PACKAGE_FILES

    def test_package_files_contains_pom_xml(self):
        """PACKAGE_FILES should contain 'pom.xml'."""
        assert "pom.xml" in PACKAGE_FILES


class TestDetectPackageFilesFunction:
    """Tests for detect_package_files() function (Task 3.1-3.4)."""

    def test_detect_package_files_returns_list_of_signals(self, tmp_path):
        """detect_package_files() should return list of DetectionSignal."""
        result = detect_package_files(tmp_path)
        assert isinstance(result, list)
        for signal in result:
            assert isinstance(signal, DetectionSignal)

    def test_detect_package_files_detects_package_json(self, tmp_path):
        """detect_package_files() should detect package.json."""
        (tmp_path / "package.json").write_text('{"name": "test"}')
        result = detect_package_files(tmp_path)
        json_signals = [s for s in result if "package.json" in s.name or "package_json" in s.name]
        assert len(json_signals) >= 1
        assert any(s.detected for s in json_signals)

    def test_detect_package_files_detects_pyproject_toml(self, tmp_path):
        """detect_package_files() should detect pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"')
        result = detect_package_files(tmp_path)
        toml_signals = [s for s in result if "pyproject" in s.name.lower()]
        assert len(toml_signals) >= 1
        assert any(s.detected for s in toml_signals)

    def test_detect_package_files_detects_cargo_toml(self, tmp_path):
        """detect_package_files() should detect Cargo.toml."""
        (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"')
        result = detect_package_files(tmp_path)
        cargo_signals = [s for s in result if "cargo" in s.name.lower()]
        assert len(cargo_signals) >= 1
        assert any(s.detected for s in cargo_signals)

    def test_detect_package_files_detects_go_mod(self, tmp_path):
        """detect_package_files() should detect go.mod."""
        (tmp_path / "go.mod").write_text('module example.com/test')
        result = detect_package_files(tmp_path)
        go_signals = [s for s in result if "go" in s.name.lower() and "mod" in s.name.lower()]
        assert len(go_signals) >= 1
        assert any(s.detected for s in go_signals)

    def test_detect_package_files_detects_pom_xml(self, tmp_path):
        """detect_package_files() should detect pom.xml."""
        (tmp_path / "pom.xml").write_text('<project></project>')
        result = detect_package_files(tmp_path)
        pom_signals = [s for s in result if "pom" in s.name.lower()]
        assert len(pom_signals) >= 1
        assert any(s.detected for s in pom_signals)

    def test_detect_package_files_no_package_files(self, tmp_path):
        """detect_package_files() should return empty when no package files."""
        (tmp_path / "readme.txt").write_text("Hello")
        result = detect_package_files(tmp_path)
        detected = [s for s in result if s.detected]
        assert len(detected) == 0

    def test_detect_package_files_multiple_package_files(self, tmp_path):
        """detect_package_files() should detect multiple package files."""
        (tmp_path / "package.json").write_text('{}')
        (tmp_path / "pyproject.toml").write_text('')
        result = detect_package_files(tmp_path)
        detected = [s for s in result if s.detected]
        assert len(detected) >= 2


# =============================================================================
# Task 4: Source File Counting Tests
# =============================================================================


class TestSourceExtensionsConstant:
    """Tests for SOURCE_EXTENSIONS constant (Task 4.1)."""

    def test_source_extensions_is_set(self):
        """SOURCE_EXTENSIONS should be a set."""
        assert isinstance(SOURCE_EXTENSIONS, (set, frozenset))

    def test_source_extensions_contains_python(self):
        """SOURCE_EXTENSIONS should contain '.py'."""
        assert ".py" in SOURCE_EXTENSIONS

    def test_source_extensions_contains_javascript(self):
        """SOURCE_EXTENSIONS should contain '.js'."""
        assert ".js" in SOURCE_EXTENSIONS

    def test_source_extensions_contains_typescript(self):
        """SOURCE_EXTENSIONS should contain '.ts'."""
        assert ".ts" in SOURCE_EXTENSIONS

    def test_source_extensions_contains_java(self):
        """SOURCE_EXTENSIONS should contain '.java'."""
        assert ".java" in SOURCE_EXTENSIONS

    def test_source_extensions_contains_go(self):
        """SOURCE_EXTENSIONS should contain '.go'."""
        assert ".go" in SOURCE_EXTENSIONS


class TestExcludedDirsConstant:
    """Tests for EXCLUDED_DIRS constant (Task 4.2)."""

    def test_excluded_dirs_is_set(self):
        """EXCLUDED_DIRS should be a set."""
        assert isinstance(EXCLUDED_DIRS, (set, frozenset))

    def test_excluded_dirs_contains_node_modules(self):
        """EXCLUDED_DIRS should contain 'node_modules'."""
        assert "node_modules" in EXCLUDED_DIRS

    def test_excluded_dirs_contains_pycache(self):
        """EXCLUDED_DIRS should contain '__pycache__'."""
        assert "__pycache__" in EXCLUDED_DIRS

    def test_excluded_dirs_contains_venv(self):
        """EXCLUDED_DIRS should contain 'venv'."""
        assert "venv" in EXCLUDED_DIRS

    def test_excluded_dirs_contains_git(self):
        """EXCLUDED_DIRS should contain '.git'."""
        assert ".git" in EXCLUDED_DIRS


class TestCountSourceFilesFunction:
    """Tests for count_source_files() function (Task 4.1-4.4)."""

    def test_count_source_files_returns_tuple(self, tmp_path):
        """count_source_files() should return (count, signal)."""
        result = count_source_files(tmp_path)
        assert isinstance(result, tuple)
        assert len(result) == 2
        count, signal = result
        assert isinstance(count, int)
        assert isinstance(signal, DetectionSignal)

    def test_count_source_files_counts_python_files(self, tmp_path):
        """count_source_files() should count .py files."""
        for i in range(5):
            (tmp_path / f"file{i}.py").write_text(f"# file {i}")
        count, signal = count_source_files(tmp_path)
        assert count == 5

    def test_count_source_files_counts_javascript_files(self, tmp_path):
        """count_source_files() should count .js files."""
        for i in range(3):
            (tmp_path / f"file{i}.js").write_text(f"// file {i}")
        count, signal = count_source_files(tmp_path)
        assert count == 3

    def test_count_source_files_counts_mixed_files(self, tmp_path):
        """count_source_files() should count mixed source files."""
        (tmp_path / "app.py").write_text("# python")
        (tmp_path / "app.js").write_text("// javascript")
        (tmp_path / "app.ts").write_text("// typescript")
        count, signal = count_source_files(tmp_path)
        assert count == 3

    def test_count_source_files_excludes_non_source_files(self, tmp_path):
        """count_source_files() should not count non-source files."""
        (tmp_path / "app.py").write_text("# python")
        (tmp_path / "readme.md").write_text("# readme")
        (tmp_path / "config.json").write_text("{}")
        count, signal = count_source_files(tmp_path)
        assert count == 1

    def test_count_source_files_recursive(self, tmp_path):
        """count_source_files() should count files recursively."""
        src = tmp_path / "src"
        src.mkdir()
        (tmp_path / "main.py").write_text("# main")
        (src / "module.py").write_text("# module")
        count, signal = count_source_files(tmp_path)
        assert count == 2

    def test_count_source_files_excludes_node_modules(self, tmp_path):
        """count_source_files() should exclude node_modules directory."""
        nm = tmp_path / "node_modules"
        nm.mkdir()
        (tmp_path / "app.js").write_text("// app")
        (nm / "lodash.js").write_text("// lodash")
        count, signal = count_source_files(tmp_path)
        assert count == 1

    def test_count_source_files_excludes_venv(self, tmp_path):
        """count_source_files() should exclude venv directory."""
        venv = tmp_path / "venv"
        venv.mkdir()
        (tmp_path / "app.py").write_text("# app")
        (venv / "activate.py").write_text("# activate")
        count, signal = count_source_files(tmp_path)
        assert count == 1

    def test_count_source_files_excludes_pycache(self, tmp_path):
        """count_source_files() should exclude __pycache__ directory."""
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (tmp_path / "app.py").write_text("# app")
        (cache / "app.cpython-311.pyc").write_text("")
        count, signal = count_source_files(tmp_path)
        assert count == 1

    def test_count_source_files_signal_detected_when_few(self, tmp_path):
        """count_source_files() signal should be detected=False for < 10 files."""
        for i in range(5):
            (tmp_path / f"file{i}.py").write_text("")
        count, signal = count_source_files(tmp_path)
        assert signal.detected is False  # Few files = greenfield signal

    def test_count_source_files_signal_detected_when_many(self, tmp_path):
        """count_source_files() signal should be detected=True for >= 10 files."""
        for i in range(15):
            (tmp_path / f"file{i}.py").write_text("")
        count, signal = count_source_files(tmp_path)
        assert signal.detected is True  # Many files = brownfield signal

    def test_count_source_files_empty_directory(self, tmp_path):
        """count_source_files() should handle empty directory."""
        count, signal = count_source_files(tmp_path)
        assert count == 0
        assert signal.detected is False


# =============================================================================
# Task 5 & 6: Detection Logic and Main Function Tests
# =============================================================================


class TestDetectProjectTypeFunction:
    """Tests for detect_project_type() main function (Task 5 & 6)."""

    def test_detect_project_type_returns_project_type_result(self, tmp_path):
        """detect_project_type() should return ProjectTypeResult."""
        result = detect_project_type(tmp_path)
        assert isinstance(result, ProjectTypeResult)

    def test_detect_project_type_has_detection_signals(self, tmp_path):
        """detect_project_type() result should include detection signals."""
        result = detect_project_type(tmp_path)
        assert isinstance(result.detection_signals, list)

    def test_detect_project_type_has_confidence(self, tmp_path):
        """detect_project_type() result should include confidence score."""
        result = detect_project_type(tmp_path)
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0


class TestDetectProjectTypeGreenfield:
    """Tests for greenfield detection scenarios (AC #1)."""

    def test_empty_directory_is_greenfield(self, tmp_path):
        """Empty directory should be detected as greenfield."""
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.GREENFIELD

    def test_only_readme_is_greenfield(self, tmp_path):
        """Directory with only readme is greenfield."""
        (tmp_path / "README.md").write_text("# My Project")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.GREENFIELD

    def test_few_source_files_no_structure_is_greenfield(self, tmp_path):
        """< 10 source files with no source dirs or package files is greenfield."""
        for i in range(5):
            (tmp_path / f"file{i}.py").write_text(f"# file {i}")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.GREENFIELD

    def test_greenfield_no_source_dirs(self, tmp_path):
        """Project without src/lib/app directories can be greenfield."""
        (tmp_path / "docs").mkdir()
        (tmp_path / "main.py").write_text("# main")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.GREENFIELD

    def test_greenfield_signals_include_no_detections(self, tmp_path):
        """Greenfield detection signals should show no brownfield indicators."""
        result = detect_project_type(tmp_path)
        # All signals should have detected=False for greenfield
        detected_signals = [s for s in result.detection_signals if s.detected]
        assert len(detected_signals) == 0


class TestDetectProjectTypeBrownfield:
    """Tests for brownfield detection scenarios (AC #2, #3)."""

    def test_src_directory_with_50_files_is_brownfield(self, tmp_path):
        """src/ with 50+ files is brownfield (AC #2)."""
        src = tmp_path / "src"
        src.mkdir()
        for i in range(55):
            (src / f"module{i}.py").write_text(f"# module {i}")
        (tmp_path / "package.json").write_text('{"name": "test"}')
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.BROWNFIELD

    def test_package_json_alone_is_brownfield(self, tmp_path):
        """package.json without source dirs is brownfield (AC #3)."""
        (tmp_path / "package.json").write_text('{"name": "test"}')
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.BROWNFIELD

    def test_pyproject_toml_alone_is_brownfield(self, tmp_path):
        """pyproject.toml alone indicates brownfield."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"')
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.BROWNFIELD

    def test_src_directory_is_brownfield(self, tmp_path):
        """Presence of src/ directory indicates brownfield."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# main")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.BROWNFIELD

    def test_lib_directory_is_brownfield(self, tmp_path):
        """Presence of lib/ directory indicates brownfield."""
        (tmp_path / "lib").mkdir()
        (tmp_path / "lib" / "utils.py").write_text("# utils")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.BROWNFIELD

    def test_app_directory_is_brownfield(self, tmp_path):
        """Presence of app/ directory indicates brownfield."""
        (tmp_path / "app").mkdir()
        (tmp_path / "app" / "main.py").write_text("# main")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.BROWNFIELD

    def test_many_source_files_is_brownfield(self, tmp_path):
        """10+ source files indicates brownfield."""
        for i in range(15):
            (tmp_path / f"module{i}.py").write_text(f"# module {i}")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.BROWNFIELD

    def test_brownfield_signals_show_detections(self, tmp_path):
        """Brownfield detection signals should show what was detected."""
        (tmp_path / "src").mkdir()
        (tmp_path / "package.json").write_text('{}')
        result = detect_project_type(tmp_path)
        # Should have at least one detected signal
        detected_signals = [s for s in result.detection_signals if s.detected]
        assert len(detected_signals) >= 1


class TestDetectProjectTypeSignals:
    """Tests for detection signal transparency (AC #4)."""

    def test_signals_include_source_directory_checks(self, tmp_path):
        """Detection signals should include source directory check results."""
        (tmp_path / "src").mkdir()
        result = detect_project_type(tmp_path)
        signal_names = [s.name for s in result.detection_signals]
        # Should have a signal related to source directories
        assert any("src" in name.lower() or "directory" in name.lower() for name in signal_names)

    def test_signals_include_package_file_checks(self, tmp_path):
        """Detection signals should include package file check results."""
        (tmp_path / "package.json").write_text('{}')
        result = detect_project_type(tmp_path)
        signal_names = [s.name for s in result.detection_signals]
        # Should have a signal related to package files
        assert any("package" in name.lower() for name in signal_names)

    def test_signals_include_source_file_count(self, tmp_path):
        """Detection signals should include source file count."""
        for i in range(5):
            (tmp_path / f"file{i}.py").write_text("")
        result = detect_project_type(tmp_path)
        signal_names = [s.name for s in result.detection_signals]
        # Should have a signal related to source files
        assert any("source" in name.lower() or "files" in name.lower() for name in signal_names)


class TestDetectProjectTypeEdgeCases:
    """Tests for edge cases in project type detection."""

    def test_nonexistent_path_raises_or_handles(self, tmp_path):
        """Non-existent path should raise FileNotFoundError."""
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError):
            detect_project_type(nonexistent)

    def test_file_instead_of_directory_raises(self, tmp_path):
        """File path instead of directory should raise NotADirectoryError."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")
        with pytest.raises(NotADirectoryError):
            detect_project_type(file_path)

    def test_confidence_higher_with_more_signals(self, tmp_path):
        """Confidence should reflect signal strength."""
        # Clear brownfield indicators should have high confidence
        src = tmp_path / "src"
        src.mkdir()
        for i in range(20):
            (src / f"mod{i}.py").write_text("")
        (tmp_path / "package.json").write_text('{}')
        result = detect_project_type(tmp_path)
        assert result.confidence >= 0.8


# =============================================================================
# Story 2a.6: Workflow Configuration Parsing Tests
# =============================================================================


from pcmrp_tools.bmad_automation.workflow_entry_wrapper import (
    ConfigParseError,
    WorkflowConfig,
)


# =============================================================================
# Task 1: WorkflowConfig Dataclass Tests
# =============================================================================


class TestConfigParseError:
    """Tests for ConfigParseError dataclass (Task 1.1)."""

    def test_create_basic_error(self):
        """Test creating error with just message."""
        error = ConfigParseError(message="Parse failed")
        assert error.message == "Parse failed"
        assert error.line_number is None
        assert error.details == ""

    def test_create_error_with_line_number(self):
        """Test creating error with line number."""
        error = ConfigParseError(message="Syntax error", line_number=5)
        assert error.message == "Syntax error"
        assert error.line_number == 5

    def test_create_error_with_all_fields(self):
        """Test creating error with all fields."""
        error = ConfigParseError(
            message="Invalid YAML",
            line_number=10,
            details="Expected colon after key",
        )
        assert error.message == "Invalid YAML"
        assert error.line_number == 10
        assert error.details == "Expected colon after key"

    def test_error_serialization(self):
        """Test that error can be serialized to dict."""
        error = ConfigParseError(
            message="config_parse_error",
            line_number=5,
            details="Invalid syntax",
        )
        data = asdict(error)
        assert data["message"] == "config_parse_error"
        assert data["line_number"] == 5
        assert data["details"] == "Invalid syntax"


class TestWorkflowConfigDataclass:
    """Tests for WorkflowConfig dataclass basic functionality (Task 1.2)."""

    def test_create_basic_config(self):
        """Test creating basic config with required fields."""
        config = WorkflowConfig(module=BMADModule.CORE)
        assert config.module == BMADModule.CORE
        assert config.settings == {}
        assert config.thresholds == {}
        assert config.raw_config == {}
        assert config.error is None

    def test_create_config_with_settings(self):
        """Test creating config with settings."""
        config = WorkflowConfig(
            module=BMADModule.BMM, settings={"batch_size": 5, "oversight": "required"}
        )
        assert config.settings["batch_size"] == 5
        assert config.settings["oversight"] == "required"

    def test_create_config_with_thresholds(self):
        """Test creating config with thresholds."""
        config = WorkflowConfig(
            module=BMADModule.BMB,
            thresholds={"blocking_errors": 3, "major_issues": 5},
        )
        assert config.thresholds["blocking_errors"] == 3
        assert config.thresholds["major_issues"] == 5

    def test_create_config_with_error(self):
        """Test creating config with error."""
        error = ConfigParseError(message="Parse failed", line_number=3)
        config = WorkflowConfig(module=BMADModule.CORE, error=error)
        assert config.error is not None
        assert config.error.message == "Parse failed"

    def test_config_serialization(self):
        """Test that config can be serialized to dict."""
        config = WorkflowConfig(
            module=BMADModule.BMM,
            settings={"batch_size": 5},
            thresholds={"confidence": 80},
            raw_config={"module": "bmm"},
        )
        data = asdict(config)
        assert data["module"] == BMADModule.BMM
        assert data["settings"]["batch_size"] == 5


class TestWorkflowConfigFactoryMethods:
    """Tests for WorkflowConfig factory methods (Task 1.3)."""

    def test_bmm_defaults(self):
        """Test BMM defaults factory method."""
        config = WorkflowConfig.bmm_defaults()
        assert config.module == BMADModule.BMM
        assert config.settings.get("batch_size") == 5
        assert config.settings.get("confidence_threshold") == 80
        assert config.settings.get("checkpoint_frequency") == "per_step"
        assert config.error is None

    def test_bmb_defaults(self):
        """Test BMB defaults factory method."""
        config = WorkflowConfig.bmb_defaults()
        assert config.module == BMADModule.BMB
        assert config.thresholds.get("blocking_errors") == 3
        assert config.thresholds.get("major_issues") == 5
        assert config.thresholds.get("compliance_score") == 70
        assert config.settings.get("party_mode_auto_trigger") is True
        assert config.error is None

    def test_core_defaults(self):
        """Test Core defaults factory method."""
        config = WorkflowConfig.core_defaults()
        assert config.module == BMADModule.CORE
        assert config.settings.get("batch_size") == "auto"
        assert config.settings.get("confidence_threshold") == 80
        assert config.settings.get("checkpoint_frequency") == "minimal"
        assert config.error is None

    def test_from_error(self):
        """Test from_error factory method."""
        error = ConfigParseError(
            message="config_parse_error",
            line_number=5,
            details="Invalid syntax",
        )
        config = WorkflowConfig.from_error(error)
        assert config.module == BMADModule.CORE
        assert config.error is not None
        assert config.error.message == "config_parse_error"
        assert config.error.line_number == 5


# =============================================================================
# Task 2: YAML File Parsing Tests
# =============================================================================


from pathlib import Path
from pcmrp_tools.bmad_automation.workflow_entry_wrapper import parse_yaml_config


class TestParseYamlConfig:
    """Tests for parse_yaml_config() function (Task 2.1-2.4)."""

    def test_parse_yaml_config_returns_workflow_config(self, tmp_path):
        """parse_yaml_config() should return a WorkflowConfig."""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text("module: core\n")
        result = parse_yaml_config(yaml_file)
        assert isinstance(result, WorkflowConfig)

    def test_parse_yaml_config_extracts_module(self, tmp_path):
        """parse_yaml_config() should extract module field."""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text("module: bmm\n")
        result = parse_yaml_config(yaml_file)
        assert result.module == BMADModule.BMM

    def test_parse_yaml_config_extracts_settings(self, tmp_path):
        """parse_yaml_config() should extract settings."""
        yaml_content = """
module: bmm
settings:
  batch_size: 3
  oversight: required
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        result = parse_yaml_config(yaml_file)
        assert result.settings.get("batch_size") == 3
        assert result.settings.get("oversight") == "required"

    def test_parse_yaml_config_extracts_thresholds(self, tmp_path):
        """parse_yaml_config() should extract thresholds."""
        yaml_content = """
module: bmb
thresholds:
  confidence: 85
  blocking_errors: 3
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        result = parse_yaml_config(yaml_file)
        assert result.thresholds.get("confidence") == 85
        assert result.thresholds.get("blocking_errors") == 3

    def test_parse_yaml_config_preserves_raw_config(self, tmp_path):
        """parse_yaml_config() should preserve the raw parsed config."""
        yaml_content = """
module: bmm
name: dev-story
settings:
  batch_size: 3
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        result = parse_yaml_config(yaml_file)
        assert result.raw_config.get("module") == "bmm"
        assert result.raw_config.get("name") == "dev-story"

    def test_parse_yaml_config_defaults_to_core_module(self, tmp_path):
        """parse_yaml_config() should default to core module if not specified."""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text("name: test-workflow\n")
        result = parse_yaml_config(yaml_file)
        assert result.module == BMADModule.CORE

    def test_parse_yaml_config_handles_empty_file(self, tmp_path):
        """parse_yaml_config() should handle empty file."""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text("")
        result = parse_yaml_config(yaml_file)
        assert result.module == BMADModule.CORE
        assert result.error is None

    def test_parse_yaml_config_handles_comments_only(self, tmp_path):
        """parse_yaml_config() should handle file with only comments."""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text("# This is a comment\n# Another comment\n")
        result = parse_yaml_config(yaml_file)
        assert result.module == BMADModule.CORE


# =============================================================================
# Task 3: Markdown Frontmatter Parsing Tests
# =============================================================================


from pcmrp_tools.bmad_automation.workflow_entry_wrapper import parse_frontmatter_config


class TestParseFrontmatterConfig:
    """Tests for parse_frontmatter_config() function (Task 3.1-3.4)."""

    def test_parse_frontmatter_config_returns_workflow_config(self, tmp_path):
        """parse_frontmatter_config() should return a WorkflowConfig."""
        md_file = tmp_path / "workflow.md"
        md_file.write_text("---\nmodule: core\n---\n\n# Workflow\n")
        result = parse_frontmatter_config(md_file)
        assert isinstance(result, WorkflowConfig)

    def test_parse_frontmatter_config_extracts_module(self, tmp_path):
        """parse_frontmatter_config() should extract module from frontmatter."""
        md_content = """---
module: bmb
name: agent-builder
---

# Agent Builder Workflow
"""
        md_file = tmp_path / "workflow.md"
        md_file.write_text(md_content)
        result = parse_frontmatter_config(md_file)
        assert result.module == BMADModule.BMB

    def test_parse_frontmatter_config_extracts_settings(self, tmp_path):
        """parse_frontmatter_config() should extract settings from frontmatter."""
        md_content = """---
module: bmb
settings:
  party_mode_auto_trigger: true
  batch_size: 10
---

# Workflow
"""
        md_file = tmp_path / "workflow.md"
        md_file.write_text(md_content)
        result = parse_frontmatter_config(md_file)
        assert result.settings.get("party_mode_auto_trigger") is True
        assert result.settings.get("batch_size") == 10

    def test_parse_frontmatter_config_extracts_thresholds(self, tmp_path):
        """parse_frontmatter_config() should extract thresholds from frontmatter."""
        md_content = """---
module: bmb
thresholds:
  blocking_errors: 3
  major_issues: 5
---

# Workflow
"""
        md_file = tmp_path / "workflow.md"
        md_file.write_text(md_content)
        result = parse_frontmatter_config(md_file)
        assert result.thresholds.get("blocking_errors") == 3
        assert result.thresholds.get("major_issues") == 5

    def test_parse_frontmatter_config_preserves_raw_config(self, tmp_path):
        """parse_frontmatter_config() should preserve raw config."""
        md_content = """---
module: bmm
name: dev-story
custom_field: value
---

# Dev Story Workflow
"""
        md_file = tmp_path / "workflow.md"
        md_file.write_text(md_content)
        result = parse_frontmatter_config(md_file)
        assert result.raw_config.get("module") == "bmm"
        assert result.raw_config.get("name") == "dev-story"
        assert result.raw_config.get("custom_field") == "value"

    def test_parse_frontmatter_config_defaults_to_core(self, tmp_path):
        """parse_frontmatter_config() should default to core if no module."""
        md_content = """---
name: test-workflow
---

# Test Workflow
"""
        md_file = tmp_path / "workflow.md"
        md_file.write_text(md_content)
        result = parse_frontmatter_config(md_file)
        assert result.module == BMADModule.CORE

    def test_parse_frontmatter_config_handles_no_frontmatter(self, tmp_path):
        """parse_frontmatter_config() should handle file without frontmatter."""
        md_content = """# Just a Markdown File

This file has no frontmatter.
"""
        md_file = tmp_path / "workflow.md"
        md_file.write_text(md_content)
        result = parse_frontmatter_config(md_file)
        assert result.module == BMADModule.CORE
        assert result.error is None

    def test_parse_frontmatter_config_handles_empty_frontmatter(self, tmp_path):
        """parse_frontmatter_config() should handle empty frontmatter."""
        md_content = """---
---

# Workflow
"""
        md_file = tmp_path / "workflow.md"
        md_file.write_text(md_content)
        result = parse_frontmatter_config(md_file)
        assert result.module == BMADModule.CORE

    def test_parse_frontmatter_config_handles_unclosed_frontmatter(self, tmp_path):
        """parse_frontmatter_config() should handle unclosed frontmatter."""
        md_content = """---
module: bmm

# This frontmatter is never closed
"""
        md_file = tmp_path / "workflow.md"
        md_file.write_text(md_content)
        result = parse_frontmatter_config(md_file)
        # Should return error or default to core
        assert result.module == BMADModule.CORE


# =============================================================================
# Task 4: Module-Specific Defaults Tests
# =============================================================================


from pcmrp_tools.bmad_automation.workflow_entry_wrapper import (
    get_module_defaults,
    merge_with_defaults,
)


class TestGetModuleDefaults:
    """Tests for get_module_defaults() function (Task 4.1-4.3)."""

    def test_get_module_defaults_bmm(self):
        """get_module_defaults() should return BMM defaults."""
        defaults = get_module_defaults(BMADModule.BMM)
        assert defaults.module == BMADModule.BMM
        assert defaults.settings.get("batch_size") == 5
        assert defaults.settings.get("confidence_threshold") == 80
        assert defaults.settings.get("checkpoint_frequency") == "per_step"

    def test_get_module_defaults_bmb(self):
        """get_module_defaults() should return BMB defaults with thresholds."""
        defaults = get_module_defaults(BMADModule.BMB)
        assert defaults.module == BMADModule.BMB
        assert defaults.thresholds.get("blocking_errors") == 3
        assert defaults.thresholds.get("major_issues") == 5
        assert defaults.thresholds.get("compliance_score") == 70
        assert defaults.settings.get("party_mode_auto_trigger") is True

    def test_get_module_defaults_core(self):
        """get_module_defaults() should return Core defaults."""
        defaults = get_module_defaults(BMADModule.CORE)
        assert defaults.module == BMADModule.CORE
        assert defaults.settings.get("batch_size") == "auto"
        assert defaults.settings.get("confidence_threshold") == 80
        assert defaults.settings.get("checkpoint_frequency") == "minimal"


class TestMergeWithDefaults:
    """Tests for merge_with_defaults() function (Task 4.4)."""

    def test_merge_with_defaults_applies_module_defaults(self, tmp_path):
        """merge_with_defaults() should apply module defaults."""
        yaml_content = """
module: bmm
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        config = parse_yaml_config(yaml_file)
        merged = merge_with_defaults(config)
        # Should have BMM default settings
        assert merged.settings.get("batch_size") == 5

    def test_merge_with_defaults_user_settings_override(self, tmp_path):
        """merge_with_defaults() should let user settings override defaults."""
        yaml_content = """
module: bmm
settings:
  batch_size: 10
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        config = parse_yaml_config(yaml_file)
        merged = merge_with_defaults(config)
        # User's batch_size should override default
        assert merged.settings.get("batch_size") == 10
        # But other defaults should still apply
        assert merged.settings.get("confidence_threshold") == 80

    def test_merge_with_defaults_user_thresholds_override(self, tmp_path):
        """merge_with_defaults() should let user thresholds override defaults."""
        yaml_content = """
module: bmb
thresholds:
  blocking_errors: 5
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        config = parse_yaml_config(yaml_file)
        merged = merge_with_defaults(config)
        # User's threshold should override default
        assert merged.thresholds.get("blocking_errors") == 5
        # But other thresholds should still apply
        assert merged.thresholds.get("major_issues") == 5

    def test_merge_with_defaults_preserves_raw_config(self, tmp_path):
        """merge_with_defaults() should preserve raw_config."""
        yaml_content = """
module: bmm
custom_field: value
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        config = parse_yaml_config(yaml_file)
        merged = merge_with_defaults(config)
        assert merged.raw_config.get("custom_field") == "value"


# =============================================================================
# Task 5: Error Handling Tests
# =============================================================================


class TestYamlParseErrors:
    """Tests for YAML parse error handling (Task 5.1-5.4)."""

    def test_yaml_syntax_error_returns_error(self, tmp_path):
        """YAML syntax error should return config_parse_error."""
        yaml_content = """
module: bmm
settings:
  batch_size: [unclosed bracket
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        result = parse_yaml_config(yaml_file)
        assert result.error is not None
        assert result.error.message == "config_parse_error"

    def test_yaml_syntax_error_has_line_number(self, tmp_path):
        """YAML syntax error should include line number when available."""
        yaml_content = """module: bmm
settings:
  batch_size: [unclosed
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        result = parse_yaml_config(yaml_file)
        assert result.error is not None
        # Line number should be present for syntax errors
        assert result.error.line_number is not None

    def test_yaml_syntax_error_has_details(self, tmp_path):
        """YAML syntax error should include details."""
        yaml_content = """
module: bmm
settings:
  batch_size: [unclosed
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        result = parse_yaml_config(yaml_file)
        assert result.error is not None
        assert result.error.details != ""

    def test_unknown_module_returns_error(self, tmp_path):
        """Unknown module should return config_parse_error."""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text("module: unknown_module\n")
        result = parse_yaml_config(yaml_file)
        assert result.error is not None
        assert "unknown" in result.error.details.lower()


class TestFrontmatterParseErrors:
    """Tests for frontmatter parse error handling."""

    def test_frontmatter_syntax_error_returns_error(self, tmp_path):
        """Frontmatter syntax error should return config_parse_error."""
        md_content = """---
module: bmm
settings:
  batch_size: [unclosed
---

# Workflow
"""
        md_file = tmp_path / "workflow.md"
        md_file.write_text(md_content)
        result = parse_frontmatter_config(md_file)
        assert result.error is not None
        assert result.error.message == "config_parse_error"


# =============================================================================
# Task 6: Main parse_workflow_config() Function Tests
# =============================================================================


from pcmrp_tools.bmad_automation.workflow_entry_wrapper import parse_workflow_config


class TestParseWorkflowConfig:
    """Tests for main parse_workflow_config() function (Task 6.1-6.5)."""

    def test_parse_workflow_config_auto_detects_yaml(self, tmp_path):
        """parse_workflow_config() should auto-detect .yaml files."""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text("module: bmm\n")
        result = parse_workflow_config(yaml_file)
        assert result.module == BMADModule.BMM

    def test_parse_workflow_config_auto_detects_yml(self, tmp_path):
        """parse_workflow_config() should auto-detect .yml files."""
        yml_file = tmp_path / "workflow.yml"
        yml_file.write_text("module: bmb\n")
        result = parse_workflow_config(yml_file)
        assert result.module == BMADModule.BMB

    def test_parse_workflow_config_auto_detects_markdown(self, tmp_path):
        """parse_workflow_config() should auto-detect .md files."""
        md_content = """---
module: bmm
---

# Workflow
"""
        md_file = tmp_path / "workflow.md"
        md_file.write_text(md_content)
        result = parse_workflow_config(md_file)
        assert result.module == BMADModule.BMM

    def test_parse_workflow_config_applies_module_defaults(self, tmp_path):
        """parse_workflow_config() should apply module defaults."""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text("module: bmm\n")
        result = parse_workflow_config(yaml_file)
        # Should have BMM defaults applied
        assert result.settings.get("batch_size") == 5

    def test_parse_workflow_config_returns_complete_config(self, tmp_path):
        """parse_workflow_config() should return complete WorkflowConfig."""
        yaml_content = """
module: bmb
settings:
  custom_setting: value
thresholds:
  blocking_errors: 5
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(yaml_content)
        result = parse_workflow_config(yaml_file)
        assert result.module == BMADModule.BMB
        assert result.settings.get("custom_setting") == "value"
        assert result.thresholds.get("blocking_errors") == 5
        assert result.error is None

    def test_parse_workflow_config_unknown_extension(self, tmp_path):
        """parse_workflow_config() should handle unknown file extension."""
        txt_file = tmp_path / "workflow.txt"
        txt_file.write_text("module: bmm\n")
        result = parse_workflow_config(txt_file)
        # Should try YAML parsing as fallback
        assert result.module in [BMADModule.BMM, BMADModule.CORE]

    def test_parse_workflow_config_nonexistent_file(self, tmp_path):
        """parse_workflow_config() should handle nonexistent file."""
        nonexistent = tmp_path / "nonexistent.yaml"
        result = parse_workflow_config(nonexistent)
        assert result.error is not None
