# Knowledge Base Setup Guide for Enhanced RLM

This guide helps you transform any project into a well-organized knowledge base that works optimally with the Enhanced RLM MCP server.

## Quick Assessment

First, identify your current state:

| State | Description | Action |
|-------|-------------|--------|
| **A** | No `CLAUDE.md` or `.claude/` folder | Start from scratch |
| **B** | Only `CLAUDE.md` (one big file) | Split and organize |
| **C** | Both exist but unstructured | Reorganize |
| **D** | Well-structured | Just add MCP config |

---

## Setup Prompt for Claude Code

**Copy and paste the following prompt into your Claude Code chat session** to have Claude analyze and set up your knowledge base:

```
I want to set up the Enhanced RLM MCP server for this project to enable intelligent knowledge base retrieval.

Please help me:

1. **Analyze Current State**
   - Check if CLAUDE.md exists and its size/structure
   - Check if .claude/ folder exists and what's inside
   - Identify what documentation/rules already exist in the project

2. **Create Optimal Knowledge Base Structure**

   Target structure:
   ```
   project/
   ├── CLAUDE.md              <- Essential rules only (max 200 lines)
   └── .claude/
       ├── REFERENCE.md       <- Detailed patterns, conventions, API docs
       ├── code_examples/     <- Reusable code snippets by category
       │   ├── <category1>.ext
       │   └── <category2>.ext
       └── [topic docs].md    <- Specific topics (architecture, deployment, etc.)
   ```

3. **CLAUDE.md Should Contain ONLY:**
   - Project scope definition (when rules apply)
   - Critical rules that MUST be followed
   - Build/run commands
   - Key gotchas (max 10)
   - Links to detailed docs in .claude/

4. **Move to .claude/REFERENCE.md:**
   - Detailed code conventions
   - API documentation
   - Database schemas
   - Architecture details
   - Function signatures and patterns

5. **Create .claude/code_examples/:**
   - Extract code snippets from documentation
   - Organize by language/purpose
   - Add header comments explaining each example

6. **Set Up MCP Configuration**

   Create `.mcp.json` in project root:
   - For WSL projects: use `wsl.exe bash -lc` wrapper
   - For Windows native: use Windows Python path
   - Don't include API key (should be in environment)

7. **Set Up Auto-Approval**

   Add to `.claude/settings.json`:
   ```json
   {
     "permissions": {
       "allow": [
         "mcp__enhanced-rlm__ask_knowledge_base",
         "mcp__enhanced-rlm__list_knowledge_base",
         "mcp__enhanced-rlm__clear_knowledge_cache"
       ]
     }
   }
   ```

8. **Verify Setup**
   - After VS Code restart, check MCP server shows "connected"
   - Test with: ask_knowledge_base("What are the key rules for this project?")

Please start by analyzing my current project state and propose a transformation plan.
```

---

## Detailed Transformation Steps

### State A: Starting from Scratch

If your project has no documentation:

1. **Create `.claude/` folder**
2. **Create `CLAUDE.md`** with:
   ```markdown
   # [Project Name] - Essential Rules

   ## Scope
   These rules apply when working with files in this project.

   ## Build & Run
   - Build: `[command]`
   - Run: `[command]`
   - Test: `[command]`

   ## Key Rules
   1. [Most important rule]
   2. [Second most important]
   ...

   ## Quick Reference
   See [.claude/REFERENCE.md](.claude/REFERENCE.md) for detailed documentation.
   ```

3. **Create `.claude/REFERENCE.md`** with detailed patterns

### State B: One Big CLAUDE.md

If you have everything in one large file:

1. **Keep in CLAUDE.md** (first ~100-200 lines):
   - Scope definition
   - Build commands
   - Critical rules only
   - Key gotchas (condensed)

2. **Move to `.claude/REFERENCE.md`**:
   - Code conventions (detailed)
   - API documentation
   - Database patterns
   - Architecture explanations

3. **Move to `.claude/code_examples/`**:
   - All code blocks longer than 10 lines
   - Name files by purpose: `database_patterns.cs`, `api_examples.py`

### State C: Exists but Unstructured

If you have both but they're disorganized:

1. **Audit `.claude/` contents**
2. **Consolidate** related docs into `REFERENCE.md`
3. **Extract** code examples to `code_examples/`
4. **Slim down** `CLAUDE.md` to essentials
5. **Add cross-references** between files

