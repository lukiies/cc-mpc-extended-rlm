"""MCP server for Enhanced RLM knowledge base retrieval."""

import argparse
import logging
import sys
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .chunker import Chunker
from .config import Config, get_token_budget, load_config
from .ranker import RankedChunk, Ranker
from .search import KnowledgeSearch

# Configure logging to stderr (not stdout which is used by STDIO transport)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("enhanced-rlm")

# Initialize MCP server
mcp = FastMCP("enhanced-rlm")

# Global config - will be set on startup
_config: Optional[Config] = None


def get_config() -> Config:
    """Get current configuration."""
    if _config is None:
        raise RuntimeError("Server not initialized. Call init_server() first.")
    return _config


def classify_query(query: str) -> str:
    """
    Classify query type to determine token budget.

    Args:
        query: Natural language query

    Returns:
        Query type: "simple", "code_example", or "complex"
    """
    query_lower = query.lower()

    # Check for code example indicators
    code_keywords = [
        "example", "code", "pattern", "how to", "implement",
        "snippet", "sample", "template", "show me"
    ]
    if any(kw in query_lower for kw in code_keywords):
        return "code_example"

    # Check for complex analysis indicators
    complex_keywords = [
        "explain", "architecture", "design", "complex", "overview",
        "understand", "describe", "analyze", "compare"
    ]
    if any(kw in query_lower for kw in complex_keywords):
        return "complex"

    return "simple"


def format_chunks_for_response(
    ranked_chunks: list[RankedChunk],
    query_type: str,
) -> str:
    """
    Format ranked chunks for response.

    Args:
        ranked_chunks: List of ranked chunks
        query_type: Type of query for formatting hints

    Returns:
        Formatted response string
    """
    if not ranked_chunks:
        return "No relevant information found in knowledge base."

    parts = []

    for i, rc in enumerate(ranked_chunks, 1):
        chunk = rc.chunk
        header = f"**Source {i}:** `{chunk.file_path}`"
        if chunk.header:
            header += f" - {chunk.header}"
        header += f" (lines {chunk.start_line}-{chunk.end_line})"

        # Add matched keywords info
        if rc.matched_keywords:
            header += f"\n*Matched: {', '.join(rc.matched_keywords)}*"

        parts.append(f"{header}\n\n{chunk.content}")

    return "\n\n---\n\n".join(parts)


@mcp.tool()
def ask_knowledge_base(
    query: str,
    context: Optional[str] = None,
) -> str:
    """
    Search the project knowledge base for relevant information.

    Use this for questions about codebase patterns, conventions, gotchas,
    examples, and documentation. The knowledge base includes CLAUDE.md
    (main rules) and the .claude/ folder (detailed documentation).

    Args:
        query: Natural language question about the codebase or development patterns
        context: Optional current file or topic for additional context

    Returns:
        Relevant information from the knowledge base
    """
    config = get_config()

    # Check if knowledge base exists
    if not config.has_knowledge_base():
        return (
            "No knowledge base found. Expected CLAUDE.md in workspace root "
            "and/or .claude/ folder with documentation."
        )

    logger.info(f"Processing query: {query[:50]}...")

    # Initialize components
    search = KnowledgeSearch(config)
    chunker = Chunker(config.search.chunk_size)
    ranker = Ranker(config.search.top_chunks)

    # Include context in search if provided
    search_query = query
    if context:
        search_query = f"{query} {context}"

    # Step 1: Search for relevant content
    search_results = search.search(search_query)
    logger.info(f"Found {len(search_results)} search results")

    if not search_results:
        return f"No relevant information found for query: {query}"

    # Step 2: Create chunks from search results
    chunks = chunker.chunk_from_results(search_results)
    logger.info(f"Created {len(chunks)} chunks")

    if not chunks:
        return f"No relevant content found for query: {query}"

    # Step 3: Rank chunks by relevance
    keywords = search.extract_keywords(search_query)
    ranked_chunks = ranker.rank(chunks, keywords)
    ranked_chunks = ranker.deduplicate(ranked_chunks)
    logger.info(f"Ranked and deduplicated to {len(ranked_chunks)} chunks")

    # Step 4: Classify query and format response
    query_type = classify_query(query)
    token_budget = get_token_budget(query_type, config.haiku)
    logger.info(f"Query type: {query_type}, token budget: {token_budget}")

    # Format response
    # NOTE: In Phase 3, this is where Haiku distillation will be added
    response = format_chunks_for_response(ranked_chunks, query_type)

    return response


@mcp.tool()
def list_knowledge_base() -> str:
    """
    List the structure of the project knowledge base.

    Returns a summary of available documentation files and their purposes.

    Returns:
        Structure of the knowledge base
    """
    config = get_config()

    if not config.has_knowledge_base():
        return "No knowledge base found."

    parts = ["# Knowledge Base Structure\n"]

    # Check CLAUDE.md
    if config.root_file_path.exists():
        size = config.root_file_path.stat().st_size
        parts.append(f"- **CLAUDE.md** (root): {size} bytes - Main rules file")

    # Check .claude/ folder
    if config.docs_folder_path.exists():
        parts.append(f"\n**{config.knowledge_base.docs_folder}/ folder:**")
        for item in sorted(config.docs_folder_path.iterdir()):
            if item.is_file() and item.suffix in (".md", ".prg", ".py", ".c"):
                size = item.stat().st_size
                parts.append(f"  - {item.name}: {size} bytes")
            elif item.is_dir() and not item.name.startswith("."):
                file_count = len(list(item.iterdir()))
                parts.append(f"  - {item.name}/: {file_count} files")

    return "\n".join(parts)


def init_server(workspace_path: Optional[str] = None) -> None:
    """
    Initialize the server with configuration.

    Args:
        workspace_path: Path to workspace root (or use env var / cwd)
    """
    global _config
    _config = load_config(workspace_path)
    logger.info(f"Initialized with workspace: {_config.workspace_path}")
    logger.info(f"Knowledge base exists: {_config.has_knowledge_base()}")


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(
        description="Enhanced RLM MCP server for knowledge base retrieval"
    )
    parser.add_argument(
        "--path",
        help="Path to workspace root (default: KNOWLEDGE_BASE_PATH env var or cwd)",
    )
    args = parser.parse_args()

    # Initialize server
    init_server(args.path)

    # Run MCP server
    logger.info("Starting Enhanced RLM MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
