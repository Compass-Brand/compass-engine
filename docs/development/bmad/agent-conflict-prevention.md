# Agent Conflict Prevention in Polyrepo Context

Last reviewed: 2026-04-08

## Why Agents Conflict

When multiple AI agents implement different parts of a system, each agent operates with its own session context and makes independent decisions. Without shared constraints, agents routinely produce contradictory output:

- **API style divergence.** One agent uses REST endpoints while another uses GraphQL mutations in the same system.
- **Convention drift.** One agent names database columns in snake_case while another uses camelCase, producing an inconsistent schema.
- **State management splits.** One agent introduces Redux while another uses React Context, creating two competing patterns in the same frontend.
- **Pattern fragmentation.** Agents invent local solutions for cross-cutting concerns (error handling, logging, authentication) that conflict when the code is integrated.

These conflicts multiply in a polyrepo environment. Agents working in different repositories have no shared filesystem, no shared session, and no automatic way to discover what decisions other agents have already made. Without explicit coordination mechanisms, polyrepo work drifts faster than monorepo work.

## How Architecture Documentation Prevents Conflicts

Architecture documentation acts as the shared source of truth that every agent reads before making implementation decisions. The upstream BMAD approach uses three reinforcing mechanisms:

### 1. Explicit Decisions via ADRs

Every significant technology choice is documented as an Architecture Decision Record with context, options considered, the decision itself, rationale, and accepted consequences. ADRs cover the decisions most likely to cause agent conflicts:

| Topic | Example Decision |
| --- | --- |
| API style | GraphQL for all client-server communication |
| Database | PostgreSQL with snake_case naming conventions |
| Authentication | JWT with refresh token rotation |
| State management | Zustand, not Redux or Context |
| Styling | Tailwind CSS with custom design tokens |
| Testing | Vitest and Playwright, not Jest |

### 2. FR/NFR-Specific Guidance

Architecture maps each functional requirement to a specific technical approach, so agents implementing different features use the same patterns for the same concerns.

### 3. Standards and Conventions

Explicit documentation of directory structure, naming conventions, code organization, and testing patterns removes ambiguity from agent decisions.

The result is a shared context layer:

```text
PRD: "What to build"
     |
Architecture: "How to build it"
     |
Agent A reads architecture -> implements Epic 1
Agent B reads architecture -> implements Epic 2
Agent C reads architecture -> implements Epic 3
     |
Result: Consistent implementation
```

## The Role of project-context.md

The `project-context.md` file is the primary conflict prevention mechanism at the implementation level. It captures rules, patterns, and preferences in a concise, LLM-optimized format that every implementation workflow loads automatically.

### What It Contains

- **Technology stack and versions.** Exact frameworks, languages, and tools with pinned versions.
- **Critical implementation rules.** Patterns and conventions that agents might otherwise miss — things that are unobvious and cannot be inferred from reading a few code snippets.

### When Workflows Load It

Every workflow that makes implementation decisions loads `project-context.md` if it exists:

- `bmad-create-architecture` — respects technical preferences during solutioning
- `bmad-create-story` — informs story creation with project patterns
- `bmad-dev-story` — guides implementation decisions
- `bmad-code-review` — validates against project standards
- `bmad-quick-dev` — applies patterns during implementation
- `bmad-sprint-planning`, `bmad-retrospective`, `bmad-correct-course` — provides project-wide context

### Why This Matters for Conflict Prevention

Without `project-context.md`, each agent decides independently based on generic best practices. With it, all agents align with the same rules before writing any code. This is especially important for Quick Flow work, which skips the PRD and architecture phases where conventions would otherwise be established.

## Polyrepo-Specific Concerns

Compass operates across 12 repositories at three altitudes. This makes agent conflict prevention both more important and more difficult than in a single-repo setup.

### Three Altitudes of Authority

The Compass BMAD workflow defines three execution scopes, each with distinct ownership rules:

| Altitude | Scope | Examples | Owns |
| --- | --- | --- | --- |
| Workspace root | Portfolio orchestration | `compass-brand` | Cross-repo coordination, repo topology, initiative routing |
| Parent repos | Domain or program orchestration | `compass-forge`, `compass-services` | Child workstream coordination within a domain |
| Leaf repos | Repo-local delivery | `compass-engine`, `forge-rag`, `legacy-system-analyzer` | PRDs, architecture, stories, implementation evidence |

The cardinal rule: **authoritative ownership stays at the actual repo root being worked on.** Parent and workspace repos coordinate; they do not own child repo-local delivery artifacts. An agent working in `compass-brand` must never create PRDs, architecture docs, or stories that belong to `compass-engine`.

### How Agents in Different Repos Maintain Consistency

Three control surfaces enforce cross-repo consistency:

1. **`repositories.yaml`** is authoritative for repo IDs, parent-child relationships, and repo-root ownership. Workspace and parent repos maintain this file. It tells agents which repos exist and how they relate.

2. **`initiative-index.yaml`** is authoritative for concurrent initiative routing state in orchestration scope. When a workspace-level phase fans out into work across multiple repos, this file tracks which repos are targeted by which initiatives and prevents overlap conflicts.

3. **Per-repo `project-context.md`** ensures that agents working in different repos follow the conventions established for each repo, while shared conventions propagate through the planning hierarchy.

### Cross-Repo Interface Contracts

When multiple repos share interfaces (APIs, shared libraries, data contracts), the Polyrepo Routing Rules require explicit gating:

> Multiple concurrent initiatives are allowed in workspace or orchestration scope, but overlap on the same repo, shared interface, or release boundary must be explicitly gated.

This means agents cannot independently modify shared interfaces without coordination through the initiative routing mechanism. The workspace-level phase sync and initiative routing workflows exist precisely to catch and prevent these conflicts before implementation begins.

### Nested Repo Execution Pattern

Every targeted repo still runs its own repo-local Phase Sync before detailed analysis begins there. This ensures that even when work is initiated from a parent or workspace scope, the leaf repo's own planning state is refreshed and its own `project-context.md` governs implementation decisions.

## How BMAD's 4-Phase Methodology Prevents Conflicts

BMAD's phased progression inherently prevents agent conflicts by establishing shared artifacts before implementation begins. Each phase produces artifacts that constrain the next phase:

### Phase 1: Analysis

High-level analysis, brainstorming, market research, domain research, and product briefs establish the problem space. All agents that later work on the same initiative share the same analytical foundation.

### Phase 2: Planning and Experience Design

The PRD and UX design establish what the system must do and how users interact with it. These artifacts eliminate conflicts about scope, features, and user flows before any agent writes architecture or code.

### Phase 3: Solutioning

Architecture, `project-context.md` generation, and security review establish how the system will be built. ADRs lock in technology decisions. The project context file captures implementation rules. After this phase, agents implementing different epics share the same technical foundation.

### Phase 4: Implementation

Stories, dev execution, code review, and testing operate within the constraints established by phases 1-3. Agents implementing different stories reference the same architecture, the same project context, and the same conventions.

The key insight: **conflicts arise when agents make decisions that should have been made earlier.** BMAD's required progression chain forces those decisions into shared artifacts before parallel implementation begins. The `bmad-correct-course` workflow exists for cases where implementation reveals that earlier decisions need revision, routing changes back through the proper artifacts rather than allowing ad-hoc divergence.

## Best Practices for Concurrent BMAD Workflows Across Repos

When running BMAD workflows in parallel across multiple Compass repositories, follow these practices to prevent agent conflicts:

### 1. Establish Workspace-Level Coordination First

Run Phase Sync and Initiative Routing at the workspace or parent level before starting repo-local work. This produces the `initiative-index.yaml` that prevents overlap and the initiative workstream directories that scope each repo's contribution.

### 2. Generate project-context.md in Every Active Repo

Before implementation begins in any repo, ensure `project-context.md` exists and reflects the current architecture decisions. Run `bmad-generate-project-context` after architecture is complete, or create the file manually if the repo has strong existing conventions.

### 3. Gate Shared Interface Changes

When an initiative touches interfaces shared between repos (APIs, shared libraries, data contracts), explicitly gate those changes through the initiative routing mechanism. Do not allow agents in different repos to independently modify shared boundaries.

### 4. Keep repositories.yaml Current

Run `bmad-bmm-sync-repositories` when repo topology changes. Stale repo registry data causes agents to make incorrect assumptions about which repos exist and how they relate.

### 5. Respect the Authority Hierarchy

- Machine files (`roadmap.yaml`, `phase-state.yaml`, `repositories.yaml`, `initiative-index.yaml`) are authoritative over their human-readable counterparts.
- Nested repo roots are authoritative for their own planning and docs state.
- Parent repos coordinate; they do not own child repo-local artifacts.

### 6. Refresh, Do Not Assume

Brownfield work should inherit prior lessons and previous-phase constraints, but always refresh assumptions against current repo reality. Run project context generation even if a context file already exists — the codebase may have evolved.

### 7. Use bmad-correct-course for Mid-Implementation Changes

When implementation reveals that an architecture decision needs to change, do not allow individual agents to diverge. Route the change through `bmad-correct-course` so the shared artifacts are updated and all agents pick up the revised guidance.

## Related Documentation

- [BMAD Overview](./bmad-overview.md) — methodology architecture and key concepts
- [Project Context](./project-context.md) — the primary conflict prevention artifact
- [Extension Modules](./extension-modules.md) — modules that add agents with conflict potential
- Canonical workflow: `src/bmad/BMAD-workflow.md` — Polyrepo Routing Rules section
