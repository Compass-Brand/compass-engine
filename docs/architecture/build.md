# Build Process

How compass-engine builds and distributes configuration.

## Overview

```
src/                      →  build.js  →  dist/.claude/
├── claude/agents/                         ├── agents/
├── claude/commands/                       ├── commands/
├── claude/skills/                         ├── skills/
├── claude/rules/                          ├── rules/
├── claude/contexts/                       ├── contexts/
├── claude/config/                         ├── config/
├── claude/scripts/                        ├── scripts/
└── claude/templates/                      ├── settings.json
                                           └── README.md
```

## Build Command

```bash
npm run build
# or
node scripts/build.js
```

## What the Build Does

1. **Clean**: Removes existing `dist/.claude/`
2. **Copy**: Copies all directories from `src/claude/` to `dist/.claude/`
3. **Generate Settings**: Creates `settings.json` from template
4. **Copy Hooks**: Copies hook scripts from `src/scripts/claude/hooks/`
5. **Generate README**: Creates a README for the distributed config
6. **Validate**: Verifies required directories exist and have content

## Build Output

```
dist/.claude/
├── agents/                 # Agent definitions
├── commands/               # Slash commands
│   └── bmad/               # BMAD-specific commands
├── skills/                 # Skill definitions
├── rules/                  # Governance rules
├── contexts/               # Context modes
├── config/                 # Configuration files
├── scripts/                # Hook scripts
├── settings.json           # Default settings
├── settings.local.json.example  # Local settings template
└── README.md               # Generated documentation
```

## Files Not Included in Build

These files are intentionally excluded:

- `src/bmad/` - BMAD customizations (stay in compass-engine)
- `src/customizations/` - System prompt overrides (stay in compass-engine)
- `src/scripts/workflow/` - Workflow scripts (distributed separately)

## Push Command

After building, push to projects:

```bash
# Push to current directory
npm run push

# Push to specific project
npm run push -- --project /path/to/project

# Push to all discovered projects
npm run push -- --all

# Dry run (show what would happen)
npm run push -- --dry-run
```

## Local-Only Preservation

These paths are preserved during push (not overwritten):

- `settings.local.json` - Machine-specific settings
- `scratchpad/` - User workspace files
- `commands/local/` - Project-specific commands

## Automated Distribution

The build and push can be automated:

```bash
# Full distribution to all projects
npm run build && npm run push -- --all
```

## Integration with compass-brand-setup

The compass-brand-setup installer runs:

1. `npm run build` in compass-engine
2. Distributes `dist/.claude/` to all projects during setup

## Troubleshooting

### Build fails with "directory not found"

Ensure `src/claude/` directories exist:

```bash
mkdir -p src/claude/{agents,commands,skills,rules,contexts,config,scripts,templates}
```

### Push fails with permission errors

Check file ownership in target project:

```bash
ls -la /path/to/project/.claude
```

### Changes not appearing after push

1. Verify build completed: `ls dist/.claude/`
2. Check push output for errors
3. Ensure target isn't in LOCAL_ONLY_PATHS
