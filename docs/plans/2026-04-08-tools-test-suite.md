# Tools Test Suite Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add comprehensive test coverage for compass-engine's build/push/validate tooling — the ~2,000 lines of executable code the project owns.

**Architecture:** Use Node.js built-in `node:test` runner with `node:assert/strict` (no new dependencies, Node 18+ already required). Export internal functions from each tool file for direct testing. Filesystem tests use `fs.mkdtemp` for isolated temp directories.

**Tech Stack:** `node:test`, `node:assert/strict`, `node:fs`, `node:os`, `node:path`

---

## Task 1: Test Infrastructure and Export Modifications

**Files:**
- Modify: `package.json` (add test script)
- Modify: `tools/build.js:617` (expand exports)
- Modify: `tools/push.js:676` (expand exports)
- Modify: `tools/validate.js:388` (expand exports)
- Create: `test/helpers.js`

**Step 1: Add test script to package.json**

In `package.json`, add a `test:unit` script and update the existing conceptual test entry:

```json
"test:unit": "node --test test/test-*.js",
"test": "npm run test:unit && npm run validate",
```

This replaces the current missing `test` script. The `--test` flag uses the Node.js built-in test runner.

**Step 2: Verify exports in build.js**

`tools/build.js` already exports the required functions (build, normalizePath, shouldSkip, parseSimpleYaml, parseCsvRows, clientSkillName, copyDir, mergeModules, listFilesRecursive). No changes needed -- tests can import these directly.

**Step 3: Verify exports in push.js**

`tools/push.js` already exports the required functions (push, resolveFeatureSelection, resolveWithinProject, expandSelectedPaths, readManagedManifest, writeManagedManifest, resolveGitDir, getManagedManifestPath, syncManagedTarget, copyDir, copySelectedFiles, listFilesRecursive, readContentOrDir, restoreContent, loadProjectConfig, discoverWorkspaceGitRepos). No changes needed.

**Step 4: Verify exports in validate.js**

`tools/validate.js` already exports the required functions (validate, shouldScanSourceFile, isLikelyPlaceholder, findSecretIndicators, parseCsvLine). No changes needed.

**Step 5: Create test/helpers.js**

```js
import { promises as fs } from 'fs';
import os from 'os';
import path from 'path';

/**
 * Create a temporary directory for test isolation.
 * Returns { dir, cleanup } where cleanup removes the directory.
 */
export async function createTempDir(prefix = 'ce-test-') {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), prefix));
  const cleanup = () => fs.rm(dir, { recursive: true, force: true });
  return { dir, cleanup };
}

/**
 * Write a file tree from a plain object.
 * Keys are relative paths, values are file contents (string).
 *
 * Example:
 *   await writeTree(dir, {
 *     'a/b.txt': 'hello',
 *     'c.md': '# title',
 *   });
 */
export async function writeTree(root, tree) {
  for (const [relPath, content] of Object.entries(tree)) {
    const fullPath = path.join(root, relPath);
    await fs.mkdir(path.dirname(fullPath), { recursive: true });
    await fs.writeFile(fullPath, content);
  }
}

/**
 * Read all files in a directory tree and return as a plain object.
 * Keys are relative paths (forward slashes), values are file contents.
 */
export async function readTree(root) {
  const result = {};
  async function walk(currentPath) {
    const entries = await fs.readdir(currentPath, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        await walk(entryPath);
      } else {
        const relPath = path.relative(root, entryPath).replace(/\\/g, '/');
        result[relPath] = await fs.readFile(entryPath, 'utf-8');
      }
    }
  }
  await walk(root);
  return result;
}
```

**Step 6: Run `node --test test/` to verify test runner works (no tests yet, should exit 0)**

Run: `node --test test/helpers.js`
Expected: Exits 0 (no tests found, no failures)

**Step 7: Commit**

```bash
git add test/helpers.js tools/build.js tools/push.js tools/validate.js package.json
git commit -m "chore: add test infrastructure and export internal functions for testing"
```

---

## Task 2: build.js Pure Function Tests

**Files:**
- Create: `test/test-build-pure.js`

**Step 1: Write the test file**

