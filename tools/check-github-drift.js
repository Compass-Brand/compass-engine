#!/usr/bin/env node
/**
 * Detect drift between source GitHub config and live .github directory.
 *
 * Source of truth: src/github
 * Synced target:   .github
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

const SOURCE_ROOT = path.join(ROOT, 'src', 'github');
const TARGET_ROOT = path.join(ROOT, '.github');

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
      await collectFiles(fullPath, baseDir, bucket);
    } else {
      const rel = path.relative(baseDir, fullPath).replace(/\\/g, '/');
      bucket.push(rel);
    }
  }
  return bucket;
}

async function compareFiles(relPath) {
  const srcPath = path.join(SOURCE_ROOT, relPath);
  const dstPath = path.join(TARGET_ROOT, relPath);

  const [srcContent, dstContent] = await Promise.all([
    fs.readFile(srcPath),
    fs.readFile(dstPath),
  ]);

  return srcContent.equals(dstContent);
}

async function run() {
  if (!(await exists(SOURCE_ROOT))) {
    console.log('Skipping drift check: src/github not found.');
    return;
  }

  if (!(await exists(TARGET_ROOT))) {
    throw new Error('Drift detected: .github directory is missing.');
  }

  const [sourceFilesRaw, targetFilesRaw] = await Promise.all([
    collectFiles(SOURCE_ROOT),
    collectFiles(TARGET_ROOT),
  ]);

  const sourceFiles = sourceFilesRaw.sort();
  const targetFiles = targetFilesRaw.sort();

  const sourceSet = new Set(sourceFiles);
  const targetSet = new Set(targetFiles);

  const missingInTarget = sourceFiles.filter((f) => !targetSet.has(f));
  const extraInTarget = targetFiles.filter((f) => !sourceSet.has(f));

  const shared = sourceFiles.filter((f) => targetSet.has(f));
  const differentContent = [];

  for (const relPath of shared) {
    // eslint-disable-next-line no-await-in-loop
    const same = await compareFiles(relPath);
    if (!same) differentContent.push(relPath);
  }

  if (
    missingInTarget.length === 0
    && extraInTarget.length === 0
    && differentContent.length === 0
  ) {
    console.log('No .github drift detected.');
    return;
  }

  console.error('GitHub drift detected between src/github and .github.');

  if (missingInTarget.length > 0) {
    console.error('\nMissing in .github:');
    for (const p of missingInTarget) console.error(`  - ${p}`);
  }

  if (extraInTarget.length > 0) {
    console.error('\nExtra in .github:');
    for (const p of extraInTarget) console.error(`  - ${p}`);
  }

  if (differentContent.length > 0) {
    console.error('\nDifferent content:');
    for (const p of differentContent) console.error(`  - ${p}`);
  }

  console.error('\nRun: npm run push -- --targets github');
  process.exit(1);
}

run().catch((err) => {
  console.error('Drift check failed:', err.message);
  process.exit(1);
});
