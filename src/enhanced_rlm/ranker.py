"""Relevance ranking module for knowledge base chunks."""

import math
from collections import Counter
from dataclasses import dataclass

from .chunker import Chunk


@dataclass
class RankedChunk:
    """A chunk with its relevance score."""

    chunk: Chunk
    score: float
    matched_keywords: list[str]

    def __str__(self) -> str:
        return f"{self.chunk} (score: {self.score:.3f})"


class Ranker:
    """Ranks chunks by relevance to query keywords."""

    def __init__(self, top_n: int = 10):
        """
        Initialize ranker.

        Args:
            top_n: Number of top chunks to return
        """
        self.top_n = top_n

    def _keyword_frequency(self, text: str, keywords: list[str]) -> dict[str, int]:
        """
        Count keyword occurrences in text.

        Args:
            text: Text to search in
            keywords: Keywords to count

        Returns:
            Dictionary of keyword -> count
        """
        text_lower = text.lower()
        counts = {}
        for kw in keywords:
            counts[kw] = text_lower.count(kw.lower())
        return counts

    def _calculate_score(
        self,
        chunk: Chunk,
        keywords: list[str],
        doc_frequencies: dict[str, int],
        total_docs: int,
    ) -> tuple[float, list[str]]:
        """
        Calculate relevance score using TF-IDF-like scoring.

        Args:
            chunk: Chunk to score
            keywords: Query keywords
            doc_frequencies: How many chunks contain each keyword
            total_docs: Total number of chunks

        Returns:
            Tuple of (score, list of matched keywords)
        """
        content = chunk.content
        header = chunk.header or ""
        combined_text = f"{header} {content}"

        # Count keyword frequencies in this chunk
        freqs = self._keyword_frequency(combined_text, keywords)

        score = 0.0
        matched = []

        for kw, tf in freqs.items():
            if tf > 0:
                matched.append(kw)
                # TF component: log(1 + tf)
                tf_score = math.log(1 + tf)

                # IDF component: log(total / (1 + df))
                df = doc_frequencies.get(kw, 0)
                idf_score = math.log(total_docs / (1 + df))

                # Boost for header matches
                header_boost = 2.0 if kw.lower() in header.lower() else 1.0

                score += tf_score * idf_score * header_boost

        # Boost for chunks with more keyword diversity
        diversity_boost = math.sqrt(len(matched)) if matched else 0
        score += diversity_boost

        return score, matched

    def rank(self, chunks: list[Chunk], keywords: list[str]) -> list[RankedChunk]:
        """
        Rank chunks by relevance to keywords.

        Args:
            chunks: List of chunks to rank
            keywords: Query keywords

        Returns:
            List of RankedChunk objects, sorted by score descending
        """
        if not chunks or not keywords:
            return []

        # Calculate document frequencies (how many chunks contain each keyword)
        doc_frequencies: Counter[str] = Counter()
        for chunk in chunks:
            combined = f"{chunk.header or ''} {chunk.content}".lower()
            for kw in keywords:
                if kw.lower() in combined:
                    doc_frequencies[kw] += 1

        total_docs = len(chunks)

        # Score each chunk
        ranked = []
        for chunk in chunks:
            score, matched = self._calculate_score(
                chunk, keywords, dict(doc_frequencies), total_docs
            )
            if score > 0:  # Only include chunks with matches
                ranked.append(RankedChunk(
                    chunk=chunk,
                    score=score,
                    matched_keywords=matched,
                ))

        # Sort by score descending
        ranked.sort(key=lambda x: x.score, reverse=True)

        # Return top N
        return ranked[:self.top_n]

    def deduplicate(self, ranked_chunks: list[RankedChunk]) -> list[RankedChunk]:
        """
        Remove duplicate or highly overlapping chunks.

        Args:
            ranked_chunks: List of ranked chunks

        Returns:
            Deduplicated list
        """
        if not ranked_chunks:
            return []

        seen_content_hashes: set[int] = set()
        result = []

        for rc in ranked_chunks:
            # Simple deduplication: hash of first 200 chars
            content_hash = hash(rc.chunk.content[:200])
            if content_hash not in seen_content_hashes:
                seen_content_hashes.add(content_hash)
                result.append(rc)

        return result
