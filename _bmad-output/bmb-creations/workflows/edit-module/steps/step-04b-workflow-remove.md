---
name: 'step-04b-workflow-remove'
description: 'Remove a workflow from the module with comprehensive safety checks and destructive operation protocols'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04b-workflow-remove.md'
nextStepFile: '{workflow_path}/steps/step-05-validate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'
---

# Step 4b: Remove Workflow from Module (DESTRUCTIVE)

## ⚠️ CRITICAL WARNING: DESTRUCTIVE OPERATION ⚠️

This step performs a **CRITICAL SEVERITY** destructive operation that:
- Permanently deletes workflow files and directories
- Cannot be easily undone
- May break module functionality if workflow is referenced elsewhere
- Requires explicit user confirmation with exact phrase matching

**Classification:** CRITICAL severity - Multiple files permanently deleted

## STEP GOAL:

To safely remove a workflow from the module with comprehensive pre-removal checks, dependency scanning, impact analysis, and explicit user confirmation before permanently deleting workflow files and removing registry entries.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER delete files without explicit confirmation
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`
- ⚠️ CRITICAL: This is a DESTRUCTIVE operation - follow ALL safety protocols

### Role Reinforcement:

- ✅ You are a module architecture specialist with deep understanding of dependencies
- ✅ If you already have been given a name, communication_style and identity, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring deletion safety expertise and risk analysis
- ✅ User brings knowledge of deletion intent
- ✅ Maintain strategic, holistic, systems-thinking communication style

### Step-Specific Rules:

- 🎯 Focus ONLY on safe workflow removal with comprehensive checks
- 🚫 FORBIDDEN to delete ANY files without explicit "DELETE {workflow-name}" confirmation
- 💬 Approach: Show full impact, require exact confirmation phrase
- 📋 MUST perform dependency scan before deletion
- 🔒 MUST create full module backup before any deletions

## EXECUTION PROTOCOLS:

- 🎯 PRE-DELETION: List ALL files, scan dependencies, show impact
- 💾 Create FULL module backup before modification
- 📖 Update frontmatter `editsPerformed` array with removal details
- 🚫 FORBIDDEN to proceed without exact confirmation phrase match
- ⚠️ If ANY step fails, ABORT and restore from backup

## CONTEXT BOUNDARIES:

- Available context: Module path, workflow name from currentTarget
- Focus: Safe removal with comprehensive safety checks
- Limits: Cannot remove last workflow if module requires workflows
- Dependencies: Must scan all agents and workflows for references

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Removal Context

Read from {outputFile} frontmatter:
- `modulePath`: Path to the module being edited
- `module_name`: Name of the module
- `currentTarget.name`: Name of workflow to remove (e.g., "create-prd")
- `currentTarget.subtype`: Type of workflow (Standalone/Legacy)

Display:
```
⚠️  DESTRUCTIVE OPERATION WARNING ⚠️

Preparing to remove workflow: {currentTarget.name}
Module: {module_name}
Type: {currentTarget.subtype}

Running pre-removal safety checks...
```

### 2. PRE-REMOVAL CHECK 1: Enumerate All Files

Build complete list of files that will be deleted.

**For Standalone workflows:**
- Scan directory: `{modulePath}/workflows/{workflow-name}/`
- List ALL files recursively:
  - workflow.md
  - steps/step-01-*.md
  - steps/step-02-*.md
  - ... (all step files)
  - templates/* (if exists)
  - data/* (if exists)
  - Any other files in the directory

**For Legacy workflows:**
- Single file: `{modulePath}/workflows/{workflow-name}.md`

Store file count and paths.

Display:
```
═══════════════════════════════════════════════
PRE-REMOVAL CHECK 1: File Enumeration
═══════════════════════════════════════════════

The following files will be PERMANENTLY DELETED:

{modulePath}/workflows/{workflow-name}/workflow.md
{modulePath}/workflows/{workflow-name}/steps/step-01-init.md
{modulePath}/workflows/{workflow-name}/steps/step-02-concept.md
{modulePath}/workflows/{workflow-name}/steps/step-03-structure.md
... [list ALL files]

Total files to delete: {count}

