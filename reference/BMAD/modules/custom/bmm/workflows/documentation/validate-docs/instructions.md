# Validate Docs Workflow

<critical>The workflow engine is governed by: {project-root}/_bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and resolved: {project-root}/_bmad/bmm/workflows/documentation/validate-docs/workflow.yaml</critical>
<critical>Communicate all responses in {communication_language}</critical>

## Goal

Validate documentation against Compass required structure and embedded documentation policies.

## Step 1: Validate Required Structure

Verify presence of required layout:

- `{docs_root}/README.md`
- `{docs_architecture_dir}/README.md`
- `{docs_architecture_decisions_dir}/README.md`
- `{docs_development_dir}/README.md`
- `{docs_getting_started_dir}/README.md`
- `{docs_getting_started_dir}/installation.md`
- `{docs_getting_started_dir}/quickstart.md`
- `{docs_guides_dir}/README.md`
- `{docs_reference_dir}/README.md`

## Step 2: Validate Policy Baseline Sync

- confirm baseline policy files exist in `{docs_human_policies_dir}`
- confirm baseline templates exist in `{docs_human_templates_dir}`
- confirm overrides file exists at `{docs_human_overrides_file}`

## Step 3: Validate Quality Rules

Check for:

- README presence at each docs directory level
- relative internal links
- naming conventions (lowercase kebab-case for docs files)
- ADR naming convention under decisions (`0001-topic.md` pattern when ADRs exist)

## Step 4: Emit Validation Report

Write `{default_output_file}` with sections:

1. Structure checks (pass/fail)
2. Policy/template sync checks (pass/fail)
3. Quality checks (pass/warn/fail)
4. Blocking issues
5. Recommended remediation order

## Step 5: Gate Recommendation

End with gate recommendation:

- `PASS` if no blocking issues
- `CONCERNS` if only warnings
- `FAIL` if structure or policy blockers exist
