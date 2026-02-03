---
description: Security audit with OWASP Top 10 and dependency scanning
---

# Security Review

## Usage

/security-review <path>

## What This Command Does

1. Invokes the security-reviewer agent
2. Applies security-review skill checklist
3. Runs dependency audit commands
4. Scans for hardcoded secrets
5. Provides CVSS scores for findings

## Invoked Components

- Agent: security-reviewer
- Skill: security-review

## Example

```text
/security-review src/auth/
```
