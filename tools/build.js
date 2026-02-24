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
const CLAUDE_REQUIRED_DIRS = ['agents', 'commands', 'skills', 'rules'];

const TARGETS = [
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

async function cleanDist() {
  console.log('Cleaning dist/...');
  await fs.rm(DIST_ROOT, { recursive: true, force: true });
  await fs.mkdir(DIST_ROOT, { recursive: true });
}

async function buildClaude() {
  console.log('\nBuilding .claude...');
  await fs.mkdir(CLAUDE_DIST, { recursive: true });

  for (const requiredDir of CLAUDE_REQUIRED_DIRS) {
    const requiredPath = path.join(CLAUDE_SRC, requiredDir);
    if (!(await exists(requiredPath))) {
      throw new Error(
        `Missing required Claude source directory: ${path.relative(ROOT, requiredPath)}`,
      );
    }
  }

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
  const { name, src, dist } = target;
  if (!(await exists(src))) {
    console.log(`\nSkipping .${name}: source not found (${path.relative(ROOT, src)})`);
    return false;
  }

  console.log(`\nBuilding ${path.basename(dist)}...`);
  await copyDir(src, dist);
  return true;
}

async function validateBuild() {
  console.log('\nValidating build output...');

  const requiredChecks = [
    { label: '.claude/agents', path: path.join(CLAUDE_DIST, 'agents') },
    { label: '.claude/commands', path: path.join(CLAUDE_DIST, 'commands') },
    { label: '.claude/skills', path: path.join(CLAUDE_DIST, 'skills') },
    { label: '.claude/rules', path: path.join(CLAUDE_DIST, 'rules') },
    { label: '.codex/skills', path: path.join(DIST_ROOT, '.codex', 'skills') },
    { label: '.codex/prompts', path: path.join(DIST_ROOT, '.codex', 'prompts') },
    { label: '.opencode/agent', path: path.join(DIST_ROOT, '.opencode', 'agent') },
    { label: '.opencode/command', path: path.join(DIST_ROOT, '.opencode', 'command') },
    { label: '.github/workflows', path: path.join(DIST_ROOT, '.github', 'workflows') },
    { label: 'root/.coderabbit.yaml', path: path.join(DIST_ROOT, 'root', '.coderabbit.yaml') },
    { label: 'root/.editorconfig', path: path.join(DIST_ROOT, 'root', '.editorconfig') },
    { label: 'root/.gitattributes', path: path.join(DIST_ROOT, 'root', '.gitattributes') },
  ];

  let isValid = true;
  for (const check of requiredChecks) {
    if (await exists(check.path)) {
      console.log(`  OK ${check.label}`);
    } else {
      console.error(`  ERROR missing ${check.label}`);
      isValid = false;
    }
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

build().catch((err) => {
  console.error('Build failed:', err.message);
  process.exit(1);
});
