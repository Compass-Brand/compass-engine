"""Cross-Reference Validator for BMAD Automation.

This module provides the AlignmentResult dataclass and alignment validation
functionality for detecting issues between BMAD planning documents.

The Cross-Reference Validator compares PRD, Architecture, and Stories documents
to identify:
- Orphaned requirements (FRs in PRD not referenced in Architecture)
- Unaddressed decisions (ADRs in Architecture not addressed in Stories)

Component: Cross-Reference Validator (Tier 1 - No dependencies)
Story: 1.3 - Cross-Reference Document Alignment
Epic: 1 - Foundation Validation
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# =============================================================================
# Enums (Task 1.3)
# =============================================================================


class Severity(Enum):
    """Enumeration of issue severity levels.

    Severity ordering: HIGH > MEDIUM > LOW
    Used for sorting issues by importance.
    """

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# Priority mapping for severity-based sorting (higher value = higher priority)
SEVERITY_PRIORITY: dict[Severity, int] = {
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
}


class AlignmentStatus(Enum):
    """Enumeration of document alignment statuses.

    ALIGNED: All documents are properly cross-referenced
    MISALIGNED: One or more alignment issues detected
    """

    ALIGNED = "ALIGNED"
    MISALIGNED = "MISALIGNED"


# =============================================================================
# FR Pattern Definitions (Task 2.1)
# =============================================================================

# Regex patterns for functional requirement extraction
# Supports: FR1, FR-1, FR01, FR-01, fr1, etc.
FR_PATTERNS: list[re.Pattern[str]] = [
    # FR followed by optional hyphen and digits (e.g., FR1, FR-1, FR01, FR-01)
    re.compile(r"\bFR[-]?\d+\b", re.IGNORECASE),
]


# =============================================================================
# ADR Pattern Definitions (Task 3.1)
# =============================================================================

# Regex patterns for architectural decision record extraction
# Supports: ADR-001, ADR001, Decision-1, decision-1, etc.
ADR_PATTERNS: list[re.Pattern[str]] = [
    # ADR followed by optional hyphen and digits (e.g., ADR-001, ADR001)
    re.compile(r"\bADR[-]?\d+\b", re.IGNORECASE),
    # Decision followed by hyphen and digits (e.g., Decision-1)
    re.compile(r"\bDecision[-]?\d+\b", re.IGNORECASE),
]


# =============================================================================
# Dataclasses (Task 1.1, 1.2)
# =============================================================================


@dataclass
class AlignmentIssue:
    """An individual alignment issue detected during cross-reference validation.

    Attributes:
        issue_type: Category of issue (e.g., "orphaned_requirements", "unaddressed_decisions")
        items: List of identifiers affected (e.g., ["FR3", "FR5"] or ["ADR-001"])
        severity: Issue severity level (HIGH, MEDIUM, LOW)
        affected_components: Optional list of components affected by this issue
        message: Human-readable description of the issue
    """

    issue_type: str
    items: list[str]
    severity: Severity
    affected_components: list[str] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert AlignmentIssue to a dictionary.

        Returns:
            Dictionary representation with severity as string value.
        """
        return {
            "issue_type": self.issue_type,
            "items": self.items,
            "severity": self.severity.value,
            "affected_components": self.affected_components,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlignmentIssue:
        """Create AlignmentIssue from a dictionary.

        Args:
            data: Dictionary with issue_type, items, severity, etc.

        Returns:
            AlignmentIssue instance.
        """
        severity_str = data["severity"]
        severity_mapping = {s.value: s for s in Severity}
        severity = severity_mapping[severity_str]

        return cls(
            issue_type=data["issue_type"],
            items=data["items"],
            severity=severity,
            affected_components=data.get("affected_components", []),
            message=data.get("message", ""),
        )


@dataclass
class AlignmentResult:
    """Result of cross-reference document alignment validation.

    Attributes:
        alignment_status: Overall status (ALIGNED or MISALIGNED)
        issues: List of alignment issues found (empty if ALIGNED)
        documents_checked: Names of documents that were validated
    """

    alignment_status: AlignmentStatus
    issues: list[AlignmentIssue] = field(default_factory=list)
    documents_checked: list[str] = field(default_factory=list)

    # Factory methods (Task 1.4)

    @classmethod
    def aligned(cls, documents_checked: list[str]) -> AlignmentResult:
        """Create an aligned result (no issues found).

        Args:
            documents_checked: List of document names that were checked.

        Returns:
            AlignmentResult with ALIGNED status and empty issues.
        """
        return cls(
            alignment_status=AlignmentStatus.ALIGNED,
            issues=[],
            documents_checked=documents_checked,
        )

    @classmethod
    def misaligned(
        cls,
        issues: list[AlignmentIssue],
        documents_checked: list[str],
    ) -> AlignmentResult:
        """Create a misaligned result with issues.

        Args:
            issues: List of alignment issues found.
            documents_checked: List of document names that were checked.

        Returns:
            AlignmentResult with MISALIGNED status and issues.
        """
        return cls(
            alignment_status=AlignmentStatus.MISALIGNED,
            issues=issues,
            documents_checked=documents_checked,
        )

    def get_sorted_issues(self) -> list[AlignmentIssue]:
        """Get issues sorted by severity (HIGH > MEDIUM > LOW).

        Returns:
            List of issues sorted by severity, highest first.
        """
        return sorted(
            self.issues,
            key=lambda issue: SEVERITY_PRIORITY[issue.severity],
            reverse=True,
        )

    # Serialization methods (Task 1.5)

    def to_dict(self) -> dict[str, Any]:
        """Convert AlignmentResult to a dictionary.

        Returns:
            Dictionary representation with alignment_status as string value.
        """
        return {
            "alignment_status": self.alignment_status.value,
            "issues": [issue.to_dict() for issue in self.issues],
            "documents_checked": self.documents_checked,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlignmentResult:
        """Create AlignmentResult from a dictionary.

        Args:
            data: Dictionary with alignment_status, issues, documents_checked.

        Returns:
            AlignmentResult instance.
        """
        status_str = data["alignment_status"]
        status_mapping = {s.value: s for s in AlignmentStatus}
        alignment_status = status_mapping[status_str]

        issues = [AlignmentIssue.from_dict(issue_data) for issue_data in data.get("issues", [])]

        return cls(
            alignment_status=alignment_status,
            issues=issues,
            documents_checked=data.get("documents_checked", []),
        )


# =============================================================================
# Helper Functions
# =============================================================================


def _strip_code_blocks(content: str) -> str:
    """Remove code blocks from content to avoid false positive pattern matches.

    Patterns inside code blocks (```...```) should not be considered as
    valid references since they're likely examples or documentation.

    Args:
        content: The content to process.

    Returns:
        Content with code blocks removed.
    """
    code_block_pattern = re.compile(r"```[\s\S]*?```", re.MULTILINE)
    return code_block_pattern.sub("", content)


def _normalize_fr(fr: str) -> str:
    """Normalize an FR reference to a canonical form.

    Converts various FR formats to uppercase without hyphen.

    Args:
        fr: The FR reference (e.g., "fr-1", "FR1", "FR-01")

    Returns:
        Normalized FR reference (e.g., "FR1", "FR01")
    """
    # Uppercase
    normalized = fr.upper()
    # Remove hyphen if present
    normalized = normalized.replace("-", "")
    return normalized


def _normalize_adr(adr: str) -> str:
    """Normalize an ADR reference to a canonical form.

    Converts various ADR formats to uppercase with hyphen.

    Args:
        adr: The ADR reference (e.g., "adr001", "ADR-001", "decision-1")

    Returns:
        Normalized ADR reference (e.g., "ADR-001", "Decision-1")
    """
    normalized = adr.upper()
    # Insert hyphen if not present (for ADR format)
    if normalized.startswith("ADR") and "-" not in normalized:
        # Insert hyphen after ADR
        normalized = "ADR-" + normalized[3:]
    elif normalized.startswith("DECISION") and "-" not in normalized:
        # Insert hyphen after DECISION
        normalized = "DECISION-" + normalized[8:]
    return normalized


# =============================================================================
# FR Extraction (Task 2)
# =============================================================================


def extract_frs_from_content(content: str) -> set[str]:
    """Extract functional requirement references from document content.

    Searches for FR patterns like FR1, FR-1, FR01, FR-01 (case insensitive).
    Ignores patterns inside code blocks.

    Args:
        content: Document content to search.

    Returns:
        Set of unique FR references found (uppercase, no hyphen).
    """
    if not content or not content.strip():
        return set()

    # Strip code blocks to avoid false positives
    clean_content = _strip_code_blocks(content)

    frs: set[str] = set()
    for pattern in FR_PATTERNS:
        matches = pattern.findall(clean_content)
        for match in matches:
            # Normalize and add to set
            normalized = _normalize_fr(match)
            frs.add(normalized)

    return frs


# =============================================================================
# ADR Extraction (Task 3)
# =============================================================================


def extract_adrs_from_content(content: str) -> set[str]:
    """Extract architectural decision record references from document content.

    Searches for ADR patterns like ADR-001, ADR001, Decision-1 (case insensitive).
    Ignores patterns inside code blocks.

    Args:
        content: Document content to search.

    Returns:
        Set of unique ADR references found (normalized form).
    """
    if not content or not content.strip():
        return set()

    # Strip code blocks to avoid false positives
    clean_content = _strip_code_blocks(content)

    adrs: set[str] = set()
    for pattern in ADR_PATTERNS:
        matches = pattern.findall(clean_content)
        for match in matches:
            # Normalize and add to set
            normalized = _normalize_adr(match)
            adrs.add(normalized)

    return adrs


# =============================================================================
# Orphaned Requirements Detection (Task 4)
# =============================================================================


def detect_orphaned_requirements(
    prd_frs: set[str],
    arch_frs: set[str],
) -> list[AlignmentIssue]:
    """Detect functional requirements in PRD not referenced in Architecture.

    Compares FR references from PRD against those in Architecture to find
    orphaned requirements that may be missing from the architecture.

    Args:
        prd_frs: Set of FR references found in PRD.
        arch_frs: Set of FR references found in Architecture.

    Returns:
        List of AlignmentIssue for orphaned requirements (empty if none).
    """
    # Find FRs in PRD but not in Architecture
    orphaned = prd_frs - arch_frs

    if not orphaned:
        return []

    # Sort for consistent output
    sorted_orphaned = sorted(orphaned)

    return [
        AlignmentIssue(
            issue_type="orphaned_requirements",
            items=sorted_orphaned,
            severity=Severity.HIGH,
            affected_components=[],
            message=f"Requirements {', '.join(sorted_orphaned)} defined in PRD but not referenced in Architecture",
        )
    ]


# =============================================================================
# Unaddressed Decisions Detection (Task 5)
# =============================================================================


def detect_unaddressed_decisions(
    arch_adrs: set[str],
    story_adrs: set[str],
) -> list[AlignmentIssue]:
    """Detect architectural decisions not addressed in Stories.

    Compares ADR references from Architecture against those in Stories to find
    decisions that may not be implemented.

    Args:
        arch_adrs: Set of ADR references found in Architecture.
        story_adrs: Set of ADR references found in Stories.

    Returns:
        List of AlignmentIssue for unaddressed decisions (empty if none).
    """
    # Find ADRs in Architecture but not in Stories
    unaddressed = arch_adrs - story_adrs

    if not unaddressed:
        return []

    # Sort for consistent output
    sorted_unaddressed = sorted(unaddressed)

    return [
        AlignmentIssue(
            issue_type="unaddressed_decisions",
            items=sorted_unaddressed,
            severity=Severity.MEDIUM,  # Decisions are MEDIUM by default
            affected_components=[],
            message=f"Decisions {', '.join(sorted_unaddressed)} defined in Architecture but not addressed in Stories",
        )
    ]


# =============================================================================
# Main Validation Function (Task 6)
# =============================================================================


def validate_alignment(
    prd_content: str,
    arch_content: str,
    stories_content: str,
) -> AlignmentResult:
    """Validate cross-reference alignment between BMAD planning documents.

    Performs comprehensive validation including:
    1. Extracting FRs from all documents
    2. Extracting ADRs from Architecture and Stories
    3. Detecting orphaned requirements (PRD FRs not in Architecture)
    4. Detecting unaddressed decisions (Architecture ADRs not in Stories)
    5. Aggregating and sorting issues by severity

    Args:
        prd_content: Content of the PRD document.
        arch_content: Content of the Architecture document.
        stories_content: Content of the Stories document.

    Returns:
        AlignmentResult with status and sorted issues.
    """
    documents_checked = ["PRD", "Architecture", "Stories"]

    # Extract FRs from documents (Task 6.1)
    prd_frs = extract_frs_from_content(prd_content)
    arch_frs = extract_frs_from_content(arch_content)
    # Note: We could also check stories_frs if needed

    # Extract ADRs from documents
    arch_adrs = extract_adrs_from_content(arch_content)
    story_adrs = extract_adrs_from_content(stories_content)

    # Run all alignment checks (Task 6.2)
    all_issues: list[AlignmentIssue] = []

    # Check for orphaned requirements
    orphaned_issues = detect_orphaned_requirements(prd_frs, arch_frs)
    all_issues.extend(orphaned_issues)

    # Check for unaddressed decisions
    unaddressed_issues = detect_unaddressed_decisions(arch_adrs, story_adrs)
    all_issues.extend(unaddressed_issues)

    # Determine alignment status (Task 6.4)
    if not all_issues:
        return AlignmentResult.aligned(documents_checked)

    # Sort issues by severity (Task 6.3)
    sorted_issues = sorted(
        all_issues,
        key=lambda issue: SEVERITY_PRIORITY[issue.severity],
        reverse=True,
    )

    return AlignmentResult.misaligned(
        issues=sorted_issues,
        documents_checked=documents_checked,
    )
