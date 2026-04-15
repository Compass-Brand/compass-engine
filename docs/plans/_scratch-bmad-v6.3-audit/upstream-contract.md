# Upstream v6.3.0 Marketplace Contract — Audit Note

**Scope:** PluginResolver + marketplace.json schema + remote registry stack + custom-content removal.
**Plan ref:** `docs/plans/2026-04-15-bmad-v6.3-marketplace-distribution.md` Task 1.1.
**Upstream ref:** `BMAD-METHOD/` submodule (v6.3.0, tagged 2026-04-09). All line numbers cited below are against this submodule.

---

## 1. `marketplace.json` schema

**Path:** `BMAD-METHOD/.claude-plugin/marketplace.json` (75 lines, JSON).

**Top-level fields (verified present):**
- `name` (string) — marketplace identifier (`"bmad-method"`).
- `owner` (object) — `{ name }`.
- `description`, `license`, `homepage`, `repository` (strings).
- `keywords` (string[]).
- `plugins` (Plugin[]) — array of plugin descriptors.

**Plugin object shape:**
- `name` (string, required) — plugin identifier used by PluginResolver as fallback module code.
- `source` (string) — relative repo path (`"./"` for repo root).
- `description` (string).
- `version` (string) — semver; PluginResolver prefers this over module.yaml's `module_version` when both exist (see `plugin-resolver.js:87`).
- `author` (object) — `{ name }`.
- `skills` (string[]) — relative paths to skill directories (each containing `SKILL.md`).

**Upstream root currently ships 2 plugins:** `bmad-pro-skills` (11 core skills) and `bmad-method-lifecycle` (28 bmm skills across phases 1–4). See `marketplace.json:11-73`.

