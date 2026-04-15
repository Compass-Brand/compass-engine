#!/usr/bin/env node
/**
 * Compass Engine Marketplace Generator
 *
 * Produces `.claude-plugin/marketplace.json` describing the 4 Compass plugins
 * (bmm, core, compass, bmad-builder) in the schema consumed by BMAD-METHOD's
 * PluginResolver (v6.3.0). Writes to repo root AND `dist/.claude-plugin/` so
 * `tools/push.js` can ship the same file to downstream consumers.
 *
 * Deliberate divergence from upstream: 4 plugins (vs upstream's 2-plugin
 * grouping) mapped 1:1 to our `dist/_bmad/{module}/` layout. Strategy 1
 * resolution: module.yaml + module-help.csv live at each plugin's source dir.
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const SRC_MODULES = path.join(ROOT, 'src', 'bmad', 'modules');

const PLUGINS = [
  {
    name: 'bmm',
    source: 'src/bmad/modules/native/bmm-skills',
    description: 'BMad Method Agile-AI Driven-Development skills (analysis, planning, solutioning, implementation).',
  },
  {
    name: 'core',
    source: 'src/bmad/modules/native/core-skills',
    description: 'BMAD Core skills (brainstorming, reviews, distillation, indexing).',
  },
  {
    name: 'compass',
    source: 'src/bmad/modules/custom/compass-skills',
    description: 'Compass Brand custom agents, workflows, and utilities.',
  },
  {
    name: 'bmad-builder',
    source: 'src/bmad/modules/custom/bmad-builder-skills',
    description: 'Tools for building and modifying BMAD modules, agents, and workflows.',
  },
];

async function pathExists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

async function findSkillDirs(rootDir) {
  const results = [];
  async function walk(dir) {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    const hasSkillMd = entries.some((e) => e.isFile() && e.name === 'SKILL.md');
    if (hasSkillMd) {
      results.push(dir);
      return;
    }
    for (const entry of entries) {
      if (entry.isDirectory()) {
        await walk(path.join(dir, entry.name));
      }
    }
  }
  await walk(rootDir);
  return results;
}

function parseVersionFromModuleYaml(content) {
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (trimmed.startsWith('version:') || trimmed.startsWith('module_version:')) {
      const value = trimmed.slice(trimmed.indexOf(':') + 1).trim();
      return value.replace(/^["']|["']$/g, '');
    }
  }
  return null;
}

async function readRootMarketplaceVersion() {
  const pkgPath = path.join(ROOT, 'package.json');
  try {
    const pkg = JSON.parse(await fs.readFile(pkgPath, 'utf-8'));
    return pkg.version || '0.0.0';
  } catch {
    return '0.0.0';
  }
}

async function buildPluginEntry(plugin) {
  const sourceAbs = path.join(ROOT, plugin.source);
  if (!(await pathExists(sourceAbs))) {
    throw new Error(`Plugin source does not exist: ${plugin.source}`);
  }
  const moduleYamlPath = path.join(sourceAbs, 'module.yaml');
  const moduleHelpPath = path.join(sourceAbs, 'module-help.csv');
  if (!(await pathExists(moduleYamlPath))) {
    throw new Error(`Missing module.yaml at ${plugin.source}`);
  }
  if (!(await pathExists(moduleHelpPath))) {
    throw new Error(`Missing module-help.csv at ${plugin.source}`);
  }

  const moduleYamlContent = await fs.readFile(moduleYamlPath, 'utf-8');
  const version = parseVersionFromModuleYaml(moduleYamlContent) || (await readRootMarketplaceVersion());

  const skillDirs = await findSkillDirs(sourceAbs);
  const skills = skillDirs
    .map((abs) => path.relative(ROOT, abs).replace(/\\/g, '/'))
    .sort();

  return {
    name: plugin.name,
    source: plugin.source,
    description: plugin.description,
    version,
    author: 'Compass Brand',
    skills,
  };
}

async function generateMarketplace() {
  const plugins = [];
  for (const pluginSpec of PLUGINS) {
    plugins.push(await buildPluginEntry(pluginSpec));
  }

  const version = await readRootMarketplaceVersion();

  return {
    name: 'compass-engine',
    owner: 'Compass Brand',
    description:
      'Compass Brand BMAD distribution: 4 plugins (bmm, core, compass, bmad-builder) installable via BMAD v6.3+ marketplace tooling.',
    license: 'UNLICENSED',
    homepage: 'https://github.com/Compass-Brand/compass-engine',
    repository: 'https://github.com/Compass-Brand/compass-engine',
    version,
    keywords: ['bmad', 'compass', 'marketplace', 'plugins'],
    plugins,
  };
}

async function writeMarketplaceJson() {
  const marketplace = await generateMarketplace();
  const json = JSON.stringify(marketplace, null, 2) + '\n';

  const rootDir = path.join(ROOT, '.claude-plugin');
  const distDir = path.join(ROOT, 'dist', '.claude-plugin');
  await fs.mkdir(rootDir, { recursive: true });
  await fs.mkdir(distDir, { recursive: true });

  const rootPath = path.join(rootDir, 'marketplace.json');
  const distPath = path.join(distDir, 'marketplace.json');
  await fs.writeFile(rootPath, json);
  await fs.writeFile(distPath, json);

  return { rootPath, distPath, plugins: marketplace.plugins };
}

const isDirectRun = process.argv[1] && path.resolve(process.argv[1]) === __filename;

if (isDirectRun) {
  writeMarketplaceJson()
    .then(({ rootPath, plugins }) => {
      console.log(`Wrote ${path.relative(ROOT, rootPath)} (${plugins.length} plugins)`);
      for (const p of plugins) {
        console.log(`  ${p.name}: ${p.skills.length} skills @ ${p.source}`);
      }
    })
    .catch((err) => {
      console.error('generate-marketplace failed:', err.message);
      process.exit(1);
    });
}

export {
  PLUGINS,
  SRC_MODULES,
  findSkillDirs,
  generateMarketplace,
  writeMarketplaceJson,
};
