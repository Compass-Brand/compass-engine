import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { generateSpecTrace } from '../../../tools/quick-dev-scan.js';

const sampleChanges = [
  {
    path: 'src/auth/refresh.ts',
    line: 42,
    concern: 'Refresh-token rotation',
    framing: 'Central rotation logic, the design intent entry point',
  },
  {
    path: 'src/auth/refresh.ts',
    line: 88,
    concern: 'Refresh-token rotation',
    framing: 'Emits the audit event on successful rotation',
  },
  {
    path: 'test/auth/refresh.test.ts',
    line: 10,
    concern: 'Tests',
    framing: 'Covers happy path and replay-attack guard',
  },
];

describe('generateSpecTrace (one-shot)', () => {
  it('produces frontmatter with route: one-shot and status: done', () => {
    const out = generateSpecTrace({
      intent: 'implement refresh token rotation for story 3.2',
      route: 'one-shot',
      changes: sampleChanges,
      slug: '3-2-refresh-rotation',
      title: 'Refresh token rotation',
      problem: 'Sessions outlive their revocation window',
      approach: 'Rotate refresh tokens on every use, revoke previous JTI',
    });
    assert.match(out, /^---\n/);
    assert.match(out, /\nroute: 'one-shot'\n/);
    assert.match(out, /\nstatus: 'done'\n/);
    assert.match(out, /\ntitle: 'Refresh token rotation'\n/);
  });

  it('writes Title heading and Intent section with Problem + Approach', () => {
    const out = generateSpecTrace({
      intent: 'implement refresh token rotation',
      route: 'one-shot',
      changes: sampleChanges,
      slug: '3-2-refresh-rotation',
      title: 'Refresh token rotation',
      problem: 'Sessions outlive their revocation window',
      approach: 'Rotate refresh tokens on every use, revoke previous JTI',
    });
    assert.match(out, /\n# Refresh token rotation\n/);
    assert.match(out, /\n## Intent\n/);
    assert.match(out, /\*\*Problem:\*\* Sessions outlive their revocation window/);
    assert.match(out, /\*\*Approach:\*\* Rotate refresh tokens on every use/);
  });

  it('writes Suggested Review Order with spec-file-relative links', () => {
    const out = generateSpecTrace({
      intent: 'implement refresh token rotation',
      route: 'one-shot',
      changes: sampleChanges,
      slug: '3-2-refresh-rotation',
      title: 'Refresh token rotation',
      problem: 'p',
      approach: 'a',
      specFileDir: 'docs/impl-artifacts',
    });
    assert.match(out, /\n## Suggested Review Order\n/);
    assert.match(out, /\*\*Refresh-token rotation\*\*/);
    assert.match(out, /\[`refresh\.ts:42`\]\(\.\.\/\.\.\/src\/auth\/refresh\.ts#L42\)/);
    assert.match(out, /\[`refresh\.test\.ts:10`\]\(\.\.\/\.\.\/test\/auth\/refresh\.test\.ts#L10\)/);
  });

  it('supports route: standard for step-07-spec-trace write-back', () => {
    const out = generateSpecTrace({
      intent: 'refactor auth middleware',
      route: 'standard',
      changes: sampleChanges.slice(0, 1),
      slug: 'refactor-auth-middleware',
      title: 'Refactor auth middleware',
      problem: 'middleware coupled to legacy storage',
      approach: 'extract token store interface',
    });
    assert.match(out, /\nroute: 'standard'\n/);
    assert.match(out, /\nstatus: 'done'\n/);
  });

  it('orders peripherals (tests/config) after primary concerns', () => {
    const out = generateSpecTrace({
      intent: 'token work',
      route: 'one-shot',
      changes: sampleChanges,
      slug: 'token-work',
      title: 'Token work',
      problem: 'p',
      approach: 'a',
    });
    const idxRotation = out.indexOf('**Refresh-token rotation**');
    const idxTests = out.indexOf('**Tests**');
    assert.ok(idxRotation >= 0 && idxTests >= 0);
    assert.ok(idxRotation < idxTests, 'peripherals (Tests) should come after primary concerns');
  });
});
