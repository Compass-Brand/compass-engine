## Quality & Testing Specification

This section provides comprehensive quality engineering specifications addressing testing, quality gates, error handling, and implementation concerns identified during analysis.

### 1. Stakeholder Analysis

**Addresses:** PARTY-003 (CRITICAL)

#### Primary Stakeholders

| Stakeholder | Role | Usage Context | Success Criteria |
|-------------|------|---------------|------------------|
| Module Maintainer | Primary user | Iterating on existing modules | Fast, safe edits with validation |
| Module Developer | Content creator | Adding new components | Clear guidance, standard compliance |
| BMAD Administrator | System owner | Managing module ecosystem | Auditability, consistency |
| AI Agent (Claude) | Executor | Automated workflows | Unambiguous instructions, error recovery |

#### Usage Contexts

| Context | Frequency | Concurrency Risk | Priority |
|---------|-----------|------------------|----------|
| **Solo editing** | High (80%) | None | P0 |
| **Sequential multi-user** | Medium (15%) | Low - stale state | P1 |
| **Concurrent editing** | Low (5%) | High - race conditions | P1 |
| **Automated batch** | Rare (<1%) | Medium - resource contention | P2 |

#### Persona-Specific Requirements

**Module Maintainer (Primary)**
- Needs: Quick edits, preview changes, undo capability
- Pain points: Accidental overwrites, losing work, unclear validation errors
- Critical path: Select -> Edit -> Preview -> Confirm -> Save

**Module Developer (Secondary)**
- Needs: Add components, ensure compliance, understand structure
- Pain points: Learning curve, standard violations discovered late
- Critical path: Discover structure -> Add component -> Validate -> Integrate

**AI Agent (Execution)**
- Needs: Deterministic instructions, clear error states, recovery paths
- Pain points: Ambiguous menus, undefined behavior, state corruption
- Critical path: Load -> Execute step -> Handle error OR proceed -> Complete

---

### 2. Concurrency Handling & Locking Mechanism

**Addresses:** ISSUE-026 (MEDIUM), PARTY-003 (concurrency ignored)

#### Lock Architecture

```
+-------------------------------------------------------------+
|                    LOCK STRATEGY                            |
+-------------------------------------------------------------+
|  Level 1: Module-level lock (edit-module.lock)              |
|  Level 2: Component-level lock (component-name.lock)        |
|  Level 3: File-level lock (file-path.lock)                  |
+-------------------------------------------------------------+
```

#### Lock File Specification

**Location:** `{module_path}/.locks/`

**Format:** `{component-name}.lock`

```yaml
# Example: .locks/agent-analyst.lock
locked_by: "session_abc123"
locked_at: "2026-01-07T14:30:00Z"
expires_at: "2026-01-07T15:30:00Z"  # 1 hour TTL
lock_type: "exclusive"  # exclusive | shared
component_path: "agents/analyst.md"
operation: "edit"
```

#### Lock Acquisition Protocol

```
1. CHECK: Does lock file exist for target component?
   |-- NO  -> Create lock file, proceed with edit
   +-- YES -> Check expiration
              |-- EXPIRED -> Remove stale lock, acquire new lock
              +-- ACTIVE  -> Display lock holder, offer options:
                           [W] Wait and retry (30s intervals)
                           [F] Force acquire (requires CONFIRM)
                           [A] Abort operation
```

#### Lock Release Protocol

```
1. On successful save: Remove lock file immediately
2. On validation failure: Keep lock, allow retry
3. On user abort: Remove lock file
4. On session timeout: Lock expires via TTL
5. On error: Keep lock, log error, notify user
```

#### Stale Lock Detection

| Condition | Detection | Action |
|-----------|-----------|--------|
| Lock older than TTL | Check `expires_at` | Auto-remove, log warning |
| Orphaned lock (no session) | Session heartbeat missing | Auto-remove after 5 min |
| Process crash | PID check fails | Auto-remove, restore backup |

#### Force Acquire Safeguards

When user selects [F] Force acquire:
1. Display warning: "Another session may lose unsaved changes"
2. Require explicit confirmation: Type 'FORCE' to proceed
3. Create backup of current file state before acquiring
4. Log force acquisition with timestamp and user

