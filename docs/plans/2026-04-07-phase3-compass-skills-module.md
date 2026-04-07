# Phase 3: Create compass-skills Module Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Convert all Compass-only content to upstream skill format, create the `compass-skills` and `bmad-builder-skills` modules, convert upstream workflow overrides to `custom/bmm-skills/`, then remove all old-format directories and the compat shim.

**Architecture:** Each workflow/agent gets a skill directory with a `SKILL.md` entry point. Compass-only content goes to `custom/compass-skills/`, upstream overrides go to `custom/bmm-skills/`, and bmad-builder goes to `custom/bmad-builder-skills/`. The build merges native + custom (custom wins). After all new directories exist, old-format directories and the compat shim are removed.

**Tech Stack:** Node.js (ESM), Markdown (SKILL.md), YAML (bmad-skill-manifest.yaml, workflow.yaml)

---

## Conventions Used Throughout This Plan

### Workflow SKILL.md Template

Every workflow skill directory gets a `SKILL.md` with this pattern:

```markdown
---
name: bmad-compass-{skill-name}
description: '{One-line description}. Use when the user says "{trigger phrase}"'
---

Follow the instructions in ./workflow.md.
```

If the workflow uses `workflow.yaml` instead of `workflow.md`, the SKILL.md body is:

```markdown
Follow the instructions in ./workflow.yaml.
```

The frontmatter `name` field MUST match the directory name exactly.

### Agent SKILL.md Template

Same as Phase 2 upstream agents. Contains frontmatter, persona sections (Identity, Communication Style, Principles), Capabilities table, and On Activation flow. See native examples in `src/bmad/modules/native/bmm-skills/*/bmad-agent-*/SKILL.md`.

### Agent bmad-skill-manifest.yaml Template

```yaml
type: agent
name: bmad-agent-{name}
displayName: {PersonaName}
title: {Title}
icon: "{emoji}"
capabilities: "{comma-separated list}"
role: {Role description}
identity: "{Identity text}"
communicationStyle: "{Style text}"
principles: "{Principles text}"
module: compass
```

### Naming Convention

| Content Type | Naming Pattern | Example |
|-------------|---------------|---------|
| Compass agent | `bmad-agent-{name}/` | `bmad-agent-wds-designer/` |
| Compass workflow | `bmad-compass-{name}/` | `bmad-compass-threat-modeling/` |
| Upstream override | Same name as native | `bmad-dev-story/` |

### File Move Convention

When moving workflow files from old to new directory:
1. Create the new skill directory
2. Copy all existing files (workflow.md, workflow.yaml, steps/, checklist.md, instructions.md/xml, templates/, data/) into it
3. Create SKILL.md entry point
4. Do NOT rename .yaml to .md — keep existing file names

---

## Task 1: Create compass-skills Module Scaffold

**Files:**
- Create: `src/bmad/modules/custom/compass-skills/module.yaml`
- Create: `src/bmad/modules/custom/compass-skills/module-help.csv`
- Create phase directories (empty, populated in later tasks)

**Step 1: Create module.yaml**

Create `src/bmad/modules/custom/compass-skills/module.yaml`:

```yaml
name: compass
displayName: Compass Skills
description: Compass Brand custom agents, workflows, and utilities
version: "1.0.0"
type: module
```

**Step 2: Create module-help.csv**

Create `src/bmad/modules/custom/compass-skills/module-help.csv` with just the header:

```csv
module,skill,display-name,menu-code,description,action,args,phase,after,before,required,output-location,outputs
```

(Rows will be added as skills are created in later tasks. Phase 4 will auto-generate this.)

**Step 3: Create phase directories**

```bash
mkdir -p src/bmad/modules/custom/compass-skills/{0-governance,1-analysis,2-plan-workflows,3-solutioning,4-implementation,anytime,documentation,planning}
```

**Step 4: Verify build**

Run: `node tools/build.js`

Expected: Build passes. `dist/_bmad/compass/` now exists with module.yaml and module-help.csv.

**Step 5: Commit**

```bash
git add src/bmad/modules/custom/compass-skills/
git commit -m "feat(bmad): scaffold compass-skills module with phase directories"
```

---

## Task 2: Convert 8 Compass-Only Agents to Skill Format

**Files:**
- Create: 8 agent directories, each with `SKILL.md` + `bmad-skill-manifest.yaml`

