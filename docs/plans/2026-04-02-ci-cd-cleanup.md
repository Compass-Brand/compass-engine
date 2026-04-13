# CI/CD Cleanup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reduce compass-engine PR checks from ~28 to ~16 by removing irrelevant checks, adding zero-cost detection, and splitting linting into core + optional modules for downstream distribution.

**Architecture:** Three complementary changes: (A) drift-exclude config lets this repo skip workflows it distributes but doesn't need, (B) a lightweight detect job prevents runner allocation for absent languages, (C) splitting linting.yml into lint-core.yml + lint-languages.yml gives downstream repos granular opt-in.

**Tech Stack:** GitHub Actions YAML, Node.js (drift checker + push script)

---

## Task 1: Create drift-exclude config and update drift checker

**Files:**
- Create: `src/github/.drift-exclude.yml`
- Modify: `tools/check-github-drift.js`

**Step 1: Create the drift-exclude config**

Create `src/github/.drift-exclude.yml`:

```yaml
# Workflows available for distribution but intentionally not used in compass-engine.
# The drift checker skips these paths when comparing src/github/ against .github/.
- workflows/codeql.yml
- workflows/necessist.yml
- workflows/runtime-security.yml
- workflows/lint-languages.yml
```

**Step 2: Update the drift checker to read exclusions**

In `tools/check-github-drift.js`, add after `const TARGET_ROOT` (line 18):

```javascript
const DRIFT_EXCLUDE_FILE = path.join(SOURCE_ROOT, '.drift-exclude.yml');

async function loadExclusions() {
  try {
    const content = await fs.readFile(DRIFT_EXCLUDE_FILE, 'utf8');
    return content
      .split('\n')
      .map((line) => line.replace(/^-\s*/, '').trim())
      .filter((line) => line && !line.startsWith('#'));
  } catch {
    return [];
  }
}
```

In the `run()` function, after collecting `sourceFiles` and `targetFiles` (line 67), filter out excluded paths:

```javascript
const exclusions = await loadExclusions();
const isExcluded = (f) => exclusions.some((ex) => f === ex || f.startsWith(ex + '/'));
const sourceFiles = sourceFilesRaw.filter((f) => !isExcluded(f)).sort();
const targetFiles = targetFilesRaw.filter((f) => !isExcluded(f)).sort();
```

Remove the old `const sourceFiles = sourceFilesRaw.sort()` and `const targetFiles = targetFilesRaw.sort()` lines.

**Step 3: Run the drift checker to verify it passes**

Run: `node tools/check-github-drift.js`
Expected: "No .github drift detected." (even though codeql.yml etc. exist in src/ but not .github/)

Wait — we haven't deleted them from .github/ yet. This step verifies the checker loads the config without errors. Actual deletion happens in Task 2.

**Step 4: Commit**

```bash
git add src/github/.drift-exclude.yml tools/check-github-drift.js
git commit -m "feat: add drift-exclude config for distribution-only workflows"
```

---

## Task 2: Remove irrelevant workflows from .github/ [DEFERRED]

> **Note:** This task was not executed. The workflows (codeql.yml, necessist.yml, runtime-security.yml) remain in .github/ and are covered by the drift-exclude config. Deletion is deferred until the next CI cleanup pass.

**Files:**
- Delete: `.github/workflows/codeql.yml`
- Delete: `.github/workflows/necessist.yml`
- Delete: `.github/workflows/runtime-security.yml`

