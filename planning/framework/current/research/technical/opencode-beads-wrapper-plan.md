# OpenCode Beads Wrapper Plan

Status: draft
Owner:
Last Updated: 2026-03-24
Phase ID:
Parent Issue: `bmad-engine-g4u`
Related Pilot Issue: `bmad-engine-reg`

## Objective

- Define exactly how Compass should wrap `joshuadavidthomas/opencode-beads`.
- Keep `bd` as the task system of record while making OpenCode session behavior Compass-aware.
- Specify how the wrapper is implemented in `compass-engine` and how it is installed into downstream repos through the normal `build` and `push` flow.

## Ground Truth

### Official OpenCode Plugin Model

From the official OpenCode docs:

- Local plugins are auto-loaded from `.opencode/plugins/`.
- npm plugins can be declared in `opencode.json`, but local plugins do not need a config entry.
- Local plugins can depend on npm packages by adding `.opencode/package.json`; OpenCode runs `bun install` at startup.
- A plugin is a JS/TS module that exports one or more plugin functions.
- Plugins can register hooks and custom tools, and they receive `project`, `directory`, `worktree`, `client`, and Bun `$`.
- Skills can be loaded from `.opencode/skills/<name>/SKILL.md` and discovered on demand via the native `skill` tool.

Practical implication for Compass:

- We should ship a local plugin through the `.opencode/` bundle instead of depending on downstream repos to install an npm package manually.
- We should use a local `.opencode/package.json` only if the Compass plugin actually imports external packages at runtime.

### Upstream `opencode-beads` Shape

The upstream plugin is intentionally thin:

- `src/plugin.ts`
  - injects `bd prime` context into sessions
  - reinjects on compaction
  - merges vendored commands and an autonomous task agent through a `config` hook
- `src/vendor.ts`
  - loads vendored command markdown and task-agent prompt
  - defines the beads CLI guidance injected into the session
- `vendor/commands/*.md`
  - one command definition per beads CLI action
- `vendor/agents/task-agent.md`
  - autonomous task-completion subagent prompt

The upstream author explicitly recommends forking or copying for customization because the surface area is small.

## Compass Wrapper Boundary

### What We Keep From Upstream

- The overall plugin architecture:
  - context injection
  - compaction reinjection
  - command registration
  - task agent registration
- The vendored command markdown model
- The thin, dependency-light runtime shape

### What We Change For Compass

- Replace generic beads guidance with Compass-aware guidance:
  - `bd` is required
  - `TodoWrite`-style tracking is not authoritative
  - session close protocol must remain aligned with repo policy
- Restrict or document command/agent behavior so it does not compete with BMAD authority
- Add explicit no-op guards for:
  - `bd` missing
  - repo not initialized for beads
  - contexts where injection should not happen
- Keep the wrapper Compass-owned in source instead of pulling the npm package downstream
- Align the task-agent wording with Compass conventions and repository policy

### What We Do Not Change In Pilot 1

- We do not redesign beads itself.
- We do not invent a new tracking abstraction over `bd`.
- We do not replace the upstream command set with a large custom tool layer.
- We do not add orchestration or memory features to this wrapper.

## Exact Source Layout

The main packaging constraint is:

- OpenCode auto-loads top-level files in `.opencode/plugins/`
- this repo wants plugin source organized under `src/opencode/plugins/<plugin>/`

To satisfy both, the wrapper should use a top-level entry shim plus a nested source folder.

### Source Files To Add

```text
src/opencode/
  package.json                       # only if runtime deps are needed
  plugins/
    compass-beads.ts                 # top-level OpenCode entry shim
    compass-beads/
      README.md
      plugin.yaml
      plugin.ts
      vendor.ts
      vendor/
        agents/
          task-agent.md
        commands/
          *.md
```

### Why This Layout

- `src/opencode/plugins/compass-beads.ts`
  - becomes `.opencode/plugins/compass-beads.ts` downstream
  - is auto-loaded by OpenCode
  - re-exports the real plugin from `./compass-beads/plugin.ts`
- `src/opencode/plugins/compass-beads/`
  - keeps Compass source, metadata, docs, and vendored assets together
  - matches the repo’s preferred per-plugin folder structure

