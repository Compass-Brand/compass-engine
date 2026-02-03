#!/usr/bin/env node
/**
 * Compass Engine Build Script
 *
 * Compiles src/ into dist/.claude/ ready for distribution to projects.
 *
 * Usage:
 *   node scripts/build.js
 *   npm run build
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

const SRC = path.join(ROOT, 'src');
const DIST = path.join(ROOT, 'dist', '.claude');

// Directories to copy from src/claude to dist/.claude
const CLAUDE_DIRS = [
  'agents',
  'commands',
  'skills',
  'rules',
  'contexts',
  'config',
  'scripts',
];

// Files that are generated or need special handling
const LOCAL_ONLY_PATHS = [
  'settings.local.json',
  'scratchpad',
  'commands/local',
];

/**
 * Check if a relative path should be skipped based on LOCAL_ONLY_PATHS
 * Returns true if the path matches or is nested under any skip path
 */
function shouldSkip(relativePath, skipPaths) {
  if (!skipPaths || skipPaths.length === 0) {
    return false;
  }
  // Normalize to forward slashes for consistent comparison
  const normalizedPath = relativePath.replace(/\\/g, '/');
  return skipPaths.some((skipPath) => {
    const normalizedSkip = skipPath.replace(/\\/g, '/');
    return (
      normalizedPath === normalizedSkip ||
      normalizedPath.startsWith(normalizedSkip + '/')
    );
  });
}

/**
 * Recursively copy a directory, optionally skipping paths
 * @param {string} src - Source directory
 * @param {string} dest - Destination directory
 * @param {string} baseDir - Base directory for computing relative paths (for skip logic)
 * @param {string[]} skipPaths - Array of relative paths to skip
 */
async function copyDir(src, dest, baseDir = null, skipPaths = []) {
  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    // Compute relative path from base directory for skip checking
    const relativePath = baseDir
      ? path.relative(baseDir, srcPath)
      : entry.name;

    if (shouldSkip(relativePath, skipPaths)) {
      console.log(`    Skipping local-only path: ${relativePath}`);
      continue;
    }

    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath, baseDir, skipPaths);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

/**
 * Clean the dist directory
 */
async function clean() {
  console.log('Cleaning dist/.claude...');
  try {
    await fs.rm(DIST, { recursive: true, force: true });
  } catch (err) {
    // Directory might not exist
  }
  await fs.mkdir(DIST, { recursive: true });
}

/**
 * Copy Claude configuration directories
 */
async function copyClaude() {
  console.log('Copying Claude configuration...');
  const srcClaude = path.join(SRC, 'claude');

  for (const dir of CLAUDE_DIRS) {
    const srcDir = path.join(srcClaude, dir);
    const destDir = path.join(DIST, dir);

    try {
      await fs.access(srcDir);
      console.log(`  Copying ${dir}/`);
      // Pass srcClaude as baseDir so relative paths are computed from src/claude
      // This allows LOCAL_ONLY_PATHS like 'commands/local' to match correctly
      await copyDir(srcDir, destDir, srcClaude, LOCAL_ONLY_PATHS);
    } catch (err) {
      console.log(`  Skipping ${dir}/ (not found)`);
    }
  }
}

/**
 * Generate settings.json from template
 */
async function generateSettings() {
  console.log('Generating settings.json...');
  const templatePath = path.join(SRC, 'claude', 'templates', 'settings.json.template');
  const destPath = path.join(DIST, 'settings.json');

  try {
    const template = await fs.readFile(templatePath, 'utf-8');
    await fs.writeFile(destPath, template);
    console.log('  Created settings.json');
  } catch (err) {
    console.log('  No template found, skipping settings.json');
  }

  // Copy example for reference
  const examplePath = path.join(SRC, 'claude', 'templates', 'settings.local.json.example');
  try {
    await fs.access(examplePath);
    await fs.copyFile(examplePath, path.join(DIST, 'settings.local.json.example'));
    console.log('  Created settings.local.json.example');
  } catch (err) {
    // Skip if not found
  }
}

/**
 * Copy hook scripts from src/scripts/claude/hooks
 */
async function copyHooks() {
  console.log('Copying hook scripts...');
  const srcHooks = path.join(SRC, 'scripts', 'claude', 'hooks');
  const destHooks = path.join(DIST, 'scripts');

  try {
    await fs.access(srcHooks);
    await copyDir(srcHooks, destHooks);
    console.log('  Copied hook scripts');
  } catch (err) {
    console.log('  No hook scripts found');
  }
}

/**
 * Generate a README for the dist output
 */
async function generateReadme() {
  console.log('Generating README...');
  const readme = `# Compass Engine - Claude Code Configuration

This directory contains Claude Code configuration generated by compass-engine.

## Contents

- \`agents/\` - Agent definitions for specialized tasks
- \`commands/\` - Slash commands for common operations
- \`skills/\` - Reusable skill definitions
- \`rules/\` - Governance and coding rules
- \`contexts/\` - Context mode configurations
- \`config/\` - Configuration files
- \`scripts/\` - Hook scripts
- \`settings.json\` - Default settings
- \`settings.local.json.example\` - Example local settings

## Local Customization

Create \`settings.local.json\` for machine-specific settings.
Create \`commands/local/\` for project-specific commands.

These paths are preserved during updates from compass-engine.

## Updates

To update from compass-engine:
\`\`\`bash
cd compass-engine
npm run build
npm run push -- --project /path/to/project
\`\`\`

Generated by compass-engine build system.
`;
  await fs.writeFile(path.join(DIST, 'README.md'), readme);
  console.log('  Created README.md');
}

/**
 * Validate the build output
 */
async function validate() {
  console.log('Validating build...');
  const requiredDirs = ['agents', 'commands', 'skills', 'rules'];
  let valid = true;

  for (const dir of requiredDirs) {
    const dirPath = path.join(DIST, dir);
    try {
      const stat = await fs.stat(dirPath);
      if (!stat.isDirectory()) {
        console.error(`  ERROR: ${dir} is not a directory`);
        valid = false;
      } else {
        const files = await fs.readdir(dirPath);
        console.log(`  ✓ ${dir}/ (${files.length} items)`);
      }
    } catch (err) {
      console.error(`  ERROR: ${dir}/ not found`);
      valid = false;
    }
  }

  if (!valid) {
    throw new Error('Build validation failed');
  }
}

/**
 * Main build function
 */
async function build() {
  console.log('');
  console.log('=================================');
  console.log('  Compass Engine Build');
  console.log('=================================');
  console.log('');

  const startTime = Date.now();

  await clean();
  await copyClaude();
  await generateSettings();
  await copyHooks();
  await generateReadme();
  await validate();

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
  console.log('');
  console.log(`Build completed in ${elapsed}s`);
  console.log(`Output: ${DIST}`);
  console.log('');
}

// Run build
build().catch((err) => {
  console.error('Build failed:', err.message);
  process.exit(1);
});
