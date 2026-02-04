---
name: full-cr-review
description: Complete codebase review using CodeRabbit CLI with parallel fixing and beads tracking
hooks:
  SessionStart:
    - matcher: "*"
      hooks:
        - type: command
          command: 'bash "$CLAUDE_PROJECT_DIR/.claude/scripts/cr-review-session-start.sh"'
          timeout: 5
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: 'bash "$CLAUDE_PROJECT_DIR/.claude/scripts/cr-review-stop.sh"'
          timeout: 10
  SubagentStop:
    - matcher: "*"
      hooks:
        - type: command
          command: 'bash "$CLAUDE_PROJECT_DIR/.claude/scripts/cr-batch-complete.sh"'
          timeout: 5
---

# Full Codebase CodeRabbit Review

Review and fix an entire codebase using CodeRabbit CLI, with parallel subagents and beads tracking.

## Usage

```bash
/full-cr-review [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--resume` | Resume an interrupted review |
| `--max-iterations N` | Override default max iterations (default: 5) |
| `--dry-run` | Show plan without executing |
| `--skip-beads` | Skip beads tracking (fixes only) |

## Prerequisites

Before running, verify:

1. **CodeRabbit CLI installed**: `which coderabbit`
2. **Beads CLI installed**: `which bd`
3. **Not on main/develop**: Create a feature branch first

## Workflow

### Phase 1: Initialization

**Step 1.1: Check Prerequisites**

```bash
# Verify CodeRabbit CLI
if ! command -v coderabbit &>/dev/null; then
    echo "ERROR: CodeRabbit CLI not installed"
    echo "Install: npm install -g @coderabbitai/cli"
    exit 1
fi

# Verify beads CLI (optional but recommended)
if ! command -v bd &>/dev/null; then
    echo "WARNING: Beads CLI not installed - issue tracking disabled"
fi

# Verify git auth
if ! gh auth status &>/dev/null; then
    echo "ERROR: GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi
```

**Step 1.2: Check/Create Feature Branch**

```bash
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "develop" ]; then
    echo "WARNING: On $CURRENT_BRANCH - creating feature branch"
    DATE_SUFFIX=$(date +%Y%m%d)
    git checkout -b "chore/cr-full-review-$DATE_SUFFIX"
fi
```

**Step 1.3: Check for Resume State**

If `--resume` flag is provided OR `.full-cr-in-progress` exists:

```bash
if [ -f ".full-cr-in-progress" ]; then
    STATE=$(cat .full-cr-in-progress)
    ITERATION=$(echo "$STATE" | jq -r '.iteration')
    echo "Resuming from iteration $ITERATION"
    # Continue from where we left off
fi
```

**Step 1.4: Create State File**

```bash
cat > .full-cr-in-progress << 'EOF'
{
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "branch": "$(git branch --show-current)",
  "iteration": 0,
  "total_issues_found": 0,
  "total_issues_fixed": 0,
  "batch_count": 0
}
EOF
```

### Phase 2: Run CodeRabbit Review

**Step 2.1: Get First Commit (Base Strategy)**

CodeRabbit reviews **changes**, so we use the first commit as base to review the entire codebase:

```bash
FIRST_COMMIT=$(git rev-list --max-parents=0 HEAD)
echo "Using first commit as base: $FIRST_COMMIT"
```

**Step 2.2: Run CodeRabbit CLI**

```bash
echo "Running CodeRabbit review (this may take 7-30 minutes)..."
coderabbit --prompt-only --base-commit "$FIRST_COMMIT" > .cr-review-output.txt 2>&1
```

The `--prompt-only` flag returns structured output without requiring a PR.

**Step 2.3: Parse Output**

Extract issues from the CodeRabbit output. Each issue includes:
- File path
- Line number(s)
- Severity (critical/major/minor/nit)
- Description
- Suggested fix
- AI prompt section (if present)

Display summary to user:

```
CodeRabbit Review Summary
---------------------------
Severity    Count
---------------------------
Critical      12
Major         45
Minor         89
Nit           23
---------------------------
TOTAL        169
```

### Phase 3: Create Beads Issues (if --skip-beads not set)

For each CodeRabbit finding, create a beads issue:

```bash
bd create "[CR] $FILE:$LINE - $SHORT_DESCRIPTION" \
  --type bug \
  --priority 2 \
  --labels coderabbit,$SEVERITY,$FILE_TYPE \
  --description "CodeRabbit Issue

File: $FILE
Line: $LINE
Severity: $SEVERITY

Suggestion:
$SUGGESTION"
```

**Label Strategy:**
- `coderabbit` - All issues from this command
- Severity: `critical`, `major`, `minor`, `nit`
- File type: `python`, `typescript`, `shell`, `markdown`, `yaml`

### Phase 4: Batch Issues

**Key Rule: Never split same file across batches** (prevents edit conflicts)

**Batching Algorithm:**
1. Group all issues by file
2. Categorize files by type
3. Create batches of 15-20 issues each
4. Balance batch sizes
5. Max 8 subagents

**Batching Table:**

| Total Issues | Subagents | Issues/Agent |
|--------------|-----------|--------------|
| 1-15         | 1         | all          |
| 16-40        | 2         | ~15-20       |
| 41-80        | 3-4       | ~20          |
| 81-120       | 5-6       | ~20          |
| 121-200      | 7-8       | ~25          |
| 200+         | 8         | 25+          |

Present batching plan:

```json
AskUserQuestion({
  "questions": [
    {
      "question": "Ready to dispatch N subagents to fix M issues across F files?",
      "header": "Confirm",
      "options": [
        {"label": "Proceed", "description": "Start parallel fixing"},
        {"label": "Review batches", "description": "Show batch breakdown first"},
        {"label": "Adjust count", "description": "Use more/fewer subagents"}
      ],
      "multiSelect": false
    }
  ]
})
```

