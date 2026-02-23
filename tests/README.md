# Tests

This repository currently uses an operational gate workflow instead of a language-level test suite.

Active gates:
- `npm run check`
  - Runs `validate` + `build` + multi-target push dry-run.

When runtime code requiring unit/integration tests is introduced, add tests under `tests/` and wire them into `npm run check`.
