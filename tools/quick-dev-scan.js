/**
 * Quick-dev helper utilities.
 *
 * Ports slug-derivation rules from upstream BMAD
 * src/bmm-skills/4-implementation/bmad-quick-dev/step-01-clarify-and-route.md
 * so the compass-quick-spec workflow and native quick-dev stay in sync.
 */

const STORY_RE = /\bstory\s+(\d+)[.\-](\d+)\b/i;
const HASH_ISSUE_RE = /#(\d+)\b/;
const ISSUE_KW_RE = /\bissue\s+(\d+)\b/i;
const GH_KW_RE = /\bgh[-\s](\d+)\b/i;

const STOPWORDS_LEADING = new Set([
  'the',
  'a',
  'an',
  'and',
  'or',
  'of',
  'to',
  'for',
  'in',
  'on',
  'with',
]);

function slugifyRemainder(text) {
  return text
    .toLowerCase()
    .replace(/['\u2019`]+/g, '')
    .replace(/[^a-z0-9\s-]+/g, ' ')
    .trim()
    .replace(/[\s-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function dropLeadingStopwords(slug) {
  if (!slug) return slug;
  const parts = slug.split('-');
  while (parts.length > 1 && STOPWORDS_LEADING.has(parts[0])) {
    parts.shift();
  }
  return parts.join('-');
}

function extractTrackingId(intent) {
  const storyMatch = intent.match(STORY_RE);
  if (storyMatch) {
    return {
      prefix: `${storyMatch[1]}-${storyMatch[2]}`,
      stripped: intent.replace(storyMatch[0], ' '),
    };
  }

  const hashMatch = intent.match(HASH_ISSUE_RE);
  if (hashMatch) {
    return {
      prefix: `gh-${hashMatch[1]}`,
      stripped: intent.replace(hashMatch[0], ' '),
    };
  }

  const issueMatch = intent.match(ISSUE_KW_RE);
  if (issueMatch) {
    return {
      prefix: `gh-${issueMatch[1]}`,
      stripped: intent.replace(issueMatch[0], ' '),
    };
  }

  const ghMatch = intent.match(GH_KW_RE);
  if (ghMatch) {
    return {
      prefix: `gh-${ghMatch[1]}`,
      stripped: intent.replace(ghMatch[0], ' '),
    };
  }

  return { prefix: '', stripped: intent };
}

function applyConflictSuffix(baseSlug, existingSlugs) {
  const existing = new Set(existingSlugs);
  if (!existing.has(baseSlug)) return baseSlug;
  let n = 2;
  while (existing.has(`${baseSlug}-${n}`)) n++;
  return `${baseSlug}-${n}`;
}

/**
 * Derive a kebab-case slug from an intent string.
 *
 * Rules (mirroring upstream step-01-clarify-and-route):
 *   - If the intent references a tracking identifier (story X.Y, #N, issue N, gh-N),
 *     lead the slug with that identifier (e.g. `3-2-digest-delivery`, `gh-47-fix-auth`).
 *   - Otherwise, slugify the intent to plain kebab-case.
 *   - If `options.existingSlugs` contains a collision, append `-2`, `-3`, ...
 *
 * @param {string} intent - Free-form intent text (spec title / user request).
 * @param {{existingSlugs?: string[]}} [options]
 * @returns {string}
 */
export function deriveSpecSlug(intent, options = {}) {
  if (typeof intent !== 'string' || intent.trim() === '') {
    throw new Error('deriveSpecSlug: intent must be a non-empty string');
  }

  const { prefix, stripped } = extractTrackingId(intent);
  let remainder = slugifyRemainder(stripped);
  remainder = dropLeadingStopwords(remainder);

  let baseSlug;
  if (prefix && remainder) {
    baseSlug = `${prefix}-${remainder}`;
  } else if (prefix) {
    baseSlug = prefix;
  } else {
    baseSlug = remainder;
  }

  if (!baseSlug) {
    throw new Error('deriveSpecSlug: intent produced empty slug');
  }

  return applyConflictSuffix(baseSlug, options.existingSlugs ?? []);
}
