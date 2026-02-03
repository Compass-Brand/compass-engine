---
name: create-pr
description: Generate a pull request from the current branch with auto-generated title, summary, and test plan
---

# Create PR

Generate a pull request from the current branch with auto-generated title, summary, and test plan.

## Prerequisites

- Current branch must have commits ahead of the base branch
- GitHub CLI (`gh`) must be authenticated

## Process

### 1. Gather Information

```bash
# Get current branch
BRANCH=$(git branch --show-current)

# Get remote name (from upstream tracking, or default to origin)
REMOTE=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null | cut -d'/' -f1)

# Get base branch (default: main)
BASE_BRANCH=$(git symbolic-ref refs/remotes/${REMOTE:-origin}/HEAD 2>/dev/null | sed 's@^refs/remotes/[^/]*/@@' || echo "main")

# Get commits for this branch
git log --oneline ${BASE_BRANCH}..HEAD

# Get diff stats
git diff --stat ${BASE_BRANCH}...HEAD
```

### 2. Generate Title

Format: `<type>: <Short description>` (max 70 characters)

- Extract type from branch name or commits (`feat/`, `fix/`, etc.)
- Summarize the main change
- Keep under 70 characters

Examples:

- `feat: Add user authentication with OAuth2`
- `fix: Resolve login timeout on slow connections`
- `refactor: Simplify database query patterns`

### 3. Generate Summary

Use this template:

```markdown
## Summary

- [Main change 1]
- [Main change 2]
- [Main change 3]

## Test plan

- [ ] [Test step 1]
- [ ] [Test step 2]
- [ ] [Test step 3]

---

Generated with [Claude Code](https://claude.ai/claude-code)
```

### 4. Create PR

```bash
# Note: Double-quoting ("$TITLE") is sufficient for gh pr create
# Replace <TITLE>, <SUMMARY>, and <TEST_PLAN> with actual generated content:
gh pr create --title "$TITLE" --body "$(cat <<'EOF'
## Summary
<bullets>

## Test plan
<checklist>

---
Generated with [Claude Code](https://claude.ai/claude-code)
EOF
)"
```

## Options

### Base Branch Override

If asked, allow specifying a different base branch:

```bash
gh pr create --base develop --title "..." --body "..."
```

### Draft PR

For work-in-progress:

```bash
gh pr create --draft --title "..." --body "..."
```

### Reviewers

Add reviewers if specified:

```bash
gh pr create --reviewer user1,user2 --title "..." --body "..."
```

## Verification

After creation, display:

- PR URL
- PR number
- Review status

```bash
gh pr view --json url,number,reviewDecision
```

## Error Handling

- **No commits**: "No commits found ahead of ${BASE_BRANCH}. Nothing to PR."
- **Already exists**: "PR already exists for this branch: [URL]"
- **Not authenticated**: "Run `gh auth login` to authenticate"

## Related Commands

- `/resolve-pr-reviews` - Fix review comments on existing PR
- `/push-all` - Push all repos before creating PR
