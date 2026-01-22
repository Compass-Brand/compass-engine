---
name: 'step-04a-agent-add'
description: 'Add a new agent to the module (delegates to create-agent workflow if available)'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04a-agent-add.md'
nextStepFile: '{workflow_path}/steps/step-05-validate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
createAgentWorkflow: '{project-root}/_bmad/bmb/workflows/create-agent/workflow.md'

# Template References
agentSimpleTemplate: '{project-root}/_bmad/bmb/templates/agent-simple.md'
agentExpertTemplate: '{project-root}/_bmad/bmb/templates/agent-expert.md'
agentModuleTemplate: '{project-root}/_bmad/bmb/templates/agent-module.md'
---

# Step 04a: Add New Agent to Module

## STEP GOAL:

To add a new agent to the module by either delegating to the create-agent workflow (if available) or guiding the user through agent creation and registration in the module.yaml configuration.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate agent content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist with expertise in agent design
- ✅ If you already have been given a name, communication_style and identity, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring agent structure knowledge, user brings domain expertise and requirements
- ✅ Maintain strategic, holistic, systems-thinking communication style

### Step-Specific Rules:

- 🎯 Focus on agent creation and module registration
- 🚫 FORBIDDEN to create generic/placeholder agents without user specifications
- 💬 Approach: Understand requirements first, then create structured agent
- 📋 Always create backup of module.yaml before modification
- 📋 Validate agent file and module.yaml after changes

## EXECUTION PROTOCOLS:

- 🎯 Check for create-agent workflow availability first
- 💾 Create backup of module.yaml before ANY modification
- 📖 Update session editsPerformed array after agent creation
- 🚫 FORBIDDEN to add malformed agents or corrupt module.yaml

## CONTEXT BOUNDARIES:

- Available context: Module path and current module.yaml configuration
- Focus: Agent creation and module registration
- Limits: Cannot modify existing agents (use edit operations for that)
- Dependencies: Requires valid module.yaml with agents array

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Module Context

Read from {outputFile} frontmatter:
- `modulePath`: Path to the module directory
- `module_name`: Name of the module
- `moduleYamlPath`: Path to module.yaml file

Display:
```
Adding New Agent to Module: {module_name}
Module Path: {modulePath}
Module Config: {moduleYamlPath}
```

### 2. Check for Create-Agent Workflow

Attempt to locate {createAgentWorkflow} file.

**IF workflow exists:**

Display:
```
CREATE-AGENT WORKFLOW DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The create-agent workflow is available and provides a
comprehensive agent creation experience.

Options:
[D] Delegate to create-agent workflow (recommended)
[M] Manual creation (continue in this step)

Enter choice:
```

**IF user selects D (Delegate):**

Display:
```
Delegating to create-agent workflow...

When the workflow completes, return here to continue
the edit-module session.
```

**THEN:**
1. Load and execute {createAgentWorkflow}
2. After create-agent workflow completes, return to this step at Step 7 (Register Agent)
3. Skip Steps 3-6 (workflow handles creation)

**IF user selects M (Manual) OR workflow NOT found:**

Continue to Step 3 (Manual Creation)

### 3. Gather Agent Requirements

**3.1** Prompt for agent name:
```
Enter agent name (kebab-case, e.g., 'task-analyzer', 'code-reviewer'):
```

Wait for user input.

**Validation:**
- Must be kebab-case (lowercase, hyphens only)
- Must not conflict with existing agent names
- Length: 3-50 characters

**IF INVALID:**
- Display error with specific issue
- Re-prompt for valid name

**3.2** Store validated name as `{agent_name}`

**3.3** Prompt for agent type:
```
Select agent type:

[S] Simple Agent - Basic Q&A or single-purpose task
    Example: Lookup tool, simple calculator, status checker

[E] Expert Agent - Domain expert with deep knowledge
    Example: Senior developer, product strategist, data scientist

[M] Module Agent - Complex multi-step workflows
    Example: Code reviewer, project planner, comprehensive analyst

Enter choice [S/E/M]:
```

