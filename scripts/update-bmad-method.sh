#!/bin/bash
# Update BMAD-METHOD submodule and show changes
#
# Usage: ./scripts/update-bmad-method.sh [--apply]
#   Without --apply: Shows what changes are available (dry run)
#   With --apply: Actually updates the submodule and commits

set -e

cd "$(dirname "$0")/.."

echo "=== BMAD-METHOD Update Script ==="
echo ""

cd BMAD-METHOD

# Fetch latest from upstream
echo "Fetching upstream changes..."
git fetch origin main

# Get current and upstream commits
CURRENT=$(git rev-parse HEAD)
UPSTREAM=$(git rev-parse origin/main)

if [ "$CURRENT" == "$UPSTREAM" ]; then
    echo ""
    echo "✅ BMAD-METHOD is already up to date!"
    echo "   Current: ${CURRENT:0:7}"
    exit 0
fi

echo ""
echo "📦 Updates available!"
echo "   Current: ${CURRENT:0:7}"
echo "   Upstream: ${UPSTREAM:0:7}"
echo ""

# Show the changelog
echo "=== Commits ==="
git log --oneline $CURRENT..$UPSTREAM
echo ""

echo "=== Changed Files ==="
git diff --stat $CURRENT..$UPSTREAM
echo ""

# Check if we should apply the update
if [ "$1" == "--apply" ]; then
    echo "=== Applying Update ==="
    git checkout origin/main
    cd ..
    git add BMAD-METHOD
    git commit -m "Update BMAD-METHOD submodule to ${UPSTREAM:0:7}

Changes from ${CURRENT:0:7}:
$(cd BMAD-METHOD && git log --oneline $CURRENT..$UPSTREAM)"
    echo ""
    echo "✅ BMAD-METHOD updated and committed!"
    echo "   Run 'git push' to push the changes."
else
    echo "=== Dry Run ==="
    echo "To apply this update, run:"
    echo "  ./scripts/update-bmad-method.sh --apply"
fi
