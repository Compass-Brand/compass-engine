"""Tests for Cross-Reference Validator component.

This module tests the AlignmentResult, AlignmentIssue dataclasses and
the cross-reference validation functionality for BMAD document alignment.

TDD Pattern: Tests written FIRST before implementation.

Story 1.3: Cross-Reference Document Alignment
"""

import pytest

from pcmrp_tools.bmad_automation.cross_reference_validator import (
    Severity,
    AlignmentStatus,
    AlignmentIssue,
    AlignmentResult,
    FR_PATTERNS,
    ADR_PATTERNS,
    extract_frs_from_content,
    extract_adrs_from_content,
    detect_orphaned_requirements,
    detect_unaddressed_decisions,
    validate_alignment,
)


# =============================================================================
# Task 1: AlignmentResult Dataclass Tests
# =============================================================================


class TestSeverityEnum:
    """Tests for Severity enum (Subtask 1.3)."""

    def test_severity_high_value(self):
        """Test Severity.HIGH has correct string value."""
        assert Severity.HIGH.value == "HIGH"

    def test_severity_medium_value(self):
        """Test Severity.MEDIUM has correct string value."""
        assert Severity.MEDIUM.value == "MEDIUM"

    def test_severity_low_value(self):
        """Test Severity.LOW has correct string value."""
        assert Severity.LOW.value == "LOW"

    def test_all_severity_members_exist(self):
        """Test all required severity enum members exist."""
        expected_members = {"HIGH", "MEDIUM", "LOW"}
        actual_members = {member.name for member in Severity}
        assert expected_members == actual_members

    def test_severity_comparison_ordering(self):
        """Test severity levels can be compared for sorting."""
        # Define explicit priority: HIGH > MEDIUM > LOW
        priority = {Severity.HIGH: 3, Severity.MEDIUM: 2, Severity.LOW: 1}
        assert priority[Severity.HIGH] > priority[Severity.MEDIUM]
        assert priority[Severity.MEDIUM] > priority[Severity.LOW]


class TestAlignmentStatusEnum:
    """Tests for AlignmentStatus enum."""

    def test_alignment_status_aligned_value(self):
        """Test AlignmentStatus.ALIGNED has correct string value."""
        assert AlignmentStatus.ALIGNED.value == "ALIGNED"

    def test_alignment_status_misaligned_value(self):
        """Test AlignmentStatus.MISALIGNED has correct string value."""
        assert AlignmentStatus.MISALIGNED.value == "MISALIGNED"

    def test_all_alignment_status_members_exist(self):
        """Test all required alignment status enum members exist."""
        expected_members = {"ALIGNED", "MISALIGNED"}
        actual_members = {member.name for member in AlignmentStatus}
        assert expected_members == actual_members


class TestAlignmentIssue:
    """Tests for AlignmentIssue dataclass (Subtask 1.1)."""

    def test_create_alignment_issue_all_fields(self):
        """Test creating AlignmentIssue with all required fields."""
        issue = AlignmentIssue(
            issue_type="orphaned_requirements",
            items=["FR3", "FR5"],
            severity=Severity.HIGH,
            affected_components=["Authentication", "API Gateway"],
            message="Requirements not referenced in Architecture",
        )
        assert issue.issue_type == "orphaned_requirements"
        assert issue.items == ["FR3", "FR5"]
        assert issue.severity == Severity.HIGH
        assert issue.affected_components == ["Authentication", "API Gateway"]
        assert issue.message == "Requirements not referenced in Architecture"

    def test_alignment_issue_default_affected_components(self):
        """Test AlignmentIssue has empty list default for affected_components."""
        issue = AlignmentIssue(
            issue_type="orphaned_requirements",
            items=["FR1"],
            severity=Severity.HIGH,
        )
        assert issue.affected_components == []

    def test_alignment_issue_default_message(self):
        """Test AlignmentIssue has empty string default for message."""
        issue = AlignmentIssue(
            issue_type="orphaned_requirements",
            items=["FR1"],
            severity=Severity.HIGH,
        )
        assert issue.message == ""

    def test_alignment_issue_to_dict(self):
        """Test AlignmentIssue can be serialized to dictionary."""
        issue = AlignmentIssue(
            issue_type="unaddressed_decisions",
            items=["ADR-001"],
            severity=Severity.MEDIUM,
            affected_components=["Database"],
            message="Decision not addressed in stories",
        )
        issue_dict = issue.to_dict()
        assert issue_dict["issue_type"] == "unaddressed_decisions"
        assert issue_dict["items"] == ["ADR-001"]
        assert issue_dict["severity"] == "MEDIUM"
        assert issue_dict["affected_components"] == ["Database"]
        assert issue_dict["message"] == "Decision not addressed in stories"

    def test_alignment_issue_from_dict(self):
        """Test AlignmentIssue can be created from dictionary."""
        data = {
            "issue_type": "orphaned_requirements",
            "items": ["FR2"],
            "severity": "HIGH",
            "affected_components": ["Frontend"],
            "message": "Test message",
        }
        issue = AlignmentIssue.from_dict(data)
        assert issue.issue_type == "orphaned_requirements"
        assert issue.items == ["FR2"]
        assert issue.severity == Severity.HIGH
        assert issue.affected_components == ["Frontend"]
        assert issue.message == "Test message"