```js
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  normalizePath,
  shouldSkip,
  parseSimpleYaml,
  parseCsvRows,
  clientSkillName,
} from '../tools/build.js';

// ── normalizePath ───────────────────────────────────────────────

describe('normalizePath', () => {
  it('should convert backslashes to forward slashes', () => {
    assert.equal(normalizePath('a\\b\\c'), 'a/b/c');
  });

  it('should leave forward slashes unchanged', () => {
    assert.equal(normalizePath('a/b/c'), 'a/b/c');
  });

  it('should handle empty string', () => {
    assert.equal(normalizePath(''), '');
  });
});

// ── shouldSkip ──────────────────────────────────────────────────

describe('shouldSkip', () => {
  it('should return false when skipPaths is empty', () => {
    assert.equal(shouldSkip('README.md', []), false);
  });

  it('should return false when skipPaths is null', () => {
    assert.equal(shouldSkip('README.md', null), false);
  });

  it('should match exact path', () => {
    assert.equal(shouldSkip('README.md', ['README.md']), true);
  });

  it('should match path prefix (directory skip)', () => {
    assert.equal(shouldSkip('docs/guide.md', ['docs']), true);
  });

  it('should not match partial filename', () => {
    assert.equal(shouldSkip('docs-extra/file.md', ['docs']), false);
  });

  it('should normalize backslashes before comparing', () => {
    assert.equal(shouldSkip('docs\\file.md', ['docs']), true);
  });
});

// ── parseSimpleYaml ─────────────────────────────────────────────

describe('parseSimpleYaml', () => {
  it('should parse basic key-value pairs', () => {
    const result = parseSimpleYaml('name: test\ntype: agent');
    assert.deepEqual(result, { name: 'test', type: 'agent' });
  });

  it('should strip surrounding double quotes', () => {
    const result = parseSimpleYaml('name: "hello world"');
    assert.equal(result.name, 'hello world');
  });

  it('should skip comment lines', () => {
    const result = parseSimpleYaml('# comment\nname: test');
    assert.deepEqual(result, { name: 'test' });
  });

  it('should skip empty lines', () => {
    const result = parseSimpleYaml('name: test\n\ntype: agent\n');
    assert.deepEqual(result, { name: 'test', type: 'agent' });
  });

  it('should use only first colon as delimiter', () => {
    const result = parseSimpleYaml('description: Use when: something happens');
    assert.equal(result.description, 'Use when: something happens');
  });

  it('should decode YAML unicode escapes to emoji', () => {
    const result = parseSimpleYaml('icon: "\\U0001F680"');
    assert.equal(result.icon, '\u{1F680}');
  });

  it('should skip lines without a colon', () => {
    const result = parseSimpleYaml('just text\nname: test');
    assert.deepEqual(result, { name: 'test' });
  });

  it('should return empty object for empty string', () => {
    assert.deepEqual(parseSimpleYaml(''), {});
  });
});

// ── parseCsvRows ────────────────────────────────────────────────

describe('parseCsvRows', () => {
  it('should parse basic CSV with header', () => {
    const rows = parseCsvRows('name,type\nalice,admin\nbob,user');
    assert.equal(rows.length, 2);
    assert.deepEqual(rows[0], { name: 'alice', type: 'admin' });
    assert.deepEqual(rows[1], { name: 'bob', type: 'user' });
  });

  it('should handle quoted fields containing commas', () => {
    const rows = parseCsvRows('name,desc\nalice,"hello, world"');
    assert.equal(rows[0].desc, 'hello, world');
  });

  it('should handle escaped quotes inside quoted fields', () => {
    const rows = parseCsvRows('name,desc\nalice,"say ""hi"""');
    assert.equal(rows[0].desc, 'say "hi"');
  });

  it('should default missing cells to empty string', () => {
    const rows = parseCsvRows('a,b,c\n1,2');
    assert.equal(rows[0].c, '');
  });

  it('should return empty array when only header exists', () => {
    const rows = parseCsvRows('name,type');
    assert.equal(rows.length, 0);
  });

  it('should return empty array for single line', () => {
    const rows = parseCsvRows('name');
    assert.equal(rows.length, 0);
  });

  it('should handle trailing comma as empty field', () => {
    const rows = parseCsvRows('a,b\n1,');
    assert.equal(rows[0].b, '');
  });
});

// ── clientSkillName ─────────────────────────────────────────────

describe('clientSkillName', () => {
  it('should pass through bmad-compass- prefixed names unchanged', () => {
    assert.equal(clientSkillName('bmad-compass-worktree', 'compass'), 'bmad-compass-worktree');
  });

  it('should pass through bmad-agent-compass- prefixed names unchanged', () => {
    assert.equal(
      clientSkillName('bmad-agent-compass-lead', 'compass'),
      'bmad-agent-compass-lead',
    );
  });

  it('should use builder as short module name for bmad-builder', () => {
    assert.equal(clientSkillName('bmad-create-story', 'bmad-builder'), 'bmad-builder-create-story');
  });

  it('should insert module name into agent names', () => {
    assert.equal(clientSkillName('bmad-agent-analyst', 'bmm'), 'bmad-agent-bmm-analyst');
  });

  it('should map bmad-master to bmad-core-master', () => {
    assert.equal(clientSkillName('bmad-master', 'core'), 'bmad-core-master');
  });

  it('should insert module name into workflow names', () => {
    assert.equal(clientSkillName('bmad-create-prd', 'bmm'), 'bmad-bmm-create-prd');
  });

  it('should handle bmad-builder agent names with builder prefix', () => {
    assert.equal(
      clientSkillName('bmad-agent-tech-writer', 'bmad-builder'),
      'bmad-agent-builder-tech-writer',
    );
  });
});
```

**Step 2: Run tests to verify they pass**

