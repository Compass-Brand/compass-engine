---
name: 'step-04b2-workflow-legacy'
description: 'Edit legacy single-file workflows or workflow.yaml formats with optional migration to modern standalone architecture'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04b2-workflow-legacy.md'
nextStepFile: '{workflow_path}/steps/step-05-validate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Migration References
migrationGuideWorkflow: '{project-root}/_bmad/bmb/workflows/create-workflow/workflow.md'

# Template References
legacyEditTemplate: '{workflow_path}/templates/legacy-workflow-edit.md'
migrationTemplate: '{workflow_path}/templates/workflow-migration-guide.md'
---

# Step 04b2: Legacy Workflow Editing

## STEP GOAL:

To edit legacy workflows (single-file .md, workflow.yaml, or inline step definitions) through simplified section-based editing while offering optional migration to modern standalone step-file architecture for workflows that would benefit from enhanced modularity and maintainability.

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
- ✅ You bring workflow modernization expertise and legacy format mastery
- ✅ User brings their workflow improvement intent and migration preferences
- ✅ Maintain strategic, holistic, collaborative tone throughout

### Step-Specific Rules:

- 🎯 Focus on legacy workflow formats (single-file, YAML, inline steps)
- 🚫 FORBIDDEN to auto-migrate without explicit user approval
- 💬 Offer migration option but respect user's choice to keep legacy format
- 📋 Validate YAML syntax for workflow.yaml files before writing
- 🔒 Use atomic swap pattern for file writes (write to .tmp, then rename)

## EXECUTION PROTOCOLS:

- 🎯 Detect specific legacy format and present appropriate editing approach
- 💾 Backup already created by step-04b-workflow-load.md
- 📖 Update session editsPerformed array with each modification
- 📖 Update frontmatter `stepsCompleted` to add '04b2' before loading next step
- 🚫 FORBIDDEN to modify file structure without user permission

## CONTEXT BOUNDARIES:

- Workflow details loaded from session state: `{workflowBeingEdited}`, `{workflowPath}`
- Workflow type confirmed as 'legacy' (no /steps/ directory or workflow.yaml format)
- Backup already exists at: `{workflowBackupPath}`
- Legacy formats include: single .md file, workflow.yaml, inline step definitions
- Migration is optional and requires user consent
- This step produces either modified legacy file OR migrated standalone workflow

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Workflow Information

Retrieve workflow metadata from session state:

- Workflow name: `{workflowBeingEdited}`
- Workflow path: `{workflowPath}`
- Backup location: `{workflowBackupPath}`
- Structure details: `{workflowStructure}`

Read the main workflow file (workflow.md, workflow.yaml, or single .md file).

### 2. Detect Legacy Format Specifics

Analyze the legacy workflow to determine exact format:

**Detection Patterns:**

```yaml
Format Detection:
  - workflow.yaml: YAML-based workflow definition
  - Single .md without /steps/: Markdown single-file workflow
  - Inline steps in workflow.md: Steps defined within main file
  - Other: Custom legacy format
```

Determine:
- File format: `.yaml` or `.md`
- Step definition method: YAML array, markdown sections, or inline
- Complexity: Simple (< 100 lines) or Complex (≥ 100 lines)
- Modularity potential: Would benefit from migration? (Complex + multiple logical sections)

### 3. Present Legacy Workflow Analysis

Display comprehensive analysis:

```
Legacy Workflow Editor
═══════════════════════════════════════════════════
Workflow: {workflowBeingEdited}
Type: Legacy Format
Backup: ✅ Created at {workflowBackupPath}

Format Analysis:
  File Type: {file_type}
  File Size: {line_count} lines
  Complexity: {simple|complex}
  Step Definition: {yaml_array|markdown_sections|inline|other}

Migration Assessment:
  Would Benefit from Migration: {yes|no}
  Reason: {assessment_reason}
```

### 4. Offer Migration Option

If workflow is complex (≥ 100 lines) or has clear step separation:

```
📋 Migration Opportunity Detected
═══════════════════════════════════════════════════

This workflow could benefit from migration to modern standalone
architecture, which provides:

✅ Modular step files for easier editing
✅ Better version control (cleaner diffs)
✅ Enhanced maintainability
✅ Advanced editing capabilities (add/remove/reorder steps)
✅ Compliance with latest BMAD standards

Would you like to:

[M] Migrate to standalone architecture first, then edit
[E] Edit in current legacy format
[C] Cancel and return to main menu

Select option (M/E/C):
```

