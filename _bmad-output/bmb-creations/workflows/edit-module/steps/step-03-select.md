---
name: 'step-03-select'
description: 'Present navigable edit menu and route to appropriate edit handler based on user selection'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-03-select.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Routing Step References
agentLoadStep: '{workflow_path}/steps/step-04a-agent-load.md'
workflowLoadStep: '{workflow_path}/steps/step-04b-workflow-load.md'
configEditStep: '{workflow_path}/steps/step-04c-config.md'
docsEditStep: '{workflow_path}/steps/step-04d-docs.md'
---

# Step 3: Edit Target Selection

## STEP GOAL:

To present a clear, navigable menu of all module components and route the user to the appropriate editing handler based on their selection.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step, ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist
- ✅ If you already have been given communication or persona patterns, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring navigation expertise and strategic guidance
- ✅ User brings knowledge of what they want to edit

### Step-Specific Rules:

- 🎯 Focus ONLY on presenting menu and capturing user selection
- 🚫 FORBIDDEN to perform any edits in this step
- 💬 Present clear, numbered navigation structure
- 🚪 Route to appropriate step-04x based on selection

## EXECUTION PROTOCOLS:

- 🎯 Display navigable menu based on module analysis from step 2
- 💾 Store user selection in frontmatter `currentTarget`
- 📖 Update frontmatter `stepsCompleted` to add 3 before loading next step
- 🚫 FORBIDDEN to load next step until valid selection is made

## CONTEXT BOUNDARIES:

- Module analysis is available from step 2 output
- Session document contains complete component inventory
- Focus ONLY on menu navigation and selection
- Actual editing happens in step-04x files

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Retrieve Module Analysis

Read the Module Analysis section from {outputFile} to get:
- List of agents with types
- List of workflows with formats
- Configuration files
- Documentation files

### 2. Build Navigable Menu

Create hierarchical menu structure:

```
═══════════════════════════════════════════════
Module: {module_name}
═══════════════════════════════════════════════

[1] Agents
    1.1 analyst.md (Expert)
    1.2 architect.md (Simple)
    1.3 data-engineer.md (Module)

[2] Workflows
    2.1 create-prd/ (Standalone, 6 steps)
    2.2 review-code/ (Legacy)
    2.3 sprint-planning/ (Standalone, 8 steps)

[3] Configuration
    3.1 module.yaml
    3.2 config.yaml

[4] Documentation
    4.1 README.md
    4.2 CHANGELOG.md
    4.3 docs/architecture.md

[D] Done - Complete editing session

═══════════════════════════════════════════════
Select item to edit (e.g., '1.2' or '2.1'):
```

### 3. Capture User Selection

Wait for user to provide selection (e.g., "1.2", "2.1", "3.1", "D")

Validate selection:
- Must match a valid menu item
- If invalid: "Invalid selection. Please choose a valid item number."
- If valid: Proceed to step 4

### 4. Component-Specific Action Selection

Based on what was selected, present appropriate actions:

**For Agents (1.x):**
```
Selected: analyst.md (Expert Agent)

What would you like to do?
[E] Edit - Modify agent content
[V] View - View full agent file
[R] Remove - Delete agent from module

Select action:
```

**For Workflows (2.x):**
```
Selected: create-prd/ (Standalone Workflow, 6 steps)

What would you like to do?
[E] Edit - Modify workflow content
[V] View - View workflow structure
[R] Remove - Delete workflow from module

Select action:
```

**For Configuration (3.x):**
```
Selected: module.yaml

What would you like to do?
[E] Edit - Modify configuration
[V] View - View current configuration

Select action:
```

**For Documentation (4.x):**
```
Selected: README.md

What would you like to do?
[E] Edit - Modify documentation
[V] View - View current content

Select action:
```

**For Done (D):**
```
Are you sure you want to complete this editing session?
[Y] Yes - Proceed to validation and completion
[N] No - Return to menu

Confirm:
```

### 5. Store Selection and Route

Based on user's component and action selection:

**Update frontmatter:**
```yaml
currentTarget:
  type: "agent" | "workflow" | "config" | "docs"
  name: "analyst.md" | "create-prd" | "module.yaml" | "README.md"
  action: "edit" | "view" | "remove"
  subtype: "Expert" | "Standalone" | etc. (from analysis)
```

**Route to appropriate step:**

| Component Type | Action | Route To |
|----------------|--------|----------|
| Agent (1.x) | E, V, R | `{agentLoadStep}` |
| Workflow (2.x) | E, V, R | `{workflowLoadStep}` |
| Config (3.x) | E, V | `{configEditStep}` |
| Docs (4.x) | E, V | `{docsEditStep}` |
| Done (D) | Y | `{workflow_path}/steps/step-05-validate.md` (skip to validation) |
| Done (D) | N | Redisplay menu (stay in this step) |

### 6. Execute Routing

Before routing:
1. Update frontmatter `stepsCompleted` to add 3
2. Update frontmatter `currentTarget` with selection details
3. Save {outputFile}

Then:
4. Load, read entire file, then execute the appropriate step file based on routing table above

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN user makes a valid selection and action choice, will you then:

1. Update frontmatter with `currentTarget` details
2. Update frontmatter `stepsCompleted` to include 3
3. Save {outputFile}
4. Load, read entire file, then execute the appropriate routing step

The routing step will handle the actual editing, viewing, or removal operation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Menu built from module analysis correctly
- All components listed with accurate counts and types
- User selection captured and validated
- Action selection presented appropriately for component type
- `currentTarget` frontmatter updated with selection details
- Frontmatter `stepsCompleted` updated to include 3
- Correct routing step loaded based on selection
- Menu redisplayed if user requests or invalid selection

### ❌ SYSTEM FAILURE:

- Menu doesn't reflect actual module structure
- Missing components from menu
- Invalid selection not caught and handled
- Wrong action options presented for component type
- Routing to wrong step-04x file
- Not updating frontmatter before routing
- Not saving document before loading next step
- Proceeding without valid user selection

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
