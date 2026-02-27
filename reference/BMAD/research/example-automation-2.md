# BMAD Agent Teams — Quick Guide

**What is it?** A way to run multiple BMAD agents in parallel using Claude Code's Agent Teams feature. Instead of running one agent at a time, you spawn a team — a lead agent coordinates workers who each run BMAD workflows simultaneously.

---

## How It Works

```
                          ┌─────────────┐
                          │   YOU       │
                          │  (Human)    │
                          └──────┬──────┘
                                 │ /bmad-team-sprint <stage>
                                 v
                          ┌─────────────┐
                          │   LEAD      │  Opus model
                          │  (Coordinator)│  Reads config, assigns work,
                          └──┬───┬───┬──┘  monitors, reports back to you
                             │   │   │
                    ┌────────┘   │   └────────┐
                    v            v            v
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ Worker 1 │ │ Worker 2 │ │ Worker 3 │  Sonnet model
              │ (Dev)    │ │ (Dev)    │ │ (QA)     │  Each runs a BMAD
              └──────────┘ └──────────┘ └──────────┘  slash command
```

**Key rules:**
- Workers talk to the lead only (no peer chat) — prevents confusion
- Only the lead writes shared files like sprint-status.yaml — prevents conflicts
- You approve the team plan before anything spawns — you stay in control
- You approve results before the session closes — nothing merges without you

---

## Agent Teams Commands

| Command | What It Does | Notes |
|---------|-------------|-------|
| `/bmad-team-verify` | Analyze story dependencies and generate parallel groups | Run before `/bmad-team-sprint` for safe parallelization |
| `/bmad-team-sprint sprint-dev` | Spawn a sprint development team | |
| `/bmad-team-sprint story-prep` | Spawn a story preparation team | |
| `/bmad-team-sprint test-automation` | Spawn a test automation team | |
| `/bmad-team-sprint architecture-review` | Spawn an architecture review team | |
| `/bmad-team-sprint research` | Spawn a parallel research team | |

**Under the hood:** `/bmad-team-sprint` is a slash command (`.claude/commands/bmad-team-sprint.md`) that invokes the `bmad-agent-teams` skill. The skill is split into 3 conditionally-loaded files for token efficiency:

| File | Loaded When | Content |
|------|-------------|---------|
| `SKILL.md` | Always | Mode selection, prerequisites, orchestration flow overview |
| `verify-workflow.md` | `/bmad-team-verify` | 5-check dependency analysis |
| `sprint-workflow.md` | `/bmad-team-sprint` | 13-step orchestration, factory spawn templates, controls |

Only the relevant workflow file loads per invocation (37–68% token reduction vs loading everything).

You can also invoke the skill directly by asking Claude:
> "Use the bmad-agent-teams skill to run sprint-dev"

---

## All BMAD Slash Commands

Every BMAD workflow is available as a slash command. Teams use a subset of these — workers run them automatically. You can also run any of them solo.

### Phase 1 — Analysis

| Command | Agent | What It Does |
|---------|-------|-------------|
| `/bmad-brainstorming` | Analyst (Mary) | Guided brainstorming session (uses party mode) |
| `/bmad-bmm-market-research` | Analyst (Mary) | Market analysis, competitive landscape, customer needs |
| `/bmad-bmm-domain-research` | Analyst (Mary) | Industry domain deep dive, terminology |
| `/bmad-bmm-technical-research` | Analyst (Mary) | Technical feasibility, architecture options |
| `/bmad-bmm-create-product-brief` | Analyst (Mary) | Guided product brief creation |

### Phase 2 — Planning

| Command | Agent | What It Does |
|---------|-------|-------------|
| `/bmad-bmm-create-prd` | PM (John) | Create Product Requirements Document |
| `/bmad-bmm-validate-prd` | PM (John) | Validate PRD completeness |
| `/bmad-bmm-edit-prd` | PM (John) | Edit/improve existing PRD |
| `/bmad-bmm-create-ux-design` | UX Designer (Sally) | UX design and wireframes |

### Phase 3 — Solutioning

| Command | Agent | What It Does |
|---------|-------|-------------|
| `/bmad-bmm-create-architecture` | Architect (Winston) | Create architecture document |
| `/bmad-bmm-create-epics-and-stories` | PM (John) | Create epics and stories listing |
| `/bmad-bmm-check-implementation-readiness` | Architect (Winston) | Validate PRD/UX/Architecture alignment |

### Phase 4 — Implementation