---

### 3. Test Strategy

**Addresses:** PARTY-016 (CRITICAL - Zero test strategy), PARTY-019 (Backup integrity)

#### Test Pyramid

```
                    +----------+
                    |   E2E    |  5%  - Critical user journeys
                   -+----------+-
                  +--------------+
                  | Integration  |  25% - Component interactions
                 -+--------------+-
                +-----------------+
                |      Unit       |  70% - Core logic, edge cases
               -+-----------------+-
```

#### Unit Tests (70% coverage target)

| Component | Test Focus | Risk Category |
|-----------|------------|---------------|
| Lock acquisition | Race conditions, TTL expiry | TECH |
| Backup creation | File integrity, path handling | DATA |
| Validation logic | Edge cases, malformed input | BUS |
| Diff generation | Content comparison accuracy | TECH |
| Menu parsing | Input validation, option handling | BUS |

**Sample Unit Test Specifications:**

```markdown
## UT-LOCK-001: Lock Acquisition Success
Given no existing lock for component
When user initiates edit on component
Then lock file created with correct metadata
And lock file path matches expected pattern

## UT-LOCK-002: Lock Collision Detection
Given existing active lock from another session
When user initiates edit on same component
Then collision detected before any file modification
And user presented with Wait/Force/Abort options

## UT-BACKUP-001: Backup Creation Integrity
Given valid module file exists
When backup is created before edit
Then backup file byte-identical to original
And backup location follows naming convention
And backup metadata recorded

## UT-BACKUP-002: Backup Restoration
Given backup exists and edit fails validation
When user selects restore option
Then original file restored from backup
And backup integrity verified via checksum
And restoration logged with timestamp
```

#### Integration Tests (25% coverage target)

| Scenario | Components | Risk Category |
|----------|------------|---------------|
| Full edit cycle | Lock + Backup + Edit + Validate + Save | TECH |
| Multi-component edit | Lock coordination, state management | TECH |
| Git integration | Commit detection, changelog update | OPS |
| Validation pipeline | Multiple validators, error aggregation | BUS |

**Sample Integration Test Specifications:**

```markdown
## IT-CYCLE-001: Complete Edit Cycle
Given valid module with agent component
When user completes full edit cycle (select -> edit -> save)
Then lock acquired at start
And backup created before modification
And validation runs after edit
And lock released after successful save
And backup cleaned up on success

## IT-CONFLICT-001: Concurrent Edit Handling
Given two sessions targeting same component
When session B attempts edit while session A holds lock
Then session B receives conflict notification
And session A edit completes uninterrupted
And session B can proceed after session A releases lock
```

#### End-to-End Tests (5% coverage target)

| Journey | Description | Priority |
|---------|-------------|----------|
| Happy path edit | Load -> Select -> Edit -> Save | P0 |
| Multi-edit session | Multiple edits in single session | P0 |
| Error recovery | Edit -> Fail validation -> Fix -> Save | P1 |
| Concurrent blocking | Two users, one blocked | P1 |

#### Error Injection Tests

**Addresses:** PARTY-016 (comprehensive testing)

| Injection Point | Failure Mode | Expected Behavior |
|-----------------|--------------|-------------------|
| Lock file write | Disk full | Graceful error, no partial state |
| Backup creation | Permission denied | Halt edit, clear error message |
| File read | Corrupted content | Validation catches, suggests repair |
| Validation | Timeout | Retry with backoff, then fail safely |
| Git check | Git not available | Warning, allow proceed without git |

**Error Injection Test Specifications:**

```markdown
## EI-DISK-001: Disk Full During Lock Creation
Given disk quota exhausted
When workflow attempts to create lock file
Then operation fails gracefully with clear error
And no partial lock file left behind
And user advised on remediation

## EI-CORRUPT-001: Corrupted Module File
Given module.yaml with malformed YAML syntax
When workflow attempts to load module
Then parse error detected and reported
And specific line/position indicated if possible
And workflow offers validation-only mode to diagnose
```

#### Backup Integrity Testing

**Addresses:** PARTY-019 (Backup integrity untested)

