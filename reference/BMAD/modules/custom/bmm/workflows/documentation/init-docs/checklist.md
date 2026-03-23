# Init Docs Checklist

## Preconditions

- [ ] `docs_root` resolves to `{project-root}/docs`
- [ ] `snapshot_date` is `YYYY-MM-DD`
- [ ] Migration snapshot path is under `{docs_tmp_migration_root}`

## Migration Safety

- [ ] Legacy docs moved to dated snapshot before transformation
- [ ] Snapshot preserves original relative paths
- [ ] Migration manifest created

## Structure Compliance

- [ ] Required `docs/*` tree exists
- [ ] `README.md` exists at each docs directory level
- [ ] `docs/getting-started/installation.md` exists
- [ ] `docs/getting-started/quickstart.md` exists

## Policy and Templates

- [ ] Baseline policies synced to `{docs_human_policies_dir}`
- [ ] Baseline templates synced to `{docs_human_templates_dir}`
- [ ] AI domain README synced to `{docs_ai_root}`
- [ ] Overrides file exists at `{docs_human_overrides_file}`
- [ ] `docs/README.md` includes maintenance ownership and review cadence
- [ ] Docs ownership model is recorded in the docs index or equivalent root docs note

## Outputs

- [ ] Initialization report written to `{default_output_file}`
- [ ] Manifest written to `{migration_manifest}`
- [ ] Lifecycle and promotion gaps are captured when migration cannot fully normalize them