| Command | Agent | What It Does |
|---------|-------|-------------|
| `/bmad-bmm-sprint-planning` | SM (Bob) | Generate sprint plan and sprint-status.yaml |
| `/bmad-bmm-sprint-status` | SM (Bob) | Summarize sprint status, route to next workflow |
| `/bmad-bmm-create-story` | SM (Bob) | Prepare a story for development (Create Mode) |
| `/bmad-bmm-create-story` | SM (Bob) | Validate story readiness (Validate Mode — same command, different mode) |
| `/bmad-bmm-dev-story` | Dev (Amelia) | Implement a story (code + tests) |
| `/bmad-bmm-code-review` | Dev (Amelia) | Review completed story implementation |
| `/bmad-bmm-qa-automate` | QA (Quinn) | Generate automated tests for implemented code |
| `/bmad-bmm-retrospective` | SM (Bob) | Review completed work, lessons learned |

### Anytime

| Command | Agent | What It Does |
|---------|-------|-------------|
| `/bmad-bmm-correct-course` | SM (Bob) | Navigate significant changes mid-sprint |
| `/bmad-bmm-document-project` | Analyst (Mary) | Analyze existing project, produce docs |
| `/bmad-bmm-generate-project-context` | Analyst (Mary) | Generate project-context.md from codebase |
| `/bmad-bmm-quick-spec` | Quick-Flow Solo Dev | Quick spec for small tasks |
| `/bmad-bmm-quick-dev` | Quick-Flow Solo Dev | Quick dev for small tasks |

### Tech Writer (anytime, multi-turn)

| Command | Agent | What It Does |
|---------|-------|-------------|
| _(invoke tech-writer agent directly)_ | Tech Writer | Write documents following best practices |
| _(invoke tech-writer agent directly)_ | Tech Writer | Update documentation standards preferences |
| _(invoke tech-writer agent directly)_ | Tech Writer | Create Mermaid diagrams |
| _(invoke tech-writer agent directly)_ | Tech Writer | Validate documents against standards |
| _(invoke tech-writer agent directly)_ | Tech Writer | Explain complex concepts |

> **Note:** Tech Writer workflows don't have dedicated slash commands — they use the tech-writer agent directly via BMAD's agent system.

---

## The 5 Team Stages

### 1. Sprint Development (`sprint-dev`) — Phase 4

**What it does:** 2 developers implement stories in parallel, then a reviewer checks their work.

```
         ┌──────────────────┐
         │  SM Lead (Bob)   │ Opus — coordinates sprint
         └──┬─────┬─────┬──┘
            │     │     │
            v     v     v
         Dev 1  Dev 2  Reviewer
         (Amelia)(Amelia)(Amelia)
         Sonnet  Sonnet  Opus
            │     │     │
            v     v     v
    /bmad-bmm  /bmad-bmm  /bmad-bmm
    -dev-story -dev-story -code-review
```

**Requires:** sprint-status.yaml, architecture doc
**Best for:** Implementing 2-3 stories at once

---

### 2. Story Preparation (`story-prep`) — Phase 4

**What it does:** 3 story creators write stories from epics in parallel.

```
         ┌──────────────────┐
         │ PM Lead (John)   │ Opus — reviews story quality against PRD
         └──┬─────┬─────┬──┘
            │     │     │
            v     v     v
        Creator Creator Creator
         (Bob)   (Bob)   (Bob)
         Sonnet  Sonnet  Sonnet
            │     │     │
            v     v     v
       /bmad-bmm-create-story (x3)
```

**Requires:** epics doc, sprint-status.yaml
**Best for:** Bulk story creation from a large epic

---

### 3. Test Automation (`test-automation`) — Phase 4

**What it does:** 2 QA engineers write tests for completed stories in parallel.

```
         ┌──────────────────┐
         │ TEA Lead (Murat) │ Opus — reviews test coverage
         └──────┬─────┬────┘
                │     │
                v     v
              QA 1   QA 2
             (Quinn) (Quinn)
             Sonnet  Sonnet
                │     │
                v     v
          /bmad-bmm-qa-automate (x2)
```

**Requires:** sprint-status.yaml + TEA module installed
**Best for:** Adding test coverage to completed stories

---

### 4. Architecture Review (`architecture-review`) — Phase 3

**What it does:** An analyst and UX designer research in parallel, then the architect synthesizes.

```
         ┌──────────────────────┐
         │ Architect Lead       │ Opus — creates architecture doc
         │ (Winston)            │
         └──────┬─────────┬────┘
                │         │
                v         v
            Analyst    UX Designer
            (Mary)     (Sally)
            Sonnet     Sonnet
                │         │
                v         v
          /bmad-bmm    /bmad-bmm
          -technical   -create-ux
          -research    -design
```

