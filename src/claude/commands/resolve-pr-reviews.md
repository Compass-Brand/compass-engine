---
name: resolve-pr-reviews
description: Automated workflow for resolving CodeRabbit and Greptile review comments using parallel subagents
hooks:
  Stop:
    - matcher: '*'
      hooks:
        - type: command
          command: 'bash "$CLAUDE_PROJECT_DIR/scripts/hooks/verify-pr-completion.sh"'
          timeout: 30
  SubagentStop:
    - matcher: '*'
      hooks:
        - type: command
          command: 'bash "$CLAUDE_PROJECT_DIR/scripts/hooks/track-subagent-batch.sh"'
          timeout: 10
---

# Resolve PR Reviews

Automated workflow for resolving CodeRabbit and Greptile review comments using parallel subagents.

## Prerequisites

This command works best when the `reviews-complete.yml` GitHub Action has posted the completion marker. Check for `<!-- REVIEWS_COMPLETE_MARKER -->` comment on the PR.

## Step 1: Identify the PR

If not provided, ask the user:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Which PR would you like to resolve reviews for?",
      "header": "PR",
      "options": [
        {"label": "Current branch PR", "description": "Find PR for the current git branch"},
        {"label": "Specify PR number", "description": "I'll tell you the PR number"}
      ],
      "multiSelect": false
    }
  ]
})
```

To find PR for current branch:

```bash
gh pr view --json number,title,url
```

## Step 2: Check Reviews Complete

Check if the completion marker exists:

```bash
gh pr view <PR_NUMBER> --json comments --jq '.comments[].body' | grep -c "REVIEWS_COMPLETE_MARKER"
```

**If marker NOT found**, check review status and ask:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Reviews may still be in progress. How would you like to proceed?",
      "header": "Status",
      "options": [
        {"label": "Wait for completion", "description": "Monitor until both CodeRabbit and Greptile finish"},
        {"label": "Proceed anyway", "description": "Fetch current comments even if reviews incomplete"},
        {"label": "Cancel", "description": "Come back later when reviews are done"}
      ],
      "multiSelect": false
    }
  ]
})
```

**If waiting**, use background task:

```bash
gh pr checks <PR_NUMBER> --watch
```

## Step 3: Check for Recurring Issues

Before fetching new issues, query Forgetful for known patterns:

```
Use the pr-fix-patterns skill to identify recurring issues:

mcp__forgetful__execute_forgetful_tool with:
- tool: "search_memories"
- params: {
    "query": "pr-review recurring issue",
    "project_id": 2,
    "limit": 10
  }
```

If the same issue type appears 3+ times across different PRs:

1. Flag it as a **recurring issue** in the batch output
2. Consider if it should be added to `.claude/config/auto-fix-rules.json`
3. Suggest creating a pre-commit hook or linter rule to prevent future occurrences

