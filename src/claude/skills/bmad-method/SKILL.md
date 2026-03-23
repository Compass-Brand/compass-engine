---
name: bmad-method
description: Use when the user needs help choosing, sequencing, or running Compass BMAD workflows and slash commands across planning, docs, solutioning, implementation, or polyrepo routing.
---

# BMAD Method

## When to Use

Use this skill when the user:

- asks what BMAD command or workflow to run next
- wants to move between roadmap, phase, and implementation work
- needs workspace or polyrepo routing guidance
- wants to understand how planning, docs, and BMAD fit together

## Instructions

1. Start with `_bmad/BMAD-workflow.md` for the high-level flow.
2. Use `_bmad/_config/bmad-help.csv` plus `references/command-catalog.md` to choose the correct command.
3. Distinguish workspace coordination from repo-local delivery before recommending a command.
4. Prefer the smallest command that moves the user forward without skipping required gates.
5. When routing is ambiguous, recommend `/bmad-help` or the exact BMAD slash command that fits the current phase.

## References

- Read `references/command-catalog.md` when you need the current shipped command surface.
- Read `_bmad/tools/automation/README.md` only if the user asks for automation or orchestration.
