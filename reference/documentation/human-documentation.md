# Documentation Basics

## Rules
- Every docs level should contain a README.md giving an explanation for the folder and an index at that level.

## Structure

### Root
```
├── READEME.md                                          #
├── CONTRIBUTING.md                                     #
├── CHANGELOG.md                                        #
├── LICENSE.md                                          #
├── CODE_OF_CONDUCT.md                                  #
```

### Docs Folder

```
$project/
├── docs/
    ├── getting-started/                                # tutorials for new users or developers
        ├── installation.md                             # how to install for either user or developer
        ├── quickstart.md                               # how to start and do basic tasks for either user or developer
    ├── guides/                                         # how-to guides
        ├── [$topic]                                    # specific per topic
    ├── reference/                                      # API and config reference
        ├── [$topic]                                    # specifc per topic
    ├── architecture/                                   # technical design
        ├── system-overview.md                          # high-level description of the entire system.
        ├── decisions/                                  # ADRs
            ├── [0001-$topic]                           # specific per topic
        ├── component-deep-dives/                       # detailed documentation for individual services or modules.
            ├── [0001-$topic]                           # specific per topic
        ├── diagrams/                                   # flow, connection, etc diagrams
        ├── structure/                                  # project structure documentation
    ├── development/                                    # development guide lines
        ├── overview.md                                 # common, high-level development rules and guidelines
        ├── [$topic]/                                   # specific development guidelines per topic
            ├── [development notes for parent topic]    # 
    ├── brand/                                          # brand information and guidelines
        ├── information/                                # specific information per brand such as brand guidelines
        ├── logos/                                      # logos for different parts of the brand
```

## Topic Examples

### By Audience
- `user/`
- `admin/`
- `developer/`

### By Module
- `auth/`
- `payments/`
- `notifications/`

## Strategy

### Multi-Repo / Polyrepo Documentation

**Pattern: Each repo self-contained + central hub**
- Each repo has its own `docs/` and README (self-documenting)
- A dedicated "docs repo" or site aggregates and links to individual repos
- Cross-repo architecture docs (system overview, integration points) live in the hub
- ADRs: component-level decisions in each repo, system-level decisions in the hub

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

## Assets and Images

**File formats:**
- SVG for diagrams and logos (vector, scales cleanly)
- PNG for screenshots (lossless)
- JPG for photos (compressed)

**Best practices:**
- Descriptive file names: `architecture-overview.svg` not `diagram1.svg`
- Keep source files (`.pptx`, `.sketch`) alongside exports for future editing
- Prefer Mermaid diagrams in markdown over external image files