**Requires:** PRD
**Best for:** Pre-sprint architecture work with research support

---

### 5. Research (`research`) — Phase 1

**What it does:** 3 researchers run market, domain, and technical research simultaneously.

```
         ┌──────────────────────┐
         │ Analyst Lead (Mary)  │ Opus — synthesizes all findings
         └──┬──────┬──────┬────┘
            │      │      │
            v      v      v
          Market    Domain   Technical
        Researcher Researcher Researcher
          (Mary)    (Mary)    (Mary)
          Sonnet    Sonnet    Sonnet
            │      │      │
            v      v      v
      /bmad-bmm  /bmad-bmm  /bmad-bmm
      -market-   -domain-   -technical-
      research   research   research
```

**Requires:** Nothing (recommended: project-context.md)
**Best for:** Phase 1 research before creating the product brief

---

## All BMAD Agents — Team Roles

| Agent | Display Name | Manifest Key | Team Role | Stages |
|-------|-------------|-------------|-----------|--------|
| Scrum Master | Bob | `sm` | Lead (sprint-dev), Story Creator (story-prep) | sprint-dev, story-prep |
| Product Manager | John | `pm` | Lead (story-prep) | story-prep |
| Developer | Amelia | `dev` | Dev worker, Code Reviewer | sprint-dev |
| Architect | Winston | `architect` | Lead (architecture-review) | architecture-review |
| Business Analyst | Mary | `analyst` | Lead (research), Analyst worker, all 3 researchers | research, architecture-review |
| UX Designer | Sally | `ux-designer` | UX worker | architecture-review |
| QA Engineer | Quinn | `qa` | QA worker | test-automation |
| Test Architect | Murat | `tea` | Lead (test-automation) | test-automation |

**Not in teams** (solo-only workflows):
- Quick-Flow Solo Dev — for small one-off tasks
- Tech Writer — documentation, diagrams, validation

---

## Workflows: Team vs Solo

| Workflow | Command | Team Stage | Solo? |
|----------|---------|------------|-------|
| Market Research | `/bmad-bmm-market-research` | `research` (worker) | Also solo |
| Domain Research | `/bmad-bmm-domain-research` | `research` (worker) | Also solo |
| Technical Research | `/bmad-bmm-technical-research` | `research` (worker), `architecture-review` (worker) | Also solo |
| Create Architecture | `/bmad-bmm-create-architecture` | `architecture-review` (lead uses) | Also solo |
| Create UX Design | `/bmad-bmm-create-ux-design` | `architecture-review` (worker) | Also solo |
| Create Story | `/bmad-bmm-create-story` | `story-prep` (worker) | Also solo |
| Validate Story | `/bmad-bmm-create-story` | -- | Solo only (same command, Validate Mode) |
| Dev Story | `/bmad-bmm-dev-story` | `sprint-dev` (worker) | Also solo |
| Code Review | `/bmad-bmm-code-review` | `sprint-dev` (worker) | Also solo |
| QA Automate | `/bmad-bmm-qa-automate` | `test-automation` (worker) | Also solo |
| Brainstorm | `/bmad-brainstorming` | -- | Solo only (party mode) |
| Create Product Brief | `/bmad-bmm-create-product-brief` | -- | Solo only |
| Create PRD | `/bmad-bmm-create-prd` | -- | Solo only |
| Validate PRD | `/bmad-bmm-validate-prd` | -- | Solo only |
| Edit PRD | `/bmad-bmm-edit-prd` | -- | Solo only |
| Sprint Planning | `/bmad-bmm-sprint-planning` | -- | Solo only |
| Sprint Status | `/bmad-bmm-sprint-status` | -- | Solo only |
| Create Epics & Stories | `/bmad-bmm-create-epics-and-stories` | -- | Solo only |
| Check Readiness | `/bmad-bmm-check-implementation-readiness` | -- | Solo only |
| Correct Course | `/bmad-bmm-correct-course` | -- | Solo only |
| Retrospective | `/bmad-bmm-retrospective` | -- | Solo only |
| Document Project | `/bmad-bmm-document-project` | -- | Solo only |
| Generate Project Context | `/bmad-bmm-generate-project-context` | -- | Solo only |
| Quick Spec | `/bmad-bmm-quick-spec` | -- | Solo only |
| Quick Dev | `/bmad-bmm-quick-dev` | -- | Solo only |

---

## Setup — Files to Copy

