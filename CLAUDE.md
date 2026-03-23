# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project: Compass Engine

**Description:** Central development tools repository for all Compass Brand projects. Contains BMAD customizations, Claude Code configuration, workflow tooling, and distribution tooling.

**Project Type:** development-tools

---

## Repository Contents

This repository serves as the central hub for Compass Brand development tools:

- **BMAD-METHOD/** - Core BMAD methodology (upstream submodule)
- **reference/** - Framework, provenance, research, and audit context that does not ship
- **src/** - Active shipped source bundles for Compass Engine
- **dist/** - Built output ready for distribution
- **tools/** - Maintainer build, push, validation, and scaffolding scripts
- **\_bmad-output/** - BMAD runtime artifacts and custom creations
- **docs/** - Documentation and guides

## Working Rule

- update shipped assets in `src/`
- keep `reference/` limited to workflow/framework reference, provenance, and research
- do not build new runtime behavior in `reference/`
- when build or push behavior changes, update `tools/` and the matching `src/` surfaces together

## What is BMAD?

BMAD (Breakthrough Method of Agile AI-Driven Development) is a structured methodology for AI-assisted software development.

---

## Tech Stack

| Layer         | Technology   |
| ------------- | ------------ |
| Documentation | Markdown     |
| Automation    | Python, Bash |
| Testing       | pytest       |

---

## Development Methodology: TDD

All functional code MUST follow Test-Driven Development.

```text
RED -> GREEN -> REFACTOR
```

---

## Git Discipline (MANDATORY)

**Commit early, commit often.**

- Commit after completing any file creation or modification
- Maximum 15-20 minutes between commits
- Use conventional commit format: `type: description`

Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`
