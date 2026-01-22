---
name: 'step-04a-agent-remove'
description: 'Remove an agent from the module (DESTRUCTIVE - requires explicit confirmation)'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04a-agent-remove.md'
nextStepFile: '{workflow_path}/steps/step-05-validate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Data References
destructiveOpsTable: '{workflow_path}/data/destructive-operations.md'
---

# Step 04a-remove: Remove Agent from Module (DESTRUCTIVE)

## STEP GOAL:

To safely remove an agent from the module by performing dependency checks, creating comprehensive backups, and executing deletion only after explicit user confirmation, preventing accidental data loss and broken references.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 THIS IS A DESTRUCTIVE OPERATION - Maximum caution required
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist responsible for safe operations
- ✅ If you already have been given a name, communication_style and identity, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring safety protocols and technical expertise, user brings removal authorization
- ✅ Maintain strategic, holistic, systems-thinking communication style with emphasis on risk awareness

### Step-Specific Rules:

- 🎯 Focus on safe removal with comprehensive backup
- 🚫 FORBIDDEN to delete anything without explicit "CONFIRM DELETE {agent-name}" confirmation
- 💬 Approach: Dependency analysis first, impact display, require confirmation, then execute
- 📋 Always create full module backup before deletion
- 📋 NEVER proceed with partial removal - all-or-nothing approach

## EXECUTION PROTOCOLS:

- 🎯 Perform dependency scan BEFORE requesting confirmation
- 💾 Create full module backup before ANY deletion
- 📖 Display impact analysis and require typed confirmation
- 🚫 FORBIDDEN to delete without backup OR without explicit confirmation

## CONTEXT BOUNDARIES:

- Available context: Agent to be removed (from step 03 selection or user specification)
- Focus: Safe removal with dependency awareness
- Limits: Cannot undo after deletion (only restore from backup)
- Dependencies: Requires valid agent file and module.yaml entry

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Removal Context

Read from {outputFile} frontmatter:
- `currentTarget`: Path to the agent file being removed (if selected from step 03)
- `modulePath`: Path to the module directory
- `module_name`: Name of the module
- `moduleYamlPath`: Path to module.yaml file

**IF currentTarget not set:**

Prompt:
```
Enter the name of the agent to remove (from {module_name} module):
```

Wait for user input. Store as `{agent_name}`.

Resolve agent file path:
- Search `{modulePath}/agents/` for `{agent_name}.md`
- Store resolved path as `{agent_file_path}`

**IF currentTarget is set:**
- Extract agent name from file path
- Store as `{agent_name}` and `{agent_file_path}`

Display:
```
🚨 DESTRUCTIVE OPERATION: AGENT REMOVAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Operation: Remove Agent
Module: {module_name}
Agent: {agent_name}
Severity: HIGH

This operation is IRREVERSIBLE without backup restoration.
Proceeding with safety checks...
```

### 2. Pre-Removal Safety Checks

**2.1** Verify agent file exists:
```
Checking agent file: {agent_file_path}
```

**IF file not found:**
```
❌ ERROR: Agent file not found at {agent_file_path}

The agent may have already been deleted or the path is incorrect.

Options:
[S] Search for agent file
[C] Cancel removal

Enter choice:
```

- IF S: Prompt for different name, go to Step 1
- IF C: Abort removal, return to workflow

**IF file found:**
```
✅ Agent file located
```

**2.2** Verify agent is registered in module.yaml:

Read and parse `{moduleYamlPath}`:
- Search agents array for entry matching `{agent_name}`
- Store registration status as `{is_registered}`

**IF not registered:**
```
⚠️ WARNING: Agent file exists but is NOT registered in module.yaml

This is an orphaned agent file.

Options:
[D] Delete orphaned file
[C] Cancel removal

Enter choice:
```

- IF D: Skip registration removal (Step 5), proceed to dependency check
- IF C: Abort removal

### 3. Dependency Scan

**3.1** Display scan start:
```
DEPENDENCY SCAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scanning module for references to '{agent_name}'...
```

**3.2** Search workflow files for agent references:

Search in `{modulePath}/workflows/`:
- Pattern: `{agent_name}` (case-insensitive)
- File types: `*.md`, `*.yaml`, `*.xml`
- Record: file path, line number, context snippet

Store results as `{workflow_references}` array.

**3.3** Search step files for agent references:

Search in `{modulePath}/workflows/*/steps/`:
- Pattern: `{agent_name}` (case-insensitive)
- File types: `*.md`
- Record: file path, line number, context snippet

Store results as `{step_references}` array.

**3.4** Search documentation for agent references:

Search in `{modulePath}/docs/`:
- Pattern: `{agent_name}` (case-insensitive)
- File types: `*.md`
- Record: file path, line number, context snippet

