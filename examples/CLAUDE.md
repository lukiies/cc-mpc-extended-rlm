# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
- Files in this workspace (Example Project codebase)
- Code in the example-project repository
- Development tasks for Example Project
- JavaScript/TypeScript, Node.js, or project-specific patterns
- Web application development

**These rules DO NOT apply to general questions unrelated to this project.**

---

## Project Overview

Example Project is a web application demonstrating Enhanced RLM integration.

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
