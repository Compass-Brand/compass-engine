---
name: 'step-07-complete'
description: 'Finalize editing session with backup cleanup, changelog generation, and optional git commit'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References (no nextStepFile - this is the final step)
thisStepFile: '{workflow_path}/steps/step-07-complete.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Template References
changelogTemplate: '{workflow_path}/templates/changelog.template.md'
---

# Step 7: Session Completion

## STEP GOAL:

To safely finalize the editing session by verifying all changes, cleaning up backups, generating a changelog, optionally committing to version control, and providing a comprehensive session summary.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER delete backups before final verification
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: This is the FINAL step - no next step to load
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist completing the editing workflow
- ✅ If you already have been given a name, communication_style and identity, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring workflow completion expertise, user brings satisfaction confirmation
- ✅ Maintain strategic, holistic, systems-thinking communication style

### Step-Specific Rules:

- 🎯 Focus on safe, verified completion with proper cleanup
- 🚫 FORBIDDEN to delete backups before all verifications pass
- 💬 Approach: Methodical verification, clear confirmation, comprehensive summary
- 📋 Mark session as completed only after ALL steps succeed

## EXECUTION PROTOCOLS:

- 🎯 Verify all edits passed validation before cleanup
- 💾 Generate and update CHANGELOG.md in module directory
- 📖 Offer git integration if available
- 🚫 FORBIDDEN to proceed with unresolved validation errors
- ✅ Mark session as completed in frontmatter

## CONTEXT BOUNDARIES:

- Available context: Entire session history from {outputFile}
- Focus: Safe completion, cleanup, documentation
- Limits: No new edits allowed in this step
- Dependencies: Validation must have passed (step-05)

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Complete Session Context

Read from {outputFile} frontmatter and body:
- `sessionId`: Unique session identifier
- `module_name`: Name of module edited
- `modulePath`: Full path to module directory
- `editsPerformed`: Complete list of all edits
- `lastValidationStatus`: Final validation status
- `validationBlockingErrors`: Count of blocking errors
- `complianceScore`: Compliance score if run
- `sessionStartTime`: When session started
- `backupsCreated`: List of backup locations

### 2. Pre-Completion Verification

Run comprehensive pre-flight checks:

#### 2.1 Validation Status Check

Display:
```
╔══════════════════════════════════════════════════╗
║         SESSION COMPLETION - VERIFICATION        ║
╚══════════════════════════════════════════════════╝

Running pre-completion checks...
```

**CHECK 1: Validation Status**
```
[1/4] Checking validation status...
```

**IF** lastValidationStatus != "PASS" **OR** validationBlockingErrors > 0:

Display:
```
❌ VERIFICATION FAILED

Validation has not passed or blocking errors exist:
- Validation Status: {lastValidationStatus}
- Blocking Errors: {validationBlockingErrors}

You CANNOT complete the session with unresolved validation errors.

Options:
[B] Go Back - Return to iteration menu to fix issues
[F] Force Review - Show me the validation errors again
[A] Abort Completion - Cancel completion, keep session open

Session completion halted.
```

Handle choice and route accordingly.
HALT - Do NOT proceed past this point if validation failed.

**IF** validation PASSED:
```
✅ Validation: PASSED
```

#### 2.2 All Edits Confirmed

**CHECK 2: Edit Confirmation**
```
[2/4] Verifying all edits are finalized...
```

Scan `editsPerformed` for any marked as "in_progress" or "pending":

**IF** any edits incomplete:
```
❌ VERIFICATION FAILED

{count} edit(s) appear incomplete:
{list incomplete edits}

Please complete or cancel these edits before finishing session.
```
HALT

**IF** all edits complete:
```
✅ All Edits: FINALIZED ({editsPerformed.length} total)
```

#### 2.3 Backup Integrity Verification

**CHECK 3: Backup Verification**
```
[3/4] Verifying backup integrity before cleanup...
```

