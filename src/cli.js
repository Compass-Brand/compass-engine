#!/usr/bin/env node

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

const COMMANDS = {
  build: 'tools/build.js',
  push: 'tools/push.js',
  validate: 'tools/validate.js',
  'create-bmad-module': 'tools/create-bmad-module.js',
  'check-github-drift': 'tools/check-github-drift.js',
  'check-root-drift': 'tools/check-root-drift.js',
};

function printHelp() {
  console.log(`
Compass Engine CLI

Usage:
  compass-engine <command> [options]

Commands:
  build                 Build distributable bundles from src/ into dist/
  push                  Push built bundles into a target project or workspace
  validate              Validate required source layout and secret hygiene
  create-bmad-module    Scaffold a custom BMAD module into src/bmad/modules/
  check-github-drift    Check drift between src/github and .github
  check-root-drift      Check drift between src/root and repository root files

Examples:
  compass-engine build
  compass-engine push --dry-run --targets bmad,planning,documentation
  compass-engine validate
`);
}

function runScript(scriptPath, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [scriptPath, ...args], {
      cwd: ROOT,
      stdio: 'inherit',
      env: process.env,
    });

    child.on('exit', (code) => {
      if (code === 0) {
        resolve();
        return;
      }
      reject(new Error(`Command failed with exit code ${code ?? 1}`));
    });

    child.on('error', reject);
  });
}

async function main() {
  const [command, ...args] = process.argv.slice(2);

  if (!command || command === '--help' || command === '-h') {
    printHelp();
    return;
  }

  const script = COMMANDS[command];
  if (!script) {
    console.error(`Unknown command: ${command}`);
    printHelp();
    process.exitCode = 1;
    return;
  }

  await runScript(path.join(ROOT, script), args);
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
