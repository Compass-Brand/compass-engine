#!/usr/bin/env node
/**
 * Compass Engine Push Script
 *
 * Pushes built bundles from dist/ to target projects.
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const DIST_ROOT = path.join(ROOT, 'dist');
const DEFAULT_PROJECT_CANDIDATES = [
  '.',
  'compass-forge',
  'compass-services',
  'compass-initiative',
  'compass-modules',
  'compass-brand-infrastructure',
  'compass-brand-setup',
  'mcps',
  'legacy-system-analyzer',
  'competitor-analysis-toolkit',
];

const TARGETS = {
  claude: {
    destName: '.claude',
    distName: '.claude',
    localOnly: ['settings.local.json', 'scratchpad', 'commands/local'],
  },
  codex: {
    destName: '.codex',
    distName: '.codex',
    localOnly: [
      'auth.json',
      'history.jsonl',
      'models_cache.json',
      'sessions',
      'tmp',
      'version.json',
    ],
  },
  opencode: {
    destName: '.opencode',
    distName: '.opencode',
    localOnly: ['state', 'cache'],
  },
  github: {
    destName: '.github',
    distName: '.github',
    localOnly: [],
  },
  root: {
    destName: '',
    distName: 'root',
    localOnly: [],
    replace: false,
  },
};

const DEFAULT_TARGETS = ['claude', 'codex', 'opencode', 'github', 'root'];

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    project: process.cwd(),
    all: false,
    dryRun: false,
    targets: [...DEFAULT_TARGETS],
    projectsConfig: null,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--project' && args[i + 1]) {
      options.project = path.resolve(args[++i]);
    } else if (arg === '--all') {
      options.all = true;
    } else if (arg === '--dry-run') {
      options.dryRun = true;
    } else if (arg === '--targets' && args[i + 1]) {
      const list = args[++i]
        .split(',')
        .map((item) => item.trim().toLowerCase())
        .filter(Boolean);
      options.targets = list;
    } else if (arg === '--projects-config' && args[i + 1]) {
      options.projectsConfig = path.resolve(args[++i]);
    } else if (arg === '--help') {
      console.log(`
Compass Engine Push

Usage:
  compass-engine push [options]

Options:
  --project <path>       Push to specific project (default: current directory)
  --all                  Push to all discovered Compass Brand projects
  --targets <list>       Comma-separated targets (claude,codex,opencode,github,root)
  --projects-config <p>  Optional file with one project path per line
  --dry-run              Show actions without modifying files
  --help                 Show this message
`);
      process.exit(0);
    }
  }

  return options;
}

async function exists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

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

async function readRootManifest(projectPath) {
  const manifestPath = await getRootManifestPath(projectPath);
  try {
    const raw = await fs.readFile(manifestPath, 'utf-8');
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed.files)) return [];
    return parsed.files.filter((rel) => typeof rel === 'string');
  } catch (err) {
    if (err.code === 'ENOENT') return [];
    throw err;
  }
}

async function writeRootManifest(projectPath, files) {
  const manifestPath = await getRootManifestPath(projectPath);
  await fs.mkdir(path.dirname(manifestPath), { recursive: true });
  const payload = {
    version: 1,
    generatedAt: new Date().toISOString(),
    files: [...files].sort(),
  };
  await fs.writeFile(manifestPath, `${JSON.stringify(payload, null, 2)}\n`);
}

async function resolveGitDir(projectPath) {
  const gitPath = path.join(projectPath, '.git');
  if (!(await exists(gitPath))) return null;

  const stat = await fs.stat(gitPath);
  if (stat.isDirectory()) return gitPath;

  if (!stat.isFile()) return null;

  const content = await fs.readFile(gitPath, 'utf-8');
  const match = content.match(/^gitdir:\s*(.+)\s*$/im);
  if (!match) return null;

  return path.resolve(projectPath, match[1].trim());
}

async function getRootManifestPath(projectPath) {
  const gitDir = await resolveGitDir(projectPath);
  if (gitDir) {
    return path.join(gitDir, 'compass-engine-root-sync.json');
  }
  return path.join(projectPath, '.compass-engine', 'root-sync-manifest.json');
}

function resolveWithinProject(projectPath, relativePath) {
  const absolute = path.resolve(projectPath, relativePath);
  const normalizedProject = `${path.resolve(projectPath)}${path.sep}`;
  if (!absolute.startsWith(normalizedProject) && absolute !== path.resolve(projectPath)) {
    throw new Error(`Refusing to operate outside project root: ${relativePath}`);
  }
  return absolute;
}

async function syncRootTarget(projectPath, sourcePath, options) {
  const currentFiles = await listFilesRecursive(sourcePath);
  const previousFiles = await readRootManifest(projectPath);
  const staleFiles = previousFiles.filter((rel) => !currentFiles.includes(rel));

  if (options.dryRun) {
    console.log(`    [DRY RUN] Merge files from dist/root into project root`);
    if (staleFiles.length > 0) {
      console.log(`    [DRY RUN] Remove ${staleFiles.length} stale root-managed files`);
    }
    return;
  }

  for (const relPath of staleFiles) {
    await fs.rm(resolveWithinProject(projectPath, relPath), { recursive: true, force: true });
  }
  await copyDir(sourcePath, projectPath);
  await writeRootManifest(projectPath, currentFiles);
}

async function readContentOrDir(filePath) {
  try {
    const content = await fs.readFile(filePath);
    return { type: 'file', content };
  } catch (err) {
    if (err.code === 'EISDIR') {
      const entries = await fs.readdir(filePath, { withFileTypes: true });
      const contents = {};
      for (const entry of entries) {
        const entryPath = path.join(filePath, entry.name);
        const entryContent = await readContentOrDir(entryPath);
        if (entryContent !== null) contents[entry.name] = entryContent;
      }
      return { type: 'directory', contents };
    }
    if (err.code === 'ENOENT') return null;
    throw err;
  }
}

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

async function syncTarget(projectPath, targetName, options) {
  const target = TARGETS[targetName];
  if (!target) throw new Error(`Unknown target: ${targetName}`);

  const sourcePath = path.join(DIST_ROOT, target.distName);
  if (!(await exists(sourcePath))) {
    console.log(`  Skipping ${targetName}: dist/${target.distName} not found`);
    return;
  }

  const destPath = path.join(projectPath, target.destName);
  const displayName = target.destName || '(project root files)';
  console.log(`  Syncing ${displayName}...`);

  if (targetName === 'root') {
    await syncRootTarget(projectPath, sourcePath, options);
    return;
  }

  if (options.dryRun) {
    if (target.replace === false) {
      console.log(`    [DRY RUN] Merge files from dist/${target.distName} into project root`);
    } else {
      console.log(`    [DRY RUN] Replace ${target.destName} from dist/${target.distName}`);
    }
    return;
  }

  const backups = {};
  for (const relPath of target.localOnly) {
    const backup = await readContentOrDir(path.join(destPath, relPath));
    if (backup !== null) backups[relPath] = backup;
  }

  if (target.replace === false) {
    await copyDir(sourcePath, destPath);
  } else {
    await fs.rm(destPath, { recursive: true, force: true });
    await copyDir(sourcePath, destPath);
  }

  for (const relPath of target.localOnly) {
    const localPath = path.join(destPath, relPath);
    await fs.rm(localPath, { recursive: true, force: true });
    if (backups[relPath]) {
      await restoreContent(localPath, backups[relPath]);
    }
  }
}

async function loadProjectConfig(configPath, workspaceRoot) {
  try {
    const content = await fs.readFile(configPath, 'utf-8');
    const lines = content.split('\n');
    const paths = [];

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const projectPath = path.isAbsolute(trimmed) ? trimmed : path.join(workspaceRoot, trimmed);
      paths.push(projectPath);
    }

    return paths.length > 0 ? paths : null;
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw err;
  }
}

async function discoverProjects(workspaceRoot, configPath) {
  const projects = [];

  if (configPath) {
    const fromConfig = await loadProjectConfig(configPath, workspaceRoot);
    if (fromConfig) {
      for (const projectPath of fromConfig) {
        if (await exists(path.join(projectPath, '.git'))) projects.push(projectPath);
      }
      return projects;
    }
  }

  const envProjects = process.env.COMPASS_PROJECTS;
  if (envProjects) {
    for (const envPath of envProjects.split(path.delimiter)) {
      const trimmed = envPath.trim();
      if (!trimmed) continue;
      const projectPath = path.isAbsolute(trimmed) ? trimmed : path.join(workspaceRoot, trimmed);
      if (await exists(path.join(projectPath, '.git'))) projects.push(projectPath);
    }
    if (projects.length > 0) return projects;
  }

  const candidates = DEFAULT_PROJECT_CANDIDATES.map((candidate) =>
    candidate === '.' ? workspaceRoot : path.join(workspaceRoot, candidate),
  );

  for (const candidate of candidates) {
    if (await exists(path.join(candidate, '.git'))) projects.push(candidate);
  }

  return projects;
}

async function syncToProject(projectPath, options) {
  console.log(`\nSyncing to: ${projectPath}`);

  for (const targetName of options.targets) {
    await syncTarget(projectPath, targetName, options);
  }

  console.log('  OK project sync complete');
}

async function push() {
  const options = parseArgs();
  const invalidTargets = options.targets.filter((target) => !TARGETS[target]);
  if (invalidTargets.length > 0) {
    throw new Error(`Unknown targets: ${invalidTargets.join(', ')}`);
  }

  console.log('\n=================================');
  console.log('  Compass Engine Push');
  console.log('=================================');
  console.log(`Targets: ${options.targets.join(', ')}`);

  if (options.all) {
    const workspaceRoot = path.resolve(ROOT, '..', '..');
    const configPath =
      options.projectsConfig ||
      process.env.COMPASS_PROJECTS_FILE ||
      path.join(ROOT, '.compass-projects');
    const projects = await discoverProjects(workspaceRoot, configPath);
    console.log(`\nFound ${projects.length} projects`);

    for (const projectPath of projects) {
      if (path.resolve(projectPath) === path.resolve(ROOT)) continue;
      await syncToProject(projectPath, options);
    }
  } else {
    await syncToProject(options.project, options);
  }

  console.log('\nOK push complete\n');
}

push().catch((err) => {
  console.error('Push failed:', err.message);
  process.exit(1);
});
