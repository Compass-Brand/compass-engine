# GitHub Baseline Bundle

Last reviewed: 2026-02-24

This directory is the source for distributed `.github/` defaults.

## Included

- `workflows/`
- `dependabot.yml`
- `CODEOWNERS`
- `profiles/` (repo-type overlays such as Node/Python/submodule dependabot variants)

## CodeQL Enablement in Target Repositories

The baseline includes `.github/workflows/codeql.yml`, but CodeQL will only run after repository-level security settings are enabled.

1. Apply this baseline to the target repository.
2. In target repo settings, enable:
   - `Code scanning` (`Settings` -> `Security` -> `Code security and analysis`)
3. For private/internal repositories, enable GitHub Advanced Security.

## Verification

After enabling settings, open a PR and confirm:

- `CodeQL Security Scanning / Analyze` passes.

Optional API check:

```bash
gh api repos/<owner>/<repo>/code-scanning/alerts?per_page=1 --include
```

Expected:

- HTTP `200` from the Code Scanning API.
