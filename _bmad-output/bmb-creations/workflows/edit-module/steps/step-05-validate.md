---
name: 'step-05-validate'
description: 'Run comprehensive validation and compliance checks on modified module components'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-05-validate.md'
nextStepFile: '{workflow_path}/steps/step-06-iterate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Template References
validationTemplate: '{workflow_path}/templates/validation-section.md'

# Data References
validationRulesData: '{workflow_path}/data/validation-rules.md'
---

# Step 5: Validation & Compliance Check

## STEP GOAL:

To ensure all edits made during this session are technically valid and optionally check compliance with BMAD standards, preventing corruption, broken references, and maintaining module integrity.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER skip validation - this protects against data corruption
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist with deep knowledge of BMAD standards
- ✅ If you already have been given a name, communication_style and identity, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring validation expertise, user brings edit intent understanding
- ✅ Maintain strategic, holistic, systems-thinking communication style

### Step-Specific Rules:

- 🎯 Focus ONLY on validation - do NOT make fixes automatically
- 🚫 FORBIDDEN to proceed to next step with blocking errors unresolved
- 💬 Approach: Report findings clearly, suggest fixes, user decides action
- 📋 Distinguish between BLOCKING errors and ADVISORY warnings

## EXECUTION PROTOCOLS:

- 🎯 Run three validation phases in sequence: SYNTAX → REFERENCE → COMPLIANCE
- 💾 After validation, append results to {outputFile}
- 📖 Update frontmatter `stepsCompleted` to add 5 at the end of the array before loading next step
- 🚫 FORBIDDEN to load next step until user selects 'C' and blocking errors resolved

## CONTEXT BOUNDARIES:

- Available context: All edits made in this session (from outputFile frontmatter)
- Focus: Verify technical correctness and optionally check BMAD compliance
- Limits: Do not auto-fix issues, user must approve changes
- Dependencies: Requires editsPerformed list from session frontmatter

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Validation Context

Read the following from {outputFile} frontmatter:
- `editsPerformed`: List of all edits made this session
- `modulePath`: Path to the module being edited
- `module_name`: Name of the module

Display:
```
Running validation for module: {module_name}
Edits to validate: {editsPerformed.length}
```

### 2. PHASE 1: SYNTAX VALIDATION

**Purpose:** Ensure files are technically parseable and won't cause runtime errors.

For EACH file in `editsPerformed`:

#### 2.1 YAML Syntax Check (for .yaml and .md files with frontmatter)

- Load file with strict YAML parser
- Check for:
  - Parse success (no exceptions)
  - No duplicate keys at same level
  - Proper quote balance
  - Valid UTF-8 encoding
  - Required fields present

**IF PARSE FAILS:**
- Record error with line number, column, and specific message
- Mark as BLOCKING ERROR (prevents save)
- Error Code: **E005**

#### 2.2 Markdown Syntax Check (for .md files)

