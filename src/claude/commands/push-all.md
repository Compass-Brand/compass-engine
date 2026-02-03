---
name: push-all
description: Push all commits from compass-brand and its submodule projects to their remotes
---

# Push All Repositories

Push all commits from compass-brand and its submodule projects to their remotes.

## Instructions

**Step 1:** Check the status of all repos to see what will be pushed:

```bash
cd "$PROJECT_DIR"
echo "=== compass-brand ==="
if git rev-parse @{u} >/dev/null 2>&1; then
  commits=$(git log --oneline @{u}..HEAD)
  if [ -z "$commits" ]; then
    echo "(no unpushed commits)"
  else
    echo "$commits"
  fi
else
  echo "(no upstream configured)"
fi
# Dynamically discover submodules from .gitmodules
SUBMODULES=$(git config --file .gitmodules --get-regexp path | awk '{print $2}')
for dir in $SUBMODULES; do
  (
    cd "$PROJECT_DIR/$dir"
    echo "=== $dir ==="
    if git rev-parse @{u} >/dev/null 2>&1; then
      commits=$(git log --oneline @{u}..HEAD)
      if [ -z "$commits" ]; then
        echo "(no unpushed commits)"
      else
        echo "$commits"
      fi
    else
      echo "(no upstream configured)"
    fi
  )
done
```

**Step 2:** Show the user what will be pushed and ask for confirmation.

**Step 3:** If confirmed, push submodules first (so parent can reference the new commits), then push parent:

```bash
cd "$PROJECT_DIR"
echo "Pushing submodules..."
# Dynamically discover submodules from .gitmodules
SUBMODULES=$(git config --file .gitmodules --get-regexp path | awk '{print $2}')
for dir in $SUBMODULES; do
  cd "$PROJECT_DIR/$dir"
  echo "  → $dir"
  output=$(git push 2>&1)
  exit_code=$?
  if [ $exit_code -ne 0 ]; then
    echo "Push failed for $dir:"
    echo "$output"
    exit $exit_code
  else
    # Show summary on success, with optional warnings
    echo "$output" | head -3
    if echo "$output" | grep -qiE "(warning)"; then
      echo "  (warnings above - review if needed)"
    fi
  fi
  cd "$PROJECT_DIR"
done
echo "Pushing compass-brand..."
git push
echo "All repos pushed"
```

**Step 4:** Report success or any errors.

## Notes

- Submodules push first so the parent repo's submodule references are valid
- If a submodule has no remote or no commits, it's skipped gracefully
- The parent push updates submodule commit references on the remote
- Submodules are discovered dynamically from `.gitmodules` - no hardcoded list to maintain
