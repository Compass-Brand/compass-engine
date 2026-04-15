import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(__dirname, '..', '..', '..');
const step01Path = join(
  repoRoot,
  'src',
  'bmad',
  'modules',
  'custom',
  'bmm-skills',
  '4-implementation',
  'bmad-quick-dev',
  'steps',
  'step-01-mode-detection.md'
);
const step02Path = join(
  repoRoot,
  'src',
  'bmad',
  'modules',
  'custom',
  'bmm-skills',
  '4-implementation',
  'bmad-quick-dev',
  'steps',
  'step-02-context-gathering.md'
);
const step03Path = join(
  repoRoot,
  'src',
  'bmad',
  'modules',
  'custom',
  'bmm-skills',
  '4-implementation',
  'bmad-quick-dev',
  'steps',
  'step-03-execute.md'
);

const step01 = readFileSync(step01Path, 'utf8');
const step02 = readFileSync(step02Path, 'utf8');
const step03 = readFileSync(step03Path, 'utf8');

describe('step-01-mode-detection.md structure (PR-A hooks)', () => {
  describe('required sub-section headings', () => {
    it('contains ### A.1 Epic inference heading', () => {
      assert.match(step01, /^####\s+A\.1\s+Epic inference\s*$/m);
    });

    it('contains ### A.2 Previous story continuity heading', () => {
      assert.match(step01, /^####\s+A\.2\s+Previous story continuity\s*$/m);
    });

    it('contains ### B.0 Planning artifact scan heading', () => {
      assert.match(step01, /^####\s+B\.0\s+Planning artifact scan\s*$/m);
    });
  });

  describe('STATE VARIABLES documentation', () => {
    it('documents {epic_num}', () => {
      assert.match(step01, /`\{epic_num\}`/);
    });

    it('documents {story_num}', () => {
      assert.match(step01, /`\{story_num\}`/);
    });

    it('documents {epic_context_path} with precedence note', () => {
      assert.match(step01, /`\{epic_context_path\}`/);
      // Precedence: epic_context_path beats planning_context_files
      assert.match(
        step01,
        /\{epic_context_path\}[\s\S]*?IGNORE[\s\S]*?\{planning_context_files\}/i
      );
    });

    it('documents {continuity_context}', () => {
      assert.match(step01, /`\{continuity_context\}`/);
    });

    it('documents {planning_context_files}', () => {
      assert.match(step01, /`\{planning_context_files\}`/);
    });
  });

  describe('frontmatter exposure', () => {
    it('exposes {epic_context_path} in the frontmatter state_vars list', () => {
      const frontmatterMatch = step01.match(/^---\n([\s\S]*?)\n---/);
      assert.ok(frontmatterMatch, 'step-01 must have YAML frontmatter');
      const fm = frontmatterMatch[1];
      assert.match(
        fm,
        /epic_context_path/,
        'frontmatter must list epic_context_path as a state var'
      );
    });
  });

  describe('NEXT directives', () => {
    it('mentions step-02-context-gathering in Mode B NEXT', () => {
      assert.match(step01, /step-02-context-gathering\.md/);
    });

    it('mentions step-03-execute in Mode A NEXT', () => {
      assert.match(step01, /step-03-execute\.md/);
    });
  });
});

describe('step-02-context-gathering.md loads epic + continuity + planning context', () => {
  it('references {epic_context_path} in AVAILABLE STATE or Load Context', () => {
    assert.match(step02, /\{epic_context_path\}/);
  });

  it('references {continuity_context}', () => {
    assert.match(step02, /\{continuity_context\}/);
  });

  it('references {planning_context_files}', () => {
    assert.match(step02, /\{planning_context_files\}/);
  });

  it('enforces precedence: ignore planning_context_files when epic_context_path is set', () => {
    assert.match(
      step02,
      /\{epic_context_path\}[\s\S]*?IGNORE[\s\S]*?\{planning_context_files\}/i,
      'step-02 must explicitly enforce Feature 1 > Feature 3 precedence'
    );
  });
});

describe('step-03-execute.md loads epic + continuity context', () => {
  it('references {epic_context_path} in AVAILABLE STATE or Load Context', () => {
    assert.match(step03, /\{epic_context_path\}/);
  });

  it('references {continuity_context}', () => {
    assert.match(step03, /\{continuity_context\}/);
  });
});
