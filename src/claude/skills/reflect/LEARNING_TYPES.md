# Learning Types Reference

This document provides detailed guidance on identifying, classifying, and storing different types of learnings.

## Overview

| Type         | Tag            | Default Importance | Description                                         |
| ------------ | -------------- | ------------------ | --------------------------------------------------- |
| Correction   | `correction`   | 9                  | User explicitly corrected output or behavior        |
| Preference   | `preference`   | 8                  | User expressed how they prefer things done          |
| Pattern      | `pattern`      | 7                  | Successful approach that worked well                |
| Edge Case    | `edge-case`    | 7                  | Scenario requiring special handling                 |
| Anti-pattern | `anti-pattern` | 9                  | Something that caused problems or should be avoided |

---

## Correction

**Description:** User explicitly corrected Claude's output, approach, or understanding.

**Importance Range:** 8-10 (default 9)

- 10: Critical correction affecting safety, data integrity, or core functionality
- 9: Standard correction of behavior or output
- 8: Minor correction or clarification

### Detection Signals

**HIGH confidence (create immediately):**

- User said "no", "wrong", "incorrect", "that's not right"
- User said "I meant...", "what I wanted was..."
- User provided explicit correction after output
- User expressed frustration: "why did you...", "stop doing..."
- User requested immediate changes to generated content

**MEDIUM confidence (verify context):**

- User made modifications to output without explicit correction
- User asked clarifying questions implying misunderstanding

### Memory Template

Note: The following is a usage template showing how to invoke the MCP tool, not executable Python code. Replace placeholder values with actual data.

```python
# MCP tool invocation template (replace <placeholders> with actual values)
mcp__forgetful__execute_forgetful_tool("create_memory", {
  "title": "[CORRECTION] Brief description of what was corrected",
  "content": """What happened: <describe the incorrect behavior>

What the user wanted: <describe the correct behavior>

How to avoid: <specific guidance for future>

Context: <when/where this applies>""",
  "context": "Captured correction during [task/skill] - prevents repeating this mistake",
  "keywords": ["correction", "<topic>", "<skill-name>"],
  "tags": ["skill-learning", "correction", "<skill-name>"],
  "importance": 9,
  "project_ids": [<if project-specific>]
})
```

### Examples

**Example 1: Code style correction**

```text
User: "No, don't use arrow functions for React components. Use function declarations."
```

Memory:

- Title: `[CORRECTION] Use function declarations for React components, not arrow functions`
- Tags: `["skill-learning", "correction", "code-generation", "react"]`

**Example 2: Output format correction**

```text
User: "I wanted the summary in bullet points, not paragraphs."
```

Memory:

- Title: `[CORRECTION] User prefers bullet points over paragraphs for summaries`
- Tags: `["skill-learning", "correction", "formatting"]`

---

## Preference

**Description:** User expressed how they prefer things done, without necessarily correcting an error.

**Importance Range:** 7-9 (default 8)

- 9: Strong, explicit preference stated as a rule
- 8: Clear preference with reasoning
- 7: Implied preference from choices

### Detection Signals

**HIGH confidence:**

- User said "I prefer...", "I like...", "always use..."
- User said "my convention is...", "our standard is..."
- User explicitly stated a rule or guideline

**MEDIUM confidence:**

- User consistently chose one approach over alternatives
- User praised a specific aspect of the output
- User said "perfect", "exactly", "that's what I wanted"

### Memory Template

```python
mcp__forgetful__execute_forgetful_tool("create_memory", {
  "title": "[PREFERENCE] Brief description of preference",
  "content": """Preference: <what the user prefers>

Reasoning: <why, if provided>

Applies to: <scope - personal/project/skill>

Examples:
- <specific example 1>
- <specific example 2>""",
  "context": "User preference expressed during [task/skill]",
  "keywords": ["preference", "<topic>", "<skill-name>"],
  "tags": ["skill-learning", "preference", "<skill-name>"],
  "importance": 8,
  "project_ids": [<if project-specific>]
})
```

### Examples

**Example 1: Naming convention preference**

```text
User: "I prefer snake_case for Python variables, camelCase for JavaScript."
```

Memory:

- Title: `[PREFERENCE] Use snake_case for Python, camelCase for JavaScript`
- Tags: `["skill-learning", "preference", "naming-conventions"]`

**Example 2: Communication preference**

```text
User: "I like when you explain your reasoning before showing code."
```

Memory:

- Title: `[PREFERENCE] Explain reasoning before showing code`
- Tags: `["skill-learning", "preference", "communication"]`

---

## Pattern

**Description:** A successful approach, technique, or solution that worked well.

**Importance Range:** 6-8 (default 7)

- 8: Pattern that solved a complex problem elegantly
- 7: Standard successful approach
- 6: Minor technique that helped

### Detection Signals

**HIGH confidence:**

- User said "this worked well", "great approach", "keep doing this"
- User explicitly asked to remember the approach
- Solution was accepted and built upon

**MEDIUM confidence:**

- User proceeded without modification
- No complaints or corrections followed
- User asked follow-up questions building on the solution

### Memory Template

```python
mcp__forgetful__execute_forgetful_tool("create_memory", {
  "title": "[PATTERN] Brief description of successful pattern",
  "content": """Pattern: <describe the approach>

When to use: <situations where this applies>

Benefits: <why this worked well>

Implementation:
<code or steps if applicable>

Related patterns: <similar approaches>""",
  "context": "Successful pattern discovered during [task/skill]",
  "keywords": ["pattern", "<topic>", "<skill-name>"],
  "tags": ["skill-learning", "pattern", "<skill-name>"],
  "importance": 7,
  "project_ids": [<if project-specific>]
})
```

