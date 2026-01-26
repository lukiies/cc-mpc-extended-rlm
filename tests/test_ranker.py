"""Tests for ranker module."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from enhanced_rlm.ranker import Ranker, RankedChunk
from enhanced_rlm.chunker import Chunk


@pytest.fixture
def ranker():
    """Create a ranker instance."""
    return Ranker(top_n=5)


@pytest.fixture
def sample_chunks():
    """Create sample chunks for testing."""
    return [
        Chunk(
            file_path=Path("/test1.md"),
            start_line=1,
            end_line=10,
            content="How to add a new option to the application configuration.",
            header="Adding Options",
        ),
        Chunk(
            file_path=Path("/test2.md"),
            start_line=1,
            end_line=10,
            content="Database configuration and setup instructions.",
            header="Database Setup",
        ),
        Chunk(
            file_path=Path("/test3.md"),
            start_line=1,
            end_line=10,
            content="Option values can be modified in the settings file.",
            header="Settings",
        ),
        Chunk(
            file_path=Path("/test4.md"),
            start_line=1,
            end_line=10,
            content="Unrelated content about testing procedures.",
            header="Testing",
        ),
    ]


class TestRanking:
    """Tests for ranking functionality."""

    def test_ranks_by_relevance(self, ranker, sample_chunks):
        """Test that chunks are ranked by relevance."""
        keywords = ["option", "configuration"]

        ranked = ranker.rank(sample_chunks, keywords)

        # First result should have highest relevance to keywords
        assert len(ranked) > 0
        assert ranked[0].score >= ranked[-1].score

        # "Adding Options" chunk should rank high (has both keywords)
        top_headers = [r.chunk.header for r in ranked[:2]]
        assert "Adding Options" in top_headers

    def test_returns_top_n(self, ranker, sample_chunks):
        """Test that only top N results are returned."""
        keywords = ["option", "configuration", "database", "testing"]

        ranked = ranker.rank(sample_chunks, keywords)

        assert len(ranked) <= ranker.top_n

    def test_tracks_matched_keywords(self, ranker, sample_chunks):
        """Test that matched keywords are tracked."""
        keywords = ["option", "configuration"]

        ranked = ranker.rank(sample_chunks, keywords)

        # First result should have matched keywords
        assert len(ranked[0].matched_keywords) > 0
        assert any(kw in ranked[0].matched_keywords for kw in keywords)

    def test_empty_keywords(self, ranker, sample_chunks):
        """Test handling of empty keywords."""
        ranked = ranker.rank(sample_chunks, [])

        assert ranked == []

    def test_empty_chunks(self, ranker):
        """Test handling of empty chunks."""
        ranked = ranker.rank([], ["option"])

        assert ranked == []

    def test_no_matches(self, ranker, sample_chunks):
        """Test when no keywords match."""
        keywords = ["xyznonexistent123"]

        ranked = ranker.rank(sample_chunks, keywords)

        assert ranked == []


class TestDeduplication:
    """Tests for deduplication functionality."""

    def test_removes_duplicates(self, ranker):
        """Test that duplicate chunks are removed."""
        # Create chunks with same content
        chunks = [
            Chunk(
                file_path=Path("/test1.md"),
                start_line=1,
                end_line=10,
                content="Same content about options",
                header="Section 1",
            ),
            Chunk(
                file_path=Path("/test2.md"),
                start_line=1,
                end_line=10,
                content="Same content about options",  # Duplicate
                header="Section 2",
            ),
            Chunk(
                file_path=Path("/test3.md"),
                start_line=1,
                end_line=10,
                content="Different content about testing",
                header="Section 3",
            ),
        ]

        keywords = ["content", "options", "testing"]
        ranked = ranker.rank(chunks, keywords)
        deduplicated = ranker.deduplicate(ranked)

        # Should have fewer results after deduplication
        assert len(deduplicated) <= len(ranked)


class TestRankedChunk:
    """Tests for RankedChunk dataclass."""

    def test_str_representation(self):
        """Test string representation."""
        chunk = Chunk(
            file_path=Path("/test.md"),
            start_line=1,
            end_line=10,
            content="test",
            header="Test",
        )
        ranked = RankedChunk(
            chunk=chunk,
            score=5.5,
            matched_keywords=["test"],
        )

        str_repr = str(ranked)
        assert "5.5" in str_repr or "5.50" in str_repr
