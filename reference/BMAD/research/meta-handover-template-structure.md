# Handover Template Structure

Agents: Read this structure when creating handovers.
Replace ALL [placeholders] with actual values.

---

# [Task Name] - Session Handover [N]
**Session Date**: [YYYY-MM-DD]
**Handover Number**: [N]
**Previous Handover**: [relative/path/to/previous.md OR "None - First session"]

---

## 🔄 CONTINUATION PROMPT

**To continue this work in a new session, type:** `continue` or read this handover

**Current Status**: [In Progress | Complete]
**Next Action**: [First To Do task from execution plan]

---

## 📋 EXECUTION PLAN

| Step | Task Description | Status | Checkpoint | Notes |
|------|-----------------|--------|------------|-------|
| [N] | [Task description] | [Done|In Progress|To Do] | [✓|⏳|-] | [Notes] |

**Status Legend**: Done = ✓ | In Progress = ⏳ | To Do = -

---

## 📊 WORK COMPLETED THIS SESSION

### Step [N]: [Task Name]
**Status**: [Done ✓ | In Progress ⏳]
**Checkpoint**: Session [N], Step [N]

**What was done**:
- [Action 1]
- [Action 2]

**Key findings**:
- [Finding 1]

**Artifacts created**:
- `[file/path]` - [Purpose]

[Repeat for each completed/in-progress step]

---

## 🎯 CONTINUATION INSTRUCTIONS

**When this session resumes:**

1. **Read this handover fully**
2. **Resume at**: Step [N] - [Task name]
3. **Load context**: [Files to read]
4. **Expected workflow**:
   - [Step 1]
   - [Step 2]

---

## 📁 CRITICAL FILE REFERENCES

| File Path | Purpose | Created/Modified | Step |
|-----------|---------|------------------|------|
| `[path]` | [Purpose] | [Created|Modified] | Step [N] |

---

## 🔍 KEY CONTEXT & DECISIONS

**Important decisions made**:
- **[Decision]**: [Rationale and implications]

**Patterns identified**:
- [Pattern or approach]

**Known blockers/issues**:
- [ ] **[Blocker]** - [Impact] - [Potential solution]

**Context for next session**:
- [Important info to remember]

---

## 🧠 SUBAGENTS UTILIZED

| Subagent Type | Purpose | Status | Notes |
|---------------|---------|--------|-------|
| [subagent-name] | [Purpose] | [Complete ✓] | [Findings] |

OR "None - direct implementation"

---

## 📈 PROGRESS METRICS

- **Total steps**: [N]
- **Completed**: [N] steps (✓)
- **In progress**: [N] steps (⏳)
- **Remaining**: [N] steps (-)
- **Overall completion**: [N]%

**Velocity**:
- Steps completed this session: [N]
- Average time per step: [Estimate or "Not tracked"]

---

## 💾 SESSION METADATA

- **Token usage**: [Approximate count from system messages]
- **Files read**: [N]
- **Files written**: [N]
- **Files modified**: [N]
- **Bash commands executed**: [N]
- **Subagents spawned**: [N]
- **Reason for handover**: [User requested | Token limit | Natural break | End of session]

---

## 📝 CONTINUATION MECHANISM

**When user types "continue" in next session:**

1. Agent searches Handovers/ for most recent handover
2. Reads entire document
3. Finds first "To Do" in execution plan
4. Loads files from Critical File References
5. Reviews Key Context & Decisions
6. Announces: "Continuing from Session [N], resuming at Step [M]: [Task]"
7. Begins work, updates status as progresses

---

**Template version**: 1.0
**Last updated**: 2026-01-20