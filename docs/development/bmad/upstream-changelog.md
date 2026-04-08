# BMAD-METHOD Upstream Changelog

Last reviewed: 2026-04-08

Release history for the upstream [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) project. This documents the evolution of the framework that Compass Engine extends.

## v6.2.2 (March 26, 2026) — Current

- Module-help CSV modernized to 13-column format with `after`/`before` dependency graph (replacing sequence numbers)
- bmad-help rewritten from procedural 8-step to outcome-based skill design (~50% shorter)
- bmad-builder module-definition path updated for v1.2.0 compatibility

## v6.2.1 (March 24, 2026)

- Qoder and Ona platform support
- Conformant agent skills; agents inlined capabilities, removed bmad-manifest.json
- Quick Dev Review Trail generation
- Deterministic skill validator for CI
- Installer discovers skills by SKILL.md instead of manifest YAML
- Removed legacy workflow/task/agent IDE generators and dead agent compilation pipeline
- Complete French (fr) translation
- Phase-based skill directory consolidation (60+ PRs merged)

## v6.2.0 (March 15, 2026) — Native Skill Conversion

All remaining workflows converted to native skill packages: `advanced-elicitation`, `create-story`, `quick-dev`, `domain-research`, `dev-story`, `create-product-brief`, `create-ux-design`, `create-architecture`, `check-implementation-readiness`, `code-review`, `create-epics-and-stories`, `retrospective`, `correct-course`, `sprint-planning`, `qa-generate-e2e-tests`, `sprint-status`, `technical-research`, `document-project`, `generate-project-context`, `quick-spec`, `edit-prd`, `create-prd`, `validate-prd`, `market-research`.

- Inference-based skill validator tool
- Code review rewritten with sharded step-file architecture
- Product brief skill prototype preview

## v6.1.0 (March 13, 2026) — Everything Is a Skill

The biggest architectural overhaul since v6 stable:

- **Skills-based architecture:** Every workflow, agent, and task installs as a unified skill with `SKILL.md` entrypoints
- All core workflows converted from YAML/XML to clean markdown
- Legacy workflow engine removed
- All 15 platforms migrated to native Agent Skills format
- Edge Case Hunter as parallel code review layer in Phase 4
- Experimental Quick Dev preview (future Phase 4 development tool)
- Pi coding agent platform support
- `@next` install channel for tip-of-main
- npm package 91% smaller (6.2 MB down to 555 KB)
- Full Chinese (zh-CN) documentation translation
- 75 commits, 61 PRs, 306 files changed

## v6.0.4 (March 2026)

- Edge Case Hunter review task for boundary condition analysis
- Brainstorming session persistence fix
- `{project-root}` path syntax replacing legacy `@` prefixes

## v6.0.3 (March 2026)

- Root cause analysis skill (`bmad-os-root-cause-analysis`)
- OpenCode integration fixes
- Rebranded acronym to "Build More Architect Dreams"

## v6.0.2 (February 2026)

- CodeBuddy platform, LLM audit prompt
- Codex `.agents/skills` format migration
- bmad-os skills with slash commands
- Fixed 104 broken file references across 68 files
- Removed Windsurf from recommended IDEs

## v6.0.1 (February 2026)

- Minor fixes post-stable release

## v6.0.0 (February 17, 2026) — Stable

Stable release of the v6 rewrite:

- `bmad uninstall` command (interactive + non-interactive)
- Dedicated GitHub Copilot installer
- PRD workflow enhancements (vision/differentiators, executive summary steps)
- Semantic version comparison fixes
- Auto-discover PRD files in validate-prd

## v6.0.0-beta (January – February 2026)

- Beta.8: Non-interactive installation for CI/CD (10 new CLI flags), CSV file reference validation, Kiro IDE support
- Beta.7: Direct workflow invocation via slash commands, version checking CLI
- Beta.6: Cross-File Reference Validator (~483 references across ~217 files), Windows CRLF fixes
- Beta.5: Generate-project-context workflow, market research customer analysis sharding
- Beta.0–Beta.4: SDET module replacing TEA, Gemini CLI TOML support, YAML parsing fixes

