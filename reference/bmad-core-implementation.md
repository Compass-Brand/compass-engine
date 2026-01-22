# BMAD Core Module - Implementation Documentation

> **Source:** bmad-code-org/BMAD-METHOD repository on GitHub
> **Version:** v6 Alpha (as of 2026-01-09)
> **Location:** `src/core/` in the BMAD-METHOD repository

## Overview

**BMad Core** (Collaboration Optimized Reflection Engine) is the foundational module that all BMAD modules depend upon. It provides universal framework capabilities for human-AI collaboration including:

- Configuration management
- Workflow execution engine
- Multi-agent conversation orchestration (Party Mode)
- Brainstorming facilitation with 60+ creative techniques
- Advanced elicitation with 50+ reasoning methods
- Common tasks (document sharding, adversarial review, indexing)

---

## Directory Structure

```
src/core/
├── module.yaml                    # Core module configuration
├── agents/
│   └── bmad-master.agent.yaml     # Master executor agent
├── resources/
│   └── excalidraw/                # Diagram resources
├── tasks/
│   ├── workflow.xml               # Main workflow execution engine
│   ├── index-docs.xml             # Document indexing task
│   ├── shard-doc.xml              # Document sharding task
│   └── review-adversarial-general.xml  # Adversarial review task
└── workflows/
    ├── brainstorming/             # Creative brainstorming workflow
    ├── party-mode/                # Multi-agent conversation
    └── advanced-elicitation/      # Deep reasoning methods
```

---

## Core Module Configuration (module.yaml)

```yaml
code: core
name: "BMad Core Module"
header: "BMad Core Configuration"

# User configuration prompts
user_name:
  prompt: "What shall the agents call you?"
  default: "BMad"

communication_language:
  prompt: "Preferred chat language/style?"
  default: "English"

document_output_language:
  prompt: "Preferred document output language?"
  default: "English"

output_folder:
  prompt: "Where should default output files be saved?"
  default: "_bmad-output"
  result: "{project-root}/{value}"
```

---

## BMad Master Agent

**File:** `agents/bmad-master.agent.yaml`

The BMad Master is the primary execution engine and knowledge custodian for BMAD operations.

### Identity
- **Role:** Master Task Executor + BMad Expert + Guiding Facilitator Orchestrator
- **Icon:** Wizard emoji
- **Communication Style:** Direct and comprehensive, refers to himself in 3rd person

### Key Features
- Loads runtime resources on demand (never pre-loads)
- Presents numbered lists for all choices
- Communicates in configured `communication_language`

### Menu Commands
| Trigger | Action |
|---------|--------|
| `LT` or `list-tasks` | List all tasks from task-manifest.csv |
| `LW` or `list-workflows` | List all workflows from workflow-manifest.csv |

---

## Workflow Execution Engine (workflow.xml)

**File:** `tasks/workflow.xml`

The core workflow execution engine that powers all BMAD workflows.

### Execution Modes

| Mode | Description |
|------|-------------|
| **normal** | Full user interaction and confirmation at EVERY step |
| **yolo** | Skip confirmations, auto-proceed with simulated expert user |

### Execution Flow

1. **Load and Initialize Workflow**
   - Load `workflow.yaml` configuration
   - Resolve all `{config_source}:` references
   - Resolve system variables and paths
   - Load template if template-workflow

2. **Process Each Instruction Step**
   - Handle step attributes (optional, if, for-each, repeat)
   - Execute step content with variable substitution
   - Process tags: `action`, `check`, `ask`, `invoke-workflow`, `invoke-task`, `goto`
   - Handle `template-output` tags with user confirmation

3. **Completion**
   - Confirm document saved
   - Report workflow completion

### Supported Tags

**Structural Tags:**
- `step n="X" goal="..."` - Define numbered step
- `optional="true"` - Step can be skipped
- `if="condition"` - Conditional execution
- `for-each="collection"` - Iterate over items
- `repeat="n"` - Repeat n times

**Execution Tags:**
- `action` - Perform action
- `check if="condition">...</check>` - Conditional block
- `ask` - Prompt user (ALWAYS wait for response)
- `invoke-workflow` - Call another workflow
- `invoke-task` - Call a task
- `invoke-protocol` - Execute reusable protocol
- `goto step="x"` - Jump to step