**Step 1: Delete the workflows from .github/**

```bash
rm .github/workflows/codeql.yml
rm .github/workflows/necessist.yml
rm .github/workflows/runtime-security.yml
```

**Step 2: Verify drift checker passes**

Run: `node tools/check-github-drift.js`
Expected: "No .github drift detected." — the exclusions prevent these from being flagged as missing.

**Step 3: Commit**

```bash
git add -A .github/workflows/
git commit -m "chore: remove irrelevant CI workflows from compass-engine

codeql, necessist, and runtime-security remain in src/github/ for
distribution to downstream repos that need them."
```

---

## Task 3: Remove codeql from baseline feature group in push.js

**Files:**
- Modify: `tools/push.js`

**Step 1: Update the baseline feature group**

In `tools/push.js`, find `GITHUB_FEATURE_GROUPS.baseline` and remove `'codeql'`:

```javascript
// Before:
baseline: [
  'codeowners',
  'dependabot',
  'quality-checks',
  'pr-size-labeler',
  'stale',
  'codeql',
],

// After:
baseline: [
  'codeowners',
  'dependabot',
  'quality-checks',
  'pr-size-labeler',
  'stale',
],
```

**Step 2: Add linting-core and linting-languages feature groups**

In the same `GITHUB_FEATURE_GROUPS` object, replace the `linting` entry and add the new groups:

```javascript
// Before:
linting: ['workflows/linting.yml'],

// After:
'linting-core': ['workflows/lint-core.yml'],
'linting-languages': ['workflows/lint-languages.yml'],
linting: ['workflows/lint-core.yml', 'workflows/lint-languages.yml'],
```

**Step 3: Verify push help shows updated feature names**

Run: `npm run push -- --help`
Expected: Feature list includes `linting-core`, `linting-languages`, and `linting`.

**Step 4: Commit**

```bash
git add tools/push.js
git commit -m "feat: split linting feature group and remove codeql from baseline"
```

---

## Task 4: Create lint-core.yml

**Files:**
- Create: `src/github/workflows/lint-core.yml`

**Step 1: Create lint-core.yml from the core jobs in linting.yml**

Create `src/github/workflows/lint-core.yml` with:
- The same `name`, `on`, `permissions`, and `concurrency` block from `linting.yml`
- Rename workflow to `Linting Core`
- Include these jobs only: `pre-commit`, `pylint`, `dotenv-linter`, `markdownlint-library`, `trivy`, `zizmor`
- Copy each job exactly as-is from `linting.yml` — no modifications to job content

**Step 2: Verify YAML is valid**

Run: `python -c "import yaml; yaml.safe_load(open('src/github/workflows/lint-core.yml'))"`
Expected: No errors.

**Step 3: Commit**

```bash
git add src/github/workflows/lint-core.yml
git commit -m "feat: create lint-core.yml with universal linting jobs"
```

---

## Task 5: Create lint-languages.yml with detect job

**Files:**
- Create: `src/github/workflows/lint-languages.yml`

**Step 1: Create lint-languages.yml with detect job and language linters**

Create `src/github/workflows/lint-languages.yml` with:
- Same trigger/permissions/concurrency pattern as lint-core.yml
- Rename workflow to `Linting Languages`
- Add a new `detect` job that does lightweight file-existence checks:

```yaml
jobs:
  detect:
    name: Detect project languages
    runs-on: ubuntu-latest
    timeout-minutes: 2
    outputs:
      has_docker: ${{ steps.check.outputs.has_docker }}
      has_terraform: ${{ steps.check.outputs.has_terraform }}
      has_rust: ${{ steps.check.outputs.has_rust }}
      has_k8s: ${{ steps.check.outputs.has_k8s }}
      has_iac: ${{ steps.check.outputs.has_iac }}
    steps:
      - name: Checkout
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
        with:
          sparse-checkout: .
          fetch-depth: 1

      - name: Detect languages
        id: check
        run: |
          echo "has_docker=$(test -n "$(find . -maxdepth 4 -name 'Dockerfile*' 2>/dev/null)" && echo true || echo false)" >> "$GITHUB_OUTPUT"
          echo "has_terraform=$(test -n "$(find . -maxdepth 4 -name '*.tf' 2>/dev/null)" && echo true || echo false)" >> "$GITHUB_OUTPUT"
          echo "has_rust=$(test -f Cargo.toml && echo true || echo false)" >> "$GITHUB_OUTPUT"
          echo "has_k8s=$(find . -maxdepth 4 -type f \( -name '*.yaml' -o -name '*.yml' \) 2>/dev/null | grep -qE '(/k8s/|/kubernetes/|/manifests/|/helm/|/charts/)' && echo true || echo false)" >> "$GITHUB_OUTPUT"
          echo "has_iac=$(test -n "$(find . -maxdepth 4 \( -name '*.tf' -o -name 'Dockerfile*' \) 2>/dev/null)" && echo true || echo false)" >> "$GITHUB_OUTPUT"
```

- Move these jobs from linting.yml, each with `needs: detect` and an `if:` guard:
  - `hadolint` — `if: needs.detect.outputs.has_docker == 'true'`
  - `checkov` — `if: needs.detect.outputs.has_iac == 'true'`
  - `terraform-lint` — `if: needs.detect.outputs.has_terraform == 'true'`
  - `rust-lint` — `if: needs.detect.outputs.has_rust == 'true'`
  - `kubeconform` — `if: needs.detect.outputs.has_k8s == 'true'`

- For each moved job: remove the internal detect step (the job-level `if:` replaces it). Keep the actual linting steps.

**Step 2: Verify YAML is valid**

Run: `python -c "import yaml; yaml.safe_load(open('src/github/workflows/lint-languages.yml'))"`
Expected: No errors.

**Step 3: Commit**

```bash
git add src/github/workflows/lint-languages.yml
git commit -m "feat: create lint-languages.yml with zero-cost detect gate"
```

---

## Task 6: Delete old linting.yml and deploy lint-core.yml [DEFERRED]

> **Note:** linting.yml was already removed, but lint-core.yml deployment to .github/ was not completed. The split workflow files exist in src/github/workflows/ but deployment is deferred until the next CI cleanup pass.

**Files:**
- Delete: `src/github/workflows/linting.yml`
- Delete: `.github/workflows/linting.yml`
- Copy: `src/github/workflows/lint-core.yml` → `.github/workflows/lint-core.yml`

**Step 1: Remove the old monolith**

```bash
rm src/github/workflows/linting.yml
rm .github/workflows/linting.yml
```

**Step 2: Copy lint-core.yml to .github/**

```bash
cp src/github/workflows/lint-core.yml .github/workflows/lint-core.yml
```

Note: `lint-languages.yml` stays in `src/github/` only — it's already in `.drift-exclude.yml`.

**Step 3: Verify drift checker passes**

Run: `node tools/check-github-drift.js`
Expected: "No .github drift detected."

**Step 4: Run the build to verify dist is clean**

Run: `npm run build`
Expected: Build completes with no errors.

**Step 5: Commit**

```bash
git add -A src/github/workflows/ .github/workflows/
git commit -m "refactor: replace linting.yml monolith with lint-core.yml + lint-languages.yml

lint-core.yml runs in compass-engine (universal checks).
lint-languages.yml available for distribution (language-specific, zero-cost detect gate).
Old linting.yml removed from both src/ and .github/."
```

---

## Task 7: Verify end-to-end

**Step 1: Run full validation**

Run: `npm run check`
Expected: All checks pass (build, drift, validation).

**Step 2: Verify .github/workflows/ only has the expected files**

Run: `ls .github/workflows/`
Expected:
- `github-drift.yml`
- `lint-core.yml`
- `pr-size-labeler.yml`
- `quality-checks.yml`
- `stale.yml`
- `submodule-security-monitoring.yml`

NOT present: `codeql.yml`, `necessist.yml`, `runtime-security.yml`, `linting.yml`, `lint-languages.yml`

**Step 3: Verify src/github/workflows/ has everything for distribution**

Run: `ls src/github/workflows/`
Expected:
- `codeql.yml`
- `github-drift.yml`
- `lint-core.yml`
- `lint-languages.yml`
- `necessist.yml`
- `pr-size-labeler.yml`
- `quality-checks.yml`
- `runtime-security.yml`
- `stale.yml`
- `submodule-security-monitoring.yml`

**Step 4: Dry-run push to verify feature groups work**

Run: `npm run push -- --targets github --github-features linting-core --dry-run --project .`
Expected: Shows lint-core.yml would be synced.

Run: `npm run push -- --targets github --github-features linting --dry-run --project .`
Expected: Shows both lint-core.yml and lint-languages.yml would be synced.

**Step 5: Final commit if any adjustments needed, then push**

```bash
git push
```
