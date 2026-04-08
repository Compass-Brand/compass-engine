# Script Replacement for BMAD Workflow Steps

## What Script Replacement Is

Script replacement is the idea of identifying individual steps within BMAD workflows that could be replaced by deterministic code (scripts) instead of requiring AI interpretation at runtime. The goal is to swap AI-driven steps that perform predictable, structured operations with scripts that accept inputs and produce structured outputs without consuming LLM context tokens.

For example, a workflow step that scans a directory for files and presents them as a numbered menu could be handled by a short script rather than by an AI agent reading and interpreting the same directory listing every time.

## Why It Matters

BMAD workflows run inside AI agent sessions where every step consumes context tokens. Predictable operations — file scanning, template rendering, structured data transformation, status aggregation — do not benefit from AI reasoning. Replacing those steps with deterministic scripts would:

- Reduce token consumption per workflow run
- Make repeatable steps faster and more consistent
- Free context budget for the steps that genuinely need AI reasoning

This motivation is directly aligned with the [context budgeting policy](../../../src/bmad/tools/automation/policies/context-budgeting.md) used by the automation wrappers, which already enforces minimum-context loading per command.

## Current Status: Aspirational, Not Implemented

The concept exists as a single 29-line prompt file at `src/bmad/tools/prompts/bmad-scripts.md`. An identical copy lives in `reference/BMAD/tools/prompts/bmad-scripts.md`, confirming it originates from the upstream BMAD method.

The prompt instructs an AI agent to:

1. Scan the custom modules folder and present available modules as a menu
2. Walk through the selected module workflows step by step, analyzing each step for script-replacement candidates

That is the entire specification. There are:

- **No script implementations** — no `.py`, `.sh`, `.js`, or `.ts` files exist under `src/bmad/tools/`
- **No script replacement tracking** — no registry, manifest, or status file records which steps have been analyzed or replaced
- **No workflow references** — no workflow, skill, or module references the bmad-scripts prompt as part of its execution
- **No integration with automation wrappers** — the automation layer in `src/bmad/tools/automation/` does not reference script replacement

The concept has not progressed beyond its original prompt definition.

## Relationship to Automation Wrappers

Automation wrappers and script replacement address the same underlying problem (reducing AI overhead in repeatable operations) but at different levels:

| Layer | Automation Wrappers | Script Replacement |
| --- | --- | --- |
| Scope | Orchestrate entire workflow phases | Replace individual workflow steps |
| Status | Fully specified, spec-only contracts | 29-line aspirational prompt |
| Approach | Wrap workflows with state, approvals, context policies | Swap AI steps with deterministic code |
| State model | YAML-based machine state with structured approval gates | Not defined |
| Context savings | Achieved through minimum-context loading policies | Would achieve through eliminating AI from predictable steps |

If script replacement were implemented, it would logically sit beneath the automation wrappers. A wrapper like `auto-story` could invoke a deterministic script for its reuse scan step instead of asking the AI to perform the scan, for example.

However, the automation wrapper specs do not reference or depend on script replacement. The two concepts developed independently.

## Which Steps Would Be Candidates

Based on the intent described in `bmad-scripts.md` and the structure of existing workflows, likely candidates for script replacement would be steps that:

- Scan directories and present menus (e.g., module/workflow selection)
- Aggregate file metadata into structured summaries
- Render templates with known variables
- Transform one structured format to another (YAML to markdown, CSV to table)
- Check file existence or validate artifact structure
- Collect status from multiple state files into a combined report

Steps that should remain AI-driven include those requiring judgment, synthesis, analysis of ambiguous requirements, or creative generation.

## If This Concept Were Pursued

The path to implementation would likely involve:

1. **Analysis pass**: Use the bmad-scripts prompt to systematically identify candidate steps across active modules
2. **Prioritization**: Rank candidates by frequency of execution and token cost
3. **Implementation**: Write scripts (likely Python, consistent with the repo's automation stack) that accept the same inputs and produce the same structured outputs as the AI-driven steps
4. **Integration**: Modify workflow step definitions to invoke scripts instead of AI prompts for replaced steps
5. **Registry**: Maintain a manifest of which steps have been replaced and which remain AI-driven

This work would need to coordinate with the automation wrapper specs if both are pursued, to avoid building two separate optimization systems for the same workflows.

## Assessment

Script replacement is an **aspirational concept** that has not been actively developed. The upstream BMAD method included it as a prompt for future exploration, and Compass Engine carried the file forward without building on it.

The automation wrappers have since addressed the same core concern (reducing AI overhead for repeatable operations) through a more comprehensive approach: structured state management, context budgeting policies, and deterministic orchestration contracts. Those wrappers do not eliminate AI from individual steps, but they sharply reduce how much context each step consumes.

If individual step replacement becomes valuable in the future, it would complement the automation wrappers rather than compete with them. For now, the automation wrapper layer is the active investment area for workflow efficiency.

## Reference

| Resource | Path |
| --- | --- |
| Script replacement prompt | `src/bmad/tools/prompts/bmad-scripts.md` |
| Upstream copy | `reference/BMAD/tools/prompts/bmad-scripts.md` |
| Automation wrappers doc | `docs/development/bmad/automation-wrappers.md` |
| Automation specs | `src/bmad/tools/automation/` |
| Context budgeting policy | `src/bmad/tools/automation/policies/context-budgeting.md` |