Present recurring patterns to user:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "I found N recurring issues that keep appearing in PRs. Should I suggest automation for these?",
      "header": "Patterns",
      "options": [
        {"label": "Yes, suggest fixes", "description": "Recommend linter rules or hooks"},
        {"label": "Just note them", "description": "Proceed without automation suggestions"},
        {"label": "Skip pattern check", "description": "Focus on this PR only"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 4: Fetch and Batch Review Issues

Use the helper script to fetch all issues with pagination, deduplication, and intelligent batching:

```powershell
# Fetch with summary output first
pwsh -File scripts/fetch-pr-reviews.ps1 -PRNumber <NUMBER> -OutputFormat summary

# Or get full JSON for processing
pwsh -File scripts/fetch-pr-reviews.ps1 -PRNumber <NUMBER> -OutputFormat json > pr-reviews.json
```

The script handles:

- **Pagination**: Fetches ALL review threads (not just first 100)
- **UTF-8 encoding**: Properly handles emoji and unicode characters
- **Deduplication**: Consolidates overlapping issues on same line
- **AI prompt extraction**: Extracts CodeRabbit's "Prompt for AI Agents" sections
- **Smart batching**: Groups by file type (shell, powershell, markdown, yaml, etc.)

### Alternative: Manual GraphQL

If the script isn't available, use GraphQL with cursor-based pagination:

```graphql
query ($owner: String!, $repo: String!, $pr: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          isResolved
          isOutdated
          path
          line
          comments(first: 10) {
            nodes {
              body
              author {
                login
              }
            }
          }
        }
      }
    }
  }
}
```

## Step 5: Create Context Marker

Before dispatching subagents, create a marker file to track the PR review session:

```bash
cat > .pr-review-in-progress << EOF
{
  "pr_number": <PR_NUMBER>,
  "owner": "Compass-Brand",
  "repo": "compass-brand",
  "initial_issue_count": <ISSUE_COUNT>,
  "batch_count": <BATCH_COUNT>,
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
```

This marker enables:

- Stop hook to verify completion
- SubagentStop hook to track batch progress
- Results aggregation in `.pr-review-results.jsonl`

## Step 6: File Conflict Detection

Before creating batches, detect files that have multiple issues to prevent parallel edit conflicts:

```bash
# Build file-to-issue map and detect overlaps
pwsh -Command "
\$data = Get-Content pr-reviews.json | ConvertFrom-Json
\$fileIssues = @{}

foreach (\$batch in \$data.batches) {
    foreach (\$issue in \$batch.issues) {
        \$file = \$issue.file
        if (-not \$fileIssues[\$file]) {
            \$fileIssues[\$file] = @()
        }
        \$fileIssues[\$file] += @{
            batch = \$batch.id
            line = \$issue.line
            confidence = \$issue.confidence
        }
    }
}

# Find files appearing in multiple batches
\$conflicts = @()
foreach (\$file in \$fileIssues.Keys) {
    \$batches = (\$fileIssues[\$file] | Select-Object -ExpandProperty batch -Unique)
    if (\$batches.Count -gt 1) {
        \$conflicts += @{
            file = \$file
            batches = \$batches
            issueCount = \$fileIssues[\$file].Count
        }
    }
}

if (\$conflicts.Count -gt 0) {
    Write-Host 'File conflicts detected:' -ForegroundColor Yellow
    \$conflicts | ForEach-Object {
        Write-Host \"  \$(\$_.file): \$(\$_.issueCount) issues across batches \$(\$_.batches -join ', ')\"
    }
}
"
```

**Conflict Resolution Strategies:**

1. **Merge Strategy** (preferred): Consolidate all issues for a conflicting file into a single batch
2. **Serialize Strategy**: Run batches touching same file sequentially, not parallel
3. **Line-Range Strategy**: If issues target non-overlapping line ranges (>10 lines apart), allow parallel execution

If conflicts are detected, the workflow will merge them into appropriate batches before dispatching.

## Step 7: Dynamic Batching (Continued)

The helper script groups issues into batches automatically. The batching algorithm:

```text
1. Group all issues by file category (shell, powershell, markdown, yaml, etc.)
2. Sort categories by issue count (descending)
3. Target batch size: 15-25 issues per subagent
4. Max subagents: 8
5. Distribute categories to balance batch sizes
```

**Batching table:**

| Total Issues | Subagents | Issues/Agent |
| ------------ | --------- | ------------ |
| 1-15         | 1         | all          |
| 16-40        | 2         | ~15-20       |
| 41-80        | 3-4       | ~20          |
| 81-120       | 5-6       | ~20          |
| 121-200      | 7-8       | ~25          |
| 200+         | 8         | 25+          |

Present the batching plan to user:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "I'll dispatch N subagents to fix M issues. Proceed?",
      "header": "Confirm",
      "options": [
        {"label": "Proceed", "description": "Start parallel fixing"},
        {"label": "Review batches first", "description": "Show me the batch breakdown"},
        {"label": "Adjust batch size", "description": "I want more/fewer subagents"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Step 8: Dispatch Subagents (Confidence-Based)

Load auto-fix rules from `.claude/config/auto-fix-rules.json` to determine handling:

```bash
# Read confidence rules
RULES=$(cat .claude/config/auto-fix-rules.json)
```

**Confidence-Based Dispatch Strategy:**

| Confidence | Action                   | Review Required |
| ---------- | ------------------------ | --------------- |
| **High**   | Auto-fix immediately     | No              |
| **Medium** | Auto-fix with validation | Yes (post-fix)  |
| **Low**    | Skip or manual only      | Yes (pre-fix)   |

For high/medium confidence issues, spawn subagents:

```json
Task({
  "subagent_type": "general-purpose",
  "description": "Fix review issues batch N",
  "prompt": "Fix the following review issues. For each issue:\n1. Read the file and understand context\n2. Apply the suggested fix\n3. Run relevant tests if available\n4. If tests fail, rollback the change\n\nIssues:\n{{issues}}\n\nRollback on failure. Log results to .pr-review-results.jsonl"
})
```

For low confidence issues, present to user:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "These N issues have low confidence and may require judgment. How should I handle them?",
      "header": "Low Conf",
      "options": [
        {"label": "Skip all", "description": "Leave for manual review"},
        {"label": "Attempt fixes", "description": "Try to fix but require approval"},
        {"label": "Show details", "description": "Let me review each one"}
      ],
      "multiSelect": false
    }
  ]
})
```

**Note:** The prompt template can be stored in `.claude/prompts/fix-review-issues.md` with placeholders for `{{repo_dir}}` and `{{issues}}`.

### Prompt Size Limits

To avoid token limit issues:

- **Target**: 15-20 issues per batch maximum
- **Large code blocks**: Replace with brief references like "See file.py lines 45-60"
- **Long AI prompts**: Truncate to first 500 characters + "..."
- **If batch exceeds ~8000 tokens**: Split into smaller batches

If a single batch would be too large:

1. Split into multiple Task calls with fewer issues each
2. Write full issue details to a temp file and reference it: "Issues in /tmp/batch-1-issues.json"

**IMPORTANT: Dispatch ALL batches in parallel** by including multiple Task tool calls in a single message.

### Test-After-Fix Rollback

Each subagent should implement this rollback logic:

```bash
#!/bin/bash
# Per-file rollback logic for subagents