### Phase 5: Dispatch Parallel Subagents

**CRITICAL:** Dispatch ALL batches in a single message with multiple Task tool calls.

For each batch, spawn a subagent:

```json
Task({
  "subagent_type": "general-purpose",
  "description": "Fix CR batch N",
  "prompt": "<subagent prompt - see below>"
})
```

**Subagent Prompt Template:**

```markdown
# CodeRabbit Issue Fixer - Batch ${BATCH_ID}

You are fixing ${ISSUE_COUNT} CodeRabbit issues.

## Instructions

For EACH issue in order:

1. **Backup** the file: `cp "$FILE" "$FILE.cr-backup"`
2. **Read** the file to understand context around the issue line
3. **Apply** the suggested fix from CodeRabbit
4. **Validate** syntax (run linter if available)
5. **Commit** the fix immediately with a conventional commit
6. **Close bead** (if tracking): `bd close ${BEAD_ID} --reason "Fixed: ${SUMMARY}"`
7. **Log result**: Append to `.cr-batch-${BATCH_ID}-results.jsonl`

## Commit Format

Each fix gets its own commit:
```
fix(cr-review): ${SHORT_DESCRIPTION}

File: ${FILE}:${LINE}
Category: ${CATEGORY}

Beads: ${BEAD_ID}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Rollback Rules

If validation fails after a fix:
```bash
cp "$FILE.cr-backup" "$FILE"
bd update ${BEAD_ID} --notes "Rollback: validation failed"
```
Do NOT commit failed fixes.

## Issues to Fix

${ISSUES_JSON}

Each issue contains:
- `file`: Path to file
- `line`: Line number
- `message`: Issue description
- `suggestion`: Recommended fix
- `bead_id`: Beads issue ID to close (optional)

## Output Format

Log each result to `.cr-batch-${BATCH_ID}-results.jsonl`:
```json
{"file": "src/foo.py", "line": 42, "bead_id": "beads-abc", "action": "fixed"}
{"file": "src/bar.py", "line": 15, "bead_id": "beads-def", "action": "rollback", "reason": "syntax_error"}
```

## Return Value

When complete, return JSON summary:
```json
{
  "batch_id": ${BATCH_ID},
  "fixed": <count>,
  "skipped": <count>,
  "rollbacks": <count>
}
```
```

### Phase 6: Wait and Aggregate Results

Wait for all subagents to complete. The SubagentStop hook tracks results in `.cr-batch-results.jsonl`.

Aggregate final counts:
- Total fixed
- Total skipped
- Total rollbacks
- Files modified

### Phase 7: Loop Control

**Step 7.1: Re-run Review**

After all fixes committed, run CodeRabbit again:

```bash
ITERATION=$((ITERATION + 1))
if [ "$ITERATION" -lt "$MAX_ITERATIONS" ]; then
    echo "Re-running CodeRabbit review (iteration $ITERATION)..."
    coderabbit --prompt-only --base-commit "$FIRST_COMMIT" > .cr-review-output.txt 2>&1
    # Parse and check issue count
fi
```

**Step 7.2: Exit Conditions**

| Condition | Action |
|-----------|--------|
| 0 issues found | Exit (success) |
| Max iterations reached | Exit (warn) |
| Issue count not decreasing | Warn user (may be stuck) |
| Issues remain | Continue to next iteration |

### Phase 8: Final Report

Display completion summary:

```
Full Codebase Review - COMPLETE
================================

Status: CLEAN (0 issues)
Iterations: 2/5

Summary:
  Total issues found: 183
  Total issues fixed: 183
  Total commits: 37
  Duration: 15m 42s

Branch: chore/cr-full-review-20260203

Next steps:
  git push && gh pr create
```

### Phase 9: Cleanup

Remove temporary files:

```bash
rm -f .full-cr-in-progress
rm -f .cr-batch-results.jsonl
rm -f .cr-review-output.txt
rm -f *.cr-backup
```

## Error Handling

| Error | Recovery |
|-------|----------|
| CodeRabbit timeout | Retry with longer timeout |
| Subagent fails | Report batch, continue others |
| Edit conflicts | Auto-resolve with latest |
| Beads unavailable | Continue without tracking |
| Max iterations reached | Exit with summary |

## Hooks

This command includes skill-scoped hooks:

| Hook | Purpose | File |
|------|---------|------|
| **SessionStart** | Detect/offer resume | `cr-review-session-start.sh` |
| **Stop** | Verify beads closed | `cr-review-stop.sh` |
| **SubagentStop** | Track batch completion | `cr-batch-complete.sh` |

Hooks only activate when `.full-cr-in-progress` exists.

## Files Created During Execution

| File | Purpose |
|------|---------|
| `.full-cr-in-progress` | Context marker + state |
| `.cr-review-output.txt` | Raw CodeRabbit output |
| `.cr-batch-results.jsonl` | Aggregated batch results |
| `.cr-batch-N-results.jsonl` | Per-batch results |
| `*.cr-backup` | File backups before edits |

## Tips

- **Large codebases**: Run on specific directories first with `--path src/`
- **Prioritize**: Fix critical/major first, then minor/nit
- **Review commits**: Use `git log --oneline -50` to review fixes
- **Stuck?**: Check `.cr-review-output.txt` for patterns

## Related Commands

- `/resolve-pr-reviews` - Fix PR-specific review comments
- `/code-review` - Local code review without CodeRabbit
- `/security-review` - Security-focused review
