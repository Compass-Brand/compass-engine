---
name: 'step-04a1-agent-simple'
description: 'Edit simple agent files using intent-based interaction with full file or section-level modifications'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04a1-agent-simple.md'
nextStepFile: '{workflow_path}/steps/step-05-validate.md'
selectStepFile: '{workflow_path}/steps/step-03-select.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Path References
backupPath: '{module_path}/.backup/{timestamp}'
lockFile: '{module_path}/.lock/{component_name}.lock'
---

# Step 4a1: Edit Simple Agent

## STEP GOAL:

Edit a simple agent file (basic markdown without complex YAML frontmatter or extensive structure) through intent-based interaction, allowing users to modify full file content or specific sections while preserving file integrity and maintaining backup safety.

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
- ✅ User brings knowledge of their agents and editing requirements
- ✅ Together we produce precise, effective agent definitions
- ✅ Maintain strategic, holistic, systems-thinking communication style

### Step-Specific Rules:

- 🎯 Focus ONLY on simple agent editing workflow
- 🚫 FORBIDDEN to skip intent gathering or user approval
- 💬 Use intent-based questions: "What would you like to change?"
- 📝 Always show proposed changes before applying
- ✅ Preserve original formatting and style
- 🔒 CRITICAL: Update session editsPerformed array after successful edit

## EXECUTION PROTOCOLS:

- 🎯 Intent-based editing: Ask what user wants to change, not how
- 💾 Apply changes only after user approval
- 📖 Display current content before proposing changes
- 🚫 Never make assumptions about desired changes
- ✅ Preserve markdown structure and formatting
- 🔄 Iterate on proposed changes until user satisfied

## CONTEXT BOUNDARIES:

- Available context: Agent file loaded, backed up, and locked from step-04a-agent-load
- Focus: Content editing through collaborative intent-based interaction
- Limits: This step is for simple agents only (basic markdown structure)
- Dependencies: Requires successful completion of step-04a-agent-load with backup created

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Current Agent Content

Read the agent file from `{currentTarget}` (available from session frontmatter).

Parse the file structure:
- Identify H1 heading (agent name)
- Identify H2/H3 section headings
- Note any list structures, emphasis, or special formatting
- Build section map: `{section_name: content}`

Display the current agent structure:

```
Simple Agent: {agent_name}
─────────────────────────────────────────
Total Lines: {line_count}
Size: {file_size}

Structure Overview:
├─ # {h1_heading}
{detected_sections}

Ready for editing.
─────────────────────────────────────────
```

**Detected Sections Example:**
```
├─ ## Role & Purpose
├─ ## Core Responsibilities
├─ ## Communication Style
└─ ## Example Interactions
```

### 2. Gather Edit Intent

Ask the user what they want to change using intent-based questions:

**Intent Gathering Dialog:**

"What would you like to change about this agent?

You can describe:
- A specific aspect (e.g., 'make the tone more formal')
- A section to modify (e.g., 'update the core responsibilities')
- Content to add (e.g., 'add a section about error handling')
- Content to remove (e.g., 'remove the example interactions')
- A complete rewrite (e.g., 'rewrite the entire agent definition')

Please describe your desired change in natural language."

**Wait for user response.** Do NOT proceed without user input.

### 3. Clarify and Confirm Scope

Based on user's intent, determine the edit scope and confirm:

**If intent is specific (single section or aspect):**
- Identify which section(s) affected
- Display current content of those section(s)
- Confirm: "I'll modify {section_name} to {user_intent}. Is that correct?"

**If intent is broad (multiple sections or full rewrite):**
- List all sections that will change
- Confirm: "This will affect {section_count} sections: {list}. Proceed?"

**If intent is unclear:**
- Ask clarifying questions
- Example: "When you say 'make it better', do you mean:
  - More detailed explanations?
  - More concise language?
  - Different tone/style?
  - Something else?"

**Wait for confirmation.** Only proceed after user confirms scope.

### 4. Display Current Content

Show the user the exact content that will be modified:

**For Section Edit:**
```
Current Content: {section_name}
─────────────────────────────────────────
{current_section_content}
─────────────────────────────────────────

I will now propose changes based on: "{user_intent}"
```

**For Full File Edit:**
```
Current Agent File (First 30 lines shown):
─────────────────────────────────────────
{first_30_lines}
...
[{remaining_line_count} more lines]
─────────────────────────────────────────

Full rewrite will replace all {total_line_count} lines.
```

### 5. Propose Changes

Generate proposed changes based on user intent and show them for approval:

**Display Format:**
```
Proposed Changes
─────────────────────────────────────────
{section_name or "Full File"}

{proposed_new_content}
─────────────────────────────────────────

Summary of Changes:
{change_summary}

Do you approve these changes?
[Y] Yes, apply these changes
[N] No, revise the proposal
[E] Explain - tell me more about what you changed
[C] Cancel - discard and return to selection menu
```

**Change Summary Examples:**
- "Updated tone from casual to formal throughout"
- "Added 3 new responsibilities, removed 1 outdated one"
- "Expanded error handling section with 4 specific scenarios"
- "Complete rewrite: new structure with 5 sections"