| Test | Verification Method | Frequency |
|------|---------------------|-----------|
| Checksum validation | SHA-256 hash comparison | Every backup |
| Restore test | Byte-for-byte comparison | Sample 10% |
| Corruption detection | Intentionally corrupt, verify detection | Integration |
| Edge case files | Unicode, large files, special chars | Unit suite |

---

### 4. Quality Gates & Metrics

**Addresses:** PARTY-018 (HIGH - No quality gate or metrics defined)

#### Gate Definitions

| Gate | Trigger | Required Conditions | Blocking |
|------|---------|---------------------|----------|
| **Pre-edit Gate** | Before any modification | Lock acquired, backup created, validation baseline | YES |
| **Post-edit Gate** | After each edit | Syntax valid, structure intact | YES |
| **Session Gate** | Before session close | All edits validated, user confirmed | YES |
| **Compliance Gate** | Optional user request | Full BMAD compliance check | NO |

#### Quality Metrics

| Metric | Target | Measurement | Alert Threshold |
|--------|--------|-------------|-----------------|
| Edit success rate | >95% | Successful saves / total attempts | <90% |
| Validation pass rate | >90% | First-time validation passes | <80% |
| Backup restore success | 100% | Successful restores / attempts | <100% |
| Lock conflict rate | <5% | Conflicts / total sessions | >10% |
| Session completion rate | >85% | Completed / started sessions | <75% |

#### Gate Status Format

```yaml
gate_status:
  pre_edit:
    status: PASS | FAIL | SKIP
    timestamp: "2026-01-07T14:30:00Z"
    checks:
      lock_acquired: true
      backup_created: true
      validation_baseline: true
  post_edit:
    status: PASS | FAIL
    timestamp: "2026-01-07T14:35:00Z"
    validation_errors: []
  session:
    status: PASS | FAIL | INCOMPLETE
    timestamp: "2026-01-07T15:00:00Z"
    edits_completed: 3
    edits_failed: 0
    user_confirmed: true
```

#### Quality Gate Decision Matrix

| Pre-edit | Post-edit | User Confirm | Gate Decision |
|----------|-----------|--------------|---------------|
| PASS | PASS | YES | **PASS** - Complete session |
| PASS | PASS | NO | **INCOMPLETE** - Pending confirmation |
| PASS | FAIL | - | **FAIL** - Validation errors |
| FAIL | - | - | **BLOCKED** - Cannot proceed |

---

### 5. Error State Definitions & Recovery Paths

**Addresses:** PARTY-005 (HIGH - No error state handling)

#### Error State Taxonomy

| Error Code | Category | Severity | Description |
|------------|----------|----------|-------------|
| E001 | LOCK | BLOCKING | Cannot acquire lock |
| E002 | LOCK | WARNING | Lock about to expire |
| E003 | BACKUP | BLOCKING | Backup creation failed |
| E004 | BACKUP | WARNING | Backup integrity check failed |
| E005 | VALIDATION | BLOCKING | Syntax error in edited content |
| E006 | VALIDATION | WARNING | Non-critical compliance issue |
| E007 | FILE | BLOCKING | File not found or inaccessible |
| E008 | FILE | BLOCKING | Permission denied |
| E009 | GIT | WARNING | Git operation failed |
| E010 | STATE | BLOCKING | Inconsistent state detected |

#### Recovery Paths by Error Type

**E001: Lock Acquisition Failed**
```
Recovery Path:
1. Check if lock held by current session (reentrant)
   |-- YES -> Reuse existing lock, proceed
   +-- NO  -> Continue to step 2
2. Check if lock expired
   |-- YES -> Remove stale lock, retry acquisition
   +-- NO  -> Continue to step 3
3. Present user options:
   [W] Wait 30 seconds, retry automatically
   [F] Force acquire (with confirmation)
   [A] Abort and exit

Escalation: If 3 retries fail, escalate to E010
```

