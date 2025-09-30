"""
Summarization module for document processing with text chunking logic.
Uses OpenAI-compatible API endpoint for generating summaries.
"""

import os
import logging
from typing import List
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("SUMMARIZATION_MODEL", "gpt-3.5-turbo")
MAX_TOKENS_PER_CHUNK = 8000
SUMMARY_MAX_TOKENS = 500


def count_tokens(text: str) -> int:
    """
    Estimate token count for text.
    Uses a simple approximation: ~4 characters per token.
    """
    return len(text) // 4


def chunk_text(text: str, max_tokens: int = MAX_TOKENS_PER_CHUNK) -> List[str]:
    """
    Split text into chunks that don't exceed max_tokens.

    Args:
        text: Text to split into chunks
        max_tokens: Maximum tokens per chunk

    Returns:
        List of text chunks
    """
    if count_tokens(text) <= max_tokens:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current_chunk = ""

    for paragraph in paragraphs:
        potential_chunk = (
            current_chunk + "\n\n" + paragraph if current_chunk else paragraph
        )

        if count_tokens(potential_chunk) <= max_tokens:
            current_chunk = potential_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if count_tokens(paragraph) > max_tokens:
                sentences = paragraph.split(". ")
                temp_chunk = ""
                for sentence in sentences:
                    temp_sentence = (
                        temp_chunk + ". " + sentence if temp_chunk else sentence
                    )
                    if count_tokens(temp_sentence) <= max_tokens:
                        temp_chunk = temp_sentence
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk)
                        temp_chunk = sentence
                if temp_chunk:
                    chunks.append(temp_chunk)
                current_chunk = ""
            else:
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks


async def summarize_chunk(chunk: str) -> str:
    """
    Summarize a single text chunk using OpenAI-compatible API.

    Args:
        chunk: Text chunk to summarize

    Returns:
        Summary of the chunk
    """
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set, returning truncated text as summary")
        return chunk[:500] + "..." if len(chunk) > 500 else chunk

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENAI_API_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL_NAME,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful assistant that creates "
                                "concise summaries of text documents."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Please provide a concise summary of the "
                                f"following text:\n\n{chunk}"
                            ),
                        },
                    ],
                    "max_tokens": SUMMARY_MAX_TOKENS,
                    "temperature": 0.3,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            summary = result["choices"][0]["message"]["content"].strip()
            logger.info(
                f"Successfully summarized chunk ({len(chunk)} chars -> "
                f"{len(summary)} chars)"
            )
            return summary
    except Exception as e:
        logger.error(f"Error summarizing chunk: {e}")
        return chunk[:500] + "..." if len(chunk) > 500 else chunk


async def summarize_document(text: str) -> str:
    """
    Summarize a document, handling text chunking for long documents.

    Args:
        text: Full document text to summarize

    Returns:
        Summary of the document
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for summarization")
        return ""

    logger.info(
        f"Starting summarization for text of {len(text)} characters "
        f"(~{count_tokens(text)} tokens)"
    )

    token_count = count_tokens(text)

    if token_count <= MAX_TOKENS_PER_CHUNK:
        logger.info("Text within token limit, summarizing directly")
        return await summarize_chunk(text)

    logger.info(f"Text exceeds {MAX_TOKENS_PER_CHUNK} tokens, chunking required")
    chunks = chunk_text(text, MAX_TOKENS_PER_CHUNK)

    chunk_summaries = []
    for i, chunk in enumerate(chunks, 1):
        logger.info(f"Summarizing chunk {i}/{len(chunks)}")
        summary = await summarize_chunk(chunk)
        chunk_summaries.append(summary)

    combined_summary = "\n\n".join(chunk_summaries)
    logger.info(
        f"Combined summaries: {len(combined_summary)} characters "
        f"(~{count_tokens(combined_summary)} tokens)"
    )

    if count_tokens(combined_summary) > MAX_TOKENS_PER_CHUNK:
        logger.info("Combined summaries too long, creating final summary")
        final_summary = await summarize_chunk(combined_summary)
        return final_summary

    return combined_summary
