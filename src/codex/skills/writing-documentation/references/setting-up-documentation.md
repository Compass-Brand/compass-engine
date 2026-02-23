# Setting Up Documentation

## Overview
Documentation structure should match the project's size, audience, and tooling. Don't over-engineer a docs folder for a small library, and don't dump everything in the root for a large application. Investigate the project first, then recommend.

## Process
1. Investigate the project (size, language, framework, team size, existing docs)
2. Recommend a documentation pattern based on what you find
3. Ask for confirmation, then scaffold

## Documentation Patterns

### Pattern 1: Root-Level Only
**Best for:** Small libraries, focused tools, single-purpose projects

```
project/
├── README.md
├── CONTRIBUTING.md          # if accepting contributions
├── CHANGELOG.md             # if publishing releases
├── LICENSE
└── CODE_OF_CONDUCT.md      # if community-facing
```

**When to recommend:** Project has a single clear purpose, documentation fits in one README, no complex setup or architecture to document.

### Pattern 2: Docs Folder
**Best for:** Applications, services, multi-component projects with substantial documentation needs

```
project/
├── docs/
│   ├── getting-started/         # tutorials for new users
│   │   ├── installation.md
│   │   └── quickstart.md
│   ├── guides/                  # how-to guides
│   │   └── [topic].md
│   ├── reference/               # API and config reference
│   │   └── [topic].md
│   ├── architecture/            # technical design
│   │   ├── overview.md
│   │   ├── decisions/           # ADRs
│   │   │   └── 0001-[title].md
│   │   └── diagrams/
│   └── assets/
│       └── images/
├── README.md                    # project overview (always at root)
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
└── CODE_OF_CONDUCT.md
```

**When to recommend:** Project has multiple audiences (users, contributors, operators), complex setup, architecture worth documenting, or uses a docs-as-code workflow.

**Organization approaches:**
- **By content type** (recommended default): `getting-started/`, `guides/`, `reference/`, `architecture/`, `explanation/` — aligns with Diataxis framework
- **By audience**: `user/`, `admin/`, `developer/` — works for platforms with distinct user roles (GitLab uses this)
- **By feature/module**: `auth/`, `payments/`, `notifications/` — works for large systems with clear domain boundaries

**Index files:** Every directory should have an index.md that introduces the topic and links to child pages.

### Pattern 3: External Docs Site
**Best for:** Large frameworks, platforms with extensive user documentation

```
project/
├── docs/                        # source for docs site
│   ├── docusaurus.config.js     # or mkdocs.yml, .vitepress/config.js
│   ├── docs/                    # markdown content
│   └── static/                  # images, downloads
├── README.md                    # points to docs site URL
├── CONTRIBUTING.md
└── ...
```

**Static site generators:**
- **Docusaurus** — React ecosystem, MDX support, versioning built-in
- **VitePress** — Vue ecosystem, lightweight, fast builds
- **MkDocs Material** — Python ecosystem, simplest setup, YAML config

**When to recommend:** Docs are a product unto themselves, need search, versioning, or custom UI. Typically for OSS frameworks with large user bases.

## Monorepo Documentation

**Centralized** — Single `docs/` at root for tightly coupled, single-team projects:
```
monorepo/
├── docs/                        # all docs here
│   ├── architecture/
│   └── guides/
└── packages/
    ├── package-a/
    │   └── README.md            # package-specific overview
    └── package-b/
        └── README.md
```

**Per-package** — Each package owns its docs for multi-team, loosely coupled projects:
```
monorepo/
├── docs/                        # shared overview + architecture only
│   └── architecture/
└── packages/
    ├── package-a/
    │   ├── docs/                # package-specific docs
    │   └── README.md
    └── package-b/
        ├── docs/
        └── README.md
```

**Principle:** Mirror your org structure. Single team → centralized. Multiple teams → per-package.

## Multi-Repo / Polyrepo Documentation

**Pattern: Each repo self-contained + central hub**
- Each repo has its own `docs/` and README (self-documenting)
- A dedicated "docs repo" or site aggregates and links to individual repos
- Cross-repo architecture docs (system overview, integration points) live in the hub
- ADRs: component-level decisions in each repo, system-level decisions in the hub

**Pattern: Submodule-based centralization**
- Central docs repo pulls in each repo's `docs/` folder as a git submodule
- MkDocs Material mono-repo plugin works with submodules
- Tradeoff: keeps docs near code, but submodule management adds friction

**Pattern: Build-time aggregation (no submodules)**
- Tools like `mkdocs-multirepo-plugin` pull docs from multiple repos at build time
- Antora does the same for Asciidoctor-based docs
- Lower friction than submodules, requires build-time network access

**Always document the strategy itself** — teams need to know how to update, build, and contribute to the docs system.

## Root-Level Files

GitHub recognizes these files in order: root → `.github/` → `docs/`

| File | Location | Required? |
|------|----------|-----------|
| `README.md` | Root (must be here) | Yes — every project |
| `LICENSE` | Root (must be here for GitHub recognition) | Yes — OSS projects |
| `CONTRIBUTING.md` | Root preferred | Yes — if accepting contributions |
| `CODE_OF_CONDUCT.md` | Root or `.github/` | Recommended for community projects |
| `SECURITY.md` | Root or `.github/` | Recommended for all projects |
| `CHANGELOG.md` | Root | Recommended if publishing releases |
| `CODEOWNERS` | Root or `.github/` | Recommended for team projects |

## AI Context Files

AI context files are NOT documentation — they guide AI behavior, not humans. Always at project root, never inside `docs/`.

```
project/
├── CLAUDE.md                    # Claude Code context
├── AGENTS.md                    # tool-agnostic AI context (emerging standard)
├── .cursorrules                 # Cursor editor context
├── .github/
│   └── instructions/            # GitHub Copilot instructions
├── docs/                        # human documentation (separate concern)
└── README.md
```

**Nested AI context files** (e.g., CLAUDE.md in subdirectories) provide component-specific guidance when AI works in those directories.

## Assets and Images

**Location options:**
- `docs/assets/images/` — shared across all docs (recommended default)
- Co-located with content — `docs/guides/images/` next to related guide
- `docs/assets/diagrams/` — separate folder for diagram source files

**File formats:**
- SVG for diagrams and logos (vector, scales cleanly)
- PNG for screenshots (lossless)
- JPG for photos (compressed)

**Best practices:**
- Descriptive file names: `architecture-overview.svg` not `diagram1.svg`
- Keep source files (`.pptx`, `.sketch`) alongside exports for future editing
- Prefer Mermaid diagrams in markdown over external image files

## Scaffolding Checklist

After deciding on a pattern, scaffold with:
- [ ] Create directory structure
- [ ] Add index.md to each docs directory
- [ ] Create README.md at root
- [ ] Add LICENSE file
- [ ] Add CONTRIBUTING.md if needed
- [ ] Add CLAUDE.md / AGENTS.md if using AI tools
- [ ] Set up .gitignore for auto-generated docs
- [ ] Configure static site generator if using one