If workflow is simple (< 100 lines):

```
Legacy Workflow - Simple Format
═══════════════════════════════════════════════════

This workflow is concise and well-suited for single-file format.
Migration to standalone architecture not recommended.

Proceeding with legacy format editing...
```

Skip to step 5 (Edit Legacy Format).

**Wait for user selection.** Do not proceed until user provides input.

### 5. Handle Migration Option Selection

#### [M] Migrate to Standalone Architecture

Display:
```
Workflow Migration Process
═══════════════════════════════════════════════════

Migration will:
1. Analyze current workflow structure
2. Extract logical sections as separate step files
3. Create /steps/ directory with step-NN-*.md files
4. Generate modern workflow.md with proper architecture
5. Preserve all existing content and functionality
6. Validate migrated workflow

This process will:
- Keep backup of original format at {workflowBackupPath}
- Create new standalone structure in same location
- Allow you to review before finalizing

Proceed with migration? (Y/N):
```

**If Y (Proceed with Migration):**

Execute migration sequence:

**5M.1 Analyze Workflow Sections:**

Parse legacy workflow to identify logical sections:
- For workflow.yaml: Extract steps array, metadata, config
- For single .md: Identify headers, step markers, logical breaks
- For inline steps: Detect step boundaries by markers or headers

**5M.2 Generate Step Files:**

For each identified section/step:
- Create step file: `step-{NN}-{section-name}.md`
- Populate with extracted content
- Add proper frontmatter (name, description, file references)
- Add standard step structure (goal, rules, sequence, menu, metrics)
- Preserve original content in sequence section

**5M.3 Create Modern workflow.md:**

Generate new workflow.md with:
- Proper frontmatter
- Workflow goal and role
- Architecture section describing flow
- References to all step files

**5M.4 Create /steps/ Directory:**

- Create `/steps/` subdirectory in workflow path
- Move all generated step files into /steps/
- Organize alphabetically

**5M.5 Validate Migration:**

- Verify all content preserved
- Check step file references are correct
- Confirm workflow.md properly structured
- Test readability of all generated files

**5M.6 Display Migration Results:**

```
✅ Migration Complete
═══════════════════════════════════════════════════

Created:
  workflow.md (new modern structure)
  /steps/ directory with {step_count} step files:
    {step_file_list}

Original Format: Preserved in backup at {workflowBackupPath}

The workflow is now using standalone architecture.
Routing to standalone workflow editor for your edits...
```

**5M.7 Route to Standalone Editor:**

Update session state:
```yaml
workflowType: 'standalone'  # Changed from 'legacy'
migrationPerformed: true
originalFormat: '{original_format}'
```

Update frontmatter `stepsCompleted` to include '04b2-migration', then load and execute step-04b1-workflow-standalone.md.

**If N (Cancel Migration):**

Display: "Keeping legacy format. Proceeding to legacy editor..."

Proceed to step 5E (Edit Legacy Format).

#### [E] Edit in Current Legacy Format

Proceed directly to step 6 (Edit Legacy Format).

#### [C] Cancel and Return

Display: "Returning to main component selection menu..."

Update frontmatter `stepsCompleted` to include '04b2', then route to step-03-select.md.

### 6. Edit Legacy Format

Execute simple section-based editing for legacy workflows:

**6.1 Display File Content:**

Show the entire workflow file with line numbers:

```
{workflow_file_name} - Current Content
═══════════════════════════════════════════════════
{file_content_with_line_numbers}
═══════════════════════════════════════════════════
Total Lines: {line_count}
```

**6.2 Present Edit Options:**

```
Legacy Workflow Edit Options
═══════════════════════════════════════════════════

[S] Section-based edit (recommended)
    Identify sections, edit specific parts

[F] Full file edit
    Replace or modify entire file content

[L] Line-based edit
    Edit specific line ranges

[V] View file again

[X] Finish editing

Select option (S/F/L/V/X):
```

**Wait for user selection.**

#### [S] Section-Based Edit

**6S.1 Identify Sections:**

For workflow.yaml:
- List YAML top-level keys as sections

