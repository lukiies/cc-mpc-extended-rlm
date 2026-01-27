@echo off
REM =============================================================================
REM Enhanced RLM MCP Server - Auto-Pull Launcher (Windows)
REM =============================================================================
REM This script ensures the MCP server is always running the latest version by:
REM 1. Pulling the latest changes from GitHub
REM 2. Starting the MCP server
REM
REM Note: Push happens when user accepts self-learning updates during session
REM
REM Usage: start_server.bat --path C:\path\to\your\project
REM =============================================================================

cd /d "%~dp0"

REM Step 1: Pull latest from GitHub
git fetch origin 2>nul
git merge --ff-only origin/main 2>nul

REM Step 2: Start the MCP server
"%~dp0.venv\Scripts\python.exe" -m enhanced_rlm.server %*
