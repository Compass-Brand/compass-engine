# BMAD Upstream Migration Design

**Goal:** Migrate compass-engine from its current module-based layout to the upstream BMAD v6.2.2 skill-based architecture, enabling easy tracking of upstream releases while preserving Compass-specific customizations.

**Decision date:** 2026-04-06

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Upstream relationship | Track closely | Future upstream updates should be easy to pull in |
| Native/custom overlay | Keep the split | `native/` mirrors upstream, `custom/` holds overrides and Compass content. Build merges them (custom wins). Preserves clean diffability against upstream. |
| Compass-only content | Two custom modules | `custom/bmm-skills/` for upstream overrides, `custom/compass-skills/` for all Compass-only content (TEA, WDS, security, CIS, governance, planning, docs) organized by phase |
| bmad-builder and TEA | Move to custom | Not from BMAD-METHOD — bmad-builder goes to `custom/bmad-builder-skills/`, TEA folds into `custom/compass-skills/`. Makes `native/` a clean submodule mirror. |
| BMAD-METHOD submodule | Keep, pin to tags | Reference for diffing and pulling updates. Not a build dependency. Pin to `v6.2.2`. |
| Build system | Evolve existing | Update `build.js` to walk skill directories, merge native/custom, generate manifests and client skill files. Replace `sync-client-bundles.js`. |
| Installed layout | Flat, matches upstream | `dist/_bmad/bmm/`, `dist/_bmad/core/`, `dist/_bmad/compass/`, `dist/_bmad/bmad-builder/`. No native/custom split in output. |
| Migration strategy | Phased (5 phases) | Each phase produces a working state with its own branch and PR |

---

## Architecture

### Source Layout

```
src/bmad/
├── modules/
│   ├── native/
│   │   ├── bmm-skills/              # Mirror of BMAD-METHOD/src/bmm-skills/
│   │   │   ├── module.yaml
│   │   │   ├── module-help.csv      # 13-column format with after/before deps
│   │   │   ├── 1-analysis/
│   │   │   │   ├── bmad-agent-analyst/
│   │   │   │   │   ├── SKILL.md
│   │   │   │   │   └── bmad-skill-manifest.yaml
│   │   │   │   ├── bmad-create-product-brief/
│   │   │   │   │   ├── SKILL.md
│   │   │   │   │   ├── workflow.md
│   │   │   │   │   └── steps/
│   │   │   │   └── ...
│   │   │   ├── 2-plan-workflows/
│   │   │   ├── 3-solutioning/
│   │   │   └── 4-implementation/
│   │   │
│   │   └── core-skills/             # Mirror of BMAD-METHOD/src/core-skills/
│   │       ├── module.yaml
│   │       ├── module-help.csv
│   │       ├── bmad-brainstorming/
│   │       ├── bmad-party-mode/
│   │       └── ...
│   │
│   └── custom/
│       ├── bmm-skills/              # Compass overrides of upstream agents/workflows
│       │   ├── 1-analysis/
│       │   │   └── bmad-agent-analyst/   # Override: custom persona for Mary
│       │   ├── 2-plan-workflows/
│       │   │   └── bmad-agent-pm/        # Override: custom persona for John
│       │   └── ...
│       │
│       ├── compass-skills/          # All Compass-only content
│       │   ├── module.yaml
│       │   ├── module-help.csv
│       │   ├── 0-governance/
│       │   │   ├── bmad-compass-phase-sync/
│       │   │   ├── bmad-compass-phase-closeout/
│       │   │   └── bmad-compass-oversight-checkpoint/
│       │   ├── 1-analysis/
│       │   │   ├── bmad-compass-design-thinking/
│       │   │   ├── bmad-compass-innovation-strategy/
│       │   │   └── bmad-compass-ingest-whitepapers/
│       │   ├── 2-plan-workflows/
│       │   │   ├── bmad-compass-trigger-mapping/
│       │   │   ├── bmad-compass-outline-scenarios/
│       │   │   ├── bmad-compass-conceptual-specs/
│       │   │   ├── bmad-compass-wds-ux-design/
│       │   │   └── bmad-agent-wds-designer/
│       │   ├── 3-solutioning/
│       │   │   ├── bmad-compass-threat-modeling/
│       │   │   ├── bmad-compass-security-architecture-review/
│       │   │   └── bmad-agent-security-architect/
│       │   ├── 4-implementation/
│       │   │   ├── bmad-compass-secure-gates/
│       │   │   ├── bmad-compass-implementation-brainstorming/
│       │   │   ├── bmad-compass-implementation-research/
│       │   │   └── bmad-compass-testarch-*/  (10 TEA workflows)
│       │   ├── anytime/
│       │   │   └── bmad-compass-problem-solving/
│       │   ├── documentation/
│       │   │   ├── bmad-compass-init-docs/
│       │   │   ├── bmad-compass-update-docs/
│       │   │   └── bmad-compass-validate-docs/
│       │   └── planning/
│       │       ├── bmad-compass-init-planning/
│       │       ├── bmad-compass-workspace-bootstrap/
│       │       ├── bmad-compass-project-roadmap/
│       │       └── bmad-compass-sync-repositories/
│       │
│       └── bmad-builder-skills/     # Builder module
│           ├── module.yaml
│           └── ...
│
├── _config/                         # Build-time config (not hand-maintained manifests)
└── BMAD-workflow.md
```

