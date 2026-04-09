# MEMORY.md Integration Guide — Three-Tier Knowledge Architecture

The proven approach for infinite memory, knowledge base, and self-learning protocol in Claude Code projects. Updated with real-world patterns from 130+ production sessions.

---

## Why Three Tiers?

Early approach said "MEMORY.md wastes tokens — don't use it." This was wrong.

After 130+ real sessions across multiple projects, the evidence is clear: **MEMORY.md is essential for behavioral continuity**. Without it, Claude repeats the same mistakes every session. The key insight is that MEMORY.md should contain **behavioral principles** (HOW to work), not technical knowledge (WHAT to know).

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

### BLOCKING Startup Protocol (CRITICAL ADDITION)

A pattern discovered after 58+ sessions on cvs_ls26: **having rules is useless if they're not actively processed at session start**. The most common failure mode was "rule existed in MEMORY.md but was ignored during execution."

**Solution:** Add a MANDATORY BLOCKING startup section to MEMORY.md that forces the agent to read and internalize ALL rules before starting work:

```markdown
## SESSION PROTOCOL

### Startup (MANDATORY BLOCKING — every new conversation)
**You MUST NOT start any work until ALL steps below are completed.**

1. Call `mcp__enhanced-rlm__get_kb_session_stats` — verify MCP responsive
2. Display: `cc-mpc-extended-rlm active. KB status: [OK/ERROR]`
3. **READ FULLY: MEMORY.md** — every line, every principle. Loaded in context ≠ understood.
4. **READ FULLY: CLAUDE.md** — every section. ALL of it.
5. **IDENTIFY which `.claude/topics/*.md` correlate to user's prompt.** READ them BEFORE starting work.
6. **READ all `feedback_*.md` files** referenced in Memory File Index.

**BLOCKING means:** If you skip ANY step and start working, you WILL violate rules and get corrected.
```

**Why this works:** A fresh session that follows this protocol has near-zero "knew the rule but didn't follow it" failures. Without it, the rate was ~7% of all incidents.

### Incident Log Pattern

A proven pattern from 130+ sessions: maintain a one-line **incident log** near the end of MEMORY.md that summarizes total corrections and their pattern distribution. This helps track improvement over time:

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

These are the most impactful memory files. Each captures a specific correction or validated approach with structured format.

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

```markdown
---
name: feedback_no_code_without_evidence
description: Never modify code without clear root cause; "I don't know" beats a guessed fix
type: feedback
---

Never modify source code without clear root cause evidence.
**Why:** Speculative fixes mask real issues and introduce new bugs. User corrected after wrong variable was "fixed".
**How to apply:** When debugging, gather evidence (logs, actual values, repro steps) BEFORE proposing a code change. If evidence is inconclusive, say "I don't know yet, let me investigate further."
```

```markdown
---
name: feedback_always_build
description: ALWAYS build module after code changes before declaring done
type: feedback
---

ALWAYS run the build command after ANY code changes before declaring done.
**Why:** User expected built module, got unbuilt source file with syntax error caught only at build time.
**How to apply:** After every code edit, run build.sh / npm build / dotnet build before saying "done".
```

```markdown
---
name: feedback_db_readonly
description: NEVER write to DB — SELECT only, give SQL to user
type: feedback
---

NEVER execute write operations on database (UPDATE/INSERT/DELETE/ALTER) — SELECT only.
If modifications are needed, provide the SQL to the user and let them execute it.
**Why:** AI-driven DB writes caused data issues. User's data is their responsibility.
**How to apply:** For any data investigation, use only SELECT. For fixes, provide SQL as text.
```

```markdown
---
name: feedback_never_duplicate_logic
description: NEVER duplicate existing function logic; always CALL the existing function
type: feedback
---

Before implementing ANY helper, search codebase for existing implementations. Always CALL existing functions.
**Why:** Duplicate rounding function had different precision, causing financial discrepancies.
**How to apply:** `grep -r "function_name" .` before writing any new helper. If similar exists, use it.
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

### Real-World Memory File Index Example

From a mature project with 58+ sessions and 27 memory files:

```markdown
## Memory File Index
- [feedback_discuss_approach_first.md](feedback_discuss_approach_first.md) — Always propose simplest approach before coding (2026-03)
- [feedback_always_build.md](feedback_always_build.md) — ALWAYS build after code changes before done (2026-04)
- [feedback_db_readonly.md](feedback_db_readonly.md) — NEVER write to DB, SELECT only (2026-04)
- [feedback_no_code_without_evidence.md](feedback_no_code_without_evidence.md) — Never guess fixes without evidence (2026-03)
- [feedback_never_duplicate_logic.md](feedback_never_duplicate_logic.md) — Always reuse existing functions (2026-03)
- [feedback_save_knowledge_incrementally.md](feedback_save_knowledge_incrementally.md) — Save lessons immediately, not batched (2026-03)
- [feedback_efficient_session_pattern.md](feedback_efficient_session_pattern.md) — API first, test immediately, fast iteration (2026-03)
- [feedback_never_raw_test_output.md](feedback_never_raw_test_output.md) — Redirect test stdout to file BEFORE running (2026-03)
- [user_role.md](user_role.md) — User role and expertise level (2026-03)
- [project_test_data.md](project_test_data.md) — Test data specifics (2026-03)
```

**Key insight:** Each file is small (5-15 lines), focused on ONE lesson, and uses the structured format (rule + Why + How to apply). This makes them fast to read during the startup protocol.

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

| Metric | KB-Only (no MEMORY.md) | Three-Tier (with MEMORY.md) | Three-Tier + BLOCKING startup |
|--------|------------------------|----------------------------|-------------------------------|
| Repeated behavioral mistakes | ~2-3 per session | ~0.5 per session | ~0.2 per session |
| Session startup effectiveness | Slow (re-learns approach) | Fast (principles loaded) | Fastest (all context pre-loaded) |
| User re-explanations needed | Frequent | Rare | Very rare |
| "Rule existed but ignored" | N/A | ~7% of incidents | ~1% of incidents |
| Technical query efficiency | Same (MCP on-demand) | Same (MCP on-demand) | Same (MCP on-demand) |
| Token overhead per turn | Lower | +120 lines (acceptable) | +120 lines (acceptable) |
| Overall user satisfaction | Good | Significantly better | Best |

The 120-line MEMORY.md overhead is vastly outweighed by the behavioral continuity it provides. The BLOCKING startup protocol added in later sessions virtually eliminated the "knew the rule but didn't follow it" failure class.

### Key Scaling Observations

From a mature project (cvs_ls26) with 69 topic files, 27 memory files, and 58+ sessions:

1. **Topic files scale well** — 69 files with <100 lines each keeps per-query token usage low
2. **Memory files accumulate fast** — 27 feedback/project/user files after 58 sessions (about 1 new file every 2 sessions)
3. **MEMORY.md at 120 lines is tight** — project-specific procedures (test steps, build chains) consume most of it
4. **Cross-project lessons** — about 60% of feedback lessons from one project are universal, 40% are project-specific
5. **INDEX.md with keywords** significantly improves MCP search quality vs. bare file listings

---

*Updated: 2026-04-09 | Source: Cross-project comparison (eFakt 75 sessions, cvs_ls26 58 sessions) — BLOCKING startup protocol, scaling observations, and real-world memory file examples added*
