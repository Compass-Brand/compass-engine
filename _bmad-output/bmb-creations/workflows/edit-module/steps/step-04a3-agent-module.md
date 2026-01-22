---
name: 'step-04a3-agent-module'
description: 'Edit module-type agents with complex structured components (activation, persona, menus, rules)'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04a3-agent-module.md'
nextStepFile: '{workflow_path}/steps/step-05-validate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Template References
agentModuleTemplate: '{workflow_path}/templates/agent-module-section.md'
---

# Step 04a3: Edit Module Agent (Complex Structured)

## STEP GOAL:

To enable precise editing of module-type agents with complex XML/structured formats by parsing their component structure (activation sequence, persona block, menu handlers, rules section) and allowing targeted modifications while preserving formatting and integrity.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist with deep knowledge of BMAD agent structures
- ✅ If you already have been given a name, communication_style and identity, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring technical expertise in structured agent formats, user brings domain knowledge
- ✅ Maintain strategic, holistic, systems-thinking communication style

### Step-Specific Rules:

- 🎯 Focus on structured component editing - preserve XML/YAML formatting
- 🚫 FORBIDDEN to corrupt agent structure or break syntax
- 💬 Approach: Parse structure, present components, edit by section
- 📋 Always create backup before modification
- 📋 Validate syntax after each edit before saving

## EXECUTION PROTOCOLS:

- 🎯 Parse agent into logical components before editing
- 💾 Create backup of agent file before ANY modification
- 📖 Update session editsPerformed array after successful edit
- 🚫 FORBIDDEN to save syntactically invalid XML/YAML

## CONTEXT BOUNDARIES:

- Available context: Agent file path from step 03 selection
- Focus: Component-level editing of module agent structure
- Limits: Cannot change agent type (module → simple), use workflows for that
- Dependencies: Requires valid module agent file with recognized structure

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Agent Context

Read from {outputFile} frontmatter:
- `currentTarget`: Path to the agent file being edited
- `agentType`: Should be "Module" (type detection from step 03)
- `module_name`: Name of the module

Display:
```
Editing Module Agent: {agent_name}
Agent Type: Module (Complex Structured)
Path: {currentTarget}
```

### 2. Parse Agent Structure

Read the complete agent file at `{currentTarget}`.

Analyze and identify the following components:

#### 2.1 Component Detection

Parse the agent file to identify:

**A. Activation Sequence Section**
- Location: Usually `<activation>` block or frontmatter `activation_steps:`
- Content: Numbered or bulleted steps for agent initialization
- Example markers: `activation:`, `<activation>`, `activation_steps:`

**B. Persona/Role Section**
- Location: Usually `<persona>` block or frontmatter `persona:`
- Content: Agent identity, communication style, expertise
- Example markers: `persona:`, `<persona>`, `role:`, `identity:`

**C. Menu Items Section**
- Location: Usually `<menu>` or `menu_items:` in frontmatter
- Content: List of user-facing menu options
- Example markers: `menu:`, `<menu>`, `menu_items:`

**D. Menu Handlers Section**
- Location: Usually `<handlers>` or embedded in steps
- Content: Logic for handling each menu selection
- Example markers: `handlers:`, `<handlers>`, `menu_handling:`

**E. Rules Section**
- Location: Usually `<rules>` block or frontmatter `rules:`
- Content: Constraints, protocols, forbidden actions
- Example markers: `rules:`, `<rules>`, `protocols:`, `constraints:`

**F. Full Agent Definition**
- The complete file content for advanced users

#### 2.2 Display Component Map

```
MODULE AGENT STRUCTURE DETECTED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] Activation Steps
    Location: Lines {start}-{end}
    Components: {count} steps detected

[2] Persona/Role
    Location: Lines {start}-{end}
    Components: Identity, style, expertise

[3] Menu Items
    Location: Lines {start}-{end}
    Components: {count} menu options

[4] Menu Handlers
    Location: Lines {start}-{end}
    Components: {count} handlers

[5] Rules
    Location: Lines {start}-{end}
    Components: {count} rules detected

[6] Full Agent Definition
    Complete file access for advanced editing
```

**IF NO STRUCTURE DETECTED:**
Display: "⚠️ Warning: Could not detect standard module agent structure. This may be a legacy format or non-standard agent. Would you like to [E] Edit as plain text [C] Cancel?"

