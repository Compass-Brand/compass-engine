---
name: beads-tree
description: Display the Beads issue dependency tree for the current repository
---

# Beads Dependency Tree

Display the Beads issue dependency tree for the current repository.

## Usage

```bash
bd dep tree
```

## Output

Shows an ASCII tree of all issues and their dependencies:

```text
bd-0001 [Epic] User Authentication System
├── bd-0001.1 [Feature] OAuth2 Implementation
│   ├── bd-0001.1.1 [Task] Add refresh token logic
│   └── bd-0001.1.2 [Task] Implement token storage
└── bd-0001.2 [Feature] Session Management
    └── bd-0001.2.1 [Task] Redis session store
```

## Prerequisites

- Beads CLI must be installed: `go install github.com/steveyegge/beads/cmd/bd@latest`
- Repository must be initialized: `bd init`

## Integration

This command integrates with:

- Forgetful Memory: Query for issue context
- Serena: Find issue references in code
- `/resolve-pr-reviews`: Link review issues to Beads

## Fallback

If Beads is not installed, display installation instructions:

```bash
echo "Beads is not installed. Install with:"
echo "  go install github.com/steveyegge/beads/cmd/bd@latest"
echo ""
echo "Then initialize:"
echo "  bd init && bd setup claude"
```
