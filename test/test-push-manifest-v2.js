import { describe, it, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { createTempDir } from './helpers.js';
import {
  readManagedManifest,
  writeManagedManifest,
} from '../tools/push.js';

let cleanups = [];
afterEach(async () => {
  for (const cleanup of cleanups) await cleanup();
  cleanups = [];
});

async function makeTempProject() {
  const { dir, cleanup } = await createTempDir('push-v2-');
  cleanups.push(cleanup);
  await fs.mkdir(path.join(dir, '.git'));
  return dir;
}

async function readManifestRaw(project, manifestName) {
  const manifestPath = path.join(project, '.git', manifestName);
  const raw = await fs.readFile(manifestPath, 'utf-8');
  return JSON.parse(raw);
}

describe('managed-manifest schema v2 (ADR-0001 Risk #3)', () => {
  it('writes version: 2 on new manifests', async () => {
    const project = await makeTempProject();
    const manifestName = 'compass-engine-claude-plugin-sync.json';
    await writeManagedManifest(project, manifestName, ['a.txt']);

    const payload = await readManifestRaw(project, manifestName);
    assert.equal(payload.version, 2, 'new manifests must be written as version 2');
  });

  it('round-trips v2 manifest stably through read/write/read', async () => {
    const project = await makeTempProject();
    const manifestName = 'compass-engine-claude-plugin-sync.json';

    const files1 = ['a.txt', 'sub/b.txt'];
    await writeManagedManifest(project, manifestName, files1);
    const read1 = await readManagedManifest(project, manifestName);

    await writeManagedManifest(project, manifestName, read1);
    const read2 = await readManagedManifest(project, manifestName);

    assert.deepEqual(read2, files1.slice().sort());
    const payload = await readManifestRaw(project, manifestName);
    assert.equal(payload.version, 2);
  });

  it('reads legacy v1 manifest file-list without data loss (migration on next write)', async () => {
    const project = await makeTempProject();
    const manifestName = 'compass-engine-legacy-sync.json';
    const manifestPath = path.join(project, '.git', manifestName);

    const legacy = {
      version: 1,
      generatedAt: '2025-01-01T00:00:00.000Z',
      files: ['legacy-a.txt', 'legacy-b.txt'],
    };
    await fs.writeFile(manifestPath, JSON.stringify(legacy, null, 2));

    const read = await readManagedManifest(project, manifestName);
    assert.deepEqual(read, ['legacy-a.txt', 'legacy-b.txt']);

    await writeManagedManifest(project, manifestName, read);
    const payload = await readManifestRaw(project, manifestName);
    assert.equal(payload.version, 2, 'subsequent writes upgrade to v2');
    assert.deepEqual(payload.files, ['legacy-a.txt', 'legacy-b.txt']);
  });

  it('reads manifest with missing version field without data loss', async () => {
    const project = await makeTempProject();
    const manifestName = 'compass-engine-pre-versioned-sync.json';
    const manifestPath = path.join(project, '.git', manifestName);

    const preVersioned = {
      generatedAt: '2025-01-01T00:00:00.000Z',
      files: ['x.txt'],
    };
    await fs.writeFile(manifestPath, JSON.stringify(preVersioned, null, 2));

    const read = await readManagedManifest(project, manifestName);
    assert.deepEqual(read, ['x.txt']);
  });
});
