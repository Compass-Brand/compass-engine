# OpenCode Plugin Development

`src/opencode/plugins/` is the dedicated source location for Compass OpenCode plugin development.

Rules:

- Treat each plugin as its own folder under `src/opencode/plugins/`.
- Keep implementation metadata and documentation with the plugin folder.
- Keep OpenCode command/agent wrappers in `src/opencode/commands/` and `src/opencode/agents/`.

Recommended structure:

```text
src/opencode/plugins/
  compass-beads.ts
  compass-bmad/
    README.md
    plugin.yaml
    commands/
    providers/
    tests/
```

If a plugin should auto-load from downstream `.opencode/plugins/`, add a top-level JS/TS entry shim in `src/opencode/plugins/` and keep the implementation assets in a matching folder beside it.

If a local plugin imports external packages, declare them in `src/opencode/package.json` so the downstream `.opencode/package.json` can trigger OpenCode's Bun install on startup.
