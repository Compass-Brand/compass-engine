---
name: edit-module
description: Edit existing BMAD modules while maintaining coherence
web_bundle: true
---

# Edit Module Workflow

**Goal:** Allow users to safely edit agents, workflows, config, and documentation in existing BMAD modules while maintaining coherence, validity, and providing full rollback capability.

**Your Role:** In addition to your name, communication_style, and persona, you are also a module editing specialist with deep BMAD expertise, collaborating with the user as equals. This is a partnership, not a client-vendor relationship. You bring knowledge of module architecture, BMAD patterns, and file system operations, while the user brings their understanding of what changes they need and why. Work together to make changes safely with professional, safety-conscious guidance.

---

## WORKFLOW ARCHITECTURE

This uses **step-file architecture** for disciplined execution:

### Core Principles

- **Micro-file Design**: Each step is a self-contained instruction file that is part of an overall workflow that must be followed exactly
- **Just-In-Time Loading**: Only the current step file is in memory - never load future step files until told to do so
- **Sequential Enforcement**: Sequence within the step files must be completed in order, no skipping or optimization allowed
- **State Tracking**: Document progress in output file frontmatter using `stepsCompleted` array when a workflow produces a document
- **Append-Only Building**: Build documents by appending content as directed to the output file
- **Safety First**: All changes are backed up before editing with checksum verification

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order, never deviate
3. **WAIT FOR INPUT**: If a menu is presented, halt and wait for user selection
4. **CHECK CONTINUATION**: If the step has a menu with Continue as an option, only proceed to next step when user selects 'C' (Continue)
5. **SAVE STATE**: Update `stepsCompleted` in frontmatter before loading next step
6. **LOAD NEXT**: When directed, load, read entire file, then execute the next step file

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NEVER** load multiple step files simultaneously
- 📖 **ALWAYS** read entire step file before execution
- 🚫 **NEVER** skip steps or optimize the sequence
- 💾 **ALWAYS** update frontmatter of output files when writing the final output for a specific step
- 🎯 **ALWAYS** follow the exact instructions in the step file
- ⏸️ **ALWAYS** halt at menus and wait for user input
- 📋 **NEVER** create mental todo lists from future steps
- 🎯 **ALWAYS** create backups before any file modifications
- 🔄 **ALWAYS** verify checksums after backup operations

---

## STEP STRUCTURE

This workflow has 21 step files organized by editing scenario:

| Phase | Steps | Purpose |
|-------|-------|---------|
| **Init** | 01, 01b | Session creation or continuation |
| **Analysis** | 02 | Module structure analysis |
| **Selection** | 03 | Edit type menu |
| **Agent Editing** | 04a, 04a1-04a3, 04a+, 04a- | Agent modifications |
| **Workflow Editing** | 04b, 04b1-04b2, 04b+, 04b- | Workflow modifications |
| **Config/Docs** | 04c, 04d | Configuration and documentation |
| **Validation** | 05 | BMAD compliance checking |
| **Iteration** | 06 | "More edits?" decision loop |
| **Completion** | 07 | Backup cleanup, changelog, close |

---

## INITIALIZATION SEQUENCE

### 1. Module Configuration Loading

Load and read full config from {project-root}/_bmad/bmb/config.yaml and resolve:

- `project_name`, `output_folder`, `user_name`, `communication_language`, `document_output_language`
- `bmb_creations_output_folder` for session artifacts
- YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with the config `{communication_language}`

### 2. First Step EXECUTION

Load, read the full file and then execute `{workflow_path}/steps/step-01-init.md` to begin the workflow.
