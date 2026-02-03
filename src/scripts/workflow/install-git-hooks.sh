#!/bin/bash
# install-git-hooks.sh
# Installs git hooks for smart .claude sync in compass-brand
#
# Usage: ./install-git-hooks.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

# Verify this is a Git repository before proceeding
if ! git -C "$REPO_ROOT" rev-parse --show-toplevel &>/dev/null; then
    echo "Error: $REPO_ROOT is not a Git repository" >&2
    exit 1
fi

HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "📦 Installing git hooks for smart .claude sync..."

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# === POST-MERGE HOOK ===
# Triggers after: git pull, git merge
cat > "$HOOKS_DIR/post-merge" << 'HOOK_EOF'
#!/bin/bash
set -euo pipefail
# post-merge hook: Smart sync .claude after pull/merge
# Only syncs if .claude/ content changed

REPO_ROOT="$(git rev-parse --show-toplevel)"

# Resolve base ref with fallback if ORIG_HEAD doesn't exist
if git rev-parse --verify ORIG_HEAD &>/dev/null; then
    BASE_REF="ORIG_HEAD"
elif git rev-parse --verify HEAD~1 &>/dev/null; then
    BASE_REF="HEAD~1"
else
    # No valid base ref available, skip check
    exit 0
fi

# Check if .claude files changed in the merge
CHANGED_FILES=$(git diff-tree -r --name-only --no-commit-id "$BASE_REF" HEAD 2>/dev/null || echo "")

if echo "$CHANGED_FILES" | grep -q "^\.claude/"; then
    echo ""
    echo "🔄 Hub .claude/ content changed - syncing to projects..."
    SYNC_SCRIPT="$REPO_ROOT/sync-claude-hub.sh"
    if [ -f "$SYNC_SCRIPT" ] && [ -x "$SYNC_SCRIPT" ]; then
        "$SYNC_SCRIPT" --force
    else
        echo "⚠️  Warning: sync-claude-hub.sh not found or not executable at $SYNC_SCRIPT"
    fi
fi
HOOK_EOF
chmod +x "$HOOKS_DIR/post-merge"
echo "   ✅ post-merge hook installed"

# === POST-CHECKOUT HOOK ===
# Triggers after: git checkout, git switch
cat > "$HOOKS_DIR/post-checkout" << 'HOOK_EOF'
#!/bin/bash
set -euo pipefail
# post-checkout hook: Smart sync .claude after branch switch
# Only syncs if switching branches (not file checkout)

REPO_ROOT="$(git rev-parse --show-toplevel)"
OLD_REF=${1:-}
NEW_REF=${2:-}
BRANCH_CHECKOUT=${3:-0}  # 1 = branch checkout, 0 = file checkout

# Only run on branch checkout
if [ "$BRANCH_CHECKOUT" != "1" ]; then
    exit 0
fi

# Validate refs before running git diff
# Check for null refs (all zeros) or empty refs
is_valid_ref() {
    local ref="$1"
    [ -n "$ref" ] && [ "$ref" != "0000000000000000000000000000000000000000" ] && git rev-parse --verify "$ref" &>/dev/null
}

if ! is_valid_ref "$OLD_REF" || ! is_valid_ref "$NEW_REF"; then
    # Invalid refs, skip the diff check
    exit 0
fi

# Check if .claude files differ between old and new ref
CHANGED_FILES=$(git diff --name-only "$OLD_REF" "$NEW_REF" 2>/dev/null || echo "")

if echo "$CHANGED_FILES" | grep -q "^\.claude/"; then
    echo ""
    echo "🔄 Hub .claude/ content differs on this branch - syncing to projects..."
    "$REPO_ROOT/sync-claude-hub.sh" --force
fi
HOOK_EOF
chmod +x "$HOOKS_DIR/post-checkout"
echo "   ✅ post-checkout hook installed"

# === POST-COMMIT HOOK ===
# Triggers after: git commit
cat > "$HOOKS_DIR/post-commit" << 'HOOK_EOF'
#!/bin/bash
set -euo pipefail
# post-commit hook: Smart sync .claude after commit
# Only syncs if .claude/ files were in the commit

REPO_ROOT="$(git rev-parse --show-toplevel)"

# Check if .claude files were in this commit
CHANGED_FILES=$(git diff-tree -r --name-only --no-commit-id HEAD 2>/dev/null || echo "")

if echo "$CHANGED_FILES" | grep -q "^\.claude/"; then
    echo ""
    echo "🔄 Hub .claude/ content committed - syncing to projects..."
    "$REPO_ROOT/sync-claude-hub.sh" --force
fi
HOOK_EOF
chmod +x "$HOOKS_DIR/post-commit"
echo "   ✅ post-commit hook installed"

echo ""
echo "✨ Git hooks installed!"
echo ""
echo "Hooks will automatically sync .claude/ to projects when:"
echo "   • You pull/merge changes that modify .claude/"
echo "   • You switch to a branch with different .claude/ content"
echo "   • You commit changes to .claude/"
echo ""
echo "Manual sync: ./sync-claude-hub.sh"
echo "Force sync:  ./sync-claude-hub.sh --force"
