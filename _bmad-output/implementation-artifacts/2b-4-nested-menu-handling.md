# Story 2b.4: Nested Menu Handling

Status: done

## Story

As a **workflow user**,
I want **nested menus within Party Mode or Advanced Elicitation to be handled correctly**,
So that **sub-workflows complete properly before returning to the parent menu**.

## Acceptance Criteria

1. **Given** Party Mode is active and presents an internal menu
   **When** the Menu Participation Engine detects the nested menu
   **Then** it tracks the menu depth and handles selection within Party Mode context

2. **Given** Advanced Elicitation presents technique selection menu
   **When** the Menu Participation Engine processes the menu
   **Then** it applies elicitation-specific selection logic

3. **Given** a nested menu completes with a selection
   **When** control returns to the parent workflow
   **Then** the parent workflow state is restored correctly

4. **Given** nested menu depth exceeds 3 levels
   **When** the Menu Participation Engine detects this
   **Then** it logs a warning and escalates to user for manual navigation

## Tasks / Subtasks

### Task 1: Create MenuDepthTracker (AC: #1, #4)

- [x] Task 1.1: Define MenuContext dataclass (menu_id, parent_context, workflow_type, depth_level)
- [x] Task 1.2: Define MAX_NESTED_DEPTH constant = 3
- [x] Task 1.3: Implement push_menu_context() to track entering nested menu
- [x] Task 1.4: Implement pop_menu_context() to track exiting nested menu
- [x] Task 1.5: Implement get_current_depth() returning current nesting level
- [x] Task 1.6: Implement is_depth_exceeded() returning bool
- [x] Task 1.7: Write tests for depth tracking including edge cases

### Task 2: Party Mode Context Handling (AC: #1)

- [x] Task 2.1: Define PartyModeMenuContext extending MenuContext
- [x] Task 2.2: Implement detect_party_mode_menu() for internal Party Mode menus
- [x] Task 2.3: Implement handle_party_mode_selection() with Party Mode-specific logic
- [x] Task 2.4: Maintain agent roster context within nested menus
- [x] Task 2.5: Write tests for Party Mode nested menu scenarios

### Task 3: Advanced Elicitation Context Handling (AC: #2)

- [x] Task 3.1: Define ElicitationMenuContext extending MenuContext
- [x] Task 3.2: Implement detect_elicitation_menu() for technique selection menus
- [x] Task 3.3: Implement handle_elicitation_selection() with elicitation-specific logic
- [x] Task 3.4: Apply appropriate confidence thresholds for elicitation menus
- [x] Task 3.5: Write tests for Advanced Elicitation nested menu scenarios

### Task 4: Parent State Restoration (AC: #3)

- [x] Task 4.1: Implement save_parent_state() before entering nested menu
- [x] Task 4.2: Implement restore_parent_state() after nested menu completes
- [x] Task 4.3: Handle state restoration on both normal completion and error paths
- [x] Task 4.4: Ensure continuation markers from parent are preserved
- [x] Task 4.5: Write tests for state restoration scenarios

### Task 5: Depth Exceeded Escalation (AC: #4)

- [x] Task 5.1: Implement handle_depth_exceeded() returning UserEscalation
- [x] Task 5.2: Log warning with full menu context stack
- [x] Task 5.3: Generate user-friendly message explaining nested depth issue
- [x] Task 5.4: Provide navigation suggestions in escalation message
- [x] Task 5.5: Write tests for depth exceeded handling

### Task 6: Integration with MenuSelector (AC: All)

- [x] Task 6.1: Add MenuDepthTracker to MenuSelector initialization
- [x] Task 6.2: Modify detect_and_select() to check depth before processing
- [x] Task 6.3: Route to appropriate context handler (PartyMode, Elicitation, or Standard)
- [x] Task 6.4: Integrate with existing selection history from Story 2b-2
- [x] Task 6.5: Write integration tests showing nested menu flows

## Dev Notes

### Architecture Context

**Component:** Menu Participation Engine - Nested Menu Handling (extends Stories 2b.1, 2b.2, 2b.3)
- **Tier:** 2-3 (Depends on Story 2b.3 BMB Threshold Checks)
- **Purpose:** Handle menus that appear within sub-workflows (Party Mode, Advanced Elicitation)
- **Integration:** Extends MenuSelector with depth tracking and context-aware selection

**Design Reference (from Architecture Document):**

```
NESTED MENU HANDLING:
- Maximum depth: 3 levels of nested workflow invocations
- Each level maintains its own menu context
- Parent state saved before entering, restored on exit
- Depth exceeded → escalate to user with warning

PARTY MODE CONTEXT:
- Internal menus may present agent selections, round controls
- Selection logic uses Party Mode-specific patterns
- Maintain agent roster context through nested selections

ADVANCED ELICITATION CONTEXT:
- Technique selection menus use elicitation patterns
- Apply different confidence thresholds for elicitation choices
- Track technique effectiveness for pattern learning
```

### Related Stories

- **Story 2b.1:** Menu Detection with Confidence Scoring (base detection)
- **Story 2b.2:** Automatic Menu Selection (base selection logic)
- **Story 2b.3:** BMB-Specific Thresholds (escalation triggers)
- **Story 5.1:** Party Mode Programmatic Input (Party Mode integration)

### Files to Create/Modify

- `pcmrp_tools/bmad_automation/nested_menu.py` (NEW)
- `pcmrp_tools/bmad_automation/menu_selection.py` (MODIFY - add depth tracking)
- `tests/bmad_automation/test_nested_menu.py` (NEW)

### TDD Approach

For each task:
1. Write failing test for expected behavior
2. Implement minimal code to pass
3. Refactor while keeping tests green

---

## Dev Agent Record

**Agent Model:** claude-opus-4-5-20251101 (via parallel subagents)

**Debug Log Refs:**
- Agent a3fa9db: Tasks 1-3 (MenuDepthTracker, PartyMode, Elicitation)
- Agent af1850a: Tasks 4-5 (State Restoration, Depth Escalation)
- Agent a748859: Task 6 (MenuSelector Integration)
- Agent a79b51e: ADVERSARIAL Code Review (9 issues found)

**Completion Notes:**
- Task 1: Created MenuDepthTracker with MAX_NESTED_DEPTH=3, MenuContext dataclass with parent linking, push/pop operations, and depth validation
- Task 2: Implemented PartyModeMenuContext with agent_roster and round_number tracking, party mode detection via PARTY_MODE_PATTERNS
- Task 3: Implemented ElicitationMenuContext with technique and phase tracking, elicitation detection via ELICITATION_PATTERNS
- Task 4: Created StateManager with state stack (not single state) for 3-level nesting support, save/restore with error path handling
- Task 5: Implemented handle_depth_exceeded() returning UserEscalation with context stack info and navigation suggestions
- Task 6: Integrated MenuDepthTracker into MenuSelector, added context handler routing via route_to_context_handler()

**Code Review Fixes:**
- Changed StateManager from single state to stack for proper 3-level nesting
- Added workflow_type and elicitation_phase validation in ElicitationMenuContext
- Added context_class parameter to push_menu_context() for specialized contexts
- Added route_to_context_handler() function for explicit routing logic

**Files Modified:**
- `pcmrp_tools/bmad_automation/nested_menu.py` (NEW - 195 statements, 90% coverage)
- `pcmrp_tools/bmad_automation/menu_selection.py` (MODIFIED - added depth tracking integration)
- `tests/bmad_automation/test_nested_menu.py` (NEW - 95 tests)
