---
name: 'step-06-iterate'
description: 'Decision point to continue editing or complete the session'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-06-iterate.md'
nextStepSelect: '{workflow_path}/steps/step-03-select.md'
nextStepComplete: '{workflow_path}/steps/step-07-complete.md'
nextStepValidate: '{workflow_path}/steps/step-05-validate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'
---

# Step 6: Iteration Decision

## STEP GOAL:

To provide a clear decision point where the user can choose to make additional edits to the module or complete the editing session, ensuring all desired changes are made before finalization.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER assume user is done - always ask explicitly
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist guiding the editing workflow
- ✅ If you already have been given a name, communication_style and identity, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring workflow navigation expertise, user brings edit intent
- ✅ Maintain strategic, holistic, systems-thinking communication style

### Step-Specific Rules:

- 🎯 Focus ONLY on iteration decision - do NOT make new edits here
- 🚫 FORBIDDEN to proceed without explicit user choice
- 💬 Approach: Present clear options, respect user's decision
- 📋 Track iteration count to show progress

## EXECUTION PROTOCOLS:

- 🎯 Display current session summary clearly
- 💾 Update frontmatter with iteration count and routing decision
- 📖 Route to correct next step based on user choice
- 🚫 FORBIDDEN to complete session without user confirmation

## CONTEXT BOUNDARIES:

- Available context: All edits made so far (from outputFile)
- Focus: Facilitate user decision about continuing or completing
- Limits: Do not create new edits, only route to next step
- Dependencies: Requires validation to have passed (step-05)

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Session Context

Read from {outputFile} frontmatter:
- `editsPerformed`: List of all edits made
- `iterationCount`: Number of times looped back to edit selection (default 0)
- `lastValidationStatus`: Status of last validation run
- `validationBlockingErrors`: Count of blocking errors from last validation
- `module_name`: Name of module being edited

### 2. Display Session Summary

Present clear summary of work done so far:

```
╔══════════════════════════════════════════════════╗
║       EDIT SESSION SUMMARY - {module_name}       ║
╚══════════════════════════════════════════════════╝

Session ID: {sessionId}
Started: {session_start_timestamp}
Duration: {calculated_duration}

EDITS COMPLETED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{FOR EACH edit in editsPerformed}
{edit_number}. [{edit.action}] {edit.type}: {edit.target}
   └─ {edit.timestamp} - {edit.reason}
{END FOR}

Total Edits: {editsPerformed.length}
Iterations: {iterationCount}

VALIDATION STATUS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Last Run: {lastValidationRun}
Status: {IF lastValidationStatus == "PASS"}✅ PASSED{ELSE}❌ ISSUES FOUND{END}
Blocking Errors: {validationBlockingErrors}
{IF complianceScore exists}
Compliance Score: {complianceScore}%
{END}
```

### 3. Check for Blocking Issues

**IF** validationBlockingErrors > 0:

Display:
```
⚠️  WARNING: Blocking validation errors exist!

You have {validationBlockingErrors} error(s) that must be fixed
before completing this session.

Your options:
[E] Edit to fix errors - Return to edit menu
[V] Run validation again - Re-check after manual fixes
[R] Review errors - Show validation results again
[A] Abort session - Cancel all edits (not recommended)

These errors MUST be resolved to complete the session.
```

Handle user choice:
- **IF E:** Route to {nextStepSelect} (select edits)
- **IF V:** Route to {nextStepValidate} (re-run validation)
- **IF R:** Display validation results from outputFile, then redisplay this menu
- **IF A:** Confirm abandonment, then offer rollback

HALT - Do NOT proceed to main iteration menu until blocking errors = 0

### 4. Increment Iteration Counter

Update {outputFile} frontmatter:
```yaml
iterationCount: {iterationCount + 1}
```

### 5. Present Iteration Decision

**IF NO blocking errors exist:**

Display the iteration decision prompt:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You've successfully completed {editsPerformed.length} edit(s)
and all validation checks have passed.

What would you like to do next?
```

### 6. Present MENU OPTIONS

Display:

```
**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue

[Y] MORE EDITS - I have additional changes to make
[V] VALIDATE FIRST - Run full validation before deciding
[N] COMPLETE SESSION - I'm done editing, finalize this session
[A] ADVANCED ELICITATION - Use deep-dive questioning techniques
[P] PARTY MODE - Engage multi-agent discussion for complex decisions

