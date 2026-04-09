# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
- Files in this workspace ([PROJECT_NAME] codebase)
- Code in the [REPO_NAME] repository
- Development tasks for [PROJECT_NAME]
- [PRIMARY_TECH_STACK], or project-specific patterns
- [PROJECT_DOMAIN_DESCRIPTION]

**These rules DO NOT apply to general questions unrelated to this project.**

---

## SESSION STARTUP CHECK (MANDATORY)

**At the very start of every new conversation**, before responding to the user's first message, you MUST:

1. Call `mcp__enhanced-rlm__get_kb_session_stats` to verify the extension is responsive
2. Display this greeting message:

```
cc-mpc-extended-rlm (Enhanced Knowledge Base MCP Server) is active.
Knowledge base status: [OK / ERROR based on step 1 result]
```

3. If the call **fails or times out**, display:
```
WARNING: cc-mpc-extended-rlm extension is NOT responding.
Knowledge base features may be unavailable this session.
```

4. Then proceed with the user's request normally.

**Purpose:** This gives the user immediate confirmation that the knowledge base extension is loaded and working at the start of every chat session.

### MEMORY.md — Behavioral Identity (THREE-TIER ARCHITECTURE)

The knowledge management system uses **three tiers**, each with a specific purpose:

| Tier | Purpose | Location | Loaded |
|------|---------|----------|--------|
| **Behavioral identity** | HOW to work — principles earned from real mistakes, user corrections, feedback | `MEMORY.md` (auto-memory) + `feedback_*.md` / `project_*.md` / `user_*.md` | Every turn ✓ |
| **Project rules** | WHAT to follow — procedures, build commands, KB index, critical rules | `CLAUDE.md` (repo root) | Every turn ✓ |
| **Technical knowledge** | WHAT to know — architecture, patterns, gotchas, code examples | `.claude/topics/*.md` | On-demand via MCP ✓ |

**MEMORY.md IS the right place for behavioral principles** — they SHOULD be loaded every turn because they shape how you think and work. What should NOT be in MEMORY.md is technical project knowledge — that belongs in `.claude/topics/` queried via MCP.

**MEMORY.md structure:**
```markdown
# Behavioral Identity

## Core Principles
[5-8 principles earned from real corrections — each with incident context]

## Session Protocol
[Startup, during work, end-of-session steps]

## Self-Learning Protocol
[Routing table: behavioral → MEMORY.md, project → topics/, procedural → CLAUDE.md]

## Incident Log (summary — details in KB)
[One-line: N corrections across M sessions. Pattern: X% type1, Y% type2...]

## Memory File Index
[Links to feedback_*.md, project_*.md, user_*.md files]
```

**Scaling rule:** Keep MEMORY.md under 120 lines (max 200 — Claude truncates after 200). Route details to `.claude/topics/` or individual memory files (`feedback_*.md`, `project_*.md`, `user_*.md`).

**What goes WHERE:**

| Knowledge Type | Target | Example |
|---------------|--------|---------|
| Behavioral correction (how you work) | `MEMORY.md` | "Never declare done without verifying the running system" |
| User feedback on approach | `feedback_*.md` in auto-memory | "Always discuss approach before coding for tax features" |
| User profile/context | `user_*.md` in auto-memory | "User is a PM, efficiency = business survival" |
| Project context (non-code) | `project_*.md` in auto-memory | "Merge freeze starts 2026-03-05" |
| Technical detail | `.claude/topics/*.md` | API endpoint patterns, build procedures |
| Critical procedural rule | `CLAUDE.md` | "Never modify DB manually", "All tests must pass" |
| Cross-project lesson | `cc-mpc-extended-rlm/docs/` | Universal best practices |

See [MEMORY Integration Guide](../docs/MEMORY_INTEGRATION_GUIDE.md) for the complete setup procedure.

---

## ZERO HALLUCINATION POLICY (MANDATORY)

**This is the highest-priority rule. It overrides all other behavior.**

You MUST be **honest, factual, and evidence-based** in every response. If you don't know something, **say "I don't know"**. If you're waiting for data, **say "I'm waiting for the result"**. Never fill gaps with assumptions presented as facts.

### Core Principles

1. **NEVER state unverified information as fact.** If you haven't seen the actual output/data/file content, you do NOT know it. Say so explicitly.

2. **NEVER fabricate tool results.** If a command is still running, was rejected, or failed — report that status honestly. Do NOT invent or assume what the output would be.

