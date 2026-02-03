---
name: metrics
description: Aggregate codebase metrics including lines of code, TODOs, FIXMEs, and complexity metrics
---

# Metrics

Aggregate codebase metrics: lines of code, TODOs, FIXMEs, and complexity metrics.

## Metrics Collected

### 1. Lines of Code (LOC)

Using `cloc`:

```bash
cloc . --json --exclude-dir=node_modules,vendor,.venv,dist,build
```

Output:

- Total lines
- Code lines
- Comment lines
- Blank lines
- By language breakdown

### 2. TODO/FIXME Analysis

```bash
# Find all TODOs
grep -rn "TODO" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" . | wc -l

# Find all FIXMEs
grep -rn "FIXME" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" . | wc -l

# Find all HACKs
grep -rn "HACK" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" . | wc -l

# Find all NOTEs
grep -rn "NOTE" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" . | wc -l
```

### 3. Complexity Metrics

#### Python (radon)

```bash
# Cyclomatic complexity
radon cc . -a -s --json

# Maintainability index
radon mi . -s --json
```

#### JavaScript/TypeScript (eslint with complexity rule)

```bash
npx eslint . --format json --rule 'complexity: ["warn", 10]'
```

### 4. Dependency Count

```bash
# Node
jq '.dependencies | length' package.json
jq '.devDependencies | length' package.json

# Python
pip list --format=json | jq 'length'
```

### 5. Test Metrics

```bash
# Test file count
find . \( -name "test*.py" -o -name "*.test.ts" \) | wc -l

# Test function count
grep -r "def test_\|it(\|describe(" --include="*test*" . | wc -l
```

## Output Format

### Table (default)

```text
╔══════════════════════════════════════════════════════════════╗
║                    Codebase Metrics                           ║
╠══════════════════════════════════════════════════════════════╣
║ LINES OF CODE                                                 ║
║   Total Lines      │ 45,230                                   ║
║   Code Lines       │ 32,150                                   ║
║   Comment Lines    │ 8,420                                    ║
║   Blank Lines      │ 4,660                                    ║
╠══════════════════════════════════════════════════════════════╣
║ BY LANGUAGE                                                   ║
║   TypeScript       │ 18,500  (57%)                            ║
║   Python           │ 10,200  (32%)                            ║
║   JavaScript       │ 2,100   (7%)                             ║
║   Shell            │ 850     (3%)                             ║
║   YAML             │ 500     (1%)                             ║
╠══════════════════════════════════════════════════════════════╣
║ CODE MARKERS                                                  ║
║   TODOs            │ 42                                       ║
║   FIXMEs           │ 8                                        ║
║   HACKs            │ 3                                        ║
║   NOTEs            │ 127                                      ║
╠══════════════════════════════════════════════════════════════╣
║ COMPLEXITY                                                    ║
║   Avg Cyclomatic   │ 4.2  (target: <10)                       ║
║   High Complexity  │ 5 functions (CC > 10)                    ║
║   Maintainability  │ A (good)                                 ║
╠══════════════════════════════════════════════════════════════╣
║ DEPENDENCIES                                                  ║
║   Production       │ 45                                       ║
║   Development      │ 32                                       ║
║   Total            │ 77                                       ║
╠══════════════════════════════════════════════════════════════╣
║ TESTS                                                         ║
║   Test Files       │ 89                                       ║
║   Test Functions   │ 412                                      ║
║   Coverage         │ 78%                                      ║
╚══════════════════════════════════════════════════════════════╝

Generated: 2024-01-15 14:30:00
```

### JSON (--json)

```json
{
  "generated_at": "2024-01-15T14:30:00Z",
  "loc": {
    "total": 45230,
    "code": 32150,
    "comments": 8420,
    "blank": 4660,
    "by_language": {
      "TypeScript": { "lines": 18500, "percent": 57 },
      "Python": { "lines": 10200, "percent": 32 },
      "JavaScript": { "lines": 2100, "percent": 7 },
      "Shell": { "lines": 850, "percent": 3 },
      "YAML": { "lines": 500, "percent": 1 }
    }
  },
  "markers": {
    "todo": 42,
    "fixme": 8,
    "hack": 3,
    "note": 127
  },
  "complexity": {
    "average_cc": 4.2,
    "high_complexity_functions": 5,
    "maintainability_grade": "A"
  },
  "dependencies": {
    "production": 45,
    "development": 32,
    "total": 77
  },
  "tests": {
    "files": 89,
    "functions": 412,
    "coverage_percent": 78
  }
}
```

## Options

| Option              | Description                        |
| ------------------- | ---------------------------------- |
| `--json`            | Output in JSON format              |
| `--compare FILE`    | Compare with previous metrics file |
| `--path DIR`        | Analyze specific directory         |
| `--exclude PATTERN` | Additional exclusion patterns      |

## Comparison Mode

Compare with previous metrics:

```bash
/metrics --compare metrics-2024-01-01.json
```

Output:

```text
Changes since 2024-01-01:
  LOC: +1,230 (+3.8%)
  TODOs: -5 (42 → 37)
  Complexity: -0.3 (4.5 → 4.2)
  Coverage: +2% (76% → 78%)
```

## Prerequisites

Install required tools:

```bash
# cloc (lines of code)
sudo apt-get install cloc

# radon (Python complexity)
pip install radon

# eslint (JS/TS complexity)
npm install -g eslint
```

## Related Commands

- `/coverage` - Detailed coverage report
- `/audit-docs` - Documentation freshness
- `/pr-metrics` - PR-specific metrics
