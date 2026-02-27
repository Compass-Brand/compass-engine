# Update Docs Workflow

<critical>The workflow engine is governed by: {project-root}/_bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and resolved: {project-root}/_bmad/bmm/workflows/documentation/update-docs/workflow.yaml</critical>
<critical>Communicate all responses in {communication_language}</critical>

## Goal

Apply incremental documentation updates across `{docs_root}` based on current phase artifacts and selected update scope.

## Step 1: Discover Current Inputs

Load current artifacts from:

- `{current_prd_dir}`
- `{current_ux_dir}`
- `{current_architecture_dir}`
- `{current_epics_dir}`
- `{current_story_dir}`
- `{current_evidence_dir}`
- `{current_testing_dir}`
- `{current_research_dir}`

## Step 2: Determine Delta Targets

Map discovered deltas to docs destinations:

- architecture and technical decisions -> `{docs_architecture_dir}`
- implementation process updates -> `{docs_development_dir}`
- onboarding or run instructions -> `{docs_getting_started_dir}`
- operator/developer guides -> `{docs_guides_dir}`
- reference artifacts, inventories, validation records -> `{docs_reference_dir}`

## Step 3: Apply Updates

1. Update only sections impacted by current deltas.
2. Preserve existing valid content unless stale or contradictory.
3. Ensure all modified docs remain aligned to policy files in `{docs_human_policies_dir}`.

## Step 4: Maintain Navigation

- Update `README.md` files for changed directories.
- Ensure new documents are linked from parent indexes.
- Ensure links remain relative.

## Step 5: Capture Report

Write `{default_output_file}` including:

- update scope
- files changed
- source artifacts used
- unresolved documentation gaps
- recommendation to run `/bmad-bmm-validate-docs`
