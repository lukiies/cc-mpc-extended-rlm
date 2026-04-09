# Development Best Practices - Lessons from Real Projects

Universal lessons learned across 75+ sessions on production projects using cc-mpc-extended-rlm. These apply to any project, regardless of tech stack.

**Evidence base:** These patterns were extracted from real incidents — each "Why" is an actual bug, deployment failure, or user correction.

---

## 1. Web Authentication Security

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

## 2. Test Discipline

### Never Mask Test Failures

**Rule:** When tests fail, investigate root cause → fix → verify. NEVER modify tests to pass artificially (removing assertions, relaxing expectations, skipping tests).

**Why:** Tests are the safety net. Weakening them to show green hides real bugs that will surface in production.

### Never Weaken the API to Make Tests Pass

**Rule:** Tests must adapt to the API, never the reverse. If tests fail because of rate limiting, auth policies, or validation — fix the tests (add proper auth, use delays/retries, send valid data). NEVER disable security features or rate limits to make tests pass.

**Why:** Disabling rate limiting in code to make tests pass means production runs without rate limiting. The API is the contract — tests prove the contract works, they don't define it.

### All Tests Must Pass (100%)

**Rule:** Every test in the suite must pass before a task is considered complete. "96% passed" is unacceptable.

**Why:** Partial pass rates hide regressions that compound over time. Each "known failure" becomes a blind spot.

### Always Create Tests for New Features

**Rule:** Every new feature MUST have tests covering: loading states, form interactions, API calls, error handling.

**Why:** Untested features break silently in future changes. If it's worth building, it's worth testing.

### Never Dismiss Test Failures as "Pre-existing"

**Rule:** If a test fails, investigate whether your change caused it — even if you think it was already broken. At minimum, verify it fails on the base branch too.

**Why:** "It was already broken" is often wrong — and even when correct, ignoring it lets rot accumulate.

---

## 3. Build, Restart & Verification

### Changed Components Must Be Restarted Before Declaring Done

**Rule:** After code changes, restart the affected components and verify they're running with the new code before reporting results. Backend changed → kill + build + start + health check. Frontend changed → kill + start + verify. Both → both.

**Why:** 8+ times across sessions, code was changed but stale processes kept running. The user tested old code every time. Build tools often cache — `dotnet run` without `clean && build` uses stale code. `next dev` hot-reloads most changes but not all.

**Pattern:**
```bash
# Backend (.NET example)
kill $(lsof -t -i:5001) 2>/dev/null
dotnet clean && dotnet build
dotnet run --no-build --urls "http://127.0.0.1:5001" &
curl -s http://127.0.0.1:5001/health  # MUST return 200

# Frontend (Next.js example)
pkill -f "next dev"
pnpm dev &
curl -s http://localhost:3000  # MUST return 200
```

### "Done" Means the User Can Immediately Test

**Rule:** Never declare a task complete unless the user can RIGHT NOW open their browser/client and see the change working. If a process needs to be restarted, restart it. If a build needs to run, run it.

**Why:** 15+ times "it's done" was reported while the system was actually broken, not restarted, or showing stale behavior.

---

## 4. Database Safety

### Databases Are Read-Only Unless Explicitly Told Otherwise

**Rule:** NEVER execute write operations against any database without explicit user instruction. This includes direct SQL writes, API calls that modify data (`POST`, `PUT`, `DELETE`), and any state-changing operations. Read operations (`SELECT`, `GET`) are always safe.

**Why:** The user's test/production data is THEIR data. Diagnosing a problem ≠ permission to fix it by modifying data. Always report findings and let the user decide.

### Never Modify Database Schema Manually

**Rule:** Use only the project's ORM migration system (EF Core migrations, Alembic, Django migrations, Prisma migrate, etc.). NEVER run manual `ALTER TABLE`, `DROP`, or direct schema modification commands.

**Why:** Manual schema changes corrupt migration state. The ORM loses track of what's been applied, future migrations fail, and the only fix is often a painful manual reconciliation.

**Allowed:** Read-only queries (`SELECT`), creating migration files via ORM CLI.
**Forbidden:** `ALTER TABLE`, `DROP TABLE`, `UPDATE sqlite_master`, direct DB tools for schema changes.

---

## 5. Deployment Discipline

### Backend + Frontend = Atomic Deploy

