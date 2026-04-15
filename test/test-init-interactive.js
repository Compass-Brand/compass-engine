import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import path from 'path';
import { fileURLToPath } from 'url';
import { loadCoreSchema, loadModuleSchema } from '../tools/init/schema-loader.js';
import { resolveDefaults } from '../tools/init/default-resolver.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');

describe('interactive prompter', () => {
  it('should use the injected answer when provided (overrides default)', async () => {
    const core = loadCoreSchema(REPO_ROOT);
    const prompter = async (varName) => {
      if (varName === 'user_name') return 'Trevor';
      return '';
    };
    const resolved = await resolveDefaults({
      coreSchema: core,
      moduleSchemas: {},
      projectRoot: '/tmp/proj',
      prompter,
    });
    assert.equal(resolved.core.user_name, 'Trevor');
    assert.equal(resolved.core.communication_language, 'English', 'empty input falls back to default');
  });

  it('should respect single-select values for user_skill_level', async () => {
    const core = loadCoreSchema(REPO_ROOT);
    const bmm = loadModuleSchema(REPO_ROOT, 'bmm');
    const prompter = async (varName) => {
      if (varName === 'user_skill_level') return 'expert';
      return '';
    };
    const resolved = await resolveDefaults({
      coreSchema: core,
      moduleSchemas: { bmm },
      projectRoot: '/tmp/proj',
      prompter,
    });
    assert.equal(resolved.bmm.user_skill_level, 'expert');
  });

  it('should pass the expanded default in varDef so prompters can display it', async () => {
    const core = loadCoreSchema(REPO_ROOT);
    const bmm = loadModuleSchema(REPO_ROOT, 'bmm');
    const seen = [];
    const prompter = async (varName, varDef) => {
      seen.push({ varName, shownDefault: varDef.default });
      return '';
    };
    await resolveDefaults({
      coreSchema: core,
      moduleSchemas: { bmm },
      projectRoot: '/tmp/proj',
      prompter,
    });
    const projectName = seen.find((e) => e.varName === 'project_name');
    assert.equal(projectName.shownDefault, 'proj', 'project_name default should be the dir basename');
    const planning = seen.find((e) => e.varName === 'planning_artifacts');
    assert.equal(planning.shownDefault, '_bmad-output/planning-artifacts');
  });
});