### 3. Present Component Selection Menu

Display:
```
Select component to edit:

[1] Activation Steps - Edit initialization sequence
[2] Persona/Role - Modify agent identity and communication style
[3] Menu Items - Add/remove/edit menu options
[4] Menu Handlers - Edit menu handling logic
[5] Rules - Modify protocols and constraints
[6] Full Agent Definition - Advanced: Edit complete file
[C] Cancel - Return to component selection

Enter selection:
```

**Wait for user selection. Do NOT proceed automatically.**

### 4. Component Edit Handler

Based on user selection from Step 3, route to appropriate component editor:

#### 4.1 IF [1] Activation Steps Selected

**4.1.1** Extract activation sequence from parsed structure

**4.1.2** Display current activation steps:
```
CURRENT ACTIVATION SEQUENCE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{activation_content}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Edit options:
[A] Add new step
[M] Modify existing step (by number)
[D] Delete step (by number)
[R] Reorder steps
[F] Full rewrite

Enter choice:
```

**4.1.3** Based on sub-selection:

**IF A (Add):**
- Prompt: "Enter new step text:"
- Wait for user input
- Prompt: "Insert position? [E] End [A] After step # [B] Before step #"
- Insert new step at specified position
- Preserve formatting and numbering

**IF M (Modify):**
- Prompt: "Which step number to modify?"
- Display current step text
- Prompt: "Enter new text for this step:"
- Replace step content, preserve structure

**IF D (Delete):**
- Prompt: "Which step number to delete?"
- Display step to be deleted
- Confirm: "Delete this step? [Y/N]"
- Remove step and renumber remaining steps

**IF R (Reorder):**
- Display numbered steps
- Prompt: "Move step # to position #:"
- Reorder and renumber

**IF F (Full rewrite):**
- Display current full sequence
- Prompt: "Enter complete new activation sequence:"
- Wait for multi-line input (user signals done)
- Replace entire activation section

**4.1.4** Display updated activation sequence for review

**4.1.5** Prompt: "Apply this change? [Y] Yes [N] No [E] Edit more"
- IF Y: Proceed to Step 5 (Save Changes)
- IF N: Discard changes, return to Step 3
- IF E: Return to 4.1.2

#### 4.2 IF [2] Persona/Role Selected

**4.2.1** Extract persona/role section from parsed structure

**4.2.2** Display current persona:
```
CURRENT PERSONA/ROLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{persona_content}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Edit options:
[I] Identity - Modify agent name/title
[S] Communication Style - Change interaction approach
[E] Expertise - Edit domain knowledge
[F] Full persona rewrite

Enter choice:
```

**4.2.3** Based on sub-selection, prompt for new content and update the specific subsection

**4.2.4** Display updated persona for review

**4.2.5** Prompt: "Apply this change? [Y] Yes [N] No [E] Edit more"
- IF Y: Proceed to Step 5 (Save Changes)
- IF N: Discard changes, return to Step 3
- IF E: Return to 4.2.2

#### 4.3 IF [3] Menu Items Selected

**4.3.1** Extract menu items from parsed structure

**4.3.2** Display current menu:
```
CURRENT MENU ITEMS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{list numbered menu items with labels and descriptions}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Edit options:
[A] Add menu item
[M] Modify menu item (by number)
[D] Delete menu item (by number)
[R] Reorder menu items

Enter choice:
```

**4.3.3** Handle sub-selection similar to activation steps (add/modify/delete/reorder)

**4.3.4** Display updated menu for review

**4.3.5** Prompt: "Apply this change? [Y] Yes [N] No [E] Edit more"
- IF Y: Proceed to Step 5 (Save Changes)
- IF N: Discard changes, return to Step 3
- IF E: Return to 4.3.2

#### 4.4 IF [4] Menu Handlers Selected

**4.4.1** Extract menu handlers from parsed structure

**4.4.2** Display current handlers:
```
CURRENT MENU HANDLERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{list handlers with their associated menu items}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Edit options:
[M] Modify handler logic (by menu item)
[F] Full handler section rewrite

Enter choice:
```

**4.4.3** Based on sub-selection:

**IF M (Modify):**
- Prompt: "Which menu item handler to edit?"
- Display current handler logic
- Prompt: "Enter new handler logic:"
- Replace handler content

**IF F (Full rewrite):**
- Display current full handler section
- Prompt: "Enter complete new handler section:"
- Replace entire handler section

