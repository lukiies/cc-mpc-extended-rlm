"""Ripgrep-based search module for knowledge base."""

import os
import platform
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import Config


def is_wsl_path(path: Path) -> bool:
    """Check if a path is a WSL UNC path (\\\\wsl.localhost\\... or \\\\wsl$\\...)."""
    path_str = str(path)
    return path_str.startswith("\\\\wsl.localhost\\") or path_str.startswith("\\\\wsl$\\")


def wsl_path_to_linux(path: Path) -> str:
    """
    Convert WSL UNC path to Linux path.

    \\\\wsl.localhost\\Ubuntu\\home\\user -> /home/user
    \\\\wsl$\\Ubuntu\\home\\user -> /home/user
    """
    path_str = str(path)
    # Remove \\wsl.localhost\Distro or \\wsl$\Distro prefix
    if path_str.startswith("\\\\wsl.localhost\\"):
        # \\wsl.localhost\Ubuntu\home\user -> Ubuntu\home\user
        remainder = path_str[len("\\\\wsl.localhost\\"):]
    elif path_str.startswith("\\\\wsl$\\"):
        remainder = path_str[len("\\\\wsl$\\"):]
    else:
        return path_str

    # Split off the distro name: Ubuntu\home\user -> home\user
    parts = remainder.split("\\", 1)
    if len(parts) > 1:
        linux_path = "/" + parts[1].replace("\\", "/")
    else:
        linux_path = "/"

    return linux_path

# Common stop words to filter out during keyword extraction
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
    "from", "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "also", "now", "i", "me",
    "my", "myself", "we", "our", "ours", "you", "your", "yours", "he", "him",
    "his", "she", "her", "hers", "it", "its", "they", "them", "their",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am",
}


@dataclass
class SearchResult:
    """A single search result from ripgrep."""

    file_path: Path
    line_number: int
    line_content: str
    match_text: str

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_number}: {self.line_content}"


