---
workflowName: edit-module
creationDate: 2026-01-07
module: bmb
status: COMPLETE
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9]
specificationRounds: 5
issuesResolved: 71
totalFiles: 26
buildAgents: 7
---

# Workflow Creation Summary: edit-module

## Workflow Information

| Field | Value |
|-------|-------|
| **Name** | edit-module |
| **Description** | Edit existing BMAD modules while maintaining coherence |
| **Module** | BMB (BMAD Module Builder) |
| **Created** | 2026-01-07 |
| **Location** | `_bmad-output/bmb-creations/workflows/edit-module/` |

## Creation Process

| Phase | Details |
|-------|---------|
| Specification | 5 adversarial review rounds, 71 issues resolved |
| Build | 7 parallel subagents across 4 phases |
| Review | 8-point validation, all checks passed |

## Generated Files (26 total)

### Entry Point
- `workflow.md` - Main workflow entry with step-file architecture

### Step Files (20)
| File | Purpose |
|------|---------|
| `step-01-init.md` | Module selection, session creation, pre-flight checks |
| `step-01b-continue.md` | Resume interrupted session |
| `step-02-analyze.md` | Deep module structure analysis |
| `step-03-select.md` | Edit type menu with routing |
| `step-04a-agent-load.md` | Load agent, detect type (Simple/Expert/Module) |
| `step-04a1-agent-simple.md` | Edit simple markdown agents |
| `step-04a2-agent-expert.md` | Edit expert agents with YAML frontmatter |
| `step-04a3-agent-module.md` | Edit complex XML/structured agents |
| `step-04a-agent-add.md` | Add new agent to module |
| `step-04a-agent-remove.md` | Remove agent (DESTRUCTIVE - HIGH severity) |
| `step-04b-workflow-load.md` | Load workflow, detect type |
| `step-04b1-workflow-standalone.md` | Edit standalone step-file workflows |
| `step-04b2-workflow-legacy.md` | Edit legacy workflows with migration option |
| `step-04b-workflow-add.md` | Add new workflow to module |
| `step-04b-workflow-remove.md` | Remove workflow (CRITICAL severity) |
| `step-04c-config.md` | Edit module.yaml configuration |
| `step-04d-docs.md` | Edit module documentation |
| `step-05-validate.md` | Syntax + BMAD compliance validation |
| `step-06-iterate.md` | "More edits?" decision loop |
| `step-07-complete.md` | Backup cleanup, changelog, session close |

### Templates (3)
- `templates/edit-session-template.md` - Session document template
- `templates/changelog-entry-template.md` - Keep-a-Changelog format
- `templates/backup-manifest-template.json` - Backup manifest structure

### Data Files (2)
- `data/validation-rules.md` - BMAD compliance rules (AGT-*, WFL-*, MOD-*)
- `data/backup-manifest-schema.json` - JSON Schema for manifest validation

## Quick Start Guide

### Running the Workflow

**Option 1: Via Module Builder Agent**
```
/bmad:bmb:agents:module-builder
```
Then select `[EM] Edit Module` from the menu.

**Option 2: Direct Invocation (after integration)**
```
/bmad:bmb:workflows:edit-module
```

### What to Expect

1. **Module Selection** - Choose which BMAD module to edit
2. **Pre-flight Checks** - Git status, module validation
3. **Structure Analysis** - Deep scan of agents, workflows, config, docs
4. **Edit Menu** - Select what to edit (agents, workflows, config, docs)
5. **Guided Editing** - Type-specific editing with safety protocols
6. **Validation** - BMAD compliance checking
7. **Iteration** - Make more edits or complete
8. **Finalization** - Backup cleanup, changelog, optional git commit

### Key Features

- **Session Continuation** - Resume interrupted editing sessions
- **Automatic Backups** - Every change backed up with checksums
- **Type Detection** - Agents/workflows routed to appropriate editors
- **Destructive Safeguards** - Removal requires typed confirmation
- **BMAD Validation** - 20+ compliance rules checked
- **Git Integration** - Optional commit with auto-generated message

## Next Steps

1. **Validate with Compliance Check**
   - Start new Claude conversation
   - Run: `/bmad:bmb:workflows:workflow-compliance-check`
   - Provide path: `_bmad-output/bmb-creations/workflows/edit-module/workflow.md`

2. **Integrate with BMB**
   - Add menu entry to `_bmad/bmb/agents/module-builder.md`
   - Copy workflow to `_bmad/bmb/workflows/edit-module/`

3. **Test with Sample Module**
   - Run workflow against a test module
   - Verify all editing paths work correctly

## Support

- **Specification Document**: `workflow-plan-edit-module.md`
- **Quality Testing Spec**: `quality-testing-specification.md`

---

*Workflow creation completed: 2026-01-07*
