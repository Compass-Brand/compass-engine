#!/usr/bin/env node
/**
 * Compass Engine Build Script
 *
 * Builds distributable development bundles for Compass Brand repos.
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

const SRC = path.join(ROOT, 'src');
const DIST_ROOT = path.join(ROOT, 'dist');

const CLAUDE_DIST = path.join(DIST_ROOT, '.claude');
const CLAUDE_SRC = path.join(SRC, 'claude');
const CLAUDE_DIRS = ['agents', 'commands', 'skills', 'rules', 'contexts', 'config', 'scripts'];

const TARGETS = [
  {
    name: 'bmad',
    src: path.join(SRC, 'bmad'),
    dist: path.join(DIST_ROOT, '_bmad'),
    required: ['BMAD-workflow.md', 'modules/custom/bmm/module-help.csv'],
  },
  {
    name: 'planning',
    src: path.join(SRC, 'planning'),
    dist: path.join(DIST_ROOT, 'planning'),
    required: ['README.md', 'current/phase.md', 'roadmap/roadmap.md', 'templates/README.md'],
  },
  {
    name: 'documentation',
    src: path.join(SRC, 'documentation'),
    dist: path.join(DIST_ROOT, 'docs'),
    required: ['README.md', 'human/policies/documentation-governance.md', 'ai/README.md'],
    skipPaths: ['README.md'],
  },
  {
    name: 'codex',
    src: path.join(SRC, 'codex'),
    dist: path.join(DIST_ROOT, '.codex'),
    required: ['skills', 'prompts'],
  },
  {
    name: 'opencode',
    src: path.join(SRC, 'opencode'),
    dist: path.join(DIST_ROOT, '.opencode'),
    required: ['agent', 'command'],
  },
  {
    name: 'github',
    src: path.join(SRC, 'github'),
    dist: path.join(DIST_ROOT, '.github'),
    required: ['workflows'],
  },
  {
    name: 'beads',
    src: path.join(SRC, 'beads'),
    dist: path.join(DIST_ROOT, 'beads'),
    required: ['README.md'],
  },
  {
    name: 'root',
    src: path.join(SRC, 'root'),
    dist: path.join(DIST_ROOT, 'root'),
    required: ['.coderabbit.yaml'],
  },
];

const CLAUDE_LOCAL_ONLY = ['settings.local.json', 'scratchpad', 'commands/local'];

const DIST_BMAD_REFERENCE_CSVS = [
  { relPath: '_config/workflow-manifest.csv', pathColumn: 3 },
  { relPath: '_config/bmad-help.csv', pathColumn: 5 },
  { relPath: 'modules/custom/bmm/module-help.csv', pathColumn: 5 },
];

function normalizePath(filePath) {
  return filePath.replace(/\\/g, '/');
}

function shouldSkip(relativePath, skipPaths) {
  if (!skipPaths || skipPaths.length === 0) return false;

  const normalizedPath = normalizePath(relativePath);
  return skipPaths.some((skipPath) => {
    const normalizedSkip = normalizePath(skipPath);
    return normalizedPath === normalizedSkip || normalizedPath.startsWith(`${normalizedSkip}/`);
  });
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

async function exists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function copyDir(src, dest, options = {}) {
  const { baseDir = null, skipPaths = [] } = options;

  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    const relativePath = baseDir ? path.relative(baseDir, srcPath) : entry.name;
    if (shouldSkip(relativePath, skipPaths)) continue;

    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath, options);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

async function listFilesRecursive(rootPath, currentPath = rootPath, files = []) {
  const entries = await fs.readdir(currentPath, { withFileTypes: true });
  for (const entry of entries) {
    const entryPath = path.join(currentPath, entry.name);
    if (entry.isDirectory()) {
      await listFilesRecursive(rootPath, entryPath, files);
    } else {
      files.push(path.relative(rootPath, entryPath).replace(/\\/g, '/'));
    }
  }
  return files;
}

function mapInstalledBmadPathToDist(installedPath) {
  if (!installedPath.startsWith('_bmad/')) {
    return null;
  }
  return path.join(DIST_ROOT, installedPath);
}

async function validateDistBmadReferences() {
  let isValid = true;

  for (const { relPath, pathColumn } of DIST_BMAD_REFERENCE_CSVS) {
    const absolutePath = path.join(DIST_ROOT, '_bmad', relPath);
    const content = await fs.readFile(absolutePath, 'utf-8');
    const lines = content.split(/\r?\n/).filter(Boolean);

    for (const [lineIndex, line] of lines.entries()) {
      const cells = parseCsvLine(line);
      if (cells.length <= pathColumn) continue;
      const installedPath = cells[pathColumn]?.trim();
      const mappedPath = mapInstalledBmadPathToDist(installedPath);
      if (!mappedPath) continue;

      if (!(await exists(mappedPath))) {
        console.error(
          `  ERROR broken dist BMAD manifest reference in _bmad/${relPath}:${lineIndex + 1} -> ${installedPath}`,
        );
        isValid = false;
      }
    }
  }

  const agentsRoot = path.join(DIST_ROOT, '_bmad', 'modules', 'custom', 'bmm', 'agents');
  if (await exists(agentsRoot)) {
    const files = await listFilesRecursive(agentsRoot);
    for (const relativePath of files) {
      if (!relativePath.endsWith('.agent.yaml')) continue;
      const filePath = path.join(agentsRoot, relativePath);
      const content = await fs.readFile(filePath, 'utf-8');
      const matches = content.matchAll(/exec:\s*"(\{project-root\}\/_bmad\/[^"]+)"/g);

      for (const match of matches) {
        const installedPath = match[1].replace('{project-root}/', '');
        const mappedPath = mapInstalledBmadPathToDist(installedPath);
        if (!mappedPath) continue;

        if (!(await exists(mappedPath))) {
          console.error(
            `  ERROR broken dist BMAD agent exec reference in _bmad/modules/custom/bmm/agents/${relativePath} -> ${installedPath}`,
          );
          isValid = false;
        }
      }
    }
  }

  if (isValid) {
    console.log('  OK dist BMAD manifest and agent references');
  }

  return isValid;
}

async function cleanDist() {
  console.log('Cleaning dist/...');
  await fs.rm(DIST_ROOT, { recursive: true, force: true });
  await fs.mkdir(DIST_ROOT, { recursive: true });
}

async function buildClaude() {
  console.log('\nBuilding .claude...');
  await fs.mkdir(CLAUDE_DIST, { recursive: true });

  for (const dir of CLAUDE_DIRS) {
    const srcDir = path.join(CLAUDE_SRC, dir);
    const destDir = path.join(CLAUDE_DIST, dir);

    if (!(await exists(srcDir))) {
      console.log(`  Skipping ${dir}/ (not found)`);
      continue;
    }

    console.log(`  Copying ${dir}/`);
    await copyDir(srcDir, destDir, {
      baseDir: CLAUDE_SRC,
      skipPaths: CLAUDE_LOCAL_ONLY,
    });
  }

  const settingsTemplate = path.join(CLAUDE_SRC, 'templates', 'settings.json.template');
  if (await exists(settingsTemplate)) {
    const content = await fs.readFile(settingsTemplate, 'utf-8');
    await fs.writeFile(path.join(CLAUDE_DIST, 'settings.json'), content);
    console.log('  Generated settings.json');
  }

  const localSettingsTemplate = path.join(CLAUDE_SRC, 'templates', 'settings.local.json.example');
  if (await exists(localSettingsTemplate)) {
    await fs.copyFile(localSettingsTemplate, path.join(CLAUDE_DIST, 'settings.local.json.example'));
    console.log('  Copied settings.local.json.example');
  }

  const hooksSrc = path.join(SRC, 'scripts', 'claude', 'hooks');
  if (await exists(hooksSrc)) {
    await copyDir(hooksSrc, path.join(CLAUDE_DIST, 'scripts'));
    console.log('  Copied Claude hook scripts');
  }

  const readme = `# Compass Engine - Claude Bundle\n\nGenerated bundle for \`.claude/\` distribution.\n`;
  await fs.writeFile(path.join(CLAUDE_DIST, 'README.md'), readme);
}

async function buildTarget(target) {
  const { name, src, dist, skipPaths = [] } = target;
  if (!(await exists(src))) {
    console.log(`\nSkipping .${name}: source not found (${path.relative(ROOT, src)})`);
    return false;
  }

  console.log(`\nBuilding ${path.basename(dist)}...`);

  if (name === 'planning') {
    await fs.mkdir(dist, { recursive: true });
    await fs.copyFile(path.join(src, 'README.md'), path.join(dist, 'README.md'));
    await copyDir(path.join(src, 'docs'), path.join(dist, 'docs'));
    await copyDir(path.join(src, 'templates'), path.join(dist, 'templates'));
    await copyDir(path.join(src, 'framework'), dist, {
      baseDir: path.join(src, 'framework'),
      skipPaths: ['README.md'],
    });
    return true;
  }

  await copyDir(src, dist, {
    baseDir: src,
    skipPaths,
  });
  return true;
}

async function validateBuild() {
  console.log('\nValidating build output...');

  const requiredChecks = [
    { label: '_bmad', path: path.join(DIST_ROOT, '_bmad') },
    { label: '_bmad/BMAD-workflow.md', path: path.join(DIST_ROOT, '_bmad', 'BMAD-workflow.md') },
    { label: '_bmad/modules/custom/bmm/module-help.csv', path: path.join(DIST_ROOT, '_bmad', 'modules', 'custom', 'bmm', 'module-help.csv') },
    { label: 'planning', path: path.join(DIST_ROOT, 'planning') },
    { label: 'planning/current/phase.md', path: path.join(DIST_ROOT, 'planning', 'current', 'phase.md') },
    { label: 'planning/roadmap/roadmap.md', path: path.join(DIST_ROOT, 'planning', 'roadmap', 'roadmap.md') },
    { label: 'docs', path: path.join(DIST_ROOT, 'docs') },
    { label: 'docs/human/policies/documentation-governance.md', path: path.join(DIST_ROOT, 'docs', 'human', 'policies', 'documentation-governance.md') },
    { label: '.claude', path: CLAUDE_DIST },
    { label: '.claude/README.md', path: path.join(CLAUDE_DIST, 'README.md') },
    { label: '.github/workflows', path: path.join(DIST_ROOT, '.github', 'workflows') },
    { label: 'root/.coderabbit.yaml', path: path.join(DIST_ROOT, 'root', '.coderabbit.yaml') },
    { label: 'root/.editorconfig', path: path.join(DIST_ROOT, 'root', '.editorconfig') },
    { label: 'root/.gitattributes', path: path.join(DIST_ROOT, 'root', '.gitattributes') },
  ];

  if (await exists(path.join(SRC, 'codex'))) {
    requiredChecks.push({ label: '.codex', path: path.join(DIST_ROOT, '.codex') });
  }

  if (await exists(path.join(SRC, 'opencode'))) {
    requiredChecks.push({ label: '.opencode', path: path.join(DIST_ROOT, '.opencode') });
  }

  let isValid = true;
  for (const check of requiredChecks) {
    if (await exists(check.path)) {
      console.log(`  OK ${check.label}`);
    } else {
      console.error(`  ERROR missing ${check.label}`);
      isValid = false;
    }
  }

  if (!(await validateDistBmadReferences())) {
    isValid = false;
  }

  if (!isValid) {
    throw new Error('Build validation failed');
  }
}

async function build() {
  console.log('\n=================================');
  console.log('  Compass Engine Build');
  console.log('=================================\n');

  const start = Date.now();

  await cleanDist();
  await buildClaude();
  for (const target of TARGETS) {
    await buildTarget(target);
  }
  await validateBuild();

  const elapsed = ((Date.now() - start) / 1000).toFixed(2);
  console.log(`\nBuild completed in ${elapsed}s`);
  console.log(`Output root: ${DIST_ROOT}\n`);
}

const isDirectRun = process.argv[1] && path.resolve(process.argv[1]) === __filename;

if (isDirectRun) {
  build().catch((err) => {
    console.error('Build failed:', err.message);
    process.exit(1);
  });
}

export { build };
