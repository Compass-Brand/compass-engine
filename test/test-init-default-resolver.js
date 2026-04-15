import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import path from 'path';
import { fileURLToPath } from 'url';
import { loadCoreSchema, loadModuleSchema } from '../tools/init/schema-loader.js';
import { resolveDefaults } from '../tools/init/default-resolver.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');

describe('resolveDefaults', () => {
  it('should resolve core vars with {value} and {project-root}/{value} templates', async () => {
    const core = loadCoreSchema(REPO_ROOT);
    const projectRoot = '/tmp/fake-project';
    const resolved = await resolveDefaults({
      coreSchema: core,
      moduleSchemas: {},
      projectRoot,
    });

    assert.equal(resolved.core.user_name, 'BMad');
    assert.equal(resolved.core.communication_language, 'English');
    assert.equal(resolved.core.document_output_language, 'English');
    assert.equal(resolved.core.output_folder, '/tmp/fake-project/_bmad-output');
  });

  it('should resolve bmm vars with {directory_name}, {output_folder}, {project-root}', async () => {
    const core = loadCoreSchema(REPO_ROOT);
    const bmm = loadModuleSchema(REPO_ROOT, 'bmm');
    const projectRoot = '/tmp/my-cool-proj';
    const resolved = await resolveDefaults({
      coreSchema: core,
      moduleSchemas: { bmm },
      projectRoot,
    });

    assert.equal(resolved.bmm.project_name, 'my-cool-proj');
    assert.equal(resolved.bmm.user_skill_level, 'intermediate');
    assert.equal(
      resolved.bmm.planning_artifacts,
      '/tmp/my-cool-proj/_bmad-output/planning-artifacts',
    );
    assert.equal(
      resolved.bmm.implementation_artifacts,
      '/tmp/my-cool-proj/_bmad-output/implementation-artifacts',
    );
    assert.equal(resolved.bmm.project_knowledge, '/tmp/my-cool-proj/docs');
  });

  it('should merge resolved core vars into each module config', async () => {
    const core = loadCoreSchema(REPO_ROOT);
    const bmm = loadModuleSchema(REPO_ROOT, 'bmm');
    const projectRoot = '/tmp/proj';
    const resolved = await resolveDefaults({
      coreSchema: core,
      moduleSchemas: { bmm },
      projectRoot,
    });
    assert.equal(resolved.bmm.user_name, 'BMad');
    assert.equal(resolved.bmm.output_folder, '/tmp/proj/_bmad-output');
  });

  it('should resolve directories against fully-expanded variable values', async () => {
    const core = loadCoreSchema(REPO_ROOT);
    const bmm = loadModuleSchema(REPO_ROOT, 'bmm');
    const projectRoot = '/tmp/proj';
    const { directories } = await resolveDefaults({
      coreSchema: core,
      moduleSchemas: { bmm },
      projectRoot,
    });
    assert.deepEqual(directories, [
      '/tmp/proj/_bmad-output/planning-artifacts',
      '/tmp/proj/_bmad-output/implementation-artifacts',
      '/tmp/proj/docs',
    ]);
  });

  it('should use the injected prompter when supplied', async () => {
    const core = loadCoreSchema(REPO_ROOT);
    const prompter = async (varName, varDef) => {
      if (varName === 'user_name') return 'Trevor';
      return varDef.default;
    };
    const resolved = await resolveDefaults({
      coreSchema: core,
      moduleSchemas: {},
      projectRoot: '/tmp/proj',
      prompter,
    });
    assert.equal(resolved.core.user_name, 'Trevor');
  });
});
