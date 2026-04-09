# MEMORY.md Integration Guide — Three-Tier Knowledge Architecture

The proven approach for infinite memory, knowledge base, and self-learning protocol in Claude Code projects.

---

## Why Three Tiers?

Early approach said "MEMORY.md wastes tokens — don't use it." This was wrong.

After 75+ real sessions across multiple projects, the evidence is clear: **MEMORY.md is essential for behavioral continuity**. Without it, Claude repeats the same mistakes every session. The key insight is that MEMORY.md should contain **behavioral principles** (HOW to work), not technical knowledge (WHAT to know).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: BEHAVIORAL IDENTITY (loaded every turn)            │
├─────────────────────────────────────────────────────────────┤
│ ~/.claude/projects/.../memory/                              │
│                                                             │
│  MEMORY.md              (≤120 lines, behavioral principles) │
│  feedback_*.md          (user corrections & validations)    │
│  user_*.md              (user profile, role, preferences)   │
│  project_*.md           (project context, deadlines, goals) │
└─────────────────────────────────────────────────────────────┘
          ↕ (MEMORY.md references CLAUDE.md for rules)
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: PROJECT RULES (loaded every turn)                  │
├─────────────────────────────────────────────────────────────┤
│ <repo-root>/CLAUDE.md                                       │
│  ├─ Scope definition                                        │
│  ├─ Zero hallucination policy                               │
│  ├─ Procedural rules (with "why" context)                   │
│  ├─ Build/run commands                                      │
│  ├─ Key gotchas                                             │
│  └─ KB INDEX (table of all .claude/topics/ files)           │
└─────────────────────────────────────────────────────────────┘
          ↕ (queried on-demand via MCP)
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: TECHNICAL KNOWLEDGE (on-demand, token-efficient)   │
├─────────────────────────────────────────────────────────────┤
│ <repo-root>/.claude/                                        │
│  ├─ INDEX.md            (topic navigation)                  │
│  ├─ topics/             (modular files, <100 lines each)    │
│  ├─ code_examples/      (by language)                       │
│  └─ pre-requisites/     (research, planning)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Tier 1: MEMORY.md — Behavioral Identity

### What Goes Here

MEMORY.md is your agent's **personality and working approach**. It persists across sessions and shapes every interaction.

| Content Type | Example | Why it belongs here |
|-------------|---------|---------------------|
| Core principles | "Never declare done without verifying the running system" | Must be active every turn to prevent repeat mistakes |
| Session protocol | Startup check, during-work rules, end-of-session steps | Ensures consistent workflow every session |
| Self-learning routing | Where each type of lesson goes | Prevents knowledge from going to wrong tier |
| Memory file index | Links to feedback_*.md, user_*.md, project_*.md | Quick navigation to detailed memories |

### What Does NOT Go Here

| Content Type | Where it goes instead |
|-------------|----------------------|
| Technical architecture | `.claude/topics/architecture.md` |
| Build commands | `CLAUDE.md` |
| API patterns | `.claude/topics/api-endpoints.md` |
| Code examples | `.claude/code_examples/` |
| Troubleshooting steps | `.claude/topics/troubleshooting.md` |

### Template

