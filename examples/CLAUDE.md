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
   | Project-specific | This project's `.claude/` folder | API quirks, framework gotchas, project conventions |
   | Universal/reusable | `cc-mcp-extended-rlm` repository | General coding patterns, tool usage tips, universal best practices |
   | Agent template improvement | Agent's `examples/CLAUDE.md` | Better rule phrasing, new section structure |

3. **Update concisely:**
   - Add to `TROUBLESHOOTING.md` for problems and solutions
   - Add to `REFERENCE.md` for patterns and conventions
   - Add to `code_examples/` for reusable code snippets
   - Update `CLAUDE.md` only for critical new rules

4. **Skip if no meaningful lessons** - Not every session produces learnings worth preserving.

5. **For cc-mcp-extended-rlm updates:** When lessons are project-agnostic and valuable for other projects, locate and update the agent repository (typically in a known path or via git clone from https://github.com/lukiies/cc-mpc-extended-rlm).

---

## Project Overview

[PROJECT_NAME] is a [brief description of your project].

**Knowledge Base:** `.claude/REFERENCE.md` contains detailed documentation.
**Code Examples:** `.claude/code_examples/` contains reusable patterns by language.

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

## Detailed Documentation

For detailed information, see `.claude/` folder:
- [REFERENCE.md](.claude/REFERENCE.md) - Full API docs, patterns, schemas
- [code_examples/](.claude/code_examples/) - Reusable code snippets by language

---

*This is an example CLAUDE.md demonstrating the recommended structure for Enhanced RLM MCP server.*
