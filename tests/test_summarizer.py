"""
Tests for document summarization functionality.
"""

import pytest
from app.summarizer import count_tokens, chunk_text, summarize_document


def test_count_tokens():
    """Test token counting estimation."""
    text = "This is a test sentence."
    tokens = count_tokens(text)
    assert tokens > 0
    assert tokens == len(text) // 4


def test_chunk_text_small():
    """Test chunking with text under max tokens."""
    text = "This is a small text."
    chunks = chunk_text(text, max_tokens=1000)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_large():
    """Test chunking with text over max tokens."""
    text = "Test paragraph.\n\n" * 1000
    chunks = chunk_text(text, max_tokens=100)
    assert len(chunks) > 1
    for chunk in chunks:
        assert count_tokens(chunk) <= 100 or len(chunks) == 1


def test_chunk_text_empty():
    """Test chunking with empty text."""
    text = ""
    chunks = chunk_text(text, max_tokens=1000)
    assert len(chunks) == 1
    assert chunks[0] == ""


@pytest.mark.asyncio
async def test_summarize_document_empty():
    """Test summarization with empty text."""
    summary = await summarize_document("")
    assert summary == ""


@pytest.mark.asyncio
async def test_summarize_document_short():
    """Test summarization with short text (no API key, fallback)."""
    text = "This is a short document for testing."
    summary = await summarize_document(text)
    assert len(summary) > 0


@pytest.mark.asyncio
async def test_summarize_document_long():
    """Test summarization with long text (triggers chunking)."""
    text = "This is a test paragraph. " * 2000
    summary = await summarize_document(text)
    assert len(summary) > 0
