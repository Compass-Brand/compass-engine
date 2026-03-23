# OpenCode Plugin Development

`src/opencode/plugins/` is the dedicated source location for Compass OpenCode plugin development.

Rules:

- Treat each plugin as its own folder under `src/opencode/plugins/`.
- Keep implementation metadata and documentation with the plugin folder.
- Keep OpenCode command/agent wrappers in `src/opencode/commands/` and `src/opencode/agents/`.

Recommended structure:

```text
src/opencode/plugins/
  compass-bmad/
    README.md
    plugin.yaml
    commands/
    providers/
    tests/
```