The Agent Teams feature is on branch [feature/agent-teams-config](https://github.com/Hidden-History/BMAD-METHOD/tree/feature/agent-teams-config) of the BMAD repo. These **9 files** need to be copied into your BMAD project:

| # | Source File (from feature branch) | Copy To (your project) | Type |
|---|-----------------------------------|----------------------|------|
| 1 | `.bmad/agent-teams.yaml` | `.bmad/agent-teams.yaml` | **New** — team config |
| 2 | `.claude/skills/bmad-agent-teams/SKILL.md` | `.claude/skills/bmad-agent-teams/SKILL.md` | **New** — orchestration skill (mode selection hub) |
| 3 | `.claude/skills/bmad-agent-teams/verify-workflow.md` | `.claude/skills/bmad-agent-teams/verify-workflow.md` | **New** — verify mode: 5-check dependency analysis |
| 4 | `.claude/skills/bmad-agent-teams/sprint-workflow.md` | `.claude/skills/bmad-agent-teams/sprint-workflow.md` | **New** — sprint mode: 13-step orchestration + templates |
| 5 | `.claude/commands/bmad-team-sprint.md` | `.claude/commands/bmad-team-sprint.md` | **New** — slash command |
| 6 | `.claude/commands/bmad-team-verify.md` | `.claude/commands/bmad-team-verify.md` | **New** — slash command — dependency verification |
| 7 | `.claude/hooks/scripts/bmad_teammate_idle.py` | `.claude/hooks/scripts/bmad_teammate_idle.py` | **New** — quality hook |
| 8 | `.claude/hooks/scripts/bmad_task_completed.py` | `.claude/hooks/scripts/bmad_task_completed.py` | **New** — quality hook |
| 9 | `.bmad/README-agent-teams.md` | `.bmad/README-agent-teams.md` | **New** — full reference docs |

The BMAD repo also includes `docs/how-to/use-agent-teams.md` (user guide) and updates to the project README — these are part of the BMAD distribution but don't need to be copied to your project.

### Quick Copy (from cloned repo)

```bash
# Clone or checkout the feature branch
git clone https://github.com/Hidden-History/BMAD-METHOD.git
cd BMAD-METHOD
git checkout feature/agent-teams-config

# Copy the 9 required files to your project
cp .bmad/agent-teams.yaml         /path/to/your-project/.bmad/
cp .bmad/README-agent-teams.md    /path/to/your-project/.bmad/
cp .claude/commands/bmad-team-sprint.md /path/to/your-project/.claude/commands/
cp .claude/commands/bmad-team-verify.md /path/to/your-project/.claude/commands/

mkdir -p /path/to/your-project/.claude/skills/bmad-agent-teams/
cp .claude/skills/bmad-agent-teams/SKILL.md             /path/to/your-project/.claude/skills/bmad-agent-teams/
cp .claude/skills/bmad-agent-teams/verify-workflow.md    /path/to/your-project/.claude/skills/bmad-agent-teams/
cp .claude/skills/bmad-agent-teams/sprint-workflow.md    /path/to/your-project/.claude/skills/bmad-agent-teams/

mkdir -p /path/to/your-project/.claude/hooks/scripts/
cp .claude/hooks/scripts/bmad_teammate_idle.py  /path/to/your-project/.claude/hooks/scripts/
cp .claude/hooks/scripts/bmad_task_completed.py /path/to/your-project/.claude/hooks/scripts/
```

> **Important:** After copying files, you must also register the hooks in your project's `.claude/settings.json`. See [Setup — Settings](#setup--settings) below.

---

## Setup — Settings

Add to your **project** `.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "hooks": {
    "TeammateIdle": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/scripts/bmad_teammate_idle.py",
            "timeout": 5000
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/scripts/bmad_task_completed.py",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

Add to your **global** `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "teammateMode": "tmux"
}
```

> **Note:** `teammateMode: "tmux"` gives you split panes (each agent visible). Without it, agents run in-process in your main terminal (use Shift+Up/Down to switch).

---

## How to Use It

### Step 0: Verify Dependencies (Recommended)

Before running a team for sprint-dev, story-prep, or test-automation:

```
/bmad-team-verify
```

This analyzes story dependencies and generates `team-parallel-groups.yaml` so the team only parallelizes stories that are safe to run together. You can skip this, but the team will warn you and fall back to sequential assignment.

### Step 1: Pick a stage

```
/bmad-team-sprint sprint-dev
```

### Step 2: Review the plan

Claude reads your config, checks prerequisites, and shows you:
- Team composition (who does what)
- Prerequisites status (which files exist/missing)
- Assignment plan (which stories go to which dev)

### Step 3: Approve

You say yes or no. Nothing spawns without your approval.

### Step 4: Watch it work

- Lead spawns workers in tmux panes (or in-process)
- Each worker runs their BMAD slash command
- Workers report back to the lead when done
- Lead validates quality, spawns reviewers if needed

### Step 5: Approve results

Lead presents a summary. You review and approve before anything is finalized.

### Step 6: Cleanup

Lead shuts down all workers and removes the team. Done.

---

## Prerequisites by Stage

Before running a team, make sure you have the required artifacts:

| Stage | Must Have | Recommended | Nice to Have | How to Create Missing Files |
|-------|-----------|-------------|--------------|---------------------------|
| `sprint-dev` | sprint-status.yaml, architecture doc | team-parallel-groups.yaml | stories | `/bmad-bmm-sprint-planning`, `/bmad-bmm-create-architecture`, `/bmad-team-verify` |
| `story-prep` | epics doc, sprint-status.yaml | team-parallel-groups.yaml | PRD | `/bmad-bmm-create-epics-and-stories`, `/bmad-bmm-sprint-planning`, `/bmad-team-verify` |
| `test-automation` | sprint-status.yaml, TEA module | team-parallel-groups.yaml | stories | `/bmad-bmm-sprint-planning`, `/bmad-team-verify` |
| `architecture-review` | PRD | _(none)_ | project-context, UX design | `/bmad-bmm-create-prd` |
| `research` | _(nothing)_ | _(none)_ | project-context.md | `/bmad-bmm-generate-project-context` |

---

## Version Requirements

| Requirement | Why | How to Check |
|-------------|-----|-------------|
| BMAD installed from source **after Feb 4, 2026** | Research stage needs 3 separate research workflows (market/domain/technical) | Check if `/bmad-bmm-market-research` exists as a slash command |
| BMAD source has `qa.agent.yaml` (not `quinn`) | test-automation stage uses `qa` manifest key | Check `src/bmm/agents/qa.agent.yaml` exists in BMAD source |
| TEA module installed | test-automation stage needs TEA | Check if `/bmad-bmm-qa-automate` exists |
| Claude Code v1.0.34+ | Agent Teams is experimental | Run `claude --version` |

> **Safe stages for any recent BMAD version:** `sprint-dev` and `story-prep` work regardless of version.

---

## Architecture — Token-Efficient Design

The skill uses **conditional loading** to minimize token usage per invocation:

```
                     ┌─────────────────────┐
                     │     SKILL.md        │  Always loaded (~830 tokens)
                     │  Mode Selection Hub │  Routes to the right workflow
                     └──────┬──────┬──────┘
                            │      │
              ┌─────────────┘      └─────────────┐
              v                                   v
    ┌───────────────────┐              ┌────────────────────┐
    │ verify-workflow.md│              │ sprint-workflow.md  │
    │  (~1,940 tokens)  │              │  (~3,825 tokens)    │
    │  5-check analysis │              │  13-step flow       │
    │  Parallel groups  │              │  Factory templates  │
    └───────────────────┘              │  Lead template      │
                                       │  Controls/checklist │
                                       └────────────────────┘
