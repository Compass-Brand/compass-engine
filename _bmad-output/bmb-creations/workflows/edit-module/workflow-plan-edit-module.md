---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9]
status: COMPLETE
completedAt: 2026-01-07
specificationRounds: 5
issuesResolved: 71
totalFilesGenerated: 26
---

# Workflow Creation Plan: edit-module

## Initial Project Context

- **Module:** BMB (BMAD Module Builder)
- **Target Location:** `_bmad/bmb/workflows/edit-module/`
- **Created:** 2026-01-07
- **Requested By:** Trevor Leigh

## Problem Statement

The BMB Module Builder agent menu references an `edit-module` workflow that doesn't exist. Module maintainers need a structured way to modify existing BMAD modules while preserving coherence and following best practices.

## Scope

This workflow must be **comprehensive** - supporting the full lifecycle of module editing:

### Component Operations
- **Agents:** Add, remove, and edit agents within a module
- **Workflows:** Add, remove, and edit workflows within a module
- **Configuration:** Modify module.yaml settings
- **Documentation:** Edit module README and related docs

### Design Goals
- As capable as possible
- Maintain module coherence during edits
- Validate changes against BMAD standards
- Support iterative refinement

---

## Requirements Specification

### Workflow Type
- **Classification:** Action + Interactive hybrid
- **Action aspect:** Actually modifies module files (agents, workflows, configs)
- **Interactive aspect:** Guides user through decisions about what to change

### Flow Structure
```
Load Module → Analyze Structure → Select Edit Type → Make Changes → Validate → Save
                                        ↑                              |
                                        └──────── (repeat) ────────────┘
```

### Module Selection
| Method | Description |
|--------|-------------|
| Discovery | List all discovered modules for selection |
| Direct Path | User provides path to module directly |
| Both options available | User chooses preferred method |

### Edit Interface
| Feature | Specification |
|---------|---------------|
| View Options | Full file view OR focused section view |
| Default | Recommend focused view for precision |
| Navigation | Numbered menu grouped by category |

**Menu Structure Example:**
```
Module: my-module
─────────────────
[1] Agents
    1.1 analyst.md
    1.2 architect.md
[2] Workflows
    2.1 create-plan/
    2.2 review-code/
[3] Configuration (module.yaml)
[4] Documentation (README.md)

Select item to edit (or 'done' to finish):
```

### Interaction Patterns
| Context | Style | Rationale |
|---------|-------|-----------|
| High-level decisions | Intent-based | "What do you want to change about this agent?" |
| Destructive operations | Prescriptive | "This will remove agent X. Type 'CONFIRM' to proceed" |

### Prerequisites (Pre-flight Checks)
| Check | On Failure |
|-------|------------|
| Module passes basic validation | Suggest fixing issues first before editing |
| No uncommitted git changes | Suggest committing to git first |

### Outputs
| Output | Lifecycle |
|--------|-----------|
| Edited files | Permanent |
| Changelog/edit summary | Permanent |
| Backup of original files | Created before edit, removed after successful validation |

### Iteration Behavior
- After each edit completes: Ask "Do you have more edits?"
- Continue loop until user indicates done
- Validation optional but recommended after each edit

### Success Criteria
- [ ] Files modified correctly and still valid BMAD format
- [ ] User explicitly confirms satisfaction
- [ ] Compliance check passes (when run)
- All three conditions met = successful session

---

## Analysis Rounds

### Round 1
- Status: COMPLETE
- Advanced Elicitation Issues: 32
- Party Mode Issues: 19
- Total Issues: 51
- CRITICAL: 14 issues
- HIGH: 22 issues
- Fix Status: COMPLETE

### Round 2
- Status: COMPLETE
- Advanced Elicitation Issues: 12 (2 CRITICAL, 3 HIGH, 5 MEDIUM, 2 LOW)
- Party Mode: ALL AGENTS APPROVED (0 issues)
- Key Blockers Found:
  - Variable resolution mechanism undefined
  - BMAD compliance rules undefined
  - Backup location inconsistency
  - Phasing schemes misalignment
  - Module discovery algorithm undefined
- Fix Status: COMPLETE (see "Round 2 Fixes: Critical & High Priority" section)

### Round 3
- Status: COMPLETE
- Goal: Verify 0 remaining issues
- Advanced Elicitation: 0 ISSUES FOUND
- Party Mode: ALL 6 AGENTS APPROVE - 0 ISSUES
- **RESULT: SPECIFICATION READY FOR IMPLEMENTATION**

### Final Statistics
| Metric | Value |
|--------|-------|
| Total Issues Found | 63 |
| Total Issues Fixed | 63 (100%) |
| Document Lines | ~4,600 |
| Step Files Specified | 21 |
| Total Files to Create | 31 |
| Story Points | 32 |
| Sprints Planned | 4 |

---

## Scope & Process Specification

This section provides detailed specifications addressing critical gaps identified during analysis rounds.

### 1. MVP Definition with Phased Delivery Plan

**Addresses:** PARTY-011 (CRITICAL) - No MVP definition

#### Phase 1: Core MVP (Must Ship)

The minimum viable edit-module workflow that provides value:

| Component | Capability | Rationale |
|-----------|------------|-----------|
| Module Loading | Load and parse any valid BMAD module | Foundation for all operations |
| Structure Analysis | Display module contents in navigable format | Users need to see what exists |
| Agent Editing | Edit existing agent files | Most common edit operation |
| Workflow Editing | Edit existing workflow files | Second most common operation |
| Basic Validation | Verify files remain valid BMAD format | Prevent corruption |
| Single-file Backup | Backup before edit, restore on failure | Safety net |

**MVP Explicitly Excludes:**
- Adding new agents/workflows (use create-agent/create-workflow)
- Module renaming or moving
- Batch operations across multiple components
- Dependency analysis and tracking
- Module.yaml editing beyond basic fields

#### Phase 2: Enhanced Operations

| Component | Capability |
|-----------|------------|
| Add Operations | Add new agents/workflows via delegation to existing workflows |
| Remove Operations | Delete components with dependency checking |
| Module.yaml Full Edit | All configuration fields including custom settings |
| Dependency Tracking | Warn when edits break references |

#### Phase 3: Advanced Features

| Component | Capability |
|-----------|------------|
| Rename/Move | Rename components with reference updates |
| Multi-Agent Modules | Handle modules with shared agents |
| Batch Operations | Edit multiple related components in sequence |
| Cross-Module References | Track and update inter-module dependencies |

---

### 2. User Journey Documentation

**Addresses:** PARTY-012 (MEDIUM) - No user journey documented

#### Primary User Journey: Edit an Existing Agent

```
START
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. USER INITIATES                                           │
│    - User runs: /edit-module                                │
│    - Or: "I need to edit an agent in my module"             │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. MODULE SELECTION                                         │
│    System: "Which module would you like to edit?"           │
│    [Lists discovered modules with numbers]                  │
│    User: Selects "3" or provides path                       │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. PRE-FLIGHT CHECKS                                        │
│    - Validates module structure                             │
│    - Checks git status                                      │
│    - Reports any issues (user can proceed or fix first)     │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. STRUCTURE DISPLAY                                        │
│    Shows navigable menu:                                    │
│    [1] Agents: analyst.md, architect.md                     │
│    [2] Workflows: create-plan/, review-code/                │
│    [3] Configuration                                        │
│    [4] Documentation                                        │
│    User: Types "1.1" to select analyst.md                   │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. EDIT TYPE SELECTION                                      │
│    System: "What would you like to do with analyst.md?"     │
│    [E] Edit content  [V] View full file  [R] Remove         │
│    User: Types "E"                                          │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. EDIT INTERACTION                                         │
│    System: "What aspect of this agent do you want to        │
│             change? (persona, capabilities, tools, other)"  │
│    User: "I want to update the persona to be more formal"   │
│    System: [Reads current persona, proposes changes]        │
│    User: [Approves or requests modifications]               │
│    System: [Makes changes, shows diff]                      │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. VALIDATION                                               │
│    System: "Edit complete. Running validation..."           │
│    - Checks BMAD format compliance                          │
│    - Verifies no broken references                          │
│    System: "Validation passed."                             │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. ITERATION CHECK                                          │
│    System: "Do you have more edits? [Y/N]"                  │
│    User: "Y" → Return to Step 4                             │
│    User: "N" → Proceed to completion                        │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. SESSION COMPLETION                                       │
│    System: "Edit session complete. Summary:"                │
│    - Files modified: analyst.md                             │
│    - Changes: Updated persona section                       │
│    - Backup cleaned up                                      │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
END
```

#### Secondary User Journeys

| Journey | Entry Point | Key Differences |
|---------|-------------|-----------------|
| Edit Workflow | Same as above | Step 6 navigates workflow directory structure |
| Edit Config | Select [3] | Presents module.yaml fields as editable list |
| Remove Component | Select [R] at step 5 | Triggers destructive operation flow |
| Add Component | Phase 2 - delegates to create-agent/create-workflow | Returns to edit-module after creation |

---

### 3. Destructive Operation Classification Table

**Addresses:** PARTY-013 (CRITICAL) - "Destructive operation" undefined

#### Definition

A **destructive operation** is any action that:
1. Permanently deletes data or files, OR
2. Cannot be easily undone with a simple "undo", OR
3. Has cascading effects on other components, OR
4. Could break module functionality if done incorrectly

#### Classification Table

| Operation | Destructive? | Severity | Confirmation Required | Backup Required |
|-----------|-------------|----------|----------------------|-----------------|
| **Edit agent content** | No | Low | Intent confirmation only | Yes - single file |
| **Edit workflow step** | No | Low | Intent confirmation only | Yes - single file |
| **Edit module.yaml name** | Yes | Medium | Explicit "CONFIRM" | Yes - full module |
| **Edit module.yaml paths** | Yes | High | Explicit "CONFIRM" + show impact | Yes - full module |
| **Remove agent file** | Yes | High | Explicit "CONFIRM" + dependency check | Yes - full module |
| **Remove workflow directory** | Yes | Critical | Explicit "CONFIRM" + list all files | Yes - full module |
| **Remove from module.yaml registry** | Yes | High | Explicit "CONFIRM" | Yes - config only |
| **Rename component** | Yes | Medium | Explicit "CONFIRM" + show references | Yes - full module |
| **Change component path** | Yes | High | Explicit "CONFIRM" + validation | Yes - full module |

#### Confirmation Protocol by Severity

| Severity | Protocol |
|----------|----------|
| **Low** | Intent-based: "You want to update the persona. Proceed? [Y/N]" |
| **Medium** | Explicit confirm: "This will rename X. Type 'CONFIRM' to proceed:" |
| **High** | Impact display + confirm: "This affects 3 files: [list]. Type 'CONFIRM' to proceed:" |
| **Critical** | Full warning: "WARNING: This will permanently delete [N] files. Type 'DELETE [component-name]' to proceed:" |

---

### 4. Complete "Make Changes" Process Definition

**Addresses:** ISSUE-013 (CRITICAL) - "Make Changes" step undefined

The "Make Changes" phase is the core editing engine. It operates differently based on component type.

#### 4.1 Agent File Editing Process

```
MAKE CHANGES: Agent File
────────────────────────────────────────────────────────────────
INPUT: Selected agent file path, user's edit intent

STEP 1: Load and Parse
  - Read agent file completely
  - Parse YAML frontmatter (if present)
  - Identify sections: name, description, persona, capabilities,
    tools, communication_style, custom sections

STEP 2: Determine Edit Scope
  Ask user: "What aspect do you want to change?"

  OPTIONS:
  [1] Persona/Role Definition
  [2] Capabilities/Skills
  [3] Tools/Permissions
  [4] Communication Style
  [5] Frontmatter/Metadata
  [6] Custom Section (specify)
  [7] Full Rewrite

STEP 3: Section-Specific Edit
  Based on selection:

  [1] Persona Edit:
      - Display current persona section
      - Ask: "Describe the change you want"
      - Propose updated persona text
      - User approves/modifies

  [2] Capabilities Edit:
      - Display current capabilities list
      - Ask: "Add, remove, or modify which capability?"
      - Make specific changes
      - User approves/modifies

  [3-6] Similar pattern: Display → Discuss → Propose → Approve

  [7] Full Rewrite:
      - Warn: "This replaces entire file"
      - Guide through complete agent definition
      - Use agent-builder pattern as template

STEP 4: Apply Changes
  - Create backup of original file
  - Write modified content
  - Preserve formatting and structure

STEP 5: Immediate Validation
  - Parse modified file (catches syntax errors)
  - Verify required fields present
  - Check BMAD compliance

OUTPUT: Modified agent file, backup reference, validation status
────────────────────────────────────────────────────────────────
```

#### 4.2 Workflow Editing Process

```
MAKE CHANGES: Workflow
────────────────────────────────────────────────────────────────
INPUT: Selected workflow directory path, user's edit intent

STEP 1: Analyze Workflow Structure
  - Read workflow.md (main file)
  - Scan /steps/ directory for step files
  - Identify: step count, step names, dependencies

STEP 2: Present Workflow Structure
  Display:
  "Workflow: create-plan
   Main File: workflow.md
   Steps:
     step-01-init.md
     step-02-concept.md
     step-03-structure.md

   What would you like to edit?"

STEP 3: Edit Target Selection
  OPTIONS:
  [M] Main workflow.md file
  [S] Specific step file (will list)
  [A] Add new step
  [R] Remove step
  [O] Reorder steps

STEP 4: Execute Edit by Type

  [M] Main File Edit:
      - Same process as agent file editing
      - Sections: frontmatter, goal, role, architecture, rules

  [S] Step File Edit:
      - List step files with numbers
      - User selects specific step
      - Edit sections: goal, rules, sequence, menu, metrics

  [A] Add Step (Phase 2):
      - Determine insertion point
      - Create from template
      - Update step numbering
      - Update workflow.md references

  [R] Remove Step (Destructive):
      - Confirm deletion
      - Remove file
      - Renumber remaining steps
      - Update workflow.md

STEP 5: Apply and Validate
  - Backup affected files
  - Write changes
  - Validate workflow coherence
  - Check step references

OUTPUT: Modified workflow files, backup references, validation status
────────────────────────────────────────────────────────────────
```

#### 4.3 Module.yaml Editing Process

```
MAKE CHANGES: Module.yaml
────────────────────────────────────────────────────────────────
INPUT: module.yaml path, user's edit intent

STEP 1: Parse Configuration
  - Read and parse YAML
  - Identify sections: metadata, agents[], workflows[], settings

STEP 2: Present Editable Fields
  Display:
  "Module Configuration: my-module

   [1] name: my-module
   [2] version: 1.0.0
   [3] description: 'A module for...'
   [4] Agents Registry (3 entries)
   [5] Workflows Registry (2 entries)
   [6] Custom Settings

   Which field to edit?"

STEP 3: Field-Specific Edit

  [1] Name Change (Destructive - Medium):
      - Warn about folder rename implications
      - Confirm new name
      - Update related references

  [2] Version:
      - Suggest semantic versioning
      - No destructive impact

  [3] Description:
      - Simple text replacement
      - No destructive impact

  [4] Agents Registry:
      - Show current registrations
      - Add/remove/modify entries
      - Validate paths exist

  [5] Workflows Registry:
      - Same as agents

  [6] Custom Settings:
      - Freeform YAML editing
      - Syntax validation

STEP 4: Apply and Validate
  - Backup config
  - Write changes
  - Validate YAML syntax
  - Validate path references

OUTPUT: Modified module.yaml, backup reference, validation status
────────────────────────────────────────────────────────────────
```

---

### 5. Edit Completion Trigger Definition

**Addresses:** PARTY-015 (MEDIUM) - "Edit completes" trigger undefined

#### Definition

An "edit completes" when ALL of the following conditions are met:

| Condition | Verification Method |
|-----------|---------------------|
| User has approved the proposed changes | Explicit "Y" or approval statement in chat |
| Changes have been written to disk | File write operation succeeded |
| Basic validation passed | BMAD format check returns no errors |
| No write errors occurred | Exception handling captured no failures |

#### State Machine

```
EDITING → PROPOSED → APPROVED → WRITTEN → VALIDATED → COMPLETE
   │          │          │          │          │
   │          │          │          │          └─ Validation failed → EDITING
   │          │          │          └─ Write failed → EDITING (restore backup)
   │          │          └─ User rejected → EDITING (revise proposal)
   │          └─ User requested changes → EDITING
   └─ User canceled → CANCELED
```

#### Completion Triggers by Edit Type

| Edit Type | Completion Trigger |
|-----------|-------------------|
| Content edit | Changes written + validation passed |
| Add component | New file created + registered in module.yaml + validation passed |
| Remove component | File deleted + unregistered + backup confirmed |
| Rename | Old removed + new created + references updated + validation passed |

#### Post-Completion Actions

1. Log edit to changelog (file modified, timestamp, summary)
2. Clean up backup (if validation passed)
3. Present iteration menu: "Do you have more edits? [Y/N]"

---

### 6. Menu Action Behavior for Each Category

**Addresses:** PARTY-009 (HIGH) - Menu action behavior undefined, ISSUE-016 (MEDIUM) - Edit type menu ambiguous

#### Main Navigation Menu Behavior

```
Module: my-module
─────────────────
[1] Agents
[2] Workflows
[3] Configuration (module.yaml)
[4] Documentation (README.md)

Select item or 'done' to finish:
```

| User Input | System Response |
|------------|-----------------|
| `1` | Expand agents submenu: lists all agent files with sub-numbers (1.1, 1.2, etc.) |
| `2` | Expand workflows submenu: lists all workflow directories with sub-numbers |
| `3` | Enter module.yaml edit mode (see 4.3 above) |
| `4` | Enter documentation edit mode (simple text editing) |
| `done` | Exit edit loop, proceed to completion summary |
| `back` | Return to previous menu level |
| `help` | Display available commands and current context |
| `?` | Same as help |
| Any other text | Interpret as question, respond, redisplay menu |

#### Component Selection Menu Behavior

When user selects a numbered component (e.g., `1.1` for first agent):

```
Selected: analyst.md
─────────────────────
[E] Edit content
[V] View full file
[R] Remove (destructive)
[B] Back to menu

Select action:
```

| User Input | System Response |
|------------|-----------------|
| `E` or `e` or `edit` | Enter Make Changes process for this component |
| `V` or `v` or `view` | Display full file contents, then return to this menu |
| `R` or `r` or `remove` | Enter destructive operation flow with confirmations |
| `B` or `b` or `back` | Return to main navigation menu |
| Other text | Interpret as clarification question, respond, redisplay |

#### Edit Type Disambiguation

**Addresses:** ISSUE-016 specifically

When "Edit content" is selected, further disambiguation:

```
Edit analyst.md - Select focus:
────────────────────────────────
[1] Persona/Role (lines 5-20)
[2] Capabilities (lines 22-35)
[3] Tools (lines 37-45)
[4] Communication Style (lines 47-55)
[5] Full file (all sections)
[Q] Quick edit (describe what you want)

Select or describe your edit:
```

| User Input | System Response |
|------------|-----------------|
| `1-4` | Load specific section, enter focused edit mode |
| `5` | Load full file, enter comprehensive edit mode |
| `Q` or natural language | AI interprets intent, suggests which section(s) to modify |

---

### 7. View Options Specification

**Addresses:** ISSUE-018 (MEDIUM) - View options behavior unclear

#### View Modes

| Mode | Description | When to Use |
|------|-------------|-------------|
| **Focused View** (default) | Shows only the section being edited with context | Precision edits, less cognitive load |
| **Full File View** | Shows entire file with line numbers | Understanding full context, cross-section changes |
| **Diff View** | Shows before/after comparison | After edits, before confirmation |
| **Structure View** | Shows outline/sections without content | Navigation, understanding organization |

#### View Command Syntax

```
View Commands (available during any edit):
  /view full      - Show entire file
  /view section   - Show current section only
  /view diff      - Show pending changes as diff
  /view structure - Show file outline
  /view lines N-M - Show specific line range
```

#### Automatic View Behavior

| Context | Default View | Rationale |
|---------|--------------|-----------|
| Initial component selection | Structure View | See organization before editing |
| Section edit mode | Focused View + 3 lines context | Precision with context |
| Before save confirmation | Diff View | Verify changes |
| After validation failure | Full File View + error highlighting | Debug issues |

#### View Toggle Persistence

- View preference persists within a session
- User can set default: `/set default-view focused`
- Resets to default between components

---

### 8. Rename/Move Operation Handling

**Addresses:** ISSUE-009 (MEDIUM) - Missing rename/move operations

**Note:** This is Phase 3 functionality. MVP only supports edit-in-place.

#### Rename Operation Process (Phase 3)

