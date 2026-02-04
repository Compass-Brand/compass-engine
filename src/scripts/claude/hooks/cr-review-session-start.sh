#!/bin/bash
# Full CR Review - Session Start Hook
# Detects in-progress full codebase reviews and offers to resume
# Used as a SessionStart hook within the full-cr-review command

set -euo pipefail

# Read hook input from stdin with timeout to prevent hanging
INPUT=""
if command -v timeout >/dev/null 2>&1; then
    INPUT=$(timeout 5 cat 2>/dev/null) || INPUT=""
else
    # POSIX fallback: use read with timeout
    while IFS= read -r -t 5 line; do
        INPUT="${INPUT}${line}"$'\n'
    done
fi

# Extract session info with defensive JSON parsing
CWD=""
if echo "$INPUT" | jq -e '.' >/dev/null 2>&1; then
    CWD=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null || echo "")
fi

# Validate and normalize CWD atomically - fall back to current working directory
# shellcheck disable=SC2015 # Intentional: pwd fallback is safe even if cd succeeds
CWD="$(cd "${CWD:-.}" 2>/dev/null && pwd || pwd)"

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

# Extract all state information with a single jq invocation for efficiency
# Output format: iteration|branch|started_at|total_found|total_fixed
STATE_VALUES=$(echo "$STATE" | jq -r '[
    (.iteration // 0),
    (.branch // "unknown"),
    (.started_at // "unknown"),
    (.total_issues_found // 0),
    (.total_issues_fixed // 0)
] | join("|")' 2>/dev/null) || STATE_VALUES="0|unknown|unknown|0|0"

# Parse the pipe-separated values
IFS='|' read -r ITERATION BRANCH STARTED_AT TOTAL_FOUND TOTAL_FIXED <<< "$STATE_VALUES"

# Ensure defaults if parsing failed
: "${ITERATION:=0}"
: "${BRANCH:=unknown}"
: "${STARTED_AT:=unknown}"
: "${TOTAL_FOUND:=0}"
: "${TOTAL_FIXED:=0}"

# Output informational message using jq for proper JSON escaping
MESSAGE="Full CodeRabbit review in progress (iteration $ITERATION on branch '$BRANCH'). Started: $STARTED_AT. Issues: $TOTAL_FOUND found, $TOTAL_FIXED fixed. Run /full-cr-review --resume to continue."
jq -n --arg msg "$MESSAGE" '{systemMessage: $msg}'

exit 0
