# Manual Config Bootstrap — `_bmad/{module}/config.yaml`

BMAD skills and agents read their project configuration from flat YAML files at `_bmad/{module}/config.yaml` inside each target project. Before BMAD v6.3.0, Compass Brand's `bmad-init` skill created these files lazily on first invocation. Starting with v6.3.0 upstream removed that bootstrap path, so Compass Engine owns the bootstrap via `compass-engine init`.

This runbook is the source of truth for default values and manual recovery steps. Keep it in sync with `tools/init/` — if a default changes in the Node pipeline, update this file in the same commit.

## When you need this

- Fresh Compass Brand project scaffold — `_bmad/` is empty.
- Existing project upgrading past `bmad-engine-lg73` Task 11 — the old lazy-bootstrap Python is gone.
- Broken or missing config files on a machine that rolled back a bad change.
- CI verification that a project is ready to run BMAD skills (check for `_bmad/core/config.yaml` first).

## Default recipe

### `compass-engine init` (preferred)

```bash
# From the target project root:
compass-engine init

# Or explicitly, from anywhere:
compass-engine init --project-root /path/to/target-project

# Flags:
#   --modules core,bmm     Which modules to bootstrap (default: core,bmm).
#   --interactive          Prompt for each value; empty input = accept default.
#   --force                Overwrite existing config files (destructive).
#   --dry-run              Print intended writes; do not touch the filesystem.
```

Behavior:

- Refuses to overwrite existing `_bmad/{module}/config.yaml` unless `--force`.
- Skips modules whose `module.yaml` declares no user-facing variables (currently `compass`, `bmad-builder` — they read from `_bmad/core/config.yaml`).
- Creates directories declared under `directories:` in each module's `module.yaml` (e.g., `_bmad-output/planning-artifacts`).

### Chained from `compass-engine push`

`push --init` bootstraps configs immediately after delivery, which is the right call for first-time pushes into a fresh project:

```bash
compass-engine push --project /path/to/new-project --targets bmad --init
```

Re-pushes into projects that already have configs are no-ops for init (the writer refuses to overwrite).

## Default values (authoritative snapshot)

Captured before `bmad-engine-lg73` Task 11 deletes `src/bmad/modules/native/core-skills/bmad-init/`. After that deletion, these values live only here and in `tools/init/schema-loader.js` + each module's `module.yaml`.

### `_bmad/core/config.yaml`

| Variable                   | Default template         | Resolved example (`--project-root=/srv/proj`)     |
| -------------------------- | ------------------------ | -------------------------------------------------- |
| `user_name`                | `BMad`                   | `BMad`                                             |
| `communication_language`   | `English`                | `English`                                          |
| `document_output_language` | `English`                | `English`                                          |
| `output_folder`            | `_bmad-output`           | `/srv/proj/_bmad-output`                           |

### `_bmad/bmm/config.yaml`

Merges the core values above, then layers BMM-specific values:

| Variable                   | Default template                            | Resolved example                                   |
| -------------------------- | ------------------------------------------- | -------------------------------------------------- |
| `project_name`             | `{directory_name}`                          | `proj`                                             |
| `user_skill_level`         | `intermediate` (single-select)              | `intermediate`                                     |
| `planning_artifacts`       | `{output_folder}/planning-artifacts`        | `/srv/proj/_bmad-output/planning-artifacts`        |
| `implementation_artifacts` | `{output_folder}/implementation-artifacts`  | `/srv/proj/_bmad-output/implementation-artifacts`  |
| `project_knowledge`        | `docs`                                      | `/srv/proj/docs`                                   |

`user_skill_level` single-select options: `beginner`, `intermediate`, `expert`.

Directories created automatically for BMM:

- `{planning_artifacts}`
- `{implementation_artifacts}`
- `{project_knowledge}`

### Skipped modules

- `compass` — declares no user-facing variables. Its agents read `_bmad/core/config.yaml`.
- `bmad-builder` — same story.

If a future module grows user-facing variables, add it to the `DEFAULT_MODULES` list in `tools/init.js` and update this table.

## Manual recovery — writing configs by hand

Use this only when `compass-engine init` is unavailable (air-gapped host, node toolchain missing, etc.). Values below assume project root `/srv/proj`:

```yaml
# _bmad/core/config.yaml
# CORE Module Configuration
user_name: BMad
communication_language: English
document_output_language: English
output_folder: /srv/proj/_bmad-output
```

```yaml
# _bmad/bmm/config.yaml
# BMM Module Configuration
user_name: BMad
communication_language: English
document_output_language: English
output_folder: /srv/proj/_bmad-output
project_name: proj
user_skill_level: intermediate
planning_artifacts: /srv/proj/_bmad-output/planning-artifacts
implementation_artifacts: /srv/proj/_bmad-output/implementation-artifacts
project_knowledge: /srv/proj/docs
```

Create the declared directories manually:

```bash
mkdir -p /srv/proj/_bmad-output/planning-artifacts
mkdir -p /srv/proj/_bmad-output/implementation-artifacts
mkdir -p /srv/proj/docs
```

## Migrating an existing Compass project

Projects scaffolded before the `bmad-engine-the2` rollout have no `_bmad/{core,bmm}/config.yaml` — skills were falling back to the now-removed lazy bootstrap. Run:

```bash
cd /path/to/existing-project
compass-engine init
```

The init writer refuses to overwrite, so this is additive and safe. If a previous operator wrote custom values that drifted from defaults and you want to reset them, first back up then:

```bash
compass-engine init --force
```

## Related work

- Plan: `docs/plans/2026-04-15-bmad-v6.3-installer-bootstrap.md` (on `docs/bmad-v6.3-alignment-plans`).
- Beads: `bmad-engine-the2` (this work) BLOCKS `bmad-engine-lg73` Task 11.
- Pipeline source: `tools/init.js`, `tools/init/schema-loader.js`, `tools/init/default-resolver.js`, `tools/init/config-writer.js`.
