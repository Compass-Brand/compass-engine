# Ralph Patterns Deep Analysis for BMAD Review Loop

## Executive Summary

This document provides a comprehensive analysis of patterns extracted from:
- **Ralph Wiggum** (Claude Code plugin by Anthropic)
- **Ralph Orchestrator** (Production Python framework by mikeyobrien)

These patterns will enhance our BMAD review loop to ensure complete execution, robust error recovery, and proper state management.

---

## Part 1: Ralph Wiggum - Complete Technical Analysis

### 1.1 Core Architecture

Ralph Wiggum implements a **stop hook interception pattern** that prevents Claude from exiting until a task is truly complete.

```
User runs /ralph-loop → Setup creates state file → Claude works →
Claude attempts exit → Stop hook intercepts → Hook checks completion →
If incomplete: block exit, re-inject prompt → Loop continues →
If complete: allow exit, cleanup state
```

### 1.2 State File Format

**File:** `.claude/ralph-loop.local.md`

```markdown
---
active: true
iteration: 1
max_iterations: 50
completion_promise: "DONE"
started_at: "2026-01-15T12:00:00Z"
---

Your task prompt goes here
```

**Why Markdown with YAML frontmatter?**
- Human-readable state inspection
- Easy parsing with `sed` and `awk`
- Prompt stored after frontmatter (natural separation)
- Works with standard Unix tools

### 1.3 Stop Hook Implementation Details

**File:** `hooks/stop-hook.sh` (193 lines)

**Key techniques discovered:**

#### 1.3.1 Hook Input/Output API

```bash
# Hook receives JSON via stdin
HOOK_INPUT=$(cat)
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')

# Hook outputs JSON to control flow
jq -n \
  --arg prompt "$PROMPT_TEXT" \
  --arg msg "$SYSTEM_MSG" \
  '{
    "decision": "block",
    "reason": $prompt,
    "systemMessage": $msg
  }'
```

#### 1.3.2 JSONL Transcript Parsing

```bash
# Extract last assistant message
LAST_LINE=$(grep '"role":"assistant"' "$TRANSCRIPT_PATH" | tail -1)

# Parse JSON content with jq
LAST_OUTPUT=$(echo "$LAST_LINE" | jq -r '
  .message.content |
  map(select(.type == "text")) |
  map(.text) |
  join("\n")
' 2>&1)
```

**Transcript format (JSONL):**
```json
{"role": "assistant", "message": {"content": [{"type": "text", "text": "..."}]}}
```

#### 1.3.3 Completion Promise Detection with Perl

```bash
# Use Perl for multiline extraction (more reliable than sed)
PROMISE_TEXT=$(echo "$LAST_OUTPUT" | perl -0777 -pe \
  's/.*?<promise>(.*?)<\/promise>.*/\1/s; s/^\s+|\s+$//g; s/\s+/ /g' \
  2>/dev/null || echo "")

# CRITICAL: Use = not == for literal string comparison
# == in [[ ]] does glob pattern matching, breaking on *, ?, [
if [[ -n "$PROMISE_TEXT" ]] && [[ "$PROMISE_TEXT" = "$COMPLETION_PROMISE" ]]; then
  echo "Ralph loop: Detected <promise>$COMPLETION_PROMISE</promise>"
  rm "$RALPH_STATE_FILE"
  exit 0
fi
```

#### 1.3.4 Atomic File Updates

```bash
# Avoid sed -i (behaves differently on macOS vs Linux)
TEMP_FILE="${RALPH_STATE_FILE}.tmp.$$"  # PID suffix prevents conflicts
sed "s/^iteration: .*/iteration: $NEXT_ITERATION/" "$RALPH_STATE_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$RALPH_STATE_FILE"  # Atomic on POSIX
```

#### 1.3.5 Prompt Extraction (Handles --- in content)

```bash
# awk counts --- delimiters, prints after second one
# i>=2 (not i==2) handles additional --- in prompt content
PROMPT_TEXT=$(awk '/^---$/{i++; next} i>=2' "$RALPH_STATE_FILE")
```

### 1.4 Error Handling Philosophy

