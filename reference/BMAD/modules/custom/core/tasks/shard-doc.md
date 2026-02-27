---
name: shard-doc
description: "Split a large markdown document into smaller files organized by level-2 sections."
standalone: true
---

# Task: Shard Document

## Objective
Split a large markdown file into a sharded folder structure using `npx @kayvan/markdown-tree-parser`.

## Critical Context
- Preferred tool: `npx @kayvan/markdown-tree-parser explode`.
- Default sharding boundary: level 2 headings (`##`).

## Mandatory Execution Rules
- Execute all steps in order.
- Halt immediately on any listed halt condition.
- Confirm paths and permissions before sharding.
- Report completion details and handle source-file disposition.

## Inputs
- `source_document` (required): absolute or relative path to `.md` file.
- `destination_folder` (optional): where shard output should be written.

## Flow
### 1. Get Source Document
- Ask for source path if not provided.
- Verify file exists and has `.md` extension.
- Halt with clear error if invalid.

### 2. Get Destination Folder
- Suggest default: sibling folder named after source without `.md`.
- Example: `/path/architecture.md` -> `/path/architecture/`.
- Ask user to accept default (`y`) or provide custom path.
- Verify destination exists or can be created.
- Verify write permission.
- Halt on permission failures.

### 3. Execute Sharding
- Announce sharding start.
- Run:
- `npx @kayvan/markdown-tree-parser explode [source-document] [destination-folder]`
- Capture stdout/stderr.
- Halt and report if command fails.

### 4. Verify Output
- Confirm destination contains generated files.
- Confirm `index.md` exists.
- Count files created.
- Halt if no output files were produced.

### 5. Report Completion
- Report:
- Source path.
- Destination path.
- Number of files created.
- `index.md` presence.
- Any warnings/tool output.

### 6. Handle Original Document
- Explain that keeping both original and shards can cause confusion.
- Ask:
- `[d]` Delete original (recommended)
- `[m]` Move original to archive
- `[k]` Keep original (not recommended)

#### If `d` (delete)
- Delete source file.
- Confirm deletion path.

#### If `m` (move)
- Suggest default archive path: sibling `archive/` folder.
- Accept default or custom archive path.
- Create archive folder if needed.
- Move source file and confirm destination.

#### If `k` (keep)
- Warn about duplicate-source confusion.
- Confirm original path remains unchanged.

## Halt Conditions
- Source file missing or not markdown.
- Sharding command fails.
- Output folder has no generated files.
