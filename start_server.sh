#!/bin/bash
# =============================================================================
# Enhanced RLM MCP Server - Auto-Pull Launcher
# =============================================================================
# This script ensures the MCP server is always running the latest version by:
# 1. Pulling the latest changes from GitHub
# 2. Starting the MCP server
#
# Note: Push happens when user accepts self-learning updates during session
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
# Platform detection (for debugging .mcp.json configuration issues)
# -----------------------------------------------------------------------------
detect_platform() {
    if [[ -f /proc/version ]] && grep -qi microsoft /proc/version 2>/dev/null; then
        if [[ -n "$WSL_DISTRO_NAME" ]]; then
            log "Platform: WSL ($WSL_DISTRO_NAME) - use 'bash -c' in .mcp.json (NOT wsl.exe)"
        else
            log "Platform: WSL - use 'bash -c' in .mcp.json (NOT wsl.exe)"
        fi
    elif [[ "$(uname)" == "Darwin" ]]; then
        log "Platform: macOS - use start_server.sh directly in .mcp.json"
    else
        log "Platform: Linux - use start_server.sh directly in .mcp.json"
    fi
}

detect_platform

# -----------------------------------------------------------------------------
# Step 1: Pull latest changes from GitHub
# -----------------------------------------------------------------------------
pull_latest() {
    if ! git rev-parse --is-inside-work-tree &>/dev/null; then
        log "WARNING: Not a git repository, skipping pull"
        return 0
    fi

    log "Fetching latest from origin..."

    if git fetch origin >/dev/null 2>&1; then
        # Get current branch
        local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

        # Try fast-forward merge (stdout MUST be silenced - MCP uses stdio)
        if git merge --ff-only "origin/$branch" >/dev/null 2>&1; then
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
# Step 2: Run the pull operation
# -----------------------------------------------------------------------------
log "Starting git pull..."

pull_latest

log "Git pull completed, starting MCP server..."

# -----------------------------------------------------------------------------
# Step 3: Start the MCP server
# -----------------------------------------------------------------------------
exec "$SCRIPT_DIR/.venv/bin/python" -m enhanced_rlm.server "$@"
