# OpenCode Handoff Wrapper Plan

Status: complete
Owner:
Last Updated: 2026-04-13
Phase ID:
Parent Issue: `bmad-engine-3c1`
Related Pilot Issue: `opencode-handoff` follow-on candidate

## Objective

- Define exactly how Compass should wrap `joshuadavidthomas/opencode-handoff`.
- Keep the plugin in the session-continuity lane so it helps with context carry-forward without turning into a general memory or workflow-authority layer.
- Specify how handoff prompts, session transcript access, and synthetic file injection should be implemented in `compass-engine` and installed into downstream repos through the normal `build` and `push` flow.

## Ground Truth

### Official OpenCode Plugin Model

From the official OpenCode plugin docs:

- local plugins auto-load from `.opencode/plugins/`
- local plugins can register commands and tools
- plugins can call OpenCode client APIs for session messages, session prompts, and TUI commands
- plugins can inject synthetic prompt parts into a session
- local plugin dependencies can be installed through `.opencode/package.json`

Practical implication for Compass:

- Compass should ship a local plugin through the managed `.opencode/` bundle
- the wrapper can keep the slash-command and tool pattern entirely inside the plugin
- Compass does not need a separate MCP service for this capability

### Upstream `opencode-handoff` Shape

The upstream plugin is intentionally small:

- `src/plugin.ts`
  - registers `/handoff <goal>`
  - registers `handoff_session` and `read_session` tools
  - detects new sessions created from handoff prompts
  - injects referenced files into the new session as synthetic read-like parts
- `src/tools.ts`
  - creates the new session and editable prompt draft
  - reads previous session transcripts by session ID
- `src/files.ts`
  - parses `@file` references from handoff prompts
  - reads referenced files and builds synthetic file parts
- `src/vendor.ts`
  - mirrors OpenCode read formatting so synthetic file parts look native

### What The Upstream Plugin Already Does Well

- preserves session continuity without needing external storage
- creates a new session with a prefilled draft instead of immediately sending the handoff
- uses `@file` references to frontload important code context
- provides transcript retrieval when the summary is not enough

### Important Upstream Risks For Compass

The upstream design is effective, but it is broader than Compass should adopt raw:

- `read_session` can read any session transcript by arbitrary session ID
- file-reference resolution uses `path.resolve(directory, ref)` without a Compass-specific repo-root safety policy
- the handoff prompt template is generic rather than BMAD/beads-aware
- the wrapper does not explicitly preserve issue ids, artifact paths, test status, or next-step gates that matter for Compass handoff quality

## Compass Wrapper Boundary

### Pilot Decision

This should be a `wrap`, not an `adopt as-is`.

Compass should:

- keep the small upstream runtime structure
- keep the `/handoff` user-facing command
- add stricter session and file-scope guardrails
- replace the generic handoff prompt with a Compass-aware one

### What We Keep From Upstream

- the overall flow:
  - generate handoff
  - create new session
  - prefill editable draft
  - allow the new session to retrieve source transcript when needed
- synthetic `@file` loading into the new session
- reuse of OpenCode-native formatting for synthetic read parts

### What We Change For Compass

- constrain transcript access to the explicit source session for that handoff
- constrain file references to repo-local files only
- rewrite the handoff command template to preserve Compass-specific continuity details
- document that this plugin complements `bd` and BMAD rather than replacing them

### What We Do Not Change In Pilot 1

- we do not build a general memory store
- we do not persist handoff data outside normal session context
- we do not auto-generate BMAD artifacts during handoff
- we do not make this a planning plugin

## Exact Wrapper Behavior

### 1. User-Facing Command

Keep the user-facing slash command:

- `/handoff <goal>`

Reason:

- it is short and already matches the upstream mental model
- this is a session action, not a BMAD command family
- the collision risk is lower on slash commands than on generic tool names

### 2. Compass Handoff Prompt Template

The command template should be rewritten for Compass.

The generated handoff should explicitly preserve:

- active objective and requested next step
- active `bd` issue ids and statuses when known
- relevant planning and docs artifact paths
- relevant source files to load in the next session
- technical decisions already made
- blockers, caveats, and known risks
- tests run, tests not run, and why
- current branch or worktree context when relevant
- explicit user preferences or constraints

The generated handoff should explicitly avoid:

- conversational chatter
- dead ends unless they remain important constraints
- replacing `bd` or BMAD artifacts with prose-only task tracking

### 3. Session Creation Tool

Keep the upstream session-creation pattern:

- create a new session through the TUI client
- append the generated prompt as an editable draft
- show a success toast

Recommended internal tool name options:

- keep `handoff_session`, or
- rename to `compass_handoff_session`

For pilot 1, keeping `handoff_session` is acceptable because it is internal to the plugin flow and low-risk.

### 4. Transcript Reading Boundary

This is the most important wrapper change.

Compass should not allow arbitrary session transcript reads by any explicit session ID.

Recommended pilot behavior:

- when a handoff is created, store an in-memory mapping:
  - `newSessionID -> sourceSessionID`
- expose a tool named `read_handoff_session`
- in the new session, `read_handoff_session` should only read the mapped source session
- optional explicit `sessionID` input, if kept at all, must match the mapped source session or be rejected

Reason:

- this preserves the continuity feature
- it prevents the plugin from becoming a broad session-exfiltration tool
- it keeps the handoff workflow tightly scoped to the source session that created it

### 5. Synthetic File Injection

Compass should keep the synthetic file injection model but add path safety rules.

Rules:

- only load files that resolve inside the current repo root
- skip non-file paths
- skip binary files
- skip unreadable files silently
- preserve the upstream read-like output formatting

This means the wrapper should add a repo-root safety check before reading the referenced file.

### 6. Session Detection

Keep the upstream pattern where the plugin:

- detects the handoff marker in the first user message of the new session
- parses `@file` references from that draft
- injects the file contents as synthetic prompt parts

That is still the right mechanism. Compass should only narrow the allowed file set and transcript scope.

## Recommended Tool Surface

User-facing:

- `/handoff <goal>`

Internal/plugin tools:

- `handoff_session`
- `read_handoff_session`

Why rename `read_session`:

- `read_session` is too generic
- the Compass wrapper should make its scope obvious
- `read_handoff_session` communicates that this is limited to the source session for the handoff

## Exact Source Layout

Recommended layout:

```text
src/opencode/
  package.json
  plugins/
    compass-handoff.ts
    compass-handoff/
      README.md
      plugin.yaml
      plugin.ts
      tools.ts
      files.ts
      vendor.ts
```

### Why This Layout

- `src/opencode/plugins/compass-handoff.ts`
  - becomes `.opencode/plugins/compass-handoff.ts` downstream
  - is auto-loaded by OpenCode
  - keeps the runtime entry stable for Compass
- `src/opencode/plugins/compass-handoff/`
  - keeps the local wrapper, helper files, metadata, and docs together

### Entry Shim

Expected shape:

```ts
export { CompassHandoffPlugin as default, CompassHandoffPlugin } from "./compass-handoff/plugin"
```

## Dependency Strategy

The upstream runtime only depends on:

- `@opencode-ai/plugin`
- `@opencode-ai/sdk`
- `zod`

Compass already ships those in `src/opencode/package.json`, so pilot 1 should not need any new runtime dependencies.

Recommended posture:

- vendor the small upstream runtime locally
- adjust the prompt template, session-scoping rules, and file-safety behavior
- do not depend on a separate upstream npm package at runtime

Reason:

- the surface area is small
- Compass wants precise behavioral constraints
- vendoring avoids version drift for a sensitive session-continuity tool

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

- this is a session-continuity utility
- it does not replace `bd`, BMAD, or planning artifacts
- it is scoped to source-session continuation, not general memory retrieval
- how it is installed through Compass Engine

## Installation With Compass Engine

This is the exact installation path if we implement the wrapper in `compass-engine`.

### Maintainer Flow In `compass-engine`

1. add the wrapper source under `src/opencode/plugins/`
2. verify `src/opencode/package.json` already covers the runtime dependencies
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
    compass-handoff.ts
    compass-handoff/
      plugin.ts
      tools.ts
      files.ts
      vendor.ts
      plugin.yaml
      README.md
  package.json
```

### How OpenCode Loads It

On downstream OpenCode startup:

1. OpenCode scans `.opencode/plugins/`
2. it auto-loads `compass-handoff.ts`
3. that file imports the real implementation from `./compass-handoff/plugin.ts`
4. if `.opencode/package.json` exists, OpenCode runs `bun install`
5. the plugin registers `/handoff`, the internal handoff tools, and the synthetic file injection behavior

## Downstream Requirements

Required:

- Bun-backed OpenCode runtime
- OpenCode version new enough to support the plugin APIs used by upstream

Not required:

- separate MCP setup
- external databases
- downstream repo-specific planning configuration

Expected repo conditions:

- files referenced by handoff should live inside the repo root
- the conversation should already contain the relevant work context

## Verification Plan

### Local Validation In `compass-engine`

- `npm run validate`
- `npm run build`
- inspect `dist/.opencode/plugins/compass-handoff.ts`
- inspect `dist/.opencode/plugins/compass-handoff/`

### Dry-Run Distribution

```bash
npm run push -- --dry-run --targets opencode --project /path/to/test-repo
```

Verify:

- managed sync installs the wrapper in `.opencode/plugins/`
- `.opencode/package.json` remains valid
- no unexpected removals occur in local OpenCode state/cache paths

### Runtime Verification In A Test Repo

1. sync the `opencode` target
2. restart OpenCode
3. run `/handoff continue implementing X`
4. verify a new session opens with an editable prompt draft
5. verify relevant `@file` references are present
6. send the draft in the new session
7. verify referenced repo-local files are injected as synthetic read-like content
8. call `read_handoff_session`
9. verify it can read the source session transcript
10. verify it rejects arbitrary unrelated session IDs

### Important Failure Cases To Test

- handoff prompt with no file references
- handoff prompt with invalid or missing file references
- file reference attempting path traversal outside repo root
- new session without stored source-session mapping
- source session deleted before follow-up read

## Implementation Sequence

1. create `src/opencode/plugins/compass-handoff/`
2. vendor the upstream runtime files
3. add the top-level `src/opencode/plugins/compass-handoff.ts` shim
4. rewrite the handoff command template for Compass continuity requirements
5. rename and constrain transcript-reading behavior
6. add repo-root path safety around file injection
7. update validation for new required files
8. run validate/build/push dry-run
9. smoke-test in one downstream repo

## Recommended Pilot Outcome

For pilot 1, the wrapper should deliver only this:

- Compass-aware `/handoff` prompt generation
- editable new-session draft creation
- repo-local synthetic file loading
- source-session-only transcript retrieval
- deterministic install through Compass Engine

Everything else should remain out of scope until this baseline proves useful.

## Sources

- OpenCode plugins docs: https://opencode.ai/docs/plugins/
- Upstream README: https://github.com/joshuadavidthomas/opencode-handoff
- Upstream source:
  - `src/plugin.ts`
  - `src/tools.ts`
  - `src/files.ts`
  - `src/vendor.ts`
  - `package.json`
- Local strategy: `docs/architecture/opencode-plugin-strategy.md`
- Local development rules: `docs/development/opencode/plugin-development.md`