BACKUP_DIR=".pr-fix-backups"
mkdir -p "$BACKUP_DIR"

fix_with_rollback() {
    local file="$1"
    local backup="$BACKUP_DIR/$(basename "$file").backup"

    # 1. Create backup
    cp "$file" "$backup"

    # 2. Apply fix (done by subagent)
    # ... fix applied ...

    # 3. Run validation
    if ! ./scripts/validate-before-push.sh --file "$file" 2>/dev/null; then
        echo "Validation failed for $file, rolling back..."
        cp "$backup" "$file"
        echo "{\"file\": \"$file\", \"action\": \"rollback\", \"reason\": \"validation_failed\"}" >> .pr-review-results.jsonl
        return 1
    fi

    # 4. Run tests if available (scoped to related test file)
    if command -v pytest &>/dev/null && [[ "$file" == *.py ]]; then
        # Find related test file preserving directory structure
        # e.g., src/module_x/file.py -> tests/module_x/test_file.py
        local file_base=$(basename "$file" .py)
        local file_dir=$(dirname "$file")
        local relative_dir=""
        local test_file=""

        # Try to derive mirrored test path from source file's relative directory
        # Strip leading src/ or similar prefix to get relative path
        if [[ "$file_dir" =~ ^\.?/?src/(.*)$ ]]; then
            relative_dir="${BASH_REMATCH[1]}"
        elif [[ "$file_dir" =~ ^\.?/?lib/(.*)$ ]]; then
            relative_dir="${BASH_REMATCH[1]}"
        else
            relative_dir="$file_dir"
        fi

        # First, try exact mirrored path: tests/<relative_dir>/test_<file>.py
        if [ -n "$relative_dir" ] && [ "$relative_dir" != "." ]; then
            if [ -f "./tests/${relative_dir}/test_${file_base}.py" ]; then
                test_file="./tests/${relative_dir}/test_${file_base}.py"
            elif [ -f "./tests/${relative_dir}/${file_base}_test.py" ]; then
                test_file="./tests/${relative_dir}/${file_base}_test.py"
            fi
        fi

        # Fallback to global find if exact path not found
        if [ -z "$test_file" ]; then
            test_file=$(find . -path "./tests/*" \( -name "test_${file_base}.py" -o -name "${file_base}_test.py" \) 2>/dev/null | head -1)
        fi

        if [ -n "$test_file" ]; then
            local sanitized_path=$(echo "$file" | tr '/' '_')
            local test_log=".pr-review-test-${sanitized_path}.log"
            if ! pytest "$test_file" --tb=short -q 2>&1 | tee "$test_log"; then
                echo "Tests failed for $file, rolling back... (see $test_log for details)"
                cp "$backup" "$file"
                echo "{\"file\": \"$file\", \"action\": \"rollback\", \"reason\": \"tests_failed\", \"log\": \"$test_log\"}" >> .pr-review-results.jsonl
                return 1
            fi
            rm -f "$test_log"
        fi
    fi

    echo "{\"file\": \"$file\", \"action\": \"fixed\", \"result\": \"success\"}" >> .pr-review-results.jsonl
    return 0
}
```

Subagents should:

1. Create backups before any edit
2. Apply the fix
3. Run `./scripts/validate-before-push.sh` if available
4. Run language-specific tests
5. Rollback on any failure
6. Log all outcomes to `.pr-review-results.jsonl`

## Step 9: Collect Results

Wait for all subagents to complete. The SubagentStop hook tracks results in `.pr-review-results.jsonl`.

Collect:

- Files modified
- Issues fixed
- Issues skipped (with reasons)
- Any errors encountered

## Step 10: Verify and Commit

After all subagents complete:

1. **Run validation** (automatically checked by pre-commit hook):

   ```bash
   ./scripts/validate-before-push.sh
   ```

2. **Review changes**:

   ```bash
   git diff --stat
   ```

3. **Ask user to confirm commit**:

   ```json
   AskUserQuestion({
     "questions": [
       {
         "question": "Subagents fixed X of Y issues. Commit all changes?",
         "header": "Commit",
         "options": [
           {"label": "Commit and push", "description": "Commit all fixes and push to PR"},
           {"label": "Commit only", "description": "Commit but don't push yet"},
           {"label": "Review first", "description": "Show me the diff before committing"},
           {"label": "Discard", "description": "Don't commit, I'll review manually"}
         ],
         "multiSelect": false
       }
     ]
   })
   ```

4. **Commit with summary**:

   ```bash
   git add -A
   git commit -m "fix: Resolve code review issues from CodeRabbit and Greptile

   Fixed X issues across Y files:
   - <category>: N fixes
   - <category>: N fixes

   Skipped Z issues (see PR comments for details)

   Co-Authored-By: {MODEL_NAME} <noreply@anthropic.com>"
   ```

5. **Push** (with fork detection):

   ```bash
   # Check if this is a fork-based PR
   ORIGIN_URL=$(git remote get-url origin)
   UPSTREAM_URL=$(git remote get-url upstream 2>/dev/null || echo "")

   if [ -n "$UPSTREAM_URL" ]; then
     # Fork-based: push to origin (user's fork)
     git push origin HEAD
     echo "Pushed to fork. PR will update automatically."
   else
     # Direct: push to origin
     git push
   fi
   ```

   For fork-based PRs where upstream is configured, push to the fork's origin.

## Step 11: Log to Forgetful Memory

After resolution, log the session outcomes to Forgetful for future learning:

```text
Use the Forgetful MCP to save this PR review session:

mcp__forgetful__execute_forgetful_tool with:
- tool: "save_memory"
- params: {
    "title": "PR Review Resolution: PR #<NUMBER>",
    "content": "Resolved <X> of <Y> review issues from CodeRabbit and Greptile.\n\nHigh confidence: <N> fixed\nMedium confidence: <N> fixed\nLow confidence: <N> skipped\n\nRollbacks: <N>\nMost common issues: <list>\n\nFiles affected: <list>",
    "tags": ["pr-review", "auto-fix", "compass-brand"],
    "project_id": 2
  }
```

This enables:

- Pattern detection across PRs (recurring issues)
- Fix success rate tracking
- Rollback analysis
- Learning from failures

## Step 12: Cleanup and Report

1. **Remove context marker**:

```bash
rm -f .pr-review-in-progress .pr-review-results.jsonl
```

2. **Post summary comment on the PR**:

```bash
gh pr comment <PR_NUMBER> --body "## Review Resolution Complete

**Fixed:** X issues
**Skipped:** Y issues
**Files modified:** Z

### Fixed Issues by Category
- Shell scripts: N fixes
- PowerShell scripts: N fixes
- Markdown docs: N fixes

### Skipped Issues
- file.md line 45: Suggestion would break formatting (manual review needed)

---
Commit: <SHA>"
```

## Error Handling

- **Subagent fails**: Report which batch failed, continue with others
- **Conflicting edits**: See Conflict Detection below
- **Reviews still posting**: Warn user, offer to wait or proceed with partial
- **No issues found**: Report "All issues already resolved" and exit
- **Validation fails**: Pre-commit hook will deny the commit - fix issues first

### Conflict Detection and Resolution

Before dispatching subagents:

1. **Build file-to-batch map**: Create a mapping of each issue's file path to its batch
2. **Detect overlaps**: Identify files that appear in multiple batches
3. **Handle overlaps**:
   - **Preferred**: Merge overlapping issues into a single batch
   - **Alternative**: Serialize execution for batches touching the same file
   - **Line-range split**: If issues target non-overlapping line ranges, allow parallel execution

After parallel execution:

```bash
# Check for git conflicts - capture exit status
if ! git diff --check; then
  echo "Warning: git diff --check reported issues"
