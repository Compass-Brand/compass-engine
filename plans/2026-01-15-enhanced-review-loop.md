# Enhanced Review Loop Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the static [a/c/p/y] menu with an intelligent review loop that dispatches parallel subagents for reviews, tracks ALL issues in a task file, and assigns fixes to parallel subagents until 0 issues remain.

**Architecture:** The review loop intercepts template-output checkpoints in workflow.xml. Based on tier and confidence, it selects the appropriate review level (adversarial-only vs full trilogy). It dispatches parallel review subagents, aggregates findings into an issue tracking file, then dispatches parallel fix subagents. The loop continues until all issues are resolved.

**Tech Stack:** BMAD XML/YAML workflows, Claude Code Task tool for parallel subagents, Forgetful MCP for memory, Serena for code analysis, Context7 for framework docs.

---

## Overview

### Review Levels (Confidence-Based)

| Confidence | Review Level | Subagents Dispatched |
|------------|--------------|---------------------|
| < 95% | Full Trilogy | Party Mode + Adversarial + Advanced Elicitation |
| 95-98% | Dual Review | Party Mode + Adversarial (skip elicitation) |
| > 98% | Minimal | Adversarial only |

### Workflow Type Override

| Workflow Type | Minimum Review Level |
|---------------|---------------------|
| Quick Fix (Tier 0) | Adversarial only (regardless of confidence) |
| Small Feature (Tier 1) | Dual Review minimum |
| Medium+ (Tier 2-4) | Full Trilogy minimum |

### Files to Create

```
_bmad/core/tasks/review-loop.xml              # Core review loop engine
_bmad/core/agents/adversarial-reviewer.md     # Adversarial review subagent prompt
_bmad/core/agents/party-facilitator.md        # Party mode subagent prompt
_bmad/core/agents/elicitation-expert.md       # Advanced elicitation subagent prompt
_bmad/core/agents/issue-fixer.md              # Fix subagent prompt
_bmad/core/templates/issue-tracker.md         # Issue tracking file template
```

### Files to Modify

```
_bmad/core/tasks/workflow.xml                 # Step 2c: invoke review-loop
_bmad/core/automation-runtime.md              # Add review loop section
_bmad/bmm/config.yaml                         # Add review_loop configuration
```

---

## Task 1: Create Issue Tracker Template

**Files:**
- Create: `_bmad/core/templates/issue-tracker.md`

**Step 1.1: Create the template file**

Create file with this content:

```markdown
# Issue Tracker - {{workflow_name}}

Generated: {{date}}
Workflow: {{workflow_path}}
Section: {{section_name}}
Confidence: {{confidence}}%

---

## Summary

| Metric | Value |
|--------|-------|
| Total Issues | {{total_count}} |
| Critical | {{critical_count}} |
| High | {{high_count}} |
| Medium | {{medium_count}} |
| Low | {{low_count}} |
| Fixed | {{fixed_count}} |
| Remaining | {{remaining_count}} |

---

## Issues

<!-- ISSUES_START -->
<!-- Issues will be appended here by review subagents -->
<!-- ISSUES_END -->

---

## Fix Log

<!-- FIXES_START -->
<!-- Fix completions will be logged here -->
<!-- FIXES_END -->
```

**Step 1.2: Verify file created**

Run: `dir _bmad\core\templates\issue-tracker.md`
Expected: File exists

**Step 1.3: Commit**

```bash
git add _bmad/core/templates/issue-tracker.md
git commit -m "feat(bmad): add issue tracker template for review loop"
```

---

## Task 2: Create Adversarial Reviewer Subagent Prompt

**Files:**
- Create: `_bmad/core/agents/adversarial-reviewer.md`

**Step 2.1: Write the subagent prompt**

Create file with frontmatter and full prompt. Key sections:

1. **YAML Frontmatter:**
   - name: adversarial-reviewer
   - description: Parallel subagent for adversarial review - finds 3-10 specific issues
   - model: sonnet

2. **MCP Integration Requirements (CRITICAL):**
   - Forgetful Memory: Query for similar past reviews and known issues
   - Serena Symbol Analysis: For code, trace symbols and references
   - Context7 Framework Docs: For framework code, validate against official patterns

3. **Review Process:**
   - Load context (read content, query Forgetful, use Serena/Context7)
   - Find issues (MINIMUM 3, TARGET 5-10)
   - Categorize each with: ID, Severity, Category, Description, Location, Suggested Fix, Evidence

4. **Output Format:** YAML with reviewer info, issues array, summary

5. **Critical Rules:**
   - NEVER approve with 0 issues
   - ALL severity levels matter
   - Be specific (no vague issues)
   - Provide evidence
   - Use MCP tools

**Step 2.2: Verify file created**

Run: `type _bmad\core\agents\adversarial-reviewer.md | findstr "adversarial-reviewer"`
Expected: `name: adversarial-reviewer`

**Step 2.3: Commit**

```bash
git add _bmad/core/agents/adversarial-reviewer.md
git commit -m "feat(bmad): add adversarial reviewer subagent with MCP integration"
```

---

## Task 3: Create Party Facilitator Subagent Prompt

**Files:**
- Create: `_bmad/core/agents/party-facilitator.md`

**Step 3.1: Write the subagent prompt**

Create file with frontmatter and full prompt. Key sections:

1. **YAML Frontmatter:**
   - name: party-facilitator
   - description: Parallel subagent for party mode - multi-perspective review discussion
   - model: sonnet

2. **MCP Integration Requirements (CRITICAL):**
   - Forgetful Memory: Load agent personas and past discussions
   - Serena Symbol Analysis: For code discussions
   - Context7 Framework Docs: For framework discussions

3. **Agent Roster:** Load from `_bmad/_config/agent-manifest.csv`, select 3-5 based on content type

4. **Discussion Process:**
   - Setup (1 round): Present content, each agent states concern
   - Discussion (2-3 rounds): Cross-examination, use MCP for verification
   - Synthesis (1 round): Consensus, disagreements, severity votes

5. **Output Format:** YAML with agents consulted, discussion summary, issues with votes

6. **Critical Rules:**
   - Authentic personas
   - Real disagreement
   - Evidence-based
   - Minimum 2 rounds
   - Vote on severity

**Step 3.2: Verify file created**

Run: `type _bmad\core\agents\party-facilitator.md | findstr "party-facilitator"`
Expected: `name: party-facilitator`

**Step 3.3: Commit**

```bash
git add _bmad/core/agents/party-facilitator.md
git commit -m "feat(bmad): add party facilitator subagent with MCP integration"
```

---

## Task 4: Create Elicitation Expert Subagent Prompt

**Files:**
- Create: `_bmad/core/agents/elicitation-expert.md`

**Step 4.1: Write the subagent prompt**

Create file with frontmatter and full prompt. Key sections:

1. **YAML Frontmatter:**
   - name: elicitation-expert
   - description: Parallel subagent for advanced elicitation - deep questioning
   - model: sonnet

2. **MCP Integration Requirements (CRITICAL):**
   - Forgetful Memory: Query for past elicitation sessions and discovered gaps
   - Serena Symbol Analysis: Find TODOs, FIXMEs, incomplete implementations
   - Context7 Framework Docs: Check completeness against framework requirements

3. **Elicitation Methods:** 5 Whys, Assumption Surfacing, Edge Case Exploration, Stakeholder Mapping, Failure Mode Analysis, Constraint Identification, Dependency Mapping

4. **Process:**
   - Context Analysis: Read content, query Forgetful, select methods
   - Method Application (3-5 methods): Apply systematically, document questions
   - Gap Synthesis: Compile gaps, categorize, assess severity

5. **Output Format:** YAML with methods applied, issues by category

6. **Critical Rules:**
   - Apply multiple methods
   - Document questions
   - Flag unanswered questions as issues
   - Use evidence
   - No softballing

**Step 4.2: Verify file created**

Run: `type _bmad\core\agents\elicitation-expert.md | findstr "elicitation-expert"`
Expected: `name: elicitation-expert`

