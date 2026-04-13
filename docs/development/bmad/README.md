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

## Usage & Integration

- [When to Use BMAD](./when-to-use-bmad.md) — decision tree for choosing the right approach and scale-adaptive levels
- [Quick-Spec & Quick-Dev](./quick-spec-quick-dev.md) — fast-path workflows and when to use them
- [Project Context](./project-context.md) — the project-context.md artifact and its role
- [Automation Wrappers](./automation-wrappers.md) — developer guide for automation orchestration layer
- [Beads Integration](./beads-integration.md) — how Beads integrates with BMAD lifecycle
- [Extension Modules](./extension-modules.md) — TEA, CIS, WDS, and CYBERSEC reference
- [Agent Conflict Prevention](./agent-conflict-prevention.md) — preventing conflicts in polyrepo context
- [Advanced Techniques](./advanced-techniques.md) — elicitation, adversarial review, and refinement loops
- [Script Replacement](./script-replacement.md) — strategy for replacing workflow steps with scripts
