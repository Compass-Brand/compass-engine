---
name: tdd-workflow
description: Enforce Test-Driven Development practices with the RED-GREEN-REFACTOR cycle
---

# TDD Workflow

## Purpose

Enforce Test-Driven Development practices with the RED-GREEN-REFACTOR cycle.

## Core Principles

### Interface-First Design

- Define interfaces/types before implementation
- Consider edge cases upfront
- Design for testability

### RED Phase

1. Write a failing test for the next piece of functionality
2. Run the test to verify it fails
3. **Verify it fails for the RIGHT reason** (not syntax errors, import issues)
4. The test defines expected behavior

### GREEN Phase

1. Write the MINIMAL code to make the test pass
2. Don't add extra functionality
3. Code quality doesn't matter yet
4. Just make it work

### REFACTOR Phase

1. Improve code without changing behavior
2. Remove duplication
3. Improve naming
4. Extract methods/functions as needed
5. **Tests must still pass after refactoring**

## Coverage Targets

- **Required**: 100% for all functional code
- Security-sensitive and critical paths must have comprehensive edge case coverage

## Framework Commands

### JavaScript/TypeScript (Jest)

```bash
npm test                    # Run all tests
npm test -- --coverage      # With coverage
npm test -- --watch         # Watch mode
npm test -- path/to/file    # Single file
```

### Python (pytest)

```bash
pytest                      # Run all tests
pytest --cov               # With coverage
pytest -v                  # Verbose
pytest path/to/test.py     # Single file
```

### Go

```bash
go test ./...              # Run all tests
go test -cover ./...       # With coverage
go test -v ./...           # Verbose
go test ./path/to/pkg      # Single package
```

## Test File Organization

- Tests live alongside source or in `tests/` directory
- Name pattern: `*.test.ts`, `*_test.py`, `*_test.go`
- One test file per source file
- Group related tests with describe/context blocks

## Anti-Patterns to Avoid

- Writing tests after implementation
- Testing implementation details (not behavior)
- Large test setups with many dependencies
- Tests that depend on external services
- Skipped tests without documented reason

## Integration with tdd-guide Agent

This skill provides the methodology; the tdd-guide agent enforces it during code changes.