**Graceful degradation - fail open, not closed:**

```bash
if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  echo "Warning: Transcript file not found" >&2
  echo "  This may indicate a Claude Code internal issue" >&2
  rm "$RALPH_STATE_FILE"  # Cleanup
  exit 0  # Allow exit (don't trap user)
fi
```

| Error Condition | Response |
|-----------------|----------|
| Corrupted state file | Remove and allow exit |
| Missing transcript | Remove and allow exit |
| Invalid JSON | Remove and allow exit |
| No assistant messages | Remove and allow exit |
| Empty output | Remove and allow exit |

### 1.5 Anti-Circumvention Messaging

```
═══════════════════════════════════════════════════════════════
CRITICAL - Ralph Loop Completion Promise
═══════════════════════════════════════════════════════════════

To complete this loop, output this EXACT text:
  <promise>DONE</promise>

STRICT REQUIREMENTS (DO NOT VIOLATE):
  ✓ Use <promise> XML tags EXACTLY as shown
  ✓ The statement MUST be completely TRUE
  ✓ Do NOT output false statements to exit
  ✓ Do NOT lie even if you think you should exit
═══════════════════════════════════════════════════════════════
```

---

## Part 2: Ralph Orchestrator - Complete Technical Analysis

### 2.1 Architecture Overview

Ralph Orchestrator is a production-ready Python framework (~400 lines core) supporting multiple AI backends with robust error recovery.

```
src/ralph_orchestrator/
├── orchestrator.py      # Core loop engine (44KB)
├── context.py           # State persistence (8KB)
├── metrics.py           # Telemetry tracking (11KB)
├── safety.py            # Circuit breakers (5KB)
├── security.py          # Path/credential protection (15KB)
├── error_formatter.py   # Error classification (9KB)
├── async_logger.py      # Thread-safe logging (16KB)
└── adapters/            # AI provider integrations
    ├── base.py          # Abstract adapter interface
    ├── claude.py        # Claude SDK adapter
    ├── acp.py           # ACP protocol adapter
    ├── gemini.py        # Gemini CLI adapter
    └── kiro.py          # Kiro CLI adapter
```

### 2.2 Context Management Pattern

**ContextManager with four layers:**

```python
class ContextManager:
    stable_prefix: str       # Cached prompt header (hashed)
    dynamic_context: list    # Recent outputs (max 5)
    error_history: list      # Failed attempts (max 5)
    success_patterns: list   # Successful approaches (max 3)
```

**Memory limits for efficiency:**
- Dynamic context: 5 entries max
- Error history: 5 items max
- Individual outputs: truncated at 500 characters
- Max context size: 5000 chars (configurable)

### 2.3 Completion Detection (Three Mechanisms)

#### Mechanism 1: Checkbox Markers in PROMPT.md

```python
def _check_completion_marker(self) -> bool:
    """Search PROMPT.md for checked checkbox completion signals"""
    # Patterns detected:
    # - "- [x] TASK_COMPLETE"
    # - "[x] TASK_COMPLETE"
```

#### Mechanism 2: Completion Promise

```python
completion_promise: str = "LOOP_COMPLETE"  # default

# Case-insensitive substring matching against:
# - Agent output
# - Prompt content
# - Whitespace-normalized variants
```

#### Mechanism 3: Safety Limit Termination

```python
# Any of these triggers exit
max_iterations: int = 100
max_runtime: int = 14400  # 4 hours
max_cost: float = 10.00
max_consecutive_failures: int = 5
```

### 2.4 Error Recovery Mechanisms

#### 2.4.1 Exponential Backoff

```python
backoff_delay = min(2 ** failure_count, 60)  # seconds, capped at 60s
await asyncio.sleep(backoff_delay)
```

#### 2.4.2 Fallback Adapter Chain

```python
agent_priority = [
    AgentType.CLAUDE,
    AgentType.KIRO,
    AgentType.GEMINI,
    AgentType.Q,
    AgentType.ACP
]
# If primary fails, attempts next available
```

#### 2.4.3 Git Rollback

```python
if consecutive_failures >= 3:
    subprocess.run(["git", "reset", "--hard", "HEAD~1"])
```