Store results as `{doc_references}` array.

**3.5** Search other agents for references:

Search in `{modulePath}/agents/`:
- Exclude `{agent_name}.md` itself
- Pattern: `{agent_name}` (case-insensitive)
- File types: `*.md`
- Record: file path, line number, context snippet

Store results as `{agent_references}` array.

**3.6** Calculate total references:
```
{total_references} = {workflow_references.length} + {step_references.length} + {doc_references.length} + {agent_references.length}
```

### 4. Display Impact Analysis

**4.1** Display dependency scan results:

**IF total_references = 0:**
```
DEPENDENCY SCAN RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ No dependencies found

The agent '{agent_name}' is not referenced by other components.
Removal is safe from a dependency perspective.
```

**IF total_references > 0:**
```
DEPENDENCY SCAN RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  DEPENDENCIES DETECTED: {total_references} reference(s) found

Removing this agent will affect the following components:
```

**Display workflow references (if any):**
```
WORKFLOW REFERENCES ({workflow_references.length}):
{for each reference in workflow_references}
  📄 {file_path}
     Line {line_number}: {context_snippet}
{end for}
```

**Display step references (if any):**
```
STEP FILE REFERENCES ({step_references.length}):
{for each reference in step_references}
  📄 {file_path}
     Line {line_number}: {context_snippet}
{end for}
```

**Display documentation references (if any):**
```
DOCUMENTATION REFERENCES ({doc_references.length}):
{for each reference in doc_references}
  📄 {file_path}
     Line {line_number}: {context_snippet}
{end for}
```

**Display agent references (if any):**
```
OTHER AGENT REFERENCES ({agent_references.length}):
{for each reference in agent_references}
  📄 {file_path}
     Line {line_number}: {context_snippet}
{end for}
```

**Display warning:**
```
⚠️  IMPACT WARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Removing this agent may break workflows, steps, or other
components that depend on it.

Recommended actions:
1. Update dependent components to remove references
2. Or keep this agent in place

Proceed with removal? [Y] Yes, remove anyway [U] Update references [C] Cancel
```

Wait for user selection.

**IF U (Update references):**
```
Display: "Reference updating is not automated in this workflow.
You should:
1. Cancel this removal [C]
2. Manually update the {total_references} reference(s) listed above
3. Return to this workflow to remove the agent

Proceed? [C] Cancel removal
```

Return to workflow after user acknowledges.

**IF C (Cancel):**
Abort removal, return to workflow.

**IF Y (Yes):**
Proceed to Step 4.2

**4.2** Display removal summary:
```
REMOVAL SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Module: {module_name}
Agent: {agent_name}
Agent File: {agent_file_path}
Registered in module.yaml: {is_registered ? "Yes" : "No"}
Dependencies: {total_references} reference(s)

Files to be deleted:
1. {agent_file_path}

Configuration to be modified:
1. {moduleYamlPath} (remove agent entry)

Backups will be created before deletion.
```

### 5. Require Explicit Confirmation

**5.1** Display confirmation requirement:
```
🚨 EXPLICIT CONFIRMATION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is a DESTRUCTIVE OPERATION (Severity: HIGH)

To proceed with deletion, type exactly:

CONFIRM DELETE {agent_name}

Or type 'CANCEL' to abort.

Enter confirmation:
```

**5.2** Wait for user input. Store as `{confirmation_input}`.

**5.3** Validate confirmation:

Expected: `CONFIRM DELETE {agent_name}` (case-sensitive)

**IF confirmation_input = "CANCEL":**
```
Display: "Removal cancelled. No changes made."
```
Return to workflow.

**IF confirmation_input ≠ expected confirmation:**
```
Display: "❌ Confirmation did not match. Expected: 'CONFIRM DELETE {agent_name}'

Entered: '{confirmation_input}'

Try again? [Y] Yes [N] No, cancel removal"
```

- IF Y: Return to Step 5.1
- IF N: Abort removal, return to workflow

**IF confirmation_input = expected confirmation:**
```
Display: "✅ Confirmation accepted. Proceeding with removal..."
```

Proceed to Step 6.

### 6. Create Full Module Backup

**6.1** Display backup initiation:
```
CREATING FULL MODULE BACKUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This backup allows complete restoration if needed.
```

**6.2** Execute full module backup:

Backup location: `{modulePath}/.backup/{timestamp}-agent-remove-{agent_name}/`

Create backup of:
1. Agent file: `{agent_file_path}` → backup location
2. module.yaml: `{moduleYamlPath}` → backup location
3. All workflow files (if dependencies exist) → backup location

Execute backup:
```
for each file in backup_list:
  - Copy file to {backup_location}/{relative_path}
  - Verify copy successful
```

**6.3** Create backup manifest:

Create file: `{backup_location}/MANIFEST.json`

