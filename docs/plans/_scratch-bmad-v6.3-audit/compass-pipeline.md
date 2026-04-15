# Compass Pipeline vs. Upstream PluginResolver — Audit Note

**Scope:** `tools/build.js`, `tools/push.js`, conflict with upstream `--custom-content` removal, manifest-equivalence with PluginResolver.
**Plan ref:** `docs/plans/2026-04-15-bmad-v6.3-marketplace-distribution.md` Task 1.2.
**Counterpart note:** `upstream-contract.md` (read first for PluginResolver strategy cascade + 13-col CSV schema).

---

## 1. `tools/build.js` (627 lines, ESM)

**Sources (read):**
- `src/bmad/modules/native/{bmm,core}-skills/` — upstream mirror (tracked against `BMAD-METHOD/src/{bmm,core}-skills/`).
- `src/bmad/modules/custom/{bmm,core,compass,bmad-builder}-skills/` — Compass overrides and Compass-only modules.
- `src/bmad/` (non-modules) — root assets copied as-is to `dist/_bmad/`.

**Merge rule (`build.js:265-273`):** `mergeModules(nativePath, customPath, outputPath)` — copy native first, then copy custom over it (custom wins via `copyDir` overwrite).

**Outputs (to `dist/_bmad/`):**
- `dist/_bmad/bmm/` — native bmm-skills + custom bmm-skills overlay.
- `dist/_bmad/core/` — native core-skills + custom core-skills overlay.
- `dist/_bmad/compass/` — custom compass-skills (no native counterpart).
- `dist/_bmad/bmad-builder/` — custom bmad-builder-skills (no native counterpart).

**Each `dist/_bmad/{module}/` contains** `module.yaml` + `module-help.csv` at the module root, with skill directories beneath. This layout is exactly what PluginResolver Strategy 1 expects.

**Three manifests generated at `dist/_bmad/_config/`:**

### 1.1 `bmad-help.csv` — via `generateBmadHelp()` (`:318-349`)
- Header (`:322`): `module,skill,display-name,menu-code,description,action,args,phase,after,before,required,output-location,outputs` — **13 columns, identical to upstream `_buildSynthesizedHelpCsv()` header (`plugin-resolver.js:341`).**
- Discovers modules by `readdir(BMAD_DIST)` excluding `_*` and `tools`.
- For each module, reads `dist/_bmad/{mod}/module-help.csv`, strips header, concatenates remaining rows.
- Module ordering = filesystem readdir order (non-deterministic across platforms, but stable on any given host).

### 1.2 `agent-manifest.csv` — via `generateAgentManifest()` (`:275-316`)
- Header (`:307`): `"id","name","displayName","title","icon","role","identity","communicationStyle","principles","module","path"` — 11 columns, all quoted.
- Walks the `dist/_bmad/` tree for files named `bmad-skill-manifest.yaml`, filters `type: agent`.
- Sorted by `(module, name)`.
- **No upstream counterpart.** PluginResolver has no concept of "agent metadata"; this schema is purely Compass-facing (used by our agent-orchestration skills, not by BMAD installer).

### 1.3 `skill-manifest.csv` — via `generateSkillManifest()` (`:351-395`)
- Header (`:386`): `name,type,description,module,path` — 5 columns, all quoted.
- Walks the `dist/_bmad/` tree for `SKILL.md` frontmatter.
- `type` = `agent` if `name` starts with `bmad-agent-` or equals `bmad-master`, else `workflow`.
- Consumed by `generateClientSkills()` (`:203-242`) to fan out `SKILL.md` stubs into `dist/.claude/skills/`, `dist/.opencode/skills/`, `dist/.codex/skills/` — one stub per skill per platform, renamed via `clientSkillName()`.
- **No upstream counterpart.** Upstream relies on each IDE's native skill loader; it does not generate a unified skill index.

**`clientSkillName()` rules (`:184-201`):**
- Compass-native (`bmad-compass-*`, `bmad-agent-compass-*`): passthrough (already prefixed).
- `bmad-builder` module short-name: `builder`.
- `bmad-agent-{name}` → `bmad-agent-{module}-{name}`.
- `bmad-master` → `bmad-core-master` (special case).
- Everything else: `bmad-{name}` → `bmad-{module}-{name}`.

**Validation floor (`:577`):** `validateBuild()` asserts `≥90` generated client skills in `dist/.claude/skills/`. Any churn that drops below 90 fails the build.