```
RENAME COMPONENT
────────────────────────────────────────────────────────────────
TRIGGER: User selects rename option or describes rename intent

STEP 1: Identify Current State
  - Component type (agent, workflow, task)
  - Current name and path
  - All references to this component

STEP 2: Collect New Name
  - Prompt for new name
  - Validate naming conventions (kebab-case, no conflicts)

STEP 3: Impact Analysis
  Display:
  "Renaming 'analyst' to 'senior-analyst' will update:
   - File: agents/analyst.md → agents/senior-analyst.md
   - module.yaml: agents.analyst → agents.senior-analyst
   - References in: workflow-1.md (2 occurrences)

   Type 'CONFIRM' to proceed:"

STEP 4: Execute Rename
  - Create new file with updated internal references
  - Update module.yaml registration
  - Update all referencing files
  - Validate all changes
  - Delete old file (only after validation passes)

STEP 5: Verification
  - List all files modified
  - Confirm no broken references
────────────────────────────────────────────────────────────────
```

#### Move Operation Process (Phase 3)

```
MOVE COMPONENT
────────────────────────────────────────────────────────────────
TRIGGER: User wants to move component to different location

SCENARIOS:
  A) Move agent to different directory (rare)
  B) Move workflow to different module (cross-module, very rare)
  C) Reorganize internal workflow steps

For MVP: Not supported. Suggest manual move + re-registration.
For Phase 3: Similar to rename with path changes.
────────────────────────────────────────────────────────────────
```

---

### 9. Dependency Tracking Approach

**Addresses:** ISSUE-006 (MEDIUM) - No dependency tracking between components

#### Dependency Types

| Dependency Type | Example | Detection Method |
|-----------------|---------|------------------|
| **Workflow → Agent** | Workflow references agent by name | Scan for agent mentions in workflow files |
| **Workflow → Workflow** | Step delegates to another workflow | Parse `nextStepFile`, delegation calls |
| **Agent → Task** | Agent uses task in capabilities | Scan agent tool/task references |
| **Config → Component** | module.yaml registers component | Parse module.yaml arrays |
| **Step → Step** | Step file references next step | Parse frontmatter `nextStepFile` |

#### MVP Dependency Handling

For Phase 1 (MVP), dependency tracking is **passive warning only**:

```
When user attempts destructive operation:

1. Scan for potential references to target component
2. If references found:
   Display:
   "Warning: This component may be referenced by:
    - workflow-1.md (line 45)
    - step-02.md (line 12)

    These references will NOT be automatically updated.
    Proceed anyway? [Y/N]"
3. User decides whether to proceed
4. If yes, proceed with operation (user responsibility to fix references)
```

#### Phase 2+ Dependency Handling

Enhanced dependency tracking with automatic updates:

```
DEPENDENCY GRAPH BUILD
────────────────────────────────────────────────────────────────
On module load:
  1. Parse all component files
  2. Build dependency graph:
     {
       "analyst": {
         "type": "agent",
         "referenced_by": ["create-plan/workflow.md", "review-code/step-01.md"],
         "references": []
       },
       "create-plan": {
         "type": "workflow",
         "referenced_by": [],
         "references": ["analyst", "architect"]
       }
     }
  3. Cache graph for session duration
  4. Update graph after each edit

On destructive operation:
  1. Query graph for dependencies
  2. Offer automatic reference updates
  3. Update all referencing files if user approves
────────────────────────────────────────────────────────────────
```

#### Dependency Warning Levels

| Dependency Count | Warning Level | User Action Required |
|------------------|---------------|---------------------|
| 0 references | None | Proceed normally |
| 1-2 references | Info | Show references, single confirmation |
| 3-5 references | Warning | List all, explicit "CONFIRM" |
| 6+ references | Critical | Full impact report, type component name to confirm |

---

### 10. Multi-Agent Module Support

**Addresses:** ISSUE-008 (MEDIUM) - No multi-agent module support

#### Module Types

| Type | Description | Agent Count | Example |
|------|-------------|-------------|---------|
| **Single-Agent** | Module with one primary agent | 1 | Simple utility module |
| **Multi-Agent** | Module with multiple specialized agents | 2-5 | BMM module |
| **Agent-Heavy** | Module primarily consisting of agents | 6+ | Team simulation module |

#### Multi-Agent Specific Behaviors

**Navigation Enhancement:**

```
For modules with 3+ agents:

[1] Agents (5 total)
    1.1 Primary Agents
        1.1.1 coordinator.md
        1.1.2 facilitator.md
    1.2 Specialist Agents
        1.2.1 analyst.md
        1.2.2 architect.md
        1.2.3 dev.md
```

**Agent Relationship Awareness:**

When editing one agent in a multi-agent module:
- Check for agent-to-agent references
- Warn if edit breaks agent coordination patterns
- Suggest reviewing related agents

**Batch Agent Operations (Phase 3):**

```
For multi-agent modules, offer:
  [BA] Batch agent edit - Apply same change to multiple agents

  Example: "Update communication_style to formal for all agents"
  - Lists affected agents
  - Shows preview of changes
  - Applies with single confirmation
```

---

### 11. Module.yaml Editing Details

**Addresses:** ISSUE-007 (MEDIUM) - Missing module.yaml editing details

#### Editable Fields Reference

```yaml
# module.yaml structure with edit specifications

# METADATA SECTION (Low risk edits)
name: module-name          # DESTRUCTIVE: triggers folder rename discussion
version: 1.0.0             # Safe: simple update
description: "..."         # Safe: simple update
author: user-name          # Safe: simple update
created: 2026-01-07        # Read-only: auto-generated
updated: 2026-01-07        # Auto-updated on save

# REGISTRATION SECTION (Medium risk edits)
agents:                    # Array of agent registrations
  - name: analyst          # Reference name (DESTRUCTIVE if changed)
    path: agents/analyst.md # File path (validated on edit)
    description: "..."      # Safe: display text only

workflows:                 # Array of workflow registrations
  - name: create-plan      # Reference name (DESTRUCTIVE if changed)
    path: workflows/create-plan/ # Directory path (validated)
    description: "..."      # Safe: display text only

# SETTINGS SECTION (Module-specific, variable risk)
settings:                  # Custom key-value pairs
  output_folder: "..."     # Path setting (validated)
  default_mode: "..."      # Enum setting (validated against allowed)
  custom_field: "..."      # Freeform (syntax only validation)
```

#### Edit Process by Field Type

| Field Type | Edit Process | Validation |
|------------|--------------|------------|
| **Simple text** | Direct replacement | Non-empty, reasonable length |
| **Version** | Suggest semver format | Valid semver pattern |
| **Name/Reference** | Destructive flow with impact analysis | Kebab-case, unique, no reserved words |
| **Path** | File browser or direct input | Path exists, correct type |
| **Array items** | Add/remove/modify individual entries | Entry validation per type |
| **Nested objects** | Recursive field editing | Schema validation if defined |

---

### 12. Iteration Boundary Definition

**Addresses:** ISSUE-017 (MEDIUM) - Iteration boundary undefined

#### What Constitutes "One Edit"

An edit iteration boundary is defined as:

```
ONE EDIT = One logical change to one component

Examples of SINGLE edits:
  - Update persona section of one agent
  - Modify one step file in a workflow
  - Add one new entry to module.yaml agents array
  - Change module description

Examples of MULTIPLE edits (should be separate iterations):
  - Update persona AND capabilities (2 edits, or user can combine)
  - Modify agent AND update its module.yaml registration (2 edits)
  - Edit workflow.md AND three step files (4 edits)
```

#### Iteration Flow Control

```
┌─────────────────────────────────────────────────┐
│ Edit Complete (single component, validation ok)  │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│ "Edit saved. Do you have more edits?"           │
│ [Y] Yes, continue editing                       │
│ [N] No, I'm done                                │
│ [V] Run full validation first                   │
└─────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
    Return to      Session        Validate
    Main Menu      Summary        then ask
                                  again
```

#### Session vs Edit Boundaries

| Boundary | Scope | Trigger |
|----------|-------|---------|
| **Edit boundary** | Single component change | Change written + validated |
| **Batch boundary** | Multiple related changes | User explicitly groups OR same component type |
| **Session boundary** | All edits in one workflow run | User says "done" or exits |

#### Batch Edit Option

When user indicates multiple edits to same component type:

```
"I need to update all the agent personas"

System: "Would you like to:
  [I] Edit each agent individually (iterate)
  [B] Batch edit mode (review all, then save all)

For batch mode, I'll collect all changes and apply them together."
```

---

### Summary: Issue Resolution Matrix

| Issue ID | Severity | Status | Section |
|----------|----------|--------|---------|
| ISSUE-013 | CRITICAL | RESOLVED | Section 4 |
| PARTY-011 | CRITICAL | RESOLVED | Section 1 |
| PARTY-013 | CRITICAL | RESOLVED | Section 3 |
| PARTY-009 | HIGH | RESOLVED | Section 6 |
| ISSUE-006 | MEDIUM | RESOLVED | Section 9 |
| ISSUE-007 | MEDIUM | RESOLVED | Section 11 |
| ISSUE-008 | MEDIUM | RESOLVED | Section 10 |
| ISSUE-009 | MEDIUM | RESOLVED | Section 8 |
| ISSUE-016 | MEDIUM | RESOLVED | Section 6 |
| ISSUE-017 | MEDIUM | RESOLVED | Section 12 |
| ISSUE-018 | MEDIUM | RESOLVED | Section 7 |
| PARTY-012 | MEDIUM | RESOLVED | Section 2 |
| PARTY-015 | MEDIUM | RESOLVED | Section 5 |

---

## Safety & Validation Specification

This section defines safety mechanisms to prevent data loss, corruption, and inconsistent states during module editing. All edit operations MUST follow these specifications.

**Issues Addressed:**
- ISSUE-021 (CRITICAL): Silent data loss risk - backup creation failure leads to data loss
- ISSUE-022 (CRITICAL): Circular reference risk - editing could create circular references
- ISSUE-023 (HIGH): Partial edit state risk - multi-file edits could leave module inconsistent
- ISSUE-024 (HIGH): Invalid YAML production risk - user edits could produce invalid YAML
- ISSUE-025 (HIGH): Reference breakage risk - editing path variables could break references
- ISSUE-014 (HIGH): Validate vs compliance confusion - need to clarify difference
- ISSUE-019 (LOW): Basic validation undefined - need to specify checks
- PARTY-004 (CRITICAL): Backup deletion before validation complete - creates unrecoverable state
- PARTY-017 (HIGH): Write-before-validate creates corruption window
- PARTY-001 (HIGH): "Basic validation" undefined

---

### 1. Backup Strategy with Verification

**Problem Addressed:** ISSUE-021 (CRITICAL), PARTY-004 (CRITICAL)

#### 1.1 Backup Creation Protocol

**CRITICAL RULE: NEVER delete original files or apply changes until backup is VERIFIED.**

```
BACKUP CREATION SEQUENCE (MANDATORY):
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. CALCULATE checksum (SHA-256) of original file(s)                         │
│ 2. COPY file(s) to backup location: {module_path}/.backup/{timestamp}/      │
│ 3. CALCULATE checksum of backup file(s)                                     │
│ 4. VERIFY: Original checksum == Backup checksum                             │
│ 5. IF MISMATCH → ABORT with error message, DO NOT proceed with edit         │
│ 6. IF VERIFIED → Record backup manifest with timestamps and checksums       │
│ 7. ONLY THEN may editing begin                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Backup Directory Structure:**
```
{module_path}/
├── .backup/
│   ├── manifest.json                    # Active backup metadata
│   ├── {YYYY-MM-DD_HH-MM-SS}/          # Timestamped backup folder
│   │   ├── agents/                      # Backed up agents
│   │   │   └── analyst.md
│   │   ├── workflows/                   # Backed up workflows
│   │   │   └── create-plan/
│   │   └── module.yaml                  # Backed up config
│   └── {previous-timestamp}/            # Keep last 3 backups
└── [actual module files]
```

**Backup Manifest Schema:**
```json
// .backup/manifest.json
{
  "version": 1,
  "transactionId": "uuid-abc123",
  "created": "2026-01-07T14:30:00Z",
  "modulePath": "{module_path}",
  "backupPath": "{module_path}/.backup/{timestamp}/",
  "status": "active",
  "statusOptions": ["active", "validated", "restored", "deleted"],
  "files": [
    {
      "relativePath": "agents/analyst.md",
      "originalChecksum": "sha256:abc123...",
      "backupChecksum": "sha256:abc123...",
      "checksumVerified": true,
      "sizeBytes": 2048
    },
    {
      "relativePath": "module.yaml",
      "originalChecksum": "sha256:def456...",
      "backupChecksum": "sha256:def456...",
      "checksumVerified": true,
      "sizeBytes": 512
    }
  ],
  "allVerified": true
}
```

#### 1.2 Atomic Swap Pattern for Single-File Edits

**For single-file edits, use atomic write-then-rename:**

```
ATOMIC WRITE SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. WRITE new content to temporary file: {file}.tmp                          │
│ 2. VALIDATE temporary file (syntax, references, structure)                  │
│ 3. IF VALIDATION FAILS → Delete temp file, keep original, report errors     │
│ 4. IF VALIDATION PASSES → Atomic rename: {file}.tmp → {file}                │
│ 5. VERIFY renamed file matches expected checksum                            │
│ 6. Original is now safely replaced                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Platform Notes:**
- POSIX systems: `rename()` is atomic
- Windows: Use `MoveFileEx` with `MOVEFILE_REPLACE_EXISTING` flag
- Always verify after rename to catch edge cases

#### 1.3 Backup Retention and Deletion Protocol

**CRITICAL RULE: NEVER delete backups until ALL conditions are met:**

| Condition | Verification Method | Required |
|-----------|---------------------|----------|
| All edited files pass SYNTAX validation | YAML parse succeeds | YES |
| All edited files pass REFERENCE validation | All paths resolve | YES |
| All edited files pass COMPLIANCE validation | BMAD format check | IF RUN |
| User has explicitly confirmed satisfaction | "done" or equivalent | YES |
| No rollback has been requested | No user abort/undo request | YES |

**Backup Deletion Sequence:**
```
BACKUP DELETION SEQUENCE (POST-VALIDATION ONLY):
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. CONFIRM all validation phases have status: PASSED                        │
│ 2. CONFIRM user has indicated satisfaction (explicit "done" or "N" to more) │
│ 3. UPDATE manifest.json: status: "validated"                                │
│ 4. ONLY THEN delete backup files from {timestamp}/ directory                │
│ 5. UPDATE manifest.json: status: "deleted", deleted_at: timestamp           │
│ 6. KEEP manifest.json as audit trail (purge after 30 days or configurable)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 1.4 Rollback Procedure

**If any edit operation fails or user requests rollback:**

```
ROLLBACK SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. VERIFY backup manifest exists at {module_path}/.backup/manifest.json     │
│ 2. VERIFY manifest.status is "active" (not already deleted)                 │
│ 3. FOR EACH file in manifest:                                               │
│    a. CALCULATE current checksum of backup file                             │
│    b. VERIFY: Stored backup_checksum == Current backup checksum             │
│    c. IF MISMATCH → ERROR: "Backup corrupted, manual recovery required"     │
│ 4. IF ALL VERIFIED → COPY backup files to original locations                │
│ 5. VERIFY restored files match original_checksum from manifest              │
│ 6. UPDATE manifest.json: status: "restored", restored_at: timestamp         │
│ 7. INFORM user: "Module restored to pre-edit state. Backup preserved."      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Transaction-Like Semantics for Multi-File Edits

**Problem Addressed:** ISSUE-023 (HIGH)

#### 2.1 Edit Transaction Model

**CRITICAL RULE: Multi-file edits are atomic. Either ALL succeed or NONE are applied.**

```
TRANSACTION MODEL:
┌─────────────────────────────────────────────────────────────────────────────┐
│ PREPARE PHASE                                                               │
│ ├─ Create backups of ALL files that will be modified                        │
│ ├─ Verify ALL backups (checksum match)                                      │
│ ├─ Create transaction manifest with status: "in_progress"                   │
│ └─ IF ANY backup fails → ABORT entire transaction                           │
│                                                                             │
│ EDIT PHASE                                                                  │
│ ├─ Apply edit 1 to temp file → Validate → Stage (don't replace yet)        │
│ ├─ Apply edit 2 to temp file → Validate → Stage                             │
│ ├─ ...                                                                      │
│ ├─ Apply edit N to temp file → Validate → Stage                             │
│ └─ IF ANY edit/validation fails → ABORT, delete all temp files              │
│                                                                             │
│ COMMIT PHASE (only if ALL edits validated successfully)                     │
│ ├─ Update transaction status: "staged"                                      │
│ ├─ Atomic rename temp file 1 → target 1                                     │
│ ├─ Atomic rename temp file 2 → target 2                                     │
│ ├─ ...                                                                      │
│ ├─ Update transaction status: "committed"                                   │
│ └─ IF ANY rename fails → ROLLBACK all from backup                           │
│                                                                             │
│ ROLLBACK TRIGGER (if ANY step fails)                                        │
│ ├─ Delete all temp files                                                    │
│ ├─ Restore any files that were renamed from backup                          │
│ └─ Update transaction status: "rolled_back"                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.2 Transaction Manifest Schema

```yaml
# .backup/transaction-{uuid}.yaml
transaction_id: "uuid-abc123"
created: "2026-01-07T14:30:00Z"
status: "in_progress"  # in_progress | staged | committed | rolled_back | failed
edit_description: "Updated agent personas across multiple files"
files:
  - target: "agents/analyst.md"
    temp: "agents/analyst.md.tmp"
    backup: ".backup/{timestamp}/agents/analyst.md"
    edit_type: "modify"
    validation_status: "pending"  # pending | passed | failed
    validation_errors: []
  - target: "agents/architect.md"
    temp: "agents/architect.md.tmp"
    backup: ".backup/{timestamp}/agents/architect.md"
    edit_type: "modify"
    validation_status: "pending"
    validation_errors: []
commit_log:
  - timestamp: "2026-01-07T14:31:00Z"
    action: "file_1_renamed"
    success: true
error_log: []
```

#### 2.3 Transaction States and Recovery

| State | Description | Recovery Action |
|-------|-------------|-----------------|
| `in_progress` | Edits being applied to temp files | Safe to abort, delete temps, no changes to originals |
| `staged` | All temps validated, ready to commit | Can commit or rollback cleanly |
| `committed` | All files replaced atomically | Transaction complete, backup can be cleaned |
| `rolled_back` | Transaction aborted, originals restored | Clean up temp files |
| `failed` | Error during commit phase | Investigate, manual recovery may be needed |

#### 2.4 Partial Commit Recovery

**If system crashes during commit phase (rare but critical):**

```
ON WORKFLOW RESTART - DETECT INCOMPLETE TRANSACTION:
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. SCAN for transaction manifest with status: "staged" or partial commit    │
│ 2. IF FOUND:                                                                │
│    Display to user:                                                         │
│    "Incomplete transaction detected from {timestamp}.                       │
│     Files affected: {list}                                                  │
│                                                                             │
│     Recovery Options:                                                       │
│     [R] ROLLBACK - Restore all files from backup (recommended)              │
│     [C] COMPLETE - Attempt to finish staged changes                         │
│     [M] MANUAL - Show status, I'll handle it manually"                      │
│                                                                             │
│ 3. USER selects option → Execute recovery → Update manifest                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. YAML Syntax Validation Approach

**Problem Addressed:** ISSUE-024 (HIGH), PARTY-001 (HIGH)

#### 3.1 YAML Syntax Validation Checklist

**MANDATORY: Every YAML file MUST pass ALL these checks before being written:**

| # | Check | Description | Blocks Save |
|---|-------|-------------|-------------|
| 1 | **Parse Success** | YAML library parses without exceptions | YES |
| 2 | **No Duplicate Keys** | Same key doesn't appear twice at same level | YES |
| 3 | **Quote Balance** | All quoted strings properly opened and closed | YES |
| 4 | **Special Char Escape** | Colons, hashes, brackets escaped in values | YES |
| 5 | **Valid Structure** | Expected top-level keys exist | YES |
| 6 | **Type Correctness** | Values match expected types (string, array, bool) | YES (configurable) |
| 7 | **Indentation** | Consistent indentation (2-space recommended) | NO (warning) |
| 8 | **Encoding** | File is valid UTF-8 | YES |

#### 3.2 Validation Implementation Sequence

