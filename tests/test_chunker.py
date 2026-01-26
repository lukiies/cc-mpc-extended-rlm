"""Tests for chunker module."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from enhanced_rlm.chunker import Chunker, Chunk


@pytest.fixture
def chunker():
    """Create a chunker instance."""
    return Chunker(chunk_size=500)


@pytest.fixture
def sample_markdown(tmp_path):
    """Create a sample markdown file."""
    content = """# Main Title

Introduction paragraph.

## Section One

Content for section one.
More content here.

## Section Two

Content for section two.

### Subsection

Nested content.

## Section Three

Final section.
"""
    file_path = tmp_path / "test.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_prg(tmp_path):
    """Create a sample PRG file."""
    content = """// Header comment

function test_one(param1)
local result
result := param1 * 2
return result

function test_two(param1, param2)
local sum
sum := param1 + param2
return sum
"""
    file_path = tmp_path / "test.prg"
    file_path.write_text(content)
    return file_path


class TestMarkdownChunking:
    """Tests for markdown chunking."""

    def test_chunks_by_headers(self, chunker, sample_markdown):
        """Test that markdown is chunked by headers."""
        chunks = chunker.chunk_file(sample_markdown)

        # Should have chunks for each header section
        assert len(chunks) >= 3

        # Check that headers are captured
        headers = [c.header for c in chunks if c.header]
        assert "Main Title" in headers
        assert "Section One" in headers
        assert "Section Two" in headers

    def test_chunk_contains_content(self, chunker, sample_markdown):
        """Test that chunks contain the right content."""
        chunks = chunker.chunk_file(sample_markdown)

        # Find section one
        section_one = next(c for c in chunks if c.header == "Section One")

        assert "Content for section one" in section_one.content

    def test_chunk_line_numbers(self, chunker, sample_markdown):
        """Test that line numbers are correct."""
        chunks = chunker.chunk_file(sample_markdown)

        for chunk in chunks:
            assert chunk.start_line >= 1
            assert chunk.end_line >= chunk.start_line


class TestCodeChunking:
    """Tests for code file chunking."""

    def test_chunks_by_functions(self, chunker, sample_prg):
        """Test that PRG files are chunked by functions."""
        chunks = chunker.chunk_file(sample_prg)

        # Should have chunks for each function
        assert len(chunks) >= 2

        # Check function names in headers
        headers = [c.header for c in chunks if c.header]
        assert any("test_one" in h for h in headers)
        assert any("test_two" in h for h in headers)

    def test_function_content(self, chunker, sample_prg):
        """Test that function chunks contain the right content."""
        chunks = chunker.chunk_file(sample_prg)

        # Find test_one function
        test_one = next(c for c in chunks if c.header and "test_one" in c.header)

        assert "param1 * 2" in test_one.content


class TestChunkDataclass:
    """Tests for Chunk dataclass."""

    def test_line_count(self):
        """Test line count calculation."""
        chunk = Chunk(
            file_path=Path("/test.md"),
            start_line=10,
            end_line=20,
            content="test",
        )

        assert chunk.line_count == 11

    def test_str_representation(self):
        """Test string representation."""
        chunk = Chunk(
            file_path=Path("/test.md"),
            start_line=10,
            end_line=20,
            content="test",
            header="Test Section",
        )

        str_repr = str(chunk)
        assert "/test.md" in str_repr
        assert "10-20" in str_repr
        assert "Test Section" in str_repr
