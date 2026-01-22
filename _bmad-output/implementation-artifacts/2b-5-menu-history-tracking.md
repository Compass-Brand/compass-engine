# Story 2b.5: Menu History Tracking

Status: done

## Story

As a **workflow automation system**,
I want **menu selection history tracked for recovery purposes**,
So that **interrupted workflows can resume with correct menu context**.

## Acceptance Criteria

1. **Given** a menu selection is made (automatic or manual)
   **When** the selection is processed
   **Then** it is recorded to `menu_history` with timestamp, menu_id, selection, and confidence

2. **Given** a workflow is interrupted after menu selections
   **When** the workflow resumes
   **Then** menu history is available to restore context

3. **Given** menu history grows beyond 100 entries
   **When** a new entry is added
   **Then** oldest entries are pruned (FIFO) to maintain limit

4. **Given** a recovery scenario needs to replay menu selections
   **When** history is accessed
   **Then** entries are returned in chronological order with full metadata

## Tasks / Subtasks

### Task 1: Define MenuHistoryEntry Dataclass (AC: #1, #4)

- [x] Task 1.1: Define MenuHistoryEntry dataclass with fields:
  - timestamp: datetime
  - menu_id: str
  - selection: str
  - confidence: float
  - source: SelectionSource (AUTO, MANUAL, ESCALATED)
  - workflow_context: Optional[str]
- [x] Task 1.2: Define SelectionSource enum (AUTO, MANUAL, ESCALATED)
- [x] Task 1.3: Implement to_dict() for serialization
- [x] Task 1.4: Implement from_dict() for deserialization
- [x] Task 1.5: Write tests for dataclass creation and serialization

### Task 2: Create MenuHistoryManager Class (AC: #1, #3)

- [x] Task 2.1: Define MAX_HISTORY_SIZE constant = 100
- [x] Task 2.2: Implement __init__() with empty history list
- [x] Task 2.3: Implement add_entry(entry: MenuHistoryEntry) with FIFO pruning
- [x] Task 2.4: Implement get_history() returning List[MenuHistoryEntry]
- [x] Task 2.5: Implement get_recent(count: int) returning most recent entries
- [x] Task 2.6: Implement clear_history() for reset scenarios
- [x] Task 2.7: Write tests for FIFO behavior at boundary (99, 100, 101 entries)

### Task 3: File Persistence for Recovery (AC: #2)

- [x] Task 3.1: Define history file path (_bmad-output/.menu-history/session-{id}.json)
- [x] Task 3.2: Implement save_to_file(path: Path) for persistence
- [x] Task 3.3: Implement load_from_file(path: Path) for recovery
- [x] Task 3.4: Handle missing/corrupt file scenarios gracefully
- [x] Task 3.5: Implement get_session_history_path() for path generation
- [x] Task 3.6: Write tests for persistence and recovery including error cases

### Task 4: Chronological Access (AC: #4)

- [x] Task 4.1: Implement get_entries_since(timestamp: datetime) returning filtered list
- [x] Task 4.2: Implement get_entries_for_menu(menu_id: str) returning filtered list
- [x] Task 4.3: Implement get_entries_for_workflow(workflow: str) returning filtered list
- [x] Task 4.4: Ensure all queries return chronological order
- [x] Task 4.5: Write tests for filtering and ordering

### Task 5: Integration with MenuSelector (AC: All)

- [x] Task 5.1: Add MenuHistoryManager to MenuSelector initialization
- [x] Task 5.2: Record entry after every selection (auto, manual, escalated)
- [x] Task 5.3: Add record_selection() helper method to MenuSelector
- [x] Task 5.4: Persist history on workflow state checkpoints
- [x] Task 5.5: Load history on workflow resume
- [x] Task 5.6: Write integration tests showing full selection-to-recovery flow

## Dev Notes

### Architecture Context

**Component:** Menu Participation Engine - Menu History Tracking (extends Stories 2b.1-2b.4)
- **Tier:** 2-3 (Depends on Story 2b.4 Nested Menu Handling)
- **Purpose:** Track menu selection history for recovery and context restoration
- **Integration:** Extends MenuSelector with persistent history tracking

**Design Reference (from Architecture Document):**

```
MENU HISTORY TRACKING:
- Record every selection with full metadata
- FIFO pruning at 100 entries (token efficiency)
- Chronological access for recovery replay
- File persistence for session recovery

HISTORY ENTRY FIELDS:
- timestamp: When selection was made
- menu_id: Unique menu identifier
- selection: The selected option
- confidence: Confidence score at selection time
- source: How selection was made (AUTO/MANUAL/ESCALATED)
- workflow_context: Current workflow/step context
```

### Related Stories

- **Story 2b.2:** Automatic Menu Selection (selection source tracking)
- **Story 2b.4:** Nested Menu Handling (context for history entries)
- **Story 3.2:** Workflow Resume (uses history for recovery)

### Files to Create/Modify

- `pcmrp_tools/bmad_automation/menu_history.py` (NEW)
- `pcmrp_tools/bmad_automation/menu_selection.py` (MODIFY - add history recording)
- `tests/bmad_automation/test_menu_history.py` (NEW)

### TDD Approach

For each task:
1. Write failing test for expected behavior
2. Implement minimal code to pass
3. Refactor while keeping tests green

---

## Dev Agent Record

**Agent Model:** claude-opus-4-5-20251101 (via parallel subagents)

**Debug Log Refs:**
- Agent a012e53: Tasks 1-2 (MenuHistoryEntry, MenuHistoryManager)
- Agent a495c83: Tasks 3-4 (File Persistence, Chronological Access)
- Agent a0cb99c: Task 5 (MenuSelector Integration)
- ADVERSARIAL Code Review (9 issues found, 8 fixed)

**Completion Notes:**
- Task 1: Created MenuHistoryEntry dataclass with SelectionSource enum, to_dict/from_dict serialization with confidence validation (0.0-1.0 in __post_init__)
- Task 2: Implemented MenuHistoryManager with deque(maxlen=100) for O(1) FIFO pruning, get_history(), get_recent(), clear_history()
- Task 3: Created file persistence with session ID path generation, save_to_file/load_from_file with corrupt file handling, path injection validation
- Task 4: Implemented chronological filtering: get_entries_since(), get_entries_for_menu(), get_entries_for_workflow() - all return chronological order
- Task 5: Integrated MenuHistoryManager into MenuSelector with record_selection() helper, persistence on checkpoints, recovery on resume

**Code Review Fixes:**
- Added confidence range validation (0.0-1.0) in MenuHistoryEntry.__post_init__
- Changed _history from list to deque(maxlen=100) for O(1) FIFO operations
- Added session ID path injection validation in save_to_file/load_from_file
- Added full integration tests for selection-to-recovery flow

**Files Modified:**
- `pcmrp_tools/bmad_automation/menu_history.py` (NEW - 106 statements, 97% coverage)
- `pcmrp_tools/bmad_automation/menu_selection.py` (MODIFIED - added history recording integration)
- `tests/bmad_automation/test_menu_history.py` (NEW - 94 tests)
