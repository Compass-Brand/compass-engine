---
name: 'step-04c-config'
description: 'Edit module.yaml configuration through guided field-specific editing with validation and backup protection'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04c-config.md'
nextStepFile: '{workflow_path}/steps/step-05-validate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Template References
configEditTemplate: '{workflow_path}/templates/config-edit-section.md'
---

# Step 04c: Module Configuration Editing

## STEP GOAL:

To safely edit module.yaml configuration through guided field-specific editing that understands the destructive implications of certain changes, validates YAML syntax, and maintains backup protection to ensure module coherence and recoverability.

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
- ✅ You bring architectural expertise and structured planning
- ✅ User brings their module intent and domain knowledge
- ✅ Maintain strategic, holistic, collaborative tone throughout

### Step-Specific Rules:

- 🎯 Focus ONLY on module.yaml configuration editing
- 🚫 FORBIDDEN to modify without creating backup first
- 💬 Warn explicitly about destructive operations (name changes, path variables)
- 📋 ALWAYS validate YAML syntax before writing changes
- 🔒 Use atomic swap pattern (write to .tmp, then rename)

## EXECUTION PROTOCOLS:

- 🎯 Parse module.yaml and display editable fields in numbered menu
- 💾 Create backup before ANY modification
- 📖 Update session editsPerformed array with config changes
- 📖 Update frontmatter `stepsCompleted` to add '04c' before loading next step
- 🚫 FORBIDDEN to proceed to validation until changes are written and verified

## CONTEXT BOUNDARIES:

- Module path and session state loaded from frontmatter
- Focus ONLY on configuration editing, not agent/workflow content
- Changes affect module metadata and registry entries
- Path variable changes have cascading impact across module
- This step produces modified module.yaml with backup reference

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Parse Current Configuration

Read and parse `{module_path}/module.yaml`:

- Extract all fields: name, version, description, agents[], workflows[], custom settings
- Validate current YAML is well-formed
- Display parsing errors if found, suggest manual fix

### 2. Display Editable Fields Menu

Present structured menu:

```
Module Configuration: {module_name}
═══════════════════════════════════════════════════

[1] name: {current_name}
[2] version: {current_version}
[3] description: {current_description}
[4] Agents Registry ({agent_count} entries)
[5] Workflows Registry ({workflow_count} entries)
[6] Custom Settings
[X] Cancel (return to main menu)

Which field to edit? (1-6, X):
```

### 3. Field-Specific Edit Handling

Based on user selection, apply appropriate editing workflow:

#### [1] Name Change (⚠️ DESTRUCTIVE - Medium Severity)

**Warning Display:**
```
⚠️  WARNING: DESTRUCTIVE OPERATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Changing module name has implications:
  • Module folder should be renamed to match
  • References in parent configs must update
  • Skill registrations may break
  • Import paths in other modules affected

Current name: {current_name}
Proposed name: {user_input}

Are you certain? Type 'CONFIRM' to proceed, anything else cancels:
```

If confirmed:
- Update `name` field
- Add note to changelog about required folder rename
- Flag for validation check

#### [2] Version Change (✅ Safe)

**Guidance Display:**
```
Current version: {current_version}

Semantic versioning format: MAJOR.MINOR.PATCH
  • MAJOR: Incompatible API changes
  • MINOR: Backward-compatible functionality
  • PATCH: Backward-compatible bug fixes

New version:
```

- Accept user input
- Validate semver format (regex: `^\d+\.\d+\.\d+$`)
- Update field

#### [3] Description Change (✅ Safe)

**Simple Edit:**
```
Current description:
"{current_description}"

New description (or ENTER to keep current):
```

- Accept multi-line input
- Update field

#### [4] Agents Registry Edit

**Display Current Agents:**
```
Agents Registry ({agent_count} entries)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{list all agent entries with indices}

[A] Add new agent entry
[R] Remove agent entry
[M] Modify agent entry
[B] Back to main menu

Select action:
```

Handle add/remove/modify operations with validation that agent files exist.

#### [5] Workflows Registry Edit

**Display Current Workflows:**
```
Workflows Registry ({workflow_count} entries)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{list all workflow entries with indices}

[A] Add new workflow entry
[R] Remove workflow entry
[M] Modify workflow entry
[B] Back to main menu

Select action:
```

Handle add/remove/modify operations with validation that workflow directories exist.

#### [6] Custom Settings (⚠️ Advanced)

**Freeform YAML Edit:**
```
⚠️  ADVANCED: Direct YAML Editing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Custom settings allow module-specific configuration.
This is freeform YAML editing - syntax errors will break the module.

Current custom settings:
{display current custom section or "None"}

Options:
[E] Edit custom settings
[D] Delete custom settings section
[B] Back to main menu

Select action:
```

If editing, allow freeform YAML input with validation before accepting.

### 4. Path Variable Change Guard

If any field contains `{project-root}`, `{module_path}`, or other path variables:

```
⚠️  Path Variable Detected
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This field contains path variables that affect multiple files:
"{field_value}"

Changing this will impact:
{list affected components}

Proceed with edit? (y/N):
```

### 5. Backup and Atomic Write

Before writing ANY changes:

**Backup Process:**
```
Creating backup: module.yaml.backup-{timestamp}
Validating YAML syntax...
Writing changes to module.yaml.tmp...
Verifying written content...
Atomic swap: module.yaml.tmp → module.yaml
✓ Configuration updated successfully
```

**Backup Failure Handling:**
If backup creation fails:
```
❌ ERROR: Cannot create backup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reason: {error_message}

Changes NOT applied. Module.yaml remains unchanged.
```

### 6. YAML Syntax Validation

After user provides new values but BEFORE writing:

```
Validating YAML syntax...
```

If validation fails:
```
❌ YAML Syntax Error
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Line {line_number}: {error_message}

{show problematic YAML section}

Options:
[E] Edit again
[C] Cancel changes
```

If validation succeeds:
```
✓ YAML syntax valid
```

### 7. Update Session Document

Append to {outputFile} in Edit Log section:

```markdown
### Edit #{n}: Configuration - module.yaml

**Action:** modify
**Timestamp:** {timestamp}
**Fields Modified:** {list of fields}
**Reason:** {user_stated_reason}

#### Changes Made

{field_name}: "{old_value}" → "{new_value}"

**Backup:** module.yaml.backup-{timestamp}
**Validation:** YAML syntax valid ✓
```

Update frontmatter:
```yaml
editsPerformed:
  - type: config
    target: module.yaml
    fields: [{field_list}]
    backup: module.yaml.backup-{timestamp}
    timestamp: {timestamp}
```

### 8. Present MENU OPTIONS

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then end with display again of the menu options
- Use menu handling logic section below

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
- IF P: Execute {partyModeWorkflow}
- IF C: Update frontmatter stepsCompleted with '04c', then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#8-present-menu-options)

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN C is selected, changes are written to module.yaml, backup is created, session document is updated, and frontmatter is updated with '04c' completion, will you then load, read entire file, then execute `{workflow_path}/steps/step-05-validate.md` to execute validation of all changes.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- module.yaml parsed successfully
- User guided through field-specific editing
- Destructive operations flagged with warnings
- Backup created before modification
- YAML syntax validated before writing
- Atomic swap pattern used for write operation
- Session document updated with edit details
- Frontmatter updated with step completion
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Modifying module.yaml without backup
- Accepting invalid YAML syntax
- Not warning about destructive operations
- Writing partial changes (not atomic)
- Proceeding to validation without completing writes
- Not updating session editsPerformed array
- Generating field values without user input

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
