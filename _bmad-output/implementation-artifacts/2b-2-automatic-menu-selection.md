# Story 2b.2: Automatic Menu Selection

Status: dev-complete

## Story

As a **workflow user**,
I want **menus to be selected automatically when confidence is high**,
So that **I don't have to manually select obvious choices**.

## Acceptance Criteria

1. **Given** a detected menu with confidence >= 80%
   **When** the Menu Participation Engine evaluates options
   **Then** it automatically selects the most appropriate option without user prompt

2. **Given** a detected menu with confidence between 50-79%
   **When** the Menu Participation Engine evaluates options
   **Then** it presents the menu to user with a recommended selection

3. **Given** a detected menu with confidence < 50%
   **When** the Menu Participation Engine evaluates options
   **Then** it presents the menu to user without recommendation

4. **Given** automatic selection is made
   **When** the selection is logged
   **Then** it includes `selection_reason` and `confidence_score` for auditability

5. **Given** any menu detection and selection operation
   **When** the operation completes under normal conditions
   **Then** total time from detection to selection is under 5 seconds (NFR2 compliance)

## Tasks / Subtasks

### Parallel Group A: High Confidence Selector (AC: #1)

- [x] Task A1: Create HighConfidenceSelector class
  - [x] A1.1 Define HighConfidenceSelector with threshold constant (80)
  - [x] A1.2 Create SelectionResult dataclass (selected, option, reason, confidence)
  - [x] A1.3 Implement should_auto_select() returning bool
  - [x] A1.4 Implement select_best_option() using menu context
  - [x] A1.5 Write tests for threshold boundary (79 vs 80 vs 81)

- [x] Task A2: Implement option scoring for high confidence
  - [x] A2.1 Create score_option() based on context alignment
  - [x] A2.2 Handle tie-breaking for equal scores
  - [x] A2.3 Write tests for option scoring scenarios

### Parallel Group B: Medium Confidence Selector (AC: #2)

- [x] Task B1: Create MediumConfidenceSelector class
  - [x] B1.1 Define MediumConfidenceSelector with thresholds (50, 79)
  - [x] B1.2 Create RecommendationResult dataclass (recommended_option, alternatives, reason)
  - [x] B1.3 Implement is_medium_confidence() returning bool
  - [x] B1.4 Implement get_recommendation() returning top option with reasoning
  - [x] B1.5 Write tests for threshold boundaries (49 vs 50, 79 vs 80)

- [x] Task B2: Implement recommendation logic
  - [x] B2.1 Create rank_options() to order by suitability
  - [x] B2.2 Generate recommendation_reason explaining why top option preferred
  - [x] B2.3 Write tests for recommendation scenarios

### Parallel Group C: Low Confidence Selector (AC: #3)

- [x] Task C1: Create LowConfidenceSelector class
  - [x] C1.1 Define LowConfidenceSelector with threshold (50)
  - [x] C1.2 Create PresentationResult dataclass (options, no_recommendation_reason)
  - [x] C1.3 Implement is_low_confidence() returning bool
  - [x] C1.4 Implement present_without_recommendation() returning all options equally
  - [x] C1.5 Write tests for low confidence scenarios

- [x] Task C2: Implement neutral presentation
  - [x] C2.1 Format options without bias indicators
  - [x] C2.2 Generate explanation for why no recommendation given
  - [x] C2.3 Write tests for presentation formatting

### Sequential: Selection Logger (AC: #4)

- [x] Task D1: Create SelectionLogger class
  - [x] D1.1 Define SelectionLogger with audit trail storage
  - [x] D1.2 Create SelectionLogEntry dataclass (timestamp, menu_type, selection, reason, confidence, duration_ms)
  - [x] D1.3 Implement log_selection() capturing all required fields
  - [x] D1.4 Implement get_audit_trail() for retrieval
  - [x] D1.5 Write tests for logging completeness

