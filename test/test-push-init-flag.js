import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import yaml from 'js-yaml';
import { createTempDir } from './helpers.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');
const PUSH_SCRIPT = path.join(REPO_ROOT, 'tools/push.js');

function runPush(args) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [PUSH_SCRIPT, ...args], {
      cwd: REPO_ROOT,
      env: { ...process.env, CI: '1' },
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('exit', (code) => resolve({ code, stdout, stderr }));
  });
}

describe('push --init flag', () => {
  let tmp;
  let cleanup;

  before(async () => {
    const created = await createTempDir('ce-push-init-');
    tmp = created.dir;
    cleanup = created.cleanup;
  });

  after(async () => {
    await cleanup();
  });

  it('should bootstrap _bmad configs after a dry-run push when --init is passed', async () => {
    const projectRoot = path.join(tmp, 'proj');
    await fs.mkdir(projectRoot, { recursive: true });
    const { code, stderr } = await runPush([
      '--project',
      projectRoot,
      '--dry-run',
      '--targets',
      'bmad',
      '--init',
    ]);
    assert.equal(code, 0, `push --init should exit 0 (stderr: ${stderr})`);
    const core = yaml.load(
      await fs.readFile(path.join(projectRoot, '_bmad/core/config.yaml'), 'utf-8'),
    );
    assert.equal(core.user_name, 'BMad');
  });

  it('should not write config files when --init is omitted', async () => {
    const projectRoot = path.join(tmp, 'no-init-proj');
    await fs.mkdir(projectRoot, { recursive: true });
    const { code } = await runPush([
      '--project',
      projectRoot,
      '--dry-run',
      '--targets',
      'bmad',
    ]);
    assert.equal(code, 0);
    await assert.rejects(() => fs.stat(path.join(projectRoot, '_bmad/core/config.yaml')));
  });
});
