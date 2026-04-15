/**
 * Quick-dev helper utilities.
 *
 * Ports slug-derivation rules from upstream BMAD
 * src/bmm-skills/4-implementation/bmad-quick-dev/step-01-clarify-and-route.md
 * so the compass-quick-spec workflow and native quick-dev stay in sync.
 *
 * Also exports epic-inference helpers consumed by our custom
 * step-01-mode-detection.md (A.1 Epic inference).
 */

import { existsSync, statSync, readdirSync, readFileSync } from 'node:fs';
import { join, basename as pathBasename } from 'node:path';

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

function toPositiveInt(value) {
  if (typeof value === 'number' && Number.isInteger(value) && value > 0) {
    return value;
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (/^\d+$/.test(trimmed)) {
      const n = Number.parseInt(trimmed, 10);
      return n > 0 ? n : null;
    }
  }
  return null;
}

function parseStoryEpic(storyValue) {
  if (storyValue == null) return null;
  const str = String(storyValue).trim();
  const match = str.match(/^(\d+)[.\-](\d+)/);
  if (!match) return null;
  return toPositiveInt(match[1]);
}

function parseFilenameEpic(filename) {
  if (typeof filename !== 'string' || filename === '') return null;
  const basename = filename.split(/[\\/]/).pop();
  if (!basename) return null;
  const stripped = basename.replace(/^spec-/i, '');
  const match = stripped.match(/^(\d+)-/);
  if (!match) return null;
  return toPositiveInt(match[1]);
}

/**
 * Derive the epic number for a quick-dev tech-spec.
 *
 * Resolution order (first positive integer wins):
 *   1. frontmatter `epic:` field
 *   2. frontmatter `story:` field parsed as `E.S` (or `E-S`)
 *   3. filename leading-digit slug (`spec-3-2-x.md` → 3, `3-2-foo.md` → 3)
 *
 * @param {object|null|undefined} specFrontmatter
 * @param {string|null|undefined} filename
 * @returns {number|null}
 */
export function extractEpicNum(specFrontmatter, filename) {
  const fm = specFrontmatter ?? {};

  const fromEpic = toPositiveInt(fm.epic);
  if (fromEpic !== null) return fromEpic;

  const fromStory = parseStoryEpic(fm.story);
  if (fromStory !== null) return fromStory;

  const fromFilename = parseFilenameEpic(filename);
  if (fromFilename !== null) return fromFilename;

  return null;
}

/**
 * Check whether a compiled epic context file exists in the implementation
 * artifacts directory. The caller (the step-01 workflow) is responsible for
 * any freshness comparison against planning-doc mtimes; this helper answers
 * only "does the cached file exist?".
 *
 * @param {string} implArtifactsDir - absolute path to the impl artifacts dir
 * @param {number} epicNum - positive integer epic number
 * @returns {boolean}
 */
export function epicContextIsCached(implArtifactsDir, epicNum) {
  if (typeof implArtifactsDir !== 'string' || implArtifactsDir === '') {
    return false;
  }
  const n = toPositiveInt(epicNum);
  if (n === null) return false;

  const candidate = join(implArtifactsDir, `epic-${n}-context.md`);
  try {
    if (!existsSync(candidate)) return false;
    return statSync(candidate).isFile();
  } catch {
    return false;
  }
}

const CONTINUITY_SECTION_HEADINGS = [
  '## Code Map',
  '## Design Notes',
  '## Spec Change Log',
  '## Tasks',
];

function parseFrontmatter(raw) {
  if (!raw.startsWith('---')) return {};
  const end = raw.indexOf('\n---', 3);
  if (end === -1) return {};
  const block = raw.slice(3, end).trim();
  const fm = {};
  for (const line of block.split('\n')) {
    const match = line.match(/^([A-Za-z0-9_-]+)\s*:\s*(.+?)\s*$/);
    if (!match) continue;
    const key = match[1];
    let value = match[2];
    if (
      (value.startsWith("'") && value.endsWith("'")) ||
      (value.startsWith('"') && value.endsWith('"'))
    ) {
      value = value.slice(1, -1);
    }
    fm[key] = value;
  }
  return fm;
}

function parseStoryNumber(fm, filename) {
  if (fm.story != null) {
    const match = String(fm.story).match(/^(\d+)[.\-](\d+)/);
    if (match) {
      const n = toPositiveInt(match[2]);
      if (n !== null) return n;
    }
  }
  const base = pathBasename(filename).replace(/^spec-/i, '');
  const match = base.match(/^\d+-(\d+)-/);
  if (match) return toPositiveInt(match[1]);
  return null;
}

function extractSectionBody(raw, heading) {
  const idx = raw.indexOf(`\n${heading}`);
  const start = idx === -1 && raw.startsWith(heading) ? 0 : idx;
  if (start === -1) return '';
  const bodyStart = raw.indexOf('\n', start === 0 ? heading.length : start + 1);
  if (bodyStart === -1) return '';
  const rest = raw.slice(bodyStart + 1);
  const nextIdx = rest.search(/\n## /);
  const body = nextIdx === -1 ? rest : rest.slice(0, nextIdx);
  return body.replace(/^\n+|\n+$/g, '');
}

function assembleContinuityContext(specPath, raw, status) {
  const sections = CONTINUITY_SECTION_HEADINGS.map((heading) => {
    const body = extractSectionBody(raw, heading);
    return `${heading}\n\n${body}`.replace(/\n+$/, '');
  });
  const header = `> Continuity from ${pathBasename(specPath)} (status: ${status})`;
  return [header, ...sections].join('\n\n') + '\n';
}

/**
 * Find the most recent `status: done` sibling spec for a given epic/story,
 * restricted to lower story numbers within the same epic. Returns the chosen
 * spec path, its parsed story number, and an assembled `continuity_context`
 * string containing the Code Map, Design Notes, Spec Change Log, and Tasks
 * sections prefixed with a provenance header.
 *
 * @param {string} implArtifactsDir - absolute path to the impl artifacts dir
 * @param {number} epicNum - current epic number
 * @param {number} storyNum - current story number (exclusive upper bound)
 * @returns {{path: string, storyNum: number, continuityContext: string}|null}
 */
export function findPreviousStoryDone(implArtifactsDir, epicNum, storyNum) {
  if (typeof implArtifactsDir !== 'string' || implArtifactsDir === '') {
    return null;
  }
  const epic = toPositiveInt(epicNum);
  const currentStory = toPositiveInt(storyNum);
  if (epic === null || currentStory === null) return null;

  let entries;
  try {
    entries = readdirSync(implArtifactsDir);
  } catch {
    return null;
  }

  const prefix = `spec-${epic}-`;
  const candidates = [];
  for (const entry of entries) {
    if (!entry.startsWith(prefix) || !entry.endsWith('.md')) continue;
    const fullPath = join(implArtifactsDir, entry);
    let raw;
    try {
      raw = readFileSync(fullPath, 'utf8');
    } catch {
      continue;
    }
    const fm = parseFrontmatter(raw);
    if (fm.status !== 'done') continue;
    const fmEpic = extractEpicNum(fm, entry);
    if (fmEpic !== epic) continue;
    const story = parseStoryNumber(fm, entry);
    if (story === null || story >= currentStory) continue;
    candidates.push({ path: fullPath, storyNum: story, raw });
  }

  if (candidates.length === 0) return null;

  candidates.sort((a, b) => b.storyNum - a.storyNum);
  const chosen = candidates[0];
  return {
    path: chosen.path,
    storyNum: chosen.storyNum,
    continuityContext: assembleContinuityContext(chosen.path, chosen.raw, 'done'),
  };
}