```

**Per-invocation load:**
- Verify mode: ~3,000 tokens (SKILL.md + verify-workflow.md + command)
- Sprint mode: ~7,800 tokens (SKILL.md + sprint-workflow.md + command + config YAML)

**Token reduction vs old monolithic design:**
- Old monolithic SKILL.md: 813 lines (~9,300 tokens)
- Verify mode: ~3,000 tokens → 68% reduction
- Sprint mode: ~7,800 tokens vs old total (~12,350 with YAML) → 37% reduction

**Factory template pattern:** Instead of storing 7 full worker spawn templates (~230 lines), a single base template + role-specific table (~70 lines) lets the orchestrating agent generate prompts on the fly. Same output, ~70% fewer tokens.

---

## Tips

- **Start with `sprint-dev`** — it's the most tested and most useful stage
- **Start small** — try 2 stories before doing 5
- **Run `/bmad-team-verify` first** — analyzes story dependencies so only safe-to-parallelize stories run together
- **Use Shift+Tab** after the team spawns to lock the lead into delegate mode (coordination only)
- **Check tmux panes** if a worker seems stuck — they might be waiting on a permission prompt
- **Permission inheritance** — all teammates inherit the lead's permission mode at spawn. You can't set per-teammate modes during spawning. If workers keep hitting permission prompts, use `dontAsk` mode (safe default). Only use `bypassPermissions` if explicitly needed — it bypasses ALL safety checks.
- **Don't skip prerequisites** — if sprint-status.yaml is missing, run `/bmad-bmm-sprint-planning` first
- **WSL users** — on NTFS mounts, hook scripts may fail silently. Verify hooks have execute permissions (`chmod +x .claude/hooks/scripts/*.py`)