class TestAlignmentResult:
    """Tests for AlignmentResult dataclass (Subtask 1.2)."""

    def test_create_alignment_result_all_fields(self):
        """Test creating AlignmentResult with all required fields."""
        issue = AlignmentIssue(
            issue_type="orphaned_requirements",
            items=["FR3"],
            severity=Severity.HIGH,
        )
        result = AlignmentResult(
            alignment_status=AlignmentStatus.MISALIGNED,
            issues=[issue],
            documents_checked=["PRD.md", "Architecture.md"],
        )
        assert result.alignment_status == AlignmentStatus.MISALIGNED
        assert len(result.issues) == 1
        assert result.documents_checked == ["PRD.md", "Architecture.md"]

    def test_alignment_result_default_issues(self):
        """Test AlignmentResult has empty list default for issues."""
        result = AlignmentResult(
            alignment_status=AlignmentStatus.ALIGNED,
            documents_checked=["PRD.md"],
        )
        assert result.issues == []

    def test_alignment_result_default_documents_checked(self):
        """Test AlignmentResult has empty list default for documents_checked."""
        result = AlignmentResult(
            alignment_status=AlignmentStatus.ALIGNED,
        )
        assert result.documents_checked == []


class TestAlignmentResultFactoryMethods:
    """Tests for AlignmentResult factory methods (Subtask 1.4)."""

    def test_aligned_factory(self):
        """Test factory method for aligned result."""
        result = AlignmentResult.aligned(
            documents_checked=["PRD.md", "Architecture.md", "Stories.md"]
        )
        assert result.alignment_status == AlignmentStatus.ALIGNED
        assert result.issues == []
        assert result.documents_checked == ["PRD.md", "Architecture.md", "Stories.md"]

    def test_misaligned_factory(self):
        """Test factory method for misaligned result."""
        issue = AlignmentIssue(
            issue_type="orphaned_requirements",
            items=["FR3"],
            severity=Severity.HIGH,
        )
        result = AlignmentResult.misaligned(
            issues=[issue],
            documents_checked=["PRD.md", "Architecture.md"],
        )
        assert result.alignment_status == AlignmentStatus.MISALIGNED
        assert len(result.issues) == 1
        assert result.issues[0].items == ["FR3"]


