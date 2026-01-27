#!/bin/bash
# =============================================================================
# Enhanced RLM MCP Server - Auto-Sync Launcher
# =============================================================================
# This script ensures the MCP server is always running the latest version by:
# 1. Committing and pushing any local changes (from self-learning protocol)
# 2. Pulling the latest changes from GitHub
# 3. Starting the MCP server
#
# Usage: ./start_server.sh --path /path/to/your/project
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="$SCRIPT_DIR/.sync.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Truncate log if > 100KB to prevent infinite growth
if [[ -f "$LOG_FILE" ]] && [[ $(stat -c%s "$LOG_FILE" 2>/dev/null || stat -f%z "$LOG_FILE" 2>/dev/null) -gt 102400 ]]; then
    tail -100 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

log "=== MCP Server startup initiated ==="

# -----------------------------------------------------------------------------
# Step 1: Commit and push any local changes (self-learning protocol updates)
# -----------------------------------------------------------------------------
sync_local_changes() {
    # Check if we're in a git repository
    if ! git rev-parse --is-inside-work-tree &>/dev/null; then
        log "WARNING: Not a git repository, skipping sync"
        return 0
    fi

    # Check for uncommitted changes
    if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
        log "Found local changes, committing..."

        # Stage all changes
        git add -A

        # Create commit with auto-generated message
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local hostname=$(hostname 2>/dev/null || echo "unknown")
        git commit -m "Auto-sync: Self-learning updates from $hostname at $timestamp" \
                   -m "Automated commit by start_server.sh" \
                   --author="Claude Code Auto-Sync <noreply@anthropic.com>" 2>/dev/null || {
            log "WARNING: Commit failed (possibly no changes to commit)"
        }

        # Push to remote
        if git push origin HEAD 2>/dev/null; then
            log "Successfully pushed local changes to GitHub"
        else
            log "WARNING: Push failed - will retry on next startup"
            # Don't fail - we can still run with local changes
        fi
    else
        log "No local changes to commit"
    fi
}

# -----------------------------------------------------------------------------
# Step 2: Pull latest changes from GitHub
# -----------------------------------------------------------------------------
pull_latest() {
    if ! git rev-parse --is-inside-work-tree &>/dev/null; then
        return 0
    fi

    log "Fetching latest from origin..."

    if git fetch origin 2>/dev/null; then
        # Get current branch
        local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

        # Try fast-forward merge
        if git merge --ff-only "origin/$branch" 2>/dev/null; then
            log "Successfully pulled latest changes from origin/$branch"
        else
            log "WARNING: Fast-forward merge not possible - local changes may diverge"
            # Don't fail - we can still run with local version
        fi
    else
        log "WARNING: Fetch failed (network issue?) - running with current version"
    fi
}

# -----------------------------------------------------------------------------
# Step 3: Run the sync operations
# -----------------------------------------------------------------------------
log "Starting git sync..."

# First push any local changes
sync_local_changes

# Then pull latest from remote
pull_latest

log "Git sync completed, starting MCP server..."

# -----------------------------------------------------------------------------
# Step 4: Start the MCP server
# -----------------------------------------------------------------------------
exec "$SCRIPT_DIR/.venv/bin/python" -m enhanced_rlm.server "$@"