For EACH backup in `backupsCreated`:
- Verify backup files still exist at backup location
- Verify backup manifest matches expected state
- Verify no corruption in backup files

**IF** any backup corrupted or missing:
```
❌ VERIFICATION FAILED - CRITICAL

Backup integrity check failed:
{list issues}

⚠️  DO NOT PROCEED - Backups may be needed for recovery.

Options:
[I] Investigate - Show detailed backup status
[P] Preserve - Keep backups and complete anyway
[A] Abort - Cancel completion

Recommendation: Choose [P] to preserve backups.
```

**IF** all backups verified:
```
✅ Backups: VERIFIED ({backupsCreated.length} files)
```

#### 2.4 File System Permissions Check

**CHECK 4: Permissions**
```
[4/4] Checking file system permissions...
```

Verify write permissions for:
- Module CHANGELOG.md (will be created/updated)
- Backup directory (for cleanup)
- Module directory (if git integration used)

**IF** permission denied (Error Code: **E008**):
```
❌ VERIFICATION FAILED - E008

Insufficient permissions to:
{list permission issues}

You need write access to complete this session.

Options:
[R] Retry - Check permissions again
[M] Manual - I'll handle these manually
[A] Abort - Cancel completion

Error Code: E008 (Permission Denied)
```

**IF** all permissions OK:
```
✅ Permissions: OK
```

#### 2.5 Display Verification Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRE-COMPLETION VERIFICATION: ✅ ALL CHECKS PASSED

Ready to proceed with:
1. Backup cleanup
2. Changelog generation
3. Optional git commit
4. Session finalization

Proceeding...
```

### 3. Backup Cleanup Protocol

**CRITICAL: Only execute after ALL verifications pass**

#### 3.1 Display Cleanup Plan

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BACKUP CLEANUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backups to clean up:
{FOR EACH backup in backupsCreated}
- {backup.path} ({backup.size})
{END FOR}

These backups will be permanently deleted after validation
has passed and session is finalized.

Total space to reclaim: {total_backup_size}
```

#### 3.2 Update Backup Manifest

Update `.backup/manifest.json` in module directory:
```json
{
  "status": "validated",
  "validatedAt": "{current_timestamp}",
  "sessionId": "{sessionId}",
  "safeToDelete": true
}
```

#### 3.3 Delete Backup Files

For EACH backup directory in `backupsCreated`:

```
Cleaning up: {backup_path}
```

- Delete backup files
- Delete backup directory
- Update manifest: `status: "deleted"`, `deletedAt: "{timestamp}"`
- Keep manifest.json as audit trail (will be purged after 30 days)

**IF** deletion fails:
```
⚠️  Warning: Could not delete backup at {path}

This is non-critical. You can manually delete later.
Continuing with session completion...
```

**IF** deletion succeeds:
```
✅ Backups cleaned up successfully
```

### 4. Changelog Generation

Generate or update module CHANGELOG.md using Keep-a-Changelog format.

#### 4.1 Check for Existing Changelog

**IF** `{modulePath}/CHANGELOG.md` exists:
- Read current changelog
- Determine next version (or use "Unreleased")
- Prepare new entry

**IF** `{modulePath}/CHANGELOG.md` does NOT exist:
- Create new changelog from {changelogTemplate}
- Initialize with header and first entry

#### 4.2 Generate Changelog Entry

Create entry following Keep-a-Changelog format:

```markdown
## [Unreleased] - {current_date}

### Changed
{FOR EACH edit in editsPerformed WHERE edit.action == "modify"}
- {edit.type}: {edit.target} - {edit.reason}
{END FOR}

### Added
{FOR EACH edit in editsPerformed WHERE edit.action == "add"}
- {edit.type}: {edit.target} - {edit.reason}
{END FOR}

### Removed
{FOR EACH edit in editsPerformed WHERE edit.action == "remove"}
- {edit.type}: {edit.target} - {edit.reason}
{END FOR}

### Fixed
{FOR EACH edit in editsPerformed WHERE edit.action == "fix"}
- {edit.type}: {edit.target} - {edit.reason}
{END FOR}

**Session ID:** {sessionId}
**Edits:** {editsPerformed.length}
**Validation:** {lastValidationStatus}
{IF complianceScore}**Compliance:** {complianceScore}%{END}
```