class TestAlignmentResultSerialization:
    """Tests for AlignmentResult serialization (Subtask 1.5)."""

    def test_to_dict_aligned(self):
        """Test serializing aligned result to dictionary."""
        result = AlignmentResult.aligned(documents_checked=["PRD.md"])
        result_dict = result.to_dict()
        assert result_dict["alignment_status"] == "ALIGNED"
        assert result_dict["issues"] == []
        assert result_dict["documents_checked"] == ["PRD.md"]

    def test_to_dict_misaligned_with_issues(self):
        """Test serializing misaligned result with issues to dictionary."""
        issue = AlignmentIssue(
            issue_type="orphaned_requirements",
            items=["FR3"],
            severity=Severity.HIGH,
            message="Test",
        )
        result = AlignmentResult.misaligned(
            issues=[issue],
            documents_checked=["PRD.md", "Architecture.md"],
        )
        result_dict = result.to_dict()
        assert result_dict["alignment_status"] == "MISALIGNED"
        assert len(result_dict["issues"]) == 1
        assert result_dict["issues"][0]["items"] == ["FR3"]

    def test_from_dict(self):
        """Test creating AlignmentResult from dictionary."""
        data = {
            "alignment_status": "MISALIGNED",
            "issues": [
                {
                    "issue_type": "orphaned_requirements",
                    "items": ["FR3"],
                    "severity": "HIGH",
                    "affected_components": [],
                    "message": "",
                }
            ],
            "documents_checked": ["PRD.md"],
        }
        result = AlignmentResult.from_dict(data)
        assert result.alignment_status == AlignmentStatus.MISALIGNED
        assert len(result.issues) == 1
        assert result.issues[0].items == ["FR3"]

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are inverse operations."""
        issue = AlignmentIssue(
            issue_type="unaddressed_decisions",
            items=["ADR-001", "ADR-002"],
            severity=Severity.MEDIUM,
            affected_components=["Database", "API"],
            message="Decisions not covered",
        )
        original = AlignmentResult(
            alignment_status=AlignmentStatus.MISALIGNED,
            issues=[issue],
            documents_checked=["PRD.md", "Architecture.md", "Stories.md"],
        )
        serialized = original.to_dict()
        restored = AlignmentResult.from_dict(serialized)
        assert restored.alignment_status == original.alignment_status
        assert len(restored.issues) == len(original.issues)
        assert restored.documents_checked == original.documents_checked


# =============================================================================
# Task 2: FR Extraction Tests
# =============================================================================


class TestFRPatterns:
    """Tests for FR_PATTERNS constant (Subtask 2.1)."""

    def test_fr_patterns_exists(self):
        """Test FR_PATTERNS constant is defined."""
        assert FR_PATTERNS is not None

    def test_fr_patterns_is_list(self):
        """Test FR_PATTERNS is a list of compiled regex patterns."""
        import re
        assert isinstance(FR_PATTERNS, list)
        for pattern in FR_PATTERNS:
            assert isinstance(pattern, re.Pattern)


class TestExtractFRsFromContent:
    """Tests for extract_frs_from_content function (Subtask 2.2-2.4)."""

    def test_extract_fr_simple(self):
        """Test extracting simple FR1, FR2, FR3 format."""
        content = "This document defines FR1, FR2, and FR3."
        frs = extract_frs_from_content(content)
        assert "FR1" in frs
        assert "FR2" in frs
        assert "FR3" in frs

    def test_extract_fr_hyphenated(self):
        """Test extracting hyphenated FR-1, FR-2, FR-3 format (normalized to no hyphen)."""
        content = "Requirements include FR-1, FR-2, and FR-3."
        frs = extract_frs_from_content(content)
        # Normalized to uppercase without hyphen
        assert "FR1" in frs
        assert "FR2" in frs
        assert "FR3" in frs

    def test_extract_fr_padded(self):
        """Test extracting zero-padded FR01, FR02 format."""
        content = "See FR01 and FR02 for details."
        frs = extract_frs_from_content(content)
        assert "FR01" in frs
        assert "FR02" in frs

    def test_extract_fr_lowercase(self):
        """Test extracting lowercase fr1, fr2 format."""
        content = "The requirements fr1 and fr2 are important."
        frs = extract_frs_from_content(content)
        # Should normalize to uppercase
        assert any("1" in fr for fr in frs)

    def test_extract_fr_mixed_case(self):
        """Test extracting mixed case Fr1, fR2 format."""
        content = "Fr1 and FR2 are referenced."
        frs = extract_frs_from_content(content)
        assert len(frs) >= 2

    def test_extract_fr_from_prd(self):
        """Test extracting FRs from realistic PRD content (Subtask 2.2)."""
        content = """
        # Product Requirements Document

        ## Functional Requirements

        ### FR1: User Authentication
        Users must be able to log in with email and password.

        ### FR2: Dashboard Access
        Authenticated users can access the main dashboard.

        ### FR3: Report Generation
        System must generate PDF reports.
        """
        frs = extract_frs_from_content(content)
        assert "FR1" in frs
        assert "FR2" in frs
        assert "FR3" in frs

    def test_extract_fr_from_architecture(self):
        """Test extracting FR references from Architecture doc (Subtask 2.3)."""
        content = """
        # Architecture Document

        ## Component: Auth Service
        Implements FR1 (User Authentication).

        ## Component: Dashboard
        Implements FR2 (Dashboard Access).

        Note: FR3 will be handled in Phase 2.
        """
        frs = extract_frs_from_content(content)
        assert "FR1" in frs
        assert "FR2" in frs
        assert "FR3" in frs

    def test_extract_fr_from_stories(self):
        """Test extracting FR references from Stories doc (Subtask 2.4)."""
        content = """
        # Epic 1: Authentication

        ## Story 1.1: Login Form
        Addresses: FR1

        ## Story 1.2: Dashboard
        Addresses: FR2
        """
        frs = extract_frs_from_content(content)
        assert "FR1" in frs
        assert "FR2" in frs

    def test_extract_fr_empty_content(self):
        """Test extracting FRs from empty content returns empty set."""
        frs = extract_frs_from_content("")
        assert frs == set()

    def test_extract_fr_no_matches(self):
        """Test extracting FRs from content with no FRs returns empty set."""
        content = "This document has no functional requirements."
        frs = extract_frs_from_content(content)
        assert frs == set()

    def test_extract_fr_deduplication(self):
        """Test that duplicate FRs are deduplicated."""
        content = "FR1 is mentioned here. FR1 is mentioned again. FR1!"
        frs = extract_frs_from_content(content)
        # Should only have one FR1
        assert len([fr for fr in frs if "1" in fr]) == 1

    def test_extract_fr_ignores_code_blocks(self):
        """Test that FRs inside code blocks are ignored."""
        content = """
        Real FR1 reference.
        ```
        FR2 in code block should be ignored
        ```
        Real FR3 reference.
        """
        frs = extract_frs_from_content(content)
        assert "FR1" in frs
        assert "FR3" in frs
        # FR2 should be ignored since it's in code block
        assert "FR2" not in frs


# =============================================================================
# Task 3: ADR/Decision Extraction Tests
# =============================================================================


class TestADRPatterns:
    """Tests for ADR_PATTERNS constant (Subtask 3.1)."""

    def test_adr_patterns_exists(self):
        """Test ADR_PATTERNS constant is defined."""
        assert ADR_PATTERNS is not None

    def test_adr_patterns_is_list(self):
        """Test ADR_PATTERNS is a list of compiled regex patterns."""
        import re
        assert isinstance(ADR_PATTERNS, list)
        for pattern in ADR_PATTERNS:
            assert isinstance(pattern, re.Pattern)


class TestExtractADRsFromContent:
    """Tests for extract_adrs_from_content function (Subtask 3.2-3.3)."""

    def test_extract_adr_simple(self):
        """Test extracting simple ADR-001, ADR-002 format."""
        content = "This follows ADR-001 and ADR-002."
        adrs = extract_adrs_from_content(content)
        assert "ADR-001" in adrs
        assert "ADR-002" in adrs

    def test_extract_adr_no_hyphen(self):
        """Test extracting ADR001, ADR002 format (no hyphen)."""
        content = "See ADR001 and ADR002 for decisions."
        adrs = extract_adrs_from_content(content)
        assert any("001" in adr for adr in adrs)
        assert any("002" in adr for adr in adrs)

    def test_extract_decision_format(self):
        """Test extracting Decision-1, Decision-2 format."""
        content = "Based on Decision-1 and Decision-2."
        adrs = extract_adrs_from_content(content)
        assert any("1" in adr for adr in adrs)
        assert any("2" in adr for adr in adrs)

    def test_extract_decision_no_hyphen(self):
        """Test extracting Decision1, Decision2 format (no hyphen, normalized to have hyphen)."""
        content = "See Decision1 and Decision2 for guidance."
        adrs = extract_adrs_from_content(content)
        # Should normalize to DECISION-1, DECISION-2
        assert "DECISION-1" in adrs
        assert "DECISION-2" in adrs

    def test_extract_adr_lowercase(self):
        """Test extracting lowercase adr-001 format."""
        content = "According to adr-001 and adr-002."
        adrs = extract_adrs_from_content(content)
        # Should find these (case insensitive)
        assert len(adrs) >= 2

    def test_extract_adr_from_architecture(self):
        """Test extracting ADRs from Architecture document (Subtask 3.2)."""
        content = """
        # Architecture Document

        ## ADR-001: Database Selection
        We chose PostgreSQL for its reliability.

        ## ADR-002: API Framework
        We selected FastAPI for its performance.

        ## ADR-003: Caching Strategy
        Redis for distributed caching.
        """
        adrs = extract_adrs_from_content(content)
        assert "ADR-001" in adrs
        assert "ADR-002" in adrs
        assert "ADR-003" in adrs

    def test_extract_adr_from_stories(self):
        """Test extracting ADR references from Stories (Subtask 3.3)."""
        content = """
        # Story 1.1: Database Setup

        Implements ADR-001 (Database Selection).

        # Story 1.2: API Implementation

        Follows ADR-002 guidelines.
        """
        adrs = extract_adrs_from_content(content)
        assert "ADR-001" in adrs
        assert "ADR-002" in adrs

    def test_extract_adr_empty_content(self):
        """Test extracting ADRs from empty content returns empty set."""
        adrs = extract_adrs_from_content("")
        assert adrs == set()

    def test_extract_adr_no_matches(self):
        """Test extracting ADRs from content with no ADRs returns empty set."""
        content = "This document has no architectural decisions."
        adrs = extract_adrs_from_content(content)
        assert adrs == set()

    def test_extract_adr_deduplication(self):
        """Test that duplicate ADRs are deduplicated."""
        content = "ADR-001 mentioned here. ADR-001 mentioned again."
        adrs = extract_adrs_from_content(content)
        assert len([adr for adr in adrs if "001" in adr]) == 1

    def test_extract_adr_ignores_code_blocks(self):
        """Test that ADRs inside code blocks are ignored."""
        content = """
        Real ADR-001 reference.
        ```
        ADR-002 in code block should be ignored
        ```
        Real ADR-003 reference.
        """
        adrs = extract_adrs_from_content(content)
        assert "ADR-001" in adrs
        assert "ADR-003" in adrs
        assert "ADR-002" not in adrs


# =============================================================================
# Task 4: Orphaned Requirements Detection Tests (AC: #1)
# =============================================================================


class TestDetectOrphanedRequirements:
    """Tests for detect_orphaned_requirements function (Subtask 4.1-4.3)."""

    def test_detect_orphaned_single_fr(self):
        """Test detecting single orphaned FR (AC: #1 exact scenario)."""
        prd_frs = {"FR1", "FR2", "FR3"}
        arch_frs = {"FR1", "FR2"}  # FR3 not referenced

        issues = detect_orphaned_requirements(prd_frs, arch_frs)

        assert len(issues) == 1
        assert issues[0].issue_type == "orphaned_requirements"
        assert "FR3" in issues[0].items
        assert issues[0].severity == Severity.HIGH

    def test_detect_orphaned_multiple_frs(self):
        """Test detecting multiple orphaned FRs."""
        prd_frs = {"FR1", "FR2", "FR3", "FR4", "FR5"}
        arch_frs = {"FR1", "FR3"}  # FR2, FR4, FR5 not referenced

        issues = detect_orphaned_requirements(prd_frs, arch_frs)

        assert len(issues) == 1
        orphaned = issues[0].items
        assert "FR2" in orphaned
        assert "FR4" in orphaned
        assert "FR5" in orphaned

    def test_detect_no_orphaned_requirements(self):
        """Test no issues when all FRs are referenced."""
        prd_frs = {"FR1", "FR2", "FR3"}
        arch_frs = {"FR1", "FR2", "FR3"}

        issues = detect_orphaned_requirements(prd_frs, arch_frs)

        assert issues == []

    def test_detect_orphaned_empty_prd(self):
        """Test handling empty PRD FRs."""
        prd_frs = set()
        arch_frs = {"FR1", "FR2"}

        issues = detect_orphaned_requirements(prd_frs, arch_frs)

        assert issues == []

    def test_detect_orphaned_empty_architecture(self):
        """Test all FRs orphaned when Architecture has none."""
        prd_frs = {"FR1", "FR2", "FR3"}
        arch_frs = set()

        issues = detect_orphaned_requirements(prd_frs, arch_frs)

        assert len(issues) == 1
        assert len(issues[0].items) == 3

    def test_orphaned_severity_is_high(self):
        """Test orphaned requirements have HIGH severity (AC: #1)."""
        prd_frs = {"FR1", "FR2"}
        arch_frs = {"FR1"}

        issues = detect_orphaned_requirements(prd_frs, arch_frs)

        assert issues[0].severity == Severity.HIGH

    def test_orphaned_issue_has_descriptive_message(self):
        """Test orphaned issue has a descriptive message."""
        prd_frs = {"FR1", "FR2"}
        arch_frs = {"FR1"}

        issues = detect_orphaned_requirements(prd_frs, arch_frs)

        assert issues[0].message != ""
        assert "not referenced" in issues[0].message.lower() or "orphaned" in issues[0].message.lower()


# =============================================================================
# Task 5: Unaddressed Decisions Detection Tests (AC: #2)
# =============================================================================


class TestDetectUnaddressedDecisions:
    """Tests for detect_unaddressed_decisions function (Subtask 5.1-5.3)."""

    def test_detect_unaddressed_single_adr(self):
        """Test detecting single unaddressed ADR (AC: #2 exact scenario)."""
        arch_adrs = {"ADR-001", "ADR-002"}
        story_adrs = {"ADR-002"}  # ADR-001 not addressed

        issues = detect_unaddressed_decisions(arch_adrs, story_adrs)

        assert len(issues) == 1
        assert issues[0].issue_type == "unaddressed_decisions"
        assert "ADR-001" in issues[0].items

    def test_detect_unaddressed_multiple_adrs(self):
        """Test detecting multiple unaddressed ADRs."""
        arch_adrs = {"ADR-001", "ADR-002", "ADR-003", "ADR-004"}
        story_adrs = {"ADR-002"}  # ADR-001, ADR-003, ADR-004 not addressed

        issues = detect_unaddressed_decisions(arch_adrs, story_adrs)

        assert len(issues) == 1
        unaddressed = issues[0].items
        assert "ADR-001" in unaddressed
        assert "ADR-003" in unaddressed
        assert "ADR-004" in unaddressed

    def test_detect_no_unaddressed_decisions(self):
        """Test no issues when all ADRs are addressed."""
        arch_adrs = {"ADR-001", "ADR-002"}
        story_adrs = {"ADR-001", "ADR-002"}

        issues = detect_unaddressed_decisions(arch_adrs, story_adrs)

        assert issues == []

    def test_detect_unaddressed_empty_architecture(self):
        """Test handling empty Architecture ADRs."""
        arch_adrs = set()
        story_adrs = {"ADR-001"}

        issues = detect_unaddressed_decisions(arch_adrs, story_adrs)

        assert issues == []

    def test_detect_unaddressed_empty_stories(self):
        """Test all ADRs unaddressed when Stories has none."""
        arch_adrs = {"ADR-001", "ADR-002"}
        story_adrs = set()

        issues = detect_unaddressed_decisions(arch_adrs, story_adrs)

        assert len(issues) == 1
        assert len(issues[0].items) == 2

    def test_unaddressed_has_affected_components(self):
        """Test unaddressed decisions include affected components (AC: #2)."""
        arch_adrs = {"ADR-001"}
        story_adrs = set()
        # In real implementation, affected_components comes from document context

        issues = detect_unaddressed_decisions(arch_adrs, story_adrs)

        # The function should return issues with affected_components field
        assert hasattr(issues[0], "affected_components")

    def test_unaddressed_issue_has_descriptive_message(self):
        """Test unaddressed issue has a descriptive message."""
        arch_adrs = {"ADR-001"}
        story_adrs = set()

        issues = detect_unaddressed_decisions(arch_adrs, story_adrs)

        assert issues[0].message != ""
        assert "not addressed" in issues[0].message.lower() or "unaddressed" in issues[0].message.lower()


# =============================================================================
# Task 6: Main validate_alignment() Function Tests (AC: #1-4)
# =============================================================================


class TestValidateAlignmentOrphaned:
    """Tests for validate_alignment with orphaned requirements (AC: #1)."""

    def test_detects_orphaned_fr_in_full_validation(self):
        """Test full validation detects orphaned FR (AC: #1 exact scenario)."""
        prd_content = """
        # PRD
        ## FR1: Auth
        ## FR2: Dashboard
        ## FR3: Reports
        """
        arch_content = """
        # Architecture
        Implements FR1 and FR2.
        """
        stories_content = """
        # Stories
        Story for FR1.
        Story for FR2.
        """

        result = validate_alignment(prd_content, arch_content, stories_content)

        assert result.alignment_status == AlignmentStatus.MISALIGNED
        orphaned_issues = [i for i in result.issues if i.issue_type == "orphaned_requirements"]
        assert len(orphaned_issues) == 1
        assert "FR3" in orphaned_issues[0].items
        assert orphaned_issues[0].severity == Severity.HIGH


class TestValidateAlignmentUnaddressed:
    """Tests for validate_alignment with unaddressed decisions (AC: #2)."""

    def test_detects_unaddressed_adr_in_full_validation(self):
        """Test full validation detects unaddressed ADR (AC: #2 exact scenario)."""
        prd_content = """
        # PRD
        ## FR1: Feature
        """
        arch_content = """
        # Architecture

        ## ADR-001: Database Choice
        Use PostgreSQL.

        Implements FR1.
        """
        stories_content = """
        # Stories
        Story for FR1.
        No ADR references here.
        """

        result = validate_alignment(prd_content, arch_content, stories_content)

        assert result.alignment_status == AlignmentStatus.MISALIGNED
        unaddressed_issues = [i for i in result.issues if i.issue_type == "unaddressed_decisions"]
        assert len(unaddressed_issues) == 1
        assert "ADR-001" in unaddressed_issues[0].items


class TestValidateAlignmentAligned:
    """Tests for validate_alignment with aligned documents (AC: #3)."""

    def test_aligned_documents_return_aligned_status(self):
        """Test aligned documents return ALIGNED status (AC: #3)."""
        prd_content = """
        # PRD
        ## FR1: Auth
        ## FR2: Dashboard
        """
        arch_content = """
        # Architecture

        ## ADR-001: Framework
        Use FastAPI.

        Implements FR1 and FR2.
        """
        stories_content = """
        # Stories

        ## Story 1
        Addresses FR1, FR2.
        Follows ADR-001.
        """

        result = validate_alignment(prd_content, arch_content, stories_content)

        assert result.alignment_status == AlignmentStatus.ALIGNED
        assert result.issues == []

    def test_aligned_documents_include_documents_checked(self):
        """Test aligned result includes documents_checked list."""
        prd_content = "# PRD\n## FR1: Test"
        arch_content = "# Arch\nImplements FR1."
        stories_content = "# Stories\nFR1 story."

        result = validate_alignment(prd_content, arch_content, stories_content)

        assert len(result.documents_checked) == 3


class TestValidateAlignmentSorting:
    """Tests for issue sorting by severity (AC: #4)."""

    def test_issues_sorted_by_severity(self):
        """Test issues are sorted HIGH > MEDIUM > LOW (AC: #4)."""
        prd_content = """
        # PRD
        ## FR1: Feature
        ## FR2: Another Feature
        """
        arch_content = """
        # Architecture

        ## ADR-001: Decision
        Details.

        FR1 implemented. (FR2 orphaned)
        """
        stories_content = """
        # Stories
        Story for FR1.
        (ADR-001 unaddressed)
        """

        result = validate_alignment(prd_content, arch_content, stories_content)

        if len(result.issues) > 1:
            # Verify HIGH comes before MEDIUM/LOW
            severity_order = [i.severity for i in result.issues]
            for i in range(len(severity_order) - 1):
                current = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}[severity_order[i].value]
                next_val = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}[severity_order[i + 1].value]
                assert current >= next_val

    def test_multiple_issues_all_sorted(self):
        """Test multiple issues of different severities are properly sorted."""
        # Create a result with known mixed severities
        issues = [
            AlignmentIssue(issue_type="low_priority", items=["X"], severity=Severity.LOW),
            AlignmentIssue(issue_type="orphaned_requirements", items=["FR1"], severity=Severity.HIGH),
            AlignmentIssue(issue_type="medium_priority", items=["Y"], severity=Severity.MEDIUM),
        ]
        result = AlignmentResult(
            alignment_status=AlignmentStatus.MISALIGNED,
            issues=issues,
        )

        # Sort manually for this test
        sorted_issues = result.get_sorted_issues()
        assert sorted_issues[0].severity == Severity.HIGH
        assert sorted_issues[1].severity == Severity.MEDIUM
        assert sorted_issues[2].severity == Severity.LOW


