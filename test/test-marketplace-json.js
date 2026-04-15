import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MARKETPLACE_PATH = path.join(ROOT, '.claude-plugin', 'marketplace.json');

describe('.claude-plugin/marketplace.json', () => {
  it('exists and parses as JSON', async () => {
    const content = await fs.readFile(MARKETPLACE_PATH, 'utf-8');
    const parsed = JSON.parse(content);
    assert.ok(parsed, 'marketplace.json should parse');
  });

  it('has required top-level fields', async () => {
    const parsed = JSON.parse(await fs.readFile(MARKETPLACE_PATH, 'utf-8'));
    assert.ok(typeof parsed.name === 'string' && parsed.name.length > 0, 'name must be non-empty');
    assert.ok(Array.isArray(parsed.plugins), 'plugins must be an array');
    assert.ok(parsed.plugins.length > 0, 'plugins must not be empty');
  });

  it('ships the 4 Compass plugins (bmm, core, compass, bmad-builder)', async () => {
    const parsed = JSON.parse(await fs.readFile(MARKETPLACE_PATH, 'utf-8'));
    const names = parsed.plugins.map((p) => p.name).sort();
    assert.deepEqual(names, ['bmad-builder', 'bmm', 'compass', 'core']);
  });

  it('each plugin has name, source, version, and non-empty skills[]', async () => {
    const parsed = JSON.parse(await fs.readFile(MARKETPLACE_PATH, 'utf-8'));
    for (const plugin of parsed.plugins) {
      assert.ok(plugin.name, `plugin missing name`);
      assert.ok(plugin.source, `plugin ${plugin.name} missing source`);
      assert.ok(plugin.version, `plugin ${plugin.name} missing version`);
      assert.ok(
        Array.isArray(plugin.skills) && plugin.skills.length > 0,
        `plugin ${plugin.name} must have non-empty skills[]`,
      );
    }
  });

  it('every skill path resolves to a directory containing SKILL.md', async () => {
    const parsed = JSON.parse(await fs.readFile(MARKETPLACE_PATH, 'utf-8'));
    for (const plugin of parsed.plugins) {
      for (const skillRel of plugin.skills) {
        const skillDir = path.join(ROOT, skillRel);
        const skillMd = path.join(skillDir, 'SKILL.md');
        const stat = await fs.stat(skillMd);
        assert.ok(stat.isFile(), `${skillRel}/SKILL.md must exist`);
      }
    }
  });

  it('each plugin source contains module.yaml + module-help.csv (Strategy 1)', async () => {
    const parsed = JSON.parse(await fs.readFile(MARKETPLACE_PATH, 'utf-8'));
    for (const plugin of parsed.plugins) {
      const srcDir = path.join(ROOT, plugin.source);
      await fs.access(path.join(srcDir, 'module.yaml'));
      await fs.access(path.join(srcDir, 'module-help.csv'));
    }
  });
});
