"""Claude Haiku integration for intelligent distillation."""

import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Optional

from .chunker import Chunk
from .config import Config, get_token_budget
from .ranker import RankedChunk

logger = logging.getLogger("enhanced-rlm.haiku")

# Cache for Haiku responses
_response_cache: dict[str, tuple[str, float]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour


@dataclass
class DistillationResult:
    """Result from Haiku distillation."""

    content: str
    query_type: str
    token_budget: int
    cached: bool = False


def _get_cache_key(query: str, chunks: list[RankedChunk]) -> str:
    """Generate cache key from query and chunk content."""
    chunk_hash = hashlib.md5(
        "".join(c.chunk.content[:100] for c in chunks).encode()
    ).hexdigest()[:16]
    query_hash = hashlib.md5(query.encode()).hexdigest()[:16]
    return f"{query_hash}:{chunk_hash}"


def _check_cache(key: str) -> Optional[str]:
    """Check if response is cached and not expired."""
    if key in _response_cache:
        content, timestamp = _response_cache[key]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return content
        else:
            del _response_cache[key]
    return None


def _store_cache(key: str, content: str) -> None:
    """Store response in cache."""
    _response_cache[key] = (content, time.time())


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
        "snippet", "sample", "template", "show me", "write"
    ]
    if any(kw in query_lower for kw in code_keywords):
        return "code_example"

    # Check for complex analysis indicators
    complex_keywords = [
        "explain", "architecture", "design", "complex", "overview",
        "understand", "describe", "analyze", "compare", "difference"
    ]
    if any(kw in query_lower for kw in complex_keywords):
        return "complex"

    return "simple"


def format_chunks_for_prompt(ranked_chunks: list[RankedChunk]) -> str:
    """Format chunks for the Haiku prompt."""
    parts = []
    for i, rc in enumerate(ranked_chunks, 1):
        chunk = rc.chunk
        header = f"[Source {i}: {chunk.file_path}"
        if chunk.header:
            header += f" - {chunk.header}"
        header += f", lines {chunk.start_line}-{chunk.end_line}]"

        parts.append(f"{header}\n{chunk.content}")

    return "\n\n---\n\n".join(parts)


class HaikuDistiller:
    """Distills search results using Claude Haiku."""

    def __init__(self, config: Config):
        """
        Initialize Haiku client.

        Args:
            config: Configuration with API settings
        """
        self.config = config
        self._client = None

    def _get_client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            api_key = self.config.anthropic_api_key
            if not api_key:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY environment variable not set. "
                    "Required for Haiku distillation."
                )
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                raise RuntimeError(
                    "anthropic package not installed. Run: pip install anthropic"
                )
        return self._client

    def distill(
        self,
        query: str,
        ranked_chunks: list[RankedChunk],
        use_cache: bool = True,
    ) -> DistillationResult:
        """
        Distill search results using Claude Haiku.

        Args:
            query: Original user query
            ranked_chunks: Ranked chunks from search
            use_cache: Whether to use cached responses

        Returns:
            DistillationResult with extracted information
        """
        if not ranked_chunks:
            return DistillationResult(
                content="No relevant information found in knowledge base.",
                query_type="simple",
                token_budget=0,
                cached=False,
            )

        # Classify query and get token budget
        query_type = classify_query(query)
        token_budget = get_token_budget(query_type, self.config.haiku)

        logger.info(f"Query type: {query_type}, token budget: {token_budget}")

        # Check cache
        if use_cache:
            cache_key = _get_cache_key(query, ranked_chunks)
            cached_response = _check_cache(cache_key)
            if cached_response:
                logger.info("Returning cached response")
                return DistillationResult(
                    content=cached_response,
                    query_type=query_type,
                    token_budget=token_budget,
                    cached=True,
                )

        # Format chunks for prompt
        context = format_chunks_for_prompt(ranked_chunks)

        # Build prompt based on query type
        if query_type == "code_example":
            instructions = """Instructions for code examples:
- Include COMPLETE, working code snippets that can be used directly
- Show the full function or section, not just fragments
- Include necessary imports or dependencies
- Add brief comments explaining key parts
- Reference the source file paths"""
        elif query_type == "complex":
            instructions = """Instructions for detailed explanations:
- Provide comprehensive coverage of the topic
- Explain the reasoning and context
- Include relevant code examples where helpful
- Describe any gotchas or important considerations
- Reference source files for further reading"""
        else:
            instructions = """Instructions for quick answers:
- Be concise and direct
- Focus on the most important information
- Include specific details (file paths, function names, values)
- Highlight any critical warnings or gotchas"""

        prompt = f"""You are a knowledge base assistant for a software development project.
Extract relevant information to answer the query based on the provided context.

Query: {query}

{instructions}

Context from knowledge base:
{context}

Provide a helpful response in up to {token_budget} tokens.
If the context doesn't contain relevant information, say so clearly.
Always include source file references when citing specific information."""

        try:
            client = self._get_client()
            response = client.messages.create(
                model=self.config.haiku.model,
                max_tokens=token_budget,
                messages=[{"role": "user", "content": prompt}],
            )

            # Safely extract response content
            result_content = ""
            if response.content and len(response.content) > 0:
                text = response.content[0].text
                if text is not None:
                    result_content = text.strip()

            if not result_content:
                result_content = "No relevant information extracted from knowledge base."

            # Cache the response
            if use_cache:
                _store_cache(cache_key, result_content)

            return DistillationResult(
                content=result_content,
                query_type=query_type,
                token_budget=token_budget,
                cached=False,
            )

        except Exception as e:
            logger.error(f"Haiku API error: {e}")
            # Fallback: return raw chunks without distillation
            return self._fallback_response(ranked_chunks, query_type, token_budget)

    def _fallback_response(
        self,
        ranked_chunks: list[RankedChunk],
        query_type: str,
        token_budget: int,
    ) -> DistillationResult:
        """Fallback response when Haiku is unavailable."""
        parts = ["*[Haiku unavailable - showing raw search results]*\n"]

        for i, rc in enumerate(ranked_chunks[:5], 1):
            chunk = rc.chunk
            header = f"**Source {i}:** `{chunk.file_path}`"
            if chunk.header:
                header += f" - {chunk.header}"

            # Truncate content for fallback
            content = chunk.content[:500]
            if len(chunk.content) > 500:
                content += "..."

            parts.append(f"{header}\n{content}")

        return DistillationResult(
            content="\n\n---\n\n".join(parts),
            query_type=query_type,
            token_budget=token_budget,
            cached=False,
        )


def clear_cache() -> int:
    """Clear the response cache. Returns number of entries cleared."""
    global _response_cache
    count = len(_response_cache)
    _response_cache = {}
    return count
