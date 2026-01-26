# Enhanced RLM - MCP Server for Knowledge Base Retrieval

An MCP (Model Context Protocol) server that provides intelligent, token-efficient knowledge base retrieval for Claude Code sessions. Based on RLM research principles.

## Features

- **Intelligent Search**: Ripgrep-powered search across your project's knowledge base
- **Dynamic Token Budgets**: Adjusts response size based on query type (1K-6K tokens)
- **Haiku Distillation**: Uses Claude Haiku 3.5 to extract only relevant information
- **Workspace-Specific**: Each project uses its own `CLAUDE.md` and `.claude/` folder

## Architecture

```
Claude Code (VS Code)     ← Uses Claude.ai Max subscription
        ↓
MCP Server (Python)       ← Keyword extraction, ripgrep search, chunking
        ↓
Claude Haiku 3.5 API      ← Smart filtering (requires API key)
```

## Installation

### Prerequisites

- Python 3.10+
- `ripgrep` installed (`rg` command available)
- Anthropic API key (for Haiku distillation only)

### Install from source

```bash
git clone https://github.com/lukiies/cc-mpc-extended-rlm.git
cd cc-mpc-extended-rlm
pip install -e .
```

### Set up API key

```bash
# For Haiku distillation only (Claude Code uses Claude.ai subscription)
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Configuration

### VS Code Workspace (recommended)

Add to your project's `.vscode/mcp.json`:

```json
{
  "servers": {
    "enhanced-rlm": {
      "command": "python",
      "args": ["-m", "enhanced_rlm.server"],
      "env": {
        "KNOWLEDGE_BASE_PATH": "${workspaceFolder}"
      }
    }
  }
}
```

### Global Configuration

Add to `~/.config/claude-code/settings.json`:

```json
{
  "mcpServers": {
    "enhanced-rlm": {
      "command": "python",
      "args": ["-m", "enhanced_rlm.server", "--path", "${workspaceFolder}"]
    }
  }
}
```

## Knowledge Base Structure

The server searches a two-level knowledge base:

```
your-project/
├── CLAUDE.md              ← PRIMARY: Main rules file (always searched first)
└── .claude/               ← SECONDARY: Detailed documentation
    ├── REFERENCE.md       ← Detailed patterns and conventions
    ├── code_examples/     ← Reusable code snippets
    └── [other docs]
```

## Usage

Once configured, Claude Code can call the `ask_knowledge_base` tool:

```
User: How do I add a new option to the application?

Claude Code automatically calls: ask_knowledge_base(query="how to add new application option")

Response: Concise, relevant instructions with code examples
```

## Dynamic Token Budgets

| Query Type | Token Limit | Examples |
|------------|-------------|----------|
| Simple | ~1,000 | Facts, gotchas, quick answers |
| Code Examples | ~4,000 | Patterns, how-to, implementations |
| Complex | ~6,000 | Architecture, design decisions |

## CLAUDE.md Scoping

Add this header to your project's `CLAUDE.md` to apply rules only for workspace-related tasks:

```markdown
# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the question relates to:**
- Files in this workspace/repository
- Code in this project
- Development tasks for this project

**These rules DO NOT apply to general questions unrelated to this project.**

---

# [Your Project] - Essential Rules
[... your rules ...]
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Credits

Based on RLM research (arXiv:2512.24601v1) - "Recursive Language Models".
