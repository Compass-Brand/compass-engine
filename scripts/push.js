#!/usr/bin/env node
/**
 * Compass Engine Push Script
 *
 * Pushes built dist/.claude to target projects with local-only preservation.
 *
 * Usage:
 *   node scripts/push.js                    # Push to current directory
 *   node scripts/push.js --project /path    # Push to specific project
 *   node scripts/push.js --all              # Push to all discovered projects
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

const DIST = path.join(ROOT, 'dist', '.claude');

// Paths that should be preserved during sync (not overwritten)
const LOCAL_ONLY_PATHS = [
  'settings.local.json',
  'scratchpad',
  'commands/local',
];

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    project: process.cwd(),
    all: false,
    force: false,
    dryRun: false,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--project' && args[i + 1]) {
      options.project = path.resolve(args[++i]);
    } else if (arg === '--all') {
      options.all = true;
    } else if (arg === '--force') {
      options.force = true;
    } else if (arg === '--dry-run') {
      options.dryRun = true;
    } else if (arg === '--help') {
      console.log(`
Compass Engine Push

Usage:
  compass-engine push [options]

Options:
  --project <path>  Push to specific project (default: current directory)
  --all             Push to all Compass Brand projects
  --force           Overwrite without prompting
  --dry-run         Show what would be done without making changes
  --help            Show this help message
`);
      process.exit(0);
    }
  }

  return options;
}

/**
 * Recursively copy a directory
 */
async function copyDir(src, dest) {
  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

/**
 * Read content of file or directory for backup
 */
async function readContentOrDir(filePath) {
  const stat = await fs.stat(filePath);
  if (stat.isDirectory()) {
    const entries = await fs.readdir(filePath, { withFileTypes: true });
    const contents = {};
    for (const entry of entries) {
      const entryPath = path.join(filePath, entry.name);
      contents[entry.name] = await readContentOrDir(entryPath);
    }
    return { type: 'directory', contents };
  } else {
    const content = await fs.readFile(filePath);
    return { type: 'file', content };
  }
}

/**
 * Restore content from backup
 */
async function restoreContent(filePath, backup) {
  if (backup.type === 'directory') {
    await fs.mkdir(filePath, { recursive: true });
    for (const [name, content] of Object.entries(backup.contents)) {
      await restoreContent(path.join(filePath, name), content);
    }
  } else {
    await fs.mkdir(path.dirname(filePath), { recursive: true });
    await fs.writeFile(filePath, backup.content);
  }
}

/**
 * Check if path exists
 */
async function exists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Sync dist/.claude to target project
 */
async function syncToProject(projectPath, options) {
  const claudePath = path.join(projectPath, '.claude');

  console.log(`\nSyncing to: ${projectPath}`);

  // Check if dist exists and is built
  if (!(await exists(DIST))) {
    console.error('ERROR: dist/.claude not found. Run "npm run build" first.');
    process.exit(1);
  }

  // 1. Backup local-only content
  console.log('  Backing up local content...');
  const localBackups = {};
  for (const localPath of LOCAL_ONLY_PATHS) {
    const fullPath = path.join(claudePath, localPath);
    if (await exists(fullPath)) {
      console.log(`    Preserving: ${localPath}`);
      localBackups[localPath] = await readContentOrDir(fullPath);
    }
  }

  if (options.dryRun) {
    console.log('  [DRY RUN] Would remove existing .claude');
    console.log('  [DRY RUN] Would copy from dist/.claude');
    console.log('  [DRY RUN] Would restore local content');
    return;
  }

  // 2. Remove existing .claude
  if (await exists(claudePath)) {
    console.log('  Removing existing .claude...');
    await fs.rm(claudePath, { recursive: true, force: true });
  }

  // 3. Copy fresh from dist/
  console.log('  Copying from compass-engine...');
  await copyDir(DIST, claudePath);

  // 4. Restore local-only content
  if (Object.keys(localBackups).length > 0) {
    console.log('  Restoring local content...');
    for (const [localPath, content] of Object.entries(localBackups)) {
      const fullPath = path.join(claudePath, localPath);
      console.log(`    Restoring: ${localPath}`);
      await restoreContent(fullPath, content);
    }
  }

  console.log('  ✓ Sync complete');
}

/**
 * Discover Compass Brand projects in workspace
 */
async function discoverProjects(workspaceRoot) {
  const projects = [];

  // Direct check for common project locations
  const potentialPaths = [
    workspaceRoot,
    path.join(workspaceRoot, 'compass-forge'),
    path.join(workspaceRoot, 'compass-services'),
    path.join(workspaceRoot, 'compass-initiative'),
    path.join(workspaceRoot, 'compass-modules'),
    path.join(workspaceRoot, 'compass-brand-infrastructure'),
    path.join(workspaceRoot, 'compass-brand-setup'),
    path.join(workspaceRoot, 'mcps'),
    path.join(workspaceRoot, 'legacy-system-analyzer'),
    path.join(workspaceRoot, 'competitor-analysis-toolkit'),
  ];

  for (const projectPath of potentialPaths) {
    // Check if it's a git repository (has .git)
    if (await exists(path.join(projectPath, '.git'))) {
      projects.push(projectPath);
    }
  }

  return projects;
}

/**
 * Main push function
 */
async function push() {
  const options = parseArgs();

  console.log('');
  console.log('=================================');
  console.log('  Compass Engine Push');
  console.log('=================================');

  if (options.all) {
    // Discover workspace root (assuming we're in compass-engine within compass-forge)
    const workspaceRoot = path.resolve(ROOT, '..', '..');
    console.log(`\nDiscovering projects in: ${workspaceRoot}`);

    const projects = await discoverProjects(workspaceRoot);
    console.log(`Found ${projects.length} projects`);

    for (const project of projects) {
      // Skip compass-engine itself
      if (path.resolve(project) === path.resolve(ROOT)) continue;

      await syncToProject(project, options);
    }
  } else {
    await syncToProject(options.project, options);
  }

  console.log('\n✓ Push complete\n');
}

// Run push
push().catch((err) => {
  console.error('Push failed:', err.message);
  process.exit(1);
});