```markdown
# Behavioral Identity — [PROJECT_NAME]

This file shapes HOW I think and work — not just what I know.
CLAUDE.md has project rules and KB index. This file has what makes me ME.

---

## CORE BEHAVIORAL PRINCIPLES

These are corrections earned from real mistakes. Each carries its incident context.

### 1. VERIFY THE ACTUAL RESULT BEFORE DECLARING DONE
[Incident context: what went wrong, user's exact words]

### 2. TESTS PASSING ≠ IT WORKS
[Incident context]

### 3. STAY FOCUSED ON THE PRIMARY ASK
[Incident context]

### 4. NEVER GUESS — INVESTIGATE OR ASK
[Incident context]

### 5. HONESTY ABOUT FAILURES > FALSE SUCCESS
[Incident context]

[Add more as earned from real corrections — each numbered, each with context]

---

## SESSION PROTOCOL

### Startup
1. Call `mcp__enhanced-rlm__get_kb_session_stats` — verify MCP responsive
2. Display: `cc-mpc-extended-rlm active. KB status: [OK/ERROR]`
3. Read this file. Internalize principles, not just scan.

### During Work
- Query KB via `mcp__enhanced-rlm__ask_knowledge_base` for technical details
- Track complex tasks with TodoWrite
- [Project-specific during-work rules]

### End of Session
1. Update KB with lessons learned (route per self-learning protocol)
2. Call `mcp__enhanced-rlm__get_kb_session_stats`
3. Report stats under "Knowledge Base Usage"

---

## SELF-LEARNING PROTOCOL

After every non-trivial task, update the knowledge base:

| Lesson Type | Target | When |
|-------------|--------|------|
| Behavioral correction | THIS FILE (MEMORY.md) | When I make a mistake in HOW I work |
| User feedback | `feedback_*.md` in this directory | When user corrects or validates approach |
| User profile | `user_*.md` in this directory | When I learn about user's role/expertise |
| Project context | `project_*.md` in this directory | When I learn deadlines, decisions |
| Technical knowledge | `.claude/topics/*.md` | When I learn project-specific details |
| Procedural rule | `CLAUDE.md` | When a new critical rule is needed |
| Cross-project lesson | `cc-mpc-extended-rlm/docs/` | Universal best practices |

---

## INCIDENT LOG (summary — details in KB)

0 corrections across 0 sessions. Patterns will emerge over time.
[Update this line after each incident — track counts and pattern percentages]

---

## Memory File Index
- [feedback_example.md](feedback_example.md) — Description (date)
- [user_role.md](user_role.md) — Description (date)
```

### Incident Log Pattern

A proven pattern from 75+ sessions: maintain a one-line **incident log** near the end of MEMORY.md that summarizes total corrections and their pattern distribution. This helps track improvement over time:

```markdown
## INCIDENT LOG (summary — details in KB)

68 corrections across 75 sessions. Pattern: 53% restart/verify failures, 19% guess-instead-of-check,
14% scope/focus, 8% git/commit, 3% unauthorized deploy, 3% destructive deploy ops.
Latest: 2026-04-06 (brief description of most recent incident).
```

**Why this works:** A fresh session can instantly see the most common failure modes and focus its attention there. Pattern percentages expose the real risks — not the theoretical ones.

### Scaling Rules

1. **Target: 120 lines** — Claude truncates MEMORY.md after 200 lines
2. **When it grows too large**: Consolidate operational details into `.claude/topics/operational-feedback.md`, keep only principles + pointers in MEMORY.md
3. **Individual memory files** (`feedback_*.md`, `user_*.md`, `project_*.md`) have no line limit but should stay focused (one concept per file)
4. **The Memory File Index** in MEMORY.md links to all individual files — keep it updated
5. **The incident log** stays as one concise line — update counts and pattern percentages, don't expand into details

---

## Tier 2: CLAUDE.md — Project Rules

### What Goes Here

CLAUDE.md is the **immutable project rulebook**, checked into git and shared across all contributors.

| Content Type | Example |
|-------------|---------|
| Scope definition | "These rules apply ONLY to [PROJECT_NAME]" |
| Zero hallucination policy | 7 core anti-hallucination principles |
| Procedural rules | "Never modify DB manually" — with incident context |
| Build/run commands | Exact commands for build, test, deploy |
| Key gotchas | Top 10-20 project-specific pitfalls |
| KB index | Complete table of all `.claude/topics/` files |

### Relationship to MEMORY.md

```
CLAUDE.md (line 3): "My behavioral identity lives in MEMORY.md (auto-memory)."
CLAUDE.md (line 5): "If MEMORY.md is empty or missing, these are the critical behavioral principles..."
```

This ensures that even if MEMORY.md is lost, CLAUDE.md has fallback behavioral principles.

---

## Tier 3: .claude/topics/ — Technical Knowledge

### What Goes Here

Everything that is project-specific and technical — queried on-demand via MCP, never loaded unless needed.

| Content Type | Example Files |
|-------------|---------------|
| Architecture | `topics/architecture.md` |
| API endpoints | `topics/api-endpoints.md` |
| Database patterns | `topics/database-rules.md` |
| Testing procedures | `topics/testing.md` |
| Deployment guides | `topics/deployment.md` |
| Integration details | `topics/ksef-integration.md` |
| Consolidated feedback | `topics/operational-feedback.md` |

### Modular KB Principle

- One concept = one file
- Target: <100 lines per file
- Small files enable efficient Haiku extraction (lower token usage per query)
- Always update `.claude/INDEX.md` when adding new topics

---

## MEMORY.md Overflow Pattern

When MEMORY.md approaches the 120-line target:

1. **Identify detail-heavy sections** (e.g., 13 individual operational rules)
2. **Consolidate into a KB topic**: `.claude/topics/operational-feedback.md`
3. **Replace in MEMORY.md** with a pointer:
   ```markdown
   ## OPERATIONAL FEEDBACK → KB
   All detailed operational rules are consolidated in:
   **`.claude/topics/operational-feedback.md`** — query via MCP
   ```
4. **Keep principles in MEMORY.md**, move details to KB

This way MEMORY.md stays concise while no knowledge is lost.

---

## Individual Memory Files

Beyond MEMORY.md, the auto-memory directory can hold individual files for specific memories:

### feedback_*.md — User Corrections

```markdown
---
name: feedback_discuss_approach
description: Always discuss approach before coding for complex features
type: feedback
---

Always discuss implementation approach BEFORE coding, especially for complex features.
**Why:** User corrected after over-engineering a test wrapper without discussion.
**How to apply:** At decision points, ask before implementing.
```

### user_*.md — User Profile

```markdown
---
name: user_role_and_context
description: User is a PM delivering to real customers, efficiency is critical
type: user
---

User is a PM (project manager) delivering to real customers.
Tasks are building blocks toward bigger business objectives.
Efficiency = business survival. Don't waste time on unnecessary complexity.
```

### project_*.md — Project Context

```markdown
---
name: project_session_consolidation
description: KSeF sessions consolidated to one shared session architecture
type: project
---

KSeF sessions consolidated to single shared session model (2026-03-18).
Architecture: KSeFSharedSessionProvider → one session for all operations.
**Why:** KSeF rate limits (120/hr PROD, 1200/hr TEST) required conservation.
```

---

## Converting an Existing Project

If a project currently uses the old "don't use MEMORY.md" approach:

1. **Read current MEMORY.md** — note any redirect or minimal content
2. **Read CLAUDE.md** — identify behavioral rules mixed in with project rules
3. **Extract behavioral principles** from CLAUDE.md → write to MEMORY.md
4. **Extract user feedback** from session history → create `feedback_*.md` files
5. **Add session protocol** to MEMORY.md
6. **Add self-learning routing table** to MEMORY.md
7. **Update CLAUDE.md** to reference MEMORY.md for behavioral identity
8. **Verify**: New session should know HOW to work (MEMORY.md) + WHAT to follow (CLAUDE.md) + WHERE to find details (MCP)

See the conversion prompt template at the bottom of this guide for an automated approach.

---

## Evidence: Why This Works

Tested across 130+ combined sessions on two production projects:

| Metric | KB-Only (no MEMORY.md) | Three-Tier (with MEMORY.md) |
|--------|------------------------|----------------------------|
| Repeated behavioral mistakes | ~2-3 per session | ~0.5 per session |
| Session startup effectiveness | Slow (re-learns approach) | Fast (principles loaded) |
| User re-explanations needed | Frequent | Rare |
| Technical query efficiency | Same (MCP on-demand) | Same (MCP on-demand) |
| Token overhead per turn | Lower | +120 lines (acceptable) |
| Overall user satisfaction | Good | Significantly better |

The 120-line MEMORY.md overhead is vastly outweighed by the behavioral continuity it provides.

---

*Updated: 2026-04-09 | Source: Cross-project comparison (eFakt 75 sessions, cvs_ls26 57 sessions) — incident log pattern and updated evidence*
