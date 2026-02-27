# Meta Handover Documentation

Complete guide to using the token-optimized handover system.

---

## Overview

**What is this?**
- Token-efficient system for creating session handovers
- 3-file architecture: Prompt (~800 tokens) + Template + Documentation
- Designed for use when context is already constrained (150K+ tokens)

**Files**:
- `META-HANDOVER-PROMPT.md` - The prompt you paste each time
- `handover-template.md` - Structure agents read when generating
- `Handover Documentation.md` - This file (read once for understanding)

---

## Quick Start

### First Time Setup

1. **Copy template to your project**:
   ```bash
   mkdir -p Handovers/templates
   cp handover-template.md Handovers/templates/
   ```

2. **Add to .gitignore**:
   ```bash
   echo "Handovers/" >> .gitignore
   ```

3. **You're ready!** No other setup needed.

### Creating a Handover

1. **When to create**:
   - End of session
   - Token usage approaching 150K
   - Before context switching
   - After major milestones

2. **Copy-paste the prompt**:
   - Open `META-HANDOVER-PROMPT.md`
   - Copy the section marked "Copy everything below"
   - Paste into Claude Code

3. **Agent creates handover**:
   - Analyzes your session automatically
   - Generates complete handover
   - Saves to `Handovers/[task]-session-[N]-[timestamp].md`

### Continuing from Handover

In a new session:

```
continue
```

OR be more explicit:

```
Read the latest handover from Handovers/ and resume the work
```

---

## How It Works

### Session Analysis

Agent automatically:
- Checks if TodoWrite was used → extracts tasks
- No TodoWrite? → Reconstructs from conversation & tool calls
- Tracks all files touched (Write/Edit/NotebookEdit)
- Identifies decisions from conversation
- Notes subagents spawned (Task tool calls)
- Captures blockers/issues mentioned

### Template Usage

Agent reads `Handovers/templates/handover-template.md` for structure, then:
1. Replaces all [placeholders] with actual values
2. Fills in execution plan from TodoWrite or reconstruction
3. Documents completed work with findings
4. Lists critical files with paths
5. Captures decisions and context
6. Calculates progress metrics

### Content Priority

When tokens are tight, agent includes:

**CRITICAL** (always):
- Execution plan table
- Next action
- Files touched

**STANDARD** (if possible):
- Work completed details
- Key decisions
- Blockers
- Progress metrics

**OPTIONAL** (if tokens abundant):
- Subagent details
- Velocity metrics
- Detailed findings

---

## Examples

### Example 1: End of Session with TodoWrite

**Context**: Working on auth refactor, used TodoWrite, 7 tasks tracked.

**You paste prompt, agent responds**:

```
Analyzing session state...

✓ Handovers/ directory exists
Found previous: auth-refactor-session-1-2026-01-18-093045.md
Session number: 2

TodoWrite found: 7 tasks (4 done, 1 active, 2 pending)

Files touched:
- 8 created (JWT utils, middleware, tests)
- 3 modified (routes, config, types)

Decisions: 2 (JWT strategy, token storage)
Subagents: 1 (Explore agent)

✓ Saved: Handovers/auth-refactor-session-2-2026-01-20-143022.md

SUMMARY:
- Session 2 (previous: session-1-2026-01-18-093045.md)
- 7 steps: 4 done, 1 active, 2 pending
- Progress: 57%
- Next: Implement token refresh endpoint

⚠️  RECOMMENDATION: Add Handovers/ to .gitignore
```

---

### Example 2: No TodoWrite - Reconstruction

**Context**: Exploratory session, no TodoWrite used.

**You paste prompt, agent responds**:

```
Analyzing session state...

✗ Handovers/ not found → Creating
Session number: 1

TodoWrite not found → Reconstructing from conversation

Analyzing tool calls:
- Glob: Found 12 auth files
- Read: 8 files (middleware, routes, config...)
- Decision: Recommended JWT over sessions
- No writes yet (exploration phase)

Retroactive plan:
  1. Survey auth files (DONE)
  2. Analyze current flow (DONE)
  3. Research JWT (DONE)
  4. Recommend approach (DONE)
  5. Design new architecture (TO DO)
  6. Implement middleware (TO DO)

✓ Saved: Handovers/auth-flow-exploration-session-1-2026-01-20-154530.md

SUMMARY:
- Session 1 (first session)
- 6 steps: 4 done, 2 pending
- Progress: 67%
- Next: Design new auth architecture

⚠️  Add to .gitignore:
    Handovers/
```

---

### Example 3: Continuing Work

**New session, you type**: `continue`

**Agent responds**:

```
Reading: Handovers/auth-refactor-session-2-2026-01-20-143022.md

RESUMING:
- Previous: Session 2 (2026-01-20)
- Continuing as: Session 3
- Progress: 4 of 7 steps (57%)
- Next: Step 5 - Implement token refresh endpoint

Loading context:
- src/auth/jwt.ts (JWT utilities)
- src/auth/middleware.ts (auth middleware)
- src/auth/routes.ts (auth routes)

Key context:
- JWT strategy: 15-min access, 7-day refresh
- Storage: httpOnly cookies
- Blocker: Refresh rotation needs security review

Starting Step 5...
```

---

## Version Control Best Practices

### Why Keep Handovers Local

**DON'T commit handovers to git**:
❌ Creates merge conflicts
❌ Personal notes not relevant to team
❌ Adds noise to git history
❌ Timestamps will always conflict