**Step 4.3: Commit**

```bash
git add _bmad/core/agents/elicitation-expert.md
git commit -m "feat(bmad): add elicitation expert subagent with MCP integration"
```

---

## Task 5: Create Issue Fixer Subagent Prompt

**Files:**
- Create: `_bmad/core/agents/issue-fixer.md`

**Step 5.1: Write the subagent prompt**

Create file with frontmatter and full prompt. Key sections:

1. **YAML Frontmatter:**
   - name: issue-fixer
   - description: Parallel subagent for fixing assigned issues
   - model: sonnet

2. **MCP Integration Requirements (CRITICAL):**
   - Forgetful Memory: Query for similar past fixes, save fix patterns after fixing
   - Serena Symbol Analysis: Understand code context, apply fixes using symbolic editing
   - Context7 Framework Docs: Verify fixes follow framework patterns

3. **Input Format:** YAML with assigned_issues array (id, severity, category, description, location, suggested_fix, content_path)

4. **Fix Process (for EACH issue):**
   - Understand Context: Read content, query Forgetful, use Serena/Context7
   - Apply Fix: Follow suggested_fix or devise better solution
   - Verify Fix: Confirm resolved, check for regressions
   - Record Fix: Save pattern to Forgetful

5. **Output Format:** YAML with fixes_applied array (status: FIXED or BLOCKED, fix_description, files_modified, verification, memory_saved)

6. **Critical Rules:**
   - Fix ALL assigned issues
   - Verify each fix
   - Record patterns to memory
   - Report blockers clearly
   - No scope creep

**Step 5.2: Verify file created**

Run: `type _bmad\core\agents\issue-fixer.md | findstr "issue-fixer"`
Expected: `name: issue-fixer`

**Step 5.3: Commit**

```bash
git add _bmad/core/agents/issue-fixer.md
git commit -m "feat(bmad): add issue fixer subagent with MCP integration"
```

---

## Task 6: Create Review Loop Task Engine

**Files:**
- Create: `_bmad/core/tasks/review-loop.xml`

**Step 6.1: Write the review loop engine**

Create XML task with these key sections:

1. **Task Definition:**
   - id: `_bmad/core/tasks/review-loop.xml`
   - name: Enhanced Review Loop
   - objective: Execute confidence-based parallel review with issue tracking and fix loop

2. **LLM Mandates:**
   - Main agent is ORCHESTRATOR ONLY
   - MUST use parallel Task tool calls
   - ALL issues must be fixed
   - Write issue tracker BEFORE dispatching fix subagents

3. **Input Parameters:**
   - content_path, section_name, workflow_name, tier, output_folder

4. **Flow Steps:**

   **Step 1: Calculate Confidence and Select Review Level**
   - 1a: Calculate base confidence per automation-runtime.md
   - 1b: Determine review level based on tier and confidence thresholds
   - 1c: Present choice to user: [R] Review or [C] Continue

   **Step 2: Dispatch Parallel Review Subagents**
   - 2a: Initialize issue tracker file
   - 2b: Dispatch review subagents in SINGLE message with MULTIPLE Task calls
   - 2c: Aggregate review results (deduplicate, merge severity)
   - 2d: Update issue tracker file

   **Step 3: Issue Resolution Loop**
   - 3a: Check issue count (if 0, exit)
   - 3b: Assign issues to fix subagents (distribute evenly, prioritize by severity)
   - 3c: Dispatch fix subagents in parallel
   - 3d: Collect results, update tracker (FIXED or BLOCKED)
   - 3e: Check remaining (if 0, proceed; if blocked, escalate; if remaining and iterations < 3, loop)

   **Step 4: Post-Fix Confidence Check**
   - 4a: Recalculate confidence (+15% if all fixed)
   - 4b: If < 95% and rounds < 3, go back to Step 2

5. **Safety Rules:**
   - Max 3 review rounds
   - Max 3 fix iterations per round
   - Always update issue tracker
   - Never skip issues based on severity
   - Blocked issues require user decision

**Step 6.2: Verify file created**

Run: `type _bmad\core\tasks\review-loop.xml | findstr "review-loop"`
Expected: `id="_bmad/core/tasks/review-loop.xml"`

**Step 6.3: Commit**

```bash
git add _bmad/core/tasks/review-loop.xml
git commit -m "feat(bmad): add review loop task engine with parallel subagent dispatch"
```

---

## Task 7: Modify workflow.xml Step 2c

**Files:**
- Modify: `_bmad/core/tasks/workflow.xml` (lines ~99-138)

**Step 7.1: Read current Step 2c**

Run: `type _bmad\core\tasks\workflow.xml`
Find substep n="2c"

**Step 7.2: Replace Step 2c with review loop invocation**

Replace the entire substep 2c block with:

```xml
<substep n="2c" title="Handle template-output Tags (Review Loop)">
  <if tag="template-output">
    <mandate>Generate content for this section</mandate>
    <mandate>Save to file (Write first time, Edit subsequent)</mandate>
    <action>Display generated content</action>

    <!-- INVOKE ENHANCED REVIEW LOOP -->
    <invoke-task path="_bmad/core/tasks/review-loop.xml">
      <param name="content_path">{current_output_file}</param>
      <param name="section_name">{current_section}</param>
      <param name="workflow_name">{workflow_name}</param>
      <param name="tier">{CURRENT_TIER}</param>
      <param name="output_folder">{output_folder}</param>
    </invoke-task>
  </if>
</substep>
```

**Step 7.3: Verify modification**

Run: `type _bmad\core\tasks\workflow.xml | findstr "review-loop"`
Expected: Shows invoke-task with review-loop.xml

**Step 7.4: Commit**

```bash
git add _bmad/core/tasks/workflow.xml
git commit -m "feat(bmad): integrate review loop into workflow.xml Step 2c"
```

---

## Task 8: Add Review Loop Configuration to BMM Config

**Files:**
- Modify: `_bmad/bmm/config.yaml`

**Step 8.1: Read current config**

Run: `type _bmad\bmm\config.yaml`
Find the automation section

**Step 8.2: Add review_loop configuration**

Add after the automation.progress section (around line 195):

```yaml
  # Review Loop Configuration
  review_loop:
    enabled: true

    # Confidence thresholds for review level selection
    confidence_thresholds:
      minimal: 98    # >98% = adversarial only
      dual: 95       # 95-98% = party + adversarial
      full: 0        # <95% = all three

    # Tier-based minimum review levels
    tier_minimums:
      0: minimal     # Quick fix = adversarial only
      1: dual        # Small feature = party + adversarial
      2: full        # Medium+ = full trilogy
      3: full
      4: full

    # Subagent configuration
    subagents:
      adversarial:
        model: sonnet
        timeout: 120
        required_issues: 3
      party:
        model: sonnet
        timeout: 180
        min_agents: 3
        max_rounds: 3
      elicitation:
        model: sonnet
        timeout: 120
        min_methods: 3
      fixer:
        model: sonnet
        timeout: 120
        max_issues_per_agent: 5

    # Loop limits
    limits:
      max_review_rounds: 3
      max_fix_iterations: 3
      max_concurrent_fixers: 3

    # Issue tracking
    issue_tracker:
      output_dir: "{output_folder}/reviews"
      filename_pattern: "{section_name}-issues.md"
      save_fix_patterns: true
```

**Step 8.3: Verify modification**

Run: `type _bmad\bmm\config.yaml | findstr "review_loop"`
Expected: `review_loop:`

**Step 8.4: Commit**

```bash
git add _bmad/bmm/config.yaml
git commit -m "feat(bmad): add review loop configuration to BMM config"
```

---

## Task 9: Update automation-runtime.md

**Files:**
- Modify: `_bmad/core/automation-runtime.md`

**Step 9.1: Read current file**

Run: `type _bmad\core\automation-runtime.md`

**Step 9.2: Add Review Loop section after Menu Handling**

Add new section after the Menu Handling section (around line 134):

