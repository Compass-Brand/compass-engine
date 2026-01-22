# Story 2b.6: Batch-Continue Logic

Status: done

## Story

As a **workflow automation system**,
I want **tier-based batching of sequential continue operations**,
So that **simple projects flow faster while complex projects get more checkpoints**.

## Acceptance Criteria

1. **Given** a Tier 0-1 project with sequential continue menus
   **When** the Menu Participation Engine processes them
   **Then** it auto-continues all without batching (auto-all mode)

2. **Given** a Tier 2 project with sequential continue menus
   **When** the Menu Participation Engine processes them
   **Then** it batches up to 5 continues before presenting checkpoint

3. **Given** a Tier 3 project with sequential continue menus
   **When** the Menu Participation Engine processes them
   **Then** it batches up to 3 continues before presenting checkpoint

4. **Given** a Tier 4 project with sequential continue menus
   **When** the Menu Participation Engine processes them
   **Then** it batches exactly 1 continue (batch size 1) for maximum oversight, presenting checkpoint after each operation

5. **Given** a batch completes
   **When** the checkpoint is presented
   **Then** it shows summary of batched operations with option to review details

6. **Given** batch-continue mode is active
   **When** operations are batched
   **Then** context is managed to avoid redundant menu state in history, reducing token usage compared to unbatched operation (NFR3 compliance)

## Tasks / Subtasks

### Task 1: Define Batch Configuration (AC: #1, #2, #3, #4)

- [x] Task 1.1: Define BATCH_SIZE_BY_TIER constant dict:
  - Tier 0: AUTO_ALL (special value -1)
  - Tier 1: AUTO_ALL (special value -1)
  - Tier 2: 5
  - Tier 3: 3
  - Tier 4: 1
- [x] Task 1.2: Define BatchMode enum (AUTO_ALL, BATCHED, SINGLE_STEP)
- [x] Task 1.3: Define BatchConfig dataclass (tier, batch_size, mode)
- [x] Task 1.4: Implement get_batch_config(tier: int) returning BatchConfig
- [x] Task 1.5: Write tests for batch size lookup per tier

### Task 2: Create BatchContinueManager Class (AC: #1-4)

- [x] Task 2.1: Define BatchState dataclass (operations: List, start_time, tier)
- [x] Task 2.2: Implement __init__(tier: int) setting batch config from tier
- [x] Task 2.3: Implement start_batch() to begin tracking batch operations
- [x] Task 2.4: Implement add_operation(operation: str) to track batched operation
- [x] Task 2.5: Implement is_batch_complete() returning bool based on batch size
- [x] Task 2.6: Implement get_batch_summary() returning List of operation descriptions
- [x] Task 2.7: Implement end_batch() returning BatchSummary and resetting state
- [x] Task 2.8: Write tests for batch lifecycle per tier

### Task 3: Implement Auto-All Mode (AC: #1)

- [x] Task 3.1: Detect continue-type menus (options like [C], Continue, Proceed)
- [x] Task 3.2: Implement is_continue_menu(detection_result) returning bool
- [x] Task 3.3: For Tier 0-1: bypass batching entirely, auto-select continue
- [x] Task 3.4: Track auto-all operations for summary at workflow end
- [x] Task 3.5: Write tests for auto-all behavior with sequential continues

### Task 4: Implement Checkpoint Presentation (AC: #5)

- [x] Task 4.1: Define BatchCheckpoint dataclass (operations, summary, has_details)
- [x] Task 4.2: Implement format_checkpoint_message(batch_summary) returning str
- [x] Task 4.3: Include operation count, key actions, and elapsed time
- [x] Task 4.4: Implement format_detail_view(batch_summary) for expanded view
- [x] Task 4.5: Provide user options: [C]ontinue, [R]eview details, [S]top
- [x] Task 4.6: Write tests for checkpoint message formatting

### Task 5: Context Management (AC: #6)

- [x] Task 5.1: Implement compact_batch_history(batch_operations) for token efficiency
- [x] Task 5.2: Store only batch summary in history, not individual operations
- [x] Task 5.3: Define BatchHistoryEntry for compacted storage
- [x] Task 5.4: Calculate token savings: len(compacted) < sum(len(individual))
- [x] Task 5.5: Write tests verifying token reduction

### Task 6: Integration with MenuSelector (AC: All)

