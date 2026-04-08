# Project Context File Guide

Last reviewed: 2026-04-08

## What Is project-context.md?

The `project-context.md` file is an AI-relevant snapshot of a project's implementation rules, technology stack, coding conventions, and critical patterns. It serves as a "constitution" that AI agents load before making any implementation decisions, ensuring consistent code generation across every workflow and session.

Without it, agents fall back on generic best practices that may conflict with established project conventions. With it, every agent — whether creating architecture, writing stories, or reviewing code — aligns to the same rules.

## Why It Matters

BMAD agents search for `**/project-context.md` during initialization. When found, they load it as foundational reference before doing any work. This single file is referenced by over 100 skills and workflows across all four BMAD phases, making it the most widely consumed runtime artifact in the system.

The impact is especially significant for:

- **Quick Flow projects** — Quick Spec and Quick Dev skip PRD and architecture, so the project context file fills the gap that those artifacts would normally provide.
- **Multi-agent consistency** — Sprint planning, story creation, dev story, code review, and retrospective all load the same rules, preventing drift between agents.
- **Brownfield projects** — Agents that discover existing patterns from the context file avoid breaking established conventions.

## When to Generate

| Scenario | Timing | Rationale |
| --- | --- | --- |
| **Brownfield project** | Early, during initialization (step 5 of Project-Level Setup) | Capture existing patterns so agents respect them from the start |
| **Greenfield project** | After high-level framing, before detailed analysis | The project needs enough shape for meaningful context; regenerate richer context after architecture |
| **Phase start** | Required at the top of Detailed Analysis (step 1 of each phase) | Refresh assumptions against current repo reality and incorporate lessons from previous phases |
| **Architecture changes** | After significant architectural decisions change | Keep agents aligned with the current technical direction |
| **Pattern evolution** | When new conventions are established during implementation | Prevent inconsistency between agents working on different stories |

## Where It Lives in Compass

In Compass projects, the project context file is stored in the planning tree:

```text
planning/current/research/project-context/project-context.md
```

This path is governed by the `current_project_context_dir` variable in the BMAD configuration (`_bmad/modules/custom/bmm/config.yaml`). The workflow writes its output to `{current_project_context_dir}/project-context.md`.

Because agents search using the glob pattern `**/project-context.md`, the file is discovered regardless of exact placement, but the planning tree location is the canonical Compass convention.

## How It Differs from Upstream

Upstream BMAD stores the file at:

```text
_bmad-output/project-context.md
```

Compass diverges from this convention in two ways:

1. **Location** — Compass places the file under `planning/current/research/project-context/` to integrate with the roadmap-driven planning tree. This means the file participates in phase closeout (archived to `planning/previous/`) and phase sync (refreshed for each new slice).
2. **Config path resolution** — The Compass custom workflow reads `current_project_context_dir` from the custom config file (`_bmad/modules/custom/bmm/config.yaml`) rather than the native `output_folder`. The native workflow resolves output from `_bmad/bmm/config.yaml`.

Both locations are found by the `**/project-context.md` glob, so agents work correctly with either convention. The Compass location provides better lifecycle management across phases.

## The Generate Command

Run the workflow with:

```text
/bmad-bmm-generate-project-context
```

The workflow executes three steps:

### Step 1: Discovery

- Searches for an existing `project-context.md` and offers to update or replace it
- Scans architecture documents, package files, configuration files, and existing code
- Identifies technology stack with specific versions, naming conventions, code organization patterns, and testing setup
- Presents a discovery summary for user review

### Step 2: Collaborative Generation

For each content category (technology stack, language rules, framework rules, testing rules, code quality, workflow rules, critical anti-patterns), the workflow:

- Presents discovered rules to the user
- Offers an A/P/C menu: **A**dvanced Elicitation for deeper exploration, **P**arty Mode for multi-perspective review, or **C**ontinue to accept and move on
- Appends accepted content to the output file

### Step 3: Completion

- Reviews the full file for LLM context efficiency
- Removes redundant or obvious information
- Optimizes formatting for quick scanning
- Updates frontmatter with completion status

The workflow is interactive and collaborative. The agent acts as a facilitator, not a content generator — it discovers patterns and proposes rules, but the user approves each section.

## What Goes into the File

The file has two main sections:

### Technology Stack and Versions

Exact frameworks, languages, and tools with pinned versions:

```markdown
## Technology Stack & Versions

- Python 3.11+, FastAPI, PostgreSQL + Memgraph
- Testing: pytest with 80% minimum coverage
- Styling: Tailwind CSS with custom design tokens
```

### Critical Implementation Rules

Rules organized by category, focused on what is **unobvious** — things agents would not infer from reading a few code snippets:

| Category | Examples |
| --- | --- |
| Language-specific | Strict mode requirements, import conventions, error handling patterns |
| Framework-specific | Hook usage, component structure, state management, API client singletons |
| Testing | Test organization, mock conventions, coverage requirements, integration vs unit boundaries |
| Code quality and style | Linting rules, naming patterns, file/folder structure, documentation requirements |
| Development workflow | Branch naming, commit format, PR requirements, deployment patterns |
| Critical anti-patterns | Security constraints, performance gotchas, patterns to avoid, edge cases |

Keep the file lean. Do not document standard practices that apply universally. Every rule should provide unique value that prevents an implementation mistake.

## Which Workflows and Agents Consume It

The project context file is loaded by agents and workflows across all phases:

| Phase | Consumers |
| --- | --- |
| Analysis | Analyst, Tech Writer, Innovation Strategist, Design Thinking Coach, WDS Analyst |
| Planning | PRD creation and discovery, UX Design initialization and discovery, Outline Scenarios |
| Solutioning | Architecture (init, context, starter, decisions), Threat Analyst, Security Architect |
| Implementation | Dev Story, Create Story, Code Review, Sprint Planning, Sprint Status, Retrospective, Quick Dev, Quick Spec, Correct Course, QA, Test Design, Test Review, NFR Assessment, Secure Gates |
| Anytime | BMAD Master, Creative Problem Solver, Workflow Map |
| Builder | Agent Builder, Module Builder, Workflow Builder |

Agents load it with the pattern: "Search for `**/project-context.md`. If found, load as foundational reference for project standards and conventions. If not found, continue without it."

## Manual Creation and Editing

Auto-generation works best when there is enough code and configuration to analyze. For new projects or when the generated output is insufficient, create or edit the file manually.

### Creating from Scratch

1. Create the file at the Compass path:
   ```bash
   mkdir -p planning/current/research/project-context
   touch planning/current/research/project-context/project-context.md
   ```
2. Add the frontmatter and two main sections:
   ```markdown
   ---
   project_name: 'Your Project'
   date: '2026-04-08'
   status: 'complete'
   ---

   # Project Context for AI Agents

   ## Technology Stack & Versions

   - [List exact technologies and versions]

   ## Critical Implementation Rules

   - [List rules agents might otherwise miss]
   ```
3. Focus on unobvious rules. If an agent would likely get it right without guidance, leave it out.

### Editing an Existing File

Edit the file directly at any time. Common reasons to update:

- Architecture decisions changed
- New conventions emerged during implementation
- Agents repeatedly made the same mistake (add a rule to prevent it)
- Technology versions were upgraded
- A phase closeout revealed lessons that should become rules

You can also re-run `/bmad-bmm-generate-project-context` to regenerate after significant changes, then review and refine the output.

## Relationship to CLAUDE.md and Other AI Configuration

The project context file and CLAUDE.md serve different purposes and different audiences:

| Aspect | project-context.md | CLAUDE.md |
| --- | --- | --- |
| **Audience** | BMAD agents and workflows | Claude Code (the IDE agent) |
| **Loaded by** | BMAD skills via `**/project-context.md` glob | Claude Code automatically on session start |
| **Scope** | Implementation rules for the current project phase | Repository-wide guidance, tech stack, methodology |
| **Lifecycle** | Refreshed each phase, archived during closeout | Persists across phases, updated less frequently |
| **Content focus** | Unobvious patterns agents must follow when writing code | Project structure, commands, development methodology, tooling |
| **Location** | `planning/current/research/project-context/` | Repository root |

The two files complement each other:

- **CLAUDE.md** tells Claude Code what the project is, how it is structured, and what methodology to follow. It is the entry point for any Claude Code session.
- **project-context.md** tells BMAD agents how to implement code consistently. It is loaded by specific workflows when they need implementation guidance.

Other related configuration files include:

- **config.yaml** (`_bmad/modules/custom/bmm/config.yaml`) — BMAD runtime configuration including paths, project name, and user preferences
- **.claude/rules/** — Claude Code behavioral rules (coding style, security, testing, git workflow) that apply outside of BMAD workflows
- **Architecture documents** — Detailed technical design that the project context file summarizes into actionable rules

When the project context file and CLAUDE.md overlap (both might mention the tech stack, for example), keep CLAUDE.md as the high-level overview and the project context file as the implementation-specific detail that agents need when writing code.

## Related Documentation

- [BMAD Method Overview](./bmad-overview.md) — architecture and phases
- [Custom Modules](./custom-modules.md) — Compass module principles
- [BMAD Workflow](../../../src/bmad/BMAD-workflow.md) — canonical workflow specification
- [Upstream Explanation](../../../BMAD-METHOD/docs/explanation/project-context.md) — upstream project context documentation
