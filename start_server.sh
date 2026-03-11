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
# Load secrets (API keys, etc.) from ~/.secrets/.env
# -----------------------------------------------------------------------------
# IMPORTANT: The Claude Code CLI may spawn this process with a minimal
# environment where $HOME is not set. We resolve HOME from the passwd database
# as a fallback. The .mcp.json "env": {} field and "set -a; source" tricks
# do NOT reliably pass environment variables to the spawned process.
# Loading secrets HERE in the script is the only reliable method.
# -----------------------------------------------------------------------------
_resolve_home() {
    if [[ -n "$HOME" ]]; then
        echo "$HOME"
    else
        getent passwd "$(whoami)" 2>/dev/null | cut -d: -f6
    fi
}

_REAL_HOME="$(_resolve_home)"
if [[ -n "$_REAL_HOME" && -f "$_REAL_HOME/.secrets/.env" ]]; then
    set -a
    source "$_REAL_HOME/.secrets/.env"
    set +a
    log "Loaded secrets from $_REAL_HOME/.secrets/.env"
else
    log "WARNING: No secrets file found at $_REAL_HOME/.secrets/.env"
fi

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
# Step 2: Run the pull operation in the BACKGROUND (non-blocking)
# -----------------------------------------------------------------------------
# IMPORTANT: git pull MUST NOT block server startup.
# The VSCode extension polls MCP status within ~3 seconds of launching a chat.
# If the server takes >3s to start, the extension gives up and shows
# "No running MCP servers." Git fetch alone takes 1-2s, which pushes total
# startup past the threshold. Running it in the background fixes this.
# -----------------------------------------------------------------------------
(
    log "Starting background git pull..."
    pull_latest
    log "Background git pull completed."
) &

log "Starting MCP server (git pull running in background)..."

# -----------------------------------------------------------------------------
# Step 3: Start the MCP server IMMEDIATELY
# -----------------------------------------------------------------------------
exec "$SCRIPT_DIR/.venv/bin/python" -m enhanced_rlm.server "$@"
