# Quickstart

Last reviewed: 2026-02-23

Use this for the fastest path to validate your local setup.

If this is your first session in this repo, run:

```bash
bd onboard
```

## Run the full gate

```bash
npm run check
```

Expected result:

- validation passes
- build succeeds
- push dry-run succeeds for `claude,codex,opencode,github,root`

## Build and sync selectively

```bash
npm run build
npm run push -- --dry-run --targets github
```

## Typical development loop

```bash
bd ready
bd show <id>
bd update <id> --status in_progress
npm run check
```
