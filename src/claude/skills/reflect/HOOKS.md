# Reflect Hooks Configuration

This document describes how to configure hooks for automatic learning detection.

## Overview

Hooks can trigger reflection automatically based on:

1. **Stop Hook:** Detect corrections at end of response
2. **PreToolUse Hook:** Load relevant learnings before skill execution
3. **SessionStart Hook:** Load context at session start

## Hook Configuration

Hooks are configured in `.claude/settings.json` or `.claude/settings.local.json`.

### Stop Hook - Correction Detection

Detects when a user may have made a correction and suggests reflection.

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "prompt",
        "prompt": "Analyze the user's last message for correction signals. If the user said 'no', 'wrong', 'not like that', 'I meant', or expressed frustration, respond with a JSON object: {\"decision\": \"suggest_reflect\", \"reason\": \"<brief reason>\"}. Otherwise respond: {\"decision\": \"continue\"}"
      }
    ]
  }
}
```

**Note:** Prompt-type hooks require the hook output to be processed. Consider using a command-type hook that outputs JSON for more control.

### Alternative: Command-Type Stop Hook

Create a script that checks for correction patterns:

**Windows (PowerShell script):**

```powershell
# .claude/hooks/detect-corrections.ps1
param([string]$UserMessage)

$correctionPatterns = @(
    "(?i)\bno\b",
    "(?i)\bwrong\b",
    "(?i)\bnot like that\b",
    "(?i)\bi meant\b",
    "(?i)\bactually\b",
    "(?i)\bstop\b"
)

$detected = $false
foreach ($pattern in $correctionPatterns) {
    if ($UserMessage -match $pattern) {
        $detected = $true
        break
    }
}

if ($detected) {
    @{
        decision = "block"
        reason = "Correction detected. Consider running /reflect to capture this learning."
    } | ConvertTo-Json
} else {
    @{ decision = "allow" } | ConvertTo-Json
}
```

**Configuration:**

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "powershell -File .claude/hooks/detect-corrections.ps1 -UserMessage \"$env:CLAUDE_USER_MESSAGE\""
      }
    ]
  }
}
```

**Shell environment variable syntax:**

- PowerShell: `$env:CLAUDE_USER_MESSAGE`
- cmd.exe: `%CLAUDE_USER_MESSAGE%`
- Bash/sh: `$CLAUDE_USER_MESSAGE`

### PreToolUse Hook - Proactive Loading

Load relevant learnings before a skill executes.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "type": "prompt",
        "prompt": "Before executing this skill, query Forgetful Memory for relevant learnings: mcp__forgetful__execute_forgetful_tool('query_memory', {query: '<skill-name> corrections preferences', query_context: 'Loading learnings before skill', tags: ['skill-learning'], k: 5}). Apply any relevant learnings to your approach."
      }
    ]
  }
}
```

Note: The `matcher` uses `""` to match all tools. Use patterns like `"mcp__forgetful__.*"` to target specific MCP tools.

### SessionStart Hook - Context Loading

Load general context at session start.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "prompt",
        "prompt": "At the start of this session, consider querying Forgetful Memory for any relevant learnings based on the project or task context."
      }
    ]
  }
}
```

## Recommended Configuration

For the reflect system, add this to your settings:

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "prompt",
        "prompt": "If the user's message contains correction signals (\"no\", \"wrong\", \"not like that\", \"I meant\", frustration), suggest: 'I noticed a correction. Would you like me to capture this as a learning with /reflect?'"
      }
    ]
  }
}
```

## Hook Types

| Type      | Description           | Output                     |
| --------- | --------------------- | -------------------------- |
| `command` | Runs shell command    | JSON with `decision` field |
| `prompt`  | Sends prompt to model | Text processed by Claude   |

### Command Hook Output Format

```json
{
  // decision options: "allow", "block", or "suggest_reflect"
  "decision": "allow",
  "reason": "Optional explanation",
  "systemMessage": "Optional message to inject"
}
```

### Decision Values

| Decision          | Behavior                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| `allow`           | Continue normally                                                                                      |
| `block`           | Stop and show reason                                                                                   |
| `suggest_reflect` | Continue but suggest reflection (project-specific custom convention, not a standard Claude hook value) |

## Environment Variables in Hooks

Available in command-type hooks:

| Variable               | Description                     |
| ---------------------- | ------------------------------- |
| `$CLAUDE_USER_MESSAGE` | The user's last message         |
| `$CLAUDE_TOOL_NAME`    | Tool being invoked (PreToolUse) |
| `$CLAUDE_SESSION_ID`   | Current session identifier      |

## Integration with Forgetful Memory

The proactive loading hook can inject learnings into the context:

```python
# Pseudocode - Query before skill execution
# Note: Forgetful returns learnings as a list of dicts, access fields via dictionary keys
learnings = mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "<skill> preferences corrections",
  "query_context": "Pre-loading for skill execution",
  "tags": ["skill-learning"],
  "k": 5
})

# Apply learnings to approach
# learnings is a list of dict objects, not objects with attributes
for learning in learnings:
    learning_type = learning.get("type") or learning.get("tags", [None])[0]
    if learning_type == "correction":
        # Avoid the corrected behavior
    elif learning_type == "preference":
        # Follow the preference
    elif learning_type == "anti-pattern":
        # Explicitly avoid this
```

## Testing Hooks

To test if hooks are working:

1. Add a test hook that logs to a file
2. Trigger the hook condition
3. Check the log file

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "echo 'Stop hook triggered' >> .claude/hook-test.log"
      }
    ]
  }
}
```

## Disabling Hooks

To temporarily disable hooks:

1. Comment out in settings.json
2. Or create `.claude/skills/reflect/.disabled` file (if using custom enable/disable logic)

## Troubleshooting

| Issue                | Solution                                        |
| -------------------- | ----------------------------------------------- |
| Hook not triggering  | Check matcher pattern matches file type         |
| Command fails        | Ensure script is executable and path is correct |
| Prompt hook ignored  | Verify prompt format returns expected structure |
| Too many suggestions | Adjust correction pattern sensitivity           |
