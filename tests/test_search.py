"""Tests for search module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from enhanced_rlm.search import KnowledgeSearch, SearchResult, STOP_WORDS
from enhanced_rlm.config import Config, KnowledgeBaseConfig, SearchConfig


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock config with temporary workspace."""
    # Create test files
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("# Test Rules\n\nThis is a test option configuration.")

    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    reference = claude_dir / "REFERENCE.md"
    reference.write_text("## Options\n\nHow to add new options to the application.")

    return Config(
        workspace_path=tmp_path,
        knowledge_base=KnowledgeBaseConfig(),
        search=SearchConfig(max_results=50),
    )


class TestKeywordExtraction:
    """Tests for keyword extraction."""

    def test_basic_extraction(self, mock_config):
        """Test basic keyword extraction."""
        search = KnowledgeSearch(mock_config)

        keywords = search.extract_keywords("How do I add a new option?")

        assert "add" in keywords
        assert "new" in keywords
        assert "option" in keywords
        # Stop words should be removed
        assert "how" not in keywords
        assert "do" not in keywords
        assert "i" not in keywords

    def test_removes_short_words(self, mock_config):
        """Test that short words are removed."""
        search = KnowledgeSearch(mock_config)

        keywords = search.extract_keywords("It is a big test")

        assert "big" in keywords
        assert "test" in keywords
        assert "it" not in keywords
        assert "is" not in keywords
        assert "a" not in keywords

    def test_preserves_order(self, mock_config):
        """Test that keyword order is preserved."""
        search = KnowledgeSearch(mock_config)

        keywords = search.extract_keywords("configuration option value")

        assert keywords == ["configuration", "option", "value"]

    def test_deduplicates(self, mock_config):
        """Test that duplicates are removed."""
        search = KnowledgeSearch(mock_config)

        keywords = search.extract_keywords("option option option test")

        assert keywords.count("option") == 1
        assert keywords.count("test") == 1

    def test_empty_query(self, mock_config):
        """Test handling of empty query."""
        search = KnowledgeSearch(mock_config)

        keywords = search.extract_keywords("")

        assert keywords == []

    def test_only_stop_words(self, mock_config):
        """Test query with only stop words."""
        search = KnowledgeSearch(mock_config)

        keywords = search.extract_keywords("the a an is are")

        assert keywords == []


class TestSearch:
    """Tests for search functionality."""

    def test_search_finds_content(self, mock_config):
        """Test that search finds content in files."""
        search = KnowledgeSearch(mock_config)

        results = search.search("option configuration")

        assert len(results) > 0
        # Should find matches in our test files
        file_names = [r.file_path.name for r in results]
        assert any("CLAUDE.md" in name or "REFERENCE.md" in name for name in file_names)

    def test_search_returns_empty_for_no_matches(self, mock_config):
        """Test that search returns empty for non-existent terms."""
        search = KnowledgeSearch(mock_config)

        results = search.search("xyznonexistent123")

        assert results == []

    def test_search_respects_max_results(self, mock_config):
        """Test that max_results is respected."""
        search = KnowledgeSearch(mock_config)

        # Limit to 2 results
        results = search.ripgrep_search(["option", "test"], max_results=2)

        assert len(results) <= 2


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_str_representation(self):
        """Test string representation of SearchResult."""
        result = SearchResult(
            file_path=Path("/test/file.md"),
            line_number=42,
            line_content="test content",
            match_text="test",
        )

        assert "/test/file.md:42: test content" in str(result)
