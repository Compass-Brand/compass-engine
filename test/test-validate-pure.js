import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {
  shouldScanSourceFile,
  isLikelyPlaceholder,
  findSecretIndicators,
  parseCsvLine,
  rejectsBmadInitReferences,
  validateNoBmadInitReferences,
} from '../tools/validate.js';

// ---------------------------------------------------------------------------
// shouldScanSourceFile
// ---------------------------------------------------------------------------
describe('shouldScanSourceFile', () => {
  it('should scan .js files', () => {
    assert.equal(shouldScanSourceFile('src/index.js'), true);
  });

  it('should scan .ts files', () => {
    assert.equal(shouldScanSourceFile('src/main.ts'), true);
  });

  it('should scan .yaml files', () => {
    assert.equal(shouldScanSourceFile('config/settings.yaml'), true);
  });

  it('should scan .env files', () => {
    assert.equal(shouldScanSourceFile('app.env'), true);
  });

  it('should skip .example files', () => {
    assert.equal(shouldScanSourceFile('config.env.example'), false);
  });

  it('should skip .template files', () => {
    assert.equal(shouldScanSourceFile('settings.template'), false);
  });

  it('should skip .sample files', () => {
    assert.equal(shouldScanSourceFile('config.sample'), false);
  });

  it('should skip files in /fixtures/ directories', () => {
    assert.equal(shouldScanSourceFile('test/fixtures/secret.js'), false);
  });

  it('should skip unknown extensions like .md', () => {
    assert.equal(shouldScanSourceFile('README.md'), false);
  });

  it('should skip binary types like .png', () => {
    assert.equal(shouldScanSourceFile('logo.png'), false);
  });
});

// ---------------------------------------------------------------------------
// isLikelyPlaceholder
// ---------------------------------------------------------------------------
describe('isLikelyPlaceholder', () => {
  it('should detect example keyword', () => {
    assert.equal(isLikelyPlaceholder('this-is-an-example-key'), true);
  });

  it('should detect changeme', () => {
    assert.equal(isLikelyPlaceholder('changeme'), true);
  });

  it('should detect your_ prefix', () => {
    assert.equal(isLikelyPlaceholder('your_api_key_here'), true);
  });

  it('should detect your- prefix', () => {
    assert.equal(isLikelyPlaceholder('your-api-key-here'), true);
  });

  it('should detect dummy', () => {
    assert.equal(isLikelyPlaceholder('dummy-value'), true);
  });

  it('should detect test keyword', () => {
    assert.equal(isLikelyPlaceholder('test-token-value'), true);
  });

  it('should detect template variable ${...}', () => {
    assert.equal(isLikelyPlaceholder('${API_KEY}'), true);
  });

  it('should detect mustache {{...}}', () => {
    assert.equal(isLikelyPlaceholder('{{api_key}}'), true);
  });

  it('should return false for real values', () => {
    assert.equal(isLikelyPlaceholder('sk-abc123realkey456'), false);
  });

  it('should be case-insensitive', () => {
    assert.equal(isLikelyPlaceholder('CHANGEME'), true);
  });
});

// ---------------------------------------------------------------------------
// findSecretIndicators
// ---------------------------------------------------------------------------
describe('findSecretIndicators', () => {
  it('should detect ctx7 token pattern', () => {
    const content = 'ctx7sk-abcdefghijklmnopqrstuv';
    const result = findSecretIndicators(content);
    assert.match(result, /ctx7 token/);
  });

  it('should detect GitHub PAT (ghp-)', () => {
    const content = 'token = ghp-abcdefghijklmnopqrstuv';
    const result = findSecretIndicators(content);
    assert.match(result, /API token/);
  });

  it('should detect sk- prefixed tokens', () => {
    const content = 'key = sk-abcdefghijklmnopqrstuvwxyz';
    const result = findSecretIndicators(content);
    assert.match(result, /API token/);
  });

  it('should detect api_key with real value', () => {
    const content = 'api_key = "sk1abc2def3ghi4jkl"';
    const result = findSecretIndicators(content);
    assert.match(result, /api_key/);
  });

  it('should ignore api_key with placeholder value', () => {
    const content = 'api_key = "your_api_key_here"';
    const result = findSecretIndicators(content);
    assert.equal(result, null);
  });

  it('should return null for clean content', () => {
    const content = 'const x = 42;\nconsole.log("hello world");';
    const result = findSecretIndicators(content);
    assert.equal(result, null);
  });

  it('should report correct line number', () => {
    const content = 'line one\nline two\nctx7sk-abcdefghijklmnopqrstuv\nline four';
    const result = findSecretIndicators(content);
    assert.match(result, /line 3/);
  });

  it('should detect api-key (hyphenated variant)', () => {
    const content = 'api-key = "realSecretValue1234567"';
    const result = findSecretIndicators(content);
    assert.match(result, /api_key/);
  });
});

