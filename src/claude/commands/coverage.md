---
name: coverage
description: Run test coverage and output per-file percentage report
---

# Coverage

Run test coverage and output per-file percentage report.

## Supported Languages

| Language              | Tool        | Config                                 |
| --------------------- | ----------- | -------------------------------------- |
| Python                | pytest-cov  | `pytest.ini` or `pyproject.toml`       |
| TypeScript/JavaScript | Jest/Vitest | `jest.config.js` or `vitest.config.ts` |
| Go                    | go test     | Built-in                               |

## Process

### 1. Detect Project Type

```bash
# Detection priority: Python > Node > Go
# Check for Python
if [[ -f "pyproject.toml" ]] || [[ -f "setup.py" ]]; then
    PROJECT_TYPE="python"
elif [[ -f "package.json" ]]; then
    PROJECT_TYPE="node"
elif [[ -f "go.mod" ]]; then
    PROJECT_TYPE="go"
fi
```

### 2. Run Coverage

#### Python (pytest-cov)

```bash
pytest --cov=. --cov-report=json --cov-report=term-missing

# Parse JSON report
cat coverage.json | jq '.files | to_entries | .[] | {file: .key, coverage: (.value.summary.percent_covered | floor)}'
```

#### Node (Jest)

```bash
npm test -- --coverage --coverageReporters=json-summary

# Parse report
jq 'to_entries | .[] | {file: .key, coverage: .value.lines.pct}' coverage/coverage-summary.json
```

#### Node (Vitest)

```bash
npx vitest run --coverage --coverage.reporter=json-summary

# Parse report
jq 'to_entries | .[] | select(.key != "total") | {file: .key, coverage: .value.lines.pct}' coverage/coverage-summary.json
```

#### Go

```bash
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out
```

### 3. Output Format

#### Table Format (default)

```text
╔══════════════════════════════════════════════════════════════╗
║                    Coverage Report                            ║
╠══════════════════════════════════════════════════════════════╣
║ File                                      │ Coverage │ Status ║
╠═══════════════════════════════════════════╪══════════╪════════╣
║ src/auth/login.py                         │   92%    │   ✓    ║
║ src/auth/oauth.py                         │   87%    │   ✓    ║
║ src/api/users.py                          │   75%    │   ⚠    ║
║ src/utils/helpers.py                      │   45%    │   ✗    ║
╠═══════════════════════════════════════════╪══════════╪════════╣
║ TOTAL                                     │   78%    │   ⚠    ║
╚══════════════════════════════════════════════════════════════╝

Legend: ✓ ≥80%  ⚠ 60-79%  ✗ <60%
```

#### JSON Format (--json)

```json
{
  "total": 78.5,
  "threshold": 80,
  "passing": false,
  "files": [
    { "file": "src/auth/login.py", "coverage": 92.3 },
    { "file": "src/auth/oauth.py", "coverage": 87.1 },
    { "file": "src/api/users.py", "coverage": 75.0 },
    { "file": "src/utils/helpers.py", "coverage": 45.2 }
  ],
  "uncovered_files": ["src/utils/helpers.py"]
}
```

### 4. Threshold Check

Default threshold: 80% (configurable in CLAUDE.md or project settings). Override in `.claude/config.json` under `coverage.threshold` (e.g., `"coverage": {"threshold": 75}`). Note: `.claude/config.json` takes precedence over CLAUDE.md settings.

**Important:** 80% is a baseline minimum for most files. Per TDD policy, production code critical paths require 100% coverage. Use `--threshold 100` for critical modules.

```bash
# Read threshold from .claude/config.json, default to 80 if not specified
THRESHOLD=$(jq -r '.coverage.threshold // 80' .claude/config.json 2>/dev/null || echo 80)

# Use awk -v to safely pass the TOTAL variable
if awk -v total="$TOTAL" -v threshold="$THRESHOLD" 'BEGIN {exit !(total < threshold)}'; then
    echo "Coverage below threshold ($THRESHOLD%)"
    exit 1
fi
```

## Options

| Option          | Description                         |
| --------------- | ----------------------------------- |
| `--json`        | Output in JSON format               |
| `--threshold N` | Set minimum coverage threshold      |
| `--file PATH`   | Run coverage for specific file only |
| `--uncovered`   | Show only files below threshold     |

## Error Handling

- **No test framework**: "No test framework detected. Install pytest, jest, or vitest."
- **Tests fail**: "Tests failed. Fix failing tests before checking coverage."
- **No tests found**: "No tests found. Create tests first."

## Related Commands

- `/tdd` - Start TDD workflow
- `/e2e` - Generate E2E tests
- `/verify` - Verify changes including coverage
