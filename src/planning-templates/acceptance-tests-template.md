# Acceptance Tests: [Epic Title]

**Epic ID:** [REPO]-EPIC-[XXX]

**Created:** YYYY-MM-DD

**Last Updated:** YYYY-MM-DD

> **TDD Requirement:** These acceptance tests must be written BEFORE implementation begins.
> They serve as the specification for what "done" means.

## Overview

[Brief description of the epic and what these tests validate]

## Test Format

All acceptance tests follow the Given-When-Then format:

- **Given:** The preconditions and context
- **When:** The action or event
- **Then:** The expected outcome

## Feature: [Feature Name]

### Scenario: [Scenario Name]

**Story Reference:** [Story ID]

**Priority:** P1 | P2 | P3

```gherkin
Given [precondition 1]
  And [precondition 2]
When [action is taken]
Then [expected outcome 1]
  And [expected outcome 2]
```

**Notes:** [Any clarifications or edge cases]

---

### Scenario: [Scenario Name]

**Story Reference:** [Story ID]

**Priority:** P1

```gherkin
Given [precondition]
When [action]
Then [outcome]
```

---

## Feature: [Feature Name]

### Scenario: [Happy Path]

**Story Reference:** [Story ID]

**Priority:** P1

```gherkin
Given [normal conditions]
When [standard action]
Then [expected success outcome]
```

### Scenario: [Error Handling]

**Story Reference:** [Story ID]

**Priority:** P1

```gherkin
Given [error condition]
When [action that should fail]
Then [appropriate error response]
  And [system remains stable]
```

### Scenario: [Edge Case]

**Story Reference:** [Story ID]

**Priority:** P2

```gherkin
Given [edge case condition]
When [action]
Then [handled gracefully]
```

---

## Feature: [Feature Name]

### Scenario Outline: [Parameterized Test]

**Story Reference:** [Story ID]

**Priority:** P1

```gherkin
Given [precondition with <parameter>]
When [action with <input>]
Then [outcome with <expected>]

Examples:
  | parameter | input | expected |
  | value1    | a     | result1  |
  | value2    | b     | result2  |
  | value3    | c     | result3  |
```

---

## Non-Functional Requirements

### Performance

```gherkin
Given the system is under normal load
When a user performs [action]
Then the response time is less than [X]ms
```

### Security

```gherkin
Given an unauthenticated user
When they attempt to access [protected resource]
Then they receive a 401 Unauthorized response
  And no sensitive data is exposed
```

### Accessibility

```gherkin
Given a user using a screen reader
When they navigate to [page/component]
Then all interactive elements are properly labeled
  And focus order is logical
```

---

## Test Coverage Matrix

| Scenario | Unit | Integration | E2E | Manual |
|----------|------|-------------|-----|--------|
| [Scenario 1] | ✓ | ✓ | ✓ | |
| [Scenario 2] | ✓ | ✓ | | |
| [Scenario 3] | ✓ | | | ✓ |

## Sign-off

- [ ] All scenarios reviewed by Product Owner
- [ ] All scenarios have corresponding test implementations
- [ ] Edge cases identified and documented
- [ ] Non-functional requirements included

**Approved by:** [Name] on YYYY-MM-DD

## References

- [Test Plan](./test-plan.md)
- [Epic Definition](../epic-definition.md)
- [Story Files](../stories/)
