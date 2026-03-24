# Type Inject Compass Wrapper Plan

Status: draft
Owner:
Last Updated: 2026-03-24
Phase ID:
Parent Issue: `bmad-engine-5zr`
Related Pilot Issue: `bmad-engine-9cb`

## Objective

- Define exactly how Compass should wrap `nick-vi/type-inject` for OpenCode.
- Keep the plugin in the code-intelligence lane so it improves TypeScript awareness without gaining workflow authority.
- Specify how type-context injection, type lookup, and write-time type feedback should be implemented in `compass-engine` and installed into downstream repos through the normal `build` and `push` flow.

## Ground Truth

### Official OpenCode Plugin Model

From the official OpenCode plugin docs:

- local plugins auto-load from `.opencode/plugins/`
- local plugins can use external packages via `.opencode/package.json`
- OpenCode runs `bun install` for those local dependencies at startup
- plugins can register custom tools
- plugins can hook `tool.execute.before` and `tool.execute.after`
- plugins also have access to file and session events such as `file.edited` and `session.compacted`

Practical implication for Compass:

- Compass should ship a local plugin through the managed `.opencode/` bundle
- we do not need a separate npm-installed OpenCode plugin in downstream repos
- we can expose custom type tools directly inside the plugin without routing through MCP

### Upstream `type-inject` Shape

The upstream monorepo has four parts:

- `@nick-vi/type-inject-core`
  - TypeScript extraction, prioritization, formatting, lookup, and checking
- `@nick-vi/opencode-type-inject`
  - OpenCode plugin with read-time injection and custom tools
- `@nick-vi/type-inject-mcp`
  - MCP server exposing the same lookup and type-check tools
- `@nick-vi/claude-type-inject-hook`
  - Claude-specific read/write hooks

### What The Upstream OpenCode Plugin Already Does

The upstream OpenCode plugin:

- loads only when `tsconfig.json` exists at the project root
- injects referenced type definitions into `read` tool output for TS, TSX, MTS, CTS, and Svelte files
- exposes these tools:
  - `lookup_type`
  - `list_types`
  - `type_check`
- uses the shared core package for lookup and diagnostics

### Important Upstream Gaps Relative To Compass Pilot Scope

The upstream OpenCode plugin does not currently:

- provide Claude-style write-time type error feedback after edits
- namespace its tool names
- use Compass-specific logging, support boundaries, or install flow
- handle nested `tsconfig.json` discovery at plugin startup; it exits early if root `tsconfig.json` is missing

## Compass Wrapper Boundary

### Pilot Decision

This pilot should be a true `wrap`, not an `adopt as-is`.

Compass should:

- keep the upstream type-extraction and type-checking core logic
- own the OpenCode runtime layer locally
- add guardrails around naming, initialization, and write-feedback behavior

### What We Keep From Upstream

- `@nick-vi/type-inject-core` as the extraction and checking engine
- the read-time type injection concept
- the lookup and type-check tool capabilities
- TypeScript-first scope with best-effort Svelte support

### What We Change For Compass

- replace generic tool names with a namespaced Compass-safe surface
- relax startup behavior so the plugin can still load in repos without a root `tsconfig.json`
- add guarded write-time type diagnostics after file edits
- make logging and failure behavior Compass-friendly
- install through the managed local `.opencode` bundle instead of telling downstream repos to add an npm plugin or MCP server manually

### What We Do Not Change In Pilot 1

- we do not reimplement the core extraction engine
- we do not give the plugin planning or issue-tracking authority
- we do not route through the upstream MCP server for OpenCode
- we do not support non-TypeScript languages
- we do not add project-specific user configuration files in pilot 1

## Why Compass Should Not Use The MCP Server For This Pilot

The upstream repo offers an MCP server, but for Compass OpenCode this adds more moving parts than value.

Reasons to avoid MCP in pilot 1:

- the OpenCode plugin can register the same tools directly
- read-time injection already belongs in the plugin hook layer, not MCP
- MCP would introduce another process and install path to manage
- the wrapper needs custom write-feedback behavior anyway, so Compass needs a local OpenCode layer regardless

Recommended posture:

- use `@nick-vi/type-inject-core` as the shared engine
- build a Compass-local OpenCode plugin on top of it

## Exact Wrapper Behavior

### 1. Read-Time Type Injection

Compass should keep the upstream pattern:

- capture `read` tool calls in `tool.execute.before`
- inspect the file path and optional offset/limit
- after the read completes, inject only relevant external type signatures into the output

