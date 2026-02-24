# Writing READMEs

## Overview

READMEs answer questions your audience will have. Different audiences need different information. Always investigate the project before asking questions — scan the codebase, then recommend.

## Process

### Step 1: Investigate the Project

Before asking anything, scan:

- Package files (package.json, Cargo.toml, pyproject.toml, etc.)
- Existing README or docs
- Folder structure and main source files
- Git history for project maturity

### Step 2: Identify the Task

| Task          | When                                                              |
| ------------- | ----------------------------------------------------------------- |
| **Creating**  | New project, no README yet                                        |
| **Adding**    | Need to document something new                                    |
| **Updating**  | Capabilities changed, content is stale                            |
| **Reviewing** | Route to the reviewing-documentation workflow with README context |

### Step 3: Recommend Project Type

Based on investigation, recommend one of:

| Type            | Audience                      | Key Sections                             | Template                              |
| --------------- | ----------------------------- | ---------------------------------------- | ------------------------------------- |
| **Open Source** | Contributors, users worldwide | Install, Usage, Contributing, License    | `assets/templates/readme-oss.md`      |
| **Personal**    | Future you, portfolio viewers | What it does, Tech stack, Learnings      | `assets/templates/readme-personal.md` |
| **Internal**    | Teammates, new hires          | Setup, Architecture, Runbooks            | `assets/templates/readme-internal.md` |
| **Config**      | Future you (confused)         | What's here, Why, How to extend, Gotchas | `assets/templates/readme-config.md`   |

Present your recommendation with reasoning. Ask the user to confirm or adjust.

### Step 4: Task-Specific Questions

Only ask what you couldn't determine from investigation.

**Creating initial README:**

1. What problem does this solve in one sentence?
2. What's the quickest path to "it works"?
3. Anything notable to highlight?

**Adding a section:**

1. What needs documenting?
2. Where should it go in the existing structure?
3. Who needs this info most?

**Updating existing content:**

1. What changed?
2. Read current README, identify stale sections
3. Propose specific edits

### Step 5: Essential Sections (All Types)

Every README needs at minimum:

1. **Name** — Self-explanatory title
2. **Description** — What + why in 1-2 sentences
3. **Usage** — How to use it (examples help)

For full section guidance by type, see the section-checklist in this references directory

## Modern Best Practices

### AI Companion Files

Recommend CLAUDE.md / AGENTS.md alongside the README. README serves humans; context files serve AI agents. Place AI files at project root, not inside docs/.

### Visual Demos

For UI-heavy projects, recommend animated GIFs or screenshots. GitHub renders GIFs inline (10MB cap). Tools: ScreenToGif, Gifski, Peek.

### Badge Discipline

Only include badges that convey meaningful info. Avoid badge saturation. Common badges: build status, version, license, coverage.

### Drift Prevention

- Include "last reviewed" date for config and internal READMEs
- Recommend CI-based link checking (markdown-link-check, lychee)
- Suggest readme-sync or similar tools for generated sections

### Companion Files (OSS)

For open source projects, recommend these alongside the README:

- CONTRIBUTING.md — how to contribute
- CODE_OF_CONDUCT.md — community standards
- CHANGELOG.md — version history
- LICENSE — license file

### After Drafting

Always ask: "Anything else to highlight or include that I might have missed?"