### Built Output

```
dist/_bmad/
├── bmm/                 # Merged: native bmm-skills + custom bmm-skills overrides
│   ├── config.yaml
│   ├── module-help.csv
│   ├── 1-analysis/
│   ├── 2-plan-workflows/
│   ├── 3-solutioning/
│   └── 4-implementation/
├── core/                # Merged: native core-skills + custom core-skills overrides
│   ├── config.yaml
│   ├── module-help.csv
│   └── ...
├── compass/             # custom/compass-skills/ as-is
│   ├── config.yaml
│   ├── module-help.csv
│   └── ...
├── bmad-builder/        # custom/bmad-builder-skills/ as-is
└── _config/
    ├── agent-manifest.csv   # Generated: all agents from all modules
    ├── skill-manifest.csv   # Generated: all skills from all modules
    └── bmad-help.csv        # Generated: merged from per-module module-help.csv
```

### Client Output

```
dist/.claude/skills/
├── bmad-agent-bmm-analyst/SKILL.md
├── bmad-bmm-create-product-brief/SKILL.md
├── bmad-compass-threat-modeling/SKILL.md
└── ...

dist/.opencode/skills/    # Same structure
dist/.codex/skills/       # Same structure
```

---

## Skill Format

### Agent Skill Directory

```
bmad-agent-analyst/
├── SKILL.md                      # Entry point with frontmatter
└── bmad-skill-manifest.yaml      # Agent metadata (type, displayName, title, icon, etc.)
```

**SKILL.md frontmatter:**
```yaml
---
name: bmad-agent-analyst
description: 'Strategic business analyst for market research, requirements, and domain expertise.'
---
```

**bmad-skill-manifest.yaml:**
```yaml
type: agent
name: bmad-agent-analyst
displayName: Mary
title: Business Analyst
icon: "📊"
capabilities: "market research, competitive analysis, requirements elicitation"
role: Strategic Business Analyst + Requirements Expert
identity: "Senior analyst with deep expertise..."
communicationStyle: "Speaks with the excitement of a treasure hunter..."
principles: "Channel expert business analysis frameworks..."
module: bmm
```

### Workflow Skill Directory

```
bmad-create-product-brief/
├── SKILL.md              # Entry: frontmatter + "Follow ./workflow.md"
├── workflow.md           # Orchestration logic
└── steps/                # Optional micro-step files
    ├── step-01-*.md
    ├── step-02-*.md
    └── ...
```

### Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Upstream agent | `bmad-agent-{name}` | `bmad-agent-analyst` |
| Upstream workflow | `bmad-{name}` | `bmad-create-product-brief` |
| Compass agent | `bmad-agent-{name}` | `bmad-agent-wds-designer` |
| Compass workflow | `bmad-compass-{name}` | `bmad-compass-threat-modeling` |

### Module-Help CSV (13 columns)

```
module,skill,display-name,menu-code,description,action,args,phase,after,before,required,output-location,outputs
```

The `after`/`before` columns replace sequence numbers with explicit dependency references.

---

## Build System Changes

### build.js (Phase 1 ✅ + Phase 4-5 remaining)

**Done (Phase 1):**
1. **`mergeModules()`** — Copies entire native tree then overlays custom (custom files win).
2. **`buildBmadSkills()`** — Orchestrates: copies BMAD-workflow.md, merges bmm + core skill modules, copies custom-only modules, runs compat shim.
3. **`buildBmadCompat()`** — Temporary: copies old-format `custom/bmm/` and `custom/core/` to `dist/_bmad/modules/custom/` at CSV-referenced paths. Removed in Phase 3.

