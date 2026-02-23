# Tests

Test strategy and current status for `compass-engine`.

## Current State

- Python test suite under `tests/bmad_core/` exists as **placeholder/spec tests**.
- These tests currently skip at module level because corresponding `_bmad` runtime modules are not implemented in this repository.

## Why They Exist

These tests preserve expected behavior for a potential BMAD automation runtime layer and act as executable specification drafts.

## Active Quality Gates Today

Current operational quality gates are:
- `npm run validate`
- `npm run build`
- `npm run push -- --dry-run --targets claude,codex,opencode,github`

## Future Direction

When/if `_bmad` runtime code is implemented in this repo:
1. Implement modules referenced by `tests/bmad_core/`.
2. Remove module-level skip guards.
3. Enforce `pytest` in CI.