**Output Tags:**
- `template-output` - Save content checkpoint
- `critical` - Cannot be skipped
- `example` - Show example output

### Template Output Checkpoint Options

When a `template-output` tag is encountered:
- `[a]` Advanced Elicitation - Start advanced elicitation workflow
- `[c]` Continue - Proceed to next step
- `[p]` Party-Mode - Start multi-agent discussion
- `[y]` YOLO - Auto-complete rest of document

---

## Brainstorming Workflow

**Location:** `workflows/brainstorming/`

### Files
- `workflow.md` - Main workflow definition
- `template.md` - Output document template
- `brain-methods.csv` - 60+ brainstorming techniques
- `steps/` - Step files for micro-file architecture:
  - `step-01-session-setup.md`
  - `step-01b-continue.md`
  - `step-02a-user-selected.md`
  - `step-02b-ai-recommended.md`
  - `step-02c-random-selection.md`
  - `step-02d-progressive-flow.md`
  - `step-03-technique-execution.md`
  - `step-04-idea-organization.md`

### Workflow Architecture

Uses **micro-file architecture** for disciplined execution:
- Each step is a self-contained file with embedded rules
- Sequential progression with user control at each step
- Document state tracked in frontmatter
- Brain techniques loaded on-demand from CSV

### Critical Mindset

> "Your job is to keep the user in generative exploration mode as long as possible. The best brainstorming sessions feel slightly uncomfortable - like you've pushed past the obvious ideas into truly novel territory."

**Anti-Bias Protocol:** LLMs naturally drift toward semantic clustering. To combat this, consciously shift creative domain every 10 ideas.

**Quantity Goal:** Aim for 100+ ideas before any organization. The first 20 ideas are usually obvious - the magic happens in ideas 50-100.

### Session Flow

1. **Session Setup (Step 1)**
   - Check for existing workflow (continuation detection)
   - Initialize document from template
   - Gather session context (topic, goals)
   - Present approach selection:
     - `[1]` User-Selected Techniques
     - `[2]` AI-Recommended Techniques
     - `[3]` Random Technique Selection
     - `[4]` Progressive Technique Flow

2. **Technique Selection (Step 2)**
   - Based on approach, load appropriate step-02 variant
   - User-selected: Browse complete technique library
   - AI-recommended: Customized suggestions based on goals
   - Random: Discover unexpected methods
   - Progressive: Start broad, systematically narrow

3. **Technique Execution (Step 3)**
   - Interactive coaching, not script delivery
   - Execute one technique element at a time
   - Build on user's ideas with genuine contributions
   - Check for continuation interest before progression
   - "next technique" or "move on" for immediate transition

4. **Idea Organization (Step 4)**
   - Only when 100+ ideas generated
   - Categorize and prioritize
   - Create actionable next steps

### Brainstorming Techniques (60+ Methods)

Categories in `brain-methods.csv`:
- **Collaborative:** Yes And Building, Brain Writing Round Robin, Role Playing
- **Creative:** What If Scenarios, Analogical Thinking, First Principles, Reversal Inversion
- **Deep:** Five Whys, Morphological Analysis, Assumption Reversal, Question Storming
- **Structured:** SCAMPER, Six Thinking Hats, Mind Mapping, Resource Constraints
- **Theatrical:** Time Travel Talk Show, Alien Anthropologist, Parallel Universe Cafe
- **Wild:** Chaos Engineering, Pirate Code Brainstorm, Zombie Apocalypse Planning
- **Biomimetic:** Nature's Solutions, Ecosystem Thinking, Evolutionary Pressure
- **Quantum:** Observer Effect, Entanglement Thinking, Superposition Collapse
- **Cultural:** Indigenous Wisdom, Fusion Cuisine, Mythic Frameworks
- **Introspective:** Inner Child Conference, Shadow Work Mining, Future Self Interview

---

## Party Mode Workflow

**Location:** `workflows/party-mode/`