**Rule:** ALWAYS deploy backend AND frontend together. They share an API contract (request/response shapes). Deploying only one side while the other expects a different format = broken site.

**Why:** Backend was deployed with pagination changes (response changed from flat array to `{items, totalCount}`). Frontend was not redeployed — it still expected a flat array. Result: `.map()` failed on an object, every page crashed.

### Never Deploy from a Dirty Workspace

**Rule:** If `git status` shows uncommitted changes, commit first or verify that both backend and frontend are built from the same code state. Building one from uncommitted code + the other from committed code = contract mismatch.

### Never Improvise Directory Structure During Deploys

**Rule:** When a deployment tool (rsync, scp) fails, STOP and read the error. Do NOT restructure directories, move databases, or `rm -rf` to "fix" the issue.

**Why:** During one deployment, rsync failed → improvised directory restructure → `rm -rf` → moved database to wrong path → customer saw "First-Time Setup" on their production system. The database was nearly lost.

**Pattern:** rsync fails → STOP → read the error → understand WHY → fix the specific conflict only.

### Follow a Deployment Checklist

**Rule:** Production deployments should follow a written checklist. Key items that are commonly forgotten:
- Version file and changelog
- API documentation
- Frontend static assets
- Template/resource directories that aren't in the standard build output
- Health check verification AFTER deploy (not just "did rsync succeed")
- Verify the version endpoint returns the new version number

### Production Deploys Only on Explicit Instruction

**Rule:** NEVER deploy to any production instance without the user's explicit instruction. Finishing a code fix ≠ permission to deploy. Even if the user asked to deploy earlier in the conversation, a NEW deploy of NEW code requires a NEW explicit order.

**Why:** Standing permission doesn't exist. Each deploy is a separate decision with separate risk.

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

## 6. Git Commit Discipline

### All Changes Must Be Committed — Verify Before Branch Switch

**Rule:** NEVER switch branches until working tree is clean. Always: `git status` → stage ALL listed files → commit → `git status` (must show "working tree clean") → ONLY THEN switch branches.

**Why:** Lost code from incomplete commits broke production features silently. Entire features were documented as "done" but code was never committed.

### Never Stage from Memory

**Rule:** Always use `git status` output to decide what to stage. Don't rely on remembering which files you changed. Modified files can be in unexpected places (config files, lock files, auto-generated code).

### Verify Commits Include ALL Files

**Rule:** Run `git status` before AND after every commit. Check for untracked files, unstaged changes, and staged-but-not-committed files. After commit, working tree MUST be clean.

**Why:** Multiple times, only documentation was committed while source code was forgotten (or vice versa).

---

## 7. API Documentation Sync

### Documentation Must Update With API Changes

**Rule:** When API endpoints change (new endpoints, changed request/response shapes, new parameters), update all documentation sources in the same commit:
- API documentation file (e.g., `API_DOCUMENTATION.md`)
- Swagger/OpenAPI annotations in code
- Any served documentation endpoints

**Why:** Out-of-sync API docs cause integration failures. Frontend developers and external consumers rely on documentation being accurate.

---

## 8. Version Tracking

### Every Code Change Gets a Version Bump + Changelog Entry

**Rule:** When completing a code change (not just docs), bump the version file and add a changelog entry describing what changed. This is part of the "done" criteria, not an afterthought.

**Why:** Without version tracking, it's impossible to know what's deployed where, when a bug was introduced, or what changed between deployments. A version number is the simplest way to answer "is this the new code?"

### Version Endpoint

**Rule:** Every deployed service should have a `/version` or `/health` endpoint that returns the current version number. This is the fastest way to verify a deployment succeeded.

---

## 9. Configuration & Credentials

### No Hardcoded URLs or Credentials

**Rule:** All configuration (API URLs, credentials, ports, paths) must come from environment files (`.env`). Frontend API calls should go through a configured API client, not raw URLs.

**Why:** Hardcoded URLs break across environments (dev/test/staging/prod). Hardcoded credentials are a security incident waiting to happen.

### Credentials: Always Read from .env

**Rule:** When you need credentials (API keys, passwords, tokens), read them from the project's `.env` file. NEVER guess, fabricate, or use defaults that might work.

**Why:** Wrong credentials can lock out accounts, hit wrong environments, or trigger rate limits on the wrong service.

---

