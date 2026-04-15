import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { validateRemovedAgents } from '../tools/validate.js';
import { createTempDir, writeTree } from './helpers.js';

const NATIVE_IMPL = 'src/bmad/modules/native/bmm-skills/4-implementation';

async function captureErrors(fn) {
  const errors = [];
  const orig = console.error;
  console.error = (msg) => errors.push(String(msg));
  try {
    const result = await fn();
    return { result, errors };
  } finally {
    console.error = orig;
  }
}

describe('validateRemovedAgents', () => {
  it('returns true on live source tree when deprecated agents are absent', async () => {
    const result = await validateRemovedAgents();
    assert.equal(result, true, 'live tree should not contain any deprecated native agents');
  });

  it('returns false when bmad-agent-qa is reintroduced and cites upstream PR #2179', async () => {
    const { dir, cleanup } = await createTempDir('ce-removed-agents-qa-');
    try {
      await writeTree(dir, {
        [`${NATIVE_IMPL}/bmad-agent-qa/SKILL.md`]: '# reintroduced\n',
      });
      const { result, errors } = await captureErrors(() => validateRemovedAgents(dir));
      assert.equal(result, false);
      assert.match(errors.join('\n'), /#2179/, 'error message must cite PR #2179');
    } finally {
      await cleanup();
    }
  });

  it('returns false when bmad-agent-sm is reintroduced and cites upstream PR #2186', async () => {
    const { dir, cleanup } = await createTempDir('ce-removed-agents-sm-');
    try {
      await writeTree(dir, {
        [`${NATIVE_IMPL}/bmad-agent-sm/SKILL.md`]: '# reintroduced\n',
      });
      const { result, errors } = await captureErrors(() => validateRemovedAgents(dir));
      assert.equal(result, false);
      assert.match(errors.join('\n'), /#2186/, 'error message must cite PR #2186');
    } finally {
      await cleanup();
    }
  });

  it('returns false when bmad-agent-quick-flow-solo-dev is reintroduced and cites upstream PR #2177', async () => {
    const { dir, cleanup } = await createTempDir('ce-removed-agents-qfsd-');
    try {
      await writeTree(dir, {
        [`${NATIVE_IMPL}/bmad-agent-quick-flow-solo-dev/SKILL.md`]: '# reintroduced\n',
      });
      const { result, errors } = await captureErrors(() => validateRemovedAgents(dir));
      assert.equal(result, false);
      assert.match(errors.join('\n'), /#2177/, 'error message must cite PR #2177');
    } finally {
      await cleanup();
    }
  });
});
