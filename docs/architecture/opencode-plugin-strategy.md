# OpenCode Plugin Strategy (BMAD-Aligned)

Last reviewed: 2026-02-23

## Goal

Create a Compass Brand OpenCode plugin that exposes BMAD workflows as first-class commands while staying compatible with Claude and Codex conventions.

## Scope for v1

1. Provide OpenCode commands that map to BMAD workflow entry points.
2. Reuse shared prompt/skill content where possible (single source, generated adapters).
3. Support beads-aware session lifecycle hooks (`bd prime`, status updates, close protocol reminders).
4. Emit normalized artifacts in standard downstream project locations.

## Current Architecture

Implementation root: `src/opencode/plugins/`

Active plugins (each a standalone TypeScript entry with a matching sub-directory):

- `compass-beads` - Beads integration wrapper
- `compass-handoff` - Structured agent/human handoff
- `compass-type-inject` - Type injection for OpenCode
- `compass-worktree` - Git worktree management

Supporting surfaces:

- `src/opencode/agents/` - OpenCode agent definitions (e.g., `bmad-orchestrator.md`)
- BMAD client skills are auto-generated at build time from `skill-manifest.csv` into `dist/.opencode/skills/`

## Integration Points

- Inputs: `.opencode/agents/*`, BMAD module metadata, `skill-manifest.csv`
- Outputs: downstream planning artifacts (`planning/` in target repos)
- Tracking: `bd` issue lifecycle hooks

## Delivery Plan

1. Inventory existing OpenCode command surface and classify by BMAD phase.
2. Build command registry schema and plugin manifest.
3. Implement two pilot BMAD commands (`create-prd`, `dev-story`) through plugin dispatch.
4. Add cross-tool parity tests (OpenCode command => same artifact behavior as Claude/Codex path).
5. Expand to full command set.

## Guardrails

- No hardcoded secrets.
- Keep upstream BMAD untouched; plugin references custom modules from `src/bmad/modules`.
- Enforce deterministic artifact paths.
