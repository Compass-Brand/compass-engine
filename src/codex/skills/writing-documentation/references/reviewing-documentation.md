# Reviewing Documentation

## Overview
Documentation review ensures docs are accurate, complete, and healthy. This branch activates for any "review", "audit", "check", or "improve existing" task. It loads alongside the relevant doc-type branch so the reviewer knows what good looks like for that type.

## Process
1. Read the document fully
2. Identify its type (README, architecture doc, guide) and load that branch's expectations
3. Investigate the actual codebase state — check claims against code, config, and API signatures
4. Run Layer 1 (content quality against type-specific standards)
5. Run Layer 2 (mechanical health checks)
6. Present findings in the structured report format below
7. Ask: "Want me to fix these, or just flag them?"

## Two-Layer Review

### Layer 1: Content Quality
Requires the doc-type branch to know what "good" looks like.

**Check against doc-type standards:**
- Does the doc have the right sections for its type? (README checklist, ADR structure, Diataxis quadrant rules)
- Is the information accurate against the current codebase?
- Is the audience clear and consistently addressed?
- Are concepts explained at the right level of detail?
- Are code examples correct, current, and runnable?
- Does the structure follow the conventions for this doc type?
- **REQUIRED:** Apply `writing-clearly-and-concisely` for prose quality assessment

### Layer 2: Mechanical Health
Universal checks that apply to all documentation types.

| Check | What to Look For |
|-------|-----------------|
| **Broken links** | Internal cross-references, external URLs, anchor links that point nowhere |
| **Freshness** | "Last reviewed" dates older than 6 months, git blame showing sections untouched for over a year, references to deprecated features or old API versions |
| **Terminology consistency** | Same concept called different names in different places (e.g., "user" vs "customer" vs "account holder"). Build a term list and check for deviations. |
| **Formatting consistency** | Mixed header levels, inconsistent code fence languages, mixed list styles (bullets vs numbers), misaligned tables |
| **Orphaned references** | Links to docs or sections that no longer exist, references to removed features or old config options |
| **Missing alt text** | Images without descriptive alt text for accessibility |
| **Code example drift** | Examples that reference old API signatures, deprecated flags, removed config options, or outdated dependency versions |
| **Readability** | Excessively long sentences (>25 words), heavy passive voice, jargon without definition, walls of text without structure |
| **Completeness gaps** | Sections that say "TODO", "TBD", or "Coming soon"; empty placeholder sections; features documented in code but missing from docs |
| **Accessibility** | Semantic markdown (proper heading hierarchy, not using bold-as-headers), meaningful link text (not "click here"), sufficient contrast in diagrams |
| **Heading hierarchy** | Skipped heading levels (h1 → h3), multiple h1 tags, headings that don't describe content |
| **File organization** | Docs in wrong folders, naming convention violations, missing index files |

## Review Output Format
Present findings as a structured report:

```markdown
## Doc Review: [filename]

### Summary
[1-2 sentence overall assessment — current state and biggest opportunity]

### Content Issues
- **[severity]** [issue]: [location] — [suggestion]
- **[severity]** [issue]: [location] — [suggestion]

### Mechanical Issues
- **[category]** [location] — [details]
- **[category]** [location] — [details]

### What's Working Well
- [positive observation — reinforce good patterns]
- [positive observation]

### Recommended Actions
1. [highest priority fix]
2. [next priority]
3. [lower priority]
```

Severity levels: **Critical** (blocks understanding), **Important** (degrades quality), **Minor** (polish)

Always include "What's Working Well" — review should reinforce good patterns, not just flag problems.

### Bulk Review
When reviewing multiple docs across a project:
1. Start with the README (entry point)
2. Follow links outward to referenced docs
3. Check for cross-reference consistency
4. Build a terminology list and check for deviations
5. Note patterns (if the same issue appears in multiple docs, flag the pattern not each instance)
6. Summarize with a project-level health assessment
