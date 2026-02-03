# Story 4.3: Graceful Degradation When Memory Unavailable

Status: done

## Story

As a **workflow automation system**,
I want **graceful degradation when Forgetful MCP is unavailable**,
So that **workflows continue functioning without failures, and memory operations queue for later processing**.

## Acceptance Criteria

1. **Given** Forgetful MCP is unreachable during session start
   **When** Context Pre-Loader attempts to query memories
   **Then** it returns `{memories: [], status: "degraded", reason: "forgetful_unavailable"}` and caches degraded status

2. **Given** Memory Bridge is in degraded mode
   **When** a query operation is requested
   **Then** it returns empty results (not exceptions) with `status: "degraded"`

3. **Given** Memory Bridge is in degraded mode
   **When** a save operation is requested
   **Then** it queues the save to a local file queue (up to 100 entries max, FIFO overflow)

4. **Given** the local save queue is full (100 entries)
   **When** a new save operation is requested
   **Then** it drops the oldest entry, logs the drop, and adds the new entry

5. **Given** Forgetful MCP becomes available during session
   **When** the periodic health check detects availability
   **Then** it processes the queued saves and clears degraded status

6. **Given** Forgetful MCP is unavailable
   **When** user starts a workflow
   **Then** they see a single warning: "Memory system unavailable. Patterns from previous sessions won't be loaded, and new patterns won't be saved until reconnection."

7. **Given** Forgetful MCP is unavailable for 30+ minutes
   **When** health checks continue
   **Then** check interval increases to every 30 minutes (reduced from every 5 minutes)

## Tasks / Subtasks

### Task 1: Create MemoryAvailabilityChecker Class (AC: #1, #5, #7)

- [x] Task 1.1: Define MemoryStatus enum (AVAILABLE, DEGRADED, PERMANENTLY_UNAVAILABLE)
- [x] Task 1.2: Create AvailabilityResult dataclass (status, reason, last_check, next_check_at)
- [x] Task 1.3: Define availability check constants:
  - [x] INITIAL_CHECK_INTERVAL_SECONDS = 300 (5 minutes)
  - [x] EXTENDED_CHECK_INTERVAL_SECONDS = 1800 (30 minutes)
  - [x] MAX_INITIAL_CHECKS = 6 (30 minutes at 5-minute intervals)
  - [x] MAX_RETRY_ATTEMPTS = 3
  - [x] RETRY_INTERVAL_MS = 100
- [x] Task 1.4: Implement check_availability() with 3x100ms retry logic
- [x] Task 1.5: Implement get_next_check_time() with interval escalation
- [x] Task 1.6: Implement should_check_now() based on cached status and time
- [x] Task 1.7: Write tests for all check scenarios and interval escalation

### Task 2: Create MemorySaveQueue Class (AC: #3, #4)

- [x] Task 2.1: Define QueuedMemory dataclass (memory_data, timestamp, retries)
- [x] Task 2.2: Define queue constants:
  - [x] MAX_QUEUE_SIZE = 100
  - [x] QUEUE_FILE_PATH = "_bmad-output/.memory-queue/{session-id}.json"
- [x] Task 2.3: Implement add_to_queue() with FIFO overflow handling
- [x] Task 2.4: Implement get_queue() returning all queued entries
- [x] Task 2.5: Implement clear_queue() for post-reconnection cleanup
- [x] Task 2.6: Implement persist_to_file() for queue durability
- [x] Task 2.7: Implement load_from_file() for session recovery
- [x] Task 2.8: Write tests for queue operations and overflow behavior

### Task 3: Implement Degraded Query Behavior (AC: #2)

- [x] Task 3.1: Create DegradedQueryResult dataclass (results=[], status="degraded", reason)
- [x] Task 3.2: Implement query_with_fallback() checking availability first
- [x] Task 3.3: Return empty DegradedQueryResult when unavailable
- [x] Task 3.4: Log degraded queries for debugging
- [x] Task 3.5: Write tests for degraded query scenarios

