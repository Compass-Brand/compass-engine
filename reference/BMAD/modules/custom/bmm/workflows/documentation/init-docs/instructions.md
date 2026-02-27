# Initialize Docs Workflow

<critical>The workflow engine is governed by: {project-root}/_bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and resolved: {project-root}/_bmad/bmm/workflows/documentation/init-docs/workflow.yaml</critical>
<critical>Communicate all responses in {communication_language}</critical>

## Goal

Migrate existing repository documentation into Compass opinionated documentation layout under `{docs_root}` while preserving all legacy content in a dated migration snapshot under `{docs_tmp_migration_root}`.

## Step 1: Preflight and Snapshot Date

1. Resolve `snapshot_date` in `YYYY-MM-DD` format.
2. Set `snapshot_root` = `{docs_tmp_migration_root}/{snapshot_date}`.
3. Confirm migration mode with user:
   - default: keep migration snapshot indefinitely
   - optional cleanup allowed only when explicitly requested and `docs_tmp_cleanup_enabled` is true

## Step 2: Discover Existing Docs Inputs

Discover all documentation candidates to migrate:

- root-level docs: `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `LICENSE`
- folder docs: `docs/**`, `documentation/**`, `reference/documentation/**`
- any markdown files in top-level operational folders that clearly function as product documentation

Produce a candidate list before moving files.

## Step 3: Move Legacy Docs to Snapshot

1. Create `{snapshot_root}`.
2. Move discovered legacy docs into the snapshot, preserving relative structure.
3. Do not delete snapshot content after move.
4. Record moved paths in `{migration_manifest}`.

## Step 4: Scaffold Required Docs Structure

Ensure all required Compass docs directories and index files exist:

- `{docs_root}/README.md`
- `{docs_architecture_dir}/README.md`
- `{docs_architecture_decisions_dir}/README.md`
- `{docs_development_dir}/README.md`
- `{docs_getting_started_dir}/README.md`
- `{docs_getting_started_dir}/installation.md`
- `{docs_getting_started_dir}/quickstart.md`
- `{docs_guides_dir}/README.md`
- `{docs_reference_dir}/README.md`

## Step 5: Sync Built-In Policy and Template Assets

1. Copy baseline policy files from `{docs_framework_human_policies_dir}` to `{docs_human_policies_dir}`.
2. Copy baseline templates from `{docs_framework_human_templates_dir}` to `{docs_human_templates_dir}`.
3. Copy `{docs_framework_ai_root}/README.md` to `{docs_ai_root}/README.md` if missing.
4. Ensure `{docs_human_overrides_file}` exists with placeholder content if missing.

## Step 6: Transform Legacy Content into Target Structure

Using moved source material in `{snapshot_root}`, generate structured docs under `{docs_root}`:

- architecture outputs -> `{docs_architecture_dir}` and `{docs_architecture_decisions_dir}`
- development/setup outputs -> `{docs_development_dir}` and `{docs_getting_started_dir}`
- guides/how-tos/tutorials -> `{docs_guides_dir}`
- inventories, API, data models, deep dives, migration logs -> `{docs_reference_dir}`

When useful, reuse native extraction heuristics from:

- `{legacy_requirements_csv}`
- `{legacy_full_scan_instructions}`
- `{legacy_deep_dive_instructions}`

## Step 7: Build Navigation and Cross-links

1. Update `{docs_root}/README.md` to index major docs sections.
2. Ensure each docs subdirectory `README.md` links to contained docs.
3. Ensure internal links are relative.

## Step 8: Emit Initialization Report

Write `{default_output_file}` including:

- snapshot path
- migrated inputs count
- generated/updated outputs count
- unresolved migration gaps
- recommended follow-up command: `/bmad-bmm-update-docs`

## Step 9: Optional Cleanup (Explicit Only)

If user explicitly requests cleanup and `docs_tmp_cleanup_enabled` is true, remove the selected snapshot folder. Otherwise keep `{snapshot_root}` unchanged.