```markdown
---

## Review Loop

When template-output checkpoints are reached, the enhanced review loop replaces the static menu.

### Review Level Selection

Based on tier and confidence:

| Tier | Confidence | Review Level | Subagents |
|------|------------|--------------|-----------|
| 0 | Any | Minimal | Adversarial only |
| 1 | Any | Dual | Party + Adversarial |
| 2-4 | > 98% | Minimal | Adversarial only |
| 2-4 | 95-98% | Dual | Party + Adversarial |
| 2-4 | < 95% | Full | Party + Adversarial + Elicitation |

### User Choice

At each checkpoint, present:

    Section: {section_name}
    Confidence: {confidence}%
    Recommended: {review_level}

    [R] Review for issues
    [C] Continue without review

### Parallel Subagent Dispatch

CRITICAL: All review subagents must be dispatched in a SINGLE message with multiple Task tool calls.

The orchestrating agent does NOT do the review work. It dispatches subagents and aggregates results.

### Issue Tracking

Before dispatching fix subagents:
1. Create issue tracker file at: {output_folder}/reviews/{section_name}-issues.md
2. Write ALL issues from all reviewers to the file
3. Then dispatch fix subagents with assigned issues

### Fix Assignment

- Calculate fix subagent count: min(3, ceil(total_issues / 3))
- Distribute issues evenly
- Prioritize: Critical > High > Medium > Low
- ALL issues must be assigned (no skipping)

### Loop Continuation

After fixes:
1. Recalculate confidence
2. If confidence >= 95%: Exit loop, continue workflow
3. If confidence < 95% and rounds < 3: Start new review round
4. If rounds >= 3: Escalate to user
```

**Step 9.3: Verify modification**

Run: `type _bmad\core\automation-runtime.md | findstr "Review Loop"`
Expected: `## Review Loop`

**Step 9.4: Commit**

```bash
git add _bmad/core/automation-runtime.md
git commit -m "feat(bmad): add review loop section to automation-runtime.md"
```

---

## Task 10: Create Reviews Output Directory

**Files:**
- Create: `_bmad-output/reviews/.gitkeep`

**Step 10.1: Create directory and gitkeep**

```bash
mkdir _bmad-output\reviews
echo. > _bmad-output\reviews\.gitkeep
```

**Step 10.2: Commit**

```bash
git add _bmad-output/reviews/.gitkeep
git commit -m "feat(bmad): add reviews output directory for issue tracking"
```

---

## Task 11: Final Integration Test

**Step 11.1: Verify all files exist**

Run:
```bash
dir _bmad\core\templates\issue-tracker.md
dir _bmad\core\agents\adversarial-reviewer.md
dir _bmad\core\agents\party-facilitator.md
dir _bmad\core\agents\elicitation-expert.md
dir _bmad\core\agents\issue-fixer.md
dir _bmad\core\tasks\review-loop.xml
```

Expected: All files exist

**Step 11.2: Verify workflow.xml integration**

Run: `type _bmad\core\tasks\workflow.xml | findstr "invoke-task"`
Expected: Shows review-loop.xml invocation

**Step 11.3: Verify config has review_loop section**

Run: `type _bmad\bmm\config.yaml | findstr "review_loop"`
Expected: `review_loop:`

**Step 11.4: Final commit (if any uncommitted changes)**

```bash
git status
git add .
git commit -m "feat(bmad): complete enhanced review loop implementation"
```

---

## Task 12: Create Stop Hook Script

**Files:**
- Create: `.claude/hooks/review-loop-stop.sh`

**Step 12.1: Create hooks directory**

```bash
mkdir -p .claude/hooks
```

**Step 12.2: Write the stop hook script**

Create file with this content (implements Ralph Wiggum patterns):

```bash
#!/bin/bash
# BMAD Review Loop Stop Hook
# Prevents premature exit until all issues are resolved
# Based on Ralph Wiggum patterns
set -euo pipefail

# Hook receives JSON via stdin
HOOK_INPUT=$(cat)
STATE_FILE=".claude/review-loop-state.yaml"

# No active review loop - allow exit
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0
fi

# Graceful degradation - if state file is corrupted, allow exit
if ! grep -q "^active:" "$STATE_FILE" 2>/dev/null; then
  echo "Warning: Corrupted state file, allowing exit" >&2
  rm -f "$STATE_FILE"
  exit 0
fi

# Parse state fields
ACTIVE=$(grep "^active:" "$STATE_FILE" | awk '{print $2}' || echo "false")
PENDING=$(grep "^pending_count:" "$STATE_FILE" | awk '{print $2}' || echo "0")
MAX_ROUNDS=$(grep "^max_rounds:" "$STATE_FILE" | awk '{print $2}' || echo "3")
CURRENT_ROUND=$(grep "^current_round:" "$STATE_FILE" | awk '{print $2}' || echo "1")
CONSECUTIVE_FAILURES=$(grep "^consecutive_failures:" "$STATE_FILE" | awk '{print $2}' || echo "0")
MAX_FAILURES=$(grep "^max_consecutive_failures:" "$STATE_FILE" | awk '{print $2}' || echo "5")
COMPLETION_PROMISE=$(grep "^completion_promise:" "$STATE_FILE" | awk '{print $2}' || echo "ALL_ISSUES_RESOLVED")

# Not active - allow exit
if [[ "$ACTIVE" != "true" ]]; then
  rm -f "$STATE_FILE"
  exit 0
fi

# Get transcript path and extract last assistant output
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path // empty' 2>/dev/null || echo "")

if [[ -z "$TRANSCRIPT_PATH" ]] || [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  echo "Warning: Transcript file not found, allowing exit" >&2
  rm -f "$STATE_FILE"
  exit 0
fi

# Extract last assistant message using JSONL parsing
LAST_OUTPUT=$(grep '"role":"assistant"' "$TRANSCRIPT_PATH" 2>/dev/null | tail -1 | \
  jq -r '.message.content | map(select(.type == "text")) | map(.text) | join("\n")' 2>/dev/null || echo "")

if [[ -z "$LAST_OUTPUT" ]]; then
  echo "Warning: No assistant output found, allowing exit" >&2
  rm -f "$STATE_FILE"
  exit 0
fi

# Check for completion promise using Perl for multiline regex
PROMISE_TEXT=$(echo "$LAST_OUTPUT" | perl -0777 -pe \
  's/.*?<review-complete>(.*?)<\/review-complete>.*/\1/s; s/^\s+|\s+$//g; s/\s+/ /g' \
  2>/dev/null || echo "")

# CRITICAL: Use = not == for literal string comparison
if [[ -n "$PROMISE_TEXT" ]] && [[ "$PROMISE_TEXT" = "$COMPLETION_PROMISE" ]]; then
  echo "Review loop complete: Detected <review-complete>$COMPLETION_PROMISE</review-complete>"
  rm -f "$STATE_FILE"
  exit 0
fi

# Check for blocked signal
BLOCKED_TEXT=$(echo "$LAST_OUTPUT" | perl -0777 -pe \
  's/.*?<review-blocked>(.*?)<\/review-blocked>.*/\1/s; s/^\s+|\s+$//g' \
  2>/dev/null || echo "")

if [[ -n "$BLOCKED_TEXT" ]]; then
  echo "Review loop blocked: $BLOCKED_TEXT - escalating to user"
  rm -f "$STATE_FILE"
  exit 0
fi

# Check max rounds safety limit
if [[ $CURRENT_ROUND -ge $MAX_ROUNDS ]]; then
  echo '{"decision": "allow", "reason": "Max review rounds reached - escalating to user"}'
  rm -f "$STATE_FILE"
  exit 0
fi

# Check consecutive failures safety limit
if [[ $CONSECUTIVE_FAILURES -ge $MAX_FAILURES ]]; then
  echo '{"decision": "allow", "reason": "Too many consecutive failures - escalating to user"}'
  rm -f "$STATE_FILE"
  exit 0
fi

# Issues remain - block exit and continue
if [[ $PENDING -gt 0 ]]; then
  # Extract original prompt (after second --- delimiter)
  PROMPT=$(awk '/^---$/{i++; next} i>=2' "$STATE_FILE")

  # Increment round counter atomically
  NEW_ROUND=$((CURRENT_ROUND + 1))
  TEMP="${STATE_FILE}.tmp.$$"
  sed "s/^current_round: $CURRENT_ROUND/current_round: $NEW_ROUND/" "$STATE_FILE" > "$TEMP"

  # Update last_updated timestamp
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  sed -i "s/^last_updated: .*/last_updated: \"$TIMESTAMP\"/" "$TEMP" 2>/dev/null || true

  mv "$TEMP" "$STATE_FILE"

  # Build system message
  SYSTEM_MSG="═══════════════════════════════════════════════════════════════
BMAD REVIEW LOOP - ROUND $NEW_ROUND / $MAX_ROUNDS
═══════════════════════════════════════════════════════════════

$PENDING issues remain to be resolved.

To complete this review loop, output this EXACT text when ALL issues are fixed:
  <review-complete>$COMPLETION_PROMISE</review-complete>

STRICT REQUIREMENTS:
  ✓ Fix ALL remaining issues before signaling completion
  ✓ Do NOT output completion signal if issues remain
  ✓ If blocked, output: <review-blocked>REASON</review-blocked>
═══════════════════════════════════════════════════════════════"

  jq -n \
    --arg prompt "$PROMPT" \
    --arg msg "$SYSTEM_MSG" \
    '{"decision": "block", "reason": $prompt, "systemMessage": $msg}'
  exit 0
fi

# No pending issues - allow exit
rm -f "$STATE_FILE"
exit 0
```