#### 2.4.4 Error Classification

```python
class ClaudeErrorFormatter:
    @staticmethod
    def format_timeout_error(timeout: int) -> ErrorMessage
    def format_process_error(exit_code: int) -> ErrorMessage
    def format_connection_error() -> ErrorMessage
    def format_rate_limit_error() -> ErrorMessage
    def format_authentication_error() -> ErrorMessage
    def format_permission_error(path: str) -> ErrorMessage

    # Special cases:
    # Exit code 143 = SIGTERM (intentional stop)
    # Exit code 1 = credential/installation issue
```

### 2.5 Loop Detection via Fuzzy Matching

```python
from rapidfuzz import fuzz

SIMILARITY_THRESHOLD = 0.90  # 90%
OUTPUT_HISTORY_SIZE = 5      # sliding window

def detect_loop(self, output: str) -> bool:
    """Compare against last 5 outputs using fuzzy matching"""
    for prev_output in self.recent_outputs:
        ratio = fuzz.ratio(output, prev_output) / 100
        if ratio >= 0.90:
            return True
    return False
```

**Detection triggers:**
- Identical task attempts
- Oscillation between similar approaches
- Recurring error messages
- Number-only variations (still >90% similar)

### 2.6 Safety Guards (Circuit Breakers)

```python
class SafetyGuard:
    max_iterations: int = 100
    max_runtime: int = 14400        # 4 hours
    max_cost: float = 10.00
    max_consecutive_failures: int = 5

    def check_iteration_limit(self) -> bool
    def check_runtime_limit(self) -> bool
    def check_cost_limit(self, current_cost: float) -> bool
    def check_consecutive_failures(self) -> bool
    def check_average_duration(self) -> bool  # >5 min/iteration = halt
```

### 2.7 Metrics and Telemetry

```python
@dataclass
class Metrics:
    iterations: int = 0
    successes: int = 0
    failures: int = 0
    errors: int = 0
    checkpoints: int = 0
    rollbacks: int = 0

    def success_rate(self) -> float:
        return self.successes / max(1, self.iterations)

    def elapsed_hours(self) -> float:
        return (time.time() - self.start_time) / 3600

class TriggerReason(Enum):
    INITIAL = "initial"
    TASK_INCOMPLETE = "task_incomplete"
    RECOVERY = "recovery"
    PREVIOUS_SUCCESS = "previous_success"
    LOOP_DETECTED = "loop_detected"
    SAFETY_LIMIT = "safety_limit"
    USER_STOP = "user_stop"
```

### 2.8 Security Masking

```python
# 20+ patterns automatically redacted
SENSITIVE_PATTERNS = [
    r"sk-[a-zA-Z0-9]{48}",           # OpenAI keys
    r"xai-[a-zA-Z0-9]{48}",          # xAI keys
    r"AIza[a-zA-Z0-9_-]{35}",        # Google API keys
    r"Bearer\s+[a-zA-Z0-9._-]+",     # Bearer tokens
    r"password\s*=\s*['\"]?[^'\"\s]+", # Passwords
    r"ANTHROPIC_API_KEY=[^\s]+",     # Anthropic keys
    r"AWS_SECRET_ACCESS_KEY=[^\s]+", # AWS secrets
]
```

### 2.9 Scratchpad for Context Continuity

**File:** `.agent/scratchpad.md`

Persists across iterations, enabling context without restarting. Adapter injects:

```python
def _enhance_prompt_with_instructions(self, prompt: str) -> str:
    return f"""
{prompt}

---
## Orchestration Instructions

You are being executed in a loop by Ralph Orchestrator.

### Context Persistence
- Maintain `.agent/scratchpad.md` for state across iterations
- Record progress, decisions, and blockers

### Completion Signaling
- When task is complete, add: `- [x] TASK_COMPLETE`
- Or output: `LOOP_COMPLETE`

### Best Practices
- Follow TDD: write failing test first
- Make incremental progress each iteration
- Document decisions in scratchpad
"""
```

### 2.10 Git-Based Checkpointing

