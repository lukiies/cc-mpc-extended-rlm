# VS Code Remote SSH + Claude Code: Persistent Background Work Guide

## The Goal

Run Claude Code tasks via VS Code GUI chat on a remote server, close laptop lid, and come back later to find work completed.

## Architecture

```
Laptop (VS Code client) ──SSH──> Remote Server (VS Code Server)
                                    ├── Extension Host
                                    │   └── Claude Code extension
                                    │       └── claude binary (stream-json)
                                    ├── ptyHost (terminals)
                                    └── fileWatcher
```

When SSH connection drops (lid close), the VS Code Server keeps running on the remote machine with a configurable **reconnection grace period** (default 3h).

## Proven: Background Work Survives Lid Close

**Tested and confirmed:** When using VS Code Remote SSH:
- Background bash commands keep running during disconnection (zero gaps in timestamps)
- Background Claude Code agents keep working (zero gaps in work output)
- VS Code Server has a reconnection grace period (default 3h, configurable up to 12h+)
- On reconnect, the chat session resumes with full context

### How to run background work

From the Claude Code VS Code chat, use background agents:
```
# In Claude's tool calls:
Task(run_in_background=true, ...)   # Background agent
Bash(run_in_background=true, ...)   # Background command
```

The user can then close the laptop lid and come back later. Check results with:
- `TaskOutput(task_id=..., block=false)` to check agent progress
- Read output files to see results

## Critical: Disconnect Types

| Event | Server behavior | Background work |
|-------|----------------|-----------------|
| **Lid close** (network drop) | Waits for reconnection (grace period) | **CONTINUES** |
| **"Reload Window"** | Graceful disconnect → kills extension host | **DIES** |
| **VS Code update** | Kills server, starts new one | **DIES** |

**Key log signatures:**
```
# Network drop (GOOD - work continues):
"The client has disconnected, will wait for reconnection 3h before disposing..."

# Window reload (BAD - kills everything):
"The client has disconnected gracefully, so the connection will be disposed."
```

## Configuration: Extend Reconnection Grace Period

The default 3h grace period can be extended. The `VSCODE_RECONNECTION_GRACE_TIME` env var is **set by the server**, not read from environment. The only reliable method is the `--reconnection-grace-time` CLI argument.

### Step 1: Patch the server launch script

Create `~/.vscode-server/patch-grace-time.sh`:
```bash
#!/bin/bash
# Auto-patch VS Code Server reconnection grace time
# Usage: patch-grace-time.sh [seconds]
# Default: 43200 (12 hours)
GRACE_SECONDS=${1:-43200}
for script in ~/.vscode-server/cli/servers/*/server/bin/code-server; do
  if [ -f "$script" ] && ! grep -q "reconnection-grace-time" "$script"; then
    sed -i "s|\"\\$ROOT/node\" \${INSPECT:-} \"\\$ROOT/out/server-main.js\" \"\\$@\"|\"\\$ROOT/node\" \${INSPECT:-} \"\\$ROOT/out/server-main.js\" --reconnection-grace-time $GRACE_SECONDS \"\\$@\"|" "$script"
    echo "Patched: $script"
  else
    echo "Already patched or not found: $script"
  fi
done
```

### Step 2: Make it survive VS Code updates

**Option A: systemd path watcher (recommended)**

```bash
# ~/.config/systemd/user/vscode-patch-grace-time.service
[Unit]
Description=Patch VS Code Server reconnection grace time

[Service]
Type=oneshot
ExecStart=/home/USER/.vscode-server/patch-grace-time.sh

# ~/.config/systemd/user/vscode-patch-grace-time.path
[Unit]
Description=Watch for new VS Code Server installations

[Path]
PathChanged=/home/USER/.vscode-server/cli/servers/
Unit=vscode-patch-grace-time.service

[Install]
WantedBy=default.target
```

Enable:
```bash
systemctl --user daemon-reload
systemctl --user enable --now vscode-patch-grace-time.path
```

**Option B: Cron job (backup/alternative)**
```bash
0 * * * * ~/.vscode-server/patch-grace-time.sh >> /tmp/vscode-patch.log 2>&1
```

### Step 3: Activate after patching

After patching, you must kill the old server for the new setting to take effect:
```bash
pkill -f "server-main.js"
```
Then reconnect from VS Code. Verify in logs:
```bash
grep "RECONNECTION" ~/.vscode-server/data/logs/$(ls -t ~/.vscode-server/data/logs/ | head -1)/remoteagent.log | tail -1
# Should show: VSCODE_RECONNECTION_GRACE_TIME=43200000ms (43200s)
```

## What Does NOT Work (Investigated)

| Approach | Why it fails |
|----------|-------------|
| `VSCODE_RECONNECTION_GRACE_TIME` in `~/.bashrc` | `.bashrc` has non-interactive guard (`return` on line ~7) |
| `VSCODE_RECONNECTION_GRACE_TIME` in `~/.profile` | VS Code Server doesn't source `.profile` |
| `VSCODE_RECONNECTION_GRACE_TIME` in `/etc/environment` | Server overrides env var from its own config |
| `~/.vscode-server/server-env-setup` file | Known bug: not reliably sourced ([Issue #2917](https://github.com/microsoft/vscode-remote-release/issues/2917)) |
| VS Code settings (`remote.SSH.*`) | No setting exists for grace time |

**Only `--reconnection-grace-time` CLI argument works** (injected into `code-server` launch script).

## Server Requirements

Minimum specs for VS Code Server + Claude Code:

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 2 GB | 4 GB |
| CPU | 1 vCPU | 2 vCPU |
| Disk | 10 GB free | 15 GB free |

**Warning:** 1 GB RAM causes heavy swap usage (~1 GB in swap). Claude Code alone uses ~250 MB. VS Code Server + extensions use another ~200 MB. With 1 GB total, constant swapping makes everything 10-50x slower.

## Known Issues

- **[Claude Code #8570](https://github.com/anthropics/claude-code/issues/8570):** CLI stops working on terminal disconnect (v2.x regression). Does NOT affect VS Code extension with Remote SSH (different communication mechanism).
- **[Claude Code #13872](https://github.com/anthropics/claude-code/issues/13872):** Chat history can be lost on VS Code restart. Platform-level issue affecting all AI chat extensions.
- **[VS Code #10122](https://github.com/microsoft/vscode-remote-release/issues/10122):** "Reconnect without reload" feature request — not yet implemented.

## Quick Reference

```bash
# Check current grace time
grep "RECONNECTION" ~/.vscode-server/data/logs/$(ls -t ~/.vscode-server/data/logs/ | head -1)/remoteagent.log | tail -1

# Check VS Code Server processes
ps aux | grep -E "(server-main|extensionHost|claude)" | grep -v grep

# Check RAM/swap usage
free -h

# Force server restart (after patching)
pkill -f "server-main.js"

# Run patch manually
~/.vscode-server/patch-grace-time.sh

# Check systemd watcher status
systemctl --user status vscode-patch-grace-time.path
```
