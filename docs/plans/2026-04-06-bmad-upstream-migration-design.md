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
│       │   │   ├── bmad-compass-design-delivery/
│       │   │   └── bmad-agent-wds-designer/
│       │   ├── 3-solutioning/
│       │   │   ├── bmad-compass-threat-modeling/
│       │   │   ├── bmad-compass-security-architecture-review/
│       │   │   └── bmad-agent-security-architect/
│       │   ├── 4-implementation/
│       │   │   ├── bmad-compass-secure-gates/
│       │   │   ├── bmad-compass-implementation-brainstorming/
│       │   │   ├── bmad-compass-implementation-research/
│       │   │   └── bmad-compass-testarch-*/  (9 TEA workflows)
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
    └── skill-manifest.csv   # Generated: all skills from all modules
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

### build.js

1. **Module walker** — Discovers skill directories by finding `SKILL.md` files. Replaces flat directory copy.
2. **Native/custom merge** — Walks `native/{module}-skills/` first, overlays `custom/{module}-skills/`. Same-named skill directory = custom wins (full replacement).
3. **Custom-only modules** — `compass-skills/` and `bmad-builder-skills/` copy directly. No merge.
4. **Manifest generation** — Walks merged `dist/_bmad/`, collects `bmad-skill-manifest.yaml` files, generates `agent-manifest.csv` and `skill-manifest.csv`.
5. **Client skill generation** — Replaces `sync-client-bundles.js`. Generates skill directories for each client platform from merged module tree.
6. **Module-help merge** — Concatenates per-module `module-help.csv` files into unified `_config/bmad-help.csv`.

### validate.js

Updates to check:
- Every skill directory has a `SKILL.md`
- Skill directory name matches SKILL.md `name:` frontmatter
- Agent skills have `bmad-skill-manifest.yaml`
- Internal path references use relative paths (no hardcoded `_bmad/` absolute paths)
- Module-help.csv `after`/`before` references resolve to real skills

### sync-client-bundles.js → removed

Replaced by client skill generation step in `build.js`.

### push.js

Unchanged — operates on `dist/` which is just a different shape.

---

## Migration Phases

### Phase 1: Native Module Restructure + Build Foundation

**Scope:** Largest phase. Establishes the new directory structure and build system.

- Pin BMAD-METHOD submodule to `v6.2.2` tag
- Copy `BMAD-METHOD/src/bmm-skills/` → `src/bmad/modules/native/bmm-skills/`
- Copy `BMAD-METHOD/src/core-skills/` → `src/bmad/modules/native/core-skills/`
- Remove old `src/bmad/modules/native/bmm/` and `src/bmad/modules/native/core/`
- Update `build.js`: skill directory walker, native/custom merge, flat dist output
- Update `validate.js` for skill format checks
- Temporary compatibility: old custom modules copy as-is until Phases 2-3 convert them

**Exit criteria:** `npm run build` produces valid `dist/_bmad/` with upstream skill layout. `npm run validate` passes.

### Phase 2: Convert Custom BMM Overrides

**Scope:** Convert Compass agent persona overrides to skill format.

- Convert ~9 agent overrides from `.agent.yaml` to `SKILL.md` + `bmad-skill-manifest.yaml`
- Place in `custom/bmm-skills/` mirroring upstream phase directories
- Validate build merges them correctly (custom persona replaces native)

**Exit criteria:** All custom agent overrides in skill format. Build produces merged agents with Compass personas.

### Phase 3: Create compass-skills Module

**Scope:** Convert all Compass-only content to skill format.

- Create `custom/compass-skills/` with `module.yaml` and `module-help.csv`
- Convert governance, security, WDS, CIS, TEA, documentation, planning workflows
- Convert custom-only agents (wds-designer, wds-analyst, security-architect, threat-analyst, tea, etc.)
- Move bmad-builder to `custom/bmad-builder-skills/`
- Remove old `src/bmad/modules/custom/bmm/` and `src/bmad/modules/custom/core/`
- Remove compatibility shim from Phase 1

**Exit criteria:** All custom content in skill format. No old-format files remain.

### Phase 4: Manifest Migration

**Scope:** Switch to build-generated manifests and new CSV format.

- Migrate `module-help.csv` files to 13-column format with `after`/`before` dependency graph
- Remove hand-maintained `workflow-manifest.csv`, `task-manifest.csv`, `bmad-help.csv`
- Build now generates `agent-manifest.csv` and `skill-manifest.csv` from module tree
- Update orchestrator and help system to use new manifest format

**Exit criteria:** No hand-maintained manifests. All manifests build-generated. Dependency graph validates.

### Phase 5: Client Bundle Generation

**Scope:** Replace command-based client bundles with skill-based bundles.

- Replace `sync-client-bundles.js` with skill-file generation in `build.js`
- Generate `.claude/skills/`, `.opencode/skills/`, `.codex/skills/` from merged module tree
- Update orchestrator agents and skill files per client
- Remove old `src/claude/commands/`, `src/opencode/commands/` directories
- Remove `sync-client-bundles.js`

**Exit criteria:** Client bundles use skill format. Old command directories removed. All clients functional.