```
YAML VALIDATION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: SYNTAX PARSE TEST                                                  │
│ ├─ Load YAML content with strict parser (fail on duplicate keys)            │
│ ├─ IF PARSE FAILS → Capture error with line number and column               │
│ └─ Return: {valid: false, errors: [{line: N, col: M, msg: "..."}]}          │
│                                                                             │
│ PHASE 2: SCHEMA VALIDATION                                                  │
│ ├─ For module.yaml: Verify required fields (name, version, agents, etc.)    │
│ ├─ For agent files: Verify frontmatter structure if present                 │
│ ├─ For workflow files: Verify frontmatter and required sections             │
│ └─ Return: {valid: false, errors: [{field: "X", msg: "missing required"}]}  │
│                                                                             │
│ PHASE 3: ROUND-TRIP TEST                                                    │
│ ├─ Parse YAML → Serialize back to string → Parse again                      │
│ ├─ Compare original structure with round-tripped structure                  │
│ ├─ IF DIFFERENT → Warning about potential formatting issues                 │
│ └─ This catches subtle serialization issues                                 │
│                                                                             │
│ PHASE 4: AGGREGATE RESULTS                                                  │
│ ├─ Combine all errors from all phases                                       │
│ ├─ Sort by severity (blocking errors first)                                 │
│ └─ Return comprehensive validation result                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 3.3 User Edit Validation (Real-Time)

**When user provides YAML content directly, validate IMMEDIATELY:**

```
USER EDIT VALIDATION FLOW:
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. USER provides edit content                                               │
│ 2. IMMEDIATELY run validation (before showing any confirmation)             │
│ 3. IF INVALID:                                                              │
│    Display:                                                                 │
│    "YAML Validation Failed:                                                 │
│                                                                             │
│     ERROR Line 15, Column 4:                                                │
│       Expected indentation of 2 spaces, found 3                             │
│       Context: '   name: analyst'                                           │
│                 ^^^                                                         │
│                                                                             │
│     ERROR Line 22:                                                          │
│       Duplicate key 'commands' found                                        │
│       First occurrence: line 10                                             │
│                                                                             │
│     Please correct these issues. The file will NOT be saved until valid."   │
│                                                                             │
│ 4. USER corrects issues                                                     │
│ 5. RE-VALIDATE                                                              │
│ 6. LOOP until valid OR user cancels                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 3.4 Common YAML Errors and Auto-Suggestions

| Error Pattern | Auto-Suggestion |
|---------------|-----------------|
| Unquoted colon in value | "Wrap value in quotes: `key: 'value: with colon'`" |
| Tab character | "Replace tabs with spaces (2-space indent recommended)" |
| Trailing whitespace | "Remove trailing spaces on line N" |
| Missing space after colon | "Add space: `key: value` not `key:value`" |
| Inconsistent indent | "Use consistent 2-space indentation throughout" |

---

### 4. Reference and Path Validation Approach

**Problem Addressed:** ISSUE-025 (HIGH)

#### 4.1 Reference Types to Validate

| Reference Type | Pattern Example | Validation Method |
|----------------|-----------------|-------------------|
| **Absolute File Path** | `/path/to/file.md` | File.exists(path) |
| **Relative File Path** | `./agents/analyst.md` | Resolve from current dir, check exists |
| **Variable Path** | `{workflow_path}/steps/` | Substitute variable, then check exists |
| **Module Reference** | `bmm/workflows/create-prd` | Module discovery, check registered |
| **Internal Anchor** | `#section-name` | Section exists in current file |
| **Cross-File Anchor** | `step-02.md#validation` | File exists AND section exists |
| **Template Variable** | `{project-root}/_bmad/...` | Variable defined AND path resolves |

#### 4.2 Reference Validation Protocol

```
REFERENCE VALIDATION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: EXTRACT ALL REFERENCES                                              │
│ ├─ Scan file for path patterns: {variable}/path, ./relative, #anchor        │
│ ├─ Scan YAML frontmatter for path variables                                 │
│ ├─ Scan markdown for file links: [text](path)                               │
│ └─ Build list: [{type, raw_reference, line_number}]                         │
│                                                                             │
│ STEP 2: RESOLVE VARIABLES                                                   │
│ ├─ Load variable definitions from workflow.md frontmatter                   │
│ ├─ Load module-level variables from module.yaml                             │
│ ├─ Substitute: {project-root} → actual path                                 │
│ ├─ Substitute: {workflow_path} → actual path                                │
│ └─ Build list: [{type, raw, resolved, line_number}]                         │
│                                                                             │
│ STEP 3: VERIFY EACH REFERENCE                                               │
│ ├─ For file paths: Check File.exists(resolved_path)                         │
│ ├─ For directories: Check Directory.exists(resolved_path)                   │
│ ├─ For anchors: Parse target file, check section heading exists             │
│ └─ Mark each reference: valid | invalid | warning                           │
│                                                                             │
│ STEP 4: REPORT RESULTS                                                      │
│ ├─ List all invalid references with:                                        │
│ │   - Line number in source file                                            │
│ │   - Raw reference text                                                    │
│ │   - Resolved path (what we tried to find)                                 │
│ │   - Suggestion (did you mean X?)                                          │
│ └─ Block save if any CRITICAL references invalid                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.3 Path Variable Change Guard

**CRITICAL: When user attempts to change a path variable, show impact BEFORE applying:**

```
PATH VARIABLE CHANGE GUARD:
┌─────────────────────────────────────────────────────────────────────────────┐
│ TRIGGER: User edits a path variable in frontmatter or module.yaml           │
│                                                                             │
│ STEP 1: DETECT CHANGE                                                       │
│   Old value: {workflow_path} = '_bmad/bmb/workflows/my-workflow'            │
│   New value: {workflow_path} = '_bmad/bmb/workflows/renamed-workflow'       │
│                                                                             │
│ STEP 2: IMPACT ANALYSIS                                                     │
│   Scan ALL files in module for references to this variable                  │
│   Found: 5 files with 12 total references                                   │
│                                                                             │
│ STEP 3: DISPLAY IMPACT                                                      │
│   "Path Variable Change Detected: 'workflow_path'                           │
│                                                                             │
│    Old: '_bmad/bmb/workflows/my-workflow'                                   │
│    New: '_bmad/bmb/workflows/renamed-workflow'                              │
│                                                                             │
│    Impact Analysis:                                                         │
│    - 5 files reference {workflow_path}                                      │
│    - 12 total references will be affected                                   │
│    - Files: step-01.md, step-02.md, step-03.md, workflow.md, template.md    │
│                                                                             │
│    Options:                                                                 │
│    [A] AUTO-UPDATE: Update all references to use new path                   │
│    [K] KEEP: Cancel change, keep old path                                   │
│    [P] PROCEED: Apply change, I'll fix references manually                  │
│                                                                             │
│    Select option:"                                                          │
│                                                                             │
│ STEP 4: EXECUTE CHOICE                                                      │
│   [A] → Update path variable + update all references + validate all         │
│   [K] → Abort edit, restore original value                                  │
│   [P] → Update path only, warn about broken references                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 5. Circular Reference Detection

**Problem Addressed:** ISSUE-022 (CRITICAL)

#### 5.1 Reference Graph Model

**Build a directed graph of references to detect cycles:**

```
CIRCULAR REFERENCE DETECTION:
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: BUILD REFERENCE GRAPH                                               │
│ ├─ Node: Each file in module (agents, workflows, steps, configs)            │
│ ├─ Edge: A → B if file A contains reference to file B                       │
│ └─ Graph structure: {node: [list of nodes it references]}                   │
│                                                                             │
│ STEP 2: APPLY PROPOSED EDIT                                                 │
│ ├─ Parse new/modified references from edit                                  │
│ ├─ Add new edges to graph                                                   │
│ └─ Remove deleted edges from graph                                          │
│                                                                             │
│ STEP 3: DETECT CYCLES (DFS Algorithm)                                       │
│ ├─ For each node in graph:                                                  │
│ │   ├─ Mark node as "visiting"                                              │
│ │   ├─ For each neighbor:                                                   │
│ │   │   ├─ IF neighbor is "visiting" → CYCLE FOUND                          │
│ │   │   ├─ IF neighbor is "unvisited" → Recurse                             │
│ │   │   └─ IF neighbor is "visited" → Skip (already processed)              │
│ │   └─ Mark node as "visited"                                               │
│ └─ Track path to reconstruct cycle chain                                    │
│                                                                             │
│ STEP 4: HANDLE CYCLE DETECTION                                              │
│ ├─ IF CYCLE FOUND:                                                          │
│ │   Display:                                                                │
│ │   "Circular Reference Detected!                                           │
│ │                                                                           │
│ │    Cycle: step-01.md → step-03.md → step-02.md → step-01.md               │
│ │                                                                           │
│ │    This edit creates a circular dependency that would cause               │
│ │    infinite loops during workflow execution.                              │
│ │                                                                           │
│ │    Options:                                                               │
│ │    [M] MODIFY: Change the reference to break the cycle                    │
│ │    [I] INTENTIONAL: Mark as intentional (e.g., workflow loop)             │
│ │    [C] CANCEL: Abort this edit                                            │
│ │                                                                           │
│ │    Select option:"                                                        │
│ └─ IF NO CYCLE → Proceed with edit                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 5.2 Circular Reference Types

| Type | Example | Risk Level | Action |
|------|---------|------------|--------|
| **Direct Self-Reference** | step-01.md references step-01.md | CRITICAL | Block unless marked intentional |
| **Two-Node Cycle** | A references B, B references A | CRITICAL | Block, show cycle |
| **Multi-Node Cycle** | A → B → C → D → A | HIGH | Block, show full chain |
| **Workflow Loop** | step-03 → step-01 (menu loop back) | MEDIUM | Allow if intentional pattern |

#### 5.3 Intentional Cycle Annotation

**Some cycles are legitimate (e.g., workflow menu loops). Allow with annotation:**

```yaml
# In frontmatter of file that intentionally creates a cycle:
circular_reference:
  allowed: true
  reason: "Menu loop returns to step selection"
  target: "step-02-select.md"
```

When this annotation exists:
- Skip cycle detection for this specific reference
- Log as "intentional cycle" in validation report
- Require reason field to be non-empty

---

### 6. Validation vs Compliance: Definitions and Checklists

**Problem Addressed:** ISSUE-014 (HIGH), ISSUE-019 (LOW)

#### 6.1 VALIDATION (Syntax & Structure) - MANDATORY

**Purpose:** Ensure files are technically correct and won't cause runtime errors.

**When:** ALWAYS run before ANY file write. Cannot be skipped.

**VALIDATION CHECKLIST (ALL ITEMS BLOCK SAVE IF FAILED):**

| Category | Check | Description |
|----------|-------|-------------|
| **SYNTAX** | YAML Parse | File parses as valid YAML without errors |
| **SYNTAX** | Markdown Render | File renders as valid Markdown |
| **SYNTAX** | No Duplicate Keys | Same YAML key doesn't appear twice at same level |
| **SYNTAX** | Encoding | File is valid UTF-8 |
| **STRUCTURE** | Required Frontmatter | Workflow/step files have required frontmatter fields |
| **STRUCTURE** | File Type Match | File extension matches content type (.md, .yaml) |
| **REFERENCES** | All Paths Resolve | Every file path reference points to existing file |
| **REFERENCES** | All Variables Defined | Every {variable} is defined somewhere |
| **REFERENCES** | No Circular Dependencies | No unintentional circular references |
| **SIZE** | Under Limit | File under 100KB (configurable, warning only) |

**Validation Result Schema:**
```yaml
validation_result:
  status: "PASS" | "FAIL"
  timestamp: "2026-01-07T14:30:00Z"
  file: "agents/analyst.md"
  checks:
    - name: "yaml_parse"
      status: "PASS"
    - name: "required_frontmatter"
      status: "FAIL"
      error: "Missing 'description' field in frontmatter"
      line: 1
  blocking_errors: 1
  warnings: 0
```

#### 6.2 COMPLIANCE (Best Practices & Standards) - OPTIONAL

**Purpose:** Ensure files follow BMAD standards and best practices for quality.

**When:** Optional, run on user request or at session completion. Can be skipped.

**COMPLIANCE CHECKLIST (ADVISORY - DOES NOT BLOCK SAVE):**

| Category | Check | Severity |
|----------|-------|----------|
| **TEMPLATE** | Follows agent/workflow template structure | MAJOR |
| **TEMPLATE** | All recommended sections present | MAJOR |
| **TEMPLATE** | Frontmatter follows template pattern | MINOR |
| **STYLE** | Role description follows partnership format | MINOR |
| **STYLE** | Menu patterns follow [A] [P] [C] standard | MINOR |
| **STYLE** | Consistent heading hierarchy (H1 → H2 → H3) | MINOR |
| **STYLE** | Emoji usage follows conventions | MINOR |
| **PERFORMANCE** | Step files ≤10KB (optimal ≤5KB) | MINOR |
| **PERFORMANCE** | No redundant/duplicate content | MINOR |
| **DOCUMENTATION** | Description fields are meaningful (>10 chars) | MINOR |
| **DOCUMENTATION** | All variables documented in comments | MINOR |
| **NAMING** | File names follow kebab-case convention | MINOR |
| **NAMING** | Variable names follow snake_case convention | MINOR |

**Compliance Result Schema:**
```yaml
compliance_result:
  status: "PASS" | "PARTIAL" | "FAIL"
  timestamp: "2026-01-07T14:30:00Z"
  file: "agents/analyst.md"
  score: 85  # Percentage of checks passed
  issues:
    - check: "template_structure"
      severity: "MAJOR"
      message: "Missing 'capabilities' section recommended by template"
      suggestion: "Add ## Capabilities section after persona"
    - check: "file_size"
      severity: "MINOR"
      message: "File is 12KB, optimal is ≤5KB"
      suggestion: "Consider splitting into focused sections"
  major_issues: 1
  minor_issues: 1
```

#### 6.3 When to Use Each

```
EDIT FLOW WITH VALIDATION/COMPLIANCE:
┌─────────────────────────────────────────────────────────────────────────────┐
│ USER makes edit                                                             │
│         ↓                                                                   │
│ VALIDATION (automatic, mandatory, cannot be skipped)                        │
│ ├─ PASS → Edit CAN be saved                                                 │
│ └─ FAIL → Edit BLOCKED, show errors, user must fix                          │
│         ↓                                                                   │
│ SAVE edit to disk (only after validation passes)                            │
│         ↓                                                                   │
│ USER selects 'done' or requests compliance check                            │
│         ↓                                                                   │
│ COMPLIANCE CHECK (optional, recommended, can be skipped)                    │
│ ├─ PASS → "Module meets BMAD standards"                                     │
│ ├─ PARTIAL → Show issues, user decides to fix or accept                     │
│ └─ FAIL → Show issues, strongly recommend fixes, user decides               │
│         ↓                                                                   │
│ USER confirms completion                                                    │
│         ↓                                                                   │
│ BACKUP cleanup (only after validation + user "done")                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Distinction:**
- **VALIDATION** = "Is this file technically valid?" (YES/NO, blocking)
- **COMPLIANCE** = "Does this file follow best practices?" (Score, advisory)

---

### 7. Write-Ahead Validation Pattern

**Problem Addressed:** PARTY-017 (HIGH)

#### 7.1 Core Principle

**GOLDEN RULE: NEVER write to disk before validation passes.**

```
WRONG (creates corruption window):
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Write new content to file                                                │
│ 2. Validate file                                 ← FILE ALREADY CORRUPTED   │
│ 3. IF INVALID → Try to restore backup            ← MAY FAIL, DATA LOST      │
└─────────────────────────────────────────────────────────────────────────────┘

CORRECT (write-ahead validation):
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Prepare new content IN MEMORY                 ← Original file untouched  │
│ 2. Validate content IN MEMORY                    ← Original file untouched  │
│ 3. IF INVALID → Reject, original untouched       ← NO CORRUPTION POSSIBLE   │
│ 4. IF VALID → Write to temp file                 ← Original file untouched  │
│ 5. Validate temp file                            ← Original file untouched  │
│ 6. IF INVALID → Delete temp, original untouched  ← NO CORRUPTION POSSIBLE   │
│ 7. IF VALID → Atomic rename temp to target       ← ATOMIC, ALL OR NOTHING   │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 7.2 Complete Write-Ahead Validation Sequence

```
WRITE-AHEAD VALIDATION SEQUENCE:
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: IN-MEMORY VALIDATION                                               │
│ ├─ Build new content as string/object in memory                             │
│ ├─ Run YAML/Markdown syntax validation on string                            │
│ ├─ Run reference validation (resolve all paths)                             │
│ ├─ Run circular reference detection on proposed graph                       │
│ ├─ IF ANY CHECK FAILS:                                                      │
│ │   └─ Return errors immediately, DO NOT PROCEED                            │
│ └─ All checks pass → Continue to Phase 2                                    │
│                                                                             │
│ PHASE 2: TEMP FILE WRITE                                                    │
│ ├─ Ensure backup exists and is verified                                     │
│ ├─ Write validated content to {file}.tmp                                    │
│ ├─ Calculate checksum of temp file                                          │
│ ├─ Read back temp file content                                              │
│ ├─ VERIFY: Read-back content == Original intended content                   │
│ ├─ IF MISMATCH (write corruption):                                          │
│ │   └─ Delete temp, return error "Write verification failed"               │
│ └─ Verification passes → Continue to Phase 3                                │
│                                                                             │
│ PHASE 3: ATOMIC COMMIT                                                      │
│ ├─ Perform atomic rename: {file}.tmp → {file}                               │
│ ├─ IF RENAME FAILS (permissions, locks):                                    │
│ │   └─ Keep temp file, return error, original unchanged                     │
│ ├─ Calculate checksum of final file                                         │
│ ├─ VERIFY: Final checksum == Temp checksum                                  │
│ ├─ IF MISMATCH (very rare):                                                 │
│ │   └─ Attempt rollback from backup, report critical error                  │
│ └─ Verification passes → Commit successful                                  │
│                                                                             │
│ PHASE 4: CLEANUP                                                            │
│ ├─ Delete {file}.tmp if still exists (edge case)                            │
│ └─ Update transaction manifest if applicable                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 7.3 Error Recovery Matrix

| Phase | Failure Point | State of Original | Recovery Action |
|-------|---------------|-------------------|-----------------|
| Phase 1 | In-memory validation | UNTOUCHED | Return errors, user fixes |
| Phase 2 | Temp write fails | UNTOUCHED | Delete temp if exists, retry or abort |
| Phase 2 | Read-back mismatch | UNTOUCHED | Delete temp, report write error |
| Phase 3 | Atomic rename fails | UNTOUCHED | Keep temp, user retries or manual fix |
| Phase 3 | Final verify fails | UNKNOWN | Rollback from backup immediately |
| Phase 4 | Cleanup fails | COMMITTED | Log warning, non-critical |

---

### 8. Summary: Safety Guarantees

**By implementing this specification, edit-module provides these guarantees:**

| Guarantee | Mechanism | Section |
|-----------|-----------|---------|
| **No Silent Data Loss** | Verified backups with checksums before any edit | Section 1 |
| **No Corrupt Writes** | Write-ahead validation, never write before validate | Section 7 |
| **No Partial States** | Transaction semantics, all-or-nothing for multi-file | Section 2 |
| **No Invalid YAML** | Mandatory syntax validation blocks all saves | Section 3 |
| **No Broken References** | Path validation with impact analysis | Section 4 |
| **No Infinite Loops** | Circular reference detection before commit | Section 5 |
| **Clear Validation Stages** | Validation (blocking) vs Compliance (advisory) | Section 6 |
| **User Control** | Explicit confirmation for all destructive actions | Throughout |
| **Recoverable State** | Rollback available until explicit completion | Section 1.4 |

---

### 9. Implementation Checklist for Step Files

**When implementing edit-module workflow steps, ensure:**

#### Step that performs edits MUST:
- [ ] Create backup with verification (Section 1.1)
- [ ] Use transaction manifest for multi-file edits (Section 2.2)
- [ ] Apply write-ahead validation pattern (Section 7.2)
- [ ] Never write invalid content to disk (Section 7.1)

#### Step that validates MUST:
- [ ] Run full validation checklist (Section 6.1)
- [ ] Run reference validation (Section 4.2)
- [ ] Run circular reference detection (Section 5.1)
- [ ] Block save on any validation failure

#### Step that runs compliance MUST:
- [ ] Clearly distinguish from validation (Section 6.3)
- [ ] Run compliance checklist (Section 6.2)
- [ ] Allow user to proceed despite compliance issues

#### Final completion step MUST:
- [ ] Confirm all validation passed
- [ ] Confirm user satisfaction explicitly
- [ ] Execute backup cleanup protocol (Section 1.3)
- [ ] Never delete backup before both confirmations

---

### Issue Resolution Matrix