- [x] Task 6.1: Add BatchContinueManager to MenuSelector initialization
- [x] Task 6.2: Modify select_or_present() to use batch logic for continue menus
- [x] Task 6.3: On batch complete: present checkpoint via existing channel
- [x] Task 6.4: Integrate with MenuHistoryManager for compact history recording
- [x] Task 6.5: Handle tier changes mid-workflow (reconfigure batch size)
- [x] Task 6.6: Write integration tests showing full batch flow per tier

## Dev Notes

### Architecture Context

**Component:** Menu Participation Engine - Batch Continue Logic (extends Stories 2b.1-2b.5)
- **Tier:** 2-3 (Depends on Story 2b.5 Menu History Tracking)
- **Purpose:** Implement tier-based batching of sequential continue operations
- **Integration:** Extends MenuSelector with batch management and checkpoint presentation

**Design Reference (from Architecture Document):**

```
BATCH CONTINUE RULES BY TIER:
  Tier 0-1 (Quick Flow):
    - Auto-all mode: no batching, continuous flow
    - Single summary at workflow completion

  Tier 2 (Standard):
    - Batch size: 5 continues
    - Checkpoint shows: "Completed 5 steps: [summary]. Continue?"

  Tier 3 (Thorough):
    - Batch size: 3 continues
    - Checkpoint shows: "Completed 3 steps: [summary]. Continue or review?"

  Tier 4 (Enterprise):
    - Batch size: 1 (effective single-step)
    - Every operation gets explicit confirmation
```

### Related Stories

- **Story 2b.2:** Automatic Menu Selection (continue detection)
- **Story 2b.5:** Menu History Tracking (compact history storage)
- **Story 2a.4:** Tier Suggestion (tier determines batch size)
- **Story 2a.7:** Adaptive Behavior Configuration (tier profiles)

### Files to Create/Modify

- `pcmrp_tools/bmad_automation/batch_continue.py` (NEW)
- `pcmrp_tools/bmad_automation/menu_selection.py` (MODIFY - add batch logic)
- `tests/bmad_automation/test_batch_continue.py` (NEW)

### TDD Approach

For each task:
1. Write failing test for expected behavior
2. Implement minimal code to pass
3. Refactor while keeping tests green

---

## Dev Agent Record

**Agent Model:** claude-opus-4-5-20251101 (via parallel subagents)

**Debug Log Refs:**
- Agent a5c81b2: Tasks 1-3 (BatchConfig, BatchContinueManager, Auto-All Mode)
- Agent a1c3e39: Tasks 4-5 (Checkpoint Presentation, Context Management)
- Agent aa32ea4: Task 6 (MenuSelector Batch Integration)
- ADVERSARIAL Code Review (10 issues found, 6 fixed)

**Completion Notes:**
- Task 1: Created BATCH_SIZE_BY_TIER dict with {0: -1, 1: -1, 2: 5, 3: 3, 4: 1}, BatchMode enum, BatchConfig dataclass, get_batch_config()
- Task 2: Implemented BatchContinueManager with start_batch(), add_operation(), is_batch_complete(), get_batch_summary(), end_batch(), has_active_batch()
- Task 3: Created CONTINUE_PATTERNS for menu detection, is_continue_menu(), auto-all bypass for Tier 0-1, auto-all operation tracking
- Task 4: Created BatchCheckpoint dataclass, format_checkpoint_message() with operation count/elapsed time, format_detail_view(), user options [C]/[R]/[S]
- Task 5: Implemented compact_batch_history() for token efficiency, BatchHistoryEntry for compacted storage, token savings verification
- Task 6: Integrated BatchContinueManager into MenuSelector, batch logic for continue menus, tier change handling mid-workflow

**Code Review Fixes:**
- Added has_active_batch() public method for encapsulation (instead of exposing _batch_state)
- Centralized CONTINUE_PATTERNS constant usage across is_continue_menu() and detect functions
- Added tests for tier change mid-workflow (reconfigure batch size dynamically)
- Added tests for full batch flow per tier (Tier 0-4 end-to-end)

**Files Modified:**
- `pcmrp_tools/bmad_automation/batch_continue.py` (NEW - 134 statements, 99% coverage)
- `pcmrp_tools/bmad_automation/menu_selection.py` (MODIFIED - added batch logic integration)
- `tests/bmad_automation/test_batch_continue.py` (NEW - 130 tests)