For .md files:
- List headers (# ## ###) as sections
- Show section titles and line ranges

Display:
```
Identified Sections
═══════════════════════════════════════════════════

{section_list_with_line_ranges}

Example:
[1] Metadata (lines 1-10)
[2] Workflow Goal (lines 11-25)
[3] Step Definitions (lines 26-80)
...

Select section to edit (1-{section_count}, X to cancel):
```

**6S.2 Edit Selected Section:**

- Display section content with line numbers
- Ask: "What changes would you like to make to this section?"
- Collect user's edit intent
- Show proposed changes as diff
- Ask for confirmation: "Apply these changes? (Y/N)"
- If Y: Apply changes using atomic swap
- If N: Allow refinement or cancel

**6S.3 Record Edit:**

Update session state editsPerformed:
```yaml
editsPerformed:
  - type: 'workflow-legacy-section'
    file: '{workflow_file_name}'
    section: '{section_name}'
    lineRange: '{start_line}-{end_line}'
    timestamp: '{timestamp}'
    description: '{brief_description}'
```

**6S.4 Continue or Return:**

Ask: "Edit another section? (Y/N)"
- If Y: Return to section selection (6S.1)
- If N: Return to edit options menu (6.2)

#### [F] Full File Edit

Display:
```
⚠️  Full File Edit - Use with Caution
═══════════════════════════════════════════════════

This will replace the entire file content.
Current file has {line_count} lines.

Recommended approach: Use section-based editing instead.

Proceed with full file edit? (Y/N):
```

If Y:
- Display current content
- Prompt user to provide replacement content
- Show diff of entire file change
- Confirm before applying
- Record edit in editsPerformed

If N: Return to edit options menu (6.2)

#### [L] Line-Based Edit

Prompt user:
```
Line-Based Edit
═══════════════════════════════════════════════════

Enter line range to edit (e.g., "15-20" or "42"):
```

- Display specified line range
- Ask: "What changes would you like to make to these lines?"
- Show proposed changes as diff
- Confirm and apply
- Record edit in editsPerformed

Return to edit options menu (6.2)

#### [V] View File Again

Re-display file content with line numbers (step 6.1), then return to edit options menu (6.2).

#### [X] Finish Editing

Proceed to step 7 (Present Menu Options).

### 7. Present MENU OPTIONS

After user selects [X] to finish editing:

Display:
```
Legacy Workflow Editing Complete
═══════════════════════════════════════════════════

Edits performed: {edit_count}
File modified: {workflow_file_name}

**Select an Option:**
[A] Advanced Elicitation
[P] Party Mode
[C] Continue to Validation
```

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}, then redisplay this menu
- IF P: Execute {partyModeWorkflow}, then redisplay this menu
- IF C: Update frontmatter `stepsCompleted` to include '04b2', save session state to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#7-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then redisplay the menu

## CRITICAL STEP COMPLETION NOTE

This step completes when:
1. ✅ Legacy workflow format analyzed and presented to user
2. ✅ Migration option offered (if applicable) and user chose edit path
3. ✅ All requested edits completed (either via migration→standalone OR direct legacy editing)
4. ✅ All changes written to files using atomic swap pattern
5. ✅ Session state updated with all edits in editsPerformed array
6. ✅ User selects [C] Continue from the final menu
7. ✅ frontmatter `stepsCompleted` includes '04b2'

ONLY WHEN [C continue option] is selected and all edits are recorded, will you then load and read fully `{nextStepFile}` (step-05-validate.md) to execute workflow validation.

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Legacy workflow format correctly detected and analyzed
- Migration opportunity properly assessed and communicated
- User's choice (migrate or edit legacy) respected
- If migrated: All content preserved in new standalone structure
- If legacy edited: Changes applied with proper diff preview
- All file writes use atomic swap pattern (.tmp then rename)
- Session state editsPerformed array updated for each modification
- YAML syntax validated before writing (for .yaml files)
- Menu presented and user input handled correctly
- frontmatter `stepsCompleted` includes '04b2' before proceeding
- Content properly saved before advancing to validation

### ❌ SYSTEM FAILURE:

- Auto-migrating without user consent
- Losing content during migration process
- Not offering migration when workflow is complex
- Forcing migration when user chooses legacy editing
- Modifying files without showing changes to user first
- Not using atomic swap pattern for file writes
- Writing invalid YAML to workflow.yaml files
- Not updating editsPerformed array after modifications
- Proceeding to validation without user selecting 'C'
- Not displaying menu after Advanced Elicitation or Party Mode
- Skipping migration validation steps
- Not routing to standalone editor after successful migration

**Master Rule:** Legacy workflows deserve respect. Offer modernization but honor user's choice. Migration must be complete and validated before routing to standalone editor. All changes must be previewed and confirmed before application. Never force architectural changes without explicit user approval.