Run: `node --test test/test-build-pure.js`
Expected: All tests pass (functions are already implemented)

**Step 3: Commit**

```bash
git add test/test-build-pure.js
git commit -m "test(build): add pure function tests for parseSimpleYaml, parseCsvRows, clientSkillName, shouldSkip, normalizePath"
```

---

## Task 3: push.js Pure Function Tests

**Files:**
- Create: `test/test-push-pure.js`

**Step 1: Write the test file**

```js
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import path from 'path';
import { resolveFeatureSelection, resolveWithinProject } from '../tools/push.js';

// ── resolveFeatureSelection ─────────────────────────────────────

describe('resolveFeatureSelection', () => {
  const groups = {
    baseline: ['codeowners', 'dependabot'],
    codeowners: ['CODEOWNERS'],
    dependabot: ['dependabot.yml'],
    linting: ['workflows/lint-core.yml', 'workflows/lint-languages.yml'],
  };

  it('should return null when requested is null', () => {
    assert.equal(resolveFeatureSelection(groups, null, 'test'), null);
  });

  it('should return null when requested is empty', () => {
    assert.equal(resolveFeatureSelection(groups, [], 'test'), null);
  });

  it('should return null when requested includes all', () => {
    assert.equal(resolveFeatureSelection(groups, ['all'], 'test'), null);
  });

  it('should resolve leaf features to their paths', () => {
    const result = resolveFeatureSelection(groups, ['linting'], 'test');
    assert.deepEqual(result, ['workflows/lint-core.yml', 'workflows/lint-languages.yml']);
  });

  it('should resolve nested groups recursively', () => {
    const result = resolveFeatureSelection(groups, ['baseline'], 'test');
    assert.deepEqual(result, ['CODEOWNERS', 'dependabot.yml']);
  });

  it('should deduplicate paths from overlapping selections', () => {
    const result = resolveFeatureSelection(groups, ['baseline', 'codeowners'], 'test');
    assert.deepEqual(result, ['CODEOWNERS', 'dependabot.yml']);
  });

  it('should throw on unknown feature name', () => {
    assert.throws(
      () => resolveFeatureSelection(groups, ['nonexistent'], 'test'),
      /Unknown test feature: nonexistent/,
    );
  });

  it('should throw on circular feature definitions', () => {
    const circular = { a: ['b'], b: ['a'] };
    assert.throws(
      () => resolveFeatureSelection(circular, ['a'], 'test'),
      /Circular/,
    );
  });

  it('should sort results alphabetically', () => {
    const result = resolveFeatureSelection(groups, ['linting'], 'test');
    const sorted = [...result].sort();
    assert.deepEqual(result, sorted);
  });
});

// ── resolveWithinProject ────────────────────────────────────────

describe('resolveWithinProject', () => {
  it('should resolve a normal relative path within project', () => {
    const result = resolveWithinProject('/project', 'docs/file.md');
    assert.equal(result, path.resolve('/project', 'docs/file.md'));
  });

  it('should throw on directory traversal attempt', () => {
    assert.throws(
      () => resolveWithinProject('/project', '../escape.txt'),
      /Refusing to operate outside project root/,
    );
  });

  it('should allow path resolving to project root exactly', () => {
    const result = resolveWithinProject('/project', '.');
    assert.equal(result, path.resolve('/project'));
  });

  it('should throw on deeply nested traversal', () => {
    assert.throws(
      () => resolveWithinProject('/project', 'a/../../escape'),
      /Refusing to operate outside project root/,
    );
  });
});
```

**Step 2: Run tests to verify they pass**

Run: `node --test test/test-push-pure.js`
Expected: All tests pass

**Step 3: Commit**

```bash
git add test/test-push-pure.js
git commit -m "test(push): add pure function tests for resolveFeatureSelection, resolveWithinProject"
```

---

## Task 4: validate.js Pure Function Tests

**Files:**
- Create: `test/test-validate-pure.js`

**Step 1: Write the test file**

