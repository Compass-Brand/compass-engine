import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, rmSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import {
  extractEpicNum,
  epicContextIsCached,
} from '../../../tools/quick-dev-scan.js';

describe('extractEpicNum', () => {
  describe('frontmatter field resolution', () => {
    it('returns the integer value of the epic: field when present', () => {
      assert.equal(extractEpicNum({ epic: 3 }, 'spec-3-2-auth.md'), 3);
    });

    it('returns the integer value of a stringified epic: field', () => {
      assert.equal(extractEpicNum({ epic: '4' }, 'anything.md'), 4);
    });

    it('falls back to story: E.S parsing when epic: is absent', () => {
      assert.equal(extractEpicNum({ story: '3.2' }, 'anything.md'), 3);
    });

    it('falls back to filename slug ^(\\d+)- when no frontmatter epic/story', () => {
      assert.equal(extractEpicNum({}, 'spec-7-1-foo.md'), 7);
    });

    it('prefers epic: over story: when both present', () => {
      assert.equal(
        extractEpicNum({ epic: 5, story: '9.1' }, 'spec-8-3-x.md'),
        5
      );
    });

    it('prefers story: over filename when epic: absent', () => {
      assert.equal(
        extractEpicNum({ story: '2.1' }, 'spec-8-3-x.md'),
        2
      );
    });
  });

  describe('no-match cases', () => {
    it('returns null when frontmatter is empty and filename has no leading digits', () => {
      assert.equal(extractEpicNum({}, 'spec-auth.md'), null);
    });

    it('returns null when epic: is not a positive integer', () => {
      assert.equal(extractEpicNum({ epic: 'not-a-number' }, 'noprefix.md'), null);
      assert.equal(extractEpicNum({ epic: 0 }, 'noprefix.md'), null);
      assert.equal(extractEpicNum({ epic: -1 }, 'noprefix.md'), null);
    });

    it('returns null when story: is malformed', () => {
      assert.equal(extractEpicNum({ story: 'bogus' }, 'noprefix.md'), null);
    });
  });

  describe('input guards', () => {
    it('tolerates null/undefined frontmatter and falls back to filename', () => {
      assert.equal(extractEpicNum(null, 'spec-3-2-x.md'), 3);
      assert.equal(extractEpicNum(undefined, 'spec-3-2-x.md'), 3);
    });

    it('returns null when both frontmatter and filename are missing', () => {
      assert.equal(extractEpicNum(null, ''), null);
      assert.equal(extractEpicNum(null, null), null);
    });
  });
});

describe('epicContextIsCached', () => {
  let tmpDir;

  before(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'epic-cache-'));
  });

  after(() => {
    rmSync(tmpDir, { recursive: true, force: true });
  });

  it('returns true when the epic context file exists in the impl artifacts dir', () => {
    const artifactsDir = join(tmpDir, 'artifacts-hit');
    mkdirSync(artifactsDir, { recursive: true });
    writeFileSync(join(artifactsDir, 'epic-3-context.md'), '# Epic 3 Context: x\n');
    assert.equal(epicContextIsCached(artifactsDir, 3), true);
  });

  it('returns false when the epic context file is missing', () => {
    const artifactsDir = join(tmpDir, 'artifacts-miss');
    mkdirSync(artifactsDir, { recursive: true });
    assert.equal(epicContextIsCached(artifactsDir, 9), false);
  });

  it('returns false when the artifacts directory does not exist', () => {
    assert.equal(
      epicContextIsCached(join(tmpDir, 'does-not-exist'), 3),
      false
    );
  });

  it('returns false when epicNum is not a positive integer', () => {
    const artifactsDir = join(tmpDir, 'artifacts-bad-epic');
    mkdirSync(artifactsDir, { recursive: true });
    writeFileSync(join(artifactsDir, 'epic-3-context.md'), '# Epic 3 Context: x\n');
    assert.equal(epicContextIsCached(artifactsDir, 0), false);
    assert.equal(epicContextIsCached(artifactsDir, -1), false);
    assert.equal(epicContextIsCached(artifactsDir, null), false);
  });
});
