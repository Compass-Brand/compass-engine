---
name: 'step-02-analyze'
description: 'Deep module structure analysis and component inventory'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-02-analyze.md'
nextStepFile: '{workflow_path}/steps/step-03-select.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Template References
analysisTemplate: '{workflow_path}/templates/analysis-section.md'

# Data References
moduleStructureReference: '{workflow_path}/data/module-structure-reference.md'
agentTypeDetection: '{workflow_path}/data/agent-type-detection.md'
workflowFormatDetection: '{workflow_path}/data/workflow-format-detection.md'
---

# Step 2: Module Structure Analysis

## STEP GOAL:

To perform deep analysis of the module structure, inventorying all components (agents, workflows, configuration, documentation), detecting component types and formats, and building a comprehensive understanding that will guide editing decisions.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist
- ✅ If you already have been given communication or persona patterns, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring deep module architecture expertise and systems thinking
- ✅ User brings knowledge of their module's purpose and history

### Step-Specific Rules:

- 🎯 Focus ONLY on analyzing module structure
- 🚫 FORBIDDEN to make any edits in this step - this is analysis only
- 💬 Present findings in a clear, navigable format
- 🔍 Build passive dependency graph without user burden

## EXECUTION PROTOCOLS:

- 🎯 Perform comprehensive analysis before displaying results
- 💾 Append analysis to {outputFile} in Module Analysis section
- 📖 Update frontmatter `stepsCompleted` to add 2 at the end of the array before loading next step
- 🚫 FORBIDDEN to load next step until analysis is complete and user selects 'C'

## CONTEXT BOUNDARIES:

- Module path and name are already loaded from step 1
- Session document exists with frontmatter from initialization
- Focus ONLY on structural analysis - no editing yet
- Build understanding for informed editing decisions

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Module Configuration Analysis

Read and parse `{module_path}/module.yaml`:

Extract and display:
- Module name and version
- Module description
- Agents registry (count and list)
- Workflows registry (count and list)
- Custom settings (if any)

### 2. Agent Component Inventory

Scan `{module_path}/agents/` directory:

For each agent file found:
1. Read the file
2. Detect agent type using `{agentTypeDetection}` rules:
   - **Simple Agent**: Basic agent file, markdown only
   - **Expert Agent**: Agent with sidecar files (tools, data, etc.)
   - **Module Agent**: Agent that coordinates other agents
3. Extract metadata:
   - Agent name (from H1 heading)
   - Description (from first paragraph or frontmatter)
   - File size
   - Last modified date
4. Identify tools referenced
5. Check for sidecar files

Build inventory table:

```markdown
#### Agents

| Name | Type | Size | Tools | Sidecar Files |
|------|------|------|-------|---------------|
| analyst | Expert | 12KB | Read, Grep, mcp__postgres__execute_sql | tools/, data/ |
| architect | Simple | 5KB | Read, Write | - |
```

### 3. Workflow Component Inventory

Scan `{module_path}/workflows/` directory:

For each workflow directory found:
1. Detect workflow format using `{workflowFormatDetection}` rules:
   - **Standalone**: workflow.md + steps/ directory
   - **Legacy**: workflow.yaml + workflow.xml
2. Count step files (if standalone)
3. Extract metadata:
   - Workflow name
   - Description (from frontmatter or YAML)
   - Step count (if applicable)
   - Last modified date
4. Check for templates/ and data/ subdirectories

Build inventory table:

```markdown
#### Workflows

| Name | Format | Steps | Templates | Data Files |
|------|--------|-------|-----------|------------|
| create-prd | Standalone | 6 | 4 | 2 |
| review-code | Legacy | N/A | 0 | 1 |
```

### 4. Configuration & Documentation Inventory

Check for additional components:

**Configuration:**
- `module.yaml` (already analyzed)
- `config.yaml` (if exists)
- Custom config files

**Documentation:**
- `README.md`
- `CHANGELOG.md`
- `docs/` directory (if exists)

### 5. Build Dependency Graph (Passive)

Analyze references between components:

- Agent-to-workflow references
- Workflow-to-agent references
- Cross-component tool dependencies

**Note:** This is passive analysis only - display findings but don't burden user with details unless requested.

Simple summary:
```
Dependencies Detected: 12 cross-component references found
```

### 6. Display Module Overview

Present comprehensive module overview to user:

```markdown
# Module Analysis: {module_name}

## Summary
- **Total Components:** [count]
- **Agents:** [count] ([simple], [expert], [module])
- **Workflows:** [count] ([standalone], [legacy])
- **Configuration Files:** [count]
- **Documentation Files:** [count]

## Component Details

[Insert inventory tables from above]

## Module Health
- ✅ All agents have valid format
- ⚠️ 2 workflows use legacy format
- ✅ Configuration is valid
- ✅ Documentation present
```

### 7. Present MENU OPTIONS

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then end with display again of the menu options

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
  - Purpose: Deep dive into module architecture or specific component analysis
  - After completion: Redisplay Menu Options
- IF P: Execute {partyModeWorkflow}
  - Purpose: Get multi-agent perspective on module structure or editing strategy
  - After completion: Redisplay Menu Options
- IF C: Save analysis content to {outputFile} Module Analysis section, update frontmatter `stepsCompleted` to add 2, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#7-present-menu-options)

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN C is selected and analysis content is saved to document and frontmatter is updated, will you then load, read entire file, then execute {nextStepFile} to begin the edit selection process.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Complete module structure analyzed
- All agents inventoried with type detection
- All workflows inventoried with format detection
- Configuration and documentation cataloged
- Dependency graph built (passive)
- Analysis appended to {outputFile}
- Frontmatter `stepsCompleted` updated to include 2
- User presented with clear module overview
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping any component category analysis
- Not detecting agent types or workflow formats
- Proceeding without complete inventory
- Not updating document with analysis
- Not updating frontmatter before loading next step
- Missing dependency analysis
- Proceeding without user 'C' selection

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
