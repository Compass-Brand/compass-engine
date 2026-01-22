# BMAD Automation Specification Archive

**Archived:** 2026-01-13
**Reason:** Pivot from Python implementation to native BMAD implementation

## What This Is

This directory contains Python code that was built to implement BMAD automation. However, this approach was incorrect - the automation should be implemented directly in BMAD's native structure (agent files, workflow configs, tasks) rather than as external Python code.

## Contents

- `bmad_automation/` - Python modules implementing automation logic
- `tests_bmad_automation/` - Test suites for the Python modules

## How To Use This

This code serves as **detailed specification/pseudocode** documenting:
- Class structures and relationships
- Test cases showing expected behavior
- Implementation patterns and edge cases

When implementing automation natively in BMAD, reference these files to understand:
- The logic for menu detection and selection
- Tier-based behavior configurations
- Confidence scoring algorithms
- Batch processing logic
- Timeout and recovery patterns

## The Correct Approach

See `docs/plans/2026-01-13-bmad-automation-pivot.md` for how automation should be implemented directly in BMAD's:
- Config files (YAML)
- Agent files (XML in markdown)
- Workflow configs (YAML)
- Tasks (YAML)

## Stories Implemented Here

These stories were implemented as Python code (now archived):
- 2b-1: Menu Detection
- 2b-2: Automatic Menu Selection
- 2b-3: BMB-Specific Menu Thresholds
- 2b-4: Nested Menu Handling
- 2b-5: Menu History Tracking
- 2b-6: Batch-Continue Logic
- 2b-7: Human Checkpoint Presentation
- 2b-8: Validation Failure Recovery
- 2b-9: Timeout Enforcement
- 4-1: Writing Workflow Decisions to Memory
- 4-2: Post-Workflow Learning Extraction
- 4-3: Graceful Degradation When Memory Unavailable

The concepts from these stories need to be re-implemented natively in BMAD.
