# Story 1.4: Custom Validation Pattern Recognition

Status: complete

## Story

As a **workflow author**,
I want **custom validation patterns defined in workflow configuration to be recognized**,
So that **specialized workflows can define their own success criteria beyond the built-in types**.

## Acceptance Criteria

1. **Given** a workflow with custom validation pattern in frontmatter:
   ```yaml
   validation:
     type: custom
     success_pattern: "Quality Gate: PASSED"
     failure_pattern: "Quality Gate: FAILED"
   ```
   **When** the Validation Type Detector analyzes the workflow
   **Then** it returns `validation_type: "custom"` with the registered patterns

2. **Given** a registered custom pattern "Quality Gate: PASSED"
   **When** workflow output contains "Quality Gate: PASSED"
   **Then** the pattern is detected and validation returns success

3. **Given** a custom pattern that conflicts with built-in patterns
   **When** the Validation Type Detector analyzes the workflow
   **Then** custom patterns take precedence over built-in detection

4. **Given** an invalid custom pattern definition (missing required fields)
   **When** the Validation Type Detector attempts to register the pattern
   **Then** it returns `error: "invalid_pattern"` with specific validation failures

## Tasks / Subtasks

- [x] Task 1: Extend ValidationTypeResult for custom patterns (AC: #1)
  - [x] 1.1 Add custom_patterns field to ValidationTypeResult
  - [x] 1.2 Add success_pattern and failure_pattern fields
  - [x] 1.3 Update factory method for custom type
  - [x] 1.4 Write tests for custom pattern result creation

- [x] Task 2: Implement custom pattern parsing from frontmatter (AC: #1)
  - [x] 2.1 Parse validation.type field from frontmatter
  - [x] 2.2 Extract success_pattern and failure_pattern
  - [x] 2.3 Handle optional pattern fields (warning_pattern, etc.)
  - [x] 2.4 Write tests for frontmatter parsing

- [x] Task 3: Implement custom pattern validation (AC: #4)
  - [x] 3.1 Validate required fields are present (type, success_pattern)
  - [x] 3.2 Validate pattern syntax is valid regex
  - [x] 3.3 Return specific error messages for each validation failure
  - [x] 3.4 Write tests for pattern validation

- [x] Task 4: Implement custom pattern matching (AC: #2)
  - [x] 4.1 Create function to match custom patterns against content
  - [x] 4.2 Return success when success_pattern matches
  - [x] 4.3 Return failure when failure_pattern matches
  - [x] 4.4 Handle case where neither pattern matches
  - [x] 4.5 Write tests for pattern matching

- [x] Task 5: Implement precedence logic (AC: #3)
  - [x] 5.1 Check for custom patterns before built-in detection
  - [x] 5.2 Custom patterns take precedence when defined
  - [x] 5.3 Fall back to built-in detection when no custom patterns
  - [x] 5.4 Write tests for precedence behavior

- [x] Task 6: Update main detect_validation_type() function (AC: #1-4)
  - [x] 6.1 Integrate custom pattern detection into main flow
  - [x] 6.2 Update confidence scoring for custom patterns
  - [x] 6.3 Ensure backward compatibility with existing behavior
  - [x] 6.4 Write integration tests

## Dev Notes

### Architecture Context

**Component:** Validation Type Detector - Custom Pattern Extension (from Design Spec S10)
- **Tier:** 1 (No dependencies)
- **Purpose:** Extends existing Validation Type Detector to support custom patterns
- **Integration Point:** Works with existing detect_validation_type() from Story 1.1
- **FR40 Coverage:** Validation Type Detector can recognize custom workflow validation patterns

**Custom Pattern Structure (from FR40):**
```yaml
validation:
  type: custom
  success_pattern: "regex or literal string"
  failure_pattern: "regex or literal string"
  warning_pattern: "optional"  # For intermediate states
  case_sensitive: false  # Optional, default false
```

### Technical Requirements

**Language:** Python 3.11+
**Testing Framework:** pytest with TDD (Red-Green-Refactor)
**File Location:** `pcmrp_tools/bmad_automation/validation_type_detector.py` (extend existing)
**Test Location:** `tests/bmad_automation/test_validation_type_detector.py` (extend existing)

### Code Patterns to Follow

Extend existing ValidationTypeResult:
```python
@dataclass
class CustomPattern:
    success_pattern: str
    failure_pattern: str
    warning_pattern: Optional[str] = None
    case_sensitive: bool = False

@dataclass
class ValidationTypeResult:
    validation_type: ValidationType
    patterns: list[str]
    confidence: float
    details: dict
    custom_patterns: Optional[CustomPattern] = None  # NEW FIELD
```

### Testing Standards

- **100% test coverage required**
- **TDD cycle:** Write failing test FIRST, then implementation
- **Extend existing test file** - don't create new test file
- **Test function naming:** `test_<function>_custom_<scenario>_<expected_result>`
- **Use pytest fixtures for workflow files with custom patterns**

### Sample Test Workflows

Add to `tests/fixtures/workflows/`:
- `custom_quality_gate.yaml` - Valid custom pattern workflow
- `custom_invalid_missing_success.yaml` - Missing success_pattern
- `custom_invalid_regex.yaml` - Invalid regex pattern
- `custom_with_builtin_conflict.yaml` - Custom + PASS/FAIL in content

### Edge Cases to Handle

1. Empty custom pattern definition
2. Custom pattern with only success_pattern (failure optional?)
3. Invalid regex syntax in patterns
4. Unicode characters in patterns
5. Very long patterns (performance)
6. Patterns that match themselves (recursive)
7. Conflict: custom says success, built-in says failure

### References

- [Source: plans/2026-01-08-bmad-automation-design.md#Component Overview] - Validation Type Detector
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.4] - Acceptance criteria
- [Source: _bmad-output/planning-artifacts/epics.md#FR Coverage Map] - FR40
- [Source: pcmrp_tools/bmad_automation/validation_type_detector.py] - Existing implementation to extend

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101) via subagent-driven-development

### Debug Log References

- 46 new tests added to validation_type_detector.py (200 total)
- Module coverage: 95%

### Completion Notes List

- **Task 1 Complete (2026-01-12):** Extended ValidationTypeResult with CustomPattern dataclass containing success_pattern, failure_pattern, warning_pattern (optional), and case_sensitive fields. Added custom_patterns field to ValidationTypeResult. Updated custom() factory method.
- **Task 2 Complete (2026-01-12):** Enhanced _check_custom_validation_frontmatter() to parse validation.type, success_pattern, failure_pattern, warning_pattern, and case_sensitive from YAML frontmatter. Returns CustomPattern instance when type="custom".
- **Task 3 Complete (2026-01-12):** Implemented validate_custom_pattern() function. Validates required fields present (type, success_pattern), validates regex syntax, returns specific error messages (missing_type, missing_success_pattern, invalid_regex) for each failure type.
- **Task 4 Complete (2026-01-12):** Implemented match_custom_pattern() function. Matches success/failure/warning patterns against content with case sensitivity support. Returns match result with pattern type and matched text.
- **Task 5 Complete (2026-01-12):** Updated detect_validation_type() with custom pattern precedence. Custom patterns checked first before built-in detection (verdict > error > checklist). Falls back to built-in when no custom patterns defined.
- **Task 6 Complete (2026-01-12):** Integrated custom pattern detection into main flow. Custom patterns get confidence 1.0 when valid. Backward compatibility maintained - existing tests still pass. Added integration tests with workflow files containing custom validation frontmatter.

### File List

- `pcmrp_tools/bmad_automation/validation_type_detector.py` (extended)
- `tests/bmad_automation/test_validation_type_detector.py` (extended)
