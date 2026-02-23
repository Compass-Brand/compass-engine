# Reference Materials

This directory stores **reference and archive material**, not active production runtime code.

## Contents

- `reference/automation-spec-archive/`
  - Archived Python-first automation implementation and tests.
  - Retained as specification/pseudocode after architecture pivot.
- `reference/bmad-core-implementation.md`
  - Notes and analysis of BMAD core internals.
- `reference/ralph-patterns-analysis.md`
  - Pattern analysis used for review-loop and orchestration design ideas.

## Rule

Do not treat files in `reference/` as source-of-truth runtime implementation.
Use them as design input when creating production behavior in `src/` and `scripts/`.