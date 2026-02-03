# Instinct Evolution

## Graduation Criteria

An instinct can graduate to a skill when ALL conditions are met:

1. **Confidence > 0.9** - Proven reliable
2. **Invocations > 10** - Sufficiently tested
3. **No contradictions** - Doesn't conflict with existing skills/rules

## Graduation Process

### 1. Identify Candidates

Query Forgetful for instincts meeting criteria:

- confidence > 0.9
- invocations > 10

### 2. Check Contradictions

- Compare against existing .claude/rules/
- Compare against existing .claude/skills/
- Flag any conflicts for human review

### 3. Generate Skill

Create skill file with:

- Pattern description
- Usage examples from instinct history
- Clear trigger conditions
- Expected outcomes

### 4. Archive Instinct

- Update instinct status to "graduated"
- Link to generated skill
- Preserve history for auditing

## Evolution Command: /evolve

```
/evolve [--dry-run] [--force instinct-id]

Options:
  --dry-run     Show candidates without graduating
  --force       Graduate specific instinct even if criteria not met
```

### Safety Guardrails for --force

The `--force` option bypasses graduation criteria but still enforces these safety checks:

1. **Minimum invocations**: At least 3 invocations required (prevents graduating untested instincts)
2. **Minimum confidence**: Confidence must be >= 0.5 (prevents graduating disproven instincts)
3. **Contradiction check**: Still verifies no conflicts with existing skills/rules
4. **User confirmation**: Displays instinct details and requires explicit "yes" to proceed
5. **Audit trail**: Logs the forced graduation with timestamp and reason for review

## Anti-Patterns

- Don't graduate instincts that are project-specific
- Don't graduate instincts that conflict with rules
- Don't auto-graduate without human review for critical patterns