**Handle user response:**

**[Y] - Apply changes:**
- Proceed to Step 6

**[N] - Revise proposal:**
- Ask: "What would you like me to change about this proposal?"
- Gather specific revision feedback
- Generate revised proposal
- Re-display and ask for approval again
- Repeat until approved or cancelled

**[E] - Explain:**
- Provide detailed explanation of changes made
- Walk through specific differences
- Highlight rationale for each change
- Then re-ask for approval (Y/N/E/C)

**[C] - Cancel:**
- Confirm: "Are you sure you want to cancel? Type 'CANCEL' to confirm."
- If confirmed: Release lock, route to `{selectStepFile}`
- If not confirmed: Re-display proposal and ask for approval

### 6. Apply Changes

**CRITICAL: Changes are applied with atomic swap pattern.**

**Application Protocol:**

1. **Create Temporary File:**
   - Write proposed content to `{currentTarget}.tmp`
   - Use atomic write operation

2. **Verify Temporary File:**
   - Read temp file back
   - Verify content matches proposal
   - Compute checksum of temp file

3. **Atomic Swap:**
   - Rename `{currentTarget}` → `{currentTarget}.old` (backup original)
   - Rename `{currentTarget}.tmp` → `{currentTarget}` (activate new)
   - Delete `{currentTarget}.old` (cleanup)

4. **Verify Final File:**
   - Read new file
   - Verify content is as expected
   - Compute new checksum

**Error Handling:**

**If write fails:**
- Preserve original file (do not modify)
- Display: "Failed to write changes: {error}"
- Offer: [R] Retry | [C] Cancel
- Do NOT proceed to validation

**If verification fails:**
- Restore from `.old` backup
- Display: "File verification failed, restored original"
- Offer: [R] Retry | [C] Cancel

**If atomic swap fails:**
- Attempt rollback: restore from `.old` if exists
- Display: "Atomic swap failed, attempting restore"
- Report final state to user

### 7. Record Edit in Session

Update the session document frontmatter to record this edit:

Add to `editsPerformed[]` array:
```yaml
editsPerformed:
  - component: "{currentTarget}"
    componentType: "agent"
    agentType: "simple"
    editType: "{section_edit | full_rewrite}"
    timestamp: "{ISO_timestamp}"
    sections_modified: [{list_of_sections}]
    change_summary: "{user_approved_summary}"
    checksum_before: "{original_checksum}"
    checksum_after: "{new_checksum}"
```

Update `lastModified` timestamp in session frontmatter.

### 8. Display Edit Confirmation

Show user the successful edit confirmation:

```
✓ Edit Applied Successfully
─────────────────────────────────────────
File: {agent_filename}
Type: {edit_type}
Sections Modified: {section_list or "Full File"}
Lines Changed: +{added} -{removed}

New Checksum: {new_checksum_first_8}...

Backup Status: Original preserved at {backup_path}
Lock Status: Still held by this session

Next: Validation
─────────────────────────────────────────
```

### 9. Present MENU OPTIONS

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue to Validation"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask} to explore alternative editing approaches
- IF P: Execute {partyModeWorkflow} to get input from other agents on the edit
- IF C: Save session state to {outputFile}, update frontmatter with this step completion, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: Help user respond, then [Redisplay Menu Options](#9-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After Advanced Elicitation or Party Mode execution completes, return to this menu
- User can chat or ask questions - always respond and then redisplay the menu options

## CRITICAL STEP COMPLETION NOTE

This step completes when:
- User intent gathered and confirmed
- Changes proposed and approved by user
- Changes applied using atomic swap pattern
- Final file verified and checksum computed
- Session frontmatter updated with edit record
- Edit confirmation displayed
- User selects [C] Continue from menu

ONLY WHEN [C continue option] is selected and all edit operations are complete and recorded, will you then save the session document to `{outputFile}`, update the frontmatter with step completion, load and read fully `{nextStepFile}` to execute step-05-validate.md and begin the validation process.

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- User intent gathered through intent-based questions (not prescriptive)
- Edit scope clarified and confirmed before proposing changes
- Current content displayed before showing proposal
- Proposed changes shown for approval before applying
- User explicitly approved changes (not assumed)
- Changes applied using atomic swap pattern (temp → old → new)
- Final file verified to match approved proposal
- Session editsPerformed array updated with complete edit record
- Backup remains intact and accessible
- Lock maintained throughout edit
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Making changes without user intent or approval
- Skipping proposal step and directly modifying file
- Not displaying current content before proposing changes
- Applying changes before user approval
- Modifying file without atomic swap pattern
- Not recording edit in session frontmatter
- Not verifying final file matches proposal
- Releasing lock before step complete
- Proceeding to validation without user selecting [C]
- Generating content without user input

**Master Rule:** Simple agent editing is COLLABORATIVE and INTENT-BASED. Never make assumptions about what user wants changed. Always show proposals before applying. Always verify results. Skipping approval or verification is FORBIDDEN and constitutes SYSTEM FAILURE.
