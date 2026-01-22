# Story 1.3: Cross-Reference Document Alignment

Status: complete

## Story

As a **workflow user**,
I want **automatic detection of alignment issues between planning documents**,
So that **I catch missing requirements, orphaned decisions, and gaps before implementation starts**.

## Acceptance Criteria

1. **Given** a PRD with FR1, FR2, FR3 defined
   **When** the Cross-Reference Validator compares PRD to Architecture
   **And** Architecture references FR1 and FR2 but not FR3
   **Then** it reports `orphaned_requirements: ["FR3"]` with severity "HIGH"

2. **Given** an Architecture document with decision ADR-001
   **When** the Cross-Reference Validator compares Architecture to Stories
   **And** no story references ADR-001
   **Then** it reports `unaddressed_decisions: ["ADR-001"]` with affected components

3. **Given** aligned PRD, Architecture, and Stories documents
   **When** the Cross-Reference Validator performs full comparison
   **Then** it returns `alignment_status: "ALIGNED"` with `issues: []`

4. **Given** multiple alignment issues detected
   **When** the Cross-Reference Validator completes
   **Then** it returns issues sorted by severity (HIGH > MEDIUM > LOW)

## Tasks / Subtasks

- [x] Task 1: Create AlignmentResult dataclass (AC: #1-4)
  - [x] 1.1 Define AlignmentIssue dataclass with type, items, severity, affected_components
  - [x] 1.2 Define AlignmentResult dataclass with status, issues, documents_checked
  - [x] 1.3 Add Severity enum (HIGH, MEDIUM, LOW)
  - [x] 1.4 Add factory methods for aligned/misaligned results
  - [x] 1.5 Write tests for dataclass creation and serialization

- [x] Task 2: Implement FR extraction from documents (AC: #1)
  - [x] 2.1 Create regex patterns to extract FR references (FR1, FR-1, FR01 variants)
  - [x] 2.2 Extract FRs from PRD documents
  - [x] 2.3 Extract FR references from Architecture documents
  - [x] 2.4 Extract FR references from Story documents
  - [x] 2.5 Write tests for FR extraction

- [x] Task 3: Implement ADR/decision extraction (AC: #2)
  - [x] 3.1 Create patterns to extract ADR references (ADR-001, Decision-1 variants)
  - [x] 3.2 Extract decisions from Architecture documents
  - [x] 3.3 Extract decision references from Stories
  - [x] 3.4 Write tests for decision extraction

- [x] Task 4: Implement orphaned requirements detection (AC: #1)
  - [x] 4.1 Compare PRD FRs to Architecture FR references
  - [x] 4.2 Identify FRs in PRD not referenced in Architecture
  - [x] 4.3 Assign HIGH severity to orphaned requirements
  - [x] 4.4 Write tests for orphaned requirement detection

- [x] Task 5: Implement unaddressed decisions detection (AC: #2)
  - [x] 5.1 Compare Architecture decisions to Story references
  - [x] 5.2 Identify decisions not addressed in any story
  - [x] 5.3 Determine affected components from decision context
  - [x] 5.4 Write tests for unaddressed decision detection

- [x] Task 6: Implement main validate_alignment() function (AC: #1-4)
  - [x] 6.1 Orchestrate document loading and parsing
  - [x] 6.2 Run all alignment checks
  - [x] 6.3 Aggregate and sort issues by severity
  - [x] 6.4 Return ALIGNED status only when no issues found
  - [x] 6.5 Write integration tests with sample documents

## Dev Notes

### Architecture Context

**Component:** Cross-Reference Validator (from Design Spec S10)
- **Tier:** 1 (No dependencies - can start immediately)
- **Purpose:** Detects alignment issues between PRD, Architecture, and Stories
- **Stateless:** Reads documents, compares, returns issues
- **Integration Point:** Called during pre-flight or on-demand validation

**Issue Types (from Architecture Design):**
| Issue Type | Severity | Description |
|------------|----------|-------------|
| orphaned_requirements | HIGH | FRs in PRD not referenced in Architecture |
| unaddressed_decisions | MEDIUM | Decisions in Architecture not in Stories |
| missing_coverage | MEDIUM | Stories without FR mapping |
| circular_references | LOW | Documents referencing each other incorrectly |

### Technical Requirements

**Language:** Python 3.11+
**Testing Framework:** pytest with TDD (Red-Green-Refactor)
**File Location:** `pcmrp_tools/bmad_automation/cross_reference_validator.py`
**Test Location:** `tests/bmad_automation/test_cross_reference_validator.py`

### Code Patterns to Follow

```python
from dataclasses import dataclass, field
from typing import Literal
from enum import Enum

class Severity(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class AlignmentStatus(Enum):
    ALIGNED = "ALIGNED"
    MISALIGNED = "MISALIGNED"

@dataclass
class AlignmentIssue:
    issue_type: str  # orphaned_requirements, unaddressed_decisions, etc.
    items: list[str]  # ["FR3", "FR5"] or ["ADR-001"]
    severity: Severity
    affected_components: list[str] = field(default_factory=list)
    message: str = ""

@dataclass
class AlignmentResult:
    alignment_status: AlignmentStatus
    issues: list[AlignmentIssue] = field(default_factory=list)
    documents_checked: list[str] = field(default_factory=list)
```

### Testing Standards

- **100% test coverage required**
- **TDD cycle:** Write failing test FIRST, then implementation
- **Test file naming:** `test_<module_name>.py`
- **Test function naming:** `test_<function>_<scenario>_<expected_result>`
- **Use pytest fixtures with sample PRD, Architecture, and Story documents**

### Sample Test Documents

Create test fixtures in `tests/fixtures/documents/`:
- `sample_prd.md` - Contains FR1, FR2, FR3
- `sample_architecture.md` - References FR1, FR2, defines ADR-001
- `sample_stories.md` - References FR1, FR2 (no FR3, no ADR-001)
- `aligned_set/` - Fully aligned document set

### Edge Cases to Handle

1. Empty documents
2. Documents with no FR references
3. Malformed FR references (FR-A, FRX, etc.)
4. Multiple documents of same type
5. Case sensitivity (FR1 vs fr1)
6. FRs in code blocks (should be ignored)
7. FRs in comments vs actual requirements

### References

- [Source: docs/plans/2026-01-08-bmad-automation-design.md#Component Overview] - Cross-Reference Validator definition
- [Source: docs/plans/2026-01-08-bmad-automation-design.md#Implementation Dependency Graph] - Tier 1 component
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.3] - Acceptance criteria
- [Source: _bmad-output/planning-artifacts/epics.md#FR Coverage Map] - FR15

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101) via subagent-driven-development

### Debug Log References

- 77 tests written and passing
- Module coverage: 100%

### Completion Notes List

- **Task 1 Complete (2026-01-12):** Created Severity enum (HIGH, MEDIUM, LOW) with comparison ordering, AlignmentStatus enum (ALIGNED, MISALIGNED), AlignmentIssue dataclass with type/items/severity/affected_components/message fields, and AlignmentResult dataclass with factory methods (aligned, misaligned) and serialization (to_dict, from_dict).
- **Task 2 Complete (2026-01-12):** Implemented FR_PATTERNS constant with compiled regex patterns for FR variants (FR1, FR-1, FR01, fr1, etc.). Created extract_frs_from_content() function with code block stripping and deduplication. Handles PRD, Architecture, and Story documents.
- **Task 3 Complete (2026-01-12):** Implemented ADR_PATTERNS constant with compiled regex for ADR and Decision variants (ADR-001, ADR001, Decision-1, decision1). Created extract_adrs_from_content() with code block filtering. Extracts from Architecture and Stories.
- **Task 4 Complete (2026-01-12):** Implemented detect_orphaned_requirements() comparing PRD FRs to Architecture references. Returns AlignmentIssue with HIGH severity, orphaned FRs list, and descriptive message. Handles empty documents.
- **Task 5 Complete (2026-01-12):** Implemented detect_unaddressed_decisions() comparing Architecture ADRs to Story references. Returns AlignmentIssue with MEDIUM severity and affected_components. Handles empty inputs.
- **Task 6 Complete (2026-01-12):** Implemented validate_alignment() main function. Runs orphaned and unaddressed checks, aggregates issues, sorts by severity (HIGH > MEDIUM > LOW), returns ALIGNED when no issues. Integration tests with realistic PRD/Architecture/Stories scenarios.

### File List

- `pcmrp_tools/bmad_automation/cross_reference_validator.py` (new)
- `tests/bmad_automation/test_cross_reference_validator.py` (new)
