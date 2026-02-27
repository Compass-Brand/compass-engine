---
name: workflow-engine
description: "Execute a workflow by loading workflow configuration, resolving variables, running instructions, and producing outputs."
standalone: false
internal: true
---

# Task: Execute Workflow

## Objective
Execute a target workflow by loading its configuration, resolving variables, reading required files completely, and running instructions in exact order.

## Critical Mandates
- Always read complete files. Never use partial reads for workflow files.
- Instructions are mandatory whether embedded or referenced (YAML, XML, or markdown forms).
- Execute steps in exact order. Never skip.
- Save output immediately when a `template-output` checkpoint is reached.
- You are responsible for end-to-end execution discipline.

## Global Workflow Rules
1. Steps execute in numerical order unless explicit `goto` is used.
2. Optional steps require user confirmation unless `#yolo` mode is active.
3. At each `template-output` checkpoint:
- save current section.
- present options.
- do not continue until user confirms (`c`) unless `#yolo`.

## Execution Modes
- `normal`: full user interaction and confirmations.
- `yolo`: skip confirmations and complete remaining steps autonomously.

## Flow
### 1. Load and Initialize Workflow
#### 1a. Load Configuration and Resolve Variables
- Read `workflow.yaml` from provided path.
- Load `config_source` (required).
- Resolve `{config_source}:...` references using loaded config.
- Resolve system variables and path tokens:
- `{project-root}`
- `{installed_path}`
- `{date}` and other system-generated values
- Ask user for any unresolved required variables.

#### 1b. Load Required Components
- Load instructions from:
- file path, or
- embedded instruction list in config.
- If template path exists: read full template.
- If validation path exists: register for later validation phase usage.
- Determine mode:
- template workflow (`template` not false), or
- action workflow (`template: false`).
- For data files (`csv`, `json`): store paths and load on-demand.

#### 1c. Initialize Output (template workflows only)
- Resolve `default_output_file` with all variables.
- Create destination directory if missing.
- If template workflow: write initial template content.
- If action workflow: skip file creation.

### 2. Process Instructions in Order
For each instruction step:

#### 2a. Handle Step Attributes
- If `optional="true"` and not `#yolo`: ask whether to include.
- Evaluate `if="condition"` guards.
- Expand `for-each="collection"` loops.
- Apply `repeat="n"` behavior.

#### 2b. Execute Step Content
- Process markdown or XML-tagged instructions.
- Resolve `{{variables}}`; ask user for missing values.
- Supported execution directives:
- `action`
- `check if="..."`
- `ask`
- `invoke-workflow`
- `invoke-task`
- `invoke-protocol name="..."`
- `goto step="..."`

#### 2c. Handle `template-output` Checkpoints
When checkpoint encountered:
- generate section content.
- write on first save; edit on subsequent saves.
- display generated section.
- ask user:
- `[a]` Advanced Elicitation
- `[c]` Continue
- `[o]` Autonomous Refinement Loop (Party + Elicitation)
- `[p]` Party Mode
- `[y]` YOLO remaining document

Actions:
- `a`: run `{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.md`
- `c`: continue to next instruction
- `o`: run `{project-root}/_bmad/core/workflows/autonomous-refinement-loop/workflow.md`
- `p`: run `{project-root}/_bmad/core/workflows/party-mode/workflow.md`
- `y`: enter `#yolo` mode for remaining workflow

#### 2d. Step Completion Prompt
- If no special tags and not `#yolo`, ask:
- `Continue to next step? (y/n/edit)`

### 3. Completion
- Confirm output was saved (if output-producing).
- Report workflow completion with output location.

## Supported Instruction Constructs
### Structural
- `step n="X" goal="..."`
- `optional="true"`
- `if="condition"`
- `for-each="collection"`
- `repeat="n"`

### Execution
- `action`
- `action if="condition"`
- `check if="condition"> ... </check>`
- `ask`
- `goto`
- `invoke-workflow`
- `invoke-task`
- `invoke-protocol`

### Output
- `template-output`
- `critical`
- `example`

## Reusable Protocol: `discover_inputs`
Execute only when `input_file_patterns` exists in workflow config.

### 1. Parse Input File Patterns
- Read configured pattern groups (e.g., `prd`, `architecture`, `epics`).
- Note each group's `load_strategy` (if provided).

### 2. Load Files with Smart Strategy
For each pattern group:

#### 2a. Prefer Sharded Documents
If sharded pattern exists:
- choose strategy (default `FULL_LOAD`).

`FULL_LOAD`
- load all matching shard files (prefer `index.md` first, then logical order).
- combine into `{pattern_name_content}`.

`SELECTIVE_LOAD`
- resolve templated shard path (e.g., `{{epic_num}}`).
- ask user for missing template vars if needed.
- load resolved file into `{pattern_name_content}`.

`INDEX_GUIDED`
- load shard `index.md`.
- analyze workflow objective and index structure.
- load all likely-relevant linked docs.
- err on the side of loading extra context.
- combine into `{pattern_name_content}`.

Mark group resolved and continue.

#### 2b. Fallback to Whole Document
If no sharded match:
- try whole-file pattern.
- load all matches completely.
- store in `{pattern_name_content}`.

#### 2c. Not Found Handling
- if neither sharded nor whole found:
- set `{pattern_name_content}` to empty.
- record as unavailable (informational, not hard error).

### 3. Report Discovery Results
- list loaded content variables and source files.
- clearly indicate unavailable groups.

## Final Critical Rules
- This file is the workflow execution engine source of truth.
- Follow instructions exactly.
- All workflow calls using legacy path `{project-root}/_bmad/core/tasks/workflow.xml` must remain compatible through shim.
- Execution style is facilitative and collaborative; do not skip required sections.
