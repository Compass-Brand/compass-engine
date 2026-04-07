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
  'src/bmad/modules/custom/compass-skills/module.yaml',
  'src/bmad/modules/native/bmm-skills/module.yaml',
  'src/bmad/modules/native/bmm-skills/module-help.csv',
  'src/bmad/modules/native/core-skills/module.yaml',
  'src/bmad/modules/native/core-skills/module-help.csv',
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
  'src/opencode/plugins/compass-handoff.ts',
  'src/opencode/plugins/compass-handoff/plugin.ts',
  'src/opencode/plugins/compass-type-inject.ts',
  'src/opencode/plugins/compass-type-inject/plugin.ts',
  'src/opencode/plugins/compass-worktree.ts',
  'src/opencode/plugins/compass-worktree/plugin.ts',
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

async function validateSkillFormat() {
  let ok = true;
  const moduleRoots = [
    path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'bmm-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'core-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'bmm-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'core-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'compass-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'bmad-builder-skills'),
  ];

  for (const moduleRoot of moduleRoots) {
    if (!(await exists(path.relative(ROOT, moduleRoot)))) continue;
    const skillFiles = await listFilesRecursive(moduleRoot);

    for (const filePath of skillFiles) {
      const normalized = filePath.replace(/\\/g, '/');
      if (!normalized.endsWith('/SKILL.md')) continue;
      const content = await fs.readFile(filePath, 'utf-8');
      const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);

      if (!frontmatterMatch) {
        console.error(`ERROR ${path.relative(ROOT, filePath)}: missing YAML frontmatter`);
        ok = false;
        continue;
      }

      const nameMatch = frontmatterMatch[1].match(/^name:\s*(.+)$/m);
      if (!nameMatch) {
        console.error(`ERROR ${path.relative(ROOT, filePath)}: missing 'name' in frontmatter`);
        ok = false;
        continue;
      }

      const skillName = nameMatch[1].trim().replace(/['"]/g, '');
      const dirName = path.basename(path.dirname(filePath));
      if (skillName !== dirName) {
        console.error(
          `ERROR ${path.relative(ROOT, filePath)}: name '${skillName}' does not match directory '${dirName}'`,
        );
        ok = false;
      }
    }
  }

  if (ok) console.log('OK skill format validation');
  return ok;
}

function parseCsvLine(line) {
  const cells = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') { current += '"'; i++; }
      else { inQuotes = !inQuotes; }
      continue;
    }
    if (char === ',' && !inQuotes) { cells.push(current); current = ''; continue; }
    current += char;
  }
  cells.push(current);
  return cells;
}

async function validateGeneratedManifests() {
  let ok = true;

  const moduleRoots = [
    path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'bmm-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'core-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'bmm-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'core-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'compass-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'bmad-builder-skills'),
  ];

  for (const moduleRoot of moduleRoots) {
    if (!(await exists(path.relative(ROOT, moduleRoot)))) continue;
    const files = await listFilesRecursive(moduleRoot);

    for (const filePath of files) {
      // NOTE: validate.js listFilesRecursive returns FULL absolute paths
      const normalized = filePath.replace(/\\/g, '/');
      if (!normalized.endsWith('/SKILL.md')) continue;

      const skillDir = path.dirname(filePath);
      const dirName = path.basename(skillDir);
      // Agent skills start with "bmad-agent-" or "bmad-master"
      if (!dirName.startsWith('bmad-agent-') && dirName !== 'bmad-master') continue;

      const manifestPath = path.join(skillDir, 'bmad-skill-manifest.yaml');
      try {
        await fs.access(manifestPath);
      } catch {
        console.error(`ERROR agent skill ${dirName} missing bmad-skill-manifest.yaml`);
        ok = false;
      }
    }
  }

  if (ok) console.log('OK agent manifest validation');
  return ok;
}

async function validateModuleHelpDeps() {
  let ok = true;

  // Collect all known skill names from SKILL.md directories
  const knownSkills = new Set();
  const moduleRoots = [
    path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'bmm-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'native', 'core-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'bmm-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'core-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'compass-skills'),
    path.join(ROOT, 'src', 'bmad', 'modules', 'custom', 'bmad-builder-skills'),
  ];

  for (const moduleRoot of moduleRoots) {
    if (!(await exists(path.relative(ROOT, moduleRoot)))) continue;
    const files = await listFilesRecursive(moduleRoot);
    for (const filePath of files) {
      if (!filePath.replace(/\\/g, '/').endsWith('/SKILL.md')) continue;
      knownSkills.add(path.basename(path.dirname(filePath)));
    }
  }

  // Check after/before refs in each module-help.csv
  const moduleHelpFiles = [
    'src/bmad/modules/native/bmm-skills/module-help.csv',
    'src/bmad/modules/native/core-skills/module-help.csv',
    'src/bmad/modules/custom/compass-skills/module-help.csv',
    'src/bmad/modules/custom/bmad-builder-skills/module-help.csv',
  ];

  for (const relPath of moduleHelpFiles) {
    if (!(await exists(relPath))) continue;
    const content = await fs.readFile(path.join(ROOT, relPath), 'utf-8');
    const lines = content.split(/\r?\n/).filter(Boolean);
    const header = parseCsvLine(lines[0]);
    const afterIdx = header.indexOf('after');
    const beforeIdx = header.indexOf('before');
    if (afterIdx < 0 && beforeIdx < 0) continue;

    for (let i = 1; i < lines.length; i++) {
      const cells = parseCsvLine(lines[i]);
      // Guard: skip rows with misaligned column count (known issue in some native CSVs)
      if (cells.length !== header.length) continue;
      for (const [colName, colIdx] of [['after', afterIdx], ['before', beforeIdx]]) {
        if (colIdx < 0 || !cells[colIdx]?.trim()) continue;
        const refs = cells[colIdx].split(/[,;]/).map((r) => r.trim()).filter(Boolean);
        for (const ref of refs) {
          // Strip :action suffix (e.g., "bmad-create-story:create" -> "bmad-create-story")
          const skillName = ref.includes(':') ? ref.split(':')[0] : ref;
          if (!knownSkills.has(skillName)) {
            console.error(`ERROR ${relPath}:${i + 1} ${colName} ref '${skillName}' is not a known skill`);
            ok = false;
          }
        }
      }
    }
  }

  if (ok) console.log('OK module-help dependency validation');
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
    validateSkillFormat(),
    validateGeneratedManifests(),
    validateModuleHelpDeps(),
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
