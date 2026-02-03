# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project: BMAD Engine

**Description:** BMAD methodology automation engine - customized BMAD Method for Compass Brand AI-assisted development workflows.

**Project Type:** methodology

---

## What is BMAD?

BMAD (Breakthrough Method of Agile AI-Driven Development) is a structured methodology for AI-assisted software development. This repository contains:

- **BMAD-METHOD/** - Core methodology documentation and templates
- **docs/** - Additional documentation and guides
- **plans/** - Project planning artifacts
- **reference/** - Reference materials and examples
- **scripts/** - Automation scripts for BMAD workflows
- **tests/** - Test suites for BMAD automation

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