**Keep local instead**:
✅ No merge conflicts ever
✅ Private workspace
✅ Clean git history

### Setup .gitignore

**First time**:
```bash
echo "Handovers/" >> .gitignore
```

**Verify**:
```bash
cat .gitignore | grep Handovers
```

**Already committed? Cleanup**:
```bash
git rm -r --cached Handovers/
echo "Handovers/" >> .gitignore
git commit -m "Remove Handovers/ from version control"
```

### Timestamped Filenames

Format: `[task]-session-[N]-YYYY-MM-DD-HHMMSS.md`

**Why timestamps matter**:

Even if accidentally committed:
```
Handovers/auth-session-1-2026-01-20-143022.md  ← Your machine
Handovers/auth-session-1-2026-01-20-143155.md  ← Teammate's machine
```

Different timestamps = Different files = No conflict

**Without timestamps**:
```
Handovers/auth-session-1-2026-01-20.md  ← Both machines
```

Same filename = Conflict

### Backup Strategies

**Option 1: Private repo**
```bash
cd Handovers/
git init
git remote add origin <your-private-repo>
git add .
git commit -m "Backup handovers"
git push
```

**Option 2: Cloud storage**
- Copy to Dropbox/Google Drive
- Symlink back to project

**Option 3: Periodic archive**
```bash
tar -czf handovers-backup-$(date +%Y%m%d).tar.gz Handovers/
```

---

## Troubleshooting

### Issue: Template file not found

**Error**: Agent says "Cannot find handover-template.md"

**Solution**:
```bash
cp handover-template.md Handovers/templates/
```

### Issue: Session numbering wrong

**Problem**: Multiple unrelated handovers confuse numbering

**Solution**: Use descriptive task names
```
Good: feature-auth-jwt-session-1-...
Bad: session-1-...
```

### Issue: "continue" doesn't work

**Problem**: Agent doesn't understand "continue"

**Solution**: Be explicit
```
Read the latest handover from Handovers/ and resume work
```

### Issue: Reconstruction inaccurate

**Problem**: Agent misinterpreted conversation

**Solution**:
- Use TodoWrite in future for accuracy
- Manually correct execution plan in handover
- Add note in "Key Context" explaining

---

## Architecture Design

### Why 3 Files?

**Prompt** (~800 tokens):
- Compact instructions
- Pasted every time
- Must be token-efficient

**Template** (~400 tokens):
- Structure definition
- Read by agents
- Changed infrequently

**Documentation** (~2000 tokens):
- Examples and explanations
- Read by humans once
- Can be verbose

### Token Efficiency

**Old approach** (META-HANDOVER-PROMPT.md):
- Single file: ~4000 tokens
- Includes template, examples, docs
- Pasted every time → wasteful

**New approach**:
- Prompt: ~800 tokens (pasted)
- Template: read once per session
- Docs: read once ever
- **Savings: 80% reduction in pasted tokens**

### Why Not Tiered Versions?

**Initial idea**: Emergency/Standard/Comprehensive

**Flaw exposed**: If emergency works, why others?

**Paradox**:
- Emergency sufficient → Only version needed
- Emergency insufficient → Shouldn't exist
- No middle ground

**Result**: ONE optimized prompt, not 3 tiers

---

## Comparison to Other Prompts

### vs MINIMAL-HANDOVER-PROMPT

**MINIMAL**: Session initialization prompt
- Used at START of session
- Sets up continuous handover behavior
- Agent manages handovers automatically

**META**: One-shot handover creation
- Used ANY time during session
- Creates single handover on demand
- User must explicitly request

### vs STANDALONE-BMAD-HANDOVER-PROMPT

**STANDALONE**: Comprehensive session protocol
- Detailed tracking requirements
- Complex checkpoint system
- ~4000 tokens

**META**: Token-optimized version
- Same handover output
- 80% smaller prompt
- Prioritizes critical content

---

## Token Budget Management

### When to Create Handover

Watch system messages for token usage:

```
Token usage: 150000/200000  ← Time to create handover!
```

**Safe zones**:
- < 100K: No urgency
- 100-140K: Consider handover at milestone
- 140-160K: Create handover soon
- 160K+: Create handover NOW

### Why 150K Threshold?

200K total context, need:
- ~1K for prompt
- ~1K for agent analysis
- ~2K for handover generation
- ~1K for confirmation
- **Total: ~5K needed**

At 150K: 50K remaining (10x safety margin)
At 180K: 20K remaining (4x margin, risky)
At 190K: 10K remaining (2x margin, dangerous)

---

## Advanced Usage

### Custom Task Names

Be descriptive:
```
Good:
- feature-auth-jwt-implementation-session-1-...
- bugfix-memory-leak-session-1-...
- refactor-database-layer-session-1-...

Bad:
- work-session-1-...
- session-1-...
- handover-session-1-...
```

### Multiple Parallel Tasks

Different task names track separately:
```
Handovers/
├── feature-auth-session-1-...
├── feature-auth-session-2-...
├── bugfix-leak-session-1-...
└── bugfix-leak-session-2-...
```

Agent finds highest N per task name.

### Sharing with Team

**Don't commit**, but can share:

1. Email specific .md file
2. Paste content into shared doc
3. Use team handover directory:
   - Personal: `/Handovers/` (gitignored)
   - Shared: `/docs/team-handovers/` (committed)

---

**Created**: 2026-01-20
**Version**: 1.0 (Token-Optimized)
**Last Updated**: 2026-01-20