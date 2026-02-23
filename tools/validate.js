#!/usr/bin/env node
/**
 * Compass Engine Validate Script
 *
 * Validates source layout and checks for obvious secret leaks.
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

const REQUIRED_PATHS = [
  'tools/build.js',
  'tools/push.js',
  'src/claude',
  'src/codex/skills',
  'src/codex/prompts',
  'src/bmad/modules',
  'src/opencode/agent',
  'src/opencode/command',
  'src/opencode/plugins',
  'src/github/workflows',
];

async function exists(relPath) {
  try {
    await fs.access(path.join(ROOT, relPath));
    return true;
  } catch {
    return false;
  }
}

async function validateRequiredPaths() {
  let ok = true;
  for (const relPath of REQUIRED_PATHS) {
    if (await exists(relPath)) {
      console.log(`OK ${relPath}`);
    } else {
      console.error(`ERROR missing: ${relPath}`);
      ok = false;
    }
  }
  return ok;
}

async function validateCodexConfig() {
  const configPath = path.join(ROOT, 'src', 'codex', 'config.toml');
  if (!(await exists('src/codex/config.toml'))) {
    console.error('ERROR missing: src/codex/config.toml');
    return false;
  }

  const content = await fs.readFile(configPath, 'utf-8');
  const blockedPatterns = [/ctx7sk-/i, /api[_-]?key\s*=\s*['"][^'"]+['"]/i];
  for (const pattern of blockedPatterns) {
    if (pattern.test(content)) {
      console.error(`ERROR src/codex/config.toml contains blocked secret-like pattern: ${pattern}`);
      return false;
    }
  }

  console.log('OK src/codex/config.toml secret scan');
  return true;
}

async function run() {
  console.log('\n=================================');
  console.log('  Compass Engine Validate');
  console.log('=================================\n');

  const checks = await Promise.all([
    validateRequiredPaths(),
    validateCodexConfig(),
  ]);

  if (checks.every(Boolean)) {
    console.log('\nValidation passed\n');
    return;
  }

  throw new Error('Validation failed');
}

run().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
