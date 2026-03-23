---
name: index-docs
description: "Generates or updates an index.md to reference all docs in the folder. Use when the user asks to create or update an index for a folder."
standalone: true
---

# Task: Index Docs

## Objective
Create or update an `index.md` file for a target folder so humans and LLMs can quickly discover content.

## Mandatory Execution Rules
- Execute steps in exact order.
- Do not skip validation checks.
- Halt on any listed halt condition.
- Read files to derive descriptions from content, not filenames.

## Inputs
- `target_directory` (required): folder to index.

## Flow
### 1. Scan Directory
- List all files and subdirectories in the target directory.
- Ignore hidden files (starting with `.`) unless explicitly requested.

### 2. Group Content
- Organize entries into:
- Top-level files.
- Subdirectories with nested files.

### 3. Generate Descriptions
- Read each included file.
- Produce a brief description (3-10 words) that reflects actual content.

### 4. Create or Update `index.md`
- Write an organized index in markdown with relative paths (`./...`).
- Sort entries alphabetically inside each section.

## Output Format
```markdown
# Directory Index

## Files

- **[filename.ext](./filename.ext)** - Brief description
- **[another-file.ext](./another-file.ext)** - Brief description

## Subdirectories

### subfolder/

- **[file1.ext](./subfolder/file1.ext)** - Brief description
- **[file2.ext](./subfolder/file2.ext)** - Brief description
```

## Halt Conditions
- Target directory does not exist or is inaccessible.
- No write permission to create or update `index.md`.

## Validation Checklist
- Uses relative links starting with `./`.
- Groups similar files together.
- Descriptions are concise and content-based.
- Alphabetical sorting applied within each group.
