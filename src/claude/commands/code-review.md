---
description: Review code for quality, naming, complexity, and issues
---

# Code Review

## Usage

/code-review <path>

## What This Command Does

1. Invokes the code-reviewer agent
2. Scans for naming issues, complexity, duplication
3. Checks error handling and basic security
4. Outputs markdown table with findings by severity

## Invoked Components

- Agent: code-reviewer

## Example

```
/code-review src/
```

## Output

Markdown table with columns: Severity, File, Line, Issue Type, Description, Recommendation
