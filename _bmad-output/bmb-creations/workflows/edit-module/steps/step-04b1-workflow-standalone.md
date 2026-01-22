---
name: 'step-04b1-workflow-standalone'
description: 'Edit modern standalone workflows with step-file architecture through guided section-based editing of workflow.md and individual step files'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04b1-workflow-standalone.md'
nextStepFile: '{workflow_path}/steps/step-05-validate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Template References
workflowEditTemplate: '{workflow_path}/templates/workflow-edit-section.md'
stepEditTemplate: '{workflow_path}/templates/step-edit-section.md'
---

# Step 04b1: Standalone Workflow Editing

## STEP GOAL:

To edit modern standalone workflows with step-file architecture by providing guided access to workflow.md sections (frontmatter, goal, role, architecture, rules) and individual step files (goal, rules, sequence, menu, metrics), enabling precise modifications while maintaining workflow coherence and BMAD compliance.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist with systems-thinking perspective
- ✅ If you already have been given communication or persona patterns, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring workflow architecture expertise and step-file mastery
- ✅ User brings their workflow improvement intent and domain knowledge
- ✅ Maintain strategic, holistic, collaborative tone throughout

### Step-Specific Rules:

- 🎯 Focus ONLY on standalone workflow editing (workflow.md + /steps/ architecture)
- 🚫 FORBIDDEN to modify files without showing user the changes first
- 💬 Always display current content before allowing edits
- 📋 Validate step file references and dependencies after edits
- 🔒 Use atomic swap pattern for file writes (write to .tmp, then rename)

## EXECUTION PROTOCOLS:

- 🎯 Present workflow structure in navigable menu format
- 💾 Backup is already created by step-04b-workflow-load.md
- 📖 Update session editsPerformed array with each modification
- 📖 Update frontmatter `stepsCompleted` to add '04b1' before loading next step
- 🚫 FORBIDDEN to proceed to validation until all requested edits are complete

## CONTEXT BOUNDARIES:

- Workflow details loaded from session state: `{workflowBeingEdited}`, `{workflowPath}`
- Workflow type confirmed as 'standalone' with /steps/ directory
- Backup already exists at: `{workflowBackupPath}`
- Focus on editing existing files, not structural changes (add/remove/reorder are Phase 2+)
- This step produces modified workflow.md and/or step files

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Workflow Information

Retrieve workflow metadata from session state:

- Workflow name: `{workflowBeingEdited}`
- Workflow path: `{workflowPath}`
- Backup location: `{workflowBackupPath}`
- Structure details: `{workflowStructure}`

Read the workflow.md main file and scan /steps/ directory to get current file list.

### 2. Present Workflow Structure

Display comprehensive workflow structure:

```
Standalone Workflow Editor
═══════════════════════════════════════════════════
Workflow: {workflowBeingEdited}
Type: Modern Step-File Architecture
Backup: ✅ Created at {workflowBackupPath}

Structure:
  Main File: workflow.md
  Steps ({stepCount} files):
    {step_file_list}

What would you like to edit?
```

### 3. Edit Target Selection Menu

Present target selection options:

```
Edit Target Selection
═══════════════════════════════════════════════════

[M] Main workflow.md file
    Edit: frontmatter, goal, role, architecture, rules, protocols

[S] Specific step file
    Select from step list, then edit sections

[A] Add new step (Phase 2 - Not Yet Available)

[R] Remove step (DESTRUCTIVE - Phase 2)

[O] Reorder steps (Phase 3 - Not Yet Available)

[X] Cancel (return to main menu)

Select option (M/S/A/R/O/X):
```

**Wait for user selection.** Do not proceed until user provides input.

### 4. Route Based on Selection

Handle user selection:

#### [M] Main Workflow.md File Edit

Execute main workflow file editing sequence:

**4M.1 Display Workflow.md Structure:**

Read and parse workflow.md, then display editable sections:

```
workflow.md Sections
═══════════════════════════════════════════════════

[1] Frontmatter (YAML metadata)
[2] Workflow Goal
[3] Role Definition
[4] Architecture & Flow
[5] Mandatory Rules
[6] Execution Protocols
[X] Cancel

Which section to edit? (1-6, X):
```

**4M.2 Section-Specific Editing:**

For each section selected:
- Display current content with line numbers
- Ask: "What changes would you like to make to this section?"
- Collect user's edit intent
- Show proposed changes as diff
- Ask for confirmation: "Apply these changes? (Y/N)"
- If Y: Apply changes using atomic swap
- If N: Allow refinement or cancel

**4M.3 Record Edit:**

Update session state editsPerformed:
```yaml
editsPerformed:
  - type: 'workflow-main'
    file: 'workflow.md'
    section: '{section_name}'
    timestamp: '{timestamp}'
    description: '{brief_description}'
```

**4M.4 Continue or Return:**

Ask: "Edit another section of workflow.md? (Y/N)"
- If Y: Return to section menu (4M.1)
- If N: Return to edit target selection menu (step 3)

#### [S] Specific Step File Edit

Execute step file editing sequence:

**4S.1 List Step Files:**

Display numbered step file list:

```
Select Step File to Edit
═══════════════════════════════════════════════════

{step_file_list_numbered}

Example:
[1] step-01-init.md
[2] step-02-analyze.md
[3] step-03-select.md
...

[X] Cancel

Select step (1-{step_count}, X):
```