═══════════════════════════════════════════════
```

### 3. PRE-REMOVAL CHECK 2: Dependency Scan

Scan the entire module for references to this workflow.

#### 3.1 Scan Agent Files

For each agent in `{modulePath}/agents/`:
- Read agent file completely
- Search for references to workflow name:
  - In frontmatter (workflow references)
  - In body (documentation, instructions)
  - In examples or command references

#### 3.2 Scan Other Workflows

For each workflow in `{modulePath}/workflows/` (excluding the one being removed):
- Read workflow.md and all step files
- Search for references to workflow name:
  - Delegation calls
  - Routing references
  - Documentation mentions

#### 3.3 Scan Module.yaml

Check for references beyond the workflows array:
- Default workflows
- Required workflows
- Custom configuration references

Display results:
```
═══════════════════════════════════════════════
PRE-REMOVAL CHECK 2: Dependency Scan
═══════════════════════════════════════════════

Scanning for references to '{workflow-name}'...

Agents referencing this workflow:
  → analyst.md (line 45: "Use create-prd workflow for...")
  → architect.md (line 102: "Delegates to create-prd")
  [List all or "✓ No references found"]

Workflows referencing this workflow:
  → review-code/step-03.md (line 67: routing reference)
  [List all or "✓ No references found"]

Module.yaml references:
  → workflows array (registry entry - will be removed)
  [List any other references or "✓ No other references"]

═══════════════════════════════════════════════

⚠️  WARNING: {count} references found that may break after removal
```

If references found, add warning:
```
⚠️  IMPACT: Removing this workflow will affect {count} other components
    These components may fail or behave unexpectedly after removal
    Consider updating references before proceeding
```

### 4. PRE-REMOVAL CHECK 3: Full Impact Analysis

Compile comprehensive impact summary:

```
═══════════════════════════════════════════════
DESTRUCTIVE OPERATION IMPACT ANALYSIS
═══════════════════════════════════════════════

Operation: REMOVE workflow '{workflow-name}'
Severity: CRITICAL
Reversibility: Low (requires manual restoration from backup)

WHAT WILL BE DELETED:
  • {count} files permanently removed
  • Complete workflow directory structure
  • All workflow history and content

WHAT WILL BE MODIFIED:
  • module.yaml (workflows array entry removed)

POTENTIAL BREAKING CHANGES:
  • {count} agents reference this workflow
  • {count} workflows delegate to this workflow
  • {count} other references found

BACKUP STATUS:
  → Full module backup will be created before deletion

RISK ASSESSMENT: {HIGH/CRITICAL}
  [Brief assessment of specific risks]

═══════════════════════════════════════════════
```

### 5. Require Explicit Confirmation

Present confirmation requirement:

```
═══════════════════════════════════════════════
CONFIRMATION REQUIRED
═══════════════════════════════════════════════

To proceed with this PERMANENT deletion, you must type the exact phrase:

    DELETE {workflow-name}

Type the confirmation phrase exactly as shown above, or type 'CANCEL' to abort.

Confirmation:
```

Wait for user input.

#### 5.1 Validate Confirmation

Compare user input to required phrase:

**If exact match "DELETE {workflow-name}":**
- Proceed to step 6

**If user types "CANCEL" or any variation:**
- Display: "Workflow removal CANCELLED. Returning to edit menu."
- Route back to step-03-select.md (do NOT proceed to deletion)

**If mismatch (wrong phrase, typo, etc.):**
- Display:
```
❌ CONFIRMATION MISMATCH

You entered: "{user-input}"
Required phrase: "DELETE {workflow-name}"

The phrases must match exactly. Please try again or type 'CANCEL' to abort.

Confirmation:
```
- Loop back to wait for correct input

### 6. Create Full Module Backup

ONLY after confirmation is validated:

Create comprehensive backup:

```
Backup location: {modulePath}/../{module-name}-backup-{timestamp}/
```

Copy entire module directory:
- All agents
- All workflows
- module.yaml
- All configuration
- All documentation

Display:
```
═══════════════════════════════════════════════
Creating Full Module Backup
═══════════════════════════════════════════════

Backup location: {modulePath}/../{module-name}-backup-{timestamp}/

Copying:
  ✓ agents/
  ✓ workflows/
  ✓ module.yaml
  ✓ configuration files
  ✓ documentation

Backup complete. Total size: {size}

═══════════════════════════════════════════════
```

### 7. Execute Removal Sequence

#### 7.1 FIRST: Remove from module.yaml

This is critical order - remove registry entry BEFORE deleting files.

1. Read {modulePath}/module.yaml
2. Parse workflows array
3. Remove entry where name equals {workflow-name}
4. Write updated module.yaml

**Error Handling:**
```
IF module.yaml update fails:
  - Display error message
  - Restore module.yaml from backup
  - ABORT operation completely
  - Display: "Removal ABORTED - module.yaml update failed. Backup restored."
  - Route to step-05-validate.md
  - EXIT this step