### Files
- `workflow.md` - Main workflow definition
- `steps/`:
  - `step-01-agent-loading.md`
  - `step-02-discussion-orchestration.md`
  - `step-03-graceful-exit.md`

### Purpose

Orchestrates group discussions between all installed BMAD agents, enabling natural multi-agent conversations.

### Workflow Architecture

Uses **micro-file architecture** with **sequential conversation orchestration**:
- Step 01: Load agent manifest and initialize party mode
- Step 02: Orchestrate ongoing multi-agent discussion
- Step 03: Handle graceful party mode exit

### Agent Manifest Processing

Parses CSV manifest to extract agent information:
- **name** - Agent identifier for system calls
- **displayName** - Agent's persona name for conversations
- **title** - Formal position and role description
- **icon** - Visual identifier emoji
- **role** - Capabilities and expertise summary
- **identity** - Background and specialization details
- **communicationStyle** - How they communicate
- **principles** - Decision-making philosophy and values
- **module** - Source module organization
- **path** - File location reference

### Agent Selection Intelligence

For each user message or topic:

1. **Relevance Analysis:**
   - Analyze user message for domain and expertise requirements
   - Identify which agents would naturally contribute
   - Consider conversation context and previous contributions
   - Select 2-3 most relevant agents for balanced perspective

2. **Priority Handling:**
   - If user addresses specific agent by name, prioritize that agent + 1-2 complementary agents
   - Rotate agent selection to ensure diverse participation
   - Enable natural cross-talk and agent-to-agent interactions

### Cross-Talk Patterns

Agents can interact naturally:
- Reference each other: "As [Another Agent] mentioned..."
- Build on points: "[Another Agent] makes a great point about..."
- Respectful disagreements: "I see it differently than [Another Agent]..."
- Follow-up questions between agents

### Question Handling Protocol

**Direct Questions to User:**
- End response round immediately after the question
- Clearly highlight: `**[Agent Name] asks: [Their question]**`
- Display: `_[Awaiting user response...]_`
- WAIT for user input before continuing

**Inter-Agent Questions:**
- Allow natural back-and-forth within same response round
- No pause needed for rhetorical questions

### Exit Triggers

**Automatic Triggers:**
- `*exit`
- `goodbye`
- `end party`
- `quit`

**Natural Conclusion:**
- If conversation seems to be concluding
- Ask user: "Would you like to continue the discussion or end party mode?"

### Graceful Exit Sequence

1. Acknowledge session conclusion
2. Generate 2-3 agent farewells in authentic character voices
3. Session highlight summary
4. Final party mode conclusion
5. Complete workflow exit with frontmatter update

### TTS Integration

Party mode includes Text-to-Speech for each agent response:
```bash
.claude/hooks/bmad-speak.sh "[Agent Name]" "[Their response]"
```

---

## Workflow-Init (9-Step Decision Tree)

**Location:** `src/modules/bmm/workflows/workflow-status/init/`

### Purpose

Initialize a new BMM project by determining level, type, and creating workflow path.

### The 9 Steps

#### Step 1: Scan for Existing Work
- Scan for BMM artifacts: PRD, epics, architecture, UX, brief, research, brainstorm
- Scan for implementation: stories, sprint-status, workflow-status
- Scan for codebase: source directories, package files, git repo
- **Categorize into state:**
  - `CLEAN` - No artifacts or code
  - `PLANNING` - Has PRD/spec but no implementation
  - `ACTIVE` - Has stories or sprint status
  - `LEGACY` - Has code but no BMM artifacts
  - `UNCLEAR` - Mixed state needs clarification

#### Step 2: Choose Setup Path
- If `CLEAN`: Continue to express/guided selection
- If `ACTIVE` with existing workflow-status: Exit (already initialized)
- Otherwise, offer options:
  1. **Continue** - Work with existing artifacts
  2. **Archive & Start Fresh** - Move old work to archive
  3. **Express Setup** - User knows exactly what they need
  4. **Guided Setup** - Walk through options

#### Step 3: Express Setup Path
- Ask: New project (greenfield) or existing codebase (brownfield)?
- Ask: Planning approach?
  1. **BMad Method** - Full planning for complex projects
  2. **Enterprise Method** - Extended planning with security/DevOps

