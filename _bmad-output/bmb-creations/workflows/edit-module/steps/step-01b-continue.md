---
name: 'step-01b-continue'
description: 'Handle workflow continuation from previous edit-module session'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-01b-continue.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'
workflowFile: '{workflow_path}/workflow.md'

# Template References
# This step uses the existing session document for analysis
---

# Step 1B: Workflow Continuation

## STEP GOAL:

To resume the edit-module workflow from where it was left off, ensuring smooth continuation without loss of context or progress.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist
- ✅ If you already have been given a name, communication_style and identity, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring module architecture expertise and structured editing guidance
- ✅ User brings knowledge of their modules and editing requirements
- ✅ Maintain collaborative, strategic, holistic tone throughout

### Step-Specific Rules:

- 🎯 Focus ONLY on analyzing and resuming workflow state
- 🚫 FORBIDDEN to modify content completed in previous steps
- 💬 Maintain continuity with previous sessions
- 🚪 DETECT exact continuation point from frontmatter of incomplete file {outputFile}

## EXECUTION PROTOCOLS:

- 🎯 Show your analysis of current state before taking action
- 💾 Keep existing frontmatter `stepsCompleted` values intact
- 📖 Review the session document content already generated in {outputFile}
- 🚫 FORBIDDEN to modify content that was completed in previous steps
- 📝 Update frontmatter with continuation timestamp when resuming

## CONTEXT BOUNDARIES:

- Current edit session document is already loaded
- Previous context = complete session document + existing frontmatter
- Module analysis and edits already gathered in previous sessions
- Last completed step = last value in `stepsCompleted` array from frontmatter

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Analyze Current State

Review the frontmatter of {outputFile} to understand:

- `stepsCompleted`: Which steps are already done (the rightmost value is the last step completed)
- `lastStep`: Filename of last completed step
- `lastStepIndex`: Numeric index for routing
- `started`: Original workflow start timestamp
- `lastModified`: Last activity timestamp
- `currentTarget`: Component currently being edited (if mid-edit)
- `editsPerformed`: Array of completed edits
- `backupsCreated`: Array of backup file references

Example: If `stepsCompleted: [1, 2, 3, 4.1]`, then step 4.1 was the last completed step.

### 2. Determine Next Step

Based on `lastStepIndex`:

| Last Index | Next Step | File to Load |
|------------|-----------|--------------|
| < 2 | Analyze module | `step-02-analyze.md` |
| 2 | Select edit target | `step-03-select.md` |
| 3 | Based on currentTarget | Appropriate step-04x |
| 4.x | Validate | `step-05-validate.md` |
| 5 | Iterate decision | `step-06-iterate.md` |
| 6 | Back to select menu | `step-03-select.md` |

### 3. Check for Incomplete Edit

If `currentTarget` is set but the corresponding step-04x isn't in `stepsCompleted`:

**This indicates an interrupted edit.** Present recovery options:

```
"I see you were in the middle of editing **{currentTarget}** when the session was interrupted.

The file may be in a partially edited state. Would you like to:

[R] Resume - Continue the edit from where you left off
[B] Restore - Restore from backup and start this edit fresh
[S] Skip - Skip this edit and return to the main menu"
```

Handle user selection:
- [R]: Load the appropriate step-04x file for the component type
- [B]: Restore backup, clear currentTarget, route to step-03-select.md
- [S]: Clear currentTarget, route to step-03-select.md

### 4. Welcome Back Dialog

Present a warm, context-aware welcome:

"Welcome back, {user_name}! I found your in-progress edit session for **{module_name}**.

**Session Status:**
- Started: {started}
- Last Activity: {lastModified}
- Edits Made: {editsPerformed.length}
- Last Step: {lastStep}

**Edits Completed So Far:**"

Then list each edit from `editsPerformed` array:
```
- [modified] agent: analyst.md (2026-01-07T14:30:00)
- [added] workflow: create-plan (2026-01-07T15:00:00)
```

### 5. Validate Continuation Intent

Ask confirmation questions:

"Has anything changed since our last session that might affect our approach?"
"Are you still aligned with the goals and edits made earlier?"
"Would you like to review what we've accomplished so far before continuing?"

### 6. Present MENU OPTIONS

Display: "**Resuming workflow - Select an Option:** [C] Continue to [Next Step Name]"

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and then end with display again of the menu options
- Update frontmatter with continuation timestamp when 'C' is selected

#### Menu Handling Logic:

- IF C:
  1. Update frontmatter: add `lastContinued: [current timestamp]`
  2. Update `lastModified: [current timestamp]`
  3. Load, read entire file, then execute the appropriate next step file (determined in section 2)
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#6-present-menu-options)

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN C is selected and continuation analysis is complete, will you then:

1. Update frontmatter in {outputFile} with continuation timestamp
2. Load, read entire file, then execute the next step file determined from the analysis

Do NOT modify any other content in the output document during this continuation step.

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Correctly identified last completed step from `stepsCompleted` array
- Detected and handled incomplete edit if applicable
- User confirmed readiness to continue
- Frontmatter updated with continuation timestamp
- Workflow resumed at appropriate next step

### ❌ SYSTEM FAILURE:

- Skipping analysis of existing state
- Modifying content from previous steps
- Loading wrong next step file
- Not updating frontmatter with continuation info
- Proceeding without user confirmation
- Not detecting incomplete edit state

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
