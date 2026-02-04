#!/bin/bash
# Full CR Review - Stop Hook
# Verifies all CodeRabbit beads are closed before allowing completion
# Used as a Stop hook within the full-cr-review command

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
    # Not in full CR review mode - allow stop
    exit 0
fi

# Check for beads CLI
if ! command -v bd >/dev/null 2>&1; then
    # Beads not available, can't check - allow stop with warning
    echo "Warning: beads CLI (bd) not found, skipping bead verification" >&2
    exit 0
fi

# Check for jq dependency
if ! command -v jq >/dev/null 2>&1; then
    echo "Warning: jq not found, skipping bead verification" >&2
    exit 0
fi

# Check for open CodeRabbit beads
# Note: beads uses --label not --tags
OPEN_COUNT=0
BEADS_OUTPUT=""

# Try to get open beads with coderabbit label
BEADS_OUTPUT=$(bd list --label coderabbit --status open --json 2>/dev/null) || BEADS_OUTPUT="[]"

# Parse the count
if echo "$BEADS_OUTPUT" | jq -e '.' >/dev/null 2>&1; then
    OPEN_COUNT=$(echo "$BEADS_OUTPUT" | jq '. | length' 2>/dev/null || echo "0")
fi

# Ensure we have a valid number
if ! [[ "$OPEN_COUNT" =~ ^[0-9]+$ ]]; then
    OPEN_COUNT=0
fi

if [ "$OPEN_COUNT" -gt 0 ]; then
    # Still have open beads - emit JSON that suggests continuation
    # Using "continue": true signals to Claude Code to continue the session
    cat <<EOF
{
  "continue": true,
  "systemMessage": "$OPEN_COUNT CodeRabbit beads still open. Consider running /full-cr-review --resume to continue fixing, or close them manually with 'bd close <id>'."
}
EOF
    exit 0
fi

# All beads closed - clean up marker and allow stop
rm -f "$MARKER_FILE"
rm -f "${CWD}/.cr-batch-results.jsonl"
rm -f "${CWD}/.cr-review-output.txt"

exit 0