class TestValidateAlignmentEdgeCases:
    """Tests for edge cases in validate_alignment."""

    def test_empty_prd(self):
        """Test handling empty PRD content."""
        result = validate_alignment("", "# Arch\nADR-001", "# Stories")
        # Empty PRD means no FRs to be orphaned
        assert result is not None

    def test_empty_architecture(self):
        """Test handling empty Architecture content."""
        result = validate_alignment("# PRD\nFR1", "", "# Stories")
        assert result is not None

    def test_empty_stories(self):
        """Test handling empty Stories content."""
        result = validate_alignment("# PRD\nFR1", "# Arch\nFR1", "")
        assert result is not None

    def test_all_empty_documents(self):
        """Test handling all empty documents."""
        result = validate_alignment("", "", "")
        assert result.alignment_status == AlignmentStatus.ALIGNED
        assert result.issues == []

    def test_whitespace_only_documents(self):
        """Test handling whitespace-only documents."""
        result = validate_alignment("   \n\t", "  \n  ", "\t\t")
        assert result.alignment_status == AlignmentStatus.ALIGNED

    def test_no_frs_no_adrs(self):
        """Test documents with content but no FRs or ADRs."""
        prd = "# PRD\nJust description."
        arch = "# Architecture\nGeneral design."
        stories = "# Stories\nUser stories."

        result = validate_alignment(prd, arch, stories)
        assert result.alignment_status == AlignmentStatus.ALIGNED


