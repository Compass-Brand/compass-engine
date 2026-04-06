# Phase 1: Native Module Restructure + Build Foundation

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the old module-based native directory structure with upstream BMAD v6.2.2's skill-based layout and update the build system to produce a flat `dist/_bmad/` output matching upstream's installed format.

**Architecture:** Pin the BMAD-METHOD submodule to v6.2.2, copy its `bmm-skills/` and `core-skills/` into `src/bmad/modules/native/`, update `build.js` to walk skill directories and merge native/custom with custom-wins semantics, and add a temporary compatibility layer so old-format custom modules continue building until Phases 2-3 convert them.

**Tech Stack:** Node.js 18+ ESM, `fs/promises`, CSV parsing, no external dependencies.

**Validation approach:** This project has no test framework. Validation is done via `node tools/validate.js` and `node tools/build.js` which check path existence, manifest integrity, and build output. These are the "tests."

---

## Context for Implementers

### Repository layout

- `BMAD-METHOD/` — git submodule pointing to upstream BMAD-METHOD repo
- `src/bmad/modules/native/` — copies of upstream content (currently old format: `bmm/`, `core/`)
- `src/bmad/modules/custom/` — Compass overrides and custom content (old format, stays unchanged in Phase 1)
- `tools/build.js` — builds `dist/` from `src/`
- `tools/validate.js` — validates source integrity
- `tools/sync-client-bundles.js` — generates client commands from `bmad-help.csv`

### Upstream v6.2.2 skill format

Every skill is a directory containing at minimum a `SKILL.md` file:

```
bmad-create-product-brief/
├── SKILL.md                    # Entry point with name/description frontmatter
├── workflow.md                 # Orchestration logic (optional)
├── bmad-skill-manifest.yaml    # Agent metadata (agents only, most use this name)
├── bmad-manifest.json          # Alternative manifest format (bmad-product-brief uses this)
└── steps/                      # Micro-step files (optional)
    ├── step-01-init.md
    └── step-02-discovery.md
```

Modules are organized by phase: `1-analysis/`, `2-plan-workflows/`, `3-solutioning/`, `4-implementation/`.

**Important:** Phase directories may contain non-skill content alongside skill directories. For example, `2-plan-workflows/create-prd/` has no SKILL.md but contains 164KB of legacy validation steps referenced by other skills. The build must copy ALL content from phase directories, not just skill directories.

**Note:** Two core skills (`bmad-distillator`, `bmad-init`) include Python scripts in `scripts/` subdirectories with tests.

### Key files to read before starting