### Entry Shim

Expected content shape:

```ts
export { CompassBeadsPlugin as default, CompassBeadsPlugin } from "./compass-beads/plugin"
```

That keeps the auto-loaded file small and lets the real implementation live in the folder.

## Wrapper Implementation Plan

### 1. Vendor The Upstream Baseline

Copy the upstream plugin’s small-surface assets into the Compass plugin folder:

- `src/plugin.ts` -> `src/opencode/plugins/compass-beads/plugin.ts`
- `src/vendor.ts` -> `src/opencode/plugins/compass-beads/vendor.ts`
- `vendor/commands/*.md` -> `src/opencode/plugins/compass-beads/vendor/commands/*.md`
- `vendor/agents/task-agent.md` -> `src/opencode/plugins/compass-beads/vendor/agents/task-agent.md`

Reason:

- The upstream repo is intentionally designed for forking/copying.
- Vendoring keeps downstream behavior deterministic.
- It avoids runtime dependency on a third-party npm package for the core tracking wrapper.

### 2. Rename And Re-scope The Runtime

Rename exported plugin symbol to something Compass-owned, for example:

- `CompassBeadsPlugin`

Then update the implementation in three places.

#### Context Injection

Keep the existing injection pattern, but change the injected guidance block.

Inject:

- `bd prime` output when available
- Compass-specific tracking guidance
- explicit reminder that BMAD artifacts and `bd` remain authoritative

Do not inject:

- into subagents by default
- into sessions where `bd prime` fails
- into repos with no active beads setup

#### Command Registration

Keep the vendored beads commands available through the plugin config hook.

Pilot posture:

- preserve upstream command coverage
- keep command names stable in pilot 1 rather than inventing a second alias set
- document that these commands expose beads operations, not a new Compass task model

#### Task Agent Registration

Keep the task agent, but rewrite its prompt to match Compass repo policy:

- use `bd` as system of record
- file discovered follow-up work in `bd`
- respect repo quality gates
- do not improvise a separate workflow

### 3. Add Compass Guards

The wrapper should add small but important guards around the upstream logic.

#### Guard A: `bd` availability

Before injecting context or expecting commands to work:

- detect whether `bd` is installed
- fail soft if it is missing
- log a structured warning through `client.app.log()`

#### Guard B: beads initialization

If the repo lacks usable beads state:

- skip automatic context injection
- keep the plugin loaded
- return clear guidance when a beads command is invoked

#### Guard C: subagent scoping

Preserve the upstream behavior that avoids polluting unrelated subagents with beads context.

#### Guard D: Compass-only guidance

Do not inject general-purpose advice that conflicts with repo policy.

The guidance block should explicitly say:

- use `bd` for issue tracking
- do not create parallel markdown TODO systems
- close the work session using the repo’s required sync/commit/push protocol

### 4. Decide Dependency Strategy

Preferred pilot approach:

- vendor plugin logic locally
- avoid external runtime dependencies where practical

If `plugin.ts` still imports:

- `@opencode-ai/plugin`
- `@opencode-ai/sdk`
- `zod`

then add `src/opencode/package.json` so the downstream `.opencode/package.json` exists and OpenCode can install dependencies automatically.

Recommended initial `src/opencode/package.json` scope:

```json
{
  "private": true,
  "type": "module",
  "dependencies": {
    "@opencode-ai/plugin": "<pinned-version>",
    "@opencode-ai/sdk": "<pinned-version>",
    "zod": "<pinned-version>"
  }
}
```

Use pinned or narrowly-ranged versions, not broad floating ranges, because this bundle is shipped downstream as a managed runtime surface.

### 5. Keep Compass Metadata Beside The Plugin

Add `plugin.yaml` for Compass-side metadata such as:

- plugin id
- upstream source repo
- wrapper posture: `wrap`
- owner
- status
- dependency notes

This file is for Compass maintainers, not OpenCode runtime loading.

## Installation With Compass Engine

This is the exact installation path if we implement the wrapper inside `compass-engine`.

### Maintainer Flow In `compass-engine`

1. Add the wrapper source under `src/opencode/plugins/`
2. Add `src/opencode/package.json` if runtime deps are needed
3. Run:

