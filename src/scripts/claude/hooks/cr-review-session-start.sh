#!/bin/bash
# Full CR Review - Session Start Hook
# Detects in-progress full codebase reviews and offers to resume
# Used as a SessionStart hook within the full-cr-review command

set -euo pipefail

# Read hook input from stdin
INPUT=$(cat)

# Extract session info with defensive JSON parsing
CWD=""
if echo "$INPUT" | jq -e '.' >/dev/null 2>&1; then
    CWD=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null || echo "")
fi

# Validate CWD - fall back to current working directory if empty or invalid
if [ -z "$CWD" ] || [ ! -d "$CWD" ]; then
    CWD="$(pwd)"
fi

# Normalize to absolute path
CWD="$(cd "$CWD" && pwd)"

# Check for full CR review context marker file
MARKER_FILE="${CWD}/.full-cr-in-progress"

if [ ! -f "$MARKER_FILE" ]; then
    # Not in full CR review mode - nothing to report
    exit 0
fi

# Check for jq dependency
if ! command -v jq >/dev/null 2>&1; then
    echo "Warning: jq not found, cannot parse review state" >&2
    exit 0
fi

# Read marker file for review state
STATE=""
if [ -r "$MARKER_FILE" ]; then
    STATE=$(cat "$MARKER_FILE" 2>/dev/null) || STATE=""
fi

if [ -z "$STATE" ] || ! echo "$STATE" | jq -e '.' >/dev/null 2>&1; then
    echo "Warning: Invalid review state file" >&2
    exit 0
fi

# Extract state information
ITERATION=$(echo "$STATE" | jq -r '.iteration // 0' 2>/dev/null || echo "0")
BRANCH=$(echo "$STATE" | jq -r '.branch // "unknown"' 2>/dev/null || echo "unknown")
STARTED_AT=$(echo "$STATE" | jq -r '.started_at // "unknown"' 2>/dev/null || echo "unknown")
TOTAL_FOUND=$(echo "$STATE" | jq -r '.total_issues_found // 0' 2>/dev/null || echo "0")
TOTAL_FIXED=$(echo "$STATE" | jq -r '.total_issues_fixed // 0' 2>/dev/null || echo "0")

# Output informational message about in-progress review
cat <<EOF
{
  "systemMessage": "Full CodeRabbit review in progress (iteration $ITERATION on branch '$BRANCH'). Started: $STARTED_AT. Issues: $TOTAL_FOUND found, $TOTAL_FIXED fixed. Run /full-cr-review --resume to continue."
}
EOF

exit 0
