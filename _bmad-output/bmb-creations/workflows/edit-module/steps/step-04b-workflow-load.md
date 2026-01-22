---
name: 'step-04b-workflow-load'
description: 'Load and analyze selected workflow directory, detect structure type (standalone vs legacy), create backup, and route to appropriate editing workflow'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04b-workflow-load.md'
nextStepStandalone: '{workflow_path}/steps/step-04b1-workflow-standalone.md'
nextStepLegacy: '{workflow_path}/steps/step-04b2-workflow-legacy.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Backup Reference
backupPath: '{bmb_creations_output_folder}/modules/{module_name}/backups/workflow-{workflow_name}-{timestamp}'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 04b: Workflow Loading & Analysis

## STEP GOAL:

To load the selected workflow directory, analyze its structure to detect whether it follows standalone (modern step-file architecture) or legacy (single-file or simple YAML) format, create a complete backup of the workflow directory, and intelligently route to the appropriate editing workflow based on the detected type.

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
- ✅ You bring architectural expertise and structural analysis capabilities
- ✅ User brings their workflow editing intent
- ✅ Maintain strategic, holistic, collaborative tone throughout

### Step-Specific Rules:

- 🎯 Focus ONLY on workflow structure detection and backup creation
- 🚫 FORBIDDEN to make ANY edits during this step - this is analysis only
- 💬 Always create complete directory backup before proceeding
- 📋 Detect workflow type with 100% accuracy using defined criteria
- 🔒 If backup fails, ABORT and raise error E003

## EXECUTION PROTOCOLS:

- 🎯 Analyze workflow directory structure to determine type
- 💾 Create complete backup of entire workflow directory (not just single file)
- 📖 Update session workflowBackupPath reference
- 📖 Update frontmatter `stepsCompleted` to add '04b' before routing to next step
- 🚫 FORBIDDEN to proceed without successful backup creation

## CONTEXT BOUNDARIES:

- Workflow path loaded from session state: `{workflow_path_selected}`
- Focus ONLY on structure analysis and backup, not content editing
- This step determines routing logic for all subsequent workflow edits
- Backup must include: workflow.md (or .yaml), all /steps/ files, all /templates/, all /data/
- Produces: workflow type detection result, backup directory reference

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Workflow Directory

Read the selected workflow directory from session state `{workflow_path_selected}`.

**Validation:**
- Verify directory exists at specified path
- If not found: Raise error **E007 (Directory Not Found)**
  ```
  ERROR E007: Workflow directory not found
  Path: {workflow_path_selected}
  Action: Return to step-03-select.md for re-selection
  ```

### 2. Analyze Workflow Structure

Perform comprehensive structure analysis:

**Detection Algorithm:**

```
STANDALONE DETECTION (Modern Step-File Architecture):
  ✅ Has workflow.md as main file
  ✅ Has /steps/ subdirectory
  ✅ /steps/ contains at least one step-*.md file
  ✅ Step files follow naming pattern: step-NN-*.md

LEGACY DETECTION (Older Formats):
  ✅ Has workflow.yaml instead of workflow.md, OR
  ✅ Has workflow.md but NO /steps/ subdirectory, OR
  ✅ Single .md file without step-file architecture, OR
  ✅ Inline step definitions in main file
```

**Structure Scan - Collect Information:**
- Main file name and path (workflow.md or workflow.yaml or other)
- Presence and contents of /steps/ directory
- Step file count (if standalone)
- Step file names (if standalone)
- Presence of /templates/ directory (optional)
- Presence of /data/ directory (optional)
- Total file count in workflow directory

**Display Analysis Results:**

```
Workflow Structure Analysis
═══════════════════════════════════════════════════
Workflow: {workflow_name}
Location: {workflow_path_selected}

Type Detected: [STANDALONE | LEGACY]

Structure:
  Main File: {main_file_name}
  Steps Directory: [YES | NO]
  Step Files: {step_count} files
  Templates: [YES | NO]
  Data Files: [YES | NO]

Total Files: {total_file_count}
```

### 3. Create Complete Directory Backup

Create full backup of entire workflow directory:

**Backup Procedure:**

1. Generate timestamp: `{timestamp}` = YYYYMMDD-HHMMSS format
2. Create backup path: `{backupPath}` as defined in frontmatter
3. Copy ENTIRE workflow directory recursively to backup location
4. Verify backup completed successfully

**Verification Steps:**
- Confirm all files copied (file count matches)
- Confirm directory structure preserved
- Test read access to backup location

**On Backup Success:**
```
✅ Backup Created Successfully
Location: {backupPath}
Files Backed Up: {file_count}
```

**On Backup Failure:**
```
ERROR E003: Backup Creation Failed
Attempted Path: {backupPath}
Reason: {error_details}
Action: ABORT workflow editing - cannot proceed safely without backup
```

If backup fails, STOP execution and return to step-03-select.md.

### 4. Update Session State

Update the output file frontmatter with:

```yaml
workflowBeingEdited: '{workflow_name}'
workflowPath: '{workflow_path_selected}'
workflowType: '[standalone|legacy]'
workflowBackupPath: '{backupPath}'
workflowStructure:
  mainFile: '{main_file_name}'
  stepCount: {step_count}
  hasTemplates: [true|false]
  hasData: [true|false]
```

### 5. Route to Appropriate Editing Workflow

Based on detected type, route to the correct editing step:

**Routing Logic:**

```
IF workflowType = 'standalone':
  Display: "Detected modern standalone workflow architecture."
  Display: "Routing to advanced workflow editor..."
  Next Step: {nextStepStandalone} (step-04b1-workflow-standalone.md)

IF workflowType = 'legacy':
  Display: "Detected legacy workflow format."
  Display: "Routing to legacy workflow editor..."
  Next Step: {nextStepLegacy} (step-04b2-workflow-legacy.md)
```

### 6. Auto-Proceed to Next Step

This is a structural routing step with no user content creation.

**Display:**
```
Workflow Loaded & Backed Up
Proceeding to {workflowType} editor...
```

**Execution:**
- Update frontmatter `stepsCompleted` to include '04b'
- Load entire next step file based on routing logic above
- Execute the routed step file

## CRITICAL STEP COMPLETION NOTE

This step completes when:
1. ✅ Workflow directory structure analyzed successfully
2. ✅ Workflow type detected (standalone or legacy)
3. ✅ Complete backup created and verified
4. ✅ Session state updated with workflow details and backup path
5. ✅ Routing determined and next step loaded

This is an **auto-proceed** step. After backup creation and routing determination, immediately load and execute the appropriate next step file.

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Workflow directory exists and is readable
- Structure correctly analyzed and type detected
- Complete directory backup created successfully at {backupPath}
- All files verified in backup location
- Session state updated with workflow metadata
- Correct next step determined and loaded based on type
- frontmatter `stepsCompleted` includes '04b'

### ❌ SYSTEM FAILURE:

- Proceeding without verifying directory exists (E007)
- Incorrect workflow type detection
- Creating backup of only main file instead of entire directory
- Proceeding when backup creation fails (E003)
- Not updating session state with backup path
- Routing to wrong editing workflow
- Allowing user to proceed without backup
- Skipping structure analysis steps

**Master Rule:** This step is CRITICAL for data safety. Backup creation is MANDATORY. Any failure in backup creation must ABORT the workflow editing process. Never proceed to editing without a verified backup.