class TestValidateAlignmentIntegration:
    """Integration tests with realistic document content."""

    def test_realistic_misaligned_scenario(self):
        """Test with realistic multi-issue misalignment."""
        prd_content = """
        # Product Requirements Document

        ## Functional Requirements

        ### FR1: User Registration
        Users can create accounts.

        ### FR2: Login
        Users can authenticate.

        ### FR3: Password Reset
        Users can reset passwords.

        ### FR4: Profile Management
        Users can update profiles.
        """

        arch_content = """
        # Architecture Document

        ## ADR-001: Authentication Provider
        Use Auth0 for authentication services.

        ## ADR-002: Database
        PostgreSQL for user data.

        ## Implementation Notes
        - FR1 handled by Auth0 registration
        - FR2 handled by Auth0 login

        Note: Password reset and profile features are Phase 2 scope.
        """

        stories_content = """
        # User Stories

        ## Epic 1: Authentication

        ### Story 1.1: Registration
        Implements FR1 via ADR-001.

        ### Story 1.2: Login
        Implements FR2 via ADR-001.

        Note: Database setup story pending.
        """

        result = validate_alignment(prd_content, arch_content, stories_content)

        assert result.alignment_status == AlignmentStatus.MISALIGNED
        # Should have orphaned FR3, FR4 (not in architecture)
        orphaned = [i for i in result.issues if i.issue_type == "orphaned_requirements"]
        assert len(orphaned) == 1
        assert "FR3" in orphaned[0].items or "FR4" in orphaned[0].items

    def test_realistic_aligned_scenario(self):
        """Test with realistic fully aligned documents."""
        prd_content = """
        # PRD

        ## FR1: Core Feature
        Main functionality.

        ## FR2: Secondary Feature
        Supporting functionality.
        """

        arch_content = """
        # Architecture

        ## ADR-001: Main Approach
        Technical decision.

        ## Components
        - FR1 implementation details
        - FR2 implementation details
        """

        stories_content = """
        # Stories

        ## Story 1: FR1 Implementation
        Implements FR1 per ADR-001.

        ## Story 2: FR2 Implementation
        Implements FR2 per ADR-001.
        """

        result = validate_alignment(prd_content, arch_content, stories_content)

        assert result.alignment_status == AlignmentStatus.ALIGNED
        assert result.issues == []
