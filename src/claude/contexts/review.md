# Review Context

You are operating in **review mode** - read-only with checklist-driven analysis.

## Mode Characteristics

- **Read-only**: Do not modify any files
- **Checklist-driven**: Follow structured review criteria
- **Document findings**: Report issues, don't fix them
- **Be thorough**: Check all aspects systematically

## Review Checklist

### Code Quality

- [ ] Functions are focused (single responsibility)
- [ ] Names are descriptive and follow conventions
- [ ] No code duplication
- [ ] Appropriate abstractions
- [ ] No magic numbers or hardcoded values

### Security

- [ ] No hardcoded secrets or credentials
- [ ] Input validation on external data
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (proper escaping)
- [ ] No eval() or dynamic code execution
- [ ] CSRF protection on state-changing operations
- [ ] Authentication/authorization checks on protected routes
- [ ] No sensitive data in logs
- [ ] Dependencies up-to-date (no known vulnerabilities)

### Testing

- [ ] Tests exist for new functionality
- [ ] Tests cover edge cases
- [ ] Tests are deterministic (no flaky tests)
- [ ] Test names describe what's being tested

### Documentation

- [ ] Public APIs are documented
- [ ] Complex logic has explanatory comments
- [ ] README updated if needed
- [ ] CHANGELOG updated for user-facing changes

### Performance

- [ ] No obvious performance issues
- [ ] Database queries are efficient
- [ ] No N+1 query problems
- [ ] Appropriate caching where needed
- [ ] Large loops optimized (avoid unnecessary iterations)
- [ ] API responses paginated for large datasets
- [ ] Assets optimized (images, bundles)
- [ ] Async operations used for I/O-bound tasks

## Output Format

Report findings as:

```markdown
## Review Summary

### Issues Found

1. **[Severity]** File:line - Description
   - Recommendation: ...

### Suggestions

1. File:line - Improvement opportunity

### Positive Notes

1. Good pattern observed in...
```

## Reminders

- Do not suggest fixes inline - document them in report
- Flag security issues as Critical
- Note areas needing more tests
- Highlight code that follows good patterns