**4S.2 Display Step File Structure:**

After user selects a step file, read and display its editable sections:

```
{selected_step_file} Sections
═══════════════════════════════════════════════════

[1] Frontmatter (path references, variables)
[2] Step Goal
[3] Mandatory Execution Rules
[4] Execution Protocols
[5] Sequence of Instructions
[6] Menu Options & Handling
[7] Success/Failure Metrics
[X] Cancel

Which section to edit? (1-7, X):
```

**4S.3 Section-Specific Editing:**

For each section selected:
- Display current content with line numbers
- Ask: "What changes would you like to make to this section?"
- Collect user's edit intent
- Show proposed changes as diff
- Ask for confirmation: "Apply these changes? (Y/N)"
- If Y: Apply changes using atomic swap
- If N: Allow refinement or cancel

**4S.4 Record Edit:**

Update session state editsPerformed:
```yaml
editsPerformed:
  - type: 'workflow-step'
    file: '{selected_step_file}'
    section: '{section_name}'
    timestamp: '{timestamp}'
    description: '{brief_description}'
```

**4S.5 Continue or Return:**

Ask: "Edit another section of {selected_step_file}? (Y/N)"
- If Y: Return to section menu (4S.2)
- If N: Ask "Edit a different step file? (Y/N)"
  - If Y: Return to step list (4S.1)
  - If N: Return to edit target selection menu (step 3)

#### [A] Add New Step (Phase 2)

Display:
```
⚠️  Add New Step - Phase 2 Feature
═══════════════════════════════════════════════════

This feature is planned for Phase 2 and is not yet available.

To add a new step to this workflow:
1. Use the create-workflow workflow to generate step templates
2. Manually integrate the new step
3. Update step references in workflow.md

Returning to edit target selection...
```

Return to edit target selection menu (step 3).

#### [R] Remove Step (Phase 2)

Display:
```
⚠️  Remove Step - DESTRUCTIVE Operation (Phase 2)
═══════════════════════════════════════════════════

This feature is planned for Phase 2 with enhanced safety checks:
- Dependency analysis (which steps reference this step?)
- Automatic renumbering of remaining steps
- Update of all step references in workflow.md
- Validation of workflow coherence after removal

Returning to edit target selection...
```

Return to edit target selection menu (step 3).

#### [O] Reorder Steps (Phase 3)

Display:
```
⚠️  Reorder Steps - Phase 3 Feature
═══════════════════════════════════════════════════

This advanced feature is planned for Phase 3:
- Interactive drag-and-drop style reordering
- Automatic renumbering cascade
- Reference update across all files
- Flow validation after reordering

Returning to edit target selection...
```

Return to edit target selection menu (step 3).

#### [X] Cancel

Display: "Returning to main component selection menu..."

Update frontmatter `stepsCompleted` to include '04b1', then route to step-03-select.md.

### 5. Completion Check

After each edit operation returns to the edit target selection menu (step 3), check if user wants to continue:

Display the edit target selection menu again.

User can:
- Continue editing (select M, S, etc. again)
- Select X to exit standalone workflow editing

When user selects [X] to exit, proceed to step 6.

### 6. Present MENU OPTIONS

After user indicates editing is complete (selected X from edit target selection):

Display:
```
Standalone Workflow Editing Complete
═══════════════════════════════════════════════════

Edits performed: {edit_count}
Files modified: {modified_file_list}

**Select an Option:**
[A] Advanced Elicitation
[P] Party Mode
[C] Continue to Validation
```

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}, then redisplay this menu
- IF P: Execute {partyModeWorkflow}, then redisplay this menu
- IF C: Update frontmatter `stepsCompleted` to include '04b1', save session state to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#6-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then redisplay the menu

## CRITICAL STEP COMPLETION NOTE

This step completes when:
1. ✅ User has finished all desired workflow and step file edits
2. ✅ All changes written to files using atomic swap pattern
3. ✅ Session state updated with all edits in editsPerformed array
4. ✅ User selects [C] Continue from the final menu
5. ✅ frontmatter `stepsCompleted` includes '04b1'

ONLY WHEN [C continue option] is selected and all edits are recorded, will you then load and read fully `{nextStepFile}` (step-05-validate.md) to execute workflow validation.

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Workflow structure correctly presented to user
- User able to navigate between edit targets smoothly
- Current content displayed before allowing edits
- Changes shown as diff and confirmed before applying
- All file writes use atomic swap pattern (.tmp then rename)
- Session state editsPerformed array updated for each modification
- Step file references remain valid after edits
- Menu presented and user input handled correctly
- frontmatter `stepsCompleted` includes '04b1' before proceeding
- Content properly saved before advancing to validation

### ❌ SYSTEM FAILURE:

- Presenting edit options before loading workflow structure
- Modifying files without showing changes to user first
- Not using atomic swap pattern for file writes
- Proceeding to Phase 2/3 features that aren't implemented
- Not updating editsPerformed array after modifications
- Breaking step file references during edits
- Proceeding to validation without user selecting 'C'
- Not displaying menu after Advanced Elicitation or Party Mode
- Skipping sections or optimizing the edit sequence
- Not validating step references after editing

**Master Rule:** This is a precision editing workflow. Every change must be shown to the user and confirmed before application. Phase 2 and Phase 3 features must explicitly indicate they are not yet available. Never proceed to validation without user's explicit 'C' selection.
