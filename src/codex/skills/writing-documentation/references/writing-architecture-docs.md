# Writing Architecture Docs

## Overview

Architecture documentation captures the technical design decisions and structure of a system. It answers: what does this system do, how is it built, and why was it built this way.

Always investigate the project before asking questions — read the codebase, existing docs, and infrastructure files to form recommendations.

## Document Types

### 1. System Overview

High-level description of the entire system.

**Investigate first:**

- Read main entry points, config files, docker-compose/k8s manifests
- Identify services, databases, external integrations
- Check for existing architecture docs or diagrams

**Recommend a structure, then ask for confirmation. Include:**

- What the system does, who it serves, why it exists
- Tech stack and key dependencies
- Deployment topology (environments, infrastructure)
- C4 Context and Container diagrams (Mermaid)
- Component relationships and data flow
- External integrations and system boundaries

### 2. Architecture Decision Records (ADRs)

Lightweight docs capturing why specific technical decisions were made.

**Use MADR format (Markdown Architectural Decision Records):**

Template: `assets/templates/adr-template.md`

**Key principles:**

- Capture the WHY and alternatives rejected, not just the WHAT
- Store in `docs/architecture/decisions/` with sequential numbering (0001-use-postgres.md)
- Should take 10-15 minutes to write — if longer, scope is too broad
- Status lifecycle: Proposed → Accepted → Deprecated → Superseded
- Link to the ADR that supersedes when deprecating

**When to write an ADR:**

- Choosing between technologies or approaches
- Deviating from team/industry conventions
- Making decisions that would be expensive to reverse
- When someone asks "why did we do it this way?"

### 3. Component Deep-Dives

Detailed documentation for individual services or modules.

**Investigate first:**

- Read the component's source, tests, and config
- Identify public interfaces, data models, dependencies

**Include:**

- Responsibilities and ownership
- Public interfaces (APIs, events, contracts)
- Data flow in and out
- Dependencies (upstream and downstream)
- Failure modes and error handling
- Sequence diagrams for key interactions (Mermaid)
- Links back to the system overview for context

### 4. Diagrams

Visual representations embedded in documentation.

**Default to Mermaid** — renders natively in GitHub, GitLab, and most doc tools. Diagrams-as-code, version-controlled, reviewable in PRs.

**Use C4 model (Simon Brown) for system architecture:**

- Context → Container → Component → Code layers
- Each level adds detail, each has a distinct audience

| Need                                     | Diagram Type     |
| ---------------------------------------- | ---------------- |
| System boundaries and external actors    | C4 Context       |
| Services, databases, message queues      | C4 Container     |
| Internal module structure                | C4 Component     |
| Request/response flow between components | Sequence diagram |
| Data transformations and pipelines       | Flowchart        |
| Lifecycle states                         | State diagram    |
| Entity relationships                     | ER diagram       |

**Diagram best practices:**

- One concept per diagram — don't overload
- Include a title and brief caption
- Use consistent naming across diagrams
- Keep Mermaid source in the markdown file, not as external images
- For complex C4 diagrams, consider Structurizr DSL

## Modern Practices

- **Living documentation** — Architecture docs live in the repo alongside code, reviewed in PRs
- **Diagrams-as-code** — Mermaid in markdown, version-controlled. No stale Visio files.
- **AI context layer** — Architecture docs double as context for AI agents when clearly structured
- **arc42 awareness** — For comprehensive needs, reference the arc42 template (quality requirements, risks, glossary, deployment view)

## Process

1. Investigate the project thoroughly (codebase, config, infra)
2. Recommend which doc type(s) are needed based on what you find
3. Ask clarifying questions only for what you couldn't determine
4. Draft using the appropriate structure above
5. Embed Mermaid diagrams inline
6. Cross-reference related docs (ADRs link to system overview, deep-dives link to each other)
7. Ask: "Anything else to highlight or include that I might have missed?"