### Task 4: Implement User Notification (AC: #6)

- [x] Task 4.1: Create DegradedModeNotification message constant
- [x] Task 4.2: Implement notify_user_once() with session-level deduplication
- [x] Task 4.3: Track notification state in session context
- [x] Task 4.4: Write tests for notification deduplication

### Task 5: Implement Queue Processing on Recovery (AC: #5)

- [x] Task 5.1: Implement process_queued_saves() iterating through queue
- [x] Task 5.2: Handle partial failures (some saves succeed, some fail)
- [x] Task 5.3: Implement retry logic for failed saves
- [x] Task 5.4: Clear processed entries from queue
- [x] Task 5.5: Write tests for recovery scenarios

### Task 6: Integration with Memory Bridge (AC: All)

- [x] Task 6.1: Add MemoryAvailabilityChecker to MemoryBridge initialization
- [x] Task 6.2: Add MemorySaveQueue to MemoryBridge initialization
- [x] Task 6.3: Modify query operations to use query_with_fallback()
- [x] Task 6.4: Modify save operations to queue when degraded
- [x] Task 6.5: Add periodic health check trigger
- [x] Task 6.6: Write integration tests for full degradation flow

## Dev Notes

### Architecture Context

**Component:** Memory Bridge - Graceful Degradation (extends Stories 4.1, 4.2)
- **Tier:** 4 (Depends on Memory Bridge from Story 4.1)
- **Purpose:** Enable workflows to continue when Forgetful MCP is unavailable
- **Integration:** Wraps all Memory Bridge operations with availability checks

**Degradation Flow (from Architecture):**

```
SESSION START:
  → MemoryAvailabilityChecker.check_availability()
    → 3 retries, 100ms apart
    → If timeout after 300ms total: mark DEGRADED
  → If DEGRADED: notify_user_once()

QUERY OPERATION:
  IF status == DEGRADED:
    → Return DegradedQueryResult(results=[], status="degraded")
    → Log: "Memory query skipped: Forgetful unavailable"
  ELSE:
    → Execute normal Forgetful query

SAVE OPERATION:
  IF status == DEGRADED:
    → MemorySaveQueue.add_to_queue(memory_data)
    → IF queue full: drop oldest, log
    → Log: "Memory queued for later: {title}"
  ELSE:
    → Execute normal Forgetful save

PERIODIC HEALTH CHECK (every 5 min, escalating to 30 min):
  IF Forgetful available:
    → process_queued_saves()
    → Set status = AVAILABLE
    → Log: "Memory system restored, processed {count} queued saves"
```

**Interval Escalation (from Architecture):**

```
CHECK SCHEDULE:
  Attempts 1-6: Every 5 minutes (30 minutes total)
  Attempts 7+: Every 30 minutes
  After 4 hours: Mark PERMANENTLY_UNAVAILABLE, stop checks
```

### Technical Requirements

**Language:** Python 3.11+
**Testing Framework:** pytest with TDD (Red-Green-Refactor)
**File Location:** `pcmrp_tools/bmad_automation/memory_degradation.py`
**Test Location:** `tests/bmad_automation/test_memory_degradation.py`

### Code Patterns to Follow

```python
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
from datetime import datetime, timedelta
import json
from pathlib import Path

class MemoryStatus(Enum):
    AVAILABLE = "available"
    DEGRADED = "degraded"
    PERMANENTLY_UNAVAILABLE = "permanently_unavailable"

@dataclass
class AvailabilityResult:
    status: MemoryStatus
    reason: Optional[str] = None
    last_check: Optional[datetime] = None
    next_check_at: Optional[datetime] = None
    check_count: int = 0

@dataclass
class QueuedMemory:
    memory_data: dict
    timestamp: datetime
    retries: int = 0

@dataclass
class DegradedQueryResult:
    results: List = field(default_factory=list)
    status: str = "degraded"
    reason: str = "forgetful_unavailable"

# Constants (from Architecture Design)
MAX_QUEUE_SIZE = 100
INITIAL_CHECK_INTERVAL_SECONDS = 300      # 5 minutes
EXTENDED_CHECK_INTERVAL_SECONDS = 1800    # 30 minutes
MAX_INITIAL_CHECKS = 6                     # First 30 minutes
PERMANENT_UNAVAILABLE_HOURS = 4
MAX_RETRY_ATTEMPTS = 3
RETRY_INTERVAL_MS = 100

# User notification message
DEGRADED_MODE_NOTIFICATION = (
    "Memory system unavailable. Patterns from previous sessions won't be loaded, "
    "and new patterns won't be saved until reconnection."
)
```

