---
description: Generate and run E2E tests from user stories
---

# E2E

## Usage

/e2e "<user-story>"

## What This Command Does

1. Invokes the e2e-runner agent
2. Parses user story into test steps
3. Generates Playwright test file
4. Runs the test
5. Captures screenshots on failure

## Invoked Components

- Agent: e2e-runner

## Example

```
/e2e "User can log in with valid credentials"
```
