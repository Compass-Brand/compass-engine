---
name: compass-brand-setup
description: Interactive setup for a complete Compass Brand development environment
---

# Compass Brand Setup

Interactive setup for a complete Compass Brand development environment.

## Prerequisites

Set the `PROJECT_DIR` variable to your compass-brand project root before running commands:

```bash
# Set PROJECT_DIR to compass-brand root (adjust path as needed)
export PROJECT_DIR="$(pwd)"  # If already in compass-brand directory
# Or: export PROJECT_DIR="$HOME/Projects/compass-brand"
```

## Step 1: Verify Prerequisites

Run these checks first:

```bash
# Check Docker is running
docker info > /dev/null 2>&1 && echo "Docker: OK" || echo "Docker: NOT RUNNING"

# Check git is configured
git config user.name && echo "Git: OK" || echo "Git: NOT CONFIGURED"

# Check we're in compass-brand directory (use PROJECT_DIR if set, else pwd)
CHECK_DIR="${PROJECT_DIR:-$(pwd)}"
basename "$CHECK_DIR" | grep -qE "^compass[-_]brand$" && echo "Location: OK ($CHECK_DIR)" || echo "Location: NOT IN compass-brand"
```

If any prerequisite fails, inform the user what needs to be fixed.

## Step 2: Determine Setup Scope

```json
AskUserQuestion({
  "questions": [
    {
      "question": "What kind of setup do you need?",
      "header": "Setup Type",
      "options": [
        {"label": "Full setup (Recommended)", "description": "MCP services, git hooks, Forgetful registration"},
        {"label": "MCP services only", "description": "Just start Docker services"},
        {"label": "Verify existing setup", "description": "Check if everything is working"},
        {"label": "Repair/reset", "description": "Fix broken configuration"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 3: MCP Services

Start the shared MCP infrastructure:

```bash
cd "$PROJECT_DIR/mcps"
docker compose --profile serena up -d
```

Verify services:

```bash
docker compose ps
```

Expected services:

| Service        | Port | Purpose          |
| -------------- | ---- | ---------------- |
| Forgetful      | 8020 | Semantic memory  |
| PostgreSQL MCP | 8001 | Database queries |
| Context7       | 8002 | Library docs     |
| Serena         | 8003 | Code navigation  |

If any service fails, ask:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "<service> failed to start. How should I proceed?",
      "header": "Service Error",
      "options": [
        {"label": "Show logs", "description": "Let me see what went wrong"},
        {"label": "Skip this service", "description": "Continue without it"},
        {"label": "Retry", "description": "Try starting it again"},
        {"label": "Abort setup", "description": "Stop and fix manually"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 4: Sync .claude Content

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Sync .claude content from hub to all projects?",
      "header": "Sync",
      "options": [
        {"label": "Yes, sync all (Recommended)", "description": "Update all projects with hub content"},
        {"label": "Selective sync", "description": "Choose which projects to sync"},
        {"label": "Skip", "description": "Don't sync now"}
      ],
      "multiSelect": false
    }
  ]
})
```

If yes:

**PowerShell (Windows):**

```powershell
cd "$PROJECT_DIR"
.\sync-claude-hub.ps1 -Force
```

**Bash (Linux/macOS):**

```bash
cd "$PROJECT_DIR"
./sync-claude-hub.sh --force
```

## Step 5: Git Hooks

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Install git hooks for auto-sync on pull?",
      "header": "Git Hooks",
      "options": [
        {"label": "Yes (Recommended)", "description": "Auto-sync .claude when pulling changes"},
        {"label": "No", "description": "I'll sync manually"}
      ],
      "multiSelect": false
    }
  ]
})
```

If yes:

```bash
cd "$PROJECT_DIR"
./install-git-hooks.sh
```

## Step 6: Register Projects in Forgetful

Check existing projects:

```python
mcp__forgetful__execute_forgetful_tool("list_projects", {})
```

For each unregistered project, ask:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Register <project_name> in Forgetful?",
      "header": "Forgetful",
      "options": [
        {"label": "Yes (Recommended)", "description": "Enable memory for this project"},
        {"label": "Skip", "description": "Don't register this project"}
      ],
      "multiSelect": false
    }
  ]
})
```

If yes, register:

```python
mcp__forgetful__execute_forgetful_tool("create_project", {
  "name": "<Project Display Name>",
  "description": "<description>",
  "project_type": "development",
  "repo_name": "Compass-Brand/<project_name>"
})
```

### Default Projects

| Project                     | Description                                   |
| --------------------------- | --------------------------------------------- |
| legacy-system-analyzer      | Web app for analyzing legacy database schemas |
| competitor-analysis-toolkit | Competitive analysis using Claude Chrome MCP  |
| compass-engine              | Central development tools and AI agent configuration |

## Step 7: Verify Serena Configuration

```python
mcp__serena__get_current_config()
```

Ensure all projects are listed. If missing, offer to add them.

## Step 8: Test Connections

### Test Forgetful

```python
mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "test connection",
  "query_context": "Verifying Forgetful setup"
})
```

### Test GitHub CLI

```bash
gh api user --jq '.login'
```

### Test Context7

```python
# Note: Context7 uses hyphenated tool names (resolve-library-id, get-library-docs)
# which differs from the underscore convention used by other MCPs
mcp__context7__resolve-library-id({
  "query": "Python async web framework",
  "libraryName": "fastapi"
})
```

## Step 9: Setup Summary

Report final status:

```text
Compass Brand Setup Complete
============================

MCP Services
------------
[OK] Forgetful (port 8020)
[OK] PostgreSQL MCP (port 8001)
[OK] Context7 (port 8002)
[OK] Serena (port 8003)

GitHub CLI
----------
[OK] gh CLI authenticated

Configuration
-------------
[OK] .claude synced to all projects
[OK] Git hooks installed
[OK] Forgetful projects registered:
     - legacy-system-analyzer (ID: 1)
     - competitor-analysis-toolkit (ID: 2)
     - compass-engine (ID: 4)

GitHub: Authenticated as <username>
Serena: <N> projects configured

Ready to develop!
```

## Troubleshooting

### MCP services not starting

```bash
cd mcps && docker compose logs <service>
```

### Forgetful connection issues

- Check port 8020 is accessible
- Verify database is initialized
- Check `mcps/forgetful/.env` for credentials

### Serena not finding projects

- Check `mcps/serena/config.yaml`
- Restart: `docker compose restart serena`

### GitHub CLI not authenticated

- Run `gh auth status` to check authentication
- Run `gh auth login` to authenticate
- Verify token has required scopes with `gh auth status`

## Standalone Scripts

For CI/CD or manual setup:

```powershell
# Sync .claude content
.\sync-claude-hub.ps1 -Force

# Check for updates
.\scripts\check-updates.ps1

# Audit documentation
.\scripts\audit-docs.ps1
```