### Examples

**Example 1: Debugging pattern**

```text
User: "That binary search approach to finding the bug was really effective."
```

Memory:

- Title: `[PATTERN] Use binary search (git bisect style) to isolate bugs`
- Tags: `["skill-learning", "pattern", "debugging"]`

**Example 2: Communication pattern**

```text
User: "I like how you broke that down into phases. Do that more often."
```

Memory:

- Title: `[PATTERN] Break complex tasks into phases for clarity`
- Tags: `["skill-learning", "pattern", "communication"]`

---

## Edge Case

**Description:** A scenario that required special handling or wasn't covered by the standard approach.

**Importance Range:** 6-8 (default 7)

- 8: Edge case that could cause significant problems if missed
- 7: Notable edge case requiring workaround
- 6: Minor edge case for awareness

### Detection Signals

**HIGH confidence:**

- Standard approach failed and needed modification
- User pointed out a scenario not initially considered
- Workaround was required

**MEDIUM confidence:**

- Questions arose that the approach didn't anticipate
- Additional conditions needed to be added
- User asked "what about when..."

### Memory Template

```python
mcp__forgetful__execute_forgetful_tool("create_memory", {
  "title": "[EDGE CASE] Brief description of edge case",
  "content": """Scenario: <describe the edge case>

Why it's special: <what makes this different>

Standard approach fails because: <why>

Correct handling:
<how to handle this case>

How to detect: <signals that indicate this edge case>""",
  "context": "Edge case discovered during [task/skill]",
  "keywords": ["edge-case", "<topic>", "<skill-name>"],
  "tags": ["skill-learning", "edge-case", "<skill-name>"],
  "importance": 7,
  "project_ids": [<if project-specific>]
})
```

### Examples

**Example 1: Data edge case**

```text
User: "What about when the date field is null? The parser breaks."
```

Memory:

- Title: `[EDGE CASE] Handle null date fields in parser`
- Tags: `["skill-learning", "edge-case", "data-parsing"]`

**Example 2: Environment edge case**

```text
User: "This doesn't work on Windows because of path separators."
```

Memory:

- Title: `[EDGE CASE] Use path.join for cross-platform compatibility`
- Tags: `["skill-learning", "edge-case", "cross-platform"]`

---

## Anti-pattern

**Description:** An approach that caused problems or should be avoided.

**Importance Range:** 8-10 (default 9)

- 10: Anti-pattern that could cause data loss, security issues, or major problems
- 9: Standard anti-pattern causing significant issues
- 8: Minor anti-pattern to avoid

### Detection Signals

**HIGH confidence:**

- User said "never do this", "don't ever...", "this caused problems"
- Approach caused errors, bugs, or failures
- User expressed strong negative reaction

**MEDIUM confidence:**

- Approach was rejected in favor of alternative
- User warned about potential issues
- Similar approach failed before

### Memory Template

```python
mcp__forgetful__execute_forgetful_tool("create_memory", {
  "title": "[ANTI-PATTERN] Brief description of what to avoid",
  "content": """Anti-pattern: <what NOT to do>

Why it's problematic: <what goes wrong>

What to do instead: <the correct approach>

Warning signs: <how to detect if about to make this mistake>

Severity: <HIGH/MEDIUM/LOW>""",
  "context": "Anti-pattern identified during [task/skill] - critical to avoid",
  "keywords": ["anti-pattern", "<topic>", "<skill-name>"],
  "tags": ["skill-learning", "anti-pattern", "<skill-name>"],
  "importance": 9,
  "project_ids": [<if project-specific>]
})
```

### Examples

**Example 1: Security anti-pattern**

```text
User: "Never commit API keys to the repository, even in .env files."
```

Memory:

- Title: `[ANTI-PATTERN] Never commit API keys or secrets to repositories`
- Tags: `["skill-learning", "anti-pattern", "security"]`
- Importance: 10

**Example 2: Performance anti-pattern**

```text
User: "Don't use N+1 queries in loops. Always batch database calls."
```

Memory:

- Title: `[ANTI-PATTERN] Avoid N+1 database queries - use batch operations`
- Tags: `["skill-learning", "anti-pattern", "database", "performance"]`

---

## Classification Decision Tree

```text
Is this about something that went WRONG?
├── YES: Was it explicitly corrected?
│   ├── YES → CORRECTION
│   └── NO: Should this be avoided in future?
│       ├── YES → ANTI-PATTERN
│       └── NO → EDGE CASE (special handling needed)
└── NO: Is this about something that went RIGHT?
    ├── YES: Was it about HOW the user wants things done?
    │   ├── YES → PREFERENCE
    │   └── NO → PATTERN
    └── NO: Was this an unexpected scenario?
        └── YES → EDGE CASE
```

## Importance Scoring Guide

| Score | Criteria                                              |
| ----- | ----------------------------------------------------- |
| 10    | Critical: affects safety, security, or data integrity |
| 9     | High: explicit correction or serious anti-pattern     |
| 8     | Standard: clear preference or notable pattern         |
| 7     | Useful: helpful pattern or edge case                  |
| 6     | Minor: good to know but not critical                  |

**Factors that increase importance:**

- Explicit statement by user
- High confidence detection
- Wide applicability (affects many situations)
- Severity of consequences if ignored
- Repeated occurrence

**Factors that decrease importance:**

- Implied rather than explicit
- Narrow applicability
- Minor consequences
- One-time occurrence
