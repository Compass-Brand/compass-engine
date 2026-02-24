---
name: writing-documentation
description: Use when writing, improving, or reviewing any documentation — READMEs, architecture docs, user guides, developer guides, or decision records. Also use when setting up documentation structure for a new or existing project.
---

# Writing Documentation

**REQUIRED:** Invoke `writing-clearly-and-concisely` for all prose output from this skill.

## Overview

Gateway skill that routes to the right documentation approach based on task and doc type. Documentation serves two audiences: humans and AI agents. Good docs are audience-aware, live in the repo, and stay fresh.

## Shared Principles

These apply across ALL branches — every doc type, every task.

1. **Investigate first, ask later** — Before asking questions, read the project (package.json, existing docs, folder structure, main source files, git history). Form a recommendation based on what you find. Present it with reasoning and ask if the user agrees. Never ask blind questions.
2. **Audience first** — Before writing a word, know who reads this and what they need
3. **Docs live in the repo** — Markdown, version-controlled, reviewed in PRs. Not wikis that drift.
4. **Show, don't tell** — Code examples, diagrams, screenshots over paragraphs of explanation
5. **One purpose per doc** — Don't mix tutorials with reference with architecture rationale
6. **Freshness is a feature** — Include "last reviewed" dates. Stale docs are worse than no docs.
7. **AI-aware** — Structure docs so both humans and AI agents can consume them effectively. Prefer explicit headings, scannable tables, and machine-parseable formats.

## Routing

### Step 1: Identify the task

| Task                          | Route                                              |
| ----------------------------- | -------------------------------------------------- |
| Write / create / add          | Go to Step 2 (doc-type branch)                     |
| Update / revise               | Go to Step 2 (doc-type branch)                     |
| Review / audit / check        | `references/reviewing-documentation.md` AND Step 2 |
| Set up / organize / structure | `references/setting-up-documentation.md`           |

### Step 2: Identify the doc type

| Doc Type                                         | Reference File                                                                                         |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| README                                           | `references/writing-readmes.md`                                                                        |
| Architecture (overview, ADR, component, diagram) | `references/writing-architecture-docs.md` (for Mermaid diagram syntax, also invoke `mermaid-diagrams`) |
| Guide (tutorial, how-to, reference, explanation) | `references/writing-guides.md`                                                                         |

If the doc type is ambiguous, investigate the project and recommend a type. Don't guess.

### Step 3: Load and follow

- Read the identified reference file(s) from the table above
- For review tasks: load `references/reviewing-documentation.md` PLUS the relevant doc-type file
- Follow the process defined in the reference file

## After Drafting

Always ask: "Anything else to highlight or include that I might have missed?"

Review the draft against these checks:

- Does it serve its stated audience?
- Can someone act on it without asking follow-up questions?
- Are code examples runnable, not pseudocode?
- Is every section earning its space?

## Supporting Files

| File                              | Purpose                                                |
| --------------------------------- | ------------------------------------------------------ |
| `references/style-guide.md`       | Common documentation mistakes and how to avoid them    |
| `references/section-checklist.md` | README section matrix by project type                  |
| `assets/templates/`               | Scaffolding for specific doc types (zero context cost) |

## The Bottom Line

Good documentation is tested against its audience the same way code is tested against its spec. If a reader would need to ask a question after reading your doc, the doc has a bug.