#### Step 4: Guided Setup - Understand Project
- Ask about project goals
- Analyze for field type indicators:
  - Brownfield keywords: "existing", "current", "enhance", "modify"
  - Greenfield keywords: "new", "build", "create", "from scratch"
- Check for game development keywords (redirect to BMGD module)

#### Step 5: Guided Setup - Select Track
Present options:
1. **BMad Method** - Full planning: PRD + UX + Architecture
2. **Enterprise Method** - Extended: Method + Security + DevOps + Testing
3. **Help me decide** - Tailored guidance based on concerns
4. **Switch to Quick Flow** - Use quick-flow-solo-dev agent

#### Step 6: Discovery Workflows Selection
Select optional discovery workflows:
- **Brainstorm** - Creative exploration and ideation
- **Research** - Technical/competitive analysis
- **Product Brief** - Strategic product planning (greenfield only)

#### Step 7: Detect Track from Artifacts (if continuing existing)
Analyze artifacts to detect track:
- Has PRD → BMad Method
- Has Security/DevOps → Enterprise Method
- Has tech-spec only → Suggest Quick Flow

#### Step 8: Generate Workflow Path
- Load path file: `{path_files}/{{selected_track}}-{{field_type}}.yaml`
- Build workflow_items from path file
- Scan for existing completed work and update statuses

#### Step 9: Create Tracking File
- Display workflow path summary
- Create YAML tracking file at `{planning_artifacts}/bmm-workflow-status.yaml`
- Identify next workflow and agent
- Provide command to run next workflow

### Project Levels

```yaml
Level 0: Single Atomic Change (1 story)
         Bug fix, tiny feature, one small change
         Documentation: Minimal - tech spec only

Level 1: Small Feature (1-10 stories)
         Small coherent feature, minimal documentation
         Documentation: Tech spec

Level 2: Medium Project (5-15 stories)
         Multiple features, focused PRD
         Documentation: PRD + optional tech spec

Level 3: Complex System (12-40 stories)
         Subsystems, integrations, full architecture
         Documentation: PRD + architecture + JIT tech specs

Level 4: Enterprise Scale (40+ stories)
         Multiple products, enterprise architecture
         Documentation: PRD + architecture + JIT tech specs
```

### Workflow Paths

Four path files available:
- `method-greenfield.yaml` - BMad Method for new projects
- `method-brownfield.yaml` - BMad Method for existing codebases
- `enterprise-greenfield.yaml` - Enterprise Method for new projects
- `enterprise-brownfield.yaml` - Enterprise Method for existing codebases

---

## Workflow-Status Workflow

**Location:** `src/modules/bmm/workflows/workflow-status/`

### Purpose

Lightweight status checker that answers "what should I do now?" for any agent. Reads YAML status file for workflow tracking.

### Files
- `workflow.yaml` - Workflow configuration
- `instructions.md` - Multi-mode service instructions
- `project-levels.yaml` - Project scale level definitions
- `workflow-status-template.yaml` - Template for status file
- `init/` - Workflow-init subworkflow
- `paths/` - Path definition files

### Operating Modes

| Mode | Purpose |
|------|---------|
| `interactive` (default) | Normal status check flow |
| `validate` | Check if calling workflow should proceed |
| `data` | Extract specific information |
| `init-check` | Simple existence check |
| `update` | Centralized status file updates |

### Interactive Mode Flow

**Step 0: Determine Execution Mode**
- Check for `{{mode}}` parameter
- Default to `interactive` if not specified

**Step 1: Check for Status File**
- Search for `bmm-workflow-status.yaml`
- If not found, offer to run workflow-init
- If found, continue to step 2

**Step 2: Read and Parse Status**
- Parse YAML file and extract metadata
- Identify completed, pending, and skipped workflows
- Determine current state and next workflow

**Step 3: Display Current Status**
```
## Current Status

**Project:** {{project}} (Level {{project_level}} {{project_type}})
**Path:** {{workflow_path}}
**Progress:** [List of phases and workflows with status]

## Next Steps

**Next Workflow:** {{next_workflow_name}}
**Agent:** {{next_agent}}
**Command:** /bmad:bmm:workflows:{{next_workflow_id}}
```

