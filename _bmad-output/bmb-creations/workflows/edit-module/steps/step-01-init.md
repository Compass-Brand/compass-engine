---
name: 'step-01-init'
description: 'Initialize the edit-module workflow by detecting continuation state and creating session document'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-01-init.md'
nextStepFile: '{workflow_path}/steps/step-02-analyze.md'
continueFile: '{workflow_path}/steps/step-01b-continue.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'
templateFile: '{workflow_path}/templates/edit-session.template.md'

# Template References
# This step doesn't use content templates, only the main template
---

# Step 1: Workflow Initialization

## STEP GOAL:

To initialize the edit-module workflow by detecting continuation state, selecting the module to edit, creating the output document, and preparing for the first collaborative editing session.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring module architecture expertise and structured editing guidance
- ✅ User brings knowledge of their modules and editing requirements
- ✅ Together we produce precise, safe module edits

### Step-Specific Rules:

- 🎯 Focus ONLY on initialization and setup
- 🚫 FORBIDDEN to look ahead to future steps
- 💬 Handle initialization professionally with strategic, holistic communication
- 🚪 DETECT existing workflow state and handle continuation properly

## EXECUTION PROTOCOLS:

- 🎯 Show analysis before taking any action
- 💾 Initialize document and update frontmatter
- 📖 Set up frontmatter `stepsCompleted: [1]` before loading next step
- 🚫 FORBIDDEN to load next step until setup is complete

## CONTEXT BOUNDARIES:

- Variables from workflow.md are available in memory
- Previous context = what's in output document + frontmatter
- Don't assume knowledge from other steps
- Module discovery happens in this step

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Module Selection

Ask user to select a module to edit using one of these methods:

**Method A: Module Discovery**
- Scan for BMAD modules in `{project-root}/_bmad/`
- List discovered modules with numbers:
  ```
  Discovered BMAD Modules:
  [1] bmm (BMAD Module Manager)
  [2] bmb (BMAD Module Builder)
  [3] custom/my-module

  Select module number or provide path:
  ```

**Method B: Direct Path**
- User provides path: `{project-root}/_bmad/bmm/`
- Validate module exists and has valid structure

After selection, set `{module_path}` and `{module_name}`.

### 2. Check for Existing Workflow

Check if an edit session already exists for this module:

- Look for file at `{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-*.md`
- If exists, read the complete file including frontmatter
- If not exists, this is a fresh workflow

### 3. Handle Continuation (If Document Exists)

If the document exists and has frontmatter with `stepsCompleted`:

- **STOP here** and load `{continueFile}` immediately
- Do not proceed with any initialization tasks
- Let step-01b handle the continuation logic

### 4. Handle Completed Workflow

If the document exists AND step 7 is in `stepsCompleted` (workflow complete):

- Ask user: "I found an existing edit session from [date]. Would you like to:
  1. Create a new edit session
  2. Update/review the existing session"
- If option 1: Create new document with timestamp suffix
- If option 2: Load step-01b-continue.md

### 5. Fresh Workflow Setup (If No Document)

If no document exists or no `stepsCompleted` in frontmatter:

#### A. Pre-flight Checks

Run validation checks on the selected module:

**Check 1: Module Structure Validation**
- Verify module.yaml exists
- Verify basic module structure is valid
- If issues found: "Module validation issues detected. Would you like to:
  [F] Fix issues first (recommended)
  [P] Proceed anyway
  [A] Abort"

**Check 2: Git Status**
- Check if module is in git repository
- Check for uncommitted changes
- If uncommitted changes: "Uncommitted changes detected in module:
  [files list]

  Recommendation: Commit changes before editing.
  [C] Commit first
  [P] Proceed anyway
  [A] Abort"

#### B. Create Output Directory Structure

Create directory structure:
```
{bmb_creations_output_folder}/modules/{module_name}/
```

#### C. Create Backup Directory

Create backup directory in module:
```
{module_path}/.backup/
```

#### D. Create Initial Session Document

Copy the template from `{templateFile}` to `{outputFile}`

Initialize frontmatter with:

```yaml
---
stepsCompleted: [1]
lastStep: 'step-01-init'
lastStepIndex: 1
currentTarget: null
editsPerformed: []
backupsCreated: []
lastValidation: null
started: [current timestamp]
lastModified: [current timestamp]
user_name: {user_name}
module_name: {module_name}
module_path: {module_path}
sessionId: {sessionId}
---
```

#### E. Show Welcome Message

"Welcome to the BMAD Module Editor! I'll guide you through a structured process to safely edit **{module_name}**.

This workflow provides:
- Deep module structure analysis
- Safe editing with automatic backups
- Real-time validation
- Comprehensive change tracking

Let's begin by analyzing your module structure."

### 6. Present MENU OPTIONS

Display: **Proceeding to module analysis...**

#### EXECUTION RULES:

- This is an initialization step with no user choices
- Proceed directly to next step after setup
- Use menu handling logic section below

#### Menu Handling Logic:

- After setup completion, immediately load, read entire file, then execute `{nextStepFile}` to begin deep module analysis

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Document created from template (for fresh workflows)
- Update frontmatter `stepsCompleted` to add 1 at the end of the array before loading next step
- Frontmatter initialized with `stepsCompleted: [1]`
- Module validated or user explicitly chose to proceed
- User welcomed to the process
- Ready to proceed to step 2
- OR existing workflow properly routed to step-01b-continue.md

### ❌ SYSTEM FAILURE:

- Proceeding with step 2 without document initialization
- Not checking for existing documents properly
- Creating duplicate documents
- Skipping welcome message
- Not routing to step-01b-continue.md when appropriate
- Skipping pre-flight validation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN initialization setup is complete and document is created (OR continuation is properly routed), will you then immediately load, read entire file, then execute `{nextStepFile}` to begin deep module structure analysis.
