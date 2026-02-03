---
name: audit-docs
description: Interactive workflow for reviewing and updating README.md and CLAUDE.md files across Compass Brand projects
---

# Audit Documentation

Interactive workflow for reviewing and updating README.md and CLAUDE.md files across Compass Brand projects.

## Step 1: Confirm Audit Scope

Use AskUserQuestion to determine scope:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "What documentation would you like to audit?",
      "header": "Scope",
      "options": [
        {"label": "All projects (Recommended)", "description": "Audit all README.md and CLAUDE.md files"},
        {"label": "Current project only", "description": "Just audit this project's documentation"},
        {"label": "Specific project", "description": "I'll specify which project to audit"}
      ],
      "multiSelect": false
    },
    {
      "question": "How thorough should the audit be?",
      "header": "Depth",
      "options": [
        {"label": "Quick check", "description": "Staleness and obvious issues only"},
        {"label": "Standard (Recommended)", "description": "Staleness, broken refs, version mismatches"},
        {"label": "Deep audit", "description": "Also check command examples and cross-references"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 2: Run Audit Script

Run the standalone script to gather issues:

```powershell
# PowerShell (Windows)
.\scripts\audit-docs.ps1                          # All projects, 30-day stale threshold
.\scripts\audit-docs.ps1 -StaleDays 14            # More aggressive staleness check
.\scripts\audit-docs.ps1 -JsonOutput              # Machine-readable output
.\scripts\audit-docs.ps1 -ProjectDir ".\my_proj"  # Specific project
```

```bash
# Bash (Linux/Mac)
./scripts/audit-docs.sh                           # All projects
./scripts/audit-docs.sh . 14                      # 14-day stale threshold
./scripts/audit-docs.sh . 30 true                 # JSON output
```

## Step 3: Query Forgetful for Context

Check for recent changes that should be documented:

```python
# First, discover the project ID for the current repo
projects = mcp__forgetful__execute_forgetful_tool("list_projects", {
  "repo_name": "Compass-Brand/compass-brand"  # Adjust for current repo
})

# Extract project_id from the response - projects contains a list with 'id' field
# Example response: {"projects": [{"id": 2, "name": "compass-brand", ...}]}
# Select the matching project:
PROJECT_ID = None
for p in projects.get("projects", []):
    if "compass-brand" in p.get("name", "").lower():
        PROJECT_ID = p["id"]
        break

# Query with project scope for better relevance
if PROJECT_ID:
    mcp__forgetful__execute_forgetful_tool("query_memory", {
      "query": "architecture changes tech stack decisions new features",
      "query_context": "Auditing documentation for recent changes that need to be reflected",
      "k": 10,
      "project_ids": [PROJECT_ID]  # Use discovered project ID
    })
else:
    # Fall back to global query if no project found
    mcp__forgetful__execute_forgetful_tool("query_memory", {
      "query": "architecture changes tech stack decisions new features",
      "query_context": "Auditing documentation for recent changes that need to be reflected",
      "k": 10
    })
```

## Step 4: Review Issues

For each issue found, present options:

### Stale Files

```json
AskUserQuestion({
  "questions": [
    {
      "question": "<file> hasn't been updated in 45 days. What should I do?",
      "header": "Stale Doc",
      "options": [
        {"label": "Review and update", "description": "I'll read the file and suggest updates"},
        {"label": "Mark as current", "description": "No changes needed, just update timestamp"},
        {"label": "Skip for now", "description": "Leave it and move to next issue"}
      ],
      "multiSelect": false
    }
  ]
})
```

### Broken References

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Found broken reference to 'src/old-file.js' in <file>. How should I fix it?",
      "header": "Broken Ref",
      "options": [
        {"label": "Remove the reference", "description": "Delete the mention of this file"},
        {"label": "Update the path", "description": "I'll find the new location"},
        {"label": "Leave a TODO", "description": "Mark it for later review"},
        {"label": "Skip", "description": "Don't change anything"}
      ],
      "multiSelect": false
    }
  ]
})
```

### Version Mismatches

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Documentation says version 1.0.0 but package.json has 2.1.0. Fix?",
      "header": "Version",
      "options": [
        {"label": "Update to current (Recommended)", "description": "Change doc to match package.json"},
        {"label": "Keep documented version", "description": "The doc version is intentional"},
        {"label": "Remove version mention", "description": "Don't track version in docs"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 5: Apply Fixes

For each approved fix:

1. Make the edit using Edit tool
2. Stage the change
3. Continue to next fix

After all fixes in a file:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "I've made N fixes to <file>. Commit now or continue to next file?",
      "header": "Commit",
      "options": [
        {"label": "Commit now", "description": "Save these changes with a commit"},
        {"label": "Continue first", "description": "Fix more files, then commit all together"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 6: Generate Audit Report

```text
Documentation Audit Report
==========================
Date: <today>

