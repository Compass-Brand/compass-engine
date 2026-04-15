import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import { createTempDir } from './helpers.js';
import { writeConfig, ensureDirectories } from '../tools/init/config-writer.js';

describe('writeConfig', () => {
  let tmp;
  let cleanup;

  before(async () => {
    const created = await createTempDir('ce-init-writer-');
    tmp = created.dir;
    cleanup = created.cleanup;
  });

  after(async () => {
    await cleanup();
  });

  it('should write _bmad/core/config.yaml with the provided values', async () => {
    const projectRoot = path.join(tmp, 'proj-a');
    await writeConfig(projectRoot, 'core', {
      user_name: 'BMad',
      output_folder: `${projectRoot}/_bmad-output`,
    });
    const abs = path.join(projectRoot, '_bmad/core/config.yaml');
    const raw = await fs.readFile(abs, 'utf-8');
    const parsed = yaml.load(raw);
    assert.equal(parsed.user_name, 'BMad');
    assert.equal(parsed.output_folder, `${projectRoot}/_bmad-output`);
    assert.match(raw, /# CORE Module Configuration/);
  });

  it('should refuse to overwrite an existing config file by default', async () => {
    const projectRoot = path.join(tmp, 'proj-b');
    await writeConfig(projectRoot, 'core', { user_name: 'Original' });
    await assert.rejects(
      () => writeConfig(projectRoot, 'core', { user_name: 'Replacement' }),
      /refus|exists/i,
    );
    const parsed = yaml.load(
      await fs.readFile(path.join(projectRoot, '_bmad/core/config.yaml'), 'utf-8'),
    );
    assert.equal(parsed.user_name, 'Original');
  });

  it('should overwrite when force: true', async () => {
    const projectRoot = path.join(tmp, 'proj-c');
    await writeConfig(projectRoot, 'core', { user_name: 'Original' });
    await writeConfig(projectRoot, 'core', { user_name: 'Replacement' }, { force: true });
    const parsed = yaml.load(
      await fs.readFile(path.join(projectRoot, '_bmad/core/config.yaml'), 'utf-8'),
    );
    assert.equal(parsed.user_name, 'Replacement');
  });

  it('should quote values containing colons so YAML round-trips correctly', async () => {
    const projectRoot = path.join(tmp, 'proj-d');
    await writeConfig(projectRoot, 'core', { user_name: 'Mary: PM' });
    const raw = await fs.readFile(path.join(projectRoot, '_bmad/core/config.yaml'), 'utf-8');
    const parsed = yaml.load(raw);
    assert.equal(parsed.user_name, 'Mary: PM');
  });

  it('should create parent directories', async () => {
    const projectRoot = path.join(tmp, 'proj-e/nested/deep');
    await writeConfig(projectRoot, 'bmm', { project_name: 'x' });
    await fs.stat(path.join(projectRoot, '_bmad/bmm/config.yaml'));
  });
});

describe('ensureDirectories', () => {
  let tmp;
  let cleanup;

  before(async () => {
    const created = await createTempDir('ce-init-ensure-');
    tmp = created.dir;
    cleanup = created.cleanup;
  });

  after(async () => {
    await cleanup();
  });

  it('should create each path recursively', async () => {
    const paths = [
      path.join(tmp, 'a/b/c'),
      path.join(tmp, 'x/y'),
    ];
    await ensureDirectories(paths);
    for (const p of paths) {
      const stat = await fs.stat(p);
      assert.ok(stat.isDirectory(), `${p} should be a directory`);
    }
  });

  it('should be idempotent — re-running does not throw', async () => {
    const p = path.join(tmp, 'repeat/dir');
    await ensureDirectories([p]);
    await ensureDirectories([p]);
    const stat = await fs.stat(p);
    assert.ok(stat.isDirectory());
  });
});