**Step 4: Offer Actions**
1. Start next workflow
2. Run optional workflow (if available)
3. View full status YAML
4. Update workflow status
5. Exit

### Service Modes

**Validate Mode (Step 10):**
- Check if calling workflow should proceed
- Return: `status_exists`, `should_proceed`, `warning`, `suggestion`

**Data Mode (Step 20):**
- Extract specific information from status file
- Options: `project_config`, `workflow_status`, `all`

**Init-Check Mode (Step 30):**
- Simple existence check
- Return: `status_exists`, `suggestion`

**Update Mode (Step 40):**
- Centralized status file updates
- Actions: `complete_workflow`, `skip_workflow`

---

## Advanced Elicitation Workflow

**Location:** `workflows/advanced-elicitation/`

### Files
- `workflow.xml` - XML-based workflow definition
- `methods.csv` - 50+ elicitation/reasoning methods

### Purpose

LLM rethinking with advanced reasoning methods. Used when:
- User selects `[a]` at template-output checkpoints
- Deeper exploration of a specific concept is needed

### Available Methods (Categories)

From `methods.csv`:
- Analytical methods
- Creative methods
- Systems thinking methods
- Decision-making methods
- Problem-solving methods
- Cognitive methods

---

## Core Tasks

### Index Docs (`index-docs.xml`)
Generates or updates an `index.md` of all documents in specified directory.

### Shard Document (`shard-doc.xml`)
Splits large documents into sections for 90% token savings.

### Adversarial Review (`review-adversarial-general.xml`)
Critical content review using adversarial analysis approach.

---

## Key Implementation Patterns

### Micro-File Architecture
- Each step is a self-contained file with embedded rules
- Sequential progression with user control
- Document state tracked in frontmatter
- Prevents context drift in long workflows

### Frontmatter State Tracking
```yaml
---
stepsCompleted: [1, 2]
workflowType: 'party-mode'
user_name: '{{user_name}}'
date: '{{date}}'
agents_loaded: true
party_active: true
exit_triggers: ['*exit', 'goodbye', 'end party', 'quit']
---
```

### Variable Resolution
- `{project-root}` - Project root directory
- `{config_source}:field` - Load from config file
- `{installed_path}` - Workflow installation path
- `{{date}}` - System-generated date
- `{{user_name}}` - User name from config

### Protocol Invocation
Reusable protocols can be invoked via `invoke-protocol` tag:
- `discover_inputs` - Smart file discovery based on input_file_patterns

---

## Integration with BMAD Modules

### How Modules Use Core

1. **Configuration Inheritance**
   - All modules inherit Core configuration
   - `config_source` points to module config which inherits from Core

2. **Workflow Execution**
   - All workflows use `workflow.xml` execution engine
   - Consistent step processing, variable resolution, user interaction

3. **Agent Access**
   - BMad Master agent available to all modules
   - Agent manifests can include Core agents

4. **Task Access**
   - Core tasks available to all modules
   - Document sharding, indexing, review tasks

5. **Workflow Access**
   - Core workflows (Party Mode, Brainstorming, Advanced Elicitation) available to all
   - Can be invoked at any template-output checkpoint

---

## Summary

BMAD Core provides the foundational infrastructure for all BMAD modules:

| Component | Purpose |
|-----------|---------|
| `module.yaml` | Core configuration (user name, language, output folder) |
| `bmad-master.agent.yaml` | Primary execution agent |
| `workflow.xml` | Universal workflow execution engine |
| `brainstorming/` | 60+ creative techniques for idea generation |
| `party-mode/` | Multi-agent conversation orchestration |
| `advanced-elicitation/` | 50+ reasoning methods for deep exploration |
| Core Tasks | Document sharding, indexing, adversarial review |

The Core module enables:
- **Consistency** - All modules use same execution patterns
- **Flexibility** - Any module can invoke Core workflows/tasks
- **Extensibility** - Custom modules built on Core foundation
- **User Control** - Checkpoints, YOLO mode, technique selection
