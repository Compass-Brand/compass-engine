import { describe, it, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { createTempDir, writeTree, readTree } from './helpers.js';
import {
  copyDir,
  copySelectedFiles,
  listFilesRecursive,
  readManagedManifest,
  writeManagedManifest,
  resolveGitDir,
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

// ---------------------------------------------------------------------------
// copyDir
// ---------------------------------------------------------------------------
describe('push copyDir', () => {
  it('should copy directory tree recursively', async () => {
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
});

// ---------------------------------------------------------------------------
// copySelectedFiles
// ---------------------------------------------------------------------------
describe('copySelectedFiles', () => {
  it('should copy only specified files and leave others', async () => {
    const src = await makeTempDir();
    const dest = await makeTempDir();

    await writeTree(src, {
      'a.txt': 'alpha',
      'b.txt': 'beta',
      'sub/c.txt': 'gamma',
    });

    await copySelectedFiles(src, dest, ['a.txt', 'sub/c.txt']);

    const tree = await readTree(dest);
    assert.deepEqual(tree, {
      'a.txt': 'alpha',
      'sub/c.txt': 'gamma',
    });
  });
});

// ---------------------------------------------------------------------------
// listFilesRecursive
// ---------------------------------------------------------------------------
describe('push listFilesRecursive', () => {
  it('should list files with forward-slash paths', async () => {
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
});

// ---------------------------------------------------------------------------
// managed manifest
// ---------------------------------------------------------------------------
describe('managed manifest', () => {
  it('should round-trip write and read manifest files', async () => {
    const project = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    const manifestName = 'test-sync.json';
    const files = ['a.txt', 'sub/b.txt'];

    await writeManagedManifest(project, manifestName, files);
    const result = await readManagedManifest(project, manifestName);

    assert.deepEqual(result, ['a.txt', 'sub/b.txt']);
  });

  it('should return empty array when manifest does not exist', async () => {
    const project = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    const result = await readManagedManifest(project, 'nonexistent.json');

    assert.deepEqual(result, []);
  });
});

// ---------------------------------------------------------------------------
// resolveGitDir
// ---------------------------------------------------------------------------
describe('resolveGitDir', () => {
  it('should return .git path when it is a directory', async () => {
    const project = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    const result = await resolveGitDir(project);

    assert.equal(result, path.join(project, '.git'));
  });

  it('should follow gitdir pointer when .git is a file (worktree)', async () => {
    const project = await makeTempDir();
    const actualGitDir = path.join(project, 'actual-git-dir');
    await fs.mkdir(actualGitDir, { recursive: true });
    await fs.writeFile(path.join(project, '.git'), `gitdir: ${actualGitDir}\n`);

    const result = await resolveGitDir(project);

    assert.equal(result, actualGitDir);
  });

  it('should return null when no .git exists', async () => {
    const project = await makeTempDir();

    const result = await resolveGitDir(project);

    assert.equal(result, null);
  });
});

// ---------------------------------------------------------------------------
// expandSelectedPaths
// ---------------------------------------------------------------------------
describe('expandSelectedPaths', () => {
  it('should expand a directory path to all contained files', async () => {
    const src = await makeTempDir();

    await writeTree(src, {
      'dir/a.txt': 'a',
      'dir/sub/b.txt': 'b',
    });

    const result = await expandSelectedPaths(src, ['dir']);

    assert.deepEqual(result, ['dir/a.txt', 'dir/sub/b.txt']);
  });

  it('should pass through individual file paths', async () => {
    const src = await makeTempDir();

    await writeTree(src, {
      'file.txt': 'content',
    });

    const result = await expandSelectedPaths(src, ['file.txt']);

    assert.deepEqual(result, ['file.txt']);
  });

  it('should throw on non-existent path', async () => {
    const src = await makeTempDir();

    await assert.rejects(
      () => expandSelectedPaths(src, ['does-not-exist']),
      (err) => {
        assert.match(err.message, /does not exist/);
        return true;
      },
    );
  });
});

// ---------------------------------------------------------------------------
// readContentOrDir + restoreContent
// ---------------------------------------------------------------------------
describe('readContentOrDir + restoreContent', () => {
  it('should round-trip a file backup', async () => {
    const dir = await makeTempDir();
    const filePath = path.join(dir, 'test.txt');
    await fs.writeFile(filePath, 'hello');

    const backup = await readContentOrDir(filePath);
    await fs.rm(filePath);
    await restoreContent(filePath, backup);

    const content = await fs.readFile(filePath, 'utf-8');
    assert.equal(content, 'hello');
  });

  it('should round-trip a directory backup', async () => {
    const dir = await makeTempDir();
    const subDir = path.join(dir, 'mydir');

    await writeTree(subDir, {
      'a.txt': 'alpha',
      'nested/b.txt': 'beta',
    });

    const backup = await readContentOrDir(subDir);
    await fs.rm(subDir, { recursive: true });
    await restoreContent(subDir, backup);

    const tree = await readTree(subDir);
    assert.deepEqual(tree, {
      'a.txt': 'alpha',
      'nested/b.txt': 'beta',
    });
  });

  it('should return null for non-existent path', async () => {
    const dir = await makeTempDir();
    const result = await readContentOrDir(path.join(dir, 'nope'));

    assert.equal(result, null);
  });
});

// ---------------------------------------------------------------------------
// syncManagedTarget
// ---------------------------------------------------------------------------
describe('syncManagedTarget', () => {
  const baseTarget = {
    destName: 'dest',
    distName: 'test',
    localOnly: [],
    syncStrategy: 'managed',
    manifestName: 'test-sync.json',
  };

  it('should install files and write manifest on fresh sync', async () => {
    const project = await makeTempDir();
    const source = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    await writeTree(source, {
      'a.txt': 'alpha',
      'sub/b.txt': 'beta',
    });

    await syncManagedTarget(project, source, baseTarget, { dryRun: false });

    const destTree = await readTree(path.join(project, 'dest'));
    assert.deepEqual(destTree, {
      'a.txt': 'alpha',
      'sub/b.txt': 'beta',
    });

    const manifest = await readManagedManifest(project, 'test-sync.json');
    assert.deepEqual(manifest, ['a.txt', 'sub/b.txt']);
  });

  it('should remove stale files on re-sync', async () => {
    const project = await makeTempDir();
    const source = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    // First sync with two files
    await writeTree(source, {
      'a.txt': 'alpha',
      'old.txt': 'old-content',
    });
    await syncManagedTarget(project, source, baseTarget, { dryRun: false });

    // Second sync with only one file - remove old.txt from source
    await fs.rm(path.join(source, 'old.txt'));
    await syncManagedTarget(project, source, baseTarget, { dryRun: false });

    const destTree = await readTree(path.join(project, 'dest'));
    assert.deepEqual(destTree, {
      'a.txt': 'alpha',
    });
  });

  it('should preserve paths listed in preservePaths', async () => {
    const project = await makeTempDir();
    const source = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    const preserveTarget = {
      ...baseTarget,
      preservePaths: ['README.md'],
    };

    // Pre-seed manifest with both files
    const manifestPath = path.join(project, '.git', 'test-sync.json');
    await fs.writeFile(
      manifestPath,
      JSON.stringify({ version: 1, files: ['a.txt', 'README.md'] }),
    );

    // Pre-create both files in dest
    await writeTree(path.join(project, 'dest'), {
      'a.txt': 'alpha',
      'README.md': 'project readme',
    });

    // Source now only has a.txt (README.md removed from source)
    await writeTree(source, {
      'a.txt': 'alpha-updated',
    });

    await syncManagedTarget(project, source, preserveTarget, { dryRun: false });

    const destTree = await readTree(path.join(project, 'dest'));
    assert.equal(destTree['a.txt'], 'alpha-updated');
    assert.equal(destTree['README.md'], 'project readme');
  });

  it('should not create files when dryRun is true', async () => {
    const project = await makeTempDir();
    const source = await makeTempDir();
    await fs.mkdir(path.join(project, '.git'));

    await writeTree(source, {
      'a.txt': 'alpha',
    });

    await syncManagedTarget(project, source, baseTarget, { dryRun: true });

    const destExists = await fs.access(path.join(project, 'dest')).then(
      () => true,
      () => false,
    );
    assert.equal(destExists, false);
  });
});

// ---------------------------------------------------------------------------
// loadProjectConfig
// ---------------------------------------------------------------------------
describe('loadProjectConfig', () => {
  it('should parse paths from config file', async () => {
    const dir = await makeTempDir();
    const configPath = path.join(dir, 'projects.conf');

    await fs.writeFile(
      configPath,
      [
        '# comment line',
        '',
        '/absolute/path/one',
        'relative/path/two',
        '',
        '# another comment',
        'relative/path/three',
      ].join('\n'),
    );

    const result = await loadProjectConfig(configPath, '/workspace');

    assert.deepEqual(result, [
      '/absolute/path/one',
      path.join('/workspace', 'relative/path/two'),
      path.join('/workspace', 'relative/path/three'),
    ]);
  });

  it('should return null for non-existent file', async () => {
    const result = await loadProjectConfig('/nonexistent/config.txt', '/workspace');

    assert.equal(result, null);
  });
});

// ---------------------------------------------------------------------------
// discoverWorkspaceGitRepos
// ---------------------------------------------------------------------------
describe('discoverWorkspaceGitRepos', () => {
  it('should find directories containing .git', async () => {
    const workspace = await makeTempDir();

    // Create repos with .git dirs
    await fs.mkdir(path.join(workspace, 'repo-a', '.git'), { recursive: true });
    await fs.mkdir(path.join(workspace, 'repo-b', '.git'), { recursive: true });
    // Create a non-repo directory (no .git)
    await fs.mkdir(path.join(workspace, 'not-a-repo'), { recursive: true });

    const result = await discoverWorkspaceGitRepos(workspace);
    const names = result.map((p) => path.basename(p)).sort();

    assert.deepEqual(names, ['repo-a', 'repo-b']);
  });

  it('should skip node_modules and dist directories', async () => {
    const workspace = await makeTempDir();

    await fs.mkdir(path.join(workspace, 'real-repo', '.git'), { recursive: true });
    await fs.mkdir(path.join(workspace, 'node_modules', '.git'), { recursive: true });
    await fs.mkdir(path.join(workspace, 'dist', '.git'), { recursive: true });

    const result = await discoverWorkspaceGitRepos(workspace);
    const names = result.map((p) => path.basename(p));

    assert.deepEqual(names, ['real-repo']);
  });
});
