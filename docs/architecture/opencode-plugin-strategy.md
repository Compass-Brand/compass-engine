# OpenCode Plugin Strategy (BMAD-Aligned)

Last reviewed: 2026-02-23

## Goal

Create a Compass Brand OpenCode plugin that exposes BMAD workflows as first-class commands while staying compatible with Claude and Codex conventions.

## Scope for v1

1. Provide OpenCode commands that map to BMAD workflow entry points.
2. Reuse shared prompt/skill content where possible (single source, generated adapters).
3. Support beads-aware session lifecycle hooks (`bd prime`, status updates, close protocol reminders).
4. Emit normalized artifacts in standard downstream project locations.

## Proposed Architecture

- `plugin-core`: workflow registry + command dispatcher
- `provider-bmad`: adapters for BMAD modules/workflows
- `provider-tracking`: beads integration wrapper
- `provider-interop`: bridges for Claude/Codex command parity

Implementation root in this repo:
- `src/opencode/plugins/`

## Integration Points

- Inputs: `.opencode/command/*`, `.opencode/agent/*`, BMAD module metadata
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
