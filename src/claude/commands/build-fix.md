---
description: Parse and fix build errors automatically
---

# Build Fix

## Usage

/build-fix <build-command>

## What This Command Does

1. Runs the specified build command
2. Invokes build-error-resolver agent on failures
3. Parses error output and applies fixes
4. Re-runs build to verify
5. Escalates to user after 2 failed attempts

## Invoked Components

- Agent: build-error-resolver

## Example

```
/build-fix npm run build
```