// ---------------------------------------------------------------------------
// parseCsvLine
// ---------------------------------------------------------------------------
describe('parseCsvLine', () => {
  it('should parse simple comma-separated values', () => {
    assert.deepEqual(parseCsvLine('a,b,c'), ['a', 'b', 'c']);
  });

  it('should handle quoted fields with commas', () => {
    assert.deepEqual(parseCsvLine('a,"b,c",d'), ['a', 'b,c', 'd']);
  });

  it('should handle escaped double quotes', () => {
    assert.deepEqual(parseCsvLine('a,"say ""hi""",c'), ['a', 'say "hi"', 'c']);
  });

  it('should handle empty fields', () => {
    assert.deepEqual(parseCsvLine('a,,c'), ['a', '', 'c']);
  });

  it('should handle trailing comma', () => {
    assert.deepEqual(parseCsvLine('a,b,'), ['a', 'b', '']);
  });

  it('should handle single field', () => {
    assert.deepEqual(parseCsvLine('hello'), ['hello']);
  });
});

// ---------------------------------------------------------------------------
// rejectsBmadInitReferences
// ---------------------------------------------------------------------------
describe('rejectsBmadInitReferences', () => {
  it('should return empty array for clean content', () => {
    const result = rejectsBmadInitReferences('line one\nline two\nnothing here');
    assert.deepEqual(result, []);
  });

  it('should return line numbers for content containing bmad-init', () => {
    const content = 'line one\nload via bmad-init skill\nline three';
    const result = rejectsBmadInitReferences(content);
    assert.equal(result.length, 1);
    assert.equal(result[0].lineNumber, 2);
    assert.match(result[0].text, /bmad-init/);
  });

  it('should report every line that contains the term', () => {
    const content = 'bmad-init here\nand bmad-init there\nclean\nfinal bmad-init';
    const result = rejectsBmadInitReferences(content);
    assert.deepEqual(
      result.map((r) => r.lineNumber),
      [1, 2, 4],
    );
  });
});

// ---------------------------------------------------------------------------
// validateNoBmadInitReferences — live-tree scan against a temp fixture
// ---------------------------------------------------------------------------
describe('validateNoBmadInitReferences', () => {
  it('should fail when a seeded SKILL.md contains bmad-init', async () => {
    const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'validate-bmad-init-'));
    const skillDir = path.join(tempRoot, 'src/bmad/modules/native/core-skills/bmad-seeded');
    await fs.mkdir(skillDir, { recursive: true });
    await fs.writeFile(
      path.join(skillDir, 'SKILL.md'),
      '---\nname: bmad-seeded\n---\n\n## On Activation\n\n1. Load via bmad-init skill\n',
    );
    const errors = [];
    const ok = await validateNoBmadInitReferences(tempRoot, { log: (msg) => errors.push(msg) });
    await fs.rm(tempRoot, { recursive: true, force: true });
    assert.equal(ok, false);
    assert.equal(errors.length, 1);
    assert.match(errors[0], /bmad-seeded\/SKILL\.md/);
    assert.match(errors[0], /line 7/);
  });

  it('should pass when no SKILL.md references bmad-init', async () => {
    const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'validate-bmad-init-'));
    const skillDir = path.join(tempRoot, 'src/bmad/modules/native/core-skills/bmad-clean');
    await fs.mkdir(skillDir, { recursive: true });
    await fs.writeFile(
      path.join(skillDir, 'SKILL.md'),
      '---\nname: bmad-clean\n---\n\n## On Activation\n\n1. Load config from {project-root}/_bmad/core/config.yaml\n',
    );
    const errors = [];
    const ok = await validateNoBmadInitReferences(tempRoot, { log: (msg) => errors.push(msg) });
    await fs.rm(tempRoot, { recursive: true, force: true });
    assert.equal(ok, true);
    assert.equal(errors.length, 0);
  });

  it('should allowlist bmad-distillator distillate-format-reference.md example content', async () => {
    const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'validate-bmad-init-'));
    const distillatorDir = path.join(
      tempRoot,
      'src/bmad/modules/native/core-skills/bmad-distillator/resources',
    );
    await fs.mkdir(distillatorDir, { recursive: true });
    await fs.writeFile(
      path.join(distillatorDir, 'distillate-format-reference.md'),
      '# Example\n\nThis references bmad-init inside a fictional distillate.\n',
    );
    const errors = [];
    const ok = await validateNoBmadInitReferences(tempRoot, { log: (msg) => errors.push(msg) });
    await fs.rm(tempRoot, { recursive: true, force: true });
    assert.equal(ok, true);
    assert.equal(errors.length, 0);
  });
});
