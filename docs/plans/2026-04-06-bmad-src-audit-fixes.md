# BMAD Source Audit Fixes Implementation Plan

> **SUPERSEDED:** All tasks in this plan have been completed. Excalidraw workflows were integrated, agent filenames were renamed, and agent .md files were created. This plan is retained for reference only.
>
> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close gaps found during the BMAD src audit: integrate excalidraw workflows from upstream, rename name-based agent filenames to purpose-based, and create missing agent documentation .md files.

**Architecture:** All changes are in `src/bmad/` (source of truth) with manifests, CSV indexes, and agent files updated in concert. After each task group, `sync-client-bundles`, `build`, and `validate` confirm integrity. No runtime code changes — this is configuration, documentation, and manifest alignment.

**Tech Stack:** Markdown, YAML, CSV, Node.js build tooling (`tools/build.js`, `tools/validate.js`, `tools/sync-client-bundles.js`)

---

## Task 1: Integrate Excalidraw Workflows from Upstream

Upstream BMAD-METHOD has 4 excalidraw diagram workflows plus supporting resources that are not deployed to the native module. These enable creating dataflows, diagrams, flowcharts, and wireframes in Excalidraw format.

**Files:**
- Copy from: `BMAD-METHOD/src/bmm/workflows/excalidraw-diagrams/` (14 files)
- Copy from: `BMAD-METHOD/src/core/resources/excalidraw/` (4 files)
- Create: `src/bmad/modules/native/bmm/workflows/excalidraw-diagrams/` (entire directory)
- Create: `src/bmad/modules/native/core/resources/excalidraw/` (entire directory)
- Modify: `src/bmad/_config/workflow-manifest.csv`
- Modify: `src/bmad/_config/bmad-help.csv`
- Modify: `src/bmad/modules/custom/bmm/module-help.csv`

### Step 1: Copy excalidraw workflow files from upstream to native

```bash
# BMM workflows (4 workflows x 3 files each + _shared directory)
cp -r BMAD-METHOD/src/bmm/workflows/excalidraw-diagrams/ \
  src/bmad/modules/native/bmm/workflows/excalidraw-diagrams/

# Core resources (4 files)
mkdir -p src/bmad/modules/native/core/resources/excalidraw/
cp BMAD-METHOD/src/core/resources/excalidraw/* \
  src/bmad/modules/native/core/resources/excalidraw/
```

### Step 2: Update installed paths in workflow YAML files

The upstream workflow.yaml files reference `{project-root}/_bmad/bmm/workflows/...` and `{project-root}/_bmad/core/resources/...`. These must be updated to use the native module path convention: `_bmad/modules/native/bmm/workflows/...` and `_bmad/modules/native/core/resources/...`.

Update each of the 4 workflow YAML files in `src/bmad/modules/native/bmm/workflows/excalidraw-diagrams/`:

**In `create-dataflow/workflow.yaml`, `create-diagram/workflow.yaml`, `create-flowchart/workflow.yaml`, `create-wireframe/workflow.yaml`:**

Replace:
```yaml
installed_path: "{project-root}/_bmad/bmm/workflows/excalidraw-diagrams/create-<type>"
shared_path: "{project-root}/_bmad/bmm/workflows/excalidraw-diagrams/_shared"
helpers: "{project-root}/_bmad/core/resources/excalidraw/excalidraw-helpers.md"
json_validation: "{project-root}/_bmad/core/resources/excalidraw/validate-json-instructions.md"
```

With:
```yaml
installed_path: "{project-root}/_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-<type>"
shared_path: "{project-root}/_bmad/modules/native/bmm/workflows/excalidraw-diagrams/_shared"
helpers: "{project-root}/_bmad/modules/native/core/resources/excalidraw/excalidraw-helpers.md"
json_validation: "{project-root}/_bmad/modules/native/core/resources/excalidraw/validate-json-instructions.md"
```

Where `<type>` is `dataflow`, `diagram`, `flowchart`, or `wireframe` respectively.

### Step 3: Add excalidraw entries to workflow-manifest.csv

Append these 4 rows to `src/bmad/_config/workflow-manifest.csv`:

```csv
"bmad-bmm-create-excalidraw-dataflow","Create data flow diagrams (DFD) in Excalidraw format.","bmm","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-dataflow/workflow.yaml"
"bmad-bmm-create-excalidraw-diagram","Create system architecture diagrams, ERDs, UML diagrams, or general technical diagrams in Excalidraw format.","bmm","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-diagram/workflow.yaml"
"bmad-bmm-create-excalidraw-flowchart","Create flowchart visualizations in Excalidraw format for processes, pipelines, or logic flows.","bmm","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-flowchart/workflow.yaml"
"bmad-bmm-create-excalidraw-wireframe","Create website or app wireframes in Excalidraw format.","bmm","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-wireframe/workflow.yaml"
```

