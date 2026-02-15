# Knowledge Base Setup Guide for Enhanced RLM

This guide helps you transform any project into a well-organized knowledge base that works optimally with the Enhanced RLM MCP server.

---

## CRITICAL: CLAUDE.md Scope Header

**Every CLAUDE.md file MUST start with a scope definition header.** This header ensures the rules are only applied when relevant to the specific project, preventing confusion in multi-project environments.

### Self-Learning Protocol (Recommended)

Immediately after the scope header, include the **Self-Learning Protocol** section. This enables Claude to automatically improve your knowledge base after successful task completions:

```markdown
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

5. **For cc-mcp-extended-rlm updates:** When lessons are project-agnostic and valuable for other projects, update the agent repository.
```

This creates a continuous improvement loop where your knowledge base gets smarter with each successful session.

### Required Header Template

```markdown
# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
- Files in this workspace ([PROJECT_NAME] codebase)
- Code in the [REPO_NAME] repository
- Development tasks for [PROJECT_NAME]
- [PRIMARY_TECH_STACK], or project-specific patterns
- [PROJECT_DOMAIN_DESCRIPTION]

**These rules DO NOT apply to general questions unrelated to this project.**

---
```

### Customization Instructions

When setting up a new project, Claude Code should automatically:

1. **Replace placeholders** with project-specific values:
   - `[PROJECT_NAME]` - The name of the project (e.g., "eFakt2", "SoftWork Professional")
   - `[REPO_NAME]` - The repository name (e.g., "efakt2", "cvs_ls26")
   - `[PRIMARY_TECH_STACK]` - Main technologies (e.g., "ASP.NET Core, React/TypeScript", "ITK-Clip/Harbour, Sybase")
   - `[PROJECT_DOMAIN_DESCRIPTION]` - Brief domain context (e.g., "Polish KSeF invoice integration", "Financial software for LSP market")

2. **Auto-detect from project** when possible:
   - Read `package.json`, `*.csproj`, `Cargo.toml`, etc. for tech stack
   - Read existing README.md for project description
   - Use folder name as fallback project name

### Example Headers

**For a .NET + React project:**
```markdown
# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
- Files in this workspace (eFakt2 codebase)
- Code in the efakt2 repository
- Development tasks for eFakt2 KSeF integration
- ASP.NET Core, React/TypeScript, or project-specific patterns
- Polish KSeF (National e-Invoice System) integration

**These rules DO NOT apply to general questions unrelated to this project.**

---
```

**For a Harbour/xBase project:**
```markdown
# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
- Files in this workspace (SoftWork Professional codebase)
- Code in the cvs_ls26 repository
- Development tasks for SoftWork Professional
- ITK-Clip/Harbour, Sybase, or project-specific patterns
- Financial/accounting software for the LSP market

**These rules DO NOT apply to general questions unrelated to this project.**

---
```

**For a Python project:**
```markdown
# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
- Files in this workspace (DataProcessor codebase)
- Code in the data-processor repository
- Development tasks for DataProcessor
- Python, pandas, FastAPI, or project-specific patterns
- ETL pipeline and data transformation tasks

**These rules DO NOT apply to general questions unrelated to this project.**

---
```