**Step 12.3: Make script executable**

```bash
chmod +x .claude/hooks/review-loop-stop.sh
```

**Step 12.4: Verify file created**

Run: `dir .claude\hooks\review-loop-stop.sh`
Expected: File exists

**Step 12.5: Commit**

```bash
git add .claude/hooks/review-loop-stop.sh
git commit -m "feat(bmad): add review loop stop hook (Ralph Wiggum pattern)"
```

---

## Task 13: Create Hooks Configuration

**Files:**
- Create: `.claude/hooks/hooks.json`

**Step 13.1: Write the hooks configuration**

Create file with this content:

```json
{
  "description": "BMAD Review Loop stop hook - prevents premature exit until all issues resolved",
  "hooks": {
    "Stop": [
      {
        "matcher": "",
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

**Step 13.2: Verify file created**

Run: `type .claude\hooks\hooks.json`
Expected: JSON content with Stop hook configuration

**Step 13.3: Commit**

```bash
git add .claude/hooks/hooks.json
git commit -m "feat(bmad): add hooks configuration for review loop"
```

---

## Task 14: Create State File Template

**Files:**
- Create: `.claude/templates/review-loop-state.yaml`

**Step 14.1: Create templates directory**

```bash
mkdir -p .claude/templates
```

**Step 14.2: Write the state file template**

Create file with this content:

```yaml
# BMAD Review Loop State File
# Generated by review-loop.xml when review starts
# Parsed by review-loop-stop.sh hook
---
active: true
workflow_name: "{{workflow_name}}"
section_name: "{{section_name}}"
content_path: "{{content_path}}"

# Iteration tracking
current_round: 1
max_rounds: 3
current_fix_iteration: 0
max_fix_iterations: 3

# Confidence tracking
initial_confidence: {{initial_confidence}}
current_confidence: {{current_confidence}}
target_confidence: 95

# Issue tracking (task queue pattern from Ralph Orchestrator)
total_issues: 0
pending_count: 0
in_progress_count: 0
fixed_count: 0
blocked_count: 0

# Error tracking (from Ralph Orchestrator)
consecutive_failures: 0
total_failures: 0
error_history: []

# Output history for loop detection (from Ralph Orchestrator)
output_hashes: []

# Safety limits
max_consecutive_failures: 5
started_at: "{{started_at}}"
last_updated: "{{last_updated}}"

# Completion promise (parsed by stop hook)
completion_promise: "ALL_ISSUES_RESOLVED"
---
# Original Prompt (re-injected by stop hook on continue)
{{original_prompt}}
```

**Step 14.3: Verify file created**

Run: `type .claude\templates\review-loop-state.yaml`
Expected: YAML template content

**Step 14.4: Commit**

```bash
git add .claude/templates/review-loop-state.yaml
git commit -m "feat(bmad): add review loop state file template"
```

---

## Task 15: Add Loop Detection Module

**Files:**
- Create: `_bmad/core/lib/loop_detection.py`

**Step 15.1: Create lib directory**

```bash
mkdir -p _bmad/core/lib
```

**Step 15.2: Write loop detection module**

Create file with this content:

```python
"""Loop detection for BMAD review loop using fuzzy matching.

Based on Ralph Orchestrator's loop detection pattern.
Uses standard library difflib for fuzzy matching (no external deps).
"""

from difflib import SequenceMatcher
import hashlib
from typing import List


SIMILARITY_THRESHOLD = 0.90  # 90% similarity = loop detected
OUTPUT_HISTORY_SIZE = 5      # Sliding window of recent outputs


def compute_hash(text: str) -> str:
    """Compute SHA256 hash of text for quick comparison."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def detect_loop(current_output: str, history: List[str]) -> bool:
    """Detect if we're stuck in a loop using fuzzy matching.

    Args:
        current_output: The current output to check
        history: List of recent outputs (up to OUTPUT_HISTORY_SIZE)

    Returns:
        True if loop detected (current output is >=90% similar to any in history)
    """
    if not current_output or not history:
        return False

    # Check against last N outputs
    for prev_output in history[-OUTPUT_HISTORY_SIZE:]:
        if not prev_output:
            continue

        # Use SequenceMatcher for fuzzy comparison
        ratio = SequenceMatcher(None, current_output, prev_output).ratio()

        if ratio >= SIMILARITY_THRESHOLD:
            return True

    return False


def normalize_output(output: str) -> str:
    """Normalize output for comparison.

    Removes timestamps, IDs, and other variable content that shouldn't
    affect loop detection.
    """
    import re

    # Remove timestamps
    output = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '', output)
    # Remove UUIDs
    output = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '', output)
    # Normalize whitespace
    output = re.sub(r'\s+', ' ', output).strip()

    return output


class LoopDetector:
    """Stateful loop detector with history management."""

    def __init__(
        self,
        threshold: float = SIMILARITY_THRESHOLD,
        history_size: int = OUTPUT_HISTORY_SIZE
    ):
        self.threshold = threshold
        self.history_size = history_size
        self.history: List[str] = []
        self.hash_history: List[str] = []

    def check(self, output: str) -> bool:
        """Check if output indicates a loop and update history.

        Returns True if loop detected.
        """
        normalized = normalize_output(output)

        # Quick hash check first
        output_hash = compute_hash(normalized)
        if output_hash in self.hash_history:
            return True

        # Fuzzy check
        if detect_loop(normalized, self.history):
            return True

        # Not a loop - add to history
        self.history.append(normalized)
        self.hash_history.append(output_hash)

        # Maintain sliding window
        if len(self.history) > self.history_size:
            self.history.pop(0)
            self.hash_history.pop(0)

        return False

    def clear(self):
        """Clear history (call on successful completion)."""
        self.history.clear()
        self.hash_history.clear()

    def get_hashes(self) -> List[str]:
        """Get current hash history for state persistence."""
        return list(self.hash_history)

    def restore_hashes(self, hashes: List[str]):
        """Restore hash history from state file."""
        self.hash_history = list(hashes)[-self.history_size:]
```

**Step 15.3: Write test file**

Create `tests/bmad_core/test_loop_detection.py`:

```python
"""Tests for BMAD loop detection module."""

import pytest
from _bmad.core.lib.loop_detection import (
    detect_loop,
    compute_hash,
    normalize_output,
    LoopDetector,
    SIMILARITY_THRESHOLD,
)


class TestDetectLoop:
    def test_empty_history_no_loop(self):
        assert detect_loop("some output", []) is False

    def test_empty_output_no_loop(self):
        assert detect_loop("", ["previous"]) is False

    def test_identical_output_is_loop(self):
        history = ["exact same output"]
        assert detect_loop("exact same output", history) is True

    def test_similar_output_is_loop(self):
        history = ["The quick brown fox jumps over the lazy dog"]
        # 95% similar (minor change)
        assert detect_loop("The quick brown fox jumps over the lazy cat", history) is True

    def test_different_output_not_loop(self):
        history = ["completely different content here"]
        assert detect_loop("something entirely new", history) is False

    def test_respects_history_size(self):
        history = ["old1", "old2", "old3", "old4", "old5", "old6"]
        # Only checks last 5
        assert detect_loop("old1", history) is False  # old1 not in last 5


class TestLoopDetector:
    def test_first_output_not_loop(self):
        detector = LoopDetector()
        assert detector.check("first output") is False

    def test_repeated_output_is_loop(self):
        detector = LoopDetector()
        detector.check("repeated output")
        assert detector.check("repeated output") is True

    def test_clear_resets_history(self):
        detector = LoopDetector()
        detector.check("output")
        detector.clear()
        assert detector.check("output") is False  # After clear, not a loop

    def test_hash_persistence(self):
        detector = LoopDetector()
        detector.check("output1")
        detector.check("output2")

        hashes = detector.get_hashes()
        assert len(hashes) == 2

        new_detector = LoopDetector()
        new_detector.restore_hashes(hashes)
        # Can detect based on restored hashes
        assert compute_hash(normalize_output("output1")) in new_detector.hash_history


class TestNormalizeOutput:
    def test_removes_timestamps(self):
        output = "Error at 2026-01-15T10:30:00 in module"
        normalized = normalize_output(output)
        assert "2026-01-15" not in normalized

    def test_removes_uuids(self):
        output = "Task 550e8400-e29b-41d4-a716-446655440000 failed"
        normalized = normalize_output(output)
        assert "550e8400" not in normalized

    def test_normalizes_whitespace(self):
        output = "multiple   spaces\n\nand\nnewlines"
        normalized = normalize_output(output)
        assert "  " not in normalized
        assert "\n" not in normalized
```

**Step 15.4: Run tests**

```bash
pytest tests/bmad_core/test_loop_detection.py -v
```

Expected: All tests pass

**Step 15.5: Commit**

```bash
git add _bmad/core/lib/loop_detection.py tests/bmad_core/test_loop_detection.py
git commit -m "feat(bmad): add loop detection module (Ralph Orchestrator pattern)"
```

---

## Task 16: Add Safety Guards Module

**Files:**
- Create: `_bmad/core/lib/safety_guards.py`

**Step 16.1: Write safety guards module**

Create file with this content:

```python
"""Safety guards (circuit breakers) for BMAD review loop.

Based on Ralph Orchestrator's safety patterns.
Provides multiple levels of circuit breakers to prevent runaway loops.
"""

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass
class ReviewLoopLimits:
    """Configurable limits for review loop safety guards."""

    max_review_rounds: int = 3
    max_fix_iterations: int = 3
    max_consecutive_failures: int = 5
    max_runtime_seconds: int = 1800  # 30 minutes
    max_total_issues: int = 50       # Sanity check


@dataclass
class ReviewLoopState:
    """Current state of review loop for safety checking."""

    current_round: int = 1
    current_fix_iteration: int = 0
    consecutive_failures: int = 0
    total_failures: int = 0
    total_issues: int = 0
    started_at: float = field(default_factory=time.time)

    def increment_round(self):
        self.current_round += 1
        self.current_fix_iteration = 0  # Reset fix iterations on new round

    def increment_fix_iteration(self):
        self.current_fix_iteration += 1

    def record_failure(self):
        self.consecutive_failures += 1
        self.total_failures += 1

    def record_success(self):
        self.consecutive_failures = 0  # Reset on success

    def elapsed_seconds(self) -> float:
        return time.time() - self.started_at


class SafetyGuard:
    """Circuit breaker checking for review loop.

    Implements multiple safety limits to prevent:
    - Infinite loops (max rounds)
    - Stuck fix iterations (max fix iterations)
    - Repeated failures (max consecutive failures)
    - Runaway execution (max runtime)
    - Explosion of issues (max total issues)
    """

    def __init__(self, limits: Optional[ReviewLoopLimits] = None):
        self.limits = limits or ReviewLoopLimits()

    def should_halt(self, state: ReviewLoopState) -> Tuple[bool, str]:
        """Check if review loop should halt.

        Returns:
            Tuple of (should_halt, reason)
        """
        # Check review rounds
        if state.current_round > self.limits.max_review_rounds:
            return True, f"Max review rounds ({self.limits.max_review_rounds}) exceeded"

        # Check fix iterations within current round
        if state.current_fix_iteration > self.limits.max_fix_iterations:
            return True, f"Max fix iterations ({self.limits.max_fix_iterations}) exceeded in round {state.current_round}"

        # Check consecutive failures
        if state.consecutive_failures >= self.limits.max_consecutive_failures:
            return True, f"Too many consecutive failures ({state.consecutive_failures})"

        # Check runtime
        elapsed = state.elapsed_seconds()
        if elapsed >= self.limits.max_runtime_seconds:
            minutes = int(elapsed / 60)
            return True, f"Max runtime ({minutes} minutes) exceeded"

        # Check total issues (sanity)
        if state.total_issues > self.limits.max_total_issues:
            return True, f"Too many total issues ({state.total_issues}) - possible issue explosion"

        return False, ""

    def check_and_raise(self, state: ReviewLoopState):
        """Check safety and raise exception if should halt."""
        should_halt, reason = self.should_halt(state)
        if should_halt:
            raise SafetyLimitExceeded(reason)

    def remaining_budget(self, state: ReviewLoopState) -> dict:
        """Get remaining budget for each limit."""
        elapsed = state.elapsed_seconds()
        return {
            "rounds_remaining": max(0, self.limits.max_review_rounds - state.current_round + 1),
            "fix_iterations_remaining": max(0, self.limits.max_fix_iterations - state.current_fix_iteration),
            "failures_remaining": max(0, self.limits.max_consecutive_failures - state.consecutive_failures),
            "seconds_remaining": max(0, self.limits.max_runtime_seconds - elapsed),
            "issues_remaining": max(0, self.limits.max_total_issues - state.total_issues),
        }


class SafetyLimitExceeded(Exception):
    """Raised when a safety limit is exceeded."""
    pass


def calculate_backoff(failure_count: int, max_delay: int = 60) -> int:
    """Calculate exponential backoff delay with cap.

    Based on Ralph Orchestrator pattern: min(2^failures, 60)

    Args:
        failure_count: Number of consecutive failures
        max_delay: Maximum delay in seconds (default 60)

    Returns:
        Delay in seconds
    """
    return min(2 ** failure_count, max_delay)
```

**Step 16.2: Write test file**

Create `tests/bmad_core/test_safety_guards.py`:

```python
"""Tests for BMAD safety guards module."""

import pytest
import time
from _bmad.core.lib.safety_guards import (
    ReviewLoopLimits,
    ReviewLoopState,
    SafetyGuard,
    SafetyLimitExceeded,
    calculate_backoff,
)


class TestSafetyGuard:
    def test_fresh_state_ok(self):
        guard = SafetyGuard()
        state = ReviewLoopState()
        should_halt, reason = guard.should_halt(state)
        assert should_halt is False
        assert reason == ""

    def test_max_rounds_exceeded(self):
        guard = SafetyGuard(ReviewLoopLimits(max_review_rounds=3))
        state = ReviewLoopState(current_round=4)
        should_halt, reason = guard.should_halt(state)
        assert should_halt is True
        assert "review rounds" in reason.lower()

    def test_max_fix_iterations_exceeded(self):
        guard = SafetyGuard(ReviewLoopLimits(max_fix_iterations=3))
        state = ReviewLoopState(current_fix_iteration=4)
        should_halt, reason = guard.should_halt(state)
        assert should_halt is True
        assert "fix iterations" in reason.lower()

    def test_consecutive_failures_exceeded(self):
        guard = SafetyGuard(ReviewLoopLimits(max_consecutive_failures=5))
        state = ReviewLoopState(consecutive_failures=5)
        should_halt, reason = guard.should_halt(state)
        assert should_halt is True
        assert "failures" in reason.lower()

    def test_max_runtime_exceeded(self):
        guard = SafetyGuard(ReviewLoopLimits(max_runtime_seconds=1))
        state = ReviewLoopState(started_at=time.time() - 2)
        should_halt, reason = guard.should_halt(state)
        assert should_halt is True
        assert "runtime" in reason.lower()

    def test_check_and_raise(self):
        guard = SafetyGuard(ReviewLoopLimits(max_review_rounds=1))
        state = ReviewLoopState(current_round=2)
        with pytest.raises(SafetyLimitExceeded):
            guard.check_and_raise(state)

    def test_remaining_budget(self):
        guard = SafetyGuard(ReviewLoopLimits(max_review_rounds=3))
        state = ReviewLoopState(current_round=1)
        budget = guard.remaining_budget(state)
        assert budget["rounds_remaining"] == 3


class TestReviewLoopState:
    def test_increment_round(self):
        state = ReviewLoopState(current_round=1, current_fix_iteration=2)
        state.increment_round()
        assert state.current_round == 2
        assert state.current_fix_iteration == 0  # Reset

    def test_record_failure(self):
        state = ReviewLoopState(consecutive_failures=0, total_failures=0)
        state.record_failure()
        assert state.consecutive_failures == 1
        assert state.total_failures == 1

    def test_record_success_resets_consecutive(self):
        state = ReviewLoopState(consecutive_failures=3)
        state.record_success()
        assert state.consecutive_failures == 0


class TestCalculateBackoff:
    def test_first_failure(self):
        assert calculate_backoff(1) == 2

    def test_second_failure(self):
        assert calculate_backoff(2) == 4

    def test_exponential_growth(self):
        assert calculate_backoff(3) == 8
        assert calculate_backoff(4) == 16
        assert calculate_backoff(5) == 32

    def test_capped_at_max(self):
        assert calculate_backoff(10) == 60  # 2^10 = 1024, capped at 60
        assert calculate_backoff(100) == 60

    def test_custom_max(self):
        assert calculate_backoff(10, max_delay=30) == 30
```

**Step 16.3: Run tests**

```bash
pytest tests/bmad_core/test_safety_guards.py -v
```

Expected: All tests pass

**Step 16.4: Commit**

```bash
git add _bmad/core/lib/safety_guards.py tests/bmad_core/test_safety_guards.py
git commit -m "feat(bmad): add safety guards module (Ralph Orchestrator pattern)"
```

---

## Task 17: Add Context Manager Module

**Files:**
- Create: `_bmad/core/lib/context_manager.py`

**Step 17.1: Write context manager module**

Create file with this content:

```python
"""Four-layer context management for BMAD review loop.

