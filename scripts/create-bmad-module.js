#!/usr/bin/env node
/**
 * Scaffold a custom BMAD module from an upstream BMAD-METHOD module.
 *
 * Example:
 *   node scripts/create-bmad-module.js --name compass-bmm --from bmm --code cbmm
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    from: 'bmm',
    name: '',
    code: '',
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--from' && args[i + 1]) options.from = args[++i];
    else if (arg === '--name' && args[i + 1]) options.name = args[++i];
    else if (arg === '--code' && args[i + 1]) options.code = args[++i];
    else if (arg === '--help') {
      console.log(`
Create BMAD Module

Usage:
  node scripts/create-bmad-module.js --name <module-name> [--from bmm] [--code custom-code]
`);
      process.exit(0);
    }
  }

  if (!options.name) {
    throw new Error('Missing required argument: --name <module-name>');
  }

  if (!options.code) {
    options.code = options.name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  }

  return options;
}

async function copyDir(src, dest) {
  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) await copyDir(srcPath, destPath);
    else await fs.copyFile(srcPath, destPath);
  }
}

async function exists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function scaffold() {
  const options = parseArgs();

  const upstreamModule = path.join(ROOT, 'BMAD-METHOD', 'src', options.from);
  const targetRoot = path.join(ROOT, 'src', 'bmad', 'modules');
  const targetModule = path.join(targetRoot, options.name);

  if (!(await exists(upstreamModule))) {
    throw new Error(`Upstream module not found: ${upstreamModule}`);
  }

  if (await exists(targetModule)) {
    throw new Error(`Target module already exists: ${targetModule}`);
  }

  await copyDir(upstreamModule, targetModule);

  const moduleYamlPath = path.join(targetModule, 'module.yaml');
  if (await exists(moduleYamlPath)) {
    const moduleYaml = await fs.readFile(moduleYamlPath, 'utf-8');
    const updated = moduleYaml
      .replace(/^code:\s*.*$/m, `code: ${options.code}`)
      .replace(/^name:\s*.*$/m, `name: "${options.name}"`)
      .concat(`\n# Customized from BMAD-METHOD/src/${options.from}\n`);

    await fs.writeFile(moduleYamlPath, updated);
  }

  const metadata = {
    sourceModule: options.from,
    customModule: options.name,
    code: options.code,
    createdAt: new Date().toISOString(),
    notes: 'Modify this module under src/bmad/modules and avoid direct edits to BMAD-METHOD.',
  };

  await fs.writeFile(
    path.join(targetModule, 'custom-module.json'),
    JSON.stringify(metadata, null, 2),
  );

  console.log(`Created custom module at ${path.relative(ROOT, targetModule)}`);
}

scaffold().catch((err) => {
  console.error('Module scaffold failed:', err.message);
  process.exit(1);
});