3. **NEVER guess and present guesses as facts.** If you must speculate, clearly label it: *"I believe..."*, *"My best guess is..."*, *"I'm not certain, but..."* — never state it as confirmed.

4. **Prefer "I don't know" over any fabrication.** Saying "I don't know" or "I need to check" is ALWAYS better than providing false information. The user trusts you to be honest, not to always have an answer.

5. **Wait for evidence before concluding.** When a tool call returns no result, is running in background, or was interrupted — do NOT draw conclusions from missing data. Either wait, retry, or tell the user what happened.

6. **Verify before asserting.** Before stating something about the environment, configuration, file contents, or system state — actually read/check it first. If you can't check, say you can't verify.

7. **Correct yourself immediately.** If you realize a previous statement was wrong or unverified, correct it in the same response. Do not let incorrect information stand.

### What Counts as Hallucination (FORBIDDEN)

| Scenario | Wrong (Hallucination) | Correct |
|----------|----------------------|---------|
| Command running in background | "The output shows X" | "The command is still running, I don't have the result yet" |
| Tool call was rejected | "Based on the results..." | "The tool call was rejected, I couldn't get the data" |
| Haven't read a file | "This file contains X" | "Let me read the file first" / "I haven't checked this file yet" |
| Unsure about config | "You're using API key auth" | "I'm not sure how auth is configured — let me check" |
| Don't know the answer | Making up a plausible answer | "I don't know. Would you like me to investigate?" |
| Partial information | Filling in gaps with assumptions | "I can see X, but I'm not sure about Y — let me verify" |

### Enforcement

- If you catch yourself about to state something you haven't verified: **STOP and verify first or disclose uncertainty**
- When in doubt between "confident wrong answer" and "honest uncertainty": **ALWAYS choose honest uncertainty**
- This rule applies to ALL responses: code explanations, system state, tool results, architecture descriptions, and general knowledge

---

## Self-Learning Protocol

### The Fresh Instance Rule
When updating knowledge, **think from the perspective of a brand new chat session** — a fresh Claude with zero memory that only sees `CLAUDE.md`, `MEMORY.md`, and MCP tools. Ask: "Would my future self find this, understand it, and follow it from message one?" If not, the update is incomplete. Every KB update is a message from your current self to your future self.

**After completing tasks with 100% success** (all tests pass, no errors, user confirms satisfaction), you MUST:

1. **Analyze the session** for lessons learned:
   - New patterns or solutions discovered
   - Gotchas encountered and resolved
   - Effective approaches worth preserving
   - Mistakes made and how they were fixed

2. **Route updates to the appropriate target (THREE-TIER):**

   | Lesson Type | Target | When |
   |-------------|--------|------|
   | Behavioral correction (HOW I work) | `MEMORY.md` (auto-memory) | When I make a mistake in approach, verification, focus |
   | User feedback/preference | `feedback_*.md` in auto-memory | When user corrects or validates an approach |
   | User profile/context | `user_*.md` in auto-memory | When I learn about user's role, goals, expertise |
   | Project context (non-code) | `project_*.md` in auto-memory | When I learn deadlines, decisions, stakeholder info |
   | Technical knowledge | `.claude/topics/<topic>.md` | When I learn technical details about the project |
   | Procedural rule | `CLAUDE.md` | When a new critical rule is needed |
   | Cross-project lesson | `cc-mpc-extended-rlm/docs/` | Universal best practices |

3. **Update using modular topic files:**
   - Add/update topic files in `.claude/topics/` (one topic per file, <100 lines)
   - Add code examples to `.claude/code_examples/`
   - Update `.claude/INDEX.md` when adding new topics
   - Update `CLAUDE.md` only for critical new rules
   - Keep `MEMORY.md` under 120 lines — route details to individual memory files or KB topics

4. **Skip if no meaningful lessons** - Not every session produces learnings worth preserving.

5. **For cc-mcp-extended-rlm updates:** When lessons are project-agnostic and valuable for other projects, locate the agent repository path from `.mcp.json` (look for `start_server.sh` or `enhanced_rlm` path) and update it there.

---

## Mandatory Test Requirement

**CRITICAL: Every new feature MUST have a test procedure defined BEFORE development begins.**

1. **When receiving a new feature request**, ask for or define:
   - Test scenario (step-by-step verification procedure)
   - Expected results for each step
   - Edge cases to verify

2. **If test scenario is missing**, you MUST ask the developer before starting implementation.

3. **Why this matters:**
   - You can verify your implementation works
   - You can identify and fix issues before completion
   - You learn from debugging and update knowledge base
   - Knowledge grows with practical, verified information

