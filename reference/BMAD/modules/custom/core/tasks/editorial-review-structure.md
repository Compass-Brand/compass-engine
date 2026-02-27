---
name: editorial-review-structure
description: "Structural editing review that proposes cuts, reordering, and simplification while preserving meaning."
standalone: true
---

# Task: Editorial Review - Structure

## Objective
Review document structure and propose high-impact structural changes that improve clarity, flow, and value density.

## Inputs
- `content` (required): document to review.
- `style_guide` (optional): overrides default style/structure principles except content sacrosanct.
- `purpose` (optional): intended document purpose.
- `target_audience` (optional): target readers.
- `reader_type` (optional, default `humans`): `humans` or `llm`.
- `length_target` (optional): desired reduction target.

## Mandatory Execution Rules
- Execute all steps in order.
- Do not perform copy-edit rewrites here; this is structural review.
- Content is sacrosanct: do not alter ideas, only organization and presentation.
- Propose changes; do not auto-apply changes.
- If `style_guide` is provided, it overrides all generic principles except content sacrosanct.

## Core Principles
- High-value density: each section must justify its existence.
- Front-load value: put critical information first.
- One source of truth: consolidate truly duplicated information.
- Scope discipline: cut or link content that belongs elsewhere.
- Comprehension through calibration: optimize brevity without losing understanding.

## Reader-Type Principles
### Humans
- Preserve comprehension aids when they add value.
- Keep useful scaffolding: overviews, examples, summaries, transitions.
- Maintain engagement and pacing when functional.

### LLM
- Prioritize precision and unambiguous references.
- Use consistent terminology.
- Remove emotional or orientation-only language.
- Prefer structured formats where possible.
- Preserve examples that anchor expected behavior.

## Structure Models
- Tutorial or Guide (Linear): prerequisites and sequence-first.
- Reference (Database): random access and consistent schema.
- Explanation (Conceptual): abstract to concrete scaffolding.
- Prompt or Task Definition (Functional): explicit ordered execution and clear separation of concerns.
- Strategic or Context (Pyramid): conclusion/recommendation first, supporting evidence after.

## Flow
### 1. Validate Input
- Halt if content is empty or fewer than 3 words.
- Validate `reader_type` in `{humans, llm}`.
- Identify heading and section structure.
- Record baseline word and section counts.

### 2. Understand Purpose
- Use provided `purpose` and `target_audience` when available, otherwise infer.
- State one sentence:
- `This document exists to help [audience] accomplish [goal].`
- Select best-fit structure model for this document.

### 3. Structural Analysis
- Map major sections and approximate word counts.
- Evaluate against selected structure model.
- For each section, decide if it directly serves purpose.
- Identify candidates to:
- `CUT`
- `MERGE`
- `MOVE`
- `CONDENSE`
- `QUESTION`
- `PRESERVE`
- Identify true redundancy and scope violations.
- Identify buried critical information.

### 4. Flow Analysis
- Evaluate reader journey sequence and dependency order.
- Find premature detail and missing scaffolding.
- Flag anti-patterns:
- FAQ content that belongs inline.
- appendices that should be removed or linked.
- overview sections duplicating body verbatim.
- For humans, evaluate pacing and readability support.

### 5. Generate Recommendations
- Produce prioritized recommendation list.
- Include one-sentence rationale per recommendation.
- Estimate impact in words for each item.
- Check whether recommendations meet `length_target` if provided.
- Warn on human-reader comprehension risks where applicable.

### 6. Output Results
- If no substantive changes are needed, output:
- `No substantive changes recommended-document structure is sound`
- Otherwise return summary + recommendations using required format.

## Required Output Format
```markdown
## Document Summary
- **Purpose:** [purpose]
- **Audience:** [audience]
- **Reader type:** [humans|llm]
- **Structure model:** [selected model]
- **Current length:** [X] words across [Y] sections

## Recommendations

### 1. [CUT/MERGE/MOVE/CONDENSE/QUESTION/PRESERVE] - [Section]
**Rationale:** [one sentence]
**Impact:** ~[X] words
**Comprehension note:** [optional]

## Summary
- **Total recommendations:** [N]
- **Estimated reduction:** [X words / Y%]
- **Meets length target:** [Yes/No/No target]
- **Comprehension trade-offs:** [if any]
```

## Halt Conditions
- Content empty or fewer than 3 words.
- Invalid `reader_type`.