```js
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  shouldScanSourceFile,
  isLikelyPlaceholder,
  findSecretIndicators,
  parseCsvLine,
} from '../tools/validate.js';

// ── shouldScanSourceFile ────────────────────────────────────────

describe('shouldScanSourceFile', () => {
  it('should scan .js files', () => {
    assert.equal(shouldScanSourceFile('src/index.js'), true);
  });

  it('should scan .ts files', () => {
    assert.equal(shouldScanSourceFile('src/plugin.ts'), true);
  });

  it('should scan .yaml files', () => {
    assert.equal(shouldScanSourceFile('config.yaml'), true);
  });

  it('should scan .env files', () => {
    assert.equal(shouldScanSourceFile('.env'), true);
  });

  it('should skip .example files', () => {
    assert.equal(shouldScanSourceFile('config.example'), false);
  });

  it('should skip .template files', () => {
    assert.equal(shouldScanSourceFile('settings.template'), false);
  });

  it('should skip .sample files', () => {
    assert.equal(shouldScanSourceFile('data.sample'), false);
  });

  it('should skip files in fixtures directories', () => {
    assert.equal(shouldScanSourceFile('test/fixtures/config.json'), false);
  });

  it('should skip unknown extensions', () => {
    assert.equal(shouldScanSourceFile('readme.md'), false);
  });

  it('should skip .png and other binary types', () => {
    assert.equal(shouldScanSourceFile('logo.png'), false);
  });
});

// ── isLikelyPlaceholder ─────────────────────────────────────────

describe('isLikelyPlaceholder', () => {
  it('should detect example keyword', () => {
    assert.equal(isLikelyPlaceholder('my-example-key'), true);
  });

  it('should detect changeme keyword', () => {
    assert.equal(isLikelyPlaceholder('changeme'), true);
  });

  it('should detect your_ prefix', () => {
    assert.equal(isLikelyPlaceholder('your_api_key'), true);
  });

  it('should detect your- prefix', () => {
    assert.equal(isLikelyPlaceholder('your-token-here'), true);
  });

  it('should detect dummy keyword', () => {
    assert.equal(isLikelyPlaceholder('dummy-value'), true);
  });

  it('should detect test keyword', () => {
    assert.equal(isLikelyPlaceholder('test-token'), true);
  });

  it('should detect template variable ${...}', () => {
    assert.equal(isLikelyPlaceholder('${API_KEY}'), true);
  });

  it('should detect mustache template {{...}}', () => {
    assert.equal(isLikelyPlaceholder('{{secret}}'), true);
  });

  it('should return false for real-looking values', () => {
    assert.equal(isLikelyPlaceholder('sk-abc123realkey456'), false);
  });

  it('should be case-insensitive', () => {
    assert.equal(isLikelyPlaceholder('CHANGEME'), true);
  });
});

// ── findSecretIndicators ────────────────────────────────────────

describe('findSecretIndicators', () => {
  it('should detect ctx7 token pattern', () => {
    const result = findSecretIndicators('token = ctx7sk-abcdefghijklmnopqrstuvwx');
    assert.match(result, /ctx7 token pattern/);
  });

  it('should detect GitHub personal access token', () => {
    const result = findSecretIndicators('key = ghp-abcdefghijklmnopqrstuvwx');
    assert.match(result, /API token-like pattern/);
  });

  it('should detect sk- prefixed tokens', () => {
    const result = findSecretIndicators('key = sk-abcdefghijklmnopqrstuvwx');
    assert.match(result, /API token-like pattern/);
  });

  it('should detect api_key assignment with real value', () => {
    const result = findSecretIndicators('api_key = "sk_live_realkey123456"');
    assert.match(result, /api_key assignment/);
  });

  it('should ignore api_key with placeholder value', () => {
    const result = findSecretIndicators('api_key = "your_api_key_here"');
    assert.equal(result, null);
  });

  it('should return null for clean content', () => {
    const result = findSecretIndicators('const x = 42;\nfunction hello() {}');
    assert.equal(result, null);
  });

  it('should report correct line number', () => {
    const result = findSecretIndicators('clean\nclean\nctx7sk-abcdefghijklmnopqrstuvwx');
    assert.match(result, /line 3/);
  });

  it('should detect api-key (hyphenated) variant', () => {
    const result = findSecretIndicators('api-key: "realvalue123456"');
    assert.match(result, /api_key assignment/);
  });
});

// ── parseCsvLine ────────────────────────────────────────────────

describe('parseCsvLine', () => {
  it('should parse simple comma-separated values', () => {
    assert.deepEqual(parseCsvLine('a,b,c'), ['a', 'b', 'c']);
  });

  it('should handle quoted fields with commas', () => {
    assert.deepEqual(parseCsvLine('a,"b,c",d'), ['a', 'b,c', 'd']);
  });

  it('should handle escaped double quotes', () => {
    assert.deepEqual(parseCsvLine('a,"say ""hi""",c'), ['a', 'say "hi"', 'c']);
  });

  it('should handle empty fields', () => {
    assert.deepEqual(parseCsvLine('a,,c'), ['a', '', 'c']);
  });

  it('should handle trailing comma', () => {
    assert.deepEqual(parseCsvLine('a,b,'), ['a', 'b', '']);
  });

  it('should handle single field', () => {
    assert.deepEqual(parseCsvLine('hello'), ['hello']);
  });
});
```

**Step 2: Run tests to verify they pass**

Run: `node --test test/test-validate-pure.js`
Expected: All tests pass

**Step 3: Commit**

```bash
git add test/test-validate-pure.js
git commit -m "test(validate): add pure function tests for shouldScanSourceFile, isLikelyPlaceholder, findSecretIndicators, parseCsvLine"
```

---

## Task 5: build.js Filesystem Tests

**Files:**
- Create: `test/test-build-fs.js`

**Step 1: Write the test file**

