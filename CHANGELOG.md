# Changelog

All notable changes to `compass-engine` are documented here.

## [Unreleased]

### Added

- GitHub Actions workflow templates and drift exclusion (`chore(ci)`)
- BMAD usage decision tree with scale-adaptive levels
- 8 developer-facing BMAD documentation guides
- Comprehensive BMAD method documentation
- bmad-compass-workflow-map skill
- Unit and integration test job to quality-checks workflow
- Integration test running full build cycle against real source
- Filesystem tests for build, push, and validate tools
- Pure function tests for build, push, and validate
- Test infrastructure and exported internal functions for testing
- Phase 5: auto-generate client skill directories from skill manifest
- Phase 4: auto-generated manifests replace hand-maintained CSVs
- Phase 3: compass-skills module and old-format removal
- Phase 2: Compass agent overrides in skill format
- Phase 1: migrate native modules to v6.2.2 skill format
- BMAD src audit fixes: excalidraw, agent renames, agent docs
- Optional whitepaper ingestion to BMAD analysis phase
- Optional oversight substrate for BMAD
- Validation updates for skill-based client bundles

### Changed

- Split `linting.yml` monolith into `lint-core.yml` and `lint-languages.yml`
- Updated orchestrator agents and codex prompts for skill-based bundles
- Updated bmad-method and bmad-automation skills for skill-based bundles
- Removed sync-client-bundles.js -- client skills now auto-generated at build time
- Removed old command directories -- replaced by auto-generated client skills
- Copy root-level BMAD assets generically instead of special-casing
- Tightened 5 BMAD workflow behaviors for delivery-repo accuracy
- CI/CD trim: drift-exclude, lint split, zero-cost detect
- BMAD workflow hygiene and OpenCode plugin smoke tests

### Fixed

- GITHUB_OUTPUT redirects grouping in lint-languages detect step
- Em-dash style and link format normalization in BMAD docs
- 0-governance added to allowed phase values
- Inaccuracies found during docs review
- Missing supporting lanes in workflow map
- CI sync for quality-checks.yml
- Excluded test/ from secret scan, fixed plan heading levels
- package.json indentation correction
- Init-planning oversight scaffold made a distinct step
- Template variable substitution note added to init step reports
- create-architecture alignment with repo identity and brief discovery
- BMAD src audit followup findings