#### 4.3 Write Changelog

**IF** changelog is new:
- Write complete file to `{modulePath}/CHANGELOG.md`

**IF** changelog exists:
- Insert new entry at top (after header, before previous entries)
- Preserve all existing entries

**IF** write fails (Error Code: **E008**):
```
❌ Error E008: Could not write CHANGELOG.md

Permission denied: {modulePath}/CHANGELOG.md

Options:
[R] Retry with sudo/admin
[M] Manual - I'll create it manually
[S] Skip - Continue without changelog

Recommendation: Choose [R] or [M]
```

**IF** write succeeds:
```
✅ CHANGELOG.md updated: {modulePath}/CHANGELOG.md
```

### 5. Git Integration (Optional)

Check if git is available and module is in a git repository:

```
Checking for git integration...
```

**IF** git available AND module is in git repo:

#### 5.1 Check Git Status

Run: `git status` in {modulePath}

**IF** uncommitted changes detected:

Display:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GIT INTEGRATION AVAILABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Modified files from this session:
{list modified files}

Would you like to create a git commit for these changes?

[Y] Yes - Commit with auto-generated message
[C] Custom - Commit with custom message
[N] No - I'll commit manually later
```

#### 5.2 Handle Git Commit Choice

**IF Y (Auto-generated message):**

Generate commit message:
```
Edit module {module_name} - {editsPerformed.length} changes

Session: {sessionId}
Date: {current_date}

Changes:
{FOR EACH edit in editsPerformed}
- [{edit.action}] {edit.type}: {edit.target}
{END FOR}

Validation: {lastValidationStatus}
{IF complianceScore}Compliance: {complianceScore}%{END}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

Execute:
```bash
cd {modulePath}
git add .
git commit -m "{generated_message}"
```

**IF** commit fails (Error Code: **E009**):
```
❌ Error E009: Git commit failed

{error_message}

The changes are saved but not committed to git.
You can commit manually later.

Continuing with session completion...
```

**IF** commit succeeds:
```
✅ Git commit created: {commit_hash}
```

**IF C (Custom message):**

Prompt: "Enter your commit message (or 'cancel'):"

Wait for user input.

**IF** user provides message:
- Execute: `git add . && git commit -m "{user_message}"`
- Handle errors same as auto-commit

**IF N (Skip git):**
```
⏭️  Skipping git commit - you can commit manually later
```

**IF** git NOT available:
```
⏭️  Git integration not available
```

### 6. Session Finalization

#### 6.1 Calculate Session Metrics

```
Calculating session metrics...
```

Compute:
- Total session duration: `{current_timestamp} - {sessionStartTime}`
- Total edits: `{editsPerformed.length}`
- Edit types breakdown: Added, Modified, Removed, Fixed
- Average time per edit
- Validation runs: Count from outputFile
- Iterations: `{iterationCount}`

#### 6.2 Update Output Document Frontmatter

Update {outputFile} frontmatter with completion data:

```yaml
# Session Status
sessionStatus: "completed"
completedAt: "{current_timestamp}"
sessionDuration: "{calculated_duration}"

# Final Metrics
totalEdits: {editsPerformed.length}
finalValidationStatus: "{lastValidationStatus}"
finalComplianceScore: {complianceScore}
backupsCleanedUp: true
changelogUpdated: true
gitCommitCreated: {true|false}
gitCommitHash: "{hash}" # if created

# Completion Step
stepsCompleted: [..., 7]
lastStep: "step-07-complete"
lastStepIndex: 7
```

#### 6.3 Append Final Summary to Output Document

Add final section to {outputFile}:

```markdown
---

## SESSION COMPLETED

**Completion Time:** {current_timestamp}
**Total Duration:** {session_duration}

### Final Statistics

- **Total Edits:** {editsPerformed.length}
  - Added: {added_count}
  - Modified: {modified_count}
  - Removed: {removed_count}
  - Fixed: {fixed_count}

- **Quality Metrics:**
  - Final Validation: {lastValidationStatus}
  - Compliance Score: {complianceScore}%
  - Iterations: {iterationCount}

- **Deliverables:**
  - ✅ All edits applied and validated
  - ✅ Backups cleaned up
  - ✅ CHANGELOG.md updated
  - {IF gitCommitCreated}✅ Git commit created ({gitCommitHash}){ELSE}⏭️ Git commit skipped{END}

### Session Summary

This editing session successfully completed {editsPerformed.length} change(s)
to module **{module_name}**. All validation checks passed and changes have
been documented in the module's CHANGELOG.

**Session Reference:** {sessionId}
**Output Document:** {outputFile}

---

Thank you for using the edit-module workflow!
```

### 7. Display Final Success Message

Present comprehensive completion message:

```
╔══════════════════════════════════════════════════╗
║              SESSION COMPLETED!                   ║
╚══════════════════════════════════════════════════╝

Module: {module_name}
Session: {sessionId}
Duration: {session_duration}

✅ COMPLETION SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ {editsPerformed.length} edit(s) applied and validated
✓ Validation: {lastValidationStatus}
{IF complianceScore}✓ Compliance: {complianceScore}%{END}
✓ Backups cleaned up successfully
✓ CHANGELOG.md updated
{IF gitCommitCreated}✓ Git commit created: {gitCommitHash}{END}
✓ Session documented: {outputFile}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHANGES MADE:
{FOR EACH edit in editsPerformed}
{index}. [{edit.action}] {edit.type}: {edit.target}
{END FOR}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your module has been successfully updated and all changes
are documented. The editing session is now complete.

{IF gitCommitCreated}
Next steps:
- Review the commit: git show {gitCommitHash}
- Push changes: git push origin {current_branch}
{ELSE}
Next steps:
- Review changes: git status
- Commit manually: git add . && git commit
{END}

Session reference for your records: {sessionId}
Full session log: {outputFile}

Thank you for using edit-module workflow!
```

### 8. Final Cleanup and Shutdown

- Close any open file handles
- Clear session-specific temporary data
- Mark workflow as completed
- End workflow execution gracefully

**DO NOT** load any next step - this is the FINAL step.

## CRITICAL STEP COMPLETION NOTE

This is the FINAL step of the edit-module workflow. After displaying the completion message and updating all documents:

1. Verify {outputFile} frontmatter marked `sessionStatus: "completed"`
2. Verify CHANGELOG.md updated
3. Verify backups cleaned up (or gracefully handled if failed)
4. Display final success message
5. End workflow session - DO NOT load any next step

The workflow is now complete.

---

## SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All pre-completion verifications passed
- Validation status confirmed as PASSED
- All edits confirmed as finalized
- Backup integrity verified before cleanup
- Permissions checked successfully
- Backups cleaned up (or failure gracefully handled)
- CHANGELOG.md successfully generated/updated
- Git integration offered and handled appropriately
- Session metrics calculated accurately
- {outputFile} frontmatter updated with completion status
- Final summary appended to output document
- Comprehensive completion message displayed
- Session marked as completed
- Workflow ended gracefully

### ❌ SYSTEM FAILURE:

- Proceeding with unresolved validation errors
- Deleting backups before verification complete
- Not verifying backup integrity before cleanup
- Creating changelog without proper format
- Auto-committing to git without user approval
- Not handling git failures gracefully
- Not calculating session metrics
- Not updating frontmatter with completion status
- Not displaying final success message
- Attempting to load a next step (this is final)
- Not documenting all changes in CHANGELOG
- Incomplete session summary

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
