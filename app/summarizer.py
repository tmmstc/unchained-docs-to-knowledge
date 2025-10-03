"""
Summarization module for document processing with text chunking logic.
Uses OpenAI-compatible API endpoint for generating summaries.
"""

import os
import json
import logging
from typing import List
from pathlib import Path
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CONFIG_DIR = Path("config")
CONFIG_FILE = CONFIG_DIR / "llm_config.json"

MAX_TOKENS_PER_CHUNK = 8000
SUMMARY_MAX_TOKENS = 500


def load_llm_config():
    """Load LLM configuration from config file or environment variables."""
    config = {
        "base_url": os.getenv(
            "OPENAI_API_BASE_URL", "https://api.openai.com/v1"
        ),
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "model": os.getenv("SUMMARIZATION_MODEL", "gpt-3.5-turbo"),
    }

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                file_config = json.load(f)
                config.update(file_config)
                logger.info("Loaded LLM config from file")
        except Exception as e:
            logger.warning(f"Error loading config file: {e}, using defaults")

    return config


def get_llm_config():
    """Get current LLM config, checking session state first if available."""
    try:
        import streamlit as st
        if (hasattr(st, "session_state")
                and st.session_state.get("llm_config_loaded")):
            return {
                "base_url": st.session_state.get(
                    "llm_base_url", "https://api.openai.com/v1"
                ),
                "api_key": st.session_state.get("llm_api_key", ""),
                "model": st.session_state.get("llm_model", "gpt-3.5-turbo"),
            }
    except (ImportError, RuntimeError):
        pass

    return load_llm_config()


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
                    if temp_chunk:
                        temp_sentence = temp_chunk + ". " + sentence
                    else:
                        temp_sentence = sentence
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
    config = get_llm_config()
    api_key = config["api_key"]
    base_url = config["base_url"]
    model = config["model"]

    if not api_key:
        logger.warning(
            "API key not set, returning truncated text as summary"
        )
        return chunk[:500] + "..." if len(chunk) > 500 else chunk

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
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
                f"Successfully summarized chunk "
                f"({len(chunk)} chars -> {len(summary)} chars)"
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

    logger.info(
        f"Text exceeds {MAX_TOKENS_PER_CHUNK} tokens, "
        f"chunking required"
    )
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
