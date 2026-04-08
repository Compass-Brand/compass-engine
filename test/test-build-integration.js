import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from '../tools/build.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIST_ROOT = path.join(ROOT, 'dist');

describe('Full build integration', () => {
  it('should produce a valid dist/ from current src/', async () => {
    // Run the real build (includes internal validateBuild())
    await build();

    // --- agent-manifest.csv: exists, has header + data rows ---
    const agentManifest = await fs.readFile(
      path.join(DIST_ROOT, '_bmad', '_config', 'agent-manifest.csv'),
      'utf-8',
    );
    const agentLines = agentManifest.split(/\r?\n/).filter(Boolean);
    assert.ok(agentLines.length >= 2, `agent-manifest.csv should have header + data rows, got ${agentLines.length} lines`);

    // --- skill-manifest.csv: exists, header contains 'name,type' ---
    const skillManifest = await fs.readFile(
      path.join(DIST_ROOT, '_bmad', '_config', 'skill-manifest.csv'),
      'utf-8',
    );
    const skillLines = skillManifest.split(/\r?\n/).filter(Boolean);
    assert.ok(skillLines.length >= 2, `skill-manifest.csv should have header + data rows, got ${skillLines.length} lines`);
    assert.ok(
      skillLines[0].includes('name,type'),
      `skill-manifest.csv header should contain 'name,type', got: ${skillLines[0]}`,
    );

    // --- bmad-help.csv: exists, has data rows ---
    const bmadHelp = await fs.readFile(
      path.join(DIST_ROOT, '_bmad', '_config', 'bmad-help.csv'),
      'utf-8',
    );
    const helpLines = bmadHelp.split(/\r?\n/).filter(Boolean);
    assert.ok(helpLines.length >= 2, `bmad-help.csv should have header + data rows, got ${helpLines.length} lines`);

    // --- Client skills for all 3 platforms: each has >=90 entries ---
    const platforms = ['.claude', '.opencode', '.codex'];
    for (const platform of platforms) {
      const skillsDir = path.join(DIST_ROOT, platform, 'skills');
      const entries = await fs.readdir(skillsDir);
      assert.ok(
        entries.length >= 90,
        `${platform}/skills/ should have >=90 entries, found ${entries.length}`,
      );
    }

    // --- Key bundle directories exist ---
    const requiredDirs = ['planning', 'docs', '.github', 'root', 'beads'];
    for (const dir of requiredDirs) {
      const dirPath = path.join(DIST_ROOT, dir);
      const stat = await fs.stat(dirPath);
      assert.ok(stat.isDirectory(), `${dir}/ should exist as a directory in dist/`);
    }
  });
});
