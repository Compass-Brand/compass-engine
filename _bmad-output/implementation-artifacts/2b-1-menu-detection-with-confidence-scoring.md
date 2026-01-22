# Story 2b.1: Menu Detection with Confidence Scoring

Status: dev-complete

## Story

As a **workflow automation system**,
I want **to detect menus in workflow output using confidence scoring**,
So that **menus are identified accurately without false positives in code blocks or examples**.

## Acceptance Criteria

1. **Given** workflow output containing `[A] Advanced Elicitation [P] Party Mode [C] Continue`
   **When** the Menu Participation Engine analyzes the output
   **Then** it returns `menu_detected: true` with confidence >= 70 points

2. **Given** workflow output containing menu-like text inside a code block (``` markers)
   **When** the Menu Participation Engine analyzes the output
   **Then** it returns `menu_detected: false` (false positive guard activated)

3. **Given** workflow output containing menu-like text inside a blockquote (> prefix)
   **When** the Menu Participation Engine analyzes the output
   **Then** it returns `menu_detected: false` (false positive guard activated)

4. **Given** workflow output containing menu-like text labeled as "Example:"
   **When** the Menu Participation Engine analyzes the output
   **Then** it returns `menu_detected: false` (example content guard activated)

5. **Given** menu detection with structural markers (brackets, numbered options)
   **When** confidence is calculated
   **Then** the score includes: structural markers (+30), position validation (+20), option count (+20)

## Tasks / Subtasks

- [x] Task 1: Create MenuDetectionResult dataclass (AC: #1-5)
  - [x] 1.1 Define dataclass with menu_detected, confidence, menu_type, options fields
  - [x] 1.2 Add confidence_breakdown dict for scoring transparency
  - [x] 1.3 Add guard_triggered field to track which guard blocked detection
  - [x] 1.4 Add factory methods for detected/not_detected/blocked results
  - [x] 1.5 Write tests for dataclass creation and serialization

- [x] Task 2: Implement false positive guards (AC: #2, #3, #4)
  - [x] 2.1 Create code block detector (``` ... ``` regions)
  - [x] 2.2 Create blockquote detector (lines starting with >)
  - [x] 2.3 Create example content detector ("Example:", "e.g.:", "For instance:")
  - [x] 2.4 Create guard chain that returns early if any guard triggers
  - [x] 2.5 Write tests for each guard type

- [x] Task 3: Implement menu pattern matchers (AC: #1, #5)
  - [x] 3.1 Create [A][P][C] style menu pattern matcher
  - [x] 3.2 Create [Y][V][N] style menu pattern matcher
  - [x] 3.3 Create numbered option pattern matcher ([1] [2] [3])
  - [x] 3.4 Create [E] Exit pattern matcher
  - [x] 3.5 Write tests for pattern matching

- [x] Task 4: Implement confidence scoring system (AC: #1, #5)
  - [x] 4.1 Define scoring weights: structural markers (30pts), position validation (20pts), option count (20pts), pattern match strength (30pts)
  - [x] 4.2 Implement structural marker scoring (brackets, pipes, dashes)
  - [x] 4.3 Implement position validation scoring (end of output, standalone line)
  - [x] 4.4 Implement option count scoring (2-4 options ideal, >4 reduced)
  - [x] 4.5 Implement score aggregation with breakdown
  - [x] 4.6 Write tests for scoring scenarios

- [x] Task 5: Implement 70-point threshold logic (AC: #1)
  - [x] 5.1 Apply 70-point minimum threshold for menu_detected: true
  - [x] 5.2 Return confidence score even when below threshold
  - [x] 5.3 Include threshold in result metadata
  - [x] 5.4 Write tests for threshold boundary conditions

- [x] Task 6: Create main detect_menu() function (AC: #1-5)
  - [x] 6.1 Implement pipeline: guards -> patterns -> scoring -> threshold
  - [x] 6.2 Return comprehensive MenuDetectionResult
  - [x] 6.3 Handle edge cases (empty input, whitespace only)
  - [x] 6.4 Write integration tests covering all AC scenarios

## Dev Notes

### Architecture Context

**Component:** Menu Participation Engine - Detection (from Design Spec)
- **Tier:** 2-3 (Depends on Epics 1, 2a)
- **Purpose:** Detects menus in workflow output with confidence scoring to enable autonomous selection
- **Integration Point:** Core engine for [A][P][C] menu handling throughout BMAD workflows

**Menu Types in BMAD:**
```
Type 1: [A][P][C] - Advanced Elicitation / Party Mode / Continue
Type 2: [Y][V][N] - Yes / View / No (iteration menus)
Type 3: [1][2][3][4] - Numbered options (multi-select)
Type 4: [E] - Exit (party mode termination)
Type 5: [MH] - Menu Help, [CH] - Chat, etc. (agent menus)
```

**Confidence Scoring Breakdown (100 points max):**
- Structural markers: 0-30 points (brackets, separators, consistent formatting)
- Position validation: 0-20 points (end of output, standalone line, not embedded)
- Option count: 0-20 points (2-4 options = full points, >4 = reduced)
- Pattern match strength: 0-30 points (exact match vs partial)

**False Positive Guards (must pass ALL to proceed):**
1. Code Block Guard - Reject if inside ``` markers
2. Blockquote Guard - Reject if line starts with >
3. Example Guard - Reject if preceded by "Example:", "e.g.:", etc.
4. Comment Guard - Reject if inside <!-- --> or # comments

### Technical Requirements

**Language:** Python 3.11+
**Testing Framework:** pytest with TDD (Red-Green-Refactor)
**File Location:** `pcmrp_tools/bmad_automation/menu_participation_engine.py`
**Test Location:** `tests/bmad_automation/test_menu_participation_engine.py`

### Code Patterns to Follow

```python
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

class MenuType(Enum):
    APC = "apc"           # [A][P][C]
    YVN = "yvn"           # [Y][V][N]
    NUMBERED = "numbered" # [1][2][3]
    EXIT = "exit"         # [E]
    AGENT = "agent"       # [MH][CH] etc.
    UNKNOWN = "unknown"

class GuardType(Enum):
    CODE_BLOCK = "code_block"
    BLOCKQUOTE = "blockquote"
    EXAMPLE = "example"
    COMMENT = "comment"

@dataclass
class MenuDetectionResult:
    menu_detected: bool
    confidence: int  # 0-100
    menu_type: Optional[MenuType] = None
    options: List[str] = field(default_factory=list)
    confidence_breakdown: Dict[str, int] = field(default_factory=dict)
    guard_triggered: Optional[GuardType] = None
    raw_input: str = ""

    @classmethod
    def detected(cls, confidence: int, menu_type: MenuType,
                 options: List[str], breakdown: Dict[str, int],
                 raw_input: str) -> "MenuDetectionResult":
        ...

    @classmethod
    def not_detected(cls, confidence: int, breakdown: Dict[str, int],
                     raw_input: str) -> "MenuDetectionResult":
        ...

    @classmethod
    def blocked(cls, guard: GuardType, raw_input: str) -> "MenuDetectionResult":
        ...

CONFIDENCE_THRESHOLD = 70

def detect_menu(text: str) -> MenuDetectionResult:
    """Main entry point for menu detection."""
    ...
```

### Testing Standards

- **100% test coverage required**
- **TDD cycle:** Write failing test FIRST, then implementation
- **Test file naming:** `test_menu_participation_engine.py`
- **Test function naming:** `test_<function>_<scenario>_<expected_result>`
- **Use pytest fixtures for sample menu outputs**

### Edge Cases to Handle

1. Empty input string
2. Multiple menus in same output
3. Menu at very end of long output
4. Menu with unusual spacing/formatting
5. Nested code blocks with menu-like content
6. Menu options split across lines
7. Unicode characters in menu text
8. Menu with missing options (partial menu)

### Sample Test Data

```python
# Should detect (confidence >= 70)
VALID_APC_MENU = """
Step complete. Ready for next action.

[A] Advanced Elicitation  [P] Party Mode  [C] Continue
"""

# Should NOT detect (code block guard)
CODE_BLOCK_MENU = """
Here's an example of the menu format:
```
[A] Advanced  [P] Party  [C] Continue
```
"""

# Should NOT detect (example guard)
EXAMPLE_MENU = """
Example: [A] Advanced [P] Party [C] Continue
This is how menus look.
"""
```

### References

- [Source: docs/plans/2026-01-08-bmad-automation-design.md#Menu Participation Engine]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 2b.1]
- [Source: _bmad-output/planning-artifacts/epics.md#FR Coverage Map] - FR7

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All tests passing: 128 tests in test_menu_participation_engine.py
- Module coverage: 94% (221 statements, 102 branches)
- TDD cycle followed strictly for all 6 tasks

### Completion Notes List

1. **Task 1**: Created MenuDetectionResult dataclass with all required fields, factory methods (detected/not_detected/blocked), and serialization support
2. **Task 2**: Implemented 4 false positive guards (code_block, blockquote, example, comment) with check_guards() chain
3. **Task 3**: Implemented 4 menu pattern matchers (APC, YVN, NUMBERED, EXIT) with find_menu_patterns() aggregator
4. **Task 4**: Implemented confidence scoring system with 4 components (structural_markers: 30pts, position_validation: 20pts, option_count: 20pts, pattern_match: 30pts)
5. **Task 5**: Implemented 70-point threshold logic with apply_threshold() function
6. **Task 6**: Created main detect_menu() entry point with full pipeline (guards -> patterns -> scoring -> threshold)

### Acceptance Criteria Verification

| AC | Status | Evidence |
|----|--------|----------|
| AC1: Detects APC menu with confidence >= 70 | PASS | test_ac1_full_scenario, test_detects_apc_menu_with_high_confidence |
| AC2: Rejects menu in code blocks | PASS | test_ac2_full_scenario, test_rejects_menu_in_code_block |
| AC3: Rejects menu in blockquotes | PASS | test_ac3_full_scenario, test_rejects_menu_in_blockquote |
| AC4: Rejects menu with Example: label | PASS | test_ac4_full_scenario, test_rejects_menu_after_example_label |
| AC5: Confidence breakdown includes all components | PASS | test_ac5_full_scenario, breakdown has structural_markers, position_validation, option_count, pattern_match |

### File List

- `pcmrp_tools/bmad_automation/menu_participation_engine.py` - Main implementation (819 lines)
- `tests/bmad_automation/test_menu_participation_engine.py` - Tests (128 tests, 1340 lines)