### Step 4: Add excalidraw entries to bmad-help.csv

Append these 4 rows to `src/bmad/_config/bmad-help.csv` (follows the existing column format):

```csv
"bmm","anytime","Create Dataflow","CDF","","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-dataflow/workflow.yaml","bmad-bmm-create-excalidraw-dataflow","false","ux-designer","Sally","UX Designer","🎨","Create Mode","Create data flow diagrams (DFD) in Excalidraw format - can be called standalone or during any workflow to add visual documentation.","planning_artifacts","dataflow diagram"
"bmm","anytime","Create Diagram","CED","","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-diagram/workflow.yaml","bmad-bmm-create-excalidraw-diagram","false","ux-designer","Sally","UX Designer","🎨","Create Mode","Create system architecture diagrams, ERDs, UML diagrams, or general technical diagrams in Excalidraw format.","planning_artifacts","diagram"
"bmm","anytime","Create Flowchart","CFC","","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-flowchart/workflow.yaml","bmad-bmm-create-excalidraw-flowchart","false","ux-designer","Sally","UX Designer","🎨","Create Mode","Create flowchart visualizations in Excalidraw format for processes, pipelines, or logic flows.","planning_artifacts","flowchart"
"bmm","anytime","Create Wireframe","CEW","","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-wireframe/workflow.yaml","bmad-bmm-create-excalidraw-wireframe","false","ux-designer","Sally","UX Designer","🎨","Create Mode","Create website or app wireframes in Excalidraw format.","planning_artifacts","wireframe"
```

### Step 5: Add excalidraw entries to module-help.csv

Append these 4 rows to `src/bmad/modules/custom/bmm/module-help.csv` (follows the existing column format with fewer columns than bmad-help):

```csv
"bmm","anytime","Create Dataflow","CDF","","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-dataflow/workflow.yaml","bmad-bmm-create-excalidraw-dataflow","false","ux-designer","Create Mode","Create data flow diagrams (DFD) in Excalidraw format - can be called standalone or during any workflow to add visual documentation.","planning_artifacts","dataflow diagram"
"bmm","anytime","Create Diagram","CED","","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-diagram/workflow.yaml","bmad-bmm-create-excalidraw-diagram","false","ux-designer","Create Mode","Create system architecture diagrams, ERDs, UML diagrams, or general technical diagrams in Excalidraw format.","planning_artifacts","diagram"
"bmm","anytime","Create Flowchart","CFC","","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-flowchart/workflow.yaml","bmad-bmm-create-excalidraw-flowchart","false","ux-designer","Create Mode","Create flowchart visualizations in Excalidraw format for processes, pipelines, or logic flows.","planning_artifacts","flowchart"
"bmm","anytime","Create Wireframe","CEW","","_bmad/modules/native/bmm/workflows/excalidraw-diagrams/create-wireframe/workflow.yaml","bmad-bmm-create-excalidraw-wireframe","false","ux-designer","Create Mode","Create website or app wireframes in Excalidraw format.","planning_artifacts","wireframe"
```

### Step 6: Sync client bundles and validate

```bash
node tools/sync-client-bundles.js   # Generates new command .md files for the 4 excalidraw commands
node tools/validate.js              # Verify all references resolve
node tools/build.js                 # Build dist and run build validation
```

Expected: 66 commands synced (was 62), validate passes, build passes.

### Step 7: Commit