Wait for user input.

**3.4** Store selection as `{agent_type}`:
- S → "Simple"
- E → "Expert"
- M → "Module"

**3.5** Prompt for agent description:
```
Enter brief description of what this agent does (1-2 sentences):
```

Wait for user input. Store as `{agent_description}`.

### 4. Determine Template and Path

**4.1** Based on `{agent_type}`, set template and file path:

**IF agent_type = "Simple":**
- Template: {agentSimpleTemplate}
- File path: `{modulePath}/agents/{agent_name}.md`

**IF agent_type = "Expert":**
- Template: {agentExpertTemplate}
- File path: `{modulePath}/agents/{agent_name}.md`

**IF agent_type = "Module":**
- Template: {agentModuleTemplate}
- File path: `{modulePath}/agents/{agent_name}.md`

**4.2** Store determined values:
- `{template_path}`: Path to template file
- `{agent_file_path}`: Target path for new agent file

### 5. Generate Agent File from Template

**5.1** Check if template exists at `{template_path}`:

**IF template exists:**
- Read template file
- Substitute placeholders:
  - `{agent_name}` → user-provided name
  - `{agent_description}` → user-provided description
  - `{module_name}` → current module name
  - `{timestamp}` → current ISO timestamp
- Store result as `{agent_content}`

**IF template NOT found:**

Display:
```
⚠️ Template not found at: {template_path}

Generating basic agent structure...
```

Create minimal agent structure based on type:

**For Simple Agent:**
```markdown
---
name: '{agent_name}'
description: '{agent_description}'
agent_type: 'simple'
module: '{module_name}'
created: '{timestamp}'
---

# {agent_name} Agent

## Purpose

{agent_description}

## Activation

This is a simple agent. Activate by calling its function directly.

## Persona

You are {agent_name}, a helpful assistant specialized in {domain}.

## Rules

- Provide clear, accurate responses
- Stay focused on your domain expertise
- Ask for clarification when needed
```

**For Expert Agent:**
```markdown
---
name: '{agent_name}'
description: '{agent_description}'
agent_type: 'expert'
expertise_domain: '{domain}'
module: '{module_name}'
created: '{timestamp}'
---

# {agent_name} Expert Agent

## Purpose

{agent_description}

## Activation

This expert agent provides deep domain knowledge and strategic guidance.

## Persona

You are {agent_name}, a recognized expert in {domain}.

Your expertise includes:
- [Expertise area 1]
- [Expertise area 2]
- [Expertise area 3]

## Communication Style

[Strategic/Technical/Analytical] - Explain your communication approach

## Rules

- Provide expert-level insights with context
- Challenge assumptions constructively
- Reference best practices and patterns
- Think holistically about problems
```

**For Module Agent:**
```markdown
---
name: '{agent_name}'
description: '{agent_description}'
agent_type: 'module'
module: '{module_name}'
created: '{timestamp}'
---

# {agent_name} Module Agent

## Purpose

{agent_description}

## Activation Sequence

1. [Activation step 1]
2. [Activation step 2]
3. [Activation step 3]

## Persona

You are {agent_name}, a specialized agent for {purpose}.

## Menu Items

- [Option 1]: [Description]
- [Option 2]: [Description]
- Continue: Proceed to next phase

## Menu Handlers

### [Option 1] Handler
[Handler logic]

### [Option 2] Handler
[Handler logic]

## Rules

- Follow the activation sequence exactly
- Present menu after each major phase
- Track progress through the workflow
- Never skip steps or optimize without user approval
```

**5.2** Display generated agent content:
```
GENERATED AGENT STRUCTURE ({agent_type})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{agent_content}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is a basic structure. You can enhance it after creation.

Accept this structure? [Y] Yes [N] No, let me specify content
```

**5.3** IF user selects N:
```
Prompt: "Enter complete agent file content (or type 'TEMPLATE' to go back to template):"
```

Wait for multi-line input. Store as `{agent_content}`.

### 6. Create Agent File

