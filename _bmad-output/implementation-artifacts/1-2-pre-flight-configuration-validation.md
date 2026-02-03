# Story 1.2: Pre-flight Configuration Validation

Status: complete

## Story

As a **workflow user**,
I want **required configuration to be validated before a workflow starts**,
So that **I get immediate feedback on missing settings rather than failing mid-workflow**.

## Acceptance Criteria

1. **Given** a workflow requiring `output_folder` configuration
   **When** the Pre-flight Validation Subagent runs before workflow start
   **And** `output_folder` is not configured
   **Then** it returns `status: "FAILED"` with `missing: ["output_folder"]` and a remediation message

2. **Given** a workflow requiring Forgetful MCP connection
   **When** the Pre-flight Validation Subagent runs before workflow start
   **And** Forgetful MCP is available
   **Then** it returns `status: "PASSED"` for the MCP check

3. **Given** a workflow requiring input documents (PRD, Architecture)
   **When** the Pre-flight Validation Subagent runs before workflow start
   **And** the required input files exist at configured paths
   **Then** it returns `status: "PASSED"` with `validated_files: [paths]`

4. **Given** all pre-flight checks pass
   **When** the Pre-flight Validation Subagent completes
   **Then** it returns `overall_status: "READY"` with 100% checks passed

## Tasks / Subtasks

- [x] Task 1: Create PreflightResult dataclass (AC: #1-4)
  - [x] 1.1 Define dataclass with status, checks, missing, remediation fields
  - [x] 1.2 Add type hints for all fields
  - [x] 1.3 Add factory methods for passed/failed/ready results
  - [x] 1.4 Write tests for dataclass creation and serialization

- [x] Task 2: Implement configuration validation (AC: #1)
  - [x] 2.1 Create function to check required config keys
  - [x] 2.2 Implement output_folder validation
  - [x] 2.3 Implement project_root validation
  - [x] 2.4 Generate remediation messages for missing config
  - [x] 2.5 Write tests for config validation

- [x] Task 3: Implement MCP availability check (AC: #2)
  - [x] 3.1 Create function to check Forgetful MCP connectivity
  - [x] 3.2 Handle timeout scenarios (use 5s timeout)
  - [x] 3.3 Return appropriate status for available/unavailable
  - [x] 3.4 Write tests for MCP check (with mocking)

- [x] Task 4: Implement input file validation (AC: #3)
  - [x] 4.1 Create function to validate required input files
  - [x] 4.2 Check PRD file exists at configured path
  - [x] 4.3 Check Architecture file exists at configured path
  - [x] 4.4 Return validated_files list on success
  - [x] 4.5 Write tests for file validation

- [x] Task 5: Implement main validate() function (AC: #1-4)
  - [x] 5.1 Orchestrate all validation checks
  - [x] 5.2 Aggregate results into overall status
  - [x] 5.3 Calculate checks_passed percentage
  - [x] 5.4 Return READY only when all checks pass
  - [x] 5.5 Write integration tests

- [x] Task 6: Add workflow configuration parsing
  - [x] 6.1 Parse workflow YAML to extract required config keys
  - [x] 6.2 Parse workflow YAML to extract required input files
  - [x] 6.3 Handle both YAML and MD workflow formats
  - [x] 6.4 Write tests for workflow parsing

## Dev Notes

### Architecture Context

**Component:** Pre-flight Validation Subagent (from Design Spec S10)
- **Tier:** 1 (No dependencies - can start immediately)
- **Purpose:** Validates required configuration before workflow execution
- **Stateless:** Reads config, validates, returns result
- **Integration Point:** Called by Workflow Entry Wrapper before workflow starts

**Pre-flight Checks (from Architecture Design):**
| Check Type | What It Validates | Failure Action |
|------------|-------------------|----------------|
| config | Required config keys present | List missing keys + remediation |
| mcp | Forgetful MCP connectivity | Warning (graceful degradation) |
| files | Required input files exist | List missing files + paths |

### Technical Requirements

**Language:** Python 3.11+
**Testing Framework:** pytest with TDD (Red-Green-Refactor)
**File Location:** `pcmrp_tools/bmad_automation/preflight_validator.py`
**Test Location:** `tests/bmad_automation/test_preflight_validator.py`

### Code Patterns to Follow

```python
from dataclasses import dataclass, field
from typing import Literal, Optional
from enum import Enum

class PreflightStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    READY = "READY"
    WARNING = "WARNING"

@dataclass
class PreflightCheck:
    name: str
    status: PreflightStatus
    message: str
    details: dict = field(default_factory=dict)

@dataclass
class PreflightResult:
    overall_status: PreflightStatus
    checks: list[PreflightCheck]
    missing: list[str] = field(default_factory=list)
    remediation: list[str] = field(default_factory=list)
    checks_passed: float = 0.0  # Percentage 0.0 to 100.0
```

### Testing Standards

- **100% test coverage required**
- **TDD cycle:** Write failing test FIRST, then implementation
- **Test file naming:** `test_<module_name>.py`
- **Test function naming:** `test_<function>_<scenario>_<expected_result>`
- **Use pytest fixtures for workflow config samples**
- **Mock MCP calls to avoid external dependencies**

### Edge Cases to Handle

1. Empty configuration file
2. Partial configuration (some keys present, some missing)
3. MCP timeout scenarios
4. MCP connection refused
5. Input files exist but are empty
6. Input files exist but are invalid format
7. Circular dependencies in required files
8. Permission denied on file access

### References

- [Source: plans/2026-01-08-bmad-automation-design.md#Component Overview] - Pre-flight Validation Subagent definition
- [Source: plans/2026-01-08-bmad-automation-design.md#Implementation Dependency Graph] - Tier 1 component
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.2] - Acceptance criteria
- [Source: _bmad-output/planning-artifacts/epics.md#FR Coverage Map] - FR14

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101) via subagent-driven-development

### Debug Log References

- 83 tests written and passing
- Module coverage: 100%

### Completion Notes List

- **Task 1 Complete (2026-01-12):** Created PreflightStatus enum (PASSED, FAILED, READY, WARNING), PreflightCheck dataclass, and PreflightResult dataclass with factory methods (passed, failed, warning, ready_result, failed_result) and serialization (to_dict, from_dict).
- **Task 2 Complete (2026-01-12):** Implemented validate_configuration() function checking required config keys. Returns FAILED with missing keys list and remediation messages. Handles None and empty string values as missing.
- **Task 3 Complete (2026-01-12):** Implemented check_mcp_availability() with 5-second default timeout. Returns PASSED/FAILED/WARNING based on MCP connectivity. Handles timeout, connection errors, and slow responses.
- **Task 4 Complete (2026-01-12):** Implemented validate_input_files() checking PRD and Architecture file existence. Returns validated_files list on success, missing files on failure. Handles empty file lists.
- **Task 5 Complete (2026-01-12):** Implemented validate() main orchestration function. Aggregates all checks, calculates checks_passed percentage, returns READY only when all pass. Supports skipping MCP and file checks.
- **Task 6 Complete (2026-01-12):** Implemented parse_workflow_required_config() and parse_workflow_required_inputs() for YAML/MD workflow parsing. Extracts config variables and input file patterns from frontmatter.

### File List

- `pcmrp_tools/bmad_automation/preflight_validator.py` (new)
- `tests/bmad_automation/test_preflight_validator.py` (new)