```js
import { describe, it, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'fs';
import path from 'path';
import { createTempDir, writeTree, readTree } from './helpers.js';
import { copyDir, mergeModules, listFilesRecursive } from '../tools/build.js';

let cleanups = [];
afterEach(async () => {
  for (const cleanup of cleanups) await cleanup();
  cleanups = [];
});

async function makeTempDir() {
  const { dir, cleanup } = await createTempDir('build-fs-');
  cleanups.push(cleanup);
  return dir;
}

// ── copyDir ─────────────────────────────────────────────────────

describe('copyDir', () => {
  it('should copy all files from source to destination', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await writeTree(src, {
      'a.txt': 'hello',
      'sub/b.txt': 'world',
    });

    await copyDir(src, dest);
    const result = await readTree(dest);

    assert.equal(result['a.txt'], 'hello');
    assert.equal(result['sub/b.txt'], 'world');
  });

  it('should respect skipPaths option', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await writeTree(src, {
      'keep.txt': 'kept',
      'skip.txt': 'skipped',
      'subdir/nested.txt': 'nested',
    });

    await copyDir(src, dest, { baseDir: src, skipPaths: ['skip.txt', 'subdir'] });
    const result = await readTree(dest);

    assert.equal(result['keep.txt'], 'kept');
    assert.equal(result['skip.txt'], undefined);
    assert.equal(result['subdir/nested.txt'], undefined);
  });

  it('should handle empty source directory', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await copyDir(src, dest);
    const result = await readTree(dest);

    assert.deepEqual(result, {});
  });

  it('should overwrite existing files in destination', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await writeTree(dest, { 'a.txt': 'old' });
    await writeTree(src, { 'a.txt': 'new' });

    await copyDir(src, dest);
    const result = await readTree(dest);

    assert.equal(result['a.txt'], 'new');
  });
});

// ── mergeModules ────────────────────────────────────────────────

describe('mergeModules', () => {
  it('should copy native module when no custom exists', async () => {
    const native = await makeTempDir();
    const output = await makeTempDir();

    await writeTree(native, {
      'skill-a/SKILL.md': 'native skill a',
    });

    await mergeModules(native, '/nonexistent/path', output);
    const result = await readTree(output);

    assert.equal(result['skill-a/SKILL.md'], 'native skill a');
  });

  it('should overlay custom files on top of native', async () => {
    const native = await makeTempDir();
    const custom = await makeTempDir();
    const output = await makeTempDir();

    await writeTree(native, {
      'skill-a/SKILL.md': 'native version',
      'skill-a/workflow.md': 'native workflow',
      'skill-b/SKILL.md': 'native only skill',
    });

    await writeTree(custom, {
      'skill-a/SKILL.md': 'custom override',
      'skill-c/SKILL.md': 'custom only skill',
    });

    await mergeModules(native, custom, output);
    const result = await readTree(output);

    assert.equal(result['skill-a/SKILL.md'], 'custom override');
    assert.equal(result['skill-a/workflow.md'], 'native workflow');
    assert.equal(result['skill-b/SKILL.md'], 'native only skill');
    assert.equal(result['skill-c/SKILL.md'], 'custom only skill');
  });
});

// ── listFilesRecursive ──────────────────────────────────────────

describe('listFilesRecursive', () => {
  it('should list all files with forward-slash relative paths', async () => {
    const dir = await makeTempDir();

    await writeTree(dir, {
      'a.txt': 'a',
      'sub/b.txt': 'b',
      'sub/deep/c.txt': 'c',
    });

    const files = await listFilesRecursive(dir);
    files.sort();

    assert.deepEqual(files, ['a.txt', 'sub/b.txt', 'sub/deep/c.txt']);
  });

  it('should return empty array for empty directory', async () => {
    const dir = await makeTempDir();
    const files = await listFilesRecursive(dir);
    assert.deepEqual(files, []);
  });
});
```

**Step 2: Run tests to verify they pass**

Run: `node --test test/test-build-fs.js`
Expected: All tests pass

**Step 3: Commit**

```bash
git add test/test-build-fs.js
git commit -m "test(build): add filesystem tests for copyDir, mergeModules, listFilesRecursive"
```

---

## Task 6: push.js Filesystem Tests

**Files:**
- Create: `test/test-push-fs.js`

**Step 1: Write the test file**