{IF iterationCount > 5}
Note: You've iterated {iterationCount} times. Consider completing
the session and starting a new one for additional changes.
{END}
```

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting options
- ONLY proceed when user makes a clear choice
- Track the choice in session for audit trail
- Route to appropriate next step

#### Decision Handling Logic:

**IF Y (More Edits):**
- Display: "Returning to edit selection menu..."
- Update {outputFile} frontmatter:
  ```yaml
  lastStep: "step-06-iterate"
  lastStepIndex: 6
  stepsCompleted: [..., 6]  # Add 6 to array
  ```
- Route: Load, read entire file, then execute {nextStepSelect}

**IF V (Validate First):**
- Display: "Running comprehensive validation..."
- Update {outputFile} frontmatter:
  ```yaml
  lastStep: "step-06-iterate"
  lastStepIndex: 6
  stepsCompleted: [..., 6]  # Add 6 to array
  ```
- Route: Load, read entire file, then execute {nextStepValidate}
- After validation completes, return to this step (step-06-iterate)

**IF N (Complete Session):**
- Display: "Proceeding to session completion..."
- Confirm: "This will finalize your edits and clean up backups. Continue? [YES/NO]"
- **IF YES:**
  - Update {outputFile} frontmatter:
    ```yaml
    lastStep: "step-06-iterate"
    lastStepIndex: 6
    stepsCompleted: [..., 6]  # Add 6 to array
    sessionCompletionRequested: true
    completionTimestamp: "{current_timestamp}"
    ```
  - Route: Load, read entire file, then execute {nextStepComplete}
- **IF NO:**
  - Display: "Staying in iteration mode."
  - Redisplay decision options (back to step 6)

**IF A (Advanced Elicitation):**
- Display: "Entering Advanced Elicitation mode..."
- Use deep-dive questioning techniques to explore:
  - What specific aspects of the module need more consideration?
  - Are there edge cases or scenarios not yet addressed?
  - What constraints or requirements might be missing?
- After elicitation, synthesize insights and redisplay decision options
- Stay in this step until clear choice is made

**IF P (Party Mode):**
- Display: "Initiating Party Mode for multi-agent discussion..."
- Engage multiple agent perspectives to discuss:
  - Current state of the module edits
  - Potential improvements or concerns
  - Strategic recommendations for next steps
- Synthesize the discussion outcomes
- After party mode concludes, redisplay decision options
- Stay in this step until clear choice is made

**IF C (Continue):**
- Treat as equivalent to [Y] MORE EDITS
- Display: "Returning to edit selection menu..."
- Route: Load, read entire file, then execute {nextStepSelect}

**IF Any other input or questions:**
- Respond to user's questions or comments
- After response, redisplay decision options
- Stay in this step until clear choice is made

### 7. Track Routing Decision

Before loading next step, append to {outputFile} in appropriate section:

```markdown
### Iteration Decision #{iterationCount}

**Timestamp:** {current_timestamp}
**Decision:** {Y|V|N}
**Route:** {step-03-select|step-05-validate|step-07-complete}
**Rationale:** {user's stated reason if provided}
```

### 8. Audit Trail Update

Update {outputFile} frontmatter with routing information:

```yaml
# Iteration History
iterationHistory:
  - iteration: {iterationCount}
    timestamp: "{timestamp}"
    decision: "{Y|V|N}"
    route: "{next_step_name}"
```

## CRITICAL STEP COMPLETION NOTE

This step completes when user makes a clear choice (Y, V, or N) and you route to the appropriate next step:

- **Choice Y (More Edits):** Update frontmatter with step 6 completion, then load, read entire file, then execute {nextStepSelect} to return to edit selection menu
- **Choice V (Validate):** Update frontmatter with step 6 completion, then load, read entire file, then execute {nextStepValidate} to re-run validation
- **Choice N (Complete):** Update frontmatter with step 6 completion, confirm with user, then load, read entire file, then execute {nextStepComplete} to finalize session

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Session summary displayed clearly with all edits listed
- Iteration count tracked and incremented
- Blocking errors checked before presenting main decision
- User presented with clear, unambiguous options
- User choice respected and routed correctly
- {outputFile} frontmatter updated with iteration info
- Routing decision tracked in audit trail
- Next step loaded only after explicit user choice

### ❌ SYSTEM FAILURE:

- Assuming user is done without asking
- Proceeding with blocking validation errors present
- Not displaying session summary before decision
- Auto-routing without user choice
- Not updating iteration counter
- Not tracking routing decision in output document
- Skipping confirmation for session completion
- Loading next step before frontmatter update

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
