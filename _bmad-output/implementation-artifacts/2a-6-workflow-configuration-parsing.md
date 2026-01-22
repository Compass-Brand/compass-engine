# Story 2a.6: Workflow Configuration Parsing

Status: done

## Story

As a **workflow developer**,
I want **the system to read configuration from both YAML and Markdown frontmatter**,
So that **I can define workflow behavior in my preferred format**.

## Acceptance Criteria

1. **Given** a workflow file `workflow.yaml` with configuration block
   **When** the Automation Controller loads the workflow
   **Then** it parses YAML configuration and applies settings

2. **Given** a workflow file `workflow.md` with YAML frontmatter (between `---` delimiters)
   **When** the Automation Controller loads the workflow
   **Then** it extracts and parses the frontmatter configuration

3. **Given** a workflow with module-specific settings `module: bmm`
   **When** the Automation Controller applies configuration
   **Then** BMM-specific defaults and behaviors are activated

4. **Given** a workflow with module-specific settings `module: bmb`
   **When** the Automation Controller applies configuration
   **Then** BMB-specific thresholds (blocking_errors > 3, etc.) are activated

5. **Given** a configuration file with syntax errors
   **When** the Automation Controller attempts to parse
   **Then** it returns `error: "config_parse_error"` with line number and details

## Tasks / Subtasks

- [x] Task 1: Create WorkflowConfig dataclass (AC: #1-5)
  - [x] 1.1 Define dataclass with module, settings, thresholds, error fields
  - [x] 1.2 Add type hints for all fields
  - [x] 1.3 Add factory methods for bmm/bmb/core configs
  - [x] 1.4 Write tests for dataclass creation and serialization

- [x] Task 2: Implement YAML file parsing (AC: #1)
  - [x] 2.1 Load and parse .yaml workflow files
  - [x] 2.2 Extract configuration sections
  - [x] 2.3 Validate required fields
  - [x] 2.4 Write tests for YAML parsing

- [x] Task 3: Implement Markdown frontmatter parsing (AC: #2)
  - [x] 3.1 Detect frontmatter delimiters (---)
  - [x] 3.2 Extract YAML content between delimiters
  - [x] 3.3 Parse extracted YAML
  - [x] 3.4 Write tests for frontmatter parsing

- [x] Task 4: Implement module-specific defaults (AC: #3, #4)
  - [x] 4.1 Define BMM default configuration
  - [x] 4.2 Define BMB default configuration (blocking_errors > 3 threshold)
  - [x] 4.3 Define Core default configuration
  - [x] 4.4 Merge user config with module defaults
  - [x] 4.5 Write tests for module defaults

- [x] Task 5: Implement error handling (AC: #5)
  - [x] 5.1 Catch YAML syntax errors
  - [x] 5.2 Extract line number from error
  - [x] 5.3 Return structured error with details
  - [x] 5.4 Write tests for error scenarios

- [x] Task 6: Create main parse_workflow_config() function (AC: #1-5)
  - [x] 6.1 Auto-detect file format (.yaml vs .md)
  - [x] 6.2 Route to appropriate parser
  - [x] 6.3 Apply module defaults
  - [x] 6.4 Return complete WorkflowConfig
  - [x] 6.5 Write integration tests

## Dev Notes

### Architecture Context

**Component:** Workflow Entry Wrapper - Configuration Parsing (from Design Spec S10)
- **Tier:** 2 (Depends on Validation Type Detector from Epic 1)
- **Purpose:** Reads and parses workflow configuration from YAML/MD files
- **Stateless:** File reading and parsing only
- **Integration Point:** Provides config to Automation Controller

**Module-Specific Defaults:**
```yaml
# BMM Module Defaults
bmm:
  batch_size: 5  # Level 2 default
  confidence_threshold: 80
  checkpoint_frequency: "per_step"

# BMB Module Defaults
bmb:
  blocking_errors_threshold: 3
  major_issues_threshold: 5
  compliance_score_threshold: 70
  party_mode_auto_trigger: true

# Core Module Defaults
core:
  batch_size: "auto"
  confidence_threshold: 80
  checkpoint_frequency: "minimal"
```

### Technical Requirements

**Language:** Python 3.11+
**Testing Framework:** pytest with TDD (Red-Green-Refactor)
**File Location:** `pcmrp_tools/bmad_automation/workflow_entry_wrapper.py` (extend from 2a.1, 2a.3)
**Test Location:** `tests/bmad_automation/test_workflow_entry_wrapper.py` (extend)

### Code Patterns to Follow

```python
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum
from pathlib import Path

class BMADModule(Enum):
    CORE = "core"
    BMM = "bmm"
    BMB = "bmb"

@dataclass
class ConfigParseError:
    message: str
    line_number: Optional[int] = None
    details: str = ""

@dataclass
class WorkflowConfig:
    module: BMADModule
    settings: dict[str, Any] = field(default_factory=dict)
    thresholds: dict[str, int] = field(default_factory=dict)
    raw_config: dict = field(default_factory=dict)
    error: Optional[ConfigParseError] = None

    @classmethod
    def bmm_defaults(cls) -> "WorkflowConfig":
        ...

    @classmethod
    def bmb_defaults(cls) -> "WorkflowConfig":
        ...

    @classmethod
    def core_defaults(cls) -> "WorkflowConfig":
        ...

    @classmethod
    def from_error(cls, error: ConfigParseError) -> "WorkflowConfig":
        ...
```

### Testing Standards

- **100% test coverage required**
- **TDD cycle:** Write failing test FIRST, then implementation
- **Use pytest tmp_path fixture for temporary files**
- **Create sample workflow files in tests**

### Sample Workflow Files for Testing

**workflow.yaml:**
```yaml
module: bmm
name: dev-story
settings:
  batch_size: 3
  oversight: required
thresholds:
  confidence: 85
```

**workflow.md:**
```markdown
---
module: bmb
name: agent-builder
settings:
  party_mode_auto_trigger: true
thresholds:
  blocking_errors: 3
---

# Agent Builder Workflow

Step 1: ...
```

### Edge Cases to Handle

1. Empty configuration file
2. Missing module field (default to core)
3. Unknown module name
4. Malformed YAML syntax
5. Frontmatter without closing delimiter
6. Multiple frontmatter blocks
7. Binary file passed as config
8. Very large configuration files

### References

- [Source: docs/plans/2026-01-08-bmad-automation-design.md#Configuration & Adaptation]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 2a.6]
- [Source: _bmad-output/planning-artifacts/epics.md#FR Coverage Map] - FR36, FR37, FR41

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Session continued from context compaction
- TDD approach followed: tests written first, then implementation
- All 49 Story 2a.6 tests passing
- All 205 tests in test_workflow_entry_wrapper.py passing

### Completion Notes List

1. **Task 1 (WorkflowConfig dataclass)**: Created ConfigParseError and WorkflowConfig dataclasses with full type hints. Added factory methods: bmm_defaults(), bmb_defaults(), core_defaults(), from_error(). Tests cover creation, serialization, and all factory methods.

2. **Task 2 (YAML parsing)**: Implemented parse_yaml_config() using yaml.safe_load(). Handles empty files, comments-only files, extracts module/settings/thresholds, preserves raw_config. Defaults to core module when not specified.

3. **Task 3 (Frontmatter parsing)**: Implemented extract_frontmatter() to detect and extract YAML between --- delimiters. parse_frontmatter_config() parses the extracted YAML. Handles no frontmatter, empty frontmatter, unclosed frontmatter edge cases.

4. **Task 4 (Module defaults)**: Implemented get_module_defaults() returning appropriate WorkflowConfig for each module. merge_with_defaults() merges parsed config with module defaults, user settings take precedence.

5. **Task 5 (Error handling)**: YAML syntax errors caught with line number extraction from yaml.YAMLError. Unknown modules return structured ConfigParseError. All errors include details field.

6. **Task 6 (Main function)**: parse_workflow_config() auto-detects file format by extension (.yaml, .yml, .md), routes to appropriate parser, applies module defaults, handles nonexistent files.

### File List

- `pcmrp_tools/bmad_automation/workflow_entry_wrapper.py` - Implementation (extended with Story 2a.6)
  - BMADModule enum (existing)
  - ConfigParseError dataclass (new)
  - WorkflowConfig dataclass with factory methods (new)
  - parse_yaml_config() (new)
  - extract_frontmatter() (new)
  - parse_frontmatter_config() (new)
  - get_module_defaults() (new)
  - merge_with_defaults() (new)
  - parse_workflow_config() (new)

- `tests/bmad_automation/test_workflow_entry_wrapper.py` - Tests (extended with Story 2a.6)
  - TestConfigParseError (4 tests)
  - TestWorkflowConfigDataclass (5 tests)
  - TestWorkflowConfigFactoryMethods (4 tests)
  - TestParseYamlConfig (8 tests)
  - TestParseFrontmatterConfig (9 tests)
  - TestGetModuleDefaults (3 tests)
  - TestMergeWithDefaults (4 tests)
  - TestYamlParseErrors (4 tests)
  - TestFrontmatterParseErrors (1 test)
  - TestParseWorkflowConfig (7 tests)
  - Total: 49 new tests for Story 2a.6

- `pcmrp_tools/bmad_automation/__init__.py` - Package exports (updated)
  - Added imports and exports for all Story 2a.6 components
