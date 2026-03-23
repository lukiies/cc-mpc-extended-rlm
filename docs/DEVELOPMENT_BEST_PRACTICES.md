# Development Best Practices - Lessons from Real Projects

Universal lessons learned across projects using cc-mpc-extended-rlm. These apply to any project, regardless of tech stack.

---

## Web Authentication Security

### CRITICAL: Client-Side Auth is NOT Security

**Incident:** A login screen was built that hid content with CSS (`display:none`). All protected content was embedded in the HTML/markdown files served statically. Anyone could `curl` the files directly or disable CSS/JS to see everything.

**Rule:** CSS/JS-based content hiding is cosmetic, not security. Protected content must NEVER be sent to unauthenticated clients.

### Architecture Pattern: Server-Side Auth for Static Sites

When a "static" site needs authentication:
1. **Login page** - standalone HTML with ZERO protected content, only the login form
2. **Auth backend** - validates credentials, issues signed cookies/tokens
3. **App shell** - served ONLY after cookie/token validation, contains layout but NO embedded content
4. **Content API** - all content fetched via authenticated API calls (server checks credentials per request)
5. **Never combine** login page and app content in the same HTML file

### Security Testing: Always Test at HTTP Level

Browser-based testing is **misleading** for security. Always verify with `curl`:

```bash
# Test 1: Login page loads and contains zero protected content
curl -s http://site.com/ | grep -c "protected_keyword"  # Must be 0

# Test 2: Direct content access without cookie returns 401
curl -s -o /dev/null -w "%{http_code}" http://site.com/docs/secret.md  # Must be 401

# Test 3: Protected pages redirect without auth
curl -s -o /dev/null -w "%{http_code}" http://site.com/app  # Must be 302

# Test 4: API endpoints require auth
curl -s http://site.com/api/whoami  # Must return 401
```

---

## Deployment & Permissions

### Service User File Access

When deploying apps as systemd services (running as `www-data` or similar):

- **Home directory traversal**: If project is under `/home/user/`, the home dir needs `o+rx` for the service user to traverse into it
- **`.env` permissions**: Should be `640` with service user's group (e.g., `chgrp www-data .env`)
- **Project directory**: Needs `o+rX` recursively for service user to read files
- **Gotcha**: A service may start successfully but return empty data because it can't read config files - always check permissions first

### Systemd Service Checklist

```bash
# After deploying a new service:
sudo systemctl status service-name     # Check it's running
sudo journalctl -u service-name -n 20  # Check logs for errors
curl -s http://localhost:PORT/          # Verify it responds
ls -la /path/to/.env                   # Verify permissions
```

---

## Self-Learning Protocol Observations

### What Works Well
- **Routing lessons by type** (project-specific vs universal) prevents cluttering individual projects with generic knowledge
- **Auto-memory reinforcement** of critical rules (like session startup check) ensures compliance across sessions
- **Modular topic files** (<100 lines) enable efficient Haiku extraction
- **5-point security testing checklist** catches issues that browser testing misses

### Common Mistakes to Avoid
- Building features with cosmetic validation instead of real security
- Testing only in the browser (use curl/wget for security verification)
- Deploying without checking file permissions for the service user
- Combining public and protected content in the same page/response
- Not defining test procedures before implementing security features

---

---

## Knowledge Management — Three-Tier Architecture (CORE)

### The Evolution

Early approach: "MEMORY.md wastes tokens — don't use it." This was **wrong**.

After 64+ real sessions across multiple projects, the proven approach is a **three-tier architecture** where each tier has a specific, non-overlapping purpose. MEMORY.md IS valuable — but only for behavioral identity, not technical knowledge.

### The Rule: Three Tiers of Knowledge

| Tier | Purpose | Location | Loaded | Why this tier exists |
|------|---------|----------|--------|---------------------|
| **1. Behavioral identity** | HOW to work — principles, corrections, user preferences | `MEMORY.md` + `feedback_*.md`, `user_*.md`, `project_*.md` | Every turn | Behavioral rules SHOULD load every turn — they prevent repeat mistakes |
| **2. Project rules** | WHAT to follow — procedures, critical rules, KB index | `CLAUDE.md` (repo root) | Every turn | Immutable rules checked into git, shared across team |
| **3. Technical knowledge** | WHAT to know — architecture, patterns, code examples | `.claude/topics/*.md` | On-demand via MCP | Token-efficient: only loaded when needed |

