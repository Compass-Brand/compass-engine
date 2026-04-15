import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { deriveSpecSlug } from '../tools/quick-dev-scan.js';

describe('deriveSpecSlug', () => {
  describe('basic kebab-case derivation', () => {
    it('should convert a simple intent to kebab-case', () => {
      assert.equal(
        deriveSpecSlug('Refactor user profile view'),
        'refactor-user-profile-view'
      );
    });

    it('should collapse whitespace and strip punctuation', () => {
      assert.equal(
        deriveSpecSlug('  Fix: the login  form!  '),
        'fix-the-login-form'
      );
    });

    it('should lowercase uppercase input', () => {
      assert.equal(deriveSpecSlug('ADD CACHE LAYER'), 'add-cache-layer');
    });

    it('should drop filler characters and keep alphanumerics', () => {
      assert.equal(
        deriveSpecSlug("Update user's email validation (v2)"),
        'update-users-email-validation-v2'
      );
    });
  });

  describe('tracking-identifier-led slugs', () => {
    it('should lead with epic-story id when intent references "story 3.2"', () => {
      assert.equal(
        deriveSpecSlug('Story 3.2: digest delivery'),
        '3-2-digest-delivery'
      );
    });

    it('should handle "story 3-2" hyphen form', () => {
      assert.equal(
        deriveSpecSlug('Story 3-2 digest delivery'),
        '3-2-digest-delivery'
      );
    });

    it('should lead with gh-<N> when intent references a github issue', () => {
      assert.equal(
        deriveSpecSlug('Fix auth regression #47'),
        'gh-47-fix-auth-regression'
      );
    });

    it('should lead with gh-<N> when intent references "issue 47"', () => {
      assert.equal(
        deriveSpecSlug('Resolve issue 47 — broken login'),
        'gh-47-resolve-broken-login'
      );
    });
  });

  describe('conflict suffixing', () => {
    it('should return base slug when no conflict', () => {
      assert.equal(
        deriveSpecSlug('Fix login form', { existingSlugs: [] }),
        'fix-login-form'
      );
    });

    it('should append -2 when base slug exists', () => {
      assert.equal(
        deriveSpecSlug('Fix login form', { existingSlugs: ['fix-login-form'] }),
        'fix-login-form-2'
      );
    });

    it('should append -3 when base and -2 both exist', () => {
      assert.equal(
        deriveSpecSlug('Fix login form', {
          existingSlugs: ['fix-login-form', 'fix-login-form-2'],
        }),
        'fix-login-form-3'
      );
    });

    it('should skip gaps and take next available', () => {
      assert.equal(
        deriveSpecSlug('Fix login form', {
          existingSlugs: ['fix-login-form', 'fix-login-form-2', 'fix-login-form-3'],
        }),
        'fix-login-form-4'
      );
    });

    it('should apply conflict suffix to tracking-id-led slug', () => {
      assert.equal(
        deriveSpecSlug('Story 3.2: digest delivery', {
          existingSlugs: ['3-2-digest-delivery'],
        }),
        '3-2-digest-delivery-2'
      );
    });
  });

  describe('input guards', () => {
    it('should throw on empty intent', () => {
      assert.throws(() => deriveSpecSlug(''), /intent/i);
    });

    it('should throw on whitespace-only intent', () => {
      assert.throws(() => deriveSpecSlug('   '), /intent/i);
    });

    it('should throw on non-string intent', () => {
      assert.throws(() => deriveSpecSlug(null), /intent/i);
      assert.throws(() => deriveSpecSlug(42), /intent/i);
    });
  });
});
