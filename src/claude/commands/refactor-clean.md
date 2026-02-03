---
description: Find and remove unused code safely
---

# Refactor Clean

## Usage

/refactor-clean <path>

## What This Command Does

1. Invokes the refactor-cleaner agent
2. Identifies unused exports/functions/variables
3. Verifies no references exist
4. Removes code safely
5. Runs tests to verify no regressions

## Invoked Components

- Agent: refactor-cleaner

## Example

```text
/refactor-clean src/utils/
```
