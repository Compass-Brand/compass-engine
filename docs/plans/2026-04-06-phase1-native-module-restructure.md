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
├── bmad-skill-manifest.yaml    # Agent metadata (agents only)
└── steps/                      # Micro-step files (optional)
    ├── step-01-init.md
    └── step-02-discovery.md
```

Modules are organized by phase: `1-analysis/`, `2-plan-workflows/`, `3-solutioning/`, `4-implementation/`.

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

## Task 3: Add Skill-Aware Module Walker to build.js

**Files:**
- Modify: `tools/build.js`

### Context

The current build copies `src/bmad/` to `dist/_bmad/` as a flat directory tree. The new build needs to:

1. Walk skill directories (find `SKILL.md` files)
2. Merge native + custom (custom directory wins)
3. Output flat module layout (`dist/_bmad/bmm/`, `dist/_bmad/core/`)

### Step 1: Add the `discoverSkillDirs` function

Add this function to `build.js` after the existing utility functions. It walks a module directory and returns a map of skill-name → absolute-path for every directory containing a `SKILL.md`.

```javascript
/**
 * Discover all skill directories within a module root.
 * A skill directory is any directory containing a SKILL.md file.
 * Returns Map<skillName, absolutePath> where skillName is the directory name.
 */
async function discoverSkillDirs(moduleRoot) {
  const skills = new Map();

  async function walk(dir) {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const fullPath = path.join(dir, entry.name);
      const skillFile = path.join(fullPath, 'SKILL.md');
      if (await exists(skillFile)) {
        skills.set(entry.name, fullPath);
      } else {
        await walk(fullPath);
      }
    }
  }

  await walk(moduleRoot);
  return skills;
}
```

### Step 2: Add the `mergeModules` function

This function takes a native module path and optional custom module path, discovers skills in both, and copies them to the output directory. Custom skills with the same name replace native ones entirely.

```javascript
/**
 * Merge native and custom skill modules into a flat output directory.
 * Custom skills override native skills of the same name (full replacement).
 * Non-skill files at the module root (module.yaml, module-help.csv) are
 * copied from native first, then overwritten by custom if present.
 */
async function mergeModules(nativePath, customPath, outputPath) {
  await fs.mkdir(outputPath, { recursive: true });

  // Copy module root files from native (module.yaml, module-help.csv, etc.)
  if (await exists(nativePath)) {
    const rootEntries = await fs.readdir(nativePath, { withFileTypes: true });
    for (const entry of rootEntries) {
      if (entry.isFile()) {
        await fs.copyFile(path.join(nativePath, entry.name), path.join(outputPath, entry.name));
      }
    }
  }

  // Overlay module root files from custom (if present)
  if (customPath && (await exists(customPath))) {
    const rootEntries = await fs.readdir(customPath, { withFileTypes: true });
    for (const entry of rootEntries) {
      if (entry.isFile()) {
        await fs.copyFile(path.join(customPath, entry.name), path.join(outputPath, entry.name));
      }
    }
  }

  // Discover skills from both trees
  const nativeSkills = (await exists(nativePath)) ? await discoverSkillDirs(nativePath) : new Map();
  const customSkills =
    customPath && (await exists(customPath)) ? await discoverSkillDirs(customPath) : new Map();

  // Merge: native first, custom overwrites
  const mergedSkills = new Map([...nativeSkills, ...customSkills]);

  // Determine output paths preserving phase directory structure
  for (const [skillName, skillSrcPath] of mergedSkills) {
    // Compute the relative path from the module root to preserve phase dirs
    const moduleRoot = customSkills.has(skillName) ? customPath : nativePath;
    const relativePath = path.relative(moduleRoot, skillSrcPath);
    const skillDestPath = path.join(outputPath, relativePath);
    await copyDir(skillSrcPath, skillDestPath);
  }

  // Copy non-skill phase directories (directories that contain skills but aren't skills themselves)
  // The phase dirs (1-analysis/, 2-plan-workflows/, etc.) may contain non-skill files
  for (const sourceRoot of [nativePath, customPath].filter(Boolean)) {
    if (!(await exists(sourceRoot))) continue;
    const entries = await fs.readdir(sourceRoot, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const destDir = path.join(outputPath, entry.name);
      await fs.mkdir(destDir, { recursive: true });
    }
  }
}
```

### Step 3: Run validation to make sure build.js still parses

```bash
node -e "import('./tools/build.js')"
```

Expected: no syntax errors.

### Step 4: Commit

```bash
git add tools/build.js
git commit -m "feat(build): add skill directory walker and module merge functions

discoverSkillDirs() finds all directories containing SKILL.md.
mergeModules() combines native + custom modules with custom-wins
semantics, preserving phase directory structure.

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

This function copies old-format custom content (`custom/bmm/`, `custom/core/`) into the dist tree so everything keeps working until Phases 2-3 convert them. It merges into the already-built skill output without overwriting skill directories.