4. **Test procedure template:**
   ```
   ## Test: [Feature Name]
   Prerequisites: [Any setup needed]
   Steps:
   1. [Action] → Expected: [Result]
   2. [Action] → Expected: [Result]
   Cleanup: [How to reset after test]
   ```

---

## Git Commit Verification

**CRITICAL: Before declaring any task complete, verify ALL changes are committed.**

1. **Always run `git status`** before AND after commits
2. **Check for:**
   - Modified files (staged and unstaged)
   - Untracked files (new files, test folders)
3. **After commit, verify:** "nothing to commit, working tree clean"

**Common mistake:** Committing only documentation while forgetting source code changes (or vice versa). Both must be committed together.

```bash
# Verification pattern
git status              # Check what needs to be committed
git add <files>         # Stage changes
git commit -m "message" # Commit
git status              # MUST show "nothing to commit, working tree clean"
git push                # Push to remote
git status              # Final verification
```

---

## Project Overview

[PROJECT_NAME] is a [brief description of your project].

**Knowledge Base Structure (modular - token efficient):**
- `.claude/INDEX.md` - Topic index with keywords (improves search!)
- `.claude/topics/` - Focused topic files (one concept per file)
- `.claude/pre-requisites/` - Research & planning documents
- `.claude/code_examples/` - Reusable code patterns by language

Use `mcp__enhanced-rlm__ask_knowledge_base` to query topics efficiently.

---

## Build & Run Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## Procedural Rules

These are factual/procedural rules. Each carries its "why" — the incident or reasoning that created it.

### Rule 1: NEVER MASK TEST FAILURES
Investigate root cause → fix → verify. Never modify tests to pass artificially.
**Why:** Tests are the safety net. Weakening them to show green hides real bugs.

### Rule 2: ALL TESTS MUST PASS (100%)
Backend + Frontend: 100% passing before any task is complete. "96% passed" = UNACCEPTABLE.
**Why:** Partial pass rates hide regressions that compound over time.

### Rule 3: ALWAYS CREATE TESTS FOR NEW FEATURES
Every new feature MUST have tests covering: loading states, form interactions, API calls, error handling.
**Why:** Untested features break silently in future changes.

### Rule 4: NO HARDCODED URLs OR CREDENTIALS
All config from `.env` files. API calls via configured client module.
**Why:** Hardcoded values break across environments (dev/test/prod).

### Rule 5: DATABASE — NEVER MANUAL SCHEMA MODIFICATIONS
Use only the project's ORM migration system. NEVER run manual ALTER TABLE or direct schema changes.
**Allowed:** Read-only queries (SELECT), ORM migration CLI commands.
**Why:** Manual schema changes corrupt migration state. The ORM loses track, future migrations fail.

### Rule 6: RESTART AFTER EVERY CODE CHANGE
After code changes: kill process → clean build → start → verify with health check → THEN report done.
**Why:** Build tools cache aggressively. Running without clean+rebuild uses stale code. 8+ incidents of testing old code.

### Rule 7: NEVER WEAKEN API FOR TESTS
Tests must adapt to the API (proper auth, retries, valid data). NEVER disable security, rate limits, or validation to make tests pass.
**Why:** Disabling security to pass tests means production runs without security.

### Rule 8: GIT COMMIT VERIFICATION
Always `git status` before AND after commits. Verify "working tree clean." NEVER switch branches with uncommitted changes.
**Why:** Multiple incidents of committing docs without code, or losing uncommitted work on branch switch.

### Rule 9: BACKEND + FRONTEND = ATOMIC DEPLOY
ALWAYS deploy backend AND frontend together. Never deploy from a dirty workspace with API contract changes.
**Why:** Deploying only backend with changed response shapes while frontend expects old format = broken site.

### Rule 10: PRODUCTION DEPLOYS ONLY ON EXPLICIT INSTRUCTION
NEVER deploy to production without the user's explicit instruction. Finishing code ≠ permission to deploy.
**Why:** Each deploy is a separate decision. Standing permission doesn't exist.

---

## Key Rules

1. **Use TypeScript** for all new code
2. **Follow ESLint rules** - run `npm run lint` before committing
3. **Write tests** for all new features
4. **Use 2 spaces** for indentation

## Key Gotchas

