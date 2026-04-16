import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, basename } from 'node:path';
import { findPreviousStoryDone } from '../../../tools/quick-dev-scan.js';

function spec({ epic, story, slug, status, sections = {} }) {
  const fm = [
    '---',
    `epic: ${epic}`,
    `story: '${epic}.${story}'`,
    `status: ${status}`,
    '---',
    '',
  ].join('\n');
  const body = [
    `# Spec ${epic}.${story} ${slug}`,
    '',
    '## Code Map',
    '',
    sections.codeMap ?? `code-map-body-${epic}-${story}`,
    '',
    '## Design Notes',
    '',
    sections.designNotes ?? `design-notes-body-${epic}-${story}`,
    '',
    '## Spec Change Log',
    '',
    sections.specChangeLog ?? `change-log-body-${epic}-${story}`,
    '',
    '## Tasks',
    '',
    sections.tasks ?? `tasks-body-${epic}-${story}`,
    '',
  ].join('\n');
  return fm + body;
}

describe('findPreviousStoryDone', () => {
  let artifactsDir;

  before(() => {
    const tmp = mkdtempSync(join(tmpdir(), 'continuity-'));
    artifactsDir = join(tmp, 'impl-artifacts');
    mkdirSync(artifactsDir, { recursive: true });

    writeFileSync(
      join(artifactsDir, 'spec-3-1-foo.md'),
      spec({
        epic: 3,
        story: 1,
        slug: 'foo',
        status: 'done',
        sections: {
          codeMap: 'foo-code-map',
          designNotes: 'foo-design-notes',
          specChangeLog: 'foo-change-log',
          tasks: 'foo-tasks',
        },
      })
    );
    writeFileSync(
      join(artifactsDir, 'spec-3-2-bar.md'),
      spec({
        epic: 3,
        story: 2,
        slug: 'bar',
        status: 'done',
        sections: {
          codeMap: 'bar-code-map',
          designNotes: 'bar-design-notes',
          specChangeLog: 'bar-change-log',
          tasks: 'bar-tasks',
        },
      })
    );
    writeFileSync(
      join(artifactsDir, 'spec-3-3-baz.md'),
      spec({ epic: 3, story: 3, slug: 'baz', status: 'draft' })
    );
  });

  after(() => {
    rmSync(artifactsDir, { recursive: true, force: true });
  });

  it('selects the max-story-number done spec below the current story', () => {
    const result = findPreviousStoryDone(artifactsDir, 3, 3);
    assert.ok(result, 'expected a match');
    assert.equal(basename(result.path), 'spec-3-2-bar.md');
    assert.equal(result.storyNum, 2);
  });

  it('builds continuity_context with the four named section bodies', () => {
    const result = findPreviousStoryDone(artifactsDir, 3, 3);
    assert.ok(result);
    const ctx = result.continuityContext;
    assert.match(ctx, /## Code Map/);
    assert.match(ctx, /## Design Notes/);
    assert.match(ctx, /## Spec Change Log/);
    assert.match(ctx, /## Tasks/);
    assert.match(ctx, /bar-code-map/);
    assert.match(ctx, /bar-design-notes/);
    assert.match(ctx, /bar-change-log/);
    assert.match(ctx, /bar-tasks/);
  });

  it('includes a provenance header naming the source spec and done status', () => {
    const result = findPreviousStoryDone(artifactsDir, 3, 3);
    assert.ok(result);
    assert.match(
      result.continuityContext,
      /^> Continuity from spec-3-2-bar\.md \(status: done\)/m
    );
  });

  it('does not select draft or current-story specs', () => {
    const result = findPreviousStoryDone(artifactsDir, 3, 3);
    assert.ok(result);
    assert.notEqual(basename(result.path), 'spec-3-3-baz.md');
    assert.equal(/baz/.test(result.continuityContext), false);
  });

  it('returns null when no lower-story done spec exists', () => {
    const tmp2 = mkdtempSync(join(tmpdir(), 'continuity-empty-'));
    const empty = join(tmp2, 'impl');
    mkdirSync(empty, { recursive: true });
    writeFileSync(
      join(empty, 'spec-3-5-only.md'),
      spec({ epic: 3, story: 5, slug: 'only', status: 'draft' })
    );
    assert.equal(findPreviousStoryDone(empty, 3, 5), null);
    rmSync(tmp2, { recursive: true, force: true });
  });

  it('returns null when the artifacts directory does not exist', () => {
    assert.equal(
      findPreviousStoryDone(join(artifactsDir, 'does-not-exist'), 3, 3),
      null
    );
  });

  it('filters by epic — ignores same-story-number specs from other epics', () => {
    const tmp3 = mkdtempSync(join(tmpdir(), 'continuity-epic-'));
    const dir = join(tmp3, 'impl');
    mkdirSync(dir, { recursive: true });
    writeFileSync(
      join(dir, 'spec-4-1-other.md'),
      spec({ epic: 4, story: 1, slug: 'other', status: 'done' })
    );
    assert.equal(findPreviousStoryDone(dir, 3, 3), null);
    rmSync(tmp3, { recursive: true, force: true });
  });
});