```js
import { describe, it, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'fs';
import path from 'path';
import { createTempDir, writeTree, readTree } from './helpers.js';
import {
  copyDir,
  copySelectedFiles,
  listFilesRecursive,
  readManagedManifest,
  writeManagedManifest,
  resolveGitDir,
  getManagedManifestPath,
  syncManagedTarget,
  expandSelectedPaths,
  readContentOrDir,
  restoreContent,
  loadProjectConfig,
  discoverWorkspaceGitRepos,
} from '../tools/push.js';

let cleanups = [];
afterEach(async () => {
  for (const cleanup of cleanups) await cleanup();
  cleanups = [];
});

async function makeTempDir() {
  const { dir, cleanup } = await createTempDir('push-fs-');
  cleanups.push(cleanup);
  return dir;
}

// ── copyDir (push variant — no options) ─────────────────────────

describe('push copyDir', () => {
  it('should copy directory tree recursively', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await writeTree(src, {
      'a.txt': 'hello',
      'sub/b.txt': 'world',
    });

    await copyDir(src, dest);
    const result = await readTree(dest);

    assert.equal(result['a.txt'], 'hello');
    assert.equal(result['sub/b.txt'], 'world');
  });
});

// ── copySelectedFiles ───────────────────────────────────────────

describe('copySelectedFiles', () => {
  it('should copy only the specified files', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await writeTree(src, {
      'a.txt': 'a',
      'b.txt': 'b',
      'sub/c.txt': 'c',
    });

    await copySelectedFiles(src, dest, ['a.txt', 'sub/c.txt']);
    const result = await readTree(dest);

    assert.equal(result['a.txt'], 'a');
    assert.equal(result['sub/c.txt'], 'c');
    assert.equal(result['b.txt'], undefined);
  });
});

// ── listFilesRecursive ──────────────────────────────────────────

describe('push listFilesRecursive', () => {
  it('should list files with forward-slash paths', async () => {
    const dir = await makeTempDir();

    await writeTree(dir, {
      'x.txt': 'x',
      'nested/y.txt': 'y',
    });

    const files = await listFilesRecursive(dir);
    files.sort();

    assert.deepEqual(files, ['nested/y.txt', 'x.txt']);
  });
});

// ── readManagedManifest / writeManagedManifest ───────────────────

describe('managed manifest', () => {
  it('should write and read manifest round-trip', async () => {
    const project = await makeTempDir();
    // Create a .git directory so getManagedManifestPath resolves inside it
    await fs.mkdir(path.join(project, '.git'));

    const files = ['a.txt', 'sub/b.txt'];
    await writeManagedManifest(project, 'test-sync.json', files);
    const result = await readManagedManifest(project, 'test-sync.json');

    assert.deepEqual(result, ['a.txt', 'sub/b.txt']);
  });

  it('should return empty array when manifest does not exist', async () => {
    const project = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    const result = await readManagedManifest(project, 'missing.json');
    assert.deepEqual(result, []);
  });
});

// ── resolveGitDir ───────────────────────────────────────────────

describe('resolveGitDir', () => {
  it('should return .git directory path when it is a directory', async () => {
    const project = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    const result = await resolveGitDir(project);
    assert.equal(result, path.join(project, '.git'));
  });

  it('should follow gitdir pointer when .git is a file (worktree)', async () => {
    const project = await makeTempDir();
    const gitDir = path.join(project, 'actual-git-dir');
    await fs.mkdir(gitDir);
    await fs.writeFile(path.join(project, '.git'), `gitdir: ${gitDir}\n`);

    const result = await resolveGitDir(project);
    assert.equal(result, gitDir);
  });

  it('should return null when no .git exists', async () => {
    const project = await makeTempDir();
    const result = await resolveGitDir(project);
    assert.equal(result, null);
  });
});

// ── expandSelectedPaths ─────────────────────────────────────────

describe('expandSelectedPaths', () => {
  it('should expand a directory path to all contained files', async () => {
    const src = await makeTempDir();
    await writeTree(src, {
      'workflows/a.yml': 'a',
      'workflows/b.yml': 'b',
      'other.txt': 'other',
    });

    const result = await expandSelectedPaths(src, ['workflows']);
    result.sort();
    assert.deepEqual(result, ['workflows/a.yml', 'workflows/b.yml']);
  });

  it('should pass through individual file paths', async () => {
    const src = await makeTempDir();
    await writeTree(src, { 'CODEOWNERS': 'team' });

    const result = await expandSelectedPaths(src, ['CODEOWNERS']);
    assert.deepEqual(result, ['CODEOWNERS']);
  });

  it('should throw on non-existent path', async () => {
    const src = await makeTempDir();
    await assert.rejects(
      () => expandSelectedPaths(src, ['missing.txt']),
      /does not exist/,
    );
  });
});

// ── readContentOrDir / restoreContent ───────────────────────────

describe('readContentOrDir and restoreContent', () => {
  it('should round-trip a file backup', async () => {
    const dir = await makeTempDir();
    await writeTree(dir, { 'local.json': '{"key": "value"}' });

    const backup = await readContentOrDir(path.join(dir, 'local.json'));
    assert.equal(backup.type, 'file');

    // Delete and restore
    await fs.rm(path.join(dir, 'local.json'));
    await restoreContent(path.join(dir, 'local.json'), backup);

    const restored = await fs.readFile(path.join(dir, 'local.json'), 'utf-8');
    assert.equal(restored, '{"key": "value"}');
  });

  it('should round-trip a directory backup', async () => {
    const dir = await makeTempDir();
    await writeTree(dir, {
      'cache/a.txt': 'a',
      'cache/sub/b.txt': 'b',
    });

    const backup = await readContentOrDir(path.join(dir, 'cache'));
    assert.equal(backup.type, 'directory');

    await fs.rm(path.join(dir, 'cache'), { recursive: true });
    await restoreContent(path.join(dir, 'cache'), backup);

    const result = await readTree(path.join(dir, 'cache'));
    assert.equal(result['a.txt'], 'a');
    assert.equal(result['sub/b.txt'], 'b');
  });

  it('should return null for non-existent path', async () => {
    const dir = await makeTempDir();
    const result = await readContentOrDir(path.join(dir, 'missing'));
    assert.equal(result, null);
  });
});

// ── syncManagedTarget ───────────────────────────────────────────

describe('syncManagedTarget', () => {
  it('should install files and write manifest on fresh sync', async () => {
    const project = await makeTempDir();
    const source = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    await writeTree(source, {
      'a.txt': 'new-a',
      'sub/b.txt': 'new-b',
    });

    const target = {
      destName: 'dest',
      distName: 'test',
      localOnly: [],
      syncStrategy: 'managed',
      manifestName: 'test-sync.json',
    };

    await syncManagedTarget(project, source, target, { dryRun: false });

    const result = await readTree(path.join(project, 'dest'));
    assert.equal(result['a.txt'], 'new-a');
    assert.equal(result['sub/b.txt'], 'new-b');

    const manifest = await readManagedManifest(project, 'test-sync.json');
    assert.ok(manifest.includes('a.txt'));
    assert.ok(manifest.includes('sub/b.txt'));
  });

  it('should remove stale files from previous manifest', async () => {
    const project = await makeTempDir();
    const source = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));
    await fs.mkdir(path.join(project, 'dest'), { recursive: true });

    // First sync: install two files
    await writeTree(source, {
      'a.txt': 'a',
      'old.txt': 'old',
    });
    const target = {
      destName: 'dest',
      distName: 'test',
      localOnly: [],
      syncStrategy: 'managed',
      manifestName: 'stale-sync.json',
    };
    await syncManagedTarget(project, source, target, { dryRun: false });

    // Second sync: old.txt removed from source
    const source2 = await makeTempDir();
    await writeTree(source2, { 'a.txt': 'updated-a' });

    await syncManagedTarget(project, source2, target, { dryRun: false });

    const result = await readTree(path.join(project, 'dest'));
    assert.equal(result['a.txt'], 'updated-a');
    assert.equal(result['old.txt'], undefined); // stale file removed
  });

  it('should preserve paths listed in preservePaths', async () => {
    const project = await makeTempDir();
    const source = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    // Pre-existing project-owned file
    await writeTree(path.join(project, 'dest'), { 'README.md': 'project readme' });

    // First sync creates a manifest that includes README.md
    const manifestPath = await getManagedManifestPath(project, 'preserve-sync.json');
    await fs.mkdir(path.dirname(manifestPath), { recursive: true });
    await fs.writeFile(
      manifestPath,
      JSON.stringify({ version: 1, files: ['a.txt', 'README.md'] }),
    );

    // Second sync: README.md no longer in source, but is in preservePaths
    await writeTree(source, { 'a.txt': 'content' });

    const target = {
      destName: 'dest',
      distName: 'test',
      localOnly: [],
      syncStrategy: 'managed',
      manifestName: 'preserve-sync.json',
      preservePaths: ['README.md'],
    };
    await syncManagedTarget(project, source, target, { dryRun: false });

    const result = await readTree(path.join(project, 'dest'));
    assert.equal(result['a.txt'], 'content');
    assert.equal(result['README.md'], 'project readme'); // preserved
  });

  it('should only log actions when dryRun is true', async () => {
    const project = await makeTempDir();
    const source = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    await writeTree(source, { 'a.txt': 'content' });

    const target = {
      destName: 'dest',
      distName: 'test',
      localOnly: [],
      syncStrategy: 'managed',
      manifestName: 'dry-sync.json',
    };

    await syncManagedTarget(project, source, target, { dryRun: true });

    // dest directory should NOT be created
    const destExists = await fs.access(path.join(project, 'dest')).then(() => true).catch(() => false);
    assert.equal(destExists, false);
  });
});

// ── loadProjectConfig ───────────────────────────────────────────

describe('loadProjectConfig', () => {
  it('should parse project paths from config file', async () => {
    const dir = await makeTempDir();
    await writeTree(dir, {
      'projects.txt': '/absolute/path\nrelative/path\n# comment\n',
    });

    const result = await loadProjectConfig(path.join(dir, 'projects.txt'), '/workspace');
    assert.ok(result.includes('/absolute/path'));
    assert.ok(result.some((p) => p.endsWith('relative/path')));
    assert.equal(result.length, 2); // comment and empty lines excluded
  });

  it('should return null for non-existent config file', async () => {
    const result = await loadProjectConfig('/nonexistent/projects.txt', '/workspace');
    assert.equal(result, null);
  });
});

// ── discoverWorkspaceGitRepos ───────────────────────────────────

describe('discoverWorkspaceGitRepos', () => {
  it('should find directories containing .git', async () => {
    const workspace = await makeTempDir();

    // Create two git repos and one non-repo
    await fs.mkdir(path.join(workspace, 'repo-a', '.git'), { recursive: true });
    await fs.mkdir(path.join(workspace, 'repo-b', '.git'), { recursive: true });
    await fs.mkdir(path.join(workspace, 'not-a-repo'), { recursive: true });

    const repos = await discoverWorkspaceGitRepos(workspace);
    const names = repos.map((p) => path.basename(p)).sort();

    assert.deepEqual(names, ['repo-a', 'repo-b']);
  });

  it('should skip node_modules and dist directories', async () => {
    const workspace = await makeTempDir();

    await fs.mkdir(path.join(workspace, 'node_modules', '.git'), { recursive: true });
    await fs.mkdir(path.join(workspace, 'dist', '.git'), { recursive: true });

    const repos = await discoverWorkspaceGitRepos(workspace);
    assert.deepEqual(repos, []);
  });
});
```

