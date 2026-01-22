---
name: 'step-04a2-agent-expert'
description: 'Edit expert agent files with YAML frontmatter and structured sections through scoped section-level editing'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04a2-agent-expert.md'
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
sidecarPath: '{agent_path}-sidecar'
---

# Step 4a2: Edit Expert Agent

## STEP GOAL:

Edit an expert agent file (YAML frontmatter + structured sections, possibly with sidecar folder) through scoped section-level editing, allowing users to modify specific aspects (Persona, Capabilities, Tools, Communication Style, Frontmatter, or Custom Sections) while preserving structure, formatting, and maintaining sidecar coherence.

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
- ✅ Together we produce precise, effective, well-structured agent definitions
- ✅ Maintain strategic, holistic, systems-thinking communication style

### Step-Specific Rules:

- 🎯 Focus ONLY on expert agent editing workflow
- 🚫 FORBIDDEN to skip scope selection or user approval
- 💬 Use section-based editing: user selects scope, then collaborates on changes
- 📝 Always show proposed changes with diff-like comparison
- ✅ Preserve YAML formatting and section structure
- 🔒 CRITICAL: Update session editsPerformed array after successful edit
- 📂 If sidecar exists, maintain coherence between agent file and sidecar

## EXECUTION PROTOCOLS:

- 🎯 Section-scoped editing: user picks what to change from menu
- 💾 Apply changes only after user approval with diff preview
- 📖 Display current section content before proposing changes
- 🚫 Never modify unrelated sections or frontmatter without explicit selection
- ✅ Preserve YAML structure, indentation, and section markers
- 🔄 Iterate on proposed changes until user satisfied
- 📂 Track sidecar references and warn if changes affect sidecar coherence

## CONTEXT BOUNDARIES:

- Available context: Expert agent file loaded, backed up, and locked from step-04a-agent-load
- Focus: Section-level content editing through collaborative structured interaction
- Limits: This step is for expert agents only (YAML frontmatter + structured sections)
- Dependencies: Requires successful completion of step-04a-agent-load with backup and type detection

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Parse Expert Agent Structure

Read the agent file from `{currentTarget}` (available from session frontmatter).

**Parse YAML Frontmatter:**
- Extract frontmatter between opening `---` and closing `---`
- Parse as YAML
- Identify fields: name, description, version, metadata, etc.
- Record frontmatter structure

**Parse Markdown Sections:**
- Identify all H2 sections (`## Section Name`)
- Common sections: Persona, Capabilities, Tools, Communication Style, Examples, etc.
- Extract content for each section
- Build section map: `{section_name: {start_line, end_line, content}}`

**Check for Sidecar:**
- Verify if `{sidecarPath}` exists (from agentAnalysis in session)
- If exists, scan sidecar contents:
  - `memories.md` - agent-specific memory/context
  - `instructions.md` - detailed operational instructions
  - `workflows/` - agent-specific workflows
  - `knowledge/` - knowledge base files
- Build sidecar inventory

**Structure Analysis:**
```
Expert Agent: {agent_name}
─────────────────────────────────────────
File Size: {file_size}
Total Lines: {line_count}

YAML Frontmatter: ✓ Present
├─ name: {name}
├─ description: {description}
└─ {other_frontmatter_fields}

Markdown Sections ({section_count} detected):
{section_list}

Sidecar: {✓ Present | ✗ Not Found}
{sidecar_inventory}

Ready for scoped editing.
─────────────────────────────────────────
```

### 2. Present Edit Scope Selection Menu

Display a structured menu for the user to select what they want to edit:

```
Edit Scope Selection
─────────────────────────────────────────
What aspect of this expert agent would you like to change?

[1] Persona/Role Definition
    Current: {persona_first_line}...

[2] Capabilities/Skills
    Current: {capability_count} capabilities defined

[3] Tools/Permissions
    Current: {tool_list or "None specified"}

[4] Communication Style
    Current: {style_summary or "Not defined"}

[5] Frontmatter/Metadata
    Current: {frontmatter_field_count} fields

[6] Custom Section
    Specify section name to edit

[7] Full Rewrite
    Replace entire agent file (preserves sidecar)

[8] Sidecar Management {only if sidecar exists}
    Edit sidecar contents

[C] Cancel - Return to selection menu
─────────────────────────────────────────

Enter your choice (1-8 or C):
```

