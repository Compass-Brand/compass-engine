---
name: pr-fix-patterns
description: Query Forgetful memory for PR review fix patterns and recurring issues
---

# PR Fix Patterns Skill

Query Forgetful memory for PR review fix patterns and recurring issues.

## Purpose

This skill helps identify:

- Recurring code review issues across PRs
- Common fix patterns that can be automated
- Areas of code that frequently trigger reviews
- Fix success/failure patterns

## Usage

Invoke when:

- Starting a new PR review resolution session
- Analyzing why certain fixes keep failing
- Looking for automation opportunities
- Reviewing team code quality trends

## Queries

### Find Recurring Issues

```
Search Forgetful for PR review patterns:

mcp__forgetful__execute_forgetful_tool with:
- tool: "search_memories"
- params: {
    "query": "pr-review recurring issue",
    # Note: project_id 2 is for compass-brand. Change this for other projects:
    # 1=legacy-system-analyzer, 3=competitor-analysis-toolkit, 4=compass-engine
    "project_id": 2,
    "limit": 20
  }
```

Look for issues that appear 3+ times across different PRs.

### Find Common Fix Patterns

```
mcp__forgetful__execute_forgetful_tool with:
- tool: "search_memories"
- params: {
    "query": "auto-fix success pattern",
    "project_id": 2,
    "limit": 10
  }
```

### Find Rollback Patterns

```
mcp__forgetful__execute_forgetful_tool with:
- tool: "search_memories"
- params: {
    "query": "pr-review rollback",
    "project_id": 2,
    "limit": 10
  }
```

### Analyze by File Type

```
mcp__forgetful__execute_forgetful_tool with:
- tool: "search_memories"
- params: {
    "query": "pr-review shell scripts",
    "project_id": 2,
    "limit": 10
  }
```

## Pattern Detection

When querying, look for these signals:

### Recurring Issue Indicators

- Same file mentioned in 3+ memories
- Same error message pattern
- Same reviewer comment type
- Same line range affected

### Automation Candidates

- High-confidence fixes with 100% success
- Simple pattern-based replacements
- Formatting/style issues
- Import ordering

### Human Review Required

- Low-confidence fixes with high rollback rate
- Architectural suggestions
- Security-related issues
- Breaking change warnings

## Output Format

When presenting patterns, use this structure:

```markdown
## PR Review Pattern Analysis

### Recurring Issues (3+ occurrences)

1. **Issue Type**: [description]
   - Files affected: [list]
   - Suggested automation: [yes/no + reason]

### Automation Opportunities

1. **Pattern**: [description]
   - Success rate: [percentage]
   - Implementation: [suggestion]

### Areas Needing Attention

1. **File/Area**: [path]
   - Issue frequency: [count]
   - Common problems: [list]
```

## Integration

This skill integrates with:

- `/resolve-pr-reviews` - Query patterns before dispatching
- `.claude/config/auto-fix-rules.json` - Update rules based on patterns
- `scripts/pr-metrics.sh` - Feed data into metrics dashboard
