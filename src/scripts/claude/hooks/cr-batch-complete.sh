#!/bin/bash
# Full CR Review - Batch Complete Hook
# Tracks subagent batch completion and aggregates results
# Used as a SubagentStop hook within the full-cr-review command

set -euo pipefail

# Check for jq dependency before using it
if ! command -v jq >/dev/null 2>&1; then
    echo "Error: jq is required for JSON parsing but was not found in PATH" >&2
    exit 0  # Don't block on missing jq
fi

# Read hook input from stdin with timeout to prevent hanging
INPUT=""
if command -v timeout >/dev/null 2>&1; then
    INPUT=$(timeout 5 cat 2>/dev/null) || INPUT=""
elif read -r -t 5 -d '' INPUT 2>/dev/null; then
    : # read succeeded
else
    INPUT=""
fi

# Extract info with defensive JSON parsing
CWD=""
AGENT_RESULT=""
if echo "$INPUT" | jq -e '.' >/dev/null 2>&1; then
    CWD=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null || echo "")
    AGENT_RESULT=$(echo "$INPUT" | jq -r '.agent_result // empty' 2>/dev/null || echo "")
fi

# Validate CWD is a valid directory BEFORE using it
if [ -z "$CWD" ] || [ ! -d "$CWD" ]; then
    exit 0
fi

# Check for full CR review context marker
MARKER_FILE="${CWD}/.full-cr-in-progress"
RESULTS_FILE="${CWD}/.cr-batch-results.jsonl"

if [ ! -f "$MARKER_FILE" ]; then
    # Not in full CR review mode
    exit 0
fi

# Ensure parent directory exists for RESULTS_FILE
RESULTS_DIR=$(dirname "$RESULTS_FILE")
if [ ! -d "$RESULTS_DIR" ]; then
    mkdir -p "$RESULTS_DIR" 2>/dev/null || {
        echo "Warning: Cannot create directory for results file: $RESULTS_DIR" >&2
        exit 0
    }
fi

# Parse agent result for batch info
BATCH_ID=""
FIXED=0
SKIPPED=0
ROLLBACKS=0

if [ -n "$AGENT_RESULT" ] && echo "$AGENT_RESULT" | jq -e '.' >/dev/null 2>&1; then
    BATCH_ID=$(echo "$AGENT_RESULT" | jq -r '.batch_id // empty' 2>/dev/null || echo "")
    FIXED=$(echo "$AGENT_RESULT" | jq -r '.fixed // 0' 2>/dev/null || echo "0")
    SKIPPED=$(echo "$AGENT_RESULT" | jq -r '.skipped // 0' 2>/dev/null || echo "0")
    ROLLBACKS=$(echo "$AGENT_RESULT" | jq -r '.rollbacks // 0' 2>/dev/null || echo "0")
fi

# Create result entry
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RESULT_ENTRY=$(jq -n \
    --arg ts "$TIMESTAMP" \
    --arg batch_id "$BATCH_ID" \
    --argjson fixed "$FIXED" \
    --argjson skipped "$SKIPPED" \
    --argjson rollbacks "$ROLLBACKS" \
    '{timestamp: $ts, batch_id: $batch_id, fixed: $fixed, skipped: $skipped, rollbacks: $rollbacks}')

# Acquire exclusive lock before writing to prevent concurrent write races
LOCK_FILE="${RESULTS_FILE}.lock"

# Set up trap to clean up lock file on exit
cleanup_lock() {
    rm -f "$LOCK_FILE" 2>/dev/null || :
}
trap cleanup_lock EXIT

if command -v flock >/dev/null 2>&1; then
    (
        flock -x 200
        if ! echo "$RESULT_ENTRY" >> "$RESULTS_FILE" 2>/dev/null; then
            echo "Warning: Failed to append result to $RESULTS_FILE" >&2
        fi
    ) 200>"$LOCK_FILE" || {
        echo "Warning: Failed to acquire lock for $RESULTS_FILE" >&2
    }
    rm -f "$LOCK_FILE" 2>/dev/null || :
else
    # Fallback without flock (less safe but functional)
    if ! echo "$RESULT_ENTRY" >> "$RESULTS_FILE" 2>/dev/null; then
        echo "Warning: Failed to append result to $RESULTS_FILE" >&2
    fi
fi

# Update state file with latest counts
if [ -f "$MARKER_FILE" ] && [ -r "$MARKER_FILE" ]; then
    STATE=$(cat "$MARKER_FILE" 2>/dev/null) || STATE="{}"

    if echo "$STATE" | jq -e '.' >/dev/null 2>&1; then
        CURRENT_FIXED=$(echo "$STATE" | jq -r '.total_issues_fixed // 0' 2>/dev/null || echo "0")
        NEW_FIXED=$((CURRENT_FIXED + FIXED))

        # Update state with new fixed count
        UPDATED_STATE=$(echo "$STATE" | jq --argjson fixed "$NEW_FIXED" '.total_issues_fixed = $fixed')
        echo "$UPDATED_STATE" > "$MARKER_FILE"
    fi
fi

# Count completed batches
COMPLETED=$(wc -l < "$RESULTS_FILE" 2>/dev/null | tr -d ' ' || echo "0")
TOTAL=$(jq -r '.batch_count // 0' "$MARKER_FILE" 2>/dev/null || echo "0")

# Ensure we have valid numbers
if ! [[ "$COMPLETED" =~ ^[0-9]+$ ]]; then
    COMPLETED=0
fi
if ! [[ "$TOTAL" =~ ^[0-9]+$ ]]; then
    TOTAL=0
fi

# Output progress
if [ -n "$BATCH_ID" ]; then
    echo "Batch $BATCH_ID complete: $FIXED fixed, $SKIPPED skipped, $ROLLBACKS rollbacks ($COMPLETED of $TOTAL batches done)"
else
    echo "Batch completed ($COMPLETED of $TOTAL)"
fi

exit 0