```bash
git add src/bmad/modules/native/bmm/workflows/excalidraw-diagrams/ \
        src/bmad/modules/native/core/resources/excalidraw/ \
        src/bmad/_config/workflow-manifest.csv \
        src/bmad/_config/bmad-help.csv \
        src/bmad/modules/custom/bmm/module-help.csv \
        src/claude/commands/bmad/ \
        src/opencode/commands/bmad/ \
        src/claude/skills/ \
        src/codex/skills/ \
        dist/
git commit -m "feat(bmad): integrate excalidraw diagram workflows from upstream

Copy 4 excalidraw workflows (dataflow, diagram, flowchart, wireframe)
and supporting core resources from BMAD-METHOD upstream into native
modules. Add manifest entries and generate client commands.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Rename Name-Based Agent Filenames to Purpose-Based

Two agent filenames use character names instead of purpose-based names:
- `freya-ux.agent.yaml` (Freya, Compass WDS Designer) → `wds-designer.agent.yaml`
- `saga-analyst.agent.yaml` (Saga, Compass WDS Analyst) → `wds-analyst.agent.yaml`

**Files:**
- Rename: `src/bmad/modules/custom/bmm/agents/freya-ux.agent.yaml` → `wds-designer.agent.yaml`
- Rename: `src/bmad/modules/custom/bmm/agents/saga-analyst.agent.yaml` → `wds-analyst.agent.yaml`
- Modify: `src/bmad/modules/custom/bmm/agents/wds-designer.agent.yaml` (update id field)
- Modify: `src/bmad/modules/custom/bmm/agents/wds-analyst.agent.yaml` (update id field)
- Modify: `src/bmad/_config/agent-manifest.csv` (2 rows: id and path columns)
- Modify: `src/bmad/_config/bmad-help.csv` (4 rows: agent column)
- Modify: `src/bmad/modules/custom/bmm/module-help.csv` (4 rows: agent column)

### Step 1: Rename the agent files

```bash
cd src/bmad/modules/custom/bmm/agents/
git mv freya-ux.agent.yaml wds-designer.agent.yaml
git mv saga-analyst.agent.yaml wds-analyst.agent.yaml
```

### Step 2: Update the id field inside each renamed agent YAML

**In `wds-designer.agent.yaml`:**

Replace:
```yaml
    id: "_bmad/modules/custom/bmm/agents/freya-ux.md"
```
With:
```yaml
    id: "_bmad/modules/custom/bmm/agents/wds-designer.md"
```

**In `wds-analyst.agent.yaml`:**

Replace:
```yaml
    id: "_bmad/modules/custom/bmm/agents/saga-analyst.md"
```
With:
```yaml
    id: "_bmad/modules/custom/bmm/agents/wds-analyst.md"
```

### Step 3: Update agent-manifest.csv

In `src/bmad/_config/agent-manifest.csv`:

- Row for Freya: change `id` from `_bmad/modules/custom/bmm/agents/freya-ux.md` to `_bmad/modules/custom/bmm/agents/wds-designer.md` AND change `path` from `_bmad/modules/custom/bmm/agents/freya-ux.agent.yaml` to `_bmad/modules/custom/bmm/agents/wds-designer.agent.yaml`
- Row for Saga: change `id` from `_bmad/modules/custom/bmm/agents/saga-analyst.md` to `_bmad/modules/custom/bmm/agents/wds-analyst.md` AND change `path` from `_bmad/modules/custom/bmm/agents/saga-analyst.agent.yaml` to `_bmad/modules/custom/bmm/agents/wds-analyst.agent.yaml`

### Step 4: Update bmad-help.csv

In `src/bmad/_config/bmad-help.csv`, update the `agent` column (column index 9, 0-based):

- Lines 39-40 (Trigger Mapping, Outline Scenarios): change `saga-analyst` to `wds-analyst`
- Lines 42-43 (Conceptual Specifications, Design Delivery): change `freya-ux` to `wds-designer`

### Step 5: Update module-help.csv

In `src/bmad/modules/custom/bmm/module-help.csv`, update the `agent` column:

- Lines 32-33 (Trigger Mapping, Outline Scenarios): change `saga-analyst` to `wds-analyst`
- Lines 35-36 (Conceptual Specifications, Design Delivery): change `freya-ux` to `wds-designer`

### Step 6: Sync client bundles and validate

```bash
node tools/sync-client-bundles.js
node tools/validate.js
node tools/build.js
```

### Step 7: Commit

```bash
git add src/bmad/modules/custom/bmm/agents/ \
        src/bmad/_config/agent-manifest.csv \
        src/bmad/_config/bmad-help.csv \
        src/bmad/modules/custom/bmm/module-help.csv \
        src/claude/commands/bmad/ \
        src/opencode/commands/bmad/ \
        src/claude/skills/ \
        src/codex/skills/ \
        dist/
git commit -m "refactor(bmad): rename name-based agent files to purpose-based

Rename freya-ux.agent.yaml -> wds-designer.agent.yaml and
saga-analyst.agent.yaml -> wds-analyst.agent.yaml. Agent character
names (Freya, Saga) are preserved inside the YAML; only filenames
and manifest references change to follow the purpose-based naming
convention (like qa.agent.yaml for Quinn).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Create Missing Agent Documentation .md Files

The `agent-manifest.csv` `id` column references 19 `.md` files that don't exist. These are used by party-mode and other workflows that load the manifest. Create a documentation profile for each agent at the path specified in the `id` column.