```javascript
/**
 * Temporary compatibility shim for old-format custom modules.
 * Copies content from custom/bmm/ and custom/core/ into the merged dist,
 * preserving the old directory layout alongside new skill directories.
 * This function is removed in Phase 3 after all custom content is converted.
 */
async function buildBmadCompat() {
  const OLD_CUSTOM_BMM = path.join(CUSTOM_ROOT, 'bmm');
  const OLD_CUSTOM_CORE = path.join(CUSTOM_ROOT, 'core');

  // Only run if old-format custom directories still exist
  if (!(await exists(OLD_CUSTOM_BMM)) && !(await exists(OLD_CUSTOM_CORE))) {
    return;
  }

  console.log('  Applying old-format compatibility shim...');

  // Copy old custom bmm content into dist/_bmad/ with _compat prefix
  // to avoid colliding with the new skill-based bmm/ directory
  if (await exists(OLD_CUSTOM_BMM)) {
    const compatDest = path.join(BMAD_DIST, '_compat', 'bmm');
    await copyDir(OLD_CUSTOM_BMM, compatDest, { baseDir: OLD_CUSTOM_BMM });
    console.log('    Copied old custom/bmm/ → _compat/bmm/');
  }

  if (await exists(OLD_CUSTOM_CORE)) {
    const compatDest = path.join(BMAD_DIST, '_compat', 'core');
    await copyDir(OLD_CUSTOM_CORE, compatDest, { baseDir: OLD_CUSTOM_CORE });
    console.log('    Copied old custom/core/ → _compat/core/');
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

Expected: Build completes. `dist/_bmad/bmm/` contains skill directories from upstream. `dist/_bmad/_compat/bmm/` contains old custom content. Some validation checks may fail — that's expected and will be fixed in Task 5.

### Step 5: Commit

```bash
git add tools/build.js
git commit -m "feat(build): add skill-based BMAD build with compatibility shim

buildBmadSkills() merges native/custom skill modules into flat
dist/_bmad/ layout. Old-format custom content copies to _compat/
subdirectory until Phases 2-3 convert it to skill format.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Update Build Validation for New Layout

**Files:**
- Modify: `tools/build.js` (the `validateBuild` function)

### Step 1: Update required checks in `validateBuild`

Replace the existing `requiredChecks` array with checks that reflect the new layout. The key changes:
- `_bmad/BMAD-workflow.md` → no longer required (was old-format)
- `_bmad/modules/custom/bmm/module-help.csv` → replaced by `_bmad/bmm/module-help.csv`
- Add checks for new skill-based paths

```javascript
const requiredChecks = [
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
  // Compatibility layer (removed after Phase 3)
  { label: '_bmad/_compat/bmm', path: path.join(DIST_ROOT, '_bmad', '_compat', 'bmm') },
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

### Step 2: Temporarily disable `validateDistBmadReferences`

The old BMAD reference validation checks CSV paths against `dist/_bmad/modules/custom/...` which no longer exists. Comment it out or wrap it in a try-catch with a warning. It will be replaced in Phase 4 with skill-manifest validation.

```javascript
// Temporarily disabled — old manifest validation incompatible with new skill layout.
// Will be replaced by skill-manifest validation in Phase 4.
// if (!(await validateDistBmadReferences())) { isValid = false; }
console.log('  SKIP dist BMAD manifest validation (pending Phase 4 migration)');
```

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

Replace old BMAD source paths with new skill-based paths. Keep all non-BMAD paths unchanged.

Remove these old paths:
```
'src/bmad/BMAD-workflow.md'
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

In the `validate()` function, add `validateSkillFormat()` to the `Promise.all` checks array.

### Step 4: Temporarily skip old BMAD CSV validation

The existing `validateBmadReferenceCsvs()` and `validateCustomBmadAgentExecPaths()` check paths against the old `src/bmad/modules/custom/...` layout. These still exist (old custom hasn't been migrated yet), so they should still run. But update `BMAD_REFERENCE_CSVS` if needed to avoid errors against deleted native paths.

Check if any CSV in `_config/` references `modules/native/` paths. If so, those CSVs will break since native now has `bmm-skills/` not `bmm/`. The old `_config/` CSVs reference `_bmad/modules/custom/...` (custom paths), not native, so they should still work.

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

## Task 7: Remove Old Native Module Directories

**Files:**
- Delete: `src/bmad/modules/native/bmm/` (entire directory)
- Delete: `src/bmad/modules/native/core/` (entire directory)
- Delete: `src/bmad/modules/native/bmad-builder/` (entire directory, moving to custom in Phase 3)
- Delete: `src/bmad/modules/native/test-architecture/` (entire directory, moving to custom in Phase 3)

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

Both must pass. The build should produce `dist/_bmad/bmm/` from the new skill modules and `dist/_bmad/_compat/` from old custom content.

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

### Step 2: Delete obsoleted manifests

```bash
git rm src/bmad/_config/workflow-manifest.csv
git rm src/bmad/_config/task-manifest.csv
```

These are replaced by per-module `module-help.csv` files.

### Step 3: Run build and validate

```bash
node tools/validate.js
node tools/build.js
```

If validate.js references the deleted CSVs in `BMAD_REFERENCE_CSVS`, update it to remove those entries.

### Step 4: Commit

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

echo "=== Compat layer ==="
ls dist/_bmad/_compat/bmm/ | head -5

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
- New native modules in skill format (bmm-skills/, core-skills/)
- Old custom modules still in old format (under `_compat/` in dist)
- Build produces flat `dist/_bmad/bmm/` and `dist/_bmad/core/` from upstream
- `sync-client-bundles.js` still generates client commands from old `bmad-help.csv`
- Old custom CSVs and manifests still present and functional