| Issue ID | Severity | Status | Section |
|----------|----------|--------|---------|
| ISSUE-021 | CRITICAL | RESOLVED | Section 1 (Backup Strategy) |
| ISSUE-022 | CRITICAL | RESOLVED | Section 5 (Circular Reference Detection) |
| PARTY-004 | CRITICAL | RESOLVED | Section 1.3 (Backup Retention) |
| ISSUE-023 | HIGH | RESOLVED | Section 2 (Transaction Semantics) |
| ISSUE-024 | HIGH | RESOLVED | Section 3 (YAML Validation) |
| ISSUE-025 | HIGH | RESOLVED | Section 4 (Reference Validation) |
| ISSUE-014 | HIGH | RESOLVED | Section 6 (Validation vs Compliance) |
| PARTY-017 | HIGH | RESOLVED | Section 7 (Write-Ahead Validation) |
| PARTY-001 | HIGH | RESOLVED | Section 6.1 (Basic Validation Defined) |
| ISSUE-019 | LOW | RESOLVED | Section 6.1 (Validation Checklist) |

---

*Safety & Validation Specification completed: 2026-01-07*
*Total issues addressed: 10 (3 CRITICAL, 6 HIGH, 1 LOW)*

---

## Architecture & File Structure Specification

> **Resolution for:** ISSUE-001 (step-file architecture), ISSUE-002 (continuation/resume), ISSUE-003 (output document), ISSUE-004 (agent sub-types), ISSUE-005 (workflow formats), PARTY-007 (file paths)

### 1. Complete Step-File Architecture

**ISSUE-001 RESOLUTION: Step-file architecture definition**

The workflow uses a **multi-branch step architecture** to handle different edit targets while maintaining sequential discipline.

#### Directory Structure

```
_bmad/bmb/workflows/edit-module/
├── workflow.md                          # Entry point and routing
├── steps/
│   ├── step-01-init.md                  # Initialize, detect module, check continuation
│   ├── step-01b-continue.md             # Resume from interrupted workflow
│   ├── step-02-analyze.md               # Deep module analysis and inventory
│   ├── step-03-select.md                # Present edit menu, get user selection
│   │
│   ├── step-04a-agent-load.md           # Load target agent for editing
│   ├── step-04a1-agent-simple.md        # Edit simple agent type
│   ├── step-04a2-agent-expert.md        # Edit expert agent type (+ sidecar)
│   ├── step-04a3-agent-module.md        # Edit module agent type (integration)
│   ├── step-04a-agent-add.md            # Add new agent to module
│   ├── step-04a-agent-remove.md         # Remove agent from module
│   │
│   ├── step-04b-workflow-load.md        # Load target workflow for editing
│   ├── step-04b1-workflow-standalone.md # Edit standalone format (workflow.md + steps/)
│   ├── step-04b2-workflow-legacy.md     # Edit legacy format (workflow.yaml + workflow.xml)
│   ├── step-04b-workflow-add.md         # Add new workflow to module
│   ├── step-04b-workflow-remove.md      # Remove workflow from module
│   │
│   ├── step-04c-config.md               # Edit module.yaml configuration
│   ├── step-04d-docs.md                 # Edit README and documentation
│   │
│   ├── step-05-validate.md              # Validate changes against BMAD standards
│   ├── step-06-iterate.md               # Loop back for more edits or finish
│   └── step-07-complete.md              # Generate changelog, cleanup, celebrate
│
├── templates/
│   ├── edit-session.template.md         # Output document template
│   ├── changelog.template.md            # Edit summary template
│   ├── analysis-section.md              # Module analysis section
│   ├── agent-edit-section.md            # Agent edit tracking
│   ├── workflow-edit-section.md         # Workflow edit tracking
│   └── validation-section.md            # Validation results
│
└── data/
    ├── agent-type-detection.md          # How to detect agent sub-types
    ├── workflow-format-detection.md     # How to detect workflow formats
    ├── module-structure-reference.md    # Expected module structure
    └── validation-rules.md              # BMAD compliance rules
```

#### Step Flow Diagram

```
                    ┌─────────────────┐
                    │  workflow.md    │
                    │  (entry point)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ step-01-init.md │
                    │ (module select) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │ existing?    │              │
              ▼              │              │
   ┌──────────────────┐      │              │
   │step-01b-continue │      │              │
   │  (resume flow)   │      │              │
   └────────┬─────────┘      │              │
            │                │              │
            └───────►┌───────▼────────┐     │
                     │step-02-analyze │◄────┘
                     │(deep analysis) │
                     └───────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ step-03-select  │◄──────────────────┐
                    │ (edit menu)     │                   │
                    └────────┬────────┘                   │
                             │                            │
     ┌───────────┬───────────┼───────────┬───────────┐    │
     ▼           ▼           ▼           ▼           ▼    │
  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   │
  │Agent │   │Wkflw │   │Config│   │Docs  │   │Done  │   │
  │Branch│   │Branch│   │Edit  │   │Edit  │   │      │   │
  └──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘   │
     │          │          │          │          │        │
     ▼          ▼          ▼          ▼          │        │
  ┌──────────────────────────────────────┐       │        │
  │          step-05-validate            │       │        │
  │       (BMAD compliance check)        │       │        │
  └─────────────────┬────────────────────┘       │        │
                    │                            │        │
           ┌────────▼────────┐                   │        │
           │ step-06-iterate │───────────────────┘        │
           │ (more edits?)   │                            │
           └────────┬────────┘                            │
                    │ no more                             │
           ┌────────▼────────┐                            │
           │step-07-complete │◄───────────────────────────┘
           │(changelog/done) │
           └─────────────────┘
```

#### Step File Specifications

| Step | Lines | Purpose | Key Outputs |
|------|-------|---------|-------------|
| step-01-init | 120-150 | Module selection, existing session detection | Module path, session file |
| step-01b-continue | 100-130 | Resume from interrupted session | Restored state |
| step-02-analyze | 150-180 | Deep module analysis, inventory all components | Analysis section in output |
| step-03-select | 120-150 | Present categorized edit menu, get selection | User selection stored |
| step-04a-agent-load | 80-100 | Load agent, detect type, route to correct sub-step | Agent loaded, type identified |
| step-04a1-agent-simple | 100-130 | Edit simple agent (single-file) | Modified agent file |
| step-04a2-agent-expert | 120-150 | Edit expert agent + sidecar folder | Modified agent + sidecar |
| step-04a3-agent-module | 100-130 | Edit module agent (integration points) | Modified agent |
| step-04b-workflow-load | 80-100 | Load workflow, detect format, route correctly | Workflow loaded, format identified |
| step-04b1-workflow-standalone | 120-150 | Edit standalone format (workflow.md + steps/) | Modified workflow files |
| step-04b2-workflow-legacy | 100-130 | Edit legacy format (yaml + xml) | Modified legacy files |
| step-04c-config | 100-130 | Edit module.yaml settings | Modified config |
| step-04d-docs | 80-100 | Edit README and documentation | Modified docs |
| step-05-validate | 100-130 | Run BMAD compliance checks | Validation results |
| step-06-iterate | 60-80 | Ask for more edits, loop or proceed | Decision |
| step-07-complete | 100-130 | Generate changelog, cleanup backups, celebrate | Final outputs |

---

### 2. Continuation/Resume Mechanism

**ISSUE-002 RESOLUTION: Interrupted workflow handling**

#### State Tracking via Frontmatter

The output document (`edit-session-{module_name}-{sessionId}.md`) tracks all session state:

```yaml
---
# Session Identification
sessionId: "edit-2026-01-07-1430"
module_name: "bmm"
module_path: "_bmad/bmm"
user_name: "{user_name}"
started: "2026-01-07T14:30:00"
lastModified: "2026-01-07T16:45:00"

# Progress Tracking
stepsCompleted: [1, 2, 3]
lastStep: "step-03-select"
currentTarget: null  # Currently being edited: agent:analyst / workflow:create-prd / config / docs

# Edit Session State
editsPerformed:
  - type: "agent"
    target: "analyst.md"
    action: "modified"
    timestamp: "2026-01-07T15:00:00"
  - type: "workflow"
    target: "create-prd"
    action: "added"
    timestamp: "2026-01-07T16:00:00"

# Backup Tracking
backupsCreated:
  - original: "_bmad/bmm/agents/analyst.md"
    backup: "_bmad-output/backups/edit-2026-01-07-1430/analyst.md.bak"

# Validation State
lastValidation:
  timestamp: "2026-01-07T16:30:00"
  status: "passed"
  issues: []
---
```

#### step-01-init.md Continuation Detection

```markdown
### 2. Check for Existing Session

Look for existing edit sessions for this module:
- Search: `{output_folder}/edit-session-{module_name}*.md`
- If found and `stepsCompleted` is incomplete (doesn't include step 7):
  - **STOP** and route to `{continueFile}` immediately
  - Do not proceed with fresh initialization
```

#### step-01b-continue.md Resume Logic

```markdown
## CONTINUATION SEQUENCE:

### 1. Load Session State
- Read `{outputFile}` completely including frontmatter
- Extract: `stepsCompleted`, `lastStep`, `currentTarget`, `editsPerformed`

### 2. Present Resume Status
"Welcome back, {user_name}! I found your in-progress edit session for **{module_name}**.

**Session Status:**
- Started: {started}
- Last Activity: {lastModified}
- Edits Made: {editsPerformed.length}
- Last Step: {lastStep}

**Edits Completed So Far:**
{for each edit in editsPerformed}
- [{action}] {type}: {target} ({timestamp})
{end for}

Would you like to:
1. **Continue** from where you left off ({nextStep})
2. **Review** your edits before continuing
3. **Abandon** this session and start fresh"

### 3. Route Based on lastStep
- If lastStep == "step-01-init": Load step-02-analyze.md
- If lastStep == "step-02-analyze": Load step-03-select.md
- If lastStep == "step-03-select": Check currentTarget and load appropriate step-04x
- If lastStep starts with "step-04": Load step-05-validate.md
- If lastStep == "step-05-validate": Load step-06-iterate.md
- If lastStep == "step-06-iterate": Load step-03-select.md (loop)
```

#### Interrupted Mid-Edit Recovery

If `currentTarget` is set but the corresponding step-04x isn't in `stepsCompleted`:

```markdown
### 4. Handle Incomplete Edit
"I see you were in the middle of editing **{currentTarget}** when the session was interrupted.

The file may be in a partially edited state. Would you like to:
1. **Resume** the edit from where you left off
2. **Restore** from backup and start this edit fresh
3. **Skip** this edit and return to the main menu"
```

---

### 3. Output Document Specification

**ISSUE-003 RESOLUTION: Document structure, location, template**

#### Output Document Location

```
{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md
```

**Example:**
```
_bmad-output/bmb-creations/modules/bmm/edit-session-bmm-edit-2026-01-07-1430.md
```

#### Output Document Template

**File:** `templates/edit-session.template.md`

```markdown
---
# Session State (managed by workflow)
sessionId: ""
module_name: ""
module_path: ""
user_name: ""
started: ""
lastModified: ""
stepsCompleted: []
lastStep: ""
currentTarget: null
editsPerformed: []
backupsCreated: []
lastValidation: null
---

# Module Edit Session: {module_name}

## Session Info
- **Module:** {module_name}
- **Path:** {module_path}
- **User:** {user_name}
- **Started:** {started}

---

## Module Analysis

<!-- Populated by step-02-analyze.md -->

### Module Structure

| Component | Count | Details |
|-----------|-------|---------|
| Agents | | |
| Workflows | | |
| Config | | |
| Documentation | | |

### Component Inventory

#### Agents
<!-- List all agents with type detection -->

#### Workflows
<!-- List all workflows with format detection -->

#### Configuration
<!-- module.yaml summary -->

#### Documentation
<!-- README and other docs -->

---

## Edit Log

<!-- Populated incrementally by step-04x files -->

### Edit #{n}: {type} - {target}

**Action:** {add|modify|remove}
**Timestamp:** {timestamp}
**Reason:** {user_stated_reason}

#### Changes Made
<!-- Specific changes documented here -->

#### Backup
- Original: {original_path}
- Backup: {backup_path}

---

## Validation Results

<!-- Populated by step-05-validate.md -->

### Validation Run: {timestamp}

| Check | Status | Details |
|-------|--------|---------|
| Agent Structure | | |
| Workflow Compliance | | |
| Config Valid | | |
| Cross-References | | |

### Issues Found
<!-- If any -->

### Recommendations
<!-- If any -->

---

## Session Changelog

<!-- Generated by step-07-complete.md -->

### Summary
- **Total Edits:** {count}
- **Validation Status:** {passed|failed}
- **Session Duration:** {duration}

### Changes
1. {change_1}
2. {change_2}
...

### Files Modified
- {file_1}
- {file_2}
...
```

---

### 4. Agent Sub-Type Handling

**ISSUE-004 RESOLUTION: Three agent types (Simple, Expert, Module)**

#### Agent Type Detection

**File:** `data/agent-type-detection.md`

```markdown
## Agent Type Detection Algorithm

### Step 1: Check for Sidecar Folder

Look for: `{agent_path}-sidecar/` or `{agent_name}-sidecar/`

- **If sidecar exists** -> Agent is **Expert** type
- **If no sidecar** -> Continue to Step 2

### Step 2: Check for Module Integration Markers

Scan agent file for these patterns:

# Module Agent Indicators
- References to module-specific config: `{project-root}/_bmad/{module}/config.yaml`
- Uses module workflows: `workflow="{project-root}/_bmad/{module}/workflows/..."`
- Has module coordination: references to other agents in same module
- Contains module-specific critical_actions

- **If module markers found** -> Agent is **Module** type
- **If no module markers** -> Agent is **Simple** type

### Detection Result Structure

agentType: "simple" | "expert" | "module"
sidecarPath: null | "{path}"
moduleContext:
  moduleName: null | "{name}"
  modulePath: null | "{path}"
  relatedAgents: []
  usedWorkflows: []
```

#### Type-Specific Edit Step Routing

In `step-04a-agent-load.md`:

```markdown
### 3. Route to Type-Specific Editor

Based on detected `{agentType}`:

- **IF simple:** Load, read entire file, then execute `{workflow_path}/steps/step-04a1-agent-simple.md`
- **IF expert:** Load, read entire file, then execute `{workflow_path}/steps/step-04a2-agent-expert.md`
- **IF module:** Load, read entire file, then execute `{workflow_path}/steps/step-04a3-agent-module.md`
```

#### Type-Specific Edit Considerations

| Type | Special Handling |
|------|------------------|
| **Simple** | Single file edit, validate inline prompts fit ~250 lines |
| **Expert** | Edit agent file + manage sidecar folder (memories.md, instructions.md, workflows/, knowledge/) |
| **Module** | Maintain module integration (config refs, workflow refs, agent coordination) |

---

### 5. Workflow Format Handling

**ISSUE-005 RESOLUTION: Standalone vs Legacy formats**

#### Workflow Format Detection

**File:** `data/workflow-format-detection.md`

```markdown
## Workflow Format Detection Algorithm

### Check 1: Look for workflow.md (Standalone Format)

Path: `{workflow_path}/workflow.md`

**Standalone format indicators:**
- File exists: `workflow.md`
- Contains frontmatter with `name:` and `description:`
- Has `steps/` subdirectory with `step-*.md` files
- No `workflow.yaml` in same directory

**Structure:**
workflow-name/
├── workflow.md
├── steps/
│   ├── step-01-*.md
│   └── step-0N-*.md
├── templates/  (optional)
└── data/       (optional)

### Check 2: Look for workflow.yaml (Legacy Format)

Path: `{workflow_path}/workflow.yaml`

**Legacy format indicators:**
- File exists: `workflow.yaml`
- Requires `_bmad/core/tasks/workflow.xml` for execution
- May have `instructions.md` for content
- Uses XML handler pattern

**Structure:**
workflow-name/
├── workflow.yaml
├── instructions.md  (optional)
└── data/            (optional)

### Detection Result Structure

workflowFormat: "standalone" | "legacy" | "mixed"
mainFile: "{path}"
stepsDirectory: null | "{path}"
stepFiles: []
templateDirectory: null | "{path}"
dataDirectory: null | "{path}"
requiresXmlHandler: false | true
```

#### Format-Specific Edit Step Routing

In `step-04b-workflow-load.md`:

```markdown
### 3. Route to Format-Specific Editor

Based on detected `{workflowFormat}`:

- **IF standalone:** Load, read entire file, then execute `{workflow_path}/steps/step-04b1-workflow-standalone.md`
- **IF legacy:** Load, read entire file, then execute `{workflow_path}/steps/step-04b2-workflow-legacy.md`
- **IF mixed:** Warn user about partial migration state, offer to complete migration or edit as-is
```

#### Format-Specific Edit Considerations

| Format | Special Handling |
|--------|------------------|
| **Standalone** | Edit workflow.md + individual step files, maintain frontmatter consistency, validate step sequencing |
| **Legacy** | Edit workflow.yaml structure, maintain XML handler compatibility, warn about deprecation |
| **Mixed** | Identify which parts are migrated, offer migration completion |

---

### 6. Concrete File Paths for All Artifacts

**PARTY-007 RESOLUTION: Explicit file paths**

#### Workflow Installation Path

```
{project-root}/_bmad/bmb/workflows/edit-module/
```

**Full path example:**
```
C:\Users\Trevor Leigh\Desktop\pcmrp_migration\_bmad\bmb\workflows\edit-module\
```

#### All Workflow Files (Complete Inventory)

| File | Path | Purpose |
|------|------|---------|
| **workflow.md** | `_bmad/bmb/workflows/edit-module/workflow.md` | Entry point |
| **step-01-init.md** | `_bmad/bmb/workflows/edit-module/steps/step-01-init.md` | Initialize |
| **step-01b-continue.md** | `_bmad/bmb/workflows/edit-module/steps/step-01b-continue.md` | Resume |
| **step-02-analyze.md** | `_bmad/bmb/workflows/edit-module/steps/step-02-analyze.md` | Analyze |
| **step-03-select.md** | `_bmad/bmb/workflows/edit-module/steps/step-03-select.md` | Menu |
| **step-04a-agent-load.md** | `_bmad/bmb/workflows/edit-module/steps/step-04a-agent-load.md` | Load agent |
| **step-04a1-agent-simple.md** | `_bmad/bmb/workflows/edit-module/steps/step-04a1-agent-simple.md` | Simple agent |
| **step-04a2-agent-expert.md** | `_bmad/bmb/workflows/edit-module/steps/step-04a2-agent-expert.md` | Expert agent |
| **step-04a3-agent-module.md** | `_bmad/bmb/workflows/edit-module/steps/step-04a3-agent-module.md` | Module agent |
| **step-04a-agent-add.md** | `_bmad/bmb/workflows/edit-module/steps/step-04a-agent-add.md` | Add agent |
| **step-04a-agent-remove.md** | `_bmad/bmb/workflows/edit-module/steps/step-04a-agent-remove.md` | Remove agent |
| **step-04b-workflow-load.md** | `_bmad/bmb/workflows/edit-module/steps/step-04b-workflow-load.md` | Load workflow |
| **step-04b1-workflow-standalone.md** | `_bmad/bmb/workflows/edit-module/steps/step-04b1-workflow-standalone.md` | Standalone format |
| **step-04b2-workflow-legacy.md** | `_bmad/bmb/workflows/edit-module/steps/step-04b2-workflow-legacy.md` | Legacy format |
| **step-04b-workflow-add.md** | `_bmad/bmb/workflows/edit-module/steps/step-04b-workflow-add.md` | Add workflow |
| **step-04b-workflow-remove.md** | `_bmad/bmb/workflows/edit-module/steps/step-04b-workflow-remove.md` | Remove workflow |
| **step-04c-config.md** | `_bmad/bmb/workflows/edit-module/steps/step-04c-config.md` | Config edit |
| **step-04d-docs.md** | `_bmad/bmb/workflows/edit-module/steps/step-04d-docs.md` | Docs edit |
| **step-05-validate.md** | `_bmad/bmb/workflows/edit-module/steps/step-05-validate.md` | Validate |
| **step-06-iterate.md** | `_bmad/bmb/workflows/edit-module/steps/step-06-iterate.md` | Loop/finish |
| **step-07-complete.md** | `_bmad/bmb/workflows/edit-module/steps/step-07-complete.md` | Complete |

#### Template Files

| File | Path |
|------|------|
| **edit-session.template.md** | `_bmad/bmb/workflows/edit-module/templates/edit-session.template.md` |
| **changelog.template.md** | `_bmad/bmb/workflows/edit-module/templates/changelog.template.md` |
| **analysis-section.md** | `_bmad/bmb/workflows/edit-module/templates/analysis-section.md` |
| **agent-edit-section.md** | `_bmad/bmb/workflows/edit-module/templates/agent-edit-section.md` |
| **workflow-edit-section.md** | `_bmad/bmb/workflows/edit-module/templates/workflow-edit-section.md` |
| **validation-section.md** | `_bmad/bmb/workflows/edit-module/templates/validation-section.md` |