**Context:** These 8 agents are Compass-only (no upstream equivalent). They go to `custom/compass-skills/` in phase directories matching where they logically belong.

### Agent Directory Mapping

| Old Path | New Path | Display Name | Phase |
|----------|----------|-------------|-------|
| `agents/creative-problem-solver.agent.yaml` | `compass-skills/anytime/bmad-agent-creative-problem-solver/` | Dr. Quinn | anytime |
| `agents/design-thinking-coach.agent.yaml` | `compass-skills/1-analysis/bmad-agent-design-thinking-coach/` | Maya | 1-analysis |
| `agents/innovation-strategist.agent.yaml` | `compass-skills/1-analysis/bmad-agent-innovation-strategist/` | Victor | 1-analysis |
| `agents/wds-analyst.agent.yaml` | `compass-skills/1-analysis/bmad-agent-wds-analyst/` | Saga | 1-analysis |
| `agents/wds-designer.agent.yaml` | `compass-skills/2-plan-workflows/bmad-agent-wds-designer/` | Freya | 2-plan-workflows |
| `agents/security-architect.agent.yaml` | `compass-skills/3-solutioning/bmad-agent-security-architect/` | Bastion | 3-solutioning |
| `agents/threat-analyst.agent.yaml` | `compass-skills/3-solutioning/bmad-agent-threat-analyst/` | Cipher | 3-solutioning |
| `agents/tea.agent.yaml` | `compass-skills/4-implementation/bmad-agent-tea/` | Murat | 4-implementation |

**Step 1: For each agent, create SKILL.md and bmad-skill-manifest.yaml**

Read each `.agent.yaml` file from `src/bmad/modules/custom/bmm/agents/` and convert to skill format:

1. Read the `.agent.yaml` to extract persona data (metadata, persona, menu, critical_actions, prompts)
2. Read the corresponding `.md` documentation file for additional context
3. Create `SKILL.md` following the agent template — includes frontmatter, persona sections, capabilities table (from menu items), and On Activation flow
4. Create `bmad-skill-manifest.yaml` with persona metadata

**For agents with menu items:** The Capabilities table should reference skill names using `bmad-compass-{workflow-name}` for Compass workflows. These skills may not exist yet (forward declarations — created in Tasks 3-7).

**For agents with critical_actions:** Include a "## Critical Actions" section in SKILL.md (see native `bmad-agent-dev` and `bmad-agent-qa` for format).

**For agents with prompts (e.g., QA welcome prompt):** Include the prompt content as a section in SKILL.md or as a sidecar .md file if large.

**Step 2: Run validation**

Run: `node tools/validate.js`

Expected: PASS — `validateSkillFormat()` now covers custom/bmm-skills but not compass-skills yet. Add compass-skills to moduleRoots:

In `tools/validate.js`, update `validateSkillFormat()` moduleRoots to also include:
```javascript
path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'compass-skills'),
```

**Step 3: Run build and verify**

Run: `node tools/build.js`

Verify agents appear in dist: `ls dist/_bmad/compass/1-analysis/`

**Step 4: Commit**

```bash
git add src/bmad/modules/custom/compass-skills/ tools/validate.js
git commit -m "feat(bmad): convert 8 Compass-only agents to skill format in compass-skills"
```

---

## Task 3: Convert Compass-Only Workflows — Governance + Documentation + Planning

**Files:**
- Create: 11 workflow skill directories in `compass-skills/`

### Workflow Mapping

| Old Path | New Skill Directory | Description |
|----------|-------------------|-------------|
| `workflows/0-governance/phase-sync/` | `0-governance/bmad-compass-phase-sync/` | Cross-phase synchronization checkpoint |
| `workflows/0-governance/phase-closeout/` | `0-governance/bmad-compass-phase-closeout/` | Phase completion and handoff |
| `workflows/0-governance/oversight-checkpoint/` | `0-governance/bmad-compass-oversight-checkpoint/` | Oversight substrate evaluation |
| `workflows/documentation/init-docs/` | `documentation/bmad-compass-init-docs/` | Initialize Compass docs layout |
| `workflows/documentation/update-docs/` | `documentation/bmad-compass-update-docs/` | Incremental documentation updates |
| `workflows/documentation/validate-docs/` | `documentation/bmad-compass-validate-docs/` | Docs structure/policy compliance |
| `workflows/planning/init-planning/` | `planning/bmad-compass-init-planning/` | Initialize planning structure |
| `workflows/planning/workspace-bootstrap/` | `planning/bmad-compass-workspace-bootstrap/` | Bootstrap new workspace |
| `workflows/planning/project-roadmap/` | `planning/bmad-compass-project-roadmap/` | Create project roadmap |
| `workflows/planning/sync-repositories/` | `planning/bmad-compass-sync-repositories/` | Sync multi-repo projects |
| `workflows/planning/initiative-routing/` | `planning/bmad-compass-initiative-routing/` | Route initiatives to correct workflow |

