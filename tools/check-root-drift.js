#!/usr/bin/env node
/**
 * Detect drift between source root baseline files and repository root files.
 *
 * Source of truth: src/root
 * Synced target:   repository root
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

const SOURCE_ROOT = path.join(ROOT, 'src', 'root');

async function exists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function collectFiles(rootDir, baseDir = rootDir, bucket = []) {
  const entries = await fs.readdir(rootDir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(rootDir, entry.name);
    if (entry.isDirectory()) {
      // eslint-disable-next-line no-await-in-loop
      await collectFiles(fullPath, baseDir, bucket);
    } else {
      const rel = path.relative(baseDir, fullPath).replace(/\\/g, '/');
      bucket.push(rel);
    }
  }
  return bucket;
}

async function run() {
  if (!(await exists(SOURCE_ROOT))) {
    console.log('Skipping root drift check: src/root not found.');
    return;
  }

  const sourceFiles = (await collectFiles(SOURCE_ROOT)).sort();
  const missingInTarget = [];
  const differentContent = [];

  for (const relPath of sourceFiles) {
    const srcPath = path.join(SOURCE_ROOT, relPath);
    const dstPath = path.join(ROOT, relPath);

    // eslint-disable-next-line no-await-in-loop
    if (!(await exists(dstPath))) {
      missingInTarget.push(relPath);
      // eslint-disable-next-line no-continue
      continue;
    }

    // eslint-disable-next-line no-await-in-loop
    const [srcContent, dstContent] = await Promise.all([
      fs.readFile(srcPath),
      fs.readFile(dstPath),
    ]);

    if (!srcContent.equals(dstContent)) {
      differentContent.push(relPath);
    }
  }

  if (missingInTarget.length === 0 && differentContent.length === 0) {
    console.log('No root-file drift detected.');
    return;
  }

  console.error('Root-file drift detected between src/root and repository root.');

  if (missingInTarget.length > 0) {
    console.error('\nMissing in root:');
    for (const p of missingInTarget) console.error(`  - ${p}`);
  }

  if (differentContent.length > 0) {
    console.error('\nDifferent content:');
    for (const p of differentContent) console.error(`  - ${p}`);
  }

  console.error('\nRun: npm run build && npm run push -- --targets root');
  process.exit(1);
}

run().catch((err) => {
  console.error('Root drift check failed:', err.message);
  process.exit(1);
});
