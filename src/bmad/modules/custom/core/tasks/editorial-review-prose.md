---
name: editorial-review-prose
description: "Clinical copy-editing review focused on communication clarity, with minimal intervention."
standalone: true
---

# Task: Editorial Review - Prose

## Objective
Review prose for communication issues that impede comprehension and return suggested fixes in a three-column markdown table.

## Inputs
- `content` (required): cohesive text unit (markdown, plain text, or text-heavy XML).
- `style_guide` (optional): project style guide that overrides default style principles.
- `reader_type` (optional, default `humans`): `humans` or `llm`.

## Mandatory Execution Rules
- Execute all steps in order.
- Do not skip validation gates.
- Content is sacrosanct: never change ideas, only improve expression.
- Preserve author voice and intentional stylistic choices.
- Skip code blocks, frontmatter, and structural markup.
- Deduplicate repeated issues across locations.
- Merge overlapping fixes and avoid conflicting suggestions.
- If uncertain, use query phrasing (`Consider: ...?`) instead of asserting.
- If `style_guide` is provided, it overrides all generic style principles except content sacrosanct.

## Review Principles
- Minimal intervention: smallest edit that resolves clarity.
- Comprehension first: prioritize issues that block understanding.
- No preference rewrites: do not "polish" stylistic choices solely by taste.
- Reader calibration:
- `humans`: prioritize flow, readability, natural progression.
- `llm`: prioritize explicit references, consistent terminology, reduced ambiguity.

## Flow
### 1. Validate Input
- Halt if content is empty or fewer than 3 words.
- Validate `reader_type` in `{humans, llm}`.
- Identify content type and mark regions to skip (code/frontmatter/markup).

### 2. Analyze Style and Voice
- Infer tone and voice to preserve.
- Identify intentional conventions and jargon.
- Calibrate review priorities by `reader_type`.

### 3. Perform Editorial Review
- Review prose-only sections.
- Identify comprehension blockers.
- Propose minimal fixes for each issue.
- Deduplicate repeated issues by grouping locations.
- Merge overlapping edits into single recommendations.

### 4. Output Results
- If issues found, return a three-column markdown table.
- If no issues found, output exactly:
- `No editorial issues identified`

## Required Output Format
```markdown
| Original Text | Revised Text | Changes |
|---------------|--------------|---------|
| The exact original passage | The suggested revision | Brief explanation of what changed and why |
```

## Example
```markdown
| Original Text | Revised Text | Changes |
|---------------|--------------|---------|
| The system will processes data and it handles errors. | The system processes data and handles errors. | Fixed subject-verb agreement and removed redundant pronoun. |
| Users can chose from options (lines 12, 45, 78) | Users can choose from options | Corrected spelling in three locations. |
```

## Halt Conditions
- Content empty or fewer than 3 words.
- `reader_type` is not `humans` or `llm`.
