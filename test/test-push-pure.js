import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import path from 'path';
import { resolveFeatureSelection, resolveWithinProject } from '../tools/push.js';

// ---------------------------------------------------------------------------
// Test fixture for feature groups
// ---------------------------------------------------------------------------
const groups = {
  baseline: ['codeowners', 'dependabot'],
  codeowners: ['CODEOWNERS'],
  dependabot: ['dependabot.yml'],
  linting: ['workflows/lint-core.yml', 'workflows/lint-languages.yml'],
};

// ---------------------------------------------------------------------------
// resolveFeatureSelection
// ---------------------------------------------------------------------------
describe('resolveFeatureSelection', () => {
  it('should return null when requested is null', () => {
    assert.equal(resolveFeatureSelection(groups, null, 'test'), null);
  });

  it('should return null when requested is empty array', () => {
    assert.equal(resolveFeatureSelection(groups, [], 'test'), null);
  });

  it('should return null when requested includes all', () => {
    assert.equal(resolveFeatureSelection(groups, ['all'], 'test'), null);
  });

  it('should resolve leaf features to their file paths', () => {
    const result = resolveFeatureSelection(groups, ['linting'], 'test');
    assert.deepEqual(result, ['workflows/lint-core.yml', 'workflows/lint-languages.yml']);
  });

  it('should resolve nested groups recursively', () => {
    const result = resolveFeatureSelection(groups, ['baseline'], 'test');
    assert.deepEqual(result, ['CODEOWNERS', 'dependabot.yml']);
  });

  it('should deduplicate paths from overlapping selections', () => {
    const result = resolveFeatureSelection(groups, ['baseline', 'codeowners'], 'test');
    assert.deepEqual(result, ['CODEOWNERS', 'dependabot.yml']);
  });

  it('should throw on unknown feature name', () => {
    assert.throws(
      () => resolveFeatureSelection(groups, ['nonexistent'], 'test'),
      (err) => {
        assert(err instanceof Error);
        assert(err.message.includes('nonexistent'));
        return true;
      },
    );
  });

  it('should throw on circular feature definitions', () => {
    const circular = {
      a: ['b'],
      b: ['a'],
    };
    assert.throws(
      () => resolveFeatureSelection(circular, ['a'], 'test'),
      (err) => {
        assert(err instanceof Error);
        assert(err.message.includes('Circular'));
        return true;
      },
    );
  });

  it('should return results sorted alphabetically', () => {
    const result = resolveFeatureSelection(groups, ['linting', 'codeowners'], 'test');
    const sorted = [...result].sort();
    assert.deepEqual(result, sorted);
  });
});

// ---------------------------------------------------------------------------
// resolveWithinProject
// ---------------------------------------------------------------------------
describe('resolveWithinProject', () => {
  const projectRoot = '/tmp/test-project';

  it('should resolve a normal relative path within project', () => {
    const result = resolveWithinProject(projectRoot, 'src/index.js');
    assert.equal(result, path.resolve(projectRoot, 'src/index.js'));
  });

  it('should throw on directory traversal', () => {
    assert.throws(
      () => resolveWithinProject(projectRoot, '../escape.txt'),
      (err) => {
        assert(err instanceof Error);
        assert(err.message.includes('outside project root'));
        return true;
      },
    );
  });

  it('should allow path resolving to project root exactly', () => {
    const result = resolveWithinProject(projectRoot, '.');
    assert.equal(result, path.resolve(projectRoot));
  });

  it('should throw on deeply nested traversal', () => {
    assert.throws(
      () => resolveWithinProject(projectRoot, 'a/../../escape'),
      (err) => {
        assert(err instanceof Error);
        assert(err.message.includes('outside project root'));
        return true;
      },
    );
  });
});
