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

const NATIVE_ROOT = path.join(SRC, 'bmad', 'modules', 'native');
const CUSTOM_ROOT = path.join(SRC, 'bmad', 'modules', 'custom');
const BMAD_DIST = path.join(DIST_ROOT, '_bmad');

const SKILL_MODULES = [
  {
    name: 'bmm',
    native: path.join(NATIVE_ROOT, 'bmm-skills'),
    custom: path.join(CUSTOM_ROOT, 'bmm-skills'),
    dist: path.join(BMAD_DIST, 'bmm'),
  },
  {
    name: 'core',
    native: path.join(NATIVE_ROOT, 'core-skills'),
    custom: path.join(CUSTOM_ROOT, 'core-skills'),
    dist: path.join(BMAD_DIST, 'core'),
  },
];

const CUSTOM_ONLY_MODULES = [
  {
    name: 'compass',
    src: path.join(CUSTOM_ROOT, 'compass-skills'),
    dist: path.join(BMAD_DIST, 'compass'),
  },
  {
    name: 'bmad-builder',
    src: path.join(CUSTOM_ROOT, 'bmad-builder-skills'),
    dist: path.join(BMAD_DIST, 'bmad-builder'),
  },
];

const TARGETS = [
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

function parseSimpleYaml(content) {
  const result = {};
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const colonIdx = trimmed.indexOf(':');
    if (colonIdx < 1) continue;
    const key = trimmed.slice(0, colonIdx).trim();
    let value = trimmed.slice(colonIdx + 1).trim();
    // Strip surrounding quotes
    if (value.startsWith('"') && value.endsWith('"')) {
      value = value.slice(1, -1);
    }
    // Decode YAML unicode escapes (\U0001FXXX → actual emoji)
    value = value.replace(/\\U([0-9A-Fa-f]{8})/g, (_, hex) =>
      String.fromCodePoint(parseInt(hex, 16)),
    );
    result[key] = value;
  }
  return result;
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

function parseCsvRows(content) {
  const lines = content.split(/\r?\n/).filter(Boolean);
  if (lines.length < 2) return [];
  const header = lines[0].split(',');
  return lines.slice(1).map((line) => {
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
    return Object.fromEntries(header.map((col, idx) => [col, cells[idx] ?? '']));
  });
}

function clientSkillName(internalName, module) {
  // Compass skills already have module prefix
  if (internalName.startsWith('bmad-compass-') || internalName.startsWith('bmad-agent-compass-')) {
    return internalName;
  }
  // bmad-builder skills — use 'builder' as short module name
  const modPrefix = module === 'bmad-builder' ? 'builder' : module;
  // Agents: bmad-agent-{name} → bmad-agent-{module}-{name}
  if (internalName.startsWith('bmad-agent-')) {
    const agentName = internalName.slice('bmad-agent-'.length);
    return `bmad-agent-${modPrefix}-${agentName}`;
  }
  // Special cases that already have module context
  if (internalName === 'bmad-master') return 'bmad-core-master';
  // Workflows: bmad-{name} → bmad-{module}-{name}
  const workflowName = internalName.slice('bmad-'.length);
  return `bmad-${modPrefix}-${workflowName}`;
}

async function generateClientSkills() {
  const manifestPath = path.join(BMAD_DIST, '_config', 'skill-manifest.csv');
  if (!(await exists(manifestPath))) {
    console.log('  Skipping client skill generation: skill-manifest.csv not found');
    return;
  }

  const content = await fs.readFile(manifestPath, 'utf-8');
  const skills = parseCsvRows(content);

  // Client platforms to generate for
  const platforms = [
    { name: 'claude', dist: path.join(DIST_ROOT, '.claude', 'skills') },
    { name: 'opencode', dist: path.join(DIST_ROOT, '.opencode', 'skills') },
    { name: 'codex', dist: path.join(DIST_ROOT, '.codex', 'skills') },
  ];

  for (const platform of platforms) {
    let count = 0;
    for (const skill of skills) {
      const clientName = clientSkillName(skill.name, skill.module);
      const skillDir = path.join(platform.dist, clientName);
      await fs.mkdir(skillDir, { recursive: true });

      const skillMd = [
        '---',
        `name: ${clientName}`,
        `description: '${(skill.description || '').replace(/'/g, "''")}'`,
        '---',
        '',
        `Load and follow the skill at \`{project-root}/${skill.path}/SKILL.md\`.`,
        '',
      ].join('\n');

      await fs.writeFile(path.join(skillDir, 'SKILL.md'), skillMd);
      count++;
    }
    console.log(`  Generated ${count} client skills for ${platform.name}`);
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

async function mergeModules(nativePath, customPath, outputPath) {
  await fs.mkdir(outputPath, { recursive: true });
  if (await exists(nativePath)) {
    await copyDir(nativePath, outputPath);
  }
  if (customPath && (await exists(customPath))) {
    await copyDir(customPath, outputPath);
  }
}

async function generateAgentManifest() {
  const configDir = path.join(BMAD_DIST, '_config');
  await fs.mkdir(configDir, { recursive: true });

  const allFiles = await listFilesRecursive(BMAD_DIST);
  const manifestFiles = allFiles.filter((f) => f.endsWith('/bmad-skill-manifest.yaml'));

  const agents = [];
  for (const relPath of manifestFiles) {
    const fullPath = path.join(BMAD_DIST, relPath);
    const content = await fs.readFile(fullPath, 'utf-8');
    const data = parseSimpleYaml(content);
    if (data.type !== 'agent') continue;

    const skillDir = path.dirname(relPath);
    agents.push({
      id: `_bmad/${skillDir}/SKILL.md`,
      name: data.name || '',
      displayName: data.displayName || '',
      title: data.title || '',
      icon: data.icon || '',
      role: data.role || '',
      identity: data.identity || '',
      communicationStyle: data.communicationStyle || '',
      principles: data.principles || '',
      module: data.module || '',
      path: `_bmad/${relPath}`,
    });
  }

  agents.sort((a, b) => a.module.localeCompare(b.module) || a.name.localeCompare(b.name));

  const header = '"id","name","displayName","title","icon","role","identity","communicationStyle","principles","module","path"';
  const rows = agents.map((a) => {
    const escape = (v) => `"${(v || '').replace(/"/g, '""')}"`;
    return [a.id, a.name, a.displayName, a.title, a.icon, a.role, a.identity, a.communicationStyle, a.principles, a.module, a.path].map(escape).join(',');
  });

  const csv = [header, ...rows].join('\n') + '\n';
  await fs.writeFile(path.join(configDir, 'agent-manifest.csv'), csv);
  console.log(`  Generated agent-manifest.csv (${agents.length} agents)`);
}

async function generateBmadHelp() {
  const configDir = path.join(BMAD_DIST, '_config');
  await fs.mkdir(configDir, { recursive: true });

  const header = 'module,skill,display-name,menu-code,description,action,args,phase,after,before,required,output-location,outputs';
  const allRows = [];

  // Dynamically discover modules (all top-level dirs in dist/_bmad/ except _config)
  const bmadEntries = await fs.readdir(BMAD_DIST, { withFileTypes: true });
  const moduleNames = bmadEntries
    .filter((e) => e.isDirectory() && !e.name.startsWith('_'))
    .map((e) => e.name);

  for (const modName of moduleNames) {
    const csvPath = path.join(BMAD_DIST, modName, 'module-help.csv');
    if (!(await exists(csvPath))) continue;

    const content = await fs.readFile(csvPath, 'utf-8');
    const lines = content.split(/\r?\n/).filter(Boolean);

    // Skip header row (first line), add data rows
    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim()) {
        allRows.push(lines[i]);
      }
    }
  }

  const csv = [header, ...allRows].join('\n') + '\n';
  await fs.writeFile(path.join(configDir, 'bmad-help.csv'), csv);
  console.log(`  Generated bmad-help.csv (${allRows.length} skills from ${moduleNames.length} modules)`);
}

async function generateSkillManifest() {
  const configDir = path.join(BMAD_DIST, '_config');
  await fs.mkdir(configDir, { recursive: true });

  const allFiles = await listFilesRecursive(BMAD_DIST);
  const skillFiles = allFiles.filter((f) => f.endsWith('/SKILL.md'));

  const skills = [];
  for (const relPath of skillFiles) {
    const fullPath = path.join(BMAD_DIST, relPath);
    const content = await fs.readFile(fullPath, 'utf-8');
    const frontmatter = content.match(/^---\n([\s\S]*?)\n---/);
    if (!frontmatter) continue;

    const nameMatch = frontmatter[1].match(/^name:\s*(.+)$/m);
    const descMatch = frontmatter[1].match(/^description:\s*['"]?(.*?)['"]?\s*$/m);
    if (!nameMatch) continue;

    const name = nameMatch[1].trim().replace(/['"]/g, '');
    const description = descMatch ? descMatch[1].trim() : '';
    const skillDir = path.dirname(relPath);
    const module = relPath.split('/')[0];
    const isAgent = name.startsWith('bmad-agent-') || name === 'bmad-master';

    skills.push({
      name,
      type: isAgent ? 'agent' : 'workflow',
      description,
      module,
      path: `_bmad/${skillDir}`,
    });
  }

  skills.sort((a, b) => a.module.localeCompare(b.module) || a.name.localeCompare(b.name));

  const header = 'name,type,description,module,path';
  const rows = skills.map((s) => {
    const escape = (v) => `"${(v || '').replace(/"/g, '""')}"`;
    return [s.name, s.type, s.description, s.module, s.path].map(escape).join(',');
  });

  const csv = [header, ...rows].join('\n') + '\n';
  await fs.writeFile(path.join(configDir, 'skill-manifest.csv'), csv);
  console.log(`  Generated skill-manifest.csv (${skills.length} skills)`);
}

async function buildBmadSkills() {
  console.log('\nBuilding _bmad (skill-based)...');
  await fs.mkdir(BMAD_DIST, { recursive: true });

  const bmadWorkflow = path.join(SRC, 'bmad', 'BMAD-workflow.md');
  if (await exists(bmadWorkflow)) {
    await fs.copyFile(bmadWorkflow, path.join(BMAD_DIST, 'BMAD-workflow.md'));
    console.log('  Copied BMAD-workflow.md');
  }

  for (const mod of SKILL_MODULES) {
    if (await exists(mod.native)) {
      console.log(`  Merging ${mod.name} (native + custom)...`);
      await mergeModules(mod.native, mod.custom, mod.dist);
    } else {
      console.log(`  Skipping ${mod.name}: native not found`);
    }
  }

  for (const mod of CUSTOM_ONLY_MODULES) {
    if (await exists(mod.src)) {
      console.log(`  Copying ${mod.name} (custom-only)...`);
      await copyDir(mod.src, mod.dist);
    } else {
      console.log(`  Skipping ${mod.name}: not found`);
    }
  }

  // Generate agent-manifest.csv and bmad-help.csv from skill directory tree
  await generateAgentManifest();
  await generateBmadHelp();
  await generateSkillManifest();
  await generateClientSkills();
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
    { label: '_bmad/BMAD-workflow.md', path: path.join(DIST_ROOT, '_bmad', 'BMAD-workflow.md') },
    { label: '_bmad/bmm', path: path.join(DIST_ROOT, '_bmad', 'bmm') },
    { label: '_bmad/bmm/module.yaml', path: path.join(DIST_ROOT, '_bmad', 'bmm', 'module.yaml') },
    { label: '_bmad/bmm/module-help.csv', path: path.join(DIST_ROOT, '_bmad', 'bmm', 'module-help.csv') },
    { label: '_bmad/core', path: path.join(DIST_ROOT, '_bmad', 'core') },
    { label: '_bmad/core/module.yaml', path: path.join(DIST_ROOT, '_bmad', 'core', 'module.yaml') },
    { label: '_bmad/core/module-help.csv', path: path.join(DIST_ROOT, '_bmad', 'core', 'module-help.csv') },
    { label: '_bmad/bmm/1-analysis/bmad-agent-analyst/SKILL.md', path: path.join(DIST_ROOT, '_bmad', 'bmm', '1-analysis', 'bmad-agent-analyst', 'SKILL.md') },
    { label: '_bmad/bmm/4-implementation/bmad-agent-dev/SKILL.md', path: path.join(DIST_ROOT, '_bmad', 'bmm', '4-implementation', 'bmad-agent-dev', 'SKILL.md') },
    { label: '_bmad/core/bmad-brainstorming/SKILL.md', path: path.join(DIST_ROOT, '_bmad', 'core', 'bmad-brainstorming', 'SKILL.md') },
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
    { label: '_bmad/_config/agent-manifest.csv', path: path.join(DIST_ROOT, '_bmad', '_config', 'agent-manifest.csv') },
    { label: '_bmad/_config/bmad-help.csv', path: path.join(DIST_ROOT, '_bmad', '_config', 'bmad-help.csv') },
    { label: '_bmad/_config/skill-manifest.csv', path: path.join(DIST_ROOT, '_bmad', '_config', 'skill-manifest.csv') },
    { label: 'dist .claude/skills generated', path: path.join(DIST_ROOT, '.claude', 'skills', 'bmad-bmm-create-prd') },
    { label: 'dist .opencode/skills generated', path: path.join(DIST_ROOT, '.opencode', 'skills', 'bmad-bmm-create-prd') },
    { label: 'dist .codex/skills generated', path: path.join(DIST_ROOT, '.codex', 'skills', 'bmad-bmm-create-prd') },
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

  // Count-based check for generated client skills
  const claudeSkillsDir = path.join(DIST_ROOT, '.claude', 'skills');
  if (await exists(claudeSkillsDir)) {
    const skillDirs = await fs.readdir(claudeSkillsDir);
    const skillCount = skillDirs.length;
    if (skillCount < 90) {
      console.error(`  ERROR Expected ≥90 client skills in dist/.claude/skills/, found ${skillCount}`);
      isValid = false;
    }
    console.log(`  ✓ dist .claude/skills count: ${skillCount}`);
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
  await buildBmadSkills();
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
