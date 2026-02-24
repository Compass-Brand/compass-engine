# Linting and Security Gates

Last reviewed: 2026-02-24

This repo ships a shared linting/security baseline for both:

- `compass-engine` itself
- generated downstream project outputs (via `src/root/` and `src/github/workflows/`)

## Source of Truth

- Root lint/security templates: `src/root/`
- GitHub Actions templates: `src/github/workflows/`
- Generated outputs:
  - root files from `dist/root` (pushed into project root)
  - workflow files from `dist/.github/workflows`

## Pre-commit Baseline

Main config:

- `src/root/.pre-commit-config.yaml`

Default stages:

- `pre-commit`
- `pre-push`

Fast-path hooks run by default on commit/push:

- `pre-commit-hooks` hygiene checks
- `sync-pre-commit-deps`
- `pyupgrade`
- `ruff-check` + `ruff-format`
- `isort`
- `yamllint` (strict)
- `gitleaks`
- `codespell`
- `biome` (JS/TS/JSON only)
- `markdownlint-cli`
- `eslint`
- `prettier` (Markdown + YAML only)
- `actionlint`
- `ansible-lint` (when matching files exist)

Manual-only hooks (heavy/system-dependent):

- `pylint`
- `dotenv-linter`
- `checkov`

Run manual hooks explicitly:

```bash
pre-commit run --hook-stage manual pylint
pre-commit run --hook-stage manual dotenv-linter
pre-commit run --hook-stage manual checkov
```

## Formatter/Linter Ownership

To avoid formatter conflicts:

- Biome owns JS/TS/JSON formatting/lint checks in pre-commit.
- Prettier is scoped to Markdown and YAML.
- ESLint handles JS/TS lint policy (`--max-warnings=0`), not formatting.

## GitHub Workflows

### Fast PR/Push Gate

- `src/github/workflows/linting.yml`

Includes:

- `pre-commit` baseline job (with pre-commit cache)
- dedicated `pylint` job for changed Python files
- `dotenv-linter`
- `markdownlint` library job
- `trivy` filesystem scan (HIGH/CRITICAL gate)
- optional jobs by repo contents:
  - `hadolint`
  - `checkov`
  - `terraform fmt + tflint`
  - `rustfmt + clippy`
  - `kubeconform`
  - `zizmor`

### CodeQL Security Analysis

- `src/github/workflows/codeql.yml`
- Trigger: push, pull request, and weekly schedule.
- Current language baseline: `javascript`.
- The workflow checks repository Code Scanning API availability first:
  - runs analysis when API returns HTTP `200`
  - skips with actionable warnings for `403`/`404` and other API failures

### Deep Analysis (outside PR fast path)

- `src/github/workflows/necessist.yml`
- Trigger: manual (`workflow_dispatch`) and weekly schedule.
- Purpose: run `necessist` only as a deep analysis job.

### Runtime/Cluster Security

- `src/github/workflows/runtime-security.yml`
- Trigger: manual (`workflow_dispatch`)
- Purpose: environment-dependent tools:
  - `kube-bench`
  - `trivy-operator`
  - `kubectl-who-can`
  - `tracee` notes/self-hosted guidance
  - `siderophile`

## CodeQL Setup and Troubleshooting

### One-time repository setup

1. Ensure the baseline workflow exists in the target repo:
   - `.github/workflows/codeql.yml`
2. Enable Code Scanning in GitHub:
   - Repository `Settings` -> `Security` -> `Code security and analysis`
3. If the repo is private/internal, ensure GitHub Advanced Security is enabled.

### Verify CodeQL is active

1. Open a PR or push a commit.
2. Confirm the check run:
   - `CodeQL Security Scanning / Analyze` is `Success`.
3. Optional API verification:

```bash
gh api repos/<owner>/<repo>/code-scanning/alerts?per_page=1 --include
```

Expected result:

- HTTP `200` means code scanning is active and accessible to the workflow token.

### Common skip cases

- HTTP `404`: Code scanning is not enabled for the repository.
- HTTP `403`: Missing access or feature entitlement (commonly GHAS requirement on private/internal repos).
- Other HTTP statuses: temporary API/platform issue or permission mismatch.

The workflow logs now print setup guidance and links whenever CodeQL is skipped.

## Operational Commands

```bash
# Validate source + drift + dry-run push gates
npm run check

# Build distributable bundles
npm run build

# Sync lint/workflow outputs into the current repo
npm run push -- --targets github,root
```

## Updating Tool Versions

When updating lint/security hooks:

1. Update `src/root/.pre-commit-config.yaml`
2. Run `pre-commit run sync-pre-commit-deps --all-files`
3. Rebuild/sync:
   - `npm run build`
   - `npm run push -- --targets github,root`
4. Re-run gates:
   - `python -m pre_commit run --all-files`
   - `npm run check`
