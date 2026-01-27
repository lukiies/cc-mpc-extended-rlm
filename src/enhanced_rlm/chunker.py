"""Text chunking module for knowledge base content."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .search import SearchResult


@dataclass
class Chunk:
    """A chunk of content from a file."""

    file_path: Path
    start_line: int
    end_line: int
    content: str
    header: Optional[str] = None  # Section header if applicable

    @property
    def line_count(self) -> int:
        """Number of lines in this chunk."""
        return self.end_line - self.start_line + 1

    def __str__(self) -> str:
        header_str = f" ({self.header})" if self.header else ""
        return f"{self.file_path}:{self.start_line}-{self.end_line}{header_str}"


class Chunker:
    """Chunker for splitting files into meaningful sections."""

    # Markdown header pattern
    MD_HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    # Code function patterns for different languages
    PRG_FUNCTION_PATTERN = re.compile(
        r"^\s*(?:static\s+)?function\s+(\w+)\s*\(",
        re.IGNORECASE | re.MULTILINE
    )
    C_FUNCTION_PATTERN = re.compile(
        r"^\s*(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*\{",
        re.MULTILINE
    )
    PYTHON_FUNCTION_PATTERN = re.compile(
        r"^\s*(?:async\s+)?def\s+(\w+)\s*\(",
        re.MULTILINE
    )
    # C# methods and classes
    CSHARP_PATTERN = re.compile(
        r"^\s*(?:public|private|protected|internal|static|async|virtual|override|\s)*"
        r"(?:class|void|Task|async\s+Task|string|int|bool|IActionResult|\w+<[^>]+>|\w+)\s+"
        r"(\w+)\s*(?:<[^>]+>)?\s*[\(\{]",
        re.MULTILINE
    )
    # TypeScript/JavaScript functions
    TS_FUNCTION_PATTERN = re.compile(
        r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(",
        re.MULTILINE
    )
    # SQL stored procedures and functions
    SQL_PATTERN = re.compile(
        r"^\s*(?:CREATE\s+)?(?:PROCEDURE|FUNCTION|PROC)\s+(?:\w+\.)?(\w+)",
        re.IGNORECASE | re.MULTILINE
    )
    # PowerShell functions
    PS_FUNCTION_PATTERN = re.compile(
        r"^\s*function\s+(\w+(?:-\w+)*)\s*(?:\([^)]*\))?\s*\{",
        re.IGNORECASE | re.MULTILINE
    )
    # Bash functions
    BASH_FUNCTION_PATTERN = re.compile(
        r"^\s*(?:function\s+)?(\w+)\s*\(\s*\)\s*\{",
        re.MULTILINE
    )

    def __init__(self, chunk_size: int = 500):
        """
        Initialize chunker.

        Args:
            chunk_size: Approximate target chunk size in tokens (1 token ~ 4 chars)
        """
        self.chunk_size = chunk_size
        self.char_limit = chunk_size * 4  # Rough conversion

    def _detect_file_type(self, file_path: Path) -> str:
        """Detect file type from extension."""
        suffix = file_path.suffix.lower()
        if suffix in (".md", ".markdown"):
            return "markdown"
        elif suffix in (".prg", ".ch"):
            return "clipper"
        elif suffix in (".c", ".h", ".cpp", ".hpp"):
            return "c"
        elif suffix == ".py":
            return "python"
        elif suffix == ".cs":
            return "csharp"
        elif suffix in (".ts", ".tsx", ".js", ".jsx"):
            return "typescript"
        elif suffix == ".sql":
            return "sql"
        elif suffix == ".ps1":
            return "powershell"
        elif suffix == ".sh":
            return "bash"
        else:
            return "text"

    def chunk_markdown(self, content: str, file_path: Path) -> list[Chunk]:
        """
        Chunk markdown file by headers.

        Args:
            content: File content
            file_path: Path to file

        Returns:
            List of chunks split by headers
        """
        chunks = []
        lines = content.split("\n")

        # Find all headers with their positions
        headers: list[tuple[int, int, str]] = []  # (line_idx, level, title)
        for i, line in enumerate(lines):
            match = self.MD_HEADER_PATTERN.match(line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headers.append((i, level, title))

        if not headers:
            # No headers, treat as single chunk
            return [Chunk(
                file_path=file_path,
                start_line=1,
                end_line=len(lines),
                content=content,
            )]

        # Create chunks between headers
        for i, (line_idx, level, title) in enumerate(headers):
            # Determine end of this section
            if i + 1 < len(headers):
                end_idx = headers[i + 1][0] - 1
            else:
                end_idx = len(lines) - 1

            # Extract content
            section_lines = lines[line_idx:end_idx + 1]
            section_content = "\n".join(section_lines)

            # Skip empty sections
            if not section_content.strip():
                continue

            chunks.append(Chunk(
                file_path=file_path,
                start_line=line_idx + 1,  # 1-indexed
                end_line=end_idx + 1,
                content=section_content,
                header=title,
            ))

        return chunks

    def chunk_code(
        self,
        content: str,
        file_path: Path,
        pattern: re.Pattern,
    ) -> list[Chunk]:
        """
        Chunk code file by function definitions.

        Args:
            content: File content
            file_path: Path to file
            pattern: Regex pattern to match function definitions

        Returns:
            List of chunks split by functions
        """
        chunks = []
        lines = content.split("\n")

        # Find all function definitions
        functions: list[tuple[int, str]] = []  # (line_idx, name)
        for i, line in enumerate(lines):
            match = pattern.match(line)
            if match:
                functions.append((i, match.group(1)))

        if not functions:
            # No functions found, return whole file as single chunk
            return [Chunk(
                file_path=file_path,
                start_line=1,
                end_line=len(lines),
                content=content,
            )]

        # Create chunks for each function
        for i, (line_idx, func_name) in enumerate(functions):
            # Determine end of this function
            if i + 1 < len(functions):
                end_idx = functions[i + 1][0] - 1
            else:
                end_idx = len(lines) - 1

            section_content = "\n".join(lines[line_idx:end_idx + 1])

            chunks.append(Chunk(
                file_path=file_path,
                start_line=line_idx + 1,
                end_line=end_idx + 1,
                content=section_content,
                header=f"function {func_name}",
            ))

        return chunks

    def chunk_file(self, file_path: Path) -> list[Chunk]:
        """
        Chunk a file based on its type.

        Args:
            file_path: Path to file

        Returns:
            List of chunks from the file
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return []

        file_type = self._detect_file_type(file_path)

        if file_type == "markdown":
            return self.chunk_markdown(content, file_path)
        elif file_type == "clipper":
            return self.chunk_code(content, file_path, self.PRG_FUNCTION_PATTERN)
        elif file_type == "c":
            return self.chunk_code(content, file_path, self.C_FUNCTION_PATTERN)
        elif file_type == "python":
            return self.chunk_code(content, file_path, self.PYTHON_FUNCTION_PATTERN)
        elif file_type == "csharp":
            return self.chunk_code(content, file_path, self.CSHARP_PATTERN)
        elif file_type == "typescript":
            return self.chunk_code(content, file_path, self.TS_FUNCTION_PATTERN)
        elif file_type == "sql":
            return self.chunk_code(content, file_path, self.SQL_PATTERN)
        elif file_type == "powershell":
            return self.chunk_code(content, file_path, self.PS_FUNCTION_PATTERN)
        elif file_type == "bash":
            return self.chunk_code(content, file_path, self.BASH_FUNCTION_PATTERN)
        else:
            # Default: return whole file as single chunk
            lines = content.split("\n")
            return [Chunk(
                file_path=file_path,
                start_line=1,
                end_line=len(lines),
                content=content,
            )]

    def chunk_from_results(self, results: list[SearchResult]) -> list[Chunk]:
        """
        Create chunks from search results, expanding context around matches.

        Groups results by file and creates chunks that include surrounding context.

        Args:
            results: List of search results

        Returns:
            List of chunks with context
        """
        if not results:
            return []

        # Group results by file
        results_by_file: dict[Path, list[SearchResult]] = {}
        for result in results:
            file_path = result.file_path
            if file_path not in results_by_file:
                results_by_file[file_path] = []
            results_by_file[file_path].append(result)

        chunks = []
        for file_path, file_results in results_by_file.items():
            # Get all chunks for this file
            file_chunks = self.chunk_file(file_path)

            # Find chunks that contain the search results
            result_lines = {r.line_number for r in file_results}
            for chunk in file_chunks:
                # Check if any result line is in this chunk
                for line_num in result_lines:
                    if chunk.start_line <= line_num <= chunk.end_line:
                        chunks.append(chunk)
                        break

        return chunks
