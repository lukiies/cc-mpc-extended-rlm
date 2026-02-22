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

### Auto Memory Reinforcement (CRITICAL)

CLAUDE.md instructions alone are **not sufficient** to guarantee the startup check runs — they can be overlooked. You MUST also have this rule in your **persistent auto memory** (`MEMORY.md` in your auto memory directory).

**On first session with any new project**, check if your auto memory contains a "MANDATORY SESSION STARTUP CHECK" section. If it does NOT exist, add it immediately:

```markdown
## MANDATORY SESSION STARTUP CHECK (BEFORE ANYTHING ELSE)
- **FIRST action in EVERY new conversation:** Call `mcp__enhanced-rlm__get_kb_session_stats` BEFORE responding to the user's first message
- Display the greeting: `cc-mpc-extended-rlm is active. Knowledge base status: OK` (or WARNING if it fails)
- **This is NOT optional** — do it before even reading the user's question
```

**Why both locations?** Auto memory is loaded directly into the system prompt and is more reliably followed than CLAUDE.md project instructions. The CLAUDE.md rule is the source of truth; the auto memory entry ensures compliance.

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

**After completing tasks with 100% success** (all tests pass, no errors, user confirms satisfaction), you MUST:

1. **Analyze the session** for lessons learned:
   - New patterns or solutions discovered
   - Gotchas encountered and resolved
   - Effective approaches worth preserving
   - Mistakes made and how they were fixed

2. **Route updates to the appropriate target:**

   | Lesson Type | Target Location | Examples |
   |-------------|-----------------|----------|
   | Project-specific | `.claude/topics/<topic>.md` | API quirks, framework gotchas, project conventions |
   | Universal/reusable | `cc-mcp-extended-rlm` repository | General coding patterns, tool usage tips, universal best practices |
   | Agent template improvement | Agent's `examples/CLAUDE.md` | Better rule phrasing, new section structure |

3. **Update using modular topic files:**
   - Add/update topic files in `.claude/topics/` (one topic per file, <100 lines)
   - Add code examples to `.claude/code_examples/`
   - Update `.claude/INDEX.md` when adding new topics
   - Update `CLAUDE.md` only for critical new rules

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

## Knowledge Base

For detailed information, see `.claude/` folder:
- [INDEX.md](.claude/INDEX.md) - Topic navigation
- [topics/](.claude/topics/) - Modular topic files
- [code_examples/](.claude/code_examples/) - Reusable code by language

**Modular KB principle:** Keep topic files small (<100 lines) so Haiku can extract relevant info efficiently. One concept = one file.

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
