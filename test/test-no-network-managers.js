import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

const FORBIDDEN_MODULES = ['external-manager', 'community-manager'];

const SCAN_ROOTS = [
  path.join(ROOT, 'tools'),
  path.join(ROOT, 'src'),
];

const SCAN_EXTENSIONS = new Set(['.js', '.cjs', '.mjs', '.ts']);

const EXCLUDED_DIRS = new Set(['node_modules', 'dist', '.git', 'BMAD-METHOD']);

async function walkFiles(root) {
  const files = [];
  async function walk(dir) {
    let entries;
    try {
      entries = await fs.readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (EXCLUDED_DIRS.has(entry.name)) continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        await walk(full);
      } else if (entry.isFile() && SCAN_EXTENSIONS.has(path.extname(entry.name))) {
        files.push(full);
      }
    }
  }
  await walk(root);
  return files;
}

function findForbiddenImports(content) {
  const hits = [];
  const importRegex = /(?:require\(|from\s+|import\s*\()\s*['"]([^'"]+)['"]/g;
  let match;
  while ((match = importRegex.exec(content)) !== null) {
    const spec = match[1];
    for (const forbidden of FORBIDDEN_MODULES) {
      if (spec.includes(forbidden)) {
        hits.push({ spec, forbidden });
      }
    }
  }
  return hits;
}

describe('No network-fetching BMAD managers imported anywhere', () => {
  it('tools/ and src/ (including tools/vendor/) must not import external-manager or community-manager', async () => {
    const offenders = [];
    for (const root of SCAN_ROOTS) {
      const files = await walkFiles(root);
      for (const file of files) {
        const content = await fs.readFile(file, 'utf-8');
        const hits = findForbiddenImports(content);
        for (const hit of hits) {
          offenders.push(`${path.relative(ROOT, file)} imports ${hit.spec} (matches ${hit.forbidden})`);
        }
      }
    }

    assert.equal(
      offenders.length,
      0,
      `Forbidden network-manager imports detected (see ADR-0001 Risk #1):\n  ${offenders.join('\n  ')}`,
    );
  });
});
