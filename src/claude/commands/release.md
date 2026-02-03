---
name: release
description: Create a new release with version bump, changelog generation, and GitHub release
---

# Release

Create a new release with version bump, changelog generation, and GitHub release.

## Process

### 1. Determine Version Bump

Ask user for version type:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "What type of release is this?",
      "header": "Version",
      "options": [
        {"label": "Patch (x.x.X)", "description": "Bug fixes, no breaking changes"},
        {"label": "Minor (x.X.0)", "description": "New features, backward compatible"},
        {"label": "Major (X.0.0)", "description": "Breaking changes"}
      ],
      "multiSelect": false
    }
  ]
})
```

### 2. Get Current Version

```bash
# From package.json
CURRENT=$(jq -r '.version' package.json 2>/dev/null)

# Or from pyproject.toml (portable awk instead of grep -P)
CURRENT=$(awk -F'"' '/^version =/ {print $2; exit}' pyproject.toml 2>/dev/null)

# Or from VERSION file
CURRENT=$(cat VERSION 2>/dev/null)
```

### 3. Calculate New Version

```bash
# Validate version was retrieved
if [[ -z "$CURRENT" ]]; then
    echo "Error: Could not determine current version"
    exit 1
fi

# Validate semver format (supports prerelease versions like 1.2.3-alpha.1)
if ! [[ "$CURRENT" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
    echo "Error: Invalid semver format: $CURRENT"
    exit 1
fi

# Strip prerelease suffix before parsing (e.g., 1.2.3-alpha.1 -> 1.2.3)
BASE_VERSION="${CURRENT%%-*}"

IFS='.' read -r major minor patch <<< "$BASE_VERSION"

case "$BUMP_TYPE" in
    patch) NEW_VERSION="$major.$minor.$((patch + 1))" ;;
    minor) NEW_VERSION="$major.$((minor + 1)).0" ;;
    major) NEW_VERSION="$((major + 1)).0.0" ;;
esac

echo "Bumping $CURRENT -> $NEW_VERSION"
```

### 4. Update Version Files

```bash
# package.json
jq ".version = \"$NEW_VERSION\"" package.json > tmp.json && mv tmp.json package.json

# pyproject.toml (portable sed with temp file)
sed "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml > pyproject.toml.tmp && mv pyproject.toml.tmp pyproject.toml

# VERSION file
echo "$NEW_VERSION" > VERSION
```

### 5. Generate Changelog

Validate git repository and extract commits since last tag:

```bash
# Validate this is a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not a git repository"
    exit 1
fi

LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [[ -n "$LAST_TAG" ]]; then
    COMMITS=$(git log "$LAST_TAG"..HEAD --oneline)
else
    COMMITS=$(git log --oneline -20)
fi
```

Group by type:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Features

- feat: Description (#PR)

### Bug Fixes

- fix: Description (#PR)

### Other Changes

- refactor: Description
- docs: Description
- chore: Description
```

### 6. Update CHANGELOG.md

Prepend new release section to `CHANGELOG.md`:

```bash
# Create new changelog entry
# Note: grep uses "|| true" to prevent script exit when no matches found
cat > /tmp/new_entry.md << EOF
## [$NEW_VERSION] - $(date +%Y-%m-%d)

### Features
$(git log "$LAST_TAG"..HEAD --pretty=format:"%s" | grep -E "^feat" | sed 's/^/- /' || true)

### Bug Fixes
$(git log "$LAST_TAG"..HEAD --pretty=format:"%s" | grep -E "^fix" | sed 's/^/- /' || true)

### Other Changes
$(git log "$LAST_TAG"..HEAD --pretty=format:"%s" | grep -vE "^(feat|fix)" | sed 's/^/- /' || true)

EOF

# Prepend to CHANGELOG.md
cat /tmp/new_entry.md CHANGELOG.md > /tmp/changelog_new.md
mv /tmp/changelog_new.md CHANGELOG.md
```

### 7. Commit and Tag

```bash
# Stage only known version files (avoids accidentally staging sensitive files)
git add package.json pyproject.toml VERSION CHANGELOG.md 2>/dev/null || true
git commit -m "chore: Release v$NEW_VERSION" \
           -m "- Bump version to $NEW_VERSION" \
           -m "- Update CHANGELOG.md" \
           -m "Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
```

### 8. Push and Create GitHub Release

```bash
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin "$CURRENT_BRANCH" && git push origin "v$NEW_VERSION"

gh release create "v$NEW_VERSION" \
    --title "v$NEW_VERSION" \
    --notes-file /tmp/new_entry.md
```

## Options

| Option         | Description                                    |
| -------------- | ---------------------------------------------- |
| `--dry-run`    | Show what would be done without making changes |
| `--no-push`    | Create commit and tag but don't push           |
| `--prerelease` | Mark as prerelease (alpha, beta, rc)           |

## Prerelease Versions

For prereleases:

```bash
# Alpha
NEW_VERSION="1.2.0-alpha.1"

# Beta
NEW_VERSION="1.2.0-beta.1"

# Release Candidate
NEW_VERSION="1.2.0-rc.1"
```

## Verification

Before release, detect project type and run appropriate checks:

```bash
# Detect project type and run appropriate commands
if [[ -f "package.json" ]]; then
    # Node.js project
    npm test
    npm run lint
    npm run build
elif [[ -f "pyproject.toml" ]] || [[ -f "setup.py" ]]; then
    # Python project
    pytest
    ruff check .
    python -m build
elif [[ -f "go.mod" ]]; then
    # Go project
    go test ./...
    go build ./...
else
    echo "Warning: Unknown project type, skipping verification"
fi
```

## Rollback

If something goes wrong:

```bash
# Delete local tag
git tag -d "v$NEW_VERSION"

# Delete remote tag
git push origin --delete "v$NEW_VERSION"

# Validate last commit is the release commit before resetting
LAST_COMMIT_MSG=$(git log -1 --pretty=%s)
if [[ "$LAST_COMMIT_MSG" != "chore: Release v$NEW_VERSION" ]]; then
    echo "Error: Last commit is not the release commit. Aborting reset."
    echo "Last commit: $LAST_COMMIT_MSG"
    exit 1
fi

# Reset commit
git reset --hard HEAD~1

# Delete GitHub release
gh release delete "v$NEW_VERSION" --yes
```

## Related Commands

- `/create-pr` - Create PR for release branch
- `/session-summary` - Summarize release work