---

## 2. `tools/push.js` (692 lines, ESM)

**9 targets** (confirmed at `push.js:29-96`, matches plan's Context Summary):
`claude, codex, opencode, bmad, planning, documentation, github, root, beads`.

**`DEFAULT_TARGETS` (`:98-108`):** all 9 listed. Push replicates `dist/{distName}/` → `<projectRoot>/{destName}/`.

**Two sync modes:**
- **Full replace (default)** — used by `claude`, `bmad`, `beads`. Copies `dist/{distName}/` onto destination, preserving `localOnly` paths (`.claude/settings.local.json`, etc.) via backup/restore.
- **Managed (`syncStrategy: 'managed'`)** — used by `codex`, `opencode`, `planning`, `documentation`, `github`, `root`. Tracks delivered files in a per-target JSON manifest; on subsequent push, stale files (in previous manifest but not in current source) are removed. See `syncManagedTarget()` (`:387-431`).

**Manifest locations (`:370-376`):**
1. If `<projectPath>/.git` resolves to a gitdir (directory OR file with `gitdir:` pointer): manifest is written to `<gitdir>/<manifestName>`.
2. Else: `<projectPath>/.compass-engine/<manifestName>`.

**Manifest payload shape (`:343-352`):**
```json
{
  "version": 1,
  "generatedAt": "<ISO8601>",
  "files": ["sorted", "relative", "paths"]
}
```
**NOTE:** `version: 1` key already exists today. The plan's Phase 3 task referencing "schemaVersion" (line 64 of the plan) should either reuse the existing `version` field or justify introducing a parallel `schemaVersion`. Flag this for the ADR.

**Project discovery (`:16-27`, `:568-613`):** Walks `DEFAULT_PROJECT_CANDIDATES` relative to `ROOT` / workspace parent, adds any candidate whose `.git` exists. Order matches the plan's listing.

**Feature subsetting:** `github` and `root` targets support per-feature selection via `--github-features` / `--root-features` CLI flags, mapped through `GITHUB_FEATURE_GROUPS` and `ROOT_FEATURE_GROUPS` tables (`:110-145`).

**Path-escape guard (`:378-385`):** `resolveWithinProject()` throws if a relative path resolves outside project root — defends against manifest tampering.

---

## 3. Conflict diff: `src/bmad/modules/custom/` vs. upstream `--custom-content`

**Verdict: naming collision, not semantic collision.**

| Axis | Compass `src/bmad/modules/custom/` | Upstream `--custom-content` (pre-v6.3, now removed) |
|---|---|---|
| Time domain | **Build-time** (merged into `dist/_bmad/` before anything ships) | **Install-time** (installer prompts user for a dir, copies its contents into their `_bmad/`) |
| Producer | Compass Engine maintainers | End-user of upstream installer |
| Consumer | Downstream Compass projects via `push.js` | Upstream installer → user's project |
| Mechanism | `mergeModules()` overlay; custom wins | Installer directory scan + copy |
| Schema | YAML modules identical to native | Ad-hoc |
| Replacement in v6.3 | N/A — unchanged | `--custom-source <url\|path>` via `custom-module-manager.js` → PluginResolver |

**Impact on our pipeline: none.** `push.js` never invokes the upstream installer; we ship pre-built `dist/_bmad/` trees. The removed flag doesn't appear in our code.

**Indirect impact on downstream projects:** If a consumer of `push.js` also wants to sideload their own plugins via the new `bmad install --custom-source`, they currently can't — we don't ship the installer binary, only the generated `_bmad/` tree. Noted in the plan's Context Summary and remains accurate.

---

## 4. Manifest equivalence (REQUIRED DELIVERABLE)

**Question per plan Task 1.2:** do our three generated CSVs match what PluginResolver Strategy 1 would produce against a hypothetical `.claude-plugin/marketplace.json`?

### 4.1 `bmad-help.csv` vs. PluginResolver output

**Schema equivalence: YES.** Both use the identical 13-column header.

**Content source: IDENTICAL.** PluginResolver Strategy 1 reads the existing `{common_parent}/module-help.csv` verbatim (no transformation). Our `generateBmadHelp()` reads the same files (`dist/_bmad/{mod}/module-help.csv`) verbatim. Strategy 5 synthesis is not in play — our layout triggers Strategy 1.

**Byte-level equivalence: partial, with known divergences.**

| Divergence | Ours | PluginResolver Strategy 1 (hypothetical invocation) | Notes |
|---|---|---|---|
| Header presence | Single header line prepended | Header per `module-help.csv` (one per module) | Caller of PluginResolver must dedupe; we assume exactly one final header. Equivalent if caller concats-then-dedupes. |
| Row order across modules | `readdir(dist/_bmad)` order | Order of `marketplace.json.plugins[]` iteration by caller | Deterministic in both but different. Post-sort on `(module, menu-code)` would unify. |
| Row order within module | Preserves file order from `module-help.csv` | Same (verbatim read) | Identical. |
| Row content | Verbatim from `module-help.csv` | Verbatim from same file | Identical (same input). |

### 4.2 `agent-manifest.csv` vs. PluginResolver output

**NO EQUIVALENCE.** PluginResolver emits no agent manifest. This 11-column schema is Compass-specific (richer metadata: `icon, role, identity, communicationStyle, principles`). It would have to be retained regardless of Option 2/3/4.

### 4.3 `skill-manifest.csv` vs. PluginResolver output

**NO EQUIVALENCE.** PluginResolver emits no unified skill index. This 5-column schema is a Compass concept feeding `generateClientSkills()`. PluginResolver's `ResolvedModule[]` could be reshaped into something similar, but the `agent|workflow` classification, `bmad-agent-*` → agent rule, and use-as-fanout-spine semantics are ours.

### 4.4 Phase 3 gating implication

**Equivalence Verdict: partial**

- `bmad-help.csv` is genuinely replaceable by a PluginResolver-strategy-1 loop (Option 3 feasible for this file).
- `agent-manifest.csv` and `skill-manifest.csv` cannot be replaced — they must remain Compass-generated.
- Therefore Phase 3 Option 3 scope is **one CSV, not three**. Any ADR that claims "swap our generators for PluginResolver" must narrow to `generateBmadHelp` only and explicitly call out the other two as retained.

### 4.5 Diff summary

**File-by-file:**

```
bmad-help.csv:          schema=match  content=match  order=differs-but-reconcilable
agent-manifest.csv:     schema=NONE   content=NONE   (Compass-only)
skill-manifest.csv:     schema=NONE   content=NONE   (Compass-only)
```

---

## 5. Equivalence Verdict

**Equivalence Verdict: partial**

Rationale: 1 of 3 generated manifests (`bmad-help.csv`) is byte-reconcilable with PluginResolver Strategy 1 output after caller-side ordering normalization. The other 2 manifests (`agent-manifest.csv`, `skill-manifest.csv`) have no upstream counterpart and are structurally Compass-specific. This permits Phase 3 Option 3 only if scoped to `generateBmadHelp()`; swapping `generateAgentManifest()` or `generateSkillManifest()` is out of scope for that option unless the ADR explicitly accepts lossy substitution.

---

## 6. Surprises / callouts for team lead

1. **`version: 1` already on managed manifests.** `push.js:347` writes `version: 1` today. The plan (line 64) describes adding `schemaVersion: 2` as if starting from scratch — the ADR should pick one key name and migrate. Recommend keeping `version` and bumping to `2` rather than introducing `schemaVersion` as a parallel field.

2. **Plan line counts off by 1** (`build.js: 628 → actual 627`, `push.js: 693 → actual 692`). Cosmetic only.

3. **Upstream marketplace.json uses 2 plugins, not 4.** `bmad-pro-skills` = core-skills subset (11/11 — all core skills listed). `bmad-method-lifecycle` = all 28 bmm-skills. If we ship our own marketplace.json under Option 2, declaring `bmm`, `core`, `compass`, `bmad-builder` as 4 separate plugins diverges from upstream's 2-plugin model but aligns 1:1 with our `dist/_bmad/` layout and is the cleanest Strategy-1 fit.

4. **PluginResolver is pure and safe to vendor** (no network, no fs writes outside its args, defensive path-traversal guard). The risk the plan flags about `external-manager`/`community-manager` is real, but the resolver itself is a good vendoring candidate with only `node:fs`, `node:path`, `yaml` as transitive deps.

5. **`custom-module-manager.js`'s `parseSource()` is 617 lines total** but the parse function alone is ~100 lines (`:27-130`) and handles 3 URL shapes + deep-path extraction for GitHub/GitLab/Gitea/Forgejo. If Option 4 were ever chosen, this is the piece we'd need to understand thoroughly.
