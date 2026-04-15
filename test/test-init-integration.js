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
const CLI = path.join(REPO_ROOT, 'src/cli.js');

function runCli(args, cwd) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [CLI, ...args], {
      cwd: cwd || REPO_ROOT,
      env: { ...process.env, CI: '1' },
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('exit', (code) => resolve({ code, stdout, stderr }));
  });
}

describe('compass-engine init integration', () => {
  let tmp;
  let cleanup;

  before(async () => {
    const created = await createTempDir('ce-init-int-');
    tmp = created.dir;
    cleanup = created.cleanup;
  });

  after(async () => {
    await cleanup();
  });

  it('should write core + bmm config files and create bmm directories', async () => {
    const projectRoot = path.join(tmp, 'proj');
    await fs.mkdir(projectRoot, { recursive: true });

    const { code, stderr } = await runCli(['init', '--project-root', projectRoot]);
    assert.equal(code, 0, `init should exit 0 (stderr: ${stderr})`);

    const core = yaml.load(
      await fs.readFile(path.join(projectRoot, '_bmad/core/config.yaml'), 'utf-8'),
    );
    assert.equal(core.user_name, 'BMad');
    assert.equal(core.output_folder, path.join(projectRoot, '_bmad-output'));

    const bmm = yaml.load(
      await fs.readFile(path.join(projectRoot, '_bmad/bmm/config.yaml'), 'utf-8'),
    );
    assert.equal(bmm.project_name, 'proj');
    assert.equal(bmm.user_skill_level, 'intermediate');
    assert.equal(
      bmm.planning_artifacts,
      path.join(projectRoot, '_bmad-output/planning-artifacts'),
    );
    assert.equal(bmm.user_name, 'BMad', 'core vars should be merged into module config');

    const planningDir = await fs.stat(path.join(projectRoot, '_bmad-output/planning-artifacts'));
    assert.ok(planningDir.isDirectory());
  });

  it('should refuse to overwrite existing configs on re-run without --force', async () => {
    const projectRoot = path.join(tmp, 'proj');
    const { code, stderr } = await runCli(['init', '--project-root', projectRoot]);
    assert.notEqual(code, 0, 'second run without --force should fail');
    assert.match(stderr, /refus|exists/i);
  });

  it('should overwrite existing configs when --force is passed', async () => {
    const projectRoot = path.join(tmp, 'proj');
    const { code } = await runCli(['init', '--project-root', projectRoot, '--force']);
    assert.equal(code, 0);
  });

  it('should print the planned writes and not touch the fs when --dry-run', async () => {
    const projectRoot = path.join(tmp, 'dry');
    await fs.mkdir(projectRoot, { recursive: true });
    const { code, stdout } = await runCli(['init', '--project-root', projectRoot, '--dry-run']);
    assert.equal(code, 0);
    assert.match(stdout, /core\/config\.yaml/);
    assert.match(stdout, /bmm\/config\.yaml/);
    await assert.rejects(() => fs.stat(path.join(projectRoot, '_bmad')));
  });
});
