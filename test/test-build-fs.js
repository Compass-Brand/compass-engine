import { describe, it, afterEach } from 'node:test';
import assert from 'node:assert/strict';
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

// ---------------------------------------------------------------------------
// copyDir
// ---------------------------------------------------------------------------
describe('copyDir', () => {
  it('should copy all files from source to destination including nested dirs', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await writeTree(src, {
      'a.txt': 'alpha',
      'sub/b.txt': 'beta',
      'sub/deep/c.txt': 'gamma',
    });

    await copyDir(src, dest);

    const tree = await readTree(dest);
    assert.deepEqual(tree, {
      'a.txt': 'alpha',
      'sub/b.txt': 'beta',
      'sub/deep/c.txt': 'gamma',
    });
  });

  it('should respect skipPaths option for exact file and directory skips', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await writeTree(src, {
      'README.md': 'readme',
      'keep.txt': 'keep',
      'secret/a.txt': 'secret-a',
      'secret/b.txt': 'secret-b',
      'other/c.txt': 'other-c',
    });

    await copyDir(src, dest, { baseDir: src, skipPaths: ['README.md', 'secret'] });

    const tree = await readTree(dest);
    assert.deepEqual(tree, {
      'keep.txt': 'keep',
      'other/c.txt': 'other-c',
    });
  });

  it('should handle empty source directory', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await copyDir(src, dest);

    const tree = await readTree(dest);
    assert.deepEqual(tree, {});
  });

  it('should overwrite existing files in destination', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await writeTree(dest, {
      'file.txt': 'old content',
    });
    await writeTree(src, {
      'file.txt': 'new content',
    });

    await copyDir(src, dest);

    const tree = await readTree(dest);
    assert.equal(tree['file.txt'], 'new content');
  });
});

// ---------------------------------------------------------------------------
// mergeModules
// ---------------------------------------------------------------------------
describe('mergeModules', () => {
  it('should copy native module when custom path does not exist', async () => {
    const native = await makeTempDir();
    const output = await makeTempDir();

    await writeTree(native, {
      'a.txt': 'native-a',
      'sub/b.txt': 'native-b',
    });

    const outputDir = path.join(output, 'merged');
    await mergeModules(native, '/nonexistent/path', outputDir);

    const tree = await readTree(outputDir);
    assert.deepEqual(tree, {
      'a.txt': 'native-a',
      'sub/b.txt': 'native-b',
    });
  });

  it('should overlay custom files on top of native', async () => {
    const native = await makeTempDir();
    const custom = await makeTempDir();
    const output = await makeTempDir();

    await writeTree(native, {
      'shared.txt': 'native-version',
      'native-only.txt': 'only-in-native',
    });
    await writeTree(custom, {
      'shared.txt': 'custom-version',
      'custom-only.txt': 'only-in-custom',
    });

    const outputDir = path.join(output, 'merged');
    await mergeModules(native, custom, outputDir);

    const tree = await readTree(outputDir);
    assert.equal(tree['shared.txt'], 'custom-version');
    assert.equal(tree['native-only.txt'], 'only-in-native');
    assert.equal(tree['custom-only.txt'], 'only-in-custom');
  });
});

// ---------------------------------------------------------------------------
// listFilesRecursive
// ---------------------------------------------------------------------------
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
