import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import path from 'path';
import { fileURLToPath } from 'url';
import { loadCoreSchema, loadModuleSchema } from '../tools/init/schema-loader.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');

describe('loadCoreSchema', () => {
  it('should parse core module.yaml and return header/subheader/vars', () => {
    const schema = loadCoreSchema(REPO_ROOT);
    assert.equal(schema.header, 'BMad Core Configuration');
    assert.match(schema.subheader, /Configure the core settings/);
    assert.ok(schema.vars, 'vars should be present');
    assert.ok(schema.vars.user_name, 'user_name var should be present');
    assert.equal(schema.vars.user_name.default, 'BMad');
    assert.equal(schema.vars.user_name.result, '{value}');
    assert.equal(schema.vars.output_folder.default, '_bmad-output');
    assert.equal(schema.vars.output_folder.result, '{project-root}/{value}');
    assert.equal(schema.vars.communication_language.default, 'English');
    assert.equal(schema.vars.document_output_language.default, 'English');
  });

  it('should not include meta keys like code/name/header/subheader inside vars', () => {
    const schema = loadCoreSchema(REPO_ROOT);
    for (const metaKey of ['code', 'name', 'header', 'subheader', 'description']) {
      assert.equal(
        schema.vars[metaKey],
        undefined,
        `vars should not contain meta key ${metaKey}`,
      );
    }
  });
});

describe('loadModuleSchema', () => {
  it('should parse bmm module.yaml and return vars + directories list', () => {
    const schema = loadModuleSchema(REPO_ROOT, 'bmm');
    assert.ok(schema.vars.project_name);
    assert.equal(schema.vars.project_name.default, '{directory_name}');
    assert.equal(schema.vars.user_skill_level.default, 'intermediate');
    assert.ok(
      Array.isArray(schema.vars.user_skill_level['single-select']),
      'user_skill_level should preserve single-select options',
    );
    assert.equal(schema.vars.planning_artifacts.default, '{output_folder}/planning-artifacts');
    assert.equal(schema.vars.planning_artifacts.result, '{project-root}/{value}');
    assert.deepEqual(schema.directories, [
      '{planning_artifacts}',
      '{implementation_artifacts}',
      '{project_knowledge}',
    ]);
  });

  it('should return empty vars for modules with no user-facing variables', () => {
    const schema = loadModuleSchema(REPO_ROOT, 'compass');
    assert.deepEqual(schema.vars, {});
    assert.deepEqual(schema.directories, []);
  });

  it('should return empty vars for bmad-builder (no user-facing variables)', () => {
    const schema = loadModuleSchema(REPO_ROOT, 'bmad-builder');
    assert.deepEqual(schema.vars, {});
    assert.deepEqual(schema.directories, []);
  });
});
