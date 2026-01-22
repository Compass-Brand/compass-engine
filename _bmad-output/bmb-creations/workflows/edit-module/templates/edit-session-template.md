---
# Edit Session Frontmatter (STRICT - all fields required)
sessionId: "{sessionId}"
modulePath: "{modulePath}"
moduleName: "{moduleName}"
startedAt: "{startedAt}"
lastUpdated: "{lastUpdated}"
status: "in_progress"
stepsCompleted: []
currentStep: 1
user: "{user_name}"
backupTransactionId: null
---

# Edit Session: {moduleName}

## Session Summary

| Field | Value |
|-------|-------|
| Started | {startedAt} |
| Module | {modulePath} |
| Status | In Progress |
| Session ID | {sessionId} |

---

## Module Structure

<!-- Populated by step-02-analyze.md -->

### Components Discovered

| Type | Count | Components |
|------|-------|------------|
| Agents | 0 | - |
| Workflows | 0 | - |
| Config Files | 0 | - |
| Documentation | 0 | - |

---

## Edits Performed

<!-- Appended as edits occur in step-04 series -->

<!-- Template for each edit entry:
### Edit {n}: {component_type} - {component_name}

- **Time:** {timestamp}
- **Action:** {edit_type} (modify|add|remove)
- **Files Changed:**
  - `{file_path}`
- **Changes Made:**
  - {description of change}
- **Validation:** {pass|fail|pending}
- **Backup ID:** {backup_transaction_id}
-->

---

## Validation Results

<!-- Appended after validation runs in step-05 -->

### Pre-Edit Validation

| Check | Status | Details |
|-------|--------|---------|
| Module exists | - | - |
| Valid structure | - | - |
| Git status | - | - |

### Post-Edit Validation

| Check | Status | Details |
|-------|--------|---------|
| YAML syntax | - | - |
| Markdown syntax | - | - |
| BMAD compliance | - | - |
| Cross-references | - | - |

---

## Backup Status

| Field | Value |
|-------|-------|
| Backup Location | `{modulePath}/.backup/{timestamp}/` |
| Transaction ID | {backupTransactionId} |
| Files Backed Up | 0 |
| All Verified | - |

---

## Session Notes

<!-- Free-form user notes - add any context or reminders here -->