fi

# Get list of conflicted files into an array
CONFLICTED=()
while IFS= read -r file; do
  [ -n "$file" ] && CONFLICTED+=("$file")
done < <(git diff --name-only --diff-filter=U 2>/dev/null)

if [ ${#CONFLICTED[@]} -gt 0 ]; then
  echo "Conflicts detected in: ${CONFLICTED[*]}"
  echo ""
  echo "WARNING: The following files have conflicts that need resolution."
  echo "Review each file before proceeding:"
  echo ""
  for file in "${CONFLICTED[@]}"; do
    echo "  - $file"
    # Create backup before any resolution
    cp "$file" "$file.conflict-backup"
    echo "    Backup saved to: $file.conflict-backup"
  done
  echo ""
  echo "Options for each conflicted file:"
  echo "  git checkout --theirs <file>  # Accept incoming changes (discards local)"
  echo "  git checkout --ours <file>    # Keep local changes (discards incoming)"
  echo "  manual edit                   # Resolve conflicts by hand"
  echo ""
  echo "Do you want to proceed with auto-resolution using --theirs? (y/N)"
  read -r response
  if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    for file in "${CONFLICTED[@]}"; do
      echo "Resolving $file with --theirs (backup at $file.conflict-backup)"
      git checkout --theirs "$file"
    done
  else
    echo "Skipping auto-resolution. Please resolve conflicts manually."
  fi
fi
```

If conflicts cannot be auto-resolved, flag them for manual review with the specific file and line information.

## Manual Override

If user wants to fix specific issues only:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Which issues would you like to fix?",
      "header": "Scope",
      "options": [
        {"label": "All unresolved", "description": "Fix everything"},
        {"label": "Critical/Major only", "description": "Skip minor and nitpick issues"},
        {"label": "Specific files", "description": "I'll specify which files to fix"},
        {"label": "CodeRabbit only", "description": "Only fix CodeRabbit issues"},
        {"label": "Greptile only", "description": "Only fix Greptile issues"}
      ],
      "multiSelect": false
    }
  ]
})
```

## Related Commands

- `/audit-docs` - Check documentation freshness
- `/check-updates` - Check for dependency updates
- `/push-all` - Push all repos after fixes

## Hooks

This command includes skill-scoped hooks:

| Hook             | Purpose                                                  |
| ---------------- | -------------------------------------------------------- |
| **Stop**         | Verifies all issues addressed before allowing completion |
| **SubagentStop** | Tracks batch completion and aggregates results           |

These hooks only activate when the `.pr-review-in-progress` marker file exists.
