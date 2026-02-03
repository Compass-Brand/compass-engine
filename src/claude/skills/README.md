# Claude Skills Index

Skills provide specialized capabilities and domain knowledge for Claude Code.

## Available Skills

| Skill                                                   | Description                                                               |
| ------------------------------------------------------- | ------------------------------------------------------------------------- |
| [agent-builder-skill](./agent-builder-skill/)           | Expert guidance on designing and building Claude Code subagents           |
| [coding-standards](./coding-standards/)                 | Language-specific coding standards for TypeScript, Python, and PowerShell |
| [creating-skills-skill](./creating-skills-skill/)       | Guidance for creating new Claude Code skills                              |
| [instincts](./instincts/)                               | Capture patterns and corrections, graduate to skills                      |
| [pr-fix-patterns](./pr-fix-patterns/)                   | Query memory for PR review fix patterns                                   |
| [reflect](./reflect/)                                   | Intelligent learning system for capturing session learnings               |
| [security-review](./security-review/)                   | OWASP Top 10, dependency auditing, secret scanning                        |
| [serena-code-architecture](./serena-code-architecture/) | Architectural analysis using Serena symbols                               |
| [strategic-compact](./strategic-compact/)               | Generate handoff documents before context limits                          |
| [tdd-workflow](./tdd-workflow/)                         | Enforce RED-GREEN-REFACTOR TDD cycle                                      |
| [using-forgetful-memory](./using-forgetful-memory/)     | Query and save to Forgetful semantic memory                               |
| [using-serena-symbols](./using-serena-symbols/)         | LSP-powered symbol analysis                                               |
| [verification-loop](./verification-loop/)               | Verify changes before marking complete                                    |

## Skill Structure

Each skill directory contains:

- `SKILL.md` - Main skill definition with frontmatter
- Optional: `reference.md`, `examples.md`, `scripts/`

## Usage

Skills are automatically loaded based on context. Reference skill descriptions when working in related areas.
