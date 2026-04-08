# Creating BMAD Modules

Last reviewed: 2026-04-08

How to create new BMAD modules for the Compass Engine distribution system.

## What Is a Module?

A module is a self-contained group of related BMAD skills (workflows and agents) organized by phase. Modules are the primary unit of composition — they package domain-specific capabilities and register them in the help system.

## Module Types

| Type | Location | Build Behavior |
| --- | --- | --- |
| Native + Custom | `modules/native/{name}` + `modules/custom/{name}` | Merged (custom overlays native) |
| Custom-Only | `modules/custom/{name}` | Copied directly to dist |

Native modules come from upstream BMAD-METHOD. Custom modules are Compass-specific. Most new modules will be custom-only.

## Quick Start: Scaffold a Module

```bash
npm run create:bmad-module -- --name my-module --code mymod
```

This creates `src/bmad/modules/custom/my-module-skills/` with a scaffolded `module.yaml` and `custom-module.json` metadata.

To scaffold from an existing upstream module as a starting point:

```bash
npm run create:bmad-module -- --name my-module --from bmm --code mymod
```

## Module Anatomy

```text
src/bmad/modules/custom/{module-name}-skills/
├── module.yaml                 # Module manifest (required)
├── module-help.csv             # Skill catalog for help system (required)
├── 0-governance/               # Phase 0 skills
├── 1-analysis/                 # Phase 1 skills
├── 2-plan-workflows/           # Phase 2 skills
├── 3-solutioning/              # Phase 3 skills
├── 4-implementation/           # Phase 4 skills
├── anytime/                    # Always-available skills
├── documentation/              # Documentation-related skills
├── planning/                   # Planning-related skills
└── _resources/                 # Supporting resources (not skills)
```

Not all phase directories are required. Include only the phases your module covers.

## module.yaml

The module manifest defines identity and optional configuration:

```yaml
code: mymod
name: "My Module"
description: "Domain-specific workflows for X"
default_selected: false
```

### Optional Configuration Variables

Modules can define interactive configuration prompts for installation:

```yaml
my_setting:
  prompt: "What is your preferred X?"
  default: "default-value"
  result: "{my_setting}"

my_choice:
  prompt: "Select a mode:"
  default: "standard"
  single-select:
    - value: "standard"
      label: "Standard Mode"
    - value: "advanced"
      label: "Advanced Mode"
```

### Optional Directory Creation

Modules can request directories be created during installation:

```yaml
directories:
  - "planning/custom/{project_name}/"
```

## module-help.csv

The help catalog registers all module skills with the BMAD help system. This file drives CLI menus, routing, and the aggregated `bmad-help.csv`.

### Format

```csv
module,skill,display-name,menu-code,description,action,args,phase,after,before,required,output-location,outputs
```

### Example Rows

```csv
My Module,bmad-mymod-analyze,Analyze Domain,AD,Run domain analysis for X,,,1-analysis,,,false,research_artifacts,domain analysis report
My Module,bmad-mymod-design,Design Solution,DS,Create solution design for X,,,3-solutioning,bmad-mymod-analyze,,false,planning_artifacts,solution design
```

### Field Reference

| Field | Required | Description |
| --- | --- | --- |
| module | Yes | Module display name |
| skill | Yes | Skill name (must match SKILL.md `name` field) |
| display-name | Yes | Human-readable name for menus |
| menu-code | Yes | 1-2 letter quick invocation code |
| description | Yes | Brief description |
| action | No | Sub-action type (create, validate, update, etc.) |
| args | No | CLI arguments the skill accepts |
| phase | Yes | `anytime`, `1-analysis`, `2-plan-workflows`, `3-solutioning`, `4-implementation` |
| after | No | Skill that must complete first (dependency) |
| before | No | Skill that should follow (ordering hint) |
| required | No | `true` if part of the required progression chain |
| output-location | No | Directory template for generated artifacts |
| outputs | No | Types of artifacts produced |

## Adding Skills to a Module

See [Creating Skills](./creating-skills.md) for the full guide. In summary:

1. Create the skill directory under the appropriate phase folder
2. Add `SKILL.md` with frontmatter
3. Add `workflow.md` (and optional `steps/`) for workflows, or inline persona for agents
4. Add a row to `module-help.csv`

## Build Integration

### How the Build Discovers Modules

The build system (`tools/build.js`) has two module lists:

```javascript
// Modules with native + custom layers (merged)
SKILL_MODULES = [
  { name: 'bmm', native: 'native/bmm-skills', custom: 'custom/bmm-skills', dist: '_bmad/bmm' },
  { name: 'core', native: 'native/core-skills', custom: 'custom/core-skills', dist: '_bmad/core' }
]

// Custom-only modules (copied directly)
CUSTOM_ONLY_MODULES = [
  { name: 'compass', src: 'custom/compass-skills', dist: '_bmad/compass' },
  { name: 'bmad-builder', src: 'custom/bmad-builder-skills', dist: '_bmad/bmad-builder' }
]
```

To register a new custom-only module, add an entry to `CUSTOM_ONLY_MODULES` in `tools/build.js`.

### Build Outputs

For each module, the build system:

1. Copies skill directories to `dist/_bmad/{module-code}/`
2. Scans all `SKILL.md` files and adds entries to `dist/_bmad/_config/skill-manifest.csv`
3. Scans all `bmad-skill-manifest.yaml` files (agents) and adds entries to `dist/_bmad/_config/agent-manifest.csv`
4. Concatenates `module-help.csv` into `dist/_bmad/_config/bmad-help.csv`
5. Generates client skill wrappers for Claude/OpenCode/Codex

### Client Skill Naming

The build applies module-specific naming transformations:

| Module Code | Input Skill Name | Generated Client Name |
| --- | --- | --- |
| bmm | `bmad-create-prd` | `bmad-bmm-create-prd` |
| core | `bmad-brainstorming` | `bmad-brainstorming` |
| compass | `bmad-compass-my-skill` | `bmad-compass-my-skill` |
| bmad-builder | `bmad-module-builder` | `bmad-builder-module-builder` |
| mymod (new) | `bmad-mymod-analyze` | `bmad-mymod-analyze` |

The exact transformation logic is in `clientSkillName()` in `tools/build.js`. New modules may need a naming rule added there.

## Validation

```bash
npm run validate && npm run build
```

Validation checks:

- Required source paths exist
- No hardcoded secrets in config files
- All SKILL.md files have valid frontmatter

After building, inspect `dist/_bmad/_config/` to verify your module's skills appear in:

- `skill-manifest.csv`
- `bmad-help.csv`
- `agent-manifest.csv` (if module includes agents)

## Distribution

Push the built module to downstream projects:

```bash
# Preview
npm run push -- --targets bmad --dry-run

# Push to all projects
npm run push -- --targets bmad --all

# Push to a specific project
npm run push -- --targets bmad --project /path/to/repo
```

## Using the Module Builder Agent

For interactive module creation, use the BMad Builder agent Morgan:

```text
/bmad-builder-module-builder
```

Morgan provides guided workflows:

| Code | Action |
| --- | --- |
| PB | Create product brief for module development |
| CM | Create a complete BMAD module (agents, workflows, infrastructure) |
| EM | Edit an existing BMAD module |
| VM | Validate a module against best practices |
| MH | Generate or update module-help.csv |

## Related Documentation

- [BMAD Overview](./bmad-overview.md) — method and architecture introduction
- [Creating Skills](./creating-skills.md) — workflow and agent skill anatomy
- [Custom Modules](./custom-modules.md) — Compass module principles
- [Build Process](../../architecture/build.md) — build pipeline details