## v6.0.0-alpha (September 2025 – January 2026)

Complete rewrite from v4:

- **Lean Core:** Simple common tasks + common agents (bmad-web-orchestrator, bmad-master)
- **BMad Method (BMM) module:** Full scale-adaptive rewrite; scales from small enhancements to massive multi-service systems
- **BMad Builder (BoMB):** Automates creation/conversion of expansion packs, modules, workflows, agents
- **Creative Intelligence Suite (CIS):** New module for creative work
- Alpha.4: 18 documentation guides (7,000+ lines), Quick Spec Flow, intent-driven workflows, 14 domain complexity types
- Alpha.6: Closed 54 legacy v4 issues
- Alpha.7: Web bundle support for BMM module, workflow vendoring system

## v5.0.0 — Skipped

Version 5 was skipped due to NPX registry corruption issues. Development jumped to v6.

## v4.0.0 (June 2025) — Professional Framework

Complete architectural overhaul from prompt collection to distributable framework:

- NPM package distribution via `npx bmad-method install`
- Modular architecture with `.bmad-core` hidden folder structure
- Multi-IDE support: Claude Code, Cursor, Roo, Windsurf, and more
- YAML-based agent and team definitions
- Expansion pack architecture for domain specialization
- Brownfield and greenfield project workflows
- Document sharding for context management

Notable v4.x releases:

- v4.10: Configuration system, debug logging
- v4.20: QA agent elevated to senior code reviewer, quality gates
- v4.30: Claude Code slash commands, Windows compatibility, Unity 2D game dev expansion
- v4.43: Codex CLI/Web, Augment Code, iFlow CLI, Godot game dev, AGENTS.md auto-generation, fork-friendly CI/CD

## v3.0.0 (May 2025) — The Orchestrator

- BMad Orchestrator — single uber-agent orchestrating all specialized agents
- Web-first approach with pre-compiled agent bundles
- Build system for web agents
- `/help` command system
- Brainstorming and ideation support

## v2.0.0 (April 2025) — Separation of Concerns

- Templates decoupled from agent definitions
- Quality checklists for document validation
- Web agent support for Gemini Gems and Custom GPTs
- Granular web agents with simplified roles

## v1.0.0 (April 2025) — The Origin

The original tech demo. Specialized AI agent personas (PM, Architect, Developer) with template-based document generation. Hard-coded custom mode prompts baked into agent configs.

## Module Ecosystem

| Module | Code | Introduced | Status |
| --- | --- | --- | --- |
| BMad Method (BMM) | bmm | v6.0.0-alpha | Active (core) |
| Core Skills | core | v6.0.0-alpha | Active (core) |
| BMad Builder (BoMB) | bmad-builder | v6.0.0-alpha | Active |
| Creative Intelligence Suite (CIS) | cis | v6.0.0-alpha | Active |
| BMad Game Dev Studio (BMGD) | bmgd | v4.30 (extracted alpha.7) | Active |
| Whiteport Design Studio (WDS) | wds | v6.1.0 | Active |
| Test Engineering & Automation (TEA) | tea | v6.0.0-beta.0 (SDET → TEA) | External |
| Cybersecurity (CYBERSEC) | cybersec | Compass extension | Compass-only |

## Platform Support Timeline

| Version | Platforms Added |
| --- | --- |
| v1.0 | Custom mode prompts (manual) |
| v2.0 | Gemini Gems, Custom GPTs |
| v4.0 | Claude Code, Cursor, Roo, Windsurf |
| v4.20 | Cline, Gemini CLI |
| v4.30 | Claude Code slash commands |
| v4.43 | Codex CLI/Web, Augment Code, iFlow CLI |
| v6.0.0 | GitHub Copilot |
| v6.0.2 | CodeBuddy |
| v6.0.0-beta.8 | Kiro |
| v6.1.0 | Pi |
| v6.2.0 | (skill conversion complete) |
| v6.2.1 | Qoder, Ona |
