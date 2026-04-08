import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  normalizePath,
  shouldSkip,
  parseSimpleYaml,
  parseCsvRows,
  clientSkillName,
} from '../tools/build.js';

// ---------------------------------------------------------------------------
// normalizePath
// ---------------------------------------------------------------------------
describe('normalizePath', () => {
  it('should convert backslashes to forward slashes', () => {
    assert.equal(normalizePath('foo\\bar\\baz'), 'foo/bar/baz');
  });

  it('should return already-normalized paths unchanged', () => {
    assert.equal(normalizePath('foo/bar/baz'), 'foo/bar/baz');
  });

  it('should return empty string for empty input', () => {
    assert.equal(normalizePath(''), '');
  });
});

// ---------------------------------------------------------------------------
// shouldSkip
// ---------------------------------------------------------------------------
describe('shouldSkip', () => {
  it('should return false when skipPaths is empty', () => {
    assert.equal(shouldSkip('foo/bar.txt', []), false);
  });

  it('should return false when skipPaths is null', () => {
    assert.equal(shouldSkip('foo/bar.txt', null), false);
  });

  it('should match an exact path', () => {
    assert.equal(shouldSkip('README.md', ['README.md']), true);
  });

  it('should match a prefix (directory)', () => {
    assert.equal(shouldSkip('docs/guide/intro.md', ['docs']), true);
  });

  it('should not partially match a filename', () => {
    // "doc" should not match "docs/guide.md" because "docs/guide.md" does not
    // equal "doc" and does not start with "doc/"
    assert.equal(shouldSkip('docs/guide.md', ['doc']), false);
  });

  it('should normalize backslashes before comparing', () => {
    assert.equal(shouldSkip('foo\\bar\\baz.txt', ['foo/bar']), true);
  });
});

// ---------------------------------------------------------------------------
// parseSimpleYaml
// ---------------------------------------------------------------------------
describe('parseSimpleYaml', () => {
  it('should parse basic key:value pairs', () => {
    const result = parseSimpleYaml('name: hello\ntype: agent');
    assert.deepEqual(result, { name: 'hello', type: 'agent' });
  });

  it('should strip surrounding double quotes from values', () => {
    const result = parseSimpleYaml('title: "My Title"');
    assert.deepEqual(result, { title: 'My Title' });
  });

  it('should skip comment lines', () => {
    const result = parseSimpleYaml('# this is a comment\nname: test');
    assert.deepEqual(result, { name: 'test' });
  });

  it('should skip empty lines', () => {
    const result = parseSimpleYaml('name: a\n\n\ntype: b');
    assert.deepEqual(result, { name: 'a', type: 'b' });
  });

  it('should handle colons inside the value portion', () => {
    const result = parseSimpleYaml('url: http://example.com:8080');
    assert.deepEqual(result, { url: 'http://example.com:8080' });
  });

  it('should decode \\U unicode escapes to actual emoji', () => {
    const result = parseSimpleYaml('icon: "\\U0001F680"');
    assert.deepEqual(result, { icon: '\u{1F680}' }); // rocket emoji
  });

  it('should skip lines without a colon', () => {
    const result = parseSimpleYaml('no-colon-here\nname: ok');
    assert.deepEqual(result, { name: 'ok' });
  });

  it('should return empty object for empty string', () => {
    assert.deepEqual(parseSimpleYaml(''), {});
  });
});

// ---------------------------------------------------------------------------
// parseCsvRows
// ---------------------------------------------------------------------------
describe('parseCsvRows', () => {
  it('should parse basic CSV with header and data rows', () => {
    const csv = 'name,type\nalpha,one\nbeta,two';
    const result = parseCsvRows(csv);
    assert.deepEqual(result, [
      { name: 'alpha', type: 'one' },
      { name: 'beta', type: 'two' },
    ]);
  });

  it('should handle quoted fields containing commas', () => {
    const csv = 'name,desc\nalpha,"has, comma"';
    const result = parseCsvRows(csv);
    assert.deepEqual(result, [{ name: 'alpha', desc: 'has, comma' }]);
  });

  it('should handle escaped quotes (doubled double-quotes)', () => {
    const csv = 'name,desc\nalpha,"say ""hi"""';
    const result = parseCsvRows(csv);
    assert.deepEqual(result, [{ name: 'alpha', desc: 'say "hi"' }]);
  });

  it('should default missing cells to empty string', () => {
    const csv = 'a,b,c\n1,2';
    const result = parseCsvRows(csv);
    assert.equal(result.length, 1);
    assert.equal(result[0].c, '');
  });

  it('should return empty array for header-only input', () => {
    assert.deepEqual(parseCsvRows('name,type'), []);
  });

  it('should return empty array for single line', () => {
    assert.deepEqual(parseCsvRows('only-one-line'), []);
  });

  it('should handle a trailing comma (empty last field)', () => {
    const csv = 'a,b\n1,';
    const result = parseCsvRows(csv);
    assert.deepEqual(result, [{ a: '1', b: '' }]);
  });
});

// ---------------------------------------------------------------------------
// clientSkillName
// ---------------------------------------------------------------------------
describe('clientSkillName', () => {
  it('should pass through bmad-compass-* names unchanged', () => {
    assert.equal(clientSkillName('bmad-compass-deploy', 'compass'), 'bmad-compass-deploy');
  });

  it('should pass through bmad-agent-compass-* names unchanged', () => {
    assert.equal(
      clientSkillName('bmad-agent-compass-nav', 'compass'),
      'bmad-agent-compass-nav',
    );
  });

  it('should use "builder" as the short prefix for bmad-builder module', () => {
    assert.equal(
      clientSkillName('bmad-create-module', 'bmad-builder'),
      'bmad-builder-create-module',
    );
  });

  it('should transform agent names: bmad-agent-{name} -> bmad-agent-{module}-{name}', () => {
    assert.equal(
      clientSkillName('bmad-agent-analyst', 'bmm'),
      'bmad-agent-bmm-analyst',
    );
  });

  it('should map bmad-master to bmad-core-master', () => {
    assert.equal(clientSkillName('bmad-master', 'core'), 'bmad-core-master');
  });

  it('should transform workflow names: bmad-{name} -> bmad-{module}-{name}', () => {
    assert.equal(
      clientSkillName('bmad-create-prd', 'bmm'),
      'bmad-bmm-create-prd',
    );
  });

  it('should use builder prefix for agent names in bmad-builder module', () => {
    assert.equal(
      clientSkillName('bmad-agent-tech-writer', 'bmad-builder'),
      'bmad-agent-builder-tech-writer',
    );
  });
});
