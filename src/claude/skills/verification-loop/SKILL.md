---
name: verification-loop
description: Ensure no completion claims without fresh evidence by verifying changes actually work before marking tasks complete
---

# Verification Loop

## Purpose

Ensure no completion claims without fresh evidence. Verify changes actually work before marking tasks complete.

## Core Principle

**Never claim completion without verification in THIS session.**

Previous runs, cached results, or assumptions are not valid evidence.

## Verification Checklist

### Before Claiming "Done"

- [ ] Build passes (run build command, show output)
- [ ] Tests pass (run test command, show output)
- [ ] Linter passes (run lint command, show output)
- [ ] No regressions (existing functionality still works)

### Evidence Requirements

Each verification requires:

1. **Command executed** in current session
2. **Output shown** (not summarized from memory)
3. **Timestamp** implicit in tool call

## Framework Detection

### JavaScript/TypeScript Projects

```bash
npm run build && npm test && npm run lint
```

### Python Projects

```bash
# Activate virtual environment first if present
source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null || true
python -m pytest && python -m flake8
```

### Go Projects

```bash
go build ./... && go test ./... && go vet ./...
```

## Failure Handling

### On Build Failure

1. Parse error message
2. Identify root cause
3. Apply fix
4. Re-run verification
5. Do NOT claim done until build passes

### On Test Failure

1. Identify failing test(s)
2. Determine if test or code is wrong
3. Fix appropriately
4. Re-run ALL tests
5. Ensure no regressions

### On Lint Failure

1. Address each linting issue
2. Prefer auto-fix where safe
3. Re-run linter
4. Verify all issues resolved

## Never Skip

- Don't skip verification "because it worked last time"
- Don't assume changes are safe without testing
- Don't rely on IDE indicators without command verification
- Don't claim partial completion as full completion

## Output Format

When verification passes:

```
## Verification Complete

### Build
✓ `npm run build` - Success (0 errors)

### Tests
✓ `npm test` - 42 tests passed, 0 failed, 85% coverage

### Lint
✓ `npm run lint` - No issues

**Status: Ready to commit**
```

When verification fails:

```
## Verification Failed

### Build
✗ `npm run build` - 2 errors

### Analysis
[Error details and fix plan]

**Status: Fixing issues before completion**
```
