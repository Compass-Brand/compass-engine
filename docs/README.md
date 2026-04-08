# Compass Engine Documentation

Last reviewed: 2026-04-08

Central documentation for the Compass Engine tooling source.

This repo owns this top-level index. The shipped Compass documentation bundle only manages:

- `docs/human/`
- `docs/ai/`
- `docs/BMAD-integration.md`

BMAD deep reference documentation is maintained upstream in `BMAD-METHOD/docs/`.

## Quick Links

| I want to...                                     | Read this                                                                   |
| ------------------------------------------------ | --------------------------------------------------------------------------- |
| Install and run build/push                       | [Getting Started](./getting-started/installation.md)                        |
| Understand build outputs                         | [Build Process](./architecture/build.md)                                    |
| Understand multi-target sync                     | [Sync Architecture](./architecture/sync.md)                                 |
| See Compass-wide GitHub standardization baseline | [GitHub Standardization](./architecture/github-standardization.md)          |
| Enable and troubleshoot CodeQL scanning          | [Linting and Security Gates](./development/linting-and-security.md)         |
| Understand day-to-day development in this repo   | [Development Model](./development/how-we-work.md)                           |
| Understand the BMAD method and architecture      | [BMAD Overview](./development/bmad/bmad-overview.md)                        |
| Create new BMAD skills (workflows and agents)    | [Creating Skills](./development/bmad/creating-skills.md)                    |
| Create new BMAD modules                          | [Creating Modules](./development/bmad/creating-modules.md)                  |
| Build custom BMAD modules                        | [Custom BMAD Modules](./development/bmad/custom-modules.md)                 |
| Modify BMAD customizations                       | [Modifying BMAD](./development/bmad/modifying-bmad.md)                      |
| Review BMAD upstream release history             | [Upstream Changelog](./development/bmad/upstream-changelog.md)              |
| Understand the Compass docs control plane        | [BMAD Integration](./BMAD-integration.md)                                   |

## Bundles Managed by This Repo

- `.claude`
- `.codex`
- `.opencode`
- `.github`
- `_bmad`
- `planning`
- `docs/human`
- `docs/ai`
- `docs/BMAD-integration.md`