```python
checkpoint_interval: int = 10  # iterations

async def _create_checkpoint(self):
    """Non-blocking async git commit"""
    await asyncio.create_subprocess_exec(
        "git", "add", "-A",
        "git", "commit", "-m", f"[ralph] Checkpoint at iteration {n}"
    )
```

**State persistence structure:**
```
.agent/
├── metrics/
│   └── metrics_TIMESTAMP.json   # Per-session telemetry
├── logs/
│   └── ralph.log                # Rotating file handler
├── prompts/
│   └── prompt_*.md              # Archived prompts
└── scratchpad.md                # Agent context continuity
```

---

## Part 3: Patterns to Apply to BMAD Review Loop

### 3.1 Priority Matrix

| Pattern | Source | Priority | Effort | Impact |
|---------|--------|----------|--------|--------|
| Stop Hook | Ralph Wiggum | **HIGH** | Medium | Prevents premature exit |
| Completion Promises | Both | **HIGH** | Low | Clear completion signals |
| State File | Both | **HIGH** | Medium | Persistence across iterations |
| Loop Detection | Ralph Orchestrator | **HIGH** | Low | Prevents infinite loops |
| Exponential Backoff | Ralph Orchestrator | MEDIUM | Low | Graceful error recovery |
| Safety Guards | Ralph Orchestrator | MEDIUM | Low | Multiple circuit breakers |
| Context Manager | Ralph Orchestrator | MEDIUM | Medium | Better state tracking |
| Metrics/Telemetry | Ralph Orchestrator | LOW | Medium | Observability |
| Security Masking | Ralph Orchestrator | LOW | Low | Credential protection |
| Git Checkpointing | Ralph Orchestrator | LOW | Low | Recovery points |

### 3.2 Essential Patterns for Review Loop

#### Pattern 1: Stop Hook for Review Loop

```bash
#!/bin/bash
# .claude/hooks/review-loop-stop.sh
set -euo pipefail

HOOK_INPUT=$(cat)
STATE_FILE=".claude/review-loop-state.yaml"

# No active review loop - allow exit
[[ ! -f "$STATE_FILE" ]] && exit 0

# Parse state
PENDING=$(grep "pending_count:" "$STATE_FILE" | awk '{print $2}')
MAX_ROUNDS=$(grep "max_rounds:" "$STATE_FILE" | awk '{print $2}')
CURRENT_ROUND=$(grep "current_round:" "$STATE_FILE" | awk '{print $2}')

# Get transcript path and extract last output
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')
LAST_OUTPUT=$(grep '"role":"assistant"' "$TRANSCRIPT_PATH" | tail -1 | \
  jq -r '.message.content | map(select(.type == "text")) | map(.text) | join("\n")')

# Check for completion promise
if echo "$LAST_OUTPUT" | grep -q "<review-complete>ALL_ISSUES_RESOLVED</review-complete>"; then
  rm -f "$STATE_FILE"
  exit 0
fi

# Check max rounds
if [[ $CURRENT_ROUND -ge $MAX_ROUNDS ]]; then
  echo '{"decision": "allow", "reason": "Max review rounds reached"}'
  rm -f "$STATE_FILE"
  exit 0
fi

# Issues remain - block exit and continue
if [[ $PENDING -gt 0 ]]; then
  PROMPT=$(awk '/^---$/{i++; next} i>=2' "$STATE_FILE")

  # Increment round
  NEW_ROUND=$((CURRENT_ROUND + 1))
  TEMP="${STATE_FILE}.tmp.$$"
  sed "s/current_round: $CURRENT_ROUND/current_round: $NEW_ROUND/" "$STATE_FILE" > "$TEMP"
  mv "$TEMP" "$STATE_FILE"

  jq -n \
    --arg prompt "$PROMPT" \
    --arg msg "Review round $NEW_ROUND | $PENDING issues remain | Output <review-complete>ALL_ISSUES_RESOLVED</review-complete> when done" \
    '{"decision": "block", "reason": $prompt, "systemMessage": $msg}'
fi
```

#### Pattern 2: State File with YAML Frontmatter

```yaml
# .claude/review-loop-state.yaml
---
active: true
workflow_name: "create-prd"
section_name: "executive-summary"
content_path: "_bmad-output/planning-artifacts/prd.md"

# Iteration tracking
current_round: 1
max_rounds: 3
current_fix_iteration: 0
max_fix_iterations: 3

# Confidence tracking
initial_confidence: 72
current_confidence: 72
target_confidence: 95

# Issue tracking (task queue pattern)
total_issues: 8
pending_count: 5
in_progress_count: 0
fixed_count: 3
blocked_count: 0

# Error tracking (from Ralph Orchestrator)
consecutive_failures: 0
total_failures: 0
error_history: []

# Safety limits
max_consecutive_failures: 5
started_at: "2026-01-15T10:30:00Z"
last_updated: "2026-01-15T10:35:00Z"

# Completion promise
completion_promise: "ALL_ISSUES_RESOLVED"
---
# Original Prompt (for re-injection)
Review the PRD executive summary section for issues.
Dispatch parallel subagents: adversarial-reviewer, party-facilitator, elicitation-expert.
Fix ALL issues found.
Continue until 0 issues remain or max iterations reached.
Output <review-complete>ALL_ISSUES_RESOLVED</review-complete> when done.
```

#### Pattern 3: Completion Promise System

Three completion signals:

```xml
<!-- Success: All issues resolved -->
<review-complete>ALL_ISSUES_RESOLVED</review-complete>

<!-- Blocked: Manual intervention required -->
<review-blocked>MANUAL_INTERVENTION_REQUIRED</review-blocked>

<!-- Timeout: Max iterations reached -->
<review-timeout>MAX_ITERATIONS_REACHED</review-timeout>
```

#### Pattern 4: Loop Detection

```python
# Python implementation for review loop
from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.90
OUTPUT_HISTORY_SIZE = 5

def detect_loop(current_output: str, history: list[str]) -> bool:
    """Detect if we're stuck in a loop using fuzzy matching"""
    for prev_output in history[-OUTPUT_HISTORY_SIZE:]:
        ratio = SequenceMatcher(None, current_output, prev_output).ratio()
        if ratio >= SIMILARITY_THRESHOLD:
            return True
    return False
```

#### Pattern 5: Exponential Backoff

```python
def calculate_backoff(failure_count: int) -> int:
    """Calculate backoff delay with cap"""
    return min(2 ** failure_count, 60)  # Max 60 seconds

# In review loop:
if subagent_failed:
    delay = calculate_backoff(consecutive_failures)
    await asyncio.sleep(delay)
    consecutive_failures += 1

    if consecutive_failures >= 3:
        # Try alternative approach
        pass

    if consecutive_failures >= 5:
        # Escalate to user
        pass
```

#### Pattern 6: Safety Guards

```python
class ReviewLoopSafetyGuard:
    max_review_rounds: int = 3
    max_fix_iterations: int = 3
    max_consecutive_failures: int = 5
    max_runtime_seconds: int = 1800  # 30 minutes

    def should_halt(self, state: ReviewLoopState) -> tuple[bool, str]:
        if state.current_round >= self.max_review_rounds:
            return True, "Max review rounds reached"

        if state.consecutive_failures >= self.max_consecutive_failures:
            return True, "Too many consecutive failures"

        elapsed = time.time() - state.started_at
        if elapsed >= self.max_runtime_seconds:
            return True, "Max runtime exceeded"

        return False, ""
```

#### Pattern 7: Context Manager for Review Loop