**Step 1: For each workflow, create skill directory**

For each entry in the table:
1. Create the target directory under `src/bmad/modules/custom/compass-skills/`
2. Copy all files from the old workflow directory into the new one
3. Create `SKILL.md` with frontmatter (name matching directory) + `Follow the instructions in ./workflow.md.` (or `./workflow.yaml` if that's what exists)

**Step 2: Verify build**

Run: `node tools/build.js && node tools/validate.js`

**Step 3: Commit**

```bash
git add src/bmad/modules/custom/compass-skills/{0-governance,documentation,planning}/
git commit -m "feat(bmad): convert governance, documentation, and planning workflows to skill format"
```

---

## Task 4: Convert Compass-Only Workflows — Analysis + Solutioning + Anytime

**Files:**
- Create: 8 workflow skill directories in `compass-skills/`

### Workflow Mapping

| Old Path | New Skill Directory | Description |
|----------|-------------------|-------------|
| `workflows/1-analysis/design-thinking/` | `1-analysis/bmad-compass-design-thinking/` | Design thinking facilitation |
| `workflows/1-analysis/innovation-strategy/` | `1-analysis/bmad-compass-innovation-strategy/` | Innovation strategy workshop |
| `workflows/1-analysis/ingest-whitepapers/` | `1-analysis/bmad-compass-ingest-whitepapers/` | Whitepaper ingestion and analysis |
| `workflows/3-solutioning/threat-modeling/` | `3-solutioning/bmad-compass-threat-modeling/` | STRIDE threat modeling |
| `workflows/3-solutioning/security-architecture-review/` | `3-solutioning/bmad-compass-security-architecture-review/` | Security architecture review |
| `workflows/4-implementation/implementation-brainstorming/` | `4-implementation/bmad-compass-implementation-brainstorming/` | Implementation approach brainstorming |
| `workflows/4-implementation/implementation-research/` | `4-implementation/bmad-compass-implementation-research/` | Implementation research and analysis |
| `workflows/anytime/problem-solving/` | `anytime/bmad-compass-problem-solving/` | Structured problem-solving |

**Step 1-3:** Same pattern as Task 3.

**Step 4: Commit**

```bash
git add src/bmad/modules/custom/compass-skills/{1-analysis,3-solutioning,4-implementation,anytime}/
git commit -m "feat(bmad): convert analysis, solutioning, anytime Compass workflows to skill format"
```

---

## Task 5: Convert Compass-Only Workflows — Plan-Workflows + Secure Gates + Quick-Spec

**Files:**
- Create: 7 workflow skill directories in `compass-skills/`

### Workflow Mapping

| Old Path | New Skill Directory | Description |
|----------|-------------------|-------------|
| `workflows/2-plan-workflows/trigger-mapping/` | `2-plan-workflows/bmad-compass-trigger-mapping/` | Trigger mapping from requirements |
| `workflows/2-plan-workflows/outline-scenarios/` | `2-plan-workflows/bmad-compass-outline-scenarios/` | Scenario outlining from triggers |
| `workflows/2-plan-workflows/wds-ux-design/` | `2-plan-workflows/bmad-compass-wds-ux-design/` | WDS UX design delivery |
| `workflows/2-plan-workflows/docs/` | `2-plan-workflows/bmad-compass-conceptual-specs/` | Conceptual specification docs |
| `workflows/4-implementation/secure-gates/` | `4-implementation/bmad-compass-secure-gates/` | Security gate evaluation |
| `workflows/bmad-quick-flow/quick-spec/` | `4-implementation/bmad-compass-quick-spec/` | Quick technical spec creation |
| `workflows/1-project-brief/vtc-workshop/` | `1-analysis/bmad-compass-vtc-workshop/` | Vision-Traction-Clarity workshop |

**Note:** `workflows/2-plan-workflows/_agent-dialogs/` and `workflows/1-project-brief/templates/` are support files, not standalone workflows. They should be placed as sidecars inside relevant skill directories or in a shared `_resources/` directory.

**Step 1-3:** Same pattern as Task 3.

**Step 4: Handle support directories**

- `_agent-dialogs/` — If referenced by other workflows, place in a shared `_resources/` dir under `compass-skills/2-plan-workflows/`
- `1-project-brief/templates/` — Place as sidecars in the VTC workshop skill or in `_resources/`

**Step 5: Commit**

```bash
git add src/bmad/modules/custom/compass-skills/
git commit -m "feat(bmad): convert plan-workflows, secure-gates, quick-spec Compass workflows to skill format"
```

---

## Task 6: Convert Testarch Workflows (10)

**Files:**
- Create: 10 workflow skill directories in `compass-skills/4-implementation/`

### Workflow Mapping

| Old Path | New Skill Directory | Description |
|----------|-------------------|-------------|
| `workflows/testarch/atdd/` | `4-implementation/bmad-compass-testarch-atdd/` | ATDD test specification |
| `workflows/testarch/automate/` | `4-implementation/bmad-compass-testarch-automate/` | Test automation scaffolding |
| `workflows/testarch/ci/` | `4-implementation/bmad-compass-testarch-ci/` | CI pipeline test integration |
| `workflows/testarch/docs/` | `4-implementation/bmad-compass-testarch-docs/` | Test documentation generation |
| `workflows/testarch/framework/` | `4-implementation/bmad-compass-testarch-framework/` | Test framework setup |
| `workflows/testarch/nfr-assess/` | `4-implementation/bmad-compass-testarch-nfr-assess/` | Non-functional requirements assessment |
| `workflows/testarch/teach-me-testing/` | `4-implementation/bmad-compass-testarch-teach-me-testing/` | Interactive testing education |
| `workflows/testarch/test-design/` | `4-implementation/bmad-compass-testarch-test-design/` | Test design strategy |
| `workflows/testarch/test-review/` | `4-implementation/bmad-compass-testarch-test-review/` | Test review and quality check |
| `workflows/testarch/trace/` | `4-implementation/bmad-compass-testarch-trace/` | Requirements traceability |

**Additional TEA knowledge files:** The directory `src/bmad/modules/custom/bmm/testarch/` contains `knowledge/` and `tea-index.csv`. These are reference data for the TEA agent, not standalone workflows. Copy them to `compass-skills/4-implementation/_tea-knowledge/`.

**Step 1-3:** Same pattern as Task 3.

**Step 4: Copy TEA knowledge**

```bash
mkdir -p src/bmad/modules/custom/compass-skills/4-implementation/_tea-knowledge
cp -r src/bmad/modules/custom/bmm/testarch/knowledge/ src/bmad/modules/custom/compass-skills/4-implementation/_tea-knowledge/
cp src/bmad/modules/custom/bmm/testarch/tea-index.csv src/bmad/modules/custom/compass-skills/4-implementation/_tea-knowledge/
```

**Step 5: Commit**

```bash
git add src/bmad/modules/custom/compass-skills/4-implementation/
git commit -m "feat(bmad): convert 10 testarch workflows + TEA knowledge to compass-skills"
```

---

## Task 7: Audit and Convert Upstream Workflow Overrides

**Files:**
- Create: Override directories in `src/bmad/modules/custom/bmm-skills/` for workflows with meaningful differences
- Modify: None of the native files

**Context:** 17 custom workflows override upstream equivalents. Like Phase 2 agents, some may be identical to upstream and need no override. This task audits each and creates overrides only where there are meaningful Compass-specific differences.

### Audit Checklist

For each override, diff the custom content against the native skill:

| Custom Workflow | Native Skill | Action |
|----------------|-------------|--------|
| `1-analysis/create-product-brief/` | `bmad-product-brief` | Compare |
| `1-analysis/research/` | `research/` | Compare |
| `2-plan-workflows/create-prd/` | `bmad-create-prd` + `bmad-edit-prd` + `bmad-validate-prd` | Compare |
| `2-plan-workflows/create-ux-design/` | `bmad-create-ux-design` | Compare |
| `3-solutioning/check-implementation-readiness/` | `bmad-check-implementation-readiness` | Compare |
| `3-solutioning/create-architecture/` | `bmad-create-architecture` | Compare |
| `3-solutioning/create-epics-and-stories/` | `bmad-create-epics-and-stories` | Compare |
| `4-implementation/code-review/` | `bmad-code-review` | Compare |
| `4-implementation/correct-course/` | `bmad-correct-course` | Compare |
| `4-implementation/create-story/` | `bmad-create-story` | Compare |
| `4-implementation/dev-story/` | `bmad-dev-story` | Compare |
| `4-implementation/retrospective/` | `bmad-retrospective` | Compare |
| `4-implementation/sprint-planning/` | `bmad-sprint-planning` | Compare |
| `4-implementation/sprint-status/` | `bmad-sprint-status` | Compare |
| `bmad-quick-flow/quick-dev/` | `bmad-quick-dev` | Compare |
| `document-project/` | `bmad-document-project` | Compare |
| `generate-project-context/` | `bmad-generate-project-context` | Compare |

**Step 1: Run audit**

For each override, compare file content and determine:
- **Skip** — content is identical or trivially different (no override needed)
- **Override** — content has meaningful Compass-specific additions (create override in `custom/bmm-skills/`)

Known significant overrides from scope analysis:
- `dev-story` — 458-line instructions.xml vs native's simple workflow.md
- `code-review` — 249-line instructions.xml vs native's 6-line SKILL.md
- `create-prd` — bundles edit/validate into single directory

**Step 2: For each workflow that needs an override, create the skill directory**

Place in `src/bmad/modules/custom/bmm-skills/` mirroring the native phase structure:

```
custom/bmm-skills/{phase}/bmad-{name}/
├── SKILL.md          # Override entry point (references custom workflow files)
├── workflow.yaml     # Custom workflow (if different from native)
├── instructions.xml  # Custom instructions (if present)
├── checklist.md      # Custom checklist (if present)
└── ...               # Other custom files
```

The custom SKILL.md should reference the custom workflow files. Native files (workflow.md, steps/) will still be copied from native but won't be referenced by the custom SKILL.md.

**Step 3: For overrides that are identical to native, document the decision**

Add a comment in the commit message listing which workflows were audited and found identical.

**Step 4: Verify build and merge**

Run: `node tools/build.js && node tools/validate.js`

Verify overrides appear in dist: `diff <custom-file> <dist-file>` for a few spot checks.

**Step 5: Commit**

```bash
git add src/bmad/modules/custom/bmm-skills/
git commit -m "feat(bmad): convert upstream workflow overrides with Compass differences to bmm-skills"
```

---

## Task 8: Convert Custom Core Module

**Files:**
- Convert: BMad Master agent, core workflows (brainstorming, party-mode, advanced-elicitation, autonomous-refinement-loop)
- Handle: Core tasks (.xml/.md pairs), documentation framework, config

**Context:** The custom/core module contains:
- BMad Master orchestrator agent (`bmad-master.agent.yaml`)
- 4 workflows: brainstorming, party-mode, advanced-elicitation, autonomous-refinement-loop
- 8 task pairs (.xml + .md) — these are old-format task definitions
- Documentation framework (policies, templates)
- Config files (config.yaml, module.yaml, module-help.csv)

**Step 1: Determine target for each item**

| Content | Target | Rationale |
|---------|--------|-----------|
| BMad Master agent | `custom/core-skills/bmad-master/` | Core module override |
| Brainstorming workflow | Check if override of native `bmad-brainstorming` | May be override → bmm-skills or core-skills |
| Party-mode workflow | Check if override of native `bmad-party-mode` | May be override → core-skills |
| Advanced-elicitation | `custom/compass-skills/anytime/` | Compass-only |
| Autonomous-refinement-loop | `custom/compass-skills/anytime/` | Compass-only |
| Core tasks | Inline into relevant skill SKILL.md files or place as sidecars | Old format → merge into new |
| Documentation framework | Already shipped separately in `src/documentation/` | Verify no unique content, then skip |
| config.yaml, module.yaml | Not needed in new format | Skip |
| module-help.csv | Rows will be in compass-skills module-help.csv | Skip |

**Step 2: Convert BMad Master**

Read `src/bmad/modules/custom/core/agents/bmad-master.agent.yaml` and convert to skill format. Place in `src/bmad/modules/custom/core-skills/bmad-master/` (or as a core-skills override if native has a bmad-master equivalent).

Note: The build system currently doesn't have a `core-skills` custom module in `SKILL_MODULES`. If needed, the bmad-master can go in `custom/compass-skills/` instead.

**Step 3: Convert core workflows**

Check if brainstorming and party-mode are overrides of native core-skills:
- Native: `src/bmad/modules/native/core-skills/bmad-brainstorming/` and `src/bmad/modules/native/core-skills/bmad-party-mode/`
- If custom has meaningful differences → create override in `custom/core-skills/`
- If identical → no override needed

For advanced-elicitation and autonomous-refinement-loop (Compass-only):
- Create skill directories in `custom/compass-skills/anytime/`

**Step 4: Handle core tasks**

The 8 task pairs in `custom/core/tasks/` are old-format task definitions:
- `brainstorming.xml` — May be referenced by brainstorming workflow
- `editorial-review-prose.md/.xml` — Standalone task
- `editorial-review-structure.md/.xml` — Standalone task
- `help.md` — Help system task
- `index-docs.md/.xml` — Documentation indexing
- `review-adversarial-general.md/.xml` — Adversarial review
- `shard-doc.md/.xml` — Document sharding
- `workflow.md/.xml` — Generic workflow execution

For each task that is referenced by a workflow, place it as a sidecar in that workflow's skill directory. For standalone tasks, evaluate if they should become their own skill or be archived.

**Step 5: Verify build**

Run: `node tools/build.js && node tools/validate.js`

**Step 6: Commit**

```bash
git add src/bmad/modules/custom/{compass-skills,core-skills}/
git commit -m "feat(bmad): convert custom core module content to skill format"
```

---

## Task 9: Move bmad-builder to custom/bmad-builder-skills

**Files:**
- Move: `reference/migration-staging/bmad-builder/` → `src/bmad/modules/custom/bmad-builder-skills/`

**Context:** The bmad-builder module contains 3 agents (agent-builder, module-builder, workflow-builder) and extensive workflow templates for building BMAD modules. It was staged in `reference/migration-staging/` during Phase 1.

**Step 1: Create bmad-builder-skills module**

```bash
mkdir -p src/bmad/modules/custom/bmad-builder-skills
```

**Step 2: Create module.yaml**

```yaml
name: bmad-builder
displayName: BMAD Builder
description: Tools for building and modifying BMAD modules, agents, and workflows
version: "1.0.0"
type: module
```

**Step 3: Convert bmad-builder agents to skill format**

Read each agent YAML from `reference/migration-staging/bmad-builder/agents/`:
- `agent-builder.agent.yaml` → `bmad-builder-skills/bmad-agent-builder/`
- `module-builder.agent.yaml` → `bmad-builder-skills/bmad-module-builder/`
- `workflow-builder.agent.yaml` → `bmad-builder-skills/bmad-workflow-builder/`

Create SKILL.md + bmad-skill-manifest.yaml for each.

**Step 4: Move workflow templates**

Copy the workflow building templates and data from `reference/migration-staging/bmad-builder/workflows/` into appropriate skill directories in `bmad-builder-skills/`.

**Step 5: Copy module-help.csv**

Copy and adapt `reference/migration-staging/bmad-builder/module-help.csv` to 13-column format.

**Step 6: Update validate.js**

Add `custom/bmad-builder-skills` to `validateSkillFormat()` moduleRoots.

**Step 7: Verify build and commit**

Run: `node tools/build.js && node tools/validate.js`

```bash
git add src/bmad/modules/custom/bmad-builder-skills/ tools/validate.js
git commit -m "feat(bmad): move bmad-builder from staging to custom/bmad-builder-skills"
```

---

## Task 10: Move test-architecture Content to compass-skills TEA Section

**Files:**
- Move: `reference/migration-staging/test-architecture/` content → `compass-skills/4-implementation/`

**Context:** The test-architecture module was staged in `reference/migration-staging/` during Phase 1. Its content (knowledge base, team configs, test review workflows) should merge into the TEA section already started in Task 6.

**Step 1: Merge knowledge files**

The TEA knowledge from `reference/migration-staging/test-architecture/testarch/` should merge with the `_tea-knowledge/` directory created in Task 6.

```bash
cp -r reference/migration-staging/test-architecture/testarch/* src/bmad/modules/custom/compass-skills/4-implementation/_tea-knowledge/
```

**Step 2: Handle test-architecture agent**

`reference/migration-staging/test-architecture/agents/tea.agent.yaml` — This is the original TEA agent definition. Compare with the `tea.agent.yaml` in `custom/bmm/agents/`. If they differ, ensure the compass-skills version (from Task 2) has the most complete data.

**Step 3: Handle teams config**

`reference/migration-staging/test-architecture/teams/default-party.csv` — Place in `compass-skills/4-implementation/_tea-knowledge/teams/` or in a shared teams directory.

**Step 4: Handle test-review workflow**

`reference/migration-staging/test-architecture/workflows/testarch/test-review/checklist.md` — This may overlap with the testarch/test-review workflow from Task 6. Merge any unique content.

**Step 5: Verify build and commit**

Run: `node tools/build.js && node tools/validate.js`

```bash
git add src/bmad/modules/custom/compass-skills/4-implementation/
git commit -m "feat(bmad): merge test-architecture staging content into compass-skills TEA section"
```

---

## Task 11: Handle Data and Teams Directories

**Files:**
- Move: `src/bmad/modules/custom/bmm/data/project-context-template.md`
- Move: `src/bmad/modules/custom/bmm/teams/default-party.csv`
- Move: `src/bmad/modules/custom/bmm/teams/team-fullstack.yaml`

**Step 1: Place project-context-template**

This template is referenced by the analyst agent's brainstorming capability. Place it as a sidecar in the brainstorming skill or in a shared `_resources/` directory under compass-skills:

```bash
mkdir -p src/bmad/modules/custom/compass-skills/_resources
cp src/bmad/modules/custom/bmm/data/project-context-template.md src/bmad/modules/custom/compass-skills/_resources/
```

**Step 2: Place team configs**

Team configurations are used by party-mode and retrospective workflows:

```bash
mkdir -p src/bmad/modules/custom/compass-skills/_resources/teams
cp src/bmad/modules/custom/bmm/teams/*.csv src/bmad/modules/custom/compass-skills/_resources/teams/
cp src/bmad/modules/custom/bmm/teams/*.yaml src/bmad/modules/custom/compass-skills/_resources/teams/
```

**Step 3: Commit**

```bash
git add src/bmad/modules/custom/compass-skills/_resources/
git commit -m "feat(bmad): move data and team configs to compass-skills _resources"
```

---

## Task 12: Update Build System — Remove Compat Shim

**Files:**
- Modify: `tools/build.js` — Remove `buildBmadCompat()` function and its call
- Modify: `tools/build.js` — Remove `DIST_BMAD_REFERENCE_CSVS` (old path validation for compat)

**Step 1: Remove buildBmadCompat() from build.js**

Delete the entire `buildBmadCompat()` function (lines ~206-234) and its call in `buildBmadSkills()` (line ~264).

**Step 2: Remove DIST_BMAD_REFERENCE_CSVS**

Remove the constant and the `validateDistBmadReferences()` function call from build.js, since the old CSV paths won't resolve in the new layout.

**Step 3: Verify build**

Run: `node tools/build.js`

Expected: Build passes. `dist/_bmad/modules/` directory no longer exists. Only `dist/_bmad/bmm/`, `dist/_bmad/core/`, `dist/_bmad/compass/`, `dist/_bmad/bmad-builder/` exist.

**Step 4: Commit**

```bash
git add tools/build.js
git commit -m "refactor(build): remove buildBmadCompat() shim — all content now in skill format"
```

---

## Task 13: Update Validation — Remove Old-Format Checks

**Files:**
- Modify: `tools/validate.js`

**Step 1: Remove validateCustomBmadAgentExecPaths()**

Delete the entire function (lines ~154-182) and its call in `validate()`. This function scans `.agent.yaml` files for exec path references — no longer needed after old agent files are removed.

**Step 2: Remove BMAD_REFERENCE_CSVS**

Remove the constant (lines ~59-62) and the `validateBmadReferenceCsvs()` function. Old CSV path validation is no longer needed.

**Step 3: Update REQUIRED_PATHS**

Remove entries that reference old paths:
- `src/bmad/modules/custom/bmm/module-help.csv`

Add entries for new modules:
- `src/bmad/modules/custom/compass-skills/module.yaml`
- `src/bmad/modules/custom/bmm-skills/` (if not already present)

**Step 4: Add compass-skills and bmad-builder-skills to validateSkillFormat()**

If not already done in earlier tasks, ensure all custom modules are validated:

```javascript
const moduleRoots = [
  path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'bmm-skills'),
  path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'core-skills'),
  path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'bmm-skills'),
  path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'compass-skills'),
  path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'bmad-builder-skills'),
];
```

**Step 5: Verify**

Run: `node tools/validate.js`

Expected: PASS with no old-format validation errors.

**Step 6: Commit**

```bash
git add tools/validate.js
git commit -m "refactor(validate): remove old-format checks, add compass-skills + bmad-builder-skills validation"
```

---

## Task 14: Remove Old Directories and Clean Up

**Files:**
- Delete: `src/bmad/modules/custom/bmm/` (entire directory)
- Delete: `src/bmad/modules/custom/core/` (entire directory)
- Delete: `reference/migration-staging/` (entire directory)
- Delete: `src/bmad/_config/` (old manifests — Phase 4 will regenerate)

**Step 1: Verify no remaining references**

Before deleting, search for any remaining references to the old paths:

```bash
grep -r "modules/custom/bmm/" src/ tools/ --include="*.js" --include="*.md" --include="*.yaml" --include="*.csv"
grep -r "modules/custom/core/" src/ tools/ --include="*.js" --include="*.md" --include="*.yaml" --include="*.csv"
grep -r "migration-staging/" src/ tools/ --include="*.js" --include="*.md" --include="*.yaml" --include="*.csv"
```

If any references remain, update them before proceeding.

**Step 2: Delete old directories**

```bash
rm -rf src/bmad/modules/custom/bmm/
rm -rf src/bmad/modules/custom/core/
rm -rf reference/migration-staging/
rm -rf src/bmad/_config/
```

**Step 3: Verify build**

Run: `node tools/build.js && node tools/validate.js`

Expected: Build passes cleanly. No old-format content in dist.

**Step 4: Verify dist layout**

```bash
ls dist/_bmad/
```

Expected: `bmm/`, `core/`, `compass/`, `bmad-builder/`, `BMAD-workflow.md` — no `modules/` or `_config/` directories.

**Step 5: Commit**

```bash
git add -A
git commit -m "refactor(bmad): remove all old-format directories — Phase 3 migration complete

Removed:
- src/bmad/modules/custom/bmm/ (old agent YAMLs + workflows)
- src/bmad/modules/custom/core/ (old core module)
- reference/migration-staging/ (temporary staging from Phase 1)
- src/bmad/_config/ (old hand-maintained manifests)"
```

---

## Task 15: Update Design Document and Create PR

**Files:**
- Modify: `docs/plans/2026-04-06-bmad-upstream-migration-design.md`

**Step 1: Update Phase 3 status**

Mark Phase 3 as complete with actual implementation details.

**Step 2: Run full build and validation**

```bash
node tools/build.js && node tools/validate.js
```

**Step 3: Push and create PR**

```bash
git push -u origin <branch-name>
gh pr create --title "feat(bmad): Phase 3 — compass-skills module and old-format removal"
```

---

## Execution Notes

### Recommended Sub-PRs

Given the large scope, consider splitting into 2-3 PRs:

1. **PR A (Tasks 1-6):** Create compass-skills module, convert agents and Compass-only workflows — purely additive, no breakage risk
2. **PR B (Tasks 7-11):** Convert upstream overrides, core module, bmad-builder, test-architecture — still additive
3. **PR C (Tasks 12-15):** Remove compat shim, old directories, update validation — the breaking change

This allows incremental merging and reduces blast radius.

### Risk Mitigation

- Old `.agent.yaml` files reference `{project-root}/_bmad/modules/custom/bmm/...` paths. These only resolve via the compat shim. Removing the compat shim (Task 12) breaks these references. This is intentional — the new SKILL.md format uses skill names instead of paths.
- The old CSVs (`bmad-help.csv`, `module-help.csv`) reference old paths. They're removed in Task 14. Phase 4 generates new manifests.
- `sync-client-bundles.js` reads `bmad-help.csv` to generate commands. After removing the CSV (Task 14), this script won't work. Phase 5 replaces it with skill-based generation. Until then, the old commands in `src/claude/commands/bmad/` remain functional.

### Build Must Pass After Each Task

After every commit, `node tools/build.js && node tools/validate.js` must pass. If a task breaks the build, fix it before proceeding.
