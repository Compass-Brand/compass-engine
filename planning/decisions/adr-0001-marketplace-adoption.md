# ADR-0001: Marketplace Adoption Posture for compass-engine

**Status:** Accepted
**Date:** 2026-04-15
**Beads:** `bmad-engine-lkja` (Phase 1 audit), `bmad-engine-uscr` (Phase 3 implementation, gated on this ADR)
**Plan:** `docs/plans/2026-04-15-bmad-v6.3-marketplace-distribution.md` (branch `docs/bmad-v6.3-alignment-plans`)

---

## Context

BMAD v6.3.0 consolidates distribution around a marketplace model: `.claude-plugin/marketplace.json` describes plugins, `BMAD-METHOD/tools/installer/modules/plugin-resolver.js` resolves them into `ResolvedModule[]` via a five-strategy cascade, and `external-manager.js` / `community-manager.js` fetch registries over HTTPS from `bmad-code-org/bmad-plugins-marketplace` (PR #2228, PR #2229). PR #2227 removed the legacy `--custom-content` installer flag, replaced by `--custom-source <url|path>` parsed by `custom-module-manager.js` (PR #2233).

compass-engine does not use any of this today. `tools/build.js` merges `src/bmad/modules/native/` with `src/bmad/modules/custom/` into `dist/_bmad/{bmm,core,compass,bmad-builder}/` and generates three manifests (`bmad-help.csv`, `agent-manifest.csv`, `skill-manifest.csv`). `tools/push.js` replicates `dist/*` into downstream Compass projects over nine targets. No network calls; no installer invoked.

Phase 1 of the plan produced two audit notes (branch `docs/bmad-v6.3-marketplace-audit`):

- `docs/plans/_scratch-bmad-v6.3-audit/upstream-contract.md` — PluginResolver strategies, marketplace.json schema, registry stack, `--custom-content` history.
- `docs/plans/_scratch-bmad-v6.3-audit/compass-pipeline.md` — our build/push mechanics, conflict diff, and manifest-equivalence analysis.

**Equivalence Verdict from Phase 1: PARTIAL.** `bmad-help.csv` maps cleanly onto PluginResolver Strategy 1 (same 13-column schema, same source files read verbatim). `agent-manifest.csv` (11 cols: `id, name, displayName, title, icon, role, identity, communicationStyle, principles, module, path`) and `skill-manifest.csv` (5 cols feeding `generateClientSkills()` fan-out) have **no upstream counterpart** and cannot be produced by PluginResolver without lossy substitution.

**Path-divergence flags surfaced during audit:**

- `push.js:347` already writes `version: 1` on managed sync manifests — the key `version` is the existing, load-bearing field; the plan's "`schemaVersion: 2`" should reuse it (bump `version` to `2`), not introduce a parallel field.
- Upstream `BMAD-METHOD/.claude-plugin/marketplace.json` declares **2 plugins** (`bmad-pro-skills`, `bmad-method-lifecycle`). Our `dist/_bmad/` layout has **4 module roots** (`bmm`, `core`, `compass`, `bmad-builder`), each with its own `module.yaml` + `module-help.csv` at the module root. A 4-plugin marketplace.json is the cleanest Strategy-1 fit for our tree but intentionally diverges from upstream's 2-plugin grouping.
- `plugin-resolver.js` itself is pure, defensively coded (path-traversal guard at `:43-45`), and has no network I/O — safe to vendor. Network and supply-chain risk live entirely in `external-manager.js` / `community-manager.js`, which reach `bmad-code-org/bmad-plugins-marketplace` (a repo outside Compass control).

---

## Options considered

### Option 1 — Status quo

Keep `tools/build.js` + `tools/push.js` as-is. Ship no `.claude-plugin/marketplace.json`. No PluginResolver imports.

- **Pros:** Zero risk. Works today. Fully offline builds preserved.
- **Cons:** External consumers have no way to consume compass-engine via upstream tooling (`bmad install --custom-source <url>` cannot find a marketplace manifest). Our `generateBmadHelp()` duplicates logic PluginResolver Strategy 1 already implements upstream.

### Option 2 — Ship `marketplace.json` alongside existing build

Add `.claude-plugin/marketplace.json` at repo root covering 4 plugins (`bmm`, `core`, `compass`, `bmad-builder`). Generate it during `build()`, mirror to `dist/`, ship via `push.js`. Build and manifest logic otherwise unchanged.

- **Pros:** Enables external installs via `bmad install --custom-source <compass-engine-repo-url>`. Low risk — additive file, existing consumers unaffected. No coupling to upstream installer code.
- **Cons:** Duplicates manifest information (marketplace.json plus our three CSVs). Doesn't reduce our bespoke generator code.

### Option 3 — Internal PluginResolver shim (narrowed)

Vendor `plugin-resolver.js` into `tools/vendor/` and delegate manifest generation to it **for `generateBmadHelp()` only**. `generateAgentManifest()` and `generateSkillManifest()` stay Compass-generated (they have no upstream equivalent per the Phase 1 Equivalence Verdict).

- **Pros:** One manifest (the one we can legitimately replace) stops drifting from upstream semantics; upstream bug fixes (e.g., #2233 version walk) flow in on the next vendor re-sync. PluginResolver is pure code — no network.
- **Cons:** Adds a vendoring workflow and a transitive-purity invariant (must NOT pull in `external-manager.js` / `community-manager.js`). Byte-stability across CSV row ordering must be preserved because `validateBuild()` asserts ≥90 fan-out skills downstream of manifest output.

### Option 4 — Full adoption

Deprecate `push.js`. Publish compass-engine to a hosted marketplace; downstream Compass projects install via `bmad install` against that marketplace.

- **Pros:** Maximum upstream alignment. One canonical distribution channel.
- **Cons:** Catastrophic downstream blast radius. Every consumer repo (`compass-forge`, `compass-services`, `compass-initiative`, `compass-modules`, `compass-brand-infrastructure`, `compass-brand-setup`, `mcps`, nested subprojects) must install the BMAD installer as a new dependency and change its sync procedure. Introduces network dependency on a GitHub repo we don't control (supply-chain surface). Rejected as disproportionate to the problem.

### Option 5 — Combined 2 + 3 (narrowed)

Do Option 2 (ship `marketplace.json`) **and** Option 3 narrowed to `generateBmadHelp()` only. The two changes are orthogonal: Option 2 opens external consumption, Option 3 reduces our internal duplication for the single manifest where equivalence is real. They reinforce each other — the shipped `marketplace.json` becomes the test fixture that validates the PluginResolver shim's output.

- **Pros:** Unlocks external installs AND removes duplicated manifest-generation logic for the one file where it's justified. Respects the Phase 1 Equivalence Verdict (narrowed scope). Preserves Compass-specific manifests that have no upstream counterpart.
- **Cons:** Two workstreams instead of one. Requires the vendor-purity test and the cross-validation integration test to prevent regressions.

---

## Decision

**Adopt Option 5, narrowed to `generateBmadHelp()` for the PluginResolver shim.**

Rationale, grounded in Phase 1 evidence:

1. **Option 2 is a strict additive win.** Shipping `marketplace.json` gives external consumers a supported install path (#2233 `--custom-source`) with zero impact on current downstream push consumers. Our `dist/_bmad/{mod}/module.yaml` + `module-help.csv` already sit at the skills' common parent, so PluginResolver Strategy 1 resolves our layout without structural changes (`upstream-contract.md` §2 Strategy 1 row).
2. **Option 3 must be narrowed.** The Phase 1 Equivalence Verdict is PARTIAL: only `bmad-help.csv` shares PluginResolver's 13-column schema and reads the same underlying `module-help.csv` files verbatim (`compass-pipeline.md` §4.1). `agent-manifest.csv` and `skill-manifest.csv` have no upstream equivalent and must stay Compass-generated (`compass-pipeline.md` §4.2, §4.3). Any ADR that claimed "swap all three manifests for PluginResolver" would be unsupported by the audit.
3. **Option 4 is rejected.** The downstream blast radius — every Compass repo must install and run an installer, against a marketplace we don't host — is disproportionate to the problem we are solving (duplicated manifest-generation logic and absent external consumption path).
4. **Supply-chain constraint is non-negotiable.** Option 5 vendors `plugin-resolver.js` only. It MUST NOT import `external-manager.js` or `community-manager.js`, which fetch registries from `bmad-code-org/bmad-plugins-marketplace` (a GitHub repo outside Compass control). Phase 3 operationalizes this as `test/no-network-managers.test.js` — a build-time invariant, not advisory text.

Phase 3 task ordering follows the plan: Option 2 tasks 3.2.1–3.2.4 (generate + commit `marketplace.json`), then Option 3 tasks 3.3.1–3.3.5 narrowed to `generateBmadHelp()` (using the just-committed marketplace.json as the integration-test fixture), then Option 2 tasks 3.2.5–3.2.6 (push.js wiring + docs).

---

## Consequences

**What changes:**

- Repo root gains `.claude-plugin/marketplace.json`, generated by `tools/build.js` (new helper, e.g. `generateMarketplaceJson()`) and committed.
- `tools/vendor/plugin-resolver.js` appears, sourced from `BMAD-METHOD/tools/installer/modules/plugin-resolver.js` with transitive imports pruned to Node builtins + `yaml`.
- `generateBmadHelp()` signature is preserved; its body delegates to the vendored PluginResolver per module. Output is byte-stable against the pre-change CSV (fixture regression test is an acceptance gate).
- `tools/push.js` gains a new managed target `claude-plugin` so `marketplace.json` ships to downstream consumers.
- New tests: `test/marketplace-json.test.js`, `test/plugin-resolver-integration.test.js`, `test/plugin-resolver-manifest.test.js`, `test/marketplace-roundtrip.test.js`, `test/no-network-managers.test.js`.

**What does NOT change:**

- `tools/push.js` core flow (nine targets, two sync modes, `localOnly` backup/restore, project discovery) is unchanged.
- `generateAgentManifest()` and `generateSkillManifest()` remain Compass-generated, unchanged in shape.
- `dist/_bmad/` layout is unchanged. `validateBuild()`'s ≥90-client-skill floor still holds.
- No network calls are added to the build path. Builds remain fully offline.
- Downstream Compass consumers of `push.js` see no behavioral change — they continue to receive the same `dist/*` tree, plus (transparently) one new file: `.claude-plugin/marketplace.json`.

**Downstream impact:**

- **Current consumers:** none. `push.js` replicates as before; the new `claude-plugin` target is additive.
- **New external consumers:** can install compass-engine plugins via `bmad install --custom-source <compass-engine-repo-url>`, which upstream `custom-module-manager.js` clones and resolves against our shipped `marketplace.json`.

**Upstream alignment posture:**

- compass-engine follows upstream schema (marketplace.json), vendors only the pure resolver, and intentionally diverges on plugin grouping (4 plugins vs. upstream's 2) to match our module layout 1:1.
- Vendor re-sync is a conscious operation on each BMAD-METHOD submodule bump, not automatic, so upstream drift surfaces as a reviewable diff.

---

## Risks

1. **Supply-chain boundary must be CI-enforced.** `external-manager.js` and `community-manager.js` reach `bmad-code-org/bmad-plugins-marketplace` — a GitHub repo outside Compass control. If compromised, attacker-controlled plugin metadata would flow into installers that consult it. PluginResolver itself is pure (`plugin-resolver.js` has no network I/O, defensively guards path traversal at `:43-45`, depends only on `node:fs`, `node:path`, `yaml`). **Phase 3 MUST add `test/no-network-managers.test.js`** that walks `tools/` and `src/`, parses imports, and fails if any file references `external-manager.js` or `community-manager.js` — including transitive imports reachable from `tools/vendor/`. This converts the constraint from text into a build-time invariant.

2. **Plugin grouping divergence is intentional and documented.** Upstream's `.claude-plugin/marketplace.json` ships 2 plugins (`bmad-pro-skills`, `bmad-method-lifecycle`). Our marketplace.json will ship 4 (`bmm`, `core`, `compass`, `bmad-builder`) to match our `dist/_bmad/` module roots 1:1 — the cleanest Strategy-1 fit per `upstream-contract.md` §2 ("our tree already matches"). This divergence is deliberate: our 4-plugin grouping aligns with how we build and push, not with how upstream curates its own catalog. External consumers see 4 installable units instead of 2; each resolves via Strategy 1 against its own module root.

3. **Schema-version field is `version`, not `schemaVersion`.** `push.js:347` already writes `version: 1` on managed sync-manifests. The plan's references to "`schemaVersion: 2`" (plan line 64) will be implemented as **`version: 2`** to reuse the existing key. Phase 3 must:
   - Treat absent `version` or `version: 1` as pre-v6.3 and rewrite the manifest from scratch without losing tracked-file lineage.
   - Add a unit test asserting (a) v1 manifests are detected and rewritten, (b) v2 manifests round-trip stable.
   - Not introduce a parallel `schemaVersion` field.

4. **Manifest byte-stability is an acceptance gate for Option 3.** `skill-manifest.csv` feeds `generateClientSkills()` which produces the ≥90-skill fan-out asserted by `validateBuild()`. `bmad-help.csv` row ordering differs between our `readdir()`-order and PluginResolver's `plugins[]`-order iteration. Phase 3 must sort on `(module, menu-code)` post-resolution to guarantee byte-stability against the pre-change fixture. Zero diff in `dist/_bmad/_config/*.csv` is the regression bar.

5. **Submodule pinning.** Adopting Option 5 assumes `BMAD-METHOD` is pinned to ≥ v6.3.0 (for PR #2233's version-walk fix). A CI check should fail downgrade attempts.

---

## Backwards-compatibility plan

- **Existing Compass projects keep working.** `push.js` continues to replicate `dist/*` to downstream. The new `.claude-plugin/marketplace.json` ships as an additive file via the new `claude-plugin` managed target. No consumer-side action required.
- **Sync-manifest migration.** The `version: 1` → `version: 2` bump (Risk #3) is handled transparently by `push.js`: on first contact with a pre-v6.3 manifest, rewrite from scratch. No consumer must delete state or re-bootstrap.
- **New external consumers** can install via `bmad install --custom-source <compass-engine-repo-url>` once this ADR's Phase 3 work lands. Documentation update lives in `docs/BMAD-integration.md` (Phase 3 Task 3.2.6).
- **`tools/push.js` flow is unchanged** for all nine existing targets. Option 5 does not deprecate the push-based distribution path; it adds a parallel external-install path.
- **Option 4 deferral.** If full adoption is revisited later, it will be a new ADR superseding this one, with a separate beads issue and its own downstream-migration plan. This ADR explicitly defers it.

---

## References

**Phase 1 audit notes** (branch `docs/bmad-v6.3-marketplace-audit`):

- `docs/plans/_scratch-bmad-v6.3-audit/upstream-contract.md` — PluginResolver 5-strategy cascade, marketplace.json schema, registry stack, `--custom-content` removal history.
- `docs/plans/_scratch-bmad-v6.3-audit/compass-pipeline.md` — `tools/build.js` + `tools/push.js` mechanics, conflict diff, manifest-equivalence verdict (PARTIAL).

**Plan:**

- `docs/plans/2026-04-15-bmad-v6.3-marketplace-distribution.md` (branch `docs/bmad-v6.3-alignment-plans`).

**Upstream code referenced:**

- `BMAD-METHOD/tools/installer/modules/plugin-resolver.js` — strategy cascade `:57-268`; path-traversal guard `:43-45`; synthesized CSV header `:341`; version walk `:87`.
- `BMAD-METHOD/tools/installer/modules/external-manager.js` — network-dependent; disallowed import.
- `BMAD-METHOD/tools/installer/modules/community-manager.js` — network-dependent; disallowed import.
- `BMAD-METHOD/tools/installer/modules/custom-module-manager.js` — `parseSource()` for `--custom-source` flag (PR #2233).
- `BMAD-METHOD/.claude-plugin/marketplace.json` — schema reference (2-plugin example).
- `BMAD-METHOD/CHANGELOG.md:7` — `--custom-content` removed (PR #2227).

**Compass code referenced:**

- `tools/build.js` — `generateBmadHelp()` `:318-349`; `generateAgentManifest()` `:275-316`; `generateSkillManifest()` `:351-395`; `generateClientSkills()` `:203-242`; `validateBuild()` `:577`.
- `tools/push.js` — 9 targets `:29-96`; managed manifest payload `:343-352`; `version: 1` write `:347`; manifest locations `:370-376`; path-escape guard `:378-385`.

**Upstream PRs:**

- #2227 — remove `--custom-content`; use marketplace-based plugin installation.
- #2228 — official-registry three-tier browse with bundled fallback.
- #2229 — community-registry browse with SHA-pinned installs.
- #2233 — `--custom-source` universal source parser; PluginResolver version-walk fix.

**Beads:**

- `bmad-engine-lkja` — Phase 1 audit (to be closed when this PR opens).
- `bmad-engine-uscr` — Phase 3 implementation, gated on this ADR's merge.