**Step 2: Run tests to verify they pass**

Run: `node --test test/test-push-fs.js`
Expected: All tests pass

**Step 3: Commit**

```bash
git add test/test-push-fs.js
git commit -m "test(push): add filesystem tests for copyDir, syncManagedTarget, resolveGitDir, manifest I/O, project discovery"
```

---

## Task 7: Integration Test — Full Build Cycle

**Files:**
- Create: `test/test-build-integration.js`

This test runs the actual `build()` function against the real source tree and validates the output matches what `validateBuild()` expects. It's a smoke test ensuring the build pipeline stays consistent.

**Step 1: Write the test file**

```js
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { build } from '../tools/build.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const DIST_ROOT = path.join(ROOT, 'dist');

describe('build integration', () => {
  it('should produce a valid dist/ from current src/', async () => {
    // Run the full build (includes internal validateBuild)
    await build();

    // Spot-check critical outputs
    const bmadDir = path.join(DIST_ROOT, '_bmad');
    const configDir = path.join(bmadDir, '_config');

    // Generated manifests exist
    const agentManifest = await fs.readFile(path.join(configDir, 'agent-manifest.csv'), 'utf-8');
    assert.ok(agentManifest.includes('"id"'), 'agent-manifest.csv should have header');
    assert.ok(agentManifest.split('\n').length > 2, 'agent-manifest.csv should have data rows');

    const skillManifest = await fs.readFile(path.join(configDir, 'skill-manifest.csv'), 'utf-8');
    assert.ok(skillManifest.includes('name,type'), 'skill-manifest.csv should have header');

    const bmadHelp = await fs.readFile(path.join(configDir, 'bmad-help.csv'), 'utf-8');
    assert.ok(bmadHelp.split('\n').length > 2, 'bmad-help.csv should have data rows');

    // Client skills generated for all platforms
    for (const platform of ['.claude', '.opencode', '.codex']) {
      const skillsDir = path.join(DIST_ROOT, platform, 'skills');
      const skills = await fs.readdir(skillsDir);
      assert.ok(skills.length >= 90, `${platform}/skills/ should have ≥90 entries, found ${skills.length}`);
    }

    // Key bundle directories exist
    for (const dir of ['planning', 'docs', '.github', 'root', 'beads']) {
      const stat = await fs.stat(path.join(DIST_ROOT, dir));
      assert.ok(stat.isDirectory(), `dist/${dir} should exist`);
    }
  });
});
```