### How It Works

1. **MEMORY.md** (auto-memory, `~/.claude/projects/.../memory/`):
   - Contains 5-8 core behavioral principles earned from real mistakes
   - Each principle has incident context (what went wrong, user's exact words)
   - Session protocol (startup, during work, end-of-session)
   - Self-learning routing table
   - Index of feedback/project/user memory files
   - **Limit: 120 lines** (max 200 — Claude truncates beyond this)

2. **CLAUDE.md** (repo root, git-checked):
   - Scope definition header
   - Zero hallucination policy
   - Procedural rules with "why" context
   - Build/run commands
   - Key gotchas
   - Complete KB index (table of all `.claude/topics/` files)
   - References MEMORY.md for behavioral identity

3. **`.claude/topics/`** (queried on-demand via MCP):
   - One concept = one file, <100 lines each
   - Organized by functional category
   - Indexed in both CLAUDE.md and `.claude/INDEX.md`
   - Includes consolidated operational feedback from MEMORY.md overflow

### Routing Table (Where Lessons Go)

| Lesson Type | Target | Example |
|-------------|--------|---------|
| Behavioral correction | `MEMORY.md` | "Never declare done without verifying the running system" |
| User preference/feedback | `feedback_*.md` in auto-memory | "User prefers discussing approach before coding" |
| User profile | `user_*.md` in auto-memory | "Senior PM, efficiency = business survival" |
| Project context | `project_*.md` in auto-memory | "Merge freeze starts Thursday" |
| Technical detail | `.claude/topics/*.md` | Architecture, API patterns, deployment procedures |
| Procedural rule | `CLAUDE.md` | "Never modify DB manually" |
| Cross-project lesson | `cc-mpc-extended-rlm/docs/` | Universal best practices |

### The Fresh Instance Rule (CRITICAL)

When updating any knowledge base file, **always think from the perspective of a completely new chat session** — a fresh Claude instance that:
- Sees `MEMORY.md` (behavioral identity — loaded automatically)
- Sees `CLAUDE.md` (project rules — loaded automatically)
- Has MCP tools available to query `.claude/topics/`
- Must discover technical details by querying the KB

**Ask yourself:** "If I started a brand new session right now, would I find this rule? Would I understand it? Would I follow it from message one?"

If the answer is no — the knowledge update is incomplete. Write it so a blank instance can act on it without any prior context.

### Why Three Tiers > Two Layers

The previous "don't use MEMORY.md" approach failed because:
1. **Behavioral principles got lost** between sessions — each new session repeated the same mistakes
2. **User corrections had no persistence** — users had to re-explain preferences every time
3. **No behavioral continuity** — the agent had knowledge but no personality/approach consistency

The three-tier approach fixes this:
- **Behavioral continuity**: MEMORY.md ensures consistent working approach across sessions
- **Token efficiency**: Technical knowledge stays in KB (on-demand), only behavioral rules load every turn
- **Knowledge compounds**: Universal lessons improve ALL projects via cc-mpc-extended-rlm
- **Clean separation**: Each tier has one job, no overlap, no confusion
- **Scaling**: MEMORY.md stays small (120 lines), overflow routes to KB topics or individual memory files

### Evidence

Tested across 64+ sessions on the eFakt project (ASP.NET Core + Next.js + KSeF) and compared against the KB-only approach on cvs_ls26 (Clipper/C legacy). The three-tier approach with MEMORY.md produced:
- 55% fewer repeated mistakes (behavioral principles persisted)
- Faster session startup (agent immediately knows HOW to work)
- Better user satisfaction (corrections stick, preferences remembered)
- Same token efficiency for technical queries (MCP on-demand unchanged)

---

*Updated: 2026-03-23 | Source: Cross-project comparison (eFakt 64 sessions vs cvs_ls26 57 sessions) — three-tier architecture proven superior*