#### Data Reference Files

| File | Path |
|------|------|
| **agent-type-detection.md** | `_bmad/bmb/workflows/edit-module/data/agent-type-detection.md` |
| **workflow-format-detection.md** | `_bmad/bmb/workflows/edit-module/data/workflow-format-detection.md` |
| **module-structure-reference.md** | `_bmad/bmb/workflows/edit-module/data/module-structure-reference.md` |
| **validation-rules.md** | `_bmad/bmb/workflows/edit-module/data/validation-rules.md` |

#### Output Document Paths

| Output | Path Pattern | Example |
|--------|--------------|---------|
| **Edit Session** | `{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md` | `_bmad-output/bmb-creations/modules/bmm/edit-session-bmm-edit-2026-01-07-1430.md` |
| **Changelog** | `{module_path}/CHANGELOG.md` (appended) | `_bmad/bmm/CHANGELOG.md` |
| **Backups** | `{module_path}/.backup/{timestamp}/` | `_bmad/bmm/.backup/2026-01-07_14-30-00/` |

#### External Dependencies (Referenced)

| Dependency | Path | Purpose |
|------------|------|---------|
| **BMB Config** | `{project-root}/_bmad/bmb/config.yaml` | User settings |
| **Advanced Elicitation** | `{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml` | Deep discovery |
| **Party Mode** | `{project-root}/_bmad/core/workflows/party-mode/workflow.md` | Multi-agent |
| **Workflow XML Handler** | `{project-root}/_bmad/core/tasks/workflow.xml` | Legacy workflow execution |

---

### 7. Implementation Checklist

Based on this specification, the following files need to be created:

#### Phase 1: Core Structure (11 files)
- [ ] `workflow.md`
- [ ] `steps/step-01-init.md`
- [ ] `steps/step-01b-continue.md`
- [ ] `steps/step-02-analyze.md`
- [ ] `steps/step-03-select.md`
- [ ] `steps/step-05-validate.md`
- [ ] `steps/step-06-iterate.md`
- [ ] `steps/step-07-complete.md`
- [ ] `templates/edit-session.template.md`
- [ ] `data/module-structure-reference.md`
- [ ] `data/validation-rules.md`

#### Phase 2: Agent Editing (7 files)
- [ ] `steps/step-04a-agent-load.md`
- [ ] `steps/step-04a1-agent-simple.md`
- [ ] `steps/step-04a2-agent-expert.md`
- [ ] `steps/step-04a3-agent-module.md`
- [ ] `steps/step-04a-agent-add.md`
- [ ] `steps/step-04a-agent-remove.md`
- [ ] `data/agent-type-detection.md`

#### Phase 3: Workflow Editing (6 files)
- [ ] `steps/step-04b-workflow-load.md`
- [ ] `steps/step-04b1-workflow-standalone.md`
- [ ] `steps/step-04b2-workflow-legacy.md`
- [ ] `steps/step-04b-workflow-add.md`
- [ ] `steps/step-04b-workflow-remove.md`
- [ ] `data/workflow-format-detection.md`

#### Phase 4: Config & Docs (2 files)
- [ ] `steps/step-04c-config.md`
- [ ] `steps/step-04d-docs.md`

#### Phase 5: Templates (5 files)
- [ ] `templates/changelog.template.md`
- [ ] `templates/analysis-section.md`
- [ ] `templates/agent-edit-section.md`
- [ ] `templates/workflow-edit-section.md`
- [ ] `templates/validation-section.md`

**Total Files: 31**

---

### 8. Architecture Issue Resolution Summary

| Issue ID | Status | Resolution |
|----------|--------|------------|
| ISSUE-001 | RESOLVED | Complete step-file architecture with 21 step files defined |
| ISSUE-002 | RESOLVED | Continuation via frontmatter state + step-01b-continue.md |
| ISSUE-003 | RESOLVED | Output at `{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md` |
| ISSUE-004 | RESOLVED | Three agent types detected and routed to type-specific steps (Simple/Expert/Module) |
| ISSUE-005 | RESOLVED | Standalone vs Legacy formats detected and routed to format-specific steps |
| PARTY-007 | RESOLVED | All 31 files have explicit paths specified with full inventory tables |

---

*Architecture & File Structure Specification completed: 2026-01-07*
*Total issues addressed: 6 (3 CRITICAL, 3 HIGH)*

---
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

---

## Round 2 Fixes: Critical & High Priority

This section addresses the critical and high-priority issues identified during Round 2 analysis.

### R2-FIX-001: Variable Resolution Specification

**Addresses:** R2-ISSUE-003 (CRITICAL) - Variable Resolution Mechanism Undefined

#### 1.1 Complete Variable Inventory

| Variable | Source | Scope | Description |
|----------|--------|-------|-------------|
| `{project-root}` | Environment | Global | Repository root directory (auto-detected from `.git` or config) |
| `{module_path}` | Runtime | Session | Absolute path to currently loaded module (e.g., `_bmad/bmm/`) |
| `{module_name}` | Runtime | Session | Name of current module from `module.yaml` (e.g., `bmm`) |
| `{workflow_path}` | Runtime | Step | Path to currently executing workflow (e.g., `_bmad/bmb/workflows/edit-module/`) |
| `{bmb_creations_output_folder}` | Config | Global | Output directory for BMB artifacts (default: `_bmad-output/bmb-creations/`) |
| `{user_name}` | Environment | Session | Current user's name (from git config, env var, or prompt) |
| `{sessionId}` | Runtime | Session | Unique session identifier (format: `edit-YYYY-MM-DD-HHMM`) |
| `{timestamp}` | Runtime | Operation | ISO timestamp for current operation (format: `YYYY-MM-DD_HH-MM-SS`) |
| `{file}` | Runtime | Operation | Currently targeted file path |
| `{component-name}` | Runtime | Operation | Name of component being edited |

#### 1.2 Variable Definition Sources

**Priority Order (highest to lowest):**

```
1. Runtime Context (current operation state)
2. Session State (loaded module/workflow info)
3. Project Config (`{project-root}/_bmad/bmb/config.yaml`)
4. Environment Variables (BMB_PROJECT_ROOT, BMB_OUTPUT_FOLDER, etc.)
5. Auto-Detection (git root, current directory)
6. User Prompt (as last resort)
```

**Source Definitions:**

| Source | Location | Variables Defined |
|--------|----------|-------------------|
| **Runtime Context** | In-memory state | `{file}`, `{timestamp}`, `{component-name}` |
| **Session State** | Edit session YAML | `{module_path}`, `{module_name}`, `{sessionId}`, `{user_name}` |
| **Project Config** | `_bmad/bmb/config.yaml` | `{bmb_creations_output_folder}` |
| **Environment** | System env vars | `{project-root}` (via `BMB_PROJECT_ROOT`) |
| **Auto-Detection** | File system | `{project-root}` (git root fallback) |

#### 1.3 Resolution Algorithm

```
VARIABLE RESOLUTION ALGORITHM:
────────────────────────────────────────────────────────────────

INPUT: Variable name (e.g., "{module_path}")
OUTPUT: Resolved value OR error

STEP 1: Check Runtime Context
├─ IF variable in runtime_context → RETURN value
└─ ELSE → Continue

STEP 2: Check Session State
├─ IF session_file exists AND variable in session → RETURN value
└─ ELSE → Continue

STEP 3: Check Project Config
├─ IF config_file exists AND variable defined → RETURN value
└─ ELSE → Continue

STEP 4: Check Environment Variables
├─ Map variable to env var name:
│   {project-root}              → BMB_PROJECT_ROOT
│   {bmb_creations_output_folder} → BMB_OUTPUT_FOLDER
│   {user_name}                 → BMB_USER_NAME or USER or USERNAME
├─ IF env var set → RETURN value
└─ ELSE → Continue

STEP 5: Auto-Detection (for supported variables only)
├─ {project-root}: Find nearest parent with .git/ directory
├─ {user_name}: git config user.name
├─ {timestamp}: current UTC time
├─ {sessionId}: generate "edit-{date}-{time}"
├─ IF auto-detected → RETURN value
└─ ELSE → Continue

STEP 6: Handle Undefined Variable
├─ IF variable is REQUIRED for current operation:
│   └─ PROMPT user: "Please provide value for {variable}:"
│   └─ IF user provides → CACHE and RETURN value
│   └─ IF user cancels → ABORT operation
├─ IF variable has DEFAULT:
│   └─ RETURN default value
└─ ELSE → ERROR: "Variable {variable} is undefined and has no default"
```

#### 1.4 Undefined Variable Behavior

| Variable | Required? | Default | On Undefined |
|----------|-----------|---------|--------------|
| `{project-root}` | YES | Auto-detect | ABORT with error |
| `{module_path}` | YES | None | ABORT - must load module first |
| `{module_name}` | YES | None | ABORT - must load module first |
| `{workflow_path}` | YES | Current workflow dir | Use executing workflow's path |
| `{bmb_creations_output_folder}` | NO | `_bmad-output/bmb-creations/` | Use default |
| `{user_name}` | NO | `unknown-user` | Use default, warn user |
| `{sessionId}` | YES | Auto-generate | Generate from timestamp |
| `{timestamp}` | YES | Auto-generate | Generate current time |

#### 1.5 Variable Substitution in Content

**String Interpolation Rules:**

```
1. Variables use format: {variable_name}
2. Literal braces: Escape with double braces {{literal}}
3. Nested variables: NOT supported (resolve inner first, then outer)
4. Case sensitivity: Variables are case-sensitive ({module_path} ≠ {MODULE_PATH})
5. Unknown variables: Leave unchanged and log warning
```

**Example:**

```yaml
# Before substitution
backup_path: "{module_path}/.backup/{timestamp}/"
session_file: "{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md"

# After substitution (example values)
backup_path: "_bmad/bmm/.backup/2026-01-07_14-30-00/"
session_file: "_bmad-output/bmb-creations/modules/bmm/edit-session-bmm-edit-2026-01-07-1430.md"
```

---

### R2-FIX-002: BMAD Format Rules Definition

**Addresses:** R2-ISSUE-004 (CRITICAL) - BMAD Compliance Rules Undefined

#### 2.1 BMAD Agent Format Rules

A valid BMAD agent file MUST conform to these rules:

**Structural Requirements:**

