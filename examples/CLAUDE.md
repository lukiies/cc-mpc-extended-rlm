# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
- Files in this workspace ([PROJECT_NAME] codebase)
- Code in the [REPO_NAME] repository
- Development tasks for [PROJECT_NAME]
- [PRIMARY_TECH_STACK], or project-specific patterns
- [PROJECT_DOMAIN_DESCRIPTION]

**These rules DO NOT apply to general questions unrelated to this project.**

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

## Project Overview

[PROJECT_NAME] is a [brief description of your project].

**Knowledge Base Structure (modular - token efficient):**
- `.claude/INDEX.md` - Topic index with links
- `.claude/topics/` - Small, focused topic files (<100 lines each)
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

## Knowledge Base

For detailed information, see `.claude/` folder:
- [INDEX.md](.claude/INDEX.md) - Topic navigation
- [topics/](.claude/topics/) - Modular topic files
- [code_examples/](.claude/code_examples/) - Reusable code by language

**Modular KB principle:** Keep topic files small (<100 lines) so Haiku can extract relevant info efficiently. One concept = one file.

---

*This is an example CLAUDE.md demonstrating the recommended structure for Enhanced RLM MCP server.*
