# Enhanced RLM - MCP Server for Knowledge Base Retrieval

An MCP (Model Context Protocol) server that provides intelligent, token-efficient knowledge base retrieval for Claude Code sessions. Based on [RLM research principles](https://arxiv.org/abs/2512.24601) (arXiv:2512.24601v1) from MIT.

## Features

- **Intelligent Search**: Ripgrep-powered search across your project's knowledge base
- **Claude Haiku Distillation**: Uses Claude Haiku 3.5 to extract only relevant information from search results
- **Dynamic Token Budgets**: Adjusts response size based on query type (1K-6K tokens)
- **Response Caching**: Caches Haiku responses for 1 hour to reduce API calls
- **Workspace-Specific**: Each project uses its own `CLAUDE.md` and `.claude/` folder
- **Cross-Platform**: Works on Linux, macOS, and Windows (including WSL)
- **Self-Learning Protocol**: Built-in rules for Claude to update knowledge base after successful task completions
- **Auto-Pull on Startup**: Automatically pulls latest from GitHub on VS Code reload, ensuring all projects run the same version

## Architecture

```
Claude Code (VS Code)     <- Uses Claude.ai Max subscription (Opus)
        |
        v
MCP Server (Python)       <- Keyword extraction, ripgrep search, chunking, ranking
        |
        v
Claude Haiku 3.5 API      <- Smart filtering and distillation (requires API key)
```

**Key insight from RLM research**: Simple grep-like filtering before reading files is highly effective - sophisticated RAG/embeddings are not always necessary.

## Installation

### Prerequisites

- Python 3.10+
- `ripgrep` installed (`rg` command available)
- Anthropic API key (for Haiku distillation - optional but recommended)

### Step 1: Install ripgrep

```bash
# Ubuntu/Debian (WSL included)
sudo apt install ripgrep

# macOS
brew install ripgrep

# Windows (via winget)
winget install BurntSushi.ripgrep.MSVC
```

### Step 2: Clone and install the MCP server

```bash
# Clone the repository
git clone https://github.com/lukiies/cc-mpc-extended-rlm.git
cd cc-mpc-extended-rlm

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS/WSL
# or: .venv\Scripts\activate  # Windows PowerShell

# Install the package
pip install -e .
```

### Step 3: Set up Anthropic API Key

The API key should be stored in your system environment (NOT in config files) for security.

#### For WSL/Linux users:

Add to your `~/.profile` (recommended for WSL) or `~/.zshrc`:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

**Important for WSL**: Use `~/.profile` instead of `~/.bashrc`. The `.bashrc` file typically exits early for non-interactive shells, which prevents the API key from being loaded when using `bash -lc`.

Then reload:
```bash
source ~/.profile
```

#### For Windows users:

**Option A: Via PowerShell (recommended)**
```powershell
[Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-api03-your-key-here', 'User')
```

**Option B: Via GUI**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to "Advanced" tab → "Environment Variables"
3. Under "User variables", click "New"
4. Variable name: `ANTHROPIC_API_KEY`
5. Variable value: `sk-ant-api03-your-key-here`
6. Click OK and restart VS Code

#### For macOS users:

Add to your `~/.zshrc`:
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

## Configuration

Create a `.mcp.json` file in your project root. Choose the configuration that matches your setup.

### Auto-Pull Feature (Recommended)

The `start_server.sh` (Linux/macOS/WSL) and `start_server.bat` (Windows) wrapper scripts provide **automatic updates** from GitHub on every VS Code reload:

1. **Pulls latest changes** from GitHub (updates from other projects)
2. **Starts the MCP server**

**Note:** Push happens when you explicitly accept self-learning updates during a session (not on startup).

This ensures all your projects always run the latest version of the agent without manual intervention.

### Option 1: Linux/macOS (Native) - With Auto-Pull

```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "/path/to/cc-mpc-extended-rlm/start_server.sh",
      "args": [
        "--path",
        "/path/to/your/project"
      ],
      "env": {}
    }
  }
}
```

### Option 2: Windows + WSL Projects (Recommended) - With Auto-Pull

If your project is in WSL but VS Code/Claude Code runs on Windows:

```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "wsl.exe",
      "args": [
        "bash",
        "-lc",
        "/path/to/cc-mpc-extended-rlm/start_server.sh --path /path/to/your/project"
      ],
      "env": {}
    }
  }
}
```

**Important**: The `-lc` flag makes bash load your login profile (including `ANTHROPIC_API_KEY` from `~/.profile`).

### Option 3: Windows Native Projects - With Auto-Pull

For projects located on Windows filesystem (not WSL), use the included `start_server.bat`:

```batch
@echo off
cd /d "%~dp0"
git fetch origin 2>nul
git merge --ff-only origin/main 2>nul
"%~dp0.venv\Scripts\python.exe" -m enhanced_rlm.server %*
```

Configure `.mcp.json`:

```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "C:\\path\\to\\cc-mpc-extended-rlm\\start_server.bat",
      "args": [
        "--path",
        "C:\\path\\to\\your\\project"
      ],
      "env": {}
    }
  }
}
```

### Legacy Configuration (Without Auto-Pull)

If you prefer manual updates, you can still use the Python module directly:

<details>
<summary>Click to expand legacy configuration</summary>

**Linux/macOS:**
```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "/path/to/cc-mpc-extended-rlm/.venv/bin/python",
      "args": ["-m", "enhanced_rlm.server", "--path", "/path/to/your/project"],
      "env": {}
    }
  }
}
```

**Windows + WSL:**
```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "wsl.exe",
      "args": ["bash", "-lc", "/path/to/cc-mpc-extended-rlm/.venv/bin/python -m enhanced_rlm.server --path /path/to/your/project"],
      "env": {}
    }
  }
}
```

**Windows Native:**
```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "C:\\path\\to\\cc-mpc-extended-rlm\\.venv\\Scripts\\python.exe",
      "args": ["-m", "enhanced_rlm.server", "--path", "C:\\path\\to\\your\\project"],
      "env": {}
    }
  }
}
```

</details>

### Migrating Existing Projects

To update an existing project to use auto-pull:

1. Update your `.mcp.json` to use `start_server.sh` (Linux/macOS/WSL) or `start_server.bat` (Windows) instead of calling Python directly
2. Reload VS Code window (`Ctrl+Shift+P` → "Developer: Reload Window")
3. The MCP server will now auto-pull latest changes on every reload

The server will automatically read `ANTHROPIC_API_KEY` from environment variables.

### Auto-approve MCP tools (optional)

Add to your project's `.claude/settings.json` to skip approval prompts:

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

## Knowledge Base Structure

The server searches a modular knowledge base in your project:

```
your-project/
├── CLAUDE.md              <- PRIMARY: Essential rules (MUST start with scope header)
└── .claude/               <- SECONDARY: Detailed documentation
    ├── INDEX.md           <- Topic navigation index
    ├── topics/            <- MODULAR topic files (<100 lines each!)
    │   ├── encoding.md
    │   ├── build-system.md
    │   ├── troubleshooting.md
    │   └── [topic].md
    ├── code_examples/     <- Reusable code snippets by language
    │   ├── python/
    │   ├── typescript/
    │   └── [language]/
    └── REFERENCE.md       <- (Legacy/fallback for large reference tables)
```

**Modular KB Principle:** Keep topic files SMALL (<100 lines). One concept = one file. This enables efficient Haiku extraction with lower token usage.

### CLAUDE.md Scope Header (Required)

Every CLAUDE.md **MUST** start with a scope definition header:

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

This ensures rules are only applied when relevant to the specific project.

### Self-Learning Protocol (Required)

Every CLAUDE.md **SHOULD** include the Self-Learning Protocol section immediately after the scope header. This enables Claude to automatically improve the knowledge base over time:

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
   | Project-specific | `.claude/topics/<topic>.md` | API quirks, framework gotchas, project conventions |
   | Universal/reusable | `cc-mcp-extended-rlm` repository | General coding patterns, tool usage tips, universal best practices |
   | Agent template improvement | Agent's `examples/CLAUDE.md` | Better rule phrasing, new section structure |

3. **Update using modular topic files:**
   - Add/update topic files in `.claude/topics/` (<100 lines each!)
   - Add code examples to `.claude/code_examples/`
   - Update `.claude/INDEX.md` when adding new topics
   - Update `CLAUDE.md` only for critical new rules

4. **Skip if no meaningful lessons** - Not every session produces learnings worth preserving.

5. **For cc-mcp-extended-rlm updates:** When lessons are project-agnostic and valuable for other projects, update the agent repository.
```

### Mandatory Test Requirement (Required)

Every CLAUDE.md **SHOULD** include the Mandatory Test Requirement section:

```markdown
## Mandatory Test Requirement

**Every new feature MUST have a test procedure defined BEFORE development.**

1. Ask for test scenario if not provided
2. Define: steps, expected results, edge cases
3. Run test after implementation to verify
4. Update knowledge base with practical learnings
```

This creates a feedback loop where Claude improves both project-specific documentation and the agent itself based on real-world usage.

### Supported file types in knowledge base

- Markdown: `*.md`
- Source code: `*.prg`, `*.c`, `*.h`, `*.ch`, `*.py`

### Setting up your knowledge base

For detailed instructions on transforming any project into an optimized knowledge base structure, see the [Knowledge Base Setup Guide](docs/KNOWLEDGE_BASE_SETUP_GUIDE.md). This guide includes:

- Quick assessment of your current state
- A complete prompt to paste into Claude Code for automated setup
- Detailed transformation steps for different scenarios
- Best practices for organizing documentation

## Available MCP Tools

### `ask_knowledge_base(query, context?)`

Search the knowledge base for relevant information.

**Parameters:**
- `query` (required): Natural language question
- `context` (optional): Current file or topic for additional context

**Example queries:**
- "How do I add a new option to the application?"
- "Show me code example for database transaction"
- "Explain the architecture layers"
- "What are the key gotchas?"

### `list_knowledge_base()`

List the structure of the knowledge base (files and sizes).

### `clear_knowledge_cache()`

Clear the Haiku response cache (useful after updating documentation).

## Dynamic Token Budgets

The server automatically classifies queries and adjusts the Haiku token budget:

| Query Type | Token Budget | Trigger Keywords |
|------------|--------------|------------------|
| Simple | ~1,000 | Default for quick questions |
| Code Examples | ~4,000 | "example", "code", "how to", "implement", "pattern" |
| Complex | ~6,000 | "explain", "architecture", "design", "overview", "analyze" |

## How It Works

1. **Keyword Extraction**: Extracts meaningful keywords from your query (removes stop words)
2. **Ripgrep Search**: Fast search across CLAUDE.md and .claude/ folder
3. **Chunking**: Splits results into meaningful chunks (by headers, code blocks)
4. **Ranking**: Ranks chunks by keyword relevance using TF-IDF-like scoring
5. **Deduplication**: Removes redundant chunks
6. **Haiku Distillation**: Sends top chunks to Claude Haiku for intelligent summarization
7. **Caching**: Caches responses for 1 hour

## Running Without Haiku (Fallback Mode)

If `ANTHROPIC_API_KEY` is not set, the server returns raw ranked chunks without distillation. This is useful for:
- Testing the search functionality
- Avoiding API costs during development
- Environments where API access is restricted

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run a specific test
pytest tests/test_search.py -v

# Lint
ruff check src/
```

## Troubleshooting

### MCP server shows "failed" status

1. Check if Python venv path is correct
2. Verify ripgrep is installed: `rg --version`
3. Check Claude Code logs for error messages

### No results returned

1. Verify CLAUDE.md or .claude/ folder exists in your project
2. Check if the search keywords match content in your docs
3. Try `list_knowledge_base` to verify detection

### Haiku distillation not working

1. Verify `ANTHROPIC_API_KEY` is set in your environment:
   - WSL/Linux: `echo $ANTHROPIC_API_KEY`
   - Windows PowerShell: `$env:ANTHROPIC_API_KEY`
2. For WSL: ensure you're using `-lc` flag (not `-c`) to load bash profile
3. Check if you have API credits available at https://console.anthropic.com

### WSL path issues

- Use native Linux paths (e.g., `/home/user/project`)
- Don't use Windows UNC paths (`\\wsl.localhost\...`) in the `--path` argument
- The `-lc` flag is required for WSL to load environment variables from `~/.profile`

## Token Usage Statistics

Currently, the server does not track token usage statistics. Haiku API usage can be monitored through your [Anthropic dashboard](https://console.anthropic.com).

Future enhancement: Add token tracking and reporting.

## Cross-Platform Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | Full support | Native ripgrep, env vars from shell profile |
| macOS | Full support | Native ripgrep, env vars from shell profile |
| Windows (native) | Full support | ripgrep via winget, env vars from Windows User Environment |
| Windows + WSL | Full support | Use `wsl.exe bash -lc` wrapper, env vars from `~/.profile` |

## Security Notes

- **Never commit API keys** to version control
- Store `ANTHROPIC_API_KEY` in system environment variables only
- The `.mcp.json` file can be committed if it doesn't contain secrets (using `-lc` approach)
- Add `.mcp.json` to `.gitignore` if you prefer to keep it private

## License

MIT License - see [LICENSE](LICENSE) file.

## Credits

- Based on [RLM research](https://arxiv.org/abs/2512.24601) (arXiv:2512.24601v1) - "Recursive Language Models" from MIT
- Uses [FastMCP](https://github.com/jlowin/fastmcp) for MCP server implementation
- Powered by [Claude Haiku 3.5](https://anthropic.com) for intelligent distillation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

---

*Built for use with [Claude Code](https://claude.ai/claude-code) - Anthropic's official CLI for Claude*
