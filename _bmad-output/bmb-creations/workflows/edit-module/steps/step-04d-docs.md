---
name: 'step-04d-docs'
description: 'Edit module documentation files (README.md and other markdown) through focused section-based editing with validation'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04d-docs.md'
nextStepFile: '{workflow_path}/steps/step-05-validate.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Template References
docsEditTemplate: '{workflow_path}/templates/docs-edit-section.md'
---

# Step 04d: Module Documentation Editing

## STEP GOAL:

To edit module documentation files (README.md and other markdown) through focused section-based editing that enables precise content updates while maintaining markdown validity and document structure integrity.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist with systems-thinking perspective
- ✅ If you already have been given communication or persona patterns, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring architectural expertise and structured planning
- ✅ User brings their module intent and domain knowledge
- ✅ Maintain strategic, holistic, collaborative tone throughout

### Step-Specific Rules:

- 🎯 Focus ONLY on markdown documentation files in module root
- 🚫 FORBIDDEN to modify without creating backup first
- 💬 Section-based editing for precision and clarity
- 📋 Validate markdown structure after edits
- 🔒 Use atomic swap pattern (write to .tmp, then rename)

## EXECUTION PROTOCOLS:

- 🎯 Discover all .md files in module root directory
- 💾 Create backup before ANY modification
- 📖 Update session editsPerformed array with doc changes
- 📖 Update frontmatter `stepsCompleted` to add '04d' before loading next step
- 🚫 FORBIDDEN to edit files outside module root directory

## CONTEXT BOUNDARIES:

- Module path and session state loaded from frontmatter
- Target files: README.md and any other .md files in {module_path}/ (root only)
- Focus on documentation content, not code or configuration
- Non-destructive editing (LOW severity)
- Changes require intent-based confirmation only

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Discover Documentation Files

Scan `{module_path}/` for markdown files:

- List all `*.md` files in module root (not subdirectories)
- Identify README.md as primary documentation
- Count total documentation files

### 2. Display Documentation File Structure

Present file selection menu:

```
Module Documentation: {module_name}
═══════════════════════════════════════════════════

Primary Documentation:
[1] README.md ({size} bytes, {line_count} lines)

Additional Documentation:
[2] CHANGELOG.md ({size} bytes, {line_count} lines)
[3] CONTRIBUTING.md ({size} bytes, {line_count} lines)
... {list any other .md files}

[X] Cancel (return to main menu)

Select file to edit (1-{n}, X):
```

### 3. Parse File Sections

After user selects file, parse markdown structure:

- Identify all heading levels (# H1, ## H2, ### H3, etc.)
- Create section map with line ranges
- Display section outline

**Section Outline Display:**
```
Editing: {selected_file}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Document Structure:

[1] # {H1 Heading} (lines 1-45)
    [1.1] ## {H2 Heading} (lines 5-20)
    [1.2] ## {H2 Heading} (lines 21-45)
[2] # {H1 Heading} (lines 46-120)
    [2.1] ## {H2 Heading} (lines 50-80)
    [2.2] ## {H2 Heading} (lines 81-120)
[3] # {H1 Heading} (lines 121-EOF)

Options:
[S] Select section to edit
[F] Full file edit
[B] Back to file selection

Choose action:
```

### 4. Section-Based Editing

If user selects section editing:

**Display Current Section:**
```
Section: {section_heading}
Lines: {start_line}-{end_line}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current content:
───────────────────────────────────────
{display section content}
───────────────────────────────────────

Options:
[E] Edit this section
[R] Replace entire section
[A] Add content after this section
[D] Delete this section
[B] Back to section menu

Choose action:
```

#### Edit Actions:

**[E] Edit Section:**
- Display current content for reference
- Accept new content from user
- Preserve section heading unless explicitly changed
- Show before/after diff

**[R] Replace Section:**
- Warn that heading and all content will be replaced
- Accept complete replacement markdown
- Validate markdown structure

**[A] Add After:**
- Accept new markdown content
- Insert after current section
- Useful for adding new subsections

**[D] Delete Section:**
- Display warning with section preview
- Require confirmation: "Type 'DELETE' to confirm"
- Remove section entirely

### 5. Full File Editing

If user selects full file edit:

```
⚠️  Full File Edit Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are editing the entire file. Preserve structure carefully.

Current file ({line_count} lines):
───────────────────────────────────────
{display first 50 lines with ... truncation if longer}
───────────────────────────────────────

Provide complete file content (or 'cancel' to abort):
```

Accept full file replacement with validation.

### 6. Content Preview and Confirmation

Before applying any changes, show preview:

```
Preview of Changes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: {filename}
Section: {section_heading} (if section edit)

BEFORE:
───────────────────────────────────────
{old_content}
───────────────────────────────────────

AFTER:
───────────────────────────────────────
{new_content}
───────────────────────────────────────

Apply these changes? (y/N):
```

### 7. Backup and Atomic Write

Before writing changes:

**Backup Process:**
```
Creating backup: {filename}.backup-{timestamp}
Validating markdown structure...
Writing changes to {filename}.tmp...
Verifying written content...
Atomic swap: {filename}.tmp → {filename}
✓ Documentation updated successfully
```

**Backup Failure Handling:**
```
❌ ERROR: Cannot create backup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reason: {error_message}

Changes NOT applied. File remains unchanged.
```

### 8. Basic Markdown Validation

After user provides new content but BEFORE writing:

```
Validating markdown structure...
```

**Validation Checks:**
- Heading hierarchy (no skipped levels)
- Balanced code fences (```)
- Balanced brackets in links
- Valid link syntax
- List formatting consistency

If validation finds issues:
```
⚠️  Markdown Structure Issues
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{list issues found}

These are warnings, not blockers.
Proceed anyway? (y/N):
```

If validation succeeds:
```
✓ Markdown structure valid
```

### 9. Update Session Document

Append to {outputFile} in Edit Log section:

```markdown
### Edit #{n}: Documentation - {filename}

**Action:** modify
**Timestamp:** {timestamp}
**Section:** {section_heading or "Full file"}
**Reason:** {user_stated_reason}

#### Changes Made

{brief description of changes}

**Backup:** {filename}.backup-{timestamp}
**Validation:** Markdown structure valid ✓
```

Update frontmatter:
```yaml
editsPerformed:
  - type: docs
    target: {filename}
    section: {section_heading}
    backup: {filename}.backup-{timestamp}
    timestamp: {timestamp}
```

### 10. Multiple Edits Loop

After completing one edit:

```
Documentation edit completed.

Options:
[E] Edit another file/section
[D] Done with documentation

Choose action:
```

Allow user to make multiple documentation edits before proceeding to validation.

### 11. Present MENU OPTIONS

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
- IF C: Update frontmatter stepsCompleted with '04d', then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#11-present-menu-options)

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN C is selected, all documentation changes are written, backups are created, session document is updated, and frontmatter is updated with '04d' completion, will you then load, read entire file, then execute `{workflow_path}/steps/step-05-validate.md` to execute validation of all changes.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All .md files in module root discovered
- File structure displayed clearly
- Section-based editing enabled for precision
- Full file editing available as option
- Content preview shown before applying
- Backup created before modification
- Markdown structure validated
- Atomic swap pattern used for write operation
- Session document updated with edit details
- Multiple edits supported in same session
- Frontmatter updated with step completion
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Modifying files without backup
- Accepting malformed markdown without warning
- Not showing preview before applying changes
- Writing partial changes (not atomic)
- Editing files outside module root
- Not updating session editsPerformed array
- Generating documentation content without user input
- Proceeding to validation without completing writes

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
