# BMAD Docs

Last reviewed: 2026-04-08

Documentation for the Compass BMAD method integration, customization, and extension.

Current working rule:

- use `src/bmad/` for shipped Compass BMAD source
- keep `src/planning/` aligned when workflow outputs or artifact paths change
- use `reference/` only for retained workflow/framework context, provenance, and research

## Guides

- [BMAD Overview](./bmad-overview.md) — what BMAD is, architecture, key concepts, and the 4-phase methodology
- [Creating Skills](./creating-skills.md) — how to create new workflow and agent skills
- [Creating Modules](./creating-modules.md) — how to create new BMAD modules with the build system
- [Custom Modules](./custom-modules.md) — Compass module principles and current active modules
- [Modifying BMAD](./modifying-bmad.md) — extending BMAD without forking upstream
- [Upstream Changelog](./upstream-changelog.md) — BMAD-METHOD release history (v1.0.0 through v6.2.2)
