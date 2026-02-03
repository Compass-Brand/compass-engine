---
name: sync-bmad-method
description: Manually sync the BMAD-METHOD folder in compass-engine from the upstream repository
---

# Sync BMAD-METHOD from Upstream

Manually sync the BMAD-METHOD folder in compass-engine from the upstream repository.

## Prerequisites

The `PROJECT_DIR` environment variable should be set to the compass-brand repository root. If not set, the script falls back to determining the repo root via `git rev-parse --show-toplevel`.

## Instructions

1. Check for updates from upstream:

```bash
# Use PROJECT_DIR if set, otherwise detect repo root
PROJECT_DIR="${PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
if [ -z "$PROJECT_DIR" ]; then
  echo "Error: Could not determine project directory. Set PROJECT_DIR or run from within the repo."
  exit 1
fi

cd "$PROJECT_DIR/compass-engine/BMAD-METHOD" || { echo "Error: Failed to cd to BMAD-METHOD directory at $PROJECT_DIR/compass-engine/BMAD-METHOD"; exit 1; }
git fetch origin main || { echo "Error: Failed to fetch from origin/main"; exit 1; }
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then
  echo "✓ BMAD-METHOD is up to date"
else
  echo "Updates available:"
  git log --oneline "$LOCAL..$REMOTE"
fi
```

2. If updates are available, ask the user if they want to pull them.

3. If confirmed, pull and commit:

   ```bash
   cd "$PROJECT_DIR/compass-engine/BMAD-METHOD" || { echo "Error: Failed to cd to BMAD-METHOD"; exit 1; }
   git pull origin main || { echo "Error: Failed to pull from origin/main"; exit 1; }

   cd "$PROJECT_DIR/compass-engine" || { echo "Error: Failed to cd to compass-engine"; exit 1; }
   git add BMAD-METHOD
   git commit -m "Sync BMAD-METHOD from upstream

   $(cd BMAD-METHOD && git log --oneline -5)

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
   ```

4. Offer to push with `/push-all`.

## Notes

- Upstream repo: <https://github.com/bmad-code-org/BMAD-METHOD.git>
- No automated sync workflow is currently configured; sync is manual only
- Use this command for immediate manual sync

### Why Manual Sync?

Manual-only sync was chosen for the following reasons:

- **Independence**: BMAD-METHOD is an upstream project that evolves separately
- **Low change frequency**: Updates are infrequent and often require human review
- **Human review**: Changes to methodology should be reviewed before adoption

**When to consider automation:**

- If upstream change rate increases significantly
- If stable CI tests exist to validate changes
- If a clear rollback strategy is documented

**Recommended sync cadence:**

- Weekly during active development periods
- Monthly for stable/maintenance phases
- On tagged releases from upstream