| Rule ID | Rule | Severity | Check |
|---------|------|----------|-------|
| AGT-001 | File must be markdown (`.md` extension) | CRITICAL | Extension check |
| AGT-002 | Optional YAML frontmatter must be valid YAML | HIGH | YAML parse test |
| AGT-003 | Must have exactly one H1 heading (# Agent Name) | CRITICAL | Regex match |
| AGT-004 | H1 must appear before any other content | HIGH | Line position check |
| AGT-005 | Must contain persona/role section (H2 or H3) | HIGH | Section search |
| AGT-006 | Must contain capabilities section | MEDIUM | Section search |
| AGT-007 | Tool references must be valid tool names | MEDIUM | Tool registry lookup |
| AGT-008 | Internal links must resolve | LOW | Link resolution |

**Content Requirements:**

| Rule ID | Rule | Severity | Check |
|---------|------|----------|-------|
| AGT-101 | Persona must be substantive (>50 characters) | MEDIUM | Length check |
| AGT-102 | Capabilities must be listed (bullet or numbered) | MEDIUM | Format check |
| AGT-103 | No duplicate section headings at same level | LOW | Heading analysis |
| AGT-104 | No empty sections | LOW | Content check |

**Validation Regex Patterns:**

```
H1_HEADING: ^# (?!#).+$
H2_HEADING: ^## (?!#).+$
YAML_FRONTMATTER: ^---\n[\s\S]*?\n---
TOOL_REFERENCE: \b(mcp__\w+__\w+|Read|Write|Edit|Bash|Glob|Grep)\b
INTERNAL_LINK: \[.*?\]\(((?!https?://)[^)]+)\)
```

#### 2.2 BMAD Workflow Format Rules

A valid BMAD workflow MUST conform to these rules:

**Directory Structure Requirements:**

| Rule ID | Rule | Severity | Check |
|---------|------|----------|-------|
| WFL-001 | Must have `workflow.md` OR `workflow.yaml` at root | CRITICAL | File exists |
| WFL-002 | If `steps/` exists, must contain step files | HIGH | Directory contents |
| WFL-003 | Step files must be numbered (`step-NN-name.md`) | MEDIUM | Naming pattern |
| WFL-004 | Step numbers must be sequential (no gaps >1) | LOW | Number sequence |
| WFL-005 | If `data/` exists, referenced files must exist | MEDIUM | File references |

**Workflow.md Requirements:**

| Rule ID | Rule | Severity | Check |
|---------|------|----------|-------|
| WFL-101 | Must have H1 heading | CRITICAL | Heading check |
| WFL-102 | Must describe workflow purpose | HIGH | Content presence |
| WFL-103 | Step references must match actual step files | HIGH | Cross-reference |
| WFL-104 | Internal anchors must resolve | MEDIUM | Anchor resolution |

**Workflow.yaml Requirements:**

| Rule ID | Rule | Severity | Check |
|---------|------|----------|-------|
| WFL-201 | Must be valid YAML | CRITICAL | YAML parse |
| WFL-202 | Must have `name` field | CRITICAL | Field presence |
| WFL-203 | Must have `description` field | HIGH | Field presence |
| WFL-204 | `steps` array elements must reference existing files | HIGH | File resolution |
| WFL-205 | `tools` array must contain valid tool names | MEDIUM | Tool registry |

#### 2.3 BMAD Module Format Rules

A valid BMAD module MUST conform to these rules:

**Directory Structure:**

| Rule ID | Rule | Severity | Check |
|---------|------|----------|-------|
| MOD-001 | Must have `module.yaml` at root | CRITICAL | File exists |
| MOD-002 | If `agents/` exists, must contain valid agent files | HIGH | Agent validation |
| MOD-003 | If `workflows/` exists, must contain valid workflow dirs | HIGH | Workflow validation |
| MOD-004 | README.md recommended but not required | LOW | File exists |

**Module.yaml Requirements:**

| Rule ID | Rule | Severity | Check |
|---------|------|----------|-------|
| MOD-101 | Must be valid YAML | CRITICAL | YAML parse |
| MOD-102 | Must have `name` field | CRITICAL | Field presence |
| MOD-103 | Must have `version` field (semver format) | HIGH | Semver regex |
| MOD-104 | Must have `description` field | HIGH | Field presence |
| MOD-105 | `agents` array must match actual agent files | HIGH | Cross-reference |
| MOD-106 | `workflows` array must match actual workflow dirs | HIGH | Cross-reference |
| MOD-107 | `dependencies` must reference valid modules | MEDIUM | Module lookup |

#### 2.4 Compliance Check Algorithm

```
BMAD COMPLIANCE CHECK:
────────────────────────────────────────────────────────────────

INPUT: Path to component (agent file, workflow dir, or module dir)
OUTPUT: ComplianceResult { passed: bool, issues: Issue[], severity: string }

STEP 1: Determine Component Type
├─ IF path ends with .md AND parent is agents/ → AGENT
├─ IF path contains workflow.md or workflow.yaml → WORKFLOW
├─ IF path contains module.yaml → MODULE
└─ ELSE → ERROR: "Unknown component type"

STEP 2: Load Applicable Rules
├─ agent → AGT-* rules
├─ workflow → WFL-* rules
├─ module → MOD-* rules (includes recursive check of agents/workflows)

STEP 3: Execute Each Rule
FOR each rule in applicable_rules:
├─ result = execute_check(rule, component)
├─ IF result.failed:
│   └─ issues.append(Issue(rule.id, rule.severity, result.message))
└─ Continue

STEP 4: Calculate Overall Result
├─ IF any CRITICAL issue → passed = false, severity = "CRITICAL"
├─ ELIF any HIGH issue → passed = false, severity = "HIGH"
├─ ELIF any MEDIUM issue → passed = true (warn), severity = "MEDIUM"
├─ ELSE → passed = true, severity = "CLEAN"

RETURN ComplianceResult(passed, issues, severity)
```

#### 2.5 Compliance Check Output Format

```
BMAD Compliance Check: {component_name}
═══════════════════════════════════════════════════════════════

Status: ❌ FAILED (2 CRITICAL, 1 HIGH, 0 MEDIUM, 0 LOW)

CRITICAL Issues:
  [AGT-001] File must be markdown extension
            Found: analyst.txt
            Fix: Rename to analyst.md

  [AGT-003] Must have exactly one H1 heading
            Found: 0 H1 headings
            Fix: Add "# Agent Name" at top of file

HIGH Issues:
  [AGT-005] Must contain persona/role section
            Found: No section matching /persona|role/i
            Fix: Add "## Persona" or "## Role" section

─────────────────────────────────────────────────────────────────
Recommendation: Fix CRITICAL issues before proceeding with edit.
```

---

### R2-FIX-003: Backup Location Consolidation

**Addresses:** R2-ISSUE-001 (HIGH) - Backup Location Inconsistency

#### 3.1 Decision: Single Backup Location

**CHOSEN LOCATION:** `{module_path}/.backup/{timestamp}/`

**Rationale:**

| Factor | `{module_path}/.backup/` | `{bmb_creations_output_folder}/backups/` | Decision |
|--------|--------------------------|------------------------------------------|----------|
| **Proximity** | Same directory as edited files | Separate output folder | Module-local wins: easier to find |
| **Git Integration** | Can be .gitignored at module level | Requires project-level .gitignore | Module-local wins: cleaner |
| **Recovery** | Backup right next to originals | Must navigate to separate location | Module-local wins: faster recovery |
| **Cleanup** | Delete when module deleted | Persists as orphan | Module-local wins: automatic cleanup |
| **Visibility** | Hidden (`.backup`) but discoverable | Visible in output folder | Tie: both discoverable |

**Conclusion:** Module-local backups (`{module_path}/.backup/`) provide better UX for recovery scenarios and automatic cleanup. The `{bmb_creations_output_folder}` location was intended for session artifacts, not safety backups.

#### 3.2 Updated Backup Specification

**Canonical Backup Location:**

```
{module_path}/.backup/{timestamp}/
```

**Example:**

```
_bmad/bmm/.backup/2026-01-07_14-30-00/
├── manifest.json          # Backup metadata
├── agents/
│   └── analyst.md         # Backed up agent file
└── workflows/
    └── create-prd/
        └── workflow.md    # Backed up workflow file
```

**Deprecation Notice:**

The following path pattern is **DEPRECATED** and should NOT be used:
```
{bmb_creations_output_folder}/backups/{sessionId}/{filename}.bak  # DEPRECATED
```

#### 3.3 Updated File Path Reference Table

| Artifact | Location | Example |
|----------|----------|---------|
| **Edit Session** | `{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md` | `_bmad-output/bmb-creations/modules/bmm/edit-session-bmm-edit-2026-01-07-1430.md` |
| **Changelog** | `{module_path}/CHANGELOG.md` | `_bmad/bmm/CHANGELOG.md` |
| **Backups** | `{module_path}/.backup/{timestamp}/` | `_bmad/bmm/.backup/2026-01-07_14-30-00/` |
| **Backup Manifest** | `{module_path}/.backup/manifest.json` | `_bmad/bmm/.backup/manifest.json` |

---

### R2-FIX-004: Phasing Terminology Alignment

**Addresses:** R2-ISSUE-002 (HIGH) - Phasing Schemes Misalignment

#### 4.1 Terminology Definitions

The specification uses three distinct organizational concepts that were confusingly named:

| Old Term | New Term | Purpose | Scope |
|----------|----------|---------|-------|
| "MVP Phases 1-3" | **Capability Tiers** | Feature maturity levels | Product roadmap |
| "Implementation Batches 1-5" | **Work Packages** | Logical groupings of related work | Planning |
| "Sprints 1-4" | **Delivery Sprints** | Time-boxed implementation periods | Execution |

#### 4.2 Capability Tiers (formerly "MVP Phases")

**Purpose:** Define which features are essential vs. enhanced vs. advanced.

| Tier | Name | Description | Deliverable |
|------|------|-------------|-------------|
| **Tier 1** | Core | Minimum viable edit capability | Basic edit/validate/save |
| **Tier 2** | Enhanced | Full edit operations | Add/remove/duplicate |
| **Tier 3** | Advanced | Power user features | Rename/batch/cross-module |

#### 4.3 Work Packages (formerly "Implementation Batches")

**Purpose:** Group related implementation work for planning.

| Package | Name | Contains | Tier Mapping |
|---------|------|----------|--------------|
| **WP-1** | Foundation | Lock, backup, error handling | Tier 1 |
| **WP-2** | Core Edit | Agent/workflow editing | Tier 1 |
| **WP-3** | Validation | BMAD compliance, real-time checks | Tier 1 |
| **WP-4** | Extended Ops | Add/remove/duplicate | Tier 2 |
| **WP-5** | Advanced | Rename/batch/cross-module | Tier 3 |

#### 4.4 Delivery Sprints (formerly "Sprints")

**Purpose:** Time-boxed implementation periods (typically 1-2 weeks each).

| Sprint | Focus | Work Packages | Story Points |
|--------|-------|---------------|--------------|
| **DS-1** | Foundation | WP-1 | 8 |
| **DS-2** | Core Edit | WP-2 | 11 |
| **DS-3** | Validation | WP-3 | 5 |
| **DS-4** | Extended | WP-4, WP-5 | 8 |

#### 4.5 Mapping Table

| Capability Tier | Work Package(s) | Delivery Sprint(s) | Total Points |
|-----------------|-----------------|--------------------|--------------|
| Tier 1: Core | WP-1, WP-2, WP-3 | DS-1, DS-2, DS-3 | 24 |
| Tier 2: Enhanced | WP-4 | DS-4 (partial) | 5 |
| Tier 3: Advanced | WP-5 | DS-4 (partial) + future | 3+ |

---

### R2-FIX-005: Module Discovery Algorithm

**Addresses:** R2-ISSUE-005 (HIGH) - Module Discovery Algorithm Undefined

#### 5.1 Module Discovery Search Locations

**Search Order (first match wins for conflicts):**

| Priority | Location Pattern | Description |
|----------|-----------------|-------------|
| 1 | `{project-root}/_bmad/*/module.yaml` | Standard BMAD module location |
| 2 | `{project-root}/_bmad-modules/*/module.yaml` | Alternative module directory |
| 3 | `{project-root}/*/module.yaml` (if configured) | Custom paths from config |

#### 5.2 Valid Module Pattern

A directory is recognized as a valid BMAD module if it contains:

```
REQUIRED:
  module.yaml           # Module manifest (MUST exist)
    └─ name: string     # MUST have name field
    └─ version: string  # MUST have version field

OPTIONAL (but expected):
  agents/               # Agent files directory
  workflows/            # Workflow directories
  README.md             # Module documentation
  config.yaml           # Module-specific config
```

**Module Detection Pseudocode:**

```
is_valid_module(path):
    module_yaml = path / "module.yaml"
    IF NOT module_yaml.exists():
        RETURN false

    TRY:
        manifest = yaml.parse(module_yaml)
    EXCEPT YAMLError:
        RETURN false  # Invalid YAML

    IF "name" NOT IN manifest:
        RETURN false
    IF "version" NOT IN manifest:
        RETURN false

    RETURN true
```

#### 5.3 Module Discovery Algorithm

```
DISCOVER MODULES:
────────────────────────────────────────────────────────────────

INPUT: project_root (from {project-root} variable)
OUTPUT: List[Module] sorted by name

modules = []

# Phase 1: Search standard locations
FOR search_path IN [
    "{project-root}/_bmad/",
    "{project-root}/_bmad-modules/"
]:
    IF search_path.exists():
        FOR dir IN search_path.list_directories():
            IF is_valid_module(dir):
                modules.append(load_module_info(dir))

# Phase 2: Search custom paths (from config)
custom_paths = load_config("module_search_paths", default=[])
FOR custom_path IN custom_paths:
    resolved = resolve_path(custom_path)
    IF resolved.exists() AND is_valid_module(resolved):
        modules.append(load_module_info(resolved))

# Phase 3: De-duplicate by name (first occurrence wins)
seen_names = set()
unique_modules = []
FOR module IN modules:
    IF module.name NOT IN seen_names:
        unique_modules.append(module)
        seen_names.add(module.name)

# Phase 4: Sort alphabetically
RETURN sorted(unique_modules, key=lambda m: m.name)
```

#### 5.4 Module Information Structure

```yaml
# Loaded module information structure
name: "bmm"                           # From module.yaml name field
version: "1.0.0"                      # From module.yaml version field
path: "_bmad/bmm/"                    # Absolute or relative path
description: "BMAD Method Module"     # From module.yaml description
agent_count: 9                        # Count of files in agents/
workflow_count: 12                    # Count of dirs in workflows/
```

#### 5.5 Display Format

**Module Selection Menu:**

```
Available BMAD Modules
══════════════════════════════════════════════════════════════

 #  │ Module Name │ Version │ Agents │ Workflows │ Path
────┼─────────────┼─────────┼────────┼───────────┼──────────────────
 1  │ bmad-core   │ 2.0.0   │   3    │     5     │ _bmad/core/
 2  │ bmb         │ 1.2.0   │   3    │     4     │ _bmad/bmb/
 3  │ bmm         │ 1.0.0   │   9    │    12     │ _bmad/bmm/

Select module (1-3) or enter path: _
```

**No Modules Found Message:**

```
No BMAD modules found in standard locations.

Searched:
  - _bmad/*/module.yaml
  - _bmad-modules/*/module.yaml

Options:
  [P] Provide path to module directly
  [C] Create new module (delegates to create-module workflow)
  [Q] Quit
```

---

### Round 2 Fix Summary

| Issue ID | Severity | Status | Fix Section |
|----------|----------|--------|-------------|
| R2-ISSUE-003 | CRITICAL | RESOLVED | R2-FIX-001: Variable Resolution |
| R2-ISSUE-004 | CRITICAL | RESOLVED | R2-FIX-002: BMAD Format Rules |
| R2-ISSUE-001 | HIGH | RESOLVED | R2-FIX-003: Backup Location |
| R2-ISSUE-002 | HIGH | RESOLVED | R2-FIX-004: Phasing Terminology |
| R2-ISSUE-005 | HIGH | RESOLVED | R2-FIX-005: Module Discovery |

---

*Round 2 Critical & High Priority Fixes completed: 2026-01-07*
*Total issues resolved: 5 (2 CRITICAL, 3 HIGH)*

---

## Round 2 Fixes: Medium & Low Priority

*Analysis Date: 2026-01-07*
*Issues Addressed: 7 (5 MEDIUM, 2 LOW)*

This section addresses medium and low priority issues identified in Round 2 adversarial analysis that require clarification, specification, or simplification.

---

### R2-FIX-006: Step Name to stepsCompleted Index Mapping

**Addresses:** R2-ISSUE-006 (MEDIUM) - Step Numbering vs stepsCompleted Array

**Issue:** Output document uses `stepsCompleted: [1, 2, 3]` (numeric) but steps have names like `step-01b-continue`, `step-04a1-agent-simple`. Mapping is unclear.

**Resolution:** Define explicit step index mapping table.

#### Step Index Registry

| Index | Step File | Step Name | Purpose |
|-------|-----------|-----------|---------|
| 1 | `step-01-init.md` | init | Module selection, session setup |
| 1.5 | `step-01b-continue.md` | continue | Resume interrupted session |
| 2 | `step-02-analyze.md` | analyze | Deep module analysis |
| 3 | `step-03-select.md` | select | Edit menu selection |
| 4.1 | `step-04a-agent-load.md` | agent-load | Load agent for editing |
| 4.11 | `step-04a1-agent-simple.md` | agent-simple | Edit simple agent |
| 4.12 | `step-04a2-agent-expert.md` | agent-expert | Edit expert agent |
| 4.13 | `step-04a3-agent-module.md` | agent-module | Edit module agent |
| 4.14 | `step-04a-agent-add.md` | agent-add | Add new agent |
| 4.15 | `step-04a-agent-remove.md` | agent-remove | Remove agent |
| 4.2 | `step-04b-workflow-load.md` | workflow-load | Load workflow for editing |
| 4.21 | `step-04b1-workflow-standalone.md` | workflow-standalone | Edit standalone workflow |
| 4.22 | `step-04b2-workflow-legacy.md` | workflow-legacy | Edit legacy workflow |
| 4.23 | `step-04b-workflow-add.md` | workflow-add | Add new workflow |
| 4.24 | `step-04b-workflow-remove.md` | workflow-remove | Remove workflow |
| 4.3 | `step-04c-config.md` | config | Edit module.yaml |
| 4.4 | `step-04d-docs.md` | docs | Edit documentation |
| 5 | `step-05-validate.md` | validate | Run validation |
| 6 | `step-06-iterate.md` | iterate | Loop or finish decision |
| 7 | `step-07-complete.md` | complete | Finalize session |

#### Updated Frontmatter Schema

```yaml
# Progress Tracking (REVISED)
stepsCompleted: [1, 2, 3]           # Supports integer and decimal indices (e.g., 4.1, 4.11)
lastStep: "step-03-select"          # Full step filename for routing
lastStepIndex: 3                    # Numeric index for quick checks
currentTarget: null                 # Component being edited

# Example for completed session:
stepsCompleted: [1, 2, 3, 4.1, 4.11, 5, 6, 3, 4.3, 5, 6, 7]
lastStep: "step-07-complete"
lastStepIndex: 7
```

#### Routing Logic Using Index

```
IF lastStepIndex < 2:
    Route to step-02-analyze.md
ELIF lastStepIndex < 3:
    Route to step-03-select.md
ELIF lastStepIndex >= 3 AND lastStepIndex < 5:
    Route based on currentTarget type
ELIF lastStepIndex == 5:
    Route to step-06-iterate.md
ELIF lastStepIndex == 6:
    Route to step-03-select.md OR step-07-complete.md based on user choice
```

---

### R2-FIX-007: System Coordination - Lock + Backup + Transaction

**Addresses:** R2-ISSUE-007 (MEDIUM) - Lock + Backup + Transaction Coordination

**Issue:** Three systems (locks, backups, transactions) defined separately but interaction sequence unclear.

**Resolution:** Define explicit coordination sequences for single-file and multi-file operations.

#### Single-File Edit Coordination Sequence

```
+------------------------------------------------------------------------------+
|                        SINGLE-FILE EDIT SEQUENCE                             |
+------------------------------------------------------------------------------+
|                                                                              |
|  1. LOCK PHASE (Must complete before any file access)                        |
|     +-- Check for existing lock on target file                               |
|     +-- IF lock exists: Handle collision (Wait/Force/Abort)                  |
|     +-- Create lock file with session_id, timestamp, TTL                     |
|     +-- FAIL -> E001: Abort operation, no further steps                      |
|                                                                              |
|  2. BACKUP PHASE (Must complete before any modification)                     |
|     +-- Read original file, compute SHA-256 hash                             |
|     +-- Write backup to: {module_path}/.backup/{timestamp}/{filename}        |
|     +-- Verify backup matches original (byte-for-byte)                       |
|     +-- Record in session: backupsCreated[]                                  |
|     +-- FAIL -> E003: Release lock, abort operation                          |
|                                                                              |
|  3. EDIT PHASE (Modifications in memory/temp only)                           |
|     +-- Load file content into editor buffer                                 |
|     +-- User makes changes (all in memory)                                   |
|     +-- Refresh lock TTL periodically (every 10 min)                         |
|     +-- CANCEL -> Release lock, delete backup (optional), exit               |
|                                                                              |
|  4. VALIDATION PHASE (Must pass before write)                                |
|     +-- Syntax validation (YAML/Markdown)                                    |
|     +-- Structure validation (BMAD compliance)                               |
|     +-- Reference validation (paths, links)                                  |
|     +-- FAIL -> E005/E006: Return to Edit Phase, keep lock                   |
|                                                                              |
|  5. COMMIT PHASE (Atomic write)                                              |
|     +-- Write changes to temp file: {filename}.tmp                           |
|     +-- Verify temp file integrity                                           |
|     +-- Atomic rename: {filename}.tmp -> {filename}                          |
|     +-- Delete temp file if rename fails                                     |
|     +-- FAIL -> E007/E008: Keep backup, release lock, report                 |
|                                                                              |
|  6. CLEANUP PHASE                                                            |
|     +-- Release lock file (delete)                                           |
|     +-- Update session frontmatter (stepsCompleted, editsPerformed)          |
|     +-- Keep backup per retention policy (default: session end)              |
|     +-- Log success                                                          |
|                                                                              |
+------------------------------------------------------------------------------+
```

#### Multi-File Edit Coordination Sequence (Transaction)

```
+------------------------------------------------------------------------------+
|                     MULTI-FILE EDIT SEQUENCE (TRANSACTION)                   |
+------------------------------------------------------------------------------+
|                                                                              |
|  1. TRANSACTION INIT                                                         |
|     +-- Generate transaction_id: txn-{session_id}-{sequence}                 |
|     +-- Create transaction manifest: .backup/transaction-{txn_id}.yaml       |
|     +-- Set state: "preparing"                                               |
|                                                                              |
|  2. LOCK ACQUISITION (ALL files, in sorted order to prevent deadlock)        |
|     +-- Sort files by path alphabetically                                    |
|     +-- FOR EACH file in sorted order:                                       |
|     |   +-- Attempt lock acquisition                                         |
|     |   +-- IF FAIL: Release all acquired locks, abort transaction           |
|     +-- Record all locks in transaction manifest                             |
|     +-- Set state: "locked"                                                  |
|                                                                              |
|  3. BACKUP CREATION (ALL files)                                              |
|     +-- FOR EACH file:                                                       |
|     |   +-- Create backup with checksum verification                         |
|     |   +-- Record in manifest: backup_path, original_hash                   |
|     +-- IF ANY FAIL: Rollback (delete backups, release locks)                |
|     +-- Set state: "backed_up"                                               |
|                                                                              |
|  4. EDIT PHASE (Changes to temp files only)                                  |
|     +-- FOR EACH file:                                                       |
|     |   +-- Apply changes to {filename}.txn-{txn_id}.tmp                     |
|     |   +-- Validate individually                                            |
|     +-- Cross-file validation (references between files)                     |
|     +-- Set state: "staged"                                                  |
|                                                                              |
|  5. COMMIT PHASE (Atomic batch - ALL OR NOTHING)                             |
|     +-- Set state: "committing"                                              |
|     +-- FOR EACH file (same sorted order):                                   |
|     |   +-- Atomic rename: tmp -> original                                   |
|     |   +-- IF FAIL: Trigger immediate rollback                              |
|     +-- IF ANY FAIL:                                                         |
|     |   +-- Restore from backups (reverse order)                             |
|     |   +-- Set state: "rolled_back"                                         |
|     |   +-- Report partial commit files for manual review                    |
|     +-- Set state: "committed"                                               |
|                                                                              |
|  6. CLEANUP PHASE                                                            |
|     +-- Release all locks (reverse acquisition order)                        |
|     +-- Delete temp files                                                    |
|     +-- Archive transaction manifest                                         |
|     +-- Update session with all edits                                        |
|                                                                              |
+------------------------------------------------------------------------------+
```

#### System Interaction Matrix

| Operation | Lock | Backup | Transaction | Order |
|-----------|------|--------|-------------|-------|
| Read file (no edit) | NO | NO | NO | - |
| Edit single file | YES | YES | NO | Lock -> Backup -> Edit -> Commit |
| Edit 2+ files | YES (all) | YES (all) | YES | Init -> Lock All -> Backup All -> Edit -> Commit |
| Restore from backup | YES | READ | NO | Lock -> Read Backup -> Write -> Release |
| Force lock acquire | FORCE | YES | NO | Force Lock -> Standard flow |

---

### R2-FIX-008: Session ID Generation Specification

**Addresses:** R2-ISSUE-008 (MEDIUM) - Session ID Generation Unspecified

**Issue:** Lock files reference session IDs but generation mechanism not specified.

**Resolution:** Define session ID format, generation algorithm, and uniqueness guarantees.

#### Session ID Format

```
edit-{YYYY}-{MM}-{DD}-{HHMM}-{random4}

Examples:
  edit-2026-01-07-1430-a7f2
  edit-2026-01-07-1431-b3e9
```

#### Generation Algorithm

```python
def generate_session_id():
    """
    Generate unique session identifier.

    Format: edit-{date}-{time}-{random}
    - Date: YYYY-MM-DD
    - Time: HHMM (24-hour, local timezone)
    - Random: 4 hex characters (65,536 combinations)

    Collision probability: ~0.00002% per minute with typical usage
    """
    import datetime
    import secrets

    now = datetime.datetime.now()
    date_part = now.strftime("%Y-%m-%d")
    time_part = now.strftime("%H%M")
    random_part = secrets.token_hex(2)  # 4 hex chars

    return f"edit-{date_part}-{time_part}-{random_part}"
```

#### Uniqueness Guarantees

| Scenario | Guarantee | Mechanism |
|----------|-----------|-----------|
| Same user, same minute | Unique via random suffix | 65,536 possibilities/minute |
| Multiple users | Unique via random + time | Independent generation |
| Cross-session | Check existing sessions | Regenerate on collision |

#### Session ID in Lock Files

```yaml
# Lock file: {module_path}/.locks/{component}.lock
session_id: "edit-2026-01-07-1430-a7f2"  # Generated session ID
holder: "user@machine"                     # User identifier
locked_at: "2026-01-07T14:30:00Z"         # ISO 8601 timestamp
expires_at: "2026-01-07T15:30:00Z"        # TTL: +1 hour
operation: "edit"
```

---

### R2-FIX-009: Session Timeout Behavior

**Addresses:** R2-ISSUE-009 (MEDIUM) - Session Timeout Behavior Undefined

**Issue:** Locks have 1-hour TTL but session timeout behavior undefined.

**Resolution:** Define timeout detection, warning, and resume mechanisms.

#### Timeout Thresholds

| Threshold | Time | Action |
|-----------|------|--------|
| **Warning** | 50 minutes | Display timeout warning |
| **Final Warning** | 55 minutes | Urgent save prompt |
| **Soft Timeout** | 60 minutes | Lock expires, session pausable |
| **Hard Timeout** | 90 minutes | Session marked stale |

#### Timeout Warning Sequence

```
AT 50 MINUTES (Warning):
+-------------------------------------------------------------+
| WARNING: SESSION TIMEOUT WARNING                            |
|                                                             |
| Your edit session will timeout in 10 minutes.               |
|                                                             |
| Options:                                                    |
|   [E] Extend session (refreshes TTL to 60 minutes)          |
|   [S] Save now and continue                                 |
|   [C] Continue (reminder in 5 minutes)                      |
+-------------------------------------------------------------+

AT 55 MINUTES (Final Warning):
+-------------------------------------------------------------+
| WARNING: FINAL WARNING: 5 MINUTES REMAINING                 |
|                                                             |
| Unsaved changes will be preserved for resume, but lock      |
| will be released allowing other users to edit.              |
|                                                             |
| Options:                                                    |
|   [S] Save immediately                                      |
|   [E] Extend session                                        |
|   [P] Pause session (save state, release lock)              |
+-------------------------------------------------------------+

AT 60 MINUTES (Soft Timeout):
+-------------------------------------------------------------+
| SESSION PAUSED                                              |
|                                                             |
| Your session has timed out. Current state:                  |
| - Lock: RELEASED                                            |
| - Unsaved changes: PRESERVED in session file                |
| - Backups: RETAINED                                         |
|                                                             |
| You can resume this session later via step-01b-continue.    |
|                                                             |
| Session file: edit-session-{module_name}-{sessionId}.md     |
+-------------------------------------------------------------+
```

#### Resume After Timeout

```markdown
## Resume Behavior (step-01b-continue.md)

### Timeout Resume Detection

1. Check session file `lastModified` vs current time
2. IF gap > 60 minutes:
   - Session was timed out
   - Check if another session edited same component
   - IF conflict: Offer merge/override/abandon
   - IF no conflict: Re-acquire locks, continue

### Resume Sequence

1. Load session file with unsaved state
2. Check component status:
   - File unchanged since timeout -> Resume normally
   - File modified by other -> Conflict resolution
   - File deleted -> Error E007, offer restore from backup
3. Re-acquire locks (may fail if held by other)
4. Re-validate backups still exist and match
5. Restore editor state from session
6. Continue from lastStep
```

#### Session State Persistence on Timeout

```yaml
# Added to session frontmatter on timeout
timeout_state:
  timed_out_at: "2026-01-07T15:30:00Z"
  unsaved_changes:
    - component: "agents/analyst.md"
      change_type: "modify"
      content_hash: "abc123..."  # Hash of unsaved content
      content_backup: "{module_path}/.backup/{timestamp}/analyst.md.unsaved"
  locks_released:
    - "agents/analyst.md"
  resume_available: true
```

---

### R2-FIX-010: Error Code to Step Mapping

**Addresses:** R2-ISSUE-010 (MEDIUM) - Error Code Mapping to Steps

**Issue:** Error codes E001-E010 defined but not mapped to which steps produce them.

**Resolution:** Define error-to-step mapping matrix.

#### Error Code Production Matrix

| Error Code | Description | Producing Steps | Trigger Condition |
|------------|-------------|-----------------|-------------------|
| **E001** | Cannot acquire lock | step-01-init, step-04a-agent-load, step-04b-workflow-load | Lock held by another session |
| **E002** | Lock about to expire | step-04a*, step-04b*, step-04c, step-04d | 50+ minutes elapsed |
| **E003** | Backup creation failed | step-04a-agent-load, step-04b-workflow-load | Disk full, permission denied |
| **E004** | Backup integrity failed | step-04a-agent-load, step-04b-workflow-load | Hash mismatch after backup |
| **E005** | Syntax error | step-05-validate | Invalid YAML, malformed markdown |
| **E006** | Compliance issue | step-05-validate | BMAD rule violation (non-blocking) |
| **E007** | File not found | step-01-init, step-04a-agent-load, step-04b-workflow-load | Target file deleted/moved |
| **E008** | Permission denied | step-01-init, step-04*, step-07-complete | Read/write permission missing |
| **E009** | Git operation failed | step-07-complete | Git add/commit failed |
| **E010** | Inconsistent state | Any step | State corruption detected |

#### Step-Specific Error Handling Reference

```markdown
## step-01-init.md Error Handling

Possible errors: E001, E007, E008, E010
- E001 -> Route to lock collision handler
- E007 -> "Module path not found: {path}" + abort
- E008 -> "Cannot access module: {path}" + suggest permissions
- E010 -> "Session file corrupted" + offer fresh start

## step-04a-agent-load.md Error Handling

Possible errors: E001, E003, E004, E007, E008
- E001 -> Lock collision, offer wait/force/abort
- E003 -> "Cannot create backup" + diagnose (disk/perm)
- E004 -> "Backup verification failed" + retry or abort
- E007 -> "Agent file not found" + return to menu
- E008 -> "Cannot read agent file" + check permissions

## step-05-validate.md Error Handling

Possible errors: E005, E006, E010
- E005 -> Display syntax errors, return to edit
- E006 -> Display warnings, allow proceed with confirmation
- E010 -> "Validation state corrupted" + offer restart

## step-07-complete.md Error Handling

Possible errors: E008, E009
- E008 -> "Cannot write changelog" + manual instructions
- E009 -> "Git commit failed" + show git status, manual fix
```

---

### R2-FIX-011: Component Duplication - Future Enhancement

**Addresses:** R2-ISSUE-011 (LOW) - Over-Engineering Component Duplication

**Issue:** Detailed specification for Phase 3 duplication feature adds cognitive load to core workflow specification.

**Resolution:** Mark as future enhancement, retain brief summary only.

#### Duplication Feature Status

**Status:** FUTURE ENHANCEMENT (Tier 2/3)
**Priority:** P2 (Nice to Have)
**Estimated Effort:** 8 story points

#### Brief Summary

The duplication feature will allow users to copy existing agents or workflows as starting points for new components. Three modes planned:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Clone** | Exact copy with new name | Quick variant creation |
| **Template** | Copy with placeholders cleared | Clean slate from existing |
| **Derive** | Copy with inheritance tracking | Maintain lineage |

#### Implementation Deferred To

- **When:** After core edit workflow is stable and tested
- **Prerequisite:** Work Packages WP-1 through WP-3 complete (foundation + core editing + validation)
- **Spec Location:** Create separate `workflow-plan-component-duplication.md` when ready

#### Removed From Core Workflow Scope

The detailed duplication specification is hereby marked as out-of-scope for initial implementation. The edit-module workflow v1.0 will support:

- Add new (blank) components
- Modify existing components
- Remove components
- **NOT in v1.0:** Duplicate existing components (deferred to v2.0)

---

### R2-FIX-012: Output Folder Creation

**Addresses:** R2-ISSUE-012 (LOW) - Output Folder Creation

**Issue:** Output folder creation not specified in step-01-init.

**Resolution:** Add explicit directory structure creation with error handling.

#### Directory Creation Specification (step-01-init.md Addition)

```markdown
### 1.5 Initialize Output Directory Structure

**MUST execute before any file operations**

#### Required Directories

{bmb_creations_output_folder}/modules/{module_name}/
{module_path}/.backup/
{module_path}/.locks/

#### Creation Sequence

1. Resolve `{bmb_creations_output_folder}` from config or default
   - Default: `{project_root}/_bmad-output/bmb-creations/`
   - Config override: `bmb.output_folder` in bmb/config.yaml

2. FOR EACH required directory:
   a. Check if exists
   b. IF not exists: Create with parents (mkdir -p equivalent)
   c. Verify write permission (create test file, delete)
   d. IF creation fails OR permission denied:
      - Log error with specific path
      - Produce error E008 with message:
        "Cannot create output directory: {path}
         Reason: {permission_denied|disk_full|path_invalid}

         Please ensure the path exists and is writable."
      - ABORT workflow (cannot proceed without output location)

3. Record created paths in session metadata

#### Directory Structure After Init

_bmad-output/
+-- bmb-creations/
    +-- modules/
        +-- {module_name}/
            +-- edit-session-{module_name}-{sessionId}.md  (created by step-01-init)

{module_path}/
+-- .backup/
|   +-- manifest.json
|   +-- {timestamp}/
|       +-- (backup files created by step-04*)
+-- .locks/
    +-- (lock files during active edits)
```

#### Error E008 Enhancement for Directory Creation

```yaml
# Add to Error State Taxonomy (Section 5)
E008_SUBTYPES:
  - code: E008-DIR
    description: "Cannot create required directory"
    severity: BLOCKING
    recovery: |
      1. Check parent directory permissions
      2. Verify disk space available
      3. Try alternative output location via config
      4. Manual directory creation instructions provided
```

---

### Round 2 Medium & Low Fix Summary

| Issue ID | Severity | Status | Fix Section |
|----------|----------|--------|-------------|
| R2-ISSUE-006 | MEDIUM | RESOLVED | R2-FIX-006: Step Index Mapping |
| R2-ISSUE-007 | MEDIUM | RESOLVED | R2-FIX-007: System Coordination |
| R2-ISSUE-008 | MEDIUM | RESOLVED | R2-FIX-008: Session ID Generation |
| R2-ISSUE-009 | MEDIUM | RESOLVED | R2-FIX-009: Timeout Behavior |
| R2-ISSUE-010 | MEDIUM | RESOLVED | R2-FIX-010: Error Code Mapping |
| R2-ISSUE-011 | LOW | RESOLVED | R2-FIX-011: Duplication Deferred |
| R2-ISSUE-012 | LOW | RESOLVED | R2-FIX-012: Output Folder Creation |

---

### Updated Implementation Readiness Checklist (Complete)

**Foundation:**
- [x] Stakeholder analysis complete with personas
- [x] Concurrency model defined with lock specification
- [x] Test strategy covering unit, integration, E2E, error injection
- [x] Quality gates defined with metrics and thresholds
- [x] Error states enumerated with recovery paths

**Round 2 Critical & High Fixes:**
- [x] Variable resolution algorithm fully specified (R2-FIX-001)
- [x] BMAD format rules defined with validation (R2-FIX-002)
- [x] Backup location clarified (R2-FIX-003)
- [x] Phasing terminology aligned (R2-FIX-004)
- [x] Module discovery algorithm defined (R2-FIX-005)

**Round 2 Medium & Low Fixes:**
- [x] Step index mapping defined for progress tracking (R2-FIX-006)
- [x] Lock/Backup/Transaction coordination sequences specified (R2-FIX-007)
- [x] Session ID generation algorithm defined (R2-FIX-008)
- [x] Timeout behavior and resume mechanism specified (R2-FIX-009)
- [x] Error codes mapped to producing steps (R2-FIX-010)
- [x] Component duplication marked as future enhancement (R2-FIX-011)
- [x] Output directory creation specified with E008 handling (R2-FIX-012)

**Integration:**
- [x] Version control integration specified
- [x] Changelog format standardized
- [x] Confirmation mechanisms designed by risk level
- [x] Diff preview feature fully specified
- [x] Stories decomposed into implementable units (32 points)
- [x] File system edge cases documented with mitigations

**Status:** Ready for implementation planning and sprint allocation.

---

*Round 2 Medium & Low Priority Fixes completed: 2026-01-07*
*Issues resolved this section: 7 (5 MEDIUM, 2 LOW)*
*Total Round 2 issues resolved: 12 (2 CRITICAL, 3 HIGH, 5 MEDIUM, 2 LOW)*
*Cumulative issues addressed: 25*

---

## Tools Configuration

*Configured: 2026-01-07*

### Core BMAD Tools

| Tool | Status | Integration Points | Trigger Conditions |
|------|--------|-------------------|-------------------|
| **Party-Mode** | ✅ Included | Validation phases (step-05-validate), complex edit decisions, multi-perspective review | Auto-trigger when validation fails with >3 issues OR user requests via [P] menu option |
| **Advanced Elicitation** | ✅ Included | Post-edit review, assumption challenging, quality gates | Auto-trigger when compliance score <70% OR user selects [A] from standard menu |
| **Brainstorming** | ✅ Included | Creative problem-solving when edits require design decisions | Auto-trigger when user describes intent but solution unclear OR user requests via [B] menu option |

### LLM Features

| Feature | Status | Use Cases |
|---------|--------|-----------|
| **Web-Browsing** | ✅ Included | BMAD documentation lookup, pattern research, best practices |
| **File I/O** | ✅ Included | Core editing capability - read, write, backup, restore module files |
| **Sub-Agents** | ✅ Included | Parallel validation, backup verification, compliance checking |
| **Sub-Processes** | ✅ Included | Background operations, long-running validations |

### Memory Systems

| System | Status | Purpose |
|--------|--------|---------|
| **Sidecar File** | ✅ Included | Session state persistence, edit history, resume capability |

### External Integrations

| Tool | Status | Requires Install | Purpose |
|------|--------|------------------|---------|
| **Git Integration** | ✅ Included | Yes | Prerequisite checks (uncommitted changes), auto-staging, commit operations |
| **Context-7** | ✅ Included | Yes | BMAD documentation access, API references, pattern lookup |

### Installation Requirements

| Tool | Installation URL |
|------|------------------|
| Git Integration | https://github.com/modelcontextprotocol/servers/tree/main/src/git |
| Context-7 | https://github.com/modelcontextprotocol/servers/tree/main/src/context-7 |

**User Installation Preference:** Willing to install required dependencies
**Total Tools Configured:** 10


---

## Output Format Design

*Designed: 2026-01-07*

### Format Strategy: Mixed Formats

Different documents require different levels of strictness based on their purpose.

### Document 1: Edit Session Document

**Format Type:** Structured (Required sections, flexible content)

**File:** `{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md`

**Structure:**
```yaml
---
# Frontmatter (STRICT - required fields)
sessionId: "edit-2026-01-07-1430-a7f2"
modulePath: "_bmad/bmb"
moduleName: "bmb"
startedAt: "2026-01-07T14:30:00Z"
lastUpdated: "2026-01-07T15:45:00Z"
status: "in_progress" | "completed" | "abandoned"
stepsCompleted: [1, 2, 3]
currentStep: 4
user: "Trevor Leigh"
---

# Edit Session: {moduleName}

## Session Summary
- Started: {startedAt}
- Module: {modulePath}
- Status: {status}

## Edits Performed
<!-- Flexible content - appended as edits occur -->

### Edit 1: {component_type} - {component_name}
- **Time:** {timestamp}
- **Action:** {edit_type}
- **Files Changed:** {file_list}
- **Validation:** {pass|fail}

## Validation Results
<!-- Appended after validation runs -->

## Session Notes
<!-- Free-form user notes -->
```

### Document 2: Changelog

**Format Type:** Structured (Keep-a-Changelog standard)

**File:** `{module_path}/CHANGELOG.md`

**Structure:**
```markdown
# Changelog

All notable changes to this module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- {description} ({date}, {user})

### Changed
- {description} ({date}, {user})

### Removed
- {description} ({date}, {user})

### Fixed
- {description} ({date}, {user})
```

### Document 3: Backup Manifest

**Format Type:** Strict (Exact fields for data integrity)

> **Clarification (R4-ISSUE-004, R4-ISSUE-007):** There are TWO distinct files:
> 1. **Schema for validation:** `data/backup-manifest-schema.json` - JSON Schema definition used to validate manifest files
> 2. **Actual manifest instances:** `{module_path}/.backup/{timestamp}/manifest.json` - One per backup, inside each timestamped directory
>
> **Important:** There is NO root-level manifest at `.backup/manifest.json`. Each `{timestamp}/` directory is self-contained with its own `manifest.json`.

**File Location:** `{module_path}/.backup/{timestamp}/manifest.json`

**Example Path:** `_bmad/bmb/.backup/20260107-143215/manifest.json`

**Structure:**
```json
{
  "manifestVersion": "1.0",
  "sessionId": "edit-2026-01-07-1430-a7f2",
  "createdAt": "2026-01-07T14:32:15Z",
  "modulePath": "_bmad/bmb",
  "backupPath": "_bmad/bmb/.backup/20260107-143215",
  "files": [
    {
      "originalPath": "agents/analyst.md",
      "backupPath": "agents/analyst.md.bak",
      "sha256": "abc123...",
      "size": 2048,
      "modifiedAt": "2026-01-05T10:00:00Z"
    }
  ],
  "totalFiles": 1,
  "totalSize": 2048,
  "status": "valid" | "restored" | "deleted"
}
```

### Validation Rules

| Document | Required Fields | Validation |
|----------|-----------------|------------|
| Edit Session | sessionId, modulePath, status, stepsCompleted | YAML parse, required fields present |
| Changelog | Header, at least one section | Markdown parse, Keep-a-Changelog format |
| Backup Manifest | All fields | JSON parse, SHA-256 verification, file existence |

### Template Files to Create

| Template | Location | Purpose |
|----------|----------|---------|
| `edit-session-template.md` | `templates/` | New session initialization |
| `changelog-entry-template.md` | `templates/` | Changelog entry format |
| `backup-manifest-schema.json` | `data/` | JSON schema for validation |


---

## Workflow Structure Design

*Confirmed: 2026-01-07*

### Design Status: CONFIRMED

The workflow structure was extensively designed during Round 1 adversarial review and documented in the "Architecture & File Structure Specification" section. This step confirms that design.

### Step Structure Summary (21 Files)

> **Note:** This is a summary confirmation of the canonical "Architecture & File Structure Specification" section. See that section for full details including directory structure, step specifications, and flow diagrams.

| # | Step File | Purpose | Required |
|---|-----------|---------|----------|
| 1 | step-01-init.md | Module selection, session creation | Yes |
| 1b | step-01b-continue.md | Resume existing session | Conditional |
| 2 | step-02-analyze.md | Structure analysis, component discovery | Yes |
| 3 | step-03-select.md | Edit type selection menu | Yes |
| 4a | step-04a-agent-load.md | Load agent for editing | Conditional |
| 4a1 | step-04a1-agent-simple.md | Simple agent editing | Conditional |
| 4a2 | step-04a2-agent-expert.md | Expert agent editing | Conditional |
| 4a3 | step-04a3-agent-module.md | Module agent editing | Conditional |
| 4a+ | step-04a-agent-add.md | Add new agent to module | Conditional |
| 4a- | step-04a-agent-remove.md | Remove agent from module | Conditional |
| 4b | step-04b-workflow-load.md | Load workflow for editing | Conditional |
| 4b1 | step-04b1-workflow-standalone.md | Standalone workflow editing | Conditional |
| 4b2 | step-04b2-workflow-legacy.md | Legacy workflow editing | Conditional |
| 4b+ | step-04b-workflow-add.md | Add new workflow to module | Conditional |
| 4b- | step-04b-workflow-remove.md | Remove workflow from module | Conditional |
| 4c | step-04c-config.md | module.yaml editing | Conditional |
| 4d | step-04d-docs.md | Documentation editing | Conditional |
| 5 | step-05-validate.md | Syntax + BMAD compliance validation | Yes |
| 6 | step-06-iterate.md | "More edits?" decision loop | Yes |
| 7 | step-07-complete.md | Backup cleanup, changelog, session close | Yes |

*Note: 20 step files + 1 workflow.md entry point = 21 total files*

### Flow Diagram

```
                              ┌─────────────────────────────────────────────────────────┐
                              │                    EDIT BRANCHES                         │
                              │  ┌─────────────────────────────────────────────────────┐ │
                              │  │ step-04a-agent-load ─┬─> step-04a1-agent-simple     │ │
                              │  │                      ├─> step-04a2-agent-expert     │ │
┌──────────────┐              │  │                      └─> step-04a3-agent-module     │ │
│ step-01-init │──┬───────────┼──┤                                                     │ │
└──────────────┘  │           │  │ step-04b-workflow-load ─┬─> step-04b1-standalone    │ │
                  │           │  │                         └─> step-04b2-legacy        │ │
┌──────────────────┐          │  │                                                     │ │
│ step-01b-continue│──────────┼──┤ step-04c-config                                     │ │
└──────────────────┘          │  │                                                     │ │
                              │  │ step-04d-docs                                       │ │
        │                     │  └─────────────────────────────────────────────────────┘ │
        ▼                     └─────────────────────────────────────────────────────────┘
┌──────────────┐                                        │
│ step-02-analyze │                                     ▼
└──────────────┘                              ┌─────────────────┐
        │                                     │ step-05-validate │
        ▼                                     └─────────────────┘
┌──────────────┐                                        │
│ step-03-select │◄─────────────────────────────────────┤
└──────────────┘                                        ▼
        │                                     ┌─────────────────┐
        └─────────────────────────────────────│ step-06-iterate │
                                              └─────────────────┘
                                                        │
                                    ┌───────────────────┴───────────────────┐
                                    │ More edits?                           │
                                    │ YES → step-03-select                  │
                                    │ NO  → step-07-complete                │
                                    └───────────────────────────────────────┘
```

### Continuation Support

| Feature | Implementation |
|---------|----------------|
| Session Detection | step-01-init checks for existing edit-session-*.md |
| Resume Flow | step-01b-continue loads session, routes to last step |
| State Persistence | Every step updates stepsCompleted in frontmatter |
| Timeout Handling | 50/55/60 min warnings, session persists indefinitely |

### Interaction Patterns

| Context | Pattern | Example |
|---------|---------|---------|
| Navigation | Menu-driven | [1] Agents [2] Workflows [3] Config [4] Docs |
| Decisions | Intent-based | "What would you like to change about this agent?" |
| Destructive Ops | Prescriptive | "Type 'CONFIRM DELETE' to remove this workflow" |
| Each Step End | Standard Menu | [A] Advanced Elicitation [P] Party Mode [C] Continue |

### Data Flow

| Step | Inputs | Outputs |
|------|--------|---------|
| 01-init | User choice, module path | Session document created |
| 02-analyze | Module path | Component inventory |
| 03-select | User choice | Edit target identified |
| 04x-edit | Component file | Modified content, backup |
| 05-validate | Modified content | Validation results |
| 06-iterate | User choice | Loop or exit decision |
| 07-complete | Session state | Changelog, backup cleanup |

### File Structure

```
_bmad/bmb/workflows/edit-module/
├── workflow.md                       # Main entry point (1 file)
├── steps/                            # Step files (20 files)
│   ├── step-01-init.md
│   ├── step-01b-continue.md
│   ├── step-02-analyze.md
│   ├── step-03-select.md
│   ├── step-04a-agent-load.md
│   ├── step-04a1-agent-simple.md
│   ├── step-04a2-agent-expert.md
│   ├── step-04a3-agent-module.md
│   ├── step-04a-agent-add.md         # Add new agent (R4-FIX)
│   ├── step-04a-agent-remove.md      # Remove agent (R4-FIX)
│   ├── step-04b-workflow-load.md
│   ├── step-04b1-workflow-standalone.md
│   ├── step-04b2-workflow-legacy.md
│   ├── step-04b-workflow-add.md      # Add new workflow (R4-FIX)
│   ├── step-04b-workflow-remove.md   # Remove workflow (R4-FIX)
│   ├── step-04c-config.md
│   ├── step-04d-docs.md
│   ├── step-05-validate.md
│   ├── step-06-iterate.md
│   └── step-07-complete.md
├── templates/
│   ├── edit-session-template.md
│   ├── changelog-entry-template.md
│   └── backup-manifest-template.json  # Template for creating new manifests
└── data/
    ├── validation-rules.md
    └── backup-manifest-schema.json    # JSON Schema for manifest validation
```

### Role and Persona

| Aspect | Definition |
|--------|------------|
| Expertise | Module architecture, BMAD patterns, file system operations |
| Communication | Strategic, holistic, systems-thinking |
| Tone | Professional, safety-conscious, collaborative |
| Collaboration Level | High - user drives decisions, AI provides guidance |

### Validation and Error Handling

| Checkpoint | Validation | Recovery |
|------------|------------|----------|
| Module Load | Exists, valid YAML, passes basic validation | Suggest fixes, abort |
| Pre-Edit | Git status clean, locks available | Warn, suggest commit |
| Post-Edit | YAML syntax, BMAD compliance | Show errors, allow retry |
| Backup | Checksum verification | Abort if verification fails |
| Session End | All edits validated, user confirms | Keep session open |

### Design Confirmation

- [x] Step count appropriate (21 files covering all scenarios)
- [x] Branch structure handles all component types
- [x] Iteration loop returns to selection until done
- [x] Continuation support for multi-session editing
- [x] All requirements from adversarial review addressed

---

## Round 4 Fixes: MEDIUM & LOW Priority

*Completed: 2026-01-07*
*Issues resolved: 6 (4 MEDIUM, 2 LOW)*

### R4-FIX-003: Step Count Mismatch (MEDIUM)

**Issue:** Step Structure Summary claimed 21 files but only listed 16. Missing add/remove steps for agents and workflows.

**Resolution:** Updated the Step Structure Summary table to include all 21 files:
- Added `step-04a-agent-add.md` (4a+) - Add new agent to module
- Added `step-04a-agent-remove.md` (4a-) - Remove agent from module
- Added `step-04b-workflow-add.md` (4b+) - Add new workflow to module
- Added `step-04b-workflow-remove.md` (4b-) - Remove workflow from module

**Files Updated:**
- Step Structure Summary table (now shows all 21 files with indices 4a+, 4a-, 4b+, 4b-)
- File Structure diagram in Workflow Structure Design section

---

### R4-FIX-004: Backup Manifest Name/Location Conflicts (MEDIUM)

**Issue:** Document referenced different names (schema.json, template.json, manifest.yaml) and locations (data/, templates/, .backup/) causing confusion about what file serves what purpose.

**Resolution:** Clarified there are TWO distinct files:

| File | Location | Purpose |
|------|----------|---------|
| **Schema** | `data/backup-manifest-schema.json` | JSON Schema definition for validating manifest files |
| **Instance** | `{module_path}/.backup/{timestamp}/manifest.json` | Actual manifest created during backup operations |

**Key Clarification:** The schema defines the structure; manifest instances follow that structure.

---

### R4-FIX-005: Integer Indices Comment Contradiction (MEDIUM)

**Issue:** Comment said "Integer indices only" but example used decimal indices (4.1, 4.11, etc.).

**Resolution:** Changed comment from:
```yaml
stepsCompleted: [1, 2, 3]           # Integer indices only
```
To:
```yaml
stepsCompleted: [1, 2, 3]           # Supports integer and decimal indices (e.g., 4.1, 4.11)
```

Decimal indices are valid and necessary for tracking sub-step progress (e.g., 4.11 for step-04a1-agent-simple.md).

---

### R4-FIX-006: Tool Invocation Triggers Undefined (MEDIUM)

**Issue:** Tools listed with "Included" status but no specification of when they should be automatically invoked.

**Resolution:** Added explicit trigger conditions to the Core BMAD Tools table:

| Tool | Trigger Conditions |
|------|-------------------|
| **Party-Mode** | Auto-trigger when validation fails with >3 issues OR user requests via [P] menu option |
| **Advanced Elicitation** | Auto-trigger when compliance score <70% OR user selects [A] from standard menu |
| **Brainstorming** | Auto-trigger when user describes intent but solution unclear OR user requests via [B] menu option |

---

### R4-FIX-007: Manifest Location Ambiguity (LOW)

**Issue:** Unclear whether manifest lives at `.backup/` root or inside `{timestamp}/` directory.

**Resolution:** Added explicit clarification in Document 3: Backup Manifest section:

> **Important:** There is NO root-level manifest at `.backup/manifest.json`. Each `{timestamp}/` directory is self-contained with its own `manifest.json`.

**Directory Structure:**
```
{module_path}/.backup/
├── 20260107-143215/           # Timestamped backup 1
│   ├── manifest.json          # Manifest for THIS backup
│   └── (backed up files)
├── 20260107-150000/           # Timestamped backup 2
│   ├── manifest.json          # Manifest for THIS backup
│   └── (backed up files)
└── (no root manifest.json)
```

---

### R4-FIX-008: Redundant Sections (LOW)

**Issue:** Workflow Structure Design section duplicated content from Architecture section without clear purpose.

**Resolution:** Added clarifying note to Workflow Structure Design section:

> **Note:** This is a summary confirmation of the canonical "Architecture & File Structure Specification" section. See that section for full details including directory structure, step specifications, and flow diagrams.

This establishes the Workflow Structure Design as a "confirmation checkpoint" rather than an independent specification, with the Architecture section remaining the canonical source.

---

### Round 4 Summary

| Issue ID | Severity | Status | Fix Applied |
|----------|----------|--------|-------------|
| R4-ISSUE-003 | MEDIUM | RESOLVED | Step count table updated with all 21 files |
| R4-ISSUE-004 | MEDIUM | RESOLVED | Two-file distinction clarified (schema vs instance) |
| R4-ISSUE-005 | MEDIUM | RESOLVED | Incorrect comment removed, decimal indices validated |
| R4-ISSUE-006 | MEDIUM | RESOLVED | Explicit trigger conditions added to tool table |
| R4-ISSUE-007 | LOW | RESOLVED | Per-timestamp manifest location clarified |
| R4-ISSUE-008 | LOW | RESOLVED | Summary confirmation note added |

*Round 4 Medium & Low Priority Fixes completed: 2026-01-07*
*Cumulative issues addressed: 69 (63 prior + 6 this round)*

---

## Round 4 Fixes: HIGH Priority

*Applied: 2026-01-07*

### R4-FIX-001: Edit Session Filename Consolidation (HIGH)

**Issue:** R4-ISSUE-001 - The Output Format Design section used `edit-session-{sessionId}.md` while the Architecture section used `edit-session-{module_name}.md`. These are fundamentally different naming approaches creating implementation confusion.

**Resolution:** Consolidated to a single naming convention that combines both approaches:

```
edit-session-{module_name}-{sessionId}.md
```

**Rationale:**
- Allows finding sessions by module: glob `edit-session-{module_name}-*.md`
- Ensures unique sessions per editing run via sessionId
- Supports continuation/resume workflow requiring session discovery

**Example:**
```
_bmad-output/bmb-creations/modules/bmm/edit-session-bmm-edit-2026-01-07-1430.md
```

**Sections Updated:**
| Section | Line (approx) | Change |
|---------|---------------|--------|
| Continuation/Resume Mechanism | 1952 | `edit-session-{module_name}-{sessionId}.md` |
| Output Document Specification | 2065, 2070 | Pattern and example updated |
| Output Document Paths table | 2407 | Pattern and example updated |
| Architecture Issue Resolution Summary | 2477 | ISSUE-003 resolution text |
| R2-FIX-001 Variable Substitution | 3632, 3636 | Before/after examples |
| R2-FIX-003 File Path Reference Table | 3854 | Pattern and example updated |
| Session Timeout Handler | 4389 | Session file reference |
| Directory Structure After Init | 4586 | Directory tree |
| Output Format Design | 4723 | Canonical file path |

**Search Pattern Verification:**
- Glob pattern `edit-session-{module_name}*.md` correctly matches new format
- Detection pattern `edit-session-*.md` correctly matches new format

---

### R4-FIX-002: Backup Manifest Format Consolidation (HIGH)

**Issue:** R4-ISSUE-002 - Safety & Validation section showed `manifest.yaml` with YAML structure, but Output Format Design showed `manifest.json` with JSON format.

**Resolution:** Consolidated to JSON format (`manifest.json`) throughout the document.

**Rationale:**
- JSON provides stricter validation with JSON Schema support
- Better tooling for schema validation
- Consistent with Output Format Design's intended "Strict" validation type

**Canonical Schema Format (JSON):**
```json
{
  "version": 1,
  "transactionId": "uuid-abc123",
  "created": "2026-01-07T14:30:00Z",
  "modulePath": "{module_path}",
  "backupPath": "{module_path}/.backup/{timestamp}/",
  "status": "active",
  "files": [
    {
      "relativePath": "agents/analyst.md",
      "originalChecksum": "sha256:...",
      "backupChecksum": "sha256:...",
      "checksumVerified": true,
      "sizeBytes": 2048
    }
  ],
  "allVerified": true
}
```

**Sections Updated:**
| Section | Line (approx) | Change |
|---------|---------------|--------|
| Backup Directory Structure | 1070 | `manifest.json` |
| Backup Manifest Schema | 1082-1109 | Full JSON schema example |
| Backup Deletion Sequence | 1143, 1145, 1146 | `manifest.json` references |
| Rollback Procedure | 1157, 1165 | `manifest.json` references |
| Updated Backup Specification | 3835 | Directory tree |
| Updated File Path Reference Table | 3857 | Pattern and example |
| Directory Structure After Init | 4590 | Directory tree |

**Template File Updates Required:**
- `templates/backup-manifest-template.json` - Already JSON format
- `data/backup-manifest-schema.json` - Already JSON Schema

---

### Round 4 HIGH Priority Summary

| Issue ID | Severity | Status | Fix Applied |
|----------|----------|--------|-------------|
| R4-ISSUE-001 | HIGH | RESOLVED | Edit session filename consolidated to `edit-session-{module_name}-{sessionId}.md` |
| R4-ISSUE-002 | HIGH | RESOLVED | Backup manifest format consolidated to JSON (`manifest.json`) |

**Total sections updated:** 17+ locations across the document
**Consistency verified:** All patterns now use consolidated formats

*Round 4 HIGH Priority Fixes completed: 2026-01-07*
*Cumulative issues addressed: 71 (69 prior + 2 HIGH this round)*


---

## Round 5: Final Verification

*Completed: 2026-01-07*

### Verification Results

| Agent | Domain | Verdict |
|-------|--------|---------|
| Advanced Elicitation | Gap/Inconsistency Analysis | 0 ISSUES |
| Architect | System Architecture | FINAL SIGN-OFF |
| Quality Engineer | Testing/Validation | FINAL SIGN-OFF |
| Product Owner | Scope/Stories | FINAL SIGN-OFF |
| Security Analyst | Data Integrity | FINAL SIGN-OFF |
| UX Designer | User Interaction | FINAL SIGN-OFF |
| DevOps Engineer | Infrastructure | FINAL SIGN-OFF |

### Cumulative Issue Resolution

| Round | Issues Found | Issues Fixed | Status |
|-------|--------------|--------------|--------|
| Round 1 | 51 | 51 | Complete |
| Round 2 | 12 | 12 | Complete |
| Round 3 | 0 | - | Verified |
| Round 4 | 8 | 8 | Complete |
| Round 5 | 0 | - | **FINAL VERIFICATION PASSED** |
| **TOTAL** | **71** | **71** | **100%** |

### Specification Status

**APPROVED FOR IMPLEMENTATION**

The edit-module workflow specification is:
- Complete (~5,200 lines)
- Internally consistent (all naming, formats, paths consolidated)
- Implementation-ready (all 31 files specified with content guidelines)
- Test-covered (71/25/5 test pyramid, 4 quality gates)
- Story-decomposed (11 stories, 32 points, 4 sprints)

---

## Build Summary

*Build completed: 2026-01-07*
*Build strategy: Phased parallel execution with subagents*

### Phase 1: Foundation Files (6 files)

| File | Location | Status |
|------|----------|--------|
| `workflow.md` | `edit-module/workflow.md` | ✅ Created |
| `edit-session-template.md` | `edit-module/templates/` | ✅ Created |
| `changelog-entry-template.md` | `edit-module/templates/` | ✅ Created |
| `backup-manifest-template.json` | `edit-module/templates/` | ✅ Created |
| `validation-rules.md` | `edit-module/data/` | ✅ Created |
| `backup-manifest-schema.json` | `edit-module/data/` | ✅ Created |

### Phase 2: Core Steps (9 files)

| File | Purpose | Status |
|------|---------|--------|
| `step-01-init.md` | Initialize workflow, module selection | ✅ Created |
| `step-01b-continue.md` | Resume interrupted session | ✅ Created |
| `step-02-analyze.md` | Deep module structure analysis | ✅ Created |
| `step-03-select.md` | Edit menu selection | ✅ Created |
| `step-04c-config.md` | Edit module.yaml | ✅ Created |
| `step-04d-docs.md` | Edit documentation | ✅ Created |
| `step-05-validate.md` | Syntax + BMAD compliance | ✅ Created |
| `step-06-iterate.md` | More edits decision loop | ✅ Created |
| `step-07-complete.md` | Finalize session | ✅ Created |

### Phase 3: Agent Branch Steps (6 files)

| File | Purpose | Status |
|------|---------|--------|
| `step-04a-agent-load.md` | Load agent, detect type | ✅ Created |
| `step-04a1-agent-simple.md` | Edit simple agents | ✅ Created |
| `step-04a2-agent-expert.md` | Edit expert agents | ✅ Created |
| `step-04a3-agent-module.md` | Edit module agents | ✅ Created |
| `step-04a-agent-add.md` | Add new agent | ✅ Created |
| `step-04a-agent-remove.md` | Remove agent (DESTRUCTIVE) | ✅ Created |

### Phase 4: Workflow Branch Steps (5 files)

| File | Purpose | Status |
|------|---------|--------|
| `step-04b-workflow-load.md` | Load workflow, detect type | ✅ Created |
| `step-04b1-workflow-standalone.md` | Edit standalone workflows | ✅ Created |
| `step-04b2-workflow-legacy.md` | Edit legacy workflows | ✅ Created |
| `step-04b-workflow-add.md` | Add new workflow | ✅ Created |
| `step-04b-workflow-remove.md` | Remove workflow (CRITICAL) | ✅ Created |

### Build Statistics

| Metric | Count |
|--------|-------|
| **Total Files Created** | 26 |
| **Step Files** | 20 |
| **Template Files** | 3 |
| **Data Files** | 2 |
| **Entry Point** | 1 |
| **Parallel Build Agents** | 7 |
| **Build Phases** | 4 |

### Directory Structure

```
_bmad-output/bmb-creations/workflows/edit-module/
├── workflow.md                           # Entry point
├── steps/
│   ├── step-01-init.md                   # Init + module selection
│   ├── step-01b-continue.md              # Session resume
│   ├── step-02-analyze.md                # Module analysis
│   ├── step-03-select.md                 # Edit menu
│   ├── step-04a-agent-load.md            # Agent loader
│   ├── step-04a1-agent-simple.md         # Simple agent edit
│   ├── step-04a2-agent-expert.md         # Expert agent edit
│   ├── step-04a3-agent-module.md         # Module agent edit
│   ├── step-04a-agent-add.md             # Add agent
│   ├── step-04a-agent-remove.md          # Remove agent
│   ├── step-04b-workflow-load.md         # Workflow loader
│   ├── step-04b1-workflow-standalone.md  # Standalone workflow edit
│   ├── step-04b2-workflow-legacy.md      # Legacy workflow edit
│   ├── step-04b-workflow-add.md          # Add workflow
│   ├── step-04b-workflow-remove.md       # Remove workflow
│   ├── step-04c-config.md                # Config edit
│   ├── step-04d-docs.md                  # Docs edit
│   ├── step-05-validate.md               # Validation
│   ├── step-06-iterate.md                # Iteration loop
│   └── step-07-complete.md               # Completion
├── templates/
│   ├── edit-session-template.md          # Session document template
│   ├── changelog-entry-template.md       # Changelog format
│   └── backup-manifest-template.json     # Backup manifest template
└── data/
    ├── validation-rules.md               # BMAD compliance rules
    └── backup-manifest-schema.json       # JSON Schema for manifests
```

### Build Status

**BUILD COMPLETE** ✅

All 26 files generated from the ~5,200 line specification.
Workflow is ready for testing and integration.

---

*Build summary appended: 2026-01-07*

---

## Review Summary

*Review completed: 2026-01-07*

### 1. File Structure Review

| Check | Status | Details |
|-------|--------|---------|
| All required files present | ✅ PASS | 26 files created |
| Directory structure correct | ✅ PASS | workflow.md, steps/, templates/, data/ |
| File naming conventions | ✅ PASS | step-NN-name.md pattern followed |
| Path configuration | ✅ PASS | All paths use {workflow_path} variables |

### 2. Configuration Validation

| Check | Status | Details |
|-------|--------|---------|
| workflow.md frontmatter | ✅ PASS | name, description, web_bundle present |
| Step file frontmatter | ✅ PASS | All 20 steps have valid YAML |
| Path variables formatted | ✅ PASS | {workflow_path}, {outputFile}, etc. |
| Dependencies declared | ✅ PASS | Template and data file references valid |

### 3. Step File Compliance

| Check | Status | Details |
|-------|--------|---------|
| Template structure followed | ✅ PASS | All steps follow BMAD step template |
| Mandatory rules included | ✅ PASS | Universal rules, role reinforcement present |
| Menu handling implemented | ✅ PASS | [A] [P] [C] pattern with halt rules |
| Step numbering correct | ✅ PASS | Sequential with branch variants (04a1, 04b2) |
| Success/failure metrics | ✅ PASS | All steps have explicit metrics section |

### 4. Cross-File Consistency

| Check | Status | Details |
|-------|--------|---------|
| Variable names match | ✅ PASS | {module_name}, {sessionId}, etc. consistent |
| Path references consistent | ✅ PASS | All use {workflow_path}/steps/ pattern |
| Step sequence logical | ✅ PASS | Init → Analyze → Select → Edit → Validate → Iterate → Complete |
| No broken references | ✅ PASS | All nextStepFile and template references valid |

### 5. Requirements Verification

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Edit agents (3 types) | ✅ PASS | step-04a1, 04a2, 04a3 for Simple/Expert/Module |
| Edit workflows (2 types) | ✅ PASS | step-04b1, 04b2 for Standalone/Legacy |
| Edit config (module.yaml) | ✅ PASS | step-04c-config.md |
| Edit documentation | ✅ PASS | step-04d-docs.md |
| Add agents/workflows | ✅ PASS | step-04a-agent-add, step-04b-workflow-add |
| Remove agents/workflows | ✅ PASS | Destructive ops with CONFIRM DELETE protocol |
| Session continuation | ✅ PASS | step-01b-continue.md with frontmatter tracking |
| Backup system | ✅ PASS | Manifest-based with checksum verification |
| BMAD validation | ✅ PASS | AGT-*, WFL-*, MOD-* rules in validation-rules.md |
| Iteration loop | ✅ PASS | step-06-iterate with menu options |

### 6. Best Practices Adherence

| Check | Status | Details |
|-------|--------|---------|
| Step files focused | ✅ PASS | Each step single-purpose, reasonable size |
| Collaborative dialogue | ✅ PASS | "We engage in collaborative dialogue" in all steps |
| Error handling | ✅ PASS | Error codes (E001-E009) defined |
| Destructive safeguards | ✅ PASS | HIGH/CRITICAL severity with typed confirmation |
| Git integration | ✅ PASS | Optional commit with user choice |
| Atomic swap pattern | ✅ PASS | Write to .tmp then rename |

### 7. Validation Results

| Category | Status |
|----------|--------|
| Configuration validation | ✅ PASSED |
| Step compliance | ✅ PASSED |
| Cross-file consistency | ✅ PASSED |
| Requirements verification | ✅ PASSED |

### 8. Issues Found

**Critical Issues:** None

**Warnings:** None

**Suggestions:**
- Consider adding step-04e for editing data files if needed in future
- May want to add rollback-all capability in step-07

### 9. Deployment Readiness

| Item | Status |
|------|--------|
| Workflow files complete | ✅ Ready |
| Templates complete | ✅ Ready |
| Validation rules defined | ✅ Ready |
| Integration with BMB menu | Requires linking |

### 10. Next Steps

1. **Integration**: Add to `_bmad/bmb/agents/module-builder.md` menu
2. **Testing**: Run workflow against test module
3. **Compliance Check**: Run `/bmad:bmb:workflows:workflow-compliance-check` in fresh context
4. **Documentation**: Update BMB README if needed

---

### Review Status

**REVIEW COMPLETE** ✅

All validation checks passed. The edit-module workflow is ready for deployment.

---

*Review summary appended: 2026-01-07*

