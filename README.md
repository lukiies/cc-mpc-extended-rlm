# Enhanced RLM - MCP Server for Knowledge Base Retrieval

An MCP (Model Context Protocol) server that provides intelligent, token-efficient knowledge base retrieval for Claude Code sessions. Based on [RLM research principles](https://arxiv.org/abs/2512.24601) (arXiv:2512.24601v1) from MIT.

## Features

- **Intelligent Search**: Ripgrep-powered search across your project's knowledge base
- **Claude Haiku Distillation**: Uses Claude Haiku 3.5 to extract only relevant information from search results
- **Dynamic Token Budgets**: Adjusts response size based on query type (1K-6K tokens)
- **Response Caching**: Caches Haiku responses for 1 hour to reduce API calls
- **Workspace-Specific**: Each project uses its own `CLAUDE.md` and `.claude/` folder
- **Cross-Platform**: Works on Linux, macOS, and Windows (including WSL)

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

### Install ripgrep

```bash
# Ubuntu/Debian
sudo apt install ripgrep

# macOS
brew install ripgrep

# Windows (via winget)
winget install BurntSushi.ripgrep.MSVC
```

### Install the MCP server

```bash
git clone https://github.com/lukiies/cc-mpc-extended-rlm.git
cd cc-mpc-extended-rlm

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install
pip install -e .
```

## Configuration

### Option 1: Linux/macOS (Native)

Create `.mcp.json` in your project root:

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
        "/path/to/your/project"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-api03-..."
      }
    }
  }
}
```

### Option 2: Windows with WSL (Recommended for WSL projects)

If your project is in WSL but Claude Code runs on Windows, use this configuration:

```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "type": "stdio",
      "command": "wsl.exe",
      "args": [
        "bash",
        "-c",
        "ANTHROPIC_API_KEY='sk-ant-api03-...' /path/to/cc-mpc-extended-rlm/.venv/bin/python -m enhanced_rlm.server --path /path/to/your/project"
      ],
      "env": {}
    }
  }
}
```

**Note**: Environment variables in the `env` block don't pass through `wsl.exe`, so the API key must be set inline in the bash command.

### Option 3: Windows Native

For native Windows projects (not in WSL):

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
        "C:\\path\\to\\your\\project"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-api03-..."
      }
    }
  }
}
```

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

The server searches a two-level knowledge base in your project:

```
your-project/
├── CLAUDE.md              <- PRIMARY: Main rules file (always searched first)
└── .claude/               <- SECONDARY: Detailed documentation
    ├── REFERENCE.md       <- Detailed patterns and conventions
    ├── code_examples/     <- Reusable code snippets
    │   ├── example1.py
    │   └── example2.js
    └── [other docs].md
```

### Supported file types in knowledge base

- Markdown: `*.md`
- Source code: `*.prg`, `*.c`, `*.h`, `*.ch`, `*.py`

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

1. Verify `ANTHROPIC_API_KEY` is set correctly
2. For WSL: API key must be in the bash command, not in `env` block
3. Check if you have API credits available

### WSL path issues

- Use native Linux paths (e.g., `/home/user/project`)
- Don't use Windows UNC paths (`\\wsl.localhost\...`) in the `--path` argument

## Token Usage Statistics

Currently, the server does not track token usage statistics. Haiku API usage can be monitored through your Anthropic dashboard.

Future enhancement: Add token tracking and reporting.

## Cross-Platform Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | Full support | Native ripgrep |
| macOS | Full support | Native ripgrep |
| Windows (native) | Full support | Requires ripgrep installation |
| Windows + WSL | Full support | Use `wsl.exe bash -c` wrapper |

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