Based on Ralph Orchestrator's ContextManager pattern.
Maintains bounded history for efficient context passing.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ReviewLoopContext:
    """Four-layer context management for review loop.

    Layers:
    1. stable_context: Original prompt, workflow info (never changes)
    2. dynamic_context: Recent review outputs (sliding window)
    3. error_history: Recent errors for debugging (sliding window)
    4. success_patterns: Successful fix patterns for reuse (sliding window)
    """

    stable_context: str = ""
    dynamic_context: List[str] = field(default_factory=list)
    error_history: List[str] = field(default_factory=list)
    success_patterns: List[str] = field(default_factory=list)

    # Bounds (from Ralph Orchestrator)
    MAX_DYNAMIC_ENTRIES: int = 5
    MAX_ERROR_ENTRIES: int = 5
    MAX_SUCCESS_ENTRIES: int = 3
    MAX_ENTRY_LENGTH: int = 500
    MAX_TOTAL_CONTEXT: int = 5000

    def set_stable_context(self, context: str):
        """Set the stable context (should only be called once at init)."""
        self.stable_context = context

    def add_review_output(self, output: str):
        """Add a review output to dynamic context."""
        truncated = self._truncate(output)
        self.dynamic_context.append(truncated)
        self._enforce_limit(self.dynamic_context, self.MAX_DYNAMIC_ENTRIES)

    def add_error(self, error: str):
        """Add an error to error history."""
        truncated = self._truncate(error)
        self.error_history.append(truncated)
        self._enforce_limit(self.error_history, self.MAX_ERROR_ENTRIES)

    def add_success_pattern(self, pattern: str):
        """Add a successful fix pattern."""
        truncated = self._truncate(pattern)
        self.success_patterns.append(truncated)
        self._enforce_limit(self.success_patterns, self.MAX_SUCCESS_ENTRIES)

    def get_full_context(self) -> str:
        """Get combined context for prompt injection.

        Returns context bounded by MAX_TOTAL_CONTEXT.
        """
        parts = []

        # Stable context first (always included)
        if self.stable_context:
            parts.append(f"## Original Context\n{self.stable_context}")

        # Recent review outputs
        if self.dynamic_context:
            recent = "\n---\n".join(self.dynamic_context[-3:])  # Last 3 only
            parts.append(f"## Recent Review Outputs\n{recent}")

        # Success patterns (helpful for fixes)
        if self.success_patterns:
            patterns = "\n- ".join(self.success_patterns)
            parts.append(f"## Successful Fix Patterns\n- {patterns}")

        # Recent errors (for debugging)
        if self.error_history:
            errors = "\n- ".join(self.error_history[-2:])  # Last 2 only
            parts.append(f"## Recent Errors\n- {errors}")

        full_context = "\n\n".join(parts)

        # Enforce total limit
        if len(full_context) > self.MAX_TOTAL_CONTEXT:
            full_context = full_context[:self.MAX_TOTAL_CONTEXT] + "\n...[truncated]"

        return full_context

    def clear_dynamic(self):
        """Clear dynamic context (but keep stable and patterns)."""
        self.dynamic_context.clear()
        self.error_history.clear()

    def clear_all(self):
        """Clear all context."""
        self.stable_context = ""
        self.dynamic_context.clear()
        self.error_history.clear()
        self.success_patterns.clear()

    def _truncate(self, text: str) -> str:
        """Truncate text to max entry length."""
        if len(text) <= self.MAX_ENTRY_LENGTH:
            return text
        return text[:self.MAX_ENTRY_LENGTH] + "..."

    def _enforce_limit(self, lst: List[str], max_size: int):
        """Remove oldest entries if over limit."""
        while len(lst) > max_size:
            lst.pop(0)

    def to_dict(self) -> dict:
        """Serialize context for state persistence."""
        return {
            "stable_context": self.stable_context,
            "dynamic_context": list(self.dynamic_context),
            "error_history": list(self.error_history),
            "success_patterns": list(self.success_patterns),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewLoopContext":
        """Restore context from state."""
        ctx = cls()
        ctx.stable_context = data.get("stable_context", "")
        ctx.dynamic_context = data.get("dynamic_context", [])
        ctx.error_history = data.get("error_history", [])
        ctx.success_patterns = data.get("success_patterns", [])
        return ctx
```

**Step 17.2: Write test file**

Create `tests/bmad_core/test_context_manager.py`:

```python
"""Tests for BMAD context manager module."""

import pytest
from _bmad.core.lib.context_manager import ReviewLoopContext


class TestReviewLoopContext:
    def test_initial_state(self):
        ctx = ReviewLoopContext()
        assert ctx.stable_context == ""
        assert ctx.dynamic_context == []
        assert ctx.error_history == []
        assert ctx.success_patterns == []

    def test_set_stable_context(self):
        ctx = ReviewLoopContext()
        ctx.set_stable_context("Original prompt")
        assert ctx.stable_context == "Original prompt"

    def test_add_review_output(self):
        ctx = ReviewLoopContext()
        ctx.add_review_output("Review 1")
        ctx.add_review_output("Review 2")
        assert len(ctx.dynamic_context) == 2

    def test_dynamic_context_limit(self):
        ctx = ReviewLoopContext()
        for i in range(10):
            ctx.add_review_output(f"Review {i}")
        assert len(ctx.dynamic_context) == ctx.MAX_DYNAMIC_ENTRIES

    def test_truncation(self):
        ctx = ReviewLoopContext()
        long_text = "x" * 1000
        ctx.add_review_output(long_text)
        assert len(ctx.dynamic_context[0]) <= ctx.MAX_ENTRY_LENGTH + 3  # +3 for ...

    def test_add_error(self):
        ctx = ReviewLoopContext()
        ctx.add_error("Error 1")
        assert len(ctx.error_history) == 1

    def test_add_success_pattern(self):
        ctx = ReviewLoopContext()
        ctx.add_success_pattern("Pattern 1")
        assert len(ctx.success_patterns) == 1

    def test_get_full_context(self):
        ctx = ReviewLoopContext()
        ctx.set_stable_context("Stable")
        ctx.add_review_output("Review")
        ctx.add_success_pattern("Pattern")
        ctx.add_error("Error")

        full = ctx.get_full_context()
        assert "Stable" in full
        assert "Review" in full
        assert "Pattern" in full
        assert "Error" in full

    def test_full_context_bounded(self):
        ctx = ReviewLoopContext()
        ctx.set_stable_context("x" * 10000)
        full = ctx.get_full_context()
        assert len(full) <= ctx.MAX_TOTAL_CONTEXT + 20  # Some buffer for truncation marker

    def test_clear_dynamic(self):
        ctx = ReviewLoopContext()
        ctx.set_stable_context("Stable")
        ctx.add_review_output("Review")
        ctx.add_error("Error")
        ctx.add_success_pattern("Pattern")

        ctx.clear_dynamic()

        assert ctx.stable_context == "Stable"  # Preserved
        assert ctx.success_patterns == ["Pattern"]  # Preserved
        assert ctx.dynamic_context == []  # Cleared
        assert ctx.error_history == []  # Cleared

    def test_serialization(self):
        ctx = ReviewLoopContext()
        ctx.set_stable_context("Stable")
        ctx.add_review_output("Review")

        data = ctx.to_dict()
        restored = ReviewLoopContext.from_dict(data)

        assert restored.stable_context == ctx.stable_context
        assert restored.dynamic_context == ctx.dynamic_context
```

**Step 17.3: Run tests**

```bash
pytest tests/bmad_core/test_context_manager.py -v
```

Expected: All tests pass

**Step 17.4: Commit**

```bash
git add _bmad/core/lib/context_manager.py tests/bmad_core/test_context_manager.py
git commit -m "feat(bmad): add context manager module (Ralph Orchestrator pattern)"
```

---

## Task 18: Add Metrics Tracking Module

**Files:**
- Create: `_bmad/core/lib/metrics.py`

**Step 18.1: Write metrics module**

Create file with this content:

```python
"""Metrics tracking for BMAD review loop.

Based on Ralph Orchestrator's telemetry patterns.
Tracks review loop performance for observability.
"""

import time
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from pathlib import Path


class TriggerReason(Enum):
    """Reasons for review loop iteration."""

    INITIAL = "initial"                    # First review round
    ISSUES_REMAIN = "issues_remain"        # Continuing due to remaining issues
    CONFIDENCE_LOW = "confidence_low"      # Confidence below threshold
    RECOVERY = "recovery"                  # Recovering from failure
    LOOP_DETECTED = "loop_detected"        # Breaking out of detected loop
    SAFETY_LIMIT = "safety_limit"          # Stopped by safety guard
    USER_STOP = "user_stop"                # User requested stop
    COMPLETE = "complete"                  # All issues resolved


@dataclass
class ReviewLoopMetrics:
    """Metrics for a single review loop execution."""

    # Counters
    review_rounds: int = 0
    fix_iterations: int = 0
    total_issues_found: int = 0
    total_issues_fixed: int = 0
    total_issues_blocked: int = 0
    subagent_invocations: int = 0

    # Error tracking
    failures: int = 0
    recoveries: int = 0
    loops_detected: int = 0

    # Timing
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    total_backoff_seconds: float = 0.0

    # Outcome
    final_confidence: float = 0.0
    exit_reason: str = ""

    def record_review_round(self):
        self.review_rounds += 1

    def record_fix_iteration(self):
        self.fix_iterations += 1

    def record_issues_found(self, count: int):
        self.total_issues_found += count

    def record_issue_fixed(self):
        self.total_issues_fixed += 1

    def record_issue_blocked(self):
        self.total_issues_blocked += 1

    def record_subagent_call(self):
        self.subagent_invocations += 1

    def record_failure(self):
        self.failures += 1

    def record_recovery(self):
        self.recoveries += 1

    def record_loop_detected(self):
        self.loops_detected += 1

    def record_backoff(self, seconds: float):
        self.total_backoff_seconds += seconds

    def complete(self, confidence: float, reason: str):
        self.ended_at = time.time()
        self.final_confidence = confidence
        self.exit_reason = reason

    def elapsed_seconds(self) -> float:
        end = self.ended_at or time.time()
        return end - self.started_at

    def elapsed_minutes(self) -> float:
        return self.elapsed_seconds() / 60

    def success_rate(self) -> float:
        total = self.total_issues_found
        if total == 0:
            return 1.0
        return self.total_issues_fixed / total

    def to_dict(self) -> dict:
        data = asdict(self)
        data["elapsed_seconds"] = self.elapsed_seconds()
        data["elapsed_minutes"] = self.elapsed_minutes()
        data["success_rate"] = self.success_rate()
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def save(self, output_dir: Path, filename: Optional[str] = None):
        """Save metrics to JSON file."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = int(self.started_at)
            filename = f"review-metrics-{timestamp}.json"

        filepath = output_dir / filename
        filepath.write_text(self.to_json())
        return filepath

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            "═" * 50,
            "REVIEW LOOP METRICS SUMMARY",
            "═" * 50,
            f"Duration: {self.elapsed_minutes():.1f} minutes",
            f"Review rounds: {self.review_rounds}",
            f"Fix iterations: {self.fix_iterations}",
            f"Subagent calls: {self.subagent_invocations}",
            "",
            f"Issues found: {self.total_issues_found}",
            f"Issues fixed: {self.total_issues_fixed}",
            f"Issues blocked: {self.total_issues_blocked}",
            f"Success rate: {self.success_rate():.1%}",
            "",
            f"Failures: {self.failures}",
            f"Recoveries: {self.recoveries}",
            f"Loops detected: {self.loops_detected}",
            f"Total backoff: {self.total_backoff_seconds:.1f}s",
            "",
            f"Final confidence: {self.final_confidence:.1f}%",
            f"Exit reason: {self.exit_reason}",
            "═" * 50,
        ]
        return "\n".join(lines)
```

**Step 18.2: Write test file**

Create `tests/bmad_core/test_metrics.py`:

```python
"""Tests for BMAD metrics module."""

import pytest
import json
import tempfile
from pathlib import Path
from _bmad.core.lib.metrics import (
    ReviewLoopMetrics,
    TriggerReason,
)


class TestReviewLoopMetrics:
    def test_initial_state(self):
        metrics = ReviewLoopMetrics()
        assert metrics.review_rounds == 0
        assert metrics.total_issues_found == 0
        assert metrics.started_at > 0

    def test_record_review_round(self):
        metrics = ReviewLoopMetrics()
        metrics.record_review_round()
        assert metrics.review_rounds == 1

    def test_record_issues(self):
        metrics = ReviewLoopMetrics()
        metrics.record_issues_found(5)
        metrics.record_issue_fixed()
        metrics.record_issue_fixed()
        metrics.record_issue_blocked()

        assert metrics.total_issues_found == 5
        assert metrics.total_issues_fixed == 2
        assert metrics.total_issues_blocked == 1

    def test_success_rate(self):
        metrics = ReviewLoopMetrics()
        metrics.record_issues_found(10)
        for _ in range(8):
            metrics.record_issue_fixed()

        assert metrics.success_rate() == 0.8

    def test_success_rate_no_issues(self):
        metrics = ReviewLoopMetrics()
        assert metrics.success_rate() == 1.0  # No issues = 100% success

    def test_complete(self):
        metrics = ReviewLoopMetrics()
        metrics.complete(confidence=95.0, reason="ALL_ISSUES_RESOLVED")

        assert metrics.ended_at is not None
        assert metrics.final_confidence == 95.0
        assert metrics.exit_reason == "ALL_ISSUES_RESOLVED"

    def test_to_json(self):
        metrics = ReviewLoopMetrics()
        metrics.record_review_round()
        json_str = metrics.to_json()

        parsed = json.loads(json_str)
        assert parsed["review_rounds"] == 1

    def test_save_to_file(self):
        metrics = ReviewLoopMetrics()
        metrics.record_review_round()

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = metrics.save(Path(tmpdir))
            assert filepath.exists()

            content = json.loads(filepath.read_text())
            assert content["review_rounds"] == 1

    def test_summary(self):
        metrics = ReviewLoopMetrics()
        metrics.record_review_round()
        metrics.record_issues_found(5)
        metrics.record_issue_fixed()
        metrics.complete(90.0, "COMPLETE")

        summary = metrics.summary()
        assert "Review rounds: 1" in summary
        assert "Issues found: 5" in summary
        assert "90.0%" in summary


class TestTriggerReason:
    def test_enum_values(self):
        assert TriggerReason.INITIAL.value == "initial"
        assert TriggerReason.COMPLETE.value == "complete"
```

**Step 18.3: Run tests**

```bash
pytest tests/bmad_core/test_metrics.py -v
```

Expected: All tests pass

**Step 18.4: Commit**

```bash
git add _bmad/core/lib/metrics.py tests/bmad_core/test_metrics.py
git commit -m "feat(bmad): add metrics tracking module (Ralph Orchestrator pattern)"
```

---

## Task 19: Create lib Package Init

**Files:**
- Create: `_bmad/core/lib/__init__.py`

**Step 19.1: Write init file**

Create file with this content:

```python
"""BMAD Core Library - Supporting modules for workflow automation.

This package contains modules based on patterns from:
- Ralph Wiggum (Claude Code plugin by Anthropic)
- Ralph Orchestrator (Production Python framework by mikeyobrien)

Modules:
- loop_detection: Fuzzy matching to detect infinite loops
- safety_guards: Circuit breakers to prevent runaway execution
- context_manager: Four-layer context management
- metrics: Telemetry tracking for observability
"""

from _bmad.core.lib.loop_detection import (
    detect_loop,
    LoopDetector,
    SIMILARITY_THRESHOLD,
)
from _bmad.core.lib.safety_guards import (
    SafetyGuard,
    ReviewLoopLimits,
    ReviewLoopState,
    SafetyLimitExceeded,
    calculate_backoff,
)
from _bmad.core.lib.context_manager import ReviewLoopContext
from _bmad.core.lib.metrics import ReviewLoopMetrics, TriggerReason

__all__ = [
    # Loop detection
    "detect_loop",
    "LoopDetector",
    "SIMILARITY_THRESHOLD",
    # Safety guards
    "SafetyGuard",
    "ReviewLoopLimits",
    "ReviewLoopState",
    "SafetyLimitExceeded",
    "calculate_backoff",
    # Context
    "ReviewLoopContext",
    # Metrics
    "ReviewLoopMetrics",
    "TriggerReason",
]
```

**Step 19.2: Create tests directory init**

Create `tests/bmad_core/__init__.py` (empty file):

```python
"""Tests for BMAD core library modules."""
```

**Step 19.3: Verify imports work**

```bash
python -c "from _bmad.core.lib import SafetyGuard, LoopDetector, ReviewLoopContext, ReviewLoopMetrics; print('OK')"
```

Expected: `OK`

**Step 19.4: Commit**

```bash
git add _bmad/core/lib/__init__.py tests/bmad_core/__init__.py
git commit -m "feat(bmad): add lib package init with all modules"
```

---

## Task 20: Update Review Loop XML with All Patterns

**Files:**
- Modify: `_bmad/core/tasks/review-loop.xml` (created in Task 6)

**Step 20.1: Read current review-loop.xml**

Read the file created in Task 6.

**Step 20.2: Add Ralph patterns integration**

Update the review-loop.xml to integrate all patterns:

1. **State File Management:**
   - Create state file at start using template from Task 14
   - Update state file after each operation
   - Delete state file on completion

2. **Loop Detection:**
   - Track output hashes in state file
   - Check for loops after each review round
   - If loop detected: escalate to user

3. **Safety Guards:**
   - Check all limits before each iteration
   - Include in state file for stop hook access
   - Respect all circuit breakers

4. **Context Management:**
   - Initialize context manager at start
   - Add review outputs to dynamic context
   - Track errors and success patterns
   - Pass context to subagents

5. **Metrics Tracking:**
   - Initialize metrics at start
   - Record all events
   - Save metrics on completion

6. **Completion Promises:**
   - Output `<review-complete>ALL_ISSUES_RESOLVED</review-complete>` when done
   - Output `<review-blocked>REASON</review-blocked>` if blocked
   - Output `<review-timeout>REASON</review-timeout>` if safety limit hit

**Step 20.3: Verify integration**

Run: `type _bmad\core\tasks\review-loop.xml | findstr "review-complete"`
Expected: Shows completion promise tag

**Step 20.4: Commit**

```bash
git add _bmad/core/tasks/review-loop.xml
git commit -m "feat(bmad): integrate all Ralph patterns into review loop XML"
```

---

## Summary

This implementation adds 20 tasks total:

### Core Review Loop (Tasks 1-11)
1. **Issue Tracker Template** - Standardized format for tracking issues and fixes
2. **Adversarial Reviewer Subagent** - Parallel review with MCP integration
3. **Party Facilitator Subagent** - Multi-agent discussion with MCP integration
4. **Elicitation Expert Subagent** - Deep questioning with MCP integration
5. **Issue Fixer Subagent** - Parallel fixes with MCP integration
6. **Review Loop Engine** - XML task orchestrating confidence-based review
7. **workflow.xml Integration** - Step 2c invokes review loop
8. **BMM Config** - Review loop configuration
9. **automation-runtime.md** - Documentation of review loop behavior
10. **Reviews Output Directory** - Storage for issue tracking files
11. **Integration Test** - Verify all components work together

### Ralph Patterns Integration (Tasks 12-20)
12. **Stop Hook Script** - Prevents premature exit until issues resolved
13. **Hooks Configuration** - JSON config for Claude Code hooks
14. **State File Template** - YAML template for loop state persistence
15. **Loop Detection Module** - Fuzzy matching to detect infinite loops
16. **Safety Guards Module** - Circuit breakers for all limits
17. **Context Manager Module** - Four-layer context tracking
18. **Metrics Module** - Telemetry for observability
19. **Lib Package Init** - Export all modules
20. **Review Loop XML Update** - Integrate all patterns

### Key Patterns Applied
- **Stop Hook Interception** (Ralph Wiggum) - Prevents exit until complete
- **Completion Promises** (Both) - Clear XML tags for signaling
- **State File Persistence** (Both) - YAML frontmatter format
- **Loop Detection** (Ralph Orchestrator) - 90% fuzzy threshold
- **Safety Guards** (Ralph Orchestrator) - Multiple circuit breakers
- **Exponential Backoff** (Ralph Orchestrator) - min(2^failures, 60)
- **Four-Layer Context** (Ralph Orchestrator) - Bounded history
- **Metrics/Telemetry** (Ralph Orchestrator) - Observability

The main agent becomes a pure orchestrator - all actual review and fix work is done by parallel subagents with explicit MCP tool usage. The stop hook ensures the loop continues until all issues are truly resolved.
