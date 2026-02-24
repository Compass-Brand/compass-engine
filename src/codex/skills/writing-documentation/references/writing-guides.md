# Writing Guides

## Overview

Guides help people accomplish goals or understand systems. The most common problem with guides is mixing different types of content in one document — tutorial steps mixed with reference tables mixed with conceptual explanations. The Diataxis framework solves this.

Always investigate the project before recommending a guide type — read the codebase, existing docs, and user-facing interfaces to understand what's needed.

## The Diataxis Framework

Four quadrants, each with a distinct purpose and structure:

### 1. Tutorials (learning-oriented)

Guide the reader through building something from scratch.

**Characteristics:**

- Linear, step-by-step, hands-on
- Every step produces a visible result — the reader is never lost
- Starts from zero assumptions. "Install X" is a valid first step.
- Success metric: can someone with no context complete it start to finish?

**Key rules:**

- Never explain concepts mid-tutorial — link to an Explanation doc instead
- Each step must be actionable and verifiable
- Include expected output after each step so the reader knows they're on track
- If a step can fail, include troubleshooting inline

**Template:** `assets/templates/guide-tutorial.md`

### 2. How-To Guides (task-oriented)

Solve a specific real-world problem.

**Characteristics:**

- Assumes the reader has working knowledge — no hand-holding
- Non-linear — reader can skip to the section they need
- Recipe structure: prerequisites, steps, verification, troubleshooting

**Key rules:**

- One goal per guide. If covering two tasks, split into two guides.
- State prerequisites clearly at the top
- Include a "Verify it worked" section at the end
- Add a "Troubleshooting" section for common failures

**Template:** `assets/templates/guide-howto.md`

### 3. Reference (information-oriented)

Comprehensive, exhaustive, lookup-oriented documentation.

**Characteristics:**

- Organized by topic/module, not by workflow
- Describes what things ARE and how they BEHAVE, not how to use them
- Consistent structure: every entry follows the same format
- Code examples for every API/config option

**Key rules:**

- Austere and to the point — no tutorials or opinions
- No "obvious" defaults left undocumented
- Consistent format across all entries (use tables for parameters, consistent headers)
- Include type information, default values, and valid ranges

### 4. Explanation (understanding-oriented)

Answers "why" and "how does this work under the hood."

**Characteristics:**

- Conceptual, discursive, explores trade-offs and alternatives
- Not tied to a specific task — provides the mental model
- Useful for: architecture rationale, design philosophy, "why we chose X over Y"

**Key rules:**

- This is the ONLY quadrant where discussion and opinion belong
- Can be longer-form and narrative
- Link to related How-To guides and Reference docs for practical application

## Decision Tree

When the user asks for "docs" or "a guide", help them identify the right quadrant:

| The reader wants to...                             | Quadrant    | Template                             |
| -------------------------------------------------- | ----------- | ------------------------------------ |
| Learn by doing, follow along step by step          | Tutorial    | `assets/templates/guide-tutorial.md` |
| Accomplish a specific goal they already understand | How-To      | `assets/templates/guide-howto.md`    |
| Look up a fact, parameter, or API detail           | Reference   | (use consistent entry format)        |
| Understand why something works the way it does     | Explanation | (narrative format)                   |

If unsure, investigate what exists and recommend based on gaps.

## Modern Practices

### TTFHW (Time to First Hello World)

The north-star metric for developer docs. How fast can someone go from zero to a working example? Measure and minimize it.

### Docs-as-Code

- Markdown in the repo, versioned with the code, reviewed in PRs
- Use static site generators (Docusaurus, VitePress, MkDocs) for published docs

### Progressive Disclosure

Don't front-load every option. Start simple, let the reader drill deeper. Expandable sections, "Advanced" subsections, and links to reference docs.

### Code Examples That Run

Every example should be copy-pasteable and produce the stated result. Test them. Stale examples destroy trust faster than missing examples.

### Documentation-Driven Development

Write the guide first, then implement. The guide becomes the spec. Creates a natural feedback loop between docs and code.

### Cross-Linking Between Quadrants

- Tutorials link to Reference for parameter details
- How-To guides link to Explanation for rationale
- Explanation links to How-To for practical application
- Reference stands alone but links to tutorials for "getting started"

## Process

1. Investigate the project and existing documentation
2. Identify which Diataxis quadrant fits (or recommend multiple docs)
3. Recommend the type with reasoning, ask for confirmation
4. Identify audience and their existing knowledge level
5. Draft using the quadrant's structure and rules
6. Cross-link to other docs where appropriate
7. Ask: "Anything else to highlight or include that I might have missed?"
