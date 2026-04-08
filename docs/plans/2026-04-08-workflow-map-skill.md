# Workflow Map Skill Design

## Summary

Create a self-contained Compass custom skill (`bmad-compass-workflow-map`) that presents the full ordered Compass BMAD workflow as a readable trail map. Registered in the help menu under code `WM`.

## Problem

- `BMAD-workflow.md` is the canonical ordering document but reads like a reference spec (495 lines of tables, routing rules, framework control rules)
- `bmad-help` is contextual and deliberately hides the full picture
- No way to ask "show me the entire workflow start to finish" and get a clean answer
- Steps that intentionally run twice (brainstorming, research, test design, secure gates) are not visually connected

## Design Decisions

- **Placement:** Compass custom skill at `src/bmad/modules/custom/compass-skills/anytime/bmad-compass-workflow-map/`
- **Menu code:** `WM` (Workflow Map)
- **Approach:** Self-contained authored content (not dynamic rendering of BMAD-workflow.md)
- **Repetitions:** Shown inline where they occur with `↩` callouts referencing the other pass
- **Scope:** What runs, in what order, what repeats. No routing rules or framework control rules.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Frontmatter + instruction to present workflow.md |
| `workflow.md` | The full ordered map |
| `module-help.csv` (update) | Registration row for WM menu code |

## Content Structure

1. Header + legend (Required/Optional/Conditional/Planned, callout notation)
2. Part A: Project-Level Setup (Sections 1-3, runs once)
3. Part B: Per-Phase Execution Loop (Sections 4-10, repeats per slice)
4. Required Spine checklist (14-step minimal progression)
5. Supporting Lanes summary (anytime/utility skills)

## Step Format

Tables with columns: #, Step, Command, Gate. Repetition callouts on separate rows beneath the step. Blockquote intros per section. Loop boundaries marked with ↻.
