# META HANDOVER PROMPT (Token-Optimized)

**Use when**: Need to create session handover
**Token cost**: ~800 tokens
**Output**: Complete handover document

---

## THE PROMPT (Copy everything below)

```text
⚠️ TOKEN WARNING: I cannot monitor token usage. Check system messages.
Request handovers at ~150K of 200K context to preserve work.

═══════════════════════════════════════════════════════════════

HANDOVER CREATION PROTOCOL

SETUP:
1. mkdir -p Handovers (if needed)
2. Check Handovers/templates/ for handover-template.md
3. Find highest session-N for this task → set N+1

ANALYZE SESSION:
TodoWrite exists?
  YES → Extract tasks with status
  NO → Reconstruct from:
    - Tool calls (Read/Write/Edit = files touched)
    - Conversation (decisions, requests, responses)
    - Bash commands (operations performed)

FILES: All Write/Edit/NotebookEdit targets
DECISIONS: Explicit choices made in conversation
SUBAGENTS: Task tool invocations
BLOCKERS: Issues/errors mentioned
PROGRESS: Count Done/InProgress/ToDo

GENERATE DOCUMENT:
Read structure: Handovers/templates/handover-template.md
Follow that structure exactly
Replace ALL [placeholders] with concrete values

CONTENT PRIORITY (if tokens tight):
CRITICAL (always):
  - Execution plan table
  - Next action (first To Do item)
  - Files touched with paths

STANDARD (include if possible):
  - Work completed details
  - Key decisions with rationale
  - Blockers with impact
  - Progress metrics

OPTIONAL (if tokens abundant):
  - Subagent details
  - Velocity metrics
  - Detailed findings per step

SAVE:
File: Handovers/[task]-session-[N]-[YYYY-MM-DD-HHMMSS].md
Use: lowercase-with-hyphens
Include: Full timestamp (avoid conflicts)

CONFIRM:
✓ File path
✓ Session number
✓ Progress % (Done/Total steps)
✓ Next action
✓ Recommend .gitignore entry (first time)

═══════════════════════════════════════════════════════════════

REQUIREMENTS:

MUST DO:
- Check/create Handovers/ directory
- Find highest session-N or start at 1
- Reconstruct plan if no TodoWrite
- Document EVERY file touched
- Capture ALL decisions
- Use concrete values (no placeholders)
- Full timestamp in filename
- Link previous handover if N>1

MUST NOT:
- Leave [placeholders] in output
- Guess session numbers
- Omit blockers/issues
- Use date-only filenames
- Skip subagent tracking

═══════════════════════════════════════════════════════════════
```

---

## USAGE

**Copy-paste the prompt above** when you need to create a handover.

**When to use**:
- End of session
- Approaching token limit (~150K)
- Before context switch
- After major milestones

**What happens**:
1. Checks Handovers/ exists (creates if not)
2. Finds session number
3. Analyzes session state
4. Reads template structure
5. Generates handover
6. Saves with timestamp
7. Recommends .gitignore

**Requirements**:
- Template file must exist: `Handovers/templates/handover-template.md`
- If missing, create it using File 2 outline

**Documentation**:
See "Handover Documentation.md" for examples, troubleshooting, best practices