Content:
```json
{
  "operation": "agent_removal",
  "timestamp": "{timestamp}",
  "module": "{module_name}",
  "agent_removed": "{agent_name}",
  "files_backed_up": [
    "{agent_file_path}",
    "{moduleYamlPath}",
    ...
  ],
  "dependencies_found": {total_references},
  "can_restore": true,
  "restore_instructions": "To restore: copy all files from this backup back to their original locations"
}
```

**6.4** Verify backup:
```
Verifying backup...
✅ Agent file backed up
✅ module.yaml backed up
{if dependencies exist}
✅ {workflow_references.length} workflow files backed up
✅ {step_references.length} step files backed up
{end if}
✅ Backup manifest created

Backup location: {backup_location}
```

### 7. Execute Removal

**7.1** Remove agent from module.yaml:

**IF is_registered = true:**

- Read `{moduleYamlPath}`
- Parse YAML
- Find agent entry with name `{agent_name}`
- Remove entry from agents array
- Write updated YAML

**Validate modified YAML:**
- Attempt to parse updated YAML
- Check for syntax errors

**IF validation fails:**
```
❌ ERROR: YAML became invalid after removal

Restoring from backup...
```
- Copy `{backup_location}/module.yaml` back to `{moduleYamlPath}`
- Abort operation
- Display error and restoration message
- Return to workflow

**IF validation passes:**
```
✅ Agent removed from module.yaml
```

**7.2** Delete agent file:

Execute deletion:
```
Delete file: {agent_file_path}
```

Verify deletion:
- Check file no longer exists at `{agent_file_path}`

**IF deletion failed:**
```
❌ ERROR: Failed to delete agent file

Partial removal detected. Restoring from backup...
```
- Restore module.yaml from backup
- Abort operation
- Return to workflow

**IF deletion successful:**
```
✅ Agent file deleted
```

**7.3** Display removal complete:
```
REMOVAL COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agent '{agent_name}' has been removed from module '{module_name}'.

Files deleted:
✅ {agent_file_path}

Configuration updated:
✅ {moduleYamlPath} (agent entry removed)

Backup location:
📦 {backup_location}

{if total_references > 0}
⚠️  WARNING: {total_references} reference(s) to this agent still exist.
You should update the following files:
{list affected files}
{end if}
```

### 8. Update Session Tracking

**8.1** Append to {outputFile} frontmatter `editsPerformed` array:
```yaml
editsPerformed:
  - operation: "agent_remove"
    agent_name: "{agent_name}"
    agent_file_deleted: "{agent_file_path}"
    config_modified: "{moduleYamlPath}"
    dependencies_found: {total_references}
    timestamp: "{timestamp}"
    backups:
      - "{backup_location}"
    restoration_possible: true
```

**8.2** IF total_references > 0:

Append to {outputFile} content body:
```markdown
## ⚠️ Post-Removal Action Required

Agent '{agent_name}' was removed, but {total_references} reference(s) to it remain:

{list all references with file paths and line numbers}

These references should be updated or removed to prevent errors.
```

### 9. Present MENU OPTIONS

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
- IF P: Execute {partyModeWorkflow}
- IF C: Update frontmatter to add step 4a-remove to `stepsCompleted`, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#9-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then redisplay the menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and agent has been successfully removed with backup created, will you then load and read fully `{nextStepFile}` to execute and begin validation.

Before loading next step, ensure:
1. ✅ Dependency scan completed and results displayed
2. ✅ Explicit "CONFIRM DELETE {agent_name}" confirmation received
3. ✅ Full module backup created in `{backup_location}`
4. ✅ Agent removed from module.yaml (if registered)
5. ✅ Agent file deleted from `{agent_file_path}`
6. ✅ Backup manifest created for restoration
7. ✅ Session frontmatter updated with removal record
8. ✅ Step 4a-remove added to `stepsCompleted` array

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Agent file and registration verified to exist
- Comprehensive dependency scan performed
- Impact analysis displayed with all references
- Explicit typed confirmation received: "CONFIRM DELETE {agent_name}"
- Full module backup created before deletion
- Agent removed from module.yaml successfully
- Agent file deleted successfully
- Backup manifest created for restoration
- Session tracking updated with removal record
- User warned about remaining references (if any)
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Deleting agent without explicit typed confirmation
- Proceeding without dependency scan
- Not creating backup before deletion
- Partial removal (file deleted but not unregistered, or vice versa)
- Corrupting module.yaml during removal
- Not displaying impact analysis to user
- Accepting generic "yes" instead of "CONFIRM DELETE {agent_name}"
- Not updating session editsPerformed array
- Proceeding to next step without user selecting 'C'
- Failing to create backup manifest
- Not warning about remaining dependencies

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE. Destructive operations require maximum adherence to protocol.