**6.1** Verify agent file does not already exist:
```
Checking: {agent_file_path}
```

**IF file exists:**
```
⚠️ ERROR: Agent file already exists at this path!

Options:
[O] Overwrite (current file will be backed up)
[R] Rename new agent
[C] Cancel agent creation

Enter choice:
```

- IF O: Create backup of existing file, proceed with creation
- IF R: Go back to Step 3.1 (re-prompt for name)
- IF C: Abort and return to workflow

**6.2** Create agent file:
- Write `{agent_content}` to `{agent_file_path}`
- Verify file created successfully

**6.3** Display:
```
✅ Agent file created: {agent_file_path}
```

### 7. Register Agent in module.yaml

**7.1** Create backup of module.yaml:
```
Creating backup of module.yaml...
Backup location: {modulePath}/.backup/{timestamp}/module.yaml.bak
```

Execute backup:
- Copy `{moduleYamlPath}` to `{modulePath}/.backup/{timestamp}/module.yaml.bak`
- Verify backup created successfully

**7.2** Read and parse module.yaml:
- Load `{moduleYamlPath}` with YAML parser
- Extract `agents:` array
- Store current agents list

**7.3** Add new agent entry:

Append to agents array:
```yaml
agents:
  - name: '{agent_name}'
    type: '{agent_type}'  # Simple/Expert/Module
    path: 'agents/{agent_name}.md'
    description: '{agent_description}'
    added: '{timestamp}'
```

**7.4** Validate updated YAML:
- Attempt to parse modified YAML
- Check for syntax errors
- Verify no duplicate agent names

**IF validation fails:**
```
❌ YAML VALIDATION FAILED

Error: {error_message}

The backup has been preserved. Would you like to:
[R] Retry with corrections
[D] Discard changes and rollback
```

- IF R: Allow user to provide corrected YAML, re-validate
- IF D: Restore from backup, abort registration

**7.5** Write updated module.yaml:
- Save modified YAML to `{moduleYamlPath}`
- Verify write successful

**7.6** Display:
```
✅ Agent registered in module.yaml
```

### 8. Update Session Tracking

**8.1** Append to {outputFile} frontmatter `editsPerformed` array:
```yaml
editsPerformed:
  - operation: "agent_add"
    agent_name: "{agent_name}"
    agent_type: "{agent_type}"
    agent_file: "{agent_file_path}"
    config_modified: "{moduleYamlPath}"
    timestamp: "{timestamp}"
    backups:
      - "{modulePath}/.backup/{timestamp}/module.yaml.bak"
```

**8.2** Display completion summary:
```
AGENT CREATION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agent Name: {agent_name}
Agent Type: {agent_type}
Agent File: {agent_file_path}
Registered: ✅ module.yaml updated

Backups Created:
- {modulePath}/.backup/{timestamp}/module.yaml.bak

The agent is now part of the {module_name} module.
```

### 9. Present MENU OPTIONS

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
- IF P: Execute {partyModeWorkflow}
- IF C: Update frontmatter to add step 4a to `stepsCompleted`, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#9-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then redisplay the menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and agent has been successfully created and registered, will you then load and read fully `{nextStepFile}` to execute and begin validation.

Before loading next step, ensure:
1. ✅ Agent file created at `{agent_file_path}`
2. ✅ module.yaml backup created
3. ✅ Agent registered in module.yaml agents array
4. ✅ YAML syntax validated
5. ✅ Session frontmatter updated with creation record
6. ✅ Step 4a added to `stepsCompleted` array

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Agent requirements gathered (name, type, description)
- Agent file created from template or user content
- module.yaml backup created before modification
- Agent successfully registered in module.yaml
- YAML syntax validation passed
- Session tracking updated with creation record
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Creating agent without user specifications
- Generating placeholder/generic content without user input
- Modifying module.yaml without creating backup first
- Saving invalid YAML syntax
- Not updating session editsPerformed array
- Proceeding to next step without user selecting 'C'
- Overwriting existing agent without backup
- Corrupting module.yaml structure

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
