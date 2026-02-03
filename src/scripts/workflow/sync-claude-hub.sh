#!/bin/bash
# sync-claude-hub.sh
# Smart sync of .claude content from compass_brand hub to child projects
#
# Features:
# - Auto-discovers projects (git submodules or directories with .claude/)
# - Syncs skills, agents, commands, and hooks
# - Preserves project-specific content (bmad/, local hooks)
# - Can be triggered by git hooks with change detection
#
# Usage:
#   ./sync-claude-hub.sh              # Sync all projects
#   ./sync-claude-hub.sh --check      # Check if sync needed (for git hooks)
#   ./sync-claude-hub.sh --force      # Force sync even if no changes detected
#   ./sync-claude-hub.sh --projects "proj1 proj2"  # Specific projects only

set -euo pipefail

HUB_PATH="$(cd "$(dirname "$0")" && pwd)"
HUB_CLAUDE="$HUB_PATH/.claude"
LAST_SYNC_FILE="$HUB_PATH/.claude-sync-hash"

# Parse arguments
CHECK_ONLY=false
FORCE_SYNC=false
SPECIFIC_PROJECTS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --check)
            CHECK_ONLY=true
            shift
            ;;
        --force)
            FORCE_SYNC=true
            shift
            ;;
        --projects)
            # Validate that an argument was provided and it's not another flag
            if [ -z "$2" ] || [[ "$2" == -* ]]; then
                echo "Error: --projects requires a space-separated list of project names" >&2
                echo "Usage: $0 --projects \"proj1 proj2\"" >&2
                exit 1
            fi
            SPECIFIC_PROJECTS="$2"
            shift 2
            ;;
        *)
            echo "Error: Unknown option: $1" >&2
            echo "Usage: $0 [--check] [--force] [--projects \"proj1 proj2\"]" >&2
            exit 1
            ;;
    esac
done

# Calculate hash of hub .claude content
get_hub_hash() {
    if [ -d "$HUB_CLAUDE" ]; then
        # Detect available hash command (md5sum on Linux, md5 -q on macOS)
        # Use array to safely handle multi-word commands like "md5 -q"
        local hash_cmd
        if command -v md5sum &> /dev/null; then
            hash_cmd=(md5sum)
        elif command -v md5 &> /dev/null; then
            hash_cmd=(md5 -q)
        else
            echo "no-hash-cmd"
            return
        fi
        # Sort files for deterministic ordering, then compute hash
        # Capture file list to avoid running xargs with no arguments when no files exist
        local files
        files=$(find "$HUB_CLAUDE" -type f | sort)
        if [ -z "$files" ]; then
            echo "empty"
            return
        fi
        # Use the detected hash_cmd for both the per-file hash and the final combined hash
        echo "$files" | xargs "${hash_cmd[@]}" 2>/dev/null | sort | "${hash_cmd[@]}" | cut -d' ' -f1
    else
        echo "empty"
    fi
}

# Check if sync is needed
check_sync_needed() {
    local current_hash
    current_hash=$(get_hub_hash)
    local last_hash=""

    if [ -f "$LAST_SYNC_FILE" ]; then
        last_hash=$(cat "$LAST_SYNC_FILE")
    fi

    if [ "$current_hash" != "$last_hash" ]; then
        return 0  # Sync needed
    else
        return 1  # No sync needed
    fi
}

# Save current hash after successful sync
save_sync_hash() {
    get_hub_hash > "$LAST_SYNC_FILE"
}

