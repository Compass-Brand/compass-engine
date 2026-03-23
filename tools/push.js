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
    syncStrategy: 'managed',
    manifestName: 'compass-engine-codex-sync.json',
  },
  opencode: {
    destName: '.opencode',
    distName: '.opencode',
    localOnly: ['state', 'cache'],
    syncStrategy: 'managed',
    manifestName: 'compass-engine-opencode-sync.json',
  },
  bmad: {
    destName: '_bmad',
    distName: '_bmad',
    localOnly: [],
  },
  planning: {
    destName: 'planning',
    distName: 'planning',
    localOnly: [],
    syncStrategy: 'managed',
    manifestName: 'compass-engine-planning-sync.json',
    cleanupPaths: ['framework'],
  },
  documentation: {
    destName: 'docs',
    distName: 'docs',
    localOnly: [],
    syncStrategy: 'managed',
    manifestName: 'compass-engine-docs-sync.json',
    preservePaths: ['README.md'],
  },
  github: {
    destName: '.github',
    distName: '.github',
    localOnly: [],
    syncStrategy: 'managed',
    manifestName: 'compass-engine-github-sync.json',
  },
  root: {
    destName: '',
    distName: 'root',
    localOnly: [],
    syncStrategy: 'managed',
    manifestName: 'compass-engine-root-sync.json',
  },
};

const DEFAULT_TARGETS = [
  'bmad',
  'planning',
  'documentation',
  'claude',
  'codex',
  'opencode',
  'github',
  'root',
];

const GITHUB_FEATURE_GROUPS = {
  baseline: [
    'codeowners',
    'dependabot',
    'quality-checks',
    'pr-size-labeler',
    'stale',
    'codeql',
  ],
  codeowners: ['CODEOWNERS'],
  dependabot: ['dependabot.yml'],
  'quality-checks': ['workflows/quality-checks.yml'],
  linting: ['workflows/linting.yml'],
  codeql: ['workflows/codeql.yml'],
  'pr-size-labeler': ['workflows/pr-size-labeler.yml'],
  stale: ['workflows/stale.yml'],
  necessist: ['workflows/necessist.yml'],
  'runtime-security': ['workflows/runtime-security.yml'],
  'submodule-security-monitoring': ['workflows/submodule-security-monitoring.yml'],
  'github-drift': ['workflows/github-drift.yml'],
  'profile-node': ['profiles/dependabot-node.yml'],
  'profile-python': ['profiles/dependabot-python.yml'],
  'profile-submodule-compass-engine': ['profiles/dependabot-submodule-compass-engine.yml'],
  'profile-submodule-bmad-method': ['profiles/dependabot-submodule-bmad-method.yml'],
  'profile-check-bmad-updates': ['profiles/workflows/check-bmad-updates.yml'],
};

const ROOT_FEATURE_GROUPS = {
  baseline: ['.editorconfig', '.gitattributes', '.pre-commit-config.yaml', '.coderabbit.yaml'],
  javascript: ['.eslint.config.mjs', 'biome.json', '.prettierignore', '.prettierrc.json'],
  python: ['.isort.cfg', '.pylintrc', '.ruff.toml'],
  docs: ['.codespellrc', '.markdownlint.yaml', '.yamllint.yaml', '.lint'],
  security: ['.gitleaks.toml', '.checkov.yaml'],
  containers: ['.hadolint.yaml', '.ansible-lint'],
  terraform: ['.tflint.hcl'],
};

