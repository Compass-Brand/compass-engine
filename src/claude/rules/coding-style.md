# Coding Style Rules

## Immutability

- Prefer `const` over `let` in JavaScript/TypeScript
- Use `readonly` for class properties that should not change
- Avoid mutating function arguments; return new values instead

## File and Function Size

- Maximum file size: 300 lines
- Maximum function size: 50 lines
- These limits are soft guidelines to promote readability, maintainability, and testability. Exceptions are acceptable for generated code, small single-purpose utilities, and performance-critical modules.
- If a file or function exceeds limits, refactor into smaller units

## Naming Conventions

- JavaScript/TypeScript: `camelCase` for variables and functions, `PascalCase` for classes
- Python: `snake_case` for variables and functions, `PascalCase` for classes
- Constants: `UPPER_SNAKE_CASE`
- Use descriptive names that convey intent

> **Note:** This is a high-level summary. See language-specific files in `src/claude/skills/coding-standards/` (typescript.md, python.md, powershell.md) for detailed guidance.

## Design Principles

- Single Responsibility Principle: each function/class does one thing well
- DRY (Don't Repeat Yourself): extract common logic into reusable functions
- KISS (Keep It Simple, Stupid): prefer simple solutions over clever ones
- Favor composition over inheritance

## Code Organization

- Group related functionality together
- Place imports at the top of files, organized by type
- Export public API explicitly; keep implementation details private
- Use consistent file structure across the project
