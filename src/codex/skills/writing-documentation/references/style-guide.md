# Documentation Style Guide

Common documentation mistakes and how to avoid them. Applies across all doc types.

## Common Mistakes

| Mistake                     | Why It's Bad                                                             | Fix                                                                              |
| --------------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| No install steps            | Never assume setup is obvious. Even "obvious" steps prevent confusion.   | Always include explicit setup instructions with exact commands.                  |
| No examples                 | Abstract descriptions don't stick. Readers learn from concrete examples. | Show, don't tell. Include copy-pasteable code for every feature.                 |
| Wall of text                | Dense paragraphs get skimmed or skipped entirely.                        | Use headers, tables, lists, diagrams. Break content into scannable chunks.       |
| Stale content               | Wrong docs are worse than no docs — they actively mislead.               | Add "last reviewed" dates. Set up CI link checking. Review quarterly.            |
| Generic tone                | "The user should..." is impersonal and vague.                            | Write for YOUR specific audience. Use "you" for the reader.                      |
| Jargon without definition   | Readers outside your team won't know your acronyms.                      | Define terms on first use, or maintain a glossary.                               |
| "Click here" links          | Screen readers announce "click here" with no context.                    | Use descriptive link text: "see the installation guide" not "click here".        |
| Bold as headers             | Using **bold text** instead of proper ## headers breaks navigation.      | Use semantic heading hierarchy (h1 → h2 → h3).                                   |
| Multiple h1 tags            | Confuses document structure and screen readers.                          | One h1 per document (the title). Use h2+ for sections.                           |
| Skipped heading levels      | h1 → h3 (skipping h2) breaks hierarchy.                                  | Maintain sequential heading levels.                                              |
| Mixed formatting            | Inconsistent code fences, list styles, or table formats.                 | Pick conventions and stick to them throughout.                                   |
| Missing code fence language | Unlabeled code blocks don't get syntax highlighting.                     | Always specify the language: `python, `bash, ```json, etc.                       |
| Outdated screenshots        | Screenshots from old UI versions confuse readers.                        | Use text descriptions where possible. When screenshots are necessary, date them. |
| Assuming knowledge          | "Obviously, you'll need to configure the reverse proxy."                 | State prerequisites explicitly. What's obvious to you isn't obvious to everyone. |

## Prose Quality

For deeper writing guidance — clear prose, active voice, conciseness, and AI writing patterns to avoid — use the `writing-clearly-and-concisely` skill.

## Formatting Conventions

- **Headings:** Sentence case ("Getting started" not "Getting Started"), except proper nouns
- **Code:** Use fenced code blocks with language identifiers. Inline `code` for file names, commands, and variable names.
- **Lists:** Use bullets for unordered items, numbers only when order matters
- **Tables:** Use for structured data with 3+ attributes. Keep tables under 10 rows; link to full reference for more.
- **Links:** Descriptive text, relative paths for internal links, full URLs for external
- **Images:** Always include alt text. Use SVG for diagrams, PNG for screenshots.
- **File names in text:** Use `inline code` formatting for paths and file names