---

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
   ├── CLAUDE.md              <- Essential rules (size based on project complexity)
   │                             MUST start with scope header (see above)
   └── .claude/
       ├── INDEX.md           <- Topic navigation index
       ├── topics/            <- MODULAR topic files (<100 lines each)
       │   ├── encoding.md
       │   ├── build-system.md
       │   ├── troubleshooting.md
       │   └── [topic].md
       ├── code_examples/     <- Reusable code snippets organized by language
       │   ├── csharp/        <- C# examples (.cs files)
       │   ├── typescript/    <- TypeScript examples (.ts, .tsx files)
       │   ├── python/        <- Python examples (.py files)
       │   └── [language]/    <- Other languages as needed
       └── REFERENCE.md       <- (Legacy) or for very large reference tables
   ```

   **IMPORTANT - Modular KB Principle:**
   - Topic files in `.claude/topics/` should be focused (~100 lines target)
   - One concept = one file (this is what enables the ~100 line target)
   - This enables efficient Haiku extraction (lower token usage)
   - Note: CLAUDE.md and REFERENCE.md can be larger as they serve different purposes
   - Use INDEX.md for navigation between topics

3. **CLAUDE.md MUST Start With Scope Header:**

   The VERY FIRST content in CLAUDE.md must be the scope definition:
   ```markdown
   # Project Rules - Scope Definition

   **IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
   - Files in this workspace ([PROJECT_NAME] codebase)
   - Code in the [REPO_NAME] repository
   - Development tasks for [PROJECT_NAME]
   - [PRIMARY_TECH_STACK], or project-specific patterns
   - [PROJECT_DOMAIN_DESCRIPTION]

   **These rules DO NOT apply to general questions unrelated to this project.**

   ---
   ```

   After the scope header, add **Self-Learning Protocol** and **Mandatory Test Requirement**:
   ```markdown
   ## Self-Learning Protocol

   **After completing tasks with 100% success** (all tests pass, no errors, user confirms satisfaction), you MUST:

   1. **Analyze the session** for lessons learned
   2. **Route updates appropriately:**
      - Project-specific → `.claude/topics/<topic>.md`
      - Universal/reusable → `cc-mcp-extended-rlm` repository
   3. **Update using modular topic files** (<100 lines each)
   4. **Skip if no meaningful lessons**

   ## Mandatory Test Requirement

   **Every new feature MUST have a test procedure defined BEFORE development.**

   1. Ask for test scenario if not provided
   2. Define: steps, expected results, edge cases
   3. Run test after implementation to verify
   4. Update knowledge base with practical learnings
   ```

   After these required sections, CLAUDE.md should contain ONLY:
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

5. **Create .claude/code_examples/ with Language Subfolders:**
   - Create subfolders for each language used in the project:
     - `csharp/` for `.cs` files
     - `typescript/` for `.ts`, `.tsx` files
     - `python/` for `.py` files
     - `sql/` for `.sql` files
     - `powershell/` for `.ps1` files
     - `bash/` for `.sh` files
   - Extract code snippets from documentation into appropriate subfolders
   - Add header comments explaining each example
   - Use descriptive filenames: `database_patterns.cs`, `api_handlers.ts`

6. **Set Up MCP Configuration**

   Create `.mcp.json` in project root:
   - For WSL projects with VS Code WSL Remote: use `bash -c` (NOT `wsl.exe`)
   - For WSL projects without WSL Remote (VS Code on Windows): use `wsl.exe bash -lc`
   - For Windows native: use Windows Python path
   - Don't include API key (should be in environment)

7. **Set Up Auto-Approval**

   Add to `.claude/settings.local.json` for full autonomous operation (all Claude Code tools + MCP tools):
   ```json
   {
     "permissions": {
       "allow": [
         "Bash(*)",
         "Edit(*)",
         "Write(*)",
         "Read(*)",
         "Glob(*)",
         "Grep(*)",
         "WebFetch(*)",
         "WebSearch(*)",
         "Task(*)",
         "TodoWrite(*)",
         "NotebookEdit(*)",
         "mcp__enhanced-rlm__ask_knowledge_base",
         "mcp__enhanced-rlm__list_knowledge_base",
         "mcp__enhanced-rlm__clear_knowledge_cache",
         "mcp__enhanced-rlm__get_kb_session_stats",
         "mcp__enhanced-rlm__reset_kb_session_stats"
       ]
     }
   }
   ```

   A ready-to-use template is at [`examples/.claude/settings.local.json`](../examples/.claude/settings.local.json).

   **Important:** `Task(*)`, `TodoWrite(*)`, and `NotebookEdit(*)` are frequently overlooked but required for autonomous subagent launching and task tracking. Without them, Claude Code prompts for confirmation on every subagent call.

8. **Set Up Auto Memory Startup Check**

   Claude Code has a persistent auto memory directory (`MEMORY.md`) that is injected into the system prompt. Rules placed here are more reliably followed than CLAUDE.md instructions alone.

   **On the very first session** with this project, Claude MUST check its auto memory for the startup check rule and add it if missing:

   ```markdown
   ## MANDATORY SESSION STARTUP CHECK (BEFORE ANYTHING ELSE)
   - **FIRST action in EVERY new conversation:** Call `mcp__enhanced-rlm__get_kb_session_stats` BEFORE responding to the user's first message
   - Display the greeting: `cc-mpc-extended-rlm is active. Knowledge base status: OK` (or WARNING if it fails)
   - **This is NOT optional** — do it before even reading the user's question
   ```

   **Why this matters:** Without auto memory reinforcement, Claude frequently "forgets" to run the startup check despite it being in CLAUDE.md. This dual-location approach ensures compliance.

9. **Verify Setup**
   - After VS Code restart, check MCP server shows "connected"
   - Test with: ask_knowledge_base("What are the key rules for this project?")

Please start by analyzing my current project state and propose a transformation plan.
```