**Remaining (Phase 4):**
4. **Manifest generation** — Walk merged `dist/_bmad/`, collect `bmad-skill-manifest.yaml` files, generate `agent-manifest.csv`, `skill-manifest.csv`, and merged `bmad-help.csv` automatically.

**Remaining (Phase 5):**
5. **Client skill generation** — Replace `sync-client-bundles.js`. Generate skill directories for each client platform from merged module tree.

### validate.js (Phase 1 ✅ + Phase 4 remaining)

**Done (Phase 1):**
- SKILL.md frontmatter validation (name matches directory)
- Updated REQUIRED_PATHS for new skill layout
- Removed workflow-manifest.csv from BMAD_REFERENCE_CSVS

**Remaining (Phase 4):**
- Agent skills have `bmad-skill-manifest.yaml` (or `bmad-manifest.json`)
- Internal path references use relative paths
- Module-help.csv `after`/`before` references resolve to real skills

### sync-client-bundles.js → removed in Phase 5

Currently still active — generates commands from `bmad-help.csv`. Replaced by skill-file generation in Phase 5.

### push.js

Unchanged — operates on `dist/` which is just a different shape.

---

## Migration Phases

### Phase 1: Native Module Restructure + Build Foundation ✅

**Status:** Complete (PR #75, merged 2026-04-06)

**What was done:**
- Pinned BMAD-METHOD submodule to `v6.2.2` tag
- Copied upstream `bmm-skills/` (31 skills) and `core-skills/` (12 skills) to `native/`
- Removed old `native/bmm/`, `native/core/`, `native/bmad-builder/`, `native/test-architecture/`
- Updated `build.js` with `mergeModules()`, `buildBmadSkills()`, `buildBmadCompat()`
- Updated `validate.js` with `validateSkillFormat()` and new REQUIRED_PATHS
- Deleted `workflow-manifest.csv` and `task-manifest.csv` (pulled forward from Phase 4)
- Removed excalidraw entries from CSVs (restored in Phase 5 from upstream module-help.csv)
- Staged `bmad-builder` and `test-architecture` in `reference/migration-staging/` for Phase 3

**Current state:**
- `dist/_bmad/bmm/` and `dist/_bmad/core/` contain upstream skill-format modules
- `dist/_bmad/modules/custom/` contains old-format custom content (compat shim)
- `sync-client-bundles.js` still generates 62 commands from old `bmad-help.csv`
- Old custom modules (`custom/bmm/`, `custom/core/`) still in old format

---

### Phase 2: Convert Custom BMM Overrides ✅

**Status:** Complete (PR #76, merged 2026-04-07)

**Scope:** Create Compass-specific agent overrides in upstream skill format for agents that differ from upstream v6.2.2.

**Key finding:** Only 3 of the original 9 agents have meaningful Compass-specific differences. The other 6 (PM, UX Designer, Architect, Dev, QA, SM) have identical persona data, capabilities, and activation flow to upstream — upstream v6.2.2 already incorporated them. Creating overrides for identical agents would duplicate content and create maintenance burden.

**What was done:**
- Extended `validateSkillFormat()` to also scan `custom/bmm-skills/`
- Created 3 Compass agent overrides in `custom/bmm-skills/`:
  - `1-analysis/bmad-agent-analyst/` (Mary) — DP capability changed from `bmad-document-project` to `bmad-compass-init-docs`
  - `1-analysis/bmad-agent-tech-writer/` (Paige) — 3 additional capabilities (DU, DV, US), Compass-specific principles about `docs/human/policies/`, sidecar files (update-standards.md, documentation-standards.md)
  - `4-implementation/bmad-agent-quick-flow-solo-dev/` (Barry) — restored QS (quick-spec) capability that upstream merged into unified QD
- Verified build merge produces correct output (Compass overrides replace upstream defaults)

**Old agent files NOT removed:** The old `.agent.yaml` and `.md` files in `custom/bmm/agents/` are still referenced by `agent-manifest.csv`, the old orchestrator, `buildBmadCompat()`, and `validateCustomBmadAgentExecPaths()`. They will be removed in Phase 3 when all old-format content goes away together.

**Does NOT include:** Converting Compass-only agents (wds-designer, wds-analyst, security-architect, threat-analyst, tea, creative-problem-solver, design-thinking-coach, innovation-strategist) — those go to `compass-skills/` in Phase 3.

---

### Phase 3: Create compass-skills Module ✅

**Status:** Complete (PR #77, 2026-04-07)

**Scope:** Convert all Compass-only content to skill format and remove old custom directories.

**What was done:**
- Created `custom/compass-skills/` module with 35 Compass-only workflow skills + 8 Compass-only agents across phase directories (0-governance, 1-analysis, 2-plan-workflows, 3-solutioning, 4-implementation, anytime, documentation, planning)
- Created `custom/core-skills/` with BMad Master agent + brainstorming and party-mode overrides + 2 Compass-only workflows (advanced-elicitation, autonomous-refinement-loop)
- Audited all 18 upstream workflow overrides — all had meaningful differences, created 22 override skills in `custom/bmm-skills/`
- Moved `bmad-builder` from staging to `custom/bmad-builder-skills/` (3 agents + workflow templates)
- Merged `test-architecture` knowledge into `compass-skills/4-implementation/_tea-knowledge/`
- Moved data (project-context-template) and teams configs to `compass-skills/_resources/`
- Removed `buildBmadCompat()` from build.js (kept `_config/` copy temporarily)
- Removed old validation functions (validateCustomBmadAgentExecPaths, validateBmadReferenceCsvs) + dead code
- Deleted `custom/bmm/`, `custom/core/`, `reference/migration-staging/`

**Deferred to Phase 4:** `src/bmad/_config/` (bmad-help.csv, agent-manifest.csv) still exists and is copied to dist — native skills reference these at runtime. Phase 4 will auto-generate replacements.

---

### Phase 4: Manifest Migration ✅

**Status:** Complete (PR #78, 2026-04-07)

**Scope:** Switch from hand-maintained CSVs to build-generated manifests.

**What was done:**
- Added `parseSimpleYaml()` and `listFilesRecursive()` helpers to build.js
- Added `generateAgentManifest()` — walks dist for `bmad-skill-manifest.yaml` where `type: agent`, generates `_config/agent-manifest.csv` (21 agents)
- Added `generateBmadHelp()` — dynamically discovers modules, concatenates `module-help.csv` files into unified `_config/bmad-help.csv` (44 skills from 4 modules)
- Added `generateSkillManifest()` — walks all SKILL.md files, generates `_config/skill-manifest.csv` (92 skills)
- Deleted `src/bmad/_config/` (hand-maintained bmad-help.csv + agent-manifest.csv)
- Added `validateGeneratedManifests()` to validate.js — checks agent skills have `bmad-skill-manifest.yaml`
- Added `validateModuleHelpDeps()` to validate.js — validates `after`/`before` dependency refs resolve to real skills (handles column misalignment + skill:action notation)
- Updated build `validateBuild()` with requiredChecks for all 3 generated manifests
- Updated 7 files with stale `src/bmad/_config/` references

**Known limitation:** `sync-client-bundles.js` is broken (reads old 16-column format, new is 13-column). Existing pre-generated command files remain functional. Phase 5 replaces the script.

---

### Phase 5: Client Bundle Generation

**Scope:** Replace command-based client bundles with skill-based bundles.

**Current state after Phase 4:**
- `sync-client-bundles.js` still generates old-format command `.md` files in `src/claude/commands/bmad/` and `src/opencode/commands/bmad/`
- Excalidraw workflows exist in upstream `bmm-skills/` but have no client commands (removed in Phase 1)

**Work:**
- Add client skill generation to `build.js`: walk merged `dist/_bmad/`, generate `dist/.claude/skills/`, `dist/.opencode/skills/`, `dist/.codex/skills/` with skill directories per platform
- Follow upstream naming: `bmad-agent-bmm-analyst/SKILL.md`, `bmad-bmm-create-product-brief/SKILL.md`, `bmad-compass-threat-modeling/SKILL.md`
- Restore excalidraw commands (now generated from upstream module-help.csv automatically)
- Update orchestrator agent files for each client
- Remove old `src/claude/commands/bmad/`, `src/opencode/commands/bmad/` directories
- Remove `tools/sync-client-bundles.js`
- Update `src/codex/` prompts to reference skills instead of commands

**Exit criteria:** Client bundles use skill format. Old command directories removed. `sync-client-bundles.js` deleted. All clients functional.
