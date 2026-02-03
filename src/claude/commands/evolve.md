---
description: Graduate qualifying instincts to skills
---

# Evolve

## Usage

/evolve [--dry-run] [--force instinct-id]

## What This Command Does

1. Finds instincts meeting graduation criteria
2. Checks for contradictions with existing rules/skills
3. Generates skill files for qualifying instincts
4. Archives graduated instincts

## Graduation Criteria

- Confidence > 0.9
- Invocations > 10
- No contradictions

## Options

- `--dry-run`: Show candidates without making changes
- `--force`: Graduate specific instinct regardless of criteria
