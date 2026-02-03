# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project: Compass Engine

**Description:** Central development tools repository for all Compass Brand projects. Contains BMAD customizations, Claude Code configuration, workflow scripts, and distribution tooling.

**Project Type:** development-tools

---

## Repository Contents

This repository serves as the central hub for Compass Brand development tools:

- **BMAD-METHOD/** - Core BMAD methodology (upstream submodule)
- **src/** - Source files for Claude Code configuration and BMAD customizations
- **dist/** - Built output ready for distribution
- **scripts/** - Build, distribution, and workflow automation
- **_bmad-output/** - BMAD runtime artifacts and custom creations
- **docs/** - Documentation and guides

## What is BMAD?

BMAD (Breakthrough Method of Agile AI-Driven Development) is a structured methodology for AI-assisted software development.

---

## Tech Stack

| Layer         | Technology    |
| ------------- | ------------- |
| Documentation | Markdown      |
| Automation    | Python, Bash  |
| Testing       | pytest        |

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
