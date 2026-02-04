# Test Plan: [Epic Title]

**Epic ID:** [REPO]-EPIC-[XXX]

**Created:** YYYY-MM-DD

**Last Updated:** YYYY-MM-DD

**Owner:** [QA Lead / Tech Lead]

## Overview

[Brief description of what this epic delivers and the testing approach]

## Test Strategy

### Testing Levels

| Level | Coverage Target | Approach |
|-------|-----------------|----------|
| Unit | ≥ 80% | [Framework, patterns] |
| Integration | ≥ 70% | [Approach] |
| E2E | Critical paths | [Tools, scope] |
| Performance | Benchmarks | [Tools, thresholds] |

### Test Frameworks

- **Unit Tests:** [Jest, Pytest, etc.]
- **Integration Tests:** [Framework]
- **E2E Tests:** [Playwright, Cypress, etc.]
- **Performance:** [k6, Artillery, etc.]

## Test Scope

### In Scope

- [Feature/component 1 to test]
- [Feature/component 2 to test]
- [Integration point to test]

### Out of Scope

- [What won't be tested and why]
- [Deferred testing items]

## Test Cases by Story

### Story: [Story ID] - [Title]

| Test ID | Description | Type | Priority |
|---------|-------------|------|----------|
| TC-001 | [Test description] | Unit | P1 |
| TC-002 | [Test description] | Integration | P1 |
| TC-003 | [Test description] | E2E | P2 |

### Story: [Story ID] - [Title]

| Test ID | Description | Type | Priority |
|---------|-------------|------|----------|
| TC-004 | [Test description] | Unit | P1 |

## TDD Requirements

### RED Phase Requirements

Before any implementation:

1. [ ] All acceptance tests translated to executable tests
2. [ ] Unit test stubs written for all components
3. [ ] Integration test scenarios defined
4. [ ] Tests must FAIL (proving they test real behavior)

### GREEN Phase Requirements

During implementation:

1. [ ] Write minimal code to pass each test
2. [ ] No skipped tests
3. [ ] All tests pass before moving to next feature

### REFACTOR Phase Requirements

After tests pass:

1. [ ] Code cleaned up without breaking tests
2. [ ] Tests remain green throughout refactoring
3. [ ] No decrease in coverage

## Test Data

### Test Data Requirements

- [Data requirement 1]
- [Data requirement 2]

### Test Data Strategy

- [ ] Fixtures in `__fixtures__/` directory
- [ ] Factory functions for dynamic data
- [ ] Seeded database for integration tests
- [ ] Mock external services

## Test Environment

### Local Development

- [Required setup]
- [Environment variables]

### CI/CD

- [Pipeline stages]
- [Parallelization strategy]

## Performance Criteria

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| API Response Time | < 200ms | < 500ms |
| Page Load Time | < 2s | < 4s |
| Memory Usage | < 512MB | < 1GB |

## Security Testing

- [ ] Input validation tests
- [ ] Authentication/authorization tests
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Sensitive data handling

## Accessibility Testing

- [ ] WCAG 2.1 AA compliance
- [ ] Screen reader compatibility
- [ ] Keyboard navigation

## Test Execution

### Pre-Commit

- Lint checks
- Unit tests (affected files)

### Pre-Merge

- Full unit test suite
- Integration tests
- Security scans

### Post-Deploy (Staging)

- E2E smoke tests
- Performance benchmarks
- Manual exploratory testing

## Risk Areas

| Area | Risk Level | Mitigation |
|------|------------|------------|
| [Component] | High | [Extra testing approach] |
| [Integration] | Medium | [Approach] |

## Sign-off Criteria

This epic test plan is approved when:

- [ ] All stories have test cases defined
- [ ] Coverage targets agreed upon
- [ ] Test data strategy approved
- [ ] CI/CD integration confirmed
- [ ] Team reviewed and approved

**Approved by:** [Name] on YYYY-MM-DD

## References

- [Link to acceptance tests](./acceptance-tests.md)
- [Link to epic definition](../epic-definition.md)
- [Link to testing guidelines]
