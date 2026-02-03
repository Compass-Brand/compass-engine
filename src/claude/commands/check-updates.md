---
name: check-updates
description: Interactive workflow for monitoring dependencies and tools across Compass Brand projects
---

# Check for Updates

Interactive workflow for monitoring dependencies and tools across Compass Brand projects.

## Step 1: Confirm Scope

Use AskUserQuestion to determine what to check:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "What would you like to check for updates?",
      "header": "Scope",
      "options": [
        {"label": "Everything (Recommended)", "description": "Node, Python, Docker, MCP servers"},
        {"label": "Node packages only", "description": "npm dependencies across all projects"},
        {"label": "Python packages only", "description": "pip packages across all projects"},
        {"label": "Docker images only", "description": "Container images in mcps/"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 2: Run Update Check Script

Based on the user's selection, run the standalone script:

```powershell
# PowerShell (Windows)
.\scripts\check-updates.ps1                    # Everything
.\scripts\check-updates.ps1 -NodeOnly          # Node only
.\scripts\check-updates.ps1 -PythonOnly        # Python only
.\scripts\check-updates.ps1 -DockerOnly        # Docker only
.\scripts\check-updates.ps1 -JsonOutput        # Machine-readable output
```

```bash
# Bash (Linux/Mac)
# Usage: ./scripts/check-updates.sh [workdir] [json_flag]
# Parameters are positional: first arg is working directory, second enables JSON output
./scripts/check-updates.sh                     # Everything (defaults to current dir)
./scripts/check-updates.sh .                   # Explicit current dir
./scripts/check-updates.sh . true              # Current dir with JSON output
./scripts/check-updates.sh ~/myproject true    # Custom workdir with JSON output
```

## Step 3: Check GitHub Releases

For key framework releases, use gh CLI:

```bash
# Next.js
gh release view --repo vercel/next.js --json tagName,publishedAt,name

# FastAPI
gh release view --repo tiangolo/fastapi --json tagName,publishedAt,name

# Forgetful
gh release view --repo ScottRBK/forgetful --json tagName,publishedAt,name
```

Or use the helper script for consistent JSON output:

```bash
./scripts/gh-latest-release.sh vercel/next.js
./scripts/gh-latest-release.sh tiangolo/fastapi
./scripts/gh-latest-release.sh ScottRBK/forgetful
```

## Step 4: Safety Check

If it's Friday or the day before a release, warn the user:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "It's Friday. Major updates are not recommended. How would you like to proceed?",
      "header": "Friday Warning",
      "options": [
        {"label": "Skip major updates", "description": "Only apply patch updates today"},
        {"label": "Note for Monday", "description": "Create a reminder to update Monday"},
        {"label": "Proceed anyway", "description": "I understand the risk"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 5: Present Update Options

After gathering all update information, ask:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Which updates would you like to apply?",
      "header": "Updates",
      "options": [
        {"label": "Safe patches only (Recommended)", "description": "Apply only patch version updates"},
        {"label": "All minor updates", "description": "Apply patch and minor version updates"},
        {"label": "Review each one", "description": "Ask me about each update individually"},
        {"label": "None for now", "description": "Just show the report, don't update"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 6: Apply Updates (if approved)

### Safe Patch Updates

```bash
cd "$PROJECT_DIR/<project>"
npm update           # Node patches
pip install --upgrade <package>  # Python
```

### Handling Update Failures

When updates fail, check for:

1. **Dependency conflicts (peer deps)**:

   ```bash
   npm ls <package>  # Check dependency tree
   npm install --legacy-peer-deps  # If needed for compatibility
   ```

2. **Build failures**: Check changelogs for breaking changes, revert if necessary:

   ```bash
   git checkout package.json package-lock.json
   npm ci  # Reinstall from lock file
   ```

3. **Test failures**: Inspect test output, check if API changes affected tests:

   ```bash
   npm test -- --verbose
   # If tests fail, revert and check changelog for migration steps
   ```

4. **Rollback commands**:

   ```bash
   # Node
   git checkout package.json package-lock.json && npm ci
   # Python
   pip install -r requirements.txt  # Restore from pinned versions
   ```

Consult CI logs for additional context on failures.

### Minor/Major Updates

For each significant update, first resolve the library ID, then fetch migration docs:

```text
# Pseudocode - MCP tool names shown with hyphens for clarity
# Actual MCP function names use underscores (e.g., mcp__context7__resolve_library_id)

# Step 1: Resolve the library ID
library_info = mcp__context7__resolve_library_id({
  "query": "next.js React framework",
  "libraryName": "next.js"
})
# Returns context7CompatibleLibraryID like "/vercel/next.js"

# Step 2: Get migration documentation
mcp__context7__get_library_docs({
  "context7CompatibleLibraryID": "/vercel/next.js",  # From step 1
  "topic": "migration"
})
```

Then ask:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Update <package> from X.X.X to Y.Y.Y? (Minor update)",
      "header": "<package>",
      "options": [
        {"label": "Yes, update", "description": "Apply this update now"},
        {"label": "Skip", "description": "Don't update this package"},
        {"label": "Show changelog", "description": "Let me see what changed first"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 7: Record in Forgetful

After checking (regardless of whether updates were applied):

```json
mcp__forgetful__execute_forgetful_tool("create_memory", {
  "title": "Dependency Check - <date>",
  "content": "Checked X projects. Found Y updates available.\n\nApplied:\n- ...\n\nDeferred:\n- ...",
  "context": "Regular dependency monitoring",
  "keywords": ["dependencies", "updates", "maintenance"],
  "tags": ["maintenance"],
  "importance": 5
})
```

## Standalone Usage

The script can run independently for CI/CD or scheduled checks:

```powershell
# Generate JSON report for CI
.\scripts\check-updates.ps1 -JsonOutput > update-report.json

# Check only Node packages
.\scripts\check-updates.ps1 -NodeOnly
```

## Safety Rules (Enforced)

- **No Friday major updates** - Script warns, Claude should confirm
- **No updates before releases/demos** - Ask user about timing
- **Always commit before updating** - Lock in working state
- **Run tests after updates** - Verify nothing broke

## Automation

For scheduled checks without Claude Code:

```yaml
# GitHub Action - runs Monday 9am
name: Weekly Dependency Check

on:
  schedule:
    - cron: "0 9 * * 1"

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/check-updates.sh . true > report.json
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: dependency-report
          path: report.json
```