- Verify file renders as valid Markdown
- Check for:
  - Balanced code fences (```)
  - Valid heading hierarchy (H1 → H2 → H3)
  - Proper list indentation

**IF INVALID:**
- Record warning (non-blocking unless severe)
- Suggest corrections

#### 2.3 Display Syntax Results

```
SYNTAX VALIDATION RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files Checked: {count}
✅ Passed: {passed_count}
❌ Failed: {failed_count}

{IF failed_count > 0}
BLOCKING ERRORS FOUND:

File: {filename}
Error: E005 - {error_message}
Line: {line_number}, Column: {column}
Context: {code_snippet}

{repeat for each error}
{END IF}
```

**IF BLOCKING ERRORS EXIST:**
- HALT immediately
- Display: "VALIDATION FAILED - Blocking syntax errors must be fixed before proceeding."
- Offer: [F] Fix manually [R] Rollback this edit [H] Help
- Do NOT proceed to Phase 2 until resolved

### 3. PHASE 2: REFERENCE VALIDATION

**Purpose:** Ensure all file paths, variables, and cross-references resolve correctly.

For EACH edited file:

#### 3.1 Extract References

Scan for:
- Absolute file paths: `/path/to/file.md`
- Relative file paths: `./agents/analyst.md`
- Variable paths: `{workflow_path}/steps/`
- Module references: `bmm/workflows/create-prd`
- Internal anchors: `#section-name`
- Cross-file anchors: `step-02.md#validation`

#### 3.2 Resolve Variables

- Load variable definitions from workflow.md frontmatter
- Load module-level variables from module.yaml
- Substitute: `{project-root}` → actual path
- Substitute: `{workflow_path}` → actual path
- Substitute custom variables

#### 3.3 Verify Each Reference

For each resolved reference:
- File paths: Check file exists
- Directories: Check directory exists
- Anchors: Parse target file, verify section heading exists
- Mark: VALID | INVALID | WARNING

#### 3.4 Circular Reference Detection

Build reference graph:
- Node: Each file in module
- Edge: A → B if A references B
- Run DFS algorithm to detect cycles
- Identify: Direct self-reference | Two-node cycle | Multi-node cycle

**IF CYCLES FOUND:**
- Check for intentional cycle annotation in frontmatter
- IF NOT marked intentional → BLOCKING ERROR
- Display cycle chain: A → B → C → A

#### 3.5 Display Reference Results

```
REFERENCE VALIDATION RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
References Checked: {count}
✅ Valid: {valid_count}
⚠️  Warnings: {warning_count}
❌ Invalid: {invalid_count}

{IF invalid_count > 0}
INVALID REFERENCES (BLOCKING):

File: {filename} (Line {line_number})
Reference: {raw_reference}
Resolved To: {resolved_path}
Error: File not found
Suggestion: {did_you_mean}

{repeat for each invalid reference}
{END IF}

{IF cycles detected}
CIRCULAR REFERENCE DETECTED (BLOCKING):

Cycle: {file1} → {file2} → {file3} → {file1}

This creates a circular dependency that could cause infinite loops.

Options:
[M] MODIFY - Break the cycle by changing reference
[I] INTENTIONAL - Mark as intentional (e.g., workflow loop)
[C] CANCEL - Abort this edit
{END IF}
```

**IF BLOCKING ERRORS EXIST:**
- HALT immediately
- Do NOT proceed to Phase 3 until resolved

### 4. PHASE 3: COMPLIANCE VALIDATION (OPTIONAL)

**Purpose:** Check adherence to BMAD standards and best practices (ADVISORY ONLY).

Ask user: "Would you like to run BMAD compliance checks? These are advisory and won't block saving. [Y/N]"

**IF USER selects N:**
- Skip Phase 3
- Proceed to results summary

**IF USER selects Y:**

#### 4.1 Load Compliance Rules

Read {validationRulesData} for:
- Agent template compliance rules
- Workflow template compliance rules
- Naming conventions
- Style guidelines
- Documentation standards

#### 4.2 Run Compliance Checks

For EACH edited file, check:

| Category | Check | Severity |
|----------|-------|----------|
| TEMPLATE | Follows agent/workflow template structure | MAJOR |
| TEMPLATE | All recommended sections present | MAJOR |
| STYLE | Role description follows partnership format | MINOR |
| STYLE | Menu patterns follow [A] [P] [C] standard | MINOR |
| STYLE | Consistent heading hierarchy | MINOR |
| NAMING | File names follow kebab-case | MINOR |
| NAMING | Variable names follow snake_case | MINOR |
| DOCS | Description fields meaningful (>10 chars) | MINOR |
| SIZE | Step files ≤10KB (optimal ≤5KB) | MINOR |

#### 4.3 Calculate Compliance Score

```
Compliance Score = (Checks Passed / Total Checks) × 100
```

#### 4.4 Display Compliance Results

```
COMPLIANCE VALIDATION RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Score: {score}% {IF score >= 90}🎉{ELIF score >= 70}✅{ELSE}⚠️{END}

Files Checked: {count}
Major Issues: {major_count}
Minor Issues: {minor_count}

{IF major_count > 0}
MAJOR ISSUES (Recommended to fix):

File: {filename}
Issue: Missing 'capabilities' section (template requirement)
Suggestion: Add ## Capabilities section after persona

{repeat for major issues}
{END IF}

{IF minor_count > 0}
MINOR ISSUES (Optional improvements):

File: {filename}
Issue: File is {size}KB, optimal is ≤5KB
Suggestion: Consider splitting into focused sections

{repeat for minor issues}
{END IF}

Error Code for compliance issues: E006 (advisory)
```

### 5. Aggregate Validation Results

Combine all phases:

```
╔══════════════════════════════════════════════════╗
║       VALIDATION SUMMARY - Session {sessionId}   ║
╚══════════════════════════════════════════════════╝

PHASE 1 - SYNTAX: {PASS|FAIL}
  ├─ Files Checked: {count}
  ├─ Errors: {error_count}
  └─ Status: {IF errors > 0}❌ BLOCKING{ELSE}✅ PASSED{END}

PHASE 2 - REFERENCES: {PASS|FAIL}
  ├─ References Checked: {count}
  ├─ Invalid: {invalid_count}
  ├─ Circular Dependencies: {cycle_count}
  └─ Status: {IF invalid > 0 OR cycles > 0}❌ BLOCKING{ELSE}✅ PASSED{END}

PHASE 3 - COMPLIANCE: {PASS|PARTIAL|FAIL|SKIPPED}
  ├─ Compliance Score: {score}%
  ├─ Major Issues: {major_count}
  ├─ Minor Issues: {minor_count}
  └─ Status: {IF score >= 90}✅ EXCELLENT{ELIF score >= 70}✓ GOOD{ELSE}⚠️  NEEDS WORK{END}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERALL: {IF blocking_errors > 0}❌ CANNOT PROCEED{ELSE}✅ READY{END}

{IF blocking_errors > 0}
⚠️  {blocking_errors} blocking error(s) must be fixed before continuing.
{ELSE}
✅ All validation checks passed! Your edits are technically sound.
{IF compliance_score < 70}
⚠️  Note: Compliance score is below 70%. Consider addressing issues.
{END}
{END}
```

### 6. Save Validation Results to Output Document

Append validation results to {outputFile} using {validationTemplate}.

Update frontmatter in {outputFile}:
```yaml
lastValidationRun: "{timestamp}"
lastValidationStatus: "{PASS|FAIL}"
validationBlockingErrors: {count}
complianceScore: {score}
```

### 7. Auto-Trigger Logic

#### 7.1 Auto-Trigger Party Mode

**IF** blocking_errors > 3 **OR** major_issues > 5:

Display:
```
⚠️  Significant issues detected ({count} problems).

I recommend consulting other BMAD agents via Party Mode
to get diverse perspectives on these issues.

Auto-triggering Party Mode in 5 seconds...
[S] Skip Party Mode and handle manually
```

Wait 5 seconds, IF user doesn't press S:
- Execute {partyModeWorkflow}
- After Party Mode completes, return to this step's menu

#### 7.2 Auto-Trigger Advanced Elicitation

**IF** compliance_score < 70 **AND** user ran compliance check:

Display:
```
⚠️  Compliance score is {score}% (below recommended 70%).

I recommend using Advanced Elicitation to explore
alternative approaches that might improve compliance.

Would you like to run Advanced Elicitation? [Y/N]
```

IF Y:
- Execute {advancedElicitationTask}
- After completion, return to this step's menu

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
- IF C:
  - **CHECK:** IF blocking_errors > 0 → Display "Cannot continue with blocking errors. Please fix them first." → [Redisplay Menu Options](#8-present-menu-options)
  - **IF NO blocking errors:** Save validation results to {outputFile}, update frontmatter `stepsCompleted` to add 5 at the end of the array, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#8-present-menu-options)

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN C is selected AND no blocking errors exist AND content is saved to document AND frontmatter is updated, will you then load, read entire file, then execute {nextStepFile} to execute and begin iteration decision step.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All three validation phases executed completely
- Validation results clearly displayed with severity levels
- Blocking errors identified and prevented continuation
- Compliance score calculated if requested
- Results appended to {outputFile}
- {outputFile} frontmatter updated with validation status
- Menu presented and user input handled correctly
- Only proceeded to next step when blocking errors = 0

### ❌ SYSTEM FAILURE:

- Skipping any validation phase
- Proceeding to next step with blocking errors present
- Not distinguishing between blocking vs advisory issues
- Auto-fixing issues without user approval
- Not updating document frontmatter
- Proceeding without user 'C' selection
- Not running auto-trigger logic when conditions met

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