---

## MCP Configuration Templates

### For WSL Projects (project in WSL, VS Code on Windows)

```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "wsl.exe",
      "args": [
        "bash",
        "-lc",
        "/home/YOUR_USER/cc-mpc-extended-rlm/.venv/bin/python -m enhanced_rlm.server --path /home/YOUR_USER/your-project"
      ],
      "env": {}
    }
  }
}
```

### For Windows Native Projects

```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "C:\\path\\to\\cc-mpc-extended-rlm\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "enhanced_rlm.server",
        "--path",
        "C:\\path\\to\\your-project"
      ],
      "env": {}
    }
  }
}
```

### For Linux/macOS Native

```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "/path/to/cc-mpc-extended-rlm/.venv/bin/python",
      "args": [
        "-m",
        "enhanced_rlm.server",
        "--path",
        "/path/to/your-project"
      ],
      "env": {}
    }
  }
}
```

---

## Best Practices for Knowledge Base Content

### CLAUDE.md Guidelines

| Do | Don't |
|----|-------|
| Keep under 200 lines | Put everything in one file |
| Use bullet points | Write long paragraphs |
| Link to detailed docs | Duplicate content |
| Focus on "must know" rules | Include rarely-used info |
| Update when rules change | Let it become stale |

### REFERENCE.md Guidelines

| Do | Don't |
|----|-------|
| Organize by topic with headers | Use flat structure |
| Include function signatures | Just describe vaguely |
| Add "See also" cross-references | Create isolated sections |
| Use tables for structured data | Use long prose |
| Include gotchas per section | Bury warnings in text |

### Code Examples Guidelines

| Do | Don't |
|----|-------|
| One concept per file | Mix unrelated examples |
| Add header comment explaining purpose | Leave unexplained |
| Show complete, working code | Show fragments |
| Use consistent naming | Random file names |
| Include both good and bad examples | Only show happy path |

---

## Validation Checklist

After setup, verify:

- [ ] `CLAUDE.md` is under 200 lines
- [ ] `.claude/REFERENCE.md` contains detailed docs
- [ ] `.claude/code_examples/` has organized snippets
- [ ] `.mcp.json` is in project root (no secrets!)
- [ ] `.claude/settings.json` has auto-approve permissions
- [ ] MCP server shows "connected" after VS Code restart
- [ ] `list_knowledge_base` returns expected structure
- [ ] `ask_knowledge_base` returns intelligent responses

---

## Troubleshooting

### MCP Server Not Connecting

1. Check Python venv path in `.mcp.json`
2. Verify `ANTHROPIC_API_KEY` is set in environment
3. For WSL: ensure using `-lc` flag, key in `~/.profile`

### Poor Search Results

1. Check if keywords match your documentation
2. Ensure important terms are in headers (ripgrep prioritizes these)
3. Add more specific terminology to docs

### Haiku Not Distilling

1. Verify API key: `echo $ANTHROPIC_API_KEY` (WSL) or `$env:ANTHROPIC_API_KEY` (PowerShell)
2. Check API credits at https://console.anthropic.com
3. Look for errors in Claude Code logs

---

## Example Transformation

**Before** (one 800-line CLAUDE.md):
```
CLAUDE.md (800 lines)
├── Project overview (50 lines)
├── Build instructions (30 lines)
├── Code conventions (200 lines)
├── Database patterns (150 lines)
├── API documentation (250 lines)
└── Troubleshooting (120 lines)
```

**After** (optimized structure):
```
CLAUDE.md (80 lines)
├── Scope definition (10 lines)
├── Build/run commands (15 lines)
├── Key rules (25 lines)
├── Quick gotchas (20 lines)
└── Links to .claude/ docs (10 lines)

.claude/
├── REFERENCE.md (400 lines)
│   ├── Code conventions
│   ├── Database patterns
│   └── API documentation
├── code_examples/
│   ├── database_queries.sql
│   ├── api_handlers.cs
│   └── validation_patterns.cs
└── TROUBLESHOOTING.md (120 lines)
```

---

*This guide is part of the [Enhanced RLM MCP Server](https://github.com/lukiies/cc-mpc-extended-rlm) project.*
