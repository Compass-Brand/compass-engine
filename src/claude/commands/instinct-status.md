---
description: List all instincts with confidence scores and invocation counts
---

# Instinct Status

## Usage

/instinct-status [--filter low|medium|high|ready]

## Filter Definitions

| Filter   | Confidence Range            | Description                              |
| -------- | --------------------------- | ---------------------------------------- |
| `low`    | 0.0 - 0.49                  | Uncertain instincts, may need more data  |
| `medium` | 0.5 - 0.74                  | Moderately confident, still learning     |
| `high`   | 0.75 - 0.89                 | Highly confident, approaching graduation |
| `ready`  | >= 0.9 AND invocations > 10 | Meets graduation criteria                |

## What This Command Does

1. Queries Forgetful for all instinct memories
2. Displays table of instincts with:
   - Pattern summary
   - Confidence score
   - Invocation count
   - Last used date
3. Highlights graduation candidates

## Output Format

| Pattern      | Confidence | Invocations | Last Used  | Status            |
| ------------ | ---------- | ----------- | ---------- | ----------------- |
| When X, do Y | 0.92       | 15          | 2026-01-28 | Ready to graduate |