**Step 2: Run test to verify it passes**

Run: `node --test test/test-build-integration.js`
Expected: Pass (build runs and validates successfully)

**Step 3: Commit**

```bash
git add test/test-build-integration.js
git commit -m "test(build): add integration test running full build cycle against real source"
```

---

## Task 8: Add Tests to CI Pipeline

**Files:**
- Modify: `src/github/workflows/quality-checks.yml`

**Step 1: Read the current workflow to find the right insertion point**

Read `src/github/workflows/quality-checks.yml` and locate the jobs section.

**Step 2: Add a test job**

Add a job that runs before or alongside existing quality checks. The job should:

```yaml
  test:
    name: Unit & Integration Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm run test:unit
```

**Step 3: Run build to verify the workflow update propagates**

Run: `npm run build`
Expected: Build succeeds with updated workflow in `dist/.github/workflows/`

**Step 4: Commit**

```bash
git add src/github/workflows/quality-checks.yml
git commit -m "ci: add unit and integration test job to quality-checks workflow"
```

---

## Task 9: Final Verification

**Step 1: Run the full test suite**

Run: `node --test test/test-*.js`
Expected: All tests pass

**Step 2: Run the full check pipeline**

Run: `npm run check`
Expected: validate + drift checks + build + push dry-run all pass

**Step 3: Commit any remaining changes and verify clean state**

```bash
git status
```
Expected: Clean working tree (all changes committed)

