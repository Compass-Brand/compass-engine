# GitHub Standardization

Last reviewed: 2026-02-23

This document defines the Compass Brand GitHub standard based on the current state of local Compass repositories.

## Scope Audited

Audited repositories with `.git` and `.github` content:
- `compass-brand-infrastructure`
- `compass-brand-setup`
- `compass-forge`
- `compass-tests`
- `compass-forge/compass-engine`

## What Exists Today

Common workflows across most repos:
- `quality-checks.yml`
- `pr-size-labeler.yml`
- `stale.yml`

Present only in some repos:
- `codeql.yml` (setup and engine)

Dependabot exists in all audited repos, but package ecosystems vary.

## Divergence Summary

1. Action versions are not fully aligned (`actions/checkout` and tool actions vary).
2. `quality-checks.yml` has multiple variants (linting and secret-regex differences).
3. `stale.yml` version differs (`actions/stale@v9` vs `@v10`).
4. `dependabot.yml` ecosystems differ per repo (actions-only, npm, pip, submodules).
5. Engine has repo-specific workflow logic (`check-bmad-updates`) that should not be in org baseline.

## Standard v1 (Defined Here)

Org baseline (`src/github/`):
- `workflows/quality-checks.yml` using latest shared Compass pattern
- `workflows/pr-size-labeler.yml`
- `workflows/stale.yml` on `actions/stale@v10`
- `workflows/codeql.yml` on `codeql-action@v4` (javascript baseline)
- `dependabot.yml` baseline for `github-actions` updates

Repo-specific overlays (`src/github/profiles/`):
- `dependabot-node.yml`
- `dependabot-python.yml`
- `dependabot-submodule-compass-engine.yml`
- `dependabot-submodule-bmad-method.yml`
- `workflows/check-bmad-updates.yml` (BMAD submodule repos only)

## Adoption Policy

1. Every Compass repo gets the org baseline.
2. Repos then apply one or more overlays based on runtime and submodule needs.
3. Repo-specific workflows must live in overlay profiles, not in the org baseline set.

## Next Standardization Pass

1. Apply baseline + appropriate overlays to each audited repo.
2. Roll out `.github` drift-check scripts/workflows across Compass repos (implemented in `compass-engine`).
3. Enforce drift checks in CI for governance.
