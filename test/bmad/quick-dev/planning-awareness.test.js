import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, basename } from 'node:path';
import { selectPlanningArtifacts } from '../../../tools/quick-dev-scan.js';

function planningFixture() {
  const tmp = mkdtempSync(join(tmpdir(), 'planning-aware-'));
  const dir = join(tmp, 'planning');
  mkdirSync(dir, { recursive: true });

  writeFileSync(
    join(dir, 'prd.md'),
    '# PRD: Authentication Flow\n\nProduct requirements for auth, login, sessions.\n'
  );
  writeFileSync(
    join(dir, 'architecture.md'),
    '# Architecture: Auth Stack\n\nSession tokens, JWT, refresh rotation.\n'
  );
  writeFileSync(
    join(dir, 'ux-checkout.md'),
    '# UX: Checkout Flow\n\nCart, payment, confirmation screens.\n'
  );
  writeFileSync(
    join(dir, 'notes.md'),
    '# Random engineering notes\n\nUnrelated scratch pad.\n'
  );
  return { tmp, dir };
}

describe('selectPlanningArtifacts', () => {
  let dir;
  let tmp;

  before(() => {
    ({ tmp, dir } = planningFixture());
  });

  after(() => {
    rmSync(tmp, { recursive: true, force: true });
  });

  it('picks PRD and architecture when intent is about auth', () => {
    const result = selectPlanningArtifacts(
      ['implement auth refresh token rotation'],
      dir
    );
    const names = result.map((p) => basename(p)).sort();
    assert.deepEqual(names, ['architecture.md', 'prd.md']);
  });

  it('picks UX file when intent is about checkout UX', () => {
    const result = selectPlanningArtifacts(
      ['tweak checkout screen copy and layout'],
      dir
    );
    const names = result.map((p) => basename(p));
    assert.ok(names.includes('ux-checkout.md'));
    assert.ok(!names.includes('architecture.md'));
    assert.ok(!names.includes('prd.md'));
  });

  it('returns empty array when intent matches no planning artifact', () => {
    const result = selectPlanningArtifacts(
      ['bump dependency version in package.json'],
      dir
    );
    assert.deepEqual(result, []);
  });

  it('ignores files outside the planning glob set', () => {
    const result = selectPlanningArtifacts(['auth refresh tokens'], dir);
    const names = result.map((p) => basename(p));
    assert.ok(!names.includes('notes.md'));
  });

  it('returns empty array when directory does not exist', () => {
    const result = selectPlanningArtifacts(
      ['anything'],
      join(dir, 'does-not-exist')
    );
    assert.deepEqual(result, []);
  });

  it('returns empty array when intents is empty', () => {
    const result = selectPlanningArtifacts([], dir);
    assert.deepEqual(result, []);
  });
});