### Sequential: Performance Validation (AC: #5)

- [x] Task E1: Add timing instrumentation
  - [x] E1.1 Add start/end timestamps to selection flow
  - [x] E1.2 Implement performance_check() asserting < 5 seconds
  - [x] E1.3 Write performance tests with timing assertions

### Integration: MenuSelector Orchestrator

- [x] Task F1: Create MenuSelector that orchestrates all components
  - [x] F1.1 Implement select_or_present() routing to appropriate selector
  - [x] F1.2 Wire up logging for all selection paths
  - [x] F1.3 Write integration tests covering all confidence tiers

## Dev Notes

### Architecture Context

**Component:** Menu Participation Engine - Selection (extends Story 2b.1)
- **Tier:** 2-3 (Depends on Story 2b.1 Menu Detection)
- **Purpose:** Automatically select or recommend menu options based on confidence level
- **Integration:** Uses MenuDetectionResult from Story 2b.1 as input

**Confidence Tiers:**
```
High (>= 80%): Auto-select without user prompt
Medium (50-79%): Present with recommendation
Low (< 50%): Present without recommendation
```

**Selection Flow:**
```
MenuDetectionResult -> confidence_score -> route to appropriate selector
  -> HighConfidenceSelector.select_best_option() [auto]
  -> MediumConfidenceSelector.get_recommendation() [recommend]
  -> LowConfidenceSelector.present_without_recommendation() [neutral]
-> SelectionLogger.log_selection()
```

### Technical Requirements

**Language:** Python 3.11+
**Testing Framework:** pytest with TDD (Red-Green-Refactor)
**File Location:** `pcmrp_tools/bmad_automation/menu_selection.py`
**Test Location:** `tests/bmad_automation/test_menu_selection.py`

### Code Patterns to Follow

```python
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
import time

class ConfidenceTier(Enum):
    HIGH = "high"      # >= 80%
    MEDIUM = "medium"  # 50-79%
    LOW = "low"        # < 50%

@dataclass
class SelectionResult:
    selected: bool
    option: Optional[str] = None
    reason: str = ""
    confidence: int = 0
    tier: ConfidenceTier = ConfidenceTier.LOW

@dataclass
class SelectionLogEntry:
    timestamp: float
    menu_type: str
    selection: Optional[str]
    reason: str
    confidence: int
    duration_ms: int
    auto_selected: bool

CONFIDENCE_THRESHOLD_HIGH = 80
CONFIDENCE_THRESHOLD_MEDIUM = 50
MAX_SELECTION_TIME_MS = 5000
```

### Testing Standards

- **100% test coverage required**
- **TDD cycle:** Write failing test FIRST, then implementation
- **Test file naming:** `test_menu_selection.py`
- **Test function naming:** `test_<function>_<scenario>_<expected_result>`

### Edge Cases to Handle

1. Confidence exactly at threshold (50, 80)
2. All options have equal scores
3. Empty options list
4. Single option menu
5. Timing near 5-second limit
6. Menu type affects selection logic

### Dependencies

**Story 2b.1 Provides:**
- MenuDetectionResult with confidence score
- MenuType enum
- detect_menu() function

### References