**Files to create (19 total):**
- `src/bmad/modules/custom/bmm/agents/analyst.md`
- `src/bmad/modules/custom/bmm/agents/architect.md`
- `src/bmad/modules/custom/bmm/agents/creative-problem-solver.md`
- `src/bmad/modules/custom/bmm/agents/design-thinking-coach.md`
- `src/bmad/modules/custom/bmm/agents/dev.md`
- `src/bmad/modules/custom/bmm/agents/wds-designer.md` (was freya-ux.md, updated in Task 2)
- `src/bmad/modules/custom/bmm/agents/innovation-strategist.md`
- `src/bmad/modules/custom/bmm/agents/pm.md`
- `src/bmad/modules/custom/bmm/agents/qa.md`
- `src/bmad/modules/custom/bmm/agents/quick-flow-solo-dev.md`
- `src/bmad/modules/custom/bmm/agents/wds-analyst.md` (was saga-analyst.md, updated in Task 2)
- `src/bmad/modules/custom/bmm/agents/security-architect.md`
- `src/bmad/modules/custom/bmm/agents/sm.md`
- `src/bmad/modules/custom/bmm/agents/tea.md`
- `src/bmad/modules/custom/bmm/agents/tech-writer.md`
- `src/bmad/modules/custom/bmm/agents/threat-analyst.md`
- `src/bmad/modules/custom/bmm/agents/ux-designer.md`
- `src/bmad/modules/custom/core/agents/bmad-master.md`

**Note:** `tech-writer.md` goes at `src/bmad/modules/custom/bmm/agents/tech-writer.md` (not inside the `tech-writer/` subdirectory), matching the manifest id `_bmad/modules/custom/bmm/agents/tech-writer.md`.

### Step 1: Create all 19 agent .md files

Each file follows this format, populated from the agent-manifest.csv data:

```markdown
# <Name> — <Title>

> <Icon> <Role>

## Identity

<Identity text from manifest>

## Communication Style

<Communication style text from manifest>

## Core Principles

<Principles text from manifest, reformatted as bullet list>

---

**Module:** <module> | **Definition:** [`<filename>.agent.yaml`](./<filename>.agent.yaml)
```

Generate each file using the corresponding row from `agent-manifest.csv`. The data is already in the CSV — this is a transformation, not authoring.

For `bmad-master.md`, the path is `src/bmad/modules/custom/core/agents/bmad-master.md` and the definition link points to `./bmad-master.agent.yaml`.

### Step 2: Validate and build

```bash
node tools/validate.js
node tools/build.js
```

Expected: validate passes (no new required paths, but confirms no regressions), build passes.

### Step 3: Commit

```bash
git add src/bmad/modules/custom/bmm/agents/*.md \
        src/bmad/modules/custom/core/agents/bmad-master.md \
        dist/
git commit -m "docs(bmad): create agent profile .md files referenced by manifest

The agent-manifest.csv id column references 19 .md documentation
files that did not exist. Create each one from the manifest data so
party-mode and other manifest-consuming workflows can resolve them.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Clean Up Stale Command Files and Rebuild

The earlier `sync-client-bundles` run already identified 2 stale commands per client (4 files total) from commands removed from `bmad-help.csv`. Ensure these are committed.

**Files removed by sync:**
- `src/claude/commands/bmad/bmad-bmm-ingest-whitepapers.md`
- `src/claude/commands/bmad/bmad-bmm-oversight-checkpoint.md`
- `src/opencode/commands/bmad/bmad-bmm-ingest-whitepapers.md`
- `src/opencode/commands/bmad/bmad-bmm-oversight-checkpoint.md`

### Step 1: Verify these files are already deleted

```bash
ls src/claude/commands/bmad/bmad-bmm-ingest-whitepapers.md 2>/dev/null && echo "EXISTS" || echo "GONE"
ls src/claude/commands/bmad/bmad-bmm-oversight-checkpoint.md 2>/dev/null && echo "EXISTS" || echo "GONE"
```

Expected: both report "GONE".

### Step 2: Commit the stale file cleanup

```bash
git add src/claude/commands/bmad/bmad-bmm-ingest-whitepapers.md \
        src/claude/commands/bmad/bmad-bmm-oversight-checkpoint.md \
        src/opencode/commands/bmad/bmad-bmm-ingest-whitepapers.md \
        src/opencode/commands/bmad/bmad-bmm-oversight-checkpoint.md
git commit -m "chore(bmad): remove stale command files no longer in bmad-help.csv

bmad-bmm-ingest-whitepapers and bmad-bmm-oversight-checkpoint were
removed from bmad-help.csv but their generated command files persisted.
Sync-client-bundles cleaned them up.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Final Validation and Push

### Step 1: Full check suite

```bash
node tools/validate.js
node tools/check-root-drift.js
node tools/check-github-drift.js
node tools/build.js
```

All must pass.

### Step 2: Push

```bash
git push
```
