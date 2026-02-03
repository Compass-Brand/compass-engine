---
name: validate-env
description: Comprehensive environment validation for development setup
---

# Validate Environment

Comprehensive environment validation for development setup.

## Checks Performed

### 1. Tool Versions

| Tool    | Minimum Version | Check Command       |
| ------- | --------------- | ------------------- |
| Node.js | 18.0.0          | `node --version`    |
| npm     | 9.0.0           | `npm --version`     |
| Python  | 3.11.0          | `python3 --version` |
| Go      | 1.22.0          | `go version`        |
| Git     | 2.40.0          | `git --version`     |
| Docker  | 24.0.0          | `docker --version`  |
| gh CLI  | 2.40.0          | `gh --version`      |

### 2. MCP Services

Check all configured MCP servers:

```bash
# Check via claude mcp list
claude mcp list

# Expected services:
# - forgetful: http://localhost:8020
# - context7: http://localhost:8002
# - serena: http://localhost:8003
```

### 3. Environment Files

Check for required `.env` files:

```bash
# Root workspace
[ -f ".env" ] && echo "✓ .env exists" || echo "✗ .env missing"

# Check for template
[ -f ".env.example" ] && echo "✓ .env.example exists"

# Validate required variables
# WARNING: Do not remove -q flag; without it, grep outputs matching lines which could leak secrets
grep -q "DATABASE_URL" .env && echo "✓ DATABASE_URL set"
grep -q "GITHUB_TOKEN" .env && echo "✓ GITHUB_TOKEN set"
```

### 4. Git Configuration

```bash
# Check user config
git config user.name && echo "✓ Git user.name configured"
git config user.email && echo "✓ Git user.email configured"

# Check for hooks
[ -d ".git/hooks" ] && echo "✓ Git hooks directory exists"

# Check submodules
git submodule status
```

### 5. Docker Services

```bash
# Check if Docker is running
docker info &>/dev/null && echo "✓ Docker running" || echo "✗ Docker not running"

# Check MCP containers
docker compose -f mcps/docker-compose.yml ps
```

## Output Format

```
╔══════════════════════════════════════════════════════════════╗
║                 Environment Validation                        ║
╠══════════════════════════════════════════════════════════════╣
║ TOOL VERSIONS                                                 ║
║   Node.js     │ 20.10.0    │ ✓ Pass (min: 18.0.0)           ║
║   npm         │ 10.2.3     │ ✓ Pass (min: 9.0.0)            ║
║   Python      │ 3.12.0     │ ✓ Pass (min: 3.11.0)           ║
║   Go          │ not found  │ ✗ Fail (required for Beads)    ║
║   Git         │ 2.43.0     │ ✓ Pass (min: 2.40.0)           ║
║   Docker      │ 24.0.7     │ ✓ Pass (min: 24.0.0)           ║
║   gh CLI      │ 2.42.0     │ ✓ Pass (min: 2.40.0)           ║
╠══════════════════════════════════════════════════════════════╣
║ MCP SERVICES                                                  ║
║   forgetful   │ :8020      │ ✓ Connected                    ║
║   context7    │ :8002      │ ✓ Connected                    ║
║   serena      │ :8003      │ ✓ Connected                    ║
║   postgres    │ :8001      │ ✗ Failed to connect            ║
╠══════════════════════════════════════════════════════════════╣
║ ENVIRONMENT FILES                                             ║
║   .env                      │ ✓ Exists                       ║
║   DATABASE_URL              │ ✓ Set                          ║
║   GITHUB_TOKEN              │ ✓ Set                          ║
╠══════════════════════════════════════════════════════════════╣
║ GIT CONFIGURATION                                             ║
║   user.name                 │ ✓ Configured                   ║
║   user.email                │ ✓ Configured                   ║
║   pre-commit hooks          │ ✓ Installed                    ║
║   submodules                │ ✓ 9/9 initialized              ║
╠══════════════════════════════════════════════════════════════╣
║ OVERALL STATUS: 18/20 checks passed                           ║
╚══════════════════════════════════════════════════════════════╝

Recommendations:
1. Install Go: sudo apt-get install golang-go
2. Start postgres MCP: docker compose -f mcps/docker-compose.yml up -d postgres
```

## Implementation Script

```bash
#!/bin/bash
# scripts/validate-env.sh

set -euo pipefail

check_version() {
    local tool="$1"
    local min_version="$2"
    local current=$(eval "$3" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

    if [[ -z "$current" ]]; then
        echo "✗ $tool: not found"
        return 1
    fi

    # Simple version comparison
    if [[ "$(printf '%s\n' "$min_version" "$current" | sort -V | head -1)" == "$min_version" ]]; then
        echo "✓ $tool: $current (min: $min_version)"
        return 0
    else
        echo "✗ $tool: $current (min: $min_version required)"
        return 1
    fi
}

check_mcp() {
    local name="$1"
    local url="$2"

    status=$(curl -sf --connect-timeout 2 -o /dev/null -w "%{http_code}" "$url" 2>/dev/null) || status="000"
    if [[ "$status" =~ ^2[0-9][0-9]$ ]]; then
        echo "✓ $name: connected"
        return 0
    else
        echo "✗ $name: failed to connect (HTTP $status)"
        return 1
    fi
}

echo "=== Environment Validation ==="
echo ""

echo "--- Tool Versions ---"
check_version "Node.js" "18.0.0" "node --version" || true
check_version "npm" "9.0.0" "npm --version" || true
check_version "Python" "3.11.0" "python3 --version" || true
check_version "Git" "2.40.0" "git --version" || true
check_version "Docker" "24.0.0" "docker --version" || true
check_version "gh" "2.40.0" "gh --version" || true

echo ""
echo "--- MCP Services ---"
check_mcp "forgetful" "http://localhost:8020/health" || true
check_mcp "context7" "http://localhost:8002/health" || true
check_mcp "serena" "http://localhost:8003/health" || true

echo ""
echo "--- Environment Files ---"
[ -f ".env" ] && echo "✓ .env exists" || echo "✗ .env missing"

echo ""
echo "--- Git Configuration ---"
git config user.name &>/dev/null && echo "✓ user.name configured" || echo "✗ user.name not set"
git config user.email &>/dev/null && echo "✓ user.email configured" || echo "✗ user.email not set"
```

## Exit Codes

| Code | Meaning                            |
| ---- | ---------------------------------- |
| 0    | All checks passed                  |
| 1    | One or more critical checks failed |
| 2    | Warnings only (non-critical)       |

> **Implementation Note:** The `check_mcp` function above uses `curl -s` which returns 0 for any HTTP response. To properly distinguish warnings (exit code 2), capture the HTTP status code: `curl -sf -o /dev/null -w "%{http_code}"` and treat only 2xx responses as success.

## Related Commands

- `/check-updates` - Check for tool updates
- `/mcp-status` - Detailed MCP status