### Testing Standards

- **100% test coverage required**
- **TDD cycle:** Write failing test FIRST, then implementation
- **Test file naming:** `test_memory_degradation.py`
- **Test function naming:** `test_<function>_<scenario>_<expected_result>`

### Edge Cases to Handle

1. Queue file doesn't exist on first run - create parent directory
2. Corrupt queue file - log error, start fresh
3. Forgetful becomes available mid-save - handle race condition
4. Session ends with items still in queue - persist to file
5. Multiple concurrent health checks - use mutex/lock
6. Recovery fails mid-processing - track which items processed
7. Check interval calculation at boundary (check 6 vs check 7)

### Dependencies

**Story 4.1 Provides:**
- MemoryBridge class for query/save operations
- Decision dataclass for memory creation

**Story 4.2 Provides:**
- PostWorkflowCurator for learning extraction
- Extractor classes that need degraded mode support

**This Story Provides (for downstream):**
- MemoryAvailabilityChecker for status checks
- MemorySaveQueue for queued operations
- DegradedQueryResult for consistent degraded responses
- Recovery logic for reconnection handling

### References

- [Source: plans/2026-01-08-bmad-automation-design.md#Graceful Degradation]
- [Source: plans/2026-01-08-bmad-automation-design.md#Forgetful MCP Unavailable]
- [Source: plans/2026-01-08-bmad-automation-design.md#Component Initialization and Shutdown Order]
- [Source: _bmad-output/implementation-artifacts/4-1-writing-workflow-decisions-to-memory.md]
- [Source: _bmad-output/implementation-artifacts/4-2-post-workflow-learning-extraction.md]

## Dev Agent Record

### Agent Model Used

claude-opus-4-5-20251101 (via parallel subagents)

### Debug Log References

- Agent aa7efb1: Tasks 1-2 (MemoryAvailabilityChecker, MemorySaveQueue)
- Agent a8bfca1: Tasks 3-4 (DegradedQuery, Notification)
- Agent a0a350c: Tasks 5-6 (Recovery, Integration)
- Agent a695af4: ADVERSARIAL Code Review

### Completion Notes List

- Task 1: Created MemoryStatus enum (AVAILABLE, DEGRADED, PERMANENTLY_UNAVAILABLE), AvailabilityResult dataclass, check constants, check_availability() with 3x100ms retry, interval escalation (5 min → 30 min after 6 checks)
- Task 2: Created QueuedMemory dataclass, MAX_QUEUE_SIZE=100, add_to_queue() with FIFO overflow logging, persist_to_file()/load_from_file() for durability
- Task 3: Created DegradedQueryResult dataclass, query_with_fallback() checking availability first, degraded query logging
- Task 4: Created DEGRADED_MODE_NOTIFICATION constant, notify_user_once() with session-level deduplication tracking
- Task 5: Implemented process_queued_saves() with partial failure handling, retry logic for failed saves, queue cleanup on success
- Task 6: Integrated MemoryAvailabilityChecker and MemorySaveQueue into MemoryBridge, periodic health check trigger

### File List

- `pcmrp_tools/bmad_automation/memory_degradation.py` (NEW)
- `pcmrp_tools/bmad_automation/memory_bridge.py` (MODIFIED - added degradation support)
- `tests/bmad_automation/test_memory_degradation.py` (NEW)

