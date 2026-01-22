---
name: 'step-04b-workflow-add'
description: 'Add a new workflow to the module by delegating to create-workflow or guiding through manual creation'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04b-workflow-add.md'
nextStepFile: '{workflow_path}/steps/step-05-validate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Workflow References
createWorkflowPath: '{project-root}/_bmad/bmb/workflows/create-workflow/workflow.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 4b: Add New Workflow to Module

## STEP GOAL:

To add a new workflow to the module by either delegating to the create-workflow workflow (if available) or guiding the user through manual workflow creation and registration in module.yaml.

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
- ✅ You bring workflow creation expertise and strategic guidance
- ✅ User brings knowledge of desired workflow functionality
- ✅ Maintain strategic, holistic, systems-thinking communication style

### Step-Specific Rules:

- 🎯 Focus ONLY on adding a new workflow, not editing existing ones
- 🚫 FORBIDDEN to modify module.yaml without creating backup first
- 💬 Approach: Delegate to create-workflow if available, otherwise guide creation
- 📋 Always register workflow in module.yaml after creation

## EXECUTION PROTOCOLS:

- 🎯 Check for create-workflow availability first
- 💾 Create backup of module.yaml before any modification
- 📖 Update frontmatter `editsPerformed` array with workflow addition
- 🚫 FORBIDDEN to proceed without proper workflow structure created

## CONTEXT BOUNDARIES:

- Available context: Module path and structure from session
- Focus: Creating and registering a new workflow
- Limits: Do not edit existing workflows
- Dependencies: Module.yaml must exist and be valid

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Context

Read from {outputFile} frontmatter:
- `modulePath`: Path to the module being edited
- `module_name`: Name of the module
- `moduleAnalysis`: Structure of the module

Display:
```
Adding new workflow to module: {module_name}
Module location: {modulePath}
```

### 2. Check for create-workflow Workflow

Attempt to locate `{createWorkflowPath}`.

**If found:**
Display:
```
✓ create-workflow workflow detected at {createWorkflowPath}

I can delegate to the create-workflow workflow to guide you through creating
a complete, BMAD-compliant workflow with all necessary files and structure.

Would you like to use the create-workflow workflow? [Y/N]
```

Wait for user response.

**If user selects Y:**
1. Inform user: "Delegating to create-workflow. After completion, return here to register the workflow in module.yaml."
2. Execute {createWorkflowPath}
3. When create-workflow completes, continue to step 3 below

**If user selects N or create-workflow not found:**
Proceed to manual workflow creation in step 2.1 below

### 2.1 Manual Workflow Creation (if not delegating)

Display:
```
I'll guide you through creating a workflow manually.

First, I need some information about the workflow:
```

#### 2.1.1 Gather Workflow Details

Ask user for:
1. **Workflow name** (kebab-case, e.g., "review-code")
   - Validate: lowercase, hyphens only, no spaces
2. **Workflow type**:
   - [S] Standalone (step-based workflow with step files)
   - [L] Legacy (single workflow.md file)

Wait for responses and validate.

#### 2.1.2 Create Workflow Structure

**For Standalone workflows:**

1. Create directory structure:
```
{modulePath}/workflows/{workflow-name}/
{modulePath}/workflows/{workflow-name}/steps/
```

2. Create workflow.md from basic template:
```markdown
---
name: '{workflow-name}'
description: '[User to provide description]'
type: 'standalone'
---

# {Workflow Name} Workflow

## Goal

[User to define workflow goal]

## Architecture

This is a step-based workflow with the following structure:

- step-01-init.md - Initialize workflow
- [Additional steps to be defined]

## Execution

To run this workflow:
[User to define execution instructions]
```

3. Create step-01-init.md from template:
```markdown
---
name: 'step-01-init'
description: 'Initialize {workflow-name} workflow'

workflow_path: '{project-root}/{modulePath}/workflows/{workflow-name}'

thisStepFile: '{workflow_path}/steps/step-01-init.md'
nextStepFile: '{workflow_path}/steps/step-02-[next-step].md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{output_folder}/{workflow-name}-{project_name}.md'
---

# Step 1: Initialize {Workflow Name}

## STEP GOAL:

[User to define initialization goal]

## MANDATORY EXECUTION RULES (READ FIRST):

[Standard rules - user to customize]

## Sequence of Instructions

### 1. [First Action]

[User to define]

### 2. Present MENU OPTIONS

Display: "**Proceeding to next step...**"

#### Menu Handling Logic:

- After initialization complete, load, read entire file, then execute {nextStepFile}
```