- [Source: plans/2026-01-08-bmad-automation-design.md#Menu Participation Engine]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 2b.2]
- [Source: _bmad-output/planning-artifacts/epics.md#FR Coverage Map] - FR8, FR10

## Dev Agent Record

### Agent Model Used

- **Group A Implementation:** Claude Opus 4.5 (claude-opus-4-5-20251101)
- **Group B Implementation:** Claude Opus 4.5 (claude-opus-4-5-20251101)
- **Group C Implementation:** Claude Opus 4.5 (claude-opus-4-5-20251101)
- **Sequential D, E, F Implementation:** Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Group A: TDD workflow completed - 47 tests for HighConfidenceSelector (all passing)
- Group B: TDD workflow completed - 57 tests for MediumConfidenceSelector (all passing)
- Group C: TDD workflow completed - 58 tests for LowConfidenceSelector (all passing)
- Sequential D, E, F: TDD workflow completed - 49 tests for SelectionLogger, performance_check, MenuSelector (all passing)

### Completion Notes List

**Group A (HighConfidenceSelector) - COMPLETE:**
- Implemented CONFIDENCE_THRESHOLD_HIGH (80) constant
- Created SelectionResult dataclass with selected, option, reason, confidence fields
- Implemented HighConfidenceSelector class with:
  - should_auto_select(): returns True when confidence >= 80%
  - select_best_option(): auto-selects best option using context-aware scoring
  - score_option(): scores options 0-100 based on priority and context alignment
  - _get_priority_bonus(): high-priority words (continue, yes) get +20, negative (exit, cancel) get -10
  - _get_context_bonus(): expected_option +30, workflow_phase/action alignment +15
  - _generate_selection_reason(): human-readable explanation for auto-selection
- Tie-breaking uses original option order for equal scores (stable sort)
- Word-boundary matching prevents false positives ("unknown" does not match "no")
- 47 Group A tests covering threshold boundaries, option scoring, tie-breaking, and integration

**Group B (MediumConfidenceSelector) - COMPLETE:**
- Implemented CONFIDENCE_THRESHOLD_MEDIUM_LOW (50) and CONFIDENCE_THRESHOLD_MEDIUM_HIGH (79) constants
- Created RecommendationResult dataclass with recommended_option, alternatives, reason, confidence fields
- Implemented MediumConfidenceSelector class with:
  - is_medium_confidence(): boundary-aware threshold check (50 <= confidence <= 79)
  - rank_options(): priority-based option ranking with context awareness
  - get_recommendation(): full recommendation with reasoning
  - _generate_reason(): context-aware reason generation with menu type descriptions
- Context-specific priority adjustments for review, approve, explore actions
- 57 Group B tests covering threshold boundaries, ranking, recommendations, and integration

**Sequential Tasks D, E, F (Logger, Timing, Orchestrator) - COMPLETE:**
- Implemented MAX_SELECTION_TIME_MS (5000) constant for NFR2 compliance
- Created SelectionLogEntry dataclass with all required fields:
  - timestamp, menu_type, selection, reason, confidence, duration_ms, auto_selected
- Implemented SelectionLogger class with:
  - log_selection(): adds entry to audit trail
  - get_audit_trail(): returns copy of all logged entries
- Implemented performance_check() function:
  - Returns True if duration_ms < 5000
  - Enforces < 5 second NFR2 compliance
- Implemented MenuSelector orchestrator class with:
  - select_or_present(): routes to appropriate selector based on confidence tier
  - Timing instrumentation: tracks start/end time, calculates duration_ms
  - Logging: creates SelectionLogEntry for every selection path
  - Context passthrough: forwards context dict to selectors
- Confidence routing:
  - >= 80%: HighConfidenceSelector (auto_selected=True)
  - 50-79%: MediumConfidenceSelector (auto_selected=False)
  - < 50%: LowConfidenceSelector (auto_selected=False, selection=None)
- 49 new tests (all passing) covering:
  - SelectionLogEntry dataclass fields
  - SelectionLogger init, log_selection, get_audit_trail
  - performance_check boundary conditions
  - MenuSelector initialization and routing
  - Logging completeness across all tiers
  - Integration tests for full workflow

### File List

**Implementation:**
- `pcmrp_tools/bmad_automation/menu_selection.py` (931 lines, all groups complete)

**Tests:**
- `tests/bmad_automation/test_menu_selection.py` (211 tests total)
  - Group A (HighConfidenceSelector): 47 tests
  - Group B (MediumConfidenceSelector): 57 tests
  - Group C (LowConfidenceSelector): 58 tests
  - Sequential D, E, F (Logger, Timing, Orchestrator): 49 tests
