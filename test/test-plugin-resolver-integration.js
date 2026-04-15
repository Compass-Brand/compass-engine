import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MARKETPLACE_PATH = path.join(ROOT, '.claude-plugin', 'marketplace.json');
const UPSTREAM_RESOLVER = path.join(
  ROOT,
  'BMAD-METHOD',
  'tools',
  'installer',
  'modules',
  'plugin-resolver.js',
);

async function pathExists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

describe('Upstream PluginResolver resolves marketplace.json via Strategy 1', () => {
  it('PluginResolver resolves all 4 plugins via Strategy 1', async (t) => {
    if (!(await pathExists(UPSTREAM_RESOLVER))) {
      t.skip(`BMAD-METHOD submodule not present at ${path.relative(ROOT, UPSTREAM_RESOLVER)}`);
      return;
    }

    const { PluginResolver } = require(UPSTREAM_RESOLVER);
    const marketplace = JSON.parse(await fs.readFile(MARKETPLACE_PATH, 'utf-8'));
    const resolver = new PluginResolver();

    for (const plugin of marketplace.plugins) {
      const resolved = await resolver.resolve(ROOT, plugin);
      assert.ok(
        Array.isArray(resolved) && resolved.length >= 1,
        `plugin ${plugin.name} did not resolve`,
      );
      assert.equal(
        resolved[0].strategy,
        1,
        `plugin ${plugin.name} resolved via strategy ${resolved[0].strategy}, expected 1`,
      );
      assert.equal(
        resolved[0].pluginName,
        plugin.name,
        `resolved pluginName mismatch for ${plugin.name}`,
      );
    }
  });
});