**4.4.4** Display updated handlers for review

**4.4.5** Prompt: "Apply this change? [Y] Yes [N] No [E] Edit more"
- IF Y: Proceed to Step 5 (Save Changes)
- IF N: Discard changes, return to Step 3
- IF E: Return to 4.4.2

#### 4.5 IF [5] Rules Selected

**4.5.1** Extract rules section from parsed structure

**4.5.2** Display current rules:
```
CURRENT RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{rules_content}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Edit options:
[A] Add rule
[M] Modify rule (by number)
[D] Delete rule (by number)
[F] Full rules rewrite

Enter choice:
```

**4.5.3** Handle sub-selection similar to activation steps

**4.5.4** Display updated rules for review

**4.5.5** Prompt: "Apply this change? [Y] Yes [N] No [E] Edit more"
- IF Y: Proceed to Step 5 (Save Changes)
- IF N: Discard changes, return to Step 3
- IF E: Return to 4.5.2

#### 4.6 IF [6] Full Agent Definition Selected

**4.6.1** Display warning:
```
⚠️  ADVANCED MODE: FULL AGENT EDIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You are about to edit the complete agent file directly.
This requires understanding of the agent XML/YAML structure.

Backup will be created automatically.

Proceed? [Y] Yes [N] No, use component editor
```

**4.6.2** IF N: Return to Step 3

**4.6.3** IF Y:
- Display current full agent content
- Prompt: "Enter complete new agent content (or type 'CANCEL' to abort):"
- Wait for multi-line input
- IF input is 'CANCEL': Return to Step 3
- Otherwise: Store new content for validation

**4.6.4** Proceed to Step 5 (Save Changes)

#### 4.7 IF [C] Cancel Selected

Return to Step 3 component selection menu

### 5. Save Changes

**5.1** Create backup before modification:
```
Creating backup...
Backup location: {module_path}/.backup/{timestamp}/{agent_filename}.bak
```

**5.2** Execute backup:
- Copy current agent file to `{module_path}/.backup/{timestamp}/{agent_filename}.bak`
- Verify backup created successfully
- Update backup manifest if exists

**5.3** Syntax validation:

**FOR XML format:**
- Attempt to parse as XML
- Check for balanced tags
- Verify no duplicate attributes
- IF INVALID: Display error, offer [R] Retry edit [D] Discard changes

**FOR YAML format:**
- Attempt to parse as YAML
- Check for proper indentation
- Verify no duplicate keys
- IF INVALID: Display error, offer [R] Retry edit [D] Discard changes

**5.4** IF validation passes:
- Write modified content to agent file
- Display: "✅ Agent file updated successfully"

**5.5** Update session tracking:

Append to {outputFile} frontmatter `editsPerformed` array:
```yaml
editsPerformed:
  - file: "{currentTarget}"
    component: "agent"
    subcomponent: "{selected_component}"  # e.g., "activation", "persona", "menu_items"
    timestamp: "{timestamp}"
    backup: "{module_path}/.backup/{timestamp}/{agent_filename}.bak"
```

**5.6** Display success summary:
```
EDIT COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Modified: {component_name}
Agent: {agent_name}
Backup: {backup_path}

Changes have been recorded in the edit session.
```

### 6. Present MENU OPTIONS

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
- IF P: Execute {partyModeWorkflow}
- IF C: Update frontmatter to add step 4a3 to `stepsCompleted`, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#6-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then redisplay the menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and agent file has been successfully modified with backup created, will you then load and read fully `{nextStepFile}` to execute and begin validation.

Before loading next step, ensure:
1. ✅ Backup created in `{module_path}/.backup/{timestamp}/`
2. ✅ Agent file syntactically valid (XML/YAML parsed successfully)
3. ✅ Session frontmatter updated with edit record
4. ✅ Step 4a3 added to `stepsCompleted` array

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Agent structure correctly parsed into components
- User selected component and provided edit input
- Backup created before modification
- Syntax validation passed
- Modified content saved to agent file
- Edit record appended to session frontmatter
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Proceeding without creating backup first
- Saving syntactically invalid XML/YAML
- Not updating session editsPerformed array
- Auto-generating content without user input
- Corrupting agent structure during edit
- Proceeding to next step without user selecting 'C'
- Skipping syntax validation step

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
