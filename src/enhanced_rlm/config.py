"""Configuration handling for Enhanced RLM MCP server."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SearchConfig:
    """Configuration for search behavior."""

    max_results: int = 50
    chunk_size: int = 500  # approximate tokens per chunk
    top_chunks: int = 10  # number of chunks to send to Haiku


@dataclass
class HaikuConfig:
    """Configuration for Claude Haiku distillation."""

    model: str = "claude-3-5-haiku-20241022"
    # Dynamic token budgets based on query type
    simple_budget: int = 1000
    code_example_budget: int = 4000
    complex_budget: int = 6000
    default_budget: int = 2000


@dataclass
class KnowledgeBaseConfig:
    """Configuration for knowledge base paths and patterns."""

    # CLAUDE.md is the primary rules file in workspace root
    root_file: str = "CLAUDE.md"
    # .claude/ folder contains detailed documentation
    docs_folder: str = ".claude"
    # File patterns to include in search
    # Supports: Markdown, Python, C/C++, Harbour/xBase, C#, TypeScript/JavaScript, SQL, PowerShell, Bash
    file_patterns: list[str] = field(
        default_factory=lambda: [
            "*.md",           # Markdown documentation
            "*.py",           # Python
            "*.prg", "*.ch",  # Harbour/xBase
            "*.c", "*.h",     # C/C++
            "*.cs",           # C#
            "*.ts", "*.tsx",  # TypeScript
            "*.js", "*.jsx",  # JavaScript
            "*.sql",          # SQL
            "*.ps1",          # PowerShell
            "*.sh",           # Bash/Shell
        ]
    )
    # Patterns to exclude
    exclude_patterns: list[str] = field(
        default_factory=lambda: ["*.pyc", "__pycache__", ".git", "node_modules"]
    )


@dataclass
class Config:
    """Main configuration for Enhanced RLM server."""

    workspace_path: Path
    knowledge_base: KnowledgeBaseConfig = field(default_factory=KnowledgeBaseConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    haiku: HaikuConfig = field(default_factory=HaikuConfig)

    @property
    def root_file_path(self) -> Path:
        """Get full path to CLAUDE.md."""
        return self.workspace_path / self.knowledge_base.root_file

    @property
    def docs_folder_path(self) -> Path:
        """Get full path to .claude/ folder."""
        return self.workspace_path / self.knowledge_base.docs_folder

    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Get Anthropic API key from environment."""
        return os.environ.get("ANTHROPIC_API_KEY")

    def has_knowledge_base(self) -> bool:
        """Check if knowledge base exists."""
        return self.root_file_path.exists() or self.docs_folder_path.exists()

    def get_search_paths(self) -> list[Path]:
        """Get all paths to search, with CLAUDE.md first."""
        paths = []
        if self.root_file_path.exists():
            paths.append(self.root_file_path)
        if self.docs_folder_path.exists():
            paths.append(self.docs_folder_path)
        return paths


def load_config(workspace_path: Optional[str] = None) -> Config:
    """
    Load configuration from environment and defaults.

    Args:
        workspace_path: Path to workspace root. If None, uses KNOWLEDGE_BASE_PATH
                       environment variable or current directory.

    Returns:
        Config object with all settings.
    """
    if workspace_path is None:
        workspace_path = os.environ.get("KNOWLEDGE_BASE_PATH", os.getcwd())

    path = Path(workspace_path).resolve()

    if not path.exists():
        raise ValueError(f"Workspace path does not exist: {path}")

    return Config(workspace_path=path)


def get_token_budget(query_type: str, config: HaikuConfig) -> int:
    """
    Get token budget based on query type.

    Args:
        query_type: One of "simple", "code_example", "complex"
        config: HaikuConfig with budget settings

    Returns:
        Token budget for the query type
    """
    budgets = {
        "simple": config.simple_budget,
        "code_example": config.code_example_budget,
        "complex": config.complex_budget,
    }
    return budgets.get(query_type, config.default_budget)