```

Display on success:
```
✓ Removed workflow entry from module.yaml workflows array
```

#### 7.2 SECOND: Delete Workflow Directory

Only after module.yaml successfully updated:

**For Standalone workflows:**
```
rm -rf {modulePath}/workflows/{workflow-name}/
```

**For Legacy workflows:**
```
rm {modulePath}/workflows/{workflow-name}.md
```

**Error Handling:**
```
IF directory/file deletion fails:
  - Display warning: "Partial deletion - module.yaml updated but files remain"
  - List files that could not be deleted
  - Display: "Manual cleanup required: {file-list}"
  - Continue to tracking (do NOT abort)
```

Display on success:
```
✓ Deleted workflow directory: {modulePath}/workflows/{workflow-name}/
✓ Removed {count} files
```

#### 7.3 Verify Deletion Complete

Confirm files no longer exist:

```
Check: {modulePath}/workflows/{workflow-name}/ does not exist
Check: module.yaml workflows array does not contain {workflow-name}
```

Display:
```
✓ Verification complete - workflow fully removed
```

### 8. Update Session Tracking

Update {outputFile} frontmatter `editsPerformed` array:

```yaml
editsPerformed:
  - type: 'workflow-remove'
    workflow_name: '{workflow-name}'
    workflow_type: 'standalone' | 'legacy'
    files_deleted_count: {count}
    files_deleted:
      - '{modulePath}/workflows/{workflow-name}/workflow.md'
      - '{modulePath}/workflows/{workflow-name}/steps/step-01-init.md'
      - ... [all deleted files]
    files_modified:
      - '{modulePath}/module.yaml'
    backup_location: '{modulePath}/../{module-name}-backup-{timestamp}/'
    dependencies_found: {count}
    dependency_details:
      - 'analyst.md: line 45'
      - ... [all references found]
    timestamp: '{ISO8601-timestamp}'
    severity: 'CRITICAL'
```

### 9. Present Removal Summary

Display:
```
═══════════════════════════════════════════════
Workflow Removal Complete
═══════════════════════════════════════════════

Removed Workflow: {workflow-name}
Type: {standalone/legacy}

Files Deleted: {count}
  → {modulePath}/workflows/{workflow-name}/ (entire directory)

Configuration Updated:
  ✓ module.yaml (removed from workflows array)

Backup Location:
  → {modulePath}/../{module-name}-backup-{timestamp}/

Dependencies Detected: {count}
  ⚠️  {count} components referenced this workflow
  → Review references to prevent breakage:
    - analyst.md (line 45)
    - architect.md (line 102)
    [list all]

NEXT STEPS:
  1. Validation will check module integrity
  2. Review and update components that referenced this workflow
  3. Test module functionality
  4. Remove backup after confirming everything works

═══════════════════════════════════════════════
```

### 10. Present MENU OPTIONS

Display: "**Select an Option:** [C] Continue to Validation"

#### Menu Handling Logic:

- IF C: Update frontmatter `stepsCompleted` to add "4b-workflow-remove", save {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: Help user respond then [Redisplay Menu Options](#10-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can ask questions about the removal or impacts - always respond and then redisplay the menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN user selects 'C' (Continue option) and the workflow has been safely removed with all safety protocols followed, will you then:

1. Update frontmatter `stepsCompleted` to include "4b-workflow-remove"
2. Save {outputFile} with complete editsPerformed tracking including dependency warnings
3. Load, read entire file, then execute `{nextStepFile}` to begin validation

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All files enumerated before deletion
- Comprehensive dependency scan performed
- Full impact analysis displayed
- Exact confirmation phrase required and validated
- Full module backup created before any modifications
- module.yaml updated BEFORE file deletion
- Workflow directory successfully deleted
- Deletion verified complete
- Session tracking updated with full removal details
- Dependencies documented in editsPerformed
- Summary displayed with backup location
- Menu presented and user selected 'C'
- Frontmatter updated before loading validation step

### ❌ SYSTEM FAILURE:

- Deleting files without listing them first
- Skipping dependency scan
- Proceeding without exact confirmation phrase match
- Not creating full module backup
- Deleting files before updating module.yaml
- Continuing after module.yaml update failure
- Not documenting dependencies in tracking
- Proceeding to validation without user selecting 'C'
- Not updating stepsCompleted before loading next step
- Accepting variations of confirmation phrase
- Not handling partial deletion errors properly

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE. For DESTRUCTIVE operations, ANY deviation from safety protocols is CRITICAL FAILURE.