**Version propagation (PR #2233):** Strategy 1 walks up from skill parent to find `module.yaml`; if marketplace.json has `plugin.version`, it overrides any value in module.yaml. This was the fix — earlier versions reported the wrong version when the walk landed on a non-root module.yaml with stale version.

---

## 2. PluginResolver — 5 strategies

**Path:** `BMAD-METHOD/tools/installer/modules/plugin-resolver.js` (398 lines, CJS).

Invocation: `async resolve(repoPath, plugin) → ResolvedModule[]`.

**Hardening observed (`plugin-resolver.js:38-49`):** skill paths are normalized and constrained to `repoRoot + path.sep`. Path-traversal attempts (`..`, absolute paths) are filtered out. Non-existent paths silently dropped. Empty result → `[]`.

**Strategy cascade** (first-match wins; each returns `ResolvedModule[]` or `null`):

| # | Name | Trigger | Output | Line |
|---|------|---------|--------|------|
| 1 | **Root Module Files** | `module.yaml` + `module-help.csv` exist at the deepest common ancestor directory of all listed skills | 1 module; reuses existing CSV verbatim | `:71-98` |
| 2 | **Setup Skill** | One skill dir ends in `-setup` and has `assets/module.yaml` + `assets/module-help.csv` | 1 module from that skill's assets | `:105-138` |
| 3 | **Single Standalone** | Exactly 1 skill listed, with `assets/module.yaml` + `assets/module-help.csv` | 1 module | `:145-174` |
| 4 | **Multiple Standalone** | ≥2 skills, **ALL** with `assets/module.yaml` + `assets/module-help.csv` | N modules (one per skill); falls through to strategy 5 on partial match | `:182-220` |
| 5 | **Synthesize Fallback** | No module files anywhere | 1 synthesized module; CSV built from plugin metadata + SKILL.md frontmatter | `:228-268` |

**ResolvedModule shape (`:83-97`):**
```
{ code, name, version, description, strategy (1-5), pluginName,
  moduleYamlPath, moduleHelpCsvPath, skillPaths,
  synthesizedModuleYaml, synthesizedHelpCsv }
```
When strategy 1–4 wins: `moduleHelpCsvPath` is a real file path, `synthesized*` is `null`.
When strategy 5 wins: paths are `null`, `synthesized*` carries the generated content.

**Strategy 5 synthesized CSV header (`:341`)** — 13 columns:
```
module,skill,display-name,menu-code,description,action,args,phase,after,before,required,output-location,outputs
```
Row formula (`:349`): `{moduleName},{dirName},{displayName},{menuCode},{description},activate,,anytime,,,false,,`

Helpers of note:
- `_computeCommonParent()` (`:277-295`): deepest common path prefix by segment; single-path input returns its `dirname`.
- `_formatDisplayName()` (`:361-367`): strips `bmad-agent-` / `bmad-` prefix, title-cases remaining words.
- `_generateMenuCode()` (`:375-382`): first char of each segment, upper, max 3 chars (e.g., `code-coach` → `CC`).

**Which strategy our layout hits:** Our `dist/_bmad/{bmm,core,compass,bmad-builder}/` trees each have `module.yaml` + `module-help.csv` at the module root, and the listed skills live as descendants. If we shipped a `.claude-plugin/marketplace.json` declaring `source: "./"` and `skills: [./src/bmad/modules/.../<skill>, ...]`, **strategy 1 fires** — the common parent of all listed skills is the module root, and both files exist there. See `compass-pipeline.md` for the byte-level equivalence verdict.

---

## 3. Remote registry stack

Three modules in `BMAD-METHOD/tools/installer/modules/` share one HTTP client:

### 3.1 `registry-client.js` (55 lines)
- Plain `node:https` GET wrapped in a Promise.
- **Timeout:** 10 s default (`:10`), overridable per call.
- **Redirects:** follows exactly one 3xx (`:25-27`).
- Non-200 → rejects with `HTTP <code>`. No retries.
- `fetchYaml()` = `fetch()` + `yaml.parse()`.

### 3.2 `external-manager.js` — Official modules (PR #2228)
- URL (`:9`): `https://raw.githubusercontent.com/bmad-code-org/bmad-plugins-marketplace/main/registry/official.yaml`
- Try remote → on any failure, fall back to bundled `registry-fallback.yaml` (`:10`, `:46-56`).
- Used to enumerate first-party modules (CIS, bmad-builder, etc.) for installer selection.
- **Side effects on install:** clones each selected module repo to `~/.bmad/cache/external-modules/<code>/` and runs `npm install --omit=dev` (`:207-239`).

### 3.3 `community-manager.js` — Community modules (PR #2229)
- URLs (`:9-10`):
  - `https://raw.githubusercontent.com/bmad-code-org/bmad-plugins-marketplace/main/registry/community-index.yaml`
  - `https://raw.githubusercontent.com/bmad-code-org/bmad-plugins-marketplace/main/categories.yaml`
- On fetch failure: **returns empty `{ modules: [] }` / `{ categories: {} }`** — no bundled fallback for community (unlike official). Community browse simply shows nothing offline.
- Three-tier browse: featured → by-category → keyword-search (`:94-112`).
- **Security:** clones are pinned to `approved_sha`. If HEAD SHA doesn't match and the pinned SHA cannot be fetched, **install is refused** (`:243-264`).

### 3.4 `custom-module-manager.js` — User-provided sources (PR #2233, universal-source)
- `parseSource()` (`:27-130`) accepts:
  - Local paths: prefix `/`, `./`, `../`, `~`.
  - SSH URLs: `git@host:owner/repo[.git]` regex (`:61`).
  - HTTPS URLs: any host, `/tree/branch/subdir` / `/-/tree/branch/subdir` (GitLab) / `/blob/branch/subdir` / `/src/branch/subdir` (Gitea/Forgejo) — all map to `{cloneUrl, subdir}`.
- After parse → clone → read `.claude-plugin/marketplace.json` → hand each plugin to PluginResolver.
- This is the `--custom-source` flag's backend.

---

## 4. `--custom-content` removal (PR #2227)

**Evidence:** `BMAD-METHOD/CHANGELOG.md:7` (v6.3.0 breaking changes):
> Remove custom content installation feature; use marketplace-based plugin installation instead (#2227)

**Historical context from CHANGELOG:**
- `:249`: `--custom-content` was introduced as a CLI flag to "populate sources and selected files in module config".
- `:283`: v1.5.0-era addition listed among non-interactive CI/CD flags.
- `:1203-1214`, `:1280-1285`, `:1336-1365`: the feature let users sideload their own `custom-content/` tree into the installer, with an interactive search prompt and a docs page `custom-content-installation.md` (now removed).

**What it did:** At install time the installer would prompt for a "custom content" directory, scan for modules/workflows/agents, and write them into the installed `_bmad/` alongside official modules. Fully end-user facing; had nothing to do with bundle producers.

**What replaces it:** `--custom-source <source>` on `install` (`custom-module-manager.js` parses, clones, resolves via PluginResolver). The new path requires a Git-addressable or local marketplace.json source — no more ad-hoc file tree scanning.

**Collision with Compass `src/bmad/modules/custom/`?** See `compass-pipeline.md` §3. **Naming collision, not semantic.** Our `custom/` is a build-time overlay over `native/`; upstream's `--custom-content` was a runtime installer flag. The removal does not touch our pipeline.

---

## 5. Evidence trail

| Claim | Upstream evidence | PR |
|---|---|---|
| 5 resolver strategies, cascade order | `plugin-resolver.js:57-61` | (pre-#2233, refined by it) |
| Path-traversal guard | `plugin-resolver.js:43-45` | — |
| Version-walk fix | `plugin-resolver.js:87`, CHANGELOG:34 | #2233 |
| Custom-source universal parsing | `custom-module-manager.js:27-130` | #2233 |
| Remote registry fallback (official has bundled, community does not) | `external-manager.js:46-56`, `community-manager.js:32-46` | #2228, #2229 |
| Community pinning with SHA-refusal | `community-manager.js:243-264` | #2229 |
| `--custom-content` removed | `CHANGELOG.md:7` | #2227 |
| 13-col help CSV schema | `plugin-resolver.js:341` | (from #2120, v6.2.2) |

---

## 6. Flags for ADR

- **Network at install time is load-bearing upstream.** If Compass adopts any Option that invokes upstream installer end-to-end (e.g., Option 4), we inherit GitHub raw-URL availability as a build dependency. Our current `push.js` flow is fully offline.
- **Supply-chain surface:** `bmad-code-org/bmad-plugins-marketplace` (not Compass-controlled) would become a trust root the moment we call `external-manager` or `community-manager`. PluginResolver alone is pure and safe; the two managers are not.
- **Strategy 1 is the "happy path" for anyone already organized as module-root + skills-below.** Our tree already matches. This is why Option 3 (vendored PluginResolver) is low-risk mechanically — we'd invoke only the pure resolver, not the managers.
- **No `module.yaml` at marketplace root.** Upstream does not ship one; they rely on strategy 1 finding the files per-plugin at `src/core-skills/` and `src/bmm-skills/` respectively. We would do the same for our 4 modules.
