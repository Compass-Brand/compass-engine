# OpenCode Worktree Pilot Adoption Plan

Status: complete
Owner:
Last Updated: 2026-04-13
Phase ID:
Parent Issue: `bmad-engine-4d3`
Related Pilot Issue: `bmad-engine-byc`

## Objective

- Define exactly how Compass should adopt `kdcokenny/opencode-worktree`.
- Keep the plugin in the utility lane so it improves isolated OpenCode execution without competing with BMAD or beads authority.
- Specify how the plugin is packaged in `compass-engine` and installed into downstream repos through the normal `build` and `push` flow.

## Ground Truth

### Official OpenCode Plugin Model

From the official OpenCode docs:

- Local plugins are auto-loaded from `.opencode/plugins/`.
- Local plugins can import npm packages when `.opencode/package.json` exists.
- OpenCode runs `bun install` for local plugin dependencies at startup.
- A plugin is a JS/TS module that exports one or more plugin functions.
- Plugins can register hooks, custom tools, and event handlers.
- Plugin context includes `project`, `directory`, `worktree`, `client`, and Bun `$`.

Practical implication for Compass:

- We should ship `opencode-worktree` as a local managed plugin inside the downstream `.opencode/` bundle.
- We should not require downstream repos to install it separately through OCX or an npm package.
- We only need to add runtime dependencies to `src/opencode/package.json` when the vendored plugin imports them.

### Upstream `opencode-worktree` Shape

The upstream plugin is larger than `opencode-beads`, but its scope is still well-bounded:

- `src/plugin/worktree.ts`
  - registers `worktree_create` and `worktree_delete` tools
  - creates and removes git worktrees
  - forks OpenCode sessions and launches terminals
  - processes cleanup on `session.idle`
- `src/plugin/worktree/state.ts`
  - stores active worktree state in a SQLite database under the user home directory
- `src/plugin/worktree/terminal.ts`
  - handles terminal launch across tmux, cmux, macOS, Linux, Windows, and WSL
- `src/plugin/kdco-primitives/**`
  - shared helpers for project ids, shell escaping, mutexes, logging, and terminal detection

The plugin is designed as a utility runtime, not as a planning or workflow authority.

### Upstream Operational Assumptions

The upstream runtime assumes:

- Bun runtime is available for plugin execution.
- `git worktree` is usable in the current repo.
- OpenCode session APIs can fork and resume sessions.
- terminal spawning is part of the expected workflow.
- project-specific sync and lifecycle behavior lives in `.opencode/worktree.jsonc`.

It also uses the following storage patterns:

- worktree directories under `~/.local/share/opencode/worktree/<project-id>/<branch>/`
- state database under `~/.local/share/opencode/plugins/worktree/<project-id>.sqlite`
- copied plan and delegation state under `~/.local/share/opencode/workspace/` and `~/.local/share/opencode/delegations/`

## Compass Adoption Posture

### Pilot Decision

This pilot stays `adopt as-is` at the behavior level.

That means:

- keep upstream tool names
- keep upstream session forking behavior
- keep upstream terminal spawning behavior
- keep upstream `.opencode/worktree.jsonc` configuration model

Compass should only add:

- managed local packaging inside `src/opencode/plugins/`
- dependency declaration in `src/opencode/package.json`
- maintainer metadata and install documentation
- explicit support-boundary documentation for BMAD and beads

### Why This Stays Utility-Only

`opencode-worktree` does not replace planning or tracking. It gives OpenCode an isolated execution surface.

Compass should treat it as:

- a workspace utility for concurrent or isolated execution
- a possible future substrate for parallel BMAD story work
- not a replacement for:
  - `bd`
  - BMAD phase or story artifacts
  - Compass workflow routing

### What We Will Not Change In Pilot 1

- We will not rename `worktree_create` or `worktree_delete`.
- We will not add BMAD-aware command wrappers on top of the worktree tools.
- We will not auto-create BMAD stories, beads issues, or planning artifacts from worktree events.
- We will not redesign the upstream session-forking model.
- We will not invent a Compass-specific worktree config schema.

## Supported Boundary

### Supported In Pilot 1

- creating isolated git worktrees from OpenCode
- spawning a new terminal/OpenCode session for that worktree
- deleting a worktree through the plugin lifecycle
- project-level `.opencode/worktree.jsonc` file sync and hook configuration
- local managed installation through Compass Engine

### Supported With Caveats

- Windows terminal launch
  - upstream supports Windows Terminal and `cmd.exe`
- WSL launch
  - upstream supports `wt.exe` interop and shell-script launch
- lifecycle hooks on Windows
  - upstream executes hooks with `bash -c`
  - practical support therefore assumes Git Bash, WSL bash, or equivalent bash availability if hooks are used
- cmux and tmux behavior
  - supported by upstream, but only when the relevant environment and executables are present

### Not Promised In Pilot 1

- Compass-owned wrapper semantics around worktree tool calls
- automatic downstream validation of project-specific hook commands
- cross-repo orchestration semantics
- auto-merge, auto-PR, or BMAD story closeout behavior

## Exact Source Layout

Compass still needs a local auto-loaded plugin entry at the top level of `src/opencode/plugins/`.

Recommended layout:

```text
src/opencode/
  package.json
  plugins/
    compass-worktree.ts
    compass-worktree/
      README.md
      plugin.yaml
      plugin.ts
      kdco-primitives/
        *.ts
      worktree/
        *.ts
```

### Why This Layout

- `src/opencode/plugins/compass-worktree.ts`
  - becomes `.opencode/plugins/compass-worktree.ts` downstream
  - is auto-loaded by OpenCode
  - keeps the top-level plugin surface stable for Compass
- `src/opencode/plugins/compass-worktree/`
  - keeps vendored source, metadata, and docs together
  - lets Compass document the plugin without forking its runtime behavior heavily

### Entry Shim

Expected shape:

```ts
export { WorktreePlugin as default, WorktreePlugin } from "./compass-worktree/plugin"
```

The runtime symbol can stay upstream-compatible. Compass ownership belongs in the packaging and metadata layer, not in renamed behavior.

## Adoption Implementation Plan

### 1. Vendor The Upstream Runtime Largely Unchanged

Copy the upstream source into the Compass plugin folder with path adjustments only:

- `src/plugin/worktree.ts` -> `src/opencode/plugins/compass-worktree/plugin.ts`
- `src/plugin/worktree/**` -> `src/opencode/plugins/compass-worktree/worktree/**`
- `src/plugin/kdco-primitives/**` -> `src/opencode/plugins/compass-worktree/kdco-primitives/**`

This is still `adopt as-is` because:

- runtime behavior stays intact
- tool names stay intact
- lifecycle semantics stay intact
- Compass is only repackaging it for managed downstream install

### 2. Keep The Tool Surface Unchanged

Pilot tool surface:

- `worktree_create(branch, baseBranch?)`
- `worktree_delete(reason)`

Do not add aliases in pilot 1.

Reason:

- this is a commodity utility
- aliasing would create another Compass-specific surface to maintain
- the current names are already descriptive and stable enough

### 3. Add Compass Metadata And Install Docs

Add `plugin.yaml` beside the vendored runtime with fields such as:

- plugin id
- wrapper posture: `adopt_as_is`
- runtime entry
- upstream repo
- owner
- status
- support caveats

Add a plugin README that explains:

- this is a utility plugin, not a planning/tracking plugin
- how it is shipped through Compass Engine
- when to use it
- current support caveats, especially Windows hook execution

### 4. Extend `src/opencode/package.json`

Current Compass OpenCode dependencies already include:

- `@opencode-ai/plugin`
- `@opencode-ai/sdk`
- `zod`

This plugin additionally needs:

- `jsonc-parser`

No external SQLite package is needed because upstream uses `bun:sqlite`.

Recommended package delta:

```json
{
  "dependencies": {
    "@opencode-ai/plugin": "1.0.143",
    "@opencode-ai/sdk": "1.0.143",
    "jsonc-parser": "<pinned-version>",
    "zod": "4.1.13"
  }
}
```

Use a pinned version, not a broad range.

### 5. Document The Authority Boundary Explicitly

The Compass README and metadata should say this clearly:

- the plugin manages isolated execution surfaces
- `bd` remains the issue and task system of record
- BMAD artifacts remain the planning and delivery system of record
- worktree creation does not grant authority to invent workflow state

### 6. Keep Project Config Repo-Local

Do not ship a default `.opencode/worktree.jsonc` from Compass Engine in pilot 1.

Reason:

- sync rules and hooks are highly repo-specific
- a generic default would be more likely to surprise than help
- the upstream plugin already auto-creates the file on first use

Compass should only document example patterns for downstream repos.

## Installation With Compass Engine

This is the exact installation path if we adopt the plugin in `compass-engine`.

### Maintainer Flow In `compass-engine`