---

## Detailed Transformation Steps

### State A: Starting from Scratch

If your project has no documentation:

1. **Create `.claude/` folder** with language subfolders:
   ```
   .claude/
   ├── code_examples/
   │   ├── csharp/       # If project uses C#
   │   ├── typescript/   # If project uses TypeScript
   │   ├── python/       # If project uses Python
   │   └── [language]/   # Other languages as needed
   ```

2. **Create `CLAUDE.md`** with scope header FIRST:
   ```markdown
   # Project Rules - Scope Definition

   **IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
   - Files in this workspace ([PROJECT_NAME] codebase)
   - Code in the [REPO_NAME] repository
   - Development tasks for [PROJECT_NAME]
   - [PRIMARY_TECH_STACK], or project-specific patterns
   - [PROJECT_DOMAIN_DESCRIPTION]

   **These rules DO NOT apply to general questions unrelated to this project.**

   ---

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

1. **Add scope header as FIRST content** in CLAUDE.md:
   ```markdown
   # Project Rules - Scope Definition

   **IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
   - Files in this workspace ([PROJECT_NAME] codebase)
   - [... customize for your project ...]

   **These rules DO NOT apply to general questions unrelated to this project.**

   ---
   ```

2. **Keep in CLAUDE.md** (after header, ~100-150 lines max):
   - Build commands
   - Critical rules only
   - Key gotchas (condensed)
   - Links to .claude/ folder

3. **Move to `.claude/REFERENCE.md`**:
   - Code conventions (detailed)
   - API documentation
   - Database patterns
   - Architecture explanations

4. **Move to `.claude/code_examples/[language]/`**:
   - Create subfolders for each language
   - All code blocks longer than 10 lines
   - Name files by purpose: `csharp/database_patterns.cs`, `python/api_examples.py`

### State C: Exists but Unstructured

If you have both but they're disorganized:

1. **Audit `.claude/` contents**
2. **Consolidate** related docs into `REFERENCE.md`
3. **Extract** code examples to `code_examples/`
4. **Slim down** `CLAUDE.md` to essentials
5. **Add cross-references** between files

---

## MCP Configuration Templates

### For WSL Projects - VS Code WSL Remote (Recommended)

If VS Code connects via WSL Remote extension (bottom-left shows "WSL: Ubuntu"):

```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-c",
        "/home/YOUR_USER/cc-mpc-extended-rlm/start_server.sh --path /home/YOUR_USER/your-project"
      ],
      "env": {}
    }
  }
}
```

### For WSL Projects - VS Code on Windows (without WSL Remote)

If VS Code runs natively on Windows without WSL Remote extension:

```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "wsl.exe",
      "args": [
        "bash",
        "-lc",
        "/home/YOUR_USER/cc-mpc-extended-rlm/start_server.sh --path /home/YOUR_USER/your-project"
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

**Size principle:** CLAUDE.md should be as small as possible while containing ALL critical rules. Quality over arbitrary line limits.

| Project Complexity | Typical CLAUDE.md Size | Notes |
|--------------------|------------------------|-------|
| Simple (single tech, few rules) | 50-150 lines | Basic projects |
| Medium (multi-component) | 150-300 lines | Most projects |
| Complex (enterprise, regulations) | 300-500+ lines | KSeF, HIPAA, financial systems |

| Do | Don't |
|----|-------|
| Include ALL critical rules | Scatter important rules across files |
| Use bullet points and tables | Write long paragraphs |
| Link to detailed docs for reference material | Duplicate content between files |
| Focus on "must follow" rules | Include nice-to-have suggestions |
| Keep rules that prevent errors | Move critical rules to obscure files |

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

### Folder Naming Guidelines

| Do | Don't |
|----|-------|
| Use regular folder names: `pre-requisites/`, `topics/` | Use hidden folders: `.prompts/`, `.internal/` |
| Keep subfolders in `.claude/` visible | Nest hidden folders inside `.claude/` |
| Use descriptive names: `research/`, `planning/` | Use cryptic names |

**Why this matters:** Folders starting with `.` (dot) are treated as hidden by ripgrep and may not be searched properly, even when inside `.claude/`. The `.claude/` folder itself is an exception configured in the search paths.

### INDEX.md Best Practices

Create an `INDEX.md` in `.claude/` with:

1. **Document table with keywords:**
   ```markdown
   | Document | Purpose | Keywords |
   |----------|---------|----------|
   | [REFERENCE.md](REFERENCE.md) | API docs | API, endpoints, models |
   | [pre-requisites/RESEARCH.md](pre-requisites/RESEARCH.md) | Market analysis | competitors, integration, format |
   ```

2. **Quick reference sections by topic:**
   ```markdown
   ### Topic: Authentication
   See: [REFERENCE.md](REFERENCE.md#authentication)
   - JWT tokens
   - Session management
   - OAuth integration
   ```

**Why keywords matter:** The MCP server uses ripgrep to search. Adding explicit keywords in INDEX.md improves search discoverability, especially for documents that might use different terminology than the search query.

### Pre-requisites Folder Pattern

For research, planning, or analysis documents that inform future development:

```
.claude/
├── pre-requisites/           <- Research & planning docs
│   ├── COMPETITOR_ANALYSIS.md
│   ├── ARCHITECTURE_DECISIONS.md
│   └── INTEGRATION_RESEARCH.md
├── REFERENCE.md              <- Implementation reference
└── TROUBLESHOOTING.md        <- Problem solving
```

**Use pre-requisites/ for:**
- Market research and competitor analysis
- Architecture decision records (ADRs)
- Integration planning documents
- Technology evaluation reports
- Requirements gathered before development

**Benefits:**
- Keeps implementation docs separate from planning docs
- New team members can understand "why" decisions were made
- Future development phases can reference earlier research

---

## Validation Checklist

After setup, verify:

- [ ] `CLAUDE.md` starts with scope definition header (Project Rules - Scope Definition)
- [ ] `CLAUDE.md` includes Self-Learning Protocol section (after scope header)
- [ ] `CLAUDE.md` contains all critical rules (size appropriate to project complexity)
- [ ] Scope header has customized project name, tech stack, and domain
- [ ] `.claude/REFERENCE.md` contains detailed docs
- [ ] `.claude/code_examples/` has language-specific subfolders (e.g., `csharp/`, `typescript/`)
- [ ] `.mcp.json` is in project root (no secrets!)
- [ ] `.claude/settings.local.json` has full auto-approve permissions (all Claude Code + MCP tools)
- [ ] MCP server shows "connected" after VS Code restart
- [ ] `list_knowledge_base` returns expected structure
- [ ] `ask_knowledge_base` returns intelligent responses
- [ ] Auto memory (`MEMORY.md`) contains "MANDATORY SESSION STARTUP CHECK" section
- [ ] First message in new conversation displays `cc-mpc-extended-rlm is active` greeting

---

## Troubleshooting

### MCP Server Not Connecting

1. Check Python venv path in `.mcp.json`
2. Verify `ANTHROPIC_API_KEY` is set in environment
3. For WSL with VS Code WSL Remote: use `bash -c` (NOT `wsl.exe`) - using `wsl.exe` from within WSL breaks the MCP stdio protocol
4. For WSL without WSL Remote: use `wsl.exe bash -lc`, ensure key is in `~/.profile`
5. Check `.sync.log` in the server directory for platform detection and error messages

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
CLAUDE.md (size varies by project complexity)
├── Scope definition header        <- MUST be first!
├── Self-learning protocol
├── Critical rules (ALL of them!)
├── Build/run commands
├── Key gotchas
└── Links to .claude/ docs

.claude/
├── INDEX.md                 <- Topic index with keywords (improves search!)
├── REFERENCE.md (400 lines)
│   ├── Code conventions
│   ├── Database patterns
│   └── API documentation
├── TROUBLESHOOTING.md (120 lines)
├── pre-requisites/          <- Research & planning docs
│   ├── ARCHITECTURE_DECISIONS.md
│   └── INTEGRATION_RESEARCH.md
└── code_examples/           <- Language-specific subfolders
    ├── csharp/
    │   ├── database_patterns.cs
    │   └── validation_patterns.cs
    ├── typescript/
    │   └── api_handlers.ts
    └── sql/
        └── database_queries.sql
```

---

*This guide is part of the [Enhanced RLM MCP Server](https://github.com/lukiies/cc-mpc-extended-rlm) project.*
