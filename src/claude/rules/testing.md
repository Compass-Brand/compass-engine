# Testing Rules

## TDD Cycle (Mandatory)

- RED: Write a failing test first
- GREEN: Write minimal code to make the test pass
- REFACTOR: Clean up while keeping tests green
- Never write production code without a failing test

## Coverage Requirements

- Baseline minimum: 80% code coverage (individual repos may enforce stricter requirements via their CLAUDE.md files)
- Critical paths require 100% coverage
- Coverage reports must be reviewed before merging

## Test Discipline

- No skipped tests without a documented reason and tracking issue
- All tests must pass before committing
- Tests must be deterministic (no flaky tests)
- Clean up test data and state between tests

## Test Naming

- Use descriptive names that explain the scenario and expected outcome
- Format: `should_<expected_behavior>_when_<condition>`
- Group related tests with descriptive describe/context blocks

## Test Quality

- Test behavior, not implementation details
- Each test should verify one specific behavior
- Use meaningful assertions with clear error messages
- Avoid testing framework or library internals