1. Vendor the plugin source under `src/opencode/plugins/compass-worktree/`
2. Add the top-level `src/opencode/plugins/compass-worktree.ts` entry shim
3. Add `jsonc-parser` to `src/opencode/package.json`
4. Run:

```bash
npm run validate
npm run build
npm run push -- --dry-run --targets opencode
```

5. Push the `opencode` target into a downstream repo:

```bash
npm run push -- --project /path/to/repo --targets opencode
```

### What Downstream Repos Receive

The current build/push pipeline copies `src/opencode/` to `dist/.opencode/`, then syncs that into the destination repo as `.opencode/`.

So a downstream repo would receive:

```text
.opencode/
  agents/
  commands/
  plugins/
    compass-worktree.ts
    compass-worktree/
      plugin.ts
      kdco-primitives/
      worktree/
  package.json
```

### How OpenCode Loads It

On downstream OpenCode startup:

1. OpenCode scans `.opencode/plugins/`
2. it auto-loads `compass-worktree.ts`
3. that file re-exports the real implementation from `./compass-worktree/plugin.ts`
4. if `.opencode/package.json` exists, OpenCode runs `bun install`
5. the plugin registers the `worktree_create` and `worktree_delete` tools and its `session.idle` cleanup handler

## Downstream Requirements

Required:

- Bun-backed OpenCode runtime
- `git` with `worktree` support
- OpenCode restarted after sync if it was already running

Conditional:

- `tmux` or `cmux` only when those execution modes are expected
- Windows Terminal for the best Windows launch path
- bash availability on Windows if downstream repos want hook execution

Repo-level expectations:

- downstream repos own their own `.opencode/worktree.jsonc`
- downstream repos decide whether to copy env files, symlink `node_modules`, or run lifecycle hooks

## Verification Plan

### Local Validation In `compass-engine`

- `npm run validate`
- `npm run build`
- inspect `dist/.opencode/plugins/compass-worktree.ts`
- inspect `dist/.opencode/plugins/compass-worktree/`
- confirm `dist/.opencode/package.json` includes `jsonc-parser`

### Dry-Run Distribution

```bash
npm run push -- --dry-run --targets opencode --project /path/to/test-repo
```

Verify:

- managed sync installs the plugin under `.opencode/plugins/`
- `.opencode/package.json` updates correctly
- no unrelated `.opencode/state` or `.opencode/cache` data is removed

### Runtime Verification In A Test Repo

1. sync the `opencode` target
2. restart OpenCode
3. call `worktree_create` with a safe test branch
4. verify a worktree is created outside the repo at the expected path
5. verify a new terminal/OpenCode session launches
6. call `worktree_delete`
7. verify cleanup runs on `session.idle`

### Important Failure Cases To Test

- repo without `git worktree` support
- branch name validation failure
- terminal launch failure after worktree creation
- Windows machine without bash when hooks are configured
- missing `jsonc-parser` dependency
- stale or broken OCX launch context variables

## Implementation Sequence

1. Create `src/opencode/plugins/compass-worktree/`
2. Vendor the upstream runtime with path adjustments only
3. Add `src/opencode/plugins/compass-worktree.ts`
4. Add plugin metadata and README
5. Add `jsonc-parser` to `src/opencode/package.json`
6. Update validation if needed for required plugin files
7. Run validate/build/push dry-run
8. Smoke-test in one downstream repo before broader use

## Recommended Pilot Outcome

For pilot 1, this plugin should deliver only this:

- managed local installation through Compass Engine
- intact upstream worktree creation and deletion behavior
- clear authority boundaries relative to BMAD and beads
- documented platform caveats

If that baseline works, later follow-on work can decide whether Compass wants:

- BMAD-aware worktree naming conventions
- worktree-to-story routing helpers
- optional safety rails for hook execution
- orchestration between this plugin and future background-agent tooling

## Sources

- OpenCode plugins docs: https://opencode.ai/docs/plugins/
- OpenCode agents docs: https://opencode.ai/docs/agents/
- Upstream plugin README: https://github.com/kdcokenny/opencode-worktree
- Upstream source:
  - `src/plugin/worktree.ts`
  - `src/plugin/worktree/state.ts`
  - `src/plugin/worktree/terminal.ts`
  - `src/plugin/worktree/launch-context.ts`
  - `src/plugin/kdco-primitives/shell.ts`
- Local strategy: `docs/architecture/opencode-plugin-strategy.md`
- Local development rules: `docs/development/opencode/plugin-development.md`