```bash
npm run validate
npm run build
npm run push -- --dry-run --targets opencode
```

4. Push the `opencode` bundle into a target repo:

```bash
npm run push -- --project /path/to/repo --targets opencode
```

Or to all managed repos:

```bash
npm run push -- --all --targets opencode
```

### What Downstream Repos Receive

The current build/push pipeline copies `src/opencode/` to `dist/.opencode/`, then syncs that into the destination repo as `.opencode/`.

So a downstream repo would receive:

```text
.opencode/
  commands/
  agents/
  plugins/
    compass-beads.ts
    compass-beads/
      plugin.ts
      vendor.ts
      vendor/...
  package.json          # if added in src/opencode/
```

### How OpenCode Loads It

On downstream OpenCode startup:

1. OpenCode scans `.opencode/plugins/`
2. It auto-loads `compass-beads.ts`
3. That file imports the real implementation from `./compass-beads/plugin.ts`
4. If `.opencode/package.json` exists, OpenCode runs `bun install` for local plugin dependencies
5. The plugin registers its hooks, commands, and task agent

### What Downstream Users Must Still Install

Compass can ship the plugin, but it does not replace beads itself.

Required downstream prerequisites:

- `bd` CLI installed on the machine
- repo initialized for beads, or at minimum a usable beads context
- OpenCode restarted after the `.opencode/` bundle is synced

Pilot documentation should include:

```bash
bd onboard
```

or the relevant repo-specific beads setup step after plugin sync.

## Recommended Installation Contract

For Compass-managed repos, prefer this contract:

- Compass ships the local plugin through `.opencode/plugins/`
- Compass ships `.opencode/package.json` when needed
- downstream repos do **not** manually add the npm package to `opencode.json`

Reason:

- local auto-load is deterministic
- plugin version stays pinned to the Compass Engine bundle version
- downstream repos get the same managed behavior from `compass-engine push`

Only use npm-package installation if Compass later decides to publish the wrapper as its own package for non-Compass users.

## Verification Plan

### Local Validation In `compass-engine`

- `npm run validate`
- `npm run build`
- inspect `dist/.opencode/plugins/compass-beads.ts`
- inspect `dist/.opencode/plugins/compass-beads/`

### Dry-Run Distribution

```bash
npm run push -- --dry-run --targets opencode --project /path/to/test-repo
```

Verify:

- managed sync preserves local `.opencode/state` and `.opencode/cache`
- plugin files land where OpenCode expects them
- no unexpected removals occur

### Runtime Verification In A Test Repo

In a repo with beads enabled:

1. sync the `opencode` target
2. restart OpenCode
3. verify automatic context injection happens once per primary session
4. compact a session and verify reinjection
5. run one beads command through the plugin
6. verify the task agent is registered

### Failure Cases To Test

- `bd` missing
- `.beads` not initialized
- repo with no git worktree
- subagent session where beads context should not be injected

## Implementation Sequence

1. Create `src/opencode/plugins/compass-beads/`
2. Vendor the upstream plugin files and command/agent assets
3. Add the top-level `src/opencode/plugins/compass-beads.ts` entry shim
4. Rewrite guidance and task-agent prompt for Compass policy
5. Add soft-failure guards for missing `bd` or missing beads state
6. Add `src/opencode/package.json` if runtime dependencies remain
7. Update validation if needed for new required OpenCode runtime files
8. Run validate/build/push dry-run
9. Test in one downstream repo before broad rollout

## Recommended Pilot Outcome

For pilot 1, the wrapper should deliver only this:

- automatic `bd prime` context injection for primary sessions
- reinjection on compaction
- vendored beads command registration
- Compass-aligned beads task agent
- deterministic install via `compass-engine push -- --targets opencode`

Everything else should stay out of scope until this baseline works reliably.

## Sources

- OpenCode plugins docs: https://opencode.ai/docs/plugins/
- OpenCode skills docs: https://opencode.ai/docs/skills/
- Upstream plugin README: https://github.com/joshuadavidthomas/opencode-beads
- Local strategy: `docs/architecture/opencode-plugin-strategy.md`
- Local development rules: `docs/development/opencode/plugin-development.md`