# Discover projects (git submodules or dirs with existing .claude)
discover_projects() {
    local projects=()

    # Method 1: Git submodules
    if [ -f "$HUB_PATH/.gitmodules" ]; then
        while IFS= read -r line; do
            if [[ $line =~ path[[:space:]]*=[[:space:]]*(.+) ]]; then
                local submodule="${BASH_REMATCH[1]}"
                # Skip mcps (infrastructure, not a project)
                if [ "$submodule" != "mcps" ] && [ -d "$HUB_PATH/$submodule" ]; then
                    projects+=("$submodule")
                fi
            fi
        done < "$HUB_PATH/.gitmodules"
    fi

    # Method 2: Directories with .claude folder (fallback/additional)
    for dir in "$HUB_PATH"/*/; do
        local dirname
        dirname=$(basename "$dir")
        # Skip hidden dirs, mcps, and already found
        if [[ ! "$dirname" =~ ^\. ]] && [ "$dirname" != "mcps" ]; then
            if [ -d "$dir/.claude" ] || [ -d "$dir/.git" ]; then
                # Check if not already in list (guard against empty array)
                # Using numeric boolean for shell idiom: 0=not found, 1=found
                local found=0
                if [ ${#projects[@]} -gt 0 ]; then
                    for p in "${projects[@]}"; do
                        if [ "$p" == "$dirname" ]; then
                            found=1
                            break
                        fi
                    done
                fi
                if [ "$found" -eq 0 ]; then
                    projects+=("$dirname")
                fi
            fi
        fi
    done

    # Output one project per line for safe array capture
    # Guard against empty array under set -u
    if [ ${#projects[@]} -gt 0 ]; then
        printf '%s\n' "${projects[@]}"
    fi
}

# Sync a single project
sync_project() {
    local project="$1"
    local project_path="$HUB_PATH/$project"
    local project_claude="$project_path/.claude"

    if [ ! -d "$project_path" ]; then
        echo "⏭️  Skipping $project (directory not found)"
        return
    fi

    echo ""
    echo "📁 Syncing to $project..."

    # Ensure .claude folder exists
    mkdir -p "$project_claude"

    # === SKILLS (full replace) ===
    if [ -d "$HUB_CLAUDE/skills" ]; then
        rm -rf "$project_claude/skills"
        cp -r "$HUB_CLAUDE/skills" "$project_claude/skills"
        local skill_count
        skill_count=$(find "$project_claude/skills" -maxdepth 1 -type d | wc -l | xargs)
        echo "   ✅ skills/ synced ($((skill_count - 1)) skills)"
    fi

    # === AGENTS (full replace) ===
    if [ -d "$HUB_CLAUDE/agents" ]; then
        rm -rf "$project_claude/agents"
        cp -r "$HUB_CLAUDE/agents" "$project_claude/agents"
        local agent_count
        agent_count=$(find "$project_claude/agents" -maxdepth 1 -type f -name "*.md" | wc -l | xargs)
        echo "   ✅ agents/ synced ($agent_count agents)"
    fi

    # === COMMANDS (merge - keep local folders, add hub files) ===
    if [ -d "$HUB_CLAUDE/commands" ]; then
        mkdir -p "$project_claude/commands"

        # Remove hub command files (but keep local folders like bmad/)
        # First, get list of hub command files
        for hub_cmd in "$HUB_CLAUDE/commands"/*.md; do
            if [ -f "$hub_cmd" ]; then
                local cmd_name
                cmd_name=$(basename "$hub_cmd")
                rm -f "$project_claude/commands/$cmd_name"
            fi
        done

        # Copy hub command files
        local cmd_count=0
        for hub_cmd in "$HUB_CLAUDE/commands"/*.md; do
            if [ -f "$hub_cmd" ]; then
                cp "$hub_cmd" "$project_claude/commands/"
                ((cmd_count++))
            fi
        done
        echo "   ✅ commands/ synced ($cmd_count commands, local folders preserved)"
    fi

    # === HOOK SCRIPTS (if any exist in .claude/hooks/) ===
    if [ -d "$HUB_CLAUDE/hooks" ]; then
        mkdir -p "$project_claude/hooks"

        # Copy hub hook scripts only if they don't exist locally
        local hooks_added=0
        local hooks_skipped=0
        for hub_hook in "$HUB_CLAUDE/hooks"/*; do
            if [ -f "$hub_hook" ]; then
                local hook_name
                hook_name=$(basename "$hub_hook")
                local project_hook="$project_claude/hooks/$hook_name"

                if [ ! -f "$project_hook" ]; then
                    cp "$hub_hook" "$project_hook"
                    ((hooks_added++))
                else
                    ((hooks_skipped++))
                fi
            fi
        done

        if [ $hooks_added -gt 0 ] || [ $hooks_skipped -gt 0 ]; then
            echo "   ✅ hooks/ scripts synced ($hooks_added added, $hooks_skipped local preserved)"
        fi
    fi

    # === SETTINGS.JSON (merge hooks from hub into project) ===
    # Hooks are configured in settings.json, not a hooks/ folder
    # Strategy: Merge hub hooks with project hooks (hub hooks take precedence for same event)
    if [ -f "$HUB_CLAUDE/settings.json" ]; then
        if [ ! -f "$project_claude/settings.json" ]; then
            # No project settings - just copy hub settings
            cp "$HUB_CLAUDE/settings.json" "$project_claude/settings.json"
            echo "   ✅ settings.json created from hub"
        else
            # Merge settings: combine env vars and hooks
            # Requires jq for JSON manipulation
            if command -v jq &> /dev/null; then
                local hub_settings="$HUB_CLAUDE/settings.json"
                local proj_settings="$project_claude/settings.json"
                local temp_settings="$project_claude/settings.json.tmp"

                # Deep merge strategy:
                # - env vars: shallow merge, project takes precedence
                # - hooks: combine arrays, dedupe by type+matcher (hub hooks first for precedence)
                # - other fields: project values preserved
                # Example: hub has SessionStart hook, project has StopHook -> both kept
                jq -s '
                    # Merge env vars (project takes precedence)
                    (.[0].env // {}) * (.[1].env // {}) as $merged_env |

                    # Merge hooks: for each event type, combine arrays (dedupe by type+matcher, hub hooks take precedence)
                    (.[0].hooks // {}) as $hub_hooks |
                    (.[1].hooks // {}) as $proj_hooks |
                    ($hub_hooks | keys) + ($proj_hooks | keys) | unique as $all_events |
                    (reduce $all_events[] as $event ({};
                        . + {($event): (
                            # Combine hub first (for precedence), then project hooks
                            # Dedupe by composite key of type + matcher
                            (($hub_hooks[$event] // []) + ($proj_hooks[$event] // []))
                            | reduce .[] as $hook ({};
                                (.[$hook.type + "::" + ($hook.matcher // "")] // null) as $existing |
                                if $existing == null then . + {($hook.type + "::" + ($hook.matcher // "")): $hook} else . end
                            )
                            | to_entries | map(.value)
                        )}
                    )) as $merged_hooks |

                    # Build final settings
                    (.[1] // {}) * {
                        env: $merged_env,
                        hooks: $merged_hooks
                    }
                ' "$hub_settings" "$proj_settings" > "$temp_settings" 2>/dev/null

                if [ -s "$temp_settings" ]; then
                    mv "$temp_settings" "$proj_settings"
                    echo "   ✅ settings.json merged (hooks combined)"
                else
                    rm -f "$temp_settings"
                    echo "   ⚠️  settings.json merge failed, keeping project settings"
                fi
            else
                echo "   ⚠️  jq not found - cannot merge settings.json hooks"
            fi
        fi
    fi
}

# Main execution
main() {
    # Check-only mode for git hooks
    if [ "$CHECK_ONLY" == "true" ]; then
        if check_sync_needed; then
            echo "SYNC_NEEDED"
            exit 0
        else
            echo "NO_SYNC_NEEDED"
            exit 0
        fi
    fi

    # Check if sync is needed (unless forced)
    if [ "$FORCE_SYNC" != "true" ]; then
        if ! check_sync_needed; then
            echo "✨ No changes in hub .claude/ - skipping sync"
            exit 0
        fi
    fi

    echo "🔄 Syncing .claude content from hub to projects..."
    echo "   Hub: $HUB_CLAUDE"

    # Get projects to sync
    local projects
    if [ -n "$SPECIFIC_PROJECTS" ]; then
        # shellcheck disable=SC2162
        read -a projects <<< "$SPECIFIC_PROJECTS"
    else
        mapfile -t projects < <(discover_projects)
    fi

    if [ ${#projects[@]} -eq 0 ]; then
        echo "⚠️  No projects found to sync"
        exit 0
    fi

    echo "   Projects: ${projects[*]}"

    # Sync each project
    for project in "${projects[@]}"; do
        sync_project "$project"
    done

    # Save hash for future comparisons
    save_sync_hash

    echo ""
    echo "✨ Sync complete!"
}

main