function listFeatureNames(featureGroups) {
  return Object.keys(featureGroups).sort().join(', ');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    project: process.cwd(),
    all: false,
    dryRun: false,
    targets: [...DEFAULT_TARGETS],
    projectsConfig: null,
    githubFeatures: null,
    rootFeatures: null,
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
    } else if (arg === '--github-features' && args[i + 1]) {
      options.githubFeatures = args[++i]
        .split(',')
        .map((item) => item.trim().toLowerCase())
        .filter(Boolean);
    } else if (arg === '--root-features' && args[i + 1]) {
      options.rootFeatures = args[++i]
        .split(',')
        .map((item) => item.trim().toLowerCase())
        .filter(Boolean);
    } else if (arg === '--help') {
      console.log(`
Compass Engine Push

Usage:
  compass-engine push [options]

Options:
  --project <path>       Push to specific project (default: current directory)
  --all                  Push to all discovered Compass Brand projects
  --targets <list>       Comma-separated targets (bmad,planning,documentation,claude,codex,opencode,github,root)
  --github-features <l>  Optional GitHub bundle subset (all or: ${listFeatureNames(GITHUB_FEATURE_GROUPS)})
  --root-features <l>    Optional root bundle subset (all or: ${listFeatureNames(ROOT_FEATURE_GROUPS)})
  --projects-config <p>  Optional file with one project path per line
  --dry-run              Show actions without modifying files
  --help                 Show this message

Notes:
  documentation target manages docs control-plane files only and preserves project-owned docs/README.md
  github and root targets install the full shipped bundle unless feature subsets are provided
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

async function copySelectedFiles(sourceRoot, destRoot, files) {
  for (const relativePath of files) {
    const sourcePath = path.join(sourceRoot, relativePath);
    const destinationPath = path.join(destRoot, relativePath);
    await fs.mkdir(path.dirname(destinationPath), { recursive: true });
    await fs.copyFile(sourcePath, destinationPath);
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

async function readManagedManifest(projectPath, manifestName) {
  const manifestPath = await getManagedManifestPath(projectPath, manifestName);
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

function resolveFeatureSelection(featureGroups, requested, label) {
  if (!requested || requested.length === 0 || requested.includes('all')) {
    return null;
  }

  const resolvedPaths = new Set();
  const activeStack = new Set();

  function visit(featureName) {
    const items = featureGroups[featureName];
    if (!items) {
      throw new Error(
        `Unknown ${label} feature: ${featureName}. Available values: all, ${listFeatureNames(featureGroups)}`,
      );
    }
    if (activeStack.has(featureName)) {
      throw new Error(`Circular ${label} feature definition detected at: ${featureName}`);
    }

    activeStack.add(featureName);
    for (const item of items) {
      if (featureGroups[item]) {
        visit(item);
      } else {
        resolvedPaths.add(item);
      }
    }
    activeStack.delete(featureName);
  }

  for (const featureName of requested) {
    visit(featureName);
  }

  return [...resolvedPaths].sort();
}

async function expandSelectedPaths(sourceRoot, selectedPaths) {
  const files = new Set();

  for (const relativePath of selectedPaths) {
    const absolutePath = path.join(sourceRoot, relativePath);
    let stat;
    try {
      stat = await fs.stat(absolutePath);
    } catch (err) {
      if (err.code === 'ENOENT') {
        throw new Error(`Selected bundle path does not exist: ${relativePath}`);
      }
      throw err;
    }

    if (stat.isDirectory()) {
      const nestedFiles = await listFilesRecursive(absolutePath);
      for (const nestedFile of nestedFiles) {
        files.add(path.join(relativePath, nestedFile).replace(/\\/g, '/'));
      }
    } else {
      files.add(relativePath.replace(/\\/g, '/'));
    }
  }

  return [...files].sort();
}

async function writeManagedManifest(projectPath, manifestName, files) {
  const manifestPath = await getManagedManifestPath(projectPath, manifestName);
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

async function getManagedManifestPath(projectPath, manifestName) {
  const gitDir = await resolveGitDir(projectPath);
  if (gitDir) {
    return path.join(gitDir, manifestName);
  }
  return path.join(projectPath, '.compass-engine', manifestName);
}

function resolveWithinProject(projectPath, relativePath) {
  const absolute = path.resolve(projectPath, relativePath);
  const normalizedProject = `${path.resolve(projectPath)}${path.sep}`;
  if (!absolute.startsWith(normalizedProject) && absolute !== path.resolve(projectPath)) {
    throw new Error(`Refusing to operate outside project root: ${relativePath}`);
  }
  return absolute;
}

async function syncManagedTarget(projectPath, sourcePath, target, options, currentFiles = null) {
  const managedFiles = currentFiles || (await listFilesRecursive(sourcePath));
  const previousFiles = await readManagedManifest(projectPath, target.manifestName);
  const preservePaths = new Set(target.preservePaths || []);
  const cleanupPaths = target.cleanupPaths || [];
  const staleFiles = previousFiles.filter(
    (rel) => !managedFiles.includes(rel) && !preservePaths.has(rel),
  );
  const destRoot = target.destName ? path.join(projectPath, target.destName) : projectPath;
  const displayTarget = target.destName || 'project root';

  if (options.dryRun) {
    console.log(`    [DRY RUN] Merge files from dist/${target.distName} into ${displayTarget}`);
    if (currentFiles) {
      console.log(`    [DRY RUN] Install ${managedFiles.length} selected managed files in ${displayTarget}`);
    }
    if (staleFiles.length > 0) {
      console.log(`    [DRY RUN] Remove ${staleFiles.length} stale managed files in ${displayTarget}`);
    }
    if (cleanupPaths.length > 0) {
      console.log(
        `    [DRY RUN] Remove legacy managed paths in ${displayTarget}: ${cleanupPaths.join(', ')}`,
      );
    }
    if (preservePaths.size > 0) {
      console.log(
        `    [DRY RUN] Preserve project-owned paths in ${displayTarget}: ${[...preservePaths].join(', ')}`,
      );
    }
    return;
  }

  for (const relPath of staleFiles) {
    await fs.rm(resolveWithinProject(destRoot, relPath), { recursive: true, force: true });
  }
  for (const relPath of cleanupPaths) {
    await fs.rm(resolveWithinProject(destRoot, relPath), { recursive: true, force: true });
  }
  if (currentFiles) {
    await copySelectedFiles(sourcePath, destRoot, managedFiles);
  } else {
    await copyDir(sourcePath, destRoot);
  }
  await writeManagedManifest(projectPath, target.manifestName, managedFiles);
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

  let selectedFiles = null;
  if (targetName === 'github') {
    const requestedPaths = resolveFeatureSelection(
      GITHUB_FEATURE_GROUPS,
      options.githubFeatures,
      'github',
    );
    if (requestedPaths) {
      selectedFiles = await expandSelectedPaths(sourcePath, requestedPaths);
      console.log(`    Selected GitHub features: ${options.githubFeatures.join(', ')}`);
    }
  } else if (targetName === 'root') {
    const requestedPaths = resolveFeatureSelection(ROOT_FEATURE_GROUPS, options.rootFeatures, 'root');
    if (requestedPaths) {
      selectedFiles = await expandSelectedPaths(sourcePath, requestedPaths);
      console.log(`    Selected root features: ${options.rootFeatures.join(', ')}`);
    }
  }

  if (targetName === 'root') {
    await syncManagedTarget(projectPath, sourcePath, target, options, selectedFiles);
    return;
  }

  if (target.syncStrategy === 'managed') {
    await syncManagedTarget(projectPath, sourcePath, target, options, selectedFiles);
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

async function discoverWorkspaceGitRepos(workspaceRoot) {
  const projects = [];
  const entries = await fs.readdir(workspaceRoot, { withFileTypes: true });

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (entry.name === 'node_modules' || entry.name === 'dist') continue;

    const candidate = path.join(workspaceRoot, entry.name);
    if (await exists(path.join(candidate, '.git'))) {
      projects.push(candidate);
    }
  }

  return projects;
}

async function discoverProjects(workspaceRoot, configPath) {
  const projects = [];
  const seen = new Set();

  function addProject(projectPath) {
    const normalized = path.resolve(projectPath);
    if (seen.has(normalized)) return;
    seen.add(normalized);
    projects.push(normalized);
  }

  if (configPath) {
    const fromConfig = await loadProjectConfig(configPath, workspaceRoot);
    if (fromConfig) {
      for (const projectPath of fromConfig) {
        if (await exists(path.join(projectPath, '.git'))) addProject(projectPath);
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
      if (await exists(path.join(projectPath, '.git'))) addProject(projectPath);
    }
    if (projects.length > 0) return projects;
  }

  const candidates = DEFAULT_PROJECT_CANDIDATES.map((candidate) =>
    candidate === '.' ? workspaceRoot : path.join(workspaceRoot, candidate),
  );

  for (const candidate of candidates) {
    if (await exists(path.join(candidate, '.git'))) addProject(candidate);
  }

  const workspaceGitRepos = await discoverWorkspaceGitRepos(workspaceRoot);
  for (const projectPath of workspaceGitRepos) {
    addProject(projectPath);
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

const isDirectRun = process.argv[1] && path.resolve(process.argv[1]) === __filename;

if (isDirectRun) {
  push().catch((err) => {
    console.error('Push failed:', err.message);
    process.exit(1);
  });
}

export { push };