**E003: Backup Creation Failed**
```
Recovery Path:
1. Diagnose failure reason:
   |-- Disk space -> "Insufficient disk space. Free {X}MB and retry"
   |-- Permission -> "Cannot write to backup location"
   +-- Path issue -> "Backup path invalid: {path}"
2. Offer remediation:
   [R] Retry after user fixes issue
   [S] Skip backup (requires CONFIRM - "SKIP_BACKUP")
   [A] Abort edit

WARNING: Proceeding without backup risks data loss
```

**E005: Validation Error**
```
Recovery Path:
1. Display validation errors with context:
   "Line 42: Invalid YAML syntax - unexpected '}'"
2. Offer options:
   [E] Re-edit the content (return to edit mode)
   [V] View full validation report
   [R] Restore from backup
   [F] Force save anyway (requires CONFIRM - "FORCE_SAVE")

NOTE: Force save may create non-compliant module
```

**E010: Inconsistent State**
```
Recovery Path:
1. Halt all operations immediately
2. Create emergency backup of current state
3. Log full state dump for diagnosis
4. Present recovery options:
   [D] Diagnose - show state inconsistency details
   [R] Restore - revert to last known good state
   [M] Manual - exit to allow manual intervention
   [C] Continue - attempt to reconcile state (advanced)

CRITICAL: Do not proceed without explicit user direction
```

---

### 6. Version Control Integration

**Addresses:** ISSUE-010 (MEDIUM - No version control integration details)

#### Git Integration Points

| Operation | Git Action | Timing | Behavior |
|-----------|------------|--------|----------|
| Session start | Check status | Pre-edit | Warn if uncommitted changes |
| After save | Stage changes | Post-save | Auto-stage edited files |
| Session end | Suggest commit | Post-session | Offer commit with message |
| Changelog update | Include in stage | With save | Always stage changelog |

#### Git Pre-flight Check

```
1. Verify git repository exists
   |-- NO  -> Warning: "Module not in git repository"
   +-- YES -> Continue
2. Check for uncommitted changes in module
   |-- YES -> Warning: "Uncommitted changes detected:"
   |         [files list]
   |         Options: [C] Commit first  [P] Proceed anyway  [A] Abort
   +-- NO  -> Proceed
3. Check branch status
   +-- Inform user: "Current branch: {branch_name}"
```

#### Auto-generated Commit Message Format

```
edit-module: {operation} {component_type} in {module_name}

{summary_of_changes}

Components modified:
- {component_1}: {change_description}

Session: {session_id}
Validated: {validation_status}
```

#### Branch Protection Awareness

| Branch Type | Behavior |
|-------------|----------|
| Main/Master | Warning: "You are editing on protected branch" |
| Feature branch | Normal operation |
| Detached HEAD | Warning: "Not on a branch. Changes may be lost." |

---

### 7. Changelog Format Specification

**Addresses:** ISSUE-020 (LOW - Changelog format unspecified)

#### Changelog File Location

```
{module_path}/CHANGELOG.md
```

#### Changelog Entry Format

```markdown
## [{version}] - {date}

### {change_type}

- **{component_path}**: {change_description}
  - Detail 1
  - Session: `{session_id}`
```

#### Change Types (Keep a Changelog standard)

| Type | Usage |
|------|-------|
| Added | New agents, workflows, or components |
| Changed | Modifications to existing components |
| Deprecated | Components marked for future removal |
| Removed | Deleted components |
| Fixed | Bug fixes or corrections |
| Security | Security-related changes |

#### Example Changelog Entry

```markdown
## [1.2.0] - 2026-01-07

### Changed

- **agents/analyst.md**: Enhanced data analysis capabilities
  - Added support for CSV parsing
  - Session: `edit_abc123`

### Added

- **agents/data-engineer.md**: New agent for ETL workflows
  - Session: `edit_def456`
```

#### Changelog Generation Rules

1. **Auto-generate** entry when edit session completes successfully
2. **Version bump**:
   - Patch (0.0.X) for fixes and minor changes
   - Minor (0.X.0) for new components or features
   - Major (X.0.0) for breaking changes (user must confirm)