Compass-specific rules:

- only operate on `.ts`, `.tsx`, `.mts`, `.cts`, and `.svelte`
- skip non-TypeScript files silently
- skip barrel files when configured by the upstream budget rules
- use nearest-available `tsconfig.json` for the file rather than requiring one at repo root
- soft-fail on extraction problems and leave the original read output unchanged

### 2. Type Lookup Tools

Compass should expose the lookup surface, but not under the upstream generic names.

Recommended pilot tool names:

- `ts_lookup_type`
- `ts_list_types`
- `ts_type_check`

Reason:

- avoids collisions with other plugins or MCP tools
- makes the TypeScript-specific purpose obvious
- keeps the wrapper from leaking raw upstream naming into the broader Compass tool surface

The tool behavior should stay close to upstream:

- lookup by type name
- list types in the project
- run type checking for the project or a specific file

### 3. Write-Time Type Feedback

This is the main wrapper addition relative to upstream OpenCode support.

Recommended behavior:

- listen on `tool.execute.after`
- target write-like editing tools, at minimum `write`
- optionally extend to other edit tools only after confirming their output shape
- when a TS/Svelte file was successfully written, run type checking using the nearest `tsconfig.json`
- append concise diagnostics to the tool result if errors are found

Output shape should mirror the upstream checker formatting:

- file-local errors first
- project spillover second
- only errors, not warnings or hints
- capped output to avoid flooding the context

Guardrails:

- if no `tsconfig.json` can be found, do nothing
- if the write target is not a TS/Svelte file, do nothing
- if type checking throws or times out, log softly and do not fail the write itself

### 4. Initialization Model

Compass should not hard-disable the plugin at startup just because root `tsconfig.json` is missing.

Instead:

- initialize the plugin runtime regardless
- create extractor and lookup helpers lazily when first needed
- use file-level `findNearestTsconfig()` resolution when handling reads or type-check requests

This is important for:

- monorepos with nested TS packages
- repos whose active TypeScript code is not rooted at the project top level
- hybrid repos where only part of the tree uses TypeScript

## Exact Source Layout

Recommended layout:

```text
src/opencode/
  package.json
  plugins/
    compass-type-inject.ts
    compass-type-inject/
      README.md
      plugin.yaml
      plugin.ts
```

### Why This Layout

- `src/opencode/plugins/compass-type-inject.ts`
  - becomes `.opencode/plugins/compass-type-inject.ts` downstream
  - is auto-loaded by OpenCode
  - keeps the runtime entry stable
- `src/opencode/plugins/compass-type-inject/`
  - keeps Compass-owned wrapper logic, metadata, and docs together

### Entry Shim

Expected shape:

```ts
export { CompassTypeInjectPlugin as default, CompassTypeInjectPlugin } from "./compass-type-inject/plugin"
```

## Dependency Strategy

Recommended pilot strategy:

- do not vendor the upstream core source
- depend on the published `@nick-vi/type-inject-core` package
- implement the OpenCode wrapper locally in Compass

Reason:

- keeps the wrapper thinner and easier to maintain
- preserves the tested extraction and checking engine
- still gives Compass full control over OpenCode-specific behavior

### Dependencies To Add

Current `src/opencode/package.json` already includes:

- `@opencode-ai/plugin`
- `@opencode-ai/sdk`
- `jsonc-parser`
- `zod`

The wrapper will additionally need:

- `@nick-vi/type-inject-core@1.1.1`
- `typescript@6.0.2`

Notes:

- `@nick-vi/type-inject-core` depends on `ts-morph`, so Compass does not need to add that directly
- the core package declares `svelte` as an optional peer; Compass should treat Svelte support as best-effort in pilot 1 rather than adding `svelte` globally to every downstream `.opencode` bundle

### Why `typescript` Must Be Added

The core package expects `typescript` as a peer dependency. Relying on each downstream repo to satisfy that inside the `.opencode` runtime would be brittle.

So Compass should install `typescript` in `.opencode/package.json` to keep the wrapper deterministic.

## Compass Metadata And Docs

Add `plugin.yaml` beside the wrapper with fields such as:

- plugin id
- wrapper posture: `wrap`
- runtime entry
- upstream repo
- owner
- status
- support notes

Add a plugin README that explains:

- this is a code-intelligence utility, not a workflow plugin
- it does not replace `bd`, BMAD, or code review
- how it is installed through Compass Engine
- what TypeScript and Svelte support is guaranteed in pilot 1

