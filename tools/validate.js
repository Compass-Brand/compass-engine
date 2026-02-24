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
const SOURCE_ROOT = path.join(ROOT, 'src');

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
  'src/root/.coderabbit.yaml',
  'src/root/.editorconfig',
  'src/root/.gitattributes',
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

function shouldScanSourceFile(filePath) {
  const normalized = filePath.replace(/\\/g, '/');
  const skipSuffixes = ['.example', '.template', '.sample'];
  if (skipSuffixes.some((suffix) => normalized.endsWith(suffix))) return false;
  if (normalized.includes('/fixtures/')) return false;

  const allowedExtensions = new Set([
    '.js',
    '.mjs',
    '.cjs',
    '.ts',
    '.tsx',
    '.json',
    '.toml',
    '.yaml',
    '.yml',
    '.env',
    '.ini',
    '.conf',
  ]);
  return allowedExtensions.has(path.extname(filePath).toLowerCase());
}

async function listFilesRecursive(rootPath, currentPath = rootPath, files = []) {
  const entries = await fs.readdir(currentPath, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(currentPath, entry.name);
    if (entry.isDirectory()) {
      await listFilesRecursive(rootPath, fullPath, files);
    } else {
      files.push(fullPath);
    }
  }
  return files;
}

function isLikelyPlaceholder(value) {
  const normalized = value.toLowerCase();
  return (
    normalized.includes('example') ||
    normalized.includes('changeme') ||
    normalized.includes('your_') ||
    normalized.includes('your-') ||
    normalized.includes('dummy') ||
    normalized.includes('test') ||
    normalized.includes('${') ||
    normalized.includes('{{')
  );
}

function findSecretIndicators(content) {
  const lines = content.split('\n');
  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx];

    if (/\bctx7sk-[a-z0-9]{20,}\b/i.test(line)) {
      return `line ${idx + 1}: ctx7 token pattern`;
    }

    if (/\b(ghp|gho|sk)-[a-z0-9]{20,}\b/i.test(line)) {
      return `line ${idx + 1}: API token-like pattern`;
    }

    const apiKeyMatch = line.match(/api[_-]?key\s*[:=]\s*["']([^"']+)["']/i);
    if (apiKeyMatch && !isLikelyPlaceholder(apiKeyMatch[1])) {
      return `line ${idx + 1}: api_key assignment`;
    }
  }

  return null;
}

async function validateSourceSecretScan() {
  const files = await listFilesRecursive(SOURCE_ROOT);
  let ok = true;
  for (const filePath of files) {
    if (!shouldScanSourceFile(filePath)) continue;
    const content = await fs.readFile(filePath, 'utf-8');
    const finding = findSecretIndicators(content);
    if (finding) {
      console.error(`ERROR potential secret in ${path.relative(ROOT, filePath)} (${finding})`);
      ok = false;
    }
  }
  if (ok) console.log('OK source secret scan');
  return ok;
}

async function run() {
  console.log('\n=================================');
  console.log('  Compass Engine Validate');
  console.log('=================================\n');

  const checks = await Promise.all([
    validateRequiredPaths(),
    validateCodexConfig(),
    validateSourceSecretScan(),
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
