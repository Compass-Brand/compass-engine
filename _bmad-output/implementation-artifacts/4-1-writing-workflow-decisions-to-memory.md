# Story 4.1: Writing Workflow Decisions to Memory

Status: completed

## Story

As a **workflow automation system**,
I want **workflow decisions and outcomes written to Forgetful memory**,
So that **future workflows can learn from past experiences**.

## Acceptance Criteria

1. **Given** a workflow completes with key decisions made
   **When** the Memory Bridge processes the workflow outcome
   **Then** it creates memories for each significant decision with appropriate importance level

2. **Given** a validation fix pattern resolves an issue
   **When** the fix is successful
   **Then** Memory Bridge writes a memory with `type: "fix_pattern"`, the error signature, and the solution

3. **Given** a menu selection leads to successful outcome
   **When** workflow completes successfully
   **Then** Memory Bridge optionally records the selection pattern for similar future contexts

4. **Given** memory content exceeds 2000 characters
   **When** Memory Bridge prepares the memory
   **Then** it summarizes to fit the atomic memory limit while preserving key information

5. **Given** memory is created
   **When** the write completes
   **Then** it includes: `project_id`, `workflow_id`, `keywords`, `tags`, and appropriate `importance` level

## Tasks / Subtasks

- [x] Task 1: Create MemoryBridge class structure (AC: #1, #5)
  - [x] 1.1 Define MemoryBridge class with Forgetful MCP connection handling
  - [x] 1.2 Create WorkflowDecision dataclass for decision capture
  - [x] 1.3 Create MemoryEntry dataclass matching Forgetful schema
  - [x] 1.4 Add importance level constants (ARCHITECTURAL=9-10, PATTERN=7-8, MILESTONE=6-7)
  - [x] 1.5 Write tests for class structure

- [x] Task 2: Implement decision extraction (AC: #1)
  - [x] 2.1 Create extract_decisions() to identify significant decisions from workflow context
  - [x] 2.2 Define decision significance criteria (architectural, technical, process)
  - [x] 2.3 Map decision types to importance levels
  - [x] 2.4 Write tests for decision extraction

- [x] Task 3: Implement fix pattern memory creation (AC: #2)
  - [x] 3.1 Create FixPattern dataclass with error_signature, solution, success_rate fields
  - [x] 3.2 Implement create_fix_pattern_memory() to format fix patterns
  - [x] 3.3 Generate searchable keywords from error signature
  - [x] 3.4 Include workflow context (step, validation type) in memory
  - [x] 3.5 Write tests for fix pattern memories

- [x] Task 4: Implement menu selection pattern recording (AC: #3)
  - [x] 4.1 Create MenuSelectionPattern dataclass with context, selection, outcome fields
  - [x] 4.2 Implement record_selection_pattern() for optional pattern storage
  - [x] 4.3 Calculate outcome success signal (workflow completed, validation passed)
  - [x] 4.4 Add configurable toggle for selection pattern recording
  - [x] 4.5 Write tests for selection patterns

- [x] Task 5: Implement content summarization (AC: #4)
  - [x] 5.1 Create summarize_content() to reduce content to 2000 char limit
  - [x] 5.2 Preserve key information: decision, rationale, outcome
  - [x] 5.3 Implement truncation with "..." indicator when summarized
  - [x] 5.4 Add summary_applied flag to memory metadata
  - [x] 5.5 Write tests for content over/under limit

- [x] Task 6: Implement Forgetful MCP write operations (AC: #5)
  - [x] 6.1 Implement write_memory() using execute_forgetful_tool("create_memory", ...)
  - [x] 6.2 Include all required fields: title, content, context, keywords, tags, importance, project_ids
  - [x] 6.3 Add workflow_id to tags for traceability
  - [x] 6.4 Handle MCP connection errors (defer to Story 4.3 graceful degradation)
  - [x] 6.5 Write tests with mocked MCP calls

- [x] Task 7: Create main process_workflow_outcome() function (AC: #1-5)
  - [x] 7.1 Orchestrate: extract decisions -> create memories -> write to Forgetful
  - [x] 7.2 Batch memory creation for efficiency
  - [x] 7.3 Return summary of memories created
  - [x] 7.4 Write integration tests

## Dev Notes

### Architecture Context

**Component:** Memory Bridge (from Design Spec)
- **Tier:** 4 (Depends on Context Pre-Loader from Epic 2a)
- **Purpose:** Writes workflow decisions and outcomes to Forgetful memory for cross-session learning
- **Integration:** Uses Context Pre-Loader to read existing patterns before writing new ones

**Memory Types to Create:**
```
1. Decision Memory - Architectural/technical decisions made during workflow
   - Importance: 9-10 (architectural), 7-8 (technical)
   - Example: "Chose PostgreSQL over MongoDB for X reason"

2. Fix Pattern Memory - Successful resolution of validation errors
   - Importance: 7-8
   - Example: "Missing import error resolved by adding X"

3. Selection Pattern Memory - Menu selections that led to success (optional)
   - Importance: 5-6
   - Example: "Selected [A] Advanced Elicitation for unclear requirements"

4. Milestone Memory - Workflow completion markers
   - Importance: 6-7
   - Example: "Epic 2a completed with all stories passing"
```

**Forgetful Memory Schema:**
```python
{
    "title": "Short title (<200 chars)",
    "content": "Memory content (<2000 chars)",
    "context": "Why this matters (<500 chars)",
    "keywords": ["kw1", "kw2"],  # max 10
    "tags": ["tag1", "tag2"],     # max 10
    "importance": 7,              # 1-10
    "project_ids": [1]            # link to project
}
```

### Technical Requirements

**Language:** Python 3.11+
**Testing Framework:** pytest with TDD (Red-Green-Refactor)
**File Location:** `pcmrp_tools/bmad_automation/memory_bridge.py`
**Test Location:** `tests/bmad_automation/test_memory_bridge.py`

### Code Patterns to Follow

```python
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import IntEnum

class ImportanceLevel(IntEnum):
    ARCHITECTURAL = 10
    ARCHITECTURAL_LOW = 9
    PATTERN_HIGH = 8
    PATTERN = 7
    MILESTONE = 6
    SELECTION = 5

@dataclass
class WorkflowDecision:
    decision_type: str  # "architectural", "technical", "process"
    description: str
    rationale: str
    outcome: Optional[str] = None
    importance: ImportanceLevel = ImportanceLevel.PATTERN

@dataclass
class FixPattern:
    error_signature: str  # Unique identifier for the error type
    solution: str
    workflow_step: str
    validation_type: str
    success_rate: float = 1.0  # Initially 100%

@dataclass
class MemoryEntry:
    title: str
    content: str
    context: str
    keywords: List[str]
    tags: List[str]
    importance: int
    project_ids: List[int]
    workflow_id: Optional[str] = None

class MemoryBridge:
    def __init__(self, project_id: int, workflow_id: str):
        self.project_id = project_id
        self.workflow_id = workflow_id

    def extract_decisions(self, workflow_context: Dict[str, Any]) -> List[WorkflowDecision]:
        """Extract significant decisions from workflow context."""
        ...

    def create_fix_pattern_memory(self, pattern: FixPattern) -> MemoryEntry:
        """Create memory entry for a successful fix pattern."""
        ...

    def record_selection_pattern(self, context: str, selection: str,
                                  outcome: str) -> Optional[MemoryEntry]:
        """Optionally record menu selection pattern."""
        ...

    def summarize_content(self, content: str, max_length: int = 2000) -> str:
        """Summarize content to fit atomic memory limit."""
        ...

    async def write_memory(self, entry: MemoryEntry) -> Dict[str, Any]:
        """Write memory to Forgetful MCP."""
        ...

    async def process_workflow_outcome(self,
                                        workflow_context: Dict[str, Any],
                                        fix_patterns: List[FixPattern] = None,
                                        record_selections: bool = False) -> Dict[str, Any]:
        """Main entry point for processing workflow outcomes."""
        ...
```

### Testing Standards

- **100% test coverage required**
- **TDD cycle:** Write failing test FIRST, then implementation
- **Test file naming:** `test_memory_bridge.py`
- **Test function naming:** `test_<function>_<scenario>_<expected_result>`
- **Mock Forgetful MCP calls** - do not make real MCP calls in tests

### Edge Cases to Handle

1. Empty workflow context (no decisions to extract)
2. Content exactly at 2000 character limit
3. Keywords exceeding 10 item limit
4. Multiple fix patterns for same error signature
5. MCP connection failure (defer to Story 4.3)
6. Invalid project_id
7. Unicode characters in decision text
8. Very long error signatures

### Dependencies

**Epic 2a Components Used:**
- Context Pre-Loader (query existing memories before writing)

**Story 4.3 Handles:**
- Graceful degradation when Forgetful unavailable
- Memory queuing for offline writes
- This story assumes MCP is available; error handling deferred to 4.3

### Sample Test Data

```python
SAMPLE_WORKFLOW_CONTEXT = {
    "workflow_id": "dev-story-123",
    "workflow_name": "dev-story",
    "decisions": [
        {
            "type": "technical",
            "description": "Used dataclass instead of TypedDict",
            "rationale": "Better IDE support and validation"
        }
    ],
    "validation_results": {
        "passed": True,
        "errors_fixed": 2
    }
}

SAMPLE_FIX_PATTERN = FixPattern(
    error_signature="ImportError:missing_module:dataclasses",
    solution="Add 'from dataclasses import dataclass' import",
    workflow_step="2a-1",
    validation_type="syntax"
)
```

### References

- [Source: plans/2026-01-08-bmad-automation-design.md#Memory Integration]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 4.1]
- [Source: _bmad-output/planning-artifacts/epics.md#FR Coverage Map] - FR32

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A - Clean TDD implementation with no debugging required.

### Completion Notes List

1. All 7 tasks completed using strict TDD (RED-GREEN-REFACTOR)
2. 91 tests written and passing
3. All 5 acceptance criteria verified
4. Added pytest-asyncio for async test support
5. Updated pyproject.toml with asyncio_mode="auto"
6. Memory Bridge integrates with Forgetful MCP via injectable client

### File List

- `pcmrp_tools/bmad_automation/memory_bridge.py` - Main implementation (178 statements)
- `tests/bmad_automation/test_memory_bridge.py` - Tests (91 test functions)
- `pyproject.toml` - Added asyncio_mode configuration