Save these files.

**For Legacy workflows:**

1. Create single workflow.md file:
```
{modulePath}/workflows/{workflow-name}.md
```

2. Populate with basic template:
```markdown
---
name: '{workflow-name}'
description: '[User to provide description]'
type: 'legacy'
---

# {Workflow Name} Workflow

[User to define workflow content]
```

Save file.

Display:
```
✓ Workflow structure created at {modulePath}/workflows/{workflow-name}/
✓ Basic template files generated
→ You'll need to customize the workflow content after this edit session
```

### 3. Register Workflow in module.yaml

Now register the new workflow in the module configuration.

#### 3.1 Create Backup

Before modifying module.yaml, create backup:

```
cp {modulePath}/module.yaml {modulePath}/module.yaml.backup-{timestamp}
```

Display:
```
✓ Backup created: module.yaml.backup-{timestamp}
```

#### 3.2 Read Current module.yaml

Parse {modulePath}/module.yaml and locate the `workflows:` array.

#### 3.3 Add Workflow Entry

**For Standalone workflows:**
Add entry to workflows array:
```yaml
workflows:
  - name: '{workflow-name}'
    type: 'standalone'
    description: '[User-provided description]'
    path: 'workflows/{workflow-name}/workflow.md'
    steps_path: 'workflows/{workflow-name}/steps/'
```

**For Legacy workflows:**
Add entry to workflows array:
```yaml
workflows:
  - name: '{workflow-name}'
    type: 'legacy'
    description: '[User-provided description]'
    path: 'workflows/{workflow-name}.md'
```

#### 3.4 Write Updated module.yaml

Save the modified module.yaml file.

Display:
```
✓ Workflow registered in module.yaml
✓ Entry added to workflows array
```

### 4. Update Session Tracking

Update {outputFile} frontmatter `editsPerformed` array:

```yaml
editsPerformed:
  - type: 'workflow-add'
    workflow_name: '{workflow-name}'
    workflow_type: 'standalone' | 'legacy'
    files_created:
      - '{modulePath}/workflows/{workflow-name}/workflow.md'
      - '{modulePath}/workflows/{workflow-name}/steps/step-01-init.md'  # if standalone
    files_modified:
      - '{modulePath}/module.yaml'
    backup_created: '{modulePath}/module.yaml.backup-{timestamp}'
    timestamp: '{ISO8601-timestamp}'
```

### 5. Present Summary

Display:
```
═══════════════════════════════════════════════
Workflow Addition Complete
═══════════════════════════════════════════════

Added Workflow: {workflow-name}
Type: {standalone/legacy}
Location: {modulePath}/workflows/{workflow-name}/

Files Created:
  ✓ workflow.md
  ✓ steps/step-01-init.md  [if standalone]

Configuration Updated:
  ✓ module.yaml (registered in workflows array)

Backup Created:
  → module.yaml.backup-{timestamp}

Next Steps:
  1. Validation will verify module structure integrity
  2. You can customize workflow content after this session
  3. Run the module to test the new workflow

═══════════════════════════════════════════════
```

### 6. Present MENU OPTIONS

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
- IF P: Execute {partyModeWorkflow}
- IF C: Update frontmatter `stepsCompleted` to add "4b-workflow-add", save {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: Help user respond then [Redisplay Menu Options](#6-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then end with display again of the menu options

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN user selects 'C' (Continue option) and the workflow has been created and registered, will you then:

1. Update frontmatter `stepsCompleted` to include "4b-workflow-add"
2. Save {outputFile} with updated editsPerformed tracking
3. Load, read entire file, then execute `{nextStepFile}` to begin validation

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- create-workflow delegation check performed correctly
- Workflow name validated (kebab-case)
- Workflow type selected (Standalone or Legacy)
- Directory structure created appropriately for type
- Template files generated with proper frontmatter
- Backup of module.yaml created before modification
- Workflow registered in module.yaml workflows array
- Session tracking updated with editsPerformed entry
- Summary displayed with all created files
- Menu presented and user selected 'C'
- Frontmatter updated before loading validation step

### ❌ SYSTEM FAILURE:

- Creating workflow without user providing name/type
- Not validating workflow name format
- Missing backup creation before module.yaml modification
- Modifying module.yaml without proper YAML parsing
- Not tracking the edit in editsPerformed array
- Creating incomplete workflow structure
- Proceeding to validation without user selecting 'C'
- Not updating stepsCompleted before loading next step

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