class KnowledgeSearch:
    """Search engine for project knowledge base using ripgrep or grep."""

    def __init__(self, config: Config):
        """
        Initialize search with configuration.

        Args:
            config: Configuration object with workspace path and settings
        """
        self.config = config
        self.workspace = config.workspace_path
        self._is_windows = platform.system() == "Windows"
        self._uses_wsl_path = is_wsl_path(self.workspace)
        self._use_ripgrep = self._check_ripgrep()

    def _check_ripgrep(self) -> bool:
        """Check if ripgrep is available."""
        # If on Windows with WSL paths, check wsl.exe rg
        if self._is_windows and self._uses_wsl_path:
            try:
                subprocess.run(
                    ["wsl.exe", "rg", "--version"],
                    capture_output=True,
                    timeout=5,
                )
                return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                return False

        # Standard ripgrep check
        try:
            subprocess.run(
                ["rg", "--version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def extract_keywords(self, query: str) -> list[str]:
        """
        Extract search keywords from natural language query.

        Simple approach: tokenize, lowercase, remove stop words and short words.

        Args:
            query: Natural language query string

        Returns:
            List of keywords for search
        """
        # Tokenize: split on non-alphanumeric characters
        tokens = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", query.lower())

        # Filter out stop words and very short words
        keywords = [
            word for word in tokens
            if word not in STOP_WORDS and len(word) > 2
        ]

        # Deduplicate while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords

    def _build_ripgrep_command(
        self,
        pattern: str,
        search_path: Path,
        max_results: Optional[int] = None,
    ) -> list[str]:
        """
        Build ripgrep command with appropriate options.

        Args:
            pattern: Search pattern (regex)
            search_path: Path to search in
            max_results: Maximum number of results

        Returns:
            Command as list of strings
        """
        # Use wsl.exe prefix if on Windows with WSL paths
        if self._is_windows and self._uses_wsl_path:
            cmd = ["wsl.exe", "rg"]
            # Convert path to Linux format
            linux_path = wsl_path_to_linux(search_path)
        else:
            cmd = ["rg"]
            linux_path = str(search_path)

        cmd.extend([
            "--ignore-case",  # Case insensitive
            "--line-number",  # Include line numbers
            "--no-heading",   # Put filename on each line
            "--color=never",  # No color codes in output
        ])

        # Add file type filters based on config
        for pattern_glob in self.config.knowledge_base.file_patterns:
            cmd.extend(["--glob", pattern_glob])

        # Add exclude patterns
        for exclude in self.config.knowledge_base.exclude_patterns:
            cmd.extend(["--glob", f"!{exclude}"])

        # Limit results if specified
        if max_results:
            cmd.extend(["--max-count", str(max_results)])

        # Add pattern and path
        cmd.append(pattern)
        cmd.append(linux_path)

        return cmd

    def ripgrep_search(
        self,
        keywords: list[str],
        max_results: Optional[int] = None,
    ) -> list[SearchResult]:
        """
        Execute ripgrep search with keywords.

        Searches CLAUDE.md first, then .claude/ folder.
        Falls back to grep if ripgrep is not available.

        Args:
            keywords: List of keywords to search for
            max_results: Maximum total results (None for config default)

        Returns:
            List of SearchResult objects
        """
        if not keywords:
            return []

        # Use grep fallback if ripgrep not available
        if not self._use_ripgrep:
            return self._grep_search(keywords, max_results)

        if max_results is None:
            max_results = self.config.search.max_results

        # Build OR pattern for all keywords
        pattern = "|".join(re.escape(kw) for kw in keywords)

        results: list[SearchResult] = []
        search_paths = self.config.get_search_paths()

        for search_path in search_paths:
            if not search_path.exists():
                continue

            remaining = max_results - len(results)
            if remaining <= 0:
                break

            cmd = self._build_ripgrep_command(pattern, search_path, remaining)

            try:
                # Don't use cwd for WSL paths on Windows (UNC paths not supported as cwd)
                run_kwargs = {
                    "capture_output": True,
                    "text": True,
                    "encoding": "utf-8",
                    "errors": "replace",
                    "timeout": 30,
                }
                if not (self._is_windows and self._uses_wsl_path):
                    run_kwargs["cwd"] = self.workspace

                process = subprocess.run(cmd, **run_kwargs)

                # Parse output (handle None stdout)
                stdout = process.stdout or ""
                for line in stdout.strip().split("\n"):
                    if not line:
                        continue

                    # Parse: file:line:content
                    match = re.match(r"^(.+?):(\d+):(.*)$", line)
                    if match:
                        file_path = Path(match.group(1))
                        line_num = int(match.group(2))
                        content = match.group(3)

                        # Find which keyword matched
                        matched_kw = ""
                        for kw in keywords:
                            if kw.lower() in content.lower():
                                matched_kw = kw
                                break

                        results.append(SearchResult(
                            file_path=file_path,
                            line_number=line_num,
                            line_content=content.strip(),
                            match_text=matched_kw,
                        ))

            except subprocess.TimeoutExpired:
                # Search took too long, return what we have
                break
            except FileNotFoundError:
                # ripgrep not installed, try grep fallback
                return self._grep_search(keywords, max_results)

        return results

    def _build_grep_command(
        self,
        pattern: str,
        search_path: Path,
        max_results: Optional[int] = None,
    ) -> list[str]:
        """Build grep command as fallback when ripgrep unavailable."""
        # Use wsl.exe prefix if on Windows with WSL paths
        if self._is_windows and self._uses_wsl_path:
            cmd = ["wsl.exe", "grep"]
            linux_path = wsl_path_to_linux(search_path)
        else:
            cmd = ["grep"]
            linux_path = str(search_path)

        cmd.extend([
            "-r",              # Recursive
            "-i",              # Case insensitive
            "-n",              # Line numbers
            "-E",              # Extended regex
            "--include=*.md",  # Include markdown files
            "--include=*.prg", # Include PRG files
            "--include=*.c",   # Include C files
            "--include=*.py",  # Include Python files
        ])

        if max_results:
            cmd.extend(["-m", str(max_results)])

        cmd.append(pattern)
        cmd.append(linux_path)

        return cmd

    def _grep_search(
        self,
        keywords: list[str],
        max_results: Optional[int] = None,
    ) -> list[SearchResult]:
        """Fallback search using grep when ripgrep unavailable."""
        if not keywords:
            return []

        if max_results is None:
            max_results = self.config.search.max_results

        pattern = "|".join(re.escape(kw) for kw in keywords)
        results: list[SearchResult] = []
        search_paths = self.config.get_search_paths()

        for search_path in search_paths:
            if not search_path.exists():
                continue

            remaining = max_results - len(results)
            if remaining <= 0:
                break

            cmd = self._build_grep_command(pattern, search_path, remaining)

            try:
                # Don't use cwd for WSL paths on Windows (UNC paths not supported as cwd)
                run_kwargs = {
                    "capture_output": True,
                    "text": True,
                    "encoding": "utf-8",
                    "errors": "replace",
                    "timeout": 30,
                }
                if not (self._is_windows and self._uses_wsl_path):
                    run_kwargs["cwd"] = self.workspace

                process = subprocess.run(cmd, **run_kwargs)

                # Parse output (handle None stdout)
                stdout = process.stdout or ""
                for line in stdout.strip().split("\n"):
                    if not line:
                        continue

                    match = re.match(r"^(.+?):(\d+):(.*)$", line)
                    if match:
                        file_path = Path(match.group(1))
                        line_num = int(match.group(2))
                        content = match.group(3)

                        matched_kw = ""
                        for kw in keywords:
                            if kw.lower() in content.lower():
                                matched_kw = kw
                                break

                        results.append(SearchResult(
                            file_path=file_path,
                            line_number=line_num,
                            line_content=content.strip(),
                            match_text=matched_kw,
                        ))

            except subprocess.TimeoutExpired:
                break
            except FileNotFoundError:
                raise RuntimeError("Neither ripgrep nor grep is available.")

        return results

    def search(self, query: str) -> list[SearchResult]:
        """
        Search knowledge base with natural language query.

        Args:
            query: Natural language query

        Returns:
            List of search results
        """
        keywords = self.extract_keywords(query)
        if not keywords:
            return []
        return self.ripgrep_search(keywords)