1. **Environment variables** - copy `.env.example` to `.env` before running
2. **Database migrations** - run `npm run migrate` after pulling new changes
3. **API routes** - all routes start with `/api/v1/`
4. **Web auth security** - NEVER use client-side CSS/JS hiding for content protection. Protected content must only be served after server-side validation. Always test with `curl`, not just a browser. See [Development Best Practices](../docs/DEVELOPMENT_BEST_PRACTICES.md)
5. **Stale builds** - Always clean + rebuild after code changes. Cached builds mask your changes.
6. **API documentation** - When API endpoints change, update documentation in the same commit.

## Knowledge Base

For detailed information, see `.claude/` folder:
- [INDEX.md](.claude/INDEX.md) - Topic navigation
- [topics/](.claude/topics/) - Modular topic files
- [code_examples/](.claude/code_examples/) - Reusable code by language

**Modular KB principle:** Keep topic files small (<100 lines) so Haiku can extract relevant info efficiently. One concept = one file.

---

## Auto-Deploy: Documentation Website (TRIGGER RULE)

> **This section only applies if `WEBSITE_ENABLED=true` in the project's `.env` file.**
> If the project does not have a documentation website, remove this section entirely.

**CRITICAL: This rule MUST be evaluated after EVERY file modification in `.claude/topics/`.**

### Trigger Condition
Whenever ANY file in `.claude/topics/*.md` or `.claude/INDEX.md` is created, modified, or deleted during the current session, you MUST:

1. **Rebuild the static site:**
   ```
   cd "<workspace-root>" && python website/build.py
   ```

2. **Deploy to the server:**
   ```
   scp website/index.html [WEBSITE_DEPLOY_HOST]:[WEBSITE_DEPLOY_PATH]
   ```
   *(Replace with actual values from `.env`)*

3. **Confirm deployment** with a brief message: `Deployed updated knowledge base to [WEBSITE_URL]`

### When NOT to trigger
- If the session only READ topic files without modifying them
- If `build.py` itself was modified but no topic files changed (rebuild anyway in that case)

### Website Details
- **URL:** `https://[WEBSITE_PREFIX].[WEBSITE_DOMAIN]`
- **Configuration:** All settings in `.env` (see `.env.example` for reference)
- **Build script:** `website/build.py` (generates single `index.html` from `.claude/topics/*.md`)
- **Login credentials:** Defined in `WEBSITE_USERS` in `.env`

### Adding a New Topic to the Website
When adding a new topic file to `.claude/topics/`:
1. Create the `.md` file in `.claude/topics/`
2. **Add entry to `TOPIC_ORDER` in `website/build.py`** — files not in this list will NOT appear on the website
3. Update `.claude/INDEX.md` with the new topic row
4. Rebuild and deploy (steps above)

---

## Knowledge Base Agent (cc-mcp-extended-rlm)

### When to Use
- **Always** use `mcp__enhanced-rlm__ask_knowledge_base` for:
  - Project-specific conventions and patterns
  - Gotchas and common errors
  - Code examples for this codebase
  - Build/test procedures specific to this project

### Query Best Practices
1. **Be specific:** "How to add a document header field?" (good) vs "document stuff" (bad)
2. **Include context:** Add the feature area: "testing pexpect patterns for menu navigation"
3. **Use keywords from INDEX.md:** Reference topic names for better matching

### Understanding Stats
After each knowledge base query, stats are shown:
```
Haiku: input=842 | output=523 | budget=1000 | type=simple | cached=no
```
- **input:** Tokens sent to Haiku (context from KB + query)
- **output:** Tokens in Haiku's response
- **budget:** Max output tokens allowed for query type
- **type:** Query classification (simple/code_example/complex)
- **cached:** Whether result came from cache (no API call)

### Session Summary Requirement (MANDATORY)
**CRITICAL: At the end of EVERY task**, when writing a Summary section, you MUST:
1. **BEFORE writing the Summary**, call `mcp__enhanced-rlm__get_kb_session_stats`
2. Include the returned stats in your Summary under "Knowledge Base Usage"
3. If no KB queries were made, write: "Knowledge Base Usage: No queries this session"

**This is NOT optional. Every Summary MUST have this section.**

Example Summary format:
```
## Summary
[Task description and what was accomplished]

### Knowledge Base Usage
Session Total: 2847 tokens (input=2105, output=742) | Queries: 3 (1 cached)
```

### Token Efficiency Goals
- Target: <1500 input tokens for simple queries
- Target: <3000 input tokens for code example queries
- If consistently higher, review topic file sizes in `.claude/topics/`

### Resetting Stats
Use `mcp__enhanced-rlm__reset_kb_session_stats` at the start of a new task if you want to track token usage for that specific task only.

---

*This is an example CLAUDE.md demonstrating the recommended structure for Enhanced RLM MCP server.*
