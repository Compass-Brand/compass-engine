---
name: new-project
description: Interactive workflow for creating a new project in the Compass Brand ecosystem
---

# Create New Compass Brand Project

Interactive workflow for creating a new project in the Compass Brand ecosystem.

## Prerequisites

Before running the commands below, set `PROJECT_DIR` to your compass-brand root directory:

```bash
# Set PROJECT_DIR to compass-brand root (adjust path as needed)
export PROJECT_DIR="$HOME/Projects/compass-brand"
# Or if already in compass-brand directory:
# export PROJECT_DIR="$(pwd)"
```

## Step 1: Gather Project Information

Use the AskUserQuestion tool to collect required information:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "What type of project is this?",
      "header": "Project Type",
      "options": [
        {"label": "Development", "description": "A software application or tool"},
        {"label": "Research", "description": "Exploratory or analysis project"},
        {"label": "Tooling", "description": "Developer tools, scripts, utilities"},
        {"label": "Infrastructure", "description": "DevOps, CI/CD, platform services"}
      ],
      "multiSelect": false
    },
    {
      "question": "Should this project be public or private?",
      "header": "Visibility",
      "options": [
        {"label": "Public (Recommended)", "description": "Open source, visible to everyone"},
        {"label": "Private", "description": "Only accessible to team members"}
      ],
      "multiSelect": false
    },
    {
      "question": "Which starter template would you like?",
      "header": "Template",
      "options": [
        {"label": "Empty (Recommended)", "description": "Minimal structure, add what you need"},
        {"label": "FastAPI Backend", "description": "Python API with FastAPI, SQLAlchemy"},
        {"label": "Next.js Frontend", "description": "React app with Next.js, Shadcn UI"},
        {"label": "Full Stack", "description": "Both FastAPI backend and Next.js frontend"}
      ],
      "multiSelect": false
    }
  ]
})
```

After receiving answers, ask for:

- **Project name** (lowercase, underscores, e.g., `inventory_tracker`)
- **Description** (brief description of the project)

## Step 2: Run Local Setup Script

Run the standalone script to create local structure:

```powershell
# PowerShell (Windows)
.\scripts\new-project.ps1 -ProjectName "<project_name>" -Description "<description>" -ProjectType "<type>"
```

```bash
# Bash (Linux/Mac)
# Note: Bash version available at scripts/new-project.sh
./scripts/new-project.sh -n "<project_name>" -d "<description>" -t "<type>"
```

The script creates:

- Project directory with `.claude/` structure
- CLAUDE.md and README.md from templates
- .gitignore
- Initial git commit

## Step 3: Create GitHub Repository

Use gh CLI to create the repo:

```bash
# For public repos (recommended)
gh repo create Compass-Brand/<project_name> --public --description "<description>"

# For private repos
gh repo create Compass-Brand/<project_name> --private --description "<description>"
```

Or use the helper script:

```bash
# Public repo
./scripts/gh-create-repo.sh <project_name> -d "<description>" -v public

# Private repo
./scripts/gh-create-repo.sh <project_name> -d "<description>" -v private

# Dry run to see what would be created
./scripts/gh-create-repo.sh <project_name> -d "<description>" --dry-run
```

## Step 4: Connect Local to Remote

See the Prerequisites section at the top if `PROJECT_DIR` is not set.

```bash
cd "$PROJECT_DIR/<project_name>"
git remote add origin https://github.com/Compass-Brand/<project_name>.git
git push -u origin main
```

## Step 5: Add as Submodule

Ask the user:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Should I add this as a submodule to compass-brand?",
      "header": "Submodule",
      "options": [
        {"label": "Yes (Recommended)", "description": "Add to compass-brand as git submodule"},
        {"label": "No", "description": "Keep as standalone repository"}
      ],
      "multiSelect": false
    }
  ]
})
```

If yes:

```bash
cd "$PROJECT_DIR"
git submodule add https://github.com/Compass-Brand/<project_name>.git <project_name>
git add <project_name> .gitmodules
git commit -m "feat: Add <project_name> as submodule

<description>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

## Step 6: Register in Forgetful

```python
mcp__forgetful__execute_forgetful_tool("create_project", {
  "name": "<Project Name>",
  "description": "<description>",
  "project_type": "<project_type>",
  "repo_name": "Compass-Brand/<project_name>"
})
```

Save the returned project ID and update the project's CLAUDE.md.

## Step 7: Sync Hub Content

```powershell
Set-Location "$PROJECT_DIR"
.\sync-claude-hub.ps1 -Force -Projects "<project_name>"
```

## Step 8: Configure Serena (Optional)

Ask the user:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Should I add this project to Serena for code analysis?",
      "header": "Serena",
      "options": [
        {"label": "Yes", "description": "Enable LSP-powered code navigation"},
        {"label": "No", "description": "Skip Serena configuration"}
      ],
      "multiSelect": false
    }
  ]
})
```

If yes, update `mcps/serena/config.yaml` and restart Serena.

## Step 9: Final Summary

Report the completed setup:

```text
New Project Created: <project_name>
===================================
GitHub Repo:     https://github.com/Compass-Brand/<project_name>
Local Path:      compass-brand/<project_name>
Forgetful ID:    <project_id>
Visibility:      <public/private>
Template:        <selected template>
.claude:         Synced from hub
Serena:          <Configured/Skipped>

Next steps:
1. Add tech stack details to CLAUDE.md
2. Begin planning with /bmad:bmm:workflows:create-product-brief
```

## Standalone Script

The local setup can also be run independently:

```powershell
# From compass-brand directory
.\scripts\new-project.ps1 -ProjectName "my_project" -Description "My description" -JsonOutput
```

This is useful for CI/CD or when you want to create the structure without Claude Code.