3. **Consolidate** multiple edits in same session under single entry
4. **Preserve** existing changelog content (append, don't overwrite)

---

### 8. Confirmation Mechanism Design

**Addresses:** PARTY-002 (MEDIUM - Confirmation mechanism missing)

#### Confirmation Levels

| Level | Trigger | Mechanism | Example |
|-------|---------|-----------|---------|
| **Implicit** | Low-risk, reversible | Single keypress | Select menu option |
| **Explicit** | Moderate risk | Y/N prompt | Save changes |
| **Strong** | High risk, irreversible | Type specific word | Delete component |
| **Double** | Critical operations | Two-step confirmation | Force overwrite |

#### Operation-to-Confirmation Mapping

| Operation | Confirmation Level | Required Input |
|-----------|-------------------|----------------|
| Select item | Implicit | Menu number |
| Edit content | Implicit | (inline editing) |
| Save changes | Explicit | Y/n |
| Cancel edit | Explicit | Y/n |
| Delete component | Strong | Type 'DELETE' |
| Force acquire lock | Double | Type 'FORCE' + Y/n |
| Skip backup | Strong | Type 'SKIP_BACKUP' |
| Force save (invalid) | Double | Type 'FORCE_SAVE' + Y/n |
| Restore from backup | Explicit | Y/n |

#### Timeout Behavior

| Context | Timeout | Default Action |
|---------|---------|----------------|
| Implicit confirmation | None | Wait for input |
| Explicit confirmation | 5 minutes | Prompt reminder, then abort |
| Strong confirmation | 2 minutes | Abort, release locks |
| Double confirmation | 1 minute per step | Abort, release locks |

---

### 9. Diff Preview Feature Design

**Addresses:** ISSUE-029 (HIGH - Add diff preview improvement)

#### Diff Display Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Inline** | Side-by-side in terminal | Quick review |
| **Unified** | Standard diff format | Git-compatible |
| **Semantic** | Structured comparison | YAML/Markdown aware |
| **Summary** | High-level overview | Large changes |

#### Diff Preview Interface

```
+-------------------------------------------------------------+
|  DIFF PREVIEW: agents/analyst.md                            |
+-------------------------------------------------------------+
|  View: [I]nline  [U]nified  [S]emantic  [M]summary          |
+-------------------------------------------------------------+
|                                                             |
|  --- Original (backed up)                                   |
|  +++ Modified                                               |
|                                                             |
|  @@ -15,7 +15,9 @@ persona:                                  |
|     communication_style: Professional                       |
|  -  expertise: Data analysis                                |
|  +  expertise: Advanced data analysis and visualization     |
|  +  skills:                                                 |
|  +    - csv_parsing                                         |
|                                                             |
|  Summary: 2 additions, 1 modification, 0 deletions          |
|                                                             |
+-------------------------------------------------------------+
|  [A]pply  [E]dit more  [R]evert  [?] Help                   |
+-------------------------------------------------------------+
```

#### Semantic Diff for Structured Content

For YAML and Markdown files, provide structure-aware diff:

```
YAML STRUCTURE DIFF: module.yaml

[UNCHANGED] name: my-module
[MODIFIED]  description:
            - OLD: "A simple module"
            + NEW: "A comprehensive module for data workflows"
[ADDED]     dependencies:
            + pandas: ">=2.0.0"
```

#### Integration Points

| Trigger | Diff Shown | Actions Available |
|---------|------------|-------------------|
| After edit, before save | Auto-display | Apply, Edit more, Revert |
| User requests preview | On-demand | View only |
| Before session close | Summary of all changes | Review, Commit, Abort |

---

### 10. Component Duplication Feature Design

**Addresses:** ISSUE-030 (HIGH - Add component duplication improvement)

#### Duplication Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Clone** | Exact copy with new name | Creating variant of existing |
| **Template** | Structure only, content cleared | Starting point for new |
| **Derive** | Copy with `derived_from` reference | Extending existing |

#### Duplication Interface

```
DUPLICATE COMPONENT
-------------------

Source: agents/analyst.md

Duplication type:
[C] Clone    - Exact copy with new name
[T] Template - Keep structure, clear content
[D] Derive   - Copy with derivation reference

Select type: C

New component name: data-engineer

Creating: agents/data-engineer.md
```

#### Clone Transformation Rules

| Field Type | Clone | Template | Derive |
|------------|-------|----------|--------|
| `name` | Replace with new | Replace with new | Replace with new |
| `description` | Copy as-is | Clear (placeholder) | Copy as-is |
| `content` | Copy as-is | Clear (placeholder) | Copy as-is |
| `created_at` | Current timestamp | Current timestamp | Current timestamp |
| `derived_from` | Not added | Not added | Set to source name |
| `version` | Reset to 1.0.0 | Reset to 1.0.0 | Reset to 1.0.0 |

#### Conflict Resolution

```
Target already exists: agents/data-engineer.md

Options:
[O] Overwrite existing (requires confirmation)
[R] Rename to data-engineer-2.md
[M] Merge with existing (advanced)
[A] Abort duplication
```

---

### 11. Story Decomposition for Implementation

**Addresses:** PARTY-014 (HIGH - No story decomposition)

#### Epic Overview

| Epic | Stories | Points | Focus |
|------|---------|--------|-------|
| Epic 1: Foundation & Safety | 3 | 8 | Lock, backup, error handling |
| Epic 2: Core Editing | 3 | 11 | Load, edit, diff preview |
| Epic 3: Validation & Compliance | 2 | 5 | Real-time, BMAD check |
| Epic 4: Persistence & Integration | 3 | 8 | Save, git, duplication |
| **Total** | **11** | **32** | |

#### Epic 1: Foundation & Safety

**Story 1.1: Lock Management System** (3 points)

As a module maintainer, I want concurrent edit protection via file locking.

Acceptance Criteria:
- Given no existing lock, When I start editing, Then lock is acquired
- Given active lock from another session, When I attempt edit, Then I see conflict options
- Given lock older than TTL, When I attempt edit, Then stale lock is removed

Tasks:
- [ ] Implement lock file creation/removal
- [ ] Implement lock collision detection
- [ ] Implement stale lock cleanup
- [ ] Implement force acquire with confirmation
- [ ] Write unit tests for lock operations

---

**Story 1.2: Backup System** (2 points)

As a module maintainer, I want automatic backups before edits.

Acceptance Criteria:
- Given I start editing, When backup created, Then backup is byte-identical to original
- Given edit fails, When I choose restore, Then original is restored from backup
- Given edit succeeds, When session completes, Then backup is cleaned up

Tasks:
- [ ] Implement backup creation with checksum
- [ ] Implement backup restoration
- [ ] Implement backup cleanup on success
- [ ] Implement backup integrity verification
- [ ] Write unit tests for backup operations

---

**Story 1.3: Error State Machine** (3 points)

As an AI agent, I want clear error states and recovery paths.

Acceptance Criteria:
- Given any error occurs, When detected, Then specific error code assigned
- Given recoverable error, When recovery path followed, Then workflow continues
- Given blocking error, When user provides input, Then appropriate action taken

Tasks:
- [ ] Define error taxonomy (E001-E010)
- [ ] Implement error state machine
- [ ] Implement recovery paths for each error type
- [ ] Implement error logging and reporting
- [ ] Write unit tests for error handling

---

#### Epic 2: Core Editing

**Story 2.1: Module Loading & Structure Analysis** (3 points)

As a module maintainer, I want to see the module structure clearly.

Acceptance Criteria:
- Given valid module path, When I load module, Then structure displayed in menu
- Given invalid path, When I attempt load, Then clear error with suggestions
- Given module with many components, When displayed, Then grouped by type

Tasks:
- [ ] Implement module discovery
- [ ] Implement structure analysis
- [ ] Implement hierarchical menu generation
- [ ] Implement path validation
- [ ] Write integration tests

---

**Story 2.2: Component Editing Interface** (5 points)

As a module maintainer, I want intuitive editing of components.

Acceptance Criteria:
- Given I select a component, When editing, Then appropriate interface shown
- Given YAML component, When editing, Then syntax validation provided
- Given Markdown component, When editing, Then structure preserved

Tasks:
- [ ] Implement component type detection
- [ ] Implement edit mode for YAML files
- [ ] Implement edit mode for Markdown files
- [ ] Implement focused section editing
- [ ] Write integration tests

---

**Story 2.3: Diff Preview System** (3 points)

As a module maintainer, I want to preview changes before saving.

Acceptance Criteria:
- Given I made changes, When I request preview, Then diff displayed
- Given YAML changes, When previewing, Then semantic diff available
- Given multiple view modes, When I switch, Then display updates

Tasks:
- [ ] Implement unified diff generation
- [ ] Implement inline diff display
- [ ] Implement semantic diff for YAML
- [ ] Implement diff summary statistics
- [ ] Write unit tests for diff generation

---

#### Epic 3: Validation & Compliance

**Story 3.1: Real-time Validation** (3 points)

As a module maintainer, I want immediate feedback on errors.

Acceptance Criteria:
- Given I edit content, When syntax invalid, Then error highlighted
- Given YAML file, When malformed, Then specific line/error indicated
- Given validation passes, When complete, Then success confirmed

Tasks:
- [ ] Implement YAML syntax validation
- [ ] Implement Markdown structure validation
- [ ] Implement real-time validation feedback
- [ ] Implement validation error formatting
- [ ] Write unit tests for validation

---

**Story 3.2: BMAD Compliance Check Integration** (2 points)

As a module maintainer, I want optional deep compliance checking.

Acceptance Criteria:
- Given I request compliance check, When run, Then full report generated
- Given violations found, When displayed, Then severity and fixes shown
- Given module passes, When complete, Then compliance status updated

Tasks:
- [ ] Integrate with workflow-compliance-check
- [ ] Implement compliance report display
- [ ] Implement fix suggestion formatting
- [ ] Write integration tests

---

#### Epic 4: Persistence & Integration

**Story 4.1: Save with Changelog** (2 points)

As a module maintainer, I want automatic changelog updates.

Acceptance Criteria:
- Given I save changes, When successful, Then changelog entry created
- Given multiple edits, When session ends, Then consolidated entry
- Given changelog exists, When updated, Then existing content preserved

Tasks:
- [ ] Implement changelog entry generation
- [ ] Implement changelog file update
- [ ] Implement session consolidation
- [ ] Implement version bump logic
- [ ] Write unit tests for changelog

---

**Story 4.2: Git Integration** (3 points)

As a module maintainer, I want git-aware editing.

Acceptance Criteria:
- Given uncommitted changes, When I start edit, Then warning displayed
- Given I save changes, When successful, Then files staged
- Given session ends, When I choose commit, Then commit created

Tasks:
- [ ] Implement git status check
- [ ] Implement auto-staging
- [ ] Implement commit message generation
- [ ] Implement branch awareness
- [ ] Write integration tests

---

**Story 4.3: Component Duplication** (3 points)

As a module maintainer, I want to duplicate existing components.

Acceptance Criteria:
- Given I select duplicate, When I choose type, Then appropriate copy created
- Given Clone type, When created, Then exact copy with new name
- Given name conflict, When detected, Then resolution options shown

Tasks:
- [ ] Implement clone duplication
- [ ] Implement template duplication
- [ ] Implement derive duplication
- [ ] Implement conflict resolution
- [ ] Write unit tests for duplication

---

#### Suggested Sprint Allocation

| Sprint | Stories | Points | Focus |
|--------|---------|--------|-------|
| Sprint 1 | 1.1, 1.2, 1.3 | 8 | Safety foundation |
| Sprint 2 | 2.1, 2.2 | 8 | Core editing |
| Sprint 3 | 2.3, 3.1, 3.2 | 8 | Preview & validation |
| Sprint 4 | 4.1, 4.2, 4.3 | 8 | Integration & polish |

---

### 12. File System Edge Case Handling

**Addresses:** PARTY-006 (MEDIUM - File system edge cases ignored)

#### Edge Case Taxonomy

| Category | Edge Case | Risk | Mitigation |
|----------|-----------|------|------------|
| **Path** | Unicode in path | File not found | Normalize to UTF-8 |
| **Path** | Spaces in path | Command failures | Quote all paths |
| **Path** | Long path (>260 chars) | Access failure | Detect and warn |
| **Path** | Symlinks | Unexpected behavior | Resolve, warn user |
| **Content** | Empty file | Parse errors | Handle as valid |
| **Content** | Binary in text file | Corruption | Detect, reject |
| **Content** | Large file (>10MB) | Memory issues | Stream, warn |
| **Content** | BOM | Parse issues | Detect and strip |
| **Encoding** | Non-UTF-8 | Mojibake | Detect, convert |
| **Permissions** | Read-only file | Save failure | Check before edit |
| **Permissions** | OS lock | Access failure | Detect, report |
| **State** | File deleted | Data loss | Monitor, warn |
| **State** | External modify | Conflict | Detect, offer merge |

#### Path Handling Rules

```python
def normalize_path(path):
    # 1. Expand user home (~)
    path = expand_user(path)
    # 2. Resolve to absolute path
    path = resolve_absolute(path)
    # 3. Normalize separators
    path = normalize_separators(path)
    # 4. Unicode normalization (NFC)
    path = unicode_normalize_nfc(path)
    # 5. Check path length
    if len(path) > 260 and is_windows():
        warn("Path exceeds Windows limit")
    # 6. Resolve symlinks
    if is_symlink(path):
        path = resolve_symlink(path)
    return path
```

#### External Modification Detection

```
At edit start:
1. Record file hash (SHA-256)
2. Record file mtime

Before save:
1. Re-check file hash and mtime
2. If changed:
   +-----------------------------------------------+
   | WARNING: File modified externally             |
   |                                               |
   | Options:                                      |
   | [D] Show diff between versions                |
   | [O] Overwrite (external changes lost)         |
   | [M] Merge changes                             |
   | [R] Reload file (your changes lost)           |
   | [A] Abort                                     |
   +-----------------------------------------------+
```

#### Permission Handling

| Scenario | Detection | Response |
|----------|-----------|----------|
| Read-only file | `stat()` check | "File is read-only" |
| Directory not writable | `access()` check | "Cannot write to directory" |
| File locked | Platform check | "File locked by {process}" |
| Insufficient perms | Exception | "Permission denied" |

---

### Quality Assurance Summary

| Issue ID | Severity | Status | Section |
|----------|----------|--------|---------|
| PARTY-003 | CRITICAL | ADDRESSED | 1. Stakeholder Analysis |
| PARTY-016 | CRITICAL | ADDRESSED | 3. Test Strategy |
| ISSUE-029 | HIGH | ADDRESSED | 9. Diff Preview Feature |
| ISSUE-030 | HIGH | ADDRESSED | 10. Component Duplication |
| PARTY-014 | HIGH | ADDRESSED | 11. Story Decomposition |
| PARTY-005 | HIGH | ADDRESSED | 5. Error State Definitions |
| PARTY-018 | HIGH | ADDRESSED | 4. Quality Gates & Metrics |
| ISSUE-026 | MEDIUM | ADDRESSED | 2. Concurrency Handling |
| ISSUE-010 | MEDIUM | ADDRESSED | 6. Version Control Integration |
| PARTY-002 | MEDIUM | ADDRESSED | 8. Confirmation Mechanism |
| PARTY-006 | MEDIUM | ADDRESSED | 12. File System Edge Cases |
| PARTY-019 | MEDIUM | ADDRESSED | 3. Test Strategy (Backup) |
| ISSUE-020 | LOW | ADDRESSED | 7. Changelog Format |

---

### Implementation Readiness Checklist

- [x] Stakeholder analysis complete with personas
- [x] Concurrency model defined with lock specification
- [x] Test strategy covering unit, integration, E2E, error injection
- [x] Quality gates defined with metrics and thresholds
- [x] Error states enumerated with recovery paths
- [x] Version control integration specified
- [x] Changelog format standardized
- [x] Confirmation mechanisms designed by risk level
- [x] Diff preview feature fully specified
- [x] Component duplication feature designed
- [x] Stories decomposed into implementable units (32 points)
- [x] File system edge cases documented with mitigations

**Status:** Ready for implementation planning and sprint allocation.

---

*Quality & Testing Specification completed: 2026-01-07*
*Total issues addressed: 13 (2 CRITICAL, 6 HIGH, 4 MEDIUM, 1 LOW)*
