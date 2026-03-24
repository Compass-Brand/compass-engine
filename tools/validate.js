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
  'src/cli.js',
  'src/index.js',
  'src/claude',
  'src/claude/commands',
  'src/claude/skills/bmad-method/SKILL.md',
  'src/codex',
  'src/codex/skills/bmad-method/SKILL.md',
  'src/codex/prompts/bmad-help.md',
  'src/bmad/BMAD-workflow.md',
  'src/bmad/modules/custom/bmm/module-help.csv',
  'src/documentation/README.md',
  'src/documentation/human/policies/documentation-governance.md',
  'src/documentation/ai/README.md',
  'src/planning/README.md',
  'src/planning/framework/README.md',
  'src/planning/templates/README.md',
  'src/opencode',
  'src/opencode/package.json',
  'src/opencode/agents/bmad-orchestrator.md',
  'src/opencode/commands',
  'src/opencode/plugins',
  'src/opencode/plugins/compass-beads.ts',
  'src/opencode/plugins/compass-beads/plugin.ts',
  'src/github/workflows',
  'src/root/.coderabbit.yaml',
  'src/root/.editorconfig',
  'src/root/.gitattributes',
];

const BMAD_REFERENCE_CSVS = [
  { relPath: 'src/bmad/_config/workflow-manifest.csv', pathColumn: 3 },
  { relPath: 'src/bmad/_config/bmad-help.csv', pathColumn: 5 },
  { relPath: 'src/bmad/modules/custom/bmm/module-help.csv', pathColumn: 5 },
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

function parseCsvLine(line) {
  const cells = [];
  let current = '';
  let inQuotes = false;

  for (let index = 0; index < line.length; index++) {
    const char = line[index];

    if (char === '"') {
      if (inQuotes && line[index + 1] === '"') {
        current += '"';
        index += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === ',' && !inQuotes) {
      cells.push(current);
      current = '';
      continue;
    }

    current += char;
  }

  cells.push(current);
  return cells;
}

function mapInstalledBmadPathToSource(installedPath) {
  if (!installedPath.startsWith('_bmad/')) {
    return null;
  }
  return path.join(ROOT, 'src', 'bmad', installedPath.slice('_bmad/'.length));
}

async function validateBmadReferenceCsvs() {
  let ok = true;

  for (const { relPath, pathColumn } of BMAD_REFERENCE_CSVS) {
    const absolutePath = path.join(ROOT, relPath);
    const content = await fs.readFile(absolutePath, 'utf-8');
    const lines = content.split(/\r?\n/).filter(Boolean);

    for (const [lineIndex, line] of lines.entries()) {
      const cells = parseCsvLine(line);
      if (cells.length <= pathColumn) continue;
      const installedPath = cells[pathColumn]?.trim();
      const mappedPath = mapInstalledBmadPathToSource(installedPath);
      if (!mappedPath) continue;

      try {
        await fs.access(mappedPath);
      } catch {
        console.error(
          `ERROR broken BMAD manifest reference in ${relPath}:${lineIndex + 1} -> ${installedPath}`,
        );
        ok = false;
      }
    }
  }

  if (ok) console.log('OK BMAD manifest workflow references');
  return ok;
}

async function validateCustomBmadAgentExecPaths() {
  const agentsRoot = path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'bmm', 'agents');
  const files = await listFilesRecursive(agentsRoot);
  let ok = true;

  for (const filePath of files) {
    if (!filePath.endsWith('.agent.yaml')) continue;
    const content = await fs.readFile(filePath, 'utf-8');
    const matches = content.matchAll(/exec:\s*"(\{project-root\}\/_bmad\/[^"]+)"/g);

    for (const match of matches) {
      const installedPath = match[1].replace('{project-root}/', '');
      const mappedPath = mapInstalledBmadPathToSource(installedPath);
      if (!mappedPath) continue;

      try {
        await fs.access(mappedPath);
      } catch {
        console.error(
          `ERROR broken BMAD agent exec reference in ${path.relative(ROOT, filePath)} -> ${installedPath}`,
        );
        ok = false;
      }
    }
  }

  if (ok) console.log('OK BMAD custom agent exec references');
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

async function validate() {
  console.log('\n=================================');
  console.log('  Compass Engine Validate');
  console.log('=================================\n');

  const checks = await Promise.all([
    validateRequiredPaths(),
    validateCodexConfig(),
    validateSourceSecretScan(),
    validateBmadReferenceCsvs(),
    validateCustomBmadAgentExecPaths(),
  ]);

  if (checks.every(Boolean)) {
    console.log('\nValidation passed\n');
    return;
  }

  throw new Error('Validation failed');
}

const isDirectRun = process.argv[1] && path.resolve(process.argv[1]) === __filename;

if (isDirectRun) {
  validate().catch((err) => {
    console.error(err.message);
    process.exit(1);
  });
}

export { validate };