## 10. Self-Learning Protocol — Observations from 75+ Sessions

### What Works Well
- **Routing lessons by type** (project-specific vs universal) prevents cluttering individual projects with generic knowledge
- **Auto-memory reinforcement** of critical rules ensures compliance across sessions
- **Modular topic files** (<100 lines) enable efficient Haiku extraction
- **5-point security testing checklist** catches issues that browser testing misses
- **Incident context ("Why")** on every rule makes edge-case judgment possible
- **Consolidation pattern** (overflow from MEMORY.md → `operational-feedback.md` topic) keeps Tier 1 small
- **Incident log** in MEMORY.md (one-line summary with pattern distribution) helps track improvement

### Common Mistakes to Avoid
- Building features with cosmetic validation instead of real security
- Testing only in the browser (use curl/wget for security verification)
- Deploying without checking file permissions for the service user
- Combining public and protected content in the same page/response
- Not defining test procedures before implementing security features
- Declaring "done" based on build success without verifying the running system
- Leaving stale processes running after code changes
- Committing partial file sets (docs without code, or code without docs)
- Modifying tests to make them pass instead of fixing the underlying bug
- Deploying only backend or only frontend when both have changed

### Pattern Distribution from Real Incidents (75 sessions)

| Pattern | Frequency | Prevention |
|---------|-----------|------------|
| Restart/verify failures | 53% | Principle #3 (Build, Restart & Verification) |
| Guess-instead-of-check | 19% | Zero Hallucination Policy |
| Scope/focus drift | 14% | "Stay focused on primary ask" principle |
| Git/commit incomplete | 8% | Git Commit Discipline rules |
| Unauthorized deploy | 3% | "Production deploys only on explicit instruction" |
| Destructive deploy ops | 3% | "Never improvise directory structure" |

---

## 11. Behavioral Principles — Universal Starter Set

These principles should be seeded into every new project's MEMORY.md. They represent the minimum behavioral baseline that prevents the most common mistakes:

### 1. Verify the Actual Result Before Declaring Done
Never declare a task complete without verifying the actual running system. Tests passing is necessary but not sufficient.

### 2. Tests Passing ≠ It Works
Tests test the code, not the user experience. Before declaring success, ask: "Would the user see this working if they tried it RIGHT NOW?"

### 3. Stay Focused on the Primary Ask
Before starting work, identify: What is the ONE thing the user needs most? Do that FIRST. Don't drift to secondary improvements.

### 4. Never Guess — Investigate or Ask
Applies to errors, credentials, API responses, everything. Read the actual data. Say "I don't know, let me check" — never fabricate a plausible-sounding answer.

### 5. Honesty About Failures > False Success
If something broke, say it broke. If you made a mistake, own it. Never hide behind "tests pass" or partial success presented as full success.

### 6. Never Overreach — Do What Was Asked
Before any change, ask: "Did the user ask for this specific change?" If not, don't do it. Unexpected changes (even "improvements") erode trust.

### 7. Changed Components Must Be Restarted and Verified
After code changes, restart ONLY the affected parts and verify with a health check. "Done" = the user can immediately test the change.

These 7 principles alone prevented 80%+ of repeated mistakes across 75 sessions. Each new project will develop additional project-specific principles over time.

---

---

## 12. Knowledge Management — Three-Tier Architecture (CORE)

### The Evolution

Early approach: "MEMORY.md wastes tokens — don't use it." This was **wrong**.

After 75+ real sessions across multiple projects, the proven approach is a **three-tier architecture** where each tier has a specific, non-overlapping purpose. MEMORY.md IS valuable — but only for behavioral identity, not technical knowledge.

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

Tested across 75+ sessions on the eFakt project (ASP.NET Core + Next.js + KSeF) and compared against the KB-only approach on cvs_ls26 (Clipper/C legacy). The three-tier approach with MEMORY.md produced:
- 55% fewer repeated mistakes (behavioral principles persisted)
- Faster session startup (agent immediately knows HOW to work)
- Better user satisfaction (corrections stick, preferences remembered)
- Same token efficiency for technical queries (MCP on-demand unchanged)

---

*Updated: 2026-04-09 | Source: Cross-project evidence (eFakt 75 sessions, cvs_ls26 57 sessions) — three-tier architecture proven superior, universal patterns extracted from 68 real incident corrections*