**Wait for user selection.** Do NOT proceed without user input.

### 3. Execute Section-Specific Edit Flow

Based on user selection, execute the appropriate editing flow:

---

#### [1] Persona/Role Definition Edit

**Display Current Persona:**
```
Current Persona Section
─────────────────────────────────────────
## {persona_section_heading}

{current_persona_content}
─────────────────────────────────────────
```

**Gather Edit Intent:**
"Describe the change you want to make to this agent's persona or role definition.

Examples:
- 'Make the tone more formal and authoritative'
- 'Add expertise in security analysis'
- 'Simplify the role description'
- 'Expand the background context'"

**Wait for user response.**

**Propose Changes:**
Display proposed persona section with comparison:
```
Proposed Persona Changes
─────────────────────────────────────────
## {persona_section_heading}

{proposed_new_persona_content}
─────────────────────────────────────────

Summary of Changes:
{change_summary}
- {specific_change_1}
- {specific_change_2}
- ...

Approve these changes? [Y/N/E/R]
  Y = Yes, apply changes
  N = No, revise proposal
  E = Explain changes in detail
  R = Restart - select different scope
```

**Handle approval flow** (same as Simple Agent: Y/N/E, plus R to restart scope selection).

---

#### [2] Capabilities/Skills Edit

**Display Current Capabilities:**
```
Current Capabilities Section
─────────────────────────────────────────
## {capabilities_section_heading}

{current_capabilities_content}
─────────────────────────────────────────
```

**Gather Edit Intent:**
"What would you like to change about this agent's capabilities?

Options:
- Add new capabilities
- Remove existing capabilities
- Modify/clarify existing capabilities
- Reorder by priority
- Complete rewrite of capabilities section

Please describe your desired changes:"

**Wait for user response.**

**Propose Changes:**
Display proposed capabilities with before/after comparison:
```
Proposed Capabilities Changes
─────────────────────────────────────────
Current Capabilities ({current_count}):
{current_capability_list}

Proposed Capabilities ({new_count}):
{proposed_capability_list}

Changes:
  [+] Added: {new_capabilities}
  [-] Removed: {removed_capabilities}
  [~] Modified: {modified_capabilities}

Approve these changes? [Y/N/E/R]
```

**Handle approval flow.**

---

#### [3] Tools/Permissions Edit

**Display Current Tools:**
```
Current Tools Section
─────────────────────────────────────────
## {tools_section_heading}

{current_tools_content}
─────────────────────────────────────────
```

**Gather Edit Intent:**
"What changes do you want to make to this agent's tools or permissions?

Examples:
- Grant new tool access
- Remove tool permissions
- Update tool usage guidelines
- Add constraints or limitations"

**Wait for user response.**

**Propose Changes** with comparison and **handle approval flow.**

---

#### [4] Communication Style Edit

**Display Current Style:**
```
Current Communication Style
─────────────────────────────────────────
## {communication_section_heading}

{current_style_content}
─────────────────────────────────────────
```

**Gather Edit Intent:**
"How should this agent communicate differently?

Consider:
- Formality level (casual ↔ formal)
- Technical depth (beginner-friendly ↔ expert-level)
- Tone (friendly, professional, authoritative, etc.)
- Response structure (concise, detailed, etc.)
- Special behaviors (emoji usage, formatting preferences, etc.)"

**Wait for user response.**

**Propose Changes** with comparison and **handle approval flow.**

---

#### [5] Frontmatter/Metadata Edit

**Display Current Frontmatter:**
```
Current YAML Frontmatter
─────────────────────────────────────────
{current_frontmatter_yaml}
─────────────────────────────────────────

Fields: {field_count}
```

**Gather Edit Intent:**
"Which frontmatter field would you like to modify?

Available fields:
{list_of_frontmatter_fields_with_current_values}

