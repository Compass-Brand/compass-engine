import { promises as fs } from 'fs';
import os from 'os';
import path from 'path';

/**
 * Create a temporary directory for test isolation.
 * Returns { dir, cleanup } where cleanup removes the directory.
 */
export async function createTempDir(prefix = 'ce-test-') {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), prefix));
  const cleanup = () => fs.rm(dir, { recursive: true, force: true });
  return { dir, cleanup };
}

/**
 * Write a file tree from a plain object.
 * Keys are relative paths, values are file contents (string).
 */
export async function writeTree(root, tree) {
  for (const [relPath, content] of Object.entries(tree)) {
    const fullPath = path.join(root, relPath);
    await fs.mkdir(path.dirname(fullPath), { recursive: true });
    await fs.writeFile(fullPath, content);
  }
}

/**
 * Read all files in a directory tree and return as a plain object.
 * Keys are relative paths (forward slashes), values are file contents.
 */
export async function readTree(root) {
  const result = {};
  async function walk(currentPath) {
    const entries = await fs.readdir(currentPath, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        await walk(entryPath);
      } else {
        const relPath = path.relative(root, entryPath).replace(/\\/g, '/');
        result[relPath] = await fs.readFile(entryPath, 'utf-8');
      }
    }
  }
  await walk(root);
  return result;
}
