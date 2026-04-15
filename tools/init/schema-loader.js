import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

const META_KEYS = new Set([
  'code',
  'name',
  'description',
  'default_selected',
  'header',
  'subheader',
  'displayName',
  'version',
  'type',
]);

const CORE_SCHEMA_REL = 'src/bmad/modules/native/core-skills/bmad-init/resources/core-module.yaml';

const MODULE_SCHEMA_CANDIDATES = [
  (code) => `src/bmad/modules/native/${code}-skills/module.yaml`,
  (code) => `src/bmad/modules/custom/${code}-skills/module.yaml`,
];

function parseYamlFile(absPath) {
  const raw = fs.readFileSync(absPath, 'utf-8');
  const doc = yaml.load(raw);
  if (!doc || typeof doc !== 'object') {
    return {};
  }
  return doc;
}

function splitSchema(doc) {
  const vars = {};
  const directories = Array.isArray(doc.directories) ? [...doc.directories] : [];
  const header = typeof doc.header === 'string' ? doc.header : undefined;
  const subheader = typeof doc.subheader === 'string' ? doc.subheader : undefined;

  for (const [key, value] of Object.entries(doc)) {
    if (META_KEYS.has(key) || key === 'directories') continue;
    if (value && typeof value === 'object' && !Array.isArray(value) && 'prompt' in value) {
      vars[key] = value;
    }
  }

  return { header, subheader, vars, directories };
}

export function loadCoreSchema(repoRoot) {
  const abs = path.join(repoRoot, CORE_SCHEMA_REL);
  const doc = parseYamlFile(abs);
  return splitSchema(doc);
}

export function loadModuleSchema(repoRoot, moduleCode) {
  for (const build of MODULE_SCHEMA_CANDIDATES) {
    const abs = path.join(repoRoot, build(moduleCode));
    if (fs.existsSync(abs)) {
      const doc = parseYamlFile(abs);
      return splitSchema(doc);
    }
  }
  return { header: undefined, subheader: undefined, vars: {}, directories: [] };
}