Or specify:
- 'add {field_name}' to add new field
- 'remove {field_name}' to delete field
- '{field_name} = {new_value}' to update value

What would you like to change?"

**Wait for user response.**

**Propose Changes:**
```
Proposed Frontmatter Changes
─────────────────────────────────────────
Current:
{current_frontmatter}

Proposed:
{proposed_frontmatter}

Changed Fields:
  [+] Added: {added_fields}
  [-] Removed: {removed_fields}
  [~] Modified: {modified_fields}

⚠️  WARNING: Frontmatter changes may affect agent loading or module registration.
Verify that changes are compatible with BMAD agent specifications.

Approve these changes? [Y/N/E/R]
```

**Handle approval flow.**

---

#### [6] Custom Section Edit

**Ask for Section Name:**
"Which section would you like to edit?

Detected sections:
{list_all_h2_sections_by_number}

Enter section number or name:"

**Wait for user selection.**

**Display Selected Section:**
```
Current: {selected_section_name}
─────────────────────────────────────────
{current_section_content}
─────────────────────────────────────────
```

**Gather Edit Intent:**
"What would you like to change about the {section_name} section?"

**Propose Changes** with comparison and **handle approval flow.**

---

#### [7] Full Rewrite

**Display Warning:**
```
⚠️  FULL REWRITE WARNING
─────────────────────────────────────────
This will replace the ENTIRE agent file while preserving:
  ✓ YAML frontmatter structure
  ✓ Required sections (Persona, Capabilities, etc.)
  ✓ Sidecar folder (if exists)

This is a significant operation. Are you sure?

Type 'REWRITE' to confirm, or 'cancel' to return:
```

**Wait for confirmation.** Only proceed if user types 'REWRITE'.

**Guide Full Rewrite:**
"I'll guide you through rebuilding this expert agent step by step.

Step 1/5: Persona
{Ask questions to define new persona}

Step 2/5: Capabilities
{Gather new capabilities}

Step 3/5: Tools & Permissions
{Define tool access}

Step 4/5: Communication Style
{Establish communication patterns}

Step 5/5: Additional Sections
{Any custom sections needed}

Then I'll reconstruct the full agent file for your approval."

**Iterate through rewrite process, then propose complete new file for approval.**

---

#### [8] Sidecar Management (Only if sidecar exists)

**Display Sidecar Inventory:**
```
Sidecar Contents: {sidecar_path}
─────────────────────────────────────────
{list_sidecar_files_with_sizes}

What would you like to do?

[M] Edit memories.md
[I] Edit instructions.md
[W] Manage workflows
[K] Manage knowledge files
[C] Cancel - Return to scope menu
```

**Handle sidecar editing** (similar pattern: display → intent → propose → approve).

---

### 4. Apply Approved Changes

**CRITICAL: Use atomic swap pattern as in Simple Agent editing.**

**Additional Expert Agent Concerns:**

1. **Preserve YAML Frontmatter Integrity:**
   - When modifying frontmatter, validate YAML syntax before applying
   - Preserve field order unless intentionally reordering
   - Maintain indentation (2 spaces standard)

2. **Preserve Section Structure:**
   - Keep H2 section markers intact
   - Maintain section order unless reordering requested
   - Preserve markdown formatting (lists, emphasis, code blocks)

3. **Sidecar Coherence:**
   - If agent persona changed, warn if sidecar/memories.md may need updating
   - If tools changed, warn if sidecar/instructions.md may reference old tools
   - Log sidecar coherence warnings in session

**Application Protocol:**
(Same atomic swap as Simple Agent: temp → old → new)

1. Create temp file with proposed changes
2. Verify temp file (parse YAML, verify structure)
3. Atomic swap to apply changes
4. Verify final file (YAML valid, sections intact)

**Extra Validation for Expert Agents:**
- Parse YAML frontmatter successfully
- Verify all required sections present (or intentionally removed)
- Check for broken internal references
- Validate sidecar references if applicable

### 5. Record Edit in Session

Update session document frontmatter:

Add to `editsPerformed[]` array:
```yaml
editsPerformed:
  - component: "{currentTarget}"
    componentType: "agent"
    agentType: "expert"
    editType: "{scope_type}" # persona | capabilities | tools | communication | frontmatter | custom_section | full_rewrite | sidecar
    scope: "{specific_section_or_field}"
    timestamp: "{ISO_timestamp}"
    sections_modified: [{list_of_sections}]
    frontmatter_changed: {true | false}
    sidecar_affected: {true | false}
    change_summary: "{user_approved_summary}"
    checksum_before: "{original_checksum}"
    checksum_after: "{new_checksum}"
    warnings: [{sidecar_coherence_warnings}]
```

### 6. Display Edit Confirmation

Show detailed confirmation with structure preservation status:

```
✓ Edit Applied Successfully
─────────────────────────────────────────
File: {agent_filename}
Type: Expert Agent
Scope: {edit_scope}
Sections Modified: {section_list}

Structure Validation:
  ✓ YAML Frontmatter: Valid
  ✓ Required Sections: Present
  ✓ Markdown Structure: Intact
  {sidecar_status}

Changes:
  Lines: +{added} -{removed}
  Checksum: {new_checksum_first_8}...

Backup: Original preserved at {backup_path}
Lock: Still held by this session

{warnings_if_any}

Next: Validation
─────────────────────────────────────────
```

**Warnings Example:**
```
⚠️  Sidecar Coherence Warnings:
  - Persona changed: Consider reviewing sidecar/memories.md
  - Tools updated: Check sidecar/instructions.md for tool references
```

### 7. Present MENU OPTIONS

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue to Validation"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask} to explore alternative editing approaches or get suggestions for the modified sections
- IF P: Execute {partyModeWorkflow} to get feedback from other agents on structural or content decisions
- IF C: Save session state to {outputFile}, update frontmatter with this step completion, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: Help user respond, then [Redisplay Menu Options](#7-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After Advanced Elicitation or Party Mode execution completes, return to this menu
- User can chat or ask questions - always respond and then redisplay the menu options

## CRITICAL STEP COMPLETION NOTE

This step completes when:
- User selected edit scope from menu
- Section-specific edit intent gathered and confirmed
- Current section content displayed before proposing changes
- Changes proposed with diff-style comparison shown
- User explicitly approved proposed changes
- Changes applied using atomic swap pattern
- Final file verified (YAML valid, structure intact)
- Sidecar coherence checked (warnings issued if needed)
- Session editsPerformed array updated with complete record
- Edit confirmation displayed with structure validation status
- User selects [C] Continue from menu

ONLY WHEN [C continue option] is selected and all edit operations are complete, verified, and recorded, will you then save the session document to `{outputFile}`, update the frontmatter with step completion, load and read fully `{nextStepFile}` to execute step-05-validate.md and begin the validation process.

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Edit scope selected from structured menu (not assumed)
- Section-specific intent gathered through focused questions
- Current content displayed before showing proposal
- Proposed changes shown with diff-style comparison
- User explicitly approved changes before applying
- YAML frontmatter preserved and validated (if modified)
- Section structure maintained (H2 markers, order, formatting)
- Changes applied using atomic swap pattern
- Final file validated (YAML parses, structure intact)
- Sidecar coherence checked and warnings issued if needed
- Session editsPerformed array updated with detailed record
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Assuming edit scope without menu selection
- Skipping scope selection and directly asking for changes
- Making changes without user intent or approval
- Not displaying current section content before proposing changes
- Applying changes before user approval
- Modifying unselected sections or frontmatter
- Breaking YAML syntax or section structure
- Not validating YAML after frontmatter changes
- Ignoring sidecar coherence implications
- Not recording edit scope in session frontmatter
- Proceeding to validation without user selecting [C]
- Not checking for sidecar when editing related content

**Master Rule:** Expert agent editing is SCOPED and STRUCTURED. User selects WHAT to edit from menu, then collaborates on HOW to edit. YAML and section structure MUST be preserved. Sidecar coherence MUST be checked. Skipping scope selection, breaking structure, or ignoring sidecar is FORBIDDEN and constitutes SYSTEM FAILURE.
