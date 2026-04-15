import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const CLI = path.join(ROOT, 'src/cli.js');

function runCli(args) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [CLI, ...args], {
      cwd: ROOT,
      env: process.env,
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('exit', (code) => resolve({ code, stdout, stderr }));
  });
}

describe('compass-engine init subcommand', () => {
  it('should exit 0 and print help banner when called with --help', async () => {
    const { code, stdout } = await runCli(['init', '--help']);
    assert.equal(code, 0, 'init --help should exit 0');
    assert.match(stdout, /Compass Engine init/, 'stdout should include "Compass Engine init"');
  });
});
