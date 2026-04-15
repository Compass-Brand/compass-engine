#!/usr/bin/env node

import path from 'path';
import { fileURLToPath } from 'url';
import { loadCoreSchema, loadModuleSchema } from './init/schema-loader.js';
import { resolveDefaults } from './init/default-resolver.js';
import { writeConfig, ensureDirectories } from './init/config-writer.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');

const DEFAULT_MODULES = ['core', 'bmm'];

function printHelp() {
  console.log(`
Compass Engine init

Usage:
  compass-engine init [options]

Options:
  --project-root <path>    Target project root (defaults to cwd)
  --modules <csv>          Modules to bootstrap (default: core,bmm)
  --interactive            Prompt for each value instead of using defaults
  --force                  Overwrite existing _bmad/{module}/config.yaml files
  --dry-run                Print intended writes without touching the filesystem
  --help, -h               Show this help

Writes _bmad/{core,bmm}/config.yaml populated from module.yaml defaults so
skills and agents can read stable project configuration on first run.
`);
}

function parseArgs(argv) {
  const out = {
    projectRoot: process.cwd(),
    modules: DEFAULT_MODULES,
    interactive: false,
    force: false,
    dryRun: false,
    help: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case '--help':
      case '-h':
        out.help = true;
        break;
      case '--interactive':
        out.interactive = true;
        break;
      case '--force':
        out.force = true;
        break;
      case '--dry-run':
        out.dryRun = true;
        break;
      case '--project-root':
        out.projectRoot = path.resolve(argv[++i]);
        break;
      case '--modules':
        out.modules = argv[++i]
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean);
        break;
      default:
        throw new Error(`Unknown option: ${arg}`);
    }
  }
  return out;
}

async function createInteractivePrompter() {
  const readline = await import('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  const ask = (question) =>
    new Promise((resolve) => rl.question(question, (answer) => resolve(answer)));

  const prompter = async (_varName, varDef) => {
    const prompt = Array.isArray(varDef.prompt) ? varDef.prompt.join('\n  ') : varDef.prompt;
    const select = varDef['single-select'];
    if (Array.isArray(select) && select.length > 0) {
      console.log(`\n${prompt}`);
      select.forEach((opt, idx) => {
        console.log(`  ${idx + 1}) ${opt.label || opt.value}`);
      });
      const defaultIdx = select.findIndex((o) => o.value === varDef.default);
      const promptStr = `Choice [${defaultIdx >= 0 ? defaultIdx + 1 : 1}]: `;
      const answer = (await ask(promptStr)).trim();
      if (!answer) return varDef.default;
      const n = Number(answer);
      if (!Number.isInteger(n) || n < 1 || n > select.length) return varDef.default;
      return select[n - 1].value;
    }
    const answer = (await ask(`\n${prompt}\n[${varDef.default}]: `)).trim();
    return answer === '' ? varDef.default : answer;
  };

  prompter.close = () => rl.close();
  return prompter;
}

export async function runInit(options) {
  const { projectRoot, modules, interactive, force, dryRun, logger = console } = options;

  const coreSchema = loadCoreSchema(REPO_ROOT);
  const moduleSchemas = {};
  for (const m of modules) {
    if (m === 'core') continue;
    const schema = loadModuleSchema(REPO_ROOT, m);
    if (Object.keys(schema.vars).length === 0) {
      logger.log(`Skipping module '${m}' (no user-facing variables)`);
      continue;
    }
    moduleSchemas[m] = schema;
  }

  let prompter = null;
  let closePrompter = () => {};
  if (interactive) {
    prompter = await createInteractivePrompter();
    closePrompter = () => prompter.close();
  }

  let resolved;
  try {
    resolved = await resolveDefaults({
      coreSchema,
      moduleSchemas,
      projectRoot,
      prompter,
    });
  } finally {
    closePrompter();
  }

  const writes = [];
  if (modules.includes('core')) {
    writes.push({ moduleCode: 'core', values: resolved.core });
  }
  for (const moduleCode of Object.keys(moduleSchemas)) {
    writes.push({ moduleCode, values: resolved[moduleCode] });
  }

  if (dryRun) {
    logger.log('--dry-run: no files written');
    for (const w of writes) {
      logger.log(`  would write ${path.join(projectRoot, '_bmad', w.moduleCode, 'config.yaml')}`);
    }
    for (const dir of resolved.directories) {
      logger.log(`  would ensure directory ${dir}`);
    }
    return { writes, directories: resolved.directories };
  }

  const written = [];
  for (const w of writes) {
    const file = await writeConfig(projectRoot, w.moduleCode, w.values, { force });
    written.push(file);
    logger.log(`wrote ${file}`);
  }

  const dirs = await ensureDirectories(resolved.directories);
  for (const d of dirs) logger.log(`ensured ${d}`);

  return { written, directories: dirs };
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv.includes('--help') || argv.includes('-h')) {
    printHelp();
    return;
  }
  let opts;
  try {
    opts = parseArgs(argv);
  } catch (err) {
    console.error(err.message);
    printHelp();
    process.exitCode = 2;
    return;
  }
  try {
    await runInit(opts);
  } catch (err) {
    console.error(err.message);
    process.exitCode = 1;
  }
}

const invokedDirectly = (() => {
  try {
    return process.argv[1] && path.resolve(process.argv[1]) === __filename;
  } catch {
    return false;
  }
})();

if (invokedDirectly) {
  main();
}
