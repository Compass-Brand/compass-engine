# Story 2a.3: Project Type Detection

Status: done

## Story

As a **workflow user**,
I want **the system to automatically detect if my project is greenfield or brownfield**,
So that **appropriate workflow paths and templates are selected**.

## Acceptance Criteria

1. **Given** a project directory with no `src/`, `lib/`, or `app/` directories
   **And** no `package.json` or `pyproject.toml` files
   **And** fewer than 10 source files
   **When** the Workflow Entry Wrapper analyzes the project
   **Then** it returns `project_type: "greenfield"`

2. **Given** a project directory with `src/` directory containing 50+ files
   **And** a `package.json` file present
   **When** the Workflow Entry Wrapper analyzes the project
   **Then** it returns `project_type: "brownfield"`

3. **Given** a project with `package.json` but no source directories
   **When** the Workflow Entry Wrapper analyzes the project
   **Then** it returns `project_type: "brownfield"` (package file indicates existing project)

4. **Given** project detection completes
   **When** the result is returned
   **Then** it includes `detection_signals: [list of matched criteria]` for transparency

## Tasks / Subtasks

- [x] Task 1: Create ProjectTypeResult dataclass (AC: #1-4)
  - [x] 1.1 Define ProjectType enum (GREENFIELD, BROWNFIELD)
  - [x] 1.2 Define dataclass with project_type, detection_signals, confidence fields
  - [x] 1.3 Add factory methods for greenfield/brownfield results
  - [x] 1.4 Write tests for dataclass creation and serialization

- [x] Task 2: Implement source directory detection (AC: #1, #2)
  - [x] 2.1 Check for src/, lib/, app/ directories
  - [x] 2.2 Count files in source directories
  - [x] 2.3 Record detection signals for each check
  - [x] 2.4 Write tests for directory detection

- [x] Task 3: Implement package file detection (AC: #2, #3)
  - [x] 3.1 Check for package.json existence
  - [x] 3.2 Check for pyproject.toml existence
  - [x] 3.3 Check for other package files (Cargo.toml, go.mod, pom.xml)
  - [x] 3.4 Write tests for package file detection

- [x] Task 4: Implement source file counting (AC: #1)
  - [x] 4.1 Define source file extensions (.py, .js, .ts, .java, etc.)
  - [x] 4.2 Count source files recursively (excluding node_modules, venv, etc.)
  - [x] 4.3 Apply threshold (< 10 files = greenfield signal)
  - [x] 4.4 Write tests for file counting

- [x] Task 5: Implement detection logic (AC: #1-4)
  - [x] 5.1 Combine all detection signals
  - [x] 5.2 Apply greenfield rules: no source dirs AND no package files AND < 10 files
  - [x] 5.3 Default to brownfield otherwise
  - [x] 5.4 Write tests for combined logic

- [x] Task 6: Create main detect_project_type() function (AC: #1-4)
  - [x] 6.1 Orchestrate all detection checks
  - [x] 6.2 Collect and return detection signals
  - [x] 6.3 Calculate confidence based on signal strength
  - [x] 6.4 Write integration tests with temp directories

## Dev Notes

### Architecture Context

**Component:** Workflow Entry Wrapper - Project Type Detection (from Design Spec S10)
- **Tier:** 2 (Depends on Validation Type Detector from Epic 1)
- **Purpose:** Determines if project is greenfield (new) or brownfield (existing)
- **Stateless:** File system inspection only
- **Integration Point:** Informs workflow-init path selection

**Detection Rules (from FR4):**
```
GREENFIELD when ALL of:
- No src/, lib/, or app/ directories
- No package.json or pyproject.toml
- < 10 source files

BROWNFIELD when ANY of:
- Source directories exist
- Package files exist
- >= 10 source files
```

### Technical Requirements

**Language:** Python 3.11+
**Testing Framework:** pytest with TDD (Red-Green-Refactor)
**File Location:** `pcmrp_tools/bmad_automation/workflow_entry_wrapper.py` (extend from 2a.1)
**Test Location:** `tests/bmad_automation/test_workflow_entry_wrapper.py` (extend)

### Code Patterns to Follow

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from pathlib import Path

class ProjectType(Enum):
    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"

@dataclass
class DetectionSignal:
    name: str
    detected: bool
    details: str = ""

@dataclass
class ProjectTypeResult:
    project_type: ProjectType
    detection_signals: list[DetectionSignal] = field(default_factory=list)
    confidence: float = 1.0

    @classmethod
    def greenfield(cls, signals: list[DetectionSignal]) -> "ProjectTypeResult":
        ...

    @classmethod
    def brownfield(cls, signals: list[DetectionSignal]) -> "ProjectTypeResult":
        ...
```

### Testing Standards

- **100% test coverage required**
- **TDD cycle:** Write failing test FIRST, then implementation
- **Use pytest tmp_path fixture for temporary directories**
- **Create realistic project structures in tests**

### Directories to Exclude from File Counting

```python
EXCLUDED_DIRS = {
    "node_modules", "__pycache__", ".git", ".svn",
    "venv", ".venv", "env", ".env",
    "dist", "build", "target", "out",
    ".idea", ".vscode", ".pytest_cache"
}
```

### Source File Extensions

```python
SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".kt", ".scala",
    ".go", ".rs", ".c", ".cpp", ".h",
    ".rb", ".php", ".swift", ".m"
}
```

### Edge Cases to Handle

1. Empty project directory
2. Directory doesn't exist
3. Permission denied on directory access
4. Symlinks in directory structure
5. Very large directory trees (performance)
6. Mixed signals (some greenfield, some brownfield indicators)

### References

- [Source: plans/2026-01-08-bmad-automation-design.md#Workflow Entry Point Handling]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 2a.3]
- [Source: _bmad-output/planning-artifacts/epics.md#FR Coverage Map] - FR4

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Task 1: 14 tests passed (ProjectTypeEnum: 4, DetectionSignalDataclass: 3, ProjectTypeResultDataclass: 3, ProjectTypeResultFactoryMethods: 4)
- Task 2: 12 tests passed (SourceDirectoriesConstant: 4, DetectSourceDirectoriesFunction: 8)
- Task 3: 14 tests passed (PackageFilesConstant: 6, DetectPackageFilesFunction: 8)
- Task 4: 23 tests passed (SourceExtensionsConstant: 6, ExcludedDirsConstant: 5, CountSourceFilesFunction: 12)
- Task 5 & 6: 22 tests passed (DetectProjectTypeFunction: 3, DetectProjectTypeGreenfield: 5, DetectProjectTypeBrownfield: 8, DetectProjectTypeSignals: 3, DetectProjectTypeEdgeCases: 3)
- **Total: 85 tests for story 2a.3**

### Completion Notes List

- **Task 1:** Created ProjectType enum (GREENFIELD, BROWNFIELD), DetectionSignal dataclass, and ProjectTypeResult dataclass with factory methods for greenfield/brownfield results
- **Task 2:** Implemented SOURCE_DIRECTORIES constant and detect_source_directories() function to check for src/, lib/, app/ directories and count files in each
- **Task 3:** Implemented PACKAGE_FILES constant and detect_package_files() function to check for package.json, pyproject.toml, Cargo.toml, go.mod, pom.xml
- **Task 4:** Implemented SOURCE_EXTENSIONS constant, EXCLUDED_DIRS constant, and count_source_files() function with recursive counting and directory exclusions
- **Task 5 & 6:** Implemented detect_project_type() main function that orchestrates all detection checks, applies greenfield/brownfield rules, calculates confidence, and returns transparent detection signals

### File List

**Created/Modified:**
- `pcmrp_tools/bmad_automation/workflow_entry_wrapper.py` - Added ProjectType enum, DetectionSignal dataclass, ProjectTypeResult dataclass, SOURCE_DIRECTORIES constant, detect_source_directories(), PACKAGE_FILES constant, detect_package_files(), SOURCE_EXTENSIONS constant, EXCLUDED_DIRS constant, SOURCE_FILE_THRESHOLD constant, count_source_files(), detect_project_type()
- `tests/bmad_automation/test_workflow_entry_wrapper.py` - Added 85 tests for project type detection covering all acceptance criteria