## Installation With Compass Engine

This is the exact installation path if we implement the wrapper in `compass-engine`.

### Maintainer Flow In `compass-engine`

1. Add the wrapper source under `src/opencode/plugins/`
2. extend `src/opencode/package.json` with the required dependencies
3. run:

```bash
npm run validate
npm run build
npm run push -- --dry-run --targets opencode
```

4. sync the OpenCode bundle into a target repo:

```bash
npm run push -- --project /path/to/repo --targets opencode
```

### What Downstream Repos Receive

The current build/push flow copies `src/opencode/` to `dist/.opencode/`, then syncs that into the destination repo as `.opencode/`.

So downstream repos would receive:

```text
.opencode/
  agents/
  commands/
  plugins/
    compass-type-inject.ts
    compass-type-inject/
      plugin.ts
      plugin.yaml
      README.md
  package.json
```

### How OpenCode Loads It

On downstream OpenCode startup:

1. OpenCode scans `.opencode/plugins/`
2. it auto-loads `compass-type-inject.ts`
3. that file imports the real implementation from `./compass-type-inject/plugin.ts`
4. if `.opencode/package.json` exists, OpenCode runs `bun install`
5. the plugin registers its read hooks, write-feedback hooks, and custom tools

## Downstream Requirements

Required:

- a Bun-backed OpenCode runtime
- TypeScript repos, or at least TS packages under the repo
- readable `tsconfig.json` near the files being inspected

Best-effort:

- Svelte support, when the downstream environment already has `svelte` available or the wrapper later opts to include it

Not required:

- separate MCP server setup
- manual npm installation of `@nick-vi/opencode-type-inject`

## Verification Plan

### Local Validation In `compass-engine`

- `npm run validate`
- `npm run build`
- inspect `dist/.opencode/plugins/compass-type-inject.ts`
- inspect `dist/.opencode/plugins/compass-type-inject/`
- inspect `dist/.opencode/package.json` for `@nick-vi/type-inject-core` and `typescript`

### Dry-Run Distribution

```bash
npm run push -- --dry-run --targets opencode --project /path/to/test-repo
```

Verify:

- managed sync installs the wrapper in `.opencode/plugins/`
- `.opencode/package.json` updates correctly
- no unexpected removals occur in local OpenCode state/cache paths

### Runtime Verification In A Test Repo

In a repo with TypeScript files:

1. sync the `opencode` target
2. restart OpenCode
3. read a TS file that references imported types
4. verify injected type context appears in the read output
5. call `ts_lookup_type`
6. call `ts_list_types`
7. call `ts_type_check`
8. write a deliberate type error into a test file
9. verify post-write diagnostics appear without blocking the write itself

### Important Failure Cases To Test

- repo with no TypeScript files
- monorepo with nested `tsconfig.json` but none at project root
- file read outside TS/Svelte scope
- large file where token budget filtering matters
- no `svelte` dependency available in a Svelte file path
- write to a TS file with no nearby `tsconfig.json`

## Implementation Sequence

1. create `src/opencode/plugins/compass-type-inject/`
2. add the top-level `src/opencode/plugins/compass-type-inject.ts` shim
3. implement the local wrapper in `plugin.ts` using `@nick-vi/type-inject-core`
4. add namespaced tool definitions
5. add guarded write-feedback behavior
6. extend `src/opencode/package.json`
7. update validation for new required files
8. run validate/build/push dry-run
9. smoke-test in one downstream TS repo

## Recommended Pilot Outcome

For pilot 1, the wrapper should deliver only this:

- read-time type injection for TS/Svelte reads
- namespaced type lookup and type-check tools
- guarded post-write type diagnostics
- deterministic install through Compass Engine

Everything else should stay out of scope until the baseline proves useful.

## Sources

- OpenCode plugins docs: https://opencode.ai/docs/plugins/
- Upstream README: https://github.com/nick-vi/type-inject
- Upstream OpenCode package:
  - `packages/opencode/package.json`
  - `packages/opencode/.opencode/plugin/type-inject.ts`
- Upstream core package:
  - `packages/core/package.json`
  - `packages/core/lib/config.ts`
  - `packages/core/lib/checker.ts`
- Upstream MCP package:
  - `packages/mcp/package.json`
  - `packages/mcp/src/index.ts`
- Local strategy: `docs/architecture/opencode-plugin-strategy.md`
- Local development rules: `docs/development/opencode/plugin-development.md`