```python
class ReviewLoopContext:
    """Four-layer context management (from Ralph Orchestrator)"""

    stable_context: str           # Original prompt, workflow info
    dynamic_context: list[str]    # Last 5 review outputs
    error_history: list[str]      # Last 5 errors (for debugging)
    success_patterns: list[str]   # Last 3 successful fix patterns

    MAX_DYNAMIC_ENTRIES = 5
    MAX_ERROR_ENTRIES = 5
    MAX_SUCCESS_ENTRIES = 3
    MAX_ENTRY_LENGTH = 500

    def add_review_output(self, output: str):
        truncated = output[:self.MAX_ENTRY_LENGTH]
        self.dynamic_context.append(truncated)
        if len(self.dynamic_context) > self.MAX_DYNAMIC_ENTRIES:
            self.dynamic_context.pop(0)

    def add_error(self, error: str):
        self.error_history.append(error[:self.MAX_ENTRY_LENGTH])
        if len(self.error_history) > self.MAX_ERROR_ENTRIES:
            self.error_history.pop(0)

    def add_success_pattern(self, pattern: str):
        self.success_patterns.append(pattern[:self.MAX_ENTRY_LENGTH])
        if len(self.success_patterns) > self.MAX_SUCCESS_ENTRIES:
            self.success_patterns.pop(0)
```

#### Pattern 8: Metrics Tracking

```python
@dataclass
class ReviewLoopMetrics:
    review_rounds: int = 0
    fix_iterations: int = 0
    total_issues_found: int = 0
    total_issues_fixed: int = 0
    total_issues_blocked: int = 0
    subagent_invocations: int = 0
    failures: int = 0
    backoff_delays_total: float = 0.0
    started_at: float = field(default_factory=time.time)

    def success_rate(self) -> float:
        total = self.total_issues_found
        return self.total_issues_fixed / max(1, total)

    def elapsed_minutes(self) -> float:
        return (time.time() - self.started_at) / 60
```

---

## Part 4: Updated Implementation Additions

Based on this analysis, add these tasks to the implementation plan:

### Task 12: Create Stop Hook

**File:** `.claude/hooks/review-loop-stop.sh`

Implements the stop hook pattern from Ralph Wiggum with:
- YAML state file parsing
- JSONL transcript parsing with jq
- Completion promise detection with Perl
- Atomic file updates
- Graceful error handling

### Task 13: Create Hooks Configuration

**File:** `.claude/hooks/hooks.json`

```json
{
  "description": "BMAD Review Loop stop hook",
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_ROOT}/.claude/hooks/review-loop-stop.sh"
          }
        ]
      }
    ]
  }
}
```

### Task 14: Create State File Template

**File:** `.claude/templates/review-loop-state.yaml`

Full YAML template with all tracking fields.

### Task 15: Add Loop Detection to Review Loop

Implement fuzzy matching with 90% threshold and 5-entry sliding window.

### Task 16: Add Safety Guards

Implement circuit breakers for:
- Max review rounds
- Max fix iterations
- Max consecutive failures
- Max runtime

### Task 17: Add Exponential Backoff

Implement `min(2^failures, 60)` delay pattern.

### Task 18: Add Context Manager

Implement four-layer context tracking.

### Task 19: Add Metrics Tracking

Implement telemetry for review loop performance.

### Task 20: Update Review Loop XML with All Patterns

Integrate all patterns into `review-loop.xml`.

---

## Part 5: Key Insights Summary

### From Ralph Wiggum

1. **Stop hooks are powerful** - Intercept exit, re-inject prompt
2. **State files should be human-readable** - Markdown + YAML
3. **Completion promises need XML tags** - `<promise>TEXT</promise>`
4. **Use Perl for multiline regex** - More reliable than sed
5. **Fail open, not closed** - Graceful degradation on errors
6. **Anti-circumvention messaging** - Prevent false promises

### From Ralph Orchestrator

1. **Four-layer context** - Stable, dynamic, errors, successes
2. **Three completion mechanisms** - Markers, promises, safety limits
3. **Loop detection via fuzzy matching** - 90% threshold
4. **Multiple safety guards** - Circuit breakers at every level
5. **Exponential backoff** - Cap at 60 seconds
6. **Bounded history** - Memory efficiency
7. **Git checkpointing** - Recovery points
8. **Metrics/telemetry** - Observability

### Combined Best Practices

1. **Always have a completion signal** - Never rely on implicit completion
2. **Always have safety limits** - Max iterations, max time, max cost
3. **Always track state in files** - Survives restarts
4. **Always handle errors gracefully** - Cleanup and allow exit
5. **Always detect loops** - Fuzzy matching prevents infinite loops
6. **Always provide escape hatches** - Users can always cancel