- `docs/plans/2026-04-06-bmad-upstream-migration-design.md` — full design document
- `tools/build.js` — current build script (you'll be modifying this)
- `tools/validate.js` — current validation script (you'll be modifying this)
- `BMAD-METHOD/src/bmm-skills/module.yaml` — upstream module definition
- `BMAD-METHOD/src/bmm-skills/module-help.csv` — upstream 13-column manifest

---

## Task 1: Pin BMAD-METHOD Submodule to v6.2.2

**Files:**
- Modify: `BMAD-METHOD` (submodule pointer)

### Step 1: Update submodule to v6.2.2 tag

```bash
cd BMAD-METHOD
git fetch origin --tags
git checkout v6.2.2
cd ..
```

### Step 2: Verify the checkout

```bash
cd BMAD-METHOD && git describe --tags --exact-match HEAD && cd ..
```

Expected: `v6.2.2`

### Step 3: Verify upstream structure exists

```bash
ls BMAD-METHOD/src/bmm-skills/module.yaml BMAD-METHOD/src/core-skills/module.yaml
```

Expected: both files exist.

### Step 4: Commit

```bash
git add BMAD-METHOD
git commit -m "chore: pin BMAD-METHOD submodule to v6.2.2

Update from dead-branch commit to official v6.2.2 tagged release.
This is the foundation for migrating to skill-based architecture.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Copy Upstream Skill Modules to Native

**Files:**
- Create: `src/bmad/modules/native/bmm-skills/` (entire directory, ~232 files)
- Create: `src/bmad/modules/native/core-skills/` (entire directory, ~40 files)

### Step 1: Copy bmm-skills from upstream

```bash
cp -r BMAD-METHOD/src/bmm-skills/ src/bmad/modules/native/bmm-skills/
```

### Step 2: Copy core-skills from upstream

```bash
cp -r BMAD-METHOD/src/core-skills/ src/bmad/modules/native/core-skills/
```

### Step 3: Verify the copy

```bash
# Check key files exist
ls src/bmad/modules/native/bmm-skills/module.yaml
ls src/bmad/modules/native/bmm-skills/module-help.csv
ls src/bmad/modules/native/core-skills/module.yaml
ls src/bmad/modules/native/core-skills/module-help.csv

# Count SKILL.md files (expected: 31 bmm + 12 core = 43)
find src/bmad/modules/native/bmm-skills -name "SKILL.md" | wc -l
find src/bmad/modules/native/core-skills -name "SKILL.md" | wc -l
```

Expected: 31 and 12.

### Step 4: Commit

```bash
git add src/bmad/modules/native/bmm-skills/ src/bmad/modules/native/core-skills/
git commit -m "feat: copy upstream v6.2.2 bmm-skills and core-skills to native

232 files in bmm-skills/ (31 skills: 9 agents + 22 workflows)
40 files in core-skills/ (12 skills: 2 workflows + 10 utilities)
These will replace the old native/bmm/ and native/core/ directories.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Add Module Merge Function to build.js

**Files:**
- Modify: `tools/build.js`

### Context

The current build copies `src/bmad/` to `dist/_bmad/` as a flat directory tree. The new build needs to:

1. Copy entire native module tree to output
2. Overlay entire custom module tree (custom files win)
3. Output flat module layout (`dist/_bmad/bmm/`, `dist/_bmad/core/`)

### Step 1: Add the `mergeModules` function

This function takes a native module path and optional custom module path, discovers skills in both, and copies them to the output directory. Custom skills with the same name replace native ones entirely.

```javascript
/**
 * Merge native and custom skill modules into a flat output directory.
 *
 * Strategy: Copy the ENTIRE native module tree first (preserving all content
 * including non-skill directories like create-prd/ which has legacy validation
 * steps). Then overlay the entire custom tree on top — custom files overwrite
 * native files of the same path. This ensures nothing is lost.
 *
 * Non-skill files at the module root (module.yaml, module-help.csv) are
 * copied from native first, then overwritten by custom if present.
 */
async function mergeModules(nativePath, customPath, outputPath) {
  await fs.mkdir(outputPath, { recursive: true });

  // Step 1: Copy the ENTIRE native module tree (all content, not just skills)
  if (await exists(nativePath)) {
    await copyDir(nativePath, outputPath);
  }

  // Step 2: Overlay the ENTIRE custom tree on top (custom files win)
  if (customPath && (await exists(customPath))) {
    await copyDir(customPath, outputPath);
  }
}
```

**Why this is simpler than skill-aware merging:** The old approach tried to discover individual skill directories and copy them selectively, which would silently lose non-skill content (e.g., `2-plan-workflows/create-prd/` has no SKILL.md but contains 164KB of validation steps used by other skills). Copying the entire tree then overlaying custom ensures nothing is lost. The custom-wins semantics still work because `copyDir` overwrites files at matching paths.

### Step 3: Run validation to make sure build.js still parses

```bash
node --input-type=module -e "await import('./tools/build.js')"
```

Expected: no syntax errors (exits cleanly).

### Step 4: Commit

```bash
git add tools/build.js
git commit -m "feat(build): add module merge function for skill-based layout

mergeModules() combines native + custom modules with custom-wins
semantics by copying the entire native tree then overlaying custom.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Add Skill-Based BMAD Build Target

**Files:**
- Modify: `tools/build.js`

### Context

Add a new `buildBmadSkills()` function that replaces the old flat-copy BMAD target. This function:
1. Merges `native/bmm-skills/` + `custom/bmm-skills/` → `dist/_bmad/bmm/`
2. Merges `native/core-skills/` + `custom/core-skills/` → `dist/_bmad/core/`
3. Copies custom-only modules directly (`compass-skills/` → `dist/_bmad/compass/`, etc.)
4. Runs a compatibility shim for old-format custom content that hasn't been converted yet

### Step 1: Add `buildBmadSkills` function

```javascript
const NATIVE_ROOT = path.join(SRC, 'bmad', 'modules', 'native');
const CUSTOM_ROOT = path.join(SRC, 'bmad', 'modules', 'custom');
const BMAD_DIST = path.join(DIST_ROOT, '_bmad');

const SKILL_MODULES = [
  {
    name: 'bmm',
    native: path.join(NATIVE_ROOT, 'bmm-skills'),
    custom: path.join(CUSTOM_ROOT, 'bmm-skills'),
    dist: path.join(BMAD_DIST, 'bmm'),
  },
  {
    name: 'core',
    native: path.join(NATIVE_ROOT, 'core-skills'),
    custom: path.join(CUSTOM_ROOT, 'core-skills'),
    dist: path.join(BMAD_DIST, 'core'),
  },
];

const CUSTOM_ONLY_MODULES = [
  {
    name: 'compass',
    src: path.join(CUSTOM_ROOT, 'compass-skills'),
    dist: path.join(BMAD_DIST, 'compass'),
  },
  {
    name: 'bmad-builder',
    src: path.join(CUSTOM_ROOT, 'bmad-builder-skills'),
    dist: path.join(BMAD_DIST, 'bmad-builder'),
  },
];

async function buildBmadSkills() {
  console.log('\nBuilding _bmad (skill-based)...');
  await fs.mkdir(BMAD_DIST, { recursive: true });

  // Copy root-level BMAD files (e.g., BMAD-workflow.md) that aren't part of any module
  // but are referenced by orchestrator agents at runtime (_bmad/BMAD-workflow.md)
  const bmadWorkflow = path.join(SRC, 'bmad', 'BMAD-workflow.md');
  if (await exists(bmadWorkflow)) {
    await fs.copyFile(bmadWorkflow, path.join(BMAD_DIST, 'BMAD-workflow.md'));
    console.log('  Copied BMAD-workflow.md');
  }

  // Merged modules (native + custom)
  for (const mod of SKILL_MODULES) {
    if (await exists(mod.native)) {
      console.log(`  Merging ${mod.name} (native + custom)...`);
      await mergeModules(mod.native, mod.custom, mod.dist);
    } else {
      console.log(`  Skipping ${mod.name}: native not found`);
    }
  }

  // Custom-only modules (direct copy)
  for (const mod of CUSTOM_ONLY_MODULES) {
    if (await exists(mod.src)) {
      console.log(`  Copying ${mod.name} (custom-only)...`);
      await copyDir(mod.src, mod.dist);
    } else {
      console.log(`  Skipping ${mod.name}: not found`);
    }
  }

  // Compatibility: copy old-format custom content that hasn't been migrated yet
  await buildBmadCompat();
}
```

### Step 2: Add `buildBmadCompat` compatibility shim

This function copies old-format custom content to the EXACT paths that `bmad-help.csv` references, so `sync-client-bundles.js` and other tools continue working. The CSV references paths like `_bmad/modules/custom/bmm/workflows/...`, so old content must exist at those paths in dist.

```javascript
/**
 * Temporary compatibility shim for old-format custom modules.
 *
 * CRITICAL: bmad-help.csv references paths like _bmad/modules/custom/bmm/workflows/...
 * and sync-client-bundles.js reads these paths. We MUST copy old custom content to
 * dist/_bmad/modules/custom/ (the exact paths the CSVs reference) so tools don't break.
 *
 * This function is removed in Phase 3 after all custom content is converted and
 * bmad-help.csv is replaced by per-module module-help.csv.
 */
async function buildBmadCompat() {
  const OLD_CUSTOM_BMM = path.join(CUSTOM_ROOT, 'bmm');
  const OLD_CUSTOM_CORE = path.join(CUSTOM_ROOT, 'core');

  // Only run if old-format custom directories still exist
  if (!(await exists(OLD_CUSTOM_BMM)) && !(await exists(OLD_CUSTOM_CORE))) {
    return;
  }

  console.log('  Applying old-format compatibility shim...');

  // Copy old custom content to the EXACT paths that bmad-help.csv references
  // (dist/_bmad/modules/custom/bmm/ and dist/_bmad/modules/custom/core/)
  if (await exists(OLD_CUSTOM_BMM)) {
    const compatDest = path.join(BMAD_DIST, 'modules', 'custom', 'bmm');
    await copyDir(OLD_CUSTOM_BMM, compatDest);
    console.log('    Copied old custom/bmm/ → modules/custom/bmm/');
  }

  if (await exists(OLD_CUSTOM_CORE)) {
    const compatDest = path.join(BMAD_DIST, 'modules', 'custom', 'core');
    await copyDir(OLD_CUSTOM_CORE, compatDest);
    console.log('    Copied old custom/core/ → modules/custom/core/');
  }

  // Copy old _config manifests for backward compatibility
  const oldConfig = path.join(SRC, 'bmad', '_config');
  if (await exists(oldConfig)) {
    const configDest = path.join(BMAD_DIST, '_config');
    await copyDir(oldConfig, configDest);
    console.log('    Copied old _config/ manifests');
  }
}
```

**Why `modules/custom/` not `_compat/`:** The `bmad-help.csv` CSV has hardcoded paths like `_bmad/modules/custom/bmm/workflows/...`. Tools like `sync-client-bundles.js` and `validateDistBmadReferences` resolve these against `dist/_bmad/`. If we put the content at a different path, every CSV and every tool that reads those CSVs would break. Keeping the exact path means zero changes to CSVs or downstream tools during Phase 1.

### Step 3: Update the `build()` function to use `buildBmadSkills`

In the `build()` function, replace the BMAD target in the `TARGETS` array loop with a call to `buildBmadSkills()`. Remove the `bmad` entry from `TARGETS` and call `buildBmadSkills()` directly before the target loop.

Replace in `build()`:
```javascript
// Old: for (const target of TARGETS) { await buildTarget(target); }
// New:
await buildBmadSkills();
for (const target of TARGETS) {
  await buildTarget(target);
}
```

And remove the `bmad` entry from the `TARGETS` array (the one with `src: path.join(SRC, 'bmad')` and `dist: path.join(DIST_ROOT, '_bmad')`).

### Step 4: Run the build

```bash
node tools/build.js
```

Expected: Build completes. `dist/_bmad/bmm/` contains skill directories from upstream. `dist/_bmad/modules/custom/bmm/` contains old custom content at CSV-referenced paths. Some validation checks may fail — that's expected and will be fixed in Task 5.

### Step 5: Commit

```bash
git add tools/build.js
git commit -m "feat(build): add skill-based BMAD build with compatibility shim

buildBmadSkills() merges native/custom skill modules into flat
dist/_bmad/ layout. Old-format custom content copies to
dist/_bmad/modules/custom/ matching CSV-referenced paths.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Update Build Validation for New Layout

**Files:**
- Modify: `tools/build.js` (the `validateBuild` function)

### Step 1: Update required checks in `validateBuild`

Replace the existing `requiredChecks` array with checks that reflect the new layout. The key changes:
- Add `_bmad/BMAD-workflow.md` check (still needed by orchestrator agents)
- Add `_bmad/bmm/` and `_bmad/core/` skill-based layout checks
- Keep `_bmad/modules/custom/bmm` check (compat shim, still needed for CSV compatibility)
- Remove old paths that no longer exist

```javascript
const requiredChecks = [
  // Root BMAD files (referenced by orchestrator agents)
  { label: '_bmad/BMAD-workflow.md', path: path.join(DIST_ROOT, '_bmad', 'BMAD-workflow.md') },
  // New skill-based layout
  { label: '_bmad/bmm', path: path.join(DIST_ROOT, '_bmad', 'bmm') },
  { label: '_bmad/bmm/module.yaml', path: path.join(DIST_ROOT, '_bmad', 'bmm', 'module.yaml') },
  { label: '_bmad/bmm/module-help.csv', path: path.join(DIST_ROOT, '_bmad', 'bmm', 'module-help.csv') },
  { label: '_bmad/core', path: path.join(DIST_ROOT, '_bmad', 'core') },
  { label: '_bmad/core/module.yaml', path: path.join(DIST_ROOT, '_bmad', 'core', 'module.yaml') },
  { label: '_bmad/core/module-help.csv', path: path.join(DIST_ROOT, '_bmad', 'core', 'module-help.csv') },
  // Verify a few key skills exist in merged output
  { label: '_bmad/bmm/1-analysis/bmad-agent-analyst/SKILL.md', path: path.join(DIST_ROOT, '_bmad', 'bmm', '1-analysis', 'bmad-agent-analyst', 'SKILL.md') },
  { label: '_bmad/bmm/4-implementation/bmad-agent-dev/SKILL.md', path: path.join(DIST_ROOT, '_bmad', 'bmm', '4-implementation', 'bmad-agent-dev', 'SKILL.md') },
  { label: '_bmad/core/bmad-brainstorming/SKILL.md', path: path.join(DIST_ROOT, '_bmad', 'core', 'bmad-brainstorming', 'SKILL.md') },
  // Compatibility layer — old custom content at CSV-referenced paths (removed after Phase 3)
  { label: '_bmad/modules/custom/bmm', path: path.join(DIST_ROOT, '_bmad', 'modules', 'custom', 'bmm') },
  // Existing non-bmad targets
  { label: 'planning', path: path.join(DIST_ROOT, 'planning') },
  { label: 'planning/current/phase.md', path: path.join(DIST_ROOT, 'planning', 'current', 'phase.md') },
  { label: 'planning/roadmap/roadmap.md', path: path.join(DIST_ROOT, 'planning', 'roadmap', 'roadmap.md') },
  { label: 'docs', path: path.join(DIST_ROOT, 'docs') },
  { label: 'docs/human/policies/documentation-governance.md', path: path.join(DIST_ROOT, 'docs', 'human', 'policies', 'documentation-governance.md') },
  { label: '.claude', path: CLAUDE_DIST },
  { label: '.claude/README.md', path: path.join(CLAUDE_DIST, 'README.md') },
  { label: '.github/workflows', path: path.join(DIST_ROOT, '.github', 'workflows') },
  { label: 'root/.coderabbit.yaml', path: path.join(DIST_ROOT, 'root', '.coderabbit.yaml') },
  { label: 'root/.editorconfig', path: path.join(DIST_ROOT, 'root', '.editorconfig') },
  { label: 'root/.gitattributes', path: path.join(DIST_ROOT, 'root', '.gitattributes') },
];
```

### Step 2: Update `DIST_BMAD_REFERENCE_CSVS` and keep validation running

Since the compat shim copies old custom content to `dist/_bmad/modules/custom/` (the exact paths CSVs reference), the dist BMAD reference validation can keep running. But `workflow-manifest.csv` will be deleted in Task 8, so remove it from the array now to avoid a future crash.

```javascript
const DIST_BMAD_REFERENCE_CSVS = [
  // workflow-manifest.csv removed — obsoleted by per-module module-help.csv (deleted in Task 8)
  { relPath: '_config/bmad-help.csv', pathColumn: 5 },
  { relPath: 'modules/custom/bmm/module-help.csv', pathColumn: 5 },
];
```

Keep the `validateDistBmadReferences()` call in `validateBuild()` — it will still work because the compat shim places files at the expected paths.

### Step 3: Run the build and verify

```bash
node tools/build.js
```

Expected: Build completes with all validation checks passing.

### Step 4: Commit

```bash
git add tools/build.js
git commit -m "feat(build): update validation for skill-based layout

Replace old _bmad path checks with new skill directory checks.
Temporarily skip old CSV manifest validation (pending Phase 4).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Update validate.js for New Source Layout

**Files:**
- Modify: `tools/validate.js`

### Step 1: Update `REQUIRED_PATHS`

Add new skill-based paths. Keep old custom paths that are still in use.

**Keep** this path (orchestrator agents reference `_bmad/BMAD-workflow.md` at runtime):
```
'src/bmad/BMAD-workflow.md'
```

**Keep** this path (old custom is still active until Phase 3):
```
'src/bmad/modules/custom/bmm/module-help.csv'
```

Add these new paths:
```
'src/bmad/modules/native/bmm-skills/module.yaml'
'src/bmad/modules/native/bmm-skills/module-help.csv'
'src/bmad/modules/native/core-skills/module.yaml'
'src/bmad/modules/native/core-skills/module-help.csv'
```

Keep all existing `src/claude/*`, `src/codex/*`, `src/opencode/*`, `src/github/*`, `src/root/*`, `src/documentation/*`, `src/planning/*` paths unchanged.

### Step 1b: Update `BMAD_REFERENCE_CSVS`

Remove `workflow-manifest.csv` from the array since it will be deleted in Task 8. Keep the other two entries (they still reference valid paths):

```javascript
const BMAD_REFERENCE_CSVS = [
  // workflow-manifest.csv removed — deleted in Task 8
  { relPath: 'src/bmad/_config/bmad-help.csv', pathColumn: 5 },
  { relPath: 'src/bmad/modules/custom/bmm/module-help.csv', pathColumn: 5 },
];
```

### Step 2: Add skill format validation function

```javascript
/**
 * Validate that every SKILL.md in the native modules has valid frontmatter.
 * Checks: name field exists and matches the parent directory name.
 */
async function validateSkillFormat() {
  let ok = true;
  const moduleRoots = [
    path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'bmm-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'core-skills'),
  ];

  for (const moduleRoot of moduleRoots) {
    if (!(await exists(path.relative(ROOT, moduleRoot)))) continue;
    const skillFiles = await listFilesRecursive(moduleRoot);

    for (const filePath of skillFiles) {
      if (!filePath.endsWith('/SKILL.md') && !filePath.endsWith('\\SKILL.md')) continue;
      const content = await fs.readFile(filePath, 'utf-8');
      const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);

      if (!frontmatterMatch) {
        console.error(`ERROR ${path.relative(ROOT, filePath)}: missing YAML frontmatter`);
        ok = false;
        continue;
      }

      const nameMatch = frontmatterMatch[1].match(/^name:\s*(.+)$/m);
      if (!nameMatch) {
        console.error(`ERROR ${path.relative(ROOT, filePath)}: missing 'name' in frontmatter`);
        ok = false;
        continue;
      }

      const skillName = nameMatch[1].trim().replace(/['"]/g, '');
      const dirName = path.basename(path.dirname(filePath));
      if (skillName !== dirName) {
        console.error(
          `ERROR ${path.relative(ROOT, filePath)}: name '${skillName}' does not match directory '${dirName}'`,
        );
        ok = false;
      }
    }
  }

  if (ok) console.log('OK skill format validation');
  return ok;
}
```

### Step 3: Add `validateSkillFormat` to the `validate()` function

In the `validate()` function, locate the `Promise.all` call (around line 294) and add `validateSkillFormat()`:

```javascript
const checks = await Promise.all([
  validateRequiredPaths(),
  validateCodexConfig(),
  validateSourceSecretScan(),
  validateBmadReferenceCsvs(),
  validateCustomBmadAgentExecPaths(),
  validateSkillFormat(),  // ← Add this
]);
```

### Step 4: Verify old BMAD CSV validation still passes

The existing `validateBmadReferenceCsvs()` and `validateCustomBmadAgentExecPaths()` should still pass because:
- `BMAD_REFERENCE_CSVS` was updated in Step 1b to remove `workflow-manifest.csv`
- The remaining CSVs reference `_bmad/modules/custom/...` paths (custom content, still in old format)
- `validateCustomBmadAgentExecPaths()` checks agent exec paths in `src/bmad/modules/custom/bmm/agents/` which still exist

No changes needed here — just verify both functions still pass.

### Step 5: Run validation

```bash
node tools/validate.js
```

Expected: All checks pass including new skill format validation.

### Step 6: Commit

```bash
git add tools/validate.js
git commit -m "feat(validate): add skill format validation for new native modules

Validate SKILL.md frontmatter: name field exists and matches parent
directory. Update required paths for bmm-skills/ and core-skills/.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Fix Excalidraw CSV Paths and Remove Old Native Directories

The 4 excalidraw entries added to CSVs earlier reference `_bmad/modules/native/bmm/workflows/excalidraw-diagrams/...` paths. These paths will be deleted. The upstream v6.2.2 excalidraw content exists in the new `native/bmm-skills/` and will be merged to `dist/_bmad/bmm/`, but the old CSV paths won't match.

**Fix:** Remove the 4 excalidraw entries from `bmad-help.csv` and `module-help.csv`. The excalidraw functionality will be restored in Phase 5 when client skills are generated from the upstream `module-help.csv`. Also remove them from `workflow-manifest.csv` (which gets deleted in Task 8 anyway, but we need validate to pass first).

**Files:**
- Modify: `src/bmad/_config/bmad-help.csv` (remove 4 excalidraw rows)
- Modify: `src/bmad/_config/workflow-manifest.csv` (remove 4 excalidraw rows)
- Modify: `src/bmad/modules/custom/bmm/module-help.csv` (remove 4 excalidraw rows)
- Delete: `src/bmad/modules/native/bmm/` (entire directory)
- Delete: `src/bmad/modules/native/core/` (entire directory)
- Delete: `src/bmad/modules/native/bmad-builder/` (entire directory, moving to custom in Phase 3)
- Delete: `src/bmad/modules/native/test-architecture/` (entire directory, moving to custom in Phase 3)

### Step 0: Remove excalidraw entries from old-format CSVs

First verify exactly 4 entries exist in each CSV:
```bash
echo "bmad-help.csv:" && grep -c "excalidraw-diagrams" src/bmad/_config/bmad-help.csv
echo "workflow-manifest.csv:" && grep -c "excalidraw-diagrams" src/bmad/_config/workflow-manifest.csv
echo "module-help.csv:" && grep -c "excalidraw-diagrams" src/bmad/modules/custom/bmm/module-help.csv
```
Expected: 4 in each.

Then remove the 4 lines referencing `_bmad/modules/native/bmm/workflows/excalidraw-diagrams/` from:
- `src/bmad/_config/bmad-help.csv`
- `src/bmad/_config/workflow-manifest.csv`
- `src/bmad/modules/custom/bmm/module-help.csv`

Also remove the corresponding generated command files:
```bash
rm -f src/claude/commands/bmad/bmad-bmm-create-excalidraw-*.md
rm -f src/opencode/commands/bmad/bmad-bmm-create-excalidraw-*.md
```

Then re-sync to clean up command catalogs and skill references:
```bash
node tools/sync-client-bundles.js
```

### Step 1: Verify new native modules are committed

```bash
ls src/bmad/modules/native/bmm-skills/module.yaml
ls src/bmad/modules/native/core-skills/module.yaml
```

Both must exist before deleting old directories.

### Step 2: Preserve bmad-builder and test-architecture for Phase 3

Before deleting, copy these to a temporary holding location so Phase 3 can convert them:

```bash
mkdir -p reference/migration-staging
cp -r src/bmad/modules/native/bmad-builder reference/migration-staging/bmad-builder
cp -r src/bmad/modules/native/test-architecture reference/migration-staging/test-architecture
```

### Step 3: Delete old native directories

```bash
git rm -r src/bmad/modules/native/bmm
git rm -r src/bmad/modules/native/core
git rm -r src/bmad/modules/native/bmad-builder
git rm -r src/bmad/modules/native/test-architecture
```

### Step 4: Run full build and validate

```bash
node tools/validate.js
node tools/build.js
```

Both must pass. The build should produce `dist/_bmad/bmm/` from the new skill modules and `dist/_bmad/modules/custom/` from old custom content.

### Step 5: Commit

```bash
git add -A
git commit -m "refactor: remove old-format native module directories

Old native/bmm/ and native/core/ replaced by native/bmm-skills/
and native/core-skills/ (upstream v6.2.2 skill format).

bmad-builder and test-architecture staged in reference/migration-staging/
for conversion in Phase 3.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Update BMAD-workflow.md and Config

**Files:**
- Modify: `src/bmad/BMAD-workflow.md` (update to reference new layout)
- Delete: `src/bmad/_config/workflow-manifest.csv` (obsoleted by module-help.csv)
- Delete: `src/bmad/_config/task-manifest.csv` (obsoleted by module-help.csv)
- Keep: `src/bmad/_config/bmad-help.csv` (still used by sync-client-bundles until Phase 5)
- Keep: `src/bmad/_config/agent-manifest.csv` (still used until Phase 4)

### Step 1: Update BMAD-workflow.md

Update the file to reference the new skill-based layout. Change references from `_bmad/modules/custom/bmm/workflows/...` to `_bmad/bmm/...` for any shipped paths. Keep the overall workflow description intact — just update directory references.

### Step 2: Verify validate.js no longer references deleted CSVs

In Task 6 Step 1b, `workflow-manifest.csv` was already removed from `BMAD_REFERENCE_CSVS` in validate.js. Verify `task-manifest.csv` is also NOT in `BMAD_REFERENCE_CSVS` (it never was — only workflow-manifest, bmad-help, and module-help were listed). If it IS referenced anywhere, remove the reference now.

Also update `DIST_BMAD_REFERENCE_CSVS` in build.js if `workflow-manifest.csv` was not already removed in Task 5 Step 2.

### Step 3: Delete obsoleted manifests

```bash
git rm src/bmad/_config/workflow-manifest.csv
git rm src/bmad/_config/task-manifest.csv
```

These are replaced by per-module `module-help.csv` files.

### Step 4: Run build and validate

```bash
node tools/validate.js
node tools/build.js
```

Both must pass. If either crashes reading a deleted file, check that Steps 2's reference cleanup was complete.

### Step 5: Commit

```bash
git add -A
git commit -m "refactor: update BMAD-workflow.md and remove obsoleted manifests

workflow-manifest.csv and task-manifest.csv replaced by per-module
module-help.csv files in the skill-based layout.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: Verify End-to-End Build and Push Dry Run

**Files:** None (verification only)

### Step 1: Clean build

```bash
rm -rf dist/
node tools/build.js
```

### Step 2: Validate

```bash
node tools/validate.js
```

### Step 3: Drift checks

```bash
node tools/check-root-drift.js
node tools/check-github-drift.js
```

### Step 4: Push dry run

```bash
node tools/push.js --dry-run --targets bmad
```

Expected: Shows what would be pushed from the new `dist/_bmad/` layout.

### Step 5: Verify dist structure

```bash
echo "=== Merged bmm skills ==="
find dist/_bmad/bmm -name "SKILL.md" | head -10

echo "=== Merged core skills ==="
find dist/_bmad/core -name "SKILL.md" | head -10

echo "=== Compat layer (old custom at CSV-referenced paths) ==="
ls dist/_bmad/modules/custom/bmm/ | head -5

echo "=== Old manifests still present ==="
ls dist/_bmad/_config/bmad-help.csv
ls dist/_bmad/_config/agent-manifest.csv
```

### Step 6: Commit (if any fixes were needed)

```bash
git add -A
git commit -m "fix: address Phase 1 verification findings

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: Final Commit and PR

### Step 1: Review all changes

```bash
git log --oneline main..HEAD
git diff --stat main..HEAD
```

### Step 2: Push and create PR

```bash
git push -u origin feat/phase1-skill-migration
gh pr create --title "feat(bmad): Phase 1 — native module restructure to skill format" --body "..."
```

### Step 3: Wait for CI, merge

Follow the session close protocol.

---

## What This Phase Does NOT Do (Deferred to Later Phases)

- **Phase 2**: Convert custom agent overrides in `custom/bmm-skills/`
- **Phase 3**: Create `custom/compass-skills/` module, convert all Compass content
- **Phase 4**: Migrate to build-generated manifests, new 13-column module-help.csv
- **Phase 5**: Replace `sync-client-bundles.js` with skill-file generation

After Phase 1, the state is:
- New native modules in skill format (`native/bmm-skills/`, `native/core-skills/`)
- Old custom modules still in old format, copied to `dist/_bmad/modules/custom/` by compat shim (exact paths that CSVs reference)
- Build produces flat `dist/_bmad/bmm/` and `dist/_bmad/core/` from upstream skill modules
- `sync-client-bundles.js` still generates client commands from old `bmad-help.csv` (works because compat shim preserves CSV-referenced paths)
- Old custom CSVs (`bmad-help.csv`, `agent-manifest.csv`, `module-help.csv`) still present and functional
- `workflow-manifest.csv` and `task-manifest.csv` deleted (obsoleted by per-module `module-help.csv`)
- `bmad-builder` and `test-architecture` staged in `reference/migration-staging/` for Phase 3 conversion