Files Reviewed
--------------
[OK] compass-brand/README.md - Last updated: <date>
[OK] compass-brand/CLAUDE.md - Last updated: <date>
[STALE] legacy-system-analyzer/README.md - Last updated: 45 days ago (FIXED)
[OK] legacy-system-analyzer/CLAUDE.md - Last updated: <date>

Issues Found & Fixed
--------------------
<file>:
  Line 23: Reference to 'src/old-file.js' - REMOVED
  Line 45: Version '1.0.0' -> '2.1.0' - UPDATED

Issues Deferred
---------------
<file>:
  Line 67: URL 'https://...' needs verification - SKIPPED

Related Memories
----------------
Recent changes that may need documentation:
- "Added BMAD-METHOD auto-sync" (Memory #X) - Now documented
- "Changed database schema" (Memory #Y) - Needs attention
```

## Step 7: Record Audit in Forgetful

```json
mcp__forgetful__execute_forgetful_tool("create_memory", {
  "title": "Documentation Audit - <date>",
  "content": "Audited X files. Found Y issues. Fixed Z issues.\n\nRemaining issues:\n- ...",
  "context": "Regular documentation maintenance audit",
  "keywords": ["documentation", "audit", "maintenance"],
  "tags": ["docs", "maintenance"],
  "importance": 6
})
```

## Standalone Usage

The script can run independently:

```powershell
# CI/CD - fail if stale docs found
$result = .\scripts\audit-docs.ps1 -JsonOutput | ConvertFrom-Json
if ($result.summary.staleFiles -gt 0) { exit 1 }

# Generate report for review
.\scripts\audit-docs.ps1 -StaleDays 7 > audit-report.txt
```

## Documentation Standards

When updating docs, follow these standards:

### README.md

- Project overview (what it does)
- Quick start (how to run it)
- Tech stack overview
- Link to CLAUDE.md for development details

### CLAUDE.md

- Detailed development guidance
- Forgetful memory integration
- Git discipline rules
- Available commands and skills
- Project-specific patterns

### CHECKLIST.md

Contributors must:

- Check `docs/CHECKLIST.md` before starting work on a project
- Update it as tasks are completed
- Ensure it reflects the current codebase state
- Include a last-updated date for tracking

The audit workflow (`audit-docs`) verifies:

- CHECKLIST.md exists in the project
- The last-updated date is recent
- Content aligns with actual project state

### Both

- Keep current with actual codebase
- Remove deprecated content promptly
- Use consistent formatting
- Include last-updated date for time-sensitive info

## Automation

For CI/CD checks:

```yaml
name: Documentation Check
on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      # Pin to commit SHA for security (v4.2.2 as of 2024-12)
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - name: Check for stale docs
        run: |
          ./scripts/audit-docs.sh . 30 true > report.json
          STALE=$(jq '.summary.staleFiles' report.json)
          if [ "$STALE" -gt 0 ]; then
            echo "::warning::Found $STALE stale documentation files"
          fi
```
