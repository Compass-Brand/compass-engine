---
description: Verify changes with fresh evidence before completion
---

# Verify

## Usage

/verify

## What This Command Does

1. Applies verification-loop skill
2. Runs build command and shows output
3. Runs test command and shows output
4. Runs lint command and shows output
5. Reports pass/fail status

## Failure Behavior

- Stops on first failure (build, test, or lint)
- Reports the failing step and its output
- Exits with non-zero status if any step fails

## Invoked Components

- Skill: verification-loop

## Example

```
/verify
```

## Output

Verification report with command outputs